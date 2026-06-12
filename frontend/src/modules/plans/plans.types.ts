export interface PlanDTO {
  plan_id: string;
  horizon: string;
  targets: Record<string, number>;
  bands: Record<string, number>;
  rules: string[];
  available: string[];
}

export interface ClassDriftDTO {
  asset_class: string;
  target_pct: number;
  actual_pct: number;
  drift_pct: number;
  band: number;
  status: "ok" | "hot" | "cold";
  action: string;
}

export interface PlanDriftDTO {
  plan_id: string;
  live: boolean;
  drift: ClassDriftDTO[];
  actions: string[];
}

export interface ProjectionDTO {
  rate_pa: number;
  inflation_pa: number;
  asset_class: string;
  years: number[];
  nominal: number[];
  real: number[];
  assumptions_ref: string;
}

export interface PlanSaveResponseDTO {
  ref: string;
  plan_id: string;
}
