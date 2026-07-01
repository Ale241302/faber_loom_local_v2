---
id: SPEC_FB_INTEGRATION_LAYER_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma
type: spec
stamp: VIGENTE 2026-05-02
fecha: 2026-05-02
agente: Cowork (redaccion) + CEO (decisiones) + ChatGPT (auditoria R5)
aplica_a: [FaberLoom]
implementa:
  - SPEC_FB_AUTH_TENANT_RBAC_v1 (permission checks per endpoint)
  - ENT_FB_USER_LEARNING_MODEL_v1 (endpoints capa 1)
  - ENT_FB_COMMITTEE_OPERATING_MODEL_v1 (endpoints capa 2)
  - SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1.1 (3 flows F1/F2/F3)
relacionado_con:
  - SPEC_FB_FRONTEND_REALTIME_STATE_v1 (consume este contrato)
  - SPEC_FB_EVENTING_AND_OUTBOX_v1 (publica eventos · este los renderiza via WS)
  - SPEC_FB_CONTRACT_TEST_HARNESS_v1 (valida este contrato)
origen: ChatGPT R5 modulariza · scope reducido (auth/topology/observability salen a SPECs propios)
---

# SPEC_FB_INTEGRATION_LAYER_v1
## Contrato frontera frontend ↔ backend (REST + WebSocket + schemas)

## 1. Proposito

Define el **contrato de frontera** entre Mesa de Control (frontend) y backend FaberLoom. Sin esto, "frontend y backend implementan lo que entendieron, no lo canonizado" (R5).

R5 modulariza · scope de este SPEC:
- ✓ REST endpoints por comando
- ✓ WebSocket/SSE protocol
- ✓ Pydantic request/response schemas
- ✓ Error envelope estandar
- ✓ Idempotency key por accion mutante
- ✓ Correlation IDs
- ✓ API versioning /api/v1
- ✓ Generated frontend types
- ✓ Reconnection behavior UI

NO incluye (sale a SPECs propios):
- Auth multi-tenant profundo → `SPEC_FB_AUTH_TENANT_RBAC_v1`
- Rate limiting avanzado → `SPEC_FB_AUTH_TENANT_RBAC_v1`
- Deployment → `SPEC_FB_SYSTEM_TOPOLOGY_v1` (indexa-i)
- Observability stack → `SPEC_FB_SYSTEM_TOPOLOGY_v1` (indexa-i)
- Event bus + outbox → `SPEC_FB_EVENTING_AND_OUTBOX_v1` (indexa-i)

R5 explicit: "Integration Layer debe ser el contrato de frontera, no el closet donde metemos todo antes de que lleguen visitas."

## 2. Stack canonico (de R5)

```
Backend:        FastAPI + Pydantic v2 + SQLAlchemy/Alembic
Frontend:       Next.js App Router + TypeScript
Schema source:  Pydantic models (backend) → OpenAPI 3.1 → TS types (auto-gen)
Auth:           sesiones httpOnly · ver SPEC_FB_AUTH_TENANT_RBAC_v1
DB:             Postgres + pgvector (RLS habilitado)
Cache/realtime: Redis Streams + WebSocket
```

## 3. Headers obligatorios (alineado con SPEC_FB_AUTH_TENANT_RBAC_v1)

```
x-trace-id        ← UUID por request original
x-tenant-id       ← extraido subdomain (auto middleware)
x-actor-id        ← user_id session (auto middleware)
x-actor-role      ← rol activo este request (AM/CURATOR/AUDITOR/CEO)
x-agent-id        ← si aplica · sub-agent invoker
x-command-id      ← UUID comando logico (frontend genera)
x-idempotency-key ← obligatorio en mutaciones (UUID frontend)
x-api-version     ← v1 default
```

Sin headers → 400 Bad Request con body indicando cuales faltan.

## 4. Endpoints REST canonicos · /api/v1/*

### 4.1 Identidad y sesion

```
POST   /api/v1/auth/login                  · ver Auth SPEC
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh
GET    /api/v1/auth/me                     · current user + active roles + active hat
POST   /api/v1/auth/role/switch            · cambia x-actor-role (multi-hat)
POST   /api/v1/auth/2fa/verify
```

