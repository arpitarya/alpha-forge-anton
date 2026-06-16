"use client";

import { useState } from "react";
import { useObjective } from "./concierge.objective";
import { PanelFrame } from "./MemoryPanel";

const inr = (n: number) => `₹${Math.round(n).toLocaleString("en-IN")}`;
const MONO = {
  fontFamily: "Space Mono, monospace",
  fontSize: 9,
  letterSpacing: "0.16em",
  textTransform: "uppercase" as const,
  color: "var(--fg-3)",
};
const GROTESK = { fontFamily: "Space Grotesk, sans-serif" };

/**
 * North-star tab beside Memory. Read-only view of the objective (target, horizon,
 * mission) + a *pending* progress track: there is no trades source yet, so MTD is a
 * distinct pending state — never a misleading 0%-width bar that reads "you're failing".
 * Edits are proposed into chat → `set_objective` → ApprovalCard → elgar; never a
 * silent write (the panel has no PUT, unlike MemoryPanel).
 */
export function ObjectivePanel({
  onEdit,
  onClose,
}: {
  onEdit: (prompt: string) => void;
  onClose: () => void;
}) {
  const { data } = useObjective();
  const [target, setTarget] = useState("");
  const active = data?.active_target ?? 0;
  const chips = data ? [data.horizon, data.risk_tolerance] : [];

  return (
    <PanelFrame
      title="Objective"
      subtitle="Orff's north-star — code measures against this"
      onClose={onClose}
    >
      <div style={{ display: "flex", flexDirection: "column", gap: 18, overflowY: "auto" }}>
        <p
          style={{
            margin: 0,
            fontSize: 13.5,
            lineHeight: 1.6,
            ...GROTESK,
            color: data?.mission ? "var(--fg-2)" : "var(--fg-4)",
            fontStyle: data?.mission ? "normal" : "italic",
          }}
        >
          {data?.mission || "No mission set yet."}
        </p>

        <div>
          <div style={MONO}>Monthly target</div>
          <div style={{ marginTop: 4, fontSize: 28, fontWeight: 600, color: "var(--fg)" }}>
            {active ? `${inr(active)}/mo` : "Not set"}
          </div>
          {data?.step_up && (
            <div style={{ marginTop: 4, ...MONO, color: "var(--accent)" }}>
              → {inr(data.step_up.monthly_target_inr)} from {data.step_up.from_date}
            </div>
          )}
        </div>

        <div style={{ display: "flex", gap: 8 }}>
          {chips.map((c) => (
            <span
              key={c}
              style={{
                padding: "4px 10px",
                borderRadius: 999,
                border: "1px solid var(--line)",
                ...MONO,
                color: "var(--fg-2)",
              }}
            >
              {c}
            </span>
          ))}
        </div>

        {/* Progress — a distinct PENDING state (dashed/striped track), not a 0% fill. */}
        <div>
          <div style={{ display: "flex", justifyContent: "space-between", ...MONO }}>
            <span>This month</span>
            <span style={{ color: "var(--fg-4)" }}>
              pending · target {active ? inr(active) : "—"}
            </span>
          </div>
          <div
            data-progress="pending"
            title="MTD tracking starts when a trades source is connected"
            style={{
              marginTop: 8,
              height: 8,
              borderRadius: 999,
              border: "1px dashed var(--line-hi)",
              background:
                "repeating-linear-gradient(45deg, transparent 0 5px, color-mix(in srgb, var(--fg-4) 22%, transparent) 5px 10px)",
            }}
          />
          <div style={{ marginTop: 6, fontSize: 11, ...GROTESK, color: "var(--fg-4)" }}>
            No trades source connected yet — progress appears once trades land.
          </div>
        </div>

        <div style={{ display: "flex", gap: 8 }}>
          <input
            value={target}
            inputMode="numeric"
            placeholder="New monthly target ₹"
            onChange={(e) => setTarget(e.target.value.replace(/\D/g, ""))}
            style={{
              flex: 1,
              padding: "9px 12px",
              borderRadius: 7,
              fontSize: 13,
              ...GROTESK,
              background: "color-mix(in srgb, var(--surface-lo) 50%, transparent)",
              border: "1px solid var(--line)",
              color: "var(--fg)",
              outline: "none",
            }}
          />
          <button
            type="button"
            disabled={!target}
            onClick={() => onEdit(`Set my monthly realized-profit target to ₹${target}.`)}
            style={{
              padding: "9px 14px",
              borderRadius: 7,
              border: "none",
              whiteSpace: "nowrap",
              cursor: target ? "pointer" : "default",
              ...MONO,
              fontSize: 10,
              letterSpacing: "0.12em",
              color: "var(--on-accent)",
              background: target ? "var(--accent)" : "var(--line-hi)",
            }}
          >
            Propose change
          </button>
        </div>
        <div style={{ ...MONO, color: "var(--fg-4)", letterSpacing: "0.1em" }}>
          Edits go through a confirm card — never a silent write.
        </div>
      </div>
    </PanelFrame>
  );
}
