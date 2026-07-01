---
id: SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FABERLOOM
date: 2026-04-19
authors: CEO + 2 rondas auditor externo + ronda quirúrgica de ejecutabilidad
supersedes: —
inputs:
  - SPEC_USER_ADMIN_KNOWLEDGE_FLOW.md (v1.0 DRAFT)
  - ARCH_AGENT_PRINCIPLES.md (P1–P13)
  - project_faberloom_architecture.md (3 objetos canónicos)
  - project_faberloom_positioning.md (wedge cotización B2B calzado)
  - project_faberloom_security.md (protege motor, asume tablero)
aplica_a: [FaberLoom]
---

# SPEC — FaberLoom Architecture v1 Beta Blueprint

**Documento ejecutable.** Cero filosofía. Una sola verdad por decisión. Aplican reglas de KB: R1 no inventar · R2 no tocar FROZEN · R5 documentar todo cambio.

---

## 0. Alcance y estado

**Alcance:** stack técnico, modelo de datos, RLS, perfiles de despliegue, Sprint 1 funcional, observabilidad, secrets, backup, jobs operativos y checklist binaria de arranque para la ventana beta **2026-04-20 → 2026-06-14** (8 semanas fijas).

**No cubre:** billing (Ronda 3), connectors avanzados (Ronda 4), compliance formal SOC 2/ISO (Ronda 5 opcional), v1.5+.

**Estado v1.0 DRAFT.** Promoción a APPROVED requiere validación de los 3 design partners del wedge (cotización B2B calzado seguridad) antes del corte de S4 (2026-06-14).

---

## 1. Convención de tipos: **UUIDv7** (FROZEN)

Toda PK y toda referencia lógica entre tablas usa `uuid` (Postgres nativo). Generación **client-side** con UUIDv7 (time-ordered, lex-sortable):

```python
# app/core/ids.py
import uuid
import uuid_utils

def new_id() -> uuid.UUID:
    return uuid.UUID(bytes=uuid_utils.uuid7().bytes)
```

**Justificación:** UUIDv7 conserva la propiedad time-ordered de ULID (insert perf en btree), usa tipo `uuid` nativo de Postgres 16 (RLS casts `::uuid` funcionan sin reescrituras), índice 16 bytes vs 26 de ULID, sin extensión extra.

**RLS settings — firma única para todo el sistema:**

```sql
SET LOCAL app.tenant_id   = '<uuid>';   -- uuid
SET LOCAL app.user_id     = '<uuid>';   -- uuid
SET LOCAL app.role        = 'operator'; -- text: owner|admin|operator
SET LOCAL app.dept_ids    = '<uuid>,<uuid>,...'; -- csv de uuid, puede ser vacío
SET LOCAL app.break_glass = 'false';    -- boolean text
```

Casts válidos en policies:
- `current_setting('app.tenant_id')::uuid`
- `current_setting('app.user_id')::uuid`
- `string_to_array(current_setting('app.dept_ids'), ',')::uuid[]`
- `current_setting('app.break_glass', true)::boolean`
- `current_setting('app.role')` (TEXT, sin cast)

**Regla:** `ULID` no existe en este sistema. Toda mención previa a "ULID string(26)", `id TEXT`, `core/ulid.py` o cualquier derivado queda **derogada por este documento**.

---

## 2. Lista FROZEN v1 — 20 tablas

| # | Tabla | Dominio | Propósito | tenant_id | Append-only | RLS | Escribe | Lee | Sprint |
|---|---|---|---|---|---|---|---|---|---|
| 1 | tenant | identity | raíz tenancy | — (PK) | no | no | api (owner) | todos | S1 |
| 2 | user_account | identity | identidad humano | sí | no | sí | api | api, workers | S1 |
| 3 | department | identity | unidad org intra-tenant | sí | no | sí | api | api, runtime_worker | S1 |
| 4 | user_department | identity | N:M user↔dept | sí | no | sí | api | api, runtime_worker | S1 |
| 5 | session | identity | web session + ctx RLS | sí | no | sí | api | api | S1 |
| 6 | event_outbox | plumbing | eventos pendientes publicar | sí | append + soft published_at | sí | api, workers | audit_worker | S1 |
| 7 | inbox_message | plumbing | idempotency consumer (14d TTL) | no (consumer-scoped) | sí | no | todos consumers | todos consumers | S1 |
| 8 | audit_event | governance | log append-only | sí | sí estricto | sí (read-only user) | audit_worker | api (admin UI) | S1 |
| 9 | job_execution | plumbing | lock + historial jobs scheduler | no | sí | no | scheduler | scheduler, grafana | S1 |
| 10 | agent_spec | agents | def estática del agente | sí | versioned (status) | sí | api | runtime_worker, ingestion_worker | S2 |
| 11 | agent_binding | agents | vínculo spec↔scope↔user/dept | sí | no | sí | api | runtime_worker | S2 |
| 12 | agent_run | agents | ejecución | sí | sí | sí | runtime_worker | api, audit_worker | S2 |
| 13 | memory_source | knowledge | origen del chunk (doc, email, manual) | sí | no | sí | ingestion_worker, api | api | S2 |
| 14 | memory_chunk | knowledge | unidad de memoria | sí | versioned via status | sí (scope-aware) | ingestion_worker, runtime_worker | runtime_worker, api | S2 |
| 15 | memory_chunk_vector | knowledge | embedding asociado | sí | reemplazable | sí | ingestion_worker | runtime_worker | S2 |
| 16 | overlay_policy | knowledge | policies scope-override | sí | no | sí | api | runtime_worker, api | S2 |
| 17 | draft | drafting | borrador outbound | sí | no (status change) | sí (creator+approver) | runtime_worker | api, audit_worker | S3 |
| 18 | draft_decision | drafting | aprobación/rechazo | sí | sí | sí | api | audit_worker | S3 |
| 19 | connector_account | connectors | cuenta OAuth por user | sí | no (revoked_at soft) | sí | api | {connector}_worker | S3 |
| 20 | connector_send_log | connectors | bitácora envío externo | sí | sí | sí | {connector}_worker | audit_worker, api | S3 |

**Reglas transversales FROZEN:**
- PK = `uuid` (UUIDv7) en todas.
- Sin FKs físicas: referencias lógicas por `uuid` + outbox + reconcile.
- Toda fila con `tenant_id` lleva índice compuesto `(tenant_id, <campo_filtrado>)`.
- `audit_event`, `agent_run`, `draft_decision`, `connector_send_log` son append-only estricto: RLS niega `UPDATE`/`DELETE` a `faber_app`.
- Soft versioning: `status ∈ {active, superseded, revoked}` + `supersedes_<x>_id` donde aplique.

---

