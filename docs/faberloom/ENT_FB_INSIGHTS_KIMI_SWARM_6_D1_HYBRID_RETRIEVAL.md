# ENT_FB_INSIGHTS_KIMI_SWARM_6_D1_HYBRID_RETRIEVAL -- Hybrid Retrieval con pgvector + BM25 + RRF

---
id: ENT_FB_INSIGHTS_KIMI_SWARM_6_D1_HYBRID_RETRIEVAL
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: ENT
stamp: VIGENTE -- 2026-05-07
fecha: 2026-05-07
agente: Kimi K2.6 multi-agente D1 (research) + Cowork (sintesis indexada) + CEO (decisiones)
aplica_a: [FaberLoom, MWT]
relacionado_con:
  - SPEC_FB_RAG_SECURITY_FIREWALL_v1.md (bumpear a v1.1 con componente C7)
  - SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md (chunks table append columnas search_vector)
  - SPEC_FB_AUTH_TENANT_RBAC_v1.md (RLS multi-tenant compatible)
  - ROADMAP_INTEGRAL_KB_4_CAPAS.md (capa 3 retrieval)
origen: |
  Kimi Swarm #6 D1 ejecutado 2026-05-07. 8+ casos production citados.
  Research bruto: docs/anexos/kimi_swarm_6/research/mwt_swarm6_d1.md (610 lineas).
  Disparado por gap identificado en plan integral 4 capas:
  "Mi SPEC_FB_RAG_SECURITY_FIREWALL_v1 cubre security pero NO formaliza
  hybrid retrieval BM25+vector. En MVP single-agent, depender solo de vector
  similarity pierde queries con terminos exactos."
---

## 1. Decision principal

Implementar **Phase 1 Hybrid Retrieval** con `tsvector` + `ts_rank_cd` + `pgvector` HNSW + RRF en Python async. **NO esperar extension BM25 verdadera** (`pg_textsearch` / `pg_search` requieren self-host fuera de Supabase).

Phase 1 cubre **85% del beneficio de hybrid** sin extensiones adicionales. Diferir migracion a extension BM25 hasta post-MVP cuando corpus exceda 50K chunks o calidad de ranking de `ts_rank` sea insuficiente.

## 2. Hallazgos clave

### 2.1 pgvector NO incluye BM25 nativo

| Opcion | Tecnologia | Licencia | Disponible Supabase 2026-06 |
|---|---|---|---|
| A | `tsvector` + `ts_rank_cd` (nativo Postgres) | PostgreSQL | Si, nativo |
| B | `pg_search` (ParadeDB sobre Tantivy) | AGPL | No nativo, requiere replicacion ParadeDB |
| C | `pg_textsearch` (TigerData, C nativo) | PostgreSQL | No en Supabase, disponible en Tiger Cloud |
| D | `vchord_bm25` (VectorChord) | Apache 2.0 | No en Supabase, self-host via Docker |

**Solo Opcion A disponible para FaberLoom (stack frozen Supabase).** `ts_rank_cd` no es BM25 verdadero (carece de IDF global y saturacion TF) pero aproxima comportamiento BM25 y es suficiente para corpus <100K documentos.

### 2.2 Indices coexisten sin conflicto

```sql
CREATE INDEX idx_embedding_hnsw ON chunks
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 128);

CREATE INDEX idx_fts_gin ON chunks
  USING gin (search_vector);
```

Ambos indices PostgreSQL estandar. Participan en WAL, replicacion, backup. RLS multi-tenant funciona nativamente porque ambos usan tabla subyacente.

**Recomendacion sobre tsvector:** usar columna **GENERATED ALWAYS** (`GENERATED ALWAYS AS (to_tsvector(...)) STORED`) por simplicidad y RLS-friendly. Overhead storage ~0.3-0.5x texto original. Aceptable para corpus <1M chunks.

### 2.3 RRF (k=60) es default produccion 2025-2026

| Metodo | Cuando usar | Tuning | Robustez |
|---|---|---|---|
| **RRF** | Default. Sin datos etiquetados | Minimo (solo k) | Alta. Ignora escalas score |
| **Weighted alpha** | Control fino, datasets etiquetados | Alto (alpha por query type) | Media. Requiere normalizacion |

