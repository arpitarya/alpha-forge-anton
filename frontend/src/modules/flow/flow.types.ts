/** Process-flow cockpit view-models — hand-mirrored from `app/modules/flow/flow_schema.py`.
 *  (A view over edge state, not a frozen engine contract; lives outside contracts codegen,
 *  same as goals.api's RecentRun/EdgeSummary.) */

export type StageId =
  | "idea"
  | "rule"
  | "test"
  | "range"
  | "plan"
  | "redteam"
  | "approve"
  | "live"
  | "watch";

export type StageState = "done" | "active" | "pending" | "na" | "blocked";

export interface StageStatus {
  id: StageId;
  label: string;
  state: StageState;
  summary: string;
}

export interface FlowState {
  edge_id: string;
  hypothesis: string;
  frozen: boolean;
  spec_ref: string | null;
  stages: StageStatus[];
}

export interface EdgeListItem {
  edge_id: string;
  hypothesis: string;
  frozen: boolean;
  stage: StageId;
}

/** The factor knobs the engine consumes (mirror of FactorConfig). */
export interface FactorConfig {
  lookback_months: number;
  skip_month: boolean;
  slice: "decile" | "quartile";
  theta_roce: number;
  theta_de: number;
  trend_on: boolean;
  stop_on: boolean;
}

/** The Rule-stage authoring form payload — only the fields the engine consumes today. */
export interface AuthorEdgeRequest {
  edge_id?: string | null;
  hypothesis: string;
  universe: string[];
  signal: string;
  holding_period_days: number;
  expected_edge_pct: number;
  factor?: FactorConfig | null;
}

export interface EdgeTemplate {
  id: string;
  family: string;
  name: string;
  description: string;
  available: boolean;
  prefill: AuthorEdgeRequest;
}
