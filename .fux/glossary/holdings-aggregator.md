---
id: holdings-aggregator
domain: portfolio
type: glossary
status: active
created: 2026-06-09
updated: 2026-06-09
code_refs:
  - backend/app/modules/brokers/aggregator.py
related: [portfolio-valuation, holdings-sum-equals-total, inr-normalization, broker-source]
aliases: [aggregator, roll-up]
keywords: [aggregator, totals, allocation, treemap, rebalance, roll-up]
---
**Term:** HoldingsAggregator

**Definition:** The read-only roll-up over every registered [[broker-source]]'s
cached holdings. It never fetches or mutates — it reads `source.cached` lists and
computes derived views: `totals` (invested / current_value / pnl), `allocation`,
`treemap`, and `rebalance` drift. Cross-currency holdings are INR-normalised here
via `fx.to_inr` before summing ([[inr-normalization]]), and the result must satisfy
[[holdings-sum-equals-total]]. Backs the `/portfolio/*` endpoints.
