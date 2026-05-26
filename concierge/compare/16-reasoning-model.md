# 16 — Reasoning Model Tier

## Recommended vs Chosen

| | Choice | Cost |
|---|---|---|
| **Recommended** | Add a `reasoning` model slug routed to a free reasoning-tier model (DeepSeek R1 via Groq/Cerebras or Gemini 2.5 Flash Thinking) | Free |
| **Chosen** | **DeepSeek R1 (distilled) via Groq as primary `reasoning` slug; Gemini 2.5 Flash Thinking as fallback.** Auto-routed for investment_plan / multi-step / what-if intents. Reasoning trace exposed in typed streaming events. | Free |

---

## Context

The fast/general/deep three-tier in [02](02-claude-model-routing.md) maps to chat-style models. State-of-the-art in 2026 includes a fourth tier: **reasoning models** that produce explicit thought traces before answers. For multi-step portfolio reasoning ("should I rebalance? consider tax, sector weights, my intent doc, current news"), they materially outperform same-size chat models.

Until 2024 reasoning models were paid (OpenAI o-series). In 2025–2026 the free landscape opened up dramatically.

## Options

| Model | Provider w/ free tier | Speed | Context | Reasoning trace exposed |
|---|---|---|---|---|
| **DeepSeek R1** | Groq, Cerebras, Together, OpenRouter | Fast (~200+ tok/s on Groq) | 128k | Yes (`<think>...</think>` content) |
| **DeepSeek R1 distill (Llama 70B)** | Groq (~500 tok/s), Cerebras (~2000 tok/s) | Very fast | 128k | Yes |
| **Gemini 2.5 Flash Thinking** | Google AI Studio free tier | Medium | 1M | Yes (separate `thoughts` field) |
| **Qwen 3 reasoning (QwQ-32B class)** | HuggingFace, Ollama, Groq | Medium | 32k–128k | Yes |
| **Llama 4 Reasoning** (if released by Meta) | Groq, OpenRouter | Fast | 128k+ | Yes |

## Tradeoffs

- **DeepSeek R1 (full)** — strongest open reasoning model. Quality competitive with OpenAI o1. Free via OpenRouter; reliable via Groq/Cerebras. Default pick.
- **DeepSeek R1 distill (Llama 70B)** — 90% of full R1 quality at 10× the speed via Groq/Cerebras. For real-time chat UX, this is usually the better tradeoff.
- **Gemini 2.5 Flash Thinking** — Google's free tier is generous (millions of tokens/day). 1M context lets it consume the full prompt (intent doc + memory + holdings + news + history) without truncation. Good vision + tool-use story too.
- **Qwen 3 reasoning** — strong, multilingual (helpful for Hindi/English code-switched queries). Best run via local Ollama for offline mode.
- **Llama 4 Reasoning** — if/when released, likely the dominant free reasoning model. Plug-and-play through Groq.

## When to route here vs the workhorse

Reasoning models are slower and costlier-in-tokens than chat models (the thinking trace alone is often 1–3k tokens). Use them when reasoning quality matters, not for every turn.

| Intent | Model |
|---|---|
| Factoid lookup | Groq Llama 3.3 (fast) |
| News summary | Groq Llama 3.3 (fast) |
| Portfolio overview | Gemini 2.0 Flash (general) |
| Investment plan / rebalance / what-if | **DeepSeek R1 distill (reasoning)** |
| Deep research (explicit) | **Full DeepSeek R1** (reasoning) |
| Code / math in response | DeepSeek R1 |

## Reasoning trace handling

DeepSeek R1's output is a mix of `<think>` content and final answer. Two routes:

1. **Hide thinking** — strip `<think>...</think>` before streaming to user; expose only final answer.
2. **Show thinking** — stream as a typed event (see [24](24-streaming-protocol.md)) so the frontend renders a collapsible "Orff is thinking..." block above the answer.

**Choice**: option 2. Showing the trace is a SOTA UX expectation in 2026 and helps the user trust the answer. Default to collapsed; expand on click.

## Verifier interaction

Reasoning models hallucinate less than chat models but still confabulate against private data (holdings, intent doc). Pair with a verifier pass ([25](25-verifier-pass.md)) that checks claims against the actual snapshot.

## Migration from current `auto` routing

Current `auto` routing in [02](02-claude-model-routing.md#recommended-vs-chosen): factoid/news → Groq fast; portfolio/investment → Gemini Flash general. Add:

```
investment_plan / what_if / deep_research / multi_step
   → reasoning slug → DeepSeek R1 distill (Groq) [primary]
                    → Gemini 2.5 Flash Thinking [fallback if Groq down]
                    → DeepSeek R1 full via OpenRouter [explicit deep pick]
```

## Open questions

- **Reasoning length cap**: R1 can spend 30+ seconds thinking. Cap at ~15s or ~3k thinking tokens for chat-style UX; expose a "deep think" toggle for unlimited.
- **Provider failover order**: Groq's free quotas are aggressive but generous; Cerebras has lower quotas but faster speed. Default Groq → Cerebras → OpenRouter.
- **Caching the reasoning trace**: cached so re-asking the same question returns instantly? Probably not worth the complexity in v1.
- **Trace visibility per intent**: always show, or only for certain intents (like `investment_plan`)? Default: always show, collapsed.
- **Calibration**: build a 50-query eval set of Indian-portfolio questions and measure R1 distill vs Gemini Thinking vs full R1 vs Llama 3.3 baseline. Pick the actual winner empirically, not by reputation.
