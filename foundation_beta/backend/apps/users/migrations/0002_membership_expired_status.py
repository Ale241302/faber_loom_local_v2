"""Add expired status to Membership."""
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="membership",
            name="status",
            field=models.CharField(
                choices=[
                    ("invited", "Invited"),
                    ("active", "Active"),
                    ("suspended", "Suspended"),
                    ("revoked", "Revoked"),
                    ("expired", "Expired"),
                ],
                default="invited",
                max_length=16,
            ),
        ),
    ]
