#!/usr/bin/env bash
# ==============================================================================
# AlphaForge Anton — Full Repository Setup
# ==============================================================================
# Usage:
#   ./setup.sh                  # Full repo setup (prereqs + venv + deps + env + dirs)
#   ./setup.sh --prereqs        # Check/install system prerequisites only
#   ./setup.sh --venv           # Create Python venv only
#   ./setup.sh --backend        # Install backend Python dependencies only
#   ./setup.sh --frontend       # Install frontend + workspace Node dependencies only
#   ./setup.sh --env            # Create .env files from examples (non-destructive)
#   ./setup.sh --dirs           # Create all required directories
#   ./setup.sh --graphify       # Setup graphify for Claude, Codex, Copilot, hooks, and graph
#   ./setup.sh --db             # Setup local PostgreSQL + Redis (macOS Homebrew)
#   ./setup.sh --help           # Show usage
# ==============================================================================

set -euo pipefail

# ── Constants ─────────────────────────────────────────────────────────────────
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$REPO_ROOT/.venv"
PYTHON="$VENV_DIR/bin/python"

REQUIRED_PYTHON_MAJOR=3
REQUIRED_PYTHON_MINOR=14

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ── Helpers ───────────────────────────────────────────────────────────────────

info()    { echo -e "${CYAN}ℹ  $*${NC}"; }
ok()      { echo -e "${GREEN}✅ $*${NC}"; }
warn()    { echo -e "${YELLOW}⚠️  $*${NC}"; }
fail()    { echo -e "${RED}❌ $*${NC}"; exit 1; }
section() { echo -e "\n${BOLD}── $* ──${NC}"; }

usage() {
    cat <<EOF
AlphaForge Anton — Full Repository Setup

Usage: $(basename "$0") [OPTION]

Setup:
  (no args)       Full setup: prereqs, venv, all deps, env files, directories
  --prereqs       Check/install system prerequisites (pyenv, nvm, pnpm, uv, brew)
  --venv          Create repo-root Python venv (.venv/) from .python-version
  --backend       Sync the uv workspace (installs all Python deps, then Playwright browsers)
  --frontend      Install frontend + workspace Node packages (pnpm)
  --env           Scaffold .env files from .env.example templates (non-destructive)
  --dirs          Create required directories (logs)
  --graphify      Setup graphify for Claude, Codex, Copilot, hooks, and graph refresh
  --db            Setup local PostgreSQL 16 + Redis via Homebrew (macOS only)

Misc:
  --help          Show this help message

Prerequisites:
  - macOS (Homebrew) — primary supported platform
  - pyenv (Python 3.14+ pinned in .python-version)
  - nvm (Node.js pinned in .nvmrc)
  - pnpm (workspace package manager)
  - uv (Python package manager — workspace-aware)
  - Homebrew (for PostgreSQL, Redis)
  - graphify (optional knowledge graph helper; install via: uv tool install graphifyy)

EOF
    exit 0
}

# ── Prerequisite Checks ──────────────────────────────────────────────────────

check_brew() {
    if ! command -v brew &>/dev/null; then
        fail "Homebrew not found. Install from https://brew.sh"
    fi
    ok "Homebrew found"
}

check_pyenv() {
    if ! command -v pyenv &>/dev/null; then
        warn "pyenv not found"
        read -rp "Install pyenv via Homebrew? [y/N] " ans
        if [[ "$ans" =~ ^[Yy]$ ]]; then
            brew install pyenv
            ok "pyenv installed — add 'eval \"\$(pyenv init -)\"' to your shell profile"
        else
            fail "pyenv is required. Install via: brew install pyenv"
        fi
    fi

    local required_ver
    required_ver=$(cat "$REPO_ROOT/.python-version" 2>/dev/null || echo "${REQUIRED_PYTHON_MAJOR}.${REQUIRED_PYTHON_MINOR}.2")

    if ! pyenv versions --bare 2>/dev/null | grep -qx "$required_ver"; then
        warn "Python $required_ver not installed in pyenv"
        read -rp "Install Python $required_ver via pyenv? [y/N] " ans
        if [[ "$ans" =~ ^[Yy]$ ]]; then
            pyenv install "$required_ver"
            ok "Python $required_ver installed"
        else
            warn "Skipping Python install. Venv creation may fail."
        fi
    else
        ok "Python $required_ver available (pyenv)"
    fi
}

