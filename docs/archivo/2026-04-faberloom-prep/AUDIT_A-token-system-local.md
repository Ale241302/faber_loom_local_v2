# AUDIT_A — Token system + dark mode

## Sección A · Executive summary

- **Estado general — usable para demos internas, no listo para design partners.** El sistema de tokens está bien cimentado (paleta editorial-warm coherente, light mode pulido, arquitectura `:root[data-theme]` limpia en líneas 15-76) pero le faltan 3 capas clave que un demo con buyer exige: tokens de spacing/radius/typography nombrados, estados empty/loading/error, y media queries (no hay ni un `@media` en 5801 líneas). **S1**.
- **Fortalezas visibles.** Paleta Claude-adyacente bien ejecutada; `--evidence` como color forense exclusivo es el hook de diferenciación más fuerte del sistema (líneas 30-31, 61-62); wordmark split-color `Faber` + `loom` funciona; pills/buttons/cards consistentes vía variables; `font-variant-numeric: tabular-nums` aplicado correctamente en métricas (líneas 872, 889, 1023, 1024, 1399-1400, 2307).
- **Deudas críticas (S1 — blocker demo).** (1) `--ico` hardcodea `stroke-width: 2` (línea 1812) contradiciendo el brand memo que pide 1.5; (2) `--text-muted` en dark (3.88:1 sobre surface) falla AA 4.5:1 para cuerpo, y se usa en `.activity-body .meta`, `.agent-mini-row .role`, `.footer-brand p`, capitions — hay que bajar un tono o restringirlo a 14px+ semibold con regla explícita; (3) `--evidence` en dark (2.66:1) rompe AA — es el color signature del producto, no puede fallar; (4) cero `@media` queries: el prototipo asume 1400px, colapsa bajo laptop 13".
- **Deudas pre-launch (S2).** Sin skeleton/empty/loading states; sin `prefers-reduced-motion`; iconografía mezcla viewBox 24 (bueno) con stroke-width 2 del `.ico` base y 1.5 de un SVG hardcoded en workflow (línea 1602), rompe consistencia; token `--border-coral` declarado en el brand memo NO existe en CSS; tipografía carece de escala nombrada (se tira `font-size: 13px` 31 veces literal); sin tokens de radius/spacing nombrados.
- **Show-stoppers antes del demo con los 3 design partners LatAm.** (a) Responsive hasta 1280px mínimo (buyer HSE abre en pantalla secundaria o ultrawide); (b) contraste en dark del `--evidence` y `--text-muted` (el producto se llama "forense", no puede fallar contraste del color de provenance); (c) focus-visible ring consistente (solo existe en inputs, no en botones ni links — fail WCAG 2.4.7); (d) stroke-width de íconos unificado a 1.5 para respetar brand atmosphere editorial.

### Scorecard · 12 dimensiones

| # | Dimensión | Score | Justificación en una línea |
|---|---|---|---|
| 1 | Jerarquía visual | 7 | Cards + wordmark + tabs bien jerarquizados; falla en escala tipográfica improvisada (14px/13px/12px/11px sin nombre). |
| 2 | Microinteracciones | 6 | Transiciones 120-200ms correctas, pero cero feedback de "acción ejecutada" (toast, checkmark animado), sin loading states. |
| 3 | Empty/Loading/Error states | 2 | No existe ni una clase `.empty-state`, `.skeleton`, `.spinner`, `.error-state` en todo el archivo. Show-stopper. |
| 4 | Dark mode parity | 6 | Paleta invertida bien, pero `--evidence`, `--text-muted` y `--error` fallan AA 4.5:1; shadows pierden legibilidad. |
| 5 | Light mode polish | 8 | Cream+coral editorial, shadows 3-layer correctos, bordes cálidos. Bien resuelto. |
| 6 | WCAG 2.1 AA | 5 | Body text pasa; `--text-muted` marginal (3.36/3.79), `--evidence` dark falla, sin `focus-visible` global, sin roles ARIA. |
| 7 | i18n readiness | 4 | `lang="es"` correcto; pero strings inline en JS (`renderDashboard`), no hay tabla `STRINGS`, botones de ancho fijo rompen con PT-BR más largo. |
| 8 | Responsive | 1 | Cero `@media`. `grid-template-columns: 240px 1fr` + `max-width: 1400px` rígido. Irreparable sin sprint dedicado. |
| 9 | Iconografía | 6 | Sprite Feather-style coherente (viewBox 24, stroke currentColor), pero stroke-width inconsistente (2 en `.ico`, 1.5 en workflow, 2 implícito en sprite). |
| 10 | Tipografía | 6 | Georgia italic + Inter + JetBrains Mono aplicados bien; escala numérica (10/11/12/13/14/15/16/17/18/22/32/36/40/48/56/72) sin nombrar. |
| 11 | Status semantics | 8 | 4 estados (Verde/Azul/Ámbar/Gris) del Autonomy Ladder mapeados a success/info/warning/neutral; falta badge "Aprendiendo" (Azul). |
| 12 | IA/navegación | 7 | 11 rutas hash-based claras; sidebar sticky; Admin separado de Settings bien ejecutado; falta breadcrumb en Skill Studio y keyboard nav global. |

---

