/** Red-team view-models — hand-mirrored from `app/modules/flow/flow_redteam_schema.py`.
 *  The ONLY LLM-backed stage; everything else in the flow is deterministic. */

import type { RunPhase } from "./flow.run.types";

export type Severity = "high" | "med" | "low";

export interface RedteamObjection {
  severity: Severity;
  title: string;
  detail: string;
}

export interface RedteamReport {
  phase: RunPhase;
  objections: RedteamObjection[];
  tenth_man: string;
  runner_ups: string[];
  tripwires: string[];
  provider: string; // metering attribution — which model spoke (cage records the cost)
  model: string;
  error: string;
}
