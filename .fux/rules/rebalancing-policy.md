---
id: rebalancing-policy
domain: portfolio
type: rule
status: active
created: 2026-06-12
updated: 2026-06-29
aliases:
  - rebalance
  - band-rebalancing
  - drift-action
keywords:
  - rebalance
  - band
  - drift
  - hot
  - cold
  - tax-aware
  - inflow
code_refs:
  - backend/app/modules/plans/plan_drift.py
  - backend/app/modules/plans/plan_loader.py
related:
  - core-allocation
  - capital-market-assumptions
  - plan-store
---
**Rule:** Rebalancing is **band-triggered, not calendar-triggered**, and follows
a fixed order of preference that minimises tax and friction:

1. **No action inside the band.** A class within its plan tolerance band
   (`plan_drift` status `ok`) is never traded — drift inside the band is noise.
2. **New money first.** Direct fresh inflows/SIPs to the coldest class until it
   re-enters its band — adding triggers no tax event and no exit friction.
3. **Sell hot classes last**, and when selling, prefer long-term lots over
   short-term ones ([[capital-gains-equity]], [[capital-gains-debt-gold]]) and
   harvest available losses in the same year ([[tax-loss-harvesting]]).
4. **Crypto trims are the most expensive** — flat-taxed with no loss offset —
   so a hot crypto sleeve is trimmed by halting inflows before selling.

**Why:** calendar rebalancing trades on schedule whether or not anything is
wrong, paying friction ([[transaction-costs]]) and tax for zero drift benefit.
Band discipline trades only when the portfolio is measurably off-plan, and the
inflow-first ordering means most corrections cost nothing. The bands themselves
live in the active plan in the elgar store ([[plan-store]]), per class.

**How to apply:** Orff's rebalance advice must derive from `plan_drift` rows
(`hot`/`cold`/`ok` + suggested points), never from raw weights, and must state
the order above when the user asks "what should I do". `GET /plans/drift` is
the single source for current drift.
