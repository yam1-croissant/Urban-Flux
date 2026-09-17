# UrbanResilience — Digital Twin & Infrastructure Cascade Simulator
## Official User Guide & Operational Manual

---

## 1. Executive Summary

**UrbanResilience** is a digital twin and simulation platform designed to model how localized urban disruptions (such as bridge structural failures, severe monsoon flooding, or metro construction barricades) propagate across metropolitan transit networks, trigger secondary cascading overloads, and degrade access to critical civic infrastructure like Level-1 emergency trauma centers.

### The Core Causal Cascade
Traditional navigation apps simply route drivers around closures without modeling the systemic consequences. UrbanResilience models the complete cascade chain:

$$\text{Primary Hazard} \longrightarrow \text{Capacity Reduction } (r) \longrightarrow \text{Commuter Diversion} \longrightarrow \text{Secondary Overload } (V/C > 1.0) \longrightarrow \text{Critical Service Delay}$$

---

## 2. Quick Launch Guide

The entire application runs locally without external cloud dependencies, API keys, or database configurations.

### Clone the Repository
Clone the repository at the `backupbackup` branch:
```bash
git clone -b backupbackup https://github.com/yam1-croissant/infrastructure-cascading.git
cd infrastructure-cascading
```

### Install Dependencies
```bash
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

### Run on 2 Separate Terminals

#### Terminal 1: Start Backend API Server
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

#### Terminal 2: Start Frontend Interface
```bash
npm --prefix frontend run dev
```

#### Finally open in your browser:
👉 **[http://localhost:5173/](http://localhost:5173/)**

---

## 3. Visual Interface Tour

![UrbanResilience Digital Twin Overview](images/01_digital_twin_overview.png)

### Core UI Layout
1. **Header Navigation Bar**: Displays system status (`● SIMULATION ACTIVE`), mode switcher between **Real Bengaluru Map** and **Schematic Twin**, the **Compare Policies** modal launcher, and the interactive **Guide** tour.
2. **Key Impact Metrics (Top Grid)**: Four real-time KPIs summarizing network damage:
   - **Net System Delay**: Total commuter vehicle-hours lost across the metropolitan network (e.g. `+387.8 veh-hours`).
   - **Hospital Access Delay**: Travel time degradation to emergency trauma centers (e.g. Manipal Hospital transit jumping from `6.8 min → 24.4 min`).
   - **Cascade Overloads**: Count of secondary bottleneck corridors that breached physical capacity ($V/C > 1.0$).
   - **Net Trip Time Change**: Average percentage increase in commuter travel duration across all active origin-destination pairs.
3. **Disruption Studio (Left Panel)**: Selection of pre-configured scenario presets and fine-grained link inspection sliders.
4. **Bird's-Eye Map Canvas (Center)**: Dark-mode geographic rendering of Bengaluru corridors (Silk Board, Koramangala, Indiranagar, Domlur, Whitefield).
5. **Causal Explainability & Criticality (Right Panel)**: Plain-English explanation of why delays occurred and ranking of most vulnerable road segments.

---

## 4. Scenario Creation & Disruption Studio

![Disruption Studio & Link Inspector](images/02_disruption_studio_and_inspector.png)

The **Disruption Studio** lets city planners and emergency managers simulate realistic shock scenarios:

### 4.1 Preset Incident Categories
- 🌧️ **Monsoon & Flooding**: Flash flooding, canal breaches, and underpass waterlogging (e.g., *Bellandur ORR & Sarjapur Flash Flood*, *Central Arterial Waterlogging*).
- 🚧 **Construction & Roadwork**: Metro Phase 3 barricades, pipeline excavations, and utility lane reductions.
- ⛔ **Infrastructure Closure**: Emergency structural inspections or bridge shutdowns (e.g., *Silk Board Elevated Flyover 100% Closure*).
- ⚡ **Events & Peak Demand**: Tech corridor morning rushes, commercial summits, and stadium event surges.
- 🚑 **Emergency Response**: Hospital green-corridors, traffic warden deployment, and signal priority routing.

### 4.2 Using the Link Inspector
Click any road segment on the map or schematic to open the **Link Inspector**:
1. **Inspect Attributes**: View nominal capacity, free-flow speed, baseline flow, and current $V/C$ stress.
2. **Adjust Capacity Slider**: Drag the capacity multiplier from `1.00` (100% capacity) down to `0.00` (complete physical closure).
3. **Quick Action Presets**:
   - `100% Closed`: Complete structural or security shutdown.
   - `50% Waterlog`: Simulated flood reducing half of the travel lanes.
   - `25% Barricade`: Single-lane utility construction blockage.
   - `Reset Link`: Restores the link to nominal design capacity.
4. **Execute**: Click **"Run Simulation Engine"** to recalculate traffic flows and cascade propagation.

---

## 5. Cascading Failure Propagation Dynamics

![Cascading Failure Propagation Dynamics](images/03_cascade_propagation_diagram.png)

### The 4 Propagation Stages
When an acute disruption occurs, the simulation models how stress moves through the urban network:

1. **Stage 1 — Primary Incident ($t = 0\text{ min}$)**:
   - Primary link (e.g., *Silk Board Flyover / Bridge_A_B*) capacity drops to zero ($C_{\text{eff}} = 0$).
   - The link becomes impassable; Dijkstra routing weight explodes to $\infty$.
2. **Stage 2 — Demand Diversion ($t = 5\text{ min}$)**:
   - 1,800 veh/hr of displaced commuter and patient volume is forced to detour onto secondary corridors (*Cambridge Layout Collector* and *Domlur Canal Road*).
3. **Stage 3 — Secondary Bottleneck Overload ($t = 15\text{ min}$)**:
   - The narrow 2-lane *Domlur Canal Bottleneck* experiences an assigned volume surge from 500 to 2,300 veh/hr.
   - Volume-to-Capacity ratio jumps from $0.36 \longrightarrow \mathbf{1.64}$, triggering severe secondary congestion miles away from the initial bridge closure.
4. **Stage 4 — Critical Asset Degradation ($t = 30\text{ min}$)**:
   - Emergency ambulance transit time to *Manipal Level-1 Trauma Center* surges by **+17.5 minutes (+256%)**, breaching the critical 15-minute emergency survival window.

### Bureau of Public Roads (BPR) Delay Formulation
Congested link travel time $t$ follows the classical BPR relationship:

$$t = t_0 \left[1 + \alpha \left(\frac{V}{C}\right)^\beta\right]$$

- **Uncongested ($V/C \ll 1.0$)**: $t \approx t_0$ (free-flow travel time).
- **At Capacity ($V/C = 1.0$)**: Travel time increases by factor $(1 + \alpha) = 1.15 \times t_0$.
- **Oversaturated ($V/C > 1.0$)**: Congestion delay surges steeply with power $\beta = 4.0$.

---

## 6. AI Causal Explainability & Criticality Rankings

![Explainability & Criticality Rankings](images/04_explainability_and_criticality_panels.png)

### 6.1 The "Why Did This Happen?" Engine
Rather than presenting opaque numbers, UrbanResilience automatically generates deterministic, causal narratives:
- `"Complete closure on 'Bridge_A_B' removed 2,400 veh/hr of operational corridor capacity."`
- `"Commuters on Zone_A → Zone_D (1,200 veh/hr) diverted away from disrupted corridors (+6.0 km detour)."`
- `"Secondary cascade overload on 'Bottleneck_E_F': volume/capacity jumped from 0.36 to 1.64 due to diverted flow."`
- `"Emergency access to HOSPITAL 'Hospital_C' degraded by +17.5 minutes (+256%, from 6.8 to 24.4 min)."`
- `"Overall network congestion penalty: +387.8 vehicle-hours of aggregate traffic delay."`

### 6.2 System Criticality Rankings
The platform scores and ranks network links by vulnerability combining **network betweenness centrality**, **flow load**, and **hospital access priority**:

| Rank | Link ID | Facility Name | Vulnerability | Operational Role |
|:---:|---|---|:---:|---|
| **#1** | `Bridge_A_B` | Silk Board Elevated Flyover | **0.96** | Primary arterial spine connecting south suburbs to IT corridors |
| **#2** | `Bottleneck_E_F` | Domlur Canal Narrow Bottleneck | **0.91** | Narrow 2-lane bottleneck absorbing 85% of diverted flow |
| **#3** | `Arterial_B_C` | Old Airport Hospital Approach | **0.85** | Primary life-safety access corridor to Manipal Trauma Center |
| **#4** | `Collector_A_E` | Agara Bypass Collector | **0.78** | Secondary collector surging into overload during flyover closures |
| **#5** | `Connector_G_C` | Indiranagar Emergency Link | **0.62** | Under-utilized alternate relief corridor for active mitigation |

---

## 7. Scenario Mitigation & Resilience Comparison

![Scenario Comparison Modal](images/05_scenario_comparison_modal.png)

Urban planners can evaluate proposed interventions before deploying resources on the ground.

Click the **"Compare"** button in the header to open the side-by-side comparison modal:

### Case Study: Unmitigated Closure vs Active Police Intervention
- **Scenario A (Unmitigated Closure)**: Silk Board Flyover closes with no active traffic control.
  - Total Lost Vehicle-Hours: **+413.9 veh-hrs**
  - Newly Overloaded Bottlenecks: **2 corridors (V/C 1.64 & 1.33)**
  - Hospital Response Delay: **+17.5 min (24.4 min total)**
- **Scenario B (Active Police Mitigation)**: Traffic wardens deploy to the northern relief corridor (*Connector_A_G*) and provide signal green-waves.
  - Total Lost Vehicle-Hours: **+70.7 veh-hrs (82.9% reduction)**
  - Newly Overloaded Bottlenecks: **0 corridors (Gridlock eliminated)**
  - Hospital Response Delay: **8.2 min (93% delay recovery)**

### Executive Verdict
> *"Scenario B demonstrates dramatic resilience superiority: By deploying traffic wardens and prioritizing signal green-waves on the West-North Relief corridor, the city saves **343.2 vehicle-hours of delay (-82.9%)** and preserves emergency ambulance access to Manipal Hospital."*

---

## 8. Command-Line Verification & Testing

For automated quality assurance and verification:

### Run the Standalone Traffic Mathematics Demo:
```bash
python3 examples/traffic_math_demo.py
```
*Generates formatted terminal tables comparing baseline vs 10%, 25%, 50%, and 100% capacity loss under peak vs off-peak demand.*

### Run the Network Disruption Demo:
```bash
python3 examples/network_disruption_demo.py
```
*Executes the complete network routing and secondary overload cascade algorithm directly in your console.*

### Run the Full 66-Test Automated Test Suite:
```bash
PYTHONPATH=./lib:. python3 -m pytest -p no:anyio tests/ -v
```
*Validates traffic mathematics, graph directionality, Dijkstra tie-breaking, cascade detection, and all FastAPI endpoints.*

---

## 9. Troubleshooting & FAQ

### Q: Why does the map show data even if the backend is not running?
The frontend contains embedded canonical benchmark snapshots of Bengaluru. If the backend is temporarily offline, the frontend seamlessly operates in offline demonstration mode and automatically connects to `http://localhost:8000` once the server is launched.

