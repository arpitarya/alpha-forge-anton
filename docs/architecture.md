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
│   │   ├── market/      routes + market_data service
│   │   ├── portfolio/   routes + Holding/Order/Watchlist ORM
│   │   ├── brokers/     pluggable BrokerSource adapters (Zerodha Kite/Coin, Groww, Angel One, Wint, Dezerv) + aggregator + registry. Used by portfolio routes. All CSV portfolio dumps share `dump_utils.py` — see broker-csv-dumps.md
│   │   ├── memory/      EmbeddingService + MemoryService + ScreenerPickEmbedding/ConversationMemory ORM. Used by ai + screener
│   │   ├── ai/          routes + AIService (RAG, sentiment, screener Q&A)
│   │   ├── llm/         routes + LLMGateway thin wrapper
│   │   ├── screener/    routes + ScreenerService
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
│       ├── market/      market.api.ts + market.query.ts
│       ├── portfolio/   portfolio.{api,query,types}.ts + components (Ledger, Treemap, SourcesPanel, ...)
│       ├── ai/          ai.{api,query}.ts + AIChat
│       ├── trade/       trade.{api,query}.ts
│       ├── screener/    screener.{api,query,types,utils}.ts + ScreenerPanel
│       ├── llm/         llm.{api,query,types}.ts
│       ├── dashboard/   dashboard.{api,query,types}.ts + terminal-home components
│       └── auth/        auth.api.ts
├── infra/            Infrastructure configs (docker-compose for services, devcontainer)
├── llm-gateway/      Publishable Python package (alphaforge-llm-gateway)
│   ├── src/alphaforge_llm_gateway/  LLMGateway, providers, router, rate_limiter, cost_guard, CLI
│   └── notebooks/    Interactive Jupyter playground for provider comparison & benchmarks
├── repo-context-mcp/ Tool-agnostic MCP server — gives Claude/Copilot/Cursor/any MCP client semantic + structural context over this repo
│   └── src/alphaforge_repo_context/  server, indexer, chunker, embeddings, watcher, tools/
├── docs/             WHY.md, WHAT.md, HOW.md, GETTING_STARTED.md + canonical shared docs for AI agents
└── design/           Design system & Gemini Stitch tokens
```

## Tech Decisions

| Area | Choice | Notes |
|------|--------|-------|
| Python pkg mgr | uv (workspace) | Single `uv.lock` at repo root; members declared in `[tool.uv.workspace]`. One `.venv/` shared across backend, screener, llm-gateway, logger-py |
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
| LLM Gateway | alphaforge-llm-gateway | 5 free providers (Gemini, Groq, HuggingFace, OpenRouter, Ollama), smart routing, $0 cost wall |
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
- `backend/app/modules/screener/screener_service.py` — Screener picks storage/retrieval
- `backend/app/modules/screener/screener_routes.py` — Screener API endpoints
- `backend/app/modules/llm/llm_service.py` — LLM Gateway thin wrapper
- `backend/app/modules/llm/llm_routes.py` — LLM Gateway API endpoints
- `backend/app/modules/memory/memory_service.py` — `MemoryService` (RAG retrieval over picks + chats)
- `backend/app/modules/memory/embedding_service.py` — `EmbeddingService` (Gemini text-embedding-004)

### Frontend
- `frontend/src/app/page.tsx` — Terminal landing page; wrapped in `BootGate` (boot sequence plays on every fresh load, then auto-advances to terminal)
- `frontend/src/app/portfolio/page.tsx` — Portfolio page (treemap + ledger + rebalance rail; SourcesPanel removed from this layout)
- `frontend/src/app/globals.css` — Theme variables (Solar Terminal design tokens)
- `frontend/next.config.mjs` — Next.js config: CSP headers (allows `fonts.googleapis.com` + `fonts.gstatic.com` for Material Symbols icons), API rewrites
- `frontend/src/modules/dashboard/TerminalTopBar.tsx` — Top nav (SVG logo mark + ALPHA/FORGE wordmark; Terminal + Portfolio tabs; no icon sidebar)
- `frontend/src/modules/dashboard/BootScreen.tsx` — Full-screen animated boot checklist (7 services, progress bar, corner labels); transitions to terminal on complete
- `frontend/src/modules/dashboard/BootGate.tsx` — Client wrapper that shows BootScreen first, then unmounts it and renders children
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
- `llm-gateway/src/alphaforge_llm_gateway/__init__.py` — LLM Gateway barrel export
- `llm-gateway/src/alphaforge_llm_gateway/gateway.py` — Main LLMGateway class (from_env, complete, analyze_screener)
- `llm-gateway/src/alphaforge_llm_gateway/cli.py` — CLI: analyze-screener, explain-picks, chat, benchmark, providers
- `llm-gateway/notebooks/llm_gateway_playground.ipynb` — Interactive notebook for provider comparison
- `repo-context-mcp/src/alphaforge_repo_context/server.py` — MCP server entry (stdio); exposes `search_code`, `get_symbol`, `module_overview`, `recent_changes`, `read_file_range`
- `repo-context-mcp/src/alphaforge_repo_context/indexer.py` — Walk → chunk → embed → pgvector
- `repo-context-mcp/src/alphaforge_repo_context/chunker.py` — AST (Python), regex (TS/TSX), section (Markdown), sliding-window fallback
- `repo-context-mcp/src/alphaforge_repo_context/db.py` — `repo_chunks` ORM model + `init_schema()`
- `repo-context-mcp/README.md` — Wire-up snippets for Claude Code, VS Code/Copilot, Cursor, Cline, Zed, Windsurf

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
