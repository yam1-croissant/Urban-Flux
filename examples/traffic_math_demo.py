"""UrbanFlux — Traffic Mathematics Demonstration.

Demonstrates the response of an illustrative Bangalore arterial road corridor
(Silk Board Junction Corridor) to increasing levels of physical disruption:
  - Baseline (0% reduction)
  - 10% capacity reduction (minor lane encroachment / shoulder blockage)
  - 25% capacity reduction (single lane closure)
  - 50% capacity reduction (major carriageway constriction / waterlogging)
  - 100% capacity reduction (complete road closure / impassable)

Usage:
    python -m examples.traffic_math_demo
    or
    python examples/traffic_math_demo.py
"""

import os
import sys

# Ensure repository root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.simulation.traffic_math import (
    free_flow_time,
    reduced_capacity,
    vc_ratio,
    bpr_travel_time,
    delay_per_vehicle,
    total_delay,
    evaluate_link_disruption,
    RoadClosedError,
)


def run_demonstration():
    print("=" * 84)
    print("   URBANFLUX — PART A: TRAFFIC MATHEMATICS DISRUPTION DEMO")
    print("=" * 84)
    print()

    # --- Scenario Definition ---
    print("--- SCENARIO SPECIFICATION ---")
    print("Corridor / Intersection : Silk Board Junction Corridor (Electronic City)")
    print("Data Source Note        : Observed volume anchored to Kaggle Bangalore Traffic Pulse;")
    print("                          Geometry and physical capacity are explicitly labelled assumptions.")
    print()
    print("Modelling Parameters:")
    print("  • Link Length (L)             : 4.50 km (Assumed corridor segment)")
    print("  • Free-Flow Speed (vf)        : 50.0 km/h (Assumed design speed)")
    print("  • Peak Demand Volume (V)      : 2,400 vehicles/hour (Derived peak-hour flow assumption)")
    print("  • Nominal Capacity (C_nom)    : 3,000 vehicles/hour (Assumed 4-lane arterial capacity)")
    print("  • BPR Function Parameters     : alpha = 0.15, beta = 4.0 (Standard Bureau of Public Roads)")
    print()

    length_km = 4.5
    vf_kmph = 50.0
    volume_vph = 2400.0
    capacity_nom_vph = 3000.0
    alpha = 0.15
    beta = 4.0

    t0_hours = free_flow_time(length_km=length_km, free_flow_speed_kmph=vf_kmph)
    t0_mins = t0_hours * 60.0

    print(f"Free-Flow Travel Time (t_0)   : {t0_hours:.4f} hours ({t0_mins:.2f} minutes)")
    print()

    # --- Disruption Scenarios ---
    scenarios = [
        ("Baseline (0%)", 0.00, "Normal operational capacity"),
        ("Minor (10%)", 0.10, "Shoulder blockage / moderate weather"),
        ("Moderate (25%)", 0.25, "1 lane blocked / roadwork"),
        ("Severe (50%)", 0.50, "2 lanes blocked / flooding / treefall"),
        ("Complete (100%)", 1.00, "Complete closure / structural failure"),
    ]

    print("-" * 84)
    print(f"{'Scenario':<18} | {'Capacity':<10} | {'V/C':<6} | {'Travel Time':<13} | {'Delay/Veh':<12} | {'Total Delay':<14}")
    print(f"{'':<18} | {'(veh/h)':<10} | {'':<6} | {'(mins)':<13} | {'(mins)':<12} | {'(veh-hours)':<14}")
    print("-" * 84)

    results = []
    for name, r, desc in scenarios:
        res = evaluate_link_disruption(
            length_km=length_km,
            free_flow_speed_kmph=vf_kmph,
            volume=volume_vph,
            nominal_capacity=capacity_nom_vph,
            reduction_fraction=r,
            alpha=alpha,
            beta=beta,
        )
        results.append((name, r, res, desc))

        if res.is_closed:
            print(f"{name:<18} | {res.effective_capacity:>10.0f} | {'N/A':>6} | {'CLOSED':>13} | {'N/A':>12} | {'DETOUR REQ.':>14}")
        else:
            print(
                f"{name:<18} | "
                f"{res.effective_capacity:>10.0f} | "
                f"{res.vc_ratio:>6.2f} | "
                f"{res.travel_time_minutes:>13.2f} | "
                f"{res.delay_per_vehicle_minutes:>12.2f} | "
                f"{res.total_delay_veh_hours:>14.1f}"
            )

    print("-" * 84)
    print()

    print("--- OBSERVATIONS & INSIGHTS ---")
    print("1. Non-linear Congestion Growth:")
    print("   At 0% reduction (V/C = 0.80), travel time is 5.73 mins (delay = 0.33 mins).")
    print("   At 25% reduction (V/C = 1.07), capacity is exceeded; travel time jumps to 6.45 mins.")
    print("   At 50% reduction (V/C = 1.60), severe oversaturation yields travel time = 10.71 mins")
    print("   (delay = 5.31 mins per vehicle, accumulating over 212 vehicle-hours of lost time per hour).")
    print("2. Safe Boundary Behavior:")
    print("   At 100% capacity reduction, the model safely handles complete closure without")
    print("   division-by-zero, reporting closure status so network routing engines can detour.")
    print()

    # --- Generate Optional Visualization Plot ---
    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive headless backend
        import matplotlib.pyplot as plt

        reductions_curve = [i / 100.0 for i in range(0, 75)]
        capacities_curve = [reduced_capacity(capacity_nom_vph, r) for r in reductions_curve]
        vc_curve = [vc_ratio(volume_vph, c) for c in capacities_curve]
        tt_mins_curve = [
            bpr_travel_time(t0_hours, volume_vph, c, alpha, beta) * 60.0
            for c in capacities_curve
        ]
        delay_mins_curve = [
            delay_per_vehicle(t / 60.0, t0_hours) * 60.0
            for t in tt_mins_curve
        ]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Subplot 1: Travel Time vs Capacity Reduction
        ax1.plot([r * 100 for r in reductions_curve], tt_mins_curve, color='#c0392b', lw=2.5, label='Predicted Travel Time')
        ax1.axhline(t0_mins, color='#27ae60', linestyle='--', label=f'Free-flow Time ({t0_mins:.1f} min)')
        ax1.set_xlabel('Capacity Reduction (%)', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Travel Time (minutes)', fontsize=11, fontweight='bold')
        ax1.set_title('Travel Time Degradation Under Disruption', fontsize=12, fontweight='bold')
        ax1.grid(True, linestyle=':', alpha=0.6)
        ax1.legend()

        # Subplot 2: V/C Ratio vs Delay per Vehicle
        ax2.plot(vc_curve, delay_mins_curve, color='#2980b9', lw=2.5, label='Delay per Vehicle')
        ax2.axvline(1.0, color='#e67e22', linestyle='--', label='Nominal Capacity Threshold (V/C = 1.0)')
        ax2.set_xlabel('Volume / Capacity (V/C) Ratio', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Delay (minutes / vehicle)', fontsize=11, fontweight='bold')
        ax2.set_title('Congestion Delay vs V/C Ratio', fontsize=12, fontweight='bold')
        ax2.grid(True, linestyle=':', alpha=0.6)
        ax2.legend()

        plt.tight_layout()
        plot_path = os.path.join(REPO_ROOT, 'examples', 'traffic_disruption_curve.png')
        plt.savefig(plot_path, dpi=200)
        plt.close()
        print(f"✓ Demonstration chart successfully saved to: {plot_path}")
    except Exception as exc:
        print(f"Note: Plot generation skipped ({exc}). Console table remains the primary output.")


if __name__ == '__main__':
    run_demonstration()
