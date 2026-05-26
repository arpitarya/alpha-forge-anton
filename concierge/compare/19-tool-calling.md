# 19 — Tool / Function Calling

## Recommended vs Chosen

| | Choice | Cost |
|---|---|---|
| **Recommended** | Native tool calling via provider APIs (Gemini, Groq); parallel execution; explicit tool registry | Free |
| **Chosen** | **Tool registry pattern: each tool is a Python class implementing `Tool` ABC, auto-registered. Native tool-calling syntax for Gemini + Groq; JSON-mode fallback for providers without first-class support. Tools execute in parallel within an agentic step ([17](17-agentic-loop.md)). Code-exec sandbox uses Python subprocess with `RestrictedPython` + `signal.SIGALRM` timeout + AST-level allowlist — no Docker.** | Free |

**Why the sandbox deviation**: original recommendation was pyodide-in-Docker. Docker is ruled out. Two non-container alternatives:

1. **`RestrictedPython` + subprocess + `SIGALRM`** — pure Python; restricts builtins, blocks `__import__` outside an allowlist, kills the process on timeout. Weaker isolation than Docker but acceptable for the single-user threat model (model-emitted code, not adversarial user code).
2. **pyodide via Python subprocess** (no browser) — uses `pyodide-py` to run code in a WASM sandbox without a container. Stronger isolation but ~500ms startup overhead per call and limited scientific stack vs full CPython.

