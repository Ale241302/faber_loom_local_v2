"""DRF views for M20 Auto Update."""
from __future__ import annotations

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.rbac.drf_permissions import HasPermission
from apps.updates.service import build_update_info, get_min_supported_version


class LatestReleaseView(APIView):
    """Return the latest update release for the current tenant and platform."""

    permission_classes = [HasPermission("config", "view")]

    def get(self, request: Request) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response(
                {"detail": "tenant_id required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        platform = str(request.query_params.get("platform", "")).lower()
        if not platform:
            return Response(
                {"detail": "platform query param required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(build_update_info(str(tenant_id), platform))


class MinSupportedVersionView(APIView):
    """Return the global minimum supported client version."""

    permission_classes = [HasPermission("config", "view")]

    def get(self, request: Request) -> Response:
        return Response({
            "min_supported_client_version": get_min_supported_version(),
        })
