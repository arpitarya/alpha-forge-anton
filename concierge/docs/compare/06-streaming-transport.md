# 06 — Streaming Transport

## Recommended vs Chosen

| | Choice | Cost |
|---|---|---|
| **Recommended** | SSE via `fetch` + `AbortController` | Free |
| **Chosen** | **SSE via `fetch` + `AbortController`** — matches the recommendation. Works identically with the existing LLMGateway streaming and future Anthropic SDK streaming. | ₹0 |

No deviation. The gateway already exposes async iterators that pipe cleanly into `StreamingResponse`.

---

## Context

Orff needs to stream Claude's tokens to the browser as they arrive. The plan implies SSE via FastAPI `StreamingResponse`. This doc validates that against the alternatives.

## Options

| Transport | Direction | Browser API | Reconnect | Through Next.js proxy | Auth |
|---|---|---|---|---|---|
| **SSE** (`text/event-stream`) | Server → Client | Native `EventSource` (but limited) or `fetch` reader | Built-in for `EventSource`; manual for `fetch` | Yes, native | Header pass-through works |
| **WebSocket** | Bidirectional | Native `WebSocket` | Manual | Yes but more setup | Token-in-URL or first-frame auth (header support is browser-spotty) |
| **HTTP chunked (raw)** | Server → Client | `fetch` + `ReadableStream` reader | Manual | Yes | Headers work normally |
| **Long-polling** | Server → Client (request/response) | `fetch` loop | Trivial | Yes | Headers work |

## Tradeoffs

- **SSE via `fetch` reader** — what the existing `useConciergeStream` likely uses. Works through Next.js rewrites cleanly. Supports custom headers (so `Authorization: Bearer` works), unlike `EventSource` which can't send headers. SSE is a thin framing on top of chunked HTTP, so it's the "obvious" path for one-way token streams.
- **WebSocket** — overkill for one-way streaming. Bidirectional is unused (the client doesn't push mid-stream). Adds complexity for auth (headers don't survive the WebSocket upgrade reliably in browsers), proxy config (Next.js rewrites don't natively proxy WS without extra work), and reconnect logic. Worth it only if the future voice path needs bidirectional binary audio streams — and even then a separate WS endpoint is cleaner than mixing modes on one channel.
- **HTTP chunked (raw)** — basically SSE without the framing convention. You'd write your own delimiter scheme. No upside over SSE; SSE's `data:` / `event:` / `id:` convention is well-tooled.
- **Long-polling** — defeats the point of streaming. Skip.

## Cancellation

Critical for chat UX. User clicks Stop or sends a new message → previous stream must abort to avoid double-charging tokens.

| Transport | Cancellation mechanism |
|---|---|
| SSE via `fetch` | `AbortController.abort()` cleanly cancels |
| WebSocket | `ws.close()` |
| HTTP chunked | Same as SSE |

All three support clean cancellation. No differentiator.

## Anthropic SDK compatibility

The Anthropic Python SDK exposes `client.messages.stream(...)` as an async iterator of typed events. This works equally well piped into:
- `StreamingResponse(generator(), media_type="text/event-stream")` — for SSE
- `StreamingResponse(generator(), media_type="application/x-ndjson")` — for raw chunked NDJSON

The SDK doesn't care about transport. The choice is purely a client-side ergonomics question.

## Recommendation

**SSE via `fetch` reader + `AbortController` — as currently implied by the plan.**

Concretely:
- Backend: `StreamingResponse(sse_generator(), media_type="text/event-stream")`
- Frame format: each line is `data: {json}\n\n`. First frame carries `{"session_id": "..."}`, middle frames carry `{"delta": "token"}`, final frame carries `{"meta": {...tokens, elapsed_ms...}}`, then `data: [DONE]\n\n`.
- Client: `fetch` with `AbortController`, read body as `ReadableStream`, parse line-by-line.

Rationale:
- Works through Next.js proxy with zero special config.
- Native `Authorization` header support.
- One-way streaming is exactly SSE's design target.
- Future voice can have its own WebSocket endpoint for audio if needed — no reason to converge transports.
- AbortController gives clean cancellation already wired in modern hooks.

## Open questions

- Should errors mid-stream be sent as a typed SSE event (`event: error\ndata: {...}\n\n`) or as a malformed-on-purpose final frame? Typed event is cleaner — pick that.
- Heartbeat frames every 15s to keep proxies from dropping idle connections? Most don't need this on local dev, but production Cloudflare-style proxies sometimes do. Cheap to add (`:\n\n` comment lines).
- Do we want to expose token-level timing in meta frames for an "Orff thinking" debug HUD? Useful, basically free.
