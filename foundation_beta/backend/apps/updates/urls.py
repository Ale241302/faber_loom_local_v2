from django.urls import path

from apps.updates import views


urlpatterns = [
    path("updates/latest", views.LatestReleaseView.as_view(), name="updates-latest"),
    path(
        "updates/min-supported",
        views.MinSupportedVersionView.as_view(),
        name="updates-min-supported",
    ),
]
