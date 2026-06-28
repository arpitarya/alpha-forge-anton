---
id: bach-mandate
domain: security
type: convention
status: active
tier: constitutional
created: 2026-06-28
updated: 2026-06-28
keywords:
  - bach
  - afbach
  - vault
  - secrets
  - credentials
  - no-secrets-in-vcs
code_refs:
  - backend/app/core/vault_client.py
  - backend/app/modules/brokers/broker_env.py
related:
  - vault-only-credentials
  - wagner-mandate
  - plan-store
seal: 8f028ba26409a625
ratification:
  by: arpit arya
  date: 2026-06-27
  content_seal: b1a11fc7a4c4a884
  debate_hash: df6a277c44696802
---
# Bach mandate — the suite's single secrets vault

**Constitutional:** **Bach (`alpha-forge-bach`) is the canonical home for every
secret.** Broker credentials, LLM API keys, and wagner's `JWT_SECRET` /
`DATABASE_URL` live in bach under a **namespaced app token** — **never committed to
a `.env` in version control and never left in the tree.** A leaked secret is one
`git add -A` from permanent history, and history is forever; this is the
irreversible-leak surface the apex exists to close.

Anton reaches secrets **only** through `vault_client.load_from_vault` (token-scoped
via `AFBACH_TOKEN`; vault values override file values), and each broker source gates
readiness through `broker_env.py` (`REQUIRED_ENV` / `source_ready()`), so a missing
key is a clear `UNCONFIGURED` status with an unlock hint — never a silent timeout or
a committed-secret shortcut.

**Migration fallback (fact, scoped, to be removed):** `vault_client.py` ships a
deliberate file-env fallback for the vault migration — no `AFBACH_TOKEN` → no-op;
an **unreachable** vault → log and continue on file env. The hardened edge already
in code: an **invalid token** always errors, and in non-development a **locked**
vault (503) is a hard `RuntimeError` with an unlock hint rather than a silent
fall-through. The sealed invariant is *no secret in VCS + bach as the single home
read via `vault_client`*; the file-env path is a documented, shrinking exception,
not a second secret home.

**Mechanism (fact, NOT sealed — bach-owned, legitimately upgradeable):** bach
refuses to start on a KDF weaker than **Argon2** (no silent downgrade) and binds
**127.0.0.1** by default. These live in the bach repo, not anton's substrate, and a
future KDF or bind change is a legitimate mechanism upgrade — so they are cited as
fact here, never sealed at anton's apex.

**Why:** Every key in bach identifies real money or a real identity. Routing all of
them through one token-scoped vault means a leak is impossible-by-default rather than
policed by review, and a missing key fails legibly instead of silently. Sealing only
what anton can enforce (no-VCS + the `vault_client` read path) keeps the rule honest;
bach's crypto is bach's to evolve.

**How to apply:**
- Store a secret → `afbach unlock` then `PUT /v1/secrets {"key": …, "value": …}` in
  the consumer's app namespace; never add it to a committed `.env`.
- Read a secret in Anton → it is injected into `os.environ` by
  `vault_client.load_from_vault`; never read a secret from a committed file as the
  source of truth.
- If a secret was ever committed → **rotate it** (deleting the file does not unleak
  it), per [[vault-only-credentials]] / `no-secrets-in-vcs`.

**Enforcement & relation:** [[vault-only-credentials]] is the specific
broker-credential instance of this charter (linked, not duplicated — the
[[plan-store]] ↔ [[elgar-mandate]] pattern). bach's Argon2/bind invariants belong
to bach's own substrate.

**Debate:** ratified over a recorded two-agent debate (both voices: seal only the
no-VCS + `vault_client` core; describe Argon2/127.0.0.1 as fact; "never fallback"
contradicts the shipped migration fallback in `vault_client.py`). See
`.fux/debates/bach-mandate.md`. The human ratifier chose the constitutional tier and
the suite-charter symmetry; the false absolute was corrected rather than sealed.

## Related

[[vault-only-credentials]] · [[wagner-mandate]] · [[elgar-mandate]] · [[plan-store]] · [[trusted-lane-tools]]
