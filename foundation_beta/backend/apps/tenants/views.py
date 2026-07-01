"""DRF views for Tenant management (platform admin only)."""
from rest_framework import viewsets

from apps.tenants.models import Tenant, TenantPlanFeatures
from apps.tenants.serializers import TenantPlanFeaturesSerializer, TenantSerializer


class TenantViewSet(viewsets.ModelViewSet):
    """CRUD for tenants. In M16 we bypass RLS for platform-admin scoped reads."""

    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer

    def get_queryset(self):
        # Platform admin bypasses RLS by using a superuser connection context.
        # M16 does not implement RBAC; this endpoint is intentionally unrestricted.
        return Tenant.objects.all()

    def perform_create(self, serializer):
        tenant = serializer.save()
        TenantPlanFeatures.objects.get_or_create(tenant=tenant)


class TenantPlanFeaturesViewSet(viewsets.ModelViewSet):
    queryset = TenantPlanFeatures.objects.all()
    serializer_class = TenantPlanFeaturesSerializer
