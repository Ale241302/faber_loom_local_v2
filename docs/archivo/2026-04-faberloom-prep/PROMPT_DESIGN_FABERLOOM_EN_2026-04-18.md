# FABERLOOM v1 — DESIGN BRIEF (2 mockups)
**For:** Claude Design
**Date:** 2026-04-18
**From:** Álvaro, FaberLoom (product architect)
**Goal:** Produce 2 standalone HTML mockups, desktop-first, editorial palette, production-intent (not marketing).

> **UI language note:** all in-product copy (buttons, labels, placeholders, empty states, example workflow names, example emails) must be in **Spanish (LatAm)**. Brief and your internal comments can be English. Product UI = Spanish.

---

## 0. What FaberLoom does (one paragraph, read first)

FaberLoom is a **control plane for AI agents in LatAm SMBs** (5–50 employees). Non-technical founders wire up agents that read email, consult their knowledge base, draft responses, quote prices, and update CRM — but **never send anything external without human approval** unless autonomy has been explicitly unlocked with evidence. The product has three surfaces: (a) **Workflow Builder** where admins design processes as visual node graphs and publish them live; (b) **Bandeja (Inbox)** where Operators triage agent-generated drafts every day — approve, edit, or reject; (c) admin/billing/connections (not in scope this round). Core principle: **draft-first absolute**. Every customer-facing action passes through a visible `awaiting_approval` state, with provenance (which document, which version, which snippet justifies each claim) inline on the draft. The v1 wedge is **B2B industrial safety footwear quoting** for Marluvas/Tecmater distributors across LatAm — concrete, not generic "AI employee".

---

## 1. Answers to your 12 questions (inline, numbered)

### Q1. Section 3 structure — here it is in full
See Section 3 of this brief. Not cut off. Includes screen layout, node types, Runs Ledger details.

### Q2. Color palette — exact hex tokens
```
--bg-primary:       #F6F1E8   /* cream/off-white editorial (main background) */
--bg-surface:       #FFFFFF   /* elevated cards, modals, panels */
--bg-subtle:        #EEE7DA   /* hover states, active list item bg */
--text-primary:     #1A1A1A   /* body text, titles */
--text-secondary:   #5A5A5A   /* labels, meta */
--text-muted:       #8A8A8A   /* timestamps, hints */
--border-subtle:    #D8D0C0   /* 1px dividers, input borders */
--vino-primary:     #6E1F2B   /* primary accent — buttons, active nav, key headings */
--vino-hover:       #531A23   /* primary accent hover */
--vino-tint:        rgba(110, 31, 43, 0.10)  /* subtle highlight over draft text */
--success:          #2E6B4F   /* completed runs, approved state */
--warning:          #A87820   /* awaiting approval, draft-unpublished banner */
--error:            #9C2B2B   /* failed runs, reject actions */
--info:             #3B5A6F   /* neutral informational (use sparingly) */
```
No gradients. No SaaS-purple. No neon. Editorial restraint.

### Q3. Product behavior — see Section 0 above
Wedge = B2B safety footwear quoting. That's the workflow to render.

### Q4. Node types in Workflow Builder
Six node types. Each has a distinct shape + icon + accent:

| Type | Symbol | Fill | Purpose |
|---|---|---|---|
| **Trigger** | solid circle | vino `#6E1F2B` | Entry point (email received, webhook, schedule, manual) |
| **Agent** | diamond (rotated square) | vino outline, white fill | AI agent does work (classify, extract, draft, summarize) |
| **Action** | rounded rectangle | neutral gray `#5A5A5A` | Deterministic tool call (send email, write to CRM, POST webhook) |
| **Policy gate** | pentagon/shield | warning `#A87820` outline | Rule check before proceeding ("if amount > $10k require approval") |
| **Approval gate** | hexagon | vino `#6E1F2B` outline | Explicit human approval required before continuing |
| **Output/sink** | arrow pointing out | neutral | Terminal node (email sent, ticket closed, record updated) |

