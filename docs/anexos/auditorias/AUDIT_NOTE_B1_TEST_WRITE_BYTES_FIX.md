# AUDIT_NOTE_B1_TEST_WRITE_BYTES_FIX

**Fecha:** 2026-05-07
**Causa:** Path.write_text() en Windows convierte LF a CRLF automaticamente.
Test setup en hooks/tests/test_b1_enforcement.py calculaba hash sobre body
con LF (memoria) pero escribia config a disk con CRLF (write_text en Windows).
Mismatch entre hash esperado y hash actual leido binario por _sha256_file.

**Resultado pre-fix:** 10/18 tests OK (los que esperaban mismatch),
8/18 FAIL (los happy-path que esperaban hooks funcionando normalmente).

**Fix:** _write_valid_config() ahora usa write_bytes con encoding utf-8
explicito. Bytes puros sin conversion line endings.

**Verificacion post-fix:** 18/18 tests OK (Ran 18 tests in 0.381s).

**Notas:**
- Bug confirmado por Round 3 hallazgo #6 (sistema no distinguia cambio
  semantico de cambio de representacion).
- Enforcement REAL en produccion NO afectado: hooks/config.json en repo
  tiene LF correcto (gitattributes), hooks calculan hash correcto.
- Break-glass procedure SPEC_HOOKS_FAIL_CLOSED v1 seccion 6 aplicado:
  edicion manual fuera de Cowork via PowerShell directo.
