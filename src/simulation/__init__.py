"""UrbanResilience — Traffic Simulation Package.

Includes:
- Traffic Mathematics (Part A): free_flow_time, vc_ratio, bpr_travel_time, delay, reduced_capacity
- Network, Disruption & Cascade Simulation (Part B): RoadNetwork, ODDemand, Disruption, CriticalAsset, simulate
"""

from src.simulation.traffic_math import (
    free_flow_time,
    vc_ratio,
    bpr_travel_time,
    delay,
    delay_per_vehicle,
    total_delay,
    reduced_capacity,
    evaluate_link_disruption,
    TrafficMathError,
    InvalidInputError,
    RoadClosedError,
    LinkImpactResult,
)

from src.simulation.models import (
    Node,
    Edge,
    EdgeEvaluation,
    ODDemand,
    Disruption,
    CriticalAsset,
    CriticalServiceImpact,
    ODRouteImpact,
    SimulationConfig,
    SimulationResult,
    NetworkValidationError,
    RouteNotFoundError,
    DisruptionError,
)

from src.simulation.graph import RoadNetwork
from src.simulation.simulation import simulate, evaluate_edge_condition, assign_demand_to_routes

__all__ = [
    # Traffic Math
    "free_flow_time",
    "vc_ratio",
    "bpr_travel_time",
    "delay",
    "delay_per_vehicle",
    "total_delay",
    "reduced_capacity",
    "evaluate_link_disruption",
    "TrafficMathError",
    "InvalidInputError",
    "RoadClosedError",
    "LinkImpactResult",
    # Models
    "Node",
    "Edge",
    "EdgeEvaluation",
    "ODDemand",
    "Disruption",
    "CriticalAsset",
    "CriticalServiceImpact",
    "ODRouteImpact",
    "SimulationConfig",
    "SimulationResult",
    "NetworkValidationError",
    "RouteNotFoundError",
    "DisruptionError",
    # Graph & Simulation
    "RoadNetwork",
    "simulate",
    "evaluate_edge_condition",
    "assign_demand_to_routes",
]
