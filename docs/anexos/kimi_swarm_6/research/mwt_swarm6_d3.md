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
