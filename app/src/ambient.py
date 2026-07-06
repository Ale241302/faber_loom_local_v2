"""Ambient cycle orchestrator for E2-5.

The orchestrator runs read-only detectors scoped to a workspace/tenant and creates
WorkLoom items (drafts) with evidence. It never executes irreversible actions.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import sqlite3

from .audit import audit_writer
from .context import Context, DEFAULT_TENANT_ID, SYSTEM_WORKSPACE_ID, system_context
from .db import (
    connect,
    db_session,
    get_database_path,
    new_id,
    row_to_dict,
    utc_now,
)
from .kb import insert_draft
from .models import SCHEMA_VERSION
from .ambient_detectors import (
    DETECTOR_REGISTRY,
    AmbientFinding,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

AMBIENT_SCHEDULER_INTERVAL_SECONDS = 60
AMBIENT_ACTOR_ID = "ambient"
AMBIENT_ACTOR_ROLE = "system"


# ---------------------------------------------------------------------------
# System context helpers
# ---------------------------------------------------------------------------

def ambient_context(
    tenant_id: str | None = None,
    workspace_id: str = SYSTEM_WORKSPACE_ID,
) -> Context:
    return Context(
        workspace_id=workspace_id,
        tenant_id=tenant_id or DEFAULT_TENANT_ID,
        user_id=AMBIENT_ACTOR_ID,
        actor_id=AMBIENT_ACTOR_ID,
        actor_role_at_decision=AMBIENT_ACTOR_ROLE,
    )


# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------

def get_ambient_config(conn: sqlite3.Connection, tenant_id: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM ambient_config WHERE tenant_id = ?",
        (tenant_id,),
    ).fetchone()
    if row is None:
        return None
    data = row_to_dict(row)
    data["global_enabled"] = bool(data.get("global_enabled", 1))
    return data


def get_ambient_workspace_config(
    conn: sqlite3.Connection,
    tenant_id: str,
    workspace_id: str,
) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM ambient_workspace_config WHERE tenant_id = ? AND workspace_id = ?",
        (tenant_id, workspace_id),
    ).fetchone()
    if row is None:
        return None
    data = row_to_dict(row)
    data["enabled"] = bool(data.get("enabled", 1))
    data["detector_allowlist"] = json.loads(data.get("detector_allowlist_json") or "[]")
    data["excluded_detector_slugs"] = json.loads(data.get("excluded_detector_slugs_json") or "[]")
    return data


def list_active_workspaces(
    conn: sqlite3.Connection,
    tenant_id: str,
) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT id, name, slug FROM workspace
        WHERE tenant_id = ?
        ORDER BY created_at ASC
        """,
        (tenant_id,),
    ).fetchall()
    return [row_to_dict(row) for row in rows]


# ---------------------------------------------------------------------------
# Cycle / detector_run / proposal CRUD helpers
# ---------------------------------------------------------------------------

def create_ambient_cycle(
    conn: sqlite3.Connection,
    tenant_id: str,
    workspace_id: str | None,
    trigger: str,
    budget_usd: float,
) -> dict[str, Any]:
    cycle_id = new_id("cyc")
    now = utc_now()
    conn.execute(
        """
        INSERT INTO ambient_cycle (
            id, tenant_id, workspace_id, status, trigger, started_at,
            budget_usd, kill_switch_state_json, evidence_json,
            actor_id, actor_role_at_decision, schema_version, source_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            cycle_id,
            tenant_id,
            workspace_id,
            "running",
            trigger,
            now,
            budget_usd,
            json.dumps({"global": True, "workspace": True}),
            json.dumps({}),
            AMBIENT_ACTOR_ID,
            AMBIENT_ACTOR_ROLE,
            SCHEMA_VERSION,
            "v1",
        ),
    )
    return row_to_dict(
        conn.execute(
            "SELECT * FROM ambient_cycle WHERE id = ?",
            (cycle_id,),
        ).fetchone()
    )


def update_ambient_cycle(
    conn: sqlite3.Connection,
    cycle_id: str,
    **fields: Any,
) -> dict[str, Any] | None:
    allowed = {
        "status",
        "ended_at",
        "detectors_run",
        "detectors_failed",
        "proposals_created",
        "proposals_visible",
        "proposals_dark",
        "cost_usd",
        "utility_score_pct",
        "kill_switch_state_json",
        "evidence_json",
    }
    updates: dict[str, Any] = {}
    for k, v in fields.items():
        if k not in allowed:
            continue
        if k in ("kill_switch_state_json", "evidence_json") and isinstance(v, dict):
            v = json.dumps(v, ensure_ascii=False)
        updates[k] = v
    if not updates:
        return None
    sets = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [cycle_id]
    conn.execute(
        f"UPDATE ambient_cycle SET {sets} WHERE id = ?",
        values,
    )
    row = conn.execute("SELECT * FROM ambient_cycle WHERE id = ?", (cycle_id,)).fetchone()
    return row_to_dict(row) if row else None


def create_detector_run(
    conn: sqlite3.Connection,
    cycle_id: str,
    tenant_id: str,
    workspace_id: str | None,
    detector_slug: str,
) -> dict[str, Any]:
    run_id = new_id("dtr")
    now = utc_now()
    conn.execute(
        """
        INSERT INTO ambient_detector_run (
            id, cycle_id, detector_slug, workspace_id, tenant_id, status,
            evidence_json, actor_id, actor_role_at_decision, schema_version,
            source_version, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            cycle_id,
            detector_slug,
            workspace_id,
            tenant_id,
            "ok",
            json.dumps({}),
            AMBIENT_ACTOR_ID,
            AMBIENT_ACTOR_ROLE,
            SCHEMA_VERSION,
            "v1",
            now,
        ),
    )
    return row_to_dict(
        conn.execute("SELECT * FROM ambient_detector_run WHERE id = ?", (run_id,)).fetchone()
    )


