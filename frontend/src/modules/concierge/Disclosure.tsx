"use client";

import { useState } from "react";

interface Props {
  label: string;
  count?: number;
  defaultOpen?: boolean;
  tone?: "accent" | "muted";
  children: React.ReactNode;
}

/**
 * A collapsible "process" block — the Claude-Code pattern of folding tool calls
 * and reasoning behind a one-line summary the user can expand on demand.
 */
export function Disclosure({ label, count, defaultOpen = false, tone = "muted", children }: Props) {
  const [open, setOpen] = useState(defaultOpen);
  const accent = tone === "accent" ? "var(--accent)" : "var(--fg-3)";
  return (
    <div
      style={{
        marginBottom: 10,
        border: "1px solid var(--line)",
        borderRadius: 8,
        background: "color-mix(in srgb, var(--surface-lo) 40%, transparent)",
        overflow: "hidden",
      }}
    >
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        style={{
          width: "100%",
          display: "flex",
          alignItems: "center",
          gap: 8,
          padding: "7px 11px",
          background: "transparent",
          border: "none",
          cursor: "pointer",
          fontFamily: "Space Mono, monospace",
          fontSize: 9,
          letterSpacing: "0.18em",
          textTransform: "uppercase",
          color: accent,
        }}
      >
        <span
          style={{
            display: "inline-block",
            transition: "transform .18s",
            transform: open ? "rotate(90deg)" : "rotate(0deg)",
          }}
        >
          ▸
        </span>
        <span>{label}</span>
        {count != null && (
          <span
            style={{
              marginLeft: "auto",
              color: "var(--fg-4)",
              letterSpacing: "0.1em",
            }}
          >
            {count}
          </span>
        )}
      </button>
      {open && (
        <div
          style={{
            padding: "4px 11px 10px",
            borderTop: "1px solid color-mix(in srgb, var(--line) 60%, transparent)",
          }}
        >
          {children}
        </div>
      )}
    </div>
  );
}
