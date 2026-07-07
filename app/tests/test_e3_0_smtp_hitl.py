"""E3-0 — SMTP HITL connector safety tests."""

from __future__ import annotations

import pytest

from app.src.connectors.smtp import SMTPConfig, SMTPError, send_email


def _config() -> SMTPConfig:
    return SMTPConfig(
        server="smtp.example.com",
        port=465,
        username="user@example.com",
        password="secret",
        use_ssl=True,
        from_email="sender@example.com",
    )


def test_send_email_dry_run_returns_token() -> None:
    result = send_email(
        _config(),
        to="to@example.com",
        subject="Hello",
        body="body",
        dry_run=True,
    )
    assert result["sent"] is False
    assert result["dry_run"] is True
    assert len(result["confirmation_token"]) == 16


def test_send_email_without_token_returns_token_but_does_not_send() -> None:
    result = send_email(
        _config(),
        to="to@example.com",
        subject="Hello",
        body="body",
    )
    assert result["sent"] is False
    assert result["dry_run"] is False
    assert len(result["confirmation_token"]) == 16


def test_send_email_with_bad_token_rejected() -> None:
    with pytest.raises(SMTPError, match="Confirmation token mismatch"):
        send_email(
            _config(),
            to="to@example.com",
            subject="Hello",
            body="body",
            confirmation_token_value="bad-token",
        )


def test_send_email_invalid_recipient_rejected() -> None:
    with pytest.raises(SMTPError, match="Invalid recipient"):
        send_email(_config(), to="not-an-email", subject="Hello", body="body")


def test_send_email_incomplete_config_rejected() -> None:
    bad_config = SMTPConfig(server="", port=0, username="", password="")
    with pytest.raises(SMTPError, match="Incomplete SMTP configuration"):
        send_email(bad_config, to="to@example.com", subject="Hello", body="body")
