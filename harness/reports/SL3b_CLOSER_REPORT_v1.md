# Reporte de cierre SL3b/c — v1 (§8)

**Fecha:** 2026-06-25  
**Agente:** Kimi Code CLI  
**Loop CLOSER:** §5 AUDIT → PLAN → IMPLEMENT → TEST → GATE → REPORTE

## Estado

SL3b/c **CERRADO**.

## 1. WorkLoom HITL queue

- **Helper:** `app/src/workloom.py::list_workloom_items()`
- **Filtros:** devuelve `routine_runs` en `requires_hitl|running|failed`, `drafts` en `draft|pending_approval` y `gold_candidates` recientes.
- **Ordenamiento:** por `urgency DESC, created_at DESC`.
- **Tests:**
  - `test_list_workloom_endpoint`
  - `test_list_workloom_helper_orders_and_filters`
  - `test_workloom_sorted_by_urgency`
  - `test_workspace_isolation_for_workloom`

## 2. `edit_pct` por tipo de tarea

- **Schema v16:** columna `task_type` en `routine_run`.
- **Captura automática:** `_execute_skill_run()` graba `task_type = routine.category`.
- **Inferencia:** `create_routine_run()` usa `routine.category` si no se provee `task_type`.
- **Test:** `test_task_type_is_captured_on_routine_run` — una routine `category=skill` genera un run con `task_type="skill"`.

## 3. Gold loop real

### Captura de gold candidates

- Cuando un `routine_run` se aprueba con `edit_pct <= 0.2`, `_upsert_gold_candidate_from_run()` crea/actualiza un `gold_candidate`.
- **Tests:**
  - `test_approve_low_edit_generates_gold_candidate`
  - `test_approve_high_edit_does_not_generate_gold_candidate`

### Promoción y aplicación

- `promote_gold_candidate()` guarda `learned_output_json` y marca `approved=1`.
- `apply_gold_to_routine()` hace shallow-merge del `learned_output_json` en `routine.schema_output_json`.
- **Test:** `test_apply_gold_to_routine_updates_schema` verifica que el schema se enriquece y el candidate queda `used=1`.

### Re-feed a generación

- `_inject_gold_examples_into_skill()` toma las approved gold de la routine y las agrega al prompt como few-shot examples.
- `_execute_skill_run()` invoca la inyección antes de llamar al LLM.
- **Test:** `test_gold_refeed_appends_approved_examples_to_skill_prompt` verifica que el prompt contiene el input y el learned output aprobado.

## 4. Evidencia de descenso de `edit_pct` (PRC-03 seeded)

- **Test:** `test_edit_pct_declines_with_repetitions_by_task_type`
- **Método:** se sembraron 5 runs consecutivos del mismo `task_type="skill"` donde el output del modelo se acerca progresivamente al target aprobado.
- **Resultado:**
  - `edit_pcts` es no-creciente.
  - Las últimas dos repeticiones son idénticas al target (`edit_pct = 0.0`).
  - La primera repetición tiene `edit_pct > 0`.

## 5. Anti-contaminación: segundo gate para campos duros

- **Detección:** `_extract_hard_tokens()` de `draft_engine.py` detecta precios, SKUs, stock, márgenes y fechas.
- **Regla:** `promote_gold_candidate()` rechaza la promoción si `learned_output_json` contiene campos duros y no se provee `verified_by`.
- **API:** `POST /gold-candidates/{id}/promote` devuelve `422` cuando falta el segundo gate.
- **Test:** `test_hard_field_gold_requires_second_gate`
  - Sin `verified_by` → `422`.
  - Con `verified_by="controller"` → `200` y `approved=1`.

## 6. Multi-tenant evidence/gold

- **Schema:** `gold_candidate.tenant_id`.
- **Queries:** todas las operaciones de gold filtran por `(workspace_id, tenant_id)`.
- **WorkLoom:** runs, drafts y gold candidates filtran por tenant.
- **Test:** `test_gold_candidate_tenant_isolation`
  - Un candidate creado en `tenant=t1` es visible desde `tenant=t1`.
  - Desde `tenant=t2` (mismo `workspace_id` forzado) la lista está vacía.

## Resultados de test

```text
pytest app/tests/test_sl3b_workloom_gold.py -q
19 passed, 1 warning

pytest app/tests -q
185 passed, 1 warning
```

Baseline SL3a: `180 passed`.  
Incremento neto: **+5 tests**.

## Archivos clave

- `app/src/models.py` — schema v16 y modelos Pydantic.
- `app/src/db.py` — `task_type`, tenant en gold, inferencia de categoría.
- `app/src/gold.py` — segundo gate, tenant scope, approved candidates.
- `app/src/api.py` — re-feed de gold, `verified_by`, manejo de errores.
- `app/src/workloom.py` — tenant scope en cola HITL.
- `app/tests/test_sl3b_workloom_gold.py` — suite SL3b/c ampliada.
- `harness/reports/PLAN_SL3b_CLOSER_v1.md`
- `harness/reports/SL3b_CLOSER_REPORT_v1.md` — este reporte.

## Restricciones respetadas

- `ENT_OPS_STATE_MACHINE` y `PLB_ORCHESTRATOR` no fueron modificados.
- No se inventaron datos MWT reales.
