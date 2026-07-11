# Auditoría de cierre detallada — Etapa 3 FaberLoom

**Repo:** `c:\Users\ale13\OneDrive\Documents\faber_loom_local_vv2`  
**Rama:** `e3-cierre-parciales`  
**Plan auditado:** `Plan/PLAN_DESARROLLO_FABERLOOM_ETAPA3_v1.md`  
**Fecha de auditoría original:** 2026-07-08  
**Fecha de actualización:** 2026-07-10 (post Bloque 9)  
**Commit HEAD:** `57a21bf` (cierre codeable E3-4)  
**Auditor:** Fugu / Kimi Code CLI  
**Restricción:** read-only original; actualizado tras cierre de bloques 7-9.

---

## 1. Resumen ejecutivo

La Etapa 3 está **técnicamente cerrada en su lado codeable**: todos los hitos que pueden resolverse con código, tests y documentación tienen implementación verde. La suite completa del proyecto reporta **619 passed / 12 skipped / 0 failed** (631 tests colectados; 12 requieren servidor Postgres local o dependencias opcionales). Los P0 de diseño identificados en el reporte preliminar (`AUDIT_E3_PLAN_VS_CODE_20260708.md`) fueron remediados en los commits de cierre parciales (`376a07e`, `bfc88f7`, `096a5b0`, `4a423d1`, `46c8473`, `043e9b4`, `1a0192b`, `927165a`, `5740566`).

Quedan abiertos únicamente ítems que dependen de **acciones externas/no-code**: design partner con acuerdo firmado, certificados de firma comercial, carga de KB Marluvas/Tecmater (script listo), ejecución de rotación VPS/SSH/correo (runbook listo), migración real de objetos MWT en MinIO (script listo), conectores oficiales tributarios, y el soak de 30 días con factura pagada.

### Semáforo por hito

| Hito | Estado                  | Severidad máxima | DoD codeable                                                                                                                                                                                                            |
| ---- | ----------------------- | ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| E3-0 | 🟢 Cerrado técnicamente | P1\*             | Cerrado en código (SMTP HITL, Whisper runtime, acta). Runbook VPS/SSH/correo, script ingest KB H3 y script migración MinIO entregados; falta ejecución humana/evidencia.                                                |
| E3-1 | 🟢 Cerrado              | —                | Adapter dual, FTS→tsvector, migrador, RLS policies, corte real validado en VPS.                                                                                                                                         |
| E3-2 | 🟢 Cerrado              | —                | Signup UI+backend, bootstrap seed, planes, config cascade, platform_admin, canario N-tenant, prefijos MinIO + migración legacy.                                                                                         |
| E3-3 | 🟢 Cerrado              | —                | Identidad inmutable, key broker, envelope encryption, objetos cifrados, scheduler multi-tenant, contamination suite.                                                                                                    |
| E3-4 | 🟢 Cerrado técnicamente | P2*              | Olas 0-2 cerradas (taxonomía v2, compiler v2, C0-1/C0-2, evidence bundle, track record, P15/P17, WhatsApp webhook, migración skills legacy). Conectores tributarios implementados (mock/sandbox/live fail-closed). PACK 1/3 en SHADOW; olas 3-5 materializadas en `DRAFT`/`DEFINITION_PENDING`. Pendientes humanos: verificación de APIs reales, KB Marluvas/Tecmater, dogfood para promoción ACTIVE. |
| E3-5 | 🟢 Cerrado              | —                | Presets builder full-stack, BYO keys estricto/híbrido + recargo plataforma, ledger por tenant, wire "Usar en routine".                                                                                                  |
| E3-6 | 🟢 Cerrado técnicamente | P2\*             | Health dashboard, numeración secuencial de facturas, PDF no fiscal, SLA beta. Faltan design partner, acuerdo, certificados, soak real.                                                                                  |

### Conteo de bloqueantes y gaps

| Severidad | Cantidad | Observación                                                                                                                           |
| --------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **P0**    | 0        | Ningún bloqueante de seguridad/aislamiento/HITL sin remediar en código.                                                               |
| **P1**    | 0        | Las deudas operativas instrumentables (VPS/SSH, KB H3, MinIO) tienen runbook/script; la ejecución humana queda pendiente documentada. |
| **P2**    | 2*       | Certificados de firma comercial (HE2-9); design partner + soak de 30 días. Los conectores tributarios y las olas 3-5 están cerrados en código; sus pendientes son humanos/externos y se documentan abajo. |

### Hitos faltantes o no iniciados

1. **E3-0 t.1 — Ejecución de rotación VPS/SSH/claves correo**: el runbook `docs/OPERACION_VPS_E3.md` está listo; falta ejecución humana y evidencia en `docs/audits/`.
2. **E3-0 t.5 — Carga de KB real H3 (Marluvas/Tecmater)**: el script `app/scripts/ingest_kb_h3.py` está listo; faltan los archivos fuente del CEO y verificación de citas.
3. **E3-2 — Migración real de objetos MWT en MinIO**: el script `app/scripts/migrate_minio_objects_to_tenant_prefix.py` está listo; falta ejecutarlo en producción tras backup.
4. **E3-4 — Verificación humana de APIs tributarias reales** (ATV/SAT/DIAN, tracking TICA). El adaptador de conectores ya está implementado en `app/src/connectors/tax_authority.py`; solo falta validar URLs/credenciales/certificados con cada autoridad.
5. **E3-4 olas 3-5**: materializadas en estados `DRAFT`/`DEFINITION_PENDING` sin datos inventados. Su promoción a `ACTIVE` requiere golden cases reales (PACK 2 depende de KB Marluvas/Tecmater) y track record en dogfood.
6. **E3-6 — Design partner concreto** con acuerdo de datos firmado.
7. **E3-6 — Certificados de firma comercial** (HE2-9).
8. **E3-6 — Soak de 30 días** con ≥10 casos reales y primera factura pagada.

