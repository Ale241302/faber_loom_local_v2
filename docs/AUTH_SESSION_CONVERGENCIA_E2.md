# Auth y sesión — Convergencia backend/Foundation/frontend (E2)

**id:** AUTH_SESSION_CONVERGENCIA_E2  
**versión:** 1.0  
**fecha:** 2026-07-06  
**estado:** vigente  

---

## 1. Decisión

El runtime de FaberLoom usa **auth local** basada en JWT legacy entregado como cookie `HttpOnly` + `SameSite=Strict`, validado por `FABERLOOM_SECRET_KEY` y derivado de `FABERLOOM_USERS`.

La **fuente de verdad de identidad** es **Foundation Beta** (`app/src/foundation/`):

- `tenant_id`
- `user_id` (UUID Foundation)
- `role` / `roles`

El JWT legacy solo transporta `sub` (email). Al validar el token, `app/src/auth.py::get_current_user` enriquece los claims consultando Foundation. Si Foundation no tiene un usuario activo para ese email, el backend resuelve un usuario **legacy local** (`tenant_id='default'`, `user_id=sub`) y lo marca como `foundation_resolved=false`.

---

## 2. Puentes legacy activos y advertencias

| Puente | Estado | Riesgo | Plan |
|---|---|---|---|
| JWT legacy como transporte de sesión | **Activo intencional** | Bajo si la cookie es `HttpOnly`/`Secure`/`SameSite=Strict` y el secret es fuerte. | Se mantiene durante E2; se evaluará OIDC/token gestionado en E3. |
| `FABERLOOM_USERS` JSON de email/password | **Activo** | Medio: manejo manual de credenciales, sin rotación. | Reemplazar por Foundation user management en E2-2/E2-3; mientras tanto, secret fuerte y `.env` no versionado. |
| Frontend obtiene identidad vía `/api/me` | **Activo desde E2-0** | Bajo. | El frontend ya no confía en `localStorage` para claims de sesión; solo usa `faberloom_user` como hint de email de login. |
| `localStorage.faberloom_token` | **Eliminado** | — | Limpiado en `AuthGate` al arrancar. |
| `foundation_resolved=false` | **Admitido** | Medio: un usuario legacy sin Foundation puede actuar con rol `owner` en el tenant default. | Solo aceptable en despliegues single-user o de desarrollo. En instancia compartida (E2-1) todo usuario debe existir en Foundation. |

---

## 3. Contrato de identidad

### Backend

```python
# app/src/auth.py
get_current_user(request) -> dict:
    sub: str          # email (legacy) o "local"
    tenant_id: str    # Foundation tenant o "default"
    user_id: str      # Foundation UUID o sub (legacy)
    role: str         # Foundation primary role o "admin"/"owner"
    roles: list[str]  # Foundation roles o []
    foundation_resolved: bool
```

### API

- `POST /api/auth/login` → crea cookie `faberloom_at` (access token) y `faberloom_rt` (refresh token).
- `POST /api/auth/logout` → revoca refresh token y borra cookies.
- `GET /api/me` → devuelve `UserRead` con claims resueltos por el backend.

### Frontend

- `AuthGate` llama a `/api/me` al arrancar para decidir si hay sesión.
- `authHeaders()` no envía token manual; la cookie se transmite automáticamente.
- El footer muestra `user.email` y un rol estático; en E2-2 se actualizará para mostrar el rol real de Foundation.

---

## 4. Escenarios de fallback

| Escenario | `foundation_resolved` | Actor efectivo | Uso esperado |
|---|---|---|---|
| Foundation activa + email coincide | `true` | Foundation user | Instancia compartida E2-1+. |
| Foundation inactiva/no existe + `FABERLOOM_USERS` configurado | `false` | Legacy user (`sub` como `user_id`) | Desarrollo local o single-user. |
| Sin `FABERLOOM_USERS` ni token | N/A | `local` | Solo cuando `FABERLOOM_AUTH_DISABLED` o sin users configurados. |

---

## 5. Riesgos P0 mitigados

- **Fuga cross-tenant:** `get_current_user` enriquece `tenant_id` desde Foundation; `Context` lo propaga a todas las queries.
- **Suplantación de actor:** `approved_by` y `actor_id` se toman de `Context.resolved_actor_id()`, no del cliente.
- **Token robado:** cookie `HttpOnly` no accesible por JS; refresh token rota en cada uso.

---

## 6. Próximos pasos (E2-2/E2-3)

1. Migrar administración de usuarios a Foundation UI/API.
2. Eliminar dependencia de `FABERLOOM_USERS` JSON.
3. Añadir roles reales en frontend (footer, permisos de UI).
4. Evaluar OIDC/SAML para MWT domain en E3.

---

## 7. Referencias

- `app/src/auth.py`
- `app/src/api.py` (`/api/me`)
- `app/src/context.py`
- `app/static/js/app.jsx` (`AuthGate`, `authHeaders`)
- `app/tests/test_e2_0_auth_context.py`
- `app/tests/test_e2_0_auth_me.py`
