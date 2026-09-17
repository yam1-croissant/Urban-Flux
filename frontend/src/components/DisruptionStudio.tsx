import {
    AlertTriangle,
    ChevronDown,
    ChevronRight,
    CloudRain,
    Construction,
    Play,
    RotateCcw,
    Scale,
    ShieldCheck,
    Sliders,
    Zap
} from "lucide-react";
import React, { useMemo, useState } from "react";
import { DisruptionInput, ScenarioPreset } from "../types";

type DisruptionCategory = "monsoon" | "construction" | "closure" | "events" | "emergency";

interface DisruptionStudioProps {
  presets: ScenarioPreset[];
  activeDisruptions: DisruptionInput[];
  isSimulating: boolean;
  onApplyPreset: (preset: ScenarioPreset) => void;
  onRunSimulation: () => void;
  onResetSimulation: () => void;
  onOpenCompare: () => void;
}

const CATEGORY_DEFINITIONS: {
  id: DisruptionCategory;
  name: string;
  icon: string;
  tagline: string;
  badgeClass: string;
}[] = [
  {
    id: "monsoon",
    name: "Monsoon",
    icon: "🌧️",
    tagline: "Heavy flooding & drainage inundation",
    badgeClass: "text-cyan-400 bg-cyan-500/10 border-cyan-500/30",
  },
  {
    id: "construction",
    name: "Construction",
    icon: "🚧",
    tagline: "Metro works, lane barricades & bottlenecks",
    badgeClass: "text-amber-400 bg-amber-500/10 border-amber-500/30",
  },
  {
    id: "closure",
    name: "Infrastructure Closure",
    icon: "⛔",
    tagline: "Flyover closures, freight breakdown & structural events",
    badgeClass: "text-rose-400 bg-rose-500/10 border-rose-500/30",
  },
  {
    id: "events",
    name: "Events / Demand",
    icon: "⚡",
    tagline: "Tech corridor peak rushes & stadium gridlock",
    badgeClass: "text-indigo-400 bg-indigo-500/10 border-indigo-500/30",
  },
  {
    id: "emergency",
    name: "Emergency Response",
    icon: "🚑",
    tagline: "Hospital green corridors & priority routing",
    badgeClass: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
  },
];

