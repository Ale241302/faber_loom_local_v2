# E3_DESGLOSE_HITOS_v1 — Desglose técnico de hitos Etapa 3 (Kimi + Fugu)

id: E3_DESGLOSE_HITOS_v1
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FaberLoom (app/)
type: DESGLOSE
stamp: 2026-07-07 — desglose operativo de PLAN_DESARROLLO_FABERLOOM_ETAPA3_v1 para ejecución por agentes seniors
relacionado: Plan/PLAN_DESARROLLO_FABERLOOM_ETAPA3_v1.md

---

## 0. Contexto de ejecución

- **Base de código:** `app/` (FastAPI + React UMD + SQLite hoy; Postgres+RLS mañana).
- **Costuras contract-first no negociables (AGENTS.md):**
  - Campos latentes en tablas: `tenant_id`, `actor_id`, `actor_role_at_decision`, `routine_version`, `skill_version`, `schema_version`, `source_version`, `approved_by`.
  - Capa `Context(workspace_id, tenant_id=None, user_id=None)` en toda query; helpers críticos llaman `enforce_tenant_scoped(ctx)`.
  - `AuditWriter` dual-write (DB + `audit.jsonl`); eventos llevan `correlation_id`.
  - Auth/session: cookie HttpOnly `faberloom_at` + `GET /api/me`; no leer JWT desde `localStorage`.
  - Tenant canario permanente (`workspace.is_canary=1`, `tenant_id='canary'`) es gate obligatorio.
  - Router abstrae proveedor; BYO-key hoy, keys gestionadas mañana.
- **Riesgos P0:** fuga cross-tenant, envío/borrado sin HITL, injection por contenido, dato inventado sin fuente, identidad reescrita en sesión.
- **Enfoque de esta ronda:** escribir primero los tests de cada hito (TDD) y el código mínimo para hacerlos verdes, respetando las costuras de arriba.

---

## 1. Resumen de hitos y riesgos P0

| Hito | Objetivo | Riesgo P0 principal |
|---|---|---|
| E3-0 | Cierre operativo E2: seguridad VPS/correo, modo auto, ambient dark-launch, Whisper local, acta de cierre. | Envío/borrado sin HITL; credenciales expuestas. |
| E3-1 | Switch runtime SQLite → Postgres+RLS; suite verde en Postgres; canario RLS por deploy. | Fuga cross-tenant por RLS mal seteado o query fuera de `Context`. |
| E3-2 | Tenant lifecycle: signup → aprobación platform_admin → seed → owner; límites por plan; aislamiento N-tenant. | `platform_admin` lee contenido; tenant hereda datos/config de otro. |
| E3-3 | Entidad por tenant + sello criptográfico: identidad inmutable, memoria namespaced, llave graduada, cifrado por tenant. | Contaminación cross-tenant (filas/memoria/objetos/injection); identidad reescribible. |
| E3-4 | Fábrica de skills: gramática P01-P18, manifest v2, compiler, evidence bundle, olas 0-2 (PACK 1 + PACK 3). | Skill con efecto externo sin HITL; dato inventado sin cita. |
| E3-5 | Routing por tenant: BYO keys, ledger separado por tenant, presets builder UI. | Request usa key/costo de otro tenant; cadena auto sin budget. |
| E3-6 | Primer tenant externo + billing manual: onboarding, factura PACK 1, conciliación PACK 3. | Fuga de datos del tenant externo; uso de sus datos para aprendizaje cross-tenant. |

---

## 2. Desglose por hito: archivos a crear / modificar / testear

### E3-0 — Cierre operativo de E2 + seguridad

**Backend**
- `app/src/security/secrets.py` (nuevo): rotación/verificación de credenciales, helpers de cifrado por tenant (preparación E3-3).
- `app/src/connectors/imap.py`: verificar app-passwords trade@ / mw_doc@; loguear fallos 535.
- `app/src/connectors/smtp.py` (si existe; si no, crear): envío HITL con doble confirmación y confirmation token.
- `app/src/audit.py`: asegurar `actor_id` + `actor_role_at_decision` en envío/aprobación.
- `app/src/router/engine.py` + `app/src/routing/auto_dispatcher.py`: encender modo auto con budget 2 USD/usuario y max 4 pasos.
- `app/src/ambient.py` + `app/src/ambient_cycle.py` (si separado): dark-launch global_enabled=1, métricas utilidad/ruido.
- `app/src/ingest.py`: integrar `faster-whisper` local (modelo small) para audio/video; canary de injection sobre transcripción.
- `app/src/main.py`: endpoints de health/gates E3-0.

