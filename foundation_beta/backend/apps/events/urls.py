"""URL routes for M15 Outbox Streams REST fallback."""
from django.urls import path

from apps.events import views


urlpatterns = [
    path("events", views.EventPollingView.as_view(), name="events-polling"),
]
