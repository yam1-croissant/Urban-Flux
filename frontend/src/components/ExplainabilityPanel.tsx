import React from "react";
import { SimulationResult } from "../types";
import { HelpCircle, CheckCircle2, ChevronRight, Lightbulb } from "lucide-react";

interface ExplainabilityPanelProps {
  simulationResult: SimulationResult | null;
}

export const ExplainabilityPanel: React.FC<ExplainabilityPanelProps> = ({ simulationResult }) => {
  const explainability = simulationResult?.explainability || [
    "The city network is operating under nominal baseline flow conditions with standard capacity.",
    "No active structural disruptions or extreme weather events are restricting throughput."
  ];

  return (
    <div className="flex flex-col bg-[#0F172A]/90 backdrop-blur-xl border border-slate-800 rounded-2xl p-5 shadow-2xl">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 mb-4">
        <div className="flex items-center gap-2">
          <HelpCircle className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
            Causal Explainability Engine
          </h3>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
          Deterministic BPR Logic
        </span>
      </div>

      <div className="space-y-3">
        {explainability.map((step, idx) => (
          <div
            key={idx}
            className="flex items-start gap-3 p-3 rounded-xl bg-slate-900/80 border border-slate-800/80 text-xs text-slate-300 leading-relaxed group hover:border-slate-700 transition-colors"
          >
            <div className="p-1 rounded bg-slate-800 text-cyan-400 font-mono font-bold text-[11px] shrink-0 mt-0.5">
              0{idx + 1}
            </div>
            <div className="flex-1">
              {step}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
