# Camino B: Foundation Beta v1.3.1 — Plan de Implementación

## 1. Resumen ejecutivo

Este documento es el plan maestro para ejecutar el **Camino B: Foundation Beta v1.3.1**, el track canónico de FaberLoom.  El spike SpaceLoom E1 queda congelado como dogfood interno/no canónico según `DEC-011`.  Este plan describe la transición desde el estado actual del spike (FastAPI + SQLite/sqlcipher + JWT simple + feature flags) hacia el stack objetivo de Foundation Beta:

- **Backend:** Django 4.2 LTS + Django REST Framework (DRF)
- **Base de datos:** PostgreSQL 16 + extensión pgvector + RLS
- **Caché / sesiones / streams:** Redis 7
- **Object storage:** MinIO
- **Routing LLM:** LiteLLM Proxy (Anthropic-only con DPA)
- **Memoria:** Letta self-hosted
- **Frontend web:** Next.js
- **Frontend desktop:** Electron + React
- **Deploy:** Docker Compose en Hostinger KVM 8

El trabajo se organiza en un **SPINE serial** de siete módulos funcionales cuyos contratos deben quedar congelados antes de abrir tracks paralelos:

```text
M16 Tenant Isolation ✅
  → M08 Auth Session ✅
      → M09 RBAC ✅
  → M15 Outbox Streams ✅
  → M12 Audit Trail ✅
      → M11 D9 Policy Gate ✅
      → M07 Bootstrap Wizard ✅
```

## 2. Stack objetivo

| Capa | Tecnología | Versión/Notas |
|---|---|---|
| Aplicación web | Next.js 14+ (App Router) | SSR, server actions donde aplique |
| API | Django 4.2 + DRF | Command-heavy, no CRUD-first |
| Base de datos | PostgreSQL 16 | `pgvector`, `FORCE ROW LEVEL SECURITY` |
| Caché / Sesiones / Streams | Redis 7 | Streams para eventos, Hash para sesiones |
| Workers | Celery 5 + Redis broker | `with_tenant_session` wrapper obligatorio |
| Object storage | MinIO | Paths `/tenants/{tenant_id}/...` |
| LLM routing | LiteLLM Proxy | Anthropic-only en E1; logs taggeados por tenant |
| Memoria | Letta self-hosted | Namespaces por tenant/agente/tarea |
| Container runtime | Docker Compose | Hostinger KVM 8, 6+ contenedores |
| Auth | Django sessions + TOTP | Cookies httpOnly/Secure/SameSite=Strict |

## 3. Orden de ejecución

| Orden | Módulo | Sprint objetivo | Bloquea a |
|---:|---|---|---|
| 1 | M16 Tenant Isolation ✅ | S1A | Todos los tracks |
| 2 | M08 Auth Session ✅ | S1A | M09, M18, M07 |
| 3 | M09 RBAC ✅ | S1A | M07, M13, M12 (permisos) |
| 4 | M15 Outbox Streams ✅ | S1B | M13, M19, consumidores |
| 5 | M12 Audit Trail ✅ | S1B | M11, M13, M14, M17 |
| 6 | M11 D9 Policy Gate ✅ | S1B | Ejecución M10, M13 outbound, M07 activation |
| 7 | M07 Bootstrap Wizard ✅ | S10 | Go-live del tenant beta |

> **Regla de oro:** ningún track operativo arranca hasta que M16 pase sus 5 tests cross-tenant.

## 4. Dependencias cruzadas

```text
M16 ──┬── M08 ──┬── M09 ──┬── M07
      │         │         └── M13 (aprobaciones)
      │         │
      │         └── M12 (actor_role_at_decision)
      │
      ├── M15 ──┬── M19 (offline sync)
      │         └── M13 (consumidor de eventos)
      │
      ├── M12 ──┬── M11
      │         ├── M13
      │         ├── M14
      │         └── M17
      │
      └── M11 ──┬── M10 (ejecución)
                └── M13 (egress)
```

## 5. Principios rector

1. **Contract-first:** cada módulo expone inputs, outputs, eventos y schemas versionados.
2. **Fail-closed:** cualquier duda en aislamiento, auth, permisos o política bloquea.
3. **No mergear spike:** el código SpaceLoom se conserva congelado; Foundation Beta se construye como código nuevo.
4. **Kill criteria E1:**
   - `>=1` incidente privacy cross-tenant confirmado → kill/replan.
   - N3/N4 sale a provider sin DPA → kill/replan.
   - D9 cae abierto → kill/replan.
   - Tests cross-tenant M16 fallan en `main` → no abrir tracks.