All nodes have a header row (icon + name) and optional 2nd row with a **risk badge** (`Customer-visible` / `Financial` / `Internal-only` / `Reversible`) and a **metrics chip** (`94% approved · 43 runs`).

### Q5. Workflow canvas style
**Not Figma-like. Not n8n-dense.** Closer to a clean Mermaid diagram with editorial warmth. Specifics:
- Nodes stacked **vertically top-to-bottom** (primary flow direction). Horizontal branching only when a Policy gate splits (yes/no paths).
- Connector lines: 1px solid `#D8D0C0`, with a thin arrowhead.
- Background: same cream `#F6F1E8` with a very subtle 32×32px dot grid at 6% opacity (barely perceptible — just enough to feel like a canvas).
- No floating panels on the canvas. No inspector on top of canvas — inspector is a right-docked panel (see layout).
- Zoom/pan is implied but don't design zoom controls ornately — small `+ / − / reset` stack in bottom-right corner, ghost styling.

### Q6. Runs Ledger layout
Horizontal table-style list **docked below the canvas**. Columns:
`[status icon] | Run ID | Triggered by | Started | Duration | Cost | Approver | ···`
- Sticky header row.
- Rows 40px tall, 14px Inter font.
- Status icons: `✓` (success `#2E6B4F`), `⚠` (awaiting `#A87820`), `✗` (failed `#9C2B2B`), `◐` (running — pulse animation), `▣` (blocked by policy `#A87820` with outline).
- Row hover → `#EEE7DA` background.
- Click row → **slide-over drawer from right** (480px wide) with timeline of nodes traversed, inputs/outputs per node (collapsible), policy checks, evidence refs, cost breakdown, approver + timestamp.
- Header filter row above ledger: status pill filter · date range picker · approver dropdown · agent dropdown · search input.

### Q7. Builder vs Ledger vertical split
**Canvas 65% height · Ledger 35% height.** Divider is a 1px line `#D8D0C0` that's draggable (optional — show a subtle 3-dot grab handle on hover). Ledger can be collapsed to a 32px strip showing just the header row with counts (`12 runs today · 2 awaiting`).

### Q8. Interactivity level — **medium**
Static-looking but with these working interactions:
- Hover states on all nodes, rows, buttons.
- Click a node → right panel slides in (360px) with node config.
- Click a ledger row → slide-over drawer from right with run detail.
- Toggle **Draft/Live** visually swaps states (just CSS class toggle, no real persistence needed).
- Tab switching in Bandeja (Aprobaciones ↔ Excepciones) works.
- Selecting a Bandeja list item updates the detail pane.
- Evidence highlights in Bandeja detail pane: hover highlight → corresponding Evidence panel item scrolls into view.
- Keyboard shortcuts work in Bandeja: `J/K` navigate list, `A` approve (shows success animation), `E` enter edit mode, `R` reject (shows confirm).

Don't build: actual node drag-and-drop, actual persistence, actual network, undo stack logic.

### Q9. Variations?
**Per view, produce these states in the SAME file** (toggle at top-right of the page for reviewer, small unobtrusive pill):
- **Builder:** (a) healthy published state · (b) "Draft with unpublished changes" banner state · (c) one node selected → right panel open.
- **Bandeja:** (a) Aprobaciones tab with 7 items, 1 active in detail · (b) Excepciones tab with 2 items, 1 active showing policy-blocked state · (c) Aprobaciones empty state ("Bandeja al día").

### Q10. Target viewport
**1440 × 900 primary.** Must not break at 1280 min. Don't design mobile or tablet this round — Operators use laptops. No responsive below 1280.

### Q11. App chrome / shell (same in both views)
```
┌─────────────────────────────────────────────────────────────┐
│ SIDEBAR 220px fixed  │  MAIN AREA flex                      │
│                      │                                      │
│  FaberLoom (logo)    │  Breadcrumb + contextual actions    │
│  ──────              │  ──────────────────────────────      │
│  Inicio              │                                      │
│  Workflows    ●      │        [view-specific content]       │
│  Bandeja (7)         │                                      │
│  Conocimiento        │                                      │
│  Agentes             │                                      │
│  Conexiones          │                                      │
│  Configuración       │                                      │
│                      │                                      │
│  ──────              │                                      │
│  Avatar              │                                      │
│  Álvaro · Owner      │                                      │
└─────────────────────────────────────────────────────────────┘
```
- Sidebar bg `#F6F1E8`, active item has vino text + 2px left border.
- `(7)` pendiente badges only on Bandeja.
- No global top navbar. No search bar in shell. No notification bell. Keep chrome minimal.

