# SCH_FB_TASK_ENTITY — Schema Entidad Tareas (Tasks) FaberLoom
id: SCH_FB_TASK_ENTITY
version: 2.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SCH
stamp: VIGENTE — 2026-04-29f (re-scope FB)
aprobador: CEO (sesión Cowork 2026-04-29 + re-scoping 2026-04-29f)
aplica_a: [FaberLoom]
relacionado: SCH_FB_SKILL_MANIFEST_v2.md · SCH_FB_FLOW_DAG.md · SPEC_FB_AGENT_BUILDER_v1.md

---

## Declaración

Este schema define **tareas (tasks)** como entidad de primera clase en la plataforma FaberLoom. Una tarea es una **instancia de invocación** de un SKILL_ o flow — el "run concreto" disparado por algún canal (ad-hoc desde dashboard del tenant, scheduled cron, webhook externo, o nodo dentro de un flow padre).

La tabla `tasks` incluye `tenant_id` desde día 1 aunque en FB v1 beta exista solo el tenant MWT — esto evita migración traumática cuando entre tenant 2.

**Distinción clave:**
- `SKILL_` define **qué sabe hacer** un agente (capacidad)
- `flow` define **cómo lo hace paso a paso** (plan)
- `task` es **una ejecución concreta** con input específico, status trackeable, y vinculación con su run real

Sin tareas como entidad, no hay forma de:
- Crear invocaciones ad-hoc desde UI ("review esta review_id=123")
- Encolar tareas con prioridad
- Ver tareas pendientes
- Trackear flows complejos donde cada nodo es una sub-tarea
- Aplicar HITL (Human In The Loop) sobre acciones específicas, no sobre el agente entero

---

## Schema tabla `tasks` (Postgres)

```sql
CREATE TABLE tasks (
    -- Identidad
    task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,                  -- ej: SKILL_RW_REVIEW_TRIAGE o WORKFLOW_X
    agent_version TEXT,
    flow_node_id TEXT,                       -- si la tarea es un nodo de un flow padre, su ID

    -- Invocación
    invocation_mode TEXT NOT NULL CHECK (invocation_mode IN ('ad_hoc', 'scheduled', 'webhook', 'flow_node')),
    invoked_by TEXT NOT NULL,                -- ceo | system | flow:<parent_task_id> | webhook:<source>
    invoked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    priority TEXT NOT NULL DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),

    -- Input/output
    payload JSONB NOT NULL,                  -- input al agente
    expected_outputs TEXT[],                 -- IDs esperados de contract.outputs[] del SKILL invocado

    -- Status lifecycle
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN (
        'queued',           -- esperando worker
        'running',          -- en ejecución
        'awaiting_approval', -- esperando aprobación humana (HITL)
        'completed',        -- terminó OK con outputs
        'failed',           -- error técnico
        'cancelled',        -- cancelada antes de completar
        'timeout'           -- excedió timeout
    )),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    expected_completion_by TIMESTAMPTZ,      -- SLA por prioridad

    -- Vinculación con runs reales
    run_id UUID,                             -- ref a episodic_memory(run_id) cuando ejecuta
    parent_task_id UUID,                     -- si es flow_node, el task del flow padre
    child_task_ids UUID[],                   -- si esta tarea spawneó sub-tareas (paralelas o flow nodes)

    -- HITL (Human In The Loop)
    review_status TEXT CHECK (review_status IN ('pending', 'accepted', 'edit_light', 'rejected', NULL)),
    reviewed_by TEXT,
    reviewed_at TIMESTAMPTZ,
    review_notes TEXT,

    -- Outputs producidos (cuando completed)
    outputs JSONB,                           -- mapa {output_id: {value, schema_compliant, persisted_to}}

    -- Auditoría
    tenant_id TEXT NOT NULL DEFAULT 'mwt_internal',
    cost_usd NUMERIC(8, 4),
    error_message TEXT,
    error_code TEXT,

    -- Constraints
    CONSTRAINT fk_run FOREIGN KEY (run_id) REFERENCES episodic_memory(run_id),
    CONSTRAINT fk_parent FOREIGN KEY (parent_task_id) REFERENCES tasks(task_id)
);

CREATE INDEX idx_tasks_status_priority ON tasks(status, priority, invoked_at);
CREATE INDEX idx_tasks_agent ON tasks(agent_id, invoked_at DESC);
CREATE INDEX idx_tasks_parent ON tasks(parent_task_id) WHERE parent_task_id IS NOT NULL;
CREATE INDEX idx_tasks_review ON tasks(status, review_status) WHERE review_status = 'pending';
CREATE INDEX idx_tasks_tenant ON tasks(tenant_id, invoked_at DESC);
```