### 4.2 Feed (Mesa de Control HERO)

```
GET    /api/v1/feed                        · feed unificado · filtros query
       ?state=urgent|firma|calma           · estado A/B/C
       ?tag=RECIBIDO|LISTO|ALARMA          · filtro tipo
       ?limit=20&cursor=<id>               · paginacion cursor-based

GET    /api/v1/feed/{item_id}              · detalle item

POST   /api/v1/feed/{item_id}/dispatch     · asignar a agente
       body: {agent_name, task_natural_language, options?}

POST   /api/v1/feed/{item_id}/archive      · archivar manualmente
```

### 4.3 Drafts (output de agentes · capa 1)

```
GET    /api/v1/drafts/pending              · drafts esperando firma
GET    /api/v1/drafts/{draft_id}           · detalle draft + evidence bundle

POST   /api/v1/drafts/{draft_id}/approve   · aprobar y enviar
       headers: x-idempotency-key obligatorio
       
POST   /api/v1/drafts/{draft_id}/edit      · editar con razon tipificada
       body: {body_edited, reason: dato|tono|fuente|accion|contexto, free_text?}
       headers: x-idempotency-key obligatorio
       
POST   /api/v1/drafts/{draft_id}/reject    · rechazar con razon tipificada
       body: {reason: dato|tono|fuente|accion|contexto, free_text?}
       headers: x-idempotency-key obligatorio
```

### 4.4 Agent console (entrar a iterar · capa 1)

```
GET    /api/v1/agents                      · lista agentes propios
GET    /api/v1/agents/{agent_name}         · detalle agente + state
POST   /api/v1/agents/{agent_name}/chat    · iterar (chat con agente)
       body: {message, context_overrides?}
GET    /api/v1/agents/{agent_name}/runs    · historico runs del agente
```

### 4.5 User Learning (capa 1 · curaduria personal AM)

```
GET    /api/v1/learning/patterns           · patterns CANDIDATE detectados
GET    /api/v1/learning/patterns/{pid}     · detalle pattern personal

POST   /api/v1/learning/patterns/{pid}/apply
       · aplicar a mi agente · queda en L2 personal
       headers: x-idempotency-key obligatorio
       
POST   /api/v1/learning/patterns/{pid}/edit_apply
       body: {refined_pattern}
       headers: x-idempotency-key obligatorio

POST   /api/v1/learning/patterns/{pid}/ignore
       body: {reason?}
       
GET    /api/v1/learning/applied            · patterns aplicados (L2 personal)
POST   /api/v1/learning/applied/{pid}/rollback
       headers: x-idempotency-key obligatorio
```

### 4.6 Committee (capa 2 · gobernanza · solo CURATOR/CEO)

```
GET    /api/v1/committee/queue             · candidates cumpliendo k-anon ≥5
GET    /api/v1/committee/queue/{cand_id}   · detalle candidate cross-AM

POST   /api/v1/committee/promote/{cand_id} · promote L2 → L3
       body: {seven_checks_passed, rationale}
       headers: x-idempotency-key obligatorio
       
POST   /api/v1/committee/reject/{cand_id}
       body: {reason, evidence_refs}

GET    /api/v1/committee/conflicts         · conflictos fuentes escalados desde capa 1
POST   /api/v1/committee/conflicts/{cid}/resolve
       body: {decision, rationale}
       
POST   /api/v1/committee/freeze/monthly    · freeze pack mensual
       headers: x-idempotency-key obligatorio
```

### 4.7 Audit (rol AUDITOR · read-only · TIER 4 con MFA)

```
GET    /api/v1/audit/trace/{trace_id}      · reconstruir trace completo
GET    /api/v1/audit/events                · eventos filtrables
GET    /api/v1/audit/sha_chain/verify      · verificar integridad chain
GET    /api/v1/audit/restricted/{event_id} · TIER 4 · requiere MFA STEP-UP
```

### 4.8 Sistema (admin tenant · solo CEO)

