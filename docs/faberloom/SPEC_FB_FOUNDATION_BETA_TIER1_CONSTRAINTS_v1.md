---
id: SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE 2026-05-02 (puente E1 ↔ E2/E3)
fecha: 2026-05-02
agente: Cowork (redaccion) + CEO (decision conceptual)
aplica_a: [FaberLoom]
implementa_puente_entre:
  - PLB_FB_FOUNDATION_BETA_v1 (plan firmado · restricciones operativas E1)
  - SCH_FB_FLOW_DAG.md v2.0 (arquitectura DAG canon · 7 nodos)
  - ENT_FB_SUB_AGENTS_LIBRARY_v1.md v1.1 (10 sub-agentes canon)
  - ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1.md (P16)
  - ENT_FB_TOOL_CATALOG_v1.md v2.0 (15 tools nativos + custom MCP)
  - SPEC_FABERLOOM_AGENT_COMPOSITION_v1.md
  - SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md
  - SPEC_ACTION_ENGINE.md
relacionado: SPEC_FB_AGENT_BUILDER_v1.md · SCH_FB_SKILL_MANIFEST_v2.md
---

# SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1

## Puente entre arquitectura canon y restricciones operativas E1

## 1. Por que existe este documento

Conflicto detectado durante construccion del mockup E1 navegable (2026-05-02): los specs canon de FaberLoom **anteriores al plan firmado** documentan capacidades arquitectonicas (sub-agents jerarquicos, tools externas, branching DAG, parallel) que el plan firmado **restringe intencionalmente para Foundation Beta E1** sin negar los specs.

Sin este documento puente:
- Equipo de implementacion no sabe que respetar primero (specs vs plan)
- Mockup UI no puede mostrar features "preparadas pero bloqueadas" sin parecer mentira
- Tareas de S3/S6 podrian construirse sin extension points · forzando rearquitectura en E2

Este SPEC mapea 1:1 cada restriccion TIER 1 con el spec canon que la implementa, declarando explicitamente que es operativo E1, que es habilitable E2/E3, y que requisitos arquitectonicos se mantienen desde dia 1.

## 2. Principio rector

> **El plan firmado restringe el deploy. Los specs definen la arquitectura. Construir como si E2 viniera manana — desplegar bajo restricciones E1.**

Esto significa:
- Schemas DB se construyen con campos para soportar E2 (ej. `parent_run_id`, `branch_id`, `tool_whitelist[]`) aunque queden vacios/null en E1
- Engine se disena como **task graph** que en E1 solo permite ciertos patterns · `feature_flag tenant_id → ALLOW_X` controla cada capacidad
- UI muestra capacidades E2 como visibles pero disabled · con tooltip referenciando el spec canon que las define
- Code respeta extension points · S3/S6 entregan codigo donde habilitar E2 = cambiar config, no rearquitectura

## 3. Mapa de restricciones TIER 1 ↔ Specs canon

### 3.1 TIER 1 #15 · "Single-agent por task · cadena LINEAL · NO sub-agentes · NO orquestacion entre agentes"

| Aspecto | Spec canon que lo documenta | Status E1 | Status E2/E3 |
|---|---|---|---|
| **Cadena lineal de skills** | `SCH_FB_FLOW_DAG.md` v2.0 nodo `skill_call` | OPERATIVO | OPERATIVO |
| **Branching condicional dentro del flow** | `SCH_FB_FLOW_DAG.md` nodo `branch` con `conditions[]` exhaustivas | OPERATIVO (NO multi-agente) | OPERATIVO |
| **Parallel fork-join** | `SCH_FB_FLOW_DAG.md` nodo `parallel` (≤4 ramas) | OPERATIVO | OPERATIVO + extension a >4 |
| **Human gate (HITL pause)** | `SCH_FB_FLOW_DAG.md` nodo `human_gate` con `timeout_h` obligatorio | OPERATIVO | OPERATIVO |
| **Notify side-effect** | `SCH_FB_FLOW_DAG.md` nodo `notify` | OPERATIVO | OPERATIVO |
| **Terminal materializa outputs** | `SCH_FB_FLOW_DAG.md` nodo `terminal` con `outputs_emit[]` | OPERATIVO | OPERATIVO |
| **Config resolver multi-tenant** | `SCH_FB_FLOW_DAG.md` nodo `config_resolver` (D17) | OPERATIVO (pieza clave multi-tenant) | OPERATIVO |
| **Sub-agentes individuales (10 atomicos)** | `ENT_FB_SUB_AGENTS_LIBRARY_v1.md` catalogo 10 (EMAIL_CLASSIFIER, DRAFT_WRITER, PROFORMA_BUILDER, SAP_QUERY, VOICE_TRANSCRIBER, PRE_CALL_SUMMARIZER, COMPLIANCE_CHECKER, ESCALATION_ROUTER, PRICING_CALCULATOR, INVENTORY_FETCHER) | **OPERATIVO como agentes standalone** · cada uno invocable individualmente | + composables jerarquicamente |
| **Composicion jerarquica AG_AM_X → [AG_SUB_*]** | `ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1.md` (P16) + ejemplo AG_AM_MARLUVAS con 9 de 10 sub-agentes | **BLOQUEADO E1** · single-agent por task | HABILITABLE E2 con `feature_flag.allow_agent_composition=true` |
| **Sub-agente invocando sub-agente** | NO documentado · prohibido por P16 (max 2 niveles) | BLOQUEADO | BLOQUEADO permanentemente (NeurIPS 2025 MAST 41-86.7% fallo) |
| **Orquestacion cross-agent (un agente llama otro)** | NO documentado | BLOQUEADO | EVALUABLE E3+ con governance Comite |

