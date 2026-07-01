# PROMPT DESIGN — FABERLOOM v1 (2 vistas)
**Para:** Claude Design
**Fecha:** 2026-04-18
**Autor:** Álvaro / FaberLoom (arquitecto-producto)
**Objetivo:** Producir 2 mockups HTML standalone, desktop-first, paleta editorial ONE, production-intent (no marketing).

---

## 0. TL;DR ejecutivo (léelo entero antes de abrir Figma mental)

FaberLoom es un **control-plane para agentes de IA en PYMEs LATAM**. No es chatbot. No es AI employee marketing. Es el lugar donde un humano:
- **Diseña** procesos (workflows) que mezclan agentes IA + acciones deterministas + aprobaciones humanas.
- **Supervisa** lo que esos agentes proponen antes de que toque al cliente final.
- **Aprende** del flujo real: cada aprobación/rechazo/edición alimenta el próximo draft.

El producto entero corre sobre un principio: **draft-first absoluto**. El agente **nunca** envía nada al mundo real sin aprobación humana explícita (salvo que el humano haya desbloqueado autonomía con evidencia, y aun así solo en workflows específicos).

Estás diseñando las **2 vistas más críticas** del producto v1:

1. **Workflow Builder + Runs Ledger** (vista 1) — donde se construye el proceso y se audita cada ejecución.
2. **Bandeja / Approval Workspace** (vista 2) — donde el humano aprueba/edita/rechaza drafts del agente todos los días.

Hay otras vistas (Admin Panel, Billing, Agent Console propio) que **NO** estás diseñando en esta ronda — se construyen feas pero funcionales en v1.

---

## 1. Contexto de producto (para que entiendas decisiones visuales)

### 1.1 Qué es FaberLoom
SaaS B2B multi-tenant para PYMEs 5–50 empleados en LATAM. Integra Email + Knowledge Base + Agent Builder. Los agentes clasifican correos, redactan respuestas, citan documentos, proponen cotizaciones, actualizan CRM — siempre como **draft** que un humano aprueba.

### 1.2 Wedge v1 (caso de uso real a diseñar para)
**Cotización B2B de calzado de seguridad industrial** (distribuidores de Marluvas/Tecmater en LatAm).
- Entra correo de cliente final pidiendo cotización para 120 pares Marluvas modelo 50S19.
- Agente "QuoteBot" lee, extrae modelo/cantidad/tallas, cruza con catálogo+precios+existencias, redacta cotización en voz de la empresa, cita fuentes (claim → evidence → source).
- Humano abre Bandeja, revisa draft, aprueba → sale a cliente por Gmail. O edita → el agente aprende. O rechaza → el agente aprende.

Diseña para este caso. No para "AI employee genérico".

### 1.3 Roles (matriz de permisos simplificada para estas 2 vistas)
- **Owner** (dueño PYME): todo.
- **Admin**: todo menos billing/ownership.
- **Operator**: ejecuta Bandeja, ve sus workflows, no edita workflows productivos. Puede editar Drafts.
- **Viewer**: solo lectura.

Para **Vista 1 (Builder)**: asume rol **Owner/Admin**.
Para **Vista 2 (Bandeja)**: asume rol **Operator**.

### 1.4 Arquitectura mental (NO la diseñes, pero respétala)
- **3 objetos por agente**: AgentSpec (estático) · AgentRuntime (estado actual) · AgentMemory (acumulado).
- **State machine del agente**: drafting → awaiting_approval → approved → executing → completed / failed / escalated.
- **Autonomy ladder L0–L5** como unlock rubric **interno** (no lo publiques como branding — sí puede aparecer en UI del Builder como indicador "L0 Shadow" / "L1 Copilot"). No pongas banners marketing de "L5 Full Autonomous".
- **Memoria 3 capas**: run/session · account/org · curated long-term. No inventes 5.

