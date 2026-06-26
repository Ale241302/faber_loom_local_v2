# Auditoría Fugu — Veredicto formal SL1b

**Fecha:** 2026-06-25  
**Rol:** fugu, auditor senior de SpaceLoom  
**Alcance:** validación final de los bloqueantes técnicos de SL1b tras tres ciclos de fixes.  
**Tests ejecutados:** `pytest app/tests` → **51 passed, 1 warning**.

---

## Resumen ejecutivo

**Veredicto global técnico de SL1b: `PASS` formal.**

Los 5 bloqueantes de seguridad/datos identificados en la auditoría original están implementados y verificados por tests. Las 3 condiciones del `PASS condicional` de `AUDIT_SL1b_FUGU_v2.md` fueron resueltas:

1. ✅ Auto-update sin fallback de claves vacías.
2. ✅ `cryptography` declarada en `pyproject.toml` y `uv.lock`.
3. ✅ Detección de valores duros inventados por el LLM sin origen KB.

---

## Veredicto por dimensión

| Dimensión | Veredicto | Justificación breve |
|---|---|---|
| `source_to_field_check` | **PASS** | Cada `hard_fact_used` se reconcilia contra `kb_fact`; hechos no declarados en `body_md` se detectan; valores duros inventados (precios, SKUs, cantidades, fechas ISO) sin origen KB fuerzan `requires_confirmation`. |
| `stale_data_block` | **PASS** | `valid_from` futuro bloquea; `valid_until` pasado genera warning + confirmación; ventanas de frescura por defecto por tipo de source. |
| `injection canaries` | **PASS** | Rechaza `<script`, event handlers, `javascript:`, `data:`, `vbscript:` y fórmulas CSV. Adecuado para SL1b. |
| `backup/restore` | **PASS** | Salt aleatorio, schema-version check, mensaje claro para passphrase incorrecto, verificación de datos de negocio, `cryptography` declarado. |
| `auto-update firmado` | **PASS** | Clave pública pinned obligatoria, downgrade protection, bloqueo de mutaciones pendientes, multi-rollback. |

---

## Issues menores persistentes (no bloquean SL1b)

1. **Docstring obsoleto en `update.py`:** `verify_update_manifest` aún menciona un fallback a verificación de firma pura que ya no existe.
2. **`validate_skill_md` es código muerto** en `app/src/security/injection.py` (no se invoca en SL1b).
3. **Matching exacto de `field_name`:** `precio` vs `precio_usd` puede generar blockers falsos; no se normalizan sinónimos de columnas.
4. **Labels citados:** no se valida que `[S1]` en `body_md` corresponda a una fuente real del evidence pack.
5. **Falsos positivos en `_extract_hard_tokens`:** números grandes o códigos SKU-like no comerciales pueden forzar confirmación innecesaria (trade-off aceptable para SL1b).
6. **Backup:** faltan checksum de integridad del archive, decisión CEO sobre AES-256, rechazo si `archive_schema` es `None`, y validación de passphrase vacía.
7. **Auto-update producción:** no hay clave pública pinned hardcodeada; el operador debe configurarla antes de habilitar updates reales (deuda documentada para SL4).
8. **Windows updater:** reemplazar el binario en ejecución seguirá siendo un problema real en producción (no resuelto, aceptado para SL1b).

---

## Recomendación

Se recomienda declarar **SL1b técnicamente aprobado** y proceder a abrir SL2a una vez que se cumplan las condiciones no técnicas.

---

## Bloqueantes que aún retienen SL2a

| Bloqueante | Quién debe actuar |
|---|---|
| Pack de datos MWT reales autorizado y validado por Alvaro | **Alvaro (CEO)** |
| Decisiones CEO: scope/freeze, licencia FSL, dedicación dev, ¿SL5 incluido o diferido?, calendario, criterio de adopción N, cifrado local obligatorio/condicional | **Alvaro (CEO)** |
| Documentación de seguridad/ops: `AUTO_UPDATE_SPEC.md`, `INJECTION_CANARY_MATRIX.md`, `BACKUP_RESTORE_RUNBOOK.md`, `source_to_field_schema.md` | **orquestador / fugu** |
| Certificados de firma de código Apple/Microsoft (bloquea SL4, no SL2a) | **CEO / ops** |
| Credenciales IMAP de Kimi Work (bloquea SL5 si entra en scope) | **Alvaro / ops** |

**Próximo paso:** con este PASS formal, el orquestador puede abrir SL2a en cuanto Alvaro entregue el pack MWT real y las decisiones estratégicas pendientes estén documentadas.
