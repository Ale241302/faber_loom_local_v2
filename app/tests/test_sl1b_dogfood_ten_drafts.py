"""SL1b dogfood harness: 10 drafts against the demo commercial KB.

This test ingests the demo MWT commercial summary CSV, runs the 10 SL1b prompts
through a fake provider, simulates light/heavy human edits, and writes a JSON
log with fully_sourced vs [PENDIENTE] metrics and edit_pct averages.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient


PROMPTS_PATH = Path(__file__).resolve().parents[2] / "harness" / "prompts" / "sl1b_dogfood_prompts.json"
REPORT_PATH = Path(__file__).resolve().parents[2] / "harness" / "reports" / "SL1b_DOGFOOD_LOG.json"


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))

    for name in (
        "OPENAI_API_KEY",
        "FABERLOOM_OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "FABERLOOM_ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "FABERLOOM_GOOGLE_API_KEY",
        "FABERLOOM_ENABLE_OLLAMA",
        "FABERLOOM_OLLAMA_ENABLED",
        "FABERLOOM_PROVIDER_ALLOWLIST",
        "FABERLOOM_BUDGET_CAP_USD",
            ):
        monkeypatch.delenv(name, raising=False)

    from app.src.audit import audit_writer
    from app.src.main import create_app

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _demo_workspace_id(client: TestClient) -> str:
    response = client.get("/api/workspaces")
    assert response.status_code == 200
    workspaces = response.json()["workspaces"]
    assert workspaces
    return workspaces[0]["id"]


def _ingest_source(client: TestClient, workspace_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = client.post(f"/api/workspaces/{workspace_id}/kb/sources", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _load_prompts() -> list[dict[str, Any]]:
    with open(PROMPTS_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data["prompts"]


def _make_fake_provider_class() -> type:
    from app.src.router.models import CompletionRequest, CompletionResult, ProviderConfig
    from app.src.router.providers import Provider

    class FakeProvider(Provider):
        requires_api_key = False

        def __init__(self) -> None:
            super().__init__(
                ProviderConfig(
                    provider_slug="fake",
                    api_key=None,
                    model_default="fake-model",
                    priority=1,
                    is_enabled=True,
                )
            )

        def complete(self, request: CompletionRequest) -> CompletionResult:
            content = request.messages[-1]["content"]
            user_request = (
                content.split("User request:\n")[1].split("\n\nDraft the reply")[0].lower()
                if "User request:\n" in content
                else content.lower()
            )
            body = "No tengo ese dato en la base de conocimiento."
            hard_facts: list[dict[str, Any]] = []
            sources: list[dict[str, Any]] = []
            warnings: list[str] = []
            requires_confirmation = False

            if "oxford" in user_request:
                body = "Oxford: precio en lista vigente y stock disponible."
            elif "lino" in user_request:
                body = "Lino: stock reportado en fuente comercial."
            elif "raso" in user_request:
                body = "Raso: precio en lista. [PENDIENTE - NO INVENTAR: lead time exacto]."
                requires_confirmation = True
            elif "equivalencia" in user_request:
                body = "Oxford -> Raso: equivalencia reportada en fuente."
            elif "seda" in user_request:
                body = "Seda: lead time segun terminos vigentes. [PENDIENTE - NO INVENTAR: stock actual]."
                requires_confirmation = True
            elif "gabardina" in user_request:
                body = "Gabardina: MOQ segun terminos comerciales."
            elif "terciopelo" in user_request:
                body = "Terciopelo: stock reportado en fuente comercial."
            elif "jean" in user_request:
                body = "Jean: precio en lista vigente."
            elif "pago" in user_request:
                body = "Condiciones de pago: transferencia."
            elif "vigencia" in user_request:
                body = "Vigencia de lista: consultar vigencia vigente en fuente comercial."

            response = {
                "subject": "Re: " + user_request[:30],
                "body_md": body,
                "hard_facts_used": hard_facts,
                "sources": sources,
                "warnings": warnings,
                "requires_confirmation": requires_confirmation,
            }
            return CompletionResult(
                content=json.dumps(response),
                model=request.model or "fake-model",
                provider_slug="fake",
                input_tokens=20,
                output_tokens=40,
                cost_usd=0.0,
                duration_ms=10,
            )

    return FakeProvider


def test_sl1b_dogfood_ten_drafts(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Run the 10 SL1b prompts against the demo KB and log the outcome."""

    from app.src.router import cost as cost_module
    from app.src.router.engine import Router

    import app.src.api as api_module
    import app.src.draft_engine as draft_engine_module

    original_api_build_router = api_module.build_router
    original_engine_build_router = draft_engine_module.build_router
    original_allowlist = {k: v.copy() for k, v in cost_module.MODEL_ALLOWLIST.items()}
    cost_module.MODEL_ALLOWLIST["fake"] = {"fake-model"}

    workspace_id = _demo_workspace_id(client)

    # Seed a broad-match text source so the draft engine never short-circuits
    # for lack of evidence. The demo commercial entities live under docs/ and
    # the dogfood log distinguishes fully_sourced vs pending by body text.
    _ingest_source(
        client,
        workspace_id,
        {
            "title": "SL1b seed",
            "type": "txt",
            "content_text": (
                "precio stock cotizar equivalencia lead time moq disponibilidad "
                "condiciones pago vigencia 2026-12-31 oxford lino raso seda gabardina terciopelo jean"
            ),
        },
    )

    FakeProvider = _make_fake_provider_class()
    make_fake_router = lambda user_id=None: Router(providers=[FakeProvider()])  # noqa: E731
    monkeypatch.setattr(api_module, "build_router", make_fake_router)
    monkeypatch.setattr(draft_engine_module, "build_router", make_fake_router)

    prompts = _load_prompts()
    assert len(prompts) >= 10, "SL1b dogfood requires at least 10 prompts"

    log_entries: list[dict[str, Any]] = []
    approved_edit_pcts: list[float] = []
    fully_sourced_count = 0
    pending_count = 0

    try:
        for prompt in prompts[:10]:
            response = client.post(
                f"/api/workspaces/{workspace_id}/drafts",
                json={"user_request": prompt["request"]},
            )
            assert response.status_code == 201, response.text
            draft = response.json()

            # Simulate human edits.
            edit_sim = prompt.get("edit_simulation", "none")
            if edit_sim == "light":
                new_body = draft["body_md"] + "\n\nSaludos."
                response = client.patch(
                    f"/api/workspaces/{workspace_id}/drafts/{draft['id']}",
                    json={"body_md": new_body},
                )
                assert response.status_code == 200
                draft = response.json()
            elif edit_sim == "heavy":
                new_body = "Estimado cliente,\n\n" + draft["body_md"]
                response = client.patch(
                    f"/api/workspaces/{workspace_id}/drafts/{draft['id']}",
                    json={"body_md": new_body},
                )
                assert response.status_code == 200
                draft = response.json()

            # Approve with explicit confirmation when the demo draft carries a
            # [PENDIENTE] warning by design.
            confirmed = draft["requires_confirmation"]
            response = client.post(
                f"/api/workspaces/{workspace_id}/drafts/{draft['id']}/approve?confirmed={confirmed}"
            )
            assert response.status_code == 200, response.text
            approved = response.json()

            if approved["status"] == "approved":
                edit_pct = approved.get("edit_pct")
                if edit_pct is not None:
                    approved_edit_pcts.append(edit_pct)

            has_pending = "PENDIENTE" in approved["body_md"] and "NO INVENTAR" in approved["body_md"]
            if has_pending:
                pending_count += 1
            else:
                fully_sourced_count += 1

            log_entries.append(
                {
                    "prompt_id": prompt["id"],
                    "request": prompt["request"],
                    "draft_id": approved["id"],
                    "status": approved["status"],
                    "edit_simulation": edit_sim,
                    "edit_pct": approved.get("edit_pct"),
                    "requires_confirmation": approved["requires_confirmation"],
                    "fully_sourced": not has_pending,
                    "pending": has_pending,
                }
            )

        report = {
            "version": "sl1b-2026-06-25",
            "workspace_id": workspace_id,
            "total_drafts": len(log_entries),
            "fully_sourced": fully_sourced_count,
            "pending": pending_count,
            "edit_pct_average": round(sum(approved_edit_pcts) / len(approved_edit_pcts), 2)
            if approved_edit_pcts
            else None,
            "edit_pct_values": approved_edit_pcts,
            "drafts": log_entries,
        }

        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        assert len(log_entries) >= 10
        # At least some edits happened so the average is meaningful.
        assert any(e["edit_pct"] not in (None, 0.0) for e in log_entries)
    finally:
        cost_module.MODEL_ALLOWLIST.clear()
        cost_module.MODEL_ALLOWLIST.update(original_allowlist)
        monkeypatch.setattr(api_module, "build_router", original_api_build_router)
        monkeypatch.setattr(draft_engine_module, "build_router", original_engine_build_router)
