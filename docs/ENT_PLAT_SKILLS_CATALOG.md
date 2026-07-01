# ENT_PLAT_SKILLS_CATALOG — Catálogo de Skills de Agentes IA
id: ENT_PLAT_SKILLS_CATALOG
version: 1.2
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
stamp: VIGENTE — 2026-04-16
aplica_a: [SHARED]

---

## A. Propósito

Registro centralizado de todos los SKILL_ del sistema. Cada skill es un system prompt especializado para un agente IA con un dominio acotado.

## B. Catálogo

| Skill | Dominio | Agente target | KB refs principales | Status |
|-------|---------|--------------|---------------------|--------|
| SKILL_AMAZON_OPS | Marketplace | RW-Ops Amazon | PLB_OPS_AMAZON, ENT_COMP_AMAZON | SHADOW |
| SKILL_CLIENT_SERVICE | Comercial | SVC-01 | PLB_INTERACCION_CLIENTE, ENT_PLAT_KNOWLEDGE.E3 | SHADOW |
| SKILL_COMPLIANCE_CHECKER | Compliance | RW-Compliance | POL_CLAIMS_SCANNER, POL_ROGERS, ENT_COMP_AMAZON | SHADOW |
| SKILL_COPY | Marketplace | Copywriter Amazon & Brand | PLB_COPY, POL_CLAIMS_SCANNER, ENT_PROD_{PROD}, LOC_{PROD}_{LANG} | SHADOW |
| SKILL_DEMAND_FORECASTER | Comercial | Kimi 2.5 / Claude Sonnet 4.6 | PLB_DEMAND_FORECASTING, ENT_DIST_FORECAST_SIGNALS, SCH_DEMAND_FORECAST_REPORT | SHADOW |
| SKILL_EXPERIMENT_RUNNER | Marketplace | RW-Growth Amazon | PLB_EXPERIMENTACION, ENT_GOB_KPI.B3 | SHADOW |
| SKILL_HUMANIZE_BRAND | Marca | Voz de plataforma y marcas | SKILL_HUMANIZE_COMMS, ENT_PROD_{PROD} | SHADOW |
| SKILL_HUMANIZE_COMMS | Comercial | Voz personal CEO | (autónomo — VOZ_CEO embebida) | SHADOW |
| SKILL_KB_AUDITOR | Gobernanza | Auditor nightly | PLB_AUDIT, POL_HEALTH_CHECK, ENT_PLAT_NIGHTLY_AUDITOR | SHADOW |
| SKILL_PROFORMA_BUILDER | Comercial | Asistente proformas | SCH_PROFORMA_MWT, ENT_COMERCIAL_MODELOS | SHADOW |

## C. Reglas

1. Cada SKILL tiene un solo dominio principal (indexado en su IDX)
2. Skills se crean cuando hay un agente real que los consumirá — no especulativos
3. Las KB refs del skill son de solo lectura para el agente — el agente no modifica la KB
4. Excepciones: SKILL_KB_AUDITOR puede generar reportes (archivos nuevos), no modificar existentes
5. Un skill puede referenciar otros skills para coordinación (ej: EXPERIMENT_RUNNER → COMPLIANCE_CHECKER)

---

Changelog:
- v1.0 (2026-04-01): Creación inicial con 6 skills. Terminología broker/trader/reseller/owner.
- v1.1 (2026-04-14): +SKILL_DEMAND_FORECASTER. Total 7 skills.
- v1.2 (2026-04-16): Arquitectura AgentSpec/Runtime/Memory. Todos los skills pasan a SHADOW. +SKILL_COPY (nuevo), +SKILL_HUMANIZE_BRAND, +SKILL_HUMANIZE_COMMS (faltaban en