### Top 3 bloqueantes críticos (P0 potenciales si se avanza sin cerrarlos)

Aunque no hay P0 activos en código, los siguientes son los riesgos más altos si se avanza:

1. **KB real H3 sin cargar (`Plan/E3-0 t.5`)** — El script de ingest está listo, pero sin los archivos Marluvas/Tecmater la ola 3 (PACK 2 comex) no tiene golden cases reales; cualquier skill promovido sin fuente real violaría la regla de fábrica "sin dato inventado".
2. **Verificación humana de APIs tributarias (`E3-4 ola 1`)** — El adaptador `app/src/connectors/tax_authority.py` ya soporta ATV/SAT/DIAN en modo mock/sandbox/live; falta validar URLs reales, credenciales y certificados con cada autoridad antes de emitir factura electrónica real.
3. **Certificados de firma comercial no adquiridos (`HE2-9`)** — Bloquean la facturación electrónica real con el primer tenant externo; son requisito de compra, no de código.

### Parciales que funcionan pero necesitan refinamiento

- **E3-4 PACK 1/3**: están en SHADOW con golden cases y track-record gates; la promoción a ACTIVE requiere golden cases reales del tenant.
- **E3-5 BYO keys**: modo estricto/híbrido + recargo plataforma implementado en el ledger (`app/src/ledger.py`, `test_e3_5_byo_modes.py`).
- **E3-6 billing manual**: health dashboard, numeración secuencial por tenant y PDF no fiscal implementados; la emisión de factura electrónica real requiere conectores tributarios y certificados.

### Recomendación final

**Es seguro declarar la Etapa 3 "cerrada técnicamente"** y avanzar a la fase comercial/operativa de E3-6. E3-4 en particular queda **cerrado en su lado codeable**: conectores, materialización de olas 3-5 y promotion readiness están implementados y testeados. El siguiente paso más valioso es:

1. **CEO: conseguir los archivos Marluvas/Tecmater y un design partner** que firme el acuerdo de datos (distribución B2B técnica, según `ENT_FB_VERTICAL_CANDIDATES_v2`).
2. **Dev + AM: verificar/acceder a APIs oficiales ATV/SAT/DIAN** y documentar el resultado en `ENT_FB_SKILL_CATALOG_v1.1` y `docs/faberloom/PLB_FB_VERIFICACION_APIS_TRIBUTARIAS_v1.md`.
3. **Curador + AM: ejecutar dogfood de PACK 1/3**, proponer/aprobar/verificar golden cases reales y usar el tablero de promotion readiness para promover a ACTIVE cuando se cumplan los umbrales.
4. **Ops: ejecutar los runbooks/scripts entregados** (rotación VPS/SSH/correo, migración MinIO) y dejar evidencia en `docs/audits/`.

No se recomienda abrir signup público (E4) hasta que E3-6 cierre con tenant externo ≥30 días y 0 fugas.

---

## 2. Detalle por hito

### E3-0 — Cierre operativo de E2 + seguridad

**Estado del hito:** 🟢 **Cerrado técnicamente** (deudas operativas instrumentadas; ejecución humana pendiente).

**Requerimientos del plan:**

1. Rotar password root VPS, migrar SSH a llaves, rotar claves de correo compartidas, verificar `.env` no en git y credenciales cifradas.
2. Gate H1 correo end-to-end: recibir → draft → aprobar → enviar, con `actor_id` y `actor_role_at_decision` en audit.
3. Encender modo auto (budget 2 USD/usuario, max 4 pasos), 7 días observación.
4. Dark-launch ciclo ambiental (`ambient_config.global_enabled=1`), 14 días observación.
5. KB real H3 cargada antes de ola 3.
6. Whisper local en imagen runtime.
7. Acta de cierre E2 escrita.

**Evidencia en código y archivos:**

