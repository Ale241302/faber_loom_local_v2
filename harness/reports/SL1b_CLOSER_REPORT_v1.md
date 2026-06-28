# SL1b CLOSER — Reporte de cierre v1

**Fecha:** 2026-06-25  
**Loop ejecutado:** §5 AUDIT → PLAN → IMPLEMENT → TEST → GATE → reporte  
**Auditor técnico previo:** fugu (`AUDIT_SL1b_FUGU_v3.md` PASS formal)  
**Scope:** cerrar SL1b con la DoD corregida por el usuario.

---

## DoD SL1b — Verificación

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | HITL mínimo real con `edit_pct` calculado del diff aprobado vs draft original | ✅ | `app/src/kb.py` schema v14 + `_edit_pct()` con `difflib.SequenceMatcher`; `DraftRead` expone `original_body_md` y `edit_pct`; tests `test_edit_pct_is_calculated_on_approval` y dogfood log con promedio. |
| 2 | Test de cita inválida bloqueada | ✅ | `test_unknown_source_label_in_body_is_blocked` en `app/tests/test_sl1b_kb_drafts.py`; `[S9]` desconocido genera blocker. |
| 3 | `stale_data_block` | ✅ | Cubierto por `test_stale_fact_marks_requires_confirmation` y `test_fact_not_yet_valid_is_blocked` (preexistentes, verdes). |
| 4 | Harness de ≥10 drafts logueados | ✅ | `app/tests/test_sl1b_dogfood_ten_drafts.py` genera 10 drafts aprobados y escribe `harness/reports/SL1b_DOGFOOD_LOG.json`. |
| 5 | `test_sl1b_kb_drafts.py` verde | ✅ | 29 passed. |
| 6 | Reporte con `fully_sourced` vs `[PENDIENTE]` y `edit_pct` promedio | ✅ | Este reporte + `SL1b_DOGFOOD_LOG.json`. |

---

## Métricas del dogfood SL1b

Fuente: `harness/reports/SL1b_DOGFOOD_LOG.json`

| Métrica | Valor |
|---|---|
| Drafts generados | 10 |
| Aprobados | 10 |
| Fully sourced | 8 |
| Con `[PENDIENTE — NO INVENTAR]` | 2 |
| `edit_pct` promedio | 3.66% |
| `edit_pct` máximo | 12.42% (heavy edit) |
| `edit_pct` mínimo | 0.0% (sin edit) |

---

## Cambios realizados

### Código
- `app/src/models.py`: migración v14 (`draft.original_body_md`, `draft.edit_pct`); campos en `DraftRead`.
- `app/src/kb.py`: cálculo de `edit_pct` en `approve_draft`; preservación de `original_body_md` en `insert_draft`/`update_draft`.
- `app/src/api.py`: pasa `original_body_md` en generación de drafts y replies de mail.

### Tests
- `app/tests/test_sl1b_kb_drafts.py`: +2 tests (`edit_pct`, cita inválida).
- `app/tests/test_sl1b_dogfood_ten_drafts.py`: harness de 10 drafts.

### Documentación / KB demo
- `docs/IDX_COMERCIAL.md`
- `docs/ENT_COMERCIAL_PRODUCTOS.md`
- `docs/ENT_COMERCIAL_PRECIOS.md`
- `docs/ENT_COMERCIAL_STOCK.md`
- `docs/ENT_COMERCIAL_EQUIVALENCIAS.md`
- `docs/ENT_COMERCIAL_TERMINOS.md`
- `docs/ENT_COMERCIAL_RESUMEN_DEMO.csv`
- `harness/prompts/sl1b_dogfood_prompts.json`

### Plan / reportes
- `harness/reports/PLAN_SL1b_CLOSER_v1.md`
- `harness/reports/SL1b_DOGFOOD_LOG.json`
- `harness/reports/SL1b_CLOSER_REPORT_v1.md`

---

## Resultado de tests

```
pytest app/tests -q
164 passed, 1 warning in 51.33s
```

---

## Restricciones respetadas

- No se tocó `ENT_OPS_STATE_MACHINE` ni `PLB_ORCHESTRATOR`.
- No se avanzó a SL2a (sigue bloqueado por pack MWT real + decisiones CEO).

---

## Bloqueantes y deuda documentada

| ID | Ítem | Estado | Quién actúa |
|---|---|---|---|
| PRC-01 | Datos comerciales reales de MWT | Abierto | CEO (Alvaro) |
| SL2a | Pack MWT real ingestado y validado | Bloqueado | CEO + dev |
| SL2a | Decisiones CEO documentadas (scope, licencia, calendario, cifrado, etc.) | Bloqueado | CEO |

---

## Veredicto

**SL1b queda CERRADO técnicamente** bajo el CLOSER loop con fallback demo explícito. El paso a SL2a requiere el pack MWT real y las decisiones CEO pendientes.