### Q12. One real workflow to render on canvas
Render this exact workflow, named **"Cotización B2B Marluvas"**:

```
◉  Trigger: Correo entrante en ventas@acme.cr
    ↓
◆  Agente: QuoteBot — Clasificar intención
    (Detecta: "solicitud de cotización B2B")
    ↓
◆  Agente: QuoteBot — Extraer pedido
    (Extrae: modelo, cantidad, tallas, plazo)
    ↓
◆  Agente: QuoteBot — Cruzar con catálogo + inventario
    (Consulta ENT_PROD_MAR v3.2 + Inv_2026-04-18)
    ↓
◆  Agente: QuoteBot — Redactar cotización
    (Aplica voz de marca + términos comerciales)
    ↓
⬢  Policy gate: ¿Monto > USD 10 000?
    ├─ sí ──┐
    │      ↓
    │   ⬡  Aprobación requerida: Operator
    │      ↓
    └─ no ──┘
            ↓
    ⬡  Aprobación: Operator (siempre en v1)
            ↓
    ▢  Acción: Enviar por Gmail a remitente
            ↓
    ↗  Output: Cotización enviada + registro en CRM
```

Symbols: ◉ trigger · ◆ agent · ⬢ policy gate · ⬡ approval · ▢ action · ↗ output.

For the Runs Ledger below, render these 6 runs (vary mix):

| # | Status | Triggered by | Started | Duration | Cost | Approver |
|---|---|---|---|---|---|---|
| #1284 | ✓ Completed | jperez@distribacme.cr | 12:04 PM | 42s | $0.08 | Álvaro |
| #1283 | ⚠ Awaiting | ventas@ferreteriabolivar.co | 11:58 AM | — | $0.04 | — |
| #1282 | ✗ Failed | compras@mineraaurora.pe | 11:52 AM | 18s | $0.02 | — |
| #1281 | ✓ Completed | operaciones@cofesa.mx | 11:40 AM | 38s | $0.07 | Álvaro |
| #1280 | ▣ Blocked | cp@grupo-valle.cr | 11:22 AM | 11s | $0.03 | — |
| #1279 | ✓ Completed | rh@textilesdelcauca.co | 10:58 AM | 51s | $0.09 | Operador M. |

Failure reason for #1282 (show in drawer): "Error al consultar catálogo: ENT_PROD_MAR v3.2 — modelo no encontrado (`50S19-XYZ`). Reintentar manualmente o escalar."
Block reason for #1280: "Monto USD 14,500 excede techo L1 del agente QuoteBot (USD 10,000). Requiere aprobación Admin."

---

## 2. Palette and visual system (binding)

Anchor reference: the `FaberLoom ONE _standalone_.html` editorial file already in the project. Do **not** use the "THREE" Bold Block variant (too marketing).

### 2.1 Colors
See Q2 above for hex tokens. All other colors must derive from those — no new colors invented.

### 2.2 Typography
- **Display / H1–H3:** Georgia (serif) — view titles, workflow names, section headings.
- **UI / body / labels:** Inter (sans) — everything else.
- **Mono (run IDs, hashes, logs):** ui-monospace, or JetBrains Mono if available.

Scale:
- H1: Georgia 32px / weight 500 / line-height 1.2
- H2: Georgia 24px / weight 500
- H3: Georgia 18px / weight 500
- Body: Inter 14px / weight 400 / line-height 1.5
- Small: Inter 12px / weight 400
- Mono: 12px

