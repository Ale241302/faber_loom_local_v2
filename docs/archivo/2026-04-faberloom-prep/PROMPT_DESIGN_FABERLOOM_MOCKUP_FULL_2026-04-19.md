# PROMPT · FaberLoom v2 — Mockup Completo del Sistema

> **Para:** claude.ai/design (Claude Design)
> **Autor:** Álvaro Alfaro · CEO Muito Work · 2026-04-19
> **Objetivo:** generar un mockup completo, navegable, multiidioma, light+dark, accesible AA, con arquitectura modular, de la plataforma FaberLoom v2.
> **Idioma de output:** español por defecto, con keys i18n para ES/EN/PT-BR.
> **Sin límite de tokens.** Usá la máxima profundidad y detalle visual posibles.

---

## 0 · Lo que ya existe (no re-diseñar desde cero)

Esto **no es un greenfield**. Tomá como base de continuidad:

1. Prototipo previo `faberloom_v2.html` (~5800 líneas) — 13 rutas, 7 agentes, hash routing, vanilla JS, paleta editorial-warm coral+cream+dark.
2. Auditoría estratégica externa: 5 P1 blockers (feedback tipificado, learning thermometer + modal consolidación, P11 classifier + P12 propagación, provenance schema, action-risk registry) + 38 filas roadmap + snippets E.1–E.5.
3. Auditoría operativa local: 6 S1 blockers visuales + 332 llaves i18n + 176 hard-coded strings + 15 a11y issues + 60 filas roadmap.
4. Brand atmosphere C: Georgia italic display + Inter UI + JetBrains Mono evidencia · coral #C96442 · cream #F4F1ED · warm-dark #1F1E1C · evidence #6E1F2B · 6% dot-grid canvas · column-rule glosas marginales.
5. NOTAS_DISEÑO.md externo: tipografía con propósito (serif = "esto es un correo, no un ticket"), evidencia como único color activo del texto, autopilot **locked by default** con criterio textual ("67 % en 43 runs, se desbloquea ≥85 %") = contrato visible, no toggle.

**Tu trabajo es elevarlo a "vendible a partner B2B" y "auditable por un Operator nuevo en 5 minutos".** No clones lo que ya está; corregí, completá y refiná.

---

## 1 · Contexto del producto (no re-explicar al user)

**FaberLoom** = control plane de agentes de IA para SMB LatAm B2B.
**Wedge:** cotización B2B de calzado de seguridad industrial (Marluvas + Tecmater) con clientes desde México hasta Colombia.
**ICP inicial (3 design partners):** dos gratis + uno pago, distribuidores B2B de calzado seguridad o consumibles industriales con ≥5 cotizaciones/semana, sin equipo de IA in-house.
**Promesa diferencial:** *control plane > category theater*. Otros venden "plataforma de agentes"; FaberLoom vende **draft-first con evidencia**: ningún agente actúa sin que un humano apruebe un borrador con su procedencia visible.

**3 personas que ven la app:**

| Rol | Lo que necesita en pantalla | Ejemplo de tarea |
|---|---|---|
| **Operator** | Aprobar/corregir drafts rápido, ver evidencia, marcar feedback tipificado | "Hay 14 cotizaciones en bandeja, despachalas en 30 min" |
| **Owner** (CEO de la SMB) | Ver qué agentes están listos para subir nivel de autonomía, qué KPIs mejoraron, cuánto cuesta cada agente | "¿El agente de cotización ya merece auto-low?" |
| **Admin** (técnico de FaberLoom o partner) | Configurar conexiones, policies, knowledge base, versionado | "Conectar SAP del cliente nuevo a su workspace" |

---

## 2 · Principios de diseño (no negociables)

