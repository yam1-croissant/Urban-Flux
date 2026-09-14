"""UrbanFlux — Part B: Network Disruption, Rerouting & Cascade Demo.

Demonstrates how an acute road disruption (e.g., bridge structural failure)
triggers traffic rerouting across alternate corridors, creates secondary overloads
on residential/collector bottlenecks, and degrades emergency access to critical
infrastructure (Manipal City Hospital).

Usage:
    python -m examples.network_disruption_demo
    or
    python examples/network_disruption_demo.py
"""

import os
import sys

# Ensure repository root is on sys.path
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


def build_demo_network() -> RoadNetwork:
    nodes = [
        Node(id="Zone_A", node_type="zone"),
        Node(id="Junction_B", node_type="junction"),
        Node(id="Hospital_C", node_type="critical_asset"),
        Node(id="Junction_E", node_type="junction"),
        Node(id="Junction_F", node_type="junction"),
        Node(id="Zone_D", node_type="zone"),
    ]

    edges = [
        # Northern Primary Corridor: Fast 4-lane arterial with bridge
        Edge(
            id="Bridge_A_B",
            source="Zone_A",
            target="Junction_B",
            length_km=3.5,
            free_flow_speed_kmph=60.0,
            nominal_capacity_veh_per_hour=2400.0,
            road_class="primary_arterial",
            baseline_flow_veh_per_hour=400.0,
        ),
        Edge(
            id="Arterial_B_C",
            source="Junction_B",
            target="Hospital_C",
            length_km=2.5,
            free_flow_speed_kmph=50.0,
            nominal_capacity_veh_per_hour=2200.0,
            road_class="arterial",
            baseline_flow_veh_per_hour=200.0,
        ),
        Edge(
            id="Arterial_C_D",
            source="Hospital_C",
            target="Zone_D",
            length_km=3.0,
            free_flow_speed_kmph=50.0,
            nominal_capacity_veh_per_hour=2000.0,
            road_class="arterial",
            baseline_flow_veh_per_hour=100.0,
        ),

        # Southern Alternate Corridor: 2-lane collector route with narrow bottleneck
        Edge(
            id="Collector_A_E",
            source="Zone_A",
            target="Junction_E",
            length_km=4.5,
            free_flow_speed_kmph=45.0,
            nominal_capacity_veh_per_hour=1500.0,
            road_class="collector",
            baseline_flow_veh_per_hour=200.0,
        ),
        Edge(
            id="Bottleneck_E_F",
            source="Junction_E",
            target="Junction_F",
            length_km=5.0,
            free_flow_speed_kmph=40.0,
            nominal_capacity_veh_per_hour=1400.0,
            road_class="secondary",
            baseline_flow_veh_per_hour=500.0,  # Local background traffic
        ),
        Edge(
            id="Connector_F_C",
            source="Junction_F",
            target="Hospital_C",
            length_km=2.0,
            free_flow_speed_kmph=45.0,
            nominal_capacity_veh_per_hour=1600.0,
            road_class="collector",
            baseline_flow_veh_per_hour=150.0,
        ),
        Edge(
            id="Connector_F_D",
            source="Junction_F",
            target="Zone_D",
            length_km=2.5,
            free_flow_speed_kmph=45.0,
            nominal_capacity_veh_per_hour=1600.0,
            road_class="collector",
            baseline_flow_veh_per_hour=100.0,
        ),
    ]

    return RoadNetwork(nodes=nodes, edges=edges)


