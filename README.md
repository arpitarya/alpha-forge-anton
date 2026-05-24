# AlphaForge Anton

<p align="center">
  <img src="logo.png" alt="AlphaForge Anton Logo" width="400" />
</p>

**Personal AI-powered Portfolio Management and Investment Terminal for Indian Markets**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

AlphaForge Anton is an open-source, self-hosted investment terminal for Indian markets (NSE/BSE + global crypto). It combines a FastAPI backend, a Next.js terminal-style frontend, a multi-broker portfolio aggregator, and an AI chat surface (Alpha).

Built for personal use and research.

---

## What Is New

- **Zerodha Coin broker** added (mutual funds via Coin CSV dumps)
- **Binance broker** added (global crypto holdings)
- **IndMoney & Tickertape** brokers added (US stocks, mutual funds, watchlist)
- **News module** added (`/news` backend routes + frontend feed)
- **Alpha Chat** — streaming AI assistant (AlphaBar + ChatRail, JWT-gated, SSE)
- **Boot screen** — animated per-service readiness check on every tab open
- **Preferences** — full 8-section settings UI (Appearance, Display, Markets, Alpha AI, Notifications, Account, Privacy, About)
- **Vault-backed secrets** via `alpha-forge-bach` (AFBACH environment)
- **Env file refactor** — `.env`, `.env.port`, `.env.cred.local`, `.env.frontend.local`

---

## Monorepo Overview

| Module | Path | Purpose |
|--------|------|---------|
| Backend | `backend/` | FastAPI, auth, portfolio, brokers, chat, news, health, vault |
| Frontend | `frontend/` | Next.js terminal UI — dashboard, portfolio, chat, preferences, news |
| UI Library | `packages/ravel-ui/` | Shared design tokens and UI components (`@alphaforge-anton/ravel-ui`) |
| Logger (Python) | `packages/logger-py/` | `alphaforge-logger` — rotating file + console |
| Logger (Node) | `packages/logger-node/` | `@alphaforge/logger` — pino-based |
| Repo Context MCP | `mcp/` | stdio MCP server for Claude/Copilot/Cursor — semantic + structural repo context |
| Infra | `infra/` | Docker Compose and local setup scripts |

---

## Quick Start

```bash
# Clone
git clone https://github.com/your-username/alpha-forge-anton.git
cd alpha-forge-anton

# Full setup (prereqs + venv + env files)
./setup.sh

# Start PostgreSQL + Redis (macOS)
./setup.sh --db

# Apply DB migrations
just db-migrate

# Start backend + frontend
just dev-local
```

Frontend: http://localhost:3000  
Backend API: http://localhost:8000  
OpenAPI docs: http://localhost:8000/docs

### Alternate Setup Modes

```bash
./setup.sh --prereqs    # Homebrew packages + pyenv + nvm
./setup.sh --venv       # Python venv + uv install
./setup.sh --backend    # Backend deps only
./setup.sh --frontend   # Frontend deps only
./setup.sh --env        # Scaffold .env.cred.local + .env.frontend.local

# Containers (OrbStack or Docker)
docker compose -f infra/docker-compose.yml up --build
```

---

## Common Commands

```bash
# Development
just dev-local      # backend + frontend together
just backend        # FastAPI only
just frontend       # Next.js only

# Quality
just test
just lint
just format

# DB
just db-migrate
just db-shell

# MCP server (Repo Context)
just mcp-install
just mcp-start
```

---

## Brokers

| Broker | Slug | Data Source | Assets |
|--------|------|-------------|--------|
| Zerodha Kite | `zerodha` | Kite Connect API / CSV | Equity, F&O |
| Zerodha Coin | `zerodha_coin` | Coin CSV dump | Mutual funds |
| Groww | `groww` | CSV dump | Equity, MF |
| Angel One | `angelone` | CSV dump | Equity |
| IndMoney | `indmoney` | CSV dump | US stocks, MF |
| Tickertape | `tickertape` | CSV dump | Watchlist, MF |
| Binance | `binance` | CSV dump | Crypto |

