"use client";

import { useEffect, useState } from "react";
import { useConciergeMemory, useSaveMemory } from "./concierge.memory";

const PLACEHOLDER =
  "Goals, constraints, preferences Orff should always know — e.g.\n" +
  "• Age 35, moderate risk, 6-month emergency buffer secured\n" +
  "• Prefer index funds over single stocks\n" +
  "• Target ₹2Cr by 2035, avoid F&O";

/**
 * Editable long-term memory — the chat-app "project instructions", scoped to
 * financial preferences and injected into every reply (see memory_service.py).
 */
export function MemoryPanel({ onClose }: { onClose: () => void }) {
  const { data } = useConciergeMemory();
  const save = useSaveMemory();
  const [text, setText] = useState("");
  const [dirty, setDirty] = useState(false);

  useEffect(() => {
    if (data && !dirty) setText(data.content);
  }, [data, dirty]);

  return (
    <PanelFrame title="Memory" subtitle="Orff remembers this every chat" onClose={onClose}>
      <textarea
        value={text}
        onChange={(e) => {
          setText(e.target.value);
          setDirty(true);
        }}
        placeholder={PLACEHOLDER}
        spellCheck={false}
        style={{
          flex: 1,
          width: "100%",
          resize: "none",
          background: "color-mix(in srgb, var(--surface-lo) 50%, transparent)",
          border: "1px solid var(--line)",
          borderRadius: 8,
          padding: "12px 14px",
          color: "var(--fg)",
          fontFamily: "Space Grotesk, sans-serif",
          fontSize: 13,
          lineHeight: 1.6,
          outline: "none",
        }}
      />
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 12 }}>
        <button
          type="button"
          disabled={!dirty || save.isPending}
          onClick={() => save.mutate(text, { onSuccess: () => setDirty(false) })}
          style={{
            padding: "8px 16px",
            borderRadius: 7,
            border: "none",
            cursor: dirty ? "pointer" : "default",
            fontFamily: "Space Mono, monospace",
            fontSize: 10,
            letterSpacing: "0.14em",
            textTransform: "uppercase",
            color: "var(--on-accent)",
            background: dirty ? "var(--accent)" : "var(--line-hi)",
            opacity: save.isPending ? 0.6 : 1,
          }}
        >
          {save.isPending ? "Saving…" : dirty ? "Save" : "Saved"}
        </button>
        <span
          style={{
            fontFamily: "Space Mono, monospace",
            fontSize: 9,
            letterSpacing: "0.1em",
            color: "var(--fg-4)",
          }}
        >
          {text.length} / 4000
        </span>
      </div>
    </PanelFrame>
  );
}

export function PanelFrame({
  title,
  subtitle,
  onClose,
  children,
}: {
  title: string;
  subtitle: string;
  onClose: () => void;
  children: React.ReactNode;
}) {
  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", padding: "16px 18px" }}>
      <div style={{ display: "flex", alignItems: "flex-start", marginBottom: 14 }}>
        <div style={{ minWidth: 0 }}>
          <div style={{ fontSize: 15, fontWeight: 500, color: "var(--fg)" }}>{title}</div>
          <div
            style={{
              marginTop: 3,
              fontFamily: "Space Mono, monospace",
              fontSize: 9,
              letterSpacing: "0.16em",
              textTransform: "uppercase",
              color: "var(--fg-3)",
            }}
          >
            {subtitle}
          </div>
        </div>
        <button
          type="button"
          onClick={onClose}
          title="Close panel"
          style={{
            marginLeft: "auto",
            width: 26,
            height: 26,
            borderRadius: 6,
            border: "1px solid var(--line)",
            background: "transparent",
            color: "var(--fg-3)",
            cursor: "pointer",
          }}
        >
          ✕
        </button>
      </div>
      {children}
    </div>
  );
}
