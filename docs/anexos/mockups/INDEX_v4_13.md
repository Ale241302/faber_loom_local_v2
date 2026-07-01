# FaberLoom Shell Mock v4.13 — Índice de estado

> **SUPERSEDED (2026-06-17):** el puntero canónico de mock es **v4.15** (ver `INDEX_v4_15.md`). Se conserva como historial; no usar como referencia activa.

**Fecha:** 2026-07-09 (sesión de consolidación)
**Archivo:** `docs/anexos/mockups/faberloom_shell_mock_v4_13.html`
**Estado:** SUPERSEDED por v4.15 (era CERRADO / FIRMADO)
**Supersede:** v4.12, v4.11, v4.10, v4.9, v4.8, v4.7, v4.6, v4.5

---

## 1. Estructura de la interfaz (3 modos)

### Modo Operar (default)
Panel izquierdo con:
- **SpaceLoom** — canvas universal de iteración (1)
- **Entrada** — Inbox (12) + WorkLoom (3)
- **My Workspaces** (4) — Sondel SA, Industrias Norte, Rana Walk, Precios dieléctrica
- **Shared Workspaces** (2) — Licitación Q3 · Grupo Construx, Corporativo MWT · Global
- **Historial** — contextual al workspace activo; cambia con cada click de workspace

### Modo Aprender
- **StackLoom** — cola de candidatos a indexar (5)
- **Conocimiento** — L0-L4 + Señales HITL (19)
- **Gold Samples** — ejemplos aprobados (42)
- **Ritual** — Próximo freeze (18d)

### Modo Admin
- **Capacidades** — Skills (16) + Agentes (7)
- **Tenant** — IA: modelos y ruteo, Audit, Usuarios (12), Configuración

---

## 2. Componentes implementados en el mock

### Panel izquierdo (Rail 1)
- [x] Modo por pestañas (Operar / Aprender / Admin) con `modebar-2` espaciado
- [x] Secciones colapsables tipo `accordion` con chevron rotativo
- [x] Contadores por sección (`<span class="cnt">`)
- [x] Badges de estado (urgencia, operativa, etc.)
- [x] Historial contextual que cambia según workspace seleccionado
- [x] My Workspaces + Shared Workspaces separados

### Canvas central (SpaceLoom)
- [x] Thread de chat limpio (sin historial previo)
- [x] Composer con textarea auto-expandible
- [x] Pedal de arquetipos: Eco / Balanceado / Sport+
- [x] Botón de envío con estado `ready`
- [x] Hint contextual: "SpaceLoom: chat universal. Cada workspace lo hereda."
- [x] Draft de proforma con HITL (Aprobar / Editar / Rechazar / Boost)
- [x] Grounding links + tags de validación + SHA-256
- [x] Welcome message que explica el canvas

### Panel derecho (Rail 3 / Toolset)
- [x] Tabs horizontales: Agentes / Skills / KB / Gold
- [x] Grupos My / Shared / Library con badge `&#128275; sealed`
- [x] Toggle switches ON/OFF para skills
- [x] Skill medular "Voice" destacada con borde coral
- [x] Tool items con icono, nombre, estado tag
- [x] KB items con nivel L0-L4 y warning de vencimiento
- [x] Gold samples con contador de usos

### WorkLoom (Inbox + Mesa)
- [x] Inbox con emails ruteados y sin asignar
- [x] Botón "+ Asignar workspace" para emails sin ruta
- [x] Kanban con 4 columnas: TU CRITERIO / ESPERANDO / DELEGADO / ERROR
- [x] Cards con score de confianza, cliente, agente, descripción
- [x] Click en card → carga draft en SpaceLoom del workspace correspondiente
- [x] Colores por urgencia: coral (crítico), amber (esperando), slate (delegado), vino (error)

### Routing · Factory de IAs (Admin)
- [x] 4 tabs: Arquetipos / Reglas de Routing / Keys & Modelos / Simulador
- [x] Dashboard de métricas: presupuesto, usado, proyección, outcome, calls
- [x] Builder de arquetipos: nombre, modelo, temperatura, tokens, system prompt, contexto
- [x] Lista de arquetipos con métricas de uso (costo, calls, %OK)
- [x] Editor de reglas tipo IF-THEN con condiciones configurables
- [x] Diagrama de flujo visual: Entrada → Evaluar → Arquetipo → Ejecutar → Outcome
- [x] Keys configuradas con estado y uso por proveedor
- [x] Tabla comparativa de modelos (costo, latency, quality, uso)
- [x] Simulador de escenario: tarea, cliente, urgencia, complejidad
- [x] Resultado simulado con comparativa vs otros arquetipos

