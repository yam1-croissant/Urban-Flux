# UrbanResilience — Backend API Specification & Integration Contract

This document provides the formal API specification for **UrbanResilience Sim**. It serves as the integration contract between the **FastAPI Backend (Agent 2)**, the **Simulation Engine (Agent 1)**, and the **Bird's-Eye Map Interface (Agent 3)**.

---

## 1. Quick Start & Server Execution

### Launching the Backend Service
The server runs locally with zero external network or cloud dependencies:

```bash
# From repository root:
python3 backend/main.py
# or via uvicorn directly:
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Base URL**: `http://localhost:8000`
- **Interactive Swagger UI**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`

CORS is enabled by default for all origins (`*`) to support local Vite / React frontends running on `http://localhost:5173` or `http://localhost:3000`.

---

## 2. API Overview

| Method | Endpoint | Description | Frontend Use Case |
|---|---|---|---|
| `GET` | `/health` | System liveness probe | Status pill / initial health check |
| `GET` | `/api/network` | Full topology, road geometry, POIs, metadata | MapLibre / Deck.gl road & marker render |
| `POST` | `/api/simulate` | Execute link disruption and cascade analysis | Scenario "Simulate" action & animations |
| `GET` | `/api/scenarios` | List available pre-packaged presets | Preset dropdown menu |
| `GET` | `/api/scenarios/{id}`| Retrieve specific scenario preset configuration | Preset selection loader |
| `POST` | `/api/scenarios/compare`| Side-by-side scenario comparison & deltas | Mitigation comparison modal |
| `POST` | `/api/data/upload` | Ingest and normalize CSV/JSON sensor feeds | Data upload & custom scenario ingestion |

---

## 3. Data Provenance Standards

Every data attribute exposed by the API carries a formal provenance tag to ensure hackathon judges understand what is empirical vs modeled:

| Tag | Meaning | Demo Examples |
|---|---|---|
| `OBSERVED` | Directly measured from empirical sensors or open GIS datasets | Road geometry (OSM), observed baseline speeds, hospital coordinates |
| `MODELED` | Derived through mathematical equations or engineering formulas | BPR travel times, effective capacities, delay, $V/C$ ratios |
| `SYNTHETIC` | Plausible commuter demand distributions created for demo scenarios | OD trip matrices (e.g. Indiranagar to Koramangala) |
| `ASSUMED` | Rule-based heuristics or operational parameters | Criticality priority weights, lane counts where unmapped |

---

## 4. Detailed Endpoint Specifications

### 4.1 GET `/health`
Returns service availability.

#### Request
```http
GET /health HTTP/1.1
Host: localhost:8000
```

#### Response (`200 OK`)
```json
{
  "status": "ok"
}
```

---

### 4.2 GET `/api/network`
Retrieves network nodes, edges, GeoJSON-compatible coordinates, critical facilities, and spatial metadata.

#### Query Parameters
- `network_id` *(string, optional, default: `"demo_city"`)*: Network identifier.

#### Request
```http
GET /api/network?network_id=demo_city HTTP/1.1
Host: localhost:8000
```

