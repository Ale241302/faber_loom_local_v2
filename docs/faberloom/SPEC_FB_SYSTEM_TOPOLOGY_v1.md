---
id: SPEC_FB_SYSTEM_TOPOLOGY_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma
type: spec
stamp: VIGENTE 2026-05-02
fecha: 2026-05-02
agente: Cowork (redaccion) + CEO (decisiones) + ChatGPT (auditoria R5)
aplica_a: [FaberLoom]
implementa: stack canonico de SPECs h+i
relacionado_con:
  - SPEC_FB_AUTH_TENANT_RBAC_v1
  - SPEC_FB_INTEGRATION_LAYER_v1
  - SPEC_FB_FRONTEND_REALTIME_STATE_v1
  - SPEC_FB_EVENTING_AND_OUTBOX_v1
  - SPEC_FB_TENANT_BOOTSTRAP_SEED_v1 (consume topology)
origen: ChatGPT R5 · "Topology debe ser mas operativo · cerrar 12 containers · networking · secrets · backups · reverse proxy · healthchecks"
---

# SPEC_FB_SYSTEM_TOPOLOGY_v1
## Plataforma · 12 containers Hostinger KVM 8

## 1. Proposito

Define el deployment fisico del FaberLoom Sprint 1. Sin esto, "el equipo va a implementar 'lo que entendio'" (R5).

R5 critical: este SPEC debe ser **operativo** (deploy commands · rollback · healthchecks · environment profiles) · NO solo conceptual.

## 2. Stack canonico (sealed por R5 + indexa-h)

| Pieza | Decision | Container |
|---|---|---|
| Reverse proxy / TLS | **Caddy** (preferido por automatic HTTPS) o Traefik | `reverse-proxy` |
| Frontend | Next.js App Router + TypeScript | `frontend` |
| Backend API | FastAPI + Pydantic v2 + SQLAlchemy/Alembic | `api` |
| Realtime | WebSocket gateway (puede fusionar con api Sprint 1) | `realtime` (opcional) |
| Workers default | Celery + Redis broker | `worker-default` |
| Workers agent | Celery dedicado LLM/agentes (cost/latency aislado) | `worker-agent` |
| Scheduler | Celery Beat | `scheduler` |
| DB primary | Postgres 16 + pgvector | `postgres` |
| Cache + Streams | Redis 7 | `redis` |
| LLM router | LiteLLM Proxy | `litellm` |
| Object storage | MinIO (evidence bundles · adjuntos) | `object-store` |
| Observability | Grafana + Loki + Prometheus minimo | `observability` |

R5 explicit prohibitions Sprint 1:
- ❌ Kubernetes (overkill 12 containers)
- ❌ Kafka (Redis Streams suficiente)
- ❌ Microservicios extras "por si acaso"
- ❌ IdP SaaS obligatorio (control + bajo costo · ver Auth SPEC)

## 3. Topologia 12 containers · Hostinger KVM 8

