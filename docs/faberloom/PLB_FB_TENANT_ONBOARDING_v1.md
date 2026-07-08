# PLB_FB_TENANT_ONBOARDING_v1 — Playbook de onboarding de tenant externo

id: PLB_FB_TENANT_ONBOARDING_v1
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: PLB
stamp: DRAFT -- 2026-07-08 -- procedimiento operativo para E3-6 primer tenant externo
aprobador: CEO / COO
aplica_a: [FaberLoom]
relacionado:
  - PLAN_DESARROLLO_FABERLOOM_ETAPA3_v1.md (E3-6)
  - SPEC_FB_TENANT_BOOTSTRAP_SEED_v1.md
  - ENT_FB_PRICING_TIERS_v1.md
  - SPEC_FB_ROUTING_PRESETS_v1.md
  - ENT_FB_SKILL_CATALOG_v1.md (PACK 1 fiscalidad electrónica, PACK 3 cobranza)
  - SCH_FB_SKILL_MANIFEST_v2.md
  - ARCH_FB_AGENT_RUNTIME_EVAL_v1.md

---

## 1. Objetivo

Este playbook documenta el procedimiento operativo para incorporar el **primer tenant externo** a FaberLoom en Etapa 3. Es un onboarding asistido, no self-service: cada paso requiere decisión humana, configuración del equipo FaberLoom y trazabilidad en audit.

> Alcance: un único design partner B2B que cumple los criterios de elegibilidad de `PLAN_DESARROLLO_FABERLOOM_ETAPA3_v1.md` Sección E3-6 t.1.

---

## 2. Criterios de elegibilidad del design partner

El candidato debe cumplir **todos** los siguientes filtros antes de aprobación comercial:

1. Relación comercial viva con MWT (distribuidor/cliente B2B activo).
2. Opera correo + cotización + facturación electrónica como parte de su flujo normal.
3. Menos de 10 usuarios finales previstos en el workspace.
4. Acepta plan **BETA gratis 90 días** con feedback quincenal.
5. Firma acuerdo de datos: sus datos jamás entrenan ni cruzan a otro tenant (garantía ya implementada por E3-3; se pone por escrito).

El CEO elige entre los candidatos que pasen el filtro. La elección se registra como decisión comercial, no como gap de diseño.

---

## 3. Flujo de onboarding

### 3.1 Aprobación del tenant

1. El candidato completa el formulario de signup (`/api/public/signup`) o se registra por canal directo.
2. `platform_admin` revisa el tenant pendiente en `/api/admin/tenants`.
3. Se verifica que el slug sea único y que el plan sea `beta_design_partner` (ver `ENT_FB_PRICING_TIERS_v1.md`).
4. `platform_admin` aprueba el tenant con confirmación HITL (`confirmation_token`).
   - Endpoint: `POST /api/admin/tenants/{tenant_id}/approve`
   - El approval dispara el bootstrap seed (`SPEC_FB_TENANT_BOOTSTRAP_SEED_v1.md`).

### 3.2 Bootstrap del tenant

El seed programa crea automáticamente:

- Workspace inicial vacío.
- Roles de sistema: owner, admin, curador, ceo (heredados del seed MWT).
- Config en cascada: timezone, budget por plan, `ambient.enabled:false`, HITL irreversibles `NEVER`, segundo gate gold activo.
- Presets de routing por defecto (`SPEC_FB_ROUTING_PRESETS_v1.md`).
- Configuración ambiental por tenant.

El owner del tenant recibe credenciales y accede por primera vez.

### 3.3 Conectar cuentas de correo del tenant

1. El owner registra cuentas IMAP/SMTP propias del tenant (app-passwords, nunca credenciales de plataforma).
   - Ver procedimiento H2 de E2 y documentación de `email_account`.
2. Se prueba recepción con un correo de prueba no productivo.
3. Se registra el resultado en `audit_log` con `actor_id` y `actor_role_at_decision`.

### 3.4 Carga inicial de Knowledge Base

1. Se identifican los documentos fuente del tenant: listas de precios, condiciones comerciales, productos/servicios, contactos clave.
2. Se usan los cargadores existentes (`/api/workspaces/{id}/kb/sources`) para ingestar:
   - PDFs de catálogos.
   - Hojas de precios (CSV/XLSX).
   - Notas de texto con políticas comerciales.
3. El curador verifica que cada fact extraído tenga cita y `source_locator`.
4. No se inventan datos: si falta una fuente, se pide al tenant.

