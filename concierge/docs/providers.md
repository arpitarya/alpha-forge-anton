# LLM Providers & Model Registry

Consolidated reference for every inference provider and model wired into `alphaforge_anton_llm.gateway`.
For decision rationale see [compare/02-claude-model-routing.md](compare/02-claude-model-routing.md) and [compare/16-reasoning-model.md](compare/16-reasoning-model.md).

> **Single source of truth:** the provider/model registry, intent routing, and
> default-model policy are authored in the manifest
> [`src/alphaforge_anton_llm/registry/providers.json`](../llm/src/alphaforge_anton_llm/registry/providers.json)
> + [`routing.json`](../llm/src/alphaforge_anton_llm/registry/routing.json). Python reads
> it via `registry.py`; the frontend regenerates `concierge.registry.generated.ts`
> with `pnpm gen:concierge`. **Edit the manifest, not this doc or any `.ts`/`.py`.**
> The tables below are a human-readable view of that manifest. See the consolidation
> plan ([6](6-registry-consolidation-plan.md)) and Fux rule `concierge-registry-single-source`.

---

## Provider Registry

The **default model** is the first entry in each provider's `models` list in `providers.json`.
Adapters no longer hardcode a model — `default_model()` reads the manifest — so adding a model (or
making a new one the default by reordering) is a one-file edit.

| Slug | Adapter | Env key | Default model | Free tier | Notes |
|---|---|---|---|---|---|
| `gemini` | `GeminiAdapter` | `GEMINI_API_KEY` | `gemini-flash-latest` | Yes — Google AI Studio | Vision + PDF native; 1M ctx |
| `groq` | `GroqAdapter` | `GROQ_API_KEY` | `llama-3.3-70b-versatile` | Yes | ~200 tok/s; fastest free text |
| `cerebras` | `CerebrasAdapter` | `CEREBRAS_API_KEY` | `llama3.1-8b` | Yes | ~2000 tok/s; very low latency |
| `mistral` | `MistralAdapter` | `MISTRAL_API_KEY` | `mistral-small-latest` | Yes (limited) | Structured output + JSON mode |
| `openrouter` | `OpenRouterAdapter` | `OPENROUTER_API_KEY` | `google/gemma-4-26b-a4b-it:free` | Yes — :free models only | DeepSeek R1 full via this route |
| `huggingface` | `HuggingFaceAdapter` | `HF_API_KEY` | `mistralai/Mistral-7B-Instruct-v0.3` | Yes (Inference API) | Fallback / experimental |
| `claude-sdk` | `ClaudeSdkAdapter` | `ANTHROPIC_API_KEY` | `claude-sonnet-4-6` | **No — paid** | Also offers `claude-opus-4-8`, `claude-haiku-4-5-20251001`; all gated by CostGuard + confirmation |

The frontend does **not** maintain this registry by hand — it is generated from the manifest into
[frontend/src/modules/concierge/concierge.registry.generated.ts](../../frontend/src/modules/concierge/concierge.registry.generated.ts)
(re-exported by `concierge.providers.ts`). The two-pane ModelPicker (providers × models) consumes it;
selecting a model sends `{ provider, model_id, auto_level }` to `POST /api/v1/concierge`. The pinned
`model_id` is **honoured end-to-end** — the gateway forwards it to the adapter, so the model shown is
the model that runs — except when the privacy floor or Auto overrides the provider, which drops it.

### Per-model consumption

Every model carries a `consumption` block in `providers.json` — `input_per_m`, `output_per_m`
(USD per 1M tokens), `max_tokens` (the output cap the adapter sends), and `paid`. This is the
single place to **see and configure** what a model costs:

- `pricing.is_paid(provider, model)` is what `CostGuard` gates on — no hardcoded paid-provider list.
- `pricing.max_tokens(provider, model)` is the output cap every adapter applies.
- `pricing.estimate_cost_usd(provider, model, prompt, completion)` turns a response's token counts
  into real spend (e.g. Opus 1000 in + 500 out = $0.0525).

To add/reprice a model, edit its `consumption` block; run `pnpm gen:concierge` then `just test-backend`.

### Streaming support

| Provider | `astream()` (token-by-token SSE) |
|---|---|
| `groq` / `cerebras` / `openrouter` / `mistral` | ✅ via shared `_openai_stream.openai_stream` |
| `gemini` / `huggingface` / `claude-sdk` | ⏳ one-shot — `Gateway.stream()` yields a single snapshot |

