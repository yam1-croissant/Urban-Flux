# Agent 1 — Simulation & Mathematical Modeling

## Mission

You own the **simulation brain** of UrbanResilience Sim.

The goal is **not** to build a scientifically perfect city simulator. The goal is to make a **small, deterministic, explainable demo** that correctly demonstrates:

> disruption → rerouting → overload → increased delay → secondary effects → critical-service impact

Your work must remain independent from React/frontend code.

---

# 1. What You Own

You are responsible for:

- Infrastructure graph/domain models
- Road/link attributes
- POIs and critical assets
- Demand representation
- Traffic/capacity calculations
- Travel-time model
- Route selection/rerouting
- Disruption representation
- Failure propagation
- Impact calculations
- Criticality ranking
- Scenario comparison
- Simulation unit tests

You are **not** responsible for:

- React UI
- Map styling
- FastAPI endpoint implementation
- Pitch deck
- Business model

---

# 2. Prototype Philosophy

Do not begin by implementing every equation from the original concept.

Build in this order:

```text
1. Network
2. Demand
3. Baseline traffic
4. Travel time
5. Failure
6. Rerouting
7. Secondary overload
8. Impact metrics
9. Criticality
10. Scenario comparison
```

The first complete end-to-end simulation is more valuable than an unfinished advanced model.

---

# 3. Domain Model

## 3.1 Node

A Node represents:

- road intersection
- junction
- interchange
- traffic centroid / zone connector

Minimum fields:

```text
id
latitude
longitude
node_type
```

Optional:

```text
signalized
cycle_length
green_time
```

---

## 3.2 Edge

An Edge represents a directed road segment.

Minimum fields:

```text
id
source
target
length_m
lanes
free_flow_speed_kmh
capacity_veh_per_hour
road_class
baseline_flow
status
```

Optional:

```text
geometry
signal_delay
curb_friction_factor
weather_factor
capacity_multiplier
```

Derived values:

```text
free_flow_time
current_flow
volume_capacity_ratio
congested_time
delay
```

---

## 3.3 POI / Critical Asset

Represent surrounding activity.

Examples:

```text
hospital
office
shopping_center
school
transit_hub
emergency_service
residential_zone
```

Fields:

```text
id
type
latitude
longitude
trip_generation
trip_attraction
service_population
criticality_weight
```

---

## 3.4 Demand

Use simple OD demand.

```text
origin
destination
time_period
vehicle_class
demand
```

Example:

```text
Residential_A → Office_District
08:30
cars
1200 trips/hour
```

For the demo, **synthetic OD demand is acceptable**.

Do not claim it is real-world ground truth.

---

## 3.5 Vehicle Mix

Support a few categories:

```text
2W
3W
car
bus
LCV
```

Use configurable conversion factors.

Important:

- Store the factor in configuration.
- Store source/provenance if the value came from research.
- Do not hard-code an empirical value and call it an established standard without verification.

For MVP:

```text
PCU flow = Σ(vehicle count × configurable factor)
```

---

# 4. Traffic Model

## 4.1 Free-flow time

Start with:

```text
t0 = distance / free_flow_speed
```

Use consistent units.

---

## 4.2 Volume/capacity ratio

```text
v_c = flow / effective_capacity
```

Expose this value because the frontend will color links by stress.

Example:

```text
0.45 → healthy
0.75 → stressed
1.00 → capacity
1.20 → overloaded
```

Thresholds should be configurable.

---

## 4.3 BPR-style travel time

Use a configurable BPR-style relationship:

```text
t(v) = t0 × [1 + α × (v/c)^β]
```

Inputs:

```text
t0
flow
capacity
alpha
beta
```

Do not treat one parameter pair as universally correct.

Make model settings explicit:

```python
TrafficModelConfig(
    alpha=...,
    beta=...
)
```

Agent 4 is responsible for validating claims about empirical values.

---

# 5. Surrounding Land Use

The concept needs to show that surrounding activity affects traffic.

For the dummy, a simple model is enough.

Each POI contributes demand toward/from nearby road zones.

Example:

```text
office_cluster
    attraction = 3000 trips/hour

shopping_center
    attraction = 1500 trips/hour
```

You can use a simple distance-weighted demand rule.

For example:

```text
attraction_weight = base_attraction / (distance + epsilon)^gamma
```

Do not over-engineer this.

The point is to produce an explainable relationship:

```text
large office
   ↓
more trips
   ↓
higher road flow
```

---

# 6. Baseline Routing

Start with shortest-path routing.

Recommended edge cost:

```text
edge_cost = travel_time
```

Version progression:

### Version 1

Shortest path using free-flow time.

### Version 2

Shortest path using congested travel time.

### Version 3

Iterative reassignment:

```text
assign demand
→ calculate congestion
→ update travel times
→ reassign
→ repeat
```

Stop when changes are small.

Do not implement a perfect equilibrium solver unless the MVP is already stable.

---

# 7. Disruption Model

Disruptions should be data.

Example:

```json
{
  "asset_id": "bridge_A",
  "type": "closure",
  "capacity_multiplier": 0.0
}
```

Support:

```text
closure
partial closure
construction
weather
event demand surge
signal adjustment
```

Example:

```json
{
  "asset_id": "road_17",
  "type": "construction",
  "capacity_multiplier": 0.5
}
```

