"""SpaceLoom SL5: read-only IMAP + SMTP send connector.

Credentials are read from environment variables at call time. Passwords are
never logged or returned.
"""

from __future__ import annotations

import imaplib
import os
import re
import smtplib
from email.header import decode_header, make_header
from email.message import EmailMessage
from email.parser import BytesParser
from email.utils import parseaddr
from typing import Any


# Minimal HTML tag stripper used when a message only provides text/html.
_HTML_TAG_RE = re.compile(r"<[^>]+>")
# Collapse whitespace produced by tag stripping.
_WS_RE = re.compile(r"\s+")


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _imap_credentials() -> dict[str, Any]:
    return {
        "server": _require_env("SPACELOOM_IMAP_SERVER"),
        "port": int(_require_env("SPACELOOM_IMAP_PORT")),
        "username": _require_env("SPACELOOM_IMAP_USER"),
        "password": _require_env("SPACELOOM_IMAP_PASSWORD"),
    }


def _smtp_credentials() -> dict[str, Any]:
    return {
        "server": _require_env("SPACELOOM_SMTP_SERVER"),
        "port": int(_require_env("SPACELOOM_SMTP_PORT")),
        "username": _require_env("SPACELOOM_IMAP_USER"),
        "password": _require_env("SPACELOOM_IMAP_PASSWORD"),
    }


def _decode_header_value(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        header = make_header(decode_header(value))
        return str(header)
    except Exception:
        return value


def _normalize_address(header_value: str | None) -> str | None:
    """Return a clean e-mail address from a From/To header.

    Handles values like 'Client <client@example.com>' and strips
    stray whitespace or angle brackets.
    """

    if header_value is None:
        return None
    raw = header_value.strip()
    if not raw:
        return None
    # email.utils.parseaddr returns (display_name, addr_spec).
    _name, addr = parseaddr(raw)
    return addr.lower().strip() or raw.lower().strip()


def _strip_html_to_text(html: str) -> str:
    """Remove HTML tags, scripts/styles and collapse whitespace."""

    # Drop script/style blocks first.
    text = re.sub(r"<(script|style)[^>]*>[^<]*</(script|style)>", " ", html, flags=re.IGNORECASE)
    text = _HTML_TAG_RE.sub(" ", text)
    text = _WS_RE.sub(" ", text)
    return text.strip()


def _extract_body_text(msg: EmailMessage) -> str:
    """Return the first text/plain payload, falling back to text/html as text."""

    if msg.is_multipart():
        plain_part: EmailMessage | None = None
        html_part: EmailMessage | None = None
        for part in msg.walk():
            if part.get_content_disposition() == "attachment":
                continue
            content_type = part.get_content_type()
            if content_type == "text/plain" and plain_part is None:
                plain_part = part
            elif content_type == "text/html" and html_part is None:
                html_part = part
        if plain_part is not None:
            return str(plain_part.get_payload(decode=True) or b"", errors="replace").strip()
        if html_part is not None:
            html = str(html_part.get_payload(decode=True) or b"", errors="replace")
            return _strip_html_to_text(html)
        return ""

    if msg.get_content_type() == "text/plain":
        return str(msg.get_payload(decode=True) or b"", errors="replace").strip()
    if msg.get_content_type() == "text/html":
        html = str(msg.get_payload(decode=True) or b"", errors="replace")
        return _strip_html_to_text(html)
    return ""


def fetch_unread_messages(
    server: str,
    port: int,
    username: str,
    password: str,
    mailbox: str = "INBOX",
    max_messages: int = 10,
) -> list[dict[str, Any]]:
    """Fetch unread messages from an IMAP mailbox using SSL.

    Returns a list of dicts with keys: uid, subject, sender, body_text,
    raw_payload. Passwords are never logged.
    """

    try:
        with imaplib.IMAP4_SSL(server, port) as mail:
            mail.login(username, password)
            status, _ = mail.select(mailbox)
            if status != "OK":
                raise RuntimeError(f"Could not select mailbox '{mailbox}' on {server}")

            status, data = mail.uid("SEARCH", None, "(UNSEEN)")
            if status != "OK" or data is None:
                return []

            message_uids = data[0].split() if data[0] else []
            messages: list[dict[str, Any]] = []

            for uid in message_uids[:max_messages]:
                status, fetch_data = mail.uid("FETCH", uid, "(RFC822)")
                if status != "OK" or fetch_data is None:
                    continue

                raw_payload: bytes | None = None
                for response_part in fetch_data:
                    if isinstance(response_part, tuple):
                        raw_payload = response_part[1]
                        break

                if raw_payload is None:
                    continue

                parsed = BytesParser().parsebytes(raw_payload)
                subject = _decode_header_value(parsed.get("Subject"))
                sender = _normalize_address(_decode_header_value(parsed.get("From")))
                body_text = _extract_body_text(parsed)

                messages.append(
                    {
                        "uid": uid.decode("ascii", errors="replace"),
                        "subject": subject,
                        "sender": sender,
                        "body_text": body_text,
                        "raw_payload": raw_payload,
                    }
                )

            return messages
    except imaplib.IMAP4.error as exc:
        raise RuntimeError(f"IMAP error: {exc}") from exc
    except OSError as exc:
        raise RuntimeError(f"IMAP connection error: {exc}") from exc


def send_message(
    server: str,
    port: int,
    username: str,
    password: str,
    to: str,
    subject: str,
    body: str,
) -> None:
    """Send an email via SMTP_SSL. This function performs no HITL checks."""

    msg = EmailMessage()
    msg["From"] = username
    msg["To"] = to
    msg["Subject"] = subject or ""
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL(server, port) as smtp:
            smtp.login(username, password)
            smtp.send_message(msg)
    except smtplib.SMTPException as exc:
        raise RuntimeError(f"SMTP error: {exc}") from exc
    except OSError as exc:
        raise RuntimeError(f"SMTP connection error: {exc}") from exc
