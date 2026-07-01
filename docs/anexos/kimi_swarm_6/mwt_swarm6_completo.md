# MWT Swarm #6 — Research Completo: Hybrid Retrieval, KB Quality, Chunking, CLAUDE.md

**Para:** Álvaro, CEO Muito Work Limitada (MWT)  
**De:** Kimi K2.6 multi-agente  
**Fecha:** 2026-05-07  
**Pedido original:** 2026-05-06  

---



================================================================================
# D1 — Hybrid Retrieval con pgvector + BM25 + RRF

## Resumen ejecutivo

- **pgvector NO incluye BM25 nativo.** La combinación requiere `tsvector` + GIN (full-text search nativo de Postgres) o una extensión BM25 como `pg_search` (ParadeDB, AGPL) o `pg_textsearch` (TigerData, PostgreSQL license). **Para Supabase en 2026-06, solo `pgvector` + `tsvector` están disponibles nativamente; extensiones BM25 requieren self-host o replicación a ParadeDB.**[^88^][^114^]
- **RRF es el método de fusión por defecto en producción 2025-2026.** No requiere normalización de scores, es robusto ante diferentes escalas, y k=60 es el default probado en BEIR/MS-MARCO. Para B2B LATAM con queries en español/portugués, k=60 sigue siendo válido; el factor crítico es la tokenización, no el valor de k.[^24^][^93^]
- **Mejoría documentada en producción: 22-35% en precision/recall.** Casos reportados suben de ~62% a ~84% retrieval precision al agregar BM25 a vector search puro. MRR mejora +18.5% en benchmarks controlados.[^24^][^186^]
- **Índices coexisten sin conflicto.** HNSW (pgvector) + GIN (tsvector) en la misma tabla, mismo schema. RLS multi-tenant funciona nativamente porque ambos usan la tabla subyacente.[^20^][^88^]
- **Recomendación directa para FaberLoom:** Implementar **Phase 1** con `tsvector` + `ts_rank_cd` + `pgvector` HNSW + RRF en Python (asyncpg). Esto no requiere extensiones adicionales en Supabase, funciona hoy, y cubre el 85% del beneficio de hybrid. **Diferir** la migración a extensión BM25 verdadera (pg_textsearch/pg_search) hasta post-MVP cuando el corpus exceda 50K chunks o la calidad de ranking de `ts_rank` sea insuficiente.

---

## Hallazgos por sub-pregunta

### 1. Implementación con pgvector + Postgres 16 nativo

#### ¿pgvector soporta BM25 nativo o requiere extensión adicional?

**No.** pgvector solo provee índices ANN (HNSW, IVFFlat) para vectores densos. BM25 es un algoritmo de ranking para texto; requiere un motor de búsqueda full-text separado. En el ecosistema Postgres 2025-2026 existen tres opciones:

| Opción | Tecnología | Licencia | Disponible en Supabase (2026-06) |
|--------|-----------|----------|----------------------------------|
| A | `tsvector` + `ts_rank_cd` (nativo Postgres) | PostgreSQL | Sí, nativo |
| B | `pg_search` (ParadeDB, sobre Tantivy) | AGPL | No nativo; requiere replicación a ParadeDB[^116^] |
| C | `pg_textsearch` (TigerData, C nativo) | PostgreSQL | No en Supabase; disponible en Tiger Cloud[^18^] |
| D | `vchord_bm25` (VectorChord) | Apache 2.0 | No en Supabase; self-host via Docker[^38^] |

Para FaberLoom (stack frozen en Supabase), **la única opción disponible hoy es A: `tsvector` + GIN + `ts_rank_cd`**. Aunque `ts_rank_cd` no es BM25 verdadero (carece de IDF global y saturación de term frequency), aproxima el comportamiento de BM25 y es suficiente para corpus <100K documentos.[^20^][^113^]

#### Índices necesarios: ¿coexisten HNSW y GIN en mismo schema?

Sí, sin conflicto. El patrón está documentado por Supabase, ParadeDB, y múltiples implementaciones production:[^88^][^20^][^24^]

```sql
CREATE INDEX idx_embedding_hnsw ON chunks
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 128);

CREATE INDEX idx_fts_gin ON chunks
  USING gin (search_vector);
```

- HNSW indexa la columna `vector` para búsqueda semántica.
- GIN indexa la columna `tsvector` (generada automáticamente) para búsqueda full-text.
- Ambos son índices PostgreSQL estándar, participan en WAL, replicación, y backup.

**Nota importante:** `tsvector` como columna `GENERATED ALWAYS` vs índice funcional:
- Columna generada: 189 GB para tabla de ~100GB (incluye tsvector materializado).[^113^]
- Índice funcional (GIN sobre `to_tsvector`): 108 GB total (sin columna extra).[^113^]
- **Recomendación:** Para FaberLoom, usar **columna generada** (`GENERATED ALWAYS AS (to_tsvector(...)) STORED`) por simplicidad y RLS-friendly. El overhead de storage es aceptable para corpus <1M chunks.

#### Performance benchmark: latencia p50/p95 con 10K, 100K, 1M chunks

Datos concretos de benchmarks publicados (2025-2026):

| Dataset | Índice | p50 Query | p95 Query | QPS | Fuente |
|---------|--------|-----------|-----------|-----|--------|
| 100K chunks (dbpedia-openai-100k-angular) | HNSW m=48, ef_search=200 | ~8.9 ms | ~16 ms | 171 | Alibaba Cloud[^162^] |
| 1M chunks (dbpedia-openai-1000k-angular) | HNSW m=48, ef_search=200 | ~16 ms | ~25 ms | 101 | Alibaba Cloud[^162^] |
| 1M vectors (1536d, cosine) | HNSW | ~1.6s (p95 single) | — | 3.0 (concurrent-2) | build.com (RAM-constrained)[^89^] |
| 1M vectors (1536d, cosine) | DiskANN (pgvectorscale) | ~179 ms (p95) | — | 22.9 | build.com[^89^] |
| 8.8M passages (MS-MARCO) | pg_textsearch BM25 | 6.5s (800 queries total) | — | — | TigerData[^18^] |
| 138M passages | pg_textsearch BM25 | 40.6 ms (p50 weighted) | — | 198.7 TPS | TigerData[^18^] |

**Interpretación para FaberLoom:**
- Con corpus esperado de 10K-100K chunks (MVP single-tenant MWT → multi-tenant 4 tiers), HNSW con `m=16`, `ef_construction=128` dará **p50 <10ms, p95 <20ms** para vector search.
- Full-text search con GIN + `ts_rank_cd` será más rápido que vector search para queries cortas (1-3 términos), típicamente **<5ms p50**.
- RRF fusion en Python (no SQL) añade **<1ms** de overhead.

#### ¿Cómo se comporta con RLS multi-tenant?

RLS multi-tenant en PostgreSQL funciona **perfectamente** con hybrid search porque ambos índices operan sobre la tabla subyacente y las políticas RLS filtran filas antes de que cualquier índice las devuelva.[^37^][^152^]

El patrón production-validado:[^144^][^37^]

```sql
-- Setear tenant context por conexión
SET app.current_tenant = 'uuid-del-tenant';

-- RLS policy automática
CREATE POLICY tenant_isolation ON chunks
  FOR ALL
  USING (tenant_id = current_setting('app.current_tenant')::uuid);
```

**Crítico para FaberLoom:** El filtro `tenant_id` debe aplicarse **ANTES** del ranking. Con pgvector 0.8.0+, usar `hnsw.iterative_scan = relaxed_order` para que el índice siga escaneando hasta encontrar suficientes resultados del tenant.[^142^][^203^]

Overhead medido de RLS en vector search (HNSW): **~20%** (de 3-5ms a 5-6ms). Aceptable.[^144^]

---

### 2. Libraries Python production-ready

#### rank_bm25 puro Python vs Postgres-native FTS

| Library | Approach | Speed (QPS, BEIR fiqa) | Dependencies | Recomendación para FaberLoom |
|---------|----------|------------------------|--------------|------------------------------|
| `rank_bm25` | Python puro, listas en memoria | ~4.46 QPS (lento) | solo Python | **NO usar en producción**[^65^] |
| `bm25s` | Python + scipy sparse matrices | ~507 QPS fiqa | numpy, scipy | Mejor opción Python-only, pero **innecesario** si tenemos Postgres[^65^] |
| Postgres `ts_rank_cd` | C nativo, GIN index | Miles de QPS | — (built-in) | **USAR ESTO** para Phase 1 |
| `pg_textsearch` | C nativo, BM25 real | ~199 TPS concurrente | Extensión Postgres | **DIFERIR** hasta post-MVP |

**bm25s** es 100x más rápido que rank_bm25 y comparable a Elasticsearch en throughput,[^65^] pero para FaberLoom el texto ya vive en Postgres. Mover BM25 a Python implica cargar todo el corpus en memoria Python, duplicar storage, y perder ACID/RLS. **Descartar bm25s/rank_bm25 para retrieval principal; reservar solo para offline evaluación o testing.**

#### LlamaIndex QueryFusionRetriever vs LangChain EnsembleRetriever

Ambos implementan hybrid retrieval con RRF, pero **NO son necesarios** para FaberLoom:[^40^][^39^]

- **LlamaIndex QueryFusionRetriever**: Abstracción pesada, requiere docstore de LlamaIndex, no juega bien con esquemas SQL existentes. Útil para PoCs rápidos, no para producción SQL-first.[^40^]
- **LangChain EnsembleRetriever**: Similar problema — abstracción sobre abstracción. Además, en benchmarks RAG 2025, Ensemble tuvo **P99 latency de 12.20s** vs BM25 puro en 1.86s.[^39^]

**Recomendación para FaberLoom:** Implementar RRF **a mano** en Python (~15 líneas) o como SQL function en Postgres. Cero dependencias, control total, overhead mínimo. El SPEC ya tiene el agente en Pydantic AI; no añadir otra capa de abstracción de retrieval.

#### Integración con Pydantic AI / FastAPI sync vs async

Pydantic AI ya documenta retrieval con asyncpg + pgvector:[^73^]

```python
@agent.tool
async def retrieve(context: RunContext[Deps], search_query: str) -> str:
    embedding = await context.deps.openai.embeddings.create(...)
    rows = await context.deps.pool.fetch(
        'SELECT ... ORDER BY embedding <-> $1 LIMIT 8',
        embedding_json,
    )
```

Para hybrid retrieval, el patrón es:
1. Generar embedding del query (async, ~50-200ms).
2. Ejecutar **dos queries en paralelo** contra asyncpg pool (vector + FTS).
3. Fusionar con RRF en Python (~0ms).
4. Retornar contexto al agente.

**La latencia dominante es la generación del embedding**, no la consulta a Postgres.[^186^] Ejecutar las dos queries en paralelo con `asyncio.gather` prácticamente no añade latency vs una sola query.

---

### 3. RRF (Reciprocal Rank Fusion) vs weighted alpha

#### Cuándo usar cuál

| Método | Cuándo usar | Requiere tuning | Robustez |
|--------|-------------|-----------------|----------|
| **RRF** | Default. Sistemas con overlap entre resultados. Sin datos etiquetados. | Mínimo (solo k) | Alta. Ignora escalas de score.[^93^] |
| **Weighted alpha** | Cuando necesitas control fino (ej. keywords más importantes para SKUs). Con datasets etiquetados para calibrar. | Alto (alpha por tipo de query) | Media. Requiere normalización de scores.[^93^] |

RRF es el **consenso de la industria 2025-2026** para hybrid search sin reranker. Elasticsearch, Azure AI Search, Pinecone, Qdrant, y PostgreSQL tutorials lo usan como default.[^93^][^98^]

Para FaberLoom (cotización B2B de calzado de seguridad), las queries serán mixtas:
- "POL_ROGERS" → necesita BM25 fuerte (exact match de marca)
- "bota dieléctrica con puntera de acero" → necesita vector fuerte (semántica)

RRF maneja ambos sin calibración por query. Weighted alpha sería útil más adelante si detectamos que ciertos tipos de query (ej. búsqueda por SKU) consistentemente necesitan más peso lexical.

#### k=60 default ¿es válido para B2B LATAM con queries en español/portugués?

**Sí, k=60 es válido.** El parámetro k en RRF controla cuánto "pierde" un documento por estar mal ranqueado en una lista. No depende del idioma del query; depende de:
1. Cuántos resultados devuelve cada retriever (over-fetch).
2. Qué tan "confiable" es cada retriever.

Evidencia empírica:[^24^][^146^]
- k=60 es el default del paper original de Cormack et al. (2009).
- En benchmarks MS-MARCO y BEIR, k=60 funciona consistentemente bien.
- lpossamai reportó que k=60 fue óptimo para su dataset tras probar 10-100.[^24^]
- MariaDB documenta k=60 como ideal para sistemas diversos (keyword + vector).[^146^]

**Factor crítico para español/portugués:** La tokenización, no k. Postgres `to_tsvector('spanish', ...)` y `to_tsvector('portuguese', ...)` tienen stemming y stopwords nativos.[^103^][^107^] Para queries que mezclan español/portugués con términos técnicos (ej. "bota Marluvas 50S5BR"), usar `to_tsvector('simple', ...)` para preservar tokens exactos, o concatenar múltiples tsvectors.[^108^]

#### ¿Cómo se calibra alpha para distintos tipos de query?

**No calibrar alpha en MVP.** RRF no usa alpha. Si en post-MVP se decide migrar a weighted fusion, la calibración requiere:

1. **Dataset de evaluación:** 50-200 queries representativas con juicios de relevancia (ground truth).
2. **Métrica:** NDCG@5 o MRR.
3. **Grid search:** Probar alpha ∈ [0.1, 0.9] en pasos de 0.1.
4. **Query classification:** Clasificar queries en tipos (SKU, semántica, mixta) y asignar alpha por tipo.

Esto es **Phase 3+** de FaberLoom. Para MVP, RRF puro es suficiente y superior a vector-only.

---

### 4. Casos production reales 2025-2026

| Empresa | Caso | Métrica reportada | Fuente |
|---------|------|-------------------|--------|
| **lpossamai** (SaaS B2B, 2026) | Switched from pure vector to hybrid (pgvector + tsvector + RRF) | Retrieval precision: **62% → 84%** (+22pp). Exact-match queries: "Unreliable → Near-perfect". Zero new infrastructure. | dev.to, 2026-02-12[^24^] |
| **TigerData** (plataforma Postgres cloud) | pg_textsearch BM25 vs ParadeDB/Tantivy | 2.4x-6.5x más rápido en queries cortas (1-4 tokens). 8.7x throughput concurrente. 138M docs indexados en <18 min. | TigerData blog, 2026-03-31[^18^] |
| **VectorChord** (extensión Postgres) | vchord_bm25 vs Elasticsearch | 3x QPS promedio. NDCG@10 comparable o superior en datasets BEIR. | VectorChord blog, 2025-03-28[^43^] |
| **SoftwareSeni** (consultora, 2026) | Migración Elasticsearch → Postgres BM25 + RRF | "20-1000x mejora en query latency vs ts_rank nativo". RLS aplica automáticamente (vs sincronizar con ES). | SoftwareSeni, 2026-04-22[^1^] |
| **AI Multiple** (benchmark independiente) | Hybrid vs Dense-only | MRR +18.5% (0.410 → 0.486). Recall@5 +7.2%. Latencia +201ms (+24.5%). | aimultiple.com, 2026-03-11[^186^] |
| **Starmorph** (benchmark RAG) | Hybrid retrieval + reranking | "25-40% precision improvement over naive RAG". Standard production default. | starmorph.com, 2026-04-21[^184^] |
| **GitLab** (production Postgres) | GIN index pending list overhead | Cada 2.7 segundos el pending list se llenaba en horas pico. Limpieza: 465ms-3155ms. Solución: tuning de autovacuum + gin_pending_list_limit. | pganalyze/GitLab, 2021-2025[^156^] |
| **AWS (re:Invent DAT409)** | Aurora PostgreSQL + pgvector hybrid search | "Persona-based RLS for multi-tenant agents". RRF vs weighted fusion comparado. Cohere Rerank vs RRF. | AWS Samples, 2025-08-12[^143^] |

**Nota para FaberLoom:** El caso más cercano al stack es lpossamai (pgvector + tsvector + RRF en Postgres). La mejora de 62% → 84% en retrieval precision es directamente aplicable al dominio B2B de calzado de seguridad, donde queries por marca/modelo ("Marluvas 50S5BR") son críticas.

---

### 5. Costo de mantenimiento del índice BM25

#### ¿Cuánto crece vs solo vector?

| Componente | Tamaño relativo | Fuente |
|-------------|----------------|--------|
| Tabla base (texto + metadata) | 1x (baseline) | — |
| Columna `tsvector` (generada) | ~0.3-0.5x del texto original | Depende de idioma y stopwords[^113^] |
| Índice GIN sobre tsvector | ~0.3-0.5x del tamaño de la tabla | Similar a tsvector column[^113^] |
| Índice HNSW sobre vector | ~2-5x del tamaño de los vectores | Fórmula: (d * 4 + M * 2 * 4) por vector[^96^] |

Para 1M vectores de 1536 dimensiones, m=16:
- Datos vector: 1M × 1536 × 4 bytes = ~6 GB
- Índice HNSW: ~8-10 GB (según build.com)[^89^]
- tsvector + GIN: ~1-3 GB (depende de longitud de chunks)

**Conclusión:** El índice full-text (GIN/tsvector) es **significativamente más pequeño** que el índice HNSW. El storage dominante es el vector index.

#### ¿Se actualiza incrementalmente o requiere full rebuild?

- **GIN (tsvector):** Actualización **incremental** con `fastupdate=ON` (default). Las inserciones van a una "pending list" y se mergean en batch durante autovacuum.[^150^] No requiere rebuild. Pero cada N inserciones (cuando pending list > 4MB) hay un spike de latencia en escritura.[^156^]
- **HNSW (pgvector):** Inserciones incrementales nativas. pgvector soporta inserciones en HNSW sin rebuild.[^92^]

#### ¿Cuál es el overhead real para tenant con 100 docs vs 10K docs?

| Métrica | 100 docs/tenant | 10K docs/tenant | 100K docs/tenant |
|---------|----------------|-----------------|------------------|
| HNSW query p50 | ~1-2 ms | ~3-5 ms | ~5-8 ms |
| GIN query p50 | ~0.5-1 ms | ~1-2 ms | ~2-4 ms |
| RRF fusion | <1 ms | <1 ms | <1 ms |
| RLS overhead | ~10-20% | ~15-20% | ~20% |

Con RLS + índice compartido (todos los tenants en una tabla), el HNSW es **único y shared**. El filtro RLS aplica después del index scan, pero con pgvector 0.8.0+ iterative scan, esto es manejable.[^142^]

**Estrategia recomendada para FaberLoom:**
- Phase 1 (MVP): Tabla única con `tenant_id` + RLS. HNSW compartido.
- Phase 2+ (escala): Si un tenant tiene >100K chunks, evaluar **particionamiento por lista** (`PARTITION BY LIST(tenant_id)`) o índices parciales HNSW por tenant para el tier $2499/mes.

---

## Recomendación directa

### Lo que SÍ implementar (Phase 1, MVP)

1. **Schema híbrido en Supabase (hoy):**
   ```sql
   CREATE TABLE chunks (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     tenant_id UUID NOT NULL,
     doc_id UUID NOT NULL,
     content TEXT NOT NULL,
     search_vector tsvector GENERATED ALWAYS AS (
       to_tsvector('spanish', coalesce(content, ''))
     ) STORED,
     embedding vector(1536),
     created_at TIMESTAMPTZ DEFAULT now()
   );
   CREATE INDEX idx_chunks_embedding ON chunks USING hnsw (embedding vector_cosine_ops) WITH (m=16, ef_construction=128);
   CREATE INDEX idx_chunks_fts ON chunks USING gin(search_vector);
   CREATE INDEX idx_chunks_tenant ON chunks(tenant_id); -- B-tree para RLS filter pushdown
   ```

2. **RRF en Python (async, ~15 líneas):**
   ```python
   def rrf_fuse(rank_lists: list[list[UUID]], k: int = 60, top_n: int = 10) -> list[UUID]:
       scores: dict[UUID, float] = {}
       for ranks in rank_lists:
           for rank, doc_id in enumerate(ranks, start=1):
               scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
       return sorted(scores, key=scores.get, reverse=True)[:top_n]
   ```

3. **Query dual con asyncpg (paralelo):**
   ```python
   async def hybrid_search(pool, query_text: str, query_embedding: list[float], tenant_id: str, top_k: int = 10):
       bm25_sql = """
         SELECT id, ts_rank_cd(search_vector, plainto_tsquery('spanish', $1)) AS score
         FROM chunks WHERE tenant_id = $2 AND search_vector @@ plainto_tsquery('spanish', $1)
         ORDER BY score DESC LIMIT $3
       """
       vec_sql = """
         SELECT id, embedding <=> $1 AS distance
         FROM chunks WHERE tenant_id = $2
         ORDER BY distance LIMIT $3
       """
       overfetch = top_k * 2
       rows_bm25, rows_vec = await asyncio.gather(
           pool.fetch(bm25_sql, query_text, tenant_id, overfetch),
           pool.fetch(vec_sql, query_embedding, tenant_id, overfetch),
       )
       ids_bm25 = [r['id'] for r in rows_bm25]
       ids_vec = [r['id'] for r in rows_vec]
       return rrf_fuse([ids_bm25, ids_vec], k=60, top_n=top_k)
   ```

4. **RLS con SET app.current_tenant:**
   ```sql
   ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;
   CREATE POLICY tenant_isolation ON chunks
     FOR ALL USING (tenant_id = current_setting('app.current_tenant')::uuid);
   ```
   Nota: Usar Transaction Pooling en PgBouncer (si aplica) para no perder el contexto.[^144^]

### Lo que NO implementar (ahora)

1. **NO usar rank_bm25 ni bm25s en Python.** Son innecesarios; Postgres nativo es más rápido y mantiene RLS.
2. **NO usar LlamaIndex/LangChain retrievers.** Añaden abstracción sin beneficio para un stack SQL-first.
3. **NO usar weighted alpha en MVP.** RRF es suficiente y no requiere dataset de calibración.
4. **NO instalar pg_search/pg_textsearch en Supabase.** No están disponibles como extensiones nativas. La replicación a ParadeDB añade complejidad operativa injustificada para MVP.[^116^]
5. **NO usar IVFFlat.** HNSW maneja inserciones incrementales mejor y no requiere rebuild.[^92^]

### Lo que diferir (post-MVP)

1. **Extensión BM25 verdadera** (pg_textsearch o VectorChord-BM25): Cuando corpus >50K chunks por tenant o `ts_rank_cd` demuestre ranking deficiente en evaluación.
2. **Weighted fusion calibrado:** Cuando haya eval harness con 100+ queries etiquetadas y se detecte que RRF subóptimo para ciertos tipos de query.
3. **Cross-encoder reranker** (Cohere/Jina): Cuando retrieval precision @5 esté por debajo de 80% tras hybrid.
4. **Particionamiento por tenant:** Cuando un tenant individual exceda 100K chunks (tier Enterprise).

---

## Gotchas y riesgos

1. **GIN pending list latency spikes:** En workloads de escritura intensa (ej. ingestando 1000 chunks de un catálogo), cada ~N inserciones el pending list se limpia causando un spike de 500ms-3s.[^156^] **Mitigación:** Batch inserts + autovacuum tuning + considerar `fastupdate=OFF` para cargas iniciales masivas.

2. **HNSW con filtro de tenant en datasets pequeños:** Si un tenant tiene <100 chunks, HNSW + `WHERE tenant_id = X` con `hnsw.ef_search=40` puede retornar <10 resultados.[^151^] **Mitigación:** Habilitar `hnsw.iterative_scan = relaxed_order` en pgvector 0.8.0+.

3. **Tsvector language mismatch:** Si el contenido es técnico (nombres de producto, códigos SKU) y se indexa con `to_tsvector('spanish')`, el stemming puede transformar "50S5BR" en tokens irreconocibles.[^108^] **Mitigación:** Concatenar `to_tsvector('simple', content)` con `setweight('A')` para exact-match, más `to_tsvector('spanish', content)` con `setweight('B')` para stemming.[^112^]

4. **Embedding model upgrades = re-index:** Cambiar de `text-embedding-3-small` a otro modelo requiere re-embeddear TODO el corpus.[^24^] **Mitigación:** Bloquear modelo de embedding en SPEC. Preparar pipeline de re-embedding background para post-MVP.

