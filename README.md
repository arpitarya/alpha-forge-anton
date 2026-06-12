# AlphaForge Anton

<p align="center">
  <img src="logo.png" alt="AlphaForge Anton Logo" width="400" />
</p>

**Personal AI-powered Portfolio Management and Investment Terminal for Indian Markets**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

AlphaForge Anton is an open-source, self-hosted investment terminal for Indian markets
(NSE/BSE + global crypto). It unifies holdings scattered across many brokers into one
currency-correct view, and layers **Orff** — a multi-provider AI concierge that can
compose live UI in chat — on top, **without your financial data ever leaving your machine
for a third-party SaaS**.

Built for personal use and research.

---

## The Ecosystem

Anton is the terminal; four sibling tools own the concerns a finance app must get right:

| Sibling | Repo | Owns |
|---------|------|------|
| **bach** (afbach) | `~/my_programs/bach` | Vault — every API key and broker credential, served over a local unlock daemon |
| **wagner** | `~/my_programs/wagner` | IAM — multi-user auth, JWT/refresh tokens, API keys; Anton proxies to it |
| **dante** | `~/my_programs/dante` | Security audit — 10 circles + a PII scanner wired into Anton's pre-commit |
| **elgar** | `~/my_programs/elgar` | Private plan store — **every money document** lives there, never in this repo |
| **fux** | `~/my_programs/fux` | Knowledge engine — `.fux/` rules/formulas/memory ground both Claude Code and Orff |

### Where knowledge and money live (the two-place rule)

- **This repo's `.fux/`** — public-safe knowledge only: conventions, formulas,
  Indian tax/market rules, investment principles. Percentages and statutes, never
  personal figures.
- **The elgar store** (`~/.alphaforge-anton/elgar`, private git repo) — all personal
  money documents: plans, targets, projections. Anton holds `elgar://plan/<id>`
  links only; `just dante-pii` + pre-commit enforce it.

---

## Highlights

- **Multi-broker aggregation** — seven sources rolled up read-only into one
  INR-normalised portfolio (valuation, day P&L, treemap, allocation drift).
- **Orff concierge** — SSE-streaming chat over a 7-provider registry (Gemini, Groq,
  Cerebras, Mistral, OpenRouter, HuggingFace, Claude SDK) with intent-based routing
  from a single JSON manifest.
- **Privacy floor** — holdings questions are auto-detected and pinned to a trusted
  provider; the model sees a percentages-only disclosure, never ₹ amounts or symbols.
- **Generated UI, safe by construction** — Orff emits a declarative JSON UISpec over a
  curated 19-component / 5-hook vocabulary, validated server-side by fux and rendered
  only from a client whitelist. No eval, no dynamic code, ever.
- **Plans & projections** — band-aware rebalance drift against your elgar-stored plan;
  compound projections from committed capital-market assumptions, every response
  citing its assumptions source. A **save plan** button writes any Orff answer
  straight into the private store.
- **Boot screen** — per-service readiness (vault, DB, LLM gateway, every broker) on
  each tab open, with mid-life vault unlock re-priming brokers automatically.

---

## Quick Start

```bash
git clone https://github.com/arpitarya/alpha-forge-anton.git
cd alpha-forge-anton

./setup.sh            # prereqs + venv + deps + env scaffolding
./setup.sh --db       # start PostgreSQL + Redis (macOS native)
just db-migrate
just dev-local        # backend :8000 + frontend :3000
```

Frontend: https://localhost:3000 · API: http://localhost:8000 · OpenAPI: `/docs`

Broker syncs and probes need the CDP Chrome: `just zerodha-chrome` (port 9299),
then log into your broker tabs there. Secrets come from the afbach vault —
`afbach unlock` before first boot.

---

## Common Commands

```bash
just dev-local        # backend + frontend together
just backend          # FastAPI only        · just frontend — Next.js only
just test             # backend pytest + frontend tests
just lint             # ruff + Biome
just probe <name>     # CDP verification probes (probes/probe.sh — the source of truth)
just dante-pii        # money-document / PII scan (also runs in pre-commit)
just fux-check        # knowledge-vs-code drift check
just gen-concierge    # regenerate frontend registry from the JSON manifest
```

