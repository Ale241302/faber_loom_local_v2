---
id: SPEC_FB_FRONTEND_REALTIME_STATE_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma
type: spec
stamp: VIGENTE 2026-05-02
fecha: 2026-05-02
agente: Cowork (redaccion) + CEO (decisiones) + ChatGPT (auditoria R5)
aplica_a: [FaberLoom]
implementa: SPEC_FB_INTEGRATION_LAYER_v1 (consume contrato REST + WebSocket)
relacionado_con:
  - SPEC_FB_AUTH_TENANT_RBAC_v1 (sesion frontend)
  - SPEC_FB_INTEGRATION_LAYER_v1 (REST + WS protocols)
  - Mock v5/v6 (Mesa de Control · UI canonica)
origen: ChatGPT R5 detecto frontend state como gap propio (puede ser anexo de Integration Layer · pero merece SPEC propio)
---

# SPEC_FB_FRONTEND_REALTIME_STATE_v1
## Estado del frontend Mesa de Control · server-state + UI-state + realtime sync

## 1. Proposito

Define como Mesa de Control (Next.js App Router) maneja estado en cliente:
- Server-state cache (datos del backend)
- UI-state local (filtros · selecciones · modales)
- Realtime sync via WebSocket (invalidacion + parches)
- Optimistic updates con rollback
- Reconnect logica

Sin esto, Sprint 1 implementa "estados falsos · eventos duplicados o perdidos · UI inconsistente con backend" (R5).

## 2. Stack canonico (de R5)

```
Framework:         Next.js App Router + React Server Components
Server-state:      TanStack Query v5 (formerly React Query)
UI-state local:    Zustand (liviano · sin Redux Toolkit overhead)
Realtime:          WebSocket nativo · custom hook useFaberloomWS
Forms:             React Hook Form + Zod (validacion · ts types desde Pydantic)
Optimistic:        TanStack Query mutations + onMutate
```

R5: "servidor como source of truth, TanStack Query para server-state, store liviano para UI local y WebSocket para invalidaciones/parches."

## 3. Arquitectura de estado

```
┌───────────────────────────────────────────────────────────────┐
│ BACKEND (source of truth)                                     │
│   - Postgres (data canonica)                                  │
│   - Redis Streams (eventos reales)                            │
└───────────────────┬───────────────────────────────────────────┘
                    │ REST + WebSocket
                    ↓
┌───────────────────────────────────────────────────────────────┐
│ FRONTEND                                                       │
│                                                                │
│   ┌─────────────────────┐   ┌─────────────────────────┐      │
│   │ TanStack Query      │   │ Zustand UI store        │      │
│   │ (server-state)      │   │ (UI local)              │      │
│   │                     │   │                         │      │
│   │ - feed              │   │ - active hat (rol)      │      │
│   │ - drafts pending    │   │ - selected item         │      │
│   │ - agent state       │   │ - filters chips         │      │
│   │ - patterns          │   │ - modal open?           │      │
│   │ - user/me           │   │ - light/dark            │      │
│   │ - tenant config     │   │ - panel slide-in?       │      │
│   └─────────────────────┘   └─────────────────────────┘      │
│            ↑                                                   │
│            │ invalidate / patch                                │
│            │                                                   │
│   ┌────────┴────────────┐                                     │
│   │ useFaberloomWS hook │                                     │
│   │ (WebSocket sync)    │                                     │
│   └─────────────────────┘                                     │
└───────────────────────────────────────────────────────────────┘
```

## 4. TanStack Query · server-state

### 4.1 Query keys canonicos

```typescript
// Hierarchical keys · facilita invalidacion por prefijo
export const qk = {
  feed: ['feed'] as const,
  feedFiltered: (state: State, tag?: Tag) => ['feed', state, tag] as const,
  feedItem: (id: string) => ['feed', 'item', id] as const,
  
  drafts: ['drafts'] as const,
  draftsPending: ['drafts', 'pending'] as const,
  draft: (id: string) => ['drafts', id] as const,
  
  agents: ['agents'] as const,
  agent: (name: string) => ['agents', name] as const,
  agentRuns: (name: string) => ['agents', name, 'runs'] as const,
  
  patterns: ['patterns'] as const,
  patternsCandidate: ['patterns', 'candidate'] as const,
  patternsApplied: ['patterns', 'applied'] as const,
  
  committee: ['committee'] as const,
  committeeQueue: ['committee', 'queue'] as const,
  
  user: {
    me: ['user', 'me'] as const,
  },
  
  tenant: {
    config: ['tenant', 'config'] as const,
  },
};
```

