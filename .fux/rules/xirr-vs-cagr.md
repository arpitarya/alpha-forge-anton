---
id: xirr-vs-cagr
domain: portfolio
type: formula
status: active
created: 2026-06-12
updated: 2026-06-12
code_refs:
  - backend/app/modules/plans/projection_service.py
related: [capital-market-assumptions, day-pnl, portfolio-valuation]
aliases: [xirr, cagr, money-weighted, time-weighted, returns]
keywords: [returns, sip, annualised, irr, benchmark]
---
**Formula:** Use the return measure that matches the cash-flow shape:

- **CAGR** — single lump sum, no flows: `cagr = (end/start)^(1/years) - 1`.
- **XIRR** — any portfolio with deposits/withdrawals (every SIP portfolio):
  the rate `r` solving `Σ cf_i / (1+r)^(t_i/365) = 0` over all dated cash
  flows plus the current value as the final inflow.

Quoting CAGR on a SIP portfolio is **wrong in both directions**: it overstates
return in a rising market (late instalments grew for months, not years) and
understates it after a dip-heavy accumulation. The error grows with the ratio
of contributions to starting corpus.

**Why:** XIRR is money-weighted — it answers "what did *my* money earn?",
which is the user's question. Fund factsheets quote time-weighted returns —
comparing a personal XIRR against a factsheet CAGR is only meaningful when
flows were small; otherwise compare against the XIRR of the same flows
invested in the benchmark.

**How to apply:** broker-reported "returns %" fields are usually absolute
gain-over-invested, not annualised — never present them as annual rates.
`projection_service.project` runs the forward direction (monthly compounding
of an assumed rate, [[capital-market-assumptions]]); a future realised-XIRR
metric must be computed from dated transactions, not from holdings snapshots.
