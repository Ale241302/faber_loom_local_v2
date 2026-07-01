# PARCHE — Módulo Chat de iteración FaberLoom v2 Mockup

**Contexto:** el mockup `faberloom-mockup/index-standalone.html` ya fue construido pero omitió la superficie primaria más importante: un **chat síncrono** de iteración con el agente (tipo Claude). El prompt original se concentró en bandeja/draft-first/workflows/consola y dejó el chat sin lugar.

**Objetivo del parche:** agregar un módulo de chat completo al mockup existente, siguiendo el mismo contrato de fragments, sin regenerar el resto.

**No es refactor. Es extensión.** Tocar únicamente los archivos listados abajo.

---

## §1 · Archivos a tocar

| Archivo | Acción |
|---------|--------|
| `fragments/17_module_chat.html.fragment` | **CREAR** — el módulo chat |
| `fragments/04_shell.html.fragment` | **EDITAR** — añadir "Chat" al inicio del bloque PRINCIPAL del sidebar |
| `fragments/05_mock_data.js.fragment` | **EDITAR** — añadir `MOCK.conversations`, `MOCK.messages`, `MOCK.availableAgents`, `MOCK.availableSkillsForChat`, `MOCK.knowledgeHeatSamples` |
| `fragments/06_widgets.js.fragment` | **EDITAR** — añadir widgets `ChatMessage`, `ChatComposer`, `ToolCallCard`, `ActionHandoffCard`, `SkillInvokePanel`, `AgentSwitcher`, `KnowledgeHeatThermometer`, `MessageActionsMenu`, `ForkBranchPreview` |
| `fragments/07_i18n_es.js.fragment` + `_en` + `_pt` | **EDITAR** — añadir bloque `chat.*` |
| `fragments/03_boot.js.fragment` | **EDITAR** — registrar ruta `#/chat`, `#/chat/:conversationId` y handlers para `chat:invoke-skill`, `chat:handoff-agent`, `chat:fork-from-message` |
| `fragments/14_module_workflows_canvas.html.fragment` | **NO TOCAR** |

Después del parche: `python build.py` para regenerar el standalone.

---

## §2 · Principio arquitectónico del chat

**El chat NO rompe draft-first.** Esta es la regla de oro.

- Cuando el agente en el chat quiere **consultar, razonar, explicar, resumir, buscar en KB** → respuesta inline en el hilo.
- Cuando el agente en el chat quiere **ejecutar una acción con efecto externo** (enviar email, crear orden, escribir en CRM, publicar listing, modificar precio) → NO se ejecuta directamente. Se genera un draft con action-risk registry, se hace push a la bandeja, y el mensaje en el chat muestra un `ActionHandoffCard` con:
  - título de la acción
  - risk badge
  - botón "Revisar en bandeja" → `router.navigate('#/bandeja/' + draftId)`
  - estado sincronizado con el draft (pending → approved → executed → completed)

En L2+ algunas acciones pueden auto-ejecutarse. En ese caso, el `ActionHandoffCard` muestra el resultado final + link al run logged en runs timeline. **Aun así, toda acción queda en audit log.**

---

## §3 · Módulo chat — especificación detallada

### 3.1 Ruta
- `#/chat` → redirige a la conversación activa más reciente.
- `#/chat/:conversationId` → abre conversación específica.
- `#/chat/new` → nueva conversación (pregunta primero por agente destino).

### 3.2 Layout (3 zonas)

```
┌─────────────────────────────────────────────────────────────┐
│ TOPBAR (ya existente)                                        │
├──────────────┬─────────────────────────────┬────────────────┤
│  SIDEBAR     │                             │  CONTEXT PANE  │
│  (lista de   │      HILO DE MENSAJES       │  (agente       │
│   conversa-  │                             │   activo,      │
│   ciones)    │                             │   skills,      │
│              │                             │   scope KB,    │
│              │                             │   runs recientes)│
│              ├─────────────────────────────┤                │
│              │       CHAT COMPOSER         │                │
└──────────────┴─────────────────────────────┴────────────────┘
```

Proporción: `240px | 1fr | 320px`. En viewport < 1280px, el context pane colapsa a drawer accesible por botón.

### 3.3 Sidebar izquierdo — lista de conversaciones
- Header con botón **+ Nueva conversación**.
- Lista de conversaciones ordenadas por `lastMessageAt` desc.
- Cada ítem:
  - Avatar del agente (inicial con bg color según tier).
  - Título (generado automático del primer mensaje o editable).
  - Timestamp relativo ("hace 2h").
  - Badge si hay acciones pendientes de aprobación (ej: `⚠ 2` en coral).
  - Estado pin (⭐ si el usuario lo pinó).

### 3.4 Hilo central — mensajes

