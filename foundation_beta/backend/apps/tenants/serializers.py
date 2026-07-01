"""DRF serializers for Tenant management."""
from rest_framework import serializers

from apps.tenants.models import Tenant, TenantPlanFeatures


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = [
            "id",
            "slug",
            "legal_name",
            "commercial_name",
            "vertical_spec_object_id",
            "plan_tier",
            "status",
            "config_json",
            "dpa_state",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TenantPlanFeaturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantPlanFeatures
        fields = [
            "tenant",
            "data_class_ceiling",
            "max_seats",
            "allow_agent_composition",
            "allow_tools_in_skills",
            "allow_email_connector",
            "allow_whatsapp_connector",
        ]
