# 13 — Holdings Context Injection

## Recommended vs Chosen

| | Choice | Cost |
|---|---|---|
| **Recommended** | Session-cached snapshot injected as a markdown block. Refresh hourly or on explicit user trigger. | Free |
| **Chosen** | **Same as recommended.** Pull from existing portfolio module on session open; cache per-session for 1 hour; format as compact markdown table; inject as prompt block 5. No tool-use in v1. | Free |

---

## Context

Orff is a portfolio assistant. Generic answers ("you should consider diversifying into IT") are useless when the user already holds 35% IT. The model needs to see the actual portfolio.

The existing `portfolio` module already aggregates positions across the user's brokers (Zerodha, Groww, AngelOne, IndMoney, Tickertape, Binance) and exposes them per-user. Concierge consumes that output, doesn't duplicate it.

## Options

### A. Full snapshot in system prompt (push)

Every session opens, fetch all holdings, format as markdown table, inject as a system block. Cache per-session.

### B. Filtered by query (push, filtered)

Per turn: extract tickers from the user's message, only inject those rows. Smaller payload but loses portfolio-level reasoning ("what's my financials exposure?").

### C. Tool-use (pull)

System prompt declares `get_holdings()` and `get_position(ticker)` tools. The model calls them when needed.

### D. RAG (semantic)

Embed each holding with its description/sector/news; retrieve top-k per query. Overkill at ~50 holdings.

## Comparison

| Dimension | A. Full snapshot | B. Filtered | C. Tool-use | D. RAG |
|---|---|---|---|---|
| Tokens per turn | ~1.5–3k | ~100–500 | 0 baseline, ~3k on tool call | ~500–1k |
| Latency added | One portfolio fetch per session | Same | Extra round trip on tool calls | Embed + query per turn |
| Portfolio-level reasoning quality | Excellent | Poor — model can't see other holdings | Excellent (when tool called) | OK |
| Per-ticker reasoning quality | Excellent | Excellent (target ticker present) | Excellent (when tool called) | OK |
| Build cost | Low (~50 LOC) | Low (~70 LOC) | Medium (~120 LOC, tool schema + handler) | High (~200 LOC) |
| Cache-friendly | Yes (snapshot stable for 1h) | No (changes per query) | Yes (tool schemas static) | Yes |
| Provider-agnostic | Yes | Yes | Provider tool-use support varies | Yes |

## Tradeoffs

- **A. Full snapshot** — best quality for the prompt-engineering effort. The cost (~2k tokens per turn) is trivial on free providers and modest on Anthropic with prompt caching. The portfolio fits comfortably; even 100 holdings render in ~3k tokens.
- **B. Filtered** — saves tokens but breaks every portfolio-level question. "What's my biggest position?" can't be answered because the model can't see the rest. Reject for v1.
- **C. Tool-use** — strictly better than A once on Anthropic with caching, because tool definitions stay in cache and the model only fetches when actually needed. Free-provider tool-use support is uneven (Gemini good, Groq newer, Cerebras variable). Skip for v1; revisit with Anthropic extension.
- **D. RAG** — wrong shape for this problem. The user has ~50 holdings, not 50,000. Semantic retrieval is unnecessary; the full set fits in context.

## Recommendation

**A. Full snapshot, session-cached, refresh-on-demand.**

### Cache key + TTL

- **Key**: `session_id` (not `user_id`) — same user in two browser tabs can have two sessions with different cached snapshots.
- **TTL**: 1 hour. Holdings change slowly (broker syncs are not instant); 1h is plenty fresh for conversation context.
- **Invalidation triggers**:
  - TTL expiry
  - User says "refresh holdings", "what are my latest positions", or similar (regex match in intent router)
  - Explicit `POST /api/v1/concierge/holdings/refresh` endpoint (future)
  - Broker sync completion event (future, requires broker module to emit an event)

### Snapshot rendering

Compact markdown table; max 50 rows by value (tail rows grouped as "Other"). See [§12 of the architecture doc](../4-news-llm-architecture.md#12-holdings-context-injection) for the format example.

Include rollups so the model doesn't have to do arithmetic:
- Total portfolio value
- Day P&L (absolute + %)
- Unrealised P&L (absolute + %)
- Sector weights (top 5)

### Privacy

- Never log full snapshots. Log only `{user_id, holding_count, total_value_lakhs}`.
- The snapshot is in-process memory only; never written to disk or sent anywhere except the LLM provider call.
- When using free providers, be aware the prompt is sent to the provider's API — that's a real privacy crossover. Document it. (When on Anthropic, same applies but their terms are clearer.)

## Migration path to tool-use (when on Anthropic)

```python
tools = [
    {
        "name": "get_holdings",
        "description": "Return the user's full current holdings snapshot.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_position",
        "description": "Return details for a single ticker the user holds.",
        "input_schema": {
            "type": "object",
            "properties": {"symbol": {"type": "string"}},
            "required": ["symbol"],
        },
    },
]
```

System prompt mentions: "You have access to the user's portfolio via tools. Call `get_holdings` if you need full context, `get_position(symbol)` for a single ticker." Anthropic prompt cache covers the tool definitions; actual data is fetched only when the model invokes them. Net token spend drops significantly for turns that don't need holdings.

## Open questions

- **Stale holdings vs sync lag**: if a broker hasn't synced in 6 hours, the snapshot is technically stale relative to reality. Surface a freshness indicator: `HOLDINGS as of {timestamp} (last broker sync: {sync_time})`.
- **Day P&L source**: needs live prices. The project has a [live-prices plan](../../docs/live-prices-plan.md) but it's not built yet. Until then, P&L is calculated against last EOD close — explicitly note this in the snapshot header.
- **Currency**: render in ₹ with lakh/crore notation. Don't translate to USD.
- **Hidden positions**: should the user be able to mark certain holdings as "don't share with Orff" (e.g., a position they're embarrassed about)? Add a `concierge_excluded_symbols` table later; out of scope for v1.
- **Watchlist injection**: similar to holdings but for tracked-not-owned symbols. Out of scope for v1; add as a Layer 5b later.
