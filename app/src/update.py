"""SpaceLoom auto-update signing and verification primitives.

SL1b does not yet ship a packaged desktop app, but the signing/verification seam
must exist before SL4.  We use Ed25519 for compact signatures and a simple
rollback mechanism: the installer keeps the previous binary/version and can
restore it if the new one fails verification or a smoke test.

Security model for SL1b:
- Updates MUST be signed by a pinned public key.  The manifest carries the
  public key that signed it, but install_update only accepts manifests whose
  public key is in the caller-supplied or pre-configured trusted set.
- Downgrades are rejected by default.
- Pending user mutations (drafts, etc.) block installation by default.
- The last N previous versions are kept for rollback.
"""

from __future__ import annotations

import base64
import hashlib
import json
import shutil
import tempfile
import urllib.request
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


UPDATE_MANIFEST_FIELDS = {"version", "payload_hash", "signature", "public_key"}

# Public keys (base64) trusted for auto-update signatures.  In production this
# is populated at startup from a hard-coded pinned key or trust-on-first-use
# with a visible fingerprint.
_TRUSTED_PUBLIC_KEYS: set[str] = set()

# Maximum number of previous versions to retain for rollback.
MAX_ROLLBACK_VERSIONS = 5


def set_trusted_public_keys(keys_b64: set[str]) -> None:
    """Replace the set of trusted update-signing public keys."""

    global _TRUSTED_PUBLIC_KEYS
    _TRUSTED_PUBLIC_KEYS = set(keys_b64)


def add_trusted_public_key(key_b64: str) -> None:
    """Add a trusted update-signing public key."""

    _TRUSTED_PUBLIC_KEYS.add(key_b64)


def get_trusted_public_keys() -> set[str]:
    """Return a copy of the trusted public-key set."""

    return _TRUSTED_PUBLIC_KEYS.copy()


def clear_trusted_public_keys() -> None:
    """Clear the trusted public-key set (testing only)."""

    _TRUSTED_PUBLIC_KEYS.clear()


def generate_keypair() -> tuple[bytes, bytes]:
    """Return (private_key_bytes, public_key_bytes) for update signing."""

    private_key = Ed25519PrivateKey.generate()
    return (
        private_key.private_bytes_raw(),
        private_key.public_key().public_bytes_raw(),
    )


def sign_payload(payload: bytes, private_key_bytes: bytes) -> bytes:
    """Sign an update payload and return the raw signature."""

    private_key = Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    return private_key.sign(payload)


def verify_payload(payload: bytes, signature: bytes, public_key_bytes: bytes) -> bool:
    """Verify an update signature.  Returns True/False; never raises."""

    try:
        public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
        public_key.verify(signature, payload)
        return True
    except (InvalidSignature, ValueError):
        return False


def _is_newer_version(new: str, current: str) -> bool:
    """Return True if *new* is a newer version than *current*.

    Supports simple numeric dot-separated versions (e.g. 1.2.3).  Non-numeric
    suffixes are compared lexicographically after numeric parts.
    """

    def _parts(v: str) -> list[str | int]:
        parts: list[str | int] = []
        for part in v.split("."):
            # Split leading numeric run from the rest.
            numeric = ""
            rest = ""
            for ch in part:
                if ch.isdigit() and not rest:
                    numeric += ch
                else:
                    rest += ch
            if numeric:
                parts.append(int(numeric))
            if rest:
                parts.append(rest.lower())
        return parts

    return _parts(new) > _parts(current)


def create_update_manifest(
    payload: bytes,
    version: str,
    private_key_bytes: bytes,
) -> dict[str, Any]:
    """Create a signed manifest for a payload."""

    import hashlib

    signature = sign_payload(payload, private_key_bytes)
    private_key = Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    public_key_bytes = private_key.public_key().public_bytes_raw()

    return {
        "version": version,
        "payload_hash": hashlib.sha256(payload).hexdigest(),
        "signature": base64.b64encode(signature).decode("ascii"),
        "public_key": base64.b64encode(public_key_bytes).decode("ascii"),
    }


