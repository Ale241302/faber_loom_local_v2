"""Grant usage on the audit sequence to the application roles."""
from __future__ import annotations

from django.db import migrations


def grant_sequence_usage(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT rolname FROM pg_roles WHERE rolname IN ('faberloom_app', 'faberloom_backend')"
        )
        for (role_name,) in cursor.fetchall():
            cursor.execute(
                f"GRANT USAGE, SELECT ON SEQUENCE audit_seq TO {role_name};"
            )


def revoke_sequence_usage(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT rolname FROM pg_roles WHERE rolname IN ('faberloom_app', 'faberloom_backend')"
        )
        for (role_name,) in cursor.fetchall():
            cursor.execute(
                f"REVOKE USAGE, SELECT ON SEQUENCE audit_seq FROM {role_name};"
            )


class Migration(migrations.Migration):
    dependencies = [
        ("audit", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(grant_sequence_usage, revoke_sequence_usage),
    ]
