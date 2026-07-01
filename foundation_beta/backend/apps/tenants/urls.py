"""URL routing for tenants app."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.tenants.views import TenantPlanFeaturesViewSet, TenantViewSet

router = DefaultRouter()
router.register(r"", TenantViewSet, basename="tenant")
router.register(r"features", TenantPlanFeaturesViewSet, basename="tenant-plan-features")

urlpatterns = [
    path("", include(router.urls)),
]