Cada mensaje es un objeto con:
```js
{
  id: 'msg_xxx',
  conversationId: 'conv_xxx',
  role: 'user' | 'agent' | 'system',
  content: 'texto markdown-ish',
  ts: '2026-04-19T10:23:00-06:00',
  citations: [
    { claimId:'c1', evidenceSpanId:'e1', source:'stock_lookup', sourceVersion:'2026-04-19T08:00:00Z', line:'V350-M: 48' }
  ],
  toolCalls: [
    { tool:'stock_lookup', args:{sku:'V350'}, result:'48 unidades', durationMs:320 }
  ],
  actionHandoff: null | { draftId:'dr_007', action:'send_email_quote', status:'awaiting_approval' }
}
```

Renderizado:
- Rol **user**: burbuja derecha, fondo `--bg-surface-raised`, text primary.
- Rol **agent**: bloque izquierda, fondo transparente, prefijo con avatar + nombre agente. Markdown básico (**bold**, _italic_, `code`, listas).
- Rol **system**: banda centrada pequeña (`cambio de contexto`, `skill activada`, `rol cambiado`).
- **Citations** inline: superíndices `[1]`, `[2]` clickeables que abren `ProvenanceSupport` widget como popover.
- **ToolCalls**: `ToolCallCard` colapsable antes de la respuesta final, muestra tool + args + result + durationMs + link al run completo.
- **ActionHandoff**: `ActionHandoffCard` al final del mensaje — destaca con `--brand-coral-haze` de fondo, tiene risk badge, status sincronizado, botón "Revisar en bandeja".

### 3.5 Composer

- Textarea con placeholder `chat.composer.placeholder` ("Escribe un mensaje o arrastra un archivo…").
- Toolbar superior:
  - Selector de skill activo (default: primary del agente).
  - Toggle "Modo explícito draft" — fuerza que cualquier sugerencia sea draft (útil para operator audit).
  - Indicador de scope de conocimiento visible (global + org + dept actual) con dropdown para añadir business_entity_id.
- Atajo `Enter` para enviar, `Shift+Enter` para nueva línea, `⌘K` para insertar command.
- Al enviar:
  1. Agrega mensaje user al hilo.
  2. Muestra mensaje agent con skeleton typing (shimmer 3 puntos).
  3. Tras 600ms-1500ms (aleatorio para realismo), reemplaza skeleton con respuesta del MOCK.
  4. Si la respuesta incluye `actionHandoff`, crea un nuevo draft en `MOCK.drafts` y lo referencia.
  5. Scroll smooth a bottom, live region announce "Nueva respuesta del agente".

### 3.6 Context pane derecho

Secciones (scrollable vertical):

**Agente activo**
- Avatar grande + nombre + autonomy badge (L1 · Propone).
- Botón "Ver consola completa" → `#/agentes/:id`.

**Skills habilitadas**
- Lista de skills del agente con risk badges. Click → `#/skills/:id`.
- Toggle para desactivar temporalmente (solo admin/owner).

**Scope de conocimiento en juego**
- Bloques visuales con 4 scopes (global/org/dept/user) con contador de chunks recuperados en la conversación actual.
- business_entity_id actual si hay (ej: "be_acme_mx — ACME Industrias MX").

**Runs recientes**
- Últimos 5 runs generados por esta conversación, cada uno con link a runs timeline.

**Acciones pendientes**
- Lista de drafts originados en este chat (con link a bandeja).
- Contador visible como badge en el sidebar izquierdo.

**Debug panel** (colapsado default, solo visible con `?debug=1`):
- Full message object del último turno (JSON pretty).
- Tool calls con timings.
- Retrieval: qué chunks se buscaron, cuáles hicieron match, scores.

### 3.7 View-states

- **loaded** — conversación con mensajes.
- **empty** — conversación nueva, el hilo muestra `EmptyState` con CTA "Hazle una pregunta al agente" + 3 sugerencias (ej: "¿Cuál es el stock actual de Velox 350?", "Cotiza 10 pares Goliath XT para ACME MX", "Resumí las últimas 5 cotizaciones").
- **loading** — skeleton de 3 mensajes alternados.
- **error** — DegradedCard con retry.

### 3.8 Autonomy-aware behavior

- En **L0 (Shadow)**: todas las respuestas del agente son internas. El usuario ve la respuesta pero el sistema marca "Shadow — no se ejecuta ninguna acción". Cualquier `actionHandoff` aparece en estado `shadow_only` (gris, no clickeable).
- En **L1 (Propone)**: toda acción genera draft → bandeja. `ActionHandoffCard` tiene botón "Revisar en bandeja".
- En **L2 (Auto-bajo)**: acciones con `reversibility = reversible_24h` Y `action.auditClass ≠ financial` pueden auto-ejecutarse. `ActionHandoffCard` muestra estado `auto_executing` → `completed` con link al run. Para el resto, sigue yendo a bandeja.
- En **L3/L4**: progresivamente más acciones auto-ejecutan, pero cada acción queda en audit log. `ActionHandoffCard` puede mostrar estado `completed` directo sin intervención.

