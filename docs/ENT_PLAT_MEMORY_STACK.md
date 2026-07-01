# ENT_PLAT_MEMORY_STACK — Stack de memoria de agentes
id: ENT_PLAT_MEMORY_STACK
status: DRAFT
stamp: DRAFT — Pendiente aprobación CEO
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
version: 1.0
classification: ENTITY — Data pura inyectable.
refs: ENT_PLAT_KNOWLEDGE, ENT_PLAT_INFRA, ENT_PLAT_AGENTIC, ENT_PLAT_AGENT_ORCHESTRATION, ENT_PLAT_LLM_ROUTING, ENT_GOB_PENDIENTES
aplica_a: [SHARED]

---

## A. Propósito

Definir el stack canónico de memoria para los agentes de MWT separando dos capas distintas:

1. **KB canónica** — markdown versionado en git, indexado en pgvector. Fuente de verdad. Cubierto por `ENT_PLAT_KNOWLEDGE`.
2. **Memoria operativa de agentes** — estado conversacional, contexto de sprint, históricos de cliente B2B, preferencias detectadas. Esta entidad cubre esta capa.

Existe un riesgo recurrente de mezclar ambas. Esta entidad fija la separación y define la herramienta para la capa operativa.

---

## B. Principios

1. **KB canónica manda.** La memoria operativa asiste, nunca reemplaza. Memoria de agentes NO alimenta KB sin pasar por gate `indexa`.
2. **Self-host primero.** Toda memoria operativa vive en infraestructura propia (Postgres existente). No se entregan datos operativos a SaaS de memoria sin justificación explícita por caso de uso.
3. **CEO-ONLY aislado a nivel de infra.** Datos CEO-ONLY nunca tocan capa de memoria de agentes. Profile/namespace dedicado o storage separado.
4. **Agnóstico de proveedor.** La capa operativa debe ser portable. Lock-in con cualquier vendor (Cloudflare, Mem0, Zep) requiere decisión CEO documentada.
5. **Escalá cuando duela, no cuando el blog asuste.** Cambios de stack se justifican por dolor medido, no por hype.

---

## C. Decisión arquitectónica

### C1. Capa KB canónica — pgvector queda

**Decisión:** mantener pgvector en Django + Postgres. NO migrar a Vectorize, Pinecone, Qdrant ni Weaviate.

**Justificación:**

| Razón | Evidencia |
|-------|-----------|
| Filtros compuestos obligatorios | 4 tiers visibilidad × 10 dominios × 8 tipos + `ceo_only_sections` exigen SQL estándar (JOIN, JSONB, CTEs). Vectorize topa en operadores básicos sin AND/OR anidado, filtro completo en 2048 bytes JSON. |
| Atomicidad transaccional del gate `indexa` | pgvector lo da nativo con Postgres. Vectorize/Pinecone son eventually consistent. |
| Sweet spot de escala | 1-5M vectores proyectados (12 meses) → pgvector HNSW responde p95 5-8ms (Neon benchmark). |
| Dirección de migración 2025 | Supabase publicó `vec2pg` para migrar HACIA pgvector desde Pinecone/Qdrant. Tendencia confirmada. |
| CEO-ONLY row-level isolation | Postgres RLS lo hace nativo, sin doble sistema de control de acceso. |

### C2. Capa memoria operativa — Letta self-hosted

**Decisión:** adoptar **Letta (ex-MemGPT)** como capa de memoria operativa para agentes (Claude Code en sprints, agentes n8n, chatbot Amazon FBA, agentes de cliente B2B).

**Justificación:**

| Razón | Evidencia |
|-------|-----------|
| Apache-2.0 self-host | Cero costo de licencia, cero lock-in. |
| pgvector NATIVO como store | Aprovecha Postgres existente. No suma servicio nuevo. |
| State machine tipo OS | Encaja con orquestación multi-agente sprint-driven (PLB_ORCHESTRATOR FROZEN). |
| Madurez | 11K+ stars GitHub, activo, comunidad sólida. |
| Path de upgrade sin refactor | Letta Cloud existe si en el futuro se quiere modo gestionado. Misma API. |

