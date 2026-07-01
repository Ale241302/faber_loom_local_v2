# FaberLoom — Stitch Prompt Master + Design System
## Versión 1.0 · 2026-04-15

---

## SÍNTESIS DE PRODUCTO (lo que entendí antes de escribir el prompt)

FaberLoom no es un inbox con IA. Es un sistema operativo de conocimiento experto para equipos B2B.
Su núcleo es una base de conocimiento canónica, versionada y con control de visibilidad estricto —
no el modelo de lenguaje. Los skills son módulos de criterio especializado que razonan *sobre* ese
conocimiento para producir outputs concretos: propuestas, respuestas, análisis. El contexto vive en
casos y contactos, no en hilos de chat. La voz se adapta por usuario y destinatario mediante perfiles
configurados. Nada sale al exterior sin aprobación humana explícita.

La jerarquía de diseño está dictada por el Marco Rector: integridad del conocimiento > corrección de
visibilidad > calidad contextual > coherencia del skill > voz. Speed y UX son los últimos en la lista.
Eso define el tipo de interfaz: seria, estructurada, con gobernanza visible, no veloz y chatty.

Visualmente es más cercano a un sistema operativo de trabajo experto (Linear + Craft + Intercom Admin)
que a un inbox (Superhuman, Gmail) o a un chatbot (ChatGPT, Claude.ai).

---

## PARTE 1 — PROMPT MAESTRO PARA STITCH

---

