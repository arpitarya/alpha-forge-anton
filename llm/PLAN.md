# LLM Research Agent — Plan

Personal AI research layer for AlphaForge. Answers portfolio-aware investment questions using
free LLMs, real news feeds, and live market data. Claude (via Agent SDK) is the optional
escalation tier requiring explicit user confirmation.

Related plan: [backend/app/modules/news/PLAN.md](../backend/app/modules/news/PLAN.md)

## Goals

1. Research assistant for Indian markets — stock picks, investment plans, news, portfolio overview
2. Zero-cost by default: free provider tiers only; Claude only on user opt-in
3. User controls the model, or the system auto-selects and switches seamlessly
4. Voice and chat from day one (browser-native, no extra infra)
5. Evaluation question bank that benchmarks providers and feeds the router
6. **Any new LLM provider can be added in one file with no changes elsewhere**
7. **Each provider can be tested in complete isolation before being wired into the system**

## Non-goals

- SEBI-registered advice (every output carries the mandatory disclaimer)
- Real-time tick-level analysis (uses daily/hourly snapshots)
- Managing trades (read-only; Trade module handles that separately)

---

## Architecture

```
User (chat or voice)
        │
        ▼
[Frontend — ResearchPanel]
  ├── ChatComposer + ModelSelector (Auto | specific model)
  ├── VoiceController (Web Speech API — STT push-to-talk, TTS reply)
  └── EscalationConfirmModal (shown before any Claude SDK call)
        │  SSE  (POST /api/v1/research/chat)
        ▼
[Backend — research module]
  ├── QueryClassifier      ← zero-shot prompt (cheapest model): routes to QueryType
  ├── AgentLoop            ← tool-calling loop; streams chunks via SSE
  │     └── ToolRegistry   ← quote, holdings, screener, news, web_search, recall_memory
  ├── ResearchSession      ← ConversationMemory ORM; carries full context across model switches
  └── ResponseShaper       ← appends SEBI disclaimer, cites sources, formats INR
        │
        ▼
[LLM layer — llm/ workspace]
  ├── ModelSelector        ← "Auto" → QueryRouter; pinned → direct dispatch
  ├── QueryRouter          ← per-QueryType fallback chain (benchmark-ranked)
  ├── ProviderRegistry     ← name → ProviderAdapter; auto-populated at import
  ├── ProviderAdapter ABC  ← the contract every provider must implement (see below)
  │     ├── GeminiAdapter
  │     ├── GroqAdapter
  │     ├── OpenRouterAdapter
  │     ├── HuggingFaceAdapter
  │     ├── OllamaAdapter
  │     └── ClaudeSdkAdapter   (gated by CostGuard + confirmation)
  ├── CostGuard            ← raises CostGuardError on any paid model/tier
  ├── RateLimiter          ← per-provider token-bucket; auto-resets on window roll
  └── Handover             ← context bridge when model switches mid-session
```

---

## Provider Extensibility Contract

The core extensibility design. Every provider is a self-contained file implementing
`ProviderAdapter`. The registry is populated at import — no manual wiring needed anywhere
else in the system.

### ProviderAdapter ABC

```python
# llm/src/alphaforge_llm/providers/base.py

class ProviderAdapter(ABC):
    name: str                    # unique slug, e.g. "groq", "gemini-flash"
    supports_tool_calling: bool  # False for HuggingFace serverless
    supports_streaming: bool
    env_key: str                 # env var that enables this provider, e.g. "GROQ_API_KEY"

    @abstractmethod
    async def complete(
        self,
        messages: list[Message],
        tools: list[ToolSchema] | None = None,
        stream: bool = False,
    ) -> AsyncIterator[str] | ProviderResponse: ...

    @abstractmethod
    async def health(self) -> ProviderHealth: ...
    # Returns: available=bool, quota_remaining=int|None, last_error=str|None

    @classmethod
    @abstractmethod
    def default_model(cls) -> str: ...
```

### Adding a new provider — full checklist

1. Create `llm/src/alphaforge_llm/providers/<name>.py`
2. Implement `ProviderAdapter` — self-contained, ≤100 lines
3. Add one line to `providers/__init__.py`:
   ```python
   from .myname import MyNameAdapter
   REGISTRY["myname"] = MyNameAdapter
   ```
