# Acta de cierre codeable — E3-4 Fábrica de skills

**Fecha:** 2026-07-10  
**Repo:** `faber_loom_local_vv2`, rama `e3-cierre-parciales`  
**Plan:** `Plan/PLAN_DESARROLLO_FABERLOOM_ETAPA3_v1.md`  
**Objetivo:** declarar E3-4 **cerrado en su lado codeable** y dejar explícitos los pendientes humanos/externos.

---

## 1. Resolución

E3-4 queda declarado **cerrado técnicamente** en su lado codeable. Todos los elementos que pueden resolverse con código, tests y documentación tienen implementación verde. Los únicos ítems abiertos dependen de acciones humanas o externas, listadas en la sección 4.

## 2. Evidencia de cierre

| Elemento | Estado | Evidencia |
|---|---|---|
| Conectores tributarios | ✅ Cerrado en código | `app/src/connectors/tax_authority.py`; modos `mock`/`sandbox`/`live`; secretos cifrados por tenant; certificado gateado (HE2-9). Tests: `app/tests/test_e3_4_tax_connectors.py` (7 passed). |
| Verificación APIs tributarias reales | ⏸️ Humano/externo | `docs/faberloom/PLB_FB_VERIFICACION_APIS_TRIBUTARIAS_v1.md` listo para ejecutar. |
| Olas 0-2 (PACK 1/3) | ✅ Cerrado en código | Skills en SHADOW con golden cases y track-record gates; `promote_pack` y `compute_pack_readiness` implementados. |
| Olas 3-5 | ✅ Materializadas sin inventar | 53 skills creados en `faberloom/SKILL_*.md` con estados `DRAFT`/`DEFINITION_PENDING` y marcadores `[PENDIENTE — NO INVENTAR]`. |
| Promotion readiness | ✅ Cerrado en código | Endpoint `/api/workspaces/{ws}/packs/readiness`, endpoint `/api/workspaces/{ws}/packs/{pack_id}/promote`, UI `app/static/js/promotion_readiness.jsx`, playbook `docs/faberloom/PLB_FB_PROMOTION_READINESS_DOGFOOD_v1.md`. Tests: `app/tests/test_e3_4_pack_readiness.py` (3 passed). |
| Auditoría actualizada | ✅ | `docs/audits/AUDIT_E3_DETAILED_CLOSURE_REPORT_20260708.md` corregido para reflejar lo implementado y lo pendiente. |

## 3. Métricas de la suite

Resultado final del cierre:

```text
619 passed, 12 skipped, 32 warnings in 516.51s (0:08:36)
```

Baseline anterior: `615 passed, 12 skipped, 0 failed`. Incremento: +4 tests (sandbox de conectores tributarios + 3 tests de promotion readiness).

## 4. Pendientes humanos/externos explícitos

1. **Verificación de APIs tributarias reales (ATV/SAT/DIAN, tracking TICA):** el adaptador está listo; falta validar URLs, credenciales y certificados con cada autoridad.
2. **Carga de KB Marluvas/Tecmater (HE2-3):** el script `app/scripts/ingest_kb_h3.py` está listo; falta que el CEO entregue los archivos fuente.
3. **Dogfood real de PACK 1/3:** acumular track record (≥100 runs / ≥90% acceptance) y golden cases aprobados+verificados para promover a ACTIVE.
4. **Certificados de firma comercial (HE2-9):** requisito de compra, no de código.
5. **Design partner, acuerdo de datos y soak de 30 días:** E3-6 continúa comercialmente abierto.

## 5. Reglas no negociables respetadas

- **No se inventaron datos:** los skills de olas 3-5 solo contienen IDs/nombres del catálogo y marcadores `[PENDIENTE — NO INVENTAR]`.
- **Fail-closed:** conectores tributarios y `promote_pack` rechazan operar sin credenciales/gates.
- **HITL:** la promoción de un pack requiere token de confirmación determinístico y doble gate de golden cases (aprobar + verificar por personas distintas).
- **Aislamiento tenant:** todos los queries usan `Context(workspace_id, tenant_id)`; secrets de conectores están cifrados por tenant.

## 6. Siguientes pasos

1. CEO: conseguir archivos Marluvas/Tecmater y design partner con acuerdo de datos.
2. Dev + AM: ejecutar `PLB_FB_VERIFICACION_APIS_TRIBUTARIAS_v1.md` y documentar resultados.
3. Curador + AM: ejecutar dogfood de PACK 1/3 y usar el tablero de promotion readiness para promover a ACTIVE.
4. Ops: ejecutar runbooks/scripts de VPS/SSH/correo y migración MinIO, dejando evidencia en `docs/audits/`.

---

*Acta preparada por Fugu / Kimi Code CLI. Cierre codeable de E3-4.*
