# Kimi Swarm #6 — Prompt único para multi-agente

**Para:** Kimi K2.6 multi-agente
**De:** Álvaro (CEO Muito Work Limitada)
**Fecha:** 2026-05-06
**Pedido:** descomponé este prompt en 4 sub-agentes paralelos (uno por dimensión D1-D4) e investigá en profundidad cada una. Devolveme research bruto estructurado por dimensión más una síntesis ejecutiva al final.

---

## Contexto operativo (común a las 4 dimensiones)

Soy CEO de **Muito Work Limitada (MWT)** en Costa Rica. Estoy construyendo **FaberLoom**, SaaS B2B LATAM para PYMEs/fabricantes. Vertical inicial: cotización B2B de calzado de seguridad (safety_footwear). MWT es primer tenant validador. Verticales candidatos post-MVP: legal_practice, software_factory, insurance, medical_regulated, financial_advisory.

### Stack técnico cerrado (FROZEN)

| Componente | Tecnología |
|---|---|
| Backend | FastAPI + Pydantic AI |
| Base de datos | Supabase (PostgreSQL 16 + pgvector + RLS) |
| Gateway LLM | LiteLLM |
| Frontend | Next.js 15 |
| Cola async | ARQ + Redis |
| Canal primario | WhatsApp Business API |
| Hosting | Railway / Fly.io |
| Observabilidad | Langfuse + logging estructurado |
| Memoria persistente | Letta self-host |
| Identifiers | UUIDv7 client-side (no ULID) |

### MVP cerrado (60 días, 13 sprints firmados)

- 1 agente, 3-5 herramientas, 2 workflows (cobranza + proformas)
- **Single-agent, NO multi-agent** en MVP (decisión basada en MAST UC Berkeley NeurIPS 2025: 41-86.7% tasa fallo multi-agent + Data Processing Inequality + costo 2-5x tokens)
- Foundation Beta 2026-04-20 → 2026-06-14
- Compliance LATAM: CO + MX + CR + PA + BR (LGPD)
- 4 tiers pricing ($19-$2499/mes según data class N0-N4)

### Estado del repo KB

- 540 archivos .md (430 operativos), 10 dominios, taxonomía de 8 tipos canónicos (ENT/PLB/SCH/LOC/POL/IDX/SKILL/LOTE)
- Score actual capa 1 taxonomía: 7.0/10 (sobre-taxonomía documentada)
- Score actual capa 3 RAG: 9.1/10 P0_APPROVED_CANDIDATE post `SPEC_FB_RAG_SECURITY_FIREWALL_v1`
- Stack ya tiene: agent_run, audit_event con SHA-chain, eventing 4 capas (Postgres + outbox + Redis + WS), contract test harness con 30 fixtures Ciclope + 702 assertions, RBAC con 5 settings RLS, archetypes (7 tipos), P16 sub-agents atomic principle, learning model 2 capas (USER + COMMITTEE)

### Decisiones cerradas no negociables (NO reconsiderar)

1. Single-agent en MVP
2. Letta self-host para memoria
3. UUIDv7 client-side
4. Sealed/Open dual mode para skills/agents
5. Draft-first invariante absoluto (P3 ARCH_AGENT_PRINCIPLES)
6. Curaduría 2 capas separadas (USER personal + COMMITTEE org con k-anon ≥5)
7. Charter como término técnico interno; UI traduce por vertical

---

## Las 4 dimensiones del swarm

Investigar en paralelo. Cada dimensión cubierta por sub-agente independiente. NO repetir contexto entre dimensiones — cada una debe ser autocontenida en su output.

---

### D1 — Hybrid Retrieval con pgvector + BM25 + RRF

**Problema:** mi `SPEC_FB_RAG_SECURITY_FIREWALL_v1` cubre security (9.1/10) pero NO formaliza hybrid retrieval. En MVP single-agent (sin Agentic RAG), depender solo de vector similarity pierde queries con términos exactos (ej. "POL_ROGERS", "Marluvas modelo 50S5BR"). Necesito agregar componente C7 al SPEC.

**Investigá específicamente:**

1. **Implementación con pgvector + Postgres 16 nativo:**
   - ¿pgvector soporta BM25 nativo o requiere extensión adicional? (ver `pg_search` / `paradedb` / `tsvector` con ranking)
   - Índices necesarios: HNSW para vector, GIN para BM25, ¿coexisten en mismo schema?
   - Performance benchmark: latencia p50/p95 con 10K, 100K, 1M chunks
   - ¿Cómo se comporta con RLS multi-tenant? (filtro por tenant_id ANTES o DESPUÉS de hybrid scoring)

