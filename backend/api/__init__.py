"""API router package initialization."""

from backend.api.data import router as data_router
from backend.api.network import router as network_router
from backend.api.scenarios import router as scenarios_router
from backend.api.simulation import router as simulation_router

__all__ = [
    "network_router",
    "simulation_router",
    "scenarios_router",
    "data_router",
]