#### Response (`200 OK`)
```json
{
  "network_id": "demo_city",
  "name": "Bengaluru Central-East Resilience Corridor",
  "version": "1.0.0",
  "metadata": {
    "city": "Bengaluru, Karnataka, India",
    "center": {
      "latitude": 12.9610,
      "longitude": 77.6380
    },
    "zoom": 13.2,
    "description": "Critical arterial and collector network spanning Indiranagar, Old Airport Road, Domlur, and Koramangala.",
    "provenance": {
      "road_geometry": "OBSERVED / OpenStreetMap",
      "speed_limits": "OBSERVED / Bangalore Traffic Police Arterial Guidelines",
      "capacities": "MODELED / IRC-106 Urban Capacity Standards",
      "baseline_flows": "OBSERVED / Kaggle Bangalore Traffic Pulse",
      "od_demand": "SYNTHETIC / Hackathon Commuter Distribution",
      "criticality_weights": "ASSUMED / Emergency Response Model"
    }
  },
  "nodes": [
    {
      "id": "Zone_A",
      "name": "Indiranagar Residential District",
      "latitude": 12.9784,
      "longitude": 77.6408,
      "node_type": "zone"
    },
    {
      "id": "Hospital_C",
      "name": "Manipal City Hospital Access Point",
      "latitude": 12.9592,
      "longitude": 77.6499,
      "node_type": "critical_asset"
    }
  ],
  "edges": [
    {
      "id": "Bridge_A_B",
      "name": "Northern Primary Flyover (Bridge A)",
      "source": "Zone_A",
      "target": "Junction_B",
      "length_km": 3.5,
      "free_flow_speed_kmph": 60.0,
      "nominal_capacity_veh_per_hour": 2400.0,
      "lanes": 4,
      "road_class": "primary_arterial",
      "baseline_flow_veh_per_hour": 400.0,
      "status": "open",
      "coordinates": [
        [77.6408, 12.9784],
        [77.6430, 12.9610]
      ]
    }
  ],
  "pois": [
    {
      "id": "Hospital_C",
      "name": "Manipal City Hospital (Level-1 Trauma Center)",
      "asset_type": "hospital",
      "node_id": "Hospital_C",
      "latitude": 12.9592,
      "longitude": 77.6499,
      "criticality_weight": 2.5,
      "service_population": 180000,
      "description": "Primary regional trauma center."
    }
  ]
}
```

---

### 4.3 POST `/api/simulate`
Simulates link disruptions, reassigns commuter demand along least-cost alternate paths, calculates secondary overloads, and evaluates critical service access degradation.

#### Request Headers
- `Content-Type: application/json`

#### Request Body Schema
```json
{
  "network_id": "demo_city",
  "time_period": "weekday_rush_hour",
  "disruptions": [
    {
      "asset_id": "Bridge_A_B",
      "type": "closure",
      "capacity_multiplier": 0.0,
      "description": "Total vehicular shutdown of Northern Primary Bridge"
    }
  ],
  "demand_modifiers": {
    "demand_multiplier": 1.0
  },
  "weather": {
    "condition": "clear",
    "rain_intensity_mm_hr": 0.0
  }
}
```