### 1.5 Principios UX no negociables
| # | Principio | Implicación visual |
|---|---|---|
| 1 | **Draft-first absoluto** | Todo lo que puede tocar al cliente final pasa por estado `awaiting_approval` visible. Nunca "envía en segundo plano sin preguntar". |
| 2 | **Provenance visible** | Cada claim del agente muestra de dónde vino (doc + versión + snippet). Highlight inline sobre el draft, con click → panel evidence. |
| 3 | **Reversibilidad** | Toda acción destructiva o externa tiene undo ≤ 10s. Rollback de workflow publicado = 1 clic. |
| 4 | **Control > autonomía** | El toggle Copilot ↔ Autopilot existe, pero Autopilot se **desbloquea** con evidencia (aceptación ≥X%, policy gates OK, volumen mínimo). No es un switch libre. |
| 5 | **Policy gates antes de ejecutar** | Enviar correo, tocar CRM, comprometer dinero: pasa por policy engine. En UI, si bloquea, explicar **por qué** en lenguaje humano. |
| 6 | **No inventar datos** | Estados vacíos honestos. "Sin datos aún, corré tu primer workflow para empezar" en vez de gráficas falsas. |
| 7 | **Audit trail inmutable** | Runs Ledger muestra todo. Nunca "ocultar" ejecuciones fallidas. |

---

## 2. Paleta y sistema visual (OBLIGATORIO)

Tomás como referencia exacta el archivo `FaberLoom ONE _standalone_.html` (editorial serif). No uses el "THREE" (Bold Block — demasiado marketing).

### 2.1 Colores
```
Fondo principal:       #F6F1E8  (cream/off-white editorial)
Fondo panel elevado:   #FFFFFF  (cards)
Fondo sutil/hover:     #EEE7DA
Texto principal:       #1A1A1A
Texto secundario:      #5A5A5A
Texto muted:           #8A8A8A
Acento primario:       #6E1F2B  (vino profundo — botones primarios, headings clave)
Acento hover:          #531A23
Borde sutil:           #D8D0C0
Success (discreto):    #2E6B4F
Warning (discreto):    #A87820
Error (discreto):      #9C2B2B
```
**Regla:** nada de gradientes saturados. Nada de purple/blue SaaS-genérico. Nada de neon. Editorial, no Silicon Valley.

### 2.2 Tipografía
- **Display / H1–H3**: Georgia (serif) — para titulares, nombres de vista, nombres de workflow.
- **UI / body / labels**: Inter (sans) — todo lo demás.
- Jerarquía:
  - H1 Georgia 32–36px weight 500
  - H2 Georgia 24px weight 500
  - H3 Georgia 18px weight 500
  - Body Inter 14px weight 400
  - Small Inter 12px weight 400
  - Mono (logs/IDs): JetBrains Mono o ui-monospace 12px

### 2.3 Espaciado y grid
- Grid 8px base.
- Paddings de panel: 24px.
- Radios: 4px (inputs), 8px (cards), 12px (modales).
- Shadow: casi invisible. `0 1px 2px rgba(0,0,0,0.04)` máximo. Prefiere bordes 1px sobre sombras.

### 2.4 Densidad
**Densa pero respirable**. No Notion-marketing (mucho aire). No Bloomberg (saturado). Pensá Linear + NYT. El usuario Operator abre Bandeja 20 veces por día — cada clic y scroll cuenta.

### 2.5 Componentes base (defínelos consistentes en los 2 mockups)
- Botón primario: vino sólido, texto cream.
- Botón secundario: borde vino 1px, texto vino, fondo transparente.
- Botón tertiary/ghost: solo texto vino con underline en hover.
- Input: borde 1px #D8D0C0, focus #6E1F2B.
- Badge de estado: pill pequeño, fondo tonificado del color, texto del mismo.
- Tab: underline animado 2px bajo texto activo.

---

## 3. VISTA 1 — Workflow Builder + Runs Ledger

### 3.1 Propósito
Un humano diseña un proceso (workflow) como cadena visual de nodos: triggers → agentes + acciones → approvals → outputs. Luego lo **publica** y ve cada ejecución real en Runs Ledger abajo.

