# SCHEMA_REGISTRY — Catálogo de Schemas Disponibles
aplica_a: [SHARED]

Principio: schema existe = yo puedo ensamblarlo. Schema no existe = primero se crea.

## FÍSICOS

| Schema | Archivo | Hereda de | Status |
|--------|---------|-----------|--------|
| SCH_EMPAQUE_BASE | SCH_EMPAQUE_BASE.md | — | ACTIVO |
| SCH_EMPAQUE_CAJA_4 | SCH_EMPAQUE_CAJA_4.md | SCH_EMPAQUE_BASE | ACTIVO |
| SCH_EMPAQUE_BOLSA_2 | SCH_EMPAQUE_BOLSA_2.md | SCH_EMPAQUE_BASE | ACTIVO |
| SCH_STICKER_BASE | SCH_STICKER_BASE.md | — | ACTIVO |
| SCH_STICKER_CAJA | SCH_STICKER_CAJA.md | SCH_STICKER_BASE | ACTIVO |
| SCH_STICKER_BOLSA | SCH_STICKER_BOLSA.md | SCH_STICKER_BASE | ACTIVO |

## MARKETPLACE

| Schema | Archivo | Hereda de | Status |
|--------|---------|-----------|--------|
| SCH_LISTING_AMAZON | SCH_LISTING_AMAZON.md | — | ACTIVO |
| SCH_APLUS_CONTENT | SCH_APLUS_CONTENT.md | — | ACTIVO |
| SCH_LLMS_TXT | SCH_LLMS_TXT.md | — | ACTIVO |

## WEB/DIGITAL

| Schema | Archivo | Hereda de | Status |
|--------|---------|-----------|--------|
| SCH_PAGINA_PRODUCTO | SCH_PAGINA_PRODUCTO.md | — | ACTIVO |
| SCH_FICHA_TECNICA | SCH_FICHA_TECNICA.md | — | ACTIVO |

## OPERATIVOS

| Schema | Archivo | Hereda de | Status |
|--------|---------|-----------|--------|
| SCH_BRIEF_PROVEEDOR | SCH_BRIEF_PROVEEDOR.md | — | ACTIVO |
| SCH_PROFORMA_MWT | SCH_PROFORMA_MWT.md | — | DRAFT |
| SCH_DEMAND_FORECAST_REPORT | SCH_DEMAND_FORECAST_REPORT.md | — | DRAFT |
| SCH_FORECAST_OUTPUTS | SCH_FORECAST_OUTPUTS.md | SCH_DEMAND_FORECAST_REPORT | DRAFT |

## PLATAFORMA

| Schema | Archivo | Hereda de | Status |
|--------|---------|-----------|--------|
| SCH_CONTRATO_NODO | SCH_CONTRATO_NODO.md | — | DRAFT |
| SCH_ISO_AUDIT_PACK | SCH_ISO_AUDIT_PACK.md | — | DRAFT |

## GOBERNANZA DE AGENTES

| Schema | Archivo | Hereda de | Status |
|--------|---------|-----------|--------|
| SCH_SKILL | SCH_SKILL.md | — | VIGENTE |
| SKILL_RUNTIME | SKILL_RUNTIME.md | — | VIGENTE |

## AI GOVERNANCE

| Schema | Archivo | Hereda de | Status |
|--------|---------|-----------|--------|
| SCH_AI_GOV_HANDOFF_DRAFT | SCH_AI_GOV_HANDOFF_DRAFT.md | — | VIGENTE v1.0 (handoff carpintero → final pass) |
| SCH_AI_GOV_DUAL_REVIEW_OUTPUT | SCH_AI_GOV_DUAL_REVIEW_OUTPUT.md | — | VIGENTE v1.0 (veredicto final del Dual Review) |

## FABERLOOM

> Agregado por PR-3 auditoría de reindexación 2026-05-03 2026-05-03. Cierra brecha de SCH_FB huerfanos del registry (POL_NUEVO_DOC).
> Decision arquitectonica: registry unico (no split MWT/FB) — POL_DETERMINISMO §1 dato unico, ademas SCH_FB_SKILL_MANIFEST_v2 hereda de SCH_SKILL del bloque GOBERNANZA DE AGENTES.

| Schema | Archivo | Hereda de | Status |
|--------|---------|-----------|--------|
| SCH_FB_CLI_INTERFACE | faberloom/SCH_FB_CLI_INTERFACE.md | — | VIGENTE v2.0 |
| SCH_FB_FLOW_DAG | faberloom/SCH_FB_FLOW_DAG.md | — | VIGENTE v2.0 |
| SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1 | faberloom/SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1.md | parametriza ENT_FB_VERTICAL_SPEC_OBJECT_v1 | VIGENTE v1.0 |
| SCH_FB_SKILL_MANIFEST_v2 | faberloom/SCH_FB_SKILL_MANIFEST_v2.md | extiende SCH_SKILL | VIGENTE v2.0 |
| SCH_FB_TASK_ENTITY | faberloom/SCH_FB_TASK_ENTITY.md | — | VIGENTE v2.0 |

Total: 26 schemas registrados (12 ACTIVO + 5 DRAFT + 9 VIGENTE) | 25 SCH_ en disco + 1 SKILL_RUNTIME (tipo SCH, prefijo SKILL_)

---

Changelog:
- 2026-06-15 (AUDIT-ROUTING-2026-06-14): Fix ref rota en encabezado de sección FABERLOOM: se sustituye el token del evento de auditoría por texto plano con fecha. v1.0 → v1.1.
- 2026-05-03 (PR-3 auditoría de reindexación 2026-05-03): +seccion FABERLOOM con 5 SCH_FB_* (resuelve huerfanos del registry detectados por audit). Total 21→26.
