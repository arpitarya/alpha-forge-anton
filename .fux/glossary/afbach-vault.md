---
id: afbach-vault
domain: security
type: glossary
status: active
created: 2026-06-09
updated: 2026-06-09
code_refs:
  - backend/app/core/vault_client.py
related: [vault-only-credentials, no-secrets-in-vcs, project-wagner-dante]
aliases: [afbach, vault, alpha-forge-bach, bach]
keywords: [vault, afbach, secrets, unlock, credentials, 54087]
---
**Term:** afbach vault (alpha-forge-bach)

**Definition:** The sibling secrets manager that holds every broker credential and
runtime secret. The backend reads keys through `vault_client.py`; a locked vault
reports `vault_locked()` so sources surface `UNCONFIGURED` with an unlock hint
instead of failing opaquely. Store a secret with
`PUT http://[::1]:54087/v1/secrets {"key": ..., "value": ...}`; unlock with
`afbach unlock`. No broker credential ever lives in `.env` or the tree
([[vault-only-credentials]], [[no-secrets-in-vcs]]). Part of the Wagner/Dante
security layer ([[project-wagner-dante]]).
