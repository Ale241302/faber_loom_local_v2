"""DRF views for M13 Draft HITL."""
from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.drafts.models import Draft
from apps.drafts.services import DraftService
from apps.rbac.drf_permissions import HasPermission


def _transition(
    request: Request,
    draft_id: str,
    method: Any,
    payload: dict[str, Any] | None = None,
) -> Response:
    tenant_id = getattr(request, "tenant_id", None)
    if not tenant_id:
        return Response({"detail": "tenant_id required"}, status=status.HTTP_400_BAD_REQUEST)

    set_db_tenant(tenant_id)
    try:
        try:
            draft = Draft.objects.get(tenant_id=tenant_id, id=draft_id)
        except Draft.DoesNotExist:
            return Response({"detail": "not found"}, status=status.HTTP_404_NOT_FOUND)

        kwargs: dict[str, Any] = {
            "draft": draft,
            "user": request.user,
            "actor_role": getattr(request, "active_hat", ""),
        }
        if payload:
            kwargs.update(payload)

        method(**kwargs)
        return Response({"id": str(draft.id), "status": draft.status})
    finally:
        clear_db_tenant()


class DraftListView(APIView):
    permission_classes = [HasPermission("workloom", "read")]

    def get(self, request: Request) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "tenant_id required"}, status=status.HTTP_400_BAD_REQUEST)

        set_db_tenant(tenant_id)
        try:
            drafts = Draft.objects.filter(tenant_id=tenant_id).order_by("-created_at")
            data = [
                {
                    "id": str(d.id),
                    "task_id": str(d.task_id),
                    "status": d.status,
                    "channel": d.channel,
                    "recipient": d.recipient,
                    "expires_at": d.expires_at.isoformat(),
                    "created_at": d.created_at.isoformat(),
                }
                for d in drafts
            ]
            return Response({"count": len(data), "items": data})
        finally:
            clear_db_tenant()


class DraftDetailView(APIView):
    permission_classes = [HasPermission("workloom", "read")]

    def get(self, request: Request, draft_id: str) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "tenant_id required"}, status=status.HTTP_400_BAD_REQUEST)

        set_db_tenant(tenant_id)
        try:
            try:
                draft = Draft.objects.get(tenant_id=tenant_id, id=draft_id)
            except Draft.DoesNotExist:
                return Response({"detail": "not found"}, status=status.HTTP_404_NOT_FOUND)

            return Response({
                "id": str(draft.id),
                "task_id": str(draft.task_id),
                "status": draft.status,
                "original_content": draft.original_content,
                "edited_content": draft.edited_content,
                "edit_reason": draft.edit_reason,
                "edit_classification": draft.edit_classification,
                "channel": draft.channel,
                "recipient": draft.recipient,
                "approver_id": str(draft.approver_id) if draft.approver_id else None,
                "expires_at": draft.expires_at.isoformat(),
                "created_at": draft.created_at.isoformat(),
            })
        finally:
            clear_db_tenant()


class DraftApproveView(APIView):
    permission_classes = [HasPermission("workloom", "approve")]

    def post(self, request: Request, draft_id: str) -> Response:
        return _transition(request, draft_id, DraftService.approve)


class DraftEditView(APIView):
    permission_classes = [HasPermission("workloom", "edit")]

    def post(self, request: Request, draft_id: str) -> Response:
        data = request.data or {}
        payload = {
            "edited": data.get("edited_content") or {},
            "reason": data.get("edit_reason", ""),
            "classification": data.get("edit_classification", "tone"),
        }
        return _transition(request, draft_id, DraftService.edit_and_approve, payload)


class DraftRejectView(APIView):
    permission_classes = [HasPermission("workloom", "edit")]

    def post(self, request: Request, draft_id: str) -> Response:
        data = request.data or {}
        payload = {"reason": data.get("reason", "")}
        return _transition(request, draft_id, DraftService.reject, payload)


class DraftCancelView(APIView):
    permission_classes = [HasPermission("workloom", "edit")]

    def post(self, request: Request, draft_id: str) -> Response:
        return _transition(request, draft_id, DraftService.cancel)
