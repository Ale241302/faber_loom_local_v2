---
id: ACTA_ETAPA3_CIERRE_PARCIALES
version: 1.0.0
status: STABLE
visibility: [INTERNAL]
domain: faberloom-spaceloom
type: acta
date: 2026-07-10
---

# Acta de cierre parcial — Etapa 3 (FaberLoom/SpaceLoom)

## 1. Alcance del acta

Este documento certifica el **cierre parcial de la Etapa 3** de FaberLoom/SpaceLoom en la rama `e3-cierre-parciales`. Se cierran los hitos codeables E3-1 a E3-6 y las deudas operativas instrumentables de E3-0; quedan pendientes ítems que requieren acción humana/externa (credenciales, archivos de proveedor, tenant real, soak comercial).

Base normativa:
- `Plan/PLAN_DESARROLLO_FABERLOOM_ETAPA3_v1.md`
- `docs/audits/AUDIT_E3_DETAILED_CLOSURE_REPORT_20260708.md`
- `docs/audits/AUDIT_E3_PLAN_VS_CODE_20260708.md`
- `docs/audits/AUDIT_E3_CIERRE_PARCIALES_20260710.md`

---

## 2. Entregables cerrados

### 2.1 E3-1 — Postgres + RLS como runtime productivo

| Entregable | Evidencia | Estado |
|---|---|---|
| Adapter dual SQLite/Postgres | `app/src/db_adapter.py` | ✅ |
| Migrador con dry-run y validación | `app/scripts/sqlite_to_postgres.py` | ✅ |
| Políticas RLS por `tenant_id` / `workspace_id` | `app/scripts/postgres_rls_policies.sql` | ✅ |
| Tests de adapter y RLS canario | `test_e3_1_postgres_adapter.py`, `test_e3_1_rls_canary.py` | ✅ |

### 2.2 E3-2 — Tenant lifecycle + N-tenant

| Entregable | Evidencia | Estado |
|---|---|---|
| Signup UI + backend | `app/src/auth.py`, `static/js/signup.jsx`, `test_e3_2_signup.py`, `test_e3_2_signup_ui.py` | ✅ |
| Planes y límites | `app/src/plans.py`, `test_e3_2_plans.py` | ✅ |
| Config cascade | `app/src/config_cascade.py`, `test_e3_2_config_cascade.py` | ✅ |
| platform_admin (aprobar/suspender tenants) | `app/src/platform_admin.py` | ✅ |
| Prefijos MinIO por tenant + script de migración | `app/src/storage.py`, `app/scripts/migrate_minio_objects_to_tenant_prefix.py`, `test_e3_2_minio_object_migration.py` | ✅ |

### 2.3 E3-3 — Entidad por tenant, memoria namespaced y cifrado

| Entregable | Evidencia | Estado |
|---|---|---|
| Identidad inmutable por tenant | `app/src/entity_identity.py`, `test_e3_3_identity.py` | ✅ |
| Key broker graduado | `app/src/key_broker.py`, `test_e3_3_key_broker.py` | ✅ |
| Envelope encryption por tenant | `app/src/crypto/envelope.py`, `test_e3_3_envelope.py` | ✅ |
| Contamination suite 4D | `test_e3_3_contamination_suite.py`, `test_e3_3_endpoints.py` | ✅ |

### 2.4 E3-4 — Fábrica de skills / comex (olas 0-2)

| Entregable | Evidencia | Estado |
|---|---|---|
| Taxonomía v2 y compiler v2 | `app/src/skills.py`, `test_e3_4_compiler_v2.py`, `test_e3_4_taxonomy_v2.py` | ✅ |
| C0-1/C0-2 (informal + external web evidence) | `test_e3_4_c0_1_informal.py`, `test_e3_4_c0_2_external.py` | ✅ |
| Evidence bundle y track record | `test_e3_4_global_skill_catalog.py` | ✅ |
| PACK 1/3 en shadow | `test_e3_4_pack1_fe.py`, `test_e3_4_pack3_cobranza.py` | ✅ |
| Golden Harvester | `test_e3_4_golden_harvester.py` | ✅ |
| Conectores tributarios como adaptadores | `test_e3_4_tax_connectors.py` | ✅ |

### 2.5 E3-5 — Routing por tenant + presets builder

| Entregable | Evidencia | Estado |
|---|---|---|
| Presets builder full-stack | `test_e3_5_presets.py` | ✅ |
| BYO keys estricto/híbrido + recargo plataforma | `test_e3_5_byo_modes.py` | ✅ |
| Ledger por tenant | `app/src/ledger.py` | ✅ |
| Wire "Usar en routine" | commits previos de UI | ✅ |

### 2.6 E3-6 — Tenant externo + billing manual

