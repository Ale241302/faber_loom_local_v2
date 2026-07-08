#!/usr/bin/env bash
# Corte SQLite -> PostgreSQL/RLS para FaberLoom E3-1.
# Ejecutar con la API DETENIDA o en ventana de mantenimiento.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

SQLITE_PATH="${FABERLOOM_DB_PATH:-/data/faberloom.sqlite3}"
PG_URL="${FABERLOOM_POSTGRES_URL:-${DATABASE_URL:-postgresql://faberloom:faberloom@postgres:5432/faberloom}}"
PG_ADMIN_URL="${FABERLOOM_POSTGRES_ADMIN_URL:-$PG_URL}"
APP_ROLE="${FABERLOOM_POSTGRES_APP_ROLE:-faberloom_app}"
APP_PASSWORD="${FABERLOOM_POSTGRES_APP_PASSWORD:-faberloom_app}"
RLS_SQL="${FABERLOOM_RLS_SQL:-$REPO_ROOT/app/scripts/postgres_rls_policies.sql}"

if [ ! -f "$SQLITE_PATH" ]; then
    echo "ERROR: SQLite database not found: $SQLITE_PATH"
    exit 1
fi

echo "== E3-1 SQLite -> PostgreSQL cutover =="
echo "SQLite source: $SQLITE_PATH"
echo "Postgres target: $PG_URL"

# 1. Backup SQLite
echo "[1/6] Backing up SQLite ..."
BACKUP_DIR="/data/backups"
mkdir -p "$BACKUP_DIR"
cp "$SQLITE_PATH" "$BACKUP_DIR/faberloom.sqlite3.$(date -u +%Y%m%d_%H%M%S).bak"

# 2. Backup Postgres antes de tocarla
echo "[2/6] Backing up Postgres ..."
"$REPO_ROOT/app/scripts/backup_postgres.sh" "$BACKUP_DIR" || true

# 3. Crear rol de aplicación sin BYPASSRLS
echo "[3/6] Ensuring application role $APP_ROLE exists ..."
psql "$PG_ADMIN_URL" -v ON_ERROR_STOP=1 <<EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '$APP_ROLE') THEN
        CREATE ROLE $APP_ROLE LOGIN NOBYPASSRLS NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD '$APP_PASSWORD';
    END IF;
END
\$\$;
GRANT CREATE ON DATABASE "$(echo "$PG_URL" | sed -n 's/.*\/\([^/]*\)$/\1/p')" TO $APP_ROLE;
GRANT CREATE ON SCHEMA public TO $APP_ROLE;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $APP_ROLE;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $APP_ROLE;
EOF

# 4. Migrar esquema y datos
echo "[4/6] Migrating SQLite -> Postgres ..."
python "$REPO_ROOT/app/scripts/sqlite_to_postgres.py" \
    --sqlite-path "$SQLITE_PATH" \
    --postgres-url "$PG_URL" \
    --schema public \
    --drop-existing

# 5. Aplicar políticas RLS
echo "[5/6] Applying RLS policies ..."
if [ -f "$RLS_SQL" ]; then
    psql "$PG_ADMIN_URL" -v ON_ERROR_STOP=1 -f "$RLS_SQL"
else
    echo "WARNING: RLS SQL not found at $RLS_SQL"
fi

# 6. Verificar canario RLS
echo "[6/6] Running RLS canary check ..."
python "$REPO_ROOT/app/scripts/check_canary_isolation_postgres.py" \
    --postgres-url "$PG_URL"

echo ""
echo "== Cutover complete =="
echo "Set FABERLOOM_DB_ENGINE=postgres and restart the API."
echo "Rollback: restore SQLite backup and set FABERLOOM_DB_ENGINE=sqlite."
