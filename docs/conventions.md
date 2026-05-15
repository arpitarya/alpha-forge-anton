# AlphaForge — Coding Conventions

Full role suffix lists: [convention/python.md](../convention/python.md) · [convention/typescript.md](../convention/typescript.md)
Legacy violations: [convention/violations.md](../convention/violations.md)

## Hard Rules (every file)

- Files ≤ **100 lines** (≤ **50** for `*_utils.py` / `*.utils.ts`)
- Backend filenames: `<domain>_<role>.py` (e.g. `portfolio_routes.py`)
- Frontend filenames: `<domain>.<role>.ts` (e.g. `portfolio.query.ts`)

## Python

- Async everywhere — `async def` for all routes, services, and DB queries
- Absolute imports: `from app.core.config import settings`
- Type hints on all function signatures
- Pydantic v2 for request/response models
- SQLAlchemy 2.0 `mapped_column` style
- Ruff for lint + format (line-length=100, target py314)
- Pyrefly for type-checking (`just typecheck` — replaces mypy)
- Package manager: `uv sync` (NOT pip)
- Logging: `from app.core.logging import get_logger`

## TypeScript

- Strict mode — no `any` unless justified with a comment
- Functional components only (no class components)
- Zustand for global state (no Redux, no Context API for global state)
- All API calls through the typed axios client in `src/lib/api.ts`
- Tailwind utility classes; CSS variables for dark Solar Terminal theme
- Tailwind v4: workspace packages must be listed in `globals.css` with `@source` so arbitrary-value classes (e.g. `grid-cols-[28px_1fr_auto_auto]`) used inside `packages/*/src` actually compile. Tailwind v4's Preflight no longer sets `cursor: pointer` on `button` — `globals.css` re-applies it; don't add `cursor-pointer` per-button
- `@alphaforge/solar-orb-ui` — import components, fonts, and theme tokens from here
- Biome v2 for formatting + linting; ESLint v9 flat config for Next.js rules
- TanStack React Query v5 for data fetching (hooks in per-domain `*.query.ts`)
- Package manager: pnpm (NOT npm or yarn)
- Logging: `import { getLogger } from "@/lib/logger"`

## New File Checklist

| Adding… | Rule |
|---------|------|
| Backend route file | `{domain}_routes.py` — register in `app/modules/__init__.py` |
| Backend service | `{domain}_service.py` — business logic lives here, never in routes |
| Backend utils | `{domain}_utils.py` — max 50 lines |
| New broker | Implement `BrokerSource` ABC from `base.py`; register in `registry.py`; CSV dumps → use `dump_utils.py` ([broker-csv-dumps.md](broker-csv-dumps.md)). CSV parsers must use `AssetClass.MUTUAL_FUND` (not `AssetClass.MF`). |
| New UI component | Add to `packages/solar-orb-ui/src/components/`, export from `src/index.ts`, rebuild with `pnpm build` |
| Frontend module file | `{domain}.{api\|query\|types\|utils}.ts` under `src/modules/{domain}/` |
| Design tokens | Source of truth is `packages/solar-orb-ui/src/tokens/` (JSON + TS). Keep `theme.css` in sync |

## Portfolio Display Conventions

- `pnl_pct` from the API is **overall unrealized %**, not a day-return. Never label it "today".
- `CountUp` with `format="inr"` passes the raw value through `formatNumber`, which preserves the sign. Always pass `Math.abs(value)` to `CountUp` when you are supplying a signed prefix (`"+₹"` / `"−₹"`).
- Use `▲` / `▼` conditionally on sign; never hardcode one direction.
- **Bonds & gold**: prefer `name` over `symbol` for the primary label (treemap cell, ledger row). Their symbols are usually ISINs/scripCodes that aren't human-recognizable. In the ledger, the full name is shown un-truncated (wraps within the symbol column) with the cryptic `symbol` code below it. For equity/MF, keep `symbol` primary with `name` underneath in smaller font.

## Testing

- Backend: `cd backend && uv run pytest -v`
- Frontend: `cd frontend && pnpm lint && pnpm type-check`
