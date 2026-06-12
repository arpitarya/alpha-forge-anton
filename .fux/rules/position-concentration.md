---
id: position-concentration
domain: portfolio
type: rule
status: active
created: 2026-06-12
updated: 2026-06-12
code_refs:
  - backend/app/modules/brokers/aggregator.py
related: [rebalancing-policy, core-allocation]
aliases: [concentration-risk, position-sizing, single-stock-limit]
keywords: [concentration, diversification, single-stock, sector, top-3]
---
**Rule:** Default concentration ceilings Orff applies when reviewing holdings
(overridable by the active plan in the elgar store, never hard-coded in code):

- a **single stock** ≤ 10% of total portfolio value;
- the **top 3 positions** combined ≤ 40%;
- a **single sector** ≤ 25% of the equity sleeve;
- a **single broker/platform** holding 100% of a class is a custody-risk flag,
  not a sell signal.

A breach is a **flag with a path back**, not an order to sell: first stop
adding ([[rebalancing-policy]] inflow-first ordering), then trim tax-aware.
Index funds and diversified mutual funds are exempt from the single-position
test — the limit targets idiosyncratic single-name risk.

**Why:** single-name blowups are the one risk diversification eliminates for
free. The thresholds are deliberately loose — tight limits force churn
([[transaction-costs]] in the indian-markets-tax pack) and over-trading hurts
more than mild concentration. What matters is that the *check runs on every
review* so concentration never grows silently.

**How to apply:** any holdings review Orff produces should compute position
weights from the aggregator's INR-normalised values ([[inr-normalization]])
and call out breaches with the specific weight, the ceiling, and the
no-tax-event path back inside it.
