#!/usr/bin/env python3
"""Smoke end-to-end idempotente contra producción.

Flujo:
  login → /api/me → list workspaces → crear fl-smoke (si no existe)
  → habilitar ambient workspace config → crear chat general
  → auto-completion con adjunto (best-effort) → brief → shadow-report.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SmokeStep:
    name: str
    status: str = "pending"
    status_code: int | None = None
    detail: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    response: dict[str, Any] = field(default_factory=dict)


@dataclass
class SmokeReport:
    started_at: str = field(default_factory=_now)
    ended_at: str | None = None
    base_url: str = ""
    tenant_id: str | None = None
    workspace_id: str | None = None
    chat_id: str | None = None
    all_ok: bool = True
    steps: list[SmokeStep] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SmokeClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers["Accept"] = "application/json"

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def login(self, email: str, password: str) -> SmokeStep:
        step = SmokeStep(name="login")
        r = self.session.post(
            self._url("/api/auth/login"),
            json={"email": email, "password": password},
            timeout=30,
        )
        step.status_code = r.status_code
        if r.status_code == 200:
            step.status = "ok"
            step.response = r.json()
        else:
            step.status = "failed"
            step.detail = r.text[:500]
        return step

    def me(self) -> SmokeStep:
        step = SmokeStep(name="me")
        r = self.session.get(self._url("/api/me"), timeout=30)
        step.status_code = r.status_code
        if r.status_code == 200:
            step.status = "ok"
            step.response = r.json()
        else:
            step.status = "failed"
            step.detail = r.text[:500]
        return step

    def list_workspaces(self) -> SmokeStep:
        step = SmokeStep(name="list_workspaces")
        r = self.session.get(self._url("/api/workspaces"), timeout=30)
        step.status_code = r.status_code
        if r.status_code == 200:
            step.status = "ok"
            step.response = r.json()
        else:
            step.status = "failed"
            step.detail = r.text[:500]
        return step

    def create_workspace(self, name: str, slug: str) -> SmokeStep:
        step = SmokeStep(name="create_workspace")
        r = self.session.post(
            self._url("/api/workspaces"),
            json={"name": name, "slug": slug},
            timeout=30,
        )
        step.status_code = r.status_code
        if r.status_code in (200, 201):
            step.status = "ok"
            step.response = r.json()
        elif r.status_code == 409:
            step.status = "skipped"
            step.detail = "workspace already exists"
        else:
            step.status = "failed"
            step.detail = r.text[:500]
        return step

    def enable_ambient_workspace(self, workspace_id: str) -> SmokeStep:
        step = SmokeStep(name="enable_ambient_workspace")
        r = self.session.patch(
            self._url(f"/api/admin/ambient/workspaces/{workspace_id}/config"),
            json={"enabled": True},
            timeout=30,
        )
        step.status_code = r.status_code
        if r.status_code in (200, 201):
            step.status = "ok"
            step.response = r.json()
        else:
            step.status = "failed"
            step.detail = r.text[:500]
        return step

    def create_chat(self, workspace_id: str, title: str = "general") -> SmokeStep:
        step = SmokeStep(name="create_chat")
        r = self.session.post(
            self._url(f"/api/workspaces/{workspace_id}/chats"),
            json={"title": title},
            timeout=30,
        )
        step.status_code = r.status_code
        if r.status_code in (200, 201):
            step.status = "ok"
            step.response = r.json()
        else:
            step.status = "failed"
            step.detail = r.text[:500]
        return step

    def auto_chain(
        self,
        workspace_id: str,
        chat_id: str,
        user_request: str,
        attachment_object_id: str | None = None,
    ) -> SmokeStep:
        step = SmokeStep(name="auto_chain")
        payload: dict[str, Any] = {"user_request": user_request}
        if attachment_object_id:
            payload["attachments"] = [{"object_id": attachment_object_id}]
        r = self.session.post(
            self._url(f"/api/workspaces/{workspace_id}/chats/{chat_id}/auto"),
            json=payload,
            timeout=120,
        )
        step.status_code = r.status_code
        step.payload = payload
        if r.status_code in (200, 201):
            step.status = "ok"
            step.response = r.json()
        else:
            step.status = "failed"
            step.detail = r.text[:500]
        return step

    def upload_attachment(
        self, workspace_id: str, file_path: str, title: str = "smoke attachment"
    ) -> SmokeStep:
        step = SmokeStep(name="upload_attachment")
        path = Path(file_path)
        r = self.session.post(
            self._url(f"/api/workspaces/{workspace_id}/kb/upload"),
            data={"title": title, "source_version": "v1", "level": "0"},
            files={"file": (path.name, path.open("rb"), "text/plain")},
            timeout=60,
        )
        step.status_code = r.status_code
        if r.status_code in (200, 201):
            step.status = "ok"
            step.response = r.json()
        else:
            step.status = "failed"
            step.detail = r.text[:500]
        return step

    def brief(self, workspace_id: str) -> SmokeStep:
        step = SmokeStep(name="brief")
        r = self.session.get(
            self._url(f"/api/workspaces/{workspace_id}/brief"), timeout=30
        )
        step.status_code = r.status_code
        if r.status_code == 200:
            step.status = "ok"
            step.response = r.json()
        elif r.status_code == 404:
            step.status = "ok"
            step.detail = "brief not found (expected for new workspace)"
            step.response = r.json() if r.text else {}
        else:
            step.status = "failed"
            step.detail = r.text[:500]
        return step

    def shadow_report(self, tenant_id: str) -> SmokeStep:
        step = SmokeStep(name="shadow_report")
        r = self.session.get(
            self._url(f"/api/tenants/{tenant_id}/routing/shadow-report"), timeout=30
        )
        step.status_code = r.status_code
        if r.status_code == 200:
            step.status = "ok"
            step.response = r.json()
        else:
            step.status = "failed"
            step.detail = r.text[:500]
        return step


def _find_workspace(workspaces: list[dict[str, Any]], slug: str) -> dict[str, Any] | None:
    for ws in workspaces:
        if ws.get("slug") == slug:
            return ws
    return None


def run_smoke(
    base_url: str,
    email: str,
    password: str,
    workspace_slug: str = "fl-smoke",
    workspace_name: str = "fl-smoke",
    attachment_path: str | None = None,
) -> SmokeReport:
    report = SmokeReport(base_url=base_url)
    client = SmokeClient(base_url)

    step = client.login(email, password)
    report.steps.append(step)
    if step.status != "ok":
        report.all_ok = False
        report.ended_at = _now()
        return report

    step = client.me()
    report.steps.append(step)
    if step.status == "ok":
        report.tenant_id = step.response.get("tenant_id")
    else:
        report.all_ok = False

    step = client.list_workspaces()
    report.steps.append(step)
    if step.status != "ok":
        report.all_ok = False
        report.ended_at = _now()
        return report

    workspaces = step.response.get("workspaces", [])
    ws = _find_workspace(workspaces, workspace_slug)
    if ws is None:
        step = client.create_workspace(workspace_name, workspace_slug)
        report.steps.append(step)
        if step.status in ("ok", "skipped"):
            ws = step.response if step.status == "ok" else None
            # If skipped, reload list
            if step.status == "skipped":
                step2 = client.list_workspaces()
                report.steps.append(step2)
                if step2.status == "ok":
                    ws = _find_workspace(step2.response.get("workspaces", []), workspace_slug)
        else:
            report.all_ok = False
    if ws:
        report.workspace_id = ws.get("id")

    if report.workspace_id:
        step = client.enable_ambient_workspace(report.workspace_id)
        report.steps.append(step)
        if step.status != "ok":
            report.all_ok = False

        step = client.create_chat(report.workspace_id, title="general")
        report.steps.append(step)
        if step.status == "ok":
            report.chat_id = step.response.get("id")
        else:
            report.all_ok = False

        attachment_object_id: str | None = None
        if attachment_path and Path(attachment_path).exists():
            step = client.upload_attachment(report.workspace_id, attachment_path)
            report.steps.append(step)
            if step.status == "ok":
                attachment_object_id = step.response.get("object_id")
            else:
                # attachment is best-effort for this smoke
                pass

        if report.chat_id:
            step = client.auto_chain(
                report.workspace_id,
                report.chat_id,
                "Hola, este es un mensaje de smoke test E2E.",
                attachment_object_id=attachment_object_id,
            )
            report.steps.append(step)
            if step.status != "ok":
                report.all_ok = False

        step = client.brief(report.workspace_id)
        report.steps.append(step)

    if report.tenant_id:
        step = client.shadow_report(report.tenant_id)
        report.steps.append(step)
        if step.status != "ok":
            report.all_ok = False

    report.ended_at = _now()
    return report


def _write_markdown(report: SmokeReport, path: Path) -> None:
    lines = [
        "# Smoke E2E en producción",
        "",
        f"**Fecha:** {report.started_at}",
        f"**Base URL:** {report.base_url}",
        f"**Tenant:** {report.tenant_id}",
        f"**Workspace:** {report.workspace_id}",
        f"**Chat:** {report.chat_id}",
        f"**Resultado:** {'✅ OK' if report.all_ok else '⚠️ CON HALLAZGOS'}",
        "",
        "## Pasos",
        "",
        "| Paso | Estado | HTTP | Detalle |",
        "|------|--------|------|---------|",
    ]
    for s in report.steps:
        detail = (s.detail or "").replace("|", "\\|")
        lines.append(f"| {s.name} | {s.status} | {s.status_code or ''} | {detail} |")
    lines.append("")
    lines.append("## Comando para encender ambient del tenant real")
    lines.append("")
    lines.append("```bash")
    lines.append(f"curl -b cookies.txt -X PATCH {report.base_url}/api/admin/ambient/workspaces/{report.workspace_id or '<WS>'}/config \\")
    lines.append("  -H 'Content-Type: application/json' -d '{\"enabled\":true}'")
    lines.append("```")
    lines.append("")
    lines.append("## Respuestas clave")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    lines.append("```")
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Smoke E2E idempotente en producción")
    parser.add_argument("--base-url", default=os.getenv("SMOKE_BASE_URL", "http://localhost:8200"))
    parser.add_argument("--email", default=os.getenv("SMOKE_EMAIL"))
    parser.add_argument("--password", default=os.getenv("SMOKE_PASSWORD"))
    parser.add_argument("--workspace-slug", default="fl-smoke")
    parser.add_argument("--workspace-name", default="fl-smoke")
    parser.add_argument("--attachment", default=None, help="Archivo adjunto opcional")
    parser.add_argument("--json", default=None, help="Ruta para reporte JSON")
    parser.add_argument("--md", default=None, help="Ruta para reporte Markdown")
    args = parser.parse_args(argv)

    if not args.email or not args.password:
        print("ERROR: --email y --password son requeridos", file=sys.stderr)
        return 1

    report = run_smoke(
        base_url=args.base_url,
        email=args.email,
        password=args.password,
        workspace_slug=args.workspace_slug,
        workspace_name=args.workspace_name,
        attachment_path=args.attachment,
    )

    if args.json:
        Path(args.json).write_text(
            json.dumps(report.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"JSON report written to {args.json}")
    if args.md:
        _write_markdown(report, Path(args.md))
        print(f"Markdown report written to {args.md}")

    print(f"smoke ok={report.all_ok} steps={len(report.steps)} tenant={report.tenant_id} ws={report.workspace_id}")
    return 0 if report.all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
