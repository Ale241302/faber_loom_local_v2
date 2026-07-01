# ENT_FABERLOOM_INSIGHTS_KIMI_FUGU — Insights Estratégicos Kimi Swarm (Sakana Fugu)
id: ENT_FABERLOOM_INSIGHTS_KIMI_FUGU
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: ENT
stamp: VIGENTE — 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: ENT_FABERLOOM_INSIGHTS_KIMI.md · SPEC_LLM_ROUTING_ARCHITECTURE.md · SPEC_ACTION_ENGINE.md · ARCH_AGENT_PRINCIPLES.md · ENT_PLAT_MEMORY_STACK.md
fuente: Kimi Swarm #7 — 4 dimensiones paralelas · fugu_final_report.md + fugu_dim01-04.md

---

## Contexto

Séptima investigación Kimi Swarm. Foco: arquitectura interna de Sakana Fugu (lanzamiento
2026-06-22) contrastada contra el diseño FaberLoom. 4 dimensiones: arquitectura interna,
routing y selección de modelo, compliance y aislamiento, contrastación directa con el
proyecto. Research raw en archivos locales (no indexables en KB).

Complementa: ENT_FABERLOOM_INSIGHTS_KIMI (arquitectura agentes) ·
ENT_FABERLOOM_INSIGHTS_KIMI_EMAIL (conectividad) ·
ENT_FABERLOOM_INSIGHTS_KIMI_RUFLO (Tier 0, P14).

Archivos raw locales (no indexar):
- fugu_dim01.md — Arquitectura interna
- fugu_dim02.md — Routing y selección
- fugu_dim03.md — Compliance y aislamiento
- fugu_dim04.md — Contrastación con FaberLoom
- fugu_landscape.md — Contexto mercado
- fugu_final_report.md — Reporte consolidado con citas

---

## F01 — L1 de FaberLoom debería ser clasificador de embeddings, no LLM

**Confianza:** High
**Aplica a:** FaberLoom
**Impacta:** SPEC_LLM_ROUTING_ARCHITECTURE.md — L1 Clasificador

TRINITY (base de Fugu standard) usa un SLM de 0.6B con un head de ~10K-20K parámetros.
La decisión de routing es un softmax sobre hidden states en un único forward pass. El
texto generado se descarta — el modelo nunca genera JSON de routing.

FaberLoom planea usar Haiku para el L1. Esto es ~10x más caro en latencia y costo de
lo necesario para una clasificación binaria/categórica.

Implicación: el L1 puede ser un clasificador ligero sobre embeddings (pgvector disponible).
Para MVP Haiku es aceptable como proxy. Arquitectura target: clasificador propio, no LLM
generativo. Decisión a revisar antes de Fase 2.

---

## F02 — Roles Thinker/Worker/Verifier son research-only; en producción Fugu solo selecciona modelo

**Confianza:** High
**Aplica a:** FaberLoom
**Impacta:** SPEC_LLM_ROUTING_ARCHITECTURE.md — L2 Dispatcher

El technical report confirma que en producción Fugu always dispatches the query to the
selected model as a worker para minimizar latencia. Los roles de TRINITY son paradigma
de entrenamiento, no de ejecución.

Implicación: si FaberLoom diseña un L2.5 advisory para Fase 2, no necesita roles
complejos. Selección de modelo + modo (single/dual/ensemble) es suficiente.

---

## F03 — Memoria de dos niveles de Fugu mapea directamente a FaberLoom

**Confianza:** High
**Aplica a:** FaberLoom
**Impacta:** ENT_PLAT_MEMORY_STACK.md

Fugu-Ultra implementa dos niveles:
- Intra-workflow isolation: contexto aislado por agente dentro de una misma tarea
- Inter-workflow shared memory: memoria persistente entre requests del mismo cliente

Mapeo directo a FaberLoom: intra-RFQ aislamiento (ClientScopedManager) + inter-RFQ
memoria persistente por tenant en PostgreSQL. Confirma que el patrón de dos niveles
es correcto y producción-probado. Usar como input para cerrar deuda de vocabulario
en memory stack.

---

## F04 — Fugu no tiene fallback runtime; solo retries HTTP

**Confianza:** Medium
**Aplica a:** FaberLoom
**Impacta:** SPEC_ACTION_ENGINE.md — D8 Circuit Breaker

No existen circuit breakers ni health checks en Fugu. Solo retries HTTP (5 stream,
4 request). Latencia reportada: 11 seg a 4+ min. Timeout CLI 2 horas.

Implicación: D8 (circuit breaker) en el Action Engine es una ventaja real, no overhead.

---

## F05 — Fugu 100% learned vs FaberLoom 100% determinístico — divergencia fundamental

**Confianza:** High
**Aplica a:** FaberLoom
**Impacta:** ARCH_AGENT_PRINCIPLES.md — P14 · SPEC_LLM_ROUTING_ARCHITECTURE.md

Fugu no tiene equivalente a P14 (Deterministic First → LLM Fallback → Human Gate).
Routing completamente aprendido vía SFT + evolutionary strategies o GRPO/RL. Sin veto
determinístico. Riesgo ModelFingerprint máximo.

Implicación: P14 validado como decisión correcta. La divergencia con Fugu es ventaja.

---

## F06 — L2.5 advisory hybrid es el camino correcto para Fase 2

