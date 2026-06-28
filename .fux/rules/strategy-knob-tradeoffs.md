---
id: strategy-knob-tradeoffs
domain: portfolio
type: rule
status: active
created: 2026-06-15
updated: 2026-06-28
aliases:
  - strategy-knobs
  - signal-config-tradeoffs
  - tunable-strategy
keywords:
  - strategy
  - config
  - knob
  - tradeoff
  - trim
  - trail
  - universe
  - adx
  - rsi
  - budget
code_refs:
  - backend/app/modules/signals/strategy_config.py
  - backend/app/modules/signals/strategy_tuning.py
  - backend/app/modules/signals/signal_rules.py
  - backend/app/modules/signals/screener_rules.py
related:
  - position-concentration
  - rebalancing-policy
  - capital-market-assumptions
---
**Rule:** the signals engine's behaviour is governed by a small set of tunable
knobs (`strategy.config.md` → `StrategyConfig`). Orff explains each knob's
**tradeoff** before proposing a change, and never mutates the config silently — a
change is an ApprovalCard, written to elgar on confirm (`strategy_tuning`). The
briefs below ground that reasoning so it is consistent and auditable, not vibes.

- **`universe.mode` — `themes` vs `nifty500`.** Themes = higher conviction, fewer
  names, less dilution, but concentration + theme risk; suits small swing capital.
  Nifty500 = a wider net and more diversification, but more shallow signals and
  attention spread thin. Widen only when you can act on more names.
- **`trim_rule.mode` — `trail` vs `trim_half`.** Trail lets winners run under a
  trailing ATR stop — the edge in a momentum book — at the cost of giving back
  open profit on a sharp reversal. Trim_half books certainty at `+trim_at_pct`
  but caps your biggest runners (the few that pay for the book). Default `trail`.
- **`trim_rule.trail_atr_mult`.** Wider (↑) = fewer whipsaws, more give-back;
  tighter (↓) = locks gains sooner but stops out on normal noise.
- **`trim_rule.max_weight_pct`.** The concentration ceiling ([[position-concentration]]):
  lower = safer, more forced trims of winners; higher = lets conviction ride with
  more single-name risk.
- **`stops.hard_pct`.** The disaster floor. Tighter = smaller max loss per name
  but more premature exits; wider = more room but a deeper hole to recover from
  (recovery is convex — see drawdown math).
- **`entry.min_adx` / `rsi_band` / `high_52w_min`.** The ADD + screener gates.
  Stricter = fewer, higher-quality entries; looser = more candidates, more noise.
- **`parallel.monthly_budget_inr` / `allow_task_api`.** The paid deep-search cap
  (§9). Higher budget = more on-demand web grounding; the engine enforces it as a
  hard cap from the Cage ledger, so this trades money for catalyst depth.

**Why:** the operator decides strategy *in conversation*, so the reasoning must be
real and repeatable. Grounding the briefs here (not in a prompt string) keeps
Orff's explanations consistent across sessions and tied to the actual knobs.

**How to apply:** when discussing or changing the strategy, cite the relevant
brief, surface the tradeoff both ways, then propose the change as an ApprovalCard —
never edit the config without confirmation.
