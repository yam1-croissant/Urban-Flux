"""Comprehensive unit test suite for UrbanFlux Traffic Mathematics.

Covers:
- Free-flow travel time (multiple lengths, speeds, edge cases, input validation)
- Volume-to-Capacity ratio (low, moderate, near-capacity, over-capacity, overload un-clamped)
- BPR congestion function (standard and custom parameters, monotonicity, saturation)
- Per-vehicle and aggregate total delay calculations
- Capacity reductions (0%, 10%, 25%, 50%, 100% complete closure)
- Complete closure and zero capacity safety guarantees (no zero-division)
- High-level LinkImpactResult evaluation
"""

import pytest
import math
from src.simulation.traffic_math import (
    free_flow_time,
    vc_ratio,
    bpr_travel_time,
    delay_per_vehicle,
    total_delay,
    delay,
    reduced_capacity,
    evaluate_link_disruption,
    TrafficMathError,
    InvalidInputError,
    RoadClosedError,
    LinkImpactResult,
)


class TestFreeFlowTime:
    """Tests for free_flow_time(length_km, free_flow_speed_kmph)."""

    def test_standard_calculation(self):
        # 10 km at 50 km/h = 0.2 hours (12 minutes)
        t0 = free_flow_time(length_km=10.0, free_flow_speed_kmph=50.0)
        assert pytest.approx(t0, rel=1e-6) == 0.2

    def test_multiple_lengths_and_speeds(self):
        # 2.5 km at 30 km/h = 0.083333 h (5 min)
        assert pytest.approx(free_flow_time(2.5, 30.0), rel=1e-6) == 2.5 / 30.0
        # 15 km at 60 km/h = 0.25 h (15 min)
        assert pytest.approx(free_flow_time(15.0, 60.0), rel=1e-6) == 0.25
        # 0.5 km at 20 km/h = 0.025 h (1.5 min)
        assert pytest.approx(free_flow_time(0.5, 20.0), rel=1e-6) == 0.025

    def test_zero_length(self):
        # Zero-length link takes 0 hours
        assert free_flow_time(0.0, 40.0) == 0.0

    def test_negative_length_raises_error(self):
        with pytest.raises(InvalidInputError, match="length cannot be negative"):
            free_flow_time(length_km=-5.0, free_flow_speed_kmph=40.0)

    def test_zero_speed_raises_error(self):
        with pytest.raises(InvalidInputError, match="Free-flow speed must be strictly positive"):
            free_flow_time(length_km=10.0, free_flow_speed_kmph=0.0)

    def test_negative_speed_raises_error(self):
        with pytest.raises(InvalidInputError, match="Free-flow speed must be strictly positive"):
            free_flow_time(length_km=10.0, free_flow_speed_kmph=-30.0)


class TestVCRatio:
    """Tests for vc_ratio(volume, capacity)."""

    def test_low_traffic(self):
        # V/C = 0.25
        assert pytest.approx(vc_ratio(500, 2000), rel=1e-6) == 0.25

    def test_moderate_traffic(self):
        # V/C = 0.60
        assert pytest.approx(vc_ratio(1200, 2000), rel=1e-6) == 0.60

    def test_near_capacity(self):
        # V/C = 0.95 and 1.00
        assert pytest.approx(vc_ratio(1900, 2000), rel=1e-6) == 0.95
        assert pytest.approx(vc_ratio(2000, 2000), rel=1e-6) == 1.00

    def test_over_capacity_not_clamped(self):
        # Must retain overload visibility (> 1.0)
        assert pytest.approx(vc_ratio(2500, 2000), rel=1e-6) == 1.25
        assert pytest.approx(vc_ratio(4000, 2000), rel=1e-6) == 2.00

    def test_zero_volume(self):
        assert vc_ratio(0, 2000) == 0.0

    def test_zero_capacity_raises_road_closed_error(self):
        with pytest.raises(RoadClosedError, match="zero capacity"):
            vc_ratio(volume=1000, capacity=0.0)

    def test_negative_volume_raises_error(self):
        with pytest.raises(InvalidInputError, match="volume cannot be negative"):
            vc_ratio(volume=-100, capacity=2000)

    def test_negative_capacity_raises_error(self):
        with pytest.raises(InvalidInputError, match="Capacity cannot be negative"):
            vc_ratio(volume=1000, capacity=-500)


