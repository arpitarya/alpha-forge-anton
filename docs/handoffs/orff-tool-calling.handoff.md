# Handoff — Orff tool-calling + Objective component (combined)

**For:** Claude Code, in the `anton` repo. **Plan first, stop for review, then build.**
**Scope:** two linked features that ship together —
1. **Tool-calling** so Orff *acts* (reads plans/signals, makes confirmed mutations)
   instead of punting. The logs show it asked to "fetch the latest plan" and replied
   *"I can't run `elgar get` from here, run it in your terminal."*
2. **Objective component** — a structured north-star (monthly ₹ target, horizon, risk,
   mission) that deterministic code measures against, surfaced as its own tab in the
   chat popup and edited via a tool (so it reuses the same confirm-card path).

They're combined because the Objective is both injected context **and** a tool target
(`get_objective` / `set_objective`), so building them together avoids two passes over
the same registry + approval plumbing.

> No personal figures in the repo. Percentages, interfaces, rules only — the objective's
> *values* (the ₹ target) live in the elgar doc, never committed here.

## Objective

Give Orff a small, safe tool layer with two tiers:

1. **Read tools — auto-run, no confirmation.** Orff calls these to answer, surfacing
   each as a ToolTrail step (the stream already renders `{tool:{...}}` events).
2. **Mutating tools — ALWAYS via the existing ApprovalCard confirm flow.** Orff
   proposes the exact change; the user taps Confirm; only then does it write. Never
   a silent mutation. (`ApprovalCard.tsx` + `action_service` already implement this.)

## What already exists (reuse, do not rebuild)

- `plans/plan_loader.py` (`load_plan`, `available_plans`), `plans/plan_routes.py`
- `plans/plan_drift.py` (`drift_for_plan`), `plans/projection_service.py`
- `signals/review_service.py` (`/signals/review`), `signals/screen_service.py`
- `signals/plan_store.py` (`latest`, save to elgar `actions/`), `signals/plan_diff.py`
- `signals/strategy_config.py` (`load_config`), `signals/strategy_tuning.py` (config change via ApprovalCard)
- `concierge/action_service.py` + `ApprovalCard.tsx` — the confirm-card pattern
- `concierge/memory_service.py` — `load_context` (reads the memory docs), `save_memory`
- `concierge/MemoryPanel.tsx` — the popup-panel pattern the Objective tab clones
- `signals/pnl_tracker.py` — realized-P&L tracker that will read the objective's target

## Read tools to expose

| Tool | Calls | Returns |
|------|-------|---------|
| `get_plan` | `plan_loader.load_plan` | the active allocation plan + targets |
| `get_drift` | `plan_drift.drift_for_plan` | per-class drift vs plan (pts only) |
| `review_holdings` | `review_service` | the deterministic buy/hold/trim/sell ActionPlan |
| `screen_candidates` | `screen_service.build_screen` | ranked new-entry candidates |
| `get_strategy` | `strategy_config.load_config` | the active strategy knobs |
| `latest_action_plan` | `plan_store.latest` + `plan_diff` | last saved plan + what changed since |
| `get_objective` | `objective_config.load_objective` | the north-star target + month-to-date progress |

These are read-only and already privacy-safe (they go through the same disclosure
chokepoint). Run them automatically when the user's intent matches.

## Agent-initiated deep search — `request_deep_search` (confirm-gated, paid)

> **Canonical spec: [`deep-search-ask.handoff.md`](./deep-search-ask.handoff.md).** The
> summary below is kept for context; build from the standalone doc.

The user shouldn't have to predict whether a prompt needs fresh web data — Orff asks when
it notices a gap. Replaces the manual `web_grounding` toggle with an agent-initiated card.

- **Tool:** `request_deep_search(reasons: str, queries: list[str])`. Orff calls it mid-answer
  when it recognises it lacks current web data. It's the model spotting its own gap — **no
  separate classifier call**.
- **Confirm card** (reuses ApprovalCard): shows the **reasons** + the exact `queries` + the
  cost (`~₹0.5`) + remaining monthly budget (from the Cage ledger, as `grounding_service`
  already computes). The ask is **free** — no Parallel call until confirm.
- **On confirm:** the executor runs `grounding_service.run(...)`, returns results as the
  `tool_result`, Orff continues the answer. **On reject:** answer from free sources and say
  what couldn't be verified.
