"""Data upload and ingestion Pydantic schemas."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DataUploadRequest(BaseModel):
    """Payload for direct JSON data ingestion."""

    data_type: str = Field(
        ...,
        description="Supported types: traffic_count, speed_observation, signal_timing, vehicle_mix, travel_time",
    )
    records: List[Dict[str, Any]] = Field(..., description="Array of data records to normalize and ingest")
    source_name: Optional[str] = Field("api_upload", description="Identifier of data provider or sensor network")


class NormalizedRecordOutput(BaseModel):
    """Single normalized record confirming schema adaptation."""

    original: Dict[str, Any]
    normalized: Dict[str, Any]
    validation_status: str


class DataUploadResponse(BaseModel):
    """Response confirming validation, normalization, and record ingestion."""

    status: str = "success"
    data_type: str
    total_records: int
    accepted_records: int
    rejected_records: int
    normalized_preview: List[NormalizedRecordOutput]
    column_mapping_applied: Dict[str, str]
    message: str

