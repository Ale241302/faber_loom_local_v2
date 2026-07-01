# MANIFIESTO_APPEND_20260414_FORECAST_B2B
tipo: MANIFIESTO_APPEND
fecha: 2026-04-14
sesion: indexa demand forecasting B2B Marluvas
aprobador: CEO
aplica_a: [MWT]

---

## Documentos creados

| Archivo | Tipo | Dominio | Version |
|---------|------|---------|---------|
| PLB_DEMAND_FORECASTING.md | PLB | DISTRIBUCION | 1.0 |
| ENT_DIST_FORECAST_SIGNALS.md | ENT | DISTRIBUCION | 1.0 |
| SCH_DEMAND_FORECAST_REPORT.md | SCH | SCHEMA_REGISTRY | 1.0 |
| SKILL_DEMAND_FORECASTER.md | SKILL | COMERCIAL | 1.0 |

## Documentos modificados

| Archivo | Cambio | Version anterior → nueva |
|---------|--------|--------------------------|
| SCHEMA_REGISTRY.md | +SCH_DEMAND_FORECAST_REPORT en sección OPERATIVOS. Total 16 schemas. | — |
| IDX_DISTRIBUCION.md | +ENT_DIST_FORECAST_SIGNALS +PLB_DEMAND_FORECASTING | — |
| IDX_COMERCIAL.md | +SKILL_DEMAND_FORECASTER | — |
| ENT_PLAT_SKILLS_CATALOG.md | +SKILL_DEMAND_FORECASTER. Total 7 skills. | v1.0 → v1.1 |
| RW_ROOT.md | Version bump. +changelog v4.7.1. | v4.7.0 → v4.7.1 |

## Origen del conocimiento

Swarm de demand forecasting ejecutado con Kimi 2.5 para caso demo Marluvas — Distribuidor Industrial del Centro S.A. Dataset simulado 24 meses, 3 SKUs. Metodología validada por CEO en sesión 2026-04-14.

## Pendientes abiertos por este batch

Ninguno obligatorio. Recomendado para futuro:
- Promover SCH_DEMAND_FORECAST_REPORT a ACTIVO tras ≥2 clientes reales
- Agregar señales S06+ a ENT_DIST_FORECAST_SIGNALS conforme se identifican en nuevas cuentas
