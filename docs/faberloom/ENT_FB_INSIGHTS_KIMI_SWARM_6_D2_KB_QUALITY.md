# ENT_FB_INSIGHTS_KIMI_SWARM_6_D2_KB_QUALITY -- KB Quality Monitoring continuo

---
id: ENT_FB_INSIGHTS_KIMI_SWARM_6_D2_KB_QUALITY
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: ENT
stamp: VIGENTE -- 2026-05-07
fecha: 2026-05-07
agente: Kimi K2.6 multi-agente D2 (research) + Cowork (sintesis indexada) + CEO (decisiones)
aplica_a: [FaberLoom, MWT]
relacionado_con:
  - SPEC_FB_CONTRACT_TEST_HARNESS_v1.md (snapshot tests, no continuo)
  - POL_AI_GOV_FINAL_OUTPUT_QUALITY.md (Final Pass Premium)
  - SPEC_FB_RAG_SECURITY_FIREWALL_v1.md (firewall_ruleset_hash drift)
  - ENT_FB_USER_LEARNING_MODEL_v1.md (signals usuario como senal calidad)
  - SPEC_FB_KB_QUALITY_MONITORING_v1 (PENDIENTE crear)
origen: |
  Kimi Swarm #6 D2 ejecutado 2026-05-07. 8+ casos production citados.
  Research bruto: docs/anexos/kimi_swarm_6/research/mwt_swarm6_d2.md (452 lineas).
  Disparado por gap: SPEC_FB_CONTRACT_TEST_HARNESS cubre fixtures
  pero NO eval continuo en produccion. Decision pendiente: MVP vs deuda.
---

## 1. Decision principal

**DEFERRED DeepEval + TruLens a Fase 2 (post-MVP, ~2026-07).** Plan B en MVP: **Langfuse datasets + freshness audit ARQ daily + drift sentinel ARQ monthly + user feedback via draft-first**.

Razon: equipos 1-3 devs reportan **15-25% tiempo dev** en mantenimiento de DeepEval+TruLens primeros 6 meses. Innecesario para MVP single-agent con 1 tenant validador (MWT).

Plan B cubre cobertura minima viable a costo despreciable (~$0.20/mes/tenant).

## 2. Hallazgos clave

### 2.1 DeepEval y TruLens NO reemplazan Langfuse

| Framework | Brilla en | Carencias |
|---|---|---|
| **DeepEval** | CI/CD pytest-native. 14+ metricas. 4 core: AnswerRelevancy, Faithfulness, ContextualPrecision, ContextualRecall | NO es sistema observabilidad. ContextualPrecisionMetric sin ground-truth se degrada silenciosamente |
| **TruLens** | Tracing OTel + RAG Triad (context relevance, groundedness, answer relevance) | SQLite default no escala >10K evals (migrar PostgreSQL) |
| **Langfuse** | Observabilidad produccion. Datasets golden questions. LLM-as-judge nativo | Menos metricas pre-built que DeepEval, pero suficientes para MVP |

**Costo LLM judge:** $0.01-$0.10 por evaluacion segun modelo. **GPT-4o-mini ($0.15/$0.60 por 1M tokens) o Claude Haiku 4.5 ($1/$5 por 1M tokens) reducen costos 60-80%** con "modest accuracy loss".

DeepEval suite 4-metric con GPT-4o cuesta $0.02-$0.04 por muestra.

### 2.2 Riesgo principal NO es costo, es sobrecarga operativa

Equipos 1-3 devs reportan 15-25% tiempo dev mantenimiento DeepEval+TruLens primeros 6 meses. Para MVP FaberLoom (Foundation Beta 8 semanas), esto es **inaceptable**.

### 2.3 Freshness y embedding drift se resuelven simple

| Tipo documento | Threshold staleness recomendado |
|---|---|
| Lista precios | **7 dias** |
| Fichas tecnicas | **30 dias** |
| Normativas estables | **90 dias** |

NO usar default generico 30 dias. Calibrar por tipo.

**Embedding drift threshold:** 0.08 cosine distance (no 0.10 default). Mas conservador para B2B con datos sensibles.

