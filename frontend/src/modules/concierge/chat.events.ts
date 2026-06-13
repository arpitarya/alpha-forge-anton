import type { UINode } from "./compose.types";
import type { ChatTurn, PendingAction, ToolStep } from "./concierge.types";

/**
 * One SSE event from the concierge stream. Mirrors the backend wire protocol in
 * concierge_service.py — a single JSON object per `data:` line. Each optional
 * field is its own event kind; a token snapshot carries `content` + meta.
 */
export interface StreamPayload {
  content?: string;
  provider?: string;
  model?: string;
  prompt_tokens?: number;
  completion_tokens?: number;
  cost_usd?: number;
  elapsed_s?: number;
  notice?: string;
  error?: string;
  /** Compose follow-up — a Fux-validated UISpec, separate from content. */
  spec?: UINode;
  /** A prompt-assembly / data-read step. */
  tool?: ToolStep;
  /** Reasoning trace split from a `<think>` block. */
  thinking?: string;
  /** Approval card for a mutating intent. */
  confirm?: PendingAction;
  /** Tap-to-send next-step prompts. */
  followups?: string[];
}

const MAX_RESPONSE_CHARS = 32_000;

/** Strip control chars, Unicode LS/PS, zero-width + BOM chars. */
export function sanitizeContent(raw: string): string {
  let out = "";
  for (let i = 0; i < raw.length && out.length < MAX_RESPONSE_CHARS; i++) {
    const cp = raw.charCodeAt(i);
    if ((cp < 0x20 && cp !== 0x09 && cp !== 0x0a) || cp === 0x7f) continue;
    if (cp === 0x2028 || cp === 0x2029) {
      out += "\n";
      continue;
    }
    if (cp === 0x200b || cp === 0x200c || cp === 0x200d || cp === 0xfeff) continue;
    out += raw[i];
  }
  return out;
}

/**
 * Reduce one stream event into a turn patch. Each branch is additive — a `spec`,
 * `thinking`, `tool`, `confirm`, or `followups` event never clobbers streamed text.
 */
export function reduceEvent(turn: ChatTurn, p: StreamPayload): Partial<ChatTurn> {
  if (p.error) return { loading: false, error: p.error };
  if (p.tool) return { tools: [...(turn.tools ?? []), p.tool] };
  if (p.thinking != null) return { thinking: sanitizeContent(p.thinking) };
  if (p.confirm) return { confirm: p.confirm };
  if (p.followups) return { followups: p.followups.slice(0, 3) };
  if (p.spec) return { spec: p.spec, elapsed: p.elapsed_s ?? turn.elapsed };
  return {
    response: p.content != null ? sanitizeContent(p.content) : turn.response,
    provider: p.provider ?? turn.provider,
    model: p.model ?? turn.model,
    elapsed: p.elapsed_s ?? turn.elapsed,
    tokens: (p.prompt_tokens ?? 0) + (p.completion_tokens ?? 0) || turn.tokens,
    costUsd: p.cost_usd ?? turn.costUsd,
    loading: false,
  };
}
