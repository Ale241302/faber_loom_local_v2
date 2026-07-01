---
id: MANIFIESTO_APPEND_20260430b_P16_DECOMPOSITION
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza
type: manifiesto_append
stamp: VIGENTE 2026-04-30
fecha: 2026-04-30
agente: Cowork (planificacion + redaccion) + CEO (autoria del insight arquitectonico)
aplica_a: [FaberLoom]
relacionado_con:
  - MANIFIESTO_APPEND_20260430_KNOWLEDGE_RIVER
  - ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1
  - ARCH_AGENT_PRINCIPLES (NO modificado · sealed core v1.5)
---

# MANIFIESTO_APPEND_20260430b_P16_DECOMPOSITION

## Que paso
Sesion Cowork 2026-04-30 segunda iteracion del dia. Tras canonizar Knowledge River (manifiesto a), la conversacion derivo a casos de uso flagship FB v1: vertical Account Management B2B (caso real Marluvas/Tecmater donde un agente gerente de cuenta gestiona inbound de cliente — emails, llamadas, propuestas).

Al revisar la lista granular de acciones esperadas del AM, CEO formulo el insight arquitectonico mayor:

> "es que veo muy granular las acciones... el agente principal se convierte en un distribuidor de tareas a sub agentes que se especializan en solo una cosa... aca lo que se me ocurre es que este tipo de necesidad se elabora con un agente orchestador"

Esto se canonizo como **P16 Atomic Agents Principle**, articulado en `docs/faberloom/ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1.md` (192 lineas).

## Decision arquitectonica clave

Los archetypes principales (AM, soporte, etc) deben implementarse como **orquestadores delgados** que delegan a **sub-agentes atomicos especializados**. NO ejecutan tareas complejas internamente.

```
AG_PRINCIPAL (orquestador · stateful · contexto cuenta)
  ├── AG_SUB_TASK_A (atomico · stateless · 1 capacidad)
  ├── AG_SUB_TASK_B (atomico · stateless · 1 capacidad)
  └── AG_SUB_TASK_C (atomico · stateless · 1 capacidad)
```

## Beneficios cuantificados

| Beneficio | Magnitud |
|---|---|
| Token cost reduction | -65% promedio · ~$11.7k/ano MWT · ~$58k/ano 5-tenants v2 |
| Audit precision | granular per sub-call (debug quirurgico, atribucion de costo) |
| Learning concentration | sub-agentes reutilizables reciben pool cross-archetype |
| Model routing | 4/10 sub-agentes Sonnet · 4/10 Haiku · 2/10 sin LLM |

## Threshold canonico

Si un componente solo hace **1 LLM call** y no tiene memoria propia → NO es sub-agente, es **skill_package determinista**. Esto evita sobre-fragmentacion.

## Catalogo inicial · 10 sub-agentes para AM B2B

AG_SUB_EMAIL_CLASSIFIER (Haiku) · AG_SUB_DRAFT_WRITER (Sonnet) · AG_SUB_PROFORMA_BUILDER (Sonnet) · AG_SUB_SAP_QUERY (Haiku+tool) · AG_SUB_VOICE_TRANSCRIBER (Whisper) · AG_SUB_PRE_CALL_SUMMARIZER (Haiku) · AG_SUB_COMPLIANCE_CHECKER (Haiku) · AG_SUB_ESCALATION_ROUTER (deterministic) · AG_SUB_PRICING_CALCULATOR (Python puro) · AG_SUB_INVENTORY_FETCHER (tool only)

## Relacion con ARCH_AGENT_PRINCIPLES core sealed v1.5

P16 **NO modifica** `docs/ARCH_AGENT_PRINCIPLES.md` (sealed CORE BLINDADO commit `9ecd190`). Vive como **extension FB-specifica** en `docs/faberloom/ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1.md`. Cuando ARCH se reabra para v2.0, P16 sera candidato a promocion al core si pasa filtro cross-tenant (FB+MWT) y se valida con datos reales >=90 dias (P15 Outcome Accountability aplicado al principio mismo).

Hasta entonces, P16 aplica SOLO a FaberLoom.

## Archivos creados/modificados en esta indexa

| Archivo | Accion |
|---|---|
| docs/faberloom/ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1.md | NUEVO · 192 lineas · principio + beneficios + threshold + tensiones + catalogo |
| docs/RW_ROOT.md | bump v4.8.9 → v4.8.10 + entry changelog |
| docs/DASHBOARD_SNAPSHOT.md | bump v12.0 → v12.1 + conteos +1 docs/ raiz +1 docs/faberloom/ |
| docs/MANIFIESTO_APPEND_20260430b_P16_DECOMPOSITION.md | NUEVO · este archivo |

## Pendientes post-merge

1. Crear `docs/faberloom/ENT_FB_SUB_AGENTS_LIBRARY_v1.md` con detalle completo de cada sub-agente: schema input/output, modelo, latency target, cost target, pool L3 propio, threshold de promocion shadow→active.
2. Crear `docs/faberloom/SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1.md` como primer SPEC end-to-end aplicando P16: AG_AM_MARLUVAS modelado con orquestador + sub-agentes desde dia 1.
3. Resolver 4 decisiones pendientes del SPEC: profundidad maxima orquestacion (rec: 2 niveles v1), sharing cross-template (rec: si), pricing per sub-agente (rec: rolled-up), versioning con shadow 30d (consistente con P3).
4. Actualizar `SPEC_FB_AGENT_BUILDER_v1` para que el flow conversacional del builder ofrezca componer archetype con sub-agentes del catalogo (no solo desde cero).
5. Definir CLI commands: `fbl subagent ls/create/test`, `fbl orchestrator inspect <archetype>`, `fbl trace <request_id>` para reconstruir grafo de sub-calls.
6. Validacion 90d: instrumentar metricas observables (token cost real vs proyeccion -65% +-10pp · latencia p95 <8s · audit log searchability <30s · curador overhead). Si no se cumplen, P16 vuelve a SHADOW y se reescribe (P15).

## Origen del insight clave

CEO durante discusion sobre granularidad de acciones del AM:
> "el agente principal se convierte en un distribuidor de tareas a sub agentes que se especializan en solo una cosa"

Y posteriormente:
> "este tipo de necesidad se elabora con un agente orchestador"

El insight cierra el ciclo arquitectonico del dia: Knowledge River define **donde vive el conocimiento** (templates como activos organizacionales con destilacion colegiada); P16 define **como se ejecuta el trabajo** (orquestadores delgados + sub-agentes atomicos). Ambos se refuerzan: pool L3 por sub-agente acelera convergencia de mejores practicas.

## Stamp
VIGENTE 2026-04-30 — Indexa del P16 Atomic Agents Principle. Habilita arquitectura canonica de orquestadores + sub-agentes atomicos para todos los archetypes FaberLoom. Complementa Knowledge River en la dimension de ejecucion. Listo para aplicarse en el primer SPEC vertical (Account Management B2B).
