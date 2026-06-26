# Auditoría Fugu — Fixes técnicos SL1b

**Fecha:** 2026-06-25  
**Rol:** fugu, auditor senior de SpaceLoom  
**Alcance:** revisión de los 5 fixes técnicos implementados por el orquestador para desbloquear SL1b.  
**Evidencia revisada:** `draft_engine.py`, `kb.py`, `security/injection.py`, `backup.py`, `update.py`, `test_sl1b_kb_drafts.py`, reporte anterior.  
**Tests ejecutados:** `tests/test_sl1b_kb_drafts.py` → **18 passed**.

---

## 1. `source_to_field_check` completo

**Veredicto:** `PASS` (con reservas menores).

**Qué está bien**
- Validación post-LLM robusta: cada `hard_fact_used` se reconcilia contra `kb_fact`.
- Doble vía de matching: `fact_id` directo, fallback por `(source_id, field_name, field_value)` exacto.
- Si el value no coincide, se genera blocker.
- El evidence pack expone `fact_id` y los facts enriquecidos incluyen `source_version`, `valid_from`, `valid_until`.
- Búsqueda de facts término por término para queries multi-palabra.
- `find_kb_fact` está workspace-scoped.

**Qué falta o está mal**
- **Solo valida lo que el LLM declara.** Si el modelo inventa un precio/SKU en `body_md` pero no lo pone en `hard_facts_used`, pasa limpio. Esto es un agujero contra el P0 “dato inventado”.
- Comparación exacta de strings sin normalización de moneda, espacios, comas o mayúsculas. Puede generar blockers falsos o permitir inventos con formato ligeramente diferente.
- No valida que el label `[S1]` citado en el cuerpo coincida con el evidence pack ni que `source_locator` sea coherente.

**Acción recomendada**
- Añadir una pasada sobre `body_md` que detecte campos duros no cubiertos por `hard_facts_used` y marque `requires_confirmation` o blocker.
- Documentar el schema de normalización (¿se incluye moneda en `value` o en `currency`?) y aplicar `strip()`/`casefold()` controlado.
- Añadir test donde `body_md` inventa un duro no declarado.

---

## 2. `stale_data_block` robusto

**Veredicto:** `PASS` (con reservas menores).

**Qué está bien**
- `_is_stale()` centralizada y simple.
- Si `valid_until < hoy`, se emite warning y `requires_confirmation = True`.
- Aplica tanto a facts con `fact_id` como a los resueltos por fallback.

**Qué falta o está mal**
- Compara strings ISO en lugar de objetos `datetime`. Funciona para el formato actual pero es frágil ante offsets o precisión variable.
- No verifica `valid_from` futuro (`kb.py` ya tiene `_is_vigente` pero no se usa en `draft_engine`).
- No hay política de **freshness por defecto**: fuentes MD/TXT sin `valid_until` nunca se marcan stale. El reporte anterior pedía `FreshnessGuard` con umbrales por tipo de fuente.
- Solo aplica a facts CSV, no a chunks/sources de texto que también pueden caducar.

**Acción recomendada**
- Parsear fechas con `datetime` antes de comparar.
- Usar `_is_vigente` o equivalente para rechazar facts con `valid_from` futuro.
- Definir `freshness_days` por tipo de source (ej. 90 días catálogo, 30 días precios) cuando no exista `valid_until`.
- Aplicar stale check a la metadata del source, no solo a facts.

---

## 3. Injection canaries

**Veredicto:** `PASS` (con reservas menores).

**Qué está bien**
- CSV: rechazo temprano de celdas con `=`, `+`, `-`, `@`.
- MD/TXT: detección de `<script>` y event handlers `on*`.
- HTML/XLSX/PDF: rechazo explícito hasta SL2.
- Integración en `kb.ingest_kb_source` vía `assert_safe_kb_source`.
- Tests de los tres vectores básicos pasan.

**Qué falta o está mal**
- **Regex HTML débil.** El patrón `<[^>]+\s(on\w+)\s*=` exige espacio antes del `=`, por lo que no detecta `onclick="..."` (sin espacio), ni comillas simples/backticks, ni atributos sin comillas, ni `javascript:` en `href`, ni SVG/scripts embebidos. Es un agujero real.
- **SKILL.md linter es código muerto.** `validate_skill_md` existe pero `assert_safe_kb_source` no la llama. No hay ingestor de skills en SL1b, pero si se deja ahí debe estar cableado o documentarse explícitamente.
- No hay tests para vectores más sofisticados (`<img src=x onerror="...">`, `javascript:`, `data:text/html`, etc.).
- No se detectan fórmulas CSV con espacios iniciales dentro de comillas (aunque `strip()` mitiga parcialmente).

**Acción recomendada**
- Corregir el regex de event handlers para aceptar cero o más espacios y comillas simples/dobles.
- Añadir detección de `javascript:`, `data:`, y SVG script.
- Integrar `validate_skill_md` en el flujo de skills (cuando exista) o eliminarla si no aplica; añadir test.
- Ampliar el banco de canaries y tests.

---

## 4. Backup/export/restore smoke test

**Veredicto:** `PASS` (con reservas menores).

