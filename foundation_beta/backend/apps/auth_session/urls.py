"""URL routes for M08 Auth Session."""
from django.urls import path

from apps.auth_session import views


urlpatterns = [
    path("auth/login", views.LoginStepOneView.as_view(), name="auth-login"),
    path("auth/2fa", views.LoginStepTwoView.as_view(), name="auth-2fa"),
    path("auth/me", views.MeView.as_view(), name="auth-me"),
    path("auth/logout", views.LogoutView.as_view(), name="auth-logout"),
    path("auth/logout-all", views.LogoutAllView.as_view(), name="auth-logout-all"),
    path(
        "auth/session/<str:session_id>/revoke",
        views.RevokeSessionView.as_view(),
        name="auth-revoke-session",
    ),
]
