"""E5: enforcement del envelope de routing (SPEC_FB_ENVELOPE_ENFORCEMENT_v1).

El envelope de `routing_preset` declara restricciones de compliance
(jurisdicciones, providers_allow, providers_deny). Antes de este spec se
guardaba pero no se enforceaba: un tenant con `providers_deny: ["kimi"]` podia
terminar servido por Kimi cuando OpenAI fallaba, porque el loop de fallback
recorria todos los proveedores registrados.

El test mandatorio es `test_denied_provider_never_serves_on_fallback`.
"""

from __future__ import annotations

import pytest

from app.src.router.engine import Router
from app.src.router.models import (
    CompletionRequest,
    CompletionResult,
    ProviderConfig,
    RouterSettings,
)
from app.src.router.providers import Provider, ProviderError
from app.src.routing.policy import compose_routing_constraints


class _FailingOpenAI(Provider):
    """OpenAI (jurisdiccion US) que falla como en un rate limit o un 500."""

    requires_api_key = False

    def __init__(self) -> None:
        super().__init__(
            ProviderConfig(
                provider_slug="openai",
                api_key=None,
                model_default="gpt-4o-mini",
                priority=1,
                is_enabled=True,
            )
        )

    def complete(self, request: CompletionRequest) -> CompletionResult:
        raise ProviderError("openai", "simulated failure")


class _WorkingKimi(Provider):
    """Kimi (jurisdiccion CN) disponible y funcional: el fallback tentador."""

    requires_api_key = False
    served: bool = False

    def __init__(self) -> None:
        super().__init__(
            ProviderConfig(
                provider_slug="kimi",
                api_key=None,
                model_default="moonshot-v1-8k",
                priority=2,
                is_enabled=True,
            )
        )

    def complete(self, request: CompletionRequest) -> CompletionResult:
        type(self).served = True
        return CompletionResult(
            content="respuesta desde China",
            model=request.model,
            provider_slug="kimi",
            input_tokens=5,
            output_tokens=2,
            cost_usd=0.0,
            duration_ms=1,
        )


class _UnknownJurisdictionProvider(Provider):
    """Proveedor ausente de PROVIDER_JURISDICTION."""

    requires_api_key = False

    def __init__(self) -> None:
        super().__init__(
            ProviderConfig(
                provider_slug="proveedor-nuevo-sin-jurisdiccion",
                api_key=None,
                model_default="gpt-4o-mini",
                priority=1,
                is_enabled=True,
            )
        )

    def complete(self, request: CompletionRequest) -> CompletionResult:
        return CompletionResult(
            content="no deberia llegar aca",
            model=request.model,
            provider_slug="proveedor-nuevo-sin-jurisdiccion",
            input_tokens=1,
            output_tokens=1,
            cost_usd=0.0,
            duration_ms=1,
        )


@pytest.fixture(autouse=True)
def _reset_kimi_served():
    _WorkingKimi.served = False
    yield
    _WorkingKimi.served = False


def _request() -> CompletionRequest:
    return CompletionRequest(messages=[{"role": "user", "content": "hola"}])


def test_denied_provider_never_serves_on_fallback():
    """MANDATORIO: OpenAI falla, pero Kimi esta denegado => error, no respuesta.

    Es el inverso de test_cross_tenant_isolation: aca la fuga no seria de datos
    entre tenants sino de jurisdiccion. Antes de este spec, el `continue` ante
    ProviderError caia a Kimi y el run figuraba como exitoso.
    """
    router = Router(
        settings=RouterSettings(provider_denylist=["kimi"]),
        providers=[_FailingOpenAI(), _WorkingKimi()],
    )

    with pytest.raises(ProviderError):
        router.complete(_request())

    assert _WorkingKimi.served is False, "Kimi sirvio la request pese a estar denegado"


def test_jurisdiction_filter_blocks_cn():
    """envelope jurisdictions: ["US","EU"] => Kimi (CN) fuera de candidatos."""
    router = Router(
        settings=RouterSettings(jurisdiction_allowlist=["US", "EU"]),
        providers=[_FailingOpenAI(), _WorkingKimi()],
    )

    assert "kimi" not in router.list_available_providers()

    with pytest.raises(ProviderError):
        router.complete(_request())

    assert _WorkingKimi.served is False


def test_deny_beats_allow():
    """providers_allow y providers_deny nombran a Kimi => gana deny."""
    router = Router(
        settings=RouterSettings(
            provider_allowlist=["kimi"],
            provider_denylist=["kimi"],
        ),
        providers=[_WorkingKimi()],
    )

    assert router.list_available_providers() == []

    with pytest.raises(ProviderError):
        router.complete(_request())

    assert _WorkingKimi.served is False


def test_deny_beats_explicit_caller_override():
    """El caller pide kimi explicitamente, pero esta denegado => no lo sirve.

    _ordered_providers trata provider_slug como preferencia y lo pone primero
    sin chequear is_available(); el deny tiene que ganar igual.
    """
    router = Router(
        settings=RouterSettings(provider_denylist=["kimi"]),
        providers=[_WorkingKimi()],
    )

    request = CompletionRequest(
        messages=[{"role": "user", "content": "hola"}],
        provider_slug="kimi",
    )

    with pytest.raises(ProviderError):
        router.complete(request)

    assert _WorkingKimi.served is False


