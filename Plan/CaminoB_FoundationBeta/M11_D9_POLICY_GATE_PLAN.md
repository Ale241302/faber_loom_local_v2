# M11 D9 Policy Gate — Plan de Implementación

## 1. Resumen ejecutivo

M11 es el gate de política de datos del Action Engine.  Garantiza que ningún dato N3/N4 se procese o salga sin DPA firmado y ceiling adecuado.  Es fail-closed: si no puede evaluar, bloquea.

**Rol en el SPINE:** consume `ActionContext` (M10 stub), DPA state (M07) y audit writer (M12).  Alimenta a skill execution, M13 outbound y M07 activation.

## 2. Entrada/salida

### Entrada
- `ActionContext`: `task_type`, `data_class`, `skill_id`, `confidence`, `source`, `tenant_id`, `retrieved_chunks[]`.
- DPA state y `data_class_ceiling` del tenant.
- Output pre-egress (texto + chunks).

### Salida
- `PolicyDecision`: `allowed`, `blocked_reason`, `effective_classification`, `requires_human_gate`.
- Eventos `policy.gate.passed`, `policy.gate.blocked`, `policy.classification_mismatch`.
- Audit entry obligatoria.

## 3. Modelo de datos

### Tablas

```sql
CREATE TABLE dpa_statements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL UNIQUE REFERENCES tenants(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'missing' CHECK (status IN ('missing','signed','blocked')),
    signed_by UUID REFERENCES users(id),
    signed_at TIMESTAMPTZ,
    version TEXT NOT NULL DEFAULT 'v1',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE data_classification_defaults (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL,  -- 'email_body', 'kb_chunk', 'whatsapp_msg'
    default_class TEXT NOT NULL CHECK (default_class IN ('N0','N1','N2','N3','N4')),
    overrides JSONB NOT NULL DEFAULT '{}',
    UNIQUE(tenant_id, source_type)
);

CREATE TABLE policy_blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    case_id TEXT,
    declared_class TEXT NOT NULL,
    effective_class TEXT NOT NULL,
    reason TEXT NOT NULL,
    resolved_at TIMESTAMPTZ,
    resolved_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### ENUMs
- `data_class`: N0, N1, N2, N3, N4.
- `dpa_status`: missing, signed, blocked.

## 4. Cambios en API/backend

### Policy engine

```python
# apps/policy/gate.py
class PolicyDecision(BaseModel):
    allowed: bool
    blocked_reason: str | None
    effective_classification: str
    requires_human_gate: bool

class D9Gate:
    def evaluate(self, ctx: Context, action: ActionContext) -> PolicyDecision:
        tenant = get_tenant(ctx.tenant_id)
        ceiling = tenant.plan_features.data_class_ceiling
        dpa = get_dpa_state(ctx.tenant_id)

        declared = action.data_class
        source_default = self._source_default(ctx.tenant_id, action.source)
        retrieved = [c.data_class for c in action.retrieved_chunks]
        effective = max([declared, source_default] + retrieved,
                        key=lambda x: DATA_CLASS_ORDER[x])

        if effective in ('N3', 'N4') and dpa.status != 'signed':
            return PolicyDecision(
                allowed=False,
                blocked_reason='PlanUpgradeRequired: N3/N4 requiere DPA firmado',
                effective_classification=effective,
                requires_human_gate=True,
            )

        if DATA_CLASS_ORDER[effective] > DATA_CLASS_ORDER[ceiling]:
            return PolicyDecision(
                allowed=False,
                blocked_reason='PlanUpgradeRequired: excede ceiling del plan',
                effective_classification=effective,
                requires_human_gate=True,
            )

        return PolicyDecision(
            allowed=True,
            blocked_reason=None,
            effective_classification=effective,
            requires_human_gate=effective in ('N2', 'N3', 'N4'),
        )

    def pre_egress(self, ctx, action: ActionContext, output_text: str, retrieved_chunks):
        # Heurística + opcional modelo classifier ligero
        detected = self._scan_output(output_text, retrieved_chunks)
        effective = max([action.data_class, detected],
                        key=lambda x: DATA_CLASS_ORDER[x])
        if detected != action.data_class and effective in ('N3', 'N4'):
            return PolicyDecision(
                allowed=False,
                blocked_reason='ClassificationMismatch',
                effective_classification=effective,
                requires_human_gate=True,
            )
        return self.evaluate(ctx, action)
