"""Tests for the encrypted provider configuration store."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.src.router.config_store import ProviderConfigStore, get_config_dir, mask_key


def test_get_config_dir_respects_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    target = tmp_path / "cfg"
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(target))
    assert get_config_dir() == target


def test_mask_key_obscures_value() -> None:
    assert mask_key("sk-test1234") == "sk-t•••1234"
    assert mask_key("short") == "•" * 5
    assert mask_key(None) is None
    assert mask_key("") is None


def test_store_encrypts_and_decrypts_values(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path / "cfg"))
    store = ProviderConfigStore()
    store.set("openai", {"api_key": "sk-secret", "model_default": "gpt-4o-mini", "priority": 5, "is_enabled": True})

    # Re-create the store to force a reload from disk.
    store2 = ProviderConfigStore()
    cfg = store2.get("openai")
    assert cfg["api_key"] == "sk-secret"
    assert cfg["model_default"] == "gpt-4o-mini"
    assert cfg["priority"] == 5
    assert cfg["is_enabled"] is True

    # Raw file must not contain the secret.
    raw = (tmp_path / "cfg" / "providers.json").read_bytes()
    assert b"sk-secret" not in raw


def test_store_merge_keeps_untouched_fields(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path / "cfg"))
    store = ProviderConfigStore()
    store.set("openai", {"api_key": "sk-secret", "model_default": "gpt-4o-mini"})
    store.set("openai", {"priority": 7})

    cfg = store.get("openai")
    assert cfg["api_key"] == "sk-secret"
    assert cfg["model_default"] == "gpt-4o-mini"
    assert cfg["priority"] == 7


def test_store_delete_key(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path / "cfg"))
    store = ProviderConfigStore()
    store.set("openai", {"api_key": "sk-secret", "model_default": "gpt-4o-mini"})
    store.delete_key("openai")

    cfg = store.get("openai")
    assert "api_key" not in cfg
    assert cfg["model_default"] == "gpt-4o-mini"


def test_store_delete_provider(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path / "cfg"))
    store = ProviderConfigStore()
    store.set("openai", {"api_key": "sk-secret"})
    store.set("anthropic", {"api_key": "sk-ant-secret"})
    store.delete("openai")

    assert store.get("openai") == {}
    assert store.get("anthropic")["api_key"] == "sk-ant-secret"


def test_store_isolates_users(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Changing a provider for one user must not affect another user or the global fallback."""

    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path / "cfg"))
    store = ProviderConfigStore()

    # Seed a global default.
    store.set("openai", {"api_key": "sk-global", "model_default": "gpt-4o-mini"})

    # User A changes only their copy.
    store.set("openai", {"api_key": "sk-user-a"}, user_id="user-a@example.com")
    assert store.get("openai", user_id="user-a@example.com")["api_key"] == "sk-user-a"
    assert store.get("openai", user_id="user-a@example.com")["model_default"] == "gpt-4o-mini"

    # User B falls back to global.
    assert store.get("openai", user_id="user-b@example.com")["api_key"] == "sk-global"

    # Global/local reads remain unchanged.
    assert store.get("openai")["api_key"] == "sk-global"
    assert store.get("openai", user_id="local")["api_key"] == "sk-global"


def test_store_user_delete_does_not_affect_global(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path / "cfg"))
    store = ProviderConfigStore()
    store.set("openai", {"api_key": "sk-global"})

    store.delete_key("openai", user_id="user-a@example.com")
    assert store.get("openai", user_id="user-a@example.com").get("api_key") is None
    assert store.get("openai")["api_key"] == "sk-global"


def test_store_user_delete_provider_does_not_affect_global(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path / "cfg"))
    store = ProviderConfigStore()
    store.set("openai", {"api_key": "sk-global"})

    store.delete("openai", user_id="user-a@example.com")
    assert store.get("openai", user_id="user-a@example.com") == {}
    assert store.get("openai")["api_key"] == "sk-global"
