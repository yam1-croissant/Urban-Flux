# UrbanFlux — Part B: Network, Disruption, Rerouting & Cascade

## Tiny Context

Part A is complete. Its traffic-mathematics functions are available in:

```text
src/simulation/traffic_math.py
```

Use those functions as the single source of truth for link free-flow time, effective capacity, V/C, BPR travel time, and delay. Do not duplicate or alter the Part A equations in this task.

We now need the smallest deterministic network simulation that demonstrates:

```text
road disruption
  -> route becomes unavailable or slower
  -> demand is rerouted
  -> alternate links receive extra flow
  -> overload is detected
  -> travel time and critical-service access worsen
```

Do not build frontend code, APIs, real-time integrations, city-scale assignment, or a microscopic traffic simulator.

---

## Objective

Build a transparent, testable Part B simulation layer around a small directed road graph. It must:

1. represent road links and intersections;
2. assign synthetic OD demand to routes;
3. apply a closure or partial capacity reduction;
4. reroute affected demand over feasible alternate paths;
5. recompute link flow and traffic metrics using Part A;
6. identify secondary overloads; and
7. report the resulting network and critical-service impacts.

Every result must be calculated from input data or clearly labelled configuration assumptions. The same input must always produce the same output.

---

## 1. Define the Network Contract

Represent the road network as a directed graph:

\[
G=(V,E)
\]

- `V` is a set of intersections, junctions, or zone connectors.
- `E` is a set of directed road segments.
- A two-way road is represented by two directed edges when travel is possible in both directions.
- Edge cost is travel time. Closed edges are infeasible, not merely expensive.

### Node fields

```text
id: str
latitude: float | None
longitude: float | None
node_type: str            # intersection, junction, zone, critical_asset
```

Coordinates are optional for the MVP because the synthetic test network does not need map rendering.

### Edge fields

```text
id: str
source: str
target: str
length_km: float
lanes: int | None
free_flow_speed_kmph: float
nominal_capacity_veh_per_hour: float
road_class: str
baseline_flow_veh_per_hour: float = 0.0
status: str = "open"     # open, restricted, closed
```

Derived values must be computed, rather than stored as competing mutable state:

```text
effective_capacity_veh_per_hour
current_flow_veh_per_hour
vc_ratio
free_flow_time_hours
travel_time_hours
delay_hours_per_vehicle
is_overloaded
```

Validate IDs, endpoints, non-negative flows/lengths, and positive capacities/speeds for open edges. Reject duplicate node or edge IDs and edges whose endpoints do not exist.

### Required documentation

Create `docs/simulation/network_model.md` covering:

- graph semantics and directionality;
- fields, units, validation rules, and derived metrics;
- routing weights and closure semantics;
- shortest path, alternate-path, bottleneck, and centrality scope;
- MVP assumptions, limitations, and data needs for a future Bengaluru network.

Do not claim synthetic topology or assumed capacities are observed Bengaluru data.

---

## 2. Demand and Baseline Routing

Represent demand with an OD record:

```text
id: str
origin: str
destination: str
demand_veh_per_hour: float
time_period: str = "peak"
vehicle_class: str = "car"
```

For this MVP, use synthetic, fixed hourly OD demand. Document it as synthetic demo demand.

### Baseline assignment

1. Start every edge with its `baseline_flow_veh_per_hour`.
2. Find the deterministic least-cost feasible path for each OD pair using current travel time; use free-flow time for the first assignment iteration.
3. Add the full OD demand to every edge on its selected path.
4. Evaluate each edge using `traffic_math`.

Use a deterministic tie-breaker for equal-cost paths, such as lexicographic edge-ID sequence. Record the selected route per OD pair.

MVP assignment is all-or-nothing shortest-path assignment. It is not user equilibrium, stochastic route choice, or a calibrated demand model. State this in documentation.

Create `docs/simulation/demand_model.md` only if this has not already been supplied by another Phase 1 task. Otherwise, document the OD contract in the Part B module docs without overwriting another agent’s work.

---

## 3. Disruption Contract

Represent disruptions as data, not special-case code:

```python
Disruption(
    asset_id="bridge_a_to_b",
    disruption_type="closure",       # closure, partial_closure, construction, weather
    capacity_multiplier=0.0,          # inclusive range [0.0, 1.0]
)
```

Rules:

- `capacity_multiplier=1.0` leaves nominal capacity unchanged.
- `0.0 < capacity_multiplier < 1.0` keeps the edge feasible but reduces capacity.
- `capacity_multiplier=0.0` closes the edge: effective capacity is zero, status is `closed`, route cost is infinite, and it must never be sent to BPR division.
- Do not mutate the baseline network. Return a scenario-specific evaluated state or work on a safe copy.
- Reject unknown asset IDs and invalid multipliers with clear errors.

### Required documentation

Create `docs/simulation/disruption_and_rerouting.md` with:

- disruption schema and exact closure semantics;
- assignment/rerouting algorithm;
- what happens when no feasible route exists;
- additional route distance and time calculations;
- configurable assumptions and limitations;
- an end-to-end worked example based on the demo network.

---

## 4. Rerouting Algorithm

For a scenario, use this sequence:

```text
1. Assign and evaluate baseline demand.
2. Apply the disruption to a scenario copy of the network.
3. Remove closed links from routing eligibility.
4. Recompute feasible paths for all OD demand, or at minimum every OD route affected by the disruption.
5. Reassign demand and calculate new edge flows.
6. Re-evaluate edge capacity, V/C, travel time, and delay with Part A.
7. Optionally repeat assignment using updated travel times for a small, configured number of iterations.
8. Stop deterministically and return the final state plus route changes.
```

