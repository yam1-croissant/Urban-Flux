# UrbanResilience UI / UX Redesign
## Interactive User Guide + Onboarding Intro Specification

### Goal

Make the UrbanResilience interface immediately understandable to a first-time user.

The onboarding should feel like a **guided tour of the interface**, not a generic help page. The user should learn the workflow by following the actual controls on screen:

**Choose a disruption → configure it → select roads/conditions → run the simulation → understand the cascade → compare scenarios.**

The visual treatment should match the existing **Scenario Policy Comparison** modal:

- Darkened/blurred background
- A focused spotlight around the active UI element
- A compact floating explanation window
- Clear `X` close control
- `Next` button for guided progression
- Smooth transitions between steps

---

## 1. Overall Onboarding Behavior

When the site is opened for the first time, launch a short interactive introduction.

Do **not** immediately explain every feature.

Instead, progressively reveal the interface in roughly 8–12 steps.

### Visual treatment

When the intro is active:

```text
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   Entire application becomes dimmed + slightly blurred      │
│                                                              │
│        ┌───────────────────────────────┐                     │
│        │  INTRODUCTION              ×  │                     │
│        │                               │                     │
│        │  This is where you can        │                     │
│        │  simulate disruptions...      │                     │
│        │                               │                     │
│        │                 [ Next → ]     │                     │
│        └───────────────────────────────┘                     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

The currently explained component should remain visually highlighted and sharp above the overlay.

### Important interaction rule

The onboarding overlay should **not change the actual application state**.

Closing with `X` should immediately return to the normal interface.

Clicking `Next` should move to the next highlighted component.

---

## 2. Step 1 — Disruption Studio

### Spotlight

Highlight the entire **Disruption Studio** panel.

Everything else becomes darker and slightly blurred.

### Text

> ## Disruption Studio
>
> This is where you create the situation you want to test.
>
> Choose what is affecting the city — such as **monsoon flooding, construction, infrastructure closures, demand surges, or emergency response events**.
>
> You can then configure the disruption and see how the network responds.
>
> **Give it a try!**

Button:

```text
Next →
```

Close:

```text
×
```

---

## 3. Step 2 — Disruption Categories

### Spotlight

Move the spotlight specifically onto the disruption category selector.

Example:

```text
[ 🌧 Monsoon ▾ ]
```

### Text

> ## Choose a disruption
>
> Similar scenarios are grouped together so the interface stays clean.
>
> Select a category such as:
>
> - Monsoon
> - Construction
> - Infrastructure Closure
> - Events / Demand
> - Emergency Response
>
> Once you select one, the other categories collapse so you only work with the scenario you need.

Button:

```text
Next →
```

---

## 4. Step 3 — Scenario Selection / Link Inspector

### Spotlight

Highlight the **Link Inspector**.

The Link Inspector should be positioned above the Disruption Studio in the final UI, but hidden on initial load.

After selecting a scenario or relevant road, it should smoothly expand into view and push the Disruption Studio downward.

### Text

> ## Your selection appears here
>
> Once you choose a scenario or select an affected road, the **Link Inspector** opens here.
>
> It gives you the important information for the selected part of the network without filling the screen with details you don't need yet.

Button:

```text
Next →
```

---

## 5. Step 4 — Schematic Twin

Switch attention to the **Schematic Twin** rather than explaining detailed road configuration on the satellite map.

### Spotlight

Highlight the **Schematic Twin / network view**.

### Text

> ## Schematic Twin
>
> This view simplifies the city into a clear road network so you can understand what is actually being simulated.
>
> Roads, intersections, capacity, and traffic flow are easier to inspect here.
>
> **This is where you can directly experiment with the network.**

Button:

```text
Next →
```

---

## 6. Step 5 — Selecting Roads

### Spotlight

Highlight a representative road/link on the Schematic Twin.

### Text

> ## Select a road
>
> Click a road on the schematic to inspect it.
>
> You can see information such as:
>
> - Road identity
> - Current traffic
> - Capacity
> - Free-flow conditions
> - Current stress / V/C
>
> Selected roads can then be modified as part of your scenario.

Button:

```text
Next →
```

---

## 7. Step 6 — Changing Traffic / Road Conditions

### Spotlight

Highlight the controls inside the Link Inspector.

### Text

> ## Change the network
>
> This is where you can experiment with the conditions of the network.
>
> Depending on the selected scenario, you can change things such as:
>
> - Road capacity
> - Number of vehicles / traffic demand
> - Closure percentage
> - Disruption intensity
> - Other scenario-specific conditions
>
> For example, you could reduce a road to **50% capacity** and then see where the displaced traffic goes.

Button:

```text
Next →
```

---

## 8. Step 7 — Run Simulation

### Spotlight

Highlight:

```text
RUN SIMULATION
```

### Text

> ## Run the simulation
>
> Once your scenario is ready, run the simulation.
>
> The system recalculates the network and evaluates how traffic moves after the disruption.
>
> It looks for:
>
> **rerouting → congestion → secondary bottlenecks → critical-service impacts**
>
> The result is shown directly on the map and in the analysis panels.

Button:

```text
Next →
```

---

## 9. Step 8 — Cascade Propagation Timeline

Highlight the **Cascade Propagation Timeline** after the simulation.

### Text

> ## Follow the cascade
>
> A disruption does not always stay isolated.
>
> The timeline shows how the initial failure propagates through the network:
>
> **Primary failure**
>
> ↓
>
> **Traffic diversion**
>
> ↓
>
> **Secondary overload**
>
> ↓
>
> **Critical service impact**
>
> This helps you understand **why** the network changed, not just what the final numbers are.

Button:

```text
Next →
```

---

## 10. Step 9 — Causal Explainability

Highlight the **Causal Explainability** panel.

### Text

> ## Why did this happen?
>
> This panel explains the simulation in a simple causal chain.
>
> Instead of only saying that a road became congested, it shows the chain of events that led there.
>
> Example:
>
> `Bridge closure → traffic diversion → bottleneck overload → hospital access penalty`

Button:

```text
Next →
```

---

## 11. Step 10 — Criticality / Vulnerability Ranking

Highlight the **Criticality & Vulnerability Ranking** panel.

### Text

> ## Which parts of the network matter most?
>
> This panel highlights roads and assets that become especially important under the current network conditions.
>
> Use it to quickly identify:
>
> - stressed corridors
> - overloaded links
> - important bottlenecks
> - critical infrastructure
>
> Think of this as the shortlist of places that deserve attention.

Button:

```text
Next →
```

---

## 12. Step 11 — Key Metrics

Highlight the row containing:

```text
Net System Delay
Hospital Access
Cascade Overloads
Net Trip Time Change
```

These metrics should be positioned **above the map** so they are visible without zooming out.

### Text

> ## Understand the impact
>
> These four numbers summarize the most important outcome of the simulation.
>
> **Net System Delay** — how much additional delay the network experienced.
>
> **Hospital Access** — how emergency/critical-service access changed.
>
> **Cascade Overloads** — how many secondary bottlenecks appeared.
>
> **Net Trip Time Change** — how much overall travel time changed.
>
> Use these to compare different scenarios quickly.

Button:

```text
Next →
```

---

## 13. Step 12 — Scenario Policy Comparison

Highlight the existing **Scenario Policy Comparison** button/modal.

Match the visual language of the existing comparison screenshot.

### Text

> ## Compare what you could do
>
> One disruption can have multiple possible responses.
>
> Use scenario comparison to examine different interventions and see how their outcomes differ.
>
> For example:
>
> **No mitigation**
>
> vs.
>
> **Alternative routing / intervention**
>
> Compare the resulting network delay, bottlenecks, and critical-service impacts.

Button:

```text
Finish →
```

---

## 14. Final Tutorial State

After `Finish`, remove the overlay and return to the normal application.

Optionally show a small confirmation:

```text
✓ You're ready

