/** Test-stage run view-models — hand-mirrored from `app/modules/flow/flow_run_schema.py`.
 *  The cone is the generated `Cone` contract; the report is the generated `TestReport`. */

import type { Cone, TestReport } from "@/modules/contracts";

export type RunPhase = "queued" | "running" | "done" | "failed";
export type GateState = "pending" | "passed" | "failed" | "skipped";

export interface GateProgress {
  gate: number; // 0 integrity · 1 backtest+overfitting · 2 walk-forward · 3 cone
  label: string;
  state: GateState;
}

export interface RunStatus {
  job_id: string;
  edge_id: string;
  phase: RunPhase;
  gates: GateProgress[];
  report: TestReport | null;
  cone: Cone | null;
  signature: string;
  error: string;
}
