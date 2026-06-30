---
id: SPEC_SPACELOOM_SL1b
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE — 2026-06-30 — cierre formal de SL1b (primer draft real + HITL)
aplica_a: [FaberLoom, MWT]
relacionado:
  - PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md
  - SPEC_SPACELOOM_ETAPA1_v1.md
  - IDX_SPACELOOM_ETAPA1_v1.md
---

# SPEC_SPACELOOM_SL1b_v1 — Primer draft real + HITL

## Objetivo

Generar un draft real contra una mini-KB de MWT, con HITL mínimo (aprobar/editar/rechazar), cálculo de `edit_pct` y trazabilidad de fuentes.

## Definition of Done

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | HITL mínimo con `edit_pct` | ✅ | `_edit_pct()` con `difflib.SequenceMatcher`; `DraftRead` expone `original_body_md` y `edit_pct`. |
| 2 | Cita inválida bloqueada | ✅ | `[S9]` desconocido genera blocker en `test_unknown_source_label_in_body_is_blocked`. |
| 3 | `stale_data_block` | ✅ | Facts vencidos o sin fecha/version bloquean el draft. |
| 4 | Harness ≥10 drafts | ✅ | `test_sl1b_dogfood_ten_drafts.py` genera 10 drafts aprobados y escribe `SL1b_DOGFOOD_LOG.json`. |
| 5 | Suite SL1b verde | ✅ | `test_sl1b_kb_drafts.py` 29 passed. |
| 6 | Métricas reportadas | ✅ | Promedio `edit_pct` = 3.66%; 8 fully sourced, 2 con `[PENDIENTE — NO INVENTAR]`. |

## Métricas del dogfood

| Métrica | Valor |
|---|---|
| Drafts generados | 10 |
| Aprobados | 10 |
| Fully sourced | 8 |
| Con `[PENDIENTE — NO INVENTAR]` | 2 |
| `edit_pct` promedio | 3.66% |
| `edit_pct` máximo | 12.42% |
| `edit_pct` mínimo | 0.0% |

## Resultados de test

```text
pytest app/tests/test_sl1b_kb_drafts.py -q
29 passed, 1 warning

pytest app/tests -q
164 passed, 1 warning
```

## Archivos clave

- `app/src/models.py` (schema v14, `DraftRead`)
- `app/src/kb.py` (`_edit_pct()`, `approve_draft`)
- `app/src/api.py` (pasa `original_body_md` en generación)
- `app/tests/test_sl1b_kb_drafts.py`
- `app/tests/test_sl1b_dogfood_ten_drafts.py`
- `harness/reports/SL1b_DOGFOOD_LOG.json`

## Datos de demo

- `docs/IDX_COMERCIAL.md`
- `docs/ENT_COMERCIAL_PRODUCTOS.md`
- `docs/ENT_COMERCIAL_PRECIOS.md`
- `docs/ENT_COMERCIAL_STOCK.md`
- `docs/ENT_COMERCIAL_EQUIVALENCIAS.md`
- `docs/ENT_COMERCIAL_TERMINOS.md`
- `docs/ENT_COMERCIAL_RESUMEN_DEMO.csv`

## Bloqueantes documentados

- PRC-01: Datos comerciales reales de MWT — Abierto (CEO).
- SL2a: Pack MWT real ingestado y validado — Bloqueado.

## Próximo hito

SL2 — Workspaces + KB.

## Changelog

- v1.0 (2026-06-30): Cierre formal de SL1b a partir de `harness/reports/SL1b_CLOSER_REPORT_v1.md`.