class TestBPRTravelTime:
    """Tests for bpr_travel_time(free_flow_time_hours, volume, capacity, alpha, beta)."""

    def test_zero_volume_equals_free_flow(self):
        t0 = 0.2
        t = bpr_travel_time(free_flow_time_hours=t0, volume=0, capacity=2000)
        assert pytest.approx(t, rel=1e-6) == t0

    def test_at_capacity_standard_bpr(self):
        # At V = C, t = t0 * (1 + alpha * 1^beta) = t0 * (1 + 0.15) = 1.15 * t0
        t0 = 0.2
        t = bpr_travel_time(free_flow_time_hours=t0, volume=2000, capacity=2000, alpha=0.15, beta=4.0)
        assert pytest.approx(t, rel=1e-6) == 0.2 * 1.15

    def test_over_capacity_steep_increase(self):
        # At V/C = 1.5, t = t0 * (1 + 0.15 * 1.5^4) = t0 * (1 + 0.15 * 5.0625) = t0 * 1.759375
        t0 = 0.2
        t = bpr_travel_time(free_flow_time_hours=t0, volume=3000, capacity=2000, alpha=0.15, beta=4.0)
        expected = 0.2 * (1.0 + 0.15 * (1.5 ** 4.0))
        assert pytest.approx(t, rel=1e-6) == expected

    def test_custom_alpha_beta(self):
        # Test configurable alpha and beta parameters
        t0 = 0.5
        t = bpr_travel_time(
            free_flow_time_hours=t0,
            volume=1000,
            capacity=1000,
            alpha=0.5,
            beta=2.0,
        )
        # t = 0.5 * (1 + 0.5 * (1)^2) = 0.5 * 1.5 = 0.75
        assert pytest.approx(t, rel=1e-6) == 0.75

    def test_monotonicity_with_volume(self):
        # Travel time strictly increases as volume grows
        t0 = 0.1
        cap = 1000.0
        volumes = [100, 500, 800, 1000, 1200, 1500, 2000]
        times = [bpr_travel_time(t0, v, cap) for v in volumes]
        assert all(t1 < t2 for t1, t2 in zip(times, times[1:]))

    def test_monotonicity_with_capacity_reduction(self):
        # Travel time strictly increases as capacity drops under constant volume
        t0 = 0.1
        vol = 800.0
        capacities = [2000.0, 1500.0, 1000.0, 850.0, 800.0, 600.0]
        times = [bpr_travel_time(t0, vol, c) for c in capacities]
        assert all(t1 < t2 for t1, t2 in zip(times, times[1:]))

    def test_zero_capacity_raises_road_closed_error(self):
        with pytest.raises(RoadClosedError):
            bpr_travel_time(free_flow_time_hours=0.2, volume=1000, capacity=0.0)

    def test_invalid_parameters_raise_errors(self):
        with pytest.raises(InvalidInputError, match="Free-flow travel time"):
            bpr_travel_time(free_flow_time_hours=-0.1, volume=100, capacity=1000)
        with pytest.raises(InvalidInputError, match="volume"):
            bpr_travel_time(free_flow_time_hours=0.1, volume=-100, capacity=1000)
        with pytest.raises(InvalidInputError, match="alpha"):
            bpr_travel_time(free_flow_time_hours=0.1, volume=100, capacity=1000, alpha=-0.15)
        with pytest.raises(InvalidInputError, match="beta"):
            bpr_travel_time(free_flow_time_hours=0.1, volume=100, capacity=1000, beta=-2.0)


