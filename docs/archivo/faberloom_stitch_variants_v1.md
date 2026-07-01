# FaberLoom — 3 Variantes Estratégicas para Stitch
## Arquitectura visual comparada · v1.0 · 2026-04-15

---

# VARIANTE 1 — KNOWLEDGE-FIRST

---

## A. Tesis de la variante

El núcleo de FaberLoom no es lo que el usuario *hace* — es lo que el sistema *sabe*.
Esta variante apuesta a que la propuesta de valor diferencial de FaberLoom es su base de
conocimiento canónica, gobernada y versionada. Sin un KB estructurado, cualquier skill
produce basura. Sin gobernanza de visibilidad, cualquier output es un riesgo. La interfaz
debe hacer sentir eso desde el primer segundo: el usuario está operando sobre verdad
verificada, no sobre inferencia libre.

En esta variante, la pantalla central no es un caso ni una cola de tareas. Es el conocimiento.
Los casos, los skills y los outputs son formas de *aplicar* ese conocimiento. La UI comunica:
"todo lo que produce este sistema parte de aquí". Esto sacrifica fluidez operativa diaria a
cambio de claridad epistémica. Es la variante correcta si FaberLoom se vende principalmente a
equipos de gobernanza, compliance, legal o gestión de conocimiento — no a operadores de ventas.

---

## B. Prompt Maestro para Stitch — KNOWLEDGE-FIRST

```
Design a B2B enterprise knowledge governance platform called FaberLoom.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CORE THESIS FOR THIS DESIGN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The center of FaberLoom is its knowledge base. Everything the system does — every output,
every skill, every case — flows from verified, structured, governed operational knowledge.
The interface must make this immediately obvious. The user should feel they are operating
on a system of verified truth, not on a probabilistic AI guessing at answers.

Cases and workflows exist, but they are surfaces. The knowledge engine is the product.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT FABERLOOM IS (KNOWLEDGE-FIRST FRAMING)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FaberLoom is a governed knowledge engine for B2B operators. Its knowledge base is organized
into domains (Sales, Legal, Operations, Compliance, Product). Each knowledge entry is
versioned, has an explicit validity date, a visibility tier (PUBLIC / PARTNER_B2B /
INTERNAL / CEO-ONLY), and a confidence status. Skills are reasoning modules that
reference this knowledge to produce outputs. Cases are applications of skills against
a specific contact or project. Nothing gets injected into an output — or sent externally —
unless it passes visibility and integrity checks against the KB.

This is not a document management system. It is not Confluence or Notion. It is an
operational truth store with active governance, retrieval logic, and output traceability.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INTERFACE FEEL AND NON-GOALS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FEEL: A compliance-grade knowledge workbench. Dense but structured. Authoritative.
The visual language of a well-governed regulatory system. Color communicates
knowledge state (active, conflicted, expired, frozen). Structure communicates
reliability. Nothing looks improvised.

DO NOT build as:
- A document wiki (Notion/Confluence aesthetic)
- A chatbot or AI assistant
- A generic dashboard with KPI charts
- A CRM with records and pipeline boards
- A folder/file tree with search

The UI must immediately surface: what domains exist, what the health of each domain
is, which entries have conflicts or are expiring, and what skills depend on what knowledge.
This is an operational truth layer, not a document repository.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRIMARY LAYOUT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Two-zone layout with a persistent left sidebar for domain navigation.

LEFT SIDEBAR (240px):
Domain tree organized hierarchically:
  ▾ Ventas
      Catálogo de Productos
      Políticas Comerciales
      Objeciones Frecuentes
  ▾ Legal
      Contratos Tipo
      Cláusulas Críticas
  ▾ Operaciones
      ...
Each domain shows a health indicator: green dot (all entries current),
amber dot (conflicts or expiring entries), red dot (critical failures).

MAIN AREA: Two-panel when browsing (entry list | entry detail).
Three-panel when working a case from knowledge context (domain tree | entry
with skills that use it | active case linked to this entry).

TOP BAR: FaberLoom wordmark + KB Health global indicator + user + search.
The global KB health chip is always visible: [KB · 3 conflictos activos].

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRIMARY SCREENS TO GENERATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. KB HOME: Domain health overview. Left = domain tree. Center = summary table:
   Domain | Total entries | Active | Conflicted | Expiring | Skills using this domain.
   Top widget: "3 conflictos requieren resolución · 2 entradas vencen esta semana".
   Not a dashboard with charts — a structured health report table.

2. DOMAIN VIEW: All entries within a domain. Dense table:
   Entry title | Type | Status (chip) | Visibility tier (chip) | Valid until | Skills using it | Last updated.
   Left sidebar highlights active domain. Filter bar above table.

3. KB ENTRY DETAIL: Full-screen knowledge document view.
   TOP: Metadata strip — ID | Version | Domain | Visibility | Valid Until | Status.
   BODY: Structured content with section markers. Inline conflict flags in red.
   RIGHT PANEL: "Skills que usan esta entrada" (list with links) + "Casos activos que
   referencian esta entrada" (compact list). Edit History at bottom.
   ACTIONS: Edit (goes to draft mode) | Flag conflict | Archive.

4. CONFLICT RESOLUTION: Split-screen view. Left = conflicting entry A.
   Right = conflicting entry B. Center divider with diff highlights.
   Bottom: "Resolver: mantener A | mantener B | fusionar | escalar".
   This screen is unique to Knowledge-First and communicates governance centrality.

5. SKILLS CATALOG: Grid of skill cards organized by domain.
   Each card: Name | Domain | Authority mode | "Requires KB: [domain chips]" | Last run.
   Click a skill: opens detail showing exactly which KB entries it queries, in what order,
   with what visibility filters applied. This makes the KB-skill dependency explicit.

6. SKILL DEPENDENCY MAP: A relationship view. Left = KB entry. Center = skills that
   use it. Right = cases/outputs that ran that skill. A chain of trust visualization:
   KB entry → skills → outputs. Not a graph — a structured three-column list with chips.

7. CASES (secondary): A compact list view. Not the hero screen. Accessed from nav.
   Cases reference KB entries; those references are shown as source badges in each case row.

8. APPROVAL QUEUE: Standard queue. Each approval shows which KB entries were used
   in generating the output, with confidence per entry. The KB provenance is prominent.

9. AUDIT TRAIL: Timeline filtered by KB entry, domain, skill, or case.
   "KB entry #042 was modified → 3 cases re-evaluated → 1 output flagged for re-approval."
   This shows the cascading governance value of a KB-centric architecture.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HERO FLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Start on KB Home. Global chip shows [2 conflictos · dominio Ventas].
User clicks domain "Ventas" in sidebar → Domain View loads.
Amber row: "Política de Descuentos v2.1 · CONFLICTO con v2.0".
User clicks row → Conflict Resolution screen.
User resolves: "mantener v2.1". Entry status updates to ACTIVE.
Right panel shows: "4 skills afectados por este cambio · 1 caso en estado Draft puede
re-evaluarse". User clicks "Re-evaluar caso". Case Detail opens.
Draft updated with corrected KB entry. Source badge now shows [HIGH confidence].
User submits for approval. Approval Queue receives item with provenance chain visible.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VISUAL AND COMPONENT DECISIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Color: Dark zinc base. Indigo for primary actions. Emerald for ACTIVE/verified entries.
Amber for CONFLICT/WARNING. Red for EXPIRED or BLOCKED. Violet for AI-generated markers.
Visibility tier chips: teal=PARTNER_B2B, blue=INTERNAL, rose=CEO-ONLY, gray=PUBLIC.

Typography: Dense, technical. Inter for UI. Monospace for KB IDs and version strings.
Tables over cards for almost everything. Cards only for skill summaries.

Navigation: Left sidebar is the primary navigation surface. Domain tree IS the nav.
No top-level tabs for "Cases" or "Approvals" — they are secondary items at the bottom
of the left sidebar.

Density: High. This is an expert tool. Every row in every table carries status, version,
and tier information. Horizontal space is used efficiently — no excessive whitespace.

Build as: A functional high-fidelity wireframe prototype of KB Home + Domain View +
Conflict Resolution + Skill Dependency Map. Use real domain names: "Ventas", "Legal",
"Operaciones". Use real entry names: "Política de Descuentos v2.1", "Contrato Marco tipo A".
```