### 3.2 Estructura de pantalla

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ [Sidebar izq 220px fijo]                [Main area flex]                     │
│                                                                              │
│  FaberLoom                              Workflows > Cotización B2B Marluvas  │
│  ─────────                              ─────────────────────────────────────│
│  Home                                   [Draft ●] [Live ○]  [Publish]  [⟲]  │
│  Workflows    ←activo                                                        │
│  Bandeja (7)                            ┌────────────────────────────────┐   │
│  Conocimiento                           │   CANVAS — nodos conectados    │   │
│  Agentes                                │                                │   │
│  Conexiones                             │   ◉ Trigger: Gmail nuevo       │   │
│  Configuración                          │      ↓                         │   │
│                                         │   ◆ Agent: QuoteBot (classify) │   │
│  ─────────                              │      ↓                         │   │
│  Alvaro · Owner                         │   ◆ Agent: QuoteBot (draft)    │   │
│                                         │      ↓                         │   │
│                                         │   ⚐ Policy gate: $ > 10k       │   │
│                                         │      ↓                         │   │
│                                         │   ✋ Approval: Operator        │   │
│                                         │      ↓                         │   │
│                                         │   ↗ Action: Send via Gmail     │   │
│                                         │                                │   │
│                                         │   [+ Add node]                 │   │
│                                         └────────────────────────────────┘   │
│                                                                              │
│                                         ╔══ RUNS LEDGER (últimos 30) ══╗    │
│                                         ║ #1284 ✓ Completed  12:04 PM  ║    │
│                                         ║ #1283 ⚠ Awaiting   11:58 AM  ║    │
│                                         ║ #1282 ✗ Failed     11:52 AM  ║    │
│                                         ║ #1281 ✓ Completed  11:40 AM  ║    │
│                                         ║ [Ver todos →]                ║    │
│                                         ╚═══════════════════════════════╝    │
│                                                                              │
│                                         [Panel derecho contextual 360px]    │
│                                         ── Al seleccionar nodo ──            │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Elementos clave

**3.3.1 Header de workflow**
- Breadcrumb: `Workflows > Cotización B2B Marluvas`
- Toggle **Draft ● / Live ○** (dos estados visuales claros). Nunca los dos al mismo tiempo activos.
- Botón **Publish** (primario). Si Draft == Live (sin cambios): deshabilitado.
- Botón **Rollback** (icono ⟲, tertiary): revierte Live al commit anterior. Confirmación modal.
- Indicador pequeño: `Última publicación: hace 3h por Álvaro` con tooltip al versión/hash.

**3.3.2 Canvas (centro, ocupa ~60% altura del main area)**
- Nodos conectados por líneas. Tipos de nodo con iconografía distinta:
  - `◉` Trigger (círculo lleno vino)
  - `◆` Agent node (diamante vino)
  - `⚙` Action/tool node (engranaje gris)
  - `⚐` Policy gate (banderín naranja sutil)
  - `✋` Approval gate (mano vino)
  - `↗` Output/side-effect node (flecha)
- Click en nodo → panel derecho contextual 360px con su config (no abrir modal).
- Nodos muestran badge de **risk_class** si hay side effect (ej. "Customer-visible", "Financial").
- Zoom/pan básico. No inventar features de Figma.
- Botón `+ Add node` al final del flow inserta nodo antes del último.

**3.3.3 Panel derecho contextual (aparece al seleccionar nodo)**
- Si el nodo seleccionado es un **Agent node**: muestra embedded lo que sería Agent Console:
  - Tabs: `Config` · `Memoria` · `Últimos runs`
  - En Config: rol, instrucciones, autonomy_ceiling (slider L0→L5 con locks visibles), skills habilitadas, tools permitidas.
  - En Memoria: sender profiles top, gold samples activos (3–5 ejemplos), KB asignada (chips).
  - En Últimos runs: lista de 5 con link a run completo en Ledger.
- Si es **Policy gate**: lista de reglas declarativas ("Si monto > $10k USD → require approval").
- Si es **Action**: lista de permisos requeridos + estado (OAuth conectado/no).

**3.3.4 Runs Ledger (abajo, ocupa ~30% altura)**
- Tabla o lista densa de runs recientes: id, estado, timestamp, duración, costo (tokens/$), approver si aplica.
- Estados visuales: `✓ Completed` (success sutil), `⚠ Awaiting` (warning), `✗ Failed` (error), `◐ Running` (pulse), `▣ Blocked by policy` (warning fuerte).
- Click en run → modal/drawer con:
  - Timeline vertical de nodos atravesados
  - Inputs/outputs de cada nodo (colapsables)
  - Policy checks ejecutados
  - Evidence refs (provenance: claim → span → doc → version)
  - Approver + timestamp si hubo aprobación
  - Cost total del run
  - Botón "Replay this run" (si aplica)
- Filtros en header del ledger: estado · rango fecha · approver · agente.