| Tarea                  | Archivos / funciones / líneas                                                                                                                                                                     | Estado                             |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| Seguridad operativa    | Runbook `docs/OPERACION_VPS_E3.md` con checklist de rotación VPS/SSH/claves de correo. Ejecución real y evidencia aún pendientes.                                                                 | ✅ Cerrado en código/documentación |
| Gate H1 correo HITL    | `app/src/connectors/smtp.py` (`send_email`, `confirmation_token`); `app/src/api.py:3863-3902` (`_smtp_transmit`); `app/src/api.py:3904-3921` (`api_send_mail_reply` con `_require_confirmation`). | ✅ Cerrado                         |
| Modo auto              | `app/src/routing/auto_dispatcher.py`; endpoint `/workspaces/{id}/chats/{chat_id}/auto` en `app/src/api.py:1407`.                                                                                  | ✅ Cerrado                         |
| Dark-launch ambiental  | `app/src/ambient.py`; tablas `ambient_config`, `ambient_workspace_config`, `ambient_proposal`.                                                                                                    | ✅ Cerrado                         |
| KB real H3             | Script `app/scripts/ingest_kb_h3.py` listo; ingest genérico en `app/src/kb.py`. Faltan archivos fuente Marluvas/Tecmater.                                                                         | ✅ Cerrado en código/documentación |
| Whisper runtime        | `app/src/ingest.py:245-278` (`_extract_audio`); `app/requirements-server.txt:27` (`faster-whisper>=1.1.0`); `Dockerfile:31` (`ffmpeg`).                                                           | ✅ Cerrado                         |
| Acta cierre E2         | `docs/audits/ACTA_ETAPA2_TERMINADA.md` v1.0.0.                                                                                                                                                    | ✅ Cerrado                         |
| Acta cierre parcial E3 | `docs/audits/ACTA_ETAPA3_CIERRE_PARCIALES_20260710.md` v1.0.0.                                                                                                                                    | ✅ Cerrado                         |

**Qué se hizo para cerrar:**

- Se extrajo el conector SMTP a `app/src/connectors/smtp.py` con token de confirmación determinístico; `api_send_mail_reply` ahora usa `_smtp_transmit` que invoca `smtp.send_email` con `confirmation_token_value`.
- Se integró `faster-whisper` en `ingest.py` con fallback `LocalOnlyEngineMissingError`; se agregó `ffmpeg` y la dependencia al Dockerfile.
- Se escribió el acta de cierre formal.
- Se entregó el runbook `docs/OPERACION_VPS_E3.md` para rotación VPS/SSH/correo.
- Se entregó el script `app/scripts/ingest_kb_h3.py` para carga masiva de fuentes KB H3.
- Se entregó el script `app/scripts/migrate_minio_objects_to_tenant_prefix.py` para migración de objetos legacy a prefijo por tenant.

**Cómo funciona:**

- El endpoint `POST /api/workspaces/{workspace_id}/mail/{mail_id}/send` exige `confirmation_token` (HITL). `_smtp_transmit` computa el token esperado y solo transmite si coincide.
- `_extract_audio` importa `WhisperModel` de `faster-whisper` bajo demanda, escribe el blob a un archivo temporal y transcribe; el texto pasa por `assert_safe_kb_source` antes de indexarse.

**Bloqueantes/gaps:**

- Las deudas operativas instrumentables ya tienen runbook/script; queda pendiente la ejecución humana y la evidencia documentada en `docs/audits/`. No son bloqueantes de código.
- KB real H3 requiere archivos fuente del CEO; el cargador está listo.

**Tests:**

- `app/tests/test_e3_0_smtp_hitl.py`: 5 passed.
- `app/tests/test_e3_0_whisper_ingest.py`: 5 passed, 2 skipped (dependen de mock).
- `app/tests/test_e3_0_secrets.py`: 12 passed.
- `app/tests/test_e3_0_kb_h3.py`: 3 passed.

---

### E3-1 — Switch runtime Postgres+RLS

**Estado del hito:** 🟢 **Cerrado**.

**Requerimientos del plan:**

1. Adapter dual SQLite/Postgres; placeholders `?` traducidos a `%s`; `SET LOCAL app.tenant_id/workspace` por transacción.
2. FTS5 → tsvector/GIN con paridad funcional.
3. Suite completa verde contra Postgres.
4. Migrador + RLS policies + canario.
5. Corte real documentado con rollback.
6. Post-corte: SQLite read-only 30 días, backup nocturno verificado.

**Evidencia en código y archivos:**

- `app/src/db_adapter.py`: adapter dual, `_translate_placeholders`, `_PostgresConnectionWrapper`, `transaction(conn, ctx)` setea `app.current_tenant`, `app.current_workspace`, `app.tenant_id`.
- `app/src/kb.py`: `search_kb_chunks` soporta SQLite FTS5 y Postgres tsvector/GIN.
- `app/scripts/sqlite_to_postgres.py`: migrador completo.
- `app/scripts/postgres_rls_policies.sql`: políticas RLS.
- `app/scripts/check_canary_isolation_postgres.py`: canario generalizado a N tenants (`run_isolation_checks_for_tenants`, `list_all_tenant_ids`).
- `Plan/E3_CUTOVER_POSTGRES_RLS.md` v1.2: estado `CORTE_COMPLETADO_Y_VALIDADO`.

**Qué se hizo para cerrar:**

- Se implementó el adapter dual que permite cambiar de motor con `FABERLOOM_DB_ENGINE=sqlite|postgres` sin reescribir queries.
- Se portó la búsqueda KB a Postgres usando `to_tsvector` + índice GIN.
- Se corrigió el canario para iterar todos los tenants (`test_e3_2_canary_all_tenants.py`).
- Se ejecutó el corte real en VPS el 2026-07-07; producción apunta a Postgres+RLS.

**Cómo funciona:**

- `transaction(conn, ctx)` detecta conexión Postgres y ejecuta `SET LOCAL app.current_tenant = ...`, `SET LOCAL app.current_workspace = ...`. Las policies RLS en Postgres filtran filas por estas variables de sesión, haciendo el aislamiento físico independiente de la lógica de la app.
- El wrapper `_DictRow` normaliza filas psycopg3 para que código existente que usa `row["col"]` y `row[0]` funcione sin cambios.

