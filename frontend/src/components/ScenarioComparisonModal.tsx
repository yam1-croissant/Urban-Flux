import React from "react";
import { ComparisonResult } from "../types";
import { X, Scale, ArrowRight, ShieldCheck, AlertTriangle, TrendingDown } from "lucide-react";

interface ScenarioComparisonModalProps {
  isOpen: boolean;
  onClose: () => void;
  comparison: ComparisonResult | null;
}

export const ScenarioComparisonModal: React.FC<ScenarioComparisonModalProps> = ({
  isOpen,
  onClose,
  comparison,
}) => {
  if (!isOpen || !comparison) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-[#0F172A] border border-slate-700 w-full max-w-3xl rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-cyan-500/10 rounded-lg border border-cyan-500/30">
              <Scale className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                Scenario Policy Comparison
              </h2>
              <p className="text-xs text-slate-400">Evaluate Trade-Offs & Mitigation ROI</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6">
          {/* Main Hero Highlight Box */}
          <div className="p-5 rounded-xl bg-gradient-to-r from-emerald-950/40 via-cyan-950/30 to-blue-950/40 border border-emerald-500/40 text-center">
            <div className="text-xs uppercase tracking-widest font-bold text-emerald-400 mb-1 flex items-center justify-center gap-1.5">
              <TrendingDown className="w-4 h-4" />
              Quantifiable Resilience Verdict
            </div>
            <div className="text-2xl font-black text-white font-mono tracking-tight">
              {comparison.summary_verdict}
            </div>
            <div className="text-xs text-slate-300 mt-2 max-w-lg mx-auto">
              Dynamic police green-wave routing on northern relief bypass reduced system delay by{" "}
              <span className="text-emerald-300 font-bold font-mono">{comparison.percentage_improvement.toFixed(1)}%</span>.
            </div>
          </div>

          {/* Side-by-Side Cards */}
          <div className="grid grid-cols-2 gap-4">
            {/* Scenario A: No Action */}
            <div className="p-5 rounded-xl bg-slate-900/90 border border-rose-500/30 space-y-3">
              <div className="flex items-center gap-2 text-rose-400 font-bold text-xs uppercase tracking-wider">
                <AlertTriangle className="w-4 h-4" />
                Scenario A: Unmitigated Crisis
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between py-1.5 border-b border-slate-800">
                  <span className="text-slate-400">System Delay:</span>
                  <span className="font-mono font-bold text-rose-400">+{comparison.scenario_a_metrics.total_delay_change_veh_h.toFixed(1)} veh-h</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-800">
                  <span className="text-slate-400">Overloaded Bottlenecks:</span>
                  <span className="font-mono font-bold text-rose-400">{comparison.scenario_a_metrics.newly_overloaded_count} corridors</span>
                </div>
                <div className="flex justify-between py-1.5">
                  <span className="text-slate-400">Hospital Transit Delta:</span>
                  <span className="font-mono font-bold text-rose-400">+17.0 minutes</span>
                </div>
              </div>
            </div>

            {/* Scenario B: Active Mitigation */}
            <div className="p-5 rounded-xl bg-slate-900/90 border border-emerald-500/30 space-y-3">
              <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs uppercase tracking-wider">
                <ShieldCheck className="w-4 h-4" />
                Scenario B: Active Mitigation
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between py-1.5 border-b border-slate-800">
                  <span className="text-slate-400">System Delay:</span>
                  <span className="font-mono font-bold text-emerald-400">+{comparison.scenario_b_metrics.total_delay_change_veh_h.toFixed(1)} veh-h</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-800">
                  <span className="text-slate-400">Overloaded Bottlenecks:</span>
                  <span className="font-mono font-bold text-emerald-400">{comparison.scenario_b_metrics.newly_overloaded_count} corridors</span>
                </div>
                <div className="flex justify-between py-1.5">
                  <span className="text-slate-400">Hospital Transit Delta:</span>
                  <span className="font-mono font-bold text-emerald-400">+2.5 minutes</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-950/60 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold transition-colors"
          >
            Close Comparison
          </button>
        </div>
      </div>
    </div>
  );
};
