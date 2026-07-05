"""M10 — L1 Classifier portado de Django (apps/classifier) a FastAPI/SQLite.

Adaptaciones local-first:

- El pipeline Tier0 (reglas deterministas) + L1 (LLM vía litellm) se colapsa en
  un clasificador heurístico determinista: reglas keyword/regex con pesos por
  label, combinadas con "noisy-or" para producir un confidence 0..1. Sin
  llamadas externas. Se deja un *seam* opcional (``llm_classify_hook``) para
  enchufar un LLM más adelante sin tocar los endpoints.
- ``ClassifierSkill`` (prompt/modelo/threshold) se reduce a una config por
  tenant (``fnd_classifier_config``): rules_json + threshold + version.
- Celery/async → síncrono dentro de la transacción del request.
- Taxonomía operativa: rfq, order, complaint, invoice, spam, other
  (el código Django clasifica a ``task_type`` abierto; el plan M10 usa RFQ como
  caso canónico — aquí se fija la taxonomía de negocio del plan).
"""

from __future__ import annotations

import json
import re
from typing import Any, Callable

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from .core import (
    SessionContext,
    get_conn,
    new_id,
    register_schema,
    require_permission,
    rows_to_dicts,
    to_dict,
    utcnow,
)

router = APIRouter(prefix="/classifier", tags=["foundation-m10-classifier"])

register_schema(
    """
CREATE TABLE IF NOT EXISTS fnd_inbound_items (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    channel TEXT NOT NULL DEFAULT 'email',
    sender TEXT NOT NULL DEFAULT '',
    subject TEXT NOT NULL DEFAULT '',
    body TEXT NOT NULL DEFAULT '',
    received_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new','classified','dismissed')),
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_fnd_inbound_tenant_status
    ON fnd_inbound_items(tenant_id, status, received_at);

CREATE TABLE IF NOT EXISTS fnd_classifications (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    item_id TEXT NOT NULL REFERENCES fnd_inbound_items(id),
    label TEXT NOT NULL,
    confidence REAL NOT NULL DEFAULT 0,
    taxonomy_json TEXT NOT NULL DEFAULT '{}',
    features_json TEXT NOT NULL DEFAULT '{}',
    classifier_version TEXT NOT NULL DEFAULT '1',
    decided_by TEXT NOT NULL DEFAULT 'rule' CHECK (decided_by IN ('rule','llm','human')),
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_fnd_classifications_item
    ON fnd_classifications(tenant_id, item_id, created_at);

CREATE TABLE IF NOT EXISTS fnd_classifier_config (
    tenant_id TEXT PRIMARY KEY,
    rules_json TEXT NOT NULL DEFAULT '[]',
    threshold REAL NOT NULL DEFAULT 0.7,
    version TEXT NOT NULL DEFAULT '1',
    updated_at TEXT NOT NULL
);
"""
)

# ---------------------------------------------------------------------------
# Taxonomía y reglas por defecto (equivalente local de Tier0Rule + skill)
# ---------------------------------------------------------------------------

TAXONOMY = ["rfq", "order", "complaint", "invoice", "spam", "other"]
ACTIONABLE_LABELS = {"rfq", "order"}
DEFAULT_THRESHOLD = 0.7
CLASSIFIER_VERSION = "1"

DEFAULT_RULES: list[dict[str, Any]] = [
    {
        "label": "rfq",
        "weight": 0.7,
        "keywords": [
            "cotizacion", "cotización", "cotizar", "coticen", "presupuesto",
            "quote", "quotation", "rfq", "precio de", "cuanto cuesta",
            "cuánto cuesta", "solicitud de precio",
        ],
        "patterns": [r"\brfq[-#]?\d*\b", r"request\s+for\s+quot"],
    },
    {
        "label": "order",
        "weight": 0.7,
        "keywords": [
            "pedido", "orden de compra", "purchase order", "confirmamos la compra",
            "queremos comprar", "adjunto orden", "nota de pedido",
        ],
        "patterns": [r"\bpo[-#]\s?\d+", r"\borden\s+n[oº°]?\.?\s?\d+"],
    },
    {
        "label": "complaint",
        "weight": 0.7,
        "keywords": [
            "queja", "reclamo", "reclamacion", "reclamación", "complaint",
            "inconforme", "defectuoso", "dañado", "garantia", "garantía",
            "no funciona", "insatisfecho",
        ],
        "patterns": [],
    },
    {
        "label": "invoice",
        "weight": 0.7,
        "keywords": [
            "factura", "invoice", "cfdi", "comprobante fiscal", "pago pendiente",
            "estado de cuenta", "payment due", "nota de credito", "nota de crédito",
        ],
        "patterns": [r"\bfact(?:ura)?[-#]?\s?\d+"],
    },
    {
        "label": "spam",
        "weight": 0.8,
        "keywords": [
            "unsubscribe", "loteria", "lotería", "premio garantizado", "haz clic aqui",
            "haz clic aquí", "oferta exclusiva!!!", "gana dinero", "criptomonedas gratis",
            "viagra",
        ],
        "patterns": [r"(?i)100%\s*(gratis|free)"],
    },
]

