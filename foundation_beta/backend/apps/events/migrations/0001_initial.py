"""Initial migration for events app."""
import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("tenants", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="OutboxEvent",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("event_type", models.CharField(max_length=128)),
                ("payload", models.JSONField(default=dict)),
                ("correlation_id", models.CharField(blank=True, max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        db_column="tenant_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={
                "db_table": "outbox_events",
            },
        ),
        migrations.AddIndex(
            model_name="outboxevent",
            index=models.Index(
                fields=["tenant", "event_type"], name="idx_outbox_tenant_type"
            ),
        ),
        migrations.AddIndex(
            model_name="outboxevent",
            index=models.Index(fields=["created_at"], name="idx_outbox_created_at"),
        ),
    ]
