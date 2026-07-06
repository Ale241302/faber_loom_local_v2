# Cierre E2-3 — KB compartida + sellado por rol/workspace + gold loop L2→L3

**Fecha:** 2026-07-06  
**Milestone:** Camino B Foundation Beta — E2-3  
**Estado:** ✅ Cerrado  
**Suite:** 342 passed / 13 warnings en `app/`  
**Schema DB app:** v25 (incluye columnas E2-2 correo + `gold_candidate.state`)

---

## 1. Alcance entregado

E2-3 cierra la evolución del gold loop y del knowledge base compartido, pasando de un esquema binario (`approved`) a una máquina de estados explícita con promoción graduada L2→L3 gobernada por rol, k-anonimato y verificación independiente.

### 1.1 KB compartida y herencia

- **Herencia org → equipo → workspace** a través de `workspace.parent_id` + `workspace.inherits_kb`.
- El scope de búsqueda (`_workspace_kb_scope` en `app/src/kb.py`) incluye al padre **solo si** comparten `tenant_id`.
- Las citas (`source_id`, `section`, `chunk_index`) se preservan sin re-escritura al devolver resultados heredados.
- Aislamiento del **tenant canario** (`canary`) verificado: no ve KB del tenant default y viceversa.

### 1.2 Sellado por workspace / rol

- El HMAC por workspace (`_workspace_seals`) sigue vigente; los candidatos gold portan `tenant_id` y `workspace_id` como parte del scoping.
- **Roles y permisos** (resumen):
  - `viewer` → solo lectura; no puede promover gold.
  - `am` / `operator` → opera skills/runs; no promueve gold.
  - `curator` / `admin` → puede promover a `active_l2` y a `l3` (con gates adicionales).
  - `ceo` / `owner` → mismo poder que curador para L3.

### 1.3 Máquina de estados gold

```
candidate
   │
   ▼
active_l2  ──► rejected
   │
   ▼ (k-anon ≥ 5)
l3_pending
   │
   ▼ (rol curador/CEO + verificador independiente en campos duros)
l3  ──► rejected
```

- Estados: `candidate`, `active_l2`, `l3_pending`, `l3`, `rejected`.
- Transiciones validadas en `_VALID_TRANSITIONS` (`app/src/gold.py`).
- Aplicación a la rutina (`apply_gold_to_routine`) requiere estado `active_l2` o `l3`.

### 1.4 Gates de promoción

| Transición | Gate obligatorio |
|---|---|
| `candidate → active_l2` | Rol curador/CEO/admin; `verified_by` independiente si hay campos duros. |
| `active_l2 → l3_pending` | `k-anon >= 5` en el mismo tenant, misma `routine_id`/`task_type`, salida canónica igual. |
| `l3_pending → l3` | Rol curador/CEO/admin; `verified_by != approved_by` cuando hay campos duros. |
| Cualquier estado → `rejected` | Rol curador/CEO/admin. |

- **Campos duros** se detectan a partir de `learned_output_json`: presencia de claves tipo `precio`, `monto`, `cantidad`, `fecha_entrega`, `deadline`, `email`, `telefono` o cualquier campo marcado con metadato `hard_field=true`.
- **k-anon**: cuenta candidatos aprobados/promovidos (`active_l2`, `l3_pending`, `l3`) con igual `routine_id` y `task_type` dentro del tenant, comparando la salida canónica (`json.dumps` ordenado de las claves de aprendizaje).

### 1.5 Modelo de datos

- Tabla `gold_candidate` añade columna `state TEXT NOT NULL DEFAULT 'candidate'`.
- `PromoteGoldCandidateRequest` añade `target_state` (default `active_l2`).
- `GoldCandidateRead` expone `state`, `approved_by`, `verified_by`.

---

## 2. Archivos modificados / añadidos

### Backend

- `app/src/gold.py` — máquina de estados, helpers k-anon, gates de rol, verificador independiente.
- `app/src/kb.py` — herencia con preservación de fuente, scoping por tenant.
- `app/src/models.py` — `PromoteGoldCandidateRequest.target_state`, `GoldCandidateRead.state`, migración v25.
- `app/src/db.py` — `GOLD_CANDIDATE_COLUMNS` incluye `state`.
- `app/src/api.py` — endpoint `/workspaces/{id}/gold-candidates/{id}/promote` pasa `target_state` y rol.

### Frontend

