# M16 Tenant Isolation — Plan de Implementación

## 1. Resumen ejecutivo

M16 es el fundamento del SPINE de Foundation Beta.  Garantiza que ningún tenant lee, escribe, procesa ni expone datos de otro tenant en las 7 capas de datos: PostgreSQL RLS, Redis, Celery, MinIO, pgvector, LiteLLM y Letta.  Sin M16 no puede arrancar ningún otro módulo operativo.

**Rol en el SPINE:** provee el `tenant_context` y las reglas de aislamiento que consumen M08 (sesión), M09 (permisos), M15 (eventing), M12 (audit), M11 (policy) y M07 (bootstrap).

## 2. Entrada/salida

### Entrada
- Ninguna del punto de vista funcional; es infraestructura base.
- Requiere el stack Postgres + Redis + MinIO + pgvector + LiteLLM + Letta desplegado.

### Salida
- `TenantContext` utility: `set_db_tenant(tenant_id)`, `clear_db_tenant()`, `current_tenant_id()`.
- Redis key prefix validator.
- Celery base task `TenantTask` con `with_tenant_session`.
- MinIO path builder `tenant_path(tenant_id, *segments)`.
- pgvector partition helper.
- LiteLLM metadata tagger.
- Letta namespace builder.
- 5 tests cross-tenant verdes en CI.

## 3. Modelo de datos

### Tablas nuevas / modificadas

Toda tabla tenant-scoped existente (workspace, chat, message, draft, routine, routine_run, usage_record, kb_source, kb_chunk, kb_fact, mail_message, mail_outbox, email_account, gold_candidate, audit_log, editorial_history, outbox, event_log) se migra a PostgreSQL con:

```sql
ALTER TABLE <tabla> ALTER COLUMN tenant_id SET NOT NULL;
CREATE INDEX idx_<tabla>_tenant_id ON <tabla>(tenant_id);
```

Para tablas nuevas de Foundation Beta:

```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    legal_name TEXT NOT NULL,
    commercial_name TEXT,
    vertical_spec_object_id TEXT NOT NULL,
    plan_tier TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('setup','active','suspended','cancelled')),
    config_json JSONB NOT NULL DEFAULT '{}',
    dpa_state TEXT NOT NULL DEFAULT 'missing' CHECK (dpa_state IN ('missing','signed','blocked')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE tenant_plan_features (
    tenant_id UUID PRIMARY KEY REFERENCES tenants(id) ON DELETE CASCADE,
    data_class_ceiling TEXT NOT NULL DEFAULT 'N2',
    max_seats INTEGER NOT NULL DEFAULT 2,
    allow_agent_composition BOOLEAN NOT NULL DEFAULT FALSE,
    allow_tools_in_skills BOOLEAN NOT NULL DEFAULT FALSE,
    allow_email_connector BOOLEAN NOT NULL DEFAULT FALSE,
    allow_whatsapp_connector BOOLEAN NOT NULL DEFAULT FALSE
);
```

### RLS policies

```sql
ALTER TABLE <tabla> ENABLE ROW LEVEL SECURITY;
ALTER TABLE <tabla> FORCE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_<tabla> ON <tabla>
    USING (tenant_id = current_setting('app.tenant_id', true)::UUID);
```

> `app.tenant_id` se setea con `SET LOCAL` dentro de `transaction.atomic()`.

### Índices
- `idx_<tabla>_tenant_id` en toda tabla aislable.
- `idx_tenants_slug`, `idx_tenants_status`.
- `idx_tenant_plan_features_tenant_id`.

### ENUMs
- `tenant_status`: setup, active, suspended, cancelled.
- `dpa_state`: missing, signed, blocked.
- `data_class`: N0, N1, N2, N3, N4 (reutilizado en M11).

## 4. Cambios en API/backend

### Middleware
- `TenantMiddleware`: extrae `tenant_id` de la sesión server-side (M08) y ejecuta `SET LOCAL app.tenant_id = '<uuid>'` en la conexión Django.
- No aceptar `tenant_id` desde headers del cliente salvo en modo `TESTING` con fixture explícita.

