"""DRF views for M12 Audit Trail."""
from __future__ import annotations

import csv
import io
import json

from django.conf import settings
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.rbac.models import PermissionLevel
from apps.rbac.permissions import resolve_permission

from .models import AuditLog
from .tasks import validate_chain


def _audit_visibility(request) -> str:
    """Return 'self' if the active role only grants read_self on audit, else 'all'."""
    membership = getattr(request, "membership", None)
    if not membership:
        return "self"

    active_hat = getattr(request, "active_hat", None)
    if not active_hat:
        return "self"

    from apps.rbac.models import Role

    try:
        role = Role.objects.get(id=active_hat)
    except Role.DoesNotExist:
        return "self"

    level = (role.permissions or {}).get("audit", PermissionLevel.NONE)
    if level in (PermissionLevel.READ, PermissionLevel.FULL):
        return "all"
    return "self"


class IsAuthenticated(permissions.IsAuthenticated):
    pass


class AuditListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        if not resolve_permission(getattr(request, "membership", None), "audit", "view"):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "No tenant context."}, status=status.HTTP_400_BAD_REQUEST)

        qs = AuditLog.objects.filter(tenant_id=tenant_id)
        if _audit_visibility(request) == "self":
            qs = qs.filter(actor_id=request.user.id)

        case_id = request.query_params.get("case_id")
        actor_id = request.query_params.get("actor_id")
        action_id = request.query_params.get("action_id")
        if case_id:
            qs = qs.filter(case_id=case_id)
        if actor_id:
            qs = qs.filter(actor_id=actor_id)
        if action_id:
            qs = qs.filter(action_id=action_id)

        qs = qs.order_by("-seq_no")
        data = [
            {
                "id": str(entry.id),
                "seq_no": entry.seq_no,
                "chain_id": entry.chain_id,
                "case_id": entry.case_id,
                "action_id": entry.action_id,
                "data_class": entry.data_class,
                "actor_id": str(entry.actor_id),
                "actor_role_at_decision": entry.actor_role_at_decision,
                "sha_chain_curr": entry.sha_chain_curr,
                "created_at": entry.created_at.isoformat(),
            }
            for entry in qs[:1000]
        ]
        return Response(data)


class AuditExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        if not resolve_permission(getattr(request, "membership", None), "audit", "export"):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "No tenant context."}, status=status.HTTP_400_BAD_REQUEST)

        fmt = request.query_params.get("format", settings.AUDIT_EXPORT_FORMAT.split(",")[0] if getattr(settings, "AUDIT_EXPORT_FORMAT", None) else "json")
        chain_id = f"{tenant_id}:default"
        report = validate_chain(str(tenant_id), chain_id)
        entries = list(AuditLog.objects.filter(tenant_id=tenant_id, chain_id=chain_id).order_by("seq_no"))

        if fmt == "csv":
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            writer.writerow(
                [
                    "seq_no",
                    "chain_id",
                    "case_id",
                    "action_id",
                    "data_class",
                    "actor_id",
                    "actor_role_at_decision",
                    "sha_chain_curr",
                    "created_at",
                ]
            )
            for entry in entries:
                writer.writerow(
                    [
                        entry.seq_no,
                        entry.chain_id,
                        entry.case_id,
                        entry.action_id,
                        entry.data_class,
                        str(entry.actor_id),
                        entry.actor_role_at_decision,
                        entry.sha_chain_curr,
                        entry.created_at.isoformat(),
                    ]
                )
            writer.writerow([])
            writer.writerow(["validation_report"])
            writer.writerow(["valid", report["valid"]])
            writer.writerow(["checked", report["checked"]])
            writer.writerow(["breaks", json.dumps(report["breaks"])])
            return Response(
                {"format": "csv", "content": buffer.getvalue(), "validation_report": report},
                content_type="text/csv" if False else None,
            )

        data = {
            "format": "json",
            "tenant_id": str(tenant_id),
            "chain_id": chain_id,
            "validation_report": report,
            "entries": [
                {
                    "seq_no": entry.seq_no,
                    "case_id": entry.case_id,
                    "action_id": entry.action_id,
                    "data_class": entry.data_class,
                    "actor_id": str(entry.actor_id),
                    "actor_role_at_decision": entry.actor_role_at_decision,
                    "sha_chain_curr": entry.sha_chain_curr,
                    "created_at": entry.created_at.isoformat(),
                }
                for entry in entries
            ],
        }
        return Response(data)


class AuditValidateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        if not resolve_permission(getattr(request, "membership", None), "audit", "export"):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "No tenant context."}, status=status.HTTP_400_BAD_REQUEST)

        chain_id = f"{tenant_id}:default"
        report = validate_chain(str(tenant_id), chain_id)
        return Response(report)
