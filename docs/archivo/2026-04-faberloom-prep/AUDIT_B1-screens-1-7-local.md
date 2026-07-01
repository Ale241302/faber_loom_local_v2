# AUDIT_B1 — Screens 1-7

## Ruta 1 — `#/landing`

### Wireframe
Nav superior con wordmark "FaberLoom" (Georgia italic, `.loom` en coral) + 4 enlaces ancla (Cómo funciona · Caso de uso · Precio · Entrar al demo). Hero en dos columnas: izquierda con eyebrow-pill (`i-shield` + "Control plane · draft-first · auditado"), H1 display con spans `.accent` coral, párrafo de sub-copy, CTA primaria coral + secundaria, y meta-row con pill coral + separador. Columna derecha "hero-visual" simula una Bandeja con 2 draft-rows (el segundo a `opacity:0.7`), evidencia con label y 3 botones de acción. Secciones inferiores: wedge (3 tarjetas numeradas 01/02/03), how (5 pasos numerados + CTA), pricing (3 tarjetas con featured coral) y footer con 3 columnas de enlaces.

### Light (≥3 findings)
- [S1] El botón "Entrar al demo →" de la nav (L.2998) usa `style="color:var(--text-primary)"` inline, no es `.btn`. Se pierde como link secundario en una nav que pide CTA clara. Fix: promover a `.btn.btn-primary.btn-sm` y quitar el inline — la diferenciación con "Cómo funciona/Caso de uso/Precio" tiene que ser visual, no sólo tipográfica. **Línea ~2998.**
- [S1] La "hero-visual" (L.3029-3063) NO usa el patrón `.card-evidence` (slice A §C.2.3) pese a ser una card con border-left y pretender parecerse al producto real. El hero-visual es lo primero que el buyer ve del producto y no comparte lenguaje visual con la Bandeja real. Fix: reemplazar el contenedor por `.card.card-evidence` y usar `.draft-row` con los mismos tokens que la ruta 3 (`--evidence` en border-left, `--bg-surface` fondo, `--shadow-sm` elevación). **Línea ~3029.**
- [S2] Los botones "Solicitar acceso/Empezar/Hablar con ventas" de pricing (L.3136, 3152, 3167) tienen `style="width:100%"` inline. Fix: añadir modifier `.btn-block` en el CSS base y eliminar los 3 inline — es una repetición que si crece (nuevos tiers) ensucia el HTML. **Línea ~3136.**
- [S2] `.hero-meta` usa `<span class="dot">·</span>` como separador manual (L.3024) igual que `.draft-meta` y `activity-time` — tres implementaciones distintas del mismo elemento. Fix: normalizar a un `.sep` o `::after` con `content:'·'; margin: 0 var(--space-2); color: var(--text-muted-weak);`.
- [S3] El párrafo hero-sub (L.3012) hace 3 líneas y termina con dos puntos y justificación rota. En ES se ve bien por casualidad de largo; en PT-BR va a overflow. Fix: endurecer `max-width: 58ch` en `.hero-sub` y limitar a 2 líneas de copy.

