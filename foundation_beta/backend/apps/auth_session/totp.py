"""TOTP and backup-code helpers for M08."""
from __future__ import annotations

import base64
import os
import secrets
from typing import cast

import bcrypt
import pyotp
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def _get_fernet() -> Fernet:
    key = settings.TOTP_ENCRYPTION_KEY
    if not key:
        raise ImproperlyConfigured("TOTP_ENCRYPTION_KEY is not set")
    # Fernet requires a 32-byte url-safe base64-encoded key.
    try:
        return Fernet(key)
    except ValueError as exc:
        raise ImproperlyConfigured("TOTP_ENCRYPTION_KEY must be a valid Fernet key") from exc


def encrypt_secret(plain: str) -> str:
    return _get_fernet().encrypt(plain.encode()).decode()


def decrypt_secret(cipher: str) -> str:
    return _get_fernet().decrypt(cipher.encode()).decode()


def generate_totp_secret() -> str:
    """Return a new random TOTP secret compatible with most authenticator apps."""
    return pyotp.random_base32()


def build_provisioning_uri(user_email: str, secret: str) -> str:
    """Return an otpauth:// URI for QR rendering."""
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=user_email,
        issuer_name=settings.TOTP_ISSUER,
    )


def verify_totp(secret: str, code: str) -> bool:
    """Verify a 6-digit TOTP code with a single-step tolerance."""
    totp = pyotp.TOTP(secret)
    return cast(bool, totp.verify(code, valid_window=1))


def generate_backup_codes(count: int = 10) -> tuple[list[str], list[str]]:
    """Return (plain_codes, hashed_codes)."""
    plain = [secrets.token_urlsafe(8) for _ in range(count)]
    hashed = [_hash_code(c) for c in plain]
    return plain, hashed


def _hash_code(code: str) -> str:
    return bcrypt.hashpw(code.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_backup_code(code: str, hashed_codes: list[str]) -> tuple[bool, list[str]]:
    """Check a backup code and return (matched, updated_hashed_codes)."""
    for hashed in hashed_codes:
        if bcrypt.checkpw(code.encode(), hashed.encode()):
            remaining = [h for h in hashed_codes if h != hashed]
            return True, remaining
    return False, hashed_codes


def generate_login_token() -> str:
    """Opaque token for the intermediate login step."""
    return secrets.token_urlsafe(32)


def generate_email_otp() -> str:
    """Six-digit OTP used only for tests/manual flows (not TOTP)."""
    return f"{secrets.randbelow(1_000_000):06d}"
