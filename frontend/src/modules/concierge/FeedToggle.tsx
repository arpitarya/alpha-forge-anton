"use client";

import type { Feed } from "./GroundedAnswer";

const OPTS: Array<{ v: Feed; label: string; warn?: boolean; bad?: boolean }> = [
  { v: "live", label: "live feed" },
  { v: "stale", label: "stale feed", warn: true },
  { v: "error", label: "feed error", bad: true },
];

/**
 * LIVE / STALE / ERROR feed switch (mirrors the Phase-0 FeedState). STALE blocks
 * the proposal's Approve and freezes the cone to honest-pending ₹0; ERROR
 * withholds the forecast entirely. React state only — no persistence.
 */
export function FeedToggle({ value, onChange }: { value: Feed; onChange: (f: Feed) => void }) {
  return (
    <div
      style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 12, flexWrap: "wrap" }}
    >
      <span
        style={{
          fontFamily: "Space Mono, monospace",
          fontSize: 9,
          letterSpacing: ".16em",
          textTransform: "uppercase",
          color: "var(--fg-3)",
          marginRight: 2,
        }}
      >
        feed
      </span>
      {OPTS.map((o) => {
        const on = value === o.v;
        const color = o.bad ? "var(--red)" : o.warn ? "var(--accent-soft)" : "var(--accent)";
        return (
          <button
            type="button"
            key={o.v}
            data-feed={o.v}
            aria-pressed={on}
            onClick={() => onChange(o.v)}
            style={{
              fontFamily: "Space Mono, monospace",
              fontSize: 9,
              letterSpacing: ".12em",
              textTransform: "uppercase",
              padding: "4px 9px",
              borderRadius: 5,
              cursor: "pointer",
              color: on ? color : "var(--fg-3)",
              background: on ? `color-mix(in srgb, ${color} 8%, transparent)` : "transparent",
              border: `1px solid ${on ? `color-mix(in srgb, ${color} 45%, transparent)` : "var(--line-hi)"}`,
            }}
          >
            {o.label}
          </button>
        );
      })}
    </div>
  );
}
