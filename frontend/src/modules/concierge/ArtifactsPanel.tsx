"use client";

import { useState } from "react";
import type { ChatTurn } from "./concierge.types";
import { PanelFrame } from "./MemoryPanel";
import { SpecHost } from "./SpecHost";

/**
 * A persistent side panel collecting every UI Orff composed this session — the
 * chat-app "Artifacts" surface. Generated specs live here as well as inline, so
 * a net-worth card or rebalance chart stays glanceable across turns.
 */
export function ArtifactsPanel({ turns, onClose }: { turns: ChatTurn[]; onClose: () => void }) {
  const artifacts = turns.filter((t) => t.spec);
  const [active, setActive] = useState(0);
  const current = artifacts[Math.min(active, artifacts.length - 1)];

  return (
    <PanelFrame title="Artifacts" subtitle={`${artifacts.length} composed`} onClose={onClose}>
      {artifacts.length === 0 ? (
        <div
          style={{
            flex: 1,
            display: "grid",
            placeItems: "center",
            color: "var(--fg-3)",
            fontFamily: "Space Grotesk, sans-serif",
            fontSize: 13,
            textAlign: "center",
            padding: 20,
          }}
        >
          Composed charts and cards appear here. Ask Orff to “show” or “chart” something to generate
          one.
        </div>
      ) : (
        <>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 12 }}>
            {artifacts.map((t, i) => (
              <button
                key={t.id}
                type="button"
                onClick={() => setActive(i)}
                style={{
                  maxWidth: 160,
                  padding: "5px 10px",
                  borderRadius: 6,
                  cursor: "pointer",
                  fontFamily: "Space Grotesk, sans-serif",
                  fontSize: 11,
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  color: i === active ? "var(--on-accent)" : "var(--fg-2)",
                  background:
                    i === active
                      ? "var(--accent)"
                      : "color-mix(in srgb, var(--surface-lo) 50%, transparent)",
                  border: `1px solid ${i === active ? "transparent" : "var(--line)"}`,
                }}
              >
                {t.query}
              </button>
            ))}
          </div>
          <div style={{ flex: 1, overflowY: "auto" }}>
            {current?.spec && <SpecHost spec={current.spec} />}
          </div>
        </>
      )}
    </PanelFrame>
  );
}