**3.3.5 Versionado (v1 simple)**
- Solo Draft / Live (no multi-branch).
- Editar canvas → estado pasa a "Draft con cambios sin publicar" — banner sutil amarillo arriba del canvas.
- Publish → Draft reemplaza Live, se archiva versión anterior con hash corto (`v41a9f2`).
- Rollback → vuelve a versión anterior de Live. Limpia Draft actual con confirm.
- **NO diseñes diff visual entre versiones** — eso es v2.

### 3.4 Estados que debes mostrar en el mockup
- **Estado feliz**: workflow publicado, 4 runs visibles con mezcla de estados.
- **Estado "Draft con cambios sin publicar"**: banner + botón Publish destacado.
- **Un run fallado en el ledger**: para mostrar cómo se ve error state.
- **Un nodo con policy gate bloqueando**: run #1283 "Awaiting" porque gate de aprobación manual.

### 3.5 Microinteracciones imprescindibles
- Hover sobre nodo: borde vino 2px + tooltip con métricas (approval rate últimos 30d, avg cost, avg duración).
- Drag nodo: snap a grid 8px.
- Conectar nodos: drag desde bullet del nodo fuente al nodo destino.
- Eliminar nodo: confirm inline ("Eliminar nodo? [Sí] [Cancelar]"), undo 10s.
- Botón Publish: loading → success check → snapshot de versión en tooltip.

### 3.6 Qué NO incluir en Vista 1
- NO diseñes marketplace de agentes.
- NO diseñes ajustes de admin/usuarios/billing (otra vista).
- NO diseñes configuración de conexiones (otra vista).
- NO diseñes homepage de marketing.
- NO diseñes onboarding wizard (otra vista).
- NO mostrés framework L0–L5 como branding público — sí como indicador del agente en su panel Config.

---

## 4. VISTA 2 — Bandeja / Approval Workspace

### 4.1 Propósito
El Operator abre esto 20 veces al día. Es donde aprueba/edita/rechaza drafts que los agentes proponen. Productividad pura. Debe sentirse como **Superhuman para IA**.