### 2.3 Spacing + geometry
- 8px base grid.
- Panel padding: 24px.
- Card padding: 16px.
- Radius: 4px (inputs) / 8px (cards) / 12px (modals and drawers).
- Shadows: nearly invisible. Max `0 1px 2px rgba(0,0,0,0.04)`. Prefer 1px borders over shadows.

### 2.4 Density
**Dense but breathable.** Reference: Linear + NYT article layout, not Notion marketing. Operator opens Bandeja 20× a day — every click and scroll counts.

### 2.5 Shared components (consistent across both mockups)
- **Primary button:** vino fill, cream text, 36px height, 16px horizontal padding, 4px radius.
- **Secondary button:** 1px vino border, vino text, transparent fill.
- **Tertiary/ghost:** vino text only, underline on hover.
- **Destructive:** error red text on transparent, red outline on hover.
- **Input:** 1px border `#D8D0C0`, focus `#6E1F2B` 2px.
- **Status pill:** small pill, tinted bg of the state color (10% opacity), text in same state color, 11px font.
- **Tab:** 2px underline of vino under active label, muted label for inactive.
- **Badge dot:** 6px circle, color-coded by state.

---

## 3. VIEW 1 — Workflow Builder + Runs Ledger

### 3.1 Purpose
A human designs a process as a visual node graph, publishes it live, and audits every real execution in the Runs Ledger docked below.

### 3.2 Screen layout
```
┌──────────────────────────────────────────────────────────────────────────────┐
│ SIDEBAR 220px │ MAIN AREA                                                    │
│               │                                                              │
│               │ Workflows / Cotización B2B Marluvas                          │
│               │ ──────────────────────────────────────                       │
│               │ [Draft ●] [Live ○]         [Publicar]  [⟲ Revertir]        │
│               │ Última publicación: hace 3h por Álvaro · v41a9f2             │
│               │                                                              │
│               │ ╔═════════════════ CANVAS (65%) ══════════════════╗ ┌──────┐│
│               │ ║                                                  ║ │INSP  ││
│               │ ║    [◉ Trigger Gmail]                            ║ │ECTOR ││
│               │ ║         │                                        ║ │360px ││
│               │ ║    [◆ QuoteBot · Clasificar]                    ║ │      ││
│               │ ║         │                                        ║ │(only ││
│               │ ║    [◆ QuoteBot · Extraer pedido]                ║ │when  ││
│               │ ║         │                                        ║ │a node││
│               │ ║    [◆ QuoteBot · Cruzar catálogo]               ║ │is    ││
│               │ ║         │                                        ║ │selec.││
│               │ ║    [◆ QuoteBot · Redactar]                      ║ │      ││
│               │ ║         │                                        ║ │      ││
│               │ ║    [⬢ Policy: > USD 10k]                        ║ │      ││
│               │ ║       sí↙   ↘no                                 ║ │      ││
│               │ ║    [⬡ Approval Admin]   │                       ║ │      ││
│               │ ║         └─┬──────────────┘                      ║ │      ││
│               │ ║           │                                     ║ │      ││
│               │ ║    [⬡ Approval Operator]                        ║ │      ││
│               │ ║           │                                     ║ │      ││
│               │ ║    [▢ Acción: Enviar Gmail]                     ║ │      ││
│               │ ║           │                                     ║ │      ││
│               │ ║    [↗ Output: CRM update]                       ║ │      ││
│               │ ║                                                  ║ │      ││
│               │ ║  [+ Agregar nodo]                    [+ − ⟳]    ║ │      ││
│               │ ╚═══════════════════════════════════════════════════╝ └──────┘│
│               │                                                              │
│               │ ══════════════ RUNS LEDGER (35%) ══════════════              │
│               │ [Todos ▾] [Últimas 24h ▾] [Approver ▾] [Agente ▾] [🔍]     │
│               │ ┌──────┬──────┬──────────────┬────────┬──────┬──────┬─────┐  │
│               │ │Estado│ID    │Disparado por │Inicio  │Dur.  │Costo │Appr.│  │
│               │ │✓     │#1284 │jperez@...    │12:04PM │42s   │$0.08 │Álv. │  │
│               │ │⚠     │#1283 │ventas@...    │11:58AM │—     │$0.04 │—    │  │
│               │ │✗     │#1282 │compras@...   │11:52AM │18s   │$0.02 │—    │  │
│               │ │✓     │#1281 │operaciones@..│11:40AM │38s   │$0.07 │Álv. │  │
│               │ │▣     │#1280 │cp@...        │11:22AM │11s   │$0.03 │—    │  │
│               │ │✓     │#1279 │rh@...        │10:58AM │51s   │$0.09 │Op.M.│  │
│               │ └──────┴──────┴──────────────┴────────┴──────┴──────┴─────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Header details
- Breadcrumb: `Workflows` (link) `/` `Cotización B2B Marluvas` (current, no link).
- Toggle **Draft ● / Live ○**: pill-switch showing which version the canvas is displaying. Swapping re-renders canvas (same workflow for mockup purposes).
- **[Publicar]** primary button. If no unpublished changes: disabled with tooltip "Sin cambios por publicar".
- **[⟲ Revertir]** tertiary with rollback icon. Click → confirm modal: *"¿Revertir a la versión anterior (v40c7d1)? Se descartarán los cambios del Draft actual."*
- Sub-header line: `Última publicación: hace 3h por Álvaro · v41a9f2` — small, muted.
- **Unpublished-changes banner** (variant b): thin amber bar directly below breadcrumb: *"Hay cambios en Draft sin publicar."* + [Publicar] inline button on right. Dismissible but reappears until published.

### 3.4 Canvas
- Background: cream `#F6F1E8` + subtle 32×32 dot grid at 6% opacity.
- Nodes: 240px wide, auto-height, 8px radius, 1px border (accent color by type), 16px internal padding.
- Each node shows:
  - Row 1: icon + node name (Inter 14 semibold).
  - Row 2: type label (12px muted). Example: *"Agente · Redactar"*.
  - Row 3 (optional): risk badge chip + metrics chip (`94% aprobación · 43 runs`).
