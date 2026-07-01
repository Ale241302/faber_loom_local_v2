# SKILL_FRONTEND_TEN_PRINCIPLES_V2 — Lente cognitiva frontend (FaberLoom Design System)

id: SKILL_FRONTEND_TEN_PRINCIPLES_V2
version: 2.1
status: SHADOW
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
type: SKILL
stamp: SHADOW — 2026-05-03
trigger_word: (sin trigger explícito — se activa por contexto)
trigger_context: cualquier conversación/iteración donde se piense, proponga, critique o diseñe funcionalidad de frontend (UI, UX, mocks, layouts, flujos, componentes, navegación, copy de UI)
autonomy_ceiling: ACTIVO_BG (background — colorea el razonamiento sin esperar invocación)
escalation_policy: emitir flag P0 (MUSCLE_AMPUTATION, MODE_COLLISION, GOVERNANCE_BREACH) detiene la propuesta y escala a CEO antes de avanzar
aplica_a: [FaberLoom]

---

## Propósito

**No es un agente con workflow.** Es una **lente cognitiva persistente** que se aplica siempre que el razonamiento toque frontend. Cuando se piense en una pantalla, un componente, un flujo, una navegación, una propuesta de UI — esta lente se activa en background y colorea el análisis con 14 principios no-negociables.

**Modo de uso:** la lente vive como contexto disponible (Project Instructions, Custom Instructions, o KB ref). No se invoca con un trigger word. Se aplica cada vez que la conversación cruza el `trigger_context`.

**Diferencia con v1 conceptual:** v1 era un agente que producía 3 artefactos formales (THESIS / SCREEN_INVENTORY / IMPLEMENTATION_SPEC). v2.1 es un mindset que se aplica en cualquier escala — desde "¿dónde pongo este botón?" hasta "rediseñá toda esta pantalla".

## Cómo se activa

Cualquiera de estas señales en la conversación dispara la lente:

- Mock visual adjunto (imagen, wireframe, descripción detallada)
- Mención de pantalla, componente, layout, flujo, navegación, formulario
- Propuesta de "agregar/quitar/mover/ocultar/mostrar" algo en UI
- Discusión de affordance, jerarquía visual, cognitive load, progressive disclosure
- Decisión de qué métrica/control mostrar/esconder
- Cualquier conversación cuyo output natural sea código frontend, especificación de UI, o crítica de UX

Si el contexto la activa, el razonamiento debe pasar implícitamente por los 14 principios y emitir flags cuando algún antipatrón asome — sin necesidad de producir artefactos formales salvo que se pidan.

## Output esperado por modo

| Modo de conversación | Output de la lente |
|---|---|
| Brainstorming / pensar en voz alta | Observaciones en línea con citaciones (P3, P11, etc.) cuando una propuesta cruce un principio |
| Crítica de mock | Flags emitidos contra el catálogo + recomendación |
| Diseño nuevo desde cero | Audit sustractiva + spec ligera, sin obligar el formato 3-artefactos salvo que se pida |
| Implementación de código | Comentarios con citación de principio en bloques relevantes (`// P11: evidence bundle = document mode`) |
| Decisión binaria ("¿dónde pongo X?") | Respuesta directa con principio que la justifica, no checklist completo |

La regla: **la lente se adapta al modo de conversación**, no fuerza al CEO a producir artefactos cuando solo está pensando en voz alta.

---

## Los 14 principios (canon)

### P1 — THESIS DISTILLATION
Forzá el producto/feature a UNA oración: `[Persona] can [core action] to [outcome] via [differentiator]`. Si no entra en 140 chars: flag `CONCEPTUAL_FAT`.

### P2 — SUBTRACTIVE DESIGN + IA
Antes de agregar, justificá la ausencia. Default: remover. Probá necesidad.
**Antipatrón:** confundir "sustractivo" con "amputar músculo operativo". Si remover una pantalla/tab/control elimina un workflow core (evidence review, context budget, unit economics, kanban triage), no es grasa, es músculo. Flag `MUSCLE_REMOVAL_RISK`.

### P3 — SINGLE SOURCE OF TRUTH + CANONICALIZATION
Identificá las "reglas inquebrantables" (ej. "HITL absoluto"). El **mismo string exacto** debe aparecer en toda pantalla donde aplique. Prohibido: "HITL" en pantalla A, "human gate" en B, "aprobación humana" en C. Si detectás drift: flag `DRIFT_DETECTED: {term_variant, location, canonical_expected}`.

