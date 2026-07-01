# AUDIT_B3 — Screens 10-13 + ⌘K

## Ruta 10 — `#/deliverable/:id`

### Wireframe

Página de detalle de entregable con header (título Georgia italic + subline con agente y pill "Listo para revisar" + botón volver), cuerpo dividido en dos columnas: `deliverable-main` con el reporte o tabla (`<h1>`, `<h2>`, tablas con clases `pct-high/mid/low`, lista de recomendaciones, footer italic de firma SHA-256) y `deliverable-aside` con cinco tarjetas apiladas: Request original (quote italic), Evidencia (3 `ctx-item`), Confianza (anillo 48px + método), Acciones (4 botones full-width), y Audit (metadata). Sin estado empty — si `MOCK.deliverables.find()` falla el fallback es el primer mock. No hay breadcrumb funcional a la versión anterior ni link a workflow que lo generó.

### Light

- [S1] No existe volver atrás por teclado ni atajo — el único affordance es el botón "← Bandeja" con `onclick="go('bandeja/entregables')"`. Un revisor que abre varios entregables no puede hacer `Alt+←` porque el hash-routing no registra historia. **Línea ~5147.** Fix: usar `history.pushState` en `go()` y añadir atajo `Esc` que regrese a bandeja mientras no haya foco en input.
- [S1] Botón "Aceptar & archivar" usa `alert()` con string inline y no muestra estado post-acción (el entregable queda visualmente igual). El revisor no sabe si la firma se registró o si el audit captó el evento. **Línea ~5124.** Fix: reemplazar por toast `toast-evidence` (slice A C.2 pattern 9) con el SHA y link al evento de audit, y aplicar clase `.card--approved` al `.deliverable-main` para deshabilitar los botones de acción.
- [S1] El `<p>` italic de firma (línea ~5213) usa `border-radius: 4px` literal y `border-left:3px solid var(--coral-primary)` — debería ser `var(--evidence)` porque es el sello forense del deliverable, no una marca de brand. El color de provenance (slice A) existe justamente para esto. **Línea ~5213.** Fix: reemplazar por `var(--evidence)` + token `var(--radius-sm)`.
- [S2] Las acciones laterales mezclan jerarquías: "Aceptar & archivar" (primary), "Pedir ajuste" y "Convertir en draft saliente" (ambos secondary) — la conversión a draft saliente es una acción destructiva de contexto (sale del scope deliverable y crea nuevo flow) y debería ir separada con divisor y microcopy "Otras acciones". **Líneas ~5124-5129.** Fix: agrupar Aceptar+Pedir ajuste arriba, divisor `border-top: 1px solid var(--border-subtle)`, debajo "Convertir en draft" y "Exportar".
- [S2] `deliverable-meta-bar` usa separadores `·` como `<span>·</span>` entre campos con `<strong>` — en responsive angosto se corta con salto duro. **Línea ~5162-5167.** Fix: `display:flex;flex-wrap:wrap;gap:var(--space-2)` y eliminar separadores manuales, usar `border-left` en cada item.

### Dark

