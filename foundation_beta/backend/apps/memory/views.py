"""DRF views for M17 Memory Letta."""
from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.memory.models import MemoryItem
from apps.memory.services import MemoryService, PromptAssembler
from apps.memory.letta_client import LettaMemoryClient
from apps.rbac.drf_permissions import HasPermission


def _get_client() -> LettaMemoryClient:
    return LettaMemoryClient()


class MemoryContextView(APIView):
    permission_classes = [HasPermission("workloom", "view")]

    def get(self, request: Request, agent_id: str) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "tenant_id required"}, status=status.HTTP_400_BAD_REQUEST)

        task_id = request.query_params.get("task_id") or None
        set_db_tenant(tenant_id)
        try:
            sections = PromptAssembler.for_agent(
                tenant_id,
                agent_id,
                client=_get_client(),
                task_id=task_id,
            )
            return Response({
                "agent_id": agent_id,
                "task_id": task_id,
                "sections": sections,
                "prompt": PromptAssembler.to_prompt(sections),
            })
        finally:
            clear_db_tenant()


class MemoryProposedListView(APIView):
    permission_classes = [HasPermission("workloom", "view")]

    def get(self, request: Request) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "tenant_id required"}, status=status.HTTP_400_BAD_REQUEST)

        set_db_tenant(tenant_id)
        try:
            items = MemoryItem.objects.filter(
                tenant_id=tenant_id,
                layer=MemoryItem.Layer.PERSISTENT,
                status=MemoryItem.Status.PROPOSED,
            ).order_by("-created_at")
            data = [
                {
                    "id": str(item.id),
                    "agent_id": item.agent_id,
                    "namespace": item.namespace,
                    "content_hash": item.content_hash,
                    "created_at": item.created_at.isoformat(),
                }
                for item in items
            ]
            return Response({"count": len(data), "items": data})
        finally:
            clear_db_tenant()


def _load_item(tenant_id, memory_id: str) -> MemoryItem | Response:
    try:
        return MemoryItem.objects.get(tenant_id=tenant_id, id=memory_id)
    except MemoryItem.DoesNotExist:
        return Response({"detail": "not found"}, status=status.HTTP_404_NOT_FOUND)


class MemoryApproveView(APIView):
    permission_classes = [HasPermission("workloom", "approve")]

    def post(self, request: Request, memory_id: str) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "tenant_id required"}, status=status.HTTP_400_BAD_REQUEST)

        set_db_tenant(tenant_id)
        try:
            item_or_response = _load_item(tenant_id, memory_id)
            if isinstance(item_or_response, Response):
                return item_or_response
            item = item_or_response
            kb_chunks = (request.data or {}).get("kb_chunks", [])
            result = MemoryService.approve_persistent(
                item,
                request.user,
                getattr(request, "active_hat", ""),
                client=_get_client(),
                kb_chunks=kb_chunks,
            )
            return Response({"id": str(item.id), **result})
        finally:
            clear_db_tenant()


class MemoryRejectView(APIView):
    permission_classes = [HasPermission("workloom", "edit")]

    def post(self, request: Request, memory_id: str) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "tenant_id required"}, status=status.HTTP_400_BAD_REQUEST)

        set_db_tenant(tenant_id)
        try:
            item_or_response = _load_item(tenant_id, memory_id)
            if isinstance(item_or_response, Response):
                return item_or_response
            item = item_or_response
            MemoryService.reject_persistent(
                item,
                request.user,
                getattr(request, "active_hat", ""),
            )
            return Response({"id": str(item.id), "status": item.status})
        finally:
            clear_db_tenant()


class MemoryDeprecateView(APIView):
    permission_classes = [HasPermission("workloom", "edit")]

    def post(self, request: Request, memory_id: str) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "tenant_id required"}, status=status.HTTP_400_BAD_REQUEST)

        set_db_tenant(tenant_id)
        try:
            item_or_response = _load_item(tenant_id, memory_id)
            if isinstance(item_or_response, Response):
                return item_or_response
            item = item_or_response
            MemoryService.deprecate(
                item,
                request.user,
                getattr(request, "active_hat", ""),
            )
            return Response({"id": str(item.id), "status": item.status})
        finally:
            clear_db_tenant()