## Sección C · Patterns globales y sistema

### C.1 · Token gaps

Auditoría de `:root[data-theme="light"]` (líneas 15-45) y `:root[data-theme="dark"]` (líneas 46-76) contra el brand memo y contra usos repetidos en el CSS.

| Token | Light actual | Dark actual | Propuesto | Uso / justificación |
|---|---|---|---|---|
| `--border-coral` | missing | missing | `#C96442` light · `#D97757` dark | Brand memo la declara; se hardcodea `1.5px solid var(--coral-primary)` en `.pricing-card.featured` (línea 635) y usos similares — normalizar. |
| `--radius-sm` | missing (literal `4px`) | missing | `4px` | Se usa literal en `.kbd` (2412), inputs pequeños. |
| `--radius-md` | missing (literal `6px`) | missing | `6px` | Usado 10+ veces literal (inputs, btn, pills). |
| `--radius-lg` | missing (literal `8px`) | missing | `8px` | Cards, launcher-agent-opt. |
| `--radius-xl` | missing (literal `10-12px`) | missing | `12px` | `.launcher-modal` (2333), `.avatar-dropdown` (1832). |
| `--radius-pill` | missing (literal `10px` / `999px`) | missing | `999px` | Pills y tab-counts deberían usarlo. |
| `--space-1` | missing | missing | `4px` | Se usa literal en ~60 declaraciones `gap/padding/margin`. |
| `--space-2` | missing | missing | `8px` | idem. |
| `--space-3` | missing | missing | `12px` | idem. |
| `--space-4` | missing | missing | `16px` | idem. |
| `--space-6` | missing | missing | `24px` | idem. |
| `--space-8` | missing | missing | `32px` | idem (`page-wrap` padding). |
| `--space-12` | missing | missing | `48px` | Hero padding, section gaps. |
| `--space-16` | missing | missing | `64px` | Landing sections. |
| `--font-display` | missing | missing | `'Georgia', 'Source Serif', serif` | Se repite literal 6+ veces (líneas 94, 130, etc.). |
| `--font-ui` | missing | missing | `'Inter', -apple-system, sans-serif` | Repetido en body + `.launcher-row` (2394). |
| `--font-mono` | missing | missing | `'JetBrains Mono', 'Menlo', monospace` | Usado literal 4 veces. |
| `--text-on-coral` | missing (hardcoded `#FFFFFF`) | missing | `#FFFFFF` | Brand memo lo declara; se usa literal en `.btn-primary` (línea 160) y `.pricing-card.featured .pricing-cta` (678-682). |
| `--focus-ring` | missing | missing | `0 0 0 3px var(--coral-tint)` light · `0 0 0 3px rgba(217,119,87,0.35)` dark | Inline en inputs (115), no en botones/links — fail WCAG 2.4.7. |
| `--duration-fast` | missing (literal `120ms`) | missing | `120ms` | 14 usos literales. |
| `--duration-base` | missing (literal `150-200ms`) | missing | `200ms` | Mezcla 150 / 200ms sin criterio. |
| `--duration-slow` | missing (literal `400ms`) | missing | `320ms` | `confidence-ring` usa 400ms (1228). |
| `--ease-standard` | missing (literal `ease`) | missing | `cubic-bezier(.2,0,0,1)` | Todo el CSS usa `ease` nativo; cambiar por curva consistente con brand editorial. |
| `--shadow-focus` | missing | missing | `0 0 0 3px var(--coral-tint)` | Necesario para focus-visible. |
| `--z-dropdown` | missing (literal `1000`) | missing | `1000` | |
| `--z-modal` | missing (literal `2000`) | missing | `2000` | `.launcher-backdrop` (2322). |
| `--z-toast` | missing | missing | `3000` | No existe toast aún; reservar antes del sprint 2. |
| `--color-warning-bg` | missing (inline `rgba(184,138,74,0.15)`) | missing (idem) | `rgba(184,138,74,0.15)` / `rgba(208,166,106,0.2)` dark | `pill-warning` (198), `activity-dot.policy` (869), `kpi-card.kpi-warning::before` (795) duplican la misma rgba a mano. |
| `--color-success-bg` | missing (rgba repetida) | missing | idem | `pill-success` (197), `activity-dot.success` (868). |
| `--color-error-bg` | missing | missing | `rgba(139,47,47,0.08)` / `rgba(184,85,85,0.18)` dark | `.btn-danger:hover` (179), `.admin-banner` (1875), `pill-error` (199). |
| `--bg-overlay` | missing (literal `rgba(0,0,0,0.3)`) | missing | `rgba(31,30,28,0.45)` / `rgba(0,0,0,0.65)` dark | Brand memo lo declara; `.launcher-backdrop` (2320) usa `rgba(0,0,0,0.3)` — inconsistente con light cream theme. |

### C.2 · Component library implícita

Patrones repetidos detectados. Canónicos propuestos, con variantes y snippet pegable.

#### 1. Status Pill (`.pill`)
Encontrado líneas 186-207. Variantes: `success·warning·error·info·neutral·coral·evidence` + modifier `.pill-dot`.
```html
<span class="pill pill-success pill-dot">Activo</span>
<span class="pill pill-warning">Esperando</span>
```
Gap: falta variante `.pill-learning` (Azul del Autonomy Ladder). Proponer:
```css
.pill-learning { background: rgba(90, 107, 124, 0.15); color: var(--info); }
```

