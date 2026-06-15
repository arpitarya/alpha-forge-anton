# Handoff — Signals Engine & Re-runnable Plan Loop

**For:** Claude Code, working in the `anton` repo.
**Author:** design handoff (operator: Arpit). **Status:** ready to build, Phase 1 first.
**One-line goal:** give Orff a deterministic, re-runnable engine that reviews holdings and emits a buy / hold / trim / sell action plan, each run aware of the previous plan and what actually changed.

> **No personal figures in this doc or the repo.** Corpus/holdings/targets live in the elgar store. This spec is percentages, rules, and interfaces only — git-safe.

---

## 1. Objective & success criteria

Build a `signals/` module + a re-runnable plan loop so that:

1. `GET /signals/review` returns a deterministic `ActionPlan` over current holdings (verdict + reason + stop + target per symbol). **No LLM touches the numbers.**
2. Each run reads the **last saved plan + outcome + current holdings** and emits the next plan as a **delta** ("last plan: TRIM PARAS at +50%; not done; re-decide").
3. Orff `/review` narrates the why and the delta; the plan is saved to the elgar `actions/` collection (one git commit per run = audit trail).
4. A buy-candidate `/screen` ranks a free universe for new swing entries.
5. Parallel web-grounding is available as an **off-by-default per-message chat toggle**.

**Definition of done per phase:** code + a `probes/` probe + a `just` recipe + doc updates, in the same session. A feature without a probe is not verified (see `probes/WHY_PROBES_NOT_MCP.md`).

---

## 2. Non-negotiable constraints (from CLAUDE.md — do not violate)

- Files ≤ **100 lines** (≤ **50** for `*_utils.py`). Backend names: `{domain}_{role}.py`.
- Python: `async def` everywhere, absolute imports from `app.`, Pydantic v2, ruff line-length 100.
- **$0 / free data only** on the default path. yfinance + ta-lib + the news aggregator are the stack. Parallel is the only paid path and is opt-in.
- **Determinism is sacred:** signal math is reproducible AST/parse/compute — same inputs ⇒ same verdicts. The LLM only narrates.
- **No auto-trading.** The engine advises and emits stop/target prices; the user places GTT orders manually. Never call a broker order API.
- **Two-place money rule:** never write personal figures or `*.plan.md` into this repo (pre-commit + `just dante-pii` enforce it). Plans persist to the elgar `actions/` collection via the elgar CLI.
- **UI/broker verification via `probes/` (CDP :9299), never Playwright MCP.**
- Every code change ships a doc update in the same session.

---

## 3. What already exists (reuse, do not rebuild)

- **Holdings, full detail, trusted lane** — `concierge/holdings_detail.holdings_table()` exposes symbol/qty/avg/ltp/pnl%/day% when the resolved provider is trusted (`holdings_private.py` is the chokepoint). `HoldingsAggregator` (`brokers/aggregator.py`) is the INR-normalised roll-up.
- **News aggregator** — `news/src/alphaforge_anton_news/` (8 source adapters → `dedup` → ranked items). Consume it; do not modify its shape.
- **Plan store pattern** — `plans/elgar_bridge.py` (subprocess to the `elgar` CLI), `plan_loader.py`, `plans_schemas.py`. The `actions/` collection follows the same pattern as `sessions/` and `plans/` (elgar `--dir actions`).
- **Concierge prompt assembly** — `concierge/prompt_service.py` composes system/intent/memory/holdings/news/history blocks. Add the plan-memory + signals blocks here.
- **Compose / cards** — `compose_service.py` + `DynamicRenderer.tsx` render a Fux-validated UISpec. Render the action plan as a card through this path.
- **Slash commands** — `frontend/src/modules/concierge/concierge.commands.ts`. Add `/review` and `/screen`.
- **Cost ledger** — Cage (`anton/docs/cage.md`); the `cage_meter` adapter records LLM/tool spend.

---

## 4. Module map to build