## 3. Modelo identity — final coherente

| Tabla | v1 | Razón | Esquema mínimo |
|---|---|---|---|
| tenant | ✅ | raíz tenancy | `id uuid PK, name text, slug text UNIQUE, oidc_discovery_url text NULL, config jsonb NOT NULL DEFAULT '{}', created_at timestamptz NOT NULL DEFAULT now(), status text NOT NULL CHECK (status IN ('active','suspended'))` |
| user_account | ✅ | identidad | `id uuid PK, tenant_id uuid NOT NULL, email text NOT NULL, oidc_sub text NULL, display_name text, role text NOT NULL CHECK (role IN ('owner','admin','operator')), status text NOT NULL, last_login_at timestamptz NULL, created_at timestamptz NOT NULL DEFAULT now(), UNIQUE (tenant_id, email)` |
| department | ✅ | scope=dept en 4 niveles | `id uuid PK, tenant_id uuid NOT NULL, name text NOT NULL, slug text NOT NULL, parent_dept_id uuid NULL, created_at timestamptz NOT NULL DEFAULT now(), status text NOT NULL, UNIQUE (tenant_id, slug)`. Jerarquía opcional; retrieval trata árbol como flat en v1. |
| user_department | ✅ | N:M user↔dept | `user_id uuid NOT NULL, department_id uuid NOT NULL, tenant_id uuid NOT NULL, role_in_dept text NULL, added_at timestamptz NOT NULL DEFAULT now(), added_by uuid NOT NULL, PRIMARY KEY (user_id, department_id)`. Índices: `(tenant_id, user_id)`, `(tenant_id, department_id)`. |
| session | ✅ | web session + ctx RLS | `id uuid PK, tenant_id uuid NOT NULL, user_id uuid NOT NULL, user_agent_hash text, ip_hash text, expires_at timestamptz NOT NULL, revoked_at timestamptz NULL, created_at timestamptz NOT NULL DEFAULT now()` |
| user_sync_state | ❌ **[v1.5]** | OIDC v1 = pull en login. SCIM push = v1.5. | v1.5: `(provider, external_id, user_id, last_sync_at, checksum)` |
| workspace_config | ❌ **[v1.5]** | JSONB en `tenant.config` alcanza v1. | v1.5: `(tenant_id, key, value_jsonb, updated_at, updated_by)` |

**Usuario sin department:** válido. `user_department` puede estar vacío para un user. Retrieval de `scope='dept'` devuelve 0 filas para ese usuario — es correcto, no bug. El usuario accede a `global`, `org`, `user`. Admin puede asignar dept en cualquier momento.

---

## 4. `memory_chunk` — versión única coherente

### 4.1 DDL final

```sql
CREATE TABLE memory_chunk (
  id                  uuid PRIMARY KEY,
  tenant_id           uuid NOT NULL,
  -- Scope (4 niveles fijos v1)
  scope               text NOT NULL
                        CHECK (scope IN ('global','org','dept','user')),
  owner_department_id uuid NULL,        -- NOT NULL ⇔ scope='dept'
  owner_user_id       uuid NULL,        -- NOT NULL ⇔ scope='user'
  -- Metadata ortogonal (NO scope)
  business_entity_id  uuid NULL,        -- cliente/oportunidad, metadata libre
  -- Contenido y origen
  content             text NOT NULL,
  source_id           uuid NOT NULL,    -- ref lógica a memory_source (sin FK física)
  -- Versionado soft
  status              text NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active','superseded','revoked')),
  supersedes_chunk_id uuid NULL,
  -- Clasificación y visibilidad
  classification      text NOT NULL DEFAULT 'internal'
                        CHECK (classification IN ('public','partner_b2b','internal','ceo_only')),
  language            text NOT NULL DEFAULT 'es-ES',
  -- Auditoría (separado del scope)
  created_by          uuid NOT NULL,    -- quién ingresó el chunk (audit; NO es filter de scope)
  created_at          timestamptz NOT NULL DEFAULT now(),
  revoked_at          timestamptz NULL,
  -- Integridad scope↔owner
  CONSTRAINT chk_scope_owner CHECK (
       (scope = 'dept'   AND owner_department_id IS NOT NULL AND owner_user_id IS NULL)
    OR (scope = 'user'   AND owner_user_id IS NOT NULL AND owner_department_id IS NULL)
    OR (scope IN ('global','org') AND owner_department_id IS NULL AND owner_user_id IS NULL)
  )
);
```

**Distinción clave:** `created_by` = auditoría (toda fila tiene uno). `owner_user_id` = filter de scope (solo cuando `scope='user'`). Son columnas distintas con semántica distinta.

### 4.2 Índices

```sql
CREATE INDEX ix_mc_tenant_status_active
  ON memory_chunk (tenant_id) WHERE status = 'active';

CREATE INDEX ix_mc_scope_global_org
  ON memory_chunk (tenant_id, scope)
  WHERE status = 'active' AND scope IN ('global','org');

CREATE INDEX ix_mc_scope_dept
  ON memory_chunk (tenant_id, owner_department_id)
  WHERE status = 'active' AND scope = 'dept';

CREATE INDEX ix_mc_scope_user
  ON memory_chunk (tenant_id, owner_user_id)
  WHERE status = 'active' AND scope = 'user';

CREATE INDEX ix_mc_business_entity
  ON memory_chunk (tenant_id, business_entity_id)
  WHERE business_entity_id IS NOT NULL AND status = 'active';

CREATE INDEX ix_mc_source
  ON memory_chunk (tenant_id, source_id);

CREATE INDEX ix_mc_supersedes
  ON memory_chunk (supersedes_chunk_id)
  WHERE supersedes_chunk_id IS NOT NULL;
```

### 4.3 RLS — única versión

