"""Encrypted local storage for AI provider configuration.

Provider API keys and runtime settings are persisted in the user data directory
(%LOCALAPPDATA%/FaberLoom/providers.json on Windows) encrypted with Fernet. The
master key is read from FABERLOOM_MASTER_KEY or stored in .master_key in the same
directory. Environment variables always take precedence over stored values so
users can BYOK without persisting secrets to disk.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet


def get_config_dir() -> Path:
    """Return the OS-appropriate FaberLoom config directory.

    Provider config lives next to the SQLite database. Importing from db ensures
    the one-time SpaceLoom -> FaberLoom directory migration runs first.
    """

    env = os.getenv("FABERLOOM_CONFIG_DIR")
    if env:
        return Path(env).expanduser().resolve()
    from ..db import _default_user_data_dir

    return _default_user_data_dir()


def load_env_file(path: Path | str | None = None) -> None:
    """Load a ``.env`` file into ``os.environ`` without overwriting existing vars.

    This lets packaged builds (e.g. the PyInstaller .exe) ship or pick up a local
    ``%LOCALAPPDATA%/FaberLoom/.env`` file with provider keys, matching the
    server-side BYOK injection pattern: the daemon supplies the credential while
    the UI can leave the key field empty.
    """

    env_path = Path(path) if path else get_config_dir() / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("\"'")
        if key and key not in os.environ:
            os.environ[key] = value


def _master_key_path() -> Path:
    return get_config_dir() / ".master_key"


def get_master_key() -> bytes:
    """Return a Fernet-compatible key (32 bytes, urlsafe base64 encoded)."""

    env = os.getenv("FABERLOOM_MASTER_KEY")
    if env:
        key = env.encode("utf-8")
        # Validate shape early; Fernet will raise later if malformed.
        Fernet(key)
        return key

    path = _master_key_path()
    if path.exists():
        key = path.read_text(encoding="utf-8").strip().encode("utf-8")
        Fernet(key)
        return key

    key = Fernet.generate_key()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(key.decode("utf-8"), encoding="utf-8")
    return key


def mask_key(value: str | None) -> str | None:
    """Return a masked representation of an API key (last 4 chars visible)."""

    if not value:
        return None
    if len(value) <= 8:
        return "•" * len(value)
    return value[:4] + "•" * (len(value) - 8) + value[-4:]


class ProviderConfigStore:
    """Encrypted JSON store for provider runtime configuration."""

    FILE_NAME = "providers.json"

    def __init__(self) -> None:
        self._config_dir = get_config_dir()
        self._config_dir.mkdir(parents=True, exist_ok=True)
        self._path = self._config_dir / self.FILE_NAME
        self._fernet = Fernet(get_master_key())

    def load(self) -> dict[str, Any]:
        """Decrypt and return the provider configuration dictionary."""

        if not self._path.exists():
            return {}
        try:
            encrypted = self._path.read_bytes()
            decrypted = self._fernet.decrypt(encrypted)
            return json.loads(decrypted.decode("utf-8"))
        except Exception:
            # A corrupted or un-decryptable store is treated as empty. The user
            # can reconfigure providers through the UI.
            return {}

    def save(self, data: dict[str, Any]) -> None:
        """Encrypt and persist the provider configuration dictionary."""

        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        encrypted = self._fernet.encrypt(payload)
        self._path.write_bytes(encrypted)

    def get(self, slug: str) -> dict[str, Any]:
        return self.load().get(slug, {})

    def set(self, slug: str, values: dict[str, Any]) -> None:
        """Merge new values into a provider entry and persist."""

        data = self.load()
        current = data.get(slug, {})
        for key, value in values.items():
            if value is None:
                current.pop(key, None)
            else:
                current[key] = value
        data[slug] = current
        self.save(data)

    def delete_key(self, slug: str) -> None:
        """Remove only the API key for a provider."""

        data = self.load()
        if slug in data:
            data[slug].pop("api_key", None)
            self.save(data)

    def delete(self, slug: str) -> None:
        """Remove an entire provider entry."""

        data = self.load()
        data.pop(slug, None)
        self.save(data)

    def all(self) -> dict[str, Any]:
        return self.load()
