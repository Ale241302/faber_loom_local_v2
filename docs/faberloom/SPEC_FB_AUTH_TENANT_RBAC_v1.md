---
id: SPEC_FB_AUTH_TENANT_RBAC_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma
type: spec
stamp: VIGENTE 2026-05-02
fecha: 2026-05-02
agente: Cowork (redaccion) + CEO (decisiones) + ChatGPT (auditoria R5)
aplica_a: [FaberLoom]
implementa:
  - ENT_FB_USER_LEARNING_MODEL_v1 (rol AM)
  - ENT_FB_COMMITTEE_OPERATING_MODEL_v1 (rol CURATOR/COMMITTEE)
  - SPEC_FB_KNOWLEDGE_RIVER_v1.1 (3 universos rol Operacion/Gobernanza/Audit)
relacionado_con:
  - SPEC_FB_INTEGRATION_LAYER_v1 (auth + permission checks per endpoint)
  - SPEC_FB_FRONTEND_REALTIME_STATE_v1 (sesion frontend)
  - POL_FB_KR_PRIVACY_TIERS_v1.1 (auditor accede TIER 4 · AM nunca)
  - ENT_FB_BRAND_DUAL_NAMING_v1 (subdomain {tenant}.faberloom.com)
origen: ChatGPT R5 detecto que auth + tenant + RBAC NO debe enterrarse en Integration Layer · necesita SPEC propio
---

# SPEC_FB_AUTH_TENANT_RBAC_v1
## Autenticacion · multi-tenant routing · RBAC ejecutable

## 1. Proposito

Define identidad y autorizacion del sistema FaberLoom. Sin esto, "AM, comite, auditor y CEO no solo ven pantallas distintas; deben tener permisos distintos a nivel API, evento y query" (R5).

R5 critico: auth + tenant + RBAC son **piezas de primer orden** · NO detalle de Integration Layer. Si quedan enterrados, Sprint 1 implementa permisos parchados tarde.

## 2. Modelo de identidad

### 2.1 Entidades

```yaml
identity:
  user:
    user_id: uuid
    email: string  # unique global
    name: string
    locale: string  # ej. es-MX
    created_at: ISO8601
    last_login_at: ISO8601?
    
  tenant:
    tenant_id: string  # ej. mwt · slug-format
    legal_name: string  # ej. Muito Work Limitada
    commercial_name: string  # ej. Mesa de Control
    vertical_spec_object_id: string  # ej. safety_footwear
    subdomain: string  # ej. mwt (resuelve mwt.faberloom.com)
    plan_tier: enum  # bronze · silver · gold · platinum · custom
    created_at: ISO8601
    
  membership:
    user_id: uuid
    tenant_id: string
    roles: array<role>  # un usuario puede tener multiples roles en mismo tenant
    active: boolean
    granted_by: uuid  # user que asigno
    granted_at: ISO8601
    revoked_at: ISO8601?
```

### 2.2 4 roles canonicos

| Rol | Capa | Que hace |
|---|---|---|
| `AM` | Operacion (Capa 1) | Operador diario · gestiona sus agentes · curaduria personal · soberano sobre sus L2 |
| `CURATOR` | Gobernanza (Capa 2) | Comite organizacional · revisa patterns cross-AM · promote L2→L3 · 7 checks privacy |
| `AUDITOR` | Audit | Read-only sobre audit log · puede objetar · NO modifica · acceso TIER 4 con MFA |
| `CEO` | Estrategia | Decisiones excepcionales · escalation final · firma contratos · acceso global tenant |

**Multi-rol por persona** (MWT v1 con CEO Alvaro):
- Mismo `user_id` puede tener `roles: [AM, CURATOR, CEO]` en tenant `mwt`
- Cada accion registra `actor_role_at_decision` (de indexa-g) · NO solo `user_id`

## 3. Multi-tenant subdomain routing

### 3.1 Resolucion

```
1. Usuario navega a https://mwt.faberloom.com
2. Reverse proxy (Caddy/Traefik) resuelve subdomain "mwt"
3. Backend recibe header X-Forwarded-Host = mwt.faberloom.com
4. Middleware extrae tenant_slug = "mwt"
5. Lookup tenant_id en cache · si miss → query postgres
6. Inyecta tenant_id al request context (header x-tenant-id obligatorio)
7. Cualquier query DB filtra por tenant_id automaticamente (row-level security)
```

