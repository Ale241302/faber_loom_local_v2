# M20 Auto Update — Plan de Implementación

## 1. Resumen ejecutivo

M20 distribuye actualizaciones del desktop Electron de forma automática, segura y no disruptiva. Usa `electron-builder` + `electron-updater`, artefactos firmados por plataforma, un feed HTTPS propio por canal (`stable`/`beta`) y una `min_supported_client_version` declarada por el backend. El cliente descarga en background e instala al cerrar la app o cuando el usuario pulsa "Reiniciar e instalar"; nunca reinicia automáticamente en medio de una tarea.

**Rol en el SPINE:** depende del pipeline de build/sign y del backend de releases. Coordina con M18 (preservar sesión) y M19 (WS reconciliado antes de instalar).

## 2. Entrada/salida

### Entrada
- Feed HTTPS con releases por plataforma y canal.
- `min_supported_client_version` declarada por el backend.
- Versión actual instalada, plataforma, canal asignado al tenant.
- Estado de mutaciones pendientes, sync y drafts guardados.

### Salida
- Artefacto descargado, firma verificada.
- Instalación al cierre/botón.
- Pantalla de bloqueo si la versión actual está por debajo de `min_supported`.
- Telemetría de versión instalada por cliente.

## 3. Modelo de datos

### Tablas de backend

```sql
CREATE TABLE client_releases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version TEXT NOT NULL,
    platform TEXT NOT NULL,  -- win, mac, linux
    channel TEXT NOT NULL CHECK (channel IN ('stable','beta')),
    feed_url TEXT NOT NULL,
    published_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    retired_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(version, platform, channel)
);

CREATE TABLE system_configs (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- Valor semilla; se actualiza cuando el backend fuerza upgrades.
INSERT INTO system_configs (key, value) VALUES ('min_supported_client_version', '1.3.0');

CREATE TABLE tenant_update_channels (
    tenant_id UUID PRIMARY KEY REFERENCES tenants(id) ON DELETE CASCADE,
    channel TEXT NOT NULL DEFAULT 'stable' CHECK (channel IN ('stable','beta')),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE client_version_telemetry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    client_version TEXT NOT NULL,
    platform TEXT NOT NULL,
    reported_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Aislamiento (RLS)
`ClientRelease`, `TenantUpdateChannel` y `ClientVersionTelemetry` son tenant-scoped (excepto `ClientRelease`, que es global a la plataforma pero filtrada por `platform`/`channel`). `TenantUpdateChannel` y `ClientVersionTelemetry` aplican `FORCE ROW LEVEL SECURITY` por `tenant_id`.

### Nota sobre eventos
M15 transporta eventos de dominio de forma genérica. Los eventos `client.update.available`, `client.update.downloaded`, `client.update.blocked` e `client.update.installed` usan el envelope canónico de M15.

## 4. Cambios en API/backend

### Release service

```python
# apps/updates/views.py
@require_permission('config:view')
def latest_release(request):
    platform = request.GET['platform']
    channel = get_tenant_channel(request.tenant_id)
    release = ClientRelease.objects.filter(
        platform=platform, channel=channel, retired_at__isnull=True
    ).order_by('-published_at').first()
    min_version = SystemConfig.objects.get(key='min_supported_client_version').value
    return Response({
        'version': release.version,
        'feed_url': release.feed_url,
        'mandatory': semver.lt(release.version, min_version),
    })

@require_permission('config:view')
def min_supported_version(request):
    config = SystemConfig.objects.get(key='min_supported_client_version')
    return Response({
        'min_supported_client_version': config.value,
    })
```

### Client updater

```typescript
// desktop/src/main/updater.ts
import { autoUpdater } from 'electron-updater';

class UpdateManager {
  async check() {
    const { min_supported_client_version } = await api.get('/api/updates/min-supported');
    if (semver.lt(app.getVersion(), min_supported_client_version)) {
      this.blockApp(min_supported_client_version);
      return;
    }
    autoUpdater.checkForUpdates();
  }

  onUpdateDownloaded() {
    // Aviso discreto; instalar solo al cerrar o botón manual
    mainWindow.webContents.send('update:ready');
  }

  async install() {
    if (await this.canInstallSafely()) {
      autoUpdater.quitAndInstall();
    }
  }

