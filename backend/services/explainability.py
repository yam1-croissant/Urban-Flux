"""Explainability engine for deriving human-readable causal narratives from simulation results."""

from __future__ import annotations

from typing import Dict, List
from src.simulation.models import Disruption, Edge, SimulationResult


def generate_explainability_narrative(
    result: SimulationResult,
    edges_meta: Dict[str, Edge],
    disruptions: List[Disruption],
) -> List[str]:
    """Generate deterministic, fact-grounded causal statements explaining simulation outcomes.

    Follows the causal chain:
        Disruption -> Capacity Lost -> Traffic Rerouting -> Secondary Bottlenecks -> Service Impact
    """
    narrative: List[str] = []

    # 1. Primary Disruptions
    for d in disruptions:
        edge = edges_meta.get(d.asset_id)
        edge_name = edge.id if edge else d.asset_id
        if d.capacity_multiplier <= 0.0:
            nom_cap = edge.nominal_capacity_veh_per_hour if edge else 0.0
            narrative.append(
                f"Complete closure on '{edge_name}' removed {nom_cap:,.0f} veh/hr of operational corridor capacity."
            )
        else:
            pct_lost = (1.0 - d.capacity_multiplier) * 100.0
            nom_cap = edge.nominal_capacity_veh_per_hour if edge else 0.0
            cap_lost = nom_cap * (1.0 - d.capacity_multiplier)
            narrative.append(
                f"Partial disruption on '{edge_name}' cut capacity by {pct_lost:.0f}% (lost {cap_lost:,.0f} veh/hr)."
            )

    # 2. Rerouting and flow diversion
    total_diverted_flow = 0.0
    for r in result.changed_routes:
        if r.rerouted and not r.unserved:
            total_diverted_flow += r.demand_veh_per_hour
            orig_dest = f"{r.origin} → {r.destination}"
            extra_dist = f"{r.extra_distance_km:+.1f} km" if r.extra_distance_km is not None else ""
            narrative.append(
                f"Commuters on {orig_dest} ({r.demand_veh_per_hour:,.0f} veh/hr) diverted away from disrupted corridors ({extra_dist} detour)."
            )

    # 3. Secondary Cascading Overloads
    if result.newly_overloaded_edges:
        for eid in result.newly_overloaded_edges:
            base_eval = result.baseline_edges[eid]
            scen_eval = result.scenario_edges[eid]
            edge_name = edges_meta.get(eid).id if eid in edges_meta else eid
            base_vc = base_eval.vc_ratio if base_eval.vc_ratio is not None else 0.0
            scen_vc = scen_eval.vc_ratio if scen_eval.vc_ratio is not None else 0.0
            narrative.append(
                f"Secondary cascade overload on '{edge_name}': volume/capacity jumped from {base_vc:.2f} to {scen_vc:.2f} due to diverted flow."
            )
    else:
        narrative.append("No secondary corridor breached capacity threshold (V/C remained <= 1.0).")

    # 4. Critical Service & Emergency Access Impacts
    for impact in result.critical_service_impacts:
        if impact.access_lost:
            narrative.append(
                f"CRITICAL: Complete vehicular access lost to {impact.asset_type.upper()} '{impact.asset_id}' from zone '{impact.origin_zone}'."
            )
        elif impact.response_time_delta_minutes and impact.response_time_delta_minutes > 0.05:
            delta = impact.response_time_delta_minutes
            base_t = impact.baseline_access_time_minutes or 0.0
            scen_t = impact.scenario_access_time_minutes or 0.0
            pct_inc = ((scen_t - base_t) / base_t * 100.0) if base_t > 0 else 0.0
            narrative.append(
                f"Emergency access to {impact.asset_type.upper()} '{impact.asset_id}' degraded by +{delta:.1f} minutes (+{pct_inc:.0f}%, from {base_t:.1f} to {scen_t:.1f} min)."
            )

    # 5. Aggregate System Impact
    tot_delay_change = result.total_delay_change_vehicle_hours
    if tot_delay_change > 0:
        narrative.append(
            f"Overall network congestion penalty: +{tot_delay_change:,.1f} vehicle-hours of aggregate traffic delay."
        )

    return narrative