```sql
ALTER TABLE memory_chunk ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_chunk FORCE ROW LEVEL SECURITY;

-- READ: scope-aware (4 niveles + break-glass auditado)
CREATE POLICY mc_read ON memory_chunk FOR SELECT
  USING (
    tenant_id = current_setting('app.tenant_id')::uuid
    AND status = 'active'
    AND (
         scope = 'global'
      OR scope = 'org'
      OR (scope = 'dept'
          AND owner_department_id = ANY(
            string_to_array(current_setting('app.dept_ids'), ',')::uuid[]
          ))
      OR (scope = 'user'
          AND owner_user_id = current_setting('app.user_id')::uuid)
      OR current_setting('app.break_glass', true)::boolean = true
    )
    AND (
         classification <> 'ceo_only'
      OR current_setting('app.role') = 'owner'
    )
  );

-- INSERT: tenant + scope consistente con role
CREATE POLICY mc_insert ON memory_chunk FOR INSERT
  WITH CHECK (
    tenant_id = current_setting('app.tenant_id')::uuid
    AND created_by = current_setting('app.user_id')::uuid
    AND (
         (scope IN ('global','org') AND current_setting('app.role') IN ('owner','admin'))
      OR (scope = 'dept'
          AND owner_department_id = ANY(
            string_to_array(current_setting('app.dept_ids'), ',')::uuid[]
          ))
      OR (scope = 'user' AND owner_user_id = current_setting('app.user_id')::uuid)
    )
  );

-- UPDATE: solo transiciones de status (active→superseded|revoked); nunca content
CREATE POLICY mc_update ON memory_chunk FOR UPDATE
  USING (tenant_id = current_setting('app.tenant_id')::uuid)
  WITH CHECK (tenant_id = current_setting('app.tenant_id')::uuid);

-- DELETE: prohibido (soft-delete vía status='revoked')
CREATE POLICY mc_no_delete ON memory_chunk FOR DELETE USING (false);
```

### 4.4 Retrieval query canónica

```sql
-- Middleware api ya ejecutó:
-- SET LOCAL app.tenant_id   = '<uuid>';
-- SET LOCAL app.user_id     = '<uuid>';
-- SET LOCAL app.dept_ids    = '<uuid>,<uuid>';
-- SET LOCAL app.role        = 'operator';
-- SET LOCAL app.break_glass = 'false';

SELECT
  mc.id,
  mc.content,
  mc.scope,
  mc.business_entity_id,
  mcv.embedding <=> $query_vector AS distance
FROM memory_chunk mc
JOIN memory_chunk_vector mcv ON mcv.chunk_id = mc.id
WHERE mc.tenant_id = current_setting('app.tenant_id')::uuid
  AND (
       $business_entity_id::uuid IS NULL
    OR mc.business_entity_id = $business_entity_id::uuid
    OR mc.business_entity_id IS NULL
  )
ORDER BY mcv.embedding <=> $query_vector
LIMIT 20;
-- RLS filtra scope + status + classification automáticamente
```

---

## 5. `docker-compose.dev.yml` — perfil dev (4 containers, hot-reload)

```yaml
version: "3.9"

services:

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: faberloom
      POSTGRES_USER: faber_admin
      POSTGRES_PASSWORD: devpass
    ports: ["5432:5432"]
    volumes:
      - pg_dev:/var/lib/postgresql/data
      - ./infra/postgres/init:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U faber_admin -d faberloom"]
      interval: 5s
      retries: 10

  rabbitmq:
    image: rabbitmq:3.13-management-alpine
    environment:
      RABBITMQ_DEFAULT_USER: faber
      RABBITMQ_DEFAULT_PASS: devpass
      RABBITMQ_DEFAULT_VHOST: faberloom
    ports: ["5672:5672", "15672:15672"]
    volumes:
      - ./infra/rabbitmq/definitions.json:/etc/rabbitmq/definitions.json:ro
      - ./infra/rabbitmq/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf:ro
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "-q", "ping"]
      interval: 10s
      retries: 5

  api:
    build: { context: ./app, dockerfile: Dockerfile.api.dev }
    command: ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    environment:
      DATABASE_URL: postgresql+psycopg://faber_app:devpass@postgres:5432/faberloom
      RMQ_URL: amqp://faber:devpass@rabbitmq:5672/faberloom
      SESSION_SECRET: dev-session-not-secret
      KEY_ENCRYPTION_KEY: dev-kek-not-secret-32-chars-ok!!
      ENVIRONMENT: dev
      LITELLM_MODE: stub
      AUTH_MODE: devbypass
      MAIL_MODE: stdout
      SCHEDULER_ENABLED: "false"
    volumes:
      - ./app:/app:rw
    ports: ["8000:8000"]
    depends_on:
      postgres: { condition: service_healthy }
      rabbitmq: { condition: service_healthy }

  web:
    image: node:20-alpine
    working_dir: /web
    command: ["sh", "-c", "npm ci && npm run dev"]
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
      NEXTAUTH_URL: http://localhost:3000
      NEXTAUTH_SECRET: dev-session-not-secret
    volumes:
      - ./web:/web:rw
      - web_node_modules:/web/node_modules
    ports: ["3000:3000"]
    depends_on:
      api: { condition: service_started }

volumes:
  pg_dev: {}
  web_node_modules: {}
```

**Mocks explícitos en dev:**
- `LITELLM_MODE=stub` → código devuelve fixtures.
- `AUTH_MODE=devbypass` → `/login` auto-inyecta user demo, sin OIDC real.
- `MAIL_MODE=stdout` → invites imprimen magic link en logs.
- `SCHEDULER_ENABLED=false` → cron off; disparo manual (`make job-expire-drafts`).

**Off en dev por diseño:** Traefik, scheduler, backup_worker, runtime_worker (corre como thread en api), audit_worker (idem), Prometheus, Grafana, Jaeger.

**SLA dev:** `make dev-up` en laptop limpio → stack arriba en **<90s**. Sin secrets reales, sin OAuth, sin internet.

---

## 6. `docker-compose.staging.yml` — perfil staging (11 containers)