---

## C. Screen Map — KNOWLEDGE-FIRST

| # | Pantalla | Propósito | Info dominante | Acciones clave | Por qué existe aquí |
|---|----------|-----------|----------------|----------------|---------------------|
| 1 | **KB Home** | Panel de salud del conocimiento global | Tabla de dominios con conteo: entradas activas / conflictos / por vencer | Ir a dominio · Resolver conflicto urgente | Es la pantalla de entrada — el estado del KB es el estado del sistema |
| 2 | **Domain View** | Todas las entradas de un dominio | Tabla densa: título · estado · visibilidad · válido hasta · skills que la usan | Añadir entrada · Filtrar por estado · Ordenar | El dominio es la unidad de gobernanza |
| 3 | **KB Entry Detail** | Inspeccionar y editar una pieza de conocimiento | Contenido estructurado · Metadata completa · Conflictos inline · Skills dependientes | Editar · Archivar · Flag conflicto · Ver historial | El KB entry es el objeto primario del sistema |
| 4 | **Conflict Resolution** | Resolver dos entradas en conflicto activo | Vista split: entrada A vs entrada B con diff | Mantener A · Mantener B · Fusionar · Escalar | Unique to KB-First — la gobernanza del conocimiento es central |
| 5 | **Skills Catalog** | Explorar skills y sus dependencias de KB | Grid/tabla: skill · modo · KB requerido · última ejecución | Ver dependencias · Invocar desde caso · Configurar scope | Los skills son "applicators" del conocimiento — su relación con el KB es clave |
| 6 | **Skill Dependency Map** | Ver la cadena KB → skill → output | Tres columnas: KB entry · Skills que la usan · Outputs recientes | Ir a KB entry · Ir a caso · Ver audit trail | Único en esta variante: muestra el linaje completo del conocimiento en acción |
| 7 | **Cases (secundario)** | Lista de casos que aplican el conocimiento | Tabla compacta con KB sources referenciadas por fila | Abrir caso · Nuevo caso · Filtrar | Los casos existen, pero como aplicaciones del KB, no como el centro |
| 8 | **Approval Queue** | Aprobaciones con KB provenance visible | Queue con: output type · KB entries usadas (badges) · confianza por entrada | Aprobar · Rechazar · Ver fuentes | La aprobación muestra la cadena de verdad KB→output |
| 9 | **Audit Trail KB** | Trazabilidad de cambios en el KB y sus efectos en cascada | Timeline: modificación KB → skills re-evaluados → casos afectados | Filtrar por entry · Exportar | Muestra el valor de gobernanza: cambiar una entrada KB afecta el sistema entero |
| 10 | **Admin / Governance** | Configurar dominios, visibilidad, roles, nightly | Tabs: Dominios · Tiers · Usuarios · Mantenimiento | Editar regla · Publicar · Revisar propuestas nightly | La gobernanza necesita una pantalla explícita en esta variante |

---

## D. Riesgos de la variante

**Qué puede salir bien**: La propuesta de valor de FaberLoom (conocimiento estructurado y
gobernado) queda comunicada de forma inmediata. En una demo para un CTO, un director de
compliance o un gerente de knowledge management, esta interfaz es irrefutable. Dice lo que
hace y hace lo que dice.

**Qué puede salir mal**: Los operadores de ventas, cobranza o CS no piensan en términos de
KB. Piensan en "tengo que responder a este cliente". Si el onboarding empieza en KB Home,
muchos usuarios van a desorientarse. La curva de aprendizaje es más pronunciada.

**Demasiado compleja**: La Conflict Resolution screen y el Skill Dependency Map son pantallas
que solo tiene sentido para KB managers o admins. Un skill promedio del equipo de ventas
nunca las usará. Si Stitch las genera con el mismo peso visual que el flujo de trabajo
cotidiano, la interfaz se verá sobrecargada.

**Demasiado abstracta**: "Conocimiento" como concepto central puede sentirse distante para un
usuario que quiere redactar un email. Necesita concreción: casos activos, outputs recientes,
notificaciones de trabajo pendiente. Sin ese anclaje operativo, la app se ve como un
repositorio, no como una herramienta de trabajo.

