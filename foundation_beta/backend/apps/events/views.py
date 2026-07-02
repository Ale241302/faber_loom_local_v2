"""REST fallback views for M15 Outbox Streams."""
from __future__ import annotations

from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.events.models import EventLog


class EventPollingView(APIView):
    """Polling fallback for clients without WebSocket support."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "No tenant context."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            since = int(request.query_params.get("since", "0"))
        except ValueError:
            since = 0

        # 24h window to avoid unbounded replay.
        since_dt = timezone.now() - timezone.timedelta(hours=24)
        qs = EventLog.objects.filter(
            tenant_id=tenant_id,
            seq_no__gt=since,
            created_at__gte=since_dt,
        ).order_by("seq_no")[:1000]

        return Response(
            {
                "events": [
                    {
                        "event_id": e.event_id,
                        "type": e.event_type,
                        "tenant_id": str(e.tenant_id),
                        "payload": e.payload_json,
                        "seq_no": e.seq_no,
                        "timestamp": e.created_at.isoformat(),
                    }
                    for e in qs
                ]
            }
        )