1. **Draft-first siempre visible.** Cada acción tiene un estado "borrador con evidencia" antes de ejecutarse. La evidencia es lo más legible de la pantalla.
2. **Procedencia como contrato visual.** Cada claim del draft lleva un superíndice `E1`, `E2`... que abre el span de evidencia en el panel derecho. Sin superíndice = sin claim = no se puede aprobar.
3. **Autonomy locked by default + evidence-gated unlock.** Cada nivel de autonomía (L0–L4) se desbloquea solo cuando el agente cumple un criterio cuantitativo visible ("≥85 % aprobado en 50 runs"). El gate es texto, no toggle.
4. **Color solo nunca señala estado.** Todo estado lleva ícono + texto + (opcionalmente) color. WCAG 2.1 AA mínimo.
5. **Tipografía con propósito.** Serif (Georgia) para títulos editoriales y asuntos de drafts (le dice al ojo "esto es un correo real"). Inter para UI funcional. JetBrains Mono solo para IDs, paths, snippets, claim spans (territorio "forense").
6. **Densidad sin piñata.** Linear-style: nodos con borde izquierdo 3 px de color por tipo, fondo neutral. Hover en `--bg-subtle`, no en azules Material.
7. **Modular y degradable.** Cada vista es un módulo independiente. Si un módulo crashea, el shell muestra una tarjeta degradada en su slot y el resto sigue navegable.
8. **Trilingüe nativo.** ES (default) · EN · PT-BR. Switch en topbar, persiste en localStorage. Cero string hardcoded en JSX/HTML — todo via `data-i18n="key"`.
9. **Light + dark paritarios.** No es un afterthought. Cada token, cada componente, ambos modos en el mockup.
10. **Accesibilidad como check de release.** Cada componente: focus-visible, role, aria-label cuando icon-only, contraste 4.5:1 mínimo body / 3:1 grandes, touch target ≥44×44, prefers-reduced-motion respetado.

---

## 3 · Sistema de tokens completo

### 3.1 Color (light)

```css
/* Surface */
--bg-canvas:        #FAF8F4;  /* cream base */
--bg-surface:       #FFFFFF;  /* card */
--bg-subtle:        #F4F1ED;  /* hover, secondary card */
--bg-sunken:        #EDE8E0;  /* code block, evidence panel */
--bg-overlay:       rgba(31, 30, 28, 0.48);

/* Stroke */
--stroke-default:   #E5DED2;
--stroke-strong:    #D4CABB;
--stroke-focus:     #C96442;  /* coral focus ring */

/* Text */
--text-primary:     #1F1E1C;
--text-secondary:   #4A4742;
--text-muted:       #6F6A62;  /* MIN 4.5:1 verificado */
--text-inverse:     #FAF8F4;
--text-evidence:    #6E1F2B;  /* vino tinto — único color activo en draft */

/* Accent */
--accent-primary:   #C96442;  /* coral */
--accent-primary-hover: #B35535;
--accent-primary-active: #9D4528;

/* Status (icon + text + color, nunca color solo) */
--status-success:   #4A7C4D;  /* verde tierra */
--status-warning:   #B57F2E;  /* ocre */
--status-danger:    #A53D2C;  /* rojo terracota */
--status-info:      #3F6B8A;  /* azul slate */
--status-neutral:   #6F6A62;

/* Node colors (canvas / agent typology) */
--node-trigger:     #4A7C4D;
--node-action:      #C96442;
--node-condition:   #B57F2E;
--node-skill:       #6E5494;  /* lavanda profunda */
--node-output:      #3F6B8A;
--node-loop:        #8A5A3F;
```

### 3.2 Color (dark)

```css
--bg-canvas:        #1F1E1C;
--bg-surface:       #2A2825;
--bg-subtle:        #34312D;
--bg-sunken:        #1A1917;
--bg-overlay:       rgba(0, 0, 0, 0.62);

--stroke-default:   #3F3B35;
--stroke-strong:    #524C44;
--stroke-focus:     #E07A57;  /* coral elevated 4.5:1 */

--text-primary:     #F4F1ED;
--text-secondary:   #C8C2B8;
--text-muted:       #9A9388;  /* CORREGIDO de 3.88 → 4.5:1 */
--text-inverse:     #1F1E1C;
--text-evidence:    #E89090;  /* CORREGIDO de 2.66 → 4.5:1 sobre bg-surface */

--accent-primary:   #E07A57;
--accent-primary-hover: #EA8B6B;
--accent-primary-active: #F09C80;

--status-success:   #7AAE7C;
--status-warning:   #DCA85A;
--status-danger:    #E07061;
--status-info:      #7BA5C2;
--status-neutral:   #9A9388;
```

### 3.3 Tipografía (escala de 13 niveles, nombrada)

