# 23 — Local LLM Fallback (Offline Mode)

## Recommended vs Chosen

| | Choice | Cost |
|---|---|---|
| **Recommended** | Ollama as a provider in the LLMGateway; auto-failover when cloud providers are down; explicit `offline` slug | Free (local compute) |
| **Chosen** | **Deferred — not in scope under current constraints.** Hardware (MacBook Air 16GB) is below the comfortable threshold for usable local models alongside Anton + browser + IDE, and the user has set a hard "no local models" rule. App is cloud-only; offline state is surfaced in UI; queued message auto-retries on reconnect. This doc is kept as reference for when the constraint relaxes (e.g., upgrade to 32GB+ or Mn Pro/Max with explicit opt-in). | n/a |

> **Why deferred, not removed**: the design here is sound and re-activatable. If the user later moves to a 32GB+ machine or chooses to allow one specific model, the only changes are: install Ollama, pull one model, set the env var that registers the provider. The LLMGateway adapter pattern keeps the integration point clean.

> **Offline-state UX (the actual v1 substitute)**: detect network failure → emit a typed `error` SSE event with `code: "offline"` → frontend preserves the draft message + shows an "offline" badge + listens for the browser `online` event → auto-retries when reconnected. No local model substitution.

---

## Context

State-of-the-art 2026 free LLMs (Llama 3.3, Qwen 3, DeepSeek R1 distill) run well on consumer hardware via Ollama. For Anton — a self-hosted, single-user app — local LLM gives:

- **Offline mode**: works without internet.
- **Privacy escape hatch**: portfolio + intent doc never leave the machine.
- **No quota anxiety**: cloud free tiers have rate limits; local has none.
- **Latency floor**: no network round trip, predictable response times.

Tradeoff: local models trail the best cloud free-tier models in quality, and inference is slower without a GPU.

## Options

### A. Don't bother — cloud-only

Skip local entirely. Simpler. But the user is stuck when network is down, and there's no privacy-mode answer for sensitive queries.

### B. Ollama as one provider among many

Ollama joins Gemini/Groq/Cerebras in the LLMGateway. Picked per-turn based on slug or auto-failover.

### C. LM Studio / vLLM / TGI

Alternative local serving frameworks. More features (multi-user, batch) but heavier setup.

### D. Llama.cpp directly

Lowest level. Maximum control. Maximum setup pain.

## Models worth running locally (2026)

| Model | RAM (Q4) | VRAM (GPU) | Quality vs cloud-free | Notes |
|---|---|---|---|---|
| **Llama 3.3 70B** | ~40GB | ~40GB | Comparable to Groq Llama 3.3 70B (same model) | Heavy; needs M-series Max or 48GB+ Mac |
| **Llama 3.3 8B / Llama 3.1 8B** | ~6GB | ~6GB | Good (better than gpt-3.5 era) | Runs on any modern laptop |
| **Qwen 3 14B** | ~10GB | ~10GB | Strong (multilingual; Hindi-capable) | Sweet spot for Apple Silicon Mn (non-Max) |
| **DeepSeek R1 distill (Llama 8B)** | ~6GB | ~6GB | Best small-model reasoning | Local reasoning model |
| **DeepSeek R1 distill (Llama 70B)** | ~40GB | ~40GB | Excellent reasoning | Needs Max-class hardware |
| **Qwen 3 32B** | ~22GB | ~22GB | Excellent general | M-series Pro/Max territory |
| **Phi-4** | ~10GB | ~10GB | Very strong small-model general | Microsoft's open model |
| **Llama 3.2 Vision 11B** | ~9GB | ~9GB | OK vision; quality below Gemini Flash | For offline vision |

## Recommendation

**Ollama, registered as a provider in LLMGateway, with auto-failover and explicit `offline` slug.**

### Slug routing

| Slug | Behavior |
|---|---|
| `auto` (default) | Cloud-first per intent. If cloud unreachable → fall back to local (best installed model). |
| `gemini-flash` / `groq-llama` / `cerebras-llama` / `claude-sdk` | Explicit cloud. No local fallback. |
| `offline` | Force local Ollama. Never touches cloud. |
| `local-reasoning` | Force local DeepSeek R1 distill. |

