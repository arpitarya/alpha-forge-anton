#!/usr/bin/env bash
# start.sh — Start all Anton local development services + sister projects
# Services started:
#   PostgreSQL + Redis   (via database/db.sh)
#   Bach vault           (../bach)
#   Dante security API   (../dante, optional local HTTP API on :9100)
#   Wagner IAM backend   (../wagner, on :8001 to avoid clash with Anton :8000)
#   Anton backend        (FastAPI on :8000)
#   Anton frontend       (Next.js on :3000)
# Wagner + Dante code is also embedded inside Anton's backend; the standalone
# servers here are for direct development against those projects.
# Run ./stop.sh to stop everything.

set -euo pipefail

ANTON_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROGRAMS_ROOT="$(cd "$ANTON_ROOT/.." && pwd)"
BACH_ROOT="$PROGRAMS_ROOT/bach"
DANTE_ROOT="$PROGRAMS_ROOT/dante"
WAGNER_ROOT="$PROGRAMS_ROOT/wagner"
PID_FILE="$ANTON_ROOT/.dev.pids"

# ── Colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BLUE='\033[0;34m'; MAGENTA='\033[0;35m'
PURPLE='\033[0;95m'; ORANGE='\033[0;33m'; NC='\033[0m'

log()  { echo -e "${CYAN}[start]${NC} $*"; }
ok()   { echo -e "${GREEN}[start]${NC} $*"; }
warn() { echo -e "${YELLOW}[start]${NC} $*"; }
err()  { echo -e "${RED}[start]${NC} $*" >&2; }

prefix_lines() {
    local col="$1" name="$2"
    while IFS= read -r line; do
        echo -e "${col}[${name}]${NC} ${line}"
    done
}

wait_for_port() {
    local name="$1" port="$2" retries="${3:-30}"
    local i=0
    while ! nc -z 127.0.0.1 "$port" 2>/dev/null && ! nc -z ::1 "$port" 2>/dev/null; do
        i=$((i + 1))
        if [ "$i" -ge "$retries" ]; then
            err "$name did not open port $port after ${retries}s — check logs"
            return 1
        fi
        sleep 1
    done
}

