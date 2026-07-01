# M08 Auth Session — Plan de Implementación

## 1. Resumen ejecutivo

M08 autentica a las personas, liga la sesión al tenant correcto y la mantiene server-side en Redis para poder revocarla al instante.  Es el segundo módulo del SPINE; sin él M09, M18 y M07 no pueden operar.

**Rol en el SPINE:** consume `tenant_context` de M16 y provee sesión con `tenant_id`, `user_id` y rol base a M09.  Emite eventos `auth.login.success`, `auth.login.failed`, `auth.2fa.locked`, `session.revoked`.

## 2. Entrada/salida

### Entrada
- `tenant_id` resuelto por M16 (desde subdominio o sesión).
- Tablas `tenants`, `users`, `memberships` (creadas parcialmente en M07/M09).

### Salida
- `session_id` opaco en Redis.
- Cookie httpOnly/Secure/SameSite=Strict (web) o Electron partition (desktop).
- `/auth/me` devuelve `{user_id, tenant_id, roles, active_hat}`.
- Eventos de auth en outbox (M15).

## 3. Modelo de datos

### Tablas

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,  -- argon2id
    display_name TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    totp_secret TEXT,             -- encrypted at rest
    backup_codes TEXT[],          -- hashed
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    roles TEXT[] NOT NULL DEFAULT '{}',
    active_hat TEXT,
    status TEXT NOT NULL DEFAULT 'invited' CHECK (status IN ('invited','active','suspended','revoked')),
    invited_by UUID REFERENCES users(id),
    invited_at TIMESTAMPTZ,
    accepted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(user_id, tenant_id)
);

CREATE INDEX idx_memberships_user_id ON memberships(user_id);
CREATE INDEX idx_memberships_tenant_id ON memberships(tenant_id);
CREATE INDEX idx_memberships_status ON memberships(tenant_id, status);
```

### Redis (sesiones)

Key: `tenant:{tenant_id}:session:{session_id}`

```json
{
  "user_id": "uuid",
  "tenant_id": "uuid",
  "roles": ["owner"],
  "active_hat": "owner",
  "issued_at": "2026-07-01T12:00:00Z",
  "expires_at": "2026-07-01T20:00:00Z",
  "remember": false
}
```

TTL: 8h normal, 30 días si `remember=true`.

## 4. Cambios en API/backend

### Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/auth/login` | Paso 1: email + password |
| POST | `/api/auth/2fa` | Paso 2: TOTP |
| POST | `/api/auth/logout` | Revoca sesión actual |
| POST | `/api/auth/logout-all` | Revoca todas las sesiones del usuario en el tenant |
| GET  | `/api/auth/me` | Reanuda sesión (Electron/desktop) |
| POST | `/api/auth/session/{id}/revoke` | Owner/Admin revoca sesión de miembro |

### Flujo de login

```text
POST /api/auth/login {email, password}
  → OK + {"requires_2fa": true, "login_token": "<opaque>"}
  → 401 credenciales inválidas (mensaje genérico)

POST /api/auth/2fa {login_token, totp, remember?}
  → crea sesión Redis
  → set-cookie: session_id=<uuid>; HttpOnly; Secure; SameSite=Strict
  → event auth.login.success → outbox
```

### Helpers

```python
# apps/auth/session.py
from django.conf import settings
import redis
import json
import uuid
from datetime import datetime, timedelta, timezone

redis_client = redis.Redis.from_url(settings.REDIS_URL)

def create_session(user_id, tenant_id, roles, active_hat, remember=False) -> str:
    session_id = uuid.uuid4().hex
    now = datetime.now(timezone.utc)
    ttl = 30 * 86400 if remember else 8 * 3600
    payload = {
        "user_id": str(user_id),
        "tenant_id": str(tenant_id),
        "roles": roles,
        "active_hat": active_hat,
        "issued_at": now.isoformat(),
        "expires_at": (now + timedelta(seconds=ttl)).isoformat(),
        "remember": remember,
    }
    key = f"tenant:{tenant_id}:session:{session_id}"
    redis_client.setex(key, ttl, json.dumps(payload))
    return session_id

def get_session(session_id, tenant_id) -> dict | None:
    key = f"tenant:{tenant_id}:session:{session_id}"
    raw = redis_client.get(key)
    return json.loads(raw) if raw else None

def revoke_session(session_id, tenant_id) -> None:
    key = f"tenant:{tenant_id}:session:{session_id}"
    redis_client.delete(key)
```

