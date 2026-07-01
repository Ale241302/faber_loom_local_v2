# Auditoría Frontend — Agente 2 · DEVELOPER FRONTEND

**Proyecto:** FaberLoom / SpaceLoom Foundation Beta  
**Fecha:** 2026-06-24  
**Auditor:** Agente 2 — DEVELOPER FRONTEND  
**Repo canónico revisado:** `C:\dev\mwt-knowledge-hub\`  
**Stack confirmado:** Next.js 15 App Router + TanStack Query v5 + Zustand + WebSocket nativo (`useFaberloomWS`)

---

## 1. Resumen Ejecutivo

La interfaz de FaberLoom/SpaceLoom está definida en **dos superficies operativas complementarias**: la **Mesa de Control** (trabajo del día a día, 5 zonas plegables) y el **Workspace/SpaceLoom** (sistema vivo + constructor, chat-first con 3 modos). La arquitectura de estado frontend (`SPEC_FB_FRONTEND_REALTIME_STATE_v1`) es sólida: server-state vía TanStack Query, UI-state vía Zustand y sincronización vía WebSocket con reconexión y `last_event_id`. Sin embargo, **existen vacíos críticos que bloquean la implementación inmediata** de varios componentes solicitados:

1. **Tres documentos obligatorios del prompt no existen** en las rutas indicadas (`SPEC_FABERLOOM_MVP.md`, `SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md`, `SPEC_FABERLOOM_AGENT_COMPOSITION_v1.md`). Su contenido está disperso en otros specs, lo que genera riesgo de interpretaciones divergentes.
2. **La Zona 5 · Automatizaciones carece de endpoints REST y eventos WebSocket**. `SPEC_FB_INTEGRATION_LAYER_v1` no los incluye y `SPEC_FB_EVENTING_AND_OUTBOX_v1` no define eventos de automatización. Esto es un bloqueador para S5/S7.
3. **El algoritmo de detección de los 3 modos del Workspace** (Operar / Automatizar / Construir) no está especificado. Sin él, el parser del Composer no puede decidir qué pipeline invocar.
4. **No existen file-upload endpoints** en la capa de integración (marcado explícitamente como pendiente), lo que bloquea adjuntos en Composer, Mesa e Inbox.
5. **Los estados de WorkLoom no están canonicalizados**: `PLAN_DESARROLLO_FABERLOOM_v5` usa 4 estados y `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1` usa otros 4 estados distintos.

La recomendación principal es **no comenzar a codificar S5/S7 hasta cerrar los contratos de Zona 5, Workspace 3 modos y upload**, mientras S1-S3 (auth, KB, engine, chat básico) sí pueden avanzar con los specs existentes.

---

## 2. Contexto y archivos consultados

### 2.1 Documentación leída (rutas canónicas)

| Archivo | Ruta real | Estado | Relevancia para esta auditoría |
|---------|-----------|--------|-------------------------------|
| `SPEC_FB_FRONTEND_REALTIME_STATE_v1.md` | `docs/faberloom/SPEC_FB_FRONTEND_REALTIME_STATE_v1.md` | VIGENTE | Arquitectura de estado, hooks, query keys, WS handlers. |
| `SPEC_FB_INTEGRATION_LAYER_v1.md` | `docs/faberloom/SPEC_FB_INTEGRATION_LAYER_v1.md` | VIGENTE | Endpoints REST, headers, WS protocol, idempotencia, paginación. |
| `SPEC_FB_EVENTING_AND_OUTBOX_v1.md` | `docs/faberloom/SPEC_FB_EVENTING_AND_OUTBOX_v1.md` | VIGENTE | 28 eventos WS, schema de evento, reconnect, fanout. |
| `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1.md` | `docs/faberloom/SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1.md` | VIGENTE | Mesa 5 zonas, Workspace 3 modos, @mención, Contexto activo, Tab Aprendizaje, Responsive. |
| `SPEC_SPACELOOM_ETAPA1_v1.md` | `docs/faberloom/SPEC_SPACELOOM_ETAPA1_v1.md` | DRAFT | Definición de Etapa 1 single-user, Inbox/WorkLoom/SpaceLoom, Routine Hub. |
| `PLAN_DESARROLLO_FABERLOOM_v5.md` | `docs/faberloom/PLAN_DESARROLLO_FABERLOOM_v5.md` | DRAFT | Timeline E0-E5, WorkLoom kanban, SpaceLoom E1, responsive móvil. |
| `PLB_FB_FOUNDATION_BETA_v1.md` | `docs/faberloom/PLB_FB_FOUNDATION_BETA_v1.md` | FIRMADO v1.3.2-enmendado | Contrato de ejecución: TIER 1, Skill Factory, Agent Factory, HITL, roles, stack. |
| `IDX_FB_FOUNDATION_BETA.md` | `docs/faberloom/IDX_FB_FOUNDATION_BETA.md` | VIGENTE | Índice maestro, artefactos, mockups. |
| `DESIGN_FABERLOOM_v1.md` | `docs/faberloom/DESIGN_FABERLOOM_v1.md` | alpha | Tokens, breakpoints, tipografía, componentes base. |
| `MOCK_FABERLOOM_v1.html` | `docs/faberloom/mocks/MOCK_FABERLOOM_v1.html` | REFERENCIA | Mock navegable de Workspace con chat, preview, tabs Configurar/Iterar/Sanidad. |
| `POL_FABERLOOM_SURFACE_CONTRACT.md` | `docs/faberloom/POL_FABERLOOM_SURFACE_CONTRACT.md` | DRAFT v0.2 | Contrato de superficies: primitivas shell, Context Dock, ActionFooter, naming Workspace/SpaceLoom. |
| `SKILL_FRONTEND_TEN_PRINCIPLES_V2.md` | `docs/faberloom/SKILL_FRONTEND_TEN_PRINCIPLES_V2.md` | SHADOW | Lente cognitiva frontend con 14 principios y flags P0/P1/P2. |
| `SPEC_FB_BUILD_SEQUENCE_v3.md` | `docs/faberloom/SPEC_FB_BUILD_SEQUENCE_v3.md` | DRAFT | Secuencia E0-E4, hitos 2a/2b, gates. |
| `SCH_FB_WS_INSTRUCTIONS_v1.md` | `docs/faberloom/SCH_FB_WS_INSTRUCTIONS_v1.md` | DEFERRED E3+ | Instrucciones de modulación workspace por voz (no gobierna E1-E2). |
| `ENT_FB_BRAND_DUAL_NAMING_v1.md` | `docs/faberloom/ENT_FB_BRAND_DUAL_NAMING_v1.md` | VIGENTE | Nombre comercial "Mesa de Control de Cotizaciones Técnicas". |
| `ENT_FB_USER_LEARNING_MODEL_v1.md` | `docs/faberloom/ENT_FB_USER_LEARNING_MODEL_v1.md` | VIGENTE | Patterns L2 personal, candidate/apply/ignore/rollback. |
| `SPEC_FABERLOOM_DESIGN_FOUNDATION_v1.md` | `docs/faberloom/SPEC_FABERLOOM_DESIGN_FOUNDATION_v1.md` | VIGENTE | Fundamentos de diseño (leído como parte del contexto). |
| `ARCH_AGENT_PRINCIPLES.md` | `docs/ARCH_AGENT_PRINCIPLES.md` | VIGENTE | Principios P3 draft-first absoluto, P14 deterministic-first, etc. |
| `SPEC_ACTION_ENGINE.md` | `docs/SPEC_ACTION_ENGINE.md` | VIGENTE | Action engine, human gates, side effects. |
| `POL_DATA_CLASSIFICATION.md` | `docs/POL_DATA_CLASSIFICATION.md` | VIGENTE | Clases de datos N0-N4. |
| `ENT_PLAT_MEMORY_STACK.md` | `docs/ENT_PLAT_MEMORY_STACK.md` | DRAFT | Stack de memoria (Letta/pgvector). |
| `ENT_PLAT_ACTION_REGISTRY.md` | `docs/ENT_PLAT_ACTION_REGISTRY.md` | VIGENTE | Catálogo de acciones. |
| `SCH_ACTION_SPEC.yaml` | `docs/SCH_ACTION_SPEC.yaml` | VIGENTE | Schema de acciones registrables. |
| `CLAUDE.md` | `docs/archivo/CLAUDE.md` | VIGENTE | Instrucciones del arquitecto ejecutor. |

### 2.2 Archivos obligatorios del prompt que NO existen en la ruta indicada

| Archivo esperado | Ruta real encontrada (si aplica) | Impacto |
|------------------|----------------------------------|---------|
| `docs/CLAUDE.md` | `docs/archivo/CLAUDE.md` | Ruta desplazada; contenido accesible. |
| `docs/faberloom/ENT_PLAT_MEMORY_STACK.md` | `docs/ENT_PLAT_MEMORY_STACK.md` | Ruta desplazada; contenido accesible. |
| `docs/faberloom/ENT_PLAT_ACTION_REGISTRY.md` | `docs/ENT_PLAT_ACTION_REGISTRY.md` | Ruta desplazada; contenido accesible. |
| `docs/faberloom/SCH_ACTION_SPEC.yaml` | `docs/SCH_ACTION_SPEC.yaml` | Ruta desplazada; contenido accesible. |
| `docs/faberloom/SPEC_FABERLOOM_MVP.md` | **No existe** | Contenido disperso en `PLB_FB_FOUNDATION_BETA_v1`, `SPEC_FB_BUILD_SEQUENCE_v3`, `SPEC_SPACELOOM_ETAPA1_v1`. |
| `docs/faberloom/SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md` | **No existe** | Parcialmente cubierto por `SCH_FB_FLOW_DAG.md` y `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1`. |
| `docs/faberloom/SPEC_FABERLOOM_AGENT_COMPOSITION_v1.md` | **No existe** | Cubierto por `ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1.md` y `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1`. |

---

## 3. Auditoría por componente

### 3.1 Mesa de Control: 5 zonas plegables

**Fuente de verdad:** `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1.md` §8.1, §8.3; `ENT_FB_BRAND_DUAL_NAMING_v1.md` §3.1.

#### ¿Por qué existe?
Es la **superficie operativa única** que absorbe toda la operación diaria del usuario (trabajo que requiere su decisión). Reemplaza la separación previa entre Mesa, Inbox RFQs, Flujos y Status de agentes, reduciendo carga cognitiva.

#### ¿Qué produce?
Un dashboard full-width con 5 zonas plegables:

| Zona | Contenido | Default | Producción UI |
|------|-----------|---------|---------------|
| Z1 · Lo urgente | Hero con drafts en alarma/alta prioridad. Acciones: Aprobar / Iterar / Descartar. | Expandida | Banner/hero card con CTA primario coral. |
| Z2 · Esperando tu firma | Lista compacta de drafts listos para HITL. Acciones inline rápidas. | Expandida | Lista de cards/rows con botones Aprobar/Iterar/Descartar. |
| Z3 · SANDBOX esperando promote | Agentes/skills nuevos creados vía Workspace, esperando firma CEO. | Expandida si hay items | Lista de candidatos con acción "Promover" (Owner/Admin). |
| Z4 · Inbox completo | Todo lo entrante (auto-resueltos, spam, ruteados, pendientes) con filtros + iteración con `@mail_X`. | Plegada | Lista priorizada con filtros y acciones por tipo. |
| Z5 · Automatizaciones activas | Triggers + crons + reglas activas. Pausar/reactivar inline. | Plegada | Lista de automatizaciones con switch on/off. |

#### ¿Cómo funciona?
- **Server-state:** `qk.feed`, `qk.feedFiltered(state, tag)`, `qk.draftsPending`, `qk.drafts(draftId)`.
- **REST:**
  - `GET /api/v1/feed?state=urgent|firma|calma&tag=RECIBIDO|LISTO|ALARMA&limit=20&cursor=<id>`
  - `GET /api/v1/feed/{item_id}`
  - `POST /api/v1/feed/{item_id}/dispatch`
  - `POST /api/v1/feed/{item_id}/archive`
  - `POST /api/v1/drafts/{draft_id}/approve|edit|reject` (con `x-idempotency-key`)
- **WebSocket:** `feed.item.new`, `feed.item.dispatched`, `feed.item.archived`, `draft.ready_for_signature`, `draft.approved`, `draft.edited`, `draft.rejected`, `pattern.candidate.detected`, `agent.alarma`.
- **UI-state:** Zustand guarda `feedFilter`, `selectedItemId`, estado plegado de cada zona.

#### ¿Cómo se relaciona?
- Con **Workspace/SpaceLoom**: al hacer click en "Abrir Workspace" de una card, se abre el Workspace contextual con `context_pack` del caso.
- Con **Inbox**: Zona 4 absorbe la vista de Inbox completo (antes pantalla separada).
- Con **Agent Factory / Skill Factory**: Zona 3 muestra candidatos creados en Workspace/Factory pendientes de promote.
- Con **Zona 5 Automatizaciones**: toggle on/off de agentes (panel lateral) y lista de automatizaciones.

#### ¿Qué endpoints o contratos faltan?
- **Mock v6 de Mesa con 5 zonas** no fue encontrado; solo existe `MOCK_FABERLOOM_v1.html` (Workspace) y referencias a `mesa_de_control_v5.html`/`mesa_e1_faberloom.html` en `IDX_FB_FOUNDATION_BETA.md`.
- **Especificación de filtros por zona**: ¿cómo se mapean `state=urgent|firma|calma` a Z1/Z2/Z4? ¿Z5 usa otro endpoint?
- **Paginación por zona**: cada zona podría requerer su propio cursor; hoy solo existe `GET /api/v1/feed`.
- **Acciones primarias contextualizadas**: el spec describe "Resolver override", "Revisar y aprobar", "Abrir Workspace", "Actualizar fuente", "Elegir plantilla", pero no hay un endpoint o schema para obtener la acción primaria sugerida por caso.

---

### 3.2 WorkLoom cards

**Fuente de verdad:** `PLAN_DESARROLLO_FABERLOOM_v5.md` §E2; `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1.md` changelog v1.7; `SPEC_SPACELOOM_ETAPA1_v1.md` §3.

#### ¿Por qué existe?
Es la **mesa HITL (Human-in-the-Loop)**. Donde el operador revisa drafts generados por agentes, toma decisiones y captura el "por qué" de cada edición/rechazo para alimentar el gold loop.

#### ¿Qué produce?
Una vista tipo Kanban con cards accionables por estado. Cada card muestra:

- Tipo de tarea (RFQ, seguimiento, cobranza post-dictamen)
- Cliente / cuenta
- Canal de origen (mail, WhatsApp, webform)
- Ruta interna (agente/skill que lo generó)
- Confidence score
- Costo estimado
- SLA / timer
- Responsable
- Próxima acción
- Acción primaria contextual

#### ¿Cómo funciona?
- **Estados según `PLAN_DESARROLLO_FABERLOOM_v5`:** `TU CRITERIO / ESPERANDO / DELEGADO / ERROR`.
- **Estados según `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1` v1.7:** `Crítico / Listo para revisar / Delegado / Error accionable`.
- **REST:**
  - `GET /api/v1/drafts/pending`
  - `GET /api/v1/drafts/{draft_id}` (detalle + evidence bundle)
  - `POST /api/v1/drafts/{draft_id}/approve`
  - `POST /api/v1/drafts/{draft_id}/edit` — body `{body_edited, reason: dato|tono|fuente|accion|contexto, free_text?}`
  - `POST /api/v1/drafts/{draft_id}/reject` — body `{reason, free_text?}`
- **WebSocket:** `draft.generated`, `draft.ready_for_signature`, `draft.approved`, `draft.edited`, `draft.rejected`, `draft.sent`, `draft.signature_blocked`.
- **Query keys:** `qk.draftsPending`, `qk.draft(draftId)`.

#### ¿Cómo se relaciona?
- Alimenta las **Zonas 1 y 2 de la Mesa de Control**.
- Al hacer click en una card se abre el **Detalle del caso** con 3 tabs: Ver solución / Editar / Workspace.
- El tab **Workspace** contiene el Workspace contextual para iterar.
- Los rechazos/edits alimentan el **Tab Aprendizaje** y los **gold samples**.

#### ¿Qué endpoints o contratos faltan?
- **Canonicalización de estados**: hay dos nomenclaturas distintas. Se necesita un mapping único.
- **Endpoint de reasignación / Delegado**: no existe `POST /api/v1/drafts/{id}/reassign` ni `POST /api/v1/tasks/{id}/reassign` en `SPEC_FB_INTEGRATION_LAYER_v1` aunque `PLB_FB_FOUNDATION_BETA_v1` §2.4 menciona `/tasks/{id}/reassign`.
- **Schema de la card**: no hay un Pydantic/TS type público para la card de WorkLoom (campos obligatorios, formato de SLA, costo, acción primaria).
- **Evento WS para cambio de estado/owner**: `draft.reassigned` o `task.delegated` no están en los 28 eventos canónicos.

---

### 3.3 Workspace: 3 modos de detección

**Fuente de verdad:** `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1.md` §8.5; `POL_FABERLOOM_SURFACE_CONTRACT.md` nota de alineación Workspace/SpaceLoom.

#### ¿Por qué existe?
Es el **constructor self-extending** del sistema. Permite al usuario operar, automatizar y crear nuevas capacidades conversando, sin salir del chat. Respeta HITL absoluto: nada va a PROD sin firma CEO.

#### ¿Qué produce?
Un chat universal (renombrado a **SpaceLoom** en shell consolidated v2) con 3 modos detectados automáticamente:

1. **Operacional · presente**: encadena agentes existentes ahora. Ej: `"@mail_alvaro buscá X, después @cotizador armá Y"`.
2. **Automatización · futuro**: crea/modifica trigger + flow. Ej: `"Cuando llegue correo así, hacé esto"`.
3. **Construcción · capacidad nueva**: sistema detecta gap → propone crear agente nuevo heredando del catálogo canon → SANDBOX → CEO promote desde Mesa Zona 3.

#### ¿Cómo funciona?
- **REST:**
  - `POST /api/v1/agents/{agent_name}/chat` — iterar con agente.
  - `POST /api/v1/feed/{item_id}/dispatch` — asignar item a agente.
  - `POST /api/v1/learning/patterns/{pid}/apply` — aplicar pattern detectado.
  - `POST /api/v1/agents` — crear agente nuevo (vía Agent Factory).
- **WebSocket:** `agent.iterate.started`, `agent.alarma`, `agent.config.updated`, `agent.shadow_promote`, `pattern.candidate.detected`.
- **UI-state:** modo activo, agente seleccionado, menciones en composer, context pack activo.

#### ¿Cómo se relaciona?
- Con **Composer**: recibe las `@menciones` y decide qué agentes/skills invocar.
- Con **Mesa Zona 3**: envía candidatos a promover.
- Con **Agent Factory / Skill Factory**: los modos Automatización y Construcción terminan en los wizards de creación.
- Con **Contexto activo**: el Workspace siempre muestra el contexto del espacio activo.

#### ¿Qué endpoints o contratos faltan?
- **Algoritmo de detección de modo**: no existe spec ni pseudo-código que defina cómo el sistema decide si una consulta es Operar / Automatizar / Construir. Es un gap funcional crítico.
- **Schema del mensaje por modo**: el body de `POST /api/v1/agents/{name}/chat` no distingue modos.
- **Transición entre modos**: no está definido si el usuario puede forzar un modo o si el sistema propone.
- **Mock de modos Automatización y Construcción**: `MOCK_FABERLOOM_v1.html` solo muestra el modo Operacional con un chat de cotización.

---

### 3.4 Composer

**Fuente de verdad:** `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1.md` §8.4 (todo-es-agente + @mención), §v1.9 (composer foco), `MOCK_FABERLOOM_v1.html`.

#### ¿Por qué existe?
Es el **punto de entrada universal** para hablar con la IA, invocar agentes, adjuntar archivos y cambiar el modo de ejecución (económico/balanceado/calidad).

#### ¿Qué produce?
Un componente de input ubicado al pie del chat con:

- Textarea auto-expandible.
- Botón **+ Archivo**.
- Botón **+ Knowledge**.
- Botones de **@mención** de agentes (`@cotizador`, `@stock_curator`, etc.).
- Selector de **modo Económico / Balanceado / Calidad**.
- Botón **Enviar**.

#### ¿Cómo funciona?
- Al escribir `@` se dispara un autocomplete con agentes disponibles.
- Cada agente pertenece a una de 4 categorías: Canal, Recurso, Cognitivo, Proceso.
- El switch on/off global de agentes (panel lateral / tab Agentes) controla si pueden ser invocados.
- **REST:**
  - `POST /api/v1/agents/{agent_name}/chat` — enviar mensaje.
  - `POST /api/v1/feed/{item_id}/dispatch` — asignar a agente.
  - File upload: **no hay endpoints en `SPEC_FB_INTEGRATION_LAYER_v1`** (marcado como pendiente).
- **WebSocket:** no hay evento específico de "stream de respuesta"; el spec solo habla de mensajes server→client como `draft.ready_for_signature` y `agent.alarma`.

#### ¿Cómo se relaciona?
- Con **Workspace/SpaceLoom**: es el input principal del chat.
- Con **Mesa Zona 4**: permite iterar con `@mail_X` sobre correos del inbox.
- Con **Tab Agentes/Skills**: click en una card de agente inserta `@mención` en el composer.
- Con **Contexto activo**: el composer muestra el contexto que la IA está usando.

#### ¿Qué endpoints o contratos faltan?
- **File upload endpoints**: `SPEC_FB_INTEGRATION_LAYER_v1` §11 lista "File upload endpoints (PDF cotización · doc técnico) → diferido SPEC implementación". Bloquea adjuntos.
- **Parser de @mención**: no hay schema de cómo se serializa una mención en el mensaje (ej. `{type:'mention',agent_id:'cotizador'}` vs texto plano `@cotizador`).
- **Autocomplete de agentes**: endpoint `GET /api/v1/agents` existe, pero no hay parámetro de búsqueda/filtro por categoría para autocomplete.
- **Modo Económico/Balanceado/Calidad**: no está reflejado en el body de `POST /api/v1/agents/{name}/chat` ni en el routing de presets (`SPEC_FB_ROUTING_PRESETS_v1`).
- **Streaming de respuesta**: no está definido si el chat usa SSE, WS o REST polling.

---

### 3.5 Tab Aprendizaje

**Fuente de verdad:** `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1.md` §v1.10 (Aprendizaje accionable); `ENT_FB_USER_LEARNING_MODEL_v1.md`; `SPEC_FB_INTEGRATION_LAYER_v1.md` §4.5.

#### ¿Por qué existe?
Permite al usuario revisar, aprobar, activar o descartar los **patterns candidatos** detectados por el sistema a partir de sus acciones (edits, aprobaciones, rechazos). Es el loop de aprendizaje personal (L2) antes de promoción a L3 por comité.

#### ¿Qué produce?
Un tab en el panel derecho del Workspace con:

- Visualizador de aprendizaje (score 0-100, breakdown por pillar).
- Lista de candidates:
  - **Golden samples**: botón "Aprobar y guardar".
  - **Reglas**: botón "Activar" (abre permission preview Owner), "Mantener candidate", "Descartar".
- Card final "Producción · sin cambios".
- Patrones repetitivos como chips debajo del composer.

#### ¿Cómo funciona?
- **REST:**
  - `GET /api/v1/learning/patterns` — candidates.
  - `GET /api/v1/learning/patterns/{pid}` — detalle.
  - `POST /api/v1/learning/patterns/{pid}/apply`
  - `POST /api/v1/learning/patterns/{pid}/edit_apply`
  - `POST /api/v1/learning/patterns/{pid}/ignore`
  - `GET /api/v1/learning/applied`
  - `POST /api/v1/learning/applied/{pid}/rollback`
- **WebSocket:** `pattern.candidate.detected`, `pattern.applied_personal`, `pattern.ignored`, `pattern.rolled_back`.
- **Query keys:** `qk.patterns`, `qk.patternsCandidate`, `qk.patternsApplied`.

#### ¿Cómo se relaciona?
- Con **Composer**: los "patrones repetitivos" aparecen como chips debajo del input.
- Con **Mesa**: el panel lateral muestra "Aprendizaje en curso" trending up.
- Con **Committee (E3+)**: candidates que cumplen k-anon ≥5 pasan a cola del comité.
- Con **Gold loop**: cada draft aprobado sin edits es un golden candidate.

#### ¿Qué endpoints o contratos faltan?
- **Algoritmo de detección de patterns**: `ENT_FB_USER_LEARNING_MODEL_v1.md` §216 lo deja diferido a "SPEC implementación".
- **Schema del score 78/100**: no hay definición de cómo se calcula el indicador visual.
- **Permiso preview antes de activar**: se menciona "abre permission preview Owner" pero no hay endpoint ni UI definida.
- **Visualizador de breakdown por pillar**: no hay especificación de los pillars ni cómo se renderizan.

---

### 3.6 Contexto activo

**Fuente de verdad:** `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1.md` §v1.10 (Contexto activo + drawer "Con qué está trabajando la IA"); `POL_FABERLOOM_SURFACE_CONTRACT.md` §3.3 (Context Controls).

#### ¿Por qué existe?
Da **visibilidad y confianza** sobre qué está usando la IA para generar una respuesta. Reduce alucinaciones al mostrar fuentes, freshness y presupuesto de tokens.

#### ¿Qué produce?
- **Panel compacto** de 5 líneas: Knowledge · Caso · Archivos · Freshness · Tokens.
- Botón "Ver contexto completo" que abre un drawer con 6 secciones:
  1. Resumen (ej: "18.4k → 5.8k = 68% ahorro").
  2. Knowledge activo.
  3. Caso/archivos.
  4. Memoria permitida.
  5. Contexto NO incluido.
  6. Agentes que pueden usar contexto.
  7. Botones "Ver todo en KB · Agregar/Excluir fuente".

#### ¿Cómo funciona?
- Se alimenta del `context_pack` que cada surface declara al shell (`POL_FABERLOOM_SURFACE_CONTRACT.md` §4.3).
- **REST:**
  - `GET /api/v1/tenant` — config del tenant.
  - `GET /api/v1/agents/{agent_name}` — estado del agente.
  - Endpoints de documentos/KB para mostrar fuentes.
- **WebSocket:** `agent.config.updated`, `freshness.violation`, `cost.threshold`.
- **UI-state:** Zustand guarda `contextPack`, fuentes activas, KB global on/off.

#### ¿Cómo se relaciona?
- Con **Composer**: el usuario decide mencionar o no agentes/fuentes sabiendo qué hay en contexto.
- Con **Context Controls del shell**: KB Global ON/OFF, scope, participantes.
- Con **Knowledge Base**: permite agregar/excluir fuentes.
- Con **ContextualClock**: click abre Aprendizaje drawer.

#### ¿Qué endpoints o contratos faltan?
- **Endpoint de resumen de contexto**: no existe `GET /api/v1/context` ni similar que devuelva el resumen compacto de 5 líneas.
- **Schema de context_pack**: `POL_FABERLOOM_SURFACE_CONTRACT.md` §4.3 propone estructura mínima pero hay open questions (OQ1) sobre tamaño máximo serializable y truncamiento.
- **Cálculo de tokens/freshness**: no está definido cómo se computa "18.4k → 5.8k = 68% ahorro" ni el freshness por fuente.
- **Drawer de contexto completo**: no hay mock ni spec detallado de las 6 secciones.

---

### 3.7 Zona 5 · Automatizaciones

**Fuente de verdad:** `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1.md` §8.1; `SPEC_SPACELOOM_ETAPA1_v1.md` §4.2 (Routine Hub).

#### ¿Por qué existe?
Permite ver y controlar los **triggers, crons y reglas activas** que ejecutan rutinas sin intervención manual. Es la cara operativa del Routine Hub / automatizaciones futuras creadas en Workspace modo Automatización.

#### ¿Qué produce?
Una lista plegada en Mesa con:

- Nombre de la automatización/rutina.
- Trigger (manual / cron / al-llegar-correo).
- Estado activo/pausado.
- Acción inline: pausar / reactivar.
- Posiblemente contador de ejecuciones/última ejecución.

#### ¿Cómo funciona?
- Según `SPEC_SPACELOOM_ETAPA1_v1`, una **Rutina** = SKILL.md + binding (preset/modelo) + trigger + persona opcional.
- Se invoca con `@nombre` en el chat o por trigger.
- En E1 (SpaceLoom Etapa 1) vive en el Routine Hub del workspace.

#### ¿Cómo se relaciona?
- Con **Workspace modo Automatización**: es donde se crean/modifican las automatizaciones.
- Con **Agentes on/off**: una rutina desactivada no debe ejecutarse ni ser invocable.
- Con **Mesa Zona 4**: las automatizaciones pueden actuar sobre correos entrantes.

#### ¿Qué endpoints o contratos faltan?
- **Endpoints REST**: `SPEC_FB_INTEGRATION_LAYER_v1.md` no incluye `/api/v1/automations`. Se requieren al menos:
  - `GET /api/v1/automations`
  - `POST /api/v1/automations`
  - `PATCH /api/v1/automations/{id}` (enable/disable)
  - `DELETE /api/v1/automations/{id}`
  - `GET /api/v1/automations/{id}/runs`
- **Eventos WebSocket**: los 28 eventos canónicos no incluyen `automation.enabled`, `automation.disabled`, `automation.triggered`, `automation.failed`.
- **Schema de trigger/cron**: no está definido el formato de `trigger_json` de la rutina.
- **SPEC de automatizaciones**: no existe un documento dedicado a automatizaciones para E1; `SPEC_SPACELOOM_ETAPA1_v1` las menciona pero no detalla la API.

---

### 3.8 SpaceLoom E1

**Fuente de verdad:** `SPEC_SPACELOOM_ETAPA1_v1.md`; `POL_FABERLOOM_SURFACE_CONTRACT.md` nota de alineación; `PLAN_DESARROLLO_FABERLOOM_v5.md` §E1a-Mail.

#### ¿Por qué existe?
Es el **canvas universal single-user local-first** de FaberLoom. Renombra a "Workspace" (chat universal) para evitar confusión con el contenedor por cliente/tema/proyecto, que sigue llamándose Workspace.

#### ¿Qué produce?
En E1:

- 1 chat.
- 1 workspace.
- Sin KB inicial (solo contexto manual según `PLAN_DESARROLLO_FABERLOOM_v5` §E1a-Mail).
- Solo modo Operar.
- App de escritorio Win/Mac (pywebview + PyInstaller + SQLite + FTS5).

#### ¿Cómo funciona?
- **Stack desktop:** FastAPI + LiteLLM + UI web servida por el motor + SQLite/FTS5.
- **REST:**
  - `GET /api/v1/agents`
  - `POST /api/v1/agents/{agent_name}/chat`
- **WebSocket:** `agent.iterate.started`, `agent.alarma`.
- **UI-state:** conversaciones recientes, conversación activa, contexto del espacio.

#### ¿Cómo se relaciona?
- Con **WorkLoom**: los drafts generados en SpaceLoom pasan a WorkLoom para HITL.
- Con **Workspaces**: SpaceLoom opera dentro de un workspace con su contexto sellado.
- Con **Routine Hub**: en Etapa 1 reemplaza a la Agent Factory; las rutinas/skills viven dentro del workspace.

#### ¿Qué endpoints o contratos faltan?
- **Definición dual web vs desktop**: `PLAN_DESARROLLO_FABERLOOM_v5` pivoteó a desktop local-first, mientras `SPEC_FB_INTEGRATION_LAYER_v1` y `SPEC_FB_FRONTEND_REALTIME_STATE_v1` asumen web/server multi-tenant. Hay que decidir si el frontend E1 se construye como web-app empacada o nativa desktop.
- **Mock E1 de SpaceLoom standalone**: no se encontró un mock específico de la app desktop single-user.
- **Endpoints de workspace scope**: no hay endpoints para crear/listar workspaces ni para herencia de contexto en la Integration Layer v1 (están en specs más antiguos/dispersos).
- **Contrato de sellado por workspace**: principio rector de Etapa 1 ("sabe-donde global / resuelve local") no tiene API definida.

---

### 3.9 Responsive

**Fuente de verdad:** `DESIGN_FABERLOOM_v1.md` §breakpoints; `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1.md` §v1.10.

#### ¿Por qué existe?
El operador debe poder aprobar drafts desde móvil en ≤45s (`PLAN_DESARROLLO_FABERLOOM_v5` §E1b gate). Además, la Mesa y el Workspace deben adaptarse a tablets y laptops.

#### ¿Qué produce?
Breakpoints canónicos:

| Breakpoint | Valor | Layout |
|------------|-------|--------|
| `sm` | 640px | Mobile single-column. Chat overlay full-screen. Sidebar drawer. |
| `md` | 768px | Tablet. Grilla 12 cols. Sidebar colapsada por defecto. |
| `lg` | 1024px | Desktop pequeño. Sidebar visible. Chat panel u overlay. |
| `xl` | 1280px | Desktop estándar. Sidebar expandida, chat panel derecho. |
| `xxl` | 1536px | Desktop amplio. Canvas con aire, paneles múltiples. |

Comportamientos específicos:

- **Mesa Kanban:** 4 cols → 2 cols → 1 col.
- **Inbox:** 2 cols → 1 col.
- **KPIs Inbox:** 5 → 3 → 2.
- **Workspace:**
  - ≥1400px: 3 columnas full.
  - 1100-1399px: sidebar izquierdo pasa a drawer toggleable con FAB.
  - <1100px: ambos paneles laterales como drawers + chat full.
  - <760px: patrones compactos.
- **FABs flotantes** (móvil): botón izquierdo abre drawer Conversaciones, botón derecho abre drawer Herramientas.

#### ¿Cómo funciona?
- CSS media queries con tokens de breakpoint.
- Zustand guarda `sidebarOpen`, `rightPanelOpen`, `activeDrawer`.
- En móvil, `MobileToolsSheet` del shell muestra max 5 slots filtrados por rol (`POL_FABERLOOM_SURFACE_CONTRACT.md` §3.8).

#### ¿Cómo se relaciona?
- Con **Mesa**: la lista priorizada y el detalle de caso deben responder.
- Con **Workspace/SpaceLoom**: el chat-first debe mantener composer accesible en móvil.
- Con **Context Dock / RightTools**: en móvil se transforman en bottom sheet.

#### ¿Qué endpoints o contratos faltan?
- **Componente Drawer/Sheet específico**: no hay spec de la implementación de drawers en Next.js/Shadcn.
- **Touch targets**: no hay guía de tamaños mínimos ni de gestos.
- **Breakpoints para WorkLoom cards**: no está definido cómo se apilan las 4 columnas en móvil ni si las acciones inline permanecen visibles.
- **Especificación de FABs**: posición, z-index, iconografía, comportamiento en scroll.

---

### 3.10 Real-time

**Fuente de verdad:** `SPEC_FB_FRONTEND_REALTIME_STATE_v1.md`; `SPEC_FB_INTEGRATION_LAYER_v1.md` §8; `SPEC_FB_EVENTING_AND_OUTBOX_v1.md`.

#### ¿Por qué existe?
Garantiza que la Mesa de Control refleje el estado real del backend sin que el usuario tenga que refrescar. Es crítico para HITL: un draft listo debe aparecer inmediatamente.

#### ¿Qué produce?
- Conexión WebSocket persistente con:
  - Subprotocol `faberloom.v1`.
  - Heartbeat 30s server→client, pong 10s client→server.
  - Reconexión exponencial (1s, 2s, 4s, 8s, 16s, max 30s).
  - Recuperación de eventos vía `last_event_id` (`?since=...`).
  - Full refresh si gap > 24h (`sync_required`).
- Mapeo de eventos a invalidación/parche de TanStack Query.
- Estados de conexión visibles: conectando, conectado, desconectado inesperado, sync_required.

#### ¿Cómo funciona?
- Hook `useFaberloomWS` abre `wss://${host}/api/v1/ws`.
- `handleEvent` actualiza query cache:
  - `feed.item.new` → patch `qk.feed`.
  - `draft.ready_for_signature` → invalidate `qk.draftsPending` + toast.
  - `agent.alarma` → invalidate `qk.agent(name)` + badge.
  - `pattern.candidate.detected` → invalidate `qk.patternsCandidate` + badge.
  - `session.invalidated` → clear cache + redirect `/login`.
  - `sync_required` → invalidate all queries.
