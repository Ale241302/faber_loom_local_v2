# M10 L1 Classifier — Plan de Implementación

## 1. Resumen ejecutivo

M10 transforma cada `feed_item` recibido en una decisión de routing accionable: un `ActionContext` con `task_type`, `data_class`, `skill_id`/`agent_id`, `confidence`, `routing` y SLA. Aplica **Tier 0 deterministico** antes de llamar al LLM; si el confidence es menor a `0.85`, el item queda en `pending_human_review` para que el Operator confirme.

**Rol en el SPINE:** consume `feed_item`, el `SystemAgent` `classify_rfq`, `TenantPlanFeatures`, `D9Gate` (M11), `AuditWriter` (M12) y `EventWriter` (M15). Alimenta la creación de `Task`, WorkLoom Zona 4 y el Outcome Ledger (M14).

## 2. Entrada/salida

### Entrada
- `FeedItem`: `tenant_id`, `source_type` (`email`, `whatsapp`, `manual`), `external_id`, `raw_payload`, `normalized_payload`.
- Catálogo `Tier0Rule` del tenant (system + clonadas por Owner/Admin).
- `ClassifierSkill` activo: prompt, output schema, threshold, modelo, timeout, cost cap.
- Contexto del tenant: `TenantPlanFeatures`, DPA state, work-type pack.

### Salida
- `ActionContext` JSON validado contra el schema del skill.
- `ClassificationResult` persistido con los 13 features y el confidence.
- `Task` creada cuando `confidence >= threshold` y no requiere human gate.
- Eventos `feed.item.dispatched`, `task.created`, `pattern.candidate.detected` (re-clasificación).
- Audit entry obligatoria.

## 3. Modelo de datos

### Tablas

```sql
CREATE TABLE feed_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL,  -- email, whatsapp, manual
    external_id TEXT,
    raw_payload JSONB NOT NULL DEFAULT '{}',
    normalized_payload JSONB NOT NULL DEFAULT '{}',
    data_class TEXT NOT NULL DEFAULT 'N1',
    status TEXT NOT NULL DEFAULT 'received' CHECK (status IN (
        'received','classifying','classified','pending_human_review',
        'routed_to_task','archived','failed','manual_review'
    )),
    received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE classification_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    feed_item_id UUID NOT NULL REFERENCES feed_items(id) ON DELETE CASCADE,
    classifier_skill_id UUID NOT NULL,
    action_context JSONB NOT NULL DEFAULT '{}',
    features JSONB NOT NULL DEFAULT '{}',
    confidence NUMERIC(4,3) NOT NULL,
    routing_zone TEXT NOT NULL DEFAULT 'zone_4',
    status TEXT NOT NULL DEFAULT 'classified' CHECK (status IN (
        'classified','pending_human_review','routed_to_task','failed'
    )),
    model_id TEXT,
    model_version TEXT,
    latency_ms INTEGER,
    cost_usd NUMERIC(8,6),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE tier0_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    pattern JSONB NOT NULL DEFAULT '{}',
    priority INTEGER NOT NULL DEFAULT 0,
    action_context JSONB NOT NULL DEFAULT '{}',
    origin TEXT NOT NULL DEFAULT 'system',  -- system | tenant
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE classifier_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    origin TEXT NOT NULL DEFAULT 'system',  -- system | tenant
    prompt_template TEXT NOT NULL,
    output_schema JSONB NOT NULL DEFAULT '{}',
    threshold NUMERIC(4,3) NOT NULL DEFAULT 0.85,
    model_id TEXT NOT NULL DEFAULT 'anthropic/claude-3-5-haiku-20241022',
    timeout_ms INTEGER NOT NULL DEFAULT 10000,
    cost_cap_usd NUMERIC(8,4) NOT NULL DEFAULT 0.05,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('shadow','active','deprecated')),
    active_version TEXT NOT NULL DEFAULT '1',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    agent_id TEXT NOT NULL,
    invocation_mode TEXT NOT NULL DEFAULT 'inbound' CHECK (invocation_mode IN ('ad_hoc','scheduled','webhook','flow_node','inbound')),
    invoked_by TEXT NOT NULL DEFAULT 'system',
    priority TEXT NOT NULL DEFAULT 'normal' CHECK (priority IN ('low','normal','high','urgent')),
    payload JSONB NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN (
        'queued','running','awaiting_approval','completed','failed','cancelled','timeout'
    )),
    expected_completion_by TIMESTAMPTZ,
    classification_result_id UUID REFERENCES classification_results(id) ON DELETE SET NULL,
    parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### ENUMs / Choices
- `data_class`: N0, N1, N2, N3, N4.
- `feed_item.status`: received, classifying, classified, pending_human_review, routed_to_task, archived, failed, manual_review.
- `task.status`: queued, running, awaiting_approval, completed, failed, cancelled, timeout.
- `routing_zone`: zone_1, zone_2, zone_3, zone_4.

### Índices
```sql
CREATE INDEX idx_feed_items_tenant_status ON feed_items(tenant_id, status, received_at);
CREATE INDEX idx_classification_results_feed_item ON classification_results(feed_item_id);
CREATE INDEX idx_tasks_tenant_status ON tasks(tenant_id, status, expected_completion_by);
CREATE INDEX idx_tier0_rules_tenant_priority ON tier0_rules(tenant_id, priority DESC);
```

### Aislamiento (RLS)
Todas las tablas anteriores son `tenant-scoped`. Aplicar `FORCE ROW LEVEL SECURITY` y policies `USING (tenant_id = current_setting('app.tenant_id')::uuid)`, heredando el patrón de M16.

### Nota sobre eventos
M15 transporta eventos de dominio de forma genérica. El "subset de 6 eventos E1" es el fanout mínimo garantizado; los planes operativos M10-M20 emiten tipos adicionales (`pattern.candidate.detected`, `draft.edited`, etc.) usando el mismo envelope canónico.

## 4. Cambios en API/backend

### ActionContext

```python
# apps/classifier/schemas.py
from dataclasses import dataclass, field
from apps.policy.gate import ActionContext as PolicyActionContext, RetrievedChunk

