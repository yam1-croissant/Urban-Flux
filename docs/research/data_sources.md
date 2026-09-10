# UrbanResilience — Scientific Data Sources & Provenance Matrix

## 1. Data Architecture Strategy

UrbanResilience integrates multiple focused real-world datasets, where each dataset supplies a distinct architectural layer of the city model:

```text
[OpenStreetMap / OSMnx] ───> Network Topology, Geometry, Road Classes, POIs
[Kaggle Traffic Pulse]  ───> Empirical Volume, Speed, Congestion Distributions
[IISc UVH-26 Dataset]   ───> Indian Heterogeneous Vehicle Mix (2W/3W/Car/Bus/LCV)
[Synthetic OD Matrix]   ───> Controlled, Reproducible Commuter & Patient Demand
[METR-LA / PeMS-Bay]    ───> Spatio-Temporal Benchmark Research (Not Bengaluru Truth)
```

---

## 2. Comprehensive Data Provenance Matrix

| Variable / Layer | Primary Source | Geography | Spatial / Temporal Resolution | License / Access | Observed vs Modeled | How We Use It in UrbanResilience | Limitations & Integrity Guardrails |
|---|---|---|---|---|---|---|---|
| **Road Network Skeleton** | OpenStreetMap (OSM) via OSMnx | Bengaluru, India | Node/Edge precision (Lat/Lon coordinates) | ODbL (Open Database License) | **Observed** | Constructs graph topology $G=(V,E)$, link lengths ($L$), intersections, and functional road classes. | OSM speed limits and lane counts are occasionally incomplete; missing lane attributes default to functional class baselines. |
| **Corridor Traffic Volume** | *Bangalore Traffic Pulse* (Kaggle) | Bengaluru (8 zones, 16 arterial links) | 8,936 daily records (2022–2024) | Open Public Dataset | **Observed** | Provides empirical distributions for link volume, congestion, and baseline speed calibration. | Daily aggregate records lack intra-day hourly timestamps; peak hourly flows are derived using standard factors ($k_{\\text{peak}} = 0.085$). |
| **Travel Time & Congestion Index** | *Bangalore Traffic Pulse* (Kaggle) | Bengaluru | Daily records | Open Public Dataset | **Observed Index** | Validates non-linear correlation between traffic volume surge and congestion onset. | Travel Time Index is an observed dimensionless ratio (max 1.50), not a physical link traversal time in seconds. |
| **Vehicle Heterogeneity & Mix** | IISc UVH-26 Dataset | Bengaluru Urban Corridors | High-resolution traffic video frames | Academic Research (IISc AIM Lab) | **Observed (Sample)** | Justifies India-specific traffic composition (heavy 2-wheeler / 3-wheeler presence) and PCU equivalence concepts. | Video detection sample; not a continuous citywide sensor stream. Used for domain calibration. |
| **Critical POI Infrastructure** | OpenStreetMap Overpass API | Bengaluru | Point / Polygon coordinates | ODbL | **Observed** | Identifies hospitals, trauma centers, fire stations, and emergency shelters attached to graph vertices. | POI tags reflect physical location; bed capacity and trauma triage levels are estimated in Phase 1. |
| **Origin-Destination Demand** | Synthetic Benchmark Matrix | Demo Network | Hourly trip flow ($veh/h$) | Project Synthetic | **Modeled (Synthetic)** | Provides reproducible, deterministic commuter and emergency travel demand across zones. | Must always be labelled as synthetic demo demand, not measured municipal cellular OD truth. |
| **Benchmark GNN Telemetry** | METR-LA / PeMS-Bay | Los Angeles / SF Bay Area | 5-minute loop detector sensor feeds | Academic Benchmark (HuggingFace) | **Observed (External)** | Used strictly for future ML traffic forecasting research (DCRNN / ST-GNN architectures). | **Never** presented as Bengaluru ground truth; strictly an algorithmic evaluation benchmark. |

---

## 3. Data Integrity & Scientific Disclosure

To prevent misleading claims during technical evaluations and hackathon judging:
1. **Never Claim Undocumented Precision**: The Kaggle dataset does not contain sub-daily timestamps; we explicitly document date-level aggregation rather than claiming hourly sensor truth.
2. **Clear Separation of Assumptions**: Geometric link lengths and capacities in synthetic test cases are explicitly designated as **Assumptions** rather than field measurements.
3. **Reproducibility Guarantee**: All synthetic matrices and configuration parameters are packaged with deterministic test fixtures, guaranteeing 100% reproducible results.