### Helpers
```python
# apps/core/tenant_context.py
from contextvars import ContextVar

tenant_ctx: ContextVar[UUID | None] = ContextVar("tenant_id", default=None)

def set_db_tenant(tenant_id: UUID) -> None:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SET LOCAL app.tenant_id = %s", [str(tenant_id)])
    tenant_ctx.set(tenant_id)

def clear_db_tenant() -> None:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("DISCARD ALL")
    tenant_ctx.set(None)

def current_tenant_id() -> UUID | None:
    return tenant_ctx.get()
```

### Redis
```python
# apps/core/redis.py
from django.conf import settings

def tenant_key(tenant_id: UUID, suffix: str) -> str:
    return f"tenant:{tenant_id}:{suffix}"

def require_tenant_prefix(key: str, tenant_id: UUID) -> None:
    prefix = f"tenant:{tenant_id}:"
    if not key.startswith(prefix):
        raise ValueError(f"Redis key must start with {prefix}")
```

### Celery
```python
# apps/core/celery.py
from celery import Task

class TenantTask(Task):
    def __call__(self, *args, **kwargs):
        tenant_id = kwargs.pop("_tenant_id", None)
        if tenant_id is None:
            raise ValueError("Celery task missing _tenant_id")
        from apps.core.tenant_context import set_db_tenant, clear_db_tenant
        set_db_tenant(tenant_id)
        try:
            return super().__call__(*args, **kwargs)
        finally:
            clear_db_tenant()
```

### MinIO
```python
# apps/core/storage.py
from pathlib import PurePosixPath

SAFE_RE = re.compile(r"^[a-zA-Z0-9_\-\.]+$")

def tenant_path(tenant_id: UUID, *segments: str) -> str:
    for s in segments:
        if ".." in s or not SAFE_RE.match(s):
            raise ValueError("Invalid storage path segment")
    return str(PurePosixPath("/tenants", str(tenant_id), *segments))
```

### pgvector
- Crear tabla `kb_embedding` particionada por `tenant_id` con `pgvector`.
- HNSW index por partición, no global.
- Query helper siempre filtra `tenant_id` antes del vector scan.

### LiteLLM
- Cada request incluye `metadata={"tenant_id": str(tenant_id)}`.
- Logs de LiteLLM filtrables por `tenant_id`.

### Letta
- Namespace: `mem:tenant:{tenant_id}:agent:{agent_id}:task:{task_id}:working`.
- Helper `letta_namespace(tenant_id, agent_id, task_id=None, kind="working")`.

## 5. Cambios en frontend

Ninguno directo.  El aislamiento es transparente.  La UI solo consume sesión (M08) y eventos (M15) de su tenant.

## 6. Cambios en infraestructura/deploy

### Docker Compose

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: faberloom
      POSTGRES_USER: faberloom_app
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U faberloom_app -d faberloom"]

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
    volumes:
      - minio_data:/data

  letta:
    image: letta/letta:latest
    environment:
      LETTA_PG_URI: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/faberloom
    depends_on:
      - postgres

  litellm:
    image: ghcr.io/berriai/litellm:latest
    command: --config /app/config.yaml
    volumes:
      - ./litellm_config.yaml:/app/config.yaml:ro
    environment:
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}

  web:
    build: ./backend
    command: gunicorn config.wsgi:application -b 0.0.0.0:8000
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/faberloom
      REDIS_URL: redis://redis:6379/0
      MINIO_ENDPOINT: minio:9000
      MINIO_ACCESS_KEY: ${MINIO_ROOT_USER}
      MINIO_SECRET_KEY: ${MINIO_ROOT_PASSWORD}
      LITELLM_URL: http://litellm:4000
      LETTA_URL: http://letta:8283
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started

  celery:
    build: ./backend
    command: celery -A config worker -l info
    environment: *web_env
    depends_on:
      - redis
      - postgres

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

