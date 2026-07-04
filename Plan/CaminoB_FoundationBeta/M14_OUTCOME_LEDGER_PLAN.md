# M14 Outcome Ledger — Plan de Implementación

## 1. Resumen ejecutivo

M14 registra cada decisión humana sobre un draft (aprobación, edición, rechazo) y correcciones de clasificación, construyendo el pipeline de **gold samples** y el **Learning Thermometer** por agente. Permite al Curator/Owner promover candidates a `ACTIVE` con validaciones y, cuando aplica, segundo aprobador.

**Rol en el SPINE:** consume decisiones de M13 y correcciones de M10. Alimenta skills/classifier (M10) con gold samples y el panel de aprendizaje.

## 2. Entrada/salida

### Entrada
- Decisión HITL: `draft_id`, `decision` (approved/edited/rejected), `diff`, `reason`, `confidence`, `actor_role`, `decision_time_ms`.
- Corrección de clasificación: `classification_result_id`, nuevo `ActionContext`, razón.
- Aprobación/descarte de gold sample por Curator.

### Salida
- `OutcomeLedgerEntry` inmutable.
- `GoldSample` en estado `CANDIDATE`, `ACTIVE`, `discarded`, `deprecated`, `blocked_pending_second_approver`.
- `LearningThermometer` por agente.
- Eventos `gold.candidate.created`, `gold.promoted`, `gold.deprecated`, `ledger.entry.created`.
- Audit entry.

## 3. Modelo de datos

### Tablas

```sql
CREATE TABLE outcome_ledger_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    draft_id UUID REFERENCES drafts(id) ON DELETE SET NULL,
    classification_result_id UUID REFERENCES classification_results(id) ON DELETE SET NULL,
    decision TEXT NOT NULL CHECK (decision IN ('approved','edited','rejected','reclassified')),
    diff JSONB,
    reason TEXT,
    confidence NUMERIC(4,3),
    actor_id UUID NOT NULL REFERENCES users(id),
    actor_role_at_decision TEXT NOT NULL,
    decision_time_ms INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE gold_samples (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    agent_id TEXT NOT NULL,
    skill_id TEXT,
    input_json JSONB NOT NULL DEFAULT '{}',
    output_json JSONB NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'candidate' CHECK (status IN (
        'candidate','active','discarded','deprecated','blocked_pending_second_approver'
    )),
    validations_json JSONB NOT NULL DEFAULT '{}',
    promoter_id UUID REFERENCES users(id),
    second_approver_id UUID REFERENCES users(id),
    promoted_at TIMESTAMPTZ,
    validity_metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE learning_thermometers (
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    agent_id TEXT NOT NULL,
    score INTEGER NOT NULL DEFAULT 0,
    bucket TEXT NOT NULL GENERATED ALWAYS AS (
        CASE
            WHEN score <= 2 THEN 'cold'
            WHEN score <= 5 THEN 'warm'
            ELSE 'hot'
        END
    ) STORED,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (tenant_id, agent_id)
);
```

### ENUMs / Choices
- `decision`: approved, edited, rejected, reclassified.
- `gold_sample.status`: candidate, active, discarded, deprecated, blocked_pending_second_approver.
- `thermometer.bucket`: cold, warm, hot.

### Índices
```sql
CREATE INDEX idx_ledger_tenant_decision ON outcome_ledger_entries(tenant_id, decision, created_at);
CREATE INDEX idx_gold_tenant_status ON gold_samples(tenant_id, status, created_at);
```

### Aislamiento (RLS)
`OutcomeLedgerEntry`, `GoldSample` y `LearningThermometer` son tenant-scoped. Aplicar `FORCE ROW LEVEL SECURITY` y policies por `tenant_id`, siguiendo M16.

### Nota sobre eventos
M15 transporta eventos de dominio de forma genérica. Los eventos `ledger.entry.created`, `gold.candidate.created`, `gold.promoted` y `gold.deprecated` usan el envelope canónico de M15.

## 4. Cambios en API/backend

### Ledger writer

```python
# apps/learning/writer.py
class LedgerWriter:
    @classmethod
    def record_decision(cls, ctx: AuditContext, draft: Draft, decision: str,
                        *, diff=None, reason=None, decision_time_ms=None):
        entry = OutcomeLedgerEntry.objects.create(
            tenant=draft.tenant,
            draft=draft,
            decision=decision,
            diff=diff,
            reason=reason,
            confidence=draft.task.classification_result.confidence if draft.task.classification_result else None,
            actor_id=ctx.actor_id,
            actor_role_at_decision=ctx.actor_role_at_decision,
            decision_time_ms=decision_time_ms,
        )
        emit_event(..., "ledger.entry.created", {"entry_id": str(entry.id)})

        if decision == "approved" and not diff and entry.confidence >= 0.85:
            GoldSample.objects.create(
                tenant=draft.tenant,
                agent_id=draft.task.agent_id,
                input_json=draft.task.payload,
                output_json=draft.original_content,
                status="candidate",
            )
            emit_event(..., "gold.candidate.created", ...)
```

### Gold sample promotions