#### 2. KPI card (`.kpi-card`)
Líneas 776-823. Tiene `::before` de 3px coral para el accent lateral, variantes por semántica (`kpi-success`, `kpi-warning`, `kpi-evidence`). Patrón sólido. Falta variante `.kpi-error` simétrica:
```css
.kpi-card.kpi-error::before { background: var(--error); }
```

#### 3. Generic card (`.card`)
Líneas 343-360. Variante implícita `.card-evidence` (border-left 3px evidence, ver `.draft-card` 1152-1157 que replica el patrón ad-hoc). Normalizar:
```html
<article class="card card-evidence">
  <header class="card-header"><h3>Título</h3></header>
  <div class="card-body">…</div>
</article>
```
```css
.card { background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); }
.card-evidence { border-left: 3px solid var(--evidence); }
.card-coral { border-left: 3px solid var(--coral-primary); }
.card-warning { border-left: 3px solid var(--warning); }
```

#### 4. Tab-bar (`.tabs`)
Dos implementaciones divergentes: `.bandeja-tabs` (2279-2312) y `.skill-tab-bar` (línea 4754 ref, referenciado en JS). Normalizar a un solo componente:
```html
<nav class="tabs" role="tablist">
  <button class="tab active" role="tab" aria-selected="true">Para aprobar <span class="tab-count">4</span></button>
  <button class="tab" role="tab">Entregables <span class="tab-count">12</span></button>
</nav>
```
```css
.tabs { display: flex; gap: 2px; border-bottom: 1px solid var(--border-subtle); }
.tab { padding: 10px 14px; font-size: 13px; font-weight: 500; color: var(--text-secondary); border-bottom: 2px solid transparent; cursor: pointer; transition: all var(--duration-fast) var(--ease-standard); display: inline-flex; align-items: center; gap: 6px; background: none; border-top: none; border-left: none; border-right: none; }
.tab:hover { color: var(--text-primary); }
.tab[aria-selected="true"], .tab.active { color: var(--coral-primary); border-bottom-color: var(--coral-primary); }
.tab:focus-visible { outline: none; box-shadow: var(--focus-ring); border-radius: var(--radius-sm); }
.tab-count { background: var(--bg-subtle); padding: 1px 7px; border-radius: var(--radius-pill); font-size: 11px; font-variant-numeric: tabular-nums; }
.tab[aria-selected="true"] .tab-count, .tab.active .tab-count { background: var(--coral-tint); color: var(--coral-primary); }
```

#### 5. Drawer (`.drawer`)
Sólo implementado como `.evidence-drawer` (1151-1228). Generalizar:
```html
<aside class="drawer drawer-evidence" aria-label="Evidencia de procedencia">
  <header class="drawer-header"><h4>Fuentes usadas</h4><button class="drawer-close" aria-label="Cerrar"><svg class="ico"><use href="#i-x"/></svg></button></header>
  <div class="drawer-body">…</div>
</aside>
```
```css
.drawer { background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); box-shadow: var(--shadow-md); display: flex; flex-direction: column; }
.drawer-evidence { border-left: 3px solid var(--evidence); }
.drawer-header { padding: 14px 16px; border-bottom: 1px solid var(--border-subtle); display: flex; justify-content: space-between; align-items: center; }
.drawer-body { padding: 14px 16px; overflow-y: auto; }
```

#### 6. Modal (`.modal`)
Sólo existe `.launcher-modal` (2328-2336) + `.launcher-backdrop` (2317). Generalizar:
```html
<div class="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <div class="modal">
    <header class="modal-header"><h3 id="modal-title">Título</h3></header>
    <div class="modal-body">…</div>
    <footer class="modal-footer">…</footer>
  </div>
</div>
```
```css
.modal-backdrop { position: fixed; inset: 0; background: var(--bg-overlay); backdrop-filter: blur(2px); z-index: var(--z-modal); display: flex; align-items: center; justify-content: center; padding: var(--space-6); }
.modal { width: min(640px, 100%); background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-xl); box-shadow: var(--shadow-lg); overflow: hidden; max-height: 90vh; display: flex; flex-direction: column; }
.modal-header { padding: var(--space-4) var(--space-6); border-bottom: 1px solid var(--border-subtle); }
.modal-body { padding: var(--space-4) var(--space-6); overflow-y: auto; }
.modal-footer { padding: var(--space-3) var(--space-6); border-top: 1px solid var(--border-subtle); background: var(--bg-subtle); display: flex; justify-content: flex-end; gap: var(--space-2); }
```

#### 7. Empty state (`.empty-state`) — S1, NO EXISTE
Crear componente. Aplicable a bandeja vacía, listado de agentes, logs, audit trail, workflow sin nodos.
```html
<div class="empty-state">
  <svg class="empty-state-icon"><use href="#i-inbox"/></svg>
  <h4 class="empty-state-title">No hay borradores por aprobar</h4>
  <p class="empty-state-body">Cuando un agente proponga algo, aparecerá aquí.</p>
  <button class="btn btn-secondary btn-sm">Pedir tarea a un agente</button>
</div>
```
```css
.empty-state { text-align: center; padding: var(--space-12) var(--space-6); color: var(--text-secondary); display: flex; flex-direction: column; align-items: center; gap: var(--space-3); }
.empty-state-icon { width: 40px; height: 40px; color: var(--text-muted); stroke-width: 1.5; }
.empty-state-title { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.empty-state-body { font-size: 13px; max-width: 360px; line-height: 1.55; }
```

