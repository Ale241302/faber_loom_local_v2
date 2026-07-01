AGENTE 1 — DEVELOPER BACKEND
==================

RESUMEN EJECUTIVO
-----------------
La KB tiene contratos sólidos para el motor de agentes (Action Engine, Skill Manifest v2, Flow DAG, Task Entity, RLS/pgvector y Audit Module), pero un developer backend no puede empezar a escribir código hoy porque hay **dos stacks contradictorios** (Django + Celery + Redis del lado MWT vs FastAPI + RabbitMQ + workers separados del blueprint FaberLoom) y componentes que aún no existen como especificación ejecutable (`automations`/`automation_runs`, integración Letta, WebSocket). Lo que más preocupa es que varios documentos se citan entre sí como si ya estuvieran alineados, pero los nombres de tablas, los workers y los brokers no cuadran.

Por componente:

  COMPONENTE: Action Engine (D1-D11) y su implementación en Django
  Por qué existe: Es el módulo medular que abstrae LLMs, APIs externas, tools locales y acceso a KB bajo un contrato API estable, con policy centralizada y observabilidad unificada (`SPEC_ACTION_ENGINE.md` v1.3 VIGENTE).
  Qué produce: Cada llamada devuelve un `ActionResult` con `success`, `output`, `latency_ms`, `cost_usd`, `action_used`, `bypassed`, `fact_attribution`, `confidence`, `audit_id`, `policy_version_applied` y `classification_enforced`. El contexto de entrada es `ActionContext` con `org_id`, `user_id`, `trace_id`, `data_classification` (N0-N4), `anonymization_level` (L0-L3), `conversation_ceiling` y `tenant_plan`.
  Cómo funciona: Se distribuye como **library Python interna** (`mwt_action_engine`), no como servicio. `execute(intent, payload, context)` resuelve una `RoutingPolicy` (YAML estático en F1) y ejecuta una cadena de acciones. `bypass(action_id, ...)` permite saltar policy logueando `bypassed=true` y una razón obligatoria. D9 enforces data classification: si `data_classification > tenant_plan_ceiling` retorna `PlanUpgradeRequired`. D10 genera un `AuditEntry` inmutable. D11 aplica `cache_control: {type: "ephemeral"}` y métrica `cache_hit_ratio`.
  Cómo se relaciona: Consume `SPEC_LLM_ROUTING_ARCHITECTURE`, `POL_DATA_CLASSIFICATION.md`, `SPEC_AUDIT_MODULE.md` y `ARCH_AGENT_PRINCIPLES.md` (P3, P4, P9, P13, P14). Es la pieza que skills y agents deberían invocar. Sin embargo, `SPEC_FB_AGENT_BUILDER_v1.md` y `PLAN_DESARROLLO_FABERLOOM_v4.md` planean usar **LiteLLM directo como librería** en Fase 0-2, no el Action Engine.
  Qué está incompleto o ambiguo para implementar:
    - No hay módulo Django/FastAPI concreto que implemente el contract; el roadmap de `SPEC_ACTION_ENGINE.md` dice "semana 3+".
    - No existe el DDL de `OutcomeLedger` ni el registry YAML detallado (`SCH_ACTION_SPEC.yaml` no fue encontrado en la ruta esperada).
    - No se especifica cómo se instancia el Engine por request en Django (middleware vs dependency injection), ni cómo se propagan las `ActionContext` vars a RLS.
    - LiteLLM aparece tanto como adapter dentro del Engine como gateway standalone; hay dualidad de responsabilidad.

  COMPONENTE: Multi-tenant isolation en las 7 capas
  Por qué existe: Garantizar que datos, embeddings, memoria, outputs, caché, logs/audit y tools de un tenant A no sean alcanzables desde el contexto de un tenant B (`ENT_PLAT_MULTITENANT.md` v1.0 VIGENTE + `SPEC_TENANT_CONTAMINATION_TESTS_v1.md` v1.0 DRAFT).
  Qué produce: Default-deny cross-tenant; RLS como source of truth; tenant context fluye por middleware/backend, nunca por header de cliente.
  Cómo funciona: `ENT_PLAT_MULTITENANT.md` define 5 invariantes. `SPEC_TENANT_CONTAMINATION_TESTS_v1.md` define 7 superficies de ataque (S1 Postgres/RLS, S2 embeddings/pgvector, S3 memoria Letta, S4 output pinning, S5 caché, S6 logs/audit, S7 tools/actions). El mecanismo técnico canonizado es `SET LOCAL` de variables de sesión Postgres:
    - `app.tenant_id` (uuid)
    - `app.user_id` (uuid)
    - `app.role` (text: owner|admin|operator)
    - `app.dept_ids` (csv de uuid)
    - `app.break_glass` ('true'|'false')
  Las policies usan `current_setting('app.tenant_id')::uuid`. `memory_chunk` tiene policy `mc_read` que filtra `scope` (global/org/dept/user) + `status='active'` + `classification <> 'ceo_only'` (a menos que role='owner') (`SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` §4.3).
  Cómo se relaciona: Aplica a toda tabla con `tenant_id`. `SPEC_FB_AUTH_TENANT_RBAC_v1.md` añade subdomain routing + 4 roles. `SCH_FB_CORE_TABLES_v1.md` añade `workspace_id` como segundo lente. `ENT_PLAT_LLM_ROUTING.md` v2.0 añade `tenant_model_allowlist` para data residency de modelos.
  Qué está incompleto o ambiguo para implementar:
    - RLS detallada solo existe para `memory_chunk`. Las otras 19 tablas FROZEN del blueprint solo tienen una policy genérica de ejemplo (`tenant_id = current_setting('app.tenant_id')::uuid`).
    - No hay seed de 2 tenants sintéticos para CI (`SPEC_TENANT_CONTAMINATION_TESTS.md` §H L2 pendiente).
    - No se especifica cómo se limpia el contexto RLS al devolver conexiones al pool (`DISCARD ALL` se menciona en `ENT_PLAT_LLM_ROUTING.md` §E5 pero no en el blueprint).
    - `SPEC_TENANT_CONTAMINATION_TESTS.md` §G sigue llamando a `ENT_PLAT_MULTITENANT` "STUB" cuando ya es VIGENTE: documento desactualizado.
    - No hay políticas para `tasks`, `automations`, `audit_event` (solo append-only), ni para la capa Letta.

  COMPONENTE: Celery workers (default vs agent): cómo se separan, qué corre en cuál
  Por qué existe: Procesar tareas asíncronas y scheduled jobs en el stack Django (`ENT_PLAT_INFRA.md` y `ENT_PLAT_EVENTOS.md`).
  Qué produce:
    - Worker default: event dispatch, background jobs, scheduled tasks.
    - Worker agent: `execute_agent_task` que carga un manifest y ejecuta `skill_executor` o `flow_executor` según el archetype (`SCH_FB_TASK_ENTITY.md`).
  Cómo funciona según la KB:
    - `ENT_PLAT_INFRA.md`: 4 workers Celery + 1 Celery Beat sobre Redis 7.
    - `ENT_PLAT_EVENTOS.md`: outbox PostgreSQL → dispatcher Celery → Redis Streams → consumer groups Celery por dominio.
    - `SCH_FB_TASK_ENTITY.md`: `@shared_task(bind=True, max_retries=2) def execute_agent_task(self, task_id)`. Lee `Task.objects.get(task_id=...)`, carga manifest, invoca `flow_executor.execute(...)` o `skill_executor.execute(...)`, persiste `outputs`, `run_id`, `cost_usd` y transiciona status.
  Cómo se relaciona: El modelo de tasks asume Celery. Pero `SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` (FastAPI) define workers separados sobre **RabbitMQ** (`runtime_worker`, `audit_worker`, `scheduler`) usando ARQ/pgboss, no Celery. `DEC-001` en `ENT_GOB_DECISIONES.md` dice explícitamente "Sin event bus, sin microservicios, sin Celery workers en MVP", mientras que `ENT_PLAT_INFRA.md` y `PLAN_DESARROLLO_FABERLOOM_v4.md` listan Celery.
  Qué está incompleto o ambiguo para implementar:
    - **Stack contradictorio**: no se puede implementar sin decidir si FaberLoom corre sobre Django+Celery+Redis o FastAPI+RabbitMQ+ARQ.
    - No hay definición de colas/routing-keys, dead letter, prioridad, rate limiting ni monitorización de workers.
    - No se especifica si `execute_agent_task` corre en la misma cola que tareas operativas o en una cola dedicada.
    - Faltan detalles del `beat_schedule` (solo se menciona `check-overdue-payments` en `RESUMEN_SPRINT26.md`).

  COMPONENTE: Tablas automations + automation_runs: FK, RLS, indexes
  Por qué existe: Programar y auditar procesos recurrentes (digest 17:00, vigencia de listas, batch de promoción, etc.) de forma unificada.
  Qué produce: **No existe** en la KB una tabla `automations` ni `automation_runs` con el shape solicitado.
  Cómo funciona según piezas relacionadas:
    - `SCH_FB_CORE_TABLES_v1.md` define `scheduled_jobs` (M9/V9.2):
      ```sql
      CREATE TABLE scheduled_jobs (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
        tenant_id uuid NOT NULL,
        job_type text NOT NULL,        -- digest | validity_check | promotion_batch
        cron_expr text NOT NULL,
        payload jsonb NOT NULL DEFAULT '{}',
        enabled boolean NOT NULL DEFAULT true,
        last_run_at timestamptz,
        last_status text,
        created_at timestamptz NOT NULL DEFAULT now()
      );
      ```
    - `SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` §11 define `job_execution` para lock + histórico:
      ```sql
      CREATE TABLE job_execution (
        id uuid PRIMARY KEY,
        name text NOT NULL,
        scheduled_for timestamptz NOT NULL,
        started_at timestamptz,
        finished_at timestamptz,
        status text NOT NULL,
        host text,
        UNIQUE (name, scheduled_for)
      );
      ```
      Nota: **no tiene `tenant_id`**.
    - `SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md` §4.1 define `workflow_runs`, `workflow_step_runs`, `workflow_approvals` y `workflow_templates`.
  Cómo se relaciona: `scheduled_jobs` debería disparar ejecuciones; `job_execution` da lock e idempotencia; `workflow_runs` maneja flujos DAG. No hay un modelo común que una ambos mundos bajo `automations`/`automation_runs`.
  Qué está incompleto o ambiguo para implementar:
    - **Gap explícito**: falta `CREATE TABLE automations (...)` y `CREATE TABLE automation_runs (...)`.
    - No hay FK entre `automations`, `scheduled_jobs`, `workflow_runs` y `job_execution`.
    - No hay RLS policy para `job_execution` (no tiene tenant_id).
    - No hay índices declarados para búsquedas por tenant + job_type + next_run, ni retry policy, ni dead letter.
    - No se define si una automation es un scheduled_job, un workflow periódico, o una entidad superior que orquesta ambos.

  COMPONENTE: Tabla tasks: cómo se crea desde los 13 tipos de inbound
  Por qué existe: Tener una entidad de primera clase para cada invocación de skill/flow, con state machine propia y HITL granular por output (`SCH_FB_TASK_ENTITY.md` v2.0 VIGENTE).
  Qué produce: Tabla `tasks` con:
    ```sql
    task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,
    agent_version TEXT,
    flow_node_id TEXT,
    invocation_mode TEXT NOT NULL CHECK (invocation_mode IN ('ad_hoc', 'scheduled', 'webhook', 'flow_node')),
    invoked_by TEXT NOT NULL,       -- ceo | system | flow:<parent_task_id> | webhook:<source>
    invoked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    priority TEXT NOT NULL DEFAULT 'normal',
    payload JSONB NOT NULL,
    expected_outputs TEXT[],
    status TEXT NOT NULL DEFAULT 'queued',  -- queued|running|awaiting_approval|completed|failed|cancelled|timeout
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    expected_completion_by TIMESTAMPTZ,
    run_id UUID REFERENCES episodic_memory(run_id),
    parent_task_id UUID REFERENCES tasks(task_id),
    child_task_ids UUID[],
    review_status TEXT,
    reviewed_by TEXT,
    reviewed_at TIMESTAMPTZ,
    review_notes TEXT,
    outputs JSONB,
    tenant_id TEXT NOT NULL DEFAULT 'mwt_internal',
    cost_usd NUMERIC(8, 4),
    error_message TEXT,
    error_code TEXT
    ```
    Índices: `idx_tasks_status_priority`, `idx_tasks_agent`, `idx_tasks_parent`, `idx_tasks_review`, `idx_tasks_tenant`.
  Cómo funciona: Se crea por:
    - `POST /api/tasks` (ad-hoc desde UI).
    - Cron trigger (`invocation_mode='scheduled'`).
    - Webhook de n8n (`invocation_mode='webhook'`, `invoked_by='webhook:gmail'`).
    - Nodo de un flow padre (`invocation_mode='flow_node'`, `parent_task_id` seteado).
    El worker `execute_agent_task` la ejecuta y transiciona estados.
  Cómo se relaciona: Cada `skill_call` en un flow DAG genera una sub-task. El dashboard del tenant muestra cola, pendientes de review, histórico y flow viewer.
  Qué está incompleto o ambiguo para implementar:
    - El prompt pide "13 tipos de inbound". La KB **no tiene 13 tipos de inbound**. Tiene **4 `invocation_mode`** y, en `AUDIT_FABERLOOM_B1_SERVICE_BLUEPRINT_v1.md`, **12 inbound item types** (email entrante, system alert, SLA/expiry timer, etc.).
    - No hay mapeo de esos 12 tipos de inbox item a `tasks`. La bandeja/inbox y la tabla `tasks` viven en documentos separados sin relación explícita.
    - No hay endpoints webhook por tipo de inbound ni schema de payload por tipo.
    - No se especifica `episodic_memory(run_id)` (tabla referenciada por FK pero DDL no encontrado en docs principales).
    - HITL granular por output requiere que el dashboard maneje múltiples review items por task; no hay schema de `task_output_reviews`.

  COMPONENTE: Letta self-hosted: cómo se conecta con Django, cómo se aísla por tenant
  Por qué existe: Proporcionar memoria operativa persistente de agentes (episodic/working/persistent) sin entregar datos a SaaS de memoria (`ENT_PLAT_MEMORY_STACK.md` v1.0 DRAFT).
  Qué produce: Perfiles aislados de memoria (`mwt-sprint-active`, `mwt-client-*`, `mwt-ceo-only`) con recall <500ms p95 y cero filtración cruzada.
  Cómo funciona según la KB:
    - Decisión: Letta self-hosted con store pgvector nativo sobre Postgres existente.
    - Perfiles como namespaces de memoria aislados; `mwt-ceo-only` nunca hace cross-reference.
    - Reglas: provenance obligatorio, supersession de Facts/Instructions, KB canónica gana ante conflicto, backup semanal.
    - Piloto de 4 semanas contra `mwt-sprint-active` (CEO-34 en `ENT_GOB_DECISIONES.md`).
  Cómo se relaciona: `ENT_PLAT_MEMORY_STACK.md` separa KB canónica (git + pgvector) de memoria operativa (Letta). `SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md` menciona Letta como parte del agent framework junto a LangGraph/Claude SDK. `DEC-010` (Jarvis) bloquea el orquestador hasta que Letta piloto esté DONE.
  Qué está incompleto o ambiguo para implementar:
    - **No hay spec de integración con Django/FastAPI**: no hay endpoints, no hay wrapper Python, no hay DDL de tablas Letta, no hay mapeo a `agent_run`/`memory_chunk`.
    - No se especifica cómo se pasa `tenant_id` al store Letta (por profile? por metadata? por RLS en Postgres subyacente?).
    - No hay decisión formal de CEO-34 (vence 2026-06-30).
    - `SPEC_FB_AGENT_BUILDER_v1.md` D4 posterga Letta a "cuando ≥3 SKILLs autónomos compitan por memoria"; el blueprint dice "Letta v1.5 opcional". Hay ambigüedad de prioridad.
    - No hay test automatizado de cross-profile leak definido.

  COMPONENTE: pgvector + RLS: cómo funciona el filter por tenant en similarity search
  Por qué existe: Retrieval vectorial multi-tenant que preserve RLS y atomicidad transaccional, sin doble sistema de control de acceso (`ENT_PLAT_MEMORY_STACK.md` C1 + `SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` §4).
  Qué produce: Similarity search que retorna solo chunks activos del tenant y scope visibles para el usuario actual.
  Cómo funciona:
    - Init: `CREATE EXTENSION vector;` (`SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` §6).
    - Tabla `memory_chunk` con scope ∈ {global, org, dept, user}, `owner_department_id`, `owner_user_id`, `business_entity_id`, `classification` ∈ {public, partner_b2b, internal, ceo_only}, `status` ∈ {active, superseded, revoked}.
    - RLS policy `mc_read`:
      ```sql
      CREATE POLICY mc_read ON memory_chunk FOR SELECT USING (
        tenant_id = current_setting('app.tenant_id')::uuid
        AND status = 'active'
        AND (
             scope = 'global'
          OR scope = 'org'
          OR (scope = 'dept' AND owner_department_id = ANY(string_to_array(current_setting('app.dept_ids'), ',')::uuid[]))
          OR (scope = 'user' AND owner_user_id = current_setting('app.user_id')::uuid)
          OR current_setting('app.break_glass', true)::boolean = true
        )
        AND (classification <> 'ceo_only' OR current_setting('app.role') = 'owner')
      );
      ```
    - Query canónica:
      ```sql
      SELECT mc.id, mc.content, mc.scope, mc.business_entity_id, mcv.embedding <=> $query_vector AS distance
      FROM memory_chunk mc
      JOIN memory_chunk_vector mcv ON mcv.chunk_id = mc.id
      WHERE mc.tenant_id = current_setting('app.tenant_id')::uuid
        AND ($business_entity_id::uuid IS NULL OR mc.business_entity_id = $business_entity_id::uuid OR mc.business_entity_id IS NULL)
      ORDER BY mcv.embedding <=> $query_vector
      LIMIT 20;
      ```
      RLS filtra scope + status + classification automáticamente.
  Cómo se relaciona: Alimenta skills/agents a través del Action Engine/runtime. KB canónica vive en git y se indexa en `memory_chunk`/`memory_chunk_vector`.
  Qué está incompleto o ambiguo para implementar:
    - **Falta DDL de `memory_chunk_vector`**: no se declaran columnas, tipo del vector (ej. `vector(768)`), FK lógica, ni índice HNSW (`CREATE INDEX ON memory_chunk_vector USING hnsw (embedding vector_cosine_ops)`).
    - Solo `memory_chunk` tiene `FORCE ROW LEVEL SECURITY` explícito; no se declara para el resto de tablas.
    - No se especifica `pg_trgm` vs embeddings: `PLAN_DESARROLLO_FABERLOOM_v4.md` E1b menciona "FTS pg_trgm. Sin embeddings" como etapa inicial, contradiciendo el blueprint que ya usa `memory_chunk_vector`.
    - No hay query plan ni benchmarks de filtrado compuesto (tenant + scope + business_entity + classification + vector).

  COMPONENTE: n8n como dumb pipe: qué hace exactamente, qué NO hace nunca
  Por qué existe: Conectar eventos externos (Gmail, Slack, SP-API, SAP webhooks) con el agent sin meter lógica de negocio en n8n, preservando versionado git, replay determinístico y audit trail completo (`SPEC_FB_AGENT_BUILDER_v1.md` D16 + `ENT_FB_TOOL_CATALOG_v1.md`).
  Qué produce: Workflows n8n pequeños que detectan evento, extraen payload y hacen POST a un endpoint del backend.
  Cómo funciona: El manifest declara triggers:
    ```yaml
    triggers:
      - kind: webhook
        source: gmail
        connector: n8n
        connector_workflow_id: gmail_b2b_watcher_v1
        idempotency_key_field: payload.email.message_id
        rate_limit_per_min: 30
        deduplication_window_h: 24
        pre_dispatch_filters:
          - kind: spam_domains_blocklist
            max_logic_complexity: trivial
        auth_method: hmac
    ```
    Convención de naming: `<source>_<purpose>_v<N>`.
  Cómo se relaciona: El agent es el "smart router": clasifica, decide y transforma. n8n es el "dumb pipe": solo detect + extract + dispatch.
  Qué NO hace nunca:
    - No usa nodes OpenAI/Claude/LLM.
    - No decide branches de negocio (switch nodes solo para tipos de evento).
    - No transforma lógica de negocio.
    - No tiene >5 nodes por workflow.
    - No envía directamente a APIs externas; siempre POST a endpoint Django/FastAPI.
  Qué está incompleto o ambiguo para implementar:
    - No hay ejemplos reales de workflows n8n (solo IDs versionados como `gmail_b2b_watcher_v1`).
    - No hay endpoints de recepción documentados (`/api/triggers/gmail` mencionado pero sin contrato de request/response).
    - No hay mecanismo de HMAC/validación de firma detallado.
    - No hay DDL de idempotencia para webhooks (tabla `inbox_message` en blueprint tiene 14d TTL pero no se liga a triggers).
    - No hay proceso de CI/CD/versionado para workflows n8n.
    - No se define qué pasa con reintentos y dead letter si el endpoint del backend falla.

  COMPONENTE: Audit trail D10: cómo se escribe, cómo se encadena el hash
  Por qué existe: Proveer trazabilidad inmutable y replay capability para sectores regulados (Enterprise/Government), materializando D10 del Action Engine (`SPEC_AUDIT_MODULE.md` v1.0 VIGENTE).
  Qué produce: `AuditEntry` con:
    ```python
    class AuditEntry(BaseModel):
        audit_id: UUID
        trace_id: str
        org_id: Optional[str]
        user_id: Optional[str]
        timestamp: datetime
        intent: str
        action_chain: list[str]
        input_hash: str
        output_hash: str
        data_classification: str
        anonymization_level: str
        conversation_ceiling: Optional[str]
        policy_version_pinned: dict
        previous_audit_hash: str
        entry_hash: str
        signature: str
        orchestrator_policy_pool_hash: Optional[str]
        retention_class: str
        storage_tier: Literal["hot", "warm", "cold_immutable"]
    ```
  Cómo se escribe:
    - Cada llamada del Action Engine genera una entry.
    - Hash chain:
      ```
      entry_hash = sha256(
          audit_id +
          trace_id +
          timestamp +
          input_hash +
          output_hash +
          policy_version_pinned +
          previous_audit_hash
      )
      ```
    - Cada entry referencia `previous_audit_hash`. Si alguien edita una entry, todos los hashes posteriores quedan inconsistentes.
    - Validación periódica: job cron diario verifica la cadena end-to-end.
  Cómo se relaciona: `SPEC_AUDIT_MODULE.md` materializa D10. El blueprint (`SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` §12) define `audit_event` como tabla append-only con taxonomía `{entity}.{verb}`, RLS que niega UPDATE/DELETE a `faber_app`, retención INFO 730d y WARN/ERROR/POLICY infinito.
  Qué está incompleto o ambiguo para implementar:
    - `SPEC_AUDIT_MODULE.md` es Fase 4-5 post-MVP; no hay DDL de tabla `audit_entry` separada en el blueprint.
    - El blueprint tiene `audit_event` operacional, pero no se especifica si es la misma entidad que `AuditEntry` del Action Engine o una vista resumen.
    - No se define dónde se almacena el tier "cold_immutable" (S3 Object Lock / Azure Immutable Blob) ni la firma digital.
    - No hay endpoints read-only del auditor con MFA (`GET /audit/v1/entries`, `/audit/v1/replay/{audit_id}`, `/audit/v1/integrity_check`, `POST /audit/v1/attestation_report`) implementados.
    - No hay trigger PostgreSQL que enforce append-only de `audit_event`; solo RLS policy genérica.

  COMPONENTE: WebSocket: cómo se mantiene la sesión por tenant, cómo se invalida
  Por qué existe: Chat/drafts en tiempo real y streaming de tokens para la UI (`PLAN_DESARROLLO_FABERLOOM_v4.md` 2.1 menciona "API REST + WebSocket chat/drafts").
  Qué produce: Conexión persistente asociada a sesión y tenant.
  Cómo funciona según la KB:
    - `PLAN_DESARROLLO_FABERLOOM_v4.md` lista WebSocket en el stack FastAPI.
    - `ARCH_AGENT_PRINCIPLES.md` define niveles de sesión: A (normal), B (sensible, MFA fresh), C (documento formal).
    - `SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` define sesiones Redis con cookie `faberloom_session` httpOnly/secure/SameSite=Strict, sliding TTL 7d.
  Cómo se relaciona: WebSocket debería reutilizar la cookie de sesión, validarla contra Redis, inyectar `tenant_id`/`user_id`/`role` en el contexto de la conexión y aplicar el mismo RLS que HTTP.
  Qué está incompleto o ambiguo para implementar:
    - **No hay spec de WebSocket**: no se define protocolo (Socket.IO, native WS, SSE), autenticación en handshake, heartbeat, reconexión, multiplexación por tenant/room, ni invalidación.
    - No se especifica cómo se invalida la conexión al hacer logout, revocar session, cambiar de tenant o expirar la cookie.
    - No hay tabla/mecanismo de rooms/channels por tenant.
    - No se define si el streaming de tokens pasa por WebSocket o por SSE.
    - No hay política de RLS aplicada a queries disparadas desde el handler WebSocket.
    - `ENT_PLAT_EVENTOS.md` usa Redis Streams + Celery para eventos; no se explica si WebSocket se alimenta del mismo bus o de pub/sub separado.

