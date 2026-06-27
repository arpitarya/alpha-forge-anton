# Signals engine (Phases 1–5)

A deterministic swing-trade engine that reviews current holdings and emits a
buy/hold/trim/sell **ActionPlan**, and screens a configured universe for new
buy-candidates — **no LLM touches the numbers**. The Orff concierge only narrates
the result (Phase 3). Design of record: [signals-engine.handoff.md](handoffs/signals-engine.handoff.md).

## What Phase 1 ships

| File (`backend/app/modules/signals/`) | Responsibility |
|---|---|
| `strategy_config.py` + `strategy.config.md` | Single source of truth for every decision threshold → typed `StrategyConfig`. **No threshold is hardcoded.** |
| `quote_source.py` | yfinance 12-mo daily OHLCV; broker→Yahoo symbol map (`.NS`/`.BO`, strip `-EQ`); disk-cached 1×/day/symbol; fail-open |
| `indicators.py` | ta-lib wrappers → `Indicators` (RSI14, ADX14, DMA50/200, ATR14, 52w-pos, trailing high, vol ratio). Pure compute |
| `signal_rules.py` | **Pure** `(facts, indicators, config) → Verdict`; SELL > TRIM > ADD > HOLD, first match wins |
| `signal_schema.py` | Pydantic `Verdict` / `ActionPlan` (no clock — the determinism anchor) |
| `review_service.py` | Orchestrator: holdings → quotes → indicators → rules → sorted `ActionPlan` |
| `signals_routes.py` | `GET /signals/review`, `GET /signals/strategy` (auth-gated) |

## The ruleset (thresholds from config — §6)

1. **SELL** — `pnl_pct < stops.hard_pct` OR close below the trailing-ATR stop
   (`recent_high − trail_atr_mult·ATR`) OR (`close < DMA50` AND `RSI < exit.weak_rsi`).
2. **TRIM** — `pnl_pct > trim_rule.trim_at_pct` (trail or book-half by `trim_rule.mode`)
   OR weight `> trim_rule.max_weight_pct` of the equity book.
3. **ADD** — near 52w-high + `ADX > entry.min_adx` + `close > DMA50` + RSI in
   `entry.rsi_band` + a matched news catalyst (catalyst wired in Phase 3).
4. **HOLD** — otherwise; reason names the nearest trigger.

Every non-HOLD verdict carries `stop_price = max(hard-stop, trailing-ATR)` and a
2R `target_price`. US (IndMoney) and crypto holdings pass through as HOLD
"not covered"; a missing quote → HOLD "no data" (never a crash).

## What Phase 2 ships — buy-candidate screener (§6 mirror)

