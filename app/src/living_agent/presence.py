"""E4-4 — Presencia única del Agente Vivo.

El chat general del tenant (workspace `ws-general`) responde:
- nivel general: solo desde índices (`workspace_brief` INDEX) + memoria personal aprobada;
- profundización: deriva al workspace concreto usando la autoridad del usuario que
  pregunta (key broker / RLS), sin elevar privilegios.
"""

from __future__ import annotations

import json
import re
from typing import Any, Literal

from ..context import SYSTEM_WORKSPACE_ID, Context, system_context
from ..db import system_get_workspace_by_slug, system_list_workspaces
from ..db_adapter import transaction
from ..draft_engine import _build_evidence_pack
from ..entity_identity import get_identity
from ..key_broker import KeyLevel, resolve_read_level
from .briefs import get_workspace_brief
from .constants import DEFAULT_AGENT_DISPLAY_NAME
from .memory import build_memory_context


PresenceIntent = Literal["general", "deepdive", "task", "chat"]

# Heurísticos simples y deterministas; no usan LLM para no inventar ni gastar.
_DEEPDIVE_HINTS = (
    "muestrame",
    "muéstrame",
    "detalle",
    "profundiza",
    "entra a",
    "workspace",
    "espacio",
    "factura #",
    "invoice #",
)
_TASK_HINTS = (
    "tarea",
    "automatiza",
    "programa",
    "cada día",
    "avisame",
    "avísame",
    "cuando llegue",
)
_GENERAL_HINTS = (
    "qué hay",
    "que hay",
    "resumen",
    "overview",
    "situación",
    "estado",
    "cuántos",
    "cuantos",
    "qué tengo",
    "que tengo",
    "qué facturas",
    "que facturas",
    "facturas tengo",
)

_WS_REFERENCE_RE = re.compile(
    r'(?:workspace|espacio|ws)[\s#-]*([a-z0-9_-]+)',
    re.IGNORECASE,
)


def classify_intent(query: str) -> PresenceIntent:
    """Clasifica la intención del mensaje sin llamar a un modelo."""

    lowered = query.lower().strip()
    if not lowered:
        return "chat"

    # General first: "qué hay", "qué tengo", "qué facturas tengo".
    for hint in _GENERAL_HINTS:
        if hint in lowered:
            return "general"

    for hint in _TASK_HINTS:
        if hint in lowered:
            return "task"

    for hint in _DEEPDIVE_HINTS:
        if hint in lowered:
            return "deepdive"

    # Saludos / conversación simple.
    first = lowered.split()[0]
    if first in {"hola", "hi", "hello", "buenas"}:
        return "chat"

    return "general"


def _user_roles(ctx: Context) -> set[str]:
    return {ctx.actor_role_at_decision} if ctx.actor_role_at_decision else set()


def _display_name_for_agent(conn: Any, tenant_id: str) -> str:
    identity = get_identity(conn, tenant_id)
    if identity is not None and identity.name:
        return identity.name
    return DEFAULT_AGENT_DISPLAY_NAME


