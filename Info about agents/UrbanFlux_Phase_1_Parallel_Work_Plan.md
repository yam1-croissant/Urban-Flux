# UrbanFlux Sim — Phase 1 Parallel Work Plan

## Team Strategy

For now, all four team members work on **Agent 1 (simulation/math)** and **Agent 4 (research/validation/product)** first.

Do not have everyone build the entire simulation independently. Split the work into independent questions, produce focused documents, then merge the findings into one final domain model.

```text
PHASE 1
Agent 1 + Agent 4
Research + mathematical foundations
        ↓
PHASE 2
Agent 2
Backend + API + data integration
        ↓
PHASE 3
Agent 3
UI + bird's-eye visualization
```

The priority is:

> Make the underlying model correct and explainable before making the UI beautiful.

---

# Person A — Traffic Mathematics

## Main question

> Given a road's length, lanes, capacity, speed and traffic flow, how do we calculate travel time, congestion and delay?

Investigate:

- free-flow travel time
- road capacity
- traffic volume
- volume/capacity ratio
- congestion
- BPR-style travel-time models
- delay
- capacity reduction
- peak-hour effects

Example:

```text
flow = 2400 veh/hr
capacity = 3000 veh/hr
v/c = 0.80

free-flow time = 4.2 min
congested time = 6.1 min
delay = 1.9 min
```

### Deliverable

Create:

```text
docs/simulation/traffic_model.md
```

Include:

```text
Variable definitions
Equations
Units
Parameter choices
Assumptions
Sources
Limitations
Example calculation
```

Never present an empirical parameter as universal unless the source supports it. Clearly label demo assumptions.

---

# Person B — Network + Disruption + Cascade

This person owns three connected but separable topics:

```text
NETWORK
   ↓
DISRUPTION / REROUTING
   ↓
CASCADING FAILURE
```

## B1. Network Model

Main question:

> How do we mathematically represent a city?

Use a graph:

```text
G = (V, E)
```

Where:

```text
V = nodes/intersections
E = directed road segments
```

Determine the required fields.

### Node

```text
id
latitude
longitude
node_type
```

### Edge

```text
id
source
target
length
lanes
capacity
speed
flow
travel_time
status
```

Investigate:

- directed vs undirected graphs
- weighted graphs
- shortest paths
- alternate paths
- centrality
- bottlenecks

Deliverable:

```text
docs/simulation/network_model.md
```

---

## B2. Disruption + Rerouting

Main question:

> What happens mathematically when a road is closed or partially blocked?

Model:

```text
NORMAL NETWORK
      ↓
CAPACITY LOSS
      ↓
AFFECTED ROUTES
      ↓
REROUTING
      ↓
NEW TRAFFIC DISTRIBUTION
```

Investigate:

- shortest-path rerouting
- alternate routes
- k-shortest paths
- capacity constraints
- additional distance
- additional travel time

Example:

```text
Bridge A closes

1000 vehicles need another path

Road B:
v/c 0.72 → 1.13

Road C:
v/c 0.55 → 0.81
```

Deliverable:

```text
docs/simulation/disruption_and_rerouting.md
```

---

## B3. Cascading Failure

One of the most important topics.

Main question:

> How do we turn one infrastructure failure into a chain of secondary effects?

Target concept:

```text
INITIAL FAILURE
      ↓
CAPACITY LOSS
      ↓
TRAFFIC DIVERSION
      ↓
SECONDARY OVERLOAD
      ↓
TRAVEL-TIME INCREASE
      ↓
FURTHER REROUTING
      ↓
CRITICAL-SERVICE IMPACT
```

Investigate:

- overload thresholds
- propagation rules
- secondary failures
- tertiary effects
- cascade termination
- cascade severity
- resilience metrics

Example:

```text
Initial:
Bridge A

Secondary:
Road B

Tertiary:
Junction C

Critical impact:
Hospital access +7.4 min
```

Deliverable:

```text
docs/simulation/cascade_model.md
```

---

# Person C — Data + Scientific Research

## Main question

> What real data and scientific literature can support the model?

Do not just collect random papers. Build an evidence base.

## C1. Dataset Investigation

Investigate:

- road networks
- traffic counts
- average speeds
- congestion
- vehicle classes
- signal timings
- travel times
- POIs
- land use
- OD/trip demand

Candidate sources:

```text
OpenStreetMap / OSMnx
Bengaluru traffic datasets
IISc traffic datasets such as UVH-26
Indian government/open-data portals
METR-LA
PeMS-BAY
```

Global datasets can support ML research/benchmarking, but should not be described as Bengaluru ground truth.

Create:

```text
docs/research/data_sources.md
```

Use:

| Variable | Source | Geography | Resolution | Access/License | Observed/Derived | How We Use It | Limitations |
|---|---|---|---|---|---|---|---|
| Roads | OSM | Bengaluru | Road | ODbL | Observed | Network | ... |
| Traffic | Dataset X | Bengaluru | ... | ... | Observed | Calibration | ... |
| Vehicle type | UVH-26 | Bengaluru | Image | ... | Observed | Vehicle mix | ... |
| OD demand | Synthetic | Demo | ... | N/A | Synthetic | Demand | Not ground truth |

---

## C2. Traffic-Model Literature

Research:

- BPR-style travel-time functions
- traffic assignment
- fundamental diagrams
- heterogeneous traffic
- Indian traffic conditions
- road-capacity estimation
- congestion modeling

Output:

```text
MODEL
SOURCE
WHAT IT SUPPORTS
LIMITATIONS
SHOULD WE USE IT?
```

Deliverable:

```text
docs/research/traffic_literature.md
```