- Query keys jerárquicos (`qk.feed`, `qk.drafts`, etc.) facilitan invalidación por prefijo.

#### ¿Cómo se relaciona?
- Con **Mesa de Control**: mantiene Z1-Z5 sincronizadas.
- Con **WorkLoom**: actualiza cards cuando cambian estados.
- Con **Tab Aprendizaje**: detecta nuevos candidates.
- Con **Contexto activo**: podría recibir `freshness.violation` y `cost.threshold`.

#### ¿Qué endpoints o contratos faltan?
- **Eventos para automatizaciones**: `automation.enabled`, `automation.disabled`, `automation.triggered`.
- **Eventos para contexto activo**: no hay evento de actualización de context pack; hoy depende de invalidación de queries existentes.
- **Conflict resolution UI**: cuando dos operadores editan el mismo draft, no hay evento ni UI (`SPEC_FB_FRONTEND_REALTIME_STATE_v1.md` §11 lo deja diferido).
- **Service Worker offline / background sync**: diferido a v2.
- **Multi-tab coordination** (BroadcastChannel): diferido a v2.

---

## 4. Hallazgos Prioritarios

### P0 — Bloquean implementación o violan principios canon

| ID | Hallazgo | Evidencia | Riesgo |
|----|----------|-----------|--------|
| P0-1 | **Tres specs obligatorios no existen** en las rutas del prompt (`SPEC_FABERLOOM_MVP.md`, `SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md`, `SPEC_FABERLOOM_AGENT_COMPOSITION_v1.md`). | `Glob` no encontró archivos; contenido disperso. | Implementación basada en interpretaciones divergentes; viola P3 SSOT/P9 spec↔impl. |
| P0-2 | **Zona 5 · Automatizaciones no tiene endpoints REST ni eventos WS definidos**. | `SPEC_FB_INTEGRATION_LAYER_v1.md` §11 lista "File upload endpoints → diferido"; tampoco hay endpoints de automations. `SPEC_FB_EVENTING_AND_OUTBOX_v1.md` no lista eventos de automatización. | Bloquea S5 (Mesa) y S7 (Workspace) si se construye Mesa unificada. |
| P0-3 | **Algoritmo de detección de los 3 modos del Workspace no está especificado**. | `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1.md` §8.5 los describe conceptualmente pero no define parser ni reglas. | El Composer no puede decidir si invocar un agente, crear un trigger o proponer un nuevo agente. |
| P0-4 | **No existen file-upload endpoints** en la capa de integración. | `SPEC_FB_INTEGRATION_LAYER_v1.md` §11. | Bloquea adjuntos en Composer, Mesa, Inbox y Contexto activo. |
| P0-5 | **Conflictos de estados en WorkLoom**: `PLAN_DESARROLLO_FABERLOOM_v5` usa `TU CRITERIO / ESPERANDO / DELEGADO / ERROR` mientras `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1` v1.7 usa `Crítico / Listo para revisar / Delegado / Error accionable`. | Ambos docs en repo. | Datos inconsistentes, query keys y filtros duplicados, confusión en UI. |