- Sin cambios de UI específicos para E2-3 (el panel Gold/Routine ya soporta el flujo L2 existente; L3 se expone a través del mismo endpoint con payload).

### Tests

- `app/tests/test_e2_3_kb_gold.py` — 11 tests nuevos:
  1. `test_kb_inheritance_preserves_source_citation`
  2. `test_kb_inheritance_disabled_isolates_child`
  3. `test_canary_workspace_isolated_from_default_kb`
  4. `test_gold_candidate_state_machine`
  5. `test_l3_requires_k_anon`
  6. `test_l3_requires_curator_role`
  7. `test_l3_hard_fields_require_independent_verifier`
  8. `test_viewer_cannot_promote_gold`
  9. `test_apply_gold_requires_active_state`
  10. `test_reject_gold_candidate`
  11. `test_cross_tenant_curator_cannot_verify`

### Documentación

- Este archivo: `docs/E2_3_KB_GOLD_CIERRE.md`.

---

## 3. Resultados de calidad

```bash
cd app && python -m pytest -q
# 342 passed, 13 warnings in 200.75s
```

- Los 13 warnings restantes son:
  - 2 `StarletteDeprecationWarning` por constante `HTTP_422_UNPROCESSABLE_ENTITY` en tests de correo.
  - 11 `InsecureKeyLengthWarning` de PyJWT porque `FABERLOOM_SECRET_KEY` en tests es corto (11 bytes). No afectan funcionalidad; se mitigan en producción con clave >= 32 bytes.

### Cobertura de riesgos P0

| Riesgo P0 | Evidencia en tests |
|---|---|
| Envío/borrado sin HITL | No se tocó flujo de envío; `confirmation_token` sigue vigente en E2-2. |
| Injection por contenido (KB/SKILL.md/PDF/Excel/HTML) | Canarios previos + E2-3 herencia/aislamiento. |
| Fuga cross-workspace / cross-tenant | `test_canary_workspace_isolated_from_default_kb`, `test_cross_tenant_curator_cannot_verify`, scoping `tenant_id` en k-anon. |
| Dato inventado sin fuente en KB | `source_id`/`section` obligatorios; herencia preserva cita. |
| Auto-promoción no autorizada | Gold loop requiere promoción manual con rol + gates; no hay trigger automático `candidate → active_l2`. |

---

## 4. Decisiones técnicas registradas

1. **Estados explícitos vs booleano.** Se prefirió una columna `state` con máquina de estados porque el plan E2 requería auditoría clara de cada gate L2/L3 y rechazo.
2. **k-anon por tenant.** El conteo de k-anonimato nunca cruza `tenant_id`; un candidato en tenant A no se suma al k-anon de tenant B.
3. **Verificador independiente en L2 y L3.** Para campos duros se exige `verified_by != approved_by` tanto en `active_l2` como en `l3`, garantizando four-eyes.
4. **Sin auto-ascenso a `l3_pending`.** Aunque un candidato alcance k-anon ≥ 5, permanece en `active_l2` hasta que un actor con rol lo promueva explícitamente.
5. **Rol CEO/owner y curador/admin equivalentes para L3.** Esto alinea con la matriz `docs/ROLES_PERMISSIONS_MATRIX_E2.md`.

---

## 5. Pendientes y próximos pasos

1. **E2-4 — Routing / ledger / modo auto:** continuar el track Foundation Beta según `Plan/PLAN_DESARROLLO_FABERLOOM_FASE3_v*.md`.
2. **Context enforcement parcial:** algunos helpers de `kb.py`/`gold.py` aún no llaman `enforce_tenant_scoped(ctx)` de forma uniforme; se auditará en E2-4.
3. **Postgres real:** la migración v25 se validó en dry-run; falta ejecutar contra PostgreSQL con Docker/psql cuando esté disponible.
4. **Graphify:** ✅ actualizado tras cierre — 25.752 nodos / 35.013 edges / 1.710 comunidades.
5. **UI de promoción L3:** agregar al frontend un selector de `target_state` y advertencia de k-anon/verificador independiente.

---

## 6. Referencias

- `app/src/gold.py`
- `app/src/kb.py`
- `app/src/models.py`
- `app/src/db.py`
- `app/src/api.py`
- `app/tests/test_e2_3_kb_gold.py`
- `docs/ROLES_PERMISSIONS_MATRIX_E2.md`
- `docs/CONTEXT_RLS_CONTRACT_E2.md`
