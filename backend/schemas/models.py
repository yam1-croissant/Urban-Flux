"""UrbanResilience — Backend Pydantic Schemas."""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel, Field


class NodeSchema(BaseModel):
    id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    node_type: str = "intersection"  # "intersection", "junction", "zone", "critical_asset"
    label: Optional[str] = None
    description: Optional[str] = None


class EdgeSchema(BaseModel):
    id: str
    source: str
    target: str
    length_km: float
    free_flow_speed_kmph: float
    nominal_capacity_veh_per_hour: float
    lanes: Optional[int] = None
    road_class: str = "arterial"
    baseline_flow_veh_per_hour: float = 0.0
    status: str = "open"
    name: Optional[str] = None


from pydantic import BaseModel, Field, model_validator

class DisruptionInput(BaseModel):
    asset_id: str
    disruption_type: str = "closure"  # "closure", "partial_closure", "weather", "construction"
    capacity_multiplier: float = 0.0  # [0.0, 1.0]

    @model_validator(mode="before")
    @classmethod
    def _remap_type(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "type" in data and "disruption_type" not in data:
                data["disruption_type"] = data.pop("type")
        return data


class ODDemandInput(BaseModel):
    id: str
    origin: str
    destination: str
    demand_veh_per_hour: float
    time_period: str = "peak"
    vehicle_class: str = "car"


class CriticalAssetSchema(BaseModel):
    id: str
    node_id: str
    asset_type: str = "hospital"
    criticality_weight: float = 1.0
    name: Optional[str] = None


class SimulationConfigRequest(BaseModel):
    overload_vc_threshold: float = 1.0
    alpha: float = 0.15
    beta: float = 4.0
    max_reassignment_iterations: int = 1


class SimulateRequest(BaseModel):
    network_id: str = "demo_city"
    time_period: str = "morning_peak"
    disruptions: List[DisruptionInput] = Field(default_factory=list)
    custom_demands: Optional[List[ODDemandInput]] = None
    config: Optional[SimulationConfigRequest] = None


class EdgeEvaluationResponse(BaseModel):
    edge_id: str
    source: str
    target: str
    length_km: float
    free_flow_speed_kmph: float
    nominal_capacity_veh_per_hour: float
    effective_capacity_veh_per_hour: float
    current_flow_veh_per_hour: float
    vc_ratio: Optional[float] = None
    free_flow_time_minutes: float
    travel_time_minutes: Optional[float] = None
    delay_minutes_per_vehicle: Optional[float] = None
    total_delay_veh_hours: Optional[float] = None
    is_overloaded: bool
    is_closed: bool
    status: str


class ODRouteImpactResponse(BaseModel):
    od_id: str
    origin: str
    destination: str
    demand_veh_per_hour: float
    baseline_edge_ids: List[str]
    scenario_edge_ids: Optional[List[str]] = None
    rerouted: bool
    unserved: bool
    baseline_distance_km: float
    scenario_distance_km: Optional[float] = None
    extra_distance_km: Optional[float] = None
    baseline_travel_time_minutes: float
    scenario_travel_time_minutes: Optional[float] = None
    travel_time_change_minutes: Optional[float] = None


class CriticalServiceImpactResponse(BaseModel):
    asset_id: str
    node_id: str
    asset_type: str
    origin_zone: str
    baseline_access_time_minutes: Optional[float] = None
    scenario_access_time_minutes: Optional[float] = None
    response_time_delta_minutes: Optional[float] = None
    access_lost: bool


class ScenarioPreset(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    disruptions: List[DisruptionInput]
    recommended_mitigation_id: Optional[str] = None


class SimulateResponse(BaseModel):
    scenario_id: str
    baseline_edges: Dict[str, EdgeEvaluationResponse]
    scenario_edges: Dict[str, EdgeEvaluationResponse]
    primary_disrupted_edges: List[str]
    newly_overloaded_edges: List[str]
    persistently_overloaded_edges: List[str]
    changed_routes: List[ODRouteImpactResponse]
    all_routes: List[ODRouteImpactResponse]
    unserved_od_ids: List[str]
    total_travel_time_change_minutes: float
    total_delay_change_vehicle_hours: float
    critical_service_impacts: List[CriticalServiceImpactResponse]
    explainability: List[str]
    iterations_completed: int


class ScenarioCompareRequest(BaseModel):
    scenario_a: SimulateRequest
    scenario_b: SimulateRequest


class ScenarioCompareResponse(BaseModel):
    scenario_a_metrics: Dict[str, Any]
    scenario_b_metrics: Dict[str, Any]
    net_delay_reduction_veh_hours: float
    percentage_improvement: float
    summary_verdict: str
