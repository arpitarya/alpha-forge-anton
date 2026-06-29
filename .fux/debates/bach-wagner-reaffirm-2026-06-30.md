# Debate — re-affirm `bach-mandate` & `wagner-mandate` (staleness re-ratification)

**Date:** 2026-06-30 · **Driver:** host session · **Ratifier (pending):** Arpit
**Proposal:** re-ratify both locked constitutional mandates *as-is* to clear the
`gate` CI block, on the stated premise that their governed backend code was
committed 2026-06-29 (past the 2026-06-28 ratification).

> This is a review transcript for a *staleness* re-affirmation. It does **not**
> overwrite the sealed authoring transcripts `bach-mandate.md` / `wagner-mandate.md`.

## Threshold finding — the premise is FALSE (Reviewer B, confirmed by driver)

The two mandates are **not** genuinely drifted:
- Real git commit dates (full local clone): `vault_client.py` 2026-05-26,
  `config.py` 2026-06-01, `iam_proxy.py` 2026-05-27, migration `b3d6f8a2c9e1`
  2026-05-25. **Nothing in the governed paths moved on 2026-06-29.**
- `fux check` (full history) flags only `probe-cdp-not-playwright` as drifted —
  neither bach nor wagner.
- **Root cause of the red gate:** `.github/workflows/constitution.yml` `gate` job
  checks out **shallow** (`actions/checkout@v4`, no `fetch-depth: 0`, line 10–11).
  In a depth-1 clone `git log <file>` returns only the HEAD commit, so fux's
  staleness check sees *every* governed file as "changed" at the PR HEAD date
  (2026-06-29) and marks *every* rule with an older `updated:` stale. This is a CI
  checkout-depth bug, not constitutional drift. (Secondary: line 19 installs
  `fux-engine>=0.4.0`, a floor that violates `fux-engine-exact-pin`.)

**Consequence:** re-ratifying bach/wagner would re-seal clean rules against code that
never moved, and would *rot again on the next day's CI run* (updated date < new HEAD
date). It masks the real fix.

## Blind pass — Reviewer A & Reviewer B (converged on merits)

Both independently: **re-affirm both as-is on the merits** — the shipped code
complies with each mandate's literal text; the removed IAM migration has not
returned; no secret literal is in VCS. Both raised the same two concrete objections:

- **wagner-mandate:** the carve-out authorizes *stateless JWKS (asymmetric)*
  verification that "may reject a bad signature, never *be* the authorization
  decision." The code drifted from that: `config.py:31-32` + `security.py:12` use a
  **symmetric HS256 shared secret** (Anton can therefore *mint* tokens, not just
  verify), and `deps.py:39-74` (`require_owner`) makes a **local owner/viewer
  authorization decision** off the JWT `role` claim with no Wagner round-trip.
  Sealing as-is blesses HS256-shared-secret + local role-gate as constitutionally
  compliant — the precedent most likely to be cited to creep auth back into Anton.
- **bach-mandate:** the file-env fallback is sealed as a "shrinking exception," but
  no code shrinks it — `load_from_vault` silently returns 0 when `AFBACH_TOKEN` is
  unset (and in `development` a locked vault also falls through), with no telemetry,
  deprecation, or count. "Shrinking" is aspirational, unenforced. Also: bach's own
  `code_refs` hold no commit-time secret scanner — leak prevention actually lives in
  the `dante pii` lane, so the seal gives false assurance.

Reviewer A's sharpest single item for the ratifier: **wagner's HS256 + local
`require_owner`** is the one place re-affirming "as-written" risks blessing exactly
what the mandate exists to forbid. Reviewer A: amend wagner to add `config.py`/
`deps.py`/`security.py` to a "local stateless-verify surface" note so the carve-out
is true to the code; Reviewer B: same, plus make bach's "shrinking" observable.

## Anti-sycophancy gates

- Each reviewer surfaced ≥1 concrete objection ✓
- Both genuinely tried to falsify — B broke the premise; both broke the "spirit" of
  each seal ✓
- Convergence is on the *merits text*, but rests on a **falsified premise** and two
  unresolved cruxes → **escalate to human**, do not author/ratify.

## Outcome — ESCALATED to human ratifier (Arpit)

Recommended (driver): **do not re-ratify bach/wagner.** Fix the root cause —
add `fetch-depth: 0` to the `gate` job checkout (and pin `fux-engine` exactly in the
workflow). That makes staleness accurate and turns the gate legitimately green
without re-affirming anything. Treat the two latent gaps (wagner HS256 / `require_owner`,
bach "shrinking" fallback) as follow-up ADRs or mandate amendments — real, but not
merge blockers.

Residual risks: documented above. No ratification performed by the agent.
