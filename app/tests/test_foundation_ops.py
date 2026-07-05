"""Tests de los módulos operativos Foundation Beta (M10, M13, M14, M17).

No dependen del módulo de auth (M08): montan una app FastAPI mínima con el
``foundation_router`` y siembran tenant/usuario/rol/sesión directamente con
``core`` (fnd_db + seed_system_roles), pasando el header ``X-Fnd-Session``.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.src.foundation import core, foundation_router, init_foundation_db
from app.src.foundation import m13_draft_hitl


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _seed_identity(email: str, tenant_slug: str, role: str = "owner",
                   tenant_id: str | None = None) -> dict[str, str]:
    """Crea (si hace falta) tenant + usuario + rol + sesión 'full'. Devuelve ids."""
    with core.fnd_db() as conn:
        if tenant_id is None:
            existing = conn.execute(
                "SELECT id FROM fnd_tenants WHERE slug = ?", (tenant_slug,)
            ).fetchone()
            if existing:
                tenant_id = existing["id"]
            else:
                tenant_id = core.new_id("tnt")
                conn.execute(
                    """INSERT INTO fnd_tenants (id, name, slug, status, created_at, activated_at)
                       VALUES (?, ?, ?, 'active', ?, ?)""",
                    (tenant_id, tenant_slug, tenant_slug, core.utcnow(), core.utcnow()),
                )
        core.seed_system_roles(conn, tenant_id)
        user_id = core.new_id("usr")
        conn.execute(
            """INSERT INTO fnd_users (id, tenant_id, email, display_name, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, tenant_id, email, email.split("@")[0], core.utcnow()),
        )
        role_row = conn.execute(
            "SELECT id FROM fnd_roles WHERE tenant_id = ? AND name = ?",
            (tenant_id, role),
        ).fetchone()
        conn.execute(
            """INSERT INTO fnd_user_roles (tenant_id, user_id, role_id, assigned_at)
               VALUES (?, ?, ?, ?)""",
            (tenant_id, user_id, role_row["id"], core.utcnow()),
        )
        token = "fnds_" + core.new_id("tok")
        expires = (datetime.now(timezone.utc) + timedelta(hours=6)).isoformat()
        conn.execute(
            """INSERT INTO fnd_sessions
               (id, tenant_id, user_id, stage, created_at, expires_at, last_seen_at)
               VALUES (?, ?, ?, 'full', ?, ?, ?)""",
            (token, tenant_id, user_id, core.utcnow(), expires, core.utcnow()),
        )
    return {"tenant_id": tenant_id, "user_id": user_id, "token": token}


@pytest.fixture()
def env(tmp_path, monkeypatch):
    monkeypatch.setenv("FABERLOOM_FOUNDATION_DB", str(tmp_path / "foundation.sqlite3"))
    init_foundation_db()
    app = FastAPI()
    app.include_router(foundation_router, prefix="/api")
    client = TestClient(app)
    owner = _seed_identity("owner@t1.test", "t1", role="owner")
    return {"client": client, "owner": owner}


def _h(identity: dict[str, str]) -> dict[str, str]:
    return {"X-Fnd-Session": identity["token"]}


BASE = "/api/foundation"


# ---------------------------------------------------------------------------
# M10 — Classifier
# ---------------------------------------------------------------------------


def test_classifier_heuristic_rfq(env):
    client, owner = env["client"], env["owner"]
    res = client.post(f"{BASE}/classifier/inbound", headers=_h(owner), json={
        "channel": "email",
        "sender": "cliente@acme.test",
        "subject": "Solicitud de cotización",
        "body": "Buen día, necesitamos presupuesto para 100 unidades. Favor de cotizar.",
    })
    assert res.status_code == 201, res.text
    item = res.json()
    assert item["status"] == "new"

    res = client.post(f"{BASE}/classifier/inbound/{item['id']}/classify", headers=_h(owner))
    assert res.status_code == 200, res.text
    data = res.json()
    cls = data["classification"]
    assert cls["label"] == "rfq"
    assert cls["decided_by"] == "rule"
    assert cls["confidence"] > data["threshold"]
    assert data["meets_threshold"] is True

    # El item quedó classified y aparece filtrado por label.
    res = client.get(f"{BASE}/classifier/inbound", headers=_h(owner),
                     params={"status": "classified", "label": "rfq"})
    assert res.status_code == 200
    items = res.json()["items"]
    assert any(i["id"] == item["id"] for i in items)

    # Evento accionable emitido para M13.
    with core.fnd_db() as conn:
        events = conn.execute(
            "SELECT type FROM fnd_events WHERE tenant_id = ? AND topic = 'classifier'",
            (owner["tenant_id"],),
        ).fetchall()
    types = {e["type"] for e in events}
    assert "classified" in types
    assert "actionable" in types


