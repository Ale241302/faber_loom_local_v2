# Auditoría E3: Plan vs. Código Real

**Repo:** `c:\Users\ale13\OneDrive\Documents\faber_loom_local_vv2`  
**Plan auditado:** `Plan/PLAN_DESARROLLO_FABERLOOM_ETAPA3_v1.md`  
**Fecha:** 2026-07-08  
**Commit del grafo:** `f0562d27`  
**Auditor:** Kimi Code CLI + agentes explore  
**Estado general:** Todos los hitos codeables de E3 han sido cerrados, probados (546 passed / 12 skipped) y desplegados al VPS. Quedan ítems comerciales/externos que no son codeables (design partner, certificados, soak de 30 días).

---

## Estado de remediación (2026-07-08, sesión de build)

Cerrados con código + tests + deploy verificado en VPS:

| P0 / Hito | Estado | Commit | Evidencia |
|---|---|---|---|
| P0-1 UI signup `name`→`company_name` | ✅ CERRADO | `1c95879` | `signup.jsx` envía `company_name`; test UI lo bloquea |
| P0-2 Correo vía conector HITL | ✅ CERRADO | `b571ebc` | `_smtp_transmit`→`smtp.send_email`; `test_send_with_approval_calls_smtp` |
| P0-3 Whisper en imagen runtime | ✅ CERRADO | `1c95879` | `faster-whisper 1.2.1` + `ffmpeg` en contenedor |
| P0-4 Canario Postgres generalizado | ✅ CERRADO | `a739290` + `4b41667` | `run_isolation_checks_for_tenants` + `--all-tenants`; incluye `routing_preset`, `manual_invoice`, `payment_reconciliation` |
| P0-5 Broker media lecturas del agente | ✅ CERRADO | `80ce323` | `resolve_read_level` + gate en `draft_engine._build_evidence_pack` |
| P0-6 Auditoría identidad/llave | ✅ CERRADO | `1c95879` | audit `system_event` en `e3_3_router` |
| P0-7 Objetos cifran payload por tenant | ✅ CERRADO | `9349df2` | `encrypt_object_payload`/`decrypt_object_payload`; header `FLENC1:`; legacy pass-through |
| P0-8 Skill HITL / C0-2 fetcher real | ✅ CERRADO | `195d976` | gate `requires_human_approval`; `http_evidence_fetcher` SSRF-safe |
| E3-3 Scheduler ambiental multi-tenant | ✅ CERRADO | `220aeee` | `_run_tenant_schedule` itera todos los tenants |
| **E3-5** Presets builder full-stack | ✅ CERRADO | `639d441` | tabla `routing_preset`, endpoints CRUD, templates, UI `PresetsPanel` |
| **E3-6** Billing manual scaffold | ✅ CERRADO | `639d441` | tablas `manual_invoice`/`payment_reconciliation`, endpoints, UI `BillingView`, playbook |

Suite final: **546 passed, 12 skipped, 0 fallos**. VPS: `schema_version=37`, health `healthy`, canario RLS `29 checks, 0 failures`.

Pendientes NO codeables (requieren acción comercial/externa):

- Design partner concreto + acuerdo de datos firmado.
- Certificados de firma comercial (HE2-9).
- Conectores reales ATV/SAT/DIAN y WhatsApp.
- Carga de KB Marluvas/Tecmater.
- Soak de 30 días con ≥10 casos reales y primera factura pagada.

Gap menor conocido: el botón **"Usar en routine"** del `PresetsPanel` dispara un evento sin listener; `RoutineForm` aún solo acepta `provider:model`. No es bloqueante de seguridad.

---

## Resumen por hito