#### Response (`200 OK`)
```json
{
  "scenario_id": "Bridge_A_B_weekday_rush_hour",
  "network_id": "demo_city",
  "time_period": "weekday_rush_hour",
  "status": "completed",
  "baseline": {
    "total_delay_veh_hours": 26.08,
    "avg_travel_time_minutes": 9.03,
    "total_travel_time_minutes": 18.06,
    "unserved_demand_veh_per_hour": 0.0,
    "overloaded_edges_count": 0
  },
  "scenario": {
    "total_delay_veh_hours": 413.92,
    "avg_travel_time_minutes": 27.66,
    "total_travel_time_minutes": 55.32,
    "unserved_demand_veh_per_hour": 0.0,
    "overloaded_edges_count": 2
  },
  "metrics": {
    "total_delay_change_veh_hours": 387.84,
    "delay_change_percent": 1487.2,
    "travel_time_change_minutes": 18.63,
    "travel_time_change_percent": 206.4,
    "population_affected": 2700,
    "newly_overloaded_count": 2,
    "unserved_trips_count": 0
  },
  "failed_assets": [
    {
      "asset_id": "Bridge_A_B",
      "name": "Bridge_A_B",
      "type": "closure",
      "capacity_multiplier": 0.0,
      "capacity_removed_veh_per_hour": 2400.0
    }
  ],
  "affected_edges": [
    {
      "edge_id": "Bridge_A_B",
      "name": "Bridge_A_B",
      "source": "Zone_A",
      "target": "Junction_B",
      "road_class": "primary_arterial",
      "status": "closed",
      "nominal_capacity_veh_per_hour": 2400.0,
      "effective_capacity_veh_per_hour": 0.0,
      "baseline_flow_veh_per_hour": 2200.0,
      "current_flow_veh_per_hour": 0.0,
      "flow_change_veh_per_hour": -2200.0,
      "vc_ratio": null,
      "free_flow_time_minutes": 3.5,
      "travel_time_minutes": null,
      "travel_time_change_minutes": null,
      "delay_minutes_per_vehicle": null,
      "total_delay_veh_hours": null,
      "is_overloaded": false,
      "is_newly_overloaded": false,
      "is_closed": true
    },
    {
      "edge_id": "Bottleneck_E_F",
      "name": "Bottleneck_E_F",
      "source": "Junction_E",
      "target": "Junction_F",
      "road_class": "secondary",
      "status": "open",
      "nominal_capacity_veh_per_hour": 1400.0,
      "effective_capacity_veh_per_hour": 1400.0,
      "baseline_flow_veh_per_hour": 500.0,
      "current_flow_veh_per_hour": 2300.0,
      "flow_change_veh_per_hour": 1800.0,
      "vc_ratio": 1.64,
      "free_flow_time_minutes": 7.5,
      "travel_time_minutes": 15.69,
      "travel_time_change_minutes": 8.17,
      "delay_minutes_per_vehicle": 8.19,
      "total_delay_veh_hours": 313.79,
      "is_overloaded": true,
      "is_newly_overloaded": true,
      "is_closed": false
    }
  ],
  "critical_assets": [
    {
      "asset_id": "Hospital_C",
      "name": "Hospital_C",
      "asset_type": "hospital",
      "node_id": "Hospital_C",
      "origin_zone": "Zone_A",
      "baseline_access_time_minutes": 6.84,
      "scenario_access_time_minutes": 24.36,
      "response_time_delta_minutes": 17.52,
      "access_lost": false
    }
  ],
  "routes": [
    {
      "od_id": "OD_ZoneA_Hospital",
      "name": "OD_ZoneA_Hospital",
      "origin": "Zone_A",
      "destination": "Hospital_C",
      "demand_veh_per_hour": 600.0,
      "rerouted": true,
      "unserved": false,
      "baseline_edge_ids": ["Bridge_A_B", "Arterial_B_C"],
      "scenario_edge_ids": ["Collector_A_E", "Bottleneck_E_F", "Connector_F_C"],
      "baseline_distance_km": 6.0,
      "scenario_distance_km": 11.5,
      "extra_distance_km": 5.5,
      "baseline_travel_time_minutes": 6.84,
      "scenario_travel_time_minutes": 24.36,
      "travel_time_change_minutes": 17.52
    }
  ],
  "explainability": [
    "Complete closure on 'Bridge_A_B' removed 2,400 veh/hr of operational corridor capacity.",
    "Commuters on Zone_A → Zone_D (1,200 veh/hr) diverted away from disrupted corridors (+6.0 km detour).",
    "Commuters on Zone_A → Hospital_C (600 veh/hr) diverted away from disrupted corridors (+5.5 km detour).",
    "Secondary cascade overload on 'Collector_A_E': volume/capacity jumped from 0.13 to 1.33 due to diverted flow.",
    "Secondary cascade overload on 'Bottleneck_E_F': volume/capacity jumped from 0.36 to 1.64 due to diverted flow.",
    "Emergency access to HOSPITAL 'Hospital_C' degraded by +17.5 minutes (+256%, from 6.8 to 24.4 min).",
    "Overall network congestion penalty: +387.8 vehicle-hours of aggregate traffic delay."
  ]
}
```

---

### 4.4 GET `/api/scenarios`
Lists pre-configured demo presets.

#### Response (`200 OK`)
```json
{
  "network_id": "demo_city",
  "presets": [
    {
      "id": "scenario_bridge_closure_rush_hour",
      "name": "Northern Primary Bridge Closure (Structural Failure)",
      "category": "bridge_closure",
      "description": "Complete physical closure of Bridge A during morning peak hour.",
      "time_period": "weekday_rush_hour",
      "disruptions": [
        {
          "asset_id": "Bridge_A_B",
          "type": "closure",
          "capacity_multiplier": 0.0
        }
      ]
    },
    {
      "id": "scenario_waterlogging_rush_hour",
      "name": "Severe Monsoon Waterlogging & Canal Overflow",
      "category": "weather_disruption",
      "description": "50% capacity loss on primary bridge and 60% on Domlur Canal bottleneck.",
      "time_period": "weekday_rush_hour",
      "disruptions": [
        {
          "asset_id": "Bridge_A_B",
          "type": "waterlogging",
          "capacity_multiplier": 0.50
        },
        {
          "asset_id": "Bottleneck_E_F",
          "type": "waterlogging",
          "capacity_multiplier": 0.40
        }
      ]
    }
  ]
}
```