#### 8. Skeleton (`.skeleton`) — S1, NO EXISTE
Respeta `prefers-reduced-motion`.
```css
.skeleton { background: linear-gradient(90deg, var(--bg-subtle) 0%, var(--bg-hover) 50%, var(--bg-subtle) 100%); background-size: 200% 100%; animation: fl-skel 1.2s ease-in-out infinite; border-radius: var(--radius-md); }
.skeleton-text { height: 12px; margin-bottom: 6px; border-radius: var(--radius-sm); }
.skeleton-title { height: 18px; width: 60%; margin-bottom: var(--space-3); }
.skeleton-avatar { width: 32px; height: 32px; border-radius: 50%; }
@keyframes fl-skel { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
@media (prefers-reduced-motion: reduce) { .skeleton { animation: none; background: var(--bg-subtle); } }
```

#### 9. Toast / notification (`.toast`) — S2, NO EXISTE
Reservar token y clase antes del sprint 2 (draft aprobado → toast).
```css
.toast-stack { position: fixed; bottom: var(--space-6); right: var(--space-6); z-index: var(--z-toast); display: flex; flex-direction: column; gap: var(--space-2); }
.toast { background: var(--bg-surface); border: 1px solid var(--border-subtle); border-left: 3px solid var(--success); border-radius: var(--radius-md); padding: var(--space-3) var(--space-4); box-shadow: var(--shadow-md); font-size: 13px; min-width: 280px; max-width: 420px; display: flex; gap: var(--space-2); align-items: flex-start; }
.toast-error { border-left-color: var(--error); }
.toast-warning { border-left-color: var(--warning); }
.toast-evidence { border-left-color: var(--evidence); }
```

#### 10. Icon button (`.icon-btn`)
Existe (líneas 316-328). Añadir focus-visible:
```css
.icon-btn:focus-visible { outline: none; box-shadow: var(--focus-ring); border-radius: var(--radius-sm); }
```

### C.3 · Iconografía normalizada

Sprite actual (líneas 2428-2464): 33 símbolos, estilo Feather.

**Inventario**: `i-inbox · i-users · i-grid · i-plug · i-settings · i-home · i-workflow · i-bell · i-search · i-check · i-x · i-arrow-right · i-edit · i-sun · i-moon · i-eye · i-shield · i-alert · i-plus · i-key · i-anvil · i-sparkle · i-layers · i-book · i-link · i-puzzle · i-webhook · i-lock · i-database · i-trash · i-file · i-brain · i-play · i-copy`.

**Inconsistencias detectadas**:
- `viewBox="0 0 24 24"` uniforme — **OK**.
- `stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"` uniforme — **OK**.
- **S2**: el sprite NO declara `stroke-width` por símbolo; hereda del CSS `.ico { stroke-width: 2 }` (línea 1812) — brand memo pide 1.5 para look editorial.
- **S2**: `i-puzzle` (2455) es estilo fill path (heavier) mientras el resto es stroke line — rompe el sistema visualmente. Sustituir por versión stroke-only.
- **S3**: `i-anvil` (2450) es un ícono custom, OK de mantener, pero visualmente más "pesado" que los Feather por cantidad de subpaths — considerar simplificar.
- **S3**: `i-sparkle` (2451) se ve como estrella genérica, puede mezclarse con brand spark de Claude — sustituir por glyph custom más "loom" (ej: lanzadera horizontal pequeña) o mantener pero no usarla como logo.
- **S3**: no hay ícono específico para evidence/provenance (se reutiliza `i-shield` en `activity-dot.evidence`). Agregar `i-quote-mark` o `i-annotation` para reforzar el device forense.

**Reglas de normalización propuestas**:
```css
.ico { width: 16px; height: 16px; stroke-width: 1.5; flex-shrink: 0; vertical-align: middle; }
.ico-xs { width: 12px; height: 12px; stroke-width: 1.75; } /* stroke sube al reducir tamaño */
.ico-sm { width: 14px; height: 14px; stroke-width: 1.5; }
.ico-lg { width: 20px; height: 20px; stroke-width: 1.5; }
.ico-xl { width: 32px; height: 32px; stroke-width: 1.25; } /* stroke baja al agrandar */
.ico-display { width: 48px; height: 48px; stroke-width: 1.25; } /* para empty-state hero icons */
```
Regla hard: todo `<symbol>` nuevo debe respetar viewBox 24 + currentColor + stroke-linecap/linejoin round. No introducir fill icons excepto en `i-play`, `i-grid` (ya usan shapes con fill-by-area) — y documentarlos como excepción en comment.

### C.4 · Typography scale

Escala encontrada en el CSS (valores literales, sin token). Propuesta de nombres y uso:

