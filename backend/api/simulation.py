"""Simulation API router executing disruptions, traffic assignment, and cascade analysis."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.schemas.simulation import SimulateRequest, SimulateResponse
from backend.services.simulation_service import simulation_service

router = APIRouter(prefix="/simulate", tags=["Simulation"])


@router.post("", response_model=SimulateResponse)
def simulate_scenario(request: SimulateRequest) -> SimulateResponse:
    """Execute a network disruption scenario, returning traffic flow, cascading overloads, and explainability."""
    try:
        return simulation_service.run_simulation(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Simulation failed during execution: {str(e)}"
        )

