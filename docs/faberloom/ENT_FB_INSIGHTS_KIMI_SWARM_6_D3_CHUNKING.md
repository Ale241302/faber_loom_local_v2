# ENT_FB_INSIGHTS_KIMI_SWARM_6_D3_CHUNKING -- Chunking strategies "by user query"

---
id: ENT_FB_INSIGHTS_KIMI_SWARM_6_D3_CHUNKING
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: ENT
stamp: VIGENTE -- 2026-05-07
fecha: 2026-05-07
agente: Kimi K2.6 multi-agente D3 (research) + Cowork (sintesis indexada) + CEO (decisiones)
aplica_a: [FaberLoom, MWT]
relacionado_con:
  - SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md (memory_chunk schema)
  - POL_CHUNKING_KB_v1 (PENDIENTE crear)
  - ROADMAP_INTEGRAL_KB_4_CAPAS.md (capa 2 manejo datos)
  - SPEC_FB_RAG_SECURITY_FIREWALL_v1.md (firewall + chunking interactuan)
origen: |
  Kimi Swarm #6 D3 ejecutado 2026-05-07. 10+ casos production citados.
  Research bruto: docs/anexos/kimi_swarm_6/research/mwt_swarm6_d3.md (849 lineas).
  Disparado por gap: archivos KB organizados por documento (taxonomia
  tematica) NO por queries reales. TDS recomienda "chunk by user query,
  not document structure". Score capa 2 estimado 5.5/10.
---

## 1. Decision principal

**NO migracion masiva ahora.** Implementar **lazy migration con dual-index PostgreSQL** usando `CREATE INDEX CONCURRENTLY`. Comenzar con **recursive chunking + sentence window** para 430 documentos operativos.

Introducir **query-enriched metadata** (5-10 preguntas generadas via LLM por archivo) en frontmatter de cada archivo KB. Esto da **80% del beneficio de "chunk by query" sin reindexar todo**.

Costo: $0.50-1.60 para 540 archivos con GPT-4.1 Nano via LiteLLM.
Esfuerzo: 2-3 dias trabajo dev. Riesgo downtime cercano a cero con `REINDEX CONCURRENTLY`.

## 2. Hallazgos clave

### 2.1 Estado del arte chunking 2025-2026

7 estrategias dominantes con ganador claro por tipo de contenido:

| Estrategia | Cuando usar | Status produccion |
|---|---|---|
| **Recursive splitting** | Default seguro. 80% casos generales | Validado por 4 benchmarks independientes |
| **Sentence window** | Preserva contexto local | Default complementario a recursive |
| **Semantic chunking** | Contenido heterogeneo con presupuesto | **Riesgo:** sin min_chunk_size floor genera micro-fragments 43 tokens |
| **Hierarchical parent-child** | Documentos estructurados criticos (POL/PLB) | **Approach premium**. Caso 47billion: 61%->89% accuracy |
| **Late chunking** | Solo con jina-embeddings-v3 | NO compatible stack frozen FaberLoom |
| **Agentic chunking** | -- | "Highest computational overhead". Discontinuado experimentos 2025 |
| **Fixed-size** | -- | **Deprecated produccion B2B** |

### 2.2 Intent-Driven Dynamic Chunking (IDC)

Investigacion 2026 formaliza "chunk by user query" como **IDC**: indexar documentos por preguntas que responden, no solo por contenido bruto.

**Mejoras documentadas:**
- 5-67% en top-1 retrieval accuracy
- 40-60% reduccion numero de chunks

Es evolucion natural de "query-focused indexing" combinando generacion automatica preguntas + boundary optimization.

**Para MWT:** IDC es **research code febrero 2026**, no implementaciones estables Python aun. Esperar Q3 2026 para evaluar.

### 2.3 Casos B2B production reales

| Empresa | Caso | Metrica reportada |
|---|---|---|
| **Harvey AI** | Legal RAG Am Law 100 | Tool selection precision 0.8-0.9. **30% reduccion contract review time**. 2-3 hrs/semana ahorradas |
| **47billion** | University/consulting KB | Fixed-size 61% -> Hierarchical **89% accuracy**. Faithfulness 0.74 -> 0.91 |
| **Lucidworks** | B2B catalog search (HVAC, automotive) | Precision answers para spec queries tecnicos |
| **UI Chicago** | SAP Business One docs | Recursive+TF-IDF **82.5% precision** vs Semantic 73.3% |
| **Snowflake** | Finance RAG | ANLS correlation chunk-level -> generation-level |
| **TDS/Enterprise KB** | Confluence + runbooks | Context recall 0.72 -> 0.88 con sentence windows |
| **H-RAG (SemEval-2026)** | Multi-turn conversational RAG | nDCG@5=0.4271. Parent rescoring +0.0197 |
| **AI21** | Query-dependent chunking | Multi-scale RRF aggregation |
| **Vectara** (NAACL 2025) | Peer-reviewed | **Fixed 200-word > Semantic en realistic datasets** |
| **Chroma** (benchmark) | Chunking | Semantic 91.9% recall. Recursive 88% |

