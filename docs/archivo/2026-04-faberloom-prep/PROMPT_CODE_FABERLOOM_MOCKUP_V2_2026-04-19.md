# PROMPT v2 · FaberLoom Mockup — Chat + Visual Language ONE + cierre de brechas

**Target:** Claude Code
**Fecha:** 2026-04-19
**Autor:** Álvaro (Muito Work) vía Claude main
**Base de trabajo:** `MWT KB/faberloom-mockup/` (v1 entregado con 25 fragmentos, ver `DELIVERY_NOTES.md`)
**Naturaleza:** **ADITIVO** sobre lo existente. No reescribís lo que ya funciona; añadís lo que falta + edits quirúrgicos en 5 fragmentos enumerados.

---

## 0. Contexto mínimo que debés internalizar

Ya existe una entrega v1 funcional en `MWT KB/faberloom-mockup/` con:

- `build.py` (concatenador Python, zero-dep)
- `index-standalone.html` (223 KB, 4,226 líneas) abierto por doble-click
- 25 fragmentos en `fragments/` (ver tabla en DELIVERY_NOTES)
- 14 módulos ruteados
- 15 widgets en `window.__faberloom.widgets`
- 17 colecciones mock
- i18n ES/EN/PT (~200 keys)
- Demo-critical en `#/bandeja/dr_001` con provenance cross-highlight funcionando
- Paleta A3 WCAG AA verificada (light + dark)
- `research/A1..A6` documentando canon y reconciliaciones

**Canon FaberLoom (no negociable, ya correctamente implementado):**

- 3 objetos canónicos: AgentSpec · AgentRuntime · AgentMemory
- State machine 10 estados (drafting · awaiting_approval · approved · executing · waiting_external_signal · blocked · completed · failed · escalated · rejected)
- Autonomy Ladder L0-L4 con internal IDs A4 (SHADOW · PROPONE · EJECUTA_INTERNO · AUTO_NOTIFICA · AUTO_EXCEPCIONES) + labels UI friendlier
- Skill 3 capas (base sellada · manual overlay · learned overlay gate humano)
- Provenance chain `claim_id → evidence_span_id → source (sourceVersion, line, retrievalRunId)`
- Action-risk registry 6 campos (action_id, reversibility, side_effects, min_autonomy, required_role, audit_class)
- ModelFingerprint P13 (provider, model_family, model_version, system_prompt_hash, tools_manifest_hash, policy_version, retrieval_index_version)
- 4 scopes knowledge: global · org · dept · user + business_entity_id (SPEC v1 Beta canónico)
- 3 roles: Tenant Owner · Admin · Operator
- Consolidation states: candidate / active / archived / revoked (UI label "Reverted" para revoked)
- Break-glass 8h con MFA (`support_impersonation` permission)
- TTL 90d default (rango 30-180)
- RLS via session variables (app.tenant_id, app.user_id, app.role, app.dept_ids, app.break_glass)

---

## 1. Decisiones ya tomadas (no preguntar, ejecutar)

| Decisión | Valor | Justificación |
|---|---|---|
| Knowledge scopes UI | **4 scopes (global/org/dept/user)** | Canónico A5 SPEC v1 Beta. No romper backend |
| Idioma primario UI | **ES** | Mercado LATAM B2B · MX/CO |
| EN + PT | Mirror simétrico | Soporte demo a partners angloparlantes/BR |
| Default route al boot | `#/chat` (nueva) | Primera impresión conversacional, no bandeja |
| Tenant default | `t_muito` | Owner pruebas |
| Rol default | `owner` | Panorama completo |
| Diseño visual chat | Hereda FaberLoom ONE | Patrones: Grounded in · Iterate on this draft · Always-on Personal+Org · Voice of Customer · Pattern/Gold/No-pattern labels · Suggest grid · SLA timers |
| Draft-first | Absoluto | Toda acción externa pasa por drafts/bandeja |
| Action handoff | Chat ↔ Bandeja bidireccional | Mensaje en chat muestra pill "Draft dr_XXX · awaiting_approval" que linkea a `#/bandeja/:id` |

