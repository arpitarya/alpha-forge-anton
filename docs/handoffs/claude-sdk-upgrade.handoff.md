# Handoff — Claude provider upgrade (use the Anthropic API to its full extent)

**For:** Claude Code, in the `anton` repo. **Plan first, stop for review, then build.**
**Target file:** `concierge/llm/src/alphaforge_anton_llm/providers/claude_sdk.py` (the
trusted lane) + the gateway/registry + `prompt_service`.

**Why:** the adapter uses ~a third of the Messages API. Today (line refs as of this
handoff): `supports_streaming = False` (blocking), the `tools` param is accepted then
**dropped** (never passed to `messages.create`), `response.content[0].text` assumes the
first block is text (crashes on `tool_use`/`thinking`), no prompt caching, no extended
thinking, one pinned model. Stay on the **Messages API** (the multi-provider gateway is
provider-agnostic by design) — do NOT adopt the Claude Agent SDK; just light up the
capabilities below.

> No personal figures in the repo. Interfaces, params, rules only.

## What the gateway already gives us (reuse)

- Streaming is opt-in per adapter: `gateway.stream()` uses `adapter.astream()` **iff**
  `supports_streaming` and `hasattr(adapter, "astream")` — else one-shot `complete()`.
  So: add `astream()` + flip the flag; no gateway change needed for streaming.
- `complete(prepared, tools=tools, model=...)` — the gateway **already forwards tools**.
  The adapter is the only thing ignoring them.
- The SSE protocol already renders `{thinking:…}`, `{tool:{…}}`, and token snapshots —
  the frontend needs nothing new for thinking/tools beyond what exists.

## Phase 1 — Streaming + correct content parsing

> **Status (2026-06-16): ✅ Shipped.** `astream()` (via `client.messages.stream()`),
> `supports_streaming = True`, the `_parse_blocks` content-block walk, and `tool_use`
> blocks kept aside all live in `claude_sdk.py` + `_claude_stream.py`; the gateway
> auto-detects `astream` (no gateway change). Verified by `just probe claude-stream`
> (10/10). Thinking-block collection is intentionally deferred to Phase 4 — thinking
> blocks only appear when `thinking` is enabled in the request, and the walk skips
> non-text blocks so a non-text first block can't crash. Not yet exercised: live
> token-by-token UI streaming against the paid lane (needs `ANTHROPIC_API_KEY` + the
> app under CDP).

- Add `async def astream(self, messages, *, model=None, tools=None)` using
  `client.messages.stream(...)`; yield cumulative `ProviderResponse` snapshots (content
  so far + running `input_tokens`/`output_tokens` from the final `message_delta`).
- Set `supports_streaming = True`.
- Replace `response.content[0].text` with a block walk: concatenate all `text` blocks;
  collect `thinking` blocks → `{thinking}` snapshots; collect `tool_use` blocks for Phase 2.
- Keep `complete()` working (non-stream callers + fallback) on the same block walk.

**Done:** the trusted lane streams token-by-token in the UI; a reply containing a
non-text first block no longer crashes. Probe: a fixture stream assembles to the full text.

## Phase 2 — Real tool-calling loop (satisfies Phase 2 of orff-tool-calling.handoff.md)

> **Status (2026-06-16): ✅ Shipped — all acceptance gates green.** Adapter converts
> `ToolSchema → tools=[…]`, passes them through, and returns `tool_use` blocks in the typed
> `ProviderResponse.tool_calls` field (not swallowed). The concierge agentic loop lives in
> `tool_layer.py` (`_MAX_ROUNDS=5`, trusted-lane-only, reads auto-run, mutating → `{confirm}`
> + pause, `tool_result` re-invoke, each hop a `{tool}` step). Mutating writes happen only
> after confirm, server-side, via `POST /concierge/exclusion` etc. Verified: `just probe
> concierge-tools` (18/18), `holdings-disclosure` + `objective` green, `just dante-pii` exit 0.
>
> **Known follow-ups (reviewer-accepted as out of scope for the verify-only pass):**
> 1. **Cage-metering gap** — `tool_layer.run()` hand-rolls its own `anthropic.AsyncAnthropic`
>    client instead of going through the gateway, so `cage_meter.record()` never runs for tool
>    rounds or the final tool answer: trusted-lane tool usage is **not** in the Cage ledger.
> 2. **Architecture divergence** — because of (1), the adapter's `tool_calls` field is built but
>    unused by the loop; client/config setup is duplicated. Unifying on `gateway.complete(tools=)`
>    first requires teaching `Message` + the adapter to round-trip `tool_use`/`tool_result` turns
>    (today `Message.content` is `str`-only). `claude_sdk.astream(tools=)` is accepted but ignored.

