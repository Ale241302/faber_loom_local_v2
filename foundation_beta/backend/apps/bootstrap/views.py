"""Bootstrap Wizard views for M07."""
from __future__ import annotations

import secrets
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.writer import AuditContext, AuditWriter
from apps.auth_session import totp as totp_helpers
from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.events.emit import emit_event
from apps.policy.gate import ActionContext, D9Gate
from apps.policy.models import DpaStatement
from apps.tenants.models import Tenant
from apps.users.models import Membership, MembershipStatus

from .models import EmailBinding, SystemAgent, TenantBootstrapProgress, VoiceProfile

User = get_user_model()

REQUIRED_STEPS = {
    "tenant_data",
    "owner_2fa",
    "mailbox",
    "kb_seed",
    "voice_profile",
    "dpa_signed",
    "seed_agents",
    "sandbox_ok",
}


class IsAuthenticated(permissions.IsAuthenticated):
    pass


def _get_or_create_progress(tenant_id: str) -> TenantBootstrapProgress:
    progress, _ = TenantBootstrapProgress.objects.get_or_create(
        tenant_id=tenant_id,
        defaults={"steps_completed": [], "steps_blocked": [], "sandbox_result": {}},
    )
    return progress


def _mark_step(progress: TenantBootstrapProgress, step: str) -> None:
    completed = set(progress.steps_completed or [])
    completed.add(step)
    progress.steps_completed = list(completed)
    progress.save(update_fields=["steps_completed", "updated_at"])


class InviteOwnerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, tenant_id: str) -> Response:
        email = str(request.data.get("email", "")).strip().lower()
        if not email:
            return Response({"detail": "email is required."}, status=status.HTTP_400_BAD_REQUEST)

        set_db_tenant(tenant_id)
        try:
            with transaction.atomic():
                user, _ = User.objects.get_or_create(
                    email=email,
                    defaults={"display_name": email.split("@")[0]},
                )
                if Membership.objects.filter(user=user, tenant_id=tenant_id).exists():
                    return Response(
                        {"detail": "User is already a member of this tenant."},
                        status=status.HTTP_409_CONFLICT,
                    )

                ttl_days = int(getattr(settings, "INVITATION_TTL_DAYS", 7))
                membership = Membership.objects.create(
                    user=user,
                    tenant_id=tenant_id,
                    roles=["owner"],
                    active_hat="owner",
                    status=MembershipStatus.INVITED,
                    invited_by_id=request.user.id,
                    invited_at=timezone.now(),
                )
                emit_event(
                    tenant_id=tenant_id,
                    event_type="user.invited",
                    payload={
                        "user_id": str(user.id),
                        "roles": ["owner"],
                        "invited_by": str(request.user.id),
                        "expires_at": (timezone.now() + timedelta(days=ttl_days)).isoformat(),
                    },
                )
        finally:
            clear_db_tenant()

        return Response({"membership_id": str(membership.id), "status": "invited"}, status=status.HTTP_201_CREATED)


