# AUDIT_B2 — Screens 8-9 (console + studio)

## Ruta 8 — `#/console/:id`

### Wireframe

Layout de dos columnas en `.console-wrap` (línea 3705): columna principal `.console-main` con tres bloques apilados (header de draft con pills + `confidenceRing`, body con 6 `console-field` + `draft-preview` + callout de draft-first, y footer `console-actions` con Volver / Editar / Rechazar / Aprobar-y-enviar) y `<aside class="evidence-drawer">` a la derecha con header + lista de ítems `.evidence-item` + nota de provenance. Rompe el target del memo (memory doc pide 4 tabs Consola/Tareas/Usuarios/Flujos + header sticky de confianza + rail derecho tripartito "Ahora mismo / Qué usó / Siguiente paso" + footer de métricas 30d + widget persistente de Learning Thermometer). Lo que está hoy cubre el caso "aprobar un draft puntual", no la consola de supervisión del agente.

### Light (≥5 findings)

- [S1] La pantalla es "approve a draft", no el Agent Console de 4 tabs del memo (Consola/Tareas/Usuarios/Flujos). Falta toda la supervisión: tab Tareas con cola, tab Usuarios con 6 KPIs (asistidos·approval·edit-light·tiempo ahorrado·resueltos sin escalar·repeat use), tab Flujos con workflows que el agente participa, y header sticky con nombre+avatar+estado+autonomy level+CTA ámbar si hay pendientes. **Línea ~3704.** Fix: envolver la vista actual dentro de tab `Consola` y montar tab-bar sobre `.console-wrap`, usando `.tabs` canónica (slice A) con `var(--coral-primary)` como underline.
- [S1] No existe widget "Learning Thermometer" (Frío/Tibio/Caliente) ni botón "Indexar Aprendizaje" que abra modal de consolidación — mecanismo de memoria principal del producto según memo de agentes. **Línea ~3789.** Fix: bottom-right fixed widget `.learning-thermometer` con `var(--bg-surface)` + border `var(--evidence)` + counter de outputs pendientes de consolidar + CTA primario.
- [S1] `console-actions` apila tres botones con pesos visuales cercanos (Editar secundario, Rechazar danger, Aprobar primario lg) pero sin separación semántica: Rechazar junto a Aprobar puede generar mis-click fatal sobre trackpad. **Línea ~3767.** Fix: mover Rechazar al extremo izquierdo con gap mínimo de `var(--space-6)` (slice A) contra el cluster Editar+Aprobar, o colapsar Rechazar en menú "Más acciones" (pero el memo pide los 3 botones fijos, nunca kebab — entonces: separación espacial).
- [S1] Estado del agente en header es solo `pill pill-coral pill-dot` con el nombre (línea 3710) — no muestra los 4 estados tipificados Verde/Azul/Ámbar/Gris con verbo + microfrase. Un Cotizador "Aprendiendo" se ve igual que uno "Activo". **Línea ~3710.** Fix: reemplazar la pill por bloque `.agent-status` con dot + nombre + microfrase ("Listo y operando" / "Ajustando respuestas" / "Necesita tu visto bueno" / "No tomará acciones").
- [S1] `background:var(--bg-subtle);padding:12px 16px;border-radius:6px` hardcoded en el callout draft-first (línea 3755) — mismo patrón repetido 8+ veces en `renderSkillStudio`. **Línea ~3755.** Fix: crear `.callout` + `.callout-info` / `.callout-evidence` / `.callout-warning` en slice A, con `border-left: 3px solid var(--info)` y padding `var(--space-3) var(--space-4)`.
- [S2] Confidence ring del draft es numérico (línea 3718) pero la pill `${draft.confidence}%` dentro del drawer (línea 3783) repite el dato sin decirle al usuario qué significa "92%" vs "68%". Falta leyenda de banda (Verde ≥85 · Ámbar 70-84 · Rojo <70) en hover del ring. **Línea ~3718.** Fix: `aria-describedby` apuntando a tooltip que describa bandas + marca visual de umbral sobre el anillo.
- [S2] El callout draft-first describe tres side effects (Gmail, HubSpot, audit log) en prosa corrida. Para el "control-plane" vendido al buyer HSE, deberían renderizarse como checklist con iconos y estado (planned · will-execute-on-approve). **Línea ~3757.** Fix: `<ul class="action-preview">` con 3 items cada uno con icon + "enviará" / "actualizará" / "registrará" + tag de reversibilidad heredado del action-risk registry.
- [S2] `console-title` usa h2 sin clase tipográfica ni truncado; subjects largos ("Cotización Marluvas Goliath GL-112 · 80 pares frigorífico Centroamericano · Net 30 · Urgente") rompen línea 3 veces en viewport 1280. **Línea ~3715.** Fix: `font-size: var(--fs-h3)`; `line-height: 1.2`; `line-clamp: 2` con `title` attr para tooltip del completo.
- [S3] El meta-row (línea 3709) mezcla 4 tipos de pill (coral, neutral mono, priority, evidence) sin jerarquía — el ojo salta entre las 4. Ordenar: [agente] · [id mono más tenue] · [evidencia como accent principal] · [prioridad como modifier final]. **Línea ~3709.** Fix: reagrupar con separador visual (middle dot) entre clusters de 2.

