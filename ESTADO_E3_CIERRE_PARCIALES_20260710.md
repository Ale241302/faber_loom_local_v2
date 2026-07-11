# Cierre parcial E3 — FaberLoom/SpaceLoom

**Fecha:** 2026-07-10  
**Estado:** ✅ CERRADO TÉCNICAMENTE (E3-4 cerrado en su lado codeable)  
**Suite:** `619 passed, 12 skipped, 32 warnings in 516.51s (0:08:36)`  
**Schema DB:** 41  
**HEAD:** `57a21bf` (cierre codeable E3-4)  
**Knowledge graph:** actualizado al cierre

---

## 1. Objetivo

Cerrar técnicamente los hitos E3-1 a E3-6 y las deudas operativas instrumentables de E3-0, dejando explícitos los pendientes que requieren acción humana/externa antes de declarar E3-6 comercialmente cerrado. En esta ronda se cierra específicamente el **lado codeable de E3-4** (conectores tributarios, materialización de olas 3-5, promotion readiness).

---

## 2. Entregables cerrados

### Bloque 1 — E3-1 BYO keys estricto/híbrido + recargo plataforma
- `app/src/router/config_store.py`: BYO keys con scope tenant/usuario.
- `app/src/ledger.py`: recargo plataforma en el ledger.
- Tests: `app/tests/test_e3_5_byo_modes.py`.

### Bloque 2 — E3-2 Conectores tributarios como capa de adaptadores
- `app/src/connectors/tax_authority.py`: adaptadores para ATV/SAT/DIAN con modos `mock`/`sandbox`/`live`, secretos cifrados por tenant y certificado gateado (HE2-9).
- `docs/faberloom/PLB_FB_VERIFICACION_APIS_TRIBUTARIAS_v1.md`: playbook de verificación humana.
- Tests: `app/tests/test_e3_4_tax_connectors.py`.

### Bloque 3 — E3-3 Webhook WhatsApp para C0-1
- `app/src/api.py`: endpoints de inbound WhatsApp.
- Tests: `app/tests/test_e3_4_whatsapp_inbound.py`.

### Bloque 4 — E3-4 Primitivas P15/P17 + correction_log
- `app/src/gold.py` / `app/src/skills.py`: primitivas de corrección y log.
- Tests: `app/tests/test_e3_4_p15_p17.py`.

### Bloque 5 — E3-5 Migración batch skills legacy a manifest v2
- `app/scripts/migrate_skills_to_manifest_v2.py`.
- Tests: `app/tests/test_e3_4_legacy_migration.py`.

### Bloque 6 — E3-6 Golden Harvester de casos reales
- `app/src/gold.py`: recolección y promoción de golden cases.
- Tests: `app/tests/test_e3_4_golden_harvester.py`.

### Bloque 7 — E3-6 Health dashboard, facturación secuencial y PDF
- `app/src/health_dashboard.py`: dashboard de salud por tenant.
- `app/src/billing.py`: numeración secuencial y PDF con `fpdf2`.
- `app/static/js/health_dashboard.jsx`: vista Salud en el shell.
- Tests: `app/tests/test_e3_6_health.py`, `test_e3_6_billing.py`.

### Bloque 8 — E3-0/E3-2 Runbook VPS, ingest KB H3 y migración MinIO
- `docs/OPERACION_VPS_E3.md`: runbook de rotación VPS/SSH/correo.
- `app/scripts/ingest_kb_h3.py`: carga masiva KB H3.
- `app/scripts/migrate_minio_objects_to_tenant_prefix.py`: migración legacy a prefijo tenant.
- `app/src/storage.py`: métodos `copy_object` y `list_object_keys`.
- Tests: `app/tests/test_e3_0_kb_h3.py`, `test_e3_2_minio_object_migration.py`.

### Bloque 9 — Cierre y auditoría
- `docs/audits/AUDIT_E3_CIERRE_PARCIALES_20260710.md`.
- `docs/audits/ACTA_ETAPA3_CIERRE_PARCIALES_20260710.md`.

### Bloque 10 — Verificación de conectores tributarios
- Confirmación de que `app/src/connectors/tax_authority.py`, `app/tests/test_e3_4_tax_connectors.py` y `docs/faberloom/PLB_FB_VERIFICACION_APIS_TRIBUTARIAS_v1.md` ya existían y son funcionales.
- Agregado test de modo `sandbox` fail-closed.
- Corrección de `docs/audits/AUDIT_E3_DETAILED_CLOSURE_REPORT_20260708.md` para reflejar que el código está listo y lo pendiente es la verificación humana.

### Bloque 11 — Materialización de olas 3-5
- Creado `app/scripts/generate_olas_3_5_skills.py` para generar 53 skills de los PACKs 2, 4-13.
- Archivos generados en `faberloom/SKILL_*.md` con estados `DRAFT` (templates) o `DEFINITION_PENDING` (GAPs) y marcadores `[PENDIENTE — NO INVENTAR]`.
- Los skills se indexan correctamente en el catálogo global (`/api/skills`).