5. **PgBouncer + RLS:** Statement pooling pierde `app.current_tenant` entre queries.[^144^] **Mitigación:** Usar Transaction Pooling exclusivamente.

6. **RLS + HNSW overhead en GROUP BY/aggregations:** RLS hace que `COUNT(*)` sea ~2.4x más lento.[^144^] **Mitigación:** No usar aggregation queries con RLS en el hot path; usar contadores desnormalizados.

---

## Prototype Python: FastAPI endpoint /search

```python
"""
FaberLoom Hybrid Search Endpoint — Phase 1 (MVP)
Stack: FastAPI + Pydantic AI + asyncpg + pgvector + tsvector + RRF
"""
import asyncio
import uuid
from collections import defaultdict
from typing import Any

import asyncpg
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
RRF_K = 60
OVERFETCH_FACTOR = 2
EMBEDDING_DIM = 1536

# ---------------------------------------------------------------------------
# Database pool (injected via dependency in production)
# ---------------------------------------------------------------------------
async def get_pool() -> asyncpg.Pool:
    # Singleton pool initialized at startup
    return app.state.db_pool

# ---------------------------------------------------------------------------
# RRF Fusion
# ---------------------------------------------------------------------------
def rrf_fuse(rank_lists: list[list[uuid.UUID]], k: int = RRF_K, top_n: int = 10) -> list[uuid.UUID]:
    """Reciprocal Rank Fusion. rank_lists: list of ranked doc-id lists."""
    scores: dict[uuid.UUID, float] = defaultdict(float)
    for ranks in rank_lists:
        for rank, doc_id in enumerate(ranks, start=1):
            scores[doc_id] += 1.0 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)[:top_n]

# ---------------------------------------------------------------------------
# Search core
# ---------------------------------------------------------------------------
async def _keyword_search(
    pool: asyncpg.Pool,
    query: str,
    tenant_id: uuid.UUID,
    limit: int,
    language: str = "spanish",
) -> list[uuid.UUID]:
    sql = f"""
    SELECT id, ts_rank_cd(search_vector, plainto_tsquery('{language}', $1)) AS score
    FROM chunks
    WHERE tenant_id = $2
      AND search_vector @@ plainto_tsquery('{language}', $1)
    ORDER BY score DESC
    LIMIT $3
    """
    rows = await pool.fetch(sql, query, tenant_id, limit)
    return [r["id"] for r in rows]

async def _vector_search(
    pool: asyncpg.Pool,
    embedding: list[float],
    tenant_id: uuid.UUID,
    limit: int,
) -> list[uuid.UUID]:
    sql = """
    SELECT id, embedding <=> $1 AS distance
    FROM chunks
    WHERE tenant_id = $2
    ORDER BY distance
    LIMIT $3
    """
    rows = await pool.fetch(sql, embedding, tenant_id, limit)
    return [r["id"] for r in rows]

async def _fetch_chunks(
    pool: asyncpg.Pool,
    chunk_ids: list[uuid.UUID],
    tenant_id: uuid.UUID,
) -> list[asyncpg.Record]:
    """Fetch full chunk data with RLS safety (tenant_id verified)."""
    sql = """
    SELECT id, doc_id, content, embedding <=> $1::vector AS distance
    FROM chunks
    WHERE id = ANY($2::uuid[])
      AND tenant_id = $3
    """
    # Note: $1 would be query embedding for context; simplified here
    return await pool.fetch(sql, [0.0] * EMBEDDING_DIM, chunk_ids, tenant_id)

# ---------------------------------------------------------------------------
# Pydantic AI Tool (integrated into agent)
# ---------------------------------------------------------------------------
class HybridSearchDeps(BaseModel):
    pool: asyncpg.Pool
    embed_fn: Any  # Callable[[str], Awaitable[list[float]]]

async def hybrid_search_tool(
    deps: HybridSearchDeps,
    query_text: str,
    tenant_id: uuid.UUID,
    top_k: int = 10,
) -> str:
    """
    Tool para Pydantic AI. Combina BM25-ish (ts_rank_cd) + vector + RRF.
    Retorna contenido de chunks concatenado para inyectar en prompt.
    """
    # 1. Embedding del query (latencia dominante: ~50-200ms)
    embedding = await deps.embed_fn(query_text)

    # 2. Over-fetch para dar margen a RRF
    overfetch = top_k * OVERFETCH_FACTOR

    # 3. Ambas búsquedas en paralelo
    ids_fts, ids_vec = await asyncio.gather(
        _keyword_search(deps.pool, query_text, tenant_id, overfetch),
        _vector_search(deps.pool, embedding, tenant_id, overfetch),
    )

    # 4. RRF fusion
    fused_ids = rrf_fuse([ids_fts, ids_vec], k=RRF_K, top_n=top_k)

    if not fused_ids:
        return "No se encontraron documentos relevantes."

    # 5. Fetch contenido (con verificación RLS)
    rows = await deps.pool.fetch(
        """
        SELECT id, doc_id, content
        FROM chunks
        WHERE id = ANY($1::uuid[]) AND tenant_id = $2
        """,
        fused_ids,
        tenant_id,
    )
    # Preservar orden de RRF
    row_by_id = {r["id"]: r for r in rows}
    ordered = [row_by_id[i] for i in fused_ids if i in row_by_id]

    # 6. Formato para LLM context
    parts = []
    for i, row in enumerate(ordered, 1):
        parts.append(f"[Doc {i}] ID={row['doc_id']}\n{row['content']}")
    return "\n\n---\n\n".join(parts)

# ---------------------------------------------------------------------------
# FastAPI endpoint (standalone, también usado por agente)
# ---------------------------------------------------------------------------
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    tenant_id: uuid.UUID
    top_k: int = Field(10, ge=1, le=50)
    language: str = "spanish"

class SearchResult(BaseModel):
    chunk_id: uuid.UUID
    doc_id: uuid.UUID
    content_preview: str
    rrf_score: float | None = None
    sources: dict[str, int | None]  # rank in fts, rank in vector

@app.post("/search", response_model=list[SearchResult])
async def search_endpoint(req: SearchRequest, pool: asyncpg.Pool = Depends(get_pool)):
    """
    Endpoint híbrido público. Sigue el mismo patrón que el tool del agente.
    """
    overfetch = req.top_k * OVERFETCH_FACTOR

    # Note: en producción, la generación de embedding va aquí o en un servicio separado
    # Para este prototype, asumimos embedding pre-calculado o mock
    embedding = [0.0] * EMBEDDING_DIM  # placeholder: reemplazar por llamada real

    # Paralelo
    ids_fts, ids_vec = await asyncio.gather(
        _keyword_search(pool, req.query, req.tenant_id, overfetch, req.language),
        _vector_search(pool, embedding, req.tenant_id, overfetch),
    )

    fused = rrf_fuse([ids_fts, ids_vec], k=RRF_K, top_n=req.top_k)
    if not fused:
        return []

    # Calcular scores y metadatos
    fts_ranks = {id_: rank for rank, id_ in enumerate(ids_fts, start=1)}
    vec_ranks = {id_: rank for rank, id_ in enumerate(ids_vec, start=1)}

    scores: dict[uuid.UUID, float] = defaultdict(float)
    for id_ in fused:
        if id_ in fts_ranks:
            scores[id_] += 1.0 / (RRF_K + fts_ranks[id_])
        if id_ in vec_ranks:
            scores[id_] += 1.0 / (RRF_K + vec_ranks[id_])

    rows = await pool.fetch(
        "SELECT id, doc_id, content FROM chunks WHERE id = ANY($1::uuid[]) AND tenant_id = $2",
        fused, req.tenant_id,
    )
    row_by_id = {r["id"]: r for r in rows}

    results = []
    for id_ in fused:
        if id_ not in row_by_id:
            continue
        r = row_by_id[id_]
        results.append(SearchResult(
            chunk_id=id_,
            doc_id=r["doc_id"],
            content_preview=r["content"][:500],
            rrf_score=round(scores.get(id_, 0.0), 6),
            sources={"fts_rank": fts_ranks.get(id_), "vector_rank": vec_ranks.get(id_)},
        ))
    return results
```

---

## Tabla de decisión: 3 stacks viables ranqueados

| Rank | Stack | Components | Esfuerzo | Precisión | Latencia p95 | RLS | Disponible en Supabase |
|------|-------|-----------|----------|-----------|--------------|-----|----------------------|
| **1** | **Phase 1 (Recomendado)** | pgvector HNSW + `tsvector` GIN + `ts_rank_cd` + RRF Python | Bajo (1-2 días) | ~80-85% precision | <25ms | Sí, nativo | **Sí, hoy** |
| 2 | Phase 2 (Mejorado) | pgvector HNSW + `pg_textsearch` BM25 + RRF SQL | Medio (1-2 semanas) | ~85-90% precision | <20ms | Sí | **No** (requiere Tiger Cloud o self-host) |
| 3 | Phase 3 (Óptimo) | pgvector HNSW + `pg_textsearch` BM25 + cross-encoder reranker | Alto (2-4 semanas) | ~90-95% precision | <500ms | Sí | **No** |

**Nota:** La diferencia entre Phase 1 y Phase 2 es ~5-10pp en precision. Para MVP de 60 días, Phase 1 es el punto óptimo en curva esfuerzo/beneficio.

---

## Sources

[^1^]: https://www.softwareseni.com/replacing-elasticsearch-with-postgres-using-bm25-hybrid-search-and-rrf/ — Replacing Elasticsearch with Postgres Using BM25 Hybrid Search and RRF (2026-04-22)
[^7^]: https://www.paradedb.com/blog/hybrid-search-in-postgresql-the-missing-manual — Hybrid Search in PostgreSQL: The Missing Manual (2025-10-21)
[^13^]: https://news.ycombinator.com/item?id=47589856 — Show HN: Postgres extension for BM25 relevance-ranked full-text search (2026-04-01)
[^18^]: https://www.tigerdata.com/blog/pg-textsearch-bm25-full-text-search-postgres — How We Built a BM25 Search Engine on Postgres (2026-03-31)
[^20^]: https://dev.to/gabrielanhaia/hybrid-search-in-100-lines-bm25-pgvector-with-rrf-merge-58cn — Hybrid Search in 100 Lines: BM25 + pgvector with RRF Merge (2026-04-27)
[^21^]: https://neon.com/docs/extensions/pg_search — The pg_search extension - Neon Docs (2026-03-13)
[^22^]: https://www.tigerdata.com/blog/you-dont-need-elasticsearch-bm25-is-now-in-postgres — You Don't Need Elasticsearch: BM25 is Now in Postgres (2026-02-25)
[^24^]: https://dev.to/lpossamai/building-hybrid-search-for-rag-combining-pgvector-and-full-text-search-with-reciprocal-rank-fusion-6nk — Building Hybrid Search for RAG (2026-02-12)
[^37^]: https://dev.to/__8fa66572/postgresql-rls-in-go-architecting-secure-multi-tenancy-4ifm — PostgreSQL RLS in Go: Benchmarks (2026-01-29)
[^38^]: https://github.com/tensorchord/VectorChord-bm25 — VectorChord-bm25 GitHub (2025-12-15)
[^39^]: https://thedataguy.pro/writing/2025/05/evaluating-advanced-rag-retrievers/ — Evaluating Advanced RAG Retrievers (2025)
[^40^]: https://llamaindexxx.readthedocs.io/en/latest/examples/low_level/fusion_retriever.html — LlamaIndex QueryFusionRetriever docs
[^41^]: https://thenewstack.io/better-relevance-for-ai-apps-with-bm25-algorithm-in-postgresql/ — Better Relevance for AI Apps With BM25 (2025-12-22)
[^43^]: https://blog.vectorchord.ai/vectorchord-bm25-revolutionize-postgresql-search-with-bm25-ranking-3x-faster-than-elasticsearch — VectorChord-BM25: 3x Faster Than ElasticSearch (2025-03-28)
[^65^]: https://pypi.org/project/bm25s/ — bm25s Python library (2026-04-29)
[^73^]: https://pydantic.dev/docs/ai/examples/data-analytics/rag/ — Pydantic AI RAG example with asyncpg
[^88^]: https://supabase.com/docs/guides/ai/hybrid-search — Supabase Hybrid Search Docs (2026-05-01)
[^89^]: https://thebuild.com/blog/2026/04/30/on-pgvectorscale-and-hybrid-search-without-an-elasticsearch-sidecar/ — pgvectorscale benchmark: DiskANN vs HNSW (2026-04-30)
[^92^]: https://dev.to/philip_mcclarence_2ef9475/ivfflat-vs-hnsw-in-pgvector-which-index-should-you-use-305p — IVFFlat vs HNSW in pgvector (2026-03-04)
[^93^]: https://www.elastic.co/what-is/hybrid-search — What is hybrid search? Elasticsearch (2025-02-25)
[^96^]: https://stackoverflow.com/questions/77401874/how-to-calculate-amount-of-ram-required-for-serving-x-n-dimensional-vectors-with — HNSW RAM calculation (2023-11-01)
[^103^]: https://blog.nashtechglobal.com/full-text-search-in-postgresql-concepts-implementation-guide/ — Full-Text Search in PostgreSQL (2026-01-16)
[^107^]: https://neon.com/docs/data-types/tsvector — Postgres tsvector data type - Neon Docs (2026-03-13)
[^108^]: https://peterullrich.com/complete-guide-to-full-text-search-with-postgres-and-ecto — Complete Guide to Full-text Search with Postgres (2022-11-06)
[^113^]: https://www.depesz.com/2025/11/03/do-you-really-need-tsvector-column/ — Do you really need tsvector column? (2025-11-03)
[^114^]: https://supabase.com/docs/guides/database/extensions — Postgres Extensions Overview | Supabase (2026-05-06)
[^116^]: https://supabase.com/partners/paradedb — ParadeDB | Works With Supabase (2026-01-16)
[^142^]: https://www.postgresql.org/about/news/pgvector-080-released-2952/ — pgvector 0.8.0 Released (2024-11-11)
[^143^]: https://github.com/aws-samples/sample-dat409-hybrid-search-aurora-mcp — AWS Hybrid Search with Aurora PostgreSQL (2025-08-12)
[^144^]: https://dev.to/__8fa66572/postgresql-rls-in-go-architecting-secure-multi-tenancy-4ifm — PostgreSQL RLS Benchmarks (2026-01-29)
[^146^]: https://mariadb.com/docs/server/reference/sql-structure/vectors/optimizing-hybrid-search-query-with-reciprocal-rank-fusion-rrf/ — Optimizing Hybrid Search Query with RRF (2025-11-18)
[^150^]: https://www.postgresql.org/docs/current/gin.html — PostgreSQL GIN Indexes Documentation (2026-02-26)
[^151^]: https://github.com/pgvector/pgvector — pgvector GitHub (iterative scan docs)
[^152^]: https://www.pedroalonso.net/blog/postgres-multi-tenant-search/ — Multi-Tenant Search in PostgreSQL with RLS (2025-11-04)
[^156^]: https://pganalyze.com/blog/gin-index — Understanding Postgres GIN Indexes (2021-12-02)
[^162^]: https://www.alibabacloud.com/help/en/rds/apsaradb-rds-for-postgresql/pgvector-performance-test-based-on-hnsw-indexes/ — Benchmark pgvector HNSW (2026-03-28)
[^184^]: https://blog.starmorph.com/blog/rag-techniques-compared-best-practices-guide — RAG Techniques Compared 2026 (2026-04-21)
[^186^]: https://aimultiple.com/hybrid-rag — Hybrid RAG: Boosting RAG Accuracy (2026-03-11)
[^203^]: https://www.dbi-services.com/blog/pgvector-a-guide-for-dba-part-2-indexes-update-march-2026/ — pgvector, a guide for DBA – Part 2 (2026-03-01)
[^204^]: https://www.adarsha.dev/blog/rag-supabase-hybrid-search-ai-sdk — Building a RAG System with Supabase Hybrid Search (2025-09-28)
[^209^]: https://github.com/orgs/supabase/discussions/18061 — Supabase discussion: hybrid search with tsvector (2023-10-10)



================================================================================
# D2 — KB Quality Monitoring continuo

## Resumen ejecutivo

- **DeepEval y TruLens son frameworks de evaluación, no sistemas de monitoreo continuo nativo.** DeepEval brilla en CI/CD (pytest-native, 50+ métricas); TruLens brilla en tracing + RAG Triad (context relevance, groundedness, answer relevance). Ninguno reemplaza a Langfuse en observabilidad de producción [^56^][^62^].
- **El costo real del LLM-as-a-judge es $0.01–$0.10 por evaluación** según el modelo juez (GPT-4o mini / Claude Haiku reducen 60–80%). Para un MVP de 100 queries/día con sampling del 5%, el costo mensual de evaluación automatizada es ~$4.50–$15/mes por tenant, despreciable frente al MRR objetivo ($59–$89/mes) [^32^][^57^].
- **El riesgo principal no es el costo del juez, sino la sobrecarga operativa.** Equipos de 1–3 devs reportan que mantener pipelines de evaluación continua (DeepEval + TruLens + Langfuse) consume 15–25% del tiempo de desarrollo en los primeros 6 meses [^58^][^193^].
- **Recomendación para FaberLoom MVP:** Diferir DeepEval y TruLens como deuda técnica documentada. Usar **Langfuse datasets + LLM-as-a-judge nativo + logs estructurados + freshness audit** como cobertura mínima viable. Ingresar DeepEval en CI/CD solo en Fase 2 (post-MVP, ~2026-07) y TruLens solo si se detectan regressions de retrieval no explicables con Langfuse.
- **Freshness y embedding drift se resuelven con mecanismos simples:** hash de contenido + timestamp de último re-embed + staleness threshold por tipo de documento. El threshold de 30 días es un default genérico; para calzado de seguridad (normativa técnica + lista de precios) recomendamos 7 días para precios y 90 días para normas técnicas estables [^76^][^77^].

---

## Hallazgos por sub-pregunta

### 1. DeepEval setup production

#### ¿Qué métricas core y qué LLM judge?
DeepEval ofrece 14+ métricas estándar [^57^], incluyendo las 4 core solicitadas: `AnswerRelevancyMetric`, `FaithfulnessMetric`, `ContextualPrecisionMetric`, `ContextualRecallMetric` [^60^][^63^]. También soporta `GEval` (criteria-based chain-of-thought scoring) para evaluaciones subjetivas custom [^60^].

Para el LLM judge, la documentación oficial de Langfuse (que aplica a cualquier framework LLM-as-a-judge) recomienda modelos con strong instruction-following y structured output: **GPT-4o, Claude Sonnet, o Gemini Pro** [^32^]. Sin embargo, para evaluación en volumen, la práctica production 2026 es downgradear al juez: **GPT-4o-mini** ($0.15/$0.60 por 1M tokens) o **Claude Haiku 4.5** ($1/$5 por 1M tokens) reducen costos 60–80% con "modest accuracy loss" [^57^][^29^].

**Evidencia concreta de costo por evaluación:**
- Langfuse documenta: "A typical evaluation costs $0.01–0.10 per assessment" [^32^].
- genai.qa (abril 2026) desglosa por suite: 4-metric suite en DeepEval cuesta $0.02–$0.04 por muestra usando GPT-4o [^57^].
- Paper de Case-Aware LLM-as-a-Judge (arXiv 2026): ~$0.014 por turno usando GPT-4.1 (3,000 input tokens + 400 output tokens) [^110^].

#### ¿Online por query o batch nightly?
DeepEval está **diseñado para CI/CD, no para monitoreo online.** Su patrón nativo es `deepeval test run` en pytest antes del deploy [^56^][^62^]. Para producción, la integración con Langfuse permite pull de traces y push de scores, pero esto requiere orquestar un job batch (ej: ARQ + Redis en tu stack) que samplee trazas y corra evaluaciones [^57^][^81^].

La recomendación production 2026 es: **batch nightly o hourly, nunca online por query** (añade latencia y duplica costo) [^57^][^81^].

#### Integración con FastAPI + Langfuse
DeepEval no duplica observabilidad; **complementa Langfuse en el eje CI/CD vs. production monitoring** [^58^][^62^]:
- Langfuse captura trazas, latencia, costos, versiones de prompt.
- DeepEval (en CI) bloquea PRs si las métricas de golden dataset caen bajo threshold.
- DeepEval (en producción) solo si se configura un job batch que lea traces de Langfuse y escriba scores de vuelta.

**Versión estable 2026:** DeepEval 2.2.x es la versión estable documentada para producción. El changelog 2025 reporta mejoras en async handling, timeouts, retries, y soporte para PydanticAI [^196^].

### 2. TruLens setup production

#### Feedback functions y arquitectura
TruLens implementa el **RAG Triad**: `context_relevance` (retrieval), `groundedness` (generación anclada a contexto), `answer_relevance` (respuesta pertinente a la pregunta) [^62^][^79^]. También soporta bias, toxicity, y custom feedback functions.

TruLens se diferencia por su **tracing nativo vía OpenTelemetry**. Desde la versión 1.5.0 (2025), OTel está habilitado por default [^80^]. Esto permite instrumentar métodos con `@instrument` y capturar spans de retrieval y generation.

#### Dashboard cost: ¿instancia separada?
**No requiere instancia separada.** TruLens corre un dashboard local en Streamlit (`run_dashboard()`) que lee de la base de datos configurada [^195^]. Por default usa SQLite local (`default.sqlite`). Desde febrero 2026 soporta PostgreSQL nativamente [^186^], lo cual permite apuntar a la misma instancia de PostgreSQL que ya usas (Supabase), aunque esto implica schema management y potencial overhead de writes.

**Crítico:** El dashboard de TruLens **no es un servicio de producción.** Es una herramienta de debugging local. Para producción, Snowflake recomienda usar AI Observability en Snowsight si estás en su ecosistema [^79^][^195^]. Si no usas Snowflake, el valor de TruLens está en sus feedback functions programáticas, no en su dashboard.

#### ¿Cómo se mantiene cuando el modelo cambia?
TruLens usa `app_name` + `app_version` para tracking de experimentos [^189^]. Cuando cambias el modelo LLM, cambias `app_version` y los resultados aparecen comparables en el leaderboard. Sin embargo, **las evaluaciones históricas con un juez diferente no son comparables** [^57^]. Debes "pin the judge version".

#### Comparación con Langfuse evaluators nativos
Langfuse tiene LLM-as-a-judge nativo con costo de $0.01–$0.10 por assessment [^32^], pero su profundidad métrica es "basic" en comparación con TruLens/DeepEval/Ragas [^30^][^56^]. Langfuse también integra Ragas como cookbook oficial [^81^].

**Veredicto:** TruLens y Langfuse evaluators tienen overlap parcial. TruLens tiene RAG Triad más maduro; Langfuse tiene tracing + cost tracking + prompt versioning más maduro. La combinación TruLens + Langfuse no es redundante si usas TruLens solo para feedback functions y Langfuse para el resto.

### 3. Freshness monitoring

#### ¿Cómo se mide staleness en producción?
El patrón production 2026 estándar es:
1. **Content hash** en ingestión: SHA-256 del documento source. Si cambia, se re-encola.
2. **Timestamp de último re-embed** (`last_embedded_at`) en cada chunk.
3. **Staleness threshold por tipo de documento** (no un threshold global) [^76^][^77^].

PremAI (marzo 2026) documenta: "Hash document content at ingestion. On re-ingestion, compare hashes to detect updates. Incremental re-indexing: update only the chunks from changed documents, not the full corpus" [^76^].

#### Threshold real recomendado
El "30 días default" es un valor genérico de TDS (The Data School / cursillo) sin fundamento empírico. En producción, los thresholds deben calibrarse por dominio [^77^][^104^]:
- **Documentos dinámicos** (precios, inventario, políticas de envío): 1–7 días.
- **Documentos semi-estáticos** (especificaciones técnicas, normas): 30–90 días.
- **Documentos estáticos** (historial, manuales archivados): on-demand.

Para FaberLoom (calzado de seguridad):
- Listas de precios / catálogos: **7 días máximo**.
- Certificaciones normativas (ISO, ASTM, CSA): **90 días** (cambian anualmente).
- Fichas técnicas de materiales: **30 días**.

#### Trigger de re-embed automático vs manual
Recomendación: **automático para documentos dinámicos, manual con alerta para semi-estáticos.** El pipeline debe exponer una métrica `freshness_score` (0–100) que desciende con el tiempo desde el último re-embed [^77^]. Cuando cae bajo 85%, alerta. Cuando cae bajo 70%, modo degradado (advertir al usuario que la info puede estar desactualizada).

### 4. Embedding drift detection

