"""Celery configuration with TenantTask base class."""
import os

from celery import Celery, Task

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "faberloom.settings")

app = Celery("faberloom")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


class TenantTask(Task):
    """Base Celery task that binds a tenant session and clears it afterwards."""

    def __call__(self, *args, **kwargs):
        tenant_id = kwargs.pop("_tenant_id", None)
        if tenant_id is None:
            raise ValueError("TenantTask missing _tenant_id")

        from apps.core.tenant_context import set_db_tenant, clear_db_tenant

        set_db_tenant(tenant_id)
        try:
            return super().__call__(*args, **kwargs)
        finally:
            clear_db_tenant()
