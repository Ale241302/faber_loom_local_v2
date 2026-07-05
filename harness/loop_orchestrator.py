#!/usr/bin/env python3
"""
FaberLoom Agent Harness — Loop Mode

Orquesta un ticket/feature a través de 5 fases:
  SPEC -> PLAN -> DELEGAR/IMPLEMENTAR -> VERIFICAR -> REPORTAR

Routing de costo:
  ALTA (arquitectura, negocio critico, seguridad, integraciones nuevas)
    -> Fugu (codex exec -p fugu)
  BAJA (boilerplate, tests, CRUD, transformaciones, refactors mecanicos)
    -> delegable Tier 2 (GLM-5.2 o MiniMax M2.7)

El orchestrator puede correr en modo autonomo para tareas ALTA y generar
specs delegables listos para ejecutar sin ida y vuelta en tareas BAJA.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import textwrap
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from jinja2 import Environment
except ImportError:
    Environment = None

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / "harness" / "loop_state.json"
CONFIG_FILE = ROOT / "harness" / "loop_config.json"
PROMPTS_DIR = ROOT / "harness" / "prompts"
AGENTS_DIR = ROOT / "harness" / "agents"
REPORTS_DIR = ROOT / "harness" / "reports"
DELEGATED_DIR = ROOT / "harness" / "delegated"


# ---------------------------------------------------------------------------
# Configuracion por defecto
# ---------------------------------------------------------------------------
DEFAULT_CONFIG: dict[str, Any] = {
    "models": {
        # Modelos caros / arquitectura (ALTA)
        "fugu": {
            "provider": "codex",
            "profile": "fugu",
            "sandbox": "workspace-write",
            "bypass_approvals": True,
        },
        "claude": {
            "provider": "codex",
            "profile": "claude",
            "sandbox": "workspace-write",
            "bypass_approvals": True,
        },
        "claude_api": {
            "provider": "anthropic",
            "model": "claude-opus-4",
            "api_key_env": "ANTHROPIC_API_KEY",
            "api_url": "https://api.anthropic.com/v1/messages",
        },
        # Modelos baratos / volumen (BAJA)
        "kimi_k27_code": {
            "provider": "openrouter",
            "model": "moonshotai/kimi-k2-7-code",
            "api_key_env": "OPENROUTER_API_KEY",
            "api_url": "https://openrouter.ai/api/v1/chat/completions",
        },
        "kimi_direct": {
            "provider": "moonshot",
            "model": "kimi-k2-7-code",
            "api_key_env": "MOONSHOT_API_KEY",
            "api_url": "sk-kimi-KO84SlyRy5faTOaBvYPfm9kSjKw4sRkJ4BenN0UqhqVHbBD8b7hne4rqJCbUF54t",
        },
        "glm52": {
            "provider": "openrouter",
            "model": "z-ai/glm-5.2",
            "api_key_env": "OPENROUTER_API_KEY",
            "api_url": "https://openrouter.ai/api/v1/chat/completions",
        },
        "minimax27": {
            "provider": "openrouter",
            "model": "minimax/minimax-m2-7",
            "api_key_env": "OPENROUTER_API_KEY",
            "api_url": "https://openrouter.ai/api/v1/chat/completions",
        },
    },
    "default_high": "fugu",
    "default_low": "kimi_k27_code",
    "max_retries": 3,
    "auto_update_graphify": True,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------
@dataclass
class Task:
    id: str
    title: str
    classification: str  # ALTA | BAJA
    spec: str = ""
    files: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)
    verification_command: str = ""
    delegate_to: str = ""  # fugu | glm52 | minimax27
    status: str = "pending"  # pending | running | done | failed | delegated
    output_file: Path | None = None
    verification_output: str = ""
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "classification": self.classification,
            "spec": self.spec,
            "files": self.files,
            "success_criteria": self.success_criteria,
            "verification_command": self.verification_command,
            "delegate_to": self.delegate_to,
            "status": self.status,
            "output_file": str(self.output_file) if self.output_file else None,
            "verification_output": self.verification_output,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        task = cls(
            id=data["id"],
            title=data["title"],
            classification=data["classification"],
            spec=data.get("spec", ""),
            files=data.get("files", []),
            success_criteria=data.get("success_criteria", []),
            verification_command=data.get("verification_command", ""),
            delegate_to=data.get("delegate_to", ""),
            status=data.get("status", "pending"),
            notes=data.get("notes", ""),
        )
        if data.get("output_file"):
            task.output_file = Path(data["output_file"])
        return task


@dataclass
class LoopTicket:
    id: str
    title: str
    description: str
    problem: str = ""
    success_criteria: list[str] = field(default_factory=list)
    non_goals: list[str] = field(default_factory=list)
    pending_confirmations: list[str] = field(default_factory=list)
    plan_summary: str = ""
    tasks: list[Task] = field(default_factory=list)
    status: str = "pending"  # pending | spec | plan | implementing | verifying | reporting | done | blocked
    report_file: Path | None = None
    created_at: str = field(default_factory=lambda: utc_now())
    updated_at: str = field(default_factory=lambda: utc_now())

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "problem": self.problem,
            "success_criteria": self.success_criteria,
            "non_goals": self.non_goals,
            "pending_confirmations": self.pending_confirmations,
            "plan_summary": self.plan_summary,
            "tasks": [t.to_dict() for t in self.tasks],
            "status": self.status,
            "report_file": str(self.report_file) if self.report_file else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LoopTicket:
        ticket = cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            problem=data.get("problem", ""),
            success_criteria=data.get("success_criteria", []),
            non_goals=data.get("non_goals", []),
            pending_confirmations=data.get("pending_confirmations", []),
            plan_summary=data.get("plan_summary", ""),
            tasks=[Task.from_dict(t) for t in data.get("tasks", [])],
            status=data.get("status", "pending"),
            created_at=data.get("created_at", utc_now()),
            updated_at=data.get("updated_at", utc_now()),
        )
        if data.get("report_file"):
            ticket.report_file = Path(data["report_file"])
        return ticket


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def load_json(path: Path, default: dict | None = None) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default or {}


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_config() -> dict[str, Any]:
    config = dict(DEFAULT_CONFIG)
    config.update(load_json(CONFIG_FILE, {}))
    return config


def load_state() -> dict[str, Any]:
    return load_json(STATE_FILE, {"tickets": [], "active_ticket_id": None})


def save_state(state: dict[str, Any]) -> None:
    save_json(STATE_FILE, state)


def render_prompt(template_name: str, **kwargs) -> str:
    template_path = PROMPTS_DIR / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"Prompt template missing: {template_path}")
    template = template_path.read_text(encoding="utf-8")
    # Reemplazar placeholders [[KEY]] por valores. Los valores pueden contener
    # {{ sin que Jinja2 los interprete porque no usamos render Jinja2 en los
    # prompts de loop (evita conflictos con codigo de ejemplo).
    for key, value in kwargs.items():
        template = template.replace(f"[[{key}]]", str(value))
    return template


def slugify(value: str) -> str:
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", "-", value)


def run_codex(prompt: str, output_file: Path, model_config: dict[str, Any]) -> subprocess.CompletedProcess:
    """Ejecuta codex exec con el perfil y sandbox configurados."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "codex", "exec",
        "-p", model_config.get("profile", "fugu"),
        "--skip-git-repo-check",
        "--sandbox", model_config.get("sandbox", "workspace-write"),
        "-o", str(output_file),
        "-C", str(ROOT),
        "--color", "never",
    ]
    if model_config.get("bypass_approvals") and model_config.get("sandbox") == "workspace-write":
        cmd.append("--dangerously-bypass-approvals-and-sandbox")
    cmd.append("-")
    print(f"[loop] invoking codex exec -p {model_config.get('profile')} -> {output_file.name}")
    result = subprocess.run(
        cmd,
        input=prompt,
        text=True,
        encoding="utf-8",
        capture_output=True,
        cwd=ROOT,
        timeout=1800,
    )
    if not output_file.exists():
        fallback = output_file.parent / f"{output_file.stem}_ERROR.md"
        fallback.write_text(
            f"# Error en codex exec\n\nstdout:\n{result.stdout}\n\nstderr:\n{result.stderr}",
            encoding="utf-8",
        )
        raise RuntimeError(f"codex exec no genero {output_file}; stderr: {result.stderr[:500]}")
    return result


