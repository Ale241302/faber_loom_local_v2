"""URL routes for M07 Bootstrap Wizard (tenant-scoped)."""
from django.urls import path

from apps.bootstrap import views

urlpatterns = [
    path("invite-owner", views.InviteOwnerView.as_view(), name="bootstrap-invite-owner"),
    path("steps/<str:step>", views.WizardStepView.as_view(), name="bootstrap-step"),
    path("bootstrap", views.BootstrapStatusView.as_view(), name="bootstrap-status"),
    path("sandbox", views.SandboxTestView.as_view(), name="bootstrap-sandbox"),
    path("activate", views.ActivateTenantView.as_view(), name="bootstrap-activate"),
]