| Token | Familia | Tamaño | Line-height | Letter-spacing | Weight | Uso |
|---|---|---|---|---|---|---|
| `--type-display-xl` | Georgia italic | 56 / 64 | 1.05 | -0.02em | 400 | Hero landing |
| `--type-display-lg` | Georgia italic | 40 / 48 | 1.1 | -0.015em | 400 | Section hero |
| `--type-display-md` | Georgia italic | 32 / 40 | 1.15 | -0.01em | 400 | Page title |
| `--type-display-sm` | Georgia italic | 24 / 32 | 1.2 | -0.005em | 400 | Card title editorial |
| `--type-heading-lg` | Inter | 22 | 1.3 | 0 | 600 | Section heading |
| `--type-heading-md` | Inter | 18 | 1.35 | 0 | 600 | Card heading |
| `--type-heading-sm` | Inter | 15 | 1.4 | 0 | 600 | Subheading |
| `--type-body-lg` | Inter | 16 | 1.55 | 0 | 400 | Lectura prolongada |
| `--type-body-md` | Inter | 14 | 1.5 | 0 | 400 | UI default |
| `--type-body-sm` | Inter | 13 | 1.45 | 0 | 400 | Captions, helper text |
| `--type-label-md` | Inter | 12 | 1.4 | 0.04em | 600 uppercase | Tags, badges |
| `--type-label-sm` | Inter | 11 | 1.35 | 0.06em | 700 uppercase | Micro-labels |
| `--type-mono` | JetBrains Mono | 13 | 1.5 | 0 | 400 | IDs, paths, claims, snippets |

### 3.4 Spacing, radius, motion, elevation

```css
/* Spacing — 4px base */
--space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px;
--space-5: 20px; --space-6: 24px; --space-8: 32px; --space-10: 40px;
--space-12: 48px; --space-16: 64px; --space-20: 80px; --space-24: 96px;

/* Radius */
--radius-sm: 4px; --radius-md: 6px; --radius-lg: 10px;
--radius-xl: 16px; --radius-pill: 9999px;

/* Stroke widths — GLOBAL 1.5, never hardcoded */
--stroke-thin: 1px; --stroke-md: 1.5px; --stroke-thick: 2px;

/* Elevation (shadow) */
--shadow-sm: 0 1px 2px rgba(31,30,28,0.06);
--shadow-md: 0 4px 12px rgba(31,30,28,0.08);
--shadow-lg: 0 12px 32px rgba(31,30,28,0.12);
--shadow-overlay: 0 24px 64px rgba(31,30,28,0.24);

/* Motion */
--ease-out: cubic-bezier(0.22, 1, 0.36, 1);
--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
--dur-fast: 120ms; --dur-base: 200ms; --dur-slow: 320ms;

/* Respect prefers-reduced-motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### 3.5 Focus ring (global)

```css
:where(button, a, input, select, textarea, [role="button"], [tabindex]):focus-visible {
  outline: 2px solid var(--stroke-focus);
  outline-offset: 2px;
  border-radius: var(--radius-md);
}
```

---

## 4 · Inventario de pantallas (13 rutas + nuevas)

Cada ruta es un **módulo independiente** con contrato `{ mount, unmount, onError }`. Si crashea, el shell muestra `<DegradedCard moduleId="X" error={err} />` en su slot.

### 4.1 Layout global (shell)

```
┌─────────────────────────────────────────────────────────────┐
│  Topbar:  [logo isotipo + wordmark]  [⌘K palette trigger]   │
│                          [lang switch ES|EN|PT-BR] [theme] │
│                          [user menu]                        │
├──────────┬──────────────────────────────────────────────────┤
│ Sidebar  │  Main slot (módulo activo)                       │
│ ◦ Dash   │                                                  │
│ ◦ Bandeja│                                                  │
│ ◦ Agentes│                                                  │
│ ◦ Skills │                                                  │
│ ◦ Workfl.│                                                  │
│ ◦ Conex. │                                                  │
│ ────     │                                                  │
│ ◦ Admin  │                                                  │
│ ◦ Settings│                                                 │
│ ◦ Factory│                                                  │
└──────────┴──────────────────────────────────────────────────┘
```

Sidebar: 240 px (expanded) / 64 px (collapsed, solo iconos). Topbar: 56 px.

### 4.2 Las 13 rutas + 2 nuevas

| # | Ruta | Módulo | Propósito en una línea |
|---|---|---|---|
| 1 | `#/` | landing | Hero editorial + 3 propuestas + 1 CTA único ("Cotizá tu primer draft") |
| 2 | `#/dashboard` | dashboard | Panel del Owner: KPIs por agente, runs hoy, lo que requiere atención |
| 3 | `#/bandeja` | bandeja | Cola unificada de drafts pendientes de aprobación (subdivisiones: por agente, por riesgo, por antigüedad) |
| 4 | `#/bandeja/:id` | bandeja-draft | Vista detalle: draft a la izquierda, evidencia a la derecha, actions abajo (aprobar / corregir / rechazar / consolidar) |
| 5 | `#/agentes` | agentes-list | Tabla de agentes con KPIs, nivel de autonomía, salud, costo |
| 6 | `#/agentes/:id` | agent-console | Detalle de un agente: 4 tabs (Resumen / Skills / Memoria / Logs) |
| 7 | `#/skills/:id` | skill-studio | Editor de skill: 3 capas (Base sellada / Overlay manual / Overlay aprendido con gate) + Learning Thermometer |
| 8 | `#/workflows` | workflows | Builder visual: canvas con nodos (trigger/action/condition/skill/output/loop), borde izquierdo 3 px de color por tipo |
| 9 | `#/conexiones` | conexiones | Conectores instalados, estado de cada uno, OAuth/API key management |
| 10 | `#/settings` | settings | Settings personales: perfil, notificaciones, idioma, tema, atajos |
| 11 | `#/admin` | admin | Admin del workspace: 3 grupos (Personas / Operación / Plataforma) con breadcrumb |
| 12 | `#/admin/autonomy-evidence` | admin-autonomy | **NUEVA** — pantalla de evidencia de autonomía: curva histórica de aprobación por agente, distribución de correcciones, qué tipo de draft aún falla |
| 13 | `#/factory` | factory | **NUEVA** — Agent Factory: wizard para crear un agente nuevo desde una plantilla o desde cero |
| 14 | (overlay) | launcher | Command palette ⌘K con focus trap + role="dialog" |
| 15 | (overlay) | feedback-modal | Modal "5 razones" tipificadas al rechazar/corregir |
| 16 | (overlay) | consolidation-modal | Modal de consolidación 4 secciones (qué se aprendió, dónde aplica, qué impacta, confirmar/descartar) |