### Dark (≥3 findings)

- [S1] `console-field .label` usa `var(--text-muted)` (heredado de estilos generales — ver slice A: muted `#8A8278` dark = 3.88:1 sobre `bg-surface`, FAIL 4.5:1 body). En labels de 11-12px bold eso viola WCAG body aunque PASS-LG marginal. **Línea ~3723.** Fix: subir a `var(--text-muted)` endurecido del slice A (propuesta `#A49C90` = 4.78:1) o promover labels a `var(--text-secondary)`.
- [S1] El callout draft-first en dark tiene `color:var(--text-secondary)` sobre `var(--bg-subtle)` — ratio ~6.85:1 OK para prosa, pero el `<strong>Draft-first:</strong>` inline hereda `var(--text-primary)` sin énfasis adicional; el `i-shield` con `color:var(--info)` dark (`#7A8A9B` = 4.16:1) queda tenue contra cream-dark subtle. **Línea ~3756.** Fix: usar `var(--evidence)` dark endurecido (`#D48090` del slice A) para el icon porque semánticamente es provenance + reliability, no info neutro.
- [S2] `evidence-drawer` tiene `border-top: 1px solid var(--border-subtle)` (línea 3786) en el footer de provenance — en dark `#3D3A34` sobre surface `#2A2824` da delta 1.30:1 (ver slice A), casi invisible. Lector no registra que "esa nota es meta, no parte del último evidence-item". **Línea ~3786.** Fix: migrar a `--border-subtle` dark endurecido (`#4A463F`) o cambiar separador por `background: var(--bg-subtle)` (contrast delta natural).
- [S2] `text-muted` en línea 3689 para `e.ts` (timestamp dentro de evidence-item, ~10-11px) falla AA dark incluso con el endurecimiento — tamaños sub-12 exigen siempre 4.5:1 sobre cualquier bg, y aquí estamos sobre `bg-surface` dark. **Línea ~3689.** Fix: subir timestamp a `var(--text-secondary)` o reservar `text-muted` estrictamente para 14px+ semibold (regla del slice A).
- [S3] `confidenceRing` stroke en dark asume que los tres estados de banda (success / warning / error) quedan legibles sobre surface dark; `--error` dark (`#B85555` = 3.13:1 sobre surface) es borderline para un indicador principal de decisión. **Línea ~3718.** Fix: aplicar `--error` dark endurecido (`#D97070` = 4.55:1 del slice A) en el ring.

### i18n

- Hard-coded ES sin fallback:
  - `'listo para tu revisión'` (línea 3716) — inline en template string, no hay tabla `STRINGS`.
  - `'Todos los checks aprobados'` (línea 3749) — mezclado con el mock `pricing_b2b · v1.4`.
  - `'Draft-first: este correo no saldrá hasta que apruebes…'` (línea 3758) — 280 caracteres inline.
  - `'Volver'` / `'Editar'` / `'Rechazar'` / `'Aprobar y enviar'` (líneas 3765-3771) — sin `data-i18n`.
  - `'Provenance: cada fuente citada queda registrada en el audit log con hash SHA-256 y timestamp. Exportable a CSV/JSON para compliance.'` (línea 3787) — copy regulado, crítico tenerlo en tabla para PT-BR cuando entre design partner Brasil.
- Overflow PT-BR:
  - "Aprobar y enviar" (18ch) → "Aprovar e enviar" (17ch) OK, pero "Todos los checks aprobados" (26ch) → "Todas as verificações aprovadas" (32ch, +23%) desborda el `text-xs text-muted` inline sin wrap, empujando la pill warning fuera del card en viewport 1280.
  - "listo para tu revisión" (23ch) → "pronto para a sua revisão" (25ch) — OK en `console-subtitle` pero justo en límite si se concatena con metadata más larga.

### a11y (≥4 findings)