def gather_index_context(
    ctx: Context,
    conn: Any,
    query: str = "",
) -> dict[str, Any]:
    """Recolecta solo información INDEX de los workspaces visibles al usuario.

    Retorna un dict con:
      - display_name: nombre del agente.
      - workspaces: lista de resúmenes INDEX por workspace.
      - memory_context: bloques personales aprobados (E4-5).
      - audit_sources: metadata para el audit trail.
    """

    tenant_id = ctx.require_tenant()
    user_roles = _user_roles(ctx)

    # El listado de workspaces es system-scoped pero filtrado por tenant.
    list_ctx = system_context(tenant_id=tenant_id)
    all_workspaces = system_list_workspaces(list_ctx, conn)

    workspace_summaries = []
    audit_sources = []
    for ws in all_workspaces:
        ws_id = ws["id"]
        if ws.get("kind") == "tenant_general":
            continue

        level, sealed = resolve_read_level(
            conn,
            tenant_id=tenant_id,
            space_id=ws_id,
            user_roles=user_roles,
            default=KeyLevel.CONTENT,
        )

        brief_row = get_workspace_brief(conn, ctx, ws_id)
        brief = brief_row.get("brief") or {} if brief_row else {}

        if level == KeyLevel.CLOSED:
            summary = {
                "workspace_id": ws_id,
                "name": ws["name"],
                "slug": ws["slug"],
                "level": "closed",
                "sealed": True,
                "object_count": sum((brief_row.get("source_counts") or {}).values())
                if brief_row
                else 0,
            }
        else:
            summary = {
                "workspace_id": ws_id,
                "name": ws["name"],
                "slug": ws["slug"],
                "level": level.value,
                "sealed": sealed,
                "source_counts": brief.get("source_counts", {}),
                "recent_titles": brief.get("recent_titles", []),
                "active_routines": brief.get("active_routines", []),
                "open_invoices": brief.get("open_invoices")
                if level == KeyLevel.CONTENT
                else None,
            }

        workspace_summaries.append(summary)
        audit_sources.append(
            {
                "workspace_id": ws_id,
                "level": level.value,
                "sealed": sealed,
            }
        )

    memory_context = build_memory_context(ctx, conn, query=query)

    return {
        "display_name": _display_name_for_agent(conn, tenant_id),
        "workspaces": workspace_summaries,
        "memory_context": memory_context,
        "audit_sources": audit_sources,
    }


def _tenant_context_is_empty(context: dict[str, Any]) -> bool:
    """True when the tenant has no indexed sources and no personal memory yet."""

    if context.get("memory_context"):
        return False
    workspaces = context.get("workspaces") or []
    return not any(
        sum((ws.get("source_counts") or {}).values()) > 0 for ws in workspaces
    )


def _format_index_answer(context: dict[str, Any]) -> str:
    """Genera una respuesta en lenguaje natural a partir del contexto INDEX."""

    lines = []
    display_name = context.get("display_name") or DEFAULT_AGENT_DISPLAY_NAME
    workspaces = context.get("workspaces") or []

    if not workspaces or _tenant_context_is_empty(context):
        return (
            f"Hola, soy {display_name}. Puedo ayudarte a conectar tu correo, "
            "subir archivos a Knowledge, o invocar skills. ¿Qué querés hacer?"
        )

    lines.append(f"Aquí está el panorama que veo ({len(workspaces)} workspace(s)):")
    for ws in workspaces:
        if ws.get("level") == "closed":
            lines.append(
                f"- **{ws['name']}**: espacio sellado ({ws.get('object_count', 0)} objetos)."
            )
            continue

        counts = ws.get("source_counts") or {}
        total = sum(counts.values())
        titles = ws.get("recent_titles") or []
        title_text = ", ".join(t["title"] for t in titles[:3] if t.get("title")) or "sin títulos recientes"
        invoice_line = ""
        open_invoices = ws.get("open_invoices")
        if open_invoices:
            invoice_line = (
                f" | facturas abiertas: {open_invoices.get('count', 0)} "
                f"(USD {open_invoices.get('total_usd', 0):.2f})"
            )
        lines.append(
            f"- **{ws['name']}**: {total} fuente(s) ({title_text}){invoice_line}"
        )

    lines.append(
        "\nSi quieres profundizar en algún workspace, escribe por ejemplo: "
        "\"muéstrame el workspace {slug}\"."
    )
    return "\n".join(lines)


def _resolve_target_workspace(
    ctx: Context,
    conn: Any,
    query: str,
) -> dict[str, Any] | None:
    """Intenta resolver el workspace objetivo a partir de la consulta."""

    tenant_id = ctx.require_tenant()
    list_ctx = system_context(tenant_id=tenant_id)

    # 1. Referencia explícita "workspace X" / "espacio Y" / "ws-Z".
    match = _WS_REFERENCE_RE.search(query)
    if match:
        ref = match.group(1).strip()
        ws = system_get_workspace_by_slug(list_ctx, conn, ref)
        if ws is None:
            # Puede ser un id parcial.
            for candidate in system_list_workspaces(list_ctx, conn):
                if candidate["id"].startswith(ref) or candidate["name"].lower() == ref.lower():
                    ws = candidate
                    break
        if ws is not None:
            return ws

    # 2. Match por nombre completo (case-insensitive).
    lowered = query.lower()
    for candidate in system_list_workspaces(list_ctx, conn):
        if candidate.get("kind") == "tenant_general":
            continue
        if candidate["name"].lower() in lowered:
            return candidate

    return None