```
Design a B2B enterprise SaaS application called FaberLoom.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT FABERLOOM IS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FaberLoom is a knowledge-first AI work platform for B2B operators. Its central thesis:
any person in the organization should be able to produce a correct output —
aligned with the company's operational truth, adapted to the specific case and
recipient — without depending on another person being available to validate what
to say, how to say it, or to whom.

The system is organized around a verified, versioned knowledge base (the "KB") as
its single source of truth. Channels (email, tasks) are surfaces. Skills are
specialized reasoning modules that apply KB knowledge to specific tasks. Context
lives in Cases and Contacts, not in chat threads. Voice profiles adapt tone per
user and per recipient. Nothing goes external without explicit human approval.

This is not a chatbot. It is not an AI inbox. It is not a generic CRM dashboard.
It is an expert work operating system with strict governance.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THE PROBLEM IT SOLVES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

B2B operators (sales reps, account managers, legal, operations, partnerships)
constantly produce outputs that require specialized knowledge: proposals, contract
responses, technical answers, follow-ups. Currently that knowledge lives in
different people's heads, old documents, and scattered tools. Outputs are
inconsistent, slow, and dependent on institutional memory.

FaberLoom solves this by structuring operational knowledge as a verified KB,
then making it actionable through skills, and governable through visibility
policies and human approval gates. The output is always grounded, traceable,
and auditable.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHO THE USERS ARE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Primary: B2B operators — sales reps, account managers, business development,
operations managers, legal/compliance coordinators. Not developers. Not consumers.
People who produce knowledge-intensive work outputs every day.

Secondary: Administrators (KB managers, team leads who approve outputs, configure
visibility rules and skill scopes).

These users work with dense information, care about accuracy and accountability,
and will distrust any system that feels like it's improvising. They need the
interface to communicate reliability, not cleverness.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOW THE INTERFACE MUST FEEL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Authoritative. Precise. Trustworthy before beautiful.

Think: a well-engineered cockpit for knowledge workers. The interface should
communicate that the system knows what it's doing and why. Every piece of AI-
generated content must make its sources visible. Every output must show its
approval state. The system should feel like it has memory, structure, and rules —
not like it's guessing.

Color communicates state, not mood. Structure communicates reliability. Density
is a feature: these users handle real information, not simplified cards.

The closest visual references: Linear (density, structure, keyboard-friendly),
Intercom Inbox (three-panel layout with inspector), Notion-as-database (organized
knowledge), Craft (premium typographic feel) — but stripped of consumer-grade
softness and governed by enterprise-grade hierarchy.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT IT MUST NOT LOOK LIKE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DO NOT build this as:
- A chat interface. No centered text input box as the main UI element.
- An email inbox (no Superhuman/Gmail-style message list as primary view).
- A generic dashboard with KPI charts as the hero screen.
- A Slack-like messaging tool.
- A Notion-like free-form document editor.
- A consumer AI assistant (no "Hi! What can I help you with today?").
- A CRM with a pipeline kanban board.
- A tool that hides governance and sourcing behind clean-looking output cards.

The absence of visible governance is a red flag in this product. If the interface
doesn't show where knowledge came from, what visibility tier applies, and who
approved what — it has failed its core promise.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MAIN MODULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CASES — The primary organizing unit. A Case has: associated contact/organization,
   loaded KB context, active skills, generated drafts, approval history, notes.
   A Case is the workspace. Everything else serves the Case.

2. KNOWLEDGE BASE — The canonical truth store. Organized by domain (Sales, Ops,
   Legal, Product, etc.). Each entry is versioned, has a validity date, a
   visibility tier (PUBLIC / PARTNER_B2B / INTERNAL / CEO-ONLY), and a confidence
   level. Never editable mid-session — changes go through an approval flow.

3. SKILLS — Specialized reasoning modules. Examples: "Draft Proposal", "Respond to
   Objection", "Analyze Contract", "Summarize Case", "Generate Follow-up". Each
   skill declares its required KB scope, authority mode (SEÑALA / PROPONE /
   EJECUTA CON APROBACIÓN / EJECUTA SOLO), and required context inputs.

4. APPROVALS — A queue of AI-generated outputs pending human review before any
   external send. Shows diff of proposed vs. previous, source attribution, skill
   used, confidence, and visibility tier. Approve / Edit / Reject actions.

5. CHANNELS — Email (primary in MVP). The surface where approved outputs go.
   Not the primary view. Accessed from Cases, not as a standalone inbox.

6. VOICE PROFILES — Per-user and per-recipient communication style configuration.
   Formality level, preferred vocabulary patterns, tone rules. Shown as an active
   indicator on every draft ("Voice: Álvaro → CEO Bancolombia · Formal / Technical").

7. CONTACTS & ORGANIZATIONS — Not a CRM. Profiles that carry: communication
   history, relevant KB snippets, active cases, voice profile overrides, and
   visibility tier assignments.

8. AUDIT TRAIL — Full history of what was generated, approved, modified, and sent.
   Immutable log. Agent attribution, timestamps, KB sources used, skill invoked,
   who approved. This screen communicates the system's integrity.

9. ADMIN / GOVERNANCE — Visibility rules, KB domain permissions, skill scope
   configuration, user roles, nightly maintenance review queue.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRIMARY SCREENS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Build these screens as the core prototype:

1. COMMAND CENTER — Not a chart dashboard. A structured overview: pending
   approvals queue, active cases with last activity, recent KB conflicts to
   resolve, scheduled nightly review status. Dense table-first layout.

2. CASE DETAIL — The hero screen. THREE-PANEL LAYOUT:
   LEFT PANEL (Context): Loaded KB snippets with source + visibility labels.
   Active contact profile summary. Previous outputs in this case.
   CENTER PANEL (Work Area): Active skill output generating in real-time.
   Draft editor with inline source markers. Approve/Send controls.
   RIGHT PANEL (Inspector): Confidence breakdown per KB source used. Visibility
   tier applied. Voice profile active. Skill logic summary. Audit trace for
   this output.

3. CASES LIST — Dense table view. Columns: Case name, Contact/Org, Status
   (Active/Pending Approval/Closed), Last Activity, Skills Used, Owner.
   Filterable by domain, status, assignee. Keyboard-navigable.

4. KB BROWSER — Left sidebar with domain tree. Main area: table of knowledge
   entries with columns: Title, Domain, Visibility Tier, Valid Until, Status
   (ACTIVE/CONFLICT/EXPIRED), Last Updated. Click to expand entry.

5. KB ENTRY DETAIL — Full document view with: header metadata (version, domain,
   visibility, validity), content with section markers, related entries panel,
   edit history, active conflicts flagged inline, skills that use this entry.

6. SKILLS CATALOG — Grid or table of available skills. Each skill card shows:
   Name, Domain, Authority Mode (SEÑALA/PROPONE/EJECUTA/AUTO), KB Scope required,
   estimated output type, last used. Click to open skill detail or invoke from
   a Case.

7. APPROVAL QUEUE — Dedicated screen. List of pending approvals ordered by
   priority. Each item shows: output type, case reference, skill used, requestor,
   time in queue. Click to open approval drawer with full diff view.

8. APPROVAL DETAIL (DRAWER) — Slides from right. Shows: full draft, inline source
   attribution badges, voice profile applied, visibility tier, KB confidence summary,
   skill trace. Actions: Approve / Edit & Approve / Reject with reason.

9. CONTACT PROFILE — Three-section layout: Profile header (name, org, tier,
   voice override), Active Cases with this contact, Communication History
   (approved and sent outputs). KB snippets tagged to this contact visible in
   sidebar.

10. AUDIT TRAIL — Immutable timeline. Filterable by: date range, user, skill,
    case, KB entry affected. Each row expandable to show full trace: what was
    generated, what KB sources were used, who approved, what changed from draft
    to final, when sent.

11. VOICE PROFILE SETUP — Form-based configuration screen. Left: sender profile
    fields (formality, vocabulary preferences, tone markers). Right: live preview
    showing how a sample output changes as settings are adjusted.

12. ADMIN / GOVERNANCE — Tabbed: KB Domains & Visibility Rules / User Roles &
    Permissions / Skill Scopes / Nightly Review Configuration. No charts.
    Table-based configuration with explicit save/publish actions.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HERO FLOW — WHAT MUST FEEL MOST NATURAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

START HERE when generating the prototype:

User opens Case "Propuesta Q2 – Bancolombia".
LEFT PANEL shows: 3 loaded KB snippets with visibility badges (PARTNER_B2B).
Contact profile: CEO, Formal/Technical voice override active.
User clicks "Invocar Skill" → selects "Draft Proposal" from a compact picker.
CENTER PANEL activates: skill streaming output in real-time, each sentence
appearing with a source badge attached (e.g., "§ KB · Catálogo Producto · HIGH").
Output completes. An amber banner appears: "1 section used inference outside KB
scope. Review required."
User clicks the banner → right panel inspector highlights the inferred section
with a "NOT FROM KB" warning chip and a recommended KB entry to reference.
User accepts edit suggestion. Banner clears. Green "Ready for Approval" state.
User clicks "Submit for Approval" — draft moves to Approval Queue.
Approver receives notification. Opens Approval Detail drawer.
Sees full draft, source badges, voice match indicator (92% match to profile),
visibility tier confirmed (PARTNER_B2B - no CEO-ONLY content injected).
Approver clicks "Approve". Output status changes to APPROVED.
System sends to email channel. Audit entry created with full trace.

This flow must be buildable as a clickable prototype with the three-panel Case
Detail as the primary hero screen. Priority: show governance, source attribution,
and approval state as first-class visual elements — not as secondary tooltips.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VISUAL HIERARCHY & DESIGN LANGUAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Typography hierarchy (in order of visual weight):
1. Screen title / section header — 18-20px, medium weight, high contrast
2. Table headers / field labels — 11-12px, uppercase, tracked, muted
3. Content body — 13-14px, regular weight, high contrast
4. Metadata / timestamps — 11-12px, muted, no decoration
5. Monospace — KB references, technical content, agent IDs

Color system — semantic, not decorative:
- Background: zinc-950 (dark base) OR zinc-50 (light base) — pick one
- Surface: zinc-900 / zinc-100
- Border: zinc-800 / zinc-200 (subtle, not heavy)
- Primary action: indigo-600 (trust, intentionality)
- Approved / Verified: emerald-500 (confidence, cleared)
- Warning / Needs Review: amber-500 (review required, not blocking)
- Blocked / Critical: red-500 (hard stop)
- AI-generated marker: violet-400/violet-600 (distinct, visible)
- CEO-ONLY visibility marker: deep orange / rose (maximum salience)
- INTERNAL: blue-slate neutral chip
- PARTNER_B2B: teal chip
- PUBLIC: neutral/gray chip

Component style decisions:
- NO heavy shadows or gradients on UI chrome
- Subtle 1px borders on cards and panels
- Tables preferred over card grids for dense list views
- Compact row height (38-44px) for table rows — these are operators, not consumers
- Chips/badges for all state and visibility labels — never plain text
- Drawers preferred over modals for detail views (preserve context)
- Modals ONLY for irreversible confirmations (approve, delete, override)
- Collapsible side panels (not tabs) for inspector/sources view
- Inline "source badge" on AI-generated content:
  [§ KB · Domain · HIGH] — small pill attached to the relevant sentence or section

Navigation structure:
- LEFT SIDEBAR: persistent, icon + label, collapsible to icon-only
  Items: Cases · KB · Skills · Approvals · Contacts · Audit Trail · Admin
- TOP BAR: Workspace/org name (left), search (center), notifications + user (right)
  Active module name shown in top bar, not in page body
- RIGHT INSPECTOR: slides in contextually from right edge, not a tab

Information density:
- HIGH in Case Detail (three panels, sources, inspector)
- MEDIUM-HIGH in KB Browser and Audit Trail (dense tables, expandable rows)
- MEDIUM in Command Center (structured, not heavy)
- LOW in Voice Profile Setup and Admin (form-based, clear fields)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GOVERNANCE, WARNINGS, BLOCKS & TRUST ELEMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Warnings (amber, non-blocking):
- Inline amber banner below draft when inference was used outside KB scope
- Row-level amber chip in KB table when a knowledge entry has a conflict flag
- "Expires in 7 days" chip on KB entries approaching validity end

Blocks (red, hard stops):
- Red bordered panel when a visibility violation is detected (CEO-ONLY content
  in a PARTNER_B2B draft)
- Skill execution blocked: "Required KB scope not available for your role"
- Output locked until block resolved — no bypass action visible to base users

Approvals (green, gated):
- Every AI output in "Work Area" shows an "Approval Required" state until cleared
- Approval state shown as a persistent status chip: [⏳ Pending] [✓ Approved] [✗ Rejected]
- Approval drawer shows diff-style comparison when approver edits a draft

Trust / Confidence elements:
- Source attribution badge on every AI-generated sentence or paragraph
  Format: [§ KB · Domain Name · CONFIDENCE] where CONFIDENCE = HIGH / MEDIUM / INFERRED
- "NOT FROM KB" warning chip when model generated content without KB source
- Voice match indicator: percentage match to active voice profile
- Visibility tier badge on every output and KB entry (color-coded chips)
- Skill used: visible in output header, not buried in metadata
- Agent ID: shown in audit trail (which agent executed, which mode)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EMPTY, ERROR & LOADING STATES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Empty Case (no context loaded):
- Center panel shows a structured action prompt: "Load KB context", "Add contact",
  "Select skill to begin" — not a generic "no data" illustration
- Each action links directly to the relevant module

Empty KB Domain:
- "No knowledge entries for this domain yet" + primary action button to add first
  entry — no illustration, no copy about how great the feature is

Loading a Skill (consulting KB):
- Skeleton lines in center panel with progress step indicator:
  Step 1: "Retrieving KB context" → Step 2: "Applying skill logic" → Step 3: "Generating draft"
- Each step shown with a subtle animated indicator

Error states:
- Specific error messages only. Never "Something went wrong."
- Examples: "KB retrieval failed — entry KB-042 is expired. Update required before
  proceeding." / "Visibility conflict: draft contains CEO-ONLY content. Cannot
  send to PARTNER_B2B recipient."
- Error messages always include: what failed, why, and what action resolves it

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INTERACTIONS THAT MUST FEEL FLUID
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- KB snippet → drag into Case context panel (or click-to-add with single action)
- Skill output streams in real-time (token by token or sentence by sentence)
  with source badges appearing as content generates
- Approval drawer slides from right with smooth transition, preserving Case view
- Collapsible inspector panel expands/collapses without losing scroll position
- Keyboard navigation: j/k for table rows, Enter to open, Esc to close drawer
- Inline editing in approval drawer: click any section to edit, change tracked
- Source badge hover: expands to show full KB entry title, version, validity

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT STITCH SHOULD BUILD FIRST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Priority 1 (build fully): Case Detail — the three-panel hero screen.
This screen alone demonstrates the core value proposition of FaberLoom. It should
show: loaded KB context with visibility badges, a skill output in progress with
source attribution, the inspector panel with confidence breakdown, and a clear
approval state on the draft.

Priority 2 (build as skeleton): Command Center (with pending approvals widget),
Cases List (dense table), and KB Browser (domain tree + entry table).

Priority 3 (build as wireframe): Approval Detail drawer, Audit Trail, and
Voice Profile Setup.

Use real-looking placeholder data. Show "Bancolombia", "Propuesta Q2", actual
KB domain names like "Política Comercial · PARTNER_B2B", skill names like
"Draft Proposal · PROPONE mode". No Lorem Ipsum. No "Example Inc." placeholders.
The data should make the governance and context elements feel meaningful.
```

