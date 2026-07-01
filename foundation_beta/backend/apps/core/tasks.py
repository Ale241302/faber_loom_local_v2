"""Example tenant-scoped Celery tasks."""
from apps.core.models import SampleItem
from faberloom.celery import TenantTask, app


@app.task(base=TenantTask)
def count_sample_items(_tenant_id: str | None = None) -> int:
    """Count sample items visible to the current tenant context.

    `_tenant_id` is accepted so TenantTask can validate the tenant header
    without breaking Celery's eager-mode argument check.
    """
    return SampleItem.objects.count()
