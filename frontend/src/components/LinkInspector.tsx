import {
    AlertTriangle,
    CheckCircle2,
    CloudRain,
    Construction,
    Gauge,
    Route,
    SlidersHorizontal,
    X
} from "lucide-react";
import React from "react";
import { DisruptionInput, EdgeData, EdgeEvaluation } from "../types";

interface LinkInspectorProps {
  edge: EdgeData | null;
  activeDisruptions: DisruptionInput[];
  edgeEval?: EdgeEvaluation;
  onUpdateDisruption: (
    assetId: string,
    multiplier: number,
    type?: "closure" | "partial_closure" | "weather" | "construction"
  ) => void;
  onClose: () => void;
}

export const LinkInspector: React.FC<LinkInspectorProps> = ({
  edge,
  activeDisruptions,
  edgeEval,
  onUpdateDisruption,
  onClose,
}) => {
  if (!edge) return null;

  const currentDisruption = activeDisruptions.find((d) => d.asset_id === edge.id);
  const currentMultiplier = currentDisruption ? currentDisruption.capacity_multiplier : 1.0;
  const currentType = currentDisruption?.disruption_type || "closure";

  const effectiveCapacity = Math.round(edge.nominal_capacity_veh_per_hour * currentMultiplier);
  const currentFlow = edgeEval?.current_flow_veh_per_hour ?? edge.baseline_flow_veh_per_hour;
  const vcRatio = edgeEval?.vc_ratio ?? (effectiveCapacity > 0 ? currentFlow / effectiveCapacity : 0);

  const getVcBadge = (vc: number) => {
    if (currentMultiplier === 0) {
      return { label: "CLOSED", color: "bg-red-500/20 text-red-400 border-red-500/40" };
    }
    if (vc > 1.0) {
      return { label: `V/C ${(vc).toFixed(2)} • OVERLOADED`, color: "bg-rose-500/20 text-rose-300 border-rose-500/40" };
    }
    if (vc > 0.75) {
      return { label: `V/C ${(vc).toFixed(2)} • STRESSED`, color: "bg-amber-500/20 text-amber-300 border-amber-500/40" };
    }
    return { label: `V/C ${(vc).toFixed(2)} • OPTIMAL`, color: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40" };
  };

  const vcBadge = getVcBadge(vcRatio);

  return (
    <div
      id="tour-link-inspector"
      className="bg-[#0F172A]/95 backdrop-blur-xl border border-cyan-500/30 rounded-2xl p-4 shadow-2xl transition-all duration-300 animate-in fade-in slide-in-from-top-4"
    >
      {/* Top Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <Route className="w-4 h-4" />
          </div>
          <div>
            <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider block">
              Link Inspector
            </span>
            <span className="text-xs font-mono font-bold text-white truncate block max-w-[160px]">
              {edge.id}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border ${vcBadge.color}`}>
            {vcBadge.label}
          </span>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
            title="Deselect Road"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Road Metadata Overview */}
      <div className="mb-3.5">
        <h3 className="text-sm font-bold text-slate-100 leading-tight">
          {edge.name || edge.id}
        </h3>
        <p className="text-[11px] text-slate-400 capitalize mt-0.5 flex items-center gap-1.5">
          <span>{edge.road_class.replace(/_/g, " ")}</span>
          <span>•</span>
          <span>{edge.length_km} km</span>
          <span>•</span>
          <span>{edge.free_flow_speed_kmph} km/h free flow</span>
        </p>
      </div>

      {/* Numerical Stats Grid */}
      <div className="grid grid-cols-3 gap-2 mb-3.5 text-xs">
        <div className="p-2 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-[9px] font-semibold text-slate-400 uppercase tracking-wider block">Nominal</span>
          <span className="text-xs font-mono font-bold text-slate-200">
            {edge.nominal_capacity_veh_per_hour}
          </span>
          <span className="text-[9px] text-slate-400 block">veh/h</span>
        </div>
        <div className="p-2 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-[9px] font-semibold text-slate-400 uppercase tracking-wider block">Available</span>
          <span className={`text-xs font-mono font-bold ${currentMultiplier === 0 ? "text-rose-400" : "text-cyan-300"}`}>
            {effectiveCapacity}
          </span>
          <span className="text-[9px] text-slate-400 block">veh/h</span>
        </div>
        <div className="p-2 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-[9px] font-semibold text-slate-400 uppercase tracking-wider block">Flow</span>
          <span className="text-xs font-mono font-bold text-slate-200">
            {Math.round(currentFlow)}
          </span>
          <span className="text-[9px] text-slate-400 block">veh/h</span>
        </div>
      </div>

      {/* Interactive Road Condition Controls */}
      <div id="tour-road-controls" className="space-y-3 pt-2 border-t border-slate-800/80">
        {/* Capacity Slider */}
        <div>
          <div className="flex justify-between items-center text-xs mb-1.5">
            <span className="text-slate-300 font-medium flex items-center gap-1.5 text-[11px]">
              <SlidersHorizontal className="w-3.5 h-3.5 text-cyan-400" />
              Available Road Capacity:
            </span>
            <span className="font-mono font-bold text-cyan-400 text-xs">
              {Math.round(currentMultiplier * 100)}% ({effectiveCapacity} veh/h)
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={currentMultiplier}
            onChange={(e) => onUpdateDisruption(edge.id, parseFloat(e.target.value), currentType)}
            className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
          />
        </div>

        {/* Quick Closure Preset Buttons */}
        <div>
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1.5">
            Closure Percentage
          </span>
          <div className="grid grid-cols-5 gap-1.5">
            {[
              { label: "0% (Shut)", mult: 0.0, color: "hover:border-rose-500 hover:text-rose-300" },
              { label: "25%", mult: 0.25, color: "hover:border-amber-500 hover:text-amber-300" },
              { label: "50%", mult: 0.5, color: "hover:border-amber-500 hover:text-amber-300" },
              { label: "75%", mult: 0.75, color: "hover:border-cyan-500 hover:text-cyan-300" },
              { label: "100%", mult: 1.0, color: "hover:border-emerald-500 hover:text-emerald-300" },
            ].map((p) => {
              const isSelected = Math.abs(currentMultiplier - p.mult) < 0.03;
              return (
                <button
                  key={p.mult}
                  onClick={() => onUpdateDisruption(edge.id, p.mult, currentType)}
                  className={`py-1 text-[10px] font-mono rounded-lg border transition-all ${
                    isSelected
                      ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/60 font-bold shadow-[0_0_8px_rgba(6,182,212,0.3)]"
                      : "bg-slate-900 text-slate-400 border-slate-800 " + p.color
                  }`}
                >
                  {p.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Disruption Type / Intensity Pills */}
        <div>
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1.5">
            Disruption Cause
          </span>
          <div className="grid grid-cols-2 gap-1.5">
            {[
              { type: "closure" as const, label: "Structural Closure", icon: AlertTriangle, color: "text-rose-400" },
              { type: "weather" as const, label: "Monsoon Flood", icon: CloudRain, color: "text-cyan-400" },
              { type: "construction" as const, label: "Metro Work", icon: Construction, color: "text-amber-400" },
              { type: "partial_closure" as const, label: "Lane Reduction", icon: Gauge, color: "text-indigo-400" },
            ].map((item) => {
              const Icon = item.icon;
              const isSelected = currentType === item.type && currentMultiplier < 1.0;
              return (
                <button
                  key={item.type}
                  onClick={() => onUpdateDisruption(edge.id, currentMultiplier === 1.0 ? 0.5 : currentMultiplier, item.type)}
                  className={`flex items-center gap-1.5 p-1.5 rounded-lg text-[11px] border transition-all text-left ${
                    isSelected
                      ? "bg-slate-800 text-white border-cyan-500/60 shadow-[0_0_10px_rgba(6,182,212,0.2)] font-semibold"
                      : "bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-slate-200"
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 shrink-0 ${item.color}`} />
                  <span className="truncate">{item.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Quick Action Buttons */}
        <div className="grid grid-cols-2 gap-2 pt-1">
          <button
            onClick={() => onUpdateDisruption(edge.id, 0.0, "closure")}
            className="px-3 py-1.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-semibold transition-colors flex items-center justify-center gap-1.5"
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            Close 100%
          </button>
          <button
            onClick={() => onUpdateDisruption(edge.id, 1.0)}
            className="px-3 py-1.5 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-semibold transition-colors flex items-center justify-center gap-1.5"
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            Restore 100%
          </button>
        </div>
      </div>
    </div>
  );
};

