"""Encrypted local storage for AI provider configuration.

Provider API keys and runtime settings are persisted in the user data directory
(%LOCALAPPDATA%/FaberLoom/providers.json on Windows) encrypted with Fernet. The
master key is read from FABERLOOM_MASTER_KEY or stored in .master_key in the same
directory. Environment variables always take precedence over stored values so
users can BYOK without persisting secrets to disk.

From schema v19 the store supports per-user configuration. From the tenant
hardening pass it also scopes those users under ``tenants[<tenant_id>]``.
Provider entries that live outside a user slice act as the tenant-wide default
and are copied into a user's slice on first write so later edits stay isolated.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet

from ..context import DEFAULT_TENANT_ID, Context


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


def encrypt_value(value: str | None) -> str | None:
    """Encrypt a sensitive string with the configured master key.

    Returns ``None`` for ``None`` input so nullable secrets stay null.
    """

    if value is None:
        return None
    return Fernet(get_master_key()).encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_value(value: str | None) -> str | None:
    """Decrypt a value encrypted with :func:`encrypt_value`.

    If decryption fails, the original value is returned as a fallback for
    legacy plaintext rows. This makes migrations from plaintext to encrypted
    storage transparent.
    """

    if value is None:
        return None
    try:
        return Fernet(get_master_key()).decrypt(value.encode("utf-8")).decode("utf-8")
    except Exception:
        return value


def _is_global_user_id(user_id: str | None) -> bool:
    """Return True for identities that should use the shared/global config slice."""

    return user_id is None or user_id == "local"


def _resolve_tenant_id(tenant_id: str | None) -> str:
    return tenant_id if tenant_id else DEFAULT_TENANT_ID


class ProviderConfigStore:
    """Encrypted JSON store for provider runtime configuration."""

    FILE_NAME = "providers.json"

    def __init__(self) -> None:
        self._config_dir = get_config_dir()
        self._config_dir.mkdir(parents=True, exist_ok=True)
        self._path = self._config_dir / self.FILE_NAME
        self._fernet = Fernet(get_master_key())

    def load(self) -> dict[str, Any]:
        """Decrypt and return the full provider configuration dictionary."""

        if not self._path.exists():
            return {}
        try:
            encrypted = self._path.read_bytes()
            decrypted = self._fernet.decrypt(encrypted)
            data = json.loads(decrypted.decode("utf-8"))
        except Exception:
            # A corrupted or un-decryptable store is treated as empty. The user
            # can reconfigure providers through the UI.
            return {}

        if isinstance(data, dict) and "tenants" not in data:
            # Migrate legacy stores that kept per-user slices (and optional
            # global entries) at the document root into the default tenant.
            if data:
                data = {"tenants": {_resolve_tenant_id(None): data}}
        return data if isinstance(data, dict) else {}

    def save(self, data: dict[str, Any]) -> None:
        """Encrypt and persist the provider configuration dictionary."""

        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        encrypted = self._fernet.encrypt(payload)
        self._path.write_bytes(encrypted)

    def _tenant_root(self, data: dict[str, Any], tenant_id: str | None) -> dict[str, Any]:
        """Return the configuration slice for ``tenant_id``."""

        tenants = data.setdefault("tenants", {})
        if not isinstance(tenants, dict):
            tenants = {}
            data["tenants"] = tenants
        return tenants.setdefault(_resolve_tenant_id(tenant_id), {})

    def _user_root(
        self,
        data: dict[str, Any],
        user_id: str | None,
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        """Return the configuration slice for ``user_id`` inside ``tenant_id``.

        For the global/local identity this is the tenant root. For real users
        the slice is taken from ``data["tenants"][tenant_id]["users"][user_id]``;
        if the user has no slice yet the tenant-wide configuration is returned
        so existing deployments keep working.
        """

        root = self._tenant_root(data, tenant_id)
        if _is_global_user_id(user_id):
            return root
        users = root.setdefault("users", {})
        if not isinstance(users, dict):
            users = {}
            root["users"] = users
        return users.get(user_id, root) if isinstance(users, dict) else root

    def _ensure_user_copy(
        self,
        data: dict[str, Any],
        user_id: str | None,
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        """Return a mutable per-user config slice, seeding it from tenant defaults."""

        root = self._tenant_root(data, tenant_id)
        if _is_global_user_id(user_id):
            return root
        users = root.setdefault("users", {})
        if not isinstance(users, dict):
            users = {}
            root["users"] = users
        if user_id not in users:
            # Seed the user's slice from tenant-wide provider entries so that
            # later edits are isolated from the shared configuration.
            users[user_id] = {
                slug: dict(config)
                for slug, config in root.items()
                if slug != "users"
            }
        return users[user_id]

    def get(
        self,
        slug: str,
        user_id: str | None = None,
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        """Return the stored configuration for a single provider."""

        data = self.load()
        return self._user_root(data, user_id, tenant_id).get(slug, {})

    def set(
        self,
        slug: str,
        values: dict[str, Any],
        user_id: str | None = None,
        tenant_id: str | None = None,
    ) -> None:
        """Merge new values into a provider entry and persist."""

        data = self.load()
        root = self._ensure_user_copy(data, user_id, tenant_id)
        current = root.get(slug, {})
        for key, value in values.items():
            if value is None:
                current.pop(key, None)
            else:
                current[key] = value
        root[slug] = current
        self.save(data)

    def delete_key(
        self,
        slug: str,
        user_id: str | None = None,
        tenant_id: str | None = None,
    ) -> None:
        """Remove only the API key for a provider."""

        data = self.load()
        root = self._ensure_user_copy(data, user_id, tenant_id)
        if slug in root:
            root[slug].pop("api_key", None)
            self.save(data)

    def delete(
        self,
        slug: str,
        user_id: str | None = None,
        tenant_id: str | None = None,
    ) -> None:
        """Remove an entire provider entry."""

        data = self.load()
        root = self._ensure_user_copy(data, user_id, tenant_id)
        root.pop(slug, None)
        self.save(data)

    def all(
        self,
        user_id: str | None = None,
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        """Return the provider configuration dictionary for ``user_id``."""

        data = self.load()
        root = self._user_root(data, user_id, tenant_id)
        return {k: v for k, v in root.items() if k != "users"}


def get_user_provider_config(ctx: Context, slug: str) -> dict[str, Any]:
    """Return the stored configuration for ``slug`` in the caller's tenant."""

    return ProviderConfigStore().get(slug, ctx.user_id, ctx.tenant_id)


def set_user_provider_config(
    ctx: Context, slug: str, values: dict[str, Any]
) -> None:
    """Merge provider values in the caller's tenant/user slice."""

    ProviderConfigStore().set(slug, values, ctx.user_id, ctx.tenant_id)


def delete_user_provider_config(ctx: Context, slug: str) -> None:
    """Remove an entire provider entry in the caller's tenant/user slice."""

    ProviderConfigStore().delete(slug, ctx.user_id, ctx.tenant_id)


def delete_user_provider_key(ctx: Context, slug: str) -> None:
    """Remove only the API key for a provider in the caller's tenant/user slice."""

    ProviderConfigStore().delete_key(slug, ctx.user_id, ctx.tenant_id)


def list_user_provider_configs(ctx: Context) -> dict[str, Any]:
    """Return the provider configuration dictionary for the caller."""

    return ProviderConfigStore().all(ctx.user_id, ctx.tenant_id)
