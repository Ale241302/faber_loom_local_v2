"""Backend service for M20 Auto Update."""
from __future__ import annotations

import re

from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.updates.models import ClientRelease, SystemConfig, TenantUpdateChannel


SEMVER_RE = re.compile(r"^(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:[-+].*)?$")


def parse_semver(version: str) -> tuple[int, int, int]:
    match = SEMVER_RE.match(version or "")
    if not match:
        return (0, 0, 0)
    major = int(match.group(1))
    minor = int(match.group(2) or 0)
    patch = int(match.group(3) or 0)
    return (major, minor, patch)


def semver_lt(a: str, b: str) -> bool:
    return parse_semver(a) < parse_semver(b)


def get_min_supported_version() -> str:
    config, _ = SystemConfig.objects.get_or_create(
        key="min_supported_client_version",
        defaults={"value": "1.3.0"},
    )
    return config.value


def get_tenant_channel(tenant_id: str) -> str:
    set_db_tenant(tenant_id)
    try:
        channel_obj, _ = TenantUpdateChannel.objects.get_or_create(
            tenant_id=tenant_id,
            defaults={"channel": TenantUpdateChannel.Channel.STABLE},
        )
        return channel_obj.channel
    finally:
        clear_db_tenant()


def get_latest_release(platform: str, channel: str) -> ClientRelease | None:
    return (
        ClientRelease.objects.filter(
            platform=platform,
            channel=channel,
            retired_at__isnull=True,
        )
        .order_by("-published_at")
        .first()
    )


def build_update_info(tenant_id: str, platform: str) -> dict:
    channel = get_tenant_channel(tenant_id)
    release = get_latest_release(platform, channel)
    min_version = get_min_supported_version()

    if not release:
        return {
            "version": None,
            "feed_url": None,
            "channel": channel,
            "min_supported_client_version": min_version,
            "mandatory": False,
        }

    return {
        "version": release.version,
        "feed_url": release.feed_url,
        "channel": channel,
        "min_supported_client_version": min_version,
        "mandatory": semver_lt(release.version, min_version),
    }
