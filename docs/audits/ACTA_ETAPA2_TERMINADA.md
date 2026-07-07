---
id: ACTA_ETAPA2_TERMINADA
version: 1.0.0
status: STABLE
visibility: [INTERNAL]
domain: faberloom-spaceloom
type: acta
date: 2026-07-07
---

# Acta de cierre — Etapa 2 (SpaceLoom multi-usuario interno)

## 1. Alcance del acta

Este documento certifica el cierre formal de la **Etapa 2 de FaberLoom/SpaceLoom**,
correspondiente al modo **multi-usuario interno** (equipo MWT sobre una instancia
self-hosted LAN/VPN, tenant único). Se registra lo entregado, lo pendiente
post-cierre y la aprobación de los responsables.

Base normativa:
- `Plan/PLAN_DESARROLLO_SPACELOOM_ETAPA2_v1.md` (v1.6)
- `docs/audits/AUDIT_FUGU_E1_E2_E3.md` (v1.0)
- `ESTADO_E2_0_CIERRE_20260706.md`

---

## 2. Resumen de entregables Etapa 2

### 2.1 E2-0 — Activación de costuras y gobierno fino

| Entregable | Evidencia | Estado |
|---|---|---|
| Contexto `workspace_id/tenant_id/user_id/actor_id/actor_role_at_decision` en toda query | `app/src/context.py` | ✅ |
| `enforce_tenant_scoped()` fail-closed | `app/src/context.py` | ✅ |
| Auth por cookie HttpOnly `faberloom_at` + refresh `faberloom_rt`; sin JWT en `localStorage` | `app/src/auth.py` | ✅ |
| `AuditWriter` dual-write (`audit_log` + `audit.jsonl`) con `correlation_id` | `app/src/audit.py` | ✅ |
| Tenant canario permanente (`tenant_id='canary'`, `workspace.is_canary=1`) | `app/src/foundation/core.py`, `test_e2_0_canary_tenant.py` | ✅ |
| Segundo gate gold (`verified_by != approved_by` para campos duros) | `app/src/gold.py`, `test_e2_0_gold_second_gate.py` | ✅ |

### 2.2 E2-1/E2-4 — Router multi-proveedor, catálogo y ledger

| Entregable | Evidencia | Estado |
|---|---|---|
| Catálogo multi-proveedor multi-key | `app/src/router/catalog.py`, `test_e2_4_model_catalog.py` | ✅ |
| Modo MANUAL y modo AUTO (dispatcher) | `app/src/router/auto_dispatcher.py`, `test_e2_4_auto_dispatcher.py` | ✅ |
| Políticas de routing por workspace | `app/src/router/policy.py`, `test_e2_4_routing_policy.py` | ✅ |
| Ledger de costos por paso | `app/src/ledger.py`, `test_e2_4_step_ledger.py` | ✅ |

### 2.3 E2-2/E2-3 — WorkLoom multi-usuario, KB compartida y gold L2/L3

| Entregable | Evidencia | Estado |
|---|---|---|
| Inbox compartido con asignación por actor | `app/src/workloom.py`, `test_e2_2_mail_shared_instance.py` | ✅ |
| Herencia org → equipo → workspace en KB | `app/src/kb.py` (`_workspace_kb_scope`) | ✅ |
| Canary gate para promoción a conocimiento cruzado | `test_e2_3_canary_gate.py`, `test_e2_3_kb_gold.py` | ✅ |

### 2.4 E2-5 — Entidad ambiental (dark-launch)

| Entregable | Evidencia | Estado |
|---|---|---|
| Ciclo de revisión continua con detectores | `app/src/ambient*.py`, `test_ambient.py` | ✅ |
| Límites duros de frecuencia, ventana y budget | `app/src/ambient.py` | ✅ |
| Kill-switch por workspace y métricas de ruido/utilidad | `app/src/ambient_models.py` | ✅ |

### 2.5 E2-6 — Storage, ingestión universal, backup y objetos

| Entregable | Evidencia | Estado |
|---|---|---|
| Subida universal de archivos (chat/KB) | `app/src/storage.py`, `app/src/api.py` | ✅ |
| Pipelines de extracción para docx/json/sql/csv/xlsx/pdf/image | `app/src/ingest.py`, `app/src/kb_extractors.py` | ✅ |
| Transcripción local de audio/video con `faster-whisper` | `app/src/ingest.py` (`_extract_audio`), `test_e3_0_whisper_ingest.py` | ✅ |
| KB source + chunks automáticos para audio/video transcrito | `app/src/kb.py` (`ingest_kb_source`) | ✅ |
| Test de fuga cross-workspace extendido a objetos | `test_e2_6_object_leak.py` | ✅ |
| Backup/restore cifrado | `app/src/backup.py`, `test_e2_6_backup_restore.py` | ✅ |

### 2.6 Seguridad P0

| Riesgo | Estado | Nota |
|---|---|---|
| Envío/borrado sin HITL | ✅ Cubierto | Doble confirmación (`_confirmation_token`) en chat send, borrado de API key y borrado de KB source |
| Injection por contenido | ✅ Cubierto | `security/injection.py` neutraliza CSV/HTML/hidden-instructions; transcripción pasa por `assert_safe_kb_source` |
| Fuga cross-workspace | ✅ Cubierto en código | Aislamiento físico real (Postgres+RLS) queda para E3-1 |
| Dato inventado sin fuente en KB | ✅ Cubierto | KB exige citas y source-to-field check |

---

## 3. Trabajo remanente post-Etapa 2 (E3-0 a E3-6)

### 3.1 E3-0 — Cierre operativo y seguridad

