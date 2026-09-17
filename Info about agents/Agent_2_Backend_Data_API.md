# Agent 2 — Backend, Data Pipeline & Integration

## Mission

You own the **bridge between the simulation and the frontend**.

Your job is to make the demo reliably do this:

```text
Frontend request
    ↓
FastAPI
    ↓
Validate scenario
    ↓
Load network/data
    ↓
Call simulation engine
    ↓
Normalize result
    ↓
Return JSON
    ↓
Frontend visualization
```

We are building a hackathon demo, so reliability and simplicity matter more than production infrastructure.

---

# 1. What You Own

You are responsible for:

- FastAPI app
- API schemas
- request validation
- scenario representation
- demo data loading
- data normalization
- simulation invocation
- result normalization
- simple caching if useful
- integration tests
- API documentation
- local/offline demo reliability

You are NOT responsible for:

- core traffic mathematics
- React components
- visual design
- pitch deck
- ML research

---

# 2. Prototype Goal

The backend must make this possible:

```http
POST /api/simulate
```

Input:

```json
{
  "network_id": "demo_city",
  "time_period": "rush_hour",
  "failed_assets": ["bridge_A"],
  "capacity_modifiers": {},
  "demand_modifiers": {},
  "weather": {},
  "options": {}
}
```

Output:

```json
{
  "scenario_id": "bridge_A_rush_hour",
  "baseline": {},
  "scenario": {},
  "failed_assets": [],
  "affected_edges": [],
  "critical_assets": [],
  "population_affected": 0,
  "service_impacts": [],
  "explainability": []
}
```

The exact schema can evolve, but changes must be documented in:

```text
docs/api.md
```

---

# 3. Suggested Folder Structure

```text
backend/
├── main.py
├── api/
│   ├── network.py
│   ├── simulation.py
│   ├── scenarios.py
│   └── data.py
├── schemas/
│   ├── network.py
│   ├── simulation.py
│   └── scenarios.py
├── services/
│   ├── simulation_service.py
│   └── data_service.py
├── storage/
└── config.py

data/
├── raw/
├── processed/
└── demo/
```

---

# 4. API Contract

## GET /api/network

Return network data required by the map.

Minimum:

```text
nodes
edges
POIs
metadata
```

Example:

```json
{
  "network_id": "demo_city",
  "nodes": [],
  "edges": [],
  "pois": []
}
```

The frontend should not need to know how OSM, CSV or Python objects are stored internally.

---

## POST /api/simulate

Accept a scenario.

Example:

```json
{
  "network_id": "demo_city",
  "time_period": "weekday_rush_hour",
  "disruptions": [
    {
      "asset_id": "bridge_A",
      "type": "closure",
      "capacity_multiplier": 0.0
    }
  ]
}
```

Call Agent 1's simulation engine.

Do not reimplement simulation equations here.

---

## POST /api/data/upload

For the demo, accept:

```text
CSV
JSON
```

Prototype supported data types:

```text
traffic_count
speed_observation
signal_timing
vehicle_mix
travel_time
```

Reject malformed or unsupported data clearly.

---

## GET /api/scenarios/{scenario_id}

Returns stored/reconstructed scenario information.

---

## POST /api/scenarios/compare

Compare two previously generated or newly simulated scenarios.

---

## GET /health

Return:

```json
{
  "status": "ok"
}
```

---

# 5. Demo Data Strategy

Use a small coherent network.

Recommended:

```text
50–300 road links
20–100 nodes
several traffic zones
1–2 hospitals
1 office district
1 shopping center
1 transit hub
multiple alternate paths
one obvious bottleneck
```

Do not wait for a gigantic dataset.

The demo network should be:

```text
small
fast
repeatable
understandable
visually interesting
```

---

# 6. Real Data vs Synthetic Data

Every dataset must be labelled.

Use these categories:

```text
OBSERVED
SYNTHETIC
MODELED
ASSUMED
```

Example:

```text
road geometry → OBSERVED / OSM
traffic counts → OBSERVED / public dataset
OD demand → SYNTHETIC
capacity → MODELED
criticality weight → ASSUMED / prototype
```

Do not allow the UI to imply that synthetic demo demand is real city data.

---

# 7. Local Demo Dataset

The live presentation must NOT depend on internet access.

Ship a local snapshot such as:

```text
data/demo/
├── network.json
├── demand.json
├── pois.json
├── scenarios.json
└── vehicle_mix.json
```

The demo should work after:

```bash
git clone ...
```

without requiring an external API key.

---

# 8. OSM/OSMnx Integration

The broader project can use OpenStreetMap and OSMnx for network geometry.

For the hackathon:

```text
download/import once
       ↓
process
       ↓
save snapshot
       ↓
ship snapshot
```