@dataclass
class ActionContext:
    """Internal classification result. Maps to the D9 PolicyActionContext."""
    tenant_id: str = ""
    case_id: str | None = None
    task_type: str = ""
    data_class: str = "N1"
    skill_id: str = ""
    agent_id: str = ""           # routing detail, not needed by D9
    confidence: float = 0.0
    source: str = ""
    routing: str = "zone_4"
    sla_minutes: int = 60
    payload_normalizado: dict = field(default_factory=dict)
    requires_human_gate: bool = False
    retrieved_chunks: list[RetrievedChunk] = field(default_factory=list)

    def to_policy_action(self) -> PolicyActionContext:
        return PolicyActionContext(
            task_type=self.task_type,
            data_class=self.data_class,
            skill_id=self.skill_id,
            confidence=self.confidence,
            source=self.source,
            tenant_id=self.tenant_id,
            case_id=self.case_id,
            retrieved_chunks=self.retrieved_chunks,
        )
```

### Tier 0 classifier

```python
# apps/classifier/tier0.py
class Tier0Classifier:
    @classmethod
    def match(cls, feed_item: FeedItem, tenant_id: str) -> ActionContext | None:
        rules = Tier0Rule.objects.filter(
            tenant_id=tenant_id, active=True
        ).order_by("-priority")
        for rule in rules:
            if cls._matches(rule.pattern, feed_item.normalized_payload):
                return ActionContext(**rule.action_context, confidence=1.0)
        return None
```

### L1 LLM classifier

```python
# apps/classifier/l1.py
class L1Classifier:
    DEFAULT_THRESHOLD = 0.85

    @classmethod
    def classify(cls, feed_item: FeedItem, skill: ClassifierSkill) -> ClassificationResult:
        features = cls._extract_features(feed_item)
        prompt = skill.prompt_template.format(
            payload=feed_item.normalized_payload,
            features=features,
            work_type_pack=...,  # KB context
        )
        # Anthropic-only via LiteLLM Proxy
        response = litellm_completion(
            model=skill.model_id,
            messages=[{"role": "user", "content": prompt}],
            metadata=litellm_metadata(feed_item.tenant_id),
            timeout=skill.timeout_ms,
        )
        action_context = cls._parse_and_validate(response, skill.output_schema)
        confidence = action_context.get("confidence", 0.0)
        return ClassificationResult.objects.create(...)
```

### Action Engine orchestrator

```python
# apps/classifier/engine.py
class ActionEngine:
    @classmethod
    def process(cls, feed_item: FeedItem, actor_id: str, actor_role: str):
        skill = ClassifierSkill.objects.get_active(feed_item.tenant_id)
        classification_result = cls._tier0_or_l1(feed_item, skill)
        ctx = classification_result.action_context  # ActionContext interno
        decision = D9Gate.evaluate(actor_id, actor_role, action=ctx.to_policy_action())
        if not decision.allowed:
            # Bloqueo M11
            return

        if ctx.confidence < skill.threshold or decision.requires_human_gate:
            feed_item.status = "pending_human_review"
            # Notificar por outbox
            return

        task = Task.objects.create(
            tenant=feed_item.tenant,
            agent_id=ctx.agent_id or ctx.skill_id,
            classification_result=classification_result,
            payload=ctx.payload_normalizado,
        )
        emit_event(tenant_id, "task.created", {"task_id": str(task.id)})


