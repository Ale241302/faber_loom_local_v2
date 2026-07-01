# AUDIT_D — Pendientes + roadmap

> Nota de scope: AUDIT_C (i18n+a11y) no existía al momento de cierre de AUDIT_D. Las filas del roadmap que dependen de C quedan marcadas `pendiente de C` en columna "Snippet ref".

## Sección G — Pending features con spec visual completa

### G.1 · Learning Thermometer widget

**Ubicación en la jerarquía.** Overlay global montado en `appShell` (mismo nivel que `launcher-root` y `toast-stack`). Posición fija `bottom-right` con `z-index: var(--z-dropdown)` (slice A C.1). Visible en todas las rutas autenticadas que involucren a un agente (Agent Console, Skill Studio, Bandeja), oculto en Landing, Settings/Perfil y Admin. Respeta el margen inferior de toast-stack sumándole `calc(var(--space-6) + 56px)` cuando hay toasts apilados.

**Wireframe estructural.** Pastilla horizontal apoyada en esquina inferior derecha, ~260px de ancho × 64px de alto, con border-left 3px del color de la temperatura (`--info` frío / `--warning` tibio / `--error` caliente). Layout: icono termómetro 28px a la izquierda (sustituye por emoji `🔵🟡🔴` con `aria-hidden`), bloque central con label ("Aprendizaje") + microfrase dinámica, contador grande tabular a la derecha con unidad "outputs pend." en 10px. Click en cualquier punto abre Modal de Consolidación. Botón `×` small top-right para hide-until-new (persiste en sesión). En estado "hot" añade animación sutil pulse en el border-left.

**Snippet HTML + CSS pegable.**

```html
<!-- Montar al final de <body> junto a launcher-root -->
<button type="button"
        id="fl-thermometer"
        class="learning-thermometer"
        data-temp="warm"
        aria-haspopup="dialog"
        aria-controls="fl-consolidation-modal"
        aria-label="Aprendizaje tibio · 4 outputs pendientes de consolidar · abrir modal"
        onclick="openConsolidationModal()">
  <span class="thermo-icon" aria-hidden="true">🟡</span>
  <span class="thermo-body">
    <span class="thermo-label">Aprendizaje · tibio</span>
    <span class="thermo-sub">Buen momento para indexar</span>
  </span>
  <span class="thermo-count">
    <span class="thermo-num tabular">4</span>
    <span class="thermo-unit">outputs pend.</span>
  </span>
  <button type="button"
          class="thermo-hide"
          aria-label="Ocultar hasta próxima actualización"
          onclick="event.stopPropagation();hideThermometer()">
    <svg class="ico-xs ico" aria-hidden="true"><use href="#i-x"/></svg>
  </button>
</button>
```

```css
.learning-thermometer {
  position: fixed;
  bottom: var(--space-6);
  right: var(--space-6);
  z-index: var(--z-dropdown);
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-left: 3px solid var(--info);
  border-radius: var(--radius-lg);
  padding: var(--space-3) var(--space-4);
  box-shadow: var(--shadow-md);
  display: inline-flex;
  align-items: center;
  gap: var(--space-3);
  min-width: 260px;
  max-width: 320px;
  cursor: pointer;
  text-align: left;
  font-family: var(--font-ui);
  transition: transform var(--duration-fast) var(--ease-standard),
              box-shadow var(--duration-fast) var(--ease-standard);
}
.learning-thermometer:hover { transform: translateY(-2px); box-shadow: var(--shadow-lg); }
.learning-thermometer:focus-visible { outline: none; box-shadow: var(--focus-ring), var(--shadow-md); }
.learning-thermometer[data-temp="cold"] { border-left-color: var(--info); }
.learning-thermometer[data-temp="warm"] { border-left-color: var(--warning); }
.learning-thermometer[data-temp="hot"]  { border-left-color: var(--error); animation: fl-thermo-pulse 2.4s var(--ease-standard) infinite; }
@keyframes fl-thermo-pulse {
  0%, 100% { box-shadow: var(--shadow-md), 0 0 0 0 rgba(184,85,85,0.35); }
  50%      { box-shadow: var(--shadow-md), 0 0 0 8px rgba(184,85,85,0); }
}
@media (prefers-reduced-motion: reduce) {
  .learning-thermometer { transition: none; }
  .learning-thermometer[data-temp="hot"] { animation: none; }
}
.thermo-icon { font-size: 22px; line-height: 1; flex-shrink: 0; }
.thermo-body { display: flex; flex-direction: column; flex: 1; min-width: 0; }
.thermo-label { font-size: var(--fs-ui-sm); font-weight: 600; color: var(--text-primary); }
.thermo-sub { font-size: var(--fs-caption); color: var(--text-secondary); }
.thermo-count { display: flex; flex-direction: column; align-items: flex-end; gap: 2px; }
.thermo-num { font-size: var(--fs-h4); font-weight: 600; color: var(--text-primary); font-variant-numeric: tabular-nums; line-height: 1; }
.thermo-unit { font-size: 10px; letter-spacing: 0.04em; text-transform: uppercase; color: var(--text-muted); }
.thermo-hide {
  position: absolute; top: 4px; right: 4px;
  background: none; border: none; padding: 4px;
  color: var(--text-muted); cursor: pointer; border-radius: var(--radius-sm);
}
.thermo-hide:hover { color: var(--text-primary); background: var(--bg-subtle); }
.thermo-hide:focus-visible { outline: none; box-shadow: var(--focus-ring); }
.learning-thermometer[hidden] { display: none; }
```

**Estados.**

- Empty (0-1 outputs): se oculta completamente (no hay nada que consolidar, no se monta).
```html
<!-- empty: widget ausente del DOM, no renderizar -->
```

- Loading (cuando el backend recalcula el shadow buffer tras `/consolidate`):
```html
<button class="learning-thermometer" data-temp="cold" disabled aria-busy="true" aria-label="Recalculando aprendizaje">
  <span class="thermo-icon" aria-hidden="true">⏳</span>
  <span class="thermo-body">
    <span class="skeleton skeleton-text" style="width:120px"></span>
    <span class="skeleton skeleton-text" style="width:80px;margin-top:4px"></span>
  </span>
  <span class="thermo-count"><span class="skeleton skeleton-text" style="width:28px;height:18px"></span></span>
</button>
```

- Error (shadow buffer no responde):
```html
<button class="learning-thermometer learning-thermometer-error" data-temp="cold" aria-label="Aprendizaje no disponible · reintentar" onclick="retryThermometer()">
  <span class="thermo-icon" aria-hidden="true"><svg class="ico"><use href="#i-alert"/></svg></span>
  <span class="thermo-body">
    <span class="thermo-label" style="color:var(--error)">Aprendizaje · error</span>
    <span class="thermo-sub">No pude leer la cola · click para reintentar</span>
  </span>
</button>
```

- Populated (caliente, 6+):
```html
<button class="learning-thermometer" data-temp="hot" aria-label="Aprendizaje caliente · 8 outputs · urgente" onclick="openConsolidationModal()">
  <span class="thermo-icon" aria-hidden="true">🔴</span>
  <span class="thermo-body">
    <span class="thermo-label">Aprendizaje · caliente</span>
    <span class="thermo-sub">Indexá ahora para no perder contexto</span>
  </span>
  <span class="thermo-count"><span class="thermo-num tabular">8</span><span class="thermo-unit">outputs pend.</span></span>
</button>
```

**Integración con tokens slice A.** Usa `--bg-surface`, `--border-subtle`, `--shadow-md`, `--shadow-lg`, `--radius-lg`, `--space-3`, `--space-4`, `--space-6`, `--fs-ui-sm`, `--fs-caption`, `--fs-h4`, `--font-ui`, `--text-primary`, `--text-secondary`, `--text-muted`, `--info`, `--warning`, `--error`, `--focus-ring`, `--duration-fast`, `--ease-standard`, `--z-dropdown`. Reutiliza `.skeleton` (slice A §C.2.8) en loading y `.ico/.ico-xs` (slice A §C.3).

**Trigger / keyboard shortcut.** Atajo global `Alt+T` (Thermometer) abre el modal si hay ≥1 output pendiente. Foco al widget: `Tab` normal dentro del flujo tras el topbar. Escape dentro del widget con foco → devuelve foco al `lastActiveElement`. Ignorar shortcut cuando el foco esté en textarea/input.

**Acceptance criteria.**
- Montado globalmente en `appShell` tras autenticación; oculto en `#/landing`, `#/admin/*` y `#/settings/perfil`.
- `data-temp` atributo refleja bucket correcto: cold `0-2`, warm `3-5`, hot `6+`. Test unit sobre la función `getThermoTemp(n)`.
- Click o Enter o `Alt+T` abren `#fl-consolidation-modal` (G.2) con foco auto en primer item.
- Recibe foco con Tab, tiene `aria-label` completo leído por VoiceOver/NVDA con valor actualizado.
- `prefers-reduced-motion` desactiva la animación pulse en estado hot.
- Estado error con botón de retry; estado loading con skeletons cumpliendo slice A §C.2.8.
- Persistencia `sessionStorage` de botón "ocultar hasta próxima actualización": vuelve a aparecer cuando el contador sube.
- No se superpone con `.toast-stack` — si hay toasts, el widget se corre `bottom: calc(var(--space-6) + 56px * n)`.

### G.2 · Modal de Consolidación

**Ubicación en la jerarquía.** Modal grande montado en `#fl-consolidation-modal`, overlay global por encima del shell (mismo nivel que `launcher-backdrop`). Se dispara exclusivamente desde Learning Thermometer (G.1), atajo `Alt+T` o desde el botón "Indexar aprendizaje" dentro de Agent Console (Ruta 8). Ancho `min(1040px, 94vw)`, alto `min(720px, 90vh)`. Layout interno 2 columnas: navegación lateral izquierda con 4 secciones y badges de conteo + panel principal derecho que muestra los items de la sección activa.

**Wireframe estructural.** Header fijo con título Georgia italic "Indexar aprendizaje · Cotizador Marluvas", subtítulo con fecha rango y contador total ("18 items · generado hace 4 min"), botón `×` cerrar. Cuerpo 2 columnas: izquierda 240px con `consolidation-nav` (4 items Patrones · Correcciones · Gold samples · Excepciones, cada uno con icono + label + `tab-count` del total); derecha panel scrolleable con lista de `consolidation-item` cards — cada card tiene título + descripción + badges (origen, confianza, volumen), tres ejes de decisión (Tipo radio / Alcance select / Propagación cross-skill checkboxes) y cluster de 4 acciones. Footer sticky con resumen ("5 aceptar · 2 editar · 3 descartar · 8 posponer") + botón primary "Aplicar cambios · 10 items".

**Snippet HTML + CSS pegable.**

```html
<dialog id="fl-consolidation-modal" class="modal-backdrop consolidation-backdrop"
        aria-labelledby="consolidation-title" aria-modal="true" role="dialog">
  <div class="modal modal-lg consolidation-modal">
    <header class="modal-header consolidation-header">
      <div>
        <h2 id="consolidation-title">Indexar aprendizaje · <em>Cotizador Marluvas</em></h2>
        <p class="consolidation-sub">Últimas 14 aprobaciones · 18 items detectados · generado hace 4 min</p>
      </div>
      <button class="icon-btn" aria-label="Cerrar modal" onclick="closeConsolidationModal()">
        <svg class="ico"><use href="#i-x"/></svg>
      </button>
    </header>

    <div class="consolidation-body">
      <nav class="consolidation-nav" role="tablist" aria-label="Secciones de consolidación">
        <button class="c-nav-item active" role="tab" aria-selected="true" aria-controls="c-panel-patterns">
          <svg class="ico-sm ico" aria-hidden="true"><use href="#i-sparkle"/></svg>
          Patrones nuevos <span class="tab-count">5</span>
        </button>
        <button class="c-nav-item" role="tab" aria-selected="false" aria-controls="c-panel-fixes">
          <svg class="ico-sm ico" aria-hidden="true"><use href="#i-edit"/></svg>
          Correcciones recurrentes <span class="tab-count">4</span>
        </button>
        <button class="c-nav-item" role="tab" aria-selected="false" aria-controls="c-panel-gold">
          <svg class="ico-sm ico" aria-hidden="true"><use href="#i-shield"/></svg>
          Gold samples candidatos <span class="tab-count">6</span>
        </button>
        <button class="c-nav-item" role="tab" aria-selected="false" aria-controls="c-panel-exceptions">
          <svg class="ico-sm ico" aria-hidden="true"><use href="#i-alert"/></svg>
          Excepciones <span class="tab-count">3</span>
        </button>
      </nav>

      <section class="consolidation-panel" id="c-panel-patterns" role="tabpanel" aria-labelledby="c-nav-patterns">
        <article class="consolidation-item" data-decision="pending">
          <header class="c-item-head">
            <span class="pill pill-warning pill-dot">Propuesta</span>
            <span class="c-item-meta">origen: edit-pattern · confianza <strong>87%</strong> · volumen 12/30d</span>
          </header>
          <h4 class="c-item-title">Cliente Marluvas pide Goliath GL-112 en Net 30 siempre</h4>
          <p class="c-item-body">Cuando el cliente pida Goliath GL-112 en volumen &gt;50 pares, ofrecer Net 30 sin dual approval.</p>

          <div class="c-item-axes">
            <fieldset class="c-axis">
              <legend class="c-axis-legend">Tipo</legend>
              <label><input type="radio" name="type-1" value="knowledge" checked> Knowledge</label>
              <label><input type="radio" name="type-1" value="instruction"> Instrucción</label>
              <label><input type="radio" name="type-1" value="output"> Output schema</label>
            </fieldset>
            <fieldset class="c-axis">
              <legend class="c-axis-legend">Alcance</legend>
              <select class="c-axis-select" aria-label="Alcance">
                <option value="user">Usuario (solo Álvaro)</option>
                <option value="skill" selected>Skill (Cotizador Marluvas)</option>
                <option value="agent">Agente (todas las skills)</option>
                <option value="org">Organización</option>
              </select>
            </fieldset>
            <fieldset class="c-axis">
              <legend class="c-axis-legend">Propagación cross-skill</legend>
              <label><input type="checkbox" value="quote-tecmater"> Quote Tecmater</label>
              <label><input type="checkbox" value="triage-rfq"> Triage RFQ</label>
              <label><input type="checkbox" value="followup"> Follow-up cobranza</label>
            </fieldset>
          </div>

          <footer class="c-item-actions" role="group" aria-label="Decisión sobre item">
            <button class="btn btn-primary btn-sm">Editar antes de indexar</button>
            <button class="btn btn-secondary btn-sm">Aceptar</button>
            <button class="btn btn-ghost btn-sm">Posponer</button>
            <button class="btn btn-ghost btn-sm c-action-discard">Descartar</button>
          </footer>
        </article>
        <!-- ... más items -->
      </section>
    </div>

    <footer class="modal-footer consolidation-footer">
      <div class="c-footer-summary" aria-live="polite">
        <span><strong>5</strong> aceptar</span>
        <span><strong>2</strong> editar</span>
        <span><strong>3</strong> descartar</span>
        <span><strong>8</strong> posponer</span>
      </div>
      <div class="c-footer-cta">
        <button class="btn btn-ghost" onclick="closeConsolidationModal()">Cancelar</button>
        <button class="btn btn-primary btn-lg" id="c-apply-btn">Aplicar cambios · 10 items</button>
      </div>
    </footer>
  </div>
</dialog>
```