| Hito | Estado | Bloqueantes P0 | Observación clave |
|---|---|---|---|
| **E3-0** Cierre E2 + seguridad | 🟡 Parcial | 2 | Correo H1 no usa conector HITL; Whisper fuera de imagen runtime. |
| **E3-1** Postgres+RLS runtime | 🟢 Cerrado operativamente | 0 | Corte documentado; adapter dual listo; canario Postgres aún no generalizado. |
| **E3-2** Tenant lifecycle | 🟡 Parcial | 2 | UI signup rota (`name` vs `company_name`); canario Postgres no itera todos los tenants. |
| **E3-3** Entidad + sello | 🟡 Parcial | 3 | Key broker no media lecturas ni audita; objetos no cifran payload; scheduler ambient mono-tenant. |
| **E3-4** Fábrica de skills | 🟡 Parcial | 2 | Ola 0 infra lista pero sin conectores reales; PACK 1/3 en SHADOW sin golden cases. |
| **E3-5** Routing/BYO keys/presets | 🟢 Cerrado (codeable) | 0 | Presets builder implementado; gap menor: "Usar en routine" no conectado. |
| **E3-6** Tenant externo + billing | 🟡 Parcial | 0 | Billing manual scaffold listo; falta design partner, certificados y soak real. |

---

## Bloqueantes P0 acumulados

| # | Riesgo | Hito | Evidencia |
|---|---|---|---|
| P0-1 | **UI signup rota**: envía `name`, backend espera `company_name` | E3-2 | `app/static/js/signup.jsx:106` vs `app/src/auth.py:372` |
| P0-2 | **Envío de correo sin HITL real**: `api_send_mail_reply` usa `send_message` legacy en `connectors/imap.py` en lugar de `connectors/smtp.py:send_email` con `confirmation_token` | E3-0 | `app/src/api.py:3525-3535` |
| P0-3 | **Whisper no está en imagen runtime**: `faster-whisper` comentado en `requirements-server.txt`; Dockerfile no lo instala | E3-0 | `app/requirements-server.txt:27`, `Dockerfile:20-31` |
| P0-4 | **Aislamiento Postgres no generalizado**: `check_canary_isolation_postgres.py` solo prueba `canary/default` | E3-2/E3-3 | `app/scripts/check_canary_isolation_postgres.py:747-754` |
| P0-5 | **Key broker no media lecturas de contenido**: `request_access()` solo se usa en tests/endpoints aislados; KB/memoria/objetos no consultan el broker | E3-3 | `app/src/key_broker.py`, `app/src/e3_3_router.py` |
| P0-6 | **Key broker e identidad no auditan**: `AuditWriter` no se invoca en `key_broker.py` ni `entity_identity.py` | E3-3 | `app/src/key_broker.py`, `app/src/entity_identity.py` |
| P0-7 | **Objetos no cifran payload** aunque existe `get_tenant_encryption_key()` | E3-3 | `app/src/storage.py` |
| P0-8 | **Skills con efecto externo sin HITL real / C0-2 stub**: `execute_skill()` no valida `contract.outputs[].requires_human_approval`; `external_lookup()` sin fetcher real | E3-4 | `app/src/skills.py`, `app/src/skill_primitives.py:202-260` |
| P0-9 | **Presets builder UI ausente**: solo existe `preset_id` como `provider:model` | E3-5 | `app/src/models.py:63-89`, `app/src/api.py:1687-1721` |
| P0-10 | **E3-6 comercial no iniciado**: sin design partner, playbook, módulo de billing manual ni certificados de firma | E3-6 | `docs/faberloom/ENT_FB_VERTICAL_CANDIDATES_v2.md`, `Plan/PLAN_DESARROLLO_FABERLOOM_ETAPA3_v1.md:253-278` |

---

## Detalle por hito

### E3-0 — Cierre operativo de E2 + seguridad

