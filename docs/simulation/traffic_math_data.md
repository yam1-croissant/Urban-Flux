# UrbanResilience — Traffic Mathematics Data Specification

## 1. Dataset Overview

- **Source**: *Bangalore's Traffic Pulse* dataset (Kaggle: `preethamgouda/banglore-city-traffic-dataset`), referenced in transportation research literature on Bengaluru urban mobility (PMC12638989).
- **File**: `data/Banglore_traffic_Dataset.csv`
- **Total Records**: 3,082 observations
- **Temporal Coverage**: 2022-01-01 to 2022-11-22 (326 distinct calendar days)
- **Spatial Coverage**: 8 major Bengaluru zones across 16 major corridors and intersections:
  - **Indiranagar**: 100 Feet Road, CMH Road
  - **Whitefield**: Marathahalli Bridge, ITPL Main Road
  - **Koramangala**: Sony World Junction, Sarjapur Road
  - **M.G. Road**: Trinity Circle, Anil Kumble Circle
  - **Jayanagar**: Jayanagar 4th Block, South End Circle
  - **Hebbal**: Hebbal Flyover, Ballari Road
  - **Yeshwanthpur**: Yeshwanthpur Circle, Tumkur Road
  - **Electronic City**: Hosur Road, Silk Board Junction

---

## 2. Model Variable to Dataset Column Mapping

| Model Variable | Dataset Column | Direct / Derived / Assumed | Notes |
|---|---|---|---|
| **Traffic volume ($V$)** | `Traffic Volume` | Direct | Total vehicle count recorded for the observation period (daily aggregate: 4,537 to 71,610 vehicles). |
| **Average speed ($v_{avg}$)** | `Average Speed` | Direct | Observed speed in km/h (range: 20.0 to 89.8 km/h, mean: 39.4 km/h). |
| **Road / intersection** | `Road/Intersection Name` + `Area Name` | Direct | Corridor identifier and geographic locality within Bengaluru. |
| **Timestamp / date** | `Date` | Direct | Recorded at daily resolution (`DD-MM-YYYY`). |
| **Travel time ($t$)** | `Travel Time Index` | Derived | Raw dataset provides Travel Time Index ($\text{TTI} = t / t_0$, ranging from 1.0 to 1.5). Absolute travel time $t = t_0 \cdot \text{TTI}$ requires link length $L$. |
| **Congestion level** | `Congestion Level` | Direct | Empirical congestion index percentage ($0\%$ to $100\%$, mean: $81.1\%$). |
| **Capacity ($C$) / Utilization** | `Road Capacity Utilization` | Derived | Utilization recorded as percentage ($\le 100\%$). Baseline capacity $C \approx 20,000 \text{ veh/day}$ inferred from uncapped records. |
| **Peak period** | Derived / Assumed | Derived & Assumed | Sub-hourly timestamps are absent. Modeled via 90th percentile peak-volume days and standard transportation engineering Peak Hour Factor ($K \approx 0.10$). |
| **Road length ($L$)** | *None* | External / Assumed | Road segment physical length is not in the sensor volume dataset; to be supplied by OpenStreetMap / OSMnx in Phase B. |
| **Free-flow speed ($v_f$)** | Derived (`Average Speed` $\times$ `Travel Time Index`) | Derived / Assumed | Uncongested operational speed ($\sim 50\text{--}55 \text{ km/h}$) calculated from off-peak speed observations and TTI definition. |

---

## 3. Treatment of Missing Variables

In accordance with project principles, we do **not** invent or fake sensor data. Missing variables are explicitly categorized:

### 3.1 Road Segment Length ($L$)
- **Status**: Missing in sensor dataset.
- **Resolution Strategy**: Supplied by road-network dataset.
- **Implementation**: In Phase A unit models, $L$ is passed as an explicit function parameter (`length_km`). In Phase B, OSMnx will extract exact geospatial segment lengths from OpenStreetMap edges.

### 3.2 Sub-Hourly Timestamp (Hourly Resolution)
- **Status**: Missing in sensor dataset (dates are daily).
- **Resolution Strategy**: Estimated from defensible transportation engineering assumptions.
- **Implementation**: Standard Peak Hour Factor formulation:
  $$V_{\text{peak}} = V_{\text{daily}} \cdot K$$
  where $K \in [0.08, 0.12]$ (default $K = 0.10$, corresponding to Indian Roads Congress arterial traffic standards).

