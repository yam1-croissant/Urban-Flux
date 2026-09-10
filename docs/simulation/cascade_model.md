# UrbanResilience — Cascading Overload Model

## 1. Causal Cascade Mechanism

The core premise of UrbanResilience is demonstrating that urban infrastructure vulnerability does not stop at the boundary of a physical hazard. Instead, disruptions propagate through behavioral rerouting and network topology:

$$\\text{Primary Disruption} \\longrightarrow \\text{Link Infeasibility} \\longrightarrow \\text{Demand Detour} \\longrightarrow \\text{Flow Concentration} \\longrightarrow \\text{Secondary Overload} \\longrightarrow \\text{Critical Service Access Degradation}$$

---

## 2. Overload Classification Taxonomy

To prevent false alarms and distinguish baseline bottlenecks from true cascading effects, links are categorized into three mutually exclusive groups:

1. **Primary Disrupted Edges (`primary_disrupted_edges`)**:
   Road links directly subject to capacity reduction or complete closure ($r > 0$ or $\\text{capacity\\_multiplier} < 1.0$).
2. **Newly Overloaded Edges (`newly_overloaded_edges`)**:
   Open links that **exceed the saturation threshold ($V/C > \\text{overload\\_vc\\_threshold}$)** in the scenario but were **operating within capacity ($V/C \le \\text{overload\\_vc\\_threshold}$)** during baseline conditions. These represent true **cascading spillovers**.
3. **Persistently Overloaded Edges (`persistently_overloaded_edges`)**:
   Links that were already congested in baseline conditions ($V/C > \\text{threshold}$) and remain overloaded in the scenario.

---

## 3. Important Physical Boundary Distinction

> [!IMPORTANT]
> **Congestion Consequence vs. Physical Failure**:
> In the Part B simulation, an "overload" ($V/C > 1.0$) means that traffic demand exceeds design throughput, triggering steep BPR delays and queuing.
>
> An overloaded link **does not automatically collapse or physically close**. Treating high congestion as automatic link closure would create unrealistic explosive cascades without empirical foundation.

---

## 4. Critical Service Accessibility Assessment

Emergency services (hospitals, trauma centers, fire stations) are attached to specific graph vertices as `CriticalAsset` objects.

For all demand flows originating from or destined to a critical asset node, the simulation computes:
- **`baseline_access_time_minutes`**: Unimpeded or normal-day travel time.
- **`scenario_access_time_minutes`**: Post-disruption travel time across the network.
- **`response_time_delta_minutes`**: Extra transit time incurred by emergency vehicles or patients.
- **`access_lost`**: Boolean indicating if the critical facility is completely unreachable.

---

## 5. Termination Rules & Iteration Control

- **Single-Pass Assignment (`max_reassignment_iterations = 1`)**:
  Default mode for fast, deterministic evaluation.
- **Iterative Assignment (`max_reassignment_iterations > 1`)**:
  Iteratively updates edge impedance weights using congested BPR travel times until link flow changes fall below `convergence_tolerance` or max iterations are reached.