```css
.consolidation-backdrop {
  position: fixed; inset: 0;
  background: var(--bg-overlay);
  backdrop-filter: blur(3px);
  z-index: var(--z-modal);
  display: flex; align-items: center; justify-content: center;
  padding: var(--space-6);
  border: none;
}
.consolidation-modal {
  width: min(1040px, 94vw);
  height: min(720px, 90vh);
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  display: grid;
  grid-template-rows: auto 1fr auto;
  overflow: hidden;
}
.consolidation-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--border-subtle);
}
.consolidation-header h2 { font-family: var(--font-display); font-style: italic; font-weight: 500; font-size: var(--fs-h3); margin: 0; color: var(--text-primary); }
.consolidation-sub { font-size: var(--fs-ui-sm); color: var(--text-secondary); margin-top: 4px; }
.consolidation-body { display: grid; grid-template-columns: 240px 1fr; overflow: hidden; }
.consolidation-nav {
  border-right: 1px solid var(--border-subtle);
  background: var(--bg-subtle);
  padding: var(--space-3);
  display: flex; flex-direction: column; gap: 2px;
  overflow-y: auto;
}
.c-nav-item {
  display: flex; align-items: center; gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border: none; background: none;
  border-radius: var(--radius-md);
  font-size: var(--fs-ui); font-weight: 500;
  color: var(--text-secondary); cursor: pointer;
  text-align: left; width: 100%;
  transition: all var(--duration-fast) var(--ease-standard);
}
.c-nav-item:hover { background: var(--bg-hover); color: var(--text-primary); }
.c-nav-item:focus-visible { outline: none; box-shadow: var(--focus-ring); }
.c-nav-item.active, .c-nav-item[aria-selected="true"] {
  background: var(--coral-tint); color: var(--coral-primary);
}
.c-nav-item .tab-count { margin-left: auto; background: var(--bg-surface); color: var(--text-secondary); font-size: 11px; padding: 1px 7px; border-radius: var(--radius-pill); font-variant-numeric: tabular-nums; }
.consolidation-panel {
  padding: var(--space-6);
  overflow-y: auto;
  display: flex; flex-direction: column; gap: var(--space-4);
}
.consolidation-item {
  border: 1px solid var(--border-subtle);
  border-left: 3px solid var(--warning);
  border-radius: var(--radius-lg);
  padding: var(--space-4) var(--space-5);
  background: var(--bg-surface);
  display: flex; flex-direction: column; gap: var(--space-3);
}
.consolidation-item[data-decision="accepted"] { border-left-color: var(--success); background: rgba(94,114,83,0.04); }
.consolidation-item[data-decision="discarded"] { border-left-color: var(--text-muted); opacity: 0.55; }
.consolidation-item[data-decision="postponed"] { border-left-color: var(--info); background: rgba(90,107,124,0.04); }
.c-item-head { display: flex; align-items: center; gap: var(--space-2); font-size: var(--fs-ui-sm); color: var(--text-secondary); }
.c-item-title { font-size: var(--fs-body); font-weight: 600; color: var(--text-primary); margin: 0; }
.c-item-body { font-size: var(--fs-body-sm); line-height: 1.55; color: var(--text-secondary); margin: 0; }
.c-item-axes { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: var(--space-3); padding: var(--space-3); background: var(--bg-subtle); border-radius: var(--radius-md); }
.c-axis { border: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.c-axis-legend { font-size: 10px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; color: var(--text-muted); margin-bottom: 4px; }
.c-axis label { display: flex; align-items: center; gap: 6px; font-size: var(--fs-ui-sm); color: var(--text-primary); cursor: pointer; }
.c-axis-select { width: 100%; padding: 6px 8px; border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); background: var(--bg-surface); font-size: var(--fs-ui-sm); color: var(--text-primary); }
.c-axis-select:focus-visible { outline: none; box-shadow: var(--focus-ring); border-color: var(--coral-primary); }
.c-item-actions { display: flex; gap: var(--space-2); flex-wrap: wrap; }
.c-action-discard { color: var(--error); }
.c-action-discard:hover { background: var(--color-error-bg, rgba(139,47,47,0.08)); }
.consolidation-footer {
  padding: var(--space-3) var(--space-6);
  border-top: 1px solid var(--border-subtle);
  background: var(--bg-subtle);
  display: flex; justify-content: space-between; align-items: center; gap: var(--space-4);
}
.c-footer-summary { display: flex; gap: var(--space-4); font-size: var(--fs-ui-sm); color: var(--text-secondary); font-variant-numeric: tabular-nums; }
.c-footer-summary strong { color: var(--text-primary); font-weight: 600; }
.c-footer-cta { display: flex; gap: var(--space-2); }
@media (max-width: 880px) {
  .consolidation-body { grid-template-columns: 1fr; }
  .consolidation-nav { border-right: none; border-bottom: 1px solid var(--border-subtle); flex-direction: row; overflow-x: auto; }
  .c-item-axes { grid-template-columns: 1fr; }
}
```

**Estados.**

- Empty (no hay items que consolidar — no debería abrirse desde thermometer, pero si se llega por URL):
```html
<section class="consolidation-panel">
  <div class="empty-state">
    <svg class="empty-state-icon"><use href="#i-sparkle"/></svg>
    <h4 class="empty-state-title">Nada que indexar todavía</h4>
    <p class="empty-state-body">El agente necesita más outputs aprobados para proponer patrones. Volvé después de aprobar 3+ drafts.</p>
    <button class="btn btn-secondary btn-sm" onclick="closeConsolidationModal()">Cerrar</button>
  </div>
</section>
```

- Loading (mientras el sistema clasifica los outputs):
```html
<section class="consolidation-panel" aria-busy="true">
  <div class="consolidation-item">
    <span class="skeleton skeleton-title"></span>
    <span class="skeleton skeleton-text" style="width:80%"></span>
    <span class="skeleton skeleton-text" style="width:60%"></span>
    <span class="skeleton" style="height:72px;margin-top:8px"></span>
  </div>
  <div class="consolidation-item">
    <span class="skeleton skeleton-title"></span>
    <span class="skeleton skeleton-text" style="width:70%"></span>
    <span class="skeleton" style="height:72px;margin-top:8px"></span>
  </div>
</section>
```

- Error (el clasificador falló):
```html
<section class="consolidation-panel">
  <div class="empty-state">
    <svg class="empty-state-icon" style="color:var(--error)"><use href="#i-alert"/></svg>
    <h4 class="empty-state-title">No pude clasificar los outputs</h4>
    <p class="empty-state-body">El pipeline de aprendizaje devolvió error. Se preserva la cola — reintentá en unos minutos.</p>
    <div style="display:flex;gap:var(--space-2)">
      <button class="btn btn-ghost btn-sm" onclick="closeConsolidationModal()">Cerrar</button>
      <button class="btn btn-primary btn-sm" onclick="retryConsolidation()">Reintentar</button>
    </div>
  </div>
</section>
```

- Populated: el snippet principal arriba.

**Integración con tokens slice A.** `--bg-overlay`, `--bg-surface`, `--bg-subtle`, `--bg-hover`, `--border-subtle`, `--radius-xl`, `--radius-lg`, `--radius-md`, `--radius-sm`, `--radius-pill`, `--shadow-lg`, `--space-3/4/5/6`, `--fs-h3`, `--fs-body`, `--fs-body-sm`, `--fs-ui`, `--fs-ui-sm`, `--font-display`, `--coral-primary`, `--coral-tint`, `--warning`, `--success`, `--info`, `--error`, `--text-primary`, `--text-secondary`, `--text-muted`, `--color-error-bg` (slice A C.1), `--focus-ring`, `--z-modal`, `--duration-fast`, `--ease-standard`. Usa `.modal-backdrop`/`.modal` (slice A §C.2.6), `.empty-state` (§C.2.7), `.skeleton` (§C.2.8), `.pill` (§C.2.1), `.tab-count` (§C.2.4).

**Trigger / keyboard shortcut.** Abre por: click en Learning Thermometer (G.1), atajo `Alt+T`, botón "Indexar aprendizaje" dentro de Agent Console. Dentro del modal: `Esc` cierra (tras confirm si hay cambios sin aplicar), `Cmd+Enter`/`Ctrl+Enter` aplica cambios, `↑/↓` navega entre items del panel activo, `1-4` cambia sección de la nav lateral. Focus trap estricto, devolver foco al trigger original.

**Acceptance criteria.**
- 4 secciones nav funcionales con `role="tablist"` + `role="tabpanel"`; navegación por flechas en el tablist.
- Cada item permite 3 ejes de decisión independientes: Tipo (radiogroup Knowledge/Instrucción/Output), Alcance (select Usuario/Skill/Agente/Org), Propagación cross-skill (checkboxes dinámicos por skill del agente).
- 4 acciones por item (Editar/Aceptar/Descartar/Posponer) cambian `data-decision` del card para feedback visual inmediato.
- Footer sticky con contador agregado actualizado `aria-live="polite"`.
- Botón primary "Aplicar cambios" deshabilitado si ningún item tiene decisión no-pending.
- Modal focus-trap completo; `Esc` con cambios pide confirm; botón `×` equivalente.
- Layout responsive: debajo de 880px se apila nav horizontal arriba y ejes en 1 columna.
- Respeta `prefers-reduced-motion`: desactiva `backdrop-filter: blur` y transiciones.

### G.3 · Acciones de ciclo de vida por artefacto

**Ubicación en la jerarquía.** Componente de menú adjunto a cada card de artefacto aprendido en:
1. Overlay Aprendido dentro de Skill Studio (Ruta 9, `.learned-rule` cards).
2. Gold Samples en Skill Studio (sección nueva dentro del editor central).
3. KB Chunks en el sidebar izquierdo de Skill Studio (`ctx-block` de KB sources).
4. Version history viewer (G.4) como acciones sobre cada snapshot.

El patrón se implementa como `.lifecycle-menu` activable por botón "···" top-right del card, o como row expandida inline cuando el card tiene foco.

**Wireframe estructural.** Cada artefacto card tiene en su esquina top-right un `icon-btn` con 3 puntos (`i-more`, si falta agregar al sprite). Click o Enter abre popover ancla-down con 5 items verticales separados en 2 grupos: grupo primario con Edit / Version history (acceso a G.4) y grupo destructivo con divider arriba: Suspend · Archive · Revert a versión anterior. Cada item tiene icono 16px + label + hint kbd opcional + sub-label si la acción muta el pipeline (ej. "Archive · mueve a Archived, reversible 30 días"). Estado visual del card refleja pipeline: border-left success=Active, warning=Candidate, info=Suspended, neutral=Archived.

**Snippet HTML + CSS pegable.**

```html
<article class="learned-rule learned-rule-accepted" data-lifecycle="active" tabindex="0">
  <header class="lr-head">
    <span class="pill pill-success pill-dot">Activa</span>
    <span class="lr-meta">v3 · aprobada por Álvaro · desde 2026-03-18</span>
    <div class="lr-actions-anchor">
      <button type="button" class="icon-btn lr-actions-trigger"
              aria-haspopup="menu" aria-expanded="false"
              aria-label="Acciones sobre la regla"
              onclick="toggleLifecycleMenu(this)">
        <svg class="ico-sm ico" aria-hidden="true"><use href="#i-more"/></svg>
      </button>
      <div class="lifecycle-menu" role="menu" hidden>
        <button role="menuitem" class="lifecycle-item" onclick="editArtifact('rule-1')">
          <svg class="ico-sm ico" aria-hidden="true"><use href="#i-edit"/></svg>
          <span class="lifecycle-label">Editar</span>
          <span class="lifecycle-kbd kbd">E</span>
        </button>
        <button role="menuitem" class="lifecycle-item" onclick="openVersionHistory('rule-1')">
          <svg class="ico-sm ico" aria-hidden="true"><use href="#i-layers"/></svg>
          <span class="lifecycle-label">Ver historial · v1..v3</span>
        </button>
        <button role="menuitem" class="lifecycle-item" onclick="revertArtifact('rule-1')">
          <svg class="ico-sm ico" aria-hidden="true"><use href="#i-arrow-right"/></svg>
          <span class="lifecycle-label">Revertir a versión anterior</span>
          <span class="lifecycle-sub">Restaura v2 · nueva versión v4</span>
        </button>
        <div class="lifecycle-divider" role="separator"></div>
        <button role="menuitem" class="lifecycle-item lifecycle-item-caution" onclick="suspendArtifact('rule-1')">
          <svg class="ico-sm ico" aria-hidden="true"><use href="#i-alert"/></svg>
          <span class="lifecycle-label">Suspender</span>
          <span class="lifecycle-sub">No se aplica · reactivable en 1 click</span>
        </button>
        <button role="menuitem" class="lifecycle-item lifecycle-item-destructive" onclick="archiveArtifact('rule-1')">
          <svg class="ico-sm ico" aria-hidden="true"><use href="#i-trash"/></svg>
          <span class="lifecycle-label">Archivar</span>
          <span class="lifecycle-sub">Reversible 30 días · luego inmutable</span>
        </button>
      </div>
    </div>
  </header>
  <p class="lr-body">Cuando el cliente pida Goliath GL-112 en volumen &gt;50 pares, ofrecer Net 30 sin dual approval.</p>
</article>
```

