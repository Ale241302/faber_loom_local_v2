# M07 Bootstrap Wizard — Plan de Implementación

## 1. Resumen ejecutivo

M07 activa un tenant productivo con los datos mínimos para recibir, clasificar y cotizar un RFQ en SANDBOX, aplicando guardrails de seguridad antes de que entre dato real.  Es el último módulo del SPINE.

**Rol en el SPINE:** consume M08 (auth + 2FA), M09 (roles), M11 (DPA + data ceiling), M12 (audit), M15 (eventos) y M16 (tenant context).  Entrega un tenant `active` con Owner/Operator, mailbox conectado, KB seed, Voice Profile y agentes system en `shadow`.

## 2. Entrada/salida

### Entrada
- Invitación de platform admin.
- Datos del tenant, Owner, mailbox, canales, KB, Voice Profile.
- Estados de M08/M09/M11/M12/M16.

### Salida
- Tenant en estado `active`.
- Memberships Owner/Operator.
- Seed de agentes system (`@router`, `@cotizador`) en estado `shadow`.
- Mailbox conectado.
- Eventos: `tenant.created`, `user.invited`, `user.2fa_enabled`, `mailbox.connected`, `document.uploaded`, `tenant.activated`.

## 3. Modelo de datos

### Tablas existentes
- `tenants` (creada en M16).
- `tenant_plan_features` (M16).
- `users`, `memberships` (M08/M09).
- `dpa_statements` (M11).

### Tablas nuevas

```sql
CREATE TABLE tenant_bootstrap_progress (
    tenant_id UUID PRIMARY KEY REFERENCES tenants(id) ON DELETE CASCADE,
    steps_completed TEXT[] NOT NULL DEFAULT '{}',
    steps_blocked TEXT[] NOT NULL DEFAULT '{}',
    sandbox_result JSONB,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE email_bindings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    provider TEXT NOT NULL CHECK (provider IN ('gmail_oauth','imap_smtp')),
    account TEXT NOT NULL,
    credentials_encrypted TEXT NOT NULL,
    is_default BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE voice_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    persona TEXT NOT NULL,
    tone TEXT NOT NULL,
    glossary TEXT[] NOT NULL DEFAULT '{}',
    greeting TEXT,
    signature TEXT,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE system_agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    origin TEXT NOT NULL DEFAULT 'system',
    skill_md TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'shadow' CHECK (status IN ('shadow','active')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## 4. Cambios en API/backend

### Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/tenants` | Platform admin crea tenant en `setup` |
| POST | `/api/tenants/{id}/invite-owner` | Envía invitación al primer Owner |
| POST | `/api/tenants/{id}/steps/{step}` | Guarda progreso de un paso |
| POST | `/api/tenants/{id}/activate` | Go-live si pasos mínimos + sandbox OK + DPA |
| GET  | `/api/tenants/{id}/bootstrap` | Estado del wizard |
| POST | `/api/tenants/{id}/sandbox` | Ejecuta sandbox test |

### Pasos del wizard

1. **Tenant data:** `legal_name`, `commercial_name`, `slug`, `language`, `vertical_spec_object_id`.
2. **Owner + 2FA:** crear user, membership Owner, enrolar TOTP, generar backup codes.
3. **Mailbox:** Gmail OAuth o IMAP/SMTP custom; cifrar credenciales.
4. **Canales WhatsApp:** paso visible pero deshabilitado (E-5: E3+).
5. **KB upload:** 5-10 documentos; parse preview; afirmaciones HIGH/LOW; reindex.
6. **Voice Profile:** persona + tono + glosario + saludo + firma del primer Operator.
7. **DPA:** Owner firma in-wizard.
8. **Seed agents:** `@router`, `@cotizador` en `shadow`.
9. **Sandbox test:** enviar/recibir RFQ de prueba; verificar L1 + draft + aprobación.
10. **Go-live:** tenant `active`.

### Reglas de activación

```python
def can_activate(tenant_id) -> bool:
    progress = get_progress(tenant_id)
    required = {'tenant_data', 'owner_2fa', 'mailbox', 'kb_seed', 'voice_profile', 'dpa_signed', 'seed_agents', 'sandbox_ok'}
    return required.issubset(set(progress.steps_completed))
```

