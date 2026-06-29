"use client";

import { useCallback, useEffect, useState } from "react";
import { ApproveActions } from "./ApproveActions";
import { fetchApprove, postDecision } from "./flow.approve.api";
import type { ApproveState, Decision } from "./flow.approve.types";

const inr = (n: number) => `₹${Math.round(n).toLocaleString("en-IN")}`;

/** Approve stage — binary, downside-first, ack-loss-first. APPROVE is disabled until the
 *  worst-case loss is acknowledged; VETO needs a reason. The decision journals to elgar and
 *  is cooldown-spaced. The exec checklist shows ON approve — Orff NEVER places the order. */
export function ApprovePanel({ edgeId }: { edgeId: string }) {
  const [st, setSt] = useState<ApproveState | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const load = useCallback(async () => {
    setSt(await fetchApprove(edgeId).catch(() => null));
  }, [edgeId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function decide(decision: Decision, ack: boolean, reason: string) {
    setErr(null);
    try {
      await postDecision(edgeId, { decision, ack_loss: ack, veto_reason: reason });
      await load();
    } catch (e) {
      setErr((e as { apiError?: { message?: string } }).apiError?.message ?? "Decision failed.");
    }
  }

  if (!st) return <p className="of-pending-lbl">Loading the proposal…</p>;
  const p = st.proposal;
  const decided = st.decision;

  return (
    <div className="of-approve" data-approve-panel>
      <div className="of-approve-hero">
        <span className="of-lbl">Worst case you must accept first</span>
        <span className="of-approve-es" data-downside>
          −{inr(p.expected_shortfall)}
        </span>
        <span className="of-pending-lbl">
          {inr(p.notional)} notional · {p.thesis || "—"}
        </span>
      </div>
      {!st.redteam_ready && (
        <p className="of-pending-lbl">
          Run the red-team first — you say yes after seeing the 10th-Man.
        </p>
      )}

      {decided ? (
        <div className="of-decided" data-decided={decided.decision}>
          <strong>{decided.decision.toUpperCase()}</strong> · downside shown{" "}
          {inr(decided.downside_shown)}
          {decided.veto_reason && <p>reason: {decided.veto_reason}</p>}
          <p className="of-pending-lbl">
            journaled to elgar · cooldown until {decided.cooldown_until.slice(0, 16)}
          </p>
          {decided.decision === "approved" && (
            <ol className="of-checklist" data-checklist>
              {st.checklist.map((s) => (
                <li key={s}>{s}</li>
              ))}
            </ol>
          )}
        </div>
      ) : !st.can_decide ? (
        <p className="of-author-err">A logged cooldown is still active — no re-decision yet.</p>
      ) : (
        <ApproveActions shortfall={inr(p.expected_shortfall)} onDecide={decide} err={err} />
      )}
    </div>
  );
}
