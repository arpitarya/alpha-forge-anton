---
id: day-pnl
domain: portfolio
type: formula
status: active
created: 2026-06-03
updated: 2026-06-03
code_refs:
  - backend/app/modules/brokers/aggregator.py#L43-L46
related: [inr-normalization, portfolio-valuation]
aliases: [day pnl, today's gain, daily change, day_change_pct]
keywords: [today, intraday, gain, loss, mark-to-market]
check: "abs(day_pnl - sum(v * (p / 100.0) for v, p in zip(inr_values, day_change_pcts))) < 0.01"
examples:
  - given: '{"day_pnl": 2000.0, "inr_values": [100000.0], "day_change_pcts": [2.0]}'
    expect: "true"
  - given: "₹1,00,000 holding up 2% today → ₹2,000 day P&L"
    expect: "₹2,000"
seal: 4669fe7da358d347
---
**Rule:** Today's P&L is computed on *current* INR value, not invested cost:
`day_pnl = Σ (inr_value(h) × day_change_pct(h) / 100)`.

**Why:** `day_change_pct` is already relative to *yesterday's close*, so it must
multiply today's market value, not the original cost. Using invested cost would
double-count appreciation. `day_pnl_pct = day_pnl / current × 100`, and is forced
to `0` when current value is `0` (div-by-zero guard).

**Edge cases:** brokers that don't populate `day_change_pct` contribute `0` — the
sum is robust to missing data, never NaN.
