"""E3-2 — Frontend UI tests for public signup and tenant admin.

These tests verify that the static assets for E3-2 exist and contain the
expected markup/component strings. Full end-to-end browser tests (Playwright)
are deferred until the backend endpoints documented in
app/.tmp/e3_2_frontend_endpoints.md are implemented.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture()
def static_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "static"


def test_signup_html_entry_point_exists_and_references_components(static_dir: Path) -> None:
    """The public signup entry point loads React, icons and signup.jsx."""

    path = static_dir / "signup.html"
    assert path.exists(), f"Missing {path}"
    text = path.read_text(encoding="utf-8")
    assert '<div id="signup-root">' in text
    assert "/static/js/icons.jsx" in text
    assert "/static/js/signup.jsx" in text
    assert "/static/css/main.css" in text
    assert "FaberLoom · Crear empresa" in text


def test_signup_jsx_contains_public_form_and_validation(static_dir: Path) -> None:
    """signup.jsx renders the public form and enforces client-side validation."""

    path = static_dir / "js" / "signup.jsx"
    assert path.exists(), f"Missing {path}"
    text = path.read_text(encoding="utf-8")
    assert "SignupPage" in text
    assert "POST" in text and "/api/public/signup" in text
    assert "owner_email" in text
    assert "owner_password" in text
    assert "Mínimo 12 caracteres" in text
    assert "slug" in text
    assert "Revisá tu correo" in text


def test_tenant_admin_jsx_has_platform_admin_gate(static_dir: Path) -> None:
    """tenant_admin.jsx requires platform_admin and never shows content."""

    path = static_dir / "js" / "tenant_admin.jsx"
    assert path.exists(), f"Missing {path}"
    text = path.read_text(encoding="utf-8")
    assert "TenantAdminPanel" in text
    assert "platform_admin" in text
    assert "/api/admin/tenants" in text
    assert "/api/admin/tenants/metrics" in text
    assert "Aprobar" in text
    assert "Suspender" in text
    assert "sin acceso a contenido" in text
    assert "total_users" in text
    assert "total_cost_usd" in text


def test_tenant_settings_jsx_implements_cascade(static_dir: Path) -> None:
    """tenant_settings.jsx shows resolved cascade and editable overrides."""

    path = static_dir / "js" / "tenant_settings.jsx"
    assert path.exists(), f"Missing {path}"
    text = path.read_text(encoding="utf-8")
    assert "TenantSettings" in text
    assert "/api/tenant/settings" in text
    assert "/api/workspaces/" in text and "/settings" in text
    assert "/api/users/me/settings" in text
    assert "/api/settings/resolved" in text
    assert "user &gt; workspace &gt; tenant &gt; default" in text
    assert "Editar overrides" in text


def test_app_jsx_integrates_new_views(static_dir: Path) -> None:
    """app.jsx adds nav items and Canvas cases for E3-2 views."""

    path = static_dir / "js" / "app.jsx"
    assert path.exists(), f"Missing {path}"
    text = path.read_text(encoding="utf-8")
    assert "tenant-admin" in text
    assert "tenant-settings" in text
    assert "isPlatformAdmin" in text
    assert "TenantAdminPanel" in text
    assert "TenantSettings" in text
    assert "Config. en cascada" in text
    assert "Admin de plataforma" in text


def test_index_html_loads_new_jsx_modules(static_dir: Path) -> None:
    """index.html includes the new tenant_admin and tenant_settings JSX modules."""

    path = static_dir / "index.html"
    assert path.exists(), f"Missing {path}"
    text = path.read_text(encoding="utf-8")
    assert "/static/js/tenant_admin.jsx" in text
    assert "/static/js/tenant_settings.jsx" in text
