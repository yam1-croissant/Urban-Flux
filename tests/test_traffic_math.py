"""Unit tests for traffic mathematics module (src.simulation.traffic_math)."""

import math
import pytest

from src.simulation.traffic_math import (
    RoadConditionResult,
    bpr_travel_time,
    delay,
    delay_per_vehicle,
    evaluate_road_condition,
    free_flow_time,
    peak_hourly_volume,
    reduced_capacity,
    total_delay,
    vc_ratio,
)


class TestFreeFlowTime:
    """Tests for free_flow_time(length_km, free_flow_speed_kmh, unit)."""

    def test_standard_minutes(self):
        # 10 km at 60 km/h = 1/6 hour = 10 minutes
        t0 = free_flow_time(10.0, 60.0, unit="minutes")
        assert math.isclose(t0, 10.0, rel_tol=1e-5)

    def test_unit_hours(self):
        t0 = free_flow_time(60.0, 60.0, unit="hours")
        assert math.isclose(t0, 1.0, rel_tol=1e-5)

    def test_unit_seconds(self):
        # 1 km at 60 km/h = 60 seconds
        t0 = free_flow_time(1.0, 60.0, unit="seconds")
        assert math.isclose(t0, 60.0, rel_tol=1e-5)

    def test_zero_length(self):
        t0 = free_flow_time(0.0, 50.0)
        assert t0 == 0.0

    def test_varying_lengths_and_speeds(self):
        # 2.5 km corridor (e.g. Marathahalli Bridge) at 50 km/h
        t0 = free_flow_time(2.5, 50.0, unit="minutes")
        assert math.isclose(t0, 3.0, rel_tol=1e-5)  # 2.5/50 * 60 = 3 min

        # 12 km outer ring road section at 80 km/h
        t0 = free_flow_time(12.0, 80.0, unit="minutes")
        assert math.isclose(t0, 9.0, rel_tol=1e-5)  # 12/80 * 60 = 9 min

    def test_negative_length_raises_error(self):
        with pytest.raises(ValueError, match="length cannot be negative"):
            free_flow_time(-5.0, 60.0)

    def test_zero_or_negative_speed_raises_error(self):
        with pytest.raises(ValueError, match="speed must be strictly positive"):
            free_flow_time(10.0, 0.0)
        with pytest.raises(ValueError, match="speed must be strictly positive"):
            free_flow_time(10.0, -30.0)

    def test_invalid_unit_raises_error(self):
        with pytest.raises(ValueError, match="Invalid time unit"):
            free_flow_time(10.0, 60.0, unit="days")


class TestVCRatio:
    """Tests for vc_ratio(volume, capacity)."""

    def test_low_traffic(self):
        # V << C
        vc = vc_ratio(200.0, 2000.0)
        assert math.isclose(vc, 0.1, rel_tol=1e-5)

    def test_moderate_traffic(self):
        # V = 0.5 * C
        vc = vc_ratio(1000.0, 2000.0)
        assert math.isclose(vc, 0.5, rel_tol=1e-5)

    def test_near_capacity(self):
        # V ~= C
        vc = vc_ratio(1980.0, 2000.0)
        assert math.isclose(vc, 0.99, rel_tol=1e-5)

    def test_at_capacity(self):
        vc = vc_ratio(2000.0, 2000.0)
        assert math.isclose(vc, 1.0, rel_tol=1e-5)

    def test_oversaturated_traffic(self):
        # V > C
        vc = vc_ratio(3000.0, 2000.0)
        assert math.isclose(vc, 1.5, rel_tol=1e-5)

    def test_zero_volume(self):
        vc = vc_ratio(0.0, 2000.0)
        assert vc == 0.0

    def test_zero_capacity_nonzero_volume(self):
        # Closed road under demand -> infinite V/C
        vc = vc_ratio(500.0, 0.0)
        assert math.isinf(vc)

    def test_zero_capacity_zero_volume(self):
        # Closed road with zero volume
        vc = vc_ratio(0.0, 0.0)
        assert vc == 0.0

    def test_negative_inputs_raise_error(self):
        with pytest.raises(ValueError, match="volume cannot be negative"):
            vc_ratio(-10.0, 1000.0)
        with pytest.raises(ValueError, match="capacity cannot be negative"):
            vc_ratio(100.0, -500.0)


