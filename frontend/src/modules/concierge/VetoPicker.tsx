"use client";

import { useState } from "react";

const REASONS = [
  "Too crowded — already live in 3 books",
  "Wait for post-RBI re-grounding",
  "Size too large for this conviction",
];

/** Veto is binary too: pick a reason (required & logged), no inline edits — the
 * vetted plan stays vetted and untouched. */
export function VetoPicker({
  onLog,
  onBack,
}: {
  onLog: (reason: string) => void;
  onBack: () => void;
}) {
  const [reason, setReason] = useState("");
  return (
    <div>
      <div className="of-sub">Why are you vetoing? (binary — no inline edits)</div>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {REASONS.map((r) => (
          <button
            type="button"
            key={r}
            onClick={() => setReason(r)}
            style={{
              textAlign: "left",
              fontFamily: "Space Mono, monospace",
              fontSize: 11,
              letterSpacing: ".02em",
              color: reason === r ? "var(--red)" : "var(--fg-2)",
              border: `1px solid ${reason === r ? "color-mix(in srgb, var(--red) 45%, transparent)" : "var(--line-hi)"}`,
              background:
                reason === r ? "color-mix(in srgb, var(--red) 8%, transparent)" : "transparent",
              borderRadius: 8,
              padding: "10px 12px",
              cursor: "pointer",
            }}
          >
            {reason === r ? "◉ " : "○ "}
            {r}
          </button>
        ))}
      </div>
      <div className="of-ap-foot">
        <div className="btnrow">
          <button
            type="button"
            className="of-btn danger full"
            disabled={!reason}
            style={{ opacity: reason ? 1 : 0.5 }}
            onClick={() => reason && onLog(reason)}
          >
            Log veto &amp; close
          </button>
          <button type="button" className="of-btn ghost full" onClick={onBack}>
            Back
          </button>
        </div>
      </div>
    </div>
  );
}