---

## 2. Reglas inquebrantables de ejecución

1. **No tocar fragmentos 10, 11, 12, 14, 15, 16, 22, 30, 31** — están sólidos según revisión.
2. Ediciones quirúrgicas **solo** en los fragmentos enumerados en §4. Cada edit debe llevar comentario `/* [V2-PATCH 2026-04-19] */` identificando la línea.
3. **Nuevo = nuevo fragmento numerado 17 en adelante.** No explotar la numeración existente.
4. **Grant sub-agent write access a `MWT KB/faberloom-mockup/`** antes de empezar. Sub-agentes escribiendo en paralelo es la aceleración clave que te frenó la v1.
5. **Concatena vía `build.py`** existente. No cambies el contrato de fragmentos.
6. **axe-core WCAG 2.1 AA** debe pasar 0 violations en las rutas nuevas (`/chat`, `/chat/:id`). Ejecutá "Validar" del topbar y capturá el output a `verification/axe_v2.md`.
7. **Dark palette A3** respetada en todo widget nuevo.
8. **No ESM, no fetch, no deps nuevas** excepto axe-core (ya cargado on-demand).
9. **i18n simétrico** ES/EN/PT. Toda key nueva en los 3 archivos.
10. **Docstring en cada widget** nuevo (propósito + props + ejemplo de uso).

---

## 3. Tareas por prioridad

### P0 · Chat module (el faltante crítico)

#### 3.1 Crear `fragments/17_module_chat.html.fragment`

**Ruta:** `#/chat` (lista/home) y `#/chat/:conversationId` (detalle)

**Layout 3 columnas (max-width 1600px):**

```
┌─ Left: Agents + Skills ─┬─ Center: Conversation ─────┬─ Right: Grounded in + SLA + Handoffs ─┐
│                         │                             │                                         │
│ Always-on (Personal+Org)│ [conversation messages]     │ Grounded in                            │
│ ─────                   │ [composer]                  │  · ENT_PROD_MAN v1.3 §B1              │
│ Agents (6 available)    │                             │  · MX price list 2026 Q1              │
│  · Cotizador MX   L1    │                             │  · Policy POL_MX_001                  │
│  · Sourcing CO    L0    │                             │ ─────                                   │
│  · Customer CS    L2    │                             │ SLA                                     │
│  · Marluvas OEM   L1    │                             │  p95 target: 300ms · current: 310ms ⚠ │
│ ─────                   │                             │ ─────                                   │
│ Skills (12 available)   │                             │ Active handoffs                         │
│  · Cotizar        🔴   │                             │  · Draft dr_042 · awaiting_approval   │
│  · Sourcing       🟡   │                             │                                         │
│  · Email draft    🟢   │                             │                                         │
│  · Consolidate    ⚪   │                             │                                         │
└─────────────────────────┴─────────────────────────────┴─────────────────────────────────────────┘
```

**Funcionalidad:**

- **Left column:**
  - Título "Always-on": con candado 🔒 chip `Personal` + chip `Org (Muito Work)`. No desactivables (son el default grounding).
  - Título "Agents": lista de `FL.mock.availableAgents` con badge autonomía + sparkline runs últimos 7d. Click en un agente → handoff chip aparece en composer + su nombre queda en cabecera de conversación ("Hablando con: Cotizador MX · L1").
  - Título "Skills": lista de `FL.mock.availableSkillsForChat` con thermometer icon (🔴🟡🟢⚪ según learningHeat). Click → activa el skill como pill en composer. Click 2do en skill activo → desactiva.

