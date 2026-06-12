---
id: emergency-fund-first
domain: portfolio
type: rule
status: active
created: 2026-06-12
updated: 2026-06-12
related: [core-allocation, rebalancing-policy, plan-store]
aliases: [emergency-fund, liquidity-buffer, cash-floor]
keywords: [emergency, liquidity, cash, buffer, 6-months]
---
**Rule:** an emergency buffer of **6 months of expenses (12 if income is
volatile)** in same-week-liquid instruments — savings, FDs, liquid/overnight
funds — is a precondition for risk-asset advice, not a portfolio position:

- it is excluded from rebalancing: a "hot" cash class is never trimmed below
  the buffer ([[rebalancing-policy]] must respect it as a floor);
- equity, crypto, and gold never count toward it — an emergency is exactly
  when they are most likely to be down ([[drawdown-recovery]]);
- the months-of-expenses target lives in the personal plan in the elgar store
  ([[plan-store]]); this repo holds only the rule, never the figure.

**Why:** the buffer's return is not its yield — it is the option to never sell
risk assets at the bottom. A forced sale in a 40% drawdown converts a paper
loss into a permanent one and typically incurs STCG on whatever was up. The
buffer also collapses sequence-of-returns risk for any SIP plan: instalments
continue through downturns instead of being diverted to emergencies.

**How to apply:** before Orff recommends increasing equity/crypto exposure or
deploying idle cash, it should confirm the buffer exists (ask, or read the
plan's cash floor) — and when the cash class shows "hot" drift, distinguish
deployable surplus from the untouchable buffer rather than advising "invest
the lot".