**Riesgo de parecerse a otro software**: Confluence, Notion, SharePoint, o cualquier wiki
enterprise. Si Stitch no logra comunicar claramente que este es un *sistema operativo de
outputs gobernados* y no un repositorio de documentos, la identidad se pierde.

---

## E. Veredicto de la variante

**Cuándo es correcta**: Si FaberLoom se vende primero a equipos de gobernanza, compliance, legal
o conocimiento institucional. Si el buyer es el CTO o el Director de Operaciones, no el
representante de ventas. Si el caso de uso principal es "gestionar y actualizar el conocimiento
operativo de la empresa" más que "producir outputs correctos rápidamente".

**Para qué tipo de usuario funciona mejor**: KB managers, administradores del sistema, directores
de compliance. Usuarios con autoridad sobre la verdad operativa de la organización.

**Qué sacrifica frente a las otras dos**: Fluidez diaria del operador. La experiencia de "entro,
veo qué tengo que hacer, lo hago, salgo" no existe aquí. Sacrifica velocidad y accesibilidad
de uso cotidiano a favor de rigor y gobernanza explícita.

---
---

# VARIANTE 2 — WORKFLOW-FIRST

---

## A. Tesis de la variante

El usuario de FaberLoom no viene a explorar conocimiento. Viene a completar trabajo. Entra con una
lista de cosas por hacer: aprobaciones pendientes, borradores por revisar, casos por avanzar,
skills por ejecutar. La interfaz debe hacer que ese trabajo fluya. El conocimiento y la
gobernanza son el sistema nervioso — están siempre presentes, pero invisibles salvo cuando
importan (un bloqueo, un warning, una fuente conflictiva).

Esta variante apuesta a que FaberLoom compite más eficazmente si se presenta como una herramienta
de trabajo asistido por IA con governance, que como un sistema de gestión de conocimiento con
outputs. La entrada a la app es la cola de trabajo, no el árbol de dominios KB. Los estados
(Pending / In Progress / Blocked / Approved / Sent) dominan la jerarquía visual. El conocimiento
aparece contextualmente dentro de cada paso del flujo, nunca como pantalla de inicio.

---

## B. Prompt Maestro para Stitch — WORKFLOW-FIRST

```
Design a B2B enterprise AI workflow platform called FaberLoom.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CORE THESIS FOR THIS DESIGN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The center of FaberLoom is the work that needs to get done. Users come to execute:
approve drafts, run skills, advance cases, resolve blocks. Knowledge and governance
are the intelligence underneath every action — visible when they matter, invisible
when they don't. The interface must feel like a focused work queue with expert AI
intelligence wired into every step.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT FABERLOOM IS (WORKFLOW-FIRST FRAMING)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FaberLoom is a governed AI work platform for B2B operators. Every output the system
helps produce is grounded in a verified knowledge base, adapted to a voice profile,
and requires explicit human approval before going external. The experience is:
see your work queue, pick up the next item, execute it with AI-powered skill
assistance, get it approved, ship it. The system handles the knowledge retrieval,
governance checks, and source attribution automatically — the user focuses on
judgment and approval.

This is not a task management tool. It is not Asana or Linear or Monday.com.
The difference is that every action is powered by expert knowledge and every output
is auditable. The workflow is the surface; the knowledge engine is what makes it
reliable.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INTERFACE FEEL AND NON-GOALS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FEEL: A focused operations center. Clear queue. Clear status. Clear next action.
The interface communicates forward motion: what's done, what's in progress, what's
blocked, what's next. Dense but directional. Every screen answers "what do I do now?"

DO NOT build as:
- A knowledge browser or document tree
- A chatbot or conversational interface
- A CRM pipeline kanban (not about stages and deals)
- A dashboard with metrics as the hero
- A project management board (not about epics and sprints)

The distinguishing visual element over generic workflow tools: every item in the
queue shows its KB source provenance, visibility tier, and approval state. These
are not secondary tooltips — they are column-level information in every table.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRIMARY LAYOUT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Two-zone with focused work area as the dominant surface.

LEFT SIDEBAR (220px, icon + label, collapsible):
  Priority items: Mi Cola · Aprobaciones · Casos · Skills
  Secondary items: Base de Conocimiento · Contactos · Auditoría
  Bottom: Admin · Settings

The sidebar conveys clear hierarchy: work items first, knowledge second.

MAIN AREA: The work queue or the active work item — depending on navigation state.
When a queue item is open: two-panel (item detail with skill output | right inspector
showing KB sources, confidence, visibility, approval state).

TOP BAR: Badge count for pending approvals (always visible, like email unread count).
Active case name when inside a case. User avatar.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRIMARY SCREENS TO GENERATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. MI COLA (Work Queue): The hero screen. A prioritized list of everything the user
   needs to act on today. Sections: "Para aprobar (3)" · "En ejecución (2)" ·
   "Bloqueados (1)" · "Completados hoy (5)".
   Each item shows: Type chip · Case name · Contact/Org · Time in state · Status badge.
   Keyboard shortcut J/K to navigate, Enter to open. No charts, no metrics. Just work.

2. TASK / SKILL EXECUTION VIEW: When a queued item is a "run a skill" task.
   Left: Task context (case name, contact, instructions, KB snippets auto-loaded).
   Center: Skill output area — streaming real-time with source badges per sentence.
   Right: Inspector — KB entries used, confidence per entry, visibility tier check,
   voice profile active. Actions at bottom: Submit for Approval · Save as Draft · Cancel.

3. APPROVAL REVIEW: When a queued item is a pending approval.
   Full draft visible with inline source badges. Voice match indicator.
   Visibility tier confirmed. Diff view if the draft was edited from original.
   Actions: Approve · Edit & Approve · Reject (with reason field, required).
   This screen must feel fast and decisive — not bureaucratic.

4. CASES LIST: Secondary screen. A table, not a kanban. Columns: Case · Contact ·
   Status · Pending actions · Skills executed · Owner. Cases are containers of work
   items, not primary objects. Accessed when needed, not as home screen.

5. CASE DETAIL: Inside a case, the user sees the work history and active items.
   Two-panel: Left = case timeline (skills run, outputs produced, approvals, notes) |
   Right = active work item or "No active task — invoke skill to continue".
   The case timeline is the memory of what happened in this case.

6. SKILLS LAUNCHER: A compact overlay (command palette style, ⌘K).
   Invoked from anywhere within a case or work item. Shows: skills relevant to current
   context, required KB scope indicator, authority mode chip.
   Select a skill → immediately opens Task Execution View.

7. BLOCKS & ALERTS: A dedicated view for items that are stuck.
   Why blocked: "KB entry expirada" / "Visibilidad violada" / "Esperando aprobador".
   Actions: "Ir a KB entry" · "Escalar" · "Reenviar a aprobador".
   Each block has an explicit resolution path — not just a red state.

8. COMPLETED QUEUE (History): Scrollable history of completed work items.
   Each row: what was done, when, by whom, which skill, which case.
   Filterable. Links to full audit entry. Not editable.

9. KB (BACKGROUND LAYER): Accessible from sidebar but not the primary surface.
   A compact entry point: Search bar prominent, domain filters, quick table of entries.
   The KB is the engine room — accessible but not the cockpit.

10. ADMIN: Skills configuration, visibility rules, user roles. Tab-based.
    Low density — form-based. Accessed rarely, not part of daily workflow.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HERO FLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

User arrives → Mi Cola shows: "Para aprobar (1) · En ejecución (1) · Bloqueado (1)".
First item: "Aprobar · Propuesta Q2 Bancolombia · En cola 2h".
User presses Enter → Approval Review opens.
Sees full draft with source badges. Voice match: 91%.
Visibility tier: PARTNER_B2B confirmed, no CEO-ONLY content.
Amber banner: "Una sección usa inferencia sin fuente KB. Revisar."
User clicks → Inspector highlights the section. User edits it inline.
Banner clears. User clicks "Aprobar" → item moves to Completed. Queue updates.
User returns to Mi Cola. Next item: "Ejecutar Skill · Respuesta RFQ · Caso Cemex".
User opens item → Skill Execution View. KB context auto-loaded.
Skill runs → draft streams with source badges. All HIGH confidence.
User clicks "Submit for Approval" → item assigned to approver. Queue updates.
Total time for two actions: under 8 minutes.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VISUAL AND COMPONENT DECISIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The status badge system is the primary visual differentiator:
PARA APROBAR: amber / EJECUTANDO: indigo pulse / BLOQUEADO: red / COMPLETADO: emerald muted.

Each queue item has exactly three pieces of visible information in the list:
(1) Type chip (Aprobar / Ejecutar / Resolver), (2) Case + Contact name,
(3) Time in current state. Everything else is in the detail view.

"Pending approvals" count in top bar nav acts like an inbox unread count — always visible,
creates urgency without being intrusive.

KB source badges appear ONLY when the user has a work item open — not in list views.
In list views, only the KB health indicator (green/amber/red dot) is shown per item.

Speed is a visual value here. Compact rows. Fast transitions. Keyboard-first.
The approval flow must be completable in 3 clicks: Open → Review → Approve.

Build as: High-fidelity prototype of Mi Cola (work queue) + Approval Review +
Task/Skill Execution View. Use real data: "Propuesta Q2 – Bancolombia",
"Respuesta RFQ – Cemex", skill names like "Draft Commercial Proposal · PROPONE".
```

