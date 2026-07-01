---
id: SPEC_FB_EVENTING_AND_OUTBOX_v1
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
  - SPEC_FB_INTEGRATION_LAYER_v1 (UI consume eventos via WebSocket)
  - SPEC_FB_AUTH_TENANT_RBAC_v1 (audit log con SHA-chain · cada evento firmado)
relacionado_con:
  - SPEC_AUDIT_MODULE (sealed previo · SHA-chain integrity)
  - SPEC_FB_VERTICAL_AM_v1.1 (eventos del flow F1/F2/F3)
  - ENT_FB_USER_LEARNING_MODEL_v1 (eventos pattern.candidate.detected)
origen: ChatGPT R5 renombro de "event_bus" a "eventing_and_outbox" · separar log canonico vs bus operativo
---

# SPEC_FB_EVENTING_AND_OUTBOX_v1
## Sistema nervioso del FaberLoom · event log + outbox + bus operativo

## 1. Proposito

R5 critico: "el riesgo no es solo publicar eventos · el riesgo real es perderlos · duplicarlos o no poder reconstruir que paso." Por eso el SPEC se renombra de "event_bus" a "eventing_and_outbox".

Define las 4 capas de eventos del sistema:
1. **Event log canonico** · Postgres (audit · reconstruction · source of truth)
2. **Outbox pattern** · transaccional · garantiza at-least-once
3. **Transport / bus operativo** · Redis Streams (distribucion realtime + workers)
4. **UI fanout** · WebSocket/SSE (consumidores frontend)

Sin separar capas, "WebSocket reconnect, doble click, retry de worker o timeout pueden duplicar drafts, decisiones, pins o eventos" (R5).

## 2. Las 4 capas

```
┌──────────────────────────────────────────────────────────────────┐
│ CAPA 1 · EVENT LOG CANONICO (Postgres)                          │
│   - Tabla event_log append-only                                  │
│   - SHA-chain integrity (sealed SPEC_AUDIT_MODULE)              │
│   - Source of truth para audit · reconstruction · replay        │
│   - Retention regulada per privacy tier                          │
└────────────┬─────────────────────────────────────────────────────┘
             │
             │ outbox pattern (mismo transaction)
             ↓
┌──────────────────────────────────────────────────────────────────┐
│ CAPA 2 · OUTBOX (Postgres)                                       │
│   - Tabla outbox transaccional                                   │
│   - Worker poll → publish a Redis Streams                        │
│   - Garantiza at-least-once                                      │
│   - Idempotency keys via event_id                                │
└────────────┬─────────────────────────────────────────────────────┘
             │
             │ Redis Streams XADD
             ↓
┌──────────────────────────────────────────────────────────────────┐
│ CAPA 3 · TRANSPORT / BUS OPERATIVO (Redis Streams)               │
│   - Append-only log con consumer groups                          │
│   - Workers consumen por tipo de evento                          │
│   - Retention 24h (gap recovery WS)                              │
│   - DLQ + retry policies                                         │
└────────────┬─────────────────────────────────────────────────────┘
             │
             │ fanout
             ↓
┌──────────────────────────────────────────────────────────────────┐
│ CAPA 4 · UI FANOUT (WebSocket)                                   │
│   - WS server suscrito a Redis Streams                           │
│   - Filtra por tenant_id + actor permissions                     │
│   - Push a clientes Mesa de Control conectados                   │
│   - last_event_id para reconnect                                 │
└──────────────────────────────────────────────────────────────────┘
```

R5: "Separar event log canonico en Postgres de bus operativo en Redis Streams. No usar solo WebSocket como bus."

## 3. Eventos canonicos · 28 tipos

### 3.1 Identidad y sesion

```
auth.login.success
auth.login.failed
auth.logout
auth.role.switched
session.invalidated
permission.denied
```

### 3.2 Feed (Mesa de Control)

```
feed.item.received      ← email/call/evento entrante
feed.item.dispatched    ← AM asigna a agente
feed.item.archived
```

