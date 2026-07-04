# M18 Electron Auth — Plan de Implementación

## 1. Resumen ejecutivo

M18 hardeniza la sesión de Electron: particiones por tenant/profile, cookies `httpOnly` en el **main process**, secretos en el keychain del SO (keytar/safeStorage) y configuración no secreta en `electron-store`. Garantiza que los tokens nunca toquen `localStorage` del renderer y que el logout limpie tanto la partición como el keychain.

**Rol en el SPINE:** es el detalle desktop de M08 Auth Session. Depende de M08 (credenciales + 2FA + sesión server-side en Redis) y M16 (aislamiento por tenant). Alimenta a M19 (offline sync) y M20 (auto-update).

## 2. Entrada/salida

### Entrada
- Credenciales del usuario (flujo M08).
- Código TOTP si aplica (Owner).
- Tenant/profile seleccionado.
- Respuesta de `/auth/me` y cookie de sesión server-side.

### Salida
- `session.fromPartition('persist:faberloom-{profile}')` por tenant.
- Cookie `httpOnly`/`Secure`/`SameSite=Strict` en el main process.
- Refresh token / secretos almacenados en keychain vía `keytar` o `safeStorage`.
- Config no secreta (preferencias, último profile) en `electron-store`.
- Eventos M08 (`auth.login.success`, `session.revoked`).
- Audit entry reutilizando M12 (acción registrada en M08).

## 3. Modelo de datos

No se agregan tablas de backend propias; M18 reutiliza:
- `User`, `Membership` (M08/M09).
- `Session` server-side en Redis (M08).
- `Tenant` (M16).

En el cliente Electron se usan tres almacenes separados:

| Almacén | Uso | Ejemplos | Restricción |
|---|---|---|---|
| `session` partition | Cookies httpOnly de sesión | `session_id` | Solo main process |
| `keytar` / `safeStorage` | Secretos cifrados por el SO | reservado para futuros device tokens (E1 no aplica) | Nunca renderer |
| `electron-store` | Config no secreta | last_profile, theme, window bounds | No tokens |

## 4. Cambios en API/backend

### Electron main process

```typescript
// desktop/src/main/session.ts
import { session } from 'electron';
import keytar from 'keytar';

export class ElectronSessionManager {
  private service = 'faberloom';

  getPartition(profile: string) {
    return `persist:faberloom-${profile}`;
  }

  async createSession(profile: string, tenantId: string, cookieValue: string) {
    const sess = session.fromPartition(this.getPartition(profile));
    await sess.cookies.set({
      url: this.apiUrl,
      name: 'faberloom_session',
      value: cookieValue,
      httpOnly: true,
      secure: true,
      sameSite: 'strict',
    });
    // E1: no hay refresh token (M08 usa session_id en Redis). keytar queda
    // preparado para futuros secretos (ej. device token) pero no se usa en E1.
    return sess;
  }

  async clearSession(profile: string) {
    const sess = session.fromPartition(this.getPartition(profile));
    await sess.clearStorageData();
    // E1: no hay refresh token. Si en el futuro se agrega un device token,
    // aquí se eliminaría de keytar.
  }
}
```

### IPC seguro

El main process registra handlers `ipcMain.handle('auth:login', ...)`, `auth:logout`, `auth:me`, `auth:switchProfile`, `auth:getProfiles`. El preload solo expone la interfaz segura al renderer.

```typescript
// desktop/src/main/preload.ts
import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('faberloom', {
  auth: {
    login: (credentials) => ipcRenderer.invoke('auth:login', credentials),
    logout: () => ipcRenderer.invoke('auth:logout'),
    me: () => ipcRenderer.invoke('auth:me'),
    switchProfile: (profile) => ipcRenderer.invoke('auth:switchProfile', profile),
    getProfiles: () => ipcRenderer.invoke('auth:getProfiles'),
  },
});
```

### Endpoints reutilizados de M08

| Método | Ruta | Uso en desktop |
|---|---|---|
| POST | `/auth/login` | Paso 1 credenciales |
| POST | `/auth/totp` | Paso 2 TOTP |
| GET | `/auth/me` | Reanudación de sesión |
| POST | `/auth/logout` | Logout server-side |
| POST | `/auth/revoke-session` | Revocación remota |

## 5. Cambios en frontend

### Desktop
- **Splash screen**: reanuda sesión si la partición tiene cookie válida.
- **Login window**: usa IPC para enviar credenciales al main process.
- **Profile selector**: si el usuario tiene varios tenants, elige profile al abrir.
- **Mesa de Control**: renderiza con `contextIsolation=true`, sin acceso a Node.

### Web
- Sin cambios; M18 es desktop-only.

## 6. Cambios en infraestructura/deploy

- Dependencias npm:
  ```bash
  npm install electron keytar electron-store
  ```
- Variables de entorno:
  ```bash
  API_URL=https://api.faberloom.io
  SESSION_PARTITION_PREFIX=persist:faberloom
  KEYTAR_SERVICE=faberloom
  ```
- `BrowserWindow` con:
  ```typescript
  webPreferences: {
    contextIsolation: true,
    nodeIntegration: false,
    preload: path.join(__dirname, 'preload.js'),
  }
  ```

## 7. Secuencia de tareas

1. Scaffolding del proceso main de Electron.
2. Implementar `ElectronSessionManager` con particiones por profile.
3. Configurar `BrowserWindow` hardened (`contextIsolation`, `nodeIntegration`).
4. Implementar preload script con IPC mínimo.
5. Integrar login flow con M08 (credenciales → TOTP → cookie).
6. Implementar reanudación vía `/auth/me` + cookie de partición.
7. Implementar logout local (partición + keychain) y remoto (M08).
8. Implementar profile selector y switch de partición.
9. Tests de seguridad: secretos no en renderer, particiones aisladas.
10. Documentación de hardening para auditoría.

## 8. Criterios de aceptación

1. `test_session_token_not_in_renderer_storage`: no hay tokens en `localStorage`/`sessionStorage`.
2. `test_partition_isolation`: cookie de tenant A no es accesible desde partición de tenant B.
3. `test_logout_clears_partition_and_keychain`: después del logout no quedan secretos locales.
4. `test_context_isolation_enabled`: `window.process` no expone Node en renderer.
5. `test_remote_revocation_invalidation`: revocar sesión desde M08 invalida la sesión desktop.
6. `test_keychain_unavailable_fail_closed`: si keytar falla, no se persiste sesión localmente.
7. Login con Owner requiere TOTP.

## 9. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Tokens en renderer | P0 fuga | `contextIsolation` + cookies httpOnly solo en main |
| Particiones compartidas | P0 cross-tenant | Naming estricto por profile/tenant |
| Keychain no disponible | P2 UX | Fail-closed: re-login, nunca fallback a localStorage |
| Partition corrupta | P2 login loop | Recrear partición y exigir re-login |
| IPC expone funciones peligrosas | P1 RCE | Preload mínimo, validación de argumentos |

## 10. Decisiones de arquitectura tomadas

1. **No tokens en `localStorage` nunca.** Cualquier excepción es P0.
2. **Partición por profile, no solo por tenant.** Permite un mismo usuario con múltiples perfiles/tenants en la misma máquina.
3. **Reutilizar sesión server-side de M08.** El desktop no tiene un modelo de sesión paralelo; solo gestiona el contenedor local.
4. **`keytar` primario, `safeStorage` fallback.** Ambos delegan al keychain del SO.
5. **Logout limpia todo.** Partición + keychain; preferencias no secretas pueden conservarse según política.

---
*Plan M18 — Foundation Beta v1.3.1*
