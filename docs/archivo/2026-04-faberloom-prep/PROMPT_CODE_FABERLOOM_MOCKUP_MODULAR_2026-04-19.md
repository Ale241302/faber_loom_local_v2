# PROMPT — FaberLoom v2 Mockup standalone (arquitectura modular-fragmentada)

**Audiencia:** Claude Code operando en `/MWT KB/faberloom-mockup/`.
**Objetivo:** construir un mockup standalone HTML de `FaberLoom v1 Beta` que cubra TODA la funcionalidad conversada en las rondas de diseño, SPEC y auditoría. El output final es **un único archivo HTML abrible con doble clic** (`file://`), pero el desarrollo se hace por **fragmentos modulares** que un integrador (`build.py`) concatena al final.

**Sin límite de líneas. Detalle exhaustivo. Iteración por módulo.**

---

## §0 · Contexto mínimo obligatorio

Antes de escribir una sola línea, leé en este orden:

1. `/MWT KB/docs/SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` (la verdad actual — 20 tablas FROZEN, 17 secciones, decisiones cerradas)
2. `/MWT KB/faberloom-mockup/README.md` (estado previo del mockup modular ESM)
3. `/MWT KB/faberloom-mockup/index-standalone.html` (versión standalone anterior, 1482 líneas, 4 módulos — es la **base** sobre la que extendés)
4. `/MWT KB/PROMPT_DESIGN_FABERLOOM_MOCKUP_FULL_2026-04-19.md` (tokens, tipografía, widgets, acceptance criteria del diseño)
5. `/MWT KB/PROMPT_CODE_FABERLOOM_MOCKUP_COMPLETO_2026-04-19.md` (versión previa de este prompt, en standalone monolítico — **este archivo la reemplaza**)

Decisiones arquitectónicas ya cerradas (NO re-debatir):

- **3 objetos canónicos:** AgentSpec / AgentRuntime / AgentMemory
- **State machine 9 estados:** drafting · awaiting_approval · approved · executing · waiting_external_signal · blocked · completed · failed · escalated
- **Autonomy Ladder L0-L4** con unlock criterion textual (NO toggle de usuario)
- **3 capas skill:** base sellada / manual overlay / learned overlay (gate humano)
- **Draft-first absoluto.** Toda acción con efecto externo pasa por drafting → awaiting_approval → approved.
- **Provenance schema:** `claim_id → evidence_span_id → source_version → retrieval_run_id`
- **Action-risk registry:** 6 campos (action_id, reversibility, side_effects, min_autonomy, required_role, audit_class)
- **Workflow state ledger** con trace paso-a-paso
- **4 scopes de conocimiento:** global / org / dept / user + `business_entity_id` como metadata ortogonal
- **3 roles:** Tenant Owner / Admin / Operator
- **Private-by-default intra-org.**
- **RLS session-scoped** (SET LOCAL app.tenant_id / user_id / role / dept_ids / break_glass)
- **TTL learned overlays 90d** (configurable 30-180 por skill)
- **5 razones de feedback tipificado:** claim sin evidencia · tono · dato incorrecto · acción riesgosa · otro
- **Consolidación:** Candidate → Active → Archived/Reverted
- **Learning Thermometer:** 🔵 Frío 0-2 · 🟡 Tibio 3-5 · 🔴 Caliente 6+
- **i18n ES + EN + PT-BR** (332+ claves, ES default)
- **Brand atmosphere:** Coral #C96442 · Cream #F4F1ED · Warm-dark #1F1E1C · Evidence #6E1F2B · Georgia italic display + Inter body + JetBrains Mono

---

## §1 · Restricciones duras

| # | Restricción | Rationale |
|---|-------------|-----------|
| 1 | Output final = 1 archivo HTML abrible con doble clic (`file://`) | Álvaro quiere verlo en local sin setup |
| 2 | Desarrollo en **fragments** bajo `faberloom-mockup/fragments/` | Iteración focalizada, paralelización real |
| 3 | Integrador = `faberloom-mockup/build.py` (Python stdlib, sin deps) | Zero build tooling |
| 4 | Prohibido `import`/`export` ESM · prohibido `fetch()` | `file://` no permite ni uno ni otro |
| 5 | Mock data inline en fragment `_mock_data.js.fragment` como `const MOCK = {...}` | No `fetch('/data/mock.json')` |
| 6 | Tipografías vía Google Fonts CDN (link tag en `<head>`) | Única excepción al no-CDN |
| 7 | `axe-core` opcional vía CDN, solo al pulsar botón **Validar** | No bloquea carga offline |
| 8 | i18n inline: 3 objetos `I18N_ES` / `I18N_EN` / `I18N_PT` en `_i18n_*.js.fragment` | No JSON externos |
| 9 | Iconos y logo inline como SVG | No assets externos |
| 10 | `localStorage` con fallback a `Map` en memoria si está bloqueado | `file://` en algunos navegadores bloquea storage |
| 11 | **Sin límite de líneas.** Priorizar claridad y completitud sobre brevedad. | Álvaro quiere iterar y el prompt debe ser inequívoco |
| 12 | Cada fragment debe correr en aislamiento: `<style>` scoped por prefijo de clase (`.mod-bandeja-*`, `.mod-skill-*`...) | Evitar colisiones cuando se concatenan |
| 13 | Ningún fragment puede referenciar a otro por import — solo via `window.__faberloom` | El boot expone bus/store/i18n/theme/router ahí |
| 14 | Cambios JS requeridos: pasar `python -c "import sys; exec(open(...).read())"` nomás — pero el HTML final debe cargar sin errores de consola | Gate de sanidad |
| 15 | Todo texto en UI pasa por `i18n.t('clave')` — nada hardcodeado en módulos | Permite toggle ES/EN/PT |

---

## §2 · Estructura de archivos objetivo

```
/MWT KB/faberloom-mockup/
├── fragments/
│   ├── 00_head.html.fragment                · <head>: meta, fonts, title
│   ├── 01_design_tokens.css.fragment        · :root tokens light + [data-theme="dark"]
│   ├── 02_base_styles.css.fragment          · reset, tipografía, layout, utilidades
│   ├── 03_boot.js.fragment                  · bus + store + i18n + theme + a11y + router + error boundary
│   ├── 04_shell.html.fragment               · topbar + sidebar + <main id="slot">
│   ├── 05_mock_data.js.fragment             · const MOCK con 17 colecciones
│   ├── 06_widgets.js.fragment               · 15 widgets (definidos en §6)
│   ├── 07_i18n_es.js.fragment               · I18N_ES default
│   ├── 07_i18n_en.js.fragment               · I18N_EN
│   ├── 07_i18n_pt.js.fragment               · I18N_PT
│   ├── 10_module_bandeja_lista.html.fragment
│   ├── 11_module_bandeja_detail.html.fragment
│   ├── 12_module_skill_studio.html.fragment
│   ├── 13_module_agent_console.html.fragment
│   ├── 14_module_workflows_canvas.html.fragment
│   ├── 15_module_runs_timeline.html.fragment
│   ├── 16_module_consolidation.html.fragment
│   ├── 20_module_admin_users.html.fragment
│   ├── 21_module_admin_knowledge.html.fragment
│   ├── 22_module_admin_audit.html.fragment
│   ├── 23_module_admin_tenant.html.fragment
│   ├── 24_module_admin_connectors.html.fragment
│   ├── 30_module_ops_health.html.fragment
│   ├── 31_module_design_system.html.fragment
│   └── 99_footer.html.fragment              · closing tags + init call
├── build.py                                 · integrador
└── index-standalone.html                    · OUTPUT (regenerado)
```

El prefijo numérico marca orden de concatenación en `build.py`.

---

## §3 · Contrato de fragment

Cada fragment sigue UNO de estos 4 patrones según extensión:

### 3.1 `*.html.fragment`
Contiene HTML + `<style>` scoped + `<script>` IIFE. Ejemplo para un módulo:

