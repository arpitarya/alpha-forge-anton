---
id: portfolio-plan-template
domain: portfolio
type: narrative
status: active
created: 2026-06-11
updated: 2026-06-11
---
# Portfolio plan — template (git-safe instance shape)

**What this is:** the shape every committed investment plan follows. A plan is
**strategy only** — target percentages, drift bands, rebalance rules, named goals,
horizon. It carries **zero personal figures** (no ₹ amounts, no quantities, no account
IDs, no holding symbols), so it is safe in a public repo. Live actuals live in the data
plane; see [[secure-holdings-plan]].

Orff reads `targets` / `bands` machine-side via `plan_loader.py`; the prose explains the
*why* so the plan is referenceable later (`fux why <plan-id>`).

## Targets (machine-read)

```yaml
plan_id: core-allocation        # one per strategy; this is the example
horizon: long-term              # short | medium | long-term
targets:                        # must sum to 100
  equity: 60
  mutual_fund: 15
  bond: 15
  gold: 5
  crypto: 3
  cash: 2
bands:                          # drift tolerance, in percentage points
  default: 5
  crypto: 1.5                   # tighter band on the volatile sleeve
rules:
  - trim any class > target + its band
  - top up any class < target − its band
  - prefer adding new capital over selling when drift is one-sided
```

## Goals (prose — the *why*)

- **Equity 60%** — primary growth engine; horizon is long enough to ride drawdowns.
- **Bonds + cash 17%** — dry powder + a floor that funds rebalancing without forced equity sales.
- **Crypto 3%, ±1.5pt band** — deliberately small and tightly banded; it drifts fast.

## How drift is computed (no figures leave the machine)

`get_drift(core-allocation)` →
`aggregator.rebalance(targets)` → per class `RebalanceDrift(target_pct, actual_pct,
drift_pct)`. Orff reports **points of drift and direction only** by default
(`disclose-aggregate-only`). Example narration — *"equity is +4pts hot, crypto is
−1pt; trim equity, add to bonds"* — no ₹, no symbols.

## Saving a real plan

1. Copy this entry to `.fux/rules/<plan-id>.plan.md`, edit `targets` / `bands` / goals.
2. `fux build` — it joins the graph and becomes `fux why <plan-id>`.
3. The git-safety guard probe must pass before commit (greps for ₹ / account IDs / symbols).

## Related

[[secure-holdings-plan]] · [[holdings-aggregator]] · [[portfolio-valuation]] ·
[[holdings-sum-equals-total]]
