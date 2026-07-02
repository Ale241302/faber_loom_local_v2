"""DRF views for M11 D9 Policy Gate."""
from __future__ import annotations

from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.rbac.permissions import resolve_permission

from .gate import ActionContext, D9Gate, RetrievedChunk
from .models import DpaStatement, PolicyBlock


class IsAuthenticated(permissions.IsAuthenticated):
    pass


class DpaStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        if not resolve_permission(getattr(request, "membership", None), "config", "view"):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "No tenant context."}, status=status.HTTP_400_BAD_REQUEST)

        dpa, _ = DpaStatement.objects.get_or_create(
            tenant_id=tenant_id,
            defaults={"status": DpaStatement.Status.MISSING, "version": "v1"},
        )
        return Response(
            {
                "status": dpa.status,
                "version": dpa.version,
                "signed_at": dpa.signed_at.isoformat() if dpa.signed_at else None,
                "signed_by": str(dpa.signed_by_id) if dpa.signed_by_id else None,
            }
        )


class DpaSignView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        membership = getattr(request, "membership", None)
        if not resolve_permission(membership, "config", "edit"):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        # E1: only Owner can sign the DPA.
        if getattr(request, "active_hat", None) != "owner":
            return Response(
                {"detail": "Only Owner can sign the DPA."},
                status=status.HTTP_403_FORBIDDEN,
            )

        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "No tenant context."}, status=status.HTTP_400_BAD_REQUEST)

        dpa, _ = DpaStatement.objects.get_or_create(
            tenant_id=tenant_id,
            defaults={"status": DpaStatement.Status.MISSING, "version": "v1"},
        )
        dpa.status = DpaStatement.Status.SIGNED
        dpa.signed_by_id = request.user.id
        dpa.signed_at = timezone.now()
        dpa.save(update_fields=["status", "signed_by", "signed_at", "updated_at"])

        # Keep Tenant.dpa_state in sync for quick lookups.
        from apps.tenants.models import Tenant

        Tenant.objects.filter(id=tenant_id).update(dpa_state="signed")

        return Response(
            {
                "status": dpa.status,
                "signed_at": dpa.signed_at.isoformat(),
                "signed_by": str(dpa.signed_by_id),
            }
        )


class PolicyEvaluateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        if not resolve_permission(getattr(request, "membership", None), "workloom", "write"):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "No tenant context."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        action = ActionContext(
            task_type=data.get("task_type", ""),
            data_class=data.get("data_class", "N1"),
            skill_id=data.get("skill_id", ""),
            confidence=float(data.get("confidence", 0)),
            source=data.get("source", ""),
            tenant_id=str(tenant_id),
            case_id=data.get("case_id"),
            retrieved_chunks=[
                RetrievedChunk(data_class=c.get("data_class", "N1"), source_type=c.get("source_type", ""))
                for c in data.get("retrieved_chunks", [])
            ],
        )

        decision = D9Gate.evaluate(
            actor_id=str(request.user.id),
            actor_role=getattr(request, "active_hat", ""),
            action=action,
        )
        return Response(
            {
                "allowed": decision.allowed,
                "blocked_reason": decision.blocked_reason,
                "effective_classification": decision.effective_classification,
                "requires_human_gate": decision.requires_human_gate,
            }
        )


class PolicyBlocksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        if not resolve_permission(getattr(request, "membership", None), "audit", "view"):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "No tenant context."}, status=status.HTTP_400_BAD_REQUEST)

        qs = PolicyBlock.objects.filter(tenant_id=tenant_id).order_by("-created_at")
        data = [
            {
                "id": str(b.id),
                "case_id": b.case_id,
                "declared_class": b.declared_class,
                "effective_class": b.effective_class,
                "reason": b.reason,
                "resolved_at": b.resolved_at.isoformat() if b.resolved_at else None,
                "created_at": b.created_at.isoformat(),
            }
            for b in qs[:500]
        ]
        return Response(data)
