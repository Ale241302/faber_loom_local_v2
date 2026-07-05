"""Foundation Beta — módulos M07–M20 portados a FastAPI/SQLite (local-first).

Cada módulo vive en su archivo ``mXX_nombre.py`` y expone un ``router``
(APIRouter). Aquí se agregan todos bajo ``foundation_router`` que main.py
monta en ``/api/foundation``. Los imports son tolerantes a módulos aún no
implementados para no romper el arranque durante el desarrollo incremental.
"""

from __future__ import annotations

import importlib
import logging

from fastapi import APIRouter, Depends

from . import core
from .core import get_conn, init_foundation_db, is_bootstrapped

logger = logging.getLogger("faberloom.foundation")

foundation_router = APIRouter(prefix="/foundation", tags=["foundation"])

# Orden canónico del SPINE + operativos + desktop.
_MODULE_FILES = [
    "m16_tenant_isolation",
    "m08_auth_session",
    "m09_rbac",
    "m15_outbox_streams",
    "m12_audit_trail",
    "m11_policy_gate",
    "m07_bootstrap",
    "m10_classifier",
    "m13_draft_hitl",
    "m14_outcome_ledger",
    "m17_memory",
    "m18_desktop_auth",
    "m19_offline_sync",
    "m20_auto_update",
]

LOADED_MODULES: list[str] = []

for _name in _MODULE_FILES:
    try:
        _mod = importlib.import_module(f".{_name}", __name__)
        _router = getattr(_mod, "router", None)
        if _router is not None:
            foundation_router.include_router(_router)
        LOADED_MODULES.append(_name)
    except ModuleNotFoundError:
        logger.debug("Foundation module %s not present yet", _name)
    except Exception:  # pragma: no cover - defensive
        logger.exception("Failed to load foundation module %s", _name)


@foundation_router.get("/status")
def foundation_status(conn=Depends(get_conn)) -> dict:
    tenant = core.get_active_tenant(conn)
    return {
        "bootstrapped": is_bootstrapped(conn),
        "tenant": core.to_dict(tenant),
        "modules": LOADED_MODULES,
    }


__all__ = ["foundation_router", "init_foundation_db", "core", "LOADED_MODULES"]