check_nvm_and_node() {
    local required_node
    required_node=$(cat "$REPO_ROOT/.nvmrc" 2>/dev/null || echo "v24.13.0")

    # Source nvm if available but not loaded
    if ! command -v nvm &>/dev/null; then
        export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
        # shellcheck disable=SC1091
        [[ -s "$NVM_DIR/nvm.sh" ]] && source "$NVM_DIR/nvm.sh"
    fi

    if ! command -v nvm &>/dev/null; then
        warn "nvm not found — install from https://github.com/nvm-sh/nvm"
        # Fall back to checking node directly
        if command -v node &>/dev/null; then
            ok "Node.js found: $(node --version) (nvm not managing it)"
        else
            fail "Neither nvm nor node found. Install nvm first."
        fi
        return
    fi

    # Install the required Node version if missing
    if ! nvm ls "$required_node" &>/dev/null; then
        info "Installing Node.js $required_node via nvm..."
        nvm install "$required_node"
    fi
    nvm use "$required_node" 2>/dev/null || true
    ok "Node.js $(node --version) active (nvm)"
}

check_pnpm() {
    if ! command -v pnpm &>/dev/null; then
        warn "pnpm not found"
        read -rp "Install pnpm via corepack? [y/N] " ans
        if [[ "$ans" =~ ^[Yy]$ ]]; then
            corepack enable
            corepack prepare pnpm@latest --activate
            ok "pnpm installed via corepack"
        else
            fail "pnpm is required. Install via: corepack enable && corepack prepare pnpm@latest --activate"
        fi
    else
        ok "pnpm $(pnpm --version) found"
    fi
}

check_uv() {
    if ! command -v uv &>/dev/null; then
        warn "uv not found"
        read -rp "Install uv via Homebrew? [y/N] " ans
        if [[ "$ans" =~ ^[Yy]$ ]]; then
            brew install uv
            ok "uv installed"
        else
            fail "uv is required. Install via: brew install uv"
        fi
    else
        ok "uv $(uv --version) found"
    fi
}

check_all_prereqs() {
    section "Checking Prerequisites"
    check_brew
    check_pyenv
    check_nvm_and_node
    check_pnpm
    check_uv
}

# ── Python Venv ───────────────────────────────────────────────────────────────

create_venv() {
    section "Python Virtual Environment (uv)"

    if [[ -x "$PYTHON" ]]; then
        ok "Venv already exists at $VENV_DIR ($($PYTHON --version))"
        return
    fi

    info "Creating venv via uv (reads .python-version)..."
    cd "$REPO_ROOT" && uv venv
    ok "Venv created at $VENV_DIR ($($PYTHON --version))"
}

check_venv() {
    if [[ ! -x "$PYTHON" ]]; then
        fail "Python venv not found at $VENV_DIR. Run './setup.sh --venv' first."
    fi
}

# ── Environment Files ─────────────────────────────────────────────────────────

scaffold_env_files() {
    section "Environment Files"
    if [[ -x "$REPO_ROOT/setup-config.sh" ]]; then
        "$REPO_ROOT/setup-config.sh"
    else
        warn "setup-config.sh missing — falling back to legacy copy"
        for pair in "backend/.env.example:backend/.env" \
                    "frontend/.env.example:frontend/.env.local" \
                    ".env.cred.example:.env.cred.local"; do
            local src="${pair%%:*}" dst="${pair##*:}"
            if [[ -f "$REPO_ROOT/$src" && ! -f "$REPO_ROOT/$dst" ]]; then
                cp "$REPO_ROOT/$src" "$REPO_ROOT/$dst"
                ok "Created $dst from $src"
            fi
        done
    fi
}

# ── Directory Setup ───────────────────────────────────────────────────────────

create_dirs() {
    section "Required Directories"

    local dirs=(
        "$REPO_ROOT/backend/logs"
        "$REPO_ROOT/frontend/logs"
    )

    for d in "${dirs[@]}"; do
        mkdir -p "$d"
    done

    ok "All directories ready"
}

# ── Graphify Knowledge Graph ──────────────────────────────────────────────────

run_graphify_installer() {
    local label="$1"
    shift

    info "Installing graphify for $label..."
    if graphify "$@"; then
        ok "graphify $label integration installed"
    else
        warn "graphify $label integration did not complete. Rerun './setup.sh --graphify' outside restricted sandboxes if needed."
    fi
}

setup_graphify() {
    section "Graphify Knowledge Graph"

    if ! command -v graphify &>/dev/null; then
        warn "graphify CLI not found."
        echo "  Install it with: uv tool install graphifyy"
        return
    fi

    ok "graphify found: $(command -v graphify)"

    run_graphify_installer "Claude" claude install
    run_graphify_installer "Codex" codex install
    run_graphify_installer "VS Code Copilot Chat" vscode install
    run_graphify_installer "GitHub Copilot CLI" copilot install

    info "Installing graphify git hooks..."
    graphify hook install
    ok "graphify git hooks installed"

    info "Refreshing graphify-out/ from the current repo..."
    graphify update .
    ok "graphify graph refreshed"
}

# ── Python Workspace Dependencies (uv) ────────────────────────────────────────

