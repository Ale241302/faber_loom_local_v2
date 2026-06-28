# Plan SL1b CLOSER — v1

**Fecha:** 2026-06-25
**Loop:** §5 AUDIT → PLAN → IMPLEMENT → TEST → GATE → reporte
**Scope:** cerrar SL1b con la DoD corregida por el usuario.

## DoD objetivo

1. HITL mínimo real con `edit_pct` calculado del diff aprobado vs draft original.
2. Test de cita inválida bloqueada.
3. `stale_data_block` (ya implementado; se verifica).
4. Harness de dogfood con ≥10 drafts logueados.
5. `test_sl1b_kb_drafts.py` verde.
6. Reporte con `fully_sourced` vs `[PENDIENTE]` y `edit_pct` promedio.

## Cambios técnicos

### 1. Schema v14 — columnas `draft.original_body_md` y `draft.edit_pct`

- `app/src/models.py`: `SCHEMA_VERSION = 14`, migración v14, campos en `DraftRead`.
- `app/src/kb.py`: `insert_draft`/`update_draft`/`approve_draft`/`export_draft` propagan los nuevos campos; `approve_draft` calcula `edit_pct` con `difflib.SequenceMatcher`.
- `app/src/api.py`: `api_generate_draft` pasa `original_body_md`.

### 2. Test de cita inválida

- Añadir `test_unknown_source_label_in_body_is_blocked` en `app/tests/test_sl1b_kb_drafts.py`.
- La funcionalidad ya existe en `draft_engine._validate_citations`; solo falta cobertura SL1b.

### 3. Harness de 10 drafts

- Crear `harness/prompts/sl1b_dogfood_prompts.json` con 10 prompts fijos contra datos demo.
- Crear `docs/IDX_COMERCIAL.md` + `docs/ENT_COMERCIAL_*.md` con fuentes demo explícitas (fallback `[PENDIENTE — NO INVENTAR]`; PRC-01 sigue abierto).
- Crear `app/tests/test_sl1b_dogfood_ten_drafts.py`:
  - Ingiere KB demo.
  - Genera 10 drafts con fake provider.
  - Edita algunos drafts.
  - Aprueba/exporta los viables.
  - Loguea `harness/reports/SL1b_DOGFOOD_LOG.json` con `fully_sourced`, `edit_pct`, pendientes.

### 4. Reporte CLOSER

- `harness/reports/SL1b_CLOSER_REPORT_v1.md` con métricas finales.

## Restricciones

- No tocar `ENT_OPS_STATE_MACHINE` ni `PLB_ORCHESTRATOR`.
- No avanzar a SL2a (sigue bloqueado por pack MWT real + decisiones CEO).
