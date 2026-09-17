# UrbanFlux — Part A: Traffic Mathematics Model

## Tiny Context

We are building the mathematical traffic-flow foundation for UrbanFlux.

Use the **Bangalore's Traffic Pulse** dataset from Kaggle as the primary real-world traffic dataset:

https://www.kaggle.com/datasets/preethamgouda/banglore-city-traffic-dataset/data

The goal is to turn this dataset into a simple, transparent traffic model that later parts of the project can use when simulating road disruptions.

Do **not** spend time researching what this project or dataset is. Start directly with the task below.

---

## Objective

Build the first working mathematical traffic model for UrbanFlux.

Focus on:

1. Free-flow travel time
2. Road capacity
3. Traffic volume
4. Volume/capacity ratio (V/C)
5. Congestion
6. BPR-style travel-time model
7. Delay
8. Capacity reduction
9. Peak-hour effects

The model must be simple, transparent, testable, and easy for later simulation/routing code to use.

---

## 1. Inspect the Dataset

Load the Kaggle dataset into Python and map its actual columns to the variables needed by our model.

Do not do broad dataset research. Inspect the actual files/columns and determine what is available.

Create a mapping like:

| Model Variable | Dataset Column | Direct / Derived | Notes |
|---|---|---|---|
| Traffic volume | | | |
| Average speed | | | |
| Road/intersection | | | |
| Timestamp/date | | | |
| Travel time | | | |
| Congestion | | | |
| Capacity / capacity utilization | | | |
| Peak period | | | |

Be explicit about variables that are **not directly available**. Do not invent measurements.

---

## 2. Define the Mathematical Model

Use established traffic-flow relationships.

### Free-flow travel time

\[
t_0 = \frac{L}{v_f}
\]

where:

- L = road length
- vf = free-flow speed
- t0 = free-flow travel time

Keep units consistent.

### Volume / Capacity Ratio

\[
V/C = \frac{V}{C}
\]

where:

- V = traffic volume
- C = road capacity

### BPR-style Travel Time

\[
t = t_0 \left[1+\alpha\left(\frac{V}{C}\right)^\beta\right]
\]

Implement this as a configurable function.

Do not hard-code unexplained parameter choices.

### Delay

At minimum:

\[
D = t-t_0
\]

Distinguish between:

- delay per vehicle
- total delay across vehicles

We will likely need both later.

### Capacity Reduction

Represent a disruption as:

\[
C_{new}=C(1-r)
\]

where r is the fraction of capacity removed.

Examples:

- 0.10 → 10% reduction
- 0.25 → 25% reduction
- 0.50 → 50% reduction
- 1.00 → complete closure

The model must safely handle a completely closed road.

---

## 3. Determine Missing Variables

Some variables may not exist directly in the dataset.

Do not fake them.

For every missing variable, decide whether it should be:

1. derived from available data,
2. estimated from a defensible assumption,
3. supplied later by the road-network dataset,
4. or left out of the MVP.

Document these decisions in:

`docs/simulation/traffic_math_data.md`

---

## 4. Peak-Hour Effects

Use the dataset's date/time information to identify traffic variation across the day.

At minimum compare:

- lower-traffic periods
- peak periods

Show traffic volume/speed/congestion by time period if the dataset supports it.

The goal is to show that the same road can behave differently depending on demand.

---

## 5. Parameter Calibration

We are **not inventing a new traffic equation**.

Use the established mathematical form and determine which parameters need to be adapted to the Bangalore data.

Where the data supports it, fit/calibrate parameters such as:

- BPR alpha
- BPR beta
- free-flow assumptions
- capacity assumptions

Clearly separate:

**Observed** — directly present in the dataset

**Derived** — calculated from observed data

**Assumed** — introduced because the dataset does not provide them

Do not silently turn assumptions into facts.

---

## 6. Build the Python Model

Create:

`src/simulation/traffic_math.py`

Implement clean, reusable functions along these lines:

```python
free_flow_time(...)
vc_ratio(...)
bpr_travel_time(...)
delay(...)
reduced_capacity(...)
```

Keep functions independent, use clear names/units, and add sensible error handling.

The later network simulation should be able to import this module without depending on notebooks.

---

## 7. Tests

Create:

`tests/test_traffic_math.py`

Test at least:

- low traffic
- moderate traffic
- high V/C
- V/C near 1
- V/C greater than 1
- capacity reduction
- complete road closure
- different road lengths
- different speeds
- invalid/zero capacity handling

Do not allow division-by-zero or silent nonsense.

---

## 8. Demonstration

Create:

`examples/traffic_math_demo.py`

Demonstrate one road under increasing disruption:

```text
Baseline
↓
10% capacity reduction
↓
25% capacity reduction
↓
50% capacity reduction
↓
100% capacity reduction
```

For each scenario show:

- capacity
- traffic volume
- V/C
- predicted travel time
- delay

If useful, generate a simple plot showing how travel time/delay changes as capacity falls.

---

## 9. Documentation

Create:

`docs/simulation/traffic_math.md`

Document:

- model purpose
- equations
- variables
- units
- assumptions
- parameter choices
- calibration approach
- limitations
- examples

Create:

`docs/simulation/traffic_math_data.md`

Document:

- dataset files used
- relevant columns
- observed vs derived variables
- missing variables
- assumptions/estimates
- preprocessing
- peak-hour analysis
- calibration procedure
- limitations

Keep the documentation concise but technically clear.

---

## Important Scope Boundary

Do **not** build:

- frontend
- API
- authentication
- Google Maps
- full routing engine
- city-wide network simulation
- computer vision
- real-time traffic
- ML forecasting model
- agent-based simulation

This task is only the **traffic mathematics foundation**.

The later network/routing work will consume this model.

---

## Definition of Done

This task is complete when we have:

```text
Kaggle Bangalore data
        ↓
data → model-variable mapping
        ↓
traffic mathematics
        ↓
calibrated/defensible parameters
        ↓
Python traffic model
        ↓
tests
        ↓
small demonstration
```

Required files:

```text
docs/simulation/traffic_math.md
docs/simulation/traffic_math_data.md
src/simulation/traffic_math.py
tests/test_traffic_math.py
examples/traffic_math_demo.py
```

The final result should let another developer do something conceptually like:

```python
from src.simulation.traffic_math import (
    free_flow_time,
    vc_ratio,
    bpr_travel_time,
    delay,
    reduced_capacity,
)
```

and use the functions directly in the UrbanFlux simulation.

## Final Principle

**Do not overbuild this.**

We need a mathematically defensible MVP, not a complete transportation research platform.

The later simulation will take this foundation and answer questions such as:

> "If this road loses 50% of its capacity during peak hour, how much does travel time increase?"

That is the output this task should enable.
