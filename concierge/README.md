# Orff — Concierge AI

**Orff** is the conversational AI layer inside AlphaForge Anton — a persistent, session-aware financial assistant backed by the Anthropic API (Claude Sonnet / Haiku) with server-side memory shared across concierge and voice modalities.

Named after Carl Orff, in keeping with the project's composer naming convention (Anton, Wagner, Dante).

---

## Documents

| # | File | What it covers |
|---|------|----------------|
| 1 | [1-concierge-plan.md](1-concierge-plan.md) | Original Anthropic-direct plan: goal, data model, backend + frontend changes, implementation order |
| 2 | [2-concierge-flow.md](2-concierge-flow.md) | 13 Mermaid flow diagrams — sequence, flowchart, ERD, state machine |
| 3 | [3-concierge-flow.html](3-concierge-flow.html) | Interactive HTML viewer for the diagrams (Solar Terminal theme, Mermaid v11) |
| 4 | [4-news-llm-architecture.md](4-news-llm-architecture.md) | **Substrate (v1)** — reuses [alphaforge-anton-news](../news/) aggregator + existing portfolio module → LLMGateway → SSE → frontend. 8-block prompt, multi-layer long-term memory, holdings injection, user intent document, per-file testability + notebooks. |
| 5 | [5-state-of-the-art.md](5-state-of-the-art.md) | **State-of-the-art capability stack (zero paid services)** — reasoning models, agentic loop, multimodal vision, tool calling, voice, web grounding, local LLM fallback, verifier. Phased roadmap v1 → v1.3. |
| — | [compare/](compare/) | Decision rationale for every open choice. Each doc has a `Recommended vs Chosen` header showing what the project actually picked. |
| — | Memory + context | [11 news sources](compare/11-news-source-expansion.md) · [12 long-term memory](compare/12-long-term-memory.md) · [13 holdings injection](compare/13-holdings-injection.md) · [14 intent doc](compare/14-user-intent-doc.md) |
| — | Engineering | [15 testing strategy](compare/15-testing-strategy.md) · [22 structured outputs](compare/22-structured-outputs.md) · [24 typed streaming](compare/24-streaming-protocol.md) |
| — | SOTA capability | [16 reasoning model](compare/16-reasoning-model.md) · [17 agentic loop](compare/17-agentic-loop.md) · [18 multimodal](compare/18-multimodal-inputs.md) · [19 tool calling](compare/19-tool-calling.md) · [25 verifier](compare/25-verifier-pass.md) |
| — | Modalities + infra | [20 voice stack](compare/20-voice-stack.md) · [21 web search](compare/21-web-search-grounding.md) · [23 local LLM](compare/23-local-llm-fallback.md) |

---

## Quick orientation

- **Memory**: `concierge_sessions` + `concierge_turns` (PostgreSQL) replace the 6-turn in-memory frontend window
- **Streaming**: Anthropic `messages.stream()` → FastAPI `StreamingResponse` → SSE → `useConciergeStream` hook
- **Shared sessions**: concierge and voice write to the same `concierge_turns` table via a `source` column — Orff sees the full interleaved history regardless of input modality
- **Prompt caching**: `cache_control: ephemeral` on the system block gives ~80% cache hit rate across turns
- **Model routing**: `auto` slug resolves to `claude-sonnet-4-6` (investment/portfolio intent) or `claude-haiku-4-5-20251001` (factoid/news); `claude-sdk` always hits Sonnet

## Implementation entry point

Start at **Step 1** in [1-concierge-plan.md](1-concierge-plan.md#implementation-order): Alembic migration at `backend/alembic/versions/c7a3e9f1d2b8_concierge_memory.py` (already written).
