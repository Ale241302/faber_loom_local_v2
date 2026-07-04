# M17 Memory Letta — Plan de Implementación

## 1. Resumen ejecutivo

M17 da a cada agente memoria por capas — **episódica** (append-only), **working** (por tarea, TTL 24h) y **persistent** (con gate humano) — usando Letta self-hosted con namespaces aislados por tenant/agente/tarea. Un `MemoryConflictGuard` garantiza que la memoria nunca contradiga la KB VIGENTE.

**Rol en el SPINE:** consume `tenant_context` (M16), ejecución de agentes, KB VIGENTE y audit (M12). Alimenta ejecución de agentes con contexto y M14 con memorias validadas.

## 2. Entrada/salida

### Entrada
- `task_id`, `agent_id`, `tenant_id`.
- Eventos de ejecución del agente (para episodic).
- Propuestas de memoria persistent generadas por el agente.
- KB VIGENTE chunks.

### Salida
- Items de memoria en Letta con namespaces `mem:tenant:{id}:agent:{agent_id}:task:{task_id}:working`.
- Prompt assembly con working + episodic + persistent (no disputed).
- Propuestas `proposed_persistent` para gate humano.
- Eventos `memory.persisted`, `memory.disputed`, `memory.deprecated`.
- Audit entry por promoción.

## 3. Modelo de datos

### Tablas (metadata en Postgres; contenido en Letta)

```sql
CREATE TABLE memory_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    agent_id TEXT NOT NULL,
    task_id TEXT,  -- NULL para persistent/episodic global
    layer TEXT NOT NULL CHECK (layer IN ('episodic','working','persistent')),
    namespace TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN (
        'active','proposed','disputed','deprecated'
    )),
    promoted_by UUID REFERENCES users(id),
    validity_metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE memory_conflicts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    memory_item_id UUID NOT NULL REFERENCES memory_items(id) ON DELETE CASCADE,
    kb_source TEXT NOT NULL,
    kb_hash TEXT NOT NULL,
    reason TEXT NOT NULL,
    resolved_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### ENUMs / Choices
- `memory_items.layer`: episodic, working, persistent.
- `memory_items.status`: active, proposed, disputed, deprecated.

### Índices
```sql
CREATE INDEX idx_memory_tenant_agent ON memory_items(tenant_id, agent_id, layer, status);
CREATE INDEX idx_memory_conflicts_item ON memory_conflicts(memory_item_id);
```

### Aislamiento (RLS)
`MemoryItem` y `MemoryConflict` son tenant-scoped. Aplicar `FORCE ROW LEVEL SECURITY` y policies por `tenant_id`, siguiendo M16.

### Nota sobre namespace
El SPEC M17 describe namespace `mem:agent:{agent_id}:task:{task_id}:working` sin tenant. Prevalezca la versión con tenant (`mem:tenant:{tenant_id}:agent:{agent_id}:task:{task_id}:working`) porque M16 exige aislamiento por tenant. El helper `apps.core.memory.letta_namespace()` ya incluye `tenant`.

### Nota sobre eventos
M15 transporta eventos de dominio de forma genérica. Los eventos `memory.persisted`, `memory.disputed`, `memory.deprecated` y `memory.proposed` usan el envelope canónico de M15.

## 4. Cambios en API/backend

### Namespace builder

Reutilizar `apps.core.memory.letta_namespace()` existente:

```python
ns = letta_namespace(tenant_id, agent_id, task_id=task_id, kind="working")
```

### Letta client wrapper

```python
# apps/memory/letta_client.py
class LettaMemoryClient:
    def create_working(self, tenant_id, agent_id, task_id, context: dict):
        ns = letta_namespace(tenant_id, agent_id, task_id, "working")
        return self._store(ns, context, ttl=86400)

    def append_episodic(self, tenant_id, agent_id, event: dict):
        ns = letta_namespace(tenant_id, agent_id, kind="episodic")
        return self._append(ns, event)

    def read_context(self, tenant_id, agent_id, task_id) -> dict:
        working = self._read(letta_namespace(tenant_id, agent_id, task_id, "working"))
        episodic = self._read(letta_namespace(tenant_id, agent_id, kind="episodic"))
        persistent = self._read_active_persistent(tenant_id, agent_id)
        return {"working": working, "episodic": episodic, "persistent": persistent}

    def propose_persistent(self, tenant_id, agent_id, content: dict):
        ns = letta_namespace(tenant_id, agent_id, kind="persistent")
        return self._store(ns, content, status="proposed")
