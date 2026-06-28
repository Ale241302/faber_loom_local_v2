# Plan SL3.5 CLOSER — v1 (CERRADO)

**Fecha:** 2026-06-25  
**Loop:** §5 AUDIT → PLAN → IMPLEMENT → TEST → GATE → REPORTE  
**Reglas:** No inventar. FROZEN (`ENT_OPS_STATE_MACHINE`, `PLB_ORCHESTRATOR`) intactos.

## DoD objetivo

1. Índice-vs-contenido + sellado HMAC por workspace ya existente; endurecer con SQLCipher.
2. SQLCipher/passphrase para workspaces con `confidential=true`; passphrase solo ahí; workspaces normales sin cifrado.
3. Test de fuga cross-workspace = 0 en ambos modos (planos y cifrados) con canarios sintéticos.
4. Backup/export/restore smoke test para workspace cifrado.
5. Multi-tenant: sellado respeta `tenant_id`; herencia no cruza tenants bajo cifrado.
6. `test_sl3_5_seal.py` verdes + tests de flag `confidential` + backup/restore.
7. Gate §6 completo.
8. Reporte §8.

## Cambios técnicos

### 1. Schema v17 para workspaces confidenciales

- `app/src/models.py`:
  - `SCHEMA_VERSION = 17`.
  - Migración añade `workspace.confidential` (INTEGER NOT NULL DEFAULT 0), `workspace.passphrase` (TEXT) y `workspace.workspace_db_path` (TEXT).
  - `WorkspaceCreate`/`WorkspaceRead` exponen `confidential` y `passphrase`.

### 2. Base de datos de datos separada con SQLCipher

- `app/src/db.py`:
  - `get_workspace_database_path(workspace_id, main_path)` construye `{main}-conf-{workspace_id}.sqlite3`.
  - `connect_workspace_data_db()` abre la DB con `sqlcipher3`, aplica `PRAGMA key`, WAL y migraciones.
  - `create_workspace()` valida passphrase para `confidential=1`, crea el archivo SQLCipher y guarda `workspace_db_path`.
  - `_mirror_workspace_to_data_db()` copia la fila del workspace a la DB cifrada sin traer `parent_id` (vive en main DB) ni `passphrase`.

### 3. Enrutamiento de requests workspace-scoped

- `app/src/api.py`:
  - `get_workspace_db()` lee el flag `confidential` del workspace.
  - Workspaces normales usan la conexión principal.
  - Workspaces confidenciales exigen header `x-workspace-passphrase`; si falta → `401`, si la clave no descifra → `401`.
  - Se eliminó bloque huérfano `system_context(...)` que causaba `NameError`.

### 4. Backup/restore de DB cifrada

- `app/src/backup.py`:
  - `export_db()` acepta `db_key` para abrir SQLCipher, ejecuta `PRAGMA wal_checkpoint(TRUNCATE)` y exporta bytes crudos.
  - Sin `db_key` sigue usando `sqlite3` para DBs planas.
  - El cifrado del archivo `.spaceloom` sigue siendo Fernet/PBKDF2 (`passphrase`).

### 5. Tests SL3.5

- `app/tests/test_sl3_5_seal.py`:
  - `test_confidential_workspace_requires_passphrase`
  - `test_confidential_workspace_without_passphrase_is_rejected`
  - `test_confidential_workspace_data_is_encrypted_separately`
  - `test_confidential_workspace_is_cross_workspace_isolated`
  - `test_backup_restore_confidential_workspace_smoke`
  - `test_confidential_workspace_tenant_isolation`
  - `test_confidential_workspace_cannot_inherit_cross_tenant_parent`

## Resultados de test

```text
pytest app/tests/test_sl3_5_seal.py -q
17 passed, 1 warning

pytest app/tests -q
194 passed, 1 warning
```

Baseline SL3b/c: `185 passed`.  
Incremento neto: **+9 tests**.

## Gate §6 — Checklist

- [x] SL3.5 tests verdes (`test_sl3_5_seal.py`).
- [x] Full suite verde (`pytest app/tests`).
- [x] Fuga cross-workspace = 0 en modo plano y cifrado.
- [x] Backup/restore smoke test para workspace cifrado.
- [x] Multi-tenant: tenant isolation + herencia cross-tenant rechazada.
- [x] FROZEN (`ENT_OPS_STATE_MACHINE`, `PLB_ORCHESTRATOR`) intactos.
- [x] Reporte §8 generado.

## Archivos modificados

- `app/src/models.py` — schema v17, modelos `WorkspaceCreate`/`WorkspaceRead`.
- `app/src/db.py` — SQLCipher connection, mirror sin `parent_id`/`passphrase`.
- `app/src/api.py` — `get_workspace_db` enrutado y manejo de passphrase.
- `app/src/backup.py` — export con `db_key` y checkpoint para SQLCipher.
- `app/tests/test_sl3_5_seal.py` — suite SL3.5 ampliada.
- `harness/reports/PLAN_SL3_5_CLOSER_v1.md` — este plan.
- `harness/reports/SL3_5_CLOSER_REPORT_v1.md` — reporte de cierre §8.

## Restricciones respetadas

- `ENT_OPS_STATE_MACHINE` y `PLB_ORCHESTRATOR` no modificados.
- No se inventaron datos MWT reales.
