"""Per-IP rate limiting for public endpoints.

Uses the Foundation ``fnd_rate_limits`` table so the limit is shared across
processes and survives restarts. Client IP is read from ``X-Forwarded-For``
first, then ``request.client.host``.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, Request, status


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def check_rate_limit(key: str, max_attempts: int, window_seconds: int) -> None:
    """Increment the counter for *key* and raise 429 if over the limit.

    The window is a fixed sliding bucket: the first attempt inside a window
    sets ``window_until``; once the limit is reached, further attempts are
    rejected until the window expires.
    """

    if max_attempts <= 0:
        return

    from .foundation.core import connect as connect_foundation, utcnow

    conn = connect_foundation()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS fnd_rate_limits (
                key TEXT PRIMARY KEY,
                window_until TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        now = utcnow()
        row = conn.execute(
            "SELECT window_until, attempts FROM fnd_rate_limits WHERE key = ?",
            (key,),
        ).fetchone()

        if row is None or row["window_until"] < now:
            new_until = (datetime.now(timezone.utc) + timedelta(seconds=window_seconds)).isoformat()
            conn.execute(
                """
                INSERT INTO fnd_rate_limits (key, window_until, attempts)
                VALUES (?, ?, 1)
                ON CONFLICT(key) DO UPDATE SET window_until = excluded.window_until,
                                               attempts = excluded.attempts
                """,
                (key, new_until),
            )
            attempts = 1
        else:
            attempts = row["attempts"] + 1
            conn.execute(
                "UPDATE fnd_rate_limits SET attempts = ? WHERE key = ?",
                (attempts, key),
            )
        conn.commit()

        if attempts > max_attempts:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded; please try again later.",
            )
    finally:
        conn.close()


def rate_limit_dependency(
    request: Request,
    *,
    action: str,
    max_attempts: int | None = None,
    window_seconds: int | None = None,
) -> None:
    """FastAPI dependency wrapper around :func:`check_rate_limit`.

    Defaults can be overridden via environment variables or call-site arguments.
    """

    env_prefix = f"FABERLOOM_RATE_LIMIT_{action.upper()}_"
    max_attempts = max_attempts or int(
        os.getenv(f"{env_prefix}MAX", os.getenv("FABERLOOM_RATE_LIMIT_MAX", "5"))
    )
    window_seconds = window_seconds or int(
        os.getenv(f"{env_prefix}WINDOW", os.getenv("FABERLOOM_RATE_LIMIT_WINDOW", "900"))
    )
    ip = _client_ip(request)
    check_rate_limit(f"{action}:{ip}", max_attempts, window_seconds)