- [S1] `console-actions` no es `<footer role="group" aria-label="Acciones del draft">`; los tres botones primarios no están agrupados semánticamente y un screen reader los lee aislados sin indicar cuál es la acción destructiva vs primaria. **Línea ~3763.** Fix: agrupar en `role="group"`, `aria-label` descriptivo, y añadir `aria-keyshortcuts` (A=Aprobar, E=Editar, R=Rechazar) visible en tooltip.
- [S1] El `confidenceRing` es puramente visual — si devuelve número dentro, no tiene `role="img"` ni `aria-label="Confianza del draft: 92 por ciento, banda alta"`. Screen reader pierde el indicador principal de decisión. **Línea ~3718.** Fix: agregar `aria-label` computado + texto `sr-only` con banda interpretada.
- [S1] `evidence-drawer` es `<aside>` sin `aria-label` ni vínculo con el body del draft. El usuario con teclado no sabe cómo llegar ahí ni que las superíndices del preview apuntan a esos ítems. **Línea ~3777.** Fix: `aria-label="Evidencia de procedencia del draft"`, `role="complementary"`, y en el preview cada cita con `<a href="#ev-${id}" aria-describedby="ev-${id}">`.
- [S2] Densidad de información en header: pills 4 + título + subtítulo + ring = 8 elementos en viewport ~960px de ancho, sin landmarks internos. Usuario con zoom 200% ve todo comprimido. **Línea ~3707.** Fix: envolver meta-row en `<dl>` con `<dt>` invisible por pill; agregar `@media (max-width: 1024px)` que colapse el ring al borde derecho del meta-row en lugar de ocupar columna separada.
- [S2] Tab order roto: si se monta el tab-bar recomendado (Consola/Tareas/Usuarios/Flujos), los botones de acción quedan lejos del foco actual tras aprobar. Falta `tabindex` y `autofocus` a la CTA primaria al entrar a la ruta.
- [S3] `button` en línea 3765-3772 no tienen `aria-describedby` apuntando al callout draft-first — el usuario con screen reader que llega al botón Aprobar no sabe que eso disparará Gmail + HubSpot + audit log.

### Snippets

Fix S1 — tabs + status + thermometer:
```html
<!-- Tab bar sobre console-wrap (memo: 4 tabs) -->
<nav class="tabs tabs-console" role="tablist" aria-label="Consola del agente">
  <button class="tab active" role="tab" aria-selected="true">Consola <span class="tab-count">1</span></button>
  <button class="tab" role="tab" aria-selected="false">Tareas <span class="tab-count">7</span></button>
  <button class="tab" role="tab" aria-selected="false">Usuarios</button>
  <button class="tab" role="tab" aria-selected="false">Flujos</button>
</nav>

<!-- Header con estado tipificado -->
<div class="agent-status agent-status-active" role="status">
  <span class="dot" aria-hidden="true"></span>
  <div>
    <div class="agent-status-name">Cotizador Marluvas</div>
    <div class="agent-status-verb">Activo · Listo y operando</div>
  </div>
  <span class="pill pill-coral" style="margin-left:auto">Autonomy L1 · Propone</span>
</div>
```

```css
.tabs-console { padding: 0 var(--space-6); background: var(--bg-surface); border-bottom: 1px solid var(--border-subtle); position: sticky; top: 0; z-index: 20; }

.agent-status { display: flex; align-items: center; gap: var(--space-3); padding: var(--space-3) var(--space-4); border-radius: var(--radius-md); background: var(--bg-subtle); }
.agent-status .dot { width: 8px; height: 8px; border-radius: 50%; }
.agent-status-active .dot { background: var(--success); box-shadow: 0 0 0 3px rgba(94,114,83,.18); }
.agent-status-learning .dot { background: var(--info); }
.agent-status-waiting .dot { background: var(--warning); box-shadow: 0 0 0 3px rgba(184,138,74,.22); animation: fl-pulse 2s var(--ease-standard) infinite; }
.agent-status-paused .dot { background: var(--text-muted); }
.agent-status-name { font-weight: 600; font-size: var(--fs-body); }
.agent-status-verb { font-size: var(--fs-ui-sm); color: var(--text-secondary); }
@keyframes fl-pulse { 50% { opacity: .55; } }

/* Learning Thermometer (widget persistente) */
.learning-thermometer { position: fixed; bottom: var(--space-6); right: var(--space-6); background: var(--bg-surface); border: 1px solid var(--border-subtle); border-left: 3px solid var(--evidence); border-radius: var(--radius-lg); padding: var(--space-3) var(--space-4); box-shadow: var(--shadow-md); display: flex; gap: var(--space-3); align-items: center; z-index: var(--z-dropdown); }
.learning-thermometer[data-temp="cold"] { border-left-color: var(--info); }
.learning-thermometer[data-temp="warm"] { border-left-color: var(--warning); }
.learning-thermometer[data-temp="hot"] { border-left-color: var(--error); animation: fl-pulse 2.4s var(--ease-standard) infinite; }
.learning-thermometer-count { font-family: var(--font-mono); font-size: var(--fs-h4); font-variant-numeric: tabular-nums; }
```

