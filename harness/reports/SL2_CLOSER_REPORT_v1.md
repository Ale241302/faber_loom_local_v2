# Reporte de cierre SL2a/b/c — v1

**Fecha:** 2026-06-25  
**Agente:** Kimi Code CLI  
**Loop CLOSER:** §5 AUDIT → PLAN → IMPLEMENT → TEST → GATE → REPORTE

## Estado

SL2a/b/c **CERRADO**.

## DoD verificado

| # | Requisito | Estado | Evidencia |
|---|-----------|--------|-----------|
| 1 | Ingestión MD/TXT/CSV/XLSX/PDF + FTS5 + sellado SL2 verde | ✅ | `test_sl2_kb_ingestion.py` 8/8 passed |
| 2 | Herencia workspace padre/hijo | ✅ | `test_sl2_kb_inheritance.py` 4/4 passed |
| 3 | Cita end-to-end campo→documento→sección | ✅ | `test_sl2_citation_e2e.py` 1/1 passed |
| 4 | `stale_data_block` robusto en ingestión y drafts | ✅ | Test CSV vencido + blockers por facts vencidos en drafts |
| 5 | Multi-tenant (`tenant_id` en queries KB) | ✅ | Filtros en chunks/facts/sources + test cross-tenant |
| 6 | `test_sl2_*` verdes + tests nuevos | ✅ | `25 passed` |
| 7 | Canarios PDF/XLSX (JS, macros, hidden instructions) | ✅ | `test_sl2_injection_canaries.py` 5/5 passed |
| 8 | Gate §6 completo | ✅ | Suite completa `175 passed, 1 warning` |

## Resultados de test

```text
$ app/.venv/Scripts/python -m pytest app/tests/test_sl2_*.py -q
25 passed, 1 warning in 11s

$ app/.venv/Scripts/python -m pytest app/tests -q
175 passed, 1 warning in 56s
```

Último baseline SL1b: `164 passed`.  
Incremento neto: **+11 tests**.

## Archivos modificados

- `app/src/models.py` — schema v15, `WorkspaceCreate`/`WorkspaceRead` con parent_id/inherits_kb, `KBFactRead`/`KBChunkRead` con tenant_id.
- `app/src/db.py` — `WORKSPACE_COLUMNS`, `create_workspace` con validación de padre/tenant.
- `app/src/kb.py` — `_workspace_kb_scope`, `_workspace_seals`, propagación `tenant_id`, `stale_data_block` en meta, HMAC por workspace en scope.
- `app/src/draft_engine.py` — `source_sheet`/`source_locator` en evidence pack y enriched facts.
- `app/src/kb_extractors.py` — detección de JavaScript en PDF y macros en XLSX.
- `app/src/security/injection.py` — `validate_hidden_instructions` reutilizable.
- `app/src/api.py` — manejo de `ValueError` en `api_create_workspace`, extensión `.xlsm`.
- `app/tests/test_sl2_kb_ingestion.py` — + test stale CSV.
- `app/tests/test_sl2_kb_inheritance.py` — nuevo.
- `app/tests/test_sl2_citation_e2e.py` — nuevo.
- `app/tests/test_sl2_injection_canaries.py` — nuevo.
- `app/tests/test_sl1b_kb_drafts.py` — canary de inyección ajustado a rechazo 422.
- `harness/reports/PLAN_SL2_CLOSER_v2.md` — plan actualizado.
- `harness/reports/SL2_CLOSER_REPORT_v1.md` — este reporte.

## Notas de implementación

- La herencia no cruza tenants: `_workspace_kb_scope` verifica `row["tenant_id"] == ctx.tenant_id`.
- La verificación HMAC soporta scope multi-workspace usando `_workspace_seals`, así un hijo puede leer facts/sources sellados con el seal del padre.
- Los canarios no dependen de ejecutar contenido: el PDF se parsea con `pdfminer` buscando acciones `/JavaScript`; el XLSX se inspecciona como ZIP buscando `xl/vbaProject.bin`; el texto extraído se re-sanitiza contra hidden instructions.

## Próximos pasos recomendados

- No avanzar a SL3 hasta que el usuario confirme el cierre formal de SL2.
- Mantener `ENT_OPS_STATE_MACHINE` y `PLB_ORCHESTRATOR` congelados según restricción.