### 4.2 Cache config canonica

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,         // 30s · datos frescos
      gcTime: 5 * 60_000,        // 5min · garbage collect
      refetchOnWindowFocus: true,
      refetchOnReconnect: true,
      retry: (failureCount, error) => {
        if (error?.status === 401 || error?.status === 403) return false;
        return failureCount < 3;
      },
    },
    mutations: {
      retry: false,  // mutaciones NO retry auto · idempotency-key handles
    },
  },
});
```

### 4.3 Optimistic updates

```typescript
const approveDraft = useMutation({
  mutationFn: ({ draftId, idempotencyKey }: ApproveDraftParams) =>
    api.drafts.approve({ draftId, idempotencyKey }),
  
  onMutate: async ({ draftId }) => {
    // Cancel outgoing queries que pueden sobre-escribir
    await queryClient.cancelQueries({ queryKey: qk.drafts });
    
    const previous = queryClient.getQueryData(qk.draftsPending);
    
    // Optimistic: remover el draft de pending
    queryClient.setQueryData(qk.draftsPending, (old: Draft[] = []) =>
      old.filter(d => d.id !== draftId)
    );
    
    return { previous };
  },
  
  onError: (err, vars, context) => {
    // Rollback
    if (context?.previous) {
      queryClient.setQueryData(qk.draftsPending, context.previous);
    }
    showToast({ kind: 'error', message: 'No se pudo aprobar · reintentando' });
  },
  
  onSettled: () => {
    // Re-fetch para sincronizar
    queryClient.invalidateQueries({ queryKey: qk.drafts });
    queryClient.invalidateQueries({ queryKey: qk.feed });
  },
});
```

## 5. Zustand · UI local store

```typescript
interface UIStore {
  // Active hat (rol activo en multi-rol persona)
  activeHat: 'AM' | 'CURATOR' | 'AUDITOR' | 'CEO' | null;
  setActiveHat: (hat: ActiveHat) => void;
  
  // Mesa de Control state
  feedFilter: { state: 'urgent'|'firma'|'calma', tag?: Tag };
  selectedItemId: string | null;
  
  // Panels
  agentConsoleOpen: boolean;
  agentConsoleAgent: string | null;
  
  // Modales
  editModalDraftId: string | null;
  rejectModalDraftId: string | null;
  
  // Theme
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  
  // Cmd+K
  cmdkOpen: boolean;
  setCmdkOpen: (open: boolean) => void;
}

// Persistencia: NO localStorage (Claude.ai artifacts no soportan · limitacion brand v2)
// → solo memoria · se pierde al refresh
// → para preferencias persistentes (theme · activeHat) usar cookie httpOnly desde backend
```

## 6. Realtime sync · useFaberloomWS hook

### 6.1 Hook canonico

```typescript
function useFaberloomWS() {
  const queryClient = useQueryClient();
  const lastEventId = useRef<string | null>(null);
  const reconnectAttempts = useRef(0);
  
  useEffect(() => {
    let ws: WebSocket | null = null;
    let pingInterval: NodeJS.Timer | null = null;
    
    const connect = () => {
      const url = `wss://${window.location.host}/api/v1/ws${
        lastEventId.current ? `?since=${lastEventId.current}` : ''
      }`;
      
      ws = new WebSocket(url, ['faberloom.v1']);
      
      ws.onopen = () => {
        reconnectAttempts.current = 0;
        // Heartbeat
        pingInterval = setInterval(() => ws?.send(JSON.stringify({ type: 'pong' })), 30_000);
      };
      
      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.event_id) lastEventId.current = msg.event_id;
        
        handleEvent(msg, queryClient);
      };
      
      ws.onclose = () => {
        if (pingInterval) clearInterval(pingInterval);
        // Exponential backoff reconnect (max 30s)
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30_000);
        reconnectAttempts.current += 1;
        setTimeout(connect, delay);
      };
    };
    
    connect();
    
    return () => {
      ws?.close();
      if (pingInterval) clearInterval(pingInterval);
    };
  }, [queryClient]);
}
```

### 6.2 Event handlers · invalidacion + parches

```typescript
function handleEvent(msg: WSEvent, qc: QueryClient) {
  switch (msg.type) {
    case 'feed.item.new':
      // Patch: insertar al feed sin re-fetch completo
      qc.setQueryData(qk.feed, (old: FeedPage[] = []) => [...old, msg.data.item]);
      break;
    
    case 'draft.ready_for_signature':
      // Invalidate · re-fetch
      qc.invalidateQueries({ queryKey: qk.draftsPending });
      qc.invalidateQueries({ queryKey: qk.feed });
      // Toast notification
      showToast({ kind: 'success', message: `Draft listo · ${msg.data.preview.account_name}` });
      break;
    
    case 'agent.alarma':
      qc.invalidateQueries({ queryKey: qk.agent(msg.data.agent_name) });
      qc.invalidateQueries({ queryKey: qk.feed });
      // Visual urgent: badge alarma se prende
      useUIStore.getState().setAlarmaCount((c) => c + 1);
      break;
    
    case 'pattern.candidate.detected':
      qc.invalidateQueries({ queryKey: qk.patternsCandidate });
      // Discreto · footer-zone notification
      useUIStore.getState().incrementLearningBadge();
      break;
    
    case 'session.invalidated':
      // Force logout
      qc.clear();
      window.location.href = '/login?reason=' + msg.data.reason;
      break;
    
    case 'sync_required':
      // Gap > 24h · re-fetch full state
      qc.invalidateQueries();
      break;
    
    case 'ping':
      // Server heartbeat · ya respondemos via pingInterval
      break;
  }
}
```

## 7. Conflict handling

### 7.1 Optimistic update + WS event llega antes que response

Escenario:
- AM aprueba draft X (optimistic: remover de pending)
- Antes de que llegue 200 OK · server emite WS `draft.signed` para draft Y
- WS handler invalida pending · se trae lista actualizada (sin X · porque ya se aprobo)

Resolucion:
- TanStack Query maneja esto auto: la invalidacion via WS sobre-escribe el cache · si la mutacion termina con 200 · onSettled re-invalida · queda consistente

### 7.2 Mutacion falla mientras WS dice estado distinto

Escenario:
- AM aprueba draft X · network error
- WS llega despues con `draft.X.signed` (otro user en multi-AM aprobó · raro · puede pasar)
- Optimistic rollback queria poner X de vuelta · pero WS dice signed

Resolucion:
- onError SIEMPRE invalida la query · trust server-state · NO trust optimistic
- Toast user-friendly: "Este draft ya fue procesado · refrescando vista"

## 8. Reconnection behavior · clave UX

### 8.1 Estados de conexion

| Estado | UI signal |
|---|---|
| `connecting` (initial o reconnect) | Spinner discreto en header · "Conectando..." |
| `connected` | Sin signal (estado normal) |
| `disconnected` (intencional logout) | Redirect a /login |
| `disconnected_unexpected` (network) | Banner amarillo "Sin conexion · reintentando..." |
| `sync_required` (gap > 24h) | Modal "Sincronizando con servidor..." · luego refresh |

### 8.2 Reconnect strategy

```
Intent 1: 1s
Intent 2: 2s
Intent 3: 4s
Intent 4: 8s
Intent 5: 16s
Intent 6+: 30s (max)

