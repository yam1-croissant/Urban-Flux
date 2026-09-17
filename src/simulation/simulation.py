"""UrbanFlux — Part B: Network Disruption & Cascade Simulation Orchestrator.

Orchestrates baseline assignment, disruption application, rerouting, Part A
traffic math re-evaluation, secondary overload classification, and critical service
accessibility assessment.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Set, Tuple

from src.simulation.graph import RoadNetwork
from src.simulation.models import (
    CriticalAsset,
    CriticalServiceImpact,
    Disruption,
    DisruptionError,
    Edge,
    EdgeEvaluation,
    ODDemand,
    ODRouteImpact,
    RouteNotFoundError,
    SimulationConfig,
    SimulationResult,
)
from src.simulation.traffic_math import (
    bpr_travel_time,
    delay_per_vehicle,
    free_flow_time,
    reduced_capacity,
    total_delay,
    vc_ratio,
)


def evaluate_edge_condition(
    edge: Edge,
    flow: float,
    capacity_multiplier: float = 1.0,
    config: Optional[SimulationConfig] = None,
) -> EdgeEvaluation:
    """Compute derived operational metrics for an edge using Part A traffic math."""
    cfg = config or SimulationConfig()

    t0 = free_flow_time(
        length_km=edge.length_km,
        free_flow_speed_kmph=edge.free_flow_speed_kmph,
    )
    reduction_fraction = 1.0 - capacity_multiplier
    c_eff = reduced_capacity(
        capacity=edge.nominal_capacity_veh_per_hour,
        reduction_fraction=reduction_fraction,
    )

    if capacity_multiplier <= 0.0 or c_eff <= 0.0:
        return EdgeEvaluation(
            edge_id=edge.id,
            source=edge.source,
            target=edge.target,
            length_km=edge.length_km,
            free_flow_speed_kmph=edge.free_flow_speed_kmph,
            nominal_capacity_veh_per_hour=edge.nominal_capacity_veh_per_hour,
            effective_capacity_veh_per_hour=0.0,
            current_flow_veh_per_hour=flow,
            vc_ratio=None,
            free_flow_time_hours=t0,
            travel_time_hours=None,
            delay_hours_per_vehicle=None,
            total_delay_veh_hours=None,
            is_overloaded=False,
            is_closed=True,
            status="closed",
        )

    vc = vc_ratio(volume=flow, capacity=c_eff)
    t = bpr_travel_time(
        free_flow_time_hours=t0,
        volume=flow,
        capacity=c_eff,
        alpha=cfg.alpha,
        beta=cfg.beta,
    )
    d_veh = delay_per_vehicle(travel_time_hours=t, free_flow_time_hours=t0)
    d_tot = total_delay(travel_time_hours=t, free_flow_time_hours=t0, volume=flow)
    is_overloaded = vc > cfg.overload_vc_threshold
    status = "restricted" if capacity_multiplier < 1.0 else "open"

    return EdgeEvaluation(
        edge_id=edge.id,
        source=edge.source,
        target=edge.target,
        length_km=edge.length_km,
        free_flow_speed_kmph=edge.free_flow_speed_kmph,
        nominal_capacity_veh_per_hour=edge.nominal_capacity_veh_per_hour,
        effective_capacity_veh_per_hour=c_eff,
        current_flow_veh_per_hour=flow,
        vc_ratio=vc,
        free_flow_time_hours=t0,
        travel_time_hours=t,
        delay_hours_per_vehicle=d_veh,
        total_delay_veh_hours=d_tot,
        is_overloaded=is_overloaded,
        is_closed=False,
        status=status,
    )


def assign_demand_to_routes(
    network: RoadNetwork,
    od_demands: Iterable[ODDemand],
    edge_weights: Optional[Dict[str, float]] = None,
    excluded_edge_ids: Optional[Set[str]] = None,
) -> Tuple[Dict[str, List[str]], Dict[str, float], List[str]]:
    """Assign OD demand across shortest paths.

    Returns:
        Tuple of (od_routes_dict, edge_flows_dict, unserved_od_ids).
    """
    od_routes: Dict[str, List[str]] = {}
    unserved: List[str] = []
    edge_flows: Dict[str, float] = {
        eid: edge.baseline_flow_veh_per_hour for eid, edge in network.edges.items()
    }

    for od in od_demands:
        try:
            path_edges, _ = network.find_shortest_path(
                origin=od.origin,
                destination=od.destination,
                edge_weights=edge_weights,
                excluded_edge_ids=excluded_edge_ids,
            )
            od_routes[od.id] = path_edges
            for eid in path_edges:
                edge_flows[eid] += od.demand_veh_per_hour
        except RouteNotFoundError:
            od_routes[od.id] = []
            unserved.append(od.id)

    return od_routes, edge_flows, unserved


def simulate(
    network: RoadNetwork,
    od_demands: Iterable[ODDemand],
    disruptions: Optional[Iterable[Disruption]] = None,
    critical_assets: Optional[Iterable[CriticalAsset]] = None,
    config: Optional[SimulationConfig] = None,
) -> SimulationResult:
    """Run complete network disruption and cascading overload simulation.

    Args:
        network: RoadNetwork graph (baseline).
        od_demands: Collection of ODDemand records.
        disruptions: Optional list of Disruption records to apply.
        critical_assets: Optional list of CriticalAsset facilities to evaluate.
        config: Optional SimulationConfig parameters.

    Returns:
        SimulationResult containing baseline, scenario, routes, cascading overloads,
        and critical service access metrics.
    """
    cfg = config or SimulationConfig()
    demands_list = list(od_demands)
    disruptions_list = list(disruptions or [])
    critical_list = list(critical_assets or [])

    # Validate disruptions
    disruption_map: Dict[str, Disruption] = {}
    for d in disruptions_list:
        if d.asset_id not in network.edges:
            raise DisruptionError(
                f"Disruption specifies unknown edge ID: '{d.asset_id}'"
            )
        if not (0.0 <= d.capacity_multiplier <= 1.0):
            raise DisruptionError(
                f"Disruption capacity_multiplier must be in [0.0, 1.0], got {d.capacity_multiplier}"
            )
        disruption_map[d.asset_id] = d

    # -------------------------------------------------------------
    # 1. Baseline Assignment & Evaluation
    # -------------------------------------------------------------
    base_od_routes, base_flows, base_unserved = assign_demand_to_routes(
        network=network,
        od_demands=demands_list,
        edge_weights=None,  # Free-flow time baseline
        excluded_edge_ids=None,
    )

    baseline_edges: Dict[str, EdgeEvaluation] = {
        eid: evaluate_edge_condition(
            edge=edge,
            flow=base_flows[eid],
            capacity_multiplier=1.0,
            config=cfg,
        )
        for eid, edge in network.edges.items()
    }

    # -------------------------------------------------------------
    # 2. Scenario Disruption & Rerouting
    # -------------------------------------------------------------
    excluded_edges: Set[str] = {
        d.asset_id for d in disruptions_list if d.capacity_multiplier <= 0.0
    }

    # Initial scenario edge weights: use baseline congested travel times for open links,
    # or free flow time if flow was 0
    scen_weights: Dict[str, float] = {}
    for eid, edge in network.edges.items():
        mult = disruption_map[eid].capacity_multiplier if eid in disruption_map else 1.0
        # If reduced capacity, initial weight uses adjusted capacity
        eval_init = evaluate_edge_condition(
            edge=edge,
            flow=base_flows[eid],
            capacity_multiplier=mult,
            config=cfg,
        )
        scen_weights[eid] = eval_init.travel_time_hours if eval_init.travel_time_hours is not None else float('inf')

    # Iterative assignment loop
    scen_od_routes: Dict[str, List[str]] = {}
    scen_flows: Dict[str, float] = {}
    scen_unserved: List[str] = []
    scenario_edges: Dict[str, EdgeEvaluation] = {}

    iterations_done = 0
    for it in range(max(1, cfg.max_reassignment_iterations)):
        iterations_done += 1
        scen_od_routes, scen_flows, scen_unserved = assign_demand_to_routes(
            network=network,
            od_demands=demands_list,
            edge_weights=scen_weights,
            excluded_edge_ids=excluded_edges,
        )

        scenario_edges = {
            eid: evaluate_edge_condition(
                edge=edge,
                flow=scen_flows[eid],
                capacity_multiplier=disruption_map[eid].capacity_multiplier if eid in disruption_map else 1.0,
                config=cfg,
            )
            for eid, edge in network.edges.items()
        }

        # Update weights for next iteration
        for eid, eval_state in scenario_edges.items():
            if eval_state.travel_time_hours is not None:
                scen_weights[eid] = eval_state.travel_time_hours

    # -------------------------------------------------------------
    # 3. Route Comparisons (ODRouteImpact)
    # -------------------------------------------------------------
    all_routes: List[ODRouteImpact] = []
    changed_routes: List[ODRouteImpact] = []
    total_travel_time_change_min = 0.0

    for od in demands_list:
        base_path = tuple(base_od_routes.get(od.id, []))
        scen_path_list = scen_od_routes.get(od.id, [])
        is_unserved = od.id in scen_unserved

        base_dist = sum(network.edges[eid].length_km for eid in base_path)
        base_tt_min = sum(
            (baseline_edges[eid].travel_time_minutes or baseline_edges[eid].free_flow_time_minutes)
            for eid in base_path
        )

        if is_unserved:
            impact = ODRouteImpact(
                od_id=od.id,
                origin=od.origin,
                destination=od.destination,
                demand_veh_per_hour=od.demand_veh_per_hour,
                baseline_edge_ids=base_path,
                scenario_edge_ids=None,
                rerouted=True,
                unserved=True,
                baseline_distance_km=base_dist,
                scenario_distance_km=None,
                extra_distance_km=None,
                baseline_travel_time_minutes=base_tt_min,
                scenario_travel_time_minutes=None,
                travel_time_change_minutes=None,
            )
        else:
            scen_path = tuple(scen_path_list)
            scen_dist = sum(network.edges[eid].length_km for eid in scen_path)
            scen_tt_min = sum(
                scenario_edges[eid].travel_time_minutes or scenario_edges[eid].free_flow_time_minutes
                for eid in scen_path
            )
            tt_change = scen_tt_min - base_tt_min
            rerouted = (scen_path != base_path)

            impact = ODRouteImpact(
                od_id=od.id,
                origin=od.origin,
                destination=od.destination,
                demand_veh_per_hour=od.demand_veh_per_hour,
                baseline_edge_ids=base_path,
                scenario_edge_ids=scen_path,
                rerouted=rerouted,
                unserved=False,
                baseline_distance_km=base_dist,
                scenario_distance_km=scen_dist,
                extra_distance_km=scen_dist - base_dist,
                baseline_travel_time_minutes=base_tt_min,
                scenario_travel_time_minutes=scen_tt_min,
                travel_time_change_minutes=tt_change,
            )
            total_travel_time_change_min += tt_change

        all_routes.append(impact)
        if impact.rerouted or impact.unserved or (
            impact.travel_time_change_minutes is not None and abs(impact.travel_time_change_minutes) > 1e-4
        ):
            changed_routes.append(impact)

    # -------------------------------------------------------------
    # 4. Cascade Overload Classification
    # -------------------------------------------------------------
    primary_disrupted = [
        d.asset_id for d in disruptions_list if d.capacity_multiplier < 1.0
    ]

    newly_overloaded: List[str] = []
    persistently_overloaded: List[str] = []

    for eid, scen_eval in scenario_edges.items():
        if scen_eval.is_closed:
            continue
        base_eval = baseline_edges[eid]
        if scen_eval.is_overloaded:
            if not base_eval.is_overloaded:
                newly_overloaded.append(eid)
            else:
                persistently_overloaded.append(eid)

    # Total network delay change in vehicle-hours
    base_tot_delay = sum(
        e.total_delay_veh_hours or 0.0 for e in baseline_edges.values()
    )
    scen_tot_delay = sum(
        e.total_delay_veh_hours or 0.0 for e in scenario_edges.values()
    )
    tot_delay_change_veh_h = scen_tot_delay - base_tot_delay

    # -------------------------------------------------------------
    # 5. Critical Service Access Assessment
    # -------------------------------------------------------------
    crit_impacts: List[CriticalServiceImpact] = []
    routes_by_destination = {r.destination: r for r in all_routes}
    routes_by_origin = {r.origin: r for r in all_routes}

    for asset in critical_list:
        # Find OD flows headed to this critical asset
        matched_routes = [r for r in all_routes if r.destination == asset.node_id or r.origin == asset.node_id]
        for r in matched_routes:
            other_zone = r.origin if r.destination == asset.node_id else r.destination
            crit_impacts.append(
                CriticalServiceImpact(
                    asset_id=asset.id,
                    node_id=asset.node_id,
                    asset_type=asset.asset_type,
                    origin_zone=other_zone,
                    baseline_access_time_minutes=r.baseline_travel_time_minutes,
                    scenario_access_time_minutes=r.scenario_travel_time_minutes,
                    response_time_delta_minutes=r.travel_time_change_minutes,
                    access_lost=r.unserved,
                )
            )

    return SimulationResult(
        baseline_edges=baseline_edges,
        scenario_edges=scenario_edges,
        primary_disrupted_edges=primary_disrupted,
        newly_overloaded_edges=newly_overloaded,
        persistently_overloaded_edges=persistently_overloaded,
        changed_routes=changed_routes,
        all_routes=all_routes,
        unserved_od_ids=scen_unserved,
        total_travel_time_change_minutes=total_travel_time_change_min,
        total_delay_change_vehicle_hours=tot_delay_change_veh_h,
        critical_service_impacts=crit_impacts,
        iterations_completed=iterations_done,
        config=cfg,
    )
