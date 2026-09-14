# UrbanFlux — Traffic Mathematics Model Specification

## 1. Executive Summary & Purpose

UrbanFlux simulates the cascading societal and infrastructure consequences of urban road disruptions (e.g., severe waterlogging, construction lane blockages, bridge structural closures, or traffic incidents).

The **Traffic Mathematics Model** (`src/simulation/traffic_math.py`) establishes the deterministic mathematical foundation for link-level traffic impedance, congestion delay, and capacity degradation. Downstream components (routing graph evaluators, emergency service response simulators, and cascading impact engines) build upon this module to evaluate how network disruptions alter travel times and spill over into essential city services.

---

## 2. Mathematical Formulations

The model uses standard, well-established traffic-flow formulations from transportation engineering.

### 2.1 Free-Flow Travel Time (t0)
The unimpeded travel time required to traverse a road link in the absence of conflicting traffic:

211179t_0 = \frac{L}{v_f}211179

- **L**: Link length in kilometres (km, \(L \ge 0\)).
- **vf**: Free-flow speed in kilometres per hour (km/h, \(v_f > 0\)).
- **t0**: Free-flow travel time in hours (h).

### 2.2 Volume-to-Capacity Ratio (V/C)
The degree of traffic saturation on a road link:

211179\frac{V}{C} = \frac{V}{C}211179

- **V**: Traffic demand volume in flow units per time period (e.g., veh/h, \(V \ge 0\)).
- **C**: Available link capacity in the same flow units per time period (veh/h, \(C > 0\)).
- **Design Rule**: V/C values exceeding 1.0 represent oversaturated conditions. Values are intentionally **not clamped at 1.0**, ensuring that severe demand overloads remain transparent to routing and impact algorithms.

### 2.3 Bureau of Public Roads (BPR) Congestion Function
Estimates congested link travel time as a non-linear power function of volume-to-capacity saturation:

211179t = t_0 \cdot \left[1 + \alpha \cdot \left(\frac{V}{C}\right)^\beta\right]211179

- **t**: Congested travel time in hours (h).
- **t0**: Free-flow travel time in hours (h).
- **alpha**: Ratio parameter controlling the onset of congestion delay (dimensionless, \(lpha \ge 0\); standard default: 0.15).
- **beta**: Exponent parameter governing the steepness of delay escalation beyond capacity (dimensionless, \(eta \ge 0\); standard default: 4.0).

### 2.4 Delay Formulations
Delay measures the excess travel time incurred due to traffic friction relative to free-flow conditions:

#### Delay per Vehicle (d)
211179d = \max(0, t - t_0)211179
- Expressed in hours per vehicle (h/veh).

#### Aggregate Link Delay (D_total)
Accumulated lost person/vehicle time across all traversing vehicles over the analysis period:

211179D_{\text{total}} = V \cdot d = V \cdot \max(0, t - t_0)211179
- Expressed in vehicle-hours (veh-h).

### 2.5 Capacity Reduction under Disruption
Physical incidents, lane blockages, construction, or weather hazards reduce available link capacity by a fraction r:

211179C_{\text{new}} = C \cdot (1 - r)211179

- **C**: Nominal baseline capacity (veh/period, \(C \ge 0\)).
- **r**: Capacity reduction fraction (\(r \in [0.0, 1.0]\)).
  - \(r = 0.00\): Normal baseline operation.
  - \(r = 0.10\): Minor disruption (shoulder obstruction, moderate rainfall).
  - \(r = 0.25\): Moderate disruption (1 lane closed on a 4-lane arterial).
  - \(r = 0.50\): Severe disruption (carriageway flooding, treefall, major construction).
  - \(r = 1.00\): Complete link closure (structural failure, total barrier, bridge out).

---

## 3. Dimensional Units & Model Contract

All public functions adhere to a strict unit contract:

| Variable | Symbol | Dimension / Unit | Permissible Range |
|---|---|---|---|
| Link Length | L | Kilometres (km) | \([0, \infty)\) |
| Free-Flow Speed | vf | Kilometres per hour (km/h) | \((0, \infty)\) |
| Free-Flow Travel Time | t0 | Hours (h) | \([0, \infty)\) |
| Traffic Volume | V | Vehicles per period (veh/period) | \([0, \infty)\) |
| Capacity | C | Vehicles per period (veh/period) | \((0, \infty)\) (or \([0, \infty)\) for closures) |
| Reduction Fraction | r | Dimensionless fraction | \([0.0, 1.0]\) |
| Congested Travel Time | t | Hours (h) | \([0, \infty)\) |
| Delay per Vehicle | d | Hours per vehicle (h) | \([0, \infty)\) |
| Aggregate Delay | D_total | Vehicle-hours (veh-h) | \([0, \infty)\) |
| BPR Alpha | alpha | Dimensionless coefficient | \([0, \infty)\) (default: 0.15) |
| BPR Beta | beta | Dimensionless power | \([0, \infty)\) (default: 4.0) |