### 3.3 Drafts (HITL P3)

```
draft.generated         ← agente devuelve LISTO
draft.ready_for_signature ← post compliance check OK
draft.approved          ← AM firma
draft.edited            ← AM edita con razon tipificada
draft.rejected          ← AM rechaza con razon tipificada
draft.sent              ← post approve · saliente al cliente
draft.signature_blocked ← compliance bloqueo
```

### 3.4 Agentes

```
agent.iterate.started   ← AM entra a agentconsole
agent.alarma            ← agente no supo resolver
agent.config.updated
agent.shadow_promote    ← shadow → active (curador)
```

### 3.5 User Learning (capa 1)

```
pattern.candidate.detected
pattern.applied_personal
pattern.ignored
pattern.rolled_back
```

### 3.6 Committee (capa 2)

```
committee.candidate.queued    ← cumple k-anon ≥5
committee.pattern.promoted_l3
committee.pattern.rejected
committee.freeze.executed
committee.conflict.resolved
```

### 3.7 Sistema

```
freshness.violation     ← source SLA breach
cost.threshold          ← LLM cost cap
audit.access.tier4      ← AUDITOR accede TIER 4
sha_chain.broken        ← critico · alarma
```

## 4. Schema canonico per evento

```yaml
event:
  event_id: UUID                    # unico global
  event_type: string                # uno de los 28
  schema_version: string            # ej. "1.0"
  
  # Correlation
  trace_id: UUID                    # cadena de request original
  request_id: UUID?                 # si nacio de un HTTP request
  parent_event_id: UUID?            # si fue triggered por otro evento
  
  # Actor
  tenant_id: string
  user_id: UUID?                    # null si es system-initiated
  actor_role_at_decision: enum?     # AM · CURATOR · AUDITOR · CEO · SYSTEM
  agent_id: string?                 # si fue triggered por sub-agente
  
  # Payload
  resource_type: string             # draft · feed_item · pattern · etc
  resource_id: UUID?
  data: object                      # type-specific schema
  
  # Privacy
  privacy_tier: enum                # PRIVATE_RAW · TENANT_DERIVED · GLOBAL_PROMOTABLE · RESTRICTED
  
  # Audit
  timestamp: ISO8601
  sha_chain_prev: string            # SHA del evento anterior (cadena tenant-scoped)
  sha_chain_curr: string            # SHA(event_payload + sha_chain_prev)
  signed_by: string?                # si requiere firma (eventos criticos)
```

## 5. Outbox pattern (R5 critical)

### 5.1 Por que outbox

Si el sistema escribe a Postgres + publica a Redis en operaciones SEPARADAS · falla parcial deja inconsistencia:
- DB committed · Redis NO recibio → evento perdido
- DB rollback · Redis publish ya pasó → evento fantasma

Outbox: escribir evento en Postgres `outbox` table en LA MISMA transaccion del cambio de negocio. Worker separado lee outbox y publica a Redis. Garantiza at-least-once.

### 5.2 Schema tabla outbox

```sql
CREATE TABLE outbox (
  outbox_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id UUID NOT NULL UNIQUE,        -- alineado con event_log
  tenant_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  payload JSONB NOT NULL,
  
  status TEXT NOT NULL DEFAULT 'pending', -- pending · published · failed · dlq
  attempts INT NOT NULL DEFAULT 0,
  last_error TEXT,
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  published_at TIMESTAMPTZ,
  expires_at TIMESTAMPTZ NOT NULL DEFAULT NOW() + INTERVAL '7 days',
  
  INDEX idx_outbox_pending (status, created_at) WHERE status = 'pending'
);
```

### 5.3 Worker poll loop