```
GET    /api/v1/tenant                      · config tenant actual
PATCH  /api/v1/tenant                      · update config (tier · settings)
GET    /api/v1/tenant/users                · usuarios + memberships
POST   /api/v1/tenant/users/invite         · invitar usuario
PATCH  /api/v1/tenant/users/{uid}/roles    · ajustar roles
```

## 5. Schemas request/response · Pydantic v2

R5: "Pydantic/OpenAPI como fuente backend y generar tipos TS para frontend. NO duplicar schemas a mano."

### 5.1 Patron canonico

```python
# Backend Pydantic
class DraftApproveRequest(BaseModel):
    notes: str | None = Field(None, max_length=500)
    
class DraftApproveResponse(BaseModel):
    draft_id: UUID
    sent_at: datetime
    audit_event_id: UUID
    sha_chain_curr: str
```

### 5.2 OpenAPI auto-generation

FastAPI expone `/api/v1/openapi.json` automaticamente. Frontend ejecuta:

```bash
npx openapi-typescript http://localhost:8000/api/v1/openapi.json -o src/types/api.ts
```

CI/CD ejecuta esto en cada push backend · frontend recibe tipos actualizados sin sync manual.

### 5.3 Versioning

- `/api/v1/*` es la version actual · breaking changes requieren nueva version
- `x-api-version: v1` header explicit en frontend · si default cambia
- Deprecated endpoints retornan header `x-deprecated: true · sunset: <ISO8601>`

## 6. Error envelope estandar

```json
{
  "error": {
    "code": "permission_denied",
    "message": "User does not have permission to approve this draft",
    "details": {
      "required_permission": "draft.approve.own",
      "user_roles": ["AM"],
      "target_id": "..."
    },
    "trace_id": "...",
    "request_id": "...",
    "timestamp": "2026-05-02T14:23:11Z"
  }
}
```

Codigos canonicos:

| HTTP | code | Cuando |
|---|---|---|
| 400 | `validation_failed` | Pydantic validation error · body invalido |
| 400 | `missing_required_header` | Falta header x-* obligatorio |
| 401 | `unauthenticated` | Sin sesion valida |
| 403 | `permission_denied` | Sin permission para accion |
| 403 | `tenant_mismatch` | User no es miembro del tenant del subdomain |
| 404 | `not_found` | Recurso no existe O no visible (RLS lo filtra) |
| 409 | `idempotency_conflict` | Mismo idempotency-key con body distinto |
| 409 | `state_conflict` | Recurso en estado incompatible (ej. draft ya aprobado) |
| 422 | `business_rule_violation` | Regla negocio violada (ej. margen <floor) |
| 429 | `rate_limit_exceeded` | Headers Retry-After + body |
| 500 | `internal_error` | Bug · trace_id para debugging |
| 503 | `service_unavailable` | Dependencia caida (DB/Redis/LiteLLM) |

## 7. Idempotency · obligatoria en mutaciones

R5 critico: "WebSocket reconnect, doble click, retry de worker o timeout pueden duplicar drafts, decisiones, pins o eventos."

### 7.1 Reglas

- Toda mutacion (POST/PATCH/DELETE) debe llevar `x-idempotency-key` (UUID generado frontend)
- Backend persiste `idempotency_keys(key, request_hash, response_hash, created_at, expires_at)` por 24h
- Si llega request con mismo key:
  - Mismo body hash → retornar response cacheado (200 + body original)
  - Body distinto → 409 idempotency_conflict
- Keys expiran a 24h · cleanup background

### 7.2 Frontend implementation

```typescript
const idempotencyKey = uuidv4();  // generado al inicio del comando
await fetch('/api/v1/drafts/X/approve', {
  method: 'POST',
  headers: {
    'x-idempotency-key': idempotencyKey,
    'x-trace-id': traceId,
    // ...
  },
  body: JSON.stringify(payload),
});
// reintento con MISMO idempotency-key si network falla · obtiene mismo response
```

## 8. WebSocket protocol

### 8.1 Conexion

```
WSS wss://mwt.faberloom.com/api/v1/ws
   subprotocol: faberloom.v1
   headers: cookie session · x-tenant-id auto via host
```

### 8.2 Mensajes server → client