### Variables de entorno
```bash
POSTGRES_PASSWORD=
MINIO_ROOT_USER=
MINIO_ROOT_PASSWORD=
ANTHROPIC_API_KEY=
DJANGO_SECRET_KEY=
REDIS_URL=
LITELLM_URL=
LETTA_URL=
```

### Migraciones
1. `python manage.py migrate` crea tablas base.
2. Script `migrations/0002_enable_rls.py` ejecuta `ENABLE ROW LEVEL SECURITY` + `FORCE` + policies.
3. Script `migrations/0003_create_partitions.py` crea particiones pgvector por tenant.

## 7. Secuencia de tareas

1. **Infra local:** levantar Postgres 16 + pgvector, Redis 7, MinIO, Letta, LiteLLM vía `docker-compose.yml`.
2. **Proyecto Django:** crear proyecto `foundation/` con Django 4.2, DRF, psycopg, django-redis, celery.
3. **Modelo `Tenant`:** crear `tenants` + `tenant_plan_features`.
4. **Middleware tenant:** implementar `TenantMiddleware` con `SET LOCAL app.tenant_id`.
5. **RLS:** crear migración que habilite y fuerce RLS en todas las tablas aislables.
6. **Redis prefix:** implementar helpers y linter.
7. **Celery wrapper:** crear `TenantTask` y usarla en todos los tasks.
8. **MinIO path builder:** implementar y testear anti path-traversal.
9. **pgvector partition:** diseñar `kb_embedding` particionada e índices HNSW por tenant.
10. **LiteLLM metadata:** asegurar que cada request taguea `tenant_id`.
11. **Letta namespace:** implementar builder y validar cross-profile bloqueado.
12. **Tests cross-tenant:** escribir los 5 tests obligatorios.
13. **CI:** integrar tests en pipeline; fallo = bloqueo de merge.

## 8. Criterios de aceptación

1. `test_postgres_rls_same_worker_tenant_a_then_b_no_cross_read`: mismo proceso Django/Celery ejecuta A y luego B; B no ve filas de A.
2. `test_celery_with_tenant_session_clears_context_after_exception`: job A falla; job B posterior no hereda `app.tenant_id`.
3. `test_redis_stream_and_cache_keys_require_tenant_prefix`: cualquier key sin `tenant:{tenant_id}:` falla lint/runtime.
4. `test_pgvector_n2_plus_uses_tenant_partition_not_global_hnsw`: `EXPLAIN` muestra partition pruning antes del vector scan.
5. `test_letta_namespace_blocks_cross_tenant_profile_access`: agente A no lista/inyecta memoria de B.
6. Cobertura de RLS ≥95% de tablas aislables.
7. Ningún endpoint autenticado funciona sin `tenant_id` server-side.

## 9. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| RLS deshabilitado por config | P0 leak | `FORCE ROW LEVEL SECURITY` + tests CI |
| Celery hereda tenant_id | P0 leak | `DISCARD ALL` + wrapper + tests A→B |
| Redis key sin prefix | P0 cache compartido | Linter + runtime check |
| MinIO path traversal | P0 datos cruzados | Validación de segmentos |
| pgvector global HNSW | P0 retrieval cross-tenant | Partición por tenant + `EXPLAIN` test |
| LiteLLM log bleed | P1 fuga de metadata | Tag `tenant_id` en cada call |
| Letta cross-profile | P0 memoria cruzada | Namespace estricto + test |

## 10. Decisiones de arquitectura tomadas

1. **Postgres RLS como source of truth.**  Toda query aislable falla cerrada si falta `app.tenant_id`.
2. **Tenant ID nunca via header en producción.**  Solo fluye por sesión server-side (M08).
3. **Partición pgvector para todo N2+.**  Simplifica operaciones y cumple M16 sin depender de umbral variable.
4. **Celery `TenantTask` base.**  Todo worker hereda de esta clase; tasks legacy se migran.
5. **Letta namespace rígido.**  Formato fijo para evitar concatenación accidental cross-tenant.

---
*Plan M16 — Foundation Beta v1.3.1*