class TestBPRTravelTime:
    """Tests for bpr_travel_time(t0, vc, alpha, beta, max_travel_time)."""

    def test_zero_volume(self):
        # When V/C == 0, t = t0
        t = bpr_travel_time(10.0, 0.0)
        assert math.isclose(t, 10.0, rel_tol=1e-5)

    def test_low_traffic(self):
        # V/C = 0.2: t ~= t0 * (1 + 0.15 * 0.2^4) = t0 * 1.00024
        t = bpr_travel_time(10.0, 0.2, alpha=0.15, beta=4.0)
        assert math.isclose(t, 10.0 * (1.0 + 0.15 * (0.2**4)), rel_tol=1e-5)

    def test_at_capacity(self):
        # At V/C = 1.0, t = t0 * (1 + alpha) = 10 * 1.15 = 11.5
        t = bpr_travel_time(10.0, 1.0, alpha=0.15, beta=4.0)
        assert math.isclose(t, 11.5, rel_tol=1e-5)

    def test_oversaturated(self):
        # V/C = 1.5: t = 10 * (1 + 0.15 * 1.5^4) = 10 * (1 + 0.15 * 5.0625) = 17.59375
        t = bpr_travel_time(10.0, 1.5, alpha=0.15, beta=4.0)
        expected = 10.0 * (1.0 + 0.15 * (1.5**4))
        assert math.isclose(t, expected, rel_tol=1e-5)

    def test_infinite_vc(self):
        t = bpr_travel_time(10.0, float("inf"))
        assert math.isinf(t)

    def test_zero_free_flow_time(self):
        t = bpr_travel_time(0.0, 1.5)
        assert t == 0.0

    def test_max_travel_time_cap(self):
        # When max_travel_time is specified, prevent unbounded blowup
        t = bpr_travel_time(10.0, 3.0, alpha=0.15, beta=4.0, max_travel_time=60.0)
        assert t == 60.0

    def test_custom_parameters(self):
        # Calibrated parameters (e.g. alpha=0.5, beta=2.0)
        t = bpr_travel_time(10.0, 0.8, alpha=0.5, beta=2.0)
        expected = 10.0 * (1.0 + 0.5 * (0.8**2))
        assert math.isclose(t, expected, rel_tol=1e-5)

    def test_invalid_parameters_raise_error(self):
        with pytest.raises(ValueError, match="Free-flow time cannot be negative"):
            bpr_travel_time(-1.0, 0.5)
        with pytest.raises(ValueError, match="ratio cannot be negative"):
            bpr_travel_time(10.0, -0.5)
        with pytest.raises(ValueError, match="Alpha parameter cannot be negative"):
            bpr_travel_time(10.0, 0.5, alpha=-0.1)
        with pytest.raises(ValueError, match="Beta parameter cannot be negative"):
            bpr_travel_time(10.0, 0.5, beta=-2.0)


class TestDelay:
    """Tests for delay_per_vehicle, total_delay, and unified delay()."""

    def test_no_delay_at_free_flow(self):
        d_veh = delay_per_vehicle(10.0, 10.0)
        assert d_veh == 0.0

        d_tot = total_delay(1500.0, 10.0, 10.0)
        assert d_tot == 0.0

    def test_delay_when_actual_less_than_free_flow(self):
        # Numerical or sensor artifact where measured time < t0
        d_veh = delay_per_vehicle(8.0, 10.0)
        assert d_veh == 0.0

    def test_positive_delay(self):
        # t = 15 min, t0 = 10 min -> delay = 5 min
        d_veh = delay_per_vehicle(15.0, 10.0)
        assert math.isclose(d_veh, 5.0, rel_tol=1e-5)

        # 2,000 vehicles -> total delay = 10,000 veh-min
        d_tot = total_delay(2000.0, 15.0, 10.0)
        assert math.isclose(d_tot, 10000.0, rel_tol=1e-5)

    def test_zero_volume_total_delay(self):
        d_tot = total_delay(0.0, 25.0, 10.0)
        assert d_tot == 0.0

    def test_infinite_travel_time(self):
        assert math.isinf(delay_per_vehicle(float("inf"), 10.0))
        assert math.isinf(total_delay(100.0, float("inf"), 10.0))
        assert total_delay(0.0, float("inf"), 10.0) == 0.0

    def test_unified_delay_function(self):
        # Without volume -> float
        res_single = delay(14.0, 10.0)
        assert math.isclose(res_single, 4.0, rel_tol=1e-5)

        # With volume -> tuple (per_veh, total)
        res_tuple = delay(14.0, 10.0, volume=500.0)
        assert isinstance(res_tuple, tuple)
        assert math.isclose(res_tuple[0], 4.0, rel_tol=1e-5)
        assert math.isclose(res_tuple[1], 2000.0, rel_tol=1e-5)