**Alternativas evaluadas y descartadas:**

| Producto | Estado abril 2026 | Veredicto |
|----------|-------------------|-----------|
| Cloudflare Agent Memory | Private beta sin fecha GA, sin precio público | No esperar. Lock-in Workers fuerte. Reevaluar post-GA. |
| Mem0 Pro | $249/mes | Caro vs Letta self-host gratis con función equivalente. Mem0 OSS es alternativa pero Letta tiene mejor encaje con Postgres. |
| Zep Cloud Flex | $125/mes (50K créditos) | Caro. Considerar solo si Letta no cubre temporal knowledge graph para FBA histórico. |
| Zep Community Edition | DEPRECADA 2025 | Descartado. Solo motor Graphiti sigue OSS. |
| LangMem | SDK MIT, no servicio | No aplica como capa standalone; es biblioteca para LangGraph. |
| Pinecone / Qdrant / Weaviate | DBs vectoriales | No son productos de memoria. Resuelven storage, no extracción/clasificación/supersession. |

### C3. Path de escala pgvector

Cuando pgvector estándar deje de alcanzar (>10M vectores o índice no cabe en RAM):

**Plan A — pgvectorscale** (Tiger Data, mayo 2025): extensión drop-in sobre pgvector.
- 471 QPS @ 99% recall en 50M vectores × 768 dims (benchmark Tiger Data).
- 11.4× Qdrant. p95 28× menor que Pinecone s1.
- No requiere migrar datos. Mismo Postgres.

**Plan B — solo si pgvectorscale no alcanza:** Qdrant self-hosted por su filtrado superior. NUNCA Vectorize para KB canónica.

---

## D. Arquitectura 3 capas

```
CAPA 1 — KB canónica (git + ~280 markdown files)
         ↓ indexa (gate 9-check)
CAPA 2 — Retrieval KB (Django + pgvector + pgvectorscale futuro)
         ↓ referencia
CAPA 2.5 — Memoria operativa (Letta self-hosted con pgvector nativo)
         ↓ recall
CAPA 3 — Ejecutores (Claude Code, n8n, chatbots, agentes B2B)
```

**Reglas de la pila:**
- Capa 1 manda. Capa 2 indexa. Capa 2.5 asiste. Capa 3 ejecuta.
- Memoria agentes NUNCA alimenta KB sin gate.
- CEO-ONLY vive solo en Postgres directo (Capa 2 con filtro), nunca en Capa 2.5 sin profile aislado.

---

## E. Letta — plan de adopción

### E1. Profiles propuestos (namespaces de memoria aislados)

| Profile | Caso de uso | Visibilidad | Dueño |
|---------|------------|-------------|-------|
| `mwt-sprint-active` | Estado de sprint actual + decisiones CEO | INTERNAL | CEO + Claude Code |
| `mwt-client-marluvas` | Histórico de pedidos, preferencias, FX | PARTNER_B2B | Agente comercial |
| `mwt-client-tecmater` | Idem | PARTNER_B2B | Agente comercial |
| `mwt-client-sondel` | Idem | PARTNER_B2B | Agente comercial |
| `mwt-rana-walk-ops` | Tickets FBA, devoluciones, issues por SKU | PARTNER_B2B | Chatbot Amazon |
| `mwt-ceo-only` | Notas privadas, decisiones no publicadas | CEO-ONLY | Solo CEO |

### E2. Piloto

**Objetivo:** validar Letta self-hosted contra `mwt-sprint-active` durante 4 semanas antes de expandir.

**Criterios de éxito:**
- Reducción medible de tokens de input en sesiones Claude Code (re-inyección de contexto).
- Cero filtración cruzada entre profiles en testing.
- Tiempo recall < 500ms p95.
- Operación estable sin intervención manual.