---

## PARTE 2 — SCREEN MAP

| # | Pantalla | Propósito | Usuario principal | Info dominante | Acciones clave | Estados críticos |
|---|----------|-----------|-------------------|----------------|----------------|------------------|
| 1 | **Command Center** | Vista general operativa de trabajo pendiente | Operador, Manager | Aprobaciones pendientes · Casos activos · Conflictos KB · Estado nightly | Abrir aprobación · Ir a caso · Resolver conflicto | Empty (sin actividad) · Conflicto urgente (red banner) |
| 2 | **Case Detail** | Pantalla de trabajo principal — 3 paneles | Operador | KB context cargado · Output del skill · Inspector (fuentes, confianza, visibilidad) | Invocar skill · Editar draft · Enviar a aprobación · Aprobar | Draft sin fuentes (warning) · Bloqueo de visibilidad · Listo para aprobar |
| 3 | **Cases List** | Inventario de casos activos/cerrados | Operador, Manager | Tabla: Caso · Contacto · Estado · Última actividad · Skills usados | Nuevo caso · Filtrar · Ordenar · Abrir caso | Vacío (primer uso) · Muchos pendientes (badge de conteo) |
| 4 | **KB Browser** | Explorar y gestionar el conocimiento canónico | Admin, Manager | Árbol de dominios (izq.) · Tabla de entradas (cen.) · Metadata (der.) | Añadir entrada · Editar · Marcar conflicto · Archivar | Entradas expiradas · Conflictos activos (amber chip) |
| 5 | **KB Entry Detail** | Ver/editar una pieza de conocimiento canónica | Admin | Contenido documentado · Metadata (versión, vigencia, visibilidad) · Conflictos inline · Skills que la usan | Editar · Aprobar conflicto · Ver historial | EXPIRED · CONFLICT (marcado en rojo/amber) · FROZEN (no editable) |
| 6 | **Skills Catalog** | Explorar e invocar skills disponibles | Operador | Grid/tabla: Nombre · Dominio · Modo de autoridad · KB Scope · Última ejecución | Invocar desde caso · Ver detalle del skill · Configurar | Skill sin KB suficiente (disabled) · Modo EJECUTA SOLO (alerta de autonomía) |
| 7 | **Approval Queue** | Cola de aprobaciones pendientes | Aprobador, Manager | Lista ordenada: Output type · Caso · Skill usado · Tiempo en cola · Solicitante | Abrir aprobación · Filtrar por tipo · Priorizar | Cola vacía · Cola crítica (+10 pendientes) |
| 8 | **Approval Detail (Drawer)** | Revisar, editar y aprobar un output antes de envío | Aprobador | Draft completo · Badges de fuente inline · Indicador de voice match · Visibility tier | Aprobar · Editar & Aprobar · Rechazar con razón | Bloqueo de visibilidad · Sección sin fuente KB (NOT FROM KB) |
| 9 | **Contact Profile** | Perfil de contacto/organización con historial | Operador | Header del contacto · Casos activos · Historial de outputs enviados · KB snippets asociados | Nuevo caso · Ver output enviado · Editar perfil de voz | Sin casos (nuevo contacto) · Conflicto de tier con organización |
| 10 | **Audit Trail** | Trazabilidad total e inmutable del sistema | Admin, Manager | Timeline filtrable: acción · skill · caso · KB usado · aprobador · timestamp | Filtrar · Expandir entrada · Exportar rango | Sin actividad · Anomalía detectada (flag automático) |
| 11 | **Voice Profile Setup** | Configurar voz del remitente y overrides por destinatario | Operador, Admin | Campos de perfil (izq.) · Preview vivo de output (der.) | Guardar perfil · Añadir override por destinatario · Restaurar default | Sin configurar (default aplicado con warning) |
| 12 | **Admin / Governance** | Configurar reglas de visibilidad, roles, skills, mantenimiento | Admin | Tabs: Dominios KB · Roles · Skills · Nightly Review | Editar regla · Asignar rol · Configurar scope · Publicar cambio | Cambios no publicados (pending indicator) · Conflicto de reglas |

