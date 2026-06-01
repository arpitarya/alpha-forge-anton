# AlphaForge Anton — Coding Conventions

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
- `@alphaforge-anton/ravel-ui` — import components, fonts, and theme tokens from here
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
| New UI component | Add to `packages/ravel-ui/src/components/`, export from `src/index.ts`, rebuild with `pnpm build` |
| Frontend module file | `{domain}.{api\|query\|types\|utils}.ts` under `src/modules/{domain}/` |
| Design tokens | Source of truth is `packages/ravel-ui/src/tokens/` (JSON + TS). Keep `theme.css` in sync |

## Portfolio Display Conventions

- `pnl_pct` from the API is **overall unrealized %**, not a day-return. Never label it "today".
- `CountUp` with `format="inr"` passes the raw value through `formatNumber`, which preserves the sign. Always pass `Math.abs(value)` to `CountUp` when you are supplying a signed prefix (`"+₹"` / `"−₹"`).
- Use `▲` / `▼` conditionally on sign; never hardcode one direction.
- **Bonds & gold**: prefer `name` over `symbol` for the primary label (treemap cell, ledger row). Their symbols are usually ISINs/scripCodes that aren't human-recognizable. In the ledger, the full name is shown un-truncated (wraps within the symbol column) with the cryptic `symbol` code below it. For equity/MF, keep `symbol` primary with `name` underneath in smaller font.

## Error Handling & Notifications

Every module must surface failures to the user via the notification system. Silently swallowing errors is not allowed.

### Frontend — the three-layer stack

```
ApiError (apiError.ts)          ← normalized error shape
    ↓
notifyApiError (apiNotify.ts)   ← ApiError → notify.error() toast
    ↓
notify (solar-ui)               ← imperative push: ok/error/warn/info/sync/upsert/dismiss
```

#### ApiError

All HTTP errors normalize to `ApiError` (`src/lib/apiError.ts`). Never inspect raw axios errors — always call `toApiError(err)` first.

```ts
// Kinds: "network" | "canceled" | "auth" | "forbidden" | "notFound"
//        | "validation" | "client" | "server" | "unknown"
const apiErr = toApiError(err);
```

The axios client in `api.ts` attaches the normalized error as `error.apiError` so callers can read it without re-parsing.

#### React Query (the default path)

`providers.tsx` wires global error handlers on both caches so modules get notifications for free:

| Usage | Behaviour | Override |
|-------|-----------|----------|
| `useMutation(...)` | Always fires `notifyApiError` on failure | Pass `meta: { silent: true }` to suppress |
| `useQuery(...)` | Silent by default (background refetches are noisy) | Pass `meta: { notifyOnError: true }` to opt in |

```ts
// Mutation — notifies automatically; no extra code needed
useMutation({ mutationFn: syncWallet })

// Mutation — suppress for polling / optimistic updates
useMutation({ mutationFn: ping, meta: { silent: true } })

// Query — opt in to user-visible error toasts
useQuery({ queryKey: [...], queryFn: fetchHoldings, meta: { notifyOnError: true } })
```

#### Manual surfacing (SSE, event handlers, imperative calls)

When you cannot use React Query (SSE streams, click handlers that call `api.*` directly, etc.) call `notifyApiError` yourself:

```ts
import { notifyApiError } from "@/lib/apiNotify";
import { toApiError } from "@/lib/api";

try {
  await api.post("/portfolio/sources/sync-all");
} catch (err) {
  notifyApiError(toApiError(err));
}
```

`notifyApiError` automatically skips `canceled` (unmount/debounce noise) and `auth` (the interceptor already redirects to `/login`).

#### Non-API notifications

Use `notify` from `@alphaforge-anton/solar-ui` directly for operations that aren't HTTP errors:

```ts
import { notify } from "@alphaforge-anton/solar-ui";

// Progress toast (indeterminate spinner, persists until dismissed)
const id = notify.sync({ title: "Syncing holdings…" });
// Replace it with the result when done
notify.upsert({ id, severity: "ok", title: "Holdings refreshed" });

// One-shot toasts
notify.ok({ title: "Saved" });
notify.warn({ title: "Stale data", message: "Last sync was 48 h ago." });
notify.info({ title: "Market closed", message: "Live prices paused." });
```

Available methods: `ok · error · warn · info · sync · custom · upsert · dismiss`

Key `NotificationInput` fields:
- `pill` — short uppercase tag shown next to the title (e.g. `"404"`, `"FAILED"`)
- `ttl` — ms before auto-dismiss; `0` = persistent (default for `error` and `sync`)
- `actions` — array of `{ label, variant, onClick }` buttons rendered in the toast
- `id` — stable key; calling `notify.*({ id })` or `notify.upsert` with the same id replaces the existing toast

### Backend — raise, don't swallow

Routes and services must raise `HTTPException` with a human-readable `detail` string. `toApiError()` on the frontend extracts `detail` verbatim.

```python
from fastapi import HTTPException

# Good — frontend shows "Broker not found"
raise HTTPException(status_code=404, detail="Broker not found")

# Good — 422 validation failures surface field + message automatically via Pydantic
# Bad — catching and returning generic 500s hides root cause
```

Rules:
- **Routes**: never catch exceptions unless you are re-raising as a more specific `HTTPException`. Let FastAPI propagate.
- **Services**: raise `HTTPException` (or a domain-specific subclass) for expected failures; let unexpected exceptions bubble.
- **Boot probes** (`boot_probes.py`) are the deliberate exception — each probe catches all errors so one failed system cannot break `/health/boot` for the others.
- **Rate limits**: already handled globally in `main.py` via `_rate_limit_exceeded_handler`; don't add per-route handling.

### Module checklist

When adding a new module or component:

- [ ] Every `useMutation` either auto-notifies or has `meta: { silent: true }` with a comment explaining why
- [ ] Every `useQuery` that can fail in a user-visible way has `meta: { notifyOnError: true }`
- [ ] Any `api.*` call outside React Query wraps its `catch` with `notifyApiError(toApiError(err))`
- [ ] Long-running operations (sync, refresh, export) show a `notify.sync` spinner and resolve it with `notify.upsert`
- [ ] Backend routes raise `HTTPException` with a `detail` string — never `return {"error": ...}`

## Testing

- Backend: `cd backend && uv run pytest -v`
- Frontend: `cd frontend && pnpm lint && pnpm type-check`
