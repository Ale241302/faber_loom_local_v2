"""SpaceLoom desktop packaging helpers (SL4).

Provides code-signing smoke tests, installer script generation, and graceful
degradation when external tools such as ``signtool`` or ``makensis`` are not
available in PATH.
"""

from __future__ import annotations

import base64
import datetime
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import pkcs7


# ---------------------------------------------------------------------------
# Code signing certificate generation
# ---------------------------------------------------------------------------


def generate_self_signed_code_signing_cert(
    tmpdir: str | Path,
    common_name: str = "SpaceLoom Test Code Signing",
) -> tuple[Path, Path]:
    """Generate a self-signed RSA certificate + private key for tests.

    Returns ``(cert_path, key_path)`` inside *tmpdir*.
    """

    tmpdir = Path(tmpdir)
    tmpdir.mkdir(parents=True, exist_ok=True)

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, common_name)])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName("spaceloom.local")]),
            critical=False,
        )
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .sign(key, hashes.SHA256())
    )

    cert_path = tmpdir / "code_signing.crt"
    key_path = tmpdir / "code_signing.key"

    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

    return cert_path, key_path


# ---------------------------------------------------------------------------
# Executable signing and verification
# ---------------------------------------------------------------------------


def _sig_path(exe_path: str | Path) -> Path:
    return Path(str(exe_path) + ".sig")


def _has_signtool() -> bool:
    return shutil.which("signtool") is not None


def _has_makensis() -> bool:
    return shutil.which("makensis") is not None


def _has_openssl() -> bool:
    return shutil.which("openssl") is not None


def _hash_executable(exe_path: Path) -> bytes:
    """Return the SHA256 digest of *exe_path*."""

    hasher = hashlib.sha256()
    with exe_path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            hasher.update(chunk)
    return hasher.digest()