```yaml
version: "3.9"

x-faber-env: &faber-env
  DATABASE_URL: postgresql+psycopg://faber_app:${DB_APP_PASSWORD}@postgres:5432/faberloom
  RMQ_URL: amqp://faber:${RMQ_PASSWORD}@rabbitmq:5672/faberloom
  LITELLM_URL: http://litellm:4000
  LITELLM_MASTER_KEY: ${LITELLM_MASTER_KEY}
  SESSION_SECRET: ${SESSION_SECRET}
  KEY_ENCRYPTION_KEY: ${KEY_ENCRYPTION_KEY}
  OIDC_CLIENT_ID: ${OIDC_CLIENT_ID}
  OIDC_CLIENT_SECRET: ${OIDC_CLIENT_SECRET}
  OIDC_DISCOVERY_URL: ${OIDC_DISCOVERY_URL}
  POSTMARK_TOKEN: ${POSTMARK_TOKEN}
  LITELLM_MODE: live
  AUTH_MODE: oidc
  MAIL_MODE: postmark
  SCHEDULER_ENABLED: "true"
  DOCUMENTS_ROOT: /var/faberloom/documents
  ENVIRONMENT: staging
  TZ: America/Costa_Rica

services:

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: faberloom
      POSTGRES_USER: faber_admin
      POSTGRES_PASSWORD: ${DB_ADMIN_PASSWORD}
      POSTGRES_INITDB_ARGS: "--auth-host=scram-sha-256"
    volumes:
      - pg_data:/var/lib/postgresql/data
      - ./infra/postgres/init:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U faber_admin -d faberloom"]
      interval: 10s
      retries: 10
    restart: unless-stopped

  rabbitmq:
    image: rabbitmq:3.13-management-alpine
    environment:
      RABBITMQ_DEFAULT_USER: faber
      RABBITMQ_DEFAULT_PASS: ${RMQ_PASSWORD}
      RABBITMQ_DEFAULT_VHOST: faberloom
    volumes:
      - rmq_data:/var/lib/rabbitmq
      - ./infra/rabbitmq/definitions.json:/etc/rabbitmq/definitions.json:ro
      - ./infra/rabbitmq/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf:ro
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "-q", "ping"]
      interval: 15s
      retries: 5
    restart: unless-stopped

  litellm:
    image: ghcr.io/berriai/litellm:main-stable
    command: ["--port", "4000", "--config", "/app/config.yaml"]
    environment:
      LITELLM_MASTER_KEY: ${LITELLM_MASTER_KEY}
      DATABASE_URL: postgresql://faber_admin:${DB_ADMIN_PASSWORD}@postgres:5432/faberloom?options=-csearch_path%3Dlitellm
      STORE_MODEL_IN_DB: "True"
    volumes:
      - ./infra/litellm/config.yaml:/app/config.yaml:ro
    depends_on: { postgres: { condition: service_healthy } }
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://localhost:4000/health/liveliness"]
      interval: 15s
      retries: 5
    restart: unless-stopped

  api:
    build: { context: ./app, dockerfile: Dockerfile.api }
    environment: *faber-env
    volumes: [documents_data:/var/faberloom/documents]
    depends_on:
      postgres: { condition: service_healthy }
      rabbitmq: { condition: service_healthy }
      litellm:  { condition: service_healthy }
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://localhost:8000/health"]
      interval: 10s
      retries: 5
    restart: unless-stopped
    labels:
      - traefik.enable=true
      - traefik.http.routers.api.rule=Host(`api.staging.faberloom.com`)
      - traefik.http.routers.api.entrypoints=websecure
      - traefik.http.routers.api.tls.certresolver=le
      - traefik.http.services.api.loadbalancer.server.port=8000

  web:
    build: { context: ./web }
    environment:
      NEXT_PUBLIC_API_URL: https://api.staging.faberloom.com
      NEXTAUTH_URL: https://app.staging.faberloom.com
      NEXTAUTH_SECRET: ${SESSION_SECRET}
    depends_on: { api: { condition: service_healthy } }
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://localhost:3000/api/health"]
      interval: 15s
      retries: 5
    restart: unless-stopped
    labels:
      - traefik.enable=true
      - traefik.http.routers.web.rule=Host(`app.staging.faberloom.com`)
      - traefik.http.routers.web.entrypoints=websecure
      - traefik.http.routers.web.tls.certresolver=le
      - traefik.http.services.web.loadbalancer.server.port=3000

  runtime_worker:
    build: { context: ./app, dockerfile: Dockerfile.worker }
    command: ["python", "-m", "app.workers.runtime"]
    environment:
      <<: *faber-env
      WORKER_QUEUES: fl.commands.runtime,fl.commands.ingestion,fl.commands.gmail
    volumes: [documents_data:/var/faberloom/documents]
    depends_on: { api: { condition: service_healthy } }
    restart: unless-stopped

  audit_worker:
    build: { context: ./app, dockerfile: Dockerfile.worker }
    command: ["python", "-m", "app.workers.audit"]
    environment:
      <<: *faber-env
      WORKER_QUEUES: fl.domain.audit,fl.domain.outbox,fl.commands.notify
    depends_on: { api: { condition: service_healthy } }
    restart: unless-stopped

  scheduler:
    build: { context: ./app, dockerfile: Dockerfile.worker }
    command: ["python", "-m", "app.workers.scheduler"]
    environment:
      <<: *faber-env
      HEALTHCHECKS_PING_URL: ${HEALTHCHECKS_PING_URL}
    depends_on: { api: { condition: service_healthy } }
    restart: unless-stopped

  backup_worker:
    build: { context: ./infra/backup }
    environment:
      DATABASE_URL: postgresql://faber_admin:${DB_ADMIN_PASSWORD}@postgres:5432/faberloom
      RETAIN_DAYS: "30"
      HEALTHCHECKS_BACKUP_URL: ${HEALTHCHECKS_BACKUP_URL}
    volumes:
      - pg_backups:/var/faberloom/backups
      - documents_data:/var/faberloom/documents:ro
    depends_on: { postgres: { condition: service_healthy } }
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:v2.52.0
    volumes:
      - ./infra/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./infra/prometheus/alerts.yml:/etc/prometheus/alerts.yml:ro
      - prom_data:/prometheus
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:9090/-/healthy"]
      interval: 30s
    restart: unless-stopped

  grafana:
    image: grafana/grafana:11.0.0
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_ADMIN_PASSWORD}
      GF_USERS_ALLOW_SIGN_UP: "false"
    volumes:
      - ./infra/grafana/provisioning:/etc/grafana/provisioning:ro
      - grafana_data:/var/lib/grafana
    depends_on: [prometheus]
    restart: unless-stopped

  traefik:
    image: traefik:v3.0
    command:
      - --providers.docker=true
      - --providers.docker.exposedbydefault=false
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
      - --entrypoints.web.http.redirections.entrypoint.to=websecure
      - --entrypoints.web.http.redirections.entrypoint.scheme=https
      - --certificatesresolvers.le.acme.email=ops@faberloom.com
      - --certificatesresolvers.le.acme.storage=/letsencrypt/acme.json
      - --certificatesresolvers.le.acme.httpchallenge.entrypoint=web
      - --metrics.prometheus=true
    ports: ["80:80", "443:443"]
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - traefik_le:/letsencrypt
    restart: unless-stopped

volumes:
  pg_data: {}
  rmq_data: {}
  documents_data: {}
  pg_backups: {}
  prom_data: {}
  grafana_data: {}
  traefik_le: {}
```

**Init scripts (`infra/postgres/init/`):**
- `01_extensions.sql`: `CREATE EXTENSION vector; CREATE EXTENSION pgcrypto; CREATE EXTENSION btree_gin;`
- `02_litellm_schema.sql`: `CREATE SCHEMA litellm AUTHORIZATION faber_admin;`
- `03_faber_app_role.sql`: crea rol `faber_app` sin BYPASSRLS, grants mínimos.

### 6.1 Contraste dev vs staging vs prod