```html
<!-- fragments/12_module_skill_studio.html.fragment -->
<template id="tpl-mod-skill-studio">
  <div class="mod-skill">
    <header class="mod-skill__header">
      <h1 data-i18n="skill.title">Skill Studio</h1>
      <div class="mod-skill__thermometer" id="thermometer-slot"></div>
    </header>
    <div class="mod-skill__cols">
      <section class="mod-skill__col mod-skill__col--base">...</section>
      <section class="mod-skill__col mod-skill__col--manual">...</section>
      <section class="mod-skill__col mod-skill__col--learned">...</section>
    </div>
  </div>
</template>

<style>
  .mod-skill { display:grid; grid-template-rows:auto 1fr; gap:var(--space-4); }
  .mod-skill__cols { display:grid; grid-template-columns:1fr 1fr 1fr; gap:var(--space-3); }
  /* ...todo prefijado .mod-skill__ para aislamiento */
</style>

<script>
(function(){
  const MODULE_ID = 'skill-studio';
  const MODULE_ROUTE = '#/skills/:id';

  async function mount(slot, ctx) {
    const tpl = document.getElementById('tpl-mod-skill-studio');
    slot.appendChild(tpl.content.cloneNode(true));
    const skillId = ctx.params.id || 'sk_cotizar';
    const skill = window.__faberloom.mock.skills[skillId];
    if (!skill) return renderEmpty(slot);
    renderBaseLayer(slot, skill.base);
    renderManualLayer(slot, skill.manualOverlays);
    renderLearnedLayer(slot, skill.learnedPatterns);
    mountThermometer(slot.querySelector('#thermometer-slot'), skill.temperature);
    window.__faberloom.i18n.applyToDom(slot);
    return { unmount: () => { /* cleanup */ } };
  }

  window.__faberloom = window.__faberloom || {};
  window.__faberloom.modules = window.__faberloom.modules || {};
  window.__faberloom.modules[MODULE_ID] = { mount, meta: { route: MODULE_ROUTE, needsTenant:true, needsRole:['operator','admin','owner'], i18nDomain:'skill' } };
})();
</script>
```

### 3.2 `*.css.fragment`
Contenido CSS puro que `build.py` envuelve en `<style>` dentro del `<head>`.

### 3.3 `*.js.fragment`
Contenido JS puro que `build.py` envuelve en `<script>` al final del `<body>`. **Orden importa** — boot antes que módulos, i18n antes que boot.init().

### 3.4 `00_head.html.fragment` / `04_shell.html.fragment` / `99_footer.html.fragment`
HTML estructural insertado tal cual.

---

## §4 · Integrador `build.py`

```python
#!/usr/bin/env python3
"""
build.py — concatena fragments/ en index-standalone.html
Uso: python build.py
Sin dependencias externas.
"""
import pathlib, re, sys, datetime

ROOT = pathlib.Path(__file__).parent
FRAGMENTS = ROOT / "fragments"
OUTPUT = ROOT / "index-standalone.html"

def load_fragment(path):
    return path.read_text(encoding="utf-8")

def wrap(content, kind):
    if kind == "css":   return f"<style>\n{content}\n</style>"
    if kind == "js":    return f"<script>\n{content}\n</script>"
    return content

def build():
    frags = sorted(FRAGMENTS.glob("*.fragment"))
    head_frags, body_frags = [], []
    for f in frags:
        name = f.name
        raw  = load_fragment(f)
        if   name.endswith(".css.fragment"):      head_frags.append(wrap(raw, "css"))
        elif name.endswith(".js.fragment"):       body_frags.append(wrap(raw, "js"))
        elif name.startswith("00_head"):          head_frags.insert(0, raw)
        elif name.startswith("99_footer"):        body_frags.append(raw)
        elif name.endswith(".html.fragment"):     body_frags.append(raw)

    html = f"""<!DOCTYPE html>
<html lang="es" data-theme="light">
<head>
{chr(10).join(head_frags)}
</head>
<body>
{chr(10).join(body_frags)}
<script>window.__faberloom.boot.init();</script>
</body>
</html>"""
    OUTPUT.write_text(html, encoding="utf-8")
    size_kb = OUTPUT.stat().st_size // 1024
    lines   = html.count("\n")
    print(f"✓ index-standalone.html · {size_kb} KB · {lines} líneas · {datetime.datetime.now():%H:%M:%S}")

if __name__ == "__main__":
    build()
```

Claude Code debe **crear este archivo** y correrlo al final de cada iteración.

---

## §5 · Design tokens (fragment `01_design_tokens.css.fragment`)

Tokens completos light + dark. Incluye:

```css
:root {
  /* ── Brand core ─────────────────────────────────────── */
  --brand-coral:        #C96442;
  --brand-coral-ink:    #A84D30;
  --brand-coral-haze:   #F2D9CE;
  --brand-evidence:     #6E1F2B;
  --brand-cream:        #F4F1ED;
  --brand-cream-deep:   #EAE6DF;
  --brand-ink:          #1F1E1C;
  --brand-ink-soft:     #3A3834;
  --brand-mist:         #8A857C;
  --brand-sage:         #7F8C5B;
  --brand-amber:        #C89A3E;
  --brand-sky:          #5A7C89;
  --brand-lilac:        #9A7FA3;

  /* ── Surface ─────────────────────────────────────────── */
  --bg-canvas:          var(--brand-cream);
  --bg-surface:         #FFFFFF;
  --bg-surface-raised:  #FBF9F5;
  --bg-overlay:         rgba(31,30,28,0.55);
  --bg-dot-grid:        rgba(31,30,28,0.06);

  /* ── Text ─────────────────────────────────────────────── */
  --text-primary:       var(--brand-ink);
  --text-secondary:     var(--brand-ink-soft);
  --text-muted:         var(--brand-mist);
  --text-inverse:       var(--brand-cream);
  --text-link:          var(--brand-coral-ink);

  /* ── Borders ──────────────────────────────────────────── */
  --border-subtle:      rgba(31,30,28,0.08);
  --border-default:     rgba(31,30,28,0.16);
  --border-strong:      rgba(31,30,28,0.32);
  --border-focus:       var(--brand-coral);

  /* ── Semantics (draft, risk, autonomy) ────────────────── */
  --draft-pending:      #C89A3E;   /* amber */
  --draft-approved:     #7F8C5B;   /* sage */
  --draft-rejected:     #9A2E2E;   /* deep coral */
  --risk-low:           #7F8C5B;
  --risk-med:           #C89A3E;
  --risk-high:          #C96442;
  --risk-irreversible:  #6E1F2B;
  --autonomy-l0:        #8A857C;
  --autonomy-l1:        #5A7C89;
  --autonomy-l2:        #7F8C5B;
  --autonomy-l3:        #C89A3E;
  --autonomy-l4:        #C96442;
  --thermo-cold:        #5A7C89;
  --thermo-warm:        #C89A3E;
  --thermo-hot:         #C96442;

  /* ── Typography ───────────────────────────────────────── */
  --font-display: 'Georgia', 'Libre Caslon Text', serif;
  --font-body:    'Inter', -apple-system, system-ui, sans-serif;
  --font-mono:    'JetBrains Mono', ui-monospace, monospace;
  --fs-1: 2.5rem;   --lh-1: 1.15;
  --fs-2: 2rem;     --lh-2: 1.2;
  --fs-3: 1.5rem;   --lh-3: 1.3;
  --fs-4: 1.25rem;  --lh-4: 1.35;
  --fs-5: 1rem;     --lh-5: 1.5;
  --fs-6: 0.875rem; --lh-6: 1.4;
  --fs-7: 0.75rem;  --lh-7: 1.3;

  /* ── Spacing (8px base) ───────────────────────────────── */
  --space-0: 0;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;
  --space-8: 64px;

  /* ── Radii ───────────────────────────────────────────── */
  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --radius-pill: 9999px;

  /* ── Shadows ─────────────────────────────────────────── */
  --shadow-subtle: 0 1px 2px rgba(31,30,28,0.04), 0 1px 1px rgba(31,30,28,0.03);
  --shadow-card:   0 2px 8px rgba(31,30,28,0.06), 0 1px 3px rgba(31,30,28,0.04);
  --shadow-float:  0 8px 28px rgba(31,30,28,0.12), 0 2px 6px rgba(31,30,28,0.05);
  --shadow-focus:  0 0 0 3px rgba(201,100,66,0.28);

  /* ── Motion ──────────────────────────────────────────── */
  --ease-out:    cubic-bezier(0.2, 0.8, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --dur-fast:    120ms;
  --dur-base:    200ms;
  --dur-slow:    320ms;
  --dur-page:    420ms;

  /* ── Z-index ──────────────────────────────────────────── */
  --z-shell:     10;
  --z-dropdown:  100;
  --z-modal:     1000;
  --z-toast:     2000;
  --z-livedbg:   9999;
}

[data-theme="dark"] {
  --bg-canvas:          #1F1E1C;
  --bg-surface:         #2A2825;
  --bg-surface-raised:  #32302C;
  --bg-dot-grid:        rgba(244,241,237,0.04);
  --text-primary:       #F4F1ED;
  --text-secondary:     #C9C3B8;
  --text-muted:         #8A857C;
  --text-inverse:       #1F1E1C;
  --border-subtle:      rgba(244,241,237,0.08);
  --border-default:     rgba(244,241,237,0.14);
  --border-strong:      rgba(244,241,237,0.28);
  --brand-evidence:     #D47B8A;  /* subido para contraste AA sobre warm-dark */
  --shadow-card:        0 2px 8px rgba(0,0,0,0.32), 0 1px 3px rgba(0,0,0,0.24);
  --shadow-float:       0 8px 28px rgba(0,0,0,0.48), 0 2px 6px rgba(0,0,0,0.28);
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation:none !important; transition:none !important; }
}
```

