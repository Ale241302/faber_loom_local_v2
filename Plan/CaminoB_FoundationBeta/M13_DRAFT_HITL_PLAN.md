# M13 Draft HITL — Plan de Implementación

## 1. Resumen ejecutivo

M13 implementa el ciclo de aprobación humana por **output** (draft). Cuando un agente genera un output con `requires_human_gate=true`, el sistema crea un `Draft` con su `EvidenceBundle`; el Operator/Supervisor/Admin/Owner debe aprobar, editar o rechazar antes de que el sistema lo envíe por el canal configurado. Ningún draft se auto-envía.

**Rol en el SPINE:** consume `Task` (creada por M10), `SystemAgent`, `VoiceProfile`, `D9Gate.pre_egress` (M11), `AuditWriter` (M12), `EventWriter` (M15) y alimenta `OutcomeLedger` (M14).

## 2. Entrada/salida

### Entrada
- `Task` con status `running` y outputs que requieren human gate.
- `EvidenceBundle` con 18 campos canónicos (per-line + per-quote) para cotizaciones; schema reducido para otros tipos.
- `VoiceProfile` del tenant (tono).
- Decisión humana: `approve`, `edit`, `reject`, `cancel`.

### Salida
- `Draft` con status `approved`, `edited`, `rejected`, `sent`, `expired`.
- Mensaje enviado al cliente por el canal configurado (email/WhatsApp).
- Eventos `draft.generated`, `draft.approved`, `draft.edited`, `draft.rejected`, `draft.sent`, `draft.expired`.
- Entrada en Outcome Ledger (M14).
- Audit entry.

## 3. Modelo de datos

### Tablas

```sql
-- Extensión del modelo Task (app `tasks`, creada en M10)
ALTER TABLE tasks ADD COLUMN review_status TEXT CHECK (review_status IN ('pending','accepted','edit_light','rejected',NULL));
ALTER TABLE tasks ADD COLUMN reviewed_by UUID REFERENCES users(id);
ALTER TABLE tasks ADD COLUMN reviewed_at TIMESTAMPTZ;
ALTER TABLE tasks ADD COLUMN review_notes TEXT;
ALTER TABLE tasks ADD COLUMN outputs JSONB;

CREATE TABLE drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
        'pending','awaiting_approval','approved','edited','rejected','sent','expired','approved_pending_send'
    )),
    original_content JSONB NOT NULL DEFAULT '{}',
    edited_content JSONB,
    edit_reason TEXT,
    edit_classification TEXT CHECK (edit_classification IN ('tone','data','structure','policy','scope','context')),
    evidence_bundle_id UUID REFERENCES evidence_bundles(id) ON DELETE SET NULL,
    channel TEXT,  -- email, whatsapp
    recipient TEXT,
    approver_id UUID REFERENCES users(id),
    sent_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE evidence_bundles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    draft_id UUID REFERENCES drafts(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    bundle_json JSONB NOT NULL DEFAULT '{}',
    bundle_hash TEXT NOT NULL,
    client_view JSONB NOT NULL DEFAULT '{}',
    internal_view JSONB NOT NULL DEFAULT '{}',
    privacy_classification TEXT NOT NULL DEFAULT 'N2',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE oscillation_counters (
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_id TEXT NOT NULL,
    consecutive_clean_approvals INTEGER NOT NULL DEFAULT 0,
    last_reset_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (tenant_id, user_id, agent_id)
);
```

### ENUMs / Choices
- `draft.status`: pending, awaiting_approval, approved, edited, rejected, sent, expired, approved_pending_send. El estado `approved_pending_send` (fallo de canal) aparece en SPEC M13 Dim 8.1 y se incorpora al CHECK para operación.
- `task.review_status`: pending, accepted, edit_light, rejected.
- `edit_classification`: tone, data, structure, policy, scope, context.