4. Add `MYNAME_API_KEY=` to `.env.example`
5. Add standalone tests: `llm/tests/providers/test_myname.py`
6. Add a notebook section in `llm/notebooks/llm_playground.py`

No changes to router, gateway, rate limiter, or agent loop.

### Tool-calling fallback for non-supporting providers

When `supports_tool_calling=False` (e.g. HuggingFace), `AgentLoop` falls back to
prompt-based tool extraction: system prompt includes JSON schema for each tool, and
the response is parsed for a `{"tool": ..., "args": ...}` block. Transparent to callers.
Tool-heavy QueryTypes are de-prioritised in the router for these providers.

### Standalone provider testing

Each test file requires only its own API key — no database, no FastAPI, no other modules.

```python
# llm/tests/providers/test_groq.py
@pytest.mark.asyncio
async def test_basic_completion():
    adapter = GroqAdapter()
    response = await adapter.complete([{"role": "user", "content": "Say hello"}])
    assert response.content

@pytest.mark.asyncio
async def test_tool_call():
    ...  # calls with a tool schema, asserts tool_call in response

@pytest.mark.asyncio
async def test_streaming():
    chunks = [c async for c in await adapter.complete([...], stream=True)]
    assert len(chunks) > 0

@pytest.mark.asyncio
async def test_health():
    h = await adapter.health()
    assert h.available
```

Run one provider in isolation: `uv run pytest llm/tests/providers/test_groq.py -v`

---

## Model Selection & Seamless Handover

### User-controlled selection

- Compact dropdown in the chat composer toolbar
- Options: `Auto` (default) | Gemini Flash | Gemini Pro | Groq Llama-3.3 | Groq Gemma2 |
  OpenRouter Auto | Ollama (local) | Claude (confirm required)
- Stored in session; persists via `localStorage`

### Auto-routing

- `QueryClassifier` categorises the message → `QueryType`
- `QueryRouter` picks the provider chain for that type
- If top choice is rate-limited or errors, next in chain takes over silently
- Model badge in the UI updates in real time ("Answered by Groq Llama-3.3")

### Seamless mid-session handover

- All turns stored in `ResearchSession` (PostgreSQL via `ConversationMemory` ORM)
- On model switch, `Handover` reconstructs the message list in the target provider's format;
  if the target has a smaller context window, it summarises older turns using the cheapest
  available model (never drops the last 8 raw turns)
- Non-blocking badge: "Switched to Gemini Flash — Groq rate-limited"
- Tool call results reattached correctly across the switch

---

## Query Types & Default Routing

| QueryType | Default chain | Strategy |
|---|---|---|
| `news_lookup` | Groq Llama-3.3 → Gemini Flash → OpenRouter | Single |
| `factoid` | Gemini Flash → Groq Gemma2 → OpenRouter | Single |
| `portfolio_overview` | Gemini Flash → Groq Llama-3.3 | Single |
| `stock_pick` | Gemini Flash ∥ Groq Llama-3.3 ∥ OpenRouter → Gemini Flash judge | **Ensemble** |
| `investment_plan` | Same ensemble → Claude SDK escalation hint offered | **Ensemble + hint** |
| `industry_news` | Tavily search → Groq summarise | Single + tool-heavy |
| `multi_turn` | Gemini Flash (long context) | Single |

Routing chains are overridable from `llm/eval/results/latest.json` — the benchmark runner
writes ranked results; `QueryRouter` reads this at startup and reloads on `SIGHUP`.

---

## SSE Event Schema

All events from `POST /api/v1/research/chat`:

```json
{ "event": "<type>", "data": { ... } }
```

| Event | Payload fields | Notes |
|---|---|---|
| `token` | `text: str` | Streamed content chunk |
| `tool_call_start` | `tool: str, args: dict, call_id: str` | Tool about to run |
| `tool_call_result` | `call_id: str, result: dict, duration_ms: int` | Tool finished |
| `model_switch` | `from: str, to: str, reason: str` | Handover fired |
| `escalation_hint` | `query_summary: str, est_tokens: int` | Offer Claude |
| `error` | `code: str, message: str, retryable: bool` | Provider or tool error |
| `done` | `provider: str, total_tokens: int, latency_ms: int` | Stream complete |