---

## C. Screen Map — WORKFLOW-FIRST

| # | Pantalla | Propósito | Info dominante | Acciones clave | Por qué existe aquí |
|---|----------|-----------|----------------|----------------|---------------------|
| 1 | **Mi Cola (Work Queue)** | Entrada principal — todo lo que el usuario debe hacer hoy | Secciones por estado: Para Aprobar · En Ejecución · Bloqueados · Completados | Abrir item · Filtrar · Marcar urgente | La cola ES la app. El trabajo se organiza por estado, no por contenedor |
| 2 | **Skill Execution View** | Ejecutar un skill contra un caso, ver output en tiempo real | KB context cargado · Streaming del output con source badges · Inspector de confianza | Submit para aprobación · Guardar draft · Cancelar | El flujo de trabajo requiere un espacio de ejecución dedicado |
| 3 | **Approval Review** | Revisar y aprobar/rechazar un output antes de envío externo | Draft completo · Source badges · Voice match · Visibility tier · Diff si hay edición previa | Aprobar · Editar & Aprobar · Rechazar | La aprobación es el paso más frecuente en el workflow diario |
| 4 | **Blocks & Alerts** | Resolver items atascados con causa y acción explícitas | Lista de bloqueados: motivo · tiempo bloqueado · acción requerida | Ir a KB entry · Escalar · Reasignar aprobador | Los bloqueos necesitan resolución, no solo visibilidad |
| 5 | **Cases List** | Contenedores de trabajo — ver el estado de cada caso | Tabla: Caso · Estado · Tareas pendientes · Skills ejecutados · Propietario | Abrir caso · Nuevo caso · Filtrar por estado | Los casos organizan el historial, no son el punto de entrada |
| 6 | **Case Detail** | Ver el timeline de un caso y sus items activos | Timeline izq. (acciones, outputs, aprobaciones) · Item activo der. (o placeholder) | Invocar skill · Ver output anterior · Añadir nota | Dentro de un caso, el usuario ve el historial y continúa trabajando |
| 7 | **Skills Launcher (overlay)** | Invocar un skill rápidamente desde cualquier contexto | Command palette: skills disponibles · KB scope · modo de autoridad | Seleccionar skill → ir a Execution View | La invocación de skills debe ser rápida y contextual, no una pantalla separada |
| 8 | **Completed Queue** | Historial de trabajo completado hoy/esta semana | Tabla compacta: qué se hizo · cuándo · quién · skill usado · caso | Ir a audit entry · Reabrir item | El historial completa el ciclo de trabajo visible |
| 9 | **KB (background)** | Acceder al KB cuando el workflow lo requiere | Barra de búsqueda + tabla de entradas con estado | Buscar · Ver entry · Cargar en caso | El KB es el motor, no el punto de entrada — accesible pero no protagonista |
| 10 | **Admin** | Configurar skills, visibilidad, roles | Tabs con formularios de configuración | Editar · Guardar · Publicar | Necesario para admins, invisible para operadores |

---

