"""Network API router providing topology, road geometry, and POI data."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from backend.schemas.network import NetworkResponse
from backend.services.data_service import data_service

router = APIRouter(prefix="/network", tags=["Network"])


@router.get("", response_model=NetworkResponse)
def get_network(
    network_id: str = Query("demo_city", description="Network dataset identifier")
) -> NetworkResponse:
    """Retrieve road network nodes, edges, geometries, and critical POIs for the map visualization."""
    try:
        network = data_service.get_network()
        if network.network_id != network_id and network_id != "demo_city":
            raise HTTPException(
                status_code=404,
                detail=f"Network '{network_id}' not found. Available networks: ['demo_city']",
            )
        return network
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))

