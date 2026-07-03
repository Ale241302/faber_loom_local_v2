"""Draft generation for M13."""
from __future__ import annotations

import hashlib
import json
from datetime import timedelta
from typing import Any

from django.conf import settings
from django.utils import timezone

from apps.bootstrap.models import VoiceProfile
from apps.drafts.models import Channel, Draft, DraftStatus, EvidenceBundle
from apps.events.emit import emit_event
from apps.tasks.models import Task


class DraftGenerator:
    """Generate a human-gated draft from a Task."""

    @classmethod
    def generate(cls, task: Task) -> Draft:
        tenant_id = str(task.tenant_id)
        voice = cls._voice_for_tenant(task.tenant_id)

        original_content = cls._build_original_content(task, voice)
        bundle = cls._build_evidence_bundle(task, original_content)

        draft = Draft.objects.create(
            tenant=task.tenant,
            task=task,
            status=DraftStatus.PENDING,
            original_content=original_content,
            evidence_bundle=bundle,
            channel=cls._default_channel(task),
            recipient=cls._default_recipient(task),
            expires_at=timezone.now() + timedelta(hours=settings.DRAFT_TTL_HOURS),
        )

        emit_event(
            tenant_id=tenant_id,
            event_type="draft.generated",
            payload={
                "draft_id": str(draft.id),
                "task_id": str(task.id),
                "channel": draft.channel,
            },
        )
        return draft

    @classmethod
    def _voice_for_tenant(cls, tenant_id) -> VoiceProfile | None:
        try:
            return VoiceProfile.objects.filter(tenant_id=tenant_id, is_default=True).first()
        except Exception:
            return None

    @classmethod
    def _build_original_content(cls, task: Task, voice: VoiceProfile | None) -> dict[str, Any]:
        payload = task.payload or {}
        greeting = voice.greeting if voice else "Estimado cliente,"
        signature = voice.signature if voice else "Saludos,\nFaberLoom"
        tone = voice.tone if voice else "profesional"

        # E1: simple RFQ/quote template.
        lines = payload.get("lines", [payload]) or [payload]
        subject = payload.get("subject", "Propuesta FaberLoom")
        body_lines = [
            greeting,
            "",
            f"Asunto: {subject}",
            "",
            "Resumen de la propuesta:",
        ]
        for line in lines:
            if isinstance(line, dict):
                desc = line.get("description") or line.get("item") or "Item"
                qty = line.get("quantity", 1)
                price = line.get("unit_price", 0)
                body_lines.append(f"- {desc}: {qty} x ${price}")
            else:
                body_lines.append(f"- {line}")

        body_lines.extend([
            "",
            "Por favor confirme para proceder.",
            "",
            signature,
        ])

        return {
            "subject": subject,
            "body": "\n".join(body_lines),
            "tone": tone,
            "source_payload": payload,
        }

    @classmethod
    def _build_evidence_bundle(cls, task: Task, original_content: dict[str, Any]) -> EvidenceBundle:
        payload = task.payload or {}
        lines = payload.get("lines", [payload]) or [payload]

        bundle_json = {
            "task_id": str(task.id),
            "agent_id": task.agent_id,
            "payload": payload,
            "generated_at": timezone.now().isoformat(),
            "line_items": [
                {
                    "description": line.get("description") if isinstance(line, dict) else str(line),
                    "quantity": line.get("quantity", 1) if isinstance(line, dict) else 1,
                    "unit_price": line.get("unit_price", 0) if isinstance(line, dict) else 0,
                }
                for line in lines
            ],
        }
        bundle_text = json.dumps(bundle_json, sort_keys=True, ensure_ascii=False)
        bundle_hash = hashlib.sha256(bundle_text.encode("utf-8")).hexdigest()

        client_view = {
            "subject": original_content.get("subject"),
            "body": original_content.get("body"),
        }
        internal_view = {
            "bundle_hash": bundle_hash,
            "line_items": bundle_json["line_items"],
            "privacy_classification": "N2",
        }

        return EvidenceBundle.objects.create(
            tenant=task.tenant,
            task=task,
            bundle_json=bundle_json,
            bundle_hash=bundle_hash,
            client_view=client_view,
            internal_view=internal_view,
            privacy_classification="N2",
        )

    @classmethod
    def _default_channel(cls, task: Task) -> str:
        payload = task.payload or {}
        return payload.get("source_type", Channel.EMAIL)

    @classmethod
    def _default_recipient(cls, task: Task) -> str:
        payload = task.payload or {}
        return payload.get("recipient", payload.get("from_email", ""))
