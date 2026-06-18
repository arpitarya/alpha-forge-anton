"use client";

import type { DeepSearchMode as Mode } from "./concierge.types";

/**
 * Tri-state "Deep search" control — replaces the old on/off toggle. Orff initiates a
 * paid Parallel search via the confirm-gated `request_deep_search` tool; this mode
 * (sent as `deep_search_mode`) governs whether it asks first. See handoff §9.
 *
 * - **Auto** (default) — Orff asks via a confirm card on a detected fresh-data gap.
 * - **Always** — the search runs cardless (auto-confirmed) when Orff would call it.
 * - **Never** — the tool isn't offered; free RSS/NSE/yfinance sources only.
 */
const MODES: { id: Mode; label: string; title: string }[] = [
  { id: "auto", label: "Auto", title: "Orff asks before any paid web search (default)" },
  { id: "always", label: "Always", title: "Run the paid web search without asking" },
  { id: "never", label: "Never", title: "Never search the web — free sources only" },
];

export function DeepSearchMode({ value, onChange }: { value: Mode; onChange: (m: Mode) => void }) {
  return (
    <div
      data-af-deep-search
      title="Deep search — paid, budget-capped web grounding (handoff §9)"
      style={{
        display: "flex",
        alignItems: "center",
        gap: 2,
        padding: "2px 6px",
        borderRadius: 999,
        border: "1px solid var(--line-hi)",
        fontFamily: "Space Mono, monospace",
        fontSize: 10,
        letterSpacing: "0.06em",
      }}
    >
      <span aria-hidden style={{ marginRight: 2 }}>
        🌐
      </span>
      {MODES.map((m) => {
        const on = value === m.id;
        return (
          <button
            key={m.id}
            type="button"
            data-mode={m.id}
            aria-pressed={on}
            onClick={() => onChange(m.id)}
            title={m.title}
            style={{
              padding: "2px 7px",
              borderRadius: 999,
              cursor: "pointer",
              border: "none",
              fontFamily: "inherit",
              fontSize: "inherit",
              letterSpacing: "inherit",
              color: on ? "var(--accent)" : "var(--fg-3)",
              background: on ? "color-mix(in srgb, var(--accent) 14%, transparent)" : "transparent",
              transition: "color 120ms, background 120ms",
            }}
          >
            {m.label}
          </button>
        );
      })}
    </div>
  );
}