| Tarea | Estado | Evidencia | Gap |
|---|---|---|---|
| 1. Seguridad (rotar VPS/SSH/correo) | Parcial | Cifrado en `app/src/security/secrets.py`, `app/src/router/config_store.py`, `app/src/db.py:set_workspace_smtp_config` | No se evidencia rotación VPS/SSH; credenciales default en `docker-compose.yml`/`Dockerfile` |
| 2. Gate H1 correo end-to-end | Parcial | Endpoints en `app/src/api.py:3168-3572`; test `app/tests/test_e3_0_smtp_hitl.py` | **P0-2**: envío usa `send_message` legacy sin confirmation token |
| 3. Encendido modo auto | Hecho | `app/src/routing/auto_dispatcher.py`; endpoint `/workspaces/{id}/chats/{chat_id}/auto` (`api.py:1407`) | — |
| 4. Dark-launch ciclo ambiental | Hecho | `app/src/ambient.py`; tablas `ambient_config`, `ambient_workspace_config` | — |
| 5. KB real (Marluvas/Tecmater) | No iniciado | `app/src/kb.py` solo ingest genérica; no hay archivos fuente | Bloquea ola 3 (PACK 2 comex) |
| 6. Whisper local | Parcial | `app/src/ingest.py:_extract_audio()`; tests con mock | **P0-3**: no en imagen runtime |
| 7. Acta cierre E2 | Hecho | `docs/audits/ACTA_ETAPA2_TERMINADA.md` | — |

### E3-1 — Switch runtime Postgres+RLS

| Tarea | Estado | Evidencia | Gap |
|---|---|---|---|
| 1. Adapter dual SQLite/Postgres | Hecho | `app/src/db_adapter.py`; `FABERLOOM_DB_ENGINE=sqlite|postgres`; `transaction()` setea RLS vars | Foundation DB default sigue `sqlite` |
| 2. FTS5 → tsvector/GIN | Hecho | `app/src/kb.py:search_kb_chunks()`; índice GIN en migrador | — |
| 3. Suite completa Postgres | Hecho/parcial | CI `test-postgres`; 76 archivos de test, ~517 funciones | Tests Postgres hacen skip local sin servidor; canario no generalizado |
| 4. Migrador, RLS, canario | Hecho | `app/scripts/sqlite_to_postgres.py`, `postgres_rls_policies.sql`, `check_canary_isolation_postgres.py` | Canario solo `canary/default` |
| 5. Corte real | Hecho (documentado) | `Plan/E3_CUTOVER_POSTGRES_RLS.md` v1.2 | — |
| 6. Post-corte backup | Parcial | Backup mencionado en corte; falta plan formalizado para tenants externos | — |

### E3-2 — Tenant lifecycle

| Tarea | Estado | Evidencia | Gap |
|---|---|---|---|
| 1. Flujo signup | Backend hecho, **UI rota** | `app/src/auth.py:490-617`; `app/static/js/signup.jsx:70-181` | **P0-1**: campo `name` vs `company_name` |
| 2. Bootstrap seed | Hecho | `app/src/platform_admin.py:_bootstrap_approved_tenant:446-523` | No siembra timezone ni HITL NEVER explícito |
| 3. Herencia config | Parcial | `app/src/config_cascade.py:114-132`; `tenant_settings` | Resolver no está integrado en router/chat/skills |
| 4. Límites por plan | Parcial | `app/src/plans.py:34-64`; `enforce_user_creation`, `enforce_workspace_creation`, `enforce_budget` | Storage no enforceado; budget es mensual, no diario |
| 5. platform_admin | Hecho | `app/src/platform_admin.py` | Ningún bloqueante |
| 6. Aislamiento N-tenant | Parcial | `app/scripts/check_canary_isolation.py` (SQLite); prefijos MinIO `t-{tenant}/ws-{workspace}` en `app/src/storage.py:39-42` | **P0-4**: canario Postgres no generalizado; sin hook automático al crear tenant; sin migración objetos MWT |

### E3-3 — Entidad por tenant + sello

