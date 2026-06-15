---
universe:
  mode: themes                 # themes | nifty500
  themes: [defence, solar, capex_td, ev_auto, specialty_chem]
trim_rule:
  mode: trail                  # trail (let winners run) | trim_half
  trim_at_pct: 50
  trail_atr_mult: 2.5
  max_weight_pct: 15           # concentration cap, % of equity book
stops:
  hard_pct: -15
exit:
  weak_rsi: 40                 # sub-DMA50 close + RSI below this => SELL
entry:
  min_adx: 25
  rsi_band: [50, 70]
  high_52w_min: 0.90
screener:
  min_vol_ratio: 1.5           # volume-breakout gate (last vol / 20-day avg)
  top_n: 10
costs:                         # net-P&L frictions + tax — verify against the Finance Act
  brokerage_per_order_inr: 20  # flat per order (Zerodha delivery = 0)
  stt_pct: 0.1                 # delivery STT, % of value per leg
  friction_pct: 0.03          # stamp + exchange + SEBI + GST, % of turnover
  stcg_pct: 20                 # §111A short-term capital gains, %
parallel:
  monthly_budget_inr: 300
  allow_task_api: true
---

# Strategy config — swing/momentum knobs (Orff-tunable)

Knobs only — **no personal figures**, so this seed is git-safe. The live,
operator-editable copy lives in the elgar `strategy/` collection and overrides
this file when present (`strategy_config.load_config`); Phase 3's
`strategy_tuning` writes changes there through the approval flow (one commit each).

Every threshold the deterministic ruleset uses is here — `signal_rules`,
`screener_rules`, `universe`, and the Parallel grounding budget all read this
config, nothing is hardcoded. Change a knob ⇒ the engine's verdicts change
deterministically (the backtest in Phase 5 validates a config after costs).

| Knob | Meaning |
|------|---------|
| `universe.mode` | `themes` (high-conviction, your 5 themes) or `nifty500` (wide net) |
| `trim_rule.mode` | `trail` keeps winners under a trailing ATR stop; `trim_half` books half at `trim_at_pct` |
| `trim_rule.trail_atr_mult` | ATR multiple for the trailing stop |
| `trim_rule.max_weight_pct` | concentration cap — trim above this share of the equity book |
| `stops.hard_pct` | hard stop on unrealised P&L |
| `exit.weak_rsi` | a close below DMA50 with RSI under this is a SELL |
| `entry.min_adx` / `rsi_band` / `high_52w_min` | ADD (continuation) + screener entry gates |
| `screener.min_vol_ratio` / `top_n` | volume-breakout gate + how many ranked candidates `/screen` returns |
| `costs.brokerage_per_order_inr` / `stt_pct` / `friction_pct` / `stcg_pct` | net-P&L frictions + short-term tax — verify against the prevailing Finance Act |
| `parallel.monthly_budget_inr` / `allow_task_api` | Parallel deep-search budget + Task-API switch (§9) |