| Entregable | Evidencia | Estado |
|---|---|---|
| Health dashboard (owner mirror + platform admin) | `app/src/health_dashboard.py`, `test_e3_6_health.py` | ✅ |
| Numeración secuencial de facturas por tenant | `app/src/db.py`, `test_e3_6_billing.py` | ✅ |
| Generación/descarga de PDF no fiscal | `app/src/billing.py`, `test_e3_6_billing.py` | ✅ |
| Vista Salud en shell React | `app/static/js/health_dashboard.jsx`, `app/static/js/app.jsx` | ✅ |

### 2.7 E3-0 — Deudas operativas instrumentables

| Entregable | Evidencia | Estado |
|---|---|---|
| Runbook rotación VPS/SSH/correo | `docs/OPERACION_VPS_E3.md` | ✅ |
| Script de ingest KB H3 | `app/scripts/ingest_kb_h3.py`, `test_e3_0_kb_h3.py` | ✅ |
| Script de migración MinIO a prefijo tenant | `app/scripts/migrate_minio_objects_to_tenant_prefix.py`, `test_e3_2_minio_object_migration.py` | ✅ |

---

## 3. Trabajo remanente post-cierre parcial

| Ítem | Tipo | Responsable | Nota |
|---|---|---|---|
| Ejecutar rotación VPS/SSH/correo y dejar evidencia | Operativo | Ops / CEO | Usar `docs/OPERACION_VPS_E3.md`. |
| Conseguir y cargar archivos KB H3 reales | Externo / CEO | CEO | Usar `app/scripts/ingest_kb_h3.py`. |
| Ejecutar migración real de objetos MWT en MinIO | Operativo | Ops / Backend | Usar `app/scripts/migrate_minio_objects_to_tenant_prefix.py`. |
| Verificar APIs ATV/SAT/DIAN y documentar resultado | Externo / AM | AM / CEO | Actualizar `docs/faberloom/PLB_FB_VERIFICACION_APIS_TRIBUTARIAS_v1.md`. |
| Conseguir design partner B2B técnico y acuerdo de datos | Comercial | CEO | Gate para E3-6 comercial. |
| Soak ≥30 días con tenant externo real | Comercial / QA | QA / Ops | Requisito para declarar E3-6 cerrado. |
| Certificados de firma comercial | Legal / CEO | CEO | Necesario para facturación fiscal post-beta. |
| Promoción PACK 1/3 de SHADOW a ACTIVE | Producto / QA | Product / QA | Requiere golden cases reales. |
| Olas 3-5 de E3-4 (corredores adicionales) | Producto / Backend | Backend | Backlog de Etapa 4 o continuación E3. |

---

## 4. Checklist de cierre y sign-off

| # | Verificación | Responsable | Fecha | Estado |
|---|---|---|---|---|
| 1 | Suite completa verde (615 passed / 12 skipped / 0 failed) | QA / Auditor | 2026-07-10 | ✅ |
| 2 | Todos los bloques 1-8 commiteados atómicamente | Auditor | 2026-07-10 | ✅ |
| 3 | Revisión de riesgos P0 sin violaciones abiertas | Auditor | 2026-07-10 | ✅ |
| 4 | Knowledge graph actualizado (`graphify update .`) | Auditor | 2026-07-10 | ✅ |
| 5 | Documentos de auditoría y acta creados | Auditor | 2026-07-10 | ✅ |
| 6 | Pendientes humanos/externos explícitamente listados | Auditor | 2026-07-10 | ✅ |
| 7 | Aprobación CEO para cerrar cierre parcial E3 y autorizar fase comercial/operativa | CEO | — | ☐ |

---

## 5. Decisiones explícitas del cierre

1. **Se declara E3 "cerrada técnicamente"**; la etapa comercial/operativa (E3-6 externo) arranca solo después de conseguir un design partner y cumplir 30 días de soak sin fugas.
2. **SQLite sigue soportado para dev/test**; Postgres+RLS es el runtime productivo objetivo. El cutover real ya fue documentado en `Plan/E3_CUTOVER_POSTGRES_RLS.md`.
3. **No se abre signup público (E4)** hasta que E3-6 cierre con tenant externo ≥30 días y 0 fugas.
4. **La facturación actual es "no fiscal beta"**; la validez tributaria requiere certificados de firma e integración con APIs oficiales, fuera del alcance de este cierre.
5. **Los pendientes humanos/externos se marcan `[PENDIENTE — NO INVENTAR]`** y no se codean datos/respuestas ficticias.

---

## 6. Sign-off

| Rol | Nombre / Función | Firma / Fecha |
|---|---|---|
| Product Owner | CEO / Fundador | — |
| Lead Backend | Backend lead | — |
| QA / Auditoría | Auditor fugu/Kimi | 2026-07-10 |
| Operaciones | Ops / VPS | — |

---

## 7. Changelog

- v1.0.0 (2026-07-10): Acta de cierre parcial Etapa 3 con entregables, brechas remanentes, decisiones y sign-off.