def update_detector_run(
    conn: sqlite3.Connection,
    run_id: str,
    **fields: Any,
) -> None:
    allowed = {
        "status",
        "proposals_count",
        "cost_usd",
        "latency_ms",
        "error_message",
        "backoff_until",
        "consecutive_failures",
        "evidence_json",
    }
    updates: dict[str, Any] = {}
    for k, v in fields.items():
        if k not in allowed:
            continue
        if k == "evidence_json" and isinstance(v, dict):
            v = json.dumps(v, ensure_ascii=False)
        updates[k] = v
    if not updates:
        return
    sets = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [run_id]
    conn.execute(
        f"UPDATE ambient_detector_run SET {sets} WHERE id = ?",
        values,
    )


def _dedup_key(detector_slug: str, target_type: str, target_id: str) -> str:
    bucket = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H")
    raw = f"{detector_slug}|{target_type}|{target_id}|{bucket}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def find_existing_proposal(
    conn: sqlite3.Connection,
    tenant_id: str,
    workspace_id: str,
    dedup_key: str,
) -> dict[str, Any] | None:
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat().replace("+00:00", "Z")
    row = conn.execute(
        """
        SELECT * FROM ambient_proposal
        WHERE tenant_id = ? AND workspace_id = ? AND dedup_key = ?
              AND state IN ('dark', 'visible', 'merged')
              AND created_at > ?
        ORDER BY created_at DESC LIMIT 1
        """,
        (tenant_id, workspace_id, dedup_key, since),
    ).fetchone()
    return row_to_dict(row) if row else None


def merge_proposal_evidence(
    conn: sqlite3.Connection,
    proposal_id: str,
    evidence_json: dict[str, Any],
) -> None:
    now = utc_now()
    conn.execute(
        """
        UPDATE ambient_proposal
        SET occurrence_count = occurrence_count + 1,
            evidence_json = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (
            json.dumps({"latest": evidence_json, "merged_at": now}),
            now,
            proposal_id,
        ),
    )


def create_ambient_proposal(
    conn: sqlite3.Connection,
    cycle_id: str,
    tenant_id: str,
    workspace_id: str,
    finding: AmbientFinding,
    state: str,
    workloom_item_id: str | None,
) -> dict[str, Any]:
    proposal_id = new_id("prp")
    now = utc_now()
    dedup_key = _dedup_key(finding.detector_slug, finding.target_type, finding.target_id)
    conn.execute(
        """
        INSERT INTO ambient_proposal (
            id, cycle_id, workspace_id, tenant_id, detector_slug, target_type,
            target_id, dedup_key, severity, title, description, suggested_action,
            evidence_json, state, workloom_item_id, occurrence_count,
            actor_id, actor_role_at_decision, schema_version, source_version,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            proposal_id,
            cycle_id,
            workspace_id,
            tenant_id,
            finding.detector_slug,
            finding.target_type,
            finding.target_id,
            dedup_key,
            finding.severity,
            finding.title,
            finding.description,
            finding.suggested_action,
            json.dumps(finding.evidence_json, ensure_ascii=False),
            state,
            workloom_item_id,
            1,
            AMBIENT_ACTOR_ID,
            AMBIENT_ACTOR_ROLE,
            SCHEMA_VERSION,
            "v1",
            now,
            now,
        ),
    )
    return row_to_dict(
        conn.execute("SELECT * FROM ambient_proposal WHERE id = ?", (proposal_id,)).fetchone()
    )


# ---------------------------------------------------------------------------
# Window / budget / utility helpers
# ---------------------------------------------------------------------------

