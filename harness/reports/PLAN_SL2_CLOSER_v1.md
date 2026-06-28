# Plan SL2a/b/c CLOSER — v1

**Fecha:** 2026-06-25  
**Loop:** §5 AUDIT → PLAN → IMPLEMENT → TEST → GATE → reporte  
**Fallback:** PRC-02 — corpus de prueba = fixtures con fuente conocida + KB demo COMERCIAL (`docs/ENT_COMERCIAL_*`). No se requiere pack MWT real.

## DoD objetivo

1. Ingestión MD/TXT/CSV/XLSX/PDF + FTS5 + sellado SL2 — mantener verde.
2. Herencia entre workspaces: hijo hereda KB del padre según regla explícita; test.
3. Cita end-to-end: campo del output → documento → sección, trazable y testeada.
4. `stale_data_block` robusto: extender a ingestión (warning en fuente vencida).
5. Multi-tenant: toda query de KB incluye `tenant_id/Context`; herencia no filtra cross-tenant.
6. Tests `test_sl2_*` verdes + test nuevo cita e2e + test herencia.
7. Canaries de inyección para PDF/XLSX: hidden instructions en texto extraído no ejecutan.
8. Gate §6 completo.

## Cambios técnicos

### 1. Schema v15

- `workspace`: `parent_id TEXT REFERENCES workspace(id)`, `inherits_kb INTEGER DEFAULT 0`.
- `kb_chunk`: `tenant_id TEXT`.
- `kb_fact`: `tenant_id TEXT`.
- Backfill `tenant_id` desde `kb_source` para filas existentes.
- Índices `idx_kb_chunk_workspace_tenant` e `idx_kb_fact_workspace_tenant`.

### 2. Multi-tenant en KB

- `ingest_kb_source` inserta `ctx.tenant_id` en `kb_chunk`/`kb_fact`.
- `_table_rows_to_facts` recibe `tenant_id` y lo persiste.
- Todas las queries de KB filtran por `tenant_id`.

### 3. Herencia KB

- Helper `_workspace_kb_scope(ctx, conn)` devuelve `[workspace_id]` o `[workspace_id, parent_id]` si `inherits_kb = 1`.
- `list_kb_sources`, `get_kb_source`, búsquedas (`search_kb_chunks`, `search_kb_facts`), y lookups (`get_kb_fact_by_id`, `find_kb_fact`, `get_kb_facts_by_source`, `get_kb_chunk_by_id`) usan el scope.
- La herencia solo cruza workspaces con igual `tenant_id`.

### 4. Workspace creation con parent_id

- `WorkspaceCreate`/`WorkspaceRead`/`WorkspaceUpdate` añaden `parent_id` e `inherits_kb`.
- `create_workspace` valida existencia del padre y mismo tenant.

### 5. Canarios de inyección PDF/XLSX

- `assert_safe_kb_source("txt", text)` detecta hidden-instruction overrides (`ignore previous instructions`, etc.).
- PDF/XLSX ya se re-sanitizan como `txt` tras extracción, por tanto quedan cubiertos.
- Tests generan PDF/XLSX maliciosos y afirman rechazo 422.

### 6. stale_data_block en ingestión

- `_table_rows_to_facts` detecta `valid_from` futuro / `valid_until` pasado y añade `stale_warning` a `extraction_warnings`.
- Test ingest CSV vencido y verifica warning.

### 7. Cita end-to-end

- Nuevo `app/tests/test_sl2_citation_end_to_end.py`:
  - Ingest CSV/XLSX/PDF fixtures.
  - Fake provider genera draft citando fact real.
  - Verifica que `hard_facts_json` conserva `source_locator`, `source_sheet`, `source_version` y se traza al source.

### 8. Tests

- `app/tests/test_sl2_kb_inheritance.py`: herencia directa y aislamiento cross-tenant.
- `app/tests/test_sl2_citation_end_to_end.py`: cita e2e.
- `app/tests/test_sl2_kb_ingestion.py`: + canarios PDF/XLSX + stale.

## Restricciones

- No tocar `ENT_OPS_STATE_MACHINE` ni `PLB_ORCHESTRATOR`.
- No inventar datos MWT reales.
