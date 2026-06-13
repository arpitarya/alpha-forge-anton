"use client";

import { useCallback, useMemo, useRef, useState } from "react";
import { reduceEvent, type StreamPayload } from "./chat.events";
import type { SessionDoc, SessionTurnDTO } from "./concierge.history";
import {
  activeModelFor,
  type ChatTurn,
  type ModelChoice,
  type ProviderId,
} from "./concierge.types";

function getToken(): string | null {
  return typeof window !== "undefined" ? localStorage.getItem("af_token") : null;
}

function nanoid(): string {
  return Math.random().toString(36).slice(2, 10);
}

export interface SessionTotals {
  tokens: number;
  costUsd: number;
  turns: number;
}

/** Rebuild a display turn from a stored (resume-only) turn — no live stream state. */
function turnFromDTO(t: SessionTurnDTO): ChatTurn {
  return {
    id: nanoid(),
    query: t.query,
    response: t.response || null,
    provider: t.provider,
    model: t.model,
    elapsed: null,
    tokens: null,
    error: null,
    loading: false,
    active: {
      provider: (t.provider as ProviderId) ?? "gemini",
      modelId: t.model ?? "",
      providerName: t.provider ?? "",
      modelName: t.model ?? "",
      autoLevel: "none",
    },
    images: [],
    thinking: null,
    tools: [],
    confirm: null,
    followups: [],
    costUsd: null,
  };
}

export function useChatStream() {
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [open, setOpen] = useState(false);
  const [sessionId, setSessionId] = useState(nanoid);
  const abortRef = useRef<AbortController | null>(null);

  const patchTurn = useCallback((id: string, patch: Partial<ChatTurn>) => {
    setTurns((prev) => prev.map((t) => (t.id === id ? { ...t, ...patch } : t)));
  }, []);

  const run = useCallback(
    async (
      turn: ChatTurn,
      history: { role: "user" | "assistant"; content: string }[],
      images: string[],
      active: ChatTurn["active"],
    ) => {
      abortRef.current?.abort();
      const ctrl = new AbortController();
      abortRef.current = ctrl;
      try {
        const token = getToken();
        const last = history[history.length - 1];
        const body = history.map((m) => (m === last ? { ...m, images } : m));
        const res = await fetch("/api/v1/concierge", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({
            messages: body,
            provider: active.provider,
            model_id: active.modelId,
            auto_level: active.autoLevel,
          }),
          signal: ctrl.signal,
        });
        if (!res.ok || !res.body) {
          patchTurn(turn.id, { loading: false, error: `HTTP ${res.status}` });
          return;
        }
        const reader = res.body.getReader();
        const dec = new TextDecoder();
        let buf = "";
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buf += dec.decode(value, { stream: true });
          const lines = buf.split("\n");
          buf = lines.pop() ?? "";
          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            const raw = line.slice(6).trim();
            if (raw === "[DONE]") {
              patchTurn(turn.id, { loading: false });
              break;
            }
            try {
              const payload: StreamPayload = JSON.parse(raw);
              setTurns((prev) =>
                prev.map((t) => (t.id === turn.id ? { ...t, ...reduceEvent(t, payload) } : t)),
              );
            } catch {
              // malformed SSE chunk — skip
            }
          }
        }
      } catch (err: unknown) {
        if ((err as Error)?.name !== "AbortError") {
          patchTurn(turn.id, { loading: false, error: String(err) });
        }
      }
    },
    [patchTurn],
  );

  const submit = useCallback(
    async (query: string, choice: ModelChoice, images: string[] = []) => {
      if (!query.trim() && !images.length) return;
      const active = activeModelFor(choice, query);
      const id = nanoid();
      setOpen(true);
      setTurns((prev) => {
        const next: ChatTurn = {
          id,
          query,
          response: null,
          provider: null,
          model: null,
          elapsed: null,
          tokens: null,
          error: null,
          loading: true,
          active,
          images,
          thinking: null,
          tools: [],
          confirm: null,
          followups: [],
          costUsd: null,
        };
        return [...prev, next];
      });
      const prior = turns.slice(-6).flatMap((t) => {
        const msgs: { role: "user" | "assistant"; content: string }[] = [
          { role: "user", content: t.query },
        ];
        if (t.response) msgs.push({ role: "assistant", content: t.response });
        return msgs;
      });
      prior.push({ role: "user", content: query });
      await run({ id } as ChatTurn, prior, images, active);
    },
    [turns, run],
  );

  // Edit a prior user turn: drop it and everything after, then resubmit (branch).
  const editTurn = useCallback(
    (id: string, newQuery: string, choice: ModelChoice) => {
      const idx = turns.findIndex((t) => t.id === id);
      if (idx < 0) return;
      const kept = turns.slice(0, idx);
      setTurns(kept);
      const active = activeModelFor(choice, newQuery);
      const prior = kept.slice(-6).flatMap((t) => {
        const msgs: { role: "user" | "assistant"; content: string }[] = [
          { role: "user", content: t.query },
        ];
        if (t.response) msgs.push({ role: "assistant", content: t.response });
        return msgs;
      });
      prior.push({ role: "user", content: newQuery });
      const newId = nanoid();
      setTurns((prev) => [
        ...prev,
        {
          id: newId,
          query: newQuery,
          response: null,
          provider: null,
          model: null,
          elapsed: null,
          tokens: null,
          error: null,
          loading: true,
          active,
          images: [],
          thinking: null,
          tools: [],
          confirm: null,
          followups: [],
          costUsd: null,
        },
      ]);
      void run({ id: newId } as ChatTurn, prior, [], active);
    },
    [turns, run],
  );

  const stop = useCallback(() => {
    abortRef.current?.abort();
    setTurns((prev) => prev.map((t) => (t.loading ? { ...t, loading: false } : t)));
  }, []);

  // New conversation: blank thread + a fresh session id so the next save is a
  // new elgar doc rather than overwriting the one we just left.
  const clear = useCallback(() => {
    abortRef.current?.abort();
    setTurns([]);
    setSessionId(nanoid());
  }, []);

  // Resume a stored conversation: adopt its id (so further saves overwrite it)
  // and rebuild its turns for display.
  const hydrate = useCallback((doc: SessionDoc) => {
    abortRef.current?.abort();
    setSessionId(doc.id);
    setTurns(doc.turns.map(turnFromDTO));
    setOpen(true);
  }, []);

  const totals = useMemo<SessionTotals>(
    () => ({
      tokens: turns.reduce((s, t) => s + (t.tokens ?? 0), 0),
      costUsd: turns.reduce((s, t) => s + (t.costUsd ?? 0), 0),
      turns: turns.length,
    }),
    [turns],
  );

  return { turns, open, setOpen, sessionId, submit, editTurn, stop, clear, hydrate, totals };
}
