import React from "react";
import { EdgeData, ScenarioPreset, DisruptionInput, SimulationResult } from "../types";
import { AlertTriangle, CloudRain, Construction, ShieldCheck, Play, RotateCcw, Scale, Zap, Sliders } from "lucide-react";

interface DisruptionStudioProps {
  edges: EdgeData[];
  presets: ScenarioPreset[];
  selectedEdge: EdgeData | null;
  activeDisruptions: DisruptionInput[];
  isSimulating: boolean;
  onApplyPreset: (preset: ScenarioPreset) => void;
  onUpdateDisruption: (assetId: string, multiplier: number, type?: "closure" | "partial_closure" | "weather" | "construction") => void;
  onRunSimulation: () => void;
  onResetSimulation: () => void;
  onOpenCompare: () => void;
}

export const DisruptionStudio: React.FC<DisruptionStudioProps> = ({
  edges,
  presets,
  selectedEdge,
  activeDisruptions,
  isSimulating,
  onApplyPreset,
  onUpdateDisruption,
  onRunSimulation,
  onResetSimulation,
  onOpenCompare,
}) => {
  const currentDisruption = selectedEdge
    ? activeDisruptions.find((d) => d.asset_id === selectedEdge.id)
    : null;

  const currentMultiplier = currentDisruption ? currentDisruption.capacity_multiplier : 1.0;

  const getPresetIcon = (iconName: string) => {
    switch (iconName) {
      case "CloudRain": return <CloudRain className="w-4 h-4 text-cyan-400" />;
      case "Construction": return <Construction className="w-4 h-4 text-amber-400" />;
      case "ShieldCheck": return <ShieldCheck className="w-4 h-4 text-emerald-400" />;
      default: return <AlertTriangle className="w-4 h-4 text-rose-400" />;
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#0F172A]/90 backdrop-blur-xl border border-slate-800 rounded-2xl p-5 shadow-2xl overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800/80 mb-5">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-cyan-500/10 rounded-lg border border-cyan-500/30">
            <Sliders className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white tracking-wide uppercase">Disruption Studio</h2>
            <p className="text-xs text-slate-400">Configure Acute Events & Cascades</p>
          </div>
        </div>
        <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
          {activeDisruptions.length} Active
        </span>
      </div>

      {/* Preset Scenarios */}
      <div className="mb-6">
        <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2.5">
          Scenario Presets
        </label>
        <div className="grid grid-cols-1 gap-2">
          {presets.map((p) => (
            <button
              key={p.id}
              onClick={() => onApplyPreset(p)}
              className="flex items-start gap-3 p-3 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 hover:border-cyan-500/50 transition-all text-left group"
            >
              <div className="p-2 rounded-lg bg-slate-900 border border-slate-700 group-hover:border-cyan-500/40 shrink-0">
                {getPresetIcon(p.icon)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs font-semibold text-slate-200 group-hover:text-cyan-300 transition-colors truncate">
                  {p.name}
                </div>
                <div className="text-[11px] text-slate-400 line-clamp-2 mt-0.5 leading-relaxed">
                  {p.description}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Selected Edge Inspector */}
      <div className="mb-6 p-4 rounded-xl bg-slate-900/90 border border-slate-800 flex-1">
        <div className="flex items-center justify-between mb-3">
          <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Link Inspector
          </label>
          {selectedEdge && (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
              {selectedEdge.id}
            </span>
          )}
        </div>

        {selectedEdge ? (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-bold text-slate-100">{selectedEdge.name || selectedEdge.id}</h3>
              <p className="text-xs text-slate-400 capitalize">{selectedEdge.road_class.replace("_", " ")} &bull; {selectedEdge.length_km} km</p>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2.5 rounded-lg bg-slate-800/80 border border-slate-700/50">
                <span className="text-[10px] text-slate-400 uppercase block">Nominal Cap</span>
                <span className="text-xs font-bold text-slate-200">{selectedEdge.nominal_capacity_veh_per_hour} veh/h</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-800/80 border border-slate-700/50">
                <span className="text-[10px] text-slate-400 uppercase block">Free-Flow Speed</span>
                <span className="text-xs font-bold text-slate-200">{selectedEdge.free_flow_speed_kmph} km/h</span>
              </div>
            </div>

            {/* Capacity Slider */}
            <div>
              <div className="flex justify-between items-center text-xs mb-1.5">
                <span className="text-slate-300 font-medium">Available Capacity:</span>
                <span className="font-mono font-bold text-cyan-400">
                  {Math.round(currentMultiplier * 100)}% ({Math.round(selectedEdge.nominal_capacity_veh_per_hour * currentMultiplier)} veh/h)
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={currentMultiplier}
                onChange={(e) => onUpdateDisruption(selectedEdge.id, parseFloat(e.target.value))}
                className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-cyan-400"
              />
            </div>

            {/* Quick Action Buttons */}
            <div className="grid grid-cols-2 gap-2 pt-1">
              <button
                onClick={() => onUpdateDisruption(selectedEdge.id, 0.0, "closure")}
                className="px-3 py-2 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-semibold transition-colors flex items-center justify-center gap-1.5"
              >
                <AlertTriangle className="w-3.5 h-3.5" />
                Close 100%
              </button>
              <button
                onClick={() => onUpdateDisruption(selectedEdge.id, 1.0)}
                className="px-3 py-2 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-semibold transition-colors flex items-center justify-center gap-1.5"
              >
                Restore 100%
              </button>
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-slate-500 text-xs">
            <Zap className="w-8 h-8 mx-auto mb-2 text-slate-600 animate-pulse" />
            Click on any road link on the map to inspect properties or apply custom disruptions.
          </div>
        )}
      </div>

      {/* Main Execution Controls */}
      <div className="space-y-2.5 pt-2 border-t border-slate-800/80">
        <button
          onClick={onRunSimulation}
          disabled={isSimulating}
          className="w-full py-3.5 px-4 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-sm tracking-wide transition-all shadow-[0_0_20px_rgba(6,182,212,0.35)] flex items-center justify-center gap-2 disabled:opacity-50"
        >
          <Play className="w-4 h-4 fill-slate-950" />
          {isSimulating ? "Simulating Network..." : "RUN SIMULATION"}
        </button>

        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={onResetSimulation}
            className="py-2.5 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors border border-slate-700 flex items-center justify-center gap-1.5"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Reset
          </button>
          <button
            onClick={onOpenCompare}
            className="py-2.5 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-300 text-xs font-semibold transition-colors border border-slate-700 flex items-center justify-center gap-1.5"
          >
            <Scale className="w-3.5 h-3.5" />
            Compare
          </button>
        </div>
      </div>
    </div>
  );
};
