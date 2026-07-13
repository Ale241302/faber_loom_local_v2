# ENT_FB_SKILL_CATALOG_v1.2 — Catálogo sin huecos de definición

**Fecha:** 2026-07-13  
**Baseline:** v1.1 (13 legacy skills) + skills v2 del pipeline E3-4 (PACK 1 FE, PACK 3 CO, etc.).  
**Política:** todo skill tiene un veredicto terminal (`DEFINIDO-SHADOW`, `MIGRADO-SHADOW`, `DEPRECATED`, `DESCARTADO` o `POSPUESTO` con razón + fecha). **Cero `DEFINITION_PENDING`.**

## Changelog v1.1 → v1.2

- Se mantiene el estado de todos los skills legacy de v1.1.
- Se añaden los skills de PACK 2 (comex, prefijo `SKILL_CX_`) con veredicto `POSPUESTO`.
- **Razón del pospuesto:** KB H3 (Marluvas/Tecmater) aún no ha sido entregada por el CEO; sin esa fuente primaria no se pueden definir golden cases honestos ni validar el dominio aduanero.
- **Fecha de revisión del pospuesto:** 2026-08-15 (o en cuanto llegue H3, lo que ocurra primero).

## Estado de los legacy skills

| ID | Nombre | Veredicto v1.2 | Ubicación | Notas |
|---|---|---|---|---|
| SKILL_AMAZON_OPS | Amazon Ops Specialist | MIGRADO-SHADOW | `faberloom/SKILL_AMAZON_OPS.md` | Archetype `generator`; output externo con HITL. |
| SKILL_CLIENT_SERVICE | Servicio Cliente B2B | MIGRADO-SHADOW | `faberloom/SKILL_CLIENT_SERVICE.md` | Archetype `generator`; output externo con HITL. |
| SKILL_COMPLIANCE_CHECKER | Validador Compliance | MIGRADO-SHADOW | `faberloom/SKILL_COMPLIANCE_CHECKER.md` | Archetype `validator`; output externo con HITL. |
| SKILL_COPY | Copywriter Amazon & Brand Content | MIGRADO-SHADOW | `faberloom/SKILL_COPY.md` | Archetype `generator`; output externo con HITL. |
| SKILL_DEMAND_FORECASTER | Demand Forecasting B2B | MIGRADO-SHADOW | `faberloom/SKILL_DEMAND_FORECASTER.md` | Archetype `generator`; output externo con HITL. |
| SKILL_EXPERIMENT_RUNNER | A/B Testing Amazon | MIGRADO-SHADOW | `faberloom/SKILL_EXPERIMENT_RUNNER.md` | Archetype `generator`; output externo con HITL. |
| SKILL_HUMANIZE_BRAND | Voz de Marca MWT.one | MIGRADO-SHADOW | `faberloom/SKILL_HUMANIZE_BRAND.md` | Archetype `generator`; output externo con HITL. |
| SKILL_HUMANIZE_COMMS | Voz Personal del CEO | MIGRADO-SHADOW | `faberloom/SKILL_HUMANIZE_COMMS.md` | Archetype `generator`; output externo con HITL. |
| SKILL_KB_AUDITOR | Auditor KB | MIGRADO-SHADOW | `faberloom/SKILL_KB_AUDITOR.md` | Archetype `validator`; output externo con HITL. |
| SKILL_KB_GATEWAY | Gateway transaccional KB | MIGRADO-SHADOW | `faberloom/SKILL_KB_GATEWAY.md` | Archetype `validator`; output externo con HITL. |
| SKILL_PROFORMA_BUILDER | Constructor de Proformas | MIGRADO-SHADOW | `faberloom/SKILL_PROFORMA_BUILDER.md` | Archetype `generator`; output externo con HITL. |
| SKILL_FRONTEND_PRINCIPLES_MWT | Lente cognitiva frontend | DEPRECATED | — | No es un skill ejecutable; referencia histórica. |
| SKILL_RUNTIME | Dashboard de Estado de Skills | DEPRECATED | — | Esquema / referencia de gobernanza; no ejecutable. |

