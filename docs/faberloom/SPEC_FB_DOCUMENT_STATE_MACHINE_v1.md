# SPEC_FB_DOCUMENT_STATE_MACHINE -- Maquina de estados de documentos KB FaberLoom

---
id: SPEC_FB_DOCUMENT_STATE_MACHINE
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE -- 2026-05-07
aprobador: CEO (delegado al Arquitecto Cowork)
aplica_a: [FaberLoom, MWT (KB hub)]
relacionado: SPEC_FB_DATA_MODEL_v1.md (entidad documents) · SPEC_FB_KNOWLEDGE_ATLAS_v1.md · SPEC_FB_KNOWLEDGE_RIVER_v1.md · POL_FB_KNOWLEDGE_VALIDITY_AND_EXPIRY_v1.md · POL_OUTAGE_CANONICAL_MIRROR_v1.md · ENT_OPS_STATE_MACHINE.md (FROZEN, modelo de referencia)
data_classification: N1
---

## Declaracion

Define la maquina de estados unica para todo documento KB FaberLoom (chunks, fixtures, replay items, agent learning artifacts) desde ingesta hasta tombstone. Cementa los 6 estados ampliados R3#15 + 4 estados base + reglas de transicion versioned-monotonic (no retroceder).

**No reemplaza** `ENT_OPS_STATE_MACHINE` (FROZEN -- maquina operativa MWT cotizaciones). Esta SPEC es la maquina KB documental, dominio distinto.

---

## Por que este documento existe

R3#15 hallazgo: state machine actual de documentos KB es implicita -- estados como `ingested`, `active`, `archived` se infieren del campo `status` sin transiciones formalizadas. Sin maquina explicita:

- Re-chunking ad-hoc no trazable (un doc puede ser re-chunked sin auditoria)
- Quarantine de contenido sospechoso sin protocolo (queda activo en queries con riesgo legal/reputacional)
- Soft-delete contradice retention policies (compliance gap)
- Versionado puede retroceder accidentalmente (drift silencioso vs autoridad documental upstream)

Esta SPEC fija el contrato de estados que el backend MVP1 debe implementar y que el frontend debe respetar al mostrar status indicators.

---

## Las 7 reglas cementadas

### R1 -- Estados completos (10 totales)

```
                    +---------+
                    |  draft  |  (creado, no publicado)
                    +----+----+
                         |
                         v
                  +------+------+
                  |   active    |  (publicado, indexed, queryable)
                  +------+------+
                         |
       +-----------------+-----------------+
       |                 |                 |
       v                 v                 v
+-------------+   +-------------+   +-----------------+
|rescan_      |   | quarantine_ |   |   archived      |
|required     |   | review      |   |  (read-only,    |
+------+------+   +------+------+   |   queryable)    |
       |                 |          +-----------------+
       v                 |                 |
+-------------+          |                 v
|reprocessing |          |          +-------------+
+------+------+          |          | tombstoned  |
       |                 |          +-------------+
       v                 |
+-------------+          |
|  reindexed  |          v
+------+------+   +-------------+
       |          |quarantine_  |
       v          |released     |
+-------------+   +------+------+
|   active    |          |
| (return)    |          v
+-------------+   +-------------+
                  |   active    |
                  | (return)    |
                  +-------------+
```

| Estado | Descripcion | Queryable? | Mutable? |
|---|---|---|---|
| `draft` | Creado, no publicado. WIP del curador. | NO | SI |
| `active` | Publicado, indexed, queryable | SI | NO directo |
| `rescan_required` | Cambio detectado en source, necesita re-lectura | SI (stale flag) | NO |
| `reprocessing` | Re-chunking/embedding en curso | NO | NO |
| `reindexed` | Completado, vector store actualizado, transitorio | SI (canary) | NO |
| `quarantine_review` | Contenido sospechoso, pendiente revision humana | NO | SI (auditor flags) |
| `quarantine_released` | Revisado y liberado, transitorio antes de active | NO | NO |
| `archived` | Inactivo, queryable como historico read-only | SI (con flag) | NO |
| `tombstoned` | Soft-delete, conserva audit, NO en queries operativas | NO (solo audit) | NO |
| `failed` | Error en pipeline (ingest, embed, index), requiere intervencion | NO | SI (operator) |

### R2 -- Transiciones permitidas (DAG monotonic)

Tabla canonica. Cualquier transicion fuera de esta lista debe **rechazarse** por el motor de estados.

