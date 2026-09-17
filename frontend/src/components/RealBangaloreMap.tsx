import L from "leaflet";
import {
    Compass,
    RotateCcw,
    ZoomIn,
    ZoomOut
} from "lucide-react";
import React, { useEffect, useMemo, useRef, useState } from "react";
import {
    CriticalAssetData,
    EdgeData,
    NodeData,
    POIData,
    SimulationResult,
} from "../types";

interface RealBangaloreMapProps {
  nodes: NodeData[];
  edges: EdgeData[];
  criticalAssets: CriticalAssetData[];
  pois?: POIData[];
  simulationResult: SimulationResult | null;
  selectedEdgeId: string | null;
  onSelectEdge: (edgeId: string | null) => void;
  onQuickToggleDisruption: (edgeId: string) => void;
}

type TileProvider = "carto_dark" | "satellite" | "osm";
type RoadGeometry = Record<string, [number, number][]>;

const TILE_LAYERS: Record<
  TileProvider,
  { url: string; attribution: string; name: string; subdomains: string; maxZoom: number }
> = {
  satellite: {
    name: "Satellite",
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attribution: '&copy; <a href="https://www.esri.com/">Esri</a>, Earthstar Geographics',
    subdomains: "",
    maxZoom: 19,
  },
  carto_dark: {
    name: "Dark Matter",
    url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
    attribution: '&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://openstreetmap.org">OSM</a>',
    subdomains: "abcd",
    maxZoom: 20,
  },
  osm: {
    name: "Street Map",
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    subdomains: "abc", // OpenStreetMap only has a, b, c. "d" causes DNS errors resulting in black square voids!
    maxZoom: 19,
  },
};

// Bengaluru default center
const BENGALURU_CENTER: [number, number] = [12.945, 77.640];
const DEFAULT_ZOOM = 13;

