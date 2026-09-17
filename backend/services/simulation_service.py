"""Simulation service bridging FastAPI API schemas to Agent 1 simulation engine."""

from __future__ import annotations

import math
from typing import Dict, List, Optional

from backend.schemas.scenarios import CompareRequest, CompareResponse, ComparisonDelta
from backend.schemas.simulation import (
    BaseMetricsOutput,
    CriticalServiceImpactOutput,
    EdgeEvaluationOutput,
    FailedAssetOutput,
    RouteImpactOutput,
    ScenarioMetricsSummary,
    SimulateRequest,
    SimulateResponse,
)
from backend.services.data_service import DataService, data_service
from backend.services.explainability import generate_explainability_narrative
from src.simulation.graph import RoadNetwork
from src.simulation.models import (
    CriticalAsset,
    Disruption,
    Edge,
    Node,
    ODDemand,
    SimulationConfig,
    SimulationResult,
)
from src.simulation.simulation import simulate


class SimulationService:
    """Orchestrates simulation execution, data bridging, and scenario comparisons."""

    def __init__(self, data_svc: DataService = data_service):
        self.data_svc = data_svc

    def _build_road_network(self) -> Tuple[RoadNetwork, Dict[str, Edge]]:
        """Construct Agent 1 RoadNetwork from cached demo network data."""
        network_data = self.data_svc.get_network()

        nodes = [
            Node(
                id=n.id,
                latitude=n.latitude,
                longitude=n.longitude,
                node_type=n.node_type,
            )
            for n in network_data.nodes
        ]

        edges = [
            Edge(
                id=e.id,
                source=e.source,
                target=e.target,
                length_km=e.length_km,
                free_flow_speed_kmph=e.free_flow_speed_kmph,
                nominal_capacity_veh_per_hour=e.nominal_capacity_veh_per_hour,
                lanes=e.lanes,
                road_class=e.road_class,
                baseline_flow_veh_per_hour=e.baseline_flow_veh_per_hour,
                status=e.status,
            )
            for e in network_data.edges
        ]

        network = RoadNetwork(nodes=nodes, edges=edges)
        edges_meta = {e.id: e for e in edges}
        return network, edges_meta

    def run_simulation(self, request: SimulateRequest) -> SimulateResponse:
        """Execute simulation using Agent 1 engine and return normalized API response."""
        network, edges_meta = self._build_road_network()

        # Validate disruption targets
        disruptions: List[Disruption] = []
        failed_assets_output: List[FailedAssetOutput] = []

        for d in request.disruptions:
            if d.asset_id not in edges_meta:
                raise ValueError(
                    f"Unknown asset_id '{d.asset_id}'. Available network edges: {sorted(list(edges_meta.keys()))}"
                )

            edge = edges_meta[d.asset_id]
            nom_cap = edge.nominal_capacity_veh_per_hour
            cap_removed = nom_cap * (1.0 - d.capacity_multiplier)

            disruptions.append(
                Disruption(
                    asset_id=d.asset_id,
                    disruption_type=d.type,
                    capacity_multiplier=d.capacity_multiplier,
                )
            )

            failed_assets_output.append(
                FailedAssetOutput(
                    asset_id=d.asset_id,
                    name=edge.id,
                    type=d.type,
                    capacity_multiplier=d.capacity_multiplier,
                    capacity_removed_veh_per_hour=cap_removed,
                )
            )

        # Load OD demand with modifiers
        demand_mult = 1.0
        od_overrides = None
        if request.demand_modifiers:
            demand_mult = request.demand_modifiers.demand_multiplier
            od_overrides = request.demand_modifiers.od_overrides

        od_demands = self.data_svc.get_od_demands(
            time_period=request.time_period,
            demand_multiplier=demand_mult,
            od_overrides=od_overrides,
        )

        # Load critical assets
        critical_assets = self.data_svc.get_critical_assets()

        # Build config
        cfg = SimulationConfig(overload_vc_threshold=1.0)

        # Invoke Agent 1 simulation
        sim_result: SimulationResult = simulate(
            network=network,
            od_demands=od_demands,
            disruptions=disruptions,
            critical_assets=critical_assets,
            config=cfg,
        )

        # Map baseline & scenario metrics
        base_tot_delay = sum(
            e.total_delay_veh_hours or 0.0 for e in sim_result.baseline_edges.values()
        )
        scen_tot_delay = sum(
            e.total_delay_veh_hours or 0.0 for e in sim_result.scenario_edges.values()
        )

        base_tt_list = [r.baseline_travel_time_minutes for r in sim_result.all_routes]
        base_avg_tt = (sum(base_tt_list) / len(base_tt_list)) if base_tt_list else 0.0

        served_scen_tt = [
            r.scenario_travel_time_minutes
            for r in sim_result.all_routes
            if r.scenario_travel_time_minutes is not None
        ]
        scen_avg_tt = (sum(served_scen_tt) / len(served_scen_tt)) if served_scen_tt else 0.0

        base_metrics = BaseMetricsOutput(
            total_delay_veh_hours=round(base_tot_delay, 2),
            avg_travel_time_minutes=round(base_avg_tt, 2),
            total_travel_time_minutes=round(sum(base_tt_list), 2),
            unserved_demand_veh_per_hour=0.0,
            overloaded_edges_count=len(
                [e for e in sim_result.baseline_edges.values() if e.is_overloaded]
            ),
        )

        unserved_vol = sum(
            r.demand_veh_per_hour for r in sim_result.all_routes if r.unserved
        )

        scen_metrics = BaseMetricsOutput(
            total_delay_veh_hours=round(scen_tot_delay, 2),
            avg_travel_time_minutes=round(scen_avg_tt, 2),
            total_travel_time_minutes=round(sum(served_scen_tt), 2),
            unserved_demand_veh_per_hour=round(unserved_vol, 1),
            overloaded_edges_count=len(
                [e for e in sim_result.scenario_edges.values() if e.is_overloaded]
            ),
        )

        delay_delta = scen_tot_delay - base_tot_delay
        delay_pct = (
            ((scen_tot_delay - base_tot_delay) / base_tot_delay * 100.0)
            if base_tot_delay > 0
            else 0.0
        )
        tt_delta = scen_avg_tt - base_avg_tt
        tt_pct = ((scen_avg_tt - base_avg_tt) / base_avg_tt * 100.0) if base_avg_tt > 0 else 0.0

        summary_metrics = ScenarioMetricsSummary(
            total_delay_change_veh_hours=round(delay_delta, 2),
            delay_change_percent=round(delay_pct, 1),
            travel_time_change_minutes=round(tt_delta, 2),
            travel_time_change_percent=round(tt_pct, 1),
            population_affected=int(sum(r.demand_veh_per_hour for r in sim_result.changed_routes) * 1.5),
            newly_overloaded_count=len(sim_result.newly_overloaded_edges),
            unserved_trips_count=len(sim_result.unserved_od_ids),
        )

        # Map edge evaluations
        affected_edges_output: List[EdgeEvaluationOutput] = []
        for eid, scen_e in sim_result.scenario_edges.items():
            base_e = sim_result.baseline_edges[eid]
            edge_meta = edges_meta[eid]

            flow_change = scen_e.current_flow_veh_per_hour - base_e.current_flow_veh_per_hour
            tt_change = None
            if scen_e.travel_time_minutes is not None and base_e.travel_time_minutes is not None:
                tt_change = round(scen_e.travel_time_minutes - base_e.travel_time_minutes, 2)

            affected_edges_output.append(
                EdgeEvaluationOutput(
                    edge_id=eid,
                    name=edge_meta.id,
                    source=scen_e.source,
                    target=scen_e.target,
                    road_class=edge_meta.road_class,
                    status=scen_e.status,
                    nominal_capacity_veh_per_hour=scen_e.nominal_capacity_veh_per_hour,
                    effective_capacity_veh_per_hour=scen_e.effective_capacity_veh_per_hour,
                    baseline_flow_veh_per_hour=round(base_e.current_flow_veh_per_hour, 1),
                    current_flow_veh_per_hour=round(scen_e.current_flow_veh_per_hour, 1),
                    flow_change_veh_per_hour=round(flow_change, 1),
                    vc_ratio=round(scen_e.vc_ratio, 2) if scen_e.vc_ratio is not None else None,
                    free_flow_time_minutes=round(scen_e.free_flow_time_minutes, 2),
                    travel_time_minutes=round(scen_e.travel_time_minutes, 2) if scen_e.travel_time_minutes is not None else None,
                    travel_time_change_minutes=tt_change,
                    delay_minutes_per_vehicle=round(scen_e.delay_minutes_per_vehicle, 2) if scen_e.delay_minutes_per_vehicle is not None else None,
                    total_delay_veh_hours=round(scen_e.total_delay_veh_hours, 2) if scen_e.total_delay_veh_hours is not None else None,
                    is_overloaded=scen_e.is_overloaded,
                    is_newly_overloaded=eid in sim_result.newly_overloaded_edges,
                    is_closed=scen_e.is_closed,
                )
            )

        # Map critical service impacts
        critical_output: List[CriticalServiceImpactOutput] = []
        for c in sim_result.critical_service_impacts:
            critical_output.append(
                CriticalServiceImpactOutput(
                    asset_id=c.asset_id,
                    name=c.asset_id,
                    asset_type=c.asset_type,
                    node_id=c.node_id,
                    origin_zone=c.origin_zone,
                    baseline_access_time_minutes=round(c.baseline_access_time_minutes, 2) if c.baseline_access_time_minutes is not None else None,
                    scenario_access_time_minutes=round(c.scenario_access_time_minutes, 2) if c.scenario_access_time_minutes is not None else None,
                    response_time_delta_minutes=round(c.response_time_delta_minutes, 2) if c.response_time_delta_minutes is not None else None,
                    access_lost=c.access_lost,
                )
            )

        # Map routes
        routes_output: List[RouteImpactOutput] = []
        for r in sim_result.all_routes:
            routes_output.append(
                RouteImpactOutput(
                    od_id=r.od_id,
                    name=r.od_id,
                    origin=r.origin,
                    destination=r.destination,
                    demand_veh_per_hour=r.demand_veh_per_hour,
                    rerouted=r.rerouted,
                    unserved=r.unserved,
                    baseline_edge_ids=list(r.baseline_edge_ids),
                    scenario_edge_ids=list(r.scenario_edge_ids) if r.scenario_edge_ids is not None else None,
                    baseline_distance_km=round(r.baseline_distance_km, 2),
                    scenario_distance_km=round(r.scenario_distance_km, 2) if r.scenario_distance_km is not None else None,
                    extra_distance_km=round(r.extra_distance_km, 2) if r.extra_distance_km is not None else None,
                    baseline_travel_time_minutes=round(r.baseline_travel_time_minutes, 2),
                    scenario_travel_time_minutes=round(r.scenario_travel_time_minutes, 2) if r.scenario_travel_time_minutes is not None else None,
                    travel_time_change_minutes=round(r.travel_time_change_minutes, 2) if r.travel_time_change_minutes is not None else None,
                )
            )

        # Build explainability narrative
        explainability = generate_explainability_narrative(
            result=sim_result,
            edges_meta=edges_meta,
            disruptions=disruptions,
        )

        scenario_id = (
            "_".join(d.asset_id for d in disruptions) + f"_{request.time_period}"
            if disruptions
            else f"baseline_{request.time_period}"
        )

        return SimulateResponse(
            scenario_id=scenario_id,
            network_id=request.network_id,
            time_period=request.time_period,
            status="completed",
            baseline=base_metrics,
            scenario=scen_metrics,
            metrics=summary_metrics,
            failed_assets=failed_assets_output,
            affected_edges=affected_edges_output,
            critical_assets=critical_output,
            routes=routes_output,
            explainability=explainability,
        )

    def compare_scenarios(self, request: CompareRequest) -> CompareResponse:
        """Run and compare two scenarios side-by-side."""
        # Resolve Scenario A
        req_a = request.scenario_a_request
        if req_a is None:
            if not request.scenario_a_id:
                raise ValueError("Either scenario_a_id or scenario_a_request must be provided.")
            preset_a = self.data_svc.get_scenario_preset_by_id(request.scenario_a_id)
            if not preset_a:
                raise ValueError(f"Preset scenario '{request.scenario_a_id}' not found.")
            req_a = SimulateRequest(
                time_period=preset_a.time_period,
                disruptions=preset_a.disruptions,
            )

        # Resolve Scenario B
        req_b = request.scenario_b_request
        if req_b is None:
            if not request.scenario_b_id:
                raise ValueError("Either scenario_b_id or scenario_b_request must be provided.")
            preset_b = self.data_svc.get_scenario_preset_by_id(request.scenario_b_id)
            if not preset_b:
                raise ValueError(f"Preset scenario '{request.scenario_b_id}' not found.")
            req_b = SimulateRequest(
                time_period=preset_b.time_period,
                disruptions=preset_b.disruptions,
            )

        res_a = self.run_simulation(req_a)
        res_b = self.run_simulation(req_b)

        # Compute delta (B - A)
        delay_diff = res_b.scenario.total_delay_veh_hours - res_a.scenario.total_delay_veh_hours
        delay_pct_diff = (
            ((res_b.scenario.total_delay_veh_hours - res_a.scenario.total_delay_veh_hours)
            / res_a.scenario.total_delay_veh_hours * 100.0)
            if res_a.scenario.total_delay_veh_hours > 0
            else 0.0
        )
        tt_diff = res_b.scenario.avg_travel_time_minutes - res_a.scenario.avg_travel_time_minutes
        overloaded_diff = res_b.metrics.newly_overloaded_count - res_a.metrics.newly_overloaded_count

        # Hospital access delta
        hosp_a = next((c for c in res_a.critical_assets if c.asset_type == "hospital"), None)
        hosp_b = next((c for c in res_b.critical_assets if c.asset_type == "hospital"), None)
        hosp_diff = None
        if hosp_a and hosp_b and hosp_a.scenario_access_time_minutes is not None and hosp_b.scenario_access_time_minutes is not None:
            hosp_diff = round(hosp_b.scenario_access_time_minutes - hosp_a.scenario_access_time_minutes, 2)

        # Verdict
        if delay_diff < -1e-4:
            verdict = (
                f"Scenario B demonstrates superior resilience, reducing system vehicle-hours of delay by "
                f"{abs(delay_diff):.1f} hours ({abs(delay_pct_diff):.1f}% reduction) relative to Scenario A."
            )
        elif delay_diff > 1e-4:
            verdict = (
                f"Scenario A performs better; Scenario B introduces an additional {delay_diff:.1f} vehicle-hours "
                f"of congestion delay (+{delay_pct_diff:.1f}%)."
            )
        else:
            verdict = "Both scenarios exhibit comparable aggregate network delay characteristics."

        delta = ComparisonDelta(
            delay_difference_veh_hours=round(delay_diff, 2),
            delay_difference_percent=round(delay_pct_diff, 1),
            travel_time_difference_minutes=round(tt_diff, 2),
            newly_overloaded_difference=overloaded_diff,
            hospital_access_difference_minutes=hosp_diff,
            mitigation_verdict=verdict,
        )

        id_a = request.scenario_a_id or res_a.scenario_id
        id_b = request.scenario_b_id or res_b.scenario_id

        return CompareResponse(
            scenario_a_id=id_a,
            scenario_b_id=id_b,
            scenario_a=res_a,
            scenario_b=res_b,
            delta=delta,
        )


# Singleton instance
simulation_service = SimulationService()