Fix S1 — separación de acciones peligrosas (mover Rechazar al extremo):
```html
<div class="console-actions" role="group" aria-label="Acciones del draft">
  <div class="console-actions-destructive">
    <button class="btn btn-danger" aria-keyshortcuts="R">
      <svg class="ico-sm ico"><use href="#i-x"/></svg>Rechazar
    </button>
  </div>
  <div class="console-actions-navigate">
    <button class="btn btn-ghost" onclick="go('bandeja')">Volver</button>
  </div>
  <div class="console-actions-primary">
    <button class="btn btn-secondary" aria-keyshortcuts="E">
      <svg class="ico-sm ico"><use href="#i-edit"/></svg>Editar
    </button>
    <button class="btn btn-primary btn-lg" aria-keyshortcuts="A"
            aria-describedby="draft-first-note">
      <svg class="ico-sm ico"><use href="#i-check"/></svg>Aprobar y enviar
    </button>
  </div>
</div>
```

```css
.console-actions { display: flex; justify-content: space-between; align-items: center; gap: var(--space-6); padding: var(--space-4) var(--space-6); border-top: 1px solid var(--border-subtle); background: var(--bg-subtle); }
.console-actions-destructive { margin-right: auto; }
.console-actions-primary { display: flex; gap: var(--space-2); }
```

Fix S1 — callout component + draft-first como action preview:
```html
<div class="callout callout-evidence" id="draft-first-note">
  <svg class="ico"><use href="#i-shield"/></svg>
  <div class="callout-body">
    <strong>Draft-first.</strong> Al aprobar se ejecutarán 3 acciones reversibles:
    <ul class="action-preview">
      <li><svg class="ico-sm ico"><use href="#i-check"/></svg>Enviar correo vía Gmail API <span class="pill pill-neutral">reversible 30 min</span></li>
      <li><svg class="ico-sm ico"><use href="#i-database"/></svg>Actualizar HubSpot · Opportunity → Propuesta enviada <span class="pill pill-neutral">reversible</span></li>
      <li><svg class="ico-sm ico"><use href="#i-shield"/></svg>Registrar evidencia firmada en audit log <span class="pill pill-evidence">append-only</span></li>
    </ul>
  </div>
</div>
```

```css
.callout { display: flex; gap: var(--space-3); padding: var(--space-3) var(--space-4); border-radius: var(--radius-md); background: var(--bg-subtle); font-size: var(--fs-body-sm); line-height: 1.55; }
.callout-info { border-left: 3px solid var(--info); }
.callout-evidence { border-left: 3px solid var(--evidence); }
.callout-warning { border-left: 3px solid var(--warning); }
.action-preview { margin: var(--space-2) 0 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: var(--space-2); }
.action-preview li { display: flex; align-items: center; gap: var(--space-2); font-size: var(--fs-ui-sm); }
```

---

## Ruta 9 — `#/agentes/:id` · Skill Studio

### Wireframe

`page-wrap` de 1640px con `agent-persona-header` arriba (nombre Georgia italic 26px + persona + counters + botones Roster/Graduar/Pausar y `skill-tab-bar` abajo con tabs de skills + "Añadir skill"). Debajo `.studio-layout` en 3 columnas: sidebar izquierdo con 6 `ctx-block` apilados (KB sources, Connections, Policies, Memory, Examples, Guardrails), main central con `.skill-head` + 3 `.instr-block` apilados (Base sealed/collapsed, Manual textarea editable, Learned con `learned-rule` cards) + Test Console + Fork Zone, y aside derecho con 4 `studio-aside-card` (runtime, últimos runs, versiones, impacto del cambio en warning). Las 3 capas de instrucción son el corazón de la pantalla: Base estéril con `i-lock`, Manual con `i-edit` coral, Learned con `i-sparkle` warning. Fork zone al final como escape hatch con borde error y MFA requerido.

### Light (≥5 findings)