### 4.3 Wireframe verbal por pantalla — DETALLE

#### 4.3.1 Landing (`#/`)

- Hero: 56px Georgia italic title, 18px Inter subtitle, 1 CTA coral, dot-grid 6% behind.
- 3 cards horizontales, borde izquierdo 3 px por color:
  - "Aprobá con evidencia" (verde)
  - "Subí autonomía con datos" (coral)
  - "Conectá lo que ya usás" (azul)
- Footer minimal: lang switch + theme + 3 links (privacidad, términos, contacto).

#### 4.3.2 Dashboard (`#/dashboard`)

- Grid 12 cols, 24 px gutter.
- Row 1: 4 KPI cards (Drafts pendientes / Aprobados hoy / Tasa aprobación 7d / Costo runs 7d).
- Row 2 (8/4 split):
  - Izq: tabla "Agentes que requieren atención" (max 5 rows, badge de razón).
  - Der: card "Próximo unlock" — agente más cercano a subir nivel + barra de progreso + criterio textual.
- Row 3: timeline editorial de últimas 8 acciones del workspace.

#### 4.3.3 Bandeja list (`#/bandeja`)

- Filtros sticky top: agente / riesgo / antigüedad / búsqueda libre.
- Lista vertical, cada item: avatar de agente + asunto en Georgia 18px + 2 líneas preview Inter 13px + chips de estado a la derecha (action-risk badge + autonomy level + tiempo en cola).
- Empty state: ilustración minimal + "Bandeja al día. Última aprobación hace 12 min."

#### 4.3.4 Bandeja detail (`#/bandeja/:id`)

**Layout 2 columnas (60/40):**

- Izquierda: el draft renderizado como correo real:
  - Header: De / Para / Asunto en Georgia 22px italic.
  - Body con superíndices `E1`, `E2`... en `var(--text-evidence)` para cada claim.
  - Hover sobre superíndice: highlight del span correspondiente en panel derecho.
  - Footer: action bar sticky con 4 botones (Aprobar coral / Editar / Rechazar / Consolidar como aprendizaje) + action-risk badge prominente.
- Derecha: panel de evidencia:
  - Tabs: Evidencia / Provenance / Action-risk / Run trace.
  - Tab Evidencia: lista de spans, cada uno con `claim_id`, `evidence_span_id`, `source` (KB doc + version + line range), botón "Abrir en KB".
  - Tab Provenance: árbol que conecta claim → evidence → source_doc → source_version.
  - Tab Action-risk: 6 campos del registro (risk_class, approval_mode, reversible, customer_visible, financial_impact, source_of_truth).
  - Tab Run trace: timeline del workflow state ledger de esta ejecución.

#### 4.3.5 Agentes list (`#/agentes`)

- Tabla con sticky header. Columnas: Avatar+Nombre / Estado salud (badge) / Autonomy level (stepper visual L0–L4) / Drafts 7d / Tasa aprob. 7d / Costo 7d / Próximo unlock / Acciones.
- Click en row abre `agent-console`.
- Filtro por estado (activo / pausado / en shadow / archivado).

#### 4.3.6 Agent Console (`#/agentes/:id`) — 4 TABS REALES

