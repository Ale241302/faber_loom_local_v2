"""Reusable SMTP HITL connector for E3-0.

This module wraps Python's ``smtplib`` with the extra safety guards required
before any external effect:

- Credentials are passed explicitly; nothing is read from the global environment.
- A ``confirmation_token`` must be supplied on the second call (double check).
- ``send_email`` can operate in ``dry_run=True`` mode to validate config/headers
  without opening the SMTP connection.
- Passwords are never logged or returned.

The higher-level API endpoints are still responsible for persisting the pending
outbox record, showing a preview to the user, and calling this connector only
after the user has confirmed.
"""

from __future__ import annotations

import hashlib
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Any


class SMTPError(Exception):
    """Raised when an SMTP operation cannot be completed safely."""


@dataclass(frozen=True, slots=True)
class SMTPConfig:
    server: str
    port: int
    username: str
    password: str
    use_ssl: bool = True
    from_email: str | None = None


def confirmation_token(payload: dict[str, Any]) -> str:
    """Deterministic token the UI must echo back before sending.

    The payload should contain enough context to make a replay useless outside
    the current session (e.g. outbox id, recipient, timestamp rounded to minute).
    """

    canonical = "|".join(f"{k}={v}" for k, v in sorted(payload.items()))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def send_email(
    config: SMTPConfig,
    to: str,
    subject: str,
    body: str,
    *,
    confirmation_token_value: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Send an email via SMTP after an optional two-step confirmation flow.

    Pass ``confirmation_token_value`` on the second (confirmed) call. If it is
    ``None``, the function still validates the message and config but only
    returns the expected token; in dry-run mode no network connection is opened.

    Returns a dict with ``sent`` (bool), ``confirmation_token`` (str) and
    ``dry_run`` (bool).
    """

    if not config.server or not config.username or not config.password:
        raise SMTPError("Incomplete SMTP configuration")

    if "@" not in to:
        raise SMTPError(f"Invalid recipient address: {to}")

    from_addr = config.from_email or config.username
    expected_token = confirmation_token(
        {
            "to": to,
            "from": from_addr,
            "subject": subject,
        }
    )

    if confirmation_token_value is None or dry_run:
        return {
            "sent": False,
            "confirmation_token": expected_token,
            "dry_run": dry_run,
        }

    if confirmation_token_value != expected_token:
        raise SMTPError("Confirmation token mismatch; send aborted")

    msg = EmailMessage()
    msg["From"] = from_addr
    msg["To"] = to
    msg["Subject"] = subject or ""
    msg.set_content(body)

    try:
        if config.use_ssl:
            with smtplib.SMTP_SSL(config.server, config.port) as smtp:
                smtp.login(config.username, config.password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(config.server, config.port) as smtp:
                smtp.starttls()
                smtp.login(config.username, config.password)
                smtp.send_message(msg)
    except smtplib.SMTPException as exc:
        raise SMTPError(f"SMTP error: {exc}") from exc
    except OSError as exc:
        raise SMTPError(f"SMTP connection error: {exc}") from exc

    return {"sent": True, "confirmation_token": expected_token, "dry_run": False}


def verify_smtp_config(config: SMTPConfig) -> dict[str, Any]:
    """Open an SMTP connection and authenticate without sending a message."""

    if not config.server or not config.username or not config.password:
        raise SMTPError("Incomplete SMTP configuration")

    try:
        if config.use_ssl:
            server = smtplib.SMTP_SSL(config.server, config.port)
        else:
            server = smtplib.SMTP(config.server, config.port)
            server.starttls()
        server.login(config.username, config.password)
        server.quit()
    except smtplib.SMTPException as exc:
        raise SMTPError(f"SMTP verification error: {exc}") from exc
    except OSError as exc:
        raise SMTPError(f"SMTP connection error: {exc}") from exc

    return {"ok": True, "server": config.server, "username": config.username}
