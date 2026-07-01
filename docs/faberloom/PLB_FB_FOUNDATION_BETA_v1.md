# PLB_FB_FOUNDATION_BETA — Playbook ejecución FaberLoom Foundation Beta 13 sprints

id: PLB_FB_FOUNDATION_BETA
version: 1.0
plan_label: v1.3.2-ENMENDADO
status: FIRMADO con enmiendas E-1 a E-6 (changelog v1.3.2, 2026-06-11) — orden de build gobernado por SPEC_FB_BUILD_SEQUENCE v2.1; contenido tecnico integro como referencia
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
subfamilia: FaberLoom
type: PLB
stamp: APROBADO — 2026-05-01
aprobador: CEO (Alvaro) + revisión cruzada ChatGPT
owner: CEO (delegable a Alejandro durante ejecución)
fuente: v1.0 → v1.1 → v1.2 → v1.2.1 → v1.3 → v1.3.1 (revisión cruzada CEO+ChatGPT sesión Cowork 2026-05-01)
aplica_a: [FaberLoom]
requires:
  - SPEC_FABERLOOM_MVP v1.2
  - SPEC_FB_AUTH_TENANT_RBAC v1.0
  - SPEC_FB_SYSTEM_TOPOLOGY v1.0
  - SPEC_FB_TENANT_BOOTSTRAP_SEED v1.0
  - SCH_FB_QUOTE_EVIDENCE_BUNDLE v1.0
  - ENT_FB_RFQ_EXCEPTION_TAXONOMY v1.0
  - ENT_FB_RFQ_REPLAY_SET v1.1
relacionado: ARCH_AGENT_PRINCIPLES v1.5 · POL_DATA_CLASSIFICATION v1.4 · IDX_FB_FOUNDATION_BETA v1.0 · PLB_FB_KICKOFF_PROMPT v1.0 · MANIFIESTO_APPEND_20260501_FOUNDATION_BETA_FIRMADO
deprecates_archived: audit/iteraciones_foundation_beta/PLAN_FABERLOOM_BETA_INICIAL_*.md (4 versiones v1.0 → v1.3)

---

## Principio rector

**Construimos una foundation beta, no un demo. Pero seguimos validando un solo workflow cliente-facing.**

FaberLoom Foundation Beta NO es una "Beta Inicial mínima" de 8 semanas. Es una foundation beta de 13 semanas para validar que FaberLoom puede operar como **plataforma configurable para una PYME B2B**: multi-email, multi-usuario, Voice Profile, Agent Factory, Skill Factory, resiliencia y cotización safety footwear con HITL.

Si esto valida con 5 testers en 13 semanas, la base arquitectónica para Etapas 2-5 está construida. Si no valida, matamos con datos.

**El único workflow cliente-facing validado en E1 sigue siendo:**
```
RFQ safety footwear B2B → draft cotización → HITL → envío aprobado
```

Cualquier otro uso creado por un tester via Skill Factory se considera **experimento interno**, no workflow validado ni métrica de salida.

---

## Tiers de cumplimiento canon — v1.3.1

### TIER 1 — Inquebrantable Foundation Beta (17 ítems)