export const RealBangaloreMap: React.FC<RealBangaloreMapProps> = ({
  nodes,
  edges,
  criticalAssets,
  pois = [],
  simulationResult,
  selectedEdgeId,
  onSelectEdge,
  onQuickToggleDisruption,
}) => {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const tileLayerRef = useRef<L.TileLayer | null>(null);
  const polylineLayerGroupRef = useRef<L.LayerGroup | null>(null);
  const markerLayerGroupRef = useRef<L.LayerGroup | null>(null);

  const [activeTile, setActiveTile] = useState<TileProvider>("satellite");
  const [hoveredEdgeId, setHoveredEdgeId] = useState<string | null>(null);
  const [roadGeometries, setRoadGeometries] = useState<RoadGeometry>({});
  const [isRoutingRoads, setIsRoutingRoads] = useState(false);

  const nodeMap = useMemo(() => {
    const map = new Map<string, NodeData>();
    nodes.forEach((n) => map.set(n.id, n));
    return map;
  }, [nodes]);

  const edgeEvals = simulationResult?.scenario_edges || {};

  // Snap the abstract network links to the real drivable road network. The
  // supplied coordinates are retained only when routing is unavailable.
  useEffect(() => {
    if (!edges.length || !nodes.length) return;

    const controller = new AbortController();
    let isCurrent = true;
    setIsRoutingRoads(true);

    const getEndpoints = (edge: EdgeData): [number, number][] => {
      const source = nodeMap.get(edge.source);
      const target = nodeMap.get(edge.target);
      if (
        source?.latitude !== undefined && source.longitude !== undefined &&
        target?.latitude !== undefined && target.longitude !== undefined
      ) {
        return [
          [source.latitude, source.longitude],
          [target.latitude, target.longitude],
        ];
      }
      return (edge.coordinates || []).map((point) =>
        point[0] > 70 ? [point[1], point[0]] : point
      );
    };

    const routeEdge = async (edge: EdgeData): Promise<[string, [number, number][]] | null> => {
      const endpoints = getEndpoints(edge);
      if (endpoints.length < 2) return null;

      const cacheKey = `urbanresilience-road-route-${edge.id}-${endpoints.flat().join("-")}`;
      const cached = sessionStorage.getItem(cacheKey);
      if (cached) return [edge.id, JSON.parse(cached) as [number, number][]];

      const coordinates = endpoints.map(([lat, lon]) => `${lon},${lat}`).join(";");
      const response = await fetch(
        `https://router.project-osrm.org/route/v1/driving/${coordinates}?overview=full&geometries=geojson&steps=false`,
        { signal: controller.signal }
      );
      if (!response.ok) return null;

      const result = (await response.json()) as {
        code: string;
        routes?: Array<{ geometry: { coordinates: [number, number][] } }>;
      };
      const geometry = result.routes?.[0]?.geometry.coordinates.map(([lon, lat]) => [lat, lon] as [number, number]);
      if (result.code !== "Ok" || !geometry || geometry.length < 2) return null;

      sessionStorage.setItem(cacheKey, JSON.stringify(geometry));
      return [edge.id, geometry];
    };

    Promise.all(edges.map((edge) => routeEdge(edge).catch(() => null)))
      .then((routes) => {
        if (!isCurrent) return;
        setRoadGeometries(Object.fromEntries(routes.filter((route): route is [string, [number, number][]] => route !== null)));
      })
      .catch((error: unknown) => {
        if ((error as DOMException).name !== "AbortError") {
          console.warn("Road routing unavailable; using corridor fallback geometry.", error);
        }
      })
      .finally(() => {
        if (isCurrent) setIsRoutingRoads(false);
      });

    return () => {
      isCurrent = false;
      controller.abort();
    };
  }, [edges, nodes.length, nodeMap]);

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: BENGALURU_CENTER,
      zoom: DEFAULT_ZOOM,
      zoomControl: false,
      attributionControl: true,
      minZoom: 10,
      maxZoom: 18,
    });

    const tileConfig = TILE_LAYERS[activeTile];
    const tileLayer = L.tileLayer(tileConfig.url, {
      attribution: tileConfig.attribution,
      subdomains: tileConfig.subdomains,
      maxZoom: tileConfig.maxZoom,
    }).addTo(map);

    tileLayerRef.current = tileLayer;

    const polylineGroup = L.layerGroup().addTo(map);
    const markerGroup = L.layerGroup().addTo(map);

    polylineLayerGroupRef.current = polylineGroup;
    markerLayerGroupRef.current = markerGroup;
    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update Tile Layer when user switches
  useEffect(() => {
    if (!mapInstanceRef.current || !tileLayerRef.current) return;
    const tileConfig = TILE_LAYERS[activeTile];
    mapInstanceRef.current.removeLayer(tileLayerRef.current);

    const newTileLayer = L.tileLayer(tileConfig.url, {
      attribution: tileConfig.attribution,
      subdomains: tileConfig.subdomains,
      maxZoom: tileConfig.maxZoom,
    }).addTo(mapInstanceRef.current);

    tileLayerRef.current = newTileLayer;
    newTileLayer.bringToBack();
  }, [activeTile]);

  // Render Polylines and Dynamic Flows
  useEffect(() => {
    if (!mapInstanceRef.current || !polylineLayerGroupRef.current) return;

    polylineLayerGroupRef.current.clearLayers();

    edges.forEach((edge) => {
      const evalData = edgeEvals[edge.id];
      const isDisrupted = simulationResult?.primary_disrupted_edges.includes(edge.id);
      const isNewlyOverloaded = simulationResult?.newly_overloaded_edges.includes(edge.id);
      const isSelected = selectedEdgeId === edge.id;
      const isHovered = hoveredEdgeId === edge.id;
      const isClosed = evalData ? evalData.is_closed : edge.status === "closed";

      // Compute color based on V/C
      let color = "#38BDF8"; // Cyan baseline
      let weight = edge.road_class === "primary_arterial" ? 7 : edge.road_class === "arterial" ? 6 : 5;
      let dashArray: string | undefined = undefined;
      let opacity = 0.9;

      if (isClosed) {
        color = "#EF4444"; // Vivid Red
        weight = 8;
        dashArray = "8, 6";
      } else if (isNewlyOverloaded || (evalData?.vc_ratio && evalData.vc_ratio > 1.0)) {
        color = "#F43F5E"; // Rose / Crimson
        weight = 8;
        dashArray = "12, 4";
      } else if (evalData?.vc_ratio && evalData.vc_ratio > 0.85) {
        color = "#F97316"; // Orange
        weight = 7;
      } else if (evalData?.vc_ratio && evalData.vc_ratio > 0.70) {
        color = "#F59E0B"; // Amber
        weight = 6;
      } else {
        color = "#10B981"; // Emerald
      }

      if (isSelected) {
        weight += 3;
        opacity = 1.0;
      }

      // Extract coordinates
      let latlngs: [number, number][] = [];
      if (roadGeometries[edge.id]) {
        latlngs = roadGeometries[edge.id];
      } else if (edge.coordinates && edge.coordinates.length > 0) {
        // If coordinate is [lat, lon] or [lon, lat]
        latlngs = edge.coordinates.map((pt) => {
          if (pt[0] > 70) return [pt[1], pt[0]]; // [lon, lat] -> [lat, lon]
          return [pt[0], pt[1]];
        });
      } else {
        const srcNode = nodeMap.get(edge.source);
        const tgtNode = nodeMap.get(edge.target);
        if (srcNode && tgtNode && srcNode.latitude && srcNode.longitude && tgtNode.latitude && tgtNode.longitude) {
          latlngs = [
            [srcNode.latitude, srcNode.longitude],
            [tgtNode.latitude, tgtNode.longitude],
          ];
        }
      }

      if (latlngs.length < 2) return;

      // 1. Background glow / casing polyline
      const casing = L.polyline(latlngs, {
        color: isSelected ? "#38BDF8" : isClosed ? "#EF4444" : isNewlyOverloaded ? "#F43F5E" : "#0F172A",
        weight: weight + (isSelected ? 6 : 4),
        opacity: isSelected ? 0.8 : 0.5,
        lineCap: "round",
        lineJoin: "round",
      });

      // 2. Main foreground road polyline
      const polyline = L.polyline(latlngs, {
        color,
        weight,
        opacity,
        dashArray,
        lineCap: "round",
        lineJoin: "round",
      });

      // Interactive Events
      polyline.on("click", (e) => {
        L.DomEvent.stopPropagation(e);
        onSelectEdge(edge.id);
      });

      polyline.on("mouseover", () => {
        setHoveredEdgeId(edge.id);
      });

      polyline.on("mouseout", () => {
        setHoveredEdgeId(null);
      });

      // Rich HTML Tooltip / Popup
      const vcRatio = evalData?.vc_ratio !== null && evalData?.vc_ratio !== undefined ? evalData.vc_ratio.toFixed(2) : (edge.baseline_flow_veh_per_hour / edge.nominal_capacity_veh_per_hour).toFixed(2);
      const flow = evalData?.current_flow_veh_per_hour ? Math.round(evalData.current_flow_veh_per_hour) : Math.round(edge.baseline_flow_veh_per_hour);
      const cap = evalData?.effective_capacity_veh_per_hour ? Math.round(evalData.effective_capacity_veh_per_hour) : Math.round(edge.nominal_capacity_veh_per_hour);
      const delayMin = evalData?.delay_minutes_per_vehicle ? evalData.delay_minutes_per_vehicle.toFixed(1) : "0.0";

      const popupHtml = `
        <div class="p-3.5 min-w-[240px] text-slate-100 font-sans">
          <div class="flex items-center justify-between gap-2 border-b border-slate-700/80 pb-2 mb-2.5">
            <div>
              <h4 class="font-bold text-xs text-white uppercase tracking-wider">${edge.name || edge.id}</h4>
              <p class="text-[10px] text-slate-400 capitalize">${edge.road_class.replace("_", " ")} Corridor</p>
            </div>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
              isClosed
                ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                : isNewlyOverloaded || Number(vcRatio) > 1.0
                ? "bg-red-500/20 text-red-400 border border-red-500/30"
                : Number(vcRatio) > 0.85
                ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
            }">
              ${isClosed ? "CLOSED" : `V/C: ${vcRatio}`}
            </span>
          </div>

          <div class="grid grid-cols-2 gap-2 text-[11px] mb-3">
            <div class="bg-slate-900/90 p-2 rounded-lg border border-slate-800">
              <span class="text-[10px] text-slate-400 block uppercase">Current Flow</span>
              <span class="font-mono font-bold text-cyan-300">${flow}</span>
              <span class="text-[9px] text-slate-500"> veh/h</span>
            </div>
            <div class="bg-slate-900/90 p-2 rounded-lg border border-slate-800">
              <span class="text-[10px] text-slate-400 block uppercase">Capacity</span>
              <span class="font-mono font-bold text-slate-200">${cap}</span>
              <span class="text-[9px] text-slate-500"> veh/h</span>
            </div>
            <div class="bg-slate-900/90 p-2 rounded-lg border border-slate-800">
              <span class="text-[10px] text-slate-400 block uppercase">Added Delay</span>
              <span class="font-mono font-bold ${Number(delayMin) > 0 ? "text-rose-400" : "text-emerald-400"}">+${delayMin} min</span>
            </div>
            <div class="bg-slate-900/90 p-2 rounded-lg border border-slate-800">
              <span class="text-[10px] text-slate-400 block uppercase">Length</span>
              <span class="font-mono font-bold text-slate-300">${edge.length_km.toFixed(1)} km</span>
            </div>
          </div>

          <button id="toggle-btn-${edge.id}" class="w-full py-1.5 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
            isClosed
              ? "bg-emerald-600 hover:bg-emerald-500 text-white"
              : "bg-rose-600 hover:bg-rose-500 text-white shadow-lg shadow-rose-600/30"
          }">
            <span>${isClosed ? "⚡ Reopen Corridor" : "🚨 100% Emergency Closure"}</span>
          </button>
        </div>
      `;

      polyline.bindPopup(popupHtml, {
        closeButton: false,
        className: "custom-leaflet-popup",
      });

      polyline.on("popupopen", () => {
        setTimeout(() => {
          const btn = document.getElementById(`toggle-btn-${edge.id}`);
          if (btn) {
            btn.onclick = () => {
              onQuickToggleDisruption(edge.id);
              mapInstanceRef.current?.closePopup();
            };
          }
        }, 50);
      });

      polylineLayerGroupRef.current?.addLayer(casing);
      polylineLayerGroupRef.current?.addLayer(polyline);
    });
  }, [edges, edgeEvals, simulationResult, selectedEdgeId, hoveredEdgeId, nodeMap, roadGeometries, onSelectEdge, onQuickToggleDisruption]);

  // Render Node and Facility Markers
  useEffect(() => {
    if (!mapInstanceRef.current || !markerLayerGroupRef.current) return;

    markerLayerGroupRef.current.clearLayers();

    // 1. Render Nodes
    nodes.forEach((node) => {
      if (!node.latitude || !node.longitude) return;

      const isHospital = node.id.includes("Hospital") || node.node_type === "critical_asset";
      const isJunction = node.node_type === "junction";
      const isZone = node.node_type === "zone";

      const hospitalImpact = simulationResult?.critical_service_impacts.find(
        (c) => c.node_id === node.id || node.id.includes("Hospital")
      );
      const hospitalDelta = hospitalImpact?.response_time_delta_minutes;

      let iconHtml = "";
      let iconSize: [number, number] = [32, 32];

      if (isHospital) {
        iconSize = [40, 40];
        iconHtml = `
          <div class="relative flex items-center justify-center w-10 h-10">
            <div class="absolute inset-0 rounded-2xl bg-rose-500/20 border-2 border-rose-400 animate-pulse-glow shadow-[0_0_20px_#F43F5E]"></div>
            <div class="relative w-8 h-8 rounded-xl bg-slate-900 border border-rose-500 flex items-center justify-center text-rose-400 font-bold shadow-lg">
              🏥
            </div>
            ${
              hospitalDelta && hospitalDelta > 0.1
                ? `<span class="absolute -top-2 -right-3 text-[9px] font-mono font-extrabold px-1.5 py-0.5 rounded-full bg-rose-600 text-white border border-rose-300 shadow-md">
                    +${hospitalDelta.toFixed(1)}m
                  </span>`
                : ""
            }
          </div>
        `;
      } else if (isJunction) {
        iconHtml = `
          <div class="relative flex items-center justify-center w-8 h-8">
            <div class="w-6 h-6 rounded-xl bg-[#0F172A] border-2 border-cyan-400 flex items-center justify-center shadow-[0_0_12px_#38BDF8]">
              <div class="w-2 h-2 rounded-full bg-cyan-400"></div>
            </div>
          </div>
        `;
      } else if (isZone) {
        iconHtml = `
          <div class="relative flex items-center justify-center w-8 h-8">
            <div class="w-6 h-6 rounded-xl bg-[#0F172A] border-2 border-indigo-400 flex items-center justify-center shadow-[0_0_12px_#818CF8]">
              <div class="w-2 h-2 rounded-full bg-indigo-400"></div>
            </div>
          </div>
        `;
      }

      const customIcon = L.divIcon({
        html: iconHtml,
        className: "custom-map-marker",
        iconSize,
        iconAnchor: [iconSize[0] / 2, iconSize[1] / 2],
      });

      const marker = L.marker([node.latitude, node.longitude], { icon: customIcon });

      marker.bindTooltip(
        `
        <div class="p-1.5 text-xs text-slate-100 font-sans">
          <p class="font-bold text-white">${node.label || node.id}</p>
          <p class="text-[10px] text-slate-400">${node.description || node.node_type}</p>
          ${
            hospitalDelta && hospitalDelta > 0.1
              ? `<p class="text-[10px] text-rose-400 font-bold mt-1">⚠️ Emergency Access Delay: +${hospitalDelta.toFixed(1)} min</p>`
              : ""
          }
        </div>
        `,
        { direction: "top", offset: [0, -16], className: "custom-leaflet-tooltip" }
      );

      markerLayerGroupRef.current?.addLayer(marker);
    });
  }, [nodes, simulationResult]);

  // Controls Handlers
  const handleZoomIn = () => mapInstanceRef.current?.zoomIn();
  const handleZoomOut = () => mapInstanceRef.current?.zoomOut();
  const handleResetView = () => mapInstanceRef.current?.setView(BENGALURU_CENTER, DEFAULT_ZOOM);

  return (
    <div id="tour-map-canvas" className="relative w-full h-full min-h-[540px] bg-[#070B14] rounded-2xl overflow-hidden border border-slate-800 shadow-2xl flex flex-col">
      {/* Top Map Header Overlay */}
      <div className="absolute top-3 left-3 z-[400] flex items-center gap-2 bg-[#0F172A]/90 backdrop-blur-xl border border-slate-800 px-3.5 py-2 rounded-xl shadow-2xl">
        <Compass className="w-4 h-4 text-cyan-400 animate-spin-slow" />
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-black tracking-wider text-white uppercase">
              Bengaluru GIS Twin
            </span>
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          </div>
          <p className="text-[10px] font-mono text-slate-400">
            {isRoutingRoads ? "Snapping corridors to roads…" : "Road-aligned GPS corridors"}
          </p>
        </div>
      </div>

      {/* Layer Switcher & Map Controls (Top-Right) */}
      <div className="absolute top-3 right-3 z-[400] flex items-center gap-2">
        {/* Layer Selector */}
        <div className="flex items-center bg-[#0F172A]/90 backdrop-blur-xl border border-slate-800 p-1 rounded-xl shadow-2xl">
          {(["carto_dark", "satellite", "osm"] as TileProvider[]).map((tp) => (
            <button
              key={tp}
              onClick={() => setActiveTile(tp)}
              className={`px-2.5 py-1 text-[10px] font-bold rounded-lg transition-all ${
                activeTile === tp
                  ? "bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              {TILE_LAYERS[tp].name}
            </button>
          ))}
        </div>

        {/* Zoom & Reset Buttons */}
        <div className="flex items-center bg-[#0F172A]/90 backdrop-blur-xl border border-slate-800 p-1 rounded-xl shadow-2xl gap-0.5">
          <button
            onClick={handleZoomIn}
            className="p-1.5 text-slate-300 hover:text-cyan-400 rounded-lg hover:bg-slate-800 transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={handleZoomOut}
            className="p-1.5 text-slate-300 hover:text-cyan-400 rounded-lg hover:bg-slate-800 transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            onClick={handleResetView}
            className="p-1.5 text-slate-300 hover:text-cyan-400 rounded-lg hover:bg-slate-800 transition-colors"
            title="Reset View"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Real Map Leaflet Container */}
      <div ref={mapContainerRef} className="w-full h-full flex-1 z-0" />

      {/* Bottom Floating Map Legend */}
      <div className="absolute bottom-3 left-3 z-[400] bg-[#0F172A]/90 backdrop-blur-xl border border-slate-800 px-4 py-2.5 rounded-2xl shadow-2xl flex items-center gap-4 text-[11px] text-slate-300">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-[#10B981]" />
          <span className="text-slate-400 text-[10px]">Normal (V/C &lt; 0.70)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-[#F59E0B]" />
          <span className="text-slate-400 text-[10px]">Stressed (0.70 - 0.85)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-[#F97316]" />
          <span className="text-slate-400 text-[10px]">Near Overload (0.85 - 1.0)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-[#F43F5E] animate-ping" />
          <span className="text-rose-400 text-[10px] font-bold">Overloaded (V/C &gt; 1.0)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-[#EF4444] border border-white" />
          <span className="text-red-400 text-[10px] font-bold">Closed (0% Cap)</span>
        </div>
      </div>
    </div>
  );
};