| Tab | Contenido |
|---|---|
| **Resumen** | KPIs grandes, autonomy ladder con criterio del próximo unlock, Learning Thermometer del agente (🔵 Frío / 🟡 Tibio / 🔴 Caliente), última actividad |
| **Skills** | Lista de skills compuestas (un agente = N skills). Cada skill: nombre, capa activa, % aprobado, link a `#/skills/:id` |
| **Memoria** | 3 capas (sesión / proyecto / global), lista de hechos memorizados con "Olvidar" inline, eventos de consolidación recientes |
| **Logs** | Workflow state ledger filtrable, cada run expandible con steps, errores, tokens consumidos |

#### 4.3.7 Skill Studio (`#/skills/:id`) — 3 CAPAS

```
┌─────────────────────────────────────────────────────────┐
│  Skill: Cotizar calzado seguridad B2B                   │
│  [Capa Base ▾] [Overlay manual] [Overlay aprendido]    │
├─────────────────────────────────────────────────────────┤
│ ╔══ Capa Base (sellada) ════════════════════════════╗   │
│ ║ Read-only · v1.0.3 · publicada 2026-03-12        ║   │
│ ║ <code en JetBrains Mono, 13px>                   ║   │
│ ╚══════════════════════════════════════════════════╝   │
│                                                         │
│ ╔══ Overlay manual (editable) ══════════════════════╗   │
│ ║ Reglas locales que el Owner edita libremente     ║   │
│ ║ [+ Agregar regla] [Versionar]                    ║   │
│ ╚══════════════════════════════════════════════════╝   │
│                                                         │
│ ╔══ Overlay aprendido (gate humano) ════════════════╗   │
│ ║ 🔴 Caliente — 7 patrones por consolidar          ║   │
│ ║ [Abrir Learning Thermometer]                     ║   │
│ ║ Reglas activas: 4 · Pendientes: 7 · Revertidas: 1║   │
│ ╚══════════════════════════════════════════════════╝   │
│                                                         │
│ Sidebar derecho: Gold samples (13 campos cada uno)     │
└─────────────────────────────────────────────────────────┘
```

#### 4.3.8 Workflows (`#/workflows`)

- Canvas full-bleed con dot-grid 6% opacity.
- Nodos: 200×80 px, fondo `--bg-surface`, borde izquierdo 3 px coloreado por tipo (ver §3.1 node colors).
- Conectores: SVG paths (idealmente) o columnas CSS + pseudo-elementos para el mockup (aceptable a esta fidelidad).
- Sidebar izq: paleta de nodos arrastrables.
- Sidebar der: inspector del nodo seleccionado.
- Toolbar superior: zoom, fit, mini-map, run, deploy.

#### 4.3.9 Conexiones (`#/conexiones`)

- Grid de cards 4 cols. Cada card: logo del conector (Gmail, SAP, Hubspot, WhatsApp, etc.), estado (connected/expired/disconnected con ícono+texto+color), última sync, botón Reconectar/Desconectar.
- Empty state: "Aún no hay conexiones. Empezá por Gmail para hacer cotizaciones." + CTA.

#### 4.3.10 Settings (`#/settings`)

- Layout 2 columnas. Izq: nav de secciones (Perfil / Notificaciones / Idioma y región / Tema / Atajos / Privacidad).
- Der: form de la sección activa. Cada campo con label, input, helper text, error state.
- Idioma: radio cards ES / EN / PT-BR con preview de la UI en miniatura.

#### 4.3.11 Admin (`#/admin`) — REORGANIZADO 10 → 3 grupos

| Grupo | Tabs |
|---|---|
| **Personas** | Usuarios / Roles / Invitaciones |
| **Operación** | Policies / Aprobaciones / SLAs |
| **Plataforma** | Knowledge base / Conectores admin / Auditoría / Billing |

Breadcrumb: `Admin / Personas / Usuarios`. Sticky.

#### 4.3.12 Admin · Autonomy Evidence (`#/admin/autonomy-evidence`) — NUEVA

- Selector de agente (dropdown).
- Curva de aprobación a 90 días (line chart, eje Y % aprobado, eje X fecha, banda gris para criterio de unlock).
- Distribución de correcciones del Operator (donut: por tipo — claim mal sourced / tono / dato faltante / acción riesgosa / otro).
- Tabla "Tipos de draft que aún fallan" (cada row: tipo, % aprob, drafts/sem, link a Skill Studio para iterar).
- CTA "Promover a L2" — disabled hasta cumplir criterio, con tooltip que explica qué falta.

#### 4.3.13 Factory (`#/factory`) — NUEVA

