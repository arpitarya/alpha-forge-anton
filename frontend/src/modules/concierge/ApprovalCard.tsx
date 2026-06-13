"use client";

import { useState } from "react";
import type { PendingAction } from "./concierge.types";

/**
 * Structured approval for a detected mutating intent — replaces a prose "shall I
 * proceed?". Approving sends an explicit confirmation turn; Anton never executes
 * a trade itself, so the steps are honest about where the user takes over.
 */
export function ApprovalCard({
  action,
  onApprove,
  onDismiss,
}: {
  action: PendingAction;
  onApprove: (a: PendingAction) => void;
  onDismiss: () => void;
}) {
  const [resolved, setResolved] = useState<"approved" | "dismissed" | null>(null);
  return (
    <div
      style={{
        marginTop: 12,
        padding: "14px 16px",
        borderRadius: 10,
        border: "1px solid color-mix(in srgb, var(--accent) 35%, var(--line))",
        background: "color-mix(in srgb, var(--accent) 6%, var(--surface))",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          marginBottom: 10,
          fontFamily: "Space Mono, monospace",
          fontSize: 9,
          letterSpacing: "0.2em",
          textTransform: "uppercase",
          color: "var(--accent)",
        }}
      >
        <span>⚐ Action · confirm to proceed</span>
      </div>
      <div style={{ fontSize: 14, fontWeight: 600, color: "var(--fg)", marginBottom: 8 }}>
        {action.action}
      </div>
      <ol
        style={{
          margin: "0 0 12px",
          paddingLeft: 18,
          display: "flex",
          flexDirection: "column",
          gap: 5,
          fontFamily: "Space Grotesk, sans-serif",
          fontSize: 12.5,
          lineHeight: 1.5,
          color: "var(--fg-2)",
        }}
      >
        {action.steps.map((s) => (
          <li key={s}>{s}</li>
        ))}
      </ol>
      {resolved ? (
        <div
          style={{
            fontFamily: "Space Mono, monospace",
            fontSize: 10,
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            color: resolved === "approved" ? "var(--green)" : "var(--fg-3)",
          }}
        >
          {resolved === "approved" ? "✓ approved — drafting" : "dismissed"}
        </div>
      ) : (
        <div style={{ display: "flex", gap: 8 }}>
          <Btn
            primary
            label="Approve & continue"
            onClick={() => {
              setResolved("approved");
              onApprove(action);
            }}
          />
          <Btn
            label="Not now"
            onClick={() => {
              setResolved("dismissed");
              onDismiss();
            }}
          />
        </div>
      )}
    </div>
  );
}

function Btn({
  label,
  onClick,
  primary,
}: {
  label: string;
  onClick: () => void;
  primary?: boolean;
}) {
  const [hov, setHov] = useState(false);
  return (
    <button
      type="button"
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        padding: "7px 14px",
        borderRadius: 7,
        cursor: "pointer",
        fontFamily: "Space Mono, monospace",
        fontSize: 10,
        letterSpacing: "0.12em",
        textTransform: "uppercase",
        border: primary ? "none" : "1px solid var(--line-hi)",
        color: primary ? "var(--on-accent)" : "var(--fg-2)",
        background: primary ? "var(--accent)" : "transparent",
        boxShadow: primary && hov ? "0 0 18px var(--glow)" : "none",
        transition: "all .16s",
      }}
    >
      {label}
    </button>
  );
}