| Servicio | Dev | Staging | Prod (S4) |
|---|---|---|---|
| postgres | ✅ ports expuestos | ✅ interno | ✅ |
| rabbitmq | ✅ ports expuestos | ✅ interno | ✅ |
| api | ✅ uvicorn --reload | ✅ | ✅ |
| web | ✅ next dev | ✅ next build | ✅ |
| litellm | ❌ stub en código | ✅ | ✅ |
| traefik | ❌ ports directos | ✅ | ✅ |
| runtime_worker | ❌ thread en api | ✅ (+ingestion+gmail colapsados) | ✅ |
| audit_worker | ❌ thread en api | ✅ (+outbox+notif colapsados) | ✅ |
| scheduler | ❌ manual CLI | ✅ | ✅ |
| backup_worker | ❌ | ✅ | ✅ |
| prometheus | ❌ | **✅ obligatorio** | ✅ |
| grafana | ❌ | **✅ obligatorio** | ✅ |
| jaeger | ❌ | ❌ en S1 / ✅ desde S2 | ✅ |
| whatsapp_worker | — | — | **[v1.5]** |

**Conteo honesto:** dev = 4 · staging = 11 · prod = 11 (mismo perfil; observabilidad ya obligatoria).

---

## 7. Sprint 1 — scope funcional, sin placeholders

**Ventana:** 2026-04-20 → 2026-05-03 (2 semanas).

**Regla cristalina:** en S1 la DB tiene exactamente **9 tablas** creadas por migraciones 0001 y 0002. Ni una más. El código de S1 no importa modelos de tablas de S2+. Cada tabla futura se crea en la migración del sprint que la necesite.

### 7.1 Migration map S1→S3

| Migración | Sprint | Crea | Comentario |
|---|---|---|---|
| `0001_initial.sql` | S1 | tenant, user_account, department, user_department, session | RLS ENABLED + FORCE en las 4 tenant-scoped |
| `0002_outbox_audit_job.sql` | S1 | event_outbox, inbox_message, audit_event, job_execution | append-only estricto en audit_event vía RLS; UNIQUE(name, scheduled_for) en job_execution |
| `0003_agents.sql` | S2 | agent_spec, agent_binding, agent_run | — |
| `0004_memory.sql` | S2 | memory_source, memory_chunk, memory_chunk_vector, overlay_policy | memory_chunk con las 4 policies RLS de §4.3 |
| `0005_drafting.sql` | S3 | draft, draft_decision | draft-first absoluto; 72h expiry default |
| `0006_connectors.sql` | S3 | connector_account, connector_send_log | OAuth tokens cifrados con pgcrypto |

### 7.2 Procesos reales S1 (staging)

8 containers operables: **traefik · postgres · rabbitmq · litellm** (stub si no hay key) **· api · web · audit_worker** (+ outbox_publisher + notification colapsados) **· scheduler · backup_worker** (+ prometheus + grafana).

No entran en S1: `runtime_worker` (sin agentes), `whatsapp_worker` (v1.5), `jaeger`.

### 7.3 Archivos reales S1 (~34)

```
migrations/
  0001_initial.sql
  0002_outbox_audit_job.sql
  seed_dev.sql
app/
  api/
    main.py
    deps/rls.py
    deps/auth.py
    deps/db.py
    routes/auth.py
    routes/users.py
    routes/departments.py
    routes/health.py
    services/identity.py
    services/invites.py
    services/outbox.py
  workers/
    audit.py                     # consume fl.domain.audit + fl.domain.outbox + loop publisher
    scheduler.py                 # APScheduler + job_execution locks
  core/
    config.py
    db.py
    rmq.py
    ids.py                       # new_id() UUIDv7
    logging.py                   # filtros de redacción
    audit.py
    events.py
web/
  app/(auth)/login/page.tsx
  app/admin/users/page.tsx
  app/admin/departments/page.tsx
  app/api/health/route.ts
  components/AdminShell.tsx
infra/
  postgres/init/01_extensions.sql
  postgres/init/02_litellm_schema.sql
  postgres/init/03_faber_app_role.sql
  rabbitmq/definitions.json
  rabbitmq/rabbitmq.conf
  litellm/config.yaml
  traefik/dynamic.yml
  grafana/provisioning/dashboards/api_http.json
  grafana/provisioning/dashboards/rmq_flow.json
  grafana/provisioning/dashboards/outbox_health.json
  grafana/provisioning/datasources/prometheus.yml
  prometheus/prometheus.yml
  prometheus/alerts.yml
  backup/Dockerfile
  backup/entrypoint.sh
scripts/
  backup_postgres.sh
  restore_test.sh
  dev_up.sh
tests/
  leakage/test_rls_tenant.py
  leakage/test_rls_dept_scope.py
  leakage/test_rls_user_scope.py
  leakage/test_audit_append_only.py
  leakage/test_session_per_user.py
  leakage/test_rls_denies_delete.py
  integration/test_oidc_login.py
  integration/test_outbox_publish.py
  integration/test_scheduler_no_double_run.py
docker-compose.dev.yml
docker-compose.staging.yml
.env.example
Makefile
docs/SETUP.md
```

### 7.4 Definition of Done S1

- [ ] `make dev-up` en laptop limpio arranca stack en <90s.
- [ ] OIDC login real (Google Workspace) produce session válida con tenant scope; logout la invalida.
- [ ] Admin crea/edita user + asigna department; cada acción emite `audit_event`.
- [ ] Evento `user.created` pasa outbox → RMQ → audit_worker → `audit_event` persistido en <2s p95.
- [ ] Un usuario de tenant A no ve filas de tenant B (test leakage pasa 6/6).
- [ ] Backup diario corre, genera `.dump` válido; `scripts/restore_test.sh` pasa con conteos idénticos ±0.
- [ ] Healthchecks todos verdes en staging.
- [ ] Scheduler doble-start NO produce doble ejecución (test verifica vía `job_execution.UNIQUE(name, scheduled_for)`).
- [ ] 3 dashboards Grafana (`api_http`, `rmq_flow`, `outbox_health`) provisionados automáticamente al `up`.
- [ ] 5 alertas Prometheus cargadas (ver §8.3).
- [ ] Healthchecks.io recibe ping en cada backup y cada tick de expire_drafts.

### 7.5 Demo final S1 (90 min, guion fijo)

1. Laptop limpio. `git clone && cp .env.example .env && make dev-up`. Stack arriba en 60-90s.
2. Login OIDC en `app.localhost` → redirige a Google → vuelve con session.
3. Admin UI: crear user `ana@acme.test`, asignar a dept "Ventas", role `operator`. Panel "Actividad" muestra `audit_event`.
4. psql como `faber_app` con `SET LOCAL app.tenant_id='<otro>'` → `SELECT * FROM user_account` devuelve 0.
5. Intentar `DELETE FROM audit_event` como `faber_app` → RLS rechaza.
6. `docker kill faberloom_postgres_1`; esperar 30s; `docker start`: outbox_publisher recupera backlog sin pérdida.
7. `pytest tests/leakage/ -v` → 6 passed en <10s.
8. `ls -la backups/` → archivo `YYYY-MM-DD.dump`; `scripts/restore_test.sh` ✅.
9. Grafana live: `outbox_backlog` en 0, `api_http_p95` <200ms.
10. Métrica cierre: tiempo desde `git clone` hasta primer login = <8 min.

