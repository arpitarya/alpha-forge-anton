---
id: holding
domain: brokers
type: glossary
status: active
created: 2026-06-09
updated: 2026-06-09
code_refs:
  - backend/app/modules/brokers/broker_schemas.py
related: [portfolio-valuation, inr-normalization, holdings-sum-equals-total, source-kind-status, broker-source]
aliases: [position, holdings]
keywords: [holding, position, quantity, pnl, invested, current_value]
---
**Term:** Holding

**Definition:** The leaf unit of the portfolio — one position in one instrument
from one broker. A Pydantic model (`broker_schemas.py`) with `source` (slug),
`asset_class`, `symbol`, `quantity`, `avg_price`, `last_price`, `invested`
(`qty×avg`), `current_value` (`qty×ltp`), `pnl`, `pnl_pct`, and an optional
`currency` (default INR; USD for IndMoney/Binance). Every `BrokerSource.fetch()`
returns a `list[Holding]`; the [[holdings-aggregator]] rolls them up read-only.
Monetary fields are stored in the source's native currency and INR-normalised only
at aggregation ([[inr-normalization]]).