---

## §6 · Widgets (fragment `06_widgets.js.fragment`)

Definí 15 widgets. **TODOS** viven en `window.__faberloom.widgets`. Cada widget expone `mount(slot, props)` y retorna `{ update(newProps), unmount() }`.

| # | Widget | Props clave | Dónde se usa |
|---|--------|-------------|--------------|
| 1 | **Thermometer** | `{ value, thresholds }` → renderiza 🔵🟡🔴 con barra + etiqueta | Skill Studio header, Bandeja list row |
| 2 | **AutonomyLadder** | `{ current: 'L0'..'L4', unlock: string }` → 5 escalones con el actual activo + textbox unlock criterion | Agent Console summary |
| 3 | **ProvenanceSupport** | `{ claimId, evidences: [{span, source, version, line}] }` → card expandible con el claim y las evidencias | Bandeja detail tab "Evidencia" |
| 4 | **RiskBadge** | `{ reversibility, sideEffects, autonomyLevel }` → badge con color semantic + tooltip con los 6 campos del action-risk registry | Bandeja detail header, Agent Console skills list |
| 5 | **DraftStateBadge** | `{ state: 'drafting'\|'awaiting_approval'\|'approved'\|...\|'escalated' }` → 9 estados de state machine | Bandeja list + detail |
| 6 | **EmptyState** | `{ illustration, title, description, cta }` | Cualquier lista vacía |
| 7 | **LoadingSkeleton** | `{ variant: 'list'\|'card'\|'table', rows }` | view-state loading |
| 8 | **DegradedCard** | `{ error, moduleId, onRetry }` → renderizado por error boundary cuando módulo truena | router error boundary |
| 9 | **Modal** | `{ title, body, actions, size, onClose }` | genérico |
| 10 | **FeedbackModal** | `{ draftId, onSubmit }` → radio con 5 razones + textarea + submit → `bus.emit('feedback:submit', payload)` | Bandeja detail |
| 11 | **ConsolidationModal** | `{ skillId, patterns }` → lista de patrones pendientes con diff visual + approve/reject por fila | Skill Studio, Admin Knowledge |
| 12 | **Toast** | `{ kind: 'success'\|'info'\|'warn'\|'error', message, duration }` | global, emitido por `bus.emit('toast', ...)` |
| 13 | **Tabs** | `{ items: [{id, label, panel}], active, onChange }` → accesible, arrow keys | Bandeja detail (4 tabs), Agent Console (4 tabs) |
| 14 | **Diff** | `{ left, right, lang?}` → render 2 columnas con líneas añadidas/removidas | Consolidation modal |
| 15 | **Timeline** | `{ entries: [{ts, actor, action, detail}] }` → verticalmente con ts formateado | Runs timeline, Admin Audit |

Cada widget debe tener un `data-widget="<name>"` en el root para debug (`document.querySelectorAll('[data-widget]')`).

---

## §7 · Mock data (fragment `05_mock_data.js.fragment`)

Define `const MOCK = {...}` con 17 colecciones. Todas inline, sin async, sin fetch.

