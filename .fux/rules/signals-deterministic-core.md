---
id: signals-deterministic-core
domain: portfolio
type: rule
status: active
created: 2026-06-16
updated: 2026-06-16
code_refs:
  - backend/app/modules/signals/signal_rules.py
  - backend/app/modules/signals/screener_rules.py
  - backend/app/modules/signals/strategy_config.py
  - backend/app/modules/signals/review_service.py
related: [strategy-knob-tradeoffs, secure-holdings-plan, finance-feature-playbook, position-concentration]
aliases: [deterministic-signals, signal-engine-law, llm-narrates-not-computes]
keywords: [signals, verdict, deterministic, config, thresholds, review, screener, llm]
---
**Rule:** the signals engine is a **deterministic core with a probabilistic edge**.
Every buy/hold/trim/sell verdict, stop, target, and screener rank is produced by typed
Python reading the strategy config — **never by an LLM**. Same holdings + same config ⇒
byte-identical `ActionPlan`. The LLM only **narrates** the verdicts and the why; it must
not compute or alter a number.

**Why:** wrong numbers in a finance terminal cost money and are unauditable. Determinism
makes verdicts reproducible, testable, and backtestable; it is what lets the plan loop and
the backtest validate a config before real capital rides on it.

**How it's enforced:**
- Thresholds live in `strategy.config.md` → `StrategyConfig`; **nothing is hardcoded** in
  `signal_rules`/`screener_rules` (change a knob ⇒ verdicts change — see [[strategy-knob-tradeoffs]]).
- `signal_rules` is pure: no I/O, no fetch, no model call (the fetch is in `quote_source`).
- A determinism probe asserts identical output for a fixed fixture; unit tests cover each
  verdict branch.
- Orff receives the computed `ActionPlan` as context to explain — it is told to narrate,
  not recompute. Consistent with the disclosure model in [[secure-holdings-plan]].

New signal/metric work follows the [[finance-feature-playbook]] pipeline.