```
┌─────────────────────────────────────────────────────────────────────┐
│                      KVM 8 · Hostinger                              │
│                                                                      │
│  ┌──────────────────┐                                               │
│  │  reverse-proxy   │ Caddy / Traefik                               │
│  │  443 · 80        │ TLS auto · subdomain routing                  │
│  └────────┬─────────┘ {tenant}.faberloom.com                        │
│           │                                                          │
│  ┌────────┴─────────────┬────────────────────┐                      │
│  ↓                      ↓                    ↓                      │
│  ┌─────────┐  ┌─────────────┐  ┌──────────────────┐                │
│  │frontend │  │     api     │  │    realtime      │                │
│  │Next.js  │  │  FastAPI    │  │  WS gateway      │                │
│  │static   │  │  REST       │  │  (puede fusionar │                │
│  │build    │  │  + WS       │  │   con api v1)    │                │
│  └─────────┘  └──────┬──────┘  └─────────┬────────┘                │
│                      │                    │                         │
│         ┌────────────┼────────────────────┘                         │
│         ↓            ↓            ↓                                  │
│  ┌──────────┐  ┌──────────┐  ┌─────────────┐                        │
│  │ postgres │  │  redis   │  │  litellm    │                        │
│  │ + pgvec  │  │ + streams│  │  proxy      │                        │
│  └──────────┘  └──────┬───┘  └─────────────┘                        │
│                       │                                              │
│         ┌─────────────┼──────────────┐                               │
│         ↓             ↓              ↓                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐                   │
│  │worker-default│  │worker-agent  │  │scheduler │                   │
│  │  Celery      │  │  Celery LLM  │  │ Celery   │                   │
│  └──────────────┘  └──────────────┘  │ Beat     │                   │
│                                       └──────────┘                   │
│                                                                      │
│  ┌──────────────┐                  ┌────────────────┐               │
│  │ object-store │                  │  observability │               │
│  │   MinIO      │                  │  Loki/Promet/  │               │
│  │              │                  │  Grafana       │               │
│  └──────────────┘                  └────────────────┘               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

Network internal: faberloom-net (Docker Compose)
External: solo reverse-proxy expone 443/80
Volumes: postgres-data · redis-data · minio-data · loki-data
```

### 3.1 Decision pragmatica (R5)

Si KVM 8 queda justo · fusionar:
- `realtime` dentro de `api` (Sprint 1 OK)
- `worker-default` y `worker-agent` en un solo `worker` con colas separadas

NO sacrificar: `postgres` · `redis` · `litellm` · workers · `reverse-proxy`.

## 4. Docker Compose canonico

```yaml
# docker-compose.yml
version: '3.9'

services:
  reverse-proxy:
    image: caddy:2
    restart: unless-stopped
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy-data:/data
      - caddy-config:/config
    networks:
      - faberloom-net

  frontend:
    build: ./frontend
    image: faberloom/frontend:latest
    restart: unless-stopped
    environment:
      - NEXT_PUBLIC_API_URL=https://api.faberloom.com
    networks:
      - faberloom-net

  api:
    build: ./backend
    image: faberloom/api:latest
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql+psycopg://faberloom:${DB_PASSWORD}@postgres:5432/faberloom
      - REDIS_URL=redis://redis:6379/0
      - LITELLM_URL=http://litellm:4000
      - SECRETS_FILE=/run/secrets/api_secrets
    secrets:
      - api_secrets
    depends_on:
      - postgres
      - redis
      - litellm
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3
    networks:
      - faberloom-net

  worker-default:
    build: ./backend
    image: faberloom/api:latest
    command: celery -A app.celery worker -Q default --concurrency=4
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql+psycopg://faberloom:${DB_PASSWORD}@postgres:5432/faberloom
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    networks:
      - faberloom-net

  worker-agent:
    build: ./backend
    image: faberloom/api:latest
    command: celery -A app.celery worker -Q agent --concurrency=2
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql+psycopg://faberloom:${DB_PASSWORD}@postgres:5432/faberloom
      - REDIS_URL=redis://redis:6379/0
      - LITELLM_URL=http://litellm:4000
    depends_on:
      - postgres
      - redis
      - litellm
    networks:
      - faberloom-net

  scheduler:
    build: ./backend
    image: faberloom/api:latest
    command: celery -A app.celery beat
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql+psycopg://faberloom:${DB_PASSWORD}@postgres:5432/faberloom
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    networks:
      - faberloom-net

  postgres:
    image: pgvector/pgvector:pg16
    restart: unless-stopped
    environment:
      - POSTGRES_USER=faberloom
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=faberloom
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./backups:/backups
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "faberloom"]
      interval: 10s
    networks:
      - faberloom-net

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 1gb --maxmemory-policy allkeys-lru
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
    networks:
      - faberloom-net

  litellm:
    image: ghcr.io/berriai/litellm:main-stable
    restart: unless-stopped
    command: --config /app/config.yaml --port 4000
    volumes:
      - ./litellm-config.yaml:/app/config.yaml
    environment:
      - ANTHROPIC_API_KEY_FILE=/run/secrets/anthropic_key
      - OPENAI_API_KEY_FILE=/run/secrets/openai_key
    secrets:
      - anthropic_key
      - openai_key
    networks:
      - faberloom-net

  object-store:
    image: minio/minio:latest
    restart: unless-stopped
    command: server /data --console-address :9001
    environment:
      - MINIO_ROOT_USER=${MINIO_USER}
      - MINIO_ROOT_PASSWORD=${MINIO_PASSWORD}
    volumes:
      - minio-data:/data
    networks:
      - faberloom-net

  observability:
    image: grafana/otel-lgtm:latest  # Loki + Grafana + Tempo + Mimir bundle
    restart: unless-stopped
    volumes:
      - observability-data:/data
    networks:
      - faberloom-net

volumes:
  caddy-data:
  caddy-config:
  postgres-data:
  redis-data:
  minio-data:
  observability-data:

networks:
  faberloom-net:
    driver: bridge

secrets:
  api_secrets:
    file: ./secrets/api_secrets.env
  anthropic_key:
    file: ./secrets/anthropic_key.txt
  openai_key:
    file: ./secrets/openai_key.txt
```