class WizardStepView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, tenant_id: str, step: str) -> Response:
        set_db_tenant(tenant_id)
        try:
            with transaction.atomic():
                progress = _get_or_create_progress(tenant_id)
                tenant = Tenant.objects.get(id=tenant_id)

                if step == "tenant_data":
                    tenant.legal_name = request.data.get("legal_name", tenant.legal_name)
                    tenant.commercial_name = request.data.get("commercial_name", tenant.commercial_name)
                    tenant.slug = request.data.get("slug", tenant.slug)
                    tenant.save(update_fields=["legal_name", "commercial_name", "slug", "updated_at"])

                elif step == "owner_2fa":
                    owner_membership = Membership.objects.get(
                        tenant_id=tenant_id, roles__contains=["owner"], status=MembershipStatus.ACTIVE
                    )
                    owner = owner_membership.user
                    secret = totp_helpers.generate_totp_secret()
                    owner.totp_secret_encrypted = totp_helpers.encrypt_secret(secret)
                    backup_codes_plain, backup_codes_hashed = totp_helpers.generate_backup_codes(10)
                    owner.backup_codes_hashed = backup_codes_hashed
                    owner.save(update_fields=["totp_secret_encrypted", "backup_codes_hashed", "updated_at"])
                    emit_event(
                        tenant_id=tenant_id,
                        event_type="user.2fa_enabled",
                        payload={"user_id": str(owner.id), "method": "totp"},
                    )

                elif step == "mailbox":
                    EmailBinding.objects.create(
                        tenant_id=tenant_id,
                        provider=request.data.get("provider", EmailBinding.Provider.IMAP_SMTP),
                        account=request.data.get("account", ""),
                        credentials_encrypted=request.data.get("credentials_encrypted", ""),
                        is_default=True,
                    )
                    emit_event(
                        tenant_id=tenant_id,
                        event_type="mailbox.connected",
                        payload={"account": request.data.get("account", "")},
                    )

                elif step == "kb_seed":
                    emit_event(
                        tenant_id=tenant_id,
                        event_type="document.uploaded",
                        payload={"count": request.data.get("count", 0)},
                    )

                elif step == "voice_profile":
                    user_id = request.data.get("user_id")
                    VoiceProfile.objects.create(
                        tenant_id=tenant_id,
                        user_id=user_id or request.user.id,
                        persona=request.data.get("persona", ""),
                        tone=request.data.get("tone", ""),
                        glossary=request.data.get("glossary", []),
                        greeting=request.data.get("greeting", ""),
                        signature=request.data.get("signature", ""),
                        is_default=True,
                    )

                elif step == "dpa_signed":
                    dpa, _ = DpaStatement.objects.get_or_create(
                        tenant_id=tenant_id,
                        defaults={"status": DpaStatement.Status.MISSING, "version": "v1"},
                    )
                    dpa.status = DpaStatement.Status.SIGNED
                    dpa.signed_by_id = request.user.id
                    dpa.signed_at = timezone.now()
                    dpa.save(update_fields=["status", "signed_by", "signed_at", "updated_at"])
                    Tenant.objects.filter(id=tenant_id).update(dpa_state="signed")

                elif step == "seed_agents":
                    SystemAgent.objects.get_or_create(
                        tenant_id=tenant_id,
                        name="@router",
                        defaults={
                            "origin": "system",
                            "skill_md": "Clasifica inbound y enruta al agente adecuado.",
                            "status": SystemAgent.Status.SHADOW,
                        },
                    )
                    SystemAgent.objects.get_or_create(
                        tenant_id=tenant_id,
                        name="@cotizador",
                        defaults={
                            "origin": "system",
                            "skill_md": "Genera cotización / draft a partir del RFQ.",
                            "status": SystemAgent.Status.SHADOW,
                        },
                    )

                elif step == "sandbox_ok":
                    # Sandbox is executed via its own endpoint; this step just records success.
                    pass

                # Re-set tenant because step handlers may emit events that clear DB tenant context.
                set_db_tenant(tenant_id)
                _mark_step(progress, step)

                AuditWriter.write(
                    AuditContext(
                        tenant_id=tenant_id,
                        actor_id=request.user.id,
                        actor_role_at_decision=getattr(request, "active_hat", ""),
                    ),
                    action_id=f"bootstrap.step.{step}",
                    payload={"step": step},
                    emit=False,
                )
        finally:
            clear_db_tenant()

        return Response({"step": step, "status": "completed"})


class BootstrapStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, tenant_id: str) -> Response:
        set_db_tenant(tenant_id)
        try:
            tenant = Tenant.objects.get(id=tenant_id)
            progress = _get_or_create_progress(tenant_id)
            dpa = DpaStatement.objects.filter(tenant_id=tenant_id).first()
            return Response(
                {
                    "tenant_id": str(tenant_id),
                    "tenant_status": tenant.status,
                    "steps_completed": progress.steps_completed,
                    "steps_blocked": progress.steps_blocked,
                    "sandbox_result": progress.sandbox_result,
                    "dpa_status": dpa.status if dpa else "missing",
                    "can_activate": self._can_activate(tenant_id),
                }
            )
        finally:
            clear_db_tenant()

    def _can_activate(self, tenant_id: str) -> bool:
        progress = _get_or_create_progress(tenant_id)
        completed = set(progress.steps_completed or [])
        if not REQUIRED_STEPS.issubset(completed):
            return False
        dpa = DpaStatement.objects.filter(tenant_id=tenant_id).first()
        if not dpa or dpa.status != DpaStatement.Status.SIGNED:
            return False
        return True


class SandboxTestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, tenant_id: str) -> Response:
        set_db_tenant(tenant_id)
        try:
            with transaction.atomic():
                # Simulate an inbound RFQ with N1 data.
                action = ActionContext(
                    tenant_id=tenant_id,
                    data_class="N1",
                    source="email_body",
                    task_type="rfq_classification",
                    case_id="sandbox-rfq",
                )
                decision = D9Gate.evaluate(
                    actor_id=str(request.user.id),
                    actor_role=getattr(request, "active_hat", ""),
                    action=action,
                )

                # Ensure tenant context is active for progress writes.
                set_db_tenant(tenant_id)

                if not decision.allowed:
                    progress = _get_or_create_progress(tenant_id)
                    progress.sandbox_result = {
                        "passed": False,
                        "reason": decision.blocked_reason,
                    }
                    progress.save(update_fields=["sandbox_result", "updated_at"])
                    return Response(
                        {
                            "passed": False,
                            "reason": decision.blocked_reason,
                            "effective_classification": decision.effective_classification,
                        },
                        status=status.HTTP_423_LOCKED,
                    )

                # Simulate draft generation in Zone 3 (internal-only).
                draft = "Draft RFQ response generated in sandbox; no external egress."

                progress = _get_or_create_progress(tenant_id)
                progress.sandbox_result = {
                    "passed": True,
                    "draft": draft,
                    "approved_by": str(request.user.id),
                }
                progress.save(update_fields=["sandbox_result", "updated_at"])
                _mark_step(progress, "sandbox_ok")

                AuditWriter.write(
                    AuditContext(
                        tenant_id=tenant_id,
                        actor_id=request.user.id,
                        actor_role_at_decision=getattr(request, "active_hat", ""),
                    ),
                    action_id="bootstrap.sandbox.passed",
                    payload={"case_id": "sandbox-rfq"},
                    emit=False,
                )

                return Response({"passed": True, "draft": draft})
        finally:
            clear_db_tenant()


class ActivateTenantView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, tenant_id: str) -> Response:
        set_db_tenant(tenant_id)
        try:
            with transaction.atomic():
                tenant = Tenant.objects.get(id=tenant_id)
                progress = _get_or_create_progress(tenant_id)
                completed = set(progress.steps_completed or [])

                if tenant.status == Tenant.Status.ACTIVE:
                    return Response({"detail": "Tenant is already active."})

                missing = REQUIRED_STEPS - completed
                if missing:
                    return Response(
                        {"detail": "Missing required steps.", "missing": sorted(missing)},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                dpa = DpaStatement.objects.filter(tenant_id=tenant_id).first()
                if not dpa or dpa.status != DpaStatement.Status.SIGNED:
                    return Response(
                        {"detail": "DPA must be signed before activation."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                tenant.status = Tenant.Status.ACTIVE
                tenant.save(update_fields=["status", "updated_at"])

                emit_event(
                    tenant_id=tenant_id,
                    event_type="tenant.activated",
                    payload={"activated_by": str(request.user.id)},
                )

                AuditWriter.write(
                    AuditContext(
                        tenant_id=tenant_id,
                        actor_id=request.user.id,
                        actor_role_at_decision=getattr(request, "active_hat", ""),
                    ),
                    action_id="tenant.activated",
                    payload={"tenant_status": tenant.status},
                    emit=False,
                )

                return Response(
                    {
                        "tenant_id": str(tenant.id),
                        "status": tenant.status,
                        "activated_at": tenant.updated_at.isoformat(),
                    }
                )
        finally:
            clear_db_tenant()
