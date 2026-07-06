# Informe de readiness E2-0 - Activar costuras + higiene E1

**id:** E2_0_READINESS_REPORT_20260706  
**version:** 1.0  
**fecha:** 2026-07-06  
**autor:** auditoria de codigo / arquitecto  
**base:** PLAN_TRABAJO_E2_FUGU_v3, PLAN_DESARROLLO_SPACELOOM_ETAPA2_v1, ESTADO_AVANCE_ETAPA1_Y_FOUNDATION_BETA_20260706.md, codigo en app/src.

---

## 1. Alcance y criterios de aceptacion E2-0

Segun los planes vigentes, E2-0 debe dejar el runtime app/ listo para multi-usuario interno. Los criterios de aceptacion son:

1. La app E1 sigue funcionando con un usuario autenticado.
2. Cada accion relevante deja auditoria con actor_id, actor_role_at_decision, tenant_id, workspace_id.
3. Ninguna query critica opera sin Context(workspace_id, tenant_id, user_id).
4. Backend, Foundation y frontend resuelven el **mismo** usuario/tenant/rol.
5. Higiene heredada de E1 cerrada (documentacion, licencia, promocion del spike).
6. Migracion SQLite a Postgres planificada y ensayada con verificacion de conteos.
7. Tenant canario sembrado para pruebas de aislamiento.
8. Suite E1 re-corre y se agregan regresiones de Context/audit/sesion.

---

## 2. Resumen ejecutivo