---

# 8. Rerouting Algorithm

When a major road closes:

```text
1. Apply capacity change
2. Identify affected route(s)
3. Recompute feasible paths
4. Reassign affected demand
5. Update flow
6. Recalculate travel times
7. Recalculate overloaded links
8. Repeat if needed
```

Return:

```text
original_route
new_route
extra_distance
extra_time
affected_edges
```

---

# 9. Cascading Failure Engine

The demo must produce a visible causal chain.

Recommended flow:

```text
INITIAL FAILURE
      ↓
capacity removed/reduced
      ↓
demand diverted
      ↓
alternate route load increases
      ↓
volume/capacity rises
      ↓
travel time increases
      ↓
secondary bottleneck detected
      ↓
critical facility access worsens
```

For the prototype, define an explicit overload threshold.

Example concept:

```text
if v/c > threshold:
    mark edge as overloaded
```

Then propagate effects to downstream/nearby dependent assets.

Keep the rules simple and explainable.

---

# 10. Criticality Score

Create an interpretable score.

Possible components:

```text
network_centrality
population_impact
service_criticality
disruption_sensitivity
```

Example weighted score:

```text
criticality =
    0.30 * centrality
  + 0.35 * population_impact
  + 0.25 * service_criticality
  + 0.10 * disruption_sensitivity
```

Weights are prototype assumptions and should be configurable.

Return component scores, not only the final score.

---

# 11. Impact Metrics

At minimum calculate:

```text
total_travel_time
average_travel_time
total_delay
delay_increase
population_affected
affected_edges
overloaded_edges
critical_assets_affected
```

For hospitals/critical facilities:

```text
baseline_access_time
scenario_access_time
response_time_delta
```

The output should be explainable.

---

# 12. Scenario Comparison

Support:

```text
baseline
scenario_A
scenario_B
```

Example:

```text
Scenario A:
Bridge closure, no intervention

Scenario B:
Bridge closure + alternate route strategy

Compare:

total delay
population affected
hospital penalty
overloaded links
worst bottleneck
```

Return both absolute and relative differences.

---

# 13. Suggested Folder Structure

```text
simulation/
├── models.py
├── graph.py
├── demand.py
├── traffic.py
├── routing.py
├── failure.py
├── cascade.py
├── impact.py
├── criticality.py
├── scenarios.py
├── config.py
└── calibration.py
```

---

# 14. Test Strategy

Use tiny synthetic networks.

Example:

```text
A ---- B ---- C
 \           /
  ---- D ----
```

Test cases:

### Test 1 — Basic routing

A → C finds the expected route.

### Test 2 — Closure

Close B.

A → C uses D.

### Test 3 — Congestion

Increase flow.

Travel time increases.

### Test 4 — Cascade

Close one bridge.

Alternative edge exceeds threshold.

It becomes overloaded.

### Test 5 — Critical facility

Hospital path becomes slower.

Hospital response penalty increases.

### Test 6 — Scenario comparison

Mitigation scenario produces lower impact.

---

# 15. Definition of Done

You are done with MVP simulation when this works without the UI:

```python
result = simulate(
    network="demo_city",
    demand="rush_hour",
    disruption="bridge_A_closed"
)
```

and returns:

```text
- failed assets
- changed routes
- affected edges
- travel-time changes
- delay
- population affected
- critical-service impact
- criticality
```

The simulation must be deterministic for identical inputs.

---

# 16. What NOT to Build

Do not spend hackathon time on:

- city-scale microscopic vehicle simulation
- perfect traffic signal physics
- massive real-time data infrastructure
- deep learning before deterministic simulation works
- perfect ML forecasting
- live external APIs
- a scientifically perfect equilibrium solver
- production-grade calibration

These belong to a future roadmap.

---

# 17. Antigravity Pro Prompt

Paste this into your Agent 1 session:

```text
You are Agent 1 for UrbanResilience Sim.

Your responsibility is ONLY the simulation and mathematical modeling layer.

Read:
- AGENTS.md
- docs/architecture.md
- docs/api.md
- docs/data-sources.md
- this agent plan

Do not build frontend code.
Do not implement FastAPI endpoints.
Do not change unrelated folders.

We are building a small, working hackathon demo, not a production city simulator.

Implement in this order:
1. domain models
2. graph
3. demand
4. travel time
5. routing
6. disruption
7. rerouting
8. cascading overload
9. impact metrics
10. criticality
11. scenario comparison

Keep empirical parameters configurable and clearly label assumptions.

Prefer deterministic, explainable models over complexity.

Before modifying code:
- inspect existing files;
- understand contracts;
- identify dependencies;
- propose the smallest implementation.

After each task:
- run tests;
- inspect git diff;
- explain assumptions;
- do not modify unrelated areas;
- prepare a focused commit.

Never fake simulation output. Every displayed result must come from actual calculations or clearly labelled demo assumptions.
```

---

# 18. Coordination With Other Agents

Agent 2 will call your simulation through a Python API/function boundary.

Agent 3 consumes the result and visualizes:

```text
affected_edges
failed_edges
delay
population_affected
critical_services
criticality
```

Agent 4 will challenge the model assumptions and identify claims that require evidence.

If an interface must change, document it before making breaking changes.
