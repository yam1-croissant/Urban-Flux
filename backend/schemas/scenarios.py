"""Scenario presets and comparison Pydantic schemas."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from backend.schemas.simulation import (
    DemandModifierInput,
    DisruptionInput,
    SimulateRequest,
    SimulateResponse,
    WeatherInput,
)


class ScenarioPreset(BaseModel):
    """Pre-packaged disruption scenario definition."""

    id: str = Field(..., description="Unique scenario preset identifier")
    name: str = Field(..., description="Scenario display title")
    category: str = Field(..., description="Category: baseline, bridge_closure, weather_disruption, construction, demand_surge")
    description: str = Field(..., description="Detailed operational scenario explanation")
    time_period: str = Field("weekday_rush_hour", description="Demand profile")
    disruptions: List[DisruptionInput] = Field(default_factory=list, description="Associated disruptions")
    demand_modifiers: Dict[str, Any] = Field(default_factory=dict, description="Demand adjustments")
    weather: Dict[str, Any] = Field(default_factory=dict, description="Weather conditions")


class ScenarioListResponse(BaseModel):
    """List of available preset scenarios."""

    network_id: str
    presets: List[ScenarioPreset]


class CompareRequest(BaseModel):
    """Payload to compare two scenarios (either by preset ID or by ad-hoc simulation requests)."""

    scenario_a_id: Optional[str] = Field(None, description="Preset ID for Scenario A (e.g. scenario_bridge_closure_rush_hour)")
    scenario_b_id: Optional[str] = Field(None, description="Preset ID for Scenario B (e.g. scenario_roadwork_construction)")
    scenario_a_request: Optional[SimulateRequest] = Field(None, description="Direct simulate payload for Scenario A if custom")
    scenario_b_request: Optional[SimulateRequest] = Field(None, description="Direct simulate payload for Scenario B if custom")


class ComparisonDelta(BaseModel):
    """Quantified delta between Scenario B and Scenario A (Scenario B - Scenario A)."""

    delay_difference_veh_hours: float = Field(..., description="Total delay delta (Scenario B - Scenario A)")
    delay_difference_percent: float = Field(..., description="Percentage delay difference")
    travel_time_difference_minutes: float = Field(..., description="Travel time delta in minutes")
    newly_overloaded_difference: int = Field(..., description="Difference in newly overloaded edges")
    hospital_access_difference_minutes: Optional[float] = Field(None, description="Hospital response time change")
    mitigation_verdict: str = Field(..., description="Actionable recommendation explaining which scenario is more resilient")


class CompareResponse(BaseModel):
    """Side-by-side scenario comparison output."""

    scenario_a_id: str
    scenario_b_id: str
    scenario_a: SimulateResponse
    scenario_b: SimulateResponse
    delta: ComparisonDelta