class TestDelayCalculations:
    """Tests for delay, delay_per_vehicle, and total_delay."""

    def test_delay_per_vehicle_zero_when_uncongested(self):
        assert delay_per_vehicle(travel_time_hours=0.2, free_flow_time_hours=0.2) == 0.0

    def test_delay_per_vehicle_positive(self):
        d = delay_per_vehicle(travel_time_hours=0.35, free_flow_time_hours=0.20)
        assert pytest.approx(d, rel=1e-6) == 0.15

    def test_total_delay_calculation(self):
        # 1000 vehicles experiencing 0.15 hours delay each = 150 vehicle-hours
        tot = total_delay(travel_time_hours=0.35, free_flow_time_hours=0.20, volume=1000.0)
        assert pytest.approx(tot, rel=1e-6) == 150.0

    def test_unified_delay_function(self):
        # When volume is None -> per-vehicle delay
        assert pytest.approx(delay(0.35, 0.20), rel=1e-6) == 0.15
        # When volume is passed -> total delay
        assert pytest.approx(delay(0.35, 0.20, volume=500.0), rel=1e-6) == 75.0

    def test_delay_negative_inputs_raise_errors(self):
        with pytest.raises(InvalidInputError):
            delay_per_vehicle(-0.1, 0.2)
        with pytest.raises(InvalidInputError):
            delay_per_vehicle(0.2, -0.1)
        with pytest.raises(InvalidInputError):
            total_delay(0.3, 0.2, -50)


class TestReducedCapacity:
    """Tests for reduced_capacity(capacity, reduction_fraction)."""

    @pytest.mark.parametrize("reduction, expected_fraction", [
        (0.00, 1.00),
        (0.10, 0.90),
        (0.25, 0.75),
        (0.50, 0.50),
        (1.00, 0.00),
    ])
    def test_standard_reductions(self, reduction, expected_fraction):
        nominal_cap = 2000.0
        eff = reduced_capacity(nominal_cap, reduction)
        assert pytest.approx(eff, rel=1e-6) == nominal_cap * expected_fraction

    def test_complete_closure(self):
        assert reduced_capacity(2500.0, 1.0) == 0.0

    def test_invalid_reduction_fraction_raises_error(self):
        with pytest.raises(InvalidInputError, match="must be between 0.0 and 1.0"):
            reduced_capacity(2000.0, -0.1)
        with pytest.raises(InvalidInputError, match="must be between 0.0 and 1.0"):
            reduced_capacity(2000.0, 1.01)

    def test_negative_capacity_raises_error(self):
        with pytest.raises(InvalidInputError, match="Capacity cannot be negative"):
            reduced_capacity(-1000.0, 0.5)


class TestLinkDisruptionEvaluation:
    """Tests for evaluate_link_disruption composite function and LinkImpactResult."""

    def test_baseline_evaluation(self):
        res = evaluate_link_disruption(
            length_km=5.0,
            free_flow_speed_kmph=50.0,
            volume=1200.0,
            nominal_capacity=2000.0,
            reduction_fraction=0.0,
        )
        assert not res.is_closed
        assert pytest.approx(res.free_flow_time_hours, rel=1e-6) == 0.1
        assert pytest.approx(res.free_flow_time_minutes, rel=1e-6) == 6.0
        assert pytest.approx(res.effective_capacity, rel=1e-6) == 2000.0
        assert pytest.approx(res.vc_ratio, rel=1e-6) == 0.6
        assert res.travel_time_hours is not None
        assert res.travel_time_minutes is not None
        assert res.delay_per_vehicle_minutes is not None
        assert res.total_delay_veh_hours is not None

    def test_partial_disruption_50_percent(self):
        res = evaluate_link_disruption(
            length_km=5.0,
            free_flow_speed_kmph=50.0,
            volume=1200.0,
            nominal_capacity=2000.0,
            reduction_fraction=0.50,
        )
        assert not res.is_closed
        assert pytest.approx(res.effective_capacity, rel=1e-6) == 1000.0
        assert pytest.approx(res.vc_ratio, rel=1e-6) == 1.2
        assert res.travel_time_hours > 0.1

    def test_complete_closure_100_percent(self):
        res = evaluate_link_disruption(
            length_km=5.0,
            free_flow_speed_kmph=50.0,
            volume=1200.0,
            nominal_capacity=2000.0,
            reduction_fraction=1.00,
        )
        assert res.is_closed
        assert res.effective_capacity == 0.0
        assert res.vc_ratio is None
        assert res.travel_time_hours is None
        assert res.travel_time_minutes is None
        assert res.delay_per_vehicle_hours is None
        assert "closure" in res.status_note.lower()
