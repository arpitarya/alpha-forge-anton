"use client";

import { useCallback, useRef, useState } from "react";
import { type ChatTurn, type ModelId, resolveAutoModel } from "./chat.types";

interface StreamPayload {
  content?: string;
  provider?: string;
  model?: string;
  prompt_tokens?: number;
  completion_tokens?: number;
  elapsed_s?: number;
  error?: string;
}

function getToken(): string | null {
  return typeof window !== "undefined" ? localStorage.getItem("af_token") : null;
}

function nanoid(): string {
  return Math.random().toString(36).slice(2, 10);
}

const MAX_RESPONSE_CHARS = 32_000;

// Strip control chars, Unicode LS/PS, zero-width + BOM chars.
// All code points expressed as hex to avoid embedding invisible chars in source.
function sanitizeContent(raw: string): string {
  let out = "";
  for (let i = 0; i < raw.length && out.length < MAX_RESPONSE_CHARS; i++) {
    const cp = raw.charCodeAt(i);
    // Keep \t (0x09) and \n (0x0A); drop other C0 controls and DEL (0x7F)
    if ((cp < 0x20 && cp !== 0x09 && cp !== 0x0a) || cp === 0x7f) continue;
    // LS (U+2028) and PS (U+2029) -> newline
    if (cp === 0x2028 || cp === 0x2029) {
      out += "\n";
      continue;
    }
    // Zero-width space (U+200B), non-joiner (U+200C), joiner (U+200D), BOM (U+FEFF)
    if (cp === 0x200b || cp === 0x200c || cp === 0x200d || cp === 0xfeff) continue;
    out += raw[i];
  }
  return out;
}

export function useChatStream() {
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [open, setOpen] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const patchTurn = useCallback((id: string, patch: Partial<ChatTurn>) => {
    setTurns((prev) => prev.map((t) => (t.id === id ? { ...t, ...patch } : t)));
  }, []);

  const submit = useCallback(
    async (query: string, modelId: ModelId) => {
      if (!query.trim()) return;

      const resolved = modelId === "auto" ? resolveAutoModel(query) : modelId;
      const id = nanoid();
      const newTurn: ChatTurn = {
        id,
        query,
        response: null,
        provider: null,
        model: null,
        elapsed: null,
        tokens: null,
        error: null,
        loading: true,
        resolvedModel: resolved,
      };

      setOpen(true);
      setTurns((prev) => [...prev, newTurn]);

      // Build history for multi-turn context (last 6 turns)
      const history = turns.slice(-6).flatMap((t) => {
        const msgs: { role: "user" | "assistant"; content: string }[] = [
          { role: "user", content: t.query },
        ];
        if (t.response) msgs.push({ role: "assistant", content: t.response });
        return msgs;
      });
      history.push({ role: "user", content: query });

      abortRef.current?.abort();
      const ctrl = new AbortController();
      abortRef.current = ctrl;

      try {
        const token = getToken();
        const res = await fetch("/api/v1/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({ messages: history, model: modelId }),
          signal: ctrl.signal,
        });

        if (!res.ok || !res.body) {
          patchTurn(id, { loading: false, error: `HTTP ${res.status}` });
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
              patchTurn(id, { loading: false });
              break;
            }
            try {
              const payload: StreamPayload = JSON.parse(raw);
              if (payload.error) {
                patchTurn(id, { loading: false, error: payload.error });
              } else {
                patchTurn(id, {
                  response: payload.content != null ? sanitizeContent(payload.content) : null,
                  provider: payload.provider ?? null,
                  model: payload.model ?? null,
                  elapsed: payload.elapsed_s ?? null,
                  tokens: (payload.prompt_tokens ?? 0) + (payload.completion_tokens ?? 0),
                  loading: false,
                });
              }
            } catch {
              // malformed SSE chunk — skip
            }
          }
        }
      } catch (err: unknown) {
        if ((err as Error)?.name !== "AbortError") {
          patchTurn(id, { loading: false, error: String(err) });
        }
      }
    },
    [turns, patchTurn],
  );

  const clear = useCallback(() => setTurns([]), []);

  return { turns, open, setOpen, submit, clear };
}