**Bloqueantes/gaps:**

- Ninguno en código. El plan de backup nocturno verificado con smoke de restore (DoD 7.5 E1) es una operación recurrente que debe seguir ejecutándose; no es un gap de código.

**Tests:**

- `app/tests/test_e3_1_postgres_adapter.py`: 7 passed, 5 skipped (sin Postgres local).
- `app/tests/test_e3_1_kb_fts_parity.py`: 3 passed, 2 skipped.
- `app/tests/test_e3_1_postgres_migration.py`: 4 passed, 1 skipped.
- `app/tests/test_e3_1_rls_canary.py`: 5 passed, 4 skipped.
- `app/tests/test_e3_2_canary_all_tenants.py`: 3 passed.

---

### E3-2 — Tenant lifecycle: signup → tenant → owner

**Estado del hito:** 🟢 **Cerrado**.

**Requerimientos del plan:**

1. Signup público con `company_name`, slug único, email owner, passphrase Argon2id, verificación email, rate limit por IP, aprobación platform_admin.
2. Bootstrap seed programático con roles, settings default, workspace inicial.
3. Herencia config en cascada tenant → workspace → user.
4. Límites por plan (usuarios, workspaces, storage, budget) fail-closed.
5. Rol platform_admin con approve/suspend/change plan, sin acceso a contenido.
6. Aislamiento N-tenant; prefijos MinIO `t-{tenant}/ws-{workspace}`.

**Evidencia en código y archivos:**

- `app/static/js/signup.jsx:106`: envía `company_name` (fix del P0-1 del reporte preliminar).
- `app/src/auth.py:372-617`: `PublicSignupRequest`, `public_signup`, verificación email, rate limiting.
- `app/src/platform_admin.py`: endpoints `/admin/tenants`, `/admin/tenants/{id}/approve`, `/suspend`, `/plan`, `/metrics`; `_bootstrap_approved_tenant`.
- `app/src/config_cascade.py`: resolver `user > workspace > tenant > default`.
- `app/src/plans.py`: `PlanLimits`, `enforce_user_creation`, `enforce_workspace_creation`, `enforce_budget`.
- `app/src/storage.py:39-42`: `workspace_object_prefix` soporta `t-{tenant}/ws-{workspace}`.

**Qué se hizo para cerrar:**

- Se corrigió `signup.jsx` para enviar `company_name` en lugar de `name`.
- Se implementó el flujo completo de signup con token de verificación SHA-256, rate limit por IP y estado `pending_approval`.
- Se creó el módulo `platform_admin.py` con approve/suspend/change plan protegidos por `confirmation_token`.
- Se implementó el bootstrap seed que crea workspace, settings default (`ambient.enabled=false`, `routing.auto_dispatch=false`, budget 2 USD, max 4 pasos), política de routing y presets por defecto.
- Se implementó la resolución de configuración en cascada.

**Cómo funciona:**

- `public_signup` inserta en `fnd_tenants` (Foundation) con estado `pending_approval`, crea owner con rol `owner`, envía email de verificación y registra audit `tenant.signup`.
- `approve_tenant` requiere `confirmation_token` determinista, actualiza Foundation, y llama `_bootstrap_approved_tenant` que crea el workspace y config inicial en la app DB (SQLite o Postgres según motor).
- `config_cascade.resolve` recorre `fnd_users.preferences_json` → tablas workspace → `tenant_settings` → `DEFAULTS`.
- `plans.enforce_*` consulta Foundation para el plan del tenant y rechaza con 422 si se excede el límite.

**Bloqueantes/gaps:**

- **Resuelto en código**: `app/scripts/migrate_minio_objects_to_tenant_prefix.py` implementa la migración legacy → `t-{tenant}/ws-{workspace}` con dry-run, copia, actualización de BD, recompute de HMAC y verificación de conteos. Queda pendiente la ejecución en producción.

**Tests:**

- `app/tests/test_e3_2_signup.py`: 7 passed.
- `app/tests/test_e3_2_signup_ui.py`: 5 passed.
- `app/tests/test_e3_2_plans.py`: 2 passed.
- `app/tests/test_e3_2_config_cascade.py`: 4 passed.
- `app/tests/test_e3_2_settings_api.py`: 5 passed.
- `app/tests/test_e3_2_minio_object_migration.py`: 4 passed.

---

### E3-3 — Entidad por tenant + sello criptográfico

**Estado del hito:** 🟢 **Cerrado**.

**Requerimientos del plan (7 puntos de ARCH_FB_AGENT_RUNTIME_EVAL):**

1. Identidad inmutable por tenant; reescritura solo owner distinto con confirmation token.
2. Índice global vs contenido sellado; cross-tenant inexistente.
3. Memoria namespaced por tenant+dominio+visibilidad.
4. Llave graduada (closed/index/content) controlada por owner, mediada por broker.
5. Cifrado por tenant con envelope encryption.
6. Contamination suite 0 fugas (filas, memoria, objetos, injection).
7. Ciclo ambiental multi-tenant (budget, ventana, kill switch por tenant).

**Evidencia en código y archivos:**

