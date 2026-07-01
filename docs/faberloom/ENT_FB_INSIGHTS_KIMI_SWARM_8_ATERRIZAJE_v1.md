# ENT_FB_INSIGHTS_KIMI_SWARM_8 - Determinismo de skills, aislamiento multi-tenant LLM, memoria temporal

id: ENT_FB_INSIGHTS_KIMI_SWARM_8_ATERRIZAJE_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (IDX_FB_FOUNDATION_BETA)
type: ENT
stamp: VIGENTE -- 2026-06-15 -- destilado de FB-SWARM-2026-06-15 (3 tracks, 12 sub-agentes, 100+ fuentes tipadas A-E). Crudos en docs/anexos/kimi_swarm_8/
aprobador: CEO (Alvaro)
aplica_a: [FaberLoom]
relacionado: SPEC_FB_KNOWLEDGE_RIVER_v1 v1.1 - SPEC_FB_AUTH_TENANT_RBAC_v1 - POL_FB_KR_PRIVACY_TIERS_v1 - SPEC_FB_BUILD_SEQUENCE_v3 - AUDIT_FB_SESION_20260615_v1

---

## A. Proposito

Hechos externos (junio 2026) sobre tres puntos ciegos de arquitectura de FaberLoom:
determinismo de outputs de skills, aislamiento multi-tenant para agentes LLM, y
memoria temporal con knowledge graphs. Cada hecho tiene fuente en los crudos
(anexos/kimi_swarm_8/). NINGUNA cifra entra como dato sin verificar la fuente
primaria. Varios IDs arXiv quedan [PENDIENTE - VERIFICAR FUENTE].

## B. Lo que CIERRA (decisiones de arquitectura)

| # | Hecho | Decision afectada | Accion |
|---|---|---|---|
| 1 | Nivel "contractual byte-identical" NO es alcanzable sobre API comercial (ni Claude garantiza determinismo). Requiere self-hosted (SGLang) + hardware fijo. | Fabrica de niveles 0-4 | Tope = "muy confiable con validacion automatica", NO "garantizado". Nivel 4 != contractual. Decision CEO 2026-06-15. |
| 2 | Constrained decoding garantiza formato (~100% schema) pero NO semantica (gap 15-30pp entre "JSON valido" y "JSON correcto"). En modelos MoE el CD logit-level es inutil o danino. | Diseno de gates por nivel | CD para formato (niveles 2-3) + validacion semantica post-hoc (nivel 4). Si la fabrica corre MoE (Qwen3/Mixtral/DeepSeek): post-hoc semantico OBLIGATORIO. |
| 3 | Aislamiento vectorial: filtrar por user_id/metadata NO basta (hasta 100% ASR con filtro mal aplicado). Namespace/shard por tenant es el minimo. pgvector necesita partial index por tenant. | Storage L0/L2 del Knowledge River | Revisar storage del River vs namespace-por-tenant al despausar. Ver AUDIT_FB_SESION_20260615 delta B. |
| 4 | RLS + tenant_id protege SQL pero NO cubre fugas LLM: KV-cache (PROMPTPEEK 99% reconstruccion), tool state global (~100% leak sin ABAC), vector retrieval. | Multi-tenant rules (CLAUDE.md) | RLS es necesario pero NO suficiente para agentes. Sumar ABAC gating server-side en tools + aislamiento vectorial antes del primer cliente enterprise. |
| 5 | Testing en capas: golden/snapshot (capta 90%+ regresiones) + LLM-as-judge (~85% agreement) son complementarios, no excluyentes. | QA de la fabrica | Ambos. Snapshot como primera linea barata + LLM-judge para lo subjetivo en niveles 3-4. |

## C. Lo que requiere DECISION CEO (conflictos escalados, no resueltos)

| C | Conflicto | Por que decide el CEO |
|---|---|---|
| C1 | CD mejora (+4% JSONSchemaBench) vs degrada (-10-30% DCCD) calidad segun modelo/tarea | Definir por nivel de la fabrica; medir con el modelo y schema reales. No asumir direccion. |
| C4 | Nivel de madurez: por skill, por tenant, o por plataforma. Nadie en la literatura lo resuelve | Decision de diseno propia. Es "trabajo original" (ver E). |
| C6 | RLS "suficiente" vs "no basta para agentes" | Definir modelo de amenaza que extienda las multi-tenant rules a 4 capas: SQL, vector, inferencia/cache, tools. |

## D. Conflictos entre fuentes (NO presupuestar sobre ellos)

1. Determinismo con seed+temp=0: docs usan lenguaje "mostly"; en produccion el no-determinismo es observable. Claude no tiene seed.
2. RLS overhead: "minimo" (docs) vs 20x (PlanetScale con funciones VOLATILE). Realidad: 10-15% con indice compuesto obligatorio.
3. Schema-per-tenant: "escala bien" (docs) vs "trampa a 200-1000" (Atlassian/ClickHouse).
4. Benchmarks memoria temporal (Mem0 vs Zep LongMemEval): cifras incompatibles entre fuentes (49% vs 94.4%). NO usar para decision sin benchmark propio.
5. IDs arXiv citados por el swarm (2603.03305, 2603.27905, 2601.06627): [PENDIENTE - VERIFICAR FUENTE] antes de citar.

## E. Investigaciones cerradas / abiertas

CERRADAS por este swarm: techo de determinismo sobre API comercial, CD formato-vs-semantica, insuficiencia de RLS solo para agentes, minimo de aislamiento vectorial (namespace), testing en capas.

SIGUEN ABIERTAS (sin solucion de estanteria - trabajo original de arquitectura, prioridad Alta):
- Framework de madurez por-skill en plataforma multi-tenant (no existe en literatura).
- Testing automatizado de aislamiento cross-tenant (no existe framework OSS).

DIFERIDO post-E2: memoria temporal (Graphiti/Mem0/Zep) en modo reconocimiento; requiere benchmark propio en espanol antes de adoptar.

---

Changelog:
- v1.0 (2026-06-15): creacion. Destilado de FB-SWARM-2026-06-15 (tracks T1 determinismo, T2 aislamiento multi-tenant, T3 memoria temporal). 5 cierres, 3 conflictos escalados a CEO, 5 conflictos de fuente, 2 investigaciones abiertas marcadas trabajo original. Crudos en docs/anexos/kimi_swarm_8/. IDs arXiv pendientes de verificar.