```

### MemoryConflictGuard

```python
# apps/memory/guard.py
class MemoryConflictGuard:
    @classmethod
    def check(cls, memory_content: dict, kb_chunks: list[dict]) -> bool:
        # E1: keyword/embedding similarity simple
        for chunk in kb_chunks:
            if cls._contradicts(memory_content, chunk):
                return False
        return True
```

### Prompt assembly

```python
# apps/memory/assembly.py
def build_agent_prompt(task, kb_chunks):
    ctx = LettaMemoryClient().read_context(task.tenant_id, task.agent_id, task.id)
    filtered_persistent = [m for m in ctx["persistent"] if m["status"] != "disputed"]
    # KB VIGENTE siempre gana
    return render_template(
        working=ctx["working"],
        episodic=ctx["episodic"],
        persistent=filtered_persistent,
        kb=kb_chunks,
    )
```

### Sweeper

```python
# apps/memory/tasks.py
@app.task(base=TenantTask)
def sweep_working_memory():
    # Limpia working entries con TTL > 24h
    ...
```

### Endpoints

| Método | Ruta | Permiso |
|---|---|---|
| GET | `/api/memory/agent/{agent_id}` | config:view |
| GET | `/api/memory/proposed` | config:edit |
| POST | `/api/memory/proposed/{id}/approve` | config:edit (Owner/Curator) |
| POST | `/api/memory/proposed/{id}/reject` | config:edit |
| POST | `/api/memory/{id}/deprecate` | config:edit |

### Eventos

- `memory.persisted`
- `memory.disputed`
- `memory.deprecated`
- `memory.proposed`

## 5. Cambios en frontend

### Web / Desktop
- Panel de agente en modo Owner/debug:
  - Memoria usada en la última ejecución.
  - Lista de conflictos `disputed`.
  - Cola de propuestas persistent.
- Botones para aprobar/rechazar/deprecar memorias.

## 6. Cambios en infraestructura/deploy

- Contenedor Letta self-hosted.
- Variables de entorno:
  ```bash
  LETTA_URL=http://letta:8283
  LETTA_TOKEN=
  MEMORY_WORKING_TTL_SECONDS=86400
  ```
- Cron Celery para sweep de working stale.

## 7. Secuencia de tareas

1. Crear app Django `memory`.
2. Modelos `MemoryItem`, `MemoryConflict`.
3. Implementar `LettaMemoryClient` con namespaces.
4. Implementar `MemoryConflictGuard`.
5. Integrar lectura de memoria en prompt assembly.
6. Implementar flujo propose → approve/reject persistent.
7. Implementar sweeper de working.
8. Emitir eventos y audit.
9. Endpoints de gestión de memoria.
10. Tests de aislamiento y conflictos.

## 8. Criterios de aceptación

1. `test_namespace_is_tenant_agent_task_scoped`: namespace incluye tenant/agent/task/kind.
2. `test_working_memory_cleaned_after_ttl`: working >24h se limpia.
3. `test_persistent_requires_human_gate`: no se escribe persistent sin aprobación.
4. `test_disputed_memory_not_injected`: memoria disputed nunca aparece en prompt.
5. `test_kb_wins_over_memory`: si hay conflicto, KB prevalece y memoria se marca disputed.
6. `test_cross_profile_access_blocked`: intento de leer namespace de otro agente/tenant falla y alerta P0.
7. Cada promoción a persistent genera audit entry.

## 9. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Letta caído | P2 degradación | Fallback a prompt sin memoria |
| Memoria contradice KB | P1 output erróneo | MemoryConflictGuard; KB siempre gana |
| Cross-tenant namespace leak | P0 leak | Validación estricta de namespace |
| Episodic mutable | P1 audit | Triggers NO UPDATE/DELETE + app role |
| Working no se limpia | P2 fuga contexto | TTL + sweeper + cleanup al terminar task |

## 10. Decisiones de arquitectura tomadas

1. **KB VIGENTE gana siempre sobre memoria.** Sin excepciones.
2. **Letta como store externo; metadata en Postgres.** Facilita RLS, queries y gobernanza.
3. **Namespace estricto `mem:tenant:{id}:agent:{agent_id}:task:{task_id}:working`.** Previene leaks.
4. **Persistent con gate humano obligatorio.** El agente propone; Owner/Curator aprueba.
5. **Conflict detection E1: keyword + embedding similarity.** Se mejora con modelo específico en S3+.

---
*Plan M17 — Foundation Beta v1.3.1*