## D. Riesgos de la variante

**Qué puede salir bien**: Esta es la experiencia más adoptable para el operador diario.
La cola de trabajo es un patrón universal — cualquier usuario entiende "esto es lo que
tengo que hacer hoy". La velocidad de aprobación y la claridad de siguiente paso van a
reducir la fricción de onboarding significativamente. Stitch puede generar esto de forma
impresionante porque el patrón es muy representable.

**Qué puede salir mal**: Sin trabajo visible en la cola, la app se ve vacía e inútil.
El empty state de "Mi Cola" es el punto de falla más crítico de esta variante: si el
usuario llega y no ve nada, no sabe qué hacer. Además, el KB queda relegado a un item
del sidebar — el diferenciador principal de FaberLoom se vuelve invisible.

**Demasiado compleja**: La intersección entre workflow states y knowledge states puede
crear confusión: ¿el item está bloqueado por una regla de visibilidad KB o por falta
de aprobador? El usuario puede no entender la diferencia sin un sistema de categorización
de bloqueos muy preciso.

**Riesgo de parecerse a otro software**: Este es el riesgo más alto de las tres variantes.
Sin los source badges y la gobernanza visible, "Mi Cola" se ve exactamente como Asana,
Linear o Monday.com. Si Stitch genera un prototipo donde los chips de KB provenance
no son prominentes, la identidad de FaberLoom desaparece completamente. Se convierte en
"otro task manager con IA".

**Demasiado abstracta**: No en esta variante. Es la más concreta de las tres.

---

## E. Veredicto de la variante

**Cuándo es correcta**: Si el buyer principal es el gerente de equipo que necesita que
su equipo ejecute trabajo consistente más rápido. Si el caso de uso es "mi equipo produce
emails y propuestas y respuestas todos los días y necesito que sean correctos y rastreables".
Si el onboarding debe ser inmediato y la adopción rápida.

**Para qué tipo de usuario funciona mejor**: Operadores de ventas, CS, cobranza, operaciones.
Equipos con volumen alto de outputs repetitivos que necesitan consistencia. El usuario
que entra, hace su trabajo, y sale.

**Qué sacrifica**: La visibilidad del KB como diferenciador. La gobernanza se vuelve
infraestructura invisible — presente pero no prominente. Si el comprador necesita ver
"qué tan gobernado está nuestro conocimiento", esta variante no lo muestra en home.

---
---

# VARIANTE 3 — CASE/PROJECT-FIRST

---

## A. Tesis de la variante

La unidad fundamental de trabajo en FaberLoom no es una tarea ni un documento de conocimiento.
Es el caso: una oportunidad comercial, una licitación, una cobranza, un reclamo, una
auditoría, una negociación. El caso tiene actores, historia, documentos, outputs, decisiones
y contexto vivo. Todo lo demás — el KB, los skills, la voz, los canales — se activa *dentro*
del caso, para ese caso, en ese momento.

Esta variante reconoce que los operadores B2B piensan en términos de "el cliente X",
"la RFQ de Cemex", "el expediente de cobranza de la Constructora Moreira". El conocimiento
y los skills son herramientas que el usuario activa dentro de ese contexto, no el punto de
entrada. La interfaz debe hacer que cada caso sea un espacio de trabajo rico, contextual y
auditable — una carpeta inteligente con capacidad de razonar. Esta es la variante con mayor
fidelidad a cómo trabajan los operadores B2B en la realidad.

---

## B. Prompt Maestro para Stitch — CASE/PROJECT-FIRST