def deepdive(
    ctx: Context,
    conn: Any,
    query: str,
) -> dict[str, Any]:
    """Profundiza en un workspace concreto con la autoridad del usuario.

    Nunca eleva privilegios: el Context del workspace destino conserva el
    usuario y rol del request original.
    """

    target_ws = _resolve_target_workspace(ctx, conn, query)
    if target_ws is None:
        return {
            "content": (
                "No detecté a qué workspace te refieres. "
                "Escribe por ejemplo: \"muéstrame el workspace mwt-demo\"."
            ),
            "target_workspace_id": None,
            "level": None,
            "evidence": [],
        }

    target_ctx = ctx.with_workspace(target_ws["id"])

    read_level, sealed = resolve_read_level(
        conn,
        tenant_id=target_ctx.tenant_id or ctx.tenant_id,
        space_id=target_ctx.workspace_id,
        user_roles=_user_roles(target_ctx),
        default=KeyLevel.CONTENT,
    )

    if read_level == KeyLevel.CLOSED:
        # POL_VISIBILIDAD: no revelar existencia más allá de lo permitido.
        return {
            "content": (
                "No tengo acceso a ese workspace. "
                "Si crees que deberías verlo, contacta al owner."
            ),
            "target_workspace_id": target_ws["id"],
            "level": "closed",
            "evidence": [],
        }

    if read_level == KeyLevel.INDEX:
        brief_row = get_workspace_brief(conn, target_ctx, target_ws["id"])
        brief = brief_row.get("brief") or {} if brief_row else {}
        total = sum((brief.get("source_counts") or {}).values())
        titles = brief.get("recent_titles") or []
        title_text = ", ".join(t["title"] for t in titles[:5] if t.get("title")) or "sin títulos"
        return {
            "content": (
                f"El workspace **{target_ws['name']}** tiene {total} fuente(s). "
                f"Títulos recientes: {title_text}. "
                "Para ver contenido detallado necesitas permiso de contenido."
            ),
            "target_workspace_id": target_ws["id"],
            "level": "index",
            "evidence": [],
        }

    # CONTENT: usamos el evidence pack normal del workspace.
    evidence = _build_evidence_pack(target_ctx, conn, query)
    if not evidence:
        return {
            "content": f"Entré al workspace **{target_ws['name']}**, pero no encontré datos relevantes.",
            "target_workspace_id": target_ws["id"],
            "level": "content",
            "evidence": [],
        }

    lines = [f"Encontré esto en **{target_ws['name']}**:"]
    for entry in evidence:
        lines.append(f"- **{entry.get('title')}**")
        if entry.get("excerpt"):
            excerpt = entry["excerpt"][:400]
            lines.append(f"  {excerpt}...")
        for fact in entry.get("facts", [])[:5]:
            lines.append(
                f"  - {fact.get('field') or 'dato'}: {fact.get('value')} "
                f"({fact.get('source_version') or 'sin versión'})"
            )

    return {
        "content": "\n".join(lines),
        "target_workspace_id": target_ws["id"],
        "level": "content",
        "evidence": evidence,
    }