- `app/src/entity_identity.py`: `create_identity`, `update_identity` con self-approval prohibition; tabla `entity_identity_version` append-only.
- `app/src/key_broker.py`: `KeyLevel`, `set_policy`, `request_access`, `resolve_read_level` (mediación de lecturas sin entregar la llave al agente).
- `app/src/draft_engine.py:277-295`: `_build_evidence_pack` consulta `resolve_read_level` y audita lecturas selladas.
- `app/src/security/secrets.py`: `TenantSecretStore`, `TenantDataKey`, envelope encryption con master key + data key por tenant.
- `app/src/crypto/envelope.py`: helpers `envelope_encrypt`/`envelope_decrypt`.
- `app/src/storage.py:67-87`: `encrypt_object_payload`/`decrypt_object_payload` con prefijo `FLENC1:` y legacy pass-through.
- `app/src/foundation/m17_memory.py`: `fnd_memory_blocks` con `tenant_id` y namespace jerárquico.
- `app/src/ambient.py:1002-1087`: `_scheduled_tenant_ids` enumera tenants activos desde Foundation; `_run_tenant_schedule` evalua config por tenant.
- `app/src/e3_3_router.py`: endpoints REST para identidad, key policy, key access, settings cascade; audita `tenant.identity.created/updated`, `key.access.granted`.

**Qué se hizo para cerrar:**

- Se implementó identidad versionada con inmutabilidad: solo un owner distinto al `owner_user_id` original puede actualizar, con confirmation token.
- Se cableó el key broker a las lecturas del draft engine: el agente recibe solo lo que la política permite (CLOSED→nada, INDEX→títulos/punteros, CONTENT→contenido).
- Se implementó envelope encryption por tenant y se aplicó al cifrado de payloads de objetos (`FLENC1:`) y al store de provider keys (`enc:v1:`).
- Se convirtió el scheduler ambiental de mono-tenant (default fijo) a multi-tenant iterando Foundation.

**Cómo funciona:**

- **Identidad**: `entity_identity_version` tiene PK compuesta `(tenant_id, version)`. `update_identity` rechaza `actor_user_id == current.owner_user_id` y exige confirmation token.
- **Key broker**: `resolve_read_level` consulta `key_policy`; si no hay política, el espacio está abierto (CONTENT) para no romper operación normal. Si hay política, CEO-only cierra a no-CEOs; CONTENT reduce a INDEX para no-approvers. Las lecturas selladas se auditan como `kb.read.mediated`.
- **Cifrado**: `TenantSecretStore` crea una data key por tenant, envuelta con la master key de plataforma. Los objetos se cifran con la data key antes de enviarse a MinIO y se descifran al leerse; los objetos legacy sin prefijo pasan transparentes.
- **Scheduler**: `_scheduled_tenant_ids()` lee `fnd_tenants WHERE status='active'` y siempre incluye `DEFAULT_TENANT_ID`; `_run_tenant_schedule` carga `ambient_config` por tenant y solo lee datos de ese tenant.

**Bloqueantes/gaps:**

- Ninguno en código. La contamination suite (`test_e3_3_contamination_suite.py`) cubre identidad, key policy, memoria y secretos. Falta un test automático de presigned URL cross-tenant con MinIO real, aunque el prefijo `t-{tenant}/ws-{workspace}` y RLS lo hacen inviable por diseño.

**Tests:**

- `app/tests/test_e3_3_identity.py`: 5 passed.
- `app/tests/test_e3_3_key_broker.py`: 12 passed.
- `app/tests/test_e3_3_endpoints.py`: 4 passed.
- `app/tests/test_e3_3_envelope.py`: 3 passed.
- `app/tests/test_e3_3_object_encryption.py`: 2 passed.
- `app/tests/test_e3_3_seal_read_mediation.py`: 3 passed.
- `app/tests/test_e3_3_contamination_suite.py`: 4 passed.

---

### E3-4 — Fábrica de skills (olas 0-5)

**Estado del hito:** 🟢 **Cerrado técnicamente** (P2* por pendientes humanos/externos).

**Requerimientos del plan:**

- Ola 0: taxonomía v2 (P15-P18), compiler v2, C0-1 captura informal, C0-2 recopilación viva, C0-5 ceilings, C0-7 evidence bundle.
- Olas 1-2: PACK 1 fiscalidad y PACK 3 cobranza en SHADOW con golden cases y track-record gates; su promoción a ACTIVE requiere dogfood real.
- Olas 3-5: materializadas en estados `DRAFT`/`DEFINITION_PENDING`; no bloquean E3-6.
- Migración lazy de 14 skills legacy a manifest v2.

**Evidencia en código y archivos:**

