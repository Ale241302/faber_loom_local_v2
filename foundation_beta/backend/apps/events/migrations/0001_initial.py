"""Initial migration for M15 Outbox and EventLog."""
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
            name="Outbox",
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
                ("event_id", models.CharField(max_length=64, unique=True)),
                ("event_type", models.CharField(max_length=128)),
                ("payload_json", models.JSONField(default=dict)),
                ("seq_no", models.BigIntegerField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("published", "Published"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("retry_count", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
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
                "db_table": "outbox",
            },
        ),
        migrations.CreateModel(
            name="EventLog",
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
                ("event_id", models.CharField(max_length=64, unique=True)),
                ("event_type", models.CharField(max_length=128)),
                ("payload_json", models.JSONField(default=dict)),
                ("seq_no", models.BigIntegerField()),
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
                "db_table": "event_log",
            },
        ),
        migrations.AddIndex(
            model_name="outbox",
            index=models.Index(fields=["status", "created_at"], name="idx_outbox_status"),
        ),
        migrations.AddIndex(
            model_name="outbox",
            index=models.Index(fields=["tenant", "status"], name="idx_outbox_tenant"),
        ),
        migrations.AddIndex(
            model_name="eventlog",
            index=models.Index(
                fields=["tenant", "seq_no"], name="idx_event_log_tenant_seq"
            ),
        ),
        migrations.RunSQL(
            sql="CREATE SEQUENCE IF NOT EXISTS global_event_seq;",
            reverse_sql="DROP SEQUENCE IF EXISTS global_event_seq;",
        ),
    ]
