"""UrbanFlux — Part B: Road Network Graph Representation & Shortest Path.

Provides strict topology validation and deterministic Dijkstra routing
with lexicographical tie-breaking.
"""

from __future__ import annotations

import heapq
from typing import Dict, Iterable, List, Optional, Set, Tuple

from src.simulation.models import (
    Edge,
    NetworkValidationError,
    Node,
    RouteNotFoundError,
)


class RoadNetwork:
    """Directed road network graph with explicit node and edge constraints."""

    def __init__(self, nodes: Iterable[Node], edges: Iterable[Edge]):
        self._nodes: Dict[str, Node] = {}
        self._edges: Dict[str, Edge] = {}
        self._outgoing: Dict[str, List[Edge]] = {}

        for n in nodes:
            if n.id in self._nodes:
                raise NetworkValidationError(f"Duplicate node ID found: '{n.id}'")
            self._nodes[n.id] = n
            self._outgoing[n.id] = []

        for e in edges:
            if e.id in self._edges:
                raise NetworkValidationError(f"Duplicate edge ID found: '{e.id}'")
            if e.source not in self._nodes:
                raise NetworkValidationError(
                    f"Edge '{e.id}' references undefined source node '{e.source}'"
                )
            if e.target not in self._nodes:
                raise NetworkValidationError(
                    f"Edge '{e.id}' references undefined target node '{e.target}'"
                )
            if e.length_km < 0.0:
                raise NetworkValidationError(
                    f"Edge '{e.id}' has negative length: {e.length_km} km"
                )
            if e.free_flow_speed_kmph <= 0.0:
                raise NetworkValidationError(
                    f"Edge '{e.id}' has non-positive speed: {e.free_flow_speed_kmph} km/h"
                )
            if e.nominal_capacity_veh_per_hour <= 0.0:
                raise NetworkValidationError(
                    f"Edge '{e.id}' has non-positive capacity: {e.nominal_capacity_veh_per_hour} veh/h"
                )
            if e.baseline_flow_veh_per_hour < 0.0:
                raise NetworkValidationError(
                    f"Edge '{e.id}' has negative baseline flow: {e.baseline_flow_veh_per_hour} veh/h"
                )

            self._edges[e.id] = e
            self._outgoing[e.source].append(e)

        # Sort outgoing edges by edge ID for complete determinism during traversal
        for node_id in self._outgoing:
            self._outgoing[node_id].sort(key=lambda edge: edge.id)

    @property
    def nodes(self) -> Dict[str, Node]:
        """Immutable view of network nodes."""
        return dict(self._nodes)

    @property
    def edges(self) -> Dict[str, Edge]:
        """Immutable view of network edges."""
        return dict(self._edges)

    def get_outgoing_edges(self, node_id: str) -> List[Edge]:
        """Return list of outgoing edges from a node."""
        if node_id not in self._nodes:
            raise NetworkValidationError(f"Node '{node_id}' does not exist in network.")
        return list(self._outgoing.get(node_id, []))

    def find_shortest_path(
        self,
        origin: str,
        destination: str,
        edge_weights: Optional[Dict[str, float]] = None,
        excluded_edge_ids: Optional[Set[str]] = None,
    ) -> Tuple[List[str], float]:
        """Find the deterministic shortest path between origin and destination.

        Uses Dijkstra's algorithm with edge weights (defaulting to free-flow time).
        Ties are broken deterministically using lexicographical path sequence.

        Args:
            origin: Origin node ID.
            destination: Destination node ID.
            edge_weights: Dict mapping edge_id -> cost (hours). If None, uses edge free-flow time.
            excluded_edge_ids: Set of edge IDs to ignore (e.g. closed/impassable links).

        Returns:
            Tuple of (list_of_edge_ids, total_cost).

        Raises:
            NetworkValidationError: If origin or destination nodes do not exist.
            RouteNotFoundError: If no feasible path exists between origin and destination.
        """
        if origin not in self._nodes:
            raise NetworkValidationError(f"Origin node '{origin}' not found in network.")
        if destination not in self._nodes:
            raise NetworkValidationError(f"Destination node '{destination}' not found in network.")

        if origin == destination:
            return ([], 0.0)

        excluded = excluded_edge_ids or set()

        # Priority queue stores tuples: (cost, path_tuple, current_node)
        # Including path_tuple ensures deterministic tie-breaking without comparing Node objects
        counter = 0
        heap: List[Tuple[float, Tuple[str, ...], str]] = [(0.0, (), origin)]
        best_costs: Dict[str, float] = {origin: 0.0}
        best_paths: Dict[str, Tuple[str, ...]] = {origin: ()}

        while heap:
            curr_cost, curr_path, curr_node = heapq.heappop(heap)

            # If we reached the destination with the best cost, return
            if curr_node == destination:
                return (list(curr_path), curr_cost)

            # If this popped entry is worse than an already found route to curr_node, skip
            if curr_cost > best_costs.get(curr_node, float('inf')):
                continue

            for edge in self._outgoing.get(curr_node, []):
                if edge.id in excluded:
                    continue

                weight = edge_weights[edge.id] if edge_weights and edge.id in edge_weights else (
                    edge.length_km / edge.free_flow_speed_kmph
                )

                if weight < 0.0:
                    raise NetworkValidationError(
                        f"Negative edge weight encountered for edge '{edge.id}': {weight}"
                    )

                new_cost = curr_cost + weight
                new_path = curr_path + (edge.id,)
                neighbor = edge.target

                # Strict improvement or deterministic tie-breaker (lexicographically smaller path)
                if new_cost < best_costs.get(neighbor, float('inf')) - 1e-12:
                    best_costs[neighbor] = new_cost
                    best_paths[neighbor] = new_path
                    heapq.heappush(heap, (new_cost, new_path, neighbor))
                elif abs(new_cost - best_costs.get(neighbor, float('inf'))) <= 1e-12:
                    if new_path < best_paths.get(neighbor, ()):
                        best_paths[neighbor] = new_path
                        heapq.heappush(heap, (new_cost, new_path, neighbor))

        raise RouteNotFoundError(
            f"No feasible path found from '{origin}' to '{destination}' "
            f"(excluded {len(excluded)} links)."
        )