```python
async def outbox_worker():
    while True:
        async with db.transaction() as tx:
            rows = await tx.fetch("""
                SELECT * FROM outbox 
                WHERE status = 'pending' AND attempts < 5
                ORDER BY created_at LIMIT 100
                FOR UPDATE SKIP LOCKED
            """)
            
            for row in rows:
                try:
                    await redis.xadd(
                        f"events:{row['tenant_id']}",
                        row['payload'],
                        id="*",  # auto-id
                        maxlen=100_000,
                    )
                    await tx.execute(
                        "UPDATE outbox SET status='published', published_at=NOW() WHERE outbox_id=$1",
                        row['outbox_id'],
                    )
                except Exception as e:
                    await tx.execute("""
                        UPDATE outbox SET attempts=attempts+1, last_error=$1
                        WHERE outbox_id=$2
                    """, str(e), row['outbox_id'])
        
        await asyncio.sleep(0.1)  # 100ms poll · ajustable
```

### 5.4 Dead Letter Queue (DLQ)

Eventos con `attempts >= 5`:
- Marcados `status='dlq'`
- Visibles en panel admin (rol CEO + AUDITOR)
- Retry manual con cambio de strategy
- Audit log `event.dlq_added` (alarma critica si > 10/dia)

## 6. Redis Streams · transport canonico

### 6.1 Stream layout

```
events:mwt              ← stream per tenant
events:mwt:dlq          ← DLQ per tenant
events:audit            ← audit-only stream global (sin tenant filter)
```

Ventajas vs Kafka (R5 explicit · NO Kafka Sprint 1):
- Append-only log nativo · simple
- Consumer groups built-in
- Retention via `MAXLEN ~ N` (aproximado · eficiente)
- Operativamente simple en Hostinger KVM 8

### 6.2 Consumer groups

```
GROUP workers              ← worker-default y worker-agent (Celery)
GROUP ws-fanout            ← WebSocket server
GROUP audit-archiver       ← background · persiste a S3/MinIO post-24h
GROUP cost-monitor         ← suscribe cost.threshold · LLM budget enforcement
```

Cada grupo lee independientemente · idempotencia via event_id en consumer side.

### 6.3 Retention

```
events:{tenant}              MAXLEN ~ 100_000 entries (≈ 24h normal · 1 semana low traffic)
events:{tenant}:dlq          sin TTL (revisar manual)
events:audit                 MAXLEN ~ 1_000_000 (mas largo · audit needs)
```

Eventos > 24h: archivados a Postgres event_log permanente y MinIO para audit cold storage.

## 7. UI fanout · WebSocket server

### 7.1 Subscription per tenant + role

```python
async def ws_server(websocket, user, tenant):
    """WebSocket server suscribe a Redis Streams y filtra eventos."""
    last_id = request.params.get('since', '$')  # $ = solo nuevos
    
    while True:
        # Read from Redis Stream con block 1s
        events = await redis.xread(
            {f"events:{tenant.id}": last_id},
            block=1000,
            count=50,
        )
        
        for stream, items in events:
            for event_id, fields in items:
                # Filtrar por permission: AM solo ve sus eventos · CURATOR ve agregados · etc
                if not has_permission_for_event(user, event_type=fields['event_type'], tenant=tenant):
                    continue
                
                await websocket.send_json({
                    'event_id': event_id,
                    'type': fields['event_type'],
                    'data': fields['data'],
                    ...
                })
                last_id = event_id
```

### 7.2 Reconnect via last_event_id

Cliente cae · reconecta:
```
WSS /api/v1/ws?since=<last_event_id>
```

Server hace `XRANGE events:{tenant} <last_event_id> +` para enviar eventos perdidos.

Si `last_event_id` < 24h y aún en Redis Stream → recover OK.
Si `last_event_id` > 24h → server responde `{type: 'sync_required'}` · cliente re-fetch full state.

## 8. SHA-chain integrity (sealed SPEC_AUDIT_MODULE)

Cada evento tiene `sha_chain_curr = SHA256(event_payload + sha_chain_prev)`. Cadena per tenant · NUNCA cross-tenant.

Verificacion peridica:
- Background job nightly · recalcula chain · alarma critica si SHA mismatch
- Endpoint `/api/v1/audit/sha_chain/verify` para CEO/AUDITOR check on-demand
- Ruptura de chain = `sha_chain.broken` event + alerta P0

