"""UrbanFlux — FastAPI Simulation Backend & Digital Twin Server."""

from __future__ import annotations

import csv
import io
import os
import sys
from typing import Any, Dict, List, Optional, Union

from fastapi import Body, FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure repo root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.simulation.graph import RoadNetwork
from src.simulation.models import (
    CriticalAsset,
    Disruption,
    DisruptionError,
    Edge,
    Node,
    ODDemand,
    SimulationConfig,
)
from src.simulation.simulation import simulate
from backend.schemas import (
    CriticalAssetSchema,
    CriticalServiceImpactResponse,
    DisruptionInput,
    EdgeEvaluationResponse,
    EdgeSchema,
    NodeSchema,
    ODRouteImpactResponse,
    ScenarioCompareRequest,
    ScenarioCompareResponse,
    ScenarioPreset,
    SimulateRequest,
    SimulateResponse,
)
from backend.services.ml_service import ml_service
from backend.bangalore_data import (
    BANGALORE_METRO_NODES,
    BANGALORE_METRO_EDGES,
    BANGALORE_METRO_CRITICAL_ASSETS,
    BANGALORE_METRO_POIS,
    BANGALORE_METRO_DEMANDS,
    BANGALORE_METRO_PRESETS,
)

app = FastAPI(
    title="UrbanFlux Digital Twin API",
    description="Deterministic traffic disruption, cascading overload, and critical facility accessibility simulation API.",
    version="1.0.0",
)

# Enable CORS for local Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================================
# Canonical Bengaluru Digital-Twin Benchmark Network
# =====================================================================

BENCHMARK_NODES = [
    NodeSchema(
        id="Zone_A",
        latitude=12.925,
        longitude=77.565,
        node_type="zone",
        label="Banashankari / West Zone",
        description="High-density residential commuter origin.",
    ),
    NodeSchema(
        id="Junction_B",
        latitude=12.917,
        longitude=77.623,
        node_type="junction",
        label="Silk Board Junction",
        description="Major arterial interchange & primary flyover bridge.",
    ),
    NodeSchema(
        id="Hospital_C",
        latitude=12.958,
        longitude=77.658,
        node_type="critical_asset",
        label="Manipal City Trauma Center",
        description="Level-1 regional emergency healthcare facility.",
    ),
    NodeSchema(
        id="Junction_E",
        latitude=12.923,
        longitude=77.648,
        node_type="junction",
        label="Agara / Sarjapur Junction",
        description="Southern secondary arterial junction.",
    ),
    NodeSchema(
        id="Junction_F",
        latitude=12.936,
        longitude=77.628,
        node_type="junction",
        label="Koramangala Sony World Hub",
        description="Commercial hub & narrow 2-lane residential bottleneck.",
    ),
    NodeSchema(
        id="Zone_D",
        latitude=12.975,
        longitude=77.720,
        node_type="zone",
        label="Whitefield Tech Corridor",
        description="Major IT & commercial employment center.",
    ),
    NodeSchema(
        id="Zone_G",
        latitude=12.978,
        longitude=77.640,
        node_type="junction",
        label="Indiranagar 100ft Hub",
        description="Northern auxiliary connection hub.",
    ),
]

