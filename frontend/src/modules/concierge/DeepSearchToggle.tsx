"use client";

/**
 * Off-by-default "Deep search" chip — opts a single message into Parallel web
 * grounding (paid). When on, the backend calls Parallel, injects the extracts,
 * records a Cage receipt, and enforces a hard monthly budget cap (handoff §9,
 * grounding_service.py). The everyday free RSS/NSE/yfinance path runs when off.
 */
export function DeepSearchToggle({ on, onToggle }: { on: boolean; onToggle: () => void }) {
  return (
    <button
      type="button"
      data-af-deep-search
      aria-pressed={on}
      onClick={onToggle}
      title="Deep search — ground this message with live web results (paid, budget-capped)"
      style={{
        display: "flex",
        alignItems: "center",
        gap: 5,
        padding: "3px 8px",
        borderRadius: 999,
        cursor: "pointer",
        fontFamily: "Space Mono, monospace",
        fontSize: 10,
        letterSpacing: "0.06em",
        border: `1px solid ${on ? "var(--accent)" : "var(--line-hi)"}`,
        color: on ? "var(--accent)" : "var(--fg-3)",
        background: on ? "color-mix(in srgb, var(--accent) 12%, transparent)" : "transparent",
        transition: "color 120ms, border-color 120ms, background 120ms",
      }}
    >
      <span aria-hidden>🌐</span>
      <span>Deep search</span>
    </button>
  );
}
