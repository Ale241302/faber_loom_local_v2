"""M16 Tenant Isolation — pure unit tests that do not require services."""
from uuid import uuid4

import pytest

from apps.core.llm import litellm_metadata
from apps.core.memory import letta_namespace
from apps.core.redis_client import require_tenant_prefix, tenant_key
from apps.core.storage import tenant_path


def test_tenant_key_format():
    tenant_id = uuid4()
    assert tenant_key(tenant_id, "cache:foo") == f"tenant:{tenant_id}:cache:foo"


def test_require_tenant_prefix_raises_on_foreign_key():
    tenant_a, tenant_b = uuid4(), uuid4()
    key_a = tenant_key(tenant_a, "x")
    with pytest.raises(ValueError):
        require_tenant_prefix(key_a, tenant_b)


def test_tenant_path_scopes_and_rejects_traversal():
    tenant_id = uuid4()
    assert tenant_path(tenant_id, "docs", "file.pdf") == f"/tenants/{tenant_id}/docs/file.pdf"
    with pytest.raises(ValueError):
        tenant_path(tenant_id, "..", "etc")
    with pytest.raises(ValueError):
        tenant_path(tenant_id, "bad/name")


def test_litellm_metadata_contains_tenant_id():
    tenant_id = uuid4()
    meta = litellm_metadata(tenant_id)
    assert meta["tenant_id"] == str(tenant_id)


def test_letta_namespace_contains_tenant_and_rejects_invalid():
    tenant_id = uuid4()
    ns = letta_namespace(tenant_id, "agent-1", task_id="task-9", kind="working")
    assert ns == f"mem:tenant:{tenant_id}:agent:agent-1:task:task-9:working"
    with pytest.raises(ValueError):
        letta_namespace(tenant_id, "bad/id")
