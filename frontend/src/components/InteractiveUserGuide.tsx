import { ArrowLeft, ArrowRight, Check, Sparkles, X } from "lucide-react";
import React, { useCallback, useEffect, useLayoutEffect, useState } from "react";

export interface TourStep {
  targetId: string;
  category: string;
  title: string;
  content: string;
  preferredPlacement?: "right" | "left" | "top" | "bottom";
}

export const TOUR_STEPS: TourStep[] = [
  {
    targetId: "tour-disruption-studio",
    category: "INTRODUCTION • STEP 1 OF 12",
    title: "Disruption Studio",
    content:
      "This is where you create the situation you want to test.\n\nChoose what is affecting the city — such as **monsoon flooding, construction, infrastructure closures, demand surges, or emergency response events**.\n\nYou can then configure the disruption and see how the network responds.\n\n**Give it a try!**",
    preferredPlacement: "right",
  },
  {
    targetId: "tour-disruption-categories",
    category: "CATEGORIES • STEP 2 OF 12",
    title: "Choose a disruption",
    content:
      "Similar scenarios are grouped together so the interface stays clean.\n\nSelect a category such as:\n• **Monsoon**\n• **Construction**\n• **Infrastructure Closure**\n• **Events / Demand**\n• **Emergency Response**\n\nOnce you select one, the other categories collapse so you only work with the scenario you need.",
    preferredPlacement: "right",
  },
  {
    targetId: "tour-link-inspector",
    category: "SELECTION • STEP 3 OF 12",
    title: "Your selection appears here",
    content:
      "Once you choose a scenario or select an affected road, the **Link Inspector** opens here directly above the disruption studio.\n\nIt gives you the important information for the selected part of the network without filling the screen with details you don't need yet.",
    preferredPlacement: "right",
  },
  {
    targetId: "tour-schematic-toggle",
    category: "NETWORK TWIN • STEP 4 OF 12",
    title: "Schematic Twin",
    content:
      "This view simplifies the city into a clear road network so you can understand what is actually being simulated.\n\nRoads, intersections, capacity, and traffic flow are easier to inspect here.\n\n**This is where you can directly experiment with the network.**",
    preferredPlacement: "bottom",
  },
  {
    targetId: "tour-map-canvas",
    category: "INTERACTION • STEP 5 OF 12",
    title: "Select a road",
    content:
      "Click a road on the schematic to inspect it.\n\nYou can see information such as:\n• **Road identity & classification**\n• **Current traffic flow**\n• **Nominal capacity**\n• **Free-flow conditions**\n• **Current stress / V/C ratio**\n\nSelected roads can then be modified as part of your scenario.",
    preferredPlacement: "left",
  },
  {
    targetId: "tour-road-controls",
    category: "ROAD CONDITIONS • STEP 6 OF 12",
    title: "Change the network",
    content:
      "This is where you can experiment with the conditions of the network.\n\nDepending on the selected scenario, you can change things such as:\n• **Road capacity slider**\n• **Number of vehicles / traffic demand**\n• **Closure percentage presets**\n• **Disruption intensity & causes**\n\nFor example, you could reduce a road to **50% capacity** and then see where the displaced traffic goes.",
    preferredPlacement: "right",
  },
  {
    targetId: "tour-run-simulation",
    category: "ENGINE • STEP 7 OF 12",
    title: "Run the simulation",
    content:
      "Once your scenario is ready, run the simulation.\n\nThe system recalculates the network and evaluates how traffic moves after the disruption.\n\nIt looks for:\n**rerouting → congestion → secondary bottlenecks → critical-service impacts**\n\nThe result is shown directly on the map and in the analysis panels.",
    preferredPlacement: "right",
  },
  {
    targetId: "tour-cascade-timeline",
    category: "PROPAGATION • STEP 8 OF 12",
    title: "Follow the cascade",
    content:
      "A disruption does not always stay isolated.\n\nThe timeline shows how the initial failure propagates through the network:\n\n**Primary failure**\n↓\n**Traffic diversion**\n↓\n**Secondary overload**\n↓\n**Critical service impact**\n\nThis helps you understand **why** the network changed, not just what the final numbers are.",
    preferredPlacement: "left",
  },
  {
    targetId: "tour-explainability",
    category: "CAUSAL EXPLAINABILITY • STEP 9 OF 12",
    title: "Why did this happen?",
    content:
      "This panel explains the simulation in a simple causal chain.\n\nInstead of only saying that a road became congested, it shows the chain of events that led there.\n\n*Example:\nBridge closure → traffic diversion → bottleneck overload → hospital access penalty*",
    preferredPlacement: "left",
  },
  {
    targetId: "tour-criticality-ranking",
    category: "VULNERABILITY • STEP 10 OF 12",
    title: "Which parts of the network matter most?",
    content:
      "This panel highlights roads and assets that become especially important under the current network conditions.\n\nUse it to quickly identify:\n• **Stressed corridors**\n• **Overloaded links**\n• **Important bottlenecks**\n• **Critical infrastructure**\n\nThink of this as the shortlist of places that deserve attention.",
    preferredPlacement: "left",
  },
  {
    targetId: "tour-key-metrics",
    category: "KEY METRICS • STEP 11 OF 12",
    title: "Understand the impact",
    content:
      "These four numbers summarize the most important outcome of the simulation.\n\n• **Net System Delay** — how much additional delay the network experienced.\n• **Hospital Access** — how emergency/critical-service access changed.\n• **Cascade Overloads** — how many secondary bottlenecks appeared.\n• **Net Trip Time Change** — how much overall travel time changed.\n\nPositioned above the map for instant visibility.",
    preferredPlacement: "bottom",
  },
  {
    targetId: "tour-compare-policies",
    category: "POLICY COMPARISON • STEP 12 OF 12",
    title: "Compare what you could do",
    content:
      "One disruption can have multiple possible responses.\n\nUse scenario comparison to examine different interventions and see how their outcomes differ.\n\nFor example:\n**No mitigation**\nvs.\n**Alternative routing / intervention**\n\nCompare the resulting network delay, bottlenecks, and critical-service impacts.",
    preferredPlacement: "bottom",
  },
];

