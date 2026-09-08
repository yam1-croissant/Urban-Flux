#!/usr/bin/env python3
"""UrbanResilience — Part A Demonstration: Traffic Disruption Simulation.

Demonstrates the mathematical response of a major Bangalore arterial corridor
under progressively severe capacity reductions (e.g. roadworks, flooding, lane closures)
comparing peak hour and off-peak conditions.

Scenarios:
1. Baseline (0% reduction)
2. 10% capacity reduction
3. 25% capacity reduction
4. 50% capacity reduction
5. 100% capacity reduction (complete closure)
"""

import math
import os
import sys

# Ensure parent directory is on python path for importing src.simulation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import matplotlib
# Use non-interactive backend for headless execution
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.simulation.traffic_math import evaluate_road_condition


def run_corridor_simulation(
    road_name: str,
    length_km: float,
    free_flow_speed_kmh: float,
    nominal_capacity_veh_per_hr: float,
    scenarios: list[tuple[str, float]],
    demand_profiles: dict[str, float],
):
    """Run simulation across scenarios and demand profiles, printing tables and plotting curves."""
    print("=" * 86)
    print(f" URBANRESILIENCE TRAFFIC SIMULATION: {road_name.upper()}")
    print("=" * 86)
    print(f" Segment Length:    {length_km:.2f} km")
    print(f" Free-flow Speed:   {free_flow_speed_kmh:.1f} km/h")
    print(f" Free-flow Time:    {(length_km / free_flow_speed_kmh) * 60:.2f} minutes")
    print(f" Nominal Capacity:  {nominal_capacity_veh_per_hr:,.0f} vehicles/hour")
    print("=" * 86)

    results_by_profile = {}

    for profile_name, volume in demand_profiles.items():
        print(f"\n--- Demand Profile: {profile_name.upper()} ({volume:,.0f} veh/h) ---")
        header = f"{'Scenario':<22} | {'Eff. Cap (veh/h)':<16} | {'V/C':<8} | {'Travel Time':<13} | {'Per-Veh Delay':<14} | {'Total Delay':<18}"
        print(header)
        print("-" * len(header))

        profile_results = []
        for scenario_label, reduction_ratio in scenarios:
            res = evaluate_road_condition(
                length_km=length_km,
                free_flow_speed_kmh=free_flow_speed_kmh,
                nominal_capacity=nominal_capacity_veh_per_hr,
                volume=volume,
                capacity_reduction_ratio=reduction_ratio,
                unit="minutes",
            )
            profile_results.append((scenario_label, reduction_ratio, res))

            if res.is_closed or math.isinf(res.travel_time):
                time_str = "CLOSED (inf)"
                delay_str = "inf"
                total_delay_str = "inf (impassable)"
                vc_str = "inf"
            else:
                time_str = f"{res.travel_time:.2f} min"
                delay_str = f"{res.delay_per_vehicle:.2f} min"
                total_delay_str = f"{res.total_delay:,.0f} veh-min"
                vc_str = f"{res.vc_ratio:.2f}"

            print(
                f"{scenario_label:<22} | {res.effective_capacity:>16,.0f} | {vc_str:>8} | {time_str:>13} | {delay_str:>14} | {total_delay_str:>18}"
            )

        results_by_profile[profile_name] = profile_results

    return results_by_profile


def generate_plot(
    road_name: str,
    length_km: float,
    free_flow_speed_kmh: float,
    nominal_capacity: float,
    demand_profiles: dict[str, float],
    output_path: str = "examples/disruption_curve.png",
):
    """Generate a high-resolution graph showing travel time explosion as capacity falls."""
    reductions_pct = [r for r in range(0, 95, 2)]  # 0% to 90% (avoid inf at 100% for plotting)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)

    colors = {"Peak Hour (Heavy Demand)": "#d95f02", "Off-Peak (Moderate Demand)": "#1b9e77"}

    for profile_name, volume in demand_profiles.items():
        times = []
        delays = []
        vcs = []
        for r_pct in reductions_pct:
            res = evaluate_road_condition(
                length_km=length_km,
                free_flow_speed_kmh=free_flow_speed_kmh,
                nominal_capacity=nominal_capacity,
                volume=volume,
                capacity_reduction_ratio=r_pct / 100.0,
                unit="minutes",
            )
            times.append(res.travel_time)
            delays.append(res.delay_per_vehicle)
            vcs.append(res.vc_ratio)

        color = colors.get(profile_name, "#7570b3")
        ax1.plot(reductions_pct, times, label=f"{profile_name} (V={volume:,.0f} veh/h)", color=color, linewidth=2)
        ax2.plot(reductions_pct, vcs, label=f"{profile_name}", color=color, linewidth=2, linestyle="--")

    # Left plot: Travel time vs capacity reduction
    ax1.set_title(f"Predicted Travel Time vs Capacity Reduction\n[{road_name}]", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Capacity Reduction (%)", fontsize=10)
    ax1.set_ylabel("Travel Time (minutes)", fontsize=10)
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.axhline((length_km / free_flow_speed_kmh) * 60, color="gray", linestyle=":", label="Free-Flow Time")
    ax1.legend(loc="upper left", fontsize=8)

    # Right plot: V/C Ratio vs capacity reduction
    ax2.set_title(f"Volume/Capacity (V/C) vs Capacity Reduction\n[{road_name}]", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Capacity Reduction (%)", fontsize=10)
    ax2.set_ylabel("V/C Ratio", fontsize=10)
    ax2.axhline(1.0, color="red", linestyle=":", label="Capacity Threshold (V/C = 1.0)")
    ax2.grid(True, linestyle=":", alpha=0.6)
    ax2.legend(loc="upper left", fontsize=8)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    plt.close()
    print(f"\n[Artifact Saved] Demonstration plot written to: {output_path}")


def main():
    # Model parameters for a major Bangalore arterial corridor (Marathahalli Bridge corridor)
    # Length: 2.5 km
    # Free-flow speed: 50 km/h (free-flow time: 3.0 min)
    # Nominal hourly capacity: 2,500 vehicles/hour (derived from Bangalore corridor observations)
    road_name = "Marathahalli Bridge Corridor (Bengaluru)"
    length_km = 2.5
    free_flow_speed_kmh = 50.0
    nominal_capacity = 2500.0

    scenarios = [
        ("Baseline (Normal)", 0.00),
        ("Minor (10% lost)", 0.10),
        ("Moderate (25% lost)", 0.25),
        ("Severe (50% lost)", 0.50),
        ("Closure (100% lost)", 1.00),
    ]

    demand_profiles = {
        "Peak Hour (Heavy Demand)": 2300.0,      # V/C baseline = 0.92
        "Off-Peak (Moderate Demand)": 1100.0,    # V/C baseline = 0.44
    }

    run_corridor_simulation(
        road_name=road_name,
        length_km=length_km,
        free_flow_speed_kmh=free_flow_speed_kmh,
        nominal_capacity_veh_per_hr=nominal_capacity,
        scenarios=scenarios,
        demand_profiles=demand_profiles,
    )

    generate_plot(
        road_name=road_name,
        length_km=length_km,
        free_flow_speed_kmh=free_flow_speed_kmh,
        nominal_capacity=nominal_capacity,
        demand_profiles=demand_profiles,
        output_path="examples/disruption_curve.png",
    )


if __name__ == "__main__":
    main()