---

### 4.5 POST `/api/scenarios/compare`
Compares two disruption scenarios side-by-side and returns quantifiable differences and actionable mitigation recommendations.

#### Request Body
```json
{
  "scenario_a_id": "scenario_bridge_closure_rush_hour",
  "scenario_b_id": "scenario_roadwork_construction"
}
```

#### Response (`200 OK`)
```json
{
  "scenario_a_id": "scenario_bridge_closure_rush_hour",
  "scenario_b_id": "scenario_roadwork_construction",
  "scenario_a": { ... },
  "scenario_b": { ... },
  "delta": {
    "delay_difference_veh_hours": -348.5,
    "delay_difference_percent": -84.2,
    "travel_time_difference_minutes": -15.4,
    "newly_overloaded_difference": -2,
    "hospital_access_difference_minutes": -14.2,
    "mitigation_verdict": "Scenario B demonstrates superior resilience, reducing system vehicle-hours of delay by 348.5 hours (84.2% reduction) relative to Scenario A."
  }
}
```

---

### 4.6 POST `/api/data/upload`
Ingests external traffic sensor data via JSON payload or CSV file upload.

#### Direct JSON Body
```http
POST /api/data/upload HTTP/1.1
Content-Type: application/json

{
  "data_type": "traffic_count",
  "records": [
    {
      "road_id": "Bridge_A_B",
      "traffic_volume": 1400.0,
      "timestamp": "2026-09-12T09:00:00"
    }
  ]
}
```

#### Multipart File Upload (CSV)
```http
POST /api/data/upload HTTP/1.1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="data_type"

speed_observation
------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="sensor_speeds.csv"
Content-Type: text/csv

road_id,avg_speed,timestamp
Bridge_A_B,52.5,2026-09-12T09:00:00
------WebKitFormBoundary--
```

#### Response (`200 OK`)
```json
{
  "status": "success",
  "data_type": "traffic_count",
  "total_records": 1,
  "accepted_records": 1,
  "rejected_records": 0,
  "normalized_preview": [
    {
      "original": {
        "road_id": "Bridge_A_B",
        "traffic_volume": 1400.0,
        "timestamp": "2026-09-12T09:00:00"
      },
      "normalized": {
        "road_id": "Bridge_A_B",
        "flow": 1400.0,
        "timestamp": "2026-09-12T09:00:00"
      },
      "validation_status": "ACCEPTED"
    }
  ],
  "column_mapping_applied": {
    "traffic_volume": "flow",
    "road_id": "road_id",
    "timestamp": "timestamp"
  },
  "message": "Ingested 1 valid records (0 rejected). Normalized using 12 column mappings."
}
```

---

## 5. Error Handling & Status Codes

All errors return standard JSON payloads with explicit diagnostic information:

```json
{
  "detail": "Unknown asset_id 'Bridge_XYZ'. Available network edges: ['Arterial_B_C', 'Arterial_C_D', 'Bottleneck_E_F', 'Bridge_A_B', 'Collector_A_E', 'Connector_F_C', 'Connector_F_D']"
}
```

| HTTP Status | Meaning | Scenario |
|---|---|---|
| `200 OK` | Success | Normal execution |
| `400 Bad Request` | Validation Error | Unknown asset ID in disruption, negative capacity, unsupported data type |
| `404 Not Found` | Resource Not Found | Unknown `scenario_id` or `network_id` |
| `422 Unprocessable` | Schema Mismatch | Malformed JSON structure (caught by Pydantic) |
| `500 Server Error` | Execution Exception | Unhandled internal algorithm failure |