def test_unknown_provider_denied_under_jurisdiction_allowlist():
    """Un proveedor sin jurisdiccion declarada no se cuela por olvido."""
    router = Router(
        settings=RouterSettings(jurisdiction_allowlist=["US", "EU"]),
        providers=[_UnknownJurisdictionProvider()],
    )

    assert router.list_available_providers() == []


def test_unknown_provider_allowed_when_no_jurisdiction_restriction():
    """Sin jurisdiction_allowlist, un slug desconocido no se bloquea.

    El fail-closed solo aplica cuando el tenant declaro jurisdicciones.
    """
    router = Router(
        settings=RouterSettings(),
        providers=[_UnknownJurisdictionProvider()],
    )

    assert router.list_available_providers() == ["proveedor-nuevo-sin-jurisdiccion"]


def test_empty_envelope_preserves_current_behavior():
    """Sin restricciones => allow-all, identico a hoy.

    Caracterizacion: protege contra romper a los tenants sin envelope.
    """
    router = Router(
        settings=RouterSettings(),
        providers=[_FailingOpenAI(), _WorkingKimi()],
    )

    assert sorted(router.list_available_providers()) == ["kimi", "openai"]

    result = router.complete(_request())

    assert result.provider_slug == "kimi"
    assert _WorkingKimi.served is True


# ---------------------------------------------------------------------------
# Composicion de restricciones (funcion pura, sin DB)
# ---------------------------------------------------------------------------


def test_compose_without_sources_does_not_restrict():
    """Nada declarado => todo None => allow-all, identico a hoy."""
    constraints = compose_routing_constraints(None, None, {})

    assert constraints.provider_allowlist is None
    assert constraints.provider_denylist is None
    assert constraints.jurisdiction_allowlist is None


def test_compose_takes_envelope_allow():
    constraints = compose_routing_constraints(None, None, {"providers_allow": ["openai"]})

    assert constraints.provider_allowlist == ["openai"]


def test_compose_intersects_env_policy_and_envelope():
    """Cada fuente restringe; el resultado es la interseccion."""
    constraints = compose_routing_constraints(
        ["openai", "anthropic", "kimi"],
        ["openai", "anthropic"],
        {"providers_allow": ["anthropic", "google"]},
    )

    assert constraints.provider_allowlist == ["anthropic"]


def test_compose_skips_sources_that_do_not_restrict():
    """None en una fuente significa 'no restrinjo', no 'no permito nada'."""
    constraints = compose_routing_constraints(None, ["openai", "kimi"], {})

    assert constraints.provider_allowlist == ["openai", "kimi"]


def test_compose_empty_intersection_denies_everything():
    """CRITICO: interseccion vacia => [] (denegar todo), nunca None (permitir todo).

    Si env permite solo openai y el envelope permite solo kimi, no hay
    proveedor legal. Devolver None aca invertiria la restriccion en permiso.
    """
    constraints = compose_routing_constraints(
        ["openai"],
        None,
        {"providers_allow": ["kimi"]},
    )

    assert constraints.provider_allowlist == []
    assert constraints.provider_allowlist is not None


def test_compose_carries_deny_and_jurisdictions():
    constraints = compose_routing_constraints(
        None,
        None,
        {"providers_deny": ["kimi"], "jurisdictions": ["US", "EU"]},
    )

    assert constraints.provider_denylist == ["kimi"]
    assert constraints.jurisdiction_allowlist == ["US", "EU"]


def test_compose_does_not_subtract_deny_from_allowlist():
    """El deny se aplica en el guard, no en la composicion.

    Restarlo aca lo haria perder contra un provider_slug pedido explicitamente
    por el caller, porque _ordered_providers pone al preferido primero.
    """
    constraints = compose_routing_constraints(
        None,
        None,
        {"providers_allow": ["openai", "kimi"], "providers_deny": ["kimi"]},
    )

    assert constraints.provider_allowlist == ["openai", "kimi"]
    assert constraints.provider_denylist == ["kimi"]


def test_compose_empty_envelope_lists_do_not_restrict():
    """Los defaults de _default_preset_envelope traen listas vacias.

    `providers_deny: []` significa "no deniego a nadie", no "deniego a todos".
    """
    constraints = compose_routing_constraints(
        None,
        None,
        {"providers_allow": [], "providers_deny": [], "jurisdictions": []},
    )

    assert constraints.provider_allowlist is None
    assert constraints.provider_denylist is None
    assert constraints.jurisdiction_allowlist is None