**Frontend**
- `app/static/js/app.jsx`: UI de aprobación de correo con doble confirmación; estado modo auto; banner dark-launch.
- `app/static/js/fnd_core.jsx`: controles de seguridad y health gates.
- `app/static/js/admin_gates.jsx` (nuevo): dashboard de gates E3-0 (correo, auto, ambient, whisper).

**Base de datos**
- Columnas existentes en `audit_log`, `mail_outbox`, `usage_record`, `ambient_config` ya cubren la mayoría; agregar columnas de dark-launch si faltan.
- Tabla `refresh_tokens`, `email_account` ya existen; verificar que soporten rotación.

**Tests**
- `app/tests/test_e3_0_mail_end_to_end.py` (nuevo): recibir → draft → aprobar → enviar, con audit.
- `app/tests/test_e3_0_auto_mode.py` (nuevo): cadena auto real por usuario sin sobrecosto.
- `app/tests/test_e3_0_ambient_darklaunch.py` (nuevo): propuestas en dark, utilidad >=25%.
- `app/tests/test_e3_0_whisper_ingest.py` (nuevo): audio → transcripción → canary injection.
- `app/tests/test_p0_security.py` (ampliar): credenciales no en git, cifrado Fernet.

---

### E3-1 — Switch runtime Postgres+RLS

**Backend**
- `app/src/db.py` (gran cambio): adapter dual `FABERLOOM_DB_ENGINE=sqlite|postgres`; pool psycopg3; placeholders `%s` vs `?`; `SET LOCAL app.tenant_id` en cada transacción.
- `app/src/context.py`: `Context` debe florecer `tenant_id` a la conexión Postgres sin pasar por headers.
- `app/src/foundation/core.py`: foundation `get_conn()` debe usar el mismo adapter dual.
- `app/src/kb.py`: portar FTS5 → `tsvector`/GIN.
- `app/src/models.py`: asegurar que migraciones generen DDL compatible con Postgres (tipos TEXT, JSONB opcional, etc.).

**Frontend**
- Casi nulo; solo banner de mantenimiento/read-only durante corte (endpoint `/api/health/maintenance`).

**Base de datos**
- `app/scripts/postgres_rls_policies.sql`: agregar tablas faltantes (si hay nuevas tablas desde E2), ajustar `set_app_scope`.
- `app/scripts/sqlite_to_postgres.py`: mantener actualizado; verificar paridad de 616+ filas.
- `app/scripts/check_canary_isolation.py` (nuevo): canario RLS bidireccional por deploy.

**Tests**
- `app/tests/test_e3_1_postgres_adapter.py` (nuevo): suite corre con `FABERLOOM_DB_ENGINE=postgres`, placeholders traducidos, transacciones.
- `app/tests/test_e3_1_postgres_migration.py` (ampliar `test_e2_0_postgres_migration.py`): migración fresca + conteos.
- `app/tests/test_e3_1_kb_fts parity.py` (nuevo): mismas queries top-k en SQLite y Postgres.
- `app/tests/test_e3_1_rls_canary.py` (nuevo): RLS fuerza tenant_id, no bypass.

---

### E3-2 — Tenant lifecycle: signup → tenant → owner

**Backend**
- `app/src/auth.py`: flujo signup público con rate-limit por IP; verificación de email; token de signup.
- `app/src/foundation/m07_bootstrap.py`: reutilizar seed de MWT; parametrizar para nuevos tenants.
- `app/src/foundation/m09_rbac.py`: rol `platform_admin` (crear/aprobar/suspender tenants, métricas agregadas, NUNCA contenido).
- `app/src/foundation/m16_tenant_isolation.py`: endpoints de aprobación/suspensión de tenants; `tenant_scoped` generalizado.
- `app/src/plans.py` (nuevo): límites por plan (`ENT_FB_PRICING_TIERS_v1`); enforcement fail-closed.
- `app/src/config_cascade.py` (nuevo): resolución `user > workspace > tenant > default`.
- `app/src/storage.py`: prefijos MinIO `t-{tenant}/ws-{workspace}/...`; migrar objetos MWT.