**Esfuerzo estimado:** 4-6 horas Ale (Docker compose + config Postgres + integración cliente Python).

### E3. Reglas de uso

1. CEO-ONLY: profile dedicado, jamás cross-reference entre profiles.
2. Toda memoria escrita por agente debe tener `provenance` (qué evento la generó).
3. Memorias clasificadas como Fact/Instruction tienen supersession (versión nueva reemplaza la previa con forward pointer).
4. Backup semanal del store Letta + Postgres.
5. Si Letta detecta una memoria que contradice contenido VIGENTE de KB, gana KB. Memoria se marca como `disputed` y se loguea para revisión.

---

## F. Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|-----------|
| Memoria agentes contamina KB canónica | Separación de bases. Agentes NO escriben en `knowledge_chunks`. Pipeline distinto. |
| CEO-ONLY filtrado entre profiles | Profile dedicado + tests automatizados de cross-profile leak. |
| Letta deja de mantenerse | Apache-2.0 + 11K stars + fork posible. Backup mensual del esquema. |
| Agentes confían en Letta y dejan de leer KB | Reforzar en SKILL/PLB: Letta = contexto reciente, KB = verdades. Periodically test. |
| Calidad extracción en ES/PT code-switching | Validar en piloto antes de escalar a clientes B2B. Si falla, fallback a manual. |
| Sprint gate saltado "porque ya está en Letta" | Regla explícita en este ENT: nada entra a KB sin gate. |

---

## G. Costos

**Marginales sobre stack actual:**
- Letta self-host: $0 licencia.
- Postgres: ya existente, no suma costo.
- Container Letta: ~512 MB RAM, ~0.25 CPU. Cabe en headroom Hostinger KVM 8.

**Si se decide complementar con Cloud (a futuro):**
- Letta Cloud Pro: $20/mes (referencia, sin compromiso).
- Cloudflare Agent Memory: sin precio público (private beta, esperar GA para evaluar).

**No se compromete presupuesto en esta fase.** Piloto = costo $0.

---

## H. Pendientes derivados (referenciados en ENT_GOB_PENDIENTES)

- CEO-34 Decidir: ¿piloto Letta `mwt-sprint-active` sí/no? (4 semanas, esfuerzo 4-6h Ale).
- CEO-35 Si CEO-34 = sí, definir métricas de éxito y baseline de tokens pre-piloto.
- POL_MEMORIA_DISCLOSURE.md por crear cuando haya cliente B2B con memoria persistente de sus datos (LGPD/CCPA opt-in).
- Reevaluar Cloudflare Agent Memory cuando salga de private beta (esperar GA + precio público).

---

## I. Fuentes primarias verificadas (2026-04-18)

| Fuente | URL |
|--------|-----|
| Cloudflare Agent Memory anuncio | https://blog.cloudflare.com/introducing-agent-memory/ |
| Vectorize pricing | https://developers.cloudflare.com/vectorize/platform/pricing/ |
| Vectorize limits | https://developers.cloudflare.com/vectorize/platform/limits/ |
| Tiger Data pgvector vs Qdrant | https://www.tigerdata.com/blog/pgvector-vs-qdrant |
| Supabase vec2pg | https://supabase.com/blog/vec2pg |
| Letta repo | https://github.com/letta-ai/letta |
| Letta pricing | https://www.letta.com/pricing |
| Mem0 pricing | https://mem0.ai/pricing |
| Zep pricing | https://www.getzep.com/pricing/ |
| Zep Community deprecada | https://github.com/getzep/zep |

---

Stamp: DRAFT — Pendiente aprobación CEO

Changelog:
- v1.0 (2026-04-19): creación inicial. Decisión: pgvector queda + Letta self-host como capa operativa. Vectorize/Pinecone/Qdrant descartados para KB. pgvectorscale como path de escala. Cloudflare Agent Memory en watch-list para reevaluación post-GA. Origen: swarm de verificación 2026-04-18 contra fuentes primarias.