### 3.2 Tenant isolation

- **Postgres row-level security (RLS)** habilitado en TODAS las tablas con tenant_id
- Cada conexion al Postgres setea `SET app.current_tenant = 'mwt'` al inicio de transaccion
- Cualquier query sin filtro tenant_id → bloqueada automaticamente
- Sin RLS · imposible garantizar separacion · violacion P3 + privacy tiers

### 3.3 Cross-tenant access (excepcional)

Solo permitido para:
- Usuarios FaberLoom-side (admin de la plataforma · NO clientes tenant)
- Patterns L3 GLOBAL_PROMOTABLE en queries explicit cross-tenant (con 7 checks · `POL_FB_KR_PRIVACY_TIERS_v1.1`)
- Audit FB-side · acceso temporal con MFA + razon documentada

## 4. Auth · sesion · login flow

### 4.1 Auth method canonico v1 (R5)

**App-native FastAPI** · NO Auth0 · NO Keycloak · NO Authentik en Sprint 1.

Razones R5:
- Mas defendible para etapa actual (control + bajo costo)
- Tenant + RBAC se pueden mantener juntos en aplicacion
- Authentik/Keycloak introducen complejidad operativa
- SaaS (Clerk/Auth0) son comodos pero ceden control de RBAC y se acoplan

### 4.2 Login flow

```
1. POST /api/v1/auth/login
   body: {email, password}
   
2. Backend valida:
   - email existe + password matchea (bcrypt cost=12)
   - cuenta no suspendida
   - intento N° dentro rate limit (5 intentos/15min · luego lockout 1h)
   
3. Si OK:
   - Crear session_id (random 256 bits)
   - Persistir en Redis con TTL 7d
   - Setear cookie httpOnly · secure · SameSite=Strict
   - Cookie name: faberloom_session
   - Domain: .faberloom.com (cross-subdomain por tenant)
   
4. Response:
   - 200 + body {user_id, available_tenants, requires_2fa}
   - Si requires_2fa = true → next request a /auth/2fa/verify
```

### 4.3 Session refresh

- Sliding expiration · cada request valida session-id contra Redis y refresh TTL
- Background job invalida sessions con last_activity > 7d
- Logout: DELETE /api/v1/auth/logout · invalida session-id de Redis

### 4.4 2FA (obligatorio para CEO + CURATOR · opcional AM)

- TOTP (Google Authenticator-compatible) · setup en /api/v1/auth/2fa/setup
- Backup codes 10 single-use · descargables al setup
- Recovery via email + admin manual confirmation
- Auditor con TIER 4 access requiere 2FA EN CADA ACCESO (no solo login) · re-auth STEP-UP

## 5. RBAC matrix ejecutable (R5 critical)

R5 explicit: "Tabla endpoint × rol × tenant × recurso" debe ser ejecutable · no conceptual.

### 5.1 Estructura de permisos

```yaml
permission:
  resource: string  # ej. drafts · pool_l3 · audit_log · agents · pricing · etc
  action: enum  # read · create · update · delete · approve · promote · reject · execute
  scope: enum  # own (mi data) · tenant (todo tenant) · global (cross-tenant FB-admin)
  
permission_grant:
  role: enum  # AM · CURATOR · AUDITOR · CEO
  permission_id: uuid  # ref a permission
  tenant_scope: string?  # null = aplica a todos los tenants del usuario · sino especifico
  conditions: array<condition>?  # ej. amount<10000 · tier=gold · etc
```

### 5.2 Matriz canonica per recurso (extracto)

