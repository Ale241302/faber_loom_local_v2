"""Purge published outbox rows older than OUTBOX_RETENTION_DAYS."""
from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.events.models import Outbox, OutboxStatus


class Command(BaseCommand):
    help = "Delete published outbox rows older than OUTBOX_RETENTION_DAYS."

    def handle(self, *args, **options):
        retention_days = int(getattr(settings, "OUTBOX_RETENTION_DAYS", 7))
        cutoff = timezone.now() - timezone.timedelta(days=retention_days)
        deleted, _ = Outbox.objects.filter(
            status=OutboxStatus.PUBLISHED,
            created_at__lt=cutoff,
        ).delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} published outbox rows."))
