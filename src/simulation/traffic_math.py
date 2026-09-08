"""UrbanResilience — Part A: Traffic Mathematics Foundation.

This module provides standard, deterministic mathematical models for traffic-flow
relationships and disruption analysis:
1. Free-flow travel time (L / vf)
2. Volume-to-capacity ratio (V / C)
3. Bureau of Public Roads (BPR) congestion travel-time function
4. Delay per vehicle and aggregate delay
5. Capacity reduction under physical or operational disruptions

Contract & Units:
- Length: kilometres (km)
- Speed: kilometres per hour (km/h)
- Travel times & Delays: hours (h)
- Flow / Volume: vehicles per time period (e.g. veh/h or veh/day)
- Capacity: vehicles per time period (must match volume unit)
- Capacity reduction fraction: float in [0.0, 1.0]

All functions are stateless, fully typed, and defensively validate inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union


# =====================================================================
# Custom Exceptions
# =====================================================================

class TrafficMathError(ValueError):
    """Base exception for all traffic mathematics errors."""
    pass


class InvalidInputError(TrafficMathError):
    """Raised when an input parameter fails domain validation."""
    pass


class RoadClosedError(TrafficMathError):
    """Raised when calculating travel time or V/C on a completely closed road (capacity <= 0)."""
    pass


# =====================================================================
# Core Mathematical Functions
# =====================================================================

def free_flow_time(length_km: float, free_flow_speed_kmph: float) -> float:
    """Calculate free-flow travel time across a road link.

    Equation:
        t_0 = L / v_f

    Args:
        length_km: Road link length in kilometres (must be non-negative).
        free_flow_speed_kmph: Free-flow speed in km/h (must be strictly positive).

    Returns:
        Free-flow travel time in hours. If length is 0.0, returns 0.0.

    Raises:
        InvalidInputError: If length_km < 0 or free_flow_speed_kmph <= 0.
    """
    if length_km < 0.0:
        raise InvalidInputError(
            f"Road link length cannot be negative: received length_km={length_km}"
        )
    if free_flow_speed_kmph <= 0.0:
        raise InvalidInputError(
            f"Free-flow speed must be strictly positive: received free_flow_speed_kmph={free_flow_speed_kmph}"
        )
    return float(length_km / free_flow_speed_kmph)


def vc_ratio(volume: float, capacity: float) -> float:
    """Calculate the Volume-to-Capacity (V/C) ratio for a link.

    Equation:
        V/C = V / C

    Note:
        V/C values above 1.0 represent over-saturated (over-capacity) conditions.
        Values are intentionally not clamped to 1.0 to preserve overload visibility.

    Args:
        volume: Traffic volume in flow units per period (must be non-negative).
        capacity: Available capacity in the same flow units per period (must be strictly positive).

    Returns:
        Volume-to-capacity ratio (dimensionless float).

    Raises:
        InvalidInputError: If volume < 0.
        RoadClosedError: If capacity == 0 (road is closed/unavailable).
        InvalidInputError: If capacity < 0.
    """
    if volume < 0.0:
        raise InvalidInputError(
            f"Traffic volume cannot be negative: received volume={volume}"
        )
    if capacity == 0.0:
        raise RoadClosedError(
            "Cannot compute V/C ratio for a road with zero capacity (complete closure)."
        )
    if capacity < 0.0:
        raise InvalidInputError(
            f"Capacity cannot be negative: received capacity={capacity}"
        )
    return float(volume / capacity)


def bpr_travel_time(
    free_flow_time_hours: float,
    volume: float,
    capacity: float,
    alpha: float = 0.15,
    beta: float = 4.0,
) -> float:
    """Calculate congested link travel time using the Bureau of Public Roads (BPR) function.

    Equation:
        t = t_0 * [1 + alpha * (V / C)^beta]

    Args:
        free_flow_time_hours: Free-flow travel time (t_0) in hours (must be non-negative).
        volume: Traffic volume (V) in flow units per period (must be non-negative).
        capacity: Link capacity (C) in flow units per period (must be strictly positive).
        alpha: BPR alpha parameter, ratio coefficient (default: 0.15, must be non-negative).
        beta: BPR beta exponent, congestion power (default: 4.0, must be non-negative).

    Returns:
        Predicted travel time (t) in hours.

    Raises:
        InvalidInputError: If free_flow_time_hours < 0, volume < 0, alpha < 0, or beta < 0.
        RoadClosedError: If capacity == 0 (road is closed).
        InvalidInputError: If capacity < 0.
    """
    if free_flow_time_hours < 0.0:
        raise InvalidInputError(
            f"Free-flow travel time cannot be negative: received free_flow_time_hours={free_flow_time_hours}"
        )
    if alpha < 0.0:
        raise InvalidInputError(
            f"BPR parameter alpha cannot be negative: received alpha={alpha}"
        )
    if beta < 0.0:
        raise InvalidInputError(
            f"BPR parameter beta cannot be negative: received beta={beta}"
        )

    # Compute V/C (handles volume and capacity validation)
    vc = vc_ratio(volume=volume, capacity=capacity)

    return float(free_flow_time_hours * (1.0 + alpha * (vc ** beta)))


def delay_per_vehicle(
    travel_time_hours: float,
    free_flow_time_hours: float,
) -> float:
    """Calculate excess delay experienced per vehicle relative to free-flow conditions.

    Equation:
        d = max(0, t - t_0)

    Args:
        travel_time_hours: Congested travel time in hours (must be non-negative).
        free_flow_time_hours: Free-flow travel time in hours (must be non-negative).

    Returns:
        Delay per vehicle in hours (non-negative float).

    Raises:
        InvalidInputError: If travel_time_hours < 0 or free_flow_time_hours < 0.
    """
    if travel_time_hours < 0.0:
        raise InvalidInputError(
            f"Travel time cannot be negative: received travel_time_hours={travel_time_hours}"
        )
    if free_flow_time_hours < 0.0:
        raise InvalidInputError(
            f"Free-flow travel time cannot be negative: received free_flow_time_hours={free_flow_time_hours}"
        )
    return float(max(0.0, travel_time_hours - free_flow_time_hours))


def total_delay(
    travel_time_hours: float,
    free_flow_time_hours: float,
    volume: float,
) -> float:
    """Calculate aggregate delay accumulated across all vehicles during the time period.

    Equation:
        D_total = volume * max(0, t - t_0)

    Args:
        travel_time_hours: Congested travel time in hours (must be non-negative).
        free_flow_time_hours: Free-flow travel time in hours (must be non-negative).
        volume: Traffic volume over the analysis period (must be non-negative).

    Returns:
        Total aggregate delay in vehicle-hours (veh-h).

    Raises:
        InvalidInputError: If volume < 0, travel_time_hours < 0, or free_flow_time_hours < 0.
    """
    if volume < 0.0:
        raise InvalidInputError(
            f"Traffic volume cannot be negative: received volume={volume}"
        )
    d_per_veh = delay_per_vehicle(
        travel_time_hours=travel_time_hours,
        free_flow_time_hours=free_flow_time_hours,
    )
    return float(volume * d_per_veh)


def delay(
    travel_time_hours: float,
    free_flow_time_hours: float,
    volume: Optional[float] = None,
) -> float:
    """Calculate link delay. Returns per-vehicle delay or total delay depending on volume argument.

    Args:
        travel_time_hours: Congested travel time in hours.
        free_flow_time_hours: Free-flow travel time in hours.
        volume: Optional traffic volume. If None, returns delay per vehicle (hours).
            If provided, returns total aggregate delay (vehicle-hours).

    Returns:
        Delay in hours (if volume is None) or vehicle-hours (if volume is provided).

    Raises:
        InvalidInputError: If any parameter is negative.
    """
    if volume is None:
        return delay_per_vehicle(
            travel_time_hours=travel_time_hours,
            free_flow_time_hours=free_flow_time_hours,
        )
    return total_delay(
        travel_time_hours=travel_time_hours,
        free_flow_time_hours=free_flow_time_hours,
        volume=volume,
    )


def reduced_capacity(capacity: float, reduction_fraction: float) -> float:
    """Calculate residual road capacity following a physical or operational disruption.

    Equation:
        C_new = C * (1 - r)

    Args:
        capacity: Nominal baseline capacity (must be non-negative).
        reduction_fraction: Fraction of capacity lost (r), in range [0.0, 1.0].
            - 0.00: No reduction (100% capacity available)
            - 0.10: 10% reduction (e.g. minor shoulder blockage / rain)
            - 0.25: 25% reduction (e.g. one lane closed on 4-lane road)
            - 0.50: 50% reduction (e.g. half the lanes blocked)
            - 1.00: 100% reduction (complete road closure)

    Returns:
        Residual available capacity in the same units.

    Raises:
        InvalidInputError: If capacity < 0 or reduction_fraction is outside [0.0, 1.0].
    """
    if capacity < 0.0:
        raise InvalidInputError(
            f"Capacity cannot be negative: received capacity={capacity}"
        )
    if not (0.0 <= reduction_fraction <= 1.0):
        raise InvalidInputError(
            f"Capacity reduction fraction must be between 0.0 and 1.0 (inclusive): received reduction_fraction={reduction_fraction}"
        )
    return float(capacity * (1.0 - reduction_fraction))


# =====================================================================
# High-Level Evaluation Data Structure
# =====================================================================

@dataclass(frozen=True)
class LinkImpactResult:
    """Structured result for a road link evaluated under baseline or disrupted conditions."""

    length_km: float
    free_flow_speed_kmph: float
    free_flow_time_hours: float
    nominal_capacity: float
    reduction_fraction: float
    effective_capacity: float
    volume: float
    vc_ratio: Optional[float]
    travel_time_hours: Optional[float]
    delay_per_vehicle_hours: Optional[float]
    total_delay_veh_hours: Optional[float]
    is_closed: bool
    status_note: str

    @property
    def free_flow_time_minutes(self) -> float:
        """Free flow travel time in minutes."""
        return self.free_flow_time_hours * 60.0

    @property
    def travel_time_minutes(self) -> Optional[float]:
        """Congested travel time in minutes, or None if closed."""
        return (self.travel_time_hours * 60.0) if self.travel_time_hours is not None else None

    @property
    def delay_per_vehicle_minutes(self) -> Optional[float]:
        """Delay per vehicle in minutes, or None if closed."""
        return (self.delay_per_vehicle_hours * 60.0) if self.delay_per_vehicle_hours is not None else None


def evaluate_link_disruption(
    length_km: float,
    free_flow_speed_kmph: float,
    volume: float,
    nominal_capacity: float,
    reduction_fraction: float = 0.0,
    alpha: float = 0.15,
    beta: float = 4.0,
) -> LinkImpactResult:
    """Evaluate traffic conditions and delays on a road link under disruption.

    Handles both operational links and complete closures safely.

    Args:
        length_km: Road link length in km.
        free_flow_speed_kmph: Free-flow speed in km/h.
        volume: Traffic volume in veh/period.
        nominal_capacity: Undisrupted capacity in veh/period.
        reduction_fraction: Fraction of capacity lost in [0.0, 1.0].
        alpha: BPR alpha parameter.
        beta: BPR beta parameter.

    Returns:
        LinkImpactResult with complete baseline and disruption metrics.
    """
    t0 = free_flow_time(length_km=length_km, free_flow_speed_kmph=free_flow_speed_kmph)
    c_eff = reduced_capacity(capacity=nominal_capacity, reduction_fraction=reduction_fraction)

    if reduction_fraction >= 1.0 or c_eff == 0.0:
        return LinkImpactResult(
            length_km=length_km,
            free_flow_speed_kmph=free_flow_speed_kmph,
            free_flow_time_hours=t0,
            nominal_capacity=nominal_capacity,
            reduction_fraction=reduction_fraction,
            effective_capacity=0.0,
            volume=volume,
            vc_ratio=None,
            travel_time_hours=None,
            delay_per_vehicle_hours=None,
            total_delay_veh_hours=None,
            is_closed=True,
            status_note="Complete closure (infinite impedance / traffic must detour)",
        )

    vc = vc_ratio(volume=volume, capacity=c_eff)
    t = bpr_travel_time(
        free_flow_time_hours=t0,
        volume=volume,
        capacity=c_eff,
        alpha=alpha,
        beta=beta,
    )
    d_veh = delay_per_vehicle(travel_time_hours=t, free_flow_time_hours=t0)
    d_tot = total_delay(travel_time_hours=t, free_flow_time_hours=t0, volume=volume)

    status_note = "Normal" if vc <= 0.85 else ("Near Capacity" if vc <= 1.0 else "Oversaturated / Congested")

    return LinkImpactResult(
        length_km=length_km,
        free_flow_speed_kmph=free_flow_speed_kmph,
        free_flow_time_hours=t0,
        nominal_capacity=nominal_capacity,
        reduction_fraction=reduction_fraction,
        effective_capacity=c_eff,
        volume=volume,
        vc_ratio=vc,
        travel_time_hours=t,
        delay_per_vehicle_hours=d_veh,
        total_delay_veh_hours=d_tot,
        is_closed=False,
        status_note=status_note,
    )
