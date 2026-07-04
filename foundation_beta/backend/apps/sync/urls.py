from django.urls import path

from apps.sync import views


urlpatterns = [
    path("sync/full-state", views.FullStateView.as_view(), name="sync-full-state"),
]
