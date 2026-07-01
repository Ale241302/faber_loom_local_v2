# SPEC_AUDIT_MODULE — Módulo de Auditoría Inmutable
id: SPEC_AUDIT_MODULE
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
type: SPEC
stamp: VIGENTE — 2026-04-28
aprobador: CEO (delegado al Arquitecto Cowork)
aplica_a: [MWT, FaberLoom]
relacionado: SPEC_ACTION_ENGINE.md (D10) · POL_DATA_CLASSIFICATION.md (§M retención) · docs/faberloom/ENT_FB_PRICING_TIERS_v1.md · ARCH_AGENT_PRINCIPLES.md (P9, P13)

---

## Declaración

El Audit Module materializa D10 del Action Engine. Provee trazabilidad inmutable, replay capability, y auditor read-only access para sectores regulados (gobierno, banca, salud, educación).

**Cementado en contract API v1.0** del Engine vía `audit_id` en `ActionResult`. Implementación efectiva: Fase 4-5 del roadmap (post-MVP). El contract evita retrofit major.

---

## Componentes

### 1. AuditEntry (estructura del log inmutable)

```python
class AuditEntry(BaseModel):
    audit_id: UUID
    trace_id: str                       # link a ActionResult
    org_id: Optional[str]
    user_id: Optional[str]
    timestamp: datetime

    # Decision provenance
    intent: str
    action_chain: list[str]             # ej. ["llm.haiku_45", "tool.regex_extract"]
    input_hash: str                     # sha256 del input
    output_hash: str                    # sha256 del output
    data_classification: str            # N0-N4 aplicado
    anonymization_level: str            # L0-L3 aplicado
    conversation_ceiling: Optional[str]

    # Policy version pinning
    policy_version_pinned: dict         # snapshot de policies vigentes
    # ej. {"POL_DATA_CLASSIFICATION": "1.2", "SPEC_ACTION_ENGINE": "1.2"}

    # Hash chain link (D10)
    previous_audit_hash: str            # sha256 de la entry anterior
    entry_hash: str                     # sha256 de ESTA entry
    signature: str                      # firma digital del Engine

    # Orchestration provenance (FG-01 — Fugu session 2026-06-24)
    orchestrator_policy_pool_hash: Optional[str]  # sha256 politica de pool activa
    # Cuando routing usa pool opaco (Fugu Standard, L2.5 advisory Fase 2),
    # loggear hash de la politica vigente en lugar de model_id exacto.
    # None cuando el modelo es nombrado explicito (N3/N4 siempre None).

    # Retention metadata
    retention_class: str                # determinada por data_classification
    storage_tier: Literal["hot", "warm", "cold_immutable"]
```

### 2. Hash chain construction

```
entry_hash = sha256(
    audit_id +
    trace_id +
    timestamp +
    input_hash +
    output_hash +
    policy_version_pinned +
    previous_audit_hash
)
```

Cada entry hashea la anterior. Detección de tampering: si alguien edita una entry, todos los hashes posteriores quedan inconsistentes.

Validación periódica: job cron diario verifica hash chain end-to-end. Si detecta inconsistencia → alerta crítica + freeze del log + auditoría manual.

### 3. Storage segregado

```
Operativo (PostgreSQL):
  └── No retiene audit logs después de N días (default 90)

Audit storage (separado):
  ├── hot      → consultas frecuentes, último año
  ├── warm     → S3 Standard, 1-5 años
  └── cold     → S3 Glacier + Object Lock, 5+ años inmutable
```

S3 Object Lock o Azure Immutable Blob obligatorios para `cold_immutable`. Sin permisos de delete ni edit. Solo append.

### 4. Auditor read-only API

```python
# Endpoint separado de operación
GET /audit/v1/entries
  Auth: MFA + auditor_role
  Filters: tenant_id, user_id, date_range, action_id, policy_version
  Returns: paginated AuditEntry list

GET /audit/v1/replay/{audit_id}
  Reproduces decisión: qué chunks, qué policy, qué routing
  No re-ejecuta — solo muestra el path determinístico

GET /audit/v1/integrity_check
  Returns: hash chain validation status

POST /audit/v1/attestation_report
  Body: {tenant_id, period, standard: "ISO27001"|"SOC2"|"LGPD"}
  Returns: PDF firmado digitalmente con compliance attestation
```

