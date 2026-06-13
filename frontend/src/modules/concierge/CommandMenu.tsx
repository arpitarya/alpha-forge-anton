"use client";

import { useEffect } from "react";
import type { SlashCommand } from "./concierge.commands";

/**
 * Inline slash-command autocomplete — shown above the composer when the input
 * begins with "/". Arrow keys move the selection; Enter/Tab picks (handled by
 * the composer via `active`), Escape dismisses.
 */
export function CommandMenu({
  commands,
  active,
  onPick,
}: {
  commands: SlashCommand[];
  active: number;
  onPick: (c: SlashCommand) => void;
}) {
  useEffect(() => {
    document.getElementById(`cmd-${active}`)?.scrollIntoView({ block: "nearest" });
  }, [active]);

  if (!commands.length) return null;
  return (
    <div
      style={{
        position: "absolute",
        bottom: "calc(100% + 8px)",
        left: 0,
        right: 0,
        maxHeight: 240,
        overflowY: "auto",
        borderRadius: 10,
        border: "1px solid var(--line-hi)",
        background: "color-mix(in srgb, var(--surface) 96%, transparent)",
        backdropFilter: "blur(18px)",
        boxShadow: "0 18px 50px -20px rgba(0,0,0,.7)",
        zIndex: 60,
        padding: 6,
      }}
    >
      {commands.map((c, i) => (
        <button
          key={c.name}
          id={`cmd-${i}`}
          type="button"
          onMouseDown={(e) => {
            e.preventDefault();
            onPick(c);
          }}
          style={{
            width: "100%",
            display: "flex",
            alignItems: "baseline",
            gap: 10,
            padding: "8px 12px",
            borderRadius: 7,
            border: "none",
            textAlign: "left",
            cursor: "pointer",
            background:
              i === active ? "color-mix(in srgb, var(--accent) 14%, transparent)" : "transparent",
          }}
        >
          <code
            style={{
              fontFamily: "Space Mono, monospace",
              fontSize: 12,
              color: "var(--accent)",
              flexShrink: 0,
            }}
          >
            /{c.name}
          </code>
          <span
            style={{
              fontFamily: "Space Grotesk, sans-serif",
              fontSize: 12,
              color: "var(--fg-3)",
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {c.hint}
          </span>
        </button>
      ))}
    </div>
  );
}