### Endpoints

| Método | Ruta | Permiso |
|---|---|---|
| POST | `/api/classifier/classify` | workloom:write (manual/debug) |
| GET | `/api/classifier/pending` | workloom:read |
| POST | `/api/classifier/{feed_item_id}/confirm` | workloom:write |
| POST | `/api/classifier/{feed_item_id}/reclassify` | workloom:write |
| GET | `/api/classifier/skills` | config:view |
| POST | `/api/classifier/skills/{id}/clone` | config:edit |

### Eventos

- `feed.item.received`
- `feed.item.dispatched`
- `task.created`
- `pattern.candidate.detected`

## 5. Cambios en frontend

### Desktop
- WorkLoom **Zona 4**: cards de items clasificados/inciertos con tipo, confidence HIGH/LOW y SLA.
- Panel de corrección: dropdown de tipo/razón al re-clasificar.
- Modo Owner/debug: "Ver cómo clasificó" con `ActionContext` y los 13 features.

### Web
- Skill Factory: clonar/promover/deprecar skills L1 con sandbox obligatorio.

## 6. Cambios en infraestructura/deploy

- LiteLLM Proxy configurado con provider Anthropic-only.
- Variables de entorno:
  ```bash
  CLASSIFIER_MODEL=anthropic/claude-3-5-haiku-20241022
  CLASSIFIER_THRESHOLD=0.85
  CLASSIFIER_TIMEOUT_MS=10000
  CLASSIFIER_COST_CAP_USD=0.05
  ```
- Seed `classify_rfq` system skill en wizard de bootstrap (M07).

## 7. Secuencia de tareas

1. Crear app Django `tasks` como dueña del modelo `Task`; M10 y M13 solo la consumen/extienden.
2. Crear app Django `classifier`.
3. Modelos `FeedItem`, `ClassificationResult`, `Tier0Rule`, `ClassifierSkill`; `Task` vive en `tasks`.
3. Seed `classify_rfq` origin=system en bootstrap.
4. Implementar `Tier0Classifier.match()`.
5. Implementar `L1Classifier.classify()` con schema validation y 13 features.
6. Integrar `D9Gate.evaluate()` antes de routing.
7. Implementar `ActionEngine.process()`.
8. Emitir eventos y audit entry.
9. Endpoints manual, pending y skills.
11. Tests cross-tenant, threshold y fallback.

## 8. Criterios de aceptación

1. `test_tier0_exact_match_creates_task`: Tier 0 match devuelve confidence 1.0 y crea `Task`.
2. `test_l1_low_confidence_goes_to_human_review`: confidence < 0.85 → `pending_human_review`, sin `Task`.
3. `test_l1_high_confidence_creates_task`: confidence >= 0.85 y D9 permite → `task.created`.
4. `test_n3n4_without_dpa_blocked`: D9 bloquea y no se crea task.
5. `test_l1_llm_error_retries_and_fallbacks`: 3 reintentos, fallback a Tier 0/default, luego `manual_review`.
6. `test_cross_tenant_classifier_skill_isolation`: tenant A no ve skills/tier0 de B.
7. Cada clasificación genera audit entry con `actor_role_at_decision`.

## 9. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Alucinación del LLM | P1 enrutamiento erróneo | Schema validation + threshold + human gate |
| Reglas Tier 0 descontroladas | P1 complejidad | Prioridad, sandbox obligatorio antes de promote |
| Costo/tokens excesivos | P2 presupuesto | Cost cap, token estimator, timeout |
| Fuga de skill entre tenants | P0 leak | RLS + tenant_id FK en todos los modelos |
| Threshold rígido | P2 UX | Configurable por skill con hard cap |

## 10. Decisiones de arquitectura tomadas

1. **Threshold default 0.85.** Valor del SPEC M10; ajustable en skill clonado dentro de hard caps.
2. **Tier 0 deterministico primero.** Reduce costo y latencia; el LLM solo cuando no hay match.
3. **Modelo Anthropic-only Haiku 4.5.** LiteLLM Proxy como único egress; DPA firmado con Anthropic.
4. **`ActionContext` versionado por skill.** Cada versión del skill define su schema; rollback = volver a versión ACTIVE previa.
5. **Task creada en M10.** M13 extiende el mismo modelo `Task` para HITL/drafts.

---
*Plan M10 — Foundation Beta v1.3.1*