```
backend/app/modules/signals/
  __init__.py            router export
  quote_source.py        yfinance adapter: symbol list -> 12mo daily OHLCV, cached 1/day
  indicators.py          ta-lib wrappers: RSI14, ADX14, DMA20/50/200, ATR14, 52w pos, vol-vs-avg
  signal_rules.py        typed rules -> Verdict; reads thresholds from strategy config (§6)
  signal_schema.py       Pydantic Verdict / ActionPlan
  strategy_config.py     load/validate the elgar strategy config -> typed StrategyConfig (§6.5)
  universe.py            resolve universe from config: themes | nifty500 (free NSE CSV)
  screener_rules.py      rank universe for new swing entries (config-driven)
  plan_store.py          read/write the elgar `actions/` plan ledger (elgar_bridge pattern)
  plan_diff.py           diff current holdings vs the snapshot inside the last plan
  signals_routes.py      GET /signals/review, GET /signals/screen, GET /signals/strategy

backend/app/modules/concierge/
  grounding_service.py   NEW: Parallel Search/Task call when web_grounding flag set, budget-gated (§9)
  strategy_tuning.py     NEW: propose/apply a strategy-config change via the approval flow (§6.5)
  prompt_service.py      EDIT: inject strategy config + tradeoff knowledge + latest plan + ActionPlan + screener + news
  concierge_schemas.py   EDIT: add `web_grounding: bool = False` to the request

news/src/alphaforge_anton_news/sources/
  parallel.py            NEW: Parallel source, same base.py contract as tavily/brave

frontend/src/modules/concierge/
  concierge.commands.ts  EDIT: add /review, /screen
  (composer)             EDIT: add an off-by-default "Deep search" toggle -> web_grounding
```

Keep each file single-purpose and within the line budget; split helpers into `*_utils.py` if needed.

---

## 5. Data layer (`quote_source.py`)

- Map broker `tradingsymbol` → Yahoo symbol: NSE `SYMBOL.NS`, BSE `SYMBOL.BO`. Strip suffixes like `-EQ`. Keep a small override table for mismatches.
- Fetch 12-mo daily OHLCV via yfinance; cache to disk (one pull/day/symbol) so a `/review` run is cheap and offline-replayable.
- US holdings (IndMoney) and crypto: out of scope for the swing ruleset v1 — pass through as HOLD with a "not covered" reason. Don't fake signals for them.
- Fail-open: a missing quote ⇒ that symbol gets `verdict=HOLD, reason="no data"`, never a crash.

---

## 6. The deterministic ruleset (`signal_rules.py`) — swing style

`Verdict{action: SELL|TRIM|HOLD|ADD, reason: str, stop_price: float|None, target_price: float|None, conviction: int}`

Evaluate in priority order; first match wins:

1. **SELL** — `pnl_pct < -15` (hard stop) OR `close < ATR_stop` OR (`close < DMA50` AND `RSI14 < 40`). Reason cites which.
2. **TRIM** — `pnl_pct > +50` (book half, let rest run) OR `position_weight > 15%` of equity book (concentration).
3. **ADD** — near 52w-high (`>= 0.9`) AND `ADX14 > 25` AND `close > DMA50` AND `50 <= RSI14 <= 70` AND a matched news catalyst. (Continuation entry.)
4. **HOLD** — otherwise. Reason states the nearest trigger ("12% below trim level").

Always compute `stop_price` and `target_price` for every non-HOLD verdict. **Every threshold above is read from the strategy config (§6.5), never hardcoded** — that's what makes the strategy tunable through Orff. The backtest (Phase 5) validates the active config after costs.

`screener_rules.py` mirrors this for the universe: rank by ADX, 52w position, volume breakout, RSI band → top N candidates with entry/stop/target.

## 6.5 Strategy config — the tunable knobs Orff can discuss & change

**Requirement:** the operator decides strategy questions *in conversation with Orff*, not by editing code. So the knobs live in a versioned config Orff can read, explain the tradeoffs of, and (on confirmation) edit.