**Frontend**
- `app/static/js/signup.jsx` (nuevo): pantalla pública signup (nombre empresa, slug, email owner, passphrase).
- `app/static/js/tenant_admin.jsx` (nuevo): panel `platform_admin` para aprobar/suspender tenants y ver métricas agregadas.
- `app/static/js/tenant_settings.jsx` (nuevo): settings tenant/workspace/user con herencia cascade.
- `app/static/js/app.jsx`: rutas públicas de signup.

**Base de datos**
- `app/src/models.py`: migraciones para tablas `tenant`, `plan`, `tenant_plan`, `tenant_settings`, `platform_admin_audit` (o reusar `audit_log` con `workspace_id='__system__'`).
- `app/scripts/postgres_rls_policies.sql`: políticas para nuevas tablas; `workspace` filtra por tenant.

**Tests**
- `app/tests/test_e3_2_signup.py` (nuevo): signup `acme`, verificación email, aprobación platform_admin.
- `app/tests/test_e3_2_tenant_seed.py` (nuevo): seed idempotente, roles owner/am/curador/ceo.
- `app/tests/test_e3_2_plan_limits.py` (nuevo): exceder usuarios/storage/budget → 422.
- `app/tests/test_e3_2_tenant_isolation.py` (nuevo): `check_canary_isolation` para cada tenant nuevo.
- `app/tests/test_e3_2_platform_admin.py` (nuevo): admin no lee contenido; acciones auditadas.

---

### E3-3 — Entidad por tenant + sello criptográfico

**Backend**
- `app/src/entity_identity.py` (nuevo): identidad inmutable por tenant; versionada; cambio solo owner con audit.
- `app/src/foundation/m17_memory.py`: memoria namespaced `tenant+domain+visibility`.
- `app/src/key_broker.py` (nuevo): llave graduada (cerrada/indice/contenido) por espacio; broker medía acceso; agente nunca tiene la llave.
- `app/src/crypto/envelope.py` (nuevo): envelope encryption — master key plataforma + data key por tenant; rotación.
- `app/src/router/config_store.py`: re-cifrar credenciales BYO con data key del tenant.
- `app/src/storage.py`: objetos sensibles cifrados con data key del tenant.
- `app/src/gold.py`: k-anon >=5 solo dentro del tenant; promoción cross-tenant inexistente por código.
- `app/src/ambient.py`: ciclo ambiental scoping por tenant.

**Frontend**
- `app/static/js/entity_identity.jsx` (nuevo): UI owner para ver/auditar identidad; cambio con doble confirmación.
- `app/static/js/key_policy.jsx` (nuevo): UI llave graduada por espacio; log de aperturas.
- `app/static/js/memory_namespace.jsx` (nuevo): visibilidad de memoria por tenant/domain.

**Base de datos**
- `app/src/models.py`: tablas `entity_identity_version`, `tenant_data_key`, `key_policy`, `memory_namespace`.
- Migración de credenciales Fernet global → data key por tenant.

**Tests**
- `app/tests/test_e3_3_identity_immutable.py` (nuevo): auto-rewrite rechazado y auditado.
- `app/tests/test_e3_3_memory_isolation.py` (nuevo): recuerdo A invisible en B.
- `app/tests/test_e3_3_key_policy.py` (nuevo): llave graduada operando; CEO-ONLY/FROZEN no cruzan.
- `app/tests/test_e3_3_crypto_envelope.py` (nuevo): cifrado/decifrado por tenant; rotación.
- `app/tests/test_e3_3_contamination_suite.py` (nuevo): filas, memoria, objetos, injection.

---

### E3-4 — Fábrica de skills (olas 0-2 para cierre de etapa)

**Backend**
- `app/src/skills.py`: compiler v2 valida manifest completo (archetype, tools_mcp, outcome metric, kill switch, learning target); rechaza manifest inválido.
- `app/src/routine_hub/compiler.py` (si separado): extender validación.
- `app/src/skills/` (nuevo directorio): implementación de primitivos P15-P18 y skills PACK 1 / PACK 3.
- `app/src/evidence_bundle.py` (nuevo): componente reutilizable de evidence bundle (URL + fecha + captura + valor).
- `app/src/track_record.py` (nuevo): ceilings mecánica por skill/usuario.
- `app/src/external_lookup.py` (nuevo): C0-2 recopilación viva con fail-closed.
- `app/src/informal_capture.py` (nuevo): C0-1 captura informal WhatsApp/texto/nota llamada.