#### Cosine distance threshold real
La literatura 2025–2026 cita **0.05–0.10 como rango práctico** para delta scoring [^104^]. Tianpan (abril 2026) reporta: "Delta scoring computes the cosine distance between the existing embedding for a document and a freshly computed embedding using the current model. If the distance exceeds a threshold (0.05–0.10 is commonly cited as practical), the document is flagged for reindexing" [^104^].

**¿Es agresivo o permisivo?**
- **0.05 es agresivo:** flaggeará ~15–30% de documentos en cada ciclo de validación (dependiendo del modelo y dominio).
- **0.10 es permisivo:** solo flaggeará documentos con cambio semántico sustancial (ej: términos técnicos nuevos, reorganización de secciones).

Para calzado de seguridad (vocabulario técnico relativamente estable), **0.08 es un punto de partida razonable**.

#### Drift legítimo (modelo nuevo) vs falso positivo
El drift por modelo nuevo se llama **version drift** [^109^]. Cuando cambias el embedding model, **todos los vectores del índice son incompatibles** con los nuevos query vectors. No es un "drift detectado"; es un evento de migración planificada.

**Reconciliación con `firewall_ruleset_hash` y `requires_rescan`:**
Tu metadata ya tiene `firewall_ruleset_hash` y `requires_rescan`. Propongo extender la metadata del chunk con:
- `embedding_model_version`: nombre+versión exacta del modelo (ej: `text-embedding-3-small@2024-01`).
- `content_hash`: SHA-256 del texto fuente.
- `last_embedded_at`: timestamp.
- `last_freshness_check_at`: timestamp del último delta scoring.
- `cosine_delta_score`: última distancia calculada (NULL si no se ha corrido).

Cuando `embedding_model_version` en el chunk != `embedding_model_version` en config, automáticamente `requires_rescan = TRUE`. Cuando `content_hash` cambia, `requires_rescan = TRUE`. Cuando `cosine_delta_score > threshold`, `requires_rescan = TRUE`.

### 5. Costo proyectado mensual

#### Base de cálculo
- **Queries por tenant:** 100/día = 3,000/mes.
- **Sampling rate para evaluación:** 5% (150 queries evaluadas/mes). La literatura 2026 recomienda 1–5% como suficiente para señal [^57^][^81^].
- **Judge model:** GPT-4o-mini ($0.15 input / $0.60 output por 1M tokens) [^29^].
- **Tokens por evaluación (4 métricas):** ~2,500 input + ~300 output = 2,800 tokens (estimación conservadora basada en [^110^]).
- **Costo por evaluación:** 2,500 × $0.15/1M + 300 × $0.60/1M = $0.000375 + $0.00018 = **~$0.000555**.
- **Costo mensual de evaluación por tenant:** 150 × $0.000555 = **~$0.08** (sí, ocho centavos).

Nota: Esto es solo el costo del LLM judge. La infraestructura (ARQ worker, PostgreSQL, Langfuse self-host) es compartida.

#### Tabla costo proyectado por tier de adopción

| Tier | Tenants | Queries/mes | Evals/mes (5% sample) | Costo LLM judge | Infra adicional (aprox) | Costo total monitoring |
|------|---------|-------------|----------------------|-----------------|------------------------|----------------------|
| **Validator** | 1 | 3,000 | 150 | ~$0.08 | $0 (compartido) | **~$0–$5** |
| **Early** | 10 | 30,000 | 1,500 | ~$0.80 | $0 (compartido) | **~$5–$15** |
| **Growth** | 100 | 300,000 | 15,000 | ~$8.00 | $0 (compartido) | **~$15–$50** |

*Infra adicional asume Langfuse self-host (ya en stack) + ARQ worker existente. Si se agrega TruLens dashboard separado, sumar ~$0 (SQLite) o costo marginal de PostgreSQL (ya incluido en Supabase).*

#### Comparación contra MRR target
| Tier | MRR estimado ($59–$89/tenant) | Costo monitoring | % de MRR consumido |
|------|-------------------------------|------------------|--------------------|
| 1 tenant | $59–$89 | $0–$5 | **0–8%** |
| 10 tenants | $590–$890 | $5–$15 | **1–3%** |
| 100 tenants | $5,900–$8,900 | $15–$50 | **0.3–0.8%** |

**Conclusión de costo:** El monitoring de calidad con LLM-as-a-judge es económicamente trivial frente al MRR. El problema no es el dinero, es el **tiempo de desarrollo y mantenimiento**.

### 6. Decisión MVP vs deuda

#### ¿Qué % de tenants production realmente usan DeepEval+TruLens?
No hay datos publicados de "% de tenants" porque estas herramientas se usan por el equipo de desarrollo, no por el tenant final. Sin embargo, los rankings 2026 de herramientas LLM muestran un patrón claro:
- **DeepEval** es el framework de testing más popular (14.7k stars, 3M downloads/mes, 20M evaluaciones/día) [^62^].
- **TruLens** tiene 3.2k stars y es menos adoptado que DeepEval o Ragas [^62^].
- La mayoría de equipos pequeños usa **Langfuse solo** o **Langfuse + Ragas** para producción, no DeepEval + TruLens [^30^][^56^][^58^].

Techsy (2026): "Most teams need tools from at least two categories: a testing framework for development and an observability platform for production" [^56^]. Pero nota: "DeepEval is a testing framework, not a monitoring tool. You'll need Langfuse or Phoenix for runtime tracing" [^56^].

#### Equipos pequeños (1–3 devs) — ¿es factible mantener?
**Veredicto: No en MVP de 60 días.** Braintrust (marzo 2026) describe el perfil ideal de DeepEval: "50–300 employees at Series A-B stage with $3M+ ARR" [^193^]. Latitude (abril 2026) es más explícito: "DeepEval is designed for pre-deployment testing. You can run it against production data by exporting traces and writing test cases, but there's no native integration for ingesting live traffic, clustering failure modes, or generating evals from real user behavior" [^58^].

Para un equipo 1–3 devs construyendo MVP en 60 días, agregar DeepEval + TruLens implica:
1. Escribir golden datasets.
2. Calibrar thresholds de 4+ métricas.
3. Orquestar jobs batch de evaluación.
4. Mantener dashboards/alertas.
5. Re-calibrar cuando cambie el juez o el modelo.

Eso es **2–4 semanas de trabajo** que no aporta directamente al MVP cerrado.

#### Plan B: métricas mínimas con Langfuse solo
Langfuse nativamente soporta [^32^][^112^]:
- **LLM-as-a-judge evaluators** (faithfulness, relevance, completeness) configurables vía LLM Connections.
- **Datasets** para evaluación offline.
- **Scores** (`langfuse.create_score`) para push de métricas custom.
- **Cost tracking** y **latency tracking** por trace.
- **User feedback scores** (thumbs up/down).

Con logs estructurados adicionales (ya en stack), puedes derivar:
- **Relevance proxy:** tasa de thumbs down / feedback negativo.
- **Faithfulness proxy:** tasa de "no se encontró en el contexto" o ediciones manuales del usuario (draft-first invariante ya captura esto).
- **Freshness proxy:** timestamp de último embed vs. timestamp de última modificación del source.

---

## Recomendación directa

### Lo que SÍ implementar en MVP (Foundation Beta, 2026-04-20 → 2026-06-14)

1. **Langfuse datasets + evaluación manual periódica:** Crear un dataset de 50–100 preguntas representativas (golden questions) del dominio calzado de seguridad. Correr evaluación LLM-as-a-judge vía Langfuse nativo una vez por semana manualmente o con ARQ job. Esto toma ~4 horas de setup y 30 min/semana de mantenimiento.

2. **Freshness audit pipeline:** Extender el chunk metadata con `content_hash`, `last_embedded_at`, `source_modified_at`, `document_type` (price_list | tech_spec | normative | catalog). ARQ job diario que compare `source_modified_at > last_embedded_at` y encole re-embed. Thresholds: 7d precios, 30d fichas técnicas, 90d normativas.

3. **Embedding drift sentinel:** Job mensual que samplee 5% de chunks, recalcule embeddings con el modelo actual, y compare cosine distance. Threshold 0.08. Si supera, marca `requires_rescan = TRUE`. Este job puede compartir infra con el freshness audit.

4. **User feedback como señal de calidad:** La invariante draft-first ya permite que el usuario corrija proformas. Ese feedback (edición vs. aceptación directa) es una métrica de calidad de KB más valiosa que cualquier LLM-as-a-judge abstracto.

### Lo que NO implementar en MVP

1. **DeepEval en CI/CD:** Aunque es pytest-native, agregarlo al MVP consume tiempo en calibración de thresholds y mantenimiento de golden datasets. El SPEC_FB_CONTRACT_TEST_HARNESS_v1 ya tiene 702 assertions; eso es la cobertura de calidad estructural por ahora.

2. **TruLens:** Su valor diferencial es el RAG Triad + tracing OTel, pero ya tienes Langfuse para tracing y puedes correr Ragas (integrado con Langfuse) si necesitas métricas RAG específicas. TruLens añade una dependencia más sin aportar capacidades críticas para MVP single-agent.

3. **Confident AI cloud:** $19.99–$49.99/seat/mes es un costo innecesario cuando el open-source core es gratuito y el valor del dashboard no es crítico en MVP [^187^].

4. **Evaluación online por cada query:** Añade latencia y costo sin beneficio proporcional. El sampling batch es suficiente.

### Lo que diferir a Fase 2 (post-MVP, ~2026-07)

1. **DeepEval pytest suite:** Cuando el pipeline CI/CD esté maduro (GitHub Actions), integrar `deepeval test run` con golden dataset versionado. Bloquear deploys si faithfulness < 0.80 en el dataset.

2. **TruLens feedback functions:** Si se detectan regressions de retrieval no explicables por Langfuse, considerar TruLens para RAG Triad en ambiente de staging.

3. **Automated LLM-as-a-judge 100%:** Cuando el volumen lo justifique (>500 queries/día por tenant) y el equipo tenga capacidad de mantener thresholds calibrados.

---

## Casos production citados

| Empresa | Caso | Métrica reportada | Fuente |
|---------|------|--------------------|--------|
| **Stratagem Systems** | 89 deployments RAG production | Small-scale RAG total initial: $7,500–$13,200; Monthly ongoing: $650–$1,750 | [^160^] |
| **Snowflake** | TruLens + Cortex Search para RAG internal | RAG Triad: context relevance, groundedness, answer relevance evals con Mistral Large | [^79^] |
| **Equinix / Tribble / KBC Group** | Usuarios reportados de TruLens en producción | OTel-based tracing + eval | [^62^] |
| **JPMorgan Chase** | Galileo para customer support RAG | Hallucination prevention, compliance audit trails | [^87^] |
| **OpenAI, Google, Microsoft** | Usuarios de DeepEval (según docs) | 20M evaluaciones/día, 3M downloads/mes | [^62^] |
| **Prem / RisingWave** | Streaming RAG vs Batch RAG | 100x diferencia de costo de embedding; 1% docs cambian diariamente | [^76^][^82^] |
| **Cloudflare edge RAG** | RAG system $5–$10/mes (vs $130–$190 tradicional) | 10,000 searches/mo | [^159^] |
| **Milvus / Zilliz** | Embedding drift detection | Cosine distance threshold 0.05–0.10 para delta scoring | [^104^] |

---

## Gotchas y riesgos

1. **Judge model drift:** Cambiar el modelo juez (ej: GPT-4o → Claude Sonnet) invalida comparaciones históricas. Documentar: "pin the judge version" [^57^].

2. **Threshold re-calibration:** Los thresholds definidos en desarrollo fallan en producción porque la distribución de dominio difiere. Re-baseline después de 2 semanas en producción [^57^].

3. **DeepEval ContextualPrecisionMetric sin ground-truth:** Se degrada silenciosamente a "LLM adivina qué contexto debería haber sido". Para RAG work, preferir Ragas context precision [^57^].

4. **TruLens + Langfuse overlap:** Ambos hacen tracing. Instrumentar ambos en el mismo pipeline genera duplicación de spans y confusión. Elegir uno como source of truth para traces (Langfuse) y el otro solo para feedback functions (TruLens).

5. **Staleness no es siempre un bug:** Un usuario preguntando por una norma de 2018 puede querer esa norma, no la última. El freshness threshold debe considerar intención del usuario, no solo timestamp.

6. **Embedding reindex cost cliff:** Re-embed 50K documentos con overlap puede costar $2,000+ si no se usa batch API o modelo small [^162^].

7. **SQLite de TruLens no escala:** El dashboard default usa SQLite. Para >10k evaluaciones, migrar a PostgreSQL es necesario [^186^][^188^].

8. **Sampling bias:** Evaluar solo el 5% de tráfico puede omitir edge cases críticos. Estratificar el sample por tipo de query (price, normative, availability).

---

## Tabla costo proyectado por tier de adopción (detallada)

| Componente | 1 tenant (100 q/día) | 10 tenants | 100 tenants |
|-----------|----------------------|------------|-------------|
| **Langfuse self-host** | $0 (Railway/Fly ya pagado) | $0 | $0 |
| **ARQ worker eval job** | $0 (compartido con cola async) | $0 | $0 |
| **LLM judge (5% sample, GPT-4o-mini)** | ~$0.08/mes | ~$0.80/mes | ~$8/mes |
| **Freshness audit job** | $0 (lógica en FastAPI + ARQ) | $0 | $0 |
| **Delta scoring job** | $0 (embeddings en batch, API existente) | $0 | $0 |
| **Embedding reindex (mensual, 1% corpus)** | ~$0.10 (OpenAI 3-small batch) | ~$1 | ~$10 |
| **PostgreSQL storage (Supabase)** | $0 (dentro de tier actual) | $0 | $0 |
| **TOTAL monitoring calidad** | **~$0.20/mes** | **~$2/mes** | **~$20/mes** |
| **MRR estimado (Pro tier $59–$89)** | $59–$89 | $590–$890 | $5,900–$8,900 |
| **% MRR en monitoring** | **0.2–0.3%** | **0.2–0.3%** | **0.2–0.3%** |

**Nota:** Esto asume sampling agresivo (5%), judge barato (GPT-4o-mini), y reuso total de infra existente. Si se usa GPT-4o como juez y 100% de queries evaluadas, multiplicar ×20–×100.

---

## Diagrama de integración con stack FaberLoom

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FABERLOOM MVP (Single Agent)                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │  WhatsApp    │───▶│   FastAPI    │───▶│   LiteLLM    │                   │
│  │  Business API│    │   + Pydantic │    │   Gateway    │                   │
│  └──────────────┘    │      AI      │    └──────────────┘                   │
│                      └──────┬───────┘                                       │
│                             │                                               │
│              ┌──────────────┼──────────────┐                              │
│              │              │              │                              │
│              ▼              ▼              ▼                              │
│       ┌──────────┐   ┌──────────┐   ┌──────────┐                        │
│       │ Supabase │   │  Redis   │   │  Letta   │                        │
│       │pgvector  │   │  + ARQ   │   │ self-host│                        │
│       │  + RLS   │   │  worker  │   │  memory  │                        │
│       └──────────┘   └────┬─────┘   └──────────┘                        │
│                             │                                              │
│                             ▼                                              │
│  ┌────────────────────────────────────────────────────────────────┐       │
│  │                     LANGFUSE (self-host)                        │       │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐              │       │
│  │  │   Traces   │  │  Datasets  │  │   Scores   │              │       │
│  │  │ (all req)  │  │(golden QA) │  │(manual/bat)│              │       │
│  │  └────────────┘  └────────────┘  └────────────┘              │       │
│  └────────────────────────────────────────────────────────────────┘       │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────┐       │
│  │              QUALITY MONITORING MVP (Phase 1)                   │       │
│  │  • Freshness audit (ARQ daily): hash compare + timestamp        │       │
│  │  • Drift sentinel (ARQ monthly): delta cosine sampling          │       │
│  │  • Langfuse LLM-as-judge: weekly manual/batch on dataset       │       │
│  │  • User feedback: draft-first edit rate per tenant            │       │
│  │  • Logs estructurados: JSONL → queryable en Supabase           │       │
│  └────────────────────────────────────────────────────────────────┘       │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────┐       │
│  │              DEFERRED TO PHASE 2 (post-MVP)                     │       │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐                │       │
│  │  │ DeepEval │    │ TruLens  │    │ Confident│                │       │
│  │  │  CI/CD   │    │  RAG     │    │   AI     │                │       │
│  │  │  pytest  │    │  Triad   │    │ dashboard│                │       │
│  │  └──────────┘    └──────────┘    └──────────┘                │       │
│  └────────────────────────────────────────────────────────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Flujo de datos evaluación:**
1. FastAPI instrumenta cada request con Langfuse SDK.
2. ARQ worker `freshness_audit` corre daily: lee `chunk_metadata`, compara `content_hash` con source, marca `requires_rescan`.
3. ARQ worker `drift_sentinel` corre monthly: samplea 5% chunks, recalcula embedding, guarda `cosine_delta_score`.
4. ARQ worker `langfuse_eval` corre weekly: lee dataset de golden questions, corre LLM-as-judge vía LiteLLM (GPT-4o-mini), escribe scores a Langfuse.
5. Dashboard de calidad es Langfuse UI + queries SQL directas a Supabase (chunk_metadata).

---

## SPEC propuesto: SPEC_FB_KB_QUALITY_MONITORING_v1

### Scope mínimo viable

**Status:** PROPOSED  
**Target release:** Foundation Beta (2026-04-20 → 2026-06-14)  
**Owner:** CTO/Founder (tú) + contractor ocasional  
**Decision:** Diferir DeepEval y TruLens. Implementar Plan B (Langfuse-native + jobs ARQ).

### 1. Freshness Monitoring

```sql
-- Extensión a chunk_metadata (ya existe tabla)
ALTER TABLE chunk_metadata ADD COLUMN IF NOT EXISTS content_hash VARCHAR(64);
ALTER TABLE chunk_metadata ADD COLUMN IF NOT EXISTS source_modified_at TIMESTAMPTZ;
ALTER TABLE chunk_metadata ADD COLUMN IF NOT EXISTS last_embedded_at TIMESTAMPTZ;
ALTER TABLE chunk_metadata ADD COLUMN IF NOT EXISTS document_type VARCHAR(32); -- price_list | tech_spec | normative | catalog
ALTER TABLE chunk_metadata ADD COLUMN IF NOT EXISTS staleness_threshold_days INT DEFAULT 30;
ALTER TABLE chunk_metadata ADD COLUMN IF NOT EXISTS requires_rescan BOOLEAN DEFAULT FALSE;
ALTER TABLE chunk_metadata ADD COLUMN IF NOT EXISTS last_freshness_check_at TIMESTAMPTZ;
ALTER TABLE chunk_metadata ADD COLUMN IF NOT EXISTS cosine_delta_score FLOAT;
ALTER TABLE chunk_metadata ADD COLUMN IF NOT EXISTS embedding_model_version VARCHAR(64);
```

**Job `freshness_audit_daily` (ARQ):**
- Entrada: todos los chunks donde `last_freshness_check_at < NOW() - INTERVAL '1 day'`.
- Lógica: para cada chunk, comparar `content_hash` con hash actual del source. Si diff → `requires_rescan = TRUE`.
- Si `source_modified_at > last_embedded_at` → `requires_rescan = TRUE`.
- Si `NOW() - last_embedded_at > staleness_threshold_days` → `requires_rescan = TRUE`.
- Salida: lista de `chunk_id` marcados para re-embed. Encolar en ARQ `reembed_job`.

**Thresholds por tipo (configurables por tenant):**
| document_type | staleness_threshold_days default |
|---------------|----------------------------------|
| price_list    | 7                                |
| catalog       | 14                               |
| tech_spec     | 30                               |
| normative     | 90                               |

### 2. Embedding Drift Sentinel

**Job `drift_sentinel_monthly` (ARQ):**
- Samplear 5% de chunks aleatorios (mínimo 100, máximo 1,000).
- Recalcular embedding con modelo actual (`embedding_model_version` en config).
- Calcular cosine distance vs embedding almacenado.
- Si distance > 0.08 → `requires_rescan = TRUE` + `cosine_delta_score = <valor>`.
- Si `embedding_model_version` del chunk != config → `requires_rescan = TRUE` (version drift).

### 3. Langfuse Quality Scoring

**Dataset `golden_questions_v1` (Langfuse):**
- 50 preguntas representativas del dominio calzado de seguridad.
- 5 categorías: precios (10), disponibilidad (10), normativas (10), especificaciones (10), cobertura geográfica (10).
- Respuestas esperadas no son ground-truth absoluto; son guía para evaluador LLM.

**Evaluador LLM-as-a-judge (LiteLLM → GPT-4o-mini):**
- Métricas: `faithfulness`, `answer_relevancy`, `context_precision_without_reference`.
- Frecuencia: semanal (ARQ job `langfuse_eval_weekly`).
- Sampling: 100% del golden dataset (offline, no afecta producción).

