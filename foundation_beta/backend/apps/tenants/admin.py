"""Django admin for tenants."""
from django.contrib import admin

from apps.tenants.models import Tenant, TenantPlanFeatures


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ["slug", "legal_name", "status", "plan_tier", "created_at"]
    list_filter = ["status", "plan_tier"]
    search_fields = ["slug", "legal_name", "commercial_name"]


@admin.register(TenantPlanFeatures)
class TenantPlanFeaturesAdmin(admin.ModelAdmin):
    list_display = ["tenant", "data_class_ceiling", "max_seats"]
