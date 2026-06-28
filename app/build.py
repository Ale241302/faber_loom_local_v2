"""FaberLoom desktop build helper (SL4).

Usage:
    uv run python build.py
    uv run python build.py --sign
    uv run python build.py --sign --installer

Environment variables:
    FABERLOOM_CODESIGN_CERT      Path to a PEM code-signing certificate.
    FABERLOOM_CODESIGN_PASSWORD  Optional password for the certificate key.
    FABERLOOM_SIGNING_KEY_B64    Base64 Ed25519 private key for update manifest.

Outputs:
    dist/FaberLoom.exe (Windows) or dist/FaberLoom (POSIX)
    dist/FaberLoom.exe.sig       Detached CMS signature when no real cert is used.
    dist/update_manifest.json    Signed update manifest (only when --sign is used).
    dist/*.nsi                   NSIS installer script (only when --installer is used).
    dist/*-Setup.exe             Compiled installer if makensis is available.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from src.packaging import (
    build_installer_windows,
    generate_self_signed_code_signing_cert,
    sign_executable_windows,
)
from src.update import create_update_manifest


APP_DIR = Path(__file__).resolve().parent
DIST_DIR = APP_DIR / "dist"
EXECUTABLE = DIST_DIR / ("FaberLoom.exe" if sys.platform == "win32" else "FaberLoom")
MANIFEST_PATH = DIST_DIR / "update_manifest.json"
INSTALLER_SPEC = APP_DIR / "FaberLoom_Installer.spec"
INSTALLER_EXE = DIST_DIR / "FaberLoom-Setup.exe"


def _bundle_faberloom_catalog() -> None:
    """Copy the FaberLoom Markdown catalog into the static bundle.

    This guarantees the desktop executable can import from ``faberloom/`` even
    though that directory is not tracked in the PyInstaller analysis by itself.
    """

    source_dir = APP_DIR.parent / "faberloom"
    dest_dir = APP_DIR / "static" / "faberloom"

    if not source_dir.exists():
        print(f"[build] FaberLoom source directory not found: {source_dir}")
        return

    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    for path in source_dir.glob("*.md"):
        shutil.copy2(path, dest_dir / path.name)
        copied += 1
    print(f"[build] Bundled {copied} FaberLoom Markdown files to {dest_dir}")


def run_pyinstaller() -> None:
    spec = APP_DIR / "FaberLoom.spec"
    if not spec.exists():
        raise RuntimeError(f"PyInstaller spec not found: {spec}")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        str(spec),
        "--clean",
        "--noconfirm",
    ]
    print(f"[build] Running: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=APP_DIR, check=True)


def sign_executable() -> None:
    """Sign the produced executable.

    If ``FABERLOOM_CODESIGN_CERT`` and ``FABERLOOM_CODESIGN_PASSWORD`` are set,
    use the real certificate.  Otherwise generate a self-signed test certificate
    and write a detached ``.sig`` file next to the executable.
    """

    if not EXECUTABLE.exists():
        raise RuntimeError(f"Executable not found: {EXECUTABLE}")

    cert_path = os.getenv("FABERLOOM_CODESIGN_CERT")
    password = os.getenv("FABERLOOM_CODESIGN_PASSWORD")

    if cert_path and Path(cert_path).exists():
        key_path = os.getenv("FABERLOOM_CODESIGN_KEY") or cert_path
        print(f"[build] Signing executable with real certificate: {cert_path}")
        sign_executable_windows(EXECUTABLE, cert_path, key_path, password=password)
    else:
        print("[build] No real code-signing certificate provided; using self-signed test cert.")
        with tempfile.TemporaryDirectory() as tmpdir:
            cert_path, key_path = generate_self_signed_code_signing_cert(tmpdir)
            sign_executable_windows(EXECUTABLE, cert_path, key_path)
        print(f"[build] Detached signature written to {EXECUTABLE}.sig")


def sign_payload() -> None:
    """Generate the signed Ed25519 update manifest for the executable."""

    if not EXECUTABLE.exists():
        raise RuntimeError(f"Executable not found: {EXECUTABLE}")

    key_b64 = os.getenv("FABERLOOM_SIGNING_KEY_B64") or os.getenv("SIGNING_KEY_B64")
    if not key_b64:
        print("[build] No signing key provided; skipping manifest generation.")
        print("[build] Set FABERLOOM_SIGNING_KEY_B64 to create update_manifest.json.")
        return

    private_key_bytes = base64.b64decode(key_b64)
    payload = EXECUTABLE.read_bytes()
    manifest = create_update_manifest(payload, version=_read_version(), private_key_bytes=private_key_bytes)

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[build] Signed manifest written to {MANIFEST_PATH}")


def build_installer() -> None:
    """Generate an installer executable.

    If ``makensis`` is available, build an NSIS installer.  Otherwise fall back
    to a terminal-free Python installer packaged with PyInstaller.  The Python
    installer embeds ``FaberLoom.exe`` and installs it to the user's local
    programs directory with Start Menu / Desktop shortcuts.
    """

    if not EXECUTABLE.exists():
        raise RuntimeError(f"Executable not found: {EXECUTABLE}")

    installer = build_installer_windows(EXECUTABLE, DIST_DIR, app_name="FaberLoom", version=_read_version())
    if installer:
        print(f"[build] NSIS installer built: {installer}")
        return

    print("[build] makensis not found; falling back to Python GUI installer.")
    build_python_installer()


def build_python_installer() -> None:
    """Package the terminal-free Python installer with PyInstaller."""

    if not INSTALLER_SPEC.exists():
        raise RuntimeError(f"Installer spec not found: {INSTALLER_SPEC}")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        str(INSTALLER_SPEC),
        "--clean",
        "--noconfirm",
    ]
    print(f"[build] Running: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=APP_DIR, check=True)
    if INSTALLER_EXE.exists():
        print(f"[build] Python installer built: {INSTALLER_EXE}")
    else:
        print(f"[build] Warning: expected installer not found at {INSTALLER_EXE}")


def _read_version() -> str:
    version_file = APP_DIR / "VERSION"
    if version_file.exists():
        return version_file.read_text(encoding="utf-8").strip()
    return "0.1.0"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build FaberLoom desktop executable.")
    parser.add_argument("--sign", action="store_true", help="Sign executable and generate signed update manifest.")
    parser.add_argument("--installer", action="store_true", help="Generate NSIS installer script/executable.")
    args = parser.parse_args()

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)

    _bundle_faberloom_catalog()
    run_pyinstaller()
    print(f"[build] Executable available at {EXECUTABLE}")

    if args.sign:
        sign_executable()
        sign_payload()

    if args.installer:
        build_installer()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