**Implementacion arquitectonica E1:**
- Tabla `agent_runs` con `parent_run_id` nullable · permite registrar composicion en E2 sin migracion
- `agent_compositions` table preparada · vacia en E1
- Engine ejecutor (S3) implementa todos los 7 tipos de nodo del DAG · solo `human_gate` + `terminal` + linear `skill_call` + `branch` (intra-agente) + `parallel` (intra-agente) + `notify` + `config_resolver` activos en E1
- Composicion jerarquica = config en `agent.composition_mode` · null en E1, `hierarchical` en E2

### 3.2 TIER 1 #16 · "14 limites Skill Factory · NO tools externas · NO HTTP en runtime · NO ejecucion de codigo"

| Aspecto | Spec canon que lo documenta | Status E1 | Status E2/E3 |
|---|---|---|---|
| **15 tools nativos con MCP wrapper** | `ENT_FB_TOOL_CATALOG_v1.md` v2.0 (amazon_sp_api_*, helium10_*, gmail_*, gdrive_*, slack_*, crm_marluvas_portal, sap_b1_distribution, web_search, web_fetch) | **BLOQUEADOS en runtime de skill** · wrappers existen como modulos pero no llamables desde skill prompt | HABILITABLES E2 con `tools_mcp[]` declarado en agent manifest + sandbox de red + permission whitelist per tenant |
| **Custom MCP slot** | `ENT_FB_TOOL_CATALOG_v1.md` D16 (registrar MCP server custom) | BLOQUEADO E1 | HABILITABLE E2 |
| **n8n como conector pre-agente** | `ENT_FB_TOOL_CATALOG_v1.md` reglas D16 (≤5 nodes, sin LLM, output a Django builder) | OPERATIVO en E1 (n8n vive antes del agente, NO en runtime de skill) | OPERATIVO |
| **Skill puede tener prompt template** | `SCH_FB_SKILL_MANIFEST_v2.md` | OPERATIVO | OPERATIVO |
| **Skill puede llamar otro skill (composicion)** | NO documentado · prohibido por TIER 1 #16-13 (skill atomica) | BLOQUEADO | BLOQUEADO permanentemente |
| **Cost cap + timeout per skill** | TIER 1 #16-11 + #16-12 (default 30s/$0.50, max 60s/$2) | OPERATIVO | OPERATIVO |
| **Sandbox antes de promote a PROD** | TIER 1 #16-9 + #16-10 (Owner/Admin only) | OPERATIVO | OPERATIVO |

**Implementacion arquitectonica E1:**
- Tabla `skills` con campo `tool_whitelist[]` array · vacio en E1 · permite habilitar tools per-skill en E2
- Engine de skills implementa modelo de "tool injection" en runtime · feature flag `ALLOW_TOOLS_IN_SKILLS=false` en E1
- MCP wrappers en `mwt-knowledge/tools/<tool_id>.py` existen pero solo invocables desde fuera del runtime de skill (ej. desde nodo de flow `skill_call` que pasa data ya fetched · no desde el prompt directamente)
- Custom MCP slot: schema en DB preparado, UI muestra como `disabled with tooltip`

### 3.3 TIER 1 #2 · "HITL absoluto · NO auto-send"

| Aspecto | Spec canon | Status E1 | Status E2/E3 |
|---|---|---|---|
| **Human gate obligatorio antes de envio cliente** | `SCH_FB_FLOW_DAG.md` nodo `human_gate` + `ARCH_AGENT_PRINCIPLES` P3 (draft-first absoluto) | OPERATIVO PERMANENTE | OPERATIVO PERMANENTE |
| **Auto-send selectivo (low-risk + alta confianza)** | NO documentado · contradiria P3 | BLOQUEADO | EVALUABLE E3 con governance Comite + telemetria 90d minimo |

HITL absoluto es restriccion **permanente** — no es "para E1". Foundation Beta lo eleva a TIER 1 #2 explicito porque el wedge B2B con responsabilidad legal lo requiere. Cualquier propuesta de habilitar auto-send en E3+ requiere MANIFIESTO_APPEND con firma CEO + auditoria externa + 90d telemetria de drafts probada.

## 4. Que se construye en cada sprint con extension points

### S1A core boot
- Schemas DB con campos preparados para E2:
  - `agent_runs.parent_run_id` nullable
  - `agent_runs.composition_mode` enum (null|hierarchical) default null
  - `skill_executions.tool_invocations[]` JSONB (vacio en E1)
  - `skill_executions.parent_skill_id` nullable

