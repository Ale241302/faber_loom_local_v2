# Arquitectura as-built — Agente Vivo (E4)

id: ARCH_FB_LIVING_AGENT_v1
version: 1.1.0
status: AS-BUILT
fecha: 2026-07-13
schema_version: 48

---

## 1. Propósito

Este documento describe la arquitectura *as-built* del Agente Vivo de FaberLoom (Ola 4). Es la fuente de verdad técnica para desarrolladores y auditores; cualquier discrepancia con el código debe resolverse a favor del código y actualizar este documento.

El agente vivo transforma a FaberLoom de un asistente reactivo por workspace en una entidad con:
- **Presencia única** por tenant (`ws-general`).
- **Memoria de corto plazo** personal (CAPA 1).
- **Gobernanza de costos y alineación** (ACE / shadow→natural).
- **Canales bidireccionales** (WhatsApp outbound).
- **Signup controlado** (manual/auto).

---

## 2. Componentes

```
Usuario (ws-general)
        │
        ▼
┌─────────────────────┐
│  presence.py        │
│  · classify_intent  │
│  · gather_index     │
│  · deepdive         │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    ▼             ▼
general      deepdive/task
(INDEX)      (workspace concreto,
              autoridad del usuario)
```

### 2.1 Módulos principales (`app/src/living_agent/`)

| Módulo | Responsabilidad | Archivo clave |
| ------ | --------------- | ------------- |
| `presence.py` | Punto de entrada del chat general; clasifica intención; enruta a general/deepdive/task/chat. | `app/src/living_agent/presence.py` |
| `briefs.py` | Generador INDEX-only de `workspace_brief`; refresh desde ciclo ambiental; key broker en reads. | `app/src/living_agent/briefs.py` |
| `planner.py` | Planificación shadow/natural; `planner_decision_log`; `model_track_record`; shadow report. | `app/src/living_agent/planner.py` |
| `autonomy.py` | ACE: evaluación de promoción, token HITL, degradación por overrun. Nunca auto-promueve. | `app/src/living_agent/autonomy.py` |
| `memory.py` | Propuestas de memoria CAPA 1, consolidación HITL, learning-state. | `app/src/living_agent/memory.py` |
| `feedback.py` | Feedback explícito por mensaje; track record por modelo. | `app/src/living_agent/feedback.py` |
| `orchestrator.py` | Ejecución multi-paso de agent tasks: HITL pause, kill switch, budget, handoff de artefactos. | `app/src/living_agent/orchestrator.py` |
| `tasks.py` | Persistencia de `agent_task` / `agent_task_step`; máquina de estados con transiciones guardadas. | `app/src/living_agent/tasks.py` |

### 2.2 Componentes de soporte

| Componente | Rol |
| ---------- | --- |
| `app/src/ambient.py` | Ciclo ambiental: corre detectores read-only y genera propuestas/drafts. |
| `app/src/ambient_detectors.py` | Detectores: failed_routine, stuck_hitl, budget_exhaustion, mail_without_draft, stale_source, unreviewed_gold, stale_backup_smoke (E5-2). |
| `app/src/health_dashboard.py` | Métricas agregadas del agente por tenant: briefs, tasks, memory blocks, costo 30d. |
| `app/src/key_broker.py` | `resolve_read_level`: decide qué nivel de lectura permite el usuario (CLOSED / INDEX / CONTENT). |
| `app/src/security/injection.py` | Sanitización de contenido; briefs/KB rechazan HTML activo e instrucciones ocultas. |

---

## 3. Flujo pregunta-general

1. `api_create_completion` detecta `workspace.kind == "tenant_general"`.
2. Llama `handle_presence_message(ctx, conn, query)`.
3. `classify_intent` decide: `general`, `deepdive`, `task`, `chat`.
4. `general` → `gather_index_context` lee `workspace_brief` INDEX de workspaces visibles + `memory_block` personal aprobada.
5. `deepdive` → `_resolve_target_workspace` + `resolve_read_level` (key broker). Nunca eleva privilegios.
6. `task` → indica al usuario que use Agent Tasks / workspace concreto.
7. `chat` → saludo u onboarding si el tenant está vacío.

### 3.1 Restricciones de seguridad en `ws-general`

- No se ejecutan acciones desde `ws-general`.
- `@menciones` y `skill_ids` rechazados en chat general.
- Modo `auto` rechazado en chat general.
- `resolve_read_level` conserva autoridad del usuario.
- KB ingestion rechaza HTML activo e instrucciones ocultas.

---

## 4. Flujo task multi-paso

```
Usuario crea agent_task
        │
        ▼
┌─────────────────────┐
│  orchestrator.py    │
│  · run_task         │
│  · _execute_step    │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    ▼             ▼
requires_hitl?   no
    │              │
    ▼              ▼
paused_hitl    ejecuta paso
(+ WorkLoom)   guarda artefacto
    │              │
    └──────┬───────┘
           ▼
    siguiente paso / done / killed
```

- Cada paso se persiste en `agent_task_step`.
- Artefactos entre pasos se guardan en `ObjectStore` con prefijo workspace y cifrado.
- `kill` detiene el task y deja estado consistente con costo parcial.
- El budget se valida antes de cada paso.

