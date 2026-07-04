# M19 Offline Sync — Plan de Implementación

## 1. Resumen ejecutivo

M19 define el protocolo de arranque y reconexión del desktop Electron. Persiste cursores de eventos (`last_event_id`, `last_sync_at`) de forma no secreta, reconcilia el estado con el server vía delta (WS `?since=last_event_id`) cuando el gap es ≤24h, o hace **full refresh** si el cursor se perdió o supera la ventana. Durante la reconciliación se bloquean las acciones sensibles (aprobar, editar, enviar).

**Rol en el SPINE:** depende de M15 (eventos/streams), M18 (sesión desktop segura) y M13 (no aprobar offline). Es transversal a toda la UI desktop.

## 2. Entrada/salida

### Entrada
- `last_event_id` y `last_sync_at` desde `electron-store`.
- Eventos del WebSocket tenant (M15).
- Endpoints de full state (`/api/workloom/state`, `/api/drafts`, `/api/tasks`, etc.).
- Estado de conectividad de red.

### Salida
- Estado local del desktop reconciliado con el server.
- Cursores actualizados en `electron-store`.
- Badge de "Sincronizando" / "Offline" en la UI.
- Acciones sensibles habilitadas/deshabilitadas.

## 3. Modelo de datos

No se agregan tablas de backend; M19 reutiliza:
- `EventLog` / `Outbox` (M15) como fuente de delta.
- `electron-store` para cursores locales no secretos:
  ```json
  {
    "last_event_id": "evt_...",
    "last_sync_at": "2026-07-02T12:00:00Z",
    "tenant_id": "...",
    "client_version": "1.3.1"
  }
  ```

Se agrega un endpoint de backend para full state:
- `GET /api/sync/full-state` — snapshot completo del estado operativo del tenant para el usuario actual.

## 4. Cambios en API/backend

### Sync service (cliente)

```typescript
// desktop/src/main/sync.ts
class SyncManager {
  async coldStart(profile: string) {
    const cursors = store.get(`cursors.${profile}`);
    this.setState('syncing');

    if (!cursors || this.hoursSince(cursors.last_sync_at) > 24) {
      await this.fullRefresh(profile);
    } else {
      await this.deltaSync(profile, cursors.last_event_id);
    }
    this.setState('online');
  }

  async deltaSync(profile: string, since: string) {
    const ws = new WebSocket(`${WS_URL}/ws/events/?since=${since}`);
    ws.onmessage = (msg) => {
      const event = JSON.parse(msg.data);
      if (event.type === 'sync_required') {
        return this.fullRefresh(profile);
      }
      this.applyEvent(event);
      this.updateCursor(profile, event.event_id);
    };
  }

  async fullRefresh(profile: string) {
    // El main process usa HTTP (no ipcRenderer). La cookie de sesión se lee de la
    // partición de Electron (M18).
    const response = await fetch(`${API_URL}/api/sync/full-state`, {
      credentials: 'include',
    });
    const state = await response.json();
    this.replaceLocalState(profile, state);
    this.updateCursor(profile, state.last_event_id);
  }
}
```

### Endpoint full state

```python
# apps/sync/views.py
@require_permission('workloom:read')
def full_state(request):
    tenant_id = request.tenant_id
    user_id = request.user_id
    # Los helpers list_* son responsabilidad de sus respectivas apps (drafts,
    # tasks, classifier). Este endpoint solo los agrega en un snapshot.
    return Response({
        'last_event_id': get_last_event_id(tenant_id),
        'drafts': list_drafts(tenant_id, user_id),
        'tasks': list_tasks(tenant_id, user_id),
        'feed_items': list_pending_feed_items(tenant_id, user_id),
    })
```

### Estado de UI

```typescript
// desktop/src/renderer/store/sync.ts
interface SyncState {
  status: 'syncing' | 'online' | 'offline';
  last_sync_at: string | null;
  block_sensitive_actions: boolean;
}
```

## 5. Cambios en frontend

### Desktop
- Badge "Sincronizando..." mientras `status === 'syncing'`.
- Badge "Offline" cuando se pierde la red.
- Botones de aprobar/editar/enviar deshabilitados con tooltip hasta estar `online`.
- Toast al completar reconciliación si llegaron cambios relevantes.

### Web
- Sin cambios; la web se reconecta por WS sin persistencia fuerte de cursores.

## 6. Cambios en infraestructura/deploy

- Variables de entorno:
  ```bash
  API_URL=https://api.faberloom.io
  WS_URL=wss://api.faberloom.io
  SYNC_DELTA_HOURS=24
  SYNC_RETRY_INTERVAL_MS=5000
  SYNC_MAX_RETRIES=10
  ```
- `electron-store` clave `cursors.{profile}`.
- WebSocket endpoint `/ws/events/?since=<last_event_id>` ya provisto por M15.

## 7. Secuencia de tareas

1. Definir schema de cursores en `electron-store`.
2. Implementar `SyncManager.coldStart()`.
3. Implementar `deltaSync()` con reconexión y manejo de `sync_required`.
4. Implementar `fullRefresh()` y endpoint `/api/sync/full-state`.
5. Bloquear acciones sensibles durante `syncing`/`offline`.
6. Manejar reconexión de red (online/offline events).
7. Tests de delta, full refresh y bloqueo de acciones.
8. Métricas de sync (duración, tasa de full refresh).

## 8. Criterios de aceptación

1. `test_cold_start_delta_within_24h`: arranque con cursor reciente abre WS con `?since=`.
2. `test_cold_start_full_refresh_after_24h`: gap >24h descarta estado local y hace full refresh.
3. `test_sync_required_triggers_full_refresh`: evento `sync_required` fuerza full refresh.
4. `test_sensitive_actions_blocked_while_syncing`: aprobar/editar/enviar deshabilitados hasta `online`.
5. `test_no_offline_approvals_s1a`: no se ejecutan aprobaciones en estado `offline`.
6. `test_cursor_updated_after_each_event`: `last_event_id` se actualiza secuencialmente.
7. `test_cross_tenant_cursor_isolation`: cursor de tenant A no se usa para tenant B.

## 9. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Estado obsoleto al aprobar | P1 decisiones erróneas | Bloquear acciones hasta reconciliación |
| Cursor corrupto | P2 full refresh innecesario | Validar cursor; fallback a full refresh |
| Intermitencia durante sync | P2 UX | Reintentos con backoff; no marcar online hasta completar |
| Full refresh muy grande | P2 latencia | Paginación progresiva; precarga crítica primero |
| Cross-tenant state mix | P0 leak | Cursores y estado local separados por profile |

## 10. Decisiones de arquitectura tomadas

1. **Ventana delta = 24h**, igual al TTL del stream de M15.
2. **Server es la fuente de la verdad.** El full refresh descarta estado local.
3. **No aprobaciones offline en S1A.** Solo lectura y redacción local no enviada.
4. **Cursores no secretos en `electron-store`.** Secretos siguen en keychain (M18).
5. **Acciones sensibles bloqueadas mientras `syncing`.** El usuario siempre actúa sobre estado reconciliado.

---
*Plan M19 — Foundation Beta v1.3.1*