- **Where:** `strategy.config.md` in the elgar store, **own collection** `strategy/` (alongside `plans/`, `actions/`, `sessions/`). YAML frontmatter, git-versioned — every change is one commit = an audit trail of how the strategy evolved.
- **Shape (starting defaults):**
  ```yaml
  universe:
    mode: themes            # themes | nifty500
    themes: [defence, solar, capex_td, ev_auto, specialty_chem]
  trim_rule:
    mode: trail             # trail | trim_half  (default: trail — see below)
    trim_at_pct: 50
    trail_atr_mult: 2.5
  stops:
    hard_pct: -15
  entry:
    min_adx: 25
    rsi_band: [50, 70]
    high_52w_min: 0.90
  parallel:
    monthly_budget_inr: 300
    allow_task_api: true
  ```
- **Single source of truth:** `strategy_config.py` loads + validates it into a typed `StrategyConfig`; `signal_rules.py`, `screener_rules.py`, `universe.py`, and `grounding_service.py` all read from it. Change the config ⇒ engine behaviour changes, deterministically.
- **Orff discusses it:** `prompt_service` injects the *current* config plus a Fux-grounded **tradeoff brief** for each knob (so Orff explains "theme-mode = higher conviction, fewer names; nifty500 = wider net, more dilution" with real reasoning, not vibes). Ground the briefs in a Fux rule (`strategy-knob-tradeoffs`) so the reasoning is consistent and auditable.
- **Orff changes it (safely):** when you decide, Orff emits an **ApprovalCard** ("Set `trim_rule.mode = trail`?") via the existing `action_service` confirm flow; on confirm, `strategy_tuning.py` writes the new config to elgar (one commit). Mutating the strategy is a confirmed action, never silent.
- `GET /signals/strategy` returns the active typed config for the UI.

**Resolved defaults (Orff can change any of these with you):**
- **Universe → `themes`.** For swing + small capital, your five held themes are higher-conviction than the full Nifty-500. Orff can widen to `nifty500` on request, or add/drop a theme conversationally.
- **Trim → `trail`, not auto-trim.** Auto-trimming at +50% would have capped your biggest runners; for a momentum/swing book the edge is letting winners run under a trailing ATR stop. `trim_half` stays available as a mode. This is exactly the kind of call to make *with* Orff once you've seen a few cycles.
- **Parallel → Search API default, Task API allowed, both under a monthly budget** (see §9).

---

## 7. The re-runnable plan loop (the spine)

```
plan(today) = f(holdings(today), last_plan, outcomes_since_last_plan, signals(today), news(today))
```

- **`plan_store.py`** — list/get/save in the elgar `actions/` collection (`elgar --dir actions ...` via `elgar_bridge`). Each saved plan embeds: the holdings snapshot, the per-symbol verdicts, and the stop/target prices it was based on. One save = one git commit.
- **`plan_diff.py`** — diff `holdings(today)` against the snapshot inside the latest `actions/` doc. Output: positions exited, new buys, stops that fired, and **un-acted verdicts** (last plan said TRIM/SELL/ADD, holding unchanged).
- **Prompt injection** — `prompt_service.py` loads the latest plan + diff so Orff reasons *from the prior plan* and explains the delta. Reuses the existing memory/history injection pattern.
- All plan I/O is **best-effort**: a missing/unreachable store degrades to a fresh plan, never blocks the chat.

---

## 8. Endpoints & slash commands

- `GET /signals/review?plan_id=...` → `ActionPlan` (held stocks, with diff vs last plan).
- `GET /signals/screen?theme=...` → ranked buy candidates.
- `/review` → prompt: "Review every holding vs my last plan — buy/hold/trim/sell with reasons and stops."
- `/screen` → prompt: "Screen for new swing entries in my themes."
- Render the plan via `compose` as a 4-column card (Buy / Hold / Trim / Sell) with a "changed since last plan" column; offer Save (writes to `actions/`).

---

## 9. Parallel grounding toggle (off by default)

- **Request flag:** add `web_grounding: bool = False` to the concierge request schema. Frontend adds a composer toggle (next to ImageAttach) — a `🌐 Deep search` chip — defaulting off.
- **`grounding_service.py`:** when the flag is set, call Parallel; `prompt_service` injects results as a grounding block and emits a `{tool:{name:"parallel", detail, ms}}` ToolTrail event.
  - **Search API** is the default call (cheap, fast) — for catalyst/news depth on a decision.
  - **Task API** is allowed (`strategy.config parallel.allow_task_api`) for deeper per-stock research runs, but only when the user explicitly asks for a deep dive — it costs more.
