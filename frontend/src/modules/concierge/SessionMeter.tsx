"use client";

import type { SessionTotals } from "./useChatStream";

const usd = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 4,
});

/**
 * A compact token / cost indicator for the live session — the Claude-Code
 * context meter. Cost is real spend (0 on free providers, priced from the
 * registry's consumption block server-side).
 */
export function SessionMeter({ totals }: { totals: SessionTotals }) {
  if (!totals.turns) return null;
  const paid = totals.costUsd > 0;
  return (
    <span
      title={`${totals.tokens.toLocaleString()} tokens · ${usd.format(totals.costUsd)} this session`}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 7,
        fontFamily: "Space Mono, monospace",
        fontSize: 9,
        letterSpacing: "0.12em",
        textTransform: "uppercase",
        color: "var(--fg-3)",
        whiteSpace: "nowrap",
      }}
    >
      <span>{fmtTokens(totals.tokens)} tok</span>
      <span style={{ opacity: 0.3 }}>·</span>
      <span style={{ color: paid ? "var(--accent)" : "var(--green)" }}>
        {paid ? usd.format(totals.costUsd) : "free"}
      </span>
    </span>
  );
}

function fmtTokens(n: number): string {
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
  return String(n);
}
