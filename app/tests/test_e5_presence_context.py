"""E5 — La presencia no debe perder el contexto de la conversación.

Bug reportado: en el chat general, tras hablar de un PDF, el mensaje
"de libro hablamos" recibió un saludo enlatado con 0 tokens y 0 ms — o sea que
nunca llegó al modelo.

Causa raíz: classify_intent devuelve "general" como FALLBACK, y la rama "general"
es la única que no llama al LLM ni pasa el historial. Solo "hola" caía en "chat",
que sí los usa (__E5FIX22__). Cualquier seguimiento conversacional perdía todo.

Regla: si no hay evidencia de que el usuario pide un panorama, una tarea o una
profundización, es conversación. La conversación necesita historial.
"""

from __future__ import annotations

import pytest

from app.src.living_agent.presence import classify_intent


# ---------------------------------------------------------------------------
# El fallback: conversación, no panorama
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "message",
    [
        "de libro hablamos",
        "y qué opinás del libro",
        "seguime contando",
        "quién es Tadeo",
        "gracias, muy bueno",
        "no entendí esa parte",
        "explicame mejor",
        "dale",
    ],
)
def test_conversational_followup_classifies_as_chat(message: str) -> None:
    """Un seguimiento conversacional es 'chat': necesita LLM + historial.

    Antes caían todos en el fallback "general", que responde desde el índice sin
    mirar el historial. Por eso el chat general solo podía sostener una
    conversación si le decías "hola".
    """
    assert classify_intent(message) == "chat"


def test_greeting_still_chat() -> None:
    assert classify_intent("hola") == "chat"


def test_empty_message_is_chat() -> None:
    assert classify_intent("") == "chat"
    assert classify_intent("   ") == "chat"


# ---------------------------------------------------------------------------
# Lo que ya funcionaba tiene que seguir funcionando
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "message",
    [
        "qué hay en mis workspaces",
        "qué tengo pendiente",
        "cuántos clientes tengo",
        "dame un overview",
        "cuál es el estado",
    ],
)
def test_explicit_overview_still_general(message: str) -> None:
    """Pedir panorama sigue yendo al índice: es barato y no necesita historial."""
    assert classify_intent(message) == "general"


@pytest.mark.parametrize(
    "message",
    [
        "muéstrame el workspace mwt",
        "profundiza en el espacio acme",
        "entra a ese workspace",
    ],
)
def test_deepdive_still_wins(message: str) -> None:
    assert classify_intent(message) == "deepdive"


@pytest.mark.parametrize(
    "message",
    [
        "creá una tarea para esto",
        "automatiza este flujo",
        "avisame cuando llegue",
    ],
)
def test_task_still_wins(message: str) -> None:
    assert classify_intent(message) == "task"


# ---------------------------------------------------------------------------
# El test que importa: el historial tiene que LLEGAR al modelo
# ---------------------------------------------------------------------------


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(tmp_path / "faberloom.sqlite3"))
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path / "config"))
    for name in (
        "OPENAI_API_KEY", "FABERLOOM_OPENAI_API_KEY",
        "ANTHROPIC_API_KEY", "FABERLOOM_ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY", "GEMINI_API_KEY", "FABERLOOM_GOOGLE_API_KEY",
        "KIMI_API_KEY", "MOONSHOT_API_KEY", "FABERLOOM_KIMI_API_KEY",
        "FABERLOOM_ENABLE_OLLAMA", "FABERLOOM_OLLAMA_ENABLED",
        "FABERLOOM_PROVIDER_ALLOWLIST", "FABERLOOM_BUDGET_CAP_USD",
        "FABERLOOM_AUTO_MODE_ENABLED",
    ):
        monkeypatch.delenv(name, raising=False)

    from fastapi.testclient import TestClient

    from app.src.audit import audit_writer
    from app.src.main import create_app

    audit_writer.audit_path = tmp_path / "audit.jsonl"
    with TestClient(create_app()) as test_client:
        yield test_client


def _headers(role: str = "owner") -> dict[str, str]:
    return {"x-actor-role": role, "x-user-id": "test", "x-actor-id": "test"}


def test_followup_reaches_the_model_with_history(client, monkeypatch) -> None:
    """El bug reportado, end-to-end.

    Tras hablar de un libro, "de libro hablamos" tiene que llegar al modelo CON
    los turnos previos. Antes recibia un saludo enlatado con 0 tokens porque el
    fallback "general" ni llamaba al modelo ni miraba el historial.
    """
    from app.src.router import registry as registry_module
    from app.src.router.engine import Router
    from app.src.router.models import CompletionResult, ProviderConfig
    from app.src.router.providers import Provider

    captured: dict[str, list] = {}

    class CapturingProvider(Provider):
        requires_api_key = False

        def __init__(self, slug: str) -> None:
            super().__init__(
                ProviderConfig(
                    provider_slug=slug, api_key="x", model_default="gpt-4o-mini",
                    priority=1, is_enabled=True,
                )
            )

        def complete(self, request):
            captured["messages"] = list(request.messages)
            return CompletionResult(
                content="Sí, hablábamos de Antígona González.",
                model=request.model or "gpt-4o-mini",
                provider_slug=self.provider_slug,
                input_tokens=10, output_tokens=5, cost_usd=0.0001, duration_ms=5,
            )

    def fake_build_router(*args, **kwargs):
        # Los cinco que registra build_router: sin API keys el catalogo resuelve
        # a ollama, asi que el fake tiene que cubrirlos todos o _chat_with_model
        # devuelve None por provider ausente y degrada a texto enlatado.
        return Router(providers=[
            CapturingProvider(s)
            for s in ("openai", "anthropic", "google", "kimi", "ollama")
        ])

    monkeypatch.setattr(registry_module, "build_router", fake_build_router)

    general_id = client.get("/api/workspaces/general", headers=_headers()).json()["id"]
    chat_id = client.post(
        f"/api/workspaces/{general_id}/chats",
        json={"title": "Chat general"},
        headers=_headers(),
    ).json()["id"]

    # Turno previo: se habló de un libro.
    first = client.post(
        f"/api/workspaces/{general_id}/chats/{chat_id}/completions",
        json={"message": "contame de Antígona González", "mode": "manual"},
        headers=_headers(),
    )
    assert first.status_code == 200, first.text

    # El seguimiento del bug.
    resp = client.post(
        f"/api/workspaces/{general_id}/chats/{chat_id}/completions",
        json={"message": "de libro hablamos", "mode": "manual"},
        headers=_headers(),
    )
    assert resp.status_code == 200, resp.text

    assert "messages" in captured, "el mensaje nunca llegó al modelo"
    roles = [m["role"] for m in captured["messages"]]
    blob = " ".join(str(m["content"]) for m in captured["messages"])

    assert roles[0] == "system"
    assert roles[-1] == "user"
    assert captured["messages"][-1]["content"] == "de libro hablamos"
    # Lo que se perdía: el turno anterior.
    assert "Antígona" in blob, f"el historial no llegó al modelo; roles={roles}"

    body = resp.json()["message"]
    assert "enlatado" not in body["content"]
    assert body["route"]["input_tokens"] > 0, "0 tokens = no fue al modelo"
