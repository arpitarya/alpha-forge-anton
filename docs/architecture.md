# AlphaForge — Architecture & Key Files

## Project

**AlphaForge** — Personal AI-powered portfolio management & investment terminal for Indian markets.
Built for personal use — not a SaaS product. Self-hosted, open-source, MIT licensed.

## Repository Structure

```
alpha-forge/
├── backend/          Python 3.14 + FastAPI + SQLAlchemy async
│   ├── app/core/     Config (pydantic-settings), DB engine, JWT/bcrypt, env_loader
│   ├── app/modules/  Feature modules — each owns its routes/service/models
│   │   ├── health/      /api/v1/* health endpoint
│   │   ├── auth/        routes + User ORM
│   │   ├── portfolio/   routes + Holding/Order/Watchlist ORM
│   │   ├── brokers/     pluggable BrokerSource adapters (Zerodha Kite/Coin, Groww, Angel One, Wint, Dezerv) + aggregator + registry. Used by portfolio routes. All CSV portfolio dumps share `dump_utils.py` — see broker-csv-dumps.md
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
│   └── solar-orb-ui/ Publishable UI component library (@alphaforge/solar-orb-ui)
│       ├── src/components/  Button, Input, Card, Badge, Icon, Text
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
│       └── auth/        auth.api.ts
├── infra/            Infrastructure configs (docker-compose for services, devcontainer)
├── repo-context-mcp/ Tool-agnostic MCP server — gives Claude/Copilot/Cursor/any MCP client semantic + structural context over this repo
│   └── src/alphaforge_repo_context/  server, indexer, chunker, embeddings, watcher, tools/
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
| UI library | @alphaforge/solar-orb-ui | Publishable package built with tsup (ESM + CJS + DTS) |
| Logging (Python) | alphaforge-logger | Rotating file + console, env-configurable |
| Logging (Node) | @alphaforge/logger | Pino-based, file + console, publishable tsup pkg |
| DB | PostgreSQL 16 | Async via asyncpg + SQLAlchemy |
| Cache | Redis 7 | Quotes cache, pub/sub, Celery broker |
| AI | OpenAI + LangChain | RAG with market data context |
| Repo Context MCP | alphaforge-repo-context-mcp | Local stdio MCP server; pgvector-backed semantic + structural repo context for Claude/Copilot/Cursor/any MCP client |
| Brokers | Abstract BrokerSource interface | Zerodha first, then Groww, Angel One, Upstox |
| Local infra | brew services (Postgres, Redis) | Containers optional via OrbStack |
| Browser MCP | Playwright MCP | Copilot can screenshot/inspect Chrome via `.vscode/settings.json` |
| CI infra | devcontainer.json | GitHub Codespaces compatible |

## Key Files

### Backend
- `backend/app/main.py` — FastAPI app factory
- `backend/app/core/config.py` — All environment variables
- `backend/app/core/logging.py` — Backend logging setup (wraps alphaforge-logger)
- `backend/app/modules/__init__.py` — registers every feature router under `/api/v1/*`
- `backend/app/modules/brokers/base.py` — `BrokerSource` ABC; implement for new brokers
- `backend/app/modules/brokers/registry.py` — broker source registry (slug → class)
- `backend/app/modules/brokers/dump_utils.py` — shared CSV-dump utilities (path, permissions, headers, P&L). See [broker-csv-dumps.md](broker-csv-dumps.md)
### Frontend
- `frontend/src/app/layout.tsx` — Root layout. Mounts `ThemeProvider` → `QueryProvider` → `AuthGuard` → `BootGate`, so the boot sequence runs once for the whole app and survives client-side route changes (`/`, `/portfolio`, `/preferences`)
- `frontend/src/app/page.tsx` — Terminal landing page (no longer wraps `BootGate` — that's now in the root layout)
- `frontend/src/app/portfolio/page.tsx` — Portfolio page. Slim `PortfolioCompactBar` on top (TOTAL · INVESTED · P&L · DAY inline + wallet pills + a "More/Less" expand toggle) so tree / ledger get the dominant vertical space; expanded state reveals the full `WalletStrip`. Source spotlight + filter bar + summary + body (treemap or ledger) on the left, rebalance rail on the right. Filter state (query, sector chip, gainers/losers, sort key + dir, view, expand) is owned here
- `frontend/src/modules/portfolio/PortfolioCompactBar.tsx` — Hi-Fi `.pf-summary-bar`: always-visible row with totals + wallet pills + expand caret. Mirrors the design's "Less / More" pattern so a single click reveals stat cards beneath
- `frontend/src/modules/portfolio/WalletStrip.tsx` + `WalletCard.tsx` — Per-broker wallet cards with brand-colored chip, free cash, holdings value, position count, weighted day move. Shown when the CompactBar is expanded; clicking filters the page to that source
- `frontend/src/modules/portfolio/SourceSpotlight.tsx` — Detail banner shown when a specific wallet is active (positions / holdings / P&L / cash + a `⟳ Refresh` that hits `POST /portfolio/wallets/{slug}/sync`)
- `frontend/src/modules/portfolio/FilterBar.tsx` (composes `SearchBox`, `SectorChips`, `PnLToggle`, `SortMenu`, `SegmentedControl` for the Tree/Ledger toggle) — Sector counts re-compute under search+pnl so the chips only show what's reachable; `/` and `⌘F` focus the search box
- `frontend/src/modules/portfolio/portfolio.filter.ts` — `FilterState`, `applyFilter`, `sectorCounts` helpers (pure functions, no React)
- `frontend/src/modules/portfolio/treemap.utils.ts` — Squarified-treemap layout in TS (mirrors `backend/app/modules/brokers/treemap_helper.py`); `Treemap.tsx` consumes filtered holdings + computes layout client-side so reflows are instant when filters change
- `frontend/src/app/preferences/page.tsx` — Preferences page. 8-section sidebar (Appearance · Display · Markets · Alpha AI · Notifications · Account · Privacy · About); reached via gear icon in the top-right
- `frontend/src/modules/preferences/` — Sidebar, section panels, and shared primitives:
  - `PrefRow.tsx` / `PrefGroup.tsx` — Row + group shells (label · description · control · tail layout)
  - `PrefControls.tsx` — Shared form atoms: `PrefSeg`, `PrefTog`, `PrefSlider`, `PrefSelect`, `PrefInput`
  - `usePrefStore.ts` — Local-state hook for non-wired draft preferences. Persists to `localStorage["af-prefs-draft-v1"]`, mirrors `chromeMode`/`showVoice` to `body.chrome-autohide` / `body.no-voice` classes
  - `AppearanceSection.tsx` — Theme tiles + accent swatches (wired to `useTheme()`)
  - `DisplaySection.tsx` — Chrome behavior (always-visible vs auto-hide), voice bar toggle, orb size/speed/HUD, ticker speed, reduce motion, number jitter
  - `MarketsSection.tsx` — Primary exchange, number format, currency, after-hours, refresh cadence
  - `AlphaSection.tsx` — Voice wake, reply style, confidence floor, auto-rebalance, screener visibility
  - `NotifSection.tsx` — Price/risk/signal toggles, threshold slider, email digest cadence + address
  - `AccountSection.tsx` — Profile (avatar, name, status), connected brokers list, hotkey reference
  - `PrivacySection.tsx` — Telemetry / crash / training toggles, retention select, danger actions
  - `AboutSection.tsx` — Build / backend / license info, reset action
- `frontend/src/app/globals.css` — Theme variables (Solar Terminal design tokens); `@source` directives extend Tailwind v4 content scanning into the workspace packages so arbitrary classes in `solar-orb-ui` resolve; restores the default `cursor: pointer` on `button` / `[role="button"]` that Tailwind v4's Preflight dropped
- `frontend/next.config.mjs` — Next.js config: CSP headers (allows `fonts.googleapis.com` + `fonts.gstatic.com` for Material Symbols icons), API rewrites
- `frontend/src/modules/dashboard/TerminalTopBar.tsx` — Slim global top bar per Hi-Fi spec (≈32px min-height, 4px×14px padding, 8px radius). SVG logo mark + ALPHA/FORGE wordmark; Terminal + Portfolio nav buttons; gear icon-button on the right routes to `/preferences`; no icon sidebar
- `frontend/src/modules/dashboard/TerminalVoice.tsx` — Slim global voice dock (≈36px min-height, 6px×14px padding). 28px `MicIndicator`, 8-bar `Waveform`, rotating prompt copy, small Deploy CTA. Rendered as `<AppShell footer>` so it appears on every page
- `packages/solar-orb-ui/src/components/TopBar.tsx` / `VoiceDock.tsx` — Reusable chrome containers carrying `data-af-top` / `data-af-voice` plus `.af-top` / `.af-voice` classes. Paired with `body.chrome-autohide` / `body.no-voice` rules in `frontend/src/app/globals.css` to enable Preferences → Display → Chrome behavior (collapses bars to an accent strip; hover/focus expands) and the voice-bar disable toggle
- `frontend/src/modules/dashboard/BootScreen.tsx` — Full-screen animated boot checklist. Renders one row per real backend system (gateway, Postgres, every broker source); each row's glyph and detail are driven by the `status: BootStatus` field (`ok` ✓ green / `warn` ! amber / `error` ✗ red). `BOOT_STEPS` is the static fallback used only when the live probe fails
- `frontend/src/modules/dashboard/boot.api.ts` + `boot.types.ts` — Frontend client and TS mirror of `BootReport` / `BootService` from the backend
- `frontend/src/modules/dashboard/BootGate.tsx` — Sits inside `AuthGuard` in the root layout. On first paint of a tab it hits `GET /api/v1/health/boot`, maps each service to a `BootStep`, then plays the boot screen exactly once per browser tab (gated by `sessionStorage['af-booted']`). Skips entirely on `/login` and survives navigations between Terminal / Portfolio / Preferences. If the probe call fails the static `BOOT_STEPS` fallback still produces a usable splash
- `backend/app/modules/health/health_routes.py` — `GET /health` (basic ping) + `GET /health/boot` (per-system readiness snapshot consumed by the terminal boot splash; aggregates database SELECT 1 + every broker source's `.status` from `SOURCES`)
- `backend/app/modules/health/boot_probes.py` — One probe function per system (`probe_backend`, `probe_database`, `probe_brokers`). Each probe swallows its own errors so a single failure can't take down the whole `/health/boot` response
- `backend/app/modules/health/boot_schemas.py` — `BootStatus` enum (`ok` / `warn` / `error` / `skip`), `BootService`, and `BootReport` Pydantic v2 schemas; the frontend mirror is `boot.types.ts`
- `frontend/src/modules/dashboard/TerminalRail.tsx` — Icon sidebar (unused; nav lives in the top bar per Hi-Fi design)
- `frontend/src/lib/api.ts` — Axios HTTP client (interceptors only; per-domain `*.api.ts` lives in each module)
- `frontend/src/lib/logger.ts` — Frontend logging setup (wraps @alphaforge/logger)
- `frontend/src/modules/<name>/<name>.api.ts` — Per-domain axios calls
- `frontend/src/modules/<name>/<name>.query.ts` — Per-domain React Query hooks

### Packages & Infra
- `packages/logger-py/src/alphaforge_logger/logger.py` — Python logger package core
- `packages/logger-node/src/logger.ts` — Node/TS logger package core
- `packages/solar-orb-ui/src/index.ts` — UI library barrel export (Button, Input, Card, Badge, Icon, Text)
- `packages/solar-orb-ui/src/styles/theme.css` — Tailwind v4 design tokens (CSS)
- `packages/solar-orb-ui/src/tokens/index.ts` — Design tokens (TypeScript)
- `packages/solar-orb-ui/src/tokens/tokens.json` — Design tokens (JSON, machine-readable)
- `packages/solar-orb-ui/tsup.config.ts` — Package build config
- `repo-context-mcp/src/alphaforge_repo_context/server.py` — MCP server entry (stdio); exposes `search_code`, `get_symbol`, `module_overview`, `recent_changes`, `read_file_range`
- `repo-context-mcp/src/alphaforge_repo_context/indexer.py` — Walk → chunk → embed → pgvector
- `repo-context-mcp/src/alphaforge_repo_context/chunker.py` — AST (Python), regex (TS/TSX), section (Markdown), sliding-window fallback
- `repo-context-mcp/src/alphaforge_repo_context/db.py` — `repo_chunks` ORM model + `init_schema()`
- `repo-context-mcp/README.md` — Wire-up snippets for Claude Code, VS Code/Copilot, Cursor, Cline, Zed, Windsurf

### Probes & Design
- `probes/ui_probe.py` — End-to-end Playwright probe (auth guard, login, dashboard, portfolio, session, logout). Writes PNGs to `screenshots/` at the repo root
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
- `.env.port` — All service ports in one file
- `.vscode/settings.json` — VS Code workspace settings (MCP server config for Playwright)
- `.env.example` / `backend/.env.example` / `frontend/.env.example` — Environment templates
