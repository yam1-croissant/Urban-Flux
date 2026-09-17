import {
    Activity,
    Check,
    Compass,
    HelpCircle,
    Layers,
    RotateCcw,
    Scale,
    X,
    Zap,
} from "lucide-react";
import React, { useCallback, useEffect, useState } from "react";
import {
    compareScenarios,
    fetchNetwork,
    fetchPresets,
    simulateScenario,
} from "./api/client";
import { BirdseyeMap } from "./components/BirdseyeMap";
import { CascadeTimeline } from "./components/CascadeTimeline";
import { CriticalityRankPanel } from "./components/CriticalityRankPanel";
import { DisruptionStudio } from "./components/DisruptionStudio";
import { ExplainabilityPanel } from "./components/ExplainabilityPanel";
import { ImpactDashboard } from "./components/ImpactDashboard";
import { InteractiveUserGuide } from "./components/InteractiveUserGuide";
import { LinkInspector } from "./components/LinkInspector";
import { RealBangaloreMap } from "./components/RealBangaloreMap";
import { ScenarioComparisonModal } from "./components/ScenarioComparisonModal";
import {
    ComparisonResult,
    DisruptionInput,
    NetworkResponse,
    ScenarioPreset,
    SimulationResult,
} from "./types";

export const App: React.FC = () => {
  const [network, setNetwork] = useState<NetworkResponse | null>(null);
  const [presets, setPresets] = useState<ScenarioPreset[]>([]);
  const [activeDisruptions, setActiveDisruptions] = useState<DisruptionInput[]>([]);
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);
  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [isCompareOpen, setIsCompareOpen] = useState<boolean>(false);
  const [comparisonResult, setComparisonResult] = useState<ComparisonResult | null>(null);
  const [isDemoRunning, setIsDemoRunning] = useState<boolean>(false);
  const [mapMode, setMapMode] = useState<"real_map" | "schematic">("real_map");

  // Onboarding tour and completion toast state
  const [isGuideOpen, setIsGuideOpen] = useState<boolean>(false);
  const [showReadyToast, setShowReadyToast] = useState<boolean>(false);

  // Initialize network and presets
  useEffect(() => {
    async function init() {
      const net = await fetchNetwork();
      const pre = await fetchPresets();
      setNetwork(net);
      setPresets(pre);
      // Run initial baseline simulation
      const res = await simulateScenario({ disruptions: [] });
      setSimulationResult(res);

      // Check first-time visitor status for interactive user guide
      const tourComplete = localStorage.getItem("urbanresilience_onboarding_complete");
      if (!tourComplete) {
        setIsGuideOpen(true);
      }
    }
    init();
  }, []);

  // Update or add a disruption for a given link
  const handleUpdateDisruption = useCallback(
    (
      assetId: string,
      multiplier: number,
      type: "closure" | "partial_closure" | "weather" | "construction" = "closure"
    ) => {
      setActiveDisruptions((prev) => {
        if (multiplier >= 1.0) {
          return prev.filter((d) => d.asset_id !== assetId);
        }
        const existing = prev.find((d) => d.asset_id === assetId);
        if (existing) {
          return prev.map((d) =>
            d.asset_id === assetId
              ? { ...d, capacity_multiplier: multiplier, disruption_type: type }
              : d
          );
        }
        return [
          ...prev,
          { asset_id: assetId, disruption_type: type, capacity_multiplier: multiplier },
        ];
      });
    },
    []
  );

  // Apply a scenario preset
  const handleApplyPreset = useCallback((preset: ScenarioPreset) => {
    setActiveDisruptions(preset.disruptions);
    // If preset targets specific edges, select the primary one for inspector
    if (preset.disruptions.length > 0) {
      setSelectedEdgeId(preset.disruptions[0].asset_id);
    }
  }, []);

  // Quick toggle closure on an edge directly from map
  const handleQuickToggleDisruption = useCallback((edgeId: string) => {
    setActiveDisruptions((prev) => {
      const exists = prev.find((d) => d.asset_id === edgeId);
      if (exists && exists.capacity_multiplier === 0) {
        return prev.filter((d) => d.asset_id !== edgeId);
      }
      return [
        ...prev.filter((d) => d.asset_id !== edgeId),
        { asset_id: edgeId, disruption_type: "closure", capacity_multiplier: 0.0 },
      ];
    });
    setSelectedEdgeId(edgeId);
  }, []);

  // Run simulation against backend or local fallback
  const handleRunSimulation = useCallback(
    async (disruptionsToRun?: DisruptionInput[]) => {
      setIsSimulating(true);
      try {
        const disruptions = disruptionsToRun !== undefined ? disruptionsToRun : activeDisruptions;
        const res = await simulateScenario({ disruptions });
        setSimulationResult(res);
      } catch (err) {
        console.error("Simulation error:", err);
      } finally {
        setIsSimulating(false);
      }
    },
    [activeDisruptions]
  );

  // Reset to nominal baseline
  const handleReset = useCallback(async () => {
    setActiveDisruptions([]);
    setSelectedEdgeId(null);
    setIsSimulating(true);
    const res = await simulateScenario({ disruptions: [] });
    setSimulationResult(res);
    setIsSimulating(false);
  }, []);

  // Trigger automated demo replay scenario
  const handleRunDemo = useCallback(async () => {
    setIsDemoRunning(true);
    // Step 1: Reset to baseline
    await handleReset();
    await new Promise((r) => setTimeout(r, 600));

    // Step 2: Apply Silk Board Bridge Closure
    const demoDisruptions: DisruptionInput[] = [
      { asset_id: "Bridge_A_B", disruption_type: "closure", capacity_multiplier: 0.0 },
    ];
    setActiveDisruptions(demoDisruptions);
    setSelectedEdgeId("Bridge_A_B");

    // Step 3: Trigger simulation
    await handleRunSimulation(demoDisruptions);
    setIsDemoRunning(false);
  }, [handleReset, handleRunSimulation]);

  // Open Scenario Policy Comparison Modal
  const handleOpenCompare = useCallback(async () => {
    const unmitigated = {
      disruptions: [
        { asset_id: "Bridge_A_B", disruption_type: "closure" as const, capacity_multiplier: 0.0 },
      ],
    };
    const mitigated = {
      disruptions: [
        { asset_id: "Bridge_A_B", disruption_type: "closure" as const, capacity_multiplier: 0.0 },
        { asset_id: "Bottleneck_E_F", disruption_type: "partial_closure" as const, capacity_multiplier: 1.0 },
      ],
    };
    const comp = await compareScenarios(unmitigated, mitigated);
    setComparisonResult(comp);
    setIsCompareOpen(true);
  }, []);

  // Guide step sync handler to adjust UI view or select representative link
  const handleGuideStepChange = useCallback(
    (stepIndex: number) => {
      // Step 4 (index 3) or Step 5 (index 4): switch to schematic mode
      if (stepIndex === 3) {
        setMapMode("schematic");
      }
      // Step 3 (index 2), Step 5 (index 4), Step 6 (index 5): select a road if none active
      if (stepIndex === 2 || stepIndex === 4 || stepIndex === 5) {
        setSelectedEdgeId((prev) => {
          if (!prev && network?.edges && network.edges.length > 0) {
            const sample =
              network.edges.find(
                (e) => e.id === "Bridge_A_B" || e.id.includes("SilkBoard") || e.id.includes("Hosur")
              ) || network.edges[0];
            return sample.id;
          }
          return prev;
        });
      }
    },
    [network]
  );

  // Guide completion handler
  const handleFinishGuide = useCallback(() => {
    localStorage.setItem("urbanresilience_onboarding_complete", "true");
    setIsGuideOpen(false);
    setShowReadyToast(true);
    setTimeout(() => {
      setShowReadyToast(false);
    }, 4500);
  }, []);

  const selectedEdge =
    network?.edges.find((e) => e.id === selectedEdgeId) || null;

  return (
    <div className="min-h-screen bg-[#070B14] text-slate-100 flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Top Application Header Bar */}
      <header className="h-16 border-b border-slate-800/80 bg-[#0F172A]/80 backdrop-blur-xl px-6 flex items-center justify-between sticky top-0 z-40 shadow-2xl">
        {/* Left: Branding & Digital Twin Status */}
        <div className="flex items-center gap-3.5">
          <div className="relative">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-600 via-cyan-500 to-indigo-500 flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.4)] border border-cyan-300/30">
              <Activity className="w-5 h-5 text-white animate-pulse" />
            </div>
            <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 border-2 border-slate-900 rounded-full" />
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold tracking-wider uppercase bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                UrbanResilience Sim
              </h1>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-semibold tracking-wide">
                v2.5 DIGITAL TWIN
              </span>
            </div>
            <p className="text-[11px] text-slate-400 flex items-center gap-1.5">
              <span>Bengaluru Central Arterial Corridor</span>
              <span className="text-slate-600">•</span>
              <span className="text-emerald-400 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping inline-block" />
                Live Deterministic Engine
              </span>
            </p>
          </div>
        </div>

        {/* Center: Map View Mode Switcher */}
        <div
          id="tour-map-view-modes"
          className="hidden md:flex items-center bg-slate-900/90 border border-slate-800 p-1 rounded-xl shadow-inner"
        >
          <button
            onClick={() => setMapMode("real_map")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              mapMode === "real_map"
                ? "bg-gradient-to-r from-cyan-600 to-cyan-500 text-white shadow-[0_0_12px_rgba(6,182,212,0.4)]"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Compass className="w-3.5 h-3.5" />
            <span>🗺️ Real Bangalore Map</span>
          </button>
          <button
            id="tour-schematic-toggle"
            onClick={() => setMapMode("schematic")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              mapMode === "schematic"
                ? "bg-gradient-to-r from-indigo-600 to-indigo-500 text-white shadow-[0_0_12px_rgba(99,102,241,0.4)]"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>⚡ Schematic Twin</span>
          </button>
        </div>

        {/* Right: Action Controls */}
        <div className="flex items-center gap-2.5">
          <button
            onClick={handleRunDemo}
            disabled={isDemoRunning || isSimulating}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-gradient-to-r from-rose-600 via-rose-500 to-orange-500 hover:from-rose-500 hover:to-orange-400 text-white font-semibold text-xs shadow-[0_0_20px_rgba(244,63,94,0.35)] hover:shadow-[0_0_25px_rgba(244,63,94,0.5)] transition-all transform active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Zap className="w-4 h-4 text-white fill-white animate-bounce" />
            <span>{isDemoRunning ? "Replaying Domino Chain..." : "▶ Run Demo"}</span>
          </button>

          <button
            id="tour-compare-policies"
            onClick={handleOpenCompare}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700/80 border border-slate-700 text-slate-200 font-semibold text-xs transition-all hover:border-cyan-500/40"
          >
            <Scale className="w-4 h-4 text-cyan-400" />
            <span>Compare Policies</span>
          </button>

          <button
            onClick={() => setIsGuideOpen(true)}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700/80 border border-slate-700 text-cyan-300 font-semibold text-xs transition-all hover:border-cyan-500/40"
            title="Open Interactive Onboarding Guide"
          >
            <HelpCircle className="w-3.5 h-3.5 text-cyan-400" />
            <span>Guide</span>
          </button>

          <button
            onClick={handleReset}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700/80 border border-slate-700 text-slate-400 hover:text-white transition-colors"
            title="Reset Network to Nominal Baseline"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* Main Command Center Grid */}
      <main className="flex-1 p-5 grid grid-cols-1 lg:grid-cols-12 gap-5 max-w-[1920px] mx-auto w-full">
        {/* Left Column: Link Inspector & Disruption Studio (Col Span 3) */}
        <div className="lg:col-span-3 flex flex-col gap-4">
          {/* Link Inspector (Expands above Disruption Studio when a link is selected) */}
          {selectedEdge && (
            <LinkInspector
              edge={selectedEdge}
              activeDisruptions={activeDisruptions}
              edgeEval={simulationResult?.scenario_edges?.[selectedEdge.id]}
              onUpdateDisruption={handleUpdateDisruption}
              onClose={() => setSelectedEdgeId(null)}
            />
          )}

          {/* Categorized Disruption Studio */}
          <DisruptionStudio
            presets={presets}
            activeDisruptions={activeDisruptions}
            isSimulating={isSimulating}
            onApplyPreset={handleApplyPreset}
            onRunSimulation={() => handleRunSimulation()}
            onResetSimulation={handleReset}
            onOpenCompare={handleOpenCompare}
          />
        </div>

        {/* Center Column: Key Metrics (Above Map) & Digital Twin Map (Col Span 6) */}
        <div className="lg:col-span-6 flex flex-col gap-4">
          {/* Real-time Metric KPI Dashboard (Above Map per Section 12) */}
          <ImpactDashboard simulationResult={simulationResult} />

          {/* Interactive Map View */}
          <div className="flex-1 min-h-[520px]">
            {mapMode === "real_map" ? (
              <RealBangaloreMap
                nodes={network?.nodes || []}
                edges={network?.edges || []}
                criticalAssets={network?.critical_assets || []}
                pois={network?.pois || []}
                simulationResult={simulationResult}
                selectedEdgeId={selectedEdgeId}
                onSelectEdge={setSelectedEdgeId}
                onQuickToggleDisruption={handleQuickToggleDisruption}
              />
            ) : (
              <BirdseyeMap
                nodes={network?.nodes || []}
                edges={network?.edges || []}
                criticalAssets={network?.critical_assets || []}
                simulationResult={simulationResult}
                selectedEdgeId={selectedEdgeId}
                onSelectEdge={setSelectedEdgeId}
                onQuickToggleDisruption={handleQuickToggleDisruption}
              />
            )}
          </div>
        </div>

        {/* Right Column: Cascade Timeline, Explainability & Vulnerability Ranking (Col Span 3) */}
        <div className="lg:col-span-3 flex flex-col gap-4">
          <div id="tour-cascade-timeline">
            <CascadeTimeline simulationResult={simulationResult} />
          </div>
          <div id="tour-explainability">
            <ExplainabilityPanel simulationResult={simulationResult} />
          </div>
          <div id="tour-criticality-ranking">
            <CriticalityRankPanel
              edges={network?.edges || []}
              simulationResult={simulationResult}
              onSelectEdge={(edgeId) => setSelectedEdgeId(edgeId)}
            />
          </div>
        </div>
      </main>

      {/* Policy Trade-off Comparison Modal */}
      <ScenarioComparisonModal
        isOpen={isCompareOpen}
        onClose={() => setIsCompareOpen(false)}
        comparison={comparisonResult}
      />

      {/* 12-Step Interactive Onboarding Guide Modal */}
      <InteractiveUserGuide
        isOpen={isGuideOpen}
        onClose={() => setIsGuideOpen(false)}
        onFinish={handleFinishGuide}
        onStepChange={handleGuideStepChange}
      />

      {/* Tutorial Completion Confirmation Toast */}
      {showReadyToast && (
        <div className="fixed bottom-6 right-6 z-50 bg-[#0F172A] border border-cyan-500/50 rounded-2xl p-4 shadow-[0_10px_35px_rgba(0,0,0,0.8),0_0_20px_rgba(6,182,212,0.3)] flex items-center gap-3 text-slate-100 animate-in fade-in slide-in-from-bottom-5">
          <div className="w-8 h-8 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center shrink-0">
            <Check className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white">✓ You're ready</h4>
            <p className="text-[11px] text-slate-400">
              Choose a disruption and run your first scenario.
            </p>
          </div>
          <button
            onClick={() => setShowReadyToast(false)}
            className="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors ml-2"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}
    </div>
  );
};

export default App;