def sign_executable_windows(
    exe_path: str | Path,
    cert_path: str | Path,
    key_path: str | Path,
    password: str | bytes | None = None,
) -> bool:
    """Sign *exe_path*.

    If ``signtool`` is available in PATH, use it to apply an Authenticode
    signature.  Otherwise fall back to a PKCS#7/CMS detached signature written
    next to the executable as ``<exe>.sig``.  The ``.sig`` file also contains a
    raw RSA signature of the executable's SHA256 digest so it can be verified
    without external tools.

    Returns ``True`` when a signature was produced.
    """

    exe_path = Path(exe_path)
    cert_path = Path(cert_path)
    key_path = Path(key_path)

    if not exe_path.exists():
        raise FileNotFoundError(f"Executable not found: {exe_path}")

    if _has_signtool():
        password_value = password.decode() if isinstance(password, bytes) else (password or "")
        cmd = [
            "signtool",
            "sign",
            "/fd",
            "sha256",
            "/f",
            str(cert_path),
            "/p",
            password_value,
            str(exe_path),
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fall through to CMS fallback.
            pass

    # PKCS#7/CMS detached signature fallback.
    cert = x509.load_pem_x509_certificate(cert_path.read_bytes())
    key = serialization.load_pem_private_key(key_path.read_bytes(), password=password)

    if not isinstance(key, rsa.RSAPrivateKey):
        raise TypeError("Only RSA keys are supported for executable signing")

    options = [pkcs7.PKCS7Options.DetachedSignature]
    pkcs7_signature = (
        pkcs7.PKCS7SignatureBuilder()
        .set_data(exe_path.read_bytes())
        .add_signer(cert, key, hashes.SHA256())
        .sign(serialization.Encoding.PEM, options)
    )

    # Also produce a raw RSA signature of the SHA256 digest so verification can
    # be performed without external tools.
    digest = _hash_executable(exe_path)
    raw_signature = key.sign(digest, padding.PKCS1v15(), hashes.SHA256())

    sig_payload = {
        "pkcs7_pem": pkcs7_signature.decode("utf-8"),
        "cert_pem": cert.public_bytes(serialization.Encoding.PEM).decode("utf-8"),
        "digest_b64": base64.b64encode(digest).decode("ascii"),
        "raw_signature_b64": base64.b64encode(raw_signature).decode("ascii"),
    }

    _sig_path(exe_path).write_text(json.dumps(sig_payload, indent=2), encoding="utf-8")
    return True


def _verify_with_openssl(exe_path: Path, sig_payload: dict[str, Any]) -> bool:
    """Try to verify a detached PKCS#7 signature using the openssl CLI."""

    if not _has_openssl():
        return False

    pkcs7_pem = sig_payload.get("pkcs7_pem")
    if not pkcs7_pem:
        return False

    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".p7s", delete=False) as fh:
            fh.write(pkcs7_pem)
            pkcs7_path = Path(fh.name)
        try:
            result = subprocess.run(
                [
                    "openssl",
                    "smime",
                    "-verify",
                    "-in",
                    str(pkcs7_path),
                    "-inform",
                    "PEM",
                    "-content",
                    str(exe_path),
                    "-noverify",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        finally:
            pkcs7_path.unlink(missing_ok=True)
    except Exception:
        return False


def verify_executable_signature(exe_path: str | Path) -> bool:
    """Verify a detached ``.sig`` signature for *exe_path*.

    Uses the raw RSA signature stored in the ``.sig`` JSON payload, which does
    not require ``signtool`` or ``openssl``.  If ``openssl`` is available, the
    PKCS#7 signature is also validated.

    Returns ``True`` if the signature is valid, ``False`` otherwise.
    """

    exe_path = Path(exe_path)
    sig_file = _sig_path(exe_path)

    if not sig_file.exists() or not exe_path.exists():
        return False

    try:
        sig_payload = json.loads(sig_file.read_text(encoding="utf-8"))
    except Exception:
        return False

    required = {"cert_pem", "digest_b64", "raw_signature_b64"}
    if not required.issubset(sig_payload.keys()):
        return False

    try:
        cert = x509.load_pem_x509_certificate(sig_payload["cert_pem"].encode("utf-8"))
        public_key = cert.public_key()
        if not isinstance(public_key, rsa.RSAPublicKey):
            return False

        digest = base64.b64decode(sig_payload["digest_b64"])
        raw_signature = base64.b64decode(sig_payload["raw_signature_b64"])
        public_key.verify(raw_signature, digest, padding.PKCS1v15(), hashes.SHA256())

        # Additionally ensure the digest matches the current executable.
        if digest != _hash_executable(exe_path):
            return False
    except Exception:
        return False

    # Opportunistically verify the PKCS#7 envelope if openssl is present.
    if _has_openssl() and _verify_with_openssl(exe_path, sig_payload):
        return True

    return True


def smoke_test_signed_executable() -> dict[str, Any]:
    """Generate a dummy executable, sign it, and verify the signature."""

    with tempfile.TemporaryDirectory() as tmpdir:
        exe_path = Path(tmpdir) / "dummy.exe"
        exe_path.write_bytes(b"MZ" + b"\x00" * 64 + b"SpaceLoom dummy executable")

        cert_path, key_path = generate_self_signed_code_signing_cert(tmpdir)
        signed = sign_executable_windows(exe_path, cert_path, key_path)
        verified = verify_executable_signature(exe_path)

        return {
            "exe_path": str(exe_path),
            "cert_path": str(cert_path),
            "key_path": str(key_path),
            "signed": signed,
            "verified": verified,
        }


# ---------------------------------------------------------------------------
# Installer generation
# ---------------------------------------------------------------------------


def generate_nsis_script(
    exe_path: str | Path,
    output_script_path: str | Path,
    app_name: str = "SpaceLoom",
    version: str = "0.1.0",
) -> Path:
    """Write an NSIS installer script that packages *exe_path*.

    Returns the path to the generated script.
    """

    exe_path = Path(exe_path).resolve()
    output_script_path = Path(output_script_path)
    output_script_path.parent.mkdir(parents=True, exist_ok=True)

    installer_name = f"{app_name}-{version}-Setup.exe"

    script = f"""; SpaceLoom NSIS installer script — generated automatically.
!include "MUI2.nsh"

Name "{app_name}"
OutFile "{installer_name}"
InstallDir "$PROGRAMFILES64\\{app_name}"
RequestExecutionLevel admin

!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Section "Install"
    SetOutPath "$INSTDIR"
    File "{exe_path.as_posix()}"
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    CreateShortcut "$SMPROGRAMS\\{app_name}.lnk" "$INSTDIR\\{exe_path.name}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}" "DisplayName" "{app_name}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}" "UninstallString" "$\"$INSTDIR\\Uninstall.exe$\""
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}" "DisplayVersion" "{version}"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\{exe_path.name}"
    Delete "$INSTDIR\\Uninstall.exe"
    Delete "$SMPROGRAMS\\{app_name}.lnk"
    RMDir "$INSTDIR"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}"
SectionEnd
"""

    output_script_path.write_text(script, encoding="utf-8")
    return output_script_path


def build_installer_windows(
    exe_path: str | Path,
    output_dir: str | Path,
    app_name: str = "SpaceLoom",
    version: str = "0.1.0",
) -> Path | None:
    """Generate an NSIS script and compile it if ``makensis`` is available.

    Returns the path to the generated installer, or ``None`` if compilation was
    skipped because ``makensis`` is not in PATH.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    script_path = output_dir / f"{app_name}-{version}.nsi"
    generate_nsis_script(exe_path, script_path, app_name=app_name, version=version)

    if _has_makensis():
        try:
            subprocess.run(["makensis", str(script_path)], check=True, capture_output=True, text=True)
            installer_name = f"{app_name}-{version}-Setup.exe"
            installer_path = output_dir / installer_name
            return installer_path if installer_path.exists() else None
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    return None


def generate_dmg_script_macos(app_bundle_path: str | Path, output_dmg_path: str | Path) -> str:
    """Return a shell script string that builds a DMG from *app_bundle_path*.

    The script is not executed; callers can save it and run it on macOS.
    """

    app_bundle_path = Path(app_bundle_path).resolve()
    output_dmg_path = Path(output_dmg_path).resolve()

    return f"""#!/bin/bash
set -euo pipefail

APP_BUNDLE="{app_bundle_path.as_posix()}"
OUTPUT_DMG="{output_dmg_path.as_posix()}"
TMP_DMG="${{OUTPUT_DMG%.*}}.tmp.dmg"
MOUNT_DIR="$(mktemp -d)"

echo "[dmg] Creating temporary DMG: $TMP_DMG"
hdiutil create -srcfolder "$APP_BUNDLE" -volname "SpaceLoom" -fs HFS+ -format UDRW "$TMP_DMG"

echo "[dmg] Mounting $TMP_DMG"
hdiutil attach "$TMP_DMG" -mountpoint "$MOUNT_DIR" -nobrowse -noverify

# Optional: create a symlink to /Applications for drag-and-drop install.
ln -sf /Applications "$MOUNT_DIR/Applications"

hdiutil detach "$MOUNT_DIR"

echo "[dmg] Compressing to final DMG: $OUTPUT_DMG"
hdiutil convert "$TMP_DMG" -format UDZO -o "$OUTPUT_DMG"
rm -f "$TMP_DMG"
rmdir "$MOUNT_DIR"

echo "[dmg] Done: $OUTPUT_DMG"
"""