BENCHMARK_EDGES = [
    EdgeSchema(
        id="Bridge_A_B",
        source="Zone_A",
        target="Junction_B",
        length_km=3.5,
        free_flow_speed_kmph=60.0,
        nominal_capacity_veh_per_hour=2400.0,
        road_class="primary_arterial",
        baseline_flow_veh_per_hour=400.0,
        name="Silk Board Elevated Bridge",
    ),
    EdgeSchema(
        id="Arterial_B_C",
        source="Junction_B",
        target="Hospital_C",
        length_km=2.5,
        free_flow_speed_kmph=50.0,
        nominal_capacity_veh_per_hour=2200.0,
        road_class="arterial",
        baseline_flow_veh_per_hour=200.0,
        name="Inner Ring Road to Hospital",
    ),
    EdgeSchema(
        id="Arterial_C_D",
        source="Hospital_C",
        target="Zone_D",
        length_km=3.0,
        free_flow_speed_kmph=50.0,
        nominal_capacity_veh_per_hour=2000.0,
        road_class="arterial",
        baseline_flow_veh_per_hour=100.0,
        name="Old Airport Road to Whitefield",
    ),
    EdgeSchema(
        id="Collector_A_E",
        source="Zone_A",
        target="Junction_E",
        length_km=4.5,
        free_flow_speed_kmph=45.0,
        nominal_capacity_veh_per_hour=1500.0,
        road_class="collector",
        baseline_flow_veh_per_hour=200.0,
        name="Agara Bypass Relief Collector",
    ),
    EdgeSchema(
        id="Bottleneck_E_F",
        source="Junction_E",
        target="Junction_F",
        length_km=5.0,
        free_flow_speed_kmph=40.0,
        nominal_capacity_veh_per_hour=1400.0,
        road_class="secondary",
        baseline_flow_veh_per_hour=500.0,
        name="Koramangala 80ft Bottleneck",
    ),
    EdgeSchema(
        id="Connector_F_C",
        source="Junction_F",
        target="Hospital_C",
        length_km=2.0,
        free_flow_speed_kmph=45.0,
        nominal_capacity_veh_per_hour=1600.0,
        road_class="collector",
        baseline_flow_veh_per_hour=150.0,
        name="Sony World to Hospital Link",
    ),
    EdgeSchema(
        id="Connector_F_D",
        source="Junction_F",
        target="Zone_D",
        length_km=2.5,
        free_flow_speed_kmph=45.0,
        nominal_capacity_veh_per_hour=1600.0,
        road_class="collector",
        baseline_flow_veh_per_hour=100.0,
        name="Koramangala to Tech Park Link",
    ),
    EdgeSchema(
        id="Connector_G_C",
        source="Zone_G",
        target="Hospital_C",
        length_km=3.0,
        free_flow_speed_kmph=45.0,
        nominal_capacity_veh_per_hour=1800.0,
        road_class="arterial",
        baseline_flow_veh_per_hour=300.0,
        name="Indiranagar Emergency Approach",
    ),
    EdgeSchema(
        id="Connector_A_G",
        source="Zone_A",
        target="Zone_G",
        length_km=6.0,
        free_flow_speed_kmph=40.0,
        nominal_capacity_veh_per_hour=1400.0,
        road_class="secondary",
        baseline_flow_veh_per_hour=200.0,
        name="West-North Relief Arterial",
    ),
]

BENCHMARK_CRITICAL_ASSETS = [
    CriticalAssetSchema(
        id="manipal_trauma_center",
        node_id="Hospital_C",
        asset_type="hospital",
        criticality_weight=1.5,
        name="Manipal City Trauma & Emergency Center",
    )
]

BENCHMARK_POIS = [
    {"id": "poi_hospital_c", "name": "Manipal Trauma Center", "category": "hospital", "node_id": "Hospital_C", "coordinates": [77.658, 12.958]},
    {"id": "poi_junction_b", "name": "Silk Board Junction", "category": "junction", "node_id": "Junction_B", "coordinates": [77.623, 12.917]},
    {"id": "poi_junction_f", "name": "Sony World Junction", "category": "junction", "node_id": "Junction_F", "coordinates": [77.628, 12.936]},
    {"id": "poi_zone_d", "name": "Whitefield Tech Hub", "category": "poi", "node_id": "Zone_D", "coordinates": [77.720, 12.975]},
]

DEFAULT_OD_DEMANDS = [
    ODDemand(
        id="OD_ZoneA_HospitalC",
        origin="Zone_A",
        destination="Hospital_C",
        demand_veh_per_hour=1200.0,
        time_period="morning_peak",
    ),
    ODDemand(
        id="OD_ZoneA_ZoneD",
        origin="Zone_A",
        destination="Zone_D",
        demand_veh_per_hour=400.0,
        time_period="morning_peak",
    ),
]

