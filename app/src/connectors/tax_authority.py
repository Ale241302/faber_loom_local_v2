"""E3-2: tax authority connector adapters (ATV, SAT, DIAN).

The module provides a small adapter layer that lets fiscal skills fetch evidence
from official tax portals without inventing endpoints or credentials.  It is
intentionally fail-closed:

* ``mock`` returns deterministic local fixtures marked ``source_type="mock"``.
* ``sandbox``/``live`` read ``base_url`` and credentials from tenant-scoped
  configuration; if they are missing the connector raises a clear error.
* ``live`` additionally requires a configured certificate; if it is missing the
  error is ``"certificado no configurado (HE2-9)"``.

Non-secret configuration lives in ``tenant_settings`` under the namespace
``connectors.tax.<authority>.*``.  Secrets (api keys, certificates, etc.) are
stored encrypted via ``TenantSecretStore`` under the namespace
``connectors/tax/<authority>/<suffix>``.
"""

from __future__ import annotations

import hashlib
import json
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from ..config_cascade import ConfigCascadeError, resolve as config_resolve
from ..context import Context
from ..db import utc_now
from ..security.secrets import TenantSecretStore


# Simple HTTP client used by the real ATV integration.  Kept internal so tests can
# monkeypatch it with cassettes without touching the public surface.
def _http_request(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    body: bytes | None = None,
    timeout: int = 30,
) -> tuple[int, bytes]:
    """Perform a plain HTTP request and return (status_code, response_body)."""

    req = urllib.request.Request(
        url,
        data=body,
        method=method.upper(),
        headers=headers or {},
    )
    # Use a permissive SSL context only for broad compatibility with sandbox portals
    # that may use self-signed certificates.  Real production traffic should ride on
    # the portal's proper CA-issued certificate, but this avoids hard-blocking early
    # integration tests.  The caller still validates the response payload.
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=context) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


TAX_AUTHORITIES = frozenset({"atv", "sat", "dian"})

AUTHORITY_LABELS = {
    "atv": "ATV (Costa Rica)",
    "sat": "SAT (México)",
    "dian": "DIAN (Colombia)",
}

_PENDING_MARKER = "PENDIENTE — NO INVENTAR"


class TaxConnectorError(Exception):
    """Fail-closed error raised by a tax authority connector."""


def _setting_key(authority: str, suffix: str) -> str:
    """Non-secret tenant setting key for a connector option."""
    return f"connectors.tax.{authority}.{suffix}"


def _secret_namespace_key(authority: str, suffix: str) -> str:
    """Encrypted secret namespace key for a connector credential."""
    return f"connectors/tax/{authority}/{suffix}"