---

## PARTE 3 — DESIGN.md INICIAL

```markdown
# FABERLOOM — DESIGN.md
## Sistema Visual y Reglas UX · v1.0 · 2026-04-15

---

## PRINCIPIOS VISUALES

1. **Gobernanza como primer ciudadano**: Las etiquetas de visibilidad, confianza y estado
   de aprobación son elementos de UI de primer nivel, nunca tooltips secundarios.

2. **Densidad con jerarquía**: La densidad es una característica del producto, no un error.
   Pero densidad sin jerarquía es caos. Cada pantalla debe tener un elemento dominante claro.

3. **Colorimetría semántica**: El color comunica estado, no estética. No usar gradientes
   decorativos. No usar color como elemento de marca en chrome de UI.

4. **Estructura sobre decoración**: Sin sombras pesadas. Sin bordes redondeados excesivos.
   Sin ilustraciones vacías. Los elementos comunican por posición, peso tipográfico y color.

5. **Confianza antes que velocidad**: Si un elemento de gobernanza enlentece visualmente
   la interfaz, se mantiene. La velocidad de UX es la última prioridad del Marco Rector.

---

## PRINCIPIOS UX

1. **El contexto nunca se pierde**: Los drawers preservan la vista del caso. Los modales
   son solo para confirmaciones irreversibles. Jamás navegar fuera de un caso para ver
   un detalle que podría vivir en panel lateral.

2. **Aprobación humana como flujo estándar**: El estado "Pending Approval" es normal,
   no una excepción. La UI debe hacer que el flujo de aprobación sea tan rápido como sea
   posible — no que parezca un obstáculo.

3. **Las fuentes son parte del output**: No se puede leer un output de FaberLoom sin ver
   de dónde viene. Source badges son parte del componente de output, no opcionales.

4. **Acciones explícitas**: El sistema nunca ejecuta algo externo por sí solo, a menos
   que esté configurado como EJECUTA SOLO y el usuario lo haya visto en la configuración
   del skill. Toda acción de salida tiene un botón explícito.

5. **El error es informativo**: Mensajes de error con causa + acción. Nunca "error genérico".

---

## JERARQUÍA DE INFORMACIÓN

Por pantalla, el orden de lectura visual debe ser:

**Case Detail (pantalla principal):**
1. Nombre del caso + contacto + tier de visibilidad activo (header)
2. Estado del output actual (Pending / Ready / Blocked) — chip de estado
3. Contenido del draft con source badges inline
4. Context panel (KB cargado, snippets)
5. Inspector (confianza, voice match, trace)

**KB Browser:**
1. Dominio activo (sidebar)
2. Tabla de entradas con estado (ACTIVE / CONFLICT / EXPIRED)
3. Metadata de la entrada seleccionada

**Approval Queue:**
1. Número de pendientes (count badge en nav)
2. Items ordenados por tiempo en cola (más viejo primero)
3. Tipo de output + caso de referencia

---

## TONO DE LA INTERFAZ

- Directo. Sin microcopy excesivo. Sin "¡Excelente!" ni onboarding hablachín.
- Los estados vacíos describen la acción que falta, no el beneficio del feature.
- Los errores son técnicos y precisos. La causa importa más que el tono amable.
- El sistema se comunica como un colega experto, no como un asistente entusiasta.
- Los labels de UI son términos operativos: "Invocar Skill", "Enviar a Aprobación",
  "Cargar contexto KB" — no "Generate", "Send", "Load".

---

## ESTILO DE COMPONENTES

### Chips / Badges de estado

Todos los estados se expresan como chips de tamaño S (24px alto, 6-8px padding lateral):

| Estado | Color | Texto |
|--------|-------|-------|
| ACTIVE | emerald-500 bg leve | VIGENTE |
| EXPIRED | red-200 bg / red-700 text | EXPIRADO |
| CONFLICT | amber-500 | CONFLICTO |
| FROZEN | zinc-700 bg / zinc-300 text | FROZEN |
| DRAFT | zinc-500 bg leve | BORRADOR |
| APPROVED | emerald-600 | APROBADO |
| REJECTED | red-500 | RECHAZADO |
| PENDING | amber-400 | EN REVISIÓN |

### Chips de visibilidad

| Tier | Color |
|------|-------|
| PUBLIC | zinc-400 neutral |
| PARTNER_B2B | teal-600 |
| INTERNAL | blue-600/indigo-600 |
| CEO-ONLY | rose-600 (alta saliencia) |

### Source Badges (inline en outputs AI)

Formato: `[§ Nombre KB · Dominio · NIVEL]`

- HIGH: texto en emerald-600, fondo emerald-50 (dark: emerald-950)
- MEDIUM: texto en amber-600, fondo amber-50
- INFERRED / NOT FROM KB: texto en red-600, fondo red-50, icono de advertencia

Size: 10px texto, pill shape, aparece como superíndice visual o al final del párrafo.
Hover: expande a tooltip con título completo, versión, válido hasta, link a entrada KB.

### Tablas

- Row height: 40px para tablas densas, 52px para tablas con metadata secundaria
- Header: 11px uppercase tracked, zinc-500 color, sin background especial
- Hover state: background zinc-100/zinc-800 (sutil)
- Selected state: indigo-600 left border indicator (2px) + background indigo-50/indigo-950
- Expandable rows: chevron en columna izquierda, expansión inline (no drawer)
- Columna de acciones: visible solo en hover del row, alineada a la derecha

### Paneles laterales (Context Panel, Inspector)

- Width: 280px context, 320px inspector
- Collapsible con transición suave (200ms)
- Header del panel: 12px uppercase label + toggle collapse
- Contenido scrollable independiente del panel central
- Separador: border de 1px, sin sombra

### Drawers (Approval Detail, KB Entry quick view)

- Width: 560px (approvals), 480px (KB quick view)
- Overlay semitransparente en el resto de la pantalla
- Header: Tipo de documento + Caso de referencia + Cerrar
- Footer sticky con acciones primarias (Aprobar / Rechazar)
- Scroll interno independiente

### Modales

Usar SOLO para:
- Confirmación de aprobación final (irreversible)
- Confirmación de rechazo con campo de razón (obligatorio)
- Eliminación de entrada KB

Width: 440px max. Header con ícono semántico (warning/confirm). Dos acciones máximo.

---

## GRID Y LAYOUT

- Layout base: sidebar 220px (colapsable a 56px) + contenido principal
- Pantalla de 3 paneles (Case Detail): 280 | flex | 320
- Gutter mínimo entre paneles: 1px border (no gap visual pesado)
- Content area padding: 24px horizontal, 20px vertical
- Top bar: 52px de alto
- Responsive: no se adapta a mobile. Este es software desktop/web para operadores.
  Breakpoint mínimo soportado: 1280px.

---

## TIPOGRAFÍA SUGERIDA

- UI principal: Inter o Geist Sans (variable weight)
- Monospace (KB refs, IDs, código): Geist Mono o JetBrains Mono
- Tamaños: 12px (meta), 13px (body), 14px (body large), 16px (section title), 20px (screen title)
- No usar fuentes display ni serif. El tono es técnico, no editorial.

---

## DENSIDAD DE CONTENIDO

| Pantalla | Densidad | Justificación |
|----------|----------|---------------|
| Case Detail | Alta | Es el área de trabajo principal |
| KB Browser | Alta | Muchas entradas, mucha metadata |
| Audit Trail | Alta | Trazabilidad requiere volumen |
| Cases List | Media-alta | Lista de trabajo, no exploración |
| Command Center | Media | Resumen, no detalle |
| Approval Drawer | Media | Lectura + edición, no escaneo |
| Voice Profile | Baja | Configuración, no trabajo |
| Admin | Baja | Configuración estructurada |

---

## USO DE COLOR PARA ESTADO

**Regla maestra**: el color es siempre semántico. Nunca decorativo.

- Verde (emerald): completado, aprobado, verificado, vigente
- Ámbar (amber): requiere revisión, advertencia, próximo a expirar
- Rojo (red): bloqueado, expirado, rechazado, violación de visibilidad
- Índigo (indigo): acción primaria intencional, selección activa
- Violeta (violet): contenido AI generado (marcador de origen, no de calidad)
- Gris (zinc): estados neutros, metadatos, contenido inactivo

---

## COMPORTAMIENTO DE WARNINGS

Tipo 1 — Inline en output (ámbar, no bloqueante):
- Aparece como banner compacto (36px) sobre el draft
- Texto: descripción del problema + link "Ver sección"
- Dismissible solo tras resolución
- Icono: triángulo ámbar a la izquierda

Tipo 2 — Row-level en tabla (chip ámbar en columna de estado):
- No interrumpe flujo de trabajo
- Al hover: tooltip con descripción del conflicto
- Al click: abre KB Entry Detail con conflicto destacado

Tipo 3 — Sistema (estado de KB degradado, nightly fallido):
- Banner en top bar (no modal)
- Color ámbar o rojo según severidad
- Link a pantalla de Admin / Governance

---

## COMPORTAMIENTO DE BLOQUEOS

Bloqueo de visibilidad (más crítico):
- Border rojo de 2px alrededor del panel de draft
- Chip rojo "BLOQUEADO — Violación de visibilidad"
- Cuerpo del draft oculto (blur o replaced por mensaje de error)
- No hay acción de bypass visible para roles base
- Solo Admin puede ver el detalle del bloqueo y resolverlo

Bloqueo de KB incompleto:
- Skill deshabilitado con tooltip explicativo
- No aparece como error, aparece como estado de requisito no cumplido

---

## PATRONES ESPECÍFICOS

### Timeline (Audit Trail)
- Línea vertical de 1px en zinc-700
- Nodos circulares (8px) por evento
- Color del nodo según tipo: emerald=aprobación, violet=generación, amber=warning, red=rechazo
- Timestamp en columna fija a la izquierda
- Descripción del evento expandible (click en row)

### Cards de Skill
- Compact: 100% width en lista, 2-col en grid
- Header: Nombre skill + Modo de autoridad (chip)
- Body: KB Scope requerido (chips de tier) + Dominio
- Footer: "Última ejecución hace X días" + botón "Invocar"
- Estado disabled: opacidad 60% + tooltip de requisito

### KB Snippet en Context Panel
- Compact card (no expandida por defecto)
- Header: Nombre del documento + Dominio + Tier de visibilidad
- Body: Primeras 2-3 líneas del chunk relevante
- Footer: Confianza chip + "Ver completo"
- Acción: click expande inline, no navega afuera del caso

### Indicador de Voice Match
- Barra horizontal con porcentaje (no número aislado)
- 0-70%: amber
- 70-90%: neutral
- 90-100%: emerald
- Tooltip: "Basado en X muestras del perfil de voz activo"
```