PRESETS: List[ScenarioPreset] = [
    ScenarioPreset(
        id="scenario_bridge_closure_rush_hour",
        name="Bridge Structural Closure",
        description="Acute 100% closure of Silk Board Bridge due to structural inspection.",
        icon="alert-triangle",
        disruptions=[
            DisruptionInput(asset_id="Bridge_A_B", disruption_type="closure", capacity_multiplier=0.0)
        ],
        recommended_mitigation_id="scenario_mitigation_active_reroute",
    ),
    ScenarioPreset(
        id="scenario_waterlogging_rush_hour",
        name="Monsoon Flash Flooding",
        description="50% capacity loss on primary corridors due to heavy waterlogging.",
        icon="cloud-rain",
        disruptions=[
            DisruptionInput(asset_id="Bridge_A_B", disruption_type="weather", capacity_multiplier=0.5),
            DisruptionInput(asset_id="Bottleneck_E_F", disruption_type="weather", capacity_multiplier=0.5),
        ],
    ),
    ScenarioPreset(
        id="scenario_roadwork_construction",
        name="Metro Line 3 Construction",
        description="Single lane blockage on Inner Ring Road approach reducing throughput by 35%.",
        icon="cone",
        disruptions=[
            DisruptionInput(asset_id="Arterial_B_C", disruption_type="construction", capacity_multiplier=0.65)
        ],
    ),
    ScenarioPreset(
        id="scenario_mitigation_active_reroute",
        name="Active Police Rerouting & Relief Lane",
        description="Deployment of traffic wardens and dedicated signal green-waves on North Relief corridor.",
        icon="shield-check",
        disruptions=[],
    ),
]

# Aliases for frontend convenience
PRESET_ALIAS_MAP = {
    "bridge_closure": "scenario_bridge_closure_rush_hour",
    "monsoon_flooding": "scenario_waterlogging_rush_hour",
    "metro_construction": "scenario_roadwork_construction",
    "mitigation_reroute": "scenario_mitigation_active_reroute",
}


def _build_sim_network() -> RoadNetwork:
    nodes = [
        Node(id=n.id, latitude=n.latitude, longitude=n.longitude, node_type=n.node_type)
        for n in BENCHMARK_NODES
    ]
    edges = [
        Edge(
            id=e.id,
            source=e.source,
            target=e.target,
            length_km=e.length_km,
            free_flow_speed_kmph=e.free_flow_speed_kmph,
            nominal_capacity_veh_per_hour=e.nominal_capacity_veh_per_hour,
            road_class=e.road_class,
            baseline_flow_veh_per_hour=e.baseline_flow_veh_per_hour,
        )
        for e in BENCHMARK_EDGES
    ]
    return RoadNetwork(nodes=nodes, edges=edges)


# =====================================================================
# API Endpoints
# =====================================================================

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def root_sitemap():
    return {
        "status": "online",
        "service": "UrbanFlux Digital Twin API",
        "version": "1.0.0",
        "endpoints": {
            "network": "/api/network",
            "simulate": "/api/simulate",
            "scenarios": "/api/scenarios",
            "upload": "/api/data/upload",
        },
    }


ALL_PRESETS = PRESETS + BANGALORE_METRO_PRESETS
PRESET_MAP = {p.id: p for p in ALL_PRESETS}
for k, v in PRESET_ALIAS_MAP.items():
    if v in PRESET_MAP:
        PRESET_MAP[k] = PRESET_MAP[v]