interface InteractiveUserGuideProps {
  isOpen: boolean;
  onClose: () => void;
  onFinish: () => void;
  onStepChange?: (stepIndex: number) => void;
}

export const InteractiveUserGuide: React.FC<InteractiveUserGuideProps> = ({
  isOpen,
  onClose,
  onFinish,
  onStepChange,
}) => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [targetRect, setTargetRect] = useState<DOMRect | null>(null);

  const step = TOUR_STEPS[currentStepIndex];

  // Notify parent of step changes to synchronize UI (e.g. view mode, edge selection)
  useEffect(() => {
    if (isOpen) {
      onStepChange?.(currentStepIndex);
    }
  }, [isOpen, currentStepIndex, onStepChange]);

  // Compute bounding rectangle of active target
  const updateTargetRect = useCallback(() => {
    if (!isOpen || !step) return;

    let el = document.getElementById(step.targetId);

    // Fallback if target element is temporarily not mounted
    if (!el) {
      if (step.targetId === "tour-link-inspector" || step.targetId === "tour-road-controls") {
        el = document.getElementById("tour-disruption-studio");
      } else if (step.targetId === "tour-schematic-toggle") {
        el = document.getElementById("tour-map-view-modes");
      }
    }

    if (el) {
      const rect = el.getBoundingClientRect();
      setTargetRect(rect);
    } else {
      // Default to center if not found
      setTargetRect(null);
    }
  }, [isOpen, step]);

  useLayoutEffect(() => {
    updateTargetRect();
    const handleResize = () => updateTargetRect();
    const handleScroll = () => updateTargetRect();

    window.addEventListener("resize", handleResize);
    window.addEventListener("scroll", handleScroll, true);

    const timer = setTimeout(updateTargetRect, 150);

    return () => {
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("scroll", handleScroll, true);
      clearTimeout(timer);
    };
  }, [updateTargetRect, currentStepIndex]);

  if (!isOpen) return null;

  const isLastStep = currentStepIndex === TOUR_STEPS.length - 1;

  const handleNext = () => {
    if (isLastStep) {
      onFinish();
    } else {
      setCurrentStepIndex((prev) => prev + 1);
    }
  };

  const handleBack = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex((prev) => prev - 1);
    }
  };

  const handleSkip = () => {
    onFinish();
  };

  // Calculate card position responsive to spotlight target
  const getCardStyle = (): React.CSSProperties => {
    const cardWidth = 380;
    const cardHeight = 320;
    const padding = 16;
    const windowWidth = typeof window !== "undefined" ? window.innerWidth : 1200;
    const windowHeight = typeof window !== "undefined" ? window.innerHeight : 800;

    if (!targetRect) {
      return {
        position: "fixed",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        zIndex: 9999,
      };
    }

    let left = targetRect.right + padding;
    let top = targetRect.top;

    // Determine placement based on screen position and preferredPlacement
    const preferred = step.preferredPlacement || "right";

    if (preferred === "bottom") {
      left = targetRect.left + targetRect.width / 2 - cardWidth / 2;
      top = targetRect.bottom + padding;
    } else if (preferred === "left" || left + cardWidth > windowWidth - 20) {
      left = targetRect.left - cardWidth - padding;
      top = targetRect.top;
    }

    // Clamp horizontally
    if (left < padding) left = padding;
    if (left + cardWidth > windowWidth - padding) {
      left = windowWidth - cardWidth - padding;
    }

    // Clamp vertically
    if (top < padding) top = padding;
    if (top + cardHeight > windowHeight - padding) {
      top = windowHeight - cardHeight - padding;
    }

    return {
      position: "fixed",
      left: `${left}px`,
      top: `${top}px`,
      zIndex: 9999,
      transition: "all 0.3s cubic-bezier(0.16, 1, 0.3, 1)",
    };
  };

  return (
    <div className="fixed inset-0 z-[9990] overflow-hidden select-none pointer-events-auto">
      {/* Background Dim & Backdrop Blur */}
      <div className="fixed inset-0 bg-slate-950/75 backdrop-blur-[5px] transition-opacity duration-300" />

      {/* Dynamic Focused Cutout Spotlight with Cyan Glow */}
      {targetRect && (
        <div
          style={{
            position: "fixed",
            left: `${targetRect.left - 6}px`,
            top: `${targetRect.top - 6}px`,
            width: `${targetRect.width + 12}px`,
            height: `${targetRect.height + 12}px`,
            borderRadius: "16px",
            boxShadow:
              "0 0 0 9999px rgba(3, 7, 18, 0.70), 0 0 35px rgba(6, 182, 212, 0.55), inset 0 0 20px rgba(6, 182, 212, 0.2)",
            border: "2px solid rgba(6, 182, 212, 0.9)",
            pointerEvents: "none",
            transition: "all 0.35s cubic-bezier(0.16, 1, 0.3, 1)",
            zIndex: 9995,
          }}
        />
      )}

      {/* Compact Floating Explanation Card */}
      <div
        style={getCardStyle()}
        className="w-[360px] md:w-[380px] bg-[#0F172A] border border-cyan-500/40 rounded-2xl p-5 shadow-[0_20px_50px_rgba(0,0,0,0.9),0_0_30px_rgba(6,182,212,0.25)] text-slate-100 flex flex-col justify-between"
      >
        {/* Header: Step counter & Close button */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <span className="p-1 rounded-md bg-cyan-500/20 text-cyan-400">
              <Sparkles className="w-3.5 h-3.5" />
            </span>
            <span className="text-[10px] font-mono font-bold tracking-wider uppercase text-cyan-400">
              {step.category}
            </span>
          </div>

          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
            title="Close Guide (Esc)"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Title and Body */}
        <div className="py-3.5">
          <h2 className="text-base font-bold text-white tracking-wide mb-2">
            {step.title}
          </h2>
          <div className="text-xs text-slate-300 leading-relaxed space-y-2 whitespace-pre-line">
            {step.content.split("\n\n").map((paragraph, idx) => {
              // Convert simple **bold** marks to JSX bold
              const parts = paragraph.split(/(\*\*.*?\*\*)/g);
              return (
                <p key={idx} className="leading-relaxed">
                  {parts.map((part, pIdx) => {
                    if (part.startsWith("**") && part.endsWith("**")) {
                      return (
                        <strong key={pIdx} className="text-cyan-300 font-semibold">
                          {part.slice(2, -2)}
                        </strong>
                      );
                    }
                    return part;
                  })}
                </p>
              );
            })}
          </div>
        </div>

        {/* Step Progress Indicators */}
        <div className="flex items-center justify-center gap-1.5 py-2">
          {TOUR_STEPS.map((_, i) => (
            <button
              key={i}
              onClick={() => setCurrentStepIndex(i)}
              className={`h-1.5 rounded-full transition-all ${
                i === currentStepIndex
                  ? "w-6 bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.6)]"
                  : i < currentStepIndex
                  ? "w-2 bg-slate-600"
                  : "w-1.5 bg-slate-800"
              }`}
              title={`Jump to step ${i + 1}`}
            />
          ))}
        </div>

        {/* Navigation Actions Footer */}
        <div className="flex items-center justify-between pt-3 border-t border-slate-800 mt-2">
          <button
            onClick={handleSkip}
            className="text-[11px] text-slate-400 hover:text-slate-200 transition-colors underline-offset-2 hover:underline"
          >
            Skip tutorial
          </button>

          <div className="flex items-center gap-2">
            {currentStepIndex > 0 && (
              <button
                onClick={handleBack}
                className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors border border-slate-700"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Back</span>
              </button>
            )}

            <button
              onClick={handleNext}
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs shadow-[0_0_15px_rgba(6,182,212,0.4)] transition-all active:scale-95"
            >
              <span>{isLastStep ? "Finish" : "Next"}</span>
              {isLastStep ? <Check className="w-3.5 h-3.5" /> : <ArrowRight className="w-3.5 h-3.5" />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