### 3.3 Explicit Lane Counts and Directionality
- **Status**: Missing in traffic pulse dataset.
- **Resolution Strategy**: Supplied by OpenStreetMap (OSM tags: `lanes=*`, `oneway=*`) in Phase B.

---

## 4. Empirical Peak-Demand & Day-of-Week Analysis

Analysis of the 3,082 records reveals distinct demand regimes across the 16 corridors:

### 4.1 Day-of-Week Variation
| Day | Mean Volume (veh/day) | Std Dev | Mean Speed (km/h) | Mean Congestion (%) |
|---|---|---|---|---|
| Monday | 29,566 | 13,140 | 39.2 | 81.6% |
| Tuesday | 29,367 | 12,486 | 40.1 | 81.6% |
| Wednesday | 29,967 | 13,102 | 38.9 | 81.9% |
| Thursday | 29,651 | 13,889 | 39.5 | 80.5% |
| Friday | 29,545 | 12,999 | 39.3 | 81.1% |
| Saturday | 28,791 | 13,305 | 40.2 | 79.7% |
| Sunday | 28,813 | 12,584 | 38.9 | 81.1% |

### 4.2 Corridor Demand Contrast: Heavy vs Moderate Demand
Corridors exhibit clear stratification in daily throughput:
- **High-Demand Arterials** (e.g. Sarjapur Road, Sony World Junction, 100 Feet Road):
  - Volumes reach **60,000 to 71,610 veh/day**.
  - Road capacity utilization consistently caps at 100%.
  - Peak hourly demand exceeds 2,500 veh/h.
- **Moderate Corridors** (e.g. Marathahalli Bridge, Hosur Road, Tumkur Road):
  - Off-peak volumes drop to **5,000 to 12,000 veh/day**.
  - Capacity utilization drops to 22%–40%, permitting free-flow speeds above 55 km/h.

---

## 5. Parameter Calibration Procedure

### 5.1 Baseline Capacity Estimation
When `Road Capacity Utilization` $< 100\%$, implied capacity is calculated as:
$$C_{\text{implied}} = \frac{V}{\text{Utilization} / 100}$$
Across all 790 uncapped observations in the dataset, the mean implied capacity is **$20,080 \text{ veh/day}$** ($\text{std} = 1,120$). When scaled to peak hour ($K = 0.10$), this yields an hourly single-direction arterial capacity of **$2,000 \text{--} 2,500 \text{ veh/h}$**, perfectly matching dual-lane urban arterial guidelines.

### 5.2 Free-Flow Speed Calibration
Using the relationship between speed, free-flow speed, and travel time index:
$$v_{\text{free-flow}} = v_{\text{observed}} \cdot \text{TTI}$$
The median implied free-flow speed across all 16 corridors evaluates to **$53.5 \text{ km/h}$** (interquartile range: $48.0\text{--}58.2 \text{ km/h}$). We adopt **$50.0 \text{ km/h}$** as the default baseline free-flow speed for urban arterials.

### 5.3 BPR Parameter Fitting
- Standard BPR parameters ($\alpha = 0.15, \beta = 4.0$) provide an accurate fit for low and moderate flow conditions ($V/C \le 1.0$), with a rapid non-linear travel time increase under oversaturation ($V/C > 1.0$).
- When fitting against the dataset's `Travel Time Index` (which was artificially clipped at $1.5$ in the source recording), standard BPR accurately predicts the onset of saturation at $V/C \approx 1.0$ where $\text{TTI} = 1 + 0.15(1)^4 = 1.15$ and accelerates toward $1.5+$ under capacity disruption.

---

## 6. Dataset Preprocessing & Cleaning

1. **Header Normalization**: Stripped outer web/markdown wrapper from live raw GitHub sources to preserve exact 16 CSV columns.
2. **Missing Values**:
   - 1 record missing `Weather Conditions` (imputed to `'Clear'`).
   - 1 record missing `Roadwork and Construction Activity` (imputed to `'No'`).
   - All core numeric features (`Traffic Volume`, `Average Speed`, `Travel Time Index`, `Congestion Level`, `Road Capacity Utilization`) are 100% complete with 0 nulls across all 3,082 rows.
3. **Data Integrity**: Enforced non-negative assertions and unit consistency across all downstream mathematical functions.

