"""URL routes for M12 Audit Trail."""
from django.urls import path

from apps.audit import views

urlpatterns = [
    path("audit", views.AuditListView.as_view(), name="audit-list"),
    path("audit/export", views.AuditExportView.as_view(), name="audit-export"),
    path("audit/validate", views.AuditValidateView.as_view(), name="audit-validate"),
]
