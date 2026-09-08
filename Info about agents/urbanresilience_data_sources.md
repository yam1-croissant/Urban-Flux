# UrbanResilience Sim - Data Sources for the Mathematical / Domain Model

## The key idea

You do **not** need one dataset containing everything.

For the mathematical/domain model, assemble several datasets where each one supplies a different part of the model:

- **OpenStreetMap + OSMnx** -> road-network skeleton and POIs
- **Bengaluru traffic data** -> traffic volume, speed, congestion observations
- **IISc UVH-26** -> Indian vehicle-class information from traffic imagery
- **Government Open Data** -> additional Bengaluru transportation information where available
- **Synthetic OD demand** -> origin-destination demand for the demo
- **METR-LA / PeMS-Bay** -> optional ML/traffic-forecasting research benchmarks, not Bengaluru ground truth

For a hackathon demo, consistency and repeatability matter more than finding a giant perfect dataset.

---

## 1. What data the model actually needs

| Model component | Data needed | Recommended source / approach |
|---|---|---|
| Road network | roads, intersections, direction, geometry, lanes, speed | OpenStreetMap + OSMnx |
| Traffic volume | vehicles/hour or counts by location/time | Bengaluru traffic dataset / Traffic Pulse |
| Average speed | speed by road/time | Bengaluru traffic dataset / Traffic Pulse |
| Congestion | congestion/index/utilization | Bengaluru traffic dataset / Traffic Pulse |
| Vehicle types | 2W, 3W, car, bus, LCV, etc. | IISc UVH-26 + explicit assumptions for demo |
| POIs / land use | hospitals, malls, offices, schools, transit | OSM / OSMnx |
| Trip demand / OD | origins, destinations, trip counts | Synthetic OD matrix for MVP |
| Forecasting / ML | time series of speed/flow | METR-LA / PeMS-Bay for research |

---

## 2. The overall data-to-model pipeline

```text
RAW DATA
   |
   +-------------------+
   |                   |
Road network        Traffic       POIs / land use
   |              observations          |
   +-------------------+-----------------+
                       |
                       v
                DOMAIN MODEL
                       |
      +-------------------------------+
      | Node                          |
      | Edge                          |
      | Capacity                      |
      | Speed                         |
      | Demand                        |
      | Travel time                   |
      | POI attraction                |
      | Criticality                   |
      | Dependencies                  |
      +-------------------------------+
                       |
                       v
                  SIMULATION
```

The important distinction is that **raw datasets do not directly give you every model variable**.

---

## 3. Road network: OpenStreetMap + OSMnx

OpenStreetMap gives you the **skeleton of the city**.

With OSMnx you can retrieve road networks and work with attributes such as geometry, directionality, length and other mapped features. It can also be used for POIs and routing/shortest-path operations.

A road edge can become something like:

```python
Edge(
    id="road_123",
    from_node="n17",
    to_node="n28",
    length=420,
    lanes=3,
    speed_limit=50,
    capacity=...
)
```

You do **not** need to manually create the roads.

**Use:**
- network topology
- road geometry
- intersections
- lane/speed attributes where mapped
- hospitals, malls, schools, offices and other POIs

**Important:** OSM is not a traffic sensor network. It gives you infrastructure structure, not real-time traffic truth.

---

## 4. Bengaluru traffic observations

A Bengaluru traffic dataset referenced in the project work contains fields such as date, area, road/intersection, traffic volume, average speed, travel-time index, congestion level and road-capacity utilization.

This is directly useful for creating empirical relationships such as:

```text
traffic volume up
      |
      v
volume / capacity up
      |
      v
travel time up
```

That gives the mathematical model a more defensible calibration starting point than completely invented numbers.

**Caveat:** corridor/intersection datasets should not be described as a perfect citywide sensor network. Use them as observations for calibration and plausibility checks.

---

## 5. Vehicle heterogeneity: IISc UVH-26

For the India-specific angle, IISc's **UVH-26** dataset is useful because it contains high-resolution traffic imagery from Bengaluru and many India-specific vehicle classes.

The conceptual pipeline is:

```text
traffic image
    |
vehicle detection / counts
    |
2W / 3W / car / bus / LCV ...
    |
vehicle mix
    |
traffic-flow model
```

For the first demo, do not build a full computer-vision pipeline unless there is spare time. Use the vehicle-class information to justify and construct a plausible synthetic mix.

---

## 6. Government transportation data

Also check the Indian Open Government Data platform and Bengaluru Smart City / transportation catalogs before relying heavily on secondary datasets.

Use government data where it gives you:
- official infrastructure information
- traffic counts
- transport inventories
- public-transport context
- city-specific metadata

The point is not to collect everything. The point is to find the few variables that materially improve your demo model.

---

## 7. Trip demand / OD data

This is the piece you are least likely to find cleanly for your demo.

You need something like:

```text
origin zone
 destination zone
 time period
 demand
 mode
```

For the MVP, **use a synthetic OD matrix**.

Example:

```text
Residential A -> Office District: 2,000 trips/h
Residential B -> Office District: 1,500 trips/h
Residential A -> Mall:              500 trips/h
Residential B -> Hospital:          250 trips/h
```

The important thing is to label this as **synthetic demo demand**, not measured city truth.