def test_classifier_low_confidence_and_override(env):
    client, owner = env["client"], env["owner"]
    res = client.post(f"{BASE}/classifier/inbound", headers=_h(owner), json={
        "subject": "hola", "body": "texto sin señales claras",
    })
    item_id = res.json()["id"]
    res = client.post(f"{BASE}/classifier/inbound/{item_id}/classify", headers=_h(owner))
    data = res.json()
    assert data["classification"]["label"] == "other"
    assert data["meets_threshold"] is False

    # Override humano.
    res = client.post(f"{BASE}/classifier/inbound/{item_id}/override",
                      headers=_h(owner), json={"label": "order", "note": "es un pedido"})
    assert res.status_code == 200, res.text
    cls = res.json()["classification"]
    assert cls["label"] == "order"
    assert cls["decided_by"] == "human"
    assert cls["confidence"] == 1.0

    # Label fuera de taxonomía → 422.
    res = client.post(f"{BASE}/classifier/inbound/{item_id}/override",
                      headers=_h(owner), json={"label": "nope"})
    assert res.status_code == 422


def test_classifier_config_roundtrip(env):
    client, owner = env["client"], env["owner"]
    res = client.get(f"{BASE}/classifier/config", headers=_h(owner))
    assert res.status_code == 200
    default_threshold = res.json()["threshold"]

    res = client.put(f"{BASE}/classifier/config", headers=_h(owner), json={
        "threshold": 0.9,
        "rules": [{"label": "rfq", "weight": 0.95, "keywords": ["cotización"], "patterns": []}],
        "version": "2",
    })
    assert res.status_code == 200, res.text
    assert res.json()["threshold"] == 0.9
    assert res.json()["version"] == "2"
    assert res.json()["threshold"] != default_threshold

    # Regex inválido → 422.
    res = client.put(f"{BASE}/classifier/config", headers=_h(owner), json={
        "rules": [{"label": "rfq", "patterns": ["("]}],
    })
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# M13 — Drafts HITL
# ---------------------------------------------------------------------------


def _mk_draft(client, identity, **overrides):
    body = {
        "channel": "email",
        "recipient": "cliente@acme.test",
        "subject": "Re: cotización",
        "body": "Adjuntamos la cotización solicitada.",
        "evidence": {"source": "test"},
    }
    body.update(overrides)
    res = client.post(f"{BASE}/drafts", headers=_h(identity), json=body)
    assert res.status_code == 201, res.text
    return res.json()


def test_draft_state_machine_and_four_eyes(env, monkeypatch):
    client, owner = env["client"], env["owner"]
    reviewer = _seed_identity("reviewer@t1.test", "t1", role="operator",
                              tenant_id=owner["tenant_id"])
    draft = _mk_draft(client, owner)
    assert draft["status"] == "draft"

    # Transiciones inválidas: approve/send antes de tiempo → 409.
    assert client.post(f"{BASE}/drafts/{draft['id']}/approve",
                       headers=_h(reviewer)).status_code == 409
    assert client.post(f"{BASE}/drafts/{draft['id']}/send",
                       headers=_h(reviewer), json={}).status_code == 409

    # Edición en draft crea revisión.
    res = client.patch(f"{BASE}/drafts/{draft['id']}", headers=_h(owner),
                       json={"body": "Versión corregida del texto."})
    assert res.status_code == 200
    assert len(res.json()["revisions"]) == 1
    assert res.json()["revisions"][0]["body"] == "Adjuntamos la cotización solicitada."

    # Submit → pending_review; doble submit → 409.
    res = client.post(f"{BASE}/drafts/{draft['id']}/submit", headers=_h(owner))
    assert res.status_code == 200
    assert res.json()["status"] == "pending_review"
    assert client.post(f"{BASE}/drafts/{draft['id']}/submit",
                       headers=_h(owner)).status_code == 409

    # Four-eyes: el creador NO puede aprobar su propio draft.
    res = client.post(f"{BASE}/drafts/{draft['id']}/approve", headers=_h(owner))
    assert res.status_code == 403

    # Otro usuario con drafts.review sí aprueba.
    res = client.post(f"{BASE}/drafts/{draft['id']}/approve", headers=_h(reviewer))
    assert res.status_code == 200
    assert res.json()["status"] == "approved"
    assert res.json()["reviewed_by"] == reviewer["user_id"]

    # Ya aprobado no se edita ni se rechaza.
    assert client.patch(f"{BASE}/drafts/{draft['id']}", headers=_h(owner),
                        json={"body": "x"}).status_code == 409
    assert client.post(f"{BASE}/drafts/{draft['id']}/reject", headers=_h(reviewer),
                       json={"note": "tarde"}).status_code == 409