- [S1] **Capa Base** sealed pero NO hay affordance visual de "esto es inmutable, lee-only". El `<pre class="instr-body-sealed collapsed">` (línea 4898) es solo un pre monospaced con fondo neutro; el candado `i-lock` en el header es el único cue. Usuario que abre por primera vez no entiende la diferencia entre capas. **Línea ~4898.** Fix: `.instr-body-sealed` con `background: repeating-linear-gradient` sutil + marca "READ ONLY" pin + cursor `not-allowed` + padding-left con line-numbers estilo code viewer. Además, cambiar `button "Mostrar/ocultar"` a disclosure nativo con `<details>/<summary>` para a11y + estado persistido.
- [S1] **Capa Manual** es `<textarea>` pelado (línea 4915) — sin resaltado de sintaxis, sin diff contra versión previa, sin auto-save visible, sin límite de caracteres visible (solo `${skill.overlayManual.length} chars` a la derecha sin máximo). El botón Guardar es la única señal de dirty; `studioPromptDirty=true` se setea pero no se refleja en UI. **Línea ~4915.** Fix: indicador de dirty state visible ("Cambios sin guardar" pill warning), límite tipo "1234/8000" con barra al 80%, autosave cada 30s a borrador local, y lint inline con warnings (ej: "Esta línea contradice policy pricing_b2b").
- [S1] **Capa Learned** (línea 4923) mezcla propuestas pendientes con reglas activas en la misma sección, solo separadas por un `learned-section-label`. Visualmente igual weight, aunque semánticamente las propuestas son la parte accionable urgente. La `pill pill-warning ${learnedProposed.length} propuestas` del header es el único indicador de urgencia. **Línea ~4937.** Fix: propuestas en panel superior con borde warning pulsante + contador grande, aceptadas en lista colapsada debajo con disclosure "Ver ${n} reglas activas". Cada regla propuesta debería tener preview de impacto ("Se aplicará a ~12% de los drafts según últimos 30 días").
- [S1] **Fork Zone** (línea 4964) está tipificada correctamente como escape hatch con warning, pero el botón "Fork this skill" usa `btn btn-ghost` con color error inline — rompe el sistema (ghost no existe en error). Además el texto explica las consecuencias pero no hay confirmación de doble-paso (pide MFA solo en el alert mock). **Línea ~4973.** Fix: `.btn-danger-outline` tokenizado; botón abre modal con checkbox "Entiendo que pierdo SLA y upgrades automáticos" + input "Escribí FORK para confirmar" + campo MFA. Patrón GitHub delete-repo.
- [S1] `ctx-block` de sidebar (línea 4764) repite 6 veces el mismo patrón header+body+addBtn — pero hay inconsistencia de affordances: algunos tienen `ctx-add-btn` ("+ Adjuntar doc"), otros no (Memory). Memory es read-only implícito pero no hay indicador visual; Guardrails tiene addBtn pero dice "Editar guardrails" (no + icono, confuso con los Add del resto). **Línea ~4831.** Fix: declarar `data-affordance="add"|"edit"|"readonly"` y renderizar icon/copy consistentes. Memory explícito con `i-lock` small + "Lectura desde AgentMemory".
- [S2] Test Console (línea 4946) devuelve mock HTML inyectado como `out.innerHTML = sim` — valioso como demo pero no replica ni siquiera un placeholder del Linked Evidence. El output indica "Confianza 92% · Evidencia 3 fuentes · Latencia 1.2s" pero las fuentes no son clickables ni expanden. **Línea ~5069.** Fix: renderizar fuentes como `<a>` pills con `href="#ev-${id}"` que abran drawer; cada claim en el output marcado con superíndice numerado que linke a la fuente.
- [S2] La tabla de skills activa (`skill-tab-bar`, línea 4754) no deja claro cuál está activa vs hover state. `skill-tab.active` existe pero no tiene underline ni color shift claro en el prototipo (solo class presente) — el ojo busca ancla. **Línea ~4726.** Fix: `.skill-tab.active` con `border-bottom: 2px solid var(--coral-primary)` + `background: var(--coral-tint)` (slice A) + scroll horizontal si `skills.length > 6`.
- [S2] `studio-aside-card` impacto del cambio (línea 5017) usa `border-color:var(--warning)` + `background:rgba(184,138,74,0.04)` inline — este patrón es el cuarto callout-warning distinto del archivo. **Línea ~5017.** Fix: consolidar bajo `.card card-warning` del sistema (slice A), que ya existe como pattern canónico.
- [S2] `agent-persona-header` usa `font-family:Georgia;font-style:italic;font-size:26px;font-weight:600` hardcoded (línea 4739) — slice A define `--fs-h3` 32px y `--fs-h4` 22px, 26px está off-scale. **Línea ~4739.** Fix: usar `var(--fs-h3)` o introducir `--fs-persona` tokenizado si Georgia-italic-26 es deliberado.
- [S3] `.instr-head-right` en capa Base muestra `v${skill.templateVersion}` pero no linkea a changelog del publisher ni indica si hay versión más nueva disponible del template. Siendo templates de proveedores externos, el upgrade path debería ser visible. **Línea ~4894.** Fix: pill "v2.1 · upgrade disponible v2.3" con link a diff del publisher.

### Dark (≥3 findings)