- **Center column:**
  - Si no hay conversación activa → empty state con SuggestGrid de 4 sugerencias ("Cotizar 500 pares Marluvas Goliath a cliente MX-123", "Consolidar feedback última semana", "Resumen pipeline Colombia", "Verificar cumplimiento política POL_MX_001").
  - Si hay conversación → lista de messages. Cada message del agente incluye:
    - Contenido con provenance superscripts `[E1]..[En]` (hover → right column Grounded in highlight).
    - `PatternBadge` en esquina inferior derecha: "Pattern learned · 14 runs" · "Gold sample · 9/10" · "No pattern yet".
    - `MessageActionsMenu` (icon button, 8 acciones): Copy · Iterate · Handoff · Open draft · Explain evidence · Consolidate · Feedback · Rerun.
    - Si la respuesta generó un draft → pill `Draft dr_XXX · awaiting_approval` linkea a `#/bandeja/:id`.
  - Message del user: simple bubble + timestamp.
  - **Iterate on this draft (ONE pattern):** cuando el user clickea "Iterate" en un message del agente → debajo de ese message aparece **IterationComposer** (caja embebida, no el composer principal) con el texto original pre-cargado + hint "Refiná el draft sin perder contexto". Enviar → el agente responde con versión iterada + badge "Iteration N".
  - `ChatComposer` al pie: input multilínea + área de pills activas (skills + agent handoff) + botón attach + botón send (⌘Enter). Placeholder rota entre 3 ejemplos contextuales.

- **Right column:**
  - `GroundedInBlock`: lista concreta de las 2-5 fuentes que el LLM usó, cada una con `sourceId · sourceVersion · line · score`. Hover en superscript `[E]` del mensaje → highlight aquí.
  - `SLABar`: p95 target vs actual con breach prediction si >= target*0.95.
  - "Active handoffs": lista de drafts creados durante esta conversación con chip de estado.

#### 3.2 Agent-level conversation (`#/chat/:conversationId` con agent locked)

Cuando el user entra al chat **desde** `agent-console` (botón "Abrir chat con este agente"), la conversación ya tiene ese agente pineado en cabecera y sus skills relevantes pre-activados. Esto cumple el requisito del patch: "si es una respuesta del agente podría hablar con ese agente relacionado".

Implementación: `#/chat/new?agent=ag_cotizador` crea conversación con `agentId` y pre-activa skills del agente.

---

### P0 · Nuevos widgets en `06_widgets.js.fragment`

**Editá el fragmento existente con marca `/* [V2-PATCH 2026-04-19] */` e incorporá:**

1. `ChatComposer({ conversationId, onSend, activeSkills, activeAgent })` — input multilínea + pills area + send. Soporta `Shift+Enter` para newline, `Enter` para send si pref simple o `⌘Enter` si multilínea (decidí con `localStorage.fl_enter_behavior`).
2. `IterationComposer({ messageId, originalText, onIterate })` — caja embebida bajo un message. Hint + textarea + botón "Iterar". Emite `iterate:request`.
3. `SkillPill({ skill, active, onToggle })` — pill clickeable con thermometer icon + nombre + (active) indicador ring.
4. `AgentChip({ agent, onRemove })` — chip con nombre + badge L0-L4 + X para remover handoff.
5. `GroundedInBlock({ sources })` — lista de fuentes. Cada una con `icon + title + version + §line + score bar`.
6. `MessageActionsMenu({ messageId, onAction })` — dropdown 8 acciones. Icon button compacto; abre al click con focus trap.
7. `PatternBadge({ kind: 'learned'|'gold'|'none', count?, rating? })` — chip pequeño esquina inferior derecha del message.
8. `VoiceOfCustomerCard({ quote, sentiment, source })` — tarjeta embebida en message cuando aplica.
9. `SuggestGrid({ items, onPick })` — grid 2×2 (o 3×1 mobile) con sugerencias contextuales; cada item con icon + título corto + 1-line hint.
10. `SLABar({ target, current, label })` — timer horizontal con color según breach prediction.

Todos deben seguir el contrato: función pura → devuelve HTML string (para compat con patrón actual de widgets). Side effects (focus trap, listeners) en una función `wireX` complementaria que se invoca post-mount.

---

### P0 · Mock data extensions en `05_mock_data.js.fragment`