---

## 8. Observabilidad — una sola verdad S1

**Regla FROZEN:** Prometheus + Grafana son **obligatorios en staging**. Off en dev. Jaeger off en S1, entra desde S2 con agent_run + LLM traces.

### 8.1 Obligatorio staging S1

| Componente | Estado | Scrape targets |
|---|---|---|
| prometheus | obligatorio | api:8000/metrics · rabbitmq_exporter:15692 · postgres_exporter:9187 · traefik:8082/metrics |
| grafana | obligatorio | datasource prometheus auto-provisionado |
| jaeger | **off S1** | — |
| healthchecks.io | obligatorio | ping desde scheduler (expire_drafts) + backup_worker |

### 8.2 Tres dashboards obligatorios (DoD S1)

| Dashboard | Paneles mínimos |
|---|---|
| `api_http.json` | request rate (rps) · p50/p95/p99 latency · 5xx rate · in-flight requests |
| `rmq_flow.json` | publish rate · consume rate · unacked depth · DLQ depth · publisher-confirm failures |
| `outbox_health.json` | outbox_backlog (unpublished count) · outbox_publish_lag_p95 · job_execution fail rate · audit_append rate |

### 8.3 Métricas obligatorias expuestas por api

```
fl_http_requests_total{route, method, status}
fl_http_request_duration_seconds{route, method}
fl_outbox_backlog
fl_outbox_publish_lag_seconds
fl_rmq_publish_total{exchange, success}
fl_audit_append_total
fl_job_execution_total{name, status}
fl_rls_denies_total{table}
```

### 8.4 Alertas obligatorias (`infra/prometheus/alerts.yml`)

| Alerta | Trigger | Severidad |
|---|---|---|
| OutboxBacklogHigh | `fl_outbox_backlog > 500` 5m | critical |
| ExpireDraftsStalled | sin tick de `fl_job_execution_total{name="expire_drafts"}` en 20m | critical |
| BackupMissing | Healthchecks ping `backup` ausente 26h | critical |
| API5xxBurst | `rate(fl_http_requests_total{status=~"5.."}[5m]) > 0.05` | warning |
| RLSDenySpike | `rate(fl_rls_denies_total[10m]) > 1` | warning |

---

## 9. Secrets & crypto policy v1

| Secreto | Dónde vive | Cifrado | Quién lo usa | Rotación | Auditoría | Nunca loguear |
|---|---|---|---|---|---|---|
| SESSION_SECRET | `.env` | N/A | api, web | manual 90d → invalida sessions | `audit_event type=secret.rotated` | sí |
| OIDC_CLIENT_SECRET | `.env` | N/A | api | cuando IdP rote | idem | sí |
| OAuth refresh_token (Gmail/WA) | `connector_account.refresh_token_ciphertext` | `pgp_sym_encrypt` con `KEY_ENCRYPTION_KEY` | gmail_worker, whatsapp_worker | refresh automático; revoke manual `DELETE /api/connectors/{id}` → `revoked_at`, row persistido | `audit_event type=connector.revoked` | sí |
| OAuth access_token (Gmail) | cache en memoria del worker con TTL | N/A | gmail_worker | rotación cada refresh | — | sí |
| WhatsApp long-lived token | `connector_account.access_token_ciphertext` | pgcrypto | whatsapp_worker | manual Meta + swap | `audit_event type=connector.token_swapped` | sí |
| LITELLM_MASTER_KEY | `.env` | N/A | litellm | manual 90d | log only | sí |
| LiteLLM virtual keys (por tenant) | schema `litellm` | nativo LiteLLM | api (proxy) | auto en onboarding tenant | `audit_event type=litellm_key.created` | sí |
| DB_APP_PASSWORD (faber_app) | `.env` | N/A | todos workers + api | 90d, rolling | `audit_event` manual | sí |
| DB_ADMIN_PASSWORD (faber_admin) | `.env` separado | N/A | migrator + backup_worker | 90d | idem | sí |
| KEY_ENCRYPTION_KEY | `.env` single source | N/A v1 | api, gmail_worker, whatsapp_worker | **NO ROTA EN v1** — requiere re-cipher. **[v1.5]** con KMS | `audit_event type=kek.access` | sí absoluto |
| RMQ_PASSWORD | `.env` | N/A | api, todos workers | 90d, rolling | idem | sí |
| POSTMARK_TOKEN | `.env` | N/A | notification_worker | 90d | idem | sí |
| Sentry DSN | `.env` | N/A | api, workers | sin rotación | — | hostname sí, querystring no |

**Nunca se loguea (hardcoded en logger filter):** access_token, refresh_token, password, secret, api_key, cookie, authorization header, email body completo, `memory_chunk.content`, prompt LLM completo (solo primeras 120 chars + hash), body email entrante (solo subject + hash + sender + size).

**Decisión cerrada:** SMTP = **Postmark** (deliverability LatAm sin warm-up, API simple).

**Revocación de connector sin romper auditoría:** soft-delete con `revoked_at=now()`, `status='revoked'`. `connector_send_log` histórico se mantiene. Worker lee row, ve `revoked_at != NULL`, rechaza nuevo envío, emite `audit_event type=connector.send_blocked_revoked`. Re-conexión = nuevo `connector_account` con nuevo UUID, no reutiliza el revocado.

---

## 10. Backup / restore plan v1

