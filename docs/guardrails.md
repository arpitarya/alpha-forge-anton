# AlphaForge Anton — Guardrails

## Security

- Never commit `.env` files or API keys — add new vars to the appropriate `.env.example` instead
- Broker tokens encrypted at rest
- CORS restricted to frontend origin only; allowed methods/headers are explicit (not `*`)
- No guaranteed return claims anywhere in code or UI
- All financial amounts use `float` for now (will migrate to `Decimal` before production)
- Password hashing uses `bcrypt` directly (passlib removed — incompatible with bcrypt 4.x)
- Auth enforced via `Depends(get_current_user)` on all routes except `/health` and `/auth/token`
- Auth handled by Wagner IAM — user credentials managed in Wagner's database; probe credentials stored in afbach vault as `PROBE_USER` / `PROBE_PASS`
- Cloud LLM providers disabled in `APP_ENV=development` unless `ALLOW_CLOUD_LLM_IN_DEV=true`
- Broker outbound HTTP guarded against unapproved hosts in dev mode via `BROKER_ALLOWED_HOSTS`
- Run `just audit` to scan Python + Node dependencies for known CVEs
- **Money documents never live in this repo.** Personal & strategy plan docs (`*.plan.md`, `*.drift.md`, anything with personal financial figures) belong in the private elgar store (`elgar save <id>`, default `~/.alphaforge-anton/elgar`); commit only `elgar://plan/<id>` links. Enforced by `just dante-pii` (also in the pre-commit hook with `DANTE_ENFORCE=true`) and `just probe plan-safety` — see `fux why plan-store`

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
- **Broker user IDs and API keys must live in the afbach vault, never in `.env` files** — vault-only keys are not listed in `.env.cred.example`
- Vault-aware env helpers are in `broker_env.py`: use `source_ready(REQUIRED_ENV, env)` in source `__init__` and `require_env(key, env)` in acquire functions — both surface a `vault locked` hint automatically

## UI Verification

- **Always use probes (`probes/`) for all UI and broker verification — never Playwright MCP**
- Probes attach to the existing Chrome session via CDP (port 9299) — the same session the broker scrapers already use. No extra browser setup required.
- Each probe is a Python script checked into the repo, runnable independently of Claude: `just ui-probe`, `just ui-portfolio`, `just probe-zerodha`, etc.
- See [probes/WHY_PROBES_NOT_MCP.md](../probes/WHY_PROBES_NOT_MCP.md) for the full rationale.
- When adding a new UI feature or broker, add a corresponding probe in `probes/` and a `just` recipe in the justfile before considering the feature verified.
- Playwright MCP is acceptable only for ad-hoc one-off exploration of external third-party pages where no project internals are needed.

## Broker CSV Dumps

- All broker holdings dumps must use `dump_utils.py` — see [broker-csv-dumps.md](broker-csv-dumps.md)
