# PLB_FB_PROMOTION_READINESS_DOGFOOD_v1 — Dogfood de promoción de packs

**Fecha:** 2026-07-10  
**Aplica a:** E3-4 Fábrica de skills  
**Responsables:** curador + AM + dev (soporte)  

## Objetivo
Promover un pack de skills de `SHADOW` a `ACTIVE` usando datos reales del tenant MWT, cumpliendo los gates de golden cases y track record. Este playbook se usa en dogfood antes de ofrecer el pack a un tenant externo.

## Gates de promoción (no negociables)

Los umbrales viven en `app/src/skill_primitives.py::PROMOTION_THRESHOLDS`:

| Gate | Umbral | Dónde se verifica |
|---|---|---|
| Golden cases | ≥ `required_golden_cases` por pack (default 1 por skill importado) | Tabla `golden_case` |
| Aprobación | 100% de golden cases aprobados (`approved = 1`) | Primera persona (curador/AM) |
| Verificación independiente | 100% de golden cases verificados (`verified_by` not null y distinto de `approved_by`) | Segunda persona (distinta al aprobador) |
| Track record | ≥ 100 runs totales y ≥ 90% acceptance rate por skill importado | Tabla `skill_track_record` |
| Confirmación HITL | Token SHA-256 truncado a 16 chars del `pack_id` | Endpoint `/api/workspaces/{ws}/packs/{pack_id}/promote` |

## Flujo paso a paso

### 1. Importar el pack en el workspace MWT

```bash
# UI: Admin → Promoción de packs, o API:
GET /api/workspaces/{workspace_id}/packs/readiness
POST /api/workspaces/{workspace_id}/routines/import-faberloom
```

Para PACK 1 importar al menos `SKILL_FE_STATUS_CHECK.md`. Para PACK 3 importar `SKILL_CO_DUNNING_FE.md` (o cualquier otro `SKILL_CO_*`).

### 2. Ejecutar el skill en dogfood real

- Usar el chat o el Routine Hub con el skill activo como contexto.
- Procesar facturas propias de MWT (PACK 1) o facturas vencidas de cartera (PACK 3).
- Todo output con efecto externo debe quedar en estado `requires_hitl` hasta aprobación humana.

### 3. Proponer golden cases

Desde una run exitosa:

```bash
POST /api/tenants/{tenant_id}/skills/{skill_id}/golden-cases/propose
{ "run_id": "<routine_run_id>" }
```

Esto congela input, output y evidencia en `golden_case` con `approved = 0` y `origin = 'dogfood'`.

### 4. Aprobar golden cases

La primera persona (curador/AM) aprueba:

```bash
POST /api/tenants/{tenant_id}/golden-cases/{case_id}/approve
{ "confirmation_token": "<sha256(case_id)[:16]>" }
```

### 5. Verificar golden cases

Una segunda persona distinta al aprobador verifica:

```bash
POST /api/tenants/{tenant_id}/golden-cases/{case_id}/verify
```

La verificación falla si `verified_by == approved_by`.

### 6. Revisar promotion readiness

```bash
GET /api/workspaces/{workspace_id}/packs/readiness
```

La respuesta incluye por pack:
- `skill_count`, `imported_count`
- `golden_cases` (total / approved / verified)
- `track_records` (total / meeting_threshold)
- `can_promote` y `blockers`

### 7. Promover el pack

Solo cuando `can_promote` sea `true`:

```bash
POST /api/workspaces/{workspace_id}/packs/{pack_id}/promote
{ "confirmation_token": "<sha256(pack_id)[:16]>" }
```

El sistema:
- Actualiza `pack_status.status` a `active`.
- Actualiza `skill_manifest.status` a `active` para los skills importados del pack.
- Registra `promoted_at` y `promoted_by`.

## Ejemplo: PACK 1 fiscalidad electrónica

1. Importar `SKILL_FE_STATUS_CHECK.md`.
2. Ejecutar con una clave de factura electrónica real de MWT.
3. Proponer la run como golden case de `SKILL_FE_STATUS_CHECK`.
4. Aprobar con curador A.
5. Verificar con curador B (B ≠ A).
6. Asegurar que `skill_track_record` para `SKILL_FE_STATUS_CHECK` tenga `runs_total >= 100` y `acceptance_rate >= 0.90`.
7. Promover `wtp_fiscalidad_electronica` con el token de confirmación.

## Ejemplo: PACK 3 cobranza

1. Importar `SKILL_CO_DUNNING_FE.md`.
2. Ejecutar con facturas vencidas reales de cartera MWT.
3. Repetir pasos 3-7 para `wtp_cobranza`.

## Bloqueos conocidos

- **PACK 2 (comex):** bloqueado hasta tener KB Marluvas/Tecmater cargado. Sin fuentes reales no se fabrican golden cases.
- **Olas 3-5:** los skills están en `DRAFT`/`DEFINITION_PENDING`; requieren localización LATAM y definición de alcance antes de importarlos.

## Rollback

Si un pack promovido produce efectos adversos en dogfood:

1. No hay reversión automática de `ACTIVE` a `SHADOW` por diseño (la promoción es deliberada).
2. El curador puede desactivar skills individuales desde el Routine Hub.
3. Abrir incidente y agregar un nuevo golden case que capture la regresión antes de volver a promover.

## Referencias

- `app/src/skill_primitives.py` — `PROMOTION_THRESHOLDS`, `promote_pack`, `compute_pack_readiness`.
- `app/src/golden_harvester.py` — `propose_golden_case_from_run`, `approve_golden_case`, `verify_golden_case`.
- `app/static/js/promotion_readiness.jsx` — UI del tablero.
- `ENT_FB_SKILL_CATALOG_v1.md` — catálogo maestro de skills/packs.
