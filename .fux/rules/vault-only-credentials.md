---
id: vault-only-credentials
domain: security
type: convention
status: active
created: 2026-06-09
updated: 2026-06-09
code_refs:
  - backend/app/modules/brokers/broker_env.py
related: [no-secrets-in-vcs, broker-source-contract, project-wagner-dante]
keywords: [vault, afbach, secrets, credentials, env, required_env, source_ready]
---
**Convention:** Broker credentials — user IDs, client IDs, API keys — live **only**
in the afbach vault (`alpha-forge-bach`), never in any `.env` file and never in the
tree. `.env.cred.example` carries **non-secret config only**: TTLs, feature flags,
and bootstrap values that must survive a locked vault (e.g. `BROKER_CACHE_KEY`,
`JWT_SECRET_KEY`). Each source declares its keys in `REQUIRED_ENV` and gates
readiness with `source_ready()` / `require_env()` from
[broker_env.py](../../backend/app/modules/brokers/broker_env.py).

**Why:** these keys identify a real brokerage account holding real money. A secret
in `.env` is one `git add -A` from history, and history is permanent
([[no-secrets-in-vcs]]). Routing every key through the vault means a missing key
produces a clear `UNCONFIGURED` status with an unlock hint — not a silent 180s CDP
timeout, and not a leak. Secrets are owned by the Wagner/Dante security layer
([[project-wagner-dante]]).

**How to apply:** store the key with `PUT /v1/secrets {"key": "BROKER_USER_ID",
"value": "<id>"}` (unlock first: `afbach unlock`). List it in the source's
`REQUIRED_ENV`; the source auto-upgrades to `READY` on next startup or vault unlock.
Never add the key to `.env.cred.example`. If a credential was ever committed,
rotate it — deleting the file does not unleak it.
