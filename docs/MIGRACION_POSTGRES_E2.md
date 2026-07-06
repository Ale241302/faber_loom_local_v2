# Migración SQLite → Postgres (E2-0 / E2-1)

**id:** MIGRACION_POSTGRES_E2  
**versión:** 1.0  
**fecha:** 2026-07-06  
**estado:** planificación ejecutable (E2-0); ejecución productiva en E2-1  

---

## 1. Alcance

Este documento describe cómo migrar la base SQLite de FaberLoom a Postgres 16+ con RLS, manteniendo la app en SQLite durante E2-0 y ejecutando la migración productiva en E2-1.

---

## 2. Requisitos

- Postgres 16+ (la imagen `postgres:16-alpine` está en `docker-compose.yml`).
- `psycopg2-binary` instalado en el entorno virtual.
- Backup de la SQLite fuente antes de cualquier migración real.
- Variables de entorno en `.env` (ver `.env.example`):
  - `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
  - `DATABASE_URL` para la app (ej. `postgresql://faberloom_app:...`)

---

## 3. Backup previo

```bash
# Antes de tocar nada
mkdir -p backups/$(date +%Y%m%d_%H%M%S)
cp app/data/faberloom.sqlite3 backups/$(date +%Y%m%d_%H%M%S)/
cp app/data/audit.jsonl backups/$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
```

---

## 4. Dry-run

El script soporta `--dry-run` para inspeccionar tablas, DDL y conteos sin conectar a Postgres:

```bash
source .venv/Scripts/activate
python app/scripts/sqlite_to_postgres.py \
  --sqlite-path app/data/faberloom.sqlite3 \
  --dry-run
```

---

## 5. Migración en vivo

### 5.1 Levantar Postgres

```bash
docker compose up -d postgres
# Esperar healthcheck (puerto host 5435)
```

### 5.2 Crear usuarios

Ejecutar como superusuario (`postgres` o un admin migrador):

```sql
CREATE USER faberloom_app WITH PASSWORD '...' NOBYPASSRLS;
CREATE USER faberloom_migrator WITH PASSWORD '...';
CREATE DATABASE faberloom OWNER faberloom_migrator;
GRANT ALL PRIVILEGES ON DATABASE faberloom TO faberloom_migrator;
```

### 5.3 Ejecutar migración de datos

```bash
source .venv/Scripts/activate
python app/scripts/sqlite_to_postgres.py \
  --sqlite-path app/data/faberloom.sqlite3 \
  --postgres-url "postgresql://faberloom_migrator:...@localhost:5435/faberloom" \
  --drop-existing \
  --log-path backups/migration_$(date +%Y%m%d_%H%M%S).jsonl
```

El script:

1. Lee el schema de SQLite.
2. Crea tablas equivalentes en Postgres.
3. Migra datos en batch.
4. Crea índices básicos.
5. Verifica conteos por tabla.

### 5.4 Aplicar RLS

```bash
psql "postgresql://faberloom_migrator:...@localhost:5435/faberloom" \
  -f app/scripts/postgres_rls_policies.sql
```

Esto crea:

- `faberloom_app` sin `BYPASS RLS`.
- Políticas RLS por `tenant_id` + `workspace_id`.
- Función `set_app_scope(tenant, workspace)`.

---

## 6. Verificación

```bash
source .venv/Scripts/activate
python app/scripts/sqlite_to_postgres.py \
  --sqlite-path app/data/faberloom.sqlite3 \
  --postgres-url "postgresql://faberloom_migrator:...@localhost:5435/faberloom" \
  --dry-run
```

Comparar la columna "sqlite rows" con "postgres rows". Deben coincidir.

Además, como `faberloom_app`:

```sql
SET ROLE faberloom_app;
SELECT COUNT(*) FROM workspace;  -- Debe ser 0 sin set_app_scope
SELECT set_app_scope('default', '__system__');
SELECT COUNT(*) FROM workspace;  -- Ahora ve workspaces del tenant default
```

---

## 7. Rollback

El rollback de E2-1 es **restaurar el backup SQLite** y apuntar la app de nuevo a él:

```bash
# Detener app
# Restaurar backup
cp backups/YYYYMMDD_HHMMSS/faberloom.sqlite3 app/data/faberloom.sqlite3
# Revertir DATABASE_URL a SQLite (o dejar vacío para default)
# Reiniciar app
```

No se borra la SQLite fuente durante la migración.

---

## 8. Cambiar app a Postgres

En `app/src/db.py` se debe implementar un switch (futuro):

```python
if os.getenv("FABERLOOM_DATABASE_URL", "").startswith("postgresql://"):
    # usar psycopg2
else:
    # sqlite3 actual
```

Esto queda fuera del alcance de E2-0; se ejecuta en E2-1.

---

## 9. Referencias

- `app/scripts/sqlite_to_postgres.py`
- `app/scripts/postgres_rls_policies.sql`
- `docker-compose.yml`
- `.env.example`
- `docs/CONTEXT_RLS_CONTRACT_E2.md`