- [S1] `.instr-body-sealed` (capa Base) usa fondo `bg-subtle` dark `#34312C` — sobre pre con `text-primary` blanco cream, OK, pero las 3 capas apiladas tienen todas fondos `bg-subtle`/`bg-surface` muy cercanos en luminancia dark (delta ~8% entre `#2A2824` y `#34312C`). La distinción de "base sealed vs manual editable vs learned propuesta" se pierde visualmente. **Línea ~4898.** Fix: introducir `--surface-base` (más oscuro que surface) y `--surface-learned` (tint warning 6-10%) como tokens diferenciados; en dark subir diferencial a ~15%.
- [S1] `learned-rule-proposed` y `learned-rule-accepted` presumiblemente difieren por border-color (warning vs success) — en dark, warning dark (`#D0A66A` endurecido `#E0B47A` = 7.69:1) OK, pero success dark (`#9BAD8C` = 6.13:1) OK, sin embargo el `border-left: 3px` sobre `bg-surface` dark resulta en contraste border vs bg de ~2.5:1 — el eye track lo lee como decorativo, no como semántico. **Línea ~4839, 4853.** Fix: sumar `background: rgba(208,166,106,.08)` (proposed) y `rgba(155,173,140,.06)` (accepted) para reforzar la banda semántica.
- [S2] Fork Zone botón con `border:1px solid var(--error-border,#e5b6a8)` (línea 4973) — el fallback hex es un tint rosa claro, incorrecto en dark (invisible sobre surface dark). El token `--error-border` no existe en slice A. **Línea ~4973.** Fix: usar `var(--error)` endurecido dark (`#D97070`) directo o crear `--error-border-strong` light/dark paired.
- [S2] `pill pill-warning pill-dot` con font-size 10px inline (línea 4729) para el status del skill tab — en dark, warning dark #D0A66A sobre bg del tab (surface o subtle) combinado con texto 10px cae en zona PASS-LG marginal pero el dot anima/no anima sin respetar `prefers-reduced-motion`. **Línea ~4729.** Fix: elevar weight del label a 600 y respetar reduce-motion (slice A incluye regla global).
- [S3] `studio-aside-card` cuarto (impacto) con `background:rgba(184,138,74,0.04)` — en dark ese alpha 4% sobre surface dark es prácticamente invisible, el tint se pierde. **Línea ~5017.** Fix: subir a 12-15% alpha en dark o usar token dedicado `--warning-tint` con override dark del slice A.

### i18n

- Hard-coded:
  - `'skills activas'` (línea 4742), `'connections'` (línea 4743), `'Añadir skill al agente'` (línea 4758) — concatenadas con counters, PT-BR: "habilidades ativas" (+2ch por cada) desborda.
  - `'Base · instrucciones del template'` (línea 4889), `'Selladas por ${publisher}. No modificables sin forkear.'` (línea 4890) — PT: "Seladas por X. Não modificáveis sem forkar." (+14%).
  - `'Overlay aprendido · reglas auto-generadas'` (línea 4928) — frase larga, PT: "Camada aprendida · regras geradas automaticamente" (51ch, +14%).
  - `'¿Necesitás modificar las instrucciones base?'` / `'Forkear desconecta la instancia del template: no recibís upgrades ni bug fixes, y FaberLoom deja de garantizar SLA.'` (líneas 4969-4970) — copy legal-operativo crítico, debe estar en tabla.
  - `'Propuestas pendientes · gate humano (P11)'` (línea 4938) — jerga interna ("gate humano P11") que no se traduce ni se explica.
  - `'publicado por ${skill.templatePublisher}'` (línea 4871) — verbo conjugado en template string.
- Overflow PT-BR:
  - "Overlay aprendido · reglas auto-generadas" (43ch) → "Camada aprendida · regras geradas automaticamente" (51ch) desborda el `.instr-title` a dos líneas en viewport 1280, rompiendo la altura del `.instr-head` y desplazando las pills del `instr-head-right`.
  - "Graduar a Active" (17ch) mezcla español + inglés; PT-BR: "Graduar a Active" o "Promover para Active" — mantener "Active" como etiqueta técnica estable es correcto pero requiere marcarla `<code>` o pill-neutral.

### a11y (≥4 findings)

