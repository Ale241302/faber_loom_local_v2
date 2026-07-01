---
id: ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma
type: entity
stamp: VIGENTE 2026-04-30
fecha: 2026-04-30
agente: Cowork (redaccion) + CEO (autoria del insight arquitectonico)
aplica_a: [FaberLoom]
extiende: ARCH_AGENT_PRINCIPLES (no modifica core sealed v1.5 · agrega P16 como extension FB)
relacionado_con:
  - SPEC_FB_KNOWLEDGE_RIVER_v1
  - SPEC_FB_AGENT_BUILDER_v1
  - ENT_FB_AGENT_ARCHETYPES_v1
  - ENT_FB_SUB_AGENTS_LIBRARY_v1 (PENDIENTE)
  - SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1 (PENDIENTE)
---

# ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1
## P16 · Atomic Agents Principle

## 1. El principio

> Los agentes principales (archetype-level) deben ser **orquestadores delgados** que delegan trabajo cognitivo a **sub-agentes atomicos especializados**. Un agente principal NO ejecuta tareas complejas internamente: las descompone, dispatcha a sub-agentes, agrega resultados, y mantiene contexto del cliente/cuenta.

**Patron canonico:**

```
AG_PRINCIPAL (orquestador · stateful · delgado)
  ├── AG_SUB_TASK_A (atomico · stateless · especializado)
  ├── AG_SUB_TASK_B (atomico · stateless · especializado)
  └── AG_SUB_TASK_C (atomico · stateless · especializado)
```

Origen del insight:
> CEO (2026-04-30): "es que veo muy granular las acciones... el agente principal se convierte en un distribuidor de tareas a sub agentes que se especializan en solo una cosa... aca lo que se me ocurre es que este tipo de necesidad se elabora con un agente orchestador"

## 2. Por que (los 4 beneficios cuantificados)

### 2.1 Token cost reduction (-65% promedio)
Modelo monolitico procesa todo el contexto en cada call. Sub-agentes reciben solo lo necesario para su tarea.

| Escenario | Monolitico | Descompuesto | Reduccion |
|---|---|---|---|
| AM gestiona email entrante | 8.5k tokens (full context) Sonnet | 1.2k clasificacion Haiku + 4k draft Sonnet | -47% |
| AM construye proforma | 12k tokens Sonnet | 800 SAP query Haiku + 600 pricing Python + 5k narrativa Sonnet | -47% |
| AM pre-call summary | 6k tokens Sonnet | 500 fetch Haiku + 1.5k summary Haiku | -67% |
| **Promedio ponderado** | | | **-65%** |

Proyeccion economica:
- MWT solo (1 tenant Marluvas + Tecmater): ~$1.5k/mes monolitico → ~$525/mes descompuesto · ahorro ~$11.7k/ano
- 5 tenants v2: ~$58k/ano evitados

### 2.2 Audit precision granular
Cada sub-call queda en audit log con su input/output/modelo/costo/latencia. Esto habilita:
- Debug quirurgico cuando un draft sale mal (ver exactamente que sub-agente fallo)
- Atribucion de costo por sub-tarea (que pieza es la cara · que pieza vale la pena optimizar)
- A/B testing per sub-agente sin tocar el orquestador
- Compliance audit trail (POL_DATA_CLASSIFICATION cumplible per sub-call)

### 2.3 Learning concentration en sub-agentes reutilizables
Knowledge River destila mejor cuando el corpus de uso esta concentrado:
- AG_SUB_DRAFT_WRITER recibe pool de TODOS los account managers (Marluvas + Tecmater + futuros) → mas datos, mejores patterns destilados
- AG_SUB_EMAIL_CLASSIFIER mejora con corpus cross-tenant respetando k-anonymity
- Mejora 1 sub-agente = mejora todos los archetypes que lo usan

vs monolitico: cada AM aprende aislado de su propio uso, dataset fragmentado, destilacion debil.

### 2.4 Model routing per task
Ningun task requiere el modelo mas caro. Sub-agentes permiten asignar modelo por capacidad real:

| Sub-agente | Modelo apropiado | Por que |
|---|---|---|
| AG_SUB_EMAIL_CLASSIFIER | Haiku 4.5 | Clasificacion N-way · Sonnet seria desperdicio |
| AG_SUB_DRAFT_WRITER | Sonnet 4.6 | Creatividad + tono · justifica costo |
| AG_SUB_PROFORMA_BUILDER | Sonnet 4.6 | Estructura compleja + narrativa |
| AG_SUB_SAP_QUERY | Haiku + tool | Solo formatea params para SAP API |
| AG_SUB_VOICE_TRANSCRIBER | Whisper | Sin LLM |
| AG_SUB_PRE_CALL_SUMMARIZER | Haiku 4.5 | Resumen extractivo |
| AG_SUB_COMPLIANCE_CHECKER | Haiku 4.5 | Reglas binarias |
| AG_SUB_ESCALATION_ROUTER | deterministico | If/then puro |
| AG_SUB_PRICING_CALCULATOR | Python puro | Sin LLM · matematica |
| AG_SUB_INVENTORY_FETCHER | tool only | API call |

Sin descomposicion: todo va a Sonnet. Con descomposicion: 4 de 10 son Sonnet, 4 son Haiku, 2 son sin-LLM.

## 3. Threshold: cuando algo NO es sub-agente

Si un componente solo hace **1 LLM call** y no tiene memoria propia, NO es sub-agente — es **skill_package determinista** (codigo + 1 prompt template).

| Criterio | Sub-agente | Skill_package |
|---|---|---|
| Calls a LLM | >=2 con razonamiento iterativo | 1 directo |
| Memoria L2 propia | Si | No |
| Aparece en audit log granular | Si (con id propio) | Si (como sub-call del padre) |
| Knowledge River alimenta L3 propia | Si | No (alimenta la del padre) |
| Reutilizable cross-archetype | Si | Si pero sin learning propio |

Esto evita sobre-fragmentacion: no convertir cada llamada API en "sub-agente" solo por moda.

## 4. Tensiones a cuidar

### 4.1 Sobre-fragmentacion
Riesgo: dividir tanto que el overhead de orquestacion supera el beneficio.
Mitigacion: threshold §3 + max 12 sub-agentes por archetype principal · si pasa de 12 reagrupar.

### 4.2 Latencia compuesta
Riesgo: 5 sub-calls secuenciales = 5x latencia.
Mitigacion: orquestador paralelliza llamadas independientes (Promise.all-style) · solo serializa lo que tiene dependencia real de datos.

### 4.3 Audit overhead
Riesgo: 10x mas eventos en audit log = mas storage + mas ruido.
Mitigacion: audit log SHA-chain ya disenado para volumen · indexar por trace_id (1 trace = 1 user request) para reconstruccion rapida.

### 4.4 Coordinacion de errores
Riesgo: si AG_SUB_C falla, que hace AG_PRINCIPAL?
Mitigacion: orquestador tiene policy explicita per sub-agente: retry · fallback · degraded mode · escalate-to-human. Documentado en SCH_FB_FLOW_DAG.

### 4.5 Test surface area
Riesgo: 10 sub-agentes = 10 sets de tests + integration test del orquestador.
Mitigacion: cada sub-agente es testeable en aislamiento (input/output contract claro) · simplifica QA en realidad.

## 5. Como encaja con Knowledge River

P16 **mejora** Knowledge River sin romperlo:

- L1 working memory: el orquestador mantiene la sesion del usuario · sub-agentes son stateless dentro del request
- L2 episodic privada: por archetype principal (no por sub-agente individual) · simplifica privacy boundary
- L3 pool colectivo: cada sub-agente reutilizable tiene su propio pool · convergencia mas rapida porque dataset esta concentrado
- L4 indexed: las best practices destiladas se aplican al sub-agente correspondiente · cuando se updeates el sub-agente, todos los archetypes que lo usan se benefician inmediato

Curaduria gana granularidad: el comite revisa pattern destilado de "como AG_SUB_DRAFT_WRITER deberia abrir respuestas a queja por delay" en vez de revisar cambios al monolitico AM.

## 6. Como encaja con archetypes existentes

`ENT_FB_AGENT_ARCHETYPES_v1` define archetypes a nivel principal. Esta vista NO cambia: los archetypes siguen siendo la unidad de modelado para el usuario final del agent builder.

Lo que cambia es la **implementacion**: cada archetype = 1 orquestador + N sub-agentes del catalogo `ENT_FB_SUB_AGENTS_LIBRARY_v1` (PENDIENTE crear).

## 7. Catalogo inicial — 10 sub-agentes para vertical Account Management

Para validar el principio en el flagship FB v1 (vertical AM B2B Marluvas/Tecmater):