// Fallback curated presets for categories if presets list is sparse
const DEFAULT_CATEGORY_PRESETS: Record<DisruptionCategory, ScenarioPreset[]> = {
  monsoon: [
    {
      id: "scenario_bellandur_flood",
      name: "Bellandur ORR & Sarjapur Flash Flood",
      description: "60mm/hr cloudburst inundates Outer Ring Road at Ecospace. Cuts arterial capacity by 60%.",
      icon: "CloudRain",
      category: "monsoon",
      disruptions: [
        { asset_id: "Edge_Sarjapur_Bellandur", disruption_type: "weather", capacity_multiplier: 0.4 },
        { asset_id: "Edge_Bellandur_Marathahalli", disruption_type: "weather", capacity_multiplier: 0.4 },
        { asset_id: "Bridge_A_B", disruption_type: "weather", capacity_multiplier: 0.5 },
      ],
    },
    {
      id: "scenario_waterlogging_rush_hour",
      name: "Central Arterial Flash Waterlogging",
      description: "50% capacity loss on primary corridors due to heavy waterlogging at underpasses.",
      icon: "CloudRain",
      category: "monsoon",
      disruptions: [
        { asset_id: "Bridge_A_B", disruption_type: "weather", capacity_multiplier: 0.5 },
        { asset_id: "Bottleneck_E_F", disruption_type: "weather", capacity_multiplier: 0.5 },
      ],
    },
  ],
  construction: [
    {
      id: "scenario_mg_road_construction",
      name: "Namma Metro Line 6 (MG Road & Trinity)",
      description: "Barricaded central lanes reduce throughput by 50% along Trinity Circle & Anil Kumble Circle.",
      icon: "Construction",
      category: "construction",
      disruptions: [
        { asset_id: "Edge_Trinity_AnilKumble", disruption_type: "construction", capacity_multiplier: 0.5 },
        { asset_id: "Arterial_B_C", disruption_type: "construction", capacity_multiplier: 0.65 },
      ],
    },
    {
      id: "scenario_roadwork_construction",
      name: "Inner Ring Road Metro Line 3 Works",
      description: "Single lane blockage on Inner Ring Road approach reducing capacity by 35%.",
      icon: "Construction",
      category: "construction",
      disruptions: [
        { asset_id: "Arterial_B_C", disruption_type: "construction", capacity_multiplier: 0.65 },
      ],
    },
  ],
  closure: [
    {
      id: "scenario_silk_board_collapse",
      name: "Silk Board Elevated Flyover Closure",
      description: "Acute 100% shutdown of Silk Board Elevated Highway. Diverts 5,000+ veh/h onto BTM & Koramangala.",
      icon: "AlertTriangle",
      category: "closure",
      disruptions: [
        { asset_id: "Edge_SilkBoard_Hosur", disruption_type: "closure", capacity_multiplier: 0.0 },
        { asset_id: "Bridge_A_B", disruption_type: "closure", capacity_multiplier: 0.0 },
      ],
      recommended_mitigation_id: "scenario_green_corridor_mitigation",
    },
    {
      id: "scenario_hebbal_gridlock",
      name: "Hebbal Airport Flyover Freight Gridlock",
      description: "Multi-axle container breakdown blocks 2 of 3 lanes inbound to Bengaluru city (-65% capacity).",
      icon: "AlertOctagon",
      category: "closure",
      disruptions: [
        { asset_id: "Edge_Hebbal_Ballari", disruption_type: "closure", capacity_multiplier: 0.35 },
      ],
    },
  ],
  events: [
    {
      id: "scenario_itpl_summit",
      name: "ITPL Tech Summit Peak Hour Surge",
      description: "Major global tech convention in Whitefield creates 35% commuter surge on Old Airport Road.",
      icon: "Zap",
      category: "events",
      disruptions: [
        { asset_id: "Edge_Domlur_Indiranagar", disruption_type: "partial_closure", capacity_multiplier: 0.7 },
        { asset_id: "Arterial_C_D", disruption_type: "partial_closure", capacity_multiplier: 0.75 },
      ],
    },
    {
      id: "scenario_chinnaswamy_event",
      name: "Chinnaswamy Stadium Event Gridlock",
      description: "Major cricket match egress creates localized arterial bottlenecks across MG Road & Domlur.",
      icon: "Zap",
      category: "events",
      disruptions: [
        { asset_id: "Edge_Indiranagar_CMH", disruption_type: "partial_closure", capacity_multiplier: 0.65 },
      ],
    },
  ],
  emergency: [
    {
      id: "scenario_green_corridor_mitigation",
      name: "Ambulance Emergency Green Wave Mitigation",
      description: "Traffic police establish priority signal green-waves for Manipal, Victoria, and NIMHANS trauma centers.",
      icon: "ShieldCheck",
      category: "emergency",
      disruptions: [],
    },
    {
      id: "scenario_mitigation_active_reroute",
      name: "Active Police Rerouting & North Relief Corridor",
      description: "Deployment of traffic wardens and dedicated signal green-waves on North Relief corridor.",
      icon: "ShieldCheck",
      category: "emergency",
      disruptions: [],
    },
  ],
};

