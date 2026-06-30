---
id: SPEC_SPACELOOM_SL4
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE — 2026-06-30 — cierre formal de SL4 (empaque desktop dogfood interno Windows)
aplica_a: [FaberLoom, MWT]
relacionado:
  - PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md
  - SPEC_SPACELOOM_ETAPA1_v1.md
  - IDX_SPACELOOM_ETAPA1_v1.md
---

# SPEC_SPACELOOM_SL4_v1 — Empaque desktop

## Objetivo

Empaquetar la app como ejecutable Windows instalable por doble-clic, sin terminal, con firma de código (self-signed para dogfood) y auto-update firmado con rollback.

## Definition of Done

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Build PyInstaller + pywebview | ✅ | `SpaceLoom.spec` produce `dist/SpaceLoom.exe` (~50 MB), subsistema GUI. |
| 2 | Instalador terminal-free | ✅ | `SpaceLoom-Setup.exe` (~60 MB) con `app/src/installer.py` (tkinter fallback NSIS). |
| 3 | Instalación silenciosa real | ✅ | `--silent --install-dir <tmp>` copia ejecutable y crea accesos directos. |
| 4 | Firma de código | ✅ | Self-signed fallback + soporte `SPACELOOM_CODESIGN_CERT`; `verify_executable_signature()`. |
| 5 | Auto-update firmado | ✅ | Ed25519 con pinned public key; rechaza downgrade y llave incorrecta; rollback a 5 versiones. |
| 6 | Backup/export/restore | ✅ | `.speloom` zip cifrado opcional; soporta workspaces SQLCipher. |
| 7 | Tests | ✅ | 11 passed (SL4); suite total 197 passed. |

## Resultados de test

```text
pytest app/tests/test_sl4_packaging.py -q
11 passed, 1 warning

pytest app/tests -q
197 passed, 1 warning
```

## Archivos clave

- `app/VERSION` (`0.2.0-sl4`)
- `app/pyproject.toml`
- `app/SpaceLoom.spec`
- `app/SpaceLoom_Installer.spec`
- `app/build.py`
- `app/src/installer.py`
- `app/src/packaging.py`
- `app/src/update.py`
- `app/src/backup.py`
- `app/tests/test_sl4_packaging.py`
- `PROCUREMENT_LEDGER.md`

## PROCURE abiertos

| ID | Ítem | Estado |
|---|---|---|
| PRC-05 | Certificado Authenticode Windows | ABIERTO (fallback self-signed verificado) |
| PRC-06 | Apple Developer + notarización Mac | ABIERTO (Mac diferido en Etapa 1) |
| PRC-07 | Llave de firma auto-update publicable | ABIERTO (mecanismo verificado) |

## Notas

- Cierre válido para dogfood interno Windows.
- Mac se difiere.
- `ENT_OPS_STATE_MACHINE` y `PLB_ORCHESTRATOR` no fueron modificados.

## Changelog

- v1.0 (2026-06-30): Cierre formal de SL4 a partir de `harness/reports/SL4_CLOSER_REPORT_v1.md`.
