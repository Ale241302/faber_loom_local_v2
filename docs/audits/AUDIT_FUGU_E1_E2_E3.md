# AUDIT_FUGU_E1_E2_E3 -- Auditoria de cobertura E1/E2/E3 (FaberLoom SpaceLoom)

id: AUDIT_FUGU_E1_E2_E3
version: 1.0
status: DRAFT
fecha: 2026-07-07
autor: fugu (auditoria de codebase, sin graphify)
alcance: Plan E1/E2/E3 vs. codigo en app/src, app/static/js, app/tests
base: PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1, _ETAPA2_v1, PLAN_DESARROLLO_FABERLOOM_ETAPA3_v1, E3_DESGLOSE_HITOS_v1

> Nota de metodo: auditoria estatica. NO se ejecuto la suite ni graphify (instruccion
> explicita). "Verde/Rojo" aqui = existencia y forma del codigo/tests, no resultado de
> ejecucion. Numeros de linea son aproximados al estado del arbol auditado.

---

## 1. COBERTURA (que esta implementado, con evidencia)

### 1.1 Etapa 1 (SL0-SL5) -- IMPLEMENTADA (base madura)

La Etapa 1 esta materializada y con una bateria de tests amplia. Evidencia principal:

- **Costuras contract-first vivas:**
  - `Context(workspace_id, tenant_id, user_id, actor_id, actor_role_at_decision)` con
    `enforce_tenant_scoped()` fail-closed -- `app/src/context.py`.
  - `AuditWriter` dual-write (DB `audit_log` + `audit.jsonl`) con `correlation_id`,
    `approved_by`, `routine_version`, `skill_version`, `source_version` -- `app/src/audit.py`.
  - Auth por cookie HttpOnly `faberloom_at` + refresh `faberloom_rt`, `GET /api/me`,
    sin JWT en localStorage -- `app/src/auth.py` (`_cookie_settings`, `get_current_user`).
- **Router / proveedores:** `app/src/router/{engine,providers,registry,config_store,cost}.py`
  (BYO-key, catalogo, costo). Tests `test_sl1a_router*.py`.
- **KB con citas + injection canaries:** `app/src/kb.py`, `app/src/security/injection.py`
  (`assert_safe_kb_source`, CSV/HTML/hidden-instruction guards). Tests `test_sl2_*`,
  `test_sl5_prompt_injection.py`.
- **Skills / WorkLoom / Gold loop / Seal / Packaging:** `skills.py`, `workloom.py`,
  `gold.py`, `seal.py`, `packaging.py`. Tests `test_sl3a_skills.py`,
  `test_sl3b_workloom_gold.py`, `test_sl3_5_seal.py`, `test_sl4_packaging.py`.
- **Correo/IMAP + feature flags:** `connectors/imap.py`, `features.py`. Tests `test_sl5_*`.

### 1.2 Etapa 2 (E2-0..E2-6) -- IMPLEMENTADA (mayoritariamente)

| Hito | Estado | Evidencia |
|---|---|---|
| E2-0 convergencia auth/context/audit + canary + gold 2o gate | Implementado | `test_e2_0_auth_context.py`, `test_e2_0_auth_me.py`, `test_e2_0_audit_correlation.py`, `test_e2_0_canary_tenant.py`, `test_e2_0_context_enforcement.py`, `test_e2_0_gold_second_gate.py` |
| E2-0 migracion Postgres (staging) | Implementado (staging) | `test_e2_0_postgres_migration.py`, `scripts/sqlite_to_postgres.py`, `scripts/postgres_rls_policies.sql` |
| E2-2 correo instancia compartida | Implementado | `test_e2_2_mail_shared_instance.py` |
| E2-3 canary gate + KB gold | Implementado | `test_e2_3_canary_gate.py`, `test_e2_3_kb_gold.py` |
| E2-4 auto-dispatcher + catalogo + policy + ledger por pasos | Implementado | `routing/auto_dispatcher.py`, `routing/catalog.py`, `routing/policy.py`, `ledger.py`; tests `test_e2_4_*` |
| E2-5 ciclo ambiental (dark-launch) | Implementado | `ambient.py`, `ambient_detectors.py`, `ambient_models.py`; `test_ambient.py` |
| E2-6 storage/ingest/backup/objetos + leak test | Implementado | `storage.py`, `ingest.py`, `backup.py`; `test_e2_6_*` (incl. `test_e2_6_object_leak.py`) |