**Confianza:** High
**Aplica a:** FaberLoom
**Impacta:** SPEC_LLM_ROUTING_ARCHITECTURE.md — Fase 2 · Q1-Q12

Paper ACAR (arXiv:2602.21231) propone hybrid approach: capa determinística como veto
inmutable + capa learned que sugiere pero no impone. Fugu usa el extremo opuesto
(100% learned), invalidando compliance y multi-tenant.

Implicación para Fase 2 de SPEC_LLM_ROUTING_ARCHITECTURE:
1. Mantener L1 determinístico como veto inmutable (no bypasseable)
2. Agregar capa que sugiere modelo/modo basada en evidencia del Token Ledger
3. Sugerencia rechazable por L1 sin log de error — advisory, no decisivo

Resuelve Q-serie routing adaptive sin activar ModelFingerprint (P13).

---

## F07 — Fugu sin multi-tenant, RLS ni data residency — confirma arquitectura FaberLoom

**Confianza:** High
**Aplica a:** FaberLoom
**Impacta:** SPEC_ACTION_ENGINE.md — D5 · D9

Sin aislamiento por tenant. Sin clasificación de datos. Sin data residency. Sin DPAs
con providers del pool. Opt-out cubre solo a Sakana. EU/EEA bloqueado sin timeline.

Implicación: LiteLLM self-hosted + RLS + N0-N4 + tenant_model_allowlist es correcto.
Fugu es inusable para datos N3/N4. Acción: configurar ZDR directamente en LiteLLM.

---

## F08 — Model attribution en D10 es ventaja competitiva real

**Confianza:** High
**Aplica a:** FaberLoom
**Impacta:** SPEC_AUDIT_MODULE.md — D10

Fugu no expone qué modelo procesó qué dato por diseño intencional. Bloquea compliance
bancario y sectores regulados.

Implicación: D10 debe incluir model_attribution explícito — qué modelo, qué versión,
qué timestamp. Diferencia entre poder vender a sectores regulados o no.

---

## F09 — Más orquestación no siempre es mejor — valida L1 de FaberLoom

**Confianza:** High
**Aplica a:** FaberLoom
**Impacta:** SPEC_LLM_ROUTING_ARCHITECTURE.md — L1 Clasificador

Fugu standard supera a Ultra en SciCode (60.1 vs 58.7) y τ³ Banking (21.7 vs 20.6).
Costo real Ultra: ~$10/mensaje pesado, $200/mes para menos de 3 hrs/semana.

Implicación: L1 clasificador de FaberLoom arquitectónicamente correcto. ROI 20x para
tareas rutinarias B2B vs orquestación innecesaria.

---

## F10 — Reward binario + GRPO suficiente para orquestador futuro

**Confianza:** High
**Aplica a:** FaberLoom
**Impacta:** SPEC_LLM_ROUTING_ARCHITECTURE.md — post-gate F2

Conductor usa reward r=0/0.5/1. Sin costo ni latencia en reward — eficiencia emerge
de GRPO. No hace falta diseñar rewards complejos.

Implicación: si FaberLoom entrena orquestador propio (post-gate F2, 18-24m), el reward
puede ser binario. Registrar para cuando gate F2 abra.

---

## Resumen por prioridad

| Insight | Prioridad | Acción |
|---|---|---|
| F06 L2.5 advisory hybrid | P0 | Agregar a Q1-Q12 propuesta Fase 2 routing |
| F01 L1 clasificador embeddings | P0 | Agregar a Q1-Q12 decisión LLM vs clasificador |
| F08 model_attribution D10 | P0 | Campo explícito en SPEC_AUDIT_MODULE siguiente bump |
| F03 memoria dos niveles | P1 | Input para ENT_PLAT_MEMORY_STACK |
| F07 ZDR por provider | P1 | Configurar en LiteLLM antes de primer tenant |
| F05 P14 validado | P1 | Sin acción — confirma decisión existente |
| F04 circuit breakers | P1 | Sin acción — D8 ya implementado |
| F02 roles research-only | P2 | Sin acción — evitar complejidad en L2.5 |
| F09 orquestación selectiva | P2 | Sin acción — confirma L1 |
| F10 reward binario | P3 | Registrar para gate F2 |

---

## 5 preguntas para sesión Fugu (Codex)

P1. ¿Cómo auditar qué modelo procesó qué dato cuando el routing es proprietary by design?
¿Hay plan de attribution logs para enterprise o es restricción permanente?

P2. ¿Qué pasa si el Conductor enruta datos de un cliente regulado a un provider sin DPA?
¿Existe algún hard veto determinístico que un admin pueda configurar?

P3. ¿Por qué Fugu standard supera a Ultra en SciCode y τ³ Banking?
¿Tienen heurística interna de cuándo orquestar vs cuándo no?

P4. ¿Cuál es el timeline concreto para GDPR compliance y qué cambios arquitectónicos requiere?
¿Es solo paperwork o requiere exponer el routing?

P5. ¿Cómo justifican el costo de Ultra ($10/mensaje, $200/mes < 3 hrs/semana) para
workflows B2B de alta frecuencia y baja complejidad con 30 casos/semana?

---

Changelog:
- v1.0 (2026-06-24): Creación. 10 insights, 5 preguntas para Fugu.
  Origen: Kimi Swarm #7 (4 dimensiones, fugu_dim01-04.md + fugu_final_report.md).
