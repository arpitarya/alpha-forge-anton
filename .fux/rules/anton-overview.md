---
id: anton-overview
domain: product
type: narrative
status: active
created: 2026-06-03
updated: 2026-06-03
related: [project-wagner-dante, day-pnl, portfolio-valuation]
aliases: [what is anton, why anton, architecture overview]
keywords: [portfolio, terminal, indian markets, brokers, monorepo]
---
## Why Anton exists

**AlphaForge Anton** is a personal, self-hosted AI portfolio-management and
investment terminal for Indian markets. It unifies holdings scattered across many
brokers (Zerodha, Groww, AngelOne, IndMoney, Binance, …) into one currency-correct
view, computes valuation and P&L, and layers AI assistance (the Orff concierge)
on top — without sending a user's financial data to a third-party SaaS.

## Shape

A monorepo: a Python 3.14 / FastAPI backend and a Next.js 15 / TypeScript
frontend, MIT-licensed and self-hosted. The backend's `brokers` module is the
heart — each broker is a `BrokerSource` that fetches holdings into a cache; the
`HoldingsAggregator` rolls them up read-only (see [[portfolio-valuation]],
[[day-pnl]], [[inr-normalization]]). Auth/IAM is owned by a sibling service,
Wagner, with Anton acting as a proxy (see [[project-wagner-dante]]); broker UI and
holdings are verified through `probes/` (CDP), never Playwright MCP.

## Principles that recur

- **Currency-correct first** — every monetary value is INR-normalised at the leaf
  before any aggregation, so USD-priced holdings sit beside INR ones safely.
- **Small files, clear seams** — source files stay ≤100 lines; backend
  `{domain}_{role}.py`, frontend `{domain}.{role}.ts`.
- **Knowledge ships with code** — a code change carries its doc/rule update in the
  same session; this very substrate (`.fux/`) is where that knowledge lives.

> Migrated into Fux from `docs/architecture.md` + the WHAT/WHY/HOW narrative as a
> `type: narrative` entry (plan §11). The source docs remain until parity is
> verified and they are formally decommissioned.