  async canInstallSafely() {
    // El UpdateManager vive en el main process; consulta directamente a los
    // managers locales (SyncManager, DraftManager, SessionManager).
    return (
      syncManager.isReconciled() &&
      draftManager.noPendingMutations() &&
      sessionManager.noPendingProfileSwitch()
    );
  }
}
```

### Eventos

- `client.update.available`
- `client.update.downloaded`
- `client.update.blocked` (por debajo de min_supported)
- `client.update.installed` (telemetría)

## 5. Cambios en frontend

### Desktop
- Indicador discreto "Actualización disponible".
- Botón "Reiniciar e instalar" cuando el update está listo.
- Pantalla de bloqueo si la versión es inferior a `min_supported`.
- Diálogo de confirmación si hay mutaciones pendientes al intentar instalar.

### Web
- Sin cambios; la web se actualiza por despliegue server-side.

## 6. Cambios en infraestructura/deploy

- Pipeline CI:
  ```bash
  npm run build:electron
  npm run dist:win
  npm run dist:mac
  npm run dist:linux
  ```
- Code signing:
  - Windows: EV cert.
  - macOS: Developer ID + notarización.
  - Linux: AppImage firmado (opcional E1).
- Feed HTTPS alojado en S3/MinIO o CDN con paths:
  ```
  /updates/stable/win/latest.yml
  /updates/beta/mac/latest-mac.yml
  ```
- Variables de entorno:
  ```bash
  UPDATE_FEED_BASE_URL=https://updates.faberloom.io
  UPDATE_CHECK_INTERVAL_MS=3600000
  CODE_SIGN_CERT_PATH=
  NOTARIZE_APPLE_ID=
  ```

## 7. Secuencia de tareas

1. Configurar `electron-builder` con code signing.
2. Crear modelos `ClientRelease`, `TenantUpdateChannel`, `ClientVersionTelemetry`.
3. Implementar endpoints `/api/updates/latest` y `/api/updates/min-supported`.
4. Generar feeds HTTPS por plataforma/canal.
5. Implementar `UpdateManager` con `electron-updater`.
6. Verificar firma del artefacto antes de instalar.
7. Implementar pre-checks de instalación segura (sync, drafts, mutaciones).
8. Implementar pantalla de bloqueo por `min_supported`.
9. Reportar telemetría de versión.
10. Tests de update flow y rollback de release.

## 8. Criterios de aceptación

1. `test_signed_artifact_required`: update con firma inválida se descarta.
2. `test_no_auto_restart_mid_task`: la app nunca reinicia sola con mutaciones pendientes.
3. `test_min_supported_blocks_old_client`: versión inferior a min_supported muestra pantalla de bloqueo.
4. `test_beta_channel_limited_to_five_tenants`: solo tenants asignados reciben canal beta.
5. `test_update_preserves_session_and_cursors`: tras instalar, M18/M19 reanudan sin pérdida.
6. `test_can_install_only_when_safe`: pre-checks bloquean instalar si hay sync/drafts pendientes.
7. `test_rollback_release_republish_previous`: publicar versión anterior restaura el feed.

## 9. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Artefacto malicioso | P0 compromiso | Code signing + verificación de firma |
| Restart sorpresa | P1 pérdida de trabajo | Pre-checks + solo cerrar/botón manual |
| Clientes obsoletos | P2 incompatibilidad | `min_supported_client_version` forzada |
| Beta inestable en producción | P1 incidente | Canal beta limitado a 5 tenants |
| Rollback lento | P2 degradación | Feed controlado; republicar versión anterior |

## 10. Decisiones de arquitectura tomadas

1. **`electron-builder` + `electron-updater` como base.** Estándar del ecosistema Electron.
2. **Feed HTTPS propio, no GitHub releases.** Mayor control de canales y firmas.
3. **`min_supported_client_version` en backend.** Permite forzar upgrades sin depender solo del feed.
4. **Instalación no disruptiva.** Nunca auto-restart; siempre requiere cierre o decisión explícita del usuario.
5. **Preservar sesión y cursores.** El update no debe borrar datos locales salvo migración explícita.

---
*Plan M20 — Foundation Beta v1.3.1*