## 5. Caddyfile (reverse proxy)

```
{
  email admin@faberloom.com
}

*.faberloom.com {
  tls {
    on_demand
  }
  
  # Tenant routing via subdomain (mwt.faberloom.com → tenant_id=mwt)
  @api path /api/*
  reverse_proxy @api api:8000
  
  @ws path /api/v1/ws*
  reverse_proxy @ws api:8000
  
  reverse_proxy frontend:3000
}

api.faberloom.com {
  reverse_proxy api:8000
}
```

## 6. Environment profiles

3 perfiles canonicos:

| Profile | Uso | Diferencias |
|---|---|---|
| `dev` | Local development | Hot reload · debug logs · NO TLS · LiteLLM mock provider |
| `staging` | Pre-prod testing | TLS valida · logs estructurados · LiteLLM real con cap budget |
| `prod` | Production | TLS strict · logs estructurados · backups automatizados · alertas activas |

Selector via env var `FABERLOOM_PROFILE=prod` en `.env`.

## 7. Deploy commands canonicos

```bash
# Deploy nuevo
./scripts/deploy.sh prod

# Internamente:
# 1. git pull origin main
# 2. docker compose pull
# 3. alembic upgrade head (db migrations)
# 4. docker compose up -d --build
# 5. wait for healthchecks
# 6. smoke test (curl /api/v1/health)
```

```bash
# Rollback minimo
./scripts/rollback.sh

# Internamente:
# 1. git checkout <previous_tag>
# 2. alembic downgrade -1 (si hubo migration)
# 3. docker compose up -d --build
# 4. healthchecks
```

## 8. Backup + Restore (R5 critical)

R5: "Backup sin restore probado es decoracion corporativa. Bonita, inutil y peligrosa."

### 8.1 Backup automatizado

```bash
# scripts/backup.sh (cron daily 02:00 GMT-6)

# Postgres dump
pg_dump -h postgres -U faberloom -F c -f /backups/postgres-$(date +%Y%m%d).dump faberloom

# Redis snapshot (RDB)
redis-cli BGSAVE
cp /redis-data/dump.rdb /backups/redis-$(date +%Y%m%d).rdb

# MinIO mirror (rclone)
rclone sync minio:faberloom /backups/minio-$(date +%Y%m%d)/

# Sync to off-site (Backblaze B2 o similar)
rclone sync /backups remote:faberloom-backups --transfers 4

# Retention: keep 7 daily · 4 weekly · 12 monthly
./scripts/rotate_backups.sh
```

### 8.2 RPO / RTO targets