class TestCapacityReductionAndClosure:
    """Tests for reduced_capacity(nominal_capacity, reduction_ratio)."""

    def test_no_reduction(self):
        c = reduced_capacity(2000.0, 0.0)
        assert math.isclose(c, 2000.0, rel_tol=1e-5)

    def test_ten_percent_reduction(self):
        c = reduced_capacity(2000.0, 0.10)
        assert math.isclose(c, 1800.0, rel_tol=1e-5)

    def test_twenty_five_percent_reduction(self):
        c = reduced_capacity(2000.0, 0.25)
        assert math.isclose(c, 1500.0, rel_tol=1e-5)

    def test_fifty_percent_reduction(self):
        c = reduced_capacity(2000.0, 0.50)
        assert math.isclose(c, 1000.0, rel_tol=1e-5)

    def test_complete_road_closure(self):
        c = reduced_capacity(2000.0, 1.00)
        assert c == 0.0

    def test_invalid_reduction_ratios_raise_error(self):
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            reduced_capacity(2000.0, -0.05)
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            reduced_capacity(2000.0, 1.05)

    def test_negative_capacity_raises_error(self):
        with pytest.raises(ValueError, match="capacity cannot be negative"):
            reduced_capacity(-100.0, 0.2)


class TestPeakHourlyVolume:
    """Tests for peak_hourly_volume(daily_volume, k_factor)."""

    def test_standard_k_factor(self):
        # 30,000 daily vehicles * 0.10 = 3,000 peak hour vehicles
        v_peak = peak_hourly_volume(30000.0, k_factor=0.10)
        assert math.isclose(v_peak, 3000.0, rel_tol=1e-5)

    def test_custom_k_factor(self):
        v_peak = peak_hourly_volume(40000.0, k_factor=0.08)
        assert math.isclose(v_peak, 3200.0, rel_tol=1e-5)

    def test_invalid_k_factor(self):
        with pytest.raises(ValueError, match="K-factor must be in range"):
            peak_hourly_volume(10000.0, k_factor=0.0)
        with pytest.raises(ValueError, match="K-factor must be in range"):
            peak_hourly_volume(10000.0, k_factor=1.2)


class TestEvaluateRoadCondition:
    """End-to-end integration tests for evaluate_road_condition."""

    def test_baseline_uncongested(self):
        # 3 km corridor, 60 km/h (t0 = 3.0 min), C = 2000, V = 800
        res = evaluate_road_condition(
            length_km=3.0,
            free_flow_speed_kmh=60.0,
            nominal_capacity=2000.0,
            volume=800.0,
            capacity_reduction_ratio=0.0,
        )
        assert isinstance(res, RoadConditionResult)
        assert math.isclose(res.free_flow_time, 3.0, rel_tol=1e-5)
        assert math.isclose(res.effective_capacity, 2000.0, rel_tol=1e-5)
        assert math.isclose(res.vc_ratio, 0.4, rel_tol=1e-5)
        assert res.travel_time > 3.0
        assert res.travel_time < 3.1  # very little congestion at V/C = 0.4
        assert not res.is_closed

    def test_partial_disruption_escalation(self):
        # 50% capacity cut on a road with 1,200 veh/h demand
        res = evaluate_road_condition(
            length_km=3.0,
            free_flow_speed_kmh=60.0,
            nominal_capacity=2000.0,
            volume=1200.0,
            capacity_reduction_ratio=0.50,
        )
        # Effective capacity drops to 1,000 veh/h -> V/C becomes 1.2
        assert math.isclose(res.effective_capacity, 1000.0, rel_tol=1e-5)
        assert math.isclose(res.vc_ratio, 1.2, rel_tol=1e-5)
        # BPR travel time = 3.0 * (1 + 0.15 * 1.2^4) = 3.0 * (1 + 0.15 * 2.0736) = 3.933 min
        assert res.travel_time > 3.9
        assert res.delay_per_vehicle > 0.9
        assert res.total_delay > 1000.0
        assert not res.is_closed

    def test_complete_closure(self):
        res = evaluate_road_condition(
            length_km=3.0,
            free_flow_speed_kmh=60.0,
            nominal_capacity=2000.0,
            volume=1200.0,
            capacity_reduction_ratio=1.00,
        )
        assert res.effective_capacity == 0.0
        assert math.isinf(res.vc_ratio)
        assert math.isinf(res.travel_time)
        assert math.isinf(res.delay_per_vehicle)
        assert math.isinf(res.total_delay)
        assert res.is_closed

