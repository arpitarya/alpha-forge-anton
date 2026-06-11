# Fux narrative

_13 narrative entries — the long-form prose absorbed into the substrate (plan §11)._

## Contents

- [Why Anton exists](#anton-overview)
- [AlphaForge Anton — Architecture & Key Files](#architecture)
- [Broker CSV Dump Convention](#broker-csv-dumps)
- [Broker Source Integration Guide](#broker-source-integration)
- [AlphaForge Anton — Commands](#commands)
- [Getting Started — Developer Setup](#getting-started)
- [How AlphaForge Anton Works](#how)
- [Live prices — design plan](#live-prices-plan)
- [Plan: Add LLM + Brokerage Sync to Boot Screen](#plan-boot-llm-brokerage)
- [Portfolio plan — template (git-safe instance shape)](#portfolio-plan-template)
- [Secure holdings access for Orff + the plan→drift→advise workflow](#secure-holdings-plan)
- [What AlphaForge Anton Is](#what)
- [Why AlphaForge Anton Exists](#why)

## Why Anton exists
<a id="anton-overview"></a>
_`anton-overview` · product_

## Why Anton exists

**AlphaForge Anton** is a personal, self-hosted AI portfolio-management and
investment terminal for Indian markets. It unifies holdings scattered across many
brokers (Zerodha, Groww, AngelOne, IndMoney, Binance, …) into one currency-correct
view, computes valuation and P&L, and layers AI assistance (the Orff concierge)
on top — without sending a user's financial data to a third-party SaaS.

## Shape

A monorepo: a Python 3.14 / FastAPI backend and a Next.js 15 / TypeScript
frontend, MIT-licensed and self-hosted. The backend's `brokers` module is the
heart — each broker is a `BrokerSource` that fetches holdings into a cache; the
`HoldingsAggregator` rolls them up read-only (see [[portfolio-valuation]],
[[day-pnl]], [[inr-normalization]]). Auth/IAM is owned by a sibling service,
Wagner, with Anton acting as a proxy (see [[project-wagner-dante]]); broker UI and
holdings are verified through `probes/` (CDP), never Playwright MCP.

## Principles that recur

- **Currency-correct first** — every monetary value is INR-normalised at the leaf
  before any aggregation, so USD-priced holdings sit beside INR ones safely.
- **Small files, clear seams** — source files stay ≤100 lines; backend
  `{domain}_{role}.py`, frontend `{domain}.{role}.ts`.
- **Knowledge ships with code** — a code change carries its doc/rule update in the
  same session; this very substrate (`.fux/`) is where that knowledge lives.

> Migrated into Fux from `docs/architecture.md` + the WHAT/WHY/HOW narrative as a
> `type: narrative` entry (plan §11). The source docs remain until parity is
> verified and they are formally decommissioned.

## AlphaForge Anton — Architecture & Key Files
<a id="architecture"></a>
_`architecture` · general_

# AlphaForge Anton — Architecture & Key Files

## Project

**AlphaForge Anton** — Personal AI-powered portfolio management & investment terminal for Indian markets.
Built for personal use — not a SaaS product. Self-hosted, open-source, MIT licensed.

## Repository Structure

```
alpha-forge-anton/
├── backend/          Python 3.14 + FastAPI + SQLAlchemy async
│   ├── app/core/     Config (pydantic-settings), DB engine, JWT/bcrypt, env_loader
│   ├── app/modules/  Feature modules — each owns its routes/service/models
│   │   ├── health/      /api/v1/* health endpoint
│   │   ├── iam/         Wagner IAM proxy — forwards /api/v1/iam/* to Wagner service on :8001
│   │   ├── portfolio/   routes + Holding/Order/Watchlist ORM
│   │   ├── brokers/     pluggable BrokerSource adapters (Zerodha Kite/Coin, Groww, Angel One, IndMoney, TickerTape, Binance) + aggregator + registry. Used by portfolio routes. All CSV portfolio dumps share `dump_utils.py` — see broker-csv-dumps.md
│   │   ├── trade/       routes (paper/live trade endpoints)
│   │   └── dashboard/   routes (cross-module aggregation)
│   ├── app/main.py   FastAPI app factory; mounts api_router from app.modules
│   ├── alembic/      Database migrations
│   └── tests/        Pytest suite
├── packages/
│   ├── logger-py/    Publishable Python logger package (alphaforge-logger)
│   │   └── src/alphaforge_logger/  setup_logging(), get_logger()
│   ├── logger-node/  Publishable Node/TS logger package (@alphaforge/logger)
│   │   └── src/      createLogger(), getLogger() — pino-based
│   └── solar-ui/ Publishable UI component library (@alphaforge-anton/solar-ui)
│       ├── src/components/  Button, Input, Card, Badge, Icon, Text, SearchBox, PrefRow, PrefGroup, PrefControls
│       └── src/styles/      fonts.css, theme.css, base.css (design tokens + base styles)
├── frontend/         Next.js 15 (App Router) + React 19 + TypeScript + Tailwind v4
│   ├── src/app/      Pages and layouts (Solar Terminal theme)
│   ├── src/lib/      Cross-cutting infra: `api.ts` (axios client), `logger.ts`, `providers.tsx`, `store.ts`
│   └── src/modules/  Feature modules — mirrors backend/app/modules layout
│       ├── portfolio/   portfolio.{api,query,types}.ts + components (Ledger, Treemap, SourcesPanel, ...)
│       ├── ai/          ai.{api,query}.ts + AIChat
│       ├── trade/       trade.{api,query}.ts
│       ├── screener/    ScreenerPanel (hardcoded stub — no live API)
│       ├── dashboard/   dashboard.{api,query,types}.ts + terminal-home components
│       └── auth/        auth.api.ts (IAM client), auth.types.ts, useAuthStore.ts, auth.guard.tsx
├── infra/            Infrastructure configs (docker-compose for services, devcontainer)
├── repo-context-mcp/ Tool-agnostic MCP server — gives Claude/Copilot/Cursor/any MCP client semantic + structural context over this repo
│   └── src/alphaforge_anton_repo_context/  server, indexer, chunker, embeddings, watcher, tools/
├── docs/             WHY.md, WHAT.md, HOW.md, GETTING_STARTED.md + canonical shared docs for AI agents
└── design/           Design system & Gemini Stitch tokens
```

## Tech Decisions

| Area | Choice | Notes |
|------|--------|-------|
| Python pkg mgr | uv (workspace) | Single `uv.lock` at repo root; members declared in `[tool.uv.workspace]`. One `.venv/` shared across backend, screener, logger-py |
| Python version | pyenv | Pinned in `.python-version` (3.14.2) |
| Node pkg mgr | pnpm | Lockfile: `pnpm-lock.yaml`; config in `.npmrc` |
| Node version | nvm | Pinned in `.nvmrc` |
| Monorepo | pnpm workspaces | `pnpm-workspace.yaml` at root; `packages/*` + `frontend` |
| UI library | @alphaforge-anton/solar-ui | Publishable package built with tsup (ESM + CJS + DTS) |
| Logging (Python) | alphaforge-logger | Rotating file + console, env-configurable |
| Logging (Node) | @alphaforge/logger | Pino-based, file + console, publishable tsup pkg |
| DB | PostgreSQL 16 | Async via asyncpg + SQLAlchemy |
| Cache | Redis 7 | Quotes cache, pub/sub, Celery broker |
| AI | OpenAI + LangChain | RAG with market data context |
| Repo Context MCP | alphaforge-anton-repo-context-mcp | Local stdio MCP server; pgvector-backed semantic + structural repo context for Claude/Copilot/Cursor/any MCP client |
| Brokers | Abstract BrokerSource interface | Zerodha first, then Groww, Angel One, Upstox |
| Auth (IAM) | Wagner (standalone service on `:8001`) | JWT + rotating refresh tokens + `wgr_` API keys; owner/viewer roles; audit log. Anton proxies `/api/v1/iam/*` → Wagner; validates JWTs locally from claims (no DB round-trip). Data lives in Wagner's SQLite (`wagner/backend/wagner.db`). |
| Security | Dante (`alphaforge-dante`) | Log redaction (`redactor`), IP allowlist middleware (`warden`), path guard (`curator`), failed-login tracking (`watchman`), zero-trust egress (`gateway`), posture step-up (`posture`), honeypot (`inferno`). Run `just dante-audit` for SAST+CVE+license |
| Local infra | brew services (Postgres, Redis) | Containers optional via OrbStack |
| CI infra | devcontainer.json | GitHub Codespaces compatible |

## Key Files

### Backend
- `backend/app/main.py` — FastAPI app factory; mounts Dante `warden` middleware after CORS
- `backend/app/core/config.py` — All environment variables; `wagner_url` points to the Wagner IAM service
- `backend/app/core/security.py` — JWT decode only (`decode_access_token → dict | None`); no bcrypt (hashing lives in Wagner)
- `backend/app/core/logging.py` — Backend logging setup (wraps alphaforge-logger + Dante `redactor` scrubs every log record)
- `backend/app/core/deps.py` — `get_current_user` stateless JWT validation → `UserClaims(id, role, email)`; `require_owner`; optional Dante posture step-up
- `backend/app/modules/__init__.py` — registers every feature router under `/api/v1/*`
- `backend/app/modules/iam/iam_proxy.py` — thin httpx reverse proxy; forwards all `/api/v1/iam/*` to Wagner `:8001/iam/*`
- `frontend/src/modules/auth/auth.api.ts` — IAM client: fetches `GET /iam/login-key` once (cached), verifies the RSA-PSS mode signature, then sends `{encrypted_payload}` in prod or plain `{email, password}` in dev. Includes session management (`listSessions`, `extendSession`, `revokeSession`) and `logoutAll`.
- `frontend/src/modules/auth/auth.query.ts` — React Query hooks: `useSessions`, `useExtendSession`, `useRevokeSession`
- `frontend/src/modules/auth/auth.types.ts` — TypeScript mirrors of IAM schemas: `LoginKeyResponse`, `SessionResponse`, user/token types
- `frontend/src/modules/auth/useAuthStore.ts` — Zustand store; `logout()` revokes the current session then clears local state; `silentRefresh()` serializes concurrent 401 retries; persisted under `af-auth`
- `frontend/src/modules/preferences/SessionsGroup.tsx` — Sessions panel in Account preferences: lists active sessions with extend/revoke per row; "Sign out this device" triggers `logout()` + redirect
- `frontend/src/modules/preferences/PrivacySection.tsx` — "Sign out everywhere" calls `logoutAll()` + `clearAuth()` + redirect to `/login`
- `backend/app/modules/chat/` — Alpha chat module: `chat_routes.py` (`POST /api/v1/chat/` → SSE), `chat_service.py` (gateway dispatch + streaming), `chat_schemas.py` (request schema + model→QueryType mapping)
- `backend/app/modules/brokers/base.py` — `BrokerSource` ABC; implement for new brokers
- `backend/app/modules/brokers/registry.py` — broker source registry (slug → class)
- `backend/app/modules/brokers/dump_utils.py` — shared CSV-dump utilities (path, permissions, headers, P&L). See [broker-csv-dumps.md](broker-csv-dumps.md)
### Frontend
- `frontend/src/app/layout.tsx` — Root layout. Mounts `ThemeProvider` → `QueryProvider` → `AuthGuard` → `BootGate` → `ChatProvider`, so the boot sequence and the global AlphaBar + ChatRail run once for the whole app across all routes
- `frontend/src/app/page.tsx` — Terminal landing page (no longer wraps `BootGate` — that's now in the root layout)
- `frontend/src/app/portfolio/page.tsx` — Portfolio page. Slim `PortfolioCompactBar` on top (TOTAL · INVESTED · P&L · DAY inline + wallet pills + a "More/Less" expand toggle) so tree / ledger get the dominant vertical space; expanded state reveals the full `WalletStrip`. Source spotlight + filter bar + summary + body (treemap or ledger) on the left, rebalance rail on the right. Filter state (query, sector chip, gainers/losers, sort key + dir, view, expand) is owned here
- `frontend/src/modules/portfolio/PortfolioCompactBar.tsx` — Hi-Fi `.pf-summary-bar`: always-visible row with totals + wallet pills + expand caret. Mirrors the design's "Less / More" pattern so a single click reveals stat cards beneath
- `frontend/src/modules/portfolio/WalletStrip.tsx` + `WalletCard.tsx` — Per-broker wallet cards with brand-colored chip, free cash, holdings value, position count, weighted day move. Shown when the CompactBar is expanded; clicking filters the page to that source. Strip has three action buttons: **⟳ Refresh cash** (`POST /portfolio/wallets/sync`), **⟳ Refresh holdings** (`POST /portfolio/sources/sync-all`), **⟳ Refresh** (hard refresh: busts all CSV caches then re-syncs sources + wallets via `POST /portfolio/refresh`)
- `frontend/src/modules/portfolio/SourceSpotlight.tsx` — Detail banner shown when a specific wallet is active (positions / holdings / P&L / cash). The `⟳ Refresh` button syncs both cash (`POST /portfolio/wallets/{slug}/sync`) and holdings (`POST /portfolio/sources/{slug}/sync`) in parallel, then invalidates wallets + holdings + treemap queries
- `frontend/src/modules/portfolio/FilterBar.tsx` (composes `SearchBox`, `SectorChips`, `PnLToggle`, `SortMenu`, `SegmentedControl` for the Tree/Ledger toggle) — Sector counts re-compute under search+pnl so the chips only show what's reachable; `/` and `⌘F` focus the search box
- `frontend/src/modules/portfolio/portfolio.filter.ts` — `FilterState`, `applyFilter`, `sectorCounts` helpers (pure functions, no React)
- `frontend/src/modules/portfolio/treemap.utils.ts` — Squarified-treemap layout in TS (mirrors `backend/app/modules/brokers/treemap_helper.py`); `Treemap.tsx` consumes filtered holdings + computes layout client-side so reflows are instant when filters change
- `frontend/src/app/preferences/page.tsx` — Preferences page. 8-section sidebar (Appearance · Display · Markets · Alpha AI · Notifications · Account · Privacy · About); reached via gear icon in the top-right
- `frontend/src/modules/preferences/` — Sidebar, section panels, and shared primitives:
  - `PrefRow` / `PrefGroup` / `PrefControls` (`PrefSeg`, `PrefTog`, `PrefSlider`, `PrefSelect`, `PrefInput`) — imported from `@alphaforge-anton/solar-ui`; no longer local files
  - `usePrefStore.ts` — Local-state hook for non-wired draft preferences. Persists to `localStorage["af-prefs-draft-v1"]`, mirrors `chromeMode`/`showVoice` to `body.chrome-autohide` / `body.no-voice` classes
  - `AppearanceSection.tsx` — Theme tiles + accent swatches (wired to `useTheme()`)
  - `DisplaySection.tsx` — Chrome behavior (always-visible vs auto-hide), voice bar toggle, orb size/speed/HUD, ticker speed, reduce motion, number jitter
  - `MarketsSection.tsx` — Primary exchange, number format, currency, after-hours, refresh cadence
  - `AlphaSection.tsx` — Voice wake, reply style, confidence floor, auto-rebalance, screener visibility
  - `NotifSection.tsx` — Price/risk/signal toggles, threshold slider, email digest cadence + address
  - `AccountSection.tsx` — Profile (avatar, name, status), connected brokers list, hotkey reference
  - `PrivacySection.tsx` — Telemetry / crash / training toggles, retention select, danger actions
  - `AboutSection.tsx` — Build / backend / license info, reset action
- `frontend/src/app/globals.css` — Theme variables (Solar Terminal design tokens); `@source` directives extend Tailwind v4 content scanning into `packages/solar-ui/src` so arbitrary classes in solar-ui resolve; restores the default `cursor: pointer` on `button` / `[role="button"]` that Tailwind v4's Preflight dropped
- `frontend/next.config.mjs` — Next.js config: CSP headers (allows `fonts.googleapis.com` + `fonts.gstatic.com` for Material Symbols icons), API rewrites
- `frontend/src/modules/dashboard/TerminalTopBar.tsx` — Slim global top bar per Hi-Fi spec (≈32px min-height, 4px×14px padding, 8px radius). SVG logo mark + ALPHA/FORGE wordmark; Terminal + Portfolio nav buttons; gear icon-button on the right routes to `/preferences`; no icon sidebar
- `frontend/src/modules/chat/` — Alpha chat module: `AlphaBar.tsx` (global bottom bar — Voice/Chat segmented toggle + model picker + Deploy), `ChatRail.tsx` (fixed right-side slide-over conversation thread; `ResponseBody` renders **markdown as safe React nodes** — bold/italic/inline-code/fenced-code/h2-h3/ul/ol/hr — no `dangerouslySetInnerHTML`), `ModelPicker.tsx` (model dropdown: Auto / Forge Pro / Forge Fast / Forge Local), `useChatStream.ts` (SSE fetch hook, multi-turn history up to 6 turns, streaming; forwards JWT from `localStorage["af_token"]` in the `Authorization` header), `ChatContext.tsx` (React context provider rendering AlphaBar + ChatRail globally), `chat.types.ts` (ModelId, ChatTurn, MODELS, `resolveAutoModel`). Mounted in `layout.tsx` as `<ChatProvider>` so it appears on every screen. **Security:** backend endpoint is JWT-gated (`Depends(get_current_user)`); frontend proxy (`/api/v1/chat` → `route.ts`) keeps provider API keys server-side only.
- `frontend/src/modules/dashboard/TerminalVoice.tsx` — Legacy static voice dock (no longer rendered — replaced by `AlphaBar` from the chat module)
- `packages/solar-ui/src/components/TopBar.tsx` / `VoiceDock.tsx` — Reusable chrome containers carrying `data-af-top` / `data-af-voice` plus `.af-top` / `.af-voice` classes. Paired with `body.chrome-autohide` / `body.no-voice` rules in `frontend/src/app/globals.css` to enable Preferences → Display → Chrome behavior (collapses bars to an accent strip; hover/focus expands) and the voice-bar disable toggle
- `frontend/src/modules/dashboard/BootScreen.tsx` — Full-screen animated boot checklist. Renders one row per real backend system (gateway, Postgres, every broker source); each row's glyph and detail are driven by the `status: BootStatus` field (`ok` ✓ green / `warn` ! amber / `error` ✗ red). `BOOT_STEPS` is the static fallback used only when the live probe fails
- `frontend/src/modules/dashboard/boot.api.ts` + `boot.types.ts` — Frontend client and TS mirror of `BootReport` / `BootService` from the backend
- `frontend/src/modules/dashboard/BootGate.tsx` — Sits inside `AuthGuard` in the root layout. On first paint of a tab it hits `GET /api/v1/health/boot`, maps each service to a `BootStep`, then plays the boot screen exactly once per browser tab (gated by `sessionStorage['af-booted']`). Skips entirely on `/login` and survives navigations between Terminal / Portfolio / Preferences. If the probe call fails the static `BOOT_STEPS` fallback still produces a usable splash
- `backend/app/modules/health/health_routes.py` — `GET /health` (basic ping) + `GET /health/boot` (per-system readiness snapshot consumed by the terminal boot splash; aggregates database SELECT 1 + every broker source's `.status` from `SOURCES`)
- `backend/app/modules/health/boot_probes.py` — One probe function per system (`probe_backend`, `probe_database`, `probe_brokers`). Each probe swallows its own errors so a single failure can't take down the whole `/health/boot` response
- `backend/app/modules/health/boot_schemas.py` — `BootStatus` enum (`ok` / `warn` / `error` / `skip`), `BootService`, and `BootReport` Pydantic v2 schemas; the frontend mirror is `boot.types.ts`
- `frontend/src/modules/dashboard/TerminalRail.tsx` — Icon sidebar (unused; nav lives in the top bar per Hi-Fi design)
- `frontend/src/lib/api.ts` — Axios HTTP client (interceptors only; per-domain `*.api.ts` lives in each module). The response interceptor handles 401 → silent refresh → redirect and attaches a normalized `ApiError` as `error.apiError` on every failed request.
- `frontend/src/lib/apiError.ts` — `ApiError` type + `toApiError()` normalizer. All HTTP errors collapse to a typed shape with `kind` (`network/canceled/auth/forbidden/notFound/validation/client/server/unknown`), `status`, `message`, and optional `detail`/`requestId`.
- `frontend/src/lib/apiNotify.ts` — `notifyApiError(err)`: bridges an `ApiError` to a `notify.error()` toast. Skips `canceled` (unmount noise) and `auth` (interceptor already handles redirect).
- `frontend/src/lib/providers.tsx` — React Query `QueryProvider`. Global error handlers: mutations always call `notifyApiError` (suppress with `meta: { silent: true }`); queries are silent unless `meta: { notifyOnError: true }`. See [conventions.md § Error Handling](conventions.md#error-handling--notifications).
- `frontend/src/lib/logger.ts` — Frontend logging setup (wraps @alphaforge/logger)
- `frontend/src/modules/<name>/<name>.api.ts` — Per-domain axios calls
- `frontend/src/modules/<name>/<name>.query.ts` — Per-domain React Query hooks

### Packages & Infra
- `packages/logger-py/src/alphaforge_logger/logger.py` — Python logger package core
- `packages/logger-node/src/logger.ts` — Node/TS logger package core
- `packages/solar-ui/src/index.ts` — UI library barrel export (Button, Input, Card, Badge, Icon, Text, SearchBox, PrefRow, PrefGroup, PrefControls, …)
- `packages/solar-ui/src/styles/theme.css` — Tailwind v4 design tokens (CSS)
- `packages/solar-ui/src/tokens/index.ts` — Design tokens (TypeScript)
- `packages/solar-ui/src/tokens/tokens.json` — Design tokens (JSON, machine-readable)
- `packages/solar-ui/tsup.config.ts` — Package build config
- `repo-context-mcp/src/alphaforge_anton_repo_context/server.py` — MCP server entry (stdio); exposes `search_code`, `get_symbol`, `module_overview`, `recent_changes`, `read_file_range`
- `repo-context-mcp/src/alphaforge_anton_repo_context/indexer.py` — Walk → chunk → embed → pgvector
- `repo-context-mcp/src/alphaforge_anton_repo_context/chunker.py` — AST (Python), regex (TS/TSX), section (Markdown), sliding-window fallback
- `repo-context-mcp/src/alphaforge_anton_repo_context/db.py` — `repo_chunks` ORM model + `init_schema()`
- `repo-context-mcp/README.md` — Wire-up snippets for Claude Code, VS Code/Copilot, Cursor, Cline, Zed, Windsurf

### Probes & Design
- `probes/ui_probe.py` — End-to-end UI smoke test via CDP (port 9299). Attaches to existing Chrome session; exercises auth, dashboard, portfolio, and console-error checks. Writes PNGs to `/tmp/alphaforge-anton-probe/`
- `probes/ui_screens.py` — Lightweight screenshot helper. Auths via `POST /api/v1/auth/token`, stashes the JWT in localStorage, then snapshots `/`, `/portfolio`, `/preferences` at 1440×900
- `probes/ui_pref_tabs.py` — Walks every Preferences sidebar tab and captures `preferences-<tab>.png` for design review
- `screenshots/` — Probe output. Tracked dir; PNGs are overwritten on each run
- `design/` — Bundle from Claude Design (`design/README.md`, `design/chats/` transcripts, `design/project/Alpha Forge Hi-Fi.html` + companion JSX prototypes). Source of truth for visual / interaction specs

### Config & Workspace
- `.python-version` — Python version for pyenv (3.14.2)
- `.nvmrc` — Node.js version for nvm
- `.npmrc` — pnpm/npm configuration (exact versions, engine-strict)
- `pyproject.toml` (repo root) — uv workspace definition + `[tool.uv.sources]` for local deps
- `uv.lock` (repo root) — single lockfile for all Python workspace members
- `pnpm-workspace.yaml` — Workspace root definition
- `.env.port` — All service ports in one file (single source of truth for BACKEND_PORT, FRONTEND_PORT, POSTGRES_PORT, REDIS_PORT)
- `.env` — App config defaults + LLM key stubs (tracked; no secrets)
- `.env.cred.example` — Credentials template (AFBACH, BROKER_CACHE_KEY, JWT, POSTGRES_PASSWORD)
- `.env.frontend.example` — Frontend env template (NEXT_PUBLIC_API_URL, ports, logging)
- `.env.cred.local` / `.env.frontend.local` — Real secrets/overrides (gitignored; created by `./setup-config.sh`)
- `frontend/.env.local` — Symlink → `../.env.frontend.local`; Next.js auto-loads it from its project root
- `.vscode/mcp.json` — VS Code MCP server config

## Broker CSV Dump Convention
<a id="broker-csv-dumps"></a>
_`broker-csv-dumps` · general_

# Broker CSV Dump Convention

All broker holdings dumps share a single implementation in
`backend/app/modules/brokers/dump_utils.py`. No broker-specific `*_dump.py`
file may duplicate path resolution, permission-setting, or P&L calculation.

## Output directory

| Priority | Source | Value |
|----------|--------|-------|
| 1 | `$PORTFOLIO_DUMP_DIR` env var | Absolute path, or repo-relative path resolved from repo root |
| 2 | Default | `~/.alphaforge-anton/portfolio-dumps/` |

Directory is created automatically with `chmod 700`. Each CSV file is written
with `chmod 600`.

## File naming

| File | Pattern | Purpose |
|------|---------|---------|
| Live (TTL-cached) | `{slug}-holdings-live.csv` | Re-used until TTL expires |
| Dated snapshot | `{slug}-holdings-{YYYY-MM-DD}.csv` | One per day, UTC date |

## CSV format

**Header comment (line 1)**

```
# source=<slug>  dumped_at_utc=<ISO-8601>  holdings_count=<n>
```

**Column headers (line 2) — `dump_utils.CSV_HEADERS`**

```
tradingsymbol, name, isin, exchange, quantity, average_price, last_price,
invested, current_value, pnl, pnl_pct, asset_class
```

`invested`, `current_value`, `pnl`, and `pnl_pct` are computed by
`dump_utils._row_values()` from `quantity`, `average_price`, and
`last_price`. Never recompute them in broker-specific code.

`name` and `asset_class` are optional — older dumps written before these
columns existed still validate. `asset_class` must be set when a broker source
returns mixed asset types (e.g. `zerodha_kite` writes `"equity"` only;
`zerodha_coin` writes `"etf"` or `"mutual_fund"`). When reading back a CSV row
that lacks `asset_class`, source code falls back to instrument-type lookup or
the source default. Valid values match `AssetClass` enum values: `equity`,
`mutual_fund`, `etf`, `bond`, `gold`, `crypto`, `cash`, `other`.

`name` (company / instrument display name): populate it in the broker normalizer
when the source returns it (Groww V2 → `symbolData.companyShortName`).
Zerodha's Kite holdings JSON does not include it;
`zerodha_kite_instruments.py` fetches the public Kite instruments dump
(`https://api.kite.trade/instruments`, ~3 MB, 24h TTL, cached to
`{dump_dir}/zerodha-instruments.csv`) and provides a `tradingsymbol → name`
lookup. TTL is overridable via `ZERODHA_INSTRUMENTS_TTL_SECONDS`.

## API

```python
from app.modules.brokers.dump_utils import (
    dump_dir,           # () -> Path  — resolves env var or default
    live_csv_path,      # (slug) -> Path
    dated_csv_path,     # (slug) -> Path
    is_csv_fresh,       # (slug, ttl_seconds) -> bool
    read_csv,           # (slug) -> list[dict[str, str]]
    write_csv,          # (rows, dst, *, source) -> None
    clear_csv_cache,    # (slug) -> bool — deletes live CSV, returns True if it existed
    CSV_HEADERS,        # canonical column tuple
)
```

`clear_csv_cache(slug)` is used by `POST /portfolio/refresh` to force a full
re-fetch from the broker API, bypassing the TTL. Broker sources check
`is_csv_fresh()` on every `fetch()` call — deleting the live file makes the
next sync skip the CSV path entirely.

## Adding a new broker

1. Create `backend/app/modules/brokers/{slug}/{slug}_dump.py`.
2. Import helpers from `dump_utils` — do not rewrite them.
3. Call `write_csv(rows, live_csv_path(slug), source=slug)` and
   `write_csv(rows, dated_csv_path(slug), source=slug)`.
4. Use `is_csv_fresh(slug, ttl)` to skip redundant API calls.

## Broker Source Integration Guide
<a id="broker-source-integration"></a>
_`broker-source-integration` · general_

# Broker Source Integration Guide

How AlphaForge Anton fetches, caches, and exposes holdings from a broker. Read this before adding a new source.

---

## Architecture at a glance

```
registry.py          ← process-wide {slug → BrokerSource} map
    └── BrokerSource (base.py)   ← ABC; two entry-points: fetch() + parse()
            ├── {slug}_source.py         ← the public adapter (implements BrokerSource)
            ├── {slug}_source_helper.py  ← auth + HTTP/CDP calls (pure async)
            ├── {slug}_dump.py           ← thin TTL-cache wrapper around dump_utils
            └── {slug}_csv.py            ← CSV-upload fallback parser
```

Sibling: `backend/notebooks/{slug}_dev.ipynb` — REPL-style end-to-end exercise of every `/portfolio/*` endpoint scoped to the source. Required for every new broker (see step 4 of "Register the new source" below).

`dump_utils.py` is shared across every broker — path resolution, file permissions, CSV headers, and P&L computation all live there.

---

## Two source kinds

| Kind | `SourceKind` | Entry-point | When to use |
|------|-------------|-------------|-------------|
| API | `SourceKind.API` | `fetch()` | Broker has an endpoint you can call (with auth) |
| CSV | `SourceKind.CSV` | `parse()` | Broker only exports a downloadable CSV |

API sources also implement `parse()` as a manual CSV fallback — the `/sources/{slug}/upload` endpoint calls it.

---

## Data flow — API source (Zerodha / Groww pattern)

```
GET /api/v1/brokers/{slug}/sync
        │
        ▼
BrokerSource.sync()          (base.py — sets status SYNCING → READY / ERROR)
        │
        ▼
{slug}_source.fetch()        (checks CSV TTL first, then calls helper)
        │
        ├─ CSV cache hit → read_csv() → list[Holding]
        │
        └─ cache miss
                │
                ▼
        {slug}_source_helper  (auth: CDP enctoken / browser fetch)
                │
                ▼
        broker API / JS eval  (raw list[dict])
                │
                ▼
        write_csv() via dump_utils  (writes live + dated files)
                │
                ▼
        _holding_from_row()   → list[Holding]
```

---

## File checklist for a new broker

Create these files under `backend/app/modules/brokers/{slug}/`:

| File | Purpose | Line budget | Required? |
|------|---------|------------|-----------|
| `__init__.py` | barrel export of public classes | ≤ 10 | yes |
| `{slug}_source_helper.py` | REQUIRED_ENV, auth, raw data fetch | ≤ 100 | yes |
| `{slug}_dump.py` | TTL wrappers + standalone CLI | ≤ 70 | yes |
| `{slug}_source.py` | `BrokerSource` subclass | ≤ 100 | yes |
| `{slug}_csv.py` | CSV-upload parser (may delegate to `_GrowwCSV` pattern) | ≤ 60 | yes |
| `{slug}_cash_helper.py` | CDP/HTTP capture of free-cash XHR | ≤ 100 | only if `supports_cash = True` |
| `{slug}_routes.py` | broker-specific extra endpoints | ≤ 50 | optional |

Plus these outside the module dir:

| File | Purpose | Required? |
|------|---------|-----------|
| `backend/notebooks/{slug}_dev.ipynb` | End-to-end REPL — see step 4 below | yes |
| `backend/tests/fixtures/broker_csvs/{slug}_holdings.csv` | 3-5 representative rows | yes |
| `probes/{slug}_probe.py` | XHR probe for holdings | API kinds only |
| `probes/{slug}_cash_probe.py` | XHR/HTTP probe for free cash | only if `supports_cash = True` |

Then register in `registry.py` (one line), store user IDs / API keys in the afbach vault (see Step 2 below), and add URL/needle constants to `broker_urls.py` (cash brokers also add `{SLUG}_BALANCE_PAGE`, `{SLUG}_BALANCE_URL_NEEDLES`).

---

## `{slug}_source_helper.py` — what it must export

```python
from app.modules.brokers.broker_env import require_env

REQUIRED_ENV: tuple[str, ...] = ("MYBROKER_USER_ID",)

def env(key: str) -> str:
    return os.getenv(key, "").strip()

# Acquire auth credential (enctoken, access_token, session cookie, …)
# require_env() raises with a vault hint if the key is missing or vault is locked.
async def acquire_token(force: bool = False) -> str:
    require_env("MYBROKER_USER_ID", env)
    ...

# Call broker API; returns raw list[dict] with at least:
#   tradingsymbol, isin, exchange, quantity, average_price, last_price
async def fetch_holdings_json(token: str) -> list[dict[str, Any]]: ...
```

`REQUIRED_ENV` drives the `SourceStatus.READY` check in `__init__` via `source_ready()` — if any env var is missing (or the vault is locked) the source stays `UNCONFIGURED` and the UI surfaces that clearly. `require_env()` in the acquire/fetch functions gives a vault-aware error at runtime instead of a silent 180-second CDP timeout.

---

## `{slug}_dump.py` — thin TTL wrapper (copy this template)

```python
"""MyBroker holdings CSV cache.

TTL controlled by MYBROKER_REFETCH_SECONDS (root .env). Default 1h.

Run standalone:
    python -m app.modules.brokers.mybroker.mybroker_dump
    python -m app.modules.brokers.mybroker.mybroker_dump --force-login
"""
from __future__ import annotations

import asyncio, os, sys
from pathlib import Path
from typing import Any

import app.modules.brokers.dump_utils as _du
from app.core.logging import get_logger
from app.modules.brokers.mybroker.mybroker_source_helper import acquire_token, fetch_holdings_json

logger = get_logger("brokers.mybroker_dump")
SLUG = "mybroker"

def _ttl() -> int:
    return int(os.getenv("MYBROKER_REFETCH_SECONDS", "3600"))

def live_csv_path() -> Path:         return _du.live_csv_path(SLUG)
def is_csv_fresh() -> bool:          return _du.is_csv_fresh(SLUG, _ttl())
def read_csv() -> list[dict]:        return _du.read_csv(SLUG)
def write_csv(rows, dst: Path):      _du.write_csv(rows, dst, source=SLUG)


async def dump_mybroker(*, force_login: bool = False) -> Path:
    token = await acquire_token(force=force_login)
    rows = await fetch_holdings_json(token)
    live = live_csv_path()
    write_csv(rows, live)
    write_csv(rows, _du.dated_csv_path(SLUG))
    logger.info("MyBroker: dumped %d holdings → %s", len(rows), live)
    return live


def main() -> int:
    force = "--force-login" in sys.argv
    try:
        path = asyncio.run(dump_mybroker(force_login=force))
    except Exception as e:
        logger.error("MyBroker dump failed: %s", e)
        return 1
    print(path)
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

---

## `{slug}_source.py` — the BrokerSource subclass (copy this template)

```python
from __future__ import annotations
from typing import IO

import httpx
from app.core.logging import get_logger
from app.modules.brokers._http import clear_session
from app.modules.brokers.base import AssetClass, BrokerSource, Holding, SourceKind, SourceStatus
from app.modules.brokers.mybroker.mybroker_csv import MyBrokerCSVSource as _CSV
from app.modules.brokers.mybroker.mybroker_dump import is_csv_fresh, live_csv_path, read_csv, write_csv
from app.modules.brokers.broker_env import source_ready
from app.modules.brokers.mybroker.mybroker_source_helper import REQUIRED_ENV, acquire_token, env, fetch_holdings_json

logger = get_logger("brokers.mybroker")
__all__ = ["MyBrokerSource", "REQUIRED_ENV", "env"]


def _holding_from_row(r: dict, slug: str) -> Holding:
    qty   = float(r.get("quantity")      or 0)
    avg   = float(r.get("average_price") or 0)
    ltp   = float(r.get("last_price")    or 0)
    inv   = qty * avg
    cur   = qty * ltp
    pnl   = cur - inv
    return Holding(
        source=slug, asset_class=AssetClass.EQUITY,
        symbol=str(r.get("tradingsymbol") or "").upper(),
        isin=r.get("isin") or None,
        quantity=qty, avg_price=avg, last_price=ltp,
        invested=inv, current_value=cur, pnl=pnl,
        pnl_pct=(pnl / inv * 100) if inv else 0.0,
        exchange=r.get("exchange") or "NSE",
    )


def _holding_from_csv(r: dict[str, str], slug: str) -> Holding:
    g = r.get
    return Holding(
        source=slug, asset_class=AssetClass.EQUITY,
        symbol=str(g("tradingsymbol") or "").upper(), isin=g("isin") or None,
        quantity=float(g("quantity") or 0), avg_price=float(g("average_price") or 0),
        last_price=float(g("last_price") or 0), invested=float(g("invested") or 0),
        current_value=float(g("current_value") or 0), pnl=float(g("pnl") or 0),
        pnl_pct=float(g("pnl_pct") or 0), exchange=g("exchange") or None,
    )


class MyBrokerSource(BrokerSource):
    slug  = "mybroker"
    label = "My Broker"
    kind  = SourceKind.API
    notes = (
        "Manual login: log in to mybroker.com inside the AlphaForge Anton Chrome "
        "(started with --remote-debugging-port=9299). "
        "Store MYBROKER_USER_ID in the afbach vault: "
        "PUT /v1/secrets {\"key\": \"MYBROKER_USER_ID\", \"value\": \"<your-id>\"}."
    )

    def __init__(self) -> None:
        super().__init__()
        if source_ready(REQUIRED_ENV, env):
            self._status = SourceStatus.READY

    def parse(self, stream: IO[bytes], filename: str | None = None) -> list[Holding]:
        holdings = _CSV().parse(stream, filename)
        return [h.model_copy(update={"source": self.slug}) for h in holdings]

    async def fetch(self) -> list[Holding]:
        if is_csv_fresh():
            rows = read_csv()
            logger.info("MyBroker: %d holdings from CSV cache", len(rows))
            return [_holding_from_csv(r, self.slug) for r in rows]
        try:
            token = await acquire_token()
            rows  = await fetch_holdings_json(token)
        except httpx.HTTPStatusError as e:
            status = e.response.status_code if e.response is not None else None
            if status in (401, 403):
                logger.warning("MyBroker: auth rejected (%s) — forcing re-login", status)
                clear_session("mybroker")
                token = await acquire_token(force=True)
                rows  = await fetch_holdings_json(token)
            else:
                raise
        write_csv(rows, live_csv_path())
        out = [_holding_from_row(r, self.slug) for r in rows]
        logger.info("MyBroker: fetched %d holdings → cached to CSV", len(out))
        return out
```

---

## Wallet cash (free balance in the broker)

A source can optionally expose its free-cash figure to power the Portfolio
wallet strip. To opt in:

1. Set the class attribute `supports_cash = True`.
2. Set `self.refetch_seconds = int(os.getenv("{SLUG}_REFETCH_SECONDS", "3600"))` in `__init__` — TTL for the on-disk cache.
3. Override `async def fetch_cash(self) -> WalletBalance` — return a `WalletBalance(source=self.slug, cash=…, currency="INR", as_of=now, available=True)`.
4. The base class wraps it in `sync_cash()` which goes through `cash_dump.cached_sync_cash` — that consults the per-broker CSV cache (TTL-gated) before hitting the network, and persists fresh results to `<dump_dir>/broker-cash-live.csv`.

Patterns in use:

| Source | Balance page | XHR needle | Field path |
|--------|--------------|------------|-----------|
| Zerodha (INR) | n/a (direct HTTP) | `GET /oms/user/margins` (enctoken) | `data.equity.available.cash` |
| Angel One (INR) | `angelone.in/trade/funds` | `/funds/v2/getRMSLimit` (CDP) | `data.netAvailableFunds` |
| Groww (INR) | `groww.in/user/balance/inr` | `/margin/user_margin_details` (CDP) | `CASH.value` (string → float) |
| IndMoney (USD) | `indmoney.com/investments/us-stocks/my-us-stocks` | `/us-stock-broker/us/portfolio/equity/summary` (CDP, same as holdings) | `user_wallet_balance.available_balance` |
| Binance (USD/USDT) | `binance.com/en/my/wallet/account/main` | `/bapi/asset/v2/private/asset-service/wallet/balance` (CDP) | sum of `data[].free` where `asset ∈ {USDT,USDC,BUSD,FDUSD}` |
| Ticker Tape | not supported (`supports_cash = False`; wallet card shows "Cash N/A") | | |

Non-INR brokers: set `currency = "USD"` (or other) as a class attribute on the `BrokerSource` subclass. The shared `_build_one` reads it so `WalletInfo.currency` is correct even before the first `fetch_cash()` call, and each `Holding` returned by the source must also set `currency="USD"` so the frontend renders `$` instead of `₹`.

Cross-currency totals are normalised to INR by `app.modules.brokers.fx.to_inr`. The USD→INR rate is fetched live from `https://open.er-api.com/v6/latest/USD` and cached on disk at `<dump_dir>/fx-rates-live.csv` with a 1-hour TTL (`_TTL_SECONDS = 3600`); on live-fetch failure it falls back to the last cached row, then to `FALLBACK_INR_PER_USD = 83.41`. The conversion is applied in `HoldingsAggregator.totals/allocation/treemap` and `wallet_aggregator._aggregate_holdings`, so `WalletInfo.holdings_value` / `pnl` and the global compact-bar totals are all in INR. Free cash is still reported in the broker's native `currency`; the frontend reads the current rate via `GET /portfolio/fx` (TanStack `useFx`, `staleTime` = TTL) and threads it into `aggregateAll` / `toInr` for the "All" wallet cash sum.

Routes (mounted under `/portfolio/cash`):

- `GET /portfolio/cash` — cached snapshot of every cash-capable broker (no network); hydrates `src._cash` from `broker-cash-live.csv` on cold start.
- `POST /portfolio/cash/sync` — refresh all cash-capable brokers in parallel.
- `POST /portfolio/cash/{slug}/sync` — refresh one broker. Returns 422 if `supports_cash = False`.

Persistence: `cash_dump.py` writes one CSV file (`broker-cash-live.csv`) with one row per slug — TTL is per-row via the stored `as_of`, so each broker has its own freshness window. Never bypass this layer with a custom on-disk cache.

## Register the new source

Four steps. Do not skip step 4 — the notebook is the single artifact that proves the source works end-to-end without booting the frontend.

**1. Wire the source into the registry** — [registry.py](../backend/app/modules/brokers/registry.py):

```python
from app.modules.brokers.mybroker import MyBrokerSource

def _build_sources() -> dict[str, BrokerSource]:
    instances: list[BrokerSource] = [
        ZerodhaKiteSource(),
        GrowwSource(),
        AngelOneSource(),
        IndMoneySource(),
        TickerTapeSource(),
        MyBrokerSource(),    # ← add here
    ]
    return {s.slug: s for s in instances}
```

**2. Declare credentials** — store the user ID / API key in the afbach vault:

```bash
# Unlock the vault first if needed
afbach unlock   # or POST http://[::1]:54087/v1/unlock

# Store the secret
curl -s -X PUT http://[::1]:54087/v1/secrets \
  -H "X-Afbach-Token: $AFBACH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"key": "MYBROKER_USER_ID", "value": "<your-id>"}'
```

Vault-only keys (user IDs, API keys) are **not** added to `.env.cred.example`. Only fallback/bootstrap values that must survive a locked vault (e.g. `BROKER_CACHE_KEY`, `JWT_SECRET_KEY`) belong there.

**3. Add a CSV fixture + parser test** — drop a sample export at `backend/tests/fixtures/broker_csvs/{slug}_holdings.csv` and add a `Test{Broker}Parser` class in `backend/tests/test_brokers.py`. The shared `BrokerSource.parse()` contract is what the `/sources/{slug}/upload` endpoint relies on.

**4. Add a dev notebook (required)** — copy an existing notebook (e.g. `backend/notebooks/zerodha_kite_dev.ipynb`) to `backend/notebooks/{slug}_dev.ipynb` and search-and-replace the slug + auth instructions. The notebook must exercise, in order:

1. `GET /portfolio/sources/{slug}` — confirm `status` transitions on env var presence
2. `POST /portfolio/sources/{slug}/sync` — trigger the live fetch
3. `POST /portfolio/sources/{slug}/upload` — confirm the CSV fallback still works
4. `GET /portfolio/holdings?source={slug}` + allocation
5. `GET /portfolio/treemap?source={slug}`
6. `GET /portfolio/rebalance?source={slug}`
7. `GET /portfolio/cash` + `POST /portfolio/cash/{slug}/sync` — only if `supports_cash = True` (otherwise assert 422)
8. Standalone `dump_{slug}()` call — bypasses FastAPI, proves the helper works alone
9. Cache reset

Both `MODE = "http"` (against a live server) and `MODE = "in_process"` (FastAPI `TestClient`) must run clean.

---

## IndMoney (`indmoney`)

US-stocks holdings from INDmoney's DriveWealth-backed brokerage account. CDP browser fetch with an on-disk cache — same pattern as Groww / Angel One. No CSV upload path.

| Detail | Value |
|--------|-------|
| Slug | `indmoney` |
| Auth | Manual login at `indmoney.com` inside the AlphaForge Anton Chrome (`--remote-debugging-port=9299`); backend attaches over CDP. |
| `REQUIRED_ENV` | `INDMONEY_USER_ID` |
| Asset classes | `EQUITY` (US stocks — fractional shares via DriveWealth) |
| Currency | **USD** (`currency = "USD"` on the source; every `Holding` is emitted with `currency="USD"`) |
| Kind | `SourceKind.API` |
| Cache TTL | `INDMONEY_REFETCH_SECONDS` (default `3600`) |
| **Trigger page** | `www.indmoney.com/investments/us-stocks/my-us-stocks` |
| **Holdings endpoint** | `apixt-fz.indmoney.com/us-stock-broker/us/portfolio/equity/summary?response_format=json` — probe-confirmed 2026-05-25 |
| **Holdings key** | `demat_summary.asset_summary.scrip_details` — list of `{metadata: {symbol, name, live_price, day_change_percentage, sector}, holdings: {quantity, avg_price, invested_amount, current_value, overall_pnl, overall_pnl_percentage}}` |
| **Field mapping** | `metadata.symbol→symbol`, `metadata.name→name`, `metadata.live_price→last_price`, `metadata.day_change_percentage→day_change_pct`, `holdings.avg_price→avg_price`, `holdings.invested_amount→invested`, `holdings.current_value→current_value`, `holdings.overall_pnl→pnl`, `holdings.overall_pnl_percentage→pnl_pct` |
| **Cash endpoint** | `apixt-iw.indmoney.com/ind-investment/api/v4/user/basic/` — field `cash_available_for_trade` (USD). Probe-confirmed 2026-05-25. |
| **Helpers** | [`indmoney_source_helper.py`](../backend/app/modules/brokers/indmoney/indmoney_source_helper.py), [`indmoney_dump.py`](../backend/app/modules/brokers/indmoney/indmoney_dump.py), [`indmoney_cash_helper.py`](../backend/app/modules/brokers/indmoney/indmoney_cash_helper.py) |

**Setup**:

1. Start Chrome with `--remote-debugging-port=9299 --user-data-dir=$HOME/.cache/alphaforge-anton-chrome`.
2. Log in to [indmoney.com](https://indmoney.com) inside that Chrome window.
3. Store `INDMONEY_USER_ID` in the afbach vault: `PUT /v1/secrets {"key": "INDMONEY_USER_ID", "value": "<your-id>"}`. The source auto-upgrades to `READY` on next startup (or vault unlock).

---

## Ticker Tape (`tickertape`)

Digital gold (SafeGold) balance from Ticker Tape. Captures two XHRs on page load and combines them into a single `DIGITAL_GOLD` holding. CDP browser fetch with an on-disk cache — same pattern as Groww / Angel One. No CSV upload path.

| Detail | Value |
|--------|-------|
| Slug | `tickertape` |
| Auth | Manual login at `tickertape.in` inside the AlphaForge Anton Chrome (`--remote-debugging-port=9299`); backend attaches over CDP. |
| `REQUIRED_ENV` | `TICKERTAPE_USER_ID` |
| Asset classes | `GOLD` (single DIGITAL_GOLD holding, quantity in grams) |
| Kind | `SourceKind.API` |
| Cache TTL | `TICKERTAPE_REFETCH_SECONDS` (default `3600`) |
| **Trigger page** | `www.tickertape.in/portfolio/digital-gold` |
| **Profile endpoint** | `gold.api.tickertape.in/profile/v2` → `{goldBalance, averageBuyPrice, goldExponent, priceExponent}` |
| **Price endpoint** | `gold.api.tickertape.in/price?type=BUY` → `{currentPrice}` (₹/gram) |
| **Normalization** | `qty = goldBalance × 10^goldExponent`, `avg = averageBuyPrice × 10^priceExponent`, `ltp = currentPrice` |
| **Helpers** | [`tickertape_source_helper.py`](../backend/app/modules/brokers/tickertape/tickertape_source_helper.py), [`tickertape_dump.py`](../backend/app/modules/brokers/tickertape/tickertape_dump.py) |

**Setup**:

1. Start Chrome with `--remote-debugging-port=9299 --user-data-dir=$HOME/.cache/alphaforge-anton-chrome`.
2. Log in to [tickertape.in](https://tickertape.in) inside that Chrome window.
3. Store `TICKERTAPE_USER_ID` in the afbach vault: `PUT /v1/secrets {"key": "TICKERTAPE_USER_ID", "value": "<your-id>"}`. The source auto-upgrades to `READY` on next startup (or vault unlock).

---

## Binance (`binance`)

Spot wallet holdings from a personal Binance account. Crypto assets, values
treated as USDT (≡ USD) — `fx.to_inr` converts to INR for portfolio totals.
CDP browser fetch with an on-disk cache — same pattern as Groww / IndMoney.

| Detail | Value |
|--------|-------|
| Slug | `binance` |
| Auth | Manual login at `binance.com` inside the AlphaForge Anton Chrome (`--remote-debugging-port=9299`); backend attaches over CDP. |
| `REQUIRED_ENV` | `BINANCE_USER_ID` |
| Asset classes | `CRYPTO` |
| Currency | **USD** (`currency = "USD"`; every `Holding` emitted with `currency="USD"`. USDT/USDC/BUSD/FDUSD are treated 1:1 with USD) |
| Kind | `SourceKind.API` |
| Cache TTL | `BINANCE_REFETCH_SECONDS` (default `3600`) |
| **Trigger page** | `www.binance.com/en/my/wallet/account/main` |
| **Holdings endpoint** | `/bapi/asset/v2/private/asset-service/wallet/balance` (probe-confirm before trusting) |
| **Holdings key** | `data` — list of `{asset, free, locked, fiatValuation, ...}` |
| **Field mapping** | `asset→symbol`, `free+locked→quantity`, `fiatValuation→current_value`, `last_price = fiatValuation/quantity` |
| **Cash endpoint** | same `wallet/balance` payload — sum of `data[].free` where `asset ∈ {USDT, USDC, BUSD, FDUSD}` |
| **Helpers** | [`binance_source_helper.py`](../backend/app/modules/brokers/binance/binance_source_helper.py), [`binance_dump.py`](../backend/app/modules/brokers/binance/binance_dump.py), [`binance_cash_helper.py`](../backend/app/modules/brokers/binance/binance_cash_helper.py) |

**Setup**:

1. Start Chrome with `--remote-debugging-port=9299 --user-data-dir=$HOME/.cache/alphaforge-anton-chrome`.
2. Log in to [binance.com](https://binance.com) inside that Chrome window.
3. Store `BINANCE_USER_ID` in the afbach vault: `PUT /v1/secrets {"key": "BINANCE_USER_ID", "value": "<your-id>"}`. The source auto-upgrades to `READY` on next startup (or vault unlock).
4. Run `uv run python probes/binance_probe.py` once to confirm the holdings XHR URL still matches `BINANCE_HOLDINGS_URL_NEEDLES`. Crypto exchanges rotate endpoints more aggressively than equity brokers.

AlphaForge Anton never sees your password or 2FA — login happens in your own Chrome; the backend just reads the authenticated XHR off the wire.

**Standalone dump**:

```bash
python -m app.modules.brokers.binance.binance_dump
python -m app.modules.brokers.binance.binance_dump --force-login
ls ~/.alphaforge-anton/portfolio-dumps/binance-*
```

---

## Zerodha Kite (`zerodha`)

Equity-only holdings from the Zerodha Kite platform. ETF and mutual fund
holdings are excluded — they live exclusively in the `zerodha_coin` source.
Uses a CDP-attached Chrome session to acquire the `enctoken` cookie.

| Detail | Value |
|--------|-------|
| Slug | `zerodha` |
| Module dir | `backend/app/modules/brokers/zerodha_kite/` |
| Auth | Manual login at `kite.zerodha.com` inside the AlphaForge Anton Chrome (`--remote-debugging-port=9299`); enctoken cookie read via CDP. |
| `REQUIRED_ENV` | `ZERODHA_USER_ID` |
| Asset classes | `EQUITY` only — ETF rows are filtered out before the CSV is written |
| Kind | `SourceKind.API` |
| Cache TTL | `ZERODHA_REFETCH_SECONDS` (default `3600`) |
| `supports_cash` | `True` — `GET /oms/user/margins` → `data.equity.available.cash` |
| **Holdings endpoint** | `kite.zerodha.com/oms/portfolio/holdings` (enctoken auth, `X-Kite-Version: 3`) |
| **Instrument type** | `zerodha_kite_instruments.py` resolves `tradingsymbol → instrument_type (EQ/ETF)` via the public Kite instruments dump. Rows where `instrument_type == ETF` are dropped before writing CSV. |
| **Helpers** | [`zerodha_kite_source_helper.py`](../backend/app/modules/brokers/zerodha_kite/zerodha_kite_source_helper.py), [`zerodha_kite_dump.py`](../backend/app/modules/brokers/zerodha_kite/zerodha_kite_dump.py), [`zerodha_kite_instruments.py`](../backend/app/modules/brokers/zerodha_kite/zerodha_kite_instruments.py) |

**Standalone dump**:

```bash
python -m app.modules.brokers.zerodha_kite.zerodha_kite_dump
python -m app.modules.brokers.zerodha_kite.zerodha_kite_dump --force-login
ls ~/.alphaforge-anton/portfolio-dumps/zerodha-*
```

---

## Zerodha Coin (`zerodha_coin`)

ETF and mutual fund holdings from Zerodha. Uses the same `enctoken` as the
Kite equity source — no separate Coin login needed. ETF holdings are fetched
from the Kite equity endpoint and filtered by instrument type; MF holdings come
from the Coin MF endpoint. Both are merged into one CSV under the `zerodha_coin`
slug.

| Detail | Value |
|--------|-------|
| Slug | `zerodha_coin` |
| Auth | Manual login at `kite.zerodha.com` inside the AlphaForge Anton Chrome (`--remote-debugging-port=9299`); `enctoken` re-used for both Kite equity and Coin MF endpoints. |
| `REQUIRED_ENV` | `ZERODHA_USER_ID` (shared with the `zerodha` Kite source) |
| Asset classes | `ETF` (from Kite equity API, filtered by `instrument_type == ETF`) + `MUTUAL_FUND` (from Coin MF API) |
| Kind | `SourceKind.API` |
| Cache TTL | `ZERODHA_COIN_REFETCH_SECONDS` (default `3600`) |
| `supports_cash` | `False` — Coin is MF/ETF-only, not a trading account |
| **MF endpoint** | `kite.zerodha.com/api/mf/holdings` (enctoken auth, `X-Kite-Version: 3`) — probe-confirmed 2026-05-22 |
| **ETF endpoint** | `kite.zerodha.com/oms/portfolio/holdings` (same as Kite equity) — rows where `instrument_type == ETF` are kept; all others discarded |
| **MF key** | `data` — list of `{tradingsymbol, fund, folio, quantity, average_price, last_price, pnl, …}` |
| **Field mapping** | `tradingsymbol→symbol`, `fund→name`, `quantity`, `average_price→avg_price`, `last_price`, computed `invested/current_value/pnl/pnl_pct` |
| **Helpers** | [`zerodha_coin_source_helper.py`](../backend/app/modules/brokers/zerodha_coin/zerodha_coin_source_helper.py), [`zerodha_coin_dump.py`](../backend/app/modules/brokers/zerodha_coin/zerodha_coin_dump.py) |

**Setup**:

1. Start Chrome with `--remote-debugging-port=9299 --user-data-dir=$HOME/.cache/alphaforge-anton-chrome`.
2. Log in to [kite.zerodha.com](https://kite.zerodha.com) inside that Chrome window.
3. Store `ZERODHA_USER_ID` in the afbach vault: `PUT /v1/secrets {"key": "ZERODHA_USER_ID", "value": "<your-id>"}` (shared with the Kite source). The source auto-upgrades to `READY` on next startup (or vault unlock).

AlphaForge Anton never sees your password or TOTP — login happens in your own Chrome; the backend reads the `enctoken` cookie from the running CDP session.

**Standalone dump**:

```bash
python -m app.modules.brokers.zerodha_coin.zerodha_coin_dump
python -m app.modules.brokers.zerodha_coin.zerodha_coin_dump --force-login
ls ~/.alphaforge-anton/portfolio-dumps/zerodha_coin-*
```

---

## Angel One (`angelone`)

SmartAPI's free tier proved unreliable for personal sync (rate limits, TOTP friction, 401s on long-lived JWTs). AlphaForge Anton now attaches to the running Chrome over CDP and captures the XHR Angel One's own web app makes — same pattern as Groww.

| Detail | Value |
|--------|-------|
| Slug | `angelone` |
| Auth | Manual login at `angelone.in` inside the AlphaForge Anton Chrome (`--remote-debugging-port=9299`); backend attaches over CDP. |
| `REQUIRED_ENV` | `ANGELONE_CLIENT_ID` |
| Asset classes | `AssetClass.EQUITY` (Bonds/SGBs/MFs come back in the same response but aren't surfaced yet) |
| CSV TTL | `ANGELONE_REFETCH_SECONDS` (default `3600`) |
| **Trigger page** | `www.angelone.in/trade/portfolio/equity` |
| **Confirmed holdings endpoint** | `POST portfolio-prod.angelone.in/family/v2/superportfolio` |
| **Holdings key** | `data.EquityPortfolio.HoldingDetail` |
| **Confirmed cash endpoint** | `POST amx-*.angelone.in/funds/v2/getRMSLimit` |
| **Cash key** | `data.netAvailableFunds` (fallback: `fundsForTrading`, `fundsAvailable`) |
| **Helpers** | [`angelone_source_helper.py`](../backend/app/modules/brokers/angelone/angelone_source_helper.py), [`angelone_cash_helper.py`](../backend/app/modules/brokers/angelone/angelone_cash_helper.py) |

**Field mapping** (probe-confirmed superportfolio row → `normalize()` → `_holding_from_row`):

| API field | `Holding` field | Notes |
|-----------|-----------------|-------|
| `tradeSymbol` | `symbol` | Upper-cased; carries the series suffix (e.g. `PGINVIT-IV`). Falls back to `symbolName`. |
| `compName` / `details` | `name` | — |
| `isin` | `isin` | — |
| `exchName` | `exchange` | Default `NSE` |
| `qty` / `total_qty` / `AvlQty` | `quantity` | — |
| `avgPrice` / `baseAvgPrice` | `avg_price` | — |
| `ltp` | `last_price` | Falls back to `avg_price` if absent |

**Setup**:

1. Start Chrome with `--remote-debugging-port=9299 --user-data-dir=$HOME/.cache/alphaforge-anton-chrome`.
2. Log in to [angelone.in](https://angelone.in) inside that Chrome window.
3. Store `ANGELONE_CLIENT_ID` in the afbach vault: `PUT /v1/secrets {"key": "ANGELONE_CLIENT_ID", "value": "<your-id>"}`. The source auto-upgrades to `READY` on next startup (or vault unlock).

AlphaForge Anton never sees your password or TOTP — login + 2FA happen in your own Chrome; the backend just reads the authenticated XHR off the wire.

**Mutual funds**: not exposed by the equity holdings page. For MF, use the CSV upload fallback (`/sources/angelone/upload`) with an Angel One MF export.

**Standalone dump**:

```bash
python -m app.modules.brokers.angelone.angelone_dump
python -m app.modules.brokers.angelone.angelone_dump --force-login
ls ~/.alphaforge-anton/portfolio-dumps/angelone-*
```

---

## Dev notebooks

One notebook per broker lives in `backend/notebooks/`. Each exercises all
`/portfolio/*` endpoints scoped to that broker and works in both
`MODE="http"` (live server) and `MODE="in_process"` (FastAPI test client).

| Broker | Notebook | Auth |
|--------|----------|------|
| Zerodha | [zerodha_kite_dev.ipynb](../backend/notebooks/zerodha_kite_dev.ipynb) | CDP enctoken (`kite.zerodha.com`) |
| Groww | [groww_dev.ipynb](../backend/notebooks/groww_dev.ipynb) | CDP browser fetch (`groww.in`) |
| Angel One | [angelone_dev.ipynb](../backend/notebooks/angelone_dev.ipynb) | CDP browser fetch (`angelone.in`) |
| IndMoney | [`indmoney_dev.ipynb`](../backend/notebooks/indmoney_dev.ipynb) | CDP browser fetch (`indmoney.com/investments/us-stocks/my-us-stocks`) |
| Ticker Tape | [`tickertape_dev.ipynb`](../backend/notebooks/tickertape_dev.ipynb) | CDP browser fetch (`tickertape.in/portfolio/digital-gold`) |
| Binance | [`binance_dev.ipynb`](../backend/notebooks/binance_dev.ipynb) | CDP browser fetch (`binance.com/en/my/wallet/account/main`) |
| Zerodha Coin | [`zerodha_coin_dev.ipynb`](../backend/notebooks/zerodha_coin_dev.ipynb) | Kite enctoken (`kite.zerodha.com` — shared with `zerodha`) |

Every new broker must ship a notebook in this list — see step 4 of [Register the new source](#register-the-new-source).

## XHR probes

Probe scripts in `backend/scripts/` attach to Chrome and print every
matching XHR shape. Run these **before** implementing `normalize()` to
discover the real endpoint URL and response key names.

| Broker | Probe script | Technique |
|--------|-------------|-----------|
| Zerodha | [zerodha_probe.py](../probes/zerodha_probe.py) | Reads `enctoken` cookie → direct Kite OMS REST calls |
| Groww | [groww_probe.py](../probes/groww_probe.py) | XHR interception on page reload |
| Angel One | [angelone_probe.py](../probes/angelone_probe.py) | XHR interception across holdings + funds pages |
| IndMoney | [indmoney_probe.py](../probes/indmoney_probe.py) | XHR interception on dashboard reload |
| Ticker Tape | [tickertape_probe.py](../probes/tickertape_probe.py) | XHR interception on portfolio reload |
| Binance | [binance_probe.py](../probes/binance_probe.py) | XHR interception on spot-wallet reload |
| Zerodha Coin | [zerodha_coin_probe.py](../probes/zerodha_coin_probe.py) | Reads `enctoken` cookie → direct Kite `/api/mf/holdings` REST call |

```bash
uv run python probes/zerodha_probe.py
uv run python probes/groww_probe.py
uv run python probes/angelone_probe.py
uv run python probes/indmoney_probe.py
uv run python probes/tickertape_probe.py
uv run python probes/binance_probe.py
```

Zerodha's probe is different: rather than intercepting XHRs, it reads the
`enctoken` cookie from Chrome and fires direct REST calls against the Kite
OMS API (`/oms/portfolio/holdings`, `/oms/portfolio/positions`,
`/oms/user/profile`, `/oms/user/margins`). Useful for verifying the token
is still valid and inspecting the live holdings shape.

Sections in each notebook:
1. Source info — verify `status: ready`
2. Sync — triggers CDP fetch + CSV cache (API sources) / Upload CSV (CSV sources)
3. Holdings — filtered by slug
4. Allocation breakdown
5. Treemap
6. Rebalance / drift
7. Standalone dump (API sources only — bypasses FastAPI)
8. Reset in-memory cache

---

## Auth patterns in use

### CDP enctoken (Zerodha)

Chrome is started externally with `--remote-debugging-port=9299`. The helper attaches over CDP via `_cdp.py`, reads the `enctoken` cookie after the user logs in manually, then caches it via `_http.save_session()`. Subsequent calls skip CDP entirely until the token is rejected (401/403).

Key helpers: `connect_existing_chrome`, `find_or_open_page`, `cookie_value` from `app.modules.brokers._cdp`.

### CDP browser fetch (Groww)

Similar CDP attach, but instead of reading a cookie the helper executes a `fetch()` call inside the authenticated page context and returns the JSON response directly. Used when the broker's API is not publicly documented or requires browser-side cookies that can't be trivially extracted.

Key helper: `fetch_holdings_via_browser` from `groww_source_helper.py`.

### Session caching

Both patterns use `_http.load_session` / `save_session` to persist the acquired credential across process restarts. The session file lives under `~/.alphaforge-anton/sessions/{slug}.json` with `chmod 600`.

---

## CSV cache rules

All CSV I/O goes through `dump_utils` — never reimplement in broker code:

```python
from app.modules.brokers.dump_utils import (
    live_csv_path,    # (slug) -> Path  — {slug}-holdings-live.csv
    dated_csv_path,   # (slug) -> Path  — {slug}-holdings-YYYY-MM-DD.csv
    is_csv_fresh,     # (slug, ttl_seconds) -> bool
    read_csv,         # (slug) -> list[dict[str, str]]
    write_csv,        # (rows, dst, *, source) -> None
)
```

CSV output directory: `$PORTFOLIO_DUMP_DIR` env var or `~/.alphaforge-anton/portfolio-dumps/` (see [broker-csv-dumps.md](broker-csv-dumps.md)).

---

## `Holding` fields

All fields the portfolio layer cares about:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `source` | `str` | yes | broker slug |
| `asset_class` | `AssetClass` | yes | usually `EQUITY` |
| `symbol` | `str` | yes | trading symbol, upper-cased |
| `isin` | `str \| None` | no | — |
| `quantity` | `float` | yes | — |
| `avg_price` | `float` | yes | — |
| `last_price` | `float` | yes | — |
| `invested` | `float` | yes | `qty × avg_price` |
| `current_value` | `float` | yes | `qty × last_price` |
| `pnl` | `float` | yes | `current_value − invested` |
| `pnl_pct` | `float` | yes | `pnl / invested × 100` |
| `exchange` | `str \| None` | no | `"NSE"` default |

---

## Environment variables

Only add **non-secret config** (TTLs, feature flags) to `.env.cred.example`. User IDs and API keys are vault-only — do not list them in any `.env` file:

```bash
# MyBroker — add to root .env (non-secret tuning knobs only)
MYBROKER_REFETCH_SECONDS=3600  # optional TTL, default 1h
```

Store the actual credential in the afbach vault:

```bash
curl -s -X PUT http://[::1]:54087/v1/secrets \
  -H "X-Afbach-Token: $AFBACH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"key": "MYBROKER_USER_ID", "value": "<your-id>"}'
```

The `REQUIRED_ENV` tuple in `{slug}_source_helper.py` lists every variable that must be non-empty before the source is usable. `source_ready(REQUIRED_ENV, env)` in `__init__` reads it and logs a vault-locked hint when keys are missing because the vault is locked. `require_env(key, env)` in acquire/fetch functions raises immediately with the same hint instead of timing out after 180s of CDP waiting.
---

## Quick sanity check after wiring up

```bash
# Run standalone dump (bypasses FastAPI, tests auth + CSV write end-to-end)
python -m app.modules.brokers.mybroker.mybroker_dump

# Force a fresh login
python -m app.modules.brokers.mybroker.mybroker_dump --force-login

# Check the output
ls ~/.alphaforge-anton/portfolio-dumps/mybroker-*
```

## AlphaForge Anton — Commands
<a id="commands"></a>
_`commands` · general_

# AlphaForge Anton — Commands

```bash
# ── Local development (all services) ────────────────────────────────────────
./start.sh                # Start PostgreSQL, Redis, Bach vault, backend, frontend
./stop.sh                 # Stop all services started by start.sh

# ── Full repo setup ───────────────────────────────────────────────────────────
./setup.sh                # One command to set up everything
./setup.sh --help         # Show all setup.sh options

# ── Setup — granular ─────────────────────────────────────────────────────────
./setup.sh --prereqs      # Check/install pyenv, nvm, pnpm, uv
./setup.sh --venv         # Create .venv via `uv venv` (reads .python-version)
./setup.sh --backend      # Sync the entire Python workspace (uv sync)
./setup.sh --frontend     # Frontend + workspace deps (pnpm) + build ravel-ui
./setup.sh --env          # Scaffold .env files from examples
./setup.sh --dirs         # Create log/data/model directories
./setup.sh --db           # Setup local PostgreSQL + Redis (macOS Homebrew)

# ── Python Workspace (uv) ────────────────────────────────────────────────────
uv sync                              # Install/refresh every workspace member into .venv
uv lock                              # Refresh uv.lock without installing
uv add httpx --package alphaforge-anton-backend   # Add a dep to a specific member
just sync                            # Same as `uv sync` (justfile shortcut)

# ── Backend ──────────────────────────────────────────────────────────────────
cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
cd backend && uv run pytest -v
uv run ruff check .

# ── Backend Debugging (VS Code) ──────────────────────────────────────────────
# Option A — launch directly: pick "Backend: FastAPI (uvicorn, debug)" in Run & Debug (F5)
# Option B — attach to running process:
just backend-debug                   # Starts uvicorn under debugpy (waits on :5678)
                                     # Then pick "Backend: Attach (debugpy on :5678)" in VS Code
# Option C — debug current pytest file: open a test file → "Backend: Pytest (current file)"

# ── Frontend ─────────────────────────────────────────────────────────────────
cd frontend && pnpm dev              # Dev server
cd frontend && pnpm lint             # Lint
cd frontend && pnpm type-check       # TypeScript check

# ── UI Package ───────────────────────────────────────────────────────────────
cd packages/ravel-ui && pnpm build   # Build ESM + CJS + DTS
cd packages/ravel-ui && pnpm dev     # Watch mode

# ── Infrastructure ───────────────────────────────────────────────────────────
./setup.sh --db                                                  # macOS native (Homebrew)
# OR:
docker compose -f infra/docker-compose.yml up -d                 # via OrbStack

# ── Migrations ───────────────────────────────────────────────────────────────
cd backend && uv run alembic upgrade head
cd backend && uv run alembic revision --autogenerate -m "description"

# ── Probes (UI + Broker verification) ────────────────────────────────────────
# Probes attach to the existing Chrome session via CDP (:9299) — never use Playwright MCP.
# See probes/WHY_PROBES_NOT_MCP.md for the rationale.

just zerodha-chrome          # Open Chrome with CDP on :9299 (required by all UI probes)

# UI probes — full-stack verification via CDP
just ui-probe                # Full UI smoke test: auth, dashboard, portfolio, console errors
just ui-portfolio            # Portfolio filter probe: chips, sort, PnL filter, text search
just ui-screens              # Capture terminal / portfolio / preferences screenshots
just ui-pref-tabs            # Walk every Preferences sidebar tab → screenshots
just ui-concierge            # Concierge AI chat UI probe
just ui-model-picker         # Model picker UI probe

# Or run directly:
uv run python probes/ui_probe.py
uv run python probes/ui_portfolio_probe.py
uv run python probes/ui_screens.py

# Broker XHR probes — confirm live API endpoints match source code
just probe-zerodha           # Zerodha equity holdings (enctoken)
just probe-zerodha-coin      # Zerodha Coin MF holdings (enctoken)
just probe-zerodha-cash      # Zerodha free cash
just probe-groww             # Groww equity holdings (XHR intercept)
just probe-groww-cash        # Groww free cash
just probe-angelone          # Angel One holdings (XHR intercept)
just probe-angelone-cash     # Angel One free cash
just probe-indmoney          # IndMoney US holdings (XHR intercept)
just probe-indmoney-cash     # IndMoney free cash
just probe-binance           # Binance crypto wallet (XHR intercept)
just probe-binance-cash      # Binance free cash
just probe-tickertape        # Ticker Tape portfolio (XHR intercept)
just probe-gullak            # Gullak gold holdings

# ── Repo Context MCP ─────────────────────────────────────────────────────────
# (code-search server for Claude/Copilot/Cursor — separate from UI probes)
cd repo-context-mcp && pdm install                               # Install deps
cd repo-context-mcp && pdm run index --full                      # Build initial vector index
cd repo-context-mcp && pdm run index --watch                     # Watch + incremental reindex
cd repo-context-mcp && pdm run serve                             # Run MCP server (stdio)
alphaforge-anton-repo-context-mcp                                      # Same server (after `pdm install`)

# ── Cleanup ──────────────────────────────────────────────────────────────────
./clean.sh                # Remove build artifacts and bytecode (keeps venv + node_modules)
./clean.sh --cache        # Remove only tool caches
./clean.sh --venv         # Remove Python venv
./clean.sh --backend      # Deep-clean backend (artifacts, caches, venv)
./clean.sh --frontend     # Deep-clean frontend (.next, node_modules)
./clean.sh --all          # Nuclear clean — removes everything (run setup.sh to restore)
```

## Getting Started — Developer Setup
<a id="getting-started"></a>
_`getting-started` · general_

# Getting Started — Developer Setup

## Prerequisites

| Tool | Version | Install | Notes |
|------|---------|---------|-------|
| pyenv | Latest | `brew install pyenv` | Manages Python versions; reads `.python-version` |
| Python | 3.14+ | `pyenv install 3.14.2` | Pinned in `.python-version` |
| PDM | Latest | `brew install pdm` | Installs into repo-root `.venv/` (see `backend/pdm.toml`) |
| uv | Latest | `brew install uv` | Fast resolver/installer for PDM |
| nvm | Latest | [nvm-sh/nvm](https://github.com/nvm-sh/nvm) | Manages Node versions; reads `.nvmrc` |
| Node.js | 22+ | `nvm install` | Pinned in `.nvmrc` |
| pnpm | 9+ | `corepack enable && corepack prepare pnpm@latest --activate` | Config in `.npmrc` |
| Git | Latest | `brew install git` | — |

**Optional (for container workflow):**

| Tool | Install | Notes |
|------|---------|-------|
| OrbStack | [orbstack.dev](https://orbstack.dev) | Lightweight Docker alternative for macOS (~6x less RAM than Docker Desktop) |
| Docker Desktop | [docker.com](https://www.docker.com/products/docker-desktop) | Heavier but more established |

> **For MacBook Air M4 (16GB RAM):** We recommend the **native local setup** (Option 1 below). It uses Homebrew to run PostgreSQL and Redis natively with zero container overhead. If you need containers, use **OrbStack** instead of Docker Desktop — it's purpose-built for Apple Silicon and uses a fraction of the memory.

---

## Option 1: Native Local Development (Recommended for macOS)

The fastest, lightest setup — no Docker at all:

```bash
# 1. Clone the repository
git clone https://github.com/your-username/alpha-forge-anton.git
cd alpha-forge-anton

# 2. Full automated setup (prereqs check, venv, deps, env files, dirs)
./setup.sh
# This checks pyenv/nvm/pnpm/pdm, creates .venv, installs all deps,
# scaffolds .env files, and creates required directories.

# 3. Setup PostgreSQL & Redis via Homebrew
./setup.sh --db
# OR: just db-local

# 4. Review & update environment files
# Edit backend/.env and frontend/.env.local with your credentials

# 5. Run database migrations
just db-migrate

# 6. Start development servers
just dev-local              # Backend + frontend via Procfile
```

**Or step-by-step if you prefer granular control:**
```bash
./setup.sh --prereqs        # Check/install system tools
./setup.sh --venv           # Create .venv from .python-version
./setup.sh --backend        # Install backend deps (PDM)
./setup.sh --frontend       # Install frontend + workspace deps (pnpm)
./setup.sh --screener       # Install screener ML deps (pip)
./setup.sh --env            # Scaffold .env files from templates
./setup.sh --dirs           # Create log/data/model directories
./setup.sh --db             # Setup local PostgreSQL + Redis
```

**Start everything at once** with a process manager:
```bash
brew install overmind       # or: pip install honcho
just dev-local              # Starts backend + frontend from Procfile
```

---

## Option 2: Containers (OrbStack or Docker)

If you prefer containers, or are on Linux/Windows:

```bash
# 1. Install OrbStack (macOS) or Docker Desktop
# OrbStack: brew install orbstack  (recommended for Apple Silicon)
# Docker:   brew install --cask docker

# 2. Clone and configure
git clone https://github.com/your-username/alpha-forge-anton.git
cd alpha-forge-anton
cp backend/.env.example backend/.env

# 3. Start everything
docker compose -f infra/docker-compose.yml up --build

# Backend API: http://localhost:8000
# API Docs:    http://localhost:8000/docs
# Frontend:    http://localhost:3000
```

---

## Option 3: GitHub Codespaces

This repo includes a `.devcontainer/devcontainer.json` for instant cloud development:

1. Go to the GitHub repo → Click **Code** → **Codespaces** → **Create codespace**
2. Wait for the container to build (installs pdm + pnpm + all deps)
3. Backend and frontend are ready to start:
   ```bash
   cd backend && pdm run dev      # Terminal 1
   cd frontend && pnpm dev        # Terminal 2
   ```
4. Codespaces auto-forwards ports 8000 and 3000

---

## Configuration

### Required Environment Variables

All ports are defined in [`.env.port`](../.env.port) at the repo root. The credential template is `.env.cred.example` (tracked in git, blank values only); real secrets go in `.env.cred.local` (gitignored). Copy the example files:

```bash
cp .env.example .env                       # Root env (used by docker-compose)
cp .env.cred.example .env.cred.local       # Credentials — fill in real secrets here (gitignored)
cp backend/.env.example backend/.env       # Backend
cp frontend/.env.example frontend/.env.local  # Frontend (Next.js uses .env.local)
```

The only **required** variables for basic operation:

```bash
SECRET_KEY=<a-random-string-for-JWT>
DATABASE_URL=postgresql+asyncpg://alphaforge_anton:alphaforge_anton@localhost:5432/alphaforge_anton
REDIS_URL=redis://localhost:6379/0
```

### Optional — AI Features (Alpha Chat)

Alpha chat routes through the `alphaforge-anton-llm` gateway. Set **at least one** provider key:

```bash
# Gemini (default auto-route target for most queries)
GEMINI_API_KEY=AIza...

# Groq — ultra-low latency (Llama / Mixtral)
GROQ_API_KEY=gsk_...

# Claude SDK (Anthropic) — investment plan & risk analysis
ANTHROPIC_API_KEY=sk-ant-...

# Cerebras — fastest throughput (screeners / factoids)
CEREBRAS_API_KEY=...

# Mistral — EU-hosted, strong at finance (privacy/local intent)
MISTRAL_API_KEY=...

# OpenRouter — routes to GPT-4o, Command R+, etc.
OPENROUTER_API_KEY=sk-or-...

# HuggingFace Inference API — open-source models
HUGGINGFACE_API_KEY=hf_...
```

`model: "auto"` (the default) picks the provider automatically based on query intent (risk → Claude, screeners → Cerebras, general → Gemini). You only need keys for the providers you want available.

> **Security:** The chat endpoint (`POST /api/v1/chat/`) requires a valid JWT (`Authorization: Bearer <token>`). The frontend proxy at `/api/v1/chat` forwards the token server-side; never expose provider API keys to the browser. Response text is rendered as safe React nodes — no `dangerouslySetInnerHTML` is used.

### Optional — Broker Integration

```bash
# Zerodha Kite (get from https://developers.kite.trade)
KITE_API_KEY=your_key
KITE_API_SECRET=your_secret
```

---

## Common Commands

```bash
# ── Setup ────────────────────────────────────────
./setup.sh                 # Full repo setup (prereqs, venv, all deps, env, dirs)
./setup.sh --prereqs       # Check/install system prerequisites
./setup.sh --venv          # Create Python venv only
./setup.sh --backend       # Install backend deps only
./setup.sh --frontend      # Install frontend deps only
./setup.sh --screener      # Install screener ML deps only
./setup.sh --env           # Scaffold .env files from examples
./setup.sh --dirs          # Create required directories
./setup.sh --db            # Setup local PostgreSQL + Redis (macOS)
./setup.sh --help          # Show all setup.sh options

# ── Development ──────────────────────────────────
just help                  # Show all available Makefile commands
just dev-local             # Start backend + frontend via Procfile
just dev-docker            # Start everything with Docker/OrbStack
just backend               # Run backend locally (pdm run dev)
just frontend              # Run frontend locally (pnpm dev)

# ── Testing & Quality ────────────────────────────
just test                  # Run all tests
just lint                  # Lint backend + frontend
just format                # Auto-format backend code

# ── Database ─────────────────────────────────────
just db-local              # Setup PostgreSQL + Redis via Homebrew
just db-up                 # Start PostgreSQL + Redis via Docker
just db-migrate            # Apply pending migrations
just db-revision msg="description"  # Create new migration

# ── Screener Pipeline ────────────────────────────
./setup.sh --pipeline      # Run full data → train → backtest pipeline
./setup.sh --scan          # Run daily live scan
just screener-pipeline     # Same as above, via Makefile
just screener-scan         # Same as above, via Makefile

```

---

## Project Layout

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app factory
│   ├── core/
│   │   ├── config.py        # Pydantic settings (env vars)
│   │   ├── database.py      # SQLAlchemy async engine
│   │   └── security.py      # JWT + password hashing
│   ├── models/
│   │   ├── user.py          # User ORM model
│   │   └── portfolio.py     # Holding, Order, Watchlist models
│   ├── routes/
│   │   ├── __init__.py      # Central router registry
│   │   ├── health.py        # GET /health
│   │   ├── auth.py          # POST /auth/register, /auth/login
│   │   ├── market.py        # GET /market/quote, /indices, /history
│   │   ├── portfolio.py     # GET /portfolio/summary, /positions
│   │   ├── ai.py            # POST /ai/chat, /ai/analyze
│   │   └── trade.py         # POST /trade/order
│   └── services/
│       ├── broker_base.py   # Abstract broker interface
│       ├── broker_zerodha.py# Zerodha Kite implementation
│       ├── ai_service.py    # LLM orchestration
│       └── market_data.py   # Market data fetcher
├── alembic/                 # Database migrations
├── tests/                   # Pytest test suite
├── Dockerfile
├── pyproject.toml           # PDM config (uses uv resolver)
└── .env.example

packages/
└── ravel-ui/            # @alphaforge-anton/ravel-ui publishable package
    ├── src/
    │   ├── index.ts         # Barrel export (components + tokens)
    │   ├── components/      # Button, Input, Card, Badge, Icon, Text
    │   ├── tokens/          # Design tokens (TypeScript + JSON)
    │   │   ├── index.ts     # TS token constants
    │   │   └── tokens.json  # Machine-readable token definitions
    │   └── styles/          # fonts.css, theme.css, base.css
    ├── tsup.config.ts       # Build config → ESM + CJS + DTS
    └── package.json

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx       # Root layout (dark theme, Space Grotesk font)
│   │   ├── page.tsx         # Terminal landing page (Solar Terminal dashboard)
│   │   └── globals.css      # Global styles, design tokens, Solar Terminal theme
│   ├── components/
│   │   ├── layout/          # Header (floating nav), Sidebar (expandable)
│   │   ├── terminal/        # Terminal landing page components
│   │   │   ├── index.ts         # Barrel export for all terminal components
│   │   │   ├── SolarOrb.tsx     # Central glowing orb hero element
│   │   │   ├── AlphaBrief.tsx   # Market sentiment & risk alert card
│   │   │   ├── TerminalWatchlist.tsx # Floating watchlist shard
│   │   │   ├── PortfolioCards.tsx   # Net Worth & Allocation cards
│   │   │   ├── RiskAnalysis.tsx     # Risk analysis bar chart shard
│   │   │   └── VoiceFooter.tsx      # Voice/text input footer bar
│   │   ├── dashboard/       # MarketOverview, Watchlist (data views)
│   │   └── ai/              # AIChat component
│   └── lib/
│       ├── api.ts           # Axios API client
│       └── store.ts         # Zustand state management
├── package.json             # pnpm managed
├── tsconfig.json
├── next.config.mjs
└── Dockerfile

infra/
├── docker-compose.yml       # Container orchestration (optional)
└── setup-local.sh           # Native macOS setup (Homebrew)
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 8000 already in use | `lsof -ti:8000 \| xargs kill` |
| Port 3000 already in use | `lsof -ti:3000 \| xargs kill` |
| `pdm install` fails | Ensure pdm + uv are installed: `brew install pdm uv` |
| `pnpm` not found | Enable corepack: `corepack enable && corepack prepare pnpm@latest --activate` |
| PostgreSQL won't start (brew) | `brew services restart postgresql@16` |
| `ta-lib` install fails | Install system lib: `brew install ta-lib` |
| Frontend can't reach backend | Check CORS config in `.env` and Next.js rewrite proxy |
| Alembic migration fails | Ensure DB is running: `brew services list` or `just db-up` |
| Docker too heavy on macOS | Use native setup: `bash infra/setup-local.sh` or install OrbStack |

---

## Next Steps

Once the base setup is running:

1. **Explore the API** at http://localhost:8000/docs
2. **Try the AI chat** (once you add an OpenAI key)
3. **Connect a broker** (get Zerodha Kite API key from developers.kite.trade)
4. **Check the roadmap** in [WHAT.md](WHAT.md) for upcoming features
5. **Open in Codespaces** for zero-setup cloud development
6. **Contribute** — pick an issue, create a PR!

## How AlphaForge Anton Works
<a id="how"></a>
_`how` · general_

# How AlphaForge Anton Works

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│               Next.js 15 + React 19 + TypeScript             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │Dashboard │ │ Charts   │ │Portfolio │ │   AI Chat    │   │
│  │  Panel   │ │(LW Charts│ │  View    │ │  Interface   │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │
│           │          │           │              │             │
│           └──────────┴───────────┴──────────────┘            │
│                         REST + WebSocket                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                     API GATEWAY (FastAPI)                     │
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │  Auth    │ │ Market   │ │  Trade   │ │     AI       │   │
│  │ Routes   │ │  Routes  │ │  Routes  │ │   Routes     │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘   │
│       │             │            │               │           │
│  ┌────┴─────────────┴────────────┴───────────────┴───────┐  │
│  │                   SERVICE LAYER                        │  │
│  │  ┌─────────────┐ ┌──────────────┐ ┌────────────────┐  │  │
│  │  │Market Data  │ │Broker Service│ │  AI Service    │  │  │
│  │  │  Service    │ │(Zerodha/Angel│ │ (LLM + RAG)   │  │  │
│  │  └──────┬──────┘ └──────┬───────┘ └───────┬────────┘  │  │
│  └─────────┼───────────────┼─────────────────┼───────────┘  │
└────────────┼───────────────┼─────────────────┼──────────────┘
             │               │                 │
             ▼               ▼                 ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │  NSE / BSE   │ │  Zerodha     │ │  OpenAI /    │
     │  Data Feeds  │ │  Kite API    │ │  LLM APIs    │
     └──────────────┘ └──────────────┘ └──────────────┘

     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │  PostgreSQL  │ │    Redis     │ │   Celery     │
     │  (primary DB)│ │ (cache/pubsub│ │  (bg tasks)  │
     └──────────────┘ └──────────────┘ └──────────────┘
```

---

## Tech Stack Deep Dive

### Backend: Python 3.14 + FastAPI

**Why Python?**
- Best-in-class ecosystem for financial analysis (pandas, numpy, ta-lib)
- Excellent ML/AI libraries (LangChain, OpenAI SDK, scikit-learn)
- FastAPI provides async performance rivaling Node.js for I/O-bound work
- Indian broker SDKs (kiteconnect, smartapi) are Python-first

**Key packages:**
| Package | Purpose |
|---------|---------|
| `fastapi` | Async API framework with auto OpenAPI docs |
| `sqlalchemy` 2.0 | Async ORM with PostgreSQL |
| `alembic` | Database schema migrations |
| `pydantic` v2 | Data validation & serialization |
| `kiteconnect` | Zerodha broker API SDK |
| `pandas` + `numpy` | Data manipulation & analysis |
| `ta-lib` | 150+ technical indicators |
| `langchain` | AI/LLM orchestration, RAG pipelines |
| `celery` | Distributed task queue for background jobs |
| `httpx` | Async HTTP client for external APIs |

**Package management**: PDM with uv as resolver/installer. Lockfile: `pdm.lock`.

### Frontend: Next.js 15 + React 19 + TypeScript

**Why Next.js?**
- Server-side rendering for fast initial load
- App Router for file-based routing
- API route proxying to backend
- Excellent TypeScript support

**Key packages:**
| Package | Purpose |
|---------|---------|
| `lightweight-charts` | TradingView's open-source charting library |
| `zustand` | Lightweight state management |
| `axios` | HTTP client for API calls |
| `socket.io-client` | Real-time WebSocket communication |
| `recharts` | Charts for portfolio/analytics views |
| `tailwindcss` v4 | Utility-first CSS with terminal aesthetic |
| `lucide-react` | Icon library |

**Package management**: pnpm (strict, disk-efficient). Lockfile: `pnpm-lock.yaml`.

### Database: PostgreSQL 16

**Schema overview:**
```
users
├── id (UUID, PK)
├── email (unique, indexed)
├── hashed_password
├── full_name
├── is_active, is_verified
└── created_at, updated_at

holdings
├── id (UUID, PK)
├── user_id (FK → users)
├── symbol, exchange
├── quantity, avg_price
└── created_at

orders
├── id (UUID, PK)
├── user_id (FK → users)
├── broker_order_id
├── symbol, exchange, side
├── order_type, product
├── quantity, price, trigger_price
├── status, status_message
└── placed_at

watchlists
├── id (UUID, PK)
├── user_id (FK → users)
├── name
├── symbols (JSON array)
└── created_at
```

### Cache & Real-Time: Redis 7

- **Quote cache** — Cache frequently-accessed stock quotes (TTL: 1-5 seconds)
- **Session store** — User sessions for faster auth
- **Pub/Sub** — Real-time price updates to WebSocket clients
- **Rate limiting** — Protect against API abuse
- **Celery broker** — Message queue for background tasks

### AI: OpenAI + LangChain

**AI Architecture:**
```
User Query
    │
    ▼
┌──────────────────────────────────────┐
│           AI ORCHESTRATOR            │
│                                      │
│  1. Parse user intent               │
│  2. Determine required data sources  │
│  3. Fetch context:                   │
│     ├─ Real-time market data         │
│     ├─ Historical price (OHLCV)      │
│     ├─ Technical indicators          │
│     ├─ Fundamental data              │
│     ├─ Recent news articles          │
│     ├─ User's portfolio (if any)     │
│     └─ Regulatory filings            │
│  4. Build RAG context                │
│  5. Send to LLM with system prompt   │
│  6. Parse response + suggested actions│
│  7. Return structured response       │
└──────────────────────────────────────┘
    │
    ▼
Structured Response:
  - Natural language analysis
  - Data tables / metrics
  - Actionable buttons (Buy/Sell/Add to Watchlist)
  - Confidence score
  - Source citations
```

**System Prompt Strategy:**
The AI is configured as a seasoned Indian market analyst with:
- Deep knowledge of NSE/BSE market microstructure
- Understanding of corporate actions and taxation
- Access to real-time data via function calling
- Conservative bias (never aggressively recommend, always show risk)

---

## Broker Integration

### Zerodha Kite Connect

```
Login Flow:
1. User clicks "Connect Broker" → Redirect to Kite login page
2. User logs in on Kite → Kite redirects back with request_token
3. Backend exchanges request_token for access_token
4. access_token stored (encrypted) for the session / day
5. All subsequent API calls use this token

API Capabilities:
├── Orders: place, modify, cancel
├── Portfolio: holdings, positions
├── Market: quotes, instruments, historical data
└── Streaming: WebSocket tick data
```

### Abstraction Layer

All brokers implement a common `BaseBroker` interface:
```python
class BaseBroker(ABC):
    async def authenticate(credentials) → bool
    async def place_order(symbol, side, qty, ...) → BrokerOrder
    async def cancel_order(order_id) → bool
    async def get_positions() → list[BrokerPosition]
    async def get_holdings() → list[BrokerPosition]
    async def get_order_history() → list[BrokerOrder]
    async def get_quote(symbol, exchange) → dict
```

This makes adding new brokers (Angel One, Upstox, Groww) a matter of implementing the interface.

---

## Security & Compliance

### Security Measures
- **JWT authentication** with short-lived tokens (30 min default)
- **bcrypt password hashing** with salt
- **CORS** restricted to frontend origin
- **Secrets in env vars** — never in code
- **Broker tokens encrypted** at rest
- **Rate limiting** on all endpoints
- **Input validation** via Pydantic (SQL injection / XSS prevention)
- **HTTPS mandatory** in production

### Regulatory Awareness
- AlphaForge Anton is a **tool**, not a financial advisor
- No guaranteed return claims
- User data privacy — minimal data collection, no selling
- Compliance with RBI's LRS guidelines for international investing features

---

## Data Flow: Real-Time Quotes

```
NSE/BSE Market
    │
    ▼ (WebSocket / polling)
Market Data Service
    │
    ├──→ Redis Cache (TTL: 1-5s)
    │
    ├──→ Redis Pub/Sub channel: "quotes:{symbol}"
    │
    └──→ API Response (REST)

Frontend
    │
    ├──→ REST /api/v1/market/quote/{symbol}  (initial load)
    │
    └──→ WebSocket subscription               (live updates)
         └── Receives pub/sub messages from Redis
```

---

## Development Workflow

### Local (Recommended for macOS Apple Silicon)

```bash
# 1. Setup infrastructure (one-time)
bash infra/setup-local.sh             # PostgreSQL + Redis via Homebrew

# 2. Install dependencies
cd backend && pdm install             # Python deps (uses uv resolver)
cd frontend && pnpm install           # Node deps

# 3. Run migrations
cd backend && pdm run migrate         # Apply schema

# 4. Start backend
cd backend && pdm run dev             # uvicorn --reload at :8000

# 5. Start frontend
cd frontend && pnpm dev               # Next.js at :3000

# Or start both at once:
just dev-local                        # Uses overmind/honcho + Procfile

# 6. Run tests
just test

# 7. Create new migration after model changes
just db-revision msg="add watchlist table"
```

### Container (OrbStack or Docker)

```bash
docker compose -f infra/docker-compose.yml up --build
```

### GitHub Codespaces

The `.devcontainer/devcontainer.json` sets up a full cloud environment with PostgreSQL, Redis, and all dependencies pre-installed.

### Code Quality
- **Backend**: `ruff` for linting + formatting, `mypy` for type checking, `pytest` for tests — all via `pdm run`
- **Frontend**: `eslint` + `next lint`, TypeScript strict mode — all via `pnpm`
- **Pre-commit hooks** (planned): lint + format on every commit

### Logging

Both backend and frontend use structured, file-based logging via **publishable logger packages** so you can check logs in the `logs/` directory.

**Packages:**
- `packages/logger-py/` — `alphaforge-logger` — Python rotating-file + console logger (zero dependencies)
- `packages/logger-node/` — `@alphaforge/logger` — pino-based structured logger (ESM + CJS, built with tsup)

**Backend** — wraps `alphaforge-logger` via `backend/app/core/logging.py`:
- Initialised at app startup in `backend/app/main.py` (lifespan)
- Get a scoped logger anywhere: `from app.core.logging import get_logger; logger = get_logger("routes.market")`
- File output: `backend/logs/alphaforge-anton.log` (10 MB per file, 5 backups)

**Frontend** — wraps `@alphaforge/logger` via `frontend/src/lib/logger.ts`:
- Get a scoped logger: `import { getLogger } from "@/lib/logger"; const log = getLogger("MyComponent")`
- Server-side logs to `frontend/logs/alphaforge-anton-frontend.log` + console (pretty in dev)
- Client-side errors can be forwarded via `POST /api/log` (warn/error/fatal only)

**Environment variables** (both stacks):
| Variable | Backend Default | Frontend Default | Description |
|----------|----------------|-----------------|-------------|
| `LOG_LEVEL` | `INFO` | `info` | Minimum log level |
| `LOG_DIR` | `logs` | `logs` | Directory for log files |
| `LOG_FILE` | `alphaforge-anton.log` | `alphaforge-anton-frontend.log` | Log filename |
| `LOG_MAX_BYTES` | `10485760` | — | Max file size before rotation (backend only) |
| `LOG_BACKUP_COUNT` | `5` | — | Rotated file copies to keep (backend only) |

---

## Deployment Architecture (Production)

```
                    Cloudflare (CDN + DDoS protection)
                              │
                              ▼
                    ┌──────────────────┐
                    │   Load Balancer  │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ Backend  │  │ Backend  │  │ Backend  │
        │ (Gunicorn│  │ (replica)│  │ (replica)│
        └──────────┘  └──────────┘  └──────────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │PostgreSQL│  │  Redis   │  │  Celery  │
        │(Primary) │  │ Cluster  │  │ Workers  │
        └──────────┘  └──────────┘  └──────────┘
```

Target deployment: **AWS / Railway / Fly.io** depending on scale requirements.

## Live prices — design plan
<a id="live-prices-plan"></a>
_`live-prices-plan` · general_

# Live prices — design plan

**Status:** _Plan only — no implementation yet._
**Owner:** picks an approach below, then writes the focused PR.

## What's live today

| Surface | Source | Refresh |
|---|---|---|
| Compact bar / Portfolio totals | `HoldingsAggregator.totals()` over broker `cached` lists | Per `_STALE_SECONDS` (3600s) when `/portfolio/holdings` is hit |
| Today's P&L | Sum of `current_value × day_change_pct/100` per holding | Same — only as fresh as the last broker sync |
| Wallet `last_price` / `pnl` | Broker source `fetch()` (Kite, Groww, AngelOne, IndMoney, TickerTape) | Sync-triggered, ~hourly |
| Terminal ticker / watchlist | `dashboard_ticker_items` / `dashboard_watchlist_items` DB rows; `price`/`change`/`tone` are the **last snapshot written** | Never updates automatically today |
| USD/INR rate | `fx.get_inr_per_usd()` → open.er-api.com | 1h CSV cache |

`day_change_pct` is wired into `Holding` and read from Zerodha Kite (`day_change_percentage`). Other brokers fall through to `0.0` until we either parse it from their existing payloads or fetch quotes ourselves — addressed below.

## Goal

A continuous stream of last-traded prices feeding three surfaces:

1. **Compact bar** — net worth + today's P&L tick as the market ticks (5–15s perceived freshness).
2. **Terminal ticker strip** — indices/commodities/large caps roll with live prices.
3. **Watchlist card** — per-symbol price + day-change line refresh in place.

Constraints we hold:
- Single-user app — no fan-out/multiplexing pressure.
- Self-hosted — no managed pub/sub. SQLite/Postgres + a Python process.
- Market data licensing — only sources we already have a session for (Kite via CDP, IndMoney US via CDP) or free quote APIs.
- Off-hours behaviour — must degrade gracefully when markets are closed.

## Option A — 15s server polling + frontend refetch

Cheapest to ship. Add a `QuoteService` that, every 15s during market hours, fetches LTP for all "subscribed" symbols (= union of holdings + ticker + watchlist) via Kite quote API (NSE/BSE) and a USD quote source (e.g. yfinance/AlphaVantage) for US tickers. Writes back to a `live_quotes` table keyed by `(symbol, exchange)`. Aggregator + dashboard read from this table when present.

- **Pros:** stays inside the FastAPI process, no new infra, easy to reason about, works off-hours (skip the loop), bounded quote-API calls per minute.
- **Cons:** 15s latency floor, batch quote APIs have request-size caps (~500 symbols/call), still polls the broker — wastes their rate limit, no per-tick UX.
- **Schema:** one new table `live_quotes(symbol, exchange, last_price, day_change_pct, as_of)` + an index on `(symbol, exchange)`.
- **Frontend:** existing TanStack `refetchInterval` drops from 30s → 5s on `/dashboard/stats|ticker|watchlist`.

## Option B — Server polling + SSE push to frontend

Same backend loop as Option A, but instead of frontend polling, expose `GET /dashboard/stream` as a Server-Sent Events endpoint. On each backend tick, broadcast a delta `{symbol, last_price, day_change_pct}` to all subscribed clients.

- **Pros:** smooth UX (sub-second visual updates after backend tick); no wasted HTTP overhead on the frontend.
- **Cons:** adds an in-process broadcaster; need to handle reconnects + auth on the long-lived stream; sse is one-way (fine here).
- **Effort:** ~1 extra day on top of Option A.

## Option C — Kite Ticker WebSocket for NSE + Option A for the rest

For NSE/BSE symbols, use Zerodha's `KiteTicker` WebSocket — it streams tick-by-tick once subscribed. For US symbols (NVDA, etc.) and indices we can't reach via Kite (some commodities), fall back to the 15s polling loop. Funnel both into the same `live_quotes` table; broadcast over SSE to the frontend.

- **Pros:** true real-time on the bulk of holdings (Indian equities); single canonical store; minimum API hits.
- **Cons:** requires a valid Kite session at all times (Kite tokens rotate daily — we'd need a re-auth flow); WebSocket lifecycle adds operational complexity; ticker reconnect logic must be solid; only works for instruments Kite exposes.
- **Effort:** ~3–5 days.

## Recommended path

Stage it:

1. **Phase 1 (Option A, 2 days):** Build `QuoteService` + `live_quotes` table + Kite quote-API polling on a 15s loop during market hours. Wire `aggregator.totals()` to prefer `live_quotes.last_price` over `Holding.last_price` when present. Drop frontend `refetchInterval` to 5s. Acceptance: net worth and today's P&L move during market hours without manual sync; off-hours show last close.
2. **Phase 2 (Option B add-on, 1 day):** Convert the frontend from polling to SSE. Keep the polling endpoints as a fallback for clients that can't hold a stream open.
3. **Phase 3 (Option C, only if Phase 2 latency feels slow):** Add Kite Ticker for NSE symbols. Keep the polling loop alive as the fallback path.

## Open questions to resolve before Phase 1

- Where do US/crypto quotes come from? IndMoney's API isn't documented for quote streaming — likely need yfinance/AlphaVantage/Coingecko. Pick one source per asset class.
- How do we model "market hours"? Hard-code NSE 09:15–15:30 IST initially; revisit when we have non-NSE symbols.
- Where does Kite's token live? It's currently in the IndMoney/Zerodha CDP-session pattern — quote API needs the same access token. Reuse `acquire_enctoken` or move to a longer-lived API key.
- Symbol-key normalisation: ticker item "NIFTY 50" vs Kite `NSE:NIFTY 50` vs holding `RELIANCE`. Need a `(symbol, exchange)` resolver before subscribing.

## Files this will touch (Phase 1 sketch)

- `backend/app/modules/quotes/quote_service.py` (new) — the 15s loop.
- `backend/app/modules/quotes/quote_repo.py` (new) — `live_quotes` upsert/read.
- `backend/alembic/versions/*_live_quotes.py` (new) — schema.
- `backend/app/modules/brokers/aggregator.py` — prefer live_quotes when fresh.
- `backend/app/modules/dashboard/dashboard_repo.py` — refresh ticker / watchlist `price`/`change` rows from live_quotes on each list call.
- `frontend/src/modules/dashboard/dashboard.query.ts` — drop `refetchInterval` from 30s → 5s.

## Plan: Add LLM + Brokerage Sync to Boot Screen
<a id="plan-boot-llm-brokerage"></a>
_`plan-boot-llm-brokerage` · general_

# Plan: Add LLM + Brokerage Sync to Boot Screen

## Goal

1. **LLM gateway row** — show which AI providers are live on the boot splash.
2. **Auto-sync brokers on boot** — for any linked broker with no cached data (`_cached` is `None`), trigger `sync()` during the boot sequence and block navigation until it completes. Brokers that are `UNCONFIGURED` are skipped silently.
3. **Richer broker detail** — show holding count and sync status in the boot row once sync finishes.
4. **Verbiage polish** — footer and headline copy updates.

---

## Key facts about broker state

- `SourceStatus.UNCONFIGURED` — no credentials, never synced. Skip silently on boot.
- `SourceStatus.READY` — credentials present, `_cached` may or may not be populated (in-memory, cleared on restart). **Always needs a sync on fresh boot.**
- `SourceStatus.SYNCING` — already in flight, wait for it.
- `SourceStatus.ERROR` — last sync failed. Attempt one retry on boot; surface error if it fails again.
- `_last_synced_at` is `None` if never synced this process lifetime — the refetch loop skips these, so boot must do the first sync.
- Sync endpoint already exists: `POST /sources/{slug}/sync` (calls `src.sync()` internally).

**Implication:** on every cold boot, any broker that is not `UNCONFIGURED` needs `sync()` called. The boot screen should fire syncs concurrently (one per linked broker), animate each row through `syncing… → N holdings` or `sync failed`, and only call `onDone` when all syncs have settled.

---

## Scope

| Layer | Files touched |
|-------|--------------|
| Backend probes | `backend/app/modules/health/boot_probes.py` |
| Backend route | `backend/app/modules/health/health_routes.py` |
| Backend new endpoint | `backend/app/modules/health/health_routes.py` — `POST /health/boot/sync` |
| Frontend API | `frontend/src/modules/dashboard/boot.api.ts` |
| Frontend types | `frontend/src/modules/dashboard/boot.types.ts` |
| Frontend gate | `frontend/src/modules/dashboard/BootGate.tsx` |
| Frontend splash | `frontend/src/modules/dashboard/BootScreen.tsx` |
| Docs | `docs/architecture.md` |

---

## Step 1 — Backend: `probe_llm()` in `boot_probes.py`

Add a new async probe using `LLMGateway.health()`.

**Logic:**
- `await create_gateway().health()` → `dict[str, ProviderHealth]`
- Count available providers; pick primary from: `gemini → cerebras → groq → openrouter`
- Never raises — swallows exceptions like the other probes.

| Condition | `status` | `detail` |
|-----------|----------|----------|
| ≥1 available | `ok` | `"N providers · via <primary>"` |
| 0 available | `error` | `"no providers available"` |
| Exception | `error` | error message truncated to 48 chars |

**Label:** `"AI Gateway · LLM routing"`

---

## Step 2 — Backend: Update `probe_brokers()` in `boot_probes.py`

Enrich the `detail` field to include holding count when data is already cached:

| Status | `detail` (before) | `detail` (after) |
|--------|-------------------|------------------|
| `READY` with cache | `"linked"` | `"N holdings"` |
| `READY` no cache | `"linked"` | `"linked · not synced"` |
| `SYNCING` | `"syncing…"` | `"syncing…"` |
| `UNCONFIGURED` | `"not linked"` | `"not linked"` |
| `ERROR` | `"error"` | `"error"` |

---

## Step 3 — Backend: `POST /health/boot/sync` in `health_routes.py`

New endpoint that fires `sync()` on all non-`UNCONFIGURED` sources concurrently and returns a per-source result. Used by `BootGate` immediately after `GET /health/boot`.

```
POST /health/boot/sync
→ { results: { [slug]: { ok: bool, holdings_count: int, detail: str } } }
```

- Runs all syncs concurrently via `asyncio.gather`.
- Per-source: catches exceptions, returns `ok: false` + error detail rather than raising.
- Does not re-authenticate — if credentials are missing the source is `UNCONFIGURED` and already excluded.
- No auth dependency (same as `GET /health/boot` — boot happens before login gate).

---

## Step 4 — Frontend: `boot.types.ts`

Add `SyncResult` and `BootSyncReport` types:

```ts
export interface SyncResult {
  ok: boolean;
  holdings_count: number;
  detail: string;
}

export interface BootSyncReport {
  results: Record<string, SyncResult>;
}
```

---

## Step 5 — Frontend: `boot.api.ts`

Add `triggerBootSync()`:

```ts
export async function triggerBootSync(): Promise<BootSyncReport> {
  const res = await api.post<BootSyncReport>("/health/boot/sync");
  return res.data;
}
```

---

## Step 6 — Frontend: `BootGate.tsx` — orchestrate sync

**New flow:**

1. `GET /health/boot` → populate step list (as today).
2. `setPhase("boot")` → splash appears, animates through static rows.
3. Concurrently, fire `POST /health/boot/sync` — this is the real work.
4. When sync resolves, update the broker step `doneStatus` values with live results (`"N holdings"` or `"sync failed"`).
5. Only then allow `onDone` to fire (pass a `syncReady` flag to `BootScreen`).

**Key constraint:** the boot animation should not wait for sync before starting — it begins immediately. But `onDone` (which transitions to the app) is held until sync settles. If sync takes longer than the animation, the final row stays in a `syncing…` state until done.

---

## Step 7 — Frontend: `BootScreen.tsx`

### 7a. Static fallback `BOOT_STEPS`

Add LLM entry after `database`, before broker rows:

```ts
{ key: "llm", label: "AI Gateway · LLM routing", status: "warn", doneStatus: "no key" }
```

### 7b. `NOW_STATUS` map

```ts
llm: "connecting to AI providers…",
```

### 7c. `HEADLINES` map

```ts
llm:  "Wiring up your AI analyst…",
done: "Welcome back, Arpit.",   // already exists, no change
```

Add broker-sync headlines for linked brokers (keyed by slug):
```ts
zerodha:   "Pulling your Zerodha positions…",   // already exists
groww:     "Loading your Groww book…",           // already exists
```

### 7d. Accept `syncReady` prop

```ts
export interface BootScreenProps {
  steps?: BootStep[];
  onDone: () => void;
  exiting?: boolean;
  syncReady?: boolean;  // ← new: gate the final onDone call
}
```

The `useEffect` animation already calls `onDoneRef.current()` after the last step. Change it to: only call `onDone` if both the animation has finished **and** `syncReady === true`. If animation finishes first, wait for `syncReady` to flip; if sync finishes first, `onDone` fires as soon as animation completes.

### 7e. Footer verbiage

| Before | After |
|--------|-------|
| `N of M services online` | `N of M systems ready` |

---

## Verbiage Summary

| Location | Before | After |
|----------|--------|-------|
| Boot footer | `N of M services online` | `N of M systems ready` |
| LLM row label | _(new)_ | `AI Gateway · LLM routing` |
| LLM now-status | _(new)_ | `connecting to AI providers…` |
| LLM headline | _(new)_ | `Wiring up your AI analyst…` |
| LLM done-status (fallback) | _(new)_ | `no key` |
| LLM done-status (live, ok) | _(new)_ | `N providers · via <primary>` |
| Broker done-status (READY + cache) | `linked` | `N holdings` |
| Broker done-status (READY, just synced) | `linked` | `N holdings` |
| Broker done-status (sync failed) | `error` | `sync failed` |

---

## What does NOT change

- `BootGate` session key (`af-booted`) logic — boot still only runs once per browser session.
- Auth/login bypass — `skip` path for `/login` unchanged.
- `BootStatus` enum — `ok / warn / error / skip` covers all new states.
- Broker rows for `UNCONFIGURED` sources — still show `"not linked"` with `warn`, no sync attempted.

## Portfolio plan — template (git-safe instance shape)
<a id="portfolio-plan-template"></a>
_`portfolio-plan-template` · portfolio_

# Portfolio plan — template (git-safe instance shape)

**What this is:** the shape every committed investment plan follows. A plan is
**strategy only** — target percentages, drift bands, rebalance rules, named goals,
horizon. It carries **zero personal figures** (no ₹ amounts, no quantities, no account
IDs, no holding symbols), so it is safe in a public repo. Live actuals live in the data
plane; see [[secure-holdings-plan]].

Orff reads `targets` / `bands` machine-side via `plan_loader.py`; the prose explains the
*why* so the plan is referenceable later (`fux why <plan-id>`).

## Targets (machine-read)

```yaml
plan_id: core-allocation        # one per strategy; this is the example
horizon: long-term              # short | medium | long-term
targets:                        # must sum to 100
  equity: 60
  mutual_fund: 15
  bond: 15
  gold: 5
  crypto: 3
  cash: 2
bands:                          # drift tolerance, in percentage points
  default: 5
  crypto: 1.5                   # tighter band on the volatile sleeve
rules:
  - trim any class > target + its band
  - top up any class < target − its band
  - prefer adding new capital over selling when drift is one-sided
```

## Goals (prose — the *why*)

- **Equity 60%** — primary growth engine; horizon is long enough to ride drawdowns.
- **Bonds + cash 17%** — dry powder + a floor that funds rebalancing without forced equity sales.
- **Crypto 3%, ±1.5pt band** — deliberately small and tightly banded; it drifts fast.

## How drift is computed (no figures leave the machine)

`get_drift(core-allocation)` →
`aggregator.rebalance(targets)` → per class `RebalanceDrift(target_pct, actual_pct,
drift_pct)`. Orff reports **points of drift and direction only** by default
(`disclose-aggregate-only`). Example narration — *"equity is +4pts hot, crypto is
−1pt; trim equity, add to bonds"* — no ₹, no symbols.

## Saving a real plan

1. Copy this entry to `.fux/rules/<plan-id>.plan.md`, edit `targets` / `bands` / goals.
2. `fux build` — it joins the graph and becomes `fux why <plan-id>`.
3. The git-safety guard probe must pass before commit (greps for ₹ / account IDs / symbols).

## Related

[[secure-holdings-plan]] · [[holdings-aggregator]] · [[portfolio-valuation]] ·
[[holdings-sum-equals-total]]

## Secure holdings access for Orff + the plan→drift→advise workflow
<a id="secure-holdings-plan"></a>
_`secure-holdings-plan` · security_

# Secure holdings access for Orff + the plan→drift→advise workflow

**Status:** _Design plan — drives the focused PRs below._
**Why this exists:** Orff routes to **free external LLM providers** (Groq, Mistral,
Gemini, OpenRouter, HuggingFace — see `concierge/.../registry/routing.json`). Today
`concierge_service.stream_chat` injects Fux grounding but **no holdings**, so nothing
has leaked yet. The moment we naively "inject holdings," symbols / quantities / ₹
amounts land in a third party's request logs. That is the primary threat — git
(public repo) is the second, because plan docs are committed.

## One principle — two planes that never cross

| Plane | Contains | Lives in | Leaves the machine? |
|---|---|---|---|
| **Data plane** (secret) | live holdings: symbols, qty, ₹ values, account IDs | broker `cached` (in-process) + gitignored `portfolio-dumps/` | Never in raw form |
| **Plan plane** (safe) | target %, drift bands, rebalance rules, named goals | committed `.fux/` (this substrate) | Yes — by design, it's strategy, not data |

**Drift** = committed targets (plan plane) × live actuals (data plane), expressed as
**percentages / bands only** → the drift report is safe to show and even to commit.

## Threat model (ranked)

1. **Third-party LLM leakage** — raw holdings in a prompt sent to a free provider.
2. **Public-git leakage** — ₹ amounts / account IDs / symbol lists in committed plan or drift docs.
3. **Browser/SSE leakage** — figures or secrets streamed to the client (errors already pass through `_redact`).
4. **At-rest** — CSV dumps, `concierge_turns` rows.

## Requirement A — most secure holdings access (4 layers, strongest first)

1. **Tools, not prompt-stuffing.** Expose server-side functions the model calls —
   `get_totals()`, `get_allocation()`, `get_drift(plan)` — running locally against
   `HoldingsAggregator`. They return only the answer asked for; nothing raw sits in
   the context window unless a tool deliberately puts it there.
2. **Least-disclosure by default** (`disclose-aggregate-only`). Tools return buckets /
   percentages (equity 58%, drift −2pts), never symbol rows or absolute ₹. Per-symbol
   or ₹ detail requires an explicit user ask + confirmation, gated through one
   redaction chokepoint (extend `_redact` → a `disclose()` layer that downgrades ₹→%
   unless escalated, and logs what was disclosed).
3. **Private-intent routing** (`portfolio-private-route`). A new `portfolio_private`
   intent pins holdings-bearing queries to a **local / trusted provider only**
   (`claude-sdk` confirmed, or a local model) — never the free third-party pool. A hard
   provider floor in the registry; `portfolio_overview` / `investment_plan` intents
   already exist as precedent.
4. **No persistence of raw figures.** Drift history + any ₹-level dumps go to gitignored
   `portfolio-dumps/`; turn logs store the redacted form only.

## Requirement B — generate → follow → show drift → advise → save

- **Plan = committed, git-safe spec.** A Fux narrative entry (see
  [[portfolio-plan-template]]) holding only: target allocation %, drift thresholds /
  bands, rebalance rules, named goals, horizon. **Zero personal figures.** This is what
  is safe in a public repo and makes plans reproducible + referenceable (`fux why`).
- **Generate.** Orff drafts the spec from a conversation → user reviews → it's
  committed. The plan overrides today's hardcoded `DEFAULT_TARGETS`.
- **Follow + show drift.** `get_drift(plan)` joins committed targets × live holdings →
  existing `RebalanceDrift(target_pct, actual_pct, drift_pct)`. Output is %-only → safe.
- **Tell me what to do.** `RebalanceSuggestion` actions as percentage moves
  ("trim equity ~2pts, add bonds ~3pts").
- **Save for later.** Plan spec → git (safe). Drift *history* → gitignored dump dir, or
  a redacted %-only entry if it should live in git.

## The git-safety guard (makes "public repo" real)

A probe + `just` recipe (and ideally a pre-commit / CI step) greps every committed plan
/ drift doc for ₹-amounts, account IDs, and known holding symbols, and **fails** if any
are found. This is the enforcement behind the two-plane rule — without it, "git-safe"
is a convention, not a guarantee.

## Build order

1. Plan schema + one example plan entry ([[portfolio-plan-template]]) + the git-safety guard probe.
2. `portfolio_private` intent + provider floor in the registry.
3. Server-side holdings tools + `disclose()` redaction chokepoint.
4. Wire `get_drift(plan)` to the existing `aggregator.rebalance()` engine.
5. Probe + `just` recipe (per `probe-cdp-not-playwright` — a feature isn't verified without one).

## Files this will touch (sketch)

- `concierge/.../registry/routing.json` — add `portfolio_private` intent + provider floor.
- `backend/app/modules/concierge/concierge_service.py` — `disclose()` chokepoint; tool wiring.
- `backend/app/modules/concierge/holdings_tools.py` (new) — `get_totals/get_allocation/get_drift`.
- `backend/app/modules/brokers/aggregator.py` — `rebalance()` accepts plan targets, not just `DEFAULT_TARGETS`.
- `backend/app/modules/brokers/plan_loader.py` (new) — parse targets/bands from the committed Fux plan entry.
- `probes/holdings_disclosure_probe.py` (new) + `just` recipe — leak guard + disclosure assertions.

## Open questions before build

- Which concrete provider is the "local / trusted" floor — `claude-sdk` confirmed only, or a local model?
- Plan targets: keep them in the Fux entry's frontmatter (machine-read) or a fenced YAML block in the body?
- Drift history: gitignored dump dir, or committed %-only? (Default: gitignored.)

## Related

[[portfolio-plan-template]] · [[holdings-aggregator]] · [[concierge-registry-single-source]] ·
[[vault-only-credentials]] · [[no-secrets-in-vcs]] · [[live-prices-plan]]

## What AlphaForge Anton Is
<a id="what"></a>
_`what` · general_

# What AlphaForge Anton Is

## One-liner

**A personal AI-powered portfolio management & investment terminal for Indian markets** — combining market data, analysis, and trade execution in a single self-hosted platform.

---

## Core Features

### 1. Real-Time Market Dashboard
- **Live market indices** — NIFTY 50, SENSEX, BANK NIFTY, sector indices
- **Stock quotes** — Real-time price, volume, bid/ask from NSE & BSE
- **Customisable watchlists** — Track your favourite stocks across multiple lists
- **Market breadth** — Advance/decline, 52-week highs/lows, volume leaders

### 2. Professional Charting
- **Candlestick charts** with multiple timeframes (1m → monthly)
- **50+ technical indicators** — RSI, MACD, Bollinger Bands, Supertrend, VWAP, etc.
- **Drawing tools** — Trendlines, Fibonacci, support/resistance zones
- **Multi-chart layout** — Compare stocks side-by-side
- Powered by **TradingView Lightweight Charts**

### 3. AI-Powered Analysis Engine
- **Conversational AI** — Ask questions in natural language
  - "Is INFY overvalued?"
  - "Show me stocks with RSI < 30 and PE < 15"
  - "Compare TCS vs INFY for long-term investment"
- **Stock analysis reports** — AI-generated comprehensive reports combining:
  - Technical analysis (indicators, patterns, chart analysis)
  - Fundamental analysis (financials, ratios, peer comparison)
  - News sentiment (NLP on recent articles)
  - Institutional activity (FII/DII data, bulk/block deals)
- **AI screener** — Find stocks matching strategies:
  - Momentum, Value, Growth, Dividend, Breakout
  - Custom criteria in natural language
- **Portfolio advisor** — AI reviews your portfolio and suggests rebalancing
- **Risk analysis** — Portfolio risk metrics, correlation analysis, max drawdown scenarios

### 4. Trade Execution
- **Connected broker accounts** — Link Zerodha, Angel One, Upstox
- **One-click trading** — Place orders directly from analysis/chat
- **Order types** — Market, Limit, Stop-Loss, Stop-Loss Market
- **Product types** — CNC (delivery), MIS (intraday), NRML (F&O)
- **Order book** — View pending, executed, cancelled orders
- **Position tracking** — Real-time P&L for open positions

### 5. Portfolio Management
- **Unified portfolio view** — All holdings across brokers
- **Performance tracking** — Daily, weekly, monthly, yearly returns
- **Sector allocation** — Visual breakdown of exposure
- **Dividend tracker** — Track dividend income
- **Tax implications** — STCG/LTCG computations for tax planning

### 6. News & Sentiment
- **Aggregated news feed** — From MoneyControl, Economic Times, LiveMint, etc.
- **AI-summarised headlines** — Get the gist without reading 20 articles
- **Per-stock sentiment score** — NLP-derived sentiment from news & social media
- **Alerts** — Get notified on breaking news for your watchlist stocks

---

## Scope & Boundaries

### In Scope (Phase 1 — India)
| Feature | Status |
|---------|--------|
| NSE & BSE equities | ✅ Planned |
| NIFTY & SENSEX indices | ✅ Planned |
| F&O (Futures & Options) | ✅ Planned |
| Mutual Funds (NAV, SIP tracking) | ✅ Planned |
| Zerodha Kite integration | ✅ Planned |
| Angel One integration | 🔜 Phase 1.1 |
| AI chat & analysis | ✅ Planned |
| Technical & fundamental analysis | ✅ Planned |
| News sentiment | ✅ Planned |

### In Scope (Phase 2 — Expand)
| Feature | Status |
|---------|--------|
| Commodities (MCX) | 🔜 Phase 2 |
| Currency pairs (USD/INR, etc.) | 🔜 Phase 2 |
| Crypto (via Indian exchanges) | 🔜 Phase 2 |
| Upstox, Groww broker integration | 🔜 Phase 2 |
| Options chain analyzer | 🔜 Phase 2 |
| Backtesting engine | 🔜 Phase 2 |
| Paper trading | 🔜 Phase 2 |

### In Scope (Phase 3 — Global)
| Feature | Status |
|---------|--------|
| US markets (NYSE, NASDAQ) | 🔜 Phase 3 |
| LRS investing from India | 🔜 Phase 3 |
| Multi-currency portfolio | 🔜 Phase 3 |
| Global ETFs | 🔜 Phase 3 |
| Interactive Brokers integration | 🔜 Phase 3 |

### Out of Scope (for now)
- Fully automated trading bots (AlphaForge Anton assists, user decides)
- Financial advisory services
- Proprietary brokerage / order routing
- Mobile app (web-first; responsive PWA later)

---

## Roadmap

```
Q2 2026  ──────────────────────────────────────────
  ✦ Base platform setup (backend + frontend + Docker)
  ✦ Health check, auth, core API skeleton
  ✦ Market data integration (NSE quotes & indices)
  ✦ Basic charting with Lightweight Charts
  ✦ AI chat MVP (OpenAI + market context)

Q3 2026  ──────────────────────────────────────────
  ✦ Zerodha Kite broker integration (auth, orders, positions)
  ✦ Portfolio dashboard with real holdings
  ✦ AI stock analysis (technical + fundamental)
  ✦ News aggregation & sentiment analysis
  ✦ Watchlist with real-time prices (WebSocket)

Q4 2026  ──────────────────────────────────────────
  ✦ F&O support (options chain, Greeks, strategy builder)
  ✦ AI screener (momentum, value, growth strategies)
  ✦ Angel One broker integration
  ✦ Alerts & notifications
  ✦ Paper trading mode

H1 2027  ──────────────────────────────────────────
  ✦ Backtesting engine
  ✦ Mutual fund tracking & SIP analysis
  ✦ Commodities (MCX)
  ✦ Crypto (Indian exchanges)
  ✦ Mobile-responsive PWA

H2 2027  ──────────────────────────────────────────
  ✦ US markets integration
  ✦ LRS investing support
  ✦ Multi-currency portfolio
  ✦ Self-hosted LLM option (Llama, Mistral)
  ✦ Community plugins / extensions
```

---

## User Flows

### Primary Flow: AI-Assisted Stock Analysis → Trade

```
User opens AlphaForge Anton
  → Sees dashboard with market overview
  → Types "Analyze TCS" in AI chat
  → AI returns comprehensive analysis with recommendation
  → User clicks [Place Buy Order]
  → Order form pre-filled (symbol, suggested price)
  → User confirms → order placed via Zerodha
  → Position appears in portfolio view
  → AI monitors and alerts on significant price moves
```

### Secondary Flow: Screener → Discovery → Analysis

```
User clicks AI Screener
  → Selects "Momentum" strategy (or types custom criteria)
  → AI returns ranked list of stocks matching criteria
  → User clicks a stock → detailed analysis panel
  → Adds to watchlist or places trade
```

## Why AlphaForge Anton Exists
<a id="why"></a>
_`why` · general_

# Why AlphaForge Anton Exists

## The Problem

As an Indian investor, managing a personal portfolio is **fragmented and frustrating**:

### 1. Institutional tools are inaccessible
- Bloomberg Terminal costs **₹15-20 lakh/year** — designed for institutions, not individuals
- Refinitiv Eikon is similarly priced and enterprise-focused
- There's no affordable way to get institutional-grade analytics for personal investing

### 2. Existing Indian platforms are limited
- **Zerodha Kite** — excellent for execution, but minimal analysis tools
- **Groww** — good for beginners, but no depth for serious analysis
- **TradingView** — great charts, but no trade execution and no India-specific intelligence
- **Screener.in** — good fundamentals, but no real-time data or AI
- No single platform combines **analysis + execution + AI guidance** for personal use

### 3. AI hasn't reached personal investing yet
- ChatGPT knows finance but has **no real-time market data**
- Existing "AI trading" tools are mostly gimmicks — backtested signals, not true intelligence
- No tool combines **conversational AI + live Indian market data + trade execution** for personal portfolio management

### 4. Cross-border investing from India is painful
- LRS (Liberalised Remittance Scheme) investing is clunky
- No unified personal tool to manage Indian + international portfolios
- Regulatory reporting is manual and error-prone

---

## The Vision

**AlphaForge Anton is a personal AI-powered investment terminal for managing your own portfolio in Indian markets.**

Imagine a tool where you can:

```
You: "Analyze RELIANCE — should I buy at current levels?"

AlphaForge Anton AI: Based on my analysis:

📊 Technical: RSI at 42 (neutral), MACD bearish crossover 2 days ago,
   trading below 50-DMA. Support at ₹2,380, resistance at ₹2,520.

📈 Fundamental: PE 26.4x (sector avg 22x), debt-to-equity 0.38,
   Jio + Retail segment growing 18% YoY. Recent ₹75K cr O2C demerger
   announcement is a catalyst.

📰 Sentiment: 72% positive across 47 recent articles. Institutional
   buying detected in last 3 sessions.

🎯 Recommendation: ACCUMULATE on dips near ₹2,400 with SL at ₹2,340.
   Confidence: 74%.

   [Place Buy Order] [Add to Watchlist] [Deep Dive Report]
```

Then with one click, place that trade through your connected Zerodha/Angel account.

---

## Who This Is For

AlphaForge Anton is built for **personal use** — a self-hosted investment terminal for managing your own portfolio. It's ideal if you are:

- An **active investor** tired of switching between 5+ tools for analysis
- Someone who wants **AI-powered analysis** on your own holdings
- An **F&O trader** who needs options chain analysis without paying for expensive platforms
- An **NRI** managing India + global portfolios from a single interface

---

## Why Now?

1. **AI maturity** — GPT-4o, Claude, and open models are genuinely capable of financial reasoning
2. **API ecosystem** — Zerodha, Angel, Upstox all have mature broker APIs
3. **Cost** — Cloud infrastructure costs have dropped; a Bloomberg-quality tool can be self-hosted for nearly nothing

---

## Competitive Positioning

```
                    Depth of Analysis
                         ▲
                         │
          Bloomberg ●    │    ● AlphaForge Anton (target)
          Refinitiv ●    │
                         │
                         │         ● TradingView
                         │
         Screener.in ●   │
                         │    ● Zerodha Kite
                    Groww ●
                         │
                         └──────────────────────► AI Intelligence
                                                   & Ease of Use
```

AlphaForge Anton aims to sit in the **top-right quadrant** — deep analysis capabilities with AI-first ease of use, at a price point accessible to retail investors.

---

## Principles

1. **AI-first, not AI-added** — AI isn't a feature; it's the core interaction model
2. **India-first, global-ready** — Built for NSE/BSE, architected for international expansion
3. **Open source** — Community-driven, transparent, trustworthy
4. **Privacy-conscious** — Your portfolio data stays yours; AI analysis runs with minimal data sharing
5. **Speed** — Real-time data, sub-second responses, terminal-grade performance