| Datatype | RPO (max data loss) | RTO (max restore time) |
|---|---|---|
| Postgres | 24h | 1h |
| Redis (cache only) | accept loss | 5min |
| Redis (persistent jobs) | 1h | 30min |
| MinIO (evidence bundles) | 24h | 2h |
| Audit log SHA-chain | 0 (zero loss · critical) | 4h |

### 8.3 Restore rehearsal · MENSUAL obligatorio (R5)

```bash
# scripts/restore_rehearsal.sh
# Ejecuta MENSUAL · primer sabado del mes

# 1. Spin up stack secundaria (KVM separada o local)
docker compose -f docker-compose.restore.yml up -d

# 2. Restore Postgres del ultimo backup
pg_restore -h postgres-restore -U faberloom -d faberloom_restore /backups/latest.dump

# 3. Restore Redis
docker cp /backups/redis-latest.rdb redis-restore:/data/dump.rdb
docker compose restart redis-restore

# 4. Restore MinIO
rclone sync /backups/minio-latest/ minio-restore:faberloom

# 5. Smoke test
./scripts/smoke_test.sh restore

# 6. Validate sample queries
./scripts/validate_restore.sh

# 7. Cleanup
docker compose -f docker-compose.restore.yml down -v
```

Si rehearsal falla · alerta P0 · CEO + AUDITOR notificados. NO releasing al mes siguiente sin rehearsal exitoso.

## 9. Secrets management

```
secrets/
├── api_secrets.env         (DB_PASSWORD · JWT_SECRET · etc)
├── anthropic_key.txt
├── openai_key.txt
└── README.md (NUNCA commitear · gitignore)
```

Secrets:
- Solo legibles por root + docker
- NUNCA en variables de entorno globales
- Rotacion trimestral (CEO ejecuta `./scripts/rotate_secrets.sh`)
- Backup secrets cifrado con GPG · stored offsite

Sprint 1 sin Vault/SOPS · queda como evolucion v2.

## 10. Observability stack minimo

R5: "OpenTelemetry + Prometheus + Loki/Grafana minimo. Solo logs Docker es ciego. Sentry-only insuficiente."

```
Loki        ← logs estructurados (JSON con trace_id, tenant_id, etc)
Prometheus  ← metricas + alertas
Tempo       ← traces distribuidos (OpenTelemetry)
Grafana     ← UI consolidada (dashboards)
```

Container `observability` corre `grafana/otel-lgtm` (bundle prebuilt).

### 10.1 Logs estructurados obligatorios

Cada log line incluye:

```json
{
  "level": "INFO",
  "timestamp": "2026-05-02T14:23:11Z",
  "trace_id": "...",
  "tenant_id": "mwt",
  "actor_id": "...",
  "agent_id": "...",
  "command_id": "...",
  "service": "api",
  "msg": "draft.approved",
  "duration_ms": 142,
  "cost_usd": 0.018
}
```

Formato JSON · ingestion Loki via Promtail.

### 10.2 Metricas canonicas

```
http_requests_total{method, endpoint, status, tenant_id}
http_request_duration_seconds{method, endpoint, tenant_id}
llm_calls_total{provider, model, tenant_id, agent_id}
llm_cost_usd{tenant_id, agent_id}
llm_latency_seconds{provider, model, tenant_id}
celery_task_duration_seconds{task_name, status}
postgres_query_duration_seconds{query_type}
redis_commands_total{command, status}
ws_connections_active{tenant_id}
sha_chain_breaks_total{tenant_id}      ← critical · alarma
```

### 10.3 Alertas

```yaml
alerts:
  - name: sha_chain_break
    expr: increase(sha_chain_breaks_total[5m]) > 0
    severity: critical
    notify: [ceo, auditor]
  
  - name: cost_threshold_breach
    expr: llm_cost_usd_tenant_daily > tenant_budget * 0.95
    severity: warning
    notify: [ceo]
  
  - name: api_5xx_spike
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 10
    severity: warning
    notify: [oncall]
  
  - name: dlq_buildup
    expr: outbox_dlq_count > 10
    severity: warning
    notify: [ceo]
  
  - name: backup_age_breach
    expr: time() - max(backup_last_success_timestamp) > 86400 * 1.5
    severity: critical
    notify: [ceo]
```

