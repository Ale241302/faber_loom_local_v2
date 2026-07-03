"""Channel sender for drafts (E1: email via Django backend, WhatsApp stub)."""
from __future__ import annotations

from django.conf import settings
from django.core.mail import send_mail

from apps.bootstrap.models import EmailBinding
from apps.drafts.models import Channel, Draft


class ChannelSender:
    """Send an approved draft through its configured channel."""

    @classmethod
    def send(cls, draft: Draft) -> bool:
        if draft.channel == Channel.EMAIL:
            return cls._send_email(draft)
        if draft.channel == Channel.WHATSAPP:
            return cls._send_whatsapp(draft)
        return False

    @classmethod
    def _send_email(cls, draft: Draft) -> bool:
        content = draft.edited_content or draft.original_content
        subject = content.get("subject", "FaberLoom draft")
        body = content.get("body", "")
        recipient = draft.recipient
        if not recipient:
            return False

        # E1: use the default EmailBinding account as sender if available.
        from_email = settings.DEFAULT_FROM_EMAIL
        try:
            binding = EmailBinding.objects.filter(
                tenant_id=draft.tenant_id, is_default=True
            ).first()
            if binding:
                from_email = binding.account
        except Exception:
            pass

        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=from_email,
                recipient_list=[recipient],
                fail_silently=False,
            )
            return True
        except Exception:
            return False

    @classmethod
    def _send_whatsapp(cls, draft: Draft) -> bool:
        # E1 stub.
        return False