**RRF k=60 valido para B2B LATAM espanol/portugues.** k=60 no depende del idioma. Factor critico es **tokenizacion**: usar `to_tsvector('spanish', ...)` o `to_tsvector('portuguese', ...)` (stemming + stopwords nativos). Para queries con terminos tecnicos (ej. "Marluvas 50S5BR"), usar `to_tsvector('simple', ...)` para preservar tokens exactos, o concatenar multiples tsvectors.

**Implementar RRF a mano en Python (~15 lineas).** NO usar LlamaIndex `QueryFusionRetriever` ni LangChain `EnsembleRetriever` (P99 12.20s vs BM25 puro 1.86s en benchmarks RAG 2025). Abstracciones pesadas innecesarias.

### 2.4 Performance benchmark

| Dataset | Indice | p50 Query | p95 Query | QPS |
|---|---|---|---|---|
| 100K chunks | HNSW m=48, ef_search=200 | ~8.9 ms | ~16 ms | 171 |
| 1M chunks | HNSW m=48, ef_search=200 | ~16 ms | ~25 ms | 101 |
| 1M vectors (DiskANN/pgvectorscale) | DiskANN | ~179 ms p95 | -- | 22.9 |
| 138M passages BM25 (pg_textsearch) | -- | 40.6 ms p50 weighted | -- | 198.7 TPS |

**Para FaberLoom** (corpus 10K-100K chunks MVP): p50 <10ms, p95 <20ms con HNSW m=16, ef_construction=128. RLS overhead ~20% (3-5ms -> 5-6ms). Aceptable.

### 2.5 Costo mantenimiento BM25

| Componente | Tamano relativo |
|---|---|
| Tabla base (texto + metadata) | 1x baseline |
| Columna tsvector generada | ~0.3-0.5x del texto |
| Indice GIN sobre tsvector | ~0.3-0.5x del tamano tabla |
| Indice HNSW sobre vector | ~2-5x del tamano vectores |

**Indice full-text es significativamente mas pequeno que indice HNSW.** Storage dominante es vector index.

GIN actualizacion incremental con `fastupdate=ON` (default). Cada N inserciones spike de latencia escritura cuando pending list >4MB. Tunning: ajustar `gin_pending_list_limit` y autovacuum.

## 3. Casos production citados

| Empresa | Caso | Metrica reportada |
|---|---|---|
| **lpossamai** (SaaS B2B 2026) | Pure vector -> hybrid (pgvector + tsvector + RRF) | Retrieval precision: **62% -> 84%** (+22pp). Exact-match: "Unreliable -> Near-perfect". Zero new infra |
| **TigerData** (Postgres cloud) | pg_textsearch BM25 vs ParadeDB/Tantivy | 2.4x-6.5x mas rapido queries cortas. 8.7x throughput concurrente. 138M docs <18min |
| **VectorChord** | vchord_bm25 vs Elasticsearch | 3x QPS promedio. NDCG@10 comparable BEIR datasets |
| **SoftwareSeni** (consultora 2026) | Migracion ES -> Postgres BM25 + RRF | "20-1000x mejora query latency". RLS automatica |
| **AI Multiple** (benchmark) | Hybrid vs Dense-only | MRR +18.5% (0.410 -> 0.486). Recall@5 +7.2%. Latencia +201ms (+24.5%) |
| **Starmorph** (benchmark RAG) | Hybrid + reranking | "25-40% precision improvement vs naive RAG" |
| **AWS re:Invent DAT409** | Aurora PG + pgvector hybrid + RLS persona-based | RRF vs weighted comparado. Cohere Rerank vs RRF |
| **GitLab** | GIN pending list overhead | Cada 2.7s pending list lleno horas pico. Cleanup 465ms-3155ms |

**Caso mas cercano:** lpossamai con pgvector + tsvector + RRF en Postgres. Mejora 62%->84% directamente aplicable a queries B2B calzado seguridad ("Marluvas 50S5BR" tipo SKU).

## 4. Recomendacion directa

### Lo que SI implementar (Phase 1, MVP)

