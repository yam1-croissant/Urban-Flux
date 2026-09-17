"""UrbanFlux — Part B: Unit & Integration Tests for Network Disruption & Cascade.

Verifies:
1. Directed graph semantics and directionality enforcement.
2. Baseline shortest-path demand assignment.
3. Full edge closure & deterministic alternate route selection.
4. Partial capacity degradation impact on travel time without closure.
5. Flow accumulation and cascading overload detection on alternate links.
6. Distinction between newly overloaded and persistently overloaded edges.
7. Explicit unserved demand handling when destination is disconnected.
8. Critical infrastructure (hospital) accessibility impact assessment.
9. Determinism, idempotence, and non-mutation of baseline network.
10. Network topology and disruption input validation.
"""

import pytest
from src.simulation.models import (
    CriticalAsset,
    Disruption,
    DisruptionError,
    Edge,
    NetworkValidationError,
    Node,
    ODDemand,
    RouteNotFoundError,
    SimulationConfig,
)
from src.simulation.graph import RoadNetwork
from src.simulation.simulation import simulate


@pytest.fixture
def sample_network() -> RoadNetwork:
    r"""Constructs a deterministic synthetic test network:

          B (Bridge) --- C (Hospital)
         /               |
        A                |
         \               |
          E ------------ F
    """
    nodes = [
        Node(id="A", node_type="zone"),
        Node(id="B", node_type="junction"),
        Node(id="C", node_type="critical_asset"),
        Node(id="E", node_type="junction"),
        Node(id="F", node_type="junction"),
    ]
    edges = [
        # Primary northern corridor: A -> B -> C (Short & fast)
        Edge(id="A_B", source="A", target="B", length_km=2.0, free_flow_speed_kmph=60.0, nominal_capacity_veh_per_hour=2000.0),
        Edge(id="B_C", source="B", target="C", length_km=3.0, free_flow_speed_kmph=60.0, nominal_capacity_veh_per_hour=2000.0),
        # Alternate southern detour: A -> E -> F -> C (Longer & lower capacity)
        Edge(id="A_E", source="A", target="E", length_km=4.0, free_flow_speed_kmph=50.0, nominal_capacity_veh_per_hour=1500.0),
        Edge(id="E_F", source="E", target="F", length_km=5.0, free_flow_speed_kmph=50.0, nominal_capacity_veh_per_hour=1200.0),
        Edge(id="F_C", source="F", target="C", length_km=2.0, free_flow_speed_kmph=50.0, nominal_capacity_veh_per_hour=1500.0),
    ]
    return RoadNetwork(nodes=nodes, edges=edges)


class TestNetworkGraphValidation:
    """Tests graph structure, directionality, and validation rules."""

    def test_directionality_enforcement(self, sample_network):
        # A -> B exists, but B -> A should fail because graph is directed
        path, cost = sample_network.find_shortest_path("A", "B")
        assert path == ["A_B"]
        assert cost > 0.0

        with pytest.raises(RouteNotFoundError):
            sample_network.find_shortest_path("B", "A")

    def test_duplicate_node_id_raises_error(self):
        nodes = [Node(id="A"), Node(id="A")]
        with pytest.raises(NetworkValidationError, match="Duplicate node ID"):
            RoadNetwork(nodes=nodes, edges=[])

    def test_duplicate_edge_id_raises_error(self):
        nodes = [Node(id="A"), Node(id="B")]
        edges = [
            Edge(id="e1", source="A", target="B", length_km=1.0, free_flow_speed_kmph=50.0, nominal_capacity_veh_per_hour=1000.0),
            Edge(id="e1", source="A", target="B", length_km=2.0, free_flow_speed_kmph=50.0, nominal_capacity_veh_per_hour=1000.0),
        ]
        with pytest.raises(NetworkValidationError, match="Duplicate edge ID"):
            RoadNetwork(nodes=nodes, edges=edges)

    def test_missing_endpoint_node_raises_error(self):
        nodes = [Node(id="A")]
        edges = [
            Edge(id="e1", source="A", target="NON_EXISTENT", length_km=1.0, free_flow_speed_kmph=50.0, nominal_capacity_veh_per_hour=1000.0)
        ]
        with pytest.raises(NetworkValidationError, match="undefined target node"):
            RoadNetwork(nodes=nodes, edges=edges)

    def test_invalid_edge_properties_raise_error(self):
        nodes = [Node(id="A"), Node(id="B")]
        # Negative length
        with pytest.raises(NetworkValidationError, match="negative length"):
            RoadNetwork(nodes=nodes, edges=[Edge(id="e1", source="A", target="B", length_km=-1.0, free_flow_speed_kmph=50.0, nominal_capacity_veh_per_hour=1000.0)])
        # Zero speed
        with pytest.raises(NetworkValidationError, match="non-positive speed"):
            RoadNetwork(nodes=nodes, edges=[Edge(id="e1", source="A", target="B", length_km=1.0, free_flow_speed_kmph=0.0, nominal_capacity_veh_per_hour=1000.0)])
        # Negative capacity
        with pytest.raises(NetworkValidationError, match="non-positive capacity"):
            RoadNetwork(nodes=nodes, edges=[Edge(id="e1", source="A", target="B", length_km=1.0, free_flow_speed_kmph=50.0, nominal_capacity_veh_per_hour=-500.0)])


