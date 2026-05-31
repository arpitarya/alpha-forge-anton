# 24 — Streaming Protocol (Typed Events)

## Recommended vs Chosen

| | Choice | Cost |
|---|---|---|
| **Recommended** | Typed SSE events distinguishing thinking / plan / tool_call / tool_result / content / verification / meta | Free |
| **Chosen** | **Typed SSE event protocol with named event types. Each event is `event: <type>\ndata: <json>\n\n`. Frontend hook dispatches by type to update separate UI regions (thinking trace, plan visualizer, tool activity feed, final answer, verification flags, meta).** | Free |

---

## Context

The v1 substrate uses untyped SSE frames (`data: {"delta": "..."}`). The planned chat UI displays model work visibly: thinking traces, plan steps, tool invocations, and sources. To support this, the streaming protocol must carry typed events, not just text deltas.

This doc upgrades the streaming envelope to support the typed-event UX needed by reasoning models ([16](16-reasoning-model.md)), agentic loop ([17](17-agentic-loop.md)), tool calls ([19](19-tool-calling.md)), and verifier pass ([25](25-verifier-pass.md)).

## Options

### A. Stay untyped (current plan)

Single event type, payload distinguishes by field presence. Simple; frontend grows messy switching on payload shape.

### B. Named SSE events with typed payloads

Use SSE `event:` lines to carry type. Frontend dispatches via `addEventListener` (EventSource) or by parsing event lines (fetch reader).

### C. WebSocket with typed messages

Move to WebSocket; each message is JSON with `type` field. More flexible but adds transport complexity ([06](06-streaming-transport.md) chose SSE for good reasons).

### D. NDJSON over HTTP

Each line is a typed JSON object. Equivalent to B but without SSE conventions. Loses standard SSE tooling.

## Recommendation

**B. Named SSE events.** Builds on the SSE choice from [06](06-streaming-transport.md) without changing transport.

## Event types

| Event | When | Payload |
|---|---|---|
| `session` | First frame | `{"session_id": "uuid", "model": "...", "provider": "..."}` |
| `intent` | After intent classification | `{"intent": "investment_plan", "model_routed_to": "reasoning"}` |
| `thinking_delta` | During reasoning model thinking | `{"text": "..."}` |
| `thinking_end` | Reasoning done | `{"total_thinking_tokens": 1284, "elapsed_ms": 4200}` |
| `plan` | Plan-execute loop emits plan | `{"plan": [...PlanStep], "iteration": 1}` |
| `step_start` | Plan step begins | `{"step_id": "s1", "description": "..."}` |
| `tool_call` | Tool invocation | `{"call_id": "tc_1", "step_id": "s1", "name": "get_price", "args": {...}}` |
| `tool_result` | Tool returns | `{"call_id": "tc_1", "ok": true, "result": {...}, "latency_ms": 230}` |
| `step_complete` | Plan step done | `{"step_id": "s1", "summary": "..."}` |
| `content_delta` | Final answer streaming | `{"text": "..."}` |
| `citation` | Reference to a source | `{"id": "c1", "url": "...", "title": "...", "source_type": "news\|web\|tool"}` |
| `verification` | Verifier flags a claim | `{"claim": "...", "verdict": "verified\|unverified\|contradicted", "evidence": "..."}` |
| `meta` | Final summary | `{"tokens_in": ..., "tokens_out": ..., "elapsed_ms": ..., "model": ..., "provider": ..., "tool_calls": 4, "news_sources_used": [...]}` |
| `error` | Any failure | `{"code": "...", "message": "...", "recoverable": bool}` |
| `done` | Stream end sentinel | `{}` (or omit) |

## Wire format

```
event: session
data: {"session_id":"abc-123","model":"reasoning","provider":"groq"}

event: intent
data: {"intent":"investment_plan","model_routed_to":"reasoning"}

event: thinking_delta
data: {"text":"Let me think about the user's portfolio..."}

event: thinking_delta
data: {"text":" Their AI exposure is high..."}

event: thinking_end
data: {"total_thinking_tokens":1284,"elapsed_ms":4200}

event: plan
data: {"plan":[{"id":"s1","description":"Fetch current prices",...}],"iteration":1}

event: step_start
data: {"step_id":"s1","description":"Fetch current prices"}

event: tool_call
data: {"call_id":"tc_1","step_id":"s1","name":"get_price","args":{"symbol":"RELIANCE"}}

event: tool_result
data: {"call_id":"tc_1","ok":true,"result":{"ltp":2890,"asof":"..."},"latency_ms":230}

event: step_complete
data: {"step_id":"s1","summary":"Got prices for 3 tickers"}

event: content_delta
data: {"text":"Based on your portfolio,"}

event: content_delta
data: {"text":" your AI exposure"}

event: citation
data: {"id":"c1","url":"https://...","title":"...","source_type":"news"}

event: verification
data: {"claim":"AI exposure is 28%","verdict":"verified","evidence":"computed from holdings"}

event: meta
data: {"tokens_in":3420,"tokens_out":890,"elapsed_ms":12300,"model":"deepseek-r1-distill-70b","provider":"groq","tool_calls":4,"news_sources_used":["moneycontrol-rss","nse-announcements"]}

event: done
data: {}
```

