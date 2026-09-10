"""UrbanResilience — Part B: Network, Disruption, Rerouting & Cascade Data Models.

Defines typed, immutable dataclasses for road network nodes, edges, OD demand,
disruptions, evaluated link states, routing results, and critical asset metrics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# =====================================================================
# Domain Exceptions
# =====================================================================

class NetworkValidationError(ValueError):
    """Raised when graph topology, node definitions, or edge parameters fail validation."""
    pass


class RouteNotFoundError(Exception):
    """Raised when no feasible path exists between an origin and destination."""
    pass


class DisruptionError(ValueError):
    """Raised when a disruption specifies an unknown asset or invalid multiplier."""
    pass


# =====================================================================
# Graph Primitives: Nodes & Edges
# =====================================================================

@dataclass(frozen=True)
class Node:
    """Represents a point of interest, intersection, junction, or zone in the road network."""

    id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    node_type: str = "intersection"  # 'intersection', 'junction', 'zone', 'critical_asset'


@dataclass(frozen=True)
class Edge:
    """Represents a directed road link connecting a source node to a target node."""

    id: str
    source: str
    target: str
    length_km: float
    free_flow_speed_kmph: float
    nominal_capacity_veh_per_hour: float
    lanes: Optional[int] = None
    road_class: str = "arterial"  # 'primary', 'secondary', 'arterial', 'collector', 'local'
    baseline_flow_veh_per_hour: float = 0.0
    status: str = "open"  # 'open', 'restricted', 'closed'


# =====================================================================
# Evaluated Edge State
# =====================================================================

@dataclass(frozen=True)
class EdgeEvaluation:
    """Derived operational metrics for an edge under a specific flow & capacity condition."""

    edge_id: str
    source: str
    target: str
    length_km: float
    free_flow_speed_kmph: float
    nominal_capacity_veh_per_hour: float
    effective_capacity_veh_per_hour: float
    current_flow_veh_per_hour: float
    vc_ratio: Optional[float]
    free_flow_time_hours: float
    travel_time_hours: Optional[float]
    delay_hours_per_vehicle: Optional[float]
    total_delay_veh_hours: Optional[float]
    is_overloaded: bool
    is_closed: bool
    status: str

    @property
    def free_flow_time_minutes(self) -> float:
        """Free-flow travel time in minutes."""
        return self.free_flow_time_hours * 60.0

    @property
    def travel_time_minutes(self) -> Optional[float]:
        """Congested travel time in minutes (or None if closed)."""
        return (self.travel_time_hours * 60.0) if self.travel_time_hours is not None else None

    @property
    def delay_minutes_per_vehicle(self) -> Optional[float]:
        """Delay per vehicle in minutes (or None if closed)."""
        return (self.delay_hours_per_vehicle * 60.0) if self.delay_hours_per_vehicle is not None else None


# =====================================================================
# Demand & Disruptions
# =====================================================================

@dataclass(frozen=True)
class ODDemand:
    """Represents Origin-Destination vehicular demand volume."""

    id: str
    origin: str
    destination: str
    demand_veh_per_hour: float
    time_period: str = "peak"
    vehicle_class: str = "car"


@dataclass(frozen=True)
class Disruption:
    """Represents a physical or operational capacity reduction on an edge."""

    asset_id: str  # Must match an Edge.id
    disruption_type: str = "closure"  # 'closure', 'partial_closure', 'construction', 'weather'
    capacity_multiplier: float = 0.0  # Fraction of nominal capacity remaining [0.0, 1.0]


# =====================================================================
# Critical Infrastructure
# =====================================================================

@dataclass(frozen=True)
class CriticalAsset:
    """Represents critical city infrastructure attached to a network node."""

    id: str
    node_id: str
    asset_type: str  # 'hospital', 'fire_station', 'emergency_shelter', 'trauma_center'
    criticality_weight: float = 1.0


@dataclass(frozen=True)
class CriticalServiceImpact:
    """Evaluates changes in travel accessibility to a critical asset."""

    asset_id: str
    node_id: str
    asset_type: str
    origin_zone: str
    baseline_access_time_minutes: Optional[float]
    scenario_access_time_minutes: Optional[float]
    response_time_delta_minutes: Optional[float]
    access_lost: bool


# =====================================================================
# Routing & Simulation Results
# =====================================================================

@dataclass(frozen=True)
class ODRouteImpact:
    """Route comparison and detour metrics for a single OD pair."""

    od_id: str
    origin: str
    destination: str
    demand_veh_per_hour: float
    baseline_edge_ids: Tuple[str, ...]
    scenario_edge_ids: Optional[Tuple[str, ...]]
    rerouted: bool
    unserved: bool
    baseline_distance_km: float
    scenario_distance_km: Optional[float]
    extra_distance_km: Optional[float]
    baseline_travel_time_minutes: float
    scenario_travel_time_minutes: Optional[float]
    travel_time_change_minutes: Optional[float]


@dataclass(frozen=True)
class SimulationConfig:
    """Configuration hyperparameters for simulation and cascade evaluation."""

    overload_vc_threshold: float = 1.0
    alpha: float = 0.15
    beta: float = 4.0
    max_reassignment_iterations: int = 1
    convergence_tolerance: float = 0.01


@dataclass(frozen=True)
class SimulationResult:
    """Comprehensive immutable output of a network disruption simulation."""

    baseline_edges: Dict[str, EdgeEvaluation]
    scenario_edges: Dict[str, EdgeEvaluation]
    primary_disrupted_edges: List[str]
    newly_overloaded_edges: List[str]
    persistently_overloaded_edges: List[str]
    changed_routes: List[ODRouteImpact]
    all_routes: List[ODRouteImpact]
    unserved_od_ids: List[str]
    total_travel_time_change_minutes: float
    total_delay_change_vehicle_hours: float
    critical_service_impacts: List[CriticalServiceImpact]
    iterations_completed: int
    config: SimulationConfig