class TestBaselineAndDisruptionSimulation:
    """Tests baseline routing, disruption application, rerouting, and cascading overload."""

    def test_baseline_shortest_path_assignment(self, sample_network):
        demands = [ODDemand(id="od_A_C", origin="A", destination="C", demand_veh_per_hour=1000.0)]
        res = simulate(network=sample_network, od_demands=demands)

        # Baseline route should be the shorter northern corridor: A_B -> B_C (5 km vs 11 km)
        od_res = res.all_routes[0]
        assert od_res.baseline_edge_ids == ("A_B", "B_C")
        assert not od_res.rerouted
        assert not od_res.unserved
        assert od_res.baseline_distance_km == 5.0
        assert res.scenario_edges["A_B"].current_flow_veh_per_hour == 1000.0
        assert res.scenario_edges["E_F"].current_flow_veh_per_hour == 0.0

    def test_bridge_closure_rerouting_and_secondary_overload(self, sample_network):
        # High demand: 1100 veh/h. Alternate bottleneck E_F has nominal capacity 1200 veh/h with 300 veh/h baseline flow
        # In baseline, E_F has 300 flow (V/C = 0.25).
        # When A_B closes, demand shifts to A_E -> E_F -> F_C.
        # E_F receives 300 + 1100 = 1400 veh/h -> V/C = 1400/1200 = 1.167 (Overloaded!)
        nodes = sample_network.nodes.values()
        edges = list(sample_network.edges.values())
        # Add 300 baseline flow to E_F
        edges[3] = Edge(id="E_F", source="E", target="F", length_km=5.0, free_flow_speed_kmph=50.0, nominal_capacity_veh_per_hour=1200.0, baseline_flow_veh_per_hour=300.0)
        net = RoadNetwork(nodes=nodes, edges=edges)

        demands = [ODDemand(id="od_A_C", origin="A", destination="C", demand_veh_per_hour=1100.0)]
        disruptions = [Disruption(asset_id="A_B", disruption_type="closure", capacity_multiplier=0.0)]
        hospital = CriticalAsset(id="city_hospital", node_id="C", asset_type="hospital")

        res = simulate(
            network=net,
            od_demands=demands,
            disruptions=disruptions,
            critical_assets=[hospital],
            config=SimulationConfig(overload_vc_threshold=1.0),
        )

        # 1. Closed edge
        assert res.scenario_edges["A_B"].is_closed
        assert res.scenario_edges["A_B"].effective_capacity_veh_per_hour == 0.0
        assert "A_B" in res.primary_disrupted_edges

        # 2. Rerouted path
        od_res = res.all_routes[0]
        assert od_res.rerouted
        assert od_res.scenario_edge_ids == ("A_E", "E_F", "F_C")
        assert od_res.extra_distance_km == 6.0  # 11 km - 5 km
        assert od_res.travel_time_change_minutes > 0.0

        # 3. Secondary overload detected on alternate link
        assert res.scenario_edges["E_F"].current_flow_veh_per_hour == 1400.0
        assert res.scenario_edges["E_F"].vc_ratio > 1.0
        assert res.scenario_edges["E_F"].is_overloaded
        assert "E_F" in res.newly_overloaded_edges

        # 4. Hospital access impact
        assert len(res.critical_service_impacts) == 1
        hosp_impact = res.critical_service_impacts[0]
        assert not hosp_impact.access_lost
        assert hosp_impact.response_time_delta_minutes > 0.0

    def test_persistent_overload_not_classified_as_newly_overloaded(self, sample_network):
        # If an edge is ALREADY overloaded in baseline (V/C > 1.0), it should be in persistently_overloaded_edges, not newly_overloaded_edges
        nodes = sample_network.nodes.values()
        edges = list(sample_network.edges.values())
        # Set E_F baseline flow to 1300 veh/h on 1200 capacity (V/C = 1.08 in baseline)
        edges[3] = Edge(id="E_F", source="E", target="F", length_km=5.0, free_flow_speed_kmph=50.0, nominal_capacity_veh_per_hour=1200.0, baseline_flow_veh_per_hour=1300.0)
        net = RoadNetwork(nodes=nodes, edges=edges)

        demands = [ODDemand(id="od_A_C", origin="A", destination="C", demand_veh_per_hour=500.0)]
        disruptions = [Disruption(asset_id="A_B", disruption_type="closure", capacity_multiplier=0.0)]

        res = simulate(network=net, od_demands=demands, disruptions=disruptions)

        assert "E_F" in res.persistently_overloaded_edges
        assert "E_F" not in res.newly_overloaded_edges

    def test_partial_capacity_reduction(self, sample_network):
        # 50% capacity reduction on A_B (capacity drops from 2000 -> 1000)
        demands = [ODDemand(id="od_A_C", origin="A", destination="C", demand_veh_per_hour=800.0)]
        disruptions = [Disruption(asset_id="A_B", disruption_type="partial_closure", capacity_multiplier=0.5)]

        res = simulate(network=sample_network, od_demands=demands, disruptions=disruptions)

        ab_base = res.baseline_edges["A_B"]
        ab_scen = res.scenario_edges["A_B"]

        assert ab_base.effective_capacity_veh_per_hour == 2000.0
        assert ab_scen.effective_capacity_veh_per_hour == 1000.0
        assert not ab_scen.is_closed
        assert ab_scen.vc_ratio == 0.8
        assert ab_scen.travel_time_hours > ab_base.travel_time_hours

    def test_unserved_demand_when_all_paths_closed(self, sample_network):
        # Close both A_B and A_E -> node A is completely cut off from C
        demands = [ODDemand(id="od_A_C", origin="A", destination="C", demand_veh_per_hour=500.0)]
        disruptions = [
            Disruption(asset_id="A_B", capacity_multiplier=0.0),
            Disruption(asset_id="A_E", capacity_multiplier=0.0),
        ]
        hospital = CriticalAsset(id="hosp", node_id="C", asset_type="hospital")

        res = simulate(
            network=sample_network,
            od_demands=demands,
            disruptions=disruptions,
            critical_assets=[hospital],
        )

        assert "od_A_C" in res.unserved_od_ids
        route = res.all_routes[0]
        assert route.unserved
        assert route.scenario_edge_ids is None
        assert route.scenario_travel_time_minutes is None
        assert route.travel_time_change_minutes is None

        # Hospital access is flagged as lost
        assert res.critical_service_impacts[0].access_lost
        assert res.critical_service_impacts[0].scenario_access_time_minutes is None

    def test_determinism_and_non_mutation(self, sample_network):
        demands = [ODDemand(id="od1", origin="A", destination="C", demand_veh_per_hour=800.0)]
        disruptions = [Disruption(asset_id="A_B", capacity_multiplier=0.0)]

        res1 = simulate(network=sample_network, od_demands=demands, disruptions=disruptions)
        res2 = simulate(network=sample_network, od_demands=demands, disruptions=disruptions)

        assert res1.total_travel_time_change_minutes == res2.total_travel_time_change_minutes
        assert res1.newly_overloaded_edges == res2.newly_overloaded_edges
        # Verify baseline edges in sample_network were not mutated
        assert sample_network.edges["A_B"].status == "open"
        assert sample_network.edges["A_B"].nominal_capacity_veh_per_hour == 2000.0

    def test_invalid_disruption_raises_error(self, sample_network):
        demands = [ODDemand(id="od1", origin="A", destination="C", demand_veh_per_hour=100.0)]
        with pytest.raises(DisruptionError, match="unknown edge ID"):
            simulate(network=sample_network, od_demands=demands, disruptions=[Disruption(asset_id="INVALID_EDGE", capacity_multiplier=0.0)])

        with pytest.raises(DisruptionError, match="must be in"):
            simulate(network=sample_network, od_demands=demands, disruptions=[Disruption(asset_id="A_B", capacity_multiplier=1.5)])