def is_within_window(config: dict[str, Any]) -> bool:
    tz_name = config.get("cycle_window_tz", "America/Bogota")
    try:
        import zoneinfo
        tz = zoneinfo.ZoneInfo(tz_name)
    except Exception:  # pragma: no cover - fallback if zoneinfo missing
        tz = timezone.utc
    now = datetime.now(tz)
    start_str = config.get("cycle_window_start", "06:00")
    end_str = config.get("cycle_window_end", "22:00")
    start_time = datetime.strptime(start_str, "%H:%M").time()
    end_time = datetime.strptime(end_str, "%H:%M").time()
    current_time = now.time()
    if start_time <= end_time:
        return start_time <= current_time <= end_time
    return current_time >= start_time or current_time <= end_time


def compute_workspace_budget(conn: sqlite3.Connection, workspace_id: str, tenant_id: str) -> float:
    row = conn.execute(
        """
        SELECT budget_cap_usd FROM workspace_routing_policy
        WHERE workspace_id = ? AND tenant_id = ?
        """,
        (workspace_id, tenant_id),
    ).fetchone()
    return float(row["budget_cap_usd"] or 0.0) if row else 0.0


def compute_tenant_daily_usage(conn: sqlite3.Connection, tenant_id: str) -> float:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    row = conn.execute(
        """
        SELECT COALESCE(SUM(cost_total_usd), 0) AS spent
        FROM usage_record
        WHERE tenant_id = ? AND date(created_at) = ?
        """,
        (tenant_id, today),
    ).fetchone()
    return float(row["spent"] or 0.0)


def should_run_critical_cycle(
    conn: sqlite3.Connection,
    tenant_id: str,
    workspace_id: str,
) -> bool:
    """Return True if there are critical conditions that justify a cycle outside window."""

    # routine_run failed in last hour
    since = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat().replace("+00:00", "Z")
    failed = conn.execute(
        """
        SELECT 1 FROM routine_run
        WHERE tenant_id = ? AND workspace_id = ? AND status = 'failed' AND created_at > ?
        LIMIT 1
        """,
        (tenant_id, workspace_id, since),
    ).fetchone()
    if failed:
        return True

    # budget above 90%
    budget = compute_workspace_budget(conn, workspace_id, tenant_id)
    if budget > 0:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        spent_row = conn.execute(
            """
            SELECT COALESCE(SUM(cost_total_usd), 0) AS spent
            FROM usage_record
            WHERE tenant_id = ? AND workspace_id = ? AND date(created_at) = ?
            """,
            (tenant_id, workspace_id, today),
        ).fetchone()
        spent = float(spent_row["spent"] or 0.0)
        if spent / budget >= 0.9:
            return True

    return False


def count_recent_proposals(
    conn: sqlite3.Connection,
    tenant_id: str,
    workspace_id: str | None,
    days: int,
) -> dict[str, int]:
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat().replace("+00:00", "Z")
    ws_clause = "AND workspace_id = ?" if workspace_id else ""
    params: list[Any] = [tenant_id, since]
    if workspace_id:
        params.append(workspace_id)

    created = conn.execute(
        f"""
        SELECT COUNT(*) FROM ambient_proposal
        WHERE tenant_id = ? AND created_at > ? {ws_clause}
        """,
        params,
    ).fetchone()[0]

    accepted = conn.execute(
        f"""
        SELECT COUNT(*) FROM ambient_proposal
        WHERE tenant_id = ? AND created_at > ? {ws_clause} AND accepted_at IS NOT NULL
        """,
        params,
    ).fetchone()[0]

    ignored = conn.execute(
        f"""
        SELECT COUNT(*) FROM ambient_proposal
        WHERE tenant_id = ? AND created_at > ? {ws_clause}
              AND state IN ('visible', 'dark') AND accepted_at IS NULL
        """,
        params,
    ).fetchone()[0]

    return {"created": created, "accepted": accepted, "ignored": ignored}


def compute_utility_score(
    conn: sqlite3.Connection,
    tenant_id: str,
    workspace_id: str | None,
    days: int = 7,
) -> float:
    counts = count_recent_proposals(conn, tenant_id, workspace_id, days)
    if counts["created"] == 0:
        return 0.0
    return round((counts["accepted"] / counts["created"]) * 100, 2)


