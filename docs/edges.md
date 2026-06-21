# Edge-discovery engine (gates 1–2 + journal)

A deterministic, typed, tested loop that takes a **pre-registered hypothesis** and
runs it through the first two validation gates, journaling every outcome. **No LLM ever
computes a number** — all math is pure Python over `signals`' existing cost model. This
is a *separate concern* from the Phase-5 `signals.backtest`, which replays the *active*
strategy config; this engine discovers *new* edges from registered hypotheses.

Module: [backend/app/modules/edges/](../backend/app/modules/edges/). Slice 1 builds
gates 1–2 + the journal only — Monte Carlo, paper-trade, and live are later slices.

## The edge doc (schema)

An edge is a pre-registered hypothesis ([edge_schema.py](../backend/app/modules/edges/edge_schema.py)):

| Field | Meaning |
|---|---|
| `id`, `hypothesis` | identity + the claim being tested |
| `universe` | symbols the signal trades |
| `signal` | id into the deterministic signal registry ([edge_signal.py](../backend/app/modules/edges/edge_signal.py)) |
| `holding_period_days` | fixed hold per round-trip |
| `expected_edge_pct` | the per-trade % after costs the author expects |
| `pre_registered_at` | **the discipline anchor** — must predate any recorded result |
| `status` | candidate / paper / live / retired |
| `gate_reached` | highest gate cleared so far |

Result stats (`ResultStats`): expectancy, hit_rate, turnover, max_dd, calmar — carried
in a `GateResult` with no clock, so the **same spec + same bars ⇒ byte-identical** output.

### Constitutional storage — elgar only

The edge doc is money/strategy content, so it lives in the **private elgar store**
(collection `edges`), referenced from this repo only as `elgar://edge/<id>`. It is
**never committed to anton** (the `plan-store` constitutional rule). The store I/O reuses
the best-effort `plans.elgar_bridge`; see [edge_store.py](../backend/app/modules/edges/edge_store.py).
The journal lives in the `edges-journal` collection and carries **stats + counts only**
(no holdings, no ₹ PII) — safe by construction.

## The two gates

**Gate 1 — out-of-sample backtest** ([edge_backtest.py](../backend/app/modules/edges/edge_backtest.py)).
Splits each symbol's history into an in-sample head and an out-of-sample tail (last 30%)
and scores **only the tail**. An edge that needs the bars it was written on is not an
edge. Pass = positive out-of-sample expectancy after costs.

**Gate 2 — walk-forward** ([edge_walkforward.py](../backend/app/modules/edges/edge_walkforward.py)).
Splits history into `n_windows+1` contiguous slices; for each adjacent pair it picks the
best param point on slice *k* (in-sample) and scores it on slice *k+1* (unseen), rolling
forward. Reports per-window Calmar + the aggregate. **Kill criterion (hard-coded for
slice 1, changed only by an explicit logged decision — not config knobs):** pass iff
**aggregate out-of-sample Calmar ≥ 0.5 AND ≥ 60% of test windows have positive
expectancy.** An edge tuned to one regime fails the consistency floor.

A deliberately **overfit** edge passes gate 1 (it fits the tail) but is **rejected at
gate 2** (its in-sample-best param does not carry to the next window) — this is the
headline acceptance test.

## The cost model

Round-trip cost ([edge_costs.py](../backend/app/modules/edges/edge_costs.py)) reuses the
signals `CostsCfg` + `pnl_tracker.realized_pnl` as the single source of truth — STCG
(~20% §111A) on short-horizon turnover, STT, and the stamp/exchange/SEBI/GST friction
bundle — and adds one knob discovery must be honest about: `slippage_pct`, charged on
both legs. Short holding periods → high turnover → these costs dominate, which is exactly
the trap a real edge has to clear.

## Pre-registration discipline

The rule that makes a result trustworthy ([edge_register.py](../backend/app/modules/edges/edge_register.py)):
`assert_pre_registered(spec, run_at)` runs **first** in `discover` and refuses
(`PreRegistrationError`) when `pre_registered_at` is missing or **later than the run** —
before any data is touched or any result journaled. **A hypothesis written after seeing
the result is rejected.**

## Data source

One seam ([edge_data.py](../backend/app/modules/edges/edge_data.py)): everything depends
on the `BarsProvider` protocol, never a concrete feed. The default `NSEDailyBars` reuses
the free NSE daily cache from `signals.backtest_data`. A paid/intraday source swaps in
here later without touching the gates.

## Run it

```bash
just edge <edge-id>                 # load elgar://edge/<id>, run gates 1-2, print verdict
just probe edge-discovery           # offline acceptance probe (no network, no store)
cd backend && uv run pytest tests/test_edge_*.py -v
```

## Verification

- `tests/test_edge_costs.py` — hand-checked net incl. STCG + slippage (qty=100, 100→110 = **+7.222%**).
- `tests/test_edge_backtest.py` — **known-answer** expectancy (−32.375%) + byte-identical reruns.
- `tests/test_edge_walkforward.py` — the **overfit edge passes gate 1 but is killed at gate 2**;
  a genuine momentum edge clears both.
- `tests/test_edge_register.py` — missing / post-result `pre_registered_at` rejected; valid passes.
- `tests/test_edge_journal.py` — PASS and KILL both journaled with the right `gate_reached`.
- `probes/edge_discovery_probe.py` (`just probe edge-discovery`) — all of the above, offline.

## Not yet (later slices)

Gate 3+ (Monte Carlo / regime stress), paper-trade, live · a capital-constrained
portfolio sim (concurrency + sizing) · promoting `status` candidate → paper → live.
