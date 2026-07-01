---
id: SPEC_FB_EVOLUTION_ROADMAP
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FaberLoom (IDX_FB_FOUNDATION_BETA)
tipo: spec
last_review: 2026-06-02
stamp: DRAFT -- 2026-06-02 -- creado en Cowork (generated_staging), pendiente promocion a canonico
aplica_a: [FaberLoom, MWT]
---

# SPEC_FB_EVOLUTION_ROADMAP -- Secuencia de Construccion por Modulos (walking-skeleton-first)

> Contrapeso de ejecucion a los ~20 SPEC_FB de diseno. No define QUE es FaberLoom
> (eso ya esta), sino EN QUE ORDEN se construye. Origen: sesion de arquitectura
> funcional Cowork 2026-06-02. Decision rectora del CEO: el chat space con routing
> es el primer modulo; de el depende todo lo demas.

## A. Diagnostico que motiva este roadmap

FaberLoom esta sobre-disenado y sub-validado: ~20 SPECs (casi todos DRAFT), 168 agentes
catalogados, 702 assertions, 13 sprints planeados, 8 planos funcionales -- y 0 flujos en
produccion, corpus golden vacio, salud KB AMARILLO. El riesgo no es tecnico, es de
SECUENCIA. Este roadmap fija el orden de construccion para emparejar la validacion con
el diseno.

## B. Principio rector

1. **Cada fase agrega UNA capacidad sobre algo que ya respira.** Nunca una capa
   horizontal completa. Si una fase no produce un sistema que corre end-to-end, esta
   mal cortada.
2. **Diseno != orden de build.** Disenamos en orden conceptual (arena -> routing ->
   modulos). Se construye casi al reves (router delgado primero, arena casi al final),
   porque hasta que algo corre no hay nada que medir.
3. **Profundidad antes que amplitud.** La amplitud (mas verticales, mas agentes, mas
   superficies) se gana cuando la profundidad de UN flujo ya esta validada.
4. **Walking skeleton:** un caso real cruza el sistema entero por su version mas fina
   antes de engrosar cualquier modulo.

## C. Las 7 fases

### Fase 0 -- Consolidar (pre-codigo)
- Reconciliar el plano de control de IA, hoy solapado: SPEC_FB_AI_CONTROL_PLANE +
  SPEC_FB_EVAL_ARENA + router (ENT_PLAT_LLM_ROUTING + SPEC_AI_GOV). Jerarquia clara:
  control plane = politica; arena = medicion; router = ejecucion.
- Congelar el alcance del slice de Fase 1.
- **Listo cuando:** un solo doc dice quien decide politica / quien mide / quien ejecuta.

### Fase 1 -- Chat space + routing (walking skeleton del sustrato)
Es el primer modulo y el cimiento. Un prompt real entra, se clasifica, se enruta, toca
la KB, responde.
- **Activa (minimo de cada plano):** router como async_pre_call_hook en LiteLLM
  (clasifica tier + allow-list + gate, con tabla de scoring A MANO, sin arena) -
  RAG/KB L0-L1 + RAG security firewall - 1 agente conversacional draft-first - API
  chat+sesion - auth/RLS por tenant - audit del turno - UNA vista de chat + WS realtime.
- **Construir de adentro hacia afuera:** router (hook + tabla manual) -> RAG/KB ->
  agente -> API -> chat UI. UI bonita = lo ultimo.
- **Caso real que lo cruza:** chat contra la KB de MWT (consultas operativas reales).
- **Listo cuando (5 fitness):** (1) clasifica tier en <20ms; (2) respeta allow-list por
  data_class, fail-closed verificado; (3) responde con grounding de la KB sin alucinar;
  (4) savings ledger muestra costo < baseline premium a calidad equivalente; (5) un
  segundo tenant no ve nada del primero (contamination test).

### Fase 2 -- Primer caso de negocio (sobre el chat space)
La cotizacion B2B corre DENTRO del chat space.
- **Activa:** agent composition (orquestador + sub-agentes atomicos P16/P17) - workflow
  engine - integration layer (salida WhatsApp) - document state machine - evidence bundle.
- **Caso real:** RFQ entra -> agente arma proforma -> humano aprueba -> sale (flujo A del
  service blueprint B1, tenant MWT/Marluvas).
- **Listo cuando:** una proforma real, aprobable, producida end-to-end.

### Fase 3 -- La arena reemplaza la tabla manual
La calidad se mide, no se adivina. La tabla de scoring a mano de Fase 1 se sustituye por
la salida de la arena.
- **Activa:** SPEC_FB_EVAL_ARENA completo (registro de APIs, evaluacion ciega, panel de
  jueces familias distintas, Elo + gate) - golden corpus poblado (curacion) - savings
  ledger con baseline - guardrails F-A-C-T.