Keep the split clean: **the LLM package stays app-agnostic** (it surfaces `tool_use`,
accepts `tool_result`); **the agentic loop lives in `concierge`** (it runs the tool and
re-calls), so the provider never imports `app.` services.

- Adapter: convert `ToolSchema` → Anthropic `tools=[…]`; pass it through; on
  `stop_reason == "tool_use"`, return the `tool_use` blocks (id, name, input) in the
  `ProviderResponse` (add a typed `tool_calls` field) instead of swallowing them.
- Concierge (`concierge_service`): when a response carries tool calls, dispatch to the
  registry tools (read tools auto-run; mutating tools emit the `{confirm}` card and pause),
  append `tool_result` turns, and re-invoke — bounded loop (max N hops), best-effort.
- Surface each hop as a `{tool:{…}}` ToolTrail step (already rendered).

**Done:** "fetch my latest plan" resolves in-chat via `latest_action_plan`; "add X to
blacklist" emits a confirm card and writes only on confirm. Cross-check: this is the same
acceptance as orff-tool-calling.handoff §Acceptance — build them in one pass.

## Phase 3 — Prompt caching (the cost lever)

> **Status (2026-06-16): ✅ Shipped.** `Message.cacheable` added; `prompt_service` marks
> SYSTEM + objective + memory as the contiguous cacheable prefix (Fux grounding, web,
> signals, live holdings stay volatile, after the breakpoint). The adapter
> (`_claude_system.system_blocks`) emits `system` as a block array with `cache_control:
> {type: ephemeral}` on the last cacheable block. `ProviderResponse` carries the
> `cache_read_input_tokens` / `cache_creation_input_tokens` split (populated in `complete()`
> and `_claude_stream`); `cage_meter` records the split + cache-aware cost into the Cage
> receipt, and **`gateway.stream()` now meters the final snapshot** (it previously metered
> nothing). Rates live in `providers.json` (`cache_read_per_m` / `cache_write_per_m`).
> Verified: `just probe claude-cache` (15/15), `dante-pii` exit 0, ruff clean (no new
> findings). Not yet exercised: a live `cache_read_input_tokens > 0` after turn 1 needs
> `ANTHROPIC_API_KEY` + 2 turns. Note: the hand-rolled `tool_layer` lane (Phase 2 follow-up)
> still builds one joined system string and is uncached — the Done criterion is met by the
> non-tool streaming lane.

The adapter joins ALL system messages into one string. To cache, split stable vs volatile:

- **Cacheable prefix = SYSTEM + objective + memory ONLY** (the turn-stable blocks).
  **NOT Fux grounding** — `fux_recall(last_user)` is query-dependent and changes every turn,
  so caching it makes the prefix never match and `cache_read` stays 0. Fux grounding, web
  grounding, signals, and live holdings are all **volatile** → they sit *after* the breakpoint.
- This requires **reordering** prompt assembly: the three stable blocks must be **contiguous
  at the front** (SYSTEM → objective → memory), the cache breakpoint right after memory, then
  every volatile block. Add `cacheable: bool` to the system `Message` (or a convention) and
  order accordingly.
- Adapter sends `system` as a block array with `cache_control: {type: "ephemeral"}` on the
  last cacheable block; volatile blocks follow without it.
- The cached prefix must clear Anthropic's **minimum cacheable length** (~1024 tokens) or
  `cache_control` is silently ignored. SYSTEM + objective + memory should clear it.
- **Pricing lives in `providers.json`** (single-source rule): add `cache_read_per_m` and
  `cache_write_per_m` to the `claude-sdk` model's consumption block — do NOT derive the
  multipliers in `pricing.py`. Using `ephemeral` (5-min), so one `cache_write_per_m` suffices.
  Record the cache read/write token split into the Cage receipt so the saving is visible.

**Done:** a multi-turn session shows `cache_read_input_tokens` > 0 after turn 1; Cage shows
the reduced input cost. This is pure cost reduction — directly serves the ₹ target.

## Phase 4 — Extended thinking + model tiering