```css
.lr-actions-anchor { position: relative; }
.lifecycle-menu {
  position: absolute; top: calc(100% + 4px); right: 0;
  min-width: 260px;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  padding: var(--space-2);
  z-index: var(--z-dropdown);
  display: flex; flex-direction: column; gap: 2px;
}
.lifecycle-menu[hidden] { display: none; }
.lifecycle-item {
  display: grid;
  grid-template-columns: 16px 1fr auto;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: none; border: none;
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  cursor: pointer;
  font-size: var(--fs-ui-sm); font-weight: 500;
  text-align: left;
  transition: background var(--duration-fast) var(--ease-standard);
}
.lifecycle-item:hover { background: var(--bg-subtle); }
.lifecycle-item:focus-visible { outline: none; box-shadow: var(--focus-ring); }
.lifecycle-label { min-width: 0; }
.lifecycle-sub { grid-column: 2 / -1; font-size: var(--fs-caption); color: var(--text-muted); font-weight: 400; margin-top: 2px; line-height: 1.3; }
.lifecycle-kbd { grid-column: 3; font-size: 10px; color: var(--text-muted); }
.lifecycle-divider { height: 1px; background: var(--border-subtle); margin: var(--space-1) 0; }
.lifecycle-item-caution { color: var(--warning); }
.lifecycle-item-caution:hover { background: rgba(184,138,74,0.10); }
.lifecycle-item-destructive { color: var(--error); }
.lifecycle-item-destructive:hover { background: var(--color-error-bg, rgba(139,47,47,0.08)); }

/* Pipeline state reflection */
.learned-rule[data-lifecycle="candidate"] { border-left-color: var(--warning); }
.learned-rule[data-lifecycle="active"]    { border-left-color: var(--success); }
.learned-rule[data-lifecycle="suspended"] { border-left-color: var(--info); opacity: 0.7; }
.learned-rule[data-lifecycle="archived"]  { border-left-color: var(--text-muted); opacity: 0.45; background: var(--bg-subtle); }
.learned-rule[data-lifecycle="reverted"]  { border-left-color: var(--evidence); }
```

**Estados.**

- Empty (artefacto no tiene acciones disponibles porque está archivado inmutable):
```html
<div class="lifecycle-menu" role="menu">
  <div class="empty-state" style="padding:var(--space-4)">
    <p class="empty-state-body">Artefacto archivado inmutable · sin acciones disponibles</p>
    <button role="menuitem" class="lifecycle-item" onclick="openVersionHistory('rule-1')">
      <svg class="ico-sm ico" aria-hidden="true"><use href="#i-layers"/></svg>
      <span class="lifecycle-label">Ver historial · solo lectura</span>
    </button>
  </div>
</div>
```

- Loading (acción en curso — post-click de Archivar p.ej.):
```html
<article class="learned-rule" data-lifecycle="active" aria-busy="true">
  <header class="lr-head">
    <span class="pill pill-neutral">Archivando…</span>
    <span class="lr-meta"><span class="skeleton skeleton-text" style="width:120px"></span></span>
  </header>
  <p class="lr-body" style="opacity:0.5">Cuando el cliente pida Goliath GL-112…</p>
</article>
```

- Error (acción falló, ej. archive sin permisos):
```html
<article class="learned-rule" data-lifecycle="active">
  <header class="lr-head">
    <span class="pill pill-error pill-dot">Error al archivar</span>
    <span class="lr-meta">Sin permisos · contactá a Owner</span>
    <button class="btn btn-ghost btn-sm" onclick="retryLifecycleAction()">Reintentar</button>
  </header>
</article>
```

- Populated: ver snippet principal.

**Integración con tokens slice A.** `--bg-surface`, `--bg-subtle`, `--border-subtle`, `--radius-md`, `--radius-sm`, `--shadow-lg`, `--space-1/2/3`, `--fs-ui-sm`, `--fs-caption`, `--text-primary`, `--text-muted`, `--warning`, `--error`, `--success`, `--info`, `--evidence`, `--color-error-bg` (slice A C.1), `--focus-ring`, `--z-dropdown`, `--duration-fast`, `--ease-standard`. Reutiliza `.icon-btn` (slice A §C.2.10), `.pill` (§C.2.1), `.skeleton` (§C.2.8), `.empty-state` (§C.2.7).

**Trigger / keyboard shortcut.** Botón `···` en top-right del card (click + Enter + Space abren). Cuando el card tiene foco, tecla `M` abre menú. Dentro del menú: `↑/↓` navega, `Esc` cierra y devuelve foco al trigger, `Enter` ejecuta item, letra inicial salta al item con esa letra (E=Editar, A=Archivar, S=Suspender, R=Revertir). Click fuera cierra. Cada item primario tiene kbd shortcut visible (E, V, R, S, A).

**Acceptance criteria.**
- Menu con 5 acciones: Editar, Ver historial (→ abre G.4), Revertir a versión anterior, Suspender, Archivar.
- `role="menu"` + `role="menuitem"`, `aria-haspopup="menu"`, `aria-expanded` sincronizado.
- Pipeline state reflejado via `data-lifecycle` con color border-left: `candidate` → warning, `active` → success, `suspended` → info+opacity 0.7, `archived` → muted+opacity 0.45, `reverted` → evidence.
- Acciones destructivas (Archive, Revert) abren confirm modal antes de ejecutar — no se disparan directo.
- Focus trap mientras menu abierto; Esc devuelve foco al `icon-btn` trigger.
- Mismo componente reutilizable en 4 contextos (overlay aprendido, gold samples, KB chunks, snapshots de G.4).
- Acciones reversibles (Archive en <30d, Suspend siempre) generan toast con botón "Deshacer".
- `prefers-reduced-motion` desactiva transición de apertura del popover.

### G.4 · Version history viewer

**Ubicación en la jerarquía.** Modal grande invocado desde el menu de G.3 (ítem "Ver historial") aplicado a cualquier artefacto versionado: reglas del overlay aprendido, gold samples, KB chunks, policy rows (ruta 13a), skill templates (G.6). También accesible desde un botón "Ver historial" en `studio-aside-card` de Skill Studio. Modal ancho `min(960px, 94vw)`, alto `min(680px, 88vh)`.

**Wireframe estructural.** Header con título del artefacto + pill de tipo ("Regla aprendida", "Gold sample", "KB chunk", "Policy") + fecha de última modificación. Cuerpo 2 columnas: izquierda 280px con `version-timeline` — lista vertical de versiones de más reciente a más antigua, cada versión como `version-item` con número grande, timestamp, badge del aprobador (avatar + nombre), resumen del cambio en 1 línea; derecha panel con `version-detail` cambiando según la versión seleccionada: title + metadata (aprobador, commit msg, tests pasados como pills verdes, tests fallidos como pills rojos), diff visual before/after con código monospace en 2 columnas (con líneas removidas en rojo tint y agregadas en verde tint). Footer sticky con botón ghost "Descargar snapshot JSON" + botón primary "Restaurar a esta versión" (deshabilitado en versión actual).

**Snippet HTML + CSS pegable.**

```html
<dialog id="fl-version-viewer" class="modal-backdrop" aria-labelledby="vh-title" aria-modal="true" role="dialog">
  <div class="modal modal-lg version-viewer-modal">
    <header class="modal-header">
      <div>
        <h2 id="vh-title">Historial · <em>Cliente Marluvas pide Goliath GL-112 en Net 30</em></h2>
        <div class="vh-meta">
          <span class="pill pill-evidence">Regla aprendida</span>
          <span class="text-xs text-muted">3 versiones · última v3 hace 18 horas</span>
        </div>
      </div>
      <button class="icon-btn" aria-label="Cerrar" onclick="closeVersionViewer()">
        <svg class="ico"><use href="#i-x"/></svg>
      </button>
    </header>

    <div class="version-viewer-body">
      <aside class="version-timeline" role="tablist" aria-orientation="vertical" aria-label="Versiones">
        <button class="version-item active" role="tab" aria-selected="true" aria-controls="vh-panel">
          <span class="version-num">v3</span>
          <span class="version-date tabular">2026-04-18 10:22</span>
          <span class="version-summary">Ampliado volumen mínimo de 40 a 50 pares</span>
          <span class="version-author"><span class="avatar" aria-hidden="true">AS</span>Álvaro</span>
          <span class="pill pill-success pill-dot pill-xs">Actual</span>
        </button>
        <button class="version-item" role="tab" aria-selected="false" aria-controls="vh-panel">
          <span class="version-num">v2</span>
          <span class="version-date tabular">2026-03-18 14:03</span>
          <span class="version-summary">Agregada condición Net 30 explícita</span>
          <span class="version-author"><span class="avatar" aria-hidden="true">AS</span>Álvaro</span>
        </button>
        <button class="version-item" role="tab" aria-selected="false" aria-controls="vh-panel">
          <span class="version-num">v1</span>
          <span class="version-date tabular">2026-02-22 09:41</span>
          <span class="version-summary">Creación inicial desde edit-pattern</span>
          <span class="version-author"><span class="avatar" aria-hidden="true">SY</span>Sistema</span>
        </button>
      </aside>

      <section class="version-detail" id="vh-panel" role="tabpanel">
        <header class="vh-detail-head">
          <h3>v3 · 2026-04-18 10:22</h3>
          <div class="vh-detail-meta">
            <span class="text-xs">Aprobado por <strong>Álvaro Solórzano</strong></span>
            <span class="text-xs">·</span>
            <span class="text-xs">Commit: <code>bf7c2a1</code></span>
          </div>
          <div class="vh-tests">
            <span class="pill pill-success">4 evals pasados</span>
            <span class="pill pill-warning">1 eval con drift bajo</span>
          </div>
        </header>

        <div class="vh-diff">
          <div class="vh-diff-col vh-diff-before">
            <div class="vh-diff-label">v2 (antes)</div>
            <pre><code><span class="diff-line diff-unchanged">Cuando el cliente pida Goliath GL-112</span>
<span class="diff-line diff-removed">- en volumen &gt;40 pares, ofrecer Net 30</span>
<span class="diff-line diff-unchanged">sin dual approval.</span></code></pre>
          </div>
          <div class="vh-diff-col vh-diff-after">
            <div class="vh-diff-label">v3 (actual)</div>
            <pre><code><span class="diff-line diff-unchanged">Cuando el cliente pida Goliath GL-112</span>
<span class="diff-line diff-added">+ en volumen &gt;50 pares, ofrecer Net 30</span>
<span class="diff-line diff-unchanged">sin dual approval.</span></code></pre>
          </div>
        </div>
      </section>
    </div>

    <footer class="modal-footer">
      <button class="btn btn-ghost" onclick="downloadSnapshot('v3')">
        <svg class="ico-sm ico" aria-hidden="true"><use href="#i-file"/></svg>
        Descargar snapshot JSON
      </button>
      <div style="display:flex;gap:var(--space-2)">
        <button class="btn btn-ghost" onclick="closeVersionViewer()">Cerrar</button>
        <button class="btn btn-primary" disabled aria-disabled="true" title="Ya estás en la versión actual">Restaurar a esta versión</button>
      </div>
    </footer>
  </div>
</dialog>
```

```css
.version-viewer-modal {
  width: min(960px, 94vw);
  height: min(680px, 88vh);
  display: grid;
  grid-template-rows: auto 1fr auto;
  background: var(--bg-surface);
  border-radius: var(--radius-xl);
  overflow: hidden;
}
.vh-meta { display: flex; gap: var(--space-2); align-items: center; margin-top: 4px; }
.version-viewer-body { display: grid; grid-template-columns: 280px 1fr; overflow: hidden; }
.version-timeline {
  border-right: 1px solid var(--border-subtle);
  background: var(--bg-subtle);
  padding: var(--space-3);
  display: flex; flex-direction: column; gap: var(--space-2);
  overflow-y: auto;
}
.version-item {
  display: grid;
  grid-template-columns: 40px 1fr auto;
  grid-template-rows: auto auto auto;
  gap: 4px 8px;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  cursor: pointer;
  text-align: left;
  transition: all var(--duration-fast) var(--ease-standard);
  font-family: var(--font-ui);
}
.version-item:hover { background: var(--bg-hover); border-color: var(--border-strong); }
.version-item:focus-visible { outline: none; box-shadow: var(--focus-ring); }
.version-item.active, .version-item[aria-selected="true"] {
  border-color: var(--coral-primary);
  background: var(--coral-tint);
}
.version-num {
  grid-row: 1 / 3; grid-column: 1;
  font-family: var(--font-display); font-style: italic;
  font-size: 22px; font-weight: 500; color: var(--coral-primary);
  align-self: center;
}
.version-date { grid-column: 2 / 4; grid-row: 1; font-size: 10px; color: var(--text-muted); font-variant-numeric: tabular-nums; }
.version-summary { grid-column: 2 / 4; grid-row: 2; font-size: var(--fs-ui-sm); font-weight: 500; color: var(--text-primary); line-height: 1.3; }
.version-author { grid-column: 2; grid-row: 3; display: inline-flex; align-items: center; gap: 4px; font-size: var(--fs-caption); color: var(--text-secondary); }
.version-author .avatar {
  width: 16px; height: 16px; border-radius: 50%;
  background: var(--coral-tint); color: var(--coral-primary);
  font-size: 9px; font-weight: 600;
  display: inline-flex; align-items: center; justify-content: center;
}
.pill-xs { font-size: 9px; padding: 1px 5px; }

.version-detail { padding: var(--space-5) var(--space-6); overflow-y: auto; display: flex; flex-direction: column; gap: var(--space-4); }
.vh-detail-head h3 { font-size: var(--fs-h4); font-weight: 600; margin: 0; color: var(--text-primary); }
.vh-detail-meta { display: flex; gap: var(--space-2); align-items: center; color: var(--text-secondary); margin-top: 4px; }
.vh-detail-meta code { font-family: var(--font-mono); font-size: 11px; background: var(--bg-subtle); padding: 1px 5px; border-radius: var(--radius-sm); }
.vh-tests { display: flex; gap: var(--space-2); margin-top: var(--space-2); flex-wrap: wrap; }

.vh-diff { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-3); }
.vh-diff-col { background: var(--bg-subtle); border-radius: var(--radius-md); overflow: hidden; border: 1px solid var(--border-subtle); }
.vh-diff-label {
  padding: var(--space-2) var(--space-3);
  background: var(--bg-hover);
  border-bottom: 1px solid var(--border-subtle);
  font-size: var(--fs-caption); font-weight: 600; color: var(--text-secondary);
  text-transform: uppercase; letter-spacing: 0.05em;
}
.vh-diff-col pre { margin: 0; padding: var(--space-3); font-family: var(--font-mono); font-size: var(--fs-ui-sm); line-height: 1.6; overflow-x: auto; }
.diff-line { display: block; padding: 0 var(--space-2); border-radius: var(--radius-sm); }
.diff-unchanged { color: var(--text-secondary); }
.diff-removed { color: var(--error); background: rgba(139,47,47,0.08); }
.diff-added { color: var(--success); background: rgba(94,114,83,0.10); }
[data-theme="dark"] .diff-removed { background: rgba(217,112,112,0.15); }
[data-theme="dark"] .diff-added { background: rgba(155,173,140,0.15); }

@media (max-width: 880px) {
  .version-viewer-body { grid-template-columns: 1fr; }
  .version-timeline { border-right: none; border-bottom: 1px solid var(--border-subtle); max-height: 240px; }
  .vh-diff { grid-template-columns: 1fr; }
}
```