| Desde | A | Trigger | Actor |
|---|---|---|---|
| (creacion) | `draft` | API insert | curator, system |
| `draft` | `active` | publish event | curator, system (autopublish skill) |
| `draft` | `tombstoned` | discard event | curator |
| `active` | `rescan_required` | source_change_detected | system (scheduled scan) |
| `active` | `quarantine_review` | flag_event (manual o ML) | curator, auditor, system (ML flag) |
| `active` | `archived` | archive_event (retention policy) | system (POL_FB_KNOWLEDGE_VALIDITY) |
| `active` | `tombstoned` | delete_event (legal/GDPR) | auditor (con audit) |
| `rescan_required` | `reprocessing` | rescan_start | system (worker pool) |
| `reprocessing` | `reindexed` | rescan_complete | system |
| `reprocessing` | `failed` | rescan_error | system |
| `reindexed` | `active` | promote_event (canary OK) | system (auto despues de N min) |
| `reindexed` | `quarantine_review` | post_reindex_flag | system (ML re-flag) |
| `quarantine_review` | `quarantine_released` | review_complete (clear) | auditor |
| `quarantine_review` | `tombstoned` | review_complete (reject) | auditor |
| `quarantine_released` | `active` | release_promote (auto despues de M min) | system |
| `archived` | `tombstoned` | retention_expired | system (POL retention) |
| `failed` | `draft` | manual_recovery | operator (con audit) |
| `failed` | `tombstoned` | give_up | operator (con audit) |

**Inquebrantables:**

- **No retroceso version:** documento en `active` v3 no puede volver a `active` v2. La unica forma de revertir contenido es publicar `active` v4 con contenido equivalente a v2.
- **`tombstoned` es terminal:** no hay transicion desde tombstoned. Recuperar documento tombstoned requiere crear nuevo doc (nuevo id) con referencia historica al tombstone.
- **Quarantine no degrada estado fuente:** un doc en `quarantine_review` no puede saltarse a `archived` directamente. Debe pasar por `quarantine_released` -> `active` -> `archived`.
- **`reprocessing` y `reindexed` son transitorios:** SLA max 30 min en `reprocessing`, max 60 min en `reindexed` antes de auto-promote. Excedido = alerta.

### R3 -- Versioning monotonic per documento

Cada transicion que modifique contenido (`reprocessing -> reindexed`, `draft -> active`) incrementa `document_version` (semver: major.minor.patch).

```python
class DocumentStateTransition:
    document_id: UUID
    from_state: DocumentState
    to_state: DocumentState
    version_before: str   # "1.2.3"
    version_after: str    # "1.3.0" (minor bump por reprocess)
    trigger_event: str
    actor: ActorRef
    timestamp: datetime
    audit_id: UUID
    
    # Rule: version_after > version_before SIEMPRE.
    # Excepcion: estados terminales (tombstoned) y transitorios sin cambio
    # de contenido (rescan_required mantiene version) preservan version.
```

Bumps:
- **Major** (1.x.x -> 2.0.0): cambio source authority (ej. URL movido a otra ubicacion canonica). Requiere re-evaluacion humana.
- **Minor** (1.2.x -> 1.3.0): re-chunking, re-embedding, mejora calidad. Auto via reprocessing.
- **Patch** (1.2.3 -> 1.2.4): metadata fix, tag update, sin cambio de contenido. No requiere reindex.

### R4 -- Audit obligatorio

Cada transicion genera `DocumentStateAuditEntry` inmutable hasheado en chain (per D10 SPEC_ACTION_ENGINE):

```python
class DocumentStateAuditEntry:
    audit_id: UUID
    document_id: UUID
    transition: DocumentStateTransition
    state_snapshot_hash: str  # SHA256 del estado completo del doc en ese momento
    previous_audit_hash: str  # link al audit anterior del doc (chain)
    actor_role: ActorRole
    actor_id: str
    reason: str  # texto libre o codigo enum (manual_quarantine, ml_flag_pii, etc.)
    timestamp: datetime
    signature: str  # HMAC con tenant key
```

Storage: tabla separada del operativo, retencion per POL_FB_KR_PRIVACY_TIERS (default 7 anos Enterprise).

### R5 -- RBAC per transicion

| Actor role | Transiciones permitidas |
|---|---|
| `system` | Todas las automaticas (rescan, reprocess, archive, retention) |
| `curator` | draft -> active, draft -> tombstoned, active -> quarantine_review |
| `auditor` | active -> tombstoned (con justificacion legal), quarantine_review -> quarantine_released, quarantine_review -> tombstoned |
| `operator` | failed -> draft, failed -> tombstoned (recuperacion) |
| `agent_runtime` | NINGUNA. Los agentes leen documentos, no mutan estados. Las flags ML son `system` despues de tool call. |
| `end_user` | NINGUNA. Solo lectura via queries. |

CEO override existe solo via break-glass auditado (per POL_OUTAGE_CANONICAL_MIRROR si requiere modificar canonical).

### R6 -- Tenancy y aislamiento

Todo `DocumentStateTransition` lleva `tenant_id` obligatorio. Estados no se comparten cross-tenant. RLS per tabla.

Excepcion: documentos en KB pool L3 (Knowledge River) tienen `tenant_id = "_pool_l3"` y siguen las mismas reglas de transicion (auditor del comite es el actor para transiciones).

### R7 -- SLA y observabilidad

Metricas obligatorias en dashboard FaberLoom:

| Metrica | Calculo | Alerta si |
|---|---|---|
| `docs_in_reprocessing` | count(state = reprocessing) | >50 simultaneos sostenido 10 min |
| `time_in_reprocessing` | now - state_entered_at | >30 min per doc |
| `time_in_reindexed` | idem | >60 min per doc |
| `quarantine_backlog` | count(state = quarantine_review) | >20 sostenido 24h |
| `failed_recovery_rate` | failed -> draft transitions / failed entries | <80% en 7 dias |
| `tombstone_rate` | tombstones / day | spike >3x baseline |

