# 08 — Prompt Caching

## Recommended vs Chosen

| | Choice | Cost |
|---|---|---|
| **Recommended** | Ephemeral (5-min) cache on system + tools + headlines; 1-hour cache on portfolio snapshot | Anthropic-paid feature |
| **Chosen** | **Defer caching entirely for v1.** Free providers have inconsistent or no prompt-cache support (Gemini has context caching as a paid feature, Groq and Cerebras don't expose one). The recommendation only activates when Anthropic is added. | ₹0 |

**Why the deviation**: prompt caching is an Anthropic-pricing optimization. With free providers we're not paying per token, so there's nothing to optimize. When Anthropic is added in the future extension, apply the recommendation below as-is — the prompt structure should already be cache-friendly (system block first, history last) so the migration is a one-line change.

---

## Context

Anthropic supports prompt caching: mark a block with `cache_control` and subsequent requests reusing that prefix are billed at ~10% input rate (cache reads) instead of full price, with cache writes at ~125% on first write. Two TTL tiers exist.

The plan calls for ephemeral caching on the system block. This doc validates that and explores when the 1-hour tier earns its keep.

## Options

| Tier | TTL | Read cost | Write cost | Best for |
|---|---|---|---|---|
| **Ephemeral (5-min)** | 5 minutes | ~10% of base input | ~125% of base input | Active conversation turns within a session |
| **1-hour** | 1 hour | ~10% of base input | ~200% of base input | Long-lived prompts reused across multiple sessions |
| **None** | n/a | 100% | n/a | One-shot calls |

(Multipliers approximate — confirm against Anthropic's pricing page.)

## What to cache in Orff

| Block | Static? | Size | Cache tier | Why |
|---|---|---|---|---|
| `_SYSTEM` (Orff persona + rules) | Yes | ~500–800 tokens | Ephemeral | Re-read on every turn in a session |
| Tool definitions (`search_news`, etc.) | Yes | ~300–500 tokens | Ephemeral | Same |
| Recent headlines preamble | Refreshed every ~5 min | ~500 tokens | Ephemeral | Lives exactly within the 5-min TTL by design |
| Portfolio snapshot | Refreshed daily | ~1–2k tokens | 1-hour | Stable for hours; user has multiple sessions per day |
| Per-turn history (`load_history` rows) | Dynamic | Variable | None | Changes every turn; not cacheable |
| Current user message | Dynamic | Small | None | Same |

## Tradeoffs

- **Ephemeral only** (current plan) — cheap and simple. 5-min window means a conversation that pauses for 10 min between turns pays a fresh cache-write on resumption. For active back-and-forth this is fine.
- **1-hour for portfolio snapshot** — meaningful win if the user starts a second session within an hour. Portfolio snapshot is a few thousand tokens; writing it once at the 200% rate and reading 5× at 10% is net ~70% cheaper than no cache.
- **Both tiers stacked** — Anthropic supports multiple cache breakpoints in one request. You can cache the system prompt at ephemeral and the portfolio snapshot at 1-hour independently. This is the optimal layout but adds prompt-construction complexity.
- **No caching** — fine for prototyping; wasteful in steady state. Saves ~70–80% on input tokens once a session has 3+ turns.

## Cache invalidation gotchas

Cache hits require *byte-exact* prefix match. Things that quietly invalidate the cache:
- Reordering tool definitions (alphabetize and lock the order).
- Reformatting the system prompt (no trailing-whitespace drift).
- Refreshing the headlines preamble at non-5-min boundaries means most writes don't get reused — align refresh cadence with the cache TTL.
- Mixing portfolio snapshot freshness between users would matter in multi-tenant; single-tenant Anton sidesteps this.

## Recommendation

**Start with ephemeral on the system + tools + headlines blocks. Add a 1-hour cache breakpoint for the portfolio snapshot when it's injected.**

Layout:
```
messages payload = [
  { type: "system", text: _SYSTEM + TOOL_DEFS, cache_control: { type: "ephemeral" } },
  { type: "system", text: RECENT_HEADLINES_24H,    cache_control: { type: "ephemeral" } },
  { type: "system", text: PORTFOLIO_SNAPSHOT,      cache_control: { type: "ephemeral", ttl: "1h" } },
  ...history,
  current_user_message,
]
```

Rationale:
- The system+tools block is the highest-leverage cache target: read on every turn, totally static, ~1k tokens.
- The headlines block fits exactly the 5-min ephemeral window — refresh cadence aligns naturally.
- The portfolio snapshot benefits from the 1-hour tier because the user often comes back to chat across multiple short sessions in a day.
- Per-turn history and the current message stay uncached (they're dynamic by definition).

## Open questions

- Anthropic charges differently for ephemeral vs 1-hour writes — at what session-count crossover does 1-hour beat ephemeral for portfolio? Probably 2+ sessions per hour.
- Should we log cache hit rates per session to a debug table for tuning?
- If we go RAG ([03 option C](03-news-retrieval-pattern.md)), the retrieved chunks are dynamic per query and can't be cached — but the retrieval system prompt scaffolding can. Plan for both.
- Beware: Anthropic occasionally adjusts pricing multipliers — the recommendation is structurally right even if exact economics shift.
