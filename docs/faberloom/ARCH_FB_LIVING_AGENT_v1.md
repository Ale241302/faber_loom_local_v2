# Arquitectura — Agente Vivo (E4)

## Componentes

```
Usuario (ws-general)
        │
        ▼
┌───────────────────┐
│  presence.py      │
│  · classify_intent│
│  · gather_index   │
│  · deepdive       │
└─────────┬─────────┘
          │
    ┌─────┴─────┐
    ▼           ▼
general    deepdive/task
(INDEX)    (workspace concreto,
            autoridad del usuario)
```

## Flujo

1. `api_create_completion` detecta `workspace.kind == "tenant_general"`.
2. Llama `handle_presence_message(ctx, conn, query)`.
3. `classify_intent` decide: `general`, `deepdive`, `task`, `chat`.
4. `general` → `gather_index_context` lee `workspace_brief` INDEX de workspaces visibles + `memory_block` personal aprobada.
5. `deepdive` → `_resolve_target_workspace` + `resolve_read_level` (key broker). Nunca eleva privilegios.
6. `task` → indica al usuario que use Agent Tasks / workspace concreto.
7. `chat` → saludo u onboarding si el tenant está vacío.

## Memoria viva (CAPA 1)

- `memory_block`: bloques personales aprobados.
- `memory_proposal`: detecciones read-only del detector.
- `orchestrate_memory_proposals`: aplica/ignora con doble confirmación HITL.
- `build_memory_context`: solo incluye memoria aprobada en el contexto del agente.

## ACE (Alignment / Cost / Execution)

- `planner_decision_log`: cada plan (shadow/natural) persistido.
- `model_track_record`: aceptación/costo/latencia por modelo.
- `get_shadow_report`: decisiones, costos, `human_alignment_score`, `oscillation_count`.

## Gates de seguridad

- No se ejecutan acciones desde `ws-general`.
- `@menciones` y skill_ids rechazados en chat general.
- Modo `auto` rechazado en chat general.
- `resolve_read_level` conserva autoridad del usuario.
- KB ingestion rechaza HTML activo e instrucciones ocultas (`security/injection.py`).

## Archivos clave

- `app/src/living_agent/presence.py`
- `app/src/living_agent/memory.py`
- `app/src/living_agent/planner.py`
- `app/src/living_agent/briefs.py`
- `app/src/health_dashboard.py`
- `app/static/js/health_dashboard.jsx`
- `app/static/js/routing_shadow.jsx`
