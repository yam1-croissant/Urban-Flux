"""Traffic Flow Mathematics Model for UrbanResilience.

Provides core mathematical relationships for link-level traffic dynamics,
congestion modeling via BPR (Bureau of Public Roads) formulation, capacity reduction,
road closure handling, and delay calculation.

Units:
- Distance: kilometers (km)
- Speed: kilometers per hour (km/h)
- Volume: vehicles per hour (veh/h) or vehicles per day (veh/day)
- Capacity: vehicles per hour (veh/h) or vehicles per day (veh/day)
- Travel Time & Delay: minutes by default (supports 'hours', 'minutes', 'seconds')
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple, Union


@dataclass(frozen=True)
class RoadConditionResult:
    """Represents the evaluated state of a road corridor or segment."""

    length_km: float
    free_flow_speed_kmh: float
    nominal_capacity: float
    capacity_reduction_ratio: float
    effective_capacity: float
    volume: float
    vc_ratio: float
    free_flow_time: float
    travel_time: float
    delay_per_vehicle: float
    total_delay: float
    is_closed: bool
    unit: str = "minutes"


def free_flow_time(
    length_km: float,
    free_flow_speed_kmh: float,
    unit: str = "minutes",
) -> float:
    """Calculate free-flow travel time across a road segment.

    Formula:
        t0 = L / vf

    Args:
        length_km: Road segment length in kilometers (L >= 0).
        free_flow_speed_kmh: Uncongested travel speed in km/h (vf > 0).
        unit: Output time unit: 'hours', 'minutes', or 'seconds'. Default 'minutes'.

    Returns:
        Free-flow travel time in the specified unit.

    Raises:
        ValueError: If length_km < 0, free_flow_speed_kmh <= 0, or invalid unit.
    """
    if length_km < 0.0:
        raise ValueError(f"Road length cannot be negative: {length_km} km")
    if free_flow_speed_kmh <= 0.0:
        raise ValueError(f"Free-flow speed must be strictly positive: {free_flow_speed_kmh} km/h")

    time_hours = length_km / free_flow_speed_kmh

    valid_units = {"hours": 1.0, "minutes": 60.0, "seconds": 3600.0}
    unit_norm = unit.lower().strip()
    if unit_norm not in valid_units:
        raise ValueError(f"Invalid time unit '{unit}'. Allowed units: {list(valid_units.keys())}")

    return time_hours * valid_units[unit_norm]


def vc_ratio(
    volume: float,
    capacity: float,
) -> float:
    """Calculate the Volume-to-Capacity (V/C) ratio.

    Formula:
        V/C = V / C

    Args:
        volume: Traffic volume (flow demand in vehicles per time window). Volume >= 0.
        capacity: Maximum sustainable road throughput (capacity >= 0).

    Returns:
        V/C ratio as a float. Returns float('inf') if capacity == 0 and volume > 0,
        or 0.0 if volume == 0.

    Raises:
        ValueError: If volume < 0 or capacity < 0.
    """
    if volume < 0.0:
        raise ValueError(f"Traffic volume cannot be negative: {volume}")
    if capacity < 0.0:
        raise ValueError(f"Road capacity cannot be negative: {capacity}")

    if capacity == 0.0:
        return float("inf") if volume > 0.0 else 0.0

    return volume / capacity


def bpr_travel_time(
    t0: float,
    vc: float,
    alpha: float = 0.15,
    beta: float = 4.0,
    max_travel_time: Optional[float] = None,
) -> float:
    """Calculate congested travel time using the Bureau of Public Roads (BPR) function.

    Formula:
        t = t0 * [1 + alpha * (V/C)^beta]

    Args:
        t0: Free-flow travel time (t0 >= 0).
        vc: Volume/capacity ratio (vc >= 0).
        alpha: BPR calibration parameter scaling congestion onset. Default 0.15.
        beta: BPR calibration power controlling congestion severity. Default 4.0.
        max_travel_time: Optional upper bound threshold for saturated conditions.

    Returns:
        Predicted congested travel time. Returns float('inf') if vc is infinite.

    Raises:
        ValueError: If t0 < 0, vc < 0, alpha < 0, or beta < 0.
    """
    if t0 < 0.0:
        raise ValueError(f"Free-flow time cannot be negative: {t0}")
    if vc < 0.0:
        raise ValueError(f"Volume/capacity ratio cannot be negative: {vc}")
    if alpha < 0.0:
        raise ValueError(f"Alpha parameter cannot be negative: {alpha}")
    if beta < 0.0:
        raise ValueError(f"Beta parameter cannot be negative: {beta}")

    if t0 == 0.0:
        return 0.0

    if math.isinf(vc):
        return float("inf")

    t = t0 * (1.0 + alpha * (vc**beta))

    if max_travel_time is not None and t > max_travel_time:
        return max_travel_time

    return t


def delay_per_vehicle(
    travel_time: float,
    free_flow_time: float,
) -> float:
    """Calculate traffic delay experienced per vehicle.

    Formula:
        D = max(0, t - t0)

    Args:
        travel_time: Actual or predicted travel time (t >= 0).
        free_flow_time: Free-flow travel time (t0 >= 0).

    Returns:
        Delay per vehicle in the same time units as the inputs.
        Returns float('inf') if travel_time is infinite.

    Raises:
        ValueError: If travel_time < 0 or free_flow_time < 0.
    """
    if travel_time < 0.0:
        raise ValueError(f"Travel time cannot be negative: {travel_time}")
    if free_flow_time < 0.0:
        raise ValueError(f"Free-flow time cannot be negative: {free_flow_time}")

    if math.isinf(travel_time):
        return float("inf")

    return max(0.0, travel_time - free_flow_time)


def total_delay(
    volume: float,
    travel_time: float,
    free_flow_time: float,
) -> float:
    """Calculate aggregate delay across all vehicles traversing the segment.

    Formula:
        D_total = V * max(0, t - t0)

    Args:
        volume: Number of vehicles traversing or attempting to traverse (volume >= 0).
        travel_time: Actual or predicted travel time (t >= 0).
        free_flow_time: Free-flow travel time (t0 >= 0).

    Returns:
        Aggregate vehicle-time of delay (e.g. vehicle-minutes or vehicle-hours).
        Returns float('inf') if travel_time is infinite and volume > 0, or 0.0 if volume == 0.

    Raises:
        ValueError: If volume < 0, travel_time < 0, or free_flow_time < 0.
    """
    if volume < 0.0:
        raise ValueError(f"Traffic volume cannot be negative: {volume}")

    if volume == 0.0:
        return 0.0

    d_per_veh = delay_per_vehicle(travel_time, free_flow_time)
    if math.isinf(d_per_veh):
        return float("inf")

    return volume * d_per_veh


def delay(
    travel_time: float,
    free_flow_time: float,
    volume: Optional[float] = None,
) -> Union[float, Tuple[float, float]]:
    """Calculate traffic delay with optional total aggregate delay.

    Convenience wrapper supporting both single-vehicle and aggregate queries.

    Args:
        travel_time: Actual or predicted travel time.
        free_flow_time: Free-flow travel time.
        volume: Optional volume. If provided, returns (per_vehicle_delay, total_delay).
                If None, returns per_vehicle_delay only.

    Returns:
        per_vehicle_delay if volume is None, else (per_vehicle_delay, total_delay).
    """
    d_veh = delay_per_vehicle(travel_time, free_flow_time)
    if volume is None:
        return d_veh

    d_tot = total_delay(volume, travel_time, free_flow_time)
    return d_veh, d_tot


def reduced_capacity(
    nominal_capacity: float,
    reduction_ratio: float,
) -> float:
    """Calculate disrupted road capacity under physical reduction or restriction.

    Formula:
        C_new = C * (1 - r)

    Args:
        nominal_capacity: Baseline designed road capacity (C >= 0).
        reduction_ratio: Fraction of capacity lost, r in [0.0, 1.0].
            0.10 -> 10% reduction
            0.25 -> 25% reduction
            0.50 -> 50% reduction
            1.00 -> complete road closure

    Returns:
        Remaining road capacity (C_new >= 0). Exactly 0.0 if reduction_ratio == 1.0.

    Raises:
        ValueError: If nominal_capacity < 0 or reduction_ratio not in [0.0, 1.0].
    """
    if nominal_capacity < 0.0:
        raise ValueError(f"Nominal capacity cannot be negative: {nominal_capacity}")
    if not (0.0 <= reduction_ratio <= 1.0):
        raise ValueError(
            f"Reduction ratio must be between 0.0 and 1.0 inclusive: got {reduction_ratio}"
        )

    if reduction_ratio == 1.0:
        return 0.0

    return nominal_capacity * (1.0 - reduction_ratio)


def peak_hourly_volume(
    daily_volume: float,
    k_factor: float = 0.10,
) -> float:
    """Convert daily aggregate traffic volume to peak hourly volume demand.

    Based on the standard transportation engineering K-factor (proportion of
    Average Annual Daily Traffic occurring during the peak hour, typically 8%-12%).

    Formula:
        V_peak = V_daily * K

    Args:
        daily_volume: Total daily vehicular count (>= 0).
        k_factor: Proportion of daily traffic in the peak hour (0.0 < k_factor <= 1.0).
            Default is 0.10 (10% peak hour concentration).

    Returns:
        Peak hourly volume demand.

    Raises:
        ValueError: If daily_volume < 0 or k_factor not in (0.0, 1.0].
    """
    if daily_volume < 0.0:
        raise ValueError(f"Daily volume cannot be negative: {daily_volume}")
    if not (0.0 < k_factor <= 1.0):
        raise ValueError(f"K-factor must be in range (0.0, 1.0]: got {k_factor}")

    return daily_volume * k_factor


def evaluate_road_condition(
    length_km: float,
    free_flow_speed_kmh: float,
    nominal_capacity: float,
    volume: float,
    capacity_reduction_ratio: float = 0.0,
    alpha: float = 0.15,
    beta: float = 4.0,
    unit: str = "minutes",
    max_travel_time: Optional[float] = None,
) -> RoadConditionResult:
    """Evaluate full traffic flow, congestion, and delay metrics for a road segment.

    Orchestrates:
        1. Free-flow time (t0)
        2. Disrupted capacity (C_new)
        3. Volume/capacity ratio (V/C)
        4. BPR congested travel time (t)
        5. Per-vehicle delay (D)
        6. Total vehicle delay (D_total)

    Args:
        length_km: Segment length in kilometers.
        free_flow_speed_kmh: Speed under free-flow conditions in km/h.
        nominal_capacity: Undisrupted capacity (veh/time).
        volume: Traffic volume demand (veh/time).
        capacity_reduction_ratio: Fraction of capacity removed (0.0 to 1.0).
        alpha: BPR alpha parameter (default 0.15).
        beta: BPR beta parameter (default 4.0).
        unit: Time unit ('minutes', 'hours', 'seconds').
        max_travel_time: Optional ceiling on travel time.

    Returns:
        RoadConditionResult containing all calculated variables and closure flag.
    """
    t0 = free_flow_time(length_km, free_flow_speed_kmh, unit=unit)
    eff_cap = reduced_capacity(nominal_capacity, capacity_reduction_ratio)
    vc = vc_ratio(volume, eff_cap)
    t = bpr_travel_time(t0, vc, alpha=alpha, beta=beta, max_travel_time=max_travel_time)
    d_veh = delay_per_vehicle(t, t0)
    d_tot = total_delay(volume, t, t0)
    is_closed = capacity_reduction_ratio >= 1.0 or eff_cap == 0.0

    return RoadConditionResult(
        length_km=length_km,
        free_flow_speed_kmh=free_flow_speed_kmh,
        nominal_capacity=nominal_capacity,
        capacity_reduction_ratio=capacity_reduction_ratio,
        effective_capacity=eff_cap,
        volume=volume,
        vc_ratio=vc,
        free_flow_time=t0,
        travel_time=t,
        delay_per_vehicle=d_veh,
        total_delay=d_tot,
        is_closed=is_closed,
        unit=unit,
    )

