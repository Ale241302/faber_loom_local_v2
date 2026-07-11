"""Skill Factory Foundation primitives (E3-4 Wave 0).

This module implements the cross-vertical primitives required before vertical
skill packs can be compiled and promoted:

* C0-1: informal interaction capture → HITL draft → citable KB fact.
* C0-2: live external lookup with mandatory evidence bundle, fail-closed.
* C0-5: autonomy ceilings via skill track record.
* C0-7: generalized evidence bundle reusable by any entity.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Callable

from .context import Context, enforce_tenant_scoped
from .db import new_id, record_editorial_event, row_to_dict, transaction, utc_now, workspace_seal_id
from .foundation.m10_classifier import run_heuristic
from .kb import approve_draft, insert_draft
from .models import SCHEMA_VERSION
from .seal import compute_workspace_hmac_for_row


TAXONOMY_V2: dict[str, Any] = {
    "primitives": ["P15", "P16", "P17", "P18"],
    "primitive_names": {
        "P15": "verificar_vigencia_normativa",
        "P16": "rastrear_externo",
        "P17": "corregir_en_cascada_temporal",
        "P18": "capturar_interaccion_informal",
    },
    "implemented": {"P15", "P16", "P17", "P18"},
    "archetypes_e1": {"classifier", "validator", "generator", "formatter", "triage", "skill_package"},
    "unit_of_work_dimensions": [
        "tenant_id",
        "workspace_id",
        "client_id",
        "unit_of_work_id",
        "sub_unit_id",
        "data_class",
        "action",
    ],
}


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def _rows_to_dicts(rows: list[Any]) -> list[dict[str, Any]]:
    return [row_to_dict(row) for row in rows]


# ---------------------------------------------------------------------------
# C0-1 — Informal capture
# ---------------------------------------------------------------------------


def classify_interaction(raw_text: str) -> dict[str, Any]:
    """Classify a raw informal interaction using the deterministic M10 heuristic."""

    result = run_heuristic(raw_text, [])
    return {
        "label": result.get("label", "other"),
        "confidence": result.get("confidence", 0.0),
        "scores": result.get("scores", {}),
    }


def capture_informal_interaction(
    ctx: Context,
    conn: Any,
    *,
    raw_text: str,
    source_type: str,
    source_locator: str,
    unit_of_work_id: str | None = None,
) -> dict[str, Any]:
    """Capture an informal interaction as a HITL draft."""

    enforce_tenant_scoped(ctx)
    workspace_id = ctx.require_scoped_workspace()

    classification = classify_interaction(raw_text)
    hard_facts = [
        {"field": "raw_text", "value": raw_text, "source_locator": source_locator},
        {"field": "classification", "value": classification["label"], "source_locator": source_locator},
    ]
    sources = [
        {
            "source_id": source_locator,
            "label": source_type,
            "title": f"Informal capture from {source_type}",
            "locator": source_locator,
            "excerpt": raw_text[:200],
        }
    ]
    if unit_of_work_id:
        hard_facts.append(
            {"field": "unit_of_work_id", "value": unit_of_work_id, "source_locator": source_locator}
        )

    draft = insert_draft(
        ctx,
        conn,
        chat_id=None,
        task="informal_capture",
        subject=f"Capture: {classification['label']}",
        body_md=raw_text,
        hard_facts=hard_facts,
        sources=sources,
        blockers=[],
        warnings=[],
        requires_confirmation=True,
        status="draft",
        source_version="v1",
    )

    return {
        "draft_id": draft["id"],
        "classification": classification,
        "status": "pending_hitl",
    }


def approve_informal_capture(
    ctx: Context,
    conn: Any,
    *,
    draft_id: str,
    confirmed: bool = True,
    reason: str | None = None,
) -> dict[str, Any]:
    """Approve the HITL draft and materialize a citable KB fact."""

    enforce_tenant_scoped(ctx)
    workspace_id = ctx.require_scoped_workspace()

    draft = approve_draft(ctx, conn, draft_id, confirmed=confirmed, reason=reason)
    if draft is None:
        raise ValueError("Draft not found")

    with transaction(conn, ctx=ctx):
        source_id = new_id("kbs")
        now = utc_now()
        conn.execute(
            """
            INSERT INTO kb_source (
                id, workspace_id, tenant_id, user_id, actor_id, type, title,
                content_text, meta_json, routine_version, skill_version, schema_version,
                source_version, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_id,
                workspace_id,
                ctx.tenant_id,
                ctx.user_id,
                ctx.resolved_actor_id(),
                "capture",
                f"Informal capture {draft_id}",
                draft["body_md"],
                _json_dumps({"draft_id": draft_id, "source_type": "informal_capture"}),
                None,
                None,
                SCHEMA_VERSION,
                "v1",
                now,
            ),
        )

        fact_id = _insert_kb_fact(
            ctx,
            conn,
            source_id=source_id,
            entity_key=f"capture:{draft_id}",
            field_name="commitment",
            field_value=draft["body_md"],
            source_locator=f"draft:{draft_id}",
        )

        record_editorial_event(ctx, conn, "draft", draft_id, "exported_to_kb", reason=reason)

    return {
        "draft_id": draft_id,
        "source_id": source_id,
        "kb_fact_id": fact_id,
        "status": "citable",
    }


