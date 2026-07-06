# Cierre E2-0 — Activar costuras + higiene E1

**Fecha:** 2026-07-06  
**Estado:** ✅ CERRADO  
**Suite:** `323 passed, 8 warnings` (188.19 s)  
**Schema DB:** v24  
**Knowledge graph:** 25.702 nodos / 34.813 edges / 1.707 comunidades

---

## 1. Objetivo

Cerrar el hito **E2-0 "Activar costuras + higiene E1"** dejando las líneas transversales listas para que E2-1 (producción/despacho) y E2-2 (Foundation Beta ↔ main app) arranquen sobre una base contract-first, auditada y con tenant aislado.

---

## 2. Entregables cerrados

### Bloque 1 — Auth/Context unificado
- `app/src/auth.py`: JWT legacy enriquecido desde Foundation Beta (`tenant_id`, `user_id`, `role`).
- `app/src/context.py`: `Context` ahora expone `resolved_actor_id()` y `actor_role_at_decision`; nuevo `enforce_tenant_scoped(ctx)` fail-closed.
- `approved_by` se resuelve desde `ctx.resolved_actor_id()`, no desde query params.
- Tests: `app/tests/test_e2_0_auth_context.py`.

### Bloque 2 — Audit correlation
- Migración v22: `audit_log.correlation_id`.
- `AuditEvent`, `AuditWriter.write` y eventos de routine/run/gold propagan `correlation_id`.
- Tests: `app/tests/test_e2_0_audit_correlation.py`.

### Bloque 3 — Tenant canario permanente
- Migración v23: `workspace.is_canary`.
- `app/src/seed.py`: `seed_canary_workspace()` crea workspace canario (`tenant_id='canary'`, `is_canary=1`).
- Gate preparado para E2-3; tests: `app/tests/test_e2_0_canary_tenant.py`, `app/tests/test_e2_3_canary_gate.py`.

### Bloque 4 — Migración Postgres
- `app/scripts/sqlite_to_postgres.py`: migración con dry-run y validación de schema.
- `docker-compose.yml`: servicio `postgres` para entornos con Docker.
- `.env.example`: variables `DATABASE_URL`, `POSTGRES_*`.
- `docs/MIGRACION_POSTGRES_E2.md`: runbook paso a paso.
- `app/scripts/postgres_rls_policies.sql`: políticas RLS iniciales por `tenant_id` / `workspace_id`.
- Tests: `app/tests/test_e2_0_postgres_migration.py` (dry-run; Postgres real no disponible en este entorno).

### Bloque 5 — Higiene E1
- `LICENSE`: FSL-1.1-ALv2.
- `docs/LESSONS_LEARNED_E1.md`.
- `Plan/PROMOCION_SPIKE_E2_BASE.md`.
- `harness/prompts/sl1b_dogfood_prompts.json` versionado.

### Bloque 6 — Auth/session convergencia
- Nuevo endpoint `GET /api/me` → `UserRead`.
- Frontend (`app/static/js/app.jsx`) usa cookie HttpOnly; eliminado uso de `localStorage.faberloom_token`.
- Documento: `docs/AUTH_SESSION_CONVERGENCIA_E2.md`.
- Tests: `app/tests/test_e2_0_auth_me.py`.

### Bloque 7 — Context/RLS enforcement
- Helpers críticos blindados: `create_chat`, `create_routine`, `create_routine_run`, `create_mail_message`, `ingest_kb_source` llaman `enforce_tenant_scoped(ctx)`.
- Tests adversariales: `app/tests/test_e2_0_context_enforcement.py`.
- Contrato: `docs/CONTEXT_RLS_CONTRACT_E2.md`.

### Bloque 8 — Roles/permisos + segundo gate gold
- Matriz de roles: `docs/ROLES_PERMISSIONS_MATRIX_E2.md`.
- Migración v24: `gold_candidate.verified_by`.
- `app/src/gold.py`: hard fields requieren `verified_by` distinto a `approved_by`.
- Tests: `app/tests/test_e2_0_gold_second_gate.py`.

---

## 3. Resultado de tests

```text
323 passed, 8 warnings in 188.19s (0:03:08)
```