### 2.4 Tabla decision strategy por tipo archivo MWT

| Tipo canonico | Ejemplo | Estrategia | Chunk size | Overlap | Query enrichment |
|---|---|---|---|---|---|
| **POL** (politicas) | POL_CALIDAD_003 | hierarchical parent-child | child=256, parent=1024 | 50 tokens | Si, 5-10 queries |
| **PLB** (playbooks) | PLB_COBRA_002 | hierarchical parent-child | child=256, parent=1024 | 50 tokens | Si, 5-10 queries |
| **SKILL** (agentes) | SKILL_PROFORMA | hierarchical parent-child | child=512, parent=1500 | 50 tokens | Si, 10-12 queries |
| **ENT** (entities datos) | ENT_PROD_BIS | recursive + sentence window | 400-512 tokens | 10-15% | Si, 5-10 queries |
| **LOC** (localizacion) | LOC_BIS_ES | sentence window | 256 tokens | 10% | No (es data plana) |
| **SCH** (schemas) | SCH_LISTING | recursive | 400 tokens | 10% | Si, 5 queries |
| **AUDIT** (logs) | AUDIT_FB_A1 | recursive | 512 tokens | 10% | No |

## 3. Recomendacion directa

### Lo que SI implementar (ahora, MVP)

1. **Recursive chunking + sentence window como default** para 430 archivos operativos. Chunk size 400-512 tokens, overlap 10-15%. Mejor ratio costo/beneficio validado por 4 benchmarks independientes.

2. **Query-enriched frontmatter** en cada archivo KB. Campo `queries_answered` con 5-10 preguntas realistas via LLM (GPT-4.1 Nano via LiteLLM). Costo total: <$2 corpus completo. Beneficio: mejora retrieval precision al permitir query-to-question matching ademas de query-to-content.

3. **Hierarchical parent-child** para documentos POL (politicas) y PLB (playbooks) que son estructurados y criticos para compliance. Child=256 tokens (retrieval), parent=1024-1500 tokens (generation context).

4. **CI validation** del frontmatter schema en cada PR. Prevenir archivos sin `queries_answered` entren al repo.

5. **Lazy migration:** cada archivo editado post-lanzamiento se re-chunkea con nueva estrategia. No tocar archivos stale.

### Lo que NO implementar (ahora)

1. NO **semantic chunking sin min_chunk_size floor.** Riesgo micro-fragments (43 tokens promedio) que retrieven bien pero respondan mal es real y documentado.

2. NO **late chunking.** Requiere jina-embeddings-v3, no compatible stack frozen.

3. NO **migracion masiva 540 archivos.** Riesgo innecesario MVP. Lazy migration suficiente.

4. NO **agentic chunking.** "Highest computational overhead". Discontinuado experimentos 2025. Overkill para corpus 540 archivos.

5. NO **cambio vector database.** Stack frozen Supabase/pgvector. HNSW suficiente <1M vectors.

### Lo que diferir (post-MVP)

1. **Intent-Driven Dynamic Chunking (IDC).** Esperar implementaciones estables Python. Evaluar Q3 2026.
2. **Multi-scale indexing (AI21 approach).** Requiere 2-5x mas storage. Evaluar si corpus >5K archivos.
3. **Cross-encoder reranker.** Anadir si retrieval precision con bi-encoder <0.80.
4. **Embedding model upgrade.** Cuando haya drift medible. Drift-Adapter pattern para evitar reindexar todo.

## 4. Convencion canonica POL_CHUNKING_KB_v1 (frontmatter schema)

