# AlphaForge Anton — Graphify

This project maintains a knowledge graph at `graphify-out/`.

## Rules

- Before answering architecture or codebase questions, read `graphify-out/GRAPH_REPORT.md` for god nodes and community structure
- If `graphify-out/wiki/index.md` exists, navigate it instead of reading raw files
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep — these traverse the graph's EXTRACTED + INFERRED edges instead of scanning files. Run them **metered through cage**: bare `graphify …` is auto-metered once the `bin/graphify` shim is on PATH (after `setup.sh --graphify`), or call it explicitly with `cage graphify -- graphify query "…"` / `just graphify-cage 'query "…"'`. This files a `tool="graphify"` token-saving receipt that `cage matrix` credits in the graphify×fux grid.
- After modifying code files in a session, run `graphify update .` to keep the graph current (AST-only, no API cost). Leave `graphify update .` **unwrapped** — it's a refresh, not a query, so there's nothing to meter.

## Copilot Chat

Type `/graphify` in Copilot Chat to build or update the knowledge graph.