- Connectors: 1px `#D8D0C0` lines, small arrowhead at target end.
- Selected node: vino 2px border + soft tint bg (`--vino-tint`).
- Hover non-selected: 2px vino border only.
- Zoom controls bottom-right: `[+]` `[−]` `[⟳ fit]` each 32×32px, ghost style.
- `[+ Agregar nodo]` button bottom-center of canvas, secondary styling.

### 3.5 Inspector panel (right, 360px, only when node selected)
Slides in from right, pushes canvas. Contains:
- Close `×` top-right.
- Node name (H3) + type label.
- Tabs: `Config` · `Memoria` · `Últimos runs` (only Memoria+runs tabs for Agent nodes).
- **Config tab (Agent node):**
  - Rol (textarea).
  - Instrucciones (textarea, monospace hint).
  - Autonomy ceiling — **slider L0 → L5**, with lock icons on L2+ if criteria not met. Default L0 (Shadow).
  - **Copilot / Autopilot toggle** below slider:
    - Copilot (default, humano aprueba) · Autopilot (ejecuta directo)
    - If Autopilot not qualified: shown locked with caption *"Se desbloquea cuando la tasa de aprobación ≥ 85% en últimos 100 runs. Actual: 67% (43 runs)."*
    - CTA link under: *"Ver criterios para desbloquear →"*.
  - Skills habilitadas (chips).
  - Herramientas permitidas (chips).
- **Memoria tab:** sender profiles top-3 (mini cards) · gold samples activos (3 preview cards) · KB asignada (chips).
- **Últimos runs tab:** 5 rows linking to ledger detail.
- **Config tab (Policy gate):** list of declarative rules. Example: *"Si monto > USD 10 000 → requerir aprobación Admin."*
- **Config tab (Action):** required permissions list + OAuth status chip (conectado/no).