Para el mockup: el banner superior del hilo muestra el nivel actual del agente y una línea "En este nivel, X tipo de acciones requieren aprobación" para que sea obvio.

### 3.9 Widgets nuevos

#### `ChatMessage`
- Props: `{ message, onCitationClick, onActionHandoffClick }`.
- Responsabilidad: renderizar un mensaje completo con todas sus partes (content, citations, toolCalls, actionHandoff).

#### `ChatComposer`
- Props: `{ agentId, skillId, onSend, onSkillChange, mode:'draft'|'auto', scope }`.
- Responsabilidad: textarea + toolbar + shortcut handling.

#### `ToolCallCard`
- Props: `{ tool, args, result, durationMs, runId }`.
- Layout: colapsable, default cerrado, muestra una línea resumen "🔧 stock_lookup(sku='V350') → 48 unidades · 320ms" y expande a JSON pretty.

#### `ActionHandoffCard`
- Props: `{ action, draftId, status, riskBadge, onReview }`.
- Layout: card con fondo `--brand-coral-haze`, título de acción, risk badge, status badge, botón "Revisar en bandeja".
- Estados: `pending` (amber), `awaiting_approval` (amber), `approved` (sage), `executing` (sky), `completed` (green), `failed` (coral), `shadow_only` (gris).

### 3.10 Keyboard shortcuts dentro del chat

- `Enter` — enviar.
- `Shift+Enter` — nueva línea.
- `⌘K` / `Ctrl+K` — abrir command palette (futuro, por ahora toast stub).
- `⌘↑` — editar último mensaje usuario.
- `Esc` — cerrar popovers (citation, tool call expanded).
- `⌘/` — toggle context pane.
- `⌘E` — invocar skill directo (abre `SkillInvokePanel`).
- `⌘A` — handoff a otro agente (abre `AgentSwitcher`).

### 3.11 Skills activables desde el chat

En el context pane derecho, la sección **Skills habilitadas** pasa de lista read-only a **panel interactivo** (widget `SkillInvokePanel`):

- Cada skill muestra:
  - Toggle on/off (desactivar temporalmente para esta conversación — no afecta config global del agente).
  - Badge risk (heredado de la skill).
  - Badge `Learning Thermometer` (🔵 Frío 0-2 · 🟡 Tibio 3-5 · 🔴 Caliente 6+ patrones pendientes) — clickeable → abre `ConsolidationModal`.
  - Botón **Invocar** (play icon).
  - Link ⚙ → `#/skills/:id` para editar en Skill Studio.
- Skills desactivadas (toggle off) quedan con opacidad 0.5 + banner "Desactivada en esta conversación".

**Invocar skill directo (path 1):**
- Click en **Invocar** abre un modal compacto (widget `SkillInvokePanel` en modo full) con los parámetros que la skill expone.
- Al ejecutar, **NO genera un mensaje user**. La invocación aparece en el hilo como:
  - Mensaje `role='system'` centrado: "Skill invocada · `sk_stock_lookup` · args=`{sku:'V350'}`"
  - Seguido de un **mensaje del agente** con el resultado formateado como tool-call style: bloque `ToolCallCard` desplegable + interpretación textual corta del resultado.
- No se dispara razonamiento del LLM si no hace falta. La skill puede ser puro tool call. Si requiere síntesis, el agente envuelve el resultado en lenguaje natural.
- `citations` apuntan al tool output como fuente (`source='tool:<name>'`, `sourceVersion=<timestamp>`).

**Handoff a agente (path 2):**
- En el context pane, debajo del agente activo, nueva sección **Otros agentes disponibles** (widget `AgentSwitcher`):
  - Lista de agentes del tenant con avatar, nombre, autonomy level, tier, 1 línea descriptiva.
  - Botón **Handoff** por cada uno.
- Click en **Handoff** inserta en el hilo:
  - Mensaje `role='system'`: "Handoff a `ag_specs_tecnicas` · contexto conversación compartido"
  - Mensaje del nuevo agente con saludo corto + respuesta a la última pregunta del user.
- El context pane actualiza agente activo, skills y scope al del nuevo agente.
- **El hilo permanece unificado** — no se bifurca en otra conversación. Queda trazabilidad del handoff.
- Se puede volver al agente anterior con otro handoff, o desde el menu del mensaje system ("Volver a ag_cotizador").

**Diferencia conceptual entre los dos paths:**

