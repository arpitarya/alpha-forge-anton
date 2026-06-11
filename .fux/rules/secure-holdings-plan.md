---
id: secure-holdings-plan
domain: security
type: narrative
status: active
created: 2026-06-11
updated: 2026-06-11
---
# Secure holdings access for Orff + the plan→drift→advise workflow

**Status:** _Shipped (steps 1–5) — plan plane, trusted-provider floor, disclosure
chokepoint, and both guard probes are live. Wiring holdings tools into Orff's
**tool-calling** loop (vs the current system-message injection) remains future work._
**Why this exists:** Orff routes to **free external LLM providers** (Groq, Mistral,
Gemini, OpenRouter, HuggingFace — see `concierge/.../registry/routing.json`). Today
`concierge_service.stream_chat` injects Fux grounding but **no holdings**, so nothing
has leaked yet. The moment we naively "inject holdings," symbols / quantities / ₹
amounts land in a third party's request logs. That is the primary threat — git
(public repo) is the second, because plan docs are committed.

## One principle — two planes that never cross

| Plane | Contains | Lives in | Leaves the machine? |
|---|---|---|---|
| **Data plane** (secret) | live holdings: symbols, qty, ₹ values, account IDs | broker `cached` (in-process) + gitignored `portfolio-dumps/` | Never in raw form |
| **Plan plane** (safe) | target %, drift bands, rebalance rules, named goals | committed `.fux/` (this substrate) | Yes — by design, it's strategy, not data |

**Drift** = committed targets (plan plane) × live actuals (data plane), expressed as
**percentages / bands only** → the drift report is safe to show and even to commit.

## Threat model (ranked)

1. **Third-party LLM leakage** — raw holdings in a prompt sent to a free provider.
2. **Public-git leakage** — ₹ amounts / account IDs / symbol lists in committed plan or drift docs.
3. **Browser/SSE leakage** — figures or secrets streamed to the client (errors already pass through `_redact`).
4. **At-rest** — CSV dumps, `concierge_turns` rows.

## Requirement A — most secure holdings access (4 layers, strongest first)

1. **Tools, not prompt-stuffing.** Expose server-side functions the model calls —
   `get_totals()`, `get_allocation()`, `get_drift(plan)` — running locally against
   `HoldingsAggregator`. They return only the answer asked for; nothing raw sits in
   the context window unless a tool deliberately puts it there.
2. **Least-disclosure by default** (`disclose-aggregate-only`). Tools return buckets /
   percentages (equity 58%, drift −2pts), never symbol rows or absolute ₹. Per-symbol
   or ₹ detail requires an explicit user ask + confirmation, gated through one
   redaction chokepoint (extend `_redact` → a `disclose()` layer that downgrades ₹→%
   unless escalated, and logs what was disclosed).
3. **Private-intent routing** (`portfolio-private-route`). A new `portfolio_private`
   intent pins holdings-bearing queries to a **local / trusted provider only**
   (`claude-sdk` confirmed, or a local model) — never the free third-party pool. A hard
   provider floor in the registry; `portfolio_overview` / `investment_plan` intents
   already exist as precedent.
4. **No persistence of raw figures.** Drift history + any ₹-level dumps go to gitignored
   `portfolio-dumps/`; turn logs store the redacted form only.

## Requirement B — generate → follow → show drift → advise → save

- **Plan = committed, git-safe spec.** A Fux narrative entry (see
  [[portfolio-plan-template]]) holding only: target allocation %, drift thresholds /
  bands, rebalance rules, named goals, horizon. **Zero personal figures.** This is what
  is safe in a public repo and makes plans reproducible + referenceable (`fux why`).
- **Generate.** Orff drafts the spec from a conversation → user reviews → it's
  committed. The plan overrides today's hardcoded `DEFAULT_TARGETS`.
- **Follow + show drift.** `get_drift(plan)` joins committed targets × live holdings →
  existing `RebalanceDrift(target_pct, actual_pct, drift_pct)`. Output is %-only → safe.
- **Tell me what to do.** `RebalanceSuggestion` actions as percentage moves
  ("trim equity ~2pts, add bonds ~3pts").
- **Save for later.** Plan spec → git (safe). Drift *history* → gitignored dump dir, or
  a redacted %-only entry if it should live in git.

## The git-safety guard (makes "public repo" real)

A probe + `just` recipe (and ideally a pre-commit / CI step) greps every committed plan
/ drift doc for ₹-amounts, account IDs, and known holding symbols, and **fails** if any
are found. This is the enforcement behind the two-plane rule — without it, "git-safe"
is a convention, not a guarantee.

## Build order

1. ✅ Plan schema ([[portfolio-plan-template]]) + first plan ([[core-allocation]]) +
   `plan_loader.py` (committed plan → `AssetClass` targets/bands) + `plan_safety_probe.py`
   git-safety guard (`just probe plan-safety`).
2. ✅ `portfolio_private` query-type + intent + a `private` manifest block
   (`trusted_providers`, `query_types`) in `registry/routing.json`; `registry.is_private` /
   `trusted_providers`; trusted-only chain. Frontend regenerated from the same manifest.
3. ✅ `holdings_private.py` — `disclosed_context()` (percentages-only, safe by construction)
   + `enforce_floor()` (overrides any free pin to the trusted floor, with a user notice).
   Wired into `concierge_service.stream_chat`: classify on the text, inject + floor when private.
4. ✅ `plan_drift.py` — `drift_for_plan()` joins plan targets/bands × live actuals via
   `aggregator.rebalance()` → band-aware per-class drift in points only.
5. ✅ `holdings_disclosure_probe.py` (`just probe holdings-disclosure`) — asserts disclosure is
   leak-free even when populated, and every private route lands on a trusted provider.

**Next (deferred):** move from system-message injection to real **tool-calling** so the model
pulls `get_drift` / `get_allocation` on demand; add a local model to `trusted_providers` so the
floor isn't paid-only; optional `<plan>.drift.md` history (redacted) for the save-for-later flow.

## Files this will touch (sketch)

- `concierge/.../registry/routing.json` — add `portfolio_private` intent + provider floor.
- `backend/app/modules/concierge/concierge_service.py` — `disclose()` chokepoint; tool wiring.
- `backend/app/modules/concierge/holdings_tools.py` (new) — `get_totals/get_allocation/get_drift`.
- `backend/app/modules/brokers/aggregator.py` — `rebalance()` accepts plan targets, not just `DEFAULT_TARGETS`.
- `backend/app/modules/brokers/plan_loader.py` (new) — parse targets/bands from the committed Fux plan entry.
- `probes/holdings_disclosure_probe.py` (new) + `just` recipe — leak guard + disclosure assertions.

## Open questions before build

- Which concrete provider is the "local / trusted" floor — `claude-sdk` confirmed only, or a local model?
- Plan targets: keep them in the Fux entry's frontmatter (machine-read) or a fenced YAML block in the body?
- Drift history: gitignored dump dir, or committed %-only? (Default: gitignored.)

## Related

[[portfolio-plan-template]] · [[holdings-aggregator]] · [[concierge-registry-single-source]] ·
[[vault-only-credentials]] · [[no-secrets-in-vcs]] · [[live-prices-plan]]