### 3.6 Runs Ledger (dockable, 35% height)
- Filter row: status pill filter · date range picker · approver dropdown · agent dropdown · search input (200px).
- Table header sticky.
- Rows 40px, Inter 13px, hover `#EEE7DA`.
- Click row → slide-over drawer from right (480px wide) showing:
  - Run ID (H3) + status badge.
  - Workflow + version (`v41a9f2`).
  - Timeline of nodes traversed (vertical, same visual style as canvas nodes but smaller, with per-node status).
  - Per-node inputs/outputs (collapsible, monospace).
  - Policy checks executed (list with pass/fail).
  - Evidencia (provenance): numbered list — claim snippet → source doc + version + snippet.
  - Approver + timestamp (if any).
  - Cost breakdown (tokens in/out + $ per model used).
  - `[Replay this run]` secondary button + `[Exportar JSON]` tertiary link.

### 3.7 Variants to render in the single file
State switcher pill top-right of page: `[Healthy] [Draft con cambios] [Nodo seleccionado]`
- **Healthy:** published state, no banner, no node selected, inspector hidden.
- **Draft con cambios:** amber banner visible, Publicar button highlighted, canvas shows same nodes.
- **Nodo seleccionado:** QuoteBot (Redactar) is selected, inspector panel open on right with Config tab showing autonomy slider at L1, Autopilot locked.

### 3.8 What NOT to design in View 1
- No agent marketplace.
- No admin/users/billing settings.
- No connection setup wizards.
- No marketing homepage.
- No onboarding.
- No public-facing L0–L5 autonomy branding (show it inside inspector only).

---

## 4. VIEW 2 — Bandeja / Approval Workspace

### 4.1 Purpose
Operator opens this 20× per day. Triages agent drafts: approve, edit, or reject. Must feel like **Superhuman for AI** — keyboard-driven, dense, fast.

### 4.2 Screen layout (3 columns)
```
┌──────────────────────────────────────────────────────────────────────────────┐
│ SIDEBAR │ LISTA 380px                    │ DETAIL PANE flex                  │
│ 220px   │                                │                                   │
│         │ Bandeja                        │ RE: Cotización 120 pares Marluvas │
│         │ ─────────────                  │ Para: jperez@distribacme.cr       │
│         │ [Aprobaciones(7)] [Excep.(2)]  │ Agente: QuoteBot · hace 4 min     │
│         │                                │ [Customer-visible] [Financial]    │
│         │ ■ ⚠ #1283                      │ ──────────────────────────        │
│         │   Cotización Marluvas          │                                   │
│         │   Cliente: ACME                │ Estimado Sr. Pérez,              │
│         │   USD 14,500                   │                                   │
│         │   QuoteBot · hace 4m           │ Gracias por su solicitud. Adjunto │
│         │                                │ cotización por 120 pares de       │
│         │ □ ⚠ #1281                      │ Marluvas modelo 50S19 en tallas   │
│         │   Cotización Tecmater          │ mixtas (38 al 44), con [precio    │
│         │   Cliente: Ferretería Bolívar  │ unitario de USD 120 cada par]¹    │
│         │   USD 8,200                    │ y [disponibilidad inmediata en    │
│         │   QuoteBot · hace 12m          │ inventario de 120 unidades]².     │
│         │                                │                                   │
│         │ □ ⚠ #1275                      │ Plazo de entrega: 5 días hábiles. │
│         │   Cotización Marluvas          │ Condiciones: 50% anticipo,        │
│         │   Cliente: Cofesa              │ 50% contra entrega.               │
│         │   USD 6,100                    │                                   │
│         │   QuoteBot · hace 27m          │ Quedo atento.                     │
│         │                                │                                   │
│         │ ── Excepciones ──              │ ▾ Ver razonamiento del agente    │
│         │                                │ ── EVIDENCIA ─────────────        │
│         │ □ ▣ #1280                      │ 1. "precio unitario de USD 120"   │
│         │   Bloqueado por policy         │    ← ENT_PROD_MAR v3.2            │
│         │   Grupo Valle                  │    Snippet fuente: "50S19 — USD   │
│         │   USD 14,500                   │    120.00 (MOQ 50 pares)"         │
│         │   Requiere Admin               │                                   │
│         │                                │ 2. "disponibilidad inmediata"     │
│         │                                │    ← Inv_2026-04-18               │
│         │                                │    Snippet fuente: "50S19 — 120   │
│         │                                │    unidades · bodega CR"          │
│         │                                │                                   │
│         │                                │ ──────────────────────────        │
│         │                                │ [Aprobar y enviar] A              │
│         │                                │ [Editar] E  [Rechazar] R          │
│         │                                │                                   │
│         │                                │ J/K navegar · ⌘K búsqueda         │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Lista column (380px wide)
- Tabs row on top:
  - **Aprobaciones (7)** and **Excepciones (2)**.
  - Active tab underlined 2px vino.
  - Counters update as items are resolved (interactivity).
- Search input + sort dropdown (default: oldest-awaiting-first, SLA-first).
- Batch actions bar appears when any checkbox checked:
  - `[Aprobar 3 seleccionados]` · `[Rechazar 3]` · `[Asignar a…]`
  - For batch approve: if any item has `Customer-visible` risk → confirm modal.
- Each list item (85px tall):
  - Checkbox left-edge (appears on hover, stays visible when checked).
  - Status icon (⚠/▣/◐/✗).
  - Run ID (mono 11px muted).
  - Title — descriptive, not "Run #1283". Example: `Cotización Marluvas`.
  - Customer: `Cliente: ACME`.
  - Amount: `USD 14,500` (if applicable).
  - Agent + relative timestamp: `QuoteBot · hace 4m`.
- Active item: bg `#EEE7DA` + 2px left border vino.
- Hover unchecked: bg `#EEE7DA` at 50% opacity.
- Hover shows tooltip with first 2 lines of draft.

