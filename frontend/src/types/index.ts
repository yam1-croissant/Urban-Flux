export interface NodeData {
  id: string;
  latitude?: number;
  longitude?: number;
  node_type: "intersection" | "junction" | "zone" | "critical_asset";
  label?: string;
  description?: string;
  x?: number; // Canvas viewport X
  y?: number; // Canvas viewport Y
}

export interface EdgeData {
  id: string;
  source: string;
  target: string;
  length_km: number;
  free_flow_speed_kmph: number;
  nominal_capacity_veh_per_hour: number;
  lanes?: number;
  road_class: string;
  baseline_flow_veh_per_hour: number;
  status: "open" | "restricted" | "closed";
  name?: string;
  coordinates?: [number, number][]; // [[lat, lon], ...] or [[lon, lat], ...]
}

export interface CriticalAssetData {
  id: string;
  node_id: string;
  asset_type: string;
  criticality_weight: number;
  name?: string;
}

export interface POIData {
  id: string;
  name: string;
  category: string;
  node_id: string;
  coordinates: [number, number]; // [lon, lat] or [lat, lon]
}

export interface NetworkResponse {
  network_id: string;
  name: string;
  nodes: NodeData[];
  edges: EdgeData[];
  critical_assets: CriticalAssetData[];
  pois?: POIData[];
}

export interface DisruptionInput {
  asset_id: string;
  disruption_type: "closure" | "partial_closure" | "weather" | "construction";
  capacity_multiplier: number; // 0.0 to 1.0
}

export interface SimulateRequest {
  disruptions: DisruptionInput[];
  iteration_limit?: number;
}

export interface EdgeEvaluation {
  edge_id: string;
  source: string;
  target: string;
  length_km: number;
  free_flow_speed_kmph: number;
  nominal_capacity_veh_per_hour: number;
  effective_capacity_veh_per_hour: number;
  current_flow_veh_per_hour: number;
  vc_ratio: number | null;
  free_flow_time_minutes: number;
  travel_time_minutes: number | null;
  delay_minutes_per_vehicle: number | null;
  total_delay_veh_hours: number | null;
  is_overloaded: boolean;
  is_closed: boolean;
  status: string;
}

export interface ODRouteImpact {
  od_id: string;
  origin: string;
  destination: string;
  demand_veh_per_hour: number;
  baseline_edge_ids: string[];
  scenario_edge_ids: string[] | null;
  rerouted: boolean;
  unserved: boolean;
  baseline_distance_km: number;
  scenario_distance_km: number | null;
  extra_distance_km: number | null;
  baseline_travel_time_minutes: number;
  scenario_travel_time_minutes: number | null;
  travel_time_change_minutes: number | null;
}

export interface CriticalServiceImpact {
  asset_id: string;
  node_id: string;
  asset_type: string;
  origin_zone: string;
  baseline_access_time_minutes: number | null;
  scenario_access_time_minutes: number | null;
  response_time_delta_minutes: number | null;
  access_lost: boolean;
}

export interface ScenarioPreset {
  id: string;
  name: string;
  description: string;
  icon: string;
  category?: "monsoon" | "construction" | "closure" | "events" | "emergency";
  disruptions: DisruptionInput[];
  recommended_mitigation_id?: string;
}

export interface SimulationResult {
  scenario_id: string;
  baseline_edges: Record<string, EdgeEvaluation>;
  scenario_edges: Record<string, EdgeEvaluation>;
  primary_disrupted_edges: string[];
  newly_overloaded_edges: string[];
  persistently_overloaded_edges: string[];
  changed_routes: ODRouteImpact[];
  all_routes: ODRouteImpact[];
  unserved_od_ids: string[];
  total_travel_time_change_minutes: number;
  total_delay_change_vehicle_hours: number;
  critical_service_impacts: CriticalServiceImpact[];
  explainability: string[];
  iterations_completed: number;
}

export interface ComparisonResult {
  scenario_a_metrics: {
    total_delay_change_veh_h: number;
    newly_overloaded_count: number;
    unserved_od_count: number;
  };
  scenario_b_metrics: {
    total_delay_change_veh_h: number;
    newly_overloaded_count: number;
    unserved_od_count: number;
  };
  net_delay_reduction_veh_hours: number;
  percentage_improvement: number;
  summary_verdict: string;
}
