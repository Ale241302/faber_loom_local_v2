"""KB vs Letta memory conflict guard (M17)."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ConflictCheckResult:
    conflict: bool
    reason: str = ""
    kb_source: str = ""
    kb_hash: str = ""


class MemoryConflictGuard:
    """Ensure KB VIGENTE always wins over a proposed persistent memory.

    E1 implementation: token overlap between the proposed memory text and the
    retrieved KB chunks. A conflict is reported when overlap ratio exceeds the
    configured threshold for any chunk.
    """

    DEFAULT_THRESHOLD = 0.5

    @classmethod
    def _tokens(cls, text: str) -> set[str]:
        return set(text.lower().split())

    @classmethod
    def check(
        cls,
        proposed_content: dict[str, Any],
        kb_chunks: list[dict[str, Any]],
        threshold: float | None = None,
    ) -> ConflictCheckResult:
        threshold = threshold if threshold is not None else cls.DEFAULT_THRESHOLD
        proposed_text = json.dumps(proposed_content, sort_keys=True)
        proposed_tokens = cls._tokens(proposed_text)
        if not proposed_tokens:
            return ConflictCheckResult(conflict=False)

        for chunk in kb_chunks:
            chunk_text = chunk.get("text") if isinstance(chunk, dict) else str(chunk)
            if not chunk_text:
                continue
            chunk_tokens = cls._tokens(chunk_text)
            if not chunk_tokens:
                continue
            overlap = proposed_tokens & chunk_tokens
            ratio = len(overlap) / len(proposed_tokens)
            if ratio >= threshold:
                kb_source = chunk.get("source", "kb") if isinstance(chunk, dict) else "kb"
                kb_hash = hashlib.sha256(chunk_text.encode()).hexdigest()
                return ConflictCheckResult(
                    conflict=True,
                    reason=(
                        f"Proposed memory overlaps {ratio:.0%} with KB source "
                        f"'{kb_source}' (threshold {threshold:.0%})"
                    ),
                    kb_source=kb_source,
                    kb_hash=kb_hash,
                )
        return ConflictCheckResult(conflict=False)
