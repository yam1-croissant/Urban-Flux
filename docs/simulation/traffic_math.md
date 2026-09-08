# UrbanResilience — Traffic Mathematics Model Documentation

## 1. Overview & Purpose

The **UrbanResilience Traffic Mathematics Model** provides the link-level foundation for simulating traffic flow, congestion dynamics, and travel-time delays under normal and degraded infrastructure states. 

Later stages of UrbanResilience (Agent 2: Network Routing / APIs and Agent 3: Geospatial Visualization) require a mathematically defensible, fast, and transparent mechanism to evaluate questions such as:
> *"If a major corridor like Marathahalli Bridge or Silk Board Junction loses 50% of its physical capacity due to flooding or roadworks, how much does link travel time increase, and what is the resulting network delay?"*

This module implements classical, empirically grounded traffic-flow relationships parameterized for urban Bangalore conditions.

---

## 2. Core Equations

### 2.1 Free-Flow Travel Time ($t_0$)
Free-flow travel time is the time required to traverse an uncongested road segment at the legal or operational free-flow speed:

$$t_0 = \frac{L}{v_f}$$

Where:
- $L$: Road segment length (kilometers, $\text{km}$)
- $v_f$: Free-flow speed (kilometers per hour, $\text{km/h}$)
- $t_0$: Free-flow travel time (hours or minutes)

### 2.2 Volume-to-Capacity Ratio ($V/C$)
The Volume-to-Capacity ratio measures traffic demand relative to the maximum sustainable throughput of the facility:

$$\frac{V}{C} = \frac{V}{C}$$

Where:
- $V$: Hourly or periodic traffic volume demand ($\text{veh/h}$)
- $C$: Road segment operational capacity ($\text{veh/h}$)

Edge cases:
- If $C = 0$ and $V > 0$ (complete road closure), $V/C \to \infty$.
- If $V = 0$, $V/C = 0.0$.

### 2.3 Congested Travel Time: BPR Formulation ($t$)
We adopt the classic Bureau of Public Roads (BPR) volume-delay function, the standard benchmark in transportation planning and traffic equilibrium modeling:

$$t = t_0 \left[1 + \alpha \left(\frac{V}{C}\right)^\beta\right]$$

Where:
- $t_0$: Free-flow travel time
- $V/C$: Volume-to-capacity ratio
- $\alpha$: Parameter determining delay onset when demand approaches capacity (default: $0.15$)
- $\beta$: Exponent governing the sharpness of the congestion penalty curve (default: $4.0$)

When $V \ll C$ (light traffic), $t \approx t_0$.  
When $V = C$ (at capacity), $t = t_0 (1 + \alpha) = 1.15 \cdot t_0$.  
When $V > C$ (oversaturated conditions), travel time increases sharply according to power $\beta$.

### 2.4 Traffic Delay ($D$ and $D_{total}$)
Delay isolates the excess time spent traversing the road beyond free-flow conditions:

- **Per-Vehicle Delay ($D$)**:
  $$D = \max(0, t - t_0)$$
- **Total Aggregate Corridor Delay ($D_{total}$)**:
  $$D_{total} = V \cdot D = V \cdot \max(0, t - t_0)$$

Units:
- $D$: Minutes per vehicle
- $D_{total}$: Vehicle-minutes (or vehicle-hours) across the corridor

### 2.5 Capacity Reduction & Disruption ($C_{new}$)
Infrastructure failure, waterlogging, accidents, or construction reduce effective throughput:

$$C_{new} = C \cdot (1 - r)$$

Where $r \in [0.0, 1.0]$ is the capacity loss ratio:
- $r = 0.00 \implies$ Normal operation ($C_{new} = C$)
- $r = 0.10 \implies 10\%$ capacity reduction
- $r = 0.25 \implies 25\%$ capacity reduction
- $r = 0.50 \implies 50\%$ capacity reduction
- $r = 1.00 \implies$ **Complete road closure** ($C_{new} = 0.0$)

---