### 2.4 Tensiones con TruLens + Langfuse

Ambos hacen tracing. Instrumentar ambos en mismo pipeline genera duplicacion spans y confusion. Elegir **uno como source of truth para traces (Langfuse)** y otro solo para feedback functions (TruLens) si se decide usar.

## 3. Casos production citados

| Empresa | Caso | Metrica reportada |
|---|---|---|
| **Stratagem Systems** | 89 deployments RAG production | Small-scale RAG total initial: $7,500-$13,200. Monthly ongoing: $650-$1,750 |
| **Snowflake** | TruLens + Cortex Search RAG internal | RAG Triad evals con Mistral Large |
| **Equinix / Tribble / KBC Group** | TruLens en produccion | OTel-based tracing + eval |
| **JPMorgan Chase** | Galileo customer support RAG | Hallucination prevention, compliance audit trails |
| **OpenAI/Google/Microsoft** | Usuarios DeepEval | 20M evaluaciones/dia, 3M downloads/mes |
| **Prem / RisingWave** | Streaming RAG vs Batch RAG | 100x diferencia costo embedding. 1% docs cambian diariamente |
| **Cloudflare edge RAG** | RAG $5-$10/mes (vs $130-$190 tradicional) | 10K searches/mes |
| **Milvus / Zilliz** | Embedding drift detection | Cosine distance 0.05-0.10 para delta scoring |

## 4. Recomendacion directa

### Lo que SI implementar en MVP (Foundation Beta)

1. **Langfuse datasets + evaluacion manual periodica:**
   - Dataset 50-100 preguntas representativas (golden questions) dominio calzado seguridad
   - Evaluacion LLM-as-judge via Langfuse nativo 1 vez/semana (manual o ARQ job)
   - Setup: ~4 horas. Mantenimiento: 30 min/semana

2. **Freshness audit pipeline (ARQ daily):**
   - Extender chunk metadata con `content_hash`, `last_embedded_at`, `source_modified_at`, `document_type` (price_list / tech_spec / normative / catalog)
   - Job diario compara `source_modified_at > last_embedded_at` y encola re-embed
   - Thresholds: 7d precios, 30d fichas tecnicas, 90d normativas

3. **Embedding drift sentinel (ARQ monthly):**
   - Job mensual samplea 5% chunks
   - Recalcula embeddings con modelo actual
   - Compara cosine distance vs threshold 0.08
   - Si supera, marca `requires_rescan = TRUE`
   - Comparte infra con freshness audit

4. **User feedback como senal calidad:**
   - Draft-first invariante (P3) ya permite usuario corregir proformas
   - Edicion vs aceptacion directa = metrica calidad KB mas valiosa que LLM-judge abstracto
   - Tipificar correcciones: tone / data / structure / policy / scope / context (P6 ARCH)

### Lo que NO implementar en MVP

1. NO **DeepEval pytest suite** (calibracion thresholds + mantenimiento golden datasets innecesario)
2. NO **TruLens feedback functions** (Langfuse cubre tracing; Ragas integrado si se necesitan metricas RAG especificas)
3. NO **Confident AI cloud** ($19.99-$49.99/seat/mes innecesario MVP)
4. NO **evaluacion online por cada query** (latencia + costo sin beneficio proporcional)

### Lo que diferir a Fase 2 (post-MVP, ~2026-07)

1. **DeepEval pytest suite en CI/CD:** integrar `deepeval test run` con golden dataset versionado. Bloquear deploys si faithfulness < 0.80
2. **TruLens feedback functions:** si regressions retrieval no explicables por Langfuse
3. **Automated LLM-as-judge 100%:** cuando volumen lo justifique (>500 queries/dia/tenant)

## 5. Costo proyectado (Plan B MVP)

