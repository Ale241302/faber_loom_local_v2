"""E5-4 — ATV smoke script fail-closed and structure tests."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


ATV_SMOKE = Path(__file__).parent.parent.parent / "app" / "scripts" / "atv_smoke.py"


def test_atv_smoke_fails_closed_without_credentials() -> None:
    """The script must refuse to run if any required env var is missing."""

    env = os.environ.copy()
    for key in ["ATV_USERNAME", "ATV_PASSWORD", "ATV_CERT_PATH", "ATV_CERT_PIN"]:
        env.pop(key, None)
    env["ATV_CERT_PATH"] = "/nonexistent/cert.p12"

    proc = subprocess.run(
        [sys.executable, str(ATV_SMOKE)],
        capture_output=True,
        text=True,
        env=env,
        cwd=Path(__file__).parent.parent.parent,
    )
    assert proc.returncode == 1
    assert "Faltan variables de entorno requeridas" in proc.stderr


def test_atv_smoke_fails_closed_with_missing_certificate() -> None:
    """The script must refuse to run if the configured .p12 does not exist."""

    env = os.environ.copy()
    env["ATV_USERNAME"] = "test"
    env["ATV_PASSWORD"] = "test"
    env["ATV_CERT_PATH"] = "/nonexistent/cert.p12"
    env["ATV_CERT_PIN"] = "1234"

    proc = subprocess.run(
        [sys.executable, str(ATV_SMOKE)],
        capture_output=True,
        text=True,
        env=env,
        cwd=Path(__file__).parent.parent.parent,
    )
    assert proc.returncode == 1
    assert "No existe el certificado" in proc.stderr
