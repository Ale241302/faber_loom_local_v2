"""User and membership models for Foundation Beta M08 Auth Session."""
from __future__ import annotations

import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

from apps.tenants.models import Tenant


class UserManager(BaseUserManager):
    def create_user(self, email: str, password: str | None = None, **extra):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra):
        extra.setdefault("is_active", True)
        return self.create_user(email, password, **extra)


class User(AbstractBaseUser):
    """Tenant-agnostic user account."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    # Encrypted TOTP secret (Fernet ciphertext as url-safe base64).
    totp_secret_encrypted = models.TextField(blank=True, null=True)
    # Hashed backup codes (bcrypt hashes); stored as JSON list.
    backup_codes_hashed = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        db_table = "users"

    def __str__(self) -> str:
        return self.email

    def set_password(self, raw_password: str | None) -> None:
        super().set_password(raw_password)
        # Invalidate all active sessions across every tenant when password changes.
        try:
            from apps.auth_session.session import revoke_all_user_sessions

            for membership in self.memberships.all():
                revoke_all_user_sessions(self.id, membership.tenant_id)
        except Exception:
            # Avoid breaking password changes if Redis is down.
            pass


class MembershipStatus(models.TextChoices):
    INVITED = "invited", "Invited"
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    REVOKED = "revoked", "Revoked"


class Membership(models.Model):
    """Many-to-many link between users and tenants with roles."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="memberships")
    roles = models.JSONField(default=list, blank=True)
    active_hat = models.CharField(max_length=64, blank=True)
    status = models.CharField(
        max_length=16, choices=MembershipStatus.choices, default=MembershipStatus.INVITED
    )
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invitations_sent",
    )
    invited_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "memberships"
        unique_together = [("user", "tenant")]
        indexes = [
            models.Index(fields=["user"], name="idx_memberships_user_id"),
            models.Index(fields=["tenant"], name="idx_memberships_tenant_id"),
            models.Index(fields=["tenant", "status"], name="idx_memberships_status"),
        ]
