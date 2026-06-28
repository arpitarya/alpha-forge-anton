# Debate — `wagner-mandate` → constitutional (proposed)

**Proposed rule:** "Wagner is the suite's identity & access layer; Anton holds NO
auth logic of its own — every `/iam/*` is forwarded to Wagner via `iam_proxy`;
identity, RBAC, refresh-token rotation with reuse detection, API keys, and the
audit log live in Wagner; legacy single-credential env auth is forbidden."
**Tier sought:** constitutional (apex — always-blocking, sealed)
**Date:** 2026-06-28
**Format:** two-agent free debate (anti-sycophancy). Both agents briefed identically,
side-free, blind to each other's first pass. Human is tie-breaker + ratifier.

---

## Blind first pass — Agent A

**Position: adopt-amended.**

`iam_proxy.py` is a genuine pure forwarder (`_forward` lines 18-40 → `settings.wagner_url
/api/v1/iam/{path}`; no token validation, no role checks, no credential store). The
migration pair `a3c9f2e1b4d7_iam_tables` → `b3d6f8a2c9e1_remove_iam_tables` is physical
evidence of completed delegation. A grep of `app/core` for `AUTH_TOKEN`/legacy single-cred
returned **nothing** — the legacy auth is already *absent*, not merely "forbidden."

**Objection (fatal to the broad wording):** mostly unenforceable-from-anton theater. Of
the clauses, anton can enforce exactly one — *"`iam_proxy` stays a pure forwarder with no
local auth logic."* Rotation, reuse detection, role model, audit log live in the **wagner
repo**; anton sealing them charters code it can't touch (a wagner refactor would violate
an *anton* constitutional rule without editing anton). **And prong two fails:** "anton
holds NO auth logic" can legitimately change — local *stateless* token introspection
(verify a JWT via Wagner-published JWKS to avoid a per-request hop) is a sane optimisation
and is literally "auth logic in anton."

**Amended (`standard`):** Anton's `/iam/*` is a pure pass-through to Wagner; Anton MUST NOT
persist identity/credential records or own the authorization decision; local *stateless*
token verification (JWKS) is permitted but never the source of truth; the removed
`iam_tables` stays removed.

## Blind first pass — Agent B

**Position: adopt-amended.**

Pure forwarder confirmed: `_forward` copies headers minus hop-by-hop (`_STRIP_REQ` line
14), streams body/params, returns Wagner's status/body verbatim; no password/JWT/role
logic in Anton. The alembic pair is proof Anton *had* IAM tables and deliberately deleted
them — exactly `elgar-mandate`'s delegation shape. Wagner README confirms reuse detection /
audit / API keys live in Wagner.

**Objection (two):** (a) **Scope theater** — "reuse detection," "audit log lives in
Wagner," "secrets in bach" are *Wagner's* facts, not anton's to seal; a Wagner refactor
would force re-ratifying an *anton* rule. Only the delegation half is enforceable here.
(b) **Anton DOES make one auth decision:** `iam_proxy.py:30-33` rewrites a Wagner `401`
to `204` on logout — Anton overriding Wagner's verdict, inside a rule that says Anton
holds *none*. The wording is literally false against its own `code_refs`; needs a
presentation-only carve-out.

**Amended:** seal only the delegation invariant; demote Wagner internals to descriptive
context (as elgar-mandate did with `store.py`); carve out the logout rewrite as
presentation-only, never an authorization decision; add a probe asserting `iam_proxy`
holds no auth primitive. Consider `standard` ADR `anton-delegates-wagner` unless the
suite-charter symmetry is wanted.

---

## Adversarial round (host)

Both agents converged blind: the enforceable apex invariant is the **delegation** —
*Anton owns no auth logic; `iam_proxy` is a pure forwarder; the removed `iam_tables` must
never return* — elgar-mandate's twin. I verified: `iam_proxy.py` forwards 1:1 to
`settings.wagner_url` (config default `http://127.0.0.1:8001`); the only local logic is
the logout `401→204` normalisation (lines 30-33); no auth primitive anywhere. Two
amendments are mandatory for the wording to be *true*: (1) permit local **stateless**
signature verification/caching that is never the source of truth (answers prong-two —
otherwise a normal JWKS optimisation would breach the apex); (2) carve out the logout
rewrite as **presentation-only**. Wagner-internal features are descriptive, not sealed.
Convergence survives falsification.

## Converged outcome

Author **`wagner-mandate`** as the suite charter (human ratifier wants the symmetry with
elgar-mandate), sealing only what anton enforces:
1. **Anton owns no auth logic.** Identity/access delegated entirely to Wagner; every
   `/iam/*` is forwarded by `iam_proxy` to `settings.wagner_url` as a transparent proxy —
   no password/token/role/session decision of its own; the removed `iam_tables` migration
   must never return. Bound to `iam_proxy.py` + `config.py` + `b3d6f8a2c9e1…`.
2. **Carve-outs (so the rule is true):** local *stateless* token verification (JWKS
   signature check / caching) is permitted but never the source of truth; any proxy
   response-rewriting (the logout `401→204`) is presentation-only, never an authorization
   decision.
3. **Descriptive, not sealed (Wagner-owned):** identity records, owner/viewer roles,
   refresh-token rotation + reuse detection, API keys, audit log; Wagner's own secrets
   live in bach ([[bach-mandate]]).

## Residual risk

- The logout carve-out is a real (benign) local response edit; if it ever grows into an
  authorization decision it breaches the rule — that is exactly what the carve-out makes
  catchable. A probe asserting `iam_proxy` holds no auth primitive would harden it.
