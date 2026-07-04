# FaberLoom Desktop — M18 Electron Auth + M19 Offline Sync + M20 Auto Update

Cliente desktop de Foundation Beta basado en Electron.

## Seguridad (M18)

- Las cookies de sesión (`session_id`) viven únicamente en el **main process** y se aislan por partición (`persist:faberloom-{tenant_id}::{email}`).
- El renderer no tiene acceso a Node.js (`nodeIntegration: false`, `contextIsolation: true`).
- Los secretos futuros (device tokens) irán al keychain vía `keytar`; la configuración no secreta se guarda en `electron-store`.
- El renderer nunca usa `localStorage` ni `sessionStorage` para tokens.

## Offline Sync (M19)

- `SyncManager` en el main process gestiona cursores `last_event_id`/`last_sync_at` por profile.
- **Cold start**:
  - Si no hay cursor o el gap es >24h → `fullRefresh` vía `GET /api/sync/full-state`.
  - Si el cursor es reciente → `deltaSync` vía WebSocket `/ws/events/?since=<last_event_id>`.
- Evento `sync_required` desde el servidor fuerza un full refresh.
- Las acciones sensibles (aprobar/editar/enviar) se bloquean mientras `status !== 'online'`.

## Auto Update (M20)

- `UpdateManager` consulta `/api/updates/min-supported` y `/api/updates/latest`.
- Si la versión actual es inferior a `min_supported_client_version`, se muestra pantalla de bloqueo.
- Descarga vía `electron-updater`; instalación solo al cerrar o botón manual.
- Pre-checks: no instala si hay sync pendiente o acciones sensibles bloqueadas.
- `electron-builder` configurado para generar artefactos firmados (variables de entorno para certificados).

## Estructura

```
desktop/
├── src/main/main.js        # proceso main + IPC handlers
├── src/main/session.js     # ElectronSessionManager (particiones/keychain)
├── src/main/api.js         # cliente HTTP hacia M08
├── src/main/sync.js        # SyncManager (delta/full/offline)
├── src/main/updater.js     # UpdateManager (auto-update)
├── src/main/preload.js     # puente IPC seguro al renderer
├── src/renderer/           # UI HTML/JS
└── tests/                  # tests de seguridad, sync y update
```

## Scripts

```bash
npm install
npm start        # levanta Electron
npm test         # tests Jest
npm run dist     # empaqueta con electron-builder
```

## Variables de entorno

- `API_URL` — URL del backend Foundation Beta (default `http://localhost:8000`).
- `WS_URL` — URL del WebSocket (default `ws://localhost:8000`).
- `UPDATE_FEED_BASE_URL` — feed de artefactos firmados.
- `UPDATE_CHECK_INTERVAL_MS` — intervalo de chequeo (default 1h).
- `KEYTAR_SERVICE` — namespace de keychain (default `faberloom`).
- `SYNC_DELTA_HOURS` — ventana delta en horas (default `24`).

## Integración con backend

- M08: `POST /api/auth/login`, `POST /api/auth/2fa`, `GET /api/auth/me`, `POST /api/auth/logout`.
- M15: `WS /ws/events/?since=<last_event_id>`.
- M19: `GET /api/sync/full-state`.
- M20: `GET /api/updates/latest`, `GET /api/updates/min-supported`.
