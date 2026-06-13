"use client";

import { useCallback, useEffect } from "react";
import { loadSession, type SessionDoc, useSaveSession } from "./concierge.history";
import type { ChatTurn } from "./concierge.types";

interface Stream {
  sessionId: string;
  turns: ChatTurn[];
  hydrate: (doc: SessionDoc) => void;
}

/**
 * Session persistence wiring: debounced auto-save of the active conversation to
 * elgar (one doc per session, see history_service.py) plus resume-by-id. The save
 * fires ~900ms after a turn settles, so a completed exchange is one store commit —
 * never per token.
 */
export function useSessions({ sessionId, turns, hydrate }: Stream) {
  const { mutate } = useSaveSession();

  useEffect(() => {
    if (turns.length === 0) return;
    const last = turns[turns.length - 1];
    if (last.loading || (!last.response && !last.error)) return;
    const handle = setTimeout(() => {
      mutate({
        id: sessionId,
        title: turns[0].query.slice(0, 80) || "Untitled chat",
        turns: turns.map((x) => ({
          query: x.query,
          response: x.response ?? "",
          provider: x.provider,
          model: x.model,
        })),
      });
    }, 900);
    return () => clearTimeout(handle);
  }, [sessionId, turns, mutate]);

  const onResume = useCallback((id: string) => void loadSession(id).then(hydrate), [hydrate]);

  return { onResume };
}