- Wizard 3 pasos:
  1. **Plantilla**: cards de plantillas (Cotización B2B / Soporte tier-1 / Outbound / En blanco).
  2. **Configuración**: nombre, descripción, conectores requeridos, KB que indexa, autonomy inicial (default L0 Shadow).
  3. **Confirmación**: resumen + checklist de prerrequisitos.
- Stepper sticky top con progreso.

#### 4.3.14 Launcher ⌘K (overlay)

- Overlay con `role="dialog"` y `aria-modal="true"`.
- Focus trap automático, Esc cierra.
- Input de búsqueda 18px, lista de resultados con keyboard nav, agrupados (Acciones / Agentes / Drafts / Conexiones / KB).
- Atajos: ⌘K abrir, ↑↓ navegar, Enter ejecutar, Tab cambiar grupo.

#### 4.3.15 Feedback modal (overlay)

5 razones tipificadas (basado en snippet E.1 del audit externo):

| Razón | Qué loggea |
|---|---|
| Claim sin evidencia suficiente | Marca `claim_id` problemático, alimenta P11 classifier |
| Tono no acorde con cliente | Etiqueta el span, va a refinement de skill |
| Dato incorrecto / desactualizado | Marca `source_version`, dispara aviso a KB owner |
| Acción riesgosa para el contexto | Sube `risk_class` del action en registry |
| Otro (texto libre) | Va a triage manual, no auto-aprende |

Cada razón con icono + checkbox + textarea opcional. Botón "Enviar feedback" coral, "Cancelar" texto.

#### 4.3.16 Consolidation modal (overlay)

4 secciones (basado en thermometer + memoria de proyecto):

1. **Qué se aprendió** — patrón sintetizado de los N feedbacks acumulados.
2. **Dónde aplica** — eje 3D: tipo (Knowledge / Instrucción / Output) × alcance (Usuario / Skill / Agente / Org) × propagación cross-skill (sí/no, cuáles).
3. **Qué impacta** — preview de drafts simulados antes/después.
4. **Confirmar / Descartar** — botón coral "Indexar como overlay aprendido" + botón texto "Descartar y mantener manual".

Header del modal: 🔴 Caliente badge + contador "7 patrones acumulados desde 2026-04-12".

---

## 5 · Widgets reusables (especificar en design-system)

| Widget | Anatomía | Estados |
|---|---|---|
| **Learning Thermometer** | Pill con ícono temperatura + texto + contador | 🔵 Frío 0–2 / 🟡 Tibio 3–5 / 🔴 Caliente 6+ |
| **Autonomy Ladder** | Stepper horizontal 5 nodos (L0 Shadow / L1 Propone / L2 Auto-low / L3 Auto+notif / L4 Auto+excep) | Active, completed, locked (con criterio textual en tooltip) |
| **Action-risk badge** | Pill con ícono + label | low (verde), medium (ocre), high (rojo), critical (rojo borde grueso) |
| **Provenance sup marker** | `<sup>E1</sup>` en `var(--text-evidence)` | default, hover (highlight span), focused (ring) |
| **Empty state** | Ilustración minimal + título + descripción + CTA | 3 variantes: zero (nunca hubo data), filtered (filtro vacía), error (degraded) |
| **Skeleton loader** | Bloques `--bg-subtle` con shimmer 1.4s | full-card, list-row, table-row |
| **Degraded card** | Card con ícono warning + "Módulo X no disponible" + botón "Reintentar" | Para fault isolation modular |

---

## 6 · Estados a entregar (3 por pantalla mínimo)

Para cada pantalla ≥1 ruta, entregar:

1. **Loaded** (con data realista — no lorem ipsum, usar contexto B2B calzado seguridad).
2. **Empty** (zero data + CTA correcto).
3. **Loading** (skeleton de la estructura, no spinner genérico).
4. **Error / Degraded** (card de error en el slot, resto del shell sigue funcional).

Pantallas con mutación (Skill Studio, Settings, Factory): agregar estado **Saving** y **Saved** con confirmación visual.

---

## 7 · Internacionalización

- Sistema de keys plano: `bandeja.list.empty.title`, `agent.console.tab.skills`, etc.
- 332 keys mínimo, agrupadas en 20 dominios (nav, status, autonomy, bandeja, agent, skill, action, empty, error, dialog, tooltip, admin, settings, launcher, landing, dashboard, draft, workflow, conn, intl).
- Switch en topbar con 3 opciones (ES, EN, PT-BR), persiste en `localStorage.faberloom.lang`.
- Convención: `data-i18n="key"` en HTML, resolver carga el JSON correspondiente al idioma.
- Mostrar el mockup en **ES como default**, pero entregar archivo `i18n.json` con las 332 keys en los 3 idiomas.
- Cuidado especial: textos de Georgia italic display deben verse bien en pt-BR (palabras con tilde + ç) y EN (sin tildes — testar kerning).