# Seam opcional para LLM: si alguien lo asigna, recibe (item_dict, config_dict)
# y devuelve {"label": str, "confidence": float, "features": dict} o None para
# caer a la heurística. Por defecto NO hay llamadas externas.
llm_classify_hook: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any] | None] | None = None


def get_config(conn, tenant_id: str) -> dict[str, Any]:
    row = conn.execute(
        "SELECT * FROM fnd_classifier_config WHERE tenant_id = ?", (tenant_id,)
    ).fetchone()
    if row is None:
        return {
            "tenant_id": tenant_id,
            "rules": DEFAULT_RULES,
            "threshold": DEFAULT_THRESHOLD,
            "version": CLASSIFIER_VERSION,
            "updated_at": None,
        }
    return to_dict(row)  # type: ignore[return-value]


def run_heuristic(text: str, rules: list[dict[str, Any]]) -> dict[str, Any]:
    """Clasificador determinista: keywords/regex con pesos → noisy-or por label."""
    haystack = (text or "").lower()
    scores: dict[str, float] = {}
    features: dict[str, list[str]] = {}
    for rule in rules:
        label = str(rule.get("label", "other"))
        weight = float(rule.get("weight", 0.6))
        weight = min(max(weight, 0.0), 1.0)
        hits: list[str] = []
        for kw in rule.get("keywords", []) or []:
            if str(kw).lower() in haystack:
                hits.append(f"kw:{kw}")
        for pat in rule.get("patterns", []) or []:
            try:
                if re.search(pat, haystack, re.IGNORECASE):
                    hits.append(f"re:{pat}")
            except re.error:
                continue
        if not hits:
            continue
        survive = 1.0
        for _ in hits:
            survive *= 1.0 - weight
        score = 1.0 - survive
        if score > scores.get(label, 0.0):
            scores[label] = round(score, 4)
            features[label] = hits
        else:
            features.setdefault(label, []).extend(hits)
    if not scores:
        return {"label": "other", "confidence": 0.1, "scores": {"other": 0.1}, "features": {}}
    best = max(scores.items(), key=lambda kv: kv[1])
    return {"label": best[0], "confidence": best[1], "scores": scores, "features": features}


def _latest_classification(conn, tenant_id: str, item_id: str):
    return conn.execute(
        """SELECT * FROM fnd_classifications
           WHERE tenant_id = ? AND item_id = ? ORDER BY created_at DESC, id DESC LIMIT 1""",
        (tenant_id, item_id),
    ).fetchone()


def _get_item(conn, tenant_id: str, item_id: str):
    row = conn.execute(
        "SELECT * FROM fnd_inbound_items WHERE tenant_id = ? AND id = ?",
        (tenant_id, item_id),
    ).fetchone()
    if row is None:
        raise HTTPException(404, "Inbound item not found")
    return row


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class InboundIn(BaseModel):
    channel: str = Field(default="email", max_length=32)
    sender: str = Field(default="", max_length=255)
    subject: str = Field(default="", max_length=500)
    body: str = Field(default="", max_length=20000)
    received_at: str | None = None


class OverrideIn(BaseModel):
    label: str
    note: str = ""


class ConfigIn(BaseModel):
    rules: list[dict[str, Any]] | None = None
    threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    version: str | None = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/inbound", status_code=201)
def create_inbound(
    payload: InboundIn,
    ctx: SessionContext = Depends(require_permission("classifier.run")),
) -> dict[str, Any]:
    item_id = new_id("inb")
    now = utcnow()
    ctx.conn.execute(
        """INSERT INTO fnd_inbound_items
           (id, tenant_id, channel, sender, subject, body, received_at, status, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'new', ?)""",
        (item_id, ctx.tenant_id, payload.channel, payload.sender, payload.subject,
         payload.body, payload.received_at or now, now),
    )
    ctx.audit("classifier.inbound.created", resource_type="inbound_item", resource_id=item_id,
              payload={"channel": payload.channel, "sender": payload.sender})
    ctx.emit("classifier", "inbound.received", {"item_id": item_id, "channel": payload.channel})
    row = _get_item(ctx.conn, ctx.tenant_id, item_id)
    return to_dict(row)  # type: ignore[return-value]


