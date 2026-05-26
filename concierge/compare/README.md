# Concierge — Comparison Docs

Decision rationale for every choice Orff needs to make beyond the three locked decisions.

## Locked decisions (no comparison needed)

| Decision | Choice |
|---|---|
| Module boundary | Concierge lives as its own backend module (`backend/app/modules/concierge`) |
| Data source | News (financial + macro + social) feeds the model's context |
| News module | **Reuse the existing `alphaforge-anton-news` workspace package** ([news/](../../news/)). Concierge calls `get_aggregator().search()` per turn — no parallel ingestion is built. New sources added by dropping `NewsSource` subclass files into [news/src/alphaforge_anton_news/sources/](../../news/src/alphaforge_anton_news/sources/). |
| LLM provider | **Existing `alphaforge_anton_llm.gateway` (free providers — Gemini / Groq / Cerebras) for v1.** Anthropic direct API added as an extension when paid usage is acceptable. |
| Cost posture | **Zero paid services for v1.** Every chosen option must have a free tier or be self-hosted. |
| Hardware | **MacBook Air 16 GB.** Everything must fit alongside Anton + browser + IDE. |
| **No local ML models** | No Ollama / Whisper.cpp / Piper / local BGE / local vision. Cloud free tiers or browser-native (OS-bundled neural voices, WASM runtimes) only. |
| **No Docker** | Self-hosted services that traditionally ship as containers (SearXNG, etc.) replaced with native installs, cloud free tiers, or skipped. |

## Open decisions

| # | Doc | Decision |
|---|-----|----------|
| 01 | [News provider](01-news-provider.md) | Which news API to ingest from |
| 02 | [Claude model routing](02-claude-model-routing.md) | Sonnet 4.6 vs Haiku 4.5 vs Opus 4.7 per intent |
| 03 | [News retrieval pattern](03-news-retrieval-pattern.md) | RAG (vector) vs tool-use vs in-context |
| 04 | [News ingestion](04-news-ingestion.md) | Poll vs RSS vs webhook |
| 05 | [Memory store](05-memory-store.md) | PostgreSQL vs Redis vs hybrid |
| 06 | [Streaming transport](06-streaming-transport.md) | SSE vs WebSocket vs HTTP chunked |
| 07 | [Intent classification](07-intent-classification.md) | Regex vs Haiku classifier vs embeddings |
| 08 | [Prompt caching](08-prompt-caching.md) | 5-min ephemeral vs 1-hour cache |
| 09 | [Vector DB](09-vector-db.md) | pgvector vs Qdrant vs Chroma vs Pinecone (only if RAG wins) |
| 10 | [Embedding model](10-embedding-model.md) | Voyage vs OpenAI vs Cohere vs local (only if RAG wins) |
| 11 | [News source expansion](11-news-source-expansion.md) | Free sources to add to the existing aggregator (StockTwits, HackerNews, Nitter, YouTube RSS, Telegram, MCA, FRED, …) + the one-file extensibility contract |
| 12 | [Long-term memory](12-long-term-memory.md) | Multi-layer memory: rolling session summary + nightly cross-session summary + extracted facts table. Anthropic memory tool deferred to paid extension. |
| 13 | [Holdings injection](13-holdings-injection.md) | Pass user portfolio into LLM context. Session-cached snapshot (1h TTL); refresh on demand. Tool-use deferred to Anthropic extension. |
| 14 | [User intent document](14-user-intent-doc.md) | Markdown file (`concierge/intent/profile.md`) the user authors describing philosophy, risk tolerance, exclusions, style preferences for Orff. Injected on every turn. |
| 15 | [Testing strategy](15-testing-strategy.md) | Per-file unit test + Jupyter notebook for every concierge module. Dependency injection, fakes, snapshot tests. |
| 16 | [Reasoning model](16-reasoning-model.md) | Add a reasoning tier. DeepSeek R1 distill via Groq primary; Gemini 2.5 Flash Thinking fallback. Reasoning trace surfaced in UI. |
| 17 | [Agentic loop](17-agentic-loop.md) | Plan-execute loop with bounded iterations + verifier pass. Single-shot for simple intents; agentic for multi-step. |
| 18 | [Multimodal inputs](18-multimodal-inputs.md) | Accept images + PDFs. Gemini Flash for vision; local pypdf for large PDFs; Qwen-VL via Ollama for offline. |
| 19 | [Tool calling](19-tool-calling.md) | Pydantic `Tool` ABC; parallel execution; pyodide sandbox for code tools. Foundational tools: prices, web, news, holdings, python, chart. |
| 20 | [Voice stack](20-voice-stack.md) | **Browser Web Speech API only** (STT + TTS). No local model weights. Frontend-only feature. |
| 21 | [Web search grounding](21-web-search-grounding.md) | **DuckDuckGo HTML primary** (no install); Brave free API opt-in; public SearXNG instance opt-in. No Docker, no local reranker. |
| 22 | [Structured outputs](22-structured-outputs.md) | Pydantic-first; native JSON-mode where supported; Instructor adapter for cross-provider. |
| 23 | [Local LLM fallback](23-local-llm-fallback.md) | **Deferred** under no-local-models + 16GB MBA constraint. App is cloud-only; offline state surfaced in UI; queued turn auto-retries on reconnect. |
| 24 | [Streaming protocol](24-streaming-protocol.md) | Typed SSE events: session / intent / thinking / plan / tool_call / tool_result / content / citation / verification / meta. |
| 25 | [Verifier pass](25-verifier-pass.md) | Hybrid symbolic + LLM verifier. Flags portfolio claims, citations, math, intent-doc adherence. ~600ms after answer streams. |

## How to read these

Each doc has the same shape:

1. **Recommended vs Chosen** — at the top, the original recommendation and what the project actually decided to use
2. **Context** — what's being decided and why now
3. **Options** — table of contenders with the dimensions that matter
4. **Tradeoffs** — narrative pros/cons per option
5. **Recommendation** — author's lean (kept for reference; the *Chosen* row at the top may override it)
6. **Open questions** — anything that should be validated before locking in

## See also

- [../4-news-llm-architecture.md](../4-news-llm-architecture.md) — end-to-end design for the chosen path: how news gets fetched, how it reaches the LLM, and how the API is exposed to the frontend.
