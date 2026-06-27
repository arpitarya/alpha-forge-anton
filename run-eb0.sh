#!/usr/bin/env bash
#
# run-eb0.sh — pull real NSE data, build the panel, run the real EB-0 verdict.
# Run on a NETWORKED machine. Idempotent: re-run to resume if NSE throttles.
#
# Prereqs: `just` on PATH; the gzip + --exclusions follow-up applied to build-panel/eb0-real.
# Override any default with an env var, e.g.  START_YEAR=2018 bash run-eb0.sh
#
set -euo pipefail

ANTON_DIR="${ANTON_DIR:-/Users/arpitarya/my_programs/anton}"
ELGAR_DIR="${ELGAR_DIR:-/Users/arpitarya/my_programs/elgar}"
EXCLUSIONS="${EXCLUSIONS:-$ELGAR_DIR/store/plans/hard-exclusion-symbols.json}"
START_YEAR="${START_YEAR:-2016}"
MAX_RETRIES="${MAX_RETRIES:-4}"
RAW_DIR=""  # OFFLINE INPUT ONLY: set to a dir of pre-downloaded NSE archives to ingest without
            # network. Leave EMPTY for the normal network fetch (cache → $NSE_DATA_DIR; resumes
            # idempotently, already-fetched days are skipped). It is NOT where data is saved.

command -v just >/dev/null || { echo "ERROR: 'just' not found on PATH"; exit 1; }
[ -d "$ANTON_DIR" ]   || { echo "ERROR: anton dir not found: $ANTON_DIR"; exit 1; }
[ -f "$EXCLUSIONS" ]  || { echo "ERROR: exclusions file not found: $EXCLUSIONS"; exit 1; }
cd "$ANTON_DIR"

TODAY="$(date +%F)"; CUR_YEAR="$(date +%Y)"
echo "==> anton=$ANTON_DIR"
echo "==> exclusions=$EXCLUSIONS"
echo "==> range=${START_YEAR}-01-01 .. ${TODAY}"

run_with_retry() {                      # retry a command with linear backoff
  local n=1
  until "$@"; do
    if [ "$n" -ge "$MAX_RETRIES" ]; then
      echo "!! failed after ${MAX_RETRIES} attempts: $*"
      echo "   ingest is idempotent — just re-run this script to resume where it stopped."
      exit 1
    fi
    local backoff=$(( 30 * n ))
    echo "   attempt ${n} failed; backing off ${backoff}s (NSE may be throttling)…"
    sleep "$backoff"; n=$(( n + 1 ))
  done
}

# 1) ingest year-by-year (smaller chunks survive throttling; cached days are skipped)
for (( y=START_YEAR; y<=CUR_YEAR; y++ )); do
  from="${y}-01-01"
  if [ "$y" -eq "$CUR_YEAR" ]; then to="$TODAY"; else to="${y}-12-31"; fi
  echo "==> ingest-nse ${from} ${to}"
  if [ -n "${RAW_DIR:-}" ]; then
    run_with_retry just ingest-nse "$from" "$to" --raw-dir "$RAW_DIR"
  else
    run_with_retry just ingest-nse "$from" "$to"
  fi
  sleep 3                               # be polite between years
done

# 2) build the committed (gzipped) panel with runtime exclusions
echo "==> build-panel"
just build-panel --exclusions "$EXCLUSIONS"

# 3) real EB-0 verdict — journals to elgar; PASS and KILL are both valid
echo "==> eb0-real"
just eb0-real --exclusions "$EXCLUSIONS"

echo
echo "==> done. Verdict journaled to elgar://edge/edge-001"
echo "    review: cat ${ELGAR_DIR}/store/edges/edge-001-groww-momentum-quality.journal.md"