### P1 — Deben resolverse antes de cerrar E1/E2

| ID | Hallazgo | Evidencia | Riesgo |
|----|----------|-----------|--------|
| P1-1 | **No se encontró mock v6 de Mesa de Control con 5 zonas**. | `IDX_FB_FOUNDATION_BETA.md` menciona `mesa_de_control_v5.html`; no mock v6. | El equipo de UI no tiene referencia visual única para S5. |
| P1-2 | **Tab Aprendizaje carece de diseño detallado y algoritmo de detección**. | `ENT_FB_USER_LEARNING_MODEL_v1.md` §216 deja algoritmo diferido. | UI se construirá sin saber qué datos mostrar. |
| P1-3 | **Contexto activo no tiene endpoint ni schema propio**. | `POL_FABERLOOM_SURFACE_CONTRACT.md` OQ1. | Cada surface podría inventar su propio context pack. |
| P1-4 | **Responsive: faltan especificaciones de Drawer/Sheet y FABs móviles**. | `DESIGN_FABERLOOM_v1.md` define breakpoints pero no componentes móviles. | Gate de aprobación móvil ≤45s en riesgo. |
| P1-5 | **Eventos WS para reasignación/delegación de drafts no existen**. | `SPEC_FB_EVENTING_AND_OUTBOX_v1.md` lista 28 eventos; ninguno de `draft.reassigned`/`task.delegated`. | WorkLoom multi-usuario no se sincroniza correctamente. |

