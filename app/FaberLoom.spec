# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for FaberLoom desktop (SL4).

Build with:
    uv run pyinstaller FaberLoom.spec --clean --noconfirm

The resulting executable launches a local uvicorn server in a background thread
and opens the FaberLoom UI via pywebview. Static assets and the data directory
are bundled so the app runs without a terminal.
"""

from pathlib import Path


APP_DIR = Path(SPECPATH)
ENTRYPOINT = APP_DIR / "entrypoint.py"
STATIC_DIR = APP_DIR / "static"
ICON_PATH = STATIC_DIR / "faberloom.ico"

# The local data directory is intentionally NOT bundled.  At runtime the app
# stores its SQLite database under the user's OS-specific data directory
# (%LOCALAPPDATA%/FaberLoom on Windows, ~/.local/share/FaberLoom elsewhere).

a = Analysis(
    [str(ENTRYPOINT)],
    pathex=[str(APP_DIR)],
    binaries=[],
    datas=[
        (str(STATIC_DIR), "static"),
    ],
    hiddenimports=[
        "uvicorn",
        "fastapi",
        "pydantic",
        "pywebview",
        "jinja2",
        "openpyxl",
        "pdfplumber",
        "filetype",
        "chardet",
        "cryptography",
        "imaplib",
        "smtplib",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirect=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="FaberLoom",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ICON_PATH),
)
