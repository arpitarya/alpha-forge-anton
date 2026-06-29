# Process-Flow Cockpit (`/flow`)

The locked 8-stage process flow — **Idea → Rule → Test → Range → Plan → Red-team →
Approve → Live → Watch** — built as the operating cockpit of Orff. The entire edge
lifecycle, *including authoring new edges*, happens in the UI. This is a **view over
edge state, not a new engine**: the deterministic funnel/gates stay server-side; the
cockpit orchestrates, displays, and captures human decisions.

Spec: `elgar://plan/handoff-process-flow-cockpit` (private). Built in stages, in flow order.

## Stage (a) — Cockpit spine + Idea/Rule  ✅ shipped

The spine renders all 9 locked nodes with the selected edge's **real** per-stage status,
and a UI to **author a complete `EdgeSpec` and pre-register it to elgar**.

### Backend — `app/modules/flow/` (mounted at `/flow`)

| File | Role |
|------|------|
| `flow_schema.py` | `StageId` (9), `StageState` (`done/active/pending/na/blocked`), `StageStatus`, `FlowState`, `EdgeListItem`, `AuthorEdgeRequest` |
| `flow_stages.py` | The locked stage table + **deterministic** status derivation from `EdgeSpec` + latest `JournalRecord` (pure, no clock/I/O) |
| `flow_author.py` | Build the spec, **server-stamp `pre_registered_at`**, freeze guard, `edge_store.save` |
| `flow_templates.py` | Idea-stage templates — Family A/B authorable, **C scaffolded** (`available=false`, engine deferred) |
| `flow_service.py` | Read side — list edges (journal ∪ UI-authored specs) + assemble one `FlowState` |
| `flow_routes.py` | `GET /flow/stages·templates·edges·edges/{id}` · `POST /flow/edges` |

