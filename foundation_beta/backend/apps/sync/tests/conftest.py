"""Fixtures for M19 Sync tests."""
import pytest

from apps.tenants.models import Tenant


@pytest.fixture
def tenant(db):
    return Tenant.objects.create(
        slug="sync-tenant",
        legal_name="Sync Tenant Legal",
        commercial_name="Sync Tenant",
        vertical_spec_object_id="vertical-001",
        plan_tier="starter",
        status=Tenant.Status.ACTIVE,
    )


@pytest.fixture
def other_tenant(db):
    return Tenant.objects.create(
        slug="other-sync-tenant",
        legal_name="Other Sync Tenant Legal",
        commercial_name="Other Sync Tenant",
        vertical_spec_object_id="vertical-002",
        plan_tier="starter",
        status=Tenant.Status.ACTIVE,
    )