- **Por que aqui y no antes:** la arena necesita trafico real (canary) y golden cases
  extraidos de produccion, que solo existen tras F1-F2.
- **Listo cuando:** el router elige por datos medidos; ahorro reportado con calidad mantenida.

### Fase 4 -- Aprendizaje
El sistema mejora con uso.
- **Activa:** Knowledge River L2 -> L3 (pool colectivo k-anon >=5) -> L4 (indexado
  firmado) - consolidation module - skill composition (learned overlay) - rol curador.
- **Por que aqui:** destilar best practices colectivas exige volumen de interacciones.
- **Listo cuando:** best practices destiladas con gate humano; mejora medible del agente.

### Fase 5 -- Multi-tenant real + APIs abiertas
Segundo tenant; self-service de modelos.
- **Activa:** multi-tenancy completo - tenant bootstrap seed - herencia/override de config
  en cascada - registro abierto de APIs - BYO-keys (disponibilidad heredada, estricto +
  hibrido opt-in) - contamination test suite a fondo.
- **Por que aqui:** la herencia de config y el aislamiento solo se ganan su complejidad
  con un segundo inquilino; antes es teoria.
- **Listo cuando:** 2 tenants aislados, uno con sus propias APIs heredando ruteo;
  contamination tests pasan.

### Fase 6 -- FaberLoom-en-MWT (MCP) + escala
Exponer a la operacion + ampliar.
- **Activa:** MCP server (FaberLoom expone capacidades a Cowork/n8n) - resto de las
  superficies UI - agent builder 168 - segundo vertical - DMS adapters.
- **Por que al final:** exponer o ampliar algo no validado solo propaga lo inmaduro.
- **Listo cuando:** MWT opera via FaberLoom sin friccion; otro vertical arranca.

## D. Dependencias duras (resumen)

| Modulo | No puede ir antes de | Razon |
|---|---|---|
| Routing | nada | es de lo que cuelga todo |
| Agentes/workflow | chat+routing (F1) | sin canal ni router no tienen donde correr |
| Arena | F1-F2 con uso real | necesita trafico + golden cases de produccion |
| Knowledge River L3+ | volumen de F1-F4 | destilar colectivo exige muchas interacciones |
| Multi-tenant real | 1 tenant funcionando (F1-F4) | aislamiento/herencia solo se gana con 2do inquilino |
| MCP / escala | capacidades probadas (F1-F5) | exponer lo inmaduro lo propaga |

## E. Diferidos a proposito (Fase 5-6)

Agent builder de 168 agentes, segundo vertical, DMS adapters, las 14 superficies UI
restantes, panel de 3 jueces, L4 firmado. No estan mal disenados: son amplitud, y la
amplitud se gana tras validar profundidad. Aplica a la secuencia de build el mismo
instinto "no implica" que ya tienen los SPECs en su diseno.

## F. Relacion con otros docs

- Detalla el orden de construccion de los modulos descritos en SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT
  y AUDIT_FABERLOOM_B1_SERVICE_BLUEPRINT (15 superficies).
- El routing de Fase 1 implementa SPEC_LLM_ROUTING_ARCHITECTURE (L1 Clasificador + L2
  Dispatcher arena-aware) y ENT_PLAT_LLM_ROUTING.
- La arena de Fase 3 es SPEC_FB_EVAL_ARENA.
- No reabre PLB_FB_FOUNDATION_BETA (plan firmado de 13 sprints); lo complementa con la
  vista de secuencia walking-skeleton-first. Numeracion conciliada con SPEC_FB_BUILD_SEQUENCE v3.0 (2026-06-13).

## G. Reglas inquebrantables

1. Ninguna fase se cierra sin su fitness function cumplida con un caso real.
2. No engrosar un modulo antes de que el walking skeleton lo cruce.
3. El router (Fase 1) nace con tabla de scoring a mano; la arena (Fase 3) la reemplaza
   sin reescribir el router.
4. Profundidad antes que amplitud: nada de Fase 5-6 arranca con F1-F4 sin validar.

---

Changelog:
- v1.0 (2026-06-02): Creacion. 7 fases (0-6) walking-skeleton-first, dependencias duras,
  fitness functions, diferidos. Decision rectora CEO: chat space + routing primero. Origen:
  sesion de arquitectura funcional Cowork 2026-06-02. DRAFT en generated_staging, pendiente
  promocion via sync + indexacion en IDX_ARQUITECTURA_FUNDACIONAL + MANIFIESTO. ASCII puro.