```js
const MOCK = {
  tenants: [
    { id: 't_muito',   name: 'Muito Work',     region: 'LATAM', plan: 'beta',  seatsActive30d: 6 },
    { id: 't_demo_mx', name: 'Demo Partner MX', region: 'MX',    plan: 'beta',  seatsActive30d: 3 },
    { id: 't_demo_co', name: 'Demo Partner CO', region: 'CO',    plan: 'beta',  seatsActive30d: 4 }
  ],

  users: [
    { id: 'u_alvaro',  tenantId:'t_muito', email:'sjoalfaro@gmail.com', role:'owner', deptIds:['d_ops'], name:'Álvaro', createdAt:'2026-01-15', lastActive:'2026-04-19' },
    { id: 'u_ana',     tenantId:'t_muito', email:'ana@muito.work',      role:'admin', deptIds:['d_ops','d_ventas'], name:'Ana', createdAt:'2026-02-01', lastActive:'2026-04-19' },
    { id: 'u_bruno',   tenantId:'t_muito', email:'bruno@muito.work',    role:'operator', deptIds:['d_ventas'],     name:'Bruno', createdAt:'2026-03-01', lastActive:'2026-04-18' },
    // ... 4 más
  ],

  departments: [
    { id:'d_ops',     tenantId:'t_muito', name:'Operaciones' },
    { id:'d_ventas',  tenantId:'t_muito', name:'Ventas' },
    { id:'d_compras', tenantId:'t_muito', name:'Compras' }
  ],

  businessEntities: [
    { id:'be_acme_mx',  tenantId:'t_muito', name:'ACME Industrias MX',   kind:'customer', country:'MX' },
    { id:'be_constru_co', tenantId:'t_muito', name:'Construcciones Bogotá', kind:'customer', country:'CO' },
    { id:'be_marluvas', tenantId:'t_muito', name:'Marluvas',             kind:'supplier', country:'BR' },
    { id:'be_tecmater', tenantId:'t_muito', name:'Tecmater',             kind:'supplier', country:'BR' }
  ],

  agents: [
    {
      id:'ag_cotizador', tenantId:'t_muito', name:'Cotizador Calzado',
      autonomy:'L1', unlockCriterion:'≥95% aceptación draft en 30 runs consecutivos',
      thermometer:{ value:4, state:'warm' },
      tier:'demo-critical',
      kpis:{ runs30d:43, approvalRate:0.67, avgLatencyMin:12, failRate:0.07, costUSD30d:21.40 },
      skills:['sk_cotizar','sk_specs_tecnicas','sk_stock_lookup'],
      state:'running'
    },
    // 6 más con variantes: L0 shadow · L2 auto-bajo · L3 · L4, distintos tier (hot, cold, experimental, internal)
  ],

  skills: {
    sk_cotizar: {
      id:'sk_cotizar', name:'Cotizar calzado seguridad',
      temperature: 6,  // hot
      base: {
        version:'1.0.3', sealed:true, author:'alvaro',
        systemPrompt:'Eres un asistente que genera cotizaciones B2B de calzado de seguridad...',
        policies:['draft-first','action-risk-check','provenance-required'],
        tools:['stock_lookup','price_table','astm_matcher']
      },
      manualOverlays: [
        { id:'mo_1', rule:'Si cliente en MX, usar tabla de precios MXN y añadir IVA 16%', author:'u_alvaro', createdAt:'2026-03-02' },
        { id:'mo_2', rule:'Marluvas stock priority sobre Tecmater para modelos Goliath/Velox', author:'u_alvaro', createdAt:'2026-03-15' },
        { id:'mo_3', rule:'Nunca prometer plazo <5 días sin check de stock real', author:'u_ana', createdAt:'2026-04-01' },
        { id:'mo_4', rule:'Si el cliente solicita norma ASTM F2413, validar composite toe vs steel toe', author:'u_alvaro', createdAt:'2026-04-10' }
      ],
      learnedPatterns: [
        { id:'lp_1', pattern:'Consolidar "Velox 350" en línea única con qty ajustada', evidenceCount:7, firstSeen:'2026-04-05', lastSeen:'2026-04-18', status:'pending', ttlDays:90 },
        { id:'lp_2', pattern:'Añadir cláusula de plazo variable cuando supplier = Marluvas', evidenceCount:5, firstSeen:'2026-04-08', lastSeen:'2026-04-17', status:'pending', ttlDays:90 },
        // ... 5 más
      ],
      goldSamples: [
        { id:'gs_1', input:'...', expectedOutput:'...', rubric:[...], createdBy:'u_alvaro' },
        // 3 más
      ]
    },
    // sk_specs_tecnicas · sk_stock_lookup · sk_seguimiento_pipeline · sk_hola_cliente · sk_validacion_astm · sk_generacion_pdf
  },

  drafts: [
    {
      id:'dr_001', agentId:'ag_cotizador', tenantId:'t_muito',
      state:'awaiting_approval', createdAt:'2026-04-19T09:12:00-06:00',
      businessEntityId:'be_acme_mx',
      subject:'Cotización pedido 14 pares Velox 350 + 8 pares Goliath XT',
      body: '...',  // texto largo con claims marcados [c1], [c2], etc.
      claims: [
        { id:'c1', text:'Stock disponible Velox 350: 48 unidades', evidenceSpans:[
          { id:'e1', source:'stock_lookup', sourceVersion:'2026-04-19T08:00:00Z', line:'V350-M: 48', retrievalRunId:'r_881' }
        ]},
        { id:'c2', text:'Plazo de entrega 7 días hábiles', evidenceSpans:[
          { id:'e2', source:'policy_playbook', sourceVersion:'1.2.0', line:'MX plazo default = 7d', retrievalRunId:'r_881' }
        ]},
        // 4 más
      ],
      action: {
        actionId:'send_email_quote',
        reversibility:'reversible_24h',
        sideEffects:['external_send','crm_log'],
        minAutonomy:'L1',
        requiredRole:'operator',
        auditClass:'commercial'
      },
      workflowTrace: [
        { step:1, node:'trigger:rfq_received', ts:'09:10:00', status:'done' },
        { step:2, node:'retrieve:stock_lookup', ts:'09:10:12', status:'done' },
        { step:3, node:'retrieve:price_table', ts:'09:10:14', status:'done' },
        { step:4, node:'llm:compose_draft', ts:'09:11:32', status:'done' },
        { step:5, node:'validator:provenance_check', ts:'09:11:48', status:'done' },
        { step:6, node:'hitl:awaiting_approval', ts:'09:12:00', status:'active' },
        { step:7, node:'action:send_email', ts:null, status:'pending' }
      ]
    },
    // 13 drafts más en distintos estados, algunos sin evidencia, algunos escalated, algunos completed
  ],

  runs: [
    // 50+ runs cortas con: id, agentId, startedAt, endedAt, finalState, tokensUsed, costUSD, tracesCount
  ],

  consolidations: [
    {
      id:'cons_1', skillId:'sk_cotizar', status:'candidate',
      triggeredBy:'thermometer_hot', triggeredAt:'2026-04-18T16:00:00-06:00',
      patterns:['lp_1','lp_2','lp_3'],
      diffPreview:{ before:'...', after:'...' }
    }
  ],

  feedbacks: [
    { id:'fb_1', draftId:'dr_012', userId:'u_alvaro', reason:'dato_incorrecto', note:'el precio del V350 era 820 no 780', createdAt:'2026-04-17T11:20:00-06:00' },
    // ... 8 más cubriendo las 5 razones
  ],

  auditEvents: [
    // 60+ eventos estructurados: ts, actor, action, target, diff, ip, userAgent
    // incluir: login, role_change, break_glass_activated, skill_promote, draft_approve, connector_enable, etc.
  ],

  actions: [
    // action-risk registry completo: 18 acciones con 6 campos cada una
    { actionId:'send_email_quote', reversibility:'reversible_24h', sideEffects:['external_send','crm_log'], minAutonomy:'L1', requiredRole:'operator', auditClass:'commercial' },
    { actionId:'create_order_sap', reversibility:'irreversible_cost', sideEffects:['erp_write','inventory_hold'], minAutonomy:'L3', requiredRole:'admin', auditClass:'financial' },
    // ...
  ],

  connectors: [
    { id:'co_postmark',  name:'Postmark SMTP', kind:'email', status:'connected',    configuredAt:'2026-04-15' },
    { id:'co_sapi',      name:'Amazon SP-API', kind:'marketplace', status:'disconnected' },
    { id:'co_helium10',  name:'Helium 10',     kind:'marketplace_intel', status:'disconnected' },
    { id:'co_gdrive',    name:'Google Drive',  kind:'kb_source', status:'connected', configuredAt:'2026-04-16' },
    { id:'co_whatsapp',  name:'WhatsApp BSP',  kind:'messaging', status:'planned' }
  ],

  policies: [
    // políticas de RLS / compliance / promoción skill — 12+
    { id:'pol_private_default', scope:'intra_org',        rule:'All memory_chunk with scope=user is invisible to admin unless break_glass', enforced:true },
    { id:'pol_break_glass_8h',  scope:'auth',             rule:'Break-glass session expires at 8h with MFA', enforced:true },
    // ...
  ],

  jobs: [
    // job_execution rows: name, scheduledFor, status, runBy, durationSec
    { name:'consolidation_eval', scheduledFor:'2026-04-19T00:00:00-06:00', status:'completed', durationSec:42 },
    { name:'leakage_tests',      scheduledFor:'2026-04-19T03:00:00-06:00', status:'completed', durationSec:128 },
    { name:'backup_snapshot',    scheduledFor:'2026-04-19T04:00:00-06:00', status:'completed', durationSec:310 }
  ],

  alerts: [
    { id:'al_1', severity:'warn',  title:'p95 retrieval 310ms (>300ms SLO)', since:'2026-04-19T08:00:00-06:00' },
    { id:'al_2', severity:'info',  title:'Consolidation candidate pending (sk_cotizar)', since:'2026-04-18T16:00:00-06:00' }
  ],

  tables: [
    // metadata de las 20 tablas FROZEN del blueprint para el módulo ops_health
    { name:'users', sprint:'S1', rowCount:7, sizeKB:4 },
    { name:'tenants', sprint:'S1', rowCount:3, sizeKB:2 },
    { name:'audit_event', sprint:'S1', rowCount:60, sizeKB:22 },
    // ... 17 más
  ]
};

window.__faberloom = window.__faberloom || {};
window.__faberloom.mock = MOCK;
```

---

## §8 · Módulos — especificación detallada por archivo

Cada módulo tiene esta ficha: **ruta**, **descripción**, **layout**, **widgets que usa**, **data mock que consulta**, **interacciones**, **view-states soportados**, **acceptance criteria específicos**.

### 8.1 `10_module_bandeja_lista.html.fragment`
- **Ruta:** `#/bandeja`
- **Descripción:** lista de drafts en bandeja bidireccional (ya generados esperando aprobación + archivo).
- **Layout:** tabla con columnas: agente · asunto · estado · riesgo · edad · acción.
- **Widgets:** `DraftStateBadge`, `RiskBadge`, `EmptyState`, `LoadingSkeleton`.
- **Interacciones:**
  - Filtro por estado (multi-select)
  - Filtro por agente
  - Filtro por business entity
  - Click en fila → `router.navigate('#/bandeja/' + draftId)`
  - Bulk approve (solo drafts con action-risk = reversible)
- **View-states:** loaded / empty / loading / error.
- **AC:** muestra 14 drafts del mock · filtros funcionan sin recargar · click navega a detail · bulk approve oculto para acciones irreversibles.

### 8.2 `11_module_bandeja_detail.html.fragment`
- **Ruta:** `#/bandeja/:id`
- **Descripción:** detalle del draft con 4 tabs: Contenido · Evidencia · Riesgo · Trace.
- **Layout:**
  - Header: agente, asunto, estado badge, risk badge, botones Aprobar/Rechazar/Editar/Feedback.
  - Tab **Contenido:** body del draft con claims marcados y links a evidencias.
  - Tab **Evidencia:** lista de `ProvenanceSupport` por claim.
  - Tab **Riesgo:** ficha completa del action-risk registry (6 campos).
  - Tab **Trace:** `Timeline` del workflow con los 7 pasos.
