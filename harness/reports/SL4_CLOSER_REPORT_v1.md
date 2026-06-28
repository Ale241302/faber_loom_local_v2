# Reporte de cierre SL4 — v1 (§8)

**Fecha:** 2026-06-27  
**Agente:** Kimi Code CLI  
**Loop CLOSER:** §5 AUDIT → PLAN → IMPLEMENT → TEST → GATE → REPORTE

## Estado

SL4 **CERRADO** para dogfood interno (D4) sobre Windows.

## 1. Empaque PyInstaller + pywebview

- **Spec:** `app/SpaceLoom.spec` produce `dist/SpaceLoom.exe` con `console=False`.
- **Subsistema PE verificado:** `IMAGE_SUBSYSTEM_WINDOWS_GUI` (2) tanto para `SpaceLoom.exe` como para `SpaceLoom-Setup.exe`.
- **Build reproducible:**
  ```bash
  cd app
  uv run python build.py --sign --installer
  ```
- **Tamaños aproximados:**
  - `SpaceLoom.exe` ~50 MB.
  - `SpaceLoom-Setup.exe` ~60 MB (embebe el ejecutable).

## 2. Instalador sin terminal

### Fallback Python

Como `makensis` no está disponible en el entorno de build, se implementó un instalador Python con tkinter que se compila como ejecutable GUI:

- **Código:** `app/src/installer.py`.
- **Spec:** `app/SpaceLoom_Installer.spec`.
- **Comportamiento:**
  - Doble-clic abre ventana con aviso self-signed, selección de carpeta y botón Instalar.
  - Instala a `%LOCALAPPDATA%\Programs\SpaceLoom` (no requiere admin).
  - Crea acceso directo en Start Menu (y escritorio si es posible) usando PowerShell.
  - Genera `uninstall.bat` para desinstalación manual.

### Prueba real de instalación silenciosa

```text
SpaceLoom-Setup.exe --silent --install-dir <tmp>\SpaceLoom
installed=<tmp>\SpaceLoom\SpaceLoom.exe
start_menu=C:\Users\...\Start Menu\Programs\SpaceLoom.lnk
desktop=None
```

El ejecutable copiado arranca (validado lanzando `SpaceLoom.exe`; la app abre su ventana pywebview).

### Aviso self-signed

`app/src/installer.py::SELF_SIGNED_WARNING` documenta en la UI:

> "This is an internal dogfood build signed with a self-signed certificate. Windows may show a SmartScreen warning. For external distribution the build must be signed with a real Authenticode certificate (PRC-05)."

## 3. Firma de código

- **Certificado real:** `build.py --sign` soporta `SPACELOOM_CODESIGN_CERT` + `SPACELOOM_CODESIGN_PASSWORD` vía `signtool`.
- **Fallback self-signed:** cuando no hay certificado real, `app/src/packaging.py` genera un certificado RSA local y escribe una firma detached `<exe>.sig`.
- **Verificación:** `verify_executable_signature()` valida la firma raw RSA sin herramientas externas.
- **Test:** `test_smoke_signed_executable`.
- **Punto de extensión limpio:** reemplazar solo las variables de entorno de `build.py`; ni `installer.py` ni `SpaceLoom.spec` cambian.

## 4. Auto-update firmado, verificado y rollback

- **Firma:** Ed25519 (`app/src/update.py`).
- **Verificación:** pinned public key; sin llave confiable `verify_update_manifest` falla cerrado.
- **Downgrade:** rechazado por `_is_newer_version`.
- **Bloqueo por mutaciones pendientes:** `pending_check` opcional en `install_update`.
- **Rollback:** `install_update` copia el binario anterior a `.spaceloom_rollback`; `rollback()` restaura la versión previa. Mantiene las últimas 5 versiones.
- **Tests:**
  - `test_auto_update_sign_verify_and_rollback` (SL1b).
  - `test_update_rejects_wrong_public_key`.
  - `test_update_rejects_downgrade`.
  - `test_update_blocks_pending_mutations`.
  - `test_signed_update_manifest_roundtrip` (SL4).
  - `test_check_for_update_smoke` (SL4).

## 5. Backup/export/restore (SL3.5)

- Referenciado, no reimplementado.
- Contrato: archivos `.spaceloom` (zip con `meta.json` + `db.sqlite3`), cifrado opcional con Fernet/PBKDF2.
- Soporta workspaces SQLCipher confidenciales (`db_key`).
- Archivo clave: `app/src/backup.py`.
- Tests: `test_backup_restore_smoke`, `test_backup_restore_confidential_workspace_smoke`.

## 6. Multi-tenant y restricciones

- `ENT_OPS_STATE_MACHINE` y `PLB_ORCHESTRATOR` no fueron modificados.
- No se inventaron datos MWT reales.
- Mac se difería; el cierre D4 cubre solo Windows.

## 7. PROCURE abiertos y trazados

Actualizados en `PROCUREMENT_LEDGER.md`:

- **PRC-05** — Certificado Authenticode Windows. Estado: ABIERTO (trazado; fallback self-signed verificado).
- **PRC-06** — Apple Developer + notarización Mac. Estado: ABIERTO (trazado; Mac diferido en Etapa 1).
- **PRC-07** — Llave de firma auto-update publicable. Estado: ABIERTO (trazado; mecanismo Ed25519 + pinned-key + rollback verificado).

Ninguno bloquea el cierre dogfood interno.

## Resultados de test

```text
pytest app/tests/test_sl4_packaging.py -q
11 passed, 1 warning

pytest app/tests -q
197 passed, 1 warning
```

Baseline SL3.5: `194 passed`.  
Incremento neto: **+3 tests**.

## Archivos clave

- `app/VERSION` — versión alineada `0.2.0-sl4`.
- `app/pyproject.toml` — versión del proyecto `0.2.0`.
- `app/src/main.py` — lee versión desde `VERSION`.
- `app/src/installer.py` — instalador terminal-free (GUI + modo silencioso).
- `app/SpaceLoom_Installer.spec` — spec PyInstaller del instalador.
- `app/build.py` — orquestación de build, sign e installer (NSIS → Python fallback).
- `app/src/packaging.py` — firma self-signed del ejecutable.
- `app/src/update.py` — auto-update Ed25519 + rollback.
- `app/src/backup.py` — backup/export/restore de datos (SL3.5).
- `app/tests/test_sl4_packaging.py` — tests de empaque.
- `PROCUREMENT_LEDGER.md` — PRC-05/06/07 abiertos y trazados.
- `harness/reports/PLAN_SL4_CLOSER_v1.md`
- `harness/reports/SL4_CLOSER_REPORT_v1.md` — este reporte.