@router.post("/inbound/{item_id}/classify")
def classify_inbound(
    item_id: str,
    ctx: SessionContext = Depends(require_permission("classifier.run")),
) -> dict[str, Any]:
    item = _get_item(ctx.conn, ctx.tenant_id, item_id)
    if item["status"] == "dismissed":
        raise HTTPException(409, "Item is dismissed")
    config = get_config(ctx.conn, ctx.tenant_id)
    rules = config.get("rules") or DEFAULT_RULES
    threshold = float(config.get("threshold", DEFAULT_THRESHOLD))

    decided_by = "rule"
    result: dict[str, Any] | None = None
    if llm_classify_hook is not None:  # seam opcional (no hay LLM por defecto)
        try:
            result = llm_classify_hook(to_dict(item) or {}, config)
            if result:
                decided_by = "llm"
        except Exception:
            result = None
    if not result:
        decided_by = "rule"
        text = " ".join([item["sender"] or "", item["subject"] or "", item["body"] or ""])
        result = run_heuristic(text, rules)

    label = str(result.get("label", "other"))
    confidence = round(float(result.get("confidence", 0.0)), 4)
    cls_id = new_id("cls")
    now = utcnow()
    ctx.conn.execute(
        """INSERT INTO fnd_classifications
           (id, tenant_id, item_id, label, confidence, taxonomy_json, features_json,
            classifier_version, decided_by, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (cls_id, ctx.tenant_id, item_id, label, confidence,
         json.dumps(result.get("scores", {}), ensure_ascii=False),
         json.dumps(result.get("features", {}), ensure_ascii=False),
         str(config.get("version", CLASSIFIER_VERSION)), decided_by, now),
    )
    ctx.conn.execute(
        "UPDATE fnd_inbound_items SET status = 'classified' WHERE tenant_id = ? AND id = ?",
        (ctx.tenant_id, item_id),
    )
    meets_threshold = confidence >= threshold
    ctx.audit("classifier.item.classified", resource_type="inbound_item", resource_id=item_id,
              payload={"classification_id": cls_id, "label": label,
                       "confidence": confidence, "decided_by": decided_by,
                       "meets_threshold": meets_threshold})
    ctx.emit("classifier", "classified", {
        "item_id": item_id, "classification_id": cls_id, "label": label,
        "confidence": confidence, "decided_by": decided_by,
        "meets_threshold": meets_threshold,
    })
    # Label accionable → evento para que M13 pueda crear un draft.
    if label in ACTIONABLE_LABELS and meets_threshold:
        ctx.emit("classifier", "actionable", {
            "item_id": item_id, "classification_id": cls_id, "label": label,
            "confidence": confidence, "channel": item["channel"],
            "sender": item["sender"], "subject": item["subject"],
        })
    classification = to_dict(_latest_classification(ctx.conn, ctx.tenant_id, item_id))
    return {
        "item_id": item_id,
        "classification": classification,
        "meets_threshold": meets_threshold,
        "threshold": threshold,
    }


@router.post("/inbound/{item_id}/override")
def override_classification(
    item_id: str,
    payload: OverrideIn,
    # El plan M10 trata la re-clasificación como corrección de Operador
    # (reason="operator_correction"), por eso classifier.run y no manage.
    ctx: SessionContext = Depends(require_permission("classifier.run")),
) -> dict[str, Any]:
    if payload.label not in TAXONOMY:
        raise HTTPException(422, f"Label inválido; taxonomía: {', '.join(TAXONOMY)}")
    item = _get_item(ctx.conn, ctx.tenant_id, item_id)
    config = get_config(ctx.conn, ctx.tenant_id)
    cls_id = new_id("cls")
    ctx.conn.execute(
        """INSERT INTO fnd_classifications
           (id, tenant_id, item_id, label, confidence, taxonomy_json, features_json,
            classifier_version, decided_by, created_at)
           VALUES (?, ?, ?, ?, 1.0, ?, ?, ?, 'human', ?)""",
        (cls_id, ctx.tenant_id, item_id, payload.label,
         json.dumps({payload.label: 1.0}),
         json.dumps({"override_note": payload.note, "override_by": ctx.email}, ensure_ascii=False),
         str(config.get("version", CLASSIFIER_VERSION)), utcnow()),
    )
    ctx.conn.execute(
        "UPDATE fnd_inbound_items SET status = 'classified' WHERE tenant_id = ? AND id = ?",
        (ctx.tenant_id, item_id),
    )
    ctx.audit("classifier.item.overridden", resource_type="inbound_item", resource_id=item_id,
              payload={"classification_id": cls_id, "label": payload.label,
                       "reason": "operator_correction", "note": payload.note})
    ctx.emit("classifier", "overridden", {
        "item_id": item_id, "classification_id": cls_id, "label": payload.label,
        "decided_by": "human",
    })
    if payload.label in ACTIONABLE_LABELS:
        ctx.emit("classifier", "actionable", {
            "item_id": item_id, "classification_id": cls_id, "label": payload.label,
            "confidence": 1.0, "channel": item["channel"],
            "sender": item["sender"], "subject": item["subject"],
        })
    return {"item_id": item_id,
            "classification": to_dict(_latest_classification(ctx.conn, ctx.tenant_id, item_id))}


@router.post("/inbound/{item_id}/dismiss")
def dismiss_inbound(
    item_id: str,
    ctx: SessionContext = Depends(require_permission("classifier.run")),
) -> dict[str, Any]:
    _get_item(ctx.conn, ctx.tenant_id, item_id)
    ctx.conn.execute(
        "UPDATE fnd_inbound_items SET status = 'dismissed' WHERE tenant_id = ? AND id = ?",
        (ctx.tenant_id, item_id),
    )
    ctx.audit("classifier.item.dismissed", resource_type="inbound_item", resource_id=item_id)
    ctx.emit("classifier", "dismissed", {"item_id": item_id})
    return {"item_id": item_id, "status": "dismissed"}


@router.get("/inbound")
def list_inbound(
    status_filter: str | None = Query(default=None, alias="status"),
    label: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    ctx: SessionContext = Depends(require_permission("classifier.read")),
) -> dict[str, Any]:
    query = "SELECT * FROM fnd_inbound_items WHERE tenant_id = ?"
    params: list[Any] = [ctx.tenant_id]
    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)
    query += " ORDER BY received_at DESC LIMIT ?"
    params.append(limit)
    items = rows_to_dicts(ctx.conn.execute(query, params).fetchall())
    out = []
    for item in items:
        cls = to_dict(_latest_classification(ctx.conn, ctx.tenant_id, item["id"]))
        if label and (cls is None or cls["label"] != label):
            continue
        item["classification"] = cls
        out.append(item)
    return {"items": out, "taxonomy": TAXONOMY}


@router.get("/config")
def read_config(
    ctx: SessionContext = Depends(require_permission("classifier.read")),
) -> dict[str, Any]:
    config = get_config(ctx.conn, ctx.tenant_id)
    config["taxonomy"] = TAXONOMY
    return config


@router.put("/config")
def update_config(
    payload: ConfigIn,
    ctx: SessionContext = Depends(require_permission("classifier.manage")),
) -> dict[str, Any]:
    current = get_config(ctx.conn, ctx.tenant_id)
    rules = payload.rules if payload.rules is not None else current.get("rules") or DEFAULT_RULES
    for rule in rules:
        if not isinstance(rule, dict) or "label" not in rule:
            raise HTTPException(422, "Cada regla necesita al menos {label}")
        if rule["label"] not in TAXONOMY:
            raise HTTPException(422, f"Label desconocido en reglas: {rule['label']}")
        for pat in rule.get("patterns", []) or []:
            try:
                re.compile(pat)
            except re.error as exc:
                raise HTTPException(422, f"Regex inválido '{pat}': {exc}") from exc
    threshold = payload.threshold if payload.threshold is not None else float(
        current.get("threshold", DEFAULT_THRESHOLD)
    )
    version = payload.version or str(current.get("version", CLASSIFIER_VERSION))
    ctx.conn.execute(
        """INSERT INTO fnd_classifier_config (tenant_id, rules_json, threshold, version, updated_at)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(tenant_id) DO UPDATE SET
             rules_json = excluded.rules_json, threshold = excluded.threshold,
             version = excluded.version, updated_at = excluded.updated_at""",
        (ctx.tenant_id, json.dumps(rules, ensure_ascii=False), threshold, version, utcnow()),
    )
    ctx.audit("classifier.config.updated", resource_type="classifier_config",
              resource_id=ctx.tenant_id,
              payload={"threshold": threshold, "version": version, "rules_count": len(rules)})
    ctx.emit("classifier", "config.updated", {"threshold": threshold, "version": version})
    config = get_config(ctx.conn, ctx.tenant_id)
    config["taxonomy"] = TAXONOMY
    return config
