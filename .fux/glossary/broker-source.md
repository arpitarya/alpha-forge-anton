---
id: broker-source
domain: brokers
type: glossary
status: active
created: 2026-06-09
updated: 2026-06-09
code_refs:
  - backend/app/modules/brokers/base.py
related: [broker-source-contract, holdings-aggregator, source-kind-status]
aliases: [source, adapter, broker adapter]
keywords: [broker, source, adapter, fetch, slug, registry]
---
**Term:** BrokerSource

**Definition:** The adapter abstraction (ABC in `base.py`) for one holdings
provider — Zerodha, Groww, Angel One, IndMoney, Ticker Tape, Binance, etc. Each
concrete source sets `slug`/`label`/`kind`, overrides `async fetch()`, and is
registered once in `registry.py`. The base class owns the lifecycle (`sync()`,
status, in-memory cache). A source is identified everywhere by its **slug** (e.g.
`"zerodha"`, `"angelone"`). Governed by [[broker-source-contract]].
