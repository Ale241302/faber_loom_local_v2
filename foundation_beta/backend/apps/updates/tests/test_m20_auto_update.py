"""M20 Auto Update backend tests."""
from __future__ import annotations

import pytest
from django.utils import timezone

from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.updates.models import ClientRelease, TenantUpdateChannel
from apps.updates.service import build_update_info, get_min_supported_version, semver_lt


pytestmark = pytest.mark.django_db


def test_semver_lt():
    assert semver_lt("1.2.3", "1.2.4")
    assert not semver_lt("1.3.0", "1.3.0")
    assert semver_lt("1.2.0", "1.3.0")


def test_min_supported_version_default():
    version = get_min_supported_version()
    assert version == "1.3.0"


def test_build_update_info_returns_latest_release(tenant, stable_release, min_version_config):
    set_db_tenant(tenant.id)
    try:
        info = build_update_info(str(tenant.id), "win")
    finally:
        clear_db_tenant()

    assert info["version"] == "1.3.5"
    assert info["feed_url"] == stable_release.feed_url
    assert info["channel"] == "stable"
    assert info["min_supported_client_version"] == "1.3.0"
    assert info["mandatory"] is False


def test_build_update_info_mandatory_when_below_min_supported(tenant, min_version_config):
    set_db_tenant(tenant.id)
    try:
        ClientRelease.objects.create(
            version="1.2.9",
            platform="win",
            channel="stable",
            feed_url="https://updates.example.com/old.yml",
        )
        info = build_update_info(str(tenant.id), "win")
    finally:
        clear_db_tenant()

    assert info["mandatory"] is True


def test_tenant_beta_channel(tenant):
    set_db_tenant(tenant.id)
    try:
        TenantUpdateChannel.objects.create(
            tenant=tenant,
            channel=TenantUpdateChannel.Channel.BETA,
        )
        ClientRelease.objects.create(
            version="1.4.0-beta.1",
            platform="win",
            channel="beta",
            feed_url="https://updates.example.com/beta.yml",
        )
        info = build_update_info(str(tenant.id), "win")
    finally:
        clear_db_tenant()

    assert info["channel"] == "beta"
    assert info["version"] == "1.4.0-beta.1"


def test_retired_release_not_considered(tenant, stable_release):
    set_db_tenant(tenant.id)
    try:
        retired = ClientRelease.objects.create(
            version="1.4.0",
            platform="win",
            channel="stable",
            feed_url="https://updates.example.com/retired.yml",
        )
        retired.retired_at = timezone.now()
        retired.save(update_fields=["retired_at"])

        info = build_update_info(str(tenant.id), "win")
    finally:
        clear_db_tenant()

    assert info["version"] == "1.3.5"
