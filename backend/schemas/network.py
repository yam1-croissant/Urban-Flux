"""Network and infrastructure Pydantic schemas."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NodeSchema(BaseModel):
    """Schema representing a network intersection, junction, or zone centroid."""

    id: str = Field(..., description="Unique node identifier")
    name: str = Field(..., description="Human-readable location or intersection name")
    latitude: Optional[float] = Field(None, description="WGS84 Latitude coordinate")
    longitude: Optional[float] = Field(None, description="WGS84 Longitude coordinate")
    node_type: str = Field("intersection", description="Type: intersection, junction, zone, critical_asset")


class EdgeSchema(BaseModel):
    """Schema representing a directed road corridor or segment."""

    id: str = Field(..., description="Unique edge/corridor identifier")
    name: str = Field(..., description="Human-readable road name")
    source: str = Field(..., description="Origin node ID")
    target: str = Field(..., description="Destination node ID")
    length_km: float = Field(..., description="Road length in kilometers", ge=0.0)
    free_flow_speed_kmph: float = Field(..., description="Free-flow speed limit in km/h", gt=0.0)
    nominal_capacity_veh_per_hour: float = Field(..., description="Design capacity in veh/h", gt=0.0)
    lanes: Optional[int] = Field(None, description="Number of active travel lanes")
    road_class: str = Field("arterial", description="Functional classification")
    baseline_flow_veh_per_hour: float = Field(0.0, description="Observed baseline background flow")
    status: str = Field("open", description="Operational status: open, restricted, closed")
    coordinates: Optional[List[List[float]]] = Field(
        None, description="GeoJSON coordinates sequence: [[lon1, lat1], [lon2, lat2]]"
    )


class POISchema(BaseModel):
    """Schema representing a Point of Interest or critical infrastructure facility."""

    id: str = Field(..., description="Unique facility identifier")
    name: str = Field(..., description="Human-readable facility name")
    asset_type: str = Field(..., description="Type: hospital, fire_station, transit_hub, commercial_hub")
    node_id: str = Field(..., description="Associated road network node ID")
    latitude: Optional[float] = Field(None, description="WGS84 Latitude coordinate")
    longitude: Optional[float] = Field(None, description="WGS84 Longitude coordinate")
    criticality_weight: float = Field(1.0, description="Relative priority weight for resilience evaluations")
    service_population: Optional[int] = Field(None, description="Estimated population served")
    description: Optional[str] = Field(None, description="Contextual description")


class NetworkMetadataSchema(BaseModel):
    """Metadata regarding spatial extent, map centers, and data provenance."""

    city: str = Field(..., description="City or metropolitan area name")
    center: Dict[str, float] = Field(..., description="Center coordinates: {latitude, longitude}")
    zoom: float = Field(13.0, description="Recommended default map zoom level")
    description: str = Field(..., description="Summary of network boundaries and coverage")
    provenance: Dict[str, str] = Field(
        default_factory=dict,
        description="Formal provenance tags: OBSERVED, MODELED, SYNTHETIC, ASSUMED",
    )


class NetworkResponse(BaseModel):
    """Full network representation returned to the frontend map visualization."""

    network_id: str = Field(..., description="Network identifier (e.g., demo_city)")
    name: str = Field(..., description="Corridor network title")
    version: str = Field("1.0.0", description="Dataset schema version")
    metadata: NetworkMetadataSchema = Field(..., description="Geospatial and provenance metadata")
    nodes: List[NodeSchema] = Field(..., description="List of network nodes")
    edges: List[EdgeSchema] = Field(..., description="List of road links with geometry")
    pois: List[POISchema] = Field(default_factory=list, description="Associated critical facilities and POIs")