```python
# apps/learning/gold.py
class GoldSampleService:
    VALIDATIONS = ["schema", "policy", "replay", "scope", "human_approval"]

    @classmethod
    def promote(cls, gold: GoldSample, curator: User, curator_role: str):
        validations = cls._run_validations(gold)
        if not all(validations.values()):
            raise PromotionRejected(validations)

        if cls._requires_second_approver(gold, curator_role):
            gold.status = "blocked_pending_second_approver"
            gold.validations_json = validations
            gold.save()
            return

        gold.status = "active"
        gold.promoter = curator
        gold.promoted_at = now()
        gold.validations_json = validations
        gold.save()
        emit_event(..., "gold.promoted", ...)
        AuditWriter.write(...)

    @classmethod
    def deprecate(cls, gold: GoldSample, curator: User, reason: str):
        gold.status = "deprecated"
        gold.save()
        emit_event(..., "gold.deprecated", {"reason": reason})
```

### Learning Thermometer

```python
# apps/learning/thermometer.py
def update_thermometer(tenant_id: str, agent_id: str):
    score = OutcomeLedgerEntry.objects.filter(
        tenant_id=tenant_id,
        draft__task__agent_id=agent_id,
        decision="approved",
    ).count()  # simplificado E1
    LearningThermometer.objects.update_or_create(
        tenant_id=tenant_id, agent_id=agent_id,
        defaults={"score": min(score, 9), "updated_at": now()}
    )
```

### Endpoints

| Método | Ruta | Permiso |
|---|---|---|
| GET | `/api/learning/ledger` | audit:view / config:view |
| GET | `/api/learning/candidates` | config:view |
| POST | `/api/learning/candidates/{id}/promote` | config:edit (Owner/Curator) |
| POST | `/api/learning/candidates/{id}/discard` | config:edit |
| POST | `/api/learning/gold/{id}/deprecate` | config:edit |
| GET | `/api/learning/thermometer` | workloom:read |

### Eventos

- `ledger.entry.created`
- `gold.candidate.created`
- `gold.promoted`
- `gold.deprecated`

## 5. Cambios en frontend

### Web
- Tab **Aprendizaje**:
  - Learning Thermometer por agente (Cold/Warm/Hot).
  - Lista de candidates con diff y confidence.
  - Vista de validaciones antes de promover.
  - Segundo aprobador para N2+.

### Desktop
- Panel del agente en Workspace muestra thermometer.
- Notificación discreta "Aprendiste N cosas esta semana" (capa usuario).

## 6. Cambios en infraestructura/deploy

- Variables de entorno:
  ```bash
  THERMOMETER_COLD_MAX=2
  THERMOMETER_WARM_MAX=5
  GOLD_SECOND_APPROVER_ROLES=Supervisor,Admin,Owner
  ```
- Job diario `update_learning_thermometers`.

## 7. Secuencia de tareas

1. Crear app Django `learning`.
2. Modelos `OutcomeLedgerEntry`, `GoldSample`, `LearningThermometer`.
3. Implementar `LedgerWriter.record_decision()`.
4. Implementar state machine de gold sample.
5. Implementar 5 validaciones antes de ACTIVE.
6. Implementar segundo aprobador para N2+.
7. Implementar Learning Thermometer.
8. Emitir eventos y audit.
9. Endpoints de curator.
10. Tests.

## 8. Criterios de aceptación

1. `test_approved_high_confidence_creates_candidate`: aprobación sin edición + HIGH → candidate.
2. `test_edited_decision_writes_diff`: edición escribe diff en ledger.
3. `test_promotion_requires_validations`: sin validaciones no pasa a ACTIVE.
4. `test_n2_plus_requires_second_approver`: Supervisor/Admin/Owner segundo aprobador.
5. `test_deprecated_gold_not_used`: skills dejan de usar gold deprecated.
6. `test_thermometer_buckets`: score 0-2 cold, 3-5 warm, 6+ hot.
7. Cada promoción genera audit entry con ambos aprobadores.

## 9. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Over-promotion | P1 agente empeora | 5 validaciones + aprobador humano |
| Gold sample stale | P1 respuesta obsoleta | `validity_metadata` + sweep diario |
| Fuga cross-tenant | P0 leak | RLS; gold samples scoped por tenant |
| Segundo aprobador bypass | P1 compliance | Check de rol en endpoint |
| Score artificialmente alto | P2 autonomía prematura | Umbral conservador en E1 |

## 10. Decisiones de arquitectura tomadas

1. **Thermometer Cold 0-2 / Warm 3-5 / Hot 6+.** Valores del SPEC M14; se ajustan con datos reales.
2. **Candidate → ACTIVE requiere Curator/Owner.** No hay auto-promote.
3. **Segundo aprobador para N2+.** Roles: Supervisor, Admin u Owner.
4. **Gold sample incluye `validity_metadata`.** Liga con `POL_FB_KNOWLEDGE_VALIDITY_AND_EXPIRY_v1`.
5. **Ledger inmutable.** No UPDATE/DELETE; reversiones via `deprecated`.

---
*Plan M14 — Foundation Beta v1.3.1*
