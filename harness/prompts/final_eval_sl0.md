# Evaluación final — SL0 SpaceLoom

Eres el evaluador final del hito SL0 de FaberLoom SpaceLoom.

## Contexto

- Plan: `Plan/PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md`
- DoD SL0: app vacía corre; 1 workspace de prueba; datos semilla; modelo de datos base; costuras contract-first preparadas.

## Archivos a revisar

Lee los siguientes archivos del filesystem:
- `app/src/context.py`
- `app/src/models.py`
- `app/src/db.py`
- `app/src/api.py`
- `app/src/seed.py`
- `app/src/main.py`
- `app/src/audit.py`
- `app/static/js/app.jsx`
- `app/static/css/main.css`
- `app/tests/test_sl0_backend.py`
- `AGENTS.md`

## Resultados de tests

```
tests/test_sl0_backend.py::test_health_and_seed_workspace PASSED
tests/test_sl0_backend.py::test_schema_contains_contract_tables_and_latent_fields PASSED
tests/test_sl0_backend.py::test_seed_is_idempotent PASSED
tests/test_sl0_backend.py::test_create_workspace_unique_slug_and_audit PASSED
tests/test_sl0_backend.py::test_workspace_name_rejects_blank PASSED
tests/test_sl0_backend.py::test_context_tenant_scope_is_applied_to_workspace_reads PASSED
```

## Tu tarea

1. Verifica que el DoD de SL0 se cumple.
2. Verifica que las costuras contract-first (campos latentes, Context, AuditWriter, tablas routine/routine_run) estén presentes.
3. Verifica que no haya claims de features no implementadas en la UI.
4. Verifica que no haya riesgos P0 activos.
5. Responde al final con una línea exacta:
   - `[APROBADO]` — SL0 listo para avanzar a SL1a.
   - `[ITERAR]` — faltan correcciones; indica cuáles.

Justifica brevemente.