**Estados.**

- Empty (artefacto nuevo, solo 1 versión):
```html
<aside class="version-timeline">
  <div class="empty-state" style="padding:var(--space-4)">
    <svg class="empty-state-icon"><use href="#i-layers"/></svg>
    <h4 class="empty-state-title">Sin historial aún</h4>
    <p class="empty-state-body">Este artefacto está en v1. Cuando se apliquen cambios vas a ver las versiones acá.</p>
  </div>
</aside>
```

- Loading (trayendo snapshots del event store):
```html
<aside class="version-timeline" aria-busy="true">
  <div class="version-item"><span class="skeleton" style="height:24px;width:32px"></span><span class="skeleton skeleton-text" style="width:120px"></span><span class="skeleton skeleton-text" style="width:180px"></span></div>
  <div class="version-item"><span class="skeleton" style="height:24px;width:32px"></span><span class="skeleton skeleton-text" style="width:120px"></span><span class="skeleton skeleton-text" style="width:160px"></span></div>
</aside>
<section class="version-detail" aria-busy="true">
  <span class="skeleton skeleton-title"></span>
  <span class="skeleton skeleton-text" style="width:60%"></span>
  <span class="skeleton" style="height:200px;margin-top:var(--space-4)"></span>
</section>
```

- Error (event store inaccesible):
```html
<section class="version-detail">
  <div class="empty-state">
    <svg class="empty-state-icon" style="color:var(--error)"><use href="#i-alert"/></svg>
    <h4 class="empty-state-title">No pude leer el historial</h4>
    <p class="empty-state-body">El event store no responde. El artefacto actual sigue operando, solo la lectura histórica falló.</p>
    <button class="btn btn-secondary btn-sm" onclick="retryVersionHistory()">Reintentar</button>
  </div>
</section>
```

- Populated: snippet principal.

**Integración con tokens slice A.** `--bg-surface`, `--bg-subtle`, `--bg-hover`, `--border-subtle`, `--border-strong`, `--radius-xl`, `--radius-md`, `--radius-sm`, `--space-2/3/4/5/6`, `--fs-h4`, `--fs-ui-sm`, `--fs-caption`, `--font-display`, `--font-mono`, `--font-ui`, `--text-primary`, `--text-secondary`, `--text-muted`, `--coral-primary`, `--coral-tint`, `--error`, `--success`, `--evidence`, `--focus-ring`, `--duration-fast`, `--ease-standard`. Usa `.modal-backdrop`/`.modal` (slice A §C.2.6), `.empty-state` (§C.2.7), `.skeleton` (§C.2.8), `.pill` (§C.2.1) incluida propuesta `pill-xs` como addendum a slice A.

**Trigger / keyboard shortcut.** Se invoca vía G.3 "Ver historial" o botón dedicado en `studio-aside-card`. Atajo dentro del modal: `↑/↓` navega versiones de la timeline, `Enter` selecciona y muestra detalle, `R` foco al botón "Restaurar", `D` dispara descargar snapshot, `Esc` cierra con foco al trigger original. Focus trap estricto.

**Acceptance criteria.**
- Timeline vertical de versiones con cada item mostrando: numeración (v1, v2, v3…), timestamp tabular, aprobador (avatar + nombre), resumen del cambio en 1 línea, badge "Actual" en la última.
- `role="tablist"` vertical; teclas flecha navegan; selección sincroniza panel detalle.
- Detalle por versión: titulo, metadata (aprobador, commit hash/msg), pills de tests con resultado, diff visual before/after monospace.
- Diff usa clases `.diff-added`/`.diff-removed`/`.diff-unchanged` con colores WCAG AA (incluye override dark).
- Botón "Restaurar a esta versión" deshabilitado en la versión actual; en cualquier otra, abre confirm modal que crea una **nueva versión v(N+1)** (no mutación in-place).
- Botón "Descargar snapshot JSON" exporta metadata + payload del artefacto.
- Responsive: <880px colapsa a una sola columna, timeline sobre detail.
- `prefers-reduced-motion` desactiva transiciones del highlight al cambiar versión.

### G.5 · Shadow memory panel

**Ubicación en la jerarquía.** Dentro de Skill Studio (ruta `#/agentes/:id`). Se agrega como cuarta columna a la derecha del aside existente (runtime/versions/impact), colapsable a drawer. Por default es drawer cerrado al que se accede con botón "Shadow memory" en el topbar del studio-layout, mostrando badge con contador de items pendientes. Cuando se abre, desplaza el layout 3-col → 4-col en viewports ≥1560px, o en viewports <1560px se abre como drawer flotante desde la derecha con overlay sutil (no bloqueante, sin backdrop opaco).

**Wireframe estructural.** Ancho 320px. Header sticky con título "Shadow memory", contador total, filtros pills (Todos · Candidates · Proposed) + icon-btn para cerrar. Body scrolleable con lista vertical de `shadow-item` cards de 12-16 por visualizador — cada card: micro-pill de tipo (`candidate`/`proposed`) con color del pipeline, subject (primera línea del aprendizaje truncado a 2 líneas), micro-row con 3 badges en fila (origen icon+label · timestamp relativo tabular · barra horizontal de confianza 3px), acciones rápidas inline: "Promover a Gold" (primary-sm) + "Descartar" (ghost-sm). Footer sticky con contador "12 items · última clasificación hace 3 min" + link "Abrir Modal de Consolidación (G.2)".

**Snippet HTML + CSS pegable.**

```html
<aside class="shadow-panel" id="shadow-memory-drawer" aria-label="Memoria shadow del agente" tabindex="-1">
  <header class="shadow-panel-head">
    <div>
      <h3>Shadow memory</h3>
      <span class="text-xs text-muted">12 items no indexados</span>
    </div>
    <button class="icon-btn" aria-label="Cerrar panel" onclick="closeShadowPanel()">
      <svg class="ico-sm ico" aria-hidden="true"><use href="#i-x"/></svg>
    </button>
  </header>

  <div class="shadow-panel-filters" role="tablist" aria-label="Filtrar por tipo">
    <button class="filter-chip active" role="tab" aria-pressed="true">Todos <span class="tab-count">12</span></button>
    <button class="filter-chip" role="tab" aria-pressed="false">Candidates <span class="tab-count">7</span></button>
    <button class="filter-chip" role="tab" aria-pressed="false">Proposed <span class="tab-count">5</span></button>
  </div>

  <div class="shadow-panel-list" role="list">
    <article class="shadow-item" data-type="proposed" role="listitem">
      <header class="shadow-item-head">
        <span class="pill pill-warning pill-dot pill-xs">Proposed</span>
        <span class="shadow-item-source">
          <svg class="ico-xs ico" aria-hidden="true"><use href="#i-edit"/></svg>
          edit-pattern
        </span>
      </header>
      <p class="shadow-item-body">Cliente Marluvas siempre pide Net 30 cuando volumen supera 50 pares de Goliath GL-112.</p>
      <div class="shadow-item-foot">
        <span class="shadow-item-time" title="2026-04-18 10:22">hace 4h</span>
        <div class="shadow-confidence" title="Confianza estimada 87%">
          <span class="shadow-conf-track"><span class="shadow-conf-fill" style="width:87%"></span></span>
          <span class="shadow-conf-label tabular">87%</span>
        </div>
      </div>
      <div class="shadow-item-actions">
        <button class="btn btn-primary btn-sm" onclick="promoteToGold('shadow-1')">Promover a Gold</button>
        <button class="btn btn-ghost btn-sm" onclick="discardShadowItem('shadow-1')">Descartar</button>
      </div>
    </article>

    <article class="shadow-item" data-type="candidate" role="listitem">
      <header class="shadow-item-head">
        <span class="pill pill-info pill-dot pill-xs">Candidate</span>
        <span class="shadow-item-source"><svg class="ico-xs ico"><use href="#i-check"/></svg>approval-streak</span>
      </header>
      <p class="shadow-item-body">Saludo "Muito obrigado" solo cuando cliente escribe en portugués.</p>
      <div class="shadow-item-foot">
        <span class="shadow-item-time">hace 1d</span>
        <div class="shadow-confidence">
          <span class="shadow-conf-track"><span class="shadow-conf-fill" style="width:62%"></span></span>
          <span class="shadow-conf-label tabular">62%</span>
        </div>
      </div>
      <div class="shadow-item-actions">
        <button class="btn btn-primary btn-sm">Promover a Gold</button>
        <button class="btn btn-ghost btn-sm">Descartar</button>
      </div>
    </article>
  </div>

  <footer class="shadow-panel-foot">
    <span class="text-xs text-muted">Última clasificación hace 3 min</span>
    <button class="btn btn-secondary btn-sm" onclick="openConsolidationModal()">
      <svg class="ico-sm ico" aria-hidden="true"><use href="#i-sparkle"/></svg>
      Consolidar todos
    </button>
  </footer>
</aside>
```

```css
.shadow-panel {
  width: 320px;
  background: var(--bg-surface);
  border-left: 1px solid var(--border-subtle);
  display: grid;
  grid-template-rows: auto auto 1fr auto;
  height: 100%;
  font-family: var(--font-ui);
}
/* Modo drawer flotante en viewports < 1560px */
@media (max-width: 1559px) {
  .shadow-panel {
    position: fixed; top: 56px; right: 0; bottom: 0;
    z-index: var(--z-dropdown);
    box-shadow: var(--shadow-lg);
    transform: translateX(100%);
    transition: transform var(--duration-base) var(--ease-standard);
  }
  .shadow-panel[data-open="true"] { transform: translateX(0); }
}
@media (prefers-reduced-motion: reduce) {
  .shadow-panel { transition: none; }
}

.shadow-panel-head {
  padding: var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
  display: flex; justify-content: space-between; align-items: flex-start;
  background: var(--bg-surface);
  position: sticky; top: 0; z-index: 2;
}
.shadow-panel-head h3 { margin: 0; font-size: var(--fs-body); font-weight: 600; color: var(--text-primary); }

.shadow-panel-filters { display: flex; gap: var(--space-1); padding: var(--space-2) var(--space-4); border-bottom: 1px solid var(--border-subtle); overflow-x: auto; }
.shadow-panel-filters .filter-chip { font-size: var(--fs-ui-sm); padding: 4px 10px; }

.shadow-panel-list { overflow-y: auto; padding: var(--space-3); display: flex; flex-direction: column; gap: var(--space-3); }

.shadow-item {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  background: var(--bg-surface);
  display: flex; flex-direction: column; gap: var(--space-2);
  transition: all var(--duration-fast) var(--ease-standard);
}
.shadow-item:hover { box-shadow: var(--shadow-sm); border-color: var(--border-strong); }
.shadow-item:focus-within { box-shadow: var(--focus-ring); }
.shadow-item[data-type="proposed"]  { border-left: 3px solid var(--warning); }
.shadow-item[data-type="candidate"] { border-left: 3px solid var(--info); }

.shadow-item-head { display: flex; justify-content: space-between; align-items: center; font-size: var(--fs-caption); color: var(--text-muted); }
.shadow-item-source { display: inline-flex; align-items: center; gap: 4px; font-size: var(--fs-caption); color: var(--text-secondary); }
.shadow-item-body { margin: 0; font-size: var(--fs-ui-sm); line-height: 1.45; color: var(--text-primary); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.shadow-item-foot { display: flex; justify-content: space-between; align-items: center; gap: var(--space-2); }
.shadow-item-time { font-size: var(--fs-caption); color: var(--text-muted); }
.shadow-confidence { display: inline-flex; align-items: center; gap: var(--space-2); }
.shadow-conf-track { display: inline-block; width: 64px; height: 3px; background: var(--bg-hover); border-radius: var(--radius-pill); overflow: hidden; }
.shadow-conf-fill { display: block; height: 100%; background: linear-gradient(90deg, var(--warning) 0%, var(--success) 100%); }
.shadow-conf-label { font-size: var(--fs-caption); color: var(--text-secondary); font-variant-numeric: tabular-nums; }

.shadow-item-actions { display: flex; gap: var(--space-2); margin-top: var(--space-1); }

.shadow-panel-foot {
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--border-subtle);
  display: flex; justify-content: space-between; align-items: center; gap: var(--space-2);
  background: var(--bg-subtle);
  position: sticky; bottom: 0;
}
```

**Estados.**

- Empty (agente sin actividad reciente):
```html
<aside class="shadow-panel">
  <header class="shadow-panel-head"><h3>Shadow memory</h3></header>
  <div class="shadow-panel-list">
    <div class="empty-state">
      <svg class="empty-state-icon"><use href="#i-sparkle"/></svg>
      <h4 class="empty-state-title">Sin items en shadow</h4>
      <p class="empty-state-body">Cuando el agente genere outputs nuevos y vos los aprobés o edités, los patrones candidatos aparecerán acá.</p>
    </div>
  </div>
</aside>
```

- Loading (rehidratando desde event store):
```html
<div class="shadow-panel-list" aria-busy="true">
  <div class="shadow-item">
    <span class="skeleton skeleton-text" style="width:40%"></span>
    <span class="skeleton skeleton-text"></span>
    <span class="skeleton skeleton-text" style="width:90%"></span>
  </div>
  <div class="shadow-item">
    <span class="skeleton skeleton-text" style="width:40%"></span>
    <span class="skeleton skeleton-text"></span>
    <span class="skeleton skeleton-text" style="width:70%"></span>
  </div>
</div>
```

- Error (clasificador offline):
```html
<div class="shadow-panel-list">
  <div class="empty-state">
    <svg class="empty-state-icon" style="color:var(--error)"><use href="#i-alert"/></svg>
    <h4 class="empty-state-title">No pude leer shadow memory</h4>
    <p class="empty-state-body">La cola persiste · reintentá en un momento.</p>
    <button class="btn btn-secondary btn-sm" onclick="retryShadowLoad()">Reintentar</button>
  </div>
</div>
```

