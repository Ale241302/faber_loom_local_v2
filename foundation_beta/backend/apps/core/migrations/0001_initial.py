# Generated manually for Foundation Beta M16
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("tenants", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SampleItem",
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
                ("name", models.CharField(max_length=255)),
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
                "db_table": "sample_items",
            },
        ),
        migrations.AddIndex(
            model_name="sampleitem",
            index=models.Index(fields=["tenant"], name="idx_sample_items_tenant_id"),
        ),
    ]