def should_pause_for_utility_breaker(
    conn: sqlite3.Connection,
    tenant_id: str,
    threshold_pct: int,
    days: int = 7,
    consecutive_cycles: int = 3,
) -> bool:
    """Utility breaker: true if last N cycles all below threshold."""

    rows = conn.execute(
        """
        SELECT utility_score_pct FROM ambient_cycle
        WHERE tenant_id = ? AND status = 'completed'
        ORDER BY started_at DESC
        LIMIT ?
        """,
        (tenant_id, consecutive_cycles),
    ).fetchall()
    if len(rows) < consecutive_cycles:
        return False
    return all(
        (row["utility_score_pct"] or 0) < threshold_pct for row in rows
    )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class AmbientOrchestrator:
    """Runs ambient cycles for a tenant/workspace."""

    def __init__(self) -> None:
        self._lock = threading.Lock()

    def run_cycle(
        self,
        conn: sqlite3.Connection,
        tenant_id: str,
        workspace_id: str | None = None,
        trigger: str = "scheduled",
    ) -> dict[str, Any]:
        """Run one ambient cycle. Returns the closed cycle record."""

        with self._lock:
            return self._run_cycle_locked(conn, tenant_id, workspace_id, trigger)

    def _run_cycle_locked(
        self,
        conn: sqlite3.Connection,
        tenant_id: str,
        workspace_id: str | None,
        trigger: str,
    ) -> dict[str, Any]:
        config = get_ambient_config(conn, tenant_id)
        if config is None:
            raise RuntimeError(f"No ambient_config for tenant {tenant_id}")

        # Global kill switch
        if not config.get("global_enabled", True):
            logger.info("Ambient cycle skipped: global kill switch")
            raise RuntimeError("Global kill switch is active")

        # Utility breaker
        if should_pause_for_utility_breaker(
            conn,
            tenant_id,
            int(config.get("utility_threshold_pct", 20)),
        ):
            logger.warning("Ambient cycle skipped: utility breaker")
            raise RuntimeError("Utility breaker active")

        # Determine workspaces to scan
        if workspace_id is None:
            workspaces = list_active_workspaces(conn, tenant_id)
        else:
            ws = conn.execute(
                "SELECT id, name, slug FROM workspace WHERE id = ? AND tenant_id = ?",
                (workspace_id, tenant_id),
            ).fetchone()
            workspaces = [row_to_dict(ws)] if ws else []

        # Budget for this cycle: pct of total tenant daily budget across workspaces
        total_budget = 0.0
        for ws in workspaces:
            total_budget += compute_workspace_budget(conn, ws["id"], tenant_id)
        if total_budget <= 0:
            total_budget = 1.0  # nominal budget to avoid div by zero
        cycle_budget = total_budget * (float(config.get("budget_pct_of_router_daily", 5.0)) / 100.0)

        cycle = create_ambient_cycle(conn, tenant_id, workspace_id, trigger, cycle_budget)
        cycle_id = cycle["id"]

        stats = {
            "detectors_run": 0,
            "detectors_failed": 0,
            "proposals_created": 0,
            "proposals_visible": 0,
            "proposals_dark": 0,
            "cost_usd": 0.0,
        }

        evidence: dict[str, Any] = {"workspaces": []}

        try:
            for ws in workspaces:
                ws_id = ws["id"]
                ws_evidence = self._process_workspace(
                    conn,
                    tenant_id,
                    ws_id,
                    cycle_id,
                    config,
                    cycle_budget,
                    stats,
                )
                evidence["workspaces"].append({"workspace_id": ws_id, "summary": ws_evidence})

            # Compute utility score for this cycle (based on last 7 days)
            utility = compute_utility_score(conn, tenant_id, workspace_id, days=7)

            closed = update_ambient_cycle(
                conn,
                cycle_id,
                status="completed",
                ended_at=utc_now(),
                detectors_run=stats["detectors_run"],
                detectors_failed=stats["detectors_failed"],
                proposals_created=stats["proposals_created"],
                proposals_visible=stats["proposals_visible"],
                proposals_dark=stats["proposals_dark"],
                cost_usd=round(stats["cost_usd"], 6),
                utility_score_pct=int(utility),
                evidence_json=json.dumps(evidence, ensure_ascii=False),
            )
            workspace_ids = [ws["id"] for ws in workspaces]
            self._write_cycle_audit(conn, tenant_id, workspace_ids, cycle_id, stats, utility)
            return closed or cycle
        except Exception as exc:
            logger.exception("Ambient cycle failed")
            update_ambient_cycle(
                conn,
                cycle_id,
                status="killed",
                ended_at=utc_now(),
                detectors_run=stats["detectors_run"],
                detectors_failed=stats["detectors_failed"] + 1,
                proposals_created=stats["proposals_created"],
                proposals_visible=stats["proposals_visible"],
                proposals_dark=stats["proposals_dark"],
                cost_usd=round(stats["cost_usd"], 6),
                evidence_json=json.dumps({"error": str(exc)}),
            )
            raise

    def _process_workspace(
        self,
        conn: sqlite3.Connection,
        tenant_id: str,
        workspace_id: str,
        cycle_id: str,
        config: dict[str, Any],
        cycle_budget: float,
        stats: dict[str, Any],
    ) -> dict[str, Any]:
        ws_config = get_ambient_workspace_config(conn, tenant_id, workspace_id)
        if ws_config is not None and not ws_config.get("enabled", True):
            logger.info("Workspace %s skipped: kill switch", workspace_id)
            return {"skipped": True, "reason": "workspace_kill_switch"}

        # Frequency guard: skip if per-workspace cycle ran too recently
        last_run = conn.execute(
            """
            SELECT started_at FROM ambient_cycle
            WHERE tenant_id = ? AND workspace_id = ? AND status = 'completed'
            ORDER BY started_at DESC LIMIT 1
            """,
            (tenant_id, workspace_id),
        ).fetchone()
        min_minutes = int(config.get("per_workspace_frequency_min", 60))
        if last_run:
            last_dt = datetime.fromisoformat(last_run["started_at"].replace("Z", "+00:00"))
            if datetime.now(timezone.utc) - last_dt < timedelta(minutes=min_minutes):
                return {"skipped": True, "reason": "frequency_guard"}

        # Determine dark mode
        first_cycle_dt = conn.execute(
            "SELECT started_at FROM ambient_cycle WHERE tenant_id = ? ORDER BY started_at ASC LIMIT 1",
            (tenant_id,),
        ).fetchone()
        dark_days = int(config.get("dark_launch_days", 14))
        dark_mode = True
        if first_cycle_dt:
            first_dt = datetime.fromisoformat(first_cycle_dt["started_at"].replace("Z", "+00:00"))
            dark_mode = (datetime.now(timezone.utc) - first_dt) < timedelta(days=dark_days)

        # Allowlist
        allowlist: list[str] | None = None
        excluded: list[str] = []
        if ws_config:
            allowlist = ws_config.get("detector_allowlist") or None
            excluded = ws_config.get("excluded_detector_slugs") or []

        detector_slugs = list(DETECTOR_REGISTRY.keys())
        if allowlist:
            detector_slugs = [s for s in detector_slugs if s in allowlist]
        detector_slugs = [s for s in detector_slugs if s not in excluded]

        ws_evidence: dict[str, Any] = {"detectors": []}
        ctx = ambient_context(tenant_id=tenant_id, workspace_id=workspace_id)

        max_proposals = int(config.get("max_proposals_per_cycle", 10))
        proposals_so_far = 0

        for slug in detector_slugs:
            # Check cost overrun
            if stats["cost_usd"] >= cycle_budget * 1.5:
                logger.warning("Cycle cost overrun: stopping detectors")
                ws_evidence["detectors"].append({"slug": slug, "status": "skipped_budget"})
                update_ambient_cycle(conn, cycle_id, status="cost_overrun")
                break

            # Workspace kill switch re-check
            ws_cfg = get_ambient_workspace_config(conn, tenant_id, workspace_id)
            if ws_cfg is not None and not ws_cfg.get("enabled", True):
                ws_evidence["detectors"].append({"slug": slug, "status": "skipped_kill"})
                continue

            detector_start = time.time()
            detector_run = create_detector_run(conn, cycle_id, tenant_id, workspace_id, slug)

            try:
                detector_fn = DETECTOR_REGISTRY[slug]
                findings = detector_fn(ctx, conn)
                latency_ms = int((time.time() - detector_start) * 1000)

                visible_count = 0
                dark_count = 0
                merged_count = 0
                for finding in findings:
                    if proposals_so_far >= max_proposals:
                        break
                    result = self._handle_finding(
                        conn,
                        ctx,
                        cycle_id,
                        workspace_id,
                        finding,
                        dark_mode,
                    )
                    proposals_so_far += 1
                    if result["state"] == "visible":
                        visible_count += 1
                    elif result["state"] == "dark":
                        dark_count += 1
                    elif result["state"] == "merged":
                        merged_count += 1

                update_detector_run(
                    conn,
                    detector_run["id"],
                    status="ok",
                    proposals_count=len(findings),
                    latency_ms=latency_ms,
                    evidence_json={"findings_count": len(findings)},
                )

                stats["detectors_run"] += 1
                stats["proposals_created"] += len(findings)
                stats["proposals_visible"] += visible_count
                stats["proposals_dark"] += dark_count
                ws_evidence["detectors"].append({
                    "slug": slug,
                    "status": "ok",
                    "findings": len(findings),
                    "visible": visible_count,
                    "dark": dark_count,
                    "merged": merged_count,
                })
            except Exception as exc:
                latency_ms = int((time.time() - detector_start) * 1000)
                logger.exception("Detector %s failed", slug)
                update_detector_run(
                    conn,
                    detector_run["id"],
                    status="failed",
                    error_message=str(exc),
                    latency_ms=latency_ms,
                )
                stats["detectors_run"] += 1
                stats["detectors_failed"] += 1
                ws_evidence["detectors"].append({"slug": slug, "status": "failed", "error": str(exc)})

        return ws_evidence

    def _handle_finding(
        self,
        conn: sqlite3.Connection,
        ctx: Context,
        cycle_id: str,
        workspace_id: str,
        finding: AmbientFinding,
        dark_mode: bool,
    ) -> dict[str, Any]:
        dedup_key = _dedup_key(finding.detector_slug, finding.target_type, finding.target_id)
        existing = find_existing_proposal(conn, ctx.tenant_id, workspace_id, dedup_key)
        if existing:
            merge_proposal_evidence(conn, existing["id"], finding.evidence_json)
            return {"state": "merged", "proposal_id": existing["id"]}

        workloom_item_id: str | None = None
        state = "dark" if dark_mode else "visible"

        if not dark_mode:
            # Create a draft as the WorkLoom item
            draft = insert_draft(
                ctx.with_workspace(workspace_id),
                conn,
                chat_id=None,
                task="ambient_proposal",
                subject=finding.title,
                body_md=f"{finding.description}\n\n**Sugerencia:** {finding.suggested_action}",
                hard_facts=[],
                sources=[],
                blockers=[],
                warnings=[],
                requires_confirmation=False,
                status="draft",
                source_version="ambient-v1",
            )
            workloom_item_id = draft["id"]

        proposal = create_ambient_proposal(
            conn,
            cycle_id,
            ctx.tenant_id,
            workspace_id,
            finding,
            state,
            workloom_item_id,
        )
        return {"state": state, "proposal_id": proposal["id"], "workloom_item_id": workloom_item_id}

    def _write_cycle_audit(
        self,
        conn: sqlite3.Connection,
        tenant_id: str,
        workspace_ids: list[str],
        cycle_id: str,
        stats: dict[str, Any],
        utility: float,
    ) -> None:
        for ws_id in workspace_ids:
            ctx = ambient_context(tenant_id=tenant_id, workspace_id=ws_id)
            audit_writer.write(
                ctx,
                conn,
                action="ambient_cycle.completed",
                payload={
                    "cycle_id": cycle_id,
                    "tenant_id": tenant_id,
                    "workspace_id": ws_id,
                    "detectors_run": stats["detectors_run"],
                    "detectors_failed": stats["detectors_failed"],
                    "proposals_created": stats["proposals_created"],
                    "proposals_visible": stats["proposals_visible"],
                    "proposals_dark": stats["proposals_dark"],
                    "cost_usd": round(stats["cost_usd"], 6),
                    "utility_score_pct": int(utility),
                },
                correlation_id=cycle_id,
                mirror_jsonl=False,
            )


