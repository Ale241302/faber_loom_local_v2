---
id: SPEC_SPACELOOM_SL3a
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE — 2026-06-30 — cierre formal de SL3a (skills / Routine Hub)
aplica_a: [FaberLoom, MWT]
relacionado:
  - PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md
  - SPEC_SPACELOOM_ETAPA1_v1.md
  - SCH_FB_SKILL_MANIFEST_v2.md
  - IDX_SPACELOOM_ETAPA1_v1.md
---

# SPEC_SPACELOOM_SL3a_v1 — Skills / Routine Hub

## Objetivo

Permitir autorizar livianamente skills en formato SKILL.md, invocar rutinas por `@nombre`, y asegurar que el manifest emitido sea un subconjunto del schema canónico.

## Definition of Done

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Skill creada por `@nombre` end-to-end | ✅ | `@cotizador` ejecuta en `test_at_mention_invokes_routine`. |
| 2 | Autoría HITL | ✅ | `test_skill_authoring_hitl_end_to_end`: create → approve → run. |
| 3 | Manifest canónico | ✅ | `compile_skill_md` emite solo claves de `SKILL_MANIFEST_TOP_LEVEL` y `SKILL_MANIFEST_MWT_FIELDS`. |
| 4 | Runtime separado | ✅ | `_extract_runtime()` provee persona/tools/schema/triggers sin formar parte del manifest. |
| 5 | Canario de inyección | ✅ | Skill con hidden instruction → `422`. |
| 6 | Tenant isolation | ✅ | `test_routine_tenant_isolation`. |
| 7 | Tests | ✅ | 39 passed (SL3a); suite total 180 passed. |

## Resultados de test

```text
pytest app/tests/test_sl3a_skills.py app/tests/test_routines_crud.py -q
39 passed, 1 warning

pytest app/tests -q
180 passed, 1 warning
```

## Archivos clave

- `app/src/skills.py` (compiler canónico + runtime separado)
- `app/src/api.py` (defaults de persona, validación name/frontmatter)
- `app/src/models.py`
- `app/src/db.py`
- `app/tests/test_sl3a_skills.py`
- `harness/reports/PLAN_SL3a_CLOSER_v1.md`

## Próximo hito

SL3b/c — WorkLoom + gold loop.

## Changelog

- v1.0 (2026-06-30): Cierre formal de SL3a a partir de `harness/reports/SL3a_CLOSER_REPORT_v1.md`.