export const DisruptionStudio: React.FC<DisruptionStudioProps> = ({
  presets,
  activeDisruptions,
  isSimulating,
  onApplyPreset,
  onRunSimulation,
  onResetSimulation,
  onOpenCompare,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<DisruptionCategory>("closure");

  // Group presets into categories
  const categorizedPresets = useMemo(() => {
    const map: Record<DisruptionCategory, ScenarioPreset[]> = {
      monsoon: [],
      construction: [],
      closure: [],
      events: [],
      emergency: [],
    };

    // Helper to determine category
    const categorize = (p: ScenarioPreset): DisruptionCategory => {
      if (p.category) return p.category;
      const lower = (p.id + " " + p.name + " " + p.description).toLowerCase();
      if (lower.includes("flood") || lower.includes("water") || lower.includes("monsoon") || p.icon?.toLowerCase().includes("rain")) {
        return "monsoon";
      }
      if (lower.includes("construction") || lower.includes("metro") || lower.includes("roadwork") || p.icon?.toLowerCase().includes("cone")) {
        return "construction";
      }
      if (lower.includes("mitigation") || lower.includes("green_wave") || lower.includes("green corridor") || lower.includes("police") || p.icon?.toLowerCase().includes("shield")) {
        return "emergency";
      }
      if (lower.includes("summit") || lower.includes("surge") || lower.includes("stadium") || lower.includes("event")) {
        return "events";
      }
      return "closure";
    };

    // Populate from fetched presets
    presets.forEach((p) => {
      const cat = categorize(p);
      map[cat].push({ ...p, category: cat });
    });

    // Ensure every category has at least the default options
    (Object.keys(DEFAULT_CATEGORY_PRESETS) as DisruptionCategory[]).forEach((cat) => {
      if (map[cat].length === 0) {
        map[cat] = DEFAULT_CATEGORY_PRESETS[cat];
      }
    });

    return map;
  }, [presets]);

  const currentCategoryPresets = categorizedPresets[selectedCategory] || [];

  return (
    <div
      id="tour-disruption-studio"
      className="flex flex-col bg-[#0F172A]/90 backdrop-blur-xl border border-slate-800 rounded-2xl p-4 shadow-2xl overflow-y-auto max-h-[calc(100vh-100px)]"
    >
      {/* Studio Header */}
      <div className="flex items-center justify-between pb-3.5 border-b border-slate-800/80 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-gradient-to-tr from-cyan-600/20 to-blue-600/20 rounded-xl border border-cyan-500/30">
            <Sliders className="w-4 h-4 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white tracking-wide uppercase">
              Disruption Studio
            </h2>
            <p className="text-[11px] text-slate-400">Configure Acute Events & Cascade Tests</p>
          </div>
        </div>
        <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
          {activeDisruptions.length} Active
        </span>
      </div>

      {/* Disruption Category Selector */}
      <div id="tour-disruption-categories" className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Choose a Disruption Category
          </label>
          <span className="text-[10px] text-slate-400">Click to expand</span>
        </div>

        {/* Collapsible Category Accordion / List */}
        <div className="space-y-1.5">
          {CATEGORY_DEFINITIONS.map((cat) => {
            const isSelected = selectedCategory === cat.id;
            const count = categorizedPresets[cat.id]?.length || 0;

            return (
              <div
                key={cat.id}
                className={`rounded-xl border transition-all overflow-hidden ${
                  isSelected
                    ? "bg-slate-900/90 border-cyan-500/50 shadow-[0_0_15px_rgba(6,182,212,0.15)]"
                    : "bg-slate-800/40 hover:bg-slate-800/80 border-slate-800/80 hover:border-slate-700"
                }`}
              >
                {/* Category Button Bar */}
                <button
                  onClick={() => setSelectedCategory(cat.id)}
                  className="w-full flex items-center justify-between p-2.5 text-left transition-colors"
                >
                  <div className="flex items-center gap-2.5">
                    <span className="text-base">{cat.icon}</span>
                    <div>
                      <div className="flex items-center gap-1.5">
                        <span className={`text-xs font-bold ${isSelected ? "text-cyan-300" : "text-slate-200"}`}>
                          {cat.name}
                        </span>
                        <span className="text-[9px] font-mono px-1.5 py-0.2 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                          {count}
                        </span>
                      </div>
                      <p className="text-[10px] text-slate-400 leading-tight truncate max-w-[210px]">
                        {cat.tagline}
                      </p>
                    </div>
                  </div>
                  <div className="text-slate-500">
                    {isSelected ? <ChevronDown className="w-4 h-4 text-cyan-400" /> : <ChevronRight className="w-4 h-4" />}
                  </div>
                </button>

                {/* Expanded Scenarios inside Selected Category */}
                {isSelected && (
                  <div className="px-2.5 pb-2.5 pt-1 border-t border-slate-800/60 space-y-2 animate-in fade-in duration-200">
                    {currentCategoryPresets.map((preset) => {
                      const isPresetActive = preset.disruptions.length > 0 && preset.disruptions.every((d) =>
                        activeDisruptions.some(
                          (ad) => ad.asset_id === d.asset_id && Math.abs(ad.capacity_multiplier - d.capacity_multiplier) < 0.05
                        )
                      );

                      return (
                        <button
                          key={preset.id}
                          onClick={() => onApplyPreset(preset)}
                          className={`w-full flex items-start gap-2.5 p-2.5 rounded-xl border text-left transition-all group ${
                            isPresetActive
                              ? "bg-cyan-950/40 border-cyan-500/50 shadow-[0_0_12px_rgba(6,182,212,0.25)]"
                              : "bg-slate-850/70 hover:bg-slate-800 border-slate-750/60 hover:border-cyan-500/30"
                          }`}
                        >
                          <div className="p-1.5 rounded-lg bg-slate-900 border border-slate-700 shrink-0 group-hover:border-cyan-500/40 mt-0.5">
                            {cat.id === "monsoon" && <CloudRain className="w-3.5 h-3.5 text-cyan-400" />}
                            {cat.id === "construction" && <Construction className="w-3.5 h-3.5 text-amber-400" />}
                            {cat.id === "closure" && <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />}
                            {cat.id === "events" && <Zap className="w-3.5 h-3.5 text-indigo-400" />}
                            {cat.id === "emergency" && <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />}
                          </div>

                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between gap-1">
                              <span className="text-xs font-semibold text-slate-100 group-hover:text-cyan-300 transition-colors truncate">
                                {preset.name}
                              </span>
                              {isPresetActive && (
                                <span className="text-[9px] font-bold text-cyan-400 bg-cyan-500/10 px-1.5 py-0.5 rounded border border-cyan-500/30 shrink-0">
                                  Active
                                </span>
                              )}
                            </div>
                            <p className="text-[11px] text-slate-400 line-clamp-2 mt-1 leading-relaxed">
                              {preset.description}
                            </p>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Execution Controls */}
      <div className="pt-3 border-t border-slate-800/80 mt-auto space-y-2.5">
        <button
          id="tour-run-simulation"
          onClick={onRunSimulation}
          disabled={isSimulating}
          className="w-full py-3.5 px-4 rounded-xl bg-gradient-to-r from-cyan-500 via-cyan-400 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-sm tracking-wide transition-all shadow-[0_0_20px_rgba(6,182,212,0.35)] flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed group active:scale-[0.98]"
        >
          <Play className="w-4 h-4 fill-slate-950 group-hover:scale-110 transition-transform" />
          <span>{isSimulating ? "Recalculating Cascade..." : "RUN SIMULATION"}</span>
        </button>

        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={onResetSimulation}
            className="py-2.5 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-semibold transition-colors border border-slate-700 flex items-center justify-center gap-1.5"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Reset
          </button>
          <button
            id="tour-compare-policies"
            onClick={onOpenCompare}
            className="py-2.5 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-300 hover:text-cyan-200 text-xs font-semibold transition-colors border border-slate-700 flex items-center justify-center gap-1.5 hover:border-cyan-500/40"
          >
            <Scale className="w-3.5 h-3.5 text-cyan-400" />
            Compare
          </button>
        </div>
      </div>
    </div>
  );
};
