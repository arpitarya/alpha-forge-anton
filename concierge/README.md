# Orff — Concierge AI

**Orff** is the conversational AI layer inside AlphaForge Anton - a persistent, session-aware financial assistant backed by the existing `alphaforge_anton_llm.gateway` free-provider stack, with server-side memory shared across concierge and browser voice modalities.

Named after Carl Orff, in keeping with the project's composer naming convention (Anton, Wagner, Dante).

---

## Documents

| # | File | What it covers |
|---|------|----------------|
| 1 | [4-news-llm-architecture.md](4-news-llm-architecture.md) | **Substrate (v1)** - reuses [alphaforge-anton-news](../news/) aggregator + existing portfolio module -> LLMGateway -> SSE -> frontend. Covers prompt assembly, multi-layer long-term memory, holdings injection, user intent document, per-file testability, and notebooks. |
| 2 | [5-capability-roadmap.md](5-capability-roadmap.md) | **Capability roadmap (zero paid services)** - reasoning route, agentic loop, multimodal input, tool calling, browser voice, web grounding, structured outputs, and verifier pass. |
| 3 | [providers.md](providers.md) | **LLM provider & model registry** - all provider slugs, env keys, active models, intent→provider routing table, vision providers, and future Anthropic tier. |
| - | [compare/](compare/) | Decision rationale for implementation choices that remain in scope. Each doc has a `Recommended vs Chosen` header showing what the project picked. |
| - | Memory + context | [11 news sources](compare/11-news-source-expansion.md) · [12 long-term memory](compare/12-long-term-memory.md) · [13 holdings injection](compare/13-holdings-injection.md) · [14 intent doc](compare/14-user-intent-doc.md) |
| - | Engineering | [15 testing strategy](compare/15-testing-strategy.md) · [22 structured outputs](compare/22-structured-outputs.md) · [24 typed streaming](compare/24-streaming-protocol.md) |
| - | Planned capabilities | [16 reasoning model](compare/16-reasoning-model.md) · [17 agentic loop](compare/17-agentic-loop.md) · [18 multimodal](compare/18-multimodal-inputs.md) · [19 tool calling](compare/19-tool-calling.md) · [25 verifier](compare/25-verifier-pass.md) |
| - | Modalities + infra | [20 browser voice](compare/20-voice-stack.md) · [21 web search](compare/21-web-search-grounding.md) |

---

## Quick orientation

- **Memory**: `concierge_sessions` + `concierge_turns` (PostgreSQL) replace the 6-turn in-memory frontend window
- **Streaming**: LLMGateway stream -> FastAPI `StreamingResponse` -> SSE -> `useConciergeStream` hook
- **Shared sessions**: concierge and browser voice write to the same `concierge_turns` table via a `source` column; Orff sees the full interleaved history regardless of input modality
- **Prompt assembly**: stable system, intent, memory, holdings, news, history, and current-message blocks are composed server-side
- **Model routing**: `auto` resolves to the gateway's free-provider route for the detected intent; reasoning-capable routes are added through the roadmap work
- **Single source of truth**: providers, intent routing, and the default-model policy are authored once in [`llm/src/alphaforge_anton_llm/registry/`](llm/src/alphaforge_anton_llm/registry/) (`providers.json` + `routing.json`). Python reads it via `registry.py`; the frontend regenerates `concierge.registry.generated.ts` with `pnpm gen:concierge`. Edit the manifest, never the `.ts`/`.py` copies — see [6-registry-consolidation-plan.md](docs/6-registry-consolidation-plan.md)

## On-the-fly UI composition (Fux-governed)

Orff can build UI on the fly without executing generated code. `POST /concierge/compose`
( [compose_service.py](../backend/app/modules/concierge/compose_service.py) ) runs:
`fux components` (the allowed vocabulary) → LLM emits a **declarative UISpec** (JSON
tree, never code) → `fux validate-spec` rejects/repairs anything off-registry (1 retry)
→ `<DynamicRenderer>` ( [frontend](../frontend/src/modules/concierge/DynamicRenderer.tsx) )
mounts it from a fixed whitelist → `fux feedback` records the outcome. The
`ui-component-contract` rule (`.fux/`) governs it; the brain is reached over the `fux`
CLI via [fux_bridge.py](../backend/app/modules/concierge/fux_bridge.py). Safe by
construction — no path renders anything outside the design-system whitelist.

## Implementation entry point

Start with the implementation order in [4-news-llm-architecture.md section 16](4-news-llm-architecture.md#16-implementation-order).