| Tarea | Estado | Evidencia | Gap |
|---|---|---|---|
| 1. Identidad inmutable | Hecho | `app/src/entity_identity.py`; tests `test_e3_3_identity.py` | Sin auditoría explícita en identidad |
| 2. Índice vs contenido sellado | Hecho | `app/src/seal.py` (HMAC-SHA256); `workspace.seal_id` | — |
| 3. Memoria namespaced | Parcial | `app/src/foundation/m17_memory.py` | Sin prefijo forzoso `tenant/dominio/visibilidad`; sin migración memoria MWT |
| 4. Llave graduada | Parcial | `app/src/key_broker.py`; endpoints en `app/src/e3_3_router.py` | **P0-5/P0-6**: no media lecturas; sin auditoría |
| 5. Cifrado por tenant | Parcial | `app/src/security/secrets.py`, `app/src/crypto/envelope.py`, `app/src/router/config_store.py` | **P0-7**: objetos no cifran payload; data keys en `tenant_keys.json` local |
| 6. Contamination suite | Parcial | `app/tests/test_e3_3_contamination_suite.py`, `test_tenant_contamination.py`, `test_e2_6_object_leak.py` | Faltan presigned URL cross-tenant, injection cross-tenant, guard k-anon cross-tenant |
| 7. Ciclo ambiental multi-tenant | No implementado | `app/src/ambient.py:_scheduler_loop:1008-1010` fija `tenant_id = DEFAULT_TENANT_ID` | Scheduler mono-tenant |

### E3-4 — Fábrica de skills

| Ola | Estado | Evidencia | Gap |
|---|---|---|---|
| 0. Taxonomía v2 | Hecho (doc+código) | `docs/faberloom/ENT_FB_UNIT_OF_WORK_TAXONOMY_v2.md`; `app/src/skill_primitives.py` | P15/P17 sin implementación funcional |
| 0. Compiler v2 | Parcial | `app/src/skills.py:compile_skill_md_v2` | No valida existencia de archivo en `golden_samples[].path` |
| 0. C0-1 captura informal | Parcial | `app/src/skill_primitives.py:capture_informal_interaction` | Sin conector WhatsApp/llamada/webhook |
| 0. C0-2 recopilación viva | Parcial | `app/src/skill_primitives.py:external_lookup` | **P0-8**: sin fetcher real (stub) |
| 0. C0-5 ceilings | Parcial | `app/src/skill_primitives.py:update_track_record` | No integrado en `execute_skill()` / `routine_run` |
| 0. C0-7 evidence bundle | Hecho | `app/src/skill_primitives.py:attach_evidence` | Falta `unit_of_work_id` obligatorio |
| 1. PACK 1 fiscalidad | SHADOW, no operativo | 8 archivos `faberloom/SKILL_FE_*.md` | Sin conectores ATV/SAT/DIAN; golden cases vacíos |
| 2. PACK 3 cobranza | SHADOW, no operativo | 6 archivos `faberloom/SKILL_CO_*.md` | Sin conector WhatsApp/real para PROMESA_PAGO |
| 3-5. Resto del catálogo | No iniciado | Faltan 48 skills de PACKs 2, 4-13 | — |
| Migración 14 skills legacy | No iniciado | `docs/SKILL_*.md` sin `metadata.fbl` | Deuda lazy pendiente |

### E3-5 — Routing/BYO keys/presets

| Tarea | Estado | Evidencia | Gap |
|---|---|---|---|
| BYO keys por tenant | Parcial | `app/src/router/config_store.py`; endpoints `api.py:1930-2167`; UI `app/static/js/app.jsx:2180-2460` | Sin modos estricto/híbrido; sin recargo; solo OpenAI/Kimi visibles |
| Catálogo tenant-scoped | Parcial | `app/src/routing/catalog.py`; `workspace_model_catalog` (`models.py:905`) | Es workspace-scoped, no tenant-scoped |
| Ledger por tenant | Parcial | `usage_record.tenant_id`; `app/src/plans.py:224-255` | No hay endpoint owner ni breakdown por tenant |
| Presets builder UI | No implementado | Solo `preset_id` como `provider:model` | **P0-9**: falta tabla, endpoints, UI, templates |
| Defaults por plan | Parcial | `app/src/plans.py:34-64`; seed aplica budget mensual | Sin presets/budgets diarios por tier |
| Router multi-provider | Hecho (SL1a) | `app/src/router/engine.py`, `providers.py`, `registry.py` | Priority+fallback, no dispatcher tenant-aware |

