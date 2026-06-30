---
id: SPEC_SPACELOOM_SL0
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE — 2026-06-30 — cierre formal de SL0 (esqueleto + seed)
aplica_a: [FaberLoom, MWT]
relacionado:
  - PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md
  - SPEC_SPACELOOM_ETAPA1_v1.md
  - IDX_SPACELOOM_ETAPA1_v1.md
---

# SPEC_SPACELOOM_SL0_v1 — Esqueleto + seed

## Objetivo

Levantar la app de escritorio single-user con un modelo de datos base, un workspace de prueba con datos semilla, y las costuras contract-first que permitan escalar a Etapa 2-3 sin reescribir.

## Definition of Done

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | App vacía corre (FastAPI + pywebview) | ✅ | `main.py` levanta lifespan, sirve shell estático, abre ventana desktop. |
| 2 | 1 workspace de prueba + datos semilla | ✅ | `seed.py` crea `MWT Demo` (`mwt-demo`) de forma idempotente. |
| 3 | Modelo de datos base versionado | ✅ | Schema v2 con `workspace`, `kb_source`, `chat`, `message`, `draft`, `audit_log`, `routine`, `routine_run`. |
| 4 | Costuras contract-first | ✅ | Campos latentes (`tenant_id`, `actor_id`, `actor_role_at_decision`, `routine_version`, `skill_version`, `schema_version`, `source_version`, `approved_by`) en tablas requeridas. |
| 5 | Contexto de seguridad | ✅ | `Context(workspace_id, tenant_id, user_id, actor_id, actor_role_at_decision)` y `system_context()` vs `require_scoped_workspace()`. |
| 6 | AuditWriter inicial | ✅ | Escritura a `audit_log` + espejo a `audit.jsonl`. |
| 7 | UI honesta | ✅ | Composer inerte con mensaje "SL0 solo de muestra"; placeholders para vistas futuras. |

## Resultados de test

```text
pytest app/tests -q
6 passed (suite SL0), 1 warning
```

Tests clave:
- `test_health_and_seed_workspace`
- `test_seed_is_idempotent`
- `test_schema_contains_contract_tables_and_latent_fields`
- `test_context_tenant_scope_is_applied_to_workspace_reads`
- `test_create_workspace_unique_slug_and_audit`

## Archivos clave

- `app/src/main.py`
- `app/src/seed.py`
- `app/src/models.py`
- `app/src/db.py`
- `app/src/context.py`
- `app/src/audit.py`
- `app/static/index.html`, `app/static/js/app.jsx`

## Riesgos P0

Ninguno activo en SL0: no hay acciones irreversibles, no ingesta de contenido externo, no fuga cross-workspace (scoping aplicado).

## Próximo hito

SL1a — Router mínimo + chat.

## Changelog

- v1.0 (2026-06-30): Cierre formal de SL0 a partir de `harness/reports/SL0_final_eval.md`.
