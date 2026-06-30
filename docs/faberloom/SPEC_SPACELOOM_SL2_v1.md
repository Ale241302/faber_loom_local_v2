---
id: SPEC_SPACELOOM_SL2
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE — 2026-06-30 — cierre formal de SL2 (workspaces + KB)
aplica_a: [FaberLoom, MWT]
relacionado:
  - PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md
  - SPEC_SPACELOOM_ETAPA1_v1.md
  - SPEC_SPACELOOM_SELFHOSTED_v1.2.md
  - IDX_SPACELOOM_ETAPA1_v1.md
---

# SPEC_SPACELOOM_SL2_v1 — Workspaces + KB

## Objetivo

Permitir crear workspaces por cliente/área con herencia, subir conocimiento en múltiples formatos (MD/TXT/CSV/XLSX/PDF) y citar fuentes end-to-end, con canarios de inyección y bloqueo de datos vencidos.

## Definition of Done

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Ingestión multi-formato + FTS5 | ✅ | `test_sl2_kb_ingestion.py` 8/8 passed. |
| 2 | Herencia workspace padre/hijo | ✅ | `test_sl2_kb_inheritance.py` 4/4 passed. |
| 3 | Cita campo→documento→sección | ✅ | `test_sl2_citation_e2e.py` 1/1 passed. |
| 4 | `stale_data_block` en ingestión y drafts | ✅ | CSV vencido + blockers por facts vencidos. |
| 5 | Multi-tenant en KB | ✅ | Filtros `tenant_id` en chunks/facts/sources + test cross-tenant. |
| 6 | Canarios de inyección | ✅ | PDF JavaScript, XLSX macros, hidden instructions — 5/5 passed. |
| 7 | Suite SL2 verde | ✅ | 25 passed; suite total 175 passed. |

## Resultados de test

```text
pytest app/tests/test_sl2_*.py -q
25 passed, 1 warning

pytest app/tests -q
175 passed, 1 warning
```

## Archivos clave

- `app/src/models.py` (schema v15)
- `app/src/db.py` (`WORKSPACE_COLUMNS`, `create_workspace` con padre/tenant)
- `app/src/kb.py` (`_workspace_kb_scope`, `_workspace_seals`, propagación `tenant_id`)
- `app/src/draft_engine.py` (`source_sheet`, `source_locator`)
- `app/src/kb_extractors.py` (detección JS en PDF, macros XLSX)
- `app/src/security/injection.py` (`validate_hidden_instructions`)
- `app/src/api.py`
- `app/tests/test_sl2_kb_ingestion.py`
- `app/tests/test_sl2_kb_inheritance.py`
- `app/tests/test_sl2_citation_e2e.py`
- `app/tests/test_sl2_injection_canaries.py`

## Notas de implementación

- La herencia no cruza tenants.
- HMAC soporta scope multi-workspace con `_workspace_seals`.
- Los canarios no ejecutan contenido; inspeccionan estructura del archivo.

## Próximo hito

SL3a — Skills / Routine Hub.

## Changelog

- v1.0 (2026-06-30): Cierre formal de SL2 a partir de `harness/reports/SL2_CLOSER_REPORT_v1.md`.