1. **Schema hibrido en Supabase:**

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
CREATE INDEX idx_chunks_tenant ON chunks(tenant_id);
```

2. **RRF Python async (~15 lineas):**

```python
def rrf_fuse(rank_lists: list[list[UUID]], k: int = 60, top_n: int = 10) -> list[UUID]:
    scores: dict[UUID, float] = {}
    for ranks in rank_lists:
        for rank, doc_id in enumerate(ranks, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)[:top_n]
```

3. **Query dual con asyncpg paralelo:** `asyncio.gather` BM25 + vector. Latencia dominante = generacion embedding (~50-200ms). Postgres queries paralelas anaden <1ms vs single query.

### Lo que NO implementar (ahora)

1. NO `pg_textsearch` o `pg_search` (requieren self-host fuera Supabase)
2. NO `rank_bm25` puro Python (4.46 QPS lento)
3. NO `bm25s` (innecesario si tenemos Postgres FTS, duplica storage)
4. NO LlamaIndex `QueryFusionRetriever` (abstraccion pesada SQL-incompatible)
5. NO LangChain `EnsembleRetriever` (P99 12.20s benchmark RAG 2025)
6. NO weighted alpha en MVP (RRF no requiere calibracion)

### Lo que diferir (post-MVP)

1. **Migracion a `pg_textsearch` o `pg_search`** cuando corpus >50K chunks o ranking insuficiente
2. **Calibracion alpha por tipo query** (Phase 3+) con dataset eval 50-200 queries
3. **Particionamiento por tenant** (`PARTITION BY LIST(tenant_id)`) o indices parciales HNSW para tier $2499/mes con >100K chunks/tenant
4. **DiskANN/pgvectorscale** si latencia HNSW insuficiente

## 5. Gotchas y riesgos

1. **Filtro tenant_id ANTES del ranking.** Con pgvector 0.8.0+ usar `hnsw.iterative_scan = relaxed_order` para que indice siga escaneando hasta encontrar suficientes resultados del tenant.

2. **Tokenizer espanol/portugues stemming agresivo.** Para SKUs/marcas usar `to_tsvector('simple', ...)` o concatenar multiples tsvectors. Riesgo: query "Marluvas" sin stemming pierde "marluv".

3. **GIN pending list overhead spikes** en escritura concurrente alta. Tunning: `gin_pending_list_limit` y autovacuum mas agresivo.

4. **RRF k=60 robusto pero no perfecto.** Para queries muy especificas (SKUs exactos), considerar boost manual al BM25 score post-RRF.

5. **Latencia embedding domina total.** Optimizaciones de Postgres queries solo aportan si embedding ya esta cacheado (mismo query texto).

## 6. Costo estimado

| Componente | Costo MVP (1 tenant 100 q/dia) | Costo escala (100 tenants) |
|---|---|---|
| Storage tsvector (overhead +0.3-0.5x texto) | $0 (dentro tier Supabase actual) | $0 |
| Indice GIN | $0 (dentro tier Supabase actual) | $0 |
| Latencia adicional (paralelo) | <1ms vs single query | <1ms |
| Embedding generation | Ya costo existente | Ya costo existente |
| **Costo NETO Phase 1** | **$0** | **$0** |

**Costo dominante = tiempo dev: 2-3 dias para implementar componente C7 + tests.**

## 7. Impacto en SPEC_FB_RAG_SECURITY_FIREWALL_v1

Bumpear a **v1.1** agregando:

- **Componente C7: Hybrid Retrieval** entre C4 (Retrieval Policy) y C5 (Output Firewall)
- C7 corre DESPUES de filtros de C4 (max_instruction_risk, exclude_quarantined)
- Output de C7 es `ranked_chunks_top_k` que entra al prompt
- Tests adicionales en CONTRACT_TEST_HARNESS para C7 (no requiere fixtures nuevos red-team, los 26 actuales aplican)

## 8. Decisiones que cierran

- ts_rank_cd como aproximacion BM25 valida para MVP
- RRF k=60 default sin calibracion en MVP
- RRF Python a mano, no abstracciones
- Schema hibrido en chunks table (append columnas, FROZEN-compatible)
- Diferir extensiones BM25 verdaderas a post-MVP

## 9. Sources

Research bruto completo en: `docs/anexos/kimi_swarm_6/research/mwt_swarm6_d1.md` (610 lineas).

8+ casos production citados, 50+ referencias web verificadas.

---

**Fin del documento.**