def test_draft_reject_flow(env):
    client, owner = env["client"], env["owner"]
    reviewer = _seed_identity("reviewer2@t1.test", "t1", role="operator",
                              tenant_id=owner["tenant_id"])
    draft = _mk_draft(client, owner)
    client.post(f"{BASE}/drafts/{draft['id']}/submit", headers=_h(owner))
    res = client.post(f"{BASE}/drafts/{draft['id']}/reject", headers=_h(reviewer),
                      json={"note": "falta el precio unitario"})
    assert res.status_code == 200
    assert res.json()["status"] == "rejected"
    assert res.json()["review_note"] == "falta el precio unitario"


def test_draft_send_fail_closed_and_override_ack(env, monkeypatch):
    client, owner = env["client"], env["owner"]
    reviewer = _seed_identity("reviewer3@t1.test", "t1", role="operator",
                              tenant_id=owner["tenant_id"])

    # Fuerza el comportamiento fail-closed (M11 ausente).
    def _fail_closed(conn, tenant_id, action, context):
        return {"decision": "needs_approval",
                "reasons": ["policy gate unavailable (fail-closed)"], "policy_id": None}

    monkeypatch.setattr(m13_draft_hitl, "policy_evaluate", _fail_closed)

    draft = _mk_draft(client, owner)
    client.post(f"{BASE}/drafts/{draft['id']}/submit", headers=_h(owner))
    client.post(f"{BASE}/drafts/{draft['id']}/approve", headers=_h(reviewer))

    # Sin override_ack → 409 con motivos.
    res = client.post(f"{BASE}/drafts/{draft['id']}/send", headers=_h(reviewer), json={})
    assert res.status_code == 409, res.text
    detail = res.json()["detail"]
    assert detail["decision"] == "needs_approval"
    assert detail["reasons"]

    # Con override_ack de alguien con drafts.send → sent.
    res = client.post(f"{BASE}/drafts/{draft['id']}/send", headers=_h(reviewer),
                      json={"override_ack": True})
    assert res.status_code == 200, res.text
    sent = res.json()
    assert sent["status"] == "sent"
    assert sent["sent_at"]
    assert sent["policy_decision"]["decision"] == "needs_approval"

    # Reenviar → 409 (ya no está en approved).
    assert client.post(f"{BASE}/drafts/{draft['id']}/send", headers=_h(reviewer),
                       json={"override_ack": True}).status_code == 409


def test_draft_send_deny(env, monkeypatch):
    client, owner = env["client"], env["owner"]
    reviewer = _seed_identity("reviewer4@t1.test", "t1", role="operator",
                              tenant_id=owner["tenant_id"])
    monkeypatch.setattr(
        m13_draft_hitl, "policy_evaluate",
        lambda conn, tenant_id, action, context: {
            "decision": "deny", "reasons": ["destinatario bloqueado"], "policy_id": "pol_x"},
    )
    draft = _mk_draft(client, owner)
    client.post(f"{BASE}/drafts/{draft['id']}/submit", headers=_h(owner))
    client.post(f"{BASE}/drafts/{draft['id']}/approve", headers=_h(reviewer))
    res = client.post(f"{BASE}/drafts/{draft['id']}/send", headers=_h(reviewer),
                      json={"override_ack": True})
    assert res.status_code == 422
    assert res.json()["detail"]["reasons"] == ["destinatario bloqueado"]