- Populated: snippet principal.

**Integración con tokens slice A.** `--bg-surface`, `--bg-subtle`, `--bg-hover`, `--border-subtle`, `--border-strong`, `--radius-md`, `--radius-pill`, `--shadow-sm`, `--shadow-lg`, `--space-1/2/3/4`, `--fs-body`, `--fs-ui-sm`, `--fs-caption`, `--font-ui`, `--text-primary`, `--text-secondary`, `--text-muted`, `--warning`, `--info`, `--success`, `--error`, `--focus-ring`, `--z-dropdown`, `--duration-fast`, `--duration-base`, `--ease-standard`. Usa `.filter-chip[aria-pressed]` (addendum slice A ruta 3), `.empty-state` (§C.2.7), `.skeleton` (§C.2.8), `.pill` (§C.2.1), `.btn` variants, `.tab-count`.

**Trigger / keyboard shortcut.** Botón "Shadow memory" en topbar de Skill Studio con badge numérico + atajo global `Alt+S` abre/cierra. Dentro del panel: `Tab` navega items, cada `.shadow-item` es `role="listitem"` con focus-within ring; `P` foco al botón "Promover" del item activo, `D` al botón "Descartar", `Esc` cierra drawer y devuelve foco al trigger. En modo split ≥1560px el panel es persistente y `Esc` solo cierra si explícitamente se abrió como drawer.

**Acceptance criteria.**
- Se monta como 4ta columna en Skill Studio en viewports ≥1560px; como drawer flotante desde la derecha en viewports menores.
- Header sticky con contador total; filtros pills `Todos/Candidates/Proposed` con counts actualizados.
- Cada item muestra: tipo (candidate/proposed), source (output/feedback/chat/edit-pattern/approval-streak) con icono, timestamp relativo con `title` absoluto, barra horizontal de confianza con % tabular.
- Acciones inline: Promover a Gold (abre confirm o mini-modal para completar 13 campos del gold sample) + Descartar (confirm destructivo).
- Border-left visual para tipo: proposed → warning, candidate → info.
- `role="list"` en container, `role="listitem"` en cada card.
- Focus-within ring en el item para compensar que hay múltiples botones internos.
- Respeta `prefers-reduced-motion` en la animación slide del drawer.
- Drawer cierra con `Esc` solo cuando está abierto explícitamente; en modo split persistente no cierra.

### G.6 · Agent Factory (`#/factory`)

**Ubicación en la jerarquía.** Nueva ruta `#/factory` accesible desde sidebar (sección "Creación" con item "Agent Factory" + icono `i-anvil`). Visible solo para roles `owner` y `skill_publisher`. En el sidebar se ubica bajo "Workflows" y encima de "Conexiones". Breadcrumb: `Admin · Agent Factory · [Template name]`.

**Wireframe estructural.** Layout 2 columnas: izquierda `factory-sidebar` 320px con header "Templates" + botón primary "Nuevo template" + tabs `Drafts/Beta/Published/Archived` + lista `template-list-item` (nombre + publisher + versión + status pill); derecha `factory-editor` con metadata bar sticky (Id mono + nombre editable + version + category + tags chips + status select + acciones Save draft/Publish/Deprecate), cuerpo en `factory-fields` dividido en 7 secciones colapsables: Base instructions (textarea grande que queda `sealed after publish`), Embedded context (chunks KB referenciados), Output schema (JSON editor), Guardrails (selector de policies + autonomy ceiling slider L0-L5), Connections required (multi-select), Trigger word (input + preview), Publishing metadata (publisher, license, changelog). Footer con resumen de validaciones.

**Snippet HTML + CSS pegable.**

```html
<div class="factory-layout">
  <aside class="factory-sidebar">
    <header class="factory-sidebar-head">
      <h2>Templates</h2>
      <button class="btn btn-primary btn-sm" onclick="newTemplate()">
        <svg class="ico-sm ico" aria-hidden="true"><use href="#i-plus"/></svg>Nuevo template
      </button>
    </header>
    <nav class="tabs factory-tabs" role="tablist" aria-label="Filtrar templates">
      <button class="tab active" role="tab" aria-selected="true">Drafts <span class="tab-count">3</span></button>
      <button class="tab" role="tab" aria-selected="false">Beta <span class="tab-count">1</span></button>
      <button class="tab" role="tab" aria-selected="false">Published <span class="tab-count">8</span></button>
      <button class="tab" role="tab" aria-selected="false">Archived <span class="tab-count">4</span></button>
    </nav>
    <div class="template-list" role="list">
      <button class="template-list-item active" role="listitem" aria-selected="true">
        <div class="template-li-head">
          <span class="template-li-name">Cotizador B2B Calzado Seguridad</span>
          <span class="pill pill-warning pill-xs">draft</span>
        </div>
        <div class="template-li-meta">
          <span class="template-li-publisher">muito.work</span>
          <span>·</span>
          <span class="template-li-version">v0.4.1</span>
        </div>
      </button>
      <button class="template-list-item" role="listitem">
        <div class="template-li-head">
          <span class="template-li-name">Follow-up cobranza LATAM</span>
          <span class="pill pill-info pill-xs">draft</span>
        </div>
        <div class="template-li-meta">
          <span class="template-li-publisher">muito.work</span>
          <span>·</span>
          <span class="template-li-version">v0.2.0</span>
        </div>
      </button>
    </div>
  </aside>

  <main class="factory-editor">
    <header class="factory-meta-bar">
      <div class="factory-meta-left">
        <code class="template-id">tpl_cotizador_b2b_calzado</code>
        <input type="text" class="factory-name-input" value="Cotizador B2B Calzado Seguridad" aria-label="Nombre del template">
        <span class="pill pill-neutral">v0.4.1</span>
        <select class="factory-category" aria-label="Categoría">
          <option value="sales" selected>Ventas B2B</option>
          <option value="support">Atención</option>
          <option value="operations">Operaciones</option>
        </select>
      </div>
      <div class="factory-meta-right">
        <button class="btn btn-ghost btn-sm">Save draft</button>
        <button class="btn btn-secondary btn-sm">Publish new version</button>
        <button class="btn btn-ghost btn-sm factory-deprecate">Deprecate</button>
      </div>
    </header>

    <div class="factory-fields">
      <details class="factory-field-group" open>
        <summary><svg class="ico-sm ico" aria-hidden="true"><use href="#i-lock"/></svg>Base instructions <span class="text-xs text-muted">(sealed after publish)</span></summary>
        <textarea class="factory-textarea" rows="12" placeholder="Describí el rol, objetivo y reglas obligatorias del agente…">Sos un cotizador de calzado de seguridad industrial B2B para distribuidores LATAM...</textarea>
        <div class="factory-hint text-xs text-muted">Este contenido se sella cuando pases a Published. Cambios posteriores requieren fork o nueva versión mayor.</div>
      </details>

      <details class="factory-field-group" open>
        <summary><svg class="ico-sm ico" aria-hidden="true"><use href="#i-book"/></svg>Embedded context <span class="text-xs text-muted">KB chunks referenciados por default</span></summary>
        <div class="factory-chunk-list">
          <span class="pill pill-evidence">Catálogo Marluvas 2026 Q1</span>
          <span class="pill pill-evidence">Política pricing B2B v1.4</span>
          <button class="btn btn-ghost btn-sm">+ Agregar chunk</button>
        </div>
      </details>

      <details class="factory-field-group">
        <summary><svg class="ico-sm ico" aria-hidden="true"><use href="#i-workflow"/></svg>Output schema (JSON)</summary>
        <pre class="factory-json-editor" contenteditable="true" spellcheck="false">{
  "type": "quote",
  "currency": "CRC|USD",
  "items": [{ "sku": "string", "qty": "number", "unit_price": "number" }],
  "payment_terms": "enum: Net15|Net30|Contado",
  "valid_until": "date"
}</pre>
      </details>

      <details class="factory-field-group">
        <summary><svg class="ico-sm ico" aria-hidden="true"><use href="#i-shield"/></svg>Guardrails</summary>
        <div class="factory-guardrails">
          <fieldset>
            <legend class="factory-field-label">Policies obligatorias</legend>
            <label><input type="checkbox" checked> pricing_b2b_v1.4</label>
            <label><input type="checkbox" checked> dual_approval_for_discount_over_15</label>
            <label><input type="checkbox"> regional_compliance_latam</label>
          </fieldset>
          <div class="factory-autonomy">
            <label class="factory-field-label" for="autonomy-slider">Autonomy ceiling</label>
            <input type="range" id="autonomy-slider" min="0" max="5" value="1" list="autonomy-marks">
            <datalist id="autonomy-marks"><option value="0" label="L0"><option value="1" label="L1"><option value="2" label="L2"><option value="3" label="L3"><option value="4" label="L4"><option value="5" label="L5"></datalist>
            <span class="text-xs text-muted">L1 · Propone siempre (draft-first)</span>
          </div>
        </div>
      </details>

      <details class="factory-field-group">
        <summary><svg class="ico-sm ico" aria-hidden="true"><use href="#i-plug"/></svg>Connections required</summary>
        <div class="factory-conn-list">
          <span class="pill pill-coral">Gmail · read</span>
          <span class="pill pill-coral">HubSpot · write</span>
          <button class="btn btn-ghost btn-sm">+ Agregar conexión</button>
        </div>
      </details>

      <details class="factory-field-group">
        <summary><svg class="ico-sm ico" aria-hidden="true"><use href="#i-sparkle"/></svg>Trigger word</summary>
        <div class="factory-trigger-row">
          <input type="text" class="input" value="@cotiza" aria-label="Trigger word" pattern="@[a-z]+">
          <div class="text-xs text-muted">Los usuarios activan este agente escribiendo <code>@cotiza</code> en cualquier superficie de FaberLoom.</div>
        </div>
      </details>
    </div>

    <footer class="factory-footer">
      <div class="factory-validations text-xs" aria-live="polite">
        <span class="pill pill-success">7 checks OK</span>
        <span class="pill pill-warning">1 warning: sin ejemplos</span>
      </div>
      <span class="text-xs text-muted">Última edición hace 12 min por Álvaro</span>
    </footer>
  </main>
</div>
```

```css
.factory-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  height: calc(100vh - 56px);
  background: var(--bg-primary);
}
.factory-sidebar {
  border-right: 1px solid var(--border-subtle);
  background: var(--bg-surface);
  display: grid;
  grid-template-rows: auto auto 1fr;
  overflow: hidden;
}
.factory-sidebar-head { padding: var(--space-4); display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-subtle); }
.factory-sidebar-head h2 { margin: 0; font-size: var(--fs-body); font-weight: 600; }
.factory-tabs { padding: 0 var(--space-3); overflow-x: auto; }
.template-list { padding: var(--space-2); display: flex; flex-direction: column; gap: 4px; overflow-y: auto; }
.template-list-item {
  padding: var(--space-3);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  background: none;
  cursor: pointer;
  text-align: left;
  display: flex; flex-direction: column; gap: 4px;
  transition: all var(--duration-fast) var(--ease-standard);
}
.template-list-item:hover { background: var(--bg-subtle); }
.template-list-item:focus-visible { outline: none; box-shadow: var(--focus-ring); }
.template-list-item.active { background: var(--coral-tint); border-color: var(--coral-primary); }
.template-li-head { display: flex; justify-content: space-between; align-items: center; gap: var(--space-2); }
.template-li-name { font-size: var(--fs-ui-sm); font-weight: 600; color: var(--text-primary); }
.template-li-meta { display: flex; gap: 4px; font-size: var(--fs-caption); color: var(--text-muted); }

.factory-editor { display: grid; grid-template-rows: auto 1fr auto; overflow: hidden; }
.factory-meta-bar {
  padding: var(--space-3) var(--space-6);
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-surface);
  display: flex; justify-content: space-between; align-items: center; gap: var(--space-3);
  position: sticky; top: 0; z-index: 2;
  flex-wrap: wrap;
}
.factory-meta-left { display: flex; align-items: center; gap: var(--space-2); flex-wrap: wrap; }
.factory-meta-right { display: flex; gap: var(--space-2); }
.template-id { font-family: var(--font-mono); font-size: var(--fs-caption); color: var(--text-muted); background: var(--bg-subtle); padding: 2px 6px; border-radius: var(--radius-sm); }
.factory-name-input {
  border: none; background: none;
  font-family: var(--font-display); font-style: italic; font-size: var(--fs-h4); font-weight: 500;
  color: var(--text-primary); min-width: 280px;
  padding: 4px 8px; border-radius: var(--radius-sm);
}
.factory-name-input:hover { background: var(--bg-subtle); }
.factory-name-input:focus-visible { outline: none; box-shadow: var(--focus-ring); background: var(--bg-surface); }
.factory-category { padding: 4px 8px; border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); background: var(--bg-surface); font-size: var(--fs-ui-sm); }
.factory-deprecate { color: var(--error); }

.factory-fields { padding: var(--space-5) var(--space-6); overflow-y: auto; display: flex; flex-direction: column; gap: var(--space-4); }
.factory-field-group {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--bg-surface);
  overflow: hidden;
}
.factory-field-group > summary {
  padding: var(--space-3) var(--space-4);
  cursor: pointer;
  display: flex; align-items: center; gap: var(--space-2);
  font-size: var(--fs-body); font-weight: 600; color: var(--text-primary);
  background: var(--bg-subtle);
  list-style: none;
}
.factory-field-group > summary::-webkit-details-marker { display: none; }
.factory-field-group > summary::before { content: '▸'; color: var(--text-muted); font-size: 12px; transition: transform var(--duration-fast) var(--ease-standard); }
.factory-field-group[open] > summary::before { transform: rotate(90deg); }
.factory-field-group[open] > *:not(summary) { padding: var(--space-4); }
.factory-textarea { width: 100%; min-height: 160px; padding: var(--space-3); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); font-family: var(--font-mono); font-size: var(--fs-ui-sm); line-height: 1.6; background: var(--bg-surface); color: var(--text-primary); resize: vertical; }
.factory-textarea:focus-visible { outline: none; box-shadow: var(--focus-ring); }
.factory-hint { margin-top: var(--space-2); }
.factory-chunk-list, .factory-conn-list { display: flex; gap: var(--space-2); flex-wrap: wrap; align-items: center; }
.factory-json-editor { font-family: var(--font-mono); font-size: var(--fs-ui-sm); background: var(--bg-subtle); padding: var(--space-3); border-radius: var(--radius-md); color: var(--text-primary); min-height: 120px; border: 1px solid var(--border-subtle); }
.factory-json-editor:focus-visible { outline: none; box-shadow: var(--focus-ring); background: var(--bg-surface); }
.factory-guardrails { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.factory-field-label { font-size: var(--fs-ui-sm); font-weight: 600; color: var(--text-primary); display: block; margin-bottom: var(--space-2); }
.factory-autonomy input[type="range"] { width: 100%; }
.factory-trigger-row { display: flex; flex-direction: column; gap: var(--space-2); }
.factory-trigger-row .input { font-family: var(--font-mono); max-width: 240px; padding: var(--space-2) var(--space-3); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); }

.factory-footer {
  padding: var(--space-3) var(--space-6);
  border-top: 1px solid var(--border-subtle);
  background: var(--bg-subtle);
  display: flex; justify-content: space-between; align-items: center;
}
.factory-validations { display: flex; gap: var(--space-2); }
```

