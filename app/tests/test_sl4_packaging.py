"""SL4: desktop packaging contracts (PyInstaller spec + signed update manifest)."""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[2]
APP_DIR = ROOT / "app"
SPEC = APP_DIR / "SpaceLoom.spec"
BUILD_SCRIPT = APP_DIR / "build.py"
VERSION_FILE = APP_DIR / "VERSION"


def test_pyinstaller_spec_exists() -> None:
    assert SPEC.exists(), f"PyInstaller spec missing: {SPEC}"
    text = SPEC.read_text(encoding="utf-8")
    assert "SpaceLoom" in text
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

    dummy_exe = tmp_path / "SpaceLoom.exe"
    dummy_exe.write_bytes(b"MZdummy")
    script_path = tmp_path / "installer.nsi"

    generated = generate_nsis_script(dummy_exe, script_path, app_name="SpaceLoom", version="0.2.0")

    assert generated == script_path
    text = script_path.read_text(encoding="utf-8")
    assert "SpaceLoom" in text
    assert "SpaceLoom.exe" in text
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
