# Auditoría Fugu — Revisión de fixes técnicos SL1b

**Fecha:** 2026-06-25  
**Rol:** fugu, auditor senior de SpaceLoom  
**Alcance:** re-auditoría de los 5 bloqueantes técnicos de SL1b tras los fixes del orquestador.  
**Evidencia revisada:** `app/src/update.py`, `app/src/backup.py`, `app/src/security/injection.py`, `app/src/draft_engine.py`, `app/src/kb.py`, `app/tests/test_sl1b_kb_drafts.py`, reportes previos.  
**Tests ejecutados:** `pytest app/tests` → **50 passed**.

---

## 1. `source_to_field_check` + hechos no declarados

**Veredicto:** `PASS` (con reservas).

**Qué está bien**
- Reconciliación robusta de cada `hard_fact_used` contra el KB.
- Doble vía de matching: `fact_id` directo y fallback por `(source_id, field_name, field_value)`.
- Normalización de valores (`strip`, lowercasing, palabras de moneda) para reducir falsos blockers.
- Cuando un source CSV es relevante se cargan **todos** sus facts (`get_kb_facts_by_source`), eliminando la dependencia de términos exactos en la query.
- Scan de hechos no declarados en `body_md` que fuerza `requires_confirmation` cuando un valor duro del KB aparece en el cuerpo sin estar en `hard_facts_used`.
- `valid_from` futuro y `valid_until` pasado generan blocker/warning usando `datetime` aware.

**Qué falta o está mal**
- **No detecta valores inventados que no estén en el KB.** El scan solo compara contra facts conocidos; si el LLM escribe un precio/SKU nuevo (ej. “USD 99.00”) que no existe en el KB, pasa limpio. El P0 “dato inventado sin fuente” sigue parcialmente expuesto.
- El matching por `field_name` es exacto: si el LLM usa `precio` y el CSV tiene `precio_usd`, puede generar un blocker falso.
- No se valida que el label `[S1]` citado en `body_md` coincida con el evidence pack ni que `source_locator` sea coherente.

**Acción recomendada**
- Agregar una segunda pasada que extraiga tokens “duros” (precios, SKUs, cantidades, fechas) del `body_md` y los compare contra el evidence pack; si un token duro no tiene origen KB, marcar `requires_confirmation` o blocker.
- Documentar el schema de normalización y considerar sinónimos de columnas (`precio` ↔ `precio_usd`).
- Añadir test donde el LLM inventa un valor no presente en el KB.

---

## 2. `stale_data_block`

**Veredicto:** `PASS`.

**Qué está bien**
- Comparaciones con `datetime` aware en `_is_stale` y `_is_not_yet_valid`.
- `valid_from` futuro genera blocker.
- `valid_until` pasado genera warning y fuerza `requires_confirmation`.
- Ventanas de frescura por defecto: MD/TXT 90 días, CSV 30 días, aplicadas por `source_created_at`.
- El stale check aplica tanto a facts individuales como a la metadata del source.

**Qué falta o está mal**
- `kb.py` aún define `_is_vigente` comparando strings ISO, pero no se usa en `draft_engine`; es código muerto.
- La política de frescura por defecto es global; no permite override por source en SL1b.
- Solo se advierte, no se bloquea, cuando un source supera su ventana de frescura por defecto (aceptable para SL1b, pero debe documentarse).

**Acción recomendada**
- Eliminar o reutilizar `_is_vigente` en `kb.py`.
- Documentar la política de frescura y su comportamiento HITL.
- En SL2 considerar `valid_until` explícito por source y posibilidad de override.

---

## 3. Injection canaries

**Veredicto:** `PASS`.

**Qué está bien**
- Regex mejorado detecta `<script`, `</script>`, `javascript:`, `data:`, `vbscript:` y event handlers (`on*`) con comillas simples/dobles/backticks o sin ellas.
- CSV: rechazo de celdas con `=`, `+`, `-`, `@`.
- HTML/XLSX/PDF rechazados hasta SL2.
- Tests nuevos pasan: `javascript:` en MD y `<img onerror>`.
- Integrado en `kb.ingest_kb_source` vía `assert_safe_kb_source`.

**Qué falta o está mal**
- **SKILL.md linter sigue siendo código muerto.** `validate_skill_md` no es llamada por `assert_safe_kb_source`; si no aplica a SL1b, debería eliminarse o documentarse explícitamente.
- Vectores menores no cubiertos: atributo event handler sin espacio previo (`<img/onerror=...>`), `expression()` CSS en IE, obfuscación por HTML comments, y esquemas con tab/newline dentro de `javascript:`.
- No hay canary para fórmulas CSV con espacios iniciales dentro de comillas (mitigado parcialmente por `strip()`).

**Acción recomendada**
- Cablear `validate_skill_md` al flujo de skills futuro o eliminarla.
- Añadir tests para `<img onerror>` sin comillas, `data:text/html`, y `javascript:` con espacios.
- Documentar la matriz de canaries para SL2.

---

## 4. Backup/export/restore

**Veredicto:** `PASS`.

**Qué está bien**
- Salt generado con `os.urandom(16)`.
- `restore_db` valida `schema_version` del backup contra `SCHEMA_VERSION`.
- `InvalidToken` se traduce a mensaje claro de passphrase incorrecto/corrupto.
- Smoke test verifica datos de negocio (`workspace_count >= 1`, `kb_source_count >= 1`) y tablas.
- Fix del handle SQLite en Windows usando `mkdtemp` + `shutil.rmtree(..., ignore_errors=True)`.
- Backup previo automático antes de sobrescribir.

