"use client";

import { useState } from "react";
import type { Decision } from "./flow.approve.types";

/** The binary decision controls — ack-loss-first (APPROVE gated on the checkbox), VETO needs
 *  a reason. Owns its own input state; hands the decision back to the panel to persist. */
export function ApproveActions({
  shortfall,
  onDecide,
  err,
}: {
  shortfall: string;
  onDecide: (decision: Decision, ack: boolean, reason: string) => void;
  err: string | null;
}) {
  const [ack, setAck] = useState(false);
  const [vetoing, setVetoing] = useState(false);
  const [reason, setReason] = useState("");

  return (
    <>
      <label className="of-ack" data-ack>
        <input type="checkbox" checked={ack} onChange={(e) => setAck(e.target.checked)} />
        <span>I acknowledge the worst-case loss of {shortfall}.</span>
      </label>
      <div className="of-actions">
        <button
          type="button"
          className="of-btn primary"
          data-approve
          disabled={!ack}
          onClick={() => onDecide("approved", ack, reason)}
        >
          Approve as proposed
        </button>
        <button type="button" className="of-btn" data-veto onClick={() => setVetoing((v) => !v)}>
          Veto with reason
        </button>
      </div>
      {vetoing && (
        <div className="of-veto">
          <textarea
            rows={2}
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Why are you vetoing? (no PAN / account numbers — they are blocked)"
          />
          <button
            type="button"
            className="of-btn danger"
            data-veto-confirm
            disabled={!reason.trim()}
            onClick={() => onDecide("vetoed", ack, reason)}
          >
            Confirm veto
          </button>
        </div>
      )}
      {err && <p className="of-author-err">{err}</p>}
    </>
  );
}
