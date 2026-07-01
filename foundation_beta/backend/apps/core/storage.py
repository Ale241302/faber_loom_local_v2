"""MinIO / S3 path builder with tenant isolation and anti-traversal checks."""
from __future__ import annotations

import re
from pathlib import PurePosixPath
from uuid import UUID

SAFE_SEGMENT_RE = re.compile(r"^[a-zA-Z0-9_\-\.]+$")


def tenant_path(tenant_id: UUID, *segments: str) -> str:
    """Build a tenant-scoped MinIO path."""
    for segment in segments:
        if ".." in segment or not SAFE_SEGMENT_RE.match(segment):
            raise ValueError(f"Invalid storage path segment: {segment!r}")
    return str(PurePosixPath("/tenants", str(tenant_id), *segments))
