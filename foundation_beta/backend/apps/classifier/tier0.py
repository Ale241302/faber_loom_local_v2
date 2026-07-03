"""Deterministic Tier 0 classifier."""
from __future__ import annotations

import json
from typing import Any

from apps.classifier.models import Tier0Rule
from apps.classifier.schemas import ActionContext


class Tier0Classifier:
    """Match feed items against deterministic rules before calling the LLM."""

    @classmethod
    def match(cls, feed_item, tenant_id: str) -> ActionContext | None:
        rules = Tier0Rule.objects.filter(
            tenant_id=tenant_id, active=True
        ).order_by("-priority", "created_at")
        for rule in rules:
            if cls._matches(rule.pattern, feed_item.normalized_payload):
                action_data = rule.action_context or {}
                return ActionContext(
                    tenant_id=str(tenant_id),
                    confidence=1.0,
                    **action_data,
                )
        return None

    @classmethod
    def _matches(cls, pattern: dict[str, Any], payload: dict[str, Any]) -> bool:
        """Simple keyword matcher. Rules can define ``keywords`` or ``exact`` conditions."""
        haystack = json.dumps(payload, sort_keys=True, ensure_ascii=False).lower()

        keywords = pattern.get("keywords", [])
        if keywords and not all(str(k).lower() in haystack for k in keywords):
            return False

        exact = pattern.get("exact", {})
        for key, value in exact.items():
            if cls._get_value(payload, key) != value:
                return False

        return True

    @classmethod
    def _get_value(cls, data: Any, path: str) -> Any:
        parts = path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current