---

## PARTE 4 — CRÍTICA BRUTAL

### Lo que es visualmente claro y fácil de llevar a Stitch

**El flujo de aprobación** es el más limpio. Tiene entrada (draft pendiente),
proceso (drawer de revisión con diff y fuentes), y salida (aprobado/rechazado).
Es un patrón conocido en software enterprise y Stitch lo puede generar bien.

**La tabla de KB** también es directa: árbol de dominios + tabla con metadata + estado.
Es un patrón de explorador de archivos con gobernanza. Stitch puede representarlo sin ambigüedad.

**El Audit Trail** es trivial de representar: timeline con filtros. Aburrido de diseñar,
pero limpio de especificar. Stitch lo maneja bien.

---

### Lo que está ambiguo y hay que decidir antes de entrar a Stitch

**1. La relación entre Cases y Channel (Email)**
¿El email vive *dentro* del caso o el caso vive *dentro* del email? La arquitectura
dice "canales como superficies", pero la UX de un operador que recibe un email nuevo
y quiere crear un caso a partir de él no está definida. Decisión que tomar:
> *Recomendación*: FaberLoom NO tiene inbox propio en MVP. Los emails se crean desde casos.
> El único punto de entrada del email es "Nuevo caso → Template de email outbound".
> Inbound email se procesa como notificación, no como pantalla principal.