# ---------------------------------------------------------------------------
# Cableado: el envelope tiene que llegar desde la DB hasta el guard
# ---------------------------------------------------------------------------


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(tmp_path / "faberloom.sqlite3"))
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path / "config"))
    for name in (
        "FABERLOOM_PROVIDER_ALLOWLIST",
        "FABERLOOM_BUDGET_CAP_USD",
        "OPENAI_API_KEY",
        "FABERLOOM_OPENAI_API_KEY",
        "KIMI_API_KEY",
        "MOONSHOT_API_KEY",
        "FABERLOOM_KIMI_API_KEY",
    ):
        monkeypatch.delenv(name, raising=False)

    from fastapi.testclient import TestClient

    from app.src.audit import audit_writer
    from app.src.main import create_app

    audit_writer.audit_path = tmp_path / "audit.jsonl"
    with TestClient(create_app()) as test_client:
        yield test_client


def test_build_router_threads_constraints_into_settings(client):
    """build_router tiene que transportar las restricciones hasta RouterSettings.

    El guard puede estar perfecto y el cable mal conectado; esto prueba el cable.
    """
    from app.src.router.registry import build_router

    router = build_router(
        provider_denylist=["kimi"],
        jurisdiction_allowlist=["US", "EU"],
    )

    assert router.settings.provider_denylist == ["kimi"]
    assert router.settings.jurisdiction_allowlist == ["US", "EU"]


def test_envelope_from_db_reaches_constraints(client):
    """Un envelope guardado en routing_preset tiene que llegar a las constraints.

    Es el tramo que faltaba: la tabla existia, el guard existia, y nadie los unia.
    """
    from fastapi import Request

    from app.src.api import context_from_request
    from app.src.db import connect, create_routing_preset
    from app.src.db_adapter import transaction
    from app.src.routing.policy import resolve_effective_routing_constraints

    workspace_id = client.get("/api/workspaces").json()["workspaces"][0]["id"]
    ctx = context_from_request(
        Request(scope={"type": "http", "headers": []}), workspace_id=workspace_id
    )

    conn = connect()
    try:
        with transaction(conn, ctx=ctx):
            create_routing_preset(
                ctx,
                conn,
                preset_id="sin-chinos",
                name="Sin chinos",
                description="Compliance: nada de proveedores en CN.",
                envelope={
                    "providers_allow": ["anthropic", "openai"],
                    "providers_deny": ["kimi"],
                    "jurisdictions": ["US", "EU"],
                },
                curve={"mode": "balanceado"},
                task_overrides={},
                caps={},
                escalation={},
            )

        constraints = resolve_effective_routing_constraints(ctx, conn, "@preset/sin-chinos")

        assert constraints.provider_denylist == ["kimi"]
        assert constraints.jurisdiction_allowlist == ["US", "EU"]
        assert constraints.provider_allowlist == ["anthropic", "openai"]
    finally:
        conn.close()


def test_resolve_preset_never_returns_incoherent_pair(client):
    """providers_allow: ["kimi"] + balanceado no debe devolver kimi/gpt-4o.

    El resolver adivinaba: elegia el modelo por la curva y despues le buscaba
    proveedor con un next(...) que caia a providers_allow[0]. Con solo kimi
    permitido devolvia el par kimi/gpt-4o, un modelo que Kimi no puede servir.
    """
    from fastapi import Request

    from app.src.api import context_from_request
    from app.src.db import connect, create_routing_preset, resolve_routing_preset
    from app.src.db_adapter import transaction
    from app.src.router import cost as router_cost

    workspace_id = client.get("/api/workspaces").json()["workspaces"][0]["id"]
    ctx = context_from_request(
        Request(scope={"type": "http", "headers": []}), workspace_id=workspace_id
    )

    conn = connect()
    try:
        with transaction(conn, ctx=ctx):
            create_routing_preset(
                ctx,
                conn,
                preset_id="solo-kimi",
                name="Solo Kimi",
                description="Unico proveedor permitido: kimi.",
                envelope={"providers_allow": ["kimi"]},
                curve={"mode": "balanceado"},
                task_overrides={},
                caps={},
                escalation={},
            )

        resolved = resolve_routing_preset(ctx, conn, "@preset/solo-kimi")

        if resolved is not None:
            provider = resolved["provider_slug"]
            model = resolved["model"]
            assert model in router_cost.MODEL_ALLOWLIST.get(provider, set()), (
                f"par incoherente: {provider}/{model} "
                f"({provider} no puede servir {model})"
            )
    finally:
        conn.close()


def test_unknown_preset_does_not_restrict(client):
    """Un preset_id colgado no debe inventar restricciones ni romper la llamada.

    delete_routing_preset no chequea referencias, asi que un preset_id colgado
    es un estado alcanzable.
    """
    from fastapi import Request

    from app.src.api import context_from_request
    from app.src.db import connect
    from app.src.routing.policy import resolve_effective_routing_constraints

    workspace_id = client.get("/api/workspaces").json()["workspaces"][0]["id"]
    ctx = context_from_request(
        Request(scope={"type": "http", "headers": []}), workspace_id=workspace_id
    )

    conn = connect()
    try:
        constraints = resolve_effective_routing_constraints(ctx, conn, "@preset/no-existe")

        assert constraints.provider_allowlist is None
        assert constraints.provider_denylist is None
        assert constraints.jurisdiction_allowlist is None
    finally:
        conn.close()