---

## Brokers

| Broker | Slug | Fetch | Assets |
|--------|------|-------|--------|
| Zerodha Kite | `zerodha` | enctoken API | Equity |
| Zerodha Coin | `zerodha_coin` | Kite enctoken | Mutual funds |
| Groww | `groww` | CDP browser fetch | Equity, MF |
| Angel One | `angelone` | CDP browser fetch | Equity |
| INDmoney | `indmoney` | CDP browser fetch | US stocks, MF |
| Tickertape | `tickertape` | CDP browser fetch | Gold |
| Binance | `binance` | CDP browser fetch | Crypto (USD) |

Every source is a `BrokerSource` subclass; CSV caching is shared through
`dump_utils.py` — see [docs/broker-csv-dumps.md](docs/broker-csv-dumps.md).
Never-synced READY sources are primed automatically at startup.

---

## Project Structure

```
alpha-forge-anton/
├── backend/app/
│   ├── core/                 # config, DB, security, vault client, env loader
│   └── modules/              # one module per domain: routes + service + schemas
│       ├── brokers/          # BrokerSource adapters, aggregator, refetch/prime
│       ├── portfolio/        # holdings, treemap, wallets
│       ├── plans/            # plan loader (elgar), drift, projections, save-plan
│       ├── concierge/        # Orff: SSE chat, privacy floor, UISpec compose
│       ├── iam/              # proxy to wagner
│       ├── news/ dashboard/ health/ vault/
├── concierge/llm/            # gateway package — providers, registry manifest, routing
├── frontend/src/modules/     # portfolio, concierge, plans, dashboard, preferences,
│                             # screener, vault, auth
├── packages/
│   ├── solar-ui/             # @alphaforge-anton/solar-ui — design system +
│   │                         # finance primitives (charts, stats, tables)
│   ├── logger-py/ logger-node/ solar-orb-ball/
├── probes/                   # CDP verification probes (never Playwright MCP)
├── .fux/                     # knowledge substrate — rules, formulas, memory, graph
├── docs/                     # architecture, conventions, commands, guardrails
└── justfile                  # all dev commands
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/architecture.md](docs/architecture.md) | Repo structure, tech decisions, key files |
| [docs/conventions.md](docs/conventions.md) | Python + TypeScript coding conventions |
| [docs/commands.md](docs/commands.md) | CLI commands (setup, run, build, migrate, clean) |
| [docs/guardrails.md](docs/guardrails.md) | Project rules — incl. the money-documents guardrail |
| [docs/broker-csv-dumps.md](docs/broker-csv-dumps.md) | Broker CSV dump contract (shared `dump_utils`) |
| [docs/vault.md](docs/vault.md) | Vault-backed secrets (`alpha-forge-bach`) |
| [concierge/README.md](concierge/README.md) | Orff concierge implementation docs |
| [probes/Probes.md](probes/Probes.md) | How to write & run CDP verification probes |

The deeper knowledge layer — business rules, formulas, decisions — lives in `.fux/`
(`fux why <id>`, `fux refs <path>`), kept drift-free against the code by `fux check`.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.14 + FastAPI (async end-to-end) · uv workspace |
| Frontend | Next.js 15 + React 19 + TypeScript (strict) · pnpm · Biome v2 |
| Database | PostgreSQL 16 (asyncpg + SQLAlchemy) · Redis 7 |
| AI gateway | Multi-provider registry (7 providers) · SSE streaming · cost guard |
| Charts | Lightweight Charts (TradingView) + solar-ui SVG primitives |
| Styling | Tailwind CSS v4 + Solar Terminal design tokens |
| Secrets | afbach vault (local daemon, auto-lock) |
| Verification | CDP probes (`probes/`, Chrome :9299) |

---

## License

MIT — see [LICENSE](LICENSE).