| Token | Font-size | Line-height | Letter-spacing | Weight | Familia | Uso / mapeo al HTML existente |
|---|---|---|---|---|---|---|
| `--fs-display` | 72px | 1.05 | -0.02em | 500 | Georgia italic | `.wordmark-xl` (141) — hero landing. |
| `--fs-h1` | 48px | 1.1 | -0.02em | 500 | Georgia italic | `.wordmark-lg` (140), landing hero h1 (422). |
| `--fs-h2` | 36px | 1.1 | -0.01em | 500-600 | Georgia italic (display) / Inter (UI) | `.how-cols h2` (580), `.pricing-price` (651), `.page-title` section (615). |
| `--fs-h3` | 32px | 1.1 | -0.02em | 500-600 | Inter | `.page-title` (765), `.kpi-card .kpi-value` (806), `.stats-row .stat-value` (545). |
| `--fs-h4` | 22px | 1.2 | -0.01em | 500-600 | Georgia italic / Inter | `.wordmark` (133), `.pricing-card h4` (641). |
| `--fs-h5` | 18px | 1.3 | 0 | 600 | Inter | `.hero-subtitle` (429), `.pricing-card .price .currency` (657). |
| `--fs-body-lg` | 16px | 1.5 | 0 | 400 | Inter | `.stats-row .stat-label` (525). |
| `--fs-body` | 15px | 1.5 | 0 | 500-600 | Inter | `.card-header h3` (360), `.launcher-head input` (2349), `.how-step-body h4` (602). |
| `--fs-body-sm` | 14px | 1.5 | 0 | 400-500 | Inter | Body base (85), inputs (104), `.page-subtitle` (770), `.btn` (152 `.btn-lg`). |
| `--fs-ui` | 13px | 1.4 | 0 | 500 | Inter | `.btn` (152), `.sidebar-nav-item` (250), `.breadcrumbs` (310), `.bandeja-tab` (2287), `.launcher-row` inputs (2391). |
| `--fs-ui-sm` | 12px | 1.4 | 0.01em | 500 | Inter | `.btn-sm` (181), `.pill` adj, `.agent-mini-row .metric` (888), `.hero-badge` (413). |
| `--fs-caption` | 11px | 1.4 | 0.01em-0.02em | 500-600 | Inter | `.pill` (192), `.tab-count` (2306), `.user-info .role` (294), `.activity-time` (872). |
| `--fs-micro` | 10px | 1.3 | 0.05em-0.08em | 600 | Inter | `.sidebar-section-label` (236), `.confidence-label` (1024), `.footer-col h5` (706), `.cta-button-text` (682). |

**Improvisaciones detectadas (S2)**:
- `font-size: 17px` aparece suelto (línea 552) — valor off-scale, debería ser 18px (body-lg) o colapsar a 16px.
- `font-size: 40px` (519) y `56px` (422) conviven — consolidar a `48px` (h1) + `72px` (display). Dejar 56px como `--fs-hero-override` solo si Alvaro lo exige en hero landing.
- `font-size: 15px` se usa 3 veces (360, 2349, 602) — definir como `--fs-body`.
- `.wordmark` base es 22px (133) y `.sidebar-brand .wordmark` lo redefine a 20px (233), `.footer-brand .wordmark` a 24px (703) — declarar variantes explícitas `--fs-wordmark-sm/md/lg` en vez de override.

### C.5 · Spacing scale

Confirmo la escala 4/8/12/16/24/32/48/64 como estándar del sistema. Añadir `--space-0` y `--space-20` para forro de layouts grandes.

| Token | Valor | Uso detectado |
|---|---|---|
| `--space-0` | 0 | Reset. |
| `--space-1` | 4px | `gap` iconos + labels (líneas 189, 205, 6), `padding` pills (190). |
| `--space-2` | 8px | Grid gaps cortos, padding btn-sm, gap sidebar nav. |
| `--space-3` | 12px | Padding tight, margin-bottom mb-3. |
| `--space-4` | 16px | Padding card medium, margin mb-4. |
| `--space-5` | 20px | Page section gap. |
| `--space-6` | 24px | Padding card large, margin mb-6, page gaps. |
| `--space-8` | 32px | `page-wrap` padding-x (756), section padding. |
| `--space-10` | 40px | Hero padding. |
| `--space-12` | 48px | Landing section padding. |
| `--space-16` | 64px | Landing mega-section. |
| `--space-20` | 80px | Hero padding-y (opcional). |

Regla: `padding` y `margin` nunca como literal — usar siempre `var(--space-N)`. `gap` en flex/grid también.

### C.6 · Motion tokens

Duraciones y easings encontrados (y usados inconsistentemente: 120 / 140 / 150 / 200 / 400 ms, todos con `ease`):

