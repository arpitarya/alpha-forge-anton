# Phase-0 contracts (engine↔UI single source of truth)

The shared shapes every later phase reads and writes. The **Pydantic models are the source
of truth**; the frontend TS types are **generated** from them and kept honest by a drift
test — they can never silently diverge. No trading logic lives here, only contracts.

Module: [backend/app/modules/contracts/](../backend/app/modules/contracts/) ·
Generated TS: `frontend/src/modules/contracts/*.types.ts` (do not hand-edit).

## The six domains (one file each)

| File (`backend/app/modules/contracts/`) | Models | What it carries |
|---|---|---|
| `objective_contract.py` | `Objective`, `DrawdownGuard`, `SelfFunding`, `CapitalStructure` | The **program mandate** — aim, `calmar_target=3`/`calmar_floor=2`, drawdown guard rails (`soft=−12`, `hard=−20`), horizon, risk tolerance, the self-funding ledger, and the capital structure (`reserve` is **LOCKED**). Read-only on the live surface; editable only in Goals. Distinct from `signals.objective_config.Objective` (the monthly ₹ swing target). **`self_funding.covered` resolves once a realised-P&L source exists (Gate-4 paper) — it is honest-pending (`None`) until then; cage savings reduce opex, they are not income.** Served live at `GET /mandate` (loaded from the elgar store at runtime, `opex_per_month` filled from the funding registry — see [track-u-ui.md](track-u-ui.md) Phase 3a). |
| `testreport_contract.py` | `TestReport`, `Walkforward` | The edge funnel's verdict — gates passed, PBO, deflated Sharpe, the multiple-testing haircut, the walk-forward summary, the pass/fail verdict, and the pre-registration anchor. Self-describing for a real run: `data_provenance` (nse-bhavcopy vs synthetic-fixture), `date_from`/`date_to`, `quality_status` (`validated` / `disabled-pending`) + `quality_pending`, and `universe_status` (per-rebalance-liquid). |
| `cone_contract.py` | `Cone` | A forward outcome cone — p5/p50/p95 paths shown **downside-first** (`es_p5`, the worst-case expected shortfall, leads), confidence, and a `stale` flag so a cone is never presented as fresh when its feed is not. |
| `approval_contract.py` | `ApprovalProposal`, `Calibration` | What Orff puts in front of the human — thesis, notional, the **largest/required** expected shortfall (shown before the upside), stress, a red-team list, the mandatory `tenth_man` dissent, runner-ups, tripwires, the calibration scoreboard, and a cooldown. |
| `decision_contract.py` | `DecisionRow` | A decision-journal row — the proposal seen, the **downside that was shown**, approve/veto, the outcome, and `replayable` (the inputs were captured well enough to re-run the call). |
| `feedstate_contract.py` | `FeedState` | Feed liveness — `live`/`stale`, `last_tick`, reason. **honest-pending** is `last_tick=None` (never a faked live `0%`); derived metrics carry `\| None` rather than defaulting to `0`. |

## Codegen + the drift guard

`contracts_codegen.py` emits one self-contained `{domain}.types.ts` per model (nested
`$defs` inlined, `Literal`→string-union, `datetime`/`date`→`string`, `T | None`→optional)
plus an `index.ts` barrel that re-exports each *root* type from its canonical file (so a
shared nested model like `ApprovalProposal` never collides in the barrel).

```bash
just contracts-gen     # regenerate the TS after changing a model
```

`tests/test_contracts_sync.py` regenerates each file in-memory and asserts byte-equality
with the checked-in `.ts`. **Change a model and forget `just contracts-gen` ⇒ the test
fails.** That is the entire sync guarantee — $0, deterministic, no runtime dependency.

## Not all shapes are codegen contracts

A **frozen engine↔UI contract** (`Objective`, `TestReport`, `Cone`, …) lives here and is
codegen'd. A **view-model that evolves with a surface** — the cockpit's `FlowState`
(`app/modules/flow/flow_schema.py`) or `goals.api`'s `EdgeSummary`/`RecentRun` — is
hand-mirrored in TS next to its fetcher (`flow.types.ts`, `goals.api.ts`), deliberately
**outside** the codegen barrel. Rule of thumb: if it's a stable shape multiple phases
read/write, add it to `contracts_codegen.MODELS`; if it's a per-surface view that changes
as the feature grows, hand-mirror it and keep it local.
