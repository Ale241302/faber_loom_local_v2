# ENT_FB_SKILL_CATALOG_v1.1 — Legacy `docs/SKILL_*.md` migration status

**Fecha:** 2026-07-10  
**Baseline:** 13 archivos encontrados en `docs/SKILL_*.md` (corrección del conteo "14" del prompt original).  
**Destino:** `faberloom/SKILL_<ID>.md` con manifest v2 (`metadata.fbl`).  
**Política:** todos los migrables quedan en estado **SHADOW**; ninguno se promueve a ACTIVE sin golden cases aprobados + verified + track record (regla de oro existente).

## Estado de los legacy skills

| ID legacy | Nombre | Estado v1.1 | Ubicación v2 | Razón / notas |
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
| SKILL_FRONTEND_PRINCIPLES_MWT | Lente cognitiva frontend | DEPRECATED | — | No es un skill ejecutable; es referencia de principios. Se mantiene en `docs/` como fuente histórica. |
| SKILL_RUNTIME | Dashboard de Estado de Skills | DEPRECATED | — | Esquema / referencia de gobernanza, no skill ejecutable. Se mantiene en `docs/` como fuente histórica. |

## Reglas de migración aplicadas

- `metadata.fbl.type = agent` para todos los migrables.
- `metadata.fbl.architectural_archetype` y `archetype` dentro de los arquetipos E1 permitidos (`classifier`, `validator`, `generator`, `formatter`, `triage`).
- `budget.kill_switch.enabled = true` declarado explícitamente.
- `learning_consolidation.auto_apply = false` (prohibido por SCH_FB_SKILL_MANIFEST_v2).
- Todo output con `destination` externo lleva `requires_human_approval: true`.
- `golden_samples` dejados como placeholders `[PENDIENTE — NO INVENTAR]`; los skills con arquetipo que no requiere golden cases no los exige, y los que sí requieren deben completarse antes de promoción.

## Discrepancias resueltas vs. el prompt original

- El prompt citaba "14 skills legacy"; el inventario real arrojó **13** archivos.
- De esos 13, **11 son migrables** y **2 son referencias** no ejecutables.
- Los packs PACK1 (FE) y PACK3 (CO) compilados v2 en `faberloom/SKILL_FE_*.md` / `SKILL_CO_*.md` no se re-migraron; ya están en SHADOW.
