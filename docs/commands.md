# AlphaForge — Commands

```bash
# ── Full repo setup ───────────────────────────────────────────────────────────
./setup.sh                # One command to set up everything
./setup.sh --help         # Show all setup.sh options

# ── Setup — granular ─────────────────────────────────────────────────────────
./setup.sh --prereqs      # Check/install pyenv, nvm, pnpm, uv
./setup.sh --venv         # Create .venv via `uv venv` (reads .python-version)
./setup.sh --backend      # Sync the entire Python workspace (uv sync) + Playwright browsers
./setup.sh --frontend     # Frontend + workspace deps (pnpm) + build solar-orb-ui
./setup.sh --env          # Scaffold .env files from examples
./setup.sh --dirs         # Create log/data/model directories
./setup.sh --db           # Setup local PostgreSQL + Redis (macOS Homebrew)

# ── Python Workspace (uv) ────────────────────────────────────────────────────
uv sync                              # Install/refresh every workspace member into .venv
uv lock                              # Refresh uv.lock without installing
uv add httpx --package alphaforge-backend   # Add a dep to a specific member
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
cd packages/solar-orb-ui && pnpm build   # Build ESM + CJS + DTS
cd packages/solar-orb-ui && pnpm dev     # Watch mode

# ── Infrastructure ───────────────────────────────────────────────────────────
./setup.sh --db                                                  # macOS native (Homebrew)
# OR:
docker compose -f infra/docker-compose.yml up -d                 # via OrbStack

# ── Migrations ───────────────────────────────────────────────────────────────
cd backend && uv run alembic upgrade head
cd backend && uv run alembic revision --autogenerate -m "description"

# ── Copilot Browser Integration ──────────────────────────────────────────────
just setup-mcp                            # Install Playwright Chromium + MCP config

# ── Repo Context MCP ─────────────────────────────────────────────────────────
cd repo-context-mcp && pdm install                               # Install deps
cd repo-context-mcp && pdm run index --full                      # Build initial vector index
cd repo-context-mcp && pdm run index --watch                     # Watch + incremental reindex
cd repo-context-mcp && pdm run serve                             # Run MCP server (stdio)
alphaforge-repo-context-mcp                                      # Same server (after `pdm install`)

# ── Cleanup ──────────────────────────────────────────────────────────────────
./clean.sh                # Remove build artifacts and bytecode (keeps venv + node_modules)
./clean.sh --cache        # Remove only tool caches
./clean.sh --venv         # Remove Python venv
./clean.sh --backend      # Deep-clean backend (artifacts, caches, venv)
./clean.sh --frontend     # Deep-clean frontend (.next, node_modules)
./clean.sh --all          # Nuclear clean — removes everything (run setup.sh to restore)
```
