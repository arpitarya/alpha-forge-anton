# AlphaForge — Copilot Instructions

Personal AI-powered portfolio management & investment terminal for Indian markets.
Python 3.14/FastAPI backend + Next.js 15/TypeScript frontend monorepo. Self-hosted, MIT licensed.

## Docs Index

| Topic | File |
|-------|------|
| Architecture, repo tree, tech decisions, key files | [docs/architecture.md](../docs/architecture.md) |
| Coding conventions (Python + TypeScript) | [docs/conventions.md](../docs/conventions.md) |
| CLI commands (setup, run, build, migrate, clean) | [docs/commands.md](../docs/commands.md) |
| Guardrails & project rules | [docs/guardrails.md](../docs/guardrails.md) |
| Broker CSV dumps (shared dump_utils contract) | [docs/broker-csv-dumps.md](../docs/broker-csv-dumps.md) |
| Graphify knowledge graph | [docs/graphify.md](../docs/graphify.md) |

## Quick Rules

- Files ≤ **100 lines** (≤ **50** for `*_utils.py` / `*.utils.ts`)
- Python: `async def` everywhere, absolute imports from `app.`, Pydantic v2, ruff
- TypeScript: strict mode, functional components, pnpm, Biome v2
- New broker dumps → always use `dump_utils.py`
- All AI outputs include financial disclaimer
- Never commit `.env` files or API keys
- Type `/graphify` in Copilot Chat to build or update the knowledge graph

## graphify

Before answering architecture or codebase questions, read `graphify-out/GRAPH_REPORT.md` if it exists.
If `graphify-out/wiki/index.md` exists, navigate it for deep questions.
Type `/graphify` in Copilot Chat to build or update the knowledge graph.
