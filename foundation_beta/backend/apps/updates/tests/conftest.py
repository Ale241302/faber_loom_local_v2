"""Fixtures for M20 Update tests."""
import pytest

from apps.tenants.models import Tenant
from apps.updates.models import ClientRelease, SystemConfig, TenantUpdateChannel


@pytest.fixture
def tenant(db):
    return Tenant.objects.create(
        slug="update-tenant",
        legal_name="Update Tenant Legal",
        commercial_name="Update Tenant",
        vertical_spec_object_id="vertical-001",
        plan_tier="starter",
        status=Tenant.Status.ACTIVE,
    )


@pytest.fixture
def stable_release(db):
    return ClientRelease.objects.create(
        version="1.3.5",
        platform="win",
        channel="stable",
        feed_url="https://updates.example.com/stable/win/latest.yml",
    )


@pytest.fixture
def min_version_config(db):
    return SystemConfig.objects.get_or_create(
        key="min_supported_client_version",
        defaults={"value": "1.3.0"},
    )[0]
