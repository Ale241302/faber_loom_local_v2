"""Example tenant-scoped Celery tasks."""
from apps.core.models import SampleItem
from faberloom.celery import TenantTask, app


@app.task(base=TenantTask)
def count_sample_items() -> int:
    """Count sample items visible to the current tenant context."""
    return SampleItem.objects.count()