| File (`backend/app/modules/signals/`) | Responsibility |
|---|---|
| `universe.py` + `themes.seed.md` | Resolve the universe from config: **themes** (union of the seed's constituents) or **nifty500** (free NSE CSV, cached 1×/day, **fail-open → themes**). `?theme=` filters to one theme |
| `screener_rules.py` | **Pure** `screen_one(symbol, indicators, config) → Candidate | None` — entry gates (`entry.*` + `screener.min_vol_ratio`), deterministic rank score, `entry/stop/target`. `rank()` sorts by (score desc, symbol) |
| `screen_service.py` | Orchestrator: universe → quotes → indicators → ranked top-N (reuses `quote_source` + `indicators`) |
| `signal_schema.py` | adds `Candidate` / `ScreenResult` (no clock) |
| `signals_routes.py` | `GET /signals/screen?theme=&limit=` |

The screener mirrors the **ADD** rule for *entries*: a symbol must clear `ADX >
entry.min_adx`, `pos_52w ≥ entry.high_52w_min`, `close > DMA50`, RSI in
`entry.rsi_band`, and `vol_ratio ≥ screener.min_vol_ratio`, then ranks by
`0.40·norm(ADX) + 0.35·pos_52w + 0.25·norm(vol_ratio)` (gates/cutoffs from config;
scoring weights are fixed code constants). Returns `screener.top_n` candidates.

## Strategy config

Knobs live in `strategy.config.md` (YAML frontmatter, **knobs only → git-safe**).
Resolution: the elgar `strategy/` copy (live, Orff-editable) → the repo seed →
built-in defaults. Change a knob ⇒ verdicts change deterministically.

## What Phase 3 ships — re-plan loop · tuning · Orff (§6.5, §7, §8)

| File (`backend/app/modules/signals/`) | Responsibility |
|---|---|
| `plan_store.py` | save/latest in the elgar **`actions/`** ledger (via `plans.elgar_bridge`); each save embeds the holdings snapshot + verdicts + stops. Best-effort |
| `plan_diff.py` | **pure** `diff(today, saved) → PlanDiff` (exited / new / stops fired / un-acted verdicts) |
| `review_service.build_review` | ActionPlan **+ diff vs the last saved plan** |
| `strategy_tuning.py` | `detect`/`propose` an ApprovalCard for a `group.knob = value` change; `apply` writes `strategy.config.md` to the elgar copy + a git commit. **Never silent** |
| `plan_card.py` | deterministic UISpec (Card + DataTable, "Δ since last" column) from the plan + diff — emitted as a `{spec}` on `/review` |
| `concierge/plan_context.py` | gated, best-effort prompt injection: strategy config + last plan + diff + top screener + matched news |

Endpoints: `GET /signals/review` (plan + diff), `POST /signals/plan` (save to
`actions/`), `POST /signals/strategy` (apply a confirmed knob change). Frontend:
`/review` `/screen` slash commands, the ApprovalCard's **Approve** POSTs a
`confirm.apply` (strategy change), and a "save plan → actions" button on the card.
Tradeoff reasoning is grounded in the `strategy-knob-tradeoffs` Fux rule. All
store I/O is best-effort — a missing/unreachable store degrades, never blocks chat.

## What Phase 4 ships — discipline loop (§10.4)

| File (`backend/app/modules/signals/`) | Responsibility |
|---|---|
| `weekly_service.py` | the **weekly job** Cowork's scheduler triggers: runs `build_review`, best-effort saves to `actions/` (the checkpoint that powers next week's diff), emits actionable verdicts + fired stops. **No auto-trading** |
| `pnl_tracker.py` | **pure** `realized_pnl(trades, costs, target)` — gross minus **explicit** brokerage + STT + friction + STCG → net vs target. ST losses offset ST gains; LT untaxed (follow-up) |
| `strategy_config.py` | `costs` knobs (`brokerage_per_order_inr`, `stt_pct`, `friction_pct`, `stcg_pct`) — **config-driven, verify against the Finance Act** (Fux `transaction-costs` / `capital-gains-equity`) |

Endpoints: `GET /signals/weekly` (the scheduled callable), `POST /signals/pnl`
(`{trades, target}` → `RealizedReport`). Costs are computed explicitly, never
approximated away; figures stay request-scoped (target never enters the repo).

## What Phase 5 ships — backtest the config after costs (§10.5)

Validates that the **active `strategy.config` has positive expectancy after costs
before you size up** — and makes it obvious when it doesn't. Composes the engine's
two halves into round-trips: **enter** when `screener_rules.screen_one` fires,
**exit** when `signal_rules.evaluate` says SELL. Per-symbol, independent, fixed equal
notional — this measures the per-trade *edge after costs*, **not** a capital/sizing
portfolio sim (concurrency & position sizing are out of scope for v1).

| File (`backend/app/modules/signals/`) | Responsibility |
|---|---|
| `backtest_schema.py` | `BacktestConfig` (lookback `years`, walk-forward `step_days`, per-trade `notional` — backtest *mechanics*, kept separate from the `StrategyConfig` under test) + `BacktestReport` |
| `backtest_data.py` | multi-year daily OHLCV **with dates**, cached by `symbol+years` (closed bars never change ⇒ reruns match). Reuses `to_yahoo`; fail-open skips a missing symbol |
| `backtest.py` | walk-forward `simulate_symbol` → `list[RealizedTrade]`; `run_backtest` over the resolved universe. Series-fn + universe are injectable so the probe replays a fixture offline |
| `backtest_metrics.py` | **pure** `build_report` → expectancy, win-rate, profit-factor, max drawdown, P&L after costs |
| `backtest_cli.py` | `just backtest` entry — real cached history → printed report + a loud ✅/❌ go-no-go verdict |

