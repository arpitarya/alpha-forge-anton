# AlphaForge Anton — Guardrails

## Security

- Never commit `.env` files or API keys — add new vars to the appropriate `.env.example` instead
- Broker tokens encrypted at rest
- CORS restricted to frontend origin only; allowed methods/headers are explicit (not `*`)
- No guaranteed return claims anywhere in code or UI
- All financial amounts use `float` for now (will migrate to `Decimal` before production)
- Password hashing uses `bcrypt` directly (passlib removed — incompatible with bcrypt 4.x)
- Auth enforced via `Depends(get_current_user)` on all routes except `/health` and `/auth/token`
- Dev login credentials stored in afbach vault (`ADMIN_USERNAME` / `ADMIN_PASSWORD`) — never hardcode them; must set `ADMIN_PASSWORD_HASH` in production
- Cloud LLM providers disabled in `APP_ENV=development` unless `ALLOW_CLOUD_LLM_IN_DEV=true`
- Broker outbound HTTP guarded against unapproved hosts in dev mode via `BROKER_ALLOWED_HOSTS`
- Run `just audit` to scan Python + Node dependencies for known CVEs

## Documentation

- Every code change must be accompanied by a documentation update in the same session
- Detailed project docs in `docs/`: WHY.md (vision), WHAT.md (features), HOW.md (architecture), GETTING_STARTED.md (setup)

## Planning

- When planning a new module or feature, create a `PLAN.md` inside that module's directory with the full plan, goals, phases, and design decisions; then link it from the root-level `PLAN.md` so all plans can be tracked from one place

## Implementation Tracking

- When a new module or feature is built, create an `implement.txt` inside that module's directory logging what was built, decisions made, and status; then link it from the root-level `implement.txt` so all modules can be tracked from one place

## File Layout

- Follow naming rules in [structure/README.md](../structure/README.md). Each top-level module has its own `files.md` and `variables.md`; consult them before creating a new file or naming a new symbol
- Files ≤ 100 lines (≤ 50 for `*_utils.py` / `*.utils.ts`) — see [conventions.md](conventions.md)

## Environment Variables

- All ports defined in `.env.port` at repo root
- Add new vars to the appropriate `.env.example` file — never commit `.env`

## Broker CSV Dumps

- All broker holdings dumps must use `dump_utils.py` — see [broker-csv-dumps.md](broker-csv-dumps.md)
