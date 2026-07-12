"""E4-6: WhatsApp Business Cloud API outbound connector (draft-first / HITL).

Security model:

* Per-tenant secrets (access_token, phone_number_id, business_account_id) are
  stored encrypted via TenantSecretStore.
* Outbound send is always HITL-gated by a deterministic confirmation token.
* 24-hour conversation window is enforced; outside the window only pre-approved
  templates can be sent.
* Fail-closed: missing secrets or configuration returns an error, never silently
  drops or sends.
"""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from ..context import Context
from ..security.secrets import TenantSecretStore


class WhatsAppOutboundError(Exception):
    """Fail-closed error from the WhatsApp outbound connector."""


@dataclass(frozen=True, slots=True)
class WhatsAppOutboundConfig:
    phone_number_id: str
    access_token: str
    business_account_id: str | None = None


class _WhatsAppOutboundSecretStore:
    """Encrypted per-tenant/per-phone-number secrets for outbound WhatsApp."""

    def __init__(self) -> None:
        from ..router.config_store import get_config_dir

        self._path = get_config_dir() / "whatsapp_secrets.json"
        self._cipher = TenantSecretStore()

    def _load(self) -> dict[str, Any]:
        if not self._path.exists():
            return {}
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save(self, data: dict[str, Any]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def _namespace(phone_number_id: str, suffix: str) -> str:
        return f"connectors/whatsapp/{phone_number_id}/{suffix}"

    def set_secret(
        self,
        ctx: Context,
        phone_number_id: str,
        suffix: str,
        plaintext: str | None,
    ) -> None:
        if plaintext is None:
            return
        data = self._load()
        tenant_secrets = data.setdefault(ctx.tenant_id or "default", {})
        tenant_secrets[self._namespace(phone_number_id, suffix)] = (
            self._cipher.encrypt_for_tenant(ctx, plaintext)
        )
        self._save(data)

    def get_secret(
        self,
        ctx: Context,
        phone_number_id: str,
        suffix: str,
    ) -> str | None:
        data = self._load()
        envelope = data.get(ctx.tenant_id or "default", {}).get(
            self._namespace(phone_number_id, suffix)
        )
        if envelope is None:
            return None
        return self._cipher.decrypt_for_tenant(ctx, envelope)

    def delete_namespace(self, ctx: Context, phone_number_id: str) -> None:
        data = self._load()
        tenant_secrets = data.get(ctx.tenant_id or "default", {})
        prefix = self._namespace(phone_number_id, "")
        data[ctx.tenant_id or "default"] = {
            k: v for k, v in tenant_secrets.items() if not k.startswith(prefix)
        }
        self._save(data)


def _secret_store() -> _WhatsAppOutboundSecretStore:
    return _WhatsAppOutboundSecretStore()


def set_whatsapp_outbound_secret(
    ctx: Context,
    phone_number_id: str,
    suffix: str,
    plaintext: str | None,
) -> None:
    _secret_store().set_secret(ctx, phone_number_id, suffix, plaintext)


def get_whatsapp_outbound_secret(
    ctx: Context,
    phone_number_id: str,
    suffix: str,
) -> str | None:
    return _secret_store().get_secret(ctx, phone_number_id, suffix)


def delete_whatsapp_outbound_secrets(ctx: Context, phone_number_id: str) -> None:
    _secret_store().delete_namespace(ctx, phone_number_id)


def load_whatsapp_outbound_config(
    ctx: Context,
    phone_number_id: str,
) -> WhatsAppOutboundConfig:
    """Load outbound config fail-closed."""

    access_token = get_whatsapp_outbound_secret(ctx, phone_number_id, "access_token")
    if not access_token:
        raise WhatsAppOutboundError("WhatsApp outbound access_token not configured")

    return WhatsAppOutboundConfig(
        phone_number_id=phone_number_id,
        access_token=access_token,
        business_account_id=get_whatsapp_outbound_secret(
            ctx, phone_number_id, "business_account_id"
        ),
    )


def confirmation_token(payload: dict[str, Any]) -> str:
    """Deterministic HITL token for a WhatsApp send request."""

    material = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(f"wa_outbound:{material}".encode("utf-8")).hexdigest()[:16]


def _graph_api_base() -> str:
    return "https://graph.facebook.com/v18.0"


def _is_within_24h(last_customer_message_at: str | None) -> bool:
    if not last_customer_message_at:
        return False
    try:
        last = datetime.fromisoformat(last_customer_message_at)
    except Exception:
        return False
    return datetime.now(timezone.utc) - last < timedelta(hours=24)


def send_message(
    config: WhatsAppOutboundConfig,
    to: str,
    body: str,
    *,
    message_id: str | None = None,
    confirmation_token_value: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Send or preview a WhatsApp text message.

    Without a confirmation token, returns the token required for HITL approval.
    With a token, posts to the Cloud API.
    """

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    if message_id:
        payload["context"] = {"message_id": message_id}

    expected_token = confirmation_token(payload)
    if dry_run or confirmation_token_value is None:
        return {
            "confirmation_token": expected_token,
            "dry_run": True,
            "provider": "whatsapp",
        }

    if confirmation_token_value != expected_token:
        raise WhatsAppOutboundError("Confirmation token mismatch")

    url = f"{_graph_api_base()}/{config.phone_number_id}/messages"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {config.access_token}",
            "Content-Type": "application/json",
            "User-Agent": "FaberLoom-WhatsApp-Outbound/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30.0) as resp:  # noqa: S310
            response_body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8") if exc else ""
        raise WhatsAppOutboundError(f"WhatsApp API error: {exc.code} {error_body}") from exc
    except urllib.error.URLError as exc:
        raise WhatsAppOutboundError(f"WhatsApp API unreachable: {exc}") from exc

    try:
        result = json.loads(response_body)
    except Exception as exc:
        raise WhatsAppOutboundError("Invalid WhatsApp API response") from exc

    return {
        "provider": "whatsapp",
        "confirmation_token": expected_token,
        "dry_run": False,
        "result": result,
    }


def send_template(
    config: WhatsAppOutboundConfig,
    to: str,
    template_name: str,
    language_code: str,
    *,
    components: list[dict[str, Any]] | None = None,
    confirmation_token_value: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Send or preview a WhatsApp template message (outside 24h window)."""

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code},
        },
    }
    if components:
        payload["template"]["components"] = components

    expected_token = confirmation_token(payload)
    if dry_run or confirmation_token_value is None:
        return {
            "confirmation_token": expected_token,
            "dry_run": True,
            "provider": "whatsapp",
        }

    if confirmation_token_value != expected_token:
        raise WhatsAppOutboundError("Confirmation token mismatch")

    url = f"{_graph_api_base()}/{config.phone_number_id}/messages"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {config.access_token}",
            "Content-Type": "application/json",
            "User-Agent": "FaberLoom-WhatsApp-Outbound/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30.0) as resp:  # noqa: S310
            response_body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8") if exc else ""
        raise WhatsAppOutboundError(f"WhatsApp API error: {exc.code} {error_body}") from exc
    except urllib.error.URLError as exc:
        raise WhatsAppOutboundError(f"WhatsApp API unreachable: {exc}") from exc

    try:
        result = json.loads(response_body)
    except Exception as exc:
        raise WhatsAppOutboundError("Invalid WhatsApp API response") from exc

    return {
        "provider": "whatsapp",
        "confirmation_token": expected_token,
        "dry_run": False,
        "result": result,
    }


def send_approved_reply(
    config: WhatsAppOutboundConfig,
    to: str,
    body: str,
    *,
    last_customer_message_at: str | None = None,
    confirmation_token_value: str,
) -> dict[str, Any]:
    """HITL-gated WhatsApp reply enforcing the 24h conversation window.

    If the last customer message is older than 24h, a template must be used
    instead of this free-form endpoint.
    """

    if not _is_within_24h(last_customer_message_at):
        raise WhatsAppOutboundError(
            "Outside 24h conversation window; use send_template instead"
        )

    return send_message(
        config,
        to,
        body,
        confirmation_token_value=confirmation_token_value,
    )