| Recurso × Accion | AM | CURATOR | AUDITOR | CEO |
|---|---|---|---|---|
| `feed.read` (own) | ✓ | ✓ | ✓ (read-only · audit purpose) | ✓ |
| `feed.read` (tenant) | ✗ | ✗ | ✓ | ✓ |
| `dispatch.create` (assign agent) | ✓ (own) | ✗ | ✗ | ✓ |
| `draft.read` (own) | ✓ | ✗ | ✓ | ✓ |
| `draft.approve` (HITL P3) | ✓ (own) | ✗ | ✗ | ✓ (override · raro) |
| `draft.edit` (own) | ✓ | ✗ | ✗ | ✓ |
| `draft.reject` (con razon) | ✓ | ✗ | ✗ | ✓ |
| `agent.iterate` (entrar a agent) | ✓ (own) | ✗ | ✓ (read-only) | ✓ |
| `agent.config.read` | ✓ (own) | ✗ | ✓ | ✓ |
| `agent.config.update` | ✓ (own · subset) | ✗ | ✗ | ✓ |
| `pattern.candidate.read` (own) | ✓ | ✗ | ✗ | ✓ |
| `pattern.candidate.apply_personal` | ✓ (own L2) | ✗ | ✗ | ✓ |
| `pattern.l2.promote_to_l3` | ✗ | ✓ (con 7 checks) | ✗ | ✓ |
| `pattern.l3.read` | ✗ | ✓ | ✓ | ✓ |
| `pattern.l3.demote_archive` | ✗ | ✓ | ✗ | ✓ |
| `replay_set.read` | ✗ | ✓ | ✓ | ✓ |
| `replay_set.candidate.promote_active` | ✓ (own) | ✗ | ✗ | ✓ |
| `replay_set.cross_am.promote_l3` | ✗ | ✓ | ✗ | ✓ |
| `audit_log.read` (tenant scope) | ✗ | ✓ (limited) | ✓ (full) | ✓ |
| `audit_log.read` (TIER 4 RESTRICTED) | ✗ | ✗ | ✓ (con MFA + razon) | ✓ |
| `freeze.execute` (mensual pack) | ✗ | ✓ | ✗ | ✓ |
| `pricing.execute_trade` | ✗ | ✗ | ✗ | ✗ (NUNCA · prohibition list R5) |
| `tenant.config.update` | ✗ | ✗ | ✗ | ✓ |
| `users.invite_to_tenant` | ✗ | ✗ | ✗ | ✓ |
| `tenant.subdomain.update` | ✗ | ✗ | ✗ | ✓ (con FB-admin coord) |

(Matriz completa en YAML reference · `docs/anexos/rbac_matrix_v1.yaml` cuando se implemente.)

### 5.3 Permission check middleware

```python
@router.post("/api/v1/drafts/{draft_id}/approve")
async def approve_draft(
    draft_id: UUID,
    user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    # 1. Verificar permission ejecutable
    if not has_permission(
        user=user,
        tenant=tenant,
        resource="draft",
        action="approve",
        scope="own",
        target_id=draft_id,
    ):
        raise HTTPException(403, "permission_denied")
    
    # 2. Registrar actor_role_at_decision
    audit_log.record(
        user_id=user.id,
        tenant_id=tenant.id,
        actor_role_at_decision=detect_active_role(user, action="draft.approve"),
        action="draft.approve",
        target_id=draft_id,
        ...
    )
    
    # 3. Ejecutar accion
    return await draft_service.approve(draft_id)
```

## 6. Headers obligatorios desde dia 1 (R5 bonus 5%/50%)

R5 explicit: "agregar desde el día 1 un header obligatorio en toda request, evento y log".

Cada request al backend debe llevar:

```
x-trace-id        ← UUID por request original (creado en frontend o reverse-proxy)
x-tenant-id       ← extraido de subdomain · auto por middleware
x-actor-id        ← user_id de session · auto por middleware
x-actor-role      ← rol activo en este request (AM/CURATOR/AUDITOR/CEO) · explicit del frontend si multi-rol
x-agent-id        ← si es invocacion a agente · cual · auto si call sub-agent
x-command-id      ← UUID del comando logico · creado en frontend al iniciar
x-idempotency-key ← obligatorio en mutaciones POST/PATCH/DELETE · UUID generado frontend
x-api-version     ← v1 default · explicit si cliente quiere otra version
```

Sin headers obligatorios · request rechazada con 400 + body indicando cuales faltan.

## 7. Rate limiting per tenant + per usuario

| Limite | Default | Configurable per tenant tier |
|---|---|---|
| Requests/min per usuario | 60 | hasta 300 (platinum) |
| Requests/min per tenant agregado | 600 | hasta 3000 (platinum) |
| LLM calls/min per usuario (cost-sensitive) | 10 | hasta 50 (platinum) |
| Login attempts/15min | 5 | fixed (security) |
| 2FA verify attempts/15min | 10 | fixed |

