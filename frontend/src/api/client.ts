import {
    ComparisonResult,
    NetworkResponse,
    ScenarioPreset,
    SimulateRequest,
    SimulationResult,
} from "../types";

const API_BASE = "";

// Canonical Fallback Data for offline demo reliability
const MOCK_NETWORK: NetworkResponse = {
  network_id: "bengaluru_core_demo",
  name: "Bengaluru Central Arterial Corridor",
  nodes: [
    { id: "Zone_A", latitude: 12.925, longitude: 77.565, node_type: "zone", label: "Banashankari (West)", description: "Major residential commuter origin." },
    { id: "Junction_B", latitude: 12.917, longitude: 77.623, node_type: "junction", label: "Silk Board Interchange", description: "Critical primary arterial flyover & bridge." },
    { id: "Hospital_C", latitude: 12.958, longitude: 77.658, node_type: "critical_asset", label: "Manipal Trauma Center", description: "Level-1 emergency medical center." },
    { id: "Junction_E", latitude: 12.923, longitude: 77.648, node_type: "junction", label: "Agara / Sarjapur Junc.", description: "Southern collector junction." },
    { id: "Junction_F", latitude: 12.936, longitude: 77.628, node_type: "junction", label: "Sony World Hub", description: "2-lane bottleneck in residential commercial grid." },
    { id: "Zone_D", latitude: 12.975, longitude: 77.720, node_type: "zone", label: "Whitefield Tech Park", description: "High-density IT employer destination." },
    { id: "Zone_G", latitude: 12.978, longitude: 77.640, node_type: "junction", label: "Indiranagar 100ft Hub", description: "Northern emergency relief corridor." },
    { id: "Zone_A", latitude: 12.9255, longitude: 77.5650, node_type: "zone", label: "Banashankari / West Suburb", description: "Major residential commuter origin." },
    { id: "Junction_B", latitude: 12.9175, longitude: 77.6238, node_type: "junction", label: "Silk Board Interchange", description: "Critical primary arterial flyover & bridge." },
    { id: "Hospital_C", latitude: 12.9584, longitude: 77.6489, node_type: "critical_asset", label: "Manipal Trauma Center (Old Airport Rd)", description: "Level-1 emergency medical center." },
    { id: "Junction_E", latitude: 12.9230, longitude: 77.6480, node_type: "junction", label: "Agara / Sarjapur Junc.", description: "Southern collector junction." },
    { id: "Junction_F", latitude: 12.9360, longitude: 77.6280, node_type: "junction", label: "Sony World Koramangala Hub", description: "2-lane bottleneck in residential commercial grid." },
    { id: "Zone_D", latitude: 12.9860, longitude: 77.7340, node_type: "zone", label: "Whitefield ITPL Tech Park", description: "High-density IT employer destination." },
    { id: "Zone_G", latitude: 12.9780, longitude: 77.6400, node_type: "junction", label: "Indiranagar 100ft Hub", description: "Northern emergency relief corridor." },
  ],
  edges: [
    { id: "Bridge_A_B", source: "Zone_A", target: "Junction_B", length_km: 3.5, free_flow_speed_kmph: 60.0, nominal_capacity_veh_per_hour: 2400.0, road_class: "primary_arterial", baseline_flow_veh_per_hour: 400.0, status: "open", name: "Silk Board Flyover Bridge" },
    { id: "Arterial_B_C", source: "Junction_B", target: "Hospital_C", length_km: 2.5, free_flow_speed_kmph: 50.0, nominal_capacity_veh_per_hour: 2200.0, road_class: "arterial", baseline_flow_veh_per_hour: 200.0, status: "open", name: "Inner Ring Road Approach" },
    { id: "Arterial_C_D", source: "Hospital_C", target: "Zone_D", length_km: 3.0, free_flow_speed_kmph: 50.0, nominal_capacity_veh_per_hour: 2000.0, road_class: "arterial", baseline_flow_veh_per_hour: 100.0, status: "open", name: "Old Airport Road to Whitefield" },
    { id: "Collector_A_E", source: "Zone_A", target: "Junction_E", length_km: 4.5, free_flow_speed_kmph: 45.0, nominal_capacity_veh_per_hour: 1500.0, road_class: "collector", baseline_flow_veh_per_hour: 200.0, status: "open", name: "Agara Bypass Collector" },
    { id: "Bottleneck_E_F", source: "Junction_E", target: "Junction_F", length_km: 5.0, free_flow_speed_kmph: 40.0, nominal_capacity_veh_per_hour: 1400.0, road_class: "secondary", baseline_flow_veh_per_hour: 500.0, status: "open", name: "Koramangala 80ft Bottleneck" },
    { id: "Connector_F_C", source: "Junction_F", target: "Hospital_C", length_km: 2.0, free_flow_speed_kmph: 45.0, nominal_capacity_veh_per_hour: 1600.0, road_class: "collector", baseline_flow_veh_per_hour: 150.0, status: "open", name: "Sony World to Hospital" },
    { id: "Connector_F_D", source: "Junction_F", target: "Zone_D", length_km: 2.5, free_flow_speed_kmph: 45.0, nominal_capacity_veh_per_hour: 1600.0, road_class: "collector", baseline_flow_veh_per_hour: 100.0, status: "open", name: "Koramangala to Tech Park" },
    { id: "Connector_G_C", source: "Zone_G", target: "Hospital_C", length_km: 3.0, free_flow_speed_kmph: 45.0, nominal_capacity_veh_per_hour: 1800.0, road_class: "arterial", baseline_flow_veh_per_hour: 300.0, status: "open", name: "Indiranagar Emergency Link" },
    { id: "Connector_A_G", source: "Zone_A", target: "Zone_G", length_km: 6.0, free_flow_speed_kmph: 40.0, nominal_capacity_veh_per_hour: 1400.0, road_class: "secondary", baseline_flow_veh_per_hour: 200.0, status: "open", name: "West-North Relief Arterial" },
    {
      id: "Bridge_A_B",
      source: "Zone_A",
      target: "Junction_B",
      length_km: 3.5,
      free_flow_speed_kmph: 60.0,
      nominal_capacity_veh_per_hour: 2400.0,
      road_class: "primary_arterial",
      baseline_flow_veh_per_hour: 400.0,
      status: "open",
      name: "Silk Board Elevated Flyover Bridge",
      coordinates: [
        [12.9255, 77.5650],
        [12.9210, 77.5850],
        [12.9165, 77.6050],
        [12.9175, 77.6238],
      ],
    },
    {
      id: "Arterial_B_C",
      source: "Junction_B",
      target: "Hospital_C",
      length_km: 2.5,
      free_flow_speed_kmph: 50.0,
      nominal_capacity_veh_per_hour: 2200.0,
      road_class: "arterial",
      baseline_flow_veh_per_hour: 200.0,
      status: "open",
      name: "Inner Ring Road to Manipal Hospital",
      coordinates: [
        [12.9175, 77.6238],
        [12.9345, 77.6190],
        [12.9460, 77.6320],
        [12.9584, 77.6489],
      ],
    },
    {
      id: "Arterial_C_D",
      source: "Hospital_C",
      target: "Zone_D",
      length_km: 3.0,
      free_flow_speed_kmph: 50.0,
      nominal_capacity_veh_per_hour: 2000.0,
      road_class: "arterial",
      baseline_flow_veh_per_hour: 100.0,
      status: "open",
      name: "Old Airport Road to Whitefield",
      coordinates: [
        [12.9584, 77.6489],
        [12.9560, 77.6780],
        [12.9555, 77.7010],
        [12.9860, 77.7340],
      ],
    },
    {
      id: "Collector_A_E",
      source: "Zone_A",
      target: "Junction_E",
      length_km: 4.5,
      free_flow_speed_kmph: 45.0,
      nominal_capacity_veh_per_hour: 1500.0,
      road_class: "collector",
      baseline_flow_veh_per_hour: 200.0,
      status: "open",
      name: "Agara Bypass Collector",
      coordinates: [
        [12.9255, 77.5650],
        [12.9100, 77.5950],
        [12.9120, 77.6300],
        [12.9230, 77.6480],
      ],
    },
    {
      id: "Bottleneck_E_F",
      source: "Junction_E",
      target: "Junction_F",
      length_km: 5.0,
      free_flow_speed_kmph: 40.0,
      nominal_capacity_veh_per_hour: 1400.0,
      road_class: "secondary",
      baseline_flow_veh_per_hour: 500.0,
      status: "open",
      name: "Koramangala 80ft Bottleneck",
      coordinates: [
        [12.9230, 77.6480],
        [12.9290, 77.6370],
        [12.9360, 77.6280],
      ],
    },
    {
      id: "Connector_F_C",
      source: "Junction_F",
      target: "Hospital_C",
      length_km: 2.0,
      free_flow_speed_kmph: 45.0,
      nominal_capacity_veh_per_hour: 1600.0,
      road_class: "collector",
      baseline_flow_veh_per_hour: 150.0,
      status: "open",
      name: "Sony World to Hospital Link",
      coordinates: [
        [12.9360, 77.6280],
        [12.9430, 77.6360],
        [12.9584, 77.6489],
      ],
    },
    {
      id: "Connector_F_D",
      source: "Junction_F",
      target: "Zone_D",
      length_km: 2.5,
      free_flow_speed_kmph: 45.0,
      nominal_capacity_veh_per_hour: 1600.0,
      road_class: "collector",
      baseline_flow_veh_per_hour: 100.0,
      status: "open",
      name: "Koramangala to Tech Park Link",
      coordinates: [
        [12.9360, 77.6280],
        [12.9260, 77.6760],
        [12.9600, 77.7100],
        [12.9860, 77.7340],
      ],
    },
    {
      id: "Connector_G_C",
      source: "Zone_G",
      target: "Hospital_C",
      length_km: 3.0,
      free_flow_speed_kmph: 45.0,
      nominal_capacity_veh_per_hour: 1800.0,
      road_class: "arterial",
      baseline_flow_veh_per_hour: 300.0,
      status: "open",
      name: "Indiranagar Emergency Link",
      coordinates: [
        [12.9780, 77.6400],
        [12.9690, 77.6420],
        [12.9584, 77.6489],
      ],
    },
    {
      id: "Connector_A_G",
      source: "Zone_A",
      target: "Zone_G",
      length_km: 6.0,
      free_flow_speed_kmph: 40.0,
      nominal_capacity_veh_per_hour: 1400.0,
      road_class: "secondary",
      baseline_flow_veh_per_hour: 200.0,
      status: "open",
      name: "West-North Relief Arterial",
      coordinates: [
        [12.9255, 77.5650],
        [12.9450, 77.5850],
        [12.9720, 77.6100],
        [12.9780, 77.6400],
      ],
    },
  ],
  critical_assets: [
    { id: "manipal_trauma_center", node_id: "Hospital_C", asset_type: "hospital", criticality_weight: 1.5, name: "Manipal City Trauma & Emergency Center" }
  ],
  pois: [
    { id: "poi_hospital_c", name: "Manipal Trauma Center (Old Airport Rd)", category: "hospital", node_id: "Hospital_C", coordinates: [77.6489, 12.9584] },
    { id: "poi_st_johns", name: "St. John's Medical College & Hospital", category: "hospital", node_id: "Junction_B", coordinates: [77.6190, 12.9345] },
    { id: "poi_nimhans", name: "NIMHANS Neuro Trauma Center", category: "hospital", node_id: "Zone_A", coordinates: [77.5950, 12.9405] },
    { id: "poi_silk_board", name: "Silk Board Central Interchange", category: "junction", node_id: "Junction_B", coordinates: [77.6238, 12.9175] },
    { id: "poi_sony_world", name: "Sony World Koramangala Hub", category: "junction", node_id: "Junction_F", coordinates: [77.6280, 12.9360] },
    { id: "poi_itpl", name: "ITPL Whitefield Tech Corridor", category: "tech_hub", node_id: "Zone_D", coordinates: [77.7340, 12.9860] },
  ]
};