---

## State machine de la tarea

```
queued ──→ running ──→ completed
   │          │
   │          ├──→ awaiting_approval ──→ completed (post-CEO accept)
   │          │                       └──→ rejected → status: failed
   │          ├──→ failed
   │          └──→ timeout
   └──→ cancelled (sin haber arrancado)
```

Transiciones válidas:
- `queued → running`: worker pickup
- `running → awaiting_approval`: hits HITL gate (output con `requires_human_approval: true`)
- `awaiting_approval → running`: CEO aprobó
- `awaiting_approval → cancelled`: CEO rechazó
- `running → completed`: terminó OK
- `running → failed`: error
- `running → timeout`: excedió timeout
- `queued → cancelled`: cancelada antes de empezar

---

## Endpoints Django

Módulo nuevo: `mwt-knowledge/agents/tasks_api.py`

### POST /api/tasks
Crea tarea ad-hoc.

```json
Request:
{
  "agent_id": "SKILL_RW_REVIEW_TRIAGE",
  "payload": { "review_id": 123, "review_text": "..." },
  "priority": "normal"
}

Response 201:
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "expected_completion_by": "2026-04-29T18:30:00Z",
  "url": "/api/tasks/550e8400-e29b-41d4-a716-446655440000"
}
```

### GET /api/tasks/queue
Cola de tareas pendientes ordenada por priority + invoked_at.

```json
Query params: ?agent_id=SKILL_X&status=queued&limit=50

Response 200:
{
  "count": 12,
  "tasks": [...]
}
```

### GET /api/tasks/{id}
Estado y outputs de una tarea.

### POST /api/tasks/{id}/approve
Aprobar tarea en `awaiting_approval`. Body: `{ "edit_diff": "..." }` opcional para edit_light.

### POST /api/tasks/{id}/reject
Rechazar tarea en `awaiting_approval`. Body: `{ "reason": "..." }`.

### POST /api/tasks/{id}/cancel
Cancelar tarea queued o awaiting_approval.

### GET /api/tasks/stats
Métricas agregadas: cola actual, tasa completion, latencia p50/p95, cost mes.

---

## Dashboard CEO en `portal.mwt.one/agents/tasks`

Vistas obligatorias:

| Vista | Función |
|-------|---------|
| **Cola** | tareas en `queued` y `running`, ordenadas por priority |
| **Pendientes review** | tareas en `awaiting_approval`, con botones Accept / Edit / Reject por output |
| **Histórico** | tareas `completed` últimos 30 días con search |
| **Flow viewer** | si una tarea es flow padre, render del DAG con status por nodo (vis-network o D3) |
| **Stats** | acceptance rate, latencia, cost, errores por SKILL |

Vista crítica: **Pendientes review** alimenta el L3 (Acceptance) de la pyramid de métricas. Sin esto, no hay autonomy graduation posible.

---

## Worker que ejecuta las tareas

Celery task nuevo: `mwt-knowledge/agents/celery_tasks.py::execute_agent_task`