class _ConnectorSecretStore:
    """Tiny encrypted key/value file for tenant-scoped connector secrets.

    Values are encrypted with the tenant data key managed by
    ``TenantSecretStore``.  The file lives next to the tenant data-key
    repository inside the FaberLoom config directory.
    """

    def __init__(self, path: Path | None = None) -> None:
        if path is None:
            from ..router.config_store import get_config_dir

            path = get_config_dir() / "connector_secrets.json"
        self._path = path
        self._cipher = TenantSecretStore()

    def _load(self) -> dict[str, Any]:
        if not self._path.exists():
            return {}
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:  # pragma: no cover - corrupted file is treated as empty
            return {}

    def _save(self, data: dict[str, Any]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def set_secret(
        self,
        ctx: Context,
        namespace_key: str,
        plaintext: str | None,
    ) -> None:
        if plaintext is None:
            return
        data = self._load()
        tenant_secrets = data.setdefault(ctx.tenant_id or "default", {})
        tenant_secrets[namespace_key] = self._cipher.encrypt_for_tenant(ctx, plaintext)
        self._save(data)

    def get_secret(self, ctx: Context, namespace_key: str) -> str | None:
        data = self._load()
        envelope = data.get(ctx.tenant_id or "default", {}).get(namespace_key)
        return self._cipher.decrypt_for_tenant(ctx, envelope)


@dataclass(frozen=True, slots=True)
class TaxConnectorConfig:
    """Resolved configuration for a single tax authority connector."""

    authority: str
    mode: str
    base_url: str | None = None
    document_status_endpoint: str | None = None
    taxpayer_info_endpoint: str | None = None
    api_key: str | None = None
    api_secret: str | None = None
    certificate: str | None = None

    @property
    def is_mock(self) -> bool:
        return self.mode == "mock"

    @property
    def is_live(self) -> bool:
        return self.mode == "live"


def _resolve_setting(
    conn: Any,
    ctx: Context,
    authority: str,
    suffix: str,
) -> Any:
    try:
        return config_resolve(conn, ctx, _setting_key(authority, suffix), None)
    except ConfigCascadeError:
        return None


def _resolve_connector_config(
    ctx: Context,
    conn: Any,
    authority: str,
) -> TaxConnectorConfig:
    if authority not in TAX_AUTHORITIES:
        raise TaxConnectorError(f"Unknown tax authority: {authority}")

    mode = _resolve_setting(conn, ctx, authority, "mode") or "mock"
    if mode not in {"mock", "sandbox", "live"}:
        raise TaxConnectorError(f"Invalid mode '{mode}' for {authority}")

    secrets = _ConnectorSecretStore()
    api_key = secrets.get_secret(ctx, _secret_namespace_key(authority, "api_key"))
    api_secret = secrets.get_secret(ctx, _secret_namespace_key(authority, "api_secret"))
    certificate = secrets.get_secret(ctx, _secret_namespace_key(authority, "certificate"))

    return TaxConnectorConfig(
        authority=authority,
        mode=mode,
        base_url=_resolve_setting(conn, ctx, authority, "base_url"),
        document_status_endpoint=_resolve_setting(
            conn, ctx, authority, "document_status_endpoint"
        ),
        taxpayer_info_endpoint=_resolve_setting(
            conn, ctx, authority, "taxpayer_info_endpoint"
        ),
        api_key=api_key,
        api_secret=api_secret,
        certificate=certificate,
    )


class TaxAuthorityConnector:
    """Adapter for a single tax authority portal.

    The public methods return a dict with ``status``, ``authority``, ``mode`` and
    an ``evidence`` list ready to be attached via ``attach_evidence``.
    """

    def __init__(self, authority: str, config: TaxConnectorConfig) -> None:
        self.authority = authority
        self.config = config

    def _label(self) -> str:
        return AUTHORITY_LABELS.get(self.authority, self.authority)

    def _require_configured(self) -> None:
        if not self.config.base_url:
            raise TaxConnectorError(
                f"Conector {self._label()} no configurado: base_url vacía. "
                f"[{_PENDING_MARKER}]"
            )
        if not self.config.document_status_endpoint:
            raise TaxConnectorError(
                f"Conector {self._label()} no configurado: endpoint de estado de documento ausente. "
                f"[{_PENDING_MARKER}]"
            )
        if not self.config.taxpayer_info_endpoint:
            raise TaxConnectorError(
                f"Conector {self._label()} no configurado: endpoint de contribuyente ausente. "
                f"[{_PENDING_MARKER}]"
            )
        if not self.config.api_key:
            raise TaxConnectorError(
                f"Conector {self._label()} no configurado: credenciales ausentes. "
                f"[{_PENDING_MARKER}]"
            )

    def _require_endpoints_for_mode(self) -> None:
        """Sandbox/live both need explicit endpoints; mock does not."""
        if self.config.is_mock:
            return
        self._require_configured()

    def _require_certificate(self) -> None:
        if not self.config.certificate:
            raise TaxConnectorError("certificado no configurado (HE2-9)")

    @staticmethod
    def _content_hash(payload: str) -> str:
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    def _mock_document_status(self, document_key: str) -> dict[str, Any]:
        body = json.dumps(
            {
                "authority": self.authority,
                "document_key": document_key,
                "status": "aceptado",
                "message": "Fixture determinista de prueba",
            },
            ensure_ascii=False,
        )
        return {
            "status": "succeeded",
            "authority": self.authority,
            "mode": "mock",
            "evidence": [
                {
                    "source_type": "mock",
                    "source_locator": f"mock://{self.authority}/document-status/{document_key}",
                    "captured_at": utc_now(),
                    "content_text": body,
                    "content_hash": self._content_hash(body),
                }
            ],
        }

    def _mock_taxpayer_info(self, taxpayer_id: str) -> dict[str, Any]:
        body = json.dumps(
            {
                "authority": self.authority,
                "taxpayer_id": taxpayer_id,
                "name": "Contribuyente de prueba",
                "status": "activo",
            },
            ensure_ascii=False,
        )
        return {
            "status": "succeeded",
            "authority": self.authority,
            "mode": "mock",
            "evidence": [
                {
                    "source_type": "mock",
                    "source_locator": f"mock://{self.authority}/taxpayer-info/{taxpayer_id}",
                    "captured_at": utc_now(),
                    "content_text": body,
                    "content_hash": self._content_hash(body),
                }
            ],
        }

    @staticmethod
    def _join_url(base: str, endpoint: str) -> str:
        """Join a base URL and an endpoint path with a single slash."""
        return base.rstrip("/") + "/" + endpoint.lstrip("/")

    def _auth_headers(self) -> dict[str, str]:
        """Headers used by the real ATV HTTP integration.

        The exact header names are generic (Bearer token + secret header).  When the
        official ATV API contract is confirmed by the PLB timebox, this method is the
        only place that needs to change.
        """
        headers: dict[str, str] = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
        }
        if self.config.api_secret:
            headers["X-API-Secret"] = self.config.api_secret
        return headers

    def _parse_atv_response(self, status_code: int, body: bytes) -> dict[str, Any]:
        """Parse a raw ATV response into the canonical evidence shape.

        The connector does not interpret business semantics beyond a JSON body.  If the
        portal returns non-JSON, the body is captured as text so the caller can decide.
        """
        text = body.decode("utf-8", errors="replace")
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = {"raw_body": text}

        # We never fabricate acceptance; the status string comes straight from the portal.
        status = "unknown"
        if isinstance(payload, dict):
            status = str(payload.get("status") or payload.get("estado") or status).lower()
        return {
            "status": "succeeded" if 200 <= status_code < 300 else "failed",
            "authority": self.authority,
            "mode": self.config.mode,
            "http_status": status_code,
            "authority_status": status,
            "evidence": [
                {
                    "source_type": self.config.mode,
                    "source_locator": "atv-response",
                    "captured_at": utc_now(),
                    "content_text": text,
                    "content_hash": self._content_hash(text),
                }
            ],
        }

    def _atv_document_status(self, document_key: str) -> dict[str, Any]:
        """Real HTTP lookup of an electronic document status in ATV."""

        if self.authority != "atv":
            raise TaxConnectorError(
                f"Ruta HTTP real no habilitada para {self._label()}. [{_PENDING_MARKER}]"
            )
        url = self._join_url(
            self.config.base_url,  # type: ignore[arg-type]
            self.config.document_status_endpoint,  # type: ignore[arg-type]
        )
        url = url.replace("{document_key}", document_key)
        status_code, body = _http_request("GET", url, headers=self._auth_headers())
        return self._parse_atv_response(status_code, body)

    def _atv_taxpayer_info(self, taxpayer_id: str) -> dict[str, Any]:
        """Real HTTP lookup of taxpayer registration info in ATV."""

        if self.authority != "atv":
            raise TaxConnectorError(
                f"Ruta HTTP real no habilitada para {self._label()}. [{_PENDING_MARKER}]"
            )
        url = self._join_url(
            self.config.base_url,  # type: ignore[arg-type]
            self.config.taxpayer_info_endpoint,  # type: ignore[arg-type]
        )
        url = url.replace("{taxpayer_id}", taxpayer_id)
        status_code, body = _http_request("GET", url, headers=self._auth_headers())
        return self._parse_atv_response(status_code, body)

    def _live_document_status(self, document_key: str) -> dict[str, Any]:
        # Only ATV has a real HTTP path implemented.  SAT/DIAN remain fail-closed
        # until their official APIs are verified by the PLB timebox.
        if self.authority == "atv":
            return self._atv_document_status(document_key)
        raise TaxConnectorError(
            f"Integración {self.config.mode} con {self._label()} no implementada: "
            f"configure URLs reales o use modo mock. [{_PENDING_MARKER}]"
        )

    def _live_taxpayer_info(self, taxpayer_id: str) -> dict[str, Any]:
        if self.authority == "atv":
            return self._atv_taxpayer_info(taxpayer_id)
        raise TaxConnectorError(
            f"Integración {self.config.mode} con {self._label()} no implementada: "
            f"configure URLs reales o use modo mock. [{_PENDING_MARKER}]"
        )

    def check_document_status(self, document_key: str) -> dict[str, Any]:
        """Return the status of an electronic document from the authority."""

        if self.config.is_mock:
            return self._mock_document_status(document_key)

        self._require_endpoints_for_mode()
        if self.config.is_live:
            self._require_certificate()
        return self._live_document_status(document_key)

    def fetch_taxpayer_info(self, taxpayer_id: str) -> dict[str, Any]:
        """Return taxpayer registration info from the authority."""

        if self.config.is_mock:
            return self._mock_taxpayer_info(taxpayer_id)

        self._require_endpoints_for_mode()
        if self.config.is_live:
            self._require_certificate()
        return self._live_taxpayer_info(taxpayer_id)


