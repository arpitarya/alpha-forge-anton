---
id: portfolio-valuation
domain: portfolio
type: formula
status: active
created: 2026-06-03
updated: 2026-06-03
code_refs:
  - backend/app/modules/brokers/aggregator.py#L38-L59
related: [inr-normalization, day-pnl]
aliases: [totals, current value, invested, pnl]
keywords: [valuation, roll-up, holdings, total]
---
**Rule:** Portfolio totals are computed over INR-normalised holdings:
`invested = Σ inr_invested(h)`, `current = Σ inr_value(h)`, `pnl = current −
invested`.

**Formula:** `pnl_pct = pnl / invested × 100` (0 when `invested == 0`).

**Why:** P&L is *unrealised* mark-to-market — current market value minus
cost-basis — so both legs must be INR-normalised first ([[inr-normalization]]).
Percentage uses **invested** as the denominator (return on capital deployed),
while *today's* move uses current value ([[day-pnl]]) — a deliberate distinction.

**Edge cases:** every percentage guards division by zero (`if invested/current
else 0.0`). `count`, `day_up`, `day_dn` are diagnostics, not part of the money math.