```

### Integración con LiteLLM

- Skill execution solo invoca LiteLLM Proxy si `PolicyDecision.allowed=True`.
- Pre-egress se ejecuta antes de enviar output a canal externo (email, API).

### Endpoints

| Método | Ruta | Permiso |
|---|---|---|
| GET | `/api/policy/dpa` | config:view |
| POST | `/api/policy/dpa/sign` | config:edit (Owner) |
| POST | `/api/policy/evaluate` | workloom:write (internal/debug) |
| GET | `/api/policy/blocks` | audit:view |

### Eventos

- `policy.gate.passed`
- `policy.gate.blocked`
- `policy.classification_mismatch`

## 5. Cambios en frontend

### Web
- Vista "Compliance / DPA": estado del DPA, botón firmar (Owner).
- Wizard M07 paso 7: firma DPA obligatoria antes de go-live.

### Desktop
- Card de bloqueo en WorkLoom con motivo y ruta de desbloqueo.
- Botón "Escalar al Owner" para Operator.

## 6. Cambios en infraestructura/deploy

- Configurar LiteLLM Proxy con provider Anthropic-only.
- Variables de entorno:
  ```bash
  LITELLM_URL=http://litellm:4000
  ANTHROPIC_API_KEY=
  DPA_VERSION=v1
  ```

## 7. Secuencia de tareas

1. Crear app Django `policy`.
2. Modelos `DpaStatement`, `DataClassificationDefault`, `PolicyBlock`.
3. Implementar `D9Gate.evaluate()`.
4. Implementar `D9Gate.pre_egress()` con scanner heurístico.
5. Integrar gate en skill execution (antes de LLM call).
6. Integrar pre-egress en envío de drafts (M13).
7. Implementar firma de DPA en wizard.
8. Emitir eventos y audit.
9. Tests de bloqueo N3/N4 sin DPA.
10. Tests de classification mismatch.
11. UI de bloqueo y DPA.

## 8. Criterios de aceptación

1. `test_d9_pre_egress_classification_mismatch_blocks_provider_call`: mismatch bloquea antes de LLM/egress.
2. Dato N3/N4 sin DPA → `PlanUpgradeRequired` y bloqueo.
3. Dato dentro del ceiling y DPA firmado → pasa.
4. Cada bloqueo/paso queda en audit (M12).
5. Owner puede firmar DPA; firma auditable.
6. No existe botón de override del gate.
7. Gate cae cerrado si classifier no responde.

## 9. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Gate bypass por SDK directo | P0 fuga | CI lint bloquea imports de SDK LLM; LiteLLM único egress |
| Sub-declaración de fuente | P1 fuga | Defaults por source_type + pre-egress scanner |
| DPA firmado retroactivo desbloquea todo | P1 UX | Reproceso explícito, no automático silencioso |
| Scanner lento | P2 latencia | Heurística sync + classifier async opcional |
| Mismatch ya egressed | P0 incidente | Runbook P0: marcar incidente, solicitar deletion, notificar |

## 10. Decisiones de arquitectura tomadas

1. **DPA firma in-wizard (checkbox + timestamp).**  Desbloquea go-live sin depender de e-sign externo; legalmente vinculante con audit.
2. **`effective_classification = max(...)` sin override.**  Fórmula sellada.
3. **Anthropic-only en E1.**  LiteLLM Proxy configura un solo provider; simplifica compliance.
4. **Pre-egress heurístico + modelo ligero.**  Heurística rápida para keywords de PII; modelo opcional para casos dudosos.
5. **No hay bypass CEO.**  Cualquier desbloqueo requiere DPA/upgrade reales.

---
*Plan M11 — Foundation Beta v1.3.1*
