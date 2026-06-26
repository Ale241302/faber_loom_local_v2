"""SpaceLoom desktop build helper (SL4).

Usage:
    uv run python build.py
    uv run python build.py --sign
    uv run python build.py --sign --installer

Environment variables:
    SPACELOOM_CODESIGN_CERT      Path to a PEM code-signing certificate.
    SPACELOOM_CODESIGN_PASSWORD  Optional password for the certificate key.
    SPACELOOM_SIGNING_KEY_B64    Base64 Ed25519 private key for update manifest.

Outputs:
    dist/SpaceLoom.exe (Windows) or dist/SpaceLoom (POSIX)
    dist/SpaceLoom.exe.sig       Detached CMS signature when no real cert is used.
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
EXECUTABLE = DIST_DIR / ("SpaceLoom.exe" if sys.platform == "win32" else "SpaceLoom")
MANIFEST_PATH = DIST_DIR / "update_manifest.json"


def run_pyinstaller() -> None:
    spec = APP_DIR / "SpaceLoom.spec"
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

    If ``SPACELOOM_CODESIGN_CERT`` and ``SPACELOOM_CODESIGN_PASSWORD`` are set,
    use the real certificate.  Otherwise generate a self-signed test certificate
    and write a detached ``.sig`` file next to the executable.
    """

    if not EXECUTABLE.exists():
        raise RuntimeError(f"Executable not found: {EXECUTABLE}")

    cert_path = os.getenv("SPACELOOM_CODESIGN_CERT")
    password = os.getenv("SPACELOOM_CODESIGN_PASSWORD")

    if cert_path and Path(cert_path).exists():
        key_path = os.getenv("SPACELOOM_CODESIGN_KEY") or cert_path
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

    key_b64 = os.getenv("SPACELOOM_SIGNING_KEY_B64") or os.getenv("SIGNING_KEY_B64")
    if not key_b64:
        print("[build] No signing key provided; skipping manifest generation.")
        print("[build] Set SPACELOOM_SIGNING_KEY_B64 to create update_manifest.json.")
        return

    private_key_bytes = base64.b64decode(key_b64)
    payload = EXECUTABLE.read_bytes()
    manifest = create_update_manifest(payload, version=_read_version(), private_key_bytes=private_key_bytes)

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[build] Signed manifest written to {MANIFEST_PATH}")


def build_installer() -> None:
    """Generate an NSIS installer script (and compile it if makensis is available)."""

    if not EXECUTABLE.exists():
        raise RuntimeError(f"Executable not found: {EXECUTABLE}")

    installer = build_installer_windows(EXECUTABLE, DIST_DIR, app_name="SpaceLoom", version=_read_version())
    if installer:
        print(f"[build] Installer built: {installer}")
    else:
        print(f"[build] NSIS script generated in {DIST_DIR}; makensis not found, skipping compilation.")


def _read_version() -> str:
    version_file = APP_DIR / "VERSION"
    if version_file.exists():
        return version_file.read_text(encoding="utf-8").strip()
    return "0.1.0"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build SpaceLoom desktop executable.")
    parser.add_argument("--sign", action="store_true", help="Sign executable and generate signed update manifest.")
    parser.add_argument("--installer", action="store_true", help="Generate NSIS installer script/executable.")
    args = parser.parse_args()

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)

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
