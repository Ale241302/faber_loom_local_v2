# Context + RLS — Contrato de Etapa 2

**id:** CONTEXT_RLS_CONTRACT_E2  
**versión:** 1.0  
**fecha:** 2026-07-06  
**estado:** vigente  

---

## 1. Principio

> **Context is God.**

Toda lectura o escritura de datos de aplicación debe recibir un `Context(workspace_id, tenant_id, user_id, actor_id, actor_role_at_decision)`. El contexto es el contrato de aislamiento: en SQLite se valida con `enforce_tenant_scoped(ctx)`; en Postgres se refuerza con Row Level Security (RLS).

---

## 2. Contrato de `Context`

```python
@dataclass(frozen=True, slots=True)
class Context:
    workspace_id: str
    tenant_id: str
    user_id: str | None = None
    actor_id: str | None = None
    actor_role_at_decision: str | None = None
```

- `system_context()` solo para bootstrap: crear/listar workspaces, health, seed.
- `Context(workspace_id=...)` para todo acceso a datos de workspace.
- `require_scoped_workspace()` falla si `workspace_id == SYSTEM_WORKSPACE_ID` o está vacío.
- `require_tenant()` falla si `tenant_id` está vacío.
- `enforce_tenant_scoped(ctx)` aplica ambas validaciones y debe llamarse al inicio de todo helper de escritura/lectura de datos de workspace.

---

## 3. Enforcement en SQLite (E2-0)

### Helpers blindados

Los siguientes helpers llaman `enforce_tenant_scoped(ctx)` al inicio:

- `app/src/db.py`: `create_chat`, `create_routine`, `create_routine_run`, `create_mail_message`.
- `app/src/kb.py`: `ingest_kb_source`.

### Tests de regresión

`app/tests/test_e2_0_context_enforcement.py` falla si:

- Se usa `system_context()` para crear datos de workspace.
- Se omite `tenant_id`.
- Se omite `workspace_id`.

---

## 4. RLS en Postgres (E2-1)

### Usuario de aplicación

- Usuario Postgres: `faberloom_app`.
- Permisos: `CONNECT`, `USAGE` en schema `public`, `SELECT/INSERT/UPDATE/DELETE` sobre tablas de aplicación.
- **NO** debe tener `CREATE TABLE`, `DROP TABLE`, `BYPASS RLS`, ni ser `SUPERUSER`.
- Migraciones se ejecutan con un usuario administrador separado (`faberloom_migrator`).

### Políticas base por tabla

Cada tabla workspace-owned tendrá una política `tenant_workspace_policy`:

```sql
CREATE POLICY tenant_workspace_policy ON <table>
    USING (tenant_id = current_setting('app.current_tenant')::TEXT
           AND workspace_id = current_setting('app.current_workspace')::TEXT);
```

Para operaciones de sistema (listar workspaces, bootstrap), el backend usará:

```sql
SET LOCAL app.current_tenant = '__system__';
SET LOCAL app.current_workspace = '__system__';
```

### Tablas con RLS obligatorio

- `workspace` (por `tenant_id`)
- `kb_source`, `kb_chunk`, `kb_fact`
- `chat`, `message`, `draft`
- `routine`, `routine_run`, `gold_candidate`
- `usage_record`
- `mail_message`, `mail_outbox`, `email_account`
- `audit_log`
- `editorial_history`
- `workspace_smtp_config`

### Tablas globales / sin RLS

- `refresh_tokens` (por `user_id`, con índice; no filtrado por tenant porque pertenecen a la instancia).
- `_schema_version`, `_workspace_seal_backup` (metadatos de migración).

---

## 5. Gate E2-1

Antes de declarar E2-1 cerrado:

1. Migración SQLite → Postgres ejecutada y conteos verificados.
2. Usuario `faberloom_app` creado sin `BYPASS RLS`.
3. `SET ROLE faberloom_app` ejecutado; las queries sin `app.current_tenant`/`app.current_workspace` correctos devuelven 0 filas.
4. Tests `test_tenant_contamination.py`, `test_e2_0_canary_tenant.py`, `test_e2_3_canary_gate.py` pasan contra Postgres.
5. Rollback smoke test documentado y probado.

---

## 6. Gate E2-3

- M16 MWT↔canario verde en ambias direcciones.
- Un usuario con rol `viewer` no puede escribir en tablas workspace-owned.
- `actor_role_at_decision` se registra en acciones sensibles.

---

## 7. Referencias

- `app/src/context.py`
- `app/src/db.py`
- `app/src/kb.py`
- `app/tests/test_e2_0_context_enforcement.py`
- `app/tests/test_tenant_contamination.py`
- `app/tests/test_e2_0_canary_tenant.py`
- `app/tests/test_e2_3_canary_gate.py`
- `app/scripts/sqlite_to_postgres.py`
- `docs/MIGRACION_POSTGRES_E2.md`