```
Design a B2B enterprise case management and AI work platform called FaberLoom.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CORE THESIS FOR THIS DESIGN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The organizing unit of FaberLoom is the Case. A case is a contextual container:
it has a contact or organization, a type (commercial proposal, dispute resolution,
procurement response, debt collection, compliance audit), a timeline of actions
and outputs, active skills, knowledge context loaded for this case specifically,
and a governance layer that controls what can be sent and to whom.

Knowledge, skills, voice profiles, and channel access are all activated from
within a Case. The Case is the workspace. Everything else is infrastructure that
the Case makes available.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT FABERLOOM IS (CASE-FIRST FRAMING)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FaberLoom is a B2B case workbench powered by a governed knowledge engine. Each case
is a living dossier: it loads relevant knowledge from the KB automatically based
on the case type and contact, activates appropriate skills, tracks every output
and decision in a timeline, and enforces approval before any external communication.
The operator works inside the case — they don't need to navigate to a separate KB
browser or skills catalog. The case surfaces what's needed, contextually.

Think of it as a digital dossier that thinks alongside the operator. Not a folder.
Not a ticket. A structured workspace with memory, governed intelligence, and an
auditable output trail.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INTERFACE FEEL AND NON-GOALS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FEEL: A structured, contextual workspace. Like a well-organized case file at a
consulting firm or law office — but digital, interactive, and AI-assisted. Rich
with context. Chronological. Auditable. The interface communicates: "everything
relevant to this case is here, nothing outside of here is needed".

DO NOT build as:
- A project management board (not epics/sprints, not cards dragged between columns)
- A CRM with deals pipeline and contact records as the hero
- A document folder structure (not just a list of files)
- A conversational AI interface
- A linear task list

The case must feel like a living workspace, not a record. It has state, history,
active work, and future actions — all visible simultaneously. The key differentiator
over generic case management tools (Zendesk, ServiceNow): every action inside the
case is backed by a verified KB, and every output is governed by a visibility policy.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRIMARY LAYOUT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The Case Detail is the primary screen. It uses a THREE-PANEL LAYOUT that is
the structural heart of the entire application.

LEFT PANEL — CASE CONTEXT (280px):
  Top: Case header — Type chip · Contact/Org · Status badge.
  Section: KB context loaded for this case. Each KB snippet shown as a compact
  card with: source name, domain, visibility tier chip, confidence chip.
  Section: Case participants — who is involved, their role, their voice profile.
  Section: Case metadata — opened date, owner, domain, linked cases.

CENTER PANEL — WORK AREA (flexible):
  The active work surface. Can show:
  (a) Skill output streaming in real-time with source badges inline.
  (b) Draft editor for an output pending approval.
  (c) Case timeline — chronological history of all actions in this case.
  (d) Empty state with "Invocar Skill" as primary action.
  Bottom: Action bar — "Invocar Skill" (⌘K) · "Añadir nota" · "Ver timeline".

RIGHT PANEL — INSPECTOR (300px):
  Active when an output is in progress or selected.
  Shows: KB sources used per section with confidence · Visibility tier confirmed ·
  Voice profile active (sender → recipient) · Skill used + authority mode ·
  Approval state. Collapsible to icon rail when not needed.

CASE LIST (before entering a case):
Left sidebar nav: Cases · Approvals · KB · Skills · Contacts · Audit.
Main area: Compact table of cases with: Type chip · Name · Contact/Org ·
Status · Last activity · Pending actions badge.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRIMARY SCREENS TO GENERATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CASES LIST: Entry point. Dense table. Columns: Type · Case Name · Contact/Org ·
   Status chip · Last Activity · Pending actions (badge count) · Owner.
   Group by: Status (Active / Pending Approval / Closed) or by Type.
   Filter bar: by type, by owner, by visibility tier, by date. No kanban.

2. CASE DETAIL — TIMELINE VIEW: Inside a case, the default view is the timeline.
   Three panels: Context (left) | Timeline (center) | Inspector (right, collapsed).
   Timeline shows chronological entries: [Skill invocado] [Draft generado] [Enviado
   para aprobación] [Aprobado] [Email enviado] [Nota añadida]. Each entry expandable.
   This is the memory of the case — what happened and when.

3. CASE DETAIL — SKILL EXECUTION VIEW: When a skill is running. Same three panels.
   Context panel shows KB snippets most relevant to this skill invocation.
   Center panel: streaming output with source badges inline per sentence.
   Inspector: confidence per KB source, visibility tier check running in real-time,
   voice profile indicator (e.g., "Álvaro → Dir. Compras Cemex · Formal/Técnico · 94%").
   Bottom actions: Submit for Approval · Save Draft · Cancel.

4. CASE DETAIL — DRAFT REVIEW (in-case): When the current user IS the approver.
   Same three panels. Center: full draft with source badges + inline edit capability.
   Inspector: diff from original (if edited) · visibility confirmation · KB sources.
   Actions: Approve · Edit & Approve · Reject with reason.

5. NEW CASE WIZARD: Three-step flow.
   Step 1: Select case type (chips: Propuesta Comercial · Cobranza · Respuesta RFQ ·
   Reclamo · Auditoría · Otro) + associate contact/org.
   Step 2: System auto-loads suggested KB context (user confirms or adjusts).
   Step 3: Confirm voice profile (sender → recipient defaults shown, editable).
   → Case opens in Timeline View, ready.

6. CONTACT PROFILE: Not a CRM record — a case context view.
   Header: Name · Org · Tier · Voice override active.
   Main: Table of all cases linked to this contact with status.
   Side: Relevant KB entries tagged to this contact (auto-suggested).
   No deal stages. No pipeline chart. A contextual relationship workspace.

7. APPROVAL QUEUE (cross-case): A list of pending approvals across ALL cases.
   Each row: Case type · Case name · Draft type · Time pending · Skill used.
   Click → opens in-case Approval Review (Case Detail - Draft Review view).
   This is a convenience aggregator — the real approval happens inside the case.

8. CASE SEARCH & FILTER: A dedicated search view for finding cases.
   Global search with instant results. Filter by: type, contact, status, date range,
   skills used, KB domains referenced, visibility tier of outputs. Result as table.

9. KB CONTEXT PANEL (in-case): Accessed from the Context Panel of Case Detail.
   "Ver más en KB" → expands to a full-screen KB browser filtered to this case's
   domain context. User can drag/add more KB snippets to the case context.
   Then returns to Case Detail. The KB is always in service of a case, never standalone.

10. AUDIT TRAIL (per case): In the case detail, a dedicated tab in the timeline shows
    the immutable audit log for this specific case: every skill run, every draft generated,
    every approval, every send, with full KB source trace.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HERO FLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

User opens Cases List → clicks "Propuesta Q2 – Bancolombia" (Type: Propuesta Comercial).
Case Detail opens in Timeline View. Left panel shows: 4 KB snippets auto-loaded
(Catálogo Productos · PARTNER_B2B, Política de Descuentos v2.1 · INTERNAL, etc.)
Timeline shows 2 prior entries: "Caso creado" · "Nota: cliente pidió propuesta antes del 20".
User clicks "Invocar Skill" → Skills Launcher overlay appears with suggested skills
based on case type. Selects "Draft Propuesta Comercial · PROPONE".
Center panel shifts to Skill Execution View. Output streams. Source badges attach inline.
Inspector shows: [§ Catálogo Productos · HIGH] [§ Política de Descuentos · HIGH] [⚠️ inferred x1].
Amber chip: "1 sección sin fuente KB confirmada". User inspects, accepts KB suggestion.
Chip clears. Output shows "Ready for Approval" state.
User clicks "Submit for Approval".
Timeline entry added: "Draft propuesta enviado a aprobación · 11:42".
Inspector shows: "Esperando aprobación de: Álvaro Alfaro".
[Approver side]: Approval Queue shows new item. Opens it → Case Detail Draft Review.
Approver sees draft in context of the case timeline. Approves.
Timeline entry: "Propuesta aprobada · 11:47". Inspector shows green APPROVED state.
Email draft generated in channel surface. Case status: "Listo para envío".

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VISUAL AND COMPONENT DECISIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Case Type chips are visually prominent — they immediately tell the user what kind
of work is happening: PROPUESTA (indigo) · COBRANZA (amber) · RECLAMO (red-muted) ·
AUDITORÍA (violet) · RFQ RESPONSE (blue). Color distinguishes work type, not just state.

The timeline is the memory of each case. Its entries use a compact format:
[Icon type] [Action description] [Timestamp] — expandable on click.
Timeline entries for AI-generated content always show the skill used as a chip.

KB snippets in the Context Panel use a compact card format (not a table):
[Domain chip] [Entry title] [Visibility chip] [Confidence chip] [Collapse/expand].
Maximum 6 snippets visible before "Ver más" overflow.

The three-panel layout is the signature of this variant. When the inspector is
collapsed, it becomes a 2-panel view. On screens below 1400px wide, the context
panel collapses to an icon rail with hover-expand.

Case status communicates with color AND label:
Active (emerald) · Pending Approval (amber + pulsing dot) · Blocked (red) · Closed (zinc muted).

Build as: High-fidelity prototype of Cases List + Case Detail in all three states
(Timeline / Skill Execution / Draft Review). Show the New Case Wizard as a secondary
flow. Use real case types and real data. Primary screen priority: Case Detail
with streaming skill output and inspector showing source confidence.
```