@app.get("/api/network")
def get_network(network_id: Optional[str] = "demo_city"):
    """Return the complete benchmark or Greater Bengaluru road network with nodes, edges, and critical assets."""
    valid_ids = {"demo_city", "bengaluru_core_demo", "bangalore_metro", "default", None}
    if network_id not in valid_ids:
        raise HTTPException(status_code=404, detail=f"Network '{network_id}' not found")

    if network_id == "bangalore_metro":
        coords_map = {n.id: [n.longitude or 77.6, n.latitude or 12.9] for n in BANGALORE_METRO_NODES}
        edges_with_coords = []
        for e in BANGALORE_METRO_EDGES:
            ed = e.model_dump()
            if not ed.get("coordinates"):
                src_coord = coords_map.get(e.source, [77.6238, 12.9175])
                tgt_coord = coords_map.get(e.target, [77.6600, 12.8450])
                ed["coordinates"] = [src_coord, tgt_coord]
            edges_with_coords.append(ed)

        return {
            "network_id": "bangalore_metro",
            "name": "Greater Bengaluru Metro Arterial Network",
            "nodes": [n.model_dump() for n in BANGALORE_METRO_NODES],
            "edges": edges_with_coords,
            "critical_assets": [c.model_dump() for c in BANGALORE_METRO_CRITICAL_ASSETS],
            "pois": BANGALORE_METRO_POIS,
            "metadata": {
                "city": "Bengaluru, Karnataka, India",
                "provenance": {
                    "road_geometry": "OBSERVED / OpenStreetMap",
                    "speed_limits": "OBSERVED / Bangalore Traffic Police Guidelines",
                    "capacities": "MODELED / IRC-106 Urban Capacity Standards",
                    "baseline_flows": "OBSERVED / Kaggle Bangalore Traffic Pulse (8,936 records)",
                    "od_demand": "SYNTHETIC / Commuter Distribution",
                    "criticality_weights": "MODELED / Emergency Response Framework",
                },
            },
        }

    coords_map = {n.id: [n.longitude or 77.6, n.latitude or 12.9] for n in BENCHMARK_NODES}

    edges_with_coords = []
    for e in BENCHMARK_EDGES:
        ed = e.model_dump()
        src_coord = coords_map.get(e.source, [77.565, 12.925])
        tgt_coord = coords_map.get(e.target, [77.623, 12.917])
        ed["coordinates"] = [src_coord, tgt_coord]
        edges_with_coords.append(ed)

    return {
        "network_id": network_id or "demo_city",
        "name": "Bengaluru Central Arterial Corridor",
        "nodes": [n.model_dump() for n in BENCHMARK_NODES],
        "edges": edges_with_coords,
        "critical_assets": [c.model_dump() for c in BENCHMARK_CRITICAL_ASSETS],
        "pois": BENCHMARK_POIS,
        "metadata": {
            "provenance": {
                "road_geometry": "OBSERVED (OSM 2026)",
                "traffic_counts": "ESTIMATED_PROBABILISTIC",
                "capacity": "CALCULATED_FORMULA",
            }
        },
    }


@app.get("/api/scenarios/presets", response_model=List[ScenarioPreset])
def get_presets_list():
    """Return pre-packaged realistic disruption and mitigation scenarios."""
    return ALL_PRESETS


@app.get("/api/scenarios")
def list_scenarios():
    """Return all preset scenario configurations."""
    return {"presets": [p.model_dump() for p in ALL_PRESETS]}


@app.get("/api/scenarios/{scenario_id}")
def get_scenario(scenario_id: str):
    """Retrieve specific preset scenario by ID."""
    canonical_id = PRESET_ALIAS_MAP.get(scenario_id, scenario_id)
    preset = PRESET_MAP.get(canonical_id) or PRESET_MAP.get(scenario_id)
    if not preset:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found")
    return preset.model_dump()


# =====================================================================
# Empirical ML Endpoints (Kaggle Bengaluru Traffic Pulse - 8,936 rows)
# =====================================================================

@app.get("/api/ml/metadata")
def get_ml_metadata():
    """Return metadata about trained Bangalore Traffic Pulse ML model."""
    return ml_service.get_metadata()


@app.get("/api/ml/corridors")
def get_ml_corridor_stats():
    """Return empirical statistics for all 16 corridors from 8,936 Bengaluru observations."""
    return {"corridors": ml_service.get_corridor_stats()}