const MOCK_PRESETS: ScenarioPreset[] = [
  {
    id: "bridge_closure",
    name: "Silk Board Bridge Inspection Closure",
    description: "Acute 100% closure of Silk Board Bridge due to structural inspection.",
    icon: "AlertTriangle",
    category: "closure",
    disruptions: [{ asset_id: "Bridge_A_B", disruption_type: "closure", capacity_multiplier: 0.0 }],
    recommended_mitigation_id: "mitigation_reroute"
  },
  {
    id: "scenario_silk_board_collapse",
    name: "Silk Board Elevated Flyover Structural Closure",
    description: "Acute 100% shutdown of Silk Board Elevated Highway. Diverts 5,000+ veh/h onto BTM & Koramangala.",
    icon: "AlertTriangle",
    category: "closure",
    disruptions: [{ asset_id: "Edge_SilkBoard_Hosur", disruption_type: "closure", capacity_multiplier: 0.0 }],
    recommended_mitigation_id: "scenario_green_corridor_mitigation"
  },
  {
    id: "monsoon_flooding",
    name: "Central Arterial Flash Waterlogging",
    description: "50% capacity loss on primary corridors due to heavy waterlogging.",
    icon: "CloudRain",
    category: "monsoon",
    disruptions: [
      { asset_id: "Bridge_A_B", disruption_type: "weather", capacity_multiplier: 0.5 },
      { asset_id: "Bottleneck_E_F", disruption_type: "weather", capacity_multiplier: 0.5 }
    ]
  },
  {
    id: "scenario_bellandur_flood",
    name: "Bellandur ORR & Sarjapur Flash Flood",
    description: "Heavy 60mm/hr monsoon downpour cuts Outer Ring Road capacity by 60%.",
    icon: "CloudRain",
    category: "monsoon",
    disruptions: [
      { asset_id: "Edge_Sarjapur_Bellandur", disruption_type: "weather", capacity_multiplier: 0.4 },
      { asset_id: "Edge_Bellandur_Marathahalli", disruption_type: "weather", capacity_multiplier: 0.4 }
    ]
  },
  {
    id: "metro_construction",
    name: "Inner Ring Road Metro Line 3 Works",
    description: "Single lane blockage on Inner Ring Road approach reducing throughput by 35%.",
    icon: "Construction",
    category: "construction",
    disruptions: [{ asset_id: "Arterial_B_C", disruption_type: "construction", capacity_multiplier: 0.65 }]
  },
  {
    id: "scenario_mg_road_construction",
    name: "Namma Metro Line 6 Construction (MG Road & Trinity)",
    description: "Barricaded arterial lanes reduce throughput by 50% along Trinity Circle & Anil Kumble Circle.",
    icon: "Construction",
    category: "construction",
    disruptions: [{ asset_id: "Edge_Trinity_AnilKumble", disruption_type: "construction", capacity_multiplier: 0.5 }]
  },
  {
    id: "scenario_itpl_summit",
    name: "ITPL Tech Summit Peak Hour Surge",
    description: "Major global tech convention in Whitefield creates 35% commuter surge on Old Airport Road.",
    icon: "Zap",
    category: "events",
    disruptions: [
      { asset_id: "Arterial_C_D", disruption_type: "partial_closure", capacity_multiplier: 0.75 }
    ]
  },
  {
    id: "mitigation_reroute",
    name: "Active Police Rerouting & Relief Lane",
    description: "Deployment of traffic wardens and dedicated signal green-waves on North Relief corridor.",
    icon: "ShieldCheck",
    category: "emergency",
    disruptions: []
  },
  {
    id: "scenario_green_corridor_mitigation",
    name: "Active Traffic Police Emergency Green Wave",
    description: "Traffic wardens establish dedicated priority green-waves for Manipal, Victoria, and NIMHANS ambulances.",
    icon: "ShieldCheck",
    category: "emergency",
    disruptions: []
  }
];