def run_demo():
    print("=" * 88)
    print("   URBANFLUX — PART B: NETWORK DISRUPTION & CASCADE SIMULATION DEMO")
    print("=" * 88)
    print()

    network = build_demo_network()

    # Define Peak-Hour OD Demand
    od_demands = [
        # Major commuter & patient demand from Zone A to Central Hospital
        ODDemand(
            id="OD_ZoneA_HospitalC",
            origin="Zone_A",
            destination="Hospital_C",
            demand_veh_per_hour=1200.0,
            time_period="morning_peak",
        ),
        # Inter-zone transit traffic from Zone A to Zone D
        ODDemand(
            id="OD_ZoneA_ZoneD",
            origin="Zone_A",
            destination="Zone_D",
            demand_veh_per_hour=400.0,
            time_period="morning_peak",
        ),
    ]

    # Critical facility specification
    hospital = CriticalAsset(
        id="hosp_manipal",
        node_id="Hospital_C",
        asset_type="hospital",
        criticality_weight=1.5,
    )

    # Disruption: Total closure of Bridge_A_B (capacity_multiplier = 0.0)
    disruptions = [
        Disruption(
            asset_id="Bridge_A_B",
            disruption_type="closure",
            capacity_multiplier=0.0,
        )
    ]

    config = SimulationConfig(
        overload_vc_threshold=1.0,
        alpha=0.15,
        beta=4.0,
        max_reassignment_iterations=1,
    )

    print("--- SIMULATION SCENARIO SPECIFICATION ---")
    print("Network Topology       : 6 Nodes, 7 Directed Road Links")
    print("Baseline Flow Demands  : 2 OD pairs totalling 1,600 veh/h from Zone A")
    print("Critical Asset Tested  : Manipal City Hospital at node 'Hospital_C'")
    print("Acute Disruption Event : Complete emergency closure of 'Bridge_A_B' (Capacity -> 0 veh/h)")
    print("Overload Threshold (V/C): 1.00 (Standard capacity saturation)")
    print()

    # Execute simulation
    result = simulate(
        network=network,
        od_demands=od_demands,
        disruptions=disruptions,
        critical_assets=[hospital],
        config=config,
    )

    # -------------------------------------------------------------
    # 1. Edge Impact Comparison Table
    # -------------------------------------------------------------
    print("-" * 88)
    print(f"{'Edge ID':<16} | {'Nom. Cap':<9} | {'Baseline Flow (V/C)':<21} | {'Scenario Flow (V/C)':<21} | {'Status'}")
    print("-" * 88)

    for eid, b_eval in result.baseline_edges.items():
        s_eval = result.scenario_edges[eid]
        b_vc_str = f"{b_eval.current_flow_veh_per_hour:>5.0f} ({b_eval.vc_ratio:.2f})" if b_eval.vc_ratio is not None else "CLOSED"
        if s_eval.is_closed:
            s_vc_str = "    0 (CLOSED)"
            status_tag = "[PRIMARY CLOSURE]"
        else:
            s_vc_str = f"{s_eval.current_flow_veh_per_hour:>5.0f} ({s_eval.vc_ratio:.2f})"
            if eid in result.newly_overloaded_edges:
                status_tag = "[CASCADE OVERLOAD!]"
            elif eid in result.persistently_overloaded_edges:
                status_tag = "[PERSISTENT OVERLOAD]"
            else:
                status_tag = "Normal"

        print(
            f"{eid:<16} | "
            f"{b_eval.nominal_capacity_veh_per_hour:>8.0f} | "
            f"{b_vc_str:<21} | "
            f"{s_vc_str:<21} | "
            f"{status_tag}"
        )
    print("-" * 88)
    print()

    # -------------------------------------------------------------
    # 2. Causal Cascade Summary
    # -------------------------------------------------------------
    print("=" * 88)
    print("   CAUSAL CHAIN & CASCADING IMPACT BREAKDOWN")
    print("=" * 88)

    print()
    print("1. PRIMARY DISRUPTION:")
    for eid in result.primary_disrupted_edges:
        print(f"   * Road link '{eid}' suffered complete structural/hazard closure (Capacity = 0 veh/h).")

    print()
    print("2. DEMAND REROUTING:")
    for r in result.changed_routes:
        base_path_str = " -> ".join(r.baseline_edge_ids)
        scen_path_str = " -> ".join(r.scenario_edge_ids) if r.scenario_edge_ids else "UNSERVED"
        pct_increase = (r.travel_time_change_minutes / r.baseline_travel_time_minutes) * 100.0
        print(f"   * OD Pair '{r.od_id}' ({r.origin} -> {r.destination}, Flow: {r.demand_veh_per_hour:.0f} veh/h):")
        print(f"       - Baseline Route : {base_path_str} ({r.baseline_distance_km:.1f} km, {r.baseline_travel_time_minutes:.1f} min)")
        print(f"       - Rerouted Route : {scen_path_str} ({r.scenario_distance_km:.1f} km, {r.scenario_travel_time_minutes:.1f} min)")
        print(f"       - Route Penalty  : +{r.extra_distance_km:.1f} km extra distance, +{r.travel_time_change_minutes:.1f} min delay (+{pct_increase:.1f}%)")

    print()
    print("3. SECONDARY CASCADING OVERLOADS:")
    if result.newly_overloaded_edges:
        for eid in result.newly_overloaded_edges:
            b_eval = result.baseline_edges[eid]
            s_eval = result.scenario_edges[eid]
            print(f"   * CRITICAL SPILLOVER: Link '{eid}' exceeded capacity!")
            print(f"       Flow surged from {b_eval.current_flow_veh_per_hour:.0f} -> {s_eval.current_flow_veh_per_hour:.0f} veh/h (V/C: {b_eval.vc_ratio:.2f} -> {s_eval.vc_ratio:.2f}).")
            print(f"       Travel time jumped from {b_eval.travel_time_minutes:.1f} -> {s_eval.travel_time_minutes:.1f} mins (Delay: {s_eval.delay_minutes_per_vehicle:.1f} min/veh).")
    else:
        print("   * No newly overloaded links detected.")

    print()
    print("4. CRITICAL SERVICE ACCESS DEGRADATION:")
    for c in result.critical_service_impacts:
        print(f"   * Emergency Facility : {c.asset_id} ({c.asset_type.upper()}) at node '{c.node_id}'")
        print(f"       - Origin Sector  : {c.origin_zone}")
        print(f"       - Baseline Access: {c.baseline_access_time_minutes:.1f} minutes")
        print(f"       - Scenario Access: {c.scenario_access_time_minutes:.1f} minutes")
        print(f"       - Response Delta : +{c.response_time_delta_minutes:.1f} minutes delay (Emergency accessibility degraded)")

    print()
    print("5. AGGREGATE NETWORK TOTALS:")
    print(f"   * Net Increase in Total User Travel Time : +{result.total_travel_time_change_minutes:.1f} minutes across OD trips")
    print(f"   * Net Increase in Aggregate System Delay : +{result.total_delay_change_vehicle_hours:.1f} vehicle-hours of lost time")
    print(f"   * Unserved Vehicle Demand                : {len(result.unserved_od_ids)} OD pairs")
    print("=" * 88)


if __name__ == "__main__":
    run_demo()