- [S1] Densidad extrema: 3 columnas + 3 capas apiladas + 4 cards aside + test console + fork zone = ~18 bloques navegables. Sin skip-links ni landmarks internos (`<nav>` para skill-tabs, `<main>` para studio-main, `<aside>` correcto). Usuario teclado recorre 40+ focusable antes de llegar a "Aprobar regla propuesta". **Línea ~5022.** Fix: skip-links "Saltar a overlay manual" / "Saltar a propuestas pendientes"; `<nav aria-label="Skills del agente">`, `<main aria-label="Editor del skill seleccionado">`, cada `ctx-block` como `<section aria-labelledby>`.
- [S1] `<textarea>` del overlay manual (línea 4915) no tiene `<label>` visible asociado — solo el header del bloque que no usa `for`. Screen reader lo lee como "textarea sin nombre". **Línea ~4915.** Fix: `<label for="overlay-manual-${skill.id}" class="sr-only">Overlay manual de ${skill.templateName}</label>` + `aria-describedby` al subtítulo "Reglas que escribiste vos…".
- [S1] `learned-rule-actions` botones Rechazar/Editar/Aceptar (línea 4845) — igual problema que en ruta 8: los 3 seguidos con pesos visuales cercanos (ghost/ghost/primary), Aceptar y Rechazar adyacentes, riesgo mis-click. Además `aria-label` ausente: cada botón debería decir "Aceptar regla: [primeros 60ch de r.rule]" para que screen reader distinga entre múltiples reglas propuestas. **Línea ~4845.** Fix: Rechazar a la izquierda con gap de `var(--space-4)`, y `aria-label={"Aceptar regla propuesta: " + r.rule.slice(0,60)}`.
- [S2] `<pre class="instr-body instr-body-sealed collapsed">` (línea 4898) con contenido preformateado largo — sin `role="region"` ni `aria-label`, screen reader lo narra como texto plano. En collapsed el `display` presumiblemente es none sin `aria-hidden`/`hidden` — focus puede caer dentro de contenido oculto. **Línea ~4898.** Fix: reemplazar por `<details><summary>`, `aria-label="Instrucciones base del template"`, `role="region"`.
- [S2] Densidad de información — sidebar izquierdo (6 ctx-block × ~5 items promedio = 30 items) + main (3 capas + test + fork = 5 bloques) + aside derecho (4 cards × 4 items = 16) = ~51 elementos informativos simultáneos en viewport. Zoom 200% rompe el grid 3-col y colapsa a 1-col sin orden priorizado. **Línea ~5025.** Fix: `@media (max-width: 1400px)` colapsa aside derecho a drawer abrible; `@media (max-width: 1024px)` colapsa sidebar izquierdo a tab accordion arriba del main; priorizar main (3 capas) como siempre-visible.
- [S3] `agent-persona-header` h1 equivalente es `<div style="font-family:Georgia...">${agent.name}</div>` (línea 4739) — NO es heading semántico. Screen reader no anuncia "encabezado nivel 1". **Línea ~4739.** Fix: `<h1 class="persona-title">`.
- [S3] Fork button dispara `alert()` (línea 4973) — bloquea screen reader y no permite cancelar con ESC. Patrón modal accesible requerido.

### Snippets

Fix S1 — affordance diferenciado por capa:
```css
/* Tokens de capa (agregar a slice A) */
:root[data-theme="light"] {
  --surface-base: #F0EBE0;        /* más oscuro que bg-subtle */
  --surface-manual: #FFFFFF;       /* = bg-surface, el editable es "lienzo en blanco" */
  --surface-learned: rgba(208, 166, 106, 0.06); /* warning tint muy leve */
  --surface-base-pattern: repeating-linear-gradient(135deg, transparent 0 12px, rgba(31,30,28,.025) 12px 13px);
}
:root[data-theme="dark"] {
  --surface-base: #1A1917;
  --surface-manual: #2A2824;
  --surface-learned: rgba(208, 166, 106, 0.10);
  --surface-base-pattern: repeating-linear-gradient(135deg, transparent 0 12px, rgba(255,255,255,.03) 12px 13px);
}

.instr-block { border-radius: var(--radius-lg); border: 1px solid var(--border-subtle); margin-bottom: var(--space-4); overflow: hidden; }
.instr-base { background: var(--surface-base); background-image: var(--surface-base-pattern); }
.instr-base .instr-body-sealed { cursor: not-allowed; user-select: text; padding: var(--space-4); font-family: var(--font-mono); font-size: var(--fs-ui-sm); line-height: 1.65; }
.instr-base::after { content: "READ ONLY · SEALED BY PUBLISHER"; position: absolute; top: var(--space-3); right: var(--space-3); font-size: 9px; letter-spacing: .08em; font-weight: 600; color: var(--text-muted); background: var(--bg-surface); padding: 2px 6px; border-radius: var(--radius-sm); }
.instr-manual { background: var(--surface-manual); border-left: 3px solid var(--coral-primary); }
.instr-manual .instr-body-editable { padding: var(--space-4); font-family: var(--font-mono); font-size: var(--fs-ui); line-height: 1.65; width: 100%; border: none; resize: vertical; min-height: 140px; background: transparent; color: var(--text-primary); }
.instr-manual .instr-body-editable:focus-visible { outline: none; box-shadow: inset 0 0 0 2px var(--coral-tint-strong); }
.instr-learned { background: var(--surface-learned); border-left: 3px solid var(--warning); }
```

