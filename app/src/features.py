"""Feature flags for optional FaberLoom capabilities.

Flags are read from environment variables at call time so deployments can
enable/disable surfaces without code changes.
"""

from __future__ import annotations

import os


def is_email_connector_enabled() -> bool:
    """Return True when the SL5 IMAP/SMTP connector surface is enabled.

    Controlled by ``FABERLOOM_ENABLE_EMAIL_CONNECTOR`` (default ``false``).
    """

    return os.getenv("FABERLOOM_ENABLE_EMAIL_CONNECTOR", "false").lower() in {
        "1",
        "true",
        "yes",
    }


def is_shared_instance() -> bool:
    """Return True when this deployment is the shared internal instance.

    In shared mode the mail connector refuses legacy/global environment
    credentials and requires per-user app-password configuration.

    Controlled by ``FABERLOOM_SHARED_INSTANCE`` (default ``false``).
    """

    return os.getenv("FABERLOOM_SHARED_INSTANCE", "false").lower() in {
        "1",
        "true",
        "yes",
    }
