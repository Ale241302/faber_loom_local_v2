"""Backward-compatible re-export of the M15 event writer."""
from __future__ import annotations

from apps.events.outbox import emit_event

__all__ = ["emit_event"]
