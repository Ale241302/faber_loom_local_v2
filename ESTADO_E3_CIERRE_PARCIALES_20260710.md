# Cierre parcial E3 — FaberLoom/SpaceLoom

**Fecha:** 2026-07-10  
**Estado:** ✅ CERRADO TÉCNICAMENTE (parcial)  
**Suite:** `615 passed, 12 skipped, 30 warnings` (468.86 s)  
**Schema DB:** v41  
**HEAD:** `927165a`  
**Knowledge graph:** 28.419 nodos / 47.947 edges / 1.821 comunidades

---

## 1. Objetivo

Cerrar técnicamente los hitos E3-1 a E3-6 y las deudas operativas instrumentables de E3-0, dejando explícitos los pendientes que requieren acción humana/externa antes de declarar E3-6 comercialmente cerrado.

---

## 2. Entregables cerrados

### Bloque 1 — E3-1 BYO keys estricto/híbrido + recargo plataforma
- `app/src/router/config_store.py`: BYO keys con scope tenant/usuario.
- `app/src/ledger.py`: recargo plataforma en el ledger.
- Tests: `app/tests/test_e3_5_byo_modes.py`.
- Commit: `376a07e`.

### Bloque 2 — E3-2 Conectores tributarios como capa de adaptadores
- `app/src/tax_connectors/`: adaptadores para ATV/SAT/DIAN con fallback a placeholder.
- Taxonomía v2 y compiler v2 integrados.
- Tests: `app/tests/test_e3_4_tax_connectors.py`, `test_e3_4_taxonomy_v2.py`.
- Commit: `46c8473`.

### Bloque 3 — E3-3 Webhook WhatsApp para C0-1
- `app/src/api.py`: endpoints de inbound WhatsApp.
- Tests: `app/tests/test_e3_4_whatsapp_inbound.py`.
- Commit: `043e9b4`.

### Bloque 4 — E3-4 Primitivas P15/P17 + correction_log
- `app/src/gold.py` / `app/src/skills.py`: primitivas de corrección y log.
- Tests: `app/tests/test_e3_4_p15_p17.py`.
- Commit: `bfc88f7`.

### Bloque 5 — E3-5 Migración batch skills legacy a manifest v2
- `app/scripts/migrate_skills_to_manifest_v2.py`.
- Tests: `app/tests/test_e3_4_legacy_migration.py`.
- Commit: `096a5b0`.

### Bloque 6 — E3-6 Golden Harvester de casos reales
- `app/src/gold.py`: recolección y promoción de golden cases.
- Tests: `app/tests/test_e3_4_golden_harvester.py`.
- Commit: `4a423d1`.

### Bloque 7 — E3-6 Health dashboard, facturación secuencial y PDF
- `app/src/health_dashboard.py`: dashboard de salud por tenant.
- `app/src/billing.py`: numeración secuencial y PDF con `fpdf2`.
- `app/static/js/health_dashboard.jsx`: vista Salud en el shell.
- Tests: `app/tests/test_e3_6_health.py`, `test_e3_6_billing.py`.
- Commit: `1a0192b`.

### Bloque 8 — E3-0/E3-2 Runbook VPS, ingest KB H3 y migración MinIO
- `docs/OPERACION_VPS_E3.md`: runbook de rotación VPS/SSH/correo.
- `app/scripts/ingest_kb_h3.py`: carga masiva KB H3.
- `app/scripts/migrate_minio_objects_to_tenant_prefix.py`: migración legacy a prefijo tenant.
- `app/src/storage.py`: métodos `copy_object` y `list_object_keys`.
- Tests: `app/tests/test_e3_0_kb_h3.py`, `test_e3_2_minio_object_migration.py`.
- Commit: `927165a`.

### Bloque 9 — Cierre y auditoría
- `docs/audits/AUDIT_E3_CIERRE_PARCIALES_20260710.md`.
- `docs/audits/ACTA_ETAPA3_CIERRE_PARCIALES_20260710.md`.
- Este documento (`ESTADO_E3_CIERRE_PARCIALES_20260710.md`).

---

## 3. Resultado de tests

