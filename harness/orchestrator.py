#!/usr/bin/env python3
"""
FaberLoom Agent Harness — Fully Autonomous
Orquesta agentes senior, auditor y evaluador vía Codex CLI (perfil fugu)
y mantiene un knowledge graph con graphify.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import textwrap
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    Environment = None

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / "harness" / "state.json"
PROMPTS_DIR = ROOT / "harness" / "prompts"
AGENTS_DIR = ROOT / "harness" / "agents"
REPORTS_DIR = ROOT / "harness" / "reports"
PLAN_FILE = ROOT / "Plan" / "PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md"


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {
        "current_phase": "SL0",
        "iteration": 0,
        "max_iterations": 3,
        "status": "in_progress",
        "completed_phases": [],
        "next_phase": "SL1a",
        "history": [],
    }


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def read_plan() -> str:
    return PLAN_FILE.read_text(encoding="utf-8")


def read_design_system() -> str:
    """Recopila un resumen canon de la marca desde @Diseños."""
    parts = []
    brand_md = ROOT / "Diseños" / "FABERLOOM_BRAND.md"
    if brand_md.exists():
        parts.append("# Brand\n\n" + brand_md.read_text(encoding="utf-8"))
    typ_md = ROOT / "Diseños" / "FaberLoom Typography.dc.html"
    if typ_md.exists():
        parts.append("# Typography\n\n" + typ_md.read_text(encoding="utf-8")[:4000])
    icon_md = ROOT / "Diseños" / "FaberLoom Iconography.dc.html"
    if icon_md.exists():
        parts.append("# Iconography\n\n" + icon_md.read_text(encoding="utf-8")[:4000])
    return "\n\n---\n\n".join(parts)


def render_prompt(template_name: str, **kwargs) -> str:
    template = (PROMPTS_DIR / template_name).read_text(encoding="utf-8")
    # 1) Renderizar lógica Jinja2 (if/for) sin pasar PLAN/DESIGN/ROOT para evitar conflictos
    jinja_kwargs = {k: v for k, v in kwargs.items() if k not in ("PLAN", "DESIGN", "ROOT")}
    if Environment is not None:
        env = Environment(autoescape=False)
        template = env.from_string(template).render(**jinja_kwargs)
    # 2) Insertar bloques grandes que podrían contener {{ via placeholders [[KEY]]
    for key in ("PLAN", "DESIGN", "ROOT"):
        value = kwargs.get(key, "")
        template = template.replace(f"[[{key}]]", str(value))
    return template


def run_codex(prompt: str, output_file: Path, sandbox: str = "workspace-write", bypass: bool = True) -> subprocess.CompletedProcess:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "codex", "exec", "-p", "fugu",
        "--skip-git-repo-check",
        "--sandbox", sandbox,
        "-o", str(output_file),
        "-C", str(ROOT),
        "--color", "never",
    ]
    if bypass and sandbox == "workspace-write":
        # Autonomous mode: the senior agent must be able to write files.
        cmd.append("--dangerously-bypass-approvals-and-sandbox")
    cmd.append("-")
    print(f"[harness] invoking codex exec -> {output_file.name}")
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
        # codex exec no generó el archivo (timeout/error interno)
        fallback = output_file.parent / f"{output_file.stem}_ERROR.md"
        fallback.write_text(
            f"# Error en codex exec\n\nstdout:\n{result.stdout}\n\nstderr:\n{result.stderr}",
            encoding="utf-8",
        )
        raise RuntimeError(
            f"codex exec no generó {output_file}; stderr: {result.stderr[:500]}"
        )
    return result


def extract_file_blocks(text: str) -> list[tuple[str, str]]:
    """
    Parsea bloques de código con anotación de ruta.
    Soporta:
      ```python:app/main.py
      ```app/main.py
      ```:app/main.py
    Rechaza paths con espacios, flechas u otros caracteres no válidos.
    """
    pattern = re.compile(
        r"```(?:\w+)?(?::|\s+)([^\n`]+?)\n(.*?)```",
        re.DOTALL | re.IGNORECASE,
    )
    valid_path = re.compile(r"^[\w./\\\-]+\.[\w]+$|^pyproject\.toml$|^requirements\.txt$")
    result = []
    for m in pattern.finditer(text):
        path = m.group(1).strip()
        # Si el path parece código/ejemplo y no una ruta, descartarlo
        if not valid_path.match(path):
            continue
        if any(bad in path for bad in ["→", "<-", "http", "GET ", "POST ", "PUT ", "DELETE ", "  "]):
            continue
        result.append((path, m.group(2)))
    return result


def apply_file_blocks(text: str, base: Path = ROOT) -> list[str]:
    """Escribe en disco los bloques de código encontrados. Devuelve lista de rutas."""
    written = []
    for rel_path, content in extract_file_blocks(text):
        target = base / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content.rstrip() + "\n", encoding="utf-8")
        written.append(str(target.relative_to(ROOT)))
        print(f"[harness] wrote {target.relative_to(ROOT)}")
    return written


