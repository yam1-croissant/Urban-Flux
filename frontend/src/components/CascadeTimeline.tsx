import React from "react";
import { SimulationResult } from "../types";
import { AlertCircle, GitFork, Flame, Hospital, Clock } from "lucide-react";

interface CascadeTimelineProps {
  simulationResult: SimulationResult | null;
}

export const CascadeTimeline: React.FC<CascadeTimelineProps> = ({ simulationResult }) => {
  if (!simulationResult || simulationResult.primary_disrupted_edges.length === 0) {
    return (
      <div className="p-5 rounded-2xl bg-[#0F172A]/90 backdrop-blur-xl border border-slate-800 text-center text-slate-500 text-xs">
        <Clock className="w-6 h-6 mx-auto mb-2 text-slate-600" />
        No active cascade events. Trigger a disruption to watch the domino chain propagate.
      </div>
    );
  }

  const primaryEdge = simulationResult.primary_disrupted_edges[0];
  const newlyOverloaded = simulationResult.newly_overloaded_edges;
  const hospitalImpact = simulationResult.critical_service_impacts[0];

  return (
    <div className="flex flex-col bg-[#0F172A]/90 backdrop-blur-xl border border-slate-800 rounded-2xl p-5 shadow-2xl">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 mb-4">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
            Cascade Propagation Timeline
          </h3>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30">
          T+3.0s Chain Complete
        </span>
      </div>

      <div className="relative pl-6 space-y-5 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-gradient-to-b before:from-rose-500 before:via-amber-500 before:to-red-500">
        {/* Step 1: T+0s Primary Event */}
        <div className="relative">
          <span className="absolute -left-[27px] top-0.5 w-3.5 h-3.5 rounded-full bg-rose-500 border-2 border-slate-900 shadow-[0_0_10px_#F43F5E]" />
          <div className="text-[11px] font-mono text-rose-400 font-bold mb-0.5">T+0.0s &bull; PRIMARY FAILURE</div>
          <div className="text-xs font-semibold text-slate-200">
            Physical closure / restriction on <span className="font-mono text-cyan-300">{primaryEdge}</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">Capacity dropped to 0 veh/h. Link excluded from routing graph.</div>
        </div>

        {/* Step 2: T+1s Demand Shift */}
        <div className="relative">
          <span className="absolute -left-[27px] top-0.5 w-3.5 h-3.5 rounded-full bg-cyan-500 border-2 border-slate-900 shadow-[0_0_10px_#06B6D4]" />
          <div className="text-[11px] font-mono text-cyan-400 font-bold mb-0.5">T+1.2s &bull; TRAFFIC DIVERSION</div>
          <div className="text-xs font-semibold text-slate-200">
            {simulationResult.changed_routes.length > 0 ? (
              <>
                <span className="text-cyan-300 font-bold">{Math.round(simulationResult.changed_routes[0].demand_veh_per_hour)} veh/h</span> rerouted to alternate residential corridors
              </>
            ) : "Vehicles rerouting to parallel paths"}
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">Traffic diverted via Agara and Koramangala 80ft collector road.</div>
        </div>

        {/* Step 3: T+2s Secondary Overload */}
        <div className="relative">
          <span className="absolute -left-[27px] top-0.5 w-3.5 h-3.5 rounded-full bg-amber-500 border-2 border-slate-900 shadow-[0_0_10px_#F59E0B]" />
          <div className="text-[11px] font-mono text-amber-400 font-bold mb-0.5">T+2.1s &bull; SECONDARY OVERLOAD</div>
          <div className="text-xs font-semibold text-slate-200">
            {newlyOverloaded.length > 0 ? (
              <>
                Bottleneck saturation on <span className="font-mono text-amber-300">{newlyOverloaded.join(", ")}</span>
              </>
            ) : "Parallel corridors operating at elevated load"}
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">Flow surged past nominal capacity (V/C &gt; 1.0), triggering steep BPR delay escalation.</div>
        </div>

        {/* Step 4: T+3s Critical Service Access Loss */}
        <div className="relative">
          <span className="absolute -left-[27px] top-0.5 w-3.5 h-3.5 rounded-full bg-red-600 border-2 border-slate-900 shadow-[0_0_10px_#DC2626]" />
          <div className="text-[11px] font-mono text-red-400 font-bold mb-0.5">T+3.0s &bull; CRITICAL SERVICE ACCESS PENALTY</div>
          <div className="text-xs font-semibold text-slate-200">
            {hospitalImpact ? (
              <>
                Hospital transit delay: <span className="text-rose-400 font-bold">+{hospitalImpact.response_time_delta_minutes?.toFixed(1)} mins</span> ({hospitalImpact.baseline_access_time_minutes?.toFixed(1)} &rarr; {hospitalImpact.scenario_access_time_minutes?.toFixed(1)} min)
              </>
            ) : "Emergency accessibility degraded across sector"}
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">Emergency ambulances and patients trapped in secondary congestion.</div>
        </div>
      </div>
    </div>
  );
};
