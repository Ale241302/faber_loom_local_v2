#!/usr/bin/env bash
# Backup de PostgreSQL para FaberLoom E3-1.
# Uso: ./backup_postgres.sh [dest_dir]
set -euo pipefail

DEST_DIR="${1:-/data/backups}"
TIMESTAMP=$(date -u +%Y%m%d_%H%M%S)
mkdir -p "$DEST_DIR"

PG_URL="${FABERLOOM_POSTGRES_URL:-${DATABASE_URL:-postgresql://faberloom:faberloom@localhost:5432/faberloom}}"
DUMP_FILE="$DEST_DIR/faberloom_postgres_${TIMESTAMP}.sql.gz"

echo "Backing up Postgres to $DUMP_FILE ..."
pg_dump "$PG_URL" --clean --if-exists --create | gzip > "$DUMP_FILE"

echo "Backup complete: $DUMP_FILE"