**Audit-of-audit:** cada acceso del auditor también se loguea (en un audit log separado para evitar ciclos). Auditor no puede borrar su propio rastro.

### 5. Compliance attestation reports

Templates por estándar:

| Estándar | Frecuencia mínima | Contenido |
|---|---|---|
| ISO 27001 | Anual | Cumplimiento A.5.12, A.5.13, A.8.* (data handling) |
| SOC 2 Type II | Anual | Trust Services Criteria — Security, Availability, Confidentiality, Privacy |
| LGPD (Brasil) | Bajo demanda regulador | Art. 33 (transferencia internacional), Art. 11 (datos sensibles), Art. 50 (DPO) |
| Ley 1581 (Colombia) | Bajo demanda SIC | Habeas Data — consentimiento, derecho de acceso/rectificación/cancelación |
| Ley 25.326 (Argentina) | Bajo demanda AAIP | Transferencia internacional, datos sensibles |
| Government LATAM | Custom por entidad | Contraloría, transparencia, retención |

Reports generados automáticamente en cron + bajo demanda. Firmados digitalmente con clave del Engine. Verificables por auditor offline.

---

## Roadmap de implementación

| Fase | Sprint | Output |
|---|---|---|
| **Fase 4 — Audit core** | sem 12-14 | AuditEntry schema + hash chain + storage tiered |
| **Fase 4 — Auditor API** | sem 14-15 | Endpoints read-only con MFA + audit-of-audit |
| **Fase 5 — Attestation reports** | sem 16-18 | Templates ISO/SOC2/LGPD + generación periódica |
| **Fase 5 — Compliance ops** | sem 18-20 | Tamper alerting + dashboards + onboarding compliance officer |

**Pre-requisito:** Action Engine v1.2 con D10 cementado en contract (ya hecho 2026-04-28).

---

## Triggers de aborto/pivot

| Trigger | Acción |
|---|---|
| Sem 12: Storage tiered no definido (S3/Azure) | Bloquear Fase 4 hasta decisión infra |
| Sem 14: Hash chain validation cuesta >1% CPU | Optimizar batching o degradar a validation periódica |
| Sem 16: Templates de attestation no aprobados por DPO/abogado | Diferir reports automáticos, hold-the-line manual |
| Sem 20: 0 clientes Enterprise/Government adoptaron audit features | Reconsiderar inversión vs roadmap general |

---

## Performance targets

- AuditEntry write: <5ms p99 (no bloquea call original)
- Hash chain validation: <10s para 1M entries
- Replay capability: <2s p99
- Auditor API query: <500ms p99 con paginación
- Attestation report: <30s para 1 año de tenant

---

## Limitaciones v1.0

| Limitación | Mitigación |
|---|---|
| Hash chain serializado limita throughput a ~1000 writes/s | Sharding por tenant (chain per-tenant) en v2 |
| Storage cold immutable es costoso a escala | Compactación + archive a Glacier Deep cuando edad >5 años |
| Replay requiere snapshots de policies históricas | POL_*.md versionados en git inmutable + tag por release |
| Auditor onboarding manual | Self-service portal en v2 |

---

## Lo que el Audit Module NO es

- **No es observability/logging.** D6 cubre observability técnica (debugging). D10 cubre auditoría regulatoria (compliance). Coexisten.
- **No reemplaza DPA.** El audit log es **evidencia** de cumplimiento del DPA, no el DPA mismo.
- **No es opcional para Enterprise/Government.** Es feature contractual del tier — sin audit, no se puede vender al sector regulado.

---

Changelog:
- v1.1 (2026-06-24): +orchestrator_policy_pool_hash en AuditEntry (FG-01 sesion Fugu).
  Confirma presencia de anonymization_level (ya existia). Sin breaking change.
- - v1.0 (2026-04-28): Creación. AuditEntry schema + hash chain + storage tiered + Auditor API + attestation reports. Cementado por D10 del Action Engine. Roadmap Fase 4-5. Origen: indexa hallazgos audit module + pricing tiers Government.
