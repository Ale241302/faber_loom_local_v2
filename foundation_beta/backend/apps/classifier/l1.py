"""LLM-based L1 classifier."""
from __future__ import annotations

import json
import re
from decimal import Decimal
from typing import Any

from django.utils import timezone

import litellm

from apps.classifier.models import ClassificationResult, ClassificationResultStatus
from apps.classifier.schemas import ActionContext
from apps.core.llm import litellm_metadata


class L1Classifier:
    """Classify a feed item using the tenant's active classifier skill."""

    MAX_RETRIES = 3

    @classmethod
    def classify(cls, feed_item, skill: "ClassifierSkill") -> ClassificationResult:
        features = cls._extract_features(feed_item)
        prompt = skill.prompt_template.format(
            payload=feed_item.normalized_payload,
            features=json.dumps(features, ensure_ascii=False),
            work_type_pack="",
        )

        started_at = timezone.now()
        response = None
        last_error = None
        for attempt in range(cls.MAX_RETRIES):
            try:
                response = litellm.completion(
                    model=skill.model_id,
                    messages=[{"role": "user", "content": prompt}],
                    metadata=litellm_metadata(feed_item.tenant_id),
                    timeout=skill.timeout_ms / 1000.0,
                )
                break
            except Exception as exc:
                last_error = exc
                if attempt == cls.MAX_RETRIES - 1:
                    break

        latency_ms = int((timezone.now() - started_at).total_seconds() * 1000)

        if response is None:
            return ClassificationResult.objects.create(
                tenant=feed_item.tenant,
                feed_item=feed_item,
                classifier_skill=skill,
                action_context={"tenant_id": str(feed_item.tenant_id)},
                features=features,
                confidence=Decimal("0.0"),
                status=ClassificationResultStatus.FAILED,
                model_id=skill.model_id,
                latency_ms=latency_ms,
                cost_usd=Decimal("0.0"),
            )

        content = response.choices[0].message.content or ""
        cost_usd = Decimal(str(getattr(response, "_hidden_params", {}).get("response_cost", 0.0)))

        action_context = cls._parse_and_validate(content, skill.output_schema)
        confidence = float(action_context.get("confidence", 0.0))

        return ClassificationResult.objects.create(
            tenant=feed_item.tenant,
            feed_item=feed_item,
            classifier_skill=skill,
            action_context=action_context.to_dict(),
            features=features,
            confidence=Decimal(str(confidence)).quantize(Decimal("0.001")),
            routing_zone=action_context.routing,
            status=ClassificationResultStatus.CLASSIFIED,
            model_id=skill.model_id,
            model_version=skill.active_version,
            latency_ms=latency_ms,
            cost_usd=cost_usd,
        )

    @classmethod
    def _extract_features(cls, feed_item) -> dict[str, Any]:
        payload = feed_item.normalized_payload or {}
        return {
            "task_type_confidence": 0.0,
            "schema_parse_success": True,
            "num_documents": len(payload.get("documents", [])),
            "num_counterparties": len(payload.get("counterparties", [])),
            "jurisdiction_count": len(payload.get("jurisdictions", [])),
            "data_class": feed_item.data_class,
            "tenant_risk_tier": "low",
            "estimated_tokens": 0,
            "expected_latency": 0,
            "business_value": 0,
            "validator_failure_count": 0,
            "prior_case_similarity": 0.0,
            "requires_human_gate": False,
        }

    @classmethod
    def _parse_and_validate(cls, content: str, output_schema: dict[str, Any]) -> ActionContext:
        """Extract JSON from the LLM response and validate against the skill schema."""
        json_text = cls._extract_json(content)
        data = json.loads(json_text)

        # Minimal schema validation: ensure required keys exist.
        required = set(output_schema.get("required", []))
        missing = required - set(data.keys())
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        return ActionContext(
            tenant_id=str(data.get("tenant_id", "")),
            case_id=data.get("case_id"),
            task_type=data.get("task_type", ""),
            data_class=data.get("data_class", "N1"),
            skill_id=data.get("skill_id", ""),
            agent_id=data.get("agent_id", ""),
            confidence=float(data.get("confidence", 0.0)),
            source=data.get("source", ""),
            routing=data.get("routing", "zone_4"),
            sla_minutes=int(data.get("sla_minutes", 60)),
            payload_normalizado=data.get("payload_normalizado", {}),
            requires_human_gate=bool(data.get("requires_human_gate", False)),
            retrieved_chunks=[],
        )

    @classmethod
    def _extract_json(cls, text: str) -> str:
        text = text.strip()
        if text.startswith("{"):
            return text
        match = re.search(r"```(?:json)?\s*({.*?})\s*```", text, re.DOTALL)
        if match:
            return match.group(1)
        raise ValueError("No JSON object found in classifier response")
