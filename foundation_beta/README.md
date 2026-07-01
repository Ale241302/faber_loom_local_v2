# Foundation Beta — M16 Tenant Isolation

Base funcional de aislamiento multi-tenant para FaberLoom Foundation Beta.
Implementa las 7 capas de aislamiento requeridas por `SPEC_FB_FUNC_M16_TENANT_ISOLATION_v1`.

## Estructura

```
foundation_beta/
├── infra/
│   ├── docker-compose.yml          # postgres (pgvector), redis, minio, litellm, letta
│   ├── .env.example                # variables de entorno
│   └── init/
│       └── 01-enable-pgvector.sql  # CREATE EXTENSION IF NOT EXISTS vector;
├── backend/
│   ├── requirements.txt            # dependencias Django/DRF/Celery/Redis/MinIO
│   ├── manage.py
│   └── faberloom/                  # settings, urls, wsgi, celery app
│   └── apps/
│       ├── core/                   # tenant_context, redis_client, storage, vector, llm, memory, middleware, SampleItem, KBEmbedding
│       └── tenants/                # Tenant, TenantPlanFeatures, init_rls
├── tests/
│   ├── test_m16_unit.py            # tests puros sin servicios
│   └── test_m16_tenant_isolation.py # 5 tests cross-tenant
```

## Requisitos

- Python 3.11–3.13
- Docker + Docker Compose (para servicios de infra)
- Windows, Linux o macOS

## Levantar servicios

```bash
cd foundation_beta/infra
cp .env.example .env
# Edita .env con tus credenciales (valores por defecto funcionan en local)
docker compose up -d
```

Servicios expuestos:
- PostgreSQL 16 + pgvector: `localhost:5432`
- Redis: `localhost:6379`
- MinIO API: `localhost:9000`, consola: `localhost:9001`
- LiteLLM: `localhost:4000`
- Letta: `localhost:8283`

## Configurar backend

```bash
cd foundation_beta/backend
python -m venv ../.venv
source ../.venv/Scripts/activate  # Windows
# source ../.venv/bin/activate    # Linux/macOS
pip install -r requirements.txt
```

## Migraciones y RLS

```bash
cd foundation_beta/backend
source ../.venv/Scripts/activate
python manage.py migrate
python manage.py init_rls
```

`init_rls` aplica `ENABLE ROW LEVEL SECURITY` + `FORCE` + policies solo a tablas que tengan columna `tenant_id`.

## Correr tests

### Tests unitarios puros (no requieren servicios)

```bash
cd foundation_beta
source .venv/Scripts/activate
PYTHONPATH=backend python -m pytest tests/test_m16_unit.py -p no:django
```

### Tests cross-tenant (requieren PostgreSQL + Redis)

```bash
cd foundation_beta
source .venv/Scripts/activate
PYTHONPATH=backend python -m pytest tests/test_m16_tenant_isolation.py
```

### Todos los tests

```bash
cd foundation_beta
source .venv/Scripts/activate
PYTHONPATH=backend python -m pytest
```

## Decisiones de arquitectura

Ver `DECISIONS.md`.

## Notas de seguridad

- `TenantMiddleware` solo acepta `X-Tenant-Id` en modo `TESTING`.
- En producción el `tenant_id` fluye por sesión server-side (M08).
- RLS usa `FORCE ROW LEVEL SECURITY` para que incluso el owner de la tabla esté sujeto a policies.
- Las policies usan `NULLIF(current_setting('app.tenant_id', true), '')::UUID` para fallar cerrado cuando no hay contexto.
- Celery `TenantTask` ejecuta `DISCARD ALL` en `finally` para evitar tenant stale entre jobs.