**Estados.**

- Empty (nunca se creó un template):
```html
<main class="factory-editor">
  <div class="empty-state">
    <svg class="empty-state-icon"><use href="#i-anvil"/></svg>
    <h4 class="empty-state-title">Sin templates todavía</h4>
    <p class="empty-state-body">Los templates son las recetas que permiten instanciar agentes idénticos en 1 click. Creá el primero para tu org.</p>
    <button class="btn btn-primary">Crear primer template</button>
  </div>
</main>
```

- Loading (trayendo templates del catálogo):
```html
<div class="template-list" aria-busy="true">
  <div class="template-list-item"><span class="skeleton skeleton-text" style="width:70%"></span><span class="skeleton skeleton-text" style="width:40%"></span></div>
  <div class="template-list-item"><span class="skeleton skeleton-text" style="width:60%"></span><span class="skeleton skeleton-text" style="width:35%"></span></div>
  <div class="template-list-item"><span class="skeleton skeleton-text" style="width:80%"></span><span class="skeleton skeleton-text" style="width:40%"></span></div>
</div>
```

- Error (publicación falló):
```html
<footer class="factory-footer">
  <div class="factory-validations" role="alert">
    <span class="pill pill-error">Publicación fallida · JSON schema inválido</span>
  </div>
  <button class="btn btn-secondary btn-sm">Ver errores · 3</button>
</footer>
```

- Populated: snippet principal.

**Integración con tokens slice A.** `--bg-primary`, `--bg-surface`, `--bg-subtle`, `--border-subtle`, `--radius-md`, `--radius-sm`, `--radius-lg`, `--space-2/3/4/5/6`, `--fs-body`, `--fs-h4`, `--fs-ui-sm`, `--fs-caption`, `--font-display`, `--font-mono`, `--text-primary`, `--text-muted`, `--coral-primary`, `--coral-tint`, `--error`, `--focus-ring`, `--duration-fast`, `--ease-standard`. Usa `.tabs/.tab/.tab-count` (slice A §C.2.4), `.pill`/`.pill-xs` (§C.2.1), `.empty-state` (§C.2.7), `.skeleton` (§C.2.8), `.btn` variants.

**Trigger / keyboard shortcut.** Acceso via sidebar "Agent Factory" o hash `#/factory`. Atajo `Alt+F` abre la ruta. Dentro del editor: `Cmd+S` save draft, `Cmd+Shift+P` publish, `Cmd+D` deprecate (pide confirm), `Cmd+B` nuevo template. Flechas `↑/↓` navegan `template-list-item` cuando foco está en la sidebar.

**Acceptance criteria.**
- Layout 2-columnas con sidebar de templates (filtros drafts/beta/published/archived) + editor a la derecha.
- Metadata bar sticky con id mono, nombre editable, versión pill, categoría select, 3 acciones (Save draft / Publish new version / Deprecate).
- 6-7 secciones colapsables como `<details>` con resumen accesible: Base instructions, Embedded context, Output schema JSON, Guardrails (policies + autonomy ceiling), Connections required, Trigger word.
- Base instructions queda `readonly` cuando el template pasa a `published` — ver G.3 lifecycle reverted para alternativa fork.
- Slider autonomy L0-L5 con label dinámico ("L1 · Propone siempre").
- Trigger word input valida pattern `@[a-z]+`.
- Footer con validaciones `aria-live="polite"` y pills de OK/warnings/errors.
- Responsive: <1100px colapsa sidebar a topbar tabs, editor ocupa 100%.
- Solo visible con rol `owner` o `skill_publisher` — enforced en router (fuera del scope visual).

### G.7 · Skills Library (`#/skills`)

**Ubicación en la jerarquía.** Nueva ruta `#/skills` accesible desde sidebar en la misma sección "Creación" (bajo G.6 Factory o al mismo nivel dependiendo del rol). Visible a todos los usuarios con rol ≥ `operator`. Funciona como marketplace interno: catálogo de skills publicadas por FaberLoom + templates forkeados de la organización. Detalle por skill en ruta anidada `#/skills/:slug` con tabs `Overview · Spec · Changelog · Samples`.

**Wireframe estructural.** Top: page-header con título "Skills Library" + subline conteo, botón secondary "Publicar skill" (solo para publishers) y search input grande al centro. Debajo toolbar de filtros: chips de categoría (Ventas · Atención · Operaciones · Finanzas · Marketing · Datos · Todos) + chip de estado (Beta · Estable · Deprecated) + `sort` select. Cuerpo: grid responsive `auto-fill minmax(320px, 1fr)` de `skill-card`. Cada card: header con logo/inicial + nombre + publisher + pill de status, body con descripción (clamp 3 líneas) + meta row (autonomy ceiling indicator L1-L5 + versión + instalaciones count), footer con pill de categoría + CTA coral "Activar en mi org". La página de detalle `#/skills/:slug` usa tabs `.tabs` canónica (slice A §C.2.4) con 4 paneles.

**Snippet HTML + CSS pegable.**

```html
<section class="skills-library">
  <header class="page-header skills-header">
    <div>
      <h1 class="page-title">Skills Library</h1>
      <p class="page-subtitle">Catálogo de skills publicadas · 24 disponibles · 8 activas en tu org</p>
    </div>
    <div class="skills-header-right">
      <label class="skills-search">
        <svg class="ico" aria-hidden="true"><use href="#i-search"/></svg>
        <input type="search" placeholder="Buscar por nombre, publisher o categoría…" aria-label="Buscar skills">
        <span class="kbd" aria-hidden="true">/</span>
      </label>
      <button class="btn btn-secondary btn-sm">
        <svg class="ico-sm ico" aria-hidden="true"><use href="#i-plus"/></svg>Publicar skill
      </button>
    </div>
  </header>

  <div class="skills-filters">
    <div class="skills-filter-group" role="group" aria-label="Filtrar por categoría">
      <button class="filter-chip active" aria-pressed="true">Todas <span class="tab-count">24</span></button>
      <button class="filter-chip" aria-pressed="false">Ventas <span class="tab-count">7</span></button>
      <button class="filter-chip" aria-pressed="false">Atención <span class="tab-count">5</span></button>
      <button class="filter-chip" aria-pressed="false">Operaciones <span class="tab-count">4</span></button>
      <button class="filter-chip" aria-pressed="false">Finanzas <span class="tab-count">3</span></button>
      <button class="filter-chip" aria-pressed="false">Datos <span class="tab-count">5</span></button>
    </div>
    <div class="skills-filter-group">
      <select class="input" aria-label="Ordenar por">
        <option>Más usadas</option>
        <option>Más nuevas</option>
        <option>Mejor rating</option>
        <option>A-Z</option>
      </select>
    </div>
  </div>

  <div class="skills-grid">
    <article class="skill-card" tabindex="0" onclick="go('skills/cotizador-b2b-calzado')">
      <header class="skill-card-head">
        <div class="skill-logo" aria-hidden="true">C</div>
        <div class="skill-identity">
          <h3 class="skill-name">Cotizador B2B Calzado</h3>
          <div class="skill-publisher">muito.work · v1.2</div>
        </div>
        <span class="pill pill-success pill-xs">Estable</span>
      </header>
      <p class="skill-desc">Agente de cotización para distribuidores de calzado de seguridad industrial. Draft-first, aplica pricing policies y devuelve quote estructurado.</p>
      <div class="skill-meta-row">
        <span class="skill-autonomy" title="Autonomy ceiling L1 · Propone siempre">
          <span class="autonomy-dots" aria-label="L1 de L5">
            <span class="dot active"></span><span class="dot"></span><span class="dot"></span><span class="dot"></span><span class="dot"></span>
          </span>
          <span class="text-xs">L1 Propone</span>
        </span>
        <span class="skill-installs text-xs"><svg class="ico-xs ico" aria-hidden="true"><use href="#i-users"/></svg>128 orgs</span>
      </div>
      <footer class="skill-card-foot">
        <span class="pill pill-coral">Ventas B2B</span>
        <button class="btn btn-primary btn-sm" onclick="event.stopPropagation();activateSkill('cotizador-b2b-calzado')">
          Activar en mi org
        </button>
      </footer>
    </article>

    <article class="skill-card" tabindex="0">
      <header class="skill-card-head">
        <div class="skill-logo" aria-hidden="true">F</div>
        <div class="skill-identity">
          <h3 class="skill-name">Follow-up Cobranza LATAM</h3>
          <div class="skill-publisher">muito.work · v0.4 beta</div>
        </div>
        <span class="pill pill-warning pill-xs">Beta</span>
      </header>
      <p class="skill-desc">Secuencia multilingüe de cobranza para cuentas vencidas. Adapta tono por país (MX/CO/CR/BR) y respeta ventana legal por jurisdicción.</p>
      <div class="skill-meta-row">
        <span class="skill-autonomy">
          <span class="autonomy-dots"><span class="dot active"></span><span class="dot"></span><span class="dot"></span><span class="dot"></span><span class="dot"></span></span>
          <span class="text-xs">L1 Propone</span>
        </span>
        <span class="skill-installs text-xs"><svg class="ico-xs ico" aria-hidden="true"><use href="#i-users"/></svg>42 orgs</span>
      </div>
      <footer class="skill-card-foot">
        <span class="pill pill-coral">Finanzas</span>
        <button class="btn btn-primary btn-sm">Activar en mi org</button>
      </footer>
    </article>
  </div>
</section>

<!-- Página detalle: #/skills/:slug -->
<section class="skill-detail">
  <header class="page-header">
    <a href="#/skills" class="breadcrumb-back">← Skills Library</a>
    <div class="skill-detail-hero">
      <div class="skill-logo skill-logo-lg" aria-hidden="true">C</div>
      <div>
        <h1 class="page-title">Cotizador B2B Calzado</h1>
        <p class="page-subtitle">muito.work · v1.2 · publicado 2026-03-04 · 128 orgs activas</p>
      </div>
      <button class="btn btn-primary btn-lg">Activar en mi org</button>
    </div>
  </header>
  <nav class="tabs" role="tablist" aria-label="Información del skill">
    <button class="tab active" role="tab" aria-selected="true">Overview</button>
    <button class="tab" role="tab">Spec</button>
    <button class="tab" role="tab">Changelog</button>
    <button class="tab" role="tab">Samples</button>
  </nav>
  <!-- panel según tab -->
</section>
```

```css
.skills-header { display: flex; justify-content: space-between; align-items: flex-start; gap: var(--space-4); flex-wrap: wrap; }
.skills-header-right { display: flex; gap: var(--space-2); align-items: center; flex: 1; justify-content: flex-end; }
.skills-search {
  display: inline-flex; align-items: center; gap: var(--space-2);
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: var(--space-2) var(--space-3);
  min-width: 320px; max-width: 480px; flex: 1;
}
.skills-search input { flex: 1; border: none; background: none; font-size: var(--fs-ui); color: var(--text-primary); outline: none; }
.skills-search:focus-within { border-color: var(--coral-primary); box-shadow: var(--focus-ring); }

.skills-filters {
  display: flex; justify-content: space-between; align-items: center; gap: var(--space-3);
  margin: var(--space-4) 0 var(--space-6);
  flex-wrap: wrap;
}
.skills-filter-group { display: flex; gap: var(--space-2); flex-wrap: wrap; }

.skills-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: var(--space-4); }

.skill-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  display: flex; flex-direction: column; gap: var(--space-3);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-standard);
  outline: none;
}
.skill-card:hover { box-shadow: var(--shadow-md); border-color: var(--border-strong); transform: translateY(-1px); }
.skill-card:focus-visible { box-shadow: var(--focus-ring), var(--shadow-sm); }
@media (prefers-reduced-motion: reduce) { .skill-card:hover { transform: none; } }

.skill-card-head { display: flex; align-items: flex-start; gap: var(--space-3); }
.skill-logo {
  width: 40px; height: 40px; border-radius: var(--radius-md);
  background: var(--coral-tint); color: var(--coral-primary);
  font-family: var(--font-display); font-style: italic; font-size: 20px; font-weight: 500;
  display: inline-flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.skill-logo-lg { width: 64px; height: 64px; font-size: 32px; }
.skill-identity { flex: 1; min-width: 0; }
.skill-name { margin: 0; font-size: var(--fs-body); font-weight: 600; color: var(--text-primary); }
.skill-publisher { font-size: var(--fs-caption); color: var(--text-muted); margin-top: 2px; }

.skill-desc { margin: 0; font-size: var(--fs-ui-sm); line-height: 1.5; color: var(--text-secondary); display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; min-height: calc(1.5em * 3); }

.skill-meta-row { display: flex; justify-content: space-between; align-items: center; gap: var(--space-2); }
.skill-autonomy { display: inline-flex; align-items: center; gap: var(--space-2); color: var(--text-secondary); }
.autonomy-dots { display: inline-flex; gap: 3px; }
.autonomy-dots .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--bg-hover); }
.autonomy-dots .dot.active { background: var(--coral-primary); }
.skill-installs { display: inline-flex; align-items: center; gap: 4px; color: var(--text-muted); }

.skill-card-foot { display: flex; justify-content: space-between; align-items: center; gap: var(--space-2); padding-top: var(--space-2); border-top: 1px solid var(--border-subtle); }

.skill-detail-hero { display: flex; align-items: center; gap: var(--space-4); padding-top: var(--space-3); }
.breadcrumb-back { display: inline-block; font-size: var(--fs-ui-sm); color: var(--coral-text, var(--coral-primary)); text-decoration: none; margin-bottom: var(--space-2); }
.breadcrumb-back:hover { text-decoration: underline; text-underline-offset: 2px; }
```