# Global orchestrator instance
_orchestrator: AmbientOrchestrator | None = None


def get_orchestrator() -> AmbientOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AmbientOrchestrator()
    return _orchestrator


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

_scheduler_thread: threading.Thread | None = None
_scheduler_stop_event = threading.Event()


def _scheduler_loop() -> None:
    """Background scheduler loop: wakes every minute and triggers cycles."""

    logger.info("Ambient scheduler started")
    while not _scheduler_stop_event.is_set():
        try:
            with db_session() as conn:
                # Support default tenant only for this MVP. Multi-tenant scheduler is E2-3+.
                tenant_id = DEFAULT_TENANT_ID
                config = get_ambient_config(conn, tenant_id)
                if config is None or not config.get("global_enabled", True):
                    time.sleep(AMBIENT_SCHEDULER_INTERVAL_SECONDS)
                    continue

                # Global frequency guard
                last_global = conn.execute(
                    """
                    SELECT started_at FROM ambient_cycle
                    WHERE tenant_id = ? AND workspace_id IS NULL AND status = 'completed'
                    ORDER BY started_at DESC LIMIT 1
                    """,
                    (tenant_id,),
                ).fetchone()

                min_global_minutes = int(config.get("global_frequency_min", 30))
                run_global = True
                if last_global:
                    last_dt = datetime.fromisoformat(last_global["started_at"].replace("Z", "+00:00"))
                    if datetime.now(timezone.utc) - last_dt < timedelta(minutes=min_global_minutes):
                        run_global = False

                if run_global and (is_within_window(config) or _any_critical_event(conn, tenant_id)):
                    try:
                        get_orchestrator().run_cycle(conn, tenant_id, trigger="scheduled")
                    except Exception:
                        logger.exception("Scheduled ambient cycle failed")
        except Exception:
            logger.exception("Ambient scheduler error")

        time.sleep(AMBIENT_SCHEDULER_INTERVAL_SECONDS)


