"""UrbanFlux Backend Configuration.

Handles paths, environment settings, and runtime library resolution.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure repository root and local lib are accessible to Python
REPO_ROOT = Path(__file__).resolve().parent.parent
LIB_DIR = REPO_ROOT / "lib"

if str(LIB_DIR) not in sys.path and LIB_DIR.exists():
    sys.path.insert(0, str(LIB_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Data directories
DATA_DIR = REPO_ROOT / "data"
DEMO_DATA_DIR = DATA_DIR / "demo"

# Server configuration
HOST = os.getenv("URBAN_HOST", "0.0.0.0")
PORT = int(os.getenv("URBAN_PORT", "8000"))
DEBUG = os.getenv("URBAN_DEBUG", "false").lower() in ("true", "1", "yes")

# API metadata
API_TITLE = "UrbanFlux Simulation & Cascade API"
API_DESCRIPTION = (
    "Backend API service bridging the UrbanFlux traffic simulation engine "
    "to the bird's-eye map visualization frontend. Provides network topologies, "
    "scenario simulation, cascading overload evaluation, and explainability narratives."
)
API_VERSION = "1.0.0"

# CORS configuration (allow all origins for local hackathon demo)
CORS_ORIGINS = ["*"]

