import React from "react";
import { SimulationResult } from "../types";
import { Clock, AlertOctagon, Hospital, TrendingUp, ShieldAlert, Activity } from "lucide-react";

interface ImpactDashboardProps {
  simulationResult: SimulationResult | null;
}

export const ImpactDashboard: React.FC<ImpactDashboardProps> = ({ simulationResult }) => {
  const isBaseline = !simulationResult || simulationResult.primary_disrupted_edges.length === 0;

  const totalDelayVehHours = simulationResult?.total_delay_change_vehicle_hours || 0.0;
  const travelTimeChangeMin = simulationResult?.total_travel_time_change_minutes || 0.0;
  const newlyOverloadedCount = simulationResult?.newly_overloaded_edges.length || 0;
  const hospitalImpact = simulationResult?.critical_service_impacts[0];
  const hospitalDelta = hospitalImpact?.response_time_delta_minutes || 0.0;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {/* Metric 1: Aggregate System Delay */}
      <div className="p-4 rounded-2xl bg-[#0F172A]/90 backdrop-blur-xl border border-slate-800 shadow-xl relative overflow-hidden group hover:border-slate-700 transition-all">
        <div className="flex items-center justify-between text-slate-400 text-xs mb-1.5">
          <span className="font-semibold uppercase tracking-wider text-[10px]">Net System Delay</span>
          <Clock className="w-4 h-4 text-cyan-400" />
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className={`text-2xl font-extrabold font-mono tracking-tight ${totalDelayVehHours > 0 ? "text-cyan-300" : "text-slate-200"}`}>
            {totalDelayVehHours > 0 ? `+${totalDelayVehHours.toFixed(1)}` : "0.0"}
          </span>
          <span className="text-xs text-slate-400">veh-hours</span>
        </div>
        <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
          {totalDelayVehHours > 0 ? (
            <span className="text-cyan-400 font-medium">Lost commuter productivity</span>
          ) : (
            <span className="text-emerald-400 font-medium">Nominal baseline state</span>
          )}
        </div>
      </div>

      {/* Metric 2: Hospital Access Delay */}
      <div className="p-4 rounded-2xl bg-[#0F172A]/90 backdrop-blur-xl border border-slate-800 shadow-xl relative overflow-hidden group hover:border-slate-700 transition-all">
        <div className="flex items-center justify-between text-slate-400 text-xs mb-1.5">
          <span className="font-semibold uppercase tracking-wider text-[10px]">Hospital Access Delay</span>
          <Hospital className="w-4 h-4 text-rose-400" />
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className={`text-2xl font-extrabold font-mono tracking-tight ${hospitalDelta > 0 ? "text-rose-400" : "text-emerald-400"}`}>
            {hospitalDelta > 0 ? `+${hospitalDelta.toFixed(1)}` : "0.0"}
          </span>
          <span className="text-xs text-slate-400">min/trip</span>
        </div>
        <div className="text-[11px] text-slate-400 mt-1 truncate">
          {hospitalDelta > 0 ? (
            <span className="text-rose-400 font-medium font-mono">{hospitalImpact?.baseline_access_time_minutes?.toFixed(1)} &rarr; {hospitalImpact?.scenario_access_time_minutes?.toFixed(1)} min</span>
          ) : (
            <span className="text-emerald-400 font-medium">Full emergency access</span>
          )}
        </div>
      </div>

      {/* Metric 3: Newly Overloaded Links */}
      <div className="p-4 rounded-2xl bg-[#0F172A]/90 backdrop-blur-xl border border-slate-800 shadow-xl relative overflow-hidden group hover:border-slate-700 transition-all">
        <div className="flex items-center justify-between text-slate-400 text-xs mb-1.5">
          <span className="font-semibold uppercase tracking-wider text-[10px]">Cascade Overloads</span>
          <AlertOctagon className="w-4 h-4 text-amber-400" />
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className={`text-2xl font-extrabold font-mono tracking-tight ${newlyOverloadedCount > 0 ? "text-amber-400" : "text-slate-200"}`}>
            {newlyOverloadedCount}
          </span>
          <span className="text-xs text-slate-400">corridors</span>
        </div>
        <div className="text-[11px] text-slate-400 mt-1">
          {newlyOverloadedCount > 0 ? (
            <span className="text-amber-400 font-medium">V/C &gt; 1.0 secondary failure</span>
          ) : (
            <span className="text-slate-400">No secondary bottlenecks</span>
          )}
        </div>
      </div>

      {/* Metric 4: Total User Travel Time Change */}
      <div className="p-4 rounded-2xl bg-[#0F172A]/90 backdrop-blur-xl border border-slate-800 shadow-xl relative overflow-hidden group hover:border-slate-700 transition-all">
        <div className="flex items-center justify-between text-slate-400 text-xs mb-1.5">
          <span className="font-semibold uppercase tracking-wider text-[10px]">Net Trip Time Change</span>
          <TrendingUp className="w-4 h-4 text-blue-400" />
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className={`text-2xl font-extrabold font-mono tracking-tight ${travelTimeChangeMin > 0 ? "text-blue-300" : "text-slate-200"}`}>
            {travelTimeChangeMin > 0 ? `+${travelTimeChangeMin.toFixed(1)}` : "0.0"}
          </span>
          <span className="text-xs text-slate-400">minutes</span>
        </div>
        <div className="text-[11px] text-slate-400 mt-1">
          {travelTimeChangeMin > 0 ? (
            <span className="text-blue-400 font-medium">Accumulated across OD trips</span>
          ) : (
            <span className="text-slate-400">Zero detour overhead</span>
          )}
        </div>
      </div>
    </div>
  );
};