def _any_critical_event(conn: sqlite3.Connection, tenant_id: str) -> bool:
    """Return True if any workspace has a critical event justifying off-window run."""

    rows = conn.execute(
        """
        SELECT id FROM workspace
        WHERE tenant_id = ?
        """,
        (tenant_id,),
    ).fetchall()
    for row in rows:
        if should_run_critical_cycle(conn, tenant_id, row["id"]):
            return True
    return False


def start_ambient_scheduler() -> None:
    """Start the background ambient scheduler thread."""

    global _scheduler_thread
    if _scheduler_thread is not None and _scheduler_thread.is_alive():
        return
    _scheduler_stop_event.clear()
    _scheduler_thread = threading.Thread(target=_scheduler_loop, daemon=True)
    _scheduler_thread.start()


def stop_ambient_scheduler() -> None:
    """Signal the scheduler to stop."""

    _scheduler_stop_event.set()


# ---------------------------------------------------------------------------
# Public helpers for API / tests
# ---------------------------------------------------------------------------

def trigger_ambient_cycle(
    conn: sqlite3.Connection,
    tenant_id: str,
    workspace_id: str | None = None,
) -> dict[str, Any]:
    """Manually trigger an ambient cycle."""

    return get_orchestrator().run_cycle(conn, tenant_id, workspace_id, trigger="manual")


