# 12 — Long-term Memory

## Recommended vs Chosen

| | Choice | Cost |
|---|---|---|
| **Recommended** | Three free layers (rolling session summary + cross-session summary + extracted facts table). Add Anthropic memory tool as Layer 5 when on paid extension. | ₹0 in v1 |
| **Chosen** | **Same as recommended.** All three layers ship in v1 using free LLM providers for summarization and fact extraction. No vector store, no embeddings — keyword + recency only. Layer 5 deferred. | ₹0 |

---

## Context

The existing plan ([1-concierge-plan.md](../1-concierge-plan.md)) gives Orff a 20-turn sliding window from `concierge_turns`. That's working memory only — once a session passes 20 turns or the user starts a new session, prior context vanishes. Real assistant behavior needs Orff to remember things across days and weeks: "you mentioned you don't want Adani exposure," "last month we talked about your SIP allocation," "your target is ₹5 cr by 2035."

## Options

### A. Sliding window only (current plan)

Just `LIMIT 20` on `concierge_turns`. Anything older is invisible.

### B. Rolling session summary

When turns exceed N (e.g., 20), summarize the oldest turns into a compact paragraph stored on `concierge_sessions.rolling_summary`. Inject as a system block so the session feels continuous beyond N turns.

### C. Cross-session summary

Nightly job: for each active user, summarize the last 30 days of conversations into a few paragraphs. Stored on `concierge_user_memory.recent_summary`. Injected on every turn so Orff knows what was discussed last week even if it's a brand-new session.

### D. Explicit fact extraction

At session close, an LLM pass extracts typed facts: preferences, constraints, goals, style requests, life context. Stored in `concierge_user_facts` (free-text + category + confidence). Injected as a system block.

### E. Vector recall over past turns

Embed every turn or every session summary. At query time, embed the user's message, top-k retrieve relevant past content, inject.

### F. Anthropic memory tool (Claude 4.5+)

Anthropic's memory tool lets Claude read/write memory files on the server itself. Persistent across sessions; the model decides what to remember and what to recall. Only available when using the Anthropic API directly.

## Comparison

| Dimension | A. Window | B. Session summary | C. Cross-session summary | D. Facts table | E. Vector recall | F. Anthropic memory |
|---|---|---|---|---|---|---|
| Cost per turn | Free | Free (rare regen) | Free (nightly) | Free (per session close) | Free if local embeddings | Free read; tool calls bill normally |
| Latency added per turn | 0 | 0 (precomputed) | 0 (precomputed) | 0 (precomputed) | ~100ms (embed + query) | varies (tool round trips) |
| Token overhead per turn | 0 | ~500 | ~500–800 | ~300–800 | ~500–2k (retrieved chunks) | Anthropic-managed |
| Recall window | 20 turns | one session | 30 days | indefinite (curated) | indefinite | indefinite |
| Implementation cost | 0 (already in plan) | ~80 LOC | ~100 LOC + nightly job | ~150 LOC + extraction prompt | ~200 LOC + embedding infra | ~30 LOC; requires Anthropic |
| Risk of stale/wrong info | n/a | low (recent only) | medium (summary drift) | medium (false facts extracted) | low (citation possible) | low (Claude self-manages) |
| Provider-agnostic | yes | yes | yes | yes | yes | Anthropic-only |

## Tradeoffs

- **A only** is a non-starter for "personal assistant" expectations. Users will be frustrated when Orff forgets stated preferences.
- **B (session summary)** is the cheapest single upgrade. Without it, long sessions silently truncate context.
- **C (cross-session summary)** is what makes "remembering across days" feel real. The nightly cadence is fine — users don't expect real-time recall of yesterday's conversation, just *eventual* recall.
- **D (facts table)** is the highest-precision layer: stable preferences ("no tobacco", "₹5cr by 2035") deserve hard storage, not soft summarization. Avoids the summary-drift failure mode where a fact gets paraphrased into wrongness.
- **E (vector recall)** is overkill at our scale. The user generates ~5–50 turns/day; cross-session summary already condenses 30 days of that into 800 tokens. Vector recall makes sense once the summary itself becomes too lossy — which won't happen for years at single-user volume.
- **F (Anthropic memory)** is the right long-term answer once we're on the paid path. It's strictly more capable than D+C combined because the model decides what's worth remembering, not a fixed extraction prompt. But locking memory into one provider is a big commitment — keep B/C/D in place underneath so we're never trapped.

## Recommendation

**Ship B + C + D in v1. Skip E. Add F as Layer 5 when Anthropic ships.**

Layered injection order in the prompt (see [§4 of the architecture doc](../4-news-llm-architecture.md#4-prompt-assembly)):

| Block # | Layer | When updated |
|---|---|---|
| 3 | D — Long-term Facts | At session close (async) |
| 4 | C — Cross-session Summary | Nightly job |
| 7a | B — Session Rolling Summary | When session crosses 20 turns |
| 7b | A — Working History (last 20 turns) | Per-turn DB load |

### Free-provider summarization economics

For a single user generating ~30 turns/day across ~3 sessions:

- Session summaries: ~3 regens/day × ~3k input tokens × Groq Llama free → $0
- Fact extraction: ~3 runs/day × ~5k input tokens × Groq Llama free → $0
- Nightly cross-session: ~1 run/day × ~10k input tokens × Groq Llama free → $0

Free providers' free tiers easily absorb this. No paid services required.

### Fact-extraction prompt (sketch)

```
You are extracting durable user facts from a conversation between a portfolio
assistant (Orff) and its user. Output a JSON array of facts. Each fact must be:

- Stable (likely true for at least 6 months)
- Specific (not generic advice)
- User-revealing (about THIS user, not market opinions)

Categories: preference | constraint | goal | style | context

Output schema:
[
  {"fact": "...", "category": "...", "confidence": 0.0–1.0}
]

Conversation:
{turns}
```

Dedup before insert: for each new fact, compute a cheap local embedding, cosine-similarity against active facts of the same category, drop if cosine > 0.85.

## Open questions

- **Fact staleness**: a fact extracted 6 months ago may have changed silently. Should the nightly job re-validate by checking if a contradicting statement appears in recent sessions? Probably yes — flag conflicts for user review rather than auto-delete.
- **User control**: should the user see the extracted facts in a UI and be able to edit/delete? Yes - surface them in a dedicated Memory view once the core memory pipeline ships.
- **Privacy**: never include the intent document text or extracted facts in logs. Add a logging sanitizer.
- **Session-close detection**: a session is "closed" if idle 30 min OR user clicks "clear" OR opens a new chat. Implement as a debounced async task triggered from `concierge_memory_service.append_turn`.
- **Cold start**: a brand-new user has no facts and no cross-session summary. Prompt builder must handle empty blocks gracefully (omit them, don't inject `"None"`).
