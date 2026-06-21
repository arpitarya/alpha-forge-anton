---
id: trusted-lane-tools
domain: security
type: rule
status: active
created: 2026-06-16
updated: 2026-06-21
aliases:
  - tool-lane-policy
  - tools-trusted-only
  - deep-search-budget
keywords:
  - tools
  - tool-calling
  - trusted
  - lane
  - claude-sdk
  - grounding
  - parallel
  - budget
  - cage
code_refs:
  - backend/app/modules/concierge/tool_layer.py
  - backend/app/modules/concierge/tool_registry.py
  - backend/app/modules/concierge/deep_search_service.py
  - backend/app/modules/concierge/grounding_service.py
related:
  - secure-holdings-plan
  - mutation-confirm-rmw
  - concierge-registry-single-source
  - vault-only-credentials
---
**Rule:** Orff's tool-calling and paid web grounding are governed by the trusted lane.

- **Tools run on the trusted (`claude-sdk`) lane only.** A non-trusted provider gets **no
  tools** — never a degraded path. Data-bearing read tools (`review_holdings`,
  `latest_action_plan`) and **all** mutating tools are trusted-lane-only, permanently. If
  free-provider tools are ever added, they get **only privacy-safe reads** (percentages /
  points: `get_drift`, `get_strategy`, `get_objective`). Extends [[secure-holdings-plan]].
- **Routing is deterministic.** Whether to use a tool, think harder, or deep-search is decided
  by intent routing + the model's own judgement — **never a separate LLM classifier on the hot
  path**. If intent is too coarse, extend the deterministic router with keyword signals.
- **Agent-initiated paid actions are confirm-gated, budget-capped, Cage-metered, fail-open.**
  Deep search is a `request_deep_search` tool: Orff asks (reasons + cost), **no Parallel call
  until confirm**; over `parallel.monthly_budget_inr` it degrades to free sources and says so;
  every call records a Cage receipt; any error → free-source answer, never a dead stream.
  Mode is tri-state `deep_search_mode` (Auto / Always / Never).

**Why:** private holdings/plan data must only reach the user-confirmed paid provider; paid
calls must stay capped and visible (the ₹ target); the live chat path must never break.

**How:** mutations follow [[mutation-confirm-rmw]]; keys come from the vault
([[vault-only-credentials]]); prices live in the manifest ([[concierge-registry-single-source]]).