## 3. Road Closure Behavior & Routing Integration

When $r = 1.00$:
1. $C_{new} = 0.0$
2. $V/C \to \infty$
3. $t \to \infty$
4. `is_closed = True`

In Dijkstra/A* routing engines (Agent 2), impassable closed links should either have edge weight set to `float('inf')` or be filtered out of the active traversal graph, preventing vehicles from traversing closed road links.

---

## 4. Parameter Choices & Calibration

| Parameter | Standard Value | Bangalore Urban Calibration | Rationale |
|---|---|---|---|
| BPR $\alpha$ | $0.15$ | $0.15 - 0.25$ | Captures the onset of delay as volume reaches 85%-100% capacity |
| BPR $\beta$ | $4.0$ | $3.5 - 4.0$ | Controls the non-linear inflection slope during peak gridlock |
| Free-flow speed ($v_f$) | $60 \text{ km/h}$ | $45 - 55 \text{ km/h}$ | Corresponds to Bangalore arterial speed limits and unhindered off-peak travel speeds |
| Peak Hour Factor ($K$) | $0.10$ | $0.09 - 0.12$ | Ratio of peak-hour vehicular volume to 24-hour total (IRC guidelines) |
| Nominal Lane Capacity | $1,800 \text{ veh/h/lane}$ | $1,200 - 1,500 \text{ PCU/h/lane}$ | Adjusted for mixed Indian traffic composition (2W/3W/buses) |

---

## 5. API Reference & Code Usage

The functions are located in `src/simulation/traffic_math.py` and are designed to be imported cleanly:

```python
from src.simulation.traffic_math import (
    free_flow_time,
    vc_ratio,
    bpr_travel_time,
    delay_per_vehicle,
    total_delay,
    reduced_capacity,
    evaluate_road_condition,
)

# 1. Compute free-flow travel time (e.g. 2.5 km at 50 km/h)
t0 = free_flow_time(length_km=2.5, free_flow_speed_kmh=50.0, unit="minutes")
# t0 = 3.0 minutes

# 2. Simulate 50% capacity loss on a road with 2,500 veh/h baseline capacity
c_disrupted = reduced_capacity(nominal_capacity=2500.0, reduction_ratio=0.50)
# c_disrupted = 1250.0 veh/h

# 3. Compute V/C under 2,300 veh/h peak demand
vc = vc_ratio(volume=2300.0, capacity=c_disrupted)
# vc = 1.84

# 4. Compute congested travel time
t_congested = bpr_travel_time(t0=t0, vc=vc, alpha=0.15, beta=4.0)
# t_congested = 8.16 minutes (up from 3.0 min)

# 5. Compute delay
d_veh = delay_per_vehicle(travel_time=t_congested, free_flow_time=t0)
d_tot = total_delay(volume=2300.0, travel_time=t_congested, free_flow_time=t0)
# d_veh = 5.16 min/vehicle, d_tot = 11,863 vehicle-minutes

# 6. High-level single call helper
result = evaluate_road_condition(
    length_km=2.5,
    free_flow_speed_kmh=50.0,
    nominal_capacity=2500.0,
    volume=2300.0,
    capacity_reduction_ratio=0.50,
)
print(f"V/C: {result.vc_ratio:.2f}, Travel Time: {result.travel_time:.2f} min")
```

---

## 6. Limitations & Boundaries

1. **Static Flow Representation**: BPR calculates travel times based on steady-state demand rates within a discrete time window (e.g., peak hour). It does not model individual vehicle physics or microscopic queue spillback.
2. **Homogeneous Flow**: Inputs represent equivalent Passenger Car Units (PCU) or counts. Explicit mixed-traffic breakdowns (e.g., 2-wheelers weaving through congested corridors) require applying PCU equivalence factors prior to feeding volume into `vc_ratio`.
3. **No Downstream Queue Spillback**: Overcapacity ($V/C > 1.0$) produces large travel times on the link itself, but does not autonomously block upstream links unless coupled with network-wide balance equations.