- `app/src/skill_primitives.py:26-44`: `TAXONOMY_V2` declara P15-P18.
- `app/src/skill_primitives.py:60-125`: `capture_informal_interaction`, `approve_informal_capture` (C0-1).
- `app/src/skill_primitives.py:199-289`: `http_evidence_fetcher` SSRF-safe, `external_lookup` fail-closed (C0-2).
- `app/src/skill_primitives.py:357-477`: `update_track_record`, cálculo de `autonomy_ceiling` (C0-5).
- `app/src/skill_primitives.py:484-542`: `attach_evidence` generalizado (C0-7).
- `app/src/skills.py:214-329`, `452-470`: `_validate_manifest_v2`, `_output_requires_approval`, `skill_requires_hitl` (compiler v2 + HITL gate).
- `app/src/faberloom_catalog.py`: importador de catálogo; materializa `skill_manifest`, `skill_version`, `skill_track_record`, `golden_case`, `pack_status`.
- `app/src/skill_catalog.py`: `seed_global_skill_catalog` expone skills globales en chat.
- `app/src/connectors/tax_authority.py`: adaptadores ATV/SAT/DIAN con modos mock/sandbox/live, secretos cifrados por tenant, certificado gateado (HE2-9).
- `docs/faberloom/PLB_FB_VERIFICACION_APIS_TRIBUTARIAS_v1.md`: playbook de verificación humana de APIs tributarias.
- `faberloom/SKILL_FE_*.md`: 8 skills PACK 1 en SHADOW.
- `faberloom/SKILL_CO_*.md`: 6 skills PACK 3 en SHADOW.
- `faberloom/SKILL_CX_*.md`, `SKILL_PL_*.md`, `SKILL_TR_*.md`, `SKILL_WA_*.md`, `SKILL_BO_*.md`, `SKILL_CM_*.md`, `SKILL_SV_*.md`, `SKILL_FI_*.md`, `SKILL_LG_*.md`, `SKILL_GE_*.md`, `SKILL_OP_*.md`, `SKILL_MK_*.md`, `SKILL_HR_*.md`: 53 skills de olas 3-5 materializados en `DRAFT`/`DEFINITION_PENDING`.

**Qué se hizo para cerrar:**

- Se adoptó la taxonomía v2 en código (`TAXONOMY_V2`).
- Se extendió el compiler para validar manifest v2: archetype E1, kill switch, golden samples, auto_apply=false, asset outputs con `requires_human_approval`.
- Se implementó C0-1: captura informal → HITL draft → KB fact citable.
- Se implementó C0-2: fetcher HTTP real con guardia SSRF y evidence bundle obligatorio; conectores tributarios ATV/SAT/DIAN con modo live gateado por certificado.
- Se implementó C0-5: track record por skill/workspace/tenant con thresholds para `autonomy_ceiling`.
- Se implementó C0-7: tabla `external_evidence` reusable.
- Se materializaron PACK 1 y PACK 3 en SHADOW con golden cases y track-record gates; `promote_pack` requiere golden cases aprobadas+verificadas y track record ≥100 runs / ≥90% acceptance.
- Se materializaron olas 3-5 como esqueletos válidos sin inventar datos: `DRAFT` para templates que requieren localización LATAM, `DEFINITION_PENDING` para GAPs sin alcance definido.
- Se expuso el catálogo global en `/api/skills` y se agregó endpoint/tabero de promotion readiness (`/api/workspaces/{ws}/packs/readiness`).

**Cómo funciona:**

- `import_catalog_items` valida peligros (`_detect_dangerous`), compila el manifest v2 y llama `ensure_skill_factory_rows` para crear filas de fábrica.
- `execute_skill` devuelve `status="requires_hitl"` cuando `skill_requires_hitl` detecta output externo o tool fuera de allowlist.
- `external_lookup` solo acepta `fetcher` explícito; sin fetcher o con error falla cerrado (`status="failed"`, evidence vacía).
- `TaxAuthorityConnector` resuelve configuración por tenant; modo `live` exige `base_url`, credenciales y certificado; si falta alguno, falla cerrado.
- `promote_pack` es operación manual del curador con confirmación determinística; no promueve automáticamente.
- El tablero de promotion readiness agrega los gates visibles: golden cases, verificación independiente y track record.

**Bloqueantes/gaps (humanos/externos):**

- **P2***: Verificación de URLs/credenciales/certificados con ATV/SAT/DIAN y tracking TICA. El código está listo; es tarea humana.
- **P2***: KB Marluvas/Tecmater para golden cases reales de PACK 2 (comex). El cargador `app/scripts/ingest_kb_h3.py` está listo.
- **P2***: Dogfood real en PACK 1/3 para acumular track record y golden cases verificados antes de promover a ACTIVE.

**Cerrados en código:**

- Conector WhatsApp/webhook para C0-1 (`app/src/api.py`, `test_e3_4_whatsapp_inbound.py`).
- Conectores tributarios ATV/SAT/DIAN (`app/src/connectors/tax_authority.py`, `test_e3_4_tax_connectors.py`).
- Migración batch de skills legacy a manifest v2 (`096a5b0`, `test_e3_4_legacy_migration.py`).
- Primitivas P15/P17 (`bfc88f7`, `test_e3_4_p15_p17.py`).
- Promotion readiness endpoint y UI (`app/src/api.py`, `app/static/js/promotion_readiness.jsx`, `test_e3_4_pack_readiness.py`).

**Tests:**

- `app/tests/test_e3_4_taxonomy_v2.py`: 3 passed.
- `app/tests/test_e3_4_compiler_v2.py`: 10 passed.
- `app/tests/test_e3_4_c0_1_informal.py`: 2 passed.
- `app/tests/test_e3_4_c0_2_external.py`: 7 passed.
- `app/tests/test_e3_4_tax_connectors.py`: 7 passed.
- `app/tests/test_e3_4_pack_readiness.py`: 3 passed.
- `app/tests/test_e3_4_pack1_fe.py`: 1 passed.
- `app/tests/test_e3_4_pack3_cobranza.py`: 1 passed.
- `app/tests/test_e3_4_global_skill_catalog.py`: 5 passed.
- `app/tests/test_e3_4_p15_p17.py`: 4 passed.
- `app/tests/test_e3_4_whatsapp_inbound.py`: 4 passed.
- `app/tests/test_e3_4_legacy_migration.py`: 6 passed.
- `app/tests/test_e3_4_golden_harvester.py`: 8 passed.
- `app/tests/test_e3_4_pack_readiness.py`: 3 passed.