- **Widgets:** `Tabs`, `DraftStateBadge`, `RiskBadge`, `ProvenanceSupport`, `FeedbackModal`, `Timeline`.
- **Data:** `MOCK.drafts.find(d => d.id === ctx.params.id)`.
- **Interacciones:** approve → toast + navegar a lista · reject → modal con 5 razones · edit → modal con textarea · feedback → `FeedbackModal`.
- **AC:** demo-crítico `dr_001` debe mostrar 6 claims con evidencia real · estado awaiting_approval debe permitir aprobar · un draft con action-risk `irreversible_cost` exige doble confirmación.

### 8.3 `12_module_skill_studio.html.fragment`
- **Ruta:** `#/skills/:id`
- **Descripción:** editor de skill con 3 columnas.
- **Layout:**
  - Header: nombre + thermometer + select de versión.
  - 3 columnas:
    - **Base sellada** (read-only, muestra system prompt, políticas, tools, hash de versión).
    - **Manual overlay** (editable, lista de reglas con autor + fecha).
    - **Learned overlay** (read-only, patrones candidatos pendientes con badge "Pendiente consolidación").
- **Widgets:** `Thermometer`, `ConsolidationModal`, `Diff`.
- **Data:** `MOCK.skills[ctx.params.id]`.
- **Interacciones:** agregar overlay manual · abrir consolidación (si thermometer = hot) · ver gold samples en un drawer lateral.
- **AC:** no permite editar base · overlays manuales se listan con autor y fecha · learned patterns solo se aprueban desde `ConsolidationModal`.

### 8.4 `13_module_agent_console.html.fragment`
- **Ruta:** `#/agentes/:id`
- **Descripción:** consola del agente con 4 tabs: Resumen · Skills · Memoria · Logs.
- **Layout:**
  - Header: nombre + autonomy ladder + thermometer + estado.
  - Tab **Resumen:** KPIs (runs30d, approvalRate, avgLatencyMin, failRate, costUSD30d) + unlock criterion + últimos 5 drafts.
  - Tab **Skills:** lista de skills con risk badges + link a skill studio.
  - Tab **Memoria:** 3 secciones (run/session · org/account · curated) con contadores.
  - Tab **Logs:** últimas 20 ejecuciones con link a runs timeline.
- **Widgets:** `AutonomyLadder`, `Thermometer`, `Tabs`, `RiskBadge`, `Timeline`.
- **AC:** autonomy ladder muestra L0-L4 con criterio textual visible · cambiar de agente resetea todo el estado de la vista · memoria muestra contadores consistentes con mock.

### 8.5 `14_module_workflows_canvas.html.fragment`
- **Ruta:** `#/workflows`
- **Descripción:** canvas SVG con grafo de nodos.
- **Layout:**
  - Canvas SVG principal (800x600 min) con zoom + pan.
  - Sidebar izquierdo: paleta de tipos de nodo.
  - Sidebar derecho: inspector del nodo seleccionado.
- **Tipos de nodo** (7, con color por tipo):
  - trigger (coral)
  - retrieve (sky)
  - llm (lilac)
  - validator (sage)
  - hitl (amber)
  - action (evidence/deep-coral para irreversibles)
  - branch (mist)
- **Data:** workflow mock con 7 nodos del cotizador (mismo que `dr_001.workflowTrace`).
- **Interacciones:** click nodo → inspector · drag node posiciona (opcional, visual) · botón "Ejecutar" → abre modal con el trace simulado.
- **AC:** 7 nodos renderizados con colores correctos · click en nodo muestra inspector con detalles · al menos un nodo de tipo hitl y uno de tipo action visible.

### 8.6 `15_module_runs_timeline.html.fragment`
- **Ruta:** `#/runs`
- **Descripción:** timeline global de ejecuciones (50+).
- **Layout:** header con filtros (agente, rango fechas, estado) + lista vertical con `Timeline` widget.
- **Data:** `MOCK.runs`.
- **AC:** paginación cada 20 runs · click en run expande el trace · filtros combinables.

### 8.7 `16_module_consolidation.html.fragment`
- **Ruta:** `#/consolidaciones`
- **Descripción:** pipeline Candidate → Active → Archived de consolidaciones.
- **Layout:** 3 columnas Kanban con tarjetas por consolidación.
- **Widgets:** `ConsolidationModal`, `Diff`.
- **Data:** `MOCK.consolidations`.
- **AC:** aprobación mueve la tarjeta y registra audit event · archivar no elimina · rollback disponible en Active (vuelve a Candidate).

### 8.8 `20_module_admin_users.html.fragment`
- **Ruta:** `#/admin/usuarios`
- **Descripción:** gestión de usuarios (solo admin/owner).
- **Layout:** tabla con email, nombre, rol, departamentos, última actividad, acciones (editar rol, desactivar, break-glass).
- **AC:** operator no ve este módulo (router rechaza con DegradedCard + mensaje "Sin permisos") · break-glass exige MFA modal · cambios generan audit events.

### 8.9 `21_module_admin_knowledge.html.fragment`
- **Ruta:** `#/admin/conocimiento`
- **Descripción:** flujo de conocimiento con 4 niveles (global / org / dept / user).
- **Layout:**
  - Tree view izquierdo con scope hierarchy.
  - Panel derecho: chunks del nivel seleccionado + metadata (business_entity_id si aplica) + status (active/superseded/revoked).
  - Botón "Promover a nivel superior" (exige permiso `can_approve_promotion`).
- **AC:** user scope no visible para admin ajeno (private-by-default) salvo break-glass activo · supersede crea relación `supersedes_chunk_id` visible · audit log activado.

### 8.10 `22_module_admin_audit.html.fragment`
- **Ruta:** `#/admin/auditoria`
- **Descripción:** log estructurado de auditoría.
- **Layout:** tabla con ts, actor, action, target, diff, ip, userAgent + filtros + export CSV (via blob).
- **AC:** 60+ eventos visibles · filtros por actor, action, rango fechas · export CSV genera blob descargable.

### 8.11 `23_module_admin_tenant.html.fragment`
- **Ruta:** `#/admin/tenant`
- **Descripción:** config del tenant.
- **Layout:** secciones: identidad SSO (OIDC config placeholder), retention, branding (colores), feature flags, SMTP (Postmark), backup info (RPO 24h / RTO 2h).
- **AC:** solo owner puede editar · cambios marcados como "requiere reinicio" cuando aplica.

### 8.12 `24_module_admin_connectors.html.fragment`
- **Ruta:** `#/admin/conectores`
- **Descripción:** gestión de conectores externos.
- **Layout:** grid de cards con status (connected/disconnected/planned) + botón configurar.
- **Data:** `MOCK.connectors`.
- **AC:** 5 conectores visibles · status filtra · configurar abre modal con campos placeholder.

### 8.13 `30_module_ops_health.html.fragment`
- **Ruta:** `#/ops/health`
- **Descripción:** salud operacional del sistema.
- **Layout:**
  - Row 1: tiles con containers (11 staging + 4 dev) estado / uptime.
  - Row 2: SLOs — p95 retrieval, disponibilidad, error rate.
  - Row 3: job_execution últimas 10 corridas (consolidation_eval, leakage_tests, backup_snapshot, etc.).
  - Row 4: alerts activas.
  - Row 5: tabla de tablas (20 FROZEN) con rowCount y sizeKB.
- **AC:** tiles renderizan sin data real pero con placeholders realistas · 1 alerta warn visible · tables list completa con 20 entradas.

### 8.14 `31_module_design_system.html.fragment`
- **Ruta:** `#/design`
- **Descripción:** showcase del design system.
- **Layout:** secciones: tokens de color · tipografía escala · widgets en vivo (los 15) · estados de draft · autonomy ladder · thermometer · risk badges · spacing grid · motion examples.
- **AC:** todos los widgets renderizables sin props reales (default props) · toggle light/dark afecta todos los tokens visiblemente.

---