> **Status (2026-06-16): ✅ Shipped (backend).** Tiers are authored in `routing.json`
> (`tiers.claude-sdk` + `reasoning_intents`); `registry.model_for` / `effort_for` /
> `is_reasoning_intent` resolve them (not the adapter). `prompt_service` → `tiering_service.
> resolve()` picks the Claude model + thinking gate from the **text intent** (`intent_qt`),
> honouring the `thinking_mode` toggle (auto/on/off) and an explicit model pin. The gateway
> passes `thinking={"type":"adaptive","display":"summarized"}` (+ `output_config.effort`)
> to the adapter only when `supports_reasoning`; `_claude_stream` surfaces `thinking_delta`
> as a `<think>` prefix so the existing `{thinking}` SSE path renders the trace (no frontend
> change). `/review` + strategy → **Opus 4.8 + thinking + effort:high**; chat + holdings →
> **Sonnet**; the Haiku tier is reserved for followups/classification (which run on the free
> chain today, so it's config-only until they route to the paid lane). Verified: `just probe
> claude-tiering` (18/18), all prior probes green, `dante-pii` exit 0, ruff clean (no new
> findings). **`budget_tokens` is intentionally NOT used** — it 400s on Sonnet 4.6 / Opus 4.8;
> adaptive thinking replaces it. **Follow-up:** the `thinking_mode` request flag is wired
> end-to-end, but the **frontend** Think-harder toggle UI (mirroring web_grounding's) is not
> built; live Opus trace needs the paid key.

**Thinking control — adaptive + effort tier** (`budget_tokens` is deprecated on Sonnet 4.6
/ Opus 4.8):
- `thinking={"type":"adaptive","display":"summarized"}` for reasoning intents; the model
  self-modulates depth. Stream thinking deltas as `{thinking}` (ThinkingBlock renders them).
- `output_config={"effort":...}` is the real depth/cost lever now: `effort:high` on
  review/strategy (Opus); a lighter default elsewhere. Author it as a registry tier, not in
  the adapter.

**Intent → tier (the cost/depth boundary):**
- `investment_plan` (incl. `/review` + strategy) and `stock_pick` → **Opus 4.8 + adaptive
  thinking + effort:high**.
- `portfolio_private` (holdings questions / net worth) and general chat → **Sonnet, no/low
  thinking**. Rationale: holdings queries are high-frequency *retrieval* (numbers come from
  deterministic code, not reasoning) — don't pay Opus+thinking on lookups. Reserve depth for
  the low-frequency, high-stakes plan/pick synthesis. Haiku for classification/followups.

**User override — a tri-state "Think harder" toggle (Auto / On / Off, default Auto):**
- **Auto** (default) = the two automatic layers above: intent routing decides *whether* to
  think; `type:adaptive` decides *how deep*. This IS the "auto-detect if it needs thinking"
  behaviour — no separate model call to decide.
- **On** = force adaptive thinking on the current intent's model (occasional "really reason
  about this"). **Off** = disable thinking (cost/latency brake).
- Same off-by-default-override pattern as the Deep-search toggle; carry a `thinking_mode`
  flag on the request, mirroring `web_grounding`.
- **Do NOT** add an LLM pre-classifier to decide thinking — intent routing + adaptive cover
  it; if the classifier proves too coarse, extend the **deterministic** router with keyword
  signals, never a model call on the hot path.

**Done:** a `/review` turn routes to Opus and shows a thinking trace; plain chat + a
"what do I own" query stay on Sonnet with no thinking; the toggle forces On/Off and Auto
falls back to intent routing. Probe: intent→(model, thinking, effort) mapping resolves as
specified, and the toggle overrides it.

## Phase 5 (optional) — Batch API for the weekly review

The Monday review is non-interactive → use `client.messages.batches` (≈50% cheaper) for
it and any other scheduled, non-streaming run. Keep interactive chat on the live API.

## Constraints

- Files ≤100 lines; `async def`; ruff-100; the LLM package has **no `app.` imports**
  (keep the agentic loop in concierge).
- Fail-open: a Claude error must fall through the gateway's existing fallback chain.
- Every phase ships a probe + `just` recipe + doc update in the same session.

## Build order

Phase 1 → Phase 2 (do with orff-tool-calling Phase 2) → Phase 3 → Phase 4 → Phase 5.
1 and 3 are independent wins; 2 is the load-bearing one and shared with the tool-calling
handoff. One phase per session; review the plan before code, the diff before merge.