- **HITL doble confirmacion:** patron `_confirmation_token` / `_require_confirmation`
  (409 si falta token) aplicado a envio de chat, borrado de API key y borrado de KB source
  -- `app/src/api.py` (~lineas 254-265, 745-751, 1995-2015, 2479-2485). Foundation:
  `m13_draft_hitl.py`.
- **Segundo gate gold (hard fields `verified_by != approved_by`):** `test_e2_0_gold_second_gate.py`.

### 1.3 Etapa 3 (E3-0..E3-6) -- PARCIAL, concentrada en E3-1/E3-2

| Hito | Estado | Evidencia / faltante |
|---|---|---|
| E3-0 cierre operativo + seguridad | Casi todo es operacion humana (rotacion VPS/correo, acta). Codigo: falta `security/secrets.py`, `connectors/smtp.py`, whisper en `ingest.py`. Tests `test_e3_0_*` NO existen. | Ver Brechas |
| E3-1 switch Postgres+RLS | **Mas avanzado.** Adapter dual `db_adapter.py` (traduce `?`->`%s`, pool psycopg3, `SET LOCAL app.current_tenant/current_workspace/tenant_id`); `context.apply_to_connection`; canario `scripts/check_canary_isolation_postgres.py`; tests `test_e3_1_postgres_adapter.py`, `test_e3_1_rls_canary.py`, `test_e3_1_kb_fts_parity.py`, `test_e3_1_postgres_migration.py`. | Falta corte real a prod; tests Postgres hacen skip sin servidor |
| E3-2 tenant lifecycle (signup->tenant->owner) | **Solo frontend + test de assets.** `static/js/signup.jsx`, `tenant_admin.jsx`, `tenant_settings.jsx` existen; `test_e3_2_signup_ui.py` valida solo strings de los assets. | Backend inexistente: no hay `/api/public/signup`, ni `plans.py`, ni `config_cascade.py`, ni rol `platform_admin` |
| E3-3 entidad por tenant + sello | **No iniciado.** | Faltan `entity_identity.py`, `key_broker.py`, `crypto/envelope.py`; memoria namespaced en `m17_memory.py`; contamination suite E3-3 |
| E3-4 fabrica de skills (olas 0-2) | **No iniciado.** | Faltan `evidence_bundle.py`, `track_record.py`, `external_lookup.py`, `informal_capture.py`, P15-P18, compiler v2; tests `test_e3_4_*` |
| E3-5 routing por tenant + BYO + presets builder | **No iniciado** (base E2-4 existe). | Falta ledger por tenant, catalogo scoped por tenant, `presets_builder.jsx` |
| E3-6 tenant externo + billing manual | **No iniciado.** | Faltan `onboarding/`, `billing/`, `health/telemetry.py`, `support.py` y tests `test_e3_6_*` |

---

## 2. BRECHAS CRITICAS (que falta para E3-0..E3-6)

**E3-0**
- No existe `app/src/security/secrets.py` (rotacion/verificacion + helpers de cifrado por tenant, prep E3-3).
- No existe `app/src/connectors/smtp.py` con envio HITL doble confirmacion (el envio HITL vive hoy en api.py, no como conector reutilizable).
- Whisper local (`faster-whisper`) NO integrado en `ingest.py`: el fail-closed de audio/video de E2-6 sigue abierto (audio/video se validan por injection pero no se transcriben).
- Faltan los tests `test_e3_0_mail_end_to_end.py`, `test_e3_0_auto_mode.py`, `test_e3_0_ambient_darklaunch.py`, `test_e3_0_whisper_ingest.py`.
- Acta `ACTA_ETAPA2_TERMINADA` no presente.

**E3-1** (mas cerca del verde)
- El corte real a Postgres en prod no esta hecho (default sigue `sqlite`). Falta script de freeze/read-only + rollback documentado.
- Los tests Postgres hacen skip cuando no hay servidor: la "suite verde en Postgres" no esta demostrada en este arbol.
- FTS5->tsvector/GIN: existe test de paridad pero conviene verificar que `kb.py` ramifica por engine (no solo SQLite FTS5).

