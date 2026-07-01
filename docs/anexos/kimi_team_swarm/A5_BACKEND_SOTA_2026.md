## A5_BACKEND — Backend Python / FastAPI / async

### Estado del arte 2026
|Práctica/Framework|Fortaleza|Trade-off|Confianza|
|---|---|---|---|
|FastAPI v0.115+|Default greenfield, ecosistema AI/LLM, hiring amplio [^70^]|Pydantic hot-path overhead|[HIGH]|
|Litestar 2.x+|msgspec más rápido, DI limpio, typing estricto [^70^]|Comunidad pequeña, bus-factor|[HIGH]|
|Híbrido SQLAlchemy writes + asyncpg reads|SOTA 2026; ORM para transacciones, raw para lecturas hot [^73^]|Doble pool, complejidad operativa|[HIGH]|

### Tendencias 2026–2028
|Tendencia|Señal/Ruido|Razón|Confianza|
|---|---|---|---|
|Go/Rust reemplaza Python backend|Ruido|Python sigue dominando AI/B2B SaaS; Go solo para >10k RPS o p99<10ms [^80^][^84^]|[HIGH]|
|Temporal como worker default|Señal|Durable execution, audit trail nativo, retries automáticos; ideal HITL [^83^]|[MEDIA]|
|Pydantic AI reemplaza Instructor|Ruido|Instructor sigue líder extracción estructurada; Pydantic AI es agent framework Tier 2 [^79^]|[HIGH]|

### Stack/herramientas SOTA top 3
|Herramienta|Uso|Trade-off|LATAM-readiness|Confianza|
|---|---|---|---|---|
|FastAPI + Pydantic v2|APIs async, validación, OpenAPI|Overhead serialización|Alta (hiring, docs español)|[HIGH]|
|ARQ (Redis)|Background jobs async para FastAPI [^91^]|Sin workflow durable ni UI avanzada|Alta (simple, Redis en stack)|[HIGH]|
|PgBouncer tx mode + asyncpg|Pool multi-tenant RLS [^72^][^81^]|Requiere SET LOCAL por tx y disable prepared statements|Alta (KVM 8, Docker Compose)|[HIGH]|

### Bloque A — Roles SOTA
|Rol|Seniority|Scope|Separado/Capability|Justificación|Confianza|
|---|---|---|---|---|---|
|Platform Engineer (Python/Go)|Senior+|Pooling, multi-tenancy RLS, observability|Separado|Specialty engineering faltante en MWT|[HIGH]|
|AI Backend Engineer|Mid-Senior|LiteLLM, Pydantic AI, RAG pipelines|Capability dentro de Backend|Stack unificado Anthropic-only|[MEDIA]|
|Data/Worker Engineer|Senior|Temporal/ARQ, idempotencia, audit logs|Capability|Audit-heavy requiere durable execution|[HIGH]|

### Bloque B — Competencias transversales
1. **Async disciplinado**: evitar gather() sobre sessions SQLAlchemy; se evalúa con code review de greenlet leaks. [HIGH]
2. **RLS hardening**: SET LOCAL por transacción + NULLIF current_setting [^98^]; se evalúa con test de penetración por tenant. [HIGH]
3. **Hybrid SQL fluency**: leer EXPLAIN, decidir ORM vs raw por path; se evalúa con benchmark de endpoints reales. [HIGH]

### Anti-patterns 2026 + KPIs
|Anti-pattern|Por qué dejó de ser SOTA|KPI/SLO de reemplazo|
|---|---|---|
|Async SQLAlchemy para todo|Greenlet bridge 1.5–14× más lento; bulk inserts críticos [^73^]|<20% paths raw SQL; p95 lectura <50ms|
|Celery en nuevo proyecto|Sin async nativo, config pesada, result backend legacy|ARQ/Temporal según complejidad; startup worker <2s|
|Session pooling sin PgBouncer|Agotamiento conexiones Postgres en multi-tenant|Pool size ≤ cores×3; waiting clients = 0 [^92^]|