## §9 · Shell (fragment `04_shell.html.fragment`)

### 9.1 Topbar

- **Izquierda:** logo FaberLoom (SVG inline, isotipo "Dir A woven lattice") + nombre + breadcrumb dinámico (actualizado por router).
- **Centro:** search stub (`⌘K` abre launcher, por ahora solo toast "Launcher pendiente").
- **Derecha:**
  - Switcher tenant (dropdown con 3 tenants del mock).
  - Switcher rol activo (dropdown con `owner` / `admin` / `operator` — simulación, cambia visibilidad de módulos).
  - Switcher lang (`ES` / `EN` / `PT`).
  - Toggle theme (light/dark).
  - Dropdown view-state (loaded/empty/loading/error) que emite `bus.emit('view-state:change', state)`.
  - Botón **Validar** — carga axe-core via CDN y corre sobre la vista actual, muestra resultados en un drawer.
  - Avatar del usuario + dropdown con Logout (stub).

### 9.2 Sidebar (3 bloques)

```
PRINCIPAL
  · Bandeja           #/bandeja
  · Agentes           #/agentes/ag_cotizador
  · Workflows         #/workflows
  · Runs              #/runs

CONSTRUCCIÓN
  · Skill Studio      #/skills/sk_cotizar
  · Consolidaciones   #/consolidaciones
  · Design System     #/design

GESTIÓN (solo admin/owner)
  · Usuarios          #/admin/usuarios
  · Conocimiento      #/admin/conocimiento
  · Auditoría         #/admin/auditoria
  · Tenant            #/admin/tenant
  · Conectores        #/admin/conectores
  · Ops Health        #/ops/health
```

El bloque GESTIÓN debe ocultarse cuando el rol activo = `operator`.

### 9.3 Main slot

`<main id="fl-slot" tabindex="-1">` — enfocable con skip-link desde el top.

### 9.4 Live region

`<div id="fl-live" aria-live="polite" class="visually-hidden"></div>` — anuncios de cambio de ruta y toasts.

---

## §10 · i18n (fragments `07_i18n_*.js.fragment`)

Estructura del objeto (mismo shape en los 3 idiomas):

```js
const I18N_ES = {
  common: {
    approve:'Aprobar', reject:'Rechazar', edit:'Editar', feedback:'Feedback',
    loading:'Cargando…', empty:'Sin elementos', error:'Algo salió mal',
    retry:'Reintentar', cancel:'Cancelar', save:'Guardar', close:'Cerrar',
    search:'Buscar…', filters:'Filtros', clear:'Limpiar', export:'Exportar'
  },
  nav: {
    bandeja:'Bandeja', agentes:'Agentes', workflows:'Workflows', runs:'Runs',
    skills:'Skill Studio', consolidaciones:'Consolidaciones', design:'Design System',
    admin_users:'Usuarios', admin_knowledge:'Conocimiento', admin_audit:'Auditoría',
    admin_tenant:'Tenant', admin_connectors:'Conectores', ops_health:'Ops Health',
    group_main:'Principal', group_build:'Construcción', group_admin:'Gestión'
  },
  bandeja: {
    title:'Bandeja de salida', col_agent:'Agente', col_subject:'Asunto',
    col_state:'Estado', col_risk:'Riesgo', col_age:'Edad', col_actions:'Acciones',
    bulk_approve:'Aprobar seleccionados', filter_state:'Filtrar por estado',
    filter_agent:'Filtrar por agente', empty:'Sin drafts pendientes',
    tab_content:'Contenido', tab_evidence:'Evidencia', tab_risk:'Riesgo', tab_trace:'Trace',
    confirm_approve:'¿Confirmás aprobación?', confirm_approve_irreversible:'Acción irreversible. ¿Confirmás?'
  },
  skill: {
    title:'Skill Studio', col_base:'Base sellada', col_manual:'Overlay manual',
    col_learned:'Overlay aprendido', add_rule:'Añadir regla', consolidate:'Consolidar',
    thermo_cold:'Frío', thermo_warm:'Tibio', thermo_hot:'Caliente',
    ttl_label:'TTL overlay aprendido (días)', gold_samples:'Gold samples',
    base_sealed:'Base sellada · solo lectura'
  },
  agent: {
    title:'Consola de agente', kpi_runs:'Runs 30d', kpi_approval:'Aprobación',
    kpi_latency:'Latencia p50', kpi_fail:'Tasa fallo', kpi_cost:'Costo USD 30d',
    tab_summary:'Resumen', tab_skills:'Skills', tab_memory:'Memoria', tab_logs:'Logs',
    autonomy_l0:'L0 · Shadow', autonomy_l1:'L1 · Propone',
    autonomy_l2:'L2 · Auto-bajo', autonomy_l3:'L3 · Auto+notif', autonomy_l4:'L4 · Auto+excepciones',
    unlock_criterion:'Criterio para subir nivel'
  },
  workflow: {
    title:'Workflows', palette:'Paleta', inspector:'Inspector',
    node_trigger:'Trigger', node_retrieve:'Retrieve', node_llm:'LLM',
    node_validator:'Validator', node_hitl:'HITL', node_action:'Action', node_branch:'Branch',
    execute:'Ejecutar'
  },
  feedback: {
    title:'Enviar feedback', reason_no_evidence:'Claim sin evidencia',
    reason_tone:'Tono inadecuado', reason_wrong_data:'Dato incorrecto',
    reason_risky:'Acción riesgosa', reason_other:'Otro',
    note:'Notas (opcional)', submit:'Enviar feedback'
  },
  consolidation: {
    title:'Consolidaciones', col_candidate:'Candidate', col_active:'Active',
    col_archived:'Archived', approve:'Aprobar', reject:'Rechazar', rollback:'Revertir',
    diff_before:'Antes', diff_after:'Después'
  },
  admin: {
    users_title:'Usuarios', users_invite:'Invitar usuario',
    knowledge_title:'Flujo de conocimiento', knowledge_promote:'Promover',
    knowledge_scope_global:'Global', knowledge_scope_org:'Organización',
    knowledge_scope_dept:'Departamento', knowledge_scope_user:'Usuario',
    audit_title:'Auditoría', audit_export:'Exportar CSV',
    tenant_title:'Tenant', tenant_identity:'Identidad SSO',
    tenant_retention:'Retención', tenant_branding:'Branding',
    tenant_flags:'Feature flags', tenant_smtp:'SMTP (Postmark)', tenant_backup:'Backup',
    connectors_title:'Conectores', connector_connected:'Conectado',
    connector_disconnected:'Desconectado', connector_planned:'Planificado',
    break_glass:'Activar break-glass', break_glass_warn:'Acceso admin privilegiado. Máximo 8h. Requiere MFA.'
  },
  ops: {
    health_title:'Ops Health', containers:'Contenedores', slos:'SLOs',
    jobs:'Jobs', alerts:'Alerts', tables:'Tablas FROZEN'
  },
  states: {
    drafting:'Redactando', awaiting_approval:'Esperando aprobación',
    approved:'Aprobado', executing:'Ejecutando',
    waiting_external:'Esperando señal externa', blocked:'Bloqueado',
    completed:'Completado', failed:'Fallido', escalated:'Escalado'
  },
  risk: {
    reversibility:'Reversibilidad', side_effects:'Efectos colaterales',
    min_autonomy:'Autonomía mínima', required_role:'Rol requerido', audit_class:'Clase auditoría',
    reversible_24h:'Reversible ≤24h', reversible_cost:'Reversible con costo',
    irreversible:'Irreversible', irreversible_cost:'Irreversible con costo'
  }
};
```

Equivalentes EN y PT-BR. Todas las claves deben existir en los 3 idiomas (fallback silencioso a ES si falta).

---

## §11 · Boot (fragment `03_boot.js.fragment`)

Expone `window.__faberloom = { bus, store, i18n, theme, a11y, router, boot }`.

### 11.1 Bus
Pub/sub simple. Eventos: `view-state:change`, `launcher:open`, `feedback:open`, `feedback:submit`, `consolidation:open`, `consolidation:submit`, `toast`, `role:change`, `tenant:change`, `lang:change`, `theme:change`, `route:change`.

