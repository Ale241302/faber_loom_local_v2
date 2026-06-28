# Plan SL2a/b/c CLOSER — v2 (CERRADO)

**Fecha:** 2026-06-25  
**Loop:** §5 AUDIT → PLAN → IMPLEMENT → TEST → GATE → reporte  
**Fallback:** PRC-02 — corpus de prueba = fixtures con fuente conocida + KB demo COMERCIAL. No se requiere pack MWT real.

## Estado de cierre

- [x] Ingestión MD/TXT/CSV/XLSX/PDF + FTS5 + sellado SL2 verde.
- [x] Herencia entre workspaces implementada y testeada.
- [x] Cita end-to-end trazable (campo → documento → sección) testeada.
- [x] `stale_data_block` extendido a ingestión.
- [x] Multi-tenant con `tenant_id` en KB; herencia no cruza tenants.
- [x] Canarios de inyección para PDF (JavaScript) y XLSX (macros + hidden instructions).
- [x] Gate §6 completo (suite `test_sl2_*` verde + suite completa verde).

## Resultados de test

```
pytest app/tests/test_sl2_*.py -q  → 25 passed, 1 warning
pytest app/tests -q                 → 175 passed, 1 warning
```

Último estado base SL1b: `164 passed, 1 warning`.  
Incremento: +11 tests nuevos (herencia, cita e2e, canarios PDF/XLSX, stale ingestión, tenant isolation).

## Cambios aplicados

### Schema v15

- `workspace`: `parent_id TEXT REFERENCES workspace(id)`, `inherits_kb INTEGER DEFAULT 0`.
- `kb_chunk`: `tenant_id TEXT`.
- `kb_fact`: `tenant_id TEXT`.
- Backfill de `tenant_id` desde `kb_source` y workspace; índices en `kb_chunk`/`kb_fact`.

### Multi-tenant KB

- `ingest_kb_source` propaga `ctx.tenant_id` a `kb_source`, `kb_chunk` y `kb_fact`.
- Todas las queries de KB filtran por `tenant_id`.

### Herencia KB

- `_workspace_kb_scope(ctx, conn)` devuelve `[workspace_id]` o `[workspace_id, parent_id]` cuando `inherits_kb = 1` y mismo tenant.
- `list_kb_sources`, `get_kb_source`, `search_kb_chunks`, `search_kb_facts`, `get_kb_fact_by_id` y `get_kb_facts_by_source` usan el scope.
- Verificación HMAC por workspace dentro del scope (`_workspace_seals`), permitiendo leer facts/sources sellados con el seal del workspace origen.

### Workspace creation

- `WorkspaceCreate`/`WorkspaceRead` soportan `parent_id` e `inherits_kb`.
- `create_workspace` valida existencia del padre y mismo tenant.
- `api_create_workspace` devuelve `422` ante errores de validación del padre.

### Canarios de inyección

- `assert_safe_kb_source` detecta hidden-instruction overrides en texto extraído (MD/TXT/CSV/PDF/XLSX).
- `kb_extractors._pdf_contains_javascript` rechaza PDFs con acciones `/JavaScript`.
- `kb_extractors._xlsx_contains_macros` rechaza XLSX que contengan `xl/vbaProject.bin`.
- Extensión `.xlsm` aceptada en el endpoint para que el canario macro pueda actuar.

### `stale_data_block` en ingestión

- `_table_rows_to_facts` detecta `valid_from` futuro / `valid_until` pasado y añade advertencias.
- `ingest_kb_source` actualiza `meta_json` con `extraction_warnings` y `stale_data_block = True` cuando aplica.

### Cita end-to-end

- `draft_engine._validate_citations` ahora enriquece cada `hard_fact` con `source_locator` y `source_sheet`, trazando el campo al documento y sección origen.

### Tests nuevos

- `app/tests/test_sl2_kb_inheritance.py`: herencia directa, aislamiento sin herencia, bloqueo cross-tenant, aislamiento de sources por tenant.
- `app/tests/test_sl2_citation_e2e.py`: cita desde draft hasta source sheet y locator usando XLSX fixture.
- `app/tests/test_sl2_injection_canaries.py`: PDF con JavaScript, XLSX con macros, hidden instructions en PDF/XLSX, y control limpio.
- `app/tests/test_sl2_kb_ingestion.py`: + test `stale_data_block` en CSV vencido.
- `app/tests/test_sl1b_kb_drafts.py`: test de canary de inyección ajustado para esperar rechazo 422 en lugar de ingestión.

## Restricciones respetadas

- `ENT_OPS_STATE_MACHINE` y `PLB_ORCHESTRATOR` no modificados.
- No se inventaron datos MWT reales.
