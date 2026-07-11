"""E3-0 — Ingesta de KB H3 (Marluvas/Tecmater) vía script masivo.

Usa fixtures sintéticos en un directorio temporal; no incluye datos reales.
El objetivo es validar el mecanismo de carga masiva y la estructura de citas.
"""

from __future__ import annotations

import importlib.util
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient


def _load_ingest_module() -> Any:
    script = Path(__file__).resolve().parents[1] / "scripts" / "ingest_kb_h3.py"
    spec = importlib.util.spec_from_file_location("ingest_kb_h3", script)
    module = importlib.util.module_from_spec(spec)
    sys.modules["ingest_kb_h3"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(tmp_path / "faberloom.sqlite3"))
    monkeypatch.setenv("FABERLOOM_FOUNDATION_DB", str(tmp_path / "foundation.sqlite3"))
    monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret-key-at-least-32-bytes-long-xyz")
    monkeypatch.setenv("FABERLOOM_USERS", '{"test@example.test":"password"}')
    monkeypatch.delenv("FABERLOOM_AUTH_DISABLED", raising=False)

    from app.src.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client


def _foundation_conn(client: TestClient) -> sqlite3.Connection:
    path = os.environ["FABERLOOM_FOUNDATION_DB"]
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _app_conn(client: TestClient) -> sqlite3.Connection:
    path = os.environ["FABERLOOM_DB_PATH"]
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _auth_headers(tenant_id: str, role: str = "owner", user_id: str = "usr_test") -> dict[str, str]:
    from app.src.auth import create_access_token

    token = create_access_token(
        "test@example.test",
        tenant_id=tenant_id,
        user_id=user_id,
        role=role,
    )
    return {"Authorization": f"Bearer {token}"}


def _bootstrap_tenant(client: TestClient, slug: str, owner_email: str) -> str:
    from app.src.foundation.core import new_id, seed_system_roles, utcnow

    conn = _foundation_conn(client)
    try:
        tenant_id = new_id("tnt")
        conn.execute(
            """
            INSERT INTO fnd_tenants
            (id, name, slug, status, plan, created_at, activated_at)
            VALUES (?, ?, ?, 'active', 'starter', ?, ?)
            """,
            (tenant_id, f"Tenant {slug}", slug, utcnow(), utcnow()),
        )
        seed_system_roles(conn, tenant_id)
        user_id = new_id("usr")
        conn.execute(
            """
            INSERT INTO fnd_users
            (id, tenant_id, email, display_name, password_hash, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'active', ?)
            """,
            (
                user_id,
                tenant_id,
                owner_email,
                owner_email.split("@")[0],
                "irrelevant",
                utcnow(),
            ),
        )
        role_row = conn.execute(
            "SELECT id FROM fnd_roles WHERE tenant_id = ? AND name = 'owner'",
            (tenant_id,),
        ).fetchone()
        conn.execute(
            """
            INSERT INTO fnd_user_roles (tenant_id, user_id, role_id, assigned_by, assigned_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (tenant_id, user_id, role_row["id"], user_id, utcnow()),
        )
        conn.commit()
        return tenant_id
    finally:
        conn.close()


def _create_workspace(client: TestClient, tenant_id: str) -> dict[str, Any]:
    resp = client.post(
        "/api/workspaces",
        json={"name": "KB H3 Test Workspace"},
        headers=_auth_headers(tenant_id),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _write_fixture_sources(source_dir: Path) -> None:
    source_dir.mkdir(parents=True, exist_ok=True)
    (source_dir / "catalogo_marluvas.md").write_text(
        "# Catálogo Marluvas (fixture de prueba)\n\n"
        "- Oxford 200: $12.50/m\n"
        "- Lino 300: $18.00/m\n",
        encoding="utf-8",
    )
    (source_dir / "precios_tecmater.csv").write_text(
        "sku,descripcion,precio_usd\n"
        "TEC001,Tela demo A,9.50\n"
        "TEC002,Tela demo B,14.00\n",
        encoding="utf-8",
    )
    (source_dir / "notas.txt").write_text(
        "Notas internas de prueba para validar ingest KB H3.",
        encoding="utf-8",
    )
    (source_dir / "ignorado.xyz").write_text("no soportado", encoding="utf-8")


def test_kb_h3_dry_run_lists_sources(client: TestClient) -> None:
    module = _load_ingest_module()
    tenant_id = _bootstrap_tenant(client, "kbh3dry", "kbh3dry@example.test")
    ws = _create_workspace(client, tenant_id)
    source_dir = Path(os.environ["FABERLOOM_DB_PATH"]).parent / "kb_h3"
    _write_fixture_sources(source_dir)

    rc = module.main(
        [
            "--tenant-id",
            tenant_id,
            "--workspace-id",
            ws["id"],
            "--source-dir",
            str(source_dir),
        ]
    )
    assert rc == 0

    conn = _app_conn(client)
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM kb_source WHERE workspace_id = ?", (ws["id"],)
        ).fetchone()
        assert row["n"] == 0
    finally:
        conn.close()


def test_kb_h3_ingest_creates_sources_and_chunks(client: TestClient) -> None:
    module = _load_ingest_module()
    tenant_id = _bootstrap_tenant(client, "kbh3ingest", "kbh3ingest@example.test")
    ws = _create_workspace(client, tenant_id)
    source_dir = Path(os.environ["FABERLOOM_DB_PATH"]).parent / "kb_h3"
    _write_fixture_sources(source_dir)

    rc = module.main(
        [
            "--tenant-id",
            tenant_id,
            "--workspace-id",
            ws["id"],
            "--source-dir",
            str(source_dir),
            "--execute",
            "--approved-by",
            "usr_test",
        ]
    )
    assert rc == 0

    conn = _app_conn(client)
    try:
        sources = conn.execute(
            "SELECT title, type, approved_by FROM kb_source WHERE workspace_id = ? ORDER BY title",
            (ws["id"],),
        ).fetchall()
        titles = [s["title"] for s in sources]
        assert "catalogo_marluvas" in titles
        assert "precios_tecmater" in titles
        assert "notas" in titles

        csv_source = next(s for s in sources if s["type"] == "csv")
        assert csv_source["approved_by"] == "usr_test"

        chunks = conn.execute(
            "SELECT COUNT(*) AS n FROM kb_chunk WHERE workspace_id = ?", (ws["id"],)
        ).fetchone()
        assert chunks["n"] > 0
    finally:
        conn.close()


def test_kb_h3_requires_valid_tenant_workspace(client: TestClient) -> None:
    module = _load_ingest_module()
    tenant_id = _bootstrap_tenant(client, "kbh3bad", "kbh3bad@example.test")
    # No creamos el workspace -> ingest debe fallar por contexto inválido
    source_dir = Path(os.environ["FABERLOOM_DB_PATH"]).parent / "kb_h3"
    _write_fixture_sources(source_dir)

    with pytest.raises(Exception):
        module.main(
            [
                "--tenant-id",
                tenant_id,
                "--workspace-id",
                "ws_inexistente",
                "--source-dir",
                str(source_dir),
                "--execute",
            ]
        )