---

## C. Screen Map — CASE/PROJECT-FIRST

| # | Pantalla | Propósito | Info dominante | Acciones clave | Por qué existe aquí |
|---|----------|-----------|----------------|----------------|---------------------|
| 1 | **Cases List** | Punto de entrada — inventario de todos los casos activos | Tabla: Tipo · Nombre · Contacto · Estado · Última actividad · Pendientes | Abrir caso · Nuevo caso · Filtrar | El caso es el objeto primario; esta lista es el menú de entrada al trabajo |
| 2 | **Case Detail — Timeline** | Vista de historia y estado de un caso | Timeline cronológico: acciones, outputs, aprobaciones, notas | Invocar skill · Añadir nota · Ver output anterior | La historia del caso es el contexto operativo que el operador necesita ver |
| 3 | **Case Detail — Skill Execution** | Generar un output dentro del contexto del caso | KB snippets cargados (izq.) · Output streaming con source badges (cen.) · Inspector con confianza (der.) | Submit para aprobación · Guardar draft · Cancelar | El trabajo ocurre dentro del caso, no en una pantalla separada de skills |
| 4 | **Case Detail — Draft Review** | Aprobar/rechazar un output dentro del caso | Draft con source badges · Diff si hay edición · Inspector con visibility confirmation | Aprobar · Editar & Aprobar · Rechazar | La aprobación tiene todo el contexto del caso disponible — es más informada |
| 5 | **New Case Wizard** | Crear un caso con contexto pre-cargado | Paso 1: Tipo + contacto · Paso 2: KB context sugerido · Paso 3: Perfil de voz | Confirmar · Ajustar KB · Cambiar voz | El caso necesita ser inicializado con el contexto correcto desde el principio |
| 6 | **Contact Profile** | Ver relación con un contacto/org en términos de casos activos | Header del contacto · Tabla de casos · KB entries asociadas | Nuevo caso · Ver caso · Editar perfil de voz | Los contactos organizan casos, no registros de CRM |
| 7 | **Approval Queue** | Agregador de aprobaciones pendientes de todos los casos | Lista: Tipo de caso · Nombre · Draft type · Tiempo pendiente · Skill usado | Abrir aprobación en contexto del caso | Facilita la labor del aprobador sin forzarlo a abrir cada caso individualmente |
| 8 | **Case Search** | Buscar y filtrar casos por cualquier dimensión | Buscador + filtros: tipo · contacto · estado · KB domain · fecha | Buscar · Filtrar · Abrir caso | Los casos se acumulan; necesitan búsqueda potente |
| 9 | **KB en contexto de caso** | Acceder al KB desde dentro de un caso para cargar más contexto | KB browser filtrado al dominio del caso | Añadir snippet al caso · Ver entry completa | El KB se accede en servicio del caso — siempre contextualizado |
| 10 | **Audit Trail por caso** | Trazabilidad completa e inmutable de un caso específico | Timeline inmutable: skills, outputs, KB sources, aprobaciones, envíos | Filtrar · Exportar · Verificar cadena de fuentes | La auditoría por caso es el mecanismo de rendición de cuentas |
| 11 | **Admin** | Configuración del sistema: skills, visibility, roles | Tabs: Skills · Tipos de caso · Visibilidad · Usuarios | Editar · Publicar | Necesario para admins, invisible para operadores |

---

## D. Riesgos de la variante

**Qué puede salir bien**: Esta variante tiene la mayor fidelidad al modelo mental del
operador B2B real. "El cliente Bancolombia tiene una propuesta pendiente" es como
piensan los representantes, gerentes de cuenta y operadores de cobranza. El contexto
está siempre presente. Los outputs son auditables por caso. La adopción es natural.

**Qué puede salir mal**: Si los casos no tienen suficiente volumen de trabajo (early users),
el Cases List se ve vacío y sin valor. Además, el Case Detail con tres paneles es
visualmente rico pero puede ser demasiado denso para un primer onboarding. Un usuario
nuevo puede no entender cómo usar los tres paneles sin guía.

**Demasiado compleja**: El New Case Wizard en tres pasos puede percibirse como fricción
innecesaria si el usuario simplemente quiere "abrir un caso rápido y escribir algo".
Hay que balancear entre estructura de inicialización y velocidad de arranque.

**Riesgo de parecerse a otro software**: Zendesk (tickets/cases), ServiceNow (expedientes),
Salesforce (oportunidades), HubSpot (deals). Si los Type chips y el contexto KB no son
prominentes, el Cases List se ve exactamente como un CRM o helpdesk. La identidad de
FaberLoom depende de que el KB context y las source badges sean visibles DESDE el primer
segundo dentro de un caso.

**Demasiado abstracta**: No en esta variante — pero puede tornarse abstracta si los tipos
de caso no están bien definidos para el mercado objetivo. "Caso" es demasiado genérico;
"Propuesta Comercial", "Cobranza", "Respuesta RFQ" son concretos.

---

## E. Veredicto de la variante

**Cuándo es correcta**: Cuando el mercado objetivo son equipos B2B que trabajan por casos
o proyectos discretos: ventas (propuestas, RFQs), cobranza (expedientes), legal (contratos),
CS (reclamos), partnerships (negociaciones). Si el case type mapping con la industria
del cliente es correcto, la adopción es casi inmediata.

**Para qué tipo de usuario funciona mejor**: Representantes comerciales, ejecutivos de cuenta,
gestores de cobranza, coordinadores legales. Usuarios que trabajan cliente por cliente,
no en flujos de tareas genéricos.

**Qué sacrifica**: La visibilidad del KB como sistema en sí mismo. Un director de knowledge
management no encontrará aquí un lugar desde donde gestionar el KB a nivel organizacional.
Esa vista existe pero es secundaria.