### Sandbox test

- Crear RFQ de prueba.
- L1 classifier (M10 stub) produce ActionContext.
- D9 gate (M11) verifica que no haya bloqueo para N0-N2.
- Generar draft (M13 stub) en Zona 3.
- Owner aprueba/rechaza sin envío externo.

### Seed agents

- `@router`: clasifica inbound y enruta.
- `@cotizador`: genera cotización/draft.
- Status `shadow`: no pueden ejecutar en producción hasta promoción con evidencia.

## 5. Cambios en frontend

### Web (Next.js)
- Wizard 10 pasos con progress bar.
- Validación inline: slug disponible, OAuth success, 2FA QR, parse preview.
- Banner bloqueante si falta DPA.
- Pantalla sandbox test result.
- Badge verde "tenant active".

### Desktop
- Ninguno; el bootstrap es web-only.

## 6. Cambios en infraestructura/deploy

- Variables de entorno:
  ```bash
  INVITATION_TTL_DAYS=7
  SANDBOX_RFQ_SUBJECT="RFQ de prueba FaberLoom"
  GOOGLE_OAUTH_CLIENT_ID=
  GOOGLE_OAUTH_CLIENT_SECRET=
  ```
- Integración OAuth con Google para Gmail.
- Seed de documentos golden en `foundation/seeds/`.

## 7. Secuencia de tareas

1. Crear app Django `bootstrap`.
2. Modelos `TenantBootstrapProgress`, `EmailBinding`, `VoiceProfile`, `SystemAgent`.
3. Endpoint platform admin para crear tenant.
4. Envío de invitación Owner.
5. Endpoint de aceptación de invitación (redirige a wizard).
6. Paso 1: datos del tenant.
7. Paso 2: Owner + 2FA (integra M08).
8. Paso 3: mailbox OAuth/IMAP.
9. Paso 4: canales WhatsApp diferido.
10. Paso 5: KB upload + parse preview.
11. Paso 6: Voice Profile.
12. Paso 7: firma DPA (integra M11).
13. Paso 8: seed agents system en `shadow`.
14. Paso 9: sandbox test.
15. Paso 10: activación.
16. Invitar Operator (M09).
17. Emitir eventos a M15.
18. Audit en M12.
19. Tests end-to-end de activación.
20. UI wizard.

## 8. Criterios de aceptación

1. `test_bootstrap_creates_owner_operator_only_in_e1`: solo roles Owner/Operator activos.
2. `test_bootstrap_blocks_activation_when_dpa_required_missing`: activación falla sin DPA.
3. `test_seed_skills_are_shadow_and_cannot_external_send`: agentes system en shadow no envían nada externo.
4. Sandbox test genera draft y permite aprobación sin salida externa.
5. Tenant `active` solo después de pasos mínimos + DPA + sandbox OK.
6. Wizard persiste progreso por paso; reanuda en paso incompleto.
7. Invitación expira en 7 días.

## 9. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Activación sin DPA | P0 fuga N3/N4 | Gate M11 + check explícito en `can_activate` |
| Sandbox no representativo | P1 falla en producción | RFQ golden pre-curados por CEO |
| OAuth Gmail falla | P2 onboarding bloqueado | Fallback IMAP/SMTP custom |
| Seed agents en active | P1 envío no controlado | Estado `shadow` + enforcement en runtime |
| Operator invitado antes de activación | P1 UX | Invitación Operator se envía post go-live |

## 10. Decisiones de arquitectura tomadas

1. **DPA in-wizard.**  Checkbox + timestamp + audit; no se espera e-sign externo.
2. **WhatsApp diferido a E3.**  Paso visible pero no bloqueante; email-only en E1.
3. **Seed agents system en `shadow`.**  No ejecutan en producción hasta evidencia de gold.
4. **Sandbox test obligatorio.**  Verifica L1, draft y HITL antes de go-live.
5. **Invitación platform admin en E1.**  No hay self-service signup público.
6. **Progreso por paso en JSONB.**  Flexible para añadir/quitar pasos sin migraciones.

---
*Plan M07 — Foundation Beta v1.3.1*