**Append al final del fragmento con marca `/* [V2-PATCH 2026-04-19] */`:**

1. `conversations` — **8 conversaciones** diversas (2 cotizaciones activas · 1 consolidation · 2 sourcing · 1 customer support · 1 compliance · 1 archived). Cada una con `id`, `tenantId`, `agentId`, `activeSkills[]`, `title`, `startedAt`, `lastMessageAt`, `messageCount`.
2. `messages` — **~50 mensajes** distribuidos. Campos: `id`, `conversationId`, `role` (user|agent|system), `content`, `timestamp`, `evidenceSpans[]` (si role=agent), `draftIds[]` (si generó drafts), `patternBadge` (learned|gold|none, count, rating), `iterationOf` (messageId si es iteración), `modelFingerprint` (para agent messages).
3. `availableAgents` — **6 agentes** visibles en panel left. Ya existen 7 en `agents[]`; crear derivación `availableAgents = agents.filter(a => a.status !== 'archived')` con `runsLast7d` y `sparklineData`.
4. `availableSkillsForChat` — **12 skills** con `{ id, name, icon, learningHeat: 'cold'|'warm'|'hot'|'gold', description, requiredRole }`. Incluir Cotizar (hot), Sourcing (warm), Email draft (cold), Consolidate (gold), Compliance check (cold), etc.
5. `knowledgeHeatSamples` — **6 muestras** grounded-in por tipo de query. Cada una con `queryPattern`, `sources[]` (cada fuente con sourceId, title, version, lineRange, score 0-1).
6. `voiceOfCustomerSamples` — **4 quotes** para embed en message cuando aplica. `{ quote, sentiment: 'positive'|'neutral'|'negative', sourceCustomer, sourceCallId, date }`.

---

### P0 · Shell edit en `04_shell.html.fragment`

**Una sola edición quirúrgica:**

Añadir al principio del grupo "Principal" (antes de "Bandeja"):

```html
<a href="#/chat" class="fl-nav-link" data-route="chat" data-i18n="nav.chat">Chat</a>
```

**Nota:** mantener "Bandeja" como 2da entrada.

---

### P0 · Boot edits en `03_boot.js.fragment`

**Ediciones quirúrgicas:**

1. Registrar rutas `/chat` y `/chat/:id` apuntando al módulo `chat`.
2. Cambiar default hash de `#/bandeja/dr_001` → `#/chat` (primera impresión conversacional).
3. Añadir keybindings globales (no interferir con ⌘K existente):
   - `⌘E` → si hay un message del agente en viewport, abrir IterationComposer sobre el último.
   - `⌘A` → `location.hash = '#/agentes/ag_cotizador'`.
   - `⌘B` → `location.hash = '#/bandeja'`.
   - `⌘/` → toggle skill search en left column del chat.
4. Manejar `#/chat/new?agent=ag_XXX&skill=sk_YYY` para crear conversación con contexto pre-cargado.

---

### P0 · i18n keys (ES/EN/PT simétrico)

**Añadir dominios nuevos a `07_i18n_{es,en,pt}.js.fragment`:**

- `nav.chat` → "Chat" / "Chat" / "Chat"
- `chat.*` (~40 keys): `empty_title`, `empty_subtitle`, `composer_placeholder_1..3`, `send`, `attach`, `active_skills`, `handoff_to`, `iterate_this_draft`, `iterate_hint`, `iterate_n`, `grounded_in_title`, `grounded_in_empty`, `sla_p95_label`, `sla_p95_breach_warn`, `active_handoffs`, `always_on_title`, `always_on_personal`, `always_on_org`, `agents_title`, `skills_title`, `suggest_1..4_title`, `suggest_1..4_hint`, etc.
- `pattern.learned` → "Pattern learned · {count} runs" / etc.
- `pattern.gold` → "Gold sample · {rating}/10"
- `pattern.none` → "No pattern yet"
- `voc.title` → "Voice of customer"
- `voc.sentiment_positive|neutral|negative`
- `message_actions.copy|iterate|handoff|open_draft|explain_evidence|consolidate|feedback|rerun`
- `iteration.n_of_m` → "Iteration {n} of {m}"

