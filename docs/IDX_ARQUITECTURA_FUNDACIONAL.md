---
id: IDX_ARQUITECTURA_FUNDACIONAL
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: ARQUITECTURA
tipo: index
last_review: 2026-05-04
stamp: VIGENTE - 2026-05-04
aplica_a: [SHARED]
---

# IDX_ARQUITECTURA_FUNDACIONAL - Domain Index

> Routers SPEC_/ARCH_ que aplican transversalmente a MWT + FaberLoom.
> Antes vivian colgados de IDX_GOBERNANZA seccion "Arquitectura Fundacional" - descongestionados aqui.
> Origen: audit retrieval golden-set 10q 2026-05-04 detecto mezcla de scopes (gobernanza vs arquitectura agentic vs FaberLoom) en IDX_GOBERNANZA.

## Principios

| Archivo | Tipo | Status |
|---|---|---|
| ARCH_AGENT_PRINCIPLES.md | 13 principios + 3 tiers + canonical objects (ImpactVector, OutcomeLedger, UserControlProfile) | VIGENTE v1.2 |

## Specs medulares MWT

| Archivo | Funcion | Status |
|---|---|---|
| SPEC_MWT_AGENT_PLATFORM.md | 3 componentes plataforma (Knowledge Hub - mwt.one - FaberLoom) + roadmap autonomia | VIGENTE v1.2 |
| SPEC_ACTION_ENGINE.md | Engine medular contract-first (D1-D10, +D9 Data Class Routing, +D10 Audit Inmutable) | VIGENTE v1.2 |
| SPEC_AUDIT_MODULE.md | Audit Module D10 materializado, audit_event schema, Fase 4-5 | VIGENTE v1.0 |
| SPEC_AUTONOMY_CONTROL_ENGINE.md | ImpactVector 8D + Task Authorization + Async Queue + Promotion Engine + ModelFingerprint + Shadow Audit Trail | VIGENTE v1.2 |
| SPEC_LLM_ROUTING_ARCHITECTURE.md | L1 Clasificador + L2 Dispatcher Arena-aware + L3 Prompt Compiler + Token Ledger (+campos governance AI_GOV) | VIGENTE v1.3 |
| SPEC_QUERY_PROCESSING_PIPELINE.md | Pipeline 8 fases consulta -> memoria, observable en Cowork, mapeado a FaberLoom | VIGENTE v1.0 |
| SPEC_AI_GOV_GOVERNANCE_AND_ROUTING.md | Capa AI_GOV sobre routing tecnico - data_class x provider, skill installation, final pass premium, output pinning, eval lab mensual | VIGENTE v1.1 |
| SPEC_AGENT_ARCHITECTURE_ALE.md | Brief tecnico AG-02 | PARA REVISION v1.0 |
| SPEC_TENANT_CONTAMINATION_TESTS.md | Suite anti-cross-tenant (7 superficies: RLS, embeddings, memory, pinning, cache, logs, tools) + gate pre-deploy | DRAFT v1.0 |

## Specs FaberLoom (scope separado)

| Archivo | Status | Ruta |
|---|---|---|
| SPEC_FABERLOOM_MVP.md | VIGENTE v1.0 | docs/ (legacy pre-29-abr) |
| docs/faberloom/IDX_FB_FOUNDATION_BETA.md | Router de SPECs FaberLoom | docs/faberloom/ |
| SPEC_FB_EVAL_ARENA_v1.md | DRAFT v1.0 -- arena ciega de evaluacion + gobernanza de routing multi-proveedor/multi-tenant (registro abierto de APIs, herencia de config, BYO, savings ledger, MCP FB-en-MWT). Da servicio a MWT | docs/faberloom/ |
| SPEC_FB_EVOLUTION_ROADMAP_v1.md | DRAFT v1.0 -- secuencia de construccion por modulos (7 fases walking-skeleton-first; chat space + routing primero). Contrapeso de ejecucion a los SPECs de diseno | docs/faberloom/ |
| SPEC_FB_ARCHETYPE_v1.md | DRAFT v1.1 (herencia plana copy-on-create; cascada DIFERIDA) -- el arquetipo como unidad central (4 dimensiones: estructura 6 facetas, herencia, evolucion optimiza/sugiere, clasificacion dinamica). Unifica archetype+template+working profile+routing | docs/faberloom/ |
| SPEC_FB_BUILD_SEQUENCE_v3.md | DRAFT v3.0 (etapa 2 generica, skills no predefinidos, cotizacion como ejemplo) -- secuencia unica de build E0-E4 + E2.5 comercial paralela. Supersede v2.1 y PLB v1.3.2; ORDEN superseded por PLAN_DESARROLLO_FABERLOOM_v5 (2026-06-22) | docs/faberloom/ |
| SPEC_FB_BUILD_SEQUENCE_v2.md | DRAFT v2.1 (superseded por v3.0 al firmarse) | docs/faberloom/ |
| SPEC_FB_ROUTING_PRESETS_v1.md | DRAFT v1.0 -- presets de ruteo 3 capas (ECU data-class / preset tenant / curva usuario) + fabrica niveles 0-4 (presets casa, wizard, template vertical, promocion HITL, builder IA chat-first con backtest ledger). Reemplaza SPEC_FB_EVAL_ARENA como mecanismo de optimizacion | docs/faberloom/ |

> Para FaberLoom usar IDX_FB_FOUNDATION_BETA como router primario. Este IDX solo lista los SPECs FB que tocan arquitectura compartida MWT+FB.

## Relacion con otros IDX

| IDX | Que mantiene | Que cede a este |
|---|---|---|
| IDX_GOBERNANZA | POLs, PLBs gobernanza, ENTs gob, AUDITs FB pre-build | SPEC_*, ARCH_* (movidos aqui) |
| IDX_PLATAFORMA | ENTs plataforma, PLBs operativos, sprints | nada |
| IDX_FB_FOUNDATION_BETA | Specs FB exclusivos | SPECs FB que tocan MWT compartido |

## Reglas

1. Cualquier `SPEC_` o `ARCH_` nuevo que aplique transversalmente (MWT + FB o solo MWT-core) se referencia aqui.
2. SPECs scope FB-puro viven en `docs/faberloom/` y se ruteo via `IDX_FB_FOUNDATION_BETA`.
3. IDX_GOBERNANZA conserva pointer a este IDX, no duplica la tabla.
4. Cualquier SPEC declarado FROZEN debe aparecer ademas en POL_INMUTABILIDAD seccion FROZEN canonicos.

---

Changelog:
- 2026-06-15 (AUDIT-ROUTING-2026-06-14): Fix patrón no concreto para SPECs FaberLoom: se reemplaza la plantilla por el router concreto docs/faberloom/IDX_FB_FOUNDATION_BETA.md. v1.0 → v1.1.
- v1.0 (2026-05-04): Creacion. Origen: audit retrieval golden-set 10q detecto que ARCH_AGENT_PRINCIPLES + 7 SPECs medulares colgaban de IDX_GOBERNANZA seccion "Arquitectura Fundacional" mezclando scopes. ASCII puro.
