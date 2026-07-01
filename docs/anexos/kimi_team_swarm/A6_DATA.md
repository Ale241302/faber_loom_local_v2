## A6_DATA — Data / lakehouse / streaming / vector DB

### Estado del arte 2026
| # | Práctica SOTA | Trade-off clave | Confianza |
|---|---|---|---|
| 1 | **Iceberg** default | Engine-agnostic; Delta=lock-in [^78^] | [HIGH] |
| 2 | **Kafka+Debezium** | Audit tenant_id; Redpanda drop-in [^82^] | [HIGH] |
| 3 | **dbt** SOTA SQLMesh challenger | 45K orgs. 9x faster [^79^] | [HIGH] |

### Tendencias 2026–2028 (señal vs ruido)
| Tendencia | S/R | Razón | Confianza |
|---|---|---|---|
| Lakehouse obligatorio todo SaaS | Ruido | <1TB/día Postgres OK [^100^] | [HIGH] |
| AE separado | Señal | DE=infra AE=modelado [^74^] | [HIGH] |
| pgvector reemplaza vector DB | Ruido | OK <10M [^70^] | [HIGH] |

### Stack/herramientas SOTA top 3
| Herramienta | Uso | Trade-off | LATAM-readiness | Confianza |
|---|---|---|---|---|
| **Iceberg+DuckDB** | Lakehouse warm/cold | Compaction manual S3/MinIO | Alta OSS [^98^] | [HIGH] |
| **Kafka+Debezium** | Streaming CDC | Ops lee WAL sin carga [^101^] | Alta low cost | [HIGH] |
| **dbt Core/Cloud** | Transform analytics | Full-refresh caro [^79^] | Alta hiring LATAM | [HIGH] |

### Bloque A — Roles SOTA
| Rol | Seniority | Scope | Sep/Cap | Confianza |
|---|---|---|---|---|
| Data Engineer | Mid-Sr | Pipelines CDC | **Separado** | [HIGH] |
| Analytics Engineer | Mid-Sr | dbt modelado | **Separado** | [HIGH] |
| Vector DB / AI Infra | Sr | pgvector RAG | **Cap. AI/ML** | [MEDIA] |

### Bloque B — Competencias transversales
1. **CDC sourcing** — WAL lag idempotency eval Debezium [HIGH]
2. **Vector search** — HNSW tuning eval pgvector vs Qdrant [HIGH]
3. **Incremental** — dbt pruning eval -30% compute 90d [HIGH]

### Anti-patterns 2026 + KPIs
| Anti-pattern | Por qué murió | KPI/SLO reemplazo |
|---|---|---|
| Batch nocturno | Stale no escala [^101^] | CDC <1s p99 |
| Pinecone sin pgvector | Lock-in 10x <10M [^70^] | pgvector p95 <50ms |
| DE haciendo BI | Cuello [^88^] | AE:DE=1:1 |
