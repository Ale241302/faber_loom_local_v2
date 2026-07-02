"""Initial migration for RBAC Role model."""
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Role",
            fields=[
                (
                    "id",
                    models.CharField(max_length=32, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=64)),
                ("permissions", models.JSONField(default=dict)),
            ],
            options={
                "db_table": "roles",
            },
        ),
    ]
