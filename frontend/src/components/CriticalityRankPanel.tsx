import React from "react";
import { EdgeData, SimulationResult } from "../types";
import { ShieldAlert, ChevronRight, Activity } from "lucide-react";

interface CriticalityRankPanelProps {
  edges: EdgeData[];
  simulationResult: SimulationResult | null;
  onSelectEdge: (edgeId: string) => void;
}

export const CriticalityRankPanel: React.FC<CriticalityRankPanelProps> = ({
  edges,
  simulationResult,
  onSelectEdge,
}) => {
  // Compute illustrative multi-criteria criticality score for each edge
  const rankedEdges = edges
    .map((e) => {
      const evalData = simulationResult?.scenario_edges[e.id];
      const isHospitalRoute = e.id.includes("Bridge") || e.id.includes("Hospital") || e.id.includes("Bottleneck");
      const vc = evalData?.vc_ratio || (e.baseline_flow_veh_per_hour / e.nominal_capacity_veh_per_hour);
      
      // Criticality formula: Flow stress (40%) + Hospital dependency (35%) + Bottleneck risk (25%)
      const score = Math.min(1.0, (vc * 0.45) + (isHospitalRoute ? 0.35 : 0.05) + (e.nominal_capacity_veh_per_hour < 1600 ? 0.20 : 0.10));
      return { edge: e, score, vc };
    })
    .sort((a, b) => b.score - a.score);

  return (
    <div className="flex flex-col bg-[#0F172A]/90 backdrop-blur-xl border border-slate-800 rounded-2xl p-5 shadow-2xl">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 mb-4">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
            Criticality & Vulnerability Ranking
          </h3>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
          A Priori Stress Score
        </span>
      </div>

      <div className="space-y-2.5">
        {rankedEdges.slice(0, 5).map(({ edge, score, vc }, idx) => (
          <div
            key={edge.id}
            onClick={() => onSelectEdge(edge.id)}
            className="p-3 rounded-xl bg-slate-900/80 hover:bg-slate-850 border border-slate-800 hover:border-cyan-500/40 cursor-pointer transition-all flex items-center justify-between group"
          >
            <div className="flex items-center gap-3">
              <span className="w-5 text-center font-mono font-bold text-xs text-slate-500 group-hover:text-cyan-400">
                0{idx + 1}
              </span>
              <div>
                <div className="text-xs font-bold text-slate-200 group-hover:text-cyan-300 transition-colors">
                  {edge.name || edge.id}
                </div>
                <div className="text-[10px] text-slate-400">
                  {edge.nominal_capacity_veh_per_hour} veh/h &bull; V/C: {(vc).toFixed(2)}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="w-20 bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${
                    score > 0.75 ? "bg-rose-500 shadow-[0_0_8px_#F43F5E]" : (score > 0.5 ? "bg-amber-500" : "bg-emerald-500")
                  }`}
                  style={{ width: `${Math.round(score * 100)}%` }}
                />
              </div>
              <span className="font-mono text-xs font-bold text-slate-300 w-9 text-right">
                {score.toFixed(2)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
