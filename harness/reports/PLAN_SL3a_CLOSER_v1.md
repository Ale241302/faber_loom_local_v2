# Plan SL3a CLOSER — v1 (CERRADO)

**Fecha:** 2026-06-25  
**Loop:** §5 AUDIT → PLAN → IMPLEMENT → TEST → GATE → REPORTE  
**Reglas:** No inventar. FROZEN (`ENT_OPS_STATE_MACHINE`, `PLB_ORCHESTRATOR`) intactos.

## DoD objetivo

1. SKILL.md + schema + sandbox, invocable `@nombre`, con biblioteca / invocación / historial — mantener verde.
2. Autoría liviana end-to-end: entidad redacta skill → HITL aprueba → se guarda. Test de flujo completo.
3. Gate del plan (§2): crear y correr una skill por `@nombre` end-to-end, con resultado real.
4. Costura contract-first (§7.6): el routine compiler emite un subconjunto de `SCH_FB_SKILL_MANIFEST_v2`, no un formato paralelo. Test que lo verifique.
5. P0 injection en SKILL.md: canary de hidden-instruction en un SKILL.md rechazado. Test.
6. Multi-tenant: routine/skill con scope por workspace/tenant; no se filtran entre tenants.
7. `test_sl3a_skills.py` + `test_routines_crud.py` verdes + test de autoría HITL + test de manifest subset.
8. Gate §6 completo.

## Cambios técnicos

### 1. Routine compiler como subconjunto del schema canónico

- `app/src/skills.py`:
  - `compile_skill_md(skill_md)` ahora emite solo campos base (`name`, `description`, `version`) + `metadata.mwt.*` canónicos (`id`, `type`, `architectural_archetype`, `domain`, `archetype`, `visibility`, `status`, y opcionales `inputs`, `depends_on_skills`, `skills_imports`, `multi_client_mode`, `client_resolver`, `contract`, `state_machine`, `golden_samples`).
  - Campos runtime (`persona`, `tools`, `schema_output`, `triggers`, `instructions`) se extraen por `_extract_runtime()` y se usan en `routine_to_skill()` / `execute_skill()` sin contaminar el manifest.
  - `SKILL_MANIFEST_TOP_LEVEL` y `SKILL_MANIFEST_MWT_FIELDS` exportados para tests.

### 2. Autoría HITL end-to-end

- Endpoint `/workspaces/{id}/routines` valida SKILL.md y crea routine sin aprobación.
- Endpoint `/workspaces/{id}/routines/{id}/approve` aplica HITL.
- Endpoint `/workspaces/{id}/routines/{id}/run` ejecuta solo si está aprobada y activa.
- Test `test_skill_authoring_hitl_end_to_end` cubre el flujo completo.

### 3. Canary de hidden instruction

- Reutiliza `_detect_dangerous()` / `HIDDEN_INSTRUCTION_RE` de `app/src/security/injection.py`.
- Test `test_create_routine_rejects_hidden_instruction_in_skill_md` verifica 422 en API.

### 4. Multi-tenant

- `create_routine`, `get_routine`, `list_routines`, `update_routine`, `delete_routine` filtran por `(workspace_id, tenant_id)`.
- Test `test_routine_tenant_isolation` verifica que un routine de `tenant-a` no es accesible desde `tenant-b`.

### 5. Gate §2: skill por `@nombre`

- Test `test_at_mention_invokes_routine` crea `@cotizador`, lo aprueba, lo invoca desde chat y verifica resultado real (`12.5`).

## Resultados de test

```text
pytest app/tests/test_sl3a_skills.py app/tests/test_routines_crud.py -q  → 39 passed, 1 warning
pytest app/tests -q                                                       → 180 passed, 1 warning
```

Baseline SL2: `175 passed`. Incremento neto: **+5 tests**.

## Archivos modificados

- `app/src/skills.py` — refactor compiler → manifest canónico + runtime separado.
- `app/src/api.py` — usar `_extract_runtime()` para defaults de `persona_md`; validar name vs frontmatter.
- `app/tests/test_sl3a_skills.py` — tests de manifest, runtime, hidden instruction, tenant isolation, HITL authoring.
- `harness/reports/PLAN_SL3a_CLOSER_v1.md` — este plan.
- `harness/reports/SL3a_CLOSER_REPORT_v1.md` — reporte de cierre §8.

## Restricciones respetadas

- `ENT_OPS_STATE_MACHINE` y `PLB_ORCHESTRATOR` no modificados.
- No se inventaron datos MWT reales.