**Total objetivo:** +130 keys × 3 idiomas = +390. Suma con los ~200 actuales → ~590 keys. Cubre y rebasa el target 332+.

---

### P1 · Cierre de brechas en módulos existentes

#### 3.7 Bulk approve en `10_module_bandeja_lista.html.fragment`

Añadir checkbox por row + toolbar superior sticky con botón "Aprobar seleccionados (N)" que dispara flow: si alguna tiene `reversibility: irreversible_cost` → modal double-confirm. Si todas reversibles → confirm simple + éxito bulk.

#### 3.8 "Grounded in" block en `11_module_bandeja_detail.html.fragment`

No reemplazar tab Evidence; añadir al panel derecho (antes de Risk) un `GroundedInBlock` compacto con top-3 sources. Link "Ver todas" salta a tab Evidence.

#### 3.9 Pattern badges en `12_module_skill_studio.html.fragment`

Añadir `PatternBadge` en cada row del layer "aprendido" mostrando count/rating. Layer "base sellada" → badge `kind: 'sealed'` distinto (🔒).

#### 3.10 Tab Conversación en `13_module_agent_console.html.fragment`

Añadir 5ta tab "Conversación" con botón prominente "Abrir chat con este agente" que hace `location.hash = '#/chat/new?agent=' + agentId`.

#### 3.11 Admin-users edit flow en `20_module_admin_users.html.fragment`

"Editar" debe abrir modal con: rol (select), departamento (multiselect), business_entities (multiselect), break-glass toggle con countdown 8h visible si activo, scope knowledge default (select 4 opciones). Save → toast "Cambios guardados" + append a auditEvents.

#### 3.12 Admin-knowledge promote flow en `21_module_admin_knowledge.html.fragment`

"Promote" abre modal 3 pasos:
- Paso 1: Preview del chunk + diff vs. versión actual.
- Paso 2: Checklist sanitización (sin PII · sin credentials · scope asignado · TTL definido).
- Paso 3: Confirm → append a auditEvents con `action: knowledge.promoted`.

#### 3.13 Admin-connectors config flow en `24_module_admin_connectors.html.fragment`

"Configurar" abre modal con 3 tabs: Credentials · Scope · Test connection. Test → simula latencia 800ms + toast.

---

### P2 · Verificación sistemática

#### 3.14 Checklist 30 AC

Crear `verification/AC_v2.md` con los 30 acceptance criteria originales + evaluación binaria Pass/Fail/Partial. Ejecutar DOM queries + axe-core para cada uno.

#### 3.15 Matriz trazabilidad 60 rows

Crear `verification/trazabilidad_v2.md` con 60 rows mapeando: requirement (prompt origin) → fragment → widget/data/route → status (green/yellow/red) → nota.

#### 3.16 axe-core export

Modificar el botón "Validar" del topbar para opcionalmente exportar resultados a `verification/axe_report_YYYY-MM-DD_HHmm.md` (via download blob) además del toast actual. Runnear en las 16 rutas (14 originales + 2 nuevas de chat) y committear el MD.

---

## 4. Fragmentos a crear / editar (tabla cerrada)