### P2 — Deuda técnica / documental

| ID | Hallazgo | Evidencia | Riesgo |
|----|----------|-----------|--------|
| P2-1 | `SKILL_FRONTEND_TEN_PRINCIPLES_V2.md` está en estado **SHADOW**, no VIGENTE. | Header del archivo. | La lente cognitiva frontend no es mandato formal. |
| P2-2 | `POL_FABERLOOM_SURFACE_CONTRACT.md` es **DRAFT v0.2** con naming Workspace/SpaceLoom pendiente de v0.3. | Header y OQ6. | Riesgo de drift de naming en implementación. |
| P2-3 | **Copy review checklist** para eliminar semántica multi-agente no se encontró como archivo separado. | `PLB_FB_FOUNDATION_BETA_v1.md` §6 menciona "Copy review checklist 12 ítems S5". | TIER 1 #11 (Mesa limpia de multi-agente) difícil de verificar. |
| P2-4 | **Service worker offline, background sync y multi-tab coordination** están diferidos a v2. | `SPEC_FB_FRONTEND_REALTIME_STATE_v1.md` §11. | Experiencia offline deficiente; múltiples tabs pueden desincronizarse. |
| P2-5 | **Stream de respuesta del chat** no está definido. | No hay evento WS ni endpoint SSE en `SPEC_FB_INTEGRATION_LAYER_v1.md`. | UX de chat lenta o inconsistente. |

