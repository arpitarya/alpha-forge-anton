---
id: inr-normalization
domain: portfolio
type: rule
status: active
created: 2026-06-03
updated: 2026-06-03
code_refs:
  - backend/app/modules/brokers/aggregator.py#L18-L23
  - backend/app/modules/brokers/fx.py#L112
related: [portfolio-valuation, day-pnl]
aliases: [forex, currency conversion, usd, to_inr]
keywords: [normalize, currency, fx, base-unit]
seal: 1f8a6dda8246a604
---
**Rule:** Every holding's monetary fields are converted to INR via `to_inr(value,
currency)` **before** any aggregation — sums, allocation, treemap, P&L.

**Why:** Holdings span currencies (e.g. NVDA priced in USD from IndMoney sitting
beside INR holdings). Summing raw values across currencies is meaningless; INR is
the single base unit the whole roll-up is expressed in. Normalizing at the leaf
(`_inr_value` / `_inr_invested`) keeps every downstream aggregate currency-correct.

**Edge cases:** a `None`/unknown currency must resolve to a defined rate in
`fx.to_inr` (never silently treat a USD value as INR — that 80× errors the total).