2. **Libraries Python production-ready:**
   - `rank_bm25` puro Python vs `pyserini` vs Postgres-native FTS
   - LlamaIndex `QueryFusionRetriever` vs LangChain `EnsembleRetriever`
   - Integración con Pydantic AI / FastAPI sync vs async
   - Pros/contras de cada uno con stack FaberLoom

3. **RRF (Reciprocal Rank Fusion) vs weighted alpha:**
   - Cuándo usar cuál
   - k=60 default ¿es válido para B2B LATAM B2B con queries en español/portugués?
   - ¿Cómo se calibra alpha para distintos tipos de query?

4. **Casos production reales 2025-2026:**
   - Empresas B2B que implementaron hybrid sobre pgvector (NO sobre Pinecone/Weaviate)
   - Métricas reportadas: improvement en MRR, NDCG, latencia
   - Gotchas conocidos (índices que se rompen, cost de re-indexar, etc.)

5. **Costo de mantenimiento del índice BM25:**
   - ¿Cuánto crece vs solo vector?
   - ¿Se actualiza incrementalmente o requiere full rebuild?
   - ¿Cuál es el overhead real para tenant con 100 docs vs 10K docs?

**Entregable D1:**
- Tabla de decisión: 2-3 stacks viables ranqueados con justificación
- Código prototype Python con FastAPI endpoint mínimo (`/search` que combina BM25 + vector + RRF)
- Métricas reales (no estimadas) cuando estén disponibles
- Recomendación final: cuál implementar en MVP FaberLoom

---

### D2 — KB Quality Monitoring continuo

**Problema:** mi `SPEC_FB_CONTRACT_TEST_HARNESS_v1` cubre fixtures (snapshot tests) pero NO eval continuo en producción. Necesito decidir si meto DeepEval + TruLens en MVP o lo difiero como deuda. Para decidir bien necesito costos reales y plan de implementación.

**Investigá específicamente:**

1. **DeepEval setup production:**
   - 4 métricas core (relevancy, faithfulness, context_precision, context_recall) con LLM judge
   - ¿Qué LLM se usa como judge? (GPT-4? Claude Sonnet? Self-hosted Llama?)
   - Costo por query evaluada (tokens consumidos)
   - Latencia: ¿corre online por query o batch nightly?
   - Integración con FastAPI + Langfuse: ¿duplica observabilidad o complementa?
   - Versiones: ¿cuál versión es estable producción 2026?

2. **TruLens setup production:**
   - Feedback functions: relevance, groundedness, context_relevance
   - Dashboard cost (¿requiere instancia separada? ¿integra con Langfuse?)
   - ¿Cómo se mantiene cuando el modelo cambia (ej. Claude Sonnet 4.7 → 4.8)?
   - Comparación con Langfuse evaluators nativos (¿hay overlap?)

3. **Freshness monitoring:**
   - Cómo se mide staleness en producción (timestamp de re-embed vs hash de source)
   - Threshold real recomendado: TDS dice 30d default, ¿qué dicen otras empresas?
   - Trigger de re-embed automático vs manual

4. **Embedding drift detection:**
   - Cosine distance threshold real (TDS sugiere 0.1) — ¿es agresivo o permisivo?
   - ¿Cuándo se dispara drift legítimo (modelo nuevo) vs falso positivo (variabilidad)?
   - Cómo se reconcilia con `firewall_ruleset_hash` y `requires_rescan` que ya tengo en chunk metadata

5. **Costo proyectado mensual:**
   - 1 tenant con 100 queries/día — costo total quality monitoring
   - 10 tenants — costo total
   - 100 tenants — costo total
   - Comparar contra MRR target del MVP ($59-89/mes Pro tier × N tenants)

6. **Decisión MVP vs deuda:**
   - ¿Qué % de tenants production realmente usan DeepEval+TruLens vs solo logs estructurados?
   - Equipos pequeños (1-3 devs) — ¿es factible mantener?
   - Plan B: ¿qué métricas mínimas con Langfuse solo (sin DeepEval/TruLens)?

**Entregable D2:**
- Tabla costo proyectado por tier de adopción
- Diagrama de integración con stack FaberLoom (FastAPI + Langfuse + LiteLLM)
- SPEC propuesto `SPEC_FB_KB_QUALITY_MONITORING_v1` con scope mínimo viable
- Recomendación final: MVP, fase 2, o deuda permanente

---

### D3 — Chunking strategies "by user query"

**Problema:** mis archivos KB están organizados por documento (taxonomía temática). TDS dice "chunk by user query, not document structure" con validación contra 10-12 questions por archivo. Esto cambia retrieval completo. Necesito convención canónica para `POL_CHUNKING_KB_v1`.