```json
{
  "type": "feed.item.new",
  "tenant_id": "mwt",
  "actor_id": null,
  "trace_id": "...",
  "data": { "item": {...} }
}

{
  "type": "draft.ready_for_signature",
  "data": { "draft_id": "...", "preview": {...} }
}

{
  "type": "agent.alarma",
  "data": { "agent_name": "@cotizador", "reason": "...", "trace_id": "..." }
}

{
  "type": "pattern.candidate.detected",
  "data": { "pattern_id": "...", "summary": "..." }
}

{
  "type": "session.invalidated",
  "data": { "reason": "logout|expired|forced" }
}
```

### 8.3 Reconnection

- Cliente mantiene `last_event_id` recibido
- Reconnect: query `?since=<last_event_id>` recibe eventos perdidos
- Backend persiste eventos en Redis Streams 24h · usa `XREVRANGE`
- Si gap > 24h · cliente recibe `{type: 'sync_required'}` · debe re-fetch state via REST

### 8.4 Heartbeat

- Server envia `{type: 'ping'}` cada 30s
- Cliente responde `{type: 'pong'}` dentro 10s
- Sin pong → server cierra conexion

## 9. Pagination

Cursor-based · NO offset (escalable):

```
GET /api/v1/feed?limit=20&cursor=eyJpZCI6Ii4uLiJ9

Response:
{
  "items": [...],
  "next_cursor": "eyJpZCI6Ii4uLiJ9",
  "has_more": true
}
```

## 10. Reglas inquebrantables

1. **Headers x-* obligatorios** en TODA request. Faltan = 400.
2. **Idempotency key obligatorio** en mutaciones POST/PATCH/DELETE. Faltan = 400.
3. **Permission check per endpoint** via SPEC_FB_AUTH_TENANT_RBAC_v1. Endpoint sin check = bug critico.
4. **Pydantic schemas como fuente unica de verdad.** TS types auto-generados · NO duplicar manual.
5. **Error envelope estandar.** Sin envelope = bug.
6. **WebSocket con reconnect via last_event_id.** Sin esto · UI inconsistente.
7. **Versioning explicit /api/v1/*.** Breaking changes → /v2 · NO romper /v1.
8. **Cursor pagination · NO offset** (escalable).

## 11. Pendientes [PENDIENTE — NO INVENTAR]

- WebSocket scaling con multiple replicas (sticky sessions? Redis pub/sub fanout?) → SPEC_FB_SYSTEM_TOPOLOGY_v1 (indexa-i)
- File upload endpoints (PDF cotizacion · doc tecnico) → diferido SPEC implementacion
- Bulk endpoints (`/drafts/bulk_approve`) → diferido v2
- GraphQL (si surge demanda · NO Sprint 1) → diferido v3
- Rate limiting detallado per endpoint → SPEC_FB_AUTH_TENANT_RBAC_v1 (alineado)
- Webhook outgoing (notify external systems) → diferido v2

## NO IMPLICA (R4 bonus 5%/50%)

`SPEC_FB_INTEGRATION_LAYER_v1` **NO implica observability stack ni rate limiting avanzado ni deployment**. Esos viven en SPECs propios (Auth + Topology · indexa-i). Integration Layer es contrato frontera · nada mas.

## Changelog
- 2026-05-02 v1.0 VIGENTE: Creacion inicial post R5 ChatGPT con scope reducido (auth/topology/observability salen). Stack canonico FastAPI + Pydantic v2 + Next.js App Router + TS auto-gen via OpenAPI. 8 headers obligatorios x-* desde dia 1. ~40 endpoints REST canonicos cubriendo auth + feed + drafts + agents + user learning capa 1 + committee capa 2 + audit + tenant admin. Pydantic schemas como fuente unica · TS types auto-generados. Error envelope estandar con 12 codigos canonicos. Idempotency obligatoria mutaciones (24h Redis cache). WebSocket protocol con reconnect via last_event_id (Redis Streams 24h). Cursor pagination. 8 reglas inquebrantables. NO implica observability ni rate limiting avanzado.

## Stamp
VIGENTE 2026-05-02 — Contrato frontera limpio · NO el closet donde metemos todo (R5). Sin esto · "frontend y backend implementan lo que entendieron, no lo canonizado" (R5).