Later, real OD data can replace it without changing the core software architecture.

---

## 8. METR-LA / PeMS-Bay

These are excellent for experimenting with traffic forecasting and spatio-temporal graph models such as DCRNN/ST-GNN-style approaches.

However:

> They are useful as research benchmarks, not as Bengaluru ground truth.

Do not use LA or Bay Area data in the pitch as if it describes Bengaluru.

Use them to test an ML pipeline or demonstrate that you understand traffic forecasting research.

---

## 9. What is actually observed vs modeled?

This distinction is critical.

### Raw / observed data

```text
Road A
volume = 3200 veh/h
speed = 34 km/h
lanes = 3
length = 1.2 km
```

### Derived / modeled quantities

```text
free-flow time = length / free-flow speed

v/c = traffic volume / capacity

delay = congested time - free-flow time

criticality = f(
    rerouting importance,
    network centrality,
    population impact,
    critical-service importance
)
```

So:

> **Dataset = observations of the real world.**
>
> **Domain model = structured representation of that world.**
>
> **Simulation = what the model predicts when the world changes.**

---

## 10. Recommended demo data stack

For the current hackathon prototype, I would use a small, coherent Bengaluru network rather than trying to reproduce the whole city.

### Recommended stack

**OSM / OSMnx**
- actual network geometry
- intersections
- roads
- POIs

**Bengaluru traffic observations**
- realistic traffic volume
- speed
- congestion

**IISc UVH-26**
- plausible Indian vehicle composition

**Government Open Data**
- city-specific transport context where useful

**Synthetic OD matrix**
- commuter demand for the demo

**Your simulation**
- capacity
- travel time
- rerouting
- cascade
- criticality
- scenario impact

---

## 11. The domain model Agent 1 should build

The modeling agent should explicitly define at least:

### Node
- id
- latitude
- longitude
- node type
- signal information where applicable
- POI associations

### Edge
- id
- source
- target
- length
- lanes
- free-flow speed
- capacity
- road class
- baseline flow
- current flow
- status
- disruption multiplier
- curb/weather modifiers where used
- geometry reference

### POI / critical asset
- id
- type
- location
- attraction/production values
- service population
- criticality weight

### Demand
- origin
- destination
- time period
- demand
- mode

### Disruption
- asset id
- disruption type
- capacity multiplier
- duration / scenario metadata

### Scenario
- baseline demand/time window
- disruptions
- demand multipliers
- weather/event parameters

### SimulationResult
- baseline metrics
- scenario metrics
- affected edges
- affected assets
- reroutes
- population affected
- service impacts
- critical assets
- warnings / explainability

---

## 12. The table the team should maintain

Create a living table like this in `docs/data-sources.md`:

| Variable | Source | Observed or modeled? | Demo status |
|---|---|---|---|
| road geometry | OSM | observed | use |
| road length | OSM | observed | use |
| lanes | OSM | observed / sometimes incomplete | use where present |
| speed limit | OSM | observed / sometimes incomplete | use where present |
| traffic volume | Bengaluru traffic data | observed | use |
| average speed | Bengaluru traffic data | observed | use |
| congestion | Bengaluru traffic data | observed | use |
| vehicle mix | UVH-26 / assumptions | mixed | use |
| POI locations | OSM | observed | use |
| OD demand | synthetic | modeled | use |
| capacity | derived / calibrated | modeled | use |
| travel time | model-derived | modeled | use |
| failure | scenario input | modeled input | use |
| rerouting | simulation | modeled | use |
| cascade | simulation | modeled | use |
| criticality | simulation | modeled | use |

This prevents the team from accidentally presenting a model assumption as measured fact.

---

## 13. What Agent 1 should hear

> Don't start by searching for the perfect dataset. First define every variable our simulation needs. Then map each variable to a credible source, a derived calculation, or an explicit demo assumption.

The agent should build the mathematical model around that table.

---

## 14. Scope recommendation for the demo

Do **not** spend the hackathon trying to find:
- ten years of perfect citywide traffic data;
- every municipal sensor feed;
- live Google/TomTom traffic scraping;
- a perfect OD matrix;
- production-grade ML training data.

Instead, make one reproducible scenario where the data is coherent and the chain works:

```text
network
  -> baseline traffic
  -> road closure
  -> rerouting
  -> secondary congestion
  -> delay
  -> hospital/service impact
  -> mitigation comparison
```

That is enough to make the mathematical/domain model credible for a working prototype.

---

## Sources to start with

- OpenStreetMap / OSMnx documentation: https://osmnx.readthedocs.io/en/stable/getting-started.html
- Bengaluru traffic dataset discussion: https://pmc.ncbi.nlm.nih.gov/articles/PMC12638989/
- Bengaluru traffic prediction research: https://www.nature.com/articles/s41598-025-25075-4
- IISc UVH-26 announcement: https://www.iisc.ac.in/events/aim-iisc-announces-public-release-of-uvh-26-dataset-and-vision-models-for-indian-urban-traffic/
- NYC TLC trip record data (useful as a research benchmark for OD/trip-data structure): https://www.nyc.gov/site/tlc/about/data.page
- METR-LA benchmark dataset: https://huggingface.co/datasets/THULab/METR-LA