| Aspecto | Invocar skill directo (⌘E) | Handoff a agente (⌘A) |
|---------|----------------------------|------------------------|
| Qué hace | Ejecuta una capacidad específica sin razonamiento LLM si no es necesario | Pasa la conversación a otro agente con su propio sistema de skills, memoria y autonomía |
| Resultado en hilo | Mensaje system + tool-call style card | Mensaje system + mensaje conversacional del agente nuevo |
| Contexto | Se mantiene el agente activo; la skill responde en su nombre | Cambia el agente activo; el nuevo toma el hilo |
| Caso típico | "Chequeá stock de V350" | "Necesito specs técnicas ASTM — pasalo a Specs Técnicas" |

### 3.12 Iteración desde mensaje del agente

Cada mensaje con `role='agent'` expone un **menu de acciones contextual** (widget `MessageActionsMenu`) al hacer hover / focus / click en botón `⋯`:

- **💬 Continuar con este agente** — si el agente activo actual es distinto (después de un handoff), vuelve al agente que generó este mensaje y pone el composer enfocado.
- **🪄 Refinar esta respuesta** — prompt-builder pre-cargado con la respuesta actual + opciones: "más corto / más detallado / con más evidencia / con tono más formal / con números actualizados". Envía como nuevo turno.
- **🌿 Bifurcar desde aquí** — crea nueva conversación copiando el contexto hasta este mensaje (widget `ForkBranchPreview` con preview antes de confirmar). Útil cuando querés explorar una alternativa sin perder la línea actual.
- **📋 Copiar** — copia el texto.
- **📌 Pinear como contexto** — marca el mensaje como "contexto pinned" — siempre incluido en los siguientes turnos aunque la conversación crezca.
- **⚠ Reportar feedback** — abre `FeedbackModal` con las 5 razones tipificadas (claim sin evidencia / tono / dato incorrecto / acción riesgosa / otro).
- **🔎 Ver evidencia completa** — expande todas las citations del mensaje al panel derecho en modo drill-down.
- **🧪 Enviar a gold samples** — captura este turno como gold sample candidato para el skill activo (abre modal con campos rubric).

**Crítico:** "editar mensaje" sigue existiendo para `role='user'` (corrige y re-envía), pero NO para `role='agent'` — la respuesta del agente es immutable histórica. Para modificar lo que dijo, usás **Refinar**, que genera nuevo turno y deja el original visible con badge "superseded" opcional.

Esto implementa "iterar sobre la respuesta del agente" sin romper el ledger conversacional ni el audit.

### 3.13 Termómetros del chat — DOS distintos

#### 3.13.1 Learning Thermometer (por skill)

- **Qué mide:** patrones learned pendientes de consolidar del skill activo.
- **Dónde vive:** en `SkillInvokePanel` del context pane, en cada skill de la lista.
- **Escala:** 🔵 Frío 0-2 · 🟡 Tibio 3-5 · 🔴 Caliente 6+.
- **Acción:** si llega a hot, el badge se vuelve clickeable → `ConsolidationModal` con los patrones pendientes del skill.
- **Ya existía** en Skill Studio. Acá se replica en el chat para visibilidad.

#### 3.13.2 Knowledge Heat (por respuesta del agente)

Widget nuevo `KnowledgeHeatThermometer`. Aparece en **dos lugares**:

**(a) Inline en cada mensaje del agente** (a la derecha del avatar o al pie del mensaje, según diseño visual):
- **Qué mide:** cobertura de evidencia de la respuesta actual.
  - Claims con `evidenceSpans.length > 0` / total claims del mensaje.
- **Escala invertida al Learning Thermometer** (coherente con el lenguaje: caliente = alerta):
  - 🔵 Frío = cobertura ≥ 80% (la mayoría de los claims tienen provenance) → OK
  - 🟡 Tibio = cobertura 50-79% (parcial) → atención
  - 🔴 Caliente = cobertura < 50% (respuesta mayormente generativa sin fuente) → alerta
- **Tooltip:** "X de Y claims con evidencia · Z claims sin respaldo".
- **Click:** abre panel de evidencia con los claims sin respaldo resaltados en `--brand-evidence`.

**(b) Global de la conversación** en el header del hilo (promedio ponderado de los últimos 5 mensajes del agente):
- Badge pill con el mismo código de color.
- Tooltip: "Cobertura promedio últimos 5 turnos: X%".
- Click: abre un panel que lista turnos con Knowledge Heat > tibio.

**Comportamiento automático:**
- Si Knowledge Heat de un turno es **rojo (caliente)**, aparece bajo la respuesta un banner discreto: `⚠ Respuesta con baja cobertura de evidencia. ¿Querés verificar antes de usarla?` con botones "Pedir respaldo" (genera nuevo turno pidiendo al agente que cite fuentes) y "Descartar aviso".
- Si en L0-L1 el Knowledge Heat > tibio, las `ActionHandoffCard` de ese turno muestran un warning adicional: "Esta acción se basa en una respuesta con baja evidencia. Revisá antes de aprobar."