### Bloque 12 — Promotion readiness
- `app/src/skill_primitives.py`: constante compartida `PROMOTION_THRESHOLDS` y helper `compute_pack_readiness`.
- `app/src/api.py`: endpoints `GET /api/workspaces/{ws}/packs/readiness` y `POST /api/workspaces/{ws}/packs/{pack_id}/promote`.
- `app/static/js/promotion_readiness.jsx`: tablero UI con progreso de gates y botón de promoción con confirmación.
- `docs/faberloom/PLB_FB_PROMOTION_READINESS_DOGFOOD_v1.md`: playbook de dogfood.
- Tests: `app/tests/test_e3_4_pack_readiness.py`.

### Bloque 13 — Cierre documental
- `docs/audits/ACTA_ETAPA3_E3_4_CIERRE_CODEABLE_20260710.md`.
- `docs/audits/AUDIT_E3_DETAILED_CLOSURE_REPORT_20260708.md` actualizado.
- Knowledge graph refrescado.

---

## 3. Resultado de tests

```text
619 passed, 12 skipped, 32 warnings in 516.51s (0:08:36)
```

Baseline anterior: `615 passed, 12 skipped, 0 failed`. Incremento: +4 tests (sandbox de conectores tributarios + 3 tests de promotion readiness).

---

## 4. Archivos clave modificados o creados

| Ruta | Tipo | Nota |
|------|------|------|
| `app/src/connectors/tax_authority.py` | E | Adaptadores tributarios ATV/SAT/DIAN. |
| `app/src/skill_primitives.py` | M | `PROMOTION_THRESHOLDS`, `compute_pack_readiness`, uso de constantes en `promote_pack`. |
| `app/src/api.py` | M | Endpoints `/workspaces/{ws}/packs/readiness` y `/workspaces/{ws}/packs/{pack_id}/promote`. |
| `app/static/js/promotion_readiness.jsx` | N | Tablero de promotion readiness. |
| `app/static/js/app.jsx` | M | Entrada Promoción de packs en navegación. |
| `app/static/index.html` | M | Carga de `promotion_readiness.jsx`. |
| `app/scripts/generate_olas_3_5_skills.py` | N | Generador de skills olas 3-5. |
| `faberloom/SKILL_CX_*.md` | N | 10 skills PACK 2. |
| `faberloom/SKILL_PL_*.md` | N | 3 skills PACK 4. |
| `faberloom/SKILL_TR_*.md` | N | 5 skills PACK 5. |
| `faberloom/SKILL_WA_*.md` | N | 3 skills PACK 6. |
| `faberloom/SKILL_BO_*.md` | N | 3 skills PACK 7. |
| `faberloom/SKILL_CM_*.md` | N | 4 skills PACK 8. |
| `faberloom/SKILL_SV_*.md` | N | 5 skills PACK 9. |
| `faberloom/SKILL_FI_*.md` | N | 4 skills PACK 10. |
| `faberloom/SKILL_LG_*.md` | N | 5 skills PACK 11. |
| `faberloom/SKILL_GE_*.md` | N | 4 skills PACK 12. |
| `faberloom/SKILL_OP_*.md` | N | 3 skills PACK 13 operaciones. |
| `faberloom/SKILL_MK_*.md` | N | 3 skills PACK 13 marketing. |
| `faberloom/SKILL_HR_*.md` | N | 1 skill PACK 13 RRHH. |
| `app/tests/test_e3_4_tax_connectors.py` | M | Test de sandbox fail-closed. |
| `app/tests/test_e3_4_pack_readiness.py` | N | Tests de readiness y promote. |
| `docs/faberloom/PLB_FB_PROMOTION_READINESS_DOGFOOD_v1.md` | N | Playbook dogfood. |
| `docs/audits/AUDIT_E3_DETAILED_CLOSURE_REPORT_20260708.md` | M | Corrección E3-4 y olas 3-5. |
| `docs/audits/ACTA_ETAPA3_E3_4_CIERRE_CODEABLE_20260710.md` | N | Acta de cierre codeable. |
| `ESTADO_E3_CIERRE_PARCIALES_20260710.md` | M | Este documento. |

---

## 5. Issues activos (no bloqueantes para el cierre técnico)

1. **Pendientes operativos humanos:** rotación VPS/SSH/correo, carga KB H3 real, migración MinIO real.
2. **Pendientes externos/comerciales:** verificación de APIs tributarias, design partner, soak 30 días, certificados de firma.
3. **Pendientes de dogfood:** acumular track record y golden cases verificados para PACK 1/3 antes de promover a ACTIVE.