---

## 5. Recomendaciones de próximos pasos

1. **Cerrar P0-1 a P0-5 antes de iniciar S5/S7:**
   - Producir un `SPEC_FB_AUTOMATIONS_v1.md` con endpoints, schema de trigger/cron y eventos WS.
   - Producir un `SPEC_WORKSPACE_MODES_v1.md` con el parser de detección de modo y body del chat por modo.
   - Producir un `SPEC_FB_FILE_UPLOAD_v1.md` con endpoints de upload, límites, MIME allowlist, destinos (`workspace_attachment`, `kb_candidate`, `mesa_evidence`) y progreso.
   - Canonicalizar los estados de WorkLoom en un único documento y actualizar `PLAN_DESARROLLO_FABERLOOM_v5` o `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1` con nota de supersede.

2. **Avanzar S1-S3 con lo existente:**
   - Auth (`SPEC_FB_AUTH_TENANT_RBAC_v1`), KB upload/parse (con upload HTTP genérico temporal), engine ejecutor y chat básico pueden construirse con los specs vigentes.

3. **Producir mocks faltantes:**
   - Mock v6 de Mesa de Control con 5 zonas.
   - Mock de Workspace en modo Automatización y Construcción.
   - Mock de SpaceLoom E1 desktop.

4. **Definir el contrato de contexto activo:**
   - Endpoint `GET /api/v1/context` o similar.
   - Schema TS auto-generado desde Pydantic.
   - Drawer de contexto completo con 6 secciones especificadas.