@app.post("/api/ml/predict")
def predict_traffic_conditions(payload: Dict[str, Any] = Body(...)):
    """Run ML regressor prediction on a corridor given weather, incidents, and volume."""
    area_name = payload.get("area_name", "Koramangala")
    road_name = payload.get("road_name", "Sony World Junction")
    traffic_volume = float(payload.get("traffic_volume", 35000.0))
    incident_reports = int(payload.get("incident_reports", 1))
    weather_condition = payload.get("weather_condition", "Clear")
    roadwork = payload.get("roadwork", "No")

    try:
        res = ml_service.predict(
            area_name=area_name,
            road_name=road_name,
            traffic_volume=traffic_volume,
            incident_reports=incident_reports,
            weather_condition=weather_condition,
            roadwork=roadwork,
        )
        return res
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@app.post("/api/simulate")
def run_simulation(req: SimulateRequest):
    """Execute deterministic network disruption simulation and return complete cascading metrics."""
    is_metro = (
        req.network_id == "bangalore_metro"
        or any(d.asset_id.startswith("Edge_") for d in req.disruptions)
    )

    if is_metro:
        active_nodes = BANGALORE_METRO_NODES
        active_edges = BANGALORE_METRO_EDGES
        active_crits = BANGALORE_METRO_CRITICAL_ASSETS
        active_demands = BANGALORE_METRO_DEMANDS
    else:
        active_nodes = BENCHMARK_NODES
        active_edges = BENCHMARK_EDGES
        active_crits = BENCHMARK_CRITICAL_ASSETS
        active_demands = DEFAULT_OD_DEMANDS

    known_edge_ids = {e.id for e in active_edges}
    for d in req.disruptions:
        if d.asset_id not in known_edge_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown asset_id: '{d.asset_id}' not present in network",
            )

    net_nodes = [
        Node(id=n.id, latitude=n.latitude, longitude=n.longitude, node_type=n.node_type)
        for n in active_nodes
    ]
    net_edges = [
        Edge(
            id=e.id,
            source=e.source,
            target=e.target,
            length_km=e.length_km,
            free_flow_speed_kmph=e.free_flow_speed_kmph,
            nominal_capacity_veh_per_hour=e.nominal_capacity_veh_per_hour,
            road_class=e.road_class,
            baseline_flow_veh_per_hour=e.baseline_flow_veh_per_hour,
        )
        for e in active_edges
    ]
    net = RoadNetwork(nodes=net_nodes, edges=net_edges)

    # Map disruptions
    disruptions = [
        Disruption(
            asset_id=d.asset_id,
            disruption_type=d.disruption_type,
            capacity_multiplier=d.capacity_multiplier,
        )
        for d in req.disruptions
    ]

    # Map demands
    demands = active_demands
    if req.custom_demands:
        demands = [
            ODDemand(
                id=od.id,
                origin=od.origin,
                destination=od.destination,
                demand_veh_per_hour=od.demand_veh_per_hour,
                time_period=od.time_period,
                vehicle_class=od.vehicle_class,
            )
            for od in req.custom_demands
        ]

    crit_assets = [
        CriticalAsset(
            id=c.id,
            node_id=c.node_id,
            asset_type=c.asset_type,
            criticality_weight=c.criticality_weight,
        )
        for c in active_crits
    ]

    cfg = SimulationConfig()
    if req.config:
        cfg = SimulationConfig(
            overload_vc_threshold=req.config.overload_vc_threshold,
            alpha=req.config.alpha,
            beta=req.config.beta,
            max_reassignment_iterations=req.config.max_reassignment_iterations,
        )

    # Run core simulation engine
    try:
        sim_res = simulate(
            network=net,
            od_demands=demands,
            disruptions=disruptions,
            critical_assets=crit_assets,
            config=cfg,
        )
    except DisruptionError as err:
        raise HTTPException(status_code=400, detail=str(err))

    # Format Edge evaluations
    def _fmt_edges(edge_dict):
        out = {}
        for eid, e in edge_dict.items():
            out[eid] = EdgeEvaluationResponse(
                edge_id=e.edge_id,
                source=e.source,
                target=e.target,
                length_km=e.length_km,
                free_flow_speed_kmph=e.free_flow_speed_kmph,
                nominal_capacity_veh_per_hour=e.nominal_capacity_veh_per_hour,
                effective_capacity_veh_per_hour=e.effective_capacity_veh_per_hour,
                current_flow_veh_per_hour=e.current_flow_veh_per_hour,
                vc_ratio=e.vc_ratio,
                free_flow_time_minutes=e.free_flow_time_minutes,
                travel_time_minutes=e.travel_time_minutes,
                delay_minutes_per_vehicle=e.delay_minutes_per_vehicle,
                total_delay_veh_hours=e.total_delay_veh_hours,
                is_overloaded=e.is_overloaded,
                is_closed=e.is_closed,
                status=e.status,
            ).model_dump()
        return out

    # Format routes
    routes_out = [
        ODRouteImpactResponse(
            od_id=r.od_id,
            origin=r.origin,
            destination=r.destination,
            demand_veh_per_hour=r.demand_veh_per_hour,
            baseline_edge_ids=list(r.baseline_edge_ids),
            scenario_edge_ids=list(r.scenario_edge_ids) if r.scenario_edge_ids else None,
            rerouted=r.rerouted,
            unserved=r.unserved,
            baseline_distance_km=r.baseline_distance_km,
            scenario_distance_km=r.scenario_distance_km,
            extra_distance_km=r.extra_distance_km,
            baseline_travel_time_minutes=r.baseline_travel_time_minutes,
            scenario_travel_time_minutes=r.scenario_travel_time_minutes,
            travel_time_change_minutes=r.travel_time_change_minutes,
        ).model_dump()
        for r in sim_res.all_routes
    ]

    changed_routes_out = [
        r for r in routes_out
        if r["rerouted"] or r["unserved"] or (r["travel_time_change_minutes"] and abs(r["travel_time_change_minutes"]) > 0.01)
    ]

    # Format critical service impacts
    crit_out = [
        CriticalServiceImpactResponse(
            asset_id=c.asset_id,
            node_id=c.node_id,
            asset_type=c.asset_type,
            origin_zone=c.origin_zone,
            baseline_access_time_minutes=c.baseline_access_time_minutes,
            scenario_access_time_minutes=c.scenario_access_time_minutes,
            response_time_delta_minutes=c.response_time_delta_minutes,
            access_lost=c.access_lost,
        ).model_dump()
        for c in sim_res.critical_service_impacts
    ]

    # Generate Explainability causality steps
    explain_steps = []
    if sim_res.primary_disrupted_edges:
        for pe in sim_res.primary_disrupted_edges:
            mult = next((d.capacity_multiplier for d in req.disruptions if d.asset_id == pe), 0.0)
            if mult == 0.0:
                explain_steps.append(f"Primary incident caused 100% physical closure on {pe} (capacity dropped to 0 veh/h).")
            else:
                explain_steps.append(f"Hazard reduced available capacity on {pe} by {int((1-mult)*100)}% (multiplier: {mult:.2f}).")

    for cr in changed_routes_out:
        if cr["rerouted"]:
            extra_dist = cr.get("extra_distance_km")
            dist_str = f", adding +{extra_dist:.1f} km" if extra_dist is not None else ""
            explain_steps.append(f"{int(cr['demand_veh_per_hour'])} veh/h on trip {cr['origin']} → {cr['destination']} diverted onto alternate corridors{dist_str}.")
        elif cr["unserved"]:
            explain_steps.append(f"Trip {cr['origin']} → {cr['destination']} lost all connectivity (unserved).")

    if sim_res.newly_overloaded_edges:
        for ne in sim_res.newly_overloaded_edges:
            s_edge = sim_res.scenario_edges[ne]
            explain_steps.append(f"Secondary bottleneck overload triggered on {ne}: V/C surged to {s_edge.vc_ratio:.2f}, causing {s_edge.delay_minutes_per_vehicle:.1f} min/veh delay.")

    for ci in crit_out:
        if ci["response_time_delta_minutes"] and ci["response_time_delta_minutes"] > 0.1:
            explain_steps.append(f"Emergency transit time to {ci['asset_id']} lengthened by +{ci['response_time_delta_minutes']:.1f} minutes ({ci['baseline_access_time_minutes']:.1f} → {ci['scenario_access_time_minutes']:.1f} min).")

    if not explain_steps:
        explain_steps = ["Nominal baseline traffic flow with zero active disruptions."]

    # Failed assets summary
    failed_assets = [
        {
            "asset_id": d.asset_id,
            "capacity_multiplier": d.capacity_multiplier,
            "disruption_type": d.disruption_type,
            "type": d.disruption_type,
        }
        for d in req.disruptions
        if d.capacity_multiplier < 1.0
    ]

    base_delay_total = max(1e-6, sum(e.total_delay_veh_hours or 0.0 for e in sim_res.baseline_edges.values()))
    delay_change_pct = (
        (sim_res.total_delay_change_vehicle_hours / base_delay_total * 100.0)
        if sim_res.primary_disrupted_edges
        else 0.0
    )

    scenario_name = (
        f"baseline_{req.time_period}"
        if not req.disruptions
        else "sim_" + "_".join(d.asset_id for d in req.disruptions)
    )

    return {
        "status": "completed",
        "scenario_id": scenario_name,
        "baseline_edges": _fmt_edges(sim_res.baseline_edges),
        "scenario_edges": _fmt_edges(sim_res.scenario_edges),
        "primary_disrupted_edges": sim_res.primary_disrupted_edges,
        "newly_overloaded_edges": sim_res.newly_overloaded_edges,
        "persistently_overloaded_edges": sim_res.persistently_overloaded_edges,
        "changed_routes": changed_routes_out,
        "all_routes": routes_out,
        "unserved_od_ids": sim_res.unserved_od_ids,
        "total_travel_time_change_minutes": sim_res.total_travel_time_change_minutes,
        "total_delay_change_vehicle_hours": sim_res.total_delay_change_vehicle_hours,
        "critical_service_impacts": crit_out,
        "critical_assets": crit_out,
        "failed_assets": failed_assets,
        "explainability": explain_steps,
        "iterations_completed": sim_res.iterations_completed,
        "metrics": {
            "total_delay_change_veh_hours": sim_res.total_delay_change_vehicle_hours,
            "delay_change_percent": delay_change_pct,
            "newly_overloaded_count": len(sim_res.newly_overloaded_edges),
            "unserved_trips_count": len(sim_res.unserved_od_ids),
        },
    }