| Token | Valor | Uso | Respaldado por línea |
|---|---|---|---|
| `--duration-instant` | 80ms | Hovers de texto, tooltips. | — nuevo |
| `--duration-fast` | 120ms | Hovers de superficies, tabs, nav, filter-chips. | Líneas 252, 325, 856, 882, 936, 988, 1183, 1253, 1447, 1503, 1714, 1862, 1912, 2032, 2051, 2292, 2366. |
| `--duration-base` | 200ms | Theme switch, dropdown show/hide, transform. | Líneas 90, 1767, 1776. |
| `--duration-slow` | 320ms | Drawer open, modal entry, data-viz stroke-dashoffset. | Reemplaza el literal 400ms de `confidence-ring` (1228) — 320ms se siente editorial, no ansioso. |
| `--duration-deliberate` | 480ms | Skeleton loop, "procesando" subtle indicators. | — nuevo. |
| `--ease-standard` | `cubic-bezier(.2,0,0,1)` | Default para entradas/salidas estándar. | Sustituye `ease` nativo (todos los usos). |
| `--ease-enter` | `cubic-bezier(0,0,.2,1)` | Elementos que entran a viewport (modal, toast). | — nuevo. |
| `--ease-exit` | `cubic-bezier(.4,0,1,1)` | Elementos que salen. | — nuevo. |
| `--ease-emphasized` | `cubic-bezier(.2,0,0,1.2)` | Overshoot sutil para éxito (checkmark drop). | Opcional, usar con moderación. |

**Respeto a `prefers-reduced-motion` (S1 — no existe en el archivo)**:
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
Excepción: mantener fade de theme switch a 200ms (feedback esencial). Si el usuario tiene reduce-motion, degradar `transform` → sólo `opacity`.

---

## Sección E · Dark mode audit

### E.1 · Token-by-token diff + contraste

Ratios computados con fórmula WCAG 2.1 (luminancia relativa con γ-expansion). Fila **pass?** evaluada contra target de uso (texto 4.5:1 para body, 3:1 para texto ≥18px/semibold ≥14px, 3:1 para UI/border/icono significativo).

| Token | Light value | Dark value | Uso canónico | Ratio light | Pass light | Ratio dark | Pass dark |
|---|---|---|---|---|---|---|---|
| `--bg-primary` | `#F4F1ED` | `#1F1E1C` | Body background. | (ref) | — | (ref) | — |
| `--bg-surface` | `#FFFFFF` | `#2A2824` | Cards, inputs. | (ref) | — | (ref) | — |
| `--bg-subtle` | `#EDE8DF` | `#34312C` | Hover, footers, filled states. | (ref) | — | (ref) | — |
| `--bg-hover` | `#E8E2D6` | `#3D3A34` | Btn-secondary hover. | (ref) | — | (ref) | — |
| `--text-primary` on surface | `#1F1E1C` | `#F4F1ED` | Cuerpo principal. | 16.66:1 | PASS | 13.07:1 | PASS |
| `--text-primary` on bg-primary | idem | idem | Page body. | 14.79:1 | PASS | 14.79:1 | PASS |
| `--text-secondary` on surface | `#5A544C` | `#B8B0A4` | Subtítulos, labels de KPI. | 7.48:1 | PASS | 6.85:1 | PASS |
| `--text-secondary` on bg-primary | idem | idem | Page-subtitle. | 6.64:1 | PASS | 7.76:1 | PASS |
| `--text-muted` on surface | `#8A8278` | `#8A8278` | Captions, meta, timestamps. | 3.79:1 | **FAIL 4.5** (PASS-LG) | 3.88:1 | **FAIL 4.5** (PASS-LG) |
| `--text-muted` on bg-primary | idem | idem | Page meta. | 3.36:1 | **FAIL 4.5** (PASS-LG) | 4.40:1 | PASS-LG, FAIL body |
| `--coral-primary` on surface | `#C96442` | `#C96442` | Links, icon accents, wordmark `.loom`. | 3.90:1 | FAIL 4.5 / PASS-LG / PASS-UI | 3.77:1 | FAIL 4.5 / PASS-LG / PASS-UI |
| `--coral-primary` on bg-primary | idem | idem | Links. | 3.46:1 | FAIL 4.5 / PASS-UI | 4.27:1 | PASS-LG, FAIL body |
| `--coral-hover` on surface | `#A84F33` | `#D97757` | Link hover, btn hover. | 5.48:1 | PASS | 4.71:1 | PASS |
| `--coral-hover` on bg-primary | idem | idem | Link hover. | 4.87:1 | PASS | 5.34:1 | PASS |
| `--text-on-coral` on coral-primary | `#FFFFFF` | `#FFFFFF` | Btn-primary label. | 3.90:1 | FAIL 4.5 / PASS-LG | 3.90:1 | FAIL 4.5 / PASS-LG |
| `--success` on surface | `#7A8E6D` | `#9BAD8C` | Pills, confidence-high. | 3.55:1 | PASS-LG | 6.13:1 | PASS |
| `--success` on bg-primary | idem | idem | Activity dot. | 3.15:1 | PASS-LG (borderline) | 6.94:1 | PASS |
| `--warning` on surface | `#B88A4A` | `#D0A66A` | Pills, node-policy, confidence-mid. | 3.10:1 | PASS-LG (borderline) | 6.55:1 | PASS |
| `--error` on surface | `#8B2F2F` | `#B85555` | Pills, btn-danger, priority-high. | 8.25:1 | PASS | 3.13:1 | PASS-LG |
| `--error` on bg-primary | idem | idem | Admin banner text. | 7.33:1 | PASS | 3.54:1 | PASS-LG |
| `--info` on surface | `#5A6B7C` | `#7A8A9B` | Pills, node-trigger. | 5.48:1 | PASS | 4.16:1 | PASS-LG |
| `--evidence` on surface | `#6E1F2B` | `#A84A5A` | Evidence pills, superíndices, card accents. | 11.09:1 | PASS | 2.66:1 | **FAIL** (S1) |
| `--evidence-tint` bg + `--evidence` text | `rgba(110,31,43,.08)` ≈ `#ECD9DD` | `rgba(168,74,90,.15)` ≈ `#362927` | Pill-evidence fill. | 8.20:1 | PASS | ~3.0:1 | PASS-LG / borderline |
| `--border-subtle` on bg-primary | `#D8D0C0` | `#3D3A34` | Separadores decorativos. | 1.36:1 | decorative OK | 1.47:1 | decorative OK |
| `--border-subtle` on bg-surface | idem | idem | Card borders. | 1.53:1 | decorative OK | 1.30:1 | decorative borderline — a subir |
| `--border-strong` on bg-primary | `#B8AE9C` | `#524E45` | Hover borders, active states. | 1.95:1 | FAIL UI 3:1 | 2.01:1 | FAIL UI 3:1 |
| `--node-agent` on surface | `#C96442` | `#D97757` | Workflow node icon + border. | 3.90:1 | PASS-UI | 4.71:1 | PASS |
| `--node-trigger` on surface | `#6B7280` | `#9CA3AF` | Workflow node icon. | ~4.5:1 | PASS | ~4.0:1 | PASS-LG |
| `--shadow-sm` visibility | `rgba(31,30,28,.04)+ .06` | `rgba(0,0,0,.3)` | Card elevation. | visible sobre cream | OK | apenas visible sobre #2A2824 | S2 |

