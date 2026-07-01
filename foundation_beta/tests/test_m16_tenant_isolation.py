"""M16 Tenant Isolation — 5 cross-tenant tests.

These tests verify that tenant isolation holds across PostgreSQL RLS, Redis,
Celery, and MinIO. They are designed to FAIL if any layer leaks data across
tenants.
"""
from __future__ import annotations

import uuid

import pytest
from django.db import connection

from apps.core.llm import litellm_metadata
from apps.core.memory import letta_namespace
from apps.core.models import SampleItem
from apps.core.redis_client import get_redis_client, require_tenant_prefix, tenant_key
from apps.core.storage import tenant_path
from apps.core.tenant_context import clear_db_tenant, current_tenant_id, set_db_tenant
from apps.tenants.models import Tenant


# ---------------------------------------------------------------------------
# 1. PostgreSQL RLS: query without tenant id fails closed
# ---------------------------------------------------------------------------
@pytest.mark.django_db
def test_rls_query_without_tenant_id_fails_closed(sample_item_a):
    """A query with no app.tenant_id must not see tenant-scoped rows."""
    clear_db_tenant()

    # NULLIF(..., '')::UUID yields NULL when the setting is missing;
    # tenant_id = NULL is never TRUE, so the RLS policy denies every row.
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM sample_items")
        (count,) = cursor.fetchone()
        assert count == 0


# ---------------------------------------------------------------------------
# 2. PostgreSQL RLS: tenant A cannot read tenant B data
# ---------------------------------------------------------------------------
@pytest.mark.django_db
def test_postgres_rls_tenant_a_cannot_read_tenant_b(
    tenant_a, tenant_b, sample_item_b
):
    """With tenant A context, rows owned by tenant B must be invisible."""
    set_db_tenant(tenant_a.id)
    try:
        # Direct ORM query under tenant A context.
        visible = list(SampleItem.objects.filter(id=sample_item_b.id))
        assert visible == []

        # Raw query with explicit tenant_id parameter for comparison.
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM sample_items WHERE tenant_id = %s",
                [str(tenant_b.id)],
            )
            assert cursor.fetchone() is not None  # Row exists in the table.
    finally:
        clear_db_tenant()


# ---------------------------------------------------------------------------
# 3. Redis: keys are scoped per tenant
# ---------------------------------------------------------------------------
@pytest.mark.django_db
def test_redis_key_isolated_by_tenant_prefix(tenant_a, tenant_b):
    """A tenant-scoped Redis key must not be reachable from another tenant."""
    redis = get_redis_client()
    key_a = tenant_key(tenant_a.id, "session:123")
    key_b = tenant_key(tenant_b.id, "session:123")

    redis.set(key_a, "secret-a")

    # Tenant B prefix must not expose tenant A data.
    assert redis.get(key_b) is None
    assert redis.get(key_a) == "secret-a"

    # Accessing A's key while validating as B must raise.
    with pytest.raises(ValueError):
        require_tenant_prefix(key_a, tenant_b.id)

    # A non-prefixed key is rejected outright.
    with pytest.raises(ValueError):
        tenant_key(tenant_a.id, "../../global")


# ---------------------------------------------------------------------------
# 4. Celery: task scoped to tenant A does not read tenant B rows
# ---------------------------------------------------------------------------
@pytest.mark.django_db
def test_celery_tenant_task_does_not_read_other_tenant(
    tenant_a, tenant_b, sample_item_a
):
    """A TenantTask for tenant B must not see rows created by tenant A."""
    from apps.core.tasks import count_sample_items

    # Execute synchronously because tests configure CELERY_TASK_ALWAYS_EAGER.
    count_a = count_sample_items.apply_async(kwargs={"_tenant_id": str(tenant_a.id)}).get()
    count_b = count_sample_items.apply_async(kwargs={"_tenant_id": str(tenant_b.id)}).get()

    assert count_a == 1
    assert count_b == 0


# ---------------------------------------------------------------------------
# 5. MinIO: path builder rejects path traversal
# ---------------------------------------------------------------------------
@pytest.mark.django_db
def test_minio_path_builder_rejects_path_traversal(tenant_a):
    """tenant_path must reject traversal attempts and unsafe segments."""
    with pytest.raises(ValueError):
        tenant_path(tenant_a.id, "..", "etc", "passwd")

    with pytest.raises(ValueError):
        tenant_path(tenant_a.id, "file../../other")

    with pytest.raises(ValueError):
        tenant_path(tenant_a.id, "bad segment")  # space not allowed

    path = tenant_path(tenant_a.id, "uploads", "doc.pdf")
    assert path == f"/tenants/{tenant_a.id}/uploads/doc.pdf"


# ---------------------------------------------------------------------------
# Helpers / metadata builders (lightweight unit checks)
# ---------------------------------------------------------------------------
def test_litellm_metadata_tags_tenant_id(tenant_a):
    """LiteLLM request metadata must include tenant_id."""
    meta = litellm_metadata(tenant_a.id, trace_id="abc")
    assert meta["tenant_id"] == str(tenant_a.id)
    assert meta["trace_id"] == "abc"


def test_letta_namespace_blocks_cross_tenant(tenant_a, tenant_b):
    """Letta namespaces must embed tenant_id and never collide."""
    ns_a = letta_namespace(tenant_a.id, "agent-1")
    ns_b = letta_namespace(tenant_b.id, "agent-1")
    assert ns_a != ns_b
    assert f"tenant:{tenant_a.id}" in ns_a
    assert f"tenant:{tenant_b.id}" in ns_b
