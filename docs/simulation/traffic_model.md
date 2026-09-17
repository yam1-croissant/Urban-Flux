# UrbanFlux — Traffic Flow & Delay Model Specification

## 1. Domain Overview & Problem Statement

UrbanFlux models link-level traffic impedance, congestion delay, and physical disruption consequences on urban road networks. The primary question addressed by this model is:

> **Given a road link's length ($L$), free-flow speed ($v_f$), nominal capacity ($C$), and hourly vehicular flow ($V$), how do we calculate travel time ($t$), volume-to-capacity saturation ($V/C$), congestion delay ($d$), and network delay ($D_{\\text{total}}$)?**

---

## 2. Core Mathematical Formulations

### 2.1 Free-Flow Travel Time ($t_0$)
The unimpeded travel time required to traverse a road link in the absence of conflicting traffic:

$$t_0 = \\frac{L}{v_f}$$

- **$L$**: Link length in kilometres (km, $L \ge 0.0$).
- **$v_f$**: Free-flow design/speed limit in kilometres per hour (km/h, $v_f > 0.0$).
- **$t_0$**: Free-flow travel time in hours (h).

### 2.2 Volume-to-Capacity Ratio ($V/C$)
Measures the demand pressure relative to available physical throughput:

$$\\frac{V}{C} = \\frac{V}{C}$$

- **$V$**: Hourly vehicular flow rate (veh/h, $V \ge 0.0$).
- **$C$**: Available effective capacity (veh/h, $C > 0.0$).
- **Design Rule**: $V/C > 1.0$ indicates oversaturated conditions. Values are **not clamped to 1.0** to preserve visibility of extreme demand overload.

### 2.3 Bureau of Public Roads (BPR) Congestion Function
Relates congested travel time to link saturation via a non-linear power function:

$$t = t_0 \\cdot \\left[1 + \\alpha \\cdot \\left(\\frac{V}{C}\\right)^\\beta\\right]$$

- **$t$**: Congested travel time in hours (h).
- **$t_0$**: Free-flow travel time in hours (h).
- **$\\alpha$**: Ratio parameter controlling the onset of congestion delay (dimensionless, standard default: $\\alpha = 0.15$).
- **$\\beta$**: Exponent parameter governing the steepness of delay escalation beyond capacity (dimensionless, standard default: $\\beta = 4.0$).

### 2.4 Delay Formulations

#### Delay per Vehicle ($d$)
$$d = \\max(0, t - t_0) \\quad (\\text{hours/vehicle})$$

#### Aggregate Link Delay ($D_{\\text{total}}$)
Accumulated lost vehicle-hours across all traversing vehicles over the hourly analysis window:

$$D_{\\text{total}} = V \\cdot d = V \\cdot \\max(0, t - t_0) \\quad (\\text{vehicle-hours})$$

### 2.5 Capacity Reduction under Disruption
Physical incidents, waterlogging, or construction reduce effective capacity by a fraction $r$:

$$C_{\\text{new}} = C \\cdot (1 - r)$$

- **$r = 0.00$**: Baseline open operation ($100\\%$ capacity).
- **$r = 0.25$**: Single lane obstruction on a 4-lane road ($75\\%$ capacity).
- **$r = 0.50$**: Major flooding / partial closure ($50\\%$ capacity).
- **$r = 1.00$**: Complete physical closure ($0\\%$ capacity, link excluded from routing).

---

## 3. Dimensional Units & Validation Contract

| Variable | Symbol | Dimensional Unit | Validation Rule |
|---|---|---|---|
| Link Length | $L$ | Kilometres (km) | $L \ge 0.0$ |
| Free-Flow Speed | $v_f$ | Kilometres per hour (km/h) | $v_f > 0.0$ |
| Nominal Capacity | $C$ | Vehicles per hour (veh/h) | $C > 0.0$ |
| Hourly Traffic Flow | $V$ | Vehicles per hour (veh/h) | $V \ge 0.0$ |
| Reduction Fraction | $r$ | Dimensionless fraction | $0.0 \le r \le 1.0$ |
| Congested Travel Time | $t$ | Hours (h) | $t \ge 0.0$ |
| Delay per Vehicle | $d$ | Hours per vehicle (h) | $d \ge 0.0$ |
| Total Delay | $D_{\\text{total}}$ | Vehicle-hours (veh-h) | $D_{\\text{total}} \ge 0.0$ |

---

## 4. Step-by-Step Worked Example

### Given Input:
- Corridor: Silk Board Junction Approach ($L = 3.5\\text{ km}$)
- Free-Flow Speed: $v_f = 50.0\\text{ km/h}$
- Nominal Capacity: $C = 3,000\\text{ veh/h}$
- Peak Hourly Flow: $V = 2,400\\text{ veh/h}$
- Disruption: $25\\%$ capacity loss due to waterlogging ($r = 0.25$)
- BPR Parameters: $\\alpha = 0.15, \\beta = 4.0$

### Step-by-Step Calculations:
1. **Free-Flow Travel Time ($t_0$)**:
   $$t_0 = \\frac{3.5}{50.0} = 0.0700\\text{ hours} = 4.20\\text{ minutes}$$

2. **Effective Capacity ($C_{\\text{eff}}$)**:
   $$C_{\\text{eff}} = 3000 \\cdot (1 - 0.25) = 2,250\\text{ veh/h}$$

3. **Volume-to-Capacity Ratio ($V/C$)**:
   $$\\frac{V}{C} = \\frac{2400}{2250} = 1.0667 \\quad (\\text{Oversaturated by } 6.7\\%)$$

4. **Congested Travel Time ($t$)**:
   $$t = 0.0700 \\cdot \\left[1 + 0.15 \\cdot (1.0667)^4\\right] = 0.0700 \\cdot [1 + 0.15 \\cdot 1.2949] = 0.0700 \\cdot 1.1942 = 0.0836\\text{ hours} = 5.02\\text{ minutes}$$

5. **Delay per Vehicle ($d$)**:
   $$d = 5.02 - 4.20 = 0.82\\text{ minutes/veh} = 0.0136\\text{ hours/veh}$$

6. **Total Hourly Lost Time ($D_{\\text{total}}$)**:
   $$D_{\\text{total}} = 2400 \\cdot 0.0136 = 32.7\\text{ vehicle-hours of lost time per hour}$$

---

## 5. Model Limitations & Boundaries

1. **Macroscopic Steady-State**: BPR assumes steady-state demand over an analysis window. It does not model microscopic vehicle-vehicle car-following or intersection signal phase cycles.
2. **Homogeneous Flow Assumption**: In the MVP, vehicles are expressed in total hourly counts. Future extensions will incorporate Passenger Car Units (PCU) for Indian heterogeneous traffic (2W, 3W, buses).
3. **No Spatial Queue Spillback**: Point capacity reductions increase link impedance; full network queue spillback across upstream junctions requires graph-level routing assignment (implemented in Part B).
