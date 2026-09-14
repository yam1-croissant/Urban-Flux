# Agent 3 — Frontend, Bird's-Eye Map & Visualization

## Mission

You own the part the judges **see**.

The project should feel like:

> "The city itself is the interface."

The map is the centerpiece.

This is NOT a conventional dashboard with a tiny map and dozens of charts.

The intended flow is:

```text
SEE CITY
   ↓
SELECT DISRUPTION
   ↓
SIMULATE
   ↓
WATCH CASCADE
   ↓
UNDERSTAND IMPACT
   ↓
COMPARE MITIGATION
```

---

# 1. What You Own

You are responsible for:

- React application
- TypeScript
- map
- network rendering
- POI display
- disruption UI
- scenario controls
- cascade animation
- dashboard
- scenario comparison
- loading/error states
- responsive layout
- accessibility
- demo mode

You are NOT responsible for:

- traffic equations
- simulation engine
- FastAPI internals
- research validation
- business model

---

# 2. Visual Direction

Use:

```text
dark
cinematic
bird's-eye
map-first
high information density
minimal clutter
```

The map should occupy most of the screen.

Think:

```text
digital twin
+
traffic control center
+
simulation/game interface
```

not:

```text
Excel dashboard
```

---

# 3. Suggested Technology

The broader architecture proposes:

```text
React
Vite
TypeScript
TailwindCSS
MapLibre
Deck.gl
```

Use this stack unless the team has already selected a simpler equivalent.

---

# 4. Initial Layout

Recommended:

```text
┌──────────────────────────────────────────────────────────────┐
│ URBANFLUX          ● SIMULATION READY     [Scenario]  │
├──────────────┬───────────────────────────────────────────────┤
│              │                                               │
│ SCENARIO     │                                               │
│              │                                               │
│ Rush hour    │                 BIRD'S-EYE MAP                │
│              │                                               │
│ Failure      │        roads + POIs + traffic flow            │
│ [Bridge A]   │                                               │
│              │                                               │
│ Capacity     │                                               │
│ [██████░░]   │                                               │
│              │                                               │
│ Weather      │                                               │
│ [Normal]     │                                               │
│              │                                               │
│ [SIMULATE]   │                                               │
├──────────────┴───────────────────────────────────────────────┤
│ Delay +42% | 42.8k affected | 3 critical | Hospital +7.4m  │
└──────────────────────────────────────────────────────────────┘
```

---

# 5. Baseline State

Before simulation:

Show:

- road network;
- traffic stress;
- critical facilities;
- land-use/POI markers;
- current scenario name;
- basic network health.

Use clear visual states:

```text
green = healthy
yellow = stressed
orange = near overload
red = overloaded/failed
```

Always provide labels/icons in addition to color.

---

# 6. Road Rendering

Edges should respond to backend values such as:

```text
volume_capacity_ratio
status
affected
failed
delay
```

Example:

```text
v/c < 0.70 → green
0.70–0.90 → yellow
0.90–1.00 → orange
> 1.00 → red
```

Do not hard-code visual states unrelated to data.

---

# 7. POIs

Show important assets:

```text
🏥 hospital
🏫 school
🏢 office
🛍 shopping
🚉 transit
🚒 emergency
```

For the demo, only show the assets relevant to the scenario.

Too many markers will destroy map readability.

---

# 8. Disruption Studio

The judge needs to understand how to trigger a scenario.

User clicks a road.

Open a compact panel:

```text
BRIDGE A

Type:
Bridge / Arterial

Current capacity:
4,200 veh/hr

Current utilization:
93%

ACTION

[ Close Road ]

Capacity:
[████████░░] 50%

[ Apply ]
```

Also support:

```text
Construction
Event surge
Weather
```

---

# 9. Main Demo Interaction

The most important click sequence:

```text
1. User sees baseline
2. User selects Bridge A
3. User clicks CLOSE
4. User clicks SIMULATE
5. Loading state
6. Cascade animation
7. Metrics appear
8. User opens explanation
9. User selects mitigation
10. Run second scenario
11. Compare
```

This should work every single time.

---

# 10. Cascade Animation

This is your biggest visual moment.

Do not animate random roads.

Use actual affected edges from the simulation result.

Concept:

```text
Bridge A
   🔴
    ↓
secondary road
   🟠
    ↓
junction
   🟠
    ↓
hospital approach
   🔴
```

The animation can:

- pulse;
- change color;
- expand outward from the initial failure;
- display a small propagation timeline.

Example:

```text
T+0s   Bridge closure
T+1s   Route redistribution
T+2s   Secondary overload
T+3s   Hospital access impact
```

This makes the model feel causal.

---

# 11. Impact Dashboard

Show only the metrics that matter.

Example:

```text
TOTAL DELAY
+404 hours

AVG TRAVEL TIME
+24%

POPULATION AFFECTED
42,800

CRITICAL SERVICES
3

HOSPITAL ACCESS
+7.4 min
```

