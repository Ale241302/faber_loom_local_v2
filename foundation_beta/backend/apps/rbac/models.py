"""RBAC models for Foundation Beta M09."""
from __future__ import annotations

from django.db import models


class Role(models.Model):
    """Canonical role with a permission matrix per surface."""

    id = models.CharField(primary_key=True, max_length=32)
    name = models.CharField(max_length=64)
    permissions = models.JSONField(default=dict)

    class Meta:
        db_table = "roles"

    def __str__(self) -> str:
        return self.name


class PermissionLevel:
    NONE = "none"
    READ = "read"
    READ_SELF = "read_self"
    WRITE = "write"
    FULL = "full"

    ORDER = [NONE, READ_SELF, READ, WRITE, FULL]

    @classmethod
    def rank(cls, level: str) -> int:
        try:
            return cls.ORDER.index(level)
        except ValueError:
            return -1