**Two cost lenses, on purpose:** win-rate / expectancy / the drawdown curve use
**per-trade friction net** (brokerage + STT + friction, *pre-tax* — the trading
edge); the headline **net** is the full after-cost figure from the Phase 4
`realized_pnl` (frictions + STCG with ST-loss offset). `positive_expectancy` =
`net > 0 AND mean friction-net > 0`. `trim_half` mode books a half-lot at the first
TRIM; the default `trail` mode rides to the SELL exit (or mark-to-close at the last bar).

`just backtest` (top-level recipe) runs `python -m app.modules.signals.backtest_cli`.

## Determinism & verification

Same holdings + same config ⇒ **byte-identical** `ActionPlan` (`generated_at`
lives in the route response, never in the plan). Verified by:

- `uv run pytest tests/test_signal_rules.py` — one test per verdict branch + a
  "thresholds come from config" test.
- `just signals-review` → `probes/signals_review_probe.py` — offline fixture,
  asserts two runs are byte-identical and prints the plan.
- `uv run pytest tests/test_screener_rules.py` — per-gate + ranking determinism.
- `just probe signals-screen` → `probes/signals_screen_probe.py` — fixture universe,
  asserts a byte-identical `ScreenResult`, score ordering, `top_n` cap, and that
  gate-failing / no-data symbols are excluded.
- `uv run pytest tests/test_plan_diff.py` — per-branch diff (exited/new/stops/unacted).
- `just probe signals-replan` → `probes/signals_replan_probe.py` — runs `build_review`
  on changed holdings and asserts the diff is reported (deterministic); a missing
  store degrades to an empty diff.
- `uv run pytest tests/test_pnl_tracker.py` — per-component costs + ST/LT + loss offset.
- `just probe signals-pnl` → `probes/signals_pnl_probe.py` — asserts the tracker nets
  brokerage + STT + friction + STCG to a hand-computed total on a fixture.
- `uv run pytest tests/test_backtest_metrics.py` — hand-computed expectancy, win-rate,
  drawdown + the friction-vs-STCG split; cross-checks `net` against `realized_pnl`.
- `just probe signals-backtest` → `probes/signals_backtest_probe.py` — replays a synthetic
  multi-year window offline, asserts the report is byte-identical across two runs, that
  both exit paths close round-trips, and that a losing set ⇒ `positive_expectancy=False`.

## Parallel "Deep search" grounding (handoff §9) — agent-initiated, shipped

The old `web_grounding` toggle is retired. Orff now calls the confirm-gated tool
`request_deep_search(reasons, queries)` (trusted lane) when it spots a fresh-data gap;
`deep_search_mode` (auto/always/never) governs it. `concierge/deep_search_service.py`
builds the confirm card (no call) and, on confirm/Always, runs the queries through the
shared executor `concierge/grounding_service.run` (Search tier; Task gated on
`parallel.allow_task_api` + a deep-dive prompt), recording a Search/Task-tagged Cage
receipt. A **hard monthly budget cap** (`grounding_service.budget_status`) checks
month-to-date Parallel spend against `parallel.monthly_budget_inr` *before* each call —
over budget ⇒ degrades to free sources, Orff says so. Key from the afbach vault.
`news/.../sources/parallel.py` mirrors the source contract but stays **out** of the free
aggregation path. Verified by `just probe deep-search` (auto / confirm / reject / always
/ never / over-budget) + `parallel-keys`. Canonical spec: `docs/handoffs/deep-search-ask.handoff.md`.

## Single-series here vs cross-sectional in `edges`

This engine is **single-series**: it reviews each holding and screens each candidate on its *own*
price history (one verdict per symbol). The **cross-sectional** factor edge — rank the whole
universe each week, hold a top-decile sleeve — lives in the edge-discovery engine
([docs/edges.md](edges.md), the EB-0 funnel), not here. Both reuse the same `signals` cost model
(`CostsCfg` + `pnl_tracker.realized_pnl`); the split keeps the live swing engine and the offline
discovery funnel as separate concerns.

## Not yet (later phases)

LTCG tax + a broker realized-trade ledger · a capital-constrained portfolio backtest
(concurrency + sizing, beyond Phase 5's per-trade-edge replay) · Parallel's true
async **Task API** (job create + long-poll — "task" mode is currently a deeper
Search call).
