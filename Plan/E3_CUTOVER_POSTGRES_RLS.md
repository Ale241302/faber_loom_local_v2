# E3 Cutover — SQLite → Postgres+RLS

id: E3_CUTOVER_POSTGRES_RLS
version: 1.0
status: READY
stamp: 2026-07-07

---

## 1. Estado actual

- Código: adapter dual (`app/src/db_adapter.py`), RLS policies (`app/scripts/postgres_rls_policies.sql`), migrador (`app/scripts/sqlite_to_postgres.py`).
- VPS Postgres (`faberloom-postgres`, port 5435) tiene esquema migrado y RLS aplicado.
- Rol `faberloom_app` existe con `NOBYPASSRLS`, `LOGIN`, password `faberloom_app`, `CREATE ON DATABASE` (para tests; revocar en prod).
- Tests E3-1 pasan contra `faberloom_app` con RLS real (19 passed).
- App en VPS sigue corriendo con SQLite (`FABERLOOM_DB_ENGINE` no está seteado o es `sqlite`).

## 2. Pre-corte

1. Backup SQLite:
   ```bash
   ssh -p 2222 root@187.77.218.102
   cp /opt/faber_loom/app/data/faberloom.sqlite3 /opt/faber_loom/backup/faberloom.sqlite3.$(date +%Y%m%d_%H%M%S)
   ```
2. Backup Postgres:
   ```bash
   docker exec faberloom-postgres pg_dump -U faberloom -d faberloom > /opt/faber_loom/backup/faberloom_postgres_$(date +%Y%m%d_%H%M%S).sql
   ```
3. Poner app en modo mantenimiento o read-only si es posible (no implementado aún).
4. Re-ejecutar migrador con datos actuales y verificar conteos:
   ```bash
   cd /opt/faber_loom/app
   source .venv/bin/activate
   FABERLOOM_POSTGRES_URL=postgresql://faberloom:faberloom@faberloom-postgres:5432/faberloom \
     python scripts/sqlite_to_postgres.py --drop --create
   ```
5. Re-aplicar RLS como owner:
   ```bash
   docker exec -i faberloom-postgres psql -U faberloom -d faberloom \
     -v app_user=faberloom_app < app/scripts/postgres_rls_policies.sql
   ```
6. Revocar `CREATE ON DATABASE` a `faberloom_app` en producción:
   ```sql
   REVOKE CREATE ON DATABASE faberloom FROM faberloom_app;
   ```
7. Generar contraseña fuerte para `faberloom_app` y rotar inmediatamente.

## 3. Corte

1. Editar `/opt/faber_loom/.env`:
   ```
   FABERLOOM_DB_ENGINE=postgres
   FABERLOOM_POSTGRES_URL=postgresql://faberloom_app:<STRONG_PASSWORD>@faberloom-postgres:5432/faberloom
   FABERLOOM_FOUNDATION_DB_ENGINE=sqlite   # Foundation puede quedar en SQLite por ahora
   ```
2. `docker compose up -d --build api`
3. Verificar health:
   ```bash
   curl -s https://<host>/api/health | jq
   ```
4. Ejecutar canario de aislamiento:
   ```bash
   python scripts/check_canary_isolation_postgres.py
   ```
5. Verificar que `/api/me`, `/api/workspaces`, login y un chat de prueba funcionan.

## 4. Rollback

1. Si algo falla, volver a `.env`:
   ```
   FABERLOOM_DB_ENGINE=sqlite
   # quitar FABERLOOM_POSTGRES_URL o dejarla
   ```
2. `docker compose up -d --build api`
3. Restaurar SQLite desde backup si hubo corrupción.

## 5. Post-corte

- Eliminar variable `FABERLOOM_DEV_TRUST_HEADERS` de cualquier `.env`/compose.
- Monitorear logs 24h.
- Programar rotación de password `faberloom_app` y master key.
- Documentar incidente en `docs/audits/`.
