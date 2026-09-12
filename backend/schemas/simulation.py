"""Simulation request and response Pydantic schemas."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DisruptionInput(BaseModel):
    """Specification of an infrastructure disruption on a specific link."""

    asset_id: str = Field(..., description="Target Edge ID (e.g., Bridge_A_B)")
    type: str = Field("closure", description="Disruption type: closure, partial_closure, construction, waterlogging")
    capacity_multiplier: float = Field(
        0.0,
        description="Remaining capacity ratio [0.0 = total closure, 1.0 = normal]",
        ge=0.0,
        le=1.0,
    )
    description: Optional[str] = Field(None, description="Human-readable incident context")


class DemandModifierInput(BaseModel):
    """Multipliers or explicit overrides on OD commuter demand."""

    demand_multiplier: float = Field(1.0, description="Global demand scale factor (e.g. 1.25 for +25% surge)", gt=0.0)
    od_overrides: Optional[Dict[str, float]] = Field(None, description="Direct demand overrides by OD pair ID")


class WeatherInput(BaseModel):
    """Weather and environmental scenario conditions."""

    condition: str = Field("clear", description="clear, overcast, rain, heavy_rain, fog")
    rain_intensity_mm_hr: float = Field(0.0, description="Precipitation rate in mm/hour", ge=0.0)


class SimulateRequest(BaseModel):
    """Input payload to trigger a network disruption and cascade simulation."""

    network_id: str = Field("demo_city", description="Network dataset to simulate")
    time_period: str = Field("weekday_rush_hour", description="Demand profile: weekday_rush_hour or off_peak")
    disruptions: List[DisruptionInput] = Field(default_factory=list, description="List of road disruptions")
    demand_modifiers: Optional[DemandModifierInput] = Field(None, description="Optional demand adjustments")
    weather: Optional[WeatherInput] = Field(None, description="Optional weather conditions")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Execution options (e.g. max_iterations)")


class FailedAssetOutput(BaseModel):
    """Summary of an asset that experienced primary capacity reduction."""

    asset_id: str
    name: str
    type: str
    capacity_multiplier: float
    capacity_removed_veh_per_hour: float


class EdgeEvaluationOutput(BaseModel):
    """Operational performance metrics of a road link under scenario conditions."""

    edge_id: str
    name: str
    source: str
    target: str
    road_class: str
    status: str  # open, restricted, closed
    nominal_capacity_veh_per_hour: float
    effective_capacity_veh_per_hour: float
    baseline_flow_veh_per_hour: float
    current_flow_veh_per_hour: float
    flow_change_veh_per_hour: float
    vc_ratio: Optional[float]
    free_flow_time_minutes: float
    travel_time_minutes: Optional[float]
    travel_time_change_minutes: Optional[float]
    delay_minutes_per_vehicle: Optional[float]
    total_delay_veh_hours: Optional[float]
    is_overloaded: bool
    is_newly_overloaded: bool
    is_closed: bool


class CriticalServiceImpactOutput(BaseModel):
    """Accessibility and emergency response metrics to critical facilities."""

    asset_id: str
    name: str
    asset_type: str
    node_id: str
    origin_zone: str
    baseline_access_time_minutes: Optional[float]
    scenario_access_time_minutes: Optional[float]
    response_time_delta_minutes: Optional[float]
    access_lost: bool


class RouteImpactOutput(BaseModel):
    """OD pair routing, detour, and travel-time impact."""

    od_id: str
    name: Optional[str]
    origin: str
    destination: str
    demand_veh_per_hour: float
    rerouted: bool
    unserved: bool
    baseline_edge_ids: List[str]
    scenario_edge_ids: Optional[List[str]]
    baseline_distance_km: float
    scenario_distance_km: Optional[float]
    extra_distance_km: Optional[float]
    baseline_travel_time_minutes: float
    scenario_travel_time_minutes: Optional[float]
    travel_time_change_minutes: Optional[float]


class ScenarioMetricsSummary(BaseModel):
    """Network-level aggregate comparison metrics."""

    total_delay_change_veh_hours: float = Field(..., description="Change in total vehicle delay (hours)")
    delay_change_percent: float = Field(..., description="Percentage change in total system delay")
    travel_time_change_minutes: float = Field(..., description="Net travel time delta across all trips")
    travel_time_change_percent: float = Field(..., description="Percentage travel time increase")
    population_affected: int = Field(..., description="Estimated population experiencing degraded travel")
    newly_overloaded_count: int = Field(..., description="Count of links experiencing secondary cascade overload")
    unserved_trips_count: int = Field(..., description="Count of OD pairs with zero feasible paths remaining")


class BaseMetricsOutput(BaseModel):
    """Network state metrics under baseline or scenario conditions."""

    total_delay_veh_hours: float
    avg_travel_time_minutes: float
    total_travel_time_minutes: float
    unserved_demand_veh_per_hour: float
    overloaded_edges_count: int


class SimulateResponse(BaseModel):
    """Complete normalized simulation output returned to the frontend."""

    scenario_id: str
    network_id: str
    time_period: str
    status: str = "completed"
    baseline: BaseMetricsOutput
    scenario: BaseMetricsOutput
    metrics: ScenarioMetricsSummary
    failed_assets: List[FailedAssetOutput]
    affected_edges: List[EdgeEvaluationOutput]
    critical_assets: List[CriticalServiceImpactOutput]
    routes: List[RouteImpactOutput]
    explainability: List[str]

