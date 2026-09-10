# UrbanResilience — Disruption & Rerouting Specification

## 1. Disruption Schema & Semantics

In UrbanResilience, physical incidents, extreme weather hazards, and structural closures are represented as declarative `Disruption` records rather than special-case code logic:

```python
@dataclass(frozen=True)
class Disruption:
    asset_id: str             # Must match an existing Edge.id
    disruption_type: str      # "closure", "partial_closure", "construction", "weather"
    capacity_multiplier: float # Fraction of nominal capacity remaining [0.0, 1.0]
```

### Capacity Multiplier Rules:
- **`capacity_multiplier = 1.0`**: Nominal baseline operation (no degradation).
- **`0.0 < capacity_multiplier < 1.0`**: Partial capacity loss (e.g., $0.5$ represents a $50\\%$ capacity reduction due to lane flooding or roadwork). The link remains feasible for routing, but travel times increase according to the BPR curve.
- **`capacity_multiplier = 0.0`**: Complete physical closure. The link's effective capacity becomes $0\\text{ veh/h}$, status becomes `"closed"`, and the edge is excluded from the routing search graph.

---

## 2. Demand Assignment & Rerouting Algorithm

UrbanResilience executes a deterministic 5-step simulation pipeline:

```text
[Baseline OD Demand]
        │
        ▼
1. Baseline Shortest-Path Assignment (All-or-Nothing on free-flow weights)
        │
        ▼
2. Baseline Traffic Evaluation (Calculate base flows, V/C, travel times, delays)
        │
        ▼
3. Disruption Injection (Reduce capacity or exclude closed edges from routing graph)
        │
        ▼
4. Scenario Rerouting (Reassign OD demands over feasible least-cost alternate paths)
        │
        ▼
5. Scenario Traffic Math Evaluation (Recompute link flows, V/C, secondary overloads)
```

### 2.1 Handling Disconnected Demands (Unserved Flows)
If an acute disruption severs all topological paths between an origin and destination:
1. `unserved` is set to `True` for that `ODRouteImpact`.
2. `scenario_edge_ids` is set to `None`.
3. `scenario_travel_time_minutes`, `extra_distance_km`, and `travel_time_change_minutes` are set to `None` (rather than fabricating an artificial finite penalty).
4. The OD ID is recorded in `unserved_od_ids` in `SimulationResult`.
5. For critical facilities (e.g., hospitals), `access_lost` is flagged as `True`.

---

## 3. Route Comparison Metrics

For every Origin-Destination pair, the simulation generates an `ODRouteImpact` record capturing:

$$\\Delta \\text{Distance} = \\text{Distance}_{\\text{scenario}} - \\text{Distance}_{\\text{baseline}} \\quad (\\text{km})$$

$$\\Delta \\text{Travel Time} = \\text{TravelTime}_{\\text{scenario}} - \\text{TravelTime}_{\\text{baseline}} \\quad (\\text{minutes})$$

$$\\text{Percentage Delay Increase} = \\frac{\\Delta \\text{Travel Time}}{\\text{TravelTime}_{\\text{baseline}}} \\times 100\\%$$

---

## 4. End-to-End Worked Example (from Demo Network)

### Scenario Setup:
- **Baseline Northern Corridor**: `Bridge_A_B` ($3.5\\text{ km}$) $\\rightarrow$ `Arterial_B_C` ($2.5\\text{ km}$). Total: $6.0\\text{ km}$, baseline travel time: $7.0\\text{ minutes}$.
- **Southern Alternate Corridor**: `Collector_A_E` ($4.5\\text{ km}$) $\\rightarrow$ `Bottleneck_E_F` ($5.0\\text{ km}$) $\\rightarrow$ `Connector_F_C` ($2.0\\text{ km}$). Total: $11.5\\text{ km}$.
- **Disruption**: Complete closure of `Bridge_A_B` (`capacity_multiplier = 0.0`).
- **Demand Shift**: $1,200\\text{ veh/h}$ of hospital-bound traffic + $400\\text{ veh/h}$ of inter-zone traffic shifts to the southern collector detour.

### Resulting Impact:
1. **Detour Distance**: Hospital trips incur $+5.5\\text{ km}$ extra distance ($6.0 \\rightarrow 11.5\\text{ km}$).
2. **Congestion Delay**: Due to surging flow on the narrow $1,400\\text{ veh/h}$ bottleneck (`Bottleneck_E_F`), travel time escalates from $7.0 \\rightarrow 23.9\\text{ minutes}$ ($+244.1\\%$ increase).
3. **Emergency Accessibility**: Hospital access delay surges by $+17.0\\text{ minutes}$, directly illustrating how network structure magnifies initial disruption impacts.