Fix S1 — Learned: propuestas arriba, activas colapsadas, con preview de impacto:
```html
<section class="learned-container" aria-labelledby="learned-title">
  <header class="instr-head">
    <h3 id="learned-title" class="instr-title">
      <svg class="ico-sm ico"><use href="#i-sparkle"/></svg>
      Overlay aprendido
    </h3>
    <span class="pill pill-warning pill-dot" aria-live="polite">3 propuestas nuevas</span>
  </header>

  <div class="learned-proposed-panel" role="region" aria-label="Reglas propuestas por el sistema, pendientes de aprobación">
    <div class="learned-proposed-banner">
      <svg class="ico"><use href="#i-alert"/></svg>
      Necesitan tu visto bueno · se aplicarán solo si las aceptás
    </div>
    <!-- cada rule con preview de impacto -->
    <article class="learned-rule learned-rule-proposed">
      <header>
        <span class="pill pill-warning pill-dot">Propuesta</span>
        <span class="rule-meta">conf. <strong>87%</strong> · origen: edit-pattern ·  detectada <time>hace 2d</time></span>
      </header>
      <p class="rule-body">Cuando el cliente pida Goliath GL-112 en volumen &gt;50 pares, ofrecer Net 30 sin dual approval.</p>
      <aside class="rule-impact">
        <strong>Impacto previsto:</strong> se aplicaría a ~12% de drafts (últimos 30d · 17 casos). Cambio en tono: bajo. Cambio de política: ninguno.
      </aside>
      <footer class="rule-actions" role="group" aria-label="Acciones sobre regla propuesta">
        <button class="btn btn-ghost btn-sm" aria-label="Rechazar regla: Cuando el cliente pida Goliath">Rechazar</button>
        <span class="rule-actions-spacer"></span>
        <button class="btn btn-ghost btn-sm">Editar antes de aceptar</button>
        <button class="btn btn-primary btn-sm">Aceptar y activar</button>
      </footer>
    </article>
  </div>

  <details class="learned-accepted-panel">
    <summary>Ver 12 reglas activas del overlay aprendido</summary>
    <!-- lista colapsada -->
  </details>
</section>
```

```css
.learned-proposed-banner { display: flex; gap: var(--space-2); align-items: center; padding: var(--space-2) var(--space-3); background: rgba(208,166,106,.12); border-radius: var(--radius-md); font-size: var(--fs-ui-sm); color: var(--text-secondary); margin-bottom: var(--space-3); }
.learned-rule { border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: var(--space-3) var(--space-4); margin-bottom: var(--space-3); background: var(--bg-surface); }
.learned-rule-proposed { border-left: 3px solid var(--warning); }
.rule-impact { margin-top: var(--space-2); padding: var(--space-2) var(--space-3); background: var(--bg-subtle); border-radius: var(--radius-sm); font-size: var(--fs-ui-sm); color: var(--text-secondary); }
.rule-actions { display: flex; gap: var(--space-2); margin-top: var(--space-3); align-items: center; }
.rule-actions-spacer { flex: 1; }
```

Fix S1 — Manual textarea con dirty state + contador:
```html
<div class="instr-manual-wrap" data-dirty="false">
  <label for="overlay-manual-${skill.id}" class="sr-only">Overlay manual de ${skill.templateName}</label>
  <textarea id="overlay-manual-${skill.id}" class="instr-body-editable"
            maxlength="8000" aria-describedby="overlay-manual-help-${skill.id}"
            oninput="markDirty(this)"></textarea>
  <div class="instr-manual-meta" id="overlay-manual-help-${skill.id}">
    <span class="dirty-indicator" aria-live="polite">Sin cambios</span>
    <span class="char-counter tabular"><span class="current">0</span>/8000</span>
  </div>
</div>
```

```css
.instr-manual-wrap[data-dirty="true"] .dirty-indicator { color: var(--warning); font-weight: 600; }
.instr-manual-wrap[data-dirty="true"] .dirty-indicator::before { content: "● "; }
.char-counter { font-family: var(--font-mono); font-size: var(--fs-caption); color: var(--text-muted); }
.char-counter[data-near-limit="true"] { color: var(--warning); }
```

Fix S1 — Fork modal (reemplaza el alert):
```html
<dialog id="fork-modal" aria-labelledby="fork-title">
  <header class="modal-header">
    <h3 id="fork-title">Forkear skill · acción irreversible</h3>
  </header>
  <div class="modal-body">
    <p>Esta instancia del skill dejará de recibir upgrades del publisher y FaberLoom ya no garantiza SLA sobre outputs.</p>
    <label><input type="checkbox" name="ack-sla"> Entiendo que pierdo SLA y updates automáticos</label>
    <label><input type="checkbox" name="ack-rollback"> Entiendo que no hay rollback desde fork a template</label>
    <label>Escribí <code>FORK ${skill.templateId}</code> para confirmar
      <input type="text" pattern="^FORK ${skill.templateId}$" required>
    </label>
    <label>Código MFA
      <input type="text" inputmode="numeric" autocomplete="one-time-code" pattern="\d{6}" required>
    </label>
  </div>
  <footer class="modal-footer">
    <button class="btn btn-ghost" value="cancel">Cancelar</button>
    <button class="btn btn-danger" value="confirm" disabled>Forkear skill</button>
  </footer>
</dialog>
```