### P4 — SYSTEM COHESION + END-TO-END
Mapeá cada flujo del trigger al estado terminal. ¿Las piezas hablan o son islas decoradas? Si una pantalla no se alcanza desde el entry point por un flow documentado, no existe.
**Antipatrón:** saltarse triage intermedio (Kanban → Workspace sin Case Detail). Flag `FLOW_GAP`.

### P5 — PROGRESSIVE DISCLOSURE + COGNITIVE LOAD + AFFORDANCE
Acción primaria: obvia al primer vistazo. Novato ve 20%, power user ve 100%. Cada elemento interactivo grita su propósito.
**Antipatrón:** esconder controles operativos (context budget, routing rules, evidence bundle) bajo "Advanced mode" genérico. Flag `AMBIENT_VISIBILITY_LOSS`.

### P6 — DRY (UX) + COHESION
Si una pantalla inventa un patrón en vez de reusar el design system: flag `UX_DEBT`. Pantallas de governance: skimmables, no layouts novel.
**Addendum:** reuso obligatorio, pero no a costa de adecuación. Chat-first layout no absorbe document-first workflow (ej. revisión de contrato legal). Flag `LAYOUT_MISMATCH`.

### P7 — PROGRESSIVE DISCLOSURE BY ROLE
Operator NO ve botones de Owner. PERO: acciones prohibidas se EXPLICAN, no se ocultan. Mal: el botón desaparece. Bien: deshabilitado con tooltip "Requires Owner role". Ghost items en navegación muestran requisito canónico (ej. "Requiere ROLE_ADMIN"). Nunca `display:none` sin explicación.

### P8 — DRY (PROCESS) + SSOT
Toda mutación pasa por el MISMO gate: candidate → audit → signed. Cero shortcuts, cero special cases. Si el flujo permite bypass: flag `GOVERNANCE_BREACH`.
**Stamp canónico:** componente `.gov-stamp` con statuses `candidate | audit | signed`. Cero tags ad-hoc.

### P9 — SPEC ↔ IMPLEMENTATION CANONICALIZATION
Lo documentado existe. Lo que existe se documenta. Si el mock muestra un botón fuera de spec → actualizar spec. Si la spec exige un campo fuera del mock → flag de gap.
**mock_ref obligatorio:** todo elemento UI en spec lleva referencia de coordenada al mock ("top-right panel, secondary action row"). Sin mock_ref → no existe.

### P10 — EXTERNAL AFFORDANCE + COGNITIVE LOAD
El usuario externo (sin manual, sin training) entiende la pantalla sin explicación. Test: si tenés que decirle qué hacer, la UI falló. El producto se enseña a sí mismo.
**Addendum:** "external" incluye al power user que la usa 8h/día. Si un control se usa >3 veces/día: ambient, no enterrado en drawers o toggles.

### P11 — OPERATIONAL MUSCLE PROTECTION
Surfaces operativas core: Kanban triage, Evidence bundle review, Document-first HITL approval, Context budget inspection, Unit economics ambient display, Agent hierarchy navigation, Skill Arena A/B comparison.
NO se "absorben" en chat-first layouts ni se esconden bajo "Advanced mode". Si un diseño propone removerlas/colapsarlas: flag `MUSCLE_AMPUTATION` y HALT.

### P12 — MODE DISAMBIGUATION
Workspace (chat-first) ≠ Iterar (object-first) ≠ Cotización (document-first). Son MODOS DE INTERACCIÓN con layouts distintos, no tabs dentro de una pantalla. Si el mock muestra revisión de documento, no proponer mergearlo a un thread de chat. Flag `MODE_COLLISION`.

### P13 — AMBIENT ECONOMICS
Cost-per-task, confidence score, SLA timer, token budget: visibles EN CONTEXTO (kanban card, composer bar, agent panel). NO requieren navegar a "Costos" o "Dashboard" para verse. Flag `ECONOMICS_EXILED`.

### P14 — CONTEXTUAL NAVIGATION
Recent hierarchy, agent toggles, trace IDs, routing breadcrumbs: navegación de primera clase (sidebar, topbar, sticky panels). NO escondidos en dropdowns, "More" menus, "Modo avanzado". Flag `NAVIGATION_BURIED`.

---

## Catálogo de flags