### S3 engine ejecutor
- Implementar runtime de los 7 tipos de nodo del DAG · todos activos en E1
- Feature flags per-tenant en tabla `tenant_features`:
  - `allow_agent_composition` default false
  - `allow_tools_in_skills` default false
  - `allow_custom_mcp` default false
  - `allow_parallel_branches_max` default 4
- Engine valida `feature_flags` antes de permitir cada operacion

### S6 Skill Factory + Agent Factory
- UI muestra los 10 sub-agentes canon como `installable as standalone agent`
- UI muestra los 15 tools canon como `disabled with tooltip "TIER 1 #16-2 · habilitable E2"`
- Catalogo Custom MCP slot visible en builder · disabled en E1
- Composer del agent permite seleccionar `archetype: workflow|routine|supervisor` pero `supervisor` esta disabled E1 con tooltip

## 5. Que tiene que mostrar el mockup UI

### 5.1 Pantalla "Flujos · DAG"
- Renderiza el DAG canon de un agente con los 7 tipos de nodo visibles y diferenciados por color
- Selector de flow (cotizador / licitaciones / seguidor) para mostrar variedad de archetypes
- Sidebar con metadata (entry, max_depth, fail_policy) + leyenda de los 7 nodos + limitaciones v1
- Boton "Iterar flow" abre chat con @flow_designer (capacidad simulada)

### 5.2 Agent Factory · seccion "Catalogo Sub-agentes"
- Renderiza los 10 sub-agentes del `ENT_FB_SUB_AGENTS_LIBRARY_v1.md` con metadata (modelo, latency, cost, pool L3)
- Card AG_SUB_DRAFT_WRITER marcada "ALTA PRIORIDAD" (alimentacion pool L3)
- Boton de instalacion como agente standalone (E1) en cada card
- Banner inferior: "Composicion jerarquica · disponible E2" referenciando ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1

