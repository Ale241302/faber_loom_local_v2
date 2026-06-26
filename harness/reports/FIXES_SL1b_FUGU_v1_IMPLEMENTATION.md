# Fixes implementados para bloqueantes SL1b (post-auditoría fugu v1)

**Fecha:** 2026-06-25  
**Autor:** orquestador  
**Tests:** 50 passed, 1 warning (`app/tests` completo).

---

## Resumen

Se atendieron los hallazgos de `harness/reports/AUDIT_FIXES_SL1b_FUGU_v1.md`.

| Fix | Archivos tocados | Estado |
|---|---|---|
| Auto-update: pinned public key + downgrade + pending mutations + multi-rollback | `app/src/update.py`, `app/tests/test_sl1b_kb_drafts.py` | ✅ |
| Backup: salt `os.urandom`, schema-version check, InvalidToken message, business data verification | `app/src/backup.py`, `app/tests/test_sl1b_kb_drafts.py` | ✅ |
| Injection canaries: regex HTML robusto, `javascript:`, `data:`, event handlers, tests | `app/src/security/injection.py`, `app/tests/test_sl1b_kb_drafts.py` | ✅ |
| Draft engine: fechas con `datetime`, `valid_from` futuro, freshness por defecto, scan de hechos no declarados | `app/src/draft_engine.py`, `app/src/kb.py`, `app/tests/test_sl1b_kb_drafts.py` | ✅ |

---

## 1. Auto-update (`app/src/update.py`)

- **Pinned public key:** `verify_update_manifest` y `install_update` aceptan un set de claves públicas confiables. Si se proporciona, el manifest cuya clave no esté en el set se rechaza. Se expone `set_trusted_public_keys` / `add_trusted_public_key` / `get_trusted_public_keys`.
- **Downgrade protection:** `install_update` acepta `current_version` y rechaza versiones menores o iguales (`_is_newer_version`).
- **Pending mutations check:** `install_update` acepta `pending_check: Callable[[], bool]`; si devuelve `True`, se bloquea la instalación.
- **Multi-rollback:** los backups previos se guardan como `<binary>.<version>.<timestamp>.old`; `list_rollback_versions` enumera versiones; `rollback` puede restaurar la más reciente o una versión específica (`to_version`). Se retienen las últimas 5 versiones.
- **Tests:** `test_update_rejects_wrong_public_key`, `test_update_rejects_downgrade`, `test_update_blocks_pending_mutations`; el smoke test ahora ejercita pinned key, downgrade y pending check.

## 2. Backup/restore (`app/src/backup.py`)

- **Salt aleatorio:** `_encrypt` usa `os.urandom(SALT_LEN)`.
- **Schema-version check:** `restore_db` valida que el backup tenga `SCHEMA_VERSION` compatible.
- **Mensaje claro:** `InvalidToken` se traduce a `ValueError("Incorrect passphrase or corrupted archive")`.
- **Datos de negocio:** `smoke_test_export_restore` verifica `workspace_count >= 1` y `kb_source_count >= 1`.
- **Windows temp fix:** `_read_schema_version` usa `mkdtemp` + `shutil.rmtree(..., ignore_errors=True)` para evitar bloqueo de handle SQLite.

## 3. Injection canaries (`app/src/security/injection.py`)

- Regex HTML mejorado: detecta `<script`, `</script>`, `javascript:`, `data:`, `vbscript:`, event handlers (`onerror`, `onclick`, …) con comillas simples/dobles/backticks o sin ellas.
- Tests para `javascript:` en MD y `<img onerror>`.

## 4. Draft engine (`app/src/draft_engine.py`) + KB (`app/src/kb.py`)

- **Fechas robustas:** `_parse_iso` devuelve `datetime` aware (UTC si no hay offset). `_is_stale` y `_is_not_yet_valid` usan comparación de objetos `datetime`.
- **`valid_from` futuro:** genera blocker.
- **Freshness por defecto:** fuentes MD/TXT 90 días, CSV 30 días; advertencia si se supera.
- **Hechos no declarados:** `_scan_for_undisclosed_facts` compara valores "duros" (con dígitos o caracteres de SKU) mencionados en `body_md` contra los declarados en `hard_facts_used`. Si falta, fuerza `requires_confirmation`.
- **Evidence pack completo por source:** cuando un source CSV es relevante, se cargan **todos** sus facts (`get_kb_facts_by_source`) para que el source-to-field check no dependa de que el LLM haya mencionado el término exacto.
- **Normalización:** `_normalize_value` estandariza espacios, mayúsculas/minúsculas y palabras de moneda para reducir falsos blockers.

---

## Próximo paso

Pasar a **fugu** para auditoría formal y emisión de `AUDIT_SL1b_FUGU_v2.md`.
