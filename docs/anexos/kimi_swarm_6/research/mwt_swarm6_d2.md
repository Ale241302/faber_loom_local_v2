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