### Índices
```sql
CREATE INDEX idx_drafts_tenant_status ON drafts(tenant_id, status, expires_at);
CREATE INDEX idx_drafts_task ON drafts(task_id);
CREATE INDEX idx_evidence_bundles_draft ON evidence_bundles(draft_id);
```

### Aislamiento (RLS)
`Draft`, `EvidenceBundle` y `OscillationCounter` son tenant-scoped. Aplicar `FORCE ROW LEVEL SECURITY` y policies por `tenant_id`, siguiendo M16.

### Nota sobre eventos
M15 transporta eventos de dominio de forma genérica. Los eventos de draft (`draft.generated`, `draft.approved`, `draft.edited`, etc.) usan el envelope canónico de M15.

## 4. Cambios en API/backend

### Draft service

```python
# apps/drafts/service.py
class DraftService:
    @classmethod
    def generate(cls, task: Task) -> Draft:
        # 1. Ejecutar skill hasta obtener output
        # 2. Construir evidence bundle
        # 3. Aplicar tone con VoiceProfile
        draft = Draft.objects.create(
            task=task,
            original_content=output,
            evidence_bundle=bundle,
            expires_at=now() + timezone.timedelta(hours=settings.DRAFT_TTL_HOURS),
        )
        emit_event(tenant_id, "draft.generated", {
            "draft_id": str(draft.id), "task_id": str(task.id)
        })
        return draft

    @classmethod
    def approve(cls, draft: Draft, user: User, actor_role: str):
        draft.status = "approved"
        draft.approver = user
        draft.save()
        cls._maybe_send(draft, actor_role)

    @classmethod
    def edit_and_approve(cls, draft: Draft, edited: dict, reason: str,
                         classification: str, user: User, actor_role: str):
        draft.edited_content = edited
        draft.edit_reason = reason
        draft.edit_classification = classification
        draft.status = "edited"
        draft.approver = user
        draft.save()
        cls._maybe_send(draft, actor_role)

    @classmethod
    def reject(cls, draft: Draft, reason: str, user: User, actor_role: str):
        draft.status = "rejected"
        draft.edit_reason = reason
        draft.approver = user
        draft.save()
```

### Pre-egress y envío

```python
    @classmethod
    def _maybe_send(cls, draft: Draft, actor_role: str):
        # D9 pre-egress antes de cualquier envío
        action = PolicyActionContext(
            task_type=draft.task.agent_id,
            data_class=draft.evidence_bundle.privacy_classification,
            skill_id=draft.task.agent_id,
            tenant_id=str(draft.tenant_id),
            source=draft.task.payload.get("source_type", "unknown"),
            case_id=draft.task.payload.get("case_id"),
            retrieved_chunks=[],  # se poblarían desde el evidence bundle si aplica
        )
        output_text = json.dumps(draft.edited_content or draft.original_content)
        decision = D9Gate.pre_egress(str(draft.approver_id), actor_role, action, output_text)
        if not decision.allowed:
            draft.status = "approved_pending_send"
            draft.save()
            return

        ChannelSender.send(draft)
        draft.status = "sent"
        draft.sent_at = now()
        draft.save()
        emit_event(..., "draft.sent", ...)
```

### Oscillation Counter

```python
# apps/drafts/oscillation.py
OSCILLATION_LIMIT = int(os.getenv("OSCILLATION_LIMIT", "10"))

def record_approval(user_id, tenant_id, agent_id, edited: bool):
    counter, _ = OscillationCounter.objects.get_or_create(
        tenant_id=tenant_id, user_id=user_id, agent_id=agent_id
    )
    if edited:
        counter.consecutive_clean_approvals = 0
    else:
        counter.consecutive_clean_approvals += 1
    if counter.consecutive_clean_approvals >= OSCILLATION_LIMIT:
        emit_event(..., "draft.review_cycle_required", ...)
        counter.consecutive_clean_approvals = 0
    counter.save()
```

### Endpoints