- **Budget is enforced, not advisory:** `parallel.monthly_budget_inr` in the strategy config is a hard cap. `grounding_service` checks month-to-date Parallel spend from the **Cage** ledger *before* each call; over budget ⇒ the call is skipped and Orff says so ("Parallel budget for June is used — answering from free sources"). Orff can report remaining budget on request.
- **Key:** from the **bach vault** (`alpha-forge-bach`), never env/code. See `docs/vault.md`.
- **Cost:** record a Cage receipt per Parallel call (Search vs Task tagged) so the SessionMeter and the budget check both see real spend. See `docs/cage.md`.
- **Default path stays free:** RSS / NSE / BSE / Reddit / yfinance remain the everyday sources; Parallel is the explicit, paid, budget-capped, on-demand depth button.

---

## 10. Build sequence

1. **Phase 1** — `strategy_config` (+ a default `strategy.config.md`), `quote_source`, `indicators`, `signal_rules`, `signal_schema`, `signals_routes` (`/review` + `/strategy`) + probe + `just signals-review` + docs. Thresholds read from config from the first commit.
2. **Phase 2** — `universe`, `screener_rules`, `/screen` (universe resolved from config).
3. **Phase 3** — `plan_store`, `plan_diff`, `strategy_tuning` + the `strategy-knob-tradeoffs` Fux rule, prompt injection (config + tradeoffs + plan), ApprovalCard wiring, `/review` `/screen` commands, compose card + save to `actions/`.
4. **Phase 4** — weekly scheduled review + monthly realized-P&L tracker (net of cost).
5. **Phase 5** — ✅ **shipped.** `backtest.py` (+ `backtest_data/metrics/schema/cli`): replays the active config over 2–3 yrs of cached history (screener entry → ruleset SELL exit, per-symbol equal-notional round-trips) and reports expectancy, win-rate, max drawdown & P&L **after costs**, with a go/no-go flag. `just backtest` + `just probe signals-backtest` + `tests/test_backtest_metrics.py`. See [docs/signals.md](signals.md) "What Phase 5 ships".
6. **Parallel toggle** — can land any time after Phase 1; independent.

---

## 11. Acceptance criteria & probes

- **Phase 1:** `just signals-review` prints a deterministic `ActionPlan` for a fixture holdings set; same fixture ⇒ identical output (determinism test). Hard-stop and trim rules covered by unit tests in `backend/tests/`.
- **Loop:** a probe that runs `/review` twice with a changed holdings fixture and asserts the second plan reports the diff (un-acted verdict + new position).
- **Disclosure safety:** the existing `holdings_disclosure_probe.py` must still pass — signals must never leak ₹/symbols to an untrusted provider.
- **Parallel:** a probe that asserts (a) flag off ⇒ no Parallel call, (b) flag on ⇒ one call + one Cage receipt + one ToolTrail event.
- **PII:** `just dante-pii` clean; no figures in the repo.

---

## 12. Resolved decisions

All three former open questions are resolved as **tunable strategy config the operator adjusts in conversation with Orff** (§6.5) — the engine ships with these defaults, Orff can change any of them via the approval flow:

1. **Universe → `themes`** (defence, solar, capex/T&D, EV/auto, specialty chem). Widen to `nifty500` on request.
2. **Trim → `trail`** (trailing ATR stop, never auto-trim winners). `trim_half` available as a mode.
3. **Parallel → Search API default + Task API allowed, under a hard monthly budget** enforced from the Cage ledger (§9).

The build adds, beyond the original spec: `strategy_config.py`, `strategy_tuning.py`, the elgar `strategy/` collection, a Fux `strategy-knob-tradeoffs` rule, and `GET /signals/strategy`. Sequence them with **Phase 3** (they share the prompt-injection + approval-card plumbing); the engine in Phases 1–2 reads the config from day one rather than hardcoding thresholds.