---

## C3. Cascading-Infrastructure Literature

Research:

- transportation network resilience
- cascading failures
- infrastructure interdependency
- critical infrastructure networks
- secondary congestion
- resilience metrics

Main goal:

> Establish why our modeling approach is scientifically reasonable.

Deliverable:

```text
docs/research/cascade_literature.md
```

---

# Person D — Product + Competition + Pitch

## Main question

> Why should anyone care about this, who would pay for it, and why is it different?

## D1. Competitor Research

Investigate:

- traffic simulation platforms
- digital twins
- infrastructure resilience tools
- transport planning software
- disaster simulation
- city-planning tools

Create:

```text
docs/product/competitors.md
```

For every competitor:

```text
Company
Product
Target customer
What it does
What it doesn't do
Pricing/model if publicly available
Our potential differentiation
```

---

## D2. Customer Validation

Research:

```text
municipal transportation departments
city planners
infrastructure engineering firms
construction planners
event planners
emergency management
```

For each:

```text
Problem
Current workflow
Existing tools
Pain point
Potential value of our product
```

Deliverable:

```text
docs/product/customers.md
```

---

## D3. Monetization

Develop:

```text
Who pays?
What are they buying?
Why is it valuable?
How does it scale?
```

Potential structure:

```text
BASIC
Scenario visualization

PRO
Private data
Calibration
Advanced scenarios

ENTERPRISE
City-scale deployments
Live feeds
APIs
Custom models
```

Do not invent precise pricing without evidence.

Deliverable:

```text
docs/product/monetization.md
```

---

# Optional Person E — Criticality + Demand

If someone finishes early, split these into their own topics.

## Criticality Model

Main question:

> Before anything fails, how do we determine which infrastructure assets are disproportionately important?

Investigate:

```text
degree centrality
betweenness centrality
closeness
flow centrality
population served
critical-service importance
```

Potential model:

```text
Criticality =
network importance
+
traffic dependence
+
population impact
+
critical-service importance
```

Make weights configurable and label assumptions.

Deliverable:

```text
docs/simulation/criticality_model.md
```

## Demand / OD Model

Main question:

> Where do vehicles come from and where are they going?

Represent:

```text
Origin → Destination
```

Example:

```text
Residential Zone A
        ↓ 1200 trips/hr
Office District

Residential Zone B
        ↓ 800 trips/hr
Hospital District
```

Investigate:

- OD matrices
- traffic zones
- peak-hour demand
- trip generation
- trip attraction
- synthetic demand
- commuter flows

Synthetic OD demand is acceptable for the demo if clearly labelled.

Deliverable:

```text
docs/simulation/demand_model.md
```

---

# How Everyone Should Use Antigravity Pro

Do not tell every agent:

> Build the whole simulation.

Give each agent a narrow research/engineering question.

Example:

```text
You are responsible for BPR and traffic travel-time modeling.

Do deep research.
Identify appropriate equations.
Compare alternatives.
List assumptions.
Provide units.
Provide sources.
Give a recommendation for a hackathon MVP.

Do NOT implement unrelated modules.
Do NOT build the UI.
Do NOT invent empirical claims.

Create/update:
docs/simulation/traffic_model.md
```

This prevents four agents from writing four incompatible traffic engines.

---

# Phase 1 Output

At the end of Phase 1:

```text
docs/
├── simulation/
│   ├── traffic_model.md
│   ├── network_model.md
│   ├── disruption_and_rerouting.md
│   ├── cascade_model.md
│   ├── criticality_model.md
│   └── demand_model.md
│
├── research/
│   ├── data_sources.md
│   ├── traffic_literature.md
│   └── cascade_literature.md
│
└── product/
    ├── competitors.md
    ├── customers.md
    └── monetization.md
```

Then merge the findings into:

```text
FINAL DOMAIN MODEL
```

---

# Merge Order

Do not start coding the full backend yet.

Merge in this order:

```text
1. Network Model
        ↓
2. Demand Model
        ↓
3. Traffic Model
        ↓
4. Disruption/Rerouting
        ↓
5. Cascade Model
        ↓
6. Criticality
        ↓
7. Data Mapping
        ↓
8. Validation
        ↓
9. API Contract
        ↓
10. Backend
        ↓
11. UI
```

---

# The Four Core Questions

Before Agent 2 begins, the team should be able to answer:

## 1. What is a road?

```text
Edge
with:
length
capacity
speed
flow
travel time
status
```

## 2. What is traffic?

```text
Demand
moving through
a network
with capacity constraints.
```

## 3. What happens when a road fails?

```text
Capacity decreases
        ↓
Routes become unavailable/expensive
        ↓
Demand reroutes
        ↓
Other roads become stressed
```

## 4. How do we measure damage?

```text
delay
travel-time increase
population affected
overloaded roads
critical-service impact
network degradation
```

If these four questions are clear, Agent 2 can integrate the system much faster.

---

# MVP Boundary

Do not try to build the whole original vision.

The MVP only needs to convincingly demonstrate:

```text
REAL/REALISTIC NETWORK
        ↓
BASELINE TRAFFIC
        ↓
ONE DISRUPTION
        ↓
REROUTING
        ↓
SECONDARY CONGESTION
        ↓
CRITICAL IMPACT
        ↓
MITIGATION
        ↓
BETTER OUTCOME
```

Everything else can be presented as the roadmap.

---

# Final Phase-1 Principle

The goal is not:

> Who can write the most code?

The goal is:

> **Who can remove the most uncertainty before we start integrating?**

Each person should finish with a document that another teammate can read and immediately use to make an implementation decision.