# Read a single KEY from a dotenv-style file (handles values with spaces;
# avoids bash `source` which mis-parses unquoted spaces in .env files).
read_env_value() {
    local file="$1" key="$2"
    [ -f "$file" ] || return 1
    awk -F= -v k="$key" '
        /^[[:space:]]*#/ { next }
        $1 == k { sub(/^[^=]*=/, ""); sub(/[[:space:]]+#.*$/, ""); print; exit }
    ' "$file"
}

# ── Guard against double-start ────────────────────────────────────────────────
if [ -f "$PID_FILE" ]; then
    err "Anton appears to be running already (.dev.pids exists). Run ./stop.sh first."
    exit 1
fi

# ── Ports (from .env.port — safe to source: numeric values only) ─────────────
set -a
source "$ANTON_ROOT/.env.port"
set +a

BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"
WAGNER_PORT="${WAGNER_BACKEND_PORT:-8001}"
DANTE_PORT="${DANTE_PORT:-9100}"

# Bach port comes from bach's own .env.local first, then .env
BACH_PORT="$(read_env_value "$BACH_ROOT/.env.local" AFBACH_VAULT_PORT 2>/dev/null \
            || read_env_value "$BACH_ROOT/.env" AFBACH_VAULT_PORT 2>/dev/null \
            || echo 8765)"
BACH_URL="$(read_env_value "$ANTON_ROOT/.env.cred.local" AFBACH_URL 2>/dev/null \
           || echo "http://[::1]:${BACH_PORT}/v1")"

# ── Cleanup on early failure ─────────────────────────────────────────────────
cleanup_on_error() {
    err "Startup failed — rolling back."
    [ -f "$PID_FILE" ] && {
        # shellcheck source=/dev/null
        source "$PID_FILE"
        for pid in ${FRONTEND_PID:-} ${BACKEND_PID:-} ${WAGNER_PID:-} ${DANTE_PID:-} ${BACH_PID:-}; do
            kill "$pid" 2>/dev/null || true
        done
        rm -f "$PID_FILE"
    }
    bash "$ANTON_ROOT/database/db.sh" stop 2>/dev/null || true
}
trap cleanup_on_error ERR

# ── 1. Database: PostgreSQL + Redis ──────────────────────────────────────────
log "Starting PostgreSQL + Redis…"
bash "$ANTON_ROOT/database/db.sh" start
ok "Database services started."

# ── 2. Bach vault ────────────────────────────────────────────────────────────
BACH_PID=""
if [ -d "$BACH_ROOT" ] && [ -x "$BACH_ROOT/.venv/bin/afbach" ]; then
    log "Starting Bach vault on :${BACH_PORT}…"
    (
        cd "$BACH_ROOT"
        exec .venv/bin/afbach serve
    ) 2>&1 | prefix_lines "$MAGENTA" "bach" &
    BACH_PID=$!

    if wait_for_port "bach" "$BACH_PORT" 15; then
        ok "Bach vault ready at ${BACH_URL}"
    else
        warn "Bach vault not responding — backend will fall back to file-based env"
    fi
else
    warn "Bach not found / not installed at $BACH_ROOT — skipping (file env will be used)"
fi

# ── 3. Dante security API (optional) ─────────────────────────────────────────
DANTE_PID=""
if [ -d "$DANTE_ROOT" ] && [ -x "$DANTE_ROOT/.venv/bin/dante" ]; then
    log "Starting Dante security API on :${DANTE_PORT}…"
    (
        cd "$DANTE_ROOT"
        exec .venv/bin/dante serve --port "$DANTE_PORT"
    ) 2>&1 | prefix_lines "$PURPLE" "dante" &
    DANTE_PID=$!
    if wait_for_port "dante" "$DANTE_PORT" 10; then
        ok "Dante ready at http://127.0.0.1:${DANTE_PORT}"
    else
        warn "Dante did not open :${DANTE_PORT} — continuing (Anton has Dante middleware embedded)"
    fi
else
    warn "Dante not found / not installed at $DANTE_ROOT — skipping standalone server (middleware is embedded in Anton)"
fi

# ── 4. Wagner IAM backend (standalone, on :WAGNER_PORT) ──────────────────────
WAGNER_PID=""
if [ -d "$WAGNER_ROOT/backend" ]; then
    log "Running Wagner Alembic migrations…"
    (cd "$WAGNER_ROOT" && BACKEND_PORT="$WAGNER_PORT" uv run --project backend alembic upgrade head 2>&1) \
        | prefix_lines "$ORANGE" "wagner-migrate" || warn "Wagner migrations failed — continuing"

    log "Starting Wagner backend on :${WAGNER_PORT}…"
    (
        cd "$WAGNER_ROOT"
        export BACKEND_HOST=127.0.0.1
        export BACKEND_PORT="$WAGNER_PORT"
        exec uv run --project backend uvicorn app.main:app --reload --host 127.0.0.1 --port "$WAGNER_PORT"
    ) 2>&1 | prefix_lines "$ORANGE" "wagner" &
    WAGNER_PID=$!
    if wait_for_port "wagner" "$WAGNER_PORT" 30; then
        ok "Wagner ready at http://127.0.0.1:${WAGNER_PORT}"
    else
        warn "Wagner backend did not open :${WAGNER_PORT} — continuing (Anton has Wagner embedded)"
    fi
else
    warn "Wagner not found at $WAGNER_ROOT — skipping standalone server (IAM is embedded in Anton)"
fi

# ── 5. Anton DB migrations ───────────────────────────────────────────────────
log "Running Anton Alembic migrations…"
(cd "$ANTON_ROOT/backend" && uv run alembic upgrade head 2>&1) | prefix_lines "$YELLOW" "migrate"
ok "Anton migrations up to date."

# ── 6. Anton backend ─────────────────────────────────────────────────────────
log "Starting Anton backend on :${BACKEND_PORT}…"
(
    cd "$ANTON_ROOT/backend"
    exec uv run uvicorn app.main:app --reload --host 0.0.0.0 --port "$BACKEND_PORT"
) 2>&1 | prefix_lines "$BLUE" "backend" &
BACKEND_PID=$!

if ! wait_for_port "backend" "$BACKEND_PORT" 30; then
    err "Backend failed to start — check logs above"
    exit 1
fi
ok "Backend ready at http://localhost:${BACKEND_PORT}"

# ── 7. Anton frontend ────────────────────────────────────────────────────────
log "Starting Anton frontend on :${FRONTEND_PORT}…"
(
    cd "$ANTON_ROOT/frontend"
    exec pnpm dev
) 2>&1 | prefix_lines "$GREEN" "frontend" &
FRONTEND_PID=$!

# ── Persist PIDs for stop.sh ─────────────────────────────────────────────────
{
    echo "BACH_PID=${BACH_PID}"
    echo "DANTE_PID=${DANTE_PID}"
    echo "WAGNER_PID=${WAGNER_PID}"
    echo "BACKEND_PID=${BACKEND_PID}"
    echo "FRONTEND_PID=${FRONTEND_PID}"
} > "$PID_FILE"

# Don't roll-back from here onward — services are launched and tracked
trap - ERR

# ── Ready ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
ok "Anton stack is running  (PIDs saved to .dev.pids)"
echo -e "  ${BLUE}Anton backend${NC}    http://localhost:${BACKEND_PORT}"
echo -e "  ${GREEN}Anton frontend${NC}   http://localhost:${FRONTEND_PORT}"
echo -e "  ${YELLOW}API docs${NC}         http://localhost:${BACKEND_PORT}/docs"
[ -n "$BACH_PID" ]   && echo -e "  ${MAGENTA}Bach vault${NC}       ${BACH_URL}"
[ -n "$DANTE_PID" ]  && echo -e "  ${PURPLE}Dante API${NC}        http://127.0.0.1:${DANTE_PORT}"
[ -n "$WAGNER_PID" ] && echo -e "  ${ORANGE}Wagner backend${NC}   http://127.0.0.1:${WAGNER_PORT}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Run ./stop.sh to stop all services${NC}"
echo ""

# Stream logs until the user disconnects this shell. Closing this terminal
# does NOT stop the background services — use ./stop.sh for that.
wait