**E3-2** (brecha grande: todo el backend)
- No hay endpoint `/api/public/signup` ni verificacion de email ni rate-limit por IP.
- No hay `plans.py` (limites por plan, enforcement 422) ni `config_cascade.py` (user>workspace>tenant>default).
- No hay rol `platform_admin` en `m09_rbac.py` con aprobar/suspender tenant y metricas agregadas SIN contenido.
- Prefijos MinIO por tenant `t-{tenant}/ws-{workspace}/...` no implementados en `storage.py`.
- `check_canary_isolation` no esta generalizado a N-tenant en el path de creacion de tenant.

**E3-3** (no iniciado, es el nucleo de aislamiento)
- Sin identidad inmutable por tenant (`entity_identity.py`) ni test de auto-reescritura rechazada.
- Sin memoria namespaced `tenant+domain+visibility` en `m17_memory.py`.
- Sin llave graduada / key broker ni envelope encryption por tenant (`crypto/envelope.py`).
- Sin contamination suite de 4 dimensiones (filas, memoria, objetos, injection).

**E3-4/E3-5/E3-6**: no iniciados (ver tabla Sec.1.3). E3-5 puede apalancar E2-4 (ledger,
catalogo, policy) pero requiere scoping por tenant y presets builder UI.

---

## 3. RIESGOS P0

### 3.1 Fuga cross-tenant -- RIESGO ALTO en runtime actual
- **RLS no esta activo en runtime:** `FABERLOOM_DB_ENGINE` default = `sqlite`
  (`app/src/db_adapter.py`, `DB_ENGINE = os.environ.get(...,"sqlite")`). El aislamiento
  depende de que cada query filtre por `workspace_id`/`tenant_id` en codigo (defensa en
  profundidad), NO de RLS. Multi-tenant real es inaceptable aqui hasta E3-1 (el propio plan
  lo dice). Mitigacion parcial: `enforce_tenant_scoped()` existe pero solo se usa en ~8 sitios;
  no hay garantia de que TODAS las queries workspace-owned lo llamen.
- **Trust de headers de tenant:** `context_from_request` (app/src/api.py ~L279-292) puede
  tomar `x-tenant-id`/`x-user-id`/`x-actor-role` desde headers si `FABERLOOM_DEV_TRUST_HEADERS`
  esta seteado. Esto viola la regla "tenant fluye via context, NUNCA via headers". Debe
  garantizarse que esa env jamas se active en prod y, idealmente, eliminarse antes de E3-2.

### 3.2 HITL (envio/borrado) -- CUBIERTO, con vigilancia
- Doble confirmacion via `_confirmation_token`/`_require_confirmation` (409) para chat send,
  borrado de API key y borrado de KB source (app/src/api.py). Riesgo residual: cada NUEVA
  accion irreversible de E3 (envio SMTP conector, borrado de tenant, rotacion de key) debe
  reusar este patron; falta el conector SMTP HITL de E3-0.

### 3.3 Injection por contenido -- CUBIERTO parcialmente
- `security/injection.py` neutraliza CSV/HTML/hidden-instructions y bloquea xlsx/pdf/html
  crudos (fuerza texto extraido). Riesgo abierto: audio/video se validan pero **no hay
  transcripcion** (whisper pendiente E3-0); una transcripcion futura debe pasar por
  `assert_safe_kb_source(source_type="audio"/"video")` (ya contemplado en el codigo, falta
  el pipeline). SKILL.md linter existe (`validate_skill_md`).

### 3.4 Dato inventado sin fuente -- CUBIERTO en KB, pendiente en skills
- KB exige citas (tests SL2). El principio "dato exacto = lookup con cita y fecha" para la
  fabrica de skills (E3-4) NO tiene aun `evidence_bundle.py` ni `external_lookup.py`
  fail-closed: riesgo P0 latente cuando se instancien skills.

### 3.5 Identidad reescribible en sesion -- RIESGO ABIERTO (E3-3 no iniciado)
- No existe `entity_identity.py` ni versionado inmutable ni test de auto-reescritura
  rechazada+auditada. Hasta E3-3, la identidad del agente-entidad por tenant no esta
  protegida por codigo.