### 4.2 Estructura de pantalla

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ [Sidebar izq 220px]      [Lista drafts 380px]        [Detail pane flex]      │
│                                                                              │
│  FaberLoom              Bandeja                      [Draft #1283]            │
│                         ─────────────────            ──────────────────      │
│  Home                   [Aprobaciones(7)][Excep(2)]                          │
│  Workflows                                            RE: Cotización Marluvas│
│  Bandeja ← activo       ▸ #1283 ⚠                    Para: jperez@acme.cr   │
│  Conocimiento             Cotización Marluvas         De: FaberLoom-QuoteBot │
│  Agentes                  Cliente: ACME                                      │
│  Conexiones               $14,500 USD                 ────────────────────── │
│  Configuración            QuoteBot · hace 4m          Estimado Sr. Pérez,   │
│                                                                              │
│                         ▸ #1281 ⚠                    Gracias por su         │
│                           Cotización Tecmater         solicitud. Adjunto    │
│                           ...                         cotización por 120    │
│                                                       pares de Marluvas     │
│                         ▸ #1275 ⚠                    50S19 en tallas...    │
│                           ...                                                │
│                                                       [highlight vino 1]    │
│                         [— Excepciones —]             [highlight vino 2]    │
│                                                                              │
│                         ▸ #1270 ✗                    ────────────────────── │
│                           Policy blocked:                                    │
│                           monto > L1 ceiling          EVIDENCIA             │
│                                                       1. Precio unit: $120  │
│                                                         ← ENT_PROD_MAR v3.2 │
│                                                       2. Stock 120 unid OK  │
│                                                         ← Inv_2026-04-18    │
│                                                                              │
│                                                       ────────────────────── │
│                                                       [Aprobar y enviar]   │
│                                                       [Editar] [Rechazar]  │
│                                                                              │
│                                                       [⌨ A: aprobar]       │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Elementos clave

**4.3.1 Lista (columna 380px)**
- Dos tabs arriba: **Aprobaciones (N)** · **Excepciones (N)**
  - Aprobaciones = drafts awaiting_approval del agente
  - Excepciones = runs bloqueados por policy, errores sin auto-recovery, escalaciones humanas
- Cada item muestra:
  - Estado (`⚠` awaiting / `✗` blocked / `◐` in-progress)
  - Título del run (descriptivo, no "Run #1283")
  - Cliente/sender
  - Monto/magnitud si aplica
  - Agente origen + timestamp relativo
  - Al hover: preview del draft en tooltip (primeras 2 líneas)
- Item activo: fondo #EEE7DA + borde izq 2px vino.
- Ordenamiento por defecto: awaiting más antiguo primero (SLA first).
- Scroll infinito o paginación simple 50 por página.

**4.3.2 Batch actions (header de lista)**
- Checkbox para multi-select.
- Acciones: `Aprobar N seleccionados` · `Rechazar N` · `Asignar a...`
- Confirm modal para batch approve si algún item tiene `risk_class: customer-visible`.

**4.3.3 Detail pane (derecha, flex)**
- Header del draft: asunto, destinatario, agente emisor, timestamp, badge de risk_class.
- **Cuerpo del draft editable inline** (rich text básico). Highlights vinos sutiles (#6E1F2B opacity 15%) sobre spans que tienen claims con evidence. Hover sobre highlight → tooltip "Ver evidencia".
- **Panel Evidencia** abajo o lateral (colapsable):
  - Lista numerada de claims
  - Cada claim: snippet del draft (span) ← documento fuente (con versión) + snippet literal de la fuente
  - Link al doc completo en nuevo panel si click
- **Razonamiento del agente** (colapsable, cerrado por defecto):
  - "Clasifiqué como cotización B2B con 94% confianza porque..."
  - "Usé precio unitario $120 de ENT_PROD_MAR v3.2 publicado 2026-03-15"
  - Keep short, actionable, no prose largo.
- **Botones de acción** (sticky al bottom):
  - `Aprobar y enviar` (primario vino)
  - `Editar` (secundario) — habilita edición inline del draft
  - `Rechazar` (tertiary con texto rojo sutil)
  - Todos con shortcut de teclado visible: `A` / `E` / `R`
- **Undo bar** aparece 10s después de cualquier acción: "Enviado. Undo (9s)"

**4.3.4 Excepciones tab**
- Similar al tab Aprobaciones pero items tienen badge `blocked by policy` o `agent failed`.
- Detail pane muestra:
  - Qué nodo del workflow falló/bloqueó
  - Razón (lenguaje humano: "Monto $14,500 excede tope L1 de este agente — requiere aprobación Admin")
  - Botones: `Escalar a Admin` · `Aprobar manualmente (override)` · `Abortar run`
  - Override deja rastro inmutable en audit log.

**4.3.5 Empty states (DISEÑALOS HONESTOS)**
- Bandeja vacía (Aprobaciones): "Bandeja al día. Próximos drafts aparecerán aquí. [Ver workflows activos →]"
- No diseñes banners motivacionales. No "¡Buen trabajo! 🎉".
- Texto sobrio, tono editorial.

**4.3.6 Loading states**
- Skeleton del detail pane mientras carga draft.
- Pulse sutil (no spinner dando vueltas).

**4.3.7 Error states**
- Si fetch draft falla: "No pudimos cargar este draft. [Reintentar]" — no esconder error.
- Si approve falla por race condition: "Este draft ya fue resuelto por Juan hace 12s. [Ver resultado]"

### 4.4 Microinteracciones imprescindibles
- Keyboard shortcuts globales en Bandeja: `J/K` navegar · `A` aprobar · `E` editar · `R` rechazar · `?` mostrar todos · `⌘K` búsqueda rápida.
- Shortcut legend siempre visible en footer del detail pane (discreta).
- Al aprobar: item se desvanece, lista avanza al siguiente. Contador del tab disminuye.
- Al hover sobre evidence highlight en el cuerpo: scroll automático del panel Evidencia al claim correspondiente.
- Edit mode: cuerpo se vuelve editable, botones cambian a `Guardar cambios y enviar` / `Cancelar`.

### 4.5 Estados que debes mostrar en el mockup
- Tab Aprobaciones con 7 items, uno activo en detail pane mostrando:
  - Cuerpo del draft con 2 highlights de evidencia
  - Panel Evidencia expandido con 2 claims
  - Razonamiento colapsado
  - Botones de acción sticky
- Tab Excepciones visible con badge (2) — al hacer mockup secundario mostrar 1 excepción policy blocked.
- Empty state para Excepciones vacío (en mockup secundario): "Sin excepciones pendientes."

### 4.6 Qué NO incluir en Vista 2
- NO diseñes configuración del agente (eso va embebido en Builder).
- NO diseñes modal "corrección recurrente" automática — ese loop se hace en background, no en UX de Bandeja v1.
- NO diseñes chat conversacional con el agente — es Bandeja, no chatbot.
- NO mostrés gráficas de analytics (van en otra vista, ronda 2).
- NO pongás CTA marketing. Ni tips. Ni emojis.

---

## 5. Consideraciones compartidas entre las 2 vistas

### 5.1 Sidebar izquierdo (igual en ambas)
- 220px fijo, fondo #F6F1E8.
- Logo/wordmark arriba (Georgia).
- Nav items con iconografía mínima + label.
- Item activo: texto vino + barra lateral 2px vino.
- Badges numéricos solo en Bandeja (pendientes).
- Footer sidebar: avatar + nombre + rol (`Owner` / `Operator`).

### 5.2 Header contextual
- Breadcrumb siempre.
- Acciones contextuales a la derecha.
- No toolbar global redundante.

### 5.3 Toggle Copilot / Autopilot (NUEVO — incluir en panel Agent del Builder)
- Toggle visual 2 estados: `Copilot` (default, humano aprueba) / `Autopilot` (agente ejecuta sin approval en workflows con policy gate OK).
- Si agente **no califica** para Autopilot (aceptación < 80% o volumen < 50 runs o policy gate faltante): Autopilot aparece **locked** con tooltip explicando qué falta ("Se desbloquea cuando acepta-rate ≥ 85% en últimos 100 runs. Actual: 67%").
- CTA accionable bajo el toggle: "Ver cómo desbloquear →" abre panel con criterios.

### 5.4 Accesibilidad
- Contraste AA mínimo (vino sobre cream lo cumple).
- Focus visible en todo elemento interactivo.
- No usar solo color para comunicar estado — siempre ícono + texto.
- Shortcut alternativos a todo mouse action crítico.

### 5.5 Responsive
- Desktop-first 1440px como target.
- Mockup mínimo 1280px ancho. No diseñes tablet/mobile en esta ronda — los Operators usan laptop.

---

## 6. Entregable

**2 archivos HTML standalone**, cada uno con:
- Todo inline (CSS + HTML en un archivo, inline SVG para íconos).
- Sin dependencias externas (no fonts CDN salvo Google Fonts para Georgia + Inter).
- Comentarios en secciones clave explicando intención de diseño.
- Naming:
  - `FaberLoom_v1_Builder.html`
  - `FaberLoom_v1_Bandeja.html`

**Adicional:** una nota `NOTAS_DISEÑO.md` (max 300 palabras) explicando:
- Decisiones visuales no obvias
- Trade-offs que hiciste
- Qué dejaste por fuera y por qué
- Sugerencias para vistas que vendrán (Admin, Billing, Analytics)

---

## 7. Principios de decisión si hay duda

1. **Si dudás entre "bonito" y "productivo para Operator 20 veces al día" → siempre productivo.**
2. **Si dudás entre mostrar feature impresionante vs. reducir fricción → reducir fricción.**
3. **Si dudás sobre densidad → una pizca más densa.**
4. **Si dudás sobre lenguaje → editorial sobrio, no SaaS marketing.**
5. **Si dudás sobre mostrar provenance/audit → siempre visible, nunca escondido.**
6. **Si dudás sobre permitir autonomía → locked por defecto, unlock con evidencia.**

---

## 8. Out of scope explícito para esta ronda

- Onboarding wizard
- Admin Panel (org/users/roles)
- Billing/usage detail
- Conexiones/integraciones setup
- Agent marketplace
- Analytics dashboard
- Mobile
- Homepage/marketing
- Multi-idioma visible (asumí ES-LatAm)
- Dark mode

Estas vistas existirán pero **no las diseñes**. Si necesitás referenciarlas (ej. "ir a Conexiones"), usá solo un link textual.

---

## 9. Cierre

Objetivo final del mockup: que cuando lo enseñe a los 3 design partners, entiendan en 30 segundos que **esto no es otro chatbot ni otra mesa de control genérica** — es **el lugar donde una PYME controla su operación con IA sin perder auditoría ni autonomía humana**.

Editorial. Denso. Auditable. Draft-first visible en cada esquina.

Dale.