```yaml
---
id: "POL_CALIDAD_003"
domain: "mwt"
kb_type: "POL"
status: "active"
version: "2025-06-20-v1"
created_at: "2025-01-10"
updated_at: "2025-06-20"
reviewed_at: "2025-06-18"
reviewed_by: "committee_carlos"

chunk_strategy: "hierarchical_parent_child"
chunk_child_size_tokens: 256
chunk_parent_size_tokens: 1024
chunk_overlap_tokens: 50

queries_answered:
  - question: "Cual es el periodo de garantia para calzado de seguridad defectuoso?"
    query_type: "factoid"
    confidence: "high"
    expected_answer_span: "El periodo de garantia es de 90 dias calendario..."
  - question: "Que documentacion se requiere para iniciar reclamacion garantia?"
    query_type: "procedural"
    confidence: "high"
  - question: "La garantia cubre desgaste normal por uso industrial?"
    query_type: "edge_case"
    confidence: "high"
  - question: "Como se compara nuestra politica garantia con competidor Z?"
    query_type: "comparative"
    confidence: "medium"
    note: "Requiere datos de POL_COMPETENCIA_001"

tags: ["garantia", "calidad", "post-venta", "reclamacion"]
related_docs: ["PLB_COBRA_002", "ENT_CLIENTE_001"]
compliance_jurisdiction: ["CR", "CO", "MX", "PA", "BR"]
compliance_class: "product_safety"
source_authority: "legal_mwt_2025"
retrieval_priority: "high"
last_retrieval_test: "2025-06-19"
retrieval_score_avg: 0.91
---
```

## 5. Plan migracion 540 archivos

### Fase 0: Preparacion (Dia 1, 4h)

- Definir POL_CHUNKING_KB_v1 con schema frontmatter
- Generar template Python para `queries_answered` con LLM
- CI validation script (`scripts/validate_chunking_frontmatter.py`)

### Fase 1: Lazy Migration Setup (Dia 1-2, 6h)

- Dual-index PostgreSQL con `CREATE INDEX CONCURRENTLY`
- Tabla `chunks_v2` con nueva estrategia
- Tabla `chunks_v1` (legacy) sigue activa hasta migracion completa
- Hooks: cuando archivo editado, re-chunkea automatico

### Fase 2: Procesamiento Batch Controlado (Dia 2-3, 6h)

- Identificar archivos criticos (POL, PLB, SKILL): ~50 archivos
- Generar `queries_answered` via LLM batch
- Re-chunkear con nueva estrategia
- Validacion humana muestreo (10%)

### Fase 3: Lazy Continuo (Post-lanzamiento)

- Cada archivo editado en futuro -> re-chunkea automatico
- Backlog visible en dashboard admin
- Sin pressure por completar 540 archivos

### Esfuerzo total estimado

- 2-3 dias trabajo dev
- $0.50-$1.60 LLM cost (one-time)
- Riesgo downtime: cercano a cero

## 6. Gotchas y riesgos

1. **Embedding drift al cambiar chunking:** si cambias chunk boundaries, embeddings cambian. NO mezclar chunks de estrategias diferentes en mismo indice sin versionado explicito.

2. **CREATE INDEX CONCURRENTLY no funciona en transacciones:** si usas Prisma/ORM, marcar migracion como non-transactional.

3. **Vacuum bloat en pgvector:** deletes/updates dejan dead tuples. Monitorear con `pg_stat_all_tables`. Usar `VACUUM` o `REINDEX CONCURRENTLY`.

4. **"Lost in the middle" problem:** aun con context windows grandes, LLMs declinan accuracy si info relevante esta en medio. Hierarchical chunking mitiga al pasar parent context rico.

5. **Query distribution shift:** queries de usuarios reales son "messier than your test set". Monitorear retrieval scores produccion y ajustar thresholds trimestralmente.

6. **Costo semantic chunking a escala:** para 1M documentos, embedding cada sentence para chunking = miles de dolares API calls.

7. **Cascading failure RAG:** "If either retriever or generator performs poorly, overall quality drops to zero". Chunking es upstream de todo.

8. **LATAM context bonus:** GPT-4o tokenizer es **15-20% mas eficiente para no-Latin (incluye espanol)**. Costos por token espanol son menores.

## 7. Tooling recomendado

- **LlamaIndex `RecursiveCharacterTextSplitter`** para recursive base
- **LlamaIndex `SentenceWindowNodeParser`** para sentence window
- **Custom Python script** para hierarchical parent-child (controlar boundaries)
- **GPT-4.1 Nano via LiteLLM** para generar `queries_answered`
- **RAGAS via Langfuse** para validacion (NO DeepEval, ver D2)
- **`scripts/validate_chunking_frontmatter.py`** CI validation

## 8. Decisiones que cierran

- Recursive + sentence window default
- Hierarchical parent-child para POL/PLB criticos
- Query-enriched frontmatter obligatorio (5-10 queries via LLM)
- Lazy migration con dual-index, NO masiva
- Validacion chunks via RAGAS, NO DeepEval
- Late chunking diferido (incompatible stack)
- Agentic chunking descartado
- Fixed-size deprecated

## 9. Sources

Research bruto completo en: `docs/anexos/kimi_swarm_6/research/mwt_swarm6_d3.md` (849 lineas).

10+ casos production citados, 70+ referencias web verificadas.

---

**Fin del documento.**
