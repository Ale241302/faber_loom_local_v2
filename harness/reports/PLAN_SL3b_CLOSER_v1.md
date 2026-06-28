# Plan SL3b/c CLOSER — v1 (CERRADO)

**Fecha:** 2026-06-25  
**Loop:** §5 AUDIT → PLAN → IMPLEMENT → TEST → GATE → REPORTE  
**Reglas:** No inventar. FROZEN (`ENT_OPS_STATE_MACHINE`, `PLB_ORCHESTRATOR`) intactos.

## DoD objetivo

1. WorkLoom funcional: cola por estado/urgencia, aprobar/editar/rechazar + evidence.
2. Capturar `edit_pct` por tipo de tarea (§7.8).
3. Cerrar el gold loop real: feedback aprobado/editado re-alimenta generación; gold candidates capturados.
4. Probar con sesiones sembradas (PRC-03) que `edit_pct` del mismo tipo de tarea desciende con repeticiones.
5. Anti-contaminación (§7.5): campos duros (precio/SKU/stock/margen) requieren segundo gate independiente; test afirmativo de rechazo sin segundo gate.
6. Multi-tenant: evidence/gold con scope por tenant.
7. Tests `test_sl3b_workloom_gold.py` verdes + test declinante + test segundo gate.
8. Gate §6 completo y reporte §8.

## Cambios técnicos

### 1. Schema v16 — métricas por tarea y tenant scope en gold

- `app/src/models.py`:
  - `SCHEMA_VERSION = 16`.
  - Migración v16 agrega `tenant_id` a `gold_candidate` y `task_type` a `routine_run`.
  - Actualiza `GoldCandidateRead` y `RoutineRunRead` para exponer los nuevos campos.

### 2. `edit_pct` tipificado por tarea

- `app/src/db.py`:
  - `create_routine_run()` infiere `task_type` desde `routine.category` si no se provee.
  - `ROUTINE_RUN_COLUMNS` incluye `task_type`.
- `app/src/api.py`:
  - `_execute_skill_run()` siempre persiste `task_type=routine.get("category")` en el run.

### 3. Gold loop real (re-feed a generación)

- `app/src/gold.py`:
  - `list_approved_gold_candidates_for_routine()` devuelve gold aprobadas de una routine.
- `app/src/api.py`:
  - `_inject_gold_examples_into_skill()` append las approved gold como few-shot examples al prompt.
  - `_execute_skill_run()` inyecta los ejemplos antes de llamar al LLM.
- `apply_gold_to_routine()` mantiene el shallow-merge de `schema_output_json` como mecanismo de retroalimentación estructural.

### 4. Anti-contaminación: segundo gate para campos duros

- `app/src/gold.py`:
  - `promote_gold_candidate()` detecta valores duros (precio/SKU/stock/margen/fechas) usando `_extract_hard_tokens()` de `draft_engine`.
  - Si `learned_output_json` contiene campos duros, exige `verified_by`; de lo contrario lanza `ValueError`.
- `app/src/api.py`:
  - `PromoteGoldCandidateRequest` acepta `verified_by` opcional.
  - `api_promote_gold_candidate()` convierte el `ValueError` en `422 Unprocessable Entity`.

### 5. Multi-tenant evidence/gold

- `app/src/db.py`:
  - `_upsert_gold_candidate_from_run()` persiste `tenant_id` desde el run.
- `app/src/gold.py`:
  - `list_gold_candidates()`, `list_approved_gold_candidates_for_routine()`, `promote_gold_candidate()` y `apply_gold_to_routine()` filtran por `(workspace_id, tenant_id)`.
- `app/src/workloom.py`:
  - `list_workloom_items()` filtra runs, drafts y gold candidates por `tenant_id`.

### 6. Tests SL3b/c

- `app/tests/test_sl3b_workloom_gold.py`:
  - `test_task_type_is_captured_on_routine_run`
  - `test_edit_pct_declines_with_repetitions_by_task_type`
  - `test_hard_field_gold_requires_second_gate`
  - `test_gold_candidate_tenant_isolation`
  - `test_gold_refeed_appends_approved_examples_to_skill_prompt`
  - Se actualiza `test_gold_candidates_endpoint_and_promote` para incluir `verified_by` en campos duros.

## Resultados de test esperados

```text
pytest app/tests/test_sl3b_workloom_gold.py -q  → 19 passed, 1 warning
pytest app/tests -q                               → 185 passed, 1 warning
```

Baseline SL3a: `180 passed`. Incremento neto: **+5 tests**.

## Archivos modificados

- `app/src/models.py` — schema v16, Pydantic models.
- `app/src/db.py` — `task_type`, `tenant_id` en gold, inferencia de categoría.
- `app/src/gold.py` — segundo gate, tenant scope, helper de approved candidates.
- `app/src/api.py` — re-feed de gold, `verified_by`, captura de errores.
- `app/src/workloom.py` — tenant scope en cola HITL.
- `app/tests/test_sl3b_workloom_gold.py` — tests de cierre SL3b/c.
- `harness/reports/PLAN_SL3b_CLOSER_v1.md` — este plan.
- `harness/reports/SL3b_CLOSER_REPORT_v1.md` — reporte de cierre §8.

## Restricciones respetadas

- `ENT_OPS_STATE_MACHINE` y `PLB_ORCHESTRATOR` no modificados.
- No se inventaron datos MWT reales.