# ---------------------------------------------------------------------------
# C0-2 — Live external lookup (stub with mandatory evidence bundle)
# ---------------------------------------------------------------------------


ExternalFetcher = Callable[[str, list[str]], list[dict[str, Any]]]


def _assert_public_url(url: str) -> None:
    """Reject non-http(s) schemes and any host that resolves to a non-public IP.

    SSRF guard: a required source URL can come from a skill definition, so it is
    untrusted. We resolve every address the host maps to and refuse loopback,
    private (RFC1918), link-local (incl. cloud metadata 169.254.169.254),
    reserved, or unspecified addresses.
    """

    import ipaddress
    import socket
    from urllib.parse import urlsplit

    parts = urlsplit(url)
    if parts.scheme.lower() not in ("http", "https"):
        raise RuntimeError(f"unsupported_source_scheme: {url}")
    host = parts.hostname
    if not host:
        raise RuntimeError(f"source_missing_host: {url}")

    try:
        infos = socket.getaddrinfo(host, parts.port or (443 if parts.scheme == "https" else 80))
    except OSError as exc:
        raise RuntimeError(f"source_unreachable: {url} ({exc})") from exc

    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_reserved or ip.is_unspecified:
            raise RuntimeError(f"source_blocked_non_public_address: {url} -> {ip}")


