"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { COMMANDS, matchCommands, type SlashCommand } from "./concierge.commands";

/**
 * Cmd+K command palette — the keyboard-first entry to every slash command,
 * Claude-Code muscle memory in the browser. Open/close is owned by the parent;
 * picking a command delegates to the same handler the inline menu uses.
 */
export function CommandPalette({
  open,
  onClose,
  onPick,
}: {
  open: boolean;
  onClose: () => void;
  onPick: (c: SlashCommand) => void;
}) {
  const [q, setQ] = useState("");
  const [active, setActive] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const list = useMemo(() => (q ? matchCommands(`/${q}`) : COMMANDS), [q]);

  useEffect(() => {
    if (open) {
      setQ("");
      setActive(0);
      requestAnimationFrame(() => inputRef.current?.focus());
    }
  }, [open]);

  useEffect(() => {
    if (active >= list.length) setActive(0);
  }, [list, active]);

  if (!open) return null;

  function onKey(e: React.KeyboardEvent) {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActive((a) => Math.min(a + 1, list.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActive((a) => Math.max(a - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      const c = list[active];
      if (c) onPick(c);
    } else if (e.key === "Escape") {
      e.preventDefault();
      onClose();
    }
  }

  return (
    <div
      aria-hidden="true"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 80,
        background: "rgba(0,0,0,.55)",
        display: "grid",
        placeItems: "start center",
        paddingTop: "14vh",
      }}
    >
      <div
        style={{
          width: "min(560px, calc(100vw - 32px))",
          borderRadius: 14,
          border: "1px solid var(--line-hi)",
          background: "color-mix(in srgb, var(--surface) 97%, transparent)",
          boxShadow: "0 30px 80px -20px rgba(0,0,0,.7)",
          overflow: "hidden",
        }}
      >
        <input
          ref={inputRef}
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={onKey}
          placeholder="Run a command…"
          style={{
            width: "100%",
            padding: "16px 18px",
            background: "transparent",
            border: "none",
            borderBottom: "1px solid var(--line)",
            outline: "none",
            color: "var(--fg)",
            fontFamily: "Space Grotesk, sans-serif",
            fontSize: 15,
          }}
        />
        <div style={{ maxHeight: 320, overflowY: "auto", padding: 8 }}>
          {list.map((c, i) => (
            <button
              key={c.name}
              type="button"
              onMouseEnter={() => setActive(i)}
              onClick={() => onPick(c)}
              style={{
                width: "100%",
                display: "flex",
                alignItems: "baseline",
                gap: 12,
                padding: "10px 14px",
                borderRadius: 8,
                border: "none",
                textAlign: "left",
                cursor: "pointer",
                background:
                  i === active
                    ? "color-mix(in srgb, var(--accent) 14%, transparent)"
                    : "transparent",
              }}
            >
              <code
                style={{
                  fontFamily: "Space Mono, monospace",
                  fontSize: 13,
                  color: "var(--accent)",
                  flexShrink: 0,
                }}
              >
                /{c.name}
              </code>
              <span style={{ fontSize: 13, color: "var(--fg-2)" }}>{c.hint}</span>
            </button>
          ))}
          {list.length === 0 && (
            <div style={{ padding: 18, color: "var(--fg-3)", fontSize: 13 }}>
              No matching command
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
