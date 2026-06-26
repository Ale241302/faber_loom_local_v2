# Fixes implementados para bloqueantes SL1b (post-auditoría fugu v2)

**Fecha:** 2026-06-25  
**Autor:** orquestador  
**Tests:** 51 passed, 1 warning (`app/tests` completo).

---

## Resumen

Se atendieron las 3 condiciones pendientes del veredicto `PASS condicional` de `harness/reports/AUDIT_SL1b_FUGU_v2.md`, más limpieza menor.

| Condición | Archivos tocados | Estado |
|---|---|---|
| Auto-update: eliminar fallback de set vacío | `app/src/update.py` | ✅ |
| Build: declarar `cryptography` y regenerar `uv.lock` | `app/pyproject.toml`, `app/uv.lock` | ✅ |
| Inventos del LLM: detectar valores duros sin origen KB | `app/src/draft_engine.py`, `app/tests/test_sl1b_kb_drafts.py` | ✅ |
| Limpieza: eliminar `_is_vigente` muerto, corregir `rollback` version | `app/src/kb.py`, `app/src/update.py` | ✅ |

---

## 1. Auto-update (`app/src/update.py`)

- `verify_update_manifest` ahora **rechaza** explícitamente si no se proporciona ninguna clave pública confiable (ni por parámetro ni en el set global). No hay fallback a "cualquier firma válida".
- Corregido `rollback()` para devolver la versión real restaurada (`chosen["version"]`).

## 2. Dependencias (`app/pyproject.toml`, `app/uv.lock`)

- Agregada `cryptography>=42.0.0` a `dependencies`.
- Regenerado `uv.lock` (`Added cryptography v49.0.0`).

## 3. Detección de valores inventados (`app/src/draft_engine.py`)

- Nuevas funciones `_extract_hard_tokens` y `_scan_for_invented_facts`.
- Extrae del `body_md` precios (con/sin moneda), cantidades grandes, SKUs y fechas ISO.
- Si un token duro no coincide con ningún valor/entity_key del evidence pack, se emite warning y se fuerza `requires_confirmation`.
- Test nuevo: `test_invented_hard_value_in_body_is_flagged` (body USD 99.00 vs KB 12.50).

## 4. Limpieza

- Eliminada `_is_vigente` no utilizada en `app/src/kb.py`.

---

## Próximo paso

Pasar a **fugu** para auditoría final y, si todo está OK, emitir `AUDIT_SL1b_FUGU_v3.md` con veredicto formal `PASS`.
