"""Initial migration for M14 Outcome Ledger, Gold Samples and Learning Thermometer."""
from __future__ import annotations

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("classifier", "0001_initial"),
        ("drafts", "0001_initial"),
        ("tenants", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="OutcomeLedgerEntry",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("decision", models.CharField(max_length=16)),
                ("diff", models.JSONField(blank=True, default=dict)),
                ("reason", models.TextField(blank=True)),
                ("confidence", models.DecimalField(blank=True, decimal_places=3, max_digits=4, null=True)),
                ("actor_role_at_decision", models.CharField(max_length=32)),
                ("decision_time_ms", models.PositiveIntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("actor_id", models.CharField(max_length=64)),
                (
                    "classification_result",
                    models.ForeignKey(
                        blank=True,
                        db_column="classification_result_id",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="classifier.classificationresult",
                    ),
                ),
                (
                    "draft",
                    models.ForeignKey(
                        blank=True,
                        db_column="draft_id",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="drafts.draft",
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
                "db_table": "outcome_ledger_entries",
            },
        ),
        migrations.CreateModel(
            name="GoldSample",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("agent_id", models.CharField(max_length=255)),
                ("skill_id", models.CharField(blank=True, max_length=255)),
                ("input_json", models.JSONField(default=dict)),
                ("output_json", models.JSONField(default=dict)),
                ("status", models.CharField(max_length=32)),
                ("validations_json", models.JSONField(blank=True, default=dict)),
                ("promoted_at", models.DateTimeField(blank=True, null=True)),
                ("validity_metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "promoter",
                    models.ForeignKey(
                        blank=True,
                        db_column="promoter_id",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="promoted_gold_samples",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "second_approver",
                    models.ForeignKey(
                        blank=True,
                        db_column="second_approver_id",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="second_approved_gold_samples",
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
                "db_table": "gold_samples",
            },
        ),
        migrations.CreateModel(
            name="LearningThermometer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("agent_id", models.CharField(max_length=255)),
                ("score", models.PositiveIntegerField(default=0)),
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
                "db_table": "learning_thermometers",
            },
        ),
        migrations.AddIndex(
            model_name="outcomeledgerentry",
            index=models.Index(fields=["tenant", "decision", "created_at"], name="idx_ledger_tenant_decision"),
        ),
        migrations.AddIndex(
            model_name="goldsample",
            index=models.Index(fields=["tenant", "status", "created_at"], name="idx_gold_tenant_status"),
        ),
        migrations.AddConstraint(
            model_name="learningthermometer",
            constraint=models.UniqueConstraint(fields=["tenant", "agent_id"], name="unique_thermometer_tenant_agent"),
        ),
    ]