### E.2 · Issues dark-specific

- **S1 · `--evidence` dark (2.66:1) rompe AA.** Es el color de provenance, el device diferenciador del producto. Propuesta: `#D48090` (5.11:1 sobre surface). Mantener el tint en `rgba(212,128,144,0.15)` para fondos de pill.
- **S1 · `--text-muted` en dark falla body.** Aunque en bg-primary (4.40:1) pasa PASS-LG, en bg-surface (3.88:1) falla 4.5:1 y se usa en `.agent-mini-row .role` (12px), `.activity-time` (11px) — tamaños que WCAG exige 4.5:1. Propuesta: `#A49C90` (4.78:1 sobre bg-surface dark).
- **S1 · `--error` dark (3.13:1 en surface) no pasa body.** Se usa en `.admin-banner` (1878 — texto 12px). Propuesta: `#D97070` (4.55:1 sobre surface, 5.15:1 sobre primary).
- **S1 · Shadows desaparecen.** `--shadow-sm: 0 1px 2px rgba(0,0,0,0.3)` sobre `#2A2824` surface apenas se ve (delta ~8% luminancia). Opción: subir opacidad y agregar rim light coral tint como lift visual.
- **S2 · `--border-subtle` dark (1.30:1 sobre surface).** Card sobre surface pierde su silueta. Light sobrevive por la sombra; dark necesita subir borde o reforzar shadow. Propuesta: `#4A463F` (1.57:1 — mejora marginal; combinar con `box-shadow` más agresivo).
- **S2 · `--border-strong` dark (2.01:1).** Se usa en hover de `.btn-secondary:hover` (168) y de pricing card featured; no da la sensación de "activated". Propuesta: `#6B6658` (2.91:1).
- **S2 · Coral-primary sobre dark bg-primary (4.27:1)** pasa PASS-LG pero falla body. En `a { color: var(--coral-primary) }` (99) los links de tamaño 13px fallan. Propuesta: usar `--coral-hover` (#D97757 → 5.34:1) como color de link base en dark, o introducir `--coral-text` específico.
- **S2 · Theme-toggle state indicator ausente.** `data-theme-btn="light"|"dark"` se aplica al botón pero el CSS `.active` no tiene regla visible en el prototipo (buscar selector — no existe regla explícita). El usuario no ve cuál modo está activo.
- **S3 · `--coral-tint` dark (rgba coral 15% sobre `#2A2824`) resulta pill fondo ~`#3C2D28`.** Legible, pero coral-text sobre él: ~4.0:1 — borderline. Se puede subir opacity del tint a 0.22.

### E.3 · CSS con correcciones (pegable)

```css
:root[data-theme="light"] {
  /* Surfaces — sin cambios */
  --bg-primary:        #F4F1ED;
  --bg-surface:        #FFFFFF;
  --bg-subtle:         #EDE8DF;
  --bg-hover:          #E8E2D6;
  --bg-overlay:        rgba(31, 30, 28, 0.45);

  /* Text — text-muted endurecido para pasar AA body sobre cualquier bg claro */
  --text-primary:      #1F1E1C;
  --text-secondary:    #5A544C;
  --text-muted:        #756E62;   /* antes #8A8278 · ahora 4.48:1 sobre bg-primary */
  --text-muted-weak:   #8A8278;   /* sólo para 14px+ semibold o captions */
  --text-inverse:      #F4F1ED;
  --text-on-coral:     #FFFFFF;

  /* Borders */
  --border-subtle:     #D8D0C0;
  --border-strong:     #B8AE9C;
  --border-coral:      #C96442;

  /* Coral */
  --coral-primary:     #C96442;
  --coral-hover:       #A84F33;
  --coral-text:        #A84F33;   /* alias: usar SIEMPRE este para texto-link, no coral-primary */
  --coral-tint:        rgba(201, 100, 66, 0.10);
  --coral-tint-strong: rgba(201, 100, 66, 0.18);

  /* Evidence — sin cambios, pasa AA light */
  --evidence:          #6E1F2B;
  --evidence-tint:     rgba(110, 31, 43, 0.08);

  /* Semantic — warning y success leve endurecimiento para body */
  --success:           #5E7253;   /* antes #7A8E6D · ahora 5.24:1 */
  --success-ui:        #7A8E6D;   /* original, para fondos de pill e iconos ≥18px */
  --warning:           #9C7238;   /* antes #B88A4A · ahora 4.31:1 */
  --warning-ui:        #B88A4A;
  --error:             #8B2F2F;
  --info:              #5A6B7C;

  /* Node colors — sin cambios */
  --node-trigger:      #6B7280;
  --node-agent:        #C96442;
  --node-action:       #4A5568;
  --node-policy:       #B88A4A;
  --node-approval:     #7A8E6D;
  --node-output:       #8A8278;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(31, 30, 28, 0.04), 0 1px 3px rgba(31, 30, 28, 0.06);
  --shadow-md: 0 2px 6px rgba(31, 30, 28, 0.06), 0 4px 12px rgba(31, 30, 28, 0.08);
  --shadow-lg: 0 8px 24px rgba(31, 30, 28, 0.10), 0 16px 48px rgba(31, 30, 28, 0.08);
  --focus-ring: 0 0 0 3px var(--coral-tint-strong);
}

:root[data-theme="dark"] {
  --bg-primary:        #1F1E1C;
  --bg-surface:        #2A2824;
  --bg-subtle:         #34312C;
  --bg-hover:          #3D3A34;
  --bg-overlay:        rgba(0, 0, 0, 0.65);

  --text-primary:      #F4F1ED;
  --text-secondary:    #B8B0A4;
  --text-muted:        #A49C90;   /* antes #8A8278 · 4.78:1 sobre bg-surface */
  --text-muted-weak:   #8A8278;
  --text-inverse:      #1F1E1C;
  --text-on-coral:     #FFFFFF;

  --border-subtle:     #4A463F;   /* antes #3D3A34 — sube luminancia para que se vea card-en-surface */
  --border-strong:     #6B6658;   /* antes #524E45 — 2.91:1, suficiente para hover states visibles */
  --border-coral:      #D97757;

  --coral-primary:     #C96442;
  --coral-hover:       #D97757;
  --coral-text:        #D97757;   /* link base en dark */
  --coral-tint:        rgba(217, 119, 87, 0.18);   /* +opacity para legibilidad */
  --coral-tint-strong: rgba(217, 119, 87, 0.28);

  --evidence:          #D48090;   /* antes #A84A5A · ahora 5.11:1 */
  --evidence-tint:     rgba(212, 128, 144, 0.15);

  --success:           #9BAD8C;
  --success-ui:        #9BAD8C;
  --warning:           #E0B47A;   /* antes #D0A66A · ahora 7.69:1 · leve pero asegura AA body */
  --warning-ui:        #D0A66A;
  --error:             #D97070;   /* antes #B85555 · ahora 4.55:1 sobre surface */
  --info:              #8EA0B2;   /* leve boost de #7A8A9B a 5.0:1 */

  --node-trigger:      #9CA3AF;
  --node-agent:        #D97757;
  --node-action:       #A0AEC0;
  --node-policy:       #D0A66A;
  --node-approval:     #9BAD8C;
  --node-output:       #B8B0A4;

  /* Shadows con rim coral sutil para recuperar elevación sobre warm-dark */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.45), 0 0 0 1px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.55), 0 1px 0 rgba(255, 255, 255, 0.02) inset;
  --shadow-lg: 0 16px 48px rgba(0, 0, 0, 0.65), 0 1px 0 rgba(255, 255, 255, 0.03) inset;
  --focus-ring: 0 0 0 3px rgba(217, 119, 87, 0.40);
}

/* Regla global para que el theme-toggle muestre el estado activo */
[data-theme-btn] {
  padding: 6px;
  border-radius: var(--radius-md, 6px);
  color: var(--text-secondary);
  transition: all var(--duration-fast, 120ms) var(--ease-standard, ease);
}
[data-theme-btn]:hover { background: var(--bg-subtle); color: var(--text-primary); }
[data-theme-btn].active { background: var(--coral-tint); color: var(--coral-primary); }

/* Focus-visible global (fill del gap WCAG 2.4.7) */
.btn:focus-visible,
.tab:focus-visible,
.icon-btn:focus-visible,
.sidebar-nav-item:focus-visible,
.filter-chip:focus-visible,
a:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
  border-radius: var(--radius-md, 6px);
}

/* Link base usa coral-text, no coral-primary — diferencia visible entre dark y light */
a { color: var(--coral-text); text-decoration: none; }
a:hover { color: var(--coral-hover); text-decoration: underline; text-underline-offset: 2px; }

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