Si > 5min sin connect → mostrar modal "Sin conexion · vuelve a iniciar sesion"
```

## 9. Performance targets

| Metric | Target |
|---|---|
| Time to Interactive (Lighthouse) | <2.5s |
| Largest Contentful Paint | <1.5s |
| Cumulative Layout Shift | <0.1 |
| WS message handler latency | <16ms (1 frame 60fps) |
| Optimistic update visual response | <100ms |
| TanStack Query cache hit ratio | >70% |
| Re-fetch on filter change | <300ms p95 |

## 10. Reglas inquebrantables

1. **Server es source of truth.** Optimistic updates SIEMPRE reconciliados con re-fetch.
2. **NO localStorage / sessionStorage** (Claude.ai artifacts compatibility · paranoia transversal). Persistencia via cookies httpOnly desde backend.
3. **TanStack Query keys hierarchical** para invalidacion por prefijo.
4. **WebSocket reconnect con last_event_id** · NO perder eventos.
5. **Idempotency key generado en frontend** ANTES de enviar mutacion (UUID).
6. **NO retry mutations auto** · idempotency-key handles · backend decide.
7. **Heartbeat 30s/10s · timeout reconnect.**
8. **Pydantic schemas → TS types auto-gen** · NO duplicar manual.

## 11. Pendientes [PENDIENTE — NO INVENTAR]

- Service Worker offline mode (post-Sprint 1) → diferido v2
- Background sync con persistencia → diferido v2
- Multi-tab coordination (BroadcastChannel) → diferido v2 si users abren multiples tabs
- Conflict resolution UI cuando 2 AMs editan mismo draft (raro · post-Sprint 1) → diferido
- Analytics tracking (sin telemetry intrusiva · solo vital signs) → diferido v2

## NO IMPLICA (R4 bonus 5%/50%)

`SPEC_FB_FRONTEND_REALTIME_STATE_v1` **NO implica state management cross-app**. Es solo Mesa de Control. Si emerge otra app frontend (curator-workspace · auditor-dashboard) compartir patron pero NO compartir store. Cada pantalla con sus queries/mutations/store.

## Changelog
- 2026-05-02 v1.0 VIGENTE: Creacion inicial post R5 ChatGPT. Stack canonico Next.js App Router + TanStack Query v5 + Zustand + WebSocket nativo. Hierarchical query keys facilitan invalidacion por prefijo. Cache config: staleTime 30s · gcTime 5min. Optimistic updates con onMutate + onError rollback + onSettled re-fetch. UI store Zustand (active hat · filters · modals · theme · cmdkOpen). Hook useFaberloomWS con reconnect exponential backoff (max 30s) + heartbeat 30s. Handlers per event type (feed.item.new patch · draft.ready_for_signature invalidate + toast · agent.alarma badge · pattern.candidate footer · session.invalidated logout · sync_required full refresh). Conflict handling server-as-truth. Reconnection states UX (connecting/connected/disconnected/sync_required). Performance targets. 8 reglas inquebrantables incluyendo NO localStorage. NO implica state management cross-app.

## Stamp
VIGENTE 2026-05-02 — Frontend state limpio · server source of truth + WS sync + reconnect robusto. Sin esto · Sprint 1 implementa "estados falsos · eventos duplicados o perdidos · UI inconsistente" (R5).
