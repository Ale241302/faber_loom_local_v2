---
id: SPEC_SPACELOOM_SL3_5
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE — 2026-06-30 — cierre formal de SL3.5 (sellado + llave graduada)
aplica_a: [FaberLoom, MWT]
relacionado:
  - PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md
  - SPEC_SPACELOOM_ETAPA1_v1.md
  - IDX_SPACELOOM_ETAPA1_v1.md
---

# SPEC_SPACELOOM_SL3_5_v1 — Sellado + llave graduada

## Objetivo

Garantizar que el contenido de un workspace no se cuela en otro, incluso en modo confidencial con SQLCipher; y proveer backup/export/restore smoke test.

## Definition of Done

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | SQLCipher para workspaces confidenciales | ✅ | Schema v17: `confidential`, `passphrase`, `workspace_db_path`; DB separada por workspace. |
| 2 | Enrutamiento seguro por request | ✅ | `get_workspace_db`: plano vs cifrado; passphrase incorrecta → `401`. |
| 3 | Sellado HMAC | ✅ | HMACs de `kb_source`, `kb_fact`, `draft` con `seal_id`; tests bloquean leak simulado. |
| 4 | Fuga cross-workspace = 0 (modo plano) | ✅ | `test_kb_source_is_cross_workspace_isolated`, `test_draft_is_cross_workspace_isolated`. |
| 5 | Fuga cross-workspace = 0 (modo cifrado) | ✅ | `test_confidential_workspace_is_cross_workspace_isolated`. |
| 6 | Backup/export/restore smoke | ✅ | `test_backup_restore_confidential_workspace_smoke`. |
| 7 | Tenant isolation | ✅ | `test_confidential_workspace_tenant_isolation`; herencia cross-tenant bloqueada. |
| 8 | Tests | ✅ | 17 passed (SL3.5); suite total 194 passed. |

## Resultados de test

```text
pytest app/tests/test_sl3_5_seal.py -q
17 passed, 1 warning

pytest app/tests -q
194 passed, 1 warning
```

## Archivos clave

- `app/src/models.py` (schema v17)
- `app/src/db.py` (`connect_workspace_data_db`, `get_workspace_database_path`)
- `app/src/api.py` (`get_workspace_db`)
- `app/src/backup.py` (export con `db_key`, cifrado opcional)
- `app/tests/test_sl3_5_seal.py`
- `harness/reports/PLAN_SL3_5_CLOSER_v1.md`

## Notas

- Workspaces normales usan SQLite plano.
- PRC-04 resuelto con canarios sintéticos; no se requirió dataset real confidencial.

## Próximo hito

SL5 — Correo (diferido) o SL4 — Empaque desktop.

## Changelog

- v1.0 (2026-06-30): Cierre formal de SL3.5 a partir de `harness/reports/SL3_5_CLOSER_REPORT_v1.md`.