@app.post("/api/scenarios/compare")
def compare_scenarios(payload: Dict[str, Any] = Body(...)):
    """Compare two scenario interventions and calculate quantifiable delay reduction."""
    preset_map = {p.id: p for p in PRESETS}
    preset_map.update({k: preset_map[v] for k, v in PRESET_ALIAS_MAP.items() if v in preset_map})

    if "scenario_a_id" in payload and "scenario_b_id" in payload:
        id_a = payload["scenario_a_id"]
        id_b = payload["scenario_b_id"]
        p_a = preset_map.get(id_a)
        p_b = preset_map.get(id_b)
        if not p_a or not p_b:
            raise HTTPException(status_code=404, detail="Preset scenario not found")
        req_a = SimulateRequest(disruptions=p_a.disruptions)
        req_b = SimulateRequest(disruptions=p_b.disruptions)
    elif "scenario_a" in payload and "scenario_b" in payload:
        req_a = SimulateRequest(**payload["scenario_a"])
        req_b = SimulateRequest(**payload["scenario_b"])
    else:
        raise HTTPException(status_code=422, detail="Invalid comparison request format")

    res_a = run_simulation(req_a)
    res_b = run_simulation(req_b)

    delay_a = res_a["total_delay_change_vehicle_hours"]
    delay_b = res_b["total_delay_change_vehicle_hours"]
    net_reduction = max(0.0, delay_a - delay_b)
    pct_imp = (net_reduction / delay_a * 100.0) if delay_a > 0.0 else 0.0

    verdict = f"Mitigation strategy successfully reduced network lost time by {pct_imp:.1f}% ({net_reduction:.1f} vehicle-hours saved)."
    if pct_imp <= 0:
        verdict = "No significant delay reduction detected between scenarios."

    return {
        "scenario_a": res_a,
        "scenario_b": res_b,
        "scenario_a_metrics": {
            "total_delay_change_veh_h": delay_a,
            "newly_overloaded_count": len(res_a["newly_overloaded_edges"]),
            "unserved_od_count": len(res_a["unserved_od_ids"]),
        },
        "scenario_b_metrics": {
            "total_delay_change_veh_h": delay_b,
            "newly_overloaded_count": len(res_b["newly_overloaded_edges"]),
            "unserved_od_count": len(res_b["unserved_od_ids"]),
        },
        "net_delay_reduction_veh_hours": net_reduction,
        "percentage_improvement": pct_imp,
        "summary_verdict": verdict,
        "delta": {
            "delay_difference_veh_hours": net_reduction,
            "mitigation_verdict": verdict,
            "percentage_improvement": pct_imp,
        },
    }