Los 8 warnings son todos por `InsecureKeyLengthWarning` de PyJWT porque `FABERLOOM_SECRET_KEY` en tests es corto (11 bytes). No son bloqueantes para E2-0, pero deben corregirse en E2-2/E2-3 forzando una clave ≥ 32 bytes en CI.

---

## 4. Archivos clave modificados o creados

| Ruta | Tipo | Nota |
|------|------|------|
| `AGENTS.md` | M | Plan vigente E2; costuras contract-first extendidas |
| `app/src/auth.py` | M | Cookie HttpOnly, enriquecimiento Foundation, `/api/me` |
| `app/src/context.py` | M | `enforce_tenant_scoped`, `resolved_actor_id` |
| `app/src/api.py` | M | `GET /api/me`, aprobaciones con Context |
| `app/src/db.py` | M | SCHEMA v24, helpers blindados |
| `app/src/models.py` | M | Migraciones v22/v23/v24, `UserRead`, `GoldCandidateRead.verified_by` |
| `app/src/audit.py` | M | `correlation_id` en eventos |
| `app/src/gold.py` | M | Segundo gate gold |
| `app/src/seed.py` | M | `seed_canary_workspace` |
| `app/src/main.py` | M | Llama seed canario |
| `app/src/kb.py` | M | `ingest_kb_source` blindado |
| `app/static/js/app.jsx` | M | Auth por cookie + `/api/me` |
| `docker-compose.yml` | M | Servicio Postgres |
| `app/scripts/sqlite_to_postgres.py` | N | Migrador |
| `app/scripts/postgres_rls_policies.sql` | N | Políticas RLS |
| `app/tests/test_e2_0_*.py` | N | 8 archivos de tests E2-0 |
| `docs/AUTH_SESSION_CONVERGENCIA_E2.md` | N | |
| `docs/CONTEXT_RLS_CONTRACT_E2.md` | N | |
| `docs/MIGRACION_POSTGRES_E2.md` | N | |
| `docs/ROLES_PERMISSIONS_MATRIX_E2.md` | N | |
| `docs/LESSONS_LEARNED_E1.md` | N | |
| `Plan/PROMOCION_SPIKE_E2_BASE.md` | N | |
| `ESTADO_E2_0_CIERRE_20260706.md` | N | Este documento |

---

## 5. Issues activos (no bloqueantes para E2-0)

1. **HMAC key warnings:** 8 warnings por clave JWT corta en tests. Mitigar en E2-2/E2-3 con secret ≥ 32 bytes en `.env` de CI.
2. **Graphify version mismatch:** `skill 0.8.30` vs `package 0.8.49`. No afecta funcionamiento.
3. **Postgres real no probado:** Docker/psql no disponibles localmente; migración validada solo en dry-run. Planificar prueba real en entorno de staging antes de E2-4.
4. **Context enforcement parcial:** helpers críticos blindados; E2-1/E2-3 deben auditar y blindar el resto del repositorio.
5. **Puentes legacy:** `FABERLOOM_USERS` JSON y fallback local siguen activos temporalmente; deben retirarse en E2-2/E2-3.

---

## 6. Próximos pasos recomendados

1. **Auditoría P0 de seguridad** sobre el delta E2-0 antes de arrancar E2-1.
2. **Infra Postgres:** levantar contenedor en staging y ejecutar migración real; validar RLS con usuario `faberloom_app` sin `BYPASS RLS`.
3. **E2-1** arrancar con contratos ya activos: Auth/Context, Audit correlation, Tenant canario, Context/RLS, Roles/permisos.
4. **Corrección warnings JWT** en tests para mantener la suite limpia.
5. **Retirada puentes legacy** (`FABERLOOM_USERS`, fallback local) en E2-2/E2-3.

---

## 7. Verificación final

- [x] Suite completa verde (`323 passed`).
- [x] Knowledge graph actualizado (`graphify update . --force`).
- [x] `AGENTS.md` refleja plan vigente E2 y costuras contract-first extendidas.
- [x] Documentos de arquitectura creados y vinculados.

**E2-0 queda cerrado y listo para promover a E2-1.**