### 3.6 Learning cross-tenant -- CORRECTO por ahora
- `gold.py` cuenta k-anon SOLO dentro del mismo `tenant_id` (WHERE tenant_id = ?), no hay
  promocion cross-tenant. E3-3 exige que esto sea "inexistente por codigo, no por config":
  hoy es por query; conviene un guard explicito.

---

## 4. DECISIONES ABIERTAS (plan dice "decidido" pero no se ve en codigo)

1. **Postgres+RLS como runtime (E3-1, "la deuda que ya no puede esperar"):** decidido y con
   adapter listo, pero el runtime sigue en SQLite (corte real pendiente).
2. **Signup con aprobacion de platform_admin (E3-2):** decidido; sin backend ni rol RBAC.
3. **P15-P18 adoptados (taxonomia v2) y compiler v2 (E3-4):** decidido; no hay codigo de
   primitivos ni validacion de manifest v2.
4. **Whisper local SI (E3-0 t.6):** decidido; no integrado en `ingest.py`.
5. **Billing manual dogfooding PACK 1/PACK 3 (E3-6):** decidido; sin `billing/manual.py`.
6. **Cross-tenant learning PROHIBIDO por codigo (E3-3):** hoy solo garantizado por filtro de
   query en `gold.py`, no por un guard dedicado e infalsificable.
7. **Llave graduada + envelope encryption por tenant (E3-3):** decidido; sin `key_broker.py`
   ni `crypto/envelope.py`.
8. **Prefijos MinIO por tenant (E3-2):** decidido; `storage.py` no los aplica aun.

---

## 5. PROXIMOS PASOS (top 10, con archivos a tocar)

1. **Cerrar E3-1 (corte real):** script de freeze/read-only + rollback; probar suite con
   `FABERLOOM_DB_ENGINE=postgres` en CI con Postgres efimero. Tocar: `app/src/db.py`,
   `app/src/main.py` (banner mantenimiento), `app/scripts/sqlite_to_postgres.py`.
2. **Eliminar/riesgo-cerrar trust de headers de tenant:** quitar rama
   `FABERLOOM_DEV_TRUST_HEADERS` o restringirla a tests. Tocar: `app/src/api.py` (~L288-292).
3. **Auditar cobertura de `enforce_tenant_scoped`:** asegurar que TODA query workspace-owned
   lo llame. Tocar: `app/src/db.py`, helpers de repositorio; añadir test de cobertura.
4. **Backend E3-2 signup:** endpoint `/api/public/signup` + verificacion email + rate-limit.
   Tocar: `app/src/api.py`, `app/src/auth.py`; test `app/tests/test_e3_2_signup.py`.
5. **Rol platform_admin (RBAC, sin contenido):** `app/src/foundation/m09_rbac.py`,
   `m16_tenant_isolation.py`; test `test_e3_2_platform_admin.py`.
6. **Limites por plan + cascada de config:** crear `app/src/plans.py` y
   `app/src/config_cascade.py` (422 fail-closed, orden user>workspace>tenant>default);
   tests `test_e3_2_plan_limits.py`.
7. **Prefijos MinIO por tenant + canario N-tenant:** `app/src/storage.py`,
   `app/scripts/check_canary_isolation_postgres.py`; test `test_e3_2_tenant_isolation.py`.
8. **E3-3 identidad inmutable + memoria namespaced:** crear `app/src/entity_identity.py`,
   extender `app/src/foundation/m17_memory.py`; tests `test_e3_3_identity_immutable.py`,
   `test_e3_3_memory_isolation.py`.
9. **E3-3 crypto por tenant + llave graduada + contamination suite:** crear
   `app/src/crypto/envelope.py`, `app/src/key_broker.py`; guard explicito cross-tenant en
   `app/src/gold.py`; test `test_e3_3_contamination_suite.py`.
10. **E3-0 whisper + secrets + smtp conector + acta:** integrar faster-whisper en
    `app/src/ingest.py`, crear `app/src/security/secrets.py` y `app/src/connectors/smtp.py`
    (HITL), escribir `ACTA_ETAPA2_TERMINADA`; tests `test_e3_0_*`.