| Componente | Estado | Nota |
|---|---|---|
| Schema contract-first (tenant_id, user_id, actor_*, versiones) | [OK] Listo | SCHEMA_VERSION 21 (app/src/models.py) con triggers NOT-NULL para tenant_id y backfills. |
| Context seam (app/src/context.py) | [OK] Listo | Dataclass y helpers presentes; usada por la mayoria de helpers DB. |
| DB helpers scoping (app/src/db.py) | [WARN] Parcial | Casi todos filtran por workspace_id + tenant_id; algunos usan ctx.user_id como actor sin fallback resolved_actor_id(). |
| Audit dual (app/src/audit.py) | [WARN] Parcial | AuditWriter escribe tabla + JSONL; actor_role_at_decision y approved_by aun dependen del JWT legacy. |
| Auth legacy (app/src/auth.py) | [FAIL] No listo | DEFAULT_TENANT_ID hard-coded; rol fijo "admin"; no lee Foundation. |
| Foundation session / RBAC (app/src/foundation/*) | [OK] Listo (Foundation) | Sesiones fnds_..., roles, permisos, TOTP, audit hash-chain, SSO bridge JWT a Foundation. |
| **Unificacion auth backend - Foundation - frontend** | [FAIL] **No listo** | api.py construye Context desde JWT legacy; Foundation routes usan require_session; son dos identidades paralelas. |
| Frontend auth (app/static/js/app.jsx) | [WARN] Parcial | Cookie HttpOnly + /api/auth/login; sin exposicion de tenant/rol ni self-service Foundation. |
| Tests de aislamiento | [WARN] Parcial | test_tenant_contamination.py, test_user_isolation.py, test_foundation_*.py existen; faltan tests E2-0 de unificacion. |
| Migracion SQLite a Postgres | [FAIL] No listo | No se encontraron scripts ni artefactos de migracion en el repo. |
| Tenant canario en tablas app | [FAIL] No listo | Foundation tiene mecanismo M16; la app principal no tiene semilla canaria. |

**Veredicto global:** E2-0 **NO esta listo para build**. La infraestructura de costuras (schema, Context, AuditWriter, Foundation spine) esta construida, pero el punto critico - que el backend principal, Foundation y el frontend resuelvan una sola identidad real - aun es hibrido. Hasta que no converja, los criterios 2, 3 y 4 del DoD estan en riesgo.

---

## 3. Estado detallado por componente

### 3.1 Auth / identidad runtime

#### 3.1.1 JWT legacy (app/src/auth.py)

```python
# auth.py ~ lineas 132-144
def create_access_token(email: str, role: str = "admin") -> str:
    payload = {
        "sub": email, "role": role,
        "tenant_id": DEFAULT_TENANT_ID,  # siempre "default" u override env
        ...
    }

def get_current_user(request: Request) -> dict[str, Any]:
    ...
    payload.setdefault("tenant_id", DEFAULT_TENANT_ID)
    request.state.user = payload
    return payload
```

- DEFAULT_TENANT_ID = os.getenv("FABERLOOM_TENANT_ID", "default") (context.py:25).
- create_access_token fuerza tenant_id=DEFAULT_TENANT_ID y role="admin" por defecto.
- El fallback local (FABERLOOM_AUTH_DISABLED o sin usuarios) retorna {"sub": "local", "role": "owner", "tenant_id": DEFAULT_TENANT_ID}.
- Los endpoints /auth/login, /auth/refresh, /auth/logout usan la tabla refresh_tokens (rotacion con SHA-256) y la cookie HttpOnly faberloom_at.

**Problema para E2-0:** el JWT no refleja el tenant/rol reales de Foundation. Un usuario Foundation con rol viewer u operator llegaria al API principal como role="admin" y tenant_id="default", rompiendo actor_role_at_decision y el aislamiento por tenant.

#### 3.1.2 Foundation session (app/src/foundation/core.py, m08_auth_session.py)

- SessionContext (core.py ~ linea 477) porta session_id, tenant_id, user_id, email, permissions, roles.
- require_session (core.py ~ linea 625) valida el token fnds_... o el cookie fnd_session; si falla, intenta _bootstrap_jwt_context y _sso_jwt_context.
- _sso_jwt_context (core.py ~ linea 580) promueve un JWT principal de FaberLoom a sesion Foundation **solo si** el sub (email) coincide con un fnd_users activo. Esto es el mecanismo correcto para unificar sin romper el shell.
- M08 provee login con PBKDF2 + TOTP, lockout, revocacion de sesiones y audit hash-chain.
- M09 provee RBAC real con roles owner, admin, operator, viewer y permisos.
- M16 provee aislamiento por tenant con scoping fail-closed.

**Problema para E2-0:** aunque Foundation es funcional, el **API principal (api.py) no consume require_session**. main.py monta foundation_router sin dependencia JWT (main.py ~ linea 122) y api_router con Depends(get_current_user) (main.py ~ linea 123), pero nunca reconcilia ambos mundos. El SSO bridge solo beneficia a rutas /foundation/*; las rutas /workspaces/* siguen usando el JWT legacy.

### 3.2 Context seam

#### 3.2.1 app/src/context.py

- Context ya tiene workspace_id, tenant_id, user_id, actor_id, actor_role_at_decision.
- system_context() y with_workspace() estan disponibles.
- resolved_actor_id() hace fallback actor_id -> user_id.

#### 3.2.2 app/src/api.py - context_from_request

```python
# api.py (context_from_request)
def context_from_request(request, workspace_id=None) -> Context:
    user = getattr(request.state, "user", None)
    if user:
        tenant_id = user.get("tenant_id") or DEFAULT_TENANT_ID
        user_id = user.get("sub") or "local"
        actor_id = user_id
        actor_role = user.get("role") or "owner"
    elif os.getenv("FABERLOOM_DEV_TRUST_HEADERS"):
        tenant_id = request.headers.get("x-tenant-id") or DEFAULT_TENANT_ID
        user_id = request.headers.get("x-user-id") or "local"
        actor_id = request.headers.get("x-actor-id") or user_id
        actor_role = request.headers.get("x-actor-role") or "owner"
    else:
        tenant_id, user_id, actor_id, actor_role = DEFAULT_TENANT_ID, "local", "local", "owner"
```

- Construye Context a partir del JWT legacy o dev-trust headers.
- Todos los endpoints /workspaces/{id}/... usan esta funcion.

**Problema para E2-0:** actor_role se toma directamente del claim JWT (role) o dev header. No hay consulta a Foundation para obtener los roles/permisos reales del usuario. Si el JWT es manipulado o el claim es "admin", el API principal lo acepta.

### 3.3 Database / schema

#### 3.3.1 app/src/models.py - SCHEMA_VERSION = 21

- Migracion v21 agrega:
  - Tabla refresh_tokens (rotacion de tokens).
  - tenant_id NOT NULL con default 'default' en todas las tablas workspace-owned.
  - Triggers trg_*_tenant_nn que abortan INSERT sin tenant_id.
  - Indices por tenant_id en workspace, chat, message, kb_source, draft, routine, routine_run, usage_record, mail_message, audit_log, etc.
- Todos los campos latentes (user_id, actor_id, actor_role_at_decision, approved_by, routine_version, skill_version, schema_version, source_version) estan presentes.

#### 3.3.2 app/src/db.py

- connect() usa WAL, foreign keys, busy timeout.
- Helpers de workspaces, chats, mensajes, KB, drafts, routines, runs, mail, usage y audit reciben Context y filtran por workspace_id + tenant_id.
- Ejemplos correctos:
  - get_chat: WHERE id = ? AND workspace_id = ? AND tenant_id = ? AND user_id = ?.
  - create_routine_run: inserta tenant_id, user_id, actor_id, actor_role_at_decision.
  - insert_usage_record: idem.

**Problemas menores / de higiene:**
- Algunos helpers usan ctx.user_id directamente como actor sin pasar por ctx.resolved_actor_id(). Aunque hoy actor_id suele igualar user_id, esto rompe el contrato si en el futuro actor_id representa una identidad delegada.
- No hay wrapper que impida llamar un helper de aplicacion sin Context (es convencion, no enforcement).

### 3.4 Audit

#### 3.4.1 app/src/audit.py - AuditWriter

```python
class AuditWriter:
    def write(self, ctx, conn, *, action, payload=None, approved_by=None, ...):
        event = AuditEvent(
            workspace_id=ctx.require_scoped_workspace(),
            actor_id=ctx.resolved_actor_id(),
            actor_role_at_decision=ctx.actor_role_at_decision,
            action=action, payload=payload or {}, tenant_id=ctx.tenant_id,
            user_id=ctx.user_id, approved_by=approved_by, ...)
        with transaction(conn):
            insert_audit_log(ctx, conn, ...)
        if mirror_jsonl and not outer_transaction:
            self.mirror(event)
```

- Escribe a audit_log (DB) y a audit.jsonl (mirror).
- Usa ctx para tenant_id, user_id, actor_id, actor_role_at_decision.

#### 3.4.2 Foundation audit (app/src/foundation/core.py, m12_audit_trail.py)

- fnd_audit_log con hash-chain (previous_hash), 18+ campos, append-only.
- audit_log() en core.py es usado por Foundation; SessionContext.audit() lo invoca.

**Problema para E2-0:** hay **dos audit trails** (audit_log de app y fnd_audit_log de Foundation) sin correlacion de IDs. Cuando un usuario actua en el API principal, la auditoria va a audit_log; cuando actua en Foundation, va a fnd_audit_log. Para E2-0/E2-1 no es bloqueante si se documenta, pero para E2-2+ se necesitara unificar la narrativa de auditoria por actor.

### 3.5 Frontend

#### 3.5.1 app/static/js/app.jsx

- LoginScreen (app.jsx ~ linea 2561) llama POST /api/auth/login y deja que el backend setee la cookie faberloom_at.
- AuthGate (app.jsx ~ linea 2654) prueba la sesion con GET /api/workspaces (cookie se envia automaticamente).
- authHeaders() (app.jsx inicio) retorna {}; se confia en la cookie HttpOnly.
- La UI no muestra tenant, rol ni permite cambiar de tenant.
- Hay una vista FoundationSection (foundation.jsx) montada bajo nav === "foundation", pero el shell no consume /foundation/auth/me para mostrar identidad.

**Problema para E2-0:** el frontend no sabe el rol real del usuario. Por tanto no puede ocultar/mostrar acciones segun permisos (p. ej. aprobacion de drafts, administracion de proveedores). Esto es aceptable como deuda de E2-0 si el backend ya falla cerrado, pero debe entrar en el plan de E2-2.

### 3.6 Tests existentes

| Test | Que cubre | Estado |
|---|---|---|
| test_p0_security.py | CORS, confirmation tokens, HITL, injection basico | [OK] verde (supuesto por suite) |
| test_tenant_contamination.py | Aislamiento cross-tenant en tablas app con x-tenant-id | [OK] presente |
| test_user_isolation.py | Aislamiento per-user (chat, providers, SMTP) | [OK] presente |
| test_foundation_spine.py | Bootstrap, login, 2FA, RBAC, policy, audit chain, M16 | [OK] presente |
| test_foundation_ops.py | M10/M13/M14/M17 + permisos + tenant isolation | [OK] presente |
| test_foundation_desktop.py | M18/M19/M20 device auth, sync, updates | [OK] presente |
| test_tenants_multi.py | Crear tenants, mover usuarios, self-service | [OK] presente |
| test_sl0_backend.py | Schema, seed idempotencia, context scope | [OK] presente |

**Faltan para E2-0:**
- Test de que un JWT principal se convierte en Context con tenant/rol real de Foundation.
- Test de que un usuario Foundation viewer no puede ejecutar acciones de owner en el API principal.
- Test de que actor_role_at_decision y approved_by en audit_log reflejan el rol Foundation real.
- Test de tenant canario en tablas de la app principal (no solo Foundation).

---

## 4. Gaps criticos que bloquean o debilitan E2-0

### 4.1 Auth unification - P0 para E2-0

**Descripcion:** api.py no consulta Foundation para resolver tenant_id, user_id y actor_role reales.
**Impacto:** cualquier usuario autenticado por Foundation puede actuar en el API principal con tenant_id="default" y role="admin" si posee un JWT valido. El RBAC de Foundation no se aplica al telar operativo.
**Archivos a modificar:** app/src/auth.py, app/src/api.py, app/src/context.py (opcional), app/src/main.py.
**Recomendacion:**
1. En get_current_user (o en un nuevo get_current_user_unified), si existe un JWT valido, buscar en Foundation el usuario por email, obtener su tenant_id, user_id y roles.
2. Setear request.state.user con claims enriquecidos (tenant_id, user_id, role real).
3. Hacer que context_from_request use esos claims.
4. Mantener el fallback FABERLOOM_AUTH_DISABLED / local user, pero con rol owner limitado y tenant_id explicito.

### 4.2 Tenant resolution - P0

**Descripcion:** DEFAULT_TENANT_ID es una constante env. create_access_token la fuerza en el payload.
**Impacto:** en una instancia con un solo tenant (MWT) esto funciona por coincidencia, pero no escala a multi-tenant interno ni permite el tenant canario.
**Archivos a modificar:** app/src/auth.py, app/src/api.py.

### 4.3 Role enforcement en API principal - P0 para E2-2, deuda aceptada en E2-0 si se documenta

**Descripcion:** los endpoints del API principal no verifican permisos Foundation.
**Impacto:** un viewer puede crear workspaces, borrar KB, aprobar rutinas, etc.
**Archivos a modificar:** app/src/api.py (decoradores o dependencias), app/src/foundation/core.py (reusar require_permission).
**Nota:** segun el plan, la matriz de permisos se define en E2-2. Para E2-0 basta con que el backend resuelva el rol real y lo persista en actor_role_at_decision; el enforcement puede llegar en E2-2.

### 4.4 approved_by y actor_role_at_decision reales

**Descripcion:** en varios endpoints approved_by se pasa como query param (?approved_by=local) o queda None. actor_role_at_decision se deriva del claim JWT.
**Impacto:** la auditoria no refleja quien aprobo realmente ni con que rol.
**Archivos a modificar:** app/src/api.py (quitar approved_by query param, tomar de ctx), app/static/js/app.jsx (no enviar approved_by=local).

### 4.5 Migracion SQLite a Postgres - P0 para E2-1

**Descripcion:** no se encontraron scripts, SQL de esquema Postgres ni procedimiento de migracion.
**Impacto:** E2-1 no puede arrancar hasta tener esto.
**Archivos a crear:** scripts/migrate_sqlite_to_postgres.py (o similar), scripts/postgres_schema.sql, runbook de rollback/backup.

### 4.6 Tenant canario en app principal

**Descripcion:** Foundation tiene M16 y tests con tenant canary; la app principal no.
**Impacto:** no se puede probar que las queries de db.py filtran correctamente bajo presion de un segundo tenant.
**Archivos a modificar/crear:** seed canario en app/src/seed.py o test fixture, y un endpoint/test de verificacion tipo M16 para la app principal.

### 4.7 Higiene documental E1

Segun PLAN_TRABAJO_E2_FUGU_v3, E2-0 debe cerrar:
- Recuperar harness/prompts/sl1b_dogfood_prompts.json.
- Documentar promocion del spike a base E2.
- Lessons learned E1.
- Aplicar licencia FSL 1.1.
- Archivar SPINE Django como contrato de referencia.

**Estado:** no se encontro evidencia de estos entregables en el repo (los docs de plan existen, pero no el LICENSE ni el prompt file). Son tareas mecanicas que deben planificarse.

---

## 5. Riesgos y decisiones pendientes

| Riesgo | Prob. | Impacto | Mitigacion / decision necesaria |
|---|---:|---:|---|
| Auth hibrida con puentes legacy | Alta | P0 | Converger get_current_user con Foundation en E2-0; no dejarlo para E2-2. |
| tenant_id="default" hard-coded | Alta | P0 | Resolver tenant desde Foundation; sembrar canario. |
| SQLite sin RLS hasta E2-1 | Alta | Alto | Aceptado como transicion, pero el scoping app debe ser fail-closed y probado con canario. |
| Dos audit trails sin correlacion | Media | Alto | Documentar arquitectura; en E2-2 definir un evento/canonical ID compartido o unificar. |
| approved_by query-param | Media | P0 | Eliminar antes de E2-2; en E2-0 al menos persistir actor real. |
| Falta de tests E2-0 especificos | Media | Alto | Agregar tests de unificacion auth/context/audit. |
| Migracion Postgres no planificada | Media | Alto | Crear scripts y runbook antes de moverse a E2-1. |

### Decisiones a tomar antes del build de E2-0

1. **El API principal adopta require_session de Foundation o enriquece el JWT?**
   - Opcion A (recomendada): get_current_user consulta Foundation por email y enriquece request.state.user con tenant/rol reales. Minima intrusion, mantiene cookie HttpOnly.
   - Opcion B: todos los endpoints del API principal pasan a depender de require_session. Mas correcto pero rompe el shell actual si no se ajusta el frontend.
2. **Se mantiene FABERLOOM_AUTH_DISABLED en produccion?**
   - Recomendacion: solo en dev/test; documentar que en instancia compartida debe estar desactivado.
3. **Como se correlacionan audit_log y fnd_audit_log?**
   - Recomendacion E2-0: agregar correlation_id o foundation_session_id en ambos. No unificar tablas todavia.
4. **Cuando se sembrara el tenant canario?**
   - Recomendacion: en E2-0, como fixture de test y opcionalmente como seed de dev.

---

## 6. Archivos a modificar (orden de prioridad)

### Bloque 1 - Unificacion de identidad (antes de cualquier otro cambio funcional)

1. app/src/auth.py
   - create_access_token: aceptar tenant_id, user_id, role reales; no forzar DEFAULT_TENANT_ID.
   - get_current_user: si hay JWT valido, buscar usuario en Foundation y enriquecer claims.
2. app/src/api.py
   - context_from_request: confiar en claims enriquecidos; eliminar fallback dev-trust por defecto en produccion.
   - Quitar approved_by query param de endpoints de aprobacion; usar ctx.resolved_actor_id().
3. app/src/context.py (opcional)
   - Agregar validacion de que tenant_id no sea "default" en modo autenticado (assert de desarrollo).

### Bloque 2 - Audit y actor real

4. app/src/audit.py
   - Asegurar que actor_role_at_decision provenga del rol Foundation real.
5. app/static/js/app.jsx
   - No enviar approved_by=local.
   - Mostrar tenant/rol minimo en UI (opcional para E2-0, recomendado).

### Bloque 3 - Tests y canario

6. app/tests/test_e2_0_auth_context.py (nuevo)
   - JWT principal -> Context con tenant/rol Foundation.
   - Viewer no puede aprobar rutinas.
   - Audit log refleja actor/rol real.
7. app/tests/test_tenant_canary_app.py (nuevo)
   - Sembrar tenant canary en tablas app; verificar que queries solo devuelven filas del tenant de sesion.
8. app/src/seed.py (si aplica)
   - Opcion de sembrar datos canario en dev.

### Bloque 4 - Migracion Postgres

9. scripts/migrate_sqlite_to_postgres.py (nuevo)
10. scripts/postgres_schema.sql (nuevo)
11. Runbook de migracion/rollback en docs/ o Plan/.

### Bloque 5 - Higiene E1

12. harness/prompts/sl1b_dogfood_prompts.json (recuperar).
13. LICENSE (FSL 1.1).
14. Plan/DEC_FB_SPIKE_PROMOTION.md (nuevo).
15. Plan/SPEC_FB_SPIKE_E1_LESSONS_LEARNED.md (nuevo).
16. Archivar/tag SPINE Django.

---

## 7. Recomendaciones operativas

1. **No iniciar E2-1 hasta que el Bloque 1 (unificacion auth) este mergeado y tests verdes.** Migrar a Postgres con dos sistemas de auth es duplicar la deuda.
2. **Tratar E2-0 como un platform gate formal.** Ninguna feature de E2-2+ debe avanzar mientras el API principal no resuelva identidad desde Foundation.
3. **Mantener FABERLOOM_DEV_TRUST_HEADERS desactivado en produccion.** Es un bypass explicito que ya se documenta en test_tenant_contamination.py; su presencia en prod socavaria RLS.
4. **Correlacionar auditoria desde el primer dia.** Incluso si hay dos tablas, un correlation_id compartido permite reconstruir la narrativa de una accion.
5. **Sembrar canario antes de la migracion Postgres.** Asi la migracion se valida con datos de dos tenants.
6. **Documentar decisiones en Plan/ con versionado.** El repo ya tiene la convencion de v1, v2, etc.; mantenerla.

---

## 8. Checklist de salida E2-0

- [ ] get_current_user resuelve tenant/rol reales desde Foundation.
- [ ] context_from_request usa claims enriquecidos; no hard-codea DEFAULT_TENANT_ID.
- [ ] Audit log escribe actor_id, actor_role_at_decision, tenant_id, user_id reales.
- [ ] approved_by no se recibe como query param; se toma de ctx.
- [ ] Tests E2-0 de unificacion auth/context/audit pasan.
- [ ] Tenant canario sembrado en tablas app y tests de fuga verdes.
- [ ] Migracion SQLite a Postgres ensayada con conteos y rollback documentado.
- [ ] Higiene E1: sl1b_dogfood_prompts.json, LICENSE FSL 1.1, lessons learned, promocion del spike.
- [ ] Suite completa (pytest app/tests) verde.
