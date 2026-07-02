"""Seed the five canonical RBAC roles."""
from django.db import migrations


CANONICAL_ROLES = [
    (
        "owner",
        "Owner",
        {
            "workloom": "full",
            "workspace": "full",
            "agent_factory": "full",
            "skill_factory": "full",
            "audit": "full",
            "config": "full",
            "users": "full",
        },
    ),
    (
        "admin",
        "Admin",
        {
            "workloom": "full",
            "workspace": "full",
            "agent_factory": "write",
            "skill_factory": "write",
            "audit": "read",
            "config": "write",
            "users": "write",
        },
    ),
    (
        "operator",
        "Operator",
        {
            "workloom": "write",
            "workspace": "write",
            "agent_factory": "none",
            "skill_factory": "none",
            "audit": "read_self",
            "config": "none",
            "users": "none",
        },
    ),
    (
        "supervisor",
        "Supervisor",
        {
            "workloom": "write",
            "workspace": "write",
            "agent_factory": "read",
            "skill_factory": "read",
            "audit": "read",
            "config": "none",
            "users": "none",
        },
    ),
    (
        "viewer",
        "Viewer",
        {
            "workloom": "read",
            "workspace": "read",
            "agent_factory": "none",
            "skill_factory": "none",
            "audit": "read_self",
            "config": "none",
            "users": "none",
        },
    ),
]


def seed_roles(apps, schema_editor):
    Role = apps.get_model("rbac", "Role")
    for role_id, name, permissions in CANONICAL_ROLES:
        Role.objects.update_or_create(
            id=role_id,
            defaults={"name": name, "permissions": permissions},
        )


def clear_roles(apps, schema_editor):
    Role = apps.get_model("rbac", "Role")
    Role.objects.filter(id__in=[r[0] for r in CANONICAL_ROLES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("rbac", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_roles, clear_roles),
    ]
