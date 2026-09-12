"""Scenarios API router for presets and side-by-side comparative analysis."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.schemas.scenarios import (
    CompareRequest,
    CompareResponse,
    ScenarioListResponse,
    ScenarioPreset,
)
from backend.services.data_service import data_service
from backend.services.simulation_service import simulation_service

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])


@router.get("", response_model=ScenarioListResponse)
def list_scenarios() -> ScenarioListResponse:
    """List all available pre-packaged disruption scenarios for demo controls."""
    presets = data_service.get_scenario_presets()
    return ScenarioListResponse(network_id="demo_city", presets=presets)


@router.get("/{scenario_id}", response_model=ScenarioPreset)
def get_scenario(scenario_id: str) -> ScenarioPreset:
    """Retrieve details and disruption configuration for a specific preset scenario."""
    preset = data_service.get_scenario_preset_by_id(scenario_id)
    if not preset:
        raise HTTPException(
            status_code=404,
            detail=f"Scenario preset '{scenario_id}' not found.",
        )
    return preset


@router.post("/compare", response_model=CompareResponse)
def compare_scenarios(request: CompareRequest) -> CompareResponse:
    """Execute and compare two scenarios side-by-side, computing quantitative impact deltas."""
    try:
        return simulation_service.compare_scenarios(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Scenario comparison failed: {str(e)}"
        )