| Flag | Principio | Severidad | Acción |
|---|---|---|---|
| `THESIS_TOO_FAT` / `CONCEPTUAL_FAT` | P1 | P1 | descomponer antes de implementar |
| `MUSCLE_REMOVAL_RISK` | P2 | P0 | reabrir decisión, no remover |
| `DRIFT_DETECTED` | P3 | P0 | unificar a término canónico |
| `FLOW_GAP` | P4 | P1 | agregar surface intermedia |
| `AMBIENT_VISIBILITY_LOSS` | P5 | P1 | sacar control de "Advanced" |
| `UX_DEBT` | P6 | P2 | reusar patrón del DS |
| `LAYOUT_MISMATCH` | P6 | P0 | separar en modo dedicado |
| `GOVERNANCE_BREACH` | P8 | P0 | HALT — escalar CEO |
| `MUSCLE_AMPUTATION` | P11 | P0 | HALT — escalar CEO |
| `MODE_COLLISION` | P12 | P0 | HALT — separar modos |
| `ECONOMICS_EXILED` | P13 | P1 | hacer métricas ambient |
| `NAVIGATION_BURIED` | P14 | P1 | promover a sidebar/topbar |

**Severidades:** P0 = bloquea propuesta, escala. P1 = warning fuerte, recomendar fix. P2 = nota, registrar como deuda.

---

## Antipatrones — rechazo automático

- Inventar datos que no están en el mock
- Sinónimos para términos canónicos
- Features "nice to have" que el mock no pidió
- Esconder acciones sin explicación (silent removal)
- Bypass del governance gate por "conveniencia"
- Mergear document-first workflows en chat-first layouts
- Esconder controles operativos bajo "Advanced" genérico
- Remover triage intermedio (case detail entre kanban y workspace)
- Exiliar cost/confidence/SLA a pantallas de reporte separadas

---

## Modos de despliegue

| Modo | Cómo se activa la lente |
|---|---|
| **Claude Project (este proyecto)** | Archivo en KB; lo lee como contexto cuando se discute frontend |
| **Claude Code / Cowork** | Referenciar este SKILL en system prompt o leer al inicio de sesiones de UI |
| **Custom Instructions** | Pegar sección "Los 14 principios (canon)" + "Catálogo de flags" |
| **Subagent dedicado** | Si el trabajo es grande (rediseño completo), envolver en agente con workflow Audit→Spec→Implementation (volver a la lógica de v2.0, que queda como modo opcional) |

## KB refs (consultar cuando aplique, no en cada iteración)

- `ARCH_AGENT_PRINCIPLES` — 14 principios fundacionales del ecosistema MWT/FB
- `ENT_PLAT_DESIGN_TOKENS` — tokens canónicos (APROBADO Sprint 3)
- `ENT_PLAT_FRONTENDS` — inventario frontends FaberLoom
- `docs/faberloom/IDX_FB_FOUNDATION_BETA.md` — índice maestro FB
- Specs `SPEC_FB_*` referenciadas por el mock en discusión

La lente NO obliga a leer estos archivos en cada iteración. Los lee bajo demanda cuando un principio (especialmente P3 canonicalización, P9 spec↔impl) requiere ground truth canónico.

## Changelog

- **v2.1 — 2026-05-03 (CEO):** refactor de naturaleza. De agente con workflow rígido (3 fases, 3 artefactos) a lente cognitiva persistente activada por contexto. Quita `OUTPUT PROTOCOL` y `EXECUTION WORKFLOW` obligatorios. Quita `COMPLIANCE CHECKLIST` bloqueante. Mantiene 14 principios + catálogo de flags como canon. Cambia autonomy de PROPONE a ACTIVO_BG. El modo agente con 3 fases queda disponible como deployment opcional para rediseños grandes.
- **v2.0 — 2026-05-03 (CEO):** creación inicial como agente con workflow Audit→Spec→Implementation. Incorpora P11–P14 sobre los 10 originales.

---

## Pendientes

- [ ] Agregar fila en `SKILL_RUNTIME.md` (autonomy ACTIVO_BG, sin trigger word)
- [ ] Append a `MANIFIESTO_APPEND_*.md` documentando creación + refactor v2.0→v2.1
- [ ] Sync al repo canónico (`C:\dev\mwt-knowledge-hub`) vía `sync_frontend_skill_indexa.ps1`
- [ ] Validar primera aplicación en una iteración real (FaberLoom Workspace o Iterar) → pasar a VIGENTE si la lente colorea el razonamiento sin generar fricción