**Investigá específicamente:**

1. **Estado del arte chunking 2025-2026:**
   - Fixed-size chunking (deprecated, qué reemplazó)
   - Semantic chunking (clustering por embedding similarity)
   - Late chunking (Jina AI, retain document context)
   - Hierarchical chunking (parent-child relationships)
   - Sliding window con overlap
   - Chunk by user query (TDS approach)
   - **¿Cuál usar cuándo?** Tabla de decisión por caso de uso B2B

2. **Casos B2B reales que migraron de doc-based a query-based:**
   - Legal (bufetes con jurisprudencia, contratos)
   - Consulting (knowledge management interno)
   - Manufacturing (catálogos productos, specs técnicas)
   - Métricas pre/post: improvement en relevance, recall, user satisfaction

3. **Herramientas para "chunk by query":**
   - LlamaIndex `QueryParser` o equivalente
   - RAGAS para validación de chunks contra queries
   - Generación automática de "10-12 questions" por archivo: ¿LLM? ¿humano? ¿híbrido?
   - Costo por archivo procesado

4. **Validación que un chunk responde una query:**
   - Metric: ¿semantic similarity? ¿LLM judge? ¿humano?
   - Threshold real: cuándo decir "este chunk SÍ responde esta query"
   - Cómo se actualiza cuando el archivo se modifica

5. **Migration strategy:**
   - Lazy migration (cuando un archivo se edita, se re-chunkea) vs masiva (script batch)
   - Cómo no romper retrieval durante la migración (dual indexing?)
   - Tools para automatizar: ¿LlamaIndex transform? ¿Custom Python con LiteLLM?
   - Tiempo estimado para migrar 540 archivos .md

6. **Convención de naming + estructura interna:**
   - ¿Cómo se documenta en cada archivo "estas son las 10 questions que respondo"?
   - Schema YAML / Markdown frontmatter sugerido
   - Validación automática (CI check que cada archivo tiene questions definidas)

**Entregable D3:**
- Tabla de decisión chunking strategy por tipo de archivo (ENT_/PLB_/POL_/SKILL_/etc.)
- Convención canónica para `POL_CHUNKING_KB_v1` con frontmatter schema
- Tooling recomendado (Python scripts + libraries)
- Plan migración 540 archivos: lazy vs masivo, esfuerzo estimado, riesgos

---

### D4 — CLAUDE.md patterns emergentes 2026

**Problema:** mi CLAUDE.md raíz tiene 6 reglas inquebrantables pero le falta la capa "behavioral constraint system" tipo Karpathy/Mehul. Cowork muchas veces ejecuta cambios "de cortesía" (ej. incidente 29-abr: 11 archivos FB metidos en `docs/` raíz pese a indicaciones explícitas). Necesito CLAUDE.md v2 robusto.

**Investigá específicamente:**

1. **Más allá de Karpathy / Mehul Gupta:**
   - Anthropic CLAUDE.md interno (si está público)
   - Repos open-source con CLAUDE.md robustos: cuáles, qué patrones usan
   - Empresas con KB grandes (>1000 archivos) que documentan su CLAUDE.md
   - Diferencias entre CLAUDE.md para codebase vs KB vs research repo

2. **Anti-patterns documentados:**
   - CLAUDE.md que NO funciona en producción
   - Reglas que se ignoran consistentemente — ¿por qué?
   - Reglas que generan parálisis (ask-loops infinitos)
   - Reglas que se contradicen entre sí

3. **Integración con sub-agents (Skill_, Plan_, Explore, etc.):**
   - ¿CLAUDE.md aplica a sub-agents o solo al main agent?
   - ¿Cómo se propagan reglas a sub-agents?
   - ¿Cómo se manejan reglas que aplican solo a ciertos sub-agents?

4. **Mantenimiento con múltiples contributors:**
   - ¿Quién aprueba cambios al CLAUDE.md en repos con 10+ contributors?
   - Versionado semántico de reglas
   - Cómo se comunican cambios al equipo
   - Métricas de adopción real (¿se está siguiendo o no?)

5. **Métricas de éxito:**
   - ¿Cómo medís si CLAUDE.md funciona?
   - Diff size promedio (debería bajar con surgical changes)
   - Number of follow-up clarifications (debería bajar con think-before)
   - Number of "AI cleanup behavior" incidents (cambios no solicitados)
   - Tiempo de PR review (debería bajar con contracts claros)

6. **Plantillas para diferentes contextos:**
   - CLAUDE.md para KB pura (mi caso)
   - CLAUDE.md para codebase (Karpathy/Mehul)
   - CLAUDE.md para research repo
   - CLAUDE.md para multi-tenant SaaS

