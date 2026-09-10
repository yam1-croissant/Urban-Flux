# UrbanResilience — Final Phase 1 Domain Model & System Synthesis

## 1. Executive Summary & Phase 1 Accomplishment

Phase 1 established the complete theoretical, mathematical, and data-provenance foundation for **UrbanResilience Sim**. 

The mathematical and simulation layer is packaged in `src/simulation/` and verified with 50 automated tests in `tests/`. This document serves as the formal architectural transition contract for **Phase 2 (Agent 2: Backend & Data Integration)** and **Phase 3 (Agent 3: Frontend & Visualization)**.

---

## 2. Answers to the Four Core Questions

### 1. What is a road?
In UrbanResilience, a road is a directed edge $e = (u, v) \\in E$ in a graph $G = (V, E)$, characterized by physical, operational, and performance attributes:
- **Geometry & Physics**: Length ($L$ in km), Free-Flow Speed ($v_f$ in km/h), Nominal Capacity ($C_{\\text{nom}}$ in veh/h), Road Class (`primary`, `arterial`, `collector`).
- **Dynamic State**: Background Flow ($V_{\\text{base}}$), Assigned Demand Flow ($V_{\\text{demand}}$), Effective Capacity ($C_{\\text{eff}} = C_{\\text{nom}} \\cdot \\text{multiplier}$), Operational Status (`open`, `restricted`, `closed`).
- **Performance Output**: Free-flow Time ($t_0$), Congested Travel Time ($t$), Delay per Vehicle ($d$), Aggregate Delay ($D_{\\text{total}}$), Overload Flag ($V/C > 1.0$).

### 2. What is traffic?
Traffic is the physical manifestation of human spatial demand (commuters, commercial fleets, emergency vehicles) moving through a constrained network topology:
- Represented as an Origin-Destination matrix ($T_{ij}$) mapping trips between spatial zones.
- Scaled from daily corridor aggregates to peak-hour demand using standard factors ($k_{\\text{peak}} \\approx 0.085$).
- Assigned across least-cost feasible paths using deterministic shortest-path algorithms.

### 3. What happens when a road fails?
Disruptions propagate through network structure and behavioral rerouting:
$$\\text{Physical Hazard} \\longrightarrow \\text{Capacity Reduction } (r) \\longrightarrow \\text{Link Infeasibility} \\longrightarrow \\text{Traffic Diversion} \\longrightarrow \\text{Secondary Overload}$$
- When a link's capacity is reduced or closed ($C_{\\text{eff}} = 0$), affected OD flows are forced onto alternate collector/arterial corridors.
- As diverted volume surges on narrow parallel routes, their $V/C$ ratios exceed $1.0$, creating **secondary cascading overloads** on links far removed from the original incident.

### 4. How do we measure damage?
Systemic impact is evaluated across four quantifiable dimensions:
1. **User Travel Time Penalty**: Net increase in individual trip duration ($\\Delta t$ in minutes, percentage delay).
2. **Aggregate System Inefficiency**: Total lost vehicle-hours across the metropolitan network ($D_{\\text{total}}$ in veh-hours).
3. **Cascading Network Degradation**: Count and identity of newly overloaded links ($V/C > 1.0$) triggered by diversion.
4. **Critical Service Accessibility Loss**: Emergency response time degradation ($\\Delta t_{\\text{hospital}}$) or complete loss of connectivity (`unserved=True`) to vital civic facilities.

---

## 3. Unified Phase 1 Documentation Index

| Domain Area | Document Path | Core Focus & Contents |
|---|---|---|
| **Traffic Mathematics** | [`docs/simulation/traffic_math.md`](file:///home/aditya/Projects/infrastructure-cascading/docs/simulation/traffic_math.md) / [`traffic_model.md`](file:///home/aditya/Projects/infrastructure-cascading/docs/simulation/traffic_model.md) | BPR equations, $V/C$ ratios, per-vehicle & aggregate delay, capacity degradation. |
| **Network Model** | [`docs/simulation/network_model.md`](file:///home/aditya/Projects/infrastructure-cascading/docs/simulation/network_model.md) | Directed graph schema, node/edge constraints, Dijkstra tie-breaking, OSM roadmap. |
| **Disruption & Rerouting** | [`docs/simulation/disruption_and_rerouting.md`](file:///home/aditya/Projects/infrastructure-cascading/docs/simulation/disruption_and_rerouting.md) | Disruption schema, closure semantics, rerouting algorithms, detour metrics. |
| **Cascade Mechanics** | [`docs/simulation/cascade_model.md`](file:///home/aditya/Projects/infrastructure-cascading/docs/simulation/cascade_model.md) | Causal cascade chain, overload taxonomy (primary vs newly overloaded vs persistent). |
| **Criticality Scoring** | [`docs/simulation/criticality_model.md`](file:///home/aditya/Projects/infrastructure-cascading/docs/simulation/criticality_model.md) | Multi-criteria vulnerability index combining betweenness, flow, and hospital access. |
| **Demand Modeling** | [`docs/simulation/demand_model.md`](file:///home/aditya/Projects/infrastructure-cascading/docs/simulation/demand_model.md) | OD matrix schema, peak-hour scaling ($k_{\\text{peak}}$), gravity model foundations. |
| **Data Provenance** | [`docs/research/data_sources.md`](file:///home/aditya/Projects/infrastructure-cascading/docs/research/data_sources.md) | Provenance matrix for OSM, Kaggle Traffic Pulse, IISc UVH-26, and METR-LA. |
| **Traffic Theory Review** | [`docs/research/traffic_literature.md`](file:///home/aditya/Projects/infrastructure-cascading/docs/research/traffic_literature.md) | Literature review on BPR, Indo-HCM PCU equivalents, and Wardrop's equilibria. |
| **Resilience Literature** | [`docs/research/cascade_literature.md`](file:///home/aditya/Projects/infrastructure-cascading/docs/research/cascade_literature.md) | Theoretical backing for interdependent network cascades and EMS accessibility. |
| **Competitive Analysis** | [`docs/product/competitors.md`](file:///home/aditya/Projects/infrastructure-cascading/docs/product/competitors.md) | Comparison vs PTV Vissim, Aimsun, Replica, UrbanLogiq, and Google Maps. |
| **Customer Personas** | [`docs/product/customers.md`](file:///home/aditya/Projects/infrastructure-cascading/docs/product/customers.md) | Target personas: Traffic Police (BTP), City Planners (BBMP), Metro Contractors. |
| **Monetization & GTM** | [`docs/product/monetization.md`](file:///home/aditya/Projects/infrastructure-cascading/docs/product/monetization.md) | Tiered SaaS pricing (Civic Free, Planner Pro, Enterprise Smart City). |

---

## 4. Phase 2 Transition Architecture (For Agent 2 & Agent 3)

### Python Module Contract:
```python
from src.simulation import (
    RoadNetwork,
    Node,
    Edge,
    ODDemand,
    Disruption,
    CriticalAsset,
    SimulationConfig,
    simulate,
)

# Deterministic entrypoint ready for FastAPI endpoints and UI consumption:
result = simulate(
    network=road_network,
    od_demands=od_list,
    disruptions=disruptions_list,
    critical_assets=critical_assets_list,
    config=SimulationConfig(overload_vc_threshold=1.0),
)
```

The system is fully modular, transparent, and tested for immediate backend and visual layer integration.