def run_api_provider(prompt: str, output_file: Path, model_config: dict[str, Any]) -> subprocess.CompletedProcess:
    """Ejecuta un provider de chat completions via curl (OpenRouter, Moonshot, Anthropic)."""
    api_key = model_config.get("api_key") or os.getenv(model_config.get("api_key_env"))
    if not api_key:
        raise RuntimeError(
            f"Falta API key para {model_config['model']}; set {model_config.get('api_key_env')}"
        )
    output_file.parent.mkdir(parents=True, exist_ok=True)

    provider = model_config.get("provider", "openrouter")
    if provider == "anthropic":
        body = {
            "model": model_config["model"],
            "max_tokens": 8192,
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = [
            "-H", "Content-Type: application/json",
            "-H", "anthropic-version: 2023-06-01",
            "-H", f"x-api-key: {api_key}",
        ]
    else:
        body = {
            "model": model_config["model"],
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = [
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {api_key}",
        ]
        if provider == "openrouter":
            headers.extend(["-H", "HTTP-Referer: https://faberloom.local", "-H", "X-Title: FaberLoom Harness"])

    result = subprocess.run(
        ["curl", "-s", "-X", "POST", model_config.get("api_url"), *headers, "-d", json.dumps(body)],
        capture_output=True,
        text=True,
        timeout=300,
    )
    output_file.write_text(result.stdout, encoding="utf-8")
    return result


def apply_file_blocks(text: str, base: Path = ROOT) -> list[str]:
    """Escribe en disco los bloques de codigo encontrados. Devuelve lista de rutas."""
    pattern = re.compile(
        r"```(?:\w+)?(?::|\s+)([^\n`]+?)\n(.*?)```",
        re.DOTALL | re.IGNORECASE,
    )
    valid_path = re.compile(r"^[\w./\\\-]+\.[\w]+$|^pyproject\.toml$|^requirements\.txt$")
    written = []
    for m in pattern.finditer(text):
        path = m.group(1).strip()
        if not valid_path.match(path):
            continue
        if any(bad in path for bad in ["->", "<-", "http", "GET ", "POST ", "PUT ", "DELETE ", "  "]):
            continue
        target = base / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(m.group(2).rstrip() + "\n", encoding="utf-8")
        written.append(str(target.relative_to(ROOT)))
        print(f"[loop] wrote {target.relative_to(ROOT)}")
    return written


def update_graphify() -> None:
    print("[loop] updating graphify knowledge graph...")
    result = subprocess.run(
        ["graphify", "update", ".", "--force"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=600,
    )
    if result.returncode != 0:
        print("[loop] graphify warning:", result.stderr[:500])
    else:
        print("[loop] graphify updated")


# ---------------------------------------------------------------------------
# Model Router
# ---------------------------------------------------------------------------
class ModelRouter:
    def __init__(self, config: dict[str, Any]):
        self.config = config

    def _model_config(self, model_key: str) -> dict[str, Any]:
        models = self.config.get("models", {})
        if model_key not in models:
            available = ", ".join(models.keys())
            raise RuntimeError(f"Modelo '{model_key}' no configurado. Disponibles: {available}")
        return models[model_key]

    def run(self, prompt: str, output_file: Path, model_key: str) -> subprocess.CompletedProcess | Path:
        """
        Ejecuta un prompt contra el modelo indicado. Los providers soportados son:
        - codex: codex exec -p <profile> (Fugu, Claude, etc.)
        - openrouter: via API (Kimi K2.7, GLM-5.2, MiniMax M2.7)
        - moonshot: API directa de Moonshot (Kimi)
        - anthropic: API directa de Anthropic (Claude)
        """
        model_cfg = self._model_config(model_key)
        provider = model_cfg.get("provider", "codex")

        if provider == "codex":
            return run_codex(prompt, output_file, model_cfg)

        if provider in ("openrouter", "moonshot", "anthropic"):
            return run_api_provider(prompt, output_file, model_cfg)

        raise RuntimeError(f"Provider no soportado: {provider}")

    def run_task(self, task: Task, ticket: LoopTicket, output_file: Path, model_key: str) -> Path:
        """
        Ejecuta una tarea contra el modelo indicado. Si el modelo no tiene API key
        disponible, genera un spec delegable en harness/delegated/.
        """
        prompt = self._task_prompt(task, ticket)
        model_cfg = self._model_config(model_key)
        provider = model_cfg.get("provider", "codex")

        # Codex siempre puede ejecutar si el binario y perfil existen.
        if provider == "codex":
            self.run(prompt, output_file, model_key)
            task.output_file = output_file
            task.status = "done"
            return output_file

        # Providers de API requieren key; si falta, delegar a archivo.
        api_key = model_cfg.get("api_key") or os.getenv(model_cfg.get("api_key_env", ""))
        if api_key:
            self.run(prompt, output_file, model_key)
            task.output_file = output_file
            task.status = "done"
            return output_file

        print(f"[loop] {model_key} no tiene API key; delegando a archivo")
        DELEGATED_DIR.mkdir(parents=True, exist_ok=True)
        delegated_file = DELEGATED_DIR / f"{task.id}_{slugify(task.title)}.md"
        delegated_file.write_text(prompt, encoding="utf-8")
        task.output_file = delegated_file
        task.status = "delegated"
        print(f"[loop] delegated task {task.id} -> {delegated_file.relative_to(ROOT)}")
        return delegated_file

    def _task_prompt(self, task: Task, ticket: LoopTicket) -> str:
        template = "loop_high.md" if task.classification == "ALTA" else "loop_low.md"
        return render_prompt(
            template,
            TICKET_ID=ticket.id,
            TICKET_TITLE=ticket.title,
            TICKET_DESCRIPTION=ticket.description,
            TICKET_SUCCESS_CRITERIA="\n".join(f"- {s}" for s in ticket.success_criteria),
            TASK_ID=task.id,
            TASK_TITLE=task.title,
            TASK_SPEC=task.spec,
            TASK_FILES="\n".join(f"- {f}" for f in task.files),
            TASK_SUCCESS_CRITERIA="\n".join(f"- {s}" for s in task.success_criteria),
            TASK_VERIFICATION=task.verification_command,
            ROOT=str(ROOT),
        )

    def run_high(self, prompt: str, output_file: Path) -> subprocess.CompletedProcess:
        """Backward-compatible: ejecuta prompt con el modelo default ALTA."""
        return self.run(prompt, output_file, self.config.get("default_high", "fugu"))

    def run_low(self, task: Task, ticket: LoopTicket, output_file: Path) -> Path:
        """Backward-compatible: ejecuta tarea BAJA con el modelo default BAJA."""
        model_key = task.delegate_to or self.config.get("default_low", "kimi_k27_code")
        return self.run_task(task, ticket, output_file, model_key)


# ---------------------------------------------------------------------------
# Loop Orchestrator
# ---------------------------------------------------------------------------
class LoopOrchestrator:
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or load_config()
        self.router = ModelRouter(self.config)
        self.state = load_state()

    def save(self) -> None:
        save_state(self.state)

    def find_ticket(self, ticket_id: str) -> LoopTicket | None:
        for t in self.state.get("tickets", []):
            if t.get("id") == ticket_id:
                return LoopTicket.from_dict(t)
        return None

    def store_ticket(self, ticket: LoopTicket) -> None:
        ticket.updated_at = utc_now()
        tickets = self.state.setdefault("tickets", [])
        for i, t in enumerate(tickets):
            if t["id"] == ticket.id:
                tickets[i] = ticket.to_dict()
                break
        else:
            tickets.append(ticket.to_dict())
        self.state["active_ticket_id"] = ticket.id
        self.save()

    # -----------------------------------------------------------------------
    # FASE 1: SPEC
    # -----------------------------------------------------------------------
    def run_spec(self, ticket: LoopTicket) -> None:
        print(f"\n[loop] === SPEC: {ticket.title} ===")
        ticket.status = "spec"
        output = REPORTS_DIR / f"{ticket.id}_spec.md"
        prompt = render_prompt(
            "loop_spec.md",
            TICKET_ID=ticket.id,
            TICKET_TITLE=ticket.title,
            TICKET_DESCRIPTION=ticket.description,
            ROOT=str(ROOT),
        )
        self.router.run_high(prompt, output)
        spec_text = output.read_text(encoding="utf-8")

        # Parseo pragmatico del output de Fugu.
        ticket.problem = self._extract_section(spec_text, "problema", "problem") or ticket.description
        ticket.success_criteria = self._extract_list(spec_text, "criterio de exito", "success criteria")
        ticket.non_goals = self._extract_list(spec_text, "non-goals", "non goals")
        ticket.pending_confirmations = self._extract_pending(spec_text)

        self.store_ticket(ticket)
        print(f"[loop] spec saved -> {output.relative_to(ROOT)}")

    # -----------------------------------------------------------------------
    # FASE 2: PLAN
    # -----------------------------------------------------------------------
    def run_plan(self, ticket: LoopTicket) -> None:
        print(f"\n[loop] === PLAN: {ticket.title} ===")
        ticket.status = "plan"
        output = REPORTS_DIR / f"{ticket.id}_plan.md"
        prompt = render_prompt(
            "loop_plan.md",
            TICKET_ID=ticket.id,
            TICKET_TITLE=ticket.title,
            TICKET_DESCRIPTION=ticket.description,
            TICKET_PROBLEM=ticket.problem,
            TICKET_SUCCESS_CRITERIA="\n".join(f"- {s}" for s in ticket.success_criteria),
            TICKET_NON_GOALS="\n".join(f"- {s}" for s in ticket.non_goals),
            PENDING_CONFIRMATIONS="\n".join(f"- {p}" for p in ticket.pending_confirmations),
            ROOT=str(ROOT),
        )
        self.router.run_high(prompt, output)
        plan_text = output.read_text(encoding="utf-8")
        ticket.plan_summary = self._extract_section(plan_text, "resumen", "summary") or plan_text[:500]
        ticket.tasks = self._parse_tasks(plan_text, ticket)
        self.store_ticket(ticket)
        print(f"[loop] plan saved -> {output.relative_to(ROOT)}")
        print(f"[loop] {len(ticket.tasks)} tasks parsed ({sum(1 for t in ticket.tasks if t.classification == 'ALTA')} ALTA, {sum(1 for t in ticket.tasks if t.classification == 'BAJA')} BAJA)")

    # -----------------------------------------------------------------------
    # FASE 3: DELEGAR / IMPLEMENTAR
    # -----------------------------------------------------------------------
    def run_implement(self, ticket: LoopTicket) -> None:
        print(f"\n[loop] === IMPLEMENT: {ticket.title} ===")
        ticket.status = "implementing"
        self.store_ticket(ticket)

        for task in ticket.tasks:
            if task.status in ("done", "delegated"):
                continue

            # El plan puede forzar un modelo especifico; si no, usa default por class.
            default_model = (
                self.config.get("default_high", "fugu")
                if task.classification == "ALTA"
                else self.config.get("default_low", "kimi_k27_code")
            )
            model_key = task.delegate_to or default_model

            print(f"[loop] running {task.classification} task {task.id}: {task.title} -> {model_key}")
            output = AGENTS_DIR / f"{ticket.id}_{task.id}_{model_key}.md"
            self.router.run_task(task, ticket, output, model_key)

            # Si fue ejecutado (no delegado), aplicar bloques de codigo devueltos.
            if task.status == "done" and task.output_file and task.output_file.exists():
                written = apply_file_blocks(task.output_file.read_text(encoding="utf-8"))
                if written:
                    print(f"[loop] applied {len(written)} file blocks")

            self.store_ticket(ticket)

    # -----------------------------------------------------------------------
    # FASE 4: VERIFICAR
    # -----------------------------------------------------------------------
    def run_verify(self, ticket: LoopTicket) -> None:
        print(f"\n[loop] === VERIFY: {ticket.title} ===")
        ticket.status = "verifying"
        output = REPORTS_DIR / f"{ticket.id}_verify.md"

        tasks_context = ""
        for task in ticket.tasks:
            task_file = task.output_file.read_text(encoding="utf-8")[:1500] if task.output_file and task.output_file.exists() else ""
            tasks_context += f"\n## {task.id} ({task.classification})\n{task_file}\n"

        prompt = render_prompt(
            "loop_verify.md",
            TICKET_ID=ticket.id,
            TICKET_TITLE=ticket.title,
            TICKET_SUCCESS_CRITERIA="\n".join(f"- {s}" for s in ticket.success_criteria),
            TASKS_CONTEXT=tasks_context,
            ROOT=str(ROOT),
        )
        self.router.run_high(prompt, output)
        verify_text = output.read_text(encoding="utf-8")

        # Actualiza estado de tareas segun verificacion (parseo pragmatico).
        for task in ticket.tasks:
            if f"[{task.id}]" in verify_text or task.id in verify_text:
                if "FAIL" in verify_text or "bloqueador" in verify_text.lower():
                    if task.classification == "ALTA":
                        task.status = "failed"
                else:
                    task.status = "done"

        self.store_ticket(ticket)
        print(f"[loop] verify saved -> {output.relative_to(ROOT)}")

    # -----------------------------------------------------------------------
    # FASE 5: REPORTAR
    # -----------------------------------------------------------------------
    def run_report(self, ticket: LoopTicket) -> None:
        print(f"\n[loop] === REPORT: {ticket.title} ===")
        ticket.status = "reporting"
        output = REPORTS_DIR / f"{ticket.id}_report.md"

        tasks_table = "| Tarea | Clase | Estado | Notas |\n|---|---|---|---|\n"
        for task in ticket.tasks:
            notes = task.notes or ""
            if task.classification == "BAJA" and task.status == "delegated":
                notes = f"delegado a {task.output_file}"
            tasks_table += f"| {task.title} | {task.classification} | {task.status} | {notes} |\n"

        pending = "\n".join(f"- {p}" for p in ticket.pending_confirmations)
        prompt = render_prompt(
            "loop_report.md",
            TICKET_ID=ticket.id,
            TICKET_TITLE=ticket.title,
            TICKET_SUCCESS_CRITERIA="\n".join(f"- {s}" for s in ticket.success_criteria),
            TASKS_TABLE=tasks_table,
            PENDING_CONFIRMATIONS=pending,
            ROOT=str(ROOT),
        )
        self.router.run_high(prompt, output)
        ticket.report_file = output
        ticket.status = "done"
        self.store_ticket(ticket)
        print(f"[loop] report saved -> {output.relative_to(ROOT)}")

    # -----------------------------------------------------------------------
    # Loop completo
    # -----------------------------------------------------------------------
    def run_loop(self, ticket: LoopTicket) -> LoopTicket:
        if ticket.status in ("pending", "spec"):
            self.run_spec(ticket)
        if ticket.status == "plan" or (ticket.status == "spec" and not ticket.pending_confirmations):
            self.run_plan(ticket)
        if ticket.status == "implementing" or ticket.status == "plan":
            self.run_implement(ticket)
        if ticket.status == "verifying" or ticket.status == "implementing":
            self.run_verify(ticket)
        if ticket.status == "reporting" or ticket.status == "verifying":
            self.run_report(ticket)
        if self.config.get("auto_update_graphify"):
            update_graphify()
        return ticket

    # -----------------------------------------------------------------------
    # Helpers de parseo pragmatico
    # -----------------------------------------------------------------------
    def _extract_section(self, text: str, *headers: str) -> str:
        for header in headers:
            for line in text.splitlines():
                if line.lower().startswith(f"## {header}") or line.lower().startswith(f"**{header}"):
                    idx = text.find(line)
                    if idx >= 0:
                        block = text[idx + len(line):]
                        next_header = re.search(r"\n## ", block)
                        end = next_header.start() if next_header else len(block)
                        return block[:end].strip()
        return ""

    def _extract_list(self, text: str, *headers: str) -> list[str]:
        section = self._extract_section(text, *headers)
        if not section:
            return []
        items = []
        for line in section.splitlines():
            line = line.strip()
            if line.startswith("-") or line.startswith("*") or re.match(r"^\d+\.", line):
                items.append(re.sub(r"^[-*\d.\s]+", "", line).strip())
        return items

    def _extract_pending(self, text: str) -> list[str]:
        pending = []
        for line in text.splitlines():
            if "[PENDIENTE - CONFIRMAR]" in line:
                pending.append(line.strip())
        return pending

    def _parse_tasks(self, text: str, ticket: LoopTicket) -> list[Task]:
        tasks: list[Task] = []
        current_task: Task | None = None
        current_section: str | None = None
        task_counter = 1

        def _norm(text: str) -> str:
            return (
                text.lower()
                .replace("*", "")
                .replace(":", "")
                .strip()
                .translate(str.maketrans("áéíóúÁÉÍÓÚ", "aeiouAEIOU"))
            )

        for raw_line in text.splitlines():
            line = raw_line.rstrip("\n")
            line_stripped = line.strip()

            if not line_stripped:
                continue

            # Inicio de tarea: "### T1 - ALTA - Titulo" o "1. **ALTA** Titulo"
            m = re.match(
                r"^(?:#{1,3}\s+)?([A-Z]?\d+)?\s*[\-\.]?\s*\*?\*?(ALTA|BAJA)\*?\*?\s*[\-\:]?\s*(.+)$",
                line_stripped,
                re.IGNORECASE,
            )
            if m:
                if current_task:
                    tasks.append(current_task)
                task_id = m.group(1) or f"T{task_counter}"
                title = m.group(3).strip("*:- ")
                current_task = Task(
                    id=task_id,
                    title=title,
                    classification=m.group(2).upper(),
                )
                task_counter += 1
                current_section = None
                continue

            if current_task is None:
                continue

            header = _norm(line_stripped)

            # Spec / Espec
            if header.startswith("spec") or header.startswith("espec"):
                current_section = "spec"
                val = re.sub(r"(?i)^\*?\*?(spec|espec)\*?\*?\s*[:\-]?\s*", "", line_stripped).strip()
                if val:
                    current_task.spec += val + "\n"
                continue

            # Archivos / Files
            if header.startswith("archivos") or header.startswith("files"):
                current_section = "files"
                continue

            # Criterio de exito / Success criteria
            if header.startswith("criterio") or header.startswith("success criteria"):
                current_section = "criteria"
                continue

            # Verificacion / Verification
            if header.startswith("verificacion") or header.startswith("verification"):
                current_section = "verification"
                val = re.sub(r"(?i)^\*?\*?(verificaci[oó]n|verification)\*?\*?\s*[:\-]?\s*", "", line_stripped).strip()
                if val:
                    current_task.verification_command += val + "\n"
                continue

            # Delegar a / Delegate to
            if header.startswith("delegar") or header.startswith("delegate"):
                current_section = "delegate"
                m = re.search(r"(?i)delegar\s*a?\s*[:\-]\s*\*?\*?\s*(.+)", line_stripped)
                if not m:
                    m = re.search(r"(?i)delegate\s*to?\s*[:\-]\s*\*?\*?\s*(.+)", line_stripped)
                if m:
                    current_task.delegate_to = m.group(1).strip().strip("*").lower()
                continue

            # Contenido de seccion
            if current_section == "spec":
                current_task.spec += line + "\n"
            elif current_section == "files" and line_stripped.startswith(("-", "*")):
                current_task.files.append(re.sub(r"^[-*\s]+", "", line_stripped))
            elif current_section == "criteria" and (
                line_stripped.startswith(("-", "*")) or re.match(r"^\d+\.", line_stripped)
            ):
                current_task.success_criteria.append(re.sub(r"^[-*\d.\s]+", "", line_stripped))
            elif current_section == "verification":
                current_task.verification_command += line + "\n"
            elif current_section == "delegate":
                current_task.delegate_to = line_stripped.lower()

        if current_task:
            tasks.append(current_task)

        # Defaults y limpieza
        for task in tasks:
            task.spec = task.spec.strip()
            task.verification_command = task.verification_command.strip()
            if not task.delegate_to:
                task.delegate_to = "kimi_k27_code" if task.classification == "BAJA" else "fugu"

        return tasks


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def create_ticket_from_args(args: argparse.Namespace) -> LoopTicket:
    ticket_id = args.id or f"loop_{slugify(args.title)}_{utc_now()[:10]}"
    return LoopTicket(
        id=ticket_id,
        title=args.title,
        description=args.description or "",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="FaberLoom Loop Harness")
    sub = parser.add_subparsers(dest="command")

    run_parser = sub.add_parser("run", help="Ejecutar un loop completo para un ticket")
    run_parser.add_argument("--title", required=True, help="Titulo del ticket")
    run_parser.add_argument("--description", required=True, help="Descripcion del problema/ticket")
    run_parser.add_argument("--id", help="ID opcional del ticket")

    resume_parser = sub.add_parser("resume", help="Reanudar el ticket activo o uno especifico")
    resume_parser.add_argument("--id", help="ID del ticket a reanudar")

    init_parser = sub.add_parser("init-config", help="Crear loop_config.json por defecto")

    args = parser.parse_args(argv)

    if args.command == "init-config":
        save_json(CONFIG_FILE, DEFAULT_CONFIG)
        print(f"[loop] config created -> {CONFIG_FILE.relative_to(ROOT)}")
        return 0

    orchestrator = LoopOrchestrator()

    if args.command == "run":
        ticket = create_ticket_from_args(args)
        orchestrator.store_ticket(ticket)
        orchestrator.run_loop(ticket)
        print(f"\n[loop] done. Report: {ticket.report_file}")
        return 0

    if args.command == "resume":
        ticket_id = args.id or orchestrator.state.get("active_ticket_id")
        if not ticket_id:
            print("[loop] error: no active ticket. Use --id or run a new ticket.")
            return 1
        ticket = orchestrator.find_ticket(ticket_id)
        if not ticket:
            print(f"[loop] error: ticket {ticket_id} not found")
            return 1
        orchestrator.run_loop(ticket)
        print(f"\n[loop] done. Report: {ticket.report_file}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
