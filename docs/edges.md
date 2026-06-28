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

**Implausible-drawdown guard** ([edge_stats.py](../backend/app/modules/edges/edge_stats.py)): a
**drawdown-free** cumulative curve over a meaningful sample (≥ `_MIN_TRADES_NO_DD` trades) is
overfit / look-ahead / data-too-short, **not** a flawless edge — it scores **Calmar 0 (fails the
gate)**, never a large positive. The `_DD_EPSILON` floor now only guards a true divide-by-zero on
tiny, low-confidence samples. Covered by `tests/test_edge_stats.py`.

### Constitutional storage — elgar only

The edge doc is money/strategy content, so it lives in the **private elgar store**
(collection `edges`), referenced from this repo only as `elgar://edge/<id>`. It is
**never committed to anton** (the `plan-store` constitutional rule). The store I/O reuses
the best-effort `plans.elgar_bridge`; see [edge_store.py](../backend/app/modules/edges/edge_store.py).
The journal lives in the `edges-journal` collection and carries **stats + counts only**
(no holdings, no ₹ PII) — safe by construction.

### Read side — the edge-library funnel (`GET /edges/summary`)

Every `append` also mirrors the run as one JSONL line in the store
(`edges-journal/journal.jsonl`, via [edge_journal.py](../backend/app/modules/edges/edge_journal.py)`.jsonl_path`),
so reads never parse markdown. [edge_library.py](../backend/app/modules/edges/edge_library.py)`.library_summary()`
aggregates the jsonl **and** tolerates legacy markdown-only entries (parsing their embedded
```json block, never crashing), dedupes by `(edge_id, run_at)`, then groups by edge — one
edge tested many times counts once. It returns `{tested, killed, passed, live, kill_rate,
recent[]}` (`live=0` until a promotion source exists; `kill_rate = killed/tested`). Served
read-only at `GET /edges/summary` for the Goals edge-library band.

## Gate-0 — data integrity (the pre-condition for every gate)

Before any backtest runs, the **data itself** must be honest. Gate-0 lives in
[backend/app/modules/marketdata/](../backend/app/modules/marketdata/) and is the admission
test no universe may skip:

- **Ingest** ([bhavcopy_ingest.py](../backend/app/modules/marketdata/bhavcopy_ingest.py)) —
  parses the free NSE bhavcopy (raw NSE header aliases supported) into typed `BhavRow` bars
  and caches them **reusing the `dump_utils` I/O discipline** (`dump_dir`, `chmod 600`,
  `# source=…` header-comment) with its own OHLCV columns (not the holdings `CSV_HEADERS`).
- **Point-in-time universe** — `universe_as_of(rows, day)` returns exactly the symbols
  trading on the latest session on/before `day`. No symbol that wasn't listed yet, no symbol
  carried back from the future.
- **The gate** ([gate0_integrity.py](../backend/app/modules/marketdata/gate0_integrity.py)) —
  `assert_no_leak(universe, rows)` recomputes the canonical as-of universe and raises
  `Gate0Error` on either leak: **look-ahead** (a symbol not trading at `as_of`) or
  **survivorship** (a symbol that *was* trading at `as_of` but the universe dropped — the
  classic "currently-listed names only" bias). Pure and deterministic.

Verified offline by `just probe gate0` ([gate0_integrity_probe.py](../probes/gate0_integrity_probe.py)):
the point-in-time universe is exact, a seeded leak is rejected, and the honest universe is accepted.

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

## Trial-ledger — multiple-testing integrity

Try enough hypotheses and one passes by luck. The append-only **trial-ledger**
([trial_ledger.py](../backend/app/modules/edges/trial_ledger.py)) records, per edge, the
trial budget the author **declared up front** (`declare_budget`) and the trials actually
spent (`record_trial`), so a later phase can deflate a result by how many shots were taken
(`budget` / `spent` / `remaining`). It is append-only (a correction is a new line, never an
edit) and carries **counts only** — no holdings, no ₹, no prompt text — constitutionally
safe by construction, the same discipline as the journal.

## Null-data self-test — the standing trust check

A funnel that "discovers" an edge in pure noise is broken or overfit. `just null-data`
([null_selftest.py](../backend/app/modules/edges/null_selftest.py)) feeds seeded, zero-drift
random walks through the funnel and **asserts it finds no edge**. It defines the `Funnel`
Protocol (the interface later phases implement) and a default `GateFunnel` that composes the
*existing* gates into a `contracts.TestReport` (no new trading logic). Run it on every change
— it's the cheapest possible guard against fooling ourselves.

## EB-0 — the cross-sectional factor edge through the full funnel (Gates 1–3)

The single-series `momentum` signal above is the toy/acceptance case. **edge-001** is a real
**cross-sectional portfolio** edge, and EB-0 pushes it through a richer funnel. Still pure,
deterministic, offline, **$0 — no LLM on the funnel path**. A PASS and an honest KILL are both
valid; nothing is tuned to force a pass.

**Factor engine** (rank → filter → trade → weekly net-return series):

| File | Role |
|---|---|
| [factor_schema.py](../backend/app/modules/edges/factor_schema.py) | `FactorConfig` + `grid_24()` — the **locked 24-config trial grid** (lookback {9,12,15} × slice {decile,quartile} × θ_roce {12,15,18} at θ_de 0.5 → 18, plus decile θ_de 1.0 × lookback {9,12,15} × θ_roce {12,15} → 6). Headline: lookback 12 / decile / θ_roce 15 / θ_de 0.5 / trend+stop on |
| [factor_rank.py](../backend/app/modules/edges/factor_rank.py) | `ret_12_1` momentum (`price[t-21]/price[t-252]-1`), deterministic rank, top decile/quartile |
| [factor_quality.py](../backend/app/modules/edges/factor_quality.py) | ROCE/D-E overlay — **honest-pending** when the fundamentals feed is absent (counted, never faked) |
| [factor_trend.py](../backend/app/modules/edges/factor_trend.py) | dual-momentum: cash when NIFTY < its 200-DMA (or unconfirmed) |
| [factor_exits.py](../backend/app/modules/edges/factor_exits.py) | −20% guard / 20-day-low stop / end-of-hold, first to fire |
| [factor_rebalance.py](../backend/app/modules/edges/factor_rebalance.py) | weekly simulator → net-return series via `edge_costs.net_pct`. **v1 cost model is conservative** (full round-trip cost per week — overcharges turnover, the honest direction) |
| [factor_panel.py](../backend/app/modules/edges/factor_panel.py) | aligned multi-symbol + NIFTY `Panel`; injectable `PanelProvider` (offline fixture now, real cached snapshot later) |

**The funnel** ([funnel.py](../backend/app/modules/edges/funnel.py)) runs pre-registration first, then:

- **Gate 1** — backtest the headline config + overfitting statistics over the 24-config grid:
  **PBO** (CSCV, [cscv_pbo.py](../backend/app/modules/edges/cscv_pbo.py)), **Deflated Sharpe**
  ([deflated_sharpe.py](../backend/app/modules/edges/deflated_sharpe.py)) and the **Harvey-Liu
  haircut** ([harvey_liu.py](../backend/app/modules/edges/harvey_liu.py)), with **N read from the
  trial-ledger** (edge-001 declares **24**). Pass = positive OOS expectancy AND PBO < 0.5 AND DSR ≥ 0.95.
- **Gate 2** — walk-forward over the 24-config return matrix
  ([factor_walkforward.py](../backend/app/modules/edges/factor_walkforward.py)), reusing the gate-2
  kill criterion (agg OOS Calmar ≥ 0.5 AND ≥ 60% windows positive).
- **Gate 3** — seeded block-bootstrap Monte-Carlo
  ([gate3_montecarlo.py](../backend/app/modules/edges/gate3_montecarlo.py)) → a Phase-0 `Cone`;
  **KILL if the P5 path drawdown breaches −20%**. The
  [scenario_library.py](../backend/app/modules/edges/scenario_library.py) (2008 / Mar-2020 /
  2024-25 −31%) rides along as red-team context.

The funnel emits a Phase-0 `TestReport` plus a **deterministic sha256 signature** (same panel +
seed ⇒ byte-identical signed report). `just eb0` ([eb0_cli.py](../backend/app/modules/edges/eb0_cli.py))
runs edge-001 (pre_registered_at 2026-06-23) on the committed offline panel and prints it.

## Data source

One seam ([edge_data.py](../backend/app/modules/edges/edge_data.py)): everything depends
on the `BarsProvider` protocol, never a concrete feed. The default `NSEDailyBars` reuses
the free NSE daily cache from `signals.backtest_data`. A paid/intraday source swaps in
here later without touching the gates.

### The committed offline panel — `nse-bhavcopy` (real)

EB-0's `FixturePanelProvider` reads a committed `Panel` JSON ({dates, closes, nifty}). A
**one-time, networked ingestion helper** produces the real one (`data_provenance =
nse-bhavcopy (real)`) — the network lives only here; the funnel stays offline / $0 /
deterministic against the cached output:

- **`just ingest-nse FROM TO`** ([bhavcopy_cli.py](../backend/app/modules/marketdata/bhavcopy_cli.py)
  → [bhavcopy_fetch.py](../backend/app/modules/marketdata/bhavcopy_fetch.py) +
  [bhavcopy_service.py](../backend/app/modules/marketdata/bhavcopy_service.py)) — primes NSE
  cookies (browser UA), pulls the era-appropriate daily bhavcopy (legacy **cm-bhav** + 2024+
  **UDiFF**, parsed by the pure [bhavcopy_parse.py](../backend/app/modules/marketdata/bhavcopy_parse.py))
  + the NIFTY close, and caches the **raw `.zip`/`.csv` per day** under `$NSE_DATA_DIR`. **Parallel**
  (stdlib `urllib`+`ThreadPoolExecutor`, `--workers`), **resumable + self-healing** via a sha256/CRC
  integrity manifest (`cache_manifest` — a day is "done" only if its bytes still match; atomic writes;
  `--verify` audits offline), **$0** (not LLM — never metered). Survivorship-safe by construction;
  No-network host: `--raw-dir DIR`. See [docs/broker-csv-dumps.md](broker-csv-dumps.md).
- **`just build-panel`** ([panel_build.py](../backend/app/modules/marketdata/panel_build.py),
  offline/$0) — emits the survivorship-safe **liquidity superset** (the union of the weekly
  point-in-time top-250-by-60-day-median-turnover sets,
  [panel_universe.py](../backend/app/modules/marketdata/panel_universe.py)) with **closes**
  (forward-filled, to hold a delisted position's value) **and a turnover series** (0 on non-trading
  days — never forward-filled, so a pre-listing / post-delisting name has no liquidity), then runs
  the **byte-integrity Gate-0** (`cache_read` re-hashes every cache file vs `cache-manifest.json` and
  refuses corrupt bytes) + **Gate-0 at every weekly rebalance** (eligible ⊆ that day's traders) before
  emitting a **deterministic gzip** `panel.json.gz` (`factor_panel.dump_panel`,
  `gzip … mtime=0` ⇒ byte-identical re-runs, ~3–4 MB vs ~20–25 MB raw; `load_panel` gunzips it
  transparently and still reads plain `.json`) + the manifest.

### The real verdict — per-rebalance universe, quality honest-pending, journaled to elgar

`just eb0-real` ([eb0_real_cli.py](../backend/app/modules/edges/eb0_real_cli.py)) runs edge-001's
**frozen 24-config campaign** on the committed real panel and prints the search-corrected verdict
(`data_provenance = nse-bhavcopy`). Three honesty rules:

- **Per-rebalance liquidity universe** — `factor_rank.rank_desc` ranks momentum over
  `factor_universe.liquid_as_of(panel, t)`, the **top-250 by trailing-60-day median turnover as of
  each rebalance**, reconstituted weekly — not pinned. A panel with no turnover (the synthetic
  `eb0/panel.json`) falls back to the full symbol set, so `just eb0` stays byte-identical.
- **Never-buy exclusions loaded at runtime, never committed** — the hard list is an elgar money doc
  (`elgar://plan/hard-exclusion-symbols`); anton holds only `factor_universe.load_exclusions`. Pass
  `--exclusions <path>` (`{"symbols":[…], "price_floor_inr": int}`) to **both** `build-panel` (excluded
  symbols never enter the committed superset) and `eb0-real`; `liquid_as_of` also drops any name whose
  **point-in-time close at `t`** is below the floor (no look-ahead, Gate-0 stays green). The
  `TestReport` records `exclusions_count` + `exclusions_source` — **counts/label only, never tickers**.
  An empty default ⇒ `just eb0` unchanged. `Exclusions` is scoped per run (set→restore), so concurrent
  synthetic/real runs never leak.
- **Quality leg disabled-pending** — there is no point-in-time ROCE/D-E feed, and applying today's
  fundamentals to history is look-ahead (Gate-0 forbids it). The real run executes **momentum +
  trend only** (`quality_on=False`) and records `quality_status="disabled-pending"` +
  `quality_pending` (names that could not be screened) in the `TestReport`. Point-in-time
  fundamentals (Screener.in / Tickertape) are the next data dependency.
- **Result journaled, never committed** — the `TestReport` (PBO/DSR/Calmar/verdict — stats/%, no ₹)
  is appended to the elgar `edges-journal` (`elgar://edge/<id>`) via `edge_journal.from_report`;
  **no figures are written into this repo** (the `plan-store` constitution). A PASS and a KILL are
  both valid — nothing is tuned.

## Run it

```bash
just edge <edge-id>                 # load elgar://edge/<id>, run gates 1-2, print verdict
just probe edge-discovery           # offline acceptance probe (no network, no store)
just probe gate0                    # Gate-0 data-integrity probe (look-ahead / survivorship)
just ingest-nse FROM TO [--workers N|--verify|--raw-dir P|--quiet]  # parallel resumable NSE ingest ($0)
just build-panel [--exclusions P]   # offline: assemble the committed EB-0 panel.json.gz (gzip) + Gate-0
just eb0-real [--exclusions P]      # the base-rate verdict on the real panel → journaled to elgar
just probe nse-ingest               # offline acceptance: parse·cache·build·Gate-0·manifest·idempotent
just probe progress                 # ingest progress bar: TTY renders, off-TTY silent (deterministic)
just probe eb0-real                 # offline: provenance + quality-pending + per-rebalance + determinism
just null-data                      # standing trust check — random data finds NO edge
just eb0                            # EB-0 — edge-001 through Gates 1-3 → signed TestReport
just probe eb0                      # EB-0 end-to-end: determinism + pre-registration + null-data
cd backend && uv run pytest tests/test_edge_*.py tests/test_factor_*.py tests/test_funnel.py tests/test_cscv_pbo.py tests/test_deflated_sharpe.py tests/test_harvey_liu.py tests/test_gate3_montecarlo.py tests/test_gate0_integrity.py tests/test_null_selftest.py tests/test_trial_ledger.py -v
```

## Verification

- `tests/test_edge_costs.py` — hand-checked net incl. STCG + slippage (qty=100, 100→110 = **+7.222%**).
- `tests/test_edge_backtest.py` — **known-answer** expectancy (−32.375%) + byte-identical reruns.
- `tests/test_edge_walkforward.py` — the **overfit edge passes gate 1 but is killed at gate 2**;
  a genuine momentum edge clears both.
- `tests/test_edge_register.py` — missing / post-result `pre_registered_at` rejected; valid passes.
- `tests/test_edge_journal.py` — PASS and KILL both journaled with the right `gate_reached`.
- `probes/edge_discovery_probe.py` (`just probe edge-discovery`) — all of the above, offline.
- `tests/test_factor_*.py` — momentum rank/select, quality honest-pending, 200-DMA trend, exit
  rules, weekly-simulator determinism.
- `tests/test_cscv_pbo.py` / `test_deflated_sharpe.py` / `test_harvey_liu.py` — PBO low/high,
  DSR + haircut monotonic in N.
- `tests/test_gate3_montecarlo.py` — seeded cone determinism + the P5 −20% kill.
- `tests/test_funnel.py` — **byte-identical signed TestReport** (same panel+seed) + pre-registration reject.
- `probes/eb0_probe.py` (`just probe eb0`) — EB-0 end-to-end offline: determinism, pre-registration,
  null-data still finds no edge.
- `tests/test_bhavcopy_parse.py` — **both** raw formats (cm-bhav + UDiFF) normalize identically;
  turnover is ₹; `parse_index_close` reads the named NIFTY close.
- `tests/test_panel_build.py` — universe pinned point-in-time, delisted name kept (forward-filled),
  post-start listing excluded, Gate-0 passes, panel byte-identical across re-runs + manifest counts.
- `probes/nse_ingest_probe.py` (`just probe nse-ingest`) — offline, via `--raw-dir`: resume downloads
  0 days; corrupting a cached zip re-fetches exactly that day; `--verify` flags it (exit≠0, no network);
  `build-panel` refuses a hash-mismatched cache (byte-integrity Gate-0); fingerprint is `--workers`-
  independent; `panel.json.gz` byte-identical. `tests/test_bhavcopy_integrity.py` +
  `tests/test_cache_manifest.py` cover sha/CRC/atomic-write + is_done/verify_all/rollup.
- `tests/test_factor_universe.py` — `liquid_as_of`: trailing-median top-N, delisted/pre-listing names
  excluded at `t`, the never-buy symbol + **point-in-time price-floor** filters, and the no-turnover
  full-universe fallback (all with dummy symbols, never real tickers).
- `tests/test_panel_build.py` — the per-rebalance superset reconstitutes (later listing enters), keeps
  delisted names (closes forward-filled, turnover 0-filled), excludes the illiquid; **deterministic
  gzip round-trip** (`load_panel(.gz)` == built panel, byte-identical re-runs); `--exclusions` drops a
  dummy symbol from the committed superset.
- `tests/test_eb0_real.py` + `probes/eb0_real_probe.py` (`just probe eb0-real`) — the real-run path:
  `data_provenance=nse-bhavcopy`, quality `disabled-pending` with pending counted, per-rebalance
  universe, deterministic signature, best-effort journaling — all offline, on a synthetic-shaped panel.

## Not yet (later slices)

Gate 3+ (Monte Carlo / regime stress), paper-trade, live · a capital-constrained
portfolio sim (concurrency + sizing) · promoting `status` candidate → paper → live.