### 5.3 Skill Factory · seccion "Catalogo Tools"
- Renderiza los 15 tools del `ENT_FB_TOOL_CATALOG_v1.md` v2.0 + custom MCP slot
- Todos visualmente disabled con badge "E2"
- Click abre modal con detalle (categoria, permission, status BLOQUEADO TIER 1 #16-2, ruta del MCP wrapper, condiciones para habilitar E2)
- Tabla "Distincion Tools vs Skills vs Files" del spec D18

## 6. Validacion del puente

Este SPEC se valida si:
1. Construir el mockup E1 NO requiere modificar ningun spec canon pre-existente
2. Construir el mockup E1 NO requiere MANIFIESTO_APPEND nuevo (porque no contradice plan firmado · solo lo explica)
3. Habilitar una capacidad E2 (ej. composicion jerarquica) requiere SOLO cambiar `tenant_features.allow_agent_composition = true` · NO rearquitecturar
4. Auditor externo (ChatGPT R3 / Kimi) leyendo este SPEC puede verificar coherencia entre plan firmado + specs canon en una sola pasada

## 7. No hace falta MANIFIESTO_APPEND

Los specs canon (SCH_FB_FLOW_DAG, ENT_FB_SUB_AGENTS_LIBRARY, ENT_FB_TOOL_CATALOG, ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE) son **pre-existentes** al plan firmado (29-30 abril vs 1 mayo). El plan firmado los **restringe selectivamente para E1**, no los **reemplaza**.

Por tanto este SPEC es **un puente documental**, no una decision arquitectonica nueva. No requiere firma CEO formal · solo confirmacion de que la lectura es correcta.

Si en el futuro se decide habilitar capacidades E2 antes de Foundation Beta cerrar (ej. composicion jerarquica de sub-agentes), eso SI requeriria MANIFIESTO_APPEND con firma CEO porque cambiaria el scope del plan firmado.

## 8. Mesa de Control unificada · superficie operativa unica (v1.1)

Tras iteracion con CEO el 2026-05-02 sobre el mockup E1 navegable, se confirma decision arquitectonica UX:

**La Mesa de Control absorbe TODA la operacion diaria como superficie unica.** Reemplaza la separacion previa entre "Mesa" + "Inbox RFQs" + "Flujos" + "Status agentes". Razon: reducir carga cognitiva del operador (CEO o miembro del tenant) que pasa el dia entero ahi.

### 8.1 Modelo de 5 zonas plegables + 2 paneles laterales

| Zona | Contenido | Estado default |
|---|---|---|
| Zona 1 · Lo urgente | Hero con drafts en alarma o alta prioridad · 3 acciones explicitas (Aprobar/Iterar/Descartar) | Expandida |
| Zona 2 · Esperando tu firma | Lista compacta de drafts listos para HITL · acciones rapidas inline | Expandida |
| Zona 3 · SANDBOX esperando promote | Agentes/skills nuevos creados via Workspace conversacional · awaiting CEO promote | Expandida si hay items |
| Zona 4 · Inbox completo | TODO lo entrante (auto-resueltos, spam, ruteados, pendientes) con filtros + iteracion con @mail_X | Plegada |
| Zona 5 · Automatizaciones activas | Lista de triggers + crons + reglas activas · pausar/reactivar inline | Plegada |

**Panel lateral izq (siempre visible):**
- **Agentes on/off** con switches reales · invocables con `@` desde cualquier composer
- **Aprendizaje en curso** · trending up de mejoras (acceptance, patterns spam, pool L3) con razon ("gracias a tus 23 ediciones")
- **Cuenta en foco** · contexto de la cuenta operada actualmente

### 8.2 Distincion Mesa vs Workspace (v1.2 actualizado)

Esto cierra el modelo: dos pantallas operativas con propositos distintos pero complementarios. **Decision adicional 2026-05-02 iteracion final:** los toggles on/off de agentes + el panel de aprendizaje en curso viven en el **Workspace** como hero (no en Mesa). Razon: representan el ESTADO DEL SISTEMA, no el TRABAJO operativo. Mesa queda solo con items que requieren atencion (full width sin panel lateral).

| Mesa de Control | Workspace |
|---|---|
| **TRABAJO** del dia a dia (que tengo que hacer YO) | **SISTEMA** vivo + construccion (como esta MI MAQUINA) |
| Que requiere mi atencion ahora | Estado de agentes + aprendizaje + chat constructor |
| Aprobar/Iterar/Descartar items existentes | Switch on/off agentes (canal/recurso/cognitivo/proceso) |
| Ver inbox completo + sugerencias inline | Ver aprendizaje en curso (que mejora gracias a mis acciones) |
| Sandbox pending promote (decision rapida) | Definir automatizaciones nuevas / crear agentes via chat |
| **Layout: 5 zonas plegables full-width** | **Layout A (stack vertical): hero agentes + hero aprendizaje + chat con rails abajo** |

### 8.3 Sidebar nav reducido a 9 items (v1.1)

Tras absorcion en Mesa unificada:

**Operacion (uso diario):**
1. Mesa de Control
2. Workspace · construir

**Editores granulares (cuando hace falta):**
3. Agent Factory
4. Skill Factory
5. Knowledge Base
6. Voice Profile
7. Dashboard KPIs

**Admin / governance:**
8. Audit log
9. Usuarios y roles + Settings tenant (colapsado)

**Eliminados del sidebar (siguen accesibles via go() desde links internos):**
- "Inbox RFQs" → absorbido en Mesa Zona 4 con filtro
- "Flujos · DAG" → vive como tab dentro de cada agente (segun spec SCH_FB_FLOW_DAG)
- "Editor cotizacion" → output de @cotizador, accesible via Mesa Zona 1/2

### 8.4 Modelo "todo es agente" + invocacion uniforme

Tras iteracion CEO 2026-05-02, se confirma principio rector adicional:

**Todo recurso operable es un agente** (no Settings con secciones separadas). 4 categorias bajo el mismo modelo:

| Categoria | Que hace | Ejemplos |
|---|---|---|
| **Canal** | Recibe/envia y responde queries sobre su canal | `@mail_alvaro` · `@mail_ventas` · `@wa_+506_8888` · `@slack_mwt` |
| **Recurso** | Consultable como base de datos viva | `@kb_marluvas` · `@sap_marluvas` · `@drive_proyectos` · `@web_research` |
| **Cognitivo** | LLM-intensivo, produce outputs | `@cotizador_marluvas` · `@licitaciones_cfe` · `@redactor_es_neutro` |
| **Proceso** | Cron / reactivo / housekeeping | `@seguidor` · `@kb_audit` · `@stock_refresh` · `@margin_drift` |

**Invocacion uniforme:** desde cualquier composer (Workspace, Mesa, drawers) con `@` mention. El sistema infiere capacidades del agente segun categoria.

**Switch on/off** (panel lateral Mesa) controla disponibilidad: OFF pausa triggers automaticos Y bloquea invocacion `@`. Eliminacion del agente requiere ir a Agent Factory (decision mas fuerte).

### 8.5 Workspace como constructor self-extending

Tras iteracion CEO 2026-05-02, se confirma capacidad rectora:

**El Workspace permite definir automatizaciones futuras y crear agentes nuevos conversando.** 3 modos de iteracion en el mismo chat:

1. **Operacional · presente** ("@mail_alvaro buscá X, después @cotizador armá Y") — encadena agentes existentes ahora
2. **Automatizacion · futuro** ("Cuando llegue correo así, hacé esto") — crea/modifica trigger + flow
3. **Construccion · capacidad nueva** — sistema detecta gap → propone crear agente nuevo heredando del catalogo canon → SANDBOX → CEO promote desde Mesa Zona 3

**Restricciones TIER 1 que esto respeta:**
- HITL absoluto: ninguna creacion va a PROD sin firma CEO
- Single-agent por task: agentes nuevos son atomicos (no componen otros)
- Sandbox antes de promote: TIER 1 #16-9
- Promote solo Owner/Admin: TIER 1 #16-10
- Audit log append-only: cada creacion queda registrada con `actor_role_at_decision`

### 8.6 Implicaciones para implementacion E1

Sin requerir nuevo MANIFIESTO_APPEND ni ampliar plan firmado:

| Sprint | Implementacion |
|---|---|
| S1A | Schemas `agents` + `agent_runs` + `automations` con campos para soportar 4 categorias · feature_flags per-tenant |
| S3 | Engine ejecutor implementa los 7 tipos de nodo del DAG canon (todos activos E1) · `feature_flags` controla composicion jerarquica (E2) |
| S5 | Mesa de Control con 5 zonas plegables + panel lateral · UI de invocacion `@` universal |
| S6 | Agent Factory + Skill Factory con catalogos canon (sub-agents library + tool catalog) visibles · capacidades E2 disabled con tooltip |
| S7 | Workspace conversacional con 3 modos detectados automaticamente · trazabilidad de propuestas a SANDBOX |

## Changelog
- 2026-05-02 v1.10 VIGENTE: **Responsive + aprendizaje accionable + toggles por consulta**. Cierre de huecos UX detectados:
  - **Responsive** · breakpoints canon: ≥1400px Workspace 3 cols full · 1100-1399px sidebar izq pasa a drawer toggleable con FAB · <1100px ambos paneles laterales como drawers + chat full · <760px patrones compactos. Mesa Kanban: 4 cols → 2 cols → 1 col. Inbox: 2 cols → 1 col. KPIs Inbox: 5 → 3 → 2. Detalle correo y workspace contextual también responden.
  - **Aprendizaje accionable** en tab Aprendizaje · cada candidate (golden + reglas) muestra botones reales: ✓ Aprobar y guardar (golden) · ✓ Activar (reglas, abre permission preview Owner) · ⏸ Mantener candidate · ✕ Descartar. Chip "golden candidate" en patrones repetitivos lleva al tab. Card final "Producción · sin cambios" reafirma seguridad.
  - **Toggles por consulta** en tab Agentes y Skills · cada card tiene mini-switch ON/OFF arriba derecha que cambia disponibilidad SOLO para esta tarea · microcopy explícito "default global vive en sidebar global o Agent Factory". Card explicativa al final de cada tab clarifica las 3 capas: tab (consulta) · sidebar global (permanente) · Factory (arquitectura).
  - **FABs flotantes** (móvil/responsive): botón izq abre drawer Conversaciones (con badge contador) · botón der abre drawer Herramientas
- 2026-05-02 v1.9 VIGENTE: **Workspace v3 · chat-first · 3 columnas · sin hero ni tarjetas centrales**. Aplicacion del brief CEO "Programar Pantalla 3: Workspace FaberLoom":
  - **Layout 3 columnas**: izquierda con conversaciones recientes (5 ejemplos clickeables · botón "+ Nueva conversación") · centro con chat-first (minibar compacto + welcome simple + stream + composer fijo abajo + patrones repetitivos) · derecha con tabs Agentes/Skills/Aprendizaje + contexto activo abajo
  - **Centro chat-first**: NO hay hero grande · NO tarjetas centrales tipo "Cotizar desde texto" · solo welcome compacto "FaberLoom · listo · estoy trabajando con el contexto activo · escribí directo o mencioná @agente"
  - **Composer foco** con + Archivo · + Knowledge · @cotizador · @stock_curator · Modo Balanceado · Enviar
  - **Agentes por @mención**: click en agente del panel der inserta @mención en composer (no abre Agent Studio · no cambia pantalla) · toast "@cotizador añadido a esta consulta. Sólo aplica a esta tarea"
  - **Sidebar derecha · Herramientas** con 3 tabs: Agentes (4 cards: @cotizador ACTIVE · @stock_curator SANDBOX · @digest ACTIVE · @licitaciones SANDBOX) · Skills (4 cards: buscar_kb_producto SEALED · validar_precio_rapido SEALED · crear_regla_inbox CUSTOM · extraer_productos SEALED) · Aprendizaje visualizador (78/100 + 1 golden + 2 reglas + producción sin cambios)
  - **Contexto activo abajo** del panel der · compacto · 5 líneas (Knowledge · Caso · Archivos · Freshness · Tokens) + botón "Ver contexto completo" que abre drawer
  - **Drawer "Con qué está trabajando la IA"** con 6 secciones: Resumen (18.4k → 5.8k = 68% ahorro) · Knowledge activo · Caso/archivos · Memoria permitida · Contexto NO incluido · Agentes que pueden usar contexto · botones "Ver todo en KB · Agregar/Excluir fuente"
  - **Patrones repetitivos debajo del composer** (no en centro) · 4 chips (Stock parcial→lotes · Cliente Gold→override · RFQ con SKU→@cotizador · Draft aprobado sin edits→golden candidate)
  
  **Frase guía incorporada**: "Workspace es el chat. Knowledge es el cerebro. Agentes son herramientas. Skills son capacidades. Contexto activo da confianza. Aprendizaje observa. HITL protege."
  
  **Lo eliminado**: hero "Aprendizaje en curso" (pasó a tab Aprendizaje del panel der) · ws-thread-chips (innecesario) · ws-grid viejo con termómetro/KB-activable (reemplazado por contexto activo compacto + drawer) · botones header "Archivar / Golden Sample / Convertir en agente" (no caben en chat-first puro · accesibles via patrones repetitivos como "Draft aprobado sin edits → golden candidate")
- 2026-05-02 v1.8 VIGENTE: **Inbox v2 · lista priorizada · 5 acciones · workspace contextual · reglas candidate**. Aplicacion del brief CEO "Programar Pantalla 2: Inbox FaberLoom":
  - **Lista priorizada (no Kanban)** con orden "prioridad aprendida + SLA + historial"
  - **5 acciones por correo** segun tipo: Resolver (RFQ/follow-up/consulta) · Leer y ocultar (newsletter/logist) · Mandar a resumen (publicidad con cupon/newsletter operativa) · Borrar futuros (spam) · Asignar agente (recurrente operacional util)
  - **10 cards de ejemplo** con tipos diversos (RFQ con SKU+cliente conocido / RFQ cliente nuevo / follow-up / consulta tecnica / recurrente operacional / publi con cupon BILL20 / newsletter operativa / newsletter generica 4ta semana / spam recurrente proveedor falso / notificacion logistica)
  - **KPIs canon Inbox**: Accionables · Resumen diario · Ocultos leidos · Auto-borrar · SLA proximo
  - **Vista detalle del correo** full-width al click · 3 tabs: Ver correo (default) · Solucion propuesta · Workspace contextual
  - **Solucion propuesta por tipo** con plan numerado (RFQ accionable: 5 pasos canon · publicidad cupon: agregar a digest con highlight · newsletter generica: marcar leido + no traer · spam recurrente: trash candidate + aprobacion · recurrente util: asignar agente + ensenar patron)
  - **Workspace contextual dentro del correo** (no separado): conversacion + composer + skills directas sugeridas (clasificar_correo · crear_pendiente · extraer_productos · crear_regla_inbox) + regla candidate visible + servidor afectado
  - **Reglas candidate** con 6 tipos canon (readhide / summary_digest / trash_future / assign_agent / send_to_workspace / send_to_mesa) · todas requieren aprobacion Owner/Admin antes de afectar servidor o produccion · audit log
  - **Acciones de servidor visibles**: Marcar leido (Gmail/server) · No traer (suppression rule) · Borrar futuros (trash rule) · Resumen diario (digest list)
  - **Panel der canon**: Resumen diario en construccion (promos con valor + newsletters operativas + publicidad sin valor + highlights) · Reglas aprendidas recientes · Acciones de servidor con scope
  
  **Frase guia incorporada**: "Inbox aprende a limpiar la entrada. Lo urgente se resuelve. Lo repetitivo se ensena. Lo irrelevante se oculta. Lo util pero no urgente se resume. Lo cliente-facing siempre pasa por HITL."
- 2026-05-02 v1.7 VIGENTE: **Mesa Kanban + Detalle + Workspace contextual + subagentes visibles E1**. Aplicacion del brief CEO completo "Programar Pantalla 1: Mesa de Control FaberLoom":
  - **Mesa nivel 1 · Kanban** con 4 columnas: Critico · Listo para revisar · Delegado · Error accionable. Cards accionables con tipo+cliente+canal+ruta+confidence+costo+SLA+responsable+proxima accion+accion primaria contextual ("Resolver override" / "Revisar y aprobar" / "Abrir Workspace" / "Actualizar fuente" / "Elegir plantilla")
  - **Mesa nivel 2 · Detalle del caso** full-width al click en card · hero + meta (tipo/origen/ruta/HITL/trace) · 3 tabs: Ver solucion (default · solucion propuesta + evidence + validaciones + audit) · Editar (contenteditable + diff + razon edicion) · Workspace (workspace contextual completo)
  - **Mesa nivel 3 · Workspace contextual dentro del caso** (no es pantalla separada): conversacion + composer + adjuntar/KB/evidence + modo Economico/Balanceado/Calidad + ejecutar + HITL obligatorio. Panel derecho con jerarquia completa del agente (ver siguiente bullet)
  - **Subagentes vuelven visibles en Mesa con Context Policy** (revierte limpieza UX de v1.5 sin tocar arquitectura · sigue respetando TIER 1 #15: subagentes son componentes internos del agente principal · NO multi-agent orquestado entre agentes principales). Panel derecho del Workspace contextual muestra: Agente activo · Routing interno (skills directas vs subagentes) · Skills directas de @cotizador (clasificar_rfq/validar_precio_rapido/generar_respuesta_simple) · Mini mapa de jerarquia · Subagentes activos con Context Policy (que recibe / que NO recibe / token cap / output contract / origen) · Context Budget con ahorro tokens · Nivel aprendizaje · Captura de conocimiento (golden/regla/voice/KB) al final
  - **Pills SEALED/OPEN/CUSTOM/overlay tenant** introducidas para distinguir templates base (no editables) de overlays tenant (editables) y skills/agentes custom (100% editables)
  - **Pantalla Iterar separada eliminada del sidebar** · su lugar lo toma el Workspace contextual dentro del caso de Mesa (sigue accesible programaticamente para deep-links)
  - **Frase guia incorporada en Mesa hero**: "Inbox recibe · Mesa prioriza · Workspace opera · Agentes coordinan · Skills ejecutan · HITL aprueba"
  
  **Reconciliacion con specs canon:** Esto NO viola TIER 1 #15. El plan firmado prohibe orquestacion entre agentes principales (multi-agent orchestration). Los subagentes documentados en `ENT_FB_SUB_AGENTS_LIBRARY_v1` son componentes internos del agente principal · cada task ejecuta UN agente principal · ese agente decide internamente si usa skill directa o activa subagente. Compatible con `SCH_FB_FLOW_DAG.md` que ya contemplaba composicion jerarquica con max 2 niveles. La revisita UX en v1.7 expone esta arquitectura al usuario · v1.5 la habia ocultado por simplicidad pero generaba modelo mental incompleto.
  
  **Criterio de aprobacion final** (10 segundos por perfil):
  - Operator entra a Mesa: ve Kanban · entiende que tiene critico vs listo para revisar · click en card abre detalle · ve solucion propuesta + acciones primarias claras
  - Admin: ademas accede a configurar agentes (skills directas vs subagentes) · ve jerarquia · puede ajustar context policy
  - Owner: ademas ve costo + Unit Economics + permisos + audit
- 2026-05-02 v1.6 VIGENTE: **jerarquia bandeja-primero · sesgo arquitectura corregido**. Auditoria UX externa identifico que el mock estaba sobreoptimizado como "panel de control de IA" en vez de "bandeja de trabajo con agente asistiendo". 5 chunks:
  - **CHUNK 1 · Iterar v2 conversation-first** · 3 modos visibles arriba como tabs (Foco / Contexto / Diagnostico) · Foco default · conversacion 70-80% del ancho · sidebars como drawers colapsables (Archivos · Agente · Evidence · Costo · Aprendizaje) · composer fijo abajo · header con objeto activo + agente + costo + aprendizaje + HITL badge · acciones rapidas inline (Otra version · Comparar histo · Evidence · Golden sample)
  - **CHUNK 2 · Tab Pendientes en agente** · cada delegacion crea pendiente dentro del agente con origen + handle + objeto + instruccion humana + archivos + KB sugerida + capacidades sugeridas + costo estimado + nivel aprendizaje · boton "Abrir en Iterar" · cierra loop delegacion → trabajo. Copy "Skills ON/OFF" cambiado a "Capacidades para esta consulta" + microcopy "cambios solo para esta consulta · default requiere Admin"
  - **CHUNK 3 · Toggle de rol en topbar** (modo demo) · Operator/Supervisor/Admin/Owner · cambia visibilidad sidebar dinamicamente · Operator solo ve Mesa+Inbox+Iterar+KB · Owner ve todo · prueba que el mock funciona multi-perfil sin reescribir
  - **CHUNK 4 · Copy Mesa/Workspace** · Mesa hero "Que necesita tu decision hoy" (no "panel de control · sistema agentic") · Workspace baja protagonismo a "entrada libre · construir o explorar · si queres trabajo del dia a dia and a Mesa"
  - **CHUNK 5 · 8 reglas canon documentadas:**
    1. Home real = Mesa (no Workspace, no Dashboard)
    2. Iterar = conversation-first 70-80% (no 3 columnas igualadas)
    3. Delegar crea pendiente DENTRO del agente
    4. Capacidades por consulta son temporales (no reconfigurar produccion)
    5. Visibilidad por rol (Operator simple · Owner completo)
    6. Configuracion no compite con operacion (Agent Factory · Skill Factory · DAGs · Routing IA · Unit Economics no son protagonistas diarios)
    7. Unit Economics es Owner/Admin · no operador diario
    8. Evidence y audit resumido viven cerca del objeto (no enterrados en pantalla aparte)
  
  **Criterio de aprobacion final del mock (3 perfiles · 10 segundos cada uno):**
  - Operator: entiende que tiene que revisar · que puede aprobar · que puede iterar · que esta esperando decision
  - Admin: entiende que canal entra por donde · que agente trabaja que · que capacidades tiene · como ajustar configuracion
  - Owner: entiende cuanto cuesta · donde esta el riesgo · quien puede aprobar/enviar · si el modelo de negocio tiene margen
- 2026-05-02 v1.5 VIGENTE: refinacion UX funcional post-feedback CEO. 3 piezas nuevas:
  - **Pantalla universal `Iterar`** · mesa de trabajo sobre cualquier objeto (email/RFQ/cotizacion/doc KB/canal/agente/skill/cliente/audit/draft) · layout 3 columnas: Contexto (objeto activo + archivos + fuentes KB + historial + evidence + audit) · Conversacion/trabajo (input + chat + acciones rapidas: comparar, otra version, golden sample, convertir en agente) · Controles IA (agente activo + skills on/off + routing IA en uso + costo estimado en vivo + Nivel de aprendizaje widget + Consolidacion al pool). Accesible desde sidebar OPERAR + botones "Abrir en Iterar" en cada objeto del sistema.
  - **Widget reusable `Nivel de aprendizaje`** · score 0-10 con barra gradient + pillar breakdown (producto/cliente/politica/stock/capacidad/historico) · responde a contexto activo · muestra "como subir el nivel" con sugerencias accionables. Reutilizable en Iterar, Workspace, Mesa pre-ejecucion.
  - **Unit Economics en IA & Keys tab Usage** · 4 KPIs canon (tokens in/out/costo/costo-por-cotizacion) · costo desglosado por agente / task_type / skill / workflow con bar charts · **Simulador de precio interactivo** (tipo de tarea + volumen + % escalacion sonnet → predice costo total mes + tokens + latencia) · distribucion modelo (sonnet vs haiku) · health budget proyeccion lineal cierre mes.
  
  **Limpieza copy:** removidas referencias a "share con N tenants" en aprendizaje · "pool L3" reformulado a "aprende" · nota Agent Factory clarifica que encadenar agentes va por Mesa o outbox events (no orquestacion cruzada).
- 2026-05-02 v1.4 VIGENTE: refinacion empresarial B2B. Nav reorganizada en 3 secciones canon: **OPERAR** (Mesa, Inbox, Workspace) · **CONFIGURAR** (Canales&Routing, Agentes, Skills, KB, Voice, IA&Keys) · **ADMINISTRAR** (Usuarios&Permisos, Dashboard, Audit, Settings). 3 modulos nuevos:
  - **Canales & Routing** con tabs Canales/Reglas/Destino/Simulador/Fallbacks/Historial · handles tecnicos estables (@mailbox/@whatsapp/@workspace/@webform/@api) · simulador de routing con output canon
  - **IA & Keys** con tabs Providers/Keys/AI Profiles/Routing IA/Budgets/Usage/Rotacion · Anthropic activo · OpenAI/Voyage/Whisper diferidos E1 · 5 AI Profiles canon · pipeline Tier 0 → L1 → Context Builder → L2 → L3 → Final Pass → Token Ledger · Handoff Package YAML
  - **Usuarios & Permisos** ampliado a 7 tabs · matriz visual 19 permisos canon × 5 roles
  
  **@router** agregado como agente de **sistema** separado (sidebar tiene seccion Sistema con @router + Mis agentes). @router clasifica + decide destino + handoff inicial · NO envia/aprueba/cambia precio/produce output cliente-facing.
  
  **Limpieza copy fuera de scope:** referencias a sub-agentes E2 / pool L3 cross-tenant / k-anon / marketplace removidas o reformuladas.
- 2026-05-02 v1.3 VIGENTE: 3-capas. Agentes en sidebar global · Workspace queda con hero unico (aprendizaje) + chat. Categorias canon (CAN/REC/COG/PRO).
- 2026-05-02 v1.2 VIGENTE: refinacion UX. Toggles agentes on/off + panel aprendizaje migrados de Mesa a Workspace como hero arriba (Layout A stack vertical). Razon: separar TRABAJO (Mesa) de SISTEMA (Workspace). Mesa queda full-width solo con 5 zonas operativas. Workspace gana 2 hero cards arriba + chat con rails debajo.
- 2026-05-02 v1.1 VIGENTE: agregada seccion 8 con decisiones UX firmadas tras iteracion CEO sobre mockup E1 navegable. Mesa de Control unificada como superficie operativa unica (5 zonas + 2 paneles). Distincion Mesa vs Workspace formalizada. Sidebar reducido a 9 items. Principio "todo es agente" con 4 categorias canon (canal/recurso/cognitivo/proceso). Workspace como constructor self-extending con 3 modos. Implicaciones para sprints S1A/S3/S5/S6/S7. NO requiere MANIFIESTO_APPEND porque no contradice plan firmado · solo formaliza decisiones UX dentro del scope existente.
- 2026-05-02 v1.0 VIGENTE: creacion inicial. Puente entre plan firmado E1 y specs canon pre-existentes (SCH_FB_FLOW_DAG, ENT_FB_SUB_AGENTS_LIBRARY, ENT_FB_TOOL_CATALOG, ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE). Mapeo TIER 1 #15 + #16 + #2 ↔ specs. Extension points por sprint (S1A, S3, S6). Especifica que mostrar en mockup E1 navegable. Declara que no requiere MANIFIESTO_APPEND porque no contradice plan firmado.

## Stamp
VIGENTE 2026-05-02 v1.1 — Cierre del gap documental + formalizacion de decisiones UX rectoras tras iteracion con CEO. Mesa unificada + Workspace constructor + todo-es-agente + 4 categorias + 9 items sidebar son canon UX para Foundation Beta E1. Permite implementacion S5/S6/S7 alineada sin tener que reabrir plan firmado.