### Navegación y UX
- [x] Paneles redimensionables con `resize-handle` (drag entre 180-400px)
- [x] Toggle paneles: `[` izquierdo, `]` derecho
- [x] Modo Focus: `f` oculta ambos paneles
- [x] Command Palette: `Cmd+K` con 10 comandos predefinidos
- [x] Toast notifications con feedback de acciones
- [x] Selección de texto deshabilitada durante resize
- [x] Animaciones de entrada (`viewIn`, `itemIn`) con easing
- [x] Dark theme consistente con paleta de colores (coral, amber, sage, slate, vino)

---

## 3. Decisiones de diseño firmadas

| Decisión | Valor | Nota |
|---|---|---|
| SpaceLoom es canvas universal | Sí | Todos los workspaces lo heredan; limpio por defecto |
| Workspaces son contextos, no espacios | Sí | El canvas es uno solo; el scope cambia |
| My/Shared/Library herencia | Sí | Library = sellado/sealed; no se enajena |
| Voice = skill medular | Sí | Aprende de interacciones; ajustable por tarea/producto/remitente |
| Routing = Factory de IAs | Sí | Keys, arquetipos, presets, reglas de contexto, simulador |
| Historial = contextual | Sí | Cambia según workspace activo; hereda de padres si es shared |
| WorkLoom = Mesa de HITL | Sí | 4 columnas por urgencia/estado; entry point a SpaceLoom |
| Paneles redimensionables | Sí | Drag en borde; min 180px, max 400px |
| Modebar espaciado | Sí | `modebar-2` con borde visible; texto legible |

---

## 4. Pendientes técnicos (no del mock; del build)

- [ ] Implementar redimensionamiento real con `ResizeObserver` (no solo mousedown/mousemove)
- [ ] Persistir ancho de paneles en `localStorage`
- [ ] Implementar historial real con backend (no solo mock data)
- [ ] Conectar command palette a comandos reales (no solo toast)
- [ ] Implementar drag & drop en WorkLoom kanban
- [ ] Agregar virtual scroll para listas largas (>100 items)
- [ ] Implementar lazy loading de toolset tabs
- [ ] Agregar tooltips nativos en hover de items
- [ ] Implementar search/filter en cada toolset tab
- [ ] Mobile responsive (colapsar a drawer)

---

## 5. Relación con BUILD_SEQUENCE v3.0

| Etapa | Mock v4.13 cubre | Gap |
|---|---|---|
| E1 SpaceLoom + Routing | SpaceLoom canvas, Routing Factory UI, Arquetipos, Keys | Backend de router, LiteLLM integration |
| E2 Skills genérico | WorkLoom kanban, Inbox, HITL 3 botones, Toolset con toggles | Engine ejecutor, SkillSpec markdown, Tier 0 |
| E3 Workspaces | My/Shared workspaces, historial contextual, scope bar | Backend RLS, workspace_members, multi-tenant |
| E4 Multi-usuario | Admin > Usuarios (12) | Auth real, roles, invitaciones |

---

## 6. Changelog del mock

- **v4.13 (2026-07-09)**: Modo Operar/Aprender/Admin con paneles redimensionables. Routing Factory elaborada con 4 tabs. My/Shared Workspaces. Historial contextual. Modebar espaciado. Toolset con toggles y herencia My/Shared/Library.
- **v4.12 (2026-07-09)**: WorkLoom=Mesa, toolset horizontal, historial de interacciones, lista de espacios. SpaceLoom base + workspaces planos.
- **v4.11 (2026-07-09)**: Izquierda=selector de espacios colapsable, derecha=toolset, centro=SpaceLoom.
- **v4.10 (2026-07-09)**: Panel derecho con secciones colapsables tipo chevron por temas.
- **v4.9 (2026-07-09)**: Invertir paneles — izquierda=toolset, derecha=selector de espacios.
- **v4.8 (2026-07-09)**: Rail 1 = selector de espacios, Canvas = iteración, Rail 3 = toolset.
- **v4.7 (2026-07-09)**: SpaceLoom limpio + Rail 3 de herramientas.
- **v4.6 (2026-07-09)**: SpaceLoom como canvas cognitivo con workspaces como contexto.
- **v4.5 (2026-07-09)**: Mesa de control con columnas por estado + SpaceLoom base.

---

## 7. Archivos relacionados

- `docs/anexos/mockups/faberloom_shell_mock_v4_13.html` — Mock principal (HTML+CSS+JS)
- `docs/anexos/mockups/faberloom_shell_mock_v4_12.html` — Versión anterior (WorkLoom unificado)
- `docs/faberloom/SPEC_FB_BUILD_SEQUENCE_v3.md` — Secuencia de build (supersede v2.1)
- `docs/faberloom/PLB_FB_FOUNDATION_BETA_v1.md` — Plan de lanzamiento beta
- `docs/faberloom/SPEC_FB_EVOLUTION_ROADMAP_v1.md` — Roadmap de evolución

---

*Este índice documenta el estado del mock v4.13 al momento de su cierre. El siguiente paso es la implementación de E1 (SpaceLoom + Routing) según SPEC_FB_BUILD_SEQUENCE_v3.md.*
