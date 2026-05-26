# 07 — Intent Classification

## Recommended vs Chosen

| | Choice | Cost |
|---|---|---|
| **Recommended** | Regex + previous-model inheritance | Free |
| **Chosen** | **Regex + previous-model inheritance** — matches the recommendation. Adds zero latency and zero cost. | ₹0 |

No deviation. Regex routing maps cleanly onto the free-provider slug table in [02](02-claude-model-routing.md#recommended-vs-chosen).

---

## Context

The model router ([02](02-claude-model-routing.md)) needs to decide *which* Claude model to use per turn, based on what the user is asking. The current plan uses regex. This doc compares regex against two LLM-based alternatives.

## Options

### A. Regex / keyword heuristics

```python
INVESTMENT_PATTERNS = re.compile(r"\b(rebalance|allocate|sell|buy|plan|strategy|sip)\b", re.I)
NEWS_PATTERNS      = re.compile(r"\b(news|happened|today|announce|update)\b", re.I)
FACTOID_PATTERNS   = re.compile(r"\b(what is|price of|market cap|p/e|yield)\b", re.I)
```

Match → assign intent → pick model.

### B. Haiku micro-classifier

A pre-call to Haiku with a tiny system prompt:

```
Classify this user message into one of: factoid, news, portfolio, investment_plan, multi_turn.
Respond with only the label.
```

### C. Embedding similarity

Pre-embed N labeled examples per intent class. At runtime, embed the user message, cosine-similarity against the examples, pick nearest cluster.

## Comparison

| Dimension | A. Regex | B. Haiku classifier | C. Embeddings |
|---|---|---|---|
| Per-turn latency added | ~0ms | ~150–300ms | ~50–100ms (embed only) |
| Per-turn cost added | $0 | ~$0.0002 (50 tok in, 5 out) | ~$0.0001 (embed) |
| Accuracy on clear cases | ~70–80% | ~95%+ | ~90% |
| Accuracy on ambiguous cases | Bad | Good (sees full context) | OK (semantic match) |
| Handles multi-turn ("and what about midcaps?") | Bad — keyword-empty | Good — sees history if included | Bad — same problem as regex |
| Build cost | ~30 LOC | ~40 LOC + prompt tuning | ~100 LOC + labeled examples |
| Maintenance | Add keywords as you discover misses | Tweak system prompt | Re-embed example set when labels shift |
| Debuggability | Trivial (which regex matched) | Medium (log Haiku response) | Hard (vector similarity is opaque) |

## Tradeoffs

- **A. Regex** — fast, free, brittle. The known failure modes are: (a) followups with no keywords ("and what about midcaps?"), (b) novel phrasings, (c) the user's natural mix of Hindi/English transliterations. For a single-user app where the user can self-correct by explicitly picking a model from the picker, the brittleness is tolerable.
- **B. Haiku classifier** — 150–300ms is noticeable. Every single turn pays this latency tax. The accuracy bump is meaningful, but the user notices the lag. Worse: if the classifier itself fails or is slow, the whole turn is delayed. The cost is trivial ($0.20 per 1000 turns) — latency is the real concern.
- **C. Embeddings** — middle ground on latency and cost but doesn't solve the multi-turn problem (which is the biggest pain point of regex). Same blindness to context.

## Recommendation

**A. Regex + previous-model inheritance, with B. as a deferred upgrade.**

Specifically:
1. Start with regex. Add an inheritance rule: if the previous turn in the session used model X, this turn uses X *unless* the regex strongly matches a different intent class (e.g., a clear "buy/sell" verb).
2. Surface the resolved model in the SSE meta frame so the user can see what the router picked. Add a "wrong model?" feedback button later.
3. Reconsider B when both of these are true: (a) regex misses are common enough to annoy the user, AND (b) latency is no longer the binding constraint (i.e., users tolerate 2.5s first-token vs 2.2s).

Rationale:
- Latency matters more than perfect routing accuracy for a personal-use app. A wrong model still gives a usable answer; a slow first token feels broken.
- The inheritance rule solves the single biggest regex weakness (multi-turn) with ~5 lines of code.
- The escape hatch (manual model picker) is already in the UI.

## Open questions

- Should inheritance decay (e.g., reset to auto-routing after 5 turns) or persist for the entire session?
- For the `claude-deep` (Opus) slug from [02](02-claude-model-routing.md), should it auto-revert to Sonnet after one turn, or stick until the user changes it?
- If we ever do B, can we run the Haiku classifier in parallel with the *main* call by speculatively starting both Haiku and Sonnet, then dropping the loser? Costs ~1.3× per turn but eliminates added latency. Probably too clever for now.
