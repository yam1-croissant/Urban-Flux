# UrbanFlux — Network Model Specification

## 1. Graph Semantics & Architecture

UrbanFlux represents urban road infrastructure as a directed graph:

$$G = (V, E)$$

where:
- **$V$** is the set of vertices (intersections, arterial junctions, zone centroids, and critical asset locations).
- **$E$** is the set of directed edges representing one-way road links or individual carriageways.
- Two-way road corridors are modelled explicitly as two opposing directed edges $(u, v)$ and $(v, u)$, enabling asymmetric capacity, flow, and disruption states.
- Edge costs are dynamic travel times derived from the Part A Traffic Mathematics Model (`src/simulation/traffic_math.py`).
- Completely closed edges ($C_{\\text{eff}} = 0$) are strictly **infeasible**, excluded from routing exploration rather than assigned an artificial finite penalty.

---

## 2. Node & Edge Schema Contract

### 2.1 Node Specification
Defined in `src/simulation/models.py`:

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Unique alphanumeric identifier (e.g., `"Junction_B"`, `"Hospital_C"`). |
| `latitude` | `Optional[float]` | WGS84 latitude (optional for synthetic MVP; mandatory for GIS mapping). |
| `longitude` | `Optional[float]` | WGS84 longitude (optional for synthetic MVP; mandatory for GIS mapping). |
| `node_type` | `str` | Functional category: `"intersection"`, `"junction"`, `"zone"`, `"critical_asset"`. |

### 2.2 Edge Specification
Defined in `src/simulation/models.py`:

| Field | Type | Dimensional Unit | Validation Constraint | Description |
|---|---|---|---|---|
| `id` | `str` | Alphanumeric | Unique across $E$ | Unique edge identifier. |
| `source` | `str` | Node ID | Must exist in $V$ | Upstream origin vertex. |
| `target` | `str` | Node ID | Must exist in $V$ | Downstream destination vertex. |
| `length_km` | `float` | Kilometres (km) | $L \ge 0.0$ | Physical traversal distance. |
| `free_flow_speed_kmph` | `float` | km/h | $v_f > 0.0$ | Uncongested design/posted speed. |
| `nominal_capacity_veh_per_hour` | `float` | veh/h | $C_{\\text{nom}} > 0.0$ | Design hourly capacity under ideal conditions. |
| `lanes` | `Optional[int]` | Count | $\\text{lanes} \ge 1$ | Physical number of lanes (optional in MVP). |
| `road_class` | `str` | Category | Valid string | Functional class: `"primary"`, `"arterial"`, `"collector"`, `"local"`. |
| `baseline_flow_veh_per_hour` | `float` | veh/h | $\\text{flow} \ge 0.0$ | Pre-existing background flow before OD assignment. |
| `status` | `str` | Enum | `"open"`, `"restricted"`, `"closed"` | Operational status indicator. |

---

## 3. Derived Metrics & Operational Evaluation

Derived metrics are computed deterministically via `evaluate_edge_condition()` using Part A traffic mathematics:

1. **Free-Flow Travel Time ($t_0$)**:
   $$t_0 = \\frac{L}{v_f} \\quad (\\text{hours})$$
2. **Effective Capacity ($C_{\\text{eff}}$)**:
   $$C_{\\text{eff}} = C_{\\text{nom}} \\cdot \\text{capacity\\_multiplier} \\quad (\\text{veh/h})$$
3. **Volume-to-Capacity Ratio ($V/C$)**:
   $$\\frac{V}{C} = \\frac{\\text{current\\_flow}}{C_{\\text{eff}}}$$
   *(Preserves un-clamped values $> 1.0$ during oversaturation).*
4. **Congested Travel Time ($t$)**:
   $$t = t_0 \\cdot \\left[1 + \\alpha \\cdot \\left(\\frac{V}{C_{\\text{eff}}}\\right)^\\beta\\right] \\quad (\\text{hours})$$
5. **Delay per Vehicle ($d$)**:
   $$d = \\max(0, t - t_0) \\quad (\\text{hours})$$
6. **Total Vehicle Delay ($D_{\\text{total}}$)**:
   $$D_{\\text{total}} = \\text{current\\_flow} \\cdot d \\quad (\\text{veh-hours})$$
7. **Overload Classification**:
   $$\\text{is\\_overloaded} = \\left(\\frac{V}{C_{\\text{eff}}} > \\text{overload\\_vc\\_threshold}\\right)$$

---

## 4. Deterministic Routing & Tie-Breaking

The shortest path between origin $s$ and destination $d$ is computed using Dijkstra's algorithm:

- **Edge Weight**: Estimated link travel time $t$ in hours (or free-flow time $t_0$ for initial assignment).
- **Infeasible Links**: Any edge with $C_{\\text{eff}} = 0$ or included in `excluded_edge_ids` is bypassed.
- **Deterministic Tie-Breaking**: When multiple paths share identical costs (within $10^{-12}$ hours), paths are ordered lexicographically by their sequence of Edge IDs. This guarantees $100\%$ reproducibility regardless of runtime hashing or platform.

---

## 5. Network Validation Rules

`RoadNetwork` enforces strict domain validation upon instantiation:
1. **Duplicate ID Rejection**: Raises `NetworkValidationError` if any node or edge ID is repeated.
2. **Topological Completeness**: Raises `NetworkValidationError` if an edge references a source or target node not present in $V$.
3. **Physical Bounds**: Rejects negative lengths, non-positive speeds, non-positive capacities, and negative baseline flows.

---

## 6. MVP Assumptions & Roadmap to Full Bengaluru Network

| Feature | Part B MVP Implementation | Phase 2 OSM / City-Scale Plan |
|---|---|---|
| **Topology** | Synthetic directed graph (6 nodes, 7 links) with arterial and collector corridors. | OpenStreetMap (OSM) automated ingestion of Bengaluru arterial grid. |
| **Geometry** | Explicitly assumed link lengths (km). | Accurate GIS polyline lengths extracted from OSM coordinates. |
| **Capacities** | Assumed nominal capacities (1,200–2,400 veh/h). | Lane-based capacity lookups ($C = \\text{lanes} \\times 900\\text{ veh/h/lane}$). |
| **Speeds** | Assumed design speeds (40–60 km/h). | Speed limits from OSM tags or calibrated empirical speeds from Kaggle dataset. |
| **Demand** | Fixed hourly synthetic OD demand matrix. | Zone-to-zone gravity model or ward-level population mobility matrices. |