| # | Fragmento | Acción | Volumen estimado |
|---|---|---|---|
| 03 | `03_boot.js.fragment` | **EDIT** (rutas chat + keybindings + default hash) | +40 líneas |
| 04 | `04_shell.html.fragment` | **EDIT** (add Chat nav item) | +1 línea |
| 05 | `05_mock_data.js.fragment` | **EDIT** (append 6 colecciones nuevas) | +250 líneas |
| 06 | `06_widgets.js.fragment` | **EDIT** (append 10 widgets nuevos + wireX) | +400 líneas |
| 07 ES | `07_i18n_es.js.fragment` | **EDIT** (append ~130 keys) | +130 líneas |
| 07 EN | `07_i18n_en.js.fragment` | **EDIT** (mirror) | +130 líneas |
| 07 PT | `07_i18n_pt.js.fragment` | **EDIT** (mirror) | +130 líneas |
| 10 | `10_module_bandeja_lista` | **EDIT** (bulk approve) | +80 líneas |
| 11 | `11_module_bandeja_detail` | **EDIT** (Grounded in panel) | +40 líneas |
| 12 | `12_module_skill_studio` | **EDIT** (PatternBadge en rows) | +20 líneas |
| 13 | `13_module_agent_console` | **EDIT** (tab Conversación + botón) | +30 líneas |
| 17 | **`17_module_chat.html.fragment`** | **NEW** | ~600 líneas |
| 20 | `20_module_admin_users` | **EDIT** (edit flow modal) | +80 líneas |
| 21 | `21_module_admin_knowledge` | **EDIT** (promote 3-step flow) | +100 líneas |
| 24 | `24_module_admin_connectors` | **EDIT** (config modal) | +70 líneas |
| — | `verification/AC_v2.md` | **NEW** | ~150 líneas |
| — | `verification/trazabilidad_v2.md` | **NEW** | ~150 líneas |
| — | `verification/axe_report_*.md` | **NEW** | var |

**Fragmentos NO TOCADOS:** 00, 01, 02, 14, 15, 16, 22, 23, 30, 31, 99. Si la v2 necesita alterar uno de estos, **preguntar antes**.

---

## 5. Aceptación binaria v2 (20 AC)

Correr al final y devolver tabla con Pass/Fail + evidencia (screenshot DOM query o línea de código):

1. [ ] Al abrir `index-standalone.html` la ruta por defecto es `#/chat` y se ve el layout 3 columnas.
2. [ ] Left column muestra Always-on (Personal+Org con 🔒), 6 agents, 12 skills con thermometers.
3. [ ] Click en skill → pill aparece en composer; 2do click → desaparece.
4. [ ] Click en agent → AgentChip en composer + cabecera "Hablando con:".
5. [ ] Empty state del center muestra SuggestGrid 2×2 con 4 sugerencias clickeables.
6. [ ] Enviar mensaje → agent responde con message que tiene MessageActionsMenu + PatternBadge + superscripts `[E1]..[En]`.
7. [ ] Hover en superscript `[E1]` → right column GroundedInBlock highlight la fuente correspondiente.
8. [ ] Click "Iterate" en MessageActionsMenu → IterationComposer aparece debajo del message (no el composer principal).
9. [ ] Enviar iteración → nuevo message con badge "Iteration 1 of N".
10. [ ] Message con draft muestra pill `Draft dr_XXX · awaiting_approval` que linkea a `#/bandeja/dr_XXX`.
11. [ ] Right column muestra SLABar con p95 target vs current.
12. [ ] Agent console tiene 5ta tab "Conversación" con botón que salta a `#/chat/new?agent=ag_XXX` y al llegar ya tiene ese agente pineado.
13. [ ] Bandeja lista tiene checkboxes por row + "Aprobar seleccionados" con double-confirm si alguna es irreversible.
14. [ ] Bandeja detail tiene GroundedInBlock compacto con top-3 sources + "Ver todas".
15. [ ] Skill studio muestra PatternBadge en cada row del layer aprendido.
16. [ ] Admin-users "Editar" abre modal con rol/dept/BE/break-glass/scope + save emite auditEvent.
17. [ ] Admin-knowledge "Promote" abre flow 3-step (preview → sanitize → confirm).
18. [ ] Admin-connectors "Configurar" abre modal 3 tabs (creds/scope/test).
19. [ ] `verification/AC_v2.md`, `trazabilidad_v2.md`, y al menos 1 `axe_report_*.md` están commiteados con resultados reales.
20. [ ] i18n total ≥ 332 keys simétricos × 3 idiomas (verificar conteo en los 3 archivos).

---

## 6. Fases de ejecución recomendadas (sub-agent distribución)

