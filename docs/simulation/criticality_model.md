# UrbanFlux — Infrastructure Criticality Model

## 1. Objective & Main Question

> **Before any disruption occurs, how do we identify which road links and intersections are disproportionately critical to citywide resilience?**

In urban networks, link importance is not merely a function of physical road width or speed limit. A 2-lane bridge providing sole access to a regional trauma center is vastly more critical than a 6-lane peripheral boulevard with abundant parallel detours.

The **Criticality Model** provides an a priori quantitative vulnerability score for every network asset, combining topological graph centrality, traffic demand volume, and critical public service dependency.

---

## 2. Multi-Criteria Criticality Formulation

For each directed edge $e = (u, v) \\in E$, the composite **Infrastructure Criticality Index** ($S_{\\text{crit}}(e) \\in [0.0, 1.0]$) is defined as:

$$S_{\\text{crit}}(e) = w_{\\text{topo}} \\cdot C_{\\text{betweenness}}(e) + w_{\\text{flow}} \\cdot S_{\\text{flow}}(e) + w_{\\text{service}} \\cdot S_{\\text{service}}(e) + w_{\\text{detour}} \\cdot S_{\\text{detour}}(e)$$

subject to:
$$w_{\\text{topo}} + w_{\\text{flow}} + w_{\\text{service}} + w_{\\text{detour}} = 1.0$$

---

## 3. Pillar Metric Definitions

### 3.1 Topological Betweenness Centrality ($C_{\\text{betweenness}}$)
Quantifies the fraction of all network shortest paths that traverse edge $e$:

$$C_{\\text{betweenness}}(e) = \\sum_{s \\ne t} \\frac{\\sigma_{st}(e)}{\\sigma_{st}}$$

- $\\sigma_{st}$: Total number of shortest paths from node $s$ to node $t$.
- $\\sigma_{st}(e)$: Number of shortest paths from $s$ to $t$ passing through edge $e$.
- Normalized to $[0.0, 1.0]$ across all edges in the graph.

### 3.2 Traffic Demand Exposure ($S_{\\text{flow}}$)
Measures baseline flow pressure and saturation on the asset:

$$S_{\\text{flow}}(e) = \\min\\left(1.0, \\frac{V(e)}{C_{\\text{nom}}(e)}\\right)$$

- High baseline $V/C$ indicates that the asset operates near capacity with zero tolerance for sudden demand surges.

### 3.3 Critical Service Dependency ($S_{\\text{service}}$)
Measures whether the edge is located on the primary access corridor for high-priority civic infrastructure (e.g., Level-1 Trauma Centers, Fire Stations, Emergency Evacuation Shelters):

$$S_{\\text{service}}(e) = \\frac{\\sum_{k \\in \\text{CriticalAssets}} \\omega_k \\cdot \\mathbb{I}(e \\in \\text{Path}(s_i \\to k))}{\\sum_k \\omega_k}$$

- $\\omega_k$: Priority weight of critical asset $k$ (e.g., Hospital = $1.5$, General Zone = $1.0$).
- $\\mathbb{I}$: Indicator function ($1$ if edge $e$ lies on the optimal path to asset $k$, $0$ otherwise).

### 3.4 Detour Impedance Penalty ($S_{\\text{detour}}$)
Evaluates the marginal penalty incurred by the network if edge $e$ were closed:

$$S_{\\text{detour}}(e) = \\min\\left(1.0, \\frac{t_{\\text{alternate}}(e) - t_0(e)}{t_0(e)}\\right)$$

- If no alternate route exists ($t_{\\text{alternate}} = \\infty$), $S_{\\text{detour}}(e) = 1.0$ (Bridge / Single Point of Failure).

---

## 4. Default Configuration & Parameter Choices

| Weight Parameter | Default Value | Rationale |
|---|---|---|
| $w_{\\text{topo}}$ | $0.25$ | Measures structural topological bridging across network zones. |
| $w_{\\text{flow}}$ | $0.25$ | Captures daily commuter volume and baseline bottleneck risk. |
| $w_{\\text{service}}$ | $0.30$ | Prioritizes emergency vehicle accessibility to healthcare and life-safety assets. |
| $w_{\\text{detour}}$ | $0.20$ | Penalizes links lacking viable parallel detour capacity. |

*(All weights are configurable in `SimulationConfig` to enable user-specific sensitivity analyses).*

---

## 5. Worked Example on Synthetic Test Network

In the standard 6-node synthetic network (`examples/network_disruption_demo.py`):
1. **`Bridge_A_B`**:
   - High betweenness ($0.85$), high flow ($V/C = 0.83$), primary route to `Hospital_C` ($1.0$), moderate detour penalty ($0.91$).
   - **Composite Criticality**: $S_{\\text{crit}} = 0.25(0.85) + 0.25(0.83) + 0.30(1.00) + 0.20(0.91) = \\mathbf{0.90}$ $\\rightarrow$ **TIER 1 CRITICAL ASSET (High Vulnerability)**.
2. **`Connector_F_D`**:
   - Low betweenness ($0.20$), low flow ($V/C = 0.06$), non-critical asset route ($0.0$), low detour penalty ($0.15$).
   - **Composite Criticality**: $S_{\\text{crit}} = 0.25(0.20) + 0.25(0.06) + 0.30(0.00) + 0.20(0.15) = \\mathbf{0.09}$ $\\rightarrow$ **TIER 3 NON-CRITICAL LINK**.