## 11. Healthchecks

```
GET /api/v1/health
  → 200 si: db reachable · redis reachable · litellm reachable
  → 503 si cualquier dependencia caida (no es 200 fake)

GET /api/v1/health/deep
  → checks adicionales: postgres replication lag · redis stream length · disk usage
  → solo accesible internal-net
```

Docker healthchecks ejecutan cada 10s · `restart: unless-stopped` recovery automatico.

## 12. Reglas inquebrantables

1. **NO Kubernetes Sprint 1** · Docker Compose suficiente para 12 containers KVM 8.
2. **NO Kafka Sprint 1** · Redis Streams suficiente.
3. **NO microservicios extras "por si acaso"** · 12 containers exact.
4. **Backup automatizado diario · restore rehearsal MENSUAL obligatorio.**
5. **RPO/RTO declarados per datatype.** SHA-chain audit log = zero loss.
6. **Secrets NUNCA en env vars globales · solo Docker secrets.**
7. **Healthchecks obligatorios · `restart: unless-stopped` en todos los services.**
8. **Logs estructurados JSON con correlation IDs · NO texto libre.**
9. **Alertas P0 (sha_chain_break · backup_age_breach) notifican CEO + AUDITOR auto.**
10. **3 environment profiles (dev · staging · prod) · diferencias documentadas.**

## 13. Pendientes [PENDIENTE — NO INVENTAR]

- Migracion a Kubernetes (post-Sprint 1 · cuando volumen multi-tenant lo justifique · gate F2)
- HA Postgres (replica + failover) → diferido v2
- HA Redis (Sentinel o Cluster) → diferido v2
- Vault / SOPS para secrets → diferido v2
- Multi-region deployment → diferido v3
- CDN (Cloudflare?) para frontend assets → diferido v2
- WAF (web app firewall) → diferido v2
- DDoS protection → diferido v2 (Cloudflare gratis basic OK)

## NO IMPLICA (R4 bonus 5%/50%)

`SPEC_FB_SYSTEM_TOPOLOGY_v1` **NO implica HA en Sprint 1**. 12 containers single-VM Hostinger KVM 8 single point of failure por diseño v1. HA queda como evolucion v2 cuando >=3 tenants en produccion lo justifique. Restore rehearsal mensual mitiga riesgo data loss.

## Changelog
- 2026-05-02 v1.0 VIGENTE: Creacion inicial post R5 ChatGPT. Stack canonico sealed (FastAPI + Next.js + Postgres+pgvector + Redis Streams + Celery + LiteLLM + Caddy + MinIO + Grafana/Loki/Prometheus). Docker Compose 12 containers Hostinger KVM 8 (puede fusionar realtime+api · workers en uno si justo). Caddyfile con tenant subdomain routing. 3 environment profiles. Deploy + rollback commands. Backup automatizado diario · restore rehearsal MENSUAL obligatorio (R5 critical). RPO/RTO per datatype con audit log zero loss. Secrets via Docker secrets (Sprint 1 · Vault diferido v2). Observability minimo (Loki+Prometheus+Tempo+Grafana bundle). Logs estructurados JSON obligatorios con correlation IDs. Metricas + alertas P0 (sha_chain_break · backup_age_breach). Healthchecks obligatorios. 10 reglas inquebrantables incluyendo NO K8s · NO Kafka · NO microservicios extra. NO implica HA Sprint 1.

## Stamp
VIGENTE 2026-05-02 — Plataforma canonica 12 containers KVM 8. Operativo (deploy + rollback + backup + restore rehearsal mensual). NO sub-spec de Auth ni Integration · piezas separadas con responsabilidad clara. Sprint 1 ejecutable post-merge.