**Chosen**: **start with option 1 (`RestrictedPython`)** for v1.1 — fits the threat model (Orff isn't running adversarial code, just its own math). If we ever expose tool-use to untrusted input (e.g., user pasting code they want analyzed), upgrade to option 2.

---

## Context

Tool calling is how the LLM goes from "talker" to "doer." Orff needs to fetch live prices, run web searches, compute portfolio math, render charts, look up filings. In 2026 all major free providers support tool calling natively.

## Initial tool set (v1.1 — v1.2)

| Tool | Purpose | Latency budget | Implementation |
|---|---|---|---|
| `get_price(symbol)` | Live LTP for an NSE/BSE ticker | <500ms | `yfinance` |
| `get_prices(symbols)` | Batch LTP | <1s | `yfinance` batched |
| `get_fundamentals(symbol)` | P/E, P/B, ROE, dividend yield | <1s | `yfinance` info |
| `get_holdings()` | User's portfolio snapshot | <100ms | reads cached snapshot from holdings_service |
| `get_position(symbol)` | One position detail | <100ms | reads from snapshot |
| `search_news(query, symbols?, since?)` | News search across aggregator | <8s | calls existing `NewsAggregator.search()` |
| `search_web(query)` | General web search | <5s | SearXNG → DuckDuckGo fallback ([21](21-web-search-grounding.md)) |
| `compute_sector_weights(holdings)` | Current sector exposure | <100ms | pure Python over holdings |
| `compute_returns(symbol, period)` | Historical return | <1s | `yfinance` history |
| `read_pdf_pages(file_id, pages)` | Pull specific pages from an uploaded PDF | <500ms | in-memory store of current-request attachments |
| `run_python(code)` | Sandboxed Python for ad-hoc math | <5s | Docker / `RestrictedPython` / `pyodide` — see sandbox section |
| `render_chart(spec)` | Generate a matplotlib PNG | <2s | inside the same sandbox as `run_python` |

## Options for the framework

### A. Roll our own registry

A `Tool` ABC, a `ToolRegistry`, JSON schema generation from Pydantic models, native provider format conversion.

### B. Use an existing library (LangChain, Instructor, MCP)

- **LangChain** — heavy, opinionated, fast-moving API.
- **Instructor** — focused on structured outputs / function calling. Lightweight.
- **MCP (Model Context Protocol)** — Anthropic's standard; growing ecosystem of pre-built MCP servers (filesystem, web search, etc.).

### C. Native provider SDKs directly

Use `google.genai`, `groq`, etc. tool-calling syntax directly per provider.

## Comparison

| Dimension | A. Roll our own | B. Library (Instructor/MCP) | C. Direct SDK |
|---|---|---|---|
| Build cost | Medium (~250 LOC) | Low (lib does most of it) | Low per-provider, high across providers |
| Provider portability | High | Medium (lib abstracts) | Low |
| Control | Full | Medium | Full per provider |
| Dependency surface | Minimal | Adds lib + transitives | Minimal |
| Future-proofing (MCP ecosystem) | Manual | MCP brings free third-party tools | Manual |
| Testability | Excellent (pure Python) | OK | OK |

## Recommendation

**A (roll our own thin registry) for v1.1, with MCP compatibility as a v1.3 goal.**

Rationale:
- Anton's tool set is small and domain-specific (portfolio tools). LangChain's surface area is mostly noise.
- A thin `Tool` ABC + `ToolRegistry` is ~200 LOC, follows the same one-file-per-source pattern as the news aggregator, and is trivially testable.
- MCP is the right long-term standard but the spec is still maturing. Add an MCP adapter in v1.3 once the v1.1/1.2 tools are stable — then we get both our own tools + the growing ecosystem of MCP servers (e.g., filesystem MCP, browser MCP).

### Contract

```python
class Tool(ABC):
    name: str                     # snake_case unique name
    description: str              # shown to LLM; what + when to use
    input_schema: type[BaseModel] # Pydantic model
    output_schema: type[BaseModel] | None = None
    sandboxed: bool = False       # code-exec tools only
    latency_budget_ms: int = 5000

    @abstractmethod
    async def call(self, args: BaseModel, *, ctx: ToolContext) -> Any: ...

class ToolContext(BaseModel):
    user_id: UUID
    session_id: UUID
    holdings_snapshot: list[Holding] | None
    intent_doc: str | None
    request_attachments: dict[str, bytes]
```

### Per-provider native format

`ToolRegistry.to_gemini_tools()`, `.to_groq_tools()`, `.to_anthropic_tools()` produce the provider-specific JSON. One function per provider; ~30 LOC each.

### Parallel execution

The agentic loop ([17](17-agentic-loop.md)) gathers all tool calls per step:

```python
tool_results = await asyncio.gather(*[
    tool_registry.call(tc.name, tc.args, ctx=ctx)
    for tc in step.tool_calls
], return_exceptions=True)
```

`return_exceptions=True` → individual tool failures surface as `tool_result` events with an error payload; the model decides whether to retry, skip, or report.

### Sandboxing for `run_python` / `render_chart`

| Option | Isolation | Setup |
|---|---|---|
| **Docker container** per call | Strong | Requires Docker on host; ~500ms cold start |
| **`RestrictedPython`** | Weak (Python-level) | Pure Python; fast; not a real security boundary |
| **`pyodide`** (WASM Python) | Strong | ~50MB WASM; fast; limited scientific stack |
| **`nsjail`** / `firejail` | Strong on Linux | Linux-only |
| **Subprocess with `seccomp`** | Strong on Linux | Linux-only |

**Choice**: **`pyodide` in a separate process** for the sandbox. Cross-platform (matches Anton's Mac dev / Linux deploy story), strong isolation (WASM), supports numpy/pandas/matplotlib. Cold start is acceptable amortized across calls.

**Fallback**: `RestrictedPython` for environments where pyodide can't run. Document the weaker isolation.

### Tool result formatting back to LLM

Tool outputs serialize to JSON. Each tool emits a Pydantic model; `model_dump_json()` is what the LLM sees. Long outputs (e.g., `search_news` returning 20 articles) truncate to a token budget per tool (default ~2k tokens); model can ask for more via pagination args.

### Tool calling on providers without native support

For local Ollama models or smaller models that don't have first-class tool calling, fall back to **JSON-mode prompting**:

```
Available tools: [tool schemas as JSON]

Respond with either:
- {"tool_calls": [{"name": "...", "args": {...}}, ...]} to call tools
- {"answer": "..."} to give a final answer
```

Brittle but functional. Reserved for the offline-mode path.

### Per-tool permissions

A tool registry per-user enable/disable map (defaults all on). User can disable e.g. `search_web` if they want strict-news-only mode. Out of scope for v1.1 (single-user defaults are fine); add when multi-user.

## Tool discovery & docs

Auto-generate a developer-facing tool catalog (`concierge/tools.md`) from the registry — name, description, input schema, output schema. Updated by a notebook (`concierge/notebooks/09_tools_catalog.ipynb`) that runs on demand.

## Open questions

- **Tool naming convention**: `snake_case`, prefix domain (`portfolio_get_holdings`)? Choose one and stick to it.
- **Tool error semantics**: if `get_price("INVALID")` is called, return `{"error": "..."}` in the result or raise? Choice: return error payload, never raise — the LLM can read errors and adapt.
- **Tool versioning**: when we add `get_price_v2`, deprecate v1 with a `deprecated: bool` flag and keep both available for one release.
- **Tool tracing**: every tool call should log `{tool, args, latency_ms, error?}` to a `concierge_tool_calls` table (or just structured logs) for debugging. Trivial to add; high value.
- **Budget per turn**: hard cap on total tool-call wall time per turn (default 20s). Beyond that, agentic loop must wrap up.
- **MCP migration path**: when MCP stabilizes, write a thin adapter that exposes our `Tool` ABC as an MCP server *and* consumes external MCP servers via our registry. Both directions.
- **Cost tracking**: track tool call counts + bytes per turn for the meta frame.