def http_evidence_fetcher(
    query: str,
    required_sources: list[str],
    *,
    timeout_s: float = 10.0,
    max_bytes: int = 65536,
) -> list[dict[str, Any]]:
    """Real C0-2 fetcher: GET each required source and build an evidence bundle.

    Every source becomes one evidence item (URL + capture timestamp + content
    hash + snippet). Fail-closed by contract: if ANY required source is
    unreachable, uses a non-http(s) scheme, resolves to a non-public address
    (SSRF guard), or does not return HTTP 200, the whole lookup raises so
    ``external_lookup`` reports the failure instead of fabricating an answer from
    model memory (catalog rule: "jamás rellena de memoria"). Inject a fake
    fetcher in tests; wire this one in production.
    """

    import urllib.error
    import urllib.request

    if not required_sources:
        raise RuntimeError("http_evidence_fetcher requires at least one source URL")

    class _ValidatingRedirectHandler(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> Any:
            # Re-run the SSRF guard on every redirect hop before following it.
            _assert_public_url(newurl)
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    opener = urllib.request.build_opener(_ValidatingRedirectHandler())

    evidence: list[dict[str, Any]] = []
    for url in required_sources:
        _assert_public_url(str(url))
        req = urllib.request.Request(str(url), headers={"User-Agent": "FaberLoom-C0-2/1.0"})
        try:
            # Scheme + resolved address are guarded above and on every redirect.
            with opener.open(req, timeout=timeout_s) as resp:  # noqa: S310
                http_status = getattr(resp, "status", None) or resp.getcode()
                if http_status != 200:
                    raise RuntimeError(f"source_unavailable: {url} returned {http_status}")
                body = resp.read(max_bytes)
        except urllib.error.URLError as exc:
            raise RuntimeError(f"source_unreachable: {url} ({exc})") from exc
        evidence.append(
            {
                "source_type": "web",
                "source_locator": str(url),
                "captured_at": utc_now(),
                "content_text": body.decode("utf-8", errors="replace"),
                "content_hash": hashlib.sha256(body).hexdigest()[:16],
                "query": query,
            }
        )
    return evidence


def external_lookup(
    ctx: Context,
    conn: Any,
    *,
    skill_id: str,
    query: str,
    required_sources: list[str],
    fetcher: ExternalFetcher | None = None,
) -> dict[str, Any]:
    """Perform a live external lookup, storing evidence for every source.

    If no ``fetcher`` is supplied or the fetcher raises, the function fails
    closed and returns ``status='failed'`` with an empty evidence list.
    """

    enforce_tenant_scoped(ctx)

    if fetcher is None:
        return {
            "status": "failed",
            "error": "external_lookup_unavailable",
            "evidence": [],
            "skill_id": skill_id,
        }

    try:
        raw_evidence = fetcher(query, required_sources)
    except Exception as exc:
        return {
            "status": "failed",
            "error": f"external_lookup_fetch_error: {exc}",
            "evidence": [],
            "skill_id": skill_id,
        }

    if not raw_evidence:
        return {
            "status": "failed",
            "error": "external_lookup_no_evidence",
            "evidence": [],
            "skill_id": skill_id,
        }

    normalized = [_normalize_evidence_item(item) for item in raw_evidence]
    for item in normalized:
        if not item.get("source_type") or not item.get("source_locator") or not item.get("captured_at"):
            return {
                "status": "failed",
                "error": "external_lookup_malformed_evidence",
                "evidence": [],
                "skill_id": skill_id,
            }

    return {
        "status": "succeeded",
        "skill_id": skill_id,
        "evidence": normalized,
        "content_hash": _hash_evidence(normalized),
    }


# ---------------------------------------------------------------------------
# C0-5 — Autonomy ceilings via track record
# ---------------------------------------------------------------------------


def update_track_record(
    ctx: Context,
    conn: Any,
    *,
    skill_id: str,
    run_status: str,
    hitl: bool = False,
    schema_compliant: bool = True,
    cost_within_budget: bool = True,
) -> dict[str, Any]:
    """Update the skill track record after a run and recompute autonomy ceiling."""

    enforce_tenant_scoped(ctx)
    workspace_id = ctx.require_scoped_workspace()

    with transaction(conn, ctx=ctx):
        row = conn.execute(
            """
            SELECT * FROM skill_track_record
            WHERE workspace_id = ? AND tenant_id = ? AND skill_id = ?
            """,
            (workspace_id, ctx.tenant_id, skill_id),
        ).fetchone()

        now = utc_now()
        if row is None:
            track_id = new_id("trk")
            conn.execute(
                """
                INSERT INTO skill_track_record (
                    id, workspace_id, tenant_id, skill_id, runs_total, runs_success,
                    runs_hitl, runs_failed, consecutive_failures, acceptance_rate,
                    schema_compliance_rate, cost_within_budget_rate, autonomy_level,
                    autonomy_ceiling, promotion_policy, last_run_at, schema_version,
                    source_version, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, 0, 0, 0, 0, 0, NULL, NULL, NULL, 0, 0, 'standard', ?, ?, 'v2', ?, ?)
                """,
                (track_id, workspace_id, ctx.tenant_id, skill_id, now, SCHEMA_VERSION, now, now),
            )
            row = conn.execute(
                "SELECT * FROM skill_track_record WHERE id = ?",
                (track_id,),
            ).fetchone()

        data = row_to_dict(row)
        total = data["runs_total"] + 1
        success = data["runs_success"] + (1 if run_status == "succeeded" and not hitl else 0)
        hitl_count = data["runs_hitl"] + (1 if hitl else 0)
        failed = data["runs_failed"] + (1 if run_status == "failed" else 0)
        consecutive = 0 if run_status == "succeeded" else data["consecutive_failures"] + 1

        acceptance = round(success / total, 4) if total else None
        schema_compliance = (
            round(
                (
                    (data["schema_compliance_rate"] or 0.0) * data["runs_total"]
                    + (1.0 if schema_compliant else 0.0)
                )
                / total,
                4,
            )
            if total
            else None
        )
        cost_rate = (
            round(
                (
                    (data["cost_within_budget_rate"] or 0.0) * data["runs_total"]
                    + (1.0 if cost_within_budget else 0.0)
                )
                / total,
                4,
            )
            if total
            else None
        )

        ceiling = data["autonomy_ceiling"]
        if (
            total >= 100
            and (acceptance or 0.0) >= 0.90
            and consecutive == 0
            and (cost_rate or 0.0) >= 0.95
        ):
            ceiling = max(ceiling, 1)
        if consecutive >= 3 or (acceptance is not None and acceptance < 0.70):
            ceiling = min(ceiling, 0)

        conn.execute(
            """
            UPDATE skill_track_record
            SET runs_total = ?, runs_success = ?, runs_hitl = ?, runs_failed = ?,
                consecutive_failures = ?, acceptance_rate = ?, schema_compliance_rate = ?,
                cost_within_budget_rate = ?, autonomy_ceiling = ?, last_run_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                total,
                success,
                hitl_count,
                failed,
                consecutive,
                acceptance,
                schema_compliance,
                cost_rate,
                ceiling,
                now,
                now,
                data["id"],
            ),
        )

    return {
        "skill_id": skill_id,
        "runs_total": total,
        "acceptance_rate": acceptance,
        "autonomy_ceiling": ceiling,
        "consecutive_failures": consecutive,
    }


# ---------------------------------------------------------------------------
# C0-7 — Generalized evidence bundle
# ---------------------------------------------------------------------------


def attach_evidence(
    ctx: Context,
    conn: Any,
    *,
    entity_type: str,
    entity_id: str,
    evidence_items: list[dict[str, Any]],
) -> list[str]:
    """Attach external evidence items to an entity."""

    enforce_tenant_scoped(ctx)
    workspace_id = ctx.require_scoped_workspace()

    allowed_entities = {"routine_run", "draft", "kb_fact", "golden_case"}
    if entity_type not in allowed_entities:
        raise ValueError(f"Invalid entity_type: {entity_type}")

    ids: list[str] = []
    now = utc_now()
    with transaction(conn, ctx=ctx):
        for item in evidence_items:
            source_type = str(item.get("source_type", "")).strip()
            source_locator = str(item.get("source_locator", "")).strip()
            captured_at = str(item.get("captured_at", "")).strip()
            if not source_type or not source_locator or not captured_at:
                raise ValueError("Evidence item requires source_type, source_locator and captured_at")

            evidence_id = new_id("evd")
            content_text = item.get("content_text")
            content_hash = item.get("content_hash") or _hash_text(str(content_text) if content_text else "")
            conn.execute(
                """
                INSERT INTO external_evidence (
                    id, workspace_id, tenant_id, entity_type, entity_id, source_type,
                    source_locator, captured_at, content_text, content_hash, schema_version,
                    source_version, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'v2', ?, ?)
                """,
                (
                    evidence_id,
                    workspace_id,
                    ctx.tenant_id,
                    entity_type,
                    entity_id,
                    source_type,
                    source_locator,
                    captured_at,
                    content_text,
                    content_hash,
                    SCHEMA_VERSION,
                    now,
                    now,
                ),
            )
            ids.append(evidence_id)

    return ids


# ---------------------------------------------------------------------------
# P15 — Normative validity check (fail-closed)
# ---------------------------------------------------------------------------


def verificar_vigencia_normativa(
    ctx: Context,
    conn: Any,
    *,
    fact: dict[str, Any],
    fetcher: ExternalFetcher | None = None,
) -> dict[str, Any]:
    """Check whether a KB fact is still valid against its registered source.

    The fact must expose ``valid_from`` and ``valid_until`` boundaries. When a
    ``fetcher`` is supplied, the source is re-consulted and the evidence bundle
    dates are compared to ``utc_now()``; otherwise the result is
    ``no_verificable`` (fail-closed).
    """

    enforce_tenant_scoped(ctx)

    fact_id = str(fact.get("id", "")).strip()
    source_locator = str(fact.get("source_locator", "")).strip()
    valid_from = str(fact.get("valid_from", "")).strip() or None
    valid_until = str(fact.get("valid_until", "")).strip() or None

    if fetcher is None or not fact_id or not source_locator:
        return {
            "status": "no_verificable",
            "fact_id": fact_id or None,
            "checked_at": utc_now(),
            "reason": "missing_fetcher_or_locator",
        }

    if not valid_from or not valid_until:
        return {
            "status": "no_verificable",
            "fact_id": fact_id,
            "checked_at": utc_now(),
            "reason": "missing_validity_boundaries",
        }

    lookup = external_lookup(
        ctx,
        conn,
        skill_id="P15",
        query=fact_id,
        required_sources=[source_locator],
        fetcher=fetcher,
    )

    if lookup["status"] != "succeeded" or not lookup.get("evidence"):
        return {
            "status": "no_verificable",
            "fact_id": fact_id,
            "checked_at": utc_now(),
            "reason": "lookup_failed",
            "error": lookup.get("error"),
        }

    # Prefer explicit validity boundaries returned by the fetcher; fall back to
    # the stored fact boundaries if the evidence does not carry its own.
    effective_from: str | None = None
    effective_until: str | None = None
    for item in lookup["evidence"]:
        if item.get("valid_from"):
            effective_from = str(item["valid_from"])
        if item.get("valid_until"):
            effective_until = str(item["valid_until"])
    if not effective_from or not effective_until:
        effective_from = valid_from
        effective_until = valid_until

    now = utc_now()
    if now < effective_from:
        return {
            "status": "no_verificable",
            "fact_id": fact_id,
            "checked_at": now,
            "valid_from": effective_from,
            "valid_until": effective_until,
            "reason": "not_yet_in_effect",
        }
    if now > effective_until:
        return {
            "status": "vencido",
            "fact_id": fact_id,
            "checked_at": now,
            "valid_from": effective_from,
            "valid_until": effective_until,
        }

    return {
        "status": "vigente",
        "fact_id": fact_id,
        "checked_at": now,
        "valid_from": effective_from,
        "valid_until": effective_until,
        "evidence_hash": lookup.get("content_hash"),
    }


# ---------------------------------------------------------------------------
# P17 — Temporal correction cascade (HITL drafts, append-only log)
# ---------------------------------------------------------------------------


def _find_derived_artifacts(
    conn: Any,
    ctx: Context,
    fact_id: str,
) -> list[dict[str, Any]]:
    """Return artifacts in the current workspace that cite the given fact.

    Today the citation signal is a hard fact that references ``fact_id`` in the
    draft's ``hard_facts_json``. The helper is intentionally narrow so we do not
    invent references that do not exist in the data model.
    """

    workspace_id = ctx.require_scoped_workspace()
    like_pattern = f'%"{fact_id}"%'
    rows = conn.execute(
        """
        SELECT id, task, subject, body_md, hard_facts_json
        FROM draft
        WHERE workspace_id = ? AND tenant_id = ?
          AND (hard_facts_json LIKE ? OR body_md LIKE ?)
        """,
        (workspace_id, ctx.require_tenant(), like_pattern, like_pattern),
    ).fetchall()
    return _rows_to_dicts(rows)


def corregir_en_cascada_temporal(
    ctx: Context,
    conn: Any,
    *,
    fact_id: str,
    new_state: str,
    reason: str | None = None,
) -> dict[str, Any]:
    """Mark a fact as expired/corrected and open HITL drafts for derived artifacts.

    The function never auto-applies corrections. Every affected artifact gets a
    new ``draft`` with ``requires_confirmation=True``, and an append-only row in
    ``correction_log`` links the original fact to the proposed correction.
    """

    enforce_tenant_scoped(ctx)
    workspace_id = ctx.require_scoped_workspace()

    if new_state not in {"vencido", "corregido"}:
        raise ValueError(f"Invalid correction state: {new_state}")

    created_drafts: list[str] = []
    log_entries: list[str] = []
    now = utc_now()

    with transaction(conn, ctx=ctx):
        fact = conn.execute(
            """
            SELECT id, field_name, field_value, valid_from, valid_until, source_locator
            FROM kb_fact
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (fact_id, workspace_id, ctx.require_tenant()),
        ).fetchone()
        if fact is None:
            raise ValueError(f"Fact not found: {fact_id}")

        derived = _find_derived_artifacts(conn, ctx, fact_id)

        for artifact in derived:
            artifact_id = artifact["id"]
            correction_draft = insert_draft(
                ctx,
                conn,
                chat_id=None,
                task="correction_cascade",
                subject=f"Corrección en cascada: fact {fact_id} → {new_state}",
                body_md=(
                    f"El fact **{fact_id}** fue marcado como **{new_state}** "
                    f"y afecta al artefacto derivado `{artifact_id}`. "
                    "Revisa antes de aplicar la corrección."
                ),
                hard_facts=[
                    {"field": "origin_fact_id", "value": fact_id, "source_locator": f"fact:{fact_id}"},
                    {"field": "proposed_state", "value": new_state, "source_locator": f"fact:{fact_id}"},
                    {"field": "affected_artifact_id", "value": artifact_id, "source_locator": f"draft:{artifact_id}"},
                    {"field": "reason", "value": reason or "", "source_locator": f"fact:{fact_id}"},
                ],
                sources=[],
                blockers=[],
                warnings=[],
                requires_confirmation=True,
                status="draft",
                source_version="v2",
            )
            created_drafts.append(correction_draft["id"])

            log_id = new_id("corr")
            conn.execute(
                """
                INSERT INTO correction_log (
                    id, workspace_id, tenant_id, origin_fact_id,
                    affected_entity_type, affected_entity_id, proposed_state,
                    reason, draft_id, actor_id, schema_version, source_version, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    log_id,
                    workspace_id,
                    ctx.tenant_id,
                    fact_id,
                    "draft",
                    artifact_id,
                    new_state,
                    reason,
                    correction_draft["id"],
                    ctx.resolved_actor_id(),
                    SCHEMA_VERSION,
                    "v2",
                    now,
                ),
            )
            log_entries.append(log_id)

    return {
        "fact_id": fact_id,
        "new_state": new_state,
        "affected_artifacts": len(derived),
        "created_draft_ids": created_drafts,
        "correction_log_ids": log_entries,
    }


# ---------------------------------------------------------------------------
# Pack materialization and promotion
# ---------------------------------------------------------------------------


def infer_pack_id(skill_id: str) -> str | None:
    """Infer the pack id from a skill id prefix."""

    mapping = {
        "SKILL_FE_": "wtp_fiscalidad_electronica",
        "SKILL_CO_": "wtp_cobranza",
        "SKILL_CX_": "wtp_comex",
        "SKILL_PL_": "wtp_planilla",
        "SKILL_TR_": "wtp_tributario",
        "SKILL_WA_": "wtp_whatsapp_formal",
        "SKILL_BO_": "wtp_bodega_importacion",
        "SKILL_CM_": "wtp_comercial",
        "SKILL_SV_": "wtp_servicio",
        "SKILL_FI_": "wtp_finanzas_cierre",
        "SKILL_LG_": "wtp_legal",
        "SKILL_GE_": "wtp_gerencia",
        "SKILL_OP_": "wtp_operaciones",
        "SKILL_MK_": "wtp_marketing",
        "SKILL_HR_": "wtp_rrhh",
    }
    for prefix, pack_id in mapping.items():
        if skill_id.upper().startswith(prefix):
            return pack_id
    return None


def ensure_skill_factory_rows(
    ctx: Context,
    conn: Any,
    *,
    skill_id: str,
    manifest_json: dict[str, Any],
    golden_samples: list[dict[str, Any]],
) -> dict[str, Any]:
    """Create or update skill_manifest, skill_version, track_record and pack_status."""

    enforce_tenant_scoped(ctx)
    workspace_id = ctx.require_scoped_workspace()
    now = utc_now()
    manifest_id = new_id("mft")
    version = str(manifest_json.get("version", "0.1.0")).strip() or "0.1.0"

    with transaction(conn, ctx=ctx):
        conn.execute(
            """
            INSERT INTO skill_manifest (
                id, workspace_id, tenant_id, skill_id, version, manifest_json,
                status, schema_version, source_version, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, 'shadow', ?, 'v2', ?, ?)
            ON CONFLICT(workspace_id, tenant_id, skill_id, version) DO UPDATE SET
                manifest_json = excluded.manifest_json,
                status = CASE WHEN skill_manifest.status = 'active' THEN 'active' ELSE 'shadow' END,
                updated_at = excluded.updated_at
            """,
            (
                manifest_id,
                workspace_id,
                ctx.tenant_id,
                skill_id,
                version,
                _json_dumps(manifest_json),
                SCHEMA_VERSION,
                now,
                now,
            ),
        )

        row = conn.execute(
            """
            SELECT id FROM skill_manifest
            WHERE workspace_id = ? AND tenant_id = ? AND skill_id = ? AND version = ?
            """,
            (workspace_id, ctx.tenant_id, skill_id, version),
        ).fetchone()
        resolved_manifest_id = row["id"] if row else manifest_id

        conn.execute(
            """
            INSERT INTO skill_version (
                id, workspace_id, tenant_id, skill_id, version, manifest_id,
                schema_version, source_version, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'v2', ?)
            ON CONFLICT(workspace_id, tenant_id, skill_id, version) DO UPDATE SET
                manifest_id = excluded.manifest_id
            """,
            (
                new_id("svr"),
                workspace_id,
                ctx.tenant_id,
                skill_id,
                version,
                resolved_manifest_id,
                SCHEMA_VERSION,
                now,
            ),
        )

        conn.execute(
            """
            INSERT INTO skill_track_record (
                id, workspace_id, tenant_id, skill_id, runs_total, runs_success,
                runs_hitl, runs_failed, consecutive_failures, autonomy_level,
                autonomy_ceiling, promotion_policy, schema_version, source_version,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, 0, 0, 0, 0, 0, 0, 0, 'standard', ?, 'v2', ?, ?)
            ON CONFLICT(workspace_id, tenant_id, skill_id) DO NOTHING
            """,
            (new_id("trk"), workspace_id, ctx.tenant_id, skill_id, SCHEMA_VERSION, now, now),
        )

        pack_id = infer_pack_id(skill_id)
        required = len(golden_samples)
        if pack_id:
            conn.execute(
                """
                INSERT INTO pack_status (
                    id, workspace_id, tenant_id, pack_id, status, required_golden_cases,
                    approved_golden_cases, autonomy_ceiling, schema_version, source_version,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, 'shadow', ?, 0, 0, ?, 'v2', ?, ?)
                ON CONFLICT(workspace_id, tenant_id, pack_id) DO UPDATE SET
                    required_golden_cases = MAX(pack_status.required_golden_cases, excluded.required_golden_cases),
                    updated_at = excluded.updated_at
                """,
                (
                    new_id("pst"),
                    workspace_id,
                    ctx.tenant_id,
                    pack_id,
                    required,
                    SCHEMA_VERSION,
                    now,
                    now,
                ),
            )

        for sample in golden_samples:
            sample_id = str(sample.get("id", "")).strip() or "sample_1"
            case_id = f"{skill_id}:{sample_id}"
            conn.execute(
                """
                INSERT INTO golden_case (
                    id, workspace_id, tenant_id, skill_id, case_id, input_json,
                    expected_output_json, evidence_required, approved, schema_version,
                    source_version, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, 0, ?, 'v2', ?, ?)
                ON CONFLICT(workspace_id, tenant_id, skill_id, case_id) DO NOTHING
                """,
                (
                    new_id("gcs"),
                    workspace_id,
                    ctx.tenant_id,
                    skill_id,
                    case_id,
                    _json_dumps(sample.get("input", {})),
                    _json_dumps(sample.get("expected_output", {})),
                    SCHEMA_VERSION,
                    now,
                    now,
                ),
            )

    return {
        "skill_id": skill_id,
        "version": version,
        "manifest_id": resolved_manifest_id,
        "pack_id": pack_id,
        "required_golden_cases": required,
    }


PROMOTION_THRESHOLDS = {
    "runs_total": 100,
    "acceptance_rate": 0.90,
}


def promote_pack(
    ctx: Context,
    conn: Any,
    *,
    pack_id: str,
    approved_by: str,
) -> dict[str, Any]:
    """Promote a pack from SHADOW to ACTIVE."""

    enforce_tenant_scoped(ctx)
    workspace_id = ctx.require_scoped_workspace()

    with transaction(conn, ctx=ctx):
        pack = conn.execute(
            """
            SELECT * FROM pack_status
            WHERE workspace_id = ? AND tenant_id = ? AND pack_id = ?
            """,
            (workspace_id, ctx.tenant_id, pack_id),
        ).fetchone()
        if pack is None:
            raise ValueError(f"Pack not found: {pack_id}")

        all_cases = _rows_to_dicts(
            conn.execute(
                "SELECT skill_id FROM golden_case WHERE workspace_id = ? AND tenant_id = ?",
                (workspace_id, ctx.tenant_id),
            ).fetchall()
        )
        pack_skill_ids = {c["skill_id"] for c in all_cases if infer_pack_id(c["skill_id"]) == pack_id}
        if not pack_skill_ids:
            raise ValueError(f"Pack {pack_id} has no associated golden cases")

        placeholders = ",".join("?" for _ in pack_skill_ids)
        params = (workspace_id, ctx.tenant_id, *pack_skill_ids)

        pending = conn.execute(
            f"""
            SELECT COUNT(*) AS cnt FROM golden_case
            WHERE workspace_id = ? AND tenant_id = ? AND skill_id IN ({placeholders}) AND approved = 0
            """,
            params,
        ).fetchone()["cnt"]
        if pending:
            raise ValueError(f"Pack {pack_id} has {pending} unapproved golden cases")

        unverified = conn.execute(
            f"""
            SELECT COUNT(*) AS cnt FROM golden_case
            WHERE workspace_id = ? AND tenant_id = ? AND skill_id IN ({placeholders})
              AND approved = 1 AND (verified_by IS NULL OR verified_by = '')
            """,
            params,
        ).fetchone()["cnt"]
        if unverified:
            raise ValueError(f"Pack {pack_id} has {unverified} unverified golden cases")

        tracks = _rows_to_dicts(
            conn.execute(
                f"""
                SELECT * FROM skill_track_record
                WHERE workspace_id = ? AND tenant_id = ? AND skill_id IN ({placeholders})
                """,
                params,
            ).fetchall()
        )
        if len(tracks) != len(pack_skill_ids):
            raise ValueError(f"Pack {pack_id} is missing track records")
        for track in tracks:
            if track["runs_total"] < PROMOTION_THRESHOLDS["runs_total"] or (
                track["acceptance_rate"] or 0.0
            ) < PROMOTION_THRESHOLDS["acceptance_rate"]:
                raise ValueError(f"Pack {pack_id} does not meet track-record thresholds")

        now = utc_now()
        conn.execute(
            """
            UPDATE pack_status
            SET status = 'active', promoted_at = ?, promoted_by = ?, updated_at = ?
            WHERE workspace_id = ? AND tenant_id = ? AND pack_id = ?
            """,
            (now, approved_by, now, workspace_id, ctx.tenant_id, pack_id),
        )
        conn.execute(
            f"""
            UPDATE skill_manifest
            SET status = 'active', updated_at = ?
            WHERE workspace_id = ? AND tenant_id = ? AND skill_id IN ({placeholders})
            """,
            (now, workspace_id, ctx.tenant_id, *pack_skill_ids),
        )

        return {"pack_id": pack_id, "status": "active", "promoted_at": now, "promoted_by": approved_by}


def compute_pack_readiness(
    ctx: Context,
    conn: Any,
    *,
    pack_id: str,
) -> dict[str, Any]:
    """Return a readiness snapshot for ``pack_id`` in the scoped workspace.

    The result is read-only and safe to expose in the promotion readiness UI.
    It never invents data: missing golden cases or track records are reported
    as blockers.

    Promotion gates are evaluated over the skills already imported into the
    workspace, matching the behaviour of ``promote_pack`` (which derives the
    active skill set from existing golden cases / manifests).
    """

    enforce_tenant_scoped(ctx)
    workspace_id = ctx.require_scoped_workspace()

    from .db import get_global_skills

    global_skills = get_global_skills(
        conn, tenant_id="global", active_only=True, pack_id=pack_id
    )
    global_skill_ids = [row["skill_id"] for row in global_skills]
    skill_count = len(global_skill_ids)

    # Imported manifests in the current workspace.
    imported: dict[str, dict[str, Any]] = {}
    if global_skill_ids:
        placeholders = ",".join("?" for _ in global_skill_ids)
        imported_rows = conn.execute(
            f"""
            SELECT * FROM skill_manifest
            WHERE workspace_id = ? AND tenant_id = ? AND skill_id IN ({placeholders})
            """,
            (workspace_id, ctx.tenant_id, *global_skill_ids),
        ).fetchall()
        imported = {row["skill_id"]: row_to_dict(row) for row in imported_rows}

    imported_count = len(imported)

    # Effective status per skill: imported manifest wins; otherwise catalog status.
    statuses: dict[str, str] = {}
    for row in global_skills:
        sid = row["skill_id"]
        if sid in imported:
            statuses[sid] = imported[sid].get("status") or "shadow"
        else:
            manifest = json.loads(row["manifest_json"] or "{}")
            statuses[sid] = (
                manifest.get("metadata", {}).get("fbl", {}).get("status") or "shadow"
            )

    # Skills that participate in the promotion gate are the imported ones.
    # If nothing is imported yet, we still report global counts but block promotion.
    gate_skill_ids = list(imported.keys()) if imported else global_skill_ids
    gate_count = len(gate_skill_ids)

    # Golden cases for the gating skills.
    total_cases = approved_cases = verified_cases = 0
    if gate_skill_ids:
        placeholders = ",".join("?" for _ in gate_skill_ids)
        total_cases = conn.execute(
            f"""
            SELECT COUNT(*) AS cnt FROM golden_case
            WHERE workspace_id = ? AND tenant_id = ? AND skill_id IN ({placeholders})
            """,
            (workspace_id, ctx.tenant_id, *gate_skill_ids),
        ).fetchone()["cnt"]
        approved_cases = conn.execute(
            f"""
            SELECT COUNT(*) AS cnt FROM golden_case
            WHERE workspace_id = ? AND tenant_id = ? AND skill_id IN ({placeholders}) AND approved = 1
            """,
            (workspace_id, ctx.tenant_id, *gate_skill_ids),
        ).fetchone()["cnt"]
        verified_cases = conn.execute(
            f"""
            SELECT COUNT(*) AS cnt FROM golden_case
            WHERE workspace_id = ? AND tenant_id = ? AND skill_id IN ({placeholders})
              AND approved = 1 AND verified_by IS NOT NULL AND verified_by != ''
            """,
            (workspace_id, ctx.tenant_id, *gate_skill_ids),
        ).fetchone()["cnt"]

    # Track records for the gating skills.
    tracks: list[dict[str, Any]] = []
    if gate_skill_ids:
        placeholders = ",".join("?" for _ in gate_skill_ids)
        track_rows = conn.execute(
            f"""
            SELECT * FROM skill_track_record
            WHERE workspace_id = ? AND tenant_id = ? AND skill_id IN ({placeholders})
            """,
            (workspace_id, ctx.tenant_id, *gate_skill_ids),
        ).fetchall()
        tracks = [row_to_dict(row) for row in track_rows]
    meeting_threshold_count = sum(
        1
        for t in tracks
        if t.get("runs_total", 0) >= PROMOTION_THRESHOLDS["runs_total"]
        and (t.get("acceptance_rate") or 0.0) >= PROMOTION_THRESHOLDS["acceptance_rate"]
    )

    pack = conn.execute(
        """
        SELECT * FROM pack_status
        WHERE workspace_id = ? AND tenant_id = ? AND pack_id = ?
        """,
        (workspace_id, ctx.tenant_id, pack_id),
    ).fetchone()
    pack_row = row_to_dict(pack) if pack else None

    blockers: list[str] = []
    if pack_row is None:
        blockers.append("Pack no importado en este workspace")
    if imported_count == 0:
        blockers.append("Ningún skill del pack ha sido importado")
    pending_cases = total_cases - approved_cases
    if pending_cases > 0:
        blockers.append(f"Hay {pending_cases} golden cases sin aprobar")
    unverified_cases = approved_cases - verified_cases
    if unverified_cases > 0:
        blockers.append(f"Hay {unverified_cases} golden cases aprobados sin verificar")
    if len(tracks) < gate_count:
        blockers.append(f"Faltan {gate_count - len(tracks)} track records")
    if meeting_threshold_count < gate_count:
        blockers.append(
            f"Solo {meeting_threshold_count}/{gate_count} skills importados cumplen el umbral "
            f"de track record (>= {PROMOTION_THRESHOLDS['runs_total']} runs, "
            f">= {PROMOTION_THRESHOLDS['acceptance_rate']*100:.0f}% acceptance)"
        )

    can_promote = pack_row is not None and imported_count > 0 and not blockers

    return {
        "pack_id": pack_id,
        "status": (pack_row.get("status") if pack_row else "not_imported"),
        "skill_count": skill_count,
        "imported_count": imported_count,
        "skill_statuses": statuses,
        "required_golden_cases": (
            pack_row.get("required_golden_cases", 0) if pack_row else 0
        ),
        "golden_cases": {
            "total": total_cases,
            "approved": approved_cases,
            "verified": verified_cases,
        },
        "track_records": {
            "total": len(tracks),
            "meeting_threshold": meeting_threshold_count,
        },
        "thresholds": PROMOTION_THRESHOLDS,
        "can_promote": can_promote,
        "blockers": blockers,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _insert_kb_fact(
    ctx: Context,
    conn: Any,
    *,
    source_id: str,
    entity_key: str,
    field_name: str,
    field_value: str,
    source_locator: str,
) -> str:
    """Insert a single KB fact for an approved capture."""

    workspace_id = ctx.require_scoped_workspace()
    fact_id = new_id("fact")
    seal_id = workspace_seal_id(ctx, conn)
    hmac = compute_workspace_hmac_for_row(
        seal_id,
        {
            "id": fact_id,
            "workspace_id": workspace_id,
            "source_id": source_id,
            "entity_key": entity_key,
            "field_name": field_name,
            "field_value": field_value,
            "source_version": "v1",
        },
        "kb_fact",
    )
    now = utc_now()
    conn.execute(
        """
        INSERT INTO kb_fact (
            id, workspace_id, source_id, entity_key, field_name, field_value,
            source_locator, source_version, schema_version, workspace_hmac,
            tenant_id, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 'v1', ?, ?, ?, ?)
        """,
        (
            fact_id,
            workspace_id,
            source_id,
            entity_key,
            field_name,
            field_value,
            source_locator,
            SCHEMA_VERSION,
            hmac,
            ctx.tenant_id,
            now,
        ),
    )
    return fact_id


def _normalize_evidence_item(item: Any) -> dict[str, Any]:
    if not isinstance(item, dict):
        return {}
    return {
        "source_type": str(item.get("source_type", "")).strip(),
        "source_locator": str(item.get("source_locator", "")).strip(),
        "captured_at": str(item.get("captured_at", "")).strip(),
        "content_text": item.get("content_text"),
        "content_hash": item.get("content_hash"),
    }


def _hash_evidence(items: list[dict[str, Any]]) -> str:
    payload = json.dumps(items, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


__all__ = [
    "TAXONOMY_V2",
    "classify_interaction",
    "capture_informal_interaction",
    "approve_informal_capture",
    "external_lookup",
    "http_evidence_fetcher",
    "verificar_vigencia_normativa",
    "corregir_en_cascada_temporal",
    "update_track_record",
    "attach_evidence",
    "ensure_skill_factory_rows",
    "promote_pack",
    "infer_pack_id",
    "compute_pack_readiness",
    "PROMOTION_THRESHOLDS",
]
