# UrbanResilience — Traffic Mathematics Data Analysis & Mapping

## 1. Dataset Overview

- **Source File**: `Banglore_traffic_Dataset.csv`
- **Origin**: *Bangalore's Traffic Pulse* (Kaggle dataset by Preetham Gouda)
- **Record Count**: 8,936 observations
- **Date Range**: 952 unique calendar dates from `2022-01-01` through `2024-08-09`
- **Spatial Coverage**: 8 geographic areas across Bengaluru, comprising 16 named arterial roads / key intersections (2 named links per area):
  - **Electronic City**: Silk Board Junction, Hosur Road
  - **Hebbal**: Hebbal Flyover, Ballari Road
  - **Indiranagar**: 100 Feet Road, CMH Road
  - **Jayanagar**: Jayanagar 4th Block, South End Circle
  - **Koramangala**: Sony World Junction, Sarjapur Road
  - **M.G. Road**: Trinity Circle, Anil Kumble Circle
  - **Whitefield**: Marathahalli Bridge, ITPL Main Road
  - **Yeshwanthpur**: Yeshwanthpur Circle, Tumkur Road

---

## 2. Variable Mapping & Provenance

To maintain strict scientific integrity, all variables in the UrbanResilience simulation are classified into four mutually exclusive categories:
1. **Observed**: Directly recorded in `Banglore_traffic_Dataset.csv`.
2. **Derived**: Computed mathematically from observed dataset fields without external assumptions.
3. **Assumed**: Explicitly documented assumptions introduced where direct measurements do not exist.
4. **Future Network Input**: Geometric or physical attributes to be supplied in Phase 2 via OpenStreetMap (OSM) / network topology.

| Model Variable | Dataset Column | Classification | Handling & Documentation |
|---|---|---|---|
| Traffic Volume | `Traffic Volume` | **Observed** | Daily aggregated traffic volume (mean: 29,236; min: 4,233; max: 72,039). Units are not explicitly specified in the raw file; treated as aggregate daily vehicle counts. |
| Average Speed | `Average Speed` | **Observed** | Observed speed (mean: 39.45 km/h; min: 6.81 km/h; max: 89.79 km/h). Treated as km/h by standard convention. |
| Road / Intersection Name | `Road/Intersection Name` | **Observed** | Nominal identifier for the road corridor or junction. |
| Area Name | `Area Name` | **Observed** | Geographic sector in Bengaluru. |
| Date | `Date` | **Observed** | ISO date string (`YYYY-MM-DD`). **Contains no time-of-day timestamp.** |
| Travel Time Index | `Travel Time Index` | **Observed Index** | Relative ratio of travel time under congestion to baseline (mean: 1.38; max: 1.50). **Note:** This is an index, not an observed link travel time in minutes. |
| Congestion Level | `Congestion Level` | **Observed** | Aggregate congestion index (mean: 80.82; scale 0–100%). |
| Capacity Utilization | `Road Capacity Utilization` | **Observed Index** | Reported utilization percentage (mean: 92.03%; scale 0–100%). **Note:** This is a percentage index, not a measured physical capacity in veh/h. |
| Supporting Context | `Incident Reports`, `Weather Conditions`, `Roadwork and Construction Activity` | **Observed** | Contextual factors for incident frequency, weather categories, and active roadworks. |
| Road Link Length (L) | *None* | **Future Network Input** | Physical link length is absent from the CSV. Must be queried from OpenStreetMap (OSM) geometry in Phase 2; never fabricated as observed data. |
| Physical Link Capacity (C) | *None* | **Future Network Input / Assumed** | Absolute physical capacity in veh/h is absent from the CSV. In Part A, realistic hourly capacities (e.g., 2,000–3,500 veh/h) are treated as explicit, documented scenario assumptions. In Phase 2, this will be derived from OSM lane counts and functional road classifications. |
| Time-of-Day Peak Period | *None* | **Assumed / Not In File** | The CSV provides daily aggregated records without sub-daily timestamps. Intra-day AM/PM peak comparisons cannot be claimed from this file alone. Peak-hour flow rates are derived using standard peak-to-daily factors (\(k pprox 0.08 - 0.10\)). |

---

## 3. Empirical Traffic Analysis & Dataset Facts

### 3.1 Summary Statistics

| Column | Count | Mean | Std Dev | Min | Median (50%) | 75% | Max |
|---|---|---|---|---|---|---|---|
| `Traffic Volume` | 8,936 | 29,236.0 | 13,001.8 | 4,233.0 | 27,600.0 | 38,058.5 | 72,039.0 |
| `Average Speed` | 8,936 | 39.45 | 8.87 | 6.81 | 39.40 | 46.64 | 89.79 |
| `Travel Time Index` | 8,936 | 1.38 | 0.17 | 1.00 | 1.48 | 1.50 | 1.50 |
| `Congestion Level` | 8,936 | 80.82 | 22.06 | 12.04 | 91.24 | 100.0 | 100.0 |
| `Road Capacity Utilization`| 8,936 | 92.03 | 16.58 | 18.74 | 100.0 | 100.0 | 100.0 |
| `Incident Reports` | 8,936 | 1.57 | 1.25 | 0 | 1.0 | 2.0 | 10 |

### 3.2 Correlation Matrix of Observed Fields

