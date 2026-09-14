"""UrbanFlux Simulation & Cascading Disruption Backend Application.

Main entry point for FastAPI service.
"""

from __future__ import annotations

import os
import sys

# Ensure local lib directory is on sys.path before any library imports
LIB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "lib"))
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if LIB_DIR not in sys.path and os.path.exists(LIB_DIR):
    sys.path.insert(0, LIB_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import data_router, network_router, scenarios_router, simulation_router
from backend.config import (
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
    CORS_ORIGINS,
    HOST,
    PORT,
)

# Initialize FastAPI application
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for frontend accessibility (Vite/React map interface)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers under /api
app.include_router(network_router, prefix="/api")
app.include_router(simulation_router, prefix="/api")
app.include_router(scenarios_router, prefix="/api")
app.include_router(data_router, prefix="/api")


@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint confirming backend availability."""
    return {"status": "ok"}


@app.get("/", tags=["System"])
def root_info():
    """Service metadata and documentation sitemap."""
    return {
        "service": API_TITLE,
        "version": API_VERSION,
        "status": "online",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "network": "/api/network",
            "simulate": "/api/simulate",
            "scenarios": "/api/scenarios",
            "compare": "/api/scenarios/compare",
            "data_upload": "/api/data/upload",
        },
    }


def main():
    """Run uvicorn server directly."""
    import uvicorn

    print(f"Starting {API_TITLE} on {HOST}:{PORT}...")
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)


if __name__ == "__main__":
    main()