# ---------------------------------------------------------------------------
# M14 — Outcome Ledger
# ---------------------------------------------------------------------------


def test_outcomes_append_only_and_stats(env):
    client, owner = env["client"], env["owner"]
    for outcome, score in [("accepted", 0.9), ("accepted", 0.8),
                           ("edited", 0.5), ("rejected", None)]:
        res = client.post(f"{BASE}/outcomes", headers=_h(owner), json={
            "kind": "draft", "ref_id": "drf_1", "outcome": outcome, "score": score,
            "feedback": "precio incorrecto" if outcome == "rejected" else "",
        })
        assert res.status_code == 201, res.text

    # Ledger: no existen endpoints de update/delete (404/405 según el router).
    outcome_id = client.get(f"{BASE}/outcomes", headers=_h(owner)).json()["outcomes"][0]["id"]
    assert client.patch(f"{BASE}/outcomes/{outcome_id}", headers=_h(owner),
                        json={}).status_code in (404, 405)
    assert client.delete(f"{BASE}/outcomes/{outcome_id}",
                         headers=_h(owner)).status_code in (404, 405)

    # Filtros.
    res = client.get(f"{BASE}/outcomes", headers=_h(owner),
                     params={"kind": "draft", "outcome": "rejected"})
    assert len(res.json()["outcomes"]) == 1

    # Kind/outcome inválidos → 422.
    assert client.post(f"{BASE}/outcomes", headers=_h(owner), json={
        "kind": "bogus", "outcome": "accepted"}).status_code == 422

    # Stats.
    stats = client.get(f"{BASE}/outcomes/stats", headers=_h(owner)).json()
    assert stats["total"] == 4
    assert stats["by_kind"]["draft"]["accepted"] == 2
    assert stats["rates"]["draft_acceptance_rate"] == 0.5
    assert stats["rates"]["draft_edit_rate"] == 0.25
    assert stats["avg_score"] == pytest.approx((0.9 + 0.8 + 0.5) / 3, abs=1e-3)

    # Insights.
    insights = client.get(f"{BASE}/outcomes/insights", headers=_h(owner)).json()
    assert insights["top_rejection_reasons"][0]["reason"] == "precio incorrecto"
    assert insights["weekly_trend"]


# ---------------------------------------------------------------------------
# M17 — Memory
# ---------------------------------------------------------------------------


def test_memory_upsert_recall_archive(env):
    client, owner = env["client"], env["owner"]
    ns = "t1/agente-ventas/task-42"

    res = client.put(f"{BASE}/memory/{ns}/cliente_preferido", headers=_h(owner), json={
        "value": "ACME prefiere entregas los viernes", "kind": "preference",
        "importance": 0.9, "source": "operator",
    })
    assert res.status_code == 200, res.text
    block = res.json()
    assert block["namespace"] == ns and block["key"] == "cliente_preferido"

    # Upsert sobre la misma key → revisión guardada.
    res = client.put(f"{BASE}/memory/{ns}/cliente_preferido", headers=_h(owner), json={
        "value": "ACME prefiere entregas los lunes", "kind": "preference", "importance": 0.9,
    })
    assert res.status_code == 200
    with core.fnd_db() as conn:
        revs = conn.execute(
            "SELECT * FROM fnd_memory_revisions WHERE tenant_id = ? AND block_id = ?",
            (owner["tenant_id"], block["id"]),
        ).fetchall()
    assert len(revs) == 1
    assert "viernes" in revs[0]["value"]

    client.put(f"{BASE}/memory/t1/agente-ventas/dato_suelto", headers=_h(owner), json={
        "value": "El catálogo 2026 tiene 120 SKUs", "kind": "fact", "importance": 0.3,
    })

    # Listado con búsqueda y filtro jerárquico de namespace.
    res = client.get(f"{BASE}/memory", headers=_h(owner),
                     params={"namespace": "t1/agente-ventas", "q": "lunes"})
    blocks = res.json()["blocks"]
    assert len(blocks) == 1 and blocks[0]["key"] == "cliente_preferido"

    # Namespaces con counts.
    res = client.get(f"{BASE}/memory/namespaces", headers=_h(owner))
    tree = {n["namespace"]: n for n in res.json()["tree"]}
    assert tree["t1/agente-ventas"]["total"] == 2

    # Recall rankeado.
    res = client.post(f"{BASE}/memory/recall", headers=_h(owner), json={
        "namespace": "t1", "query": "entregas lunes", "limit": 5,
    })
    results = res.json()["results"]
    assert results and results[0]["key"] == "cliente_preferido"
    assert results[0]["score"] > 0

    # Archivado (no borra).
    res = client.delete(f"{BASE}/memory/{ns}/cliente_preferido", headers=_h(owner))
    assert res.status_code == 200 and res.json()["archived"] is True
    res = client.get(f"{BASE}/memory", headers=_h(owner), params={"namespace": ns})
    assert res.json()["blocks"] == []
    res = client.get(f"{BASE}/memory", headers=_h(owner),
                     params={"namespace": ns, "include_archived": "true"})
    assert len(res.json()["blocks"]) == 1
    # Doble archivado → 404.
    assert client.delete(f"{BASE}/memory/{ns}/cliente_preferido",
                         headers=_h(owner)).status_code == 404


