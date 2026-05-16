# CLAUDE.md — Context for Claude Code

**AlphaForge** — Personal AI-powered portfolio management & investment terminal for Indian markets.
Python 3.14/FastAPI backend + Next.js 15/TypeScript frontend monorepo. Self-hosted, MIT licensed.

## Docs Index

| Topic | File |
|-------|------|
| Architecture, repo tree, tech decisions, key files | [docs/architecture.md](docs/architecture.md) |
| Coding conventions (Python + TypeScript) | [docs/conventions.md](docs/conventions.md) |
| CLI commands (setup, run, build, migrate, clean) | [docs/commands.md](docs/commands.md) |
| Guardrails & project rules | [docs/guardrails.md](docs/guardrails.md) |
| Broker CSV dumps (shared dump_utils contract) | [docs/broker-csv-dumps.md](docs/broker-csv-dumps.md) |
| Graphify knowledge graph | [docs/graphify.md](docs/graphify.md) |
| Live-prices design plan (not yet built) | [docs/live-prices-plan.md](docs/live-prices-plan.md) |

## Must-Know Rules

Apply these on every file without looking up the docs:

- Files ≤ **100 lines** (≤ **50** for `*_utils.py` / `*.utils.ts`)
- Backend filenames: `{domain}_{role}.py` — Frontend: `{domain}.{role}.ts`
- Python: `async def` everywhere, absolute imports from `app.`, Pydantic v2, ruff (line-length=100)
- TypeScript: strict mode, functional components only, pnpm, Biome v2
- Never commit `.env` files or API keys
- All broker CSV dumps use `dump_utils.py` — see [docs/broker-csv-dumps.md](docs/broker-csv-dumps.md)
- Every code change must be accompanied by a doc update in the same session

## Skills

| Trigger | What it does |
|---------|--------------|
| `/broker` | Add, edit, or remove a broker source (registry, module files, fixtures, docs) |

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep — these traverse the graph's EXTRACTED + INFERRED edges instead of scanning files
- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost)