`POST /api/v1/chat` always returns an SSE stream: progressively-growing `content` for streaming
providers, a single `[DONE]`-terminated event for the rest. The frontend `useChatStream` handles
both uniformly — each event overwrites `turn.response`.

### Voice (browser-only)

`useVoice` ([frontend/src/modules/chat/useVoice.ts](../frontend/src/modules/chat/useVoice.ts))
wraps the Web Speech API: `SpeechRecognition` for STT (`en-IN`) and `speechSynthesis` for TTS.
The `VoiceCenter` component in the bottom bar shows the mic button + live transcript and submits
the final transcript through the same `POST /api/v1/chat` path. No paid voice services involved.

---

## Intent → Provider Routing

Authored in [`routing.json`](../llm/src/alphaforge_anton_llm/registry/routing.json) (`intents`
text→`QueryType`, `chains` `QueryType`→providers); `router.py` and the backend classifier read it
via `registry.py`. First available provider in the chain wins; next takes over on failure.

| Intent (`QueryType`) | Primary chain | Typical model used |
|---|---|---|
| `factoid` | cerebras → gemini → groq → openrouter | Cerebras llama3.1-8b |
| `news_lookup` | cerebras → groq → gemini → openrouter | Cerebras llama3.1-8b |
| `industry_news` | groq → gemini → openrouter | Groq llama-3.3-70b |
| `portfolio_overview` | gemini → groq | Gemini Flash |
| `multi_turn` | gemini → groq | Gemini Flash |
| `stock_pick` | deepseek¹ → gemini → groq | Gemini Flash (until deepseek added) |
| `investment_plan` | deepseek¹ → mistral → gemini | Mistral Small (until deepseek added) |

¹ `deepseek` slug is planned — not yet in the registry. Falls through to next in chain today.

---

## Three-Tier Model Routing

| Tier | Slug | Provider | Model | Use when |
|---|---|---|---|---|
| Fast | `groq` / `cerebras` | Groq / Cerebras | llama-3.3-70b / llama3.1-8b | Factoid, news lookup, short summaries |
| General | `gemini` | Google AI Studio | gemini-flash-latest | Portfolio overview, multi-turn, structured Q&A |
| Deep research | `gemini` | Google AI Studio | gemini-2.5-pro (free limits) | Explicit deep research; long-form synthesis |
| Reasoning | `deepseek` (planned) | Groq (R1 distill) / OpenRouter (R1 full) | DeepSeek R1 distill 70B / R1 full | Investment plan, rebalance, what-if, multi-step |

Fallback order for reasoning until `deepseek` slug is live:
`Groq R1 distill → Gemini 2.5 Flash Thinking → DeepSeek R1 full via OpenRouter`

---

## Vision & Multimodal

| Use case | Primary | Failover | Notes |
|---|---|---|---|
| Image attachments (PNG/JPG) | `gemini` (`gemini-2.0-flash`) | Groq `llama-3.2-vision` | Both cloud-only |
| PDF ≤ 20 pages | `gemini` (native PDF) | — | Preserves layout |
| PDF > 20 pages | `pypdf` local extract → any text model | — | No ML, pure-Python |
| Both providers down | Hard error | — | Frontend prompts user to describe in text |

---

## Paid Tier (Anthropic)

All three Claude models are registered under the `claude-sdk` slug and gated behind `CostGuard`
confirmation (`consumption.paid: true`). They appear in the ModelPicker and run when pinned + confirmed.

| Model | Intent fit | Pricing (in/out per 1M) |
|---|---|---|
| `claude-haiku-4-5-20251001` | Factoid / news — fast, cheapest | $1 / $5 |
| `claude-sonnet-4-6` | Portfolio / investment — **default** | $3 / $15 |
| `claude-opus-4-8` | Deep research — deepest, priciest | $15 / $75 |

---

## Web Search Providers

Not part of the LLM registry but used by the planned web grounding tool ([21](compare/21-web-search-grounding.md)).

| Provider | Cost | Activation |
|---|---|---|
| DuckDuckGo HTML search | Free | Default |
| Brave Search free tier | Free | Set `BRAVE_SEARCH_API_KEY` env var |
