"use client";

import type { ToolStep } from "./concierge.types";
import { Disclosure } from "./Disclosure";

/**
 * The data-read trail for a turn (Fux recall, memory load, holdings disclosure,
 * vision routing) — Claude-Code-style collapsible tool blocks, not hidden prose.
 */
export function ToolTrail({ steps }: { steps: ToolStep[] }) {
  if (!steps.length) return null;
  return (
    <Disclosure label="Context read" count={steps.length}>
      <div style={{ display: "flex", flexDirection: "column", gap: 6, paddingTop: 6 }}>
        {steps.map((s) => (
          <div
            key={`${s.name}:${s.detail}`}
            style={{ display: "flex", alignItems: "baseline", gap: 8, minWidth: 0 }}
          >
            <code
              style={{
                fontFamily: "Space Mono, monospace",
                fontSize: 10.5,
                color: "var(--accent)",
                flexShrink: 0,
              }}
            >
              {s.name}
            </code>
            <span
              style={{
                fontFamily: "Space Grotesk, sans-serif",
                fontSize: 11.5,
                color: "var(--fg-2)",
                flex: 1,
                minWidth: 0,
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
            >
              {s.detail}
            </span>
            <span
              style={{
                fontFamily: "Space Mono, monospace",
                fontSize: 9,
                color: "var(--fg-4)",
                flexShrink: 0,
              }}
            >
              {s.ms}ms
            </span>
          </div>
        ))}
      </div>
    </Disclosure>
  );
}