**Diferencia con Learning Thermometer — explícita:**

| Termómetro | Objeto | Qué mide | Escala | Acción |
|-----------|--------|----------|--------|--------|
| **Learning Thermometer** | Skill | Patrones learned pendientes | 🔵0-2 🟡3-5 🔴6+ (hot = oportunidad de consolidar) | Abrir `ConsolidationModal` |
| **Knowledge Heat** | Respuesta del agente | Cobertura de evidencia | 🔵≥80% 🟡50-79% 🔴<50% (hot = alerta de respuesta sin respaldo) | Pedir respaldo / verificar |

Ambos visibles simultáneamente — son ortogonales.

### 3.14 Composer extendido

Además de lo descrito en §3.5, el composer ahora expone:

- **Dropdown de agente activo** al lado del selector de skill — permite cambiar agente directo desde el composer (alternativa a `AgentSwitcher`).
- **Dropdown de modo de envío:**
  - **Pregunta** — turno normal user → agente.
  - **Invocar skill** — abre `SkillInvokePanel` (equivalente a ⌘E).
  - **Handoff** — abre `AgentSwitcher` (equivalente a ⌘A).
- **Indicador de Knowledge Heat estimado** (preview) — si el texto que estás escribiendo menciona entidades conocidas en KB, muestra preview del heat esperado.

---

## §4 · Mock data para el chat (editar `05_mock_data.js.fragment`)

Añadir 2 colecciones nuevas:

```js
MOCK.conversations = [
  {
    id:'conv_001', tenantId:'t_muito', userId:'u_alvaro', agentId:'ag_cotizador',
    title:'Cotización ACME MX — 22 pares calzado',
    businessEntityId:'be_acme_mx',
    createdAt:'2026-04-19T09:05:00-06:00',
    lastMessageAt:'2026-04-19T10:23:00-06:00',
    pendingActions:1, pinned:true, state:'active'
  },
  {
    id:'conv_002', tenantId:'t_muito', userId:'u_alvaro', agentId:'ag_cotizador',
    title:'Consulta stock Velox 350 disponibilidad inmediata',
    businessEntityId:null,
    createdAt:'2026-04-18T14:10:00-06:00',
    lastMessageAt:'2026-04-18T14:32:00-06:00',
    pendingActions:0, pinned:false, state:'active'
  },
  {
    id:'conv_003', tenantId:'t_muito', userId:'u_ana', agentId:'ag_pipeline_follow',
    title:'Seguimiento 3 oportunidades Constru Bogotá',
    businessEntityId:'be_constru_co',
    createdAt:'2026-04-17T11:00:00-06:00',
    lastMessageAt:'2026-04-17T17:45:00-06:00',
    pendingActions:2, pinned:false, state:'active'
  },
  // 4 conversaciones más cubriendo: otra con agente distinto, una archivada, una con error, una sin mensajes (empty state)
];

MOCK.messages = {
  conv_001: [
    {
      id:'msg_001_1', conversationId:'conv_001', role:'user',
      content:'Necesito cotizar 14 pares Velox 350 + 8 pares Goliath XT para ACME MX. Plazo máximo 10 días.',
      ts:'2026-04-19T09:05:12-06:00',
      citations:[], toolCalls:[], actionHandoff:null
    },
    {
      id:'msg_001_2', conversationId:'conv_001', role:'agent',
      content:'Confirmado. Verifico stock y tabla de precios MX.',
      ts:'2026-04-19T09:05:18-06:00',
      citations:[], toolCalls:[
        { tool:'stock_lookup', args:{skus:['V350','GXT']}, result:'V350: 48 unidades · GXT: 12 unidades', durationMs:320, runId:'r_881' },
        { tool:'price_table', args:{country:'MX'}, result:'Tabla MX v2026.04 cargada', durationMs:85, runId:'r_881' }
      ], actionHandoff:null
    },
    {
      id:'msg_001_3', conversationId:'conv_001', role:'agent',
      content:'Preparé la cotización con los siguientes datos:\n\n- **Velox 350 (14 pares)**: $14,840 MXN [1]\n- **Goliath XT (8 pares)**: $9,680 MXN [2]\n- **Subtotal**: $24,520 MXN\n- **IVA 16%**: $3,923 MXN\n- **Total**: $28,443 MXN\n- **Plazo estimado**: 7 días hábiles [3]\n\nGeneré un draft para tu revisión.',
      ts:'2026-04-19T09:12:00-06:00',
      citations:[
        { claimId:'c1', evidenceSpanId:'e1', source:'price_table', sourceVersion:'2026.04', line:'V350-M × 14 = 14,840 MXN' },
        { claimId:'c2', evidenceSpanId:'e2', source:'price_table', sourceVersion:'2026.04', line:'GXT × 8 = 9,680 MXN' },
        { claimId:'c3', evidenceSpanId:'e3', source:'policy_playbook', sourceVersion:'1.2.0', line:'MX plazo default = 7d' }
      ],
      toolCalls:[],
      actionHandoff:{ draftId:'dr_001', action:'send_email_quote', status:'awaiting_approval' }
    },
    {
      id:'msg_001_4', conversationId:'conv_001', role:'user',
      content:'¿Podés añadir cláusula de garantía 6 meses estándar?',
      ts:'2026-04-19T10:22:00-06:00',
      citations:[], toolCalls:[], actionHandoff:null
    },
    {
      id:'msg_001_5', conversationId:'conv_001', role:'agent',
      content:'Actualizo el draft con cláusula de garantía 6 meses para defectos de fabricación (estándar Marluvas/Tecmater) [1].',
      ts:'2026-04-19T10:23:15-06:00',
      citations:[
        { claimId:'c4', evidenceSpanId:'e4', source:'policy_playbook', sourceVersion:'1.2.0', line:'Garantía default 6 meses defectos fabricación' }
      ],
      toolCalls:[
        { tool:'draft_update', args:{draftId:'dr_001', patch:'+garantía 6 meses'}, result:'Draft dr_001 actualizado', durationMs:150, runId:'r_883' }
      ],
      actionHandoff:{ draftId:'dr_001', action:'send_email_quote', status:'awaiting_approval' }
    }
  ],
  conv_002: [
    // 6-8 mensajes de una consulta de stock corta (sin actionHandoff, solo tool calls)
  ],
  conv_003: [
    // 12+ mensajes con 2 actionHandoffs (seguimiento pipeline)
  ],
  conv_004: [
    // conversación con agent en L0 Shadow — actionHandoff status = shadow_only
  ],
  conv_005: [
    // conversación con agent en L3 — actionHandoff status = completed directo
  ],
  conv_006: [
    // conversación con error: último mensaje con toolCall failed
  ],
  conv_007: [] // empty state demo
};

// Respuestas canned para simular el agente cuando el usuario manda un mensaje nuevo en el mockup:
MOCK.cannedResponses = {
  default: 'Entiendo. Déjame revisar los datos disponibles.',
  'stock': 'Stock actual: Velox 350: 48 unidades · Goliath XT: 12 unidades · Manta: 34 unidades.',
  'cotiz': 'Genero cotización con precios MXN + IVA 16%. Plazo estimado 7 días hábiles.',
  'precio': 'Tabla de precios MX v2026.04. Para descuento volumen >50 pares, escalar a admin.',
  'resumen': 'Últimas 5 cotizaciones: 3 aprobadas, 1 pendiente, 1 rechazada por plazo.'
};

// Agentes disponibles para handoff desde chat (subset de MOCK.agents con campos relevantes):
MOCK.availableAgents = [
  { id:'ag_cotizador',        name:'Cotizador Calzado',         tier:'demo-critical', autonomy:'L1', tagline:'Genera cotizaciones B2B Marluvas/Tecmater' },
  { id:'ag_specs_tecnicas',   name:'Specs Técnicas',            tier:'hot',           autonomy:'L1', tagline:'ASTM F2413, composite vs steel toe, normativas' },
  { id:'ag_stock_lookup',     name:'Stock Lookup',              tier:'internal',      autonomy:'L2', tagline:'Consulta stock real-time suppliers' },
  { id:'ag_pipeline_follow',  name:'Seguimiento Pipeline',      tier:'warm',          autonomy:'L1', tagline:'Follow-up oportunidades CRM' },
  { id:'ag_onboarding',       name:'Onboarding Cliente',        tier:'cold',          autonomy:'L0', tagline:'Shadow — captura proceso nuevos clientes' },
  { id:'ag_soporte_post',     name:'Soporte Post-venta',        tier:'warm',          autonomy:'L1', tagline:'Garantías, reclamos, reposiciones' },
  { id:'ag_precios_experimental', name:'Precios Dinámicos',     tier:'experimental',  autonomy:'L0', tagline:'Shadow — explora pricing por volumen' }
];

// Skills disponibles al chat con estado por conversación:
MOCK.availableSkillsForChat = [
  { id:'sk_cotizar',          name:'Cotizar calzado seguridad', owner:'ag_cotizador',       risk:'reversible_24h',  learningHeat:6,  enabledByDefault:true,  invokeParams:[{name:'cliente',type:'businessEntity',required:true},{name:'items',type:'array[{sku,qty}]',required:true},{name:'plazo_max_dias',type:'int',required:false}] },
  { id:'sk_specs_tecnicas',   name:'Validación ASTM',            owner:'ag_specs_tecnicas', risk:'reversible_24h',  learningHeat:2,  enabledByDefault:true,  invokeParams:[{name:'norma',type:'string',required:true},{name:'modelo',type:'string',required:true}] },
  { id:'sk_stock_lookup',     name:'Consulta stock',             owner:'ag_stock_lookup',    risk:'reversible_24h',  learningHeat:1,  enabledByDefault:true,  invokeParams:[{name:'sku',type:'string',required:true}] },
  { id:'sk_seguimiento_pipeline', name:'Seguimiento oportunidades', owner:'ag_pipeline_follow', risk:'reversible_24h', learningHeat:4, enabledByDefault:true, invokeParams:[{name:'account',type:'businessEntity',required:true},{name:'tipo',type:'enum[email,llamada,reunion]',required:true}] },
  { id:'sk_hola_cliente',     name:'Saludo cliente',             owner:'ag_onboarding',      risk:'reversible_24h',  learningHeat:0,  enabledByDefault:false, invokeParams:[{name:'cliente',type:'businessEntity',required:true}] },
  { id:'sk_validacion_astm',  name:'Validación ASTM detallada',  owner:'ag_specs_tecnicas', risk:'reversible_24h',  learningHeat:3,  enabledByDefault:true,  invokeParams:[{name:'modelo',type:'string',required:true}] },
  { id:'sk_generacion_pdf',   name:'Generar cotización PDF',     owner:'ag_cotizador',       risk:'reversible_24h',  learningHeat:5,  enabledByDefault:true,  invokeParams:[{name:'draftId',type:'string',required:true}] }
];

// Para cada message del agente, agregar computed knowledgeHeat (0-100%).
// En el mockup lo derivamos del mensaje: (claims con evidencia / total claims) · 100.
// Si no hay claims: knowledgeHeat = null (no aplica, ej: system messages o ack cortos).
// Ejemplos incrustados en MOCK.messages:
//   msg_001_3 (cotización completa): 3 claims con evidencia / 3 = 100% → 🔵 Frío (OK)
//   msg_001_5 (añadir garantía): 1 claim con evidencia / 1 = 100% → 🔵 Frío
//   conv_004 mensaje con respuesta generativa sin source: knowledgeHeat = 30% → 🔴 Caliente
//   conv_006 mensaje con 2 de 4 claims respaldados: knowledgeHeat = 50% → 🟡 Tibio

// Samples para demo del Knowledge Heat (se inyectan en conversaciones específicas):
MOCK.knowledgeHeatSamples = {
  conv_004: { avgHeat:'hot', avgCoverage:0.32, turnsWithAlert:3 },
  conv_005: { avgHeat:'cold', avgCoverage:0.94, turnsWithAlert:0 },
  conv_006: { avgHeat:'warm', avgCoverage:0.58, turnsWithAlert:1 },
  conv_001: { avgHeat:'cold', avgCoverage:0.90, turnsWithAlert:0 }
};

// Mensajes system adicionales para demostrar invocación directa y handoff:
//   msg_002_4 (en conv_002): role=system, content='Skill invocada · sk_stock_lookup · args={sku:"V350"}'
//   msg_002_5 (en conv_002): role=agent (stock_lookup), content='48 unidades disponibles...', con toolCall
//   msg_003_8 (en conv_003): role=system, content='Handoff a ag_specs_tecnicas · contexto compartido'
//   msg_003_9 (en conv_003): role=agent, agentId=ag_specs_tecnicas, content='Tomo el hilo. Según ASTM F2413...'
```