- **Preference (replaces the on/off toggle) — tri-state:** `Auto` (default — Orff asks on a
  gap) · `Always` (auto-run when needed, no ask) · `Never` (free sources only). Carry it as
  `deep_search_mode` on the request, mirroring `web_grounding`.
- Trusted tool-calling lane only (where Parallel + the tools already live).

## Mutating tools — via ApprovalCard only

| Tool | Writes (elgar) | Confirm card shows |
|------|----------------|--------------------|
| `set_strategy_knob` | `strategy/strategy.config.md` | "Set `trim_rule.mode = trail`?" (already built in `strategy_tuning`) |
| `edit_exclusion_list` | `plans/hard-exclusion-list` | "Add NEOGEN to your never-buy list?" / "Remove X?" |
| `update_context` | `plans/orff-context` | "Add this note to your standing context?" |
| `save_action_plan` | `actions/<date>` | "Save this plan to your ledger?" |
| `set_objective` | `strategy/objective.md` | "Update your monthly target to ₹12,000 from Jul 1?" |

Each follows the existing flow: Orff emits `{confirm:{id, action, summary, steps}}` →
user confirms → `action_service` dispatches the write (one elgar git commit) → a
ToolTrail step records it. A rejected card writes nothing.

**Mutations carry the intent; the executor owns the merge (read-modify-write server-side).**
`build_confirm(...)` stays **sync and pure** — it emits a minimal intent payload, never
the merged doc, and never does I/O:
- `update_context` → `apply.body = {"append": note}` → **`POST /concierge/memory/append`**
  (POST, not PUT — append isn't idempotent) reads `orff-context`, concatenates with a
  separator, and `save_memory`s it atomically.
- `edit_exclusion_list` → `{"add": "SPICEJET"}` / `{"remove": "X"}` → executor reads
  `hard-exclusion-list`, applies the diff, writes.
The confirm card represents the **operation** ("Append to your context: '…'") — that's the
honest unit; it does NOT need to render the full merged doc. Reserve a full-doc preview for
true replacements (set-to-this) only. The frontend never merges authoritative content.

**Resolved — update_context transport (2026-06-15):** `build_confirm` stays sync and pure,
emitting `apply.body = {"note": note}` only. The write is `POST /concierge/memory/append`
(not PUT — appending is not idempotent; two calls must produce two notes). The executor
reads `orff-context`, concatenates with a date-stamp separator, calls `save_memory` —
one atomic elgar commit. Both `update_context` and `edit_exclusion_list` follow the same
rule: minimal intent payload (append/add/remove), async executor owns the read-modify-write,
`build_confirm` never does I/O. The confirm card is honest by showing the operation ("Append
X"), not the merged doc; the user approves the diff, not the final-state blob.

### Blacklist add/remove (answers the operator's design question)

"Add a stock to the blacklist" / "remove from blacklist" is a **mutating intent**,
so it routes through `edit_exclusion_list` + an ApprovalCard — **not** a generic
"Save memory" button. The card names the exact diff ("Add SPICEJET to never-buy"),
writes to `hard-exclusion-list`, and commits. This beats a button because the command
already specifies the change; the card just confirms the precise, auditable diff.

## Objective component (the north-star tab)

**Why it's not just a Memory note:** the objective is *operative* — code measures
against it. A free-text note can't drive the monthly tracker; a typed target can. Three
layers in the popup, by reader: **Objective** (what/why — read by code), **Memory**
(durable rules — read by the model), **Strategy** (how — the signal knobs, read by code).

**Backend — `signals/objective_config.py`** (mirror `strategy_config.py`):
- Doc: `objective.md` in the elgar `strategy/` collection. YAML frontmatter:
  ```yaml
  monthly_target_inr: 2000     # the realized-profit target for the current month
  step_up:                     # optional scheduled change
    from: 2026-07-01
    monthly_target_inr: 12000
  horizon: swing               # swing | long_term
  risk_tolerance: aggressive
  mission: >                   # the free-text "why" (e.g. fund the Claude Max plan)
  ```
- `load_objective()` returns a typed `Objective`; values (the ₹) live only in elgar.
- `GET /signals/objective` returns the typed objective **+ `active_target`** (the
  `step_up` resolved by today's date). It does **NOT** return progress — there is no
  stored trades source yet, and a finance endpoint must not emit a derived figure with no
  real data behind it. No GET-with-body; when a trades source exists, GET reads it
  server-side, or add a separate `POST /signals/pnl` calculator — never a GET body.

**Wiring:**
- `progress_pct` lives on `RealizedReport` in `pnl_tracker` (next to `vs_target`), as one
  pure formula `net/target*100` — `target==0 → 0`, **raw and allowed-negative** (a losing
  month reads negative; don't clamp). Any display cap is frontend-only (clamp the bar
  width, not the value). The probe tests it via `pnl_tracker.realized_pnl(trades, costs,
  target=active_target)` directly on fixtures.
- `pnl_tracker.py` reads `monthly_target_inr` (resolving `step_up` by today's date). The
  weekly review and `/review` cite progress once a trades source feeds them.
- `plan_context` / `prompt_service` inject the objective at the **top** of context
  (above memory) so Orff always optimizes toward it.

**Frontend — `ObjectivePanel.tsx`** (clone `MemoryPanel.tsx`):
- New tab in the chat popup beside Memory. Shows target, horizon, mission. For progress:
  render an honest **"MTD pending"** state (a distinct state, NOT a 0%-width bar) until a
  trades source exists — `GET /signals/objective` returns no P&L, so there is nothing to
  fill from. When trades land, this flips to a real bar; don't animate up from a
  misleading zero. Editable; edits go through `set_objective` → ApprovalCard → elgar commit
  (never a silent write), same as every other mutation here.

## Build sequence

1. **Objective backend** ✅ — `objective_config.py` (`Objective` + `StepUp` models, `active_target()`, `context_text()`) + `objective_loader.py` (elgar → seed → defaults) + `objective.md` seed (figure-free) + `GET /signals/objective` (typed objective + `active_target`, no P&L) + `pnl_tracker.py` wiring (`progress_pct` on `RealizedReport`, `monthly_target()` fallback) + prompt injection above memory in `prompt_service.py`. `StrategyChange` + `PnlRequest` moved to `signal_schema.py`. Probe: `just probe objective` — 16 checks green; `dante-pii` clean.
2. **Tool layer (trusted lane only)** ✅ — native function-calling on `claude-sdk`; `tool_registry.py` (12 schemas), `tool_executor.py` (7 read + 5 mutating dispatch), `tool_layer.py` (agentic loop, MAX_ROUNDS=5), `exclusion_service.py`, `objective_tuning.py`, `append_memory()` in memory_service, `tool_routes.py` (POST /memory/append + POST /exclusion), POST /signals/objective, claude_sdk.py tools pass-through. `concierge_service.py` integrates tool_layer before gateway.stream; text-based detectors guarded by `if not tool_events`. Probe: `just probe concierge-tools` — 18 checks green; `dante-pii` clean.
3. **Frontend** ✅ — `ObjectivePanel.tsx` (clones `MemoryPanel`'s `PanelFrame`; read-only
   `useObjective()` in `concierge.objective.ts` → `GET /signals/objective`, **no PUT**) as a
   new tab beside Memory in `ChatRail.tsx` (`TargetIcon` NavBtn + `panel === "objective"`
   branch). Shows `active_target` + `step_up` note, horizon/risk chips, mission, and progress
   as a **distinct pending state** (`data-progress="pending"` dashed/striped track) — never a
   0%-width bar (a 0% fill reads "you're failing"; the truth is "no trades source connected
   yet", so it flips to a real bar when trades land rather than animating up from a misleading
   zero). Edits route the change as a chat prompt → `set_objective` → ApprovalCard → elgar
   commit; the panel never writes. Tool/confirm events stay surfaced by the existing thread
   (`ToolTrail` + `ApprovalCard`). Probe: `just probe ui-objective` (CDP :9299, real Chrome
   render, `GET /signals/objective` **fixture-fed** + confirm SSE mocked — hermetic data, real
   render; not the live data plane, not a headless mock). The `progress_pct` math stays the
   pure `objective_probe` (`pnl_tracker`) unit layer — not duplicated in the UI probe.

## Constraints

- Files ≤100 lines; `async def`; absolute `app.` imports; Pydantic v2; ruff-100.
- Tool registry is the single source of truth (mirror the `concierge.registry`
  manifest pattern) — names + schemas authored once, read by Python and the frontend.
- Read tools never mutate; mutating tools never run without a confirmed card.
- All tool I/O best-effort: a tool error becomes an SSE error event + a graceful
  message, never a dead stream (matches `stream_chat`'s existing try).
- Every change ships a probe + `just` recipe + doc update in the same session.

## Acceptance / probes

- A probe asserting: a read-intent prompt triggers the matching read tool and a
  ToolTrail step; the answer no longer says "run it in your terminal".
- A probe asserting: "add X to blacklist" emits a `confirm` event and writes
  `hard-exclusion-list` **only** after confirm; a rejected card writes nothing.
- A probe asserting: `get_objective` returns `active_target` with a future `step_up`
  resolving to the current target; and, separately, `pnl_tracker.realized_pnl(...)`
  computes `progress_pct` correctly on fixtures (target=0 → 0; a net-loss fixture → a
  negative pct, not clamped). `get_objective` does not return progress.
- A probe asserting: "set my monthly target to ₹12,000" emits a `confirm` event and
  writes `objective.md` **only** after confirm.
- A probe asserting deep-search: a fresh-data query in `Auto` mode emits a
  `request_deep_search` confirm card (reasons + cost, **no Parallel call yet**); confirm →
  one Parallel call + one Cage receipt; reject → zero calls, answers from free sources;
  `Never` mode never asks; `Always` runs without a card.
- `holdings_disclosure_probe` still passes (tools must not leak ₹/symbols off-lane).
- `just dante-pii` clean (no objective ₹ values committed to the repo).

## Shipped this session (context-grounding fix, prerequisite for the above)

The chat logs showed a context split-brain: `memory_service.load_memory()` read only
`orff-context` (which was empty), while `investor-profile`, `trading-sleeve-rules`,
`hard-exclusion-list`, and `portfolio-snapshot` were never injected — so Orff ran with
zero durable context and contradicted live data (HDFC "47%" vs live 21%, "NEOGEN +38%"
vs +49%). Fixed:
- `memory_service.load_context()` (new) concatenates all standing-context docs, best-effort
  per doc; `prompt_service` now injects it. `load_memory`/`save_memory` stay scoped to
  `orff-context` for the Memory panel.
- Stale **position figures** stripped from the elgar docs (`portfolio-snapshot`,
  `trading-sleeve-rules`); those now defer to the live holdings disclosure. Figure-free
  rules/preferences remain.
- **Probes shipped:** `memory-context` (`memory_context_probe.py`) asserts `load_context`
  concatenates all five MEMORY_DOCS with best-effort degradation; `context-drift`
  (`context_drift_probe.py`) reads the live elgar docs and fails if any carries a position
  figure (holding qty, comma-grouped ₹ value, signed P&L, or stale ltp/avg price field).
  Both registered in `probe.sh`; run via `just probe memory-context` / `just probe context-drift`.

## Resolved — tool-calling transport

**Native function-calling on the trusted (`claude-sdk`) lane only, for this build.**
That's where private holdings/plan data already routes, so tools that touch real data
stay on the lane cleared to see them — no off-lane leakage risk to design around.

**Free-provider tools are an explicit follow-up** (not this PR). When built, they use a
provider-agnostic JSON-tool protocol (parse a structured tool-call block from the model
text), and — because free providers are untrusted — they get **only the privacy-safe
read tools** (percentages/points: `get_drift`, `get_strategy`, `get_objective`). The
data-bearing read tools (`review_holdings`, `latest_action_plan`) and **all** mutating
tools remain trusted-lane-only, permanently. Track the follow-up as a separate handoff.

Implication for this build: gate the tool layer behind the trusted provider; a
non-trusted provider simply gets no tools (today's behaviour), never a degraded path.

**Known divergence (2026-06-16, reviewer-accepted):** `tool_layer.run()` drives the loop with
its own `anthropic.AsyncAnthropic` client rather than `gateway.complete(tools=).tool_calls`, so
trusted-lane tool usage is **not** recorded into the Cage ledger and the adapter's `tool_calls`
field is unused by the loop. Unifying on the gateway requires `Message`/adapter to round-trip
`tool_use`/`tool_result` turns. Tracked in `docs/claude-sdk-upgrade.handoff.md` §Phase 2 status.
