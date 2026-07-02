"""WebSocket routing for M15 Outbox Streams."""
from django.urls import re_path

from apps.events import consumers


websocket_urlpatterns = [
    re_path(r"ws/events/$", consumers.EventsConsumer.as_asgi()),
]