**Fase A (paralela, 2 sub-agents):**
- SA1: mock data `05_*` (6 colecciones) + i18n `07_{es,en,pt}` (3 archivos simétricos).
- SA2: widgets `06_*` (10 widgets + wireX + estilos).

**Fase B (serial, main thread):**
- Shell `04_*` (1 línea).
- Boot `03_*` (rutas + keybindings + default).
- Módulo chat nuevo `17_*` (depende de widgets + mock + i18n).

**Fase C (paralela, 3 sub-agents):**
- SA3: Bandeja lista bulk approve + Bandeja detail Grounded in.
- SA4: Agent console tab Conversación + Skill studio PatternBadge.
- SA5: Admin edits (users + knowledge + connectors).

**Fase D (serial, main thread):**
- `build.py` → `index-standalone.html`.
- Verificación: 20 AC + 60-row trazabilidad + axe-core en 16 rutas.
- Commit + DELIVERY_NOTES_v2.md.

---

## 7. Entregables finales

```
MWT KB/faberloom-mockup/
├── index-standalone.html          ← REBUILD con todo el patch
├── DELIVERY_NOTES_v2.md           ← Nuevo (versión 2)
├── fragments/
│   ├── 03_boot.js.fragment        ← EDITED
│   ├── 04_shell.html.fragment     ← EDITED (1 línea)
│   ├── 05_mock_data.js.fragment   ← EDITED (append)
│   ├── 06_widgets.js.fragment     ← EDITED (append)
│   ├── 07_i18n_es.js.fragment     ← EDITED
│   ├── 07_i18n_en.js.fragment     ← EDITED
│   ├── 07_i18n_pt.js.fragment     ← EDITED
│   ├── 10_module_bandeja_lista    ← EDITED
│   ├── 11_module_bandeja_detail   ← EDITED
│   ├── 12_module_skill_studio     ← EDITED
│   ├── 13_module_agent_console    ← EDITED
│   ├── 17_module_chat.html.fragment  ← **NEW**
│   ├── 20_module_admin_users      ← EDITED
│   ├── 21_module_admin_knowledge  ← EDITED
│   └── 24_module_admin_connectors ← EDITED
└── verification/                  ← NEW DIR
    ├── AC_v2.md
    ├── trazabilidad_v2.md
    └── axe_report_2026-04-19_*.md
```

**DELIVERY_NOTES_v2.md** debe incluir, al final:
- Tabla Pass/Fail de los 20 AC con evidencia.
- Conteo exacto de keys i18n por idioma.
- Diff resumen vs. v1 (archivos tocados, líneas añadidas, línea neta).
- Próximas brechas honestas si alguna quedó abierta.

---

## 8. Prohibiciones explícitas

- ❌ No introducir dependencias nuevas (ni CDN, ni npm, ni fetch).
- ❌ No cambiar el contrato `fragments → build.py → index-standalone.html`.
- ❌ No mover ni renombrar fragmentos existentes.
- ❌ No romper rutas existentes.
- ❌ No tocar `research/A1..A6`. Si querés añadir, creá `research/A7_chat_patterns.md`.
- ❌ No eliminar features de v1.
- ❌ No usar `localStorage` para data persistente de demo (solo para prefs como theme/lang).
- ❌ No reescribir widgets existentes; solo añadir.

---

## 9. Ejecutá y devolveme

1. El path absoluto al `index-standalone.html` regenerado.
2. El resultado de los 20 AC en tabla.
3. Los 3 archivos de `verification/`.
4. `DELIVERY_NOTES_v2.md`.
5. Git diff resumen (archivos tocados, +líneas, -líneas).

Si encontrás contradicción entre este prompt y el SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md → gana SPEC, flag la contradicción en notes. Si encontrás contradicción con research/A1..A6 → gana research, flag. Si encontrás gap donde no hay canon → usá judgment, flag en `DELIVERY_NOTES_v2.md §Decisiones autónomas`.

Arrancá.