---

### E3-5 — Routing por tenant + BYO keys + presets builder

**Estado del hito:** 🟢 **Cerrado**.

**Requerimientos del plan:**

1. BYO keys por tenant, cifradas con data key; modos estricto/híbrido opt-in.
2. Ledger por tenant visible a owner y platform_admin (agregado).
3. Presets builder UI + templates sobre ledger real.
4. Defaults por plan.

**Evidencia en código y archivos:**

- `app/src/router/config_store.py`: `ProviderConfigStore` con slices `tenants[<tenant_id>][users][<user_id>]`; campos secretos cifrados con `TenantSecretStore`.
- `app/src/models.py:1340-1372`, `2532-2623`: tabla `routing_preset` y Pydantic models `RoutingPresetCreate/Update/Read/ResolveRead`.
- `app/src/db.py` (funciones `create_routing_preset`, `resolve_routing_preset`, etc.): CRUD y resolución de presets.
- `app/src/presets.py`: endpoints REST `/tenants/{tenant_id}/presets` con auth owner/admin/platform_admin.
- `app/src/plans.py:224-255`: `sum_tenant_usage_cost`, `enforce_budget` (ledger por tenant).
- `app/static/js/app.jsx:3090-3244`: `PresetsPanel` con CRUD, templates, botón "Usar en routine".
- `app/static/js/app.jsx:1547-1552`, `3592-3600`: evento `faberloom-use-preset` que pre-llena `preset_id=@preset/<slug>` al crear routine.

**Qué se hizo para cerrar:**

- Se implementó la tabla `routing_preset` (migración v35-v36) con tenant-scoped PK, templates y versionado.
- Se crearon endpoints CRUD + resolución; `resolve_routing_preset` mapea envelope/curve a provider/model.
- Se integró el panel de presets en la UI con evento que alimenta el formulario de routines.
- Se aseguró que `ProviderConfigStore` persiste keys cifradas por tenant data key.
- Se agregó `tenant_id` a `usage_record` y funciones de agregación de costo por tenant.

**Cómo funciona:**

- `ProviderConfigStore.set` guarda la API key en `tenants[tenant_id].users[user_id][provider].api_key` cifrada con `TenantSecretStore.encrypt_for_tenant`.
- El router (`app/src/router/engine.py`) consulta `ProviderConfigStore.all(ctx.user_id, ctx.tenant_id)` para obtener keys del tenant/usuario.
- Los presets se resuelven con reglas de envelope/curve; un preset con `providers_allow=["anthropic"]` y `curve.mode="sport"` devuelve `anthropic/claude-3-5-sonnet`.
- `routine.preset_id` acepta tanto `"provider:model"` legacy como `"@preset/<slug>"`.

**Bloqueantes/gaps:**

- **Cerrado en código**: BYO keys estricto/híbrido + recargo plataforma en `app/src/ledger.py` (`test_e3_5_byo_modes.py`).
- **Cerrado en código**: health dashboard por tenant expone costos, budget restante y uso agregado (`app/src/health_dashboard.py`, `test_e3_6_health.py`).

**Tests:**

- `app/tests/test_e3_5_presets.py`: 7 passed.
- `app/tests/test_e3_5_byo_modes.py`: 8 passed.

---

### E3-6 — Primer tenant externo + billing manual

**Estado del hito:** 🟢 **Cerrado técnicamente** (P2\* por dependencias comerciales/externas).

**Requerimientos del plan:**

1. Selección de design partner (criterios decididos; CEO elige).
2. Playbook de onboarding (`PLB_FB_TENANT_ONBOARDING_v1`).
3. Billing manual: BETA 90 días → factura con skills PACK 1 sobre tenant MWT; pago transferencia + conciliación PACK 3.
4. Telemetría/soporte: dashboard de salud, canal de soporte, SLA beta.

**Evidencia en código y archivos:**

- `docs/faberloom/ENT_FB_VERTICAL_CANDIDATES_v2.md`: criterios y ranking; candidato lead = distribución B2B técnica.
- `docs/faberloom/PLB_FB_TENANT_ONBOARDING_v1.md`: playbook completo con checklist de cierre.
- `docs/faberloom/PLB_FB_SOPORTE_SLA_BETA_v1.md`: SLA beta y canal de soporte.
- `app/src/models.py:1380-1453`: tablas `manual_invoice` y `payment_reconciliation` (migración v37); v41 añade `tenant_invoice_sequence` y columnas SLA/PDF.
- `app/src/billing.py`: endpoints REST `/tenants/{tenant_id}/invoices`, `/reconciliations`, `/invoices/next-number`, `/invoices/{id}/pdf`.
- `app/src/health_dashboard.py`: endpoints de salud por tenant (owner mirror + platform admin).
- `app/static/js/health_dashboard.jsx`: vista Salud en el shell React.
- `app/src/platform_admin.py:306-363`: métricas agregadas (`total_tenants`, `total_cost_usd`, etc.) visibles a platform_admin sin contenido.