---

## Agent Tools

All tools are read-only. News access goes through the standalone `news` module.

| Tool | Source module | Notes |
|---|---|---|
| `get_quote(symbol)` | `market` | Real-time NSE/BSE quote |
| `get_holdings(broker=None)` | `portfolio` | Live cached holdings |
| `get_portfolio_summary()` | `dashboard` | P&L, wallet totals, day move |
| `get_screener_picks(sector=None)` | `screener` | ML picks + SHAP scores |
| `search_news(query, symbols, since)` | `news` (standalone module) | Aggregated, deduped |
| `search_web(query)` | `news` module (Tavily/Brave sources) | Non-news research |
| `get_ohlcv(symbol, days)` | `market` | Historical candles |
| `recall_memory(topic)` | `memory` | RAG over past screener + chats |

---

## Claude Agent SDK Escalation

Gated by two checks:

1. **Auto-hint** — after ensemble answer for `stock_pick` / `investment_plan`, UI offers
   "Get deeper analysis with Claude?" as a non-intrusive suggestion
2. **Direct request** — user picks "Claude" from model selector, or says "go deeper"

Confirmation modal: the query, estimated tokens, current free-tier answer.
On confirm: `ClaudeSdkAdapter` spawns a `claude` subprocess, streams stdout over SSE,
ledger persists the invocation (query, tokens, timestamp) for quota auditing.

---

## Evaluation Question Bank

`llm/eval/questions.yaml` — benchmarks providers and feeds routing chain ranking.

| Category | Initial Qs |
|---|---|
| `stock_pick` | 8 |
| `investment_plan` | 5 |
| `stock_news` | 6 |
| `industry_news` | 5 |
| `portfolio_overview` | 4 |
| `factoid` | 6 |
| `multi_turn` | 4 |
| `model_selection` | 3 (test "pick model X" + switch works correctly) |
| `edge_cases` | 4 (ambiguous ticker, date arithmetic, INR formatting, disclaimer check) |

Eval runner: runs all questions × all enabled providers; scores heuristically + LLM judge;
writes `results/latest.json` → `QueryRouter` reads for chain ranking.
When to run: manually after adding providers or questions; scheduled weekly.
CLI: `uv run python -m alphaforge_llm.eval.eval_runner`

---

## Testing Surfaces

### 1. Notebook Playground — Phase 1 (offline)

`llm/notebooks/llm_playground.py` (Jupytext `.py` ↔ `.ipynb`)

- Call each provider directly — validate API key + response shape
- Call via router — see which provider wins and why
- Side-by-side comparison across providers for the same query
- Rate limiter state: `gateway.health()`
- Cost guard: assert `ClaudeSdkAdapter` raises `CostGuardError` without confirmation
- Ensemble timing: mock 3 providers, measure judge latency
- News tool smoke: `await news_service.search("Reliance", since="-7d")`

### 2. Browser Playground — Phase 5 (dev-only, `APP_ENV=development`)

`frontend/src/app/dev/llm/page.tsx` — returns 403 in production.

- Raw SSE event stream viewer (every event with raw JSON)
- Model selector: test pinned + auto + mid-session switch
- Voice push-to-talk → transcript → send; TTS playback toggle
- Tool call inspector: collapsible cards with args + result
- Provider health panel: quota remaining, last-used timestamp
- Latency bar: time-to-first-token + total completion time

`llm-dev.stream.ts` is promoted to `research.stream.ts` in Phase 6 — write once, test
here, then promote.

---

## Dependency Direction

```
research  →  llm          (gateway.complete)
research  →  news         (NewsService via search_news tool)
research  →  market, portfolio, screener, memory  (other tools)
llm       →  (nothing in this repo — pure Python, no app imports)
news      →  (nothing in this repo — pure Python + HTTP clients)
```

`llm/` and `news/` are importable standalone. The backend modules import from them,
never the reverse. This is enforced in CI via `import-linter` rules.

---

## File Layout

