"use client";

import { useState } from "react";

/** The decay-kill control — a PII-guarded reason gates retiring the edge. Owns its reason
 *  state; hands it back to the panel, which journals the retirement to elgar. */
export function DecayKillBlock({ onKill }: { onKill: (reason: string) => void }) {
  const [reason, setReason] = useState("");
  return (
    <div className="of-veto" data-kill-block>
      <input
        value={reason}
        placeholder="decay-kill reason (PII-guarded)"
        onChange={(e) => setReason(e.target.value)}
      />
      <button
        type="button"
        className="of-btn danger"
        data-decay-kill
        disabled={!reason.trim()}
        onClick={() => onKill(reason)}
      >
        Decay-kill — retire this edge
      </button>
    </div>
  );
}
