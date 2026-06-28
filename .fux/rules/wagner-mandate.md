---
id: wagner-mandate
domain: security
type: convention
status: active
tier: constitutional
created: 2026-06-28
updated: 2026-06-28
keywords:
  - wagner
  - iam
  - identity
  - auth
  - delegation
  - proxy
code_refs:
  - backend/app/modules/iam/iam_proxy.py
  - backend/app/core/config.py
  - backend/alembic/versions/b3d6f8a2c9e1_remove_iam_tables.py
related:
  - bach-mandate
  - elgar-mandate
  - configurable-paths
seal: ddf81aec9399127c
ratification:
  by: arpit arya
  date: 2026-06-27
  content_seal: 69d29608ceb8f385
  debate_hash: 904a52a470d3648d
---
# Wagner mandate — identity & access, fully delegated

**Constitutional:** **Anton owns no authentication or authorization logic.**
Identity and access are delegated entirely to **Wagner (`alpha-forge-wagner`)**:
every `/iam/*` request is forwarded by `iam_proxy` to `settings.wagner_url`
(`/api/v1/iam/…`) as a **transparent proxy** — Anton performs no password, token,
role, or session decision of its own, and the **removed `iam_tables` migration
(`b3d6f8a2c9e1`) must never return.** Anton having once held its own IAM tables and
deliberately deleted them is the shape this rule seals: a single identity-of-record,
in Wagner, never split back into Anton.

**Carve-outs (so the rule is exactly true to the code):**
- Local **stateless** token verification — a JWKS signature check / cache to avoid a
  per-request hop — is **permitted**, but Wagner remains the **source of truth**; a
  local check may reject a bad signature, never *be* the authorization decision.
- Any proxy response-rewriting — e.g. the logout `401 → 204` normalization in
  `iam_proxy.py` — is **presentation-only** and may never become an authorization
  decision. (This is the one piece of local logic in the proxy today; the carve-out
  is what keeps it honest.)

**Descriptive (Wagner-owned, NOT sealed here):** identity records, role-based access
(`owner` / `viewer`), refresh-token rotation with reuse detection, programmatic API
keys, and the audit log all live in Wagner. These are Wagner's internals — cited as
fact, never sealed at Anton's apex, because Anton cannot enforce a foreign repo's
behaviour and a Wagner refactor must not breach an *Anton* rule. Wagner's own secrets
(`JWT_SECRET`, `DATABASE_URL`) live in bach ([[bach-mandate]]).

**Why:** If Anton grows a second login path or its own credential store, the
identity-of-record silently splits — two systems disagree about who someone is, and
the audit log in Wagner no longer sees the whole picture. That is a trust- and
audit-integrity failure, irreversible after the fact. Delegation keeps one auditable
door. The invariant ("Anton owns no auth logic") never legitimately changes; the
stateless-verification carve-out is precisely what prevents a normal performance
optimization from being mistaken for a breach.

**How to apply:**
- Auth in Anton → call Wagner through `iam_proxy`; never persist identity/credential
  records in Anton, never re-add IAM tables.
- A local token check is fine only as a stateless signature verification that defers
  to Wagner; if you need a real authorization decision, it belongs in Wagner.
- Guard: a probe asserting `iam_proxy` contains no auth primitive and forwards 1:1
  would harden this (recommended follow-up).

**Debate:** ratified over a recorded two-agent debate — both voices independently
reached the same shape: seal only the *delegation* invariant (elgar-mandate's twin),
permit stateless JWKS verification (else a sane optimization would breach prong two),
and carve out the logout `401→204` rewrite (without it the wording is false against
its own `code_refs`). See `.fux/debates/wagner-mandate.md`. The human ratifier chose
the constitutional tier and the suite-charter symmetry.

## Related

[[bach-mandate]] · [[elgar-mandate]] · [[fux-mandate]] · [[configurable-paths]]