def _chat_with_model(
    ctx: Context,
    conn: Any,
    query: str,
    index_context: dict[str, Any],
    requested_provider: str | None = None,
    requested_model: str | None = None,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any] | None:
    """E5-fix4: responde conversación con un modelo REAL (cheap-first).

    System prompt = identidad del agente + contexto INDEX (sin contenido).
    Registra el costo en usage_record. Fail-soft: None si no hay providers
    configurados o algo falla — el caller cae al texto de cortesía.
    """

    try:
        import time as _time

        from ..config_cascade import resolve as cascade_resolve
        from ..db import insert_usage_record, sum_workspace_usage_cost
        from ..router.models import CompletionRequest
        from ..router.registry import build_router
        from ..routing.catalog import (
            has_catalog_capability,
            resolve_model_for_capability,
            seed_workspace_catalog,
        )

        if ctx.workspace_id and not has_catalog_capability(ctx, conn, "text"):
            seed_workspace_catalog(ctx, conn, ctx.workspace_id)

        budget_cap = float(cascade_resolve(conn, ctx, "routing.max_budget_usd", default=2.0) or 2.0)
        spent = sum_workspace_usage_cost(ctx, conn)
        remaining = max(0.0, budget_cap - spent)
        # __E5FIX9__: en modo manual el usuario manda — si eligió provider/modelo
        # en el composer, se respeta (si está configurado); cheap-first es solo
        # el default cuando no eligió nada.
        entry = None
        if requested_provider:
            try:
                entry = resolve_model_for_capability(
                    ctx,
                    conn,
                    "text",
                    budget_remaining=remaining,
                    complexity="low",
                    preferred_provider=requested_provider,
                )
            except ValueError:
                entry = None
            if entry is not None and requested_model:
                entry = {**entry, "model": requested_model}
        if entry is None:
            try:
                entry = resolve_model_for_capability(ctx, conn, "cheap", budget_remaining=remaining)
            except ValueError:
                entry = resolve_model_for_capability(
                    ctx, conn, "text", budget_remaining=remaining, complexity="low"
                )

        byo_mode = cascade_resolve(conn, ctx, "routing.byo_mode", default="hibrido")
        router = build_router(user_id=ctx.user_id, tenant_id=ctx.tenant_id, byo_mode=byo_mode)
        provider = router.providers.get(entry["provider_slug"])
        if provider is None:
            return None

        display_name = index_context.get("display_name") or DEFAULT_AGENT_DISPLAY_NAME
        ws_lines = []
        for ws in (index_context.get("workspaces") or [])[:8]:
            counts = ws.get("source_counts") or {}
            ws_lines.append(
                f"- {ws.get('name')}: {sum(counts.values())} fuente(s), nivel {ws.get('level')}"
            )
        system_prompt = (
            f"Eres {display_name}, el agente vivo de este tenant en FaberLoom. "
            "Responde en el idioma del usuario, breve, cálido y útil. Regla dura: "
            "no inventes datos de negocio; si preguntan por contenido concreto, "
            "ofrece mirar el workspace correspondiente. Workspaces visibles "
            "(solo índice):\n" + ("\n".join(ws_lines) if ws_lines else "(ninguno)")
        )

        started = _time.time()
        result = provider.complete(
            CompletionRequest(
                # __E5FIX22__: historial del chat entre el system y la query.
                messages=(
                    [{"role": "system", "content": system_prompt}]
                    + [
                        {"role": m["role"], "content": str(m.get("content", ""))[:2500]}
                        for m in (history or [])[-6:]
                        if m.get("role") in ("user", "assistant") and m.get("content")
                    ]
                    + [{"role": "user", "content": query}]
                ),
                model=entry["model"],
                provider_slug=entry["provider_slug"],
                temperature=0.4,
                max_tokens=400,
                spent_usd=spent,
            )
        )
        duration_ms = int((_time.time() - started) * 1000)
        content = (getattr(result, "content", "") or "").strip()
        if not content:
            return None
        info = {
            "content": content,
            "provider_slug": entry["provider_slug"],
            "model": entry["model"],
            "input_tokens": int(getattr(result, "input_tokens", 0) or 0),
            "output_tokens": int(getattr(result, "output_tokens", 0) or 0),
            "cost_usd": float(getattr(result, "cost_usd", 0.0) or 0.0),
            "duration_ms": duration_ms,
        }
        try:
            insert_usage_record(
                ctx,
                conn,
                chat_id=None,
                provider_slug=info["provider_slug"],
                model=info["model"],
                input_tokens=info["input_tokens"],
                output_tokens=info["output_tokens"],
                cost_usd=info["cost_usd"],
                duration_ms=duration_ms,
                status="succeeded",
                error=None,
                attempts_json=[],
                request_json={"origin": "living_agent.presence.chat"},
                response_json={"chars": len(content)},
                capability="text",
                key_origin=getattr(result, "key_origin", None),
            )
        except Exception:
            pass  # el registro de costo no debe tumbar la respuesta
        return info
    except Exception:
        return None