---

## 8 · Accesibilidad — checklist de release

Aplicar a cada componente:

- `aria-label` en todo botón icon-only.
- `role` apropiado en cada landmark (`banner`, `navigation`, `main`, `complementary`, `contentinfo`).
- Foco visible 2 px coral con offset 2 px en todo elemento interactivo.
- Contraste verificado: 4.5:1 body, 3:1 large text (≥18px o ≥14px bold), 3:1 UI components vs background.
- Touch targets ≥44×44 px en mobile.
- `prefers-reduced-motion` apaga animaciones decorativas.
- `prefers-color-scheme` respetado, override manual posible.
- `dialog` overlays con focus trap, `aria-modal="true"`, Esc cierra.
- Tablas con `<th scope>`, `<caption>` cuando aplica.
- Form: cada `<input>` con `<label>` asociado, errores via `aria-describedby` y `role="alert"`.
- Skip link "Saltar al contenido principal" como primer focusable.

Validación recomendada: axe-core inyectado en runtime (CDN: `https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.4/axe.min.js`). Cero violations críticos al cargar cada ruta.

---

## 9 · Arquitectura modular (REQUERIDO)

El mockup debe entregarse como **módulos independientes**, no como single-file monolítico. Estructura:

```
faberloom-mockup/
├── index.html                 # shell vacío + bootstrap
├── core/
│   ├── boot.js                # arma router, carga i18n, monta shell
│   ├── shell.js               # topbar + sidebar + main slot
│   ├── router.js              # hash router con error boundary
│   ├── bus.js                 # pub/sub para comunicación entre módulos
│   ├── store.js               # localStorage adapter versionado
│   ├── i18n.js                # resolver data-i18n
│   ├── a11y.js                # focus trap, live regions
│   └── tokens.css             # tokens sellados light + dark
├── modules/
│   ├── landing/
│   ├── dashboard/
│   ├── bandeja/
│   ├── agentes/
│   ├── agent-console/
│   ├── skill-studio/
│   ├── workflows/
│   ├── conexiones/
│   ├── settings/
│   ├── admin/
│   ├── admin-autonomy/
│   ├── factory/
│   └── launcher/
├── widgets/
│   ├── thermometer/
│   ├── autonomy-ladder/
│   ├── action-risk-badge/
│   ├── provenance-sup/
│   ├── feedback-modal/
│   ├── consolidation-modal/
│   ├── empty-state/
│   ├── skeleton/
│   └── degraded-card/
└── i18n/
    ├── es.json
    ├── en.json
    └── pt-BR.json
```

**Reglas inquebrantables:**

1. Cada módulo exporta `{ meta, mount, unmount, onError }`.
2. Cero imports directos entre módulos. Comunicación solo via `bus.emit / bus.on`.
3. Estado compartido solo en `core/store`. Nunca globals mutables.
4. Cada módulo tiene su propio CSS scoped (prefijo `.m-{id}-*` o BEM).
5. El shell envuelve cada `mount()` en try/catch — si crashea, renderiza `<DegradedCard moduleId={id} />` en su slot. El resto sigue funcionando.
6. Cada módulo es lazy: solo se carga cuando su ruta se activa.
7. `core/tokens.css` carga primero, sellado, nadie puede pisar variables raíz.

---

## 10 · Restricciones técnicas

- **No frameworks pesados.** Vanilla JS + CSS + (opcional) build con esbuild.
- **No localStorage ni sessionStorage en bloque artifact**. Si claude.ai/design impone esto, simular con variable JS in-memory que persiste durante la sesión.
- **No CDN de librerías visuales propietarias.** Permitido: axe-core, JetBrains Mono, Inter, Georgia (system).
- **Sin imágenes externas excepto SVG inline.** Iconos: usar set lucide-react o feather, embebido como SVG.
- **HTML semántico**. Nada de `<div onclick>` cuando un `<button>` aplica.
- **Validar con `node --check`** todo JS antes de entregar. Si refactorizás HTML, eliminar refs JS huérfanas.

---

## 11 · Entregables esperados

1. **`index.html`** + estructura modular completa según §9.
2. **`design-system.html`** — página standalone que muestra todos los tokens, tipografía, componentes y widgets en light + dark, lado a lado.
3. **`i18n/{es,en,pt-BR}.json`** — 332 keys mínimo.
4. **`README.md`** del mockup con: cómo correr, mapa de módulos, contrato de cada uno, atajos de teclado, checklist a11y.
5. **`CHANGELOG_DESIGN.md`** — qué cambió respecto al `faberloom_v2.html` original, qué resuelve cada cambio (referenciar S1/P1 que cierra).

