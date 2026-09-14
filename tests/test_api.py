"""Integration and functional tests for the UrbanFlux FastAPI backend."""

import os
import sys
import io
import pytest

# Ensure lib and repo root are in sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB_DIR = os.path.join(REPO_ROOT, "lib")
if LIB_DIR not in sys.path and os.path.exists(LIB_DIR):
    sys.path.insert(0, LIB_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestHealthAndMetadata:
    """Tests for health check and root service metadata."""

    def test_health_check_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data == {"status": "ok"}

    def test_root_endpoint_returns_sitemap(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "endpoints" in data
        assert data["endpoints"]["network"] == "/api/network"
        assert data["endpoints"]["simulate"] == "/api/simulate"


class TestNetworkEndpoint:
    """Tests for GET /api/network."""

    def test_get_network_default(self):
        response = client.get("/api/network")
        assert response.status_code == 200
        data = response.json()

        assert data["network_id"] == "demo_city"
        assert "nodes" in data
        assert "edges" in data
        assert "pois" in data
        assert "metadata" in data

        assert len(data["nodes"]) >= 6
        assert len(data["edges"]) >= 7
        assert len(data["pois"]) >= 4

        # Verify coordinates exist for map rendering
        first_edge = data["edges"][0]
        assert "coordinates" in first_edge
        assert len(first_edge["coordinates"]) == 2  # [[lon1, lat1], [lon2, lat2]]

        # Verify data provenance labels
        provenance = data["metadata"]["provenance"]
        assert "road_geometry" in provenance
        assert "OBSERVED" in provenance["road_geometry"]

    def test_get_network_nonexistent(self):
        response = client.get("/api/network?network_id=nonexistent_city")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestSimulationEndpoint:
    """Tests for POST /api/simulate."""

    def test_simulate_baseline_no_disruptions(self):
        payload = {
            "network_id": "demo_city",
            "time_period": "weekday_rush_hour",
            "disruptions": [],
        }
        response = client.post("/api/simulate", json=payload)
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "completed"
        assert data["scenario_id"] == "baseline_weekday_rush_hour"
        assert data["metrics"]["total_delay_change_veh_hours"] == 0.0
        assert data["metrics"]["newly_overloaded_count"] == 0
        assert data["metrics"]["unserved_trips_count"] == 0
        assert len(data["failed_assets"]) == 0

    def test_simulate_bridge_closure_triggers_cascade(self):
        payload = {
            "network_id": "demo_city",
            "time_period": "weekday_rush_hour",
            "disruptions": [
                {
                    "asset_id": "Bridge_A_B",
                    "type": "closure",
                    "capacity_multiplier": 0.0,
                }
            ],
        }
        response = client.post("/api/simulate", json=payload)
        assert response.status_code == 200
        data = response.json()

        # 1. Disruption verified
        assert len(data["failed_assets"]) == 1
        assert data["failed_assets"][0]["asset_id"] == "Bridge_A_B"

        # 2. Delay increases
        metrics = data["metrics"]
        assert metrics["total_delay_change_veh_hours"] > 0.0
        assert metrics["delay_change_percent"] > 100.0

        # 3. Cascade secondary overload
        assert metrics["newly_overloaded_count"] >= 1

        # 4. Critical service (hospital access time degraded)
        hospital_impact = next(
            (c for c in data["critical_assets"] if c["asset_type"] == "hospital"), None
        )
        assert hospital_impact is not None
        assert hospital_impact["response_time_delta_minutes"] > 0.0

        # 5. Explainability narratives generated
        explainability = data["explainability"]
        assert len(explainability) >= 4
        assert any("Bridge_A_B" in s for s in explainability)
        assert any("diverted" in s.lower() for s in explainability)

    def test_simulate_partial_capacity_reduction(self):
        payload = {
            "network_id": "demo_city",
            "time_period": "weekday_rush_hour",
            "disruptions": [
                {
                    "asset_id": "Bridge_A_B",
                    "type": "partial_closure",
                    "capacity_multiplier": 0.50,
                }
            ],
        }
        response = client.post("/api/simulate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert len(data["failed_assets"]) == 1
        assert data["failed_assets"][0]["capacity_multiplier"] == 0.50

    def test_simulate_invalid_asset_returns_400(self):
        payload = {
            "network_id": "demo_city",
            "disruptions": [
                {
                    "asset_id": "Unknown_Bridge_999",
                    "type": "closure",
                    "capacity_multiplier": 0.0,
                }
            ],
        }
        response = client.post("/api/simulate", json=payload)
        assert response.status_code == 400
        assert "Unknown asset_id" in response.json()["detail"]


class TestScenariosEndpoint:
    """Tests for GET /api/scenarios and POST /api/scenarios/compare."""

    def test_list_scenarios_returns_presets(self):
        response = client.get("/api/scenarios")
        assert response.status_code == 200
        data = response.json()
        assert "presets" in data
        assert len(data["presets"]) >= 4

        preset_ids = [p["id"] for p in data["presets"]]
        assert "scenario_bridge_closure_rush_hour" in preset_ids
        assert "scenario_waterlogging_rush_hour" in preset_ids

    def test_get_scenario_by_id_found(self):
        response = client.get("/api/scenarios/scenario_bridge_closure_rush_hour")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "scenario_bridge_closure_rush_hour"
        assert len(data["disruptions"]) == 1

    def test_get_scenario_by_id_not_found(self):
        response = client.get("/api/scenarios/nonexistent_scenario")
        assert response.status_code == 404

    def test_compare_scenarios_preset_ids(self):
        payload = {
            "scenario_a_id": "scenario_bridge_closure_rush_hour",
            "scenario_b_id": "scenario_roadwork_construction",
        }
        response = client.post("/api/scenarios/compare", json=payload)
        assert response.status_code == 200
        data = response.json()

        assert "scenario_a" in data
        assert "scenario_b" in data
        assert "delta" in data

        delta = data["delta"]
        assert "delay_difference_veh_hours" in delta
        assert "mitigation_verdict" in delta
        assert len(delta["mitigation_verdict"]) > 10


class TestDataUploadEndpoint:
    """Tests for POST /api/data/upload (JSON and CSV)."""

    def test_upload_json_traffic_counts(self):
        payload = {
            "data_type": "traffic_count",
            "records": [
                {"road_id": "Bridge_A_B", "traffic_volume": 1250.0, "time": "2026-09-12T08:30:00"},
                {"link_id": "Collector_A_E", "veh_count": 450.0, "date": "2026-09-12T08:30:00"},
            ],
        }
        response = client.post("/api/data/upload", json=payload)
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["total_records"] == 2
        assert data["accepted_records"] == 2
        assert data["rejected_records"] == 0
        assert "flow" in data["column_mapping_applied"].values()

    def test_upload_csv_speed_observations(self):
        csv_content = (
            "road_id,avg_speed,timestamp\n"
            "Bridge_A_B,55.4,2026-09-12T08:30:00\n"
            "Bottleneck_E_F,28.2,2026-09-12T08:30:00\n"
        )
        files = {"file": ("speeds.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
        data = {"data_type": "speed_observation"}

        response = client.post("/api/data/upload", files=files, data=data)
        assert response.status_code == 200
        res = response.json()
        assert res["accepted_records"] == 2
        assert "speed_kmh" in res["column_mapping_applied"].values()

    def test_upload_unsupported_data_type_returns_400(self):
        payload = {
            "data_type": "unsupported_metric_xyz",
            "records": [{"some": "data"}],
        }
        response = client.post("/api/data/upload", json=payload)
        assert response.status_code == 400
        assert "Unsupported data_type" in response.json()["detail"]

    def test_upload_malformed_records_rejected(self):
        payload = {
            "data_type": "traffic_count",
            "records": [
                {"flow": -500.0},  # Missing road_id and negative flow
            ],
        }
        response = client.post("/api/data/upload", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["accepted_records"] == 0
        assert data["rejected_records"] == 1
        assert "REJECTED" in data["normalized_preview"][0]["validation_status"]

