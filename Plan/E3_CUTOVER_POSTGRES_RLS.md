# E3 Cutover — SQLite → Postgres+RLS

id: E3_CUTOVER_POSTGRES_RLS
version: 1.2
status: CORTE_COMPLETADO_Y_VALIDADO
stamp: 2026-07-07

---

## 1. Estado actual

- Código: adapter dual (`app/src/db_adapter.py`), RLS policies (`app/scripts/postgres_rls_policies.sql`), migrador (`app/scripts/sqlite_to_postgres.py`).
- VPS Postgres (`faberloom-postgres`, port 5435) tiene esquema migrado y RLS aplicado.
- Rol `faberloom_app` existe con `NOBYPASSRLS`, `LOGIN`, password rotada.
- Tests E3-1 pasan contra `faberloom_app` con RLS real (23 passed: adapter + RLS canary + FTS parity + migration).
- **CORTE REALIZADO Y VALIDADO**: `.env` de producción apunta a Postgres; contenedor `faberloom-api` está healthy y responde en `https://app.faberloom.ai`.
- **Reconciliación de tenant completada**: Foundation resolvió al usuario autenticado como `tnt_5d9b14dbab2f4f61b105`, pero las filas migradas desde SQLite quedaron bajo `default`. Se migraron todos los datos tenant-scoped a `tnt_5d9b14dbab2f4f61b105` (workspace, kb_*, chat, message, usage_record, object, ambient_*, audit_log, editorial_history, workspace_smtp_config, workspace_routing_policy, workspace_model_catalog, email_account, mail_message, mail_outbox). Se preservó `canary`.
- `/api/me`, `/api/auth/login` y `/api/workspaces` verificados en producción: devuelven los workspaces del owner.
- Password de `faberloom_app` rotada; `CREATE ON DATABASE` revocado.
- `FABERLOOM_TENANT_ID=tnt_5d9b14dbab2f4f61b105` configurado para alinear seed con tenant foundation.

## 2. Pre-corte (histórico — ya ejecutado)

1. Backup SQLite realizado en `/data/backups/faberloom.sqlite3.20260707_162233`.
2. Backup Postgres realizado antes del corte.
3. Migrador ejecutado con `--drop --create`.
4. RLS re-aplicada como owner.
5. Permisos ajustados para `faberloom_app` (`CREATE, USAGE` en `public`).

## 3. Corte (realizado)

1. `.env` en `/opt/faber_loom/.env`:
   ```
   FABERLOOM_DB_ENGINE=postgres
   FABERLOOM_POSTGRES_URL=postgresql://faberloom_app:<ROTADO>@faberloom-postgres:5432/faberloom
   FABERLOOM_FOUNDATION_DB_ENGINE=sqlite
   FABERLOOM_FOUNDATION_DB=/data/foundation.sqlite3
   FABERLOOM_TENANT_ID=tnt_5d9b14dbab2f4f61b105
   ```
2. Imagen Docker reconstruida con `psycopg[binary]` y `psycopg-pool`.
3. `docker compose up -d --build api` ejecutado; contenedor healthy.
4. Healthcheck: `GET http://localhost:8200/api/health` → 200.
5. Canary isolation: ejecutado contra réplica idéntica de producción; pasó 122/122.
6. `/api/me`, `/api/workspaces`, login y listado de workspaces verificados.

## 4. Rollback

1. Si algo falla, volver a `.env`:
   ```
   FABERLOOM_DB_ENGINE=sqlite
   ```
2. `docker compose up -d --build api`
3. Restaurar SQLite desde backup si hubo corrupción.

## 5. Post-corte / TODOs cerrados

- [x] Ejecutar `scripts/check_canary_isolation_postgres.py` en producción (contra réplica idéntica; pasó 122/122).
- [x] Fix crítico P0: envolver `system_get_workspace` y `system_get_workspace_by_slug` en `transaction(conn, ctx=ctx)` para que RLS vea las filas en Postgres; sin esto el seed fallaba al reiniciar.
- [x] Fix P0: `_DictRow` ahora soporta acceso posicional `row[0]` para compatibilidad con código existente bajo Postgres.
- [x] Revocar `CREATE ON DATABASE` a `faberloom_app` en producción y rotar su password.
- [x] Implementar endpoints `platform_admin` de E3-2 (aprobación/suspensión de tenants y métricas agregadas).
- [x] Integrar `security/secrets.py` en `router/config_store.py` y `storage.py` (E3-3).
- [x] Integrar `faster-whisper` en `ingest.py` y escribir `ACTA_ETAPA2_TERMINADA` (E3-0).
- [x] Eliminar/verificar variable `FABERLOOM_DEV_TRUST_HEADERS` de cualquier `.env`/compose (no estaba presente).
- [x] Validación de tests: suite local 480 passed/12 skipped; tests Postgres E3 23 passed; producción health + `/api/me` + `/api/workspaces` OK.
- [x] Monitoreo inicial: logs muestran arranque limpio, conexiones Postgres devueltas al pool (`rolling back returned connection`).
- [ ] Documentar incidente en `docs/audits/` si aplica (pendiente a criterio del owner).

## 6. Notas para el próximo despliegue

- Los tests E3 que usan `TestClient` no pueden correr con `FABERLOOM_DB_ENGINE=postgres` porque `initialize_database` aplica migrations SQLite a Postgres. Se validaron en SQLite localmente y los tests específicos de Postgres contra el VPS.
- `check_canary_isolation_postgres.py` fue corregido para insertar `tenant_id` en `kb_chunk`, `kb_fact`, `gold_candidate` y `mail_outbox`, y para incluir `updated_at` en `ambient_detector`.
- `test_e3_1_postgres_migration.py` fue corregido para manejar tablas auxiliares FTS y el conteo de tablas SQLite.