### 4.4 Detail pane (right, flex-fill)
- **Header area:**
  - Subject line (H2 Georgia).
  - To / From / Agent + timestamp (Inter 12 muted).
  - Risk badges inline: `Customer-visible` + `Financial` if applicable.
  - Divider.
- **Draft body:**
  - Rendered as rich text, Inter 14px, line-height 1.6.
  - Inline **evidence highlights**: spans with subtle vino tint bg (`--vino-tint`) + superscript number (¹, ²…). Hover highlight → scroll evidence panel to matching claim. Click highlight → evidence panel expands if collapsed.
  - Editable inline when Edit mode active — contenteditable with vino caret.
- **Reasoning collapsible (closed by default):**
  - `▸ Ver razonamiento del agente` trigger.
  - Expanded: bulleted list, small Inter 13 muted. Example:
    - "Clasifiqué como cotización B2B con 94% de confianza (palabras clave: cotización, modelo, pares)."
    - "Usé precio unitario USD 120 de ENT_PROD_MAR v3.2 publicado el 2026-03-15."
    - "Condiciones de pago estándar Tier-B por monto entre USD 10k–50k."
- **Evidencia panel (always visible, scrollable if long):**
  - Numbered items matching inline superscripts.
  - Each item:
    - Quoted claim span from draft.
    - `← Source: ENT_PROD_MAR v3.2`
    - Snippet fuente (italic, muted).
    - Link: `Abrir documento →` (tertiary).
- **Sticky action bar (bottom):**
  - `[Aprobar y enviar]` primary vino + `A` shortcut label.
  - `[Editar]` secondary + `E`.
  - `[Rechazar]` tertiary (error text tint) + `R`.
- **Shortcut legend** (footer row, 11px muted, very discreet):
  - `J/K navegar · A aprobar · E editar · R rechazar · ⌘K búsqueda rápida · ? ver todos`.
- **Undo bar** (slides from bottom after action): *"Cotización enviada. Deshacer (9s)"* — vino bg, cream text, 10s countdown.

### 4.5 Excepciones tab
Same list/detail structure. Detail pane differs:
- Header badge: `Bloqueado por policy` (amber) or `Falló ejecución` (red).
- Reason block (replaces draft body):
  - Plain-language explanation. Example: *"Monto USD 14,500 excede el techo L1 del agente QuoteBot (USD 10,000). Requiere aprobación de un Admin."*
  - Which node blocked/failed (small card showing the node).
  - Timestamp + input that triggered it.
