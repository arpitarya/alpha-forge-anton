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
8. **Full token usage tracking — summary and per-call detail — visible in the AlphaForge UI**
9. **All LLM management (provider keys, usage, health) accessible from the app — no terminal needed**

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

## Token Cost Tracking

Every LLM call is recorded in a `LlmCallLedger` table. The UI exposes both a summary
(monthly totals at a glance) and a full per-call detail view.

### LlmCallLedger ORM

```python
class LlmCallLedger(Base):
    id: uuid
    session_id: str | None       # ResearchSession FK (null for eval runner calls)
    provider: str                # "groq", "gemini-flash", "claude-sdk"
    model: str                   # exact model name used
    query_type: str              # QueryType slug
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int            # prompt + completion
    latency_ms: int
    is_paid: bool                # True only for ClaudeSdkAdapter
    cost_usd: Decimal            # $0.00 for all free providers; real cost for Claude
    created_at: datetime
```

Cost calculation:
- All free providers (Gemini, Groq, OpenRouter free, HuggingFace, Ollama): `cost_usd = 0.00`
- Claude SDK: `cost_usd = (prompt_tokens / 1M) * input_rate + (completion_tokens / 1M) * output_rate`
  Rates stored in `llm_service.py` as constants; updated when Anthropic changes pricing.

### Summary view (Preferences → Alpha AI → Usage)

| Metric | Grouping |
|---|---|
| Total tokens | This session / today / this month |
| Tokens by provider | Bar chart per provider |
| Tokens by query type | Bar chart per QueryType |
| Claude invocations | Count + total cost this month |
| Estimated total cost | Always shown; $0.00 for pure free-tier usage |
| Avg latency per provider | ms; helps identify slow providers |

### Detail view (Preferences → Alpha AI → Usage → "View all")

Paginated ledger table: timestamp · provider · model · query type · prompt tokens ·
completion tokens · cost · session link (opens that session in the research panel).
Filterable by date range, provider, query type.
Exportable as CSV for personal auditing.

### API routes

```
GET  /api/v1/llm/usage/summary
     ?period=today|week|month|all
     → UsageSummary { total_tokens, by_provider, by_query_type, total_cost_usd, claude_calls }

GET  /api/v1/llm/usage/ledger
     ?page=1&limit=50&provider=groq&since=2026-05-01
     → Page[LlmCallRecord]

GET  /api/v1/llm/usage/export
     ?since=2026-05-01&until=2026-05-31
     → CSV download
```

---

## API Key Management via Settings

Provider API keys are manageable from Preferences → Alpha AI — no terminal or `.env`
editing needed after initial setup. Keys are stored encrypted at rest (Fernet, same
mechanism already used for broker tokens).

### LlmProviderSettings ORM

```python
class LlmProviderSettings(Base):
    provider: str           # primary key — "gemini", "groq", "openrouter", etc.
    encrypted_key: bytes    # Fernet-encrypted API key
    last_tested_at: datetime | None
    test_status: str        # "ok" | "invalid" | "untested"
    updated_at: datetime
```

### Key resolution order (at gateway startup)

1. `LlmProviderSettings` table (if row exists and key is non-empty)
2. Environment variable (`.env` fallback)
3. Provider is skipped (not registered as available)

This means `.env` keys still work during development; UI-saved keys take precedence
in production without requiring a server restart.

### API routes

```
GET  /api/v1/llm/settings
     → List[ProviderKeyStatus]
     # { provider, has_key, masked_key (last 4 chars), test_status, last_tested_at }
     # Never returns the raw key

PUT  /api/v1/llm/settings/{provider}
     body: { api_key: str }
     → ProviderKeyStatus
     # Encrypts, saves, then immediately calls provider.health() to validate
     # Sets test_status and last_tested_at before responding

POST /api/v1/llm/settings/{provider}/test
     → ProviderKeyStatus
     # Re-runs health check against the stored key without changing anything

DELETE /api/v1/llm/settings/{provider}
     → 204
     # Removes stored key; gateway falls back to env var
```

### Frontend — Preferences → Alpha AI → Provider Keys

One row per registered provider:

```
[ Groq ]  ••••••••••••3f8a  [Test]  ✓ Working — last tested 2 min ago  [Edit]  [Remove]
[ Gemini ] ••••••••••••91bc  [Test]  ✓ Working — last tested 1 hr ago   [Edit]  [Remove]
[ Ollama ] http://localhost:11434      ✓ Local — always available               [Edit]
[ Claude ] Not configured             — Confirm required each use        [Add key]
```

- "Edit" opens an inline input (masked, paste-friendly)
- "Test" fires `POST /llm/settings/{provider}/test` and updates the status badge inline
- Saving a new key fires `PUT /llm/settings/{provider}` — validation happens server-side
- News source keys follow the same pattern in Preferences → Alpha AI → News Sources