---
---

# COMPARACIÓN FINAL Y RECOMENDACIÓN

---

## Tabla Comparativa

| Dimensión | KNOWLEDGE-FIRST | WORKFLOW-FIRST | CASE/PROJECT-FIRST |
|-----------|-----------------|----------------|--------------------|
| **Centro del producto** | El KB y su gobernanza | La cola de trabajo y el estado de tareas | El caso como workspace contextual |
| **Fortalezas** | Hace visible el diferenciador de FaberLoom. Irrefutable en demo B2B2B. Gobernanza como protagonista | Más adoptable. Flujo de trabajo claro. Approval flow óptimo. Velocidad de ejecución. | Mayor fidelidad al modelo mental del operador. Contexto siempre presente. Escalable a múltiples industrias |
| **Debilidades** | Distante para el operador diario. Onboarding difícil. Se parece a un wiki | Riesgo de verse genérico. KB invisible. Identidad de FaberLoom diluida | Densidad inicial alta. Riesgo de parecerse a CRM/helpdesk sin diferenciadores claros |
| **Complejidad visual** | Alta (árbol de dominios, conflict resolution, dependency map) | Media (cola de trabajo + estados claros) | Media-Alta (3 paneles + timeline + inspector) |
| **Claridad para el usuario** | Baja al inicio, alta para power users | Alta desde el primer día | Alta una vez entendido el concepto de caso |
| **Ajuste a FaberLoom** | Alto en arquitectura, bajo en usabilidad diaria | Medio — funcional pero no diferenciador | **Alto en ambas dimensiones** |
| **Riesgo de verse genérica** | Riesgo de wiki/Confluence | **Riesgo alto de task manager** | Riesgo de CRM — mitigable con diferenciadores KB |
| **Potencial para Stitch** | Bueno para pantallas de KB y governance | **Excelente para flujo lineal de aprobación** | **Excelente para hero screen (Case Detail 3 paneles)** |

---

## Ranking Final

| # | Variante | Razón |
|---|----------|-------|
| 🥇 1 | **CASE/PROJECT-FIRST** | Fidelidad al modelo mental del operador B2B. Contexto siempre presente. Diferenciadores de FaberLoom (KB sources, governance) son visibles en el contexto correcto — dentro del trabajo real — no como capas separadas. Escalable. Representable excelentemente por Stitch. |
| 🥈 2 | **WORKFLOW-FIRST** | Más adoptable a corto plazo. Aprobaciones más rápidas. Mejor para teams con volumen alto de outputs repetitivos. Pero sacrifica demasiado de la identidad de FaberLoom si no se cuida el diseño. |
| 🥉 3 | **KNOWLEDGE-FIRST** | Arquitecturalmente correcta pero operativamente difícil. Valiosa como CAPA DE ADMIN — no como experiencia del operador diario. |

---

## Recomendación Específica

**Probar PRIMERO en Stitch: CASE/PROJECT-FIRST**

Razón: El Case Detail de tres paneles es el artefacto visual más representativo de
lo que FaberLoom es. Muestra simultáneamente: contexto KB gobernado, skill execution con
source attribution, approval state, voice profile activo, y timeline de caso. En una
sola pantalla, FaberLoom se explica a sí mismo. El hero flow (New Case → load KB → run
skill → approve → done) es lineal, demostrable y diferenciador. Es el prototipo que
deberías mostrar en demos.

**Probar SEGUNDO: WORKFLOW-FIRST**

Razón: Como variante de adopción rápida y para validar el flujo de aprobaciones como
mecanismo principal de trabajo del equipo. Si el primer mercado son equipos con volumen
alto de outputs (call centers B2B, cobranza, operaciones comerciales), esta variante
puede ser más adoptable inicialmente. Usar el prototipo de Mi Cola + Approval Review
para testear con usuarios reales.

**Usar KNOWLEDGE-FIRST solo si las dos anteriores fallan — o para un segmento específico:**

Si el buyer principal resulta ser el Director de Calidad, el Gerente de Cumplimiento
o el CTO que necesita demostrar gobernanza de conocimiento a un regulador o auditor,
KNOWLEDGE-FIRST tiene su momento. Pero ese no debería ser el primer prototipo.

---

## Hero Flows Recomendados para Stitch por Variante

| Variante | Hero Flow para Stitch |
|----------|-----------------------|
| **CASE/PROJECT-FIRST** | Cases List → Abrir "Propuesta Q2 Bancolombia" → Case Detail (Timeline) → Invocar Skill "Draft Proposal" → Skill Execution (streaming + sources) → Approval state → Draft Review → Aprobar → Timeline actualizado |
| **WORKFLOW-FIRST** | Mi Cola → "Para aprobar (1)" → Approval Review → Source badges + warning → Edit inline → Aprobar → Cola actualizada → Siguiente item: Ejecutar Skill → Skill Execution → Submit → Done |
| **KNOWLEDGE-FIRST** | KB Home → Conflicto activo en Ventas → Domain View → Conflict Resolution → Resolver → Re-evaluar caso afectado → Case con draft actualizado → Aprobar → Audit trail muestra cadena KB→output |

---

## Postura final

La CASE/PROJECT-FIRST no solo es la más potente para Stitch — es la arquitectura
de interfaz que más honra el Marco Rector de FaberLoom. El Marco dice que la prioridad
es la integridad del conocimiento, pero el *propósito* del sistema es que cualquier
persona pueda producir un output correcto, adaptado al caso y al destinatario. El caso
es el lugar donde ese propósito se materializa. El KB es el mecanismo. El flujo de
trabajo es la consecuencia. Esa es la jerarquía correcta para el diseño de la interfaz.

La KNOWLEDGE-FIRST comete el error de exponer la arquitectura como si fuera la experiencia.
La WORKFLOW-FIRST comete el error de ocultar la arquitectura hasta hacerla invisible.
La CASE/PROJECT-FIRST equilibra ambas: la arquitectura está presente y visible, pero
siempre en servicio del trabajo real.

---

*Archivo generado: 2026-04-15 · FaberLoom · Muito Work Limitada · Confidencial*
*Usar en conjunto con faberloom_stitch_prompt_master.md y FABERLOOM_MARCO_RECTOR_v1.md*
