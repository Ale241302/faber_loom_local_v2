#!/usr/bin/env bash
# Cron wrapper: weekly soak + routing evidence reports.
# Intended for VPS deployment at /opt/faber_loom.

set -euo pipefail

REPO_DIR="/opt/faber_loom"
VENV="$REPO_DIR/.venv"
PYTHON="$VENV/bin/python"
DB_PATH="$REPO_DIR/app/data/faberloom.sqlite3"
FOUNDATION_DB="$REPO_DIR/app/data/foundation.sqlite3"
OUT_DIR="$REPO_DIR/docs/audits"
LOG_FILE="$REPO_DIR/app/data/weekly_reports_$(date +%Y%m%d_%H%M%S).log"

export FABERLOOM_DB_PATH="$DB_PATH"
export FABERLOOM_FOUNDATION_DB="$FOUNDATION_DB"

cd "$REPO_DIR"

# shellcheck disable=SC2094
exec >> "$LOG_FILE" 2>&1

echo "[$(date -Iseconds)] Starting weekly reports"
"$PYTHON" "$REPO_DIR/app/scripts/run_weekly_reports.py" \
    --db-path "$DB_PATH" \
    --foundation-db "$FOUNDATION_DB" \
    --out-dir "$OUT_DIR" \
    --week "$(date +%V)"
echo "[$(date -Iseconds)] Weekly reports finished with exit code $?"