Implementacion: Redis con sliding window (no fixed window).

## 8. Audit obligatorio

Cada accion sensible emite audit event:

```yaml
event: auth_action | permission_check | role_assumed | tenant_switched | login | logout
event_id: uuid
trace_id: uuid (cadena)
user_id: uuid
tenant_id: string
actor_role_at_decision: enum
permission_resource: string
permission_action: string
permission_granted: boolean
target_id: uuid?
ip_address: string
user_agent: string
mfa_used: boolean
timestamp: ISO8601
sha_chain_prev: string
sha_chain_curr: string
```

Audit trail con SHA-chain · ruptura de chain = alerta critica.

## 9. Cross-rol guarding (multi-hat MWT v1)

Cuando CEO Alvaro tiene `roles: [AM, CURATOR, CEO]` en mwt:
- Frontend muestra selector de hat activo (defaults al rol mas restrictivo · AM)
- Cada accion lleva `x-actor-role` explicit al backend
- Backend valida que el rol declarado tiene permission · NO el rol mas alto del usuario
- Cambios de hat se logean (event `role_assumed`)

Esto permite operar como AM normalmente · y solo elevar a CURATOR cuando hay reunion semanal · sin contaminar logs.

## 10. Reglas inquebrantables

1. **Subdomain por tenant obligatorio.** Sin subdomain · no hay tenant · request rechazada.
2. **Postgres RLS habilitado en TODAS las tablas con tenant_id.** Sin RLS · request rechazada en boot.
3. **Permission check por endpoint · sin excepcion.** Endpoint sin check = bug critico.
4. **Headers obligatorios x-* en TODA request.** Faltan = 400.
5. **2FA obligatorio CEO + CURATOR · STEP-UP para AUDITOR TIER 4.**
6. **Cross-tenant access requiere 7 checks privacy** (POL_FB_KR_PRIVACY_TIERS_v1.1).
7. **`pricing.execute_trade` NUNCA · ningun rol** (prohibition list R5).
8. **Multi-rol persona explicit hat declarado** · NO inferir rol mas alto auto.
9. **Audit log con SHA-chain · ruptura = alerta critica.**

## 11. Pendientes [PENDIENTE — NO INVENTAR]

- Email provider para verification + invites (SendGrid? AWS SES?) → diferido SPEC implementacion
- Password recovery flow detallado → diferido
- Session storage scaling (Redis cluster?) → diferido v2
- Tenant onboarding flow UI → SPEC_FB_TENANT_BOOTSTRAP_SEED_v1 (indexa-i)
- SSO/OIDC para tenants enterprise (post-Sprint 1)
- Audit dashboard UI (rol Auditor) → diferido v6/v7

## NO IMPLICA (R4 bonus 5%/50%)

`SPEC_FB_AUTH_TENANT_RBAC_v1` **NO implica IdP externo en Sprint 1**. Implementacion app-native FastAPI con sesiones httpOnly + Redis. Migracion a Keycloak/Auth0 queda como evolucion v2 cuando volumen multi-tenant lo justifique. Auth provider es decision tactica · NO core.

## Changelog
- 2026-05-02 v1.0 VIGENTE: Creacion inicial post R5 ChatGPT. 4 roles canonicos (AM/CURATOR/AUDITOR/CEO) + multi-rol persona con `actor_role_at_decision` registrado. Subdomain routing canonico mwt.faberloom.com con Postgres RLS obligatorio. Auth app-native FastAPI v1 (NO Keycloak/Auth0/Authentik). 2FA obligatorio CEO+CURATOR · STEP-UP AUDITOR TIER 4. RBAC matrix ejecutable con 25+ recursos×acciones canonicos. Headers obligatorios x-* desde dia 1 (8 canonicos). Rate limiting per usuario + per tenant. Audit con SHA-chain. Cross-rol guarding explicit hat declarado. 9 reglas inquebrantables. NO implica IdP externo Sprint 1.

## Stamp
VIGENTE 2026-05-02 — Auth + Tenant + RBAC como SPEC propio (no enterrado en Integration Layer · R5 critical). Define identidad/autorizacion del sistema antes de Integration Layer · que solo aplica permission checks declarados aqui. Sin esto · Sprint 1 implementa permisos parchados tarde.