### Middleware de sesión

- `SessionMiddleware`: lee cookie `session_id`, valida en Redis, setea `request.user` y `request.tenant_id`.
- Integración con `TenantMiddleware` de M16: `request.tenant_id` se propaga a `app.tenant_id`.

### 2FA

- TOTP obligatorio para Owner.
- 10 backup codes generados al enrolar, hasheados con bcrypt.
- 3 fallos → estado `locked` por 15 min.

### Password

- argon2id mediante `django.contrib.auth.hashers.Argon2PasswordHasher`.
- Validación de fortaleza mínima: 12 caracteres, mayúscula, minúscula, número.

## 5. Cambios en frontend

### Web (Next.js)
- Pantalla `/login` con email/password.
- Pantalla `/2fa` con campo TOTP.
- Banner "conectado como [nombre] / [tenant]".
- Settings → perfil: cambiar password, re-enrolar 2FA.

### Desktop (Electron)
- Login web embebido en partition `persist:faberloom-{tenant_id}`.
- Reanudación vía `GET /api/auth/me` al inicio.
- Tokens sensibles en keytar; cookie httpOnly en partition.
- `contextIsolation=true`, `nodeIntegration=false`.

## 6. Cambios en infraestructura/deploy

- Añadir `django-redis`, `pyotp`, `argon2-cffi` a `requirements.txt`.
- Configurar `SESSION_ENGINE` para usar Redis (aunque usaremos sesiones custom, no `django.contrib.sessions`).
- Variables de entorno:
  ```bash
  REDIS_URL=redis://redis:6379/0
  SESSION_TTL_SECONDS=28800
  SESSION_REMEMBER_TTL_SECONDS=2592000
  TOTP_ISSUER=FaberLoom
  ```

## 7. Secuencia de tareas

1. Crear apps Django `auth` y `users`.
2. Modelos `User`, `Membership`.
3. Configurar argon2id como hasher.
4. Implementar TOTP con `pyotp`; generar QR para enrolamiento.
5. Implementar Redis session store.
6. Implementar endpoints `/auth/login`, `/auth/2fa`, `/auth/me`, `/auth/logout`.
7. Implementar `SessionMiddleware`.
8. Integrar con M16: `request.tenant_id` → `app.tenant_id`.
9. Implementar revocación remota de sesiones.
10. Emitir eventos auth a outbox (M15).
11. Tests unitarios e integración.
12. Actualizar Electron para usar partitions + keytar.

## 8. Criterios de aceptación

1. Owner puede loguearse con email + password + TOTP.
2. Cookie/session no contiene claims sensibles en cliente.
3. `/auth/me` requiere sesión válida y devuelve `tenant_id` correcto.
4. Revocación remota invalida sesión en <1s.
5. 3 fallos TOTP bloquean login por 15 min.
6. Cambio de password invalida todas las sesiones del usuario.
7. Electron no expone token al renderer (verificar con test).
8. Redis caído → modo degradado, requiere re-login.

## 9. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| JWT en localStorage | P0 token leak | Cookie httpOnly + Electron partition |
| Sesión en DB sin Redis | P1 no revocable | Redis server-side |
| TOTP brute-force | P1 takeover | 3 fallos → lockout 15 min |
| Password débil | P1 takeover | Validación + argon2id |
| Electron partition compartida | P0 cross-tenant | Partition por tenant_id |
| Redis caído bloquea todo | P1 downtime | Fail-closed: exigir re-login |

## 10. Decisiones de arquitectura tomadas

1. **Sesión server-side en Redis, no JWT.**  Permite revocación inmediata y evita tokens en cliente.
2. **2FA TOTP obligatorio solo Owner.**  Operator puede usar 2FA opcional en E1, Owner es obligatorio.
3. **Cookie httpOnly/Secure/SameSite=Strict.**  Mitiga XSS/CSRF.
4. **TTL 8h / remember 30 días.**  Jornada laboral + UX desktop razonable.
5. **argon2id.**  Recomendación del spec M08; Django lo soporta nativamente.
6. **Partition Electron por tenant.**  Aisla cookies entre tenants en desktop.

---
*Plan M08 — Foundation Beta v1.3.1*
