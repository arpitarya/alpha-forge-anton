---
id: core-allocation
domain: portfolio
type: glossary
status: active
created: 2026-06-11
updated: 2026-06-12
---
# core-allocation

The default portfolio rebalance plan. **Content lives in the private elgar store**
— linked, never stored, per [[plan-store]]:

> `elgar://plan/core-allocation` — read it with `elgar get core-allocation`

`plan_loader.load_plan("core-allocation")` reads its `targets` / `bands` from the
store; `plan_drift.drift_for_plan()` joins them with live actuals into
percentages-only drift.

## Related

[[plan-store]] · [[portfolio-plan-template]] · [[secure-holdings-plan]] ·
[[holdings-aggregator]]
