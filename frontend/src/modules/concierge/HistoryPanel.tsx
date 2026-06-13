"use client";

import { useDeleteSession, useHistory } from "./concierge.history";
import { PanelFrame } from "./MemoryPanel";

/**
 * Conversation history — the chat-app sidebar of past chats, persisted in elgar
 * (see history_service.py). Click a row to resume it; ✕ deletes it from the store.
 */
export function HistoryPanel({
  activeId,
  onResume,
  onClose,
}: {
  activeId: string;
  onResume: (id: string) => void;
  onClose: () => void;
}) {
  const { data, isLoading } = useHistory();
  const del = useDeleteSession();
  const sessions = data ?? [];

  return (
    <PanelFrame title="History" subtitle="Past chats, stored in elgar" onClose={onClose}>
      <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: 6 }}>
        {isLoading ? (
          <Empty text="Loading…" />
        ) : sessions.length === 0 ? (
          <Empty text="No saved conversations yet" />
        ) : (
          sessions.map((s) => (
            <div
              key={s.id}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                padding: "9px 11px",
                borderRadius: 8,
                border: "1px solid var(--line)",
                background:
                  s.id === activeId
                    ? "color-mix(in srgb, var(--accent) 14%, transparent)"
                    : "color-mix(in srgb, var(--surface-lo) 50%, transparent)",
              }}
            >
              <button
                type="button"
                onClick={() => onResume(s.id)}
                title="Resume this conversation"
                style={{
                  flex: 1,
                  minWidth: 0,
                  textAlign: "left",
                  background: "transparent",
                  border: "none",
                  cursor: "pointer",
                  color: "var(--fg)",
                  fontFamily: "Space Grotesk, sans-serif",
                  fontSize: 13,
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                {s.title || "Untitled chat"}
              </button>
              <button
                type="button"
                onClick={() => del.mutate(s.id)}
                title="Delete from store"
                disabled={del.isPending}
                style={{
                  flex: "none",
                  width: 22,
                  height: 22,
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
          ))
        )}
      </div>
    </PanelFrame>
  );
}

function Empty({ text }: { text: string }) {
  return (
    <div
      style={{
        marginTop: 24,
        textAlign: "center",
        fontFamily: "Space Mono, monospace",
        fontSize: 10,
        letterSpacing: "0.12em",
        textTransform: "uppercase",
        color: "var(--fg-4)",
      }}
    >
      {text}
    </div>
  );
}
