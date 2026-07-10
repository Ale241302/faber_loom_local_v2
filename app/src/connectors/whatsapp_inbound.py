"""E3-3: WhatsApp Business Cloud API inbound webhook (C0-1).

Only inbound ingestion is supported; outbound sending is out of scope.

Security model:

* The endpoint is public (no JWT) because Meta signs POST requests with the
  per-tenant app secret via ``X-Hub-Signature-256``.
* GET verification uses ``hub.verify_token``; the token is stored encrypted per
  phone number and searched at verification time.
* Per-tenant feature flag ``whatsapp_inbound.enabled`` (default ``False``) is
  enforced fail-closed: if disabled, the endpoint returns 404.
* Text messages become HITL drafts via ``capture_informal_interaction``.
* Audio messages are downloaded and transcribed with the existing Whisper
  pipeline; any failure is discarded and audited.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..audit import audit_writer
from ..config_cascade import ConfigCascadeError, resolve as config_resolve
from ..context import Context
from ..db import transaction, utc_now
from ..ingest import IngestError, LocalOnlyEngineMissingError, extract_text_from_blob
from ..security.secrets import TenantSecretStore
from ..skill_primitives import capture_informal_interaction

MAX_MEDIA_BYTES = 25 * 1024 * 1024  # WhatsApp media size ceiling
MEDIA_TIMEOUT_S = 30.0


class WhatsAppInboundError(Exception):
    """Fail-closed error from the WhatsApp inbound connector."""


class _WhatsAppSecretStore:
    """Encrypted per-tenant/per-phone-number secrets for WhatsApp webhooks."""

    def __init__(self, path: Path | None = None) -> None:
        if path is None:
            from ..router.config_store import get_config_dir

            path = get_config_dir() / "whatsapp_secrets.json"
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
        return self._cipher.decrypt_for_tenant(ctx, envelope)

    def find_verify_token(
        self,
        verify_token: str,
    ) -> tuple[str, str] | None:
        """Return (tenant_id, phone_number_id) for a matching verify_token."""

        data = self._load()
        for tenant_id, tenant_secrets in data.items():
            ctx = Context(
                workspace_id="__system__",
                tenant_id=tenant_id,
                user_id="webhook",
                actor_id="webhook",
            )
            for namespace_key, envelope in tenant_secrets.items():
                if not namespace_key.endswith("/verify_token"):
                    continue
                candidate = self._cipher.decrypt_for_tenant(ctx, envelope)
                if candidate == verify_token:
                    # namespace_key = connectors/whatsapp/<phone_number_id>/verify_token
                    phone_number_id = namespace_key.split("/")[-2]
                    return tenant_id, phone_number_id
        return None


def _secret_store() -> _WhatsAppSecretStore:
    return _WhatsAppSecretStore()


def set_whatsapp_secret(
    ctx: Context,
    phone_number_id: str,
    suffix: str,
    plaintext: str | None,
) -> None:
    """Store an encrypted WhatsApp secret for ``phone_number_id``."""

    _secret_store().set_secret(ctx, phone_number_id, suffix, plaintext)


def get_whatsapp_secret(
    ctx: Context,
    phone_number_id: str,
    suffix: str,
) -> str | None:
    """Read an encrypted WhatsApp secret for ``phone_number_id``."""

    return _secret_store().get_secret(ctx, phone_number_id, suffix)


@dataclass(frozen=True, slots=True)
class WhatsAppTarget:
    tenant_id: str
    workspace_id: str
    phone_number_id: str


def register_whatsapp_number(
    ctx: Context,
    conn: Any,
    phone_number_id: str,
    workspace_id: str,
) -> None:
    """Register ``phone_number_id`` as an inbound WhatsApp number for a tenant."""

    if not ctx.tenant_id:
        raise WhatsAppInboundError("A tenant context is required")

    with transaction(conn, ctx=ctx):
        conn.execute(
            """
            INSERT INTO tenant_settings (tenant_id, key, value_json, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(tenant_id, key) DO UPDATE SET
                value_json = excluded.value_json,
                updated_at = excluded.updated_at
            """,
            (
                ctx.tenant_id,
                f"whatsapp.number.{phone_number_id}",
                json.dumps({"workspace_id": workspace_id}, ensure_ascii=False),
                utc_now(),
            ),
        )


def resolve_whatsapp_target(conn: Any, phone_number_id: str) -> WhatsAppTarget:
    """Resolve a registered phone number to its tenant/workspace."""

    row = conn.execute(
        """
        SELECT tenant_id, value_json FROM tenant_settings
        WHERE key = ?
        LIMIT 1
        """,
        (f"whatsapp.number.{phone_number_id}",),
    ).fetchone()
    if row is None:
        raise WhatsAppInboundError(
            f"WhatsApp number not registered: {phone_number_id}"
        )
    value = json.loads(row["value_json"])
    workspace_id = value.get("workspace_id")
    if not workspace_id:
        raise WhatsAppInboundError(
            f"WhatsApp number mapping malformed: {phone_number_id}"
        )
    return WhatsAppTarget(
        tenant_id=row["tenant_id"],
        workspace_id=workspace_id,
        phone_number_id=phone_number_id,
    )


def is_whatsapp_enabled(conn: Any, ctx: Context) -> bool:
    """Return the tenant-scoped inbound WhatsApp feature flag."""

    try:
        value = config_resolve(conn, ctx, "whatsapp_inbound.enabled", False)
    except ConfigCascadeError:
        return False
    return bool(value)


def verify_signature(
    body: bytes,
    signature_header: str | None,
    app_secret: str,
) -> None:
    """Validate Meta's X-Hub-Signature-256 header."""

    if not signature_header:
        raise WhatsAppInboundError("Missing signature")
    expected = "sha256=" + hmac.new(
        app_secret.encode("utf-8"), body, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected, signature_header):
        raise WhatsAppInboundError("Invalid signature")


def _download_media(url: str, access_token: str) -> bytes:
    """Download a WhatsApp media blob using the Graph API access token."""

    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "FaberLoom-WhatsApp-Inbound/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=MEDIA_TIMEOUT_S) as resp:  # noqa: S310
            return resp.read(MAX_MEDIA_BYTES)
    except urllib.error.URLError as exc:
        raise WhatsAppInboundError(f"Media download failed: {exc}") from exc


def _transcribe_audio(audio_bytes: bytes) -> str:
    """Transcribe a WhatsApp audio blob using the local Whisper pipeline."""

    try:
        return extract_text_from_blob(
            blob=audio_bytes,
            ingest_type="audio",
            require_local=False,
        )
    except LocalOnlyEngineMissingError as exc:
        raise WhatsAppInboundError(f"Whisper not available: {exc}") from exc
    except IngestError as exc:
        raise WhatsAppInboundError(f"Audio transcription failed: {exc}") from exc


def _process_message(
    ctx: Context,
    conn: Any,
    phone_number_id: str,
    msg: dict[str, Any],
) -> dict[str, Any]:
    """Process a single WhatsApp message and return the capture result."""

    msg_id = msg.get("id")
    if not msg_id:
        raise WhatsAppInboundError("Message without id")

    msg_type = msg.get("type", "unknown")
    if msg_type == "text":
        raw_text = msg.get("text", {}).get("body", "")
    elif msg_type == "audio":
        audio_info = msg.get("audio", {})
        url = audio_info.get("url")
        access_token = get_whatsapp_secret(ctx, phone_number_id, "access_token")
        if not url or not access_token:
            raise WhatsAppInboundError("Audio media not configured")
        audio_bytes = _download_media(url, access_token)
        raw_text = _transcribe_audio(audio_bytes)
    else:
        raise WhatsAppInboundError(f"Unsupported message type: {msg_type}")

    if not raw_text or not raw_text.strip():
        raise WhatsAppInboundError("Empty message")

    with transaction(conn, ctx=ctx):
        result = capture_informal_interaction(
            ctx,
            conn,
            raw_text=raw_text,
            source_type="whatsapp",
            source_locator=msg_id,
        )
        event = audit_writer.write(
            ctx,
            conn,
            action="whatsapp.message_received",
            payload={
                "phone_number_id": phone_number_id,
                "wa_msg_id": msg_id,
                "draft_id": result["draft_id"],
                "type": msg_type,
            },
            correlation_id=msg_id,
            mirror_jsonl=False,
        )

    try:
        audit_writer.mirror(event)
    except Exception:  # pragma: no cover - mirror is best-effort
        pass

    return result


def process_whatsapp_payload(
    conn: Any,
    payload: dict[str, Any],
    body: bytes,
    signature_header: str | None,
) -> dict[str, Any]:
    """Process a signed WhatsApp webhook payload.

    Raises ``WhatsAppInboundError`` for any fail-closed condition.
    """

    entry = payload.get("entry", [{}])[0]
    changes = entry.get("changes", [{}])[0]
    value = changes.get("value", {})
    phone_number_id = value.get("metadata", {}).get("phone_number_id")
    if not phone_number_id:
        return {"status": "ignored", "reason": "no_phone_number_id"}

    target = resolve_whatsapp_target(conn, phone_number_id)
    ctx = Context(
        workspace_id=target.workspace_id,
        tenant_id=target.tenant_id,
        user_id="whatsapp",
        actor_id="webhook",
        actor_role_at_decision="external",
    )

    if not is_whatsapp_enabled(conn, ctx):
        raise WhatsAppInboundError("whatsapp_inbound_disabled")

    app_secret = get_whatsapp_secret(ctx, phone_number_id, "app_secret")
    if not app_secret:
        raise WhatsAppInboundError("app_secret not configured")

    verify_signature(body, signature_header, app_secret)

    messages = value.get("messages", [])
    results: list[dict[str, Any]] = []
    errors: list[str] = []
    for msg in messages:
        try:
            results.append(_process_message(ctx, conn, phone_number_id, msg))
        except WhatsAppInboundError as exc:
            errors.append(str(exc))
            # Audit the failure but keep processing remaining messages.
            try:
                event = audit_writer.write(
                    ctx,
                    conn,
                    action="whatsapp.message_failed",
                    payload={
                        "phone_number_id": phone_number_id,
                        "wa_msg_id": msg.get("id"),
                        "error": str(exc),
                        "type": msg.get("type"),
                    },
                    correlation_id=msg.get("id"),
                    mirror_jsonl=False,
                )
                try:
                    audit_writer.mirror(event)
                except Exception:
                    pass
            except Exception:
                pass

    if errors and not results:
        raise WhatsAppInboundError("; ".join(errors))

    return {
        "status": "ok",
        "processed": len(results),
        "errors": errors,
        "results": results,
    }