def test_memory_namespace_validation(env):
    client, owner = env["client"], env["owner"]
    res = client.put(f"{BASE}/memory/mal//ns/key", headers=_h(owner),
                     json={"value": "x"})
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# Transversal — permisos y aislamiento de tenant
# ---------------------------------------------------------------------------


def test_permissions_enforced(env):
    client, owner = env["client"], env["owner"]
    viewer = _seed_identity("viewer@t1.test", "t1", role="viewer",
                            tenant_id=owner["tenant_id"])
    # viewer: classifier.read sí, classifier.run no.
    assert client.get(f"{BASE}/classifier/inbound", headers=_h(viewer)).status_code == 200
    assert client.post(f"{BASE}/classifier/inbound", headers=_h(viewer),
                       json={"subject": "x"}).status_code == 403
    # viewer no tiene drafts.* → 403 incluso en GET.
    assert client.get(f"{BASE}/drafts", headers=_h(viewer)).status_code == 403
    # viewer: outcomes.read sí, outcomes.write no.
    assert client.get(f"{BASE}/outcomes/stats", headers=_h(viewer)).status_code == 200
    assert client.post(f"{BASE}/outcomes", headers=_h(viewer), json={
        "kind": "draft", "outcome": "accepted"}).status_code == 403
    # viewer: memory.read sí, memory.write no.
    assert client.get(f"{BASE}/memory", headers=_h(viewer)).status_code == 200
    assert client.put(f"{BASE}/memory/a/b", headers=_h(viewer),
                      json={"value": "x"}).status_code == 403
    # Sin sesión → 401.
    assert client.get(f"{BASE}/classifier/inbound").status_code == 401


def test_tenant_isolation(env):
    client, owner = env["client"], env["owner"]
    other = _seed_identity("owner@t2.test", "t2", role="owner")
    assert other["tenant_id"] != owner["tenant_id"]

    # Datos del tenant 1.
    res = client.post(f"{BASE}/classifier/inbound", headers=_h(owner), json={
        "subject": "cotización urgente", "body": "presupuesto por favor"})
    item_id = res.json()["id"]
    draft = _mk_draft(client, owner)
    client.put(f"{BASE}/memory/t1/agente/x", headers=_h(owner), json={"value": "secreto t1"})
    client.post(f"{BASE}/outcomes", headers=_h(owner), json={
        "kind": "draft", "outcome": "accepted"})

    # El tenant 2 no ve nada.
    assert client.get(f"{BASE}/classifier/inbound", headers=_h(other)).json()["items"] == []
    assert client.get(f"{BASE}/drafts", headers=_h(other)).json()["drafts"] == []
    assert client.get(f"{BASE}/memory", headers=_h(other)).json()["blocks"] == []
    assert client.get(f"{BASE}/outcomes", headers=_h(other)).json()["outcomes"] == []
    assert client.get(f"{BASE}/outcomes/stats", headers=_h(other)).json()["total"] == 0

    # Acceso directo por id cruzado → 404.
    assert client.get(f"{BASE}/drafts/{draft['id']}", headers=_h(other)).status_code == 404
    assert client.post(f"{BASE}/classifier/inbound/{item_id}/classify",
                       headers=_h(other)).status_code == 404
    assert client.delete(f"{BASE}/memory/t1/agente/x", headers=_h(other)).status_code == 404
