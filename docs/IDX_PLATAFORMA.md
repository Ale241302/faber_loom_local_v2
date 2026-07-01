---
id: IDX_PLATAFORMA
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: PLATAFORMA
tipo: index
last_review: 2026-04-21
stamp: VIGENTE — 2026-04-21
---

# IDX_PLATAFORMA — Domain Index

> **Health:** 25/41 archivos con contenido (+2 ENT_AI_GOV) · 12 stubs · 0 deprecated · +1 SPEC_AI_GOV en Arquitectura · +1 SKILL_FRONTEND_PRINCIPLES_MWT v1.0 SHADOW
> **Última revisión:** 2026-05-04 (INDEXA SKILL_FRONTEND_PRINCIPLES_MWT v1.0 SHADOW — lente cognitiva 9 principios MWT derivada de SKILL_FRONTEND_TEN_PRINCIPLES_V2 FB v2.1 · selección 9/14 + adaptación a 3 frontends MWT · ACTIVO_BG · 16 flags · 4 P0 bloqueantes · pendiente §UI_GLOSSARY en ENT_PLAT_FRONTENDS)
> **Revisión anterior:** 2026-05-01 (INDEXA AI_GOV — +ENT_AI_GOV_GOLDEN_CORPUS_MWT +ENT_AI_GOV_OUTPUT_PINS +SPEC_AI_GOV_GOVERNANCE_AND_ROUTING · SPEC_LLM_ROUTING v1.2→v1.3 con campos governance en Token Ledger · 3 POLs en IDX_GOBERNANZA)
> **Revisión anterior:** 2026-04-21 (ENT_PLAT_LLM_ROUTING v1.0 → v2.0 post Kimi Swarm #4)

## Entities
| Entity | Archivo | Status |
|--------|---------|--------|
| Agentic | ENT_PLAT_AGENTIC.md | DRAFT |
| Agent Orchestration | ENT_PLAT_AGENT_ORCHESTRATION.md | DRAFT |
| Artefactos | ENT_PLAT_ARTEFACTOS.md | DRAFT |
| Automations | ENT_PLAT_AUTOMATIONS.md | DRAFT |
| Canales | ENT_PLAT_CANALES.md | DRAFT |
| Canales Cliente | ENT_PLAT_CANALES_CLIENTE.md | DRAFT (v1.0 — canales interacción B2B) |
| Contrato Nodo | ENT_PLAT_CONTRATO_NODO.md | DRAFT |
| Design Tokens | ENT_PLAT_DESIGN_TOKENS.md | APROBADO — Sprint 3 |
| Eventos | ENT_PLAT_EVENTOS.md | DRAFT |
| Frontends | ENT_PLAT_FRONTENDS.md | DRAFT |
| I18N | ENT_PLAT_I18N.md | DRAFT |
| Action Registry | ENT_PLAT_ACTION_REGISTRY.md | VIGENTE v1.1 (catálogo 53 acciones + DPA LATAM por LLM) |
| Infra | ENT_PLAT_INFRA.md | DRAFT |
| Knowledge | ENT_PLAT_KNOWLEDGE.md | DRAFT |
| Legal Entity | ENT_PLAT_LEGAL_ENTITY.md | DRAFT |
| LLM Routing | ENT_PLAT_LLM_ROUTING.md | DRAFT (v2.0 — tiered hardcoded F1 FaberLoom + data residency `tenant_model_allowlist` + HA LiteLLM + circuit breakers + cold start 30d + F2 adaptive postponed; model registry, pricing, PLT-11 arquitectura preservados) |
| Marcas | ENT_PLAT_MARCAS.md | DRAFT |
| Memory Stack | ENT_PLAT_MEMORY_STACK.md | DRAFT (v1.0 — pgvector + Letta self-host, CF Agent Memory en watch-list) |
| Módulos | ENT_PLAT_MODULOS.md | DRAFT |
| Multitenant | ENT_PLAT_MULTITENANT.md | STUB |
| MVP | ENT_PLAT_MVP.md | DRAFT |
| Nightly Auditor | ENT_PLAT_NIGHTLY_AUDITOR.md | DRAFT |
| Observabilidad | ENT_PLAT_OBSERVABILIDAD.md | STUB |
| Países | ENT_PLAT_PAISES.md | STUB |
| Seguridad | ENT_PLAT_SEGURIDAD.md | DRAFT (v1.0 — framework 8 secciones, PARTNER_B2B) |
| Skills Catalog | ENT_PLAT_SKILLS_CATALOG.md | VIGENTE v1.2 |
| SSOT | ENT_PLAT_SSOT.md | STUB |
| Scanner Security | ENT_PLAT_SCANNER_SECURITY.md | STUB (v0.1 — seguridad scanner biométrico) |
| AI Gov · Golden Corpus MWT | ENT_AI_GOV_GOLDEN_CORPUS_MWT.md | DRAFT v1.0 (esqueleto · corpus vacío pendiente curación CEO) |
| AI Gov · Output Pins | ENT_AI_GOV_OUTPUT_PINS.md | DRAFT v1.0 (registry vacío · poblamiento via promoción Token Ledger) |

## Playbooks
| Playbook | Archivo | Status |
|----------|---------|--------|
| API | PLB_API.md | STUB |
| Architect | PLB_ARCHITECT.md | STUB |
| DevOps | PLB_DEVOPS.md | STUB |
| Frontend | PLB_FRONTEND.md | STUB |
| Integration | PLB_INTEGRATION.md | STUB |
| Migration | PLB_MIGRATION.md | STUB |
| Ops Amazon | PLB_OPS_AMAZON.md | DRAFT (framework completo v1.1) |
| Interacción Cliente | PLB_INTERACCION_CLIENTE.md | DRAFT (v1.0 — playbook B2B) |
| Prompting | PLB_PROMPTING.md | DRAFT (v1.0 — fichas por modelo, anti-alucinación, contraparte) |
| QA | PLB_QA.md | STUB |
| Orchestrator | PLB_ORCHESTRATOR.md | FROZEN |
| Scanner Distrib | PLB_SCANNER_DISTRIB.md | DRAFT |

## Localizations (Service)
| LOC | Archivo | Status |
|-----|---------|--------|
| SVC ES | LOC_SVC_ES.md | DRAFT (v1.0 — templates servicio cliente español) |
| SVC PT | LOC_SVC_PT.md | DRAFT (v1.0 — templates servicio cliente português BR) |

## Skills
| Skill | Archivo | Status |
|-------|---------|--------|
| Client Service (ver IDX_COMERCIAL) | SKILL_CLIENT_SERVICE.md | SHADOW v1.1 |
| Frontend Principles MWT (lente cognitiva 9 principios · ACTIVO_BG) | SKILL_FRONTEND_PRINCIPLES_MWT.md | SHADOW v1.0 |
| KB Gateway (gateway transaccional para escrituras KB) | SKILL_KB_GATEWAY.md | SHADOW v1.0 |
| Frontend Ten Principles V2 FB (lente cognitiva FB Design System · ACTIVO_BG) | docs/faberloom/SKILL_FRONTEND_TEN_PRINCIPLES_V2.md | SHADOW v2.1 |

## Arquitectura de Plataforma
| Archivo | Tipo | Status |
|---------|------|--------|
| SPEC_MWT_AGENT_PLATFORM.md | SPEC — 3 componentes (Knowledge Hub · mwt.one · FaberLoom), stack mwt.one, 3 objetos, roadmap autonomía | VIGENTE v1.2 |
| SPEC_ACTION_ENGINE.md | SPEC — Action Engine medular contract-first, 8 decisiones cementadas, +D9 +D10, 9 semanas roadmap | VIGENTE v1.2 |
| SPEC_AUDIT_MODULE.md | SPEC — Audit Module D10 materializado, audit_event schema, Fase 4-5 | VIGENTE v1.0 |
| SPEC_AUTONOMY_CONTROL_ENGINE.md | SPEC — ImpactVector 8D, Task Authorization, Async Queue, Promotion Engine, ModelFingerprint, Shadow Audit Trail | VIGENTE v1.2 |
| SPEC_LLM_ROUTING_ARCHITECTURE.md | SPEC — L1 Clasificador + L2 Dispatcher Arena-aware + L3 Prompt Compiler + Token Ledger (v1.3 +campos governance AI_GOV) | VIGENTE v1.3 |
| SPEC_QUERY_PROCESSING_PIPELINE.md | SPEC — pipeline 8 fases consulta→memoria, observable en Cowork, mapeado a FaberLoom | VIGENTE v1.0 |
| SPEC_AI_GOV_GOVERNANCE_AND_ROUTING.md | SPEC — capa AI_GOV sobre routing técnico; gobierna data_class×provider, skill installation, final pass premium, output pinning, eval lab mensual | VIGENTE v1.0 |