## 6. Checklist consolidado

### M16 Tenant Isolation ✅ SPINE gate verde
- [x] Esquema Postgres con `tenant_id NOT NULL` en tablas aislables
- [x] RLS `FORCE` + policies `USING (tenant_id = current_setting('app.tenant_id')::uuid)`
- [x] Middleware Django setea `app.tenant_id` en cada request
- [x] Redis keys con prefijo `tenant:{tenant_id}:`
- [x] Celery `TenantTask` + `RESET app.tenant_id` + assert
- [x] MinIO paths `/tenants/{tenant_id}/...` con anti path-traversal
- [ ] pgvector partición por tenant para N2+ (helper listo; partición E2+)
- [x] LiteLLM Proxy recibe `tenant_id` en metadata
- [x] Letta namespace por tenant
- [x] Tests cross-tenant pasan en VPS (`pytest -q --create-db` → 12 passed)

### M08 Auth Session ✅ SPINE gate verde
- [x] Modelo `User` con hash argon2id
- [x] Modelo `Session` server-side en Redis
- [x] 2FA TOTP obligatorio para Owner (fallback directo si no enrolado)
- [x] Login flow: credenciales → TOTP → sesión Redis → cookie httpOnly
- [x] `/auth/me` para reanudación
- [x] Revocación remota de sesiones (owner/admin) y logout-all
- [ ] Electron partition por tenant + keytar para secrets (frontend desktop E2+)

### M09 RBAC ✅ SPINE gate verde
- [x] Tabla `Role` con 5 roles canónicos seedeados
- [x] Tabla `Membership` (user_id, tenant_id, roles[], status, active_hat)
- [x] Permission resolver server-side (`HasPermission`, `require_permission`)
- [ ] UI muestra/oculta según rol (frontend web E2+)
- [x] Selector de "hat" vía header `X-Active-Hat` validado
- [x] Eventos outbox: `user.invited`, `user.role_changed`, `user.revoked`, `permission.denied`

### M15 Outbox Streams ✅ SPINE gate verde
- [x] Tablas `outbox` y `event_log` + secuencia global
- [x] Event envelope canónico (`event_id`, `tenant_id`, `type`, `payload`, `seq_no`, `timestamp`)
- [x] `EventWriter.emit()` transaccional
- [x] Relay Celery drena outbox → Redis Stream `tenant:{id}:events`
- [x] WebSocket fanout por tenant (`ws/events/`) + polling fallback (`/api/events`)
- [x] Reconexión con `?since=<seq>` + `sync_required` si gap
- [x] Dedupe por `event_id` y purga de publicados

### M12 Audit Trail ✅ SPINE gate verde
- [x] Tabla `audit_log` con 18 campos canónicos
- [x] Hash chain por `chain_id = tenant_id:default`
- [x] Append-only: triggers NO UPDATE/DELETE + app role sin UPDATE/DELETE (no-op para el owner de la tabla en tests)
- [x] `AuditWriter.write()` transaccional con RLS y emisión de `audit.entry.created`
- [x] Integración en login/logout y RBAC (invite/role_change/revoke)
- [x] Endpoints `/api/audit`, `/api/audit/export`, `/api/audit/validate` con permisos RBAC
- [x] Job diario `validate_audit_chains` detecta rupturas y alerta P0
- [x] Export per-tenant JSON/CSV con validation report
- [x] Tests M12 pasan en VPS (`pytest -q --create-db` → 11 passed)

### M11 D9 Policy Gate ✅ SPINE gate verde
- [x] `ActionContext` + `PolicyDecision`
- [x] Modelos `DpaStatement`, `DataClassificationDefault`, `PolicyBlock` con RLS
- [x] Ceiling por plan/tenant (`TenantPlanFeatures.data_class_ceiling`)
- [x] DPA state por tenant; firma solo Owner
- [x] Gate pre-skill (`evaluate`) + pre-egress (`pre_egress`) con heurística de PII
- [x] `effective_classification = max(declared, source_default, retrieved_chunks, pre_egress_detected)`
- [x] Respuesta `PlanUpgradeRequired` canonizada; fail-closed
- [x] Endpoints `/api/policy/dpa`, `/api/policy/dpa/sign`, `/api/policy/evaluate`, `/api/policy/blocks`
- [x] Eventos `policy.gate.passed`, `policy.gate.blocked`, `policy.classification_mismatch`
- [x] Audit entry por cada decisión (M12)
- [x] Tests M11 pasan en VPS (`pytest -q --create-db` → 9 passed)