Avoid 20 meaningless KPIs.

---

# 12. "Why?"

Add an explainability panel:

```text
WHY DID THIS HAPPEN?

1. Bridge A lost 100% capacity.
2. 2,140 veh/hr shifted to Road B.
3. Road B exceeded 1.0 volume/capacity.
4. Congestion propagated toward Hospital C.
5. Hospital access increased by 7.4 min.
```

All values should come from backend results.

---

# 13. Criticality Visualization

Provide a small ranked panel:

```text
MOST CRITICAL ASSETS

1. Bridge A       0.91 █████████
2. Road B         0.86 ████████
3. Junction 12    0.77 ███████
4. Hospital Rd    0.74 ███████
```

Clicking an asset should highlight it on the map.

---

# 14. Scenario Comparison

After mitigation, show:

```text
                 NO ACTION      MITIGATION

Delay            +42%           +11%

Affected         42.8k          12.7k

Hospitals        3              1

Worst bottleneck Road B         Road D
```

Then a strong summary:

```text
MITIGATION REDUCED NETWORK IMPACT BY 53%
```

Only show that percentage if actually calculated.

---

# 15. Demo Mode

Build one button:

```text
▶ RUN DEMO SCENARIO
```

It should automatically:

```text
load baseline
→ select bridge
→ simulate failure
→ animate cascade
→ show impact
→ show mitigation
```

The demo must be replayable.

Never depend on a developer manually setting up the state before the judges arrive.

---

# 16. Loading States

Use narrative loading:

```text
Analyzing network...
Reassigning traffic...
Evaluating secondary bottlenecks...
Assessing critical services...
```

Do not show a generic spinner for several seconds.

---

# 17. Error States

If simulation fails:

```text
SIMULATION ERROR

We couldn't complete this scenario.

[Retry]
[Reset to Demo]
```

Don't leave an empty map.

---

# 18. API Dependency

You consume:

```text
GET /api/network
POST /api/simulate
POST /api/scenarios/compare
```

Do not fake backend results once integration starts.

During early development, use fixtures:

```text
mock_network.json
mock_simulation.json
```

Then replace them with live backend calls.

---

# 19. State Model

At a high level:

```text
BASELINE
   ↓
SELECTING
   ↓
CONFIGURED
   ↓
SIMULATING
   ↓
RESULT
   ↓
COMPARING
```

Keep state transitions predictable.

---

# 20. Suggested Folder Structure

```text
frontend/
├── src/
│   ├── components/
│   ├── map/
│   ├── dashboard/
│   ├── scenario/
│   ├── comparison/
│   ├── api/
│   ├── state/
│   └── types/
├── public/
└── ...
```

---

# 21. Definition of Done

MVP is done when:

- map loads;
- network appears;
- POIs appear;
- road can be selected;
- disruption can be applied;
- simulation actually runs;
- affected roads change;
- metrics update;
- critical asset is highlighted;
- scenario can be reset;
- mitigation comparison works;
- demo mode works.

---

# 22. What NOT to Build

Do not spend time on:

- perfect 3D buildings;
- fully realistic city rendering;
- excessive animations;
- 15 dashboard pages;
- complex user accounts;
- enterprise UX;
- advanced map editing;
- mobile app;
- dozens of scenario types.

A polished single flow beats a huge unfinished interface.

---

# 23. Antigravity Pro Prompt

```text
You are Agent 3 for UrbanFlux Sim.

You own ONLY:
- React frontend
- map
- visualization
- scenario UI
- dashboard
- comparison UI
- demo mode

Read AGENTS.md, docs/api.md and docs/demo-scenarios.md first.

Do not implement traffic mathematics.
Do not modify the simulation engine.
Do not put domain logic into map components.

The goal is a visually excellent hackathon demo.

Design principle:
"The city is the UI."

Prioritize:
1. bird's-eye map
2. baseline network
3. click-to-fail
4. simulation
5. visible cascade
6. impact dashboard
7. explanation
8. mitigation comparison
9. demo replay

Use real backend results once integration is available.

Never fake affected roads or metrics in production/demo mode.

Build the UI in small components.

Before changing shared API assumptions:
- inspect docs/api.md;
- check with Agent 2.

Before completing a PR:
- run the application;
- test the entire click → simulate → result flow;
- verify reset;
- verify demo mode;
- remove dead controls.
```

---

# 24. Coordination

### With Agent 1

You need these values:

```text
failed_edges
affected_edges
critical_assets
travel_time_delta
population_affected
service_impacts
criticality
explainability
```

Do not ask Agent 1 to format them for React.

### With Agent 2

Agent 2 owns the API.

You consume the API contract.

If a field is missing:

```text
document request
→ Agent 2
→ Agent 1 if required
```

### With Agent 4

Agent 4 provides:

- demo narrative;
- verified wording;
- metrics that matter to judges;
- pitch/video requirements.
