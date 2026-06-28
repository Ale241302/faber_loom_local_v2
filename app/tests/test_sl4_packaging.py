"""SL4: desktop packaging contracts (PyInstaller spec + signed update manifest)."""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[2]
APP_DIR = ROOT / "app"
SPEC = APP_DIR / "FaberLoom.spec"
BUILD_SCRIPT = APP_DIR / "build.py"
VERSION_FILE = APP_DIR / "VERSION"


def test_pyinstaller_spec_exists() -> None:
    assert SPEC.exists(), f"PyInstaller spec missing: {SPEC}"
    text = SPEC.read_text(encoding="utf-8")
    assert "FaberLoom" in text
    assert "static" in text
    assert "console=False" in text


def test_build_script_exists() -> None:
    assert BUILD_SCRIPT.exists()
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    assert "PyInstaller" in text
    assert "create_update_manifest" in text
    assert "--sign" in text
    assert "--installer" in text


def test_version_file_exists() -> None:
    assert VERSION_FILE.exists()
    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    assert version


def test_signed_update_manifest_roundtrip() -> None:
    from app.src.update import (
        add_trusted_public_key,
        create_update_manifest,
        generate_keypair,
        verify_update_manifest,
    )

    private_key, public_key = generate_keypair()
    public_key_b64 = base64.b64encode(public_key).decode("ascii")
    add_trusted_public_key(public_key_b64)

    payload = b"fake executable payload"
    manifest = create_update_manifest(payload, version="0.2.0", private_key_bytes=private_key)

    assert verify_update_manifest(payload, manifest)
    assert not verify_update_manifest(b"tampered", manifest)


def test_smoke_signed_executable() -> None:
    from app.src.packaging import smoke_test_signed_executable

    result = smoke_test_signed_executable()
    assert result["signed"] is True
    assert result["verified"] is True


def test_nsis_script_generation(tmp_path: Path) -> None:
    from app.src.packaging import generate_nsis_script

    dummy_exe = tmp_path / "FaberLoom.exe"
    dummy_exe.write_bytes(b"MZdummy")
    script_path = tmp_path / "installer.nsi"

    generated = generate_nsis_script(dummy_exe, script_path, app_name="FaberLoom", version="0.2.0")

    assert generated == script_path
    text = script_path.read_text(encoding="utf-8")
    assert "FaberLoom" in text
    assert "FaberLoom.exe" in text
    assert "InstallDir" in text


def test_check_for_update_smoke(tmp_path: Path) -> None:
    from app.src.update import (
        check_for_update,
        create_update_manifest,
        download_update,
        generate_keypair,
    )

    private_key, public_key = generate_keypair()
    public_key_b64 = base64.b64encode(public_key).decode("ascii")

    payload = b"updated executable payload"
    manifest = create_update_manifest(payload, version="0.2.0", private_key_bytes=private_key)
    manifest["payload_url"] = (tmp_path / "payload.bin").as_uri()

    payload_path = tmp_path / "payload.bin"
    payload_path.write_bytes(payload)

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    manifest_url = manifest_path.as_uri()

    # Newer version + trusted key -> manifest returned.
    found = check_for_update(manifest_url, current_version="0.1.0", trusted_keys={public_key_b64})
    assert found is not None
    assert found["version"] == "0.2.0"

    # Same version -> no update.
    same = check_for_update(manifest_url, current_version="0.2.0", trusted_keys={public_key_b64})
    assert same is None

    # Untrusted key -> no update.
    _, other_public = generate_keypair()
    other_b64 = base64.b64encode(other_public).decode("ascii")
    untrusted = check_for_update(manifest_url, current_version="0.1.0", trusted_keys={other_b64})
    assert untrusted is None

    # Download payload via manifest and verify hash/signature.
    download_dir = tmp_path / "downloads"
    downloaded = download_update(found, download_dir)
    assert downloaded.exists()
    assert downloaded.read_bytes() == payload


def test_download_update_missing_payload_url(tmp_path: Path) -> None:
    from app.src.update import download_update

    manifest = {"version": "0.2.0"}
    with pytest.raises(ValueError, match="payload_url"):
        download_update(manifest, tmp_path)


INSTALLER_SPEC = APP_DIR / "FaberLoom_Installer.spec"


def test_installer_spec_exists() -> None:
    assert INSTALLER_SPEC.exists(), f"Installer spec missing: {INSTALLER_SPEC}"
    text = INSTALLER_SPEC.read_text(encoding="utf-8")
    assert "FaberLoom-Setup" in text
    assert "console=False" in text
    assert "FaberLoom.exe" in text


def test_installer_silent_install(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The Python installer can copy the executable without a GUI."""

    from app.src import installer

    source_exe = tmp_path / "FaberLoom.exe"
    source_exe.write_bytes(b"MZFaberLoom")

    install_dir = tmp_path / "installed"

    # Avoid creating real shortcuts during unit tests.
    monkeypatch.setattr(installer, "create_shortcut", lambda lnk, target, description="": True)

    result = installer.install_app(source_exe, install_dir)

    assert Path(result["installed_exe"]).exists()
    assert Path(result["installed_exe"]).read_bytes() == source_exe.read_bytes()
    assert Path(result["install_dir"]) == install_dir


def test_installer_self_signed_warning_documented() -> None:
    """The installer exposes the self-signed fallback warning text."""

    from app.src.installer import SELF_SIGNED_WARNING

    assert "self-signed" in SELF_SIGNED_WARNING.lower()
    assert "PRC-05" in SELF_SIGNED_WARNING


def test_build_script_targets_faberloom_names() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    assert "FaberLoom.exe" in text
    assert "FaberLoom-Setup.exe" in text
    assert "SpaceLoom" not in text
