"""Classifier API views for M10."""
from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.classifier.models import ClassifierSkill, FeedItem, FeedItemStatus
from apps.classifier.schemas import ActionContext
from apps.classifier.services import ClassifierService
from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.rbac.drf_permissions import HasPermission


class ClassifyView(APIView):
    permission_classes = [HasPermission("workloom", "write")]

    def post(self, request: Request) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "tenant_id required"}, status=status.HTTP_400_BAD_REQUEST)

        set_db_tenant(tenant_id)
        try:
            data = request.data or {}
            feed_item = ClassifierService.create_feed_item(
                tenant_id=tenant_id,
                source_type=data.get("source_type", "manual"),
                raw_payload=data.get("raw_payload", {}),
                normalized_payload=data.get("normalized_payload", data.get("raw_payload", {})),
                external_id=data.get("external_id", ""),
                data_class=data.get("data_class", "N1"),
            )
            result = ClassifierService.manual_classify(
                feed_item,
                actor_id=str(request.user.id),
                actor_role=getattr(request, "active_hat", ""),
            )
            return Response(result, status=status.HTTP_201_CREATED)
        finally:
            clear_db_tenant()


class PendingView(APIView):
    permission_classes = [HasPermission("workloom", "read")]

    def get(self, request: Request) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "tenant_id required"}, status=status.HTTP_400_BAD_REQUEST)

        set_db_tenant(tenant_id)
        try:
            items = FeedItem.objects.filter(
                tenant_id=tenant_id,
                status=FeedItemStatus.PENDING_HUMAN_REVIEW,
            ).order_by("received_at")
            data = [
                {
                    "id": str(item.id),
                    "source_type": item.source_type,
                    "status": item.status,
                    "received_at": item.received_at.isoformat(),
                }
                for item in items
            ]
            return Response({"count": len(data), "items": data})
        finally:
            clear_db_tenant()


class ConfirmView(APIView):
    permission_classes = [HasPermission("workloom", "write")]

    def post(self, request: Request, feed_item_id: str) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "tenant_id required"}, status=status.HTTP_400_BAD_REQUEST)

        set_db_tenant(tenant_id)
        try:
            feed_item = FeedItem.objects.get(tenant_id=tenant_id, id=feed_item_id)
            result = ClassifierService.confirm_pending(
                feed_item,
                actor_id=str(request.user.id),
                actor_role=getattr(request, "active_hat", ""),
            )
            return Response(result)
        except FeedItem.DoesNotExist:
            return Response({"detail": "not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            clear_db_tenant()


class ReclassifyView(APIView):
    permission_classes = [HasPermission("workloom", "write")]

    def post(self, request: Request, feed_item_id: str) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "tenant_id required"}, status=status.HTTP_400_BAD_REQUEST)

        set_db_tenant(tenant_id)
        try:
            feed_item = FeedItem.objects.get(tenant_id=tenant_id, id=feed_item_id)
            data = request.data or {}
            action_context = data.get("action_context", {})
            result = ClassifierService.reclassify(
                feed_item,
                action_context=action_context,
                actor_id=str(request.user.id),
                actor_role=getattr(request, "active_hat", ""),
                reason=data.get("reason", "operator_correction"),
            )
            return Response(result)
        except FeedItem.DoesNotExist:
            return Response({"detail": "not found"}, status=status.HTTP_404_NOT_FOUND)
        finally:
            clear_db_tenant()


class SkillListView(APIView):
    permission_classes = [HasPermission("config", "view")]

    def get(self, request: Request) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "tenant_id required"}, status=status.HTTP_400_BAD_REQUEST)

        set_db_tenant(tenant_id)
        try:
            skills = ClassifierSkill.objects.filter(tenant_id=tenant_id).order_by("name")
            data = [
                {
                    "id": str(skill.id),
                    "name": skill.name,
                    "origin": skill.origin,
                    "status": skill.status,
                    "threshold": str(skill.threshold),
                    "model_id": skill.model_id,
                }
                for skill in skills
            ]
            return Response({"count": len(data), "skills": data})
        finally:
            clear_db_tenant()


class SkillCloneView(APIView):
    permission_classes = [HasPermission("config", "edit")]

    def post(self, request: Request, skill_id: str) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "tenant_id required"}, status=status.HTTP_400_BAD_REQUEST)

        set_db_tenant(tenant_id)
        try:
            skill = ClassifierSkill.objects.get(tenant_id=tenant_id, id=skill_id)
            new_name = (request.data or {}).get("name", f"{skill.name} (clone)")
            cloned = ClassifierService.clone_skill(
                skill,
                new_name,
                actor_id=str(request.user.id),
                actor_role=getattr(request, "active_hat", ""),
            )
            return Response(
                {"id": str(cloned.id), "name": cloned.name, "status": cloned.status},
                status=status.HTTP_201_CREATED,
            )
        except ClassifierSkill.DoesNotExist:
            return Response({"detail": "not found"}, status=status.HTTP_404_NOT_FOUND)
        finally:
            clear_db_tenant()