### Dark (≥2 findings)
- [S1] `hero-visual` fondo `--bg-surface` (#2A2824) contra `--bg-primary` (#1F1E1C) diferencia sólo ~10% luminancia y `--shadow-sm` dark (ver slice A E.2) apenas se ve. La card flota sin elevación → parece parte del fondo. Fix: aplicar `--shadow-md` (no `-sm`) al hero-visual en dark y usar el nuevo `border: 1px solid var(--border-subtle)` propuesto en slice A (`#4A463F`).
- [S2] `.accent` (el coral de "proponen" y "apruebas" en el H1, L.3009-3010) usa `--coral-primary` (#C96442) que en dark sobre `--bg-primary` da 4.27:1 — pasa PASS-LG por ser 56px pero el splash sobre crema->warm-dark se ve anémico vs. light. Fix: en dark usar `--coral-text` (#D97757) para el accent hero — es el único lugar donde importa que "arda".
- [S2] El `badge-featured` de pricing ("Más común", L.3139) suele ir coral sólido → en dark queda hot. Verificar que usa `--coral-primary` bg + `--text-on-coral`, no un gradient.

### i18n
- Hard-coded: "Cómo funciona" (L.2995), "Caso de uso" (L.2996), "Precio" (L.2997), "Entrar al demo →" (L.2998), "Agentes de IA que proponen, tú apruebas." (L.3009-3010), "Probar el demo" (L.3017), "Design partner pilot" (L.3023), "Distribuidores calzado seguridad · MX · CO · CR" (L.3025), "Bandeja · Drafts pendientes" (L.3032), "7 esperando aprobación" (L.3033), "Hecho para distribuidores B2B de calzado de seguridad" (L.3068), "Cómo funciona en 5 pasos" (L.3093), "Precio transparente" (L.3121), "Más común" (L.3139), "Solicitar acceso" (L.3136), "Empezar" (L.3152), "Hablar con ventas" (L.3167), "Muito Work" (L.3189), "Términos/Privacidad/Seguridad" (L.3197-3199). Todo en JS strings literales sin tabla `STRINGS`.
- Overflow ES→EN→PT-BR: "Solicitar acceso" (16ch) → "Request access" (14ch, OK) → "Solicitar acesso" (16ch, OK) pero "Hablar con ventas" (17ch) → "Talk to sales" (13ch, OK) → "Falar com vendas" (16ch, OK). El caso que rompe: el eyebrow "Control plane · draft-first · auditado" (35ch) → "Control plane · draft-first · audited" (37ch) → "Plano de controle · rascunho-primeiro · auditado" (50ch) — el pill-eyebrow desborda el flex-container del hero en laptop 13" con PT-BR.

### a11y (≥2 findings)
- [S1] Los `<a onclick="…">` del nav y footer (L.2995-2998, 3181-3199) NO tienen `href` — no son focusables por teclado, fail WCAG 2.1.1. Fix: cambiar a `<button class="link-ghost">` o poner `href="#how"` real y prevent-default en el handler.
- [S1] `.hero-cta > button` (L.3016, 3020) no tiene `aria-label`, y el primer botón incluye un ícono `i-arrow-right` cuyo texto "Probar el demo" ya basta, pero el screen reader lee el SVG si no tiene `aria-hidden="true"`. Fix: añadir `aria-hidden="true"` a todos los `<svg class="ico">` decorativos (~30 instancias en esta ruta).
- [S2] Contraste del `hero-sub` (L.3012) usa `--text-secondary` (#5A544C) sobre `--bg-primary` (#F4F1ED) = 6.64:1 PASS; en dark (#B8B0A4 sobre #1F1E1C) = 7.76:1 PASS. Pero la `.hero-eyebrow` con `--coral-primary` sobre `--coral-tint` apenas pasa (4.0:1 light, borderline dark). Fix: usar `--coral-text` (#A84F33 light / #D97757 dark) en el texto del eyebrow.
- [S2] `scrollToId()` no respeta `prefers-reduced-motion` — siempre hace smooth-scroll (L.3214). Fix: leer la media query y usar `'auto'` si el usuario la activa.

### Snippets (solo para S1)
```css
/* Fix 1 — CTA de nav consistente */
.landing-nav-links .btn-sm { margin-left: var(--space-2); }
.landing-nav-links a:not(.btn) {
  color: var(--text-secondary);
  font-size: var(--fs-ui, 13px);
  font-weight: 500;
  transition: color var(--duration-fast, 120ms) var(--ease-standard, ease);
}
.landing-nav-links a:not(.btn):hover { color: var(--text-primary); }

/* Fix 2 — hero-visual como card-evidence canónica */
.hero-visual {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-left: 3px solid var(--evidence);
  border-radius: var(--radius-lg, 8px);
  box-shadow: var(--shadow-md);
  padding: var(--space-4, 16px);
  display: flex; flex-direction: column; gap: var(--space-3, 12px);
}
[data-theme="dark"] .hero-visual {
  border-color: #4A463F;
  box-shadow: var(--shadow-lg);
}

/* Fix a11y 1 — nav anchors focusables */
.landing-nav-links a,
.footer-col a {
  cursor: pointer;
  outline: none;
}
.landing-nav-links a:focus-visible,
.footer-col a:focus-visible {
  box-shadow: var(--focus-ring);
  border-radius: var(--radius-sm, 4px);
}
```

---

## Ruta 2 — `#/dashboard`

### Wireframe
Shell estándar (sidebar 240px sticky con wordmark + 2 secciones de nav + user footer; topbar con breadcrumbs + search icon-btn + bell + theme toggle + avatar-menu). Main: page-header con saludo "Buenas tardes, Álvaro" + subtítulo rol/org, y 2 CTAs derecha ("Nuevo workflow" + "Ver bandeja (N)"). Debajo: grid de 4 `.kpi-card` (default · kpi-warning · kpi-success · kpi-evidence) cada una con label + value tabular + delta. Luego `.dash-grid` 2 columnas con paneles "Drafts recientes" y "Agentes activos" (listas clickeables), y `.dash-grid-2` con "Estado de conexiones" + "Control operativo" (3 bloques apilados con border-bottom).

### Light (≥3 findings)
- [S1] El saludo "Buenas tardes, Álvaro" (L.3316, slice A) está hardcodeado — no calcula la hora del usuario ni conoce su nombre sin passing MOCK. Fix: `getGreeting()` que mire `new Date().getHours()` y devuelva buenas días/tardes/noches + usar `MOCK.user.name` via variable i18n. No es cosmético, es el primer texto que el buyer lee en el demo. **Línea ~3316.**
- [S1] Los 4 KPIs no tienen tooltip ni definición de qué miden: "Evidencia promedio" (L.3347) puede leerse como "% de drafts con evidencia" o "# de fuentes por draft"; en rigor es el promedio del campo `evidenceAvg` pero nadie que no lo codeó lo sabe. Fix: añadir `<button class="info-dot">` con tooltip que explique fórmula (ej. "Confianza media del modelo por draft · últimas 24h"). **Línea ~3347.**
- [S2] `.dash-grid` usa `grid-template-columns: 1fr 1fr` (slice A implícito) — los paneles tienen contenidos heterogéneos (drafts son filas densas con pill+to+time, agents son filas con 2 métricas). Fix: definir `.dash-grid { grid-template-columns: 1.4fr 1fr; }` porque drafts necesita más ancho para el subject largo. **Línea ~3352.**
- [S2] Los `.kpi-delta` mezclan `<span class="up">+1</span>` y texto libre ("Promedio revisión: 2m 14s") → inconsistente. Algunos tienen semántica de variación (flechitas `.up/.down`), otros son contexto estático. Fix: separar en dos sub-componentes `.kpi-delta-trend` (con icono ↑↓) y `.kpi-delta-context` (sin icono, `--text-muted`).
- [S3] La fila de agent-mini (L.3286-3293) muestra `approvalRate%` con `confidenceClass` — pero approvalRate ≠ confidence. Es un false friend semántico (el color verde/ámbar/rojo se asigna con la misma función). Fix: crear `approvalClass(v)` separado y usar thresholds distintos (aprobación ≥95 verde, ≥85 ámbar, sino rojo).

### Dark (≥2 findings)
- [S1] `.kpi-card::before` (accent lateral coral 3px) es el único diferenciador visual entre kpi-cards. Las variantes `kpi-warning/success/evidence` pintan el accent del color semántico — en dark `--warning` (#D0A66A) sobre `--bg-surface` (#2A2824) da 6.55:1 OK, pero `--evidence` dark viejo (#A84A5A) da 2.66:1 → apenas visible, pierde el device forense. Fix: aplicar el `--evidence: #D48090` propuesto en slice A E.3.
- [S2] El `.activity-time` en `.activity-item` (L.3282) usa `--text-muted` (#8A8278) sobre `--bg-surface` (#2A2824) = 3.88:1, falla AA body. Son fechas relativas ("hace 4 min") en 11px → exactamente el tamaño WCAG más duro. Fix: usar `--text-muted` endurecido de slice A (#A49C90 en dark = 4.78:1) o subir font-size a 12px y weight a 500.
- [S2] `.conn-mini-row .text-xs.text-muted` con `white-space:nowrap` (L.3306) se corta en ellipsis sin aviso — el user no sabe que "carlos@distribuidoras…" era "carlos@distribuidorasdelnorte.com.mx". En dark esto se agrava porque el ellipsis `…` pierde contraste. Fix: `title="${c.account}"` en el parent div para que el hover muestre la cuenta completa.

### i18n
- Hard-coded: "Buenas tardes, Álvaro" (L.3316), "Nuevo workflow" (L.3321), "Ver bandeja" (L.3324), "Agentes activos" (L.3331, 3363), "Drafts pendientes" (L.3336), "Promedio revisión" (L.3338), "Aprobados hoy" (L.3341), "Evidencia promedio" (L.3346), "Drafts recientes" (L.3355), "Estado de conexiones" (L.3373), "Control operativo" (L.3382), "Últimas 24 horas" (L.3383), "Acciones bloqueadas por policy" (L.3388), "Pricing fuera de rango · falta evidencia · destinatario no verificado" (L.3391), "Drafts con revisión manual" (L.3395), "Esperando aprobación humana en bandeja" (L.3398), "Shadow runs evaluados" (L.3402), "2 agentes candidatos · 1 próximo a graduar" (L.3405). ≥3 cumplido.
- Overflow ES→EN→PT-BR: "Acciones bloqueadas por policy" (30ch) → "Actions blocked by policy" (25ch) → "Ações bloqueadas pela política" (30ch). En PT-BR + "runs" (3ch) → "execuções" (9ch) — la métrica "<b>${a.metrics.runs}</b> runs" rompe a 2 líneas en el `.agent-mini-row` porque el `.metric` es `min-content`. También "Shadow runs evaluados" → "Execuções shadow avaliadas" (26ch) no cabe en el ancho de label actual.

### a11y (≥2 findings)
- [S1] Los `.activity-item` y `.agent-mini-row` son clickables via `onclick=""` en el div padre (L.3273, 3286) pero NO tienen `role="link"`, `tabindex="0"` ni keydown handler → no navegables por teclado, fail WCAG 2.1.1. Fix: convertir a `<a href="#/console/${d.id}">` o agregar `role="link" tabindex="0" onkeydown="if(e.key==='Enter')…"`.
- [S1] Ningún `.kpi-card` tiene aria semantics — son números que cambian en tiempo real sin `aria-live` ni landmark. Fix: envolver `.kpi-grid` en `<section aria-labelledby="kpis-title">` y cada `.kpi-value` con `aria-label="${value} ${unit}, ${label}"`.
- [S2] Las métricas tabulares (L.3332, 3337, 3342, 3347) usan `font-variant-numeric: tabular-nums` correctamente pero el `.unit` que las acompaña (" / 14", "%") no tiene separación semántica — screen reader dice "ocho barra catorce" en vez de "ocho de catorce". Fix: `<span class="unit" aria-label="de 14"> / ${total}</span>`.
- [S2] Los `.widget-link "Ver todos →"` (L.3356, 3364, 3374) son `<a onclick>` sin href — no focusables. Mismo patrón que ruta 1.

### Snippets (solo para S1)
```css
/* Fix info-dot para KPIs con definición */
.kpi-label-row { display: flex; align-items: center; gap: var(--space-1, 4px); }
.info-dot {
  width: 14px; height: 14px;
  border-radius: 50%;
  background: var(--bg-subtle);
  color: var(--text-muted);
  font-size: 10px; font-weight: 700;
  display: inline-flex; align-items: center; justify-content: center;
  cursor: help;
  border: none;
  transition: all var(--duration-fast, 120ms) var(--ease-standard, ease);
}
.info-dot:hover, .info-dot:focus-visible {
  background: var(--coral-tint);
  color: var(--coral-primary);
  outline: none;
  box-shadow: var(--focus-ring);
}
.info-dot::before { content: 'i'; font-family: var(--font-display, Georgia), serif; font-style: italic; }

/* Fix keyboard para filas clickables */
.activity-item, .agent-mini-row, .conn-mini-row {
  cursor: pointer;
  outline: none;
  transition: background var(--duration-fast, 120ms) var(--ease-standard, ease);
}
.activity-item:hover, .agent-mini-row:hover, .conn-mini-row:hover { background: var(--bg-subtle); }
.activity-item:focus-visible, .agent-mini-row:focus-visible, .conn-mini-row:focus-visible {
  box-shadow: var(--focus-ring);
  border-radius: var(--radius-md, 6px);
}

/* Fix saludo dinámico — en JS */
/* function getGreeting() {
     const h = new Date().getHours();
     if (h < 12) return STRINGS.greeting_morning;
     if (h < 19) return STRINGS.greeting_afternoon;
     return STRINGS.greeting_evening;
   } */
```

---

## Ruta 3 — `#/bandeja` (tab Aprobar — default)

### Wireframe
Shell estándar + page-header con H1 "Bandeja" + subtítulo contextual al tab. Debajo `.bandeja-tabs` (row flex con 4 tabs: Para aprobar · Entregables · Alertas · Todo — cada uno con icono + label + `.tab-count`) + spacer flex-1 + CTA "Pedir tarea a agente" con kbd "⌘K". Toolbar: row con filter-chips (Todos · Prioridad alta · Correos · Cotizaciones · CRM) + search-input-wrap con ícono. Lista de `.draft-list-row` (grid): indicador de prioridad + type-icon · subject + meta (agent pill coral + destinatario + separador + tipo + ago + evidence-pill) · confidence-block (confidence-value grande + label) · priorityBadge + icon-btn para abrir.

### Light (≥3 findings)
- [S1] `.bandeja-tabs` (L.3434) es un componente custom paralelo a `.tabs` canónico (slice A §C.2.4) — rompe el sistema. Fix: migrar a `<nav class="tabs" role="tablist">` con `.tab[aria-selected="true"]` y pedir a AG-01 que actualice estilos. **Línea ~3434.**
- [S1] Los `.draft-list-row` son `onclick="go('console/${d.id}')"` en el row padre (L.3522) PERO adentro hay un `.icon-btn` con `event.stopPropagation()` (L.3548) que también lleva al mismo lugar — dos elementos focusables hacen lo mismo, el botón es redundante. Fix: quitar el icon-btn "→" y dejar sólo el row clickable con chevron visual al hover. **Línea ~3522, 3548.**
- [S2] `.evidence-pill` (L.3536) tiene el ícono de escudo en 10×10px con `stroke-width` heredado de `.ico` (=2, ver slice A). A ese tamaño el stroke queda muy grueso y se lee como manchón. Fix: usar modifier `.ico-xs { stroke-width: 1.75 }` del slice A §C.3. **Línea ~3537.**
- [S2] El empty state "Sin drafts para estos filtros" (L.3520) es un `<div>` inline con `padding:48px;text-align:center;color:var(--text-muted)` — no usa el `.empty-state` canónico propuesto en slice A §C.2.7. Fix: reemplazar por `.empty-state` con ícono + título + body + CTA ("Limpiar filtros").
- [S3] El subtítulo "Drafts salientes esperando tu aprobación · nada sale sin tu visto bueno" (L.3478) es muy largo para `page-subtitle`. El punto "nada sale sin tu visto bueno" es promesa de valor, repetida de landing — aquí el user ya está dentro, es ruido. Fix: trim a "Drafts salientes esperando tu aprobación".

### Dark (≥2 findings)
- [S1] `.priority-indicator.priority-high` es una barra vertical coral/roja de 3-4px — en dark sobre el `--bg-surface` del row, `--error` (#B85555) da 3.13:1. Para una barra decorativa de 3px que marca prioridad es borderline. Fix: aplicar el `--error: #D97070` del slice A E.3 para llevarla a 4.55:1.
- [S2] `.confidence-value.confidence-high` usa `--success` (#9BAD8C en dark) — 6.13:1 PASS. Pero `.confidence-value.confidence-mid` (`--warning`) y `.confidence-value.confidence-low` (`--error`) tienen font-size grande (~24px) sobre surface; `confidence-low` con `--error` dark queda demasiado brillante junto al row sutil → el eye va al rojo antes que al subject. Fix: bajar brillo con `filter: saturate(.85)` en dark o usar variantes `-muted` (rgba al 85%).
- [S2] `.filter-chip.active` usa `--coral-tint` bg + `--coral-primary` text (asumiendo slice A), en dark `rgba(217,119,87,0.18)` sobre `--bg-primary` (#1F1E1C) da un background apenas visible — el chip activo y el inactivo se ven casi iguales. Fix: usar `--coral-tint-strong: rgba(217,119,87,0.28)` solo para estado activo.

### i18n
- Hard-coded: "Bandeja" (L.3462), "Para aprobar" (L.3437, 3484), "Entregables" (L.3441, 3484), "Alertas" (L.3445, 3484), "Todo" (L.3448, 3484), "Pedir tarea a agente" (L.3453), "Todos" (L.3562), "Prioridad alta" (L.3563), "Correos" (L.3564), "Cotizaciones" (L.3565), "Buscar asunto, agente, destinatario…" (L.3570), "Mostrando X de Y drafts" (L.3577), "Ordenados por prioridad y antigüedad" (L.3579), "Sin drafts para estos filtros." (L.3520), "Drafts salientes esperando tu aprobación · nada sale sin tu visto bueno" (L.3478). ≥3 cumplido.
- Overflow ES→EN→PT-BR: "Pedir tarea a agente" (20ch) → "Ask an agent" (12ch, OK) → "Pedir tarefa ao agente" (22ch). En PT-BR el botón + kbd "⌘K" (que no se traduce) llega a ~28ch y el flex `justify-content: flex-end` del toolbar lo comprime contra los tabs. "Prioridad alta" (14ch) → "High priority" (13ch) → "Prioridade alta" (15ch) — chip aún OK. El caso duro: "Drafts salientes esperando tu aprobación" (41ch) → "Outbound drafts waiting for your approval" (42ch) → "Rascunhos de saída aguardando sua aprovação" (44ch) — ya corta en el page-subtitle en 1280px.

### a11y (≥2 findings)
- [S1] Los tabs `.bandeja-tab` son `<div onclick>` sin `role="tab"`, sin `aria-selected`, sin `aria-controls` — no anunciados como tabs al screen reader (L.3435-3447). Fix: migrar al `.tabs` canónico con `role="tablist"` + `<button role="tab" aria-selected="true" aria-controls="panel-aprobar">`.
- [S1] El input de búsqueda (L.3570) no tiene `<label>` ni `aria-label` — el ícono decorativo no lo sustituye. Fix: `aria-label="Buscar drafts"` en el input + `aria-hidden="true"` en el SVG.
- [S2] `.kbd` dentro del CTA ("⌘K", L.3454) se lee como "barra K" o "kbd kbd" según reader. Fix: envolver en `<kbd aria-label="Atajo Comando K">⌘K</kbd>`.
- [S2] `.filter-chip` activos no tienen `aria-pressed="true"` — son filtros toggle, no radio group. Fix: `<button class="filter-chip" aria-pressed="true" onclick="setBandejaFilter('high')">`.

### Snippets (solo para S1)
```css
/* Migrar bandeja-tabs a .tabs canónico (slice A §C.2.4) */
.bandeja-tabs { /* legacy alias — deprecar */ }
.page-wrap > .tabs {
  display: flex;
  gap: 2px;
  border-bottom: 1px solid var(--border-subtle);
  margin-bottom: var(--space-4, 16px);
  align-items: center;
}
.page-wrap > .tabs .tabs-spacer { flex: 1; }

/* Draft-row sin icon-btn redundante — chevron al hover */
.draft-list-row {
  position: relative;
  cursor: pointer;
  outline: none;
  transition: background var(--duration-fast, 120ms) var(--ease-standard, ease);
}
.draft-list-row::after {
  content: '›';
  position: absolute;
  right: var(--space-4, 16px);
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  font-size: 18px;
  opacity: 0;
  transition: opacity var(--duration-fast, 120ms) var(--ease-standard, ease);
}
.draft-list-row:hover { background: var(--bg-subtle); }
.draft-list-row:hover::after { opacity: 1; }
.draft-list-row:focus-visible {
  box-shadow: var(--focus-ring);
  border-radius: var(--radius-md, 6px);
}

/* Empty state canónico */
.empty-state {
  text-align: center;
  padding: var(--space-12, 48px) var(--space-6, 24px);
  color: var(--text-secondary);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3, 12px);
}
.empty-state-icon { width: 40px; height: 40px; color: var(--text-muted); stroke-width: 1.5; }
.empty-state-title { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.empty-state-body { font-size: 13px; max-width: 360px; line-height: 1.55; }
```

---

## Ruta 4 — `#/bandeja/entregables`

### Wireframe
Mismo shell + tabs bar. Body: lista de `.draft-list-row` reutilizada de Aprobar pero con diferencias clave — `.priority-indicator` siempre `priority-normal` (gris), `.type-icon.crm` con `i-file`, subject + meta (agent pill + "Tabla/Reporte" + ago + evidence-pill), bloque italic con cita del request (`"${d.request.substring(0,120)}…"`), confidence-block + pill "Listo" verde + icon-btn "→". Empty state hardcoded inline: card-padded con texto "Sin entregables pendientes. Pedile algo a un agente con ⌘K."

### Light (≥3 findings)
- [S1] La cita del request (L.3606) se trunca a 120 chars con `…` pero el título ya está truncado por CSS — doble truncamiento sin tooltip. El valor operativo del entregable es entender qué se pidió; si ambos truncan, el user pierde contexto. Fix: el request debería ir como `.request-snippet` con 2 líneas (`-webkit-line-clamp: 2`) + `title="${d.request}"` para hover completo. **Línea ~3606.**
- [S1] La ruta reutiliza `.draft-list-row` pero un "entregable" NO es un draft — es un resultado ya producido, no algo para aprobar. El icon-btn sigue siendo "→" y el CTA implícito es "abrir" (`deliverable/${d.id}`). Faltan acciones propias del dominio: Descargar, Compartir, Archivar. Fix: crear variante `.deliverable-row` con 3 acciones fijas (descargar/compartir/archivar) al estilo Agent Console brief (project_faberloom_agents_design, "3 botones fijos"). **Línea ~3589.**
- [S2] `.pill.pill-success.pill-dot` "Listo" (L.3613) es redundante con el confidence-block — ambos indican salud. Si el entregable está en esta tab es porque `status === 'ready'` ya, así que la pill es ruido. Fix: quitar pill y mostrar en su lugar el `format` (Tabla · Reporte · Dashboard) como pill neutra de metadato.
- [S2] Tipo icon `.type-icon.crm` para entregables no tiene sentido semántico (L.3592) — todos los entregables muestran el mismo ícono-marco "CRM" aunque el entregable sea un reporte. Fix: mapear `d.format` a iconos distintos (`i-file` reporte, `i-grid` tabla, `i-workflow` dashboard).
- [S3] El empty state (L.3586) menciona "⌘K" pero no explica qué significa para usuario nuevo. Fix: reemplazar por `.empty-state` canónico con CTA explícita "Pedir tarea a agente" + hint kbd.

### Dark (≥2 findings)
- [S1] La cita italic `"${d.request…}"` (L.3606) usa `color:var(--text-muted);font-style:italic` — en dark con `--text-muted` actual (#8A8278, 3.88:1) falla AA body. Son strings de 120 chars, body content real, no caption. Fix: endurecer a `--text-secondary` o aplicar el `--text-muted: #A49C90` del slice A.
- [S2] La pill-success "Listo" dark usa `--success` (#9BAD8C) sobre `rgba(success,0.15)` — en dark sobre el row-surface (#2A2824) el fondo rgba queda muy apagado (luminancia casi idéntica a bg-primary). Fix: subir opacidad del bg a 0.22 en dark (o crear `--color-success-bg` explícito — ver slice A C.1).

### i18n
- Hard-coded: "Entregables" (bandeja-tab L.3441, breadcrumb L.3484), "Tabla" (L.3598), "Reporte" (L.3598), "fuentes" (L.3603), "Listo" (L.3613), "Sin entregables pendientes. Pedile algo a un agente con ⌘K." (L.3586), "Reportes y análisis que pediste a tus agentes · listos para revisar" (L.3479). ≥3 cumplido.
- Overflow ES→EN→PT-BR: "Reportes y análisis que pediste a tus agentes · listos para revisar" (67ch) → "Reports and analyses you asked your agents for · ready to review" (63ch) → "Relatórios e análises que você pediu aos seus agentes · prontos para revisar" (76ch) — PT-BR desborda `page-subtitle`. "Listo" (5ch) → "Ready" (5ch) → "Pronto" (6ch) — pill OK.

### a11y (≥2 findings)
- [S1] La cita truncada en italic no tiene `title=""` ni `aria-describedby` — screen reader sólo lee el texto visible truncado, queda frase sin cerrar. Fix: `<div class="request-snippet" title="${d.request}" aria-label="Solicitud original: ${d.request}">`.
- [S2] El empty state (L.3586) no tiene `role="status"` ni landmark — si cambia de "lista con N" a "vacío" tras un filtro, el SR no lo anuncia. Fix: envolver en `<div role="status" aria-live="polite">` para anunciar cambios dinámicos.
- [S2] `.pill.pill-success.pill-dot` usa un `::before` o `::after` como "dot" pintado con color — sin texto. Si es decorativo (lo es, el text "Listo" ya carga la semántica) → `aria-hidden` implícito ya funciona por CSS pseudo, pero la pill entera merece `role="status"` para ser leída por SR como estado.

### Snippets (solo para S1)
```css
/* Fix request snippet con clamp visual */
.request-snippet {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-size: 12px;
  color: var(--text-muted);
  font-style: italic;
  margin-top: 6px;
  cursor: help;
}

/* Deliverable-row variant con acciones propias */
.deliverable-row {
  /* hereda de .draft-list-row */
}
.deliverable-row .deliverable-actions {
  display: flex;
  gap: var(--space-1, 4px);
}
.deliverable-row .deliverable-actions .icon-btn {
  width: 30px; height: 30px;
  border-radius: var(--radius-md, 6px);
}
.deliverable-row .format-pill {
  background: var(--bg-subtle);
  color: var(--text-secondary);
  font-size: 11px;
  padding: 2px 8px;
  border-radius: var(--radius-pill, 999px);
  font-weight: 500;
}
```

---

## Ruta 5 — `#/bandeja/alertas`

### Wireframe
Mismo shell + tabs bar (tab "Alertas" activo). Body: lista de `.draft-list-row` reutilizada con variantes — `.priority-indicator priority-high` si severity=warning, `.type-icon.crm` con `i-alert` pintado con color dinámico (`var(--warning)` o `var(--text-muted)` según severity). Subject + meta (agent pill coral + detail + separador + ago), div vacío `style="min-width:0"` como spacer (hack), pill de severity (warning/error/neutral) + botón secondary-sm con label dinámico `a.action`.

### Light (≥3 findings)
- [S1] La severity se pinta con `alert('Mock: ${a.action}')` en el botón (L.3643) — los labels ("Revisar" / "Bloquear" / "Ignorar" / etc.) son verbos heterogéneos sin visual consistency. Algunos son CTAs fuertes (bloquear = acción destructiva), otros secundarios (revisar = abrir). Fix: mapear `a.action` a variantes `.btn-danger` cuando sea "Bloquear/Revertir", `.btn-primary` cuando sea "Revisar/Ver", `.btn-ghost` cuando sea "Ignorar". **Línea ~3643.**
- [S1] El spacer `<div style="min-width:0"></div>` (L.3640) es un hack para rellenar la columna del confidence-block del grid template de `.draft-list-row`. No hay confidence en una alerta → la columna queda vacía visualmente. Fix: crear `.alert-row` como grid distinto (priority+icon · content · severity+action) sin columna fantasma, o reemplazar con el campo `a.detectedBy` (qué policy/agente disparó la alerta). **Línea ~3640.**
- [S2] El ícono de alert toma `color:var(--${severity==='warning'?'warning':'text-muted'})` (L.3629) inline — falla para severity=error que cae en el else y se pinta text-muted (gris) en vez de rojo. Fix: mapeo explícito error→`--error`, warning→`--warning`, info→`--info`, neutral→`--text-muted`.
- [S2] La pill de severity muestra `${a.severity}` literal (L.3642) — "warning", "error", "info" en inglés-técnico al usuario. Fix: traducir via `severityLabel(s)` a "Atención", "Crítica", "Informativa".
- [S3] La subtítulo "Los agentes detectaron algo que necesita tu atención" (L.3480) es cálida pero vaga. Fix: sumar contador dinámico: "${N} alertas · ${M} requieren acción".

### Dark (≥2 findings)
- [S1] `--warning` color del ícono en dark (#D0A66A) sobre `--bg-surface` (#2A2824) da 6.55:1 OK, pero el `.pill.pill-warning` con bg `rgba(184,138,74,0.15)` pierde definición — el contenedor de la pill sangra al fondo del row. Fix: pasar a `rgba(208,166,106,0.22)` en dark (slice A propone `--color-warning-bg` tokenizado).
- [S2] `.priority-indicator.priority-high` pintado con `--error` en dark (#B85555 → 3.13:1) es el primer elemento que el ojo ve en una alerta crítica y está subexpuesto. Fix: aplicar `--error: #D97070` de slice A (4.55:1).
- [S2] Las pills `.pill-error.pill-dot` dark con el dot que debería ser "alarma pulsante" no tienen animación — en dark, sin pulso, una alerta crítica se ve idéntica a una normal. Fix: `@keyframes pulse` en el `.pill-error.pill-dot::before` con `prefers-reduced-motion` fallback.

### i18n
- Hard-coded: "Alertas" (L.3445, 3484), "Los agentes detectaron algo que necesita tu atención" (L.3480), severity labels literales "warning/error/info" (L.3642), `a.action` string dinámico sin tabla (ej. "Revisar", "Bloquear"), empty state ausente. ≥3 cumplido pero la mayoría vienen de MOCK data inline.
- Overflow ES→EN→PT-BR: "Los agentes detectaron algo que necesita tu atención" (52ch) → "Your agents detected something that needs your attention" (54ch) → "Seus agentes detectaram algo que precisa da sua atenção" (55ch). Subtítulo OK en laptop 13". El caso malo: `a.detail` dinámico — si dice "Pricing fuera del rango acordado con Distribuidora del Norte SA de CV" (70ch) en ES, PT-BR lo estira y choca con el flex del row en 1280px.

### a11y (≥2 findings)
- [S1] La lista de alertas no tiene `role="log"` ni `aria-live="polite"` — si llega una alerta nueva mientras el user está en la tab, el SR no la anuncia. Fix: `<div class="draft-list" role="log" aria-live="polite" aria-label="Alertas recientes">`.
- [S1] El botón `a.action` (L.3643) tiene `onclick="alert('Mock: ${a.action}')"` sin `aria-label` de contexto — SR lee sólo el verbo ("Bloquear") sin el objeto ("Bloquear envío de Cotizador Marluvas"). Fix: `aria-label="${a.action} ${a.subject}"`.
- [S2] El ícono de alerta no tiene `role="img"` ni `aria-label` — para un elemento crítico como alerta, el ícono debería reforzar la semántica. Fix: `<svg role="img" aria-label="Alerta de ${severity}">`.

### Snippets (solo para S1)
```css
/* Fix grid propio para alert-row */
.alert-row {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: var(--space-3, 12px);
  align-items: center;
  padding: var(--space-3, 12px) var(--space-4, 16px);
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md, 6px);
  cursor: pointer;
  transition: all var(--duration-fast, 120ms) var(--ease-standard, ease);
}
.alert-row.sev-error { border-left: 3px solid var(--error); }
.alert-row.sev-warning { border-left: 3px solid var(--warning); }
.alert-row.sev-info { border-left: 3px solid var(--info); }

.alert-row .alert-actions {
  display: flex;
  gap: var(--space-2, 8px);
}

/* Pulse del dot de alerta crítica */
@keyframes fl-alert-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(184, 85, 85, 0.4); }
  50% { box-shadow: 0 0 0 6px rgba(184, 85, 85, 0); }
}
.pill-error.pill-dot::before {
  animation: fl-alert-pulse 1.8s var(--ease-standard, ease) infinite;
}
@media (prefers-reduced-motion: reduce) {
  .pill-error.pill-dot::before { animation: none; }
}

/* Mapeo action → variante button (a aplicar en JS) */
/* const actionVariant = { Revisar: 'btn-primary', Bloquear: 'btn-danger',
     Revertir: 'btn-danger', Ignorar: 'btn-ghost' }; */
```

---

## Ruta 6 — `#/bandeja/todo`

### Wireframe
Mismo shell + tabs bar con tab "Todo" activo. Body: concatenación literal de `renderBandejaAprobar() + renderBandejaEntregables() + renderBandejaAlertas()`, separados por dos `<h3>` hardcoded ("Entregables" · "Alertas") con margin-top 28px. No hay agrupación temporal, ni orden unificado, ni filtros específicos.

### Light (≥3 findings)
- [S1] La concatenación (L.3651) es literalmente 3 renders apilados — el user ve el toolbar de filtros de Aprobar (chips Correos/Cotizaciones/CRM) aunque esté en "Todo". Si filtra por "Cotizaciones", los filtros no aplican a Entregables ni Alertas y quedan visibles sin filtrar → estado inconsistente. Fix: en tab "todo" NO mostrar toolbar de filtros del tab "aprobar", o crear filtros cross-section (tipo + prioridad + agente). **Línea ~3651.**
- [S1] Los headers de sección "Entregables" y "Alertas" son `<h3 style="font-size:14px;font-weight:600">` inline, sin componente. No hay counter ("Entregables · 3"), no hay link "Ver sólo esto". Fix: crear `.section-header` con título + counter + link "Abrir tab" que navegue al tab específico. **Línea ~3651.**
- [S2] No hay separación temporal en "Todo". Un draft de hace 4 min se mezcla con un entregable de ayer y una alerta de la semana pasada. Un feed unificado exige ordenamiento por tiempo. Fix: agrupar por "Hoy / Ayer / Esta semana / Anteriores" con sticky headers.
- [S2] El tab "Todo" muestra `counts.todo = drafts + deliverables + alerts` — count correcto numéricamente pero sin signal de urgencia. Un usuario ve "42" sin saber si son 2 drafts críticos o 40 logs. Fix: componer count con badges ("12 críticos · 30 total") o priorizar por severidad máxima.
- [S3] "Todo" como label no comunica feed — confunde con "TODO list" en inglés para bilingües. Fix: renombrar a "Actividad" o "Feed" (más clara la semántica de agregación).

### Dark (≥2 findings)
- [S1] Los 3 sub-bloques concatenados no tienen separadores visuales entre sí — en light funciona por los h3 "Entregables"/"Alertas"; en dark, como `--text-secondary` pierde contraste contra el bg, los headers se pierden y el feed se lee como lista continua. Fix: usar `.section-divider` con `border-top: 1px solid var(--border-subtle)` + padding-top y h3 de mayor peso visual.
- [S2] `--border-subtle` dark (#3D3A34) sobre surface da 1.30:1 (slice A E.1) — insuficiente para separar secciones en feed largo. Fix: aplicar el `#4A463F` propuesto en slice A E.3 o reforzar con `box-shadow` interior.

### i18n
- Hard-coded: "Todo" (L.3448, 3484), "Entregables" y "Alertas" como h3 inline (L.3651), "Toda la actividad reciente de tus agentes — outbound, deliverables y alertas" (L.3481). La palabra "deliverables" está mezclada en el subtítulo ES — anglicismo sin traducir. ≥3 cumplido.
- Overflow ES→EN→PT-BR: "Toda la actividad reciente de tus agentes — outbound, deliverables y alertas" (77ch) → "All recent activity from your agents — outbound, deliverables and alerts" (72ch) → "Toda a atividade recente dos seus agentes — saída, entregáveis e alertas" (73ch). El subtítulo ya es demasiado largo en ES.

### a11y (≥2 findings)
- [S1] No hay `aria-label` ni `role="feed"` en el contenedor concatenado — screen reader lee 3 listas sin jerarquía clara. Fix: `<div role="feed" aria-labelledby="todo-title" aria-busy="false">` en el wrapper, con `<section aria-labelledby="drafts-h">` y `<section aria-labelledby="deliverables-h">` para cada segmento.
- [S2] Los h3 "Entregables"/"Alertas" son `<h3>` — si el page-title es h1 y los widget-titles son h3 en otras rutas, se pierde jerarquía. Fix: estos deberían ser h2 (secciones de page), no h3 (widgets).
- [S2] El toolbar de filtros heredado de "aprobar" sigue focusable en "todo" aunque no aplique a las secciones 2 y 3 — confuso para keyboard-only users. Fix: deshabilitar o esconder en tab "todo".

### Snippets (solo para S1)
```css
/* Section header unificado para feed agregado */
.section-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding: var(--space-3, 12px) 0 var(--space-2, 8px);
  border-top: 1px solid var(--border-subtle);
  margin-top: var(--space-6, 24px);
}
.section-header h2 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--space-2, 8px);
}
.section-header .section-count {
  font-size: 12px;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
  font-weight: 500;
}
.section-header .section-open {
  font-size: 12px;
  color: var(--coral-text, var(--coral-primary));
  display: inline-flex;
  align-items: center;
  gap: var(--space-1, 4px);
  cursor: pointer;
}

/* Time-bucket sticky headers */
.feed-bucket {
  position: sticky;
  top: 56px;
  background: var(--bg-primary);
  padding: var(--space-2, 8px) 0;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--text-muted);
  z-index: 10;
  border-bottom: 1px solid var(--border-subtle);
}
```

---

## Ruta 7 — `#/agentes`

### Wireframe
Shell estándar + page-header con H1 "Agentes" + subtítulo "Roster · Shadow Mode · pipeline de graduación" + 2 CTAs derecha ("Desde template" + "Nuevo agente"). Debajo `.pipeline-bar` con 3 stages clickables (Activos · Shadow · Archivados), cada stage con label+icono + count tabular + descripción. Row de filtros: "Viendo" + chip "Todos (N)". Grid de `.agent-card` (por default 2 columnas): head con nombre + pill estado + rol + `.agent-icon-lg` (iniciales); si shadow → shadow-progress-wrap con barra de 14 días; 4 `.agent-metric` (Runs · Aprob. · Confianza · Evid. avg); footer con conn-badges + 2 botones (editar + Graduar/Pausar).

### Light (≥3 findings)
- [S1] El pill de estado (L.3835-3836) sólo distingue "Shadow" (warning) vs "Activo" (success) — 2 estados, pero slice A (project_faberloom_agents_design) define 4 estados con verbos humanos: Verde-Activo "Listo y operando" · Azul-Aprendiendo "Ajustando respuestas" · Ámbar-Esperando aprobación · Gris-Pausado. El roster pierde el estado "Aprendiendo" (Azul) y "Pausado" (Gris) — es el mapeo canónico de Autonomy Ladder. Fix: crear `.pill-learning` (Azul info) + `.pill-paused` (neutral) y derivar del campo `a.state`, no del `a.mode`. **Línea ~3835.**
- [S1] El CTA "Graduar" (L.3881) de un shadow-agent es destructivo (promoción a Active con efectos side) sin modal de confirmación ni review del shadow-performance. Slice A dice: "Candidate → Active → Archived" con review humano + eval. Un click simple rompe la regla. Fix: abrir modal "¿Graduar ${name}?" con 3 KPIs (precisión contra humano, # runs, drift) + checkbox "He revisado los gold samples candidatos". **Línea ~3881.**
- [S2] Las 4 métricas (L.3853-3869) son idénticas en visual para activos y shadow, pero en shadow las métricas importan diferente: "Aprob." no tiene sentido en shadow (no hay aprobaciones, hay comparaciones). Fix: variante `.agent-metrics.shadow` que muestre "Precisión vs. humano · # runs · Drift · Excepciones" en vez de los 4 genéricos.
- [S2] `.agent-icon-lg` con iniciales (L.3840) es genérico — pero slice A brand atmosphere pide device distintivo por agente (el `trigger_word` de cada AgentSpec). Fix: usar iniciales + color coral-tint al hover + tooltip con `trigger_word` ("Escribí `@cotiza` en cualquier lado").
- [S3] `.pipeline-bar` stages son clickables pero el stage activo sólo cambia `border` — poca signal visual. Y "Activos" y "all" comparten el estilo activo (L.3902: `agentesStage === 'all' || agentesStage === 'active'`), confuso. Fix: estilos distintos para "all" (ligero + chevron hacia todos los stages) vs "active" (coral accent).

### Dark (≥2 findings)
- [S1] `.shadow-progress-fill` usa color coral o warning según implementación — la `shadow-progress-bar` de fondo es `--bg-subtle` (#34312C en dark, 1.10:1 sobre bg-primary). La barra total se ve casi invisible salvo por el fill. Fix: `--bg-subtle` dark para progress-track es insuficiente; usar `--bg-hover` (#3D3A34) o agregar `box-shadow: inset 0 0 0 1px var(--border-subtle)`.
- [S2] `.pill.pill-warning.pill-dot` "Shadow" (L.3835) — en dark el dot ámbar (#D0A66A) contra el bg-tint queda OK, pero el label "Shadow" sin contexto no comunica el estado. Un user nuevo ve "ámbar" y piensa "error/pendiente". Fix: extender label a "Shadow · evaluando" en dark o tooltip siempre visible.
- [S2] `.agent-card.shadow` tiene un tratamiento visual distinto (fondo levemente apagado), en dark se confunde con un card "archivado/deshabilitado". Fix: cambiar el modifier a un `border-left: 3px solid var(--warning)` en vez de opacity/bg diferente.

### i18n
- Hard-coded: "Agentes" (L.3892), "Roster · Shadow Mode · pipeline de graduación" (L.3893), "Desde template" (L.3896), "Nuevo agente" (L.3897), "Activos" (L.3905), "Operando draft-first · acciones requieren aprobación humana" (L.3908), "Shadow · en evaluación" (L.3913), "Procesan pero no publican · miden precisión contra decisiones humanas" (L.3916), "Archivados" (L.3921), "Pausados o descontinuados · historial conservado para audit" (L.3924), "Viendo" (L.3929), "Todos" (L.3930), "Sin agentes en esta etapa." (L.3934), "Shadow" (L.3835), "Activo" (L.3836), "Shadow mode · evaluación" (L.3846), "Próximo a graduar a Activo" (L.3850), "Acumulando runs para evaluar" (L.3850), "Runs / Aprob. / Confianza / Evid. avg" (L.3856, 3860, 3864, 3868), "Graduar" (L.3881), "Pausar" (L.3882). ≥3 cumplido.
- Overflow ES→EN→PT-BR: "Operando draft-first · acciones requieren aprobación humana" (55ch) → "Running draft-first · actions require human approval" (52ch) → "Operando rascunho-primeiro · ações exigem aprovação humana" (57ch). Cabe en stage-desc. El caso duro: "Procesan pero no publican · miden precisión contra decisiones humanas" (65ch) → en PT-BR "Processam mas não publicam · medem precisão contra decisões humanas" (66ch) — ya rompe a 2 líneas en stage-desc, crea desbalance vertical entre stages. Arreglar con `max-width` + line-clamp de 2 líneas.

### a11y (≥2 findings)
- [S1] `.agent-card` es `onclick` div (L.3829) sin role ni keyboard — mismo problema sistémico que rutas anteriores. Con adición: el card contiene 2 botones internos que hacen `stopPropagation()` — keyboard user no puede distinguir entre "abrir card" y "graduar/pausar". Fix: convertir card en `<a href>` con "Graduar/Pausar" como botones explícitos en footer (no como children clickables dentro de un link — viola HTML: no se pueden anidar controls).
- [S1] `.pipeline-bar .pipeline-stage` son `<div onclick>` (L.3902, 3910, 3918) sin `role="tab"` ni `aria-selected` — funcionalmente son tabs de filtro de un roster. Fix: `<button class="pipeline-stage" role="tab" aria-selected="${stage===current}" aria-controls="agent-roster">`.
- [S2] `.shadow-progress-bar` no tiene `role="progressbar"` ni `aria-valuenow/valuemin/valuemax` — SR no comunica "7 de 14 días". Fix: `<div role="progressbar" aria-valuenow="${days}" aria-valuemin="0" aria-valuemax="${target}" aria-label="Shadow mode progress">`.
- [S2] `conn-badge` (L.3874) es un span con 1 char — sin `aria-label`, SR lee "G" "H" "D". Fix: `title="Gmail"` + `aria-label="Conectado a Gmail"`.

### Snippets (solo para S1)
```css
/* 4 estados canónicos — mapea project_faberloom_agents_design */
.pill-active { background: rgba(122, 142, 109, 0.15); color: var(--success); }
.pill-learning { background: rgba(90, 107, 124, 0.15); color: var(--info); }
.pill-waiting { background: rgba(184, 138, 74, 0.15); color: var(--warning); }
.pill-paused { background: var(--bg-subtle); color: var(--text-muted); }
[data-theme="dark"] .pill-active { background: rgba(155, 173, 140, 0.18); }
[data-theme="dark"] .pill-learning { background: rgba(126, 144, 160, 0.18); }
[data-theme="dark"] .pill-waiting { background: rgba(208, 166, 106, 0.22); }
[data-theme="dark"] .pill-paused { background: var(--bg-subtle); color: var(--text-muted-weak, var(--text-muted)); }

/* Agent card sin clickable-parent anti-patrón */
.agent-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg, 8px);
  box-shadow: var(--shadow-sm);
  padding: var(--space-4, 16px);
  display: flex;
  flex-direction: column;
  gap: var(--space-3, 12px);
  transition: all var(--duration-fast, 120ms) var(--ease-standard, ease);
}
.agent-card:hover { box-shadow: var(--shadow-md); border-color: var(--border-strong); }
.agent-card.shadow { border-left: 3px solid var(--warning); }
.agent-card .agent-title-link {
  color: var(--text-primary);
  text-decoration: none;
  font-weight: 600;
  outline: none;
}
.agent-card .agent-title-link:focus-visible { box-shadow: var(--focus-ring); }

/* Pipeline-bar como tablist */
.pipeline-bar { display: flex; gap: var(--space-3, 12px); margin-bottom: var(--space-4, 16px); }
.pipeline-stage {
  flex: 1;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md, 6px);
  padding: var(--space-3, 12px) var(--space-4, 16px);
  cursor: pointer;
  outline: none;
  transition: all var(--duration-fast, 120ms) var(--ease-standard, ease);
  text-align: left;
}
.pipeline-stage:hover { background: var(--bg-subtle); }
.pipeline-stage[aria-selected="true"] {
  border-color: var(--coral-primary);
  background: var(--coral-tint);
}
.pipeline-stage:focus-visible { box-shadow: var(--focus-ring); }

/* Progress bar de shadow con role semántico */
.shadow-progress-bar {
  height: 6px;
  background: var(--bg-hover);
  border-radius: var(--radius-pill, 999px);
  overflow: hidden;
  box-shadow: inset 0 0 0 1px var(--border-subtle);
}
.shadow-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--warning) 0%, var(--success) 100%);
  transition: width var(--duration-slow, 320ms) var(--ease-standard, ease);
}
```

---

## Addendum a Slice A

Deudas de tokens detectadas en rutas 1-7 NO cubiertas en slice A:

- `--fs-micro-caps` (10px, weight 600, letter-spacing 0.05em, uppercase) — usado en `.feed-bucket` (time headers de ruta 6) y potencialmente `.stage-label` de pipeline. Slice A tiene `--fs-micro` pero sin las reglas de caps+letter-spacing.
- `--border-coral-strong` (`2px solid var(--coral-primary)`) — slice A define `--border-coral` como color; necesita variante para `.pricing-card.featured` (ruta 1) que hardcodea `1.5px solid var(--coral-primary)` y `.pipeline-stage[aria-selected]` (ruta 7) que necesita 2px para signal clara.
- `.section-header` + `.section-count` + `.section-open` — componente propuesto para ruta 6 (feed agregado "Todo") + dashboard widgets (ruta 2). No es una variante de card, es un "header of grouped list". Proponer añadir al component library de slice A §C.2.
- `.progressbar` canónico — slice A no tiene progress-bar como component. Al menos 2 lugares la usan (shadow-progress-bar en ruta 7, y hay otros en Workflow/Agent Console). Definir `--progress-track-bg`, `--progress-fill-bg`, `--progress-height` como tokens.
- `--link-decoration-hover-offset` (`text-underline-offset: 2px`) — slice A lo propone en link-base pero no tokeniza el offset. Agregar `--link-ul-offset: 2px` para que `a:hover` sea consistente.
- `pulse` keyframe para `.pill-error.pill-dot` en alertas críticas (ruta 5). Slice A cubre `skeleton` y `confidence-ring` stroke-dashoffset pero no el pulse semántico de alertas. Agregar `@keyframes fl-alert-pulse` con `prefers-reduced-motion` fallback.
- `.filter-chip[aria-pressed="true"]` como estado semántico — slice A propone `.tab[aria-selected]` pero no tipifica filter-chips como toggles. Son semánticamente distintos de tabs y distintos de buttons-group. Definir variante.
- `severityLabel()` helper + token `--color-severity-{error|warning|info|neutral}-text` + `-bg` con contraste AA asegurado en dark (slice A C.1 cubre warning-bg/success-bg/error-bg pero sin el par text+bg verificado).
