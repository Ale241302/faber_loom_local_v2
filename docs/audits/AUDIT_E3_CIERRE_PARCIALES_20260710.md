---
id: AUDIT_E3_CIERRE_PARCIALES
version: 1.0.0
status: STABLE
visibility: [INTERNAL]
domain: faberloom-spaceloom
type: audit
date: 2026-07-10
---

# Auditoría de cierre parcial — Etapa 3 (E3 cierre parciales)

**Fecha de auditoría:** 2026-07-10  
**Rama:** `e3-cierre-parciales`  
**HEAD:** `927165a`  
**Schema DB:** v41  
**Suite:** `615 passed, 12 skipped, 0 failed` (468.86 s)  
**Knowledge graph:** 28.419 nodos / 47.947 edges / 1.821 comunidades  
**Perfil auditor:** fugu (Sakana/Codex CLI)

---

## 1. Alcance y criterios

Esta auditoría certifica el cierre parcial de los hitos E3-1 a E3-6 y de las deudas operativas E3-0 documentadas como bloques codeables en la rama `e3-cierre-parciales`. El criterio de aceptación es:

- Suite completa: 0 failed, passed > 552 (baseline E3-1).
- Cada bloque entrega código + tests + documentación mínima.
- No se inventan datos de fuentes externas (APIs tributarias, archivos Marluvas/Tecmater, credenciales VPS/correo).

Referencias:
- `Plan/PLAN_DESARROLLO_FABERLOOM_ETAPA3_v1.md`
- `docs/audits/AUDIT_E3_DETAILED_CLOSURE_REPORT_20260708.md` (baseline)
- `docs/audits/AUDIT_E3_PLAN_VS_CODE_20260708.md` (baseline P0)

---

## 2. Resumen por bloque

| Bloque | Hito E3 | Gap cerrado | Commit | Tests principales |
|---|---|---|---|---|
| 1 | E3-1 | BYO keys estricto/híbrido + recargo plataforma | `376a07e` | `test_e3_5_byo_modes.py` |
| 2 | E3-2 | Conectores tributarios como capa de adaptadores | `46c8473` | `test_e3_4_tax_connectors.py`, `test_e3_4_taxonomy_v2.py` |
| 3 | E3-3 | Webhook WhatsApp para C0-1 | `043e9b4` | `test_e3_4_whatsapp_inbound.py` |
| 4 | E3-4 | Primitivas P15/P17 + correction_log | `bfc88f7` | `test_e3_4_p15_p17.py` |
| 5 | E3-5 | Migración batch skills legacy a manifest v2 | `096a5b0` | `test_e3_4_legacy_migration.py` |
| 6 | E3-6 | Golden Harvester de casos reales | `4a423d1` | `test_e3_4_golden_harvester.py` |
| 7 | E3-6 | Health dashboard, numeración secuencial de facturas y PDF | `1a0192b` | `test_e3_6_health.py`, `test_e3_6_billing.py` |
| 8 | E3-0/E3-2 | Runbook VPS, ingest KB H3 y migración MinIO | `927165a` | `test_e3_0_kb_h3.py`, `test_e3_2_minio_object_migration.py` |

**Nota:** la numeración de bloques sigue el orden de ejecución aprobado por el orquestador (1 → 4 → 5 → 6 → 2 → 3 → 7 → 8 → 9), no el orden canónico de hitos E3.

---

## 3. Semáforo por hito E3

