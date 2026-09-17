import { AlertOctagon, Clock, Hospital, TrendingUp } from "lucide-react";
import React from "react";
import { SimulationResult } from "../types";

interface ImpactDashboardProps {
  simulationResult: SimulationResult | null;
}

export const ImpactDashboard: React.FC<ImpactDashboardProps> = ({ simulationResult }) => {
  const totalDelayVehHours = simulationResult?.total_delay_change_vehicle_hours || 0.0;
  const travelTimeChangeMin = simulationResult?.total_travel_time_change_minutes || 0.0;
  const newlyOverloadedCount = simulationResult?.newly_overloaded_edges.length || 0;
  const hospitalImpact = simulationResult?.critical_service_impacts[0];
  const hospitalDelta = hospitalImpact?.response_time_delta_minutes || 0.0;

  return (
    <div id="tour-key-metrics" className="grid grid-cols-2 md:grid-cols-4 gap-3 w-full">
      {/* Metric 1: Aggregate System Delay */}
      <div className="p-3.5 rounded-2xl bg-[#0F172A]/90 backdrop-blur-xl border border-slate-800 shadow-xl relative overflow-hidden group hover:border-slate-700 transition-all">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="font-semibold uppercase tracking-wider text-[11px] text-slate-400">
            Net System Delay
          </span>
          <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400">
            <Clock className="w-3.5 h-3.5" />
          </div>
        </div>
        <div className="flex items-baseline gap-1.5 mt-0.5">
          <span
            className={`text-2xl font-bold font-mono tracking-tight ${
              totalDelayVehHours > 0 ? "text-cyan-300" : "text-slate-200"
            }`}
          >
            {totalDelayVehHours > 0 ? `+${totalDelayVehHours.toFixed(1)}` : "0.0"}
          </span>
          <span className="text-xs text-slate-400 font-medium">veh-hours</span>
        </div>
        <p className="text-[11px] text-slate-400 mt-1 truncate">
          {totalDelayVehHours > 0 ? (
            <span className="text-cyan-400 font-medium">Lost commuter throughput</span>
          ) : (
            <span className="text-emerald-400 font-medium">Nominal baseline flow</span>
          )}
        </p>
      </div>

      {/* Metric 2: Hospital Access Delay */}
      <div className="p-3.5 rounded-2xl bg-[#0F172A]/90 backdrop-blur-xl border border-slate-800 shadow-xl relative overflow-hidden group hover:border-slate-700 transition-all">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="font-semibold uppercase tracking-wider text-[11px] text-slate-400">
            Hospital Access
          </span>
          <div className="p-1.5 rounded-lg bg-rose-500/10 text-rose-400">
            <Hospital className="w-3.5 h-3.5" />
          </div>
        </div>
        <div className="flex items-baseline gap-1.5 mt-0.5">
          <span
            className={`text-2xl font-bold font-mono tracking-tight ${
              hospitalDelta > 0 ? "text-rose-400" : "text-emerald-400"
            }`}
          >
            {hospitalDelta > 0 ? `+${hospitalDelta.toFixed(1)}` : "0.0"}
          </span>
          <span className="text-xs text-slate-400 font-medium">min delay</span>
        </div>
        <p className="text-[11px] text-slate-400 mt-1 truncate">
          {hospitalDelta > 0 ? (
            <span className="text-rose-400 font-medium font-mono">
              {hospitalImpact?.baseline_access_time_minutes?.toFixed(1)} &rarr;{" "}
              {hospitalImpact?.scenario_access_time_minutes?.toFixed(1)} min access
            </span>
          ) : (
            <span className="text-emerald-400 font-medium">Full emergency corridor access</span>
          )}
        </p>
      </div>

      {/* Metric 3: Newly Overloaded Links */}
      <div className="p-3.5 rounded-2xl bg-[#0F172A]/90 backdrop-blur-xl border border-slate-800 shadow-xl relative overflow-hidden group hover:border-slate-700 transition-all">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="font-semibold uppercase tracking-wider text-[11px] text-slate-400">
            Cascade Overloads
          </span>
          <div className="p-1.5 rounded-lg bg-amber-500/10 text-amber-400">
            <AlertOctagon className="w-3.5 h-3.5" />
          </div>
        </div>
        <div className="flex items-baseline gap-1.5 mt-0.5">
          <span
            className={`text-2xl font-bold font-mono tracking-tight ${
              newlyOverloadedCount > 0 ? "text-amber-400" : "text-slate-200"
            }`}
          >
            {newlyOverloadedCount}
          </span>
          <span className="text-xs text-slate-400 font-medium">corridors</span>
        </div>
        <p className="text-[11px] text-slate-400 mt-1 truncate">
          {newlyOverloadedCount > 0 ? (
            <span className="text-amber-400 font-medium">Secondary V/C &gt; 1.0 bottlenecks</span>
          ) : (
            <span className="text-slate-400">No secondary choke points</span>
          )}
        </p>
      </div>

      {/* Metric 4: Total User Travel Time Change */}
      <div className="p-3.5 rounded-2xl bg-[#0F172A]/90 backdrop-blur-xl border border-slate-800 shadow-xl relative overflow-hidden group hover:border-slate-700 transition-all">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="font-semibold uppercase tracking-wider text-[11px] text-slate-400">
            Net Trip Time Change
          </span>
          <div className="p-1.5 rounded-lg bg-blue-500/10 text-blue-400">
            <TrendingUp className="w-3.5 h-3.5" />
          </div>
        </div>
        <div className="flex items-baseline gap-1.5 mt-0.5">
          <span
            className={`text-2xl font-bold font-mono tracking-tight ${
              travelTimeChangeMin > 0 ? "text-blue-300" : "text-slate-200"
            }`}
          >
            {travelTimeChangeMin > 0 ? `+${travelTimeChangeMin.toFixed(1)}` : "0.0"}
          </span>
          <span className="text-xs text-slate-400 font-medium">minutes</span>
        </div>
        <p className="text-[11px] text-slate-400 mt-1 truncate">
          {travelTimeChangeMin > 0 ? (
            <span className="text-blue-400 font-medium">Aggregated across all OD routes</span>
          ) : (
            <span className="text-slate-400">Zero detour overhead</span>
          )}
        </p>
      </div>
    </div>
  );
};
