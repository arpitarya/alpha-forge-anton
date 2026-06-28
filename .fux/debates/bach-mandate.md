# Debate — `bach-mandate` → constitutional (proposed)

**Proposed rule:** "Bach is the suite's single secrets vault; every secret lives in
bach under a namespaced app token, never in committed `.env` or the tree; bach
refuses a KDF weaker than Argon2 and binds 127.0.0.1; Anton reaches secrets only
through `vault_client.load_from_vault`, never a silent fallback to a committed
secret."
**Tier sought:** constitutional (apex — always-blocking, sealed)
**Date:** 2026-06-28
**Format:** two-agent free debate (anti-sycophancy). Both agents briefed identically,
side-free, blind to each other's first pass. Human is tie-breaker + ratifier.

---

## Blind first pass — Agent A

**Position: REJECT as a separate constitutional rule** (amend `vault-only-credentials`).

Cost-half passes (`vault-only-credentials.md:22-26` — these keys "identify a real
brokerage account holding real money"; a leak is irreversible). But three things break
the wording:

**(c, the sharp one) The rule seals a claim the code contradicts.** `vault_client.py`
is a *deliberate fallback by design*: docstring line 8 "file env is the fallback"; no
`AFBACH_TOKEN` → `return 0` (file env still works); vault unreachable → `logger.warning
(… "using file env")` → `return 0`. Sealing "never fallback to a committed secret"
constitutionalises a lie — the failure a prior debate caught. The enforceable kernel is
narrower: line 62-63 hardens *non-development* — a **locked** vault (503) raises rather
than falling through.

**(b) Half the rule is unenforceable from anton.** Argon2-refusal and 127.0.0.1-bind
live in the **bach repo** (`README.md:19,100`), not anton; `vault_client.py:24` even
defaults to `[::1]` and trusts `AFBACH_URL`. Anton's `.fux/` can't gate bach's KDF —
theater. Those are also prong-two failures: a future KDF upgrade is a *legitimate*
mechanism change.

**(a) Duplicates `vault-only-credentials`** — same vault, same no-VCS, same unlock-hint.
The genuine delta is scope-widening (LLM keys, wagner's JWT/DATABASE_URL).

**Amended:** bind to what anton enforces — secrets never in VCS + read only via
token-scoped `vault_client`; in non-dev a locked vault is a hard error with unlock hint,
never silent fall-through; dev may fall back for migration. Argon2/bind described as
fact, not sealed.

## Blind first pass — Agent B

**Position: adopt-amended** (promote/relate `vault-only-credentials`; don't seal bach's mechanics).

The core — "single vault, secrets never in VCS" — passes both prongs: a committed key is
one `git add -A` from permanent history; "don't commit secrets" never legitimately
changes. Apex-grade. But the wording overreaches exactly twice: (1) it seals bach's
internal mechanics (Argon2, 127.0.0.1) anton cannot enforce and which can legitimately
change — sealing "Argon2" forces a constitutional supersede to do a routine crypto bump;
(2) it contradicts shipped code — `vault_client.py` is *built* as a migration fallback
(no token → no-op; unreachable → "using file env"), so "never fallback" makes current
intentional design unconstitutional on day one.

**Objection:** the constitutional core is narrow — *secrets never committed + anton reads
only through the token-scoped `vault_client` path*. Bach mechanics belong in bach's own
rules/README as cited fact. Heavy overlap with `vault-only-credentials` means a separate
charter is redundant; promote/relate rather than duplicate.

**Amended:** "No secret — broker creds, LLM keys, wagner's JWT_SECRET/DATABASE_URL — is
ever committed to VCS or left in the tree; secrets resolve only through
`vault_client.load_from_vault` (token-scoped, vault overrides file). A missing/locked
vault surfaces an unlock hint, never a silent leak. (Fact, not sealed: bach enforces
Argon2id + 127.0.0.1 bind; the file-env path is a migration fallback to be removed.)"

---

## Adversarial round (host)

Both agents converged blind: the apex core is "secrets never in VCS + anton reads only
via token-scoped `vault_client`"; bach's KDF/bind are mechanism (unenforceable from
anton + legitimately changeable) to describe as fact, not seal; and "never fallback"
contradicts shipped code. I verified `vault_client.py` exactly: 403 → `RuntimeError`
(invalid token, all envs); 503 **locked** → raises only when `APP_ENV != development`,
else warn + `return 0`; **unreachable** (`URLError`/timeout) → warn + `return 0` in *all*
envs (the migration fallback). So even the non-dev hardening covers only the *locked*
case, not the *unreachable* one — the fallback is real and broader than "never." Sealing
"never fallback" would be false. Convergence survives falsification.

## Converged outcome

Author **`bach-mandate`** as the suite charter (the human ratifier wants the symmetry),
but seal only the enforceable invariant:
1. Bach is the canonical secrets home; **no secret is ever committed to VCS or left in
   the tree**; Anton reads secrets only through token-scoped `vault_client.load_from_vault`
   (vault overrides file). Bound to `vault_client.py` + `broker_env.py`.
2. The **file-env path is a documented migration fallback** (unreachable vault, or a
   dev-mode locked vault) — to be removed once the vault is canonical; in non-dev a
   *locked* vault is already a hard error with an unlock hint.
3. Bach's Argon2 KDF + 127.0.0.1 bind are **described as fact, not sealed** (bach-owned,
   legitimately upgradeable).
4. `vault-only-credentials` is the specific broker-credential instance — **linked, not
   duplicated** (the plan-store ↔ elgar-mandate pattern).

## Residual risk

- The migration fallback is a real exception to "vault-only" until removed; tracked in
  the rule as fact, and broker creds are already gated by `vault-only-credentials` +
  `no-secrets-in-vcs`. Lower blast radius than sealing a false absolute.