| # | Ítem |
|---|---|
| 1 | RLS Postgres por tenant en toda tabla con `tenant_id` |
| 2 | HITL absoluto en todo output cliente-facing — cero auto-send |
| 3 | N0–N2 only — N3-N4 prohibidos en upload, hard-block |
| 4 | Audit log append-only con `actor_user_id` + `actor_role_at_decision` |
| 5 | Evidence bundle mínimo (8 campos por línea + 5 por cotización) + SHA-256 hash |
| 6 | Token Ledger simple (10 campos) |
| 7 | 5 roles tenant activos: Owner, Admin, Operator, Supervisor, Viewer |
| 8 | Backup diario automatizado + 1 restore test demostrado antes de abrir beta |
| 9 | 10–15 RFQs reales/semirreales validados por CEO como golden seed |
| 10 | Anthropic-only para LLM — no OpenAI/Voyage/Whisper sin MANIFIESTO_APPEND |
| 11 | Mesa de Control limpia de semántica multi-agente, sub-agentes, pool L3, k-anon |
| 12 | Métrica de salida: ≥4/5 testers usan sin insistencia CEO durante 4 semanas consecutivas |
| 13 | Multi-email nativo: Gmail OAuth + IMAP/SMTP custom (Outlook diferido E2) |
| 14 | Voice Profile completo (persona + tono + glosario + saludo + firma por user) |
| 15 | **Agent Factory + regla single-agent por task** (ver TIER 1 #15 expandido abajo) |
| 16 | **Skill Factory con 14 límites duros** (ver TIER 1 #16 expandido abajo) |
| 17 | Resiliencia full: circuit breakers, retry exponencial, DLQ, skill+agent fault isolation, chaos tests, aislamiento por tenant en worker |

#### TIER 1 #15 — Agent Factory + regla single-agent por task

```
✓ Puede haber múltiples agentes configurables por tenant
✓ Cada task ejecuta exactamente UN agente asignado
✓ Ese agente ejecuta una cadena LINEAL de skills en orden definido
✗ NO sub-agentes
✗ NO orquestación entre agentes
✗ NO un agente llamando a otro agente
✗ NO multi-agent runtime
✗ NO agente que se reasigna a sí mismo a otro task
```

Esto preserva flexibilidad sin violar la regla anti-multiagente (MAST 41-86.7% fallo).

#### TIER 1 #16 — Skill Factory con 14 límites duros

| # | Límite | Implementación |
|---|---|---|
| 1 | Solo skills tipo `classifier`, `generator`, `formatter` | Enum hard en `skills.skill_type` |
| 2 | NO tools externas | Engine no expone tool-calling al SkillSpec |
| 3 | NO HTTP calls desde el prompt o el engine | Solo retrieval interno (KB del tenant) |
| 4 | NO ejecución de código | Engine NO interpreta código del SkillSpec; solo template prompt + Pydantic |
| 5 | NO acceso cross-tenant | RLS hard a nivel DB en cada query del Engine |
| 6 | NO auto-send | Skills no pueden disparar outbound; solo HITL gate aprueba |
| 7 | NO modificación directa de KB | Skills son read-only sobre KB |
| 8 | NO skills compartidas entre tenants | `skills.tenant_id` obligatorio; sin marketplace E1 |
| 9 | Sandbox obligatorio antes de promote | UI bloquea promote si no hay ejecución sandbox exitosa |
| 10 | Promote solo Owner/Admin | Permission matrix enforced |
| 11 | Timeout obligatorio por skill (default 30s, max 60s) | `skills.timeout_ms` con hard cap |
| 12 | Cost cap por skill (default USD 0.50/exec, max USD 2.00) | `skills.cost_cap_usd` con hard cap |
| 13 | Toda ejecución registrada en `skill_executions` | Sin opt-out |
| 14 | Skill failed → task=skill_failed, agente NO se cae | Fault isolation TIER 1 #17 |

**La factory valida configurabilidad, no libertad total.** E1 permite adaptar, no crear un generador industrial de incidentes.

#### Skill Factory ≠ Skill Studio

| Skill Factory E1 permite | NO permite (E1) |
|---|---|
| Clonar skill (system o tenant) | Linter avanzado |
| Editar prompt template | CI gate por skill |
| Definir schema input/output simple | Marketplace cross-tenant |
| Probar en sandbox | Publicación cross-tenant |
| Promover a producción | Version diff visual |
| Ver history versions básica | A/B testing |
| | Tools externas |
| | Runtime code execution |

### TIER 2 — Subset E1, completar E2

| Ítem | E1 |
|---|---|
| Evidence bundle 18/18 campos canónicos | 8+5 en E1; resto E2 |
| Exception taxonomy 15 codes | 15 detectados; QA fuerte solo en 8 prioritarios |
| Skill versioning con diff visual | Version int simple en E1 |
| Microsoft 365 / Outlook OAuth | E2 |
| SHA-chain del audit log completa | E1 acepta SHA-256 evidence; chain audit log E2 salvo Alejandro <1 día |
| Tests automáticos por skill (CI gate) | E1 sandbox manual; CI gate E2 |
| Subdomain por tenant en email outbound | E2 |
| Página `/status` pública para testers | E1 admin-internal; pública E2 |
| Skill marketplace cross-tenant | E4-E5 |

### TIER 3 — Diferido (no entra E1)

CURATOR/AUDITOR operativos, comité k-anon, Layer 3 cross-AM, DMS, marketplace skills, Skill Studio editable con linter/CI, AgentSpec en KB, multi-archetype con composition spec, sub-agentes/orquestación entre agentes, output pinning runtime, AI_GOV runtime completo, bandit routing, provider matrix runtime, cross-tenant learning, voz audio cliente (Whisper), Voice Profile con learning de muestras, A/B testing entre skills, replica + failover Postgres, multi-region, segundo workflow (cobranza o proformas).

---

## Sección 1 — Validación de contexto

### 1.1 Archivos KB consultados

15 archivos canon más los específicos `docs/faberloom/` críticos: SPEC_FB_AUTH_TENANT_RBAC v1.0, SPEC_FB_SYSTEM_TOPOLOGY v1.0, SPEC_FB_TENANT_BOOTSTRAP_SEED v1.0, SCH_FB_QUOTE_EVIDENCE_BUNDLE v1.0, ENT_FB_RFQ_EXCEPTION_TAXONOMY v1.0, ENT_FB_RFQ_REPLAY_SET v1.1, POL_FB_KNOWLEDGE_VALIDITY_AND_EXPIRY v1.

Pendiente lectura por Alejandro pre-código (no bloquean plan): SPEC_FB_EVENTING_AND_OUTBOX, SPEC_FB_FRONTEND_REALTIME_STATE, SPEC_FB_CONTRACT_TEST_HARNESS, SPEC_FB_INTEGRATION_LAYER.

### 1.2 Contradicciones resueltas vs prompt original + canon + iteraciones CEO

| Item | Resolución firmada |
|---|---|
| Workflows E1 | 1 (cotización safety footwear). Cobranza/proformas a E2. **Factories no agregan workflows validados E1.** |
| Hosting | Hostinger KVM 8 (CEO confirma) |
| Roles tenant | 5 activos |
| Providers IA | Anthropic-only |
| Embeddings | Postgres FTS + pg_trgm |
| Voz audio cliente | Diferida E2 |
| Replay set | 10-15 S3, 40 S8 obj, 60 gate E2 |
| Evidence bundle | 8+5 + SHA-256. 18/18 canon a E2 |
| Audit | Append-only + actor_role + SHA-256 evidence. SHA-chain audit completa diferida |
| Headers | 3 obligatorios (x-trace-id, x-tenant-id, x-idempotency-key) |
| Worker queue | Alejandro elige Celery o ARQ <1 día |
| Topología | KVM 8 oficial; Sprint 1 partido en 1A/1B (ver Sprint 1) |
| Sub-agentes | Excluidos E1 (incluso SHADOW). E2+ |
| Email canal | Multi-email nativo: Gmail OAuth + IMAP/SMTP custom. Outlook E2. Resend fallback |
| Voice Profile | E1: persona + tono + glosario + saludo + firma por user. Learning de muestras E3 |
| **Agent Factory** | E1: wizard 4 pasos + AgentSpec en DB + **múltiples agentes configurables por tenant con ejecución single-agent por task** (NO multi-archetype runtime, NO orquestación). Composition spec en KB E3 |
| **Skill Factory** | E1: wizard 5 pasos + clonar (de system o tenant) o crear desde cero + sandbox + SkillSpec en DB + **14 límites duros TIER 1 #16**. Editable con linter+CI E2 |
| Engine ejecutor | E1: genérico, lee SkillSpec de DB, ejecuta vía LiteLLM con Pydantic dinámico, **timeout + cost cap obligatorios por skill** |
| Resiliencia | Camino C completo |
| Plazo | **13 semanas** firmado |

### 1.3 Decisiones bloqueantes pre-Sprint 1

Cero — todas firmadas. Subdecisiones técnicas no bloqueantes para CEO: worker queue (Celery vs ARQ — Alejandro elige <1 día).

---

## Sección 2 — Arquitectura propuesta

### 2.1 Diagrama de componentes

```
            [Cliente final / Operator empresa / CEO tenant]
                           │
                           ▼
                    [Caddy + TLS]
                           │
        ┌──────────────────┴──────────────────┐
        ▼                                     ▼
  [Next.js 15]                      [FastAPI + Pydantic AI]
   Console                              REST + middleware
        │                                     │
        │              ┌──────────────────────┴───────────────────┐
        │              ▼                                          │
        │        [Worker Pool — Celery o ARQ]                     │
        │        ─ Priority queue por tenant_id                   │
        │        ─ Circuit breaker LLM                            │
        │        ─ DLQ → tabla dead_letter_queue                  │
        │        ─ Retry exponencial (3x: 1s, 5s, 25s)            │
        │        ─ Skill execution fault isolation                │
        │              │                                          │
        │              ▼                                          │
        │   ┌──────────────────────────────────────────┐          │
        │   │   ENGINE EJECUTOR GENÉRICO DE SKILLS     │          │
        │   │   ─ Lee AgentSpec de DB                  │          │
        │   │   ─ Itera skills LINEAL (no recursivo)   │          │
        │   │   ─ Pydantic dinámico desde schema       │          │
        │   │   ─ Timeout por skill (30s default,      │          │
        │   │     hard cap 60s)                        │          │
        │   │   ─ Cost cap por skill (USD 0.50 def,    │          │
        │   │     hard cap USD 2.00)                   │          │
        │   │   ─ NO HTTP externo, NO code exec        │          │
        │   │   ─ NO tools externas                    │          │
        │   │   ─ NO acceso cross-tenant (RLS DB hard) │          │
        │   │   ─ Logs por skill_execution             │          │
        │   │   ─ Catch errors → task=skill_failed     │          │
        │   └────┬───────────────────────────────┬─────┘          │
        │        │                               │                │
        │        ▼                               ▼                │
        │  [LiteLLM Gateway]              [Postgres 16 + RLS]     │
        │   Anthropic only                 ─ pg_trgm + FTS        │
        │   Sonnet 4.6 + Haiku 4.5         ─ pgvector reservado   │
        │   Circuit breaker                ─ AOF Redis adyacente  │
        │   Retry + cost log               ─ 20 tablas E1         │
        │        │                                                │
        │        ▼                                                │
        │  [Anthropic API]                                        │
        │                                                         │
        ▼                                                         │
  [WhatsApp Meta Cloud API]  ◄────  webhooks  ────►  [API]        │
  [Gmail OAuth + Watch]      ◄────  push       ────►              │
  [IMAP/SMTP custom poll]    ◄────  poll 60s   ────►              │
  [Resend fallback]                                               │
                                                                  │
                                                                  ▼
                              [MinIO + filesystem KVM]
                              uploads PDF/imagen/email attachments

OBSERVABILIDAD (camino C):
  [Langfuse]  → LLM traces + cost
  [Loki]      → logs JSON estructurados con correlation_id
  [Prometheus]→ métricas componentes + circuit breaker state
  [Grafana]   → dashboards componentes + alertas
  [Health endpoints]  /health/{api,worker,db,redis,litellm,gmail,imap,whatsapp,minio}

DEPLOY: 12 containers Docker Compose en Hostinger KVM 8
BACKUP: pg_dump diario + rsync S3 externo + restore drill mensual
```

### 2.2 Decisiones técnicas

| Decisión | Elección | Por qué |
|---|---|---|
| Hosting | Hostinger KVM 8 | CEO confirma. Canon SPEC_FB_SYSTEM_TOPOLOGY |
| Containers | 12 (8 core + 4 obs) | Camino C requiere observabilidad completa |
| DB | Postgres 16 + pg_trgm + RLS | RLS TIER 1; pg_trgm cubre fuzzy SKU |
| Vector | pgvector schema only, reservado E2 | E1 usa FTS+trigram |
| Worker queue | Alejandro elige Celery o ARQ <1 día | Sin paralelismo de stacks |
| LLM | Anthropic only via LiteLLM (Sonnet 4.6 + Haiku 4.5) | DPA único |
| OCR imagen | Sonnet vision (Anthropic) | Sin DPA adicional |
| Voz audio cliente | Diferida — entrada manual transcrita | Sin DPA Whisper en E1 |
| PDF | WeasyPrint | Open license |
| Auth | FastAPI app-native + httpOnly sessions + Redis | Canon SPEC_FB_AUTH_TENANT_RBAC §1 |
| 2FA | TOTP — obligatorio Owner+Admin, opcional Operator+Supervisor, no Viewer | Subset 5 roles |
| Storage | Filesystem KVM con symlink + MinIO + backup rsync S3 externo | Doble redundancia |
| Frontend | Next.js 15 App Router | Canon |
| Observabilidad | Langfuse + Loki + Prometheus + Grafana | Camino C completo |
| Email inbound | Gmail Watch (push) + IMAP poll 60s + Resend fallback | Cobertura típica PYME LATAM |
| Email outbound | Gmail send API + SMTP custom + Resend fallback | Sale desde el buzón origen del tenant |
| WhatsApp | Meta Cloud API directo, cuenta única MWT | Sin markup Twilio |
| Pydantic dinámico | Engine genera modelo Pydantic desde SkillSpec.schema_json en runtime | Habilita SkillFactory sin reescribir código |
| Engine restrictions | NO HTTP externo, NO code exec, NO tools, NO cross-tenant, timeout + cost cap obligatorios | TIER 1 #16 enforcement runtime |
| Circuit breaker | py-breaker o impl propia simple | <1 día setup |
| DLQ | Tabla `dead_letter_queue` + UI admin | Visible y accionable |

### 2.3 Schema DB E1 (20 tablas + ajustes)

Schema heredado de v1.3 con 2 ajustes en `skills`:

```sql
skills (
  id uuid pk, tenant_id uuid fk,
  name text, description text,
  skill_type text check in ('classifier','generator','formatter'), -- TIER 1 #16.1
  prompt_system text, prompt_user text,
  schema_input jsonb, schema_output jsonb,
  model text check in ('haiku-4.5','sonnet-4.6'),
  origin text check in ('system','cloned','user_created'),
  parent_skill_id uuid,
  version int default 1,
  status text check in ('draft','active','deprecated'),
  -- TIER 1 #16.11 + #16.12 ajustes:
  timeout_ms int default 30000 check (timeout_ms <= 60000),
  cost_cap_usd numeric(6,4) default 0.5 check (cost_cap_usd <= 2.0),
  last_sandbox_test_at timestamptz, -- TIER 1 #16.9: sandbox obligatorio antes de promote
  promoted_by uuid, promoted_at timestamptz,
  created_by uuid fk users, created_at timestamptz
)
```

`agents.health_state` jsonb captura `failure_rate`, `last_error`, `degraded_at` para fault isolation TIER 1 #15.

Resto del schema idéntico a v1.3 (tenants, users, sessions, invitations, audit_log, rbac_overrides, mailboxes, whatsapp_accounts, email_threads, documents, document_chunks, kb_assertions, agents, agent_skills, agent_channels, tasks, drafts, draft_decisions, skill_executions, llm_calls, dead_letter_queue, circuit_breakers, gold_candidates_v).

**RLS uniforme TIER 1:** todas las tablas con `tenant_id`. 5 tests cross-tenant en CI Sprint 1A.

### 2.4 Endpoints API mínimos

Heredado de v1.3 sin cambios. Endpoints clave:
- Auth: `/auth/login`, `/auth/2fa/verify`, `/me`
- Users tenant: `/tenants/{id}/users`, `/tenants/{id}/invitations`, `/invitations/{token}/accept`, `/users/{id}/role`, `/users/{id}/suspend`
- Mailboxes: `/tenants/{id}/mailboxes`, `/mailboxes/{id}/oauth/google/callback`, `/mailboxes/{id}/test`
- Webhooks: `/webhooks/gmail`, `/webhooks/whatsapp`
- Documents: `/tenants/{id}/documents`, `/documents/{id}/verify`
- Agents: `/tenants/{id}/agents`, `/agents/{id}/skills`, `/agents/{id}/channels`
- Skills: `/tenants/{id}/skills`, `/skills/{id}/sandbox-test`, `/skills/{id}/promote`
- Tasks/HITL: `/tenants/{id}/tasks`, `/tasks/{id}`, `/tasks/{id}/reassign`, `/drafts/{id}/{approve|edit|reject}`
- Resiliencia: `/tenants/{id}/dlq`, `/dlq/{id}/retry`, `/admin/health`, `/admin/circuit-breakers`
- Métricas: `/tenants/{id}/metrics`

### 2.5 Flujo end-to-end RFQ → cotización

Igual a v1.3 con validaciones TIER 1 #16 enforcement runtime:
- Cada skill ejecutada respeta su `timeout_ms` y `cost_cap_usd`
- Engine NO permite tools externas, HTTP externo ni code exec
- RLS hard a nivel DB en cada query
- Si una skill falla → `task.status=skill_failed`, `failed_skill_id` + `failed_reason`, agente sigue procesando otros tasks normalmente

SLO E1: P95 inbound→pending < 12s. Costo medio < USD 0.30/cotización. Disponibilidad target 95%.

---

## Sección 3 — Plan por sprint (13 sprints × 1 semana)

### Sprint 1 — Stack base + auth + RLS + 5 roles + audit + observabilidad (partido en 1A/1B)

**Objetivo:** infraestructura productiva en KVM 8 con base sólida + observabilidad completa. Sprint 1 partido en dos gates internos para evitar bloqueo total si observability se atrasa.

#### Sprint 1A — Core boot (debe quedar funcionando primero)

**Entregables:**
1. KVM 8 operativo + Docker Compose con 8 containers core (caddy, web, api, worker, postgres, redis, litellm, langfuse)
2. Caddy TLS Let's Encrypt
3. Schema 20 tablas + RLS policies + 5 tests integration cross-tenant
4. FastAPI auth (httpOnly + Redis) + 2FA TOTP Owner+Admin
5. Permission matrix con 5 roles tenant
6. Audit log append-only simple con `actor_user_id` + `actor_role_at_decision` (sin SHA-chain todavía)
7. 3 headers obligatorios middleware
8. Backup script (pg_dump diario + rsync S3 externo)
9. Healthcheck básico `/health` + Docker `restart: unless-stopped`
10. CI/CD GitHub Actions: lint, typecheck, tests unit, RLS cross-tenant, deploy on merge
11. Landing pública + login

**DoD 1A:**
- 2 tenants seed; 5 escenarios cross-tenant retornan 0 filas
- Login E2E + 2FA Owner+Admin pasa
- Audit log con 50+ entries
- Backup script corre exitoso en cron de 24h
- 8 containers core operando con auto-restart

#### Sprint 1B — Observability + restore (puede atrasarse sin bloquear S2)

**Entregables:**
12. 4 containers obs adicionales: minio, loki, prometheus, grafana
13. Loki ingesta logs JSON estructurados con correlation_id
14. Prometheus scrape API/worker + 5 alertas básicas (api_5xx_rate, worker_jobs_pending, postgres_uptime, disk_usage, llm_cost_daily)
15. Grafana 3 dashboards (componentes, errores, latencia)
16. Restore test demostrado <1h hasta sistema operativo en staging

**DoD 1B:**
- Grafana renderiza 3 dashboards con datos reales
- 5 alertas Prometheus disparan correctamente en simulación
- Restore drill <1h documentado

**Regla de gate interno:**
> Si 1B se atrasa, NO bloquea inicio de S2 siempre que 1A esté completo: logs JSON + RLS tests + backup + healthcheck básico operando. 1B completa en buffer S12 si es necesario.

**Riesgos top 3:**
- KVM 8 sin recursos para 12 containers concurrentes → benchmark Sprint 1A; si falla, 1B reduce a Loki+Prometheus solamente, Grafana a buffer
- Permission matrix de 5 roles con bugs sutiles → test exhaustivo por par (rol, recurso, action)
- 2FA Owner backup codes perdidos → almacenamiento físico + gestor contraseñas

**Dependencias:** decisiones CEO firmadas en kickoff.

**Tests:** unit Pydantic + RLS integration + 2FA flow + permission matrix por rol + backup/restore drill + Playwright login E2E.

---

### Sprint 2 — KB upload + parse + verify + replay set seed CEO

(Idéntico a v1.3)

**Objetivo:** owner sube docs + verifica afirmaciones; CEO en paralelo curate 10-15 RFQs reales del historial MWT.

**Entregables:**
1. Tablas `documents`, `document_chunks` con FTS+pg_trgm índices, `kb_assertions`
2. Endpoint upload + MinIO storage + filesystem KVM symlinks
3. Parsers PDF (pdfplumber), Excel (openpyxl), Markdown directo
4. Chunker 800 tokens overlap 100; tsvector con setweight A/B/C
5. Wizard 4 pasos KB: upload → parse preview → afirmaciones HIGH/LOW → reindex
6. Validez per-document
7. Paralelo CEO Sem 0-S2: curaduría 10-15 RFQs reales MWT

**DoD:**
- 5 docs Marluvas reales subidos tenant MWT, 100% chunks FTS-indexed
- ≥10 afirmaciones HIGH manualmente
- Búsqueda FTS+pg_trgm <300ms para 5k chunks
- 10-15 RFQs validados CEO disponibles para S3

**Riesgos top 3:**
- Parser Excel pricelist con celdas merged → 1.5d buffer
- Curaduría CEO se patea → bloque de 3h dedicado en S2
- Sinónimos ausentes (zapato seguridad ≠ bota industrial) → diccionario sinónimos manual en `tenants.agent_config.glossary`

**Dependencias:** S1A cerrado. (S1B puede estar pendiente.)

---

### Sprint 3 — Engine ejecutor genérico + skills system + Tier 0 + clasificar_rfq + 15 exception codes

(Heredado de v1.3 con TIER 1 #16 enforcement)

**Objetivo:** Engine ejecutor lee SkillSpec de DB y ejecuta vía LiteLLM con Pydantic dinámico + **timeout + cost cap + restricciones runtime**.

**Entregables:**
1. Tablas `agents`, `skills`, `agent_skills`, `agent_channels` con seed inicial
2. **Engine ejecutor genérico** con TIER 1 #16 enforcement:
   - Lee AgentSpec + SkillSpec de DB
   - Itera skills LINEAL (no recursivo)
   - Pydantic dinámico desde `skills.schema_input/output`
   - Llama LiteLLM con prompt + input mapping
   - **Timeout por skill** (default 30s, hard cap 60s) — kill si excede
   - **Cost cap por skill** (default USD 0.50, hard cap USD 2.00) — abort si excede pre-call
   - NO HTTP externo, NO code exec, NO tools externas
   - RLS hard a nivel DB
   - Persiste `skill_executions` row por cada skill
   - Catch errors → `task.status=skill_failed`, `failed_skill_id`, agente NO se cae
3. 4 skills system creadas como SkillSpec en DB (`origin='system'`, inmutables):
   - `classify_rfq` (Haiku 4.5)
   - `retrieve_kb` (sin LLM)
   - `generate_quote` (Sonnet 4.6) — placeholder, completa en S4
   - `format_output` (Sonnet 4.6) — placeholder, completa en S5
4. `apps/api/tier0` con 8 reglas LATAM
5. Detección 15 exception codes en `classify_rfq`
6. Endpoint `POST /tenants/{id}/tasks` consume input → engine
7. Logging completo `llm_calls` + `skill_executions`
8. Soporte imagen via Sonnet vision

**DoD:**
- 10 RFQs golden procesados; ≥8 con clasificación correcta
- Tier 0 cubre ≥40% sin invocar Haiku
- 8 prioritarios exception codes detectados ≥6/8
- Engine ejecuta skills system end-to-end con Pydantic dinámico
- **Test enforcement TIER 1 #16:** intentar skill con timeout >60s → rechazado en validation; skill con HTTP call → rechazado; skill cross-tenant → 403
- P95 latencia clasificar < 1500ms; costo medio < USD 0.001/RFQ
- Skill failure aislada: si una skill falla, no propaga al agente

**Riesgos top 3:**
- Pydantic dinámico complejo → reservar 2 días buffer; fallback estático si bloquea
- Tier 0 cobertura <40% → ajustar threshold a 0.6
- Imagen RFQ borrosa → forzar HITL

**Dependencias:** S2 cerrado.

---

### Sprint 4 — generar_cotizacion + evidence bundle 8+5 + retrieval + pricing

(Idéntico a v1.3)

**Objetivo:** skill `generate_quote` system produce draft con evidence bundle subset E1 + SHA-256.

(Entregables, DoD, riesgos heredados de v1.3)

---

### Sprint 5 — Mesa Control + WhatsApp + Email Gmail OAuth + IMAP custom + multi-buzón + formatear_output

(Idéntico a v1.3)

**Objetivo:** operator revisa drafts en Mesa Control limpia; cliente final recibe respuesta desde el buzón origen del tenant.

(Entregables, DoD, riesgos heredados de v1.3 incluyendo fallback "consola web + copia manual a WhatsApp MWT, no Telegram")

---

### Sprint 6 — Agent Factory + Skill Factory + sandbox + asignaciones + límites duros

**Objetivo:** Owner/Admin tenant puede crear agentes y skills con **14 límites duros TIER 1 #16** enforced + sandbox obligatorio antes de promote.

**Entregables:**
1. **Agent Factory wizard** (4 pasos) → POST `/tenants/{id}/agents`:
   - Identidad (nombre, descripción, persona/Voice Profile, tono, glosario)
   - Skills asignadas con drag-drop (orden de ejecución lineal)
   - Canales que escucha (mailboxes + WhatsApp del tenant)
   - HITL config (operator default, fallback supervisor, timeout horas)
2. **Skill Factory wizard** (5 pasos) con TIER 1 #16 enforced:
   - Paso 1: clonar (system o tenant) o crear desde cero
   - Paso 2: identidad (nombre, descripción, **tipo: classifier/generator/formatter SOLO**)
   - Paso 3: prompt template con variables `{{input.field}}`
   - Paso 4: schema input/output con form simple
   - Paso 5: modelo (Haiku/Sonnet) + **timeout** (max 60s) + **cost cap** (max USD 2.00) + sandbox test
3. **Sandbox obligatorio antes de promote** (TIER 1 #16.9):
   - Pegás RFQ de prueba, ejecuta skill aislada, muestra output JSON + tokens + costo + latencia
   - UI bloquea promote si no hay ejecución sandbox exitosa registrada
   - `skills.last_sandbox_test_at` se actualiza
4. **Promote solo Owner/Admin** (TIER 1 #16.10): permission matrix enforced en endpoint `/skills/{id}/promote`
5. Skills system inmutables (no editables, solo clonables); seed automático en tenant new
6. UI listado agentes + skills + edición + clonación
7. Drag-drop asignar skills a agente con orden
8. UI asignar canales (mailboxes + WhatsApp) a agentes
9. Routing dinámico: `task.agent_id` se determina por `mailbox.default_agent_id` o `whatsapp.default_agent_id` o assignment manual
10. **Validador TIER 1 #16 en backend**: rechaza SkillSpec con
    - skill_type fuera de enum
    - prompt template con `<script>`, fetch, exec, eval (regex check)
    - schema con tipos no whitelisted
    - timeout > 60s
    - cost_cap > USD 2.00

**DoD:**
- Owner crea 1 agente custom + 1 skill clonada + asigna ambos a un buzón → flujo completo opera
- Sandbox test ejecuta sin afectar producción; 10 ejecuciones registradas
- Agente custom procesa 1 RFQ end-to-end en staging
- Listado muestra agente system + custom; edición opera correctamente
- **Test TIER 1 #16:** intentar promote sin sandbox → rechazado. Operator intenta promote → 403. Skill con timeout 120s en wizard → validation error. Skill con prompt `<script>alert</script>` → validation error.

**Riesgos top 3:**
- Pydantic dinámico (heredado S3) con bugs runtime → tests robustos por skill_type
- Wizard UI complejo → usar component library robusta (shadcn/ui) y enfocar en happy path
- Sandbox test con costo descontrolado → cap de tokens_in en sandbox + cost_cap por exec

**Dependencias:** S5 cerrado. Engine ejecutor de S3 estable.

**Tests:** unit AgentSpec + SkillSpec validation + TIER 1 #16 enforcement; integration crear agente + skill + sandbox + promote + ejecutar; permission tests (solo Owner/Admin promove).

---

### Sprint 7 — Voice Profile + multi-usuario tenant + invitaciones + 5 roles + onboarding

(Idéntico a v1.3)

---

### Sprint 8 — Resiliencia full (camino C)

(Idéntico a v1.3)

---

### Sprint 9 — Token Ledger + dashboard 4 KPIs + gold candidates tabla + alertas

(Idéntico a v1.3)

---

### Sprint 10 — Onboarding 4 pasos polished + 5 cuentas + DPA + bootstrap checks

(Idéntico a v1.3)

---

### Sprint 11 — QA intensivo + 5 testers operando + survey + decisión

(Idéntico a v1.3)

---

### Sprint 12 — Buffer slip + iteración con feedback testers + completar S1B si quedó pendiente

**Objetivo:** absorber slip + iterar feedback + cerrar gates internos pendientes (Sprint 1B observability si se atrasó).

(Resto idéntico a v1.3)

---

### Sprint 13 — Cierre + decisión avance/kill + handoff a Etapa 2

(Idéntico a v1.3)

---

## Sección 4 — Métricas y kill criteria E1

| Dimensión | Métrica | Umbral | Medición |
|---|---|---|---|
| Adopción real | Testers con ≥10 tareas en sem 6 | ≥4/5 | SQL `tasks` count |
| Adopción sin presión | Testers sin insistencia CEO 4 sem consecutivas | ≥4/5 | Survey + log |
| Calidad output | % aprobado sin edits últimas 30 | ≥60% | SQL `drafts` |
| Costo IA | USD/tarea aprobada | <USD 0.50 | `llm_calls.cost_usd` |
| Latencia | P95 inbound→pending | <12s | Prometheus |
| Privacy | RLS leak / DPA / N3+ | 0 | Audit log + pen-test |
| Irreversibles | Cotizaciones a destinatario equivocado | 0 | CEO weekly review |
| Reducción tiempo | Auto-reportado vs manual | ≥5x | Survey + 2 cronómetro |
| Resiliencia | Disponibilidad sistema | ≥95% | Prometheus uptime |
| **Factory adoption** | **Tenants amigos que crearon ≥1 agente custom o skill clonada** | **≥2/3 amigos** | SQL `agents` + `skills` filtered |
| Replay set | Acumulado real/semirreal | ≥40 (objetivo, no kill) | `replay_set_cases` |

### Kill criteria

1. <3/5 testers ≥3 tareas/sem en sem 6 → producto no resuelve dolor real
2. <3/5 testers sin insistencia CEO 4 sem consecutivas → señal "amistad", no fit (TIER 1 #12)
3. Edit rate sostenido ≥60% últimas 30 → modelo no genera drafts útiles
4. Costo medio >USD 1.00/tarea con caching → economía rota
5. ≥1 incidente privacy o irreversible → riesgo regulatorio supera valor
6. Reducción tiempo ≤2x auto-reportado → no hay ROI
7. Disponibilidad <85% en S10-S11 → arquitectura falla bajo uso real
8. **Cero tenants amigos crearon agente o skill custom** → factories no resuelven necesidad real

---

## Sección 5 — Decisiones CEO firmadas para kickoff Sprint 1A

| # | Decisión | Resolución |
|---|---|---|
| 1 | Hosting | Hostinger KVM 8 |
| 2 | Canal cliente | WhatsApp + Gmail OAuth + IMAP custom + Resend fallback |
| 3 | Roles activos E1 | 5 roles tenant: Owner/Admin/Operator/Supervisor/Viewer |
| 4 | Idioma agente | Español neutro LATAM con defaults MWT (configurable en Voice Profile) |
| 5 | Costo IA visible | Solo Owner+Admin tenant + CEO super-admin |
| 6 | Gold candidates | Vista materializada en DB; sin UI curación E1 |
| 7 | Providers IA | Anthropic-only |
| 8 | Replay set | 10-15 mín S3, 40 obj S8, 60 gate E2 |
| 9 | Audit | Append-only + actor_role + SHA-256 evidence |
| 10 | Topología | KVM 8; 12 containers con Sprint 1 partido en 1A core + 1B observability |
| 11 | Worker queue | Alejandro elige <1 día |
| 12 | Embeddings | Postgres FTS + pg_trgm |
| 13 | Email outbound | Sale desde el buzón origen del tenant |
| 14 | Subdomain por tenant | Diferido E2 |
| 15 | Voice Profile | Persona+tono+glosario+saludo por tenant; firma por user |
| 16 | **Agent Factory** | Wizard 4 pasos. **Múltiples agentes configurables por tenant con ejecución single-agent por task** (NO multi-archetype runtime, NO orquestación) |
| 17 | **Skill Factory** | Wizard 5 pasos + clonar/zero + sandbox obligatorio + **14 límites duros TIER 1 #16** + promote solo Owner/Admin |
| 18 | Engine ejecutor | Genérico, lee SkillSpec de DB, Pydantic dinámico, timeout + cost cap obligatorios, NO HTTP externo, NO code exec, NO tools, NO cross-tenant |
| 19 | Resiliencia | Camino C completo |
| 20 | Plazo | **13 semanas** |
| 21 | **Workflow validado E1** | **Solo cotización safety footwear B2B**. Factories no agregan workflows validados. Cualquier otro uso = experimento interno |

### Compromisos CEO esta semana (pre-kickoff)

- Confirmar 3 amigos B2B con incentivo + commitment verbal
- Iniciar trámite WhatsApp Business MWT con Meta
- Iniciar trámite Google OAuth approval para FaberLoom
- Iniciar redacción DPA legal
- Pre-curar `client_map.xlsx` MWT — entrega lunes S4

### 5.B Condiciones operativas de kickoff (firmadas con v1.3.1)

Estas tres condiciones NO son bloqueantes de firma del plan, pero deben quedar claras en kickoff Sprint 1A. Alejandro las recibe como parte del contrato de ejecución.

| # | Condición | Detalle |
|---|---|---|
| **A** | **Worker queue elegido en Sprint 1A — congelado para E1** | Alejandro elige Celery o ARQ en S1A. El que levante en <1 día. Desde el momento en que se elige, queda congelado para los 13 sprints. NO se permite paralelismo de stacks (no Celery+ARQ); NO se cambia a mitad de E1 aunque aparezca el otro como mejor opción. Cambio = MANIFIESTO_APPEND firmado por CEO |
| **B** | **Resend con límite de uso** | Resend es fallback outbound, no canal principal. NO debe saltarse el buzón origen del tenant. Si Gmail OAuth o IMAP/SMTP custom funciona, esos van primero. Resend solo se invoca cuando el provider primario falla y el circuit breaker abre. Para datos N1-N2 (clientes reales), DPA Resend debe estar cubierto antes de S10 o limitar a mensajes no sensibles (notificaciones internas, bounces, etc.). Métrica de control: % outbound vía Resend < 5% del total mensual |
| **C** | **Restore test antes de abrir beta externa con datos reales** | Sprint 1B (observability completa) puede atrasarse a S12 sin bloquear S2. PERO el restore test demostrado de Sprint 1B NO puede faltar antes de S10 (onboarding 5 cuentas + DPA). Es decir: cuando los 3 amigos firmen DPA y suban dato real, el restore drill ya tiene que estar probado. Si en S10 el restore no está demostrado, S10 se freezar hasta que esté |

---

## Sección 6 — Riesgos arquitectónicos top 5

| Riesgo | Prob | Impacto | Mitigación |
|---|---|---|---|
| RLS leak cross-tenant | Media | Catastrófico | 5 tests integration en CI desde S1A día 3; pen-test S11 |
| Pydantic dinámico de Engine ejecutor con bugs runtime | Alta | Alto | 2 días buffer S3; fallback estático si bloquea; tests por skill_type |
| **Skill Factory genera skills con prompts/schemas dañinos** | Media | Alto | TIER 1 #16 con 14 límites duros enforced en validador backend; sandbox obligatorio; cost cap + timeout hard |
| Mockup arrastra semántica multi-agente al UI | Alta | Medio | Copy review checklist 12 ítems S5 con bloqueo merge |
| KB pequeña + retrieval FTS no cubre dolor → calidad < umbral | Alta | Alto (kill) | Catálogo seed completo MWT pre-S4; diccionario sinónimos manual; re-rank Haiku contingencia S5 |

### Single Points of Failure (SPOF) aceptados E1

- Postgres se cae → todo cae. Mitigación E1: backup diario + restore probado. Replica + failover E3.
- Hostinger KVM 8 hardware → todo cae hasta vuelta. Mitigación E1: monitoreo uptime + backup off-site. Multi-region E3+.
- Anthropic upstream → no se generan drafts. Sin mitigación E1.

---

## Sección 7 — Veredicto final

**Proceder con v1.3.1 como FaberLoom Foundation Beta — 13 semanas — camino C completo.**

Hostinger KVM 8 confirmado. Anthropic-only firme. Multi-canal nativo aprobado. Multi-usuario real con 5 roles aprobado. Voice Profile aprobado. Agent Factory y Skill Factory aprobadas **con límites duros**. Resiliencia camino C aprobada. Sprint 1 partido en 1A/1B para evitar bloqueo total.

### NO reabrir

- hosting (Hostinger KVM 8)
- stack (FastAPI + Next.js + Postgres + Redis + LiteLLM + Anthropic)
- wedge safety footwear
- Anthropic-only
- HITL absoluto
- single-agent por task
- no DMS
- no AI_GOV runtime
- no sub-agentes
- no marketplace cross-tenant
- no skills compartidas entre tenants
- no tools externas en skills
- no code execution

### Lo que esto valida con 5 testers en 13 semanas

- ¿Una empresa B2B PYME LATAM puede operar FaberLoom como plataforma configurable?
- ¿Voice Profile + Agent Factory permite que cada empresa moldee el sistema a su realidad?
- ¿Skill Factory con 14 límites permite cubrir excepciones que el agente system no cubre — sin convertirse en pantano?
- ¿Multi-canal cubre los flujos reales de PYME LATAM?
- ¿Resiliencia C es suficiente para que los testers no pierdan confianza ante el primer fallo?
- ¿5 personas cotizan más rápido, con menos errores, sin que el CEO los persiga durante 4 semanas consecutivas?

Si sí → Etapa 2 arranca con base sólida.
Si no → matamos con datos.

### Lo que NO valida E1

- Skill marketplace cross-tenant
- AI_GOV runtime + governance
- Multi-archetype con composition spec
- Sub-agentes / orquestación
- DMS integration
- Voz audio nativa (Whisper)
- Microsoft 365 / Outlook
- Workflow #2 (cobranza o proformas)
- Skills con tools externas / HTTP / code exec

Eso espera a Etapas 2-5.

### La frase operativa

**Construimos una foundation beta, no un demo. Pero seguimos validando un solo workflow cliente-facing.**

La diferencia entre plataforma y pantano es una lista de límites. Aquí ya tenemos la pala (factories) y la cerca (TIER 1 #16).

### Ajuste único pediría reconsiderar (post-aprobación)

Delegar curaduría 10-15 RFQs reales paralelo S2 a sesión Cowork dirigida (2-3h CEO supervisando) en vez de bloque solo CEO. Ahorro: ~1 día CEO reasignable a entrevistas pre-S4 con los 3 amigos.

---

Changelog:
- v1.3.2-ENMENDADO (2026-06-11): CEO autoriza levantamiento de items firmados via mandato explicito sesion Cowork 2026-06-11 ("tienes libertad para levantar cualquier cosa firmada"). SEIS enmiendas - el contenido del plan queda integro como referencia; lo enmendado se declara superseded con su doc rector:
  E-1 ORDEN DE BUILD: los 13 sprints como secuencia y el plazo de 13 semanas quedan superseded por SPEC_FB_BUILD_SEQUENCE v3.0 (E0-E4 + E2.5 comercial paralela, ~9-10 sem a interno). Siguen vigentes: TIER 1 (con la excepcion E-4), kill criteria integros, decisiones CEO #1-21 salvo las enmendadas abajo. Los contenidos tecnicos de S1A/S2/S3-S5 se reutilizan donde BUILD_SEQUENCE los referencia.
  E-2 TOPOLOGIA Y OBSERVABILIDAD: decision #10 (12 containers) y Sprint 1B (grafana/loki/prometheus/minio self-host) superseded por 6 containers core + observabilidad gestionada (Langfuse Cloud + uptime externo + alertas costo). KVM 8 se mantiene (decision #1 intacta). Restore test pre-datos-reales (condicion C) se mantiene. STORAGE DE ADJUNTOS (dependia de MinIO): filesystem KVM + backup diario existente; migracion a S3 solo si E3 lo exige.
  E-3 ENGINE DE SKILLS: Sprint 3 engine bespoke (SkillSpec en DB + Pydantic dinamico) superseded por skill = markdown versionado + tools allowlist + schema de salida, ejecutado como capa fina sobre SDK estandar. Se conservan de S3: Tier 0 deterministico, 15 exception codes, limites duros (NO HTTP externo, NO code exec, timeout + cost cap, NO cross-tenant). Allowlist de tools E1-E2 (8): kb_search, get_client, get_prices, create_draft, send_email_tenant, get_invoice_status, log_audit, schedule_job. TIER 1 #16 (limites Skill Factory) se mantiene para cuando las factories entren (E3+).
  E-4 ROLES: decision #3 y TIER 1 #7 (5 roles tenant activos) enmendados a 2 roles en E1 (Owner, Operator); los 5 roles entran en E3 con el primer tenant externo. El permission matrix de 5 roles queda como diseno de referencia.
  E-5 CANALES: decision #2 (WhatsApp + Gmail OAuth + IMAP custom + Resend) enmendada a email-only en E1-E2 (Gmail OAuth out; IMAP in para lectura); WhatsApp Business y multi-buzon completo a E3 (tramites Meta/Google arrancan en paralelo, no bloquean). Condicion B (Resend <5%) se mantiene si Resend se usa.
  E-6 RETRIEVAL: decision #12 (Postgres FTS + pg_trgm como mecanismo unico) matizada: retrieval primario E1 = seleccion de documentos completos via taxonomia KB + prompt caching (los corpus de 1 tenant caben en la economia del cache); FTS+pg_trgm queda como mecanismo secundario para lookup exacto (SKUs, codigos); chunking a nivel fragmento diferido a corpus que excedan el cache (E3+). Eval set de retrieval (E1 sem 2) valida esta decision con datos.
  Origen: EVAL_STRAT_2026-06-09 + revision de arquitectura 2026-06-10 + AUDIT_FB_MODULAR_2026-06-11 (vacio #1: 3+ contradicciones acumuladas sin enmienda formal). Documentos rectores: SPEC_FB_BUILD_SEQUENCE v2.1, SPEC_FB_ROUTING_PRESETS v1, SPEC_FB_ARCHETYPE v1.1, SPEC_FB_VOICE_HUMANIZER v2.1.
- v1.3.1-FIRMADO (2026-05-01 cierre): CEO firma como contrato de ejecución. Agregada Sección 5.B con 3 condiciones operativas de kickoff: (A) worker queue congelado en S1A, (B) Resend con límite <5% outbound mensual y DPA cubierto antes S10 o limitarse a mensajes no sensibles, (C) restore test demostrado antes de S10 (apertura beta con datos reales). Status: FIRMADO. Próximo paso: kickoff Sprint 1A con Alejandro.
- v1.3.1 (2026-05-01): **Renombre a Foundation Beta** + 10 cambios firmados CEO+ChatGPT:
  1. Plan renombrado de `BETA_INICIAL` a `FOUNDATION_BETA` para reflejar scope real (foundation beta, no MVP mínimo)
  2. Principio rector explícito: "construimos foundation beta, no demo; un solo workflow cliente-facing validado"
  3. TIER 1 #16: Skill Factory con 14 límites duros enforced (solo classifier/generator/formatter, no tools, no HTTP, no code exec, no cross-tenant, no auto-send, no mod KB, no shared, sandbox obligatorio, promote Owner/Admin, timeout + cost cap, fault isolation)
  4. TIER 1 #15: regla single-agent por task explícita (múltiples agentes configurables, ejecución lineal, no orquestación, no sub-agentes)
  5. Sprint 1 partido en 1A (core boot) + 1B (observability) con gate interno; 1B puede atrasar a S12 sin bloquear S2
  6. "multi-archetype" reemplazado por "múltiples agentes configurables por tenant con ejecución single-agent por task"
  7. Skill Factory ≠ Skill Studio aclarado (qué permite y qué no en E1)
  8. Métrica factory adoption corregida: ≥2/3 amigos (no ≥3/4 excluyendo MWT que estaba ambiguo)
  9. Wedge E1 reforzado: factories no agregan workflows validados; usos custom = experimento interno
  10. Sección 7 reescrita: Foundation Beta no Beta Inicial; lista NO REABRIR explícita
- v1.3 (2026-05-01): Re-scope CEO post-iteración. 13 sem. Multi-usuario tenant + multi-email + Voice Profile + Agent Factory + Skill Factory + Engine ejecutor + Resiliencia C. 12 containers. Schema 20 tablas.
- v1.2.1 (2026-05-01): Microcorrecciones editoriales (Telegram→consola web, 11 tablas, replay_set no bloquea S1).
- v1.2 (2026-05-01): Consolidado autocontenido. TIER 1 limitado a 12 ítems; Hostinger KVM 8 confirmado; Anthropic-only puro.
- v1.1 (2026-05-01): Patch sobre v1.0 con lectura `docs/faberloom/`.
- v1.0 (2026-05-01): Plan inicial 8 sprints.
