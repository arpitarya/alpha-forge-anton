# 03 — News Retrieval Pattern

## Recommended vs Chosen

| | Choice | Cost |
|---|---|---|
| **Recommended** | Tool-use (`search_news`) + small headlines preamble | Anthropic paid; tool-use round-trips |
| **Chosen** | **A. In-context injection** — every relevant turn fetches a compact set of news items (titles + short summaries, plus full text for items matching the user's holdings or the query keywords) and stuffs them into the system prompt. No tool-use, no embeddings. | Free |

**Why the deviation**:
- Tool-use quality is uneven across free LLM providers (Gemini supports it well; Groq's function-calling is newer; Cerebras varies). In-context works identically everywhere.
- No prompt caching to optimize for in v1 (see [08](08-prompt-caching.md)), so the cache-friendliness argument for tool-use disappears.
- Implementation is ~50 LOC vs ~150 for tool-use plumbing.
- The token cost penalty of in-context injection is irrelevant on free tiers.

**Tradeoff accepted**: each turn ships ~3–8k extra tokens of news context the model may not need. Acceptable on free providers. When Anthropic is added, revisit tool-use to shrink the cached prefix.

---

## Context

News is the data source. The question is *how* news gets into Claude's context window when the user asks something news-relevant. Three patterns are viable.

## Options

### A. In-context injection (push everything)

Every turn, fetch the latest N news items for the user's holdings + recent macro and inject the full text into the system prompt.

```
system: [_SYSTEM] + "Recent news (last 24h):" + [top 30 articles, full text]
user: "What happened with Adani?"
```

### B. Tool-use / function calling (pull on demand)

System prompt declares a `search_news(query, ticker?, date_range?)` tool. Claude decides when to call it.

```
system: [_SYSTEM] + tool definitions
user: "What happened with Adani?"
assistant: → calls search_news(query="Adani", date_range="24h")
[tool result: 5 articles]
assistant: synthesizes answer
```

### C. RAG (semantic search via embeddings)

Background job embeds every news article into pgvector. Each turn, embed the user's query, top-k retrieve, inject results into the prompt.

```
user: "What happened with Adani?"
→ embed query → search pgvector → top 8 articles
system: [_SYSTEM] + [8 retrieved articles]
```

## Comparison

| Dimension | A. In-context | B. Tool-use | C. RAG |
|---|---|---|---|
| Tokens per turn | High (~10–30k) | Low when not called, medium when called | Low–medium (~3–8k) |
| Latency | Low (no extra round trip) | High (2× Claude calls for tool turns) | Medium (one embedding + vector query, ~100ms) |
| Cost per turn | High (Sonnet at 30k tokens = ~$0.09 input) | Low for non-news turns, ~2× for news turns | Medium (~$0.02 input + ~$0.0001 embedding) |
| Freshness | Real-time (last poll) | Real-time (Claude calls live) | Stale until next embed batch |
| Relevance quality | Poor (Claude wades through irrelevant items) | Good (Claude picks query) | Good (semantic match) |
| Build complexity | Trivial (~20 LOC) | Medium (tool schema + handler, ~80 LOC) | High (embedder + pgvector + retrieval + reindex job, ~250 LOC) |
| Works with Haiku routing | Yes but wasteful | Yes | Yes |
| Prompt cache friendliness | Bad (news changes invalidate cache) | Excellent (system prompt is static) | Good (system prompt static, retrieval injected after) |

## Tradeoffs

- **A. In-context** — simplest but expensive and breaks prompt caching. Every news refresh invalidates the cached system block, killing the 80% cache-hit-rate win from [08](08-prompt-caching.md). Also wastes Claude attention on items unrelated to the question.
- **B. Tool-use** — most "agentic" and lets Claude reason about when news matters. Two-call latency hurts (~3–5s end-to-end for news turns vs. ~1–2s for direct answers). Pairs beautifully with prompt caching since the system prompt never changes.
- **C. RAG** — best relevance per token spent. Needs the embedding infrastructure ([09](09-vector-db.md), [10](10-embedding-model.md)) and a reindex job. Stale-until-reindex window is fine for news (5-minute reindex cadence is plenty).

## Recommendation

**B. Tool-use as primary, with A. (light injection of headlines-only) as a complement.**

Specifically:
1. System prompt always includes a compact "recent headlines (24h)" block — just titles + tickers, ~500 tokens. Keeps cache valid for 5 min between refreshes and gives Claude awareness that news exists.
2. A `search_news(query, ticker?, date_range?)` tool is declared. When the user asks something news-specific, Claude calls it and gets full article text.
3. Skip RAG for v1. Reconsider if the news corpus grows past ~10k articles or if tool-use precision proves insufficient.

Rationale:
- Avoids the embedding infra cost upfront (saves [09](09-vector-db.md) and [10](10-embedding-model.md) from being needed yet).
- Cache-friendly: headlines block is small enough that even when it changes every 5 min, the rest of the cached system prompt stays valid for the rest of the session.
- Latency-acceptable: tool-use adds ~2s for news turns, but news turns are a minority. Factoid/portfolio turns stay fast.
- RAG can be layered on later by making `search_news` switch its backend from keyword DB query to vector search — no API change.

## Open questions

- How many headlines fit in the cache-friendly preamble before it hurts more than it helps? Probably 30–50.
- Should the tool also accept a `summarize_only: bool` to return just titles (saves output tokens when Claude is exploring)?
- For multi-turn news threads, should retrieved articles persist into the session's working set so Claude doesn't re-fetch?