## Skills v2 definidos en pipeline E3-4

Los siguientes skills ya fueron materializados por el pipeline del compilador v2 y se encuentran en estado `SHADOW`:

- PACK 1 (fiscalidad): `SKILL_FE_*`
- PACK 3 (cobranza): `SKILL_CO_*`
- Otros dominios operativos: `SKILL_BO_*`, `SKILL_CM_*`, `SKILL_FI_*`, `SKILL_GE_*`, `SKILL_HR_*`, `SKILL_LG_*`, `SKILL_MK_*`, `SKILL_OP_*`, `SKILL_PL_*`, `SKILL_SV_*`, `SKILL_TR_*`, `SKILL_WA_*`.

Todos ellos cumplen:
- `metadata.fbl.type = agent`.
- `budget.kill_switch.enabled = true`.
- `learning_consolidation.auto_apply = false`.
- Outputs externos con `requires_human_approval: true`.
- `golden_samples` honestos (`[PENDIENTE — NO INVENTAR]` donde aplica).

## PACK 2 (comex) — pospuesto por ausencia de H3

| ID | Nombre | Veredicto v1.2 | Razón | Revisión |
|---|---|---|---|---|
| SKILL_CX_DISPUTE_PACK | Dispute Pack Comex | POSPUESTO | Falta KB H3 (Marluvas/Tecmater) para validar disputas aduaneras reales. | 2026-08-15 |
| SKILL_CX_DOC_COMPLETENESS | Document Completeness Comex | POSPUESTO | Falta KB H3 para definir checklist documental por país/producto. | 2026-08-15 |
| SKILL_CX_DUTY_CALC | Duty Calculation Comex | POSPUESTO | Falta KB H3 para aranceles/impuestos reales. | 2026-08-15 |
| SKILL_CX_EMBARQUE_TRACK | Embarque Tracking Comex | POSPUESTO | Falta KB H3 para rutas y estados de embarque. | 2026-08-15 |
| SKILL_CX_HS_CLASSIFY | HS Classification Comex | POSPUESTO | Falta KB H3 para partidas arancelarias reales. | 2026-08-15 |
| SKILL_CX_LANDED_COST | Landed Cost Comex | POSPUESTO | Falta KB H3 para costos logísticos reales. | 2026-08-15 |
| SKILL_CX_ORIGIN_CHECK | Origin Check Comex | POSPUESTO | Falta KB H3 para reglas de origen. | 2026-08-15 |
| SKILL_CX_PEDIMENTO_CROSSCHECK | Pedimento Crosscheck Comex | POSPUESTO | Falta KB H3 para pedimentos/modelos de aduana. | 2026-08-15 |
| SKILL_CX_REG_WATCH | Regulatory Watch Comex | POSPUESTO | Falta KB H3 para regulaciones vigentes por país. | 2026-08-15 |
| SKILL_CX_REQUISITOS_PREVIOS | Requisitos Previos Comex | POSPUESTO | Falta KB H3 para permisos/requisitos por producto. | 2026-08-15 |

## Reglas no negociables aplicables a todo el catálogo

- Ningún skill nuevo puede quedar en estado `ACTIVE` sin golden cases `approved + verified` y track record ≥100 runs / ≥90% acceptance.
- `learning_consolidation.auto_apply = false` siempre.
- `verified_by != approved_by` para golden cases (segundo gate).
- No se inventan datos de dominio; los `golden_samples` se completan solo desde runs reales vía harvester.

## DoD de cierre de catálogo v1.2

- [x] Cada skill del catálogo tiene un veredicto terminal o `POSPUESTO` con razón + fecha.
- [x] Cero skills en `DEFINITION_PENDING` sin veredicto.
- [ ] KB H3 cargada y ≥3 golden candidates reales de PACK 2 (bloqueado por entrega de CEO).
- [ ] Skills `DEFINIDO-SHADOW` materializados en SHADOW (cuando H3 llegue).
- [x] Test `test_e5_3_catalog_v12.py` verde.