---

## §5 · i18n a añadir

En `07_i18n_es.js.fragment` agregar al objeto `I18N_ES`:

```js
chat: {
  title: 'Chat con agente',
  new_conversation: 'Nueva conversación',
  placeholder_composer: 'Escribí un mensaje o arrastrá un archivo…',
  send: 'Enviar',
  sending: 'Enviando…',
  typing: 'El agente está pensando',
  empty_title: 'Sin conversaciones aún',
  empty_description: 'Empezá hablando con un agente. Podés pedirle que busque datos, razone sobre información, o prepare un draft para revisar.',
  suggest_1: '¿Cuál es el stock actual de Velox 350?',
  suggest_2: 'Cotizá 10 pares Goliath XT para ACME MX',
  suggest_3: 'Resumí las últimas 5 cotizaciones',
  context_agent: 'Agente activo',
  context_skills: 'Skills habilitadas',
  context_scope: 'Scope de conocimiento',
  context_runs: 'Runs recientes',
  context_pending: 'Acciones pendientes',
  context_debug: 'Debug',
  view_console: 'Ver consola completa',
  review_in_bandeja: 'Revisar en bandeja',
  tool_call: 'Tool call',
  duration_ms: '{ms}ms',
  autonomy_banner_l0: 'Shadow — ninguna acción se ejecuta',
  autonomy_banner_l1: 'Propone — las acciones con efecto externo requieren aprobación en bandeja',
  autonomy_banner_l2: 'Auto-bajo — acciones reversibles se ejecutan solas · irreversibles siguen requiriendo aprobación',
  autonomy_banner_l3: 'Auto+notif — casi todo auto-ejecuta con log',
  autonomy_banner_l4: 'Auto+excepciones — solo edge cases requieren aprobación',
  force_draft_mode: 'Forzar modo draft',
  shadow_only: 'Shadow · sin ejecutar',
  action_pending: 'Pendiente',
  action_awaiting: 'Esperando aprobación',
  action_approved: 'Aprobado',
  action_executing: 'Ejecutando',
  action_completed: 'Completado',
  action_failed: 'Falló',
  edit_last: 'Editar último mensaje',
  new_message_announce: 'Nueva respuesta del agente',
  citation_label: 'Cita {n}'
}
```

