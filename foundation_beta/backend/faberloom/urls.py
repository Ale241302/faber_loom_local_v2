"""URL configuration for FaberLoom Foundation Beta."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/tenants/<uuid:tenant_id>/", include("apps.bootstrap.urls")),
    path("api/tenants/", include("apps.tenants.urls")),
    path("api/", include("apps.auth_session.urls")),
    path("api/", include("apps.rbac.urls")),
    path("api/", include("apps.events.urls")),
    path("api/", include("apps.audit.urls")),
    path("api/", include("apps.policy.urls")),
    path("api/", include("apps.classifier.urls")),
]
