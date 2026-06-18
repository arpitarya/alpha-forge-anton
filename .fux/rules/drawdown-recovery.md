---
id: drawdown-recovery
domain: portfolio
type: formula
status: active
principle: drawdown-recovery-convexity
enforcement: deterministic
created: 2026-06-12
updated: 2026-06-12
related: [capital-market-assumptions, position-concentration, core-allocation]
aliases: [max-drawdown, recovery-math, loss-asymmetry]
keywords: [drawdown, risk, recovery, loss, volatility]
check: "abs(recovery_pct - dd_pct / (1 - dd_pct)) < 1e-9"
examples:
  - given: '{"dd_pct": 0.50, "recovery_pct": 1.00}'
    expect: "true"
  - given: "a 50% drawdown needs a +100% gain to recover; 20% needs +25%"
    expect: "recovery = dd / (1 - dd)"
---
**Formula:** the gain required to recover a drawdown is convex in the loss:

```
recovery = dd / (1 - dd)      # dd as a fraction
10% → +11% · 20% → +25% · 33% → +50% · 50% → +100% · 70% → +233%
```

**Why:** losses and gains are asymmetric — volatility itself is a drag
(geometric mean < arithmetic mean by roughly half the variance). Two portfolios
with the same average return but different volatility end at different values,
the calmer one ahead. This is the quantitative case for allocation bands and
concentration ceilings ([[position-concentration]]): capping how much any one
bet can draw down beats chasing the highest expected return.

**How to apply:** when Orff discusses risk, frame it in drawdown terms ("a 40%
crypto drawdown needs +67% to break even"), not volatility jargon. Sizing rule
of thumb: the maximum tolerable portfolio drawdown bounds the high-volatility
sleeve — at a plausible 50% class drawdown, a 15% allocation costs ~7.5 points
of portfolio value, recoverable; a 50% allocation costs 25 points, a
multi-year hole. Use the plan's class weights ([[core-allocation]]) to make
this concrete with live numbers, never invented ones.
