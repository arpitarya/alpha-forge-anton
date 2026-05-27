# LLM Providers & Model Registry

Consolidated reference for every inference provider and model wired into `alphaforge_anton_llm.gateway`.
For decision rationale see [compare/02-claude-model-routing.md](compare/02-claude-model-routing.md) and [compare/16-reasoning-model.md](compare/16-reasoning-model.md).

---

## Provider Registry

| Slug | Adapter | Env key | Model (current) | Free tier | Notes |
|---|---|---|---|---|---|
| `gemini` | `GeminiAdapter` | `GEMINI_API_KEY` | `gemini-flash-latest` | Yes — Google AI Studio | Vision + PDF native; 1M ctx |
| `groq` | `GroqAdapter` | `GROQ_API_KEY` | `llama-3.3-70b-versatile` | Yes | ~200 tok/s; fastest free text |
| `cerebras` | `CerebrasAdapter` | `CEREBRAS_API_KEY` | `llama3.1-8b` | Yes | ~2000 tok/s; very low latency |
| `mistral` | `MistralAdapter` | `MISTRAL_API_KEY` | `mistral-small-latest` | Yes (limited) | Structured output + JSON mode |
| `openrouter` | `OpenRouterAdapter` | `OPENROUTER_API_KEY` | `google/gemma-4-26b-a4b-it:free` | Yes — :free models only | DeepSeek R1 full via this route |
| `huggingface` | `HuggingFaceAdapter` | `HF_API_KEY` | `mistralai/Mistral-7B-Instruct-v0.3` | Yes (Inference API) | Fallback / experimental |
| `claude-sdk` | `ClaudeSdkAdapter` | `ANTHROPIC_API_KEY` | `claude-sonnet-4-6` | **No — paid** | Gated by CostGuard + confirmation |

---

## Intent → Provider Routing

Defined in `router.py`. First available provider in the chain wins; next takes over on failure.

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

## Future / Paid Tier (Anthropic)

Not active. Gated behind `claude-sdk` slug + `CostGuard` confirmation. Swap-in when paid usage is acceptable.

| Intent | Planned model |
|---|---|
| Factoid / news | `claude-haiku-4-5-20251001` |
| Portfolio / investment | `claude-sonnet-4-6` |
| Deep research (explicit) | `claude-opus-4-7` |

---

## Web Search Providers

Not part of the LLM registry but used by the planned web grounding tool ([21](compare/21-web-search-grounding.md)).

| Provider | Cost | Activation |
|---|---|---|
| DuckDuckGo HTML search | Free | Default |
| Brave Search free tier | Free | Set `BRAVE_SEARCH_API_KEY` env var |
