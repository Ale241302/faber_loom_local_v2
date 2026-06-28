# Reporte de cierre SL3.5 — v1 (§8)

**Fecha:** 2026-06-25  
**Agente:** Kimi Code CLI  
**Loop CLOSER:** §5 AUDIT → PLAN → IMPLEMENT → TEST → GATE → REPORTE

## Estado

SL3.5 **CERRADO**.

## 1. SQLCipher para workspaces confidenciales

- **Schema v17:** `workspace.confidential`, `workspace.passphrase`, `workspace.workspace_db_path`.
- **DB separada:** cada workspace confidencial vive en `{main}-conf-{workspace_id}.sqlite3` y se abre con `sqlcipher3` usando `PRAGMA key`.
- **Workspaces normales:** continúan usando SQLite plano sin cifrado.
- **Archivos:** `app/src/db.py::connect_workspace_data_db`, `app/src/db.py::get_workspace_database_path`.

## 2. Enrutamiento seguro por request

- **Dependency:** `app/src/api.py::get_workspace_db`.
- Si `workspace.confidential = 0`, usa la conexión principal.
- Si `workspace.confidential = 1`, exige `x-workspace-passphrase`. Sin header → `401`; clave incorrecta → `401` (no `500`).
- Se corrigió el bloque huérfano `system_context(...)` que rompía requests a workspaces cifrados.

## 3. Sellado HMAC + confidencialidad

- Cada workspace mantiene `seal_id` independiente.
- Los HMACs de `kb_source`, `kb_fact` y `draft` se computan con `seal_id`.
- **Test:** `test_kb_source_hmac_blocks_simulated_leak`, `test_kb_fact_hmac_blocks_simulated_leak`, `test_draft_hmac_blocks_simulated_leak`.

## 4. Fuga cross-workspace = 0

### Modo plano

- **Tests:** `test_kb_source_is_cross_workspace_isolated`, `test_draft_is_cross_workspace_isolated`.
- Resultado: canario de workspace A no aparece en búsqueda de workspace B ni en la DB principal.

### Modo cifrado

- **Test:** `test_confidential_workspace_is_cross_workspace_isolated`.
- Se ingestó canario `FUGA_CANARY_999` en workspace confidencial.
- Un workspace normal adyacente no lo encontró (`facts == []`, `chunks == []`).
- La DB plana principal no contiene el canario.

## 5. Backup/export/restore de workspace cifrado

- **Test:** `test_backup_restore_confidential_workspace_smoke`.
- Flujo:
  1. Crear workspace confidencial con passphrase `bk-secret`.
  2. Ingestar fuente con canario `BACKUP_CANARY_12345`.
  3. Exportar DB cifrada con `db_key=bk-secret` y encriptar archivo con `passphrase=export-secret`.
  4. Restaurar a nueva ruta usando `passphrase=export-secret`.
  5. Abrir restored con `sqlcipher3` + `PRAGMA key='bk-secret'` y verificar el canario.
- Resultado: canario recuperado intacto.

## 6. Multi-tenant

- **Tenant isolation:** `test_confidential_workspace_tenant_isolation`.
  - Workspace confidencial creado en `tenant-a`.
  - `tenant-a` + passphrase correcta → `200`.
  - `tenant-b` + passphrase correcta → `404` (el workspace no existe para ese tenant).
  - `seal-check` respeta el mismo scope.
- **Herencia cross-tenant bloqueada:** `test_confidential_workspace_cannot_inherit_cross_tenant_parent`.
  - Crear padre confidencial en `tenant-a`.
  - Intentar crear hijo en `tenant-b` con `parent_id=padre` → `422`.

## 7. PRC-04 fallback

- Se usaron canarios sintéticos (`CANARY_CONFIDENTIAL_CONTENT_42`, `FUGA_CANARY_999`, `BACKUP_CANARY_12345`).
- No se requirió dataset real confidencial para cerrar el gate.

## Resultados de test

```text
pytest app/tests/test_sl3_5_seal.py -q
17 passed, 1 warning

pytest app/tests -q
194 passed, 1 warning
```

Baseline SL3b/c: `185 passed`.  
Incremento neto: **+9 tests**.

## Archivos clave

- `app/src/models.py` — schema v17 y modelos `WorkspaceCreate`/`WorkspaceRead`.
- `app/src/db.py` — conexión SQLCipher, mirror seguro del workspace.
- `app/src/api.py` — `get_workspace_db`, manejo de passphrase, creación de workspace confidencial.
- `app/src/backup.py` — export con `db_key` y checkpoint para bases cifradas.
- `app/tests/test_sl3_5_seal.py` — suite SL3.5 (17 tests).
- `harness/reports/PLAN_SL3_5_CLOSER_v1.md`
- `harness/reports/SL3_5_CLOSER_REPORT_v1.md` — este reporte.

## Restricciones respetadas

- `ENT_OPS_STATE_MACHINE` y `PLB_ORCHESTRATOR` no fueron modificados.
- No se inventaron datos MWT reales.