**Routes** (all auth-gated):

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/flow/stages` | The 9-node skeleton (labels + order) |
| `GET` | `/flow/templates` | Idea candidates (Family A/B/C) |
| `GET` | `/flow/edges` | Every cockpit edge + its furthest stage |
| `GET` | `/flow/edges/{id}` | One edge's 9-stage `FlowState` (404 if unknown) |
| `POST` | `/flow/edges` | Author + pre-register (201; **422** if frozen; **503** if store unreachable) |

### How stage status is derived (honest by construction)

- **Idea** → `done` (a candidate exists). **Rule** → `done` once `pre_registered_at` is set
  (`frozen` once a run exists), else `active` (draft).
- **Test** → `done` with `Gate N · PASS/KILL` when a journal run exists; else `active`.
- **Range → Watch** → **`na`** (honest-pending — "lands in a later slice"), or **`blocked`**
  when a KILL gates the downstream off. Never a faked `done`.

### Source of truth for "what edges exist"

The journal is the truth for **what ran** (keyed by run `edge_id`, e.g. `edge-001`, whose
embedded `TestReport` carries `pre_registered_at`). The cockpit lists the **union** of
journal edges and UI-authored specs that round-trip through `edge_store` (a JSON-block
doc). A hand-authored markdown spec with no JSON block is not a machine edge — it does not
appear. The cockpit **debuts on edge-001** (a real KILL).

### Pre-registration freeze

`pre_registered_at` is **server-stamped** on save (never client-supplied). Re-authoring an
edge that already has a journal run is rejected (`EdgeFrozenError` → HTTP 422) — a
hypothesis edited after seeing a result is invalid (`edge_register`, the discipline anchor).

### Frontend — `src/modules/flow/` + `/flow`

`FlowCockpit` (spine: edge picker + rail + stage detail) · `FlowStages` (the rail) ·
`FlowStageDetail` · `FlowAuthorPanel` → `IdeaTemplates` + `EdgeAuthor` (author + pre-register).
View-models in `flow.types.ts` are **hand-mirrored** from `flow_schema.py` (a view, not a
frozen contract — outside the codegen barrel, like `goals.api`'s `EdgeSummary`). Styles:
`src/app/forge-flow.css` (reuses `.of-*` primitives; honest-pending via `.of-pending`).
Nav: a **Flow** item added to `TerminalTopBar` (Terminal stays the landing page).

**Authoring scope (stage a):** the form captures only the fields the engine consumes today
(hypothesis, signal, holding period, universe, factor knobs). Sizing · exits · rebalance
cadence are **later-stage artifacts** — shown honest-pending, not faked into the spec.

### Verification

- `probes/flow_author_probe.py` — `just probe flow-author` (standalone, no CDP): 9-node order,
  template availability, honest derivation, server-stamp, freeze, determinism.
- `probes/ui_flow_probe.py` — `just probe ui-flow` (CDP :9299): all 9 stages render for
  edge-001 (Test = KILL, downstream BLOCKED); "New edge" opens the author panel (Family A/B/C,
  C disabled). Requires the running stack + Chrome on :9299.
- `tests/test_flow_stages.py` — the deterministic spine + authoring freeze (no elgar I/O).

## Stage (b) — Test/Range  ✅ shipped

The **Test** stage triggers the funnel (Gates 0–3) as an **async server-side job**; the
**Range** stage renders the Gate-3 outcome cone, downside-first. Deterministic, $0, LLM-free.
Debuts on **edge-001** (`factor_volscale` for edge-002 isn't merged → run debuts on edge-001).

### Backend (`app/modules/flow/`)

| File | Role |
|------|------|
| `flow_run.py` | Resolve the spec (edge-001 → the pinned `edge_001()`; else `edge_store.load`) + run the funnel against the **real nse-bhavcopy panel** with the exact `eb0_real` params, in a worker thread (`asyncio.to_thread`, never blocks the loop), then journal. `gates_from_report` derives per-gate progress. |
| `flow_jobs.py` | In-memory async job registry — `start`/`get`/`latest_for`, **no double-run** per edge. The POST returns immediately; the cockpit polls. |
| `flow_run_schema.py` | `RunPhase`, `GateProgress` (gate/label/state), `RunStatus` (phase, gates, `TestReport`, `Cone`, signature). |
| `flow_run_routes.py` | `POST /flow/edges/{id}/run` (202) · `GET /flow/runs/{job_id}` · `GET /flow/edges/{id}/run` (latest). |

**Determinism contract:** a UI-triggered run is **byte-identical** to the CLI run — edge-001
reproduces its KILL with the same `signature` across runs (`flow_run_probe --heavy`). The funnel
is invoked whole; **gate internals are never rewritten**. Per-gate progress is derived from the
completed `gates_passed`: Gate-0 passed (the panel is Gate-0 clean), the killer gate `failed`,
the rest `skipped`.

**Honest derivation update:** a **KILL gates Plan→Watch** (you don't size, red-team, approve, or
trade a dead edge) but **NOT Range** — the funnel computes the cone on every run, and the
downside-first cone is informative even for a killed edge.

### Frontend (`src/modules/flow/`)

`TestRunPanel` (Run button → polls the job → the 4 gates resolve → verdict + determinism
signature) · `RangeConePanel` (the **real** `Cone`, downside-first: worst-case `es_p5` loud and
red, a minimal SVG band from the real p5/p50/p95 paths — percent space, **no ₹**; honest-pending
until run; stale guard) · `flow.cone.ts` (SVG points from the arrays). `FlowStageDetail` branches
to these for the Test and Range stages.

### Verification

- `probes/flow_run_probe.py` — `just probe flow-run` (fast: gate mapping + job no-double-run);
  `--heavy` adds the ~30s determinism check (edge-001 KILL + identical signature + cone).
- `tests/test_flow_run.py` — gate derivation branches + the job lifecycle (mocked, fast).
- `probes/ui_flow_probe.py` — extended: Test renders the 4 gates (gate-1 FAILED) + FAIL verdict;
  Range renders the downside-first cone.

## Stage (c) — Plan (position sizing)  ✅ shipped

Deterministic position sizing for a **surviving** edge — four constraints, the **binding
(smallest)** one wins, so no single assumption can over-size. **Shown for approval, never
auto-applied, never an order.** $0, LLM-free, no I/O.

| Constraint | Bound |
|------------|-------|
| **fixed-risk** | `capital × risk% / stop%` — a stop-out loses a fixed fraction of capital |
| **downside cap** | `capital × max_loss% / guard%` — a catastrophic guard breach loses ≤ max_loss% (mandate soft −12 / hard −20) |
| **ADV liquidity cap** | `participation% × ADV` — stay a small share of a day's volume (0 ADV → dropped) |
| **fractional-Kelly** | `kelly_fraction × max(0, p − (1−p)/b) × capital` — de-risked Kelly |

Backend: [flow_sizing.py](../backend/app/modules/flow/flow_sizing.py) (pure engine) +
[flow_sizing_schema.py](../backend/app/modules/flow/flow_sizing_schema.py) +
`POST /flow/sizing` ([flow_sizing_routes.py](../backend/app/modules/flow/flow_sizing_routes.py)).
Frontend: [PlanSizingPanel.tsx](../frontend/src/modules/flow/PlanSizingPanel.tsx) — capital + ADV
inputs, the four constraints with the **binding one highlighted**, the recommended notional + %,
and the "never auto-applied" disclaimer.

**Gating:** Plan is `ACTIVE` only for a **passing** edge (sizing unlocks on survival), `BLOCKED`
for a kill ("no position to size"), `NA` for an un-run edge. Since no edge passes yet (base rate
0/1), Plan is honest-pending for edge-001 — correct, not a bug.

**Verification:** `just probe flow-sizing` (formulas, binding=min, clamp, 0-ADV drop, determinism,
Plan-unlocks-on-pass) · `tests/test_flow_sizing.py` · the CDP probe exercises Plan on a synthetic
surviving edge (the constraints + binding render).

Worked-example ₹ only (the human sets their capital); the sizing output is a runtime recommendation
shown in the UI, never journaled/committed to this repo.

## Stage (d) — Red-team (the only LLM stage)  ✅ shipped

A two-tier critique of a **surviving** edge — the **only LLM call in the flow**, cage-metered by
the gateway and **OFF the deterministic number path** (the funnel/cone/sizing never import it; it
critiques numbers handed to it read-only, never recomputes them).

- **Tier 1 — evidence critic:** severity-tagged objections (high/med/low) about the statistics
  (overfitting, deflation, the multiple-testing haircut, walk-forward, the worst-case cone, the size).
- **Tier 2 — 10th-Man:** a forced dissent — the single strongest case AGAINST proceeding even if
  every number looks clean.
- Plus **runner-ups** (alternatives) and **tripwires** (live invalidation conditions).

Backend: [flow_redteam.py](../backend/app/modules/flow/flow_redteam.py) calls
`create_gateway().complete()` (auto-recorded to the **cage** ledger), parses strict JSON with one
repair round, sorts objections by severity, and **caches per edge** (the LLM costs money — no
re-bill on re-view). The run is a background job (never blocking). Prompt:
[flow_redteam_prompt.py](../backend/app/modules/flow/flow_redteam_prompt.py); evidence assembled in
[flow_redteam_routes.py](../backend/app/modules/flow/flow_redteam_routes.py) from the run + cone +
sizing. `POST/GET /flow/edges/{id}/redteam`. Frontend:
[RedteamPanel.tsx](../frontend/src/modules/flow/RedteamPanel.tsx).

**Shapes:** a NEW `RedteamReport` (explicit `severity` objects) — additive, **not** a change to the
public `ApprovalProposal` contract (stage e bridges them). Gated `ACTIVE` only on a PASS.

**Verification:** `just probe flow-redteam` (mocked gateway — parse, severity sort, repair round,
cache, **and that the module imports no funnel/sizing engine**) · `tests/test_flow_redteam.py` · the
CDP probe renders objections + 10th-Man + metering attribution. Real LLM calls happen at runtime,
cage-metered; the probes never bill.

## Stage (e) — Approve (decision capture)  ✅ shipped

A **binary** decision on a surviving edge — **Approve-as-proposed** or **Veto-with-reason** —
**downside-first** and **ack-loss-first**, with a logged cooldown and an execution checklist on
approve. The decision **journals to the private elgar store** (`decisions` collection). **Nothing
here places an order** — it records the human's call; Live (stage f) prepares the orders.

- **Downside-first:** the proposal leads with the worst-case ₹ loss (`notional × hard-guard%`,
  the −20% guard), assembled deterministically from sizing — not the LLM.
- **Ack-loss-first:** APPROVE is **refused** (`DecisionError` → 422) unless the human acknowledged
  that loss; the UI checkbox gates the button.
- **Veto needs a reason**, and the free-text reason is **PII-guarded** before it reaches elgar —
  `critic_guard.pii_block` (the same deterministic PAN/Aadhaar/account block as `append_memory`,
  exposed as a reusable function; the brief mandates a runtime PII guard on free-text writes).
- **Cooldown:** a decision server-stamps `cooldown_until` (1h); a re-decision inside it is 409.
- **Exec checklist on approve:** discipline steps (ack the loss, size to the binding constraint,
  place the entry *yourself*, set the staged −12/−20 guard) — **Orff never places the order.**

Backend: [flow_approve.py](../backend/app/modules/flow/flow_approve.py) (proposal + checklist +
ack/PII/cooldown decide), [flow_decision_store.py](../backend/app/modules/flow/flow_decision_store.py)
(**fail-loud** elgar write — a 503 if the store is unreachable, unlike best-effort discovery writes),
[flow_decision_schema.py](../backend/app/modules/flow/flow_decision_schema.py),
`GET /flow/edges/{id}/approve` + `POST /flow/edges/{id}/decision`. Frontend:
[ApprovePanel.tsx](../frontend/src/modules/flow/ApprovePanel.tsx) +
[ApproveActions.tsx](../frontend/src/modules/flow/ApproveActions.tsx). The proposal reuses the public
`ApprovalProposal` contract.

**Verification:** `just probe flow-approve` (proposal downside-first, checklist never orders, ack-gate,
veto-needs-reason, **PAN blocked before elgar**, cooldown stamp — elgar write mocked) ·
`tests/test_flow_approve.py` · the CDP probe asserts Approve is disabled until the loss is acknowledged.
Real decisions journal to elgar at runtime; the probes never write.

## Stage (f) — Live (human-placed orders + reconciliation)  ✅ shipped

The **hard invariant**: Orff **prepares** the exact orders + a checklist for the human to place
and **reconciles** the fills — it **NEVER places a broker order and never auto-executes** (product
law, `you-say-yes` / `start-small`). Unlocks only for an **approved** edge.

- **Order plan** ([flow_live.py](../backend/app/modules/flow/flow_live.py) `build_plan`): a copy-only
  list — the **entry** sized to the *exact approved notional* (persisted on the decision) + the
  staged **−12% de-risk / −20% flatten** guard + an execution checklist ("copy each order into YOUR
  broker… Orff never places an order").
- **Reconciliation** (`reconcile`): **manual fill entry** (you enter what you actually got filled at
  — no broker call, no live-auth dependency) → true P&L, **slippage vs the planned notional**, and
  the staged guard lights (soft ≤ −12%, hard ≤ −20%).

Routes: `GET /flow/edges/{id}/live` (order plan, gated on an *approved* decision → 409 otherwise) ·
`POST /flow/edges/{id}/reconcile` (fills → true P&L). Frontend:
[LivePanel.tsx](../frontend/src/modules/flow/LivePanel.tsx) +
[ReconcileForm.tsx](../frontend/src/modules/flow/ReconcileForm.tsx) — a "never auto-executes" banner,
the copy-only orders, and the fill-entry → guard read-back.

**No broker dependency:** the Live engine **imports no broker module** and makes **no
order-placement call** — enforced by `flow_live_probe.py`. (Reconciliation reads human-entered
fills; wiring it to the live broker read/sync is a deliberate later choice.)

**Verification:** `just probe flow-live` (plan is copy-only + staged guard, true-P&L + slippage math,
guard lights at −12/−20, **no broker import / no placement call**) · `tests/test_flow_live.py` · the
CDP probe prepares the order plan and reconciles a −21% read-back into the HARD guard.

## Stage (g) — Watch (decay monitor)  ✅ shipped

A **deterministic** ($0, no LLM, no broker) live-edge decay monitor — log the realized periods and
the monitor flags decay; a decayed edge can be **decay-killed** (retired). Unlocks only on a PASS.

- **Decay signals** ([flow_watch.py](../backend/app/modules/flow/flow_watch.py) `analyze`,
  severity-tagged): realized **expectancy** going negative / collapsing vs the approved expectation;
  a cumulative **drawdown** breaching the **−12 / −20** guard; a **losing streak**.
- **Verdict:** `healthy` → `decaying` (1 MED) → `decayed` (any HIGH or ≥2 MED) ⇒ kill recommended.
- **Decay-kill** (`retire`): journals a `RetirementRecord` to elgar (fail-loud, **PII-guarded**
  reason) — and **never mutates the frozen pre-registered spec** (the freeze holds for life).

Routes: `POST /flow/edges/{id}/watch` (stateless decay read-back) · `POST /flow/edges/{id}/decay-kill`
(retire). Frontend: [WatchPanel.tsx](../frontend/src/modules/flow/WatchPanel.tsx) +
[DecayKillBlock.tsx](../frontend/src/modules/flow/DecayKillBlock.tsx). The realized series is logged by
the human (no realized-P&L source yet — honest-pending until paper trading).

**Verification:** `just probe flow-watch` (healthy→no-kill, decayed→kill + severity signals, PII-guard
on the reason, **no broker / no edge_store import** so the frozen spec is untouched, Watch unlocks on
PASS) · `tests/test_flow_watch.py` · the CDP probe logs a period, sees DECAYED, and is offered the
decay-kill.

---

## Status: all 8 process-flow stages shipped 🎉

Idea → Rule → Test → Range → Plan → Red-team → Approve → Live → Watch — every stage is working
software in the `/flow` cockpit. Edges are **authored, run, ranged, sized, red-teamed, approved,
prepared-for-execution, and decay-monitored entirely in the UI**. The deterministic spine is $0/LLM-free;
**Red-team is the only LLM stage** (cage-metered, off the number path); **Live never places an order**.
Honest-pending/blocked render wherever a real edge hasn't reached a stage (base rate 0/1 — correct).
