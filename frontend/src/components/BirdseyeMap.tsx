import React, { useState, useMemo } from "react";
import { NodeData, EdgeData, EdgeEvaluation, SimulationResult, CriticalAssetData } from "../types";
import { Activity, AlertOctagon, Hospital, Building, Navigation, Zap, Shield, ZoomIn, ZoomOut, RotateCcw } from "lucide-react";

interface BirdseyeMapProps {
  nodes: NodeData[];
  edges: EdgeData[];
  criticalAssets: CriticalAssetData[];
  simulationResult: SimulationResult | null;
  selectedEdgeId: string | null;
  onSelectEdge: (edgeId: string | null) => void;
  onQuickToggleDisruption: (edgeId: string) => void;
}

// Fixed canvas layout coordinates mapping Bengaluru spatial layout
const NODE_POSITIONS: Record<string, { x: number; y: number }> = {
  Zone_A: { x: 120, y: 380 },        // Banashankari / West Suburb
  Junction_B: { x: 380, y: 380 },    // Silk Board Interchange
  Hospital_C: { x: 620, y: 160 },    // Manipal Trauma Center
  Junction_E: { x: 260, y: 560 },    // Agara / Sarjapur Junc
  Junction_F: { x: 520, y: 440 },    // Sony World Hub / Bottleneck
  Zone_D: { x: 880, y: 220 },        // Whitefield Tech Corridor
  Zone_G: { x: 340, y: 140 },        // Indiranagar 100ft Hub
};