5. **Actualizar estados de documentos:**
   - Promover `SKILL_FRONTEND_TEN_PRINCIPLES_V2.md` a VIGENTE tras primera aplicación real.
   - Resolver OQ6 de `POL_FABERLOOM_SURFACE_CONTRACT.md` (Workspace vs SpaceLoom).

---

## 6. Apéndice — Mapa de eventos WebSocket a componentes

| Evento WS | Origen | Componentes afectados | Acción frontend |
|-----------|--------|----------------------|-----------------|
| `feed.item.new` | Backend/inbox | Mesa Z1-Z4 | Patch `qk.feed` |
| `feed.item.dispatched` | Backend | Mesa Z4 | Invalidate `qk.feed` |
| `feed.item.archived` | Backend | Mesa Z4 | Invalidate `qk.feed` |
| `draft.generated` | Engine | WorkLoom, Mesa Z1-Z2 | Invalidate `qk.draftsPending` |
| `draft.ready_for_signature` | Engine | WorkLoom, Mesa Z2 | Invalidate + toast |
| `draft.approved` | HITL | WorkLoom, Mesa | Invalidate `qk.drafts` |
| `draft.edited` | HITL | WorkLoom, Mesa | Invalidate `qk.draft(id)` |
| `draft.rejected` | HITL | WorkLoom, Mesa, Aprendizaje | Invalidate + capturar razón |
| `draft.sent` | Backend | WorkLoom | Invalidate + notificación |
| `agent.alarma` | Engine/agente | Mesa, Workspace | Badge alarma + invalidate `qk.agent(name)` |
| `agent.config.updated` | Admin | Contexto activo, Agent Factory | Invalidate `qk.agent(name)` |
| `agent.shadow_promote` | Curador | Mesa Z3 | Invalidate `qk.agents` |
| `pattern.candidate.detected` | Learning | Tab Aprendizaje, Mesa panel lateral | Invalidate `qk.patternsCandidate` + badge |
| `pattern.applied_personal` | Learning | Tab Aprendizaje | Invalidate `qk.patternsApplied` |
| `pattern.ignored` | Learning | Tab Aprendizaje | Invalidate candidates |
| `pattern.rolled_back` | Learning | Tab Aprendizaje | Invalidate applied |
| `freshness.violation` | KB/source | Contexto activo | Mostrar warning |
| `cost.threshold` | Monitor | Contexto activo, Dashboard | Mostrar warning/throttle |
| `session.invalidated` | Auth | Toda la app | Clear cache + redirect `/login` |
| `sync_required` | WS server | Toda la app | `qc.invalidateQueries()` + modal |
| *(faltante)* `automation.enabled/disabled/triggered` | Routine Hub | Mesa Z5 | Actualizar lista de automatizaciones |
| *(faltante)* `draft.reassigned` | HITL | WorkLoom | Mover card entre columnas |

---

**Fin del reporte.**
