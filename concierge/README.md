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

- **Memory**: a user-editable **context doc** (goals/constraints) lives in the elgar store and is injected into every prompt; full **conversation history** is also persisted to elgar in its own `sessions/` collection (separate from money `plans/`) — one doc per session, listed, resumed, and deleted from the History panel — see the feature set below
- **Streaming**: LLMGateway stream -> FastAPI `StreamingResponse` -> SSE -> `useConciergeStream` hook. The trusted lane (`claude-sdk`) streams token-by-token via `client.messages.stream()` (Phase 1 — `_claude_stream.py`); free providers use the OpenAI-compat SSE path
- **Prompt caching** (trusted lane, Phase 3): the turn-stable system prefix (`SYSTEM` + objective + memory) is flagged `cacheable`; the adapter sends `system` as a block array with `cache_control: {ephemeral}` on the last cacheable block (`_claude_system.py`), so multi-turn sessions read it from cache (~0.1× input). Volatile blocks (Fux grounding, web, signals, live holdings) stay uncached. The cache read/write split + cache-aware cost land in the Cage receipt; rates live in `providers.json`
- **Shared sessions**: concierge and browser voice write to the same `concierge_turns` table via a `source` column; Orff sees the full interleaved history regardless of input modality
- **Prompt assembly**: stable system, intent, memory, holdings, news, history, and current-message blocks are composed server-side
- **Model routing**: `auto` resolves to the gateway's free-provider route for the detected intent. On the trusted lane, an intent→model tier (Phase 4, authored in `routing.json` `tiers`) picks **Opus 4.8 + adaptive thinking + `effort:high`** for plan/strategy/pick intents and **Sonnet** for chat/holdings; the `thinking_mode` request flag (Auto/On/Off) overrides the thinking gate. Thinking deltas stream as `{thinking}` via a `<think>` prefix — no frontend change
- **Single source of truth**: providers, intent routing, and the default-model policy are authored once in [`llm/src/alphaforge_anton_llm/registry/`](llm/src/alphaforge_anton_llm/registry/) (`providers.json` + `routing.json`). Python reads it via `registry.py`; the frontend regenerates `concierge.registry.generated.ts` with `pnpm gen:concierge`. Edit the manifest, never the `.ts`/`.py` copies — see [6-registry-consolidation-plan.md](docs/6-registry-consolidation-plan.md)

## Chat-app & Claude-Code feature set

Orff works like a combination of the Claude chat app and Claude Code, over the free-provider
gateway. Each capability is registry/manifest-driven and safe by construction.

| Feature | Surface | Where |
|---------|---------|-------|
| Artifacts panel | every composed UISpec collected in a side panel | [ArtifactsPanel.tsx](../frontend/src/modules/concierge/ArtifactsPanel.tsx) |
| Objective tab | north-star **target + horizon + mission** beside Memory; read-only view (`GET /signals/objective`), progress shown as a **distinct pending state** until a trades source lands; edits are proposed into chat → `set_objective` → ApprovalCard → elgar (never a silent write) | [ObjectivePanel.tsx](../frontend/src/modules/concierge/ObjectivePanel.tsx) · [objective_config.py](../backend/app/modules/signals/objective_config.py) |
| Project context / memory | user-editable doc injected into every chat, **stored in elgar** | [MemoryPanel.tsx](../frontend/src/modules/concierge/MemoryPanel.tsx) · [memory_service.py](../backend/app/modules/concierge/memory_service.py) |
| Conversation history | past chats listed in a sidebar, resume or delete — **elgar `sessions/` collection, one doc per chat** | [HistoryPanel.tsx](../frontend/src/modules/concierge/HistoryPanel.tsx) · [history_service.py](../backend/app/modules/concierge/history_service.py) |
| Claude-chat import | re-runnable sync of investment-related local Claude Code chats into Orff history (`just sync-claude-history`) | [claude_import.py](../backend/app/modules/concierge/claude_import.py) · [claude_parse.py](../backend/app/modules/concierge/claude_parse.py) |
| Vision input | paste/attach a broker screenshot → vision provider floor | `routing.json` `vision` · [_vision.py](llm/src/alphaforge_anton_llm/providers/_vision.py) · [ImageAttach.tsx](../frontend/src/modules/concierge/ImageAttach.tsx) |
| Suggested follow-ups | 3 tap-to-send chips after each reply | [FollowupChips.tsx](../frontend/src/modules/concierge/FollowupChips.tsx) · [followup_service.py](../backend/app/modules/concierge/followup_service.py) |
| Edit & branch | edit a prior turn, drop everything after, resubmit | `useChatStream.editTurn` |
| Export thread | download the conversation as Markdown | [chat.export.ts](../frontend/src/modules/concierge/chat.export.ts) |
| Voice readback (TTS) | speak each completed reply | `useVoice.speak` |
| Tool / data-read trail | collapsible blocks for Fux recall, memory, disclosure | [ToolTrail.tsx](../frontend/src/modules/concierge/ToolTrail.tsx) |
| Reasoning trace | `<think>…</think>` split into a collapsible block | [ThinkingBlock.tsx](../frontend/src/modules/concierge/ThinkingBlock.tsx) · `stream_events.split_thinking` |
| Slash commands | `/rebalance`, `/projection`, `/export`, `/memory`, … | [concierge.commands.ts](../frontend/src/modules/concierge/concierge.commands.ts) |
| Cmd+K palette | keyboard-first command launcher | [CommandPalette.tsx](../frontend/src/modules/concierge/CommandPalette.tsx) |
| Plan-change diffs | before/after reallocation as a two-column diff | `DiffTable` (solar-ui, composable) |
| Session cost meter | live token + real-USD spend (priced from the registry) | [SessionMeter.tsx](../frontend/src/modules/concierge/SessionMeter.tsx) |
| Stop generation | abort the in-flight stream mid-token | `useChatStream.stop` |
| Action confirmations | structured approval card for mutating intents | [ApprovalCard.tsx](../frontend/src/modules/concierge/ApprovalCard.tsx) · [action_service.py](../backend/app/modules/concierge/action_service.py) |