### Default model selection at startup

Backend probes Ollama at startup, builds a `local_model_preferences` ordered list based on what's installed:

```python
PREFERENCES = [
    ("llama3.3:70b", "general"),
    ("qwen3:32b", "general"),
    ("qwen3:14b", "general"),
    ("phi4:14b", "general"),
    ("llama3.1:8b", "general"),
    ("deepseek-r1:70b", "reasoning"),
    ("deepseek-r1:8b", "reasoning"),
    ("llama3.2-vision:11b", "vision"),
]
# pick first available per category
```

### Failover logic

```python
async def stream(self, intent_class, messages, ...):
    primary = self._route_cloud(intent_class)
    try:
        async for chunk in primary.stream(messages, timeout=30):
            yield chunk
        return
    except (NetworkError, RateLimitError, ProviderDownError) as e:
        logger.warning("Cloud %s failed: %s — falling back to local", primary.name, e)
        local = self._route_local(intent_class)
        async for chunk in local.stream(messages):
            yield chunk
```

Critically: failover surfaces in the meta SSE frame as `provider: ollama (failover from gemini)` so the user knows the answer came from local.

### Privacy-mode UX

The frontend model picker exposes an `offline` option explicitly. When selected:

- Badge in the composer: "🔒 Local only"
- Tool calls that require network (e.g., `search_web`, `get_price` via yfinance) are disabled — the model can't fetch what doesn't have a local source.
- Holdings + intent doc + memory all work normally (all local).

## Installation

Ollama install is one curl + start:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b
ollama pull deepseek-r1:8b
ollama pull qwen3:14b
ollama serve  # background; default port 11434
```

Backend talks to `http://localhost:11434/api/chat` via the standard Ollama client lib.

### Model download UX

Backend exposes:

- `GET /api/v1/local-llm/installed` — list models Ollama has
- `POST /api/v1/local-llm/pull` — pull a model (streams progress)
- `DELETE /api/v1/local-llm/{model}` — delete

Frontend has an admin pane showing installed/available, disk usage, with one-click pull.

## Performance expectations (Apple M-series, no discrete GPU)

| Hardware | Best local model | Tokens/sec |
|---|---|---|
| M1 8GB | Llama 3.1 8B Q4 | ~25 |
| M1 16GB | Qwen 3 14B Q4 | ~15 |
| M2/M3 16GB | Qwen 3 14B Q4 | ~25 |
| M-series Pro 32GB | Qwen 3 32B Q4 | ~15 |
| M-series Max 64GB+ | Llama 3.3 70B Q4 | ~12 |

Cloud free providers (Groq especially) are ~10–20× faster than local. Offline mode is functional, not snappy.

## When NOT to use local

- **Tool-heavy turns** with `search_web` / `get_price` — these need network anyway, so going local on the LLM gains little.
- **Long context turns** (>32k tokens) — local model context limits are usually 128k for the modern ones, but inference slows down dramatically beyond ~16k tokens on CPU/Apple Silicon.
- **Time-sensitive UX** — cloud free is just faster. Use local for privacy or as failover, not for speed.

## Open questions

- **Recommended baseline**: ship docs with a recommended model per hardware tier? Probably yes — most users won't know to pull Qwen 3 14B specifically.
- **Auto-detect hardware**: query system specs at install, suggest the right model. Modest UX win.
- **Streaming tool calls on local**: Ollama supports tool calling on some models (Llama 3 + Qwen 3 reliably). Verify before promising.
- **Quantization tradeoffs**: Q4 is the default; Q5/Q6 give better quality at more disk/RAM. Expose as an advanced setting.
- **Model updates**: when a new Llama drops, how do we notify? Periodic check against Ollama's library? Defer.
- **Embeddings on local**: BGE-large via `sentence-transformers` is already the embedding choice ([10](10-embedding-model.md)); Ollama supports embeddings too (`nomic-embed-text`). Use either; document tradeoffs.
- **Power consumption / thermals**: local inference is heavy. Worth surfacing battery-aware behavior (don't auto-failover to local on battery; ask first).
