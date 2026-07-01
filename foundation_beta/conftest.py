"""Pytest fixtures for Foundation Beta M16 tenant isolation tests."""
from __future__ import annotations

import os
import sys
from uuid import UUID

import pytest

# Ensure backend is on path when running from repo root.
BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "faberloom.settings")
os.environ["TESTING"] = "True"

import django

django.setup()

from cryptography.fernet import Fernet
from django.conf import settings
from django.test import RequestFactory

from apps.core.redis_client import get_redis_client
from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.core.vector import ensure_tenant_partition
from apps.tenants.models import Tenant

# M08: deterministic Fernet key for tests so TOTP secrets can be encrypted/decrypted.
if not settings.TOTP_ENCRYPTION_KEY:
    settings.TOTP_ENCRYPTION_KEY = Fernet.generate_key().decode()


@pytest.fixture
def tenant_a(db):
    """Create tenant A for cross-tenant tests."""
    tenant = Tenant.objects.create(
        slug="tenant-a",
        legal_name="Tenant A Legal",
        commercial_name="Tenant A",
        vertical_spec_object_id="vertical-001",
        plan_tier="starter",
        status=Tenant.Status.ACTIVE,
    )
    ensure_tenant_partition(tenant.id)
    return tenant


@pytest.fixture
def tenant_b(db):
    """Create tenant B for cross-tenant tests."""
    tenant = Tenant.objects.create(
        slug="tenant-b",
        legal_name="Tenant B Legal",
        commercial_name="Tenant B",
        vertical_spec_object_id="vertical-002",
        plan_tier="starter",
        status=Tenant.Status.ACTIVE,
    )
    ensure_tenant_partition(tenant.id)
    return tenant


@pytest.fixture
def sample_item_a(db, tenant_a):
    """Create a sample item owned by tenant A."""
    from apps.core.models import SampleItem

    set_db_tenant(tenant_a.id)
    item = SampleItem.objects.create(tenant=tenant_a, name="Item A")
    clear_db_tenant()
    return item


@pytest.fixture
def sample_item_b(db, tenant_b):
    """Create a sample item owned by tenant B."""
    from apps.core.models import SampleItem

    set_db_tenant(tenant_b.id)
    item = SampleItem.objects.create(tenant=tenant_b, name="Item B")
    clear_db_tenant()
    return item


@pytest.fixture
def redis_client():
    """Provide a Redis client and clean up tenant keys after tests."""
    client = get_redis_client()
    yield client
    # Best-effort cleanup of test tenant keys.
    for key in client.scan_iter(match="tenant:*"):
        client.delete(key)


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture(autouse=True)
def _celery_eager():
    """Run Celery tasks synchronously during tests."""
    from faberloom.celery import app

    original = app.conf.task_always_eager
    app.conf.task_always_eager = True
    yield
    app.conf.task_always_eager = original


@pytest.fixture
def owner_user(db):
    """Create a test user with owner membership."""
    from apps.users.models import User

    return User.objects.create_user(
        email="owner@example.com",
        password="FaberLoom1234!",
        display_name="Owner User",
        is_active=True,
    )


@pytest.fixture
def owner_membership(db, owner_user, tenant_a):
    """Create an active owner membership for owner_user in tenant_a."""
    from apps.users.models import Membership, MembershipStatus

    return Membership.objects.create(
        user=owner_user,
        tenant=tenant_a,
        roles=["owner"],
        active_hat="owner",
        status=MembershipStatus.ACTIVE,
    )


@pytest.fixture
def operator_user(db):
    """Create a test operator user."""
    from apps.users.models import User

    return User.objects.create_user(
        email="operator@example.com",
        password="FaberLoom1234!",
        display_name="Operator User",
        is_active=True,
    )


@pytest.fixture
def operator_membership(db, operator_user, tenant_a):
    """Create an active operator membership."""
    from apps.users.models import Membership, MembershipStatus

    return Membership.objects.create(
        user=operator_user,
        tenant=tenant_a,
        roles=["operator"],
        active_hat="operator",
        status=MembershipStatus.ACTIVE,
    )
