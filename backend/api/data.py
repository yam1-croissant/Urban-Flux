"""Data API router for uploading and normalizing sensor feeds and external datasets."""

from __future__ import annotations

import csv
import io
import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Request

from backend.schemas.data import DataUploadRequest, DataUploadResponse
from backend.services.data_service import data_service

router = APIRouter(prefix="/data", tags=["Data Pipeline"])


@router.post("/upload", response_model=DataUploadResponse)
async def upload_data(request: Request) -> DataUploadResponse:
    """Ingest external traffic counts, speed observations, or signal timings via JSON or CSV file upload."""
    content_type = request.headers.get("content-type", "").lower()
    resolved_type = ""
    records: List[Dict[str, Any]] = []

    # Case 1: Application JSON payload
    if "application/json" in content_type:
        try:
            body = await request.json()
            upload_req = DataUploadRequest(**body)
            resolved_type = upload_req.data_type
            records = upload_req.records
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {str(e)}")

    # Case 2: Multipart Form-Data (File upload or form fields)
    elif "multipart/form-data" in content_type:
        form = await request.form()
        data_type = form.get("data_type")
        if not data_type or not isinstance(data_type, str):
            raise HTTPException(
                status_code=400,
                detail="Form field 'data_type' is required when uploading a file.",
            )
        resolved_type = data_type

        file_obj = form.get("file")
        if not file_obj:
            raise HTTPException(status_code=400, detail="Form file 'file' is required.")

        content = await file_obj.read()
        filename = getattr(file_obj, "filename", "data.csv").lower()

        if filename.endswith(".json"):
            try:
                parsed = json.loads(content.decode("utf-8"))
                if isinstance(parsed, list):
                    records = parsed
                elif isinstance(parsed, dict) and "records" in parsed:
                    records = parsed["records"]
                else:
                    raise HTTPException(
                        status_code=400,
                        detail="JSON upload must be a list of records or contain a 'records' key.",
                    )
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid JSON file: {str(e)}")
        else:
            # Parse as CSV
            try:
                text_stream = io.StringIO(content.decode("utf-8"))
                reader = csv.DictReader(text_stream)
                records = [dict(row) for row in reader]
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid CSV file: {str(e)}")

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported Content-Type '{content_type}'. Must be 'application/json' or 'multipart/form-data'.",
        )

    if not records:
        raise HTTPException(status_code=400, detail="Uploaded dataset contains 0 records.")

    try:
        preview, mapping_applied, accepted, rejected = data_service.normalize_uploaded_data(
            data_type=resolved_type,
            records=records,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return DataUploadResponse(
        status="success" if accepted > 0 else "rejected",
        data_type=resolved_type,
        total_records=len(records),
        accepted_records=accepted,
        rejected_records=rejected,
        normalized_preview=preview[:10],
        column_mapping_applied=mapping_applied,
        message=f"Ingested {accepted} valid records ({rejected} rejected). Normalized using {len(mapping_applied)} column mappings.",
    )