def update_graphify() -> None:
    print("[harness] updating graphify knowledge graph...")
    result = subprocess.run(
        ["graphify", "update", ".", "--force"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=600,
    )
    if result.returncode != 0:
        print("[harness] graphify warning:", result.stderr[:500])
    else:
        print("[harness] graphify updated")


def run_senior(role: str, phase: str, iteration: int) -> Path:
    output = AGENTS_DIR / f"{phase}_{role}_iter{iteration}.md"
    plan = read_plan()
    design = read_design_system()
    prompt = render_prompt(
        f"senior_{role}.md",
        PHASE=phase,
        ITERATION=str(iteration),
        PLAN=plan,
        DESIGN=design,
        ROOT=str(ROOT),
    )
    result = run_codex(prompt, output)
    if result.returncode != 0:
        print(f"[harness] codex error for {role}:", result.stderr[:1000])
    # Aplica los bloques de código que el agente haya devuelto
    written = apply_file_blocks(output.read_text(encoding="utf-8"))
    return output, written


def summarize(path: Path, max_chars: int = 2000) -> str:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    return text[:max_chars] + ("\n... [truncado]" if len(text) > max_chars else "")


def run_auditor(phase: str, iteration: int, agent_outputs: list[Path], written_files: list[str]) -> Path:
    output = REPORTS_DIR / f"{phase}_audit_iter{iteration}.md"
    plan = read_plan()
    design = read_design_system()
    context = ""
    for p in agent_outputs:
        if p.exists():
            context += f"\n\n## Output: {p.name}\n\n" + summarize(p, 1500)
    files_list = "\n".join(f"- {w}" for w in written_files)
    prompt = render_prompt(
        "auditor.md",
        PHASE=phase,
        ITERATION=str(iteration),
        PLAN=plan,
        DESIGN=design,
        AGENT_OUTPUTS=context,
        WRITTEN_FILES=files_list,
    )
    run_codex(prompt, output, sandbox="read-only", bypass=False)
    return output


def run_evaluator(phase: str, iteration: int, audit: Path, agent_outputs: list[Path], written_files: list[str]) -> Path:
    output = REPORTS_DIR / f"{phase}_eval_iter{iteration}.md"
    plan = read_plan()
    design = read_design_system()
    context = ""
    for p in agent_outputs:
        if p.exists():
            context += f"\n\n## Output: {p.name}\n\n" + summarize(p, 1500)
    audit_text = summarize(audit, 2000)
    files_list = "\n".join(f"- {w}" for w in written_files)
    prompt = render_prompt(
        "evaluator.md",
        PHASE=phase,
        ITERATION=str(iteration),
        PLAN=plan,
        DESIGN=design,
        AGENT_OUTPUTS=context,
        AUDIT=audit_text,
        WRITTEN_FILES=files_list,
    )
    run_codex(prompt, output, sandbox="read-only", bypass=False)
    return output


def decide_next_step(eval_path: Path) -> str:
    """
    Heurística simple: si el evaluador incluye [APROBADO] o 'visto bueno', avanzamos.
    De lo contrario, iteramos hasta max_iterations.
    """
    if not eval_path.exists():
        print(f"[harness] evaluator output missing ({eval_path}); forcing iterate")
        return "iterate"
    text = eval_path.read_text(encoding="utf-8").lower()
    if "[aprobado]" in text or "visto bueno" in text or "listo para avanzar" in text:
        return "advance"
    return "iterate"


def phase_spec(phase: str) -> dict:
    specs = {
        "SL0": {
            "roles": ["backend", "frontend", "brand"],
            "next": "SL1a",
        },
        "SL1a": {
            "roles": ["backend", "frontend"],
            "next": "SL1b",
        },
        "SL1b": {
            "roles": ["backend", "frontend"],
            "next": "SL2",
        },
    }
    return specs.get(phase, {"roles": ["backend", "frontend"], "next": None})


def run_phase(state: dict) -> dict:
    phase = state["current_phase"]
    iteration = state["iteration"] + 1
    state["iteration"] = iteration
    spec = phase_spec(phase)
    print(f"\n{'='*60}")
    print(f"[harness] Running {phase} — iteration {iteration}")
    print(f"{'='*60}")

    agent_outputs = []
    all_written: list[str] = []
    for role in spec["roles"]:
        out, written = run_senior(role, phase, iteration)
        agent_outputs.append(out)
        all_written.extend(written)
        state["history"].append({
            "phase": phase,
            "iteration": iteration,
            "role": role,
            "output": str(out.relative_to(ROOT)),
            "written": written,
        })

    update_graphify()

    audit = run_auditor(phase, iteration, agent_outputs, all_written)
    eval_path = run_evaluator(phase, iteration, audit, agent_outputs, all_written)

    decision = decide_next_step(eval_path)
    print(f"[harness] evaluator decision: {decision}")

    if decision == "advance":
        state["completed_phases"].append(phase)
        state["current_phase"] = spec["next"] or phase
        state["iteration"] = 0
        state["status"] = "in_progress"
    elif iteration >= state["max_iterations"]:
        print(f"[harness] max iterations reached for {phase}; stopping for human review")
        state["status"] = "needs_review"
    else:
        state["status"] = "in_progress"

    save_state(state)
    return state


def main() -> int:
    state = load_state()
    print("[harness] FaberLoom autonomous harness started")
    print(f"[harness] current phase: {state['current_phase']}, iteration: {state['iteration']}")

    while state["status"] == "in_progress":
        state = run_phase(state)
        if state["status"] == "needs_review":
            print("[harness] stopping for human review")
            break
        if state["current_phase"] is None:
            state["status"] = "completed"
            save_state(state)
            print("[harness] all planned phases completed")
            break

    return 0


if __name__ == "__main__":
    sys.exit(main())