---

## 6. Resumen de estado

- E1: implementada y con tests amplios. E2: implementada (E2-0..E2-6). E3: parcial, con
  E3-1 (adapter/RLS + tests) como lo mas avanzado y E3-2 solo en frontend.
- El aislamiento fisico (RLS) aun NO gobierna el runtime (default sqlite): es el bloqueo
  #1 antes de crear tenants reales.
- E3-3 (identidad inmutable, memoria namespaced, cifrado por tenant, contamination suite)
  es la brecha de mayor riesgo P0 y no esta iniciada.

---

Changelog:
- v1.0 (2026-07-07): Auditoria estatica inicial E1/E2/E3 por fugu. Sin ejecucion de suite ni graphify.


---

## 5. AVANCES POST-AUDITORIA (2026-07-07)

### 5.1 P0 header-trust mitigado

- `FABERLOOM_DEV_TRUST_HEADERS` ahora solo tiene efecto cuando `PYTEST_CURRENT_TEST`
  está presente (`app/src/api.py`). En producción los headers `x-tenant-id`,
  `x-user-id`, `x-actor-id`, `x-actor-role` son ignorados.

### 5.2 E3-1 Postgres+RLS verificado

- Corregido `SET LOCAL app.current_tenant/workspace/tenant_id` en
  `app/src/db_adapter.py` usando interpolación segura con `psycopg.sql`.
- Corregidas políticas y placeholders en tests E3-1.
- RLS probado con rol `faberloom_app` (NOBYPASSRLS) en VPS Postgres:
  **19 passed** (`test_e3_1_*`).
- VPS Postgres tiene esquema migrado, RLS aplicado y rol `faberloom_app`
  configurado.
- Documentado cutover en `Plan/E3_CUTOVER_POSTGRES_RLS.md`.

### 5.3 E3-0 cimientos de seguridad

- Creado `app/src/security/secrets.py` con `TenantDataKey`, envelope encryption,
  rotación de data keys; tests `test_e3_0_secrets.py`.
- Creado `app/src/connectors/smtp.py` con `SMTPConfig`, `send_email`,
  `confirmation_token`, `verify_smtp_config`; tests `test_e3_0_smtp_hitl.py`.

### 5.4 E3-2 backend de tenant lifecycle

- Agregado `platform_admin` a `SYSTEM_ROLES` en `app/src/foundation/core.py`.
- Creado `app/src/plans.py` con planes `starter`/`growth`/`enterprise` y
  enforcement fail-closed; tests `test_e3_2_plans.py`.
- Creado `app/src/config_cascade.py` con resolución
  `user > workspace > tenant > default`; tests `test_e3_2_config_cascade.py`.
- Creado endpoint `POST /api/public/signup` en `app/src/auth.py` que crea tenant
  `pending_approval`, owner y roles; tests `test_e3_2_signup.py`.

### 5.5 E3-3 sello criptográfico (cimientos)

- Creado `app/src/entity_identity.py` con identidad inmutable por tenant,
  versionado y cambio solo por owner con confirmación; tests
  `test_e3_3_identity.py`.
- Creado `app/src/key_broker.py` con llave graduada
  (`closed`/`index`/`content`) y políticas CEO-only; tests
  `test_e3_3_key_broker.py`.
- Creado `app/src/crypto/envelope.py` sobre `security/secrets.py`; tests
  `test_e3_3_envelope.py`.

### 5.6 Tests representativos verdes

- Suite local representativa (E3 + E2 + E1): **57 passed**.
- Suite Postgres E3-1 contra VPS: **19 passed**.
- Tests de seguridad/auth/foundation: **26 passed**.

### 5.7 Pendiente explicito

- Corte real del VPS a Postgres+RLS (checklist listo, no ejecutado).
- Aprobación/suspensión de tenants por `platform_admin` (endpoint pendiente).
- Integrar `security/secrets.py` con `router/config_store.py` y `storage.py`.
- Whisper (`faster-whisper`) en `ingest.py`.
- `ACTA_ETAPA2_TERMINADA`.
- E3-4, E3-5, E3-6 no iniciados.