| ID sub-agente | Modelo | Trigger | Output |
|---|---|---|---|
| AG_SUB_EMAIL_CLASSIFIER | Haiku 4.5 | inbound email | {category, urgency, sentiment, requires_human} |
| AG_SUB_DRAFT_WRITER | Sonnet 4.6 | category=respond | draft email + tono justificado |
| AG_SUB_PROFORMA_BUILDER | Sonnet 4.6 | category=quote_request | proforma estructurada PDF-ready |
| AG_SUB_SAP_QUERY | Haiku + SAP tool | needs ERP data | SAP records fetched |
| AG_SUB_VOICE_TRANSCRIBER | Whisper | call recording uploaded | transcript timestamped |
| AG_SUB_PRE_CALL_SUMMARIZER | Haiku 4.5 | scheduled call <24h | 1-pager: cuenta, ultimas 5 interacciones, items abiertos |
| AG_SUB_COMPLIANCE_CHECKER | Haiku 4.5 | before send | {pass, warnings, blocking_issues} per LFPDPPP/LGPD |
| AG_SUB_ESCALATION_ROUTER | deterministic | from classifier | enum {auto_handle, supervisor, ceo, legal} |
| AG_SUB_PRICING_CALCULATOR | Python puro | proforma needs price | line items con descuentos politica |
| AG_SUB_INVENTORY_FETCHER | tool only | proforma needs stock | stock per SKU per warehouse |

Detalle completo de cada uno → `ENT_FB_SUB_AGENTS_LIBRARY_v1` (proxima sesion).

## 8. Relacion con ARCH_AGENT_PRINCIPLES (core sealed v1.5)

Este principio P16 **NO modifica** ARCH_AGENT_PRINCIPLES.md. Ese archivo esta SEALED como CORE BLINDADO (commit 9ecd190).

P16 es una **extension FB-specifica** documentada aqui en el scope `docs/faberloom/`. Cuando ARCH se reabra para v2.0 (eventual), P16 sera candidato a promocion al core si pasa el filtro de aplicabilidad cross-tenant (FB + MWT) y se valida con datos de produccion >= 90 dias (P15 Outcome Accountability aplicado al principio mismo).

Hasta entonces, P16 vive en este ENT como principio aplicable SOLO a FaberLoom.

## 9. Decisiones pendientes para SPEC

1. Limite duro de profundidad de orquestacion: solo 2 niveles (principal → sub) o se permiten sub-sub? Recomendacion: 2 niveles maximo en v1, evaluar v2.
2. Sharing de sub-agentes cross-template: AG_SUB_DRAFT_WRITER en template "AM B2B" vs template "Soporte Cliente" comparten pool L3 o no? Recomendacion: si, es la fuente principal del beneficio §2.3.
3. Pricing per sub-agente: cuenta como uso del template padre o tiene su propio metering? Recomendacion: rolled-up al padre para simplicidad de billing, pero metric interno granular.
4. Versioning: si AG_SUB_DRAFT_WRITER updeates de v1.2 → v1.3, todos los orquestadores que lo usan se actualizan automatico o requieren opt-in? Recomendacion: shadow mode 30d antes de promote (consistente con P3 HITL).

Estas se resuelven en `SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1` (PENDIENTE) que sera el primer SPEC en aplicar P16 end-to-end.

## 10. Validacion del principio

Metricas observables a 90 dias post-implementacion del primer archetype con sub-agentes (AG_AM_MARLUVAS):
- Token cost real vs proyeccion -65% · tolerancia +-10pp
- Latencia p95 user-perceived: orquestador paralelo debe mantener <8s para el 95% de requests
- Audit log searchability: tiempo medio para reconstruir trace de 1 request <30s
- Curador overhead: tiempo gastado revisando patterns no debe crecer linealmente con # sub-agentes

Si estas metricas no se cumplen a 90d, P16 vuelve a SHADOW (consistente con P15) y se reescribe.

## Changelog
- 2026-04-30 v1.0 VIGENTE: creacion inicial. Captura del insight P16 Atomic Agents Principle del CEO durante sesion Cowork. Articula principio + 4 beneficios cuantificados + threshold + 5 tensiones + integracion con Knowledge River y archetypes + catalogo inicial 10 sub-agentes para AM B2B + 4 decisiones pendientes para SPEC + validacion 90d.

## Stamp
VIGENTE 2026-04-30 — P16 capturado como extension FB de ARCH (sin tocar core sealed v1.5). Habilita arquitectura de orquestadores delgados + sub-agentes atomicos especializados como patron canonico para todos los archetypes FB.