**2. ¿Cómo se "carga" el contexto KB en un caso?**
¿Es manual (el operador busca y agrega snippets)? ¿Es automático al abrir el caso
basado en el contacto/dominio? ¿Es semi-automático (el sistema sugiere, el usuario confirma)?
Esta decisión define completamente cómo se ve el Context Panel.
> *Recomendación*: Semi-automático. Al abrir un caso con contacto asignado, el sistema
> pre-carga los 3-5 snippets KB más relevantes (con chip "Auto-cargado"). El operador
> puede agregar más manualmente. Stitch puede mostrar esto como estado de carga inicial.

**3. Skill invocation UI**
¿Los skills son un menú desplegable? ¿Una barra de búsqueda tipo command palette?
¿Están siempre visibles como botones en el panel central? Esto cambia radicalmente
cómo se siente el flujo principal.
> *Recomendación*: Command palette (⌘K), con skills sugeridos basados en el contexto
> del caso activo. Los 2-3 más relevantes también visibles como botones en el panel central.

---

### Partes que corren riesgo de verse demasiado complejas

**El Inspector Panel (lado derecho del Case Detail)**
Si se intenta mostrar todo simultáneamente — confianza por fuente, voice match,
visibility tier, skill trace, KB entries usadas — el panel se convierte en noise visual.
> *Solución*: Tabs dentro del inspector: [Fuentes] [Voz] [Traza]. Por defecto muestra [Fuentes].
> El resto está a un click de distancia, no todo visible al mismo tiempo.