### Q: How do I test custom traffic sensor data?
You can upload CSV or JSON traffic count files via the API:
```bash
curl -X POST http://localhost:8000/api/data/upload \
  -F "data_type=traffic_count" \
  -F "file=@sample_sensor_counts.csv"
```
The backend normalizes disparate column names (`traffic_volume`, `veh_count` $\to$ `flow`) and validates all numerical inputs.

### Q: How are road closures handled in routing?
When capacity multiplier $r = 0.00$, the road capacity becomes zero, its $V/C \to \infty$, and its travel time becomes $\infty$. The Dijkstra shortest-path engine excludes the edge from the active graph, preventing impossible traversal.

---

## 10. Summary of Key Files

| Category | File | Description |
|---|---|---|
| **User Guide** | [`docs/USER_GUIDE.md`](file:///home/aaryan/mhash/infrastructure-cascading/docs/USER_GUIDE.md) | This operational user manual with screenshots |
| **API Contract** | [`docs/api.md`](file:///home/aaryan/mhash/infrastructure-cascading/docs/api.md) | Formal REST API schema and endpoint documentation |
| **Domain Model** | [`docs/FINAL_DOMAIN_MODEL.md`](file:///home/aaryan/mhash/infrastructure-cascading/docs/FINAL_DOMAIN_MODEL.md) | Theoretical foundation and domain architecture |
| **Backend App** | [`backend/main.py`](file:///home/aaryan/mhash/infrastructure-cascading/backend/main.py) | FastAPI digital twin server and ML inference engine |
| **Simulation Core** | [`src/simulation/`](file:///home/aaryan/mhash/infrastructure-cascading/src/simulation/) | Mathematical BPR formulation, graph models, and routing |
| **Frontend UI** | [`frontend/`](file:///home/aaryan/mhash/infrastructure-cascading/frontend/) | React 18 + Leaflet digital twin web application |

