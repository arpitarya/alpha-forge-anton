/** Approve-stage view-models — hand-mirrored from `app/modules/flow/flow_decision_schema.py`.
 *  Reuses the generated `ApprovalProposal` contract for the proposal itself. */

import type { ApprovalProposal } from "@/modules/contracts";

export type Decision = "approved" | "vetoed";

export interface DecisionRequest {
  decision: Decision;
  ack_loss: boolean; // APPROVE requires acknowledging the worst-case loss first
  veto_reason: string; // VETO requires a reason (PII-guarded server-side)
}

export interface DecisionRecord {
  edge_id: string;
  decision: Decision;
  thesis: string;
  downside_shown: number;
  veto_reason: string;
  decided_at: string;
  cooldown_until: string;
  ref: string | null;
}

export interface ApproveState {
  proposal: ApprovalProposal;
  checklist: string[];
  redteam_ready: boolean;
  decision: DecisionRecord | null;
  can_decide: boolean;
}
