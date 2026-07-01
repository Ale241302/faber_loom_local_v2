# MANIFIESTO_APPEND_20260414_FORECAST_V2
tipo: MANIFIESTO_APPEND
fecha: 2026-04-14
sesion: SKILL_DEMAND_FORECASTER v2.0 — self-contained + SAP + outputs
aprobador: CEO
aplica_a: [MWT]

---

## Documentos creados

| Archivo | Tipo | Dominio | Version |
|---------|------|---------|---------|
| ENT_DIST_SAP_SCHEMAS.md | ENT | DISTRIBUCION | 1.0 |
| SCH_FORECAST_OUTPUTS.md | SCH | SCHEMA_REGISTRY | 1.0 |

## Documentos modificados

| Archivo | Cambio | Version |
|---------|--------|---------|
| SKILL_DEMAND_FORECASTER.md | Reescritura completa. v1.0→v2.0. Self-contained. +Agent_0A +Agent_F. 7 agentes. Señales y specs inline. | v1.0→v2.0 |
| SCH_DEMAND_FORECAST_REPORT.md | +ENT_DIST_SAP_SCHEMAS y SCH_FORECAST_OUTPUTS en requires. Ref a 7 agentes. | v1.0 |
| SCHEMA_REGISTRY.md | +SCH_FORECAST_OUTPUTS. Total 17 schemas. | — |
| IDX_DISTRIBUCION.md | +ENT_DIST_SAP_SCHEMAS | — |
| RW_ROOT.md | Version bump v4.7.1→v4.7.2 | v4.7.1→v4.7.2 |

## Descripción del cambio

SKILL_DEMAND_FORECASTER v2.0 es ahora completamente autocontenido:
- Todas las señales de negocio están inline (no referencia ENT_DIST_FORECAST_SIGNALS)
- Toda la lógica de normalización SAP está inline (no referencia ENT_DIST_SAP_SCHEMAS)
- Todos los specs de output están inline (no referencia SCH_FORECAST_OUTPUTS)
- Los documentos ENT/SCH existen para mantenimiento y referencia, no para inyección en runtime

Flujo completo: SAP/CSV → Agent_0A → Agent_A → B → C → D → E → Agent_F → Excel/PPT/Word
