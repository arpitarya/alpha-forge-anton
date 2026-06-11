---
id: core-allocation
domain: portfolio
type: narrative
status: active
created: 2026-06-11
updated: 2026-06-11
---
# Core allocation — default portfolio plan

The project's default rebalance plan. **Strategy only — zero personal figures**, so it
is safe in this public repo (the git-safety guard probe enforces it). Live holdings
never appear here; drift is computed at runtime against the data plane. Shape and rules
follow [[portfolio-plan-template]]; rationale for the design is in [[secure-holdings-plan]].

`plan_loader.load_plan("core-allocation")` reads the `targets` / `bands` below;
`aggregator.rebalance()` joins them against live actuals → `RebalanceDrift`.

## Targets (machine-read)

```yaml
plan_id: core-allocation
horizon: long-term
targets:                        # must sum to 100
  equity: 60
  mutual_fund: 15
  bond: 15
  gold: 5
  crypto: 3
  cash: 2
bands:                          # drift tolerance, in percentage points
  default: 5
  crypto: 1.5
rules:
  - trim any class > target + its band
  - top up any class < target - its band
  - prefer adding new capital over selling when drift is one-sided
```

## Goals (the *why*)

- **Equity 60%** — primary growth engine; the long horizon absorbs drawdowns.
- **Mutual funds 15%** — diversified core that needs no per-name attention.
- **Bonds + cash 17%** — stability plus dry powder that funds rebalancing without forced equity sales.
- **Gold 5%** — inflation / currency hedge, lightly held.
- **Crypto 3%, ±1.5pt band** — deliberately small and tightly banded; it drifts fast.

## Related

[[portfolio-plan-template]] · [[secure-holdings-plan]] · [[holdings-aggregator]] · [[portfolio-valuation]]