def ambient_metrics(
    conn: sqlite3.Connection,
    tenant_id: str,
    workspace_id: str | None = None,
    days: int = 7,
) -> dict[str, Any]:
    """Return aggregated ambient metrics."""

    counts = count_recent_proposals(conn, tenant_id, workspace_id, days)
    total_budget = 0.0
    if workspace_id:
        total_budget = compute_workspace_budget(conn, workspace_id, tenant_id)
    else:
        row = conn.execute(
            """
            SELECT COALESCE(SUM(budget_cap_usd), 0) AS total
            FROM workspace_routing_policy
            WHERE tenant_id = ?
            """,
            (tenant_id,),
        ).fetchone()
        total_budget = float(row["total"] or 0.0)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    spent_row = conn.execute(
        """
        SELECT COALESCE(SUM(cost_usd), 0) AS spent
        FROM ambient_cycle
        WHERE tenant_id = ? AND date(started_at) = ?
        """ + (" AND workspace_id = ?" if workspace_id else ""),
        (tenant_id, today) + ((workspace_id,) if workspace_id else ()),
    ).fetchone()
    cost = float(spent_row["spent"] or 0.0)

    utility = compute_utility_score(conn, tenant_id, workspace_id, days)
    noise = 0.0
    if counts["created"] > 0:
        noise = round((counts["ignored"] / counts["created"]) * 100, 2)

    return {
        "tenant_id": tenant_id,
        "workspace_id": workspace_id,
        "period_days": days,
        "proposals_created": counts["created"],
        "proposals_visible": counts["created"] - counts["accepted"] - counts["ignored"],
        "proposals_accepted": counts["accepted"],
        "proposals_ignored": counts["ignored"],
        "utility_pct": utility,
        "noise_pct": noise,
        "cost_usd": cost,
        "budget_usd": total_budget,
    }


def set_kill_switch(
    conn: sqlite3.Connection,
    tenant_id: str,
    enabled: bool,
    workspace_id: str | None = None,
) -> dict[str, Any]:
    """Enable or disable the ambient kill switch."""

    now = utc_now()
    if workspace_id is None:
        conn.execute(
            """
            UPDATE ambient_config
            SET global_enabled = ?, updated_at = ?
            WHERE tenant_id = ?
            """,
            (1 if enabled else 0, now, tenant_id),
        )
        return {"scope": "global", "enabled": enabled}

    existing = conn.execute(
        """
        SELECT id FROM ambient_workspace_config
        WHERE tenant_id = ? AND workspace_id = ?
        """,
        (tenant_id, workspace_id),
    ).fetchone()
    if existing:
        conn.execute(
            """
            UPDATE ambient_workspace_config
            SET enabled = ?, updated_at = ?
            WHERE id = ?
            """,
            (1 if enabled else 0, now, existing["id"]),
        )
    else:
        cfg_id = new_id("wcfg")
        conn.execute(
            """
            INSERT INTO ambient_workspace_config (
                id, workspace_id, tenant_id, enabled,
                actor_id, actor_role_at_decision, schema_version,
                source_version, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cfg_id,
                workspace_id,
                tenant_id,
                1 if enabled else 0,
                AMBIENT_ACTOR_ID,
                AMBIENT_ACTOR_ROLE,
                SCHEMA_VERSION,
                "v1",
                now,
                now,
            ),
        )
    return {"scope": "workspace", "workspace_id": workspace_id, "enabled": enabled}


def update_ambient_config(
    conn: sqlite3.Connection,
    tenant_id: str,
    updates: dict[str, Any],
) -> dict[str, Any] | None:
    """Apply allowed updates to ambient_config."""

    allowed = {
        "global_enabled",
        "cycle_window_start",
        "cycle_window_end",
        "cycle_window_tz",
        "global_frequency_min",
        "per_workspace_frequency_min",
        "budget_pct_of_router_daily",
        "max_proposals_per_cycle",
        "dark_launch_days",
        "utility_threshold_pct",
        "cost_overrun_pct",
    }
    fields = {k: v for k, v in updates.items() if k in allowed}
    if not fields:
        return get_ambient_config(conn, tenant_id)

    sets = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [utc_now(), tenant_id]
    conn.execute(
        f"UPDATE ambient_config SET {sets}, updated_at = ? WHERE tenant_id = ?",
        values,
    )
    return get_ambient_config(conn, tenant_id)


def update_ambient_workspace_config(
    conn: sqlite3.Connection,
    tenant_id: str,
    workspace_id: str,
    updates: dict[str, Any],
) -> dict[str, Any] | None:
    """Apply allowed updates to ambient_workspace_config."""

    allowed = {"enabled", "detector_allowlist", "excluded_detector_slugs"}
    fields: dict[str, Any] = {}
    for k, v in updates.items():
        if k not in allowed:
            continue
        if k in ("detector_allowlist", "excluded_detector_slugs") and isinstance(v, list):
            fields[f"{k}_json"] = json.dumps(v, ensure_ascii=False)
        else:
            fields[k] = v
    if not fields:
        return get_ambient_workspace_config(conn, tenant_id, workspace_id)

    existing = conn.execute(
        """
        SELECT id FROM ambient_workspace_config
        WHERE tenant_id = ? AND workspace_id = ?
        """,
        (tenant_id, workspace_id),
    ).fetchone()
    now = utc_now()
    if existing:
        sets = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [now, existing["id"]]
        conn.execute(
            f"UPDATE ambient_workspace_config SET {sets}, updated_at = ? WHERE id = ?",
            values,
        )
    else:
        cfg_id = new_id("wcfg")
        defaults = {
            "enabled": 1,
            "detector_allowlist_json": "[]",
            "excluded_detector_slugs_json": "[]",
        }
        defaults.update(fields)
        conn.execute(
            """
            INSERT INTO ambient_workspace_config (
                id, workspace_id, tenant_id, enabled, detector_allowlist_json,
                excluded_detector_slugs_json, actor_id, actor_role_at_decision,
                schema_version, source_version, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cfg_id,
                workspace_id,
                tenant_id,
                defaults["enabled"],
                defaults["detector_allowlist_json"],
                defaults["excluded_detector_slugs_json"],
                AMBIENT_ACTOR_ID,
                AMBIENT_ACTOR_ROLE,
                SCHEMA_VERSION,
                "v1",
                now,
                now,
            ),
        )
    return get_ambient_workspace_config(conn, tenant_id, workspace_id)