Storage: timeseries en POL_DETERMINISMO source-of-truth dashboard (DASHBOARD_SNAPSHOT) o ya en runtime FaberLoom telemetry (decision diferida -- ver §Implementacion).

---

## Contract API minimo

```python
from typing import Optional
from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from uuid import UUID

class DocumentState(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    RESCAN_REQUIRED = "rescan_required"
    REPROCESSING = "reprocessing"
    REINDEXED = "reindexed"
    QUARANTINE_REVIEW = "quarantine_review"
    QUARANTINE_RELEASED = "quarantine_released"
    ARCHIVED = "archived"
    TOMBSTONED = "tombstoned"
    FAILED = "failed"

class TransitionRequest(BaseModel):
    tenant_id: str
    document_id: UUID
    target_state: DocumentState
    trigger_event: str
    actor_role: str
    actor_id: str
    reason: Optional[str] = None
    expected_version: Optional[str] = None  # optimistic concurrency

class TransitionResult(BaseModel):
    success: bool
    new_state: Optional[DocumentState]
    new_version: Optional[str]
    audit_id: Optional[UUID]
    error: Optional[str]  # "invalid_transition", "version_conflict", "rbac_denied"

# Endpoint canonico
def transition_document(req: TransitionRequest) -> TransitionResult:
    """
    Validates: RBAC (R5), DAG legality (R2), version monotonicity (R3),
    tenant isolation (R6). On success: writes audit (R4), updates state,
    bumps version, emits event for observability (R7).
    """
    ...
```

---

## Implementacion

| Componente | Implementador | Sprint |
|---|---|---|
| Backend FastAPI -- endpoint `transition_document` | FaberLoom dev | Sprint 1 |
| Tabla `documents` con `state` enum + `version` semver + `state_entered_at` | FaberLoom dev | Sprint 1 |
| Tabla `document_state_audit` con hash chain | FaberLoom dev | Sprint 1 |
| Worker pool reprocessing (consumer Outbox) | FaberLoom dev | Sprint 2 |
| Dashboard metricas R7 | FaberLoom dev | Sprint 2 |
| ML flagging (PII/secrets/abuse) -> quarantine_review | A1.11 RAG_FIREWALL v2 + scope FaberLoom dev | Sprint 3 |
| MWT KB hub adopcion (replicar esquema) | Cowork (KB curator) | post-A1 |

**Decision diferida:** storage timeseries metricas R7. Opciones (a) Postgres con materialized views, (b) TimescaleDB extension, (c) external Prometheus + Grafana. Decision en SPEC_FB_KB_QUALITY_MONITORING (A1.10).

---

## Anti-patrones explicitos

| Anti-patron | Por que falla |
|---|---|
| Mutar `state` directo en SQL sin pasar por `transition_document` | Bypass del audit chain (R4) y RBAC (R5) |
| Permitir `reindexed -> active` con version_after <= version_before | Viola monotonicity R3 -- queries devuelven contenido stale |
| Tombstone como hard-delete (DELETE FROM documents) | Pierde audit chain, viola compliance retention |
| Quarantine sin SLA (sin alerta backlog) | Backlog crece silencioso, contenido legitimo bloqueado en review |
| Agentes mutando state via tool call | Viola R5 -- agentes son consumers read-only |
| Cross-tenant transitions (auditor de tenant A revisando docs tenant B) | Viola R6, riesgo legal severo |

---

## Riesgos asumidos

- **Storage timeseries diferido:** R7 metricas pueden capturarse 100% en v1, pero alertas activas dependen de A1.10. Mitigacion: log estructurado con campos timeseries-friendly, migrable post-A1.10.
- **ML flagging requiere A1.11:** quarantine_review por ML solo opera cuando RAG_FIREWALL v2 con C8 abuse_scoring exista. Hasta entonces, quarantine es 100% manual (curator/auditor flag).
- **Operator break-glass para failed recovery:** sin tracking metrico explicit, recovery rate <80% (alerta R7) puede pasar desapercibido si no hay revisor humano. Mitigacion: dashboard con widget dedicado.
- **MWT KB hub adopcion lazy:** replicar esquema en `mwt-knowledge-hub` requiere migration de archivos existentes. Diferido a post-A1 con sprint mecanico dedicado.

---

## Changelog

```
v1.0 (2026-05-07): Creacion. Origen: PLAN_INTEGRACION_v4_POST_ROUND3.md A1.2.
                   R3#15 hallazgo: 6 estados ampliados (rescan_required,
                   reprocessing, reindexed, quarantine_review,
                   quarantine_released, tombstoned) + 4 estados base
                   (draft, active, archived, failed). Versioned monotonic
                   semver. Audit chain D10. RBAC per transicion.
                   Aplica FaberLoom + MWT KB hub.
```

---

Ultima actualizacion: 2026-05-07 v1.0
Generado por: Cowork (AG-07) -- Arquitecto Ejecutor