### 3.5 Habilitar packs de skills

1. Se habilitan los skills del **PACK 1 (fiscalidad electrónica)** para facturación:
   - `SKILL_FE_EMITIR_FACTURA`
   - `SKILL_FE_VALIDAR_RECEPTOR`
   - `SKILL_FE_ANULAR_FACTURA`
2. Se habilitan los skills del **PACK 3 (cobranza)** para conciliación:
   - `SKILL_CO_PAYMENT_MATCH_FE`
   - `SKILL_CO_COBRANZA_SEGUIMIENTO`
3. Cada skill se promueve a `ACTIVE` solo después de >=3 golden cases verdes con evidencia real del tenant.
4. Se configuran los modelos y presupuestos por tenant (`ENT_FB_PRICING_TIERS_v1.md`).

### 3.6 Capacitación de 1 sesión

1. Duración: 60-90 minutos.
2. Contenido:
   - Flujo de trabajo: correo → cotización → borrador HITL → aprobación → envío.
   - Cómo usar la bandeja WorkLoom para aprobar/rechazar acciones.
   - Cómo revisar el ledger de costo por tenant.
   - Cómo emitir la primera factura manual usando PACK 1.
3. Se entrega guía rápida escrita y se agenda check-in quincenal.

### 3.7 Billing manual

1. El tenant opera 90 días gratis (plan BETA). No hay pasarela de pagos en E3-6.
2. Al finalizar el período de prueba, el owner emite la **primera factura electrónica** usando los propios skills del PACK 1 sobre el tenant MWT (dogfooding).
3. El pago se recibe por transferencia bancaria.
4. El equipo FaberLoom registra el pago en `payment_reconciliation` y lo empareja con la factura (`PATCH /api/tenants/{tenant_id}/reconciliations/{id}/match`).
5. Si el monto coincide, el sistema marca la factura como `paid` automáticamente.

### 3.8 Soporte y SLA

- Canal: correo al equipo FaberLoom.
- Ventana de mantenimiento: documentada y comunicada antes del onboarding.
- SLA honesto de beta:
  - Mejor esfuerzo en horario hábil.
  - Backup diario.
  - RPO 24h.
  - Sin garantía de uptime escrita hasta salida de beta.

---

## 4. Checklist de cierre

- [ ] Design partner aprobado por CEO y acuerdo de datos firmado.
- [ ] Tenant aprobado por `platform_admin` con audit.
- [ ] Workspace bootstrap creado y verificado.
- [ ] Cuentas de correo conectadas con app-passwords propias.
- [ ] KB inicial cargado, curado y con citas verificables.
- [ ] PACK 1 y PACK 3 en `ACTIVE` con golden cases verdes.
- [ ] Sesión de capacitación completada y registrada.
- [ ] Primera factura emitida y pagada mediante billing manual + reconciliación.
- [ ] Soporte/SLA documentado y comunicado al tenant.

---

## 5. Riesgos P0 y acciones

| Riesgo | Acción |
|---|---|
| Fuga cross-tenant | Detener onboarding inmediatamente; ejecutar suite E3-3 antes de reanudar. |
| Skill ejecuta efecto externo sin HITL | Pasar skill a SHADOW; revisar compiler v2. |
| Dato inventado en output | No promover a ACTIVE; exigir fuente citada. |
| `platform_admin` accede a contenido | Tratar como incidente; el rol no debe leer contenido. |
| Pago no concilia | Mantener factura como `sent` hasta resolución manual; no marcar pagada sin evidencia. |

---

## 6. Referencias

- `PLAN_DESARROLLO_FABERLOOM_ETAPA3_v1.md`: hito E3-6 y gates de cierre de etapa.
- `SPEC_FB_TENANT_BOOTSTRAP_SEED_v1.md`: semilla de bootstrap.
- `ENT_FB_PRICING_TIERS_v1.md`: planes y límites.
- `SPEC_FB_ROUTING_PRESETS_v1.md`: presets de routing por tenant.
- `ENT_FB_SKILL_CATALOG_v1.md` y `SCH_FB_SKILL_MANIFEST_v2.md`: catálogo de skills y manifest.
- `ARCH_FB_AGENT_RUNTIME_EVAL_v1.md`: modelo de sello criptográfico y aislamiento.

---

Changelog:
- v1.0 (2026-07-08): Creación. Playbook de onboarding asistido para primer tenant externo E3-6.