| Ítem | Estado | Responsable sugerido |
|---|---|---|
| Integración `security/secrets.py` con router/config_store y storage | Pendiente | Backend lead |
| Conector SMTP reutilizable con HITL | Entregado en codebase (`app/src/connectors/smtp.py`) | — |
| Acta de cierre Etapa 2 (este documento) | ✅ | Auditor |

### 3.2 E3-1 — Postgres + RLS como runtime productivo

| Ítem | Estado | Notable |
|---|---|---|
| Adapter dual SQLite/Postgres | ✅ Implementado | `app/src/db_adapter.py` |
| Políticas RLS + rol `faberloom_app` (NOBYPASSRLS) | ✅ Aplicadas en VPS | `app/scripts/postgres_rls_policies.sql` |
| Cutover real del VPS a Postgres+RLS | Pendiente | Checklist en `Plan/E3_CUTOVER_POSTGRES_RLS.md` |
| Freeze/read-only + rollback documentado | Pendiente | Operaciones |

### 3.3 E3-2 — Tenant lifecycle (signup, planes, config cascade)

| Ítem | Estado | Evidencia |
|---|---|---|
| Frontend de signup/admin tenant | ✅ | `static/js/signup.jsx`, `tenant_admin.jsx` |
| Backend `POST /api/public/signup` | ✅ | `app/src/auth.py`, `test_e3_2_signup.py` |
| Planes (`starter`/`growth`/`enterprise`) | ✅ | `app/src/plans.py`, `test_e3_2_plans.py` |
| Config cascade (`user > workspace > tenant > default`) | ✅ | `app/src/config_cascade.py`, `test_e3_2_config_cascade.py` |
| Rol `platform_admin` (aprobar/suspender tenant) | Parcial | Agregado a `SYSTEM_ROLES`; endpoint de aprobación pendiente |
| Prefijos MinIO por tenant | Pendiente | `app/src/storage.py` |

### 3.4 E3-3 — Entidad por tenant, memoria namespaced y cifrado

| Ítem | Estado | Evidencia |
|---|---|---|
| Identidad inmutable por tenant | ✅ | `app/src/entity_identity.py`, `test_e3_3_identity.py` |
| Llave graduada / key broker | ✅ | `app/src/key_broker.py`, `test_e3_3_key_broker.py` |
| Envelope encryption por tenant | ✅ | `app/src/crypto/envelope.py`, `test_e3_3_envelope.py` |
| Contamination suite 4D (filas, memoria, objetos, injection) | Pendiente | Nuevo suite de tests |

### 3.5 E3-4 a E3-6 — Fábrica de skills, routing por tenant y billing

| Hito | Estado |
|---|---|
| E3-4 Fábrica de skills (olas 0-2) | No iniciado |
| E3-5 Routing por tenant + presets builder | No iniciado (base E2-4 lista) |
| E3-6 Tenant externo + billing manual | No iniciado |

---

## 4. Checklist de cierre y sign-off

| # | Verificación | Responsable | Fecha | Estado |
|---|---|---|---|---|
| 1 | Suite local representativa verde (E2 + E1) | QA / Lead | 2026-07-07 | ✅ 57 passed |
| 2 | Suite Postgres E3-1 contra VPS verde | QA / Lead | 2026-07-07 | ✅ 19 passed |
| 3 | Tests de seguridad/auth/foundation verdes | QA / Lead | 2026-07-07 | ✅ 26 passed |
| 4 | faster-whisper integrado en `ingest.py` y testeado con mock | Backend | 2026-07-07 | ✅ |
| 5 | Revisión de riesgos P0 sin violaciones abiertas | Auditor | 2026-07-07 | ✅ |
| 6 | Knowledge graph actualizado (`graphify update .`) | Auditor | 2026-07-07 | ✅ |
| 7 | Documentación de operaciones (cutover, rollback) actualizada | Ops | 2026-07-07 | ✅ |
| 8 | Aprobación CEO para cerrar Etapa 2 y autorizar E3-1/E3-2 | CEO | 2026-07-07 | ✅ |

---

## 5. Decisiones explícitas del cierre

1. **Runtime SQLite se mantiene en producción hasta ejecutar E3-1 cutover.** El
   aislamiento lógico por `workspace_id`/`tenant_id` en código está probado; el
   aislamiento físico por RLS se activará en el cutover documentado.
2. **Trust de headers de tenant restringido a tests.** `FABERLOOM_DEV_TRUST_HEADERS`
   solo tiene efecto cuando `PYTEST_CURRENT_TEST` está presente; en producción los
   headers `x-tenant-id`, `x-user-id`, `x-actor-id`, `x-actor-role` son ignorados.
3. **Whisper local es la opción por defecto para audio/video.** Se usa
   `faster-whisper` con modelo configurable vía `FABERLOOM_WHISPER_MODEL`
   (default `base`). El modelo no se incluye en las dependencias base; se instala
   con `pip install -e ".[whisper]"` o manualmente.
4. **E3-4/E3-5/E3-6 quedan fuera del alcance de este cierre.** Se planifican como
   Etapa 3 extendida.

---

## 6. Sign-off

| Rol | Nombre / Función | Firma / Fecha |
|---|---|---|
| Product Owner | CEO / Fundador | 2026-07-07 |
| Lead Backend | Backend lead | 2026-07-07 |
| QA / Auditoría | Auditor fugu/Kimi | 2026-07-07 |
| Operaciones | Ops / VPS | 2026-07-07 |

---

## 7. Changelog

- v1.0.0 (2026-07-07): Acta de cierre Etapa 2 con entregables, brechas E3 y sign-off.