```
llm/
├── PLAN.md
├── pyproject.toml
├── src/alphaforge_llm/
│   ├── __init__.py
│   ├── types.py                     # QueryType, ProviderResponse, EscalationRequest, Message
│   ├── cost_guard.py
│   ├── rate_limiter.py
│   ├── router.py
│   ├── handover.py
│   ├── gateway.py                   # LLMGateway: entry point (create_from_env)
│   └── providers/
│       ├── __init__.py              # REGISTRY dict + auto-registration on import
│       ├── base.py                  # ProviderAdapter ABC + ProviderHealth
│       ├── gemini.py
│       ├── groq.py
│       ├── openrouter.py
│       ├── huggingface.py
│       ├── ollama.py
│       └── claude_sdk.py
├── eval/
│   ├── questions.yaml
│   ├── eval_runner.py
│   ├── eval_judge.py
│   └── results/                     # gitignored
├── notebooks/
│   ├── llm_playground.py            # Jupytext source — commit this
│   └── llm_playground.ipynb         # generated — gitignored
└── tests/
    ├── test_router.py
    ├── test_cost_guard.py
    ├── test_handover.py
    └── providers/
        ├── test_gemini.py           # standalone — needs only GEMINI_API_KEY
        ├── test_groq.py
        ├── test_openrouter.py
        ├── test_huggingface.py
        ├── test_ollama.py
        └── test_claude_sdk.py
```

Backend integration (`backend/app/modules/`):

```
llm/
├── llm_service.py                   # singleton LLMGateway wrapper
└── llm_routes.py                    # GET /llm/providers, POST /llm/benchmark/run
news/                                # see news/PLAN.md
research/
├── agent_loop.py
├── agent_tools.py
├── agent_prompts.py
├── agent_session.py
├── research_routes.py
└── research_schemas.py
```

Frontend:

```
frontend/src/app/dev/llm/page.tsx
frontend/src/modules/llm-dev/
├── SseInspector.tsx
├── ProviderHealthPanel.tsx
├── DevChatComposer.tsx
└── llm-dev.stream.ts               # promoted → research.stream.ts in Phase 6
frontend/src/modules/research/
├── ResearchPanel.tsx
├── ModelSelector.tsx
├── ChatBubble.tsx
├── ToolCallCard.tsx
├── SourceCitations.tsx
├── EscalationConfirmModal.tsx
├── VoiceController.ts
├── HandoverBadge.tsx
├── research.api.ts
├── research.query.ts
├── research.stream.ts
└── research.types.ts
```

---

## Environment Variables (add to `.env.example`)

```
GEMINI_API_KEY=
GROQ_API_KEY=
OPENROUTER_API_KEY=
HF_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434

ALLOW_CLOUD_LLM_IN_DEV=false
RESEARCH_ENABLE_ENSEMBLE=true
RESEARCH_ENSEMBLE_TIMEOUT_S=15
RESEARCH_CLAUDE_ESCALATION=true
LLM_DEV_PLAYGROUND=true             # auto-true when APP_ENV=development
```

---

## Implementation Phases

| Phase | Deliverable | Notes |
|---|---|---|
| 1 | `llm/` workspace: ABC, registry, types, cost_guard, rate_limiter, router, 5 adapters + notebook | Validate each adapter standalone in notebook before wiring backend |
| 2 | `backend/app/modules/news/` | See news/PLAN.md; validate each source standalone first |
| 3 | `llm/eval/` — questions.yaml (45 Qs), runner, judge | CLI only |
| 4 | Backend `research/` — agent loop, tool registry, SSE routes | ConversationMemory reuse |
| 5 | Handover + ClaudeSdkAdapter + `/dev/llm` playground | Test SSE, voice, model switch end-to-end |
| 6 | Frontend `research/` — ResearchPanel, ModelSelector, VoiceController | Promote stream.ts; chat + voice |
| 7 | Wire into terminal home + Alpha AI preferences | Replace old AIChat slot |
| 8 | Run eval, update router chains | Benchmark → routing improvement loop |

---

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Web Speech API is Chrome/Edge only | Document; type input always works |
| Claude SDK subprocess needs `~/.claude/` | 5-min headless invocation spike before Phase 5 |
| Ensemble latency too high | `RESEARCH_ENSEMBLE_TIMEOUT_S` returns fastest N if judge stalls |
| Context window overflow | Handover summarises turns older than 8; configurable |
| HuggingFace no tool calling | Prompt-based extraction fallback in AgentLoop |