HALLAZGOS PRIORITARIOS:

  P0 (bloquea):
    1. **Stack contradictorio**: la KB propone simultáneamente Django+Celery+Redis (MWT/ENT_PLAT_INFRA) y FastAPI+RabbitMQ+ARQ/pgboss (FaberLoom blueprint). Un backend dev no puede empezar sin una decisión única de framework, broker y worker model.
    2. **No existe `automations`/`automation_runs`**: solo hay `scheduled_jobs`, `job_execution` y `workflow_runs` sin unificar. Bloquea cualquier scheduler unificado.
    3. **Action Engine no tiene implementación concreta**: es un contrato Python library sin módulo Django/FastAPI, sin DDL de `OutcomeLedger`, sin adapters.

  P1 (importante):
    1. **Letta self-hosted sin spec de integración**: CEO-34 vence 2026-06-30; no hay endpoints, wrapper, DDL ni aislamiento por tenant concreto.
    2. **WebSocket no especificado**: falta auth, invalidación, rooms, protocolo y RLS en handlers.
    3. **RLS policies incompletas**: solo `memory_chunk` tiene policy detallada; faltan para `tasks`, identity, `automations`, `audit_event`, etc.
    4. **Tabla `tasks` no se relaciona con los 12 inbound types** de la bandeja/inbox; no hay 13 tipos de inbound como pide el prompt, solo 4 `invocation_mode` y 12 inbox item types.

  P2 (mejora):
    1. Namespace `metadata.mwt.*` debería migrar a `metadata.fbl.*` (deuda técnica documentada).
    2. `SPEC_TENANT_CONTAMINATION_TESTS.md` aún llama a `ENT_PLAT_MULTITENANT` "STUB".
    3. Falta DDL completo de `memory_chunk_vector` con índice HNSW.
