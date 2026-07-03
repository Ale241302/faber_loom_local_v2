"""DRF views for M14 Outcome Ledger, Gold Samples and Learning Thermometer."""
from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.learning.gold import GoldSampleService, PromotionRejected
from apps.learning.models import GoldSample, LearningThermometer, OutcomeLedgerEntry
from apps.learning.thermometer import update_thermometer
from apps.rbac.drf_permissions import HasPermission
from apps.rbac.permissions import resolve_permission


class LedgerListView(APIView):
    """List outcome ledger entries. Requires audit:view or config:view."""

    permission_classes = [HasPermission("audit", "view")]

    def get(self, request: Request) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "tenant_id required"}, status=status.HTTP_400_BAD_REQUEST)

        membership = getattr(request, "membership", None)
        if not resolve_permission(membership, "audit", "view") and not resolve_permission(membership, "config", "view"):
            return Response({"detail": "permission denied"}, status=status.HTTP_403_FORBIDDEN)

        set_db_tenant(tenant_id)
        try:
            entries = OutcomeLedgerEntry.objects.filter(tenant_id=tenant_id).order_by("-created_at")
            data = [
                {
                    "id": str(e.id),
                    "draft_id": str(e.draft_id) if e.draft_id else None,
                    "classification_result_id": str(e.classification_result_id) if e.classification_result_id else None,
                    "decision": e.decision,
                    "reason": e.reason,
                    "confidence": str(e.confidence) if e.confidence is not None else None,
                    "actor_id": str(e.actor_id),
                    "actor_role_at_decision": e.actor_role_at_decision,
                    "created_at": e.created_at.isoformat(),
                }
                for e in entries
            ]
            return Response({"count": len(data), "items": data})
        finally:
            clear_db_tenant()


class CandidateListView(APIView):
    """List gold sample candidates. Requires config:view."""

    permission_classes = [HasPermission("config", "view")]

    def get(self, request: Request) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "tenant_id required"}, status=status.HTTP_400_BAD_REQUEST)

        set_db_tenant(tenant_id)
        try:
            candidates = GoldSample.objects.filter(
                tenant_id=tenant_id,
                status=GoldSample.Status.CANDIDATE,
            ).order_by("-created_at")
            data = [
                {
                    "id": str(c.id),
                    "agent_id": c.agent_id,
                    "skill_id": c.skill_id,
                    "input_json": c.input_json,
                    "output_json": c.output_json,
                    "validity_metadata": c.validity_metadata,
                    "created_at": c.created_at.isoformat(),
                }
                for c in candidates
            ]
            return Response({"count": len(data), "items": data})
        finally:
            clear_db_tenant()


class CandidatePromoteView(APIView):
    """Promote a gold sample candidate. Requires config:edit."""

    permission_classes = [HasPermission("config", "edit")]

    def post(self, request: Request, gold_id: str) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "tenant_id required"}, status=status.HTTP_400_BAD_REQUEST)

        set_db_tenant(tenant_id)
        try:
            gold = get_object_or_404(GoldSample, tenant_id=tenant_id, id=gold_id)
            try:
                result = GoldSampleService.promote(
                    gold,
                    request.user,
                    getattr(request, "active_hat", ""),
                )
            except PromotionRejected as exc:
                return Response({"detail": "validation failed", "validations": exc.validations}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            return Response({
                "id": str(gold.id),
                "status": gold.status,
                "requires_second_approver": result.requires_second_approver,
            })
        finally:
            clear_db_tenant()


class CandidateDiscardView(APIView):
    """Discard a gold sample candidate. Requires config:edit."""

    permission_classes = [HasPermission("config", "edit")]

    def post(self, request: Request, gold_id: str) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "tenant_id required"}, status=status.HTTP_400_BAD_REQUEST)

        set_db_tenant(tenant_id)
        try:
            gold = get_object_or_404(GoldSample, tenant_id=tenant_id, id=gold_id)
            GoldSampleService.discard(gold)
            return Response({"id": str(gold.id), "status": gold.status})
        finally:
            clear_db_tenant()


class GoldSecondApproveView(APIView):
    """Second approver unblocks a gold sample. Requires config:edit."""

    permission_classes = [HasPermission("config", "edit")]

    def post(self, request: Request, gold_id: str) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "tenant_id required"}, status=status.HTTP_400_BAD_REQUEST)

        set_db_tenant(tenant_id)
        try:
            gold = get_object_or_404(GoldSample, tenant_id=tenant_id, id=gold_id)
            try:
                GoldSampleService.approve_second(
                    gold,
                    request.user,
                    getattr(request, "active_hat", ""),
                )
            except (ValueError, PermissionError) as exc:
                return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)

            return Response({"id": str(gold.id), "status": gold.status})
        finally:
            clear_db_tenant()


class GoldDeprecateView(APIView):
    """Deprecate an active gold sample. Requires config:edit."""

    permission_classes = [HasPermission("config", "edit")]

    def post(self, request: Request, gold_id: str) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "tenant_id required"}, status=status.HTTP_400_BAD_REQUEST)

        set_db_tenant(tenant_id)
        try:
            gold = get_object_or_404(GoldSample, tenant_id=tenant_id, id=gold_id)
            reason = (request.data or {}).get("reason", "")
            GoldSampleService.deprecate(gold, request.user, reason)
            return Response({"id": str(gold.id), "status": gold.status})
        finally:
            clear_db_tenant()


class ThermometerView(APIView):
    """Get the learning thermometer for the tenant. Requires workloom:read."""

    permission_classes = [HasPermission("workloom", "read")]

    def get(self, request: Request) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "tenant_id required"}, status=status.HTTP_400_BAD_REQUEST)

        agent_id = request.query_params.get("agent_id")
        if not agent_id:
            return Response({"detail": "agent_id query parameter required"}, status=status.HTTP_400_BAD_REQUEST)

        thermometer = update_thermometer(tenant_id, agent_id)
        return Response({
            "tenant_id": tenant_id,
            "agent_id": agent_id,
            "score": thermometer.score,
            "bucket": thermometer.bucket,
        })