---

## AlphaForge UI Surfaces

All LLM-related management is accessible from within the app.
No terminal commands needed for day-to-day use after initial setup.

| Surface | Location | What it shows |
|---|---|---|
| Research chat + voice | Terminal home (primary panel) or `/research` | The main agent interface |
| Model selector | Chat composer toolbar | Auto / pinned model dropdown |
| Provider keys | Preferences → Alpha AI → Provider Keys | Add, test, remove API keys |
| News source keys | Preferences → Alpha AI → News Sources | Same pattern as provider keys |
| Token usage summary | Preferences → Alpha AI → Usage | Monthly totals, by provider, cost |
| Token usage detail | Preferences → Alpha AI → Usage → "View all" | Full ledger, filterable, CSV export |
| Provider health | Preferences → Alpha AI → Provider Health | Quota remaining, last-used, status |
| Dev playground | `/dev/llm` (dev-only) | Raw SSE inspector, voice test, all providers |
| Eval results | `/dev/llm/eval` (dev-only) | Benchmark scores per provider/query-type |

The Alpha AI preferences section (`AlphaSection.tsx`) grows to cover all of the above.
Existing preferences (voice wake, reply style, confidence floor, auto-rebalance, screener
visibility) stay; the new subsections are added below them.

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
├── llm_routes.py                    # GET /llm/providers, POST /llm/benchmark/run
├── llm_settings_service.py          # LlmProviderSettings ORM + key resolution
├── llm_settings_routes.py           # GET/PUT/POST/DELETE /llm/settings/{provider}
├── llm_ledger_models.py             # LlmCallLedger ORM
├── llm_ledger_service.py            # write call records, query summaries
└── llm_usage_routes.py              # GET /llm/usage/summary|ledger|export
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
frontend/src/modules/preferences/
├── AlphaSection.tsx                 # extended with Provider Keys, News Sources, Usage subsections
├── ProviderKeysPanel.tsx            # per-provider key row: masked input + Test + status badge
├── NewsSourcesPanel.tsx             # same pattern for news source API keys
├── UsageSummaryPanel.tsx            # monthly totals, by-provider bar chart, cost
└── UsageLedgerDrawer.tsx            # paginated detail table + CSV export
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

# Token ledger
LLM_LEDGER_ENABLED=true             # set false to disable DB writes (e.g. high-volume eval runs)

# Key storage encryption (reuses existing FERNET_KEY from broker token setup)
# FERNET_KEY is already defined in backend/.env.example
```

---

## Implementation Phases

| Phase | Deliverable | Notes |
|---|---|---|
| 1 | `llm/` workspace: ABC, registry, types, cost_guard, rate_limiter, router, 5 adapters + notebook | Validate each adapter standalone in notebook before wiring backend |
| 2 | `backend/app/modules/news/` | See news/PLAN.md; validate each source standalone first |
| 3 | `llm/eval/` — questions.yaml (45 Qs), runner, judge | CLI only |
| 4 | Backend `research/` — agent loop, tool registry, SSE routes | ConversationMemory reuse |
| 5 | `LlmCallLedger` ORM + `llm_ledger_service` + usage routes | Write ledger on every gateway call; expose summary + detail API |
| 6 | `LlmProviderSettings` ORM + settings routes | Encrypted key storage; key resolution order wired into gateway |
| 7 | Handover + ClaudeSdkAdapter + `/dev/llm` playground | Test SSE, voice, model switch, ledger writes end-to-end |
| 8 | Frontend `research/` — ResearchPanel, ModelSelector, VoiceController | Promote stream.ts; chat + voice |
| 9 | Preferences → Alpha AI extended: ProviderKeysPanel, NewsSourcesPanel, UsageSummaryPanel, UsageLedgerDrawer | Full in-app management; no terminal needed |
| 10 | Wire research panel into terminal home | Replace old AIChat slot |
| 11 | Run eval, update router chains | Benchmark → routing improvement loop |

---

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Web Speech API is Chrome/Edge only | Document; type input always works |
| Claude SDK subprocess needs `~/.claude/` | 5-min headless invocation spike before Phase 5 |
| Ensemble latency too high | `RESEARCH_ENSEMBLE_TIMEOUT_S` returns fastest N if judge stalls |
| Context window overflow | Handover summarises turns older than 8; configurable |
| HuggingFace no tool calling | Prompt-based extraction fallback in AgentLoop |
| Ledger writes slow down responses | Fire-and-forget via `asyncio.create_task` — never on the critical path |
| Fernet key rotation breaks stored provider keys | Re-encrypt on key rotation; document procedure in ops runbook |
| User saves wrong API key | `PUT /llm/settings/{provider}` validates key before persisting — returns error if health check fails |
