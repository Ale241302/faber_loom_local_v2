# Plan SL4 CLOSER — v1 (CERRADO)

**Fecha:** 2026-06-27  
**Loop:** §5 AUDIT → PLAN → IMPLEMENT → TEST → GATE → REPORTE  
**Reglas:** No inventar. FROZEN (`ENT_OPS_STATE_MACHINE`, `PLB_ORCHESTRATOR`) intactos.

## DoD objetivo

1. SpaceLoom.exe vía PyInstaller + pywebview reproducible.
2. Instalador sin terminal (doble-clic): un no-técnico instala y abre la app sin ayuda.
3. Auto-update firmado y verificado + rollback (§7.5): mecanismo corre contra llave self-signed local; sin firma válida no instala; rollback probado.
4. Firma de código: fallback self-signed con aviso documentado en el instalador (PRC-05); punto de extensión limpio para cert real.
5. Backup/export/restore (ya cerrado en SL3.5) — referenciar, no reimplementar.
6. Smoke tests de empaque: build genera app que abre, persiste estado local, update verificado contra llave disponible, rollback funciona.
7. Gate §6 completo.
8. Reporte §8 con resultado del instalador, auto-update + rollback self-signed, y PROCURE abiertos.

## Cambios técnicos

### 1. Versión alineada

- `app/VERSION` → `0.2.0-sl4`.
- `app/pyproject.toml` → `version = "0.2.0"`.
- `app/src/main.py` → `FastAPI(version=_read_version())` leyendo de `app/VERSION`.

### 2. Instalador terminal-free (fallback Python)

- `app/src/installer.py`:
  - GUI tkinter con selección de carpeta, aviso self-signed, botón Instalar.
  - Modo `--silent --install-dir <dir>` para tests y CI.
  - Instala a `%LOCALAPPDATA%\Programs\SpaceLoom` (no requiere admin).
  - Crea accesos directos en Start Menu/Desktop vía PowerShell.
  - Copia el ejecutable embebido desde `sys._MEIPASS` cuando corre como bundle.
- `app/SpaceLoom_Installer.spec`:
  - Especificación PyInstaller para `SpaceLoom-Setup.exe`.
  - `console=False`, embebe `dist/SpaceLoom.exe`.
- `app/build.py`:
  - `--installer` primero intenta NSIS (`makensis`); si no está disponible, compila el instalador Python fallback.

### 3. Firma de código y auto-update

- `app/src/packaging.py`: firma self-signed con certificado RSA generado localmente + firma detached `.sig`; verificación sin herramientas externas.
- `app/src/update.py`: Ed25519 firmado/verificación, pinned public key, downgrade blocker, pending-mutation blocker, rollback de binario (`~/.spaceloom_rollback`).
- `app/build.py --sign`: firma el ejecutable y genera `update_manifest.json` firmado.

### 4. Backup/export/restore

- Referenciado desde SL3.5 (`app/src/backup.py`, `.spaceloom` archives).
- No se reimplementó; se documenta como capa de portabilidad de datos de usuario separada del rollback de binario.

## Resultados de test

```text
pytest app/tests/test_sl4_packaging.py -q
11 passed, 1 warning

pytest app/tests -q
197 passed, 1 warning
```

Baseline SL3.5: `194 passed`.  
Incremento neto: **+3 tests**.

## Gate §6 — Checklist

- [x] PyInstaller spec reproduce `SpaceLoom.exe` sin terminal.
- [x] Instalador `SpaceLoom-Setup.exe` se compila y funciona en modo silencioso.
- [x] Auto-update firma/verificación + rollback probados (tests SL1b + SL4).
- [x] Self-signed warning documentado en instalador.
- [x] Backup/export/restore referenciado (SL3.5).
- [x] Full suite verde.
- [x] PROCUREMENT_LEDGER.md actualizado con trazabilidad de PRC-05/06/07.
- [x] Reporte §8 generado.

## Archivos modificados

- `app/VERSION`
- `app/pyproject.toml`
- `app/src/main.py`
- `app/src/installer.py` (nuevo)
- `app/SpaceLoom_Installer.spec` (nuevo)
- `app/build.py`
- `app/tests/test_sl4_packaging.py`
- `PROCUREMENT_LEDGER.md`
- `harness/reports/PLAN_SL4_CLOSER_v1.md` — este plan.
- `harness/reports/SL4_CLOSER_REPORT_v1.md` — reporte de cierre §8.

## Restricciones respetadas

- `ENT_OPS_STATE_MACHINE` y `PLB_ORCHESTRATOR` no modificados.
- No se inventaron datos MWT reales.
- Mac queda diferido; el cierre D4 se hace sobre Windows.
