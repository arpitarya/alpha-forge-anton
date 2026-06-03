---
id: project-wagner-dante
domain: project
type: memory
subtype: project
scope: shared
status: active
created: 2026-05-25
updated: 2026-06-03
---
Wagner IAM and Dante security have been fully integrated as of 2026-05-25.

**Why:** Replace the single-user admin password auth with a proper multi-user IAM system (Wagner) and add layered security hardening (Dante).

**How to apply:** These are live — all auth routes, frontend store, and backend security layers are in place.

## Wagner IAM

**IAM is now exclusively owned by Wagner** — Anton is a pure proxy. Data lives in Wagner's SQLite (`wagner/backend/wagner.db`), NOT Anton's PostgreSQL.

- Wagner runs on `:8001`; Anton runs on `:8000`
- Anton `backend/app/modules/iam/iam_proxy.py` — thin httpx reverse proxy forwarding all `/api/v1/iam/*` → Wagner `:8001/iam/*`
- Anton `core/deps.py` — stateless JWT validation only; returns `UserClaims(id, role, email)` dataclass; no DB lookup
- Anton `core/config.py` — `wagner_url = "http://127.0.0.1:8001"` (configurable via `WAGNER_URL` env var)
- Alembic migration `b3d6f8a2c9e1_remove_iam_tables.py` dropped the IAM tables from Anton's PG
- Routes at `/api/v1/iam/*`: login, register, refresh, logout, me, users, audit, api-keys (all proxied to Wagner)
- Login is JSON `{email, password}` — `POST /api/v1/iam/login`
- First `POST /iam/register` on Wagner is open (bootstrap); subsequent require owner JWT
- JWT payload: `sub` (Wagner guid UUID), `role`, `email`
- Wagner schema: `iam_users` has `uid` (int PK) + `guid` (UUID, exposed in JWT sub)

## Wagner Frontend

- `frontend/src/modules/auth/auth.types.ts` — IamUser, TokenResponse, etc.
- `frontend/src/modules/auth/auth.api.ts` — axios instance + all IAM endpoints
- `frontend/src/modules/auth/useAuthStore.ts` — zustand store with rotating refresh, silent-refresh interceptor, bootstrap
- `frontend/src/modules/auth/auth.guard.tsx` — uses useAuthStore (not raw localStorage)
- `frontend/src/app/login/page.tsx` — email+password (not username), uses useAuthStore
- `frontend/src/lib/api.ts` — 401 handler tries silent refresh before redirecting to /login

## Dante Security

Dante (`alphaforge-dante`) added as path dep: `{ path = "../dante" }` in root pyproject.toml.

All Dante integrations use try/except ImportError so they degrade gracefully if Dante isn't installed.

| Component | File | What it does |
|-----------|------|-------------|
| redactor | `core/logging.py` | Scrubs PII/secrets from every log record |
| warden | `main.py` | `warden.install(app)` — IP allowlist middleware after CORS |
| curator | `brokers/dump_utils.py` | `safe_resolve(name, root=dump_dir())` prevents path traversal on CSV paths |
| watchman | Wagner `modules/iam/iam_service.py` | `on_failed_login(ip, n)` called on login failure (in Wagner, not Anton) |
| gateway | `brokers/_http.py` | `wrap_httpx(client, load_policy(...))` on every broker HTTP client |
| posture | `core/deps.py` | `decide(score, path, rules)` — STEP_UP or BLOCK based on posture.yaml |
| inferno | `frontend/src/app/layout.tsx` | Hidden honeypot anchor `/.well-known/honeypot-af1337` |

Justfile recipes: `just dante-audit`, `just dante-audit-deep`, `just dante-harden`.
`just dante-harden` regenerates `frontend/public/robots.txt`.

## Old Auth

The old `backend/app/modules/auth/` (single admin user, form-based `/auth/token`) is no longer mounted. The module still exists on disk but is excluded from `modules/__init__.py`. Can be deleted later.
