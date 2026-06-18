# Handoff — Agent-initiated deep search (Orff asks before spending)

**For:** Claude Code, in the `anton` repo. **Plan first, stop for review, then build.**
**Builds on:** the shipped tool-calling loop (`tool_layer.py`, `tool_registry.py`,
`tool_executor.py`) and `grounding_service.py` (Parallel, budget-capped, Cage-metered).
**Canonical spec** for this feature — supersedes the inline "Agent-initiated deep search"
note in `orff-tool-calling.handoff.md`.

> **Status — shipped (both phases).**
> **Phase 1 (backend):** `request_deep_search` registered (confirm-gated, trusted-lane, own
> class); `deep_search_service.py` builds the card (no call) + runs the confirmed queries via
> `grounding_service.run`; `deep_search_mode` (auto/always/never) threaded request →
> `Assembled` → `tool_layer`; the always-on `grounding_service.inject` retired; system prompt
> instructs the call; apply target `POST /concierge/deep-search`. Verified by
> `just probe deep-search` (all §Acceptance rows); `concierge-tools` + `holdings-disclosure`
> green, `dante-pii` clean.
> **Phase 2 (frontend):** the on/off toggle is replaced by the tri-state **Auto / Always /
> Never** control (`DeepSearchMode.tsx`), sending `deep_search_mode` and persisting it to
> `localStorage["af-deep-search-mode"]` via `ChatContext`; `ApprovalCard` now renders the
> reasons + cost line. Verified by `just probe ui-deep-search` (CDP :9299, fixture-served,
> 13/13): the control renders + sends the mode, an Auto gap raises the card with reasons +
> cost, and Approve dispatches `POST /concierge/deep-search`.

> No personal figures in the repo. Interfaces, params, rules only.

## Objective

Replace the manual `web_grounding` on/off toggle with an **agent-initiated, confirm-gated**
flow. The user shouldn't have to predict whether a prompt needs fresh web data — Orff notices
the gap mid-answer and asks, naming its reasons and the cost. No spend without confirmation.

Behaviour:
```
user asks → Orff (mid-answer) realises it lacks current web data
  → calls request_deep_search(reasons, queries)
  → {confirm} card: the reasons + the exact queries + "~₹0.5 · ₹X of ₹<budget> used"
  → NO Parallel call yet
     ├─ confirm → grounding_service.run(...) → results returned as tool_result → Orff finishes
     └─ reject  → no call → Orff answers from free sources and says what it couldn't verify
```

## What already exists (reuse, do not rebuild)

- `concierge/tool_registry.py` / `tool_executor.py` / `tool_layer.py` — the trusted-lane
  tool loop (reads auto-run; mutating tools emit `{confirm}` + pause; `tool_result` re-invoke).
- `concierge/grounding_service.py` — `run(query, kind=...)` does one Parallel call, records a
  Cage receipt, and already computes month-to-date Parallel spend vs the budget.
- `ApprovalCard.tsx` + `action_service.py` — the confirm-card pattern (renders reasons/steps).
- The SSE protocol already emits `{confirm:{…}}` and `{tool:{…}}` — no new event types needed.

## Design

### The tool
`request_deep_search(reasons: str, queries: list[str])` — registered in `tool_registry`,
**confirm-gated and trusted-lane only** (same class as the mutating tools, though it writes
nothing). Orff calls it when it recognises a fresh-data gap; this is the model spotting its
own gap — **no separate classifier call** on the hot path.

### The confirm card
On the call, the executor emits `{confirm}` with:
- `summary` = the `reasons` (human-readable why),
- `steps` = the `queries` (exactly what would be searched),
- `detail` = cost line: `~₹0.5 · ₹<mtd> of ₹<budget> used this month` (read mtd + budget the
  way `grounding_service.inject` already does).
The ask makes **no Parallel call** — it's free until confirmed.

### Confirm / reject
- **Confirm** → executor runs `grounding_service.run(query, kind=...)` for the queries,
  returns results as the `tool_result`, Orff continues. One Parallel call → one Cage receipt.
- **Reject** → no call; Orff answers from free sources and states what couldn't be verified.

### The mode (replaces the toggle)
`deep_search_mode` on the request, mirroring how `web_grounding` was carried — tri-state:
- **Auto** (default) — Orff asks via the card on a detected gap.
- **Always** — when Orff would call the tool, the executor runs `grounding_service.run`
  **without** a card (auto-confirm).
- **Never** — the tool is not offered / is a no-op; free sources only.

### System prompt
Instruct Orff to call `request_deep_search` — with concrete reasons — when a query needs
current web data it lacks, rather than guessing or answering from stale knowledge.

### Retire the old path
Remove the always-on `req.web_grounding` inject (`grounding_service.inject`); keep
`grounding_service.run` + the budget check as the shared executor the tool calls.

## Constraints

- Files ≤100 lines; `async def`; ruff-100; the LLM package keeps **no `app.` imports**.
- **Fail-open** (touches the live chat path): a grounding error → a free-source answer, never
  a dead stream. Over budget → the card says so / the run is skipped, never an error.
- Trusted tool-calling lane only (where Parallel + the tools live).
- Every change ships a probe + `just` recipe + doc update in the same session.

## Acceptance / probes

- **Auto:** a fresh-data query emits a `request_deep_search` confirm card with reasons +
  cost and makes **no** Parallel call until confirm.
- **Confirm:** one Parallel call + one Cage receipt; results reach the answer.
- **Reject:** zero calls; the answer proceeds from free sources.
- **Always:** runs `grounding_service.run` with no card. **Never:** never asks, never calls.
- **Budget:** over the monthly cap, the card/flow degrades to free sources and says so.
- `holdings_disclosure_probe` still green; `just dante-pii` clean.

## Build sequence

1. **Backend** — the tool + confirm + `deep_search_mode` + system-prompt instruction + retire
   the old inject path. Probe per §Acceptance.
2. **Frontend** — swap the on/off toggle for the tri-state `deep_search_mode` control
   (Auto default); the confirm card already renders via ApprovalCard. CDP probe (real Chrome,
   fixture-served) asserting the control sends the mode and an Auto gap shows the card.

Phase 1 first; verify the confirm event before the frontend. One phase per session.