### Stream event protocol

`POST /concierge` streams Server-Sent Events — one JSON object per `data:` line, assembled in
[concierge_service.py](../backend/app/modules/concierge/concierge_service.py) and reduced
client-side by [chat.events.ts](../frontend/src/modules/concierge/chat.events.ts):

| Event shape | Meaning |
|-------------|---------|
| `{content, provider, model, prompt_tokens, completion_tokens, cost_usd, …}` | cumulative token snapshot |
| `{tool: {name, detail, ms}}` | a prompt-assembly / data-read step (Fux recall, memory, disclosure, vision route, `parallel` web grounding) |
| `{thinking: "…"}` | reasoning trace split from a `<think>` block |
| `{confirm: {id, action, summary, steps, apply?}}` | approval card for a mutating intent; an optional `apply: {path, body}` makes Approve POST it (e.g. a signals strategy-knob change) |
| `{spec: {…}}` | a UISpec — either a Fux-validated compose follow-up or the **deterministic signals plan card** (`signals/plan_card.py`) on a `/review` turn |
| `{followups: ["…"]}` | up to 3 tap-to-send next prompts |
| `{error: "…"}` then `[DONE]` | redacted error; the stream always terminates with `[DONE]` |

Every step runs inside `stream_chat`'s `try`, so a failure becomes an SSE `error` event rather than
a dead connection. Prompt assembly (system, Fux grounding, **elgar memory**, holdings disclosure,
history, vision floor) lives in [prompt_service.py](../backend/app/modules/concierge/prompt_service.py).
The protocol is covered by `just probe concierge-events` (standalone, no CDP).

**Agent-initiated deep search — Orff asks before spending (handoff §9; canonical spec
in [deep-search-ask.handoff.md](../docs/handoffs/deep-search-ask.handoff.md)).** The old on/off
`web_grounding` toggle is retired. Instead the trusted tool-calling lane offers a
**confirm-gated** tool, `request_deep_search(reasons, queries)` ([tool_registry.py](../backend/app/modules/concierge/tool_registry.py));
the system prompt tells Orff to call it — with concrete reasons — when a question needs
current web data it lacks, rather than guessing or answering stale. A request carries
`deep_search_mode` (default `auto`), set by the tri-state **🌐 Auto / Always / Never**
control in the composer ([DeepSearchMode.tsx](../frontend/src/modules/concierge/DeepSearchMode.tsx),
persisted to `localStorage["af-deep-search-mode"]` via `ChatContext`):

- **Auto** — on the call, [deep_search_service.py](../backend/app/modules/concierge/deep_search_service.py)
  emits a `{confirm}` card (`summary`=reasons, `steps`=queries, `detail`=`~₹0.5 · ₹<mtd> of
  ₹<budget> used this month`) and **makes no Parallel call**. The card renders via
  [ApprovalCard.tsx](../frontend/src/modules/concierge/ApprovalCard.tsx) (now showing the
  reasons + the cost line beneath the queries); on Approve it `POST`s the apply target
  `/concierge/deep-search` to run the queries; reject ⇒ Orff answers from free sources and
  says what it couldn't verify.
- **Always** — the tool runs cardless (auto-confirm) inside the loop; grounding is fed back
  as the `tool_result` and Orff continues.
