# Generated manually for M17 Memory Letta
from __future__ import annotations

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("tenants", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MemoryItem",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("agent_id", models.CharField(max_length=128)),
                ("task_id", models.CharField(blank=True, max_length=128)),
                ("layer", models.CharField(max_length=16)),
                ("namespace", models.CharField(max_length=255)),
                ("content_hash", models.CharField(blank=True, max_length=64)),
                ("status", models.CharField(max_length=16)),
                ("validity_metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "promoted_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
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
                "db_table": "memory_items",
            },
        ),
        migrations.CreateModel(
            name="MemoryConflict",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("kb_source", models.CharField(max_length=255)),
                ("kb_hash", models.CharField(max_length=64)),
                ("reason", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "memory_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="conflicts",
                        to="memory.memoryitem",
                    ),
                ),
                (
                    "resolved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
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
                "db_table": "memory_conflicts",
            },
        ),
        migrations.AddIndex(
            model_name="memoryitem",
            index=models.Index(
                fields=["tenant", "agent_id", "layer", "status"],
                name="idx_memory_agent_layer_status",
            ),
        ),
        migrations.AddIndex(
            model_name="memoryitem",
            index=models.Index(
                fields=["namespace", "status"],
                name="idx_memory_namespace_status",
            ),
        ),
        migrations.AddIndex(
            model_name="memoryconflict",
            index=models.Index(
                fields=["tenant", "memory_item"],
                name="idx_conflict_tenant_memory",
            ),
        ),
    ]