export const BirdseyeMap: React.FC<BirdseyeMapProps> = ({
  nodes,
  edges,
  criticalAssets,
  simulationResult,
  selectedEdgeId,
  onSelectEdge,
  onQuickToggleDisruption,
}) => {
  const [zoom, setZoom] = useState(1);
  const [hoveredEdgeId, setHoveredEdgeId] = useState<string | null>(null);
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);

  const edgeEvals = simulationResult?.scenario_edges || {};

  const getEdgeVisualProps = (edge: EdgeData) => {
    const evalData = edgeEvals[edge.id];
    const isDisrupted = simulationResult?.primary_disrupted_edges.includes(edge.id);
    const isNewlyOverloaded = simulationResult?.newly_overloaded_edges.includes(edge.id);
    const isClosed = evalData ? evalData.is_closed : edge.status === "closed";

    let color = "#38BDF8"; // Default cyan
    let strokeWidth = 5;
    let isPulsing = false;

    if (isClosed) {
      color = "#EF4444"; // Red
      isPulsing = true;
      strokeWidth = 6;
    } else if (isNewlyOverloaded || (evalData?.vc_ratio && evalData.vc_ratio > 1.0)) {
      color = "#F43F5E"; // Vivid Rose/Crimson
      isPulsing = true;
      strokeWidth = 7;
    } else if (evalData?.vc_ratio && evalData.vc_ratio > 0.85) {
      color = "#F59E0B"; // Amber
      strokeWidth = 6;
    } else if (evalData?.vc_ratio && evalData.vc_ratio > 0.65) {
      color = "#EAB308"; // Yellow
      strokeWidth = 5;
    } else {
      color = "#10B981"; // Emerald green
      strokeWidth = 4;
    }

    return { color, strokeWidth, isPulsing, isClosed, isNewlyOverloaded, isDisrupted, evalData };
  };

  return (
    <div className="relative w-full h-full bg-[#070B14] overflow-hidden flex items-center justify-center select-none border border-slate-800/80 rounded-2xl shadow-2xl">
      {/* Background Digital Twin Grid */}
      <div 
        className="absolute inset-0 opacity-20 pointer-events-none"
        style={{
          backgroundImage: `
            radial-gradient(circle at 50% 50%, rgba(6,182,212,0.15) 0%, transparent 70%),
            linear-gradient(to right, #1E293B 1px, transparent 1px),
            linear-gradient(to bottom, #1E293B 1px, transparent 1px)
          `,
          backgroundSize: "100% 100%, 40px 40px, 40px 40px"
        }}
      />

      {/* Floating Map HUD Controls */}
      <div className="absolute top-4 right-4 z-20 flex flex-col gap-2 bg-slate-900/80 backdrop-blur-md p-1.5 rounded-xl border border-slate-700/60 shadow-lg">
        <button
          onClick={() => setZoom((z) => Math.min(1.6, z + 0.15))}
          className="p-2 text-slate-300 hover:text-cyan-400 hover:bg-slate-800 rounded-lg transition-colors"
          title="Zoom In"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={() => setZoom((z) => Math.max(0.7, z - 0.15))}
          className="p-2 text-slate-300 hover:text-cyan-400 hover:bg-slate-800 rounded-lg transition-colors"
          title="Zoom Out"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={() => setZoom(1)}
          className="p-2 text-slate-300 hover:text-cyan-400 hover:bg-slate-800 rounded-lg transition-colors"
          title="Reset Zoom"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      {/* Legend Pill */}
      <div className="absolute bottom-4 left-4 z-20 bg-slate-900/85 backdrop-blur-md px-4 py-2.5 rounded-xl border border-slate-800 text-xs text-slate-300 flex items-center gap-4 shadow-xl">
        <span className="font-semibold text-slate-400 uppercase tracking-wider text-[10px]">V/C Saturation:</span>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-emerald-500 shadow-[0_0_8px_#10B981]" />
          <span>&lt; 0.70 Normal</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-amber-500 shadow-[0_0_8px_#F59E0B]" />
          <span>0.70–0.90 Stressed</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-rose-500 shadow-[0_0_8px_#F43F5E] animate-pulse" />
          <span>&gt; 1.00 Bottleneck</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-sm bg-red-600 border border-red-400 flex items-center justify-center text-[9px] font-bold text-white">✕</span>
          <span>Closed Link</span>
        </div>
      </div>

      {/* Interactive SVG Canvas */}
      <svg
        viewBox="0 0 1000 680"
        className="w-full h-full transition-transform duration-300 ease-out cursor-grab"
        style={{ transform: `scale(${zoom})` }}
      >
        <defs>
          {/* Neon Glow Filters */}
          <filter id="glow-rose" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id="glow-cyan" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          {/* Arrowhead Markers */}
          <marker id="arrowhead" markerWidth="6" markerHeight="6" refX="16" refY="3" orient="auto">
            <polygon points="0 0, 6 3, 0 6" fill="#64748B" />
          </marker>
          <marker id="arrowhead-red" markerWidth="7" markerHeight="7" refX="16" refY="3.5" orient="auto">
            <polygon points="0 0, 7 3.5, 0 7" fill="#F43F5E" />
          </marker>
          <marker id="arrowhead-emerald" markerWidth="6" markerHeight="6" refX="16" refY="3" orient="auto">
            <polygon points="0 0, 6 3, 0 6" fill="#10B981" />
          </marker>
        </defs>

        {/* 1. Draw Road Edges */}
        <g className="edges-layer">
          {edges.map((edge) => {
            const p1 = NODE_POSITIONS[edge.source] || { x: 500, y: 340 };
            const p2 = NODE_POSITIONS[edge.target] || { x: 500, y: 340 };
            const { color, strokeWidth, isPulsing, isClosed, isNewlyOverloaded, evalData } = getEdgeVisualProps(edge);
            const isSelected = selectedEdgeId === edge.id;
            const isHovered = hoveredEdgeId === edge.id;

            // Calculate midpoint for interactive badge
            const midX = (p1.x + p2.x) / 2;
            const midY = (p1.y + p2.y) / 2;

            return (
              <g
                key={edge.id}
                className="group cursor-pointer"
                onClick={() => onSelectEdge(isSelected ? null : edge.id)}
                onMouseEnter={() => setHoveredEdgeId(edge.id)}
                onMouseLeave={() => setHoveredEdgeId(null)}
              >
                {/* Wider Invisible Hit Target */}
                <line
                  x1={p1.x}
                  y1={p1.y}
                  x2={p2.x}
                  y2={p2.y}
                  stroke="transparent"
                  strokeWidth={24}
                />

                {/* Base Shadow / Glow line */}
                <line
                  x1={p1.x}
                  y1={p1.y}
                  x2={p2.x}
                  y2={p2.y}
                  stroke={color}
                  strokeWidth={strokeWidth + (isSelected || isHovered ? 6 : 2)}
                  strokeOpacity={isClosed ? 0.3 : (isSelected ? 0.6 : 0.25)}
                  filter={isPulsing ? "url(#glow-rose)" : undefined}
                />

                {/* Primary Physical Road Line */}
                <line
                  x1={p1.x}
                  y1={p1.y}
                  x2={p2.x}
                  y2={p2.y}
                  stroke={color}
                  strokeWidth={strokeWidth}
                  strokeDasharray={isClosed ? "8 6" : undefined}
                  strokeLinecap="round"
                  className={isPulsing ? "animate-pulse" : ""}
                />

                {/* Active Traffic Pulse Animation (Travelling dash) */}
                {!isClosed && evalData && evalData.current_flow_veh_per_hour > 0 && (
                  <line
                    x1={p1.x}
                    y1={p1.y}
                    x2={p2.x}
                    y2={p2.y}
                    stroke="#FFFFFF"
                    strokeWidth={2}
                    strokeOpacity={0.8}
                    strokeDasharray="6 34"
                    className="animate-flow-dash"
                  />
                )}

                {/* Edge Status Tag / Button at Midpoint */}
                <g transform={`translate(${midX}, ${midY})`}>
                  <rect
                    x={-42}
                    y={-14}
                    width={84}
                    height={28}
                    rx={14}
                    fill="#0F172A"
                    stroke={isSelected ? "#06B6D4" : (isClosed ? "#EF4444" : (isNewlyOverloaded ? "#F43F5E" : "#334155"))}
                    strokeWidth={isSelected ? 2 : 1.5}
                    className="transition-all duration-200 hover:scale-110"
                  />
                  <text
                    x={0}
                    y={3.5}
                    textAnchor="middle"
                    fill={isClosed ? "#EF4444" : (isNewlyOverloaded ? "#F43F5E" : "#94A3B8")}
                    fontSize="10"
                    fontWeight="700"
                    fontFamily="monospace"
                  >
                    {isClosed ? "CLOSED" : (evalData?.vc_ratio ? `${(evalData.vc_ratio).toFixed(2)} V/C` : `${edge.nominal_capacity_veh_per_hour}`)}
                  </text>
                </g>
              </g>
            );
          })}
        </g>

        {/* 2. Draw Nodes / Intersections & Facilities */}
        <g className="nodes-layer">
          {nodes.map((node) => {
            const pos = NODE_POSITIONS[node.id] || { x: 500, y: 340 };
            const isHospital = node.node_type === "critical_asset";
            const isZone = node.node_type === "zone";
            const isHovered = hoveredNodeId === node.id;

            return (
              <g
                key={node.id}
                transform={`translate(${pos.x}, ${pos.y})`}
                className="cursor-pointer"
                onMouseEnter={() => setHoveredNodeId(node.id)}
                onMouseLeave={() => setHoveredNodeId(null)}
              >
                {/* Hospital Radial Pulse */}
                {isHospital && (
                  <circle
                    r={36}
                    fill="rgba(244,63,94,0.15)"
                    stroke="#F43F5E"
                    strokeWidth={1.5}
                    strokeDasharray="4 4"
                    className="animate-pulse-glow"
                  />
                )}

                {/* Node Outer Ring */}
                <circle
                  r={isHospital ? 24 : (isZone ? 20 : 16)}
                  fill="#0F172A"
                  stroke={isHospital ? "#F43F5E" : (isZone ? "#06B6D4" : "#475569")}
                  strokeWidth={isHovered ? 3 : 2}
                  className="transition-transform duration-200 hover:scale-125 shadow-2xl"
                  filter={isHospital ? "url(#glow-rose)" : "url(#glow-cyan)"}
                />

                {/* Node Icon */}
                {isHospital ? (
                  <g transform="translate(-10, -10)">
                    <Hospital className="w-5 h-5 text-rose-400" />
                  </g>
                ) : isZone ? (
                  <g transform="translate(-8, -8)">
                    <Building className="w-4 h-4 text-cyan-400" />
                  </g>
                ) : (
                  <circle r={5} fill="#94A3B8" />
                )}

                {/* Node Label Below */}
                <g transform="translate(0, 32)">
                  <rect
                    x={-60}
                    y={-10}
                    width={120}
                    height={20}
                    rx={6}
                    fill="rgba(15,23,42,0.9)"
                    stroke="#334155"
                    strokeWidth={1}
                  />
                  <text
                    x={0}
                    y={4}
                    textAnchor="middle"
                    fill={isHospital ? "#FDA4AF" : (isZone ? "#A5F3FC" : "#E2E8F0")}
                    fontSize="10"
                    fontWeight="700"
                  >
                    {node.label || node.id}
                  </text>
                </g>
              </g>
            );
          })}
        </g>
      </svg>
    </div>
  );
};