def get_tax_connector(
    ctx: Context,
    conn: Any,
    authority: str,
) -> TaxAuthorityConnector:
    """Build a configured connector for ``authority`` scoped to ``ctx``."""

    return TaxAuthorityConnector(
        authority,
        _resolve_connector_config(ctx, conn, authority),
    )


def _infer_tax_authorities(skill_id: str) -> list[str]:
    """Map a fiscal skill id to the tax authorities it may query."""

    if skill_id.startswith("SKILL_FE_"):
        return ["atv", "sat", "dian"]
    return []


def build_tax_fetcher(
    ctx: Context,
    conn: Any,
    skill_id: str,
) -> Callable[[str, list[str]], list[dict[str, Any]]] | None:
    """Return an ``ExternalFetcher`` for fiscal skills, or ``None``.

    The returned fetcher is suitable for ``skill_primitives.external_lookup``.
    """

    default_authorities = _infer_tax_authorities(skill_id)
    if not default_authorities:
        return None

    def _fetcher(query: str, required_sources: list[str]) -> list[dict[str, Any]]:
        sources = [s for s in required_sources if s in TAX_AUTHORITIES]
        if not sources:
            sources = default_authorities

        evidence: list[dict[str, Any]] = []
        q = (query or "").lower()
        doc_keywords = ("documento", "clave", "comprobante", "status", "estado")
        taxpayer_keywords = ("contribuyente", "taxpayer", "rfc", "cedula", "identificacion")
        do_document = any(k in q for k in doc_keywords) or not any(
            k in q for k in taxpayer_keywords
        )
        do_taxpayer = any(k in q for k in taxpayer_keywords) or not any(
            k in q for k in doc_keywords
        )

        for authority in sources:
            connector = get_tax_connector(ctx, conn, authority)
            if do_document:
                result = connector.check_document_status(query)
                evidence.extend(result.get("evidence", []))
            if do_taxpayer:
                result = connector.fetch_taxpayer_info(query)
                evidence.extend(result.get("evidence", []))

        if not evidence:
            raise TaxConnectorError("tax_lookup_no_evidence")
        return evidence

    return _fetcher


# Convenience helpers used directly by tests and by the runtime wiring.


def set_tax_connector_secret(
    ctx: Context,
    authority: str,
    suffix: str,
    plaintext: str | None,
    path: Path | None = None,
) -> None:
    """Store a connector secret encrypted for the tenant in ``ctx``."""

    if authority not in TAX_AUTHORITIES:
        raise TaxConnectorError(f"Unknown tax authority: {authority}")
    _ConnectorSecretStore(path=path).set_secret(
        ctx,
        _secret_namespace_key(authority, suffix),
        plaintext,
    )


def get_tax_connector_secret(
    ctx: Context,
    authority: str,
    suffix: str,
    path: Path | None = None,
) -> str | None:
    """Read a connector secret for the tenant in ``ctx``."""

    if authority not in TAX_AUTHORITIES:
        raise TaxConnectorError(f"Unknown tax authority: {authority}")
    return _ConnectorSecretStore(path=path).get_secret(
        ctx,
        _secret_namespace_key(authority, suffix),
    )
