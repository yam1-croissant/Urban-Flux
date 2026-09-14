"""UrbanResilience — FastAPI Simulation Backend & Digital Twin Server."""

from __future__ import annotations

import os
import sys
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Ensure repo root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.simulation.graph import RoadNetwork
from src.simulation.models import (
    CriticalAsset,
    Disruption,
    Edge,
    Node,
    ODDemand,
    SimulationConfig,
)
from src.simulation.simulation import simulate
from backend.schemas import (
    CriticalAssetSchema,
    CriticalServiceImpactResponse,
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

app = FastAPI(
    title="UrbanResilience Digital Twin API",
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
        name="Agara Collector Bypass",
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
        name="Koramangala-Whitefield Connector",
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
        id="bridge_closure",
        name="Bridge Structural Closure",
        description="Acute 100% closure of Silk Board Bridge due to structural inspection.",
        icon="alert-triangle",
        disruptions=[
            {"asset_id": "Bridge_A_B", "disruption_type": "closure", "capacity_multiplier": 0.0}
        ],
        recommended_mitigation_id="mitigation_reroute",
    ),
    ScenarioPreset(
        id="monsoon_flooding",
        name="Monsoon Flash Flooding",
        description="50% capacity loss on primary corridors due to heavy waterlogging.",
        icon="cloud-rain",
        disruptions=[
            {"asset_id": "Bridge_A_B", "disruption_type": "weather", "capacity_multiplier": 0.5},
            {"asset_id": "Bottleneck_E_F", "disruption_type": "weather", "capacity_multiplier": 0.5},
        ],
    ),
    ScenarioPreset(
        id="metro_construction",
        name="Metro Line 3 Construction",
        description="Single lane blockage on Inner Ring Road approach reducing throughput by 35%.",
        icon="cone",
        disruptions=[
            {"asset_id": "Arterial_B_C", "disruption_type": "construction", "capacity_multiplier": 0.65}
        ],
    ),
    ScenarioPreset(
        id="mitigation_reroute",
        name="Active Police Rerouting & Relief Lane",
        description="Deployment of traffic wardens and dedicated signal green-waves on North Relief corridor.",
        icon="shield-check",
        disruptions=[],
    ),
]


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
    return {"status": "ok", "service": "UrbanResilience Digital Twin API", "version": "1.0.0"}


@app.get("/api/network")
def get_network():
    """Return the complete benchmark road network with nodes, edges, and critical assets."""
    return {
        "network_id": "bengaluru_core_demo",
        "name": "Bengaluru Central Arterial Corridor",
        "nodes": [n.model_dump() for n in BENCHMARK_NODES],
        "edges": [e.model_dump() for e in BENCHMARK_EDGES],
        "critical_assets": [c.model_dump() for c in BENCHMARK_CRITICAL_ASSETS],
    }


@app.get("/api/scenarios/presets", response_model=List[ScenarioPreset])
def get_presets():
    """Return pre-packaged realistic disruption and mitigation scenarios."""
    return PRESETS


@app.post("/api/simulate", response_model=SimulateResponse)
def run_simulation(req: SimulateRequest):
    """Execute deterministic network disruption simulation and return complete cascading metrics."""
    net = _build_sim_network()

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
    demands = DEFAULT_OD_DEMANDS
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

    # Critical assets
    crit_assets = [
        CriticalAsset(
            id=c.id,
            node_id=c.node_id,
            asset_type=c.asset_type,
            criticality_weight=c.criticality_weight,
        )
        for c in BENCHMARK_CRITICAL_ASSETS
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
    sim_res = simulate(
        network=net,
        od_demands=demands,
        disruptions=disruptions,
        critical_assets=crit_assets,
        config=cfg,
    )

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
            )
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
        )
        for r in sim_res.all_routes
    ]

    changed_routes_out = [r for r in routes_out if r.rerouted or r.unserved or (r.travel_time_change_minutes and abs(r.travel_time_change_minutes) > 0.01)]

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
        )
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
                explain_steps.append(f"Hazard reduced available capacity on {pe} by {int((1-mult)*100)}%.")

    for cr in changed_routes_out:
        if cr.rerouted:
            explain_steps.append(f"{int(cr.demand_veh_per_hour)} veh/h on trip {cr.origin} → {cr.destination} diverted onto alternate corridors, adding +{cr.extra_distance_km:.1f} km.")
        elif cr.unserved:
            explain_steps.append(f"Trip {cr.origin} → {cr.destination} lost all connectivity (unserved).")

    if sim_res.newly_overloaded_edges:
        for ne in sim_res.newly_overloaded_edges:
            s_edge = sim_res.scenario_edges[ne]
            explain_steps.append(f"Secondary bottleneck overload triggered on {ne}: V/C surged to {s_edge.vc_ratio:.2f}, causing {s_edge.delay_minutes_per_vehicle:.1f} min/veh delay.")

    for ci in crit_out:
        if ci.response_time_delta_minutes and ci.response_time_delta_minutes > 0.1:
            explain_steps.append(f"Emergency transit time to {ci.asset_id} lengthened by +{ci.response_time_delta_minutes:.1f} minutes ({ci.baseline_access_time_minutes:.1f} → {ci.scenario_access_time_minutes:.1f} min).")

    return SimulateResponse(
        scenario_id="sim_" + "_".join(d.asset_id for d in req.disruptions) if req.disruptions else "baseline",
        baseline_edges=_fmt_edges(sim_res.baseline_edges),
        scenario_edges=_fmt_edges(sim_res.scenario_edges),
        primary_disrupted_edges=sim_res.primary_disrupted_edges,
        newly_overloaded_edges=sim_res.newly_overloaded_edges,
        persistently_overloaded_edges=sim_res.persistently_overloaded_edges,
        changed_routes=changed_routes_out,
        all_routes=routes_out,
        unserved_od_ids=sim_res.unserved_od_ids,
        total_travel_time_change_minutes=sim_res.total_travel_time_change_minutes,
        total_delay_change_vehicle_hours=sim_res.total_delay_change_vehicle_hours,
        critical_service_impacts=crit_out,
        explainability=explain_steps,
        iterations_completed=sim_res.iterations_completed,
    )


@app.post("/api/scenarios/compare", response_model=ScenarioCompareResponse)
def compare_scenarios(req: ScenarioCompareRequest):
    """Compare two scenario interventions and calculate quantifiable delay reduction."""
    res_a = run_simulation(req.scenario_a)
    res_b = run_simulation(req.scenario_b)

    delay_a = res_a.total_delay_change_vehicle_hours
    delay_b = res_b.total_delay_change_vehicle_hours
    net_reduction = max(0.0, delay_a - delay_b)
    pct_imp = (net_reduction / delay_a * 100.0) if delay_a > 0.0 else 0.0

    verdict = f"Mitigation strategy successfully reduced network lost time by {pct_imp:.1f}% ({net_reduction:.1f} vehicle-hours saved)."
    if pct_imp <= 0:
        verdict = "No significant delay reduction detected between scenarios."

    return ScenarioCompareResponse(
        scenario_a_metrics={
            "total_delay_change_veh_h": delay_a,
            "newly_overloaded_count": len(res_a.newly_overloaded_edges),
            "unserved_od_count": len(res_a.unserved_od_ids),
        },
        scenario_b_metrics={
            "total_delay_change_veh_h": delay_b,
            "newly_overloaded_count": len(res_b.newly_overloaded_edges),
            "unserved_od_count": len(res_b.unserved_od_ids),
        },
        net_delay_reduction_veh_hours=net_reduction,
        percentage_improvement=pct_imp,
        summary_verdict=verdict,
    )