---

## 5. Autonomy Ladder (shadow → natural)

| Nivel | Modo | Descripción | Transición permitida |
| ----- | ---- | ----------- | -------------------- |
| 0 | `manual` | Humano elige proveedor/modelo y ejecuta. | → shadow (config) |
| 1 | `shadow` | El agente planifica pero no ejecuta; se registra decisión, costo y alineación. | → natural (HITL token) |
| 2 | `natural` | El agente ejecuta internamente dentro de límites (max 2 niveles de profundidad). | → shadow (auto-degrade por overrun) |

### 5.1 Promoción

- `evaluate_promotion_readiness` revisa: días en shadow ≥ X, decisiones ≥ Y, ahorro ≥ 0, 0 absurdas, no cooldown.
- Si está listo, se genera `confirmation_token` determinista (SHA-256).
- La promoción requiere acción humana con el token; ACE nunca auto-promueve.

### 5.2 Degradación

- `degrade_workspace_if_needed` compara costo real vs estimado.
- Si overrun > umbral (default 150%), degrada a `shadow` automáticamente.
- Se incrementa `oscillation_count`.

---

## 6. Memoria viva CAPA 1

```
eventos latentes del usuario
        │
        ▼
┌─────────────────────┐
│  ambient_detectors  │
│  · memory_proposal  │
└──────────┬──────────┘
           │
           ▼
   memory_proposal (HITL)
           │
    ┌──────┴──────┐
    ▼             ▼
  aprobar      ignorar
    │
    ▼
 memory_block (aprobada)
    │
    ▼
build_memory_context (solo aprobada)
```

- `memory_block` almacena bloques personales aprobados.
- `memory_proposal` es el buffer de propuestas pendientes.
- `orchestrate_memory_proposals` aplica/ignora con doble confirmación HITL.
- `build_memory_context` solo incluye memoria aprobada del usuario.
- `thumbs up` nunca escribe memoria; solo el gate humano consolida.

---

## 7. Tablas de base de datos (v42–v48)

| Versión | Tabla / cambio | Propósito |
| ------- | -------------- | --------- |
| v42 | `workspace_brief` | Caché INDEX-only de estado de workspaces. |
| v43 | `planner_decision_log`, `model_track_record` | Evidencia de decisiones shadow y track record por modelo. |
| v44 | `workspace_routing_policy.mode`, `promoted_at`, `degraded_count`, `last_degraded_at` | Estado de routing por workspace. |
| v45 | `message_feedback` | Feedback explícito por mensaje para track record. |
| v46 | `agent_task`, `agent_task_step`; `task_id` en `usage_record` | Persistencia y ledger de tasks multi-paso. |
| v47 | `user_learning_state`, `memory_proposal`, `memory_block`, `memory_revision` | Memoria viva CAPA 1. |
| v48 | `workspace.kind` (`standard` / `tenant_general`) | Distingue workspaces concretos del workspace general del tenant. |

---

## 8. Interfaces API relevantes

| Método | Endpoint | Descripción |
| ------ | -------- | ----------- |
| GET | `/api/workspaces/general` | Resuelve `ws-general` del tenant actual. |
| POST | `/api/workspaces/{id}/chats/{chat_id}/completions` | Chat general si `workspace.kind == "tenant_general"`. |
| GET | `/api/workspaces/{id}/brief?missing_ok=1` | Lee brief INDEX del workspace. |
| GET/POST | `/api/workspaces/{id}/memory/*` | Propuestas y bloques de memoria CAPA 1. |
| GET/POST | `/api/workspaces/{id}/agent-tasks/*` | CRUD y control de tasks multi-paso. |
| GET | `/api/workspaces/{id}/shadow-report` | Reporte ACE de decisiones shadow. |
| GET | `/admin/tenants/{id}/health` | Health dashboard agregado del tenant. |

---

## 9. Gates de seguridad no negociables

1. **No acciones desde `ws-general`.**
2. **No `@menciones` ni skill_ids en chat general.**
3. **No modo `auto` en chat general.**
4. **`resolve_read_level` conserva autoridad del usuario.**
5. **KB ingestion rechaza HTML activo e instrucciones ocultas.**
6. **ACE nunca auto-promueve.**
7. **Degradación automática por overrun.**
8. **HITL para envío/borrado y consolidación de memoria.**

---

## 10. Pendientes arquitectónicos

- **CAPA 2 organizacional:** memoria compartida a nivel tenant/organización; no implementada en E4.
- **Bundle frontend:** reemplazar Babel standalone por módulos ES/IIFE para eliminar deuda de `var` top-level.
- **Detector `stale_backup_smoke`:** agregar en E5-2 para monitorear frescura de backups.

---

## 11. Referencias

- `docs/faberloom/SPEC_E2_5_ENTIDAD_VIVA.md`
- `docs/faberloom/SCH_FB_TASK_ENTITY.md`
- `docs/faberloom/PLB_FB_E4_ROUTING_NATURAL_v1.md`
- `docs/faberloom/ENT_FB_USER_LEARNING_MODEL_v1.md`
- `docs/audits/AUDIT_E4_CIERRE_20260711.md`
