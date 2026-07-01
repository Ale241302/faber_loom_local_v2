# M15 Outbox Streams — Plan de Implementación

## 1. Resumen ejecutivo

M15 entrega eventos de dominio de forma confiable desde el backend a las UIs, con reconexión robusta y aislamiento por tenant.  Usa el patrón outbox transaccional: el evento se escribe en la misma transacción que el cambio de dato.

**Rol en el SPINE:** consume `tenant_context` de M16 y sesión de M08; alimenta a WorkLoom, M19 (offline sync), M12 (audit) y cualquier consumidor de eventos.

## 2. Entrada/salida

### Entrada
- Transacciones de negocio que emiten eventos (M07, M08, M09, M10, M11, M12, M13).
- Event envelope canónico.

### Salida
- Fila en tabla `outbox` (misma transacción que el dato).
- Entrada en Redis Stream `tenant:{tenant_id}:events`.
- WebSocket fanout por tenant y permisos.
- Reconexión con `?since=last_event_id`.

## 3. Modelo de datos

### Tablas

```sql
CREATE TABLE event_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id TEXT NOT NULL UNIQUE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    payload_json JSONB NOT NULL DEFAULT '{}',
    seq_no BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE outbox (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    event_id TEXT NOT NULL UNIQUE,
    event_type TEXT NOT NULL,
    payload_json JSONB NOT NULL DEFAULT '{}',
    seq_no BIGINT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','published','failed')),
    retry_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE SEQUENCE global_event_seq;

CREATE INDEX idx_outbox_status ON outbox(status, created_at);
CREATE INDEX idx_outbox_tenant ON outbox(tenant_id, status);
CREATE INDEX idx_event_log_tenant_seq ON event_log(tenant_id, seq_no);
```

### Event envelope

```json
{
  "event_id": "evt_<uuid>",
  "tenant_id": "<uuid>",
  "type": "draft.generated",
  "payload": { "draft_id": "...", "task_id": "..." },
  "seq_no": 12345,
  "timestamp": "2026-07-01T12:00:00Z"
}
```

### Redis Streams

- Stream key: `tenant:{tenant_id}:events`
- Entry ID secuencial basado en `seq_no`.
- TTL: 24h.

## 4. Cambios en API/backend

### Event writer

```python
# apps/events/outbox.py
from django.db import transaction
from django.db import connection

class EventWriter:
    def emit(self, tenant_id, event_type, payload):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT nextval('global_event_seq')")
                seq_no = cursor.fetchone()[0]
            event_id = f"evt_{uuid.uuid4().hex}"
            Outbox.objects.create(
                tenant_id=tenant_id,
                event_id=event_id,
                event_type=event_type,
                payload_json=payload,
                seq_no=seq_no,
            )
            EventLog.objects.create(
                tenant_id=tenant_id,
                event_id=event_id,
                event_type=event_type,
                payload_json=payload,
                seq_no=seq_no,
            )
            return event_id
```

### Relay Celery

```python
# apps/events/tasks.py
from config.celery import TenantTask

@app.task(base=TenantTask, bind=True)
def relay_outbox(self, tenant_id):
    pending = Outbox.objects.filter(tenant_id=tenant_id, status='pending').order_by('seq_no')
    for row in pending:
        key = f"tenant:{tenant_id}:events"
        redis_client.xadd(key, {
            b"event_id": row.event_id.encode(),
            b"type": row.event_type.encode(),
            b"payload": json.dumps(row.payload_json).encode(),
            b"seq_no": str(row.seq_no).encode(),
        })
        row.status = 'published'
        row.save(update_fields=['status', 'updated_at'])
```

- Scheduler Celery beat: cada 1s por tenant activo o listener Postgres `NOTIFY`.

### WebSocket fanout

- Consumer Django Channels conectado a Redis Streams.
- Filtra eventos por permisos del usuario (M09) antes de enviar.
- URL: `/ws/events/?since=<last_event_id>`.
- Si gap >24h o cursor inválido → envía `sync_required: true`.

### Endpoints REST (fallback)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/events?since=<seq>` | Polling fallback para entornos sin WS |

## 5. Cambios en frontend

### Web / Desktop
- Conectar WS al abrir la app.
- Guardar `last_event_id`/`seq_no` en localStorage (web) o safeStorage (desktop).
- Mostrar badge "Sincronizando" al reconectar.
- Si recibe `sync_required` → hacer re-fetch full del estado.

## 6. Cambios en infraestructura/deploy

- Añadir `channels`, `channels-redis`, `daphne`.
- Configurar ASGI con Channels.
- Celery beat para relay periódico.
- Variables de entorno:
  ```bash
  REDIS_URL=redis://redis:6379/0
  EVENT_STREAM_TTL_SECONDS=86400
  OUTBOX_RETENTION_DAYS=7
  ```
- Job nocturno purga outbox publicados con más de 7 días.

## 7. Secuencia de tareas

1. Crear app Django `events`.
2. Modelos `EventLog`, `Outbox` + sequence.
3. Implementar `EventWriter.emit()`.
4. Implementar Celery relay task.
5. Configurar Channels + consumer WS.
6. Implementar fanout por tenant + permisos.
7. Implementar protocolo `?since=last_event_id`.
8. Implementar polling fallback.
9. Purga de outbox publicados.
10. Tests de idempotencia y cross-tenant.
11. Integrar con frontend.

## 8. Criterios de aceptación

1. `test_outbox_publishes_after_business_transaction_commit`: DB commit + Redis publish atómico.
2. `test_duplicate_event_id_processed_once`: re-procesar outbox no duplica eventos.
3. `test_ws_fanout_filters_by_tenant_and_permission`: tenant A no recibe eventos de B.
4. Reconexión con `since` recupera eventos de <=24h.
5. Gap >24h dispara `sync_required` y re-fetch.
6. Relay resiste crash y recontinúa desde outbox.
7. Latencia p95 evento WS <500ms.

## 9. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| DB commit sin outbox | P1 inconsistencia | `EventWriter.emit()` dentro de `transaction.atomic()` |
| Relay duplica eventos | P1 UI confusa | Dedupe por `event_id` en consumer |
| Fanout cross-tenant | P0 leak | Filtrar por `tenant_id` + permisos M09 |
| WS no disponible | P2 UX degradada | Polling fallback |
| Outbox crece sin límite | P1 almacenamiento | Purga 7 días publicados |

## 10. Decisiones de arquitectura tomadas

1. **Outbox + Redis Streams, no solo WS.**  Garantiza durabilidad ante crash.
2. **Sequence global monotónica.**  Simplifica `since` y orden total.
3. **Stream TTL 24h, outbox 7 días.**  Balance recuperación/almacenamiento.
4. **Fanout filtra por permisos.**  Aunque el stream es por tenant, el usuario solo ve lo que su rol permite.
5. **Eventos E1: subset de 6.**  `feed.item.received`, `feed.item.dispatched`, `task.created`, `draft.generated`, `draft.approved`, `draft.sent`.

---
*Plan M15 — Foundation Beta v1.3.1*
