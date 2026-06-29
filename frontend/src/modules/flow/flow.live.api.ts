import api from "@/lib/api";
import type { Fill, OrderPlan, ReconcileResult } from "./flow.live.types";

/** GET /flow/edges/{id}/live — the exact orders + checklist for an approved edge (copy-only). */
export async function fetchOrderPlan(edgeId: string): Promise<OrderPlan> {
  const res = await api.get<OrderPlan>(`/flow/edges/${encodeURIComponent(edgeId)}/live`);
  return res.data;
}

/** POST /flow/edges/{id}/reconcile — true-P&L read-back from the human's actual fills. */
export async function reconcileFills(edgeId: string, fills: Fill[]): Promise<ReconcileResult> {
  const res = await api.post<ReconcileResult>(
    `/flow/edges/${encodeURIComponent(edgeId)}/reconcile`,
    fills,
  );
  return res.data;
}