```text
615 passed, 12 skipped, 30 warnings in 468.86s (0:07:48)
```

Los 30 warnings son:
- Deprecaciones de `ln=True`/`ln=False` en `fpdf2` (Bloque 7).
- Fallback a memoria de MinIO cuando no hay credenciales configuradas (esperado en tests).

Ningún warning bloquea el cierre.

---

## 4. Archivos clave modificados o creados

| Ruta | Tipo | Nota |
|------|------|------|
| `app/src/db.py` | M | Secuencias de facturas, health summary, helpers de facturación. |
| `app/src/models.py` | M | SCHEMA v41, modelos `TenantHealthRead`, columnas SLA/PDF. |
| `app/src/billing.py` | M | Endpoints de siguiente número y PDF. |
| `app/src/health_dashboard.py` | N | Router de salud por tenant. |
| `app/src/storage.py` | M | `copy_object`, `list_object_keys`. |
| `app/src/main.py` | M | Registro de `health_router`. |
| `app/static/js/health_dashboard.jsx` | N | Vista Salud. |
| `app/static/js/app.jsx` | M | Entrada Salud en navegación. |
| `app/static/js/icons.jsx` | M | Icono `activity`. |
| `app/static/index.html` | M | Carga de `health_dashboard.jsx`. |
| `app/scripts/ingest_kb_h3.py` | N | Carga masiva KB H3. |
| `app/scripts/migrate_minio_objects_to_tenant_prefix.py` | N | Migración MinIO a prefijo tenant. |
| `app/scripts/postgres_rls_policies.sql` | M | RLS para `tenant_invoice_sequence`. |
| `app/requirements-server.txt` | M | `fpdf2>=2.8.7`. |
| `app/tests/test_e3_6_health.py` | N | Dashboard de salud. |
| `app/tests/test_e3_6_billing.py` | M | Facturación secuencial/PDF. |
| `app/tests/test_e3_0_kb_h3.py` | N | Ingest KB H3. |
| `app/tests/test_e3_2_minio_object_migration.py` | N | Migración MinIO. |
| `docs/OPERACION_VPS_E3.md` | N | Runbook VPS/SSH/correo. |
| `docs/audits/AUDIT_E3_CIERRE_PARCIALES_20260710.md` | N | Auditoría de cierre. |
| `docs/audits/ACTA_ETAPA3_CIERRE_PARCIALES_20260710.md` | N | Acta formal. |
| `ESTADO_E3_CIERRE_PARCIALES_20260710.md` | N | Este documento. |

---

## 5. Issues activos (no bloqueantes para el cierre técnico)

1. **Pendientes operativos humanos:** rotación VPS/SSH/correo, carga KB H3 real, migración MinIO real.
2. **Pendientes externos/comerciales:** APIs tributarias, design partner, soak 30 días, certificados de firma.
3. **Warnings de `fpdf2`:** parámetro `ln` deprecado; no afecta funcionamiento.
4. **Graphify version mismatch:** `skill 0.8.30` vs `package 0.8.49`. No afecta funcionamiento.
5. **E3-4 comercial:** PACK 1/3 en SHADOW hasta contar con golden cases reales.

---

## 6. Próximos pasos recomendados

1. **CEO/AM:** conseguir design partner B2B técnico, archivos Marluvas/Tecmater y acceso/verificación de APIs ATV/SAT/DIAN.
2. **Ops:** ejecutar rotación VPS/SSH/correo y migración MinIO usando los runbooks/scripts entregados.
3. **QA/Product:** promover PACK 1/3 a ACTIVE tras cargar KB real y validar citas.
4. **Backend:** iniciar preparación de Etapa 4 o continuación de olas 3-5 de E3-4.
5. **Legal:** tramitar certificados de firma comercial para facturación fiscal.

---

## 7. Verificación final

- [x] Suite completa verde (`615 passed`).
- [x] Knowledge graph actualizado (`graphify update .`).
- [x] Bloques 1-9 commiteados atómicamente.
- [x] Auditoría y acta de cierre creadas.
- [x] Pendientes humanos/externos explícitamente documentados.

**E3 queda cerrada técnicamente y lista para la fase comercial/operativa.**