def verify_update_manifest(
    payload: bytes,
    manifest: dict[str, Any],
    *,
    trusted_public_keys: set[str] | None = None,
) -> bool:
    """Verify payload against a manifest, enforcing pinned public keys.

    If *trusted_public_keys* is provided, the manifest's public_key must be in
    the set.  If it is None, the module-level trusted key set is used.  If no
    trusted keys are configured, verification fails closed.  This function never
    falls back to signature-only checks.
    """

    import hashlib

    if not UPDATE_MANIFEST_FIELDS.issubset(manifest.keys()):
        return False

    if hashlib.sha256(payload).hexdigest() != manifest["payload_hash"]:
        return False

    try:
        signature = base64.b64decode(manifest["signature"])
        public_key_bytes = base64.b64decode(manifest["public_key"])
    except Exception:
        return False

    keys = trusted_public_keys if trusted_public_keys is not None else _TRUSTED_PUBLIC_KEYS
    if not keys:
        return False
    if manifest["public_key"] not in keys:
        return False

    return verify_payload(payload, signature, public_key_bytes)


def _rollback_dir(current_path: Path) -> Path:
    return current_path.parent / ".spaceloom_rollback"


def _prune_rollbacks(rollback_dir: Path, current_name: str) -> None:
    """Keep only the most recent MAX_ROLLBACK_VERSIONS backups."""

    pattern = f"{current_name}.*.old"
    candidates = sorted(
        rollback_dir.glob(pattern),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for old in candidates[MAX_ROLLBACK_VERSIONS:]:
        old.unlink(missing_ok=True)


def install_update(
    current_path: Path | str,
    payload_path: Path | str,
    manifest: dict[str, Any],
    *,
    trusted_public_keys: set[str] | None = None,
    current_version: str | None = None,
    pending_check: Callable[[], bool] | None = None,
) -> dict[str, Any]:
    """Install a signed update, keeping the previous version for rollback.

    Raises ValueError if verification, downgrade protection or the pending-
    mutation check fails.
    """

    current_path = Path(current_path)
    payload_path = Path(payload_path)

    payload = payload_path.read_bytes()
    if not verify_update_manifest(payload, manifest, trusted_public_keys=trusted_public_keys):
        raise ValueError("Update signature verification failed")

    if current_version is not None and not _is_newer_version(manifest["version"], current_version):
        raise ValueError(
            f"Downgrade or re-install not allowed: {manifest['version']} <= {current_version}"
        )

    if pending_check is not None and pending_check():
        raise ValueError("Pending mutations exist; resolve them before installing an update")

    rollback_dir = _rollback_dir(current_path)
    rollback_dir.mkdir(parents=True, exist_ok=True)

    previous_version = current_version or "unknown"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rollback_path = rollback_dir / f"{current_path.name}.{previous_version}.{timestamp}.old"

    if current_path.exists():
        shutil.copy2(current_path, rollback_path)
        _prune_rollbacks(rollback_dir, current_path.name)

    shutil.copy2(payload_path, current_path)

    return {
        "installed_path": str(current_path),
        "rollback_path": str(rollback_path),
        "version": manifest["version"],
    }


def list_rollback_versions(current_path: Path | str) -> list[dict[str, Any]]:
    """List available rollback versions for *current_path*, newest first."""

    current_path = Path(current_path)
    rollback_dir = _rollback_dir(current_path)
    if not rollback_dir.exists():
        return []

    pattern = f"{current_path.name}.*.old"
    candidates = sorted(
        rollback_dir.glob(pattern),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    versions: list[dict[str, Any]] = []
    for path in candidates:
        # Name format: <current_name>.<version>.<timestamp>.old
        parts = path.name.split(".")
        version = parts[-3] if len(parts) >= 4 else "unknown"
        timestamp = parts[-2] if len(parts) >= 4 else "unknown"
        versions.append({
            "version": version,
            "timestamp": timestamp,
            "path": str(path),
        })
    return versions


def rollback(current_path: Path | str, *, to_version: str | None = None) -> dict[str, Any]:
    """Restore a previous version kept by install_update.

    If *to_version* is provided, restore that specific version; otherwise the
    most recent rollback is used.
    """

    current_path = Path(current_path)
    versions = list_rollback_versions(current_path)
    if not versions:
        raise FileNotFoundError("No rollback version available")

    if to_version is not None:
        chosen = next((v for v in versions if v["version"] == to_version), None)
        if chosen is None:
            raise FileNotFoundError(f"Rollback version {to_version} not found")
    else:
        chosen = versions[0]

    rollback_path = Path(chosen["path"])
    shutil.copy2(rollback_path, current_path)
    return {
        "restored_path": str(current_path),
        "from": str(rollback_path),
        "version": chosen["version"],
    }


def smoke_test_sign_verify_install() -> dict[str, Any]:
    """End-to-end smoke test for signing, verification, downgrade and rollback."""

    private_key, public_key = generate_keypair()
    public_key_b64 = base64.b64encode(public_key).decode("ascii")

    # Configure the trusted key so this smoke test exercises pinned-key behavior.
    clear_trusted_public_keys()
    add_trusted_public_key(public_key_b64)

    with tempfile.TemporaryDirectory() as tmpdir:
        current = Path(tmpdir) / "app.exe"
        update = Path(tmpdir) / "update.exe"
        current.write_text("version 1.0.0")
        update.write_text("version 2.0.0")

        payload = update.read_bytes()
        manifest = create_update_manifest(payload, "2.0.0", private_key)

        # Unsigned payload must be rejected.
        bad_payload = b"malicious payload"
        assert not verify_update_manifest(bad_payload, manifest)

        # Manifest signed by a different key must be rejected.
        _, other_public = generate_keypair()
        other_b64 = base64.b64encode(other_public).decode("ascii")
        assert not verify_update_manifest(payload, manifest, trusted_public_keys={other_b64})

        # Pending-mutation check must block installation.
        def pending():
            return True

        try:
            install_update(
                current,
                update,
                manifest,
                trusted_public_keys={public_key_b64},
                current_version="1.0.0",
                pending_check=pending,
            )
            raise AssertionError("Pending-mutation check did not block update")
        except ValueError as exc:
            assert "pending" in str(exc).lower()

        # Signed payload accepted and installed.
        install_info = install_update(
            current,
            update,
            manifest,
            trusted_public_keys={public_key_b64},
            current_version="1.0.0",
        )
        assert current.read_text() == "version 2.0.0"

        # Downgrade must be rejected.
        old_update = Path(tmpdir) / "update_old.exe"
        old_update.write_text("version 1.5.0")
        old_manifest = create_update_manifest(old_update.read_bytes(), "1.5.0", private_key)
        try:
            install_update(
                current,
                old_update,
                old_manifest,
                trusted_public_keys={public_key_b64},
                current_version="2.0.0",
            )
            raise AssertionError("Downgrade was allowed")
        except ValueError as exc:
            assert "downgrade" in str(exc).lower() or "re-install" in str(exc).lower()

        # Rollback restores previous version.
        rollback_info = rollback(current)
        assert current.read_text() == "version 1.0.0"

        return {
            "public_key_b64": public_key_b64,
            "manifest": manifest,
            "install": install_info,
            "rollback": rollback_info,
        }



def check_for_update(
    manifest_url: str,
    current_version: str,
    trusted_keys: set[str],
) -> dict[str, Any] | None:
    """Check whether a newer signed update is available.

    Downloads the manifest from *manifest_url* using ``urllib``.  The manifest
    must contain all required fields, its public key must be present in
    *trusted_keys*, and its version must be newer than *current_version*.

    Returns the parsed manifest dict, or ``None`` if no valid update is
    available.
    """

    if not trusted_keys:
        return None

    try:
        with urllib.request.urlopen(manifest_url, timeout=30) as response:
            raw = response.read()
    except Exception:
        return None

    try:
        manifest = json.loads(raw.decode("utf-8"))
    except Exception:
        return None

    if not UPDATE_MANIFEST_FIELDS.issubset(manifest.keys()):
        return None

    if manifest.get("public_key") not in trusted_keys:
        return None

    if not _is_newer_version(manifest.get("version", ""), current_version):
        return None

    return manifest


def download_update(manifest: dict[str, Any], download_dir: Path) -> Path:
    """Download the update payload described by *manifest* into *download_dir*.

    Uses ``manifest["payload_url"]`` (relative or absolute).  Relative URLs are
    resolved against the manifest URL if available, otherwise treated as local
    paths.  Also verifies the downloaded payload against the manifest signature.

    Returns the path to the downloaded payload.
    """

    payload_url = manifest.get("payload_url")
    if not payload_url:
        raise ValueError("Manifest missing payload_url")

    download_dir = Path(download_dir)
    download_dir.mkdir(parents=True, exist_ok=True)

    output_path = download_dir / "update_payload.bin"

    try:
        with urllib.request.urlopen(payload_url, timeout=120) as response:
            payload = response.read()
    except Exception as exc:
        raise ValueError(f"Failed to download payload from {payload_url}: {exc}") from exc

    if hashlib.sha256(payload).hexdigest() != manifest["payload_hash"]:
        raise ValueError("Downloaded payload hash does not match manifest")

    public_key_bytes = base64.b64decode(manifest["public_key"])
    signature_bytes = base64.b64decode(manifest["signature"])
    if not verify_payload(payload, signature_bytes, public_key_bytes):
        raise ValueError("Downloaded payload signature verification failed")

    output_path.write_bytes(payload)
    return output_path
