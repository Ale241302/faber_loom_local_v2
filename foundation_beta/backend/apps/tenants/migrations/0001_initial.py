# Generated manually for Foundation Beta M16
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Tenant",
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
                ("slug", models.SlugField(unique=True)),
                ("legal_name", models.CharField(max_length=255)),
                ("commercial_name", models.CharField(blank=True, max_length=255)),
                ("vertical_spec_object_id", models.CharField(max_length=255)),
                ("plan_tier", models.CharField(max_length=64)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("setup", "Setup"),
                            ("active", "Active"),
                            ("suspended", "Suspended"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="setup",
                        max_length=16,
                    ),
                ),
                ("config_json", models.JSONField(default=dict)),
                (
                    "dpa_state",
                    models.CharField(
                        choices=[
                            ("missing", "Missing"),
                            ("signed", "Signed"),
                            ("blocked", "Blocked"),
                        ],
                        default="missing",
                        max_length=16,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "tenants",
            },
        ),
        migrations.AddIndex(
            model_name="tenant",
            index=models.Index(fields=["slug"], name="idx_tenants_slug"),
        ),
        migrations.AddIndex(
            model_name="tenant",
            index=models.Index(fields=["status"], name="idx_tenants_status"),
        ),
        migrations.CreateModel(
            name="TenantPlanFeatures",
            fields=[
                (
                    "tenant",
                    models.OneToOneField(
                        db_column="tenant_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="tenants.tenant",
                    ),
                ),
                (
                    "data_class_ceiling",
                    models.CharField(
                        choices=[
                            ("N0", "N0"),
                            ("N1", "N1"),
                            ("N2", "N2"),
                            ("N3", "N3"),
                            ("N4", "N4"),
                        ],
                        default="N2",
                        max_length=2,
                    ),
                ),
                ("max_seats", models.PositiveIntegerField(default=2)),
                ("allow_agent_composition", models.BooleanField(default=False)),
                ("allow_tools_in_skills", models.BooleanField(default=False)),
                ("allow_email_connector", models.BooleanField(default=False)),
                ("allow_whatsapp_connector", models.BooleanField(default=False)),
            ],
            options={
                "db_table": "tenant_plan_features",
            },
        ),
        migrations.AddIndex(
            model_name="tenantplanfeatures",
            index=models.Index(fields=["tenant"], name="idx_tpf_tenant_id"),
        ),
    ]