- **Never** — the tool isn't offered at all.

The shared executor is `grounding_service.run` (one Parallel call → one **Search-vs-Task-tagged**
Cage receipt via `cage_meter.record_tool`; key `PARALLEL_API_KEY`, afbach-vault-injected —
never env/code). `grounding_service.budget_status` reads `cage_meter.month_spend_usd("parallel")`
(month-to-date, INR-converted) vs `parallel.monthly_budget_inr` — over budget ⇒ the card/flow
degrades to free sources and says so, no call, no receipt. Task tier is gated on
`parallel.allow_task_api` + a deep-dive prompt. **Fail-open throughout** — a grounding error
yields a free-source answer, never a dead stream. Verified by `just probe deep-search`
(backend: auto / confirm / reject / always / never / over-budget) and `just probe ui-deep-search`
(frontend: the tri-state control sends the mode + an Auto gap renders the card, real Chrome).

The user-context doc lives in the **elgar store** (`elgar get/save orff-context`), not a home-dir
file — it holds personal goals/figures, exactly the money-adjacent data the `plan-store` rule keeps
in elgar. Anton reaches it over the shared `elgar` CLI via [elgar_bridge.py](../backend/app/modules/plans/elgar_bridge.py).

**Conversation history** uses the same store but its **own collection** — elgar docs
live in named subdirs (`store/plans/*.plan.md` for money plans, `store/sessions/*.session.md`
for chat history), so a chat never mixes with a plan or shows up in `elgar list`. Each chat is
one `sessions/` doc, rewritten in place as it grows (debounced ~900ms after a turn settles, so a
completed exchange is one git commit — never per token). The store's git log *is* the
conversation's audit trail. [history_service.py](../backend/app/modules/concierge/history_service.py)
renders a human-readable transcript with a machine block for lossless resume; the routes are
`GET /concierge/history` (list), `GET|PUT|DELETE /concierge/history/{id}`. All history I/O is
best-effort — a missing/unreachable store degrades to an empty sidebar, never blocking the chat.
The collection is selected with the elgar `--dir sessions` flag (`elgar list/get/save/rm`), which
the bridge threads through `list_docs` / `get` / `save` / `remove`.

**Importing past Claude chats** — `just sync-claude-history [--dry-run]` is a re-runnable
mechanism that copies investment-related conversations from the local Claude Code transcripts
(`~/.claude/projects/*.jsonl`) into the same `sessions/` collection.
[claude_parse.py](../backend/app/modules/concierge/claude_parse.py) strips tool calls, tool
results, and system/command wrappers so each import reads as a clean You/Orff transcript;
[claude_import.py](../backend/app/modules/concierge/claude_import.py) keeps a chat only when the
human's prompts carry real **advice signal** — ≥`MIN_HITS` investment-decision phrases (`_INVEST`)
that also **outweigh** engineering signal (`_DEV`) — so coding sessions on the app itself are
excluded even though they mention broker/holdings/portfolio. Matches upsert under a stable id
(`claude-<sessionId>`, `source: claude-code` in frontmatter). The render is deterministic (the
transcript's mtime as `updated`), so re-syncing only commits transcripts that actually changed.
(Note: a pure Claude Code dev history typically yields zero — genuine investment chats live in the
claude.ai chat app, which would need its data export as the source instead.)
Contract: `just probe claude-import` (standalone — no real `~/.claude`, no store writes).

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

## Private holdings disclosure (chokepoint)

Holdings-classified prompts never reach a free provider: [holdings_private.py](../backend/app/modules/concierge/holdings_private.py)
floors routing to the trusted provider (`enforce_floor()`), then discloses **tiered by
trust**: the trusted lane gets `detailed_context()` — full holding rows (symbol, qty,
avg/ltp, INR value, P&L) rendered by [holdings_detail.py](../backend/app/modules/concierge/holdings_detail.py) —
while any other provider would get `disclosed_context()`, percentages-only, no ₹, no
symbols. Both lanes are asserted by `probes/holdings_disclosure_probe.py`. When the
elgar store has no committed plan, contexts degrade honestly instead of raising — a
missing plan once killed the SSE stream before its first byte and surfaced as
`TypeError: Failed to fetch` in the chat rail. Two invariants guard the path:
`stream_chat` runs entirely inside its `try` (any failure becomes an SSE `error` event +
`[DONE]`, never a dead connection), and the claude-sdk adapter joins **all** system
messages (persona + Fux grounding + disclosure) — keeping only the first silently
dropped the disclosure rules and produced fabricated demo holdings tables.

## Implementation entry point

Start with the implementation order in [4-news-llm-architecture.md section 16](4-news-llm-architecture.md#16-implementation-order).