Y equivalentes en `I18N_EN` y `I18N_PT` (traducidos, mantener mismas claves).

---

## §6 · Shell — insertar en sidebar

En `04_shell.html.fragment`, en el bloque PRINCIPAL del sidebar, agregar **Chat al principio** (antes de Bandeja):

```html
<nav class="fl-sidebar__group">
  <div class="fl-sidebar__group-title" data-i18n="nav.group_main">Principal</div>
  <a class="fl-sidebar__item" href="#/chat" data-i18n="nav.chat">Chat</a>         <!-- NUEVO -->
  <a class="fl-sidebar__item" href="#/bandeja" data-i18n="nav.bandeja">Bandeja</a>
  <a class="fl-sidebar__item" href="#/agentes/ag_cotizador" data-i18n="nav.agentes">Agentes</a>
  <a class="fl-sidebar__item" href="#/workflows" data-i18n="nav.workflows">Workflows</a>
  <a class="fl-sidebar__item" href="#/runs" data-i18n="nav.runs">Runs</a>
</nav>
```

Y en i18n `nav`:
```js
nav: { ..., chat:'Chat', ... }
```

Y cambiar la ruta default del router (fragment `03_boot.js.fragment`) de `#/bandeja/dr_001` a `#/chat/conv_001` — el chat es la entrada primaria.

---

## §7 · Router — añadir rutas

En `03_boot.js.fragment`, en el objeto `ROUTES`:

```js
const ROUTES = {
  '#/chat':                'chat',               // redirige a lastActive
  '#/chat/new':            'chat',               // modo nueva conversación
  '#/chat/:conversationId':'chat',               // conversación específica
  '#/bandeja':             'bandeja-lista',
  '#/bandeja/:id':         'bandeja-detail',
  // ... resto igual
};
```

Parseo de `:conversationId` debe resolver a `ctx.params.conversationId`.

---

## §8 · Acceptance criteria del parche (10 binarios)

1. Ruta `#/chat` carga y redirige a `conv_001` por default.
2. Sidebar izquierdo muestra 7 conversaciones con `conv_001` al tope, pinned.
3. Hilo de `conv_001` muestra 5 mensajes con alternancia user/agent correcta.
4. Mensaje `msg_001_2` muestra 2 ToolCallCards colapsables.
5. Mensaje `msg_001_3` muestra 3 citations clickeables que abren popover con ProvenanceSupport.
6. Mensaje `msg_001_3` muestra ActionHandoffCard con link a `#/bandeja/dr_001`.
7. Click en "Revisar en bandeja" navega a Bandeja con el draft abierto.
8. Composer con Enter envía mensaje, agrega respuesta canned del agente tras 800-1200ms con shimmer intermedio.
9. Context pane derecho muestra agente activo, skills, scope, runs, pending actions con contador.
10. Toggle light/dark + idioma ES/EN/PT afectan correctamente el módulo chat.

---

## §9 · Cómo arranca Claude Code

```
Leé /MWT KB/PROMPT_PARCHE_FABERLOOM_CHAT_2026-04-19.md.
Trabajá en /MWT KB/faberloom-mockup/.
NO regenerar el mockup completo. Solo parchar los archivos listados en §1.
Seguí specs §3 (módulo), §4 (mock), §5 (i18n), §6 (shell), §7 (router).
Al terminar, `python build.py` y verificar los 10 AC de §8 abriendo index-standalone.html.
Reportá: cuáles AC pasaron verdes, cuáles no, con detalle del fail.
```

---

**Fin del parche.** Este prompt es aditivo — no toca widgets existentes ni módulos previos.
