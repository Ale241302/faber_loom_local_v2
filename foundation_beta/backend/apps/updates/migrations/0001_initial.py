# Generated manually for M20 Auto Update
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
            name="ClientRelease",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("version", models.CharField(max_length=32)),
                ("platform", models.CharField(max_length=16)),
                ("feed_url", models.URLField()),
                ("published_at", models.DateTimeField(auto_now_add=True)),
                ("retired_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("channel", models.CharField(max_length=16)),
            ],
            options={
                "db_table": "client_releases",
            },
        ),
        migrations.CreateModel(
            name="SystemConfig",
            fields=[
                ("key", models.CharField(max_length=64, primary_key=True, serialize=False)),
                ("value", models.TextField()),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "system_configs",
            },
        ),
        migrations.CreateModel(
            name="TenantUpdateChannel",
            fields=[
                ("channel", models.CharField(max_length=16)),
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
                "db_table": "tenant_update_channels",
            },
        ),
        migrations.CreateModel(
            name="ClientVersionTelemetry",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("client_version", models.CharField(max_length=32)),
                ("platform", models.CharField(max_length=16)),
                ("reported_at", models.DateTimeField(auto_now_add=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        db_column="tenant_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tenants.tenant",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        db_column="user_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "client_version_telemetry",
            },
        ),
        migrations.AddIndex(
            model_name="clientrelease",
            index=models.Index(
                fields=["platform", "channel", "published_at"],
                name="idx_releases_platform_channel",
            ),
        ),
        migrations.AddIndex(
            model_name="clientversiontelemetry",
            index=models.Index(
                fields=["tenant", "reported_at"],
                name="idx_telemetry_tenant_reported",
            ),
        ),
    ]