Choose a disruption and run your first scenario.
```

This should disappear automatically after a short duration.

Do not trap the user inside the tutorial.

---

## 15. Tutorial Navigation

### Close

`X` in the top-right of the explanation window.

Behavior:

- Immediately exit onboarding.
- Remove blur.
- Remove spotlight.
- Return to normal UI.

### Next

Moves to the next tutorial step.

### Back

Optional, but useful once onboarding becomes longer.

### Skip Tutorial

Optional link:

```text
Skip tutorial
```

Store a local flag such as:

```text
urbanresilience_onboarding_complete = true
```

so the tutorial does not automatically appear on every visit.

Provide a small `?` / `Help` button somewhere in the application to reopen it later.

---

## 16. Spotlight Design

Use the existing Scenario Policy Comparison visual language as the reference.

Suggested treatment:

```text
background:
rgba(0, 0, 0, 0.65)

backdrop-filter:
blur(5px)
```

The highlighted component should remain sharp.

Add a subtle glow/border around the highlighted element.

The spotlight should follow the actual element rather than using hard-coded screen coordinates.

---

## 17. Explanation Window Design

Use a compact floating card rather than a huge modal.

Recommended structure:

```text
┌────────────────────────────────────┐
│ INTRODUCTION                    ×  │
│                                    │
│ Disruption Studio                  │
│                                    │
│ This is where you create the       │
│ situation you want to test...      │
│                                    │
│                        [ Next → ]  │
└────────────────────────────────────┘
```

Match the existing Scenario Policy Comparison modal:

- rounded corners
- dark navy panel
- subtle border
- soft shadow/glow
- clean typography
- cyan accent
- strong white title
- muted supporting text

---

## 18. Responsive Behavior

The tutorial must work at different viewport sizes.

Do not position tutorial windows using fixed page coordinates.

Preferred behavior:

```text
Desktop:
tooltip next to highlighted target