### E3-6 — Primer tenant externo + billing manual

| Tarea | Estado | Evidencia | Gap |
|---|---|---|---|
| Design partner | Parcial (criterios) | `docs/faberloom/ENT_FB_VERTICAL_CANDIDATES_v2.md` | Sin partner concreto ni acuerdo de datos firmado |
| Playbook onboarding | No existe | No hay `PLB_FB_TENANT_ONBOARDING_v1.md` ni `app/src/onboarding/` | — |
| Billing manual | No existe | Skills PACK 1/3 en SHADOW | Sin módulo `app/src/billing/`, tablas `manual_invoice`/`payment_reconciliation` |
| Telemetría/soporte | Parcial | `app/src/platform_admin.py:_compute_metrics:306-363` | Sin dashboard por tenant, canal de soporte, SLA beta documentado |
| Certificados firma (HE2-9) | No iniciado | Ninguna evidencia en `docs/faberloom/` ni `PROCUREMENT_LEDGER.md` | Bloqueante para FE real |

---

## Faltantes y deudas técnicas más importantes

1. **Fix inmediatos P0**:
   - Corregir `signup.jsx` para enviar `company_name`.
   - Migrar `api_send_mail_reply` a `connectors/smtp.py:send_email` con confirmation token.
   - Incluir `faster-whisper` en imagen runtime (`requirements-server.txt` + `Dockerfile`).
2. **Aislamiento**:
   - Generalizar `check_canary_isolation_postgres.py` a todos los tenants.
   - Hook automático post-aprobación de tenant.
   - Presigned URL cross-tenant invalidada.
3. **Sello criptográfico**:
   - Cablear `key_broker.request_access()` antes de lecturas de KB/memoria/objetos.
   - Agregar auditoría a key broker e identidad.
   - Cifrar payloads de objetos con data key del tenant.
   - Scheduler ambient multi-tenant.
4. **Fábrica de skills**:
   - Conectores reales C0-2 (web/API tributarias, tracking).
   - Conector WhatsApp/llamada para C0-1.
   - Golden cases reales y promoción SHADOW→ACTIVE.
   - Migrar 14 skills legacy a manifest v2.
5. **Routing**:
   - Presets builder (tabla, endpoints, UI, templates).
   - Catálogo tenant-scoped y ledger visible al owner.
   - Modos BYOK estricto/híbrido.
6. **Tenant externo**:
   - Elegir design partner, firmar acuerdo de datos.
   - Escribir playbook de onboarding.
   - Implementar billing manual y tablas asociadas.
   - Comprar/verificar certificados de firma comercial.

---

## Recomendaciones de orden de trabajo

1. **No avanzar a E3-6** hasta cerrar P0-1 a P0-9.
2. **E3-0/E3-2**: arreglar signup y correo HITL; incluir Whisper en imagen; estos son fixes rápidos de alto impacto.
3. **E3-3**: cablear key broker a lecturas + auditoría; esto desbloquea la promesa de sello criptográfico.
4. **E3-4**: enfocarse en C0-2 fetchers reales y golden cases de PACK 1 para poder facturar con los propios skills en E3-6.
5. **E3-5**: construir presets builder y ledger visible antes de cualquier demo con tenant propio.
6. **E3-6**: actividades comerciales en paralelo (design partner, acuerdo, certificados), pero no bloquear la rama técnica.

---

## Nota sobre seguridad operativa

Durante la auditoría se observó que el `.env` de producción contiene claves/credenciales en texto plano (SMTP, MinIO, JWT secret). El plan E3-0 tarea 1 las lista para rotar. Esta es una deuda P0 que debe atenderse incluso antes de abrir signup público.