Do NOT make the live demo fetch OSM every time.

---

# 9. Data Normalization

Different sources will have different column names.

Normalize into internal schemas.

Example raw inputs:

```text
vehicle_count
veh_count
volume
traffic_volume
```

Map them to:

```text
flow
```

Similarly:

```text
avg_speed
mean_speed
speed_kmh
```

→

```text
speed_kmh
```

Keep normalization explicit.

---

# 10. Scenario Manager

A scenario should be serializable.

Example:

```json
{
  "id": "scenario_bridge_closure_rush_hour",
  "name": "Bridge Closure During Rush Hour",
  "base_scenario": "weekday_08_30",
  "disruptions": [
    {
      "asset_id": "bridge_A",
      "type": "closure",
      "capacity_multiplier": 0.0
    }
  ],
  "demand_modifiers": {},
  "weather": {}
}
```

Support a few presets:

```text
Bridge Closure
Road Construction
Shopping/Event Surge
Heavy Rain / Waterlogging
```

---

# 11. Result Normalization

Agent 1 owns simulation semantics.

You own API representation.

Normalize outputs into a stable shape:

```json
{
  "failed_assets": [],
  "affected_edges": [],
  "affected_nodes": [],
  "metrics": {
    "total_delay_hours": 0,
    "avg_travel_time_min": 0,
    "population_affected": 0
  },
  "service_impacts": [],
  "critical_assets": []
}
```

Do not transform values in ways that alter their meaning.

---

# 12. Explainability

The frontend will need "Why did this happen?"

Build an explainability section from the simulation result.

Example:

```json
{
  "explainability": [
    "Bridge A closure removed 2,100 veh/hr of capacity.",
    "1,840 veh/hr shifted to Road B.",
    "Road B volume/capacity increased from 0.78 to 1.19.",
    "Hospital access time increased by 7.4 minutes."
  ]
}
```

Prefer facts directly derived from the model.

Do not invent causal statements.

---

# 13. Integration Tests

Minimum:

### Test health

```text
GET /health → 200
```

### Test network

```text
GET /api/network → valid schema
```

### Test simulation

```text
POST /api/simulate → valid result
```

### Test closure

Closing a known demo bridge changes at least one route/affected metric.

### Test scenario comparison

Scenario B returns comparable metrics with consistent keys.

---

# 14. Error Handling

Make errors useful.

Example:

```json
{
  "error": "Unknown asset",
  "asset_id": "bridge_X"
}
```

or:

```json
{
  "error": "Simulation failed validation",
  "details": [...]
}
```

Do not let one bad UI request crash the server.

---

# 15. Performance

Do not optimize prematurely.

Target:

```text
demo simulation:
fast enough to feel interactive
```

If simulation takes too long:

1. shrink demo network;
2. cache baseline;
3. optimize repeated calculations;
4. simplify iteration count.

Do not build distributed infrastructure for the hackathon.

---

# 16. Definition of Done

Agent 2 is done with MVP when:

```bash
uvicorn backend.main:app --reload
```

starts,

and:

```text
GET /health
GET /api/network
POST /api/simulate
POST /api/scenarios/compare
```

all work using local demo data.

---

# 17. Antigravity Pro Prompt

```text
You are Agent 2 for UrbanFlux Sim.

Own only:
- FastAPI
- API schemas
- scenario handling
- demo data
- data normalization
- simulation integration
- backend tests

Read AGENTS.md and the docs first.

Do not implement traffic mathematics in the backend.
Do not build React/UI code.
Do not change Agent 1's simulation semantics without coordination.

The goal is a reliable hackathon demo.

Priorities:
1. stable API contracts
2. deterministic demo data
3. clean simulation invocation
4. normalized results
5. integration tests
6. local/offline reliability

Keep the demo runnable without external services.

Before changing an API:
- inspect docs/api.md;
- check frontend expectations;
- check simulation input/output.

After each task:
- test endpoints;
- inspect git diff;
- document breaking changes;
- make a focused commit.
```

---

# 18. Coordination

### With Agent 1

You consume the simulation engine.

Never duplicate its traffic logic.

If you need a new simulation output:

```text
request → Agent 1
update engine result
document schema
```

### With Agent 3

Tell them exactly what each endpoint returns.

The frontend should rely on:

```text
GET /api/network
POST /api/simulate
POST /api/scenarios/compare
```

### With Agent 4

Provide model configuration and output definitions so claims can be validated.

---

# 19. What NOT to Build

Defer:

- authentication
- billing
- enterprise deployment
- complex databases
- real-time streaming infrastructure
- production observability
- live external APIs
- massive ETL pipelines
- arbitrary private-data intelligence

The goal is a reliable demo.
