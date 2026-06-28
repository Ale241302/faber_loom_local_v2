# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the FaberLoom terminal-free installer (SL4).

Build with:
    uv run pyinstaller FaberLoom_Installer.spec --clean --noconfirm

This bundles the previously built ``dist/FaberLoom.exe`` so the installer can be
double-clicked without any external toolchain.  For production distribution the
same extension points apply: replace the self-signed certificate in
``build.py --sign`` and optionally switch ``build_installer()`` to NSIS/Inno
Setup without changing this spec.
"""

from pathlib import Path


APP_DIR = Path(SPECPATH)
ENTRYPOINT = APP_DIR / "src" / "installer.py"
ICON_PATH = APP_DIR / "static" / "faberloom.ico"
BUNDLED_EXE = APP_DIR / "dist" / "FaberLoom.exe"

# Fall back gracefully if the app has not been built yet; PyInstaller will fail
# with a clear missing-data error instead of a cryptic Analysis failure.
extra_datas = []
if BUNDLED_EXE.exists():
    extra_datas.append((str(BUNDLED_EXE), "."))
else:
    extra_datas.append((str(APP_DIR / "VERSION"), "."))

a = Analysis(
    [str(ENTRYPOINT)],
    pathex=[str(APP_DIR)],
    binaries=[],
    datas=extra_datas,
    hiddenimports=[],
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
    name="FaberLoom-Setup",
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
