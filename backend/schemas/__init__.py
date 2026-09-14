"""UrbanFlux Backend API Schemas."""

from backend.schemas.data import (
    DataUploadRequest,
    DataUploadResponse,
    NormalizedRecordOutput,
)
from backend.schemas.network import (
    EdgeSchema,
    NetworkMetadataSchema,
    NetworkResponse,
    NodeSchema,
    POISchema,
)
from backend.schemas.scenarios import (
    CompareRequest,
    CompareResponse,
    ComparisonDelta,
    ScenarioListResponse,
    ScenarioPreset,
)
from backend.schemas.simulation import (
    BaseMetricsOutput,
    CriticalServiceImpactOutput,
    DemandModifierInput,
    DisruptionInput,
    EdgeEvaluationOutput,
    FailedAssetOutput,
    RouteImpactOutput,
    ScenarioMetricsSummary,
    SimulateRequest,
    SimulateResponse,
    WeatherInput,
)

__all__ = [
    "NodeSchema",
    "EdgeSchema",
    "POISchema",
    "NetworkMetadataSchema",
    "NetworkResponse",
    "DisruptionInput",
    "DemandModifierInput",
    "WeatherInput",
    "SimulateRequest",
    "FailedAssetOutput",
    "EdgeEvaluationOutput",
    "CriticalServiceImpactOutput",
    "RouteImpactOutput",
    "ScenarioMetricsSummary",
    "BaseMetricsOutput",
    "SimulateResponse",
    "ScenarioPreset",
    "ScenarioListResponse",
    "CompareRequest",
    "CompareResponse",
    "ComparisonDelta",
    "DataUploadRequest",
    "DataUploadResponse",
    "NormalizedRecordOutput",
]

