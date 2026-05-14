# AlphaForge — Guardrails

## Security

- Never commit `.env` files or API keys — add new vars to the appropriate `.env.example` instead
- Broker tokens encrypted at rest
- CORS restricted to frontend origin only
- No guaranteed return claims anywhere in code or UI
- All AI outputs must include financial disclaimer: "Not SEBI registered investment advice"
- All financial amounts use `float` for now (will migrate to `Decimal` before production)

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
