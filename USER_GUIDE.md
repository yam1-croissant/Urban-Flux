# UrbanResilience — User Guide & Operational Manual

The complete, illustrated User Guide with high-resolution screenshots and detailed explanations is available at:

👉 **[`docs/USER_GUIDE.md`](docs/USER_GUIDE.md)**

---

## Quick Launch Summary

### 1. Start the Backend API (Terminal 1)
```bash
PYTHONPATH=./lib:. python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
- Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

### 2. Launch the Digital Twin Map Interface (Terminal 2)
```bash
cd frontend/dist
python3 -m http.server 5173
```
- Open Browser to: 👉 **[http://localhost:5173](http://localhost:5173)**

---

## Screenshot Previews

### 1. Digital Twin Overview
![Digital Twin Overview](docs/images/01_digital_twin_overview.png)

### 2. Disruption Studio & Link Inspector
![Disruption Studio & Inspector](docs/images/02_disruption_studio_and_inspector.png)

### 3. Cascading Failure Dynamics
![Cascading Failure Dynamics](docs/images/03_cascade_propagation_diagram.png)

### 4. Causal Explainability & Criticality Rankings
![Explainability & Criticality Rankings](docs/images/04_explainability_and_criticality_panels.png)

### 5. Policy Mitigation Comparison
![Policy Mitigation Comparison](docs/images/05_scenario_comparison_modal.png)

---
*For full technical details, mathematical formulations, and step-by-step feature tours, see [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md).*