Start with one reassignment pass. If a bounded iterative mode is implemented, make iteration count and convergence tolerance explicit configuration; do not imply equilibrium.

For every changed OD route, return:

```text
od_id
baseline_edge_ids
scenario_edge_ids | null
rerouted: bool
unserved: bool
extra_distance_km | null
baseline_travel_time_minutes
scenario_travel_time_minutes | null
travel_time_change_minutes | null
```

If no path exists, set `unserved=True`, retain the baseline route for explanation, and use `None` for scenario travel-time/detour values. Do not hide the demand or invent a finite penalty.

---

## 5. Cascading-Overload Model

The cascade model is a transparent threshold-based consequence model, not a claim that overloaded asphalt physically fails.

### Primary failure

The initial disruption is the primary failed/restricted asset.

### Secondary effect

After rerouting, classify an open edge as overloaded when:

```text
current_flow_veh_per_hour / effective_capacity_veh_per_hour > overload_vc_threshold
```

Use a configurable `overload_vc_threshold` (default may be `1.0`, clearly labelled an MVP assumption). A secondary overload must be both:

1. overloaded in the scenario; and
2. not overloaded in the baseline.

For the first MVP, an overload changes reported congestion and delay; it does not automatically close the link. This avoids unsupported physical-failure claims and unbounded recursion.

### Cascade termination

Terminate when the configured reassignment iterations complete or no route assignment changes. Also report:

```text
primary_disrupted_edges
newly_overloaded_edges
persistently_overloaded_edges
unserved_od_ids
iterations_completed
```

### Required documentation

Create `docs/simulation/cascade_model.md` containing:

- causal chain and exact propagation rule;
- overload threshold and configurability;
- distinction between congestion consequence and physical secondary failure;
- termination rule;
- outputs, severity interpretation, assumptions, and limitations;
- a worked primary-to-secondary example from the synthetic network.

---

## 6. Critical-Service Access Impact

Support critical assets as named destination or origin nodes:

```text
id: str
node_id: str
asset_type: str            # hospital, fire_station, shelter, etc.
criticality_weight: float
```

For OD pairs involving a critical asset, calculate:

```text
baseline_access_time_minutes
scenario_access_time_minutes | null
response_time_delta_minutes | null
access_lost: bool
```

This measures route-access change only. It is not a clinical outcome, emergency dispatch model, or population-health estimate.

---

## 7. Implementation Layout

Keep Part B independent from UI and API layers. Prefer small modules with typed dataclasses and pure/mostly-pure functions:

```text
src/simulation/
├── models.py       # Node, Edge, OD demand, Disruption, result records
├── graph.py        # graph construction and deterministic shortest path
├── demand.py       # baseline/scenario assignment
├── routing.py      # route comparison and rerouting helpers
├── disruption.py   # safe scenario-state application
├── cascade.py      # overload classification and cascade summary
└── simulation.py   # one orchestration entry point
```

It is acceptable to combine closely related modules for a small MVP, but preserve the separation between traffic mathematics and network/cascade orchestration.

Suggested entry point:

```python
result = simulate(
    network=demo_network,
    od_demands=peak_hour_demands,
    disruptions=[bridge_closure],
    config=SimulationConfig(overload_vc_threshold=1.0),
)
```

The result must expose at least:

```text
baseline_edges
scenario_edges
primary_disrupted_edges
changed_routes
unserved_od_ids
newly_overloaded_edges
total_travel_time_change_minutes
total_delay_change_vehicle_hours
critical_service_impacts
assumptions/configuration used
```

---

## 8. Tests

Create focused tests, for example `tests/test_network_simulation.py`. Use a tiny synthetic graph such as:

```text
          B -------- C (hospital)
         /                    \
A ------                       D
         \                    /
          E -------- F --------
```

Choose explicit lengths, capacities, speeds, and OD flows so outcomes can be checked exactly.

Test at least:

1. directed edge direction is respected;
2. the baseline chooses the known shortest path;
3. closing a bridge/edge excludes it and selects the known alternate path;
4. partial capacity loss increases V/C and BPR travel time without making the link impassable;
5. rerouting raises flow on the alternate link(s);
6. an alternate link newly exceeds the configured overload threshold;
7. a pre-existing overload is not incorrectly reported as a new cascade effect;
8. no feasible path produces an explicit unserved result;
9. hospital/critical-asset access time worsens after the relevant disruption;
10. identical inputs return identical results and do not mutate the baseline network;
11. invalid network references, duplicate IDs, and invalid disruption multipliers fail clearly.

Run the complete test suite after implementation.

---

## 9. Demonstration

Create `examples/network_disruption_demo.py`.

Run and print a baseline and a bridge-closure scenario. The output should make the causal chain obvious:

```text
Baseline route: A -> B -> C
Baseline hospital access: 6.0 min

Disruption: bridge_A_B closed
Rerouted route: A -> E -> F -> C
Newly overloaded edge: E_F (V/C 0.72 -> 1.13)
Hospital access change: +7.4 min
Unserved OD pairs: none
```

The numbers above are illustrative only. Print values calculated from the chosen synthetic network, not copied constants.

---

## Definition of Done

Part B is complete when:

- the three model documents exist and distinguish facts from demo assumptions;
- a typed directed network can be created and validated;
- OD demand is assigned to deterministic feasible routes;
- a full and partial disruption produce the documented behavior;
- rerouting changes edge flows and invokes Part A traffic calculations;
- newly overloaded links and unserved OD pairs are explicitly reported;
- critical-service route-access impact is calculated where applicable;
- the demo runs without the UI; and
- all existing and new tests pass.

Do not implement criticality ranking, full scenario optimization, external data ingestion, backend endpoints, or frontend rendering in this part.
