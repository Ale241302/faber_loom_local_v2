"""URL routes for M09 RBAC."""
from django.urls import path

from apps.rbac import views


urlpatterns = [
    path("memberships", views.MembershipListView.as_view(), name="rbac-memberships-list"),
    path("memberships/invite", views.MembershipCreateView.as_view(), name="rbac-memberships-invite"),
    path(
        "memberships/<str:membership_id>",
        views.MembershipDetailView.as_view(),
        name="rbac-memberships-detail",
    ),
    path(
        "memberships/<str:membership_id>/revoke",
        views.RevokeMembershipView.as_view(),
        name="rbac-memberships-revoke",
    ),
    path("memberships/me/hat", views.SetActiveHatView.as_view(), name="rbac-set-hat"),
]
