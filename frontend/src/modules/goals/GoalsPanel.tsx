"use client";

import { useState } from "react";
import { GoalsScore } from "./GoalsScore";
import { GoalsStructure } from "./GoalsStructure";
import { GOALS_LIVE_MOCK, GOALS_LIVE_PENDING, OBJECTIVE_MOCK } from "./goals.mock";

/**
 * The editable north-star (Goals surface). Leads with Calmar (return per unit of
 * pain) + the drawdown guard; edges, funding and structure stay visibly pending
 * rather than faking progress. This is the ONLY place the objective is editable —
 * the live surface shows it read-only ([[GuardrailStrip]]). "Propose change →"
 * routes a prompt into chat → confirm card → elgar; never a silent write.
 */
export function GoalsPanel({ onPropose }: { onPropose: (prompt: string) => void }) {
  const [variant, setVariant] = useState<"default" | "pending">("default");
  const pending = variant === "pending";
  const live = pending ? GOALS_LIVE_PENDING : GOALS_LIVE_MOCK;

  return (
    <div data-goals-variant={variant}>
      <div style={{ display: "flex", justifyContent: "flex-end", gap: 6, marginBottom: 14 }}>
        <Tog on={variant === "default"} onClick={() => setVariant("default")}>
          default
        </Tog>
        <Tog on={pending} warn onClick={() => setVariant("pending")}>
          first-run · pending
        </Tog>
      </div>

      <GoalsScore obj={OBJECTIVE_MOCK} live={live} />
      <GoalsStructure obj={OBJECTIVE_MOCK} live={live} pending={pending} />

      <div className="of-actions">
        <button
          type="button"
          className="of-btn primary"
          onClick={() =>
            onPropose(
              "I'd like to change my objective (Calmar target / drawdown guard / capital structure). Walk me through the trade-offs and propose the edit.",
            )
          }
        >
          Propose change →
        </button>
        <button
          type="button"
          className="of-why"
          onClick={() => onPropose("Why is my objective showing pending?")}
        >
          Why pending?
        </button>
      </div>
    </div>
  );
}

function Tog({
  on,
  warn,
  onClick,
  children,
}: {
  on: boolean;
  warn?: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  const color = on ? (warn ? "var(--accent-soft)" : "var(--accent)") : "var(--fg-3)";
  return (
    <button
      type="button"
      onClick={onClick}
      style={{
        fontFamily: "Space Mono, monospace",
        fontSize: 9,
        letterSpacing: ".12em",
        textTransform: "uppercase",
        padding: "4px 9px",
        borderRadius: 5,
        cursor: "pointer",
        color,
        background: on ? `color-mix(in srgb, ${color} 8%, transparent)` : "transparent",
        border: `1px solid ${on ? `color-mix(in srgb, ${color} 45%, transparent)` : "var(--line-hi)"}`,
      }}
    >
      {children}
    </button>
  );
}