### 11.2 Store
Wrapper sobre localStorage con prefijo `faberloom.v1.` y fallback a Map in-memory si localStorage falla (file:// en algunos browsers). Versionado: si la versión del schema cambia, wipe.

### 11.3 i18n
- `i18n.t(key, vars?)` con lookup en dict del idioma activo, fallback a ES, retorna `[??key]` si no existe (para debug).
- `i18n.setLang(lang)` emite `bus.emit('lang:change', lang)` y dispara re-render de la vista actual.
- `i18n.applyToDom(root)` reemplaza textContent de todo `[data-i18n]` y placeholder de `[data-i18n-placeholder]`.

### 11.4 Theme
- `theme.set('light'|'dark')` setea `html[data-theme]` y persiste.
- `theme.toggle()` alterna.
- Respeta `prefers-color-scheme` solo en primer load (no overrides posteriores).

### 11.5 a11y
- Skip-link injection.
- Focus management: al cambiar ruta, enfocar `<main id="fl-slot">` tras el mount.
- Live region updates.
- Botón Validar que carga axe-core por CDN y corre sobre `<main>`.

### 11.6 Router
- Parseo de hash `#/ruta/:param` → `{ path, params, query }`.
- Tabla `ROUTES[path] = moduleId`.
- Mount con **error boundary**: wrap en try/catch · si truena, renderiza `DegradedCard` + emite `bus.emit('toast',{kind:'error',...})` · guarda ruta en `window.__faberloom.failedRoutes` para reintento.
- Navegación programática `router.navigate(hash)`.
- Default → `#/bandeja/dr_001` en primera carga (demo-crítico).

### 11.7 Boot.init
- Detecta tema inicial.
- Carga lang por defecto ES.
- Renderiza shell.
- Attach listeners al router.
- Dispara primera navegación.

---

## §12 · Acceptance criteria (25+ binarios)

**Globales:**
1. `python build.py` genera `index-standalone.html` sin errores.
2. Doble clic sobre el HTML lo abre en navegador y carga sin errores en consola.
3. Tamaño final entre 700 KB y 2 MB (no explotar con mock bloat).
4. No hay `import`/`export` / `fetch()` / `require()` en el HTML final.
5. Todas las imágenes son SVG inline (verificable con grep `<img src=` → 0 matches).
6. Todas las rutas del sidebar (13) cargan sin crash.
7. Cambio de idioma actualiza topbar + sidebar + módulo activo sin reload.
8. Toggle light/dark actualiza tokens en <1s sin flash.
9. View-state dropdown alterna los 4 estados en el módulo activo.
10. Cambio de rol `operator` oculta bloque GESTIÓN del sidebar.

**Bandeja detail (demo-crítico):**
11. Ruta `#/bandeja/dr_001` muestra 6 claims con evidencia en tab Evidencia.
12. Tab Trace muestra los 7 pasos del workflow con ts y estado.
13. Botón Feedback abre FeedbackModal con las 5 razones radio.
14. Aprobar acción irreversible exige doble confirmación.

**Skill Studio:**
15. Ruta `#/skills/sk_cotizar` muestra 3 columnas con contenido del mock.
16. Thermometer en estado `hot` (6 patrones) activa botón Consolidar.
17. Base sellada es read-only (input disabled, sin botón delete).

**Agent Console:**
18. Ruta `#/agentes/ag_cotizador` muestra autonomy ladder L0-L4 con L1 activo y criterion visible.
19. 5 KPIs renderizados con valores del mock.

**Workflows:**
20. Canvas renderiza 7 nodos coloreados según tipo.
21. Click en nodo abre inspector con detalles.

**Admin:**
22. Admin Audit muestra 60+ eventos con filtros operativos.
23. Admin Knowledge muestra scope tree con 4 niveles.
24. Admin Connectors muestra 5 conectores con 3 estados distintos.

**Ops:**
25. Ops Health muestra 11+4 containers, SLOs, jobs, alerts, y 20 tablas FROZEN.

**A11y:**
26. Botón Validar corre axe-core y muestra resultados (0 violations nivel A obligatorio, 0 críticas AA).
27. Skip-link visible al Tab desde url bar.
28. Todos los focus rings visibles en 2px coral.
29. `prefers-reduced-motion` desactiva animaciones.

**Error boundary:**
30. Forzar error en un módulo (ej: borrar mock de un agente) renderiza `DegradedCard` con botón Reintentar — el shell sigue operativo.

---

## §13 · Fases de ejecución

### Fase 1 — Research (3 sub-agentes paralelos)
- **A1 lee** SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md y extrae lista canónica de: estados, scopes, roles, políticas, 6 campos action-risk.
- **A2 lee** faberloom_v2.html y index-standalone.html existente y documenta qué ya está hecho y qué falta.
- **A3 lee** memoria de marca + tokens existentes y genera la paleta completa dark-mode verificada WCAG AA.

Output: `faberloom-mockup/research_synthesis.md` (200-400 líneas).

### Fase 2 — Infraestructura base (main thread, secuencial)
- Crear `build.py`.
- Crear `fragments/00_head.html.fragment`, `01_design_tokens.css.fragment`, `02_base_styles.css.fragment`, `03_boot.js.fragment`, `04_shell.html.fragment`, `05_mock_data.js.fragment`, `06_widgets.js.fragment`, `07_i18n_es.js.fragment`, `07_i18n_en.js.fragment`, `07_i18n_pt.js.fragment`, `99_footer.html.fragment`.
- Correr `python build.py` — debe generar HTML vacío con shell, sin módulos todavía.

### Fase 3 — Módulos (9 sub-agentes paralelos)
Cada sub-agente toma UN módulo y escribe su fragment siguiendo el contrato de §3.1 y las specs de §8.

| Agente | Módulo |
|--------|--------|
| B1 | `10_module_bandeja_lista.html.fragment` |
| B2 | `11_module_bandeja_detail.html.fragment` |
| B3 | `12_module_skill_studio.html.fragment` |
| B4 | `13_module_agent_console.html.fragment` |
| B5 | `14_module_workflows_canvas.html.fragment` |
| B6 | `16_module_consolidation.html.fragment` + `15_module_runs_timeline.html.fragment` |
| B7 | `20_module_admin_users.html.fragment` + `23_module_admin_tenant.html.fragment` |
| B8 | `21_module_admin_knowledge.html.fragment` + `22_module_admin_audit.html.fragment` + `24_module_admin_connectors.html.fragment` |
| B9 | `30_module_ops_health.html.fragment` + `31_module_design_system.html.fragment` |

Cada agente recibe en su contexto: §3.1, §6, §7 (solo las colecciones que su módulo consume), §8.x (su ficha), §10 (claves i18n de su dominio).

### Fase 4 — Ensamblado (main thread)
- Correr `python build.py`.
- Abrir `index-standalone.html` en browser.
- Navegar por las 13 rutas, verificar AC 1-30.
- Fix loop: si algún módulo truena, relanzar sub-agente específico con el error.

### Fase 5 — Verificación (2 sub-agentes)
- **V1:** Corre axe-core en las 13 rutas y reporta violations.
- **V2:** Valida trazabilidad matriz (§14): cada concepto del SPEC tiene presencia visible en al menos una ruta.

Output final: `faberloom-mockup/verification_report.md`.

---

## §14 · Apéndice A — Matriz de trazabilidad (SPEC → HTML)

Checklist que V2 debe marcar en verde:

| # | Concepto SPEC | Fragment | Selector/evidencia visible |
|---|---------------|----------|----------------------------|
| 1  | AgentSpec                         | skill-studio | col "Base sellada" con systemPrompt + hash versión |
| 2  | AgentRuntime                      | agent-console | header con estado `running` |
| 3  | AgentMemory (3 capas)             | agent-console | tab Memoria con 3 secciones |
| 4  | State drafting                    | bandeja-lista | DraftStateBadge color amber |
| 5  | State awaiting_approval           | bandeja-detail | header badge + botón Aprobar |
| 6  | State approved                    | bandeja-lista | badge sage |
| 7  | State executing                   | runs-timeline | entries con status=active |
| 8  | State waiting_external_signal     | workflows-canvas | nodo con status=pending en inspector |
| 9  | State blocked                     | bandeja-lista | filtro disponible |
| 10 | State completed                   | runs-timeline | entries con finalState=completed |
| 11 | State failed                      | runs-timeline + bandeja-lista | badge deep-coral |
| 12 | State escalated                   | bandeja-lista | badge + tooltip |
| 13 | Autonomy L0 Shadow                | agent-console | Ladder con L0 label |
| 14 | Autonomy L1 Propone               | agent-console | Ladder L1 activo en ag_cotizador |
| 15 | Autonomy L2 Auto-bajo             | agent-console | Ladder label |
| 16 | Autonomy L3 Auto+notif            | agent-console | Ladder label |
| 17 | Autonomy L4 Auto+excepciones      | agent-console | Ladder label |
| 18 | Unlock criterion textual          | agent-console | textbox debajo de Ladder |
| 19 | 3 capas skill base/manual/learned | skill-studio | 3 columnas |
| 20 | Base sellada read-only            | skill-studio | inputs disabled |
| 21 | Gate humano learned overlay       | skill-studio + consolidation | ConsolidationModal con approve por fila |
| 22 | Provenance claim→evidence→source  | bandeja-detail | tab Evidencia con ProvenanceSupport |
| 23 | source_version en evidencia       | bandeja-detail | columna version visible |
| 24 | retrieval_run_id                  | bandeja-detail | footer de evidencia |
| 25 | Action-risk registry 6 campos     | bandeja-detail | tab Riesgo con 6 filas |
| 26 | Reversibility states              | RiskBadge | tooltip con los 4 niveles |
| 27 | Workflow state ledger             | bandeja-detail | tab Trace con 7 pasos |
| 28 | 4 scopes knowledge                | admin-knowledge | tree con global/org/dept/user |
| 29 | business_entity_id metadata       | admin-knowledge + bandeja-lista | columna + filtro |
| 30 | 3 roles (owner/admin/operator)    | topbar switcher + admin-users | dropdown + tabla |
| 31 | Private-by-default                | admin-knowledge | chunk user invisible a admin ajeno |
| 32 | Break-glass 8h MFA                | admin-users | botón con modal MFA + timer 8h visible |
| 33 | RLS session-scoped                | ops-health | indicator SET LOCAL en debug panel |
| 34 | TTL 90d learned overlay           | skill-studio | config slider TTL |
| 35 | 5 razones feedback                | feedback-modal | 5 radios |
| 36 | Candidate/Active/Archived         | consolidation | 3 columnas Kanban |
| 37 | Thermometer 🔵🟡🔴                | skill-studio header | widget visible |
| 38 | Consolidación gate humano         | consolidation | modal con approve por fila |
| 39 | Leakage tests pytest              | ops-health | job leakage_tests visible |
| 40 | Backup RPO 24h / RTO 2h           | admin-tenant | sección Backup con valores |
| 41 | Postmark SMTP                     | admin-tenant + connectors | config + conector |
| 42 | Outbox pattern                    | ops-health | tabla con job_execution |
| 43 | Scheduler UNIQUE(name, sched_for) | ops-health | columna scheduledFor sin duplicados |
| 44 | Prometheus + Grafana staging      | ops-health | tile Observability con link placeholder |
| 45 | Jaeger OFF S1                     | ops-health | flag deshabilitado visible |
| 46 | 20 tablas FROZEN                  | ops-health | tabla Tables con 20 filas |
| 47 | 11 containers staging             | ops-health | tile con 11 entradas |
| 48 | 4 containers dev                  | ops-health | tile con 4 entradas |
| 49 | UUIDv7                            | ops-health + debug | id format en mock.tables |
| 50 | Beta slice 2026-04-20→06-14       | admin-tenant | sección Plan con fechas |
| 51 | i18n ES/EN/PT-BR                  | topbar switcher | 3 botones |
| 52 | 332+ claves i18n                  | fragment i18n | conteo verificable |
| 53 | Brand coral/cream/warm-dark       | design-system | token grid |
| 54 | Georgia italic display            | design-system | sección tipografía |
| 55 | Inter body + JetBrains mono       | design-system | sección tipografía |
| 56 | Draft-first workflow              | bandeja-lista | todos los drafts en estado no-completed al inicio |
| 57 | Error boundary DegradedCard       | design-system + forzar error | card visible con Retry |
| 58 | Skip-link                         | shell | tab desde url bar revela skip link |
| 59 | Live region polite                | shell | `#fl-live` presente |
| 60 | axe-core on demand                | topbar Validar | drawer de resultados |

V2 debe producir reporte con 60/60 verdes o explicar cada ausencia.

---

## §15 · Apéndice B — Glosario mínimo

- **Fragment:** archivo bajo `fragments/` con extensión `*.html.fragment` / `*.css.fragment` / `*.js.fragment` que `build.py` concatena.
- **Módulo:** unidad de UI asociada a una ruta (`#/...`), registrada en `window.__faberloom.modules`.
- **Widget:** componente UI reusable, registrado en `window.__faberloom.widgets`.
- **Claim:** afirmación generada por el agente dentro de un draft. Tiene `id` y una lista de `evidence_span_id`.
- **Evidence span:** fragmento de fuente que respalda un claim. Tiene `source`, `source_version`, `line`, `retrieval_run_id`.
- **Action-risk:** 6 campos (`action_id`, `reversibility`, `side_effects`, `min_autonomy`, `required_role`, `audit_class`) asociados a una acción con efecto externo.
- **Autonomy Ladder:** L0-L4, no es toggle, cada nivel tiene `unlock_criterion` textual.
- **Thermometer:** indicador de "heat" del skill = cuántos patrones learned pendientes → cold 0-2, warm 3-5, hot 6+.
- **Consolidation:** pipeline Candidate → Active → Archived/Reverted que gatea la promoción de learned patterns a base sellada (gate humano).
- **Break-glass:** sesión privilegiada del Tenant Owner con MFA, time-bound 8h, permite visibilidad intra-org incluyendo user-scope ajeno.
- **Scope:** nivel de visibilidad de un memory_chunk — global / org / dept / user. business_entity_id es metadata ortogonal, no un 5º scope.

---

## §16 · Reglas inquebrantables

1. **NO re-debatir decisiones cerradas del SPEC.** Si algo falta, agregarlo; si algo entra en conflicto, parar y escalar — no inventar.
2. **NO hardcodear texto de UI en módulos.** Todo pasa por `i18n.t()`.
3. **NO usar import/export/fetch.** `file://` lo prohíbe.
4. **NO eliminar el contrato de fragment.** Todos los módulos siguen el patrón de §3.1.
5. **NO mezclar lógica de negocio en widgets.** Widgets son puros de presentación + emit events.
6. **NO saltarse la trazabilidad matriz.** 60 filas, todas evidenciables.
7. **NO generar el HTML final a mano.** Siempre via `build.py`.
8. **NO dejar `console.log` en producción del fragment.** Permitido durante debug, limpiar antes del commit.
9. **NO asumir network.** Offline-first: fonts vía CDN con `font-display: swap`, fallback a system fonts.
10. **NO saltarse el error boundary.** Cada mount envuelto.

---

## §17 · Cómo arranca Claude Code

1. **Leer en orden:** §0 archivos, §1 restricciones, §2 estructura, §3 contrato, §4 integrador, §5-7 especificaciones.
2. **Crear `build.py`** (§4).
3. **Lanzar Fase 1** (research sub-agentes A1, A2, A3 en paralelo).
4. **Ejecutar Fase 2** (infra base secuencial).
5. **Correr `python build.py`** para verificar shell vacío.
6. **Lanzar Fase 3** (9 sub-agentes en paralelo).
7. **Ejecutar Fase 4** (ensamblar + fix loop hasta 30/30 AC).
8. **Lanzar Fase 5** (verificación).
9. **Entregar:** `faberloom-mockup/index-standalone.html` + `verification_report.md` + summary con:
   - rutas funcionales (13/13 esperadas),
   - AC pasadas (X/30),
   - trazabilidad SPEC (X/60),
   - violations axe (0 críticas esperadas).

Doble clic y listo. Si algo se rompe: identificar el fragment → relanzar el sub-agente específico → `python build.py` → reabrir.

---

**Fin del prompt. Ejecutar con disciplina de frontera — no inventar fuera del SPEC.**