export async function fetchNetwork(): Promise<NetworkResponse> {
  try {
    const res = await fetch(`${API_BASE}/api/network`);
    if (!res.ok) throw new Error("Backend unavailable");
    return await res.json();
  } catch (err) {
    console.warn("Using offline benchmark network data:", err);
    return MOCK_NETWORK;
  }
}

export async function fetchPresets(): Promise<ScenarioPreset[]> {
  try {
    const res = await fetch(`${API_BASE}/api/scenarios/presets`);
    if (!res.ok) throw new Error("Backend unavailable");
    return await res.json();
  } catch (err) {
    return MOCK_PRESETS;
  }
}

export async function simulateScenario(req: SimulateRequest): Promise<SimulationResult> {
  try {
    const res = await fetch(`${API_BASE}/api/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req),
    });
    if (!res.ok) throw new Error(`Simulation failed: ${res.statusText}`);
    return await res.json();
  } catch (err) {
    console.warn("Executing local simulation fallback:", err);
    // Simple deterministic client fallback matching Part A/B
    const isClosed = req.disruptions.some(d => d.asset_id === "Bridge_A_B" && d.capacity_multiplier === 0);
    const mockEdges: Record<string, any> = {};
    MOCK_NETWORK.edges.forEach(e => {
      const isDisrupted = req.disruptions.find(d => d.asset_id === e.id);
      const mult = isDisrupted ? isDisrupted.capacity_multiplier : 1.0;
      const c_eff = e.nominal_capacity_veh_per_hour * mult;
      let flow = e.baseline_flow_veh_per_hour;
      if (e.id === "Bridge_A_B") flow = isClosed ? 0 : 2000;
      else if (e.id === "Bottleneck_E_F") flow = isClosed ? 2100 : 500;
      else if (e.id === "Collector_A_E") flow = isClosed ? 1800 : 200;
      else if (e.id === "Connector_F_C") flow = isClosed ? 1350 : 150;

      const vc = c_eff > 0 ? flow / c_eff : null;
      const t0 = (e.length_km / e.free_flow_speed_kmph) * 60;
      const tt = (c_eff > 0 && vc !== null) ? t0 * (1 + 0.15 * Math.pow(vc, 4)) : null;

      mockEdges[e.id] = {
        edge_id: e.id,
        source: e.source,
        target: e.target,
        length_km: e.length_km,
        free_flow_speed_kmph: e.free_flow_speed_kmph,
        nominal_capacity_veh_per_hour: e.nominal_capacity_veh_per_hour,
        effective_capacity_veh_per_hour: c_eff,
        current_flow_veh_per_hour: flow,
        vc_ratio: vc,
        free_flow_time_minutes: t0,
        travel_time_minutes: tt,
        delay_minutes_per_vehicle: tt && t0 ? Math.max(0, tt - t0) : 0,
        total_delay_veh_hours: tt && t0 ? (flow * Math.max(0, tt - t0)) / 60 : 0,
        is_overloaded: vc !== null && vc > 1.0,
        is_closed: c_eff === 0,
        status: c_eff === 0 ? "closed" : (mult < 1 ? "restricted" : "open"),
      };
    });

    return {
      scenario_id: "sim_fallback",
      baseline_edges: mockEdges,
      scenario_edges: mockEdges,
      primary_disrupted_edges: req.disruptions.filter(d => d.capacity_multiplier < 1).map(d => d.asset_id),
      newly_overloaded_edges: isClosed ? ["Collector_A_E", "Bottleneck_E_F"] : [],
      persistently_overloaded_edges: [],
      changed_routes: isClosed ? [{
        od_id: "OD_ZoneA_HospitalC",
        origin: "Zone_A",
        destination: "Hospital_C",
        demand_veh_per_hour: 1200,
        baseline_edge_ids: ["Bridge_A_B", "Arterial_B_C"],
        scenario_edge_ids: ["Collector_A_E", "Bottleneck_E_F", "Connector_F_C"],
        rerouted: true,
        unserved: false,
        baseline_distance_km: 6.0,
        scenario_distance_km: 11.5,
        extra_distance_km: 5.5,
        baseline_travel_time_minutes: 7.0,
        scenario_travel_time_minutes: 23.9,
        travel_time_change_minutes: 16.9,
      }] : [],
      all_routes: [],
      unserved_od_ids: [],
      total_travel_time_change_minutes: isClosed ? 30.8 : 0.0,
      total_delay_change_vehicle_hours: isClosed ? 245.3 : 0.0,
      critical_service_impacts: isClosed ? [{
        asset_id: "manipal_trauma_center",
        node_id: "Hospital_C",
        asset_type: "hospital",
        origin_zone: "Zone_A",
        baseline_access_time_minutes: 7.0,
        scenario_access_time_minutes: 23.9,
        response_time_delta_minutes: 16.9,
        access_lost: false,
      }] : [],
      explainability: isClosed ? [
        "Primary structural incident closed Silk Board Bridge (Bridge_A_B).",
        "1,200 veh/h commuter & patient demand diverted to Agara/Koramangala collector routes.",
        "Secondary bottleneck overloads triggered on Bottleneck_E_F (V/C: 1.50) and Collector_A_E (V/C: 1.20).",
        "Emergency hospital transit time to Manipal Trauma Center increased by +16.9 minutes (+241%)."
      ] : ["Network running under nominal baseline flow."],
      iterations_completed: 1,
    };
  }
}

export async function compareScenarios(a: SimulateRequest, b: SimulateRequest): Promise<ComparisonResult> {
  try {
    const res = await fetch(`${API_BASE}/api/scenarios/compare`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario_a: a, scenario_b: b }),
    });
    if (!res.ok) throw new Error("Comparison failed");
    return await res.json();
  } catch (err) {
    return {
      scenario_a_metrics: { total_delay_change_veh_h: 245.3, newly_overloaded_count: 2, unserved_od_count: 0 },
      scenario_b_metrics: { total_delay_change_veh_h: 42.1, newly_overloaded_count: 0, unserved_od_count: 0 },
      net_delay_reduction_veh_hours: 203.2,
      percentage_improvement: 82.8,
      summary_verdict: "Active mitigation strategy reduced system delay by 82.8% (203.2 vehicle-hours saved).",
    };
  }
}