---

## 12 · Criterios de aceptación

- [ ] 13 rutas + 2 nuevas, todas navegables.
- [ ] 4 estados (loaded / empty / loading / error) en cada ruta.
- [ ] Light + dark paritarios, sin gaps de contraste.
- [ ] 3 idiomas funcionando con switch persistente.
- [ ] axe-core runtime: 0 violations críticos en cada ruta.
- [ ] focus-visible global, skip link presente.
- [ ] prefers-reduced-motion respetado.
- [ ] Cada módulo crashable individualmente sin tumbar el shell (probar con `throw new Error('test')` en mount de uno y verificar que los otros siguen).
- [ ] ⌘K con focus trap real, Esc cierra.
- [ ] Provenance superíndices funcionando: hover en `E1` highlightea span en panel evidencia.
- [ ] Learning Thermometer + Modal Consolidación implementados al menos en Skill Studio.
- [ ] Autonomy Ladder presente en Agent Console y Admin Autonomy Evidence.
- [ ] Action-risk badge presente en Bandeja detail y en cada nodo de Workflow.
- [ ] Feedback modal con 5 razones tipificadas presente en Bandeja detail.

---

## 13 · Tono visual y voz

**Atmósfera C — editorial-warm Claude-adjacent.** No es Linear, no es Notion, no es Material. Tiene alma editorial (revistas tipo *Monocle* o *Eye Magazine*) cruzada con disciplina de control plane (Stripe Dashboard).

**Voz UI:**
- Directa, sin condescendencia. ("14 drafts esperando" no "Tienes 14 elementos pendientes en tu bandeja").
- Específica con números cuando hay datos ("85 % aprobado en 50 runs" no "buen desempeño").
- Honesta cuando no se puede ("Este agente aún no califica para L2. Le faltan 12 runs aprobados consecutivos").
- Cero jerga IA cuando se puede evitar ("evidencia" no "RAG citation"; "borrador" no "draft" en strings ES; "aprobar" no "validate"; "consolidar" no "ingest").
- Emocional cero. Esto es B2B, no consumer.

**Glosas marginales (NOTAS_DISEÑO column-rule):** en pantallas con concepto nuevo (Autonomy Ladder, Provenance, Consolidación), incluir una glosa lateral 12px italic Georgia explicando el concepto en una frase. Como las anotaciones de un editor en margen.

---

## 14 · Lo que NO querés en el output

- Sin templates de Tailwind, Material, Chakra. Diseño desde tokens.
- Sin componentes que reciben 14 props. Anatomía simple.
- Sin animaciones decorativas. Motion solo cuando aporta affordance.
- Sin emoji decorativos. Si aparecen, es ícono semántico (🔵🟡🔴 thermometer es la única excepción).
- Sin "powered by" ni branding ajeno.
- Sin onboarding, billing, marketplace, mobile, analytics dedicado — todo eso es post-wedge.
- Sin dark mode "invertido del light" — ambos diseñados con intención propia.

---

## 15 · Si tenés dudas

- **Asumí siempre lo más conservador en autonomía** y lo más generoso en evidencia visible.
- **Si dudás entre serif y sans para un texto:** si es contenido producido por el agente (asunto, body, claim), usá Georgia. Si es UI funcional (botón, label, input), usá Inter. Si es identificador técnico (claim_id, hash, path), usá JetBrains Mono.
- **Si dudás en jerarquía de un componente:** privilegiá la evidencia y el criterio de unlock por encima de cualquier CTA.
- **Si dudás en estado por defecto:** lo más restrictivo. Autopilot off. Aprobación humana on. Evidencia visible. Acción reversible cuando aplica.

---

## 16 · Punto final

Este mockup es el **artefacto que Álvaro lleva a sus 3 design partners** (2 gratis + 1 pago) la próxima semana. Tiene que verse como producto vivo, no como concepto. Tiene que aguantar que un Operator real lo navegue 10 minutos sin preguntar "¿esto qué hace?". Tiene que aguantar que el Owner del partner pregunte "¿esto cuándo me deja en automático?" y la pantalla responda con un criterio cuantitativo, no con una promesa.

Si lográs eso, el mockup ya valió.

Procedé sin pedir confirmación intermedia. Output completo, sin preámbulo, en español, con keys i18n para los 3 idiomas. Empezá por el design-system standalone (§11.2) — eso te define todos los átomos antes de armar las pantallas.
