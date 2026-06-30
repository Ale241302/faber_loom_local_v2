---
id: SPEC_SPACELOOM_SL3bc
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE — 2026-06-30 — cierre formal de SL3b/c (WorkLoom + gold loop)
aplica_a: [FaberLoom, MWT]
relacionado:
  - PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md
  - SPEC_SPACELOOM_ETAPA1_v1.md
  - IDX_SPACELOOM_ETAPA1_v1.md
---

# SPEC_SPACELOOM_SL3bc_v1 — WorkLoom + gold loop

## Objetivo

Construir la mesa de trabajo (WorkLoom) con cola de items por estado/urgencia, capturar `edit_pct` por tipo de tarea, e implementar el gold loop con anti-contaminación para campos duros.

## Definition of Done

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | WorkLoom queue | ✅ | `list_workloom_items()` filtra y ordena por `urgency DESC, created_at DESC`. |
| 2 | `edit_pct` por tipo de tarea | ✅ | Schema v16 agrega `task_type` en `routine_run`; captura automática por categoría. |
| 3 | Gold candidates | ✅ | Aprobación con `edit_pct <= 0.2` crea/actualiza `gold_candidate`. |
| 4 | Promoción/aplicación de gold | ✅ | `promote_gold_candidate()` + `apply_gold_to_routine()` enriquecen `schema_output_json`. |
| 5 | Re-feed a generación | ✅ | `_inject_gold_examples_into_skill()` agrega few-shots al prompt. |
| 6 | Evidencia de descenso de `edit_pct` | ✅ | `test_edit_pct_declines_with_repetitions_by_task_type`. |
| 7 | Segundo gate para campos duros | ✅ | `promote_gold_candidate()` rechaza campos duros sin `verified_by`. |
| 8 | Tenant isolation | ✅ | `test_gold_candidate_tenant_isolation`. |
| 9 | Tests | ✅ | 19 passed (SL3b/c); suite total 185 passed. |

## Resultados de test

```text
pytest app/tests/test_sl3b_workloom_gold.py -q
19 passed, 1 warning

pytest app/tests -q
185 passed, 1 warning
```

## Archivos clave

- `app/src/models.py` (schema v16)
- `app/src/db.py` (`task_type`, tenant en gold)
- `app/src/gold.py` (segundo gate, tenant scope, approved candidates)
- `app/src/workloom.py` (cola HITL)
- `app/src/api.py` (re-feed de gold, `verified_by`)
- `app/tests/test_sl3b_workloom_gold.py`
- `harness/reports/PLAN_SL3b_CLOSER_v1.md`

## Próximo hito

SL3.5 — Sellado + llave graduada.

## Changelog

- v1.0 (2026-06-30): Cierre formal de SL3b/c a partir de `harness/reports/SL3b_CLOSER_REPORT_v1.md`.