### M07 Bootstrap Wizard ✅ SPINE gate verde
- [x] Tenant creado en estado `setup` por platform admin (endpoint existente `POST /api/tenants`)
- [x] Wizard backend con pasos: datos, Owner+2FA, mailbox, KB seed, Voice Profile, DPA, seed agents, sandbox, go-live
- [x] Modelos `TenantBootstrapProgress`, `EmailBinding`, `VoiceProfile`, `SystemAgent` con RLS
- [x] Seed de agentes system (`@router`, `@cotizador`) en estado `shadow`
- [x] Invitación Owner vía `/api/tenants/{id}/invite-owner` (TTL 7 días)
- [x] Firma DPA in-wizard (paso `dpa_signed`)
- [x] Sandbox test obligatorio con D9 gate + draft interno sin egress
- [x] Activación `/api/tenants/{id}/activate` fail-closed: requiere todos los pasos + DPA + sandbox OK
- [x] Eventos `tenant.activated`, `user.invited`, `user.2fa_enabled`, `mailbox.connected`, `document.uploaded`
- [x] Audit M12 en cada paso y activación
- [x] Tests M07 pasan en VPS (`pytest -q --create-db` → 8 passed)

## 7. Riesgos P0 transversales

1. **Cross-tenant leak por Celery stale tenant_id.** Mitigación: wrapper + `DISCARD ALL` + tests A→B.
2. **LLM egress bypass D9.** Mitigación: LiteLLM Proxy como único egress; CI bloquea SDK directos.
3. **pgvector global HNSW para N2+.** Mitigación: partición por tenant; test `EXPLAIN`.
4. **Audit mutable.** Mitigación: triggers + app role sin UPDATE/DELETE.
5. **Electron token leak.** Mitigación: httpOnly cookies + keytar + `contextIsolation`.

## 8. Decisiones de arquitectura tomadas

| Tema | Decisión | Rationale |
|---|---|---|
| Framework | Django 4.2 + DRF | `DEC-001`, command-heavy, maduro para multi-tenant |
| Migración desde spike | No mergear código SQLite | `DEC-011` spike congelado/no canónico |
| Roles E1 | Schema 5 roles, UI Owner/Operator | Enmienda E-4; Admin/Supervisor/Viewer E3+ |
| DPA | Firma in-wizard (checkbox + timestamp) | Desbloquea go-live sin esperar e-sign externo; auditable |
| TTL sesión | 8h / remember 30 días | Jornada laboral + UX desktop |
| Hash password | argon2id (Django default) | Estándar, verificado por spec M08 |
| Lockout 2FA | 3 fallos → 15 min cooldown | Balance seguridad/UX |
| Audit schema | 18 campos de SPEC M12 | Es el superset; cubre evidence bundle |
| Eventos E1 | Subset de 6 eventos | M15 especifica scope E1 |
| pgvector | Partición por tenant para todo N2+ | Simplifica operación y cumple M16 |
| Outbox retención | 7 días publicados / stream 24h | Recuperación sin acumulación infinita |
| App DB role | No superuser, `CREATEDB` solo en tests | Superusers bypass RLS; el dueño de la tabla debe estar sujeto a `FORCE RLS` |

## 9. Archivos generados

- `Plan/CaminoB_FoundationBeta/README.md` (este archivo)
- `Plan/CaminoB_FoundationBeta/M16_TENANT_ISOLATION_PLAN.md`
- `Plan/CaminoB_FoundationBeta/M08_AUTH_SESSION_PLAN.md`
- `Plan/CaminoB_FoundationBeta/M09_RBAC_PLAN.md`
- `Plan/CaminoB_FoundationBeta/M15_OUTBOX_STREAMS_PLAN.md`
- `Plan/CaminoB_FoundationBeta/M12_AUDIT_TRAIL_PLAN.md`
- `Plan/CaminoB_FoundationBeta/M11_D9_POLICY_GATE_PLAN.md`
- `Plan/CaminoB_FoundationBeta/M07_BOOTSTRAP_WIZARD_PLAN.md`

---
*Generado por Fugu (arquitecto senior) — 2026-07-01.  Estado: plan de implementación, sin código.*