**Las reglas de visibilidad en Admin**
El Policy Engine es poderoso pero su UI puede verse como una tabla de permisos
incomprensible. En Stitch, mantenerlo simple: listas de reglas con toggle on/off y
"Edit" que abre un drawer. No intentar representar todas las permutaciones visuales.

**La taxonomía de autoridad de agentes (SEÑALA / PROPONE / EJECUTA)**
Para un operador, esto es ruido si se muestra en todas partes. Solo debe ser visible
en: (1) la configuración del skill y (2) el header del approval drawer. Nowhere else.

---

### Lo que hay que simplificar en la representación visual inicial

**No mostrar la arquitectura interna del KB** (chunking, embeddings, vector store).
Eso es infraestructura invisible para el operador. El KB es simplemente una lista
de documentos organizados por dominio con estados.

**No mostrar el Nightly Maintenance Engine en el Command Center**
Para el prototipo inicial, reducirlo a un simple indicador: "Mantenimiento nocturno: OK / Pendiente".
No intentar representar el pipeline completo.

**No construir Voice Profile Setup en la primera versión de Stitch**
Es un form. Puede representarse con un wireframe de baja fidelidad.
El effort de Stitch debe ir en Case Detail, Approval Drawer y KB Browser.

**Reducir el número de visibility tiers visibles en el prototipo**
Para claridad visual inicial, usar solo INTERNAL y PARTNER_B2B en los ejemplos.
CEO-ONLY puede mostrarse como un warning en una sola pantalla de demo.

---

### El hero flow para la primera versión de Stitch

**Usar este flujo, y solo este:**

> Usuario abre Caso "Propuesta Q2 – Bancolombia" →
> Case Detail con Context Panel ya cargado (3 snippets KB auto-cargados, tier PARTNER_B2B) →
> Click en "Invocar Skill" → selecciona "Draft Proposal" →
> Centro del panel muestra output generándose con source badges inline →
> Un warning amber aparece (sección sin fuente KB) →
> Usuario ve inspector, acepta sugerencia de KB, warning desaparece →
> Output en estado "Listo para Aprobación" →
> Click "Enviar a Aprobación" →
> Approval Drawer se abre desde derecha →
> Aprobador ve draft + fuentes + voice match →
> Click "Aprobar" → estado cambia a APROBADO → pantalla de confirmación limpia.

Este flujo toca todas las pantallas críticas, muestra governance en acción,
y es completamente lineal. Es el candidato más fuerte para el hero prototype.
El resto puede ser navegación secundaria.

---

*Archivo generado: 2026-04-15 · Para uso con Stitch AI UI Generator*
*FaberLoom · Muito Work Limitada · Confidencial*
```
