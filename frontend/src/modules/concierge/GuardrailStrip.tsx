import Link from "next/link";
import { GOALS_LIVE_MOCK, OBJECTIVE_MOCK } from "@/modules/goals";

/**
 * Pinned READ-ONLY guardrail at the top of the chat thread: the aim, the live
 * Calmar, and the drawdown guard — the mandate every Orff answer is measured
 * against. Editing happens only in Goals (this is the read-only live surface),
 * so the only affordance here is "edit in Goals →".
 */
export function GuardrailStrip() {
  const mono = {
    fontFamily: "Space Mono, monospace",
    fontSize: 9,
    letterSpacing: "0.14em",
    textTransform: "uppercase" as const,
  };
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 10,
        flexWrap: "wrap",
        padding: "8px 12px",
        borderRadius: 8,
        border: "1px solid color-mix(in srgb, var(--accent) 22%, var(--line))",
        background: "color-mix(in srgb, var(--accent) 5%, transparent)",
        ...mono,
        color: "var(--fg-3)",
      }}
    >
      <span style={{ color: "var(--accent)" }}>◆ guardrail</span>
      <span style={{ color: "var(--fg-2)", textTransform: "none", letterSpacing: 0, fontSize: 11 }}>
        {OBJECTIVE_MOCK.aim}
      </span>
      <span style={{ opacity: 0.4 }}>·</span>
      <span>
        Calmar <b style={{ color: "var(--fg)" }}>{GOALS_LIVE_MOCK.calmar}×</b>
      </span>
      <span style={{ opacity: 0.4 }}>·</span>
      <span>
        drawdown <b style={{ color: "var(--fg)" }}>{GOALS_LIVE_MOCK.current_dd}%</b>
      </span>
      <Link
        href="/goals"
        style={{ marginLeft: "auto", color: "var(--accent)", textDecoration: "none" }}
      >
        edit in Goals →
      </Link>
    </div>
  );
}