# =====================================================================
# Data Pipeline & Normalization Endpoints
# =====================================================================

SUPPORTED_DATA_TYPES = {"traffic_count", "speed_observation", "od_demand"}

COLUMN_SYNONYMS = {
    "traffic_count": {
        "road_id": ["road_id", "link_id", "edge_id", "segment_id"],
        "flow": ["flow", "traffic_volume", "veh_count", "volume", "count"],
        "timestamp": ["timestamp", "time", "date", "datetime"],
    },
    "speed_observation": {
        "road_id": ["road_id", "link_id", "edge_id", "segment_id"],
        "speed_kmh": ["speed_kmh", "avg_speed", "speed", "velocity"],
        "timestamp": ["timestamp", "time", "date", "datetime"],
    },
}


import json
import re
from fastapi import Request

@app.post("/api/data/upload")
async def upload_data(request: Request):
    """Normalize and ingest external CSV or JSON traffic telemetry."""
    content_type = request.headers.get("content-type", "")
    target_data_type = None
    raw_records = []

    if "application/json" in content_type:
        body_json = await request.json()
        target_data_type = body_json.get("data_type")
        raw_records = body_json.get("records", [])
    elif "multipart/form-data" in content_type:
        body_bytes = await request.body()
        body_text = body_bytes.decode("utf-8", errors="ignore")
        
        # Extract data_type form field
        dt_match = re.search(r'name="data_type"\r?\n\r?\n([^\r\n]+)', body_text)
        if dt_match:
            target_data_type = dt_match.group(1).strip()
        
        # Extract CSV file content
        file_match = re.search(r'filename="[^"]+"\r?\nContent-Type:[^\r\n]+\r?\n\r?\n([\s\S]*?)\r?\n--', body_text)
        if file_match:
            csv_text = file_match.group(1).strip()
            csv_reader = csv.DictReader(io.StringIO(csv_text))
            raw_records = list(csv_reader)
    else:
        # Try json fallback
        try:
            body_json = await request.json()
            target_data_type = body_json.get("data_type")
            raw_records = body_json.get("records", [])
        except Exception:
            pass

    if not target_data_type or target_data_type not in SUPPORTED_DATA_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported data_type: '{target_data_type}'. Supported: {list(SUPPORTED_DATA_TYPES)}",
        )

    # Apply column synonym normalization and schema validation
    synonym_map = COLUMN_SYNONYMS.get(target_data_type, {})
    accepted_records = []
    rejected_records = []
    mapping_applied = {}

    for row in raw_records:
        normalized_row = {}
        # Attempt to map columns
        for canonical_col, synonyms in synonym_map.items():
            for syn in synonyms:
                if syn in row and row[syn] is not None:
                    normalized_row[canonical_col] = row[syn]
                    mapping_applied[syn] = canonical_col
                    break

        # Validate
        is_valid = True
        reject_reason = None

        if "road_id" not in normalized_row:
            is_valid = False
            reject_reason = "Missing required road/link identifier."
        elif target_data_type == "traffic_count":
            try:
                flow_val = float(normalized_row.get("flow", -1))
                if flow_val < 0:
                    is_valid = False
                    reject_reason = "Traffic flow value cannot be negative."
                else:
                    normalized_row["flow"] = flow_val
            except (ValueError, TypeError):
                is_valid = False
                reject_reason = "Invalid numerical flow value."
        elif target_data_type == "speed_observation":
            try:
                speed_val = float(normalized_row.get("speed_kmh", -1))
                if speed_val < 0 or speed_val > 250:
                    is_valid = False
                    reject_reason = "Speed value out of physical bounds [0, 250 km/h]."
                else:
                    normalized_row["speed_kmh"] = speed_val
            except (ValueError, TypeError):
                is_valid = False
                reject_reason = "Invalid numerical speed value."

        if is_valid:
            normalized_row["validation_status"] = "ACCEPTED"
            accepted_records.append(normalized_row)
        else:
            normalized_row["validation_status"] = f"REJECTED: {reject_reason}"
            rejected_records.append(normalized_row)

    return {
        "status": "success",
        "data_type": target_data_type,
        "total_records": len(raw_records),
        "accepted_records": len(accepted_records),
        "rejected_records": len(rejected_records),
        "column_mapping_applied": mapping_applied,
        "normalized_preview": (accepted_records + rejected_records)[:10],
    }
