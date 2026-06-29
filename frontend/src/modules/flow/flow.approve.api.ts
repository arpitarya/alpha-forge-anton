import api from "@/lib/api";
import type { ApproveState, DecisionRecord, DecisionRequest } from "./flow.approve.types";

/** GET /flow/edges/{id}/approve — the downside-first proposal + checklist + live decision. */
export async function fetchApprove(edgeId: string): Promise<ApproveState> {
  const res = await api.get<ApproveState>(`/flow/edges/${encodeURIComponent(edgeId)}/approve`);
  return res.data;
}

/** POST /flow/edges/{id}/decision — record the binary decision (journaled to elgar). */
export async function postDecision(edgeId: string, req: DecisionRequest): Promise<DecisionRecord> {
  const res = await api.post<DecisionRecord>(
    `/flow/edges/${encodeURIComponent(edgeId)}/decision`,
    req,
  );
  return res.data;
}