sync_workspace() {
    section "Python Workspace (uv sync)"

    info "Syncing all workspace members (backend, logger-py)..."
    cd "$REPO_ROOT" && uv sync --group dev
    ok "Workspace synced into $VENV_DIR"

    info "Installing nbstripout git filter (strips notebook outputs before commit)..."
    cd "$REPO_ROOT" && uv run nbstripout --install
    ok "nbstripout git filter active"

    info "Wiring nbdime diff/merge drivers (full venv paths)..."
    VENV_BIN="$REPO_ROOT/.venv/bin"
    git -C "$REPO_ROOT" config diff.jupyternotebook.command         "$VENV_BIN/git-nbdiffdriver diff"
    git -C "$REPO_ROOT" config merge.jupyternotebook.driver         "$VENV_BIN/git-nbmergedriver merge %O %A %B %L %P"
    git -C "$REPO_ROOT" config merge.jupyternotebook.name           "jupyter notebook merge driver"
    git -C "$REPO_ROOT" config difftool.nbdime.cmd                  "$VENV_BIN/git-nbdifftool diff \"\$LOCAL\" \"\$REMOTE\" \"\$BASE\""
    git -C "$REPO_ROOT" config mergetool.nbdime.cmd                 "$VENV_BIN/git-nbmergetool merge \"\$BASE\" \"\$LOCAL\" \"\$REMOTE\" \"\$MERGED\""
    ok "nbdime diff/merge drivers wired"

    install_headless_browser
}

install_backend() { sync_workspace; }

# ── Frontend / Workspace Dependencies ─────────────────────────────────────────

install_frontend() {
    section "Frontend & Workspace Dependencies (pnpm)"

    info "Installing workspace Node packages (frontend + packages/*)..."
    cd "$REPO_ROOT" && pnpm install
    ok "Workspace Node packages installed"

    # Build the UI package so the frontend can consume it
    info "Building @alphaforge-anton/ravel-ui package..."
    cd "$REPO_ROOT/packages/ravel-ui" && pnpm build
    cd "$REPO_ROOT"
    ok "ravel-ui built"
}

# ── Headless Browser Dependencies ─────────────────────────────────────────────

install_headless_browser() {
    section "Headless Browser Dependencies"

    check_venv
    info "Installing Playwright Chromium browser..."
    "$PYTHON" -m playwright install chromium
    ok "Playwright Chromium installed"
}

# ── Database Setup ────────────────────────────────────────────────────────────

setup_db() {
    section "Local Database Setup"

    if [[ "$(uname)" != "Darwin" ]]; then
        warn "Local DB setup currently supports macOS only. Use Docker instead:"
        echo "  docker compose -f infra/docker-compose.yml up postgres redis -d"
        return
    fi

    if [[ -f "$REPO_ROOT/infra/setup-local.sh" ]]; then
        bash "$REPO_ROOT/infra/setup-local.sh"
    else
        fail "infra/setup-local.sh not found"
    fi
}

# ── Full Setup ────────────────────────────────────────────────────────────────

full_setup() {
    echo ""
    echo "╔══════════════════════════════════════════════╗"
    echo "║   AlphaForge Anton — Full Repository Setup         ║"
    echo "╚══════════════════════════════════════════════╝"
    echo ""

    check_all_prereqs
    create_venv
    create_dirs
    scaffold_env_files
    setup_graphify
    install_backend
    install_frontend
    install_headless_browser
    echo ""
    echo "╔══════════════════════════════════════════════╗"
    echo "║   Setup Complete!                            ║"
    echo "╚══════════════════════════════════════════════╝"
    echo ""
    echo "  Next steps:"
    echo ""
    echo "  1. Review & update environment files:"
    echo "     - backend/.env        (DB credentials, API keys)"
    echo "     - frontend/.env.local (API URL, ports)"
    echo ""
    echo "  2. Start local infrastructure (if not running):"
    echo "     just db-local          # PostgreSQL + Redis via Homebrew"
    echo "     # OR: just db-up       # via Docker/OrbStack"
    echo ""
    echo "  3. Run database migrations:"
    echo "     just db-migrate"
    echo ""
    echo "  4. Start development servers:"
    echo "     just dev-local         # Backend + frontend (Procfile)"
    echo "     # OR individually:"
    echo "     just backend           # Backend only"
    echo "     just frontend          # Frontend only"
    echo ""
}

# ── Main ──────────────────────────────────────────────────────────────────────

cd "$REPO_ROOT"

case "${1:-}" in
    --help|-h)      usage ;;
    --prereqs)      check_all_prereqs ;;
    --venv)         create_venv ;;
    --backend)      install_backend ;;
    --frontend)     install_frontend ;;
    --env)          scaffold_env_files ;;
    --dirs)         create_dirs ;;
    --graphify)     setup_graphify ;;
    --db)           setup_db ;;
    "")             full_setup ;;
    *)              fail "Unknown option: $1 (use --help for usage)" ;;
esac
