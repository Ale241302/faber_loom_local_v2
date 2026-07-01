"""URL configuration for FaberLoom Foundation Beta."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/tenants/", include("apps.tenants.urls")),
]