**Frontend**
- `app/static/js/skill_catalog.jsx` (nuevo): catálogo de packs/skills; estados SHADOW/ACTIVE.
- `app/static/js/skill_golden_cases.jsx` (nuevo): revisión de golden cases por curador.
- `app/static/js/evidence_viewer.jsx` (nuevo): mostrar evidence bundle en outputs.

**Base de datos**
- `app/src/models.py`: tabla `skill_manifest`, `skill_version`, `golden_case`, `skill_track_record`, `pack_status`.

**Tests**
- `app/tests/test_e3_4_taxonomy_v2.py` (nuevo): P15-P18 presentes y validados.
- `app/tests/test_e3_4_compiler_v2.py` (nuevo): manifest inválido → fail-closed.
- `app/tests/test_e3_4_c0_1_informal.py` (nuevo): captura informal → HITL.
- `app/tests/test_e3_4_c0_2_external.py` (nuevo): fuente no disponible → fail-closed.
- `app/tests/test_e3_4_pack1_fe.py` (nuevo): golden cases PACK 1 fiscalidad electrónica.
- `app/tests/test_e3_4_pack3_cobranza.py` (nuevo): golden cases PACK 3 cobranza.

---

### E3-5 — Routing por tenant + BYO keys + presets builder

**Backend**
- `app/src/router/engine.py`: scoping de catálogo por tenant; BYO keys cifradas con data key del tenant.
- `app/src/router/providers.py`: modo estricto/híbrido opt-in; fallback a keys plataforma con recargo.
- `app/src/router/config_store.py`: almacenar keys por tenant; re-cifrado.
- `app/src/ledger.py`: costo agregado por tenant además de por usuario.
- `app/src/routing/policy.py` + `app/src/routing/catalog.py`: presets builder + templates.
- `app/src/plans.py`: defaults por tier.

**Frontend**
- `app/static/js/keys_manager.jsx` (nuevo): UI owner para registrar keys propias y elegir modo estricto/híbrido.
- `app/static/js/tenant_ledger.jsx` (nuevo): dashboard de costos por tenant.
- `app/static/js/presets_builder.jsx` (nuevo): builder de presets sobre ledger real.

**Base de datos**
- `app/src/models.py`: tablas `tenant_api_key`, `tenant_model_catalog`, `tenant_ledger`, `preset`, `plan_defaults`.

**Tests**
- `app/tests/test_e3_5_byo_keys.py` (nuevo): demo opera 100% con key propia; 0 requests con keys MWT.
- `app/tests/test_e3_5_tenant_ledger.py` (nuevo): costo separado por tenant.
- `app/tests/test_e3_5_presets_builder.py` (nuevo): preset creado y usado en cadena auto.
- `app/tests/test_e3_5_budget_tenant.py` (nuevo): budget por tenant fail-closed.

---

### E3-6 — Primer tenant externo + billing manual

**Backend**
- `app/src/onboarding/external_tenant.py` (nuevo): playbook de onboarding programático.
- `app/src/billing/manual.py` (nuevo): emisión de factura manual usando skills PACK 1; conciliación PACK 3.
- `app/src/health/telemetry.py` (nuevo): métricas agregadas por tenant para platform_admin.
- `app/src/support.py` (nuevo): canal de soporte y SLA honesto.

**Frontend**
- `app/static/js/external_onboarding.jsx` (nuevo): wizard de onboarding para design partner.
- `app/static/js/tenant_health.jsx` (nuevo): dashboard salud por tenant (uptime, errores, costo, casos).
- `app/static/js/manual_billing.jsx` (nuevo): vista de facturas/conciliaciones manuales.

**Base de datos**
- `app/src/models.py`: tablas `external_tenant`, `onboarding_checklist`, `manual_invoice`, `payment_reconciliation`, `support_ticket`.

**Tests**
- `app/tests/test_e3_6_onboarding.py` (nuevo): playbook completo de onboarding.
- `app/tests/test_e3_6_manual_invoice.py` (nuevo): factura emitida con skill PACK 1.
- `app/tests/test_e3_6_payment_match.py` (nuevo): conciliación PACK 3.
- `app/tests/test_e3_6_telemetry.py` (nuevo): métricas agregadas sin contenido.
- `app/tests/test_e3_6_continuous_isolation.py` (nuevo): suite E3-3 verde durante convivencia.