7. **Reglas específicas para repo KB con sync canónico:**
   - Mi caso: repo canónico C:\dev\mwt-knowledge-hub + mirror OneDrive vía mirror_to_onedrive.ps1
   - Cowork escribe en OneDrive, sync_*_indexa.ps1 mueve al canónico
   - Cómo CLAUDE.md previene escribir directo al canónico desde Cowork
   - Cómo previene perder cambios entre canónico y mirror

**Entregable D4:**
- 4-6 patrones canónicos para incorporar a MWT CLAUDE.md v2
- Plantilla de sección por patrón con ejemplos concretos
- Métricas de éxito a trackear post-implementación
- Anti-patterns a evitar explícitamente
- Caso especial: secciones para KB con sync canónico (no codebase)

---

## Restricciones comunes (todas las dimensiones)

1. **NO recomendar cosas que ya están canonizadas en mi repo:**
   - Single-agent en MVP (decisión cerrada)
   - Letta para memoria persistente
   - UUIDv7 client-side
   - Sealed/Open dual mode
   - Draft-first invariante (P3)
   - Curaduría 2 capas USER + COMMITTEE
   - 7 archetypes (`ENT_FB_AGENT_ARCHETYPES_v1`)
   - P16 sub-agents atomic principle
   - SPEC_FB_RAG_SECURITY_FIREWALL_v1 con sus 6 componentes
   - Stack técnico (FastAPI + Supabase + LiteLLM + Next.js + ARQ)

2. **NO marketing-talk:** "transformación digital", "AI-powered", "next-gen". Datos concretos o no decir nada.

3. **NO frameworks teóricos sin aterrizaje:** si propones Graph RAG, decime cuándo NO usarlo. Si propones DeepEval, decime el costo real.

4. **SÍ casos production reales 2025-2026:** empresas, métricas reportadas, gotchas. Si no hay caso real, decimos "no encontré caso production validado" — preferible a inventar.

5. **SÍ recomendaciones directas:** no listas neutrales A/B/C. Decí "yo recomiendo X porque Y, descarto Z porque W".

6. **SÍ contexto LATAM cuando aplique:** 95% de la documentación AI es US-centric. Si hay especificidades LATAM (DPA, costos, herramientas con presencia LATAM), levantarlas.

---

## Formato de respuesta esperado

Por cada dimensión D1/D2/D3/D4:

```markdown
## D[N] — [Título]

### Resumen ejecutivo (3-5 bullets)

### Hallazgos por sub-pregunta

[Por cada sub-pregunta del prompt: respuesta directa + evidencia + fuentes]

### Recomendación directa

[Lo que SÍ implementar, lo que NO, lo que diferir, con por qué]

### Casos production citados

[Empresa | Caso | Métrica reportada | Fuente]

### Gotchas y riesgos

[Cosas que el research reveló como problemáticas]

### Sources

[Markdown links a las referencias]
```

Al final del swarm completo:

```markdown
## Síntesis ejecutiva del swarm

### Decisiones que el roadmap MWT debe incorporar

[Tabla: dimensión | decisión | impacto en sprint X | bloquea Y]

### Tensiones cross-dimensión

[Si D1 sugiere X y D2 sugiere Y contradictorio, levantarlo]

### Roadmap ajustado post-swarm

[Si las recomendaciones cambian el orden propuesto, decirlo]

### Costos proyectados consolidados

[Suma de costos D1+D2+D3+D4 que afecten MVP]
```

---

## Criterios de éxito del swarm

El swarm es exitoso si:

1. Cada dimensión devuelve **al menos 3 casos production reales** con métricas
2. Cada dimensión termina con **recomendación directa**, no análisis abstracto
3. Las **tensiones cross-dimensión** se levantan explícitamente (no se evitan)
4. El **costo proyectado consolidado** es real, no estimado
5. La **síntesis ejecutiva** apunta a cambios concretos en mi roadmap

---

## Lo que NO necesito

- Definiciones genéricas de RAG, hybrid retrieval, chunking, CLAUDE.md (ya las conozco)
- Comparaciones con sistemas que no aplican (ej. enterprise RAG con $50K/mes infra)
- Recomendaciones de migrar de Supabase a algo más exótico (decisión cerrada)
- Sugerencias de multi-agent en MVP (decisión cerrada con MAST)
- Marketing-talk de vendors

---

## Plazo

Aspiro a recibir output completo en **24-48h** para integrar al roadmap antes de Sprint 0.

Gracias.

---

**Fin del prompt único swarm #6.**