**Estados.**

- Empty (catálogo sin skills o filtros devuelven 0):
```html
<div class="empty-state">
  <svg class="empty-state-icon"><use href="#i-puzzle"/></svg>
  <h4 class="empty-state-title">Sin skills para estos filtros</h4>
  <p class="empty-state-body">Probá limpiar filtros o publicá el primer skill de tu org desde Agent Factory.</p>
  <div style="display:flex;gap:var(--space-2)">
    <button class="btn btn-ghost btn-sm" onclick="clearSkillFilters()">Limpiar filtros</button>
    <button class="btn btn-primary btn-sm" onclick="go('factory')">Ir a Agent Factory</button>
  </div>
</div>
```

- Loading (trayendo catálogo):
```html
<div class="skills-grid" aria-busy="true">
  <div class="skill-card">
    <div style="display:flex;gap:var(--space-3)">
      <span class="skeleton" style="width:40px;height:40px;border-radius:8px"></span>
      <div style="flex:1"><span class="skeleton skeleton-text" style="width:70%"></span><span class="skeleton skeleton-text" style="width:40%"></span></div>
    </div>
    <span class="skeleton skeleton-text"></span>
    <span class="skeleton skeleton-text" style="width:85%"></span>
    <span class="skeleton skeleton-text" style="width:60%"></span>
  </div>
  <div class="skill-card">
    <div style="display:flex;gap:var(--space-3)">
      <span class="skeleton" style="width:40px;height:40px;border-radius:8px"></span>
      <div style="flex:1"><span class="skeleton skeleton-text" style="width:60%"></span><span class="skeleton skeleton-text" style="width:40%"></span></div>
    </div>
    <span class="skeleton skeleton-text"></span>
    <span class="skeleton skeleton-text" style="width:75%"></span>
  </div>
</div>
```

- Error (catálogo no disponible):
```html
<div class="empty-state">
  <svg class="empty-state-icon" style="color:var(--error)"><use href="#i-alert"/></svg>
  <h4 class="empty-state-title">No pude cargar el catálogo</h4>
  <p class="empty-state-body">La Skills Library no responde. Tus skills activas siguen funcionando normalmente.</p>
  <button class="btn btn-secondary btn-sm" onclick="retrySkillsLoad()">Reintentar</button>
</div>
```

- Populated: snippet principal.

**Integración con tokens slice A.** `--bg-surface`, `--bg-hover`, `--border-subtle`, `--border-strong`, `--radius-md`, `--radius-lg`, `--shadow-sm`, `--shadow-md`, `--space-2/3/4/6`, `--fs-body`, `--fs-ui`, `--fs-ui-sm`, `--fs-caption`, `--font-display`, `--text-primary`, `--text-secondary`, `--text-muted`, `--coral-primary`, `--coral-tint`, `--coral-text`, `--focus-ring`, `--duration-fast`, `--ease-standard`. Reutiliza `.tabs/.tab/.tab-count` (§C.2.4), `.pill`/`.pill-xs` (§C.2.1), `.filter-chip[aria-pressed]` (addendum), `.empty-state`/`.skeleton` (§C.2.7/8).

**Trigger / keyboard shortcut.** Acceso via sidebar "Skills Library" o `#/skills`. Atajo global `Alt+K` (Katalog) abre la ruta. Dentro: `/` foco al search (patrón GitHub), `←/→` navega entre cards del grid, `Enter` abre detalle, `A` activa skill seleccionado. En página detalle: `1-4` cambia tab (Overview/Spec/Changelog/Samples), `Esc` vuelve al catálogo.

**Acceptance criteria.**
- Grid responsive `auto-fill minmax(320px, 1fr)` con 2-4 columnas según viewport.
- Cada `.skill-card` con header (logo + nombre + publisher + pill status), descripción clamp 3 líneas, meta row con autonomy-dots (L0-L5 con `.active` por nivel) + installs count, footer con pill categoría + CTA "Activar".
- Cards focusable via `tabindex="0"`, `Enter` navega al detalle; click en CTA usa `stopPropagation()` para activar sin navegar.
- Search input con atajo `/` para foco; filter chips toggles con `aria-pressed` (no radio group — múltiples filtros combinan).
- Página detalle con 4 tabs (Overview · Spec · Changelog · Samples); Spec linkea al template de Agent Factory (G.6) si el usuario tiene permisos.
- Estado "beta"/"deprecated" en pill + warning en CTA de activar ("Activar beta · sin SLA").
- Empty state diferenciado por "sin resultados con filtros" vs "catálogo vacío".
- Loading con skeletons que preservan altura de card para evitar layout shift.
- Funciona con `prefers-reduced-motion`: desactiva hover translateY.

---

## Sección H — Roadmap priorizado consolidado

Fórmula: `Score = Impact × (6 − Effort)`. Rango 1-25. Top 10 quick wins (score ≥16), 11-20 structural (11-15), 21-35+ polish (≤10).

**Top 10 · Quick wins (score ≥16)**

| # | Hallazgo | Pantalla / Sección | Severity | Impact | Effort | Score | Fuente | Snippet ref |
|---|---|---|---|---|---|---|---|---|
| 1 | Token `--evidence` dark (2.66:1) rompe AA — color signature del producto, fix 1 línea | Sistema · tokens dark | S1 | 5 | 1 | 25 | Slice A | `AUDIT_A §E.2 / §E.3` |
| 2 | `--text-muted` dark (3.88:1) falla body en captions, timestamps, metas en 30+ lugares | Sistema · tokens dark | S1 | 5 | 1 | 25 | Slice A | `AUDIT_A §E.2 / §E.3` |
| 3 | `--ico { stroke-width: 2 }` contradice brand memo (1.5) — 30+ íconos | Sistema · iconografía | S1 | 4 | 1 | 20 | Slice A | `AUDIT_A §C.3` |
| 4 | `prefers-reduced-motion` no respetado — bloqueo WCAG 2.3.3 | Sistema · a11y | S1 | 4 | 1 | 20 | Slice A | `AUDIT_A §C.6` |
| 5 | `focus-visible` ausente global (solo inputs) — fail WCAG 2.4.7 | Sistema · a11y | S1 | 5 | 2 | 20 | Slice A | `AUDIT_A §E.3` |
| 6 | Empty/Loading/Error states no existen (cero `.empty-state`, `.skeleton`) | Sistema · estados | S1 | 5 | 2 | 20 | Slice A | `AUDIT_A §C.2.7 / §C.2.8` |
| 7 | `--border-subtle` dark (1.30:1 surface) pierde siluetas de cards | Sistema · tokens dark | S2 | 4 | 1 | 20 | Slice A | `AUDIT_A §E.2 / §E.3` |
| 8 | `--error` dark (3.13:1) falla body — usado en admin-banner, priority-high | Sistema · tokens dark | S1 | 4 | 1 | 20 | Slice A | `AUDIT_A §E.3` |
| 9 | Landing: `onclick` sin `href` ni `tabindex` en nav/footer — fail WCAG 2.1.1 | Ruta 1 landing | S1 | 4 | 1 | 20 | Slice B1 | `AUDIT_B1 Ruta 1 a11y` |
| 10 | Dashboard: filas clickables (`activity-item`, `agent-mini-row`) sin role/keyboard — fail 2.1.1 | Ruta 2 dashboard | S1 | 4 | 1 | 20 | Slice B1 | `AUDIT_B1 Ruta 2 a11y` |

**11-20 · Quick wins continuación (score ≥16)**

| # | Hallazgo | Pantalla / Sección | Severity | Impact | Effort | Score | Fuente | Snippet ref |
|---|---|---|---|---|---|---|---|---|
| 11 | Pipeline-bar agentes con `<div onclick>` sin `role=tab`/`aria-selected` | Ruta 7 agentes | S1 | 4 | 1 | 20 | Slice B1 | `AUDIT_B1 Ruta 7 snippets` |
| 12 | `aria-hidden="true"` faltante en ~30 SVG decorativos — SR lee "imagen" | Sistema · a11y | S1 | 4 | 1 | 20 | Slice B1-B3 | `AUDIT_B1 Ruta 1 a11y` · `pendiente de C` |
| 13 | Console actions: Rechazar junto a Aprobar mismo peso visual — riesgo mis-click | Ruta 8 console | S1 | 4 | 1 | 20 | Slice B2 | `AUDIT_B2 Ruta 8 snippets` |
| 14 | Learning Thermometer widget — bloqueante del pitch de memoria | Overlay global | S1 | 5 | 2 | 20 | G.1 | `ver Sección G.1` |
| 15 | Tokens spacing/radius/typography sin nombrar (60+ literales) | Sistema · tokens | S1 | 4 | 2 | 16 | Slice A | `AUDIT_A §C.1 / §C.4 / §C.5` |
| 16 | Bandeja: `.bandeja-tabs` custom paralelo a `.tabs` canónico + icon-btn redundante | Ruta 3 bandeja | S1 | 4 | 2 | 16 | Slice B1 | `AUDIT_B1 Ruta 3 snippets` |
| 17 | Agentes: faltan 4 estados Autonomy Ladder (Activo/Aprendiendo/Esperando/Pausado) | Ruta 7 agentes | S1 | 4 | 2 | 16 | Slice B1 | `AUDIT_B1 Ruta 7 snippets` |
| 18 | Admin: 10 tabs sin wayfinding por sección Plataforma/Seguridad/Gobernanza | Ruta 13b admin | S1 | 4 | 2 | 16 | Slice B3 | `AUDIT_B3 Ruta 13b snippets` |
| 19 | ⌘K sin focus trap — escapa a página detrás, fail WCAG 2.4.3 | Task launcher | S1 | 4 | 2 | 16 | Slice B3 | `AUDIT_B3 Task launcher snippets` |
| 20 | Danger zone sin diferenciación visual + `prompt()` nativo para destroy | Ruta 13b admin/danger | S1 | 4 | 2 | 16 | Slice B3 | `AUDIT_B3 Ruta 13b snippets` |

**21-30 · Structural (score 11-15)**

| # | Hallazgo | Pantalla / Sección | Severity | Impact | Effort | Score | Fuente | Snippet ref |
|---|---|---|---|---|---|---|---|---|
| 21 | Settings: toggles sin `<input type=checkbox>` real — no keyboard, no form-submittable | Ruta 13a settings | S1 | 4 | 2 | 16 | Slice B3 | `AUDIT_B3 Ruta 13a snippets` |
| 22 | Learned rules: propuestas mezcladas con activas sin jerarquía | Ruta 9 studio | S1 | 4 | 2 | 16 | Slice B2 | `AUDIT_B2 Ruta 9 snippets` |
| 23 | Lifecycle actions por artefacto (Edit/Version/Revert/Suspend/Archive) | Skill Studio + Deliverable + KB | S2 | 4 | 2 | 16 | G.3 | `ver Sección G.3` |
| 24 | Cero `@media` queries en 5801 líneas — colapsa bajo 1280px | Sistema · responsive | S1 | 5 | 3 | 15 | Slice A | `AUDIT_A §A scorecard dim 8` |
| 25 | Bandeja tabs: tabs `<div>` sin `role=tab`/`aria-selected`/`aria-controls` | Ruta 3 bandeja | S1 | 3 | 1 | 15 | Slice B1 | `AUDIT_B1 Ruta 3 a11y` |
| 26 | Alertas: severity literal "warning/error/info" inglés-técnico mostrado al usuario | Ruta 5 alertas | S1 | 3 | 1 | 15 | Slice B1 | `AUDIT_B1 Ruta 5 light` |
| 27 | Admin banner sin `position: sticky` — pierde contexto de modo destructivo | Ruta 13b admin | S1 | 3 | 1 | 15 | Slice B3 | `AUDIT_B3 Ruta 13b light` |
| 28 | Deliverable: 2 `<h1>` en la misma vista (page + reporte) rompe jerarquía | Ruta 10 deliverable | S1 | 3 | 1 | 15 | Slice B3 | `AUDIT_B3 Ruta 10 a11y` |
| 29 | Conexiones: banner solo primer error hardcoded — no loopea errored[] | Ruta 12 conexiones | S1 | 3 | 1 | 15 | Slice B3 | `AUDIT_B3 Ruta 12 snippets` |
| 30 | Settings nav con `<div onclick>` — no `<a>` ni role/aria-current | Ruta 13a settings | S1 | 3 | 1 | 15 | Slice B3 | `AUDIT_B3 Ruta 13a snippets` |

**31-45 · Structural continuación + polish (score ≤15)**

| # | Hallazgo | Pantalla / Sección | Severity | Impact | Effort | Score | Fuente | Snippet ref |
|---|---|---|---|---|---|---|---|---|
| 31 | Agent status en console: `pill-coral pill-dot` único para todos — pierde 4 estados | Ruta 8 console | S1 | 3 | 1 | 15 | Slice B2 | `AUDIT_B2 Ruta 8 snippets` |
| 32 | Confidence ring sin `role=img` ni aria-label — indicador invisible a SR | Ruta 8 + 10 | S1 | 3 | 1 | 15 | Slice B2/B3 | `AUDIT_B2 Ruta 8 a11y` |
| 33 | Skill Studio: 3 capas Base/Manual/Learned sin diferenciación visual radical | Ruta 9 studio | S1 | 4 | 3 | 12 | Slice B2 | `AUDIT_B2 Ruta 9 snippets` |
| 34 | Fork Zone usa `alert()` — debería ser modal con MFA + doble check | Ruta 9 studio | S1 | 3 | 2 | 12 | Slice B2 | `AUDIT_B2 Ruta 9 fork modal` |
| 35 | Agent card: clickable parent con 2 botones internos — viola HTML nested | Ruta 7 agentes | S1 | 3 | 2 | 12 | Slice B1 | `AUDIT_B1 Ruta 7 a11y` |
| 36 | Audit log tabla: `<div>` styled como tabla — sin `<thead>`/`scope` | Ruta 13a+13b | S2 | 3 | 2 | 12 | Slice B3 | `AUDIT_B3 Ruta 13a light` |
| 37 | Sistema: `.toast` no existe — feedback post-acción inexistente | Sistema · patterns | S2 | 3 | 2 | 12 | Slice A | `AUDIT_A §C.2.9` |
| 38 | Tab "Todo": concatenación 3 renders con filtros heredados — estado inconsistente | Ruta 6 todo | S1 | 3 | 2 | 12 | Slice B1 | `AUDIT_B1 Ruta 6 snippets` |
| 39 | Workflows: publicar sin diff ni checklist tests — riesgo real v2.4→v2.5 | Ruta 11 workflows | S2 | 4 | 3 | 12 | Slice B3 | `AUDIT_B3 Ruta 11 light` |
| 40 | Workflows: canvas 1400×820 hard-coded sin scroll/zoom | Ruta 11 workflows | S1 | 4 | 3 | 12 | Slice B3 | `AUDIT_B3 Ruta 11 snippets` |
| 41 | Modal consolidación con ejes Tipo/Alcance/Propagación + 4 acciones | Overlay global | S2 | 3 | 2 | 12 | G.2 | `ver Sección G.2` |
| 42 | Landing: botones pricing con `style="width:100%"` ×3 — falta `.btn-block` | Ruta 1 landing | S2 | 2 | 1 | 10 | Slice B1 | `AUDIT_B1 Ruta 1 light` |
| 43 | Dashboard: saludo "Buenas tardes, Álvaro" hardcoded — sin hora dinámica | Ruta 2 dashboard | S1 | 2 | 1 | 10 | Slice B1 | `AUDIT_B1 Ruta 2 light` |
| 44 | Bandeja: empty state inline `<div>` — no usa `.empty-state` canónico | Ruta 3 bandeja | S2 | 2 | 1 | 10 | Slice B1 | `AUDIT_B1 Ruta 3 light` |
| 45 | Bandeja/entregables: cita request truncada doble (JS 120ch + CSS clamp) | Ruta 4 entregables | S1 | 2 | 1 | 10 | Slice B1 | `AUDIT_B1 Ruta 4 light` |