| Hito | Estado | Severidad máxima remanente | Observación |
|---|---|---|---|
| E3-0 Cierre operativo + seguridad | 🟡 Parcial cerrado en código | P1 | Scripts de ingest KB H3 y migración MinIO listos; ejecución real y rotación VPS/SSH/correo quedan como deuda operativa humana documentada. |
| E3-1 Postgres + RLS runtime | 🟢 Cerrado técnicamente | — | Adapter dual, migrador, RLS policies, cutover documentado; SQLite sigue disponible para dev. |
| E3-2 Tenant lifecycle | 🟢 Cerrado | — | Signup, planes, config cascade, platform_admin, prefijos MinIO. |
| E3-3 Entidad por tenant + sello | 🟢 Cerrado | — | Identidad inmutable, key broker, envelope encryption, contamination suite. |
| E3-4 Fábrica de skills / comex | 🟡 Parcial | P2 | Olas 0-2 cerradas (taxonomía v2, compiler v2, C0-1/C0-2, evidence bundle, track record, PACK 1/3 en shadow). Conectores reales y promoción ACTIVE quedan para E3-6 comercial. |
| E3-5 Routing por tenant + presets | 🟢 Cerrado | — | Presets builder, BYO keys tenant-scoped, ledger, wire "Usar en routine". |
| E3-6 Tenant externo + billing manual | 🟢 Cerrado técnicamente | P2 | Health dashboard, secuencia de facturas, PDF no fiscal, SLA beta. Falta tenant externo real con soak ≥30 días para declarar E3-6 comercial cerrado. |

---

## 4. Riesgos P0 — estado

| Riesgo | Estado | Evidencia |
|---|---|---|
| Envío/borrado sin HITL | ✅ Cubierto | Confirmation token en envío de correo, borrado de API key y borrado de KB source. |
| Injection por contenido | ✅ Cubierto | `security/injection.py`, `assert_safe_kb_source`, neutralización de CSV/HTML/hidden-instructions. |
| Fuga cross-workspace | ✅ Cubierto en código | `enforce_tenant_scoped`, aislamiento por Context, RLS policies, canario. Aislamiento físico real depende de cutover Postgres en VPS. |
| Dato inventado sin fuente en KB | ✅ Cubierto | KB exige citas y source-to-field check; no se cargaron datos reales sin fuente. |

---

## 5. Pendientes humanos / externos (no codeables)

Estos ítems quedan explícitamente documentados como fuera del alcance de esta rama y requieren acción humana/externa:

1. **Rotación real VPS/SSH/correo** — ejecutar el runbook `docs/OPERACION_VPS_E3.md` en la ventana de mantenimiento y dejar evidencia en `docs/audits/EVIDENCIA_ROTACION_SEGURIDAD_VPS_YYYYMMDD.md`. `[PENDIENTE — NO INVENTAR]`
2. **Archivos fuente KB H3 (Marluvas/Tecmater)** — el CEO debe entregar listas de precios/catálogos/fichas técnicas; luego ejecutar `app/scripts/ingest_kb_h3.py`. `[PENDIENTE — NO INVENTAR]`
3. **Migración real de objetos MWT en MinIO** — ejecutar `app/scripts/migrate_minio_objects_to_tenant_prefix.py` contra la instancia productiva tras backup. `[PENDIENTE — NO INVENTAR]`
4. **Verificación de APIs tributarias (ATV/SAT/DIAN)** — acceso real y documentación de resultado en `docs/faberloom/PLB_FB_VERIFICACION_APIS_TRIBUTARIAS_v1.md`. `[PENDIENTE — NO INVENTAR]`
5. **Tenant externo real y soak ≥30 días** — requisito comercial para declarar E3-6 cerrado. `[PENDIENTE — NO INVENTAR]`
6. **Certificados de firma comercial y acuerdo de datos con design partner.** `[PENDIENTE — NO INVENTAR]`

---

## 6. Métricas de calidad

| Métrica | Valor | Nota |
|---|---|---|
| Tests | 615 passed / 12 skipped / 0 failed | +7 respecto al cierre del Bloque 7 (608). |
| Schema version | 41 | Incluye migraciones v41 para facturación secuencial/SLA/PDF. |
| Warnings | 30 | Todos por `ln` deprecado en `fpdf2` y fallback a memoria de MinIO en tests; no son bloqueantes. |
| Coverage P0 | 4/4 | Ninguna violación abierta. |
| Bloques codeables cerrados | 8/8 | Bloque 9 = cierre/auditoría (este informe). |

---

## 7. Changelog

- v1.0.0 (2026-07-10): Auditoría de cierre parcial E3 con mapeo Bloque 1‑8, semáforo de hitos, pendientes humanos/externos y métricas de suite.