def seed_ambient_config(conn: sqlite3.Connection, tenant_id: str) -> None:
    """Seed default ambient config and detector registry for a tenant."""

    existing = conn.execute(
        "SELECT 1 FROM ambient_config WHERE tenant_id = ?",
        (tenant_id,),
    ).fetchone()
    if existing:
        return

    now = utc_now()
    cfg_id = new_id("cfg")
    conn.execute(
        """
        INSERT INTO ambient_config (
            id, tenant_id, global_enabled, cycle_window_start, cycle_window_end,
            cycle_window_tz, global_frequency_min, per_workspace_frequency_min,
            budget_pct_of_router_daily, max_proposals_per_cycle, dark_launch_days,
            utility_threshold_pct, cost_overrun_pct, actor_id, actor_role_at_decision,
            schema_version, source_version, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            cfg_id,
            tenant_id,
            1,
            "06:00",
            "22:00",
            "America/Bogota",
            30,
            60,
            5.0,
            10,
            14,
            20,
            150,
            AMBIENT_ACTOR_ID,
            AMBIENT_ACTOR_ROLE,
            SCHEMA_VERSION,
            "v1",
            now,
            now,
        ),
    )

    detectors = [
        ("failed_routine", "Rutina fallida", "Detecta routine_run con status failed en las ultimas 24h", "high", 0.0, 60),
        ("stuck_hitl", "HITL estancado", "Detecta routine_run/draft pendientes de aprobacion por mas de 4h", "medium", 0.0, 60),
        ("budget_exhaustion", "Budget agotado", "Detecta workspace/tenant con budget diario al >= 90%", "critical", 0.0, 60),
    ]
    for slug, name, description, severity, cost, freq in detectors:
        existing_det = conn.execute(
            "SELECT 1 FROM ambient_detector WHERE tenant_id = ? AND slug = ?",
            (tenant_id, slug),
        ).fetchone()
        if existing_det:
            continue
        det_id = new_id("det")
        conn.execute(
            """
            INSERT INTO ambient_detector (
                id, tenant_id, slug, name, description, input_scope_json,
                output_type, severity_default, cost_estimate_usd, max_frequency_min,
                actor_id, actor_role_at_decision, schema_version, source_version,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                det_id,
                tenant_id,
                slug,
                name,
                description,
                json.dumps(["routine_run", "draft", "usage_record"], ensure_ascii=False),
                "workloom_item",
                severity,
                cost,
                freq,
                AMBIENT_ACTOR_ID,
                AMBIENT_ACTOR_ROLE,
                SCHEMA_VERSION,
                "v1",
                now,
                now,
            ),
        )
