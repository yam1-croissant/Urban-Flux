# UrbanResilience — Traffic Flow Theory & Literature Review

## 1. Executive Summary

This document establishes the theoretical and scientific foundations of UrbanResilience by synthesizing foundational transportation engineering literature, macroscopic traffic assignment theories, and India-specific traffic flow research.

---

## 2. Core Models in Transportation Literature

### 2.1 Bureau of Public Roads (BPR) Congestion Function (1964)
- **Primary Source**: *Bureau of Public Roads (1964). "Traffic Assignment Manual." U.S. Dept. of Commerce, Urban Planning Division.*
- **Mathematical Form**:
  $$t = t_0 \\cdot \\left[1 + \\alpha \\cdot \\left(\\frac{V}{C}\\right)^\\beta\\right]$$
- **What It Supports**: Widely accepted standard macroscopic link performance function. Models non-linear impedance growth as volume approaches and exceeds nominal capacity.
- **Parameters**: Standard defaults ($\\alpha = 0.15, \\beta = 4.0$).
- **Limitations**: Overestimates link speeds at extreme saturation unless calibrated or supplemented with dynamic queuing; assumes steady-state uniform flow over the analysis period.
- **UrbanResilience Usage**: Core impedance engine in `src/simulation/traffic_math.py`. Parameters $\\alpha, \\beta$ are fully configurable.

### 2.2 Indian Highway Capacity Manual (Indo-HCM, 2017) & IRC:106-1990
- **Primary Sources**:
  - *CSIR-CRRI (2017). "Indian Highway Capacity Manual (Indo-HCM)." Council of Scientific and Industrial Research, New Delhi.*
  - *Indian Roads Congress (1990). "IRC:106-1990: Guidelines for Capacity of Urban Roads in Plain Areas."*
- **What It Supports**: Rigorous scientific justification for **Passenger Car Unit (PCU)** equivalents in heterogeneous, lane-less Indian traffic:
  - Two-Wheelers (2W): $0.5 - 0.75\\text{ PCU}$
  - Auto-Rickshaws (3W): $1.0 - 1.2\\text{ PCU}$
  - Standard Cars: $1.0\\text{ PCU}$
  - City Buses / Heavy Vehicles: $2.5 - 3.0\\text{ PCU}$
- **Limitations**: PCU values vary dynamically with traffic composition and flow speed rather than remaining strictly static.
- **UrbanResilience Usage**: Justifies vehicle conversion factors and capacity thresholds for Indian arterial corridors.

### 2.3 Macroscopic Fundamental Diagram (MFD) & Greenshields Model
- **Primary Sources**:
  - *Greenshields, B.D. (1935). "A Study of Traffic Capacity." Proceedings of the Highway Research Board.*
  - *Daganzo, C.F. & Geroliminis, N. (2008). "An analytical approximation for the macroscopic fundamental diagram of urban networks." Transportation Research Part B.*
- **What It Supports**: Establishes the relationship between traffic density ($k$), speed ($v$), and flow ($q = k \\cdot v$). Proves the existence of a critical network density beyond which network throughput collapses (gridlock).
- **UrbanResilience Usage**: Theoretical backing for cascading saturation thresholds ($V/C > 1.0$).

### 2.4 Traffic Assignment Principles (Wardrop's Equilibria)
- **Primary Source**: *Wardrop, J.G. (1952). "Some Theoretical Aspects of Road Traffic Research." Proceedings of the Institution of Civil Engineers, 1(3), 325-362.*
- **What It Supports**:
  - **User Equilibrium (UE)**: No driver can unilaterally reduce travel time by switching paths.
  - **All-or-Nothing (AON) Assignment**: Vehicles take deterministic shortest paths under current link travel times.
- **UrbanResilience Usage**: AON shortest path is used for the Phase 1 deterministic prototype, with bounded iterative reassignment provided for scenario evaluation.

---

## 3. Literature Evaluation Matrix

| Model / Concept | Primary Reference | What It Supports in UrbanResilience | Known Limitations | Prototype Integration Status |
|---|---|---|---|---|
| **BPR Function** | BPR (1964), FHWA | Link traversal time as a function of volume-to-capacity saturation. | Static steady-state assumption. | **Implemented in `traffic_math.py`** |
| **Indo-HCM PCU Equivalents** | CSIR-CRRI (2017) | Heterogeneous Indian traffic conversion (2W/3W/buses). | Complex dynamic PCUs simplified for MVP. | **Documented & Ready for Phase 2** |
| **Dijkstra Shortest Path** | Dijkstra (1959) | Deterministic route selection on directed road graphs. | Assumes single-criterion least cost. | **Implemented in `graph.py`** |
| **Cascading Network Failure** | Gao et al. (2012), Nature | Interdependent network stress propagation. | Physical failure vs congestion overload. | **Implemented in `cascade_model.md`** |
