"""Full-state sync endpoint for M19 Offline Sync."""
from __future__ import annotations

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.rbac.drf_permissions import HasPermission
from apps.sync.service import build_full_state


class FullStateView(APIView):
    """Return a tenant-scoped snapshot of the operative state for desktop sync."""

    permission_classes = [HasPermission("workloom", "view")]

    def get(self, request: Request) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response(
                {"detail": "tenant_id required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(build_full_state(str(tenant_id)))
