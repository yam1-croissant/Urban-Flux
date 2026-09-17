# UrbanFlux

> **Deterministic Digital Twin & Cascading Infrastructure Disruption Simulator for Bengaluru**

UrbanFlux models multi-modal urban traffic cascades, critical facility access (trauma centers, tech corridors, arterials), and evaluates dynamic disruption scenarios using deterministic network flow algorithms and ML-backed empirical observations.

---

## 🚀 Quickstart with Docker (Recommended)

Run the full stack (FastAPI simulation backend + React/Vite/Tailwind frontend behind Nginx reverse proxy):

```bash
docker compose up --build
```

Once running:
- **Frontend App**: [http://localhost:3000](http://localhost:3000)
- **Backend API & Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

To shut down:
```bash
docker compose down
```

---

## 🛠️ Docker Live-Reload Development

For live-reloading during code modifications:

```bash
docker compose -f docker-compose.dev.yml up
```

- **Frontend Dev Server (Vite HMR)**: [http://localhost:5173](http://localhost:5173)
- **Backend API (Uvicorn Reload)**: [http://localhost:8000](http://localhost:8000)

---

## 💻 Local Setup (Without Docker)

### 1. Backend Service
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run backend API
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Application
```bash
cd frontend
npm install
npm run dev
```

### 3. Run Test Suite
```bash
pytest -v
```

---

## 📦 Container Architecture

```
                 ┌─────────────────────────────┐
                 │        User Browser         │
                 └──────────────┬──────────────┘
                                │
                        Port 3000 (HTTP)
                                │
                 ┌──────────────▼──────────────┐
                 │      urbanflux-frontend     │
                 │   Nginx Alpine (Multi-stage)│
                 │  - Serves React SPA (dist)  │
                 │  - Proxies /api/ & /health  │
                 └──────────────┬──────────────┘
                                │
               Internal Docker Network (Port 8000)
                                │
                 ┌──────────────▼──────────────┐
                 │      urbanflux-backend      │
                 │       Python 3.11-slim      │
                 │  - FastAPI + Uvicorn        │
                 │  - Graph Simulation Engine  │
                 │  - ML Corridor Predictions  │
                 └─────────────────────────────┘
```