```python
@shared_task(bind=True, max_retries=2)
def execute_agent_task(self, task_id):
    task = Task.objects.get(task_id=task_id)
    task.status = 'running'
    task.started_at = now()
    task.save()

    # Cargar manifest del agent_id
    manifest = load_manifest(task.agent_id)

    # Si archetype workflow, invocar flow_executor
    if manifest['archetype'] in ['workflow', 'routine', 'supervisor']:
        result = flow_executor.execute(manifest, task.payload, task.task_id)
    else:
        result = skill_executor.execute(manifest, task.payload, task.task_id)

    # Persistir outputs
    task.outputs = result['outputs']
    task.run_id = result['run_id']
    task.cost_usd = result['cost_usd']

    # Determinar siguiente estado
    if result.get('requires_approval'):
        task.status = 'awaiting_approval'
        task.review_status = 'pending'
    else:
        task.status = 'completed'
        task.completed_at = now()

    task.save()
    return task.task_id
```

---

## Vinculación con flow

Cuando un `archetype: workflow` ejecuta, el flow_executor:

1. Crea task padre con `agent_id: WORKFLOW_X`, `status: running`
2. Por cada `node` del flow que sea `kind: skill_call`:
   - Crea sub-task con `agent_id: <skill_ref>`, `parent_task_id: <padre>`, `flow_node_id: <node.id>`
   - Espera completion (sync) o spawna paralelo (async para `kind: parallel`)
3. Cuando todas las sub-tasks completan, padre transiciona a `completed`
4. Si una sub-task falla y `fail_policy: stop`, padre falla con propagación

Esto da **trazabilidad completa**: cada step del flow es una task individual con su propio episodic_memory entry. Replay determinístico posible.

---

## HITL (Human In The Loop) granular

A diferencia de los GPTs/agents donde la aprobación es del agente entero, aquí **la aprobación es por output específico**. Si un SKILL emite 3 outputs:

```yaml
contract:
  outputs:
    - { id: response_draft, kind: asset, requires_human_approval: true }   # ← review CEO
    - { id: severity_tag, kind: decision, requires_human_approval: false } # ← auto-persiste
    - { id: escalation_ticket, kind: side_effect, requires_human_approval: true } # ← review CEO
```

Cuando la task entra a `awaiting_approval`, el dashboard muestra **2 ítems** para revisar (response_draft y escalation_ticket), no la task entera. CEO puede:
- Aceptar uno y rechazar otro
- Editar uno y aceptar el otro tal cual
- Aplicar la decisión por output

Esto es lo que valida P3 draft-first absoluto al nivel de granularidad correcta.

---

## Compatibilidad con archetype

| Archetype | Tasks generadas |
|-----------|-----------------|
| `skill` (atómico) | 1 task |
| `workflow` | 1 task padre + N sub-tasks (una por node skill_call) |
| `routine` (cron/webhook) | 1 task padre + N sub-tasks si tiene flow |
| `autonomous` | 1 task con múltiples iterations dentro de un solo run |
| `supervisor` | 1 task padre + N sub-tasks de los sub-agents invocados |

---

## Limitaciones v1

- **No retry inteligente.** `max_retries=2` simple. Para retry exponencial backoff, FB v2.
- **No prioridad dinámica.** Priority se setea al crear, no se ajusta por aging. FB v2.
- **No quotas por tenant.** En FB v1 con un solo tenant beta no aplica; quotas vienen en FB v2 cuando entren tenants pagantes.
- **No observability avanzada de cola.** Métricas básicas; para dashboarding profundo, usar Langfuse + custom queries.

---

Stamp: VIGENTE — 2026-04-29f (re-scope FB)

Changelog:
- v1.0 (2026-04-29b): creación con scope MWT-only erróneo. Schema tabla `tasks` Postgres + state machine 8 estados + 6 endpoints Django + dashboard + worker Celery + vinculación con flow + HITL granular por output.
- **v2.0 (2026-04-29f): re-scope completo a FaberLoom. Renombrado SCH_TASK_ENTITY → SCH_FB_TASK_ENTITY. Tabla `tasks` con `tenant_id` desde día 1 aunque tenant inicial sea único (MWT). Endpoints multi-tenant aware. Dashboard del admin del tenant (no "dashboard CEO" universal). Aprobador: CEO sesión re-scoping 2026-04-29f.**