- [S1] `<p>` de firma usa `background:var(--bg-subtle)` + `color:var(--text-muted)` (slice A). En dark `--text-muted` sobre `--bg-subtle` (#8A8278 sobre #34312C) cae a ~3.9:1 y el tamaño es 12px italic — falla AA body. **Línea ~5213.** Fix: usar `--text-secondary` endurecido (slice A) o subir a `--text-muted` corregido `#A49C90` (slice A).
- [S2] Tabla del reporte no tiene estilos de `thead` en dark (hereda `bg-subtle`) pero las celdas con `pct-high` (verde salvia) y `pct-mid` (ámbar) no tienen reglas dark-aware — si se usan tokens `--success`/`--warning` sin corrección dan borderline. **Líneas ~5175-5196.** Fix: usar `--success` corregido `#9BAD8C` y `--warning` corregido `#E0B47A` del slice A.
- [S2] `border-left` en `<p>` de firma es `var(--coral-primary)` (#C96442) — en dark sobre `--bg-subtle` el delta coral-vs-surface es el mismo (coral no cambia hex), pero la barra de 3px pierde presencia visual porque dark surface es warmer. Considerar usar `var(--border-coral)` (slice A) que en dark es `#D97757` y se ve con más separación.

### i18n

- Hard-coded:
  - "Período:", "Método:", "Versión:" como strings literales dentro de `deliverableReport()` — **líneas ~5163-5167**.
  - "Clientes analizados: Distribuidora Seguridad del Norte", "SKUs: 8", "Período: Q1 2026" — **líneas ~5221-5225**.
  - "Generado por agente Forecast v1.1 · 2026-04-18 10:35 · Confidence 88% · SHA-256 a3f8…c921" — **línea ~5214** (formato de fecha en español mezclado con label inglés "Confidence").
  - "Listo para revisar" dentro del pill **línea ~5145**.
  - "Retención: 7 años (SOC2)" **línea ~5136**.
- Overflow: "Convertir en draft saliente" en aside de 280px ya está al límite en ES. En PT-BR "Converter em rascunho de saída" (27ch) o DE "In ausgehenden Entwurf umwandeln" (35ch) rompe — el botón usa `width:100%` pero la línea parte con wrap feo. **Línea ~5128.**

### a11y

- [S1] `<h1 class="page-title" style="font-family:Georgia;font-style:italic">` dentro del `page-header` es el único `<h1>`, pero el reporte interno también usa `<h1>` (línea ~5169, ~5219) — dos `<h1>` por vista rompe jerarquía semántica para SR. **Líneas ~5144 + ~5169.** Fix: el de `deliverableReport` debe ser `<h2>` y el `<h1>` queda sólo en page-header.
- [S1] Botones del aside no tienen `aria-label` explícito y los que llevan ícono inline (ej. `<svg class="ico-sm ico">`) no tienen `aria-hidden="true"` — lectores de pantalla leen "imagen Aceptar & archivar". **Líneas ~5124-5128.** Fix: añadir `aria-hidden="true"` en svg y `aria-label` en botón si el ícono es único.
- [S2] La tabla (`<table>`) no tiene `<caption>` ni `scope="col"` en `<th>` — datos forenses deben ser navegables por header. **Líneas ~5173-5196.** Fix: añadir `<caption class="sr-only">Proyección mensual Q2 2026</caption>` y `scope="col"` en cada `<th>`.
- [S3] Confidence ring (`confidenceRing(d.confidence, 48)`) es SVG sin `role="img"` + `aria-label`. Un revisor ciego no sabe que "88% confianza" está graficado. **Línea ~5115.** Fix: envolver con `<div role="img" aria-label="Confianza 88% · evidencia más método más volumen">`.

### Snippets

```html
<!-- S1: deliverable firmado, con estado aprobado + toast-evidence -->
<article class="deliverable-main card-evidence" data-state="pending">
  <!-- ... reporte ... -->
  <p class="deliverable-signature">
    Generado por agente Forecast v1.1 · 2026-04-18 10:35 · Confianza 88% · SHA-256 a3f8…c921
  </p>
</article>
```

```css
.deliverable-signature {
  margin-top: var(--space-6);
  padding: var(--space-3) var(--space-4);
  background: var(--bg-subtle);
  border-left: 3px solid var(--evidence); /* slice A — forense, no brand */
  border-radius: var(--radius-sm);
  font-size: var(--fs-caption);
  color: var(--text-secondary); /* slice A — endurecido, pasa AA dark */
  font-style: italic;
  font-family: var(--font-mono);
}
/* Estado aprobado: desactivar acciones + toast */
.deliverable-main[data-state="approved"] .btn-primary,
.deliverable-main[data-state="approved"] .btn-secondary { opacity: .5; pointer-events: none; }
```

```html
<!-- S1: CTA group con jerarquía clara y aria -->
<div class="studio-aside-card">
  <div class="studio-aside-title">Acciones</div>
  <div class="action-group action-group-primary">
    <button class="btn btn-primary btn-sm" aria-label="Aceptar y archivar deliverable">
      <svg class="ico-sm ico" aria-hidden="true"><use href="#i-check"/></svg>
      Aceptar y archivar
    </button>
    <button class="btn btn-secondary btn-sm">Pedir ajuste</button>
  </div>
  <hr class="action-divider">
  <div class="action-group action-group-secondary">
    <button class="btn btn-secondary btn-sm">Convertir en draft saliente</button>
    <button class="btn btn-ghost btn-sm">Exportar</button>
  </div>
</div>
```

---

## Ruta 11 — `#/workflows`

### Wireframe

Canvas builder de workflows a tres columnas: toolbar top (nombre editable tipo input + pill "Live · v2.4" + 4 botones Versiones/Simular/Guardar draft/Publicar), paleta izquierda (`wf-palette` con 6 categorías: Triggers, Agentes, Políticas, Aprobación, Acciones, Outputs — cada item con `border-left-color` por tipo y dot), canvas central (`wf-canvas` de 1400×820 con nodos `wf-node` posicionados por `left/top` absolutos, conexiones Bezier renderizadas en SVG, dos glosas italic flotando y una línea coral dashed "de feedback" extraña), e inspector derecho (`wf-inspector` con header por tipo, secciones Configuración/Evidencia/Errores/Últimas ejecuciones + botones Editar/Eliminar). Sin empty state para canvas vacío — la función asume siempre mocks cargados.

### Light

- [S1] El canvas es `1400×820` hard-coded (líneas ~3984, ~4107, ~4115) sin scroll ni zoom. En laptop 13" con sidebar (~240px) queda <1100px útil y se recorta todo el tramo derecho del workflow. No hay minimap. **Líneas ~3984, ~4107.** Fix: wrap `wf-canvas-wrap` con `overflow:auto`, canvas como `min-width: 1400px`, y añadir controles zoom `+/-/fit` en toolbar.
- [S1] La línea dashed coral (línea ~4116) que cruza de `(1180, 80) → (500, 280)` no tiene label ni affordance — un revisor no sabe qué significa. Si pretende representar "feedback loop" necesita tooltip o leyenda. **Línea ~4116.** Fix: envolver en `<g role="img" aria-label="Loop de feedback">` con `<title>` y añadir `<text>` "feedback" sobre la curva, o eliminar hasta que haya semántica clara.
- [S1] Botones Simular / Guardar draft / Publicar están en línea sin confirmación ni diff. "Publicar" sobre un workflow live v2.4 debería mostrar diff (nodos agregados/removidos) + checklist de tests antes de subir versión. **Líneas ~4090-4094.** Fix: Publicar abre modal con diff contra v2.4, lista de tests simulados OK/FAIL, y microcopy "Pasa a v2.5 · ¿Confirmar?".
- [S2] Paleta no tiene búsqueda — 6 categorías × 2-3 items funciona hoy pero cuando haya 20+ agentes o 10+ acciones el scroll es doloroso. **Líneas ~4097-4103.** Fix: input search en `wf-palette-header` con filtrado por label y tipo.
- [S2] El `input.wf-workflow-name` de 340px (línea ~4083) no tiene hint de auto-save ni indicador dirty. Si el usuario lo edita, no sabe si se guardó hasta apretar "Guardar draft". **Línea ~4083.** Fix: debounce 800ms + pill "Guardado" o "Cambios sin guardar" junto al nombre.
- [S2] Inspector vacío (sin nodo seleccionado) muestra solo `<p>` gris diciendo "Selecciona un nodo…" (línea ~4077). Es un empty state pobre — podría mostrar stats globales del workflow (runs 24h, latency p95, drafts aprobados last 7d) que hoy están enterrados por nodo. **Línea ~4075-4078.** Fix: empty state con stats agregados + CTA "Arrastrar primer nodo".
- [S3] `wfSelectedNode` es estado global module-level (línea ~3970) y al re-renderizar se pierde el focus del teclado en la paleta — el flujo drag-select-inspect es mouse-only. Sin navegación por teclado entre nodos no hay a11y.

### Dark

- [S1] Las conexiones Bezier (`<path class="wf-connection">`) usan color CSS no definido en el snippet leído pero probablemente `--border-strong`. En dark, `--border-strong` sin corregir (slice A) es 2.01:1 sobre bg — las conexiones se pierden. **Líneas ~3985-3997.** Fix: usar `var(--border-strong)` corregido (#6B6658 en slice A) + subir a 1.5px stroke-width y añadir `.wf-connection.active` con `--coral-primary` + stroke 2px.
- [S2] Las glosas italic (líneas ~4109, ~4112) que dicen "Pipeline · lectura a acción" usan `background:var(--bg-surface);border:1px solid var(--border-subtle)` — en dark el border subtle es 1.30:1 contra surface, la tarjeta flota sin silueta. **Líneas ~4109, ~4112.** Fix: usar `--border-subtle` corregido (#4A463F, slice A) + añadir `box-shadow: var(--shadow-sm)` corregido.
- [S2] Border-left de glosas usa `var(--node-trigger)` (gris) y `var(--node-action)` — en dark `--node-trigger` es `#9CA3AF` y la glosa se lee pero pierde jerarquía frente a los nodos activos de mismo color. Considerar atenuar 60% opacidad para glosa vs nodo.

### i18n

- Hard-coded:
  - Labels de categoría: "Triggers", "Agentes", "Políticas", "Aprobación", "Acciones", "Outputs" **líneas ~4003-4031**.
  - Labels de items: "Correo entrante", "Webhook", "Schedule", "Cotizador", "Triage", "Quote Drafter", "Pricing check", "Bandeja humana", "Slack DM", "Enviar correo", "Actualizar CRM", "Crear documento", "Audit log", "Notificar operador" — **líneas ~4003-4031**.
  - Valor default del nombre: "Cotización RFQ · B2B calzado seguridad" **línea ~4083**.
  - Pill "Live · v2.4" **línea ~4086**.
  - Botones "Versiones", "Simular", "Guardar draft", "Publicar" **líneas ~4090-4094**.
  - "Pipeline · lectura a acción", "Ejecución · post-aprobación" **líneas ~4110, ~4113**.
  - "Arrastra al canvas para añadir" **línea ~4100**.
  - Labels inspector "Configuración", "Evidencia requerida", "Mínimo", "3 fuentes", "Fuentes válidas", "Errores", "On fail", "Reintentos", "Últimas ejecuciones", "Exitosas 24h", "Latencia p95" **líneas ~4053-4069**.
- Overflow: "Quote Drafter · Propuestas B2B" en palette-item de ancho fijo (paleta ~240px) ya está al límite. PT-BR "Redator de Propostas · Propostas B2B" revienta el label. **Línea ~4011.** Segundo ejemplo: el pill "Live · v2.4" con traducción DE "Aktiv · v2.4" no rompe, pero "Cambios sin guardar" (feature S2 propuesta) en DE "Nicht gespeicherte Änderungen" (30ch) sí.

### a11y

- [S1] Canvas SVG (`svg.wf-connections`) no tiene `role="img"` ni `<desc>` — un workflow de cotización B2B es contenido crítico que debería poder leerse en modo lista por keyboard. **Línea ~4107.** Fix: generar `<ol class="sr-only">` paralelo con la secuencia de nodos + conexiones ("1. Trigger: Correo entrante → 2. Agente Triage → 3. Policy Pricing check…").
- [S1] `onclick` en cada nodo (línea ~3972) no tiene equivalente keyboard — no hay `tabindex="0"` ni `keydown` con Enter/Space. El builder es mouse-only. **Líneas ~3969-3980.** Fix: añadir `tabindex="0" role="button" aria-label="Nodo ${type}: ${title}"` + `onkeydown` handler.
- [S2] Paleta items con `draggable="true"` (línea ~4036) no tienen anuncio para SR — drag-and-drop nativo no es accesible. Necesita alternativa keyboard: seleccionar item, tecla Enter, elige posición (grid) y Enter para colocar. **Línea ~4036.**
- [S2] Toolbar `wf-workflow-name` input sin `<label>` visible ni `aria-label`. **Línea ~4083.** Fix: `<label class="sr-only">Nombre del workflow</label>` o `aria-label`.

### Snippets

```html
<!-- S1: canvas con scroll + zoom controls + a11y paralelo -->
<div class="wf-toolbar">
  <div class="wf-toolbar-left">
    <label class="sr-only" for="wf-name">Nombre del workflow</label>
    <input id="wf-name" class="wf-workflow-name" value="Cotización RFQ · B2B calzado seguridad">
    <span class="wf-save-state" data-state="saved">Guardado</span>
    <span class="wf-status-pill wf-status-live"><span class="dot"></span>Activo · v2.4</span>
  </div>
  <div class="wf-zoom-controls" role="group" aria-label="Controles de zoom">
    <button class="icon-btn" aria-label="Alejar">−</button>
    <span class="wf-zoom-value tabular">100%</span>
    <button class="icon-btn" aria-label="Acercar">+</button>
    <button class="btn btn-ghost btn-sm">Ajustar</button>
  </div>
</div>
<div class="wf-canvas-wrap" style="overflow:auto">
  <div class="wf-canvas" style="min-width:1400px;min-height:820px">
    <svg class="wf-connections" role="img" aria-labelledby="wf-desc">
      <desc id="wf-desc">Workflow: Trigger Correo entrante → Agente Triage → Policy Pricing → Aprobación humana → Acción Enviar correo → Output Audit log</desc>
      <!-- paths -->
    </svg>
    <!-- nodos con tabindex="0" role="button" -->
  </div>
</div>
<ol class="sr-only" aria-label="Secuencia del workflow">
  <li>Trigger: Correo entrante (Gmail bandeja@muitowork.com)</li>
  <li>Agente: Triage de RFQ</li>
  <li>Policy: Pricing check (rangos permitidos)</li>
  <!-- ... -->
</ol>
```

```javascript
// S1: nodo con soporte teclado
const nodeHTML = (n) => `
  <div class="wf-node node-${n.type}"
       style="left:${n.x}px;top:${n.y}px"
       tabindex="0"
       role="button"
       aria-label="Nodo ${wfTypeLabel(n.type)}: ${n.title}"
       onclick="wfSelectNode('${n.id}')"
       onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();wfSelectNode('${n.id}')}">
    <div class="node-header"><span class="node-type">${wfTypeLabel(n.type)}</span></div>
    <div class="node-title">${n.title}</div>
    <div class="node-sub">${n.sub}</div>
  </div>`;
```

---

## Ruta 12 — `#/conexiones`

### Wireframe

Grilla de integraciones con header (título "Conexiones" + subline con conteos "N conectadas · N con error · N disponibles" + botones Audit OAuth events y Catálogo completo), banner condicional `healthBanner` si hay errores (card coral-error con ícono alert + mensaje + botón "Ejecutar health check"), grilla `conn-grid` con `conn-tile` por integración — cada tile tiene head (logo circular con inicial + nombre + provider + pill de status), body con metadata variable por estado (Conectado: cuenta + last sync + scopes; Error: error message + último intento; Disponible: desc + scopes solicitados), y footer con acciones (Actividad/Configurar · Ver log/Reintentar · Conectar). Al final card dashed "¿Necesitás una integración que no está?" con CTA Solicitar integración.

### Light

- [S1] Banner de error (línea ~4191-4199) solo muestra el primer error en microcopy ("Amazon SP-API · token expirado — los agentes dependientes están pausados") hard-coded, no un loop sobre `conns.filter(c => c.status === 'error')`. Si hay 2 integraciones en error, el banner sigue mostrando solo Amazon. **Línea ~4196.** Fix: generar lista `errored.map(e => e.name + ': ' + e.error).join(' · ')` o expandible con `<details>`.
- [S1] `conn-tile-logo` es solo la primera letra del nombre (`${c.name[0]}`, línea ~4236) — para integraciones clave (Gmail, HubSpot, Amazon) el usuario espera el logo oficial para reconocimiento instantáneo. Un círculo con "G" para Gmail Y Google Drive es confuso. **Línea ~4236.** Fix: añadir `logo: 'url(...)' | inline-svg` en `CONN_META` y fallback a inicial solo si falta.
- [S1] Tiles no tienen affordance de estado "procesando" / "reintentando" cuando el usuario aprieta "Reintentar" — `alert()` y ya. Un OAuth retry debería cambiar pill a "Reintentando…" con `.skeleton` en el body durante ~2s. **Línea ~4217.** Fix: usar `aria-busy="true"` + skeleton (slice A C.2 pattern 8) y luego toast con resultado.
- [S2] La acción "Conectar" en tile Disponible (línea ~4225) abre flujo OAuth via `alert()` pero no muestra qué scopes va a pedir — los scopes están en el body del tile pero el botón no los repite en confirm modal. Regulación exige consent claro. **Línea ~4225.** Fix: Conectar abre modal con lista de scopes + botón "Continuar a Google" (o provider correspondiente).
- [S2] Grid `conn-grid` no se menciona con media query — probablemente es `repeat(auto-fill, minmax(320px, 1fr))` pero si es fijo de 3 cols, en laptop colapsa. Verificar y forzar auto-fill con minmax. **Línea ~4266.**

### Dark

- [S1] Banner de error (línea ~4191) usa `border-left:3px solid var(--error)` + body en `--text-muted`. En dark `--error` sin corregir es 3.13:1 (slice A) — la barra coral-roja se confunde con el coral-primary del brand. **Línea ~4192.** Fix: usar `--error` corregido (slice A #D97070) y en el mensaje body usar `--text-secondary` no `--text-muted` (pasa AA).
- [S2] El card dashed de "Solicitar integración" (línea ~4268) usa `background:var(--bg-subtle);border-style:dashed` — en dark `--bg-subtle` es `#34312C`, muy cerca del `--bg-surface` (#2A2824); el dashed se pierde y parece un tile más. **Línea ~4268.** Fix: cambiar border color a `var(--border-strong)` corregido + aumentar a dashed 1.5px o usar `border-color:var(--coral-tint-strong)` (slice A).

### i18n

- Hard-coded:
  - Todo `CONN_META[].desc` **líneas ~4175-4182** — "Lectura/envío de correo operativo. OAuth2 solo-lectura hasta aprobación.", "CRM: deals, contactos, pipelines. Escritura requiere aprobación humana.", etc. (6 strings completos).
  - Pills y labels: "Conectado", "Error", "Disponible", "Cuenta:", "Última sync:", "Scopes:", "Último intento:" **líneas ~4205, ~4210-4213**.
  - Microcopy banner: "X integración con error activo", "los agentes dependientes (ej. Monitor FBA) están pausados" **línea ~4195-4196**.
  - Strings botones: "Actividad", "Configurar", "Ver log", "Reintentar", "Conectar", "Audit · OAuth events", "Catálogo completo →", "Ejecutar health check", "Solicitar integración" **líneas ~4207-4259**.
  - "¿Necesitás una integración que no está en el catálogo?" **línea ~4272**.
- Overflow: "sellingpartnerapi::orders · sellingpartnerapi::inventory" (línea ~4179) ya rompe el body del tile (280px ancho útil). En PT-BR o ES con hint adicional revienta aún más. **Línea ~4212.** Fix: `word-break: break-all` + `max-height: 3em; overflow: hidden; text-overflow: ellipsis` con tooltip del scope completo.

### a11y

- [S1] Tiles son `<div class="conn-tile">` sin rol (`role="article"` o anidar en `<article>`) — cada tile es unidad semántica independiente. **Línea ~4234.** Fix: `<article class="conn-tile" aria-labelledby="conn-${c.id}-title">` y el título como `<h3 id="conn-${c.id}-title">`.
- [S2] Pills de status (`pill-success`, `pill-error`, `pill-neutral`) solo comunican por color + texto. Si un color-blind revisa, "Conectado/Error/Disponible" se distinguen solo por label — OK, pero el dot decorativo necesita `aria-hidden="true"` para no leerse como "bullet".
- [S2] Botones con ícono único (`<svg class="ico-sm ico"><use href="#i-arrow-right"/></svg>` dentro del CTA Conectar) no tienen `aria-hidden` en svg — SR lee "imagen Conectar". **Línea ~4226.** Fix: envolver svg con `aria-hidden="true"` o usar `role="img" aria-label` si es el único contenido.

### Snippets

```html
<!-- S1: tile con logo real + aria-busy en retry -->
<article class="conn-tile" aria-labelledby="conn-gmail-title" data-status="connected">
  <div class="conn-tile-head">
    <div class="conn-tile-logo">
      <img src="/logos/gmail.svg" alt="" width="32" height="32">
    </div>
    <div style="flex:1">
      <h3 class="conn-tile-title" id="conn-gmail-title">Gmail</h3>
      <div class="conn-tile-sub">Google</div>
    </div>
    <span class="pill pill-success pill-dot"><span class="dot" aria-hidden="true"></span>Conectado</span>
  </div>
  <div class="conn-tile-body">...</div>
  <div class="conn-tile-footer">
    <span class="text-xs text-muted" aria-label="Identificador OAuth">gmail_oauth2</span>
    <div class="actions">
      <button class="btn btn-ghost btn-sm">Actividad</button>
      <button class="btn btn-secondary btn-sm">Configurar</button>
    </div>
  </div>
</article>
```

```javascript
// S1: banner multi-error + detalle expandible
const errored = conns.filter(c => c.status === 'error');
const healthBanner = errored.length > 0 ? `
  <div class="card card-error" role="status" aria-live="polite">
    <svg class="ico" aria-hidden="true"><use href="#i-alert"/></svg>
    <div style="flex:1">
      <div class="card-error-title">${errored.length} ${errored.length === 1 ? 'integración' : 'integraciones'} con error activo</div>
      ${errored.length > 1 ? `
        <details><summary class="text-xs">Ver detalle</summary>
          <ul class="text-xs">${errored.map(e => `<li><strong>${e.name}:</strong> ${e.error}</li>`).join('')}</ul>
        </details>` : `
        <div class="text-xs text-muted">${errored[0].name}: ${errored[0].error}</div>`}
    </div>
    <button class="btn btn-secondary btn-sm">Ejecutar health check</button>
  </div>` : '';
```

---

## Ruta 13a — `#/settings/:tab` (6 tabs)

### Wireframe

Layout `settings-layout` a dos columnas: nav vertical izquierdo (`settings-nav` con 6 links Perfil/Equipo/Policies/Pricing/Audit log/Facturación) y contenido derecho con N `settings-section` por tab. Cada section tiene `<h3>`, `.section-desc`, y serie de `.form-row` grid-based (label + input). Header arriba con título "Configuración" + subline "Workspace · Muito Work Limitada · plan Pilot". Los 6 sub-render: Perfil (2 secciones: identidad + notificaciones con toggles), Equipo (lista miembros + roles y permisos), Policies (engine + 5 policy rows), Pricing (plan actual + próximos planes), Audit log (tabla mono 6 eventos + botón cargar más), Facturación (datos fiscales + método de pago). Densidad alta-media; `form-row` declarada implícitamente como grid de dos columnas rígido.

### Light

- [S1] Nav de settings usa `onclick="go('settings/${t.id}')"` sobre `<div>` — no es `<a>` ni `<button>`, no tiene focus outline ni `role="link"`. **Línea ~4302.** Fix: usar `<a href="#/settings/${t.id}" class="settings-nav-link">` o `<button role="tab">`.
- [S1] `form-row` tiene `grid-template-columns` sobrescrito inline en varios lugares con valores diferentes (`1fr 140px 120px 80px` equipo línea ~4406, `170px 200px 1fr 120px 80px` audit línea ~4561, `1fr 80px 90px 80px` policies línea ~4491). No hay clase canónica para cada densidad. **Líneas varias.** Fix: definir `.form-row--2col`, `.form-row--member`, `.form-row--audit`, `.form-row--policy` y eliminar inline styles.
- [S1] El toggle de notificaciones (`<label class="toggle active">`) no tiene input semántico — es un `<label>` con `<span class="toggle-switch">` decorativo. No se puede activar por keyboard, no refleja estado en HTML, no es form-submittable. **Líneas ~4374, ~4380, ~4386, ~4392.** Fix: envolver `<input type="checkbox" class="sr-only" checked>` dentro, toggle se estiliza con `:has(input:checked)`.
- [S2] En Audit log tab (líneas ~4551-4585), la tabla tiene `font-family:'JetBrains Mono'` inline y tamaño 11px — se lee bien para 6 eventos pero con 50+ (botón "Cargar 50 eventos anteriores") la experiencia sin virtualización ni filtros funcionales es pesada. Los botones "Filtrar" y "Exportar CSV" son `alert()` mocks. **Línea ~4576-4577.** Fix: filtros por actor/action/fecha persistentes en URL `?actor=x&action=draft.approved`.
- [S2] `policyRow()` (línea ~4488) muestra pill `v1.4.2` como `pill-neutral` pero no hay diff viewer ni historial accesible — botón "Ver" es `alert()`. Una policy es un contrato, necesita changelog + diff visual. **Línea ~4499.** Fix: "Ver" abre drawer con tabs "Actual | Historial | Diff v1.4.1 → v1.4.2".
- [S2] Pricing tab muestra "Uso este mes" con barra de progreso 25% (línea ~4520-4525) pero no tiene alert threshold. Al 80% debería aparecer `pill-warning` "Cerca del límite" + CTA upgrade. **Línea ~4524.**
- [S3] Ni un `<form>` en todo Settings — cada input es standalone sin `onchange` ni batch save. El usuario modifica 5 campos y no hay "Guardar cambios" visible, asume auto-save pero no hay feedback. **Varias líneas.** Fix: footer sticky por section con "Guardar" + "Descartar" cuando haya dirty state.

### Dark

- [S1] `pill-coral` en Pricing "Actual" y plan current (líneas ~4511, ~4543) tiene color `var(--coral-primary)` sobre fondo `var(--coral-tint)`. En dark original el tint es 0.15 opacity — borderline (slice A reporta ~4.0:1). **Línea ~4511.** Fix: aplicar `--coral-tint` corregido del slice A (0.18).
- [S2] Barra de progreso uso (línea ~4521) es un div con `background:var(--bg-subtle)` wrapeando otro con `width:25%;background:var(--coral-primary)`. En dark sobre `--bg-primary` (#1F1E1C) la barra `--bg-subtle` (#34312C) es apenas visible y el fill coral sobre ella tiene delta ok pero el track se pierde. **Línea ~4521.** Fix: `--bg-subtle` corregido (slice A no lo cambia pero el wrapper podría tener `box-shadow:inset 0 0 0 1px var(--border-subtle)`).
- [S2] Audit log tabla usa `color:var(--text-muted)` en timestamp (línea ~4562) — 11px mono en dark con `--text-muted` original falla AA (3.88:1). **Línea ~4562.** Fix: `--text-muted` corregido slice A (#A49C90 = 4.78:1) o usar `--text-secondary`.

### i18n

- Hard-coded:
  - Labels de campos: "Nombre completo", "Aparece en drafts y audit log", "Email", "Rol en workspace", "Zona horaria", "Idioma de la interfaz" **líneas ~4341-4365**.
  - Valores de select: "Owner", "Operador", "Viewer", "America/Costa_Rica (UTC-6)", "Español (CR)", "English", "Português (BR)" **líneas ~4351, ~4357, ~4363**.
  - Títulos sección: "Perfil de usuario", "Preferencias de notificación", "Equipo", "Roles y permisos", "Policy engine", "Policies activas", "Plan actual", "Próximos planes", "Audit log", "Datos fiscales", "Método de pago" — **múltiples líneas**.
  - Microcopy: "Tu identidad dentro del workspace. Esta información es visible para tu equipo." **línea ~4339**, "Reglas externas al LLM. Versionadas en Git. Evaluadas en cada draft antes de ir a aprobación." **línea ~4457**, "Pilot design partner · facturación manual mensual." **línea ~4508**.
  - Pills status: "activo", "pendiente", "activa", "draft", "rotada" **múltiples líneas**.
  - "Cargar 50 eventos anteriores" **línea ~4582**.
  - "4 miembros · 3 activos · 1 pendiente de invitación" **línea ~4422**.
- Overflow: "Aprobación dual obligatoria" (`select option` línea ~4448) en EN "Mandatory dual approval" (23ch) OK, pero en DE "Zwingend vorgeschriebene Zweifachgenehmigung" (43ch) excede los 280px típicos de `.form-input`. Segundo: "Descuentos por volumen + plazos pago net" (línea ~4481) en PT-BR "Descontos por volume + prazos de pagamento líquido" (48ch) rompe la cell de `.form-row` en ancho policy.

### a11y

- [S1] Nav de settings no tiene `role="tablist"` ni `aria-current` — el link active solo tiene clase `.active` sin semántica. **Línea ~4302.** Fix: `<nav aria-label="Configuración"><a href aria-current="${t.id === active ? 'page' : 'false'}">`.
- [S1] `input disabled` del email (línea ~4346) usa `style="opacity:.7"` inline — semántica OK (el atributo `disabled`) pero el ratio de contraste del texto baja por debajo de AA. **Línea ~4346.** Fix: mantener `disabled` + añadir `aria-readonly="true"` y texto hint "solo lectura · contactá soporte para cambiar".
- [S2] `<select>` sin `<label for>` — la `form-label` existe pero es un `<div>`, no un `<label for="...">`. SR no asocia. **Varias líneas.** Fix: usar `<label for="sel-timezone">` y `<select id="sel-timezone">`.
- [S3] Audit log filter button con `onclick` sin `aria-expanded` — no hay feedback de estado si es dropdown. **Línea ~4576.**

### Snippets

```html
<!-- S1: nav con semántica + aria-current -->
<nav class="settings-nav" aria-label="Secciones de configuración">
  <a href="#/settings/perfil"
     class="settings-nav-link ${t.id === active ? 'active' : ''}"
     aria-current="${t.id === active ? 'page' : 'false'}">
    Perfil
  </a>
  <!-- ... -->
</nav>
```

```html
<!-- S1: toggle accesible con input real -->
<label class="toggle">
  <input type="checkbox" class="sr-only" checked>
  <span class="toggle-switch" aria-hidden="true"></span>
  <span class="toggle-label text-xs">Correo + push</span>
</label>
```

```css
.toggle { display: inline-flex; align-items: center; gap: var(--space-2); cursor: pointer; }
.toggle-switch { width: 32px; height: 18px; background: var(--bg-hover); border-radius: var(--radius-pill); position: relative; transition: background var(--duration-fast) var(--ease-standard); }
.toggle-switch::after { content: ''; position: absolute; top: 2px; left: 2px; width: 14px; height: 14px; background: var(--bg-surface); border-radius: 50%; transition: transform var(--duration-fast) var(--ease-standard); box-shadow: var(--shadow-sm); }
.toggle:has(input:checked) .toggle-switch { background: var(--coral-primary); }
.toggle:has(input:checked) .toggle-switch::after { transform: translateX(14px); }
.toggle:focus-within .toggle-switch { box-shadow: var(--focus-ring); }
```

---

## Ruta 13b — `#/admin/:tab` (10 tabs)

### Wireframe

Layout `admin-layout` tipo Settings pero con banner `.admin-banner` persistente arriba ("Modo administrador — cada acción queda registrada en System audit. Solo Owner.", con ícono `#i-lock`). Nav izquierdo `admin-nav` agrupado por sección en 3 grupos — Plataforma (Overview/API keys/Webhooks/OAuth apps), Seguridad (Secrets vault/Rate limits/IP allowlist/System audit), Gobernanza (Data & compliance/Danger zone con `.danger-link`). 10 tabs totales. Contenido derecho por tab: Overview (4 KPIs mini + grid 2col health rows + eventos críticos), Keys (rows con scope pill + masked key + usage + rotate/revoke), Webhooks (event + URL + secret + success rate + test ping), OAuth (disabled + empty state), Secrets vault (rows nombre + usedBy + status + rotar), Rate limits (inputs), IP allowlist (toggle enforce + textarea CIDRs), System audit (rows mono + filtros), Data & compliance (retenciones + SOC2 + backups + export), Danger zone (4 acciones destructivas con `confirmDanger()` que requiere tipear workspace name).

### Light

- [S1] Wayfinding crítico con 10 tabs en 3 secciones — el breadcrumb (`['Admin', ADMIN_TABS.find(t => t.id === activeTab).label]`, línea ~5303) solo tiene 2 niveles, no muestra la sección intermedia (Plataforma/Seguridad/Gobernanza). Un admin que sale de "Secrets vault" y vuelve no tiene orientación visual. **Línea ~5303.** Fix: breadcrumb de 3 niveles `['Admin', section, label]` y en nav la sección activa highlighted con `--coral-primary` en `.admin-nav-section`.
- [S1] El banner "Modo administrador" está fijo arriba pero no `position: sticky` — al scrollear Secrets vault (rows largos) el banner desaparece y el admin pierde el contexto de "estás en modo destructivo". **Líneas ~5282-5286.** Fix: `position: sticky; top: 0; z-index: 10` + `box-shadow: var(--shadow-sm)` al scrollear.
- [S1] Danger zone (`adminDanger`, líneas ~5645-5683) tiene 4 acciones irreversibles en el mismo bloque visual, distinguidas solo por título. La "Eliminar workspace" debería estar aislada con separador visual grueso y agrupada al final con segundo confirm (doble phrase check). **Líneas ~5651-5681.** Fix: dos sub-secciones "Reset operativo" (revocar keys, purgar memoria, congelar) vs "Destructivo final" (eliminar workspace) con divider `border-top: 2px solid var(--error)`.
- [S1] `confirmDanger()` (línea ~5684) usa `prompt()` nativo del browser — es feísimo, no sigue el sistema visual y no tiene focus trap. Además el string hardcoded `'Muito Work Limitada'` (línea ~5686) asume ese workspace. **Líneas ~5684-5690.** Fix: modal custom con `workspace_name` dinámico (`MOCK.workspace.name`), doble confirm (tipear nombre + apretar "Entiendo, eliminar"), botón `btn-danger` deshabilitado hasta que coincida el input.
- [S1] Admin banner usa `var(--error)` en el borde o fondo (implícito del `admin-banner` slice A línea 1875) y body text en 12px — en light `--error` pasa AA (7.33:1) pero en dark (3.13:1 sin corregir) falla. El banner más visible del producto no puede fallar AA. **Línea ~5283.** Fix: usar `--error` corregido (slice A #D97070 dark) + tamaño min 13px para el mensaje crítico.
- [S2] Secrets vault (línea ~5503) muestra `usedBy.join(', ')` en una celda de 1fr — con 5+ agentes rompe. No hay link desde el agent name a la vista del agente. **Línea ~5513.** Fix: `usedBy.slice(0,3).join(', ') + (rest > 0 ? ` y ${rest} más` : '')` + cada nombre como `<a href="#/agentes/${id}">`.
- [S2] IP allowlist (línea ~5572) tiene toggle "Enforce" pero al editarlo no hay validación CIDR ni "test" antes de guardar. El microcopy dice "no bloquea tu IP actual" pero no hay simulación preview. **Línea ~5577.** Fix: validar CIDR en blur + botón "Previsualizar efecto" que liste qué keys/IPs quedarían fuera.
- [S2] Rate limits (línea ~5551) tiene 5 inputs sueltos sin agrupar visualmente entre API rate limits y Agent runtime quotas — hay dos sections (línea ~5553 y ~5563) pero la relación no queda clara (una por key, otra por agente). **Líneas ~5551-5569.** Fix: añadir hint en cada `<h3>` "(aplica a cada API key individual)" vs "(aplica por agente)".

### Dark

- [S1] `admin-nav-link.danger-link` (`adminDanger` acceso en nav) usa color error; en dark falla AA. **Línea ~5275.** Fix: aplicar corrección slice A `--error:#D97070`.
- [S1] `.danger-row` en Danger zone (línea ~5651-5680) probablemente hereda un `border-color:var(--error)` o `background:rgba(139,47,47,.08)` — en dark este bg es casi invisible (mismo warm-brown del surface). **Línea ~5651.** Fix: `background: var(--color-error-bg)` corregido (slice A C.1) = `rgba(184,85,85,0.18)` dark, con `border-left: 3px solid var(--error)` (corregido).
- [S2] KPI mini tiles en Overview (línea ~5326) con `.kpi-mini-value tabular` — si el estilo hereda `--text-primary` OK; el `.kpi-mini-delta.up/down` usa semantic colors (`--success` / `--error`) que fallan AA dark sin corregir. **Línea ~5328.**

### i18n

- Hard-coded:
  - Labels de tabs `ADMIN_TABS`: "Overview", "API keys", "Webhooks", "OAuth apps", "Secrets vault", "Rate limits", "IP allowlist", "System audit", "Data & compliance", "Danger zone" **líneas ~5250-5259** — mezcla ES y EN sin lógica (keys en plural EN, Overview EN, Gobernanza ES).
  - Section names: "Plataforma", "Seguridad", "Gobernanza" **línea ~5268**.
  - Banner: "Modo administrador — cada acción queda registrada en System audit. Solo Owner." **línea ~5285**.
  - Microcopy dispersa: "Keys con scope (read/write/admin) · rotación automática cada 90 días recomendada · revocación inmediata disponible" **línea ~5405**, "Credenciales compartidas entre agentes · nunca expuestas al LLM · inyectadas en runtime por el policy engine · referenciables solo por nombre" **línea ~5526**.
  - Danger zone titles y descs (líneas ~5653-5680) — 4 acciones × 2 strings = 8 strings dentro de template.
  - Título subtitle del workspace: `'Eliminar workspace Muito Work Limitada'` **línea ~5680** — concat hard-coded del nombre.
  - Prompt string: "Acción destructiva: \"${action}\"\n\nPara confirmar, tipeá el nombre del workspace:" **línea ~5685**.
- Overflow: "Rotación automática cada 90 días recomendada · revocación inmediata disponible" (línea ~5405) ya es largo en ES; en DE "Automatische Rotation alle 90 Tage empfohlen · sofortige Widerrufung verfügbar" (78ch) rompe la línea subtitle. Segundo: pill `pill-error` "connection.error" + target largo `amazon_sp_api` + detail "token_expired hace 2h · 8 retries" en la row de eventos críticos (línea ~5359) — columna `1fr` se comprime con mono font, overflow horizontal.

### a11y

- [S1] **Wayfinding con 10 tabs.** Solo un `admin-nav-section` label (`<div>`, línea ~5273) separa Plataforma/Seguridad/Gobernanza — no hay `role="navigation"` ni `aria-label` por grupo. Screen reader lee los 10 links como lista plana. **Líneas ~5269-5280.** Fix: `<nav aria-label="Administración"><section aria-label="Plataforma"><h4 class="sr-only">Plataforma</h4>...` por grupo, convertir `admin-nav-section` a `<h4>` semántico.
- [S1] **Banner admin.** El banner `.admin-banner` no tiene `role="status"` ni `aria-live` — si el admin entra a la ruta via URL directa, SR no anuncia "estás en modo administrador". **Línea ~5283.** Fix: `<div role="region" aria-label="Contexto: modo administrador" class="admin-banner">`. Además la svg del lock no tiene `aria-hidden="true"` (línea ~5284).
- [S1] **Danger zone visual.** La sección `.danger-zone` (línea ~5647) y cada `.danger-row` no tienen diferenciación visual radical frente a otras admin-sections — mismo padding, mismo bg, solo cambia un pill rojo pequeño en botones. El admin necesita ver "estás en zona destructiva" a 2 metros del monitor. **Líneas ~5647-5681.** Fix: bg `rgba(139,47,47,.04)` light / corregido en dark, border-top 3px solid `--error`, ícono skull o warning grande 32px al inicio de la section.
- [S2] Tabla de System audit (línea ~5589-5596) sin `<table>` semántico — son `<div class="form-row">` styled como tabla. SR no navega por columnas. **Líneas ~5589-5596.** Fix: reemplazar por `<table>` con `<thead>` + `scope="col"` + `<tbody>`.
- [S2] Danger confirm usa `prompt()` nativo — no tiene focus trap, no retiene foco al cerrar, no es `aria-modal`. **Línea ~5685.** Fix: modal custom con `role="dialog" aria-modal="true" aria-labelledby="danger-title"` (ver snippet).
- [S3] Los botones `↻` y `✕` (líneas ~5395, ~5396) de la tabla de keys usan unicode arrow/x como label — inaccesible para SR. Solo `title="Rotar"` / `title="Revocar"` que no siempre lee SR. Fix: `aria-label="Rotar key fl_prod_live"`.

### Snippets

```html
<!-- S1: nav con wayfinding accesible -->
<nav class="admin-nav" aria-label="Administración">
  <section aria-labelledby="admin-nav-plataforma">
    <h4 id="admin-nav-plataforma" class="admin-nav-section">Plataforma</h4>
    <a href="#/admin/overview" class="admin-nav-link active" aria-current="page">
      <svg class="ico-sm ico" aria-hidden="true"><use href="#i-home"/></svg>Overview
    </a>
    <!-- ... -->
  </section>
  <section aria-labelledby="admin-nav-seguridad">
    <h4 id="admin-nav-seguridad" class="admin-nav-section">Seguridad</h4>
    <!-- ... -->
  </section>
  <section aria-labelledby="admin-nav-gobernanza">
    <h4 id="admin-nav-gobernanza" class="admin-nav-section">Gobernanza</h4>
    <!-- ... -->
    <a href="#/admin/danger" class="admin-nav-link danger-link">
      <svg class="ico-sm ico" aria-hidden="true"><use href="#i-trash"/></svg>Danger zone
    </a>
  </section>
</nav>
```

```html
<!-- S1: banner persistente con semántica -->
<div class="admin-banner" role="region" aria-label="Contexto de administración">
  <svg class="ico" aria-hidden="true"><use href="#i-lock"/></svg>
  <span><strong>Modo administrador</strong> — cada acción queda registrada en System audit. Solo Owner.</span>
</div>
```

```css
.admin-banner {
  position: sticky; top: 0; z-index: var(--z-dropdown, 100);
  background: var(--color-error-bg); /* slice A C.1 */
  border-bottom: 1px solid var(--error);
  color: var(--error);
  padding: var(--space-2) var(--space-8);
  display: flex; align-items: center; gap: var(--space-2);
  font-size: var(--fs-body-sm);
}
```

```html
<!-- S1: danger zone visual radical + confirm custom modal -->
<section class="admin-section danger-zone" aria-labelledby="danger-title">
  <div class="danger-zone-hero">
    <svg class="ico-xl" aria-hidden="true" style="color:var(--error)"><use href="#i-alert"/></svg>
    <div>
      <h3 id="danger-title" style="color:var(--error)">Danger zone</h3>
      <p class="text-xs">Acciones irreversibles · requieren confirmación por nombre · quedan registradas en System audit.</p>
    </div>
  </div>
  <!-- Sub-sección 1: reset operativo (reversible en parte) -->
  <div class="danger-group" data-severity="reset">
    <div class="danger-row">...</div>
  </div>
  <!-- Sub-sección 2: destructivo final -->
  <div class="danger-group" data-severity="destroy">
    <h4>Destructivo final</h4>
    <div class="danger-row">
      <div>
        <div class="danger-row-title">Eliminar workspace</div>
        <div class="text-xs text-muted">Destruye todo · no hay undo.</div>
      </div>
      <button class="btn btn-danger btn-sm" onclick="openDangerModal('destroy-workspace')">Eliminar workspace</button>
    </div>
  </div>
</section>
```

```javascript
// S1: modal custom reemplaza prompt()
function openDangerModal(action) {
  const ws = MOCK.workspace?.name || 'Muito Work Limitada';
  const modal = `
    <div class="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="danger-modal-title">
      <div class="modal modal-danger">
        <header class="modal-header">
          <h3 id="danger-modal-title">Confirmación destructiva</h3>
        </header>
        <div class="modal-body">
          <p>Esta acción no se puede deshacer. Para confirmar, tipeá el nombre del workspace:</p>
          <p class="workspace-name-echo"><strong>${ws}</strong></p>
          <input id="danger-confirm" class="input-danger" autocomplete="off" autofocus>
        </div>
        <footer class="modal-footer">
          <button class="btn btn-ghost" onclick="closeDangerModal()">Cancelar</button>
          <button id="danger-submit" class="btn btn-danger" disabled>Entiendo, eliminar</button>
        </footer>
      </div>
    </div>`;
  // render + focus trap + input listener que habilita submit si === ws
}
```

---

## Task launcher — ⌘K

### Wireframe

Modal `launcher-modal` sobre `launcher-backdrop` (fondo blur), ancho ~640px. Head (`launcher-head`) con ícono search + input "Comando rápido: pedir, crear, consultar…" + kbd "esc". Body en secciones: (1) label uppercase "¿A qué agente le pedís?" + grilla de `launcher-agent-opt` (ancho fijo con nombre + role truncado a 48ch), (2) textarea "Descripción de la tarea" con placeholder de ejemplo Goliath L42, (3) grid 1fr 1fr con "Input / archivo" input + "Tipo de output esperado" select (Reporte/Tabla/Draft saliente/Recomendación binaria), (4) "Prioridad" select (Normal SLA 4h / Alta SLA 1h / Low). Foot con microcopy "⏎ para enviar · esc para cerrar · el agente trabaja async…" + botón primary "Pedir tarea". Shortcut global `⌘K` / `Ctrl+K` atado en `window.keydown` (línea ~5792).

### Light

- [S1] **Focus trap ausente.** Al abrir el modal, el foco va al input via `setTimeout(() => cmd.focus(), 40)` (línea ~5761-5764) pero si el usuario tabbea fuera, se escapa a la página detrás. Modal sin trap no es accesible y permite click-through sobre controles del shell. **Líneas ~5757-5765.** Fix: trap con `focus-trap` pattern (primer+último tabbable + loop), y al cerrar devolver foco al elemento originador (`lastActiveElement`).
- [S1] **Search affordance sin función.** El input `launcher-cmd` (línea ~5711) tiene placeholder "Comando rápido" pero no hace nada — ni filtra agentes, ni ejecuta slash commands. El ícono search sugiere búsqueda que no existe. **Línea ~5711.** Fix: ligar a filtrado de `launcher-agent-opt` (fuzzy match nombre+role) y parsear slash commands (`/ask`, `/forecast`, `/compare`) como atajos.
- [S1] **Submit con Enter desde textarea** — el microcopy dice "⏎ para enviar" (línea ~5749) pero `submitLauncher()` solo se dispara por click del botón. Enter en textarea hace saltar línea. **Líneas ~5720, ~5750.** Fix: listener global en modal `keydown` — si `Cmd/Ctrl+Enter` desde cualquier field → submit; microcopy actualizado a "⌘⏎ para enviar".
- [S2] `launcher-agent-opt` no muestra qué modo de agente (Shadow/Learning/Active) tiene — arrastra toda la lista de `MOCK.agents` incluyendo agentes en shadow. Un pilot que pide algo a un agente en Shadow Mode no recibirá output visible (shadow no ejecuta). **Línea ~5701.** Fix: mostrar pill de modo junto al nombre + ordenar Active primero, Shadow al final con opacidad 0.6.
- [S2] `pickLauncherAgent()` (línea ~5775) usa `event.currentTarget` implícito sin declaración — funciona pero `onclick="pickLauncherAgent('${a.id}')"` no pasa event si se invoca por keyboard (Enter sin evento sintético). **Línea ~5775.** Fix: `pickLauncherAgent(id, event)` explícito y keyboard-friendly.
- [S2] No hay preview ni "last used" — si Álvaro siempre pide al Forecast agent, debería aparecer primero. **Línea ~5700-5704.** Fix: persistir `lastUsedAgentId` en localStorage + bubble al top.
- [S2] Submit bloquea por `task.trim()` vacío con `alert()` (línea ~5783) — inconsistente con estilo del producto. Fix: inline validation con `aria-describedby="task-error"` + texto rojo debajo del textarea.

### Dark

- [S1] Backdrop usa `rgba(0,0,0,0.3)` (slice A línea 2320) — en dark sobre `--bg-primary` warm-dark el delta es insuficiente, el fondo no se oscurece lo suficiente para que el modal destaque. **Línea ~5707 CSS en slice A 2320.** Fix: `--bg-overlay` corregido slice A = `rgba(0,0,0,0.65)` dark + `backdrop-filter: blur(2px)`.
- [S1] `launcher-agent-opt.selected` usa `border-color: var(--coral-primary); background: var(--coral-tint)` (slice A línea 2369). En dark el tint 0.14 opacity da un coral sobre warm-dark apenas visible; la selección se comunica por border solo. Usuario con daltonismo rojo-verde ve idéntico a hover. **Línea ~5701 (2369 CSS).** Fix: aplicar `--coral-tint` corregido (0.18+); añadir checkmark visual en la opt seleccionada (`::after` con svg check).
- [S2] `kbd` "esc" (línea ~5712) hereda estilos base del slice A — si el color es `--text-muted` sobre `--bg-subtle` en dark, falla AA. **Línea ~5712.** Fix: usar `--text-secondary` o `--text-muted` corregido.

### i18n

- Hard-coded:
  - Placeholder input: "Comando rápido: pedir, crear, consultar…" **línea ~5711**.
  - Label: "¿A qué agente le pedís?" **línea ~5715**.
  - Labels: "Descripción de la tarea", "Input / archivo", "Tipo de output esperado", "Prioridad" **líneas ~5719, ~5725, ~5729, ~5740**.
  - Placeholder textarea con nombres tech: "Revisá ventas_q1_2026.xlsx y dame forecast abril-junio con estacionalidad. Focus en Goliath L42." **línea ~5720**.
  - Placeholder input: "drive://… o URL o texto pegado" **línea ~5726**.
  - Select options: "Reporte narrativo", "Tabla / dataset", "Draft saliente", "Recomendación binaria", "Normal · SLA 4h", "Alta · SLA 1h", "Low · cuando haya capacity" **líneas ~5731-5745**.
  - Foot: "⏎ para enviar · esc para cerrar · el agente trabaja async, el deliverable aparece en Bandeja → Entregables" **línea ~5749**.
  - Button: "Pedir tarea" **línea ~5751**.
  - Alert strings: "Describí qué querés que haga el agente." **línea ~5783**, "Tarea enviada a ${agent.name}..." **línea ~5788**.
- Overflow: "Recomendación binaria" (línea ~5734) en select — en DE "Binäre Empfehlung" OK, pero "Low · cuando haya capacity" (línea ~5744) mezcla EN "Low" + ES "cuando haya capacity", y en traducción completa "Baja · cuando haya capacidad disponible" (35ch) comprime el select de 1fr en el grid 1fr 1fr. Tech names Goliath/Rana Walk en placeholder (línea ~5720) no se traducen — OK per CLAUDE.md, pero el resto del string sí.

### a11y

- [S1] **Focus trap.** Como dicho arriba, no existe. WCAG 2.4.3 + 2.1.2 exigen que el foco quede contenido en modal hasta cerrarse. **Líneas ~5757-5765.** Fix ver snippet.
- [S1] **Escape handler.** Existe (`launcherEsc`, línea ~5767) y es correcto pero se registra en `document` — si otro modal se superpone (ej. confirmDanger), ambos reciben Escape y cierran. **Línea ~5765.** Fix: listener local al modal element o top-of-stack pattern.
- [S1] **Modal sin `role="dialog"`.** El `launcher-backdrop` y `launcher-modal` no declaran `role="dialog"` ni `aria-modal="true"` ni `aria-labelledby`. SR no anuncia "diálogo abierto". **Líneas ~5707-5708.** Fix: `<div class="launcher-backdrop" role="dialog" aria-modal="true" aria-labelledby="launcher-title">` + `<h2 id="launcher-title" class="sr-only">Pedir tarea a un agente</h2>`.
- [S1] **Focus ring en input.** El input search no tiene `:focus-visible` explícito — hereda del slice A focus-ring solo si se aplicó la corrección. Dentro del backdrop oscuro, el coral-ring es crítico. **Línea ~5711.** Fix: `.launcher-head input:focus-visible { outline: none; box-shadow: var(--focus-ring) }` (slice A token).
- [S2] Labels de form (`<label>`) no tienen `for=` — textarea y selects no están asociados semánticamente. **Líneas ~5719, ~5725, ~5729, ~5740.** Fix: añadir `for="launcher-task"` etc.
- [S2] `launcher-agent-opt` es `<div onclick>` — ni `role="radio"` ni `tabindex`. El picker de agente es grupo de radios funcionalmente. **Línea ~5701.** Fix: `<div role="radio" aria-checked="${a.id === selected}" tabindex="0" onkeydown="Enter/Space">` dentro de `<div role="radiogroup" aria-label="Elegí un agente">`.
- [S3] Contraste del kbd "esc" pequeño (tamaño ~11px) debe pasar AA — validar con slice A.

### Snippets

```html
<!-- S1: modal con dialog semántico + focus trap + labels -->
<div class="launcher-backdrop"
     role="dialog"
     aria-modal="true"
     aria-labelledby="launcher-title"
     onclick="if(event.target===this)closeTaskLauncher()">
  <div class="launcher-modal">
    <h2 id="launcher-title" class="sr-only">Pedir tarea a un agente</h2>
    <div class="launcher-head">
      <svg class="ico" aria-hidden="true"><use href="#i-search"/></svg>
      <input type="text"
             id="launcher-cmd"
             placeholder="Comando rápido: pedir, crear, consultar…"
             aria-label="Búsqueda o slash command">
      <span class="kbd" aria-hidden="true">esc</span>
    </div>
    <div class="launcher-body">
      <div role="radiogroup" aria-labelledby="launcher-agent-label">
        <div id="launcher-agent-label" class="launcher-section-label">¿A qué agente le pedís?</div>
        <div class="launcher-agent-pick">
          <!-- opts con role="radio" aria-checked tabindex="0" -->
        </div>
      </div>
      <div class="launcher-row">
        <label for="launcher-task">Descripción de la tarea</label>
        <textarea id="launcher-task" required aria-describedby="task-error"></textarea>
        <div id="task-error" class="field-error" hidden role="alert"></div>
      </div>
      <!-- ... -->
    </div>
    <div class="launcher-foot">
      <span>⌘⏎ para enviar · esc para cerrar · async · deliverable aparece en Bandeja</span>
      <button class="btn btn-primary btn-sm" onclick="submitLauncher()">
        <svg class="ico-sm ico" aria-hidden="true"><use href="#i-arrow-right"/></svg>Pedir tarea
      </button>
    </div>
  </div>
</div>
```

```javascript
// S1: focus trap + return focus + Cmd+Enter submit
let _lastActiveElement = null;

function openTaskLauncher(preAgent) {
  _lastActiveElement = document.activeElement;
  // ... render modal ...
  const root = document.getElementById('launcher-root');
  trapFocus(root);
  root.addEventListener('keydown', handleLauncherKeys);
}

function trapFocus(container) {
  const focusables = container.querySelectorAll(
    'input, textarea, select, button, [tabindex="0"], [role="radio"]'
  );
  const first = focusables[0];
  const last = focusables[focusables.length - 1];
  container.addEventListener('keydown', (e) => {
    if (e.key !== 'Tab') return;
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault(); last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault(); first.focus();
    }
  });
}

function handleLauncherKeys(e) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
    e.preventDefault();
    submitLauncher();
  }
}

function closeTaskLauncher() {
  const r = document.getElementById('launcher-root');
  if (r) r.remove();
  document.removeEventListener('keydown', launcherEsc);
  if (_lastActiveElement && document.contains(_lastActiveElement)) {
    _lastActiveElement.focus(); // devolver foco al originador
  }
  _lastActiveElement = null;
}
```

```css
/* S1: focus-visible explícito en input launcher + opt radio */
.launcher-head input:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring); /* slice A */
  border-color: var(--coral-primary);
}
.launcher-agent-opt {
  position: relative;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-standard);
}
.launcher-agent-opt:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}
.launcher-agent-opt[aria-checked="true"]::after {
  content: '';
  position: absolute; top: 8px; right: 8px;
  width: 14px; height: 14px;
  background: var(--coral-primary);
  mask: url('data:image/svg+xml,...check...') center / contain no-repeat;
}
```