## 9. Idempotencia transversal

R5 critical. Cada evento tiene `event_id` UUID · consumers chequean dedup:

```python
# Consumer side
async def handle_event(event):
    seen_key = f"event_seen:{tenant_id}:{event['event_id']}"
    if await redis.set(seen_key, "1", ex=86400, nx=True):
        # First time · process
        await process_event(event)
    else:
        # Duplicate · skip
        logger.info(f"event {event['event_id']} already processed · skip")
```

## 10. Rate limiting + backpressure

| Limite | Default |
|---|---|
| Outbox publish rate | 10000 events/min per tenant |
| Redis Stream length | MAXLEN ~ 100k per tenant |
| WS broadcast rate | 100 msg/sec per WS connection |
| Worker consumer parallel | 10 per tenant |

Si tenant excede limite · backpressure (delay outbox publish · WS slowdown). NO drop events.

## 11. Cost monitoring (R5 bonus alusion)

Eventos `cost.threshold` cuando:
- Tenant supera 80% budget mensual
- Agente individual supera daily_cap
- Action especifica supera per_action_cap

Consumer `cost-monitor` evalua:
- 80% → warning visible al CEO
- 95% → throttle (rate limit a 50%)
- 100% → block hasta nuevo budget approval

## 12. Reglas inquebrantables

1. **Outbox pattern obligatorio** para todo evento que cruza Postgres ↔ Redis. Sin outbox = riesgo de perder/duplicar.
2. **Event_id UUID · idempotencia consumer-side obligatoria.**
3. **SHA-chain per tenant · NUNCA cross-tenant.**
4. **Retention Redis Streams 24h · archivar a Postgres + MinIO post-24h.**
5. **DLQ revisado por CEO + AUDITOR · alarma >10/dia.**
6. **WebSocket fanout filtra por permission · AM no ve eventos comite.**
7. **Reconnect via last_event_id · si gap >24h `sync_required`.**
8. **NO Kafka Sprint 1.** Redis Streams suficiente para 12 containers KVM 8.
9. **NO usar solo WebSocket como bus.** WebSocket es fanout · NO transport durable.

## 13. Pendientes [PENDIENTE — NO INVENTAR]

- Kafka migration plan (post-Sprint 1 · cuando volumen lo justifique · gate F2)
- Cross-tenant event sharing (audit FB-side · post-Sprint 1)
- Event schema versioning (migrations entre v1.0 → v1.1) → SPEC implementacion
- Replay tool UI para debugging → diferido v2
- Event correlation viewer (graph) → diferido v3

## NO IMPLICA (R4 bonus 5%/50%)

`SPEC_FB_EVENTING_AND_OUTBOX_v1` **NO implica Kafka en Sprint 1**. Redis Streams + outbox pattern es suficiente para 12 containers KVM 8. Migracion a Kafka queda como evolucion v2 cuando volumen multi-tenant lo justifique.

## Changelog
- 2026-05-02 v1.0 VIGENTE: Creacion inicial post R5 ChatGPT (renombrado de SPEC_FB_EVENT_BUS_v1). 4 capas separadas (Event Log Postgres · Outbox · Bus Redis Streams · UI Fanout WebSocket). 28 eventos canonicos categorizados (auth · feed · drafts · agentes · user learning · committee · sistema). Schema evento con correlation IDs + actor + privacy_tier + SHA-chain. Outbox pattern transaccional con worker poll loop + DLQ. Redis Streams con consumer groups + retention 24h. WebSocket fanout filtra por permission. Idempotencia transversal via event_id. Rate limiting + backpressure. Cost monitoring. 9 reglas inquebrantables incluyendo NO Kafka Sprint 1. NO implica migracion Kafka v1.

## Stamp
VIGENTE 2026-05-02 — Sistema nervioso canonico con 4 capas separadas (R5 critical). Sin esto · "perder eventos · duplicar · no reconstruir" · riesgo real (R5).