All CSV-based brokers share `dump_utils.py` — see [docs/broker-csv-dumps.md](docs/broker-csv-dumps.md).

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/architecture.md](docs/architecture.md) | Repo structure, tech decisions, key files |
| [docs/conventions.md](docs/conventions.md) | Python + TypeScript coding conventions |
| [docs/commands.md](docs/commands.md) | CLI commands (setup, run, build, migrate, clean) |
| [docs/guardrails.md](docs/guardrails.md) | Project rules and guardrails |
| [docs/broker-csv-dumps.md](docs/broker-csv-dumps.md) | Broker CSV dump contract (shared `dump_utils`) |
| [docs/vault.md](docs/vault.md) | Vault-backed secrets (`alpha-forge-bach`) |
| [docs/live-prices-plan.md](docs/live-prices-plan.md) | Live prices design plan (not yet built) |

---

## Project Structure

```
alpha-forge-anton/
├── backend/                  # Python 3.14 + FastAPI
│   ├── app/
│   │   ├── core/             # Config, DB, security, env_loader
│   │   └── modules/          # Feature modules (each owns routes + service + schemas)
│   │       ├── auth/         # JWT auth + User ORM
│   │       ├── brokers/      # BrokerSource adapters + aggregator + registry
│   │       ├── portfolio/    # Holdings, orders, watchlist
│   │       ├── chat/         # Alpha AI chat (SSE streaming)
│   │       ├── news/         # News feed routes
│   │       ├── dashboard/    # Cross-module aggregation
│   │       ├── trade/        # Paper / live trade endpoints
│   │       ├── health/       # /health + /health/boot (boot probes)
│   │       └── vault/        # Vault-backed secret access
│   ├── alembic/              # DB migrations
│   └── tests/
├── frontend/                 # Next.js 15 + React 19 + TypeScript + Tailwind v4
│   └── src/
│       ├── app/              # App Router pages (/, /portfolio, /preferences, /news)
│       ├── lib/              # api.ts, logger.ts, store.ts, providers.tsx
│       └── modules/
│           ├── portfolio/    # Treemap, ledger, wallet strip, filter bar, compact bar
│           ├── chat/         # AlphaBar, ChatRail, ModelPicker, useChatStream
│           ├── dashboard/    # TerminalTopBar, BootScreen, BootGate
│           ├── preferences/  # 8-section settings UI
│           ├── news/         # News feed components
│           ├── auth/         # Login + AuthGuard
│           └── trade/        # Trade panel
├── packages/
│   ├── ravel-ui/             # @alphaforge-anton/ravel-ui (Button, Input, Card, Badge…)
│   ├── logger-py/            # alphaforge-logger (Python)
│   └── logger-node/          # @alphaforge/logger (Node/TS, pino)
├── mcp/                      # Repo Context MCP server (Claude/Copilot/Cursor)
├── infra/                    # docker-compose.yml + setup-local.sh
├── probes/                   # UI smoke tests via CDP (ui_probe.py, ui_screens.py)
├── design/                   # Hi-Fi HTML prototype + Claude Design transcripts
├── docs/                     # Project documentation
├── CLAUDE.md                 # Claude Code context
├── pyproject.toml            # uv workspace root
├── pnpm-workspace.yaml       # pnpm workspace root
├── justfile                  # Dev commands
└── LICENSE
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | Python 3.14 + FastAPI (async) |
| Python tooling | uv (workspace, single lockfile) |
| Frontend | Next.js 15 + React 19 + TypeScript |
| Node tooling | pnpm |
| Database | PostgreSQL 16 (asyncpg + SQLAlchemy) |
| Cache / Pub-Sub | Redis 7 |
| AI Chat | OpenAI + LangChain (SSE streaming, JWT-gated) |
| Charts | Lightweight Charts (TradingView) |
| Styling | Tailwind CSS v4 + Solar Terminal design tokens |
| Local infra | Homebrew (native) or OrbStack |
| Secrets | Vault-backed via `alpha-forge-bach` |

---

## License

MIT — see [LICENSE](LICENSE).