Narrow screen:
tooltip above/below target

Very small screen:
centered explanation window while preserving the spotlight
```

---

## 19. Important UX Rule — Do Not Explain Everything at Once

The central principle is:

> **Progressive disclosure.**

Initial state:

```text
What are you simulating?
↓
Choose a category
```

After selection:

```text
What scenario?
↓
Configure it
```

After selecting a road:

```text
What is this road?
↓
Inspect / modify it
```

After simulation:

```text
What happened?
↓
Cascade / metrics / explainability
```

The user should never have to read ten cards and eight paragraphs before interacting with the system.

---

## 20. Visual / Typography Changes

Use a modern UI font such as:

**Inter**

Do not use extremely condensed typography.

Increase spacing and line-height.

Reduce unnecessary borders.

Reduce repeated warning icons.

Avoid excessive uppercase text.

Suggested hierarchy:

```text
Major heading:      16–18px / 600
Section heading:    12–13px / 600
Body:               13–14px / 400
Metadata:           10–11px / 400
Metrics:            20–28px / 600
```

The application should feel like a **professional decision-support product**, not a densely packed engineering dashboard.

---

## 21. Default Map State

Set the default map layer to:

```text
Satellite
```

Do not use **Dark Matter** as the initial state because that layer is currently unreliable due to the API issue.

Satellite should be selected automatically when the application loads.

Users can still switch to:

```text
Satellite
Street Map
Dark Matter
```

if the respective layer is available.

---

## 22. Desired User Journey

The entire application should communicate this workflow:

```text
                    START
                      │
                      ▼
              Choose disruption
                      │
                      ▼
             Choose scenario
                      │
                      ▼
           Configure conditions
                      │
                      ▼
              Select / inspect
                  roads
                      │
                      ▼
              Run simulation
                      │
                      ▼
          ┌───────────┴───────────┐
          ▼                       ▼
      What changed?           Why did it happen?
          │                       │
          ▼                       ▼
       Metrics              Causal explanation
          │
          ▼
      Cascade timeline
          │
          ▼
     Compare policies
```

The UI should make this workflow obvious without requiring the user to already understand transportation modelling.