def handle_presence_message(
    ctx: Context,
    conn: Any,
    query: str,
    *,
    correlation_id: str | None = None,
    requested_provider: str | None = None,
    requested_model: str | None = None,
    chat_id: str | None = None,
) -> dict[str, Any]:
    """Punto de entrada de la presencia para una consulta en ws-general.

    Retorna un dict con:
      - content: texto de respuesta.
      - intent: clasificación.
      - level: 'index' | 'content' | None.
      - target_workspace_id: str | None.
      - audit_payload: dict para escribir living_agent.read.
    """

    intent = classify_intent(query)

    if intent == "deepdive":
        result = deepdive(ctx, conn, query)
        return {
            "content": result["content"],
            "intent": intent,
            "level": result.get("level"),
            "target_workspace_id": result.get("target_workspace_id"),
            "audit_payload": {
                "action": "living_agent.read",
                "intent": intent,
                "target_workspace_id": result.get("target_workspace_id"),
                "level": result.get("level"),
                "correlation_id": correlation_id,
            },
        }

    if intent == "task":
        return {
            "content": (
                "Para crear una tarea o automatización, ve a **Agent Tasks** "
                "o escribe directamente en el workspace donde quieres que actúe."
            ),
            "intent": intent,
            "level": None,
            "target_workspace_id": None,
            "audit_payload": {
                "action": "living_agent.read",
                "intent": intent,
                "correlation_id": correlation_id,
            },
        }

    if intent == "chat":
        index_context = gather_index_context(ctx, conn, query=query)
        # __E5FIX6__: el modelo real se intenta SIEMPRE primero — la ausencia de
        # briefs (tenant "vacío" a ojos del índice) no debe degradar a texto
        # enlatado si hay providers configurados.
        _history: list[dict[str, str]] = []
        if chat_id:
            try:
                from ..db import get_message_history

                _history = get_message_history(ctx, conn, chat_id)
                if _history and _history[-1].get("role") == "user":
                    _history = _history[:-1]
            except Exception:
                _history = []
        llm = _chat_with_model(
            ctx, conn, query, index_context,
            requested_provider=requested_provider,
            requested_model=requested_model,
            history=_history,
        )
        if llm is not None:
            content = llm["content"]
        elif _tenant_context_is_empty(index_context):
            content = _format_index_answer(index_context)
        else:
            content = (
                f"Hola, soy {_display_name_for_agent(conn, ctx.require_tenant())}. "
                "Pregúntame qué hay en tus workspaces o pídeme que profundice en alguno."
            )
        out = {
            "content": content,
            "intent": intent,
            "level": None,
            "target_workspace_id": None,
            "audit_payload": {
                "action": "living_agent.read",
                "intent": intent,
                "model": (llm or {}).get("model"),
                "provider_slug": (llm or {}).get("provider_slug"),
                "correlation_id": correlation_id,
            },
        }
        if llm is not None:
            out["llm"] = llm
        return out

    # general
    index_context = gather_index_context(ctx, conn, query=query)
    content = _format_index_answer(index_context)
    return {
        "content": content,
        "intent": intent,
        "level": "index",
        "target_workspace_id": None,
        "audit_payload": {
            "action": "living_agent.read",
            "intent": intent,
            "level": "index",
            "workspaces": index_context["audit_sources"],
            "correlation_id": correlation_id,
        },
    }
