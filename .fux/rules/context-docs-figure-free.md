---
id: context-docs-figure-free
domain: security
type: rule
status: active
created: 2026-06-16
updated: 2026-06-18
aliases:
  - memory-figure-free
  - no-stale-figures
  - live-numbers-only
keywords:
  - context
  - memory
  - figures
  - holdings
  - drift
  - investor-profile
  - orff-context
code_refs:
  - backend/app/modules/concierge/memory_service.py
  - backend/app/modules/concierge/prompt_service.py
  - backend/app/modules/concierge/holdings_detail.py
related:
  - secure-holdings-plan
  - plan-store
  - signals-deterministic-core
  - position-concentration
seal: 92cf24b9f5e0f819
---
**Rule:** Orff's standing-context / memory docs hold **durable preferences and rules only —
never position figures**. Share counts, ₹ amounts, P&L %, and weights come **live from the
holdings disclosure** at chat time, never from a stored doc.

**Why:** figures in a context doc go stale and Orff then contradicts live data in the same
answer (the real bug: a doc said HDFC "~47%" / "NEOGEN +38%" while live was 21% / +49%). A
rule ("HDFC is the single largest position — flag before adding") stays true; a number rots.

**How it's enforced:**
- `memory_service.load_context()` injects the durable docs (`investor-profile`,
  `trading-sleeve-rules`, `hard-exclusion-list`, `portfolio-snapshot`) — all figure-free.
  `orff-context` is the user's free-text additions. (`load_memory`/`save_memory` stay scoped
  to `orff-context` for the Memory panel.)
- Live numbers arrive only via `holdings_detail`/disclosure on the trusted lane — see
  [[secure-holdings-plan]]; the engine's own figures are deterministic — see
  [[signals-deterministic-core]].
- A drift guard fails if any context doc carries a position figure.

This is the memory-doc counterpart of the two-plane money rule in [[plan-store]].
