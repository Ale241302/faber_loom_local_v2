# M09 RBAC — Plan de Implementación

## 1. Resumen ejecutivo

M09 gobierna qué puede ver y hacer cada persona por superficie, con mínimo privilegio y multi-rol seleccionable.  Es el tercer módulo del SPINE; bloquea aprobaciones HITL, cambios de roles y flujos del bootstrap.

**Rol en el SPINE:** consume sesión de M08, provee `actor_role_at_decision` a M12/M13/M14/M17 y decide permisos para M07/M13.

## 2. Entrada/salida

### Entrada
- Sesión autenticada de M08: `user_id`, `tenant_id`, `roles[]`, `active_hat`.
- Tabla `memberships` (creada en M08).

### Salida
- Decisión de permiso por request: `allowed=True/False`.
- `active_hat` normalizado.
- Eventos `user.invited`, `user.role_changed`, `user.revoked`, `permission.denied`.
- `actor_role_at_decision` para audit.

## 3. Modelo de datos

### Tablas

```sql
CREATE TABLE roles (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    permissions JSONB NOT NULL DEFAULT '{}'
);

INSERT INTO roles (id, name, permissions) VALUES
('owner', 'Owner', '{
  "workloom": "full", "workspace": "full", "agent_factory": "full",
  "skill_factory": "full", "audit": "full", "config": "full", "users": "full"
}'),
('admin', 'Admin', '{
  "workloom": "full", "workspace": "full", "agent_factory": "write",
  "skill_factory": "write", "audit": "read", "config": "write", "users": "write"
}'),
('operator', 'Operator', '{
  "workloom": "write", "workspace": "write", "agent_factory": "none",
  "skill_factory": "none", "audit": "read_self", "config": "none", "users": "none"
}'),
('supervisor', 'Supervisor', '{
  "workloom": "write", "workspace": "write", "agent_factory": "read",
  "skill_factory": "read", "audit": "read", "config": "none", "users": "none"
}'),
('viewer', 'Viewer', '{
  "workloom": "read", "workspace": "read", "agent_factory": "none",
  "skill_factory": "none", "audit": "read_self", "config": "none", "users": "none"
}');

CREATE TABLE memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    roles TEXT[] NOT NULL DEFAULT '{}',
    active_hat TEXT,
    status TEXT NOT NULL DEFAULT 'invited' CHECK (status IN ('invited','active','suspended','revoked','expired')),
    invited_by UUID REFERENCES users(id),
    invited_at TIMESTAMPTZ,
    accepted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(user_id, tenant_id)
);
```

### ENUMs
- `membership_status`: invited, active, suspended, revoked, expired.
- `permission_level`: none, read, read_self, write, full.

## 4. Cambios en API/backend

### Permission resolver

```python
# apps/rbac/permissions.py
from functools import wraps
from rest_framework.exceptions import PermissionDenied

SURFACE_MAP = {
    "workloom": ["view", "approve", "edit", "create"],
    "workspace": ["view", "edit"],
    "agent_factory": ["view", "create", "edit"],
    "skill_factory": ["view", "create", "edit"],
    "audit": ["view", "export"],
    "config": ["view", "edit"],
    "users": ["view", "invite", "change_roles", "revoke"],
}

def resolve_permission(membership, surface, action):
    if not membership or membership.status != "active":
        return False
    active_hat = membership.active_hat or membership.roles[0]
    # ... check role permission matrix
    return allowed

def require_permission(surface, action):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            membership = request.membership
            if not resolve_permission(membership, surface, action):
                emit_permission_denied(request, surface, action)
                raise PermissionDenied(f"Requires {surface}:{action}")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

### Middleware

- `RBACMiddleware`: carga `request.membership` desde `request.user` + `request.tenant_id`.
- Si usuario tiene múltiples roles, `active_hat` se toma del header `X-Active-Hat` (solo si pertenece a sus roles) o del rol por defecto.

### Endpoints

| Método | Ruta | Permiso |
|---|---|---|
| GET  | `/api/memberships` | users:view |
| POST | `/api/memberships` | users:invite |
| PATCH | `/api/memberships/{id}` | users:change_roles |
| POST | `/api/memberships/{id}/revoke` | users:revoke |
| POST | `/api/memberships/me/hat` | cualquier usuario activo |

### Reglas de negocio

- Owner no puede auto-revocarse si es el último Owner del tenant.
- Admin no puede crear otro Owner ni modificar Owner.
- Invitación expira a los 7 días → status `expired`.
- Al revocar: cerrar sesiones del usuario en el tenant (M08), tasks abiertas pasan a `unassigned`.

### Eventos

- `user.invited`: al crear membership en `invited`.
- `user.role_changed`: al modificar roles o hat.
- `user.revoked`: al revocar.
- `permission.denied`: al rechazar una acción (con throttling para no saturar).

## 5. Cambios en frontend

### Web
- Vista "Usuarios y roles": lista, invitar, cambiar roles, revocar.
- UI muestra roles E1: Owner/Operator (Admin/Supervisor/Viewer deshabilitados con tooltip "E3+").

### Desktop
- Selector de "hat" en header si el usuario tiene múltiples roles.
- Superficies/acciones no permitidas aparecen ocultas o deshabilitadas con tooltip "requiere rol [X]".

## 6. Cambios en infraestructura/deploy

- Seed de 5 roles canónicos en migración `0004_seed_roles.py`.
- Variables de entorno:
  ```bash
  INVITATION_TTL_DAYS=7
  ```

## 7. Secuencia de tareas

1. Crear app Django `rbac`.
2. Modelos `Role`, actualizar `Membership`.
3. Seed de 5 roles canónicos.
4. Implementar `RBACMiddleware`.
5. Implementar `resolve_permission` y `require_permission`.
6. Implementar endpoints de gestión de memberships.
7. Implementar invitaciones con email (M07/M08 provee email provider).
8. Implementar revocación + cierre de sesiones + reasignación de tasks.
9. Emitir eventos a outbox (M15).
10. Integrar con M12 para audit de cambios.
11. Tests de matriz de permisos.
12. UI web/desktop.

## 8. Criterios de aceptación

1. Owner puede invitar Operator.
2. Admin (E3+) no puede crear Owner.
3. Último Owner no puede auto-revocarse.
4. Cambio de rol se audita con `actor_role_at_decision` anterior y nuevo.
5. UI oculta acciones no permitidas; server rechaza si hay desync.
6. Selector de hat cambia permisos activos en desktop.
7. Revocación cierra sesiones del afectado en <1s.
8. Tasks abiertas de Operator revocado pasan a `unassigned`.

## 9. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| UI es la verdad, no el server | P0 escalation | Server-side permission check obligatorio |
| Hat spoofing | P0 escalation | Validar que hat pertenece a roles del usuario |
| Último Owner revocado | P1 tenant sin gestión | Bloqueo explícito |
| Invitación sin expirar | P1 acceso zombie | TTL 7 días + status expired |
| Cambio de rol no auditado | P1 compliance | Audit en M12 obligatorio |

## 10. Decisiones de arquitectura tomadas

1. **5 roles canónicos seedeados, 2 activos en E1.**  Schema preparado para E3; UI limitada a Owner/Operator.
2. **Permission check server-side como verdad.**  UI es solo presentación.
3. **`active_hat` via header validado.**  No se confía en el cliente; se verifica contra `membership.roles`.
4. **`actor_role_at_decision` congelado en audit.**  Cambios futuros no reescriben decisiones pasadas.
5. **Reasignación de tasks a cola general.**  Sencillo y sin inventar supervisor específico.

---
*Plan M09 — Foundation Beta v1.3.1*