| Componente | 1 tenant (100 q/dia) | 10 tenants | 100 tenants |
|---|---|---|---|
| Langfuse self-host | $0 (Railway/Fly ya pagado) | $0 | $0 |
| ARQ worker eval job | $0 (compartido cola async) | $0 | $0 |
| LLM judge (5% sample, GPT-4o-mini) | ~$0.08/mes | ~$0.80/mes | ~$8/mes |
| Freshness audit job | $0 (logica FastAPI + ARQ) | $0 | $0 |
| Delta scoring job | $0 (embeddings batch existente) | $0 | $0 |
| Embedding reindex (mensual, 1% corpus) | ~$0.10 (OpenAI 3-small batch) | ~$1 | ~$10 |
| PostgreSQL storage (Supabase) | $0 (dentro tier actual) | $0 | $0 |
| **TOTAL monitoring calidad** | **~$0.20/mes** | **~$2/mes** | **~$20/mes** |
| **MRR estimado (Pro tier $59-89)** | $59-$89 | $590-$890 | $5,900-$8,900 |
| **% MRR en monitoring** | **0.2-0.3%** | **0.2-0.3%** | **0.2-0.3%** |

Costo despreciable vs MRR objetivo. Si se usa GPT-4o como judge y 100% queries evaluadas, multiplicar x20-x100.

## 6. Gotchas y riesgos

1. **Judge model drift:** cambiar modelo juez (GPT-4o -> Claude Sonnet) invalida comparaciones historicas. Documentar "pin the judge version".

2. **Threshold re-calibration:** thresholds desarrollo fallan en produccion porque distribucion dominio difiere. Re-baseline despues de 2 semanas en produccion.

3. **Staleness no es siempre bug:** usuario preguntando norma 2018 puede querer esa norma, no la ultima. Threshold debe considerar intencion usuario, no solo timestamp.

4. **Embedding reindex cost cliff:** re-embed 50K documentos con overlap puede costar $2,000+ sin batch API o modelo small.

5. **TruLens SQLite no escala:** dashboard default usa SQLite. Para >10K evaluaciones, migrar PostgreSQL.

6. **Sampling bias:** evaluar solo 5% trafico puede omitir edge cases criticos. Estratificar sample por tipo query (price, normative, availability).

7. **DeepEval ContextualPrecisionMetric sin ground-truth:** se degrada silenciosamente a "LLM adivina que contexto deberia haber sido". Para RAG work, preferir Ragas context precision.

## 7. SPEC propuesto: SPEC_FB_KB_QUALITY_MONITORING_v1

Status: **DRAFT** pendiente generar.

### Scope minimo viable

1. Freshness Monitoring (ARQ daily)
2. Embedding Drift Sentinel (ARQ monthly)
3. Langfuse Quality Scoring (semanal manual + golden dataset)
4. Alertas (severidad gradual: low/medium/high/critical)
5. Deuda tecnica documentada (DeepEval/TruLens diferidos a Fase 2)

## 8. Diagrama integracion stack FaberLoom

```
WhatsApp -> FastAPI + Pydantic AI -> LiteLLM
                |
                +-- Supabase pgvector + RLS
                +-- Redis + ARQ worker
                +-- Letta self-host memory
                |
                v
        Langfuse (self-host)
          |
          +-- Traces (all req)
          +-- Datasets (golden QA, 50-100 preguntas)
          +-- Scores (manual/batch eval LLM judge GPT-4o-mini 5% sample)

ARQ Workers:
  - freshness_audit (daily)
  - drift_sentinel (monthly)
  - llm_judge_sample (daily, 5% trafico)
```

## 9. Decisiones que cierran

- DeepEval/TruLens DEFERRED a Fase 2 (post-MVP)
- Plan B Langfuse + ARQ jobs cubre cobertura minima viable MVP
- Threshold staleness por tipo doc: 7d/30d/90d
- Threshold drift cosine: 0.08 (no 0.10 default)
- LLM judge GPT-4o-mini 5% sample default
- User feedback (draft-first) es senal calidad mas valiosa que LLM-judge abstracto

## 10. Sources

Research bruto completo en: `docs/anexos/kimi_swarm_6/research/mwt_swarm6_d2.md` (452 lineas).

8+ casos production citados, 60+ referencias web verificadas.

---

**Fin del documento.**