**46-60 · Polish + deudas nuevas features (score ≤10)**

| # | Hallazgo | Pantalla / Sección | Severity | Impact | Effort | Score | Fuente | Snippet ref |
|---|---|---|---|---|---|---|---|---|
| 46 | Conexiones: `conn-tile-logo` solo inicial — falta logo oficial Gmail/HubSpot/Amazon | Ruta 12 conexiones | S1 | 2 | 1 | 10 | Slice B3 | `AUDIT_B3 Ruta 12 light` |
| 47 | Deliverable: botones aside sin `aria-label` + svg sin `aria-hidden` | Ruta 10 deliverable | S2 | 2 | 1 | 10 | Slice B3 | `AUDIT_B3 Ruta 10 a11y` |
| 48 | Admin keys: botones `↻` y `✕` unicode sin `aria-label` | Ruta 13b admin | S3 | 2 | 1 | 10 | Slice B3 | `AUDIT_B3 Ruta 13b a11y` |
| 49 | Workflows: `wf-workflow-name` input sin label visible ni auto-save | Ruta 11 workflows | S2 | 2 | 1 | 10 | Slice B3 | `AUDIT_B3 Ruta 11 snippets` |
| 50 | Theme toggle sin indicador de estado activo visible | Sistema · topbar | S2 | 2 | 1 | 10 | Slice A | `AUDIT_A §E.2 / §E.3` |
| 51 | i18n: cero `STRINGS` table — literales ES en todo el JS, bloquea PT-BR/EN | Sistema · i18n | S1 | 5 | 4 | 10 | Slice B1-B3 | `AUDIT_B1 Ruta 1 i18n` · `pendiente de C` |
| 52 | Agent Console: falta estructura 4 tabs (Consola/Tareas/Usuarios/Flujos) | Ruta 8 console | S1 | 5 | 4 | 10 | Slice B2 | `AUDIT_B2 Ruta 8 snippets` |
| 53 | Modal de Consolidación — loop de aprendizaje curado completo | Overlay global | S1 | 5 | 4 | 10 | G.2 | `ver Sección G.2` |
| 54 | Settings/Admin: formularios sin `<form>` ni batch save — 5 cambios sin feedback | Ruta 13a settings | S3 | 3 | 3 | 9 | Slice B3 | `AUDIT_B3 Ruta 13a light` |
| 55 | Workflows: paleta items `draggable=true` sin alternativa keyboard | Ruta 11 workflows | S2 | 3 | 3 | 9 | Slice B3 | `AUDIT_B3 Ruta 11 a11y` |
| 56 | Evidence drawer: links claim→evidence vía superíndice no existen | Ruta 8 console | S2 | 3 | 3 | 9 | Slice B2 | `AUDIT_B2 Ruta 8 a11y` |
| 57 | Version history viewer — audit + rollback por artefacto | Modal overlay | S2 | 3 | 3 | 9 | G.4 | `ver Sección G.4` |
| 58 | Shadow memory panel — infra para ver qué no se indexó | Skill Studio 4ta col | S2 | 3 | 3 | 9 | G.5 | `ver Sección G.5` |
| 59 | Skills Library `#/skills` — marketplace interno inexistente | Nueva ruta | S2 | 4 | 4 | 8 | G.7 | `ver Sección G.7` |
| 60 | Agent Factory `#/factory` — creación de templates inexistente | Nueva ruta | S2 | 4 | 5 | 4 | G.6 | `ver Sección G.6` |

---

## Sección I — Deuda no urgente

Ítems identificados durante la auditoría que no bloquean release ni degradan percepción de calidad de forma crítica. Se difieren a ciclos de polish (sprint T+2 o posterior) o se absorben cuando se toque el componente afectado por otra razón. Sin snippets por decisión explícita — la implementación es mecánica una vez priorizada.

- `wordmark` varía en `font-size` entre landing (22px hero), header app (18px) y footer (14px): faltan tokens `--fs-wordmark-hero/-app/-footer` o, alternativa, unificar en 3 clases `.wordmark-lg/-md/-sm` con ratio 1.5× entre escalones; hoy hay valores duros en 6 lugares que derivan en inconsistencia de tracking.
- `font-size: 17px` off-scale aparece en `.conn-tile-name` y en `.wf-node-label`: ninguno está en la escala tipográfica de Slice A (12/13/14/15/16/18/20/24). Subir a 18 (`--fs-body`) o bajar a 16 (`--fs-body`) — decisión estética menor pero requiere un roundtrip de diseño.
- Tokens `--font-display`, `--font-ui`, `--font-mono` existen pero se aplican de forma inconsistente: hay 14 usos de `font-family: "Inter"` hardcoded que deberían migrar a `var(--font-ui)`. No rompe nada hoy porque `--font-ui` es Inter, pero bloquea cambio global de familia.
- Falta variante `--border-coral-strong` en tokens: hoy se usa `border: 2px solid var(--coral-primary)` con valor hard en 4 componentes (`.agent-card[data-state="active"]`, `.task-chip-selected`, `.gold-pill-active`, `.skill-card-featured`). Agregar token ahorra 4 sitios a mantener.
- Componente `.section-header` propuesto en Slice A no está implementado aún: hoy cada ruta tiene su propio `h2 + .subtitle + divider` con microvariaciones (margin-bottom 8px vs 12px, gap 4px vs 6px). Componetizar reduce ~120 líneas de CSS.
- `.progressbar` no es canónico: hay 3 implementaciones distintas (Dashboard KPI, Learning Thermometer latente, Skill mastery bar en console). Unificar en `.fl-progressbar` con `data-variant="linear|radial|stepped"`.
- Helper `severityLabel(s1|s2|s3)` para renderizar pill de severidad con color + label + icono no existe: hoy hay 6 lugares con ternarios inline. Extraer a función pura de ~10 líneas.
- Shadow rim-light (`inset 0 1px 0 rgba(255,255,255,0.04)`) en modo dark aparece solo en 3 de los ~18 cards que lo pedirían por elevación. No rompe el dark, pero el contraste entre cards con y sin rim se nota side-by-side.
- Íconos `i-puzzle` y `i-anvil` usan `fill` mientras el resto del set usa `stroke` con `stroke-width: 1.5`: inconsistencia visual menor en el sidebar. Rehacer en 2 pasos en Figma + export SVG.
- `i-sparkle` tiene 11 paths innecesarios (hecho en Illustrator sin simplificar): pasar por SVGO o rehacer con 4 paths. Impacto: -2.3KB en bundle inicial.
- Faltan íconos `i-quote-mark` (para testimonios de evidencia en Learning Thermometer modal) y `i-annotation` (para notas en gold samples): hoy se sustituye con emoji `"` y `"`. Encargar a diseño.
- `--coral-tint` en dark mode está a `rgba(255, 122, 100, 0.12)` — contraste insuficiente sobre `--bg-surface` dark. Subir a `0.22` o crear `--coral-tint-dark` específico.
- Regla `.theme-toggle.active` no existe explícitamente: el toggle de tema funciona por toggle de `data-theme` en `<html>` pero el botón mismo no tiene estado visual de "tema actualmente aplicado". Agregar `[aria-pressed="true"]` styling.
- Token `--link-ul-offset` (distancia del underline al baseline en links) no existe: hoy `text-underline-offset: 3px` hardcoded en 8 lugares. Tokenizar.
- Componente `.sep` (separador vertical entre metadata inline) tiene 2 variantes: unas con `color: var(--text-muted)` y otras con `opacity: 0.4`. Canonicalizar a una sola regla.
- `--fs-micro-caps` (12px, letter-spacing 0.08em, text-transform uppercase) lo usan los headers de feed-buckets en Bandeja pero no está tokenizado: hoy se replica en 4 lugares con valores duros.
- Estado activo de `.wf-connection` (línea entre nodos de workflow) no tiene visual distintivo cuando la ejecución está pasando por esa arista: oportunidad de animación `stroke-dasharray` sutil pero no bloquea.
- `.conn-tile-scopes` truncan con `text-overflow: ellipsis` a 1 línea pero algunos scopes pasan de 45 chars y el tooltip no los expone; agregar `title` attribute o popover on-hover.
- `hero-eyebrow` en landing desborda en PT-BR ("Controle. Memória. Escala." → 32 chars) porque tiene `max-width: 28ch`: subir a `34ch` o permitir wrap en 2 líneas.
- Dashboard `dash-grid` tiene ratio asimétrico 2fr/1fr/1fr/1fr que genera columna izquierda ~dos veces el ancho: funciona pero algunos KPIs quedan muy anchos; revisar si 1.4fr/1fr/1fr/1fr mejora lectura.
- `.chip-active` en tabs de Bandeja usa `background: var(--coral-tint)` pero sobre `--bg-subtle` en light el contraste es muy bajo (4.1:1 vs 4.5 requerido para UI). Agregar capa de `box-shadow: inset 0 0 0 1px var(--coral-primary)` como refuerzo.
- `.agent-icon-lg` en sidebar no muestra tooltip con `trigger_word` del agente: útil cuando el usuario invoca por ⌘K y olvida el comando. Tooltip en hover 600ms.
- CopyBot (agente demo de onboarding) no tiene showcase en Skills Library aunque es el mejor ejemplo de "skill lista para usar": agregar como primer item destacado en `#/skills` una vez G.7 exista.
- Admin tabs tienen naming inconsistente EN/ES (`Users` vs `Usuarios`, `Audit` vs `Auditoría`, `Policies` vs `Políticas`): consolidar en ES dado que el producto es ES-first.
- Audit log en Admin necesita virtualización a partir de 50 eventos: hoy renderiza todo el DOM y con 200+ entries (proyectado producción) causa lag perceptible en scroll. React-window o IntersectionObserver manual.
- Keyboard shortcut `⌘K` no aparece documentado en UI (ni en landing ni en empty state de dashboard): agregar hint discreto `⌘K para buscar` en topbar.
- `prefers-reduced-motion` está respetado en Learning Thermometer, modales y toasts, pero falta revisar `.agent-card:hover` (scale 1.02), transiciones de tab y animaciones de `stroke-dashoffset` en workflow connections.
- Focus ring en dark mode sobre `--bg-overlay` tiene contraste marginal (3.2:1): subir `--focus-ring` dark a amarillo más saturado o añadir outline doble.
- Landing hero no tiene `og:image` ni `twitter:card` definidos en `<head>`: SEO y preview social degradados. Producir asset 1200×630.
- Footer `copyright` año está hardcoded `2026`: cambiar a `<script>document.getElementById('y').textContent = new Date().getFullYear()</script>` o equivalente server-side.
- `lang="en"` en `<html>` pero el contenido es ES: cambiar a `lang="es"` para lectores de pantalla y SEO.
- Skip-link `<a href="#main">Skip to content</a>` no existe: a11y básico faltante para teclado-only.
- Heading hierarchy en Skill Studio salta de `h2` a `h4` en panel derecho (sin `h3` intermedio): reordenar semántica sin cambiar visual.
- `aria-label` faltante en 7 íconos-botón en topbar (theme-toggle, command-palette-trigger, notifications-bell, user-menu, help, status-light, org-switcher): añadir labels traducidos.
- Color de fondo de `code` inline en prosa no tiene token dedicado (`--bg-code` sugerido): hoy usa `rgba(0,0,0,0.04)` duro que no se adapta a dark.
- `<kbd>` styling es inconsistente entre ⌘K modal y documentación inline en empty states: canonicalizar a un solo set de reglas.
- Scrollbar styling custom existe solo en Webkit (`::-webkit-scrollbar`); Firefox queda con scrollbar nativo. Añadir `scrollbar-color` + `scrollbar-width`.
- Timezone de timestamps en feed está hardcoded a `America/Argentina/Buenos_Aires`: respetar `Intl.DateTimeFormat()` del navegador o preferencia de usuario en settings.
- Formato de números grandes (`1,234` vs `1.234`) inconsistente entre Dashboard KPIs y Analytics tab: usar `Intl.NumberFormat(navigator.language)` en todos lados.
- `meta name="description"` de landing es genérico ("FaberLoom"): reescribir con wedge cotización B2B calzado seguridad en ≤160 chars.
- Favicon es el default de Vite: exportar isotipo Dir A woven lattice 32×32 + 16×16 + 180×180 apple-touch-icon.
- `<title>` de cada ruta es estático (`FaberLoom`): actualizar dinámicamente por ruta (`Bandeja · FaberLoom`, `Skill Studio · FaberLoom`).
- Tooltip positioning library no existe: hoy `title` attribute nativo es el único mecanismo. Adoptar Floating UI o equivalente cuando se pase de 10 usos.
- Toast stacking no está probado con 5+ toasts simultáneos: verificar que no se salgan del viewport ni bloqueen UI crítica.
- Modal backdrop tiene `backdrop-filter: blur(8px)` que en Safari móvil causa jank: añadir `@supports` fallback o reducir blur.
- `copy-to-clipboard` en gold samples no tiene confirmación visual (toast): feedback silencioso desanima uso. Toast inline 2s.
