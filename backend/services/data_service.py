"""Data service for loading, caching, and normalizing demo and uploaded datasets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from backend.config import DEMO_DATA_DIR
from backend.schemas.data import NormalizedRecordOutput
from backend.schemas.network import (
    EdgeSchema,
    NetworkMetadataSchema,
    NetworkResponse,
    NodeSchema,
    POISchema,
)
from backend.schemas.scenarios import ScenarioPreset
from src.simulation.models import CriticalAsset, ODDemand


class DataService:
    """Manages cached access to local demo data snapshots and normalizes input data."""

    def __init__(self, demo_dir: Path = DEMO_DATA_DIR):
        self.demo_dir = demo_dir
        self._network_cache: Optional[NetworkResponse] = None
        self._pois_cache: Optional[List[POISchema]] = None
        self._demand_cache: Optional[Dict[str, Any]] = None
        self._scenarios_cache: Optional[List[ScenarioPreset]] = None
        self._vehicle_mix_cache: Optional[Dict[str, Any]] = None

    def get_network(self) -> NetworkResponse:
        """Load and cache the demo network response including nodes, edges, and POIs."""
        if self._network_cache is not None:
            return self._network_cache

        network_file = self.demo_dir / "network.json"
        if not network_file.exists():
            raise FileNotFoundError(f"Demo network file not found at: {network_file}")

        with open(network_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Merge POIs into the network response
        pois = self.get_pois_schemas()

        resp = NetworkResponse(
            network_id=data["network_id"],
            name=data["name"],
            version=data.get("version", "1.0.0"),
            metadata=NetworkMetadataSchema(**data["metadata"]),
            nodes=[NodeSchema(**n) for n in data["nodes"]],
            edges=[EdgeSchema(**e) for e in data["edges"]],
            pois=pois,
        )
        self._network_cache = resp
        return resp

    def get_pois_schemas(self) -> List[POISchema]:
        """Load POIs as API schemas."""
        if self._pois_cache is not None:
            return self._pois_cache

        pois_file = self.demo_dir / "pois.json"
        if not pois_file.exists():
            return []

        with open(pois_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        schemas = [POISchema(**p) for p in data.get("pois", [])]
        self._pois_cache = schemas
        return schemas

    def get_critical_assets(self) -> List[CriticalAsset]:
        """Load POIs mapped directly to Agent 1 CriticalAsset domain models."""
        pois = self.get_pois_schemas()
        critical_assets: List[CriticalAsset] = []
        for p in pois:
            critical_assets.append(
                CriticalAsset(
                    id=p.id,
                    node_id=p.node_id,
                    asset_type=p.asset_type,
                    criticality_weight=p.criticality_weight,
                )
            )
        return critical_assets

    def get_od_demands(
        self,
        time_period: str = "weekday_rush_hour",
        demand_multiplier: float = 1.0,
        od_overrides: Optional[Dict[str, float]] = None,
    ) -> List[ODDemand]:
        """Load OD commuter demands mapped to Agent 1 ODDemand models with optional modifiers."""
        demand_file = self.demo_dir / "demand.json"
        if not demand_file.exists():
            raise FileNotFoundError(f"Demo demand file not found at: {demand_file}")

        with open(demand_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        periods = data.get("time_periods", {})
        period_data = periods.get(time_period)
        if not period_data:
            # Fallback to rush hour if specified period does not exist
            period_data = periods.get("weekday_rush_hour", list(periods.values())[0])

        demands_raw = period_data.get("demands", [])
        od_list: List[ODDemand] = []

        for d in demands_raw:
            demand_val = float(d["demand_veh_per_hour"]) * demand_multiplier
            if od_overrides and d["id"] in od_overrides:
                demand_val = float(od_overrides[d["id"]])

            od_list.append(
                ODDemand(
                    id=d["id"],
                    origin=d["origin"],
                    destination=d["destination"],
                    demand_veh_per_hour=max(0.0, demand_val),
                    time_period=time_period,
                    vehicle_class=d.get("vehicle_class", "car"),
                )
            )

        return od_list

    def get_scenario_presets(self) -> List[ScenarioPreset]:
        """Load preset scenarios."""
        if self._scenarios_cache is not None:
            return self._scenarios_cache

        scenarios_file = self.demo_dir / "scenarios.json"
        if not scenarios_file.exists():
            return []

        with open(scenarios_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        presets = [ScenarioPreset(**p) for p in data.get("presets", [])]
        self._scenarios_cache = presets
        return presets

    def get_scenario_preset_by_id(self, preset_id: str) -> Optional[ScenarioPreset]:
        """Find preset scenario by ID."""
        presets = self.get_scenario_presets()
        for p in presets:
            if p.id == preset_id:
                return p
        return None

    def normalize_uploaded_data(
        self,
        data_type: str,
        records: List[Dict[str, Any]],
    ) -> Tuple[List[NormalizedRecordOutput], Dict[str, str], int, int]:
        """Normalize raw incoming records into standardized internal schemas.

        Returns:
            (preview_list, applied_mapping, accepted_count, rejected_count)
        """
        valid_types = {
            "traffic_count",
            "speed_observation",
            "signal_timing",
            "vehicle_mix",
            "travel_time",
        }
        if data_type not in valid_types:
            raise ValueError(
                f"Unsupported data_type '{data_type}'. Allowed types: {sorted(list(valid_types))}"
            )

        # Mapping rules by data type
        mappings: Dict[str, Dict[str, str]] = {
            "traffic_count": {
                "vehicle_count": "flow",
                "veh_count": "flow",
                "volume": "flow",
                "traffic_volume": "flow",
                "count": "flow",
                "road_id": "road_id",
                "edge_id": "road_id",
                "link_id": "road_id",
                "corridor": "road_id",
                "time": "timestamp",
                "date": "timestamp",
                "datetime": "timestamp",
                "timestamp": "timestamp",
            },
            "speed_observation": {
                "avg_speed": "speed_kmh",
                "mean_speed": "speed_kmh",
                "speed": "speed_kmh",
                "velocity": "speed_kmh",
                "speed_kmph": "speed_kmh",
                "road_id": "road_id",
                "edge_id": "road_id",
                "link_id": "road_id",
                "timestamp": "timestamp",
            },
            "signal_timing": {
                "cycle": "cycle_length_sec",
                "cycle_time": "cycle_length_sec",
                "cycle_length": "cycle_length_sec",
                "green": "green_time_sec",
                "green_time": "green_time_sec",
                "junction_id": "node_id",
                "node_id": "node_id",
                "intersection": "node_id",
            },
            "vehicle_mix": {
                "share": "share_percentage",
                "percentage": "share_percentage",
                "pct": "share_percentage",
                "proportion": "share_percentage",
                "vehicle_type": "vehicle_class",
                "class": "vehicle_class",
                "mode": "vehicle_class",
                "pcu": "pcu_equivalent",
            },
            "travel_time": {
                "tti": "travel_time_index",
                "travel_time_index": "travel_time_index",
                "travel_time": "travel_time_minutes",
                "duration": "travel_time_minutes",
                "time_min": "travel_time_minutes",
                "road_id": "road_id",
                "edge_id": "road_id",
            },
        }

        active_map = mappings[data_type]
        normalized_results: List[NormalizedRecordOutput] = []
        accepted = 0
        rejected = 0

        for r in records:
            norm: Dict[str, Any] = {}
            for k, v in r.items():
                k_clean = str(k).lower().strip().replace(" ", "_").replace("-", "_")
                target_key = active_map.get(k_clean, k_clean)
                norm[target_key] = v

            # Validate basic requirements
            is_valid = True
            reason = "Valid"

            if data_type == "traffic_count":
                if "road_id" not in norm:
                    is_valid = False
                    reason = "Missing road_id/link_id identifier"
                elif "flow" not in norm:
                    is_valid = False
                    reason = "Missing volume/flow metric"
                elif float(norm.get("flow", -1)) < 0:
                    is_valid = False
                    reason = "Flow value cannot be negative"

            elif data_type == "speed_observation":
                if "road_id" not in norm or "speed_kmh" not in norm:
                    is_valid = False
                    reason = "Missing road_id or speed metric"
                elif float(norm.get("speed_kmh", -1)) <= 0:
                    is_valid = False
                    reason = "Speed must be strictly positive"

            if is_valid:
                accepted += 1
            else:
                rejected += 1

            normalized_results.append(
                NormalizedRecordOutput(
                    original=r,
                    normalized=norm,
                    validation_status="ACCEPTED" if is_valid else f"REJECTED: {reason}",
                )
            )

        return normalized_results, active_map, accepted, rejected


# Singleton instance for simple dependency injection
data_service = DataService()