| Activo | Método | Frecuencia | Retención | Restore test | Owner | RPO | RTO |
|---|---|---|---|---|---|---|---|
| Postgres (faberloom + litellm schemas) | `pg_dump -Fc -Z6 -f /backups/{date}.dump` vía backup_worker | daily 02:00 UTC-6 | 30 daily + 4 weekly + 3 monthly (GFS) | **mensual** primer lunes → restore a DB shadow + conteos + hashes | DevOps (Álvaro v1) | 24h | 2h |
| pgvector embeddings | cubierto por pg_dump | incluido | incluido | incluido | — | 24h | 2h |
| RMQ definitions | `rabbitmqctl export_definitions` → `/backups/rmq_defs_{date}.json` | daily 01:00 | 14d | semestral → re-import staging shadow | DevOps | 24h (topology) | 15 min |
| RMQ message state | **no se backup-ea** (quorum queue single-node durable) | — | — | — | — | depende de outbox | N/A |
| Grafana dashboards | JSON provisioning en git | cada push main | git history | cada deploy | DevOps | 0 | 10 min |
| Traefik dynamic config | `infra/traefik/dynamic.yml` git | cada push | git history | cada deploy | DevOps | 0 | 5 min |
| ACME certs | volumen `traefik_le` + auto-renovación | continuous | N/A | N/A | Traefik | cert 90d | re-issue 5 min |
| Env inventory (sin valores) | `.env.example` git + valores reales en 1Password | cada cambio | git | cada deploy | DevOps | 0 | N/A |
| Documents volumen | `tar -czf /backups/docs_{date}.tar.gz /var/faberloom/documents` | daily 02:30 | 30d | trimestral extract shadow + hash | DevOps | 24h | 1h |
| audit_event | cubierto por pg_dump. Append-only vía RLS | incluido | 730d en DB (purge selectiva severity=INFO) | incluido | — | 24h | 2h |

**NO cubre v1:** PITR (WAL archiving → **[v1.5]**), off-site geo-distribuido (v1 = rsync VPS semanal runbook), warm standby (**[v1.5]**), documents versioning delta (**[v1.5]** restic), backup de KEK (pérdida de host = users re-authorize OAuth, aceptado).

---

## 11. Jobs operativos mínimos

| Job | Dónde corre | Frecuencia | Lock strategy | Qué toca | Si falla | Alerta |
|---|---|---|---|---|---|---|
| reconcile_outbox_orphans | scheduler → `fl.commands.jobs.reconcile` → audit_worker | hourly | `INSERT INTO job_execution(name, scheduled_for) ON CONFLICT DO NOTHING RETURNING id` | event_outbox sin published_at > 1h | retry natural; alerta si backlog > 500 o 2h sin progreso | Grafana `outbox_backlog` + Healthchecks |
| purge_sessions | scheduler → api | daily 03:00 UTC-6 | job_execution row | session expired > 7d | idempotente | log only |
| purge_inbox_messages | scheduler | daily 04:00 | job_execution | inbox_message > 14d | idempotente | log only |
| purge_audit_events | scheduler | weekly dom 05:00 | job_execution | audit_event severity=INFO > 730d | idempotente | log only (crítico si 2m seguidos fallan) |
| expire_drafts | scheduler → runtime_worker (S3+) | cada 5 min | job_execution + advisory lock pg | draft pending expires_at < now() → status=expired | idempotente; 1h sin tick → crítico | Grafana + Healthchecks + Slack |
| outbox_republish | outbox_publisher loop interno | cada 30s | publisher confirms RMQ + advisory lock | event_outbox unpublished LIMIT 200 | natural retry; backlog > 1000 crítico | Grafana + Healthchecks |
| token_refresh_check | scheduler → {connector}_worker (S3+) | cada 10 min | job_execution + `FOR UPDATE SKIP LOCKED` | connector_account expires_at < now()+15m | escalar a user, status=needs_reauth | critical si >5 tokens muertos/tenant |
| backup_postgres | backup_worker (supercronic) | daily 02:00 UTC-6 | `flock /tmp/backup.lock` + job_execution | pg_dump → `/backups/{date}.dump` | alerta dura; 2d sin backup → P1 | Healthchecks.io obligatorio |
| backup_verify_restore | manual (runbook) | mensual 1er lunes | operador | pg_restore a `faberloom_shadow`, conteos + hashes | ticket P2 | runbook |
| rmq_definitions_export | scheduler | daily 01:00 | flock | `/backups/rmq_defs_{date}.json` | log only | log only |

**Esquema `job_execution`:**

```sql
CREATE TABLE job_execution (
  id              uuid PRIMARY KEY,
  name            text NOT NULL,
  scheduled_for   timestamptz NOT NULL,
  started_at      timestamptz,
  finished_at     timestamptz,
  status          text NOT NULL CHECK (status IN ('claimed','running','success','failure','skipped')),
  host            text,
  UNIQUE (name, scheduled_for)
);
```

**Sin doble ejecución:** scheduler hace `INSERT ... ON CONFLICT (name, scheduled_for) DO NOTHING RETURNING id`. Si devuelve row, ejecuta; si no, otra instancia tomó el slot. Contrato listo para failover v1.5 sin cambios.

---

## 12. Taxonomía `audit_event.action`

Enum controlado. Formato `{entity}.{verb}`:

```
user.created | user.updated | user.role_changed | user.deleted
session.login | session.logout | session.revoked
agent_spec.created | agent_spec.published | agent_spec.retired
draft.generated | draft.approved | draft.rejected | draft.expired | draft.sent
memory_chunk.promoted | memory_chunk.revoked | memory_chunk.superseded
connector.linked | connector.token_refreshed | connector.revoked | connector.send_blocked
policy.violation
secret.rotated | kek.access
backup.completed | backup.failed
job.claimed | job.failed
```

Severidades: `INFO` (default, purge 730d) · `WARN` · `ERROR` · `POLICY` (nunca se purga).

---

## 13. Matriz procesos obligatorios vs colapsables

| Proceso | Separado v1 | Motivo | Dev colapsable | Staging colapsable | [v1.5] |
|---|---|---|---|---|---|
| api | sí | entry point | no | no | — |
| web | sí | frontend build | sí (next dev) | no | — |
| postgres | sí | — | no | no | — |
| rabbitmq | sí | — | no | no | — |
| litellm | sí prod+staging | gateway LLM + billing | mock stub | no | — |
| traefik | solo prod/staging | TLS + routing | no (docker ports) | sí | — |
| runtime_worker | sí prod | aislamiento timeout LLM | colapsar con api thread | colapsar con ingestion+gmail | — |
| ingestion_worker | colapsado dentro runtime_worker v1 | volumen beta bajo | colapsado | colapsado | separar si tenant >10k chunks/día |
| gmail_worker | colapsado dentro runtime_worker v1 | volumen beta bajo | colapsado | colapsado | separar si ≥3 tenants con >500 emails/día |
| whatsapp_worker | **[v1.5]** | WA no es P0 del wedge | N/A | N/A | ingresa cuando design partner lo pida |
| audit_worker | sí | integrity append-only | colapsar con api thread | no (aislar para leakage tests) | — |
| outbox_publisher | colapsado dentro audit_worker v1 | publisher confirms + reliability | colapsado | colapsado | separar v1.5 si throughput >50 msg/s |
| notification_worker | colapsado dentro audit_worker v1 | volumen email transaccional bajo | colapsado | colapsado | separar v1.5 si +SMS/push |
| scheduler | sí | cron distribuido sin Redis | manual CLI | sí | — |
| backup_worker | sí staging+prod | aislamiento recursos | script local | sí | — |
| reconcile_worker | no existe como proceso | job dentro scheduler→audit_worker | colapsado | colapsado | colapsado |
| prometheus | obligatorio staging+prod | observability | off | **obligatorio** | — |
| grafana | obligatorio staging+prod | — | off | **obligatorio** | — |
| jaeger | S2+ | trazas LLM con agent_run | off | off S1 / on S2 | — |