---

## 3. Asignación a agentes seniors

| Agente senior | Responsabilidad principal | Hitos | Archivos clave |
|---|---|---|---|
| **Backend Senior** | Lógica de negocio, APIs, adapter dual, tenant lifecycle, crypto/seal, routing/BYO, skills, onboarding/billing. | E3-0 backend, E3-1, E3-2 backend, E3-3 backend, E3-4 backend, E3-5, E3-6 backend. | `app/src/db.py`, `app/src/auth.py`, `app/src/foundation/*.py`, `app/src/router/*.py`, `app/src/skills.py`, `app/src/entity_identity.py`, `app/src/key_broker.py`, `app/src/crypto/`, `app/src/onboarding/`, `app/src/billing/`. |
| **Frontend Senior** | UI/UX pública y de admin: signup, tenant admin, identity/key policy, skill catalog, presets builder, onboarding externo, health. | E3-0 UI, E3-2 UI, E3-3 UI, E3-4 UI, E3-5 UI, E3-6 UI. | `app/static/js/app.jsx`, `app/static/js/signup.jsx`, `app/static/js/tenant_admin.jsx`, `app/static/js/entity_identity.jsx`, `app/static/js/key_policy.jsx`, `app/static/js/skill_catalog.jsx`, `app/static/js/presets_builder.jsx`, `app/static/js/external_onboarding.jsx`. |
| **Database SQL Senior** | Schema Postgres, RLS, migraciones, data keys, envelope encryption, FTS, backups, canarios de aislamiento. | E3-1 DB, E3-2 DB, E3-3 DB, E3-5 DB, E3-6 DB. | `app/src/models.py`, `app/scripts/postgres_rls_policies.sql`, `app/scripts/sqlite_to_postgres.py`, `app/scripts/check_canary_isolation.py`, DDL de `tenant_*`, `entity_identity_version`, `tenant_data_key`, `memory_namespace`. |

---

## 4. Orden de ataque recomendado

1. **E3-0 tarea 1 (seguridad):** rotar root VPS / SSH keys / claves correo. Esto es operación humana, no código.
2. **E3-1 (Postgres+RLS):** cimiento físico. Sin esto no se crea tenant real.
   - Database SQL Senior lidera schema/RLS/migración.
   - Backend Senior lidera adapter dual y tests.
3. **E3-2 (Tenant lifecycle):** una vez RLS real, se construye signup/seed/limits.
   - Backend Senior + Frontend Senior en paralelo.
4. **E3-3 (Sello criptográfico):** sobre E3-2.
   - Backend Senior + Database SQL Senior lideran crypto/schema.
   - Frontend Senior hace UI de identidad/llave.
5. **E3-4 (Fábrica de skills):** banda paralela desde E3-0.
   - Backend Senior lidera compiler + skills PACK 1/3.
   - Frontend Senior hace catálogo/golden cases.
6. **E3-5 (Routing/BYO):** sobre E3-2 + E3-3.
   - Backend Senior + Frontend Senior.
7. **E3-6 (Tenant externo):** cierre comercial.
   - Todos los agentes en onboarding, billing y telemetría.

---

## 5. Notas de implementación cruzadas

- **Adapter dual:** nunca dejar un `?` hardcodeado cuando `FABERLOOM_DB_ENGINE=postgres`. Usar un wrapper de placeholder o una query builder mínima.
- **Tenant_id en conexión Postgres:** llamar `SET LOCAL app.tenant_id = <ctx.tenant_id>` al inicio de cada transacción; nunca confiar en que la app recuerde el filtro.
- **MinIO:** migrar prefijos MWT existentes con script idempotente + verificación de conteo.
- **Crypto:** master key en env (`FABERLOOM_MASTER_KEY`); data keys por tenant almacenadas cifradas en `tenant_data_key`.
- **Skills:** todo skill nuevo debe tener golden case con evidencia real; sin cita verificable → SHADOW.
- **Tests:** cada PR debe pasar `pytest app/tests/test_e3_*` con `FABERLOOM_DB_ENGINE=postgres` en CI antes de merge.

---

## 6. Changelog

- v1.0 (2026-07-07): Desglose colaborativo Kimi + Fugu. Lista archivos backend/frontend/DB/tests por hito E3-0..E3-6, asignación a agentes seniors, orden de ataque y notas cruzadas.