| Método | Ruta | Permiso |
|---|---|---|
| GET | `/api/drafts` | workloom:read |
| GET | `/api/drafts/{id}` | workloom:read |
| POST | `/api/drafts/{id}/approve` | workloom:write |
| POST | `/api/drafts/{id}/edit` | workloom:write |
| POST | `/api/drafts/{id}/reject` | workloom:write |
| POST | `/api/drafts/{id}/cancel` | workloom:write |

### Eventos

- `draft.generated`
- `draft.approved`
- `draft.edited`
- `draft.rejected`
- `draft.sent`
- `draft.expired`
- `draft.review_cycle_required`

## 5. Cambios en frontend

### Desktop
- **WorkLoom Zona 2**: cards "Listo para revisar" con cliente, tipo, confidence, SLA.
- Panel de revisión: draft + evidence bundle completo (vista interna).
- Edición inline con diff en tiempo real y dropdown de razón.
- Animación de aprobación y desaparición de card.

### Web
- Vista simple de drafts pendientes e histórico; sin edición inline en E1.

## 6. Cambios en infraestructura/deploy

- Variables de entorno:
  ```bash
  DRAFT_TTL_HOURS=48
  OSCILLATION_LIMIT=10
  EMAIL_BACKEND=smtp  # o sendgrid, etc.
  WHATSAPP_BACKEND=stub  # E1 stub
  ```
- Canal email usa `EmailBinding` (M07).
- Canal WhatsApp: stub en E1.

## 7. Secuencia de tareas

1. Extender modelo `Task` con campos HITL y `outputs`.
2. Crear app Django `drafts` con modelos `Draft`, `EvidenceBundle`, `OscillationCounter`.
3. Implementar generador de evidence bundle (cotización y schema reducido).
4. Implementar state machine del draft.
5. Integrar `D9Gate.pre_egress()` antes de envío.
6. Implementar `ChannelSender` (email + stub WhatsApp).
7. Implementar Oscillation Counter.
8. Emitir eventos y audit.
9. Endpoints de aprobación/rechazo/edicion.
10. Tests de HITL, D9 pre-egress y expiración.

## 8. Criterios de aceptación

1. `test_draft_requires_approval_no_auto_send`: un draft nunca se envía sin aprobación.
2. `test_draft_edit_creates_diff_and_ledger_entry`: edición guarda original, diff y escribe M14.
3. `test_draft_reject_with_reason`: rechazo con razón, no envío.
4. `test_draft_expires_without_action`: al vencer TTL pasa a `expired`.
5. `test_d9_pre_egress_blocks_before_send`: D9 pre-egress bloquea antes de tocar el canal externo.
6. `test_oscillation_counter_fires_after_n_clean_approvals`: tras N aprobaciones sin edición se emite ciclo de revisión.
7. `test_channel_failure_goes_to_approved_pending_send`: fallo de envío → reintento, badge de error.

## 9. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Auto-send bypass | P0 fuga | No existe código path de auto-send; D9 pre-egress obligatorio |
| Edición borra evidence | P1 audit | Original se preserva; diff se hashea |
| Envío por canal equivocado | P1 UX | Canal fijo por tenant/config del draft |
| Aprobador sin permiso | P1 compliance | RBAC M09 + validación en endpoint |
| Drafts acumulados | P2 operación | TTL + expiración + alerta Zona 1 |

## 10. Decisiones de arquitectura tomadas

1. **Aprobación por output/draft, no por task.** Un task puede generar N drafts independientes.
2. **Evidence bundle inmutable y con 3 vistas.** Cliente solo ve vista filtrada.
3. **No hay auto-send en E1.** Todo egress requiere gate humano.
4. **Precio bajo margen no editable.** Validación en `edit` endpoint.
5. **Offline no aprueba en E1.** Las decisiones requieren conexión para permisos y envío.

---
*Plan M13 — Foundation Beta v1.3.1*