---

## 4. Closure Semantics & Boundary Safety

A primary failure mode in naive traffic models is dividing by zero when a road is completely closed (\(C = 0\)). UrbanFlux enforces strict mathematical and computational boundaries:

1. **Explicit Zero-Capacity Error**:
   Calling `vc_ratio(volume, capacity=0)` or `bpr_travel_time(t0, volume, capacity=0)` raises `RoadClosedError` (a subclass of `TrafficMathError` and `ValueError`).
2. **Deterministic Evaluation Structure**:
   The composite helper `evaluate_link_disruption(..., reduction_fraction=1.0)` safely identifies complete closures, returning `is_closed=True`, `effective_capacity=0.0`, and `travel_time_hours=None`.
3. **Downstream Routing Handling**:
   Network routing engines encountering `is_closed=True` or catching `RoadClosedError` must assign infinite edge weight (impassable) and compute alternate detours rather than processing invalid numerical travel times.

---

## 5. Python API Reference

Import path:
```python
from src.simulation.traffic_math import (
    free_flow_time,
    vc_ratio,
    bpr_travel_time,
    delay,
    delay_per_vehicle,
    total_delay,
    reduced_capacity,
    evaluate_link_disruption,
    LinkImpactResult,
    TrafficMathError,
    InvalidInputError,
    RoadClosedError,
)
```

### Function Signatures & Behaviors

#### `free_flow_time(length_km: float, free_flow_speed_kmph: float) -> float`
Calculates \(t_0 = L / v_f\) in hours.
- Raises `InvalidInputError` if \(L < 0\) or \(v_f \le 0\).

#### `vc_ratio(volume: float, capacity: float) -> float`
Calculates \(V / C\).
- Raises `RoadClosedError` if \(C == 0\).
- Raises `InvalidInputError` if \(V < 0\) or \(C < 0\).

#### `bpr_travel_time(free_flow_time_hours: float, volume: float, capacity: float, alpha: float = 0.15, beta: float = 4.0) -> float`
Calculates congested travel time \(t\) in hours using the BPR formula.
- Fully configurable `alpha` and `beta`.
- Raises `RoadClosedError` if \(C == 0\).
- Raises `InvalidInputError` if any parameter is negative.

#### `delay_per_vehicle(travel_time_hours: float, free_flow_time_hours: float) -> float`
Calculates \(\max(0, t - t_0)\) in hours.

#### `total_delay(travel_time_hours: float, free_flow_time_hours: float, volume: float) -> float`
Calculates \(V \cdot \max(0, t - t_0)\) in vehicle-hours.

#### `delay(travel_time_hours: float, free_flow_time_hours: float, volume: Optional[float] = None) -> float`
Unified delay function. Returns per-vehicle delay in hours if `volume is None`, or total delay in vehicle-hours if `volume` is provided.

#### `reduced_capacity(capacity: float, reduction_fraction: float) -> float`
Calculates \(C \cdot (1 - r)\).
- Raises `InvalidInputError` if \(C < 0\) or \(r 
otin [0.0, 1.0]\).

#### `evaluate_link_disruption(...) -> LinkImpactResult`
High-level evaluator returning a frozen dataclass with complete metrics, minute conversions, and closure detection.

---

## 6. Code Example

```python
from src.simulation.traffic_math import evaluate_link_disruption

# Evaluate a 4.5 km corridor under a 50% capacity reduction
result = evaluate_link_disruption(
    length_km=4.5,
    free_flow_speed_kmph=50.0,
    volume=2400.0,
    nominal_capacity=3000.0,
    reduction_fraction=0.50,
)

print(f"Effective Capacity : {result.effective_capacity:.0f} veh/h")
print(f"V/C Ratio          : {result.vc_ratio:.2f}")
print(f"Free-Flow Time     : {result.free_flow_time_minutes:.2f} mins")
print(f"Travel Time        : {result.travel_time_minutes:.2f} mins")
print(f"Delay per Vehicle  : {result.delay_per_vehicle_minutes:.2f} mins")
print(f"Total Lost Time    : {result.total_delay_veh_hours:.1f} vehicle-hours")
```

---

## 7. Model Scope & Limitations

1. **Macroscopic Steady-State**: BPR represents macroscopic, steady-state flow relationships over an analysis period. It does not model microscopic vehicle-vehicle interactions, shockwave propagation, or intersection signal queuing.
2. **Spatial Bottleneck Spillback**: Point capacity reductions increase link traversal time; spatial queue spillback across upstream links requires the full network simulation graph (Phase 2).
3. **Unit Consistency**: Callers must ensure that volume and capacity use identical time periods (e.g., both hourly rates or both daily totals).