## Frontend hook shape

```typescript
type ConciergeEvent =
  | { type: 'session'; sessionId: string; model: string; provider: string }
  | { type: 'intent'; intent: string; modelRoutedTo: string }
  | { type: 'thinking_delta'; text: string }
  | { type: 'thinking_end'; totalThinkingTokens: number; elapsedMs: number }
  | { type: 'plan'; plan: PlanStep[]; iteration: number }
  | { type: 'step_start'; stepId: string; description: string }
  | { type: 'tool_call'; callId: string; stepId: string; name: string; args: unknown }
  | { type: 'tool_result'; callId: string; ok: boolean; result: unknown; latencyMs: number }
  | { type: 'step_complete'; stepId: string; summary: string }
  | { type: 'content_delta'; text: string }
  | { type: 'citation'; id: string; url: string; title: string; sourceType: string }
  | { type: 'verification'; claim: string; verdict: string; evidence: string }
  | { type: 'meta'; /* ... */ }
  | { type: 'error'; code: string; message: string; recoverable: boolean }
  | { type: 'done' };
```

Hook reducer splits state into separate slices:

```typescript
interface ConciergeTurnState {
  thinking: { text: string; tokens: number; elapsedMs: number; collapsed: boolean };
  plan: { steps: PlanStep[]; currentStep: string | null };
  tools: { calls: ToolCall[]; results: ToolResult[] };
  content: string;
  citations: Citation[];
  verifications: Verification[];
  meta: Meta | null;
  status: 'streaming' | 'complete' | 'error';
}
```

Each event type updates the corresponding slice. UI renders each slice independently.

## UI regions

```
┌─────────────────────────────────────────────┐
│ [User message]                              │
├─────────────────────────────────────────────┤
│ ▶ Thinking (1284 tokens, 4.2s) [collapsed]  │  ← thinking_delta accumulates here
├─────────────────────────────────────────────┤
│ Plan (4 steps):                             │  ← plan event renders
│   ✓ s1 Fetch prices                         │
│   ✓ s2 Compute weights                      │
│   ⟳ s3 Compare to target                    │  ← step_start sets ⟳, step_complete sets ✓
│   · s4 Recommend                            │
├─────────────────────────────────────────────┤
│ Tool activity:                              │  ← tool_call + tool_result feed
│   • get_price(RELIANCE) → ₹2,890 (230ms)    │
│   • get_price(HDFCBANK) → ₹1,685 (210ms)    │
│   • compute_sector_weights → IT: 28% ...    │
├─────────────────────────────────────────────┤
│ Answer:                                     │  ← content_delta streams here
│ Based on your portfolio, your AI exposure   │
│ is 28% — well above your 20% target...      │
│                                             │
│ [1] Moneycontrol  [2] NSE filing            │  ← citations
├─────────────────────────────────────────────┤
│ Verified:                                   │  ← verification events
│ ✓ AI exposure: 28% (computed)               │
│ ✓ Target: 20% (from intent doc)             │
│ ⚠ Earnings date: unverified                 │
└─────────────────────────────────────────────┘
```

## Backwards compatibility

The v1 substrate uses untyped frames. To not break existing clients during the upgrade:

1. New events are *additive*. Old `{"delta": "..."}` frames continue working under `event: content_delta` (the data shape just gains `type: "content_delta"`).
2. Old clients ignore unknown event types (SSE spec behavior). They'll see only `content_delta` and `meta` — degraded but functional.
3. Bump the route to `/api/v1/concierge/stream/v2` if needed, and keep v1 routes for one release cycle.

## Cancellation

Same as v1 substrate ([06](06-streaming-transport.md)) — `AbortController` on client; backend generator catches `CancelledError`. Mid-stream cancellation emits a final `event: error\ndata: {"code":"cancelled"}` if backend gets a chance, otherwise just closes the stream.

## Error semantics

Errors mid-stream emit `event: error` and the stream ends:

```
event: error
data: {"code": "tool_timeout", "message": "search_news timed out after 8s", "recoverable": false}
```

`recoverable: true` errors (transient provider hiccup) can be retried client-side automatically. `recoverable: false` errors surface as a turn-level error.

## Open questions

- **Heartbeat events** every 15s to keep proxies open? Use SSE comment lines (`:\n\n`) to avoid polluting the typed event stream.
- **Event versioning**: when we add a new event type, do clients break? No — unknown types are skipped. Document the contract.
- **Snapshot replay**: for testing and debugging, capture full event streams to disk and replay. Built-in to the SSE client makes this easy.
- **Compression**: long thinking traces could benefit from `Content-Encoding: gzip`. SSE is just chunked HTTP, so gzip works. Verify Next.js proxy doesn't buffer.
- **Reasoning trace token budget**: very long thinking traces (10k+ tokens) bloat the UI. Cap visible trace, show "show full" link if user wants it.
- **Frontend rendering performance**: rapid `content_delta` events can re-render expensively. Batch into animation frames.