**Qué falta o está mal**
- **`cryptography` no está declarado en `pyproject.toml` ni en `uv.lock`.** En un entorno fresco (como el `.venv` raíz) el import falla. Esto es un defecto de build/reproducibilidad.
- Si `_read_schema_version` devuelve `None` (backup antiguo o corrupto), `restore_db` permite la restauración en lugar de rechazarla.
- No hay verificación de integridad del archive (checksum/hash).
- Cifrado sigue siendo AES-128-CBC vía Fernet; la decisión de AES-256 queda pendiente del CEO.
- No se valida passphrase vacía.

**Acción recomendada**
- Agregar `cryptography` a las dependencias del proyecto y regenerar `uv.lock`.
- Rechazar restore cuando `archive_schema` sea `None`.
- Documentar decisiones de cifrado en `docs/security/BACKUP_RESTORE_RUNBOOK.md`.

---

## 5. Auto-update firmado + rollback

**Veredicto:** `PASS condicional`.

**Qué está bien**
- `verify_update_manifest` / `install_update` aceptan un set de claves públicas confiables y rechazan manifests firmados con otra clave.
- `add_trusted_public_key` / `set_trusted_public_keys` exponen la configuración.
- Downgrade protection rechaza versiones menores o iguales (`_is_newer_version`).
- `pending_check` bloquea la instalación si hay mutaciones pendientes.
- Multi-rollback: retiene las últimas 5 versiones, con `list_rollback_versions` y `rollback(to_version=...)`.
- Tests nuevos cubren clave incorrecta, downgrade y mutaciones pendientes; el smoke test ejercita pinned key.

**Qué falta o está mal**
- **No hay clave pública pinned por defecto.** `_TRUSTED_PUBLIC_KEYS` arranca vacío y `verify_update_manifest` hace *fallback* a verificación de firma pura cuando el set está vacío. En producción, olvidar configurar el set implica aceptar cualquier clave válida: el defecto de seguridad original persiste como modo fallback.
- No hay wiring con endpoints de la app ni separación updater/aplicación (aceptable para SL1b, pero obligatorio antes de SL4).
- En Windows, reemplazar el binario en ejecución seguirá fallando; no se resuelve el problema del archivo bloqueado.
- `rollback()` devuelve siempre `versions[0]["version"]` aunque se haya restaurado una versión específica via `to_version`.

**Acción recomendada**
- Eliminar el fallback de “set vacío”: `verify_update_manifest` debe fallar explícitamente si no se proporciona ninguna clave confiable, y/o embarcar una clave pública pinned hardcodeada para producción.
- Corregir el valor de retorno de `rollback()` para reflejar la versión real restaurada.
- Crear el diseño del updater separado para SL4 y documentarlo.

---

## Veredicto global de SL1b técnico

**`PASS condicional`.**

Los 5 bloqueantes técnicos originales están implementados y los 50 tests de `app/tests` pasan. El nivel de madurez es suficiente para considerar SL1b técnicamente cerrado **con las siguientes condiciones antes de declarar PASS formal**:

1. **Auto-update:** eliminar el fallback de set de claves vacío y/o hardcodear la clave pública de producción.
2. **Build:** declarar `cryptography` como dependencia en `pyproject.toml` y `uv.lock`.
3. **Inventos del LLM:** reforzar `_scan_for_undisclosed_facts` para detectar valores duros en `body_md` que no existan en el KB, no solo los que falten en `hard_facts_used`.

---

## Cosas que aún bloquean SL2a (no técnicas)

| Bloqueante | Quién debe actuar |
|---|---|
| Emisión de `AUDIT_SL1b_FUGU_v2.md` con PASS formal | fugu / orquestador |
| Pack de datos MWT reales autorizado y validado por Alvaro | Alvaro (CEO) |
| Decisiones CEO: scope/freeze, licencia FSL, dedicación dev, ¿SL5 incluido o diferido?, calendario, criterio de adopción N, cifrado local obligatorio/condicional | Alvaro (CEO) |
| Documentación de seguridad/ops: `AUTO_UPDATE_SPEC.md`, `INJECTION_CANARY_MATRIX.md`, `BACKUP_RESTORE_RUNBOOK.md`, `source_to_field_schema.md` | orquestador / fugu |
| Certificados de firma de código Apple/Microsoft (bloquea SL4, no SL2a) | CEO / ops |
| Credenciales IMAP de Kimi Work (bloquea SL5 si entra en scope) | Alvaro / ops |

---

## Recomendación de próximo paso

1. **Orquestador** aplica los 3 ajustes técnicos menores restantes:
   - Quitar fallback de claves vacías en `update.py` y preparar la clave pinned de producción.
   - Agregar `cryptography` al `pyproject.toml` de `app/` y regenerar `uv.lock`.
   - Reforzar la detección de valores inventados en `draft_engine.py`.
2. **fugu** emite `harness/reports/AUDIT_SL1b_FUGU_v2.md` con veredicto formal.
3. **Paralelamente**, Alvaro (CEO) entrega el pack MWT real y las decisiones estratégicas pendientes.
4. Una vez cumplidas las condiciones, declarar SL1b aprobado y abrir SL2a.

**No se recomienda abrir SL2a antes de:** PASS formal de fugu, datos MWT reales ingestados, decisiones CEO documentadas, y auto-update con clave pinned sin fallback.