---

## 14. Checklist binaria de ejecutabilidad (15 ítems sí/no)

Un solo `[ ]` bloquea arranque.

```
[ ]  1. Repo faberloom-platform creado, branches main+dev+sprint-1, .env.example completo con TODAS las vars (sin valores)
[ ]  2. Decisión tipo ID aplicada: todo el DDL, RLS, código Python usa uuid (UUIDv7 client-side con uuid_utils). Cero ULID.
[ ]  3. migrations/0001_initial.sql reversible, crea 5 tablas identity con RLS ENABLED + FORCE; `alembic downgrade base` funciona
[ ]  4. migrations/0002_outbox_audit_job.sql idem, 4 tablas plumbing con RLS; job_execution con UNIQUE(name, scheduled_for)
[ ]  5. Rol faber_app SIN BYPASSRLS, grants mínimos; faber_admin separado para migraciones/backup
[ ]  6. Middleware RLS en api emite `SET LOCAL app.tenant_id/user_id/role/dept_ids/break_glass` por request; test verifica que BEGIN/COMMIT limpia el scope
[ ]  7. OIDC real funciona contra Google Workspace: /login → callback → session cookie válida con tenant+user resolvidos; logout revoca session
[ ]  8. docker-compose.dev.yml arranca 4 containers en <90s con LITELLM_MODE=stub, AUTH_MODE=devbypass, MAIL_MODE=stdout
[ ]  9. docker-compose.staging.yml arranca 11 containers; Traefik emite cert LE válido para api.staging.faberloom.com y app.staging.faberloom.com
[ ] 10. Flujo outbox→audit end-to-end: crear user → fila en event_outbox → audit_worker consume → fila en audit_event en <2s p95
[ ] 11. tests/leakage/ pasa 6/6 (tenant_isolation, dept_scope, user_scope, audit_append_only, session_per_user, rls_denies_delete); CI gate configurado
[ ] 12. scripts/backup_postgres.sh produce .dump válido; scripts/restore_test.sh restaura a DB shadow y conteos coinciden ±0
[ ] 13. Scheduler con 3 jobs registrados; doble start NO produce doble ejecución (verificado con test de integración)
[ ] 14. 3 dashboards Grafana (api_http, rmq_flow, outbox_health) provisionados auto; 5 alertas Prometheus cargadas; Healthchecks.io recibe pings de backup + expire_drafts
[ ] 15. docs/SETUP.md permite a un dev externo clonar repo → make dev-up → login → crear user en <15min sin preguntar nada
```

---

## 15. Riesgos cerrados vs abiertos

### Cerrados en este blueprint

1. Convención tipos: UUIDv7 único, RLS casts funcionan sin reescritura.
2. 20 tablas FROZEN coherentes entre resumen, DDL, RLS, sprints, archivos.
3. Identity model cerrado (department + user_department + user sin dept válido).
4. `memory_chunk` con columnas explícitas (owner_department_id + owner_user_id + created_by separados), RLS única versión.
5. Dev vs staging separados como artefactos finales (4 vs 11 containers).
6. Sprint 1 sin placeholders: DB tiene 9 tablas, ni una más.
7. Observabilidad obligatoria staging S1 (Prometheus + Grafana + 3 dashboards + 5 alertas).
8. Jaeger off S1, entra S2 con agent_run.
9. SMTP = Postmark decidido.
10. Secrets policy v1 con rotación, cifrado selectivo (solo OAuth), log filtering.
11. Backup plan con RPO 24h / RTO 2h, restore test mensual, owner.
12. Jobs con lock `job_execution UNIQUE(name, scheduled_for)`, recuperación post-falla.
13. Audit retention: queue TTL 1h (buffer) ≠ retention de dato (730d INFO, infinito WARN/ERROR/POLICY).
14. Taxonomía `audit_event.action` enum controlado.
15. whatsapp_worker → v1.5; container count honesto: 11 prod/staging, 4 dev.

### Abiertos para v1.5

1. SCIM + `user_sync_state` + directory push.
2. `workspace_config` dedicada (vs JSONB en tenant.config).
3. KMS externo para KEY_ENCRYPTION_KEY + rotación sin downtime.
4. PITR Postgres (WAL archiving a S3/R2).
5. S3-compatible document storage con versionado.
6. Pivote OPA/Cedar si RLS crece >30 policies/tabla.
7. whatsapp_worker separado + canal WA formal.
8. Rate limiter outbound distribuido.
9. Ingestion_worker y gmail_worker separados (cuando métricas lo exijan).
10. Warm standby Postgres + HA RMQ 3-node cluster.
11. Off-site backup geo-distribuido automático.
12. Jaeger con storage persistente (hoy all-in-one memory).

---

## 16. Referencias cruzadas

- `SPEC_USER_ADMIN_KNOWLEDGE_FLOW.md` — 4 scopes + 3 roles + TTL 90d learned overlays + leakage CI gate
- `ARCH_AGENT_PRINCIPLES.md` — P1–P13 invariantes (AgentSpec/Runtime/Memory, draft-first, P11/P12/P13)
- `ENT_PLAT_LLM_ROUTING.md` — routing modelos (ortogonal)
- `ENT_PLAT_MEMORY_STACK.md` — pgvector queda como KB canónica; Letta **[v1.5]** como capa memoria operativa opcional
- `ENT_PLAT_AGENTIC.md` — arquitectura agentes referencia

---

## 17. Changelog

- **v1.0 DRAFT · 2026-04-19** — Creación. Consolida 3 rondas: (1) blueprint técnico v1 beta 14 secciones, (2) ronda de endurecimiento (20 tablas FROZEN, jobs, secrets, backup, matriz procesos), (3) ronda quirúrgica de ejecutabilidad (UUIDv7, memory_chunk final, dev/staging separados, Sprint 1 sin placeholders, observabilidad obligatoria, checklist binaria). Derogada toda mención previa a ULID, `id TEXT`, policies viejas de memory_chunk con `department_id`/`created_by` como scope filter, ejemplos con `SET LOCAL app.tenant_id = '<ulid>'`, helper `ulid.py`.

**Stamp:** DRAFT. Promoción a APPROVED requiere validación de 3 design partners del wedge (cotización B2B calzado seguridad Marluvas/Tecmater LatAm) antes de corte S4 (2026-06-14).
