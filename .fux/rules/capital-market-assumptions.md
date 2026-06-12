---
id: capital-market-assumptions
domain: portfolio
type: rule
status: active
created: 2026-06-12
updated: 2026-06-12
---
# Capital-market assumptions — expected returns used for projections

**Rule:** Every forward projection Anton shows (Orff answers, `/plans/projection`,
composed charts) uses **these** long-term nominal return assumptions — never
ad-hoc numbers invented per answer. Percentages only — generic market estimates,
zero personal data, so this entry is git-safe by construction. Personal amounts
(initial corpus, SIP) enter only at request time and are never persisted here
(see [[plan-store]]).

`projection_service.py` reads the fenced YAML; Orff cites this entry
(`fux why capital-market-assumptions`) whenever it presents a projection, so
every number in a projection is auditable back to one committed source.

## Assumptions (machine-read)

```yaml
# Long-term nominal expected returns, % per annum (India, conservative CMA-style)
expected_return_pa:
  equity: 12.0
  mutual_fund: 11.0
  bond: 7.0
  gold: 8.0
  crypto: 15.0
  cash: 4.0
inflation_pa: 5.0
```

## Notes

- These are planning assumptions, not forecasts; revise them here (one place)
  when conviction changes — every consumer updates automatically.
- "Real" projection series are nominal deflated by `inflation_pa`.
- Crypto's premium reflects its volatility — the [[core-allocation]] band (1.5pts)
  is what keeps its weight honest, not the return assumption.

## Related

[[portfolio-valuation]] · [[plan-store]] · [[core-allocation]] · [[day-pnl]]
