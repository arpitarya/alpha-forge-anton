# 02 — Claude Model Routing

## Recommended vs Chosen

| | Choice | Cost |
|---|---|---|
| **Recommended** | Three-tier Claude (Haiku / Sonnet / Opus) via Anthropic direct API | Paid |
| **Chosen** | **Existing `alphaforge_anton_llm.gateway` with free providers (Gemini / Groq / Cerebras) for v1.** Anthropic direct API added as an *extension* when the project is ready to pay. The intent-routing logic (factoid → fast model, investment → strong model) still applies, but maps to free-tier slugs instead of Claude. |
| **Future extension** | Add a `claude-sdk` slug that bypasses the gateway and uses `anthropic.AsyncAnthropic` directly with Sonnet/Haiku — exactly as the original plan describes. The plumbing for this stays in the design but is gated behind opt-in until paid use is acceptable. |

**Intent → model mapping under the chosen path** (replaces the Claude-only table further down):

| Intent | Free-tier model (v1) | Future Anthropic mapping |
|---|---|---|
| Factoid / news lookup | Groq `llama-3.3-70b` *or* Cerebras `llama-3.3-70b` (fastest free) | `claude-haiku-4-5-20251001` |
| Portfolio / investment / multi-turn | Gemini `gemini-2.0-flash` (best free reasoning + 1M ctx) | `claude-sonnet-4-6` |
| Deep research (explicit pick) | Gemini `gemini-2.5-pro` (free tier limits apply) | `claude-opus-4-7` |

**Why the deviation**: zero paid services for v1. Free-tier LLMs are good enough to ship the concierge end-to-end; Anthropic becomes a quality upgrade once the rest of the system is proven.

---

## Context

Orff routes each turn to one of three Claude models based on intent. The existing plan ([1-concierge-plan.md](../1-concierge-plan.md)) hard-codes `claude-sonnet-4-6` for investment/portfolio intents and `claude-haiku-4-5-20251001` for factoid/news intents. This doc validates that split and asks whether Opus has a role.

## Options

| Model | Input $/MTok | Output $/MTok | Speed (tok/s) | Reasoning | Context | Best for |
|---|---|---|---|---|---|---|
| **claude-haiku-4-5-20251001** | $1.00 | $5.00 | ~120 | Strong | 200k | Factoid lookup, news summary, intent classification |
| **claude-sonnet-4-6** | $3.00 | $15.00 | ~80 | Excellent | 200k | Investment reasoning, portfolio analysis, multi-step |
| **claude-opus-4-7** | $15.00 | $75.00 | ~50 | Best-in-class | 200k | Rare: deep portfolio rebalancing, scenario planning |

(Prices are per-million-token list, rounded; check Anthropic pricing page for exact.)

## Intent → model matrix

| Intent | Example user msg | Model | Why |
|---|---|---|---|
| Factoid | "What's HDFC Bank's market cap?" | Haiku | One-shot lookup, no reasoning |
| News lookup | "What happened with Adani today?" | Haiku | Summarize fetched news; no analysis |
| Portfolio overview | "Show my AI exposure" | Sonnet | Needs to interpret holdings + sector tags |
| Investment plan | "Should I rebalance?" | Sonnet | Multi-step reasoning across holdings + news + macro |
| Scenario / what-if | "What if RBI hikes 50bps?" | Sonnet | Same — Sonnet handles this fine |
| Deep research | "Build me a thesis on Indian renewables for 2026" | Opus | Multi-source synthesis, novel argument |
| Multi-turn followup | "And what about midcaps?" | Inherit from previous turn | Avoid demoting mid-conversation |

## Tradeoffs

- **All-Haiku** — cheapest, fastest. Falls apart on portfolio reasoning where Sonnet's multi-step planning matters. Tried in early prototypes of similar products; users complained answers were "shallow."
- **All-Sonnet** — uniform quality, no routing logic to maintain. 3× the input cost and 3× the output cost of Haiku. For factoid queries this is pure waste.
- **Haiku + Sonnet split** (plan's current design) — best $/quality balance. Routing overhead is ~10 lines of regex/heuristic.
- **Add Opus tier** — Opus is 5× Sonnet's price and ~40% slower. For a single-user app the volume that *needs* Opus quality is tiny (maybe weekly "deep research" sessions). Worth exposing as an explicit model picker option rather than auto-routing.
- **Followup inheritance** — important UX detail: if turn 1 routed to Sonnet, turn 2 ("and what about midcaps?") should stay on Sonnet even if its surface text looks factoid. Otherwise quality drops mid-conversation.

## Recommendation

**Three-tier with auto-routing to Haiku/Sonnet, Opus as explicit-pick only.**

- `auto` slug → Haiku for factoid/news, Sonnet for everything else
- `claude-sdk` slug → Sonnet (current default)
- New `claude-deep` slug → Opus, surfaced in ModelPicker for explicit deep-research use
- Followup turns inherit the previous turn's model unless the user changes the picker

Rationale:
- Cost-optimized: ~70% of turns go to Haiku at 1/3 price.
- Quality-preserved: investment reasoning stays on Sonnet.
- User control: Opus exists for when the user explicitly wants it, no surprise billing.

## Open questions

- Should the router be regex (current plan) or a Haiku classifier call ([07](07-intent-classification.md))? Adding an LLM classifier adds 100–200ms of latency to every turn.
- Inheritance window: stick on same model for the full session, or only for the next N turns?
- Should "investment plan" intent ever upgrade to Opus automatically when the prompt mentions specific large amounts (e.g., "rebalance ₹50L")?