- Action bar changes:
  - `[Escalar a Admin]` primary.
  - `[Aprobar manualmente (override)]` secondary + confirm modal warning that override leaves immutable audit trail.
  - `[Abortar run]` tertiary error.

### 4.6 Empty states (design honestly)
- Aprobaciones empty: H3 *"Bandeja al día"* + body *"Los próximos drafts aparecerán aquí."* + link *"Ver workflows activos →"*. No emoji. No celebration.
- Excepciones empty: *"Sin excepciones pendientes."* — one line, muted.

### 4.7 Loading / error states
- Detail pane loading: skeleton rectangles with subtle pulse, not spinner.
- Fetch fail: *"No pudimos cargar este draft."* + `[Reintentar]`.
- Race condition on approve: *"Este draft ya fue resuelto por Juan hace 12s. [Ver resultado]"*.

### 4.8 Variants to render in the single file
State switcher pill top-right: `[Aprobaciones activa] [Excepciones activa] [Bandeja vacía]`
- **Aprobaciones activa:** 7 items, #1283 selected in detail with 2 evidence highlights.
- **Excepciones activa:** 2 items, #1280 selected showing policy-blocked state.
- **Bandeja vacía:** honest empty state copy.

### 4.9 What NOT to design in View 2
- No agent config form (that lives in Builder inspector).
- No "corrección recurrente" modal.
- No chatbot conversational UI.
- No analytics charts.
- No marketing CTAs. No tips. No emoji.

---

## 5. Shared details (both views)

### 5.1 Sidebar (220px, identical both views)
- Fixed position, cream bg `#F6F1E8`.
- Logo wordmark top (Georgia 20px, vino).
- Nav items: `Inicio · Workflows · Bandeja · Conocimiento · Agentes · Conexiones · Configuración`.
- Active item: vino text + 2px vino left border + bg `#EEE7DA`.
- Badge count on `Bandeja (7)`.
- Bottom: 32×32 avatar circle + `Álvaro` (Inter 14) + `Owner` (Inter 12 muted). In View 2, show `Operador M.` + `Operator` instead.

### 5.2 Accessibility
- AA contrast minimum (vino on cream passes).
- Visible focus ring on every interactive element (2px vino outline + 2px offset).
- Never use color alone for state — always icon + label.
- Keyboard alternatives for every mouse-only action.

### 5.3 Responsive
1440 × 900 primary target. Must not break at 1280. No mobile/tablet.

---

## 6. Deliverables

**2 standalone HTML files**, all inline (CSS + HTML + inline SVG icons):
- `FaberLoom_v1_Builder.html`
- `FaberLoom_v1_Bandeja.html`

Each file includes the 3 variants as toggle-able states (small pill top-right).

Font imports: Google Fonts for Georgia fallback + Inter + JetBrains Mono. No other CDNs.

**Plus one note:** `NOTAS_DISEÑO.md` (≤ 300 words) explaining:
- Non-obvious visual decisions you made.
- Trade-offs.
- What you left out and why.
- Suggestions for next-round views (Admin Panel, Billing, Analytics).

---

## 7. Decision principles when in doubt

1. Pretty vs. productive for 20×/day Operator → **productive always**.
2. Impressive feature vs. reduced friction → **reduce friction**.
3. Density question → **one notch denser**.
4. Voice question → **editorial sober, not SaaS marketing**.
5. Show provenance/audit vs. hide for "clean" → **always show**.
6. Allow autonomy vs. lock until evidence → **lock by default**.

---

## 8. Out of scope (do NOT design)

Onboarding · Admin Panel · Billing · Connections setup · Agent marketplace · Analytics dashboard · Mobile · Homepage/marketing · Multi-language toggle · Dark mode.

If you need to reference one (e.g., "go to Conexiones"), use a text link only.

---

## 9. Closing

Final intent: when Álvaro shows this to 3 design partners, they understand in 30 seconds that FaberLoom is **not another chatbot, not another generic orchestration dashboard** — it's **where a LatAm SMB controls AI operations without losing human oversight or audit trail**.

Editorial. Dense. Auditable. Draft-first visible in every corner.

Build it.