| Metric | Traffic Volume | Average Speed | Travel Time Index | Congestion Level | Capacity Utilization |
|---|---|---|---|---|---|
| **Traffic Volume** | 1.000 | -0.341 | 0.698 | 0.837 | 0.653 |
| **Average Speed** | -0.341 | 1.000 | -0.376 | -0.360 | -0.250 |
| **Travel Time Index** | 0.698 | -0.376 | 1.000 | 0.752 | 0.508 |
| **Congestion Level** | 0.837 | -0.360 | 0.752 | 1.000 | 0.865 |
| **Capacity Utilization** | 0.653 | -0.250 | 0.508 | 0.865 | 1.000 |

**Key Empirical Insights**:
1. **Strong Congestion-Volume Coupling**: Traffic Volume exhibits a strong positive correlation with Congestion Level (\(r = 0.837\)) and Travel Time Index (\(r = 0.698\)).
2. **Inverse Speed-Volume Relationship**: Average speed degrades consistently as volume and congestion increase (\(r = -0.341\)), aligning with classic fundamental traffic-flow diagrams.
3. **Saturation Ceiling**: Travel Time Index reaches a recorded ceiling of 1.50, while Congestion Level and Capacity Utilization frequently hit 100%, indicating persistent high-demand corridors in Bengaluru.

### 3.3 Spatial Congestion Ranking across Bengaluru Corridors

Corridors ranked by mean observed Congestion Level:
1. **Koramangala** (Sony World Junction: 94.13%, Sarjapur Road: 93.85%) — *Highest congestion in dataset*
2. **M.G. Road** (Anil Kumble Circle: 90.78%, Trinity Circle: 90.37%)
3. **Indiranagar** (CMH Road: 88.18%, 100 Feet Road: 87.11%)
4. **Hebbal** (Hebbal Flyover: 80.66%, Ballari Road: 79.51%)
5. **Jayanagar** (South End Circle: 77.28%, Jayanagar 4th Block: 76.71%)
6. **Whitefield** (ITPL Main Road: 71.10%, Marathahalli Bridge: 67.18%)
7. **Yeshwanthpur** (Yeshwanthpur Circle: 63.74%, Tumkur Road: 60.95%)
8. **Electronic City** (Hosur Road: 55.20%, Silk Board Junction: 53.70%)

---

## 4. Analysis of Temporal Traffic Variation & Limitations

### 4.1 Day-of-Week & Date-Level Patterns

| Day of Week | Mean Traffic Volume | Mean Average Speed (km/h) | Mean Travel Time Index | Mean Congestion Level (%) |
|---|---|---|---|---|
| **Monday** | 29,510 | 39.24 | 1.38 | 81.42 |
| **Tuesday** | 28,911 | 39.55 | 1.37 | 80.33 |
| **Wednesday** | 29,698 | 39.41 | 1.38 | 81.28 |
| **Thursday** | 29,530 | 39.47 | 1.38 | 81.15 |
| **Friday** | 28,843 | 39.50 | 1.37 | 80.27 |
| **Saturday** | 29,063 | 39.59 | 1.37 | 80.28 |
| **Sunday** | 29,105 | 39.38 | 1.38 | 81.02 |

- **Weekday vs Weekend Comparison**:
  - Weekday Mean Volume: **29,297 vehicles/day** (Mean Congestion: 80.89%)
  - Weekend Mean Volume: **29,084 vehicles/day** (Mean Congestion: 80.64%)
  - Day-to-day variance is modest, indicating sustained demand across all days of the week on these major commercial and tech corridors.

### 4.2 Why Intra-Day Peak-Hour Analysis Cannot Be Claimed from This File

- **Dataset Limitation**: Each record in `Banglore_traffic_Dataset.csv` represents a single daily aggregate for a specific road on a given calendar date. The dataset **lacks hourly timestamps (e.g. 08:00 AM, 05:30 PM)**.
- **Handling in UrbanResilience**:
  - We do **not** claim to observe hourly AM/PM peaks directly from this file.
  - For hourly simulation and demonstration scenarios (such as `examples/traffic_math_demo.py`), we convert daily volume to peak hourly demand using standard transportation planning assumptions:
    211183V_{\text{peak}} = V_{\text{daily}} \times k211183
    where \(k pprox 0.08 - 0.10\) is the peak-hour factor (yielding \(pprox 2,400 - 3,000	ext{ veh/h}\) for major arterial links).
  - All such conversions are explicitly labelled as **Assumptions** rather than observed facts.

---

## 5. Parameter Calibration Considerations

### 5.1 Identifiability of Physical BPR Parameters (\(lpha, eta\))
The standard Bureau of Public Roads (BPR) function relates physical link travel time to physical link capacity:

211183t = t_0 \cdot \left[1 + \alpha \cdot \left(\frac{V}{C}\right)^\beta\right]211183

Because `Banglore_traffic_Dataset.csv` contains:
- **No link lengths** (cannot compute true physical \(t_0\)),
- **No absolute link capacities in veh/h** (only percentage utilization index), and
- **No measured link travel times in seconds/minutes** (only Travel Time Index capped at 1.5),

a rigorous physical calibration of link-level \(lpha\) and \(eta\) is **not identifiable** from this dataset alone.

### 5.2 Recommended Calibration Architecture
1. **Configurable Default Baseline**:
   Use standard Bureau of Public Roads defaults (\(lpha = 0.15, eta = 4.0\)) as the baseline in `src/simulation/traffic_math.py`.
2. **Explicit Parameter Interfaces**:
   All mathematical functions accept explicit `alpha` and `beta` arguments, enabling sensitivity testing and calibration against synthetic or future sensor telemetry.
3. **Phase 2 Integration**:
   When OpenStreetMap geometric link lengths and lane counts are loaded in Phase 2, link capacities will be computed directly (\(C = 	ext{lanes} 	imes 900	ext{ veh/h/lane}\)), providing a complete physical grounding.