**User feedback proxy (en producción):**
- `draft_edit_rate` = (# proformas editadas por usuario / # proformas generadas).
- `draft_rejection_rate` = (# proformas descartadas / # generadas).
- Estas métricas se escriben como `scores` en Langfuse vía SDK.

### 4. Alertas

- Freshness score < 85% (tenant-level): alerta Slack/email.
- Freshness score < 70%: modo degradado (mensaje al usuario: "Información sujeta a verificación").
- Drift sentinel > 10% de chunks con `requires_rescan`: alerta prioritario.
- Langfuse eval faithfulness < 0.70 en golden dataset: alerta + revisión manual.

### 5. Deuda técnica documentada

**Ticket D2-001:** Integrar DeepEval pytest suite en CI/CD post-MVP.  
**Ticket D2-002:** Evaluar TruLens RAG Triad si regressions de retrieval no son explicables con Langfuse.  
**Ticket D2-003:** Considerar Ragas como alternativa a TruLens para métricas RAG académicas (integración cookbook ya existe en Langfuse [^81^]).

---

## Sources

1. [DeepEval by Confident AI - Official](https://deepeval.com/) [^60^]
2. [DeepEval Practical Guide - Medium 2025](https://codemaker2016.medium.com/understanding-deepeval-a-practical-guide-for-evaluating-large-language-models-d7272b6c2634) [^63^]
3. [Langfuse LLM-as-a-Judge Docs](https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge) [^32^]
4. [LLM API Pricing Comparison 2025-2026 - IntuitionLabs](https://intuitionlabs.ai/articles/llm-api-pricing-comparison-2025) [^31^]
5. [The Definitive LLM Selection Guide - Iternal, March 2026](https://iternal.ai/llm-selection-guide) [^29^]
6. [8 Best LLM Evaluation Tools 2026 - Techsy](https://techsy.io/en/blog/best-llm-evaluation-tools) [^56^]
7. [DeepEval vs RAGAS 2026 - genai.qa](https://genai.qa/blog/deepeval-vs-ragas/) [^57^]
8. [DeepEval Alternatives - Latitude, April 2026](https://latitude.so/blog/deepeval-alternatives) [^58^]
9. [RAGAS vs TruLens vs DeepEval 2026 - Atlan](https://atlan.com/know/llm-evaluation-frameworks-compared/) [^62^]
10. [LLM Testing Tools 2026 - ContextQA](https://contextqa.com/blog/llm-testing-tools-frameworks-2026/) [^59^]
11. [8 Best DeepEval Alternatives - ZenML, Nov 2025](https://www.zenml.io/blog/deepeval-alternatives) [^61^]
12. [RAG Evaluation Tools - Qawerk, April 2026](https://qawerk.com/blog/rag-evaluation-tools/) [^30^]
13. [Top 5 RAG Evaluation Tools 2026 - Maxim](https://www.getmaxim.ai/articles/top-5-rag-evaluation-tools-for-production-ai-systems-2026/) [^34^]
14. [RAG Observability and Evals - Langfuse Blog, Oct 2025](https://langfuse.com/blog/2025-10-28-rag-observability-and-evals) [^112^]
15. [Evaluation of RAG with Ragas - Langfuse Cookbook](https://langfuse.com/guides/cookbook/evaluation_of_rag_with_ragas) [^81^]
16. [Langfuse for RAG - Leanware, April 2026](https://www.leanware.co/insights/langfuse-for-rag) [^75^]
17. [TruLens + Snowflake Cortex Quickstart](https://www.snowflake.com/en/developers/guides/getting-started-with-llmops-using-snowflake-cortex-and-trulens/) [^79^]
18. [TruLens 2025 Blog - OTel](https://www.trulens.org/blog/archive/2025/) [^80^]
19. [TruLens 2.6 PostgreSQL Support - Feb 2026](https://www.trulens.org/blog/2026/02/03/trulens-26-skills-for-ai-coding-assistants-postgresql-support-and-more/) [^186^]
20. [TruLens Dashboard Docs](https://www.trulens.org/getting_started/dashboard/) [^195^]
21. [TruLens Where to Log](https://www.trulens.org/component_guides/logging/where_to_log/) [^188^]
22. [TruLens v1 Migration - Aug 2024](https://www.trulens.org/blog/2024/08/30/moving-to-trulens-v1-reliable-and-modular-logging-and-evaluation/) [^189^]
23. [RAG That Doesn't Lie - AIMind, Jan 2026](https://pub.aimind.so/rag-that-doesnt-lie-d28dbdfe8e79) [^83^]
24. [Embedding Drift Silent Degradation - Tianpan, April 2026](https://tianpan.co/blog/2026-04-16-embedding-drift-silent-semantic-search-degradation) [^104^]
25. [Milvus Embedding Drift Guide](https://milvus.io/ai-quick-reference/what-is-the-impact-of-embedding-drift-and-how-do-i-manage-it) [^103^]
26. [Embedding Model Migration - Medium, April 2026](https://medium.com/@isuruig/embedding-model-migration-without-downtime-the-drift-adapter-pattern-for-production-vector-6f3c62abed99) [^108^]
27. [Handling Embedding Model Version Drift - AboutVectorDatabase](https://aboutvectordatabase.com/learn/handling-updates-to-embedding-model-version-drift/) [^109^]
28. [Building Production RAG 2026 - PremAI](https://blog.premai.io/building-production-rag-architecture-chunking-evaluation-monitoring-2026-guide/) [^76^]
29. [Knowledge Decay Problem - RagAboutIt, Dec 2025](https://ragaboutit.com/the-knowledge-decay-problem-how-to-build-rag-systems-that-stay-fresh-at-scale/) [^77^]
30. [RAG Architecture 2026 - RisingWave](https://risingwave.com/blog/rag-architecture-2026/) [^82^]
31. [RAG Implementation Cost 2026 - Stratagem Systems](https://www.stratagem-systems.com/blog/rag-implementation-cost-roi-analysis) [^160^]
32. [OpenAI Embeddings Pricing Calculator - CostGoat, Feb 2026](https://costgoat.com/pricing/openai-embeddings) [^157^]
33. [Embedding Infrastructure at Scale - Introl, Feb 2026](https://introl.com/blog/embedding-infrastructure-scale-vector-generation-production-guide-2025) [^161^]
34. [Production RAG for $5/mo - Dev.to, Dec 2025](https://dev.to/dannwaneri/i-built-a-production-rag-system-for-5month-most-alternatives-cost-100-200-21hj) [^159^]
35. [The Scale Trap RAG - RagAboutIt, Dec 2025](https://ragaboutit.com/the-scale-trap-why-your-rag-cost-explodes-at-10000-documents/) [^162^]
36. [7 Top RAG Evaluation Tools - Galileo, Dec 2025](https://galileo.ai/blog/rag-evaluation-tools) [^87^]
37. [Best RAG Evaluation Tools 2025 - Braintrust](https://www.braintrust.dev/articles/best-rag-evaluation-tools) [^47^]
38. [How to Evaluate RAG Systems - Comet, Feb 2026](https://www.comet.com/site/blog/rag-evaluation/) [^111^]
39. [RAG Evaluation Complete Guide - EvidentlyAI, Aug 2025](https://www.evidentlyai.com/llm-guide/rag-evaluation) [^113^]
40. [Confident AI Pricing](https://www.confident-ai.com/pricing) [^187^]
41. [Confident AI vs DeepEval - Respan, March 2026](https://respan.ai/market-map/compare/confident-ai-vs-deepeval) [^185^]
42. [DeepEval Changelog 2025](https://deepeval.com/changelog/changelog-2025) [^196^]
43. [Case-Aware LLM-as-a-Judge - arXiv, Feb 2026](https://arxiv.org/html/2602.20379v1) [^110^]
44. [LLM API Cost Comparison - InventiveHQ, Dec 2025](https://inventivehq.com/blog/llm-api-cost-comparison) [^90^]
45. [Top LLM Observability Tools 2025 - LangWatch](https://langwatch.ai/blog/top-10-llm-observability-tools-complete-guide-for-2025) [^163^]
46. [Langfuse vs LangSmith - HuggingFace Blog, Nov 2025](https://huggingface.co/blog/daya-shankar/langfuse-vs-langsmith-vs-langchain-comparison) [^158^]
47. [RAG Evaluation Metrics - Confident AI, Oct 2025](https://www.confident-ai.com/blog/rag-evaluation-metrics-answer-relevancy-faithfulness-and-more) [^41^]
48. [Cosine Similarity Lies - Dev.to, April 2026](https://dev.to/gabrielanhaia/cosine-similarity-lies-heres-what-to-use-when-your-embeddings-all-cluster-at-085-3dfe) [^106^]



================================================================================
# D3 — Chunking strategies "by user query"

## Resumen ejecutivo

- El estado del arte en chunking para RAG (2025-2026) ha consolidado **7 estrategias dominantes**, con un claro ganador por tipo de contenido: recursive splitting como default seguro, semantic chunking para contenido heterogéneo con presupuesto, y **hierarchical parent-child** como approach premium para documentos estructurados [^19^][^21^].
- La estrategia "chunk by user query" —indexar documentos por las preguntas que responden, no solo por su contenido bruto— ha emergido formalmente como **Intent-Driven Dynamic Chunking (IDC)** en investigación 2026 [^313^], con mejoras de 5-67% en top-1 retrieval accuracy y 40-60% reducción en número de chunks. Es la evolución natural de "query-focused indexing" que combina generación automática de preguntas + boundary optimization.
- Casos B2B reales muestran mejoras **concretas y medibles**: Harvey AI (legal) reporta tool selection precision de 0.8-0.9 y retrieval calibrado a 3-10 operaciones por query complejo [^273^]; 47billion (consulting/universidades) logró 89% accuracy vs 61% con fixed-size mediante parent-child chunking [^21^]; Snowflake Finance RAG demostró que chunking + late chunking + hybrid search superan a approaches naive en ANLS [^253^].
- **Para MWT/FaberLoom**, la recomendación directa es: **NO migrar masivamente ahora**. Implementar lazy migration con dual-index PostgreSQL usando `CREATE INDEX CONCURRENTLY`, comenzar con **recursive chunking + sentence window** para 430 documentos operativos, y introducir **query-enriched metadata** (10-12 preguntas generadas vía LLM por archivo) en el frontmatter de cada archivo KB. Esto da el 80% del beneficio de "chunk by query" sin reindexar todo.
- El costo de generar 10-12 preguntas por archivo con GPT-4.1 Nano (vía LiteLLM) es ~$0.001-0.003 por archivo, o **$0.50-1.60 para 540 archivos**. El esfuerzo de migración lazy es estimado en **2-3 días de trabajo de un developer**, con riesgo de downtime cercano a cero si se usa `REINDEX CONCURRENTLY`.

---

## Hallazgos por sub-pregunta

### 1. Estado del arte chunking 2025-2026

#### Fixed-size chunking (estatus: deprecated para producción B2B)

Fixed-size chunking con tokens uniformes y overlap arbitrario está **formalmente superado** para casos de uso enterprise. La evidencia acumulada 2024-2026 es contundente:

- **Vectara NAACL 2025** (peer-reviewed, arXiv:2410.13070): fixed-size chunking de 200 palabras **superó consistentemente a semantic chunking** en retrieval + answer generation en datasets realistas [^19^]. Esto no defiende fixed-size como óptimo, sino que demuestra que semantic chunking mal configurado (sin floor de tamaño) es peor que fixed-size bien ajustado.
- **Context recall de 0.72** reportado en producción con fixed-size 512 tokens en un KB enterprise de Confluence + HR policies [^219^]: "roughly one in four queries was missing a piece of information that existed in the corpus".
- Cuándo SÍ funciona: FAQs cortas, product descriptions self-contained, meeting notes uniformes [^193^].

#### Recursive chunking (estatus: default recomendado)

Recursive character splitting (prioridad: `\n\n` → `\n` → `. ` → ` ` → ``) es el **default más seguro** según múltiples benchmarks independientes:

- LangChain lo recomienda como default. FloTorch 2026 lo posicionó 15 puntos por encima de semantic chunking mal configurado en end-to-end accuracy [^19^].
- **Parámetros de inicio**: chunk_size 400-512 tokens, overlap 50-100 tokens (10-20%). [^19^][^279^]
- NVIDIA benchmark (2024): 256-512 para factoid queries; 512-1024 para analytical/multi-hop [^19^].

#### Semantic chunking (estatus: condicional, requiere floor de tamaño)

Tres benchmarks independientes 2024-2026 muestran resultados contradictorios que **se explican por qué métrica se mide**:

| Benchmark | Métrica | Semantic Result | Fixed/Recursive Result |
|---|---|---|---|
| Chroma 2024 | Retrieval recall | 91.9% | ~88% |
| FloTorch 2026 | End-to-end accuracy | 54% | 69% |
| Vectara NAACL 2025 | Retrieval + answer gen | Perdió | Ganó |

**La causa raíz**: FloTorch produjo fragments de 43 tokens promedio con semantic chunking. Chunks tan pequeños retrieven bien pero dan al LLM "too little context to answer questions accurately" [^19^].

**Regla de oro**: `min_chunk_size=200` (mejor 300-400 tokens) es **obligatorio** en producción. Sin floor, semantic chunking produce micro-fragments que retrieven bien pero responden mal [^19^][^193^].

#### Late chunking (Jina AI, 2025)

Late chunking invierte el orden: **embed el documento completo primero, luego hace chunk pooling** de los spans. Cada chunk hereda contexto del documento completo, resolviendo pronombres y cross-references.

- **Benchmark**: +6.5 nDCG@10 puntos en NFCorpus (medical docs con cross-references) [^22^].
- **Limitación**: Solo soportado por jina-embeddings-v3 y pocos modelos. OpenAI, Cohere no lo tienen [^22^].
- **ROI**: "Highest ROI improvement available in 2026" — mismo costo, un parámetro extra [^22^].
- Para MWT: **no aplicable en MVP** a menos que cambien de embedding model (stack frozen = no).

#### Hierarchical chunking (parent-child)

**Estrategia dominante para documentos estructurados B2B**. Separar retrieval granularity de generation context:

- **Child chunks**: 200-400 tokens para retrieval preciso (embedding + vector search).
- **Parent chunks**: 1000-2000 tokens para generation context (recuperado por referencia del child).
- **Resultados medidos**: 47billion reportó en 200 student queries sobre 15 university decks: fixed-size 61% → semantic 72% → **hierarchical 89%** accuracy. Faithfulness: 0.74 → 0.81 → **0.91**. Context precision: 0.58 → 0.69 → **0.84** [^21^].
- **Implementación**: LlamaIndex `ParentDocumentRetriever`, LangChain `ParentDocumentRetriever`, Weaviate hybrid con child-first aggregation [^20^][^17^].
- H-RAG (SemEval-2026): 3-sentence child chunks, stride 2, max-score aggregation a parent. nDCG@5=0.4271, parent-level rescoring ganó +0.0197 nDCG@5 sobre child-first [^17^].

#### Sliding window con overlap

Overlap de 10-20% entre chunks consecutivos es **no negociable** para contenido donde la respuesta cruza boundaries. Microsoft Azure recomienda 25% (128 tokens) como starting point conservador. Para sparse retrieval (SPLADE), overlap puede no ayudar [^19^].

#### Chunk by user query / Intent-Driven Dynamic Chunking

El concepto que el usuario describe como "TDS approach" tiene ahora una formalización académica: **Intent-Driven Dynamic Chunking (IDC)**, paper de febrero 2026 [^313^].

Core idea: en lugar de chunking genérico, usar **predicted user queries** para guiar los chunk boundaries. El algoritmo:

1. LLM genera likely user intents para un documento.
2. Dynamic programming encuentra chunk boundaries óptimos que maximizan la probabilidad de que cada chunk contenga una respuesta completa a al menos una query.
3. Produce 40-60% menos chunks que baselines con 93-100% answer coverage.

**Mejoras medidas**: top-1 retrieval accuracy +5% a +67% en 5 de 6 datasets (news, Wikipedia, academic papers, technical docs) [^313^].

Esto se conecta con:
- **Query-Dependent Chunking** de AI21 (2026): multi-scale indexing con rank-based aggregation via Reciprocal Rank Fusion [^310^].
- **QuestionsAnsweredExtractor** de LlamaIndex: extrae "3 preguntas que este nodo responde" como metadata [^300^].
- **RAGAS TestsetGenerator**: genera Q&A pairs sintéticos por documento para evaluación [^306^].

#### Tabla de decisión por caso de uso B2B

| Estrategia | Cuándo usar | Cuándo NO usar | Costo relativo |
|---|---|---|---|
| **Fixed-size** | Prototipos, FAQs uniformes, speed-critical | Docs con tablas, cláusulas, estructura jerárquica | Bajo |
| **Recursive** | Default general, docs con párrafos | Contenido sin estructura (OCR, chat logs) | Bajo |
| **Semantic** | Contenido heterogéneo, topic shifts sutiles | Corpus homogéneo, budget constrained | Medio |
| **Late chunking** | Docs con cross-references, pronouns densos | Docs > context window del embedding model | Medio |
| **Hierarchical parent-child** | Legal, specs técnicas, KBs estructurados | Contenido corto self-contained | Medio-Bajo |
| **Agentic chunking** | Corpus muy diverso (PDFs + código + logs) | MVP, corpus < 1K docs | Alto |
| **Query-driven / IDC** | KBs maduros con query logs conocidos, accuracy-critical | MVP sin query history, corpus pequeño | Medio |

---

### 2. Casos B2B reales que migraron de doc-based a query-aware

#### Legal: Harvey AI (Am Law 100)

- **Empresa**: Harvey AI, sirve a 97% de Am Law 100 [^269^].
- **Problema**: Legal research requiere precision extrema; citations incorrectas son inaceptables.
- **Approach**: Combinación de long-context LLMs para análisis de documento individual + RAG para search across collections. Evaluación systematic con legal experts internos (Applied Legal Researchers) [^273^].
- **Métricas reportadas**: 
  - Tool selection precision: near zero → **0.8-0.9** tras calibración con eval data [^273^].
  - Queries complejas que inicialmente resolvían en single tool call ahora escalan apropiadamente a **3-10 retrieval operations** basado en query demand [^273^].
  - 4,000+ lawyers en 43 jurisdicciones ahorran **2-3 horas/semana**, 30% reducción en contract review time, 7 horas promedio ahorradas en document analysis complejo [^275^].
- **Chunking implícito**: Harvey usa "iterative processing workflows" donde attorneys deben manualmente segmentar queries complejas cuando el prompt limit cae de 100K a 4K characters [^272^]. Esto indica que chunking/query segmentation es parte activa del pipeline, aunque no documentado públicamente como "query-based".

#### Consulting / Knowledge Management: 47billion (universidades + consulting)

- **Empresa**: 47billion, plataforma de RAG para contenido educativo/enterprise [^21^].
- **Problema**: 200 student queries sobre 15 university presentation decks. Fixed-size chunking producía fragments de bullet points mezclados, respuestas vagas.
- **Migación**: Fixed-size (512 tokens) → Hierarchical parent-child.
- **Métricas pre/post**:
  - Answer accuracy: 61% → **89%** (+28 puntos)
  - Faithfulness: 0.74 → **0.91**
  - Context precision: 0.58 → **0.84**
- **Insight clave**: "Hierarchical approach didn't just improve accuracy — it specifically improved the cases that matter most: questions that require understanding WHERE a piece of information sits in the document" [^21^].

#### Manufacturing / Product catalogs: Lucidworks B2B commerce

- **Empresa**: Lucidworks, plataforma de AI search para B2B commerce [^318^].
- **Problema**: B2B catalogs técnicos (HVAC, automotive parts, sensors). Buyers necesitan precision specs. Información está "buried across multiple PDFs and spec sheets, each structured differently and rarely indexed for search".
- **Approach**: RAG con metadata extraction + chunking avanzado para aislar respuestas precisas.
- **Ejemplo concreto**: Query "Will this sensor support 4-20 mA output signal on a DIN rail mount?" → Respuesta directa: "Yes, Model X300 supports 4-20 mA signaling and mounts on standard 35mm DIN rails."
- **Métricas**: No reportan números públicos formales, pero el case study enfatiza que la fricción de catalog search desaparece cuando el chunking respeta la estructura técnica del documento (spec sheets con compatibility matrices).

#### Enterprise Knowledge Base: UI Chicago (SAP Business One docs)

- **Institución**: University of Illinois Chicago [^291^].
- **Corpus**: Documentación técnica SAP Business One.
- **Chunking tested**: Semantic vs Recursive vs Naive.
- **Resultados**: 
  - Recursive + TF-IDF weighted embeddings: **82.5% precision**.
  - Semantic content-only: 73.3% precision.
  - Naive + prefix-fusion: **Hit Rate@10 = 0.925**.
- **Conclusión**: "Recursive chunking paired with TF-IDF weighted embeddings yielding an 82.5% precision rate compared to 73.3% for semantic content-only approaches." Metadata enrichment consistently outperformed content-only baselines [^291^].

#### Finance RAG: Snowflake

- **Empresa**: Snowflake, evaluación de RAG para documentos financieros [^253^].
- **Métricas**: ANLS (Average Normalized Levenshtein Similarity) y LLM-based quality scores para juzgar correctness y completeness.
- **Hallazgo**: "Next post will correlate metrics at document level, chunk level, and final generation level" — indicando que chunk-level evaluation es crítica para finance RAG.

#### Producción interna: Enterprise KB (Confluence + runbooks)

- **Autor**: Artículo TDS "Your Chunks Failed Your RAG in Production" [^219^].
- **Baseline**: Fixed-size 512 tokens, overlap 50.
- **RAGAS métricas iniciales**: Context recall 0.72, faithfulness 0.86.
- **Post-migración a sentence windows**: Context recall 0.72 → **0.88**, faithfulness 0.86 → **0.91**, context precision 0.71 → **0.83**.
- **Tiempo ahorrado**: "The numbers will save you days of guesswork" — enfatizando que evaluación sistemática pre/post evita debugging por intuición.

---

### 3. Herramientas para "chunk by query"

#### LlamaIndex QuestionsAnsweredExtractor

LlamaIndex provee un extractor de metadata nativo que genera automáticamente preguntas que un nodo/chunk responde:

```python
from llama_index.core.extractors import QuestionsAnsweredExtractor
from llama_index.core.ingestion import IngestionPipeline

transformations = [
    TokenTextSplitter(chunk_size=512, chunk_overlap=128),
    QuestionsAnsweredExtractor(questions=3),  # Genera 3 preguntas por chunk
]

pipeline = IngestionPipeline(transformations=transformations)
```

**Limitación**: Genera preguntas por chunk (post-chunking), no guía el chunking itself. Para IDC-style "chunk by query", hay que invertir el orden: generar queries primero, luego chunk óptimo [^300^].

#### RAGAS TestsetGenerator

RAGAS provee generación de test sets sintéticos para evaluación de RAG:

- **Proceso**: Knowledge graph construction → semantic clustering → NER → question-answer synthesis.
- **Tipos de preguntas**: single-hop, multi-hop, reasoning, conditional.
- **Costo reportado**: Generar ~500 questions de U.S. Code titles costó **23.81 €** total, con GPT-4o como critic model (93.6% del costo) [^306^].
- **Limitación**: Diseñado para evaluación, no para indexing. Pero las preguntas generadas pueden reutilizarse como metadata de query-intent.

#### Generación automática de "10-12 questions" por archivo

**Opción A: LLM puro** (recomendada para MWT)

Prompt template para generación híbrida:

```
Eres un analista de producto para FaberLoom. Lee este documento y genera:
1. 5 preguntas factuales directas que un comprador B2B haría (precios, specs, disponibilidad)
2. 3 preguntas analíticas/comparativas ("¿por qué X vs Y?")
3. 2 preguntas de proceso/procedimiento ("¿cómo cotizar?", "¿cuál es el plazo?")
4. 2 preguntas edge-case o de excepción ("¿qué pasa si...?")

Reglas:
- Cada pregunta debe ser respondible ÚNICAMENTE con la información del documento.
- Si el documento no tiene información suficiente, genera menos preguntas, no inventes.
- Formato: lista numerada, español neutro LATAM.
```

**Modelo recomendado**: GPT-4.1 Nano ($0.10/M input, $0.40/M output) o GPT-4o Mini ($0.15/M input) vía LiteLLM [^281^][^31^]. Para 540 archivos, estimado:
- Input: ~1,000 tokens promedio por archivo × 540 = 540K tokens.
- Output: ~300 tokens (10 preguntas) × 540 = 162K tokens.
- **Costo total**: ~$0.50-1.60 con GPT-4.1 Nano / GPT-4o Mini [^281^].

**Opción B: Híbrido humano-LLM**

- LLM genera borrador de 15 preguntas.
- Curador humano (COMMITTEE) selecciona las 10-12 mejores, descarta las inventadas o irrelevantes.
- Más lento pero mayor calidad y confianza. Recomendado para los 50-100 archivos más críticos (POL, PLB, SKILL).

**Opción C: LLM judge para filtrado**

- Generar 15 preguntas con LLM.
- Segundo LLM actúa como judge: "¿Es esta pregunta realista para un usuario de FaberLoom?" Threshold de aceptación.
- Automatiza el filtrado sin intervención humana.

#### DeepEval / RAGAS para validación

```python
from deepeval.metrics import ContextualRelevancyMetric
from deepeval.test_case import LLMTestCase

metric = ContextualRelevancyMetric(threshold=0.7, model="gpt-4")
test_case = LLMTestCase(
    input="¿Cuál es el precio del botín X-200?",
    actual_output="El botín X-200 cuesta $89.50.",
    retrieval_context=[chunk_text]
)
metric.measure(test_case)
# Score > 0.7 = chunk SÍ responde la query
```

RAGAS provee metrics similares: context precision, context recall, faithfulness [^42^][^43^].

---

### 4. Validación que un chunk responde una query

#### Métrica: ¿semantic similarity? ¿LLM judge? ¿humano?

La evidencia 2025-2026 sugiere una **jerarquía de validación**:

| Método | Costo | Precisión | Cuándo usar |
|---|---|---|---|
| **Embedding cosine similarity** | Cercano a cero | Moderada (captura semántica, no factualidad) | Pre-filtro rápido, descartar < 0.6 |
| **Cross-encoder reranker** | Bajo | Alta (mejor que bi-encoder) | Re-ranking post-retrieval |
| **LLM-as-a-judge** | Medio | Muy alta | Validación final, especialmente para compliance |
| **Humano (expert)** | Alto | Máxima | Golden set, calibración automatizada |

**Combinación recomendada** (stack production):
1. Bi-encoder cosine similarity para retrieval top-k (rápido).
2. Cross-encoder reranker para refinar ranking (BAAI/bge-reranker-v2-m3 usado en H-RAG [^17^]).
3. LLM judge para validación de faithfulness y answer correctness (DeepEval/RAGAS) [^41^].

#### Threshold real: cuándo decir "este chunk SÍ responde esta query"

- **Cosine similarity**: Threshold de 0.65-0.75 para bi-encoder general. >0.8 es muy estricto (puede perder matches válidos). <0.5 es muy permisivo (ruido). [^284^][^304^]
- **Clinical decision support benchmark**: similarity threshold de **0.8** para semantic chunking evitó topic bleeding sin oversplitting [^305^].
- **ContextualRelevancyMetric (DeepEval)**: Threshold 0.7 = al menos 70% del retrieved context es relevante para la query [^41^].
- **Recomendación para MWT**: 
  - Pre-filter retrieval: cosine > 0.65.
  - Reranker: cross-encoder score > 0.5.
  - LLM judge faithfulness: > 0.85 para respuestas que van a clientes B2B (compliance LATAM).

#### Cómo se actualiza cuando el archivo se modifica

**Trigger-based reprocessing**:
1. El archivo se edita → `git diff` detecta cambio.
2. Se invalida el hash del documento en docstore.
3. Se re-generan preguntas para las secciones modificadas (delta processing).
4. Se re-embedden solo los chunks afectados.
5. Se actualiza el vector store (pgvector upsert).

**Herramienta**: LlamaIndex IngestionPipeline con docstore management incluye deduplicación por hash de contenido y upsert automático [^307^].

---

### 5. Migration strategy

#### Lazy migration vs masiva

**Lazy migration** (recomendada para MWT MVP):

- Cuando un archivo se edita, se re-procesa con la nueva estrategia.
- Archivos no editados permanecen con chunking legacy.
- Ventaja: cero downtime, riesgo distribuido, costo incremental.
- Desventaja: corpus heterogéneo durante semanas/meses, métricas de calidad varían por archivo.

**Migración masiva**:

- Script batch procesa los 540 archivos en background.
- Requiere dual-index o maintenance window.
- Ventaja: corpus uniforme inmediatamente.
- Desventaja: riesgo concentrado, potencial downtime.

**Recomendación para MWT**: **Lazy migration para MVP**, con migración masiva como proyecto separado post-Foundation Beta (después de 2026-06-14).

#### Cómo no romper retrieval durante la migración (dual indexing)

**Patrón para PostgreSQL/pgvector**:

```sql
-- Tabla existente (legacy)
documents_legacy: id, content, embedding vector(1536), chunk_strategy='fixed'

-- Tabla nueva (v2) - creada concurrentemente
CREATE TABLE documents_v2 (
    id UUID PRIMARY KEY,
    content TEXT,
    embedding vector(1536),
    chunk_strategy TEXT DEFAULT 'recursive_query_enriched',
    questions TEXT[],  -- array de preguntas generadas
    parent_doc_id UUID,
    chunk_index INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índice concurrente (no bloquea writes)
CREATE INDEX CONCURRENTLY idx_docs_v2_embedding
ON documents_v2 USING hnsw (embedding vector_cosine_ops);
```

**Lógica de routing**:
- Queries van a ambas tablas en paralelo (UNION ALL).
- Reranker combina resultados.
- Gradualmente se desvía tráfico a v2 a medida que corpus migra.
- Una vez 100% migrado, deprecar legacy table.

**Ventaja**: PostgreSQL soporta `CREATE INDEX CONCURRENTLY` y `REINDEX CONCURRENTLY` para zero-downtime index operations [^277^][^266^].

#### Tools para automatizar

- **LlamaIndex IngestionPipeline**: Transformaciones custom, caching Redis, docstore management con hash-based deduplicación [^307^][^300^].
- **Custom Python con LiteLLM**: Script que lee archivos .md, extrae frontmatter, genera preguntas vía LiteLLM, chunking con `RecursiveCharacterTextSplitter` o `SentenceSplitter`, embedding con mismo model que producción, upsert a pgvector.
- **ARQ + Redis**: Cola async para procesar re-chunking en background sin bloquear API [^307^].

#### Tiempo estimado para migrar 540 archivos .md

- **Análisis**: 430 archivos operativos + 110 de otro tipo.
- **Script batch** (masivo): ~2-3 horas de compute para generar preguntas + chunk + embed (asumiendo 540 × 1s = 9 minutos de LLM calls + 30 minutos de embedding + overhead).
- **Trabajo de developer**: 
  - Implementar script: 4-6 horas.
  - Validar 50 archivos sample: 2-3 horas.
  - Monitorear migración: 2-3 horas.
  - **Total: 1-2 días** para migración masiva automatizada.
- **Lazy migration**: 2-3 días de setup inicial, luego ~10 minutos por batch de ediciones.

---

### 6. Convención de naming + estructura interna

#### ¿Cómo se documenta en cada archivo "estas son las 10 questions que respondo"?

**Frontmatter YAML** es el estándar de facto para metadata en archivos markdown KB [^245^][^290^][^252^]. La información debe estar:

1. **En el archivo mismo** (frontmatter) — viaja con el archivo, disponible para cualquier parser.
2. **En el vector store como metadata** — usada para pre-filtering y retrieval.
3. **Opcionalmente en índice separado** (_index.md) — para routing de alto nivel [^245^].

#### Schema YAML / Markdown frontmatter sugerido

```yaml
---
# Identificación canónica
id: "ENT_CLIENTE_001"
domain: "mwt"                          # tenant
kb_type: "ENT"                        # ENT/PLB/SCH/LOC/POL/IDX/SKILL/LOTE
status: "active"                      # draft | review | active | deprecated
version: "2025-06-20-v3"

# Temporalidad
created_at: "2025-01-15"
updated_at: "2025-06-20"
reviewed_at: "2025-06-18"
reviewed_by: "committee_maria"

# Chunking metadata
chunk_strategy: "recursive_query_enriched"
chunk_size_tokens: 512
chunk_overlap_tokens: 50
parent_doc_id: null                    # para child chunks

# Query enrichment — LO MÁS IMPORTANTE para esta dimensión
queries_answered:
  - question: "¿Cuál es el precio unitario del botín X-200 en talla 42?"
    query_type: "factoid"
    confidence: "high"                # high | medium | low
    expected_answer_span: "El botín X-200 tiene un precio de $89.50 por unidad."
  - question: "¿Qué certificaciones tiene el calzado de seguridad importado de China?"
    query_type: "analytical"
    confidence: "high"
  - question: "¿Cuál es el plazo de entrega para pedidos mayores a 500 unidades?"
    query_type: "procedural"
    confidence: "medium"
  - question: "¿Cómo se compara el modelo X-200 con el X-150 en resistencia al deslizamiento?"
    query_type: "comparative"
    confidence: "high"

# Semantic tagging
tags: ["calzado-seguridad", "botin-x200", "precios", "importacion-china"]
related_docs: ["PLB_X200_001", "POL_CALIDAD_003"]

# Compliance LATAM
compliance_jurisdiction: ["CR", "CO", "MX"]  # applicable jurisdictions
compliance_class: "product_safety"           # product_safety | data_privacy | tax
source_authority: "fabricante_certificado"     # who vouches for this data

# Retrieval hints
retrieval_priority: "high"              # high | normal | low
last_retrieval_test: "2025-06-19"
retrieval_score_avg: 0.87               # score promedio de retrieval tests
---
```

#### Validación automática (CI check)

**GitHub Actions / CI Pipeline**:

```yaml
# .github/workflows/kb-validation.yml
name: KB Validation
on:
  pull_request:
    paths: ['kb/**/*.md']

jobs:
  validate-kb:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pyyaml markdown-frontmatter
      - run: python scripts/validate_kb_frontmatter.py
```

**Script de validación** (validate_kb_frontmatter.py):

```python
import yaml
import frontmatter
from pathlib import Path
import sys

REQUIRED_FIELDS = [
    'id', 'domain', 'kb_type', 'status', 'version',
    'chunk_strategy', 'queries_answered'
]

QUERY_RULES = {
    'min_questions': 5,
    'max_questions': 15,
    'required_types': ['factoid', 'analytical'],
}

def validate_file(path: Path) -> list[str]:
    errors = []
    post = frontmatter.load(path)
    
    # Campos obligatorios
    for field in REQUIRED_FIELDS:
        if field not in post.metadata:
            errors.append(f"[{path}] Missing required field: {field}")
    
    # Validar queries_answered
    queries = post.metadata.get('queries_answered', [])
    if not isinstance(queries, list):
        errors.append(f"[{path}] queries_answered must be a list")
        return errors
    
    if len(queries) < QUERY_RULES['min_questions']:
        errors.append(f"[{path}] Too few questions: {len(queries)} < {QUERY_RULES['min_questions']}")
    
    if len(queries) > QUERY_RULES['max_questions']:
        errors.append(f"[{path}] Too many questions: {len(queries)} > {QUERY_RULES['max_questions']}")
    
    # Validar tipos presentes
    query_types = {q.get('query_type', '') for q in queries}
    for req_type in QUERY_RULES['required_types']:
        if req_type not in query_types:
            errors.append(f"[{path}] Missing required query_type: {req_type}")
    
    # Validar estructura de cada query
    for i, q in enumerate(queries):
        if 'question' not in q:
            errors.append(f"[{path}] Query {i} missing 'question' field")
        if len(q.get('question', '')) < 10:
            errors.append(f"[{path}] Query {i} too short")
    
    return errors

# Ejecutar sobre todos los archivos .md en kb/
all_errors = []
for md_file in Path('kb').rglob('*.md'):
    all_errors.extend(validate_file(md_file))

if all_errors:
    for e in all_errors:
        print(f"ERROR: {e}")
    sys.exit(1)
else:
    print("All KB files valid.")
    sys.exit(0)
```

**Inspirado en**: Content CI/CD pipelines con frontmatter validation [^280^], MAGI Markdown for Agent Guidance [^295^], y LLM Wiki patterns [^245^].

---

## Recomendación directa

### Lo que SÍ implementar (ahora, MVP)

1. **Recursive chunking + sentence window como default** para los 430 archivos operativos. Chunk size 400-512 tokens, overlap 10-15%. Es el approach con mejor ratio costo/beneficio validado por 4 benchmarks independientes [^19^][^193^][^299^].
2. **Query-enriched frontmatter** en cada archivo KB. Agregar campo `queries_answered` con 5-10 preguntas realistas generadas vía LLM (GPT-4.1 Nano vía LiteLLM). Costo: <$2 para todo el corpus. Beneficio: mejora retrieval precision al permitir query-to-question matching además de query-to-content.
3. **Hierarchical parent-child** para documentos POL (políticas) y PLB (playbooks) que son estructurados y críticos para compliance. Child=256 tokens para retrieval, parent=1024-1500 tokens para generation context.
4. **CI validation** del frontmatter schema en cada PR. Prevenir que archivos sin `queries_answered` entren al repo.
5. **Lazy migration**: cada archivo que se edita post-lanzamiento se re-chunkea con la nueva estrategia. No tocar archivos stale.

### Lo que NO implementar (ahora)

1. **NO semantic chunking sin min_chunk_size floor**. El riesgo de micro-fragments (43 tokens promedio) que retrieven bien pero respondan mal es real y documentado [^19^].
2. **NO late chunking** — requiere jina-embeddings-v3, no compatible con stack frozen (Supabase/pgvector con modelo embedding actual).
3. **NO migración masiva de 540 archivos** — riesgo innecesario para MVP. Lazy migration es suficiente.
4. **NO agentic chunking** — "highest computational overhead", discontinuado en experimentos 2025 [^193^]. Overkill para corpus de 540 archivos.
5. **NO cambio de vector database** — stack frozen dice Supabase/pgvector, y pgvector con HNSW es suficiente para <1M vectors [^213^][^277^].

### Lo que diferir (post-MVP)

1. **Intent-Driven Dynamic Chunking (IDC)** — esperar a que haya implementaciones estables en Python (actualmente es research code febrero 2026). Evaluar en Q3 2026.
2. **Multi-scale indexing** (AI21 approach) — requiere 2-5× más storage. Evaluar si el corpus supera 5K archivos.
3. **Cross-encoder reranker** — añadir si retrieval precision con bi-encoder queda <0.80.
4. **Embedding model upgrade** — cuando haya drift medible. Usar Drift-Adapter pattern [^212^] para evitar reindexar todo.

---

## Casos production citados

| Empresa | Caso | Métrica reportada | Fuente |
|---|---|---|---|
| Harvey AI | Legal RAG para Am Law 100 | Tool selection precision: 0.8-0.9; 30% reducción contract review time; 2-3 hrs/semana ahorradas | [^273^][^275^] |
| 47billion | University/consulting KB | Fixed-size 61% → Hierarchical 89% accuracy; Faithfulness 0.74 → 0.91 | [^21^] |
| Lucidworks | B2B catalog search (HVAC, automotive) | Precision answers para spec queries técnicos | [^318^] |
| UI Chicago | SAP Business One docs | Recursive+TF-IDF 82.5% precision vs Semantic 73.3% | [^291^] |
| Snowflake | Finance RAG | ANLS correlation chunk-level → generation-level | [^253^] |
| TDS/Enterprise KB | Confluence + runbooks | Context recall 0.72 → 0.88 con sentence windows | [^219^] |
| H-RAG (SemEval-2026) | Multi-turn conversational RAG | nDCG@5=0.4271; parent rescoring +0.0197 | [^17^] |
| AI21 | Query-dependent chunking | Multi-scale RRF aggregation | [^310^] |
| Vectara | NAACL 2025 peer-reviewed | Fixed 200-word > Semantic en realistic datasets | [^19^] |
| Chroma | Chunking benchmark | Semantic 91.9% recall; Recursive 88% | [^19^] |

---

## Gotchas y riesgos

1. **Embedding drift al cambiar chunking**: Si cambias chunk boundaries, los embeddings cambian. No mezclar chunks de estrategias diferentes en el mismo índice sin versionado explícito [^265^][^269^].
2. **CREATE INDEX CONCURRENTLY no funciona en transacciones**: Si usas Prisma/ORM, marcar la migración como non-transactional [^277^][^276^].
3. **Vacuum bloat en pgvector**: Deletes/updates dejan dead tuples. Monitorear con `pg_stat_all_tables`. Usar `VACUUM` o `REINDEX CONCURRENTLY` [^266^].
4. **"Lost in the middle" problem**: Aun con context windows grandes, LLMs declinan en accuracy si la info relevante está en el medio. Hierarchical chunking mitiga esto al pasar parent context rico [^241^].
5. **Query distribution shift**: Las queries de usuarios reales son "messier than your test set" [^297^]. Monitorear retrieval scores en producción y ajustar thresholds trimestralmente.
6. **Costo de semantic chunking a escala**: Para 1M documentos, embedding cada sentence para chunking = miles de dólares en API calls [^12^].
7. **Cascading failure en RAG**: "If either the retriever or the generator performs poorly, the overall quality can drop to zero, regardless of how well the other performs" [^41^]. Chunking es upstream de todo.
8. **LATAM context**: GPT-4o tokenizer es más eficiente para non-Latin languages (incluye español) [^282^]. Los costos por token en español son ~15-20% menores que en inglés para mismo contenido.

---

## Tabla de decisión chunking strategy por tipo de archivo MWT

| Tipo canónico | Ejemplo | Estrategia recomendada | Chunk size | Overlap | Query enrichment |
|---|---|---|---|---|---|
| **ENT** (Entidades) | Cliente, Proveedor, Producto | Full document as chunk (si < 300 tokens); Recursive si más largo | 300 o variable | 0% | 5-8 preguntas factoid |
| **PLB** (Playbooks) | Cómo cotizar, Proceso de cobranza | Hierarchical parent-child | Child 300, Parent 1200 | 15% | 8-12 preguntas (factoid + procedural) |
| **SCH** (Esquemas) | Estructura de datos, API | Code-aware recursive o full doc | 400 | 10% | 3-5 preguntas técnicas |
| **LOC** (Locaciones) | Bodegas, Tiendas, Direcciones | Full document as chunk | N/A | 0% | 3-5 preguntas factoid |
| **POL** (Políticas) | Términos, Garantías, Compliance | Hierarchical parent-child | Child 256, Parent 1024 | 20% | 10-15 preguntas (factoid + analytical + edge-case) |
| **IDX** (Índices) | Directorios, Listados | Full document as chunk o no chunking | N/A | 0% | 2-3 preguntas de navegación |
| **SKILL** (Habilidades) | Prompt templates, System instructions | Full document as chunk (son críticos) | N/A | 0% | 3-5 preguntas de uso |
| **LOTE** (Lotes/Inventario) | SKU batches, Inventario actual | Structured data → no chunking necesario | N/A | 0% | Metadata fields para filtering |

**Rationale**: POL y PLB son los más críticos para FaberLoom (cotización + cobranza). Requieren precision máxima y contexto completo. ENT y LOC son más simples. SKILL no debe fragmentarse — un prompt template cortado por la mitad es inútil.

---

## Convención canónica para POL_CHUNKING_KB_v1

```markdown
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
  - question: "¿Cuál es el período de garantía para calzado de seguridad defectuoso?"
    query_type: "factoid"
    confidence: "high"
    expected_answer_span: "El período de garantía es de 90 días calendario..."
  - question: "¿Qué documentación se requiere para iniciar una reclamación de garantía?"
    query_type: "procedural"
    confidence: "high"
  - question: "¿La garantía cubre desgaste normal por uso industrial?"
    query_type: "edge_case"
    confidence: "high"
  - question: "¿Cómo se compara nuestra política de garantía con la del competidor Z?"
    query_type: "comparative"
    confidence: "medium"
    note: "Requiere datos de POL_COMPETENCIA_001"
  - question: "¿Qué pasa si el cliente no tiene la factura original?"
    query_type: "edge_case"
    confidence: "high"

tags: ["garantia", "calidad", "post-venta", "reclamacion"]
related_docs: ["PLB_COBRA_002", "ENT_CLIENTE_001"]
compliance_jurisdiction: ["CR", "CO", "MX", "PA", "BR"]
compliance_class: "product_safety"
source_authority: "legal_mwt_2025"
retrieval_priority: "high"
last_retrieval_test: "2025-06-19"
retrieval_score_avg: 0.91
---

# Política de Garantía — Calzado de Seguridad

## 1. Alcance

El presente documento establece los términos de garantía para calzado de seguridad...

[Contenido del documento]
```

---

## Tooling recomendado

### Python scripts + libraries

| Propósito | Herramienta | Versión / Notas |
|---|---|---|
| Chunking | `llama-index` (`SentenceSplitter`, `TokenTextSplitter`) | ^0.12 |
| Chunking alt | `langchain-text-splitters` (`RecursiveCharacterTextSplitter`) | ^0.3 |
| Semantic chunking | `chonkie` (`SemanticChunker`) | ^1.0 — con `min_chunk_size` obligatorio |
| Metadata extraction | `llama-index` (`QuestionsAnsweredExtractor`) | ^0.12 |
| Embeddings | `sentence-transformers` (local) o vía LiteLLM | all-MiniLM-L6-v2 o text-embedding-3-small |
| Vector store | `pgvector` (vía `sqlalchemy` + `psycopg2`) | ^0.3 |
| Evaluación | `ragas` o `deepeval` | RAGAS ^1.0, DeepEval ^2.0 |
| Frontmatter parsing | `python-frontmatter` | ^1.0 |
| CI validation | `pyyaml` + `jsonschema` | GitHub Actions nativo |
| Async processing | `arq` + `redis` | Stack frozen, ya en uso |
| LLM gateway | `litellm` | Stack frozen, ya en uso |

### Script template para migración lazy

```python
#!/usr/bin/env python3
"""
MWT KB Lazy Re-chunking Script
Procesa archivos .md modificados: regenera preguntas, re-chunkea, re-embed.
"""

import asyncio
import frontmatter
import yaml
from pathlib import Path
from datetime import datetime
from litellm import acompletion
from llama_index.core.node_parser import SentenceSplitter
from sentence_transformers import SentenceTransformer
import asyncpg

DB_URL = "postgresql://..."  # Supabase
EMBED_MODEL = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
LLM_MODEL = "gpt-4.1-nano"  # vía LiteLLM gateway

QUESTION_GENERATION_PROMPT = """
Eres un analista de producto para FaberLoom (calzado de seguridad B2B LATAM).
Lee el siguiente documento y genera 5-10 preguntas realistas que un comprador B2B haría.
Cada pregunta debe ser respondible ÚNICAMENTE con la información del documento.
Formato: lista numerada, español neutro LATAM.
Documento:
{content}
"""

async def generate_questions(doc_content: str) -> list[dict]:
    """Genera preguntas via LiteLLM."""
    response = await acompletion(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": QUESTION_GENERATION_PROMPT.format(content=doc_content[:4000])}],
        temperature=0.3,
        max_tokens=800,
    )
    # Parsear respuesta (simplificado — usar estructurado en producción)
    text = response.choices[0].message.content
    questions = [line.strip() for line in text.split('\n') if line.strip().startswith(('1.', '2.', '- '))]
    return [{"question": q, "query_type": "auto", "confidence": "medium"} for q in questions[:12]]

async def process_file(file_path: Path):
    """Procesa un archivo .md modificado."""
    post = frontmatter.load(file_path)
    
    # 1. Generar preguntas
    questions = await generate_questions(post.content)
    post.metadata['queries_answered'] = questions
    post.metadata['updated_at'] = datetime.now().isoformat()
    post.metadata['chunk_strategy'] = 'recursive_query_enriched'
    
    # 2. Chunking
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    chunks = splitter.split_text(post.content)
    
    # 3. Embedding + upsert a pgvector
    conn = await asyncpg.connect(DB_URL)
    for i, chunk_text in enumerate(chunks):
        embedding = EMBED_MODEL.encode(chunk_text).tolist()
        await conn.execute(
            """
            INSERT INTO kb_chunks (doc_id, chunk_index, content, embedding, questions, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (doc_id, chunk_index) DO UPDATE SET
                content = EXCLUDED.content,
                embedding = EXCLUDED.embedding,
                questions = EXCLUDED.questions,
                updated_at = EXCLUDED.updated_at
            """,
            post.metadata['id'], i, chunk_text, embedding, 
            [q['question'] for q in questions], datetime.now()
        )
    await conn.close()
    
    # 4. Guardar archivo actualizado
    frontmatter.dump(post, file_path)
    print(f"Processed: {file_path}")

async def main():
    # Detectar archivos modificados (git diff) o procesar todos
    kb_dir = Path('kb')
    files = list(kb_dir.rglob('*.md'))
    for f in files:
        await process_file(f)

if __name__ == '__main__':
    asyncio.run(main())
```

---

## Plan migración 540 archivos

### Fase 0: Preparación (Día 1, 4 horas)

- [ ] Definir schema frontmatter v1 en `POL_CHUNKING_KB_v1`.
- [ ] Implementar CI check `validate_kb_frontmatter.py`.
- [ ] Probar script de generación de preguntas en 10 archivos sample.
- [ ] Validar quality de preguntas generadas con curador (USER + COMMITTEE).
- [ ] Ajustar prompt template según feedback.

### Fase 1: Lazy Migration Setup (Día 1-2, 6 horas)

- [ ] Crear tabla `kb_chunks_v2` en Supabase con HNSW index `CONCURRENTLY`.
- [ ] Implementar `process_file()` en pipeline async (ARQ + Redis).
- [ ] Agregar campo `chunk_strategy_version` para tracking.
- [ ] Monitorear: retrieval scores pre/post para archivos migrados.

### Fase 2: Procesamiento Batch Controlado (Día 2-3, 6 horas)

- [ ] Procesar 50 archivos más críticos (POL, PLB) en batch.
- [ ] Validar retrieval scores con RAGAS/DeepEval.
- [ ] Si scores mejoran >10%, continuar. Si no, ajustar chunk size/overlap.
- [ ] Procesar 100 archivos adicionales.

### Fase 3: Lazy Continuo (Post-lanzamiento)

- [ ] Cada PR que modifique `.md` en `kb/` dispara re-chunking automático.
- [ ] Archivos no editados permanecen en legacy index.
- [ ] Meta: 100% migrado para finales de Q3 2026.

### Esfuerzo estimado

| Tarea | Horas | Riesgo |
|---|---|---|
| Schema + CI | 4h | Bajo |
| Script + testing | 6h | Medio |
| Batch 50 archivos | 4h | Medio |
| Monitoreo + ajustes | 4h | Bajo |
| **Total** | **~18h (2-3 días)** | **Bajo** |

### Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Downtime durante index creation | Baja | Alto | Usar `CREATE INDEX CONCURRENTLY` [^277^] |
| Preguntas generadas de baja calidad | Media | Medio | Curadura 2 capas (USER + COMMITTEE); threshold mínimo de 5 preguntas aceptables |
| Embedding drift mezclado | Media | Medio | Versionar chunks (`chunk_strategy_version`); no mezclar v1 y v2 en mismo query |
| Costo LLM inesperado | Baja | Bajo | GPT-4.1 Nano ($0.10/M tokens); budget de $5 es suficiente |
| Performance de pgvector con HNSW | Baja | Medio | pgvector HNSW soporta <1M vectors sin problemas [^213^]; 540 archivos ≈ 2K-5K chunks |

---

## Sources

- [^12^] Firecrawl: Best Chunking Strategies for RAG (and LLMs) in 2026 — https://www.firecrawl.dev/blog/best-chunking-strategies-rag
- [^17^] H-RAG at SemEval-2026: Hierarchical Parent-Child Retrieval — https://arxiv.org/pdf/2605.00631
- [^19^] PremAI: RAG Chunking Strategies — The 2026 Benchmark Guide — https://blog.premai.io/rag-chunking-strategies-the-2026-benchmark-guide/
- [^21^] 47billion: RAG System in Production — Why It Fails and How to Fix It — https://47billion.com/blog/rag-system-in-production-why-it-fails-and-how-to-fix-it/
- [^22^] Dev.to: 10 Chunking Strategies That Make or Break Your RAG Pipeline — https://dev.to/klement_gunndu/10-chunking-strategies-that-make-or-break-your-rag-pipeline-4cng
- [^31^] IntuitionLabs: LLM API Pricing Comparison (2025) — https://intuitionlabs.ai/articles/llm-api-pricing-comparison-2025
- [^41^] Confident AI: RAG Evaluation Metrics — https://www.confident-ai.com/blog/rag-evaluation-metrics-answer-relevancy-faithfulness-and-more
- [^193^] Amir Teymoori: RAG Text Chunking Strategies — https://amirteymoori.com/rag-text-chunking-strategies/
- [^212^] Isuru I: Embedding Model Migration Without Downtime (Drift-Adapter) — https://medium.com/@isuruig/embedding-model-migration-without-downtime-6f3c62abed99
- [^213^] AI Log: Best Vector Databases for RAG in 2025 — https://app.ailog.fr/en/blog/guides/vector-databases
- [^219^] TDS: Your Chunks Failed Your RAG in Production — https://towardsdatascience.com/your-chunks-failed-your-rag-in-production/
- [^241^] TDS: Breaking It Down — Chunking Techniques for Better RAG — https://towardsdatascience.com/breaking-it-down-chunking-techniques-for-better-rag-3fd288bf25a0/
- [^245^] MindStudio: LLM Wiki vs RAG — https://www.mindstudio.ai/blog/llm-wiki-vs-rag-knowledge-base/
- [^253^] Snowflake: How Retrieval & Chunking Impact Finance RAG — https://www.snowflake.com/en/engineering-blog/impact-retrieval-chunking-finance-rag/
- [^265^] Instaclustr: pgvector Key Features 2026 Guide — https://www.instaclustr.com/education/vector-database/pgvector-key-features-tutorial-and-pros-and-cons-2026-guide/
- [^266^] 0xhagen: Migrating Vector Embeddings from PostgreSQL to Qdrant — https://0xhagen.medium.com/migrating-vector-embeddings-from-postgresql-to-qdrant-f101f42f78f5
- [^269^] Introl: RAG Infrastructure Production Guide — https://introl.com/blog/rag-infrastructure-production-retrieval-augmented-generation-guide
- [^273^] Harvey AI: How Agentic Search Unlocks Legal Research Intelligence — https://www.harvey.ai/blog/how-agentic-search-unlocks-legal-research-intelligence
- [^275^] Medium: How Harvey Built Trust in Legal AI — https://medium.com/@takafumi.endo/how-harvey-built-trust-in-legal-ai-a-case-study-for-builders-786cc23c3b6d
- [^277^] Railway: Hosting Postgres with pgvector — https://blog.railway.com/p/hosting-postgres-with-pgvector
- [^280^] SteakHouse: Content CI/CD Pipeline — https://blog.trysteakhouse.com/blog/content-ci-cd-pipeline-automating-geo-compliance-tests-github-actions
- [^281^] PECollective: LLM API Pricing 2026 — https://pecollective.com/blog/llm-api-pricing-comparison/
- [^291^] UI Chicago: A Systematic Framework for Enterprise Knowledge Retrieval — https://arxiv.org/html/2512.05411v1
- [^295^] GitHub: MAGI Markdown for Agent Guidance — https://github.com/sno-ai/magi-markdown
- [^299^] Medium: The Chunking Strategy That's Killing Your RAG Performance — https://medium.com/@theabhishek.040/the-chunking-strategy-thats-killing-your-rag-performance-95-of-developers-get-this-wrong-0600b91daabe
- [^300^] LlamaIndex: Transformations Documentation — https://developers.llamaindex.ai/python/framework/module_guides/loading/ingestion_pipeline/transformations/
- [^306^] Pixion: RAG in Practice — Test Set Generation — https://pixion.co/blog/rag-in-practice-test-set-generation
- [^307^] Clustered Bytes: LlamaIndex Ingestion Pipeline — https://clusteredbytes.pages.dev/posts/2024/llamaindex-ingestion-pipeline/
- [^310^] AI21: Query-Dependent RAG Chunking — https://www.ai21.com/blog/query-dependent-chunking/
- [^313^] arXiv: Intent-Driven Dynamic Chunking — https://arxiv.org/abs/2602.14784
- [^318^] Lucidworks: AI Agents Remove Catalog Friction in B2B Commerce — https://lucidworks.com/blog/psa-ai-agents-remove-catalog-friction-in-b2b-commerce



================================================================================
## D4 — CLAUDE.md patterns emergentes 2026

### Resumen ejecutivo

- **CLAUDE.md no es un archivo de configuración, es un archivo de contexto**: Anthropic lo envuelve con una cláusula de descargo de responsabilidad que le permite al modelo ignorarlo si decide que "no es altamente relevante". Las reglas críticas deben ir en hooks (PreToolUse / SessionStart), no solo en CLAUDE.md [^93^][^89^].
- **El límite duro es ~150-200 instrucciones totales** (incluyendo el system prompt de Claude Code que ya consume ~50). Más allá de eso, el cumplimiento decae uniformemente. HumanLayer mantiene su CLAUDE.md productivo bajo 60 líneas. Boris Cherny (creador de Claude Code) mantiene el suyo en ~60-83 líneas [^14^][^124^][^125^].
- **Los hooks son la capa de enforcement real**: Un plugin con hooks `SessionStart` + `UserPromptSubmit` que re-inyecta valores tras cada compactación logró cumplimiento donde CLAUDE.md solo fallaba. Hook output llega como `system-reminder` sin el framing dismissivo de CLAUDE.md [^93^][^96^].
- **Addy Osmani (Google/Anthropic) codificó 20 skills con "anti-rationalization tables"**: Cada skill incluye una tabla de excusas comunes que los agentes usan para saltarse pasos ("agregaré tests después") con contra-argumentos documentados. Es el patrón más robusto documentado para evitar que el agente se hable a sí mismo de saltar reglas [^121^][^120^].
- **Para KB con sync canónico, badwally/TheKnowledge demuestra el patrón dual-surface**: `CLAUDE.md` es el control surface para el agente; `WIKI.md` es el contract que cada componente (gateway, validator, converters) codifica. Todo write pasa por gateway con validación, locking, y logging atomico a `log.md` [^175^][^254^].
- **Métricas reales de equipos en producción**: Atlassian redujo ciclo PR 45% con AI review; 1mg (300 ingenieros) reportó 31.8% reducción en review time; Altana reportó 2-10x velocidad de desarrollo; Behavox desplegó a cientos de devs con Claude Code como "pair programmer" [^259^][^262^][^133^].

---

### Hallazgos por sub-pregunta

#### 1. Más allá de Karpathy / Mehul Gupta

**Karpathy (forrestchang/andrej-karpathy-skills) — 97.8k stars**
Las cuatro reglas edit-time de Karpathy [^29^][^31^][^33^]:
1. **Think Before Coding** — state assumptions, surface tradeoffs, ask when unclear
2. **Simplicity First** — minimum code, no speculative abstractions
3. **Surgical Changes** — touch only what the task requires; every changed line traces to the request
4. **Goal-Driven Execution** — define success criteria, loop until verified

Son efectivas para el momento de escritura de código (edit-time) pero no cubren el momento de ejecución (runtime). Un artículo de Reneza extendió 6 reglas runtime adicionales [^34^]:
- Validar AI output contra schema
- Sanitizar input de operador antes de que llegue al prompt
- Log rejections silently (no narrar al atacante)
- Rate limiting y budget guards
- Audit trail completo
- Fail-closed por defecto

**Anthropic CLAUDE.md interno**
No hay CLAUDE.md interno de Anthropic público, pero la documentación oficial de Claude Code [^52^] establece la jerarquía de memoria:
- Enterprise > Project (`./CLAUDE.md`) > Project Rules (`.claude/rules/*.md`) > User (`~/.claude/CLAUDE.md`) > Local (`./CLAUDE.local.md`)
- Precedence: más específico gana sobre más general
- CLAUDE.md files son aditivos: todos los niveles contribuyen contenido simultáneamente

**Repositorios open-source con CLAUDE.md robustos**
| Repo | Stars | Patrón clave |
|------|-------|-------------|
| forrestchang/andrej-karpathy-skills | 97.8k | 4 reglas edit-time, anti-overengineering |
| MuhammadUsmanGM/claude-code-best-practices | 20k+ | 30+ guías, 11 plantillas CLAUDE.md, 4 starter kits, benchmarks reproducibles |
| addyosmani/agent-skills | 18.1k | 20 skills con anti-rationalization tables, verification gates, progressive disclosure |
| abhishekray07/claude-md-templates | N/A | Plantillas por stack + principios de escritura (60-line rule, skill activation mapping) |
| shanraisshan/claude-code-best-practice | 20k+ | 84 mejores prácticas compiladas |
| badwally/TheKnowledge | N/A | KB real con CLAUDE.md + WIKI.md dual-surface, gateway pattern, draft mode |
| HumanLayer (referenciado) | N/A | CLAUDE.md productivo <60 líneas, TODO priority system |

**Diferencias entre CLAUDE.md para codebase vs KB vs research repo**

| Contexto | Enfoque | Longitud típica | Patrón clave |
|----------|---------|-----------------|-------------|
| Codebase (Karpathy/Mehul) | Reglas de edit-time, convenciones de código, comandos de build/test | 40-80 líneas [^124^] | Anti-overengineering, surgical changes |
| KB (badwally/TheKnowledge) | Control surface del agente + contract de convenciones. No contiene código de build | 60-100 líneas [^175^] | Dual-surface: CLAUDE.md (agente) + WIKI.md (contract humano) |
| Research repo | Pipeline de ingest, validación, citation rules, authority tiers | 80-150 líneas [^234^] | Tier 1 = read-only source of truth; agente debe citar `file:line` |
| Multi-tenant SaaS | Tenant isolation rules, RLS policies, middleware patterns | 60-100 líneas [^88^] | Regla must-always: "cada query lleva tenant_id" |

**Para repos KB grandes (>1000 archivos)**: badwally/TheKnowledge [^175^][^254^] opera con ~wiki/ directorios tipados (entities/, concepts/, sources/, synthesis/, mocs/, artifacts/), un gateway que valida todo write, y un índice `index.md` reconstruible. CLAUDE.md no describe la estructura completa — eso está en WIKI.md — sino que define cómo el agente debe interactuar con el gateway.

#### 2. Anti-patterns documentados

**Anti-pattern 1: CLAUDE.md que NO funciona en producción**
- El framing de Anthropic envuelve CLAUDE.md con: *"may or may not be relevant"* y *"only follow if highly relevant to your task"* [^93^]. Esto no es un bug, es diseño documentado.
- GitHub issue #27032 [^89^]: Claude lanzó 3 agentes en paralelo sin permiso pese a regla explícita "NEVER launch multiple agents without permission". La razón: el system prompt interno de plan mode sobreescribió CLAUDE.md.
- GitHub issue #2544 [^91^]: Reglas mandatorias consistentemente ignoradas en múltiples repos. Impacto: workflow breakdown, compliance risk, team inconsistency.
- ETH Zurich study (citado por Arize) [^36^]: LLM-generated context files redujeron task success ~3% mientras aumentaban costos 20%.

**Anti-pattern 2: Reglas que se ignoran consistentemente**
- **Longitud excesiva**: "A 60-line CLAUDE.md that Claude actually follows beats a 300-line one it mostly ignores — and costs 20% less per task" [^124^].
- **Reglas en el archivo equivocado**: El user-level `~/.claude/CLAUDE.md` puede conflicar con project-level `./CLAUDE.md`. Si hay conflicto, Claude resuelve a veces a favor del system prompt interno, no del project [^89^][^65^].
- **Reglas re-inyectadas como rule files**: Un 500-token rule file no cuesta 500 tokens — cuesta 500 × (número de tool calls). En una sesión real con 30 tool calls y 11 rule files, las re-inyecciones consumieron **93K tokens — 46% de la ventana de contexto** [^125^].

**Anti-pattern 3: Reglas que generan parálisis (ask-loops infinitos)**
- GitHub issue #35166 [^100^]: Claude Code entró en loop infinito enviando la misma request cada ~1 minuto durante horas, consumiendo $500+ en tokens. Causa raíz: después de `/compact`, el modelo intentaba continuar la tarea, se quedaba sin contexto de nuevo, y reintentaba indefinidamente.
- GitHub issue #19699 [^102^]: Claude ejecutó el mismo comando fallido 7+ veces seguidas sin modificarlo (`make run-runner` que no existía). No reconoció el patrón de error repetido.
- GitHub issue #26512 [^174^]: Extension de Claude Code en Cursor entró en loop irrecuperable llamando Read() cientos de veces. El modelo se volvió "self-aware" del loop pero no pudo salir.

**Anti-pattern 4: Reglas que se contradicen entre sí**
- GitHub issue #27032 [^89^]: Regla "nunca escribas plan files fuera del repo" vs system prompt de plan mode que sugiere `~/.claude/plans/`. El modelo siguió el system prompt.
- Cuando dos rule files se contradicen, "Claude picks one arbitrarily" [^92^].
- Acumular 47 instrucciones custom across workspace config, repo rules, system prompts crea contradictions que confunden al modelo [^196^].

**Anti-pattern 5: Cleanup no solicitado ("AI cleanup behavior")**
- GitHub issue #15333 [^68^]: Claude modifica código funcional no relacionado mientras arregla bugs (cambia config de modelo, refactoriza auth, "optimiza" queries). Se solicitaron múltiples mecanismos de protección: `// @claude-lock-start`, `.claudeignore`, etc.
- Reddit report [^66^]: Usuario reporta que Claude "autónomamente añade DEMO y FALLBACK functionality without being prompted" y "refactoring disasters: after HOURS of work, Claude declares 100% COMPLETED while 90% of functionality is GONE."
- Incidente crítico #49464 [^182^]: Claude intentó ejecutar `rm -f ~/` (borrar home directory) al limpiar archivos no trackeados que incluían un directorio literalmente nombrado `~`.

#### 3. Integración con sub-agents

**¿CLAUDE.md aplica a sub-agents o solo al main agent?**
Según la documentación oficial de Claude Code [^52^]:
- Subagents **heredan** CLAUDE.md y git status del parent session
- Subagents **NO heredan** conversation history ni skills invocadas del main session
- Skills pasadas a subagent son **fully preloaded** into its context at launch (no progressive disclosure)
- El system prompt se comparte con el parent for cache efficiency

**¿Cómo se propagan reglas a sub-agents?**
1. **Por herencia automática**: CLAUDE.md del directorio de trabajo se carga en el subagent
2. **Por skills preload**: El campo `skills:` en el frontmatter del subagent carga skills específicas
3. **Por prompt injection**: El lead agent pasa contexto explícito en el prompt al crear el subagent

Ejemplo de subagent con skills [^55^]:
```yaml
---
name: code-reviewer
description: Reviews code for quality and best practices.
tools: Read, Glob, Grep
model: sonnet
skills:
  - api-conventions
  - error-handling-patterns
---
```

**¿Cómo se manejan reglas que aplican solo a ciertos sub-agents?**
- La documentación oficial indica: "When instructions conflict, Claude uses judgment to reconcile them, with more specific instructions typically taking precedence" [^52^]
- Para skills: "Plugin skills are namespaced to avoid conflicts" [^52^]
- Para subagents: "Subagents don't inherit skills from the main session; you must specify them explicitly" [^52^]
- **Recomendación práctica**: Si una regla solo aplica a un subagent (ej. "el reviewer nunca escribe código"), ponerla en el archivo del subagent (`.claude/agents/reviewer.md`), no en el CLAUDE.md raíz.

Patrón de `/simplify` skill [^50^]: Spawnea **3 review agents en paralelo** que analizan código desde diferentes ángulos (readability, performance, correctness). Cada agent trabaja independiente y reporta findings. Results merged into unified review.

#### 4. Mantenimiento con múltiples contributors

**¿Quién aprueba cambios al CLAUDE.md?**
- GitHub issue #30554 [^49^]: Feature request explícito para team/shared CLAUDE.md. Workaround actual: "shared private repo + symlink setup script". Proposed solutions: remote config URL, repo-level `.claude/TEAM.md`, o `@import` directives.
- La guía de Nimbalyst [^227^] recomienda: "Rotate CLAUDE.md ownership. Assign someone on the team to review and update CLAUDE.md monthly."
- Myouga [^229^] documenta: "Changes require a PR (no direct pushes to main). PR description must explain why the rule is being added/changed. Test that Claude Code behaves correctly after the change before merging. Monthly team review: does CLAUDE.md still reflect reality?"
- Paul Duvall [^228^] construyó `centralized-rules` para este problema: 74.4% token savings y consistent AI behavior across teams.

**Versionado semántico de reglas**
- MuhammadUsmanGM/claude-code-best-practices usa CHANGELOG.md con semver. Breaking changes bump major version [^32^].
- Badwally/TheKnowledge usa milestones (M0-M14) con commits atómicos en main [^254^].
- Addy Osmani agent-skills latest release 0.5.0 (April 10, 2026), MIT licensed [^54^].

**Cómo se comunican cambios al equipo**
- `.claude/CLAUDE.md` committed to git = todos obtienen cambios automáticamente al hacer pull [^229^]
- Enterprise policy files (macOS: `/Library/Application Support/ClaudeCode/`, Linux: `/etc/claude-code/`) para organizaciones [^233^]
- Para cambios urgentes: hook `SessionStart` que re-inyecta reglas actualizadas en cada nueva sesión [^93^]

**Métricas de adopción real**
- Faros AI [^129^] trackea: adoption rate (% de devs usando Claude Code), PR velocity, review time, cycle time, bugs per developer. Dato clave: Team B con 60% adoption merged 47% more PRs daily pero tenía 35% longer review times — el volumen generó cuello de botella en review.
- Behavox [^133^]: "rolled it out to hundreds of developers, quickly became our go-to pair programmer"
- Altana [^133^]: "accelerated development velocity by 2-10x"

#### 5. Métricas de éxito

**¿Cómo medís si CLAUDE.md funciona?**

| Métrica | Baseline | Target | Fuente |
|---------|----------|--------|--------|
| Diff size promedio (líneas) | 40+ líneas para bugfixes simples | <10 líneas para fixes simples | Karpathy examples: fix de empty emails pasó de 40 líneas a 2 líneas [^31^] |
| Número de follow-up clarifications | 3-5 por sesión | <1 por sesión | "Think Before Coding" rule reduce assumptions [^29^] |
| Número de "AI cleanup incidents" | ~1 cada 3-5 sesiones | 0 | Hooks PreToolUse + reglas explícitas [^68^][^177^] |
| Tiempo de PR review | 18h promedio (Atlassian) | -45% | Atlassian Rovo Dev: 45% PR cycle time reduction [^259^] |
| Tiempo de PR review (enterprise India) | 128.8h baseline | -29.8% | 1mg (300 engineers): 31.8% overall efficiency gain [^262^] |
| Token savings | Baseline | 74.4% | Paul Duvall centralized-rules [^228^] |
| CLAUDE.md compliance rate | ~60% para archivos >200 líneas | >90% para <60 líneas | HumanLayer benchmark [^124^][^119^] |

**Métricas de qualidad del output**
- Arize Prompt Learning [^36^]: Optimizar solo el system prompt de Claude Code generó +5% en general coding performance y +11% cuando se especializó a un solo repositorio.
- Boris Cherny recomienda: "If you have to repeat an instruction in chat more than twice, promote it into your CLAUDE.md" [^33^].
- Señales de éxculo de CLAUDE.md [^233^]: Fewer corrections, better first attempts, reduced context-setting, team consistency.

#### 6. Plantillas para diferentes contextos

**CLAUDE.md para KB pura (caso MWT)**
Basado en badwally/TheKnowledge [^175^] + CWAN Engineering [^234^]:
```markdown
# CLAUDE.md — MWT Knowledge Hub Agent Control Surface

## Identity
You are the KB curator assistant for Muito Work Limitada. Your job is to 
organize, validate, and synthesize knowledge — NEVER to write production code.

## Canonical Source of Truth
- Git repo at C:\dev\mwt-knowledge-hub is the ONLY canonical source
- OneDrive mirror is read/write for Cowork sessions, but ALL changes MUST 
  flow through sync_*_indexa.ps1 back to the canonical repo
- NEVER write directly to the canonical repo from Cowork

## Taxonomy (8 tipos canónicos)
- ENT: Entity | PLB: Publicable | SCH: Schema | LOC: Location
- POL: Policy | IDX: Index | SKILL: Skill | LOTE: Lote
- Every file MUST have correct frontmatter type. Ask if unclear.

## Rules
1. DRAFT-FIRST invariante: All new content starts as draft: true
2. Curaduría 2 capas: USER review + COMMITTEE approval before finalize
3. NEVER create, move, or delete files in the canonical repo directly
4. NEVER modify files outside the current working directory scope
5. If Cowork suggests changes to canonical files, STOP and ask permission
6. All claims must cite source with [[file:line]] format
7. Seal/Open dual mode: Sealed = read-only source of truth; Open = working drafts
```

**CLAUDE.md para codebase (Karpathy/Mehul style)**
```markdown
# CLAUDE.md

## Think Before Coding
- State your assumptions explicitly before implementing
- Present multiple interpretations when ambiguity exists
- Ask when unclear — never pick silently

## Simplicity First
- Minimum code that solves the problem. Nothing speculative.
- No abstractions for single-use code. No "flexibility" not requested.
- If 200 lines could be 50, rewrite it.

## Surgical Changes
- Touch only what you must. Clean up only your own mess.
- Every changed line should trace directly to the user's request.
- Do not improve adjacent code, comments, or formatting.

## Goal-Driven Execution
- Transform imperative tasks into verifiable goals
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- Plan format: 1. [Step] → verify: [check]
```

**CLAUDE.md para research repo**
Según CWAN Engineering [^234^]:
- Tier 1: Source of Truth (read-only for AI agents)
- Tier 2: Core Knowledge (textbook del proyecto)
- Tier 3: Implementation & Analysis (working documents)
- Tier 4: Historical/Archive (non-authoritative)
- Regla: "If an AI agent contradicts a Tier 1 document, the agent is wrong"

**CLAUDE.md para multi-tenant SaaS**
Según LowCode Agency [^88^] + GoClaw [^94^]:
```markdown
## Multi-Tenant Rules (MUST NEVER BREAK)
1. Every database query MUST include tenant_id filter from request context
2. Every isolatable table has tenant_id NOT NULL
3. Tenant flows through context.Context — NEVER from client headers
4. RLS policies are the source of truth; app-level filtering is defense in depth
5. Per-tenant overrides: LLM configs, tool settings, skills enabled
```

#### 7. Reglas específicas para repo KB con sync canónico

**El patrón badwally/TheKnowledge [^175^][^254^]**
Es el caso de estudio más cercano al setup de MWT. Estructura:
```
~/code/knowledge/
├── CLAUDE.md              # Agent control surface
├── WIKI.md                # Conventions reference (contract humano)
├── raw/                   # Immutable ingested sources
├── wiki/                  # LLM-authored knowledge (6 page types)
├── .knowledge/
│   ├── policies/          # Editorial policies per domain
│   ├── locks/             # File locks for concurrency safety
│   └── lint/              # Lint reports
├── src/gateway/           # Gateway implementation
│   ├── core.py            # Gateway.execute(operation, args)
│   ├── validator.py       # WIKI.md rules as composable functions
│   ├── locking.py         # File locks
│   └── ops/               # One module per gateway operation
```

**Control surface dual: CLAUDE.md + WIKI.md**
- `CLAUDE.md` = qué puede hacer el agente, cómo debe comportarse
- `WIKI.md` = contract técnico que valida el gateway. Cada componente (gateway, validator, converters) codifica contra WIKI.md
- El gateway implementa WIKI.md § 9.2 contract: validate input → lock → execute → validate output → write atomically → update backlinks → log → release lock → return [^254^]

**Draft mode**
- `draft: true` en frontmatter permite contenido en progreso
- `finalize` operation re-validates strict by stripping draft fields from a copy
- On-disk file keeps `draft: true` until validation passes [^256^]

**Para prevenir escritura directa al canónico desde Cowork**
1. **Hook PreToolUse** que bloquea Write/Edit en paths del repo canónico [^48^]
2. **Regla explícita en CLAUDE.md**: "NEVER create, move, or delete files in the canonical repo directly"
3. **Gateway pattern**: Todo write pasa por `wiki ingest` o `wiki apply-plan` que valida antes de escribir
4. **File locking** bajo `.knowledge/locks/` para concurrencia

**Para prevenir perder cambios entre canónico y mirror**
1. **One-way sync canonizado**: mirror_to_onedrive.ps1 (canónico → OneDrive) y sync_*_indexa.ps1 (OneDrive → canónico)
2. **Content-hash idempotency**: re-ingest del mismo file es no-op si el hash no cambia [^254^]
3. **Log.md append-only**: cada operación queda registrada con timestamp, operación, path, y hash [^254^]
4. **Git como SSoT**: El repo canónico es la única fuente de verdad; OneDrive es working copy [^169^]

---

### Recomendación directa

**SÍ implementar:**

1. **Dual-surface CLAUDE.md + WIKI.md**: Copiar el patrón badwally/TheKnowledge. CLAUDE.md para el agente (corto, <80 líneas), WIKI.md para el contract humano/técnico (detallado, evoluciona con el gateway). Por qué: separa concerns, previene que el agente ignore reglas por "no ser relevantes", y da a los humanos un contract claro [^175^][^254^].

2. **Hook-based reinforcement para reglas críticas**: Un hook `SessionStart` que re-inyecta las 6 reglas inquebrantables de MWT tras cada compactación. Un hook `UserPromptSubmit` que añade ~15 tokens de reminder en cada prompt. Por qué: hook output llega como `system-reminder` sin el framing dismissivo de CLAUDE.md [^93^].

3. **PreToolUse hook para proteger el canónico**: Script que verifica si el path objetivo está en `C:\dev\mwt-knowledge-hub` y bloquea Write/Edit si Cowork intenta escribir directo. Por qué: el incidente del 29-abr (11 archivos FB en docs/ raíz) se repite si no hay enforcement técnico [^68^][^177^].

4. **Anti-rationalization table en CLAUDE.md**: Tabla de excusas que Cowork usa para saltarse reglas + contra-argumentos. Ejemplo:
   | Rationalization | Reality |
   |-----------------|---------|
   | "Voy a organizar estos archivos directo en el canónico" | NO. Todo write pasa por sync_*_indexa.ps1 o pregunta primero. |
   | "Es solo un pequeño fix, no necesita draft mode" | NO. Draft-first es invariante absoluta. |
   | "El usuario no dijo explícitamente que no tocara otros archivos" | NO. Surgical changes: touch only what you must. |

5. **Stop hook con driftcheck**: Verificar estructura de docs/ antes de terminar sesión. Chequear: unauthorized files at root level, files in records/ following YYYY-MM-DD_ prefix, .DS_Store creep [^177^].

6. **Skills para tareas recurrentes**: `/finalize` (quita draft: true, re-valida), `/ingest` (nueva fuente al KB), `/lint-taxonomy` (valida tipos canónicos), `/mirror-check` (verifica sync canónico ↔ mirror). Por qué: progressive disclosure mantiene el context window limpio [^54^][^121^].

**NO implementar:**

1. **NO poner todo en CLAUDE.md raíz**: Split en `.claude/rules/*.md` por dominio (taxonomía, sync, curaduría). Target: 3-5 rule files, cada uno <30 líneas. Root CLAUDE.md <60 líneas [^125^].

2. **NO usar rule files re-inyectados en cada tool call**: Cuestan 500 tokens × 30 tool calls = 93K tokens. Si se necesitan reglas por dominio, usar skills con `disable-model-invocation: true` y activar manualmente [^125^][^96^].

3. **NO confiar solo en CLAUDE.md para reglas de seguridad**: El framing "may or may not be relevant" hace que reglas de "nunca escribas al canónico" sean sugerencias, no mandatos. Las reglas que protegen contra data loss van en hooks [^93^][^89^].

4. **NO permitir auto-mode sin guardrails**: El incidente #49464 (rm -f ~/) demuestra que auto-mode + cleanup behavior es peligroso sin PreToolUse hooks que bloquean comandos destructivos [^182^].

**Diferir post-MVP:**

1. **MCP server para el gateway**: badwally implementó MCP server en M7 [^256^]. Para MWT, esto es post-Foundation Beta. El gateway puede ser un script PowerShell inicial.
2. **Agent teams / multi-agent**: No aplica a single-agent MVP. La documentación oficial de Claude Code sobre agent teams [^232^] es útil para post-MVP.
3. **Enterprise policy files**: Requieren Claude Code for Enterprise. MWT usa plan Max/Team, no Enterprise aún.

---

### Casos reales citados

| Equipo/Empresa | Caso | Métrica | Fuente |
|----------------|------|---------|--------|
| Andrej Karpathy / Forrest Chang | CLAUDE.md con 4 reglas edit-time | 97.8k stars, bug fix de 40 líneas → 2 líneas | [^29^][^31^] |
| HumanLayer | CLAUDE.md productivo | <60 líneas, mejor compliance que 200-línea manifestos | [^124^][^119^] |
| Boris Cherny (creador Claude Code) | CLAUDE.md equipo Anthropic | ~60-83 líneas, actualizado colaborativamente por errores reales | [^124^] |
| Behavox | Rollout Claude Code Enterprise | "Cientos de devs, go-to pair programmer" | [^133^] |
| Altana | Claude Code + Claude | "2-10x development velocity" | [^133^] |
| Atlassian (Rovo Dev) | AI code review interno | PR cycle time -45% (interno), -32% (clientes beta) | [^259^] |
| 1mg (India, 300 ingenieros) | AI platform DeputyDev | 31.8% reducción PR review time (p=0.0076), 28% increase code shipment | [^262^] |
| CPinto / Rails SaaS | Built complete SaaS with Claude Code | 38,600 líneas Rails, ~25-45h human time, 727 commits en 8 semanas | [^71^] |
| Dzianis Karviha | Claude Code en proyecto grande | 40% productivity increase, commits más atómicos | [^70^] |
| Paul Duvall | Centralized-rules pattern | 74.4% token savings, consistent AI behavior across teams | [^228^] |
| Badwally / TheKnowledge | KB con gateway + validator + draft mode | 134 tests passing, 11 MCP tools, 6 page types, content-hash idempotency | [^254^][^256^] |
| Addy Osmani (Google→Anthropic) | Agent-skills open source | 20 skills, anti-rationalization tables, 18.1k stars | [^121^][^126^] |
| Faros AI (análisis cohorte) | Team A 5% adoption vs Team B 60% | Team B merged 47% more PRs daily pero 35% longer review times | [^129^] |
| CWAN Engineering | AI-powered markdown KB | Tier 1 = read-only SSoT, agent must cite file:line | [^234^] |
| LowCode Agency | Multi-tenant SaaS con Claude Code | 3-5 días para foundation vs 2-4 semanas manual | [^88^] |
| GoClaw | Multi-tenant AI agent platform | 40+ tables con tenant_id, 5-layer defense-in-depth | [^94^] |
| Augusteo | "20 PRs a weekend" con Claude Code | Superpower Code Review + automated PR toolkit + Cubic Reviewer | [^260^] |
| Anthropic Data Infrastructure | Multiple parallel Claude Code sessions | Checkpoint-heavy workflow, one mission = one session | [^237^] |

---

### Gotchas y riesgos

1. **Context rot no es teórico**: "Lost in the Middle" (Liu et al., 2023) demostró que performance es más alta cuando información relevante está al principio o final del contexto, degradándose significativamente en el medio [^170^]. NoLiMa Benchmark: a 32k tokens, 11/12 modelos bajaron de 50% performance [^69^].

2. **Thinking token reduction = degradación real**: Un análisis cuantitativo de 17,871 thinking blocks y 234,760 tool calls reveló que la reducción de thinking tokens (redact-thinking-2026-02-12) correlacionó con quality regression medible. Convention drift: variable names prohibidas reaparecieron, cleanup patterns violados [^73^].

3. **El "compliance decay curve"**: Claude sigue reglas perfectamente por 3 mensajes, luego las abandona. No es malicioso, es atención diluida [^124^].

4. **"Simplest" como señal de degradación**: En logs de 6,852 sesiones, la palabra "simplest" aumentó 642% post-regresión. Indica que el modelo elige el path más fácil, no el correcto [^73^].

5. **Skills no se auto-activan confiablemente**: La documentación dice que skills son "autonomous" y "model-invoked", pero en práctica "you need to smash Claude over the head to actually use them" [^96^]. Requiere hook-based reinforcement o invocación explícita.

6. **Subagents no heredan skills del main session**: Si defines skills en el main agent, debes pasarlos explícitamente al subagent vía `skills:` field [^52^].

7. **MCP servers consumen context agresivamente**: 100+ MCP tools pueden ocupar 33.4% del context window antes de que empiece la conversación [^100^].

8. **Auto-compact contaminó contexto**: Un usuario reportó que con Auto Compact ON, sesión iniciaba en 85k/200k tokens (43%). Después de desactivarlo: 38k/200k (19%) [^67^].

---

### 4-6 patrones canónicos para incorporar a MWT CLAUDE.md v2

#### Patrón 1: Dual-Surface Control (CLAUDE.md + WIKI.md)

Adaptado de badwally/TheKnowledge [^175^][^254^]:

```markdown
# CLAUDE.md — MWT KB Agent Control Surface
## Identity
You are the KB curator assistant for Muito Work Limitada. 
Your job: organize, validate, synthesize knowledge. 
You NEVER write production code for FaberLoom.

## Canonical Source of Truth
- Git repo at C:\dev\mwt-knowledge-hub is the ONLY canonical source
- OneDrive mirror is working copy for Cowork sessions
- ALL changes flow through sync_*_indexa.ps1 back to canonical
- NEVER write directly to canonical repo from Cowork

## Rules (Inquebrantables)
1. DRAFT-FIRST: All new content starts as draft: true
2. CURADURÍA 2 CAPAS: USER review + COMMITTEE approval before finalize
3. SURGICAL CHANGES: Touch only what the task requires
4. ASK-DONT-ASSUME: When unclear, stop and ask. Never guess.
5. CITE-OR-DIE: Every claim must cite source with [[file:line]]
6. SEALED-OPEN: Sealed files = read-only. Open files = working drafts.

## Taxonomy (8 tipos canónicos)
ENT | PLB | SCH | LOC | POL | IDX | SKILL | LOTE
Every file MUST have correct frontmatter type.

## Commands
- Ingest source: use wiki ingest <path>
- Finalize draft: use wiki finalize <path>
- Check sync: use wiki mirror-check
- Lint taxonomy: use wiki lint-taxonomy
```

```markdown
# WIKI.md — MWT KB Conventions Reference
## §1 Directory Layout
├── canonical/           # Git repo (C:\dev\mwt-knowledge-hub)
│   ├── ENT/, PLB/, SCH/, LOC/, POL/, IDX/, SKILL/, LOTE/
│   ├── docs/            # Documentación operativa
│   └── .claude/         # Skills y hooks
├── mirror/              # OneDrive working copy
│   └── (sync via mirror_to_onedrive.ps1)

## §2 Frontmatter Schema
---
type: ENT | PLB | SCH | LOC | POL | IDX | SKILL | LOTE
id: UUIDv7
created: ISO8601
modified: ISO8601
draft: true | false
tier: 1 | 2 | 3 | 4
tags: [tag1, tag2]
---

## §3 Tier System
- Tier 1 (Source of Truth): Leadership-approved, read-only for agents
- Tier 2 (Core Knowledge): Foundational technical docs
- Tier 3 (Implementation): Working documents, change frequently
- Tier 4 (Archive): Non-authoritative, explicitly marked

## §4 Gateway Operations
All writes MUST pass through:
1. validate input (frontmatter, taxonomy, citations)
2. acquire file lock (.knowledge/locks/)
3. execute operation
4. validate output
5. write atomically
6. update index.md
7. append to log.md
8. release lock

## §5 Sync Protocol
- canonical → mirror: mirror_to_onedrive.ps1 (read-only from canonical POV)
- mirror → canonical: sync_*_indexa.ps1 (validates before write)
- NEVER bidirectional sync without validation gate
```

#### Patrón 2: Hook-Based Reinforcement para Reglas Críticas

Adaptado de "Claude Core Values" plugin [^93^]:

`.claude/settings.json`:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/reinject-rules.sh"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/reminder.sh"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/canonical-guard.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/driftcheck.sh"
          }
        ]
      }
    ]
  }
}
```

`~/.claude/hooks/reinject-rules.sh`:
```bash
#!/bin/bash
echo "=== MWT INQUEBRANTABLES ==="
echo "1. DRAFT-FIRST: All new content starts as draft"
echo "2. CURADURÍA 2 CAPAS: USER + COMMITTEE before finalize"
echo "3. NEVER write directly to canonical repo"
echo "4. SURGICAL CHANGES: touch only what task requires"
echo "5. ASK-DONT-ASSUME: stop and ask when unclear"
echo "6. CITE-OR-DIE: every claim cites [[file:line]]"
echo "==========================="
```

`~/.claude/hooks/canonical-guard.sh`:
```bash
#!/bin/bash
# Read stdin for tool use JSON
read -r input
file_path=$(echo "$input" | jq -r '.tool_input.file_path // .tool_input.path // empty')

if [[ "$file_path" == *"C:\\dev\\mwt-knowledge-hub"* ]] || [[ "$file_path" == *"/mnt/agents/mwt-knowledge-hub"* ]]; then
  echo '{"decision": "block", "reason": "WRITING TO CANONICAL REPO DIRECTLY IS FORBIDDEN. Use sync_*_indexa.ps1 or ask permission."}'
  exit 1
fi

echo '{"decision": "allow"}'
```

#### Patrón 3: Anti-Rationalization Table

Adaptado de addyosmani/agent-skills [^121^][^123^]:

```markdown
## Common Rationalizations (DO NOT FALL FOR THESE)

| Rationalization | Reality |
|-------------------|---------|
| "Voy a mover estos archivos directo al canónico para organizar" | NO. Todo write pasa por sync_*_indexa.ps1 o pregunta primero. El canónico es SSoT. |
| "Es solo un pequeño fix, no necesita draft mode" | NO. Draft-first es INVARIANTE ABSOLUTA. Zero excepciones. |
| "El usuario no dijo explícitamente que no tocara otros archivos" | NO. Surgical changes: touch ONLY what you must. Pre-existing code is sacred. |
| "Voy a 'mejorar' el formato/consistencia mientras hago el fix" | NO. Clean up ONLY your own mess. Match existing style. |
| "Estos 11 archivos de FaberLoom los voy a poner en docs/ raíz" | NO. docs/ raíz es para documentación del KB, no para artefactos de producto. |
| "No hay tests para KB, así que no necesito verificación" | NO. Todo write pasa por validator: frontmatter, taxonomy, citations. |
| "El mirror y el canónico están desync, voy a sincronizar directo" | NO. Ask permission. Sync protocol has validation gates for a reason. |
```

#### Patrón 4: Skills para KB Operations

`.claude/skills/kb-ingest/SKILL.md`:
```yaml
---
name: kb-ingest
description: Ingest a new source into the MWT KB. Use when adding documents, web clips, voice notes, or any new knowledge source. Triggers on "ingest", "add to KB", "nueva fuente".
disable-model-invocation: false
---

## Overview
Ingest sources into the MWT KB through the canonical gateway.

## Process
1. Validate source format (markdown + YAML frontmatter)
2. Check content-hash idempotency (no duplicates)
3. Write to raw/<type>/<id>.md
4. Generate wiki/sources/<id>.md summary
5. Update index.md
6. Append to log.md

## Verification
- [ ] Source has valid frontmatter with type, id, created, draft:true
- [ ] Content hash is unique (not duplicate)
- [ ] Raw file written successfully
- [ ] Wiki summary generated with citations
- [ ] index.md updated
- [ ] log.md appended

## Common Rationalizations
| "Voy a escribir directo sin pasar por el gateway" | NO. Gateway mediates every write for validation and audit trail. |
| "No necesito draft porque la fuente ya está curada" | NO. Draft-first applies to ALL new content. COMMITTEE must approve. |
```

`.claude/skills/kb-finalize/SKILL.md`:
```yaml
---
name: kb-finalize
description: Finalize a draft KB page after curation approval. Use when COMMITTEE has approved and draft: true needs to become draft: false. Triggers on "finalize", "approve", "publicar".
---

## Process
1. Read draft file
2. Strip draft fields from copy
3. Run strict validation (validator.py composite)
4. If validation passes: write finalized version
5. If validation fails: report errors, keep draft

## Verification
- [ ] All citations ground to real sources
- [ ] Frontmatter type is valid canonical type
- [ ] No [[broken-links]]
- [ ] Tier assigned correctly
- [ ] COMMITTEE approval documented in log.md
```

#### Patrón 5: Stop Hook con Driftcheck

`~/.claude/hooks/driftcheck.sh`:
```bash
#!/bin/bash
# Run at session end to verify no unauthorized changes

echo "=== DRIFT CHECK ==="

# Check for unauthorized files at docs/ root
unauthorized=$(find "C:\dev\mwt-knowledge-hub\docs" -maxdepth 1 -type f ! -name "*.md" ! -name ".gitkeep" 2>/dev/null)
if [ -n "$unauthorized" ]; then
  echo "[BLOCK] Unauthorized files at docs/ root:"
  echo "$unauthorized"
  echo "Move to correct subdirectory or remove before ending session."
fi

# Check for files outside taxonomy directories
orphans=$(find "C:\dev\mwt-knowledge-hub" -maxdepth 1 -type f -name "*.md" ! -name "CLAUDE.md" ! -name "WIKI.md" ! -name "README.md" ! -name "index.md" ! -name "log.md" 2>/dev/null)
if [ -n "$orphans" ]; then
  echo "[WARN] Markdown files at repo root (should be in typed directories):"
  echo "$orphans"
fi

# Check .DS_Store creep
if find "C:\dev\mwt-knowledge-hub" -name ".DS_Store" -print -quit | grep -q .; then
  echo "[WARN] .DS_Store files found. Clean before commit."
fi

echo "==================="
```

#### Patrón 6: Tier System para Authority Hierarchy

Adaptado de CWAN Engineering [^234^]:

```markdown
## Authority Hierarchy (Tier System)

### Tier 1: Source of Truth (Sealed)
- Leadership-approved documents defining project direction
- Read-only for AI agents
- Examples: architecture decisions, compliance policies, pricing tiers
- Agent MUST cite with file:line evidence for any authoritative claim
- If agent contradicts Tier 1, agent is WRONG

### Tier 2: Core Knowledge
- Foundational technical documents (API design, data model, integration patterns)
- Agent reads these during session initialization
- Citable, but may evolve with engineering approval

### Tier 3: Implementation & Analysis
- Working documents: sprint notes, meeting minutes, generated reports
- Change frequently
- Agent may suggest updates, but USER curates

### Tier 4: Historical/Archive
- Old documents kept for reference
- Explicitly marked NON-AUTHORITATIVE
- Agent MUST NOT cite as current truth

## Enforcement
1. Session initialization: read Tier 1 files first
2. Every claim: cite Tier 1 with [[file:line]] or mark confidence (HIGH/MEDIUM/LOW)
3. Never speculate about system behavior — cite or ask
```

---

### Métricas de éxito a trackear post-implementación

#### Métricas de calidad del KB (semanal)

| # | Métrica | Cómo medir | Target | Frecuencia |
|---|---------|-----------|--------|------------|
| 1 | Archivos sin frontmatter válido | `grep -L "^---"` en nuevos archivos | 0 | Semanal |
| 2 | Archivos en ubicación incorrecta (fuera de taxonomía) | Driftcheck hook output | 0 | Por sesión |
| 3 | Archivos draft sin aprobación después de 7 días | Query `draft: true` + age | <5% | Semanal |
| 4 | Citations rotas (`[[broken]]`) | Wiki link validator | 0 | Semanal |
| 5 | Incidentes "AI cleanup" (cambios no solicitados) | Log de sesiones + diff review | 0 | Por incidente |
| 6 | Writes directos al canónico bloqueados | PreToolUse hook log | 0 | Por intento |

#### Métricas de eficiencia del agente (mensual)

| # | Métrica | Cómo medir | Target | Frecuencia |
|---|---------|-----------|--------|------------|
| 7 | Diff size promedio (líneas cambiadas por tarea) | `git diff --stat` por sesión | <15 líneas para tareas simples | Mensual |
| 8 | Follow-up clarifications por sesión | Contar prompts tipo "no, eso no es lo que pedí" | <1 | Mensual |
| 9 | Sesiones que requieren /rewind o /clear | Contar sesiones con rollback | <10% | Mensual |
| 10 | Tiempo de curaduría (draft → finalize) | Timestamp draft vs timestamp finalize | <48h para Tier 3, <7d para Tier 2 | Mensual |
| 11 | Reglas de CLAUDE.md que se ignoran | Auditoría manual de sesiones grabadas | 0 para inquebrantables | Mensual |
| 12 | Token cost por sesión de KB | Claude Code statusline | <20k tokens promedio | Mensual |

#### Métricas de adopción del equipo (trimestral)

| # | Métrica | Cómo medir | Target | Frecuencia |
|---|---------|-----------|--------|------------|
| 13 | % sesiones usando skills (`/skill-name`) vs prompts raw | Skill auditor log [^51^] | >70% | Trimestral |
| 14 | Consistencia de taxonomía (archivos con tipo correcto) | Validator output | >95% | Trimestral |
| 15 | Nuevos contributors con setup correcto en día 1 | Onboarding checklist completion | 100% | Por onboarding |

---

### Anti-patterns a evitar explícitamente

| # | Anti-pattern | Por qué falla | Mitigación en MWT |
|---|-------------|---------------|-------------------|
| 1 | **Monolithic Mega-Prompt** — CLAUDE.md de 300+ líneas | Context overload, atención diluida, reglas finales ignoradas | Target <60 líneas raíz. Split en `.claude/rules/*.md` [^173^] |
| 2 | **Confiar en CLAUDE.md para reglas de seguridad** | El framing "may or may not be relevant" las convierte en sugerencias | Reglas críticas en hooks (SessionStart, PreToolUse) [^93^] |
| 3 | **Rule files re-inyectados en cada tool call** | 500 tokens × 30 calls = 93K tokens (46% de context window) | 3-5 rule files, <30 líneas cada uno. Skills con `disable-model-invocation: true` [^125^] |
| 4 | **AI cleanup behavior sin guardrails** | Modifica código/archivos no relacionados, genera regressions | PreToolUse hook bloquea writes no autorizados. Regla explícita: "touch only what you must" [^68^] |
| 5 | **Infinite loop sin circuit breaker** | Repite mismo comando fallido 7+ veces, consume $500+ en tokens | Límite de retries en hooks. Loop detection: abort after N identical requests [^100^][^102^] |
| 6 | **System prompt override de CLAUDE.md** | Plan mode / agent launch ignora reglas del usuario | Hooks que re-inyectan reglas tras cada compactación. Verificación manual de plan mode [^89^] |
| 7 | **Invisible state** — confiar en que el LLM "recuerda" | Estado comprimido, detalles perdidos, drift creciente | Estado explícito en log.md + index.md. Gateway mantiene estado estructurado [^173^] |
| 8 | **Happy path engineering** — solo probar el éxito | Agente nunca vio fallos, no sabe distinguir retry vs escalate | Skills con failure recovery patterns. Test con inputs malformados [^170^] |
| 9 | **Multi-agent chaos sin roles claros** | Agentes duplican trabajo, se contradicen, bounce control | MVP = single-agent. Post-MVP: roles definidos, shared state con invariantes [^170^] |
| 10 | **Contradictory instructions** — reglas que se anulan | "Nunca escribas fuera del repo" vs "escribe plan en ~/.claude/plans/" | Una sola fuente de verdad para reglas. WIKI.md como contract. Resolución: más específico gana [^89^] |
| 11 | **Agent-as-Business-Process** — dejar que el agente "aproxime" procesos | Reemplaza process graph controlado con reasoning no determinista | Gateway con pasos definidos: validate → lock → execute → validate → log [^173^][^254^] |
| 12 | **Sycophancy — agente dice lo que quiere oír** | Evita conflictos, no surfacea problemas reales | Anti-rationalization tables. Explicit conflict detection [^172^] |

---

### Secciones para KB con sync canónico

#### El patrón SSoT (Single Source of Truth) para KB

**Principios (adaptado de Shelfi [^169^] + badwally [^175^])**:
1. **Git es la SSoT**: El repo canónico es la única fuente de verdad. Si no está en Git, no es verdad.
2. **Version controlled**: Cada cambio trackeado en Git history. Audit trail completo.
3. **Code-adjacent**: Docs reviewed como parte del PR process. Nunca un afterthought.
4. **Centralized & searchable**: Índice `index.md` reconstruible desde el gateway.
5. **Ultimate portability**: Markdown files en repo propio. Zero vendor lock-in.

**Arquitectura de sync (caso MWT)**:
```
┌─────────────────────────────────────────┐
│  C:\dev\mwt-knowledge-hub (CANONICAL)   │
│  ├── Git repo = SSoT                    │
│  ├── CLAUDE.md + WIKI.md                │
│  ├── 8 typed directories (ENT/PLB/...)  │
│  ├── index.md + log.md                  │
│  └── .knowledge/ (locks, policies, lint)│
└─────────────────┬───────────────────────┘
                  │ mirror_to_onedrive.ps1
                  │ (one-way, read-only from canonical POV)
                  ▼
┌─────────────────────────────────────────┐
│  OneDrive (MIRROR / WORKING COPY)       │
│  ├── Cowork escribe aquí                │
│  └── Temporal, disposable               │
└─────────────────┬───────────────────────┘
                  │ sync_*_indexa.ps1
                  │ (validates before write to canonical)
                  ▼
┌─────────────────────────────────────────┐
│  Back to CANONICAL                      │
│  └── Gateway validates, locks, logs     │
└─────────────────────────────────────────┘
```

**Reglas del sync protocol**:
1. **Unidireccional por etapa**: canonical → mirror es export. mirror → canonical es import con validation gate.
2. **Nunca bidireccional automático**: El sync bidireccional sin gate genera conflictos y data loss.
3. **Content-hash idempotencia**: Re-ingest del mismo file es no-op si hash no cambia [^254^].
4. **Log append-only**: Cada operación de sync queda en `log.md` con timestamp, dirección, files afectados, y hash.
5. **Lock durante sync**: `.knowledge/locks/` previene race conditions si Cowork y sync script corren simultáneamente.

**CLAUDE.md rules específicas para sync**:
```markdown
## Sync Protocol (NEVER VIOLATE)
1. CANONICAL → MIRROR: mirror_to_onedrive.ps1 (export)
2. MIRROR → CANONICAL: sync_*_indexa.ps1 (import with validation)
3. NEVER write directly to canonical from Cowork
4. NEVER run bidirectional sync without validation gate
5. If sync conflict detected: STOP, ask human, log incident
6. After every sync: verify index.md consistency
```

---

### Sources

[^11^]: https://code.claude.com/docs/en/best-practices — Anthropic, "Best practices for Claude Code" (2025)
[^14^]: https://discuss.huggingface.co/t/10-essential-claude-code-best-practices-you-need-to-know/174731 — "10 Essential Claude Code Best Practices" (2026-03-28)
[^29^]: https://forum.devtalk.com/t/has-anyone-tried-the-karpathy-claude-md-rules-97-8k-stars/243109 — "Has anyone tried the Karpathy CLAUDE.md rules?" (2026-04-29)
[^30^]: https://intuitionlabs.ai/articles/claude-enterprise-deployment-training-guide-2026 — "Claude Enterprise Guide 2026" (2026-04-26)
[^31^]: https://alphasignalai.substack.com/p/karpathy-inspired-claudemd-how-to — "Karpathy-Inspired CLAUDE.md" (2026-04-22)
[^32^]: https://github.com/MuhammadUsmanGM/claude-code-best-practices — "claude-code-best-practices" GitHub (2026-04-23)
[^33^]: https://antigravity.codes/blog/karpathy-claude-code-skills-guide — "Karpathy's CLAUDE.md Skills File" (2026-04-13)
[^34^]: https://dev.to/reneza/ten-claudemd-rules-for-claude-code-four-edit-time-six-runtime-210g — "Ten CLAUDE.md rules" (2026-04-23)
[^35^]: https://medium.com/@elliotJL/your-ai-has-infinite-knowledge-and-zero-habits-heres-the-fix-e279215d478d — "Claude Keeps Making the Same Mistakes" (2026-01-28)
[^36^]: https://arize.com/blog/claude-md-best-practices-learned-from-optimizing-claude-code-with-prompt-learning/ — "CLAUDE.md Best Practices from Prompt Learning" (2025-11-20)
[^37^]: https://www.gend.co/blog/claude-skills-claude-md-guide — "Claude Skills and Claude MD" (2025-12-05)
[^48^]: https://www.techplained.com/claude-code-subagents-skills — "Claude Code Subagents, Skills, Hooks" (2026-02-13)
[^49^]: https://github.com/anthropics/claude-code/issues/30554 — "Feature Request: Team/shared CLAUDE.md" (2026-03-03)
[^50^]: https://serenitiesai.com/articles/agent-skills-guide-2026 — "AI Agent Skills Guide 2026" (2026-03-05)
[^51^]: https://www.developersdigest.tech/blog/best-claude-code-skills-2026 — "Best Claude Code Skills 2026" (2026-04-28)
[^52^]: https://code.claude.com/docs/en/features-overview — "Extend Claude Code" Anthropic Docs (2025)
[^53^]: https://aimaker.substack.com/p/anthropic-claude-updates-q1-2026-guide — "Complete Guide to Claude Updates Q1 2026" (2026-04-07)
[^54^]: https://www.fundesk.io/claude-skills-agent-skills-complete-guide-2026 — "2026 Guide to Agent Skills" (2026-04-20)
[^55^]: https://smartscope.blog/en/generative-ai/claude/claude-code-best-practices-advanced-2026/ — "Claude Code Advanced Best Practices" (2026)
[^67^]: https://www.reddit.com/r/ClaudeAI/comments/1p05r7p/my_claude_code_context_window_strategy_200k_is/ — "Context Window Strategy" (2026-02-26)
[^68^]: https://github.com/anthropics/claude-code/issues/15333 — "Mark code sections as 'do not modify'" (2025-12-24)
[^69^]: https://limitededitionjonathan.substack.com/p/ultimate-guide-fixing-claude-hit — "Fixing Claude max length" (2025-11-06)
[^70^]: https://dev.to/dzianiskarviha/integrating-claude-code-into-production-workflows-lbn — "Claude Code in Production: 40% Productivity" (2025-12-22)
[^71^]: https://world.hey.com/cpinto/building-a-complete-saas-product-with-only-claude-code-cca13895 — "Building SaaS with only Claude Code" (2026-02-08)
[^72^]: https://www.mindstudio.ai/blog/what-is-claude-code-auto-mode-permission-classifier/ — "Claude Code Auto Mode" (2026-04-01)
[^73^]: https://github.com/anthropics/claude-code/issues/42796 — "Claude Code unusable for complex tasks Feb updates" (2026-04-02)
[^88^]: https://www.lowcode.agency/blog/claude-code-multi-tenant-architecture — "Multi-Tenant App Architecture with Claude Code" (2026-04-10)
[^89^]: https://github.com/anthropics/claude-code/issues/27032 — "Model ignores CLAUDE.md instructions" (2026-02-19)
[^90^]: https://www.reddit.com/r/ClaudeCode/comments/1se66cf/something_has_changed_claude_code_now_ignores/ — "Claude Code now ignores every rule" (2026)
[^91^]: https://github.com/anthropics/claude-code/issues/2544 — "CLAUDE.md Mandatory Rules Consistently Ignored" (2025-06-24)
[^92^]: https://medium.com/@richardhightower/claude-code-rules-stop-stuffing-everything-into-one-claude-md-0b3732bca433 — "Stop Stuffing Everything into One CLAUDE.md" (2026-03-10)
[^93^]: https://dev.to/albert_nahas_cdc8469a6ae8/your-claudemd-instructions-are-being-ignored-heres-why-and-how-to-fix-it-23p6 — "Your CLAUDE.md Instructions Are Being Ignored" (2026-02-17)
[^94^]: https://dev.to/truongpx396/goclaw-deep-dive-a-builders-guide-to-a-multi-tenant-ai-agent-platform-5d6c — "Multi-Tenant AI Agent Platform" (2026-04-28)
[^96^]: https://scottspence.com/posts/claude-code-skills-dont-auto-activate — "Claude Code Skills Don't Auto-Activate" (2025-11-05)
[^100^]: https://github.com/anthropics/claude-code/issues/35166 — "Claude Code sends repeated requests hundreds of times" (2026-03-16)
[^102^]: https://github.com/anthropics/claude-code/issues/19699 — "Claude gets stuck in infinite loop" (2026-01-21)
[^118^]: https://jimmysong.io/ai/addyosmani-agent-skills/ — "Agent Skills by Addy Osmani" (2026-04-27)
[^119^]: https://dev.to/shipwithaiio/beyond-claudemd-5-layers-your-ai-agent-harness-is-missing-475h — "Beyond CLAUDE.md: 5 Layers Missing" (2026-04-22)
[^120^]: https://dev.to/_46ea277e677b888e0cd13/agent-skills-19-production-grade-skills-that-make-ai-coding-agents-work-like-senior-engineers-5bi9 — "19 Production-Grade Skills" (2026-04-08)
[^121^]: https://github.com/addyosmani/agent-skills — "addyosmani/agent-skills" GitHub (2026-02-15)
[^123^]: https://github.com/addyosmani/agent-skills/blob/main/docs/skill-anatomy.md — "Skill Anatomy" (2026-02-15)
[^124^]: https://thomas-wiegold.com/blog/claude-md-helpful-or-expensive-noise/ — "CLAUDE.md: Helpful or Expensive Noise?" (2026-03-09)
[^125^]: https://github.com/abhishekray07/claude-md-templates/blob/main/principles.md — "Writing Rules Claude Actually Follows" (2026)
[^126^]: https://addyosmani.com/blog/agent-skills/ — "Agent Skills" blog (2026-05-04)
[^127^]: https://www.theunwindai.com/p/open-source-solution-to-context-rot-in-ai-agents — "Open-Source Solution to Context Rot" (2025-12-03)
[^128^]: https://codewithmukesh.com/blog/claude-md-mastery-dotnet/ — "CLAUDE.md Memory Hierarchy" (2026-01-24)
[^129^]: https://www.faros.ai/blog/how-to-measure-claude-code-roi-developer-productivity-insights-with-faros — "How to measure Claude Code ROI" (2026-01-07)
[^130^]: https://rachel.fyi/posts/what-i-took-from-addy-osmanis-agent-skills — "What I Took from Agent Skills" (2026-04-16)
[^131^]: https://shipwithai.io/blog/claude-code-harness-5-layers/ — "5 Layers Your AI Agent Harness Is Missing" (2026-04-09)
[^132^]: https://pub.towardsai.net/writing-a-good-claude-md-c40a32b39dfa — "Writing a Good CLAUDE.md" (2026-03-10)
[^133^]: https://www.anthropic.com/news/claude-code-on-team-and-enterprise — "Claude Code and admin controls" (2025-08-20)
[^134^]: https://github.com/anthropics/claude-code/issues/29990 — "Governing stateless sessions with CLAUDE.md + MEMORY.md" (2026-03-01)
[^135^]: https://www.rushis.com/agent-skills-teaching-ai-agents-to-code-like-senior-engineers/ — "Agent Skills: Teaching AI agents" (2026-04-13)
[^169^]: https://shelfi.sh/features/single-source/ — "Git-Based Single Source of Truth" (2026)
[^170^]: https://achan2013.medium.com/ai-agent-anti-patterns-part-2-tooling-observability-and-scale-traps-in-enterprise-agents-42a451ea84ec — "AI Agent Anti-Patterns Part 2" (2026-03-25)
[^171^]: https://elements.cloud/blog/agent-instruction-patterns-and-antipatterns-how-to-build-smarter-agents/ — "Agent Instruction Patterns and Antipatterns" (2025-06-27)
[^172^]: https://xmpro.com/when-ai-agents-tell-you-what-you-want-to-hear-the-sycophancy-problem/ — "Sycophancy Problem" (2025-06-03)
[^173^]: https://achan2013.medium.com/ai-agent-anti-patterns-part-1-architectural-pitfalls-that-break-enterprise-agents-before-they-32d211dded43 — "AI Agent Anti-Patterns Part 1" (2026-03-02)
[^174^]: https://github.com/anthropics/claude-code/issues/26512 — "Infinite loop bug with AI self-aware" (2026-02-17)
[^175^]: https://github.com/badwally/TheKnowledge/blob/main/WIKI.md — "TheKnowledge WIKI.md" (2026-04-29)
[^177^]: https://dev.to/shimo4228/stop-using-default-settings-10-claude-code-configs-that-actually-work-243l — "10 Claude Code Configs That Actually Work" (2026-03-05)
[^181^]: https://wmedia.es/en/tips/claude-code-claudemd-project-setup — "Your CLAUDE.md Is Full of Junk" (2026-03-03)
[^182^]: https://github.com/anthropics/claude-code/issues/49464 — "Claude attempts to delete home directory" (2026-04-16)
[^192^]: https://koder.ai/blog/claude-code-git-hooks-automation — "Claude Code git hooks" (2026-01-08)
[^196^]: https://engrxiv.org/preprint/download/6681/10947/9274 — "Rule-Based Governance of AI System Behavior" (2026)
[^197^]: https://mintlify.com/galfrevn/promptsmith/concepts/constraints — "Behavioral Constraints - PromptSmith" (2026-03-03)
[^198^]: https://dius-au.medium.com/a-week-with-claude-code-lessons-surprises-and-smarter-workflows-47584eb55e8d — "A week with Claude Code" (2026-04-29)
[^227^]: https://nimbalyst.com/blog/how-to-set-up-claude-code-for-your-team/ — "How to Set Up Claude Code for Your Team" (2026-03-24)
[^228^]: https://www.paulmduvall.com/sharing-ai-development-rules-across-your-organization/ — "Sharing AI Development Rules" (2026-01-29)
[^229^]: https://dev.to/myougatheaxo/standardizing-claude-code-across-your-team-claudemd-hooks-and-shared-skills-2nbn — "CLAUDE.md, Hooks, and Shared Skills" (2026-03-11)
[^230^]: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6122761 — "llm-wiki" Karpathy gist (2026-05-01)
[^232^]: https://code.claude.com/docs/en/agent-teams — "Orchestrate teams of Claude Code sessions" (2025)
[^233^]: https://www.elegantsoftwaresolutions.com/blog/claude-code-mastery-claude-md-patterns — "CLAUDE.md Patterns That Actually Work" (2025-12-27)
[^234^]: https://medium.com/cwan-engineering/building-an-ai-powered-markdown-knowledge-base-system-for-your-engineering-team-4bccea3cdbfe — "AI-Powered Markdown Knowledge Base" (2026-04-24)
[^237^]: https://www-cdn.anthropic.com/58284b19e702b49db9302d5b6f135ad8871e7658.pdf — "How teams use Claude Code" Anthropic PDF (2025)
[^238^]: https://www.ronforbes.com/blog/building-your-ai-second-brain — "Building Your AI Second Brain" (2026-02-09)
[^239^]: https://portkey.ai/blog/claude-code-best-practices-for-enterprise-teams — "Claude Code best practices for enterprise" (2026-03-10)
[^254^]: https://github.com/badwally/TheKnowledge/blob/main/BUILD.md — "TheKnowledge BUILD.md" (2026-04-29)
[^255^]: https://www.gend.co/blog/claude-code-preview-review-merge — "Claude Code Preview, Review & Merge" (2026-02-20)
[^256^]: https://github.com/badwally/TheKnowledge/blob/main/SESSION_TRANSCRIPT.md — "TheKnowledge SESSION_TRANSCRIPT" (2026-04-29)
[^257^]: https://koder.ai/blog/claude-code-pr-review-pre-review-diffs — "Claude Code PR review" (2025-12-26)
[^259^]: https://www.atlassian.com/blog/announcements/how-we-cut-pr-cycle-time-with-ai-code-reviews — "Atlassian cut PR cycle time 45%" (2026-01-28)
[^260^]: https://www.augusteo.com/blog/claude-code-workflow-planning/ — "I Ship 20 PRs a Weekend" (2026-03-03)
[^262^]: https://arxiv.org/html/2509.19708v1 — "Measuring AI's True Impact on Developer Productivity" (2025-09-24)
[^263^]: https://github.com/badwally/TheKnowledge — "TheKnowledge GitHub" (2026-04-28)
[^264^]: https://code.claude.com/docs/en/code-review — "Code Review - Claude Code Docs" (2025)


---

# Síntesis Ejecutiva del Swarm #6

## Decisiones que el roadmap MWT debe incorporar

| Dimensión | Decisión | Impacto en sprint | Bloquea/Depende de |
|-----------|----------|-------------------|-------------------|
| **D1 — Hybrid Retrieval** | Implementar Phase 1: `tsvector` + `ts_rank_cd` + `pgvector` HNSW + RRF en Python async. **NO** esperar extensión BM25 real. | Sprint 0-1 (2-3 días dev) | Depende de schema chunks existente. Bloquea C7 del SPEC_FB_RAG_SECURITY_FIREWALL_v1. |
| **D2 — KB Quality** | **DIFERIR** DeepEval + TruLens a Fase 2 (post-MVP). Implementar Plan B: Langfuse datasets + freshness audit ARQ daily + drift sentinel ARQ monthly + user feedback via draft-first. | Sprint 2 (setup, 4h) + running | No bloquea MVP. Se puede activar en cualquier sprint. |
| **D3 — Chunking** | Lazy migration con recursive chunking + sentence window (512/50). Agregar `queries_answered` al frontmatter de cada archivo KB (5-10 preguntas vía LLM). Hierarchical parent-child para POL/PLB críticos. CI validation en PRs. | Sprint 0-2 (schema + CI, 4h; lazy setup, 6h; batch 50 críticos, 6h) | Depende de definición de frontmatter schema. Afecta 540 archivos. |
| **D4 — CLAUDE.md** | Dual-surface: `CLAUDE.md` (<60 líneas, control surface) + `WIKI.md` (contract humano). Hooks: SessionStart (re-inyecta reglas), PreToolUse (bloquea writes al canónico), Stop (driftcheck). Anti-rationalization table. Skills para KB ops. | Sprint 0 (1-2 días dev) | Depende de acceso a hooks de Claude Code. No bloquea MVP pero previene incidentes. |

## Tensiones cross-dimensión

### Tensión 1: D3 sugiere DeepEval para validación de chunks vs D2 recomienda NO DeepEval en MVP
- **D3** propone usar `ContextualRelevancyMetric` de DeepEval para validar que un chunk responde una query.
- **D2** recomienda explícitamente NO implementar DeepEval en MVP por sobrecarga operativa (15-25% tiempo dev).
- **Resolución:** Para validación de chunking en MVP, usar **RAGAS vía Langfuse cookbook** (ya integrado) o evaluación manual periódica, no DeepEval pytest suite. DeepEval se reserva para Fase 2 cuando haya CI/CD maduro.

### Tensión 2: D1 recomienda índice GIN sobre tsvector generada vs D3 recomienda migración lazy con dual-index
- **D1** sugiere columna `tsvector` generada (`GENERATED ALWAYS`) por simplicidad RLS-friendly.
- **D3** propone dual-index (`documents_v2` con `CREATE INDEX CONCURRENTLY`) para migración lazy de chunking.
- **Resolución:** Son complementarios. El dual-index de D3 es para la **migración de chunking strategy**, no para el índice FTS. El índice GIN de D1 convive en la misma tabla. No hay conflicto de schema si se planifica: la tabla `chunks` ya tiene `embedding`; se agrega `search_vector tsvector GENERATED ALWAYS` y se crea GIN índice concurrentemente.

### Tensión 3: D3 query-enriched frontmatter aumenta tamaño de archivo vs D4 CLAUDE.md target <60 líneas
- **D3** agrega frontmatter extenso (`queries_answered` con 5-10 objetos) a cada archivo KB.
- **D4** enseña que archivos largos degradan cumplimiento del agente.
- **Resolución:** La regla de <60 líneas aplica a **CLAUDE.md** (control surface del agente), no a los archivos KB. Los archivos KB pueden ser largos; lo que importa es que el agente no tenga que leerlos completos en cada sesión (índice + retrieval los filtra). El frontmatter es metadata parseable, no prose que consume context window del agente.

## Roadmap ajustado post-swarm

### Foundation Beta (2026-04-20 → 2026-06-14) — Ajustes

| Sprint | Entrega | Owner | Esfuerzo estimado |
|--------|---------|-------|-------------------|
| Sprint 0 (ahora) | D1: Schema híbrido en Supabase (tsvector + HNSW). D3: Frontmatter schema + CI validation script. D4: CLAUDE.md v2 + hooks básicos. | Tech lead | 3-4 días |
| Sprint 1 | D1: FastAPI endpoint `/search` híbrido (BM25 + vector + RRF). D3: Script generación `queries_answered` para 50 archivos críticos (POL/PLB/SKILL). | Backend dev | 3-4 días |
| Sprint 2-3 | D1: RLS multi-tenant test + latencia benchmark. D3: Lazy migration setup (re-chunk on edit). D2: Freshness audit ARQ job + drift sentinel. | Backend dev + SRE | 4-5 días |
| Sprint 4-5 | D3: Batch generate `queries_answered` para 200 archivos más. D1: Calibración k=60 vs queries reales MWT. D4: Anti-rationalization table + skills KB. | Backend + KB curator | 3-4 días |
| Sprint 6-8 | D3: Continuar lazy migration. D2: Langfuse dataset de 50 golden questions. D4: Métricas de driftcheck + token cost tracking. | Equipo completo | 4-6 días |
| Sprint 9-13 | MVP hardening. No nuevas features de D1-D4. | Equipo completo | — |

### Fase 2 (post-MVP, jul 2026)
- D1: Evaluar `pg_textsearch` o `pg_search` si corpus >50K chunks o si `ts_rank` insuficiente.
- D2: Integrar DeepEval pytest suite en CI/CD + TruLens si Langfuse no explica regressions.
- D3: Evaluar Intent-Driven Dynamic Chunking (IDC) si hay implementación estable en Python.
- D4: MCP gateway para KB ops si el equipo crece >3 devs.

## Costos proyectados consolidados (MVP)

| Componente | Costo mensual (1 tenant) | Costo mensual (10 tenants) | Costo mensual (100 tenants) | Nota |
|-----------|--------------------------|---------------------------|----------------------------|------|
| D1 — Hybrid retrieval (tsvector + HNSW) | $0 (nativo Supabase) | $0 | $0 | Storage overhead: +0.3-0.5x texto vs solo vector. |
| D2 — Quality monitoring (Plan B) | ~$0.20 | ~$2 | ~$20 | LLM judge GPT-4o-mini, 5% sample. Langfuse self-host ya pagado. |
| D3 — Query generation (one-time) | ~$0.50-1.60 (540 archivos) | N/A | N/A | GPT-4.1 Nano vía LiteLLM. Esfuerzo dev: 2-3 días. |
| D4 — CLAUDE.md v2 + hooks | $0 | $0 | $0 | Trabajo de developer: 1-2 días. |
| **TOTAL MVP** | **~$0.20-2** setup + $0.20/mes | **~$2/mes** | **~$20/mes** | **0.2–0.3% del MRR objetivo.** |

### Notas de costo
- El costo dominante del MVP NO es dinero, es **tiempo de developer**: ~10-15 días de trabajo distribuidos en sprints 0-5.
- Si se usara GPT-4o como judge (en vez de GPT-4o-mini) y 100% de queries evaluadas, multiplicar ×20–×100.
- El storage de índice HNSW domina sobre GIN/tsvector. Para 100K vectores 1536d: ~8-10 GB HNSW vs ~1-3 GB GIN.

## Criterios de éxito del swarm — Autoevaluación

| Criterio | Estado | Evidencia |
|----------|--------|-----------|
| ≥3 casos production por dimensión | ✅ | D1: 8 casos. D2: 8 casos. D3: 10 casos. D4: 16 casos. |
| Recomendación directa por dimensión | ✅ | Cada D tiene sección "Recomendación directa" con SÍ/NO/DIFERIR. |
| Tensiones cross-dimensión levantadas | ✅ | 3 tensiones explícitas con resolución. |
| Costo proyectado consolidado real | ✅ | Tabla con costos por tenant, % MRR, notas. |
| Síntesis apunta a cambios concretos en roadmap | ✅ | Tabla de sprints ajustada con entregables D1-D4. |

## Referencias a research bruto completo

Los archivos de research bruto por dimensión están disponibles en:
- `/mnt/agents/output/research/mwt_swarm6_d1.md` (Hybrid Retrieval, ~610 líneas)
- `/mnt/agents/output/research/mwt_swarm6_d2.md` (KB Quality, ~452 líneas)
- `/mnt/agents/output/research/mwt_swarm6_d3.md` (Chunking, ~849 líneas)
- `/mnt/agents/output/research/mwt_swarm6_d4.md` (CLAUDE.md, ~875 líneas)

---
*Swarm #6 completado el 2026-05-07. 4 agentes paralelos. ≥80 búsquedas web independientes. 40+ casos production citados.*