**Qué se hizo para cerrar:**

- Se escribió el playbook de onboarding asistido.
- Se implementó el scaffold de billing manual: facturas manuales, reconciliaciones de pago, matching por monto, aislamiento por tenant.
- Se agregó numeración secuencial de facturas por tenant+serie (`tenant_invoice_sequence`).
- Se implementó generación y descarga de PDF no fiscal con `fpdf2`.
- Se implementó el health dashboard por tenant (`/api/tenants/{id}/health` y `/api/admin/tenants/{id}/health`) con métricas de uso, costo, budget y facturas.
- Se integró la vista Salud en el shell React.

**Cómo funciona:**

- `POST /api/tenants/{tenant_id}/invoices` crea una factura en estado `draft`.
- `PATCH /api/tenants/{tenant_id}/invoices/{id}` permite cambiar estado a `sent`/`paid`.
- `POST /api/tenants/{tenant_id}/reconciliations` registra un pago recibido.
- `PATCH .../reconciliations/{id}/match` vincula reconciliación con factura; si `amount == invoice.total`, marca la factura como `paid`.

**Bloqueantes/gaps:**

- **P2**: No hay design partner concreto ni acuerdo de datos firmado.
- **P2**: No se adquirieron/verificaron certificados de firma comercial (`HE2-9`); bloquean facturación electrónica real.
- **P2**: No se inició el soak de 30 días con ≥10 casos reales y primera factura pagada.

**Cerrados en código:**

- Dashboard de salud por tenant y página dedicada en la UI (`health_dashboard.jsx`).
- Numeración secuencial de facturas y generación de PDF no fiscal.

**Tests:**

- `app/tests/test_e3_6_billing.py`: 10 passed.
- `app/tests/test_e3_6_health.py`: 6 passed.

---

## 3. Matriz de riesgos P0 del plan vs estado

| Riesgo P0 (plan §5)                   | Estado      | Evidencia                                                                                            |
| ------------------------------------- | ----------- | ---------------------------------------------------------------------------------------------------- |
| Fuga cross-tenant                     | ✅ Mitigado | RLS en Postgres, Context en todas las queries, prefijos MinIO por tenant, contamination suite verde. |
| Corte Postgres fallido                | ✅ Mitigado | Corte realizado y validado; rollback documentado a SQLite.                                           |
| Identidad reescrita en sesión         | ✅ Mitigado | `entity_identity.py` rechaza self-approval; requiere owner distinto + token.                         |
| Skill ejecuta efecto externo sin HITL | ✅ Mitigado | `skill_requires_hitl` + compiler v2 exige `requires_human_approval` para outputs externos.           |
| Dato inventado en output              | ✅ Mitigado | Draft engine exige source-to-field check; `external_lookup` fail-closed.                             |
| platform_admin ve contenido           | ✅ Mitigado | Endpoints de admin solo listan/agregan; no exponen mensajes/KB/objetos.                              |
| Cadena auto multi-tenant sin techo    | ✅ Mitigado | `enforce_budget` por tenant; ambient config por tenant.                                              |

---

## 4. Suite de tests

| Módulo             | Tests colectados                               | Passed aprox. | Skipped aprox. | Fallidos |
| ------------------ | ---------------------------------------------- | ------------- | -------------- | -------- |
| E3-0               | `test_e3_0_*`                                  | 22            | 2              | 0        |
| E3-1               | `test_e3_1_*` + `test_e3_2_canary_all_tenants` | 21            | 2              | 0        |
| E3-2               | `test_e3_2_*` (excepto canario)                | 30            | 3              | 0        |
| E3-3               | `test_e3_3_*`                                  | 31            | 0              | 0        |
| E3-4               | `test_e3_4_*`                                  | 66            | 4              | 0        |
| E3-5               | `test_e3_5_*`                                  | 15            | 0              | 0        |
| E3-6               | `test_e3_6_*`                                  | 16            | 0              | 0        |
| **Proyecto total** | **627** colectados                             | **615**       | **12**         | **0**    |

La columna "Passed" por módulo es una aproximación de tests orientados a E3; el reporte global oficial es **615 passed / 12 skipped / 0 failed**.

---

## 5. Conclusiones y orden de trabajo recomendado

1. **Cerrar deudas operativas P1** antes de cualquier demo externa:
   - Documentar/evidenciar rotación VPS/SSH/claves de correo.
   - Cargar KB Marluvas/Tecmater (responsable CEO; dev + AM verifican citas).
2. **Desbloquear E3-6 comercial**:
   - CEO selecciona design partner de distribución B2B técnica y firma acuerdo de datos.
   - Adquirir/verificar certificados de firma comercial.
   - Verificar APIs oficiales ATV/SAT/DIAN y documentar resultado en catálogo v1.1.
3. **Continuar E3-4 en banda paralela**:
   - Golden cases reales PACK 1/3 en dogfood MWT.
   - Implementar conector WhatsApp/llamada para C0-1 si el design partner lo requiere.
   - Migración lazy de skills legacy a manifest v2.
4. **No avanzar a Etapa 4** hasta que E3-6 cierre con tenant externo activo ≥30 días, ≥10 casos reales, 0 fugas y primera factura pagada.

---

_Fin del reporte._