**Qué está bien**
- Formato `.spaceloom` como zip con `meta.json` + `db.sqlite3`.
- Cifrado opcional con Fernet + PBKDF2-HMAC-SHA256 (480k iteraciones).
- Backup previo automático en `restore_db`.
- Smoke test E2E que simula corrupción y verifica restauración.

**Qué falta o está mal**
- **Generación de salt subóptima:** `Fernet.generate_key()[:SALT_LEN]` toma bytes de una cadena base64, no 16 bytes aleatorios completos. Debería ser `os.urandom(16)`.
- Fernet usa AES-128-CBC. Para datos comerciales sensibles se preferiría AES-256 (esto depende de la decisión CEO sobre cifrado).
- El smoke test verifica tablas y `schema_version`, pero **no datos de negocio** (workspaces, kb_source, drafts). Una corrupción parcial podría pasar.
- `restore_db` no valida `schema_version` ni compatibilidad antes de sobrescribir.
- Clave incorrecta devuelve `InvalidToken` crudo al usuario.

**Acción recomendada**
- Cambiar a `os.urandom(SALT_LEN)`.
- Ampliar `smoke_test_export_restore` para verificar al menos un workspace y una `kb_source`.
- Añadir validación de `schema_version` en `restore_db`.
- Capturar `InvalidToken` y devolver mensaje claro de passphrase incorrecto.

---

## 5. Auto-update firmado + rollback

**Veredicto:** `NEEDS_FIX` (defecto de seguridad real).

**Qué está bien**
- Ed25519 para firmas compactas y verificación rápida.
- Manifest con `version`, `payload_hash`, `signature`, `public_key`.
- `verify_update_manifest` verifica hash + firma.
- `install_update` verifica antes de copiar y preserva versión anterior.
- `rollback` restaura la versión anterior.
- Smoke test E2E de firma/instalación/rollback.

**Qué falta o está mal**
- **No hay clave pública pinned/confiable.** El manifest incluye su propia `public_key`, así que cualquiera puede generar un par Ed25519, firmar un payload malicioso y pasar la verificación. Esto invalida el propósito del auto-update firmado.
- No hay **downgrade protection**: se puede instalar una versión anterior.
- No se verifica que no haya **drafts/mutaciones pendientes** antes de instalar.
- Solo guarda **un único rollback**; si se instalan dos updates seguidos se pierde la versión original.
- No hay separación entre aplicación y updater; en producción `current_path` puede ser un directorio o bundle.

**Acción recomendada**
- Implementar **pinned public key** (hardcodeada o trust-on-first-use con fingerprint visible) y rechazar manifests firmados con otra clave.
- Añadir **downgrade protection** (`version` > current).
- Bloquear `install_update` si existen drafts/mutaciones pendientes.
- Considerar retener múltiples rollbacks o documentar la limitación.
- Añadir test de rechazo con clave pública distinta.

---

## Veredicto global de SL1b técnico

**`PASS condicional`.**

Los 5 bloqueantes técnicos de SL1b están implementados, los tests pasan y el nivel de madurez es suficiente para cerrar el hito técnico. Sin embargo, el fix de **auto-update tiene un defecto de seguridad real** (falta de pinned public key) que debe corregirse antes de declarar SL1b formalmente aprobado y definitivamente antes de SL4. Los demás fixes son aceptables para SL1b con mejoras menores.

---

## Cosas que aún bloquean SL2a (no técnicas)

| Bloqueante | Quién debe actuar |
|---|---|
| Auditoría formal de SL1b por fugu (este informe es el input; falta `AUDIT_SL1b_FUGU_v2.md` con PASS formal) | fugu / orquestador |
| Pack de datos MWT reales autorizado por Alvaro | Alvaro (CEO) |
| Decisiones CEO: carve-out/freeze scope, licencia FSL, dedicación dev, ¿SL5 entra o difiere?, calendario, criterio de adopción N, cifrado local obligatorio/condicional | Alvaro (CEO) |
| Credenciales IMAP de Kimi Work (solo bloquea SL5, no SL2a, pero debe decidirse scope) | Alvaro / ops |
| Presupuesto y certificados de firma de código Apple/Microsoft (bloquea SL4) | CEO / ops |

---

## Recomendación de próximo paso

1. **Orquestador corrige el defecto crítico de auto-update:** pinned public key + downgrade protection + bloqueo con mutaciones pendientes.
2. **Aplica mejoras menores en paralelo:** regex HTML, sal con `os.urandom`, stale check con `datetime`/freshness por defecto, validación de hechos no declarados en `body_md`.
3. **Actualiza documentación de seguridad/ops:**
   - `docs/security/AUTO_UPDATE_SPEC.md`
   - `docs/security/INJECTION_CANARY_MATRIX.md`
   - `docs/ops/BACKUP_RESTORE_RUNBOOK.md`
   - `docs/contracts/source_to_field_schema.md`
4. **fugu emite** `harness/reports/AUDIT_SL1b_FUGU_v2.md` con verdicto formal.
5. **Paralelamente Alvaro (CEO)** entrega el pack MWT real y las decisiones estratégicas pendientes.

**No se recomienda abrir SL2a hasta tener:** PASS formal de fugu, pack MWT real ingestado, decisiones CEO documentadas, `source_to_field_check` y `stale_data_block` refuerzos menores aplicados, y auto-update con pinned key.
