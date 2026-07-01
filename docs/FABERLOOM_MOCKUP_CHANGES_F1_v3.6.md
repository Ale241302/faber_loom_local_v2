---
id: FABERLOOM_MOCKUP_CHANGES_F1_v3.6
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FABERLOOM
authors: [alvaro_alfaro, claude_cowork_2026-04-21]
inputs:
  - SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT (v1.0)
  - SPEC_FABERLOOM_SKILL_COMPOSITION_v1 (v1.0)
  - SPEC_FABERLOOM_AGENT_COMPOSITION_v1 (v1.1 con addendum)
  - SPEC_FABERLOOM_WORKFLOW_ENGINE_v1 (v1.0)
  - docs/archivo/kimi_swarm_3_workflows_autonomous.md
  - mockup actual: faberloom_v2.html (5801 líneas, commit vigente 2026-04-21)
audience: claude_code (implementa refactor HTML), alvaro (revisa y aprueba)
scope: Rehacer faberloom_v2.html para alinear UI con Fase 1 canonizada (pg-boss + YAML DSL + 4 patrones handoff + Authority Mode + sandwich contención + PatchRAG + Langfuse + 5 templates wedge). Pantalla por pantalla: qué modificar, qué añadir, qué remover.
output_target: faberloom_v3.html (nuevo archivo, NO sobreescribir v2 hasta validación)
aplica_a: [FaberLoom]
---

# Propuesta de cambios al mockup — FaberLoom Fase 1

**Objetivo:** alinear el prototipo HTML con las 4 SPECs canonizadas (2026-04-21). Claude Code implementa; Álvaro revisa pantalla por pantalla.

**Regla sagrada mantenida:** el mockup ya tiene draft-first + HITL + evidence drawer + Shadow Mode + 3 capas de instrucciones. Esto NO se toca — se extiende. Las piezas conceptuales nuevas (Authority Mode, Autonomy Ladder L0-L4, Sealed/Open, Add-ons, Templates wedge, Workflow Runs, PatchRAG, kill switch) se añaden sin romper la UX existente.

**Archivo resultado:** `faberloom_v3.html` (nuevo). Mantener `faberloom_v2.html` intacto como baseline hasta aprobación final.

---

## 0 · Prerequisitos de implementación

Antes de tocar HTML:

1. **Validar sintaxis**: `node --check faberloom_v3.html` debe pasar antes de cada commit (regla de memoria feedback_faberloom_prototype).
2. **Preservar navegación**: el `router` y la `appShell` siguen idénticos. Se añaden rutas nuevas, no se renombran las existentes.
3. **No acoplar**: cada `render*` queda autosuficiente. Si una pantalla necesita data nueva, se añade al `MOCK` global, no se consulta API real.
4. **Stack de tokens CSS**: los tokens de brand (coral, cream, dark) existentes se respetan. Se añaden tokens nuevos documentados abajo.

---

## 1 · Cambios globales (aplican a todas las pantallas)

### 1.1 Tokens CSS nuevos

Añadir en el bloque `:root` (y su gemelo dark):

```css
/* Authority Mode colors (5 niveles) */
--auth-signal: #7A8A9C;       /* SEÑALA — gris azulado neutro */
--auth-propose: #B98E4A;      /* PROPONE — coral amarillo */
--auth-exec-approve: #E26B3A; /* EJECUTA_CON_APROBACIÓN — coral primary */
--auth-exec-solo: #C44A3E;    /* EJECUTA_SOLO — rojo controlado */
--auth-external-lock: #931C1C; /* canal externo siempre gate, color alarma */

/* Autonomy Ladder L0-L4 */
--ladder-l0: #7A8A9C; /* Shadow */
--ladder-l1: #8D9CB0;
--ladder-l2: #B98E4A;
--ladder-l3: #E26B3A;
--ladder-l4: #2E7D32; /* Autonomous con HITL */

/* Learning / PatchRAG */
--learning-hot: #E26B3A;     /* termómetro aprendizaje activo */
--learning-cool: #7A8A9C;    /* sin cambios recientes */
--patch-accepted: #2E7D32;
--patch-candidate: #B98E4A;
--patch-reverted: #C44A3E;

/* Sealed vs Open badges */
--sealed-bg: #F5EFE4;         /* cream suave */
--sealed-fg: #5A4A2C;
--open-bg: #FDEDE4;           /* coral pálido */
--open-fg: #8B3A1E;
```

### 1.2 Componentes reutilizables nuevos

Añadir funciones helper arriba de `renderLanding` (antes del primer `render*`):

```javascript
/* ═══════════════════════════════════════════════════════════════
   AUTHORITY MODE · LADDER · SEALED/OPEN · BADGES
   ═══════════════════════════════════════════════════════════════ */

function authorityBadge(mode) {
  // mode: 'signal' | 'propose' | 'exec_approve' | 'exec_solo'
  const labels = {
    signal: 'SEÑALA',
    propose: 'PROPONE',
    exec_approve: 'EJEC · aprobación',
    exec_solo: 'EJEC · solo',
  };
  const colors = {
    signal: '--auth-signal',
    propose: '--auth-propose',
    exec_approve: '--auth-exec-approve',
    exec_solo: '--auth-exec-solo',
  };
  return `
    <span class="auth-badge" style="background:var(${colors[mode]});color:white;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:600;letter-spacing:0.02em">
      ${labels[mode]}
    </span>`;
}

function ladderPip(current) {
  // current: 0..4
  const levels = ['L0 Shadow', 'L1', 'L2', 'L3', 'L4 Auto'];
  return `
    <div class="ladder-pip" style="display:flex;gap:3px;align-items:center">
      ${levels.map((l, i) => `
        <span class="pip ${i <= current ? 'pip-on' : 'pip-off'}"
              style="width:${i === current ? '22px' : '10px'};height:6px;border-radius:3px;
                     background:${i <= current ? 'var(--ladder-l' + Math.min(i, 4) + ')' : 'var(--border-subtle)'}"
              title="${l}"></span>`).join('')}
      <span class="text-xs text-muted" style="margin-left:6px">L${current}</span>
    </div>`;
}

function sealedOpenBadge(kind) {
  // kind: 'sealed' | 'open'
  if (kind === 'sealed') {
    return `<span class="pill" style="background:var(--sealed-bg);color:var(--sealed-fg);font-size:10px">
      <svg class="ico-sm ico" style="width:10px;height:10px"><use href="#i-lock"/></svg> Sealed
    </span>`;
  }
  return `<span class="pill" style="background:var(--open-bg);color:var(--open-fg);font-size:10px">
    <svg class="ico-sm ico" style="width:10px;height:10px"><use href="#i-edit"/></svg> Open
  </span>`;
}

function learningThermometer(tempPct) {
  // tempPct: 0..100, intensidad actividad aprendizaje última 7d
  const color = tempPct > 60 ? 'var(--learning-hot)' : tempPct > 30 ? 'var(--patch-candidate)' : 'var(--learning-cool)';
  return `
    <div class="learning-therm" title="Actividad PatchRAG 7d: ${tempPct}%"
         style="display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border-radius:12px;
                background:var(--bg-subtle);border:1px solid var(--border-subtle)">
      <span style="width:8px;height:8px;border-radius:50%;background:${color};box-shadow:0 0 8px ${color}"></span>
      <span class="text-xs">${tempPct}%</span>
    </div>`;
}

function depthBudget(depthRemaining, maxDepth, budgetRemaining, budgetMax) {
  // Visualización de contadores anti-loop
  return `
    <div class="depth-budget" style="display:flex;gap:12px;font-size:11px;font-family:'JetBrains Mono',monospace">
      <span title="Profundidad restante de composición">
        <svg class="ico-sm ico" style="width:10px;height:10px"><use href="#i-layers"/></svg>
        ${depthRemaining}/${maxDepth}
      </span>
      <span title="Budget USD restante este run">
        $ ${budgetRemaining.toFixed(2)}/${budgetMax.toFixed(2)}
      </span>
    </div>`;
}
```

### 1.3 Íconos nuevos (añadir al sprite SVG existente)

```
#i-layers     — depth/composición (stack layers)
#i-yaml       — archivo YAML
#i-template   — template pre-armado
#i-fork       — fork sealed→open
#i-kill       — kill switch (cuadrado rojo con pausa)
#i-circuit    — circuit breaker
#i-langfuse   — trace/observability (ojo con líneas)
#i-canary     — canary deploy (pajarito o partículas)
#i-patch      — PatchRAG (parche tipo cruz)
```

### 1.4 MOCK data nuevo (inicializar al tope)

Añadir a `MOCK` objeto global:

```javascript
MOCK.templates = [
  { id: 't-cotizacion-b2b', name: 'Cotización Rápida B2B',
    sector: 'Calzado seguridad', authority_mode: 'propose',
    autonomy_level: 'L1', runs: 42, approval_rate: 91,
    p95_latency_s: 187, cost_avg_usd: 0.34,
    description: 'QualifyBot analiza RFQ, cruza catálogo, redacta cotización. Gerente aprueba.' },
  { id: 't-cobranza', name: 'Cobranza Inteligente',
    sector: 'Cross-sector', authority_mode: 'propose',
    autonomy_level: 'L1', runs: 18, approval_rate: 88,
    p95_latency_s: 45, cost_avg_usd: 0.12,
    description: 'CollectionBot redacta recordatorio escalado. Auto-approve si <$5k MXN + conf>0.85.' },
  { id: 't-stock-bajo', name: 'Alerta Stock Bajo',
    sector: 'Cross-sector', authority_mode: 'signal',
    autonomy_level: 'L2', runs: 156, approval_rate: 100,
    p95_latency_s: 12, cost_avg_usd: 0.02,
    description: 'Determinístico · cron 6h · alerta admin cuando stock<reorder_point.' },
  { id: 't-bienvenida', name: 'Bienvenida Nuevos Clientes',
    sector: 'Cross-sector', authority_mode: 'exec_solo',
    autonomy_level: 'L3', runs: 23, approval_rate: 96,
    p95_latency_s: 8, cost_avg_usd: 0.01,
    description: 'NotifierBot · template pre-aprobado · envío inmediato tras creación en CRM.',
    external_lock: false /* template legal + marketing pre-aprobó */ },
  { id: 't-post-venta', name: 'Seguimiento Post-Venta',
    sector: 'Cross-sector', authority_mode: 'exec_approve',
    autonomy_level: 'L2', runs: 5, approval_rate: 100,
    p95_latency_s: 23, cost_avg_usd: 0.08,
    description: 'SurveyBot · NPS post-delivery · graduará a EJEC_SOLO tras 5 envíos con 90%+ aprobación.' },
];

MOCK.workflowRuns = [
  { id: 'run-001', template_id: 't-cotizacion-b2b', started: '2026-04-21 09:23:45',
    duration_s: 154, status: 'succeeded', cost_usd: 0.41, trace_url: '#langfuse/trace/abc123',
    steps: 6, depth_used: 1, tenant: 'muitowork' },
  { id: 'run-002', template_id: 't-cobranza', started: '2026-04-21 08:15:02',
    duration_s: 38, status: 'awaiting_approval', cost_usd: 0.09, trace_url: '#langfuse/trace/def456',
    steps: 4, depth_used: 0, tenant: 'muitowork' },
  { id: 'run-003', template_id: 't-cotizacion-b2b', started: '2026-04-20 16:42:11',
    duration_s: 212, status: 'circuit_broken', cost_usd: 0.15,
    error: 'circuit_breaker: 3 fallos consecutivos al consultar SP-API',
    trace_url: '#langfuse/trace/ghi789', steps: 3, depth_used: 1, tenant: 'muitowork' },
];

MOCK.goldSamples = [
  { id: 'gs-001', skill: 'qualify_b2b_quote', stage: 'active',
    input_summary: 'RFQ 120 pares Goliath bota alta · Distribuidora Seguridad MX',
    expected_output_summary: 'Cotización $48.40/par · 15 días entrega · términos 30 días',
    runs_matched: 12, confidence_current: 94, last_updated: '2026-04-18' },
  { id: 'gs-002', skill: 'qualify_b2b_quote', stage: 'candidate',
    input_summary: 'RFQ sin cantidad especificada · pedido info producto',
    expected_output_summary: 'Request clarification antes de cotizar',
    runs_matched: 3, confidence_current: 68, last_updated: '2026-04-20' },
  { id: 'gs-003', skill: 'collection_reminder', stage: 'archived',
    input_summary: 'Factura vencida 15 días · cliente recurrente',
    expected_output_summary: 'Recordatorio suave con términos · ofrece plan pago',
    runs_matched: 8, confidence_current: 87, last_updated: '2026-04-10',
    archived_reason: 'Reemplazada por gs-019 con mejor tono' },
];

MOCK.tenantBudget = {
  daily_llm_cap_usd: 20,      /* Pilot pago */
  daily_llm_used_usd: 8.42,
  free_tier_cap_usd: 5,
  kill_switch_armed: false,   /* auto-armed si cost z-score > 4 */
  canary_tenant: 'marluvas-pilot',  /* deploy a este primero */
};

MOCK.circuitBreakers = [
  { workflow_id: 't-cotizacion-b2b', state: 'closed', failure_count: 0, last_failure: null },
  { workflow_id: 't-cobranza', state: 'half-open', failure_count: 2,
    last_failure: '2026-04-21 07:30:00', fallback_enabled: true },
  { workflow_id: 't-amazon-sp', state: 'open', failure_count: 3,
    last_failure: '2026-04-21 08:40:15', reopens_at: '2026-04-21 09:10:15' },
];
```

---

## 2 · Cambios por pantalla

### 2.1 `renderLanding` (L2988-3210)

**Cambios mínimos.** El mensaje está alineado con la SPEC (draft-first, control plane, wedge calzado seguridad).

**Añadir:**
- En el bloque `hero-meta` (L3022), agregar una tercera pill: `<span class="pill pill-neutral">Beta · 8 semanas · 3 design partners</span>`
- En el `how-section` (L3090), ajustar paso 03 para mencionar explícitamente PatchRAG:
  - **Antes:** "Genera la cotización con evidencia: 4 fuentes citadas, confianza 92%"
  - **Después:** "Genera la cotización usando patches aprendidos de cotizaciones anteriores (PatchRAG) + 4 fuentes citadas + confianza 92%"

**Remover:** nada.

**Justificación:** el landing ya vende correctamente la propuesta. Solo refinar vocabulario para que F1 quede visible a visitors técnicos que miren el demo.

---

### 2.2 `renderDashboard` (L3265-3412)

**Cambios mayores** — el dashboard es la pantalla que Álvaro mira cada mañana. Necesita reflejar las métricas F1 canonizadas.

**Añadir al `kpi-grid` (L3329-3350):** añadir un 5º KPI card (reemplazar grid 4-col por 5-col responsive):

```html
<div class="kpi-card kpi-cost">
  <div class="kpi-label">Cost per run promedio</div>
  <div class="kpi-value tabular">$0.34<span class="unit"></span></div>
  <div class="kpi-delta"><span class="up">-8%</span> vs sem. prev · target <$0.50</div>
</div>
```

**Añadir panel nuevo en `dash-grid-2` (reemplazar "Control operativo" existente en L3378-3407):**

Ampliar el panel "Control operativo" con secciones nuevas:

```html
<div class="panel card-padded">
  <div class="flex items-center gap-3 mb-3">
    <div class="activity-dot evidence"><svg class="ico"><use href="#i-shield"/></svg></div>
    <div>
      <div class="font-semibold" style="font-size:14px">Control operativo · Fase 1</div>
      <div class="text-xs text-muted">Últimas 24 horas · tenant ${MOCK.user.org}</div>
    </div>
  </div>

  <!-- Row existente: Acciones bloqueadas por policy -->
  <!-- Row existente: Drafts con revisión manual -->
  <!-- Row existente: Shadow runs evaluados -->

  <!-- NUEVOS ROWS F1 -->
  <div style="padding:12px 0;border-bottom:1px solid var(--border-subtle)">
    <div class="flex items-center justify-between mb-1">
      <span class="text-sm">Budget LLM diario</span>
      <span class="tabular font-semibold">$${MOCK.tenantBudget.daily_llm_used_usd} / $${MOCK.tenantBudget.daily_llm_cap_usd}</span>
    </div>
    <div class="text-xs text-muted">Kill switch: ${MOCK.tenantBudget.kill_switch_armed ? 'ARMADO ⚠️' : 'inactivo'} · trigger: z-score cost > 4</div>
  </div>
  <div style="padding:12px 0;border-bottom:1px solid var(--border-subtle)">
    <div class="flex items-center justify-between mb-1">
      <span class="text-sm">Circuit breakers</span>
      <span class="tabular font-semibold">${MOCK.circuitBreakers.filter(c => c.state !== 'closed').length} abiertos</span>
    </div>
    <div class="text-xs text-muted">Amazon SP-API · token_expired · reopen en 12 min</div>
  </div>
  <div style="padding:12px 0">
    <div class="flex items-center justify-between mb-1">
      <span class="text-sm">PatchRAG · patches aplicados hoy</span>
      <span class="tabular font-semibold">14</span>
    </div>
    <div class="text-xs text-muted">3 candidatos en pipeline · ver Gold Samples</div>
  </div>
</div>
```

**Añadir botón en header (L3319-3327):** al lado de "Ver bandeja", añadir:

```html
<button class="btn btn-secondary" onclick="go('workflow-runs')">
  <svg class="ico-sm ico"><use href="#i-activity"/></svg>Ver runs
</button>
```

**Remover:** nada. El dashboard mantiene estructura + agrega capas.

**Justificación:** sin cost-per-run, budget cap visible y circuit breakers, Álvaro no puede detectar runaway antes de que le cueste dinero. Todo viene del Go/No-Go checklist §13 de SPEC_WORKFLOW_ENGINE.

---

### 2.3 `renderBandeja` (L3421-3670)

**Cambios focalizados** en la tab `aprobar` y visualización del contexto Authority Mode.

**Modificar `renderBandejaAprobar` (L3495-3581)** — en el `draft-list-row` (L3522-3552), añadir badge de Authority Mode + depth remaining:

```javascript
// Después de la pill pill-coral del agente, añadir:
<span class="auth-badge-inline">${authorityBadge(d.authority_mode || 'propose')}</span>
<span class="ladder-inline">${ladderPip(d.autonomy_level || 1)}</span>
```

**Añadir campo en cada draft de MOCK.drafts:**
```javascript
authority_mode: 'propose',  // o 'exec_approve' según workflow
autonomy_level: 1,
depth_remaining: 1,
budget_used_usd: 0.34,
budget_max_usd: 1.00,
idempotency_key: 'rfq-goliath-120-20260421',
sla_remaining_min: 45,  // para mostrar countdown
```

**Añadir "batch approve" solo para `exec_approve` mode:**

Añadir chip filter nuevo en toolbar (L3561-3567):

```html
${chip('exec_approve', 'Modo: EJEC con aprobación', counts.exec_approve)}
${chip('batch_ready', 'Listos para batch (conf≥90)', counts.batch_ready)}
```

Y un botón "Aprobar lote" visible solo cuando el filter `batch_ready` está activo:

```html
<button class="btn btn-primary btn-sm" onclick="batchApprove()">
  <svg class="ico-sm ico"><use href="#i-check"/></svg>
  Aprobar lote (${counts.batch_ready})
</button>
```

**Añadir SLA countdown en cada row:** al lado del `confidence-block` (L3542-3545):

```html
<div class="sla-block" style="min-width:80px;text-align:center">
  <div class="sla-countdown ${d.sla_remaining_min < 15 ? 'sla-urgent' : ''}" style="font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:600">
    ${d.sla_remaining_min}m
  </div>
  <div class="text-xs text-muted">SLA</div>
</div>
```

**Remover:** nada.

**Justificación:** el mockup no expone Authority Mode ni SLA — crítico para que el aprobador sepa por qué esto requiere su atención vs otro draft. Viene de SPEC_WORKFLOW_ENGINE §5.3 y SPEC_AGENT_COMPOSITION §18.2.

---

### 2.4 `renderConsole` (L3675-3803)

**Cambios en panel lateral de evidencia + panel nuevo de control.**

**Modificar el header del draft (en el cuerpo central):** añadir bloque de contexto Authority Mode + Autonomy Ladder visible:

```html
<div class="console-auth-strip" style="padding:12px;background:var(--bg-subtle);border-radius:6px;margin-bottom:16px;
                                        display:grid;grid-template-columns:auto auto auto 1fr;gap:16px;align-items:center">
  <div>
    <div class="text-xs text-muted">Authority Mode</div>
    ${authorityBadge(draft.authority_mode)}
  </div>
  <div>
    <div class="text-xs text-muted">Autonomy</div>
    ${ladderPip(draft.autonomy_level)}
  </div>
  <div>
    <div class="text-xs text-muted">Depth / Budget</div>
    ${depthBudget(draft.depth_remaining, 2, draft.budget_max_usd - draft.budget_used_usd, draft.budget_max_usd)}
  </div>
  <div style="text-align:right">
    <div class="text-xs text-muted">Idempotency key</div>
    <code style="font-size:10px">${draft.idempotency_key}</code>
  </div>
</div>
```

**Añadir al evidence drawer (L3680-3690):** una sección "Patches aplicados" para mostrar PatchRAG en acción:

```html
<div class="evidence-section" style="margin-top:16px">
  <div class="evidence-section-title" style="font-size:11px;text-transform:uppercase;letter-spacing:0.04em;color:var(--text-muted);margin-bottom:8px">
    Patches PatchRAG aplicados (3)
  </div>
  ${MOCK.patchesApplied.map(p => `
    <div class="patch-item" style="padding:10px;background:var(--bg-subtle);border-left:3px solid var(--patch-accepted);margin-bottom:6px">
      <div class="text-xs font-semibold">${p.rule_summary}</div>
      <div class="text-xs text-muted">Retrieved from ${p.source_runs} runs similares · relevance ${p.relevance}%</div>
    </div>`).join('')}
</div>
```

Requiere añadir a MOCK:
```javascript
MOCK.patchesApplied = [
  { rule_summary: 'Para Goliath L42+ siempre incluir caña de 20cm, no 18cm', source_runs: 8, relevance: 94 },
  { rule_summary: 'Distribuidora Seguridad MX: precio lista, no distribuidor (histórico)', source_runs: 3, relevance: 87 },
  { rule_summary: 'Cantidad >100 pares → ofrecer descuento 5% en cuerpo, no pie', source_runs: 12, relevance: 91 },
];
```

**Añadir botón "Ver trace completo en Langfuse"** en el footer del console:

```html
<div class="console-footer-obs" style="padding:12px;border-top:1px solid var(--border-subtle);
                                         display:flex;justify-content:space-between;align-items:center;font-size:12px">
  <span class="text-muted">
    Run ID: <code>${draft.run_id}</code> · Tenant: <code>${MOCK.user.org_slug}</code>
  </span>
  <a href="${draft.trace_url}" target="_blank" class="btn btn-ghost btn-sm">
    <svg class="ico-sm ico"><use href="#i-langfuse"/></svg>
    Ver trace en Langfuse
  </a>
</div>
```

**Remover:** nada.

**Justificación:** el aprobador no tiene forma hoy de saber si el draft viene de PROPONE vs EJECUTA_CON_APROBACIÓN, ni cuánto budget queda, ni qué patches se aplicaron. Todo esto está en SPEC_AGENT_COMPOSITION §§5-8 + SPEC_WORKFLOW_ENGINE §5.

---

### 2.5 `renderAgentes` (L3805-3964)

**Cambios estructurales** — el pipeline Shadow/Active/Archived queda, se le añaden ladder + sealed/open + fork.

**Modificar cada agent card:**

En el header de la card (donde va name + role + mode pill), añadir:

```html
<div class="agent-card-meta" style="display:flex;gap:8px;align-items:center;margin-top:6px">
  ${sealedOpenBadge(a.kind)}  <!-- sealed o open -->
  ${ladderPip(a.autonomy_level)}
  ${authorityBadge(a.primary_authority_mode)}
  ${a.kind === 'sealed' ? `
    <button class="btn btn-ghost btn-sm" onclick="event.stopPropagation();forkAgent('${a.id}')"
            style="margin-left:auto" title="Fork a Open mode (edición plena)">
      <svg class="ico-sm ico"><use href="#i-fork"/></svg>Fork
    </button>` : ''}
</div>
```

**Modificar Shadow progress bar (actual L3862-3876 aprox):** hacer que indique criterios de graduación L0→L1:

```html
<div class="shadow-progress" style="margin-top:10px">
  <div class="shadow-progress-header" style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:4px">
    <span>Criterios para graduar a L1</span>
    <span class="text-muted">${a.shadow.runs}/20 runs · ${a.shadow.approval_rate}% approval</span>
  </div>
  <div class="shadow-progress-bar" style="height:6px;background:var(--border-subtle);border-radius:3px;overflow:hidden">
    <div class="shadow-progress-fill" style="height:100%;
         background:linear-gradient(90deg, var(--ladder-l0), var(--ladder-l1));
         width:${Math.min(100, (a.shadow.runs/20)*100)}%"></div>
  </div>
  <div class="text-xs text-muted" style="margin-top:4px">
    Graduación: ≥20 runs + ≥90% approval + ≥95% confidence avg
  </div>
</div>
```

**Añadir filtro Sealed/Open en el header de la pantalla:**

```html
<div class="agentes-filters" style="display:flex;gap:8px;margin-bottom:16px">
  <button class="filter-chip ${filterKind==='all'?'active':''}" onclick="setAgentFilter('all')">Todos</button>
  <button class="filter-chip ${filterKind==='sealed'?'active':''}" onclick="setAgentFilter('sealed')">Sealed</button>
  <button class="filter-chip ${filterKind==='open'?'active':''}" onclick="setAgentFilter('open')">Open</button>
</div>
```

**Actualizar MOCK.agents:** cada agent gana:
```javascript
kind: 'sealed' | 'open',
base_sealed_hash: 'sha256:abc...' /* solo si open forkeado de sealed */,
autonomy_level: 0 | 1 | 2 | 3 | 4,
primary_authority_mode: 'propose',
position: 'QuoterPrimary' | 'CollectorShadow' | null,
can_fork: true /* solo sealed */,
```

**Remover:** nada estructural. La pipeline Shadow/Active/Archived se mantiene, solo se enriquece.

**Justificación:** sin Sealed/Open visible, Álvaro no puede distinguir qué agente es su versión custom vs template. Sin ladder explícito, graduación de Shadow→Active no tiene criterios visuales. Todo viene de SPEC_AGENT_COMPOSITION v1.1 §§5-8.

---

### 2.6 `renderSkillStudio` (L4690-~5090)

**Cambios vocabulario + tab Add-ons nueva.**

**Mantener:** las 3 capas (Base sealed / Manual overlay / Learned overlay) ya aplican perfectamente al modelo Sealed/Open. Solo se renombran.

**Modificar capa 1 header (L4883-4890):**

- **Antes:** "Base · instrucciones del template"
- **Después:** `<svg #i-lock/> <strong>Sealed base</strong> · template v${skill.templateVersion} · hash: ${skill.base_sealed_hash}`

Añadir botón "Fork a Open" al lado del Sealed base header (si el skill es sealed):

```html
${skill.kind === 'sealed' ? `
  <button class="btn btn-ghost btn-sm" onclick="forkSkill('${skill.id}')"
          title="Convertir a Open mode · permite editar instrucciones base">
    <svg class="ico-sm ico"><use href="#i-fork"/></svg>Fork a Open
  </button>` : `
  <span class="pill" style="background:var(--open-bg);color:var(--open-fg)">Open · forked ${skill.fork_date}</span>`}
```

**Añadir tab "Add-ons" al skill-tab-bar:** 5 sub-pestañas al nivel tenant (no al skill):

```html
<div class="skill-tab-bar-secondary" style="margin-top:8px;border-bottom:1px solid var(--border-subtle);
                                             display:flex;gap:16px;padding-bottom:8px">
  <div class="addon-tab ${addonTab==='golden'?'active':''}" onclick="setAddonTab('golden')">
    <svg class="ico-sm ico"><use href="#i-check"/></svg>Golden samples · ${skill.addons.golden_samples.length}
  </div>
  <div class="addon-tab ${addonTab==='kb'?'active':''}" onclick="setAddonTab('kb')">
    <svg class="ico-sm ico"><use href="#i-database"/></svg>Static KB · ${skill.addons.static_kb.length}
  </div>
  <div class="addon-tab ${addonTab==='corpus'?'active':''}" onclick="setAddonTab('corpus')">
    <svg class="ico-sm ico"><use href="#i-activity"/></svg>Living corpus · ${skill.addons.living_corpus.count}
  </div>
  <div class="addon-tab ${addonTab==='tools'?'active':''}" onclick="setAddonTab('tools')">
    <svg class="ico-sm ico"><use href="#i-plug"/></svg>Tool pack · ${skill.addons.tool_pack.length}
  </div>
  <div class="addon-tab ${addonTab==='memory'?'active':''}" onclick="setAddonTab('memory')">
    <svg class="ico-sm ico"><use href="#i-brain"/></svg>Memory profile
  </div>
</div>
```

**Añadir contenedor renderAddonTab(addonTab)** que cambia según tab seleccionado:
- `golden` — lista de 13-campo golden samples con botón "Nueva propuesta" (entra como candidate)
- `kb` — lista de docs adjuntos (PDF, URL, GDrive)
- `corpus` — contador de runs consolidados + política de sampling
- `tools` — MCP connectors / SP-API / HTTP clients habilitados para este skill
- `memory` — TTL + namespaces Letta + tamaño buffer

**Modificar MOCK.agentDetails[id].skills[n]:**

```javascript
kind: 'sealed' | 'open',
base_sealed_hash: 'sha256:...',
fork_date: '2026-04-15' /* solo si open */,
addons: {
  golden_samples: [...],  // array de 13-campo
  static_kb: [...],
  living_corpus: { count: 8421, last_consolidated: '2026-04-18' },
  tool_pack: ['spapi:get_inventory', 'gmail:send', 'hubspot:create_deal'],
  memory_profile: { ttl_days: 90, namespaces: ['episodic', 'semantic'], buffer_size: 10000 },
},
```

**Remover:** nada. Se respeta la arquitectura 3-capas que ya funciona.

**Justificación:** el Skill Studio ya tiene el concepto 3-capas, pero no distingue Sealed de Open ni expone Add-ons como entidad separable a nivel tenant (SPEC_SKILL_COMPOSITION §§4-6). Hoy los Add-ons están mezclados en "Contexto" del skill.

---

### 2.7 `renderWorkflows` (L3966-4170) — **REFACTOR MAYOR**

Esta es la pantalla que más cambia. Hoy es un drag-drop canvas con paleta de nodos. **Fase 1 canoniza YAML DSL + 5 templates wedge, NO canvas visual**. React Flow queda para Fase 2 (post-beta).

**Remover en Fase 1:**
- Canvas SVG con bezier connections
- Paleta de nodos drag-drop
- Inspector de nodos
- Toda la lógica de `WF_NODES` hardcoded

**Estructura nueva: 3-column layout**

```
┌─────────────────────────────────────────────────────────────┐
│  Header: "Workflows"  · tabs: Templates | Runs | YAML Editor │
├──────────────┬──────────────────────────────┬────────────────┤
│              │                              │                │
│  Templates   │  Template Detail / Runs      │  YAML Editor   │
│  list        │  Timeline / Stats            │  syntax        │
│  (5 wedge)   │                              │  highlight     │
│              │                              │                │
└──────────────┴──────────────────────────────┴────────────────┘
```

**Código esqueleto:**

```javascript
let workflowTab = 'templates';  // 'templates' | 'runs' | 'yaml'
let selectedTemplate = 't-cotizacion-b2b';

function renderWorkflows(params) {
  const app = document.getElementById('app-root');
  const tab = (params && params[0]) || workflowTab;
  workflowTab = tab;

  const header = `
    <div class="page-header">
      <div>
        <h1 class="page-title">Workflows</h1>
        <p class="page-subtitle">Templates pre-armados · YAML declarativo · motor pg-boss · Fase 1</p>
      </div>
      <div class="flex gap-2">
        <button class="btn btn-secondary" onclick="go('workflow-runs')">
          <svg class="ico-sm ico"><use href="#i-activity"/></svg>Ver runs
        </button>
        <button class="btn btn-primary" onclick="alert('Mock: clonar template como Open')">
          <svg class="ico-sm ico"><use href="#i-fork"/></svg>Nuevo desde template
        </button>
      </div>
    </div>

    <div class="wf-tabs" style="display:flex;gap:4px;border-bottom:1px solid var(--border-subtle);margin-bottom:16px">
      <div class="wf-tab ${tab==='templates'?'active':''}" onclick="go('workflows/templates')">Templates (5)</div>
      <div class="wf-tab ${tab==='runs'?'active':''}" onclick="go('workflows/runs')">Runs (${MOCK.workflowRuns.length})</div>
      <div class="wf-tab ${tab==='yaml'?'active':''}" onclick="go('workflows/yaml')">YAML Editor</div>
    </div>`;

  const body = tab === 'templates' ? renderWorkflowTemplates() :
               tab === 'runs'      ? renderWorkflowRuns() :
                                     renderWorkflowYaml();

  app.innerHTML = appShell('workflows', ['Workflows', tab], `
    <div class="page-wrap">${header}${body}</div>`);
  initTheme();
}

function renderWorkflowTemplates() {
  const tpl = MOCK.templates.find(t => t.id === selectedTemplate) || MOCK.templates[0];

  const listHTML = MOCK.templates.map(t => `
    <div class="tpl-card ${t.id === selectedTemplate ? 'active' : ''}"
         onclick="selectTemplate('${t.id}')">
      <div class="tpl-card-head">
        <div class="tpl-card-title">${t.name}</div>
        ${authorityBadge(t.authority_mode)}
      </div>
      <div class="tpl-card-meta">
        <span>${t.sector}</span>
        <span>·</span>
        ${ladderPip(parseInt(t.autonomy_level.slice(1)))}
      </div>
      <div class="tpl-card-stats">
        <span>${t.runs} runs</span>
        <span>${t.approval_rate}% aprob.</span>
        <span>$${t.cost_avg_usd.toFixed(2)} avg</span>
      </div>
    </div>`).join('');

  const detailHTML = `
    <div class="tpl-detail">
      <div class="tpl-detail-head">
        <h2>${tpl.name}</h2>
        <div class="flex gap-2">
          ${authorityBadge(tpl.authority_mode)}
          ${ladderPip(parseInt(tpl.autonomy_level.slice(1)))}
          ${sealedOpenBadge('sealed')}
        </div>
      </div>
      <p>${tpl.description}</p>

      <div class="tpl-kpi-row">
        <div class="kpi-mini"><div class="kpi-mini-label">Runs (30d)</div><div class="kpi-mini-value">${tpl.runs}</div></div>
        <div class="kpi-mini"><div class="kpi-mini-label">Approval rate</div><div class="kpi-mini-value">${tpl.approval_rate}%</div></div>
        <div class="kpi-mini"><div class="kpi-mini-label">Latency P95</div><div class="kpi-mini-value">${tpl.p95_latency_s}s</div></div>
        <div class="kpi-mini"><div class="kpi-mini-label">Cost avg</div><div class="kpi-mini-value">$${tpl.cost_avg_usd}</div></div>
      </div>

      <div class="tpl-steps-flow">
        <h3>Pasos del workflow</h3>
        <div class="flow-preview">
          ${renderTemplateStepsPreview(tpl.id)}
        </div>
      </div>

      <div class="tpl-constraints">
        <h3>Constraints anti-loop</h3>
        <ul>
          <li>max_depth: <strong>2</strong></li>
          <li>max_turns: <strong>20</strong></li>
          <li>max_budget_usd: <strong>$1.00</strong></li>
          <li>timeout_minutes: <strong>5</strong></li>
          <li>circuit_breaker: 3 fallos → fallback</li>
        </ul>
      </div>
    </div>`;

  const yamlPreview = `<pre class="yaml-preview"><code>${getTemplateYaml(tpl.id)}</code></pre>`;

  return `
    <div class="wf-layout-3col">
      <aside class="wf-templates-list">${listHTML}</aside>
      <section class="wf-template-detail">${detailHTML}</section>
      <aside class="wf-yaml-preview">
        <div class="wf-yaml-head">
          <span class="text-xs text-muted">YAML · ${tpl.id}.yaml</span>
          <button class="btn btn-ghost btn-sm" onclick="copyYaml('${tpl.id}')">Copy</button>
        </div>
        ${yamlPreview}
      </aside>
    </div>`;
}
```

**`renderWorkflowYaml`** — editor en pantalla completa para Open templates:

```javascript
function renderWorkflowYaml() {
  // Editor con syntax highlighting simple (mockup usa CSS classes)
  // Botones: Validate YAML · Dry-run · Save as Open template · Deploy to Canary
  return `
    <div class="yaml-editor-layout">
      <div class="yaml-editor-toolbar">
        <select onchange="loadYaml(this.value)">
          <option value="t-cotizacion-b2b">Cotización Rápida B2B</option>
          <option value="t-cobranza">Cobranza Inteligente</option>
          <option value="new">+ Nuevo (en blanco)</option>
        </select>
        <button class="btn btn-secondary btn-sm">Validate</button>
        <button class="btn btn-secondary btn-sm">Dry-run</button>
        <button class="btn btn-primary btn-sm">Deploy a canary</button>
      </div>
      <textarea class="yaml-editor-textarea" spellcheck="false">${getTemplateYaml(selectedTemplate)}</textarea>
      <div class="yaml-editor-footer">
        <span class="text-xs text-muted">DSL subset: CNCF Serverless Workflow · schema v1.0</span>
        <span class="text-xs" style="color:var(--success)">✓ YAML válido · 6 steps · depth=1</span>
      </div>
    </div>`;
}
```

**`renderWorkflowRuns`** — tabla simple de runs con drill-down a Langfuse:

```javascript
function renderWorkflowRuns() {
  const rowsHTML = MOCK.workflowRuns.map(r => {
    const tpl = MOCK.templates.find(t => t.id === r.template_id);
    const statusColor = r.status === 'succeeded' ? 'pill-success' :
                        r.status === 'awaiting_approval' ? 'pill-warning' :
                        r.status === 'circuit_broken' ? 'pill-error' : 'pill-neutral';
    return `
      <div class="wf-run-row">
        <div class="run-id"><code>${r.id}</code></div>
        <div class="run-tpl">${tpl?.name || r.template_id}</div>
        <div class="run-status"><span class="pill ${statusColor} pill-dot">${r.status}</span></div>
        <div class="run-duration">${r.duration_s}s</div>
        <div class="run-cost">$${r.cost_usd}</div>
        <div class="run-steps">${r.steps} steps · depth ${r.depth_used}</div>
        <div class="run-time text-xs text-muted">${r.started}</div>
        <div class="run-actions">
          <a href="${r.trace_url}" target="_blank" class="btn btn-ghost btn-sm">
            <svg class="ico-sm ico"><use href="#i-langfuse"/></svg>Trace
          </a>
        </div>
      </div>`;
  }).join('');

  return `
    <div class="wf-runs-filters" style="display:flex;gap:8px;margin-bottom:12px">
      <button class="filter-chip active">Todos (${MOCK.workflowRuns.length})</button>
      <button class="filter-chip">Succeeded</button>
      <button class="filter-chip">Awaiting approval</button>
      <button class="filter-chip">Failed / circuit broken</button>
      <button class="filter-chip">Últimas 24h</button>
    </div>
    <div class="wf-runs-table">${rowsHTML}</div>`;
}
```

**Helpers a añadir:**

```javascript
function getTemplateYaml(id) {
  // Devuelve YAML pre-formateado — en mockup es string hardcodeado por template
  const yamls = {
    't-cotizacion-b2b': `id: cotizacion_b2b_v1
name: Cotización Rápida B2B
trigger:
  type: email_received
  filter: subject_contains("RFQ") OR "cotización"
constraints:
  max_depth: 2
  max_turns: 20
  max_budget_usd: 1.00
  timeout_minutes: 5
steps:
  - name: validar_input
    type: deterministic
    action: validate_rfq_fields
  - name: consultar_stock
    type: tool_call
    tool: spapi.get_inventory
    with_circuit_breaker: { failure_threshold: 3, fallback: use_cached_stock }
  - name: qualify
    type: agent
    agent: QualifyBot
    authority: propose
  - name: aprobacion
    type: wait_for_approval
    approver: sales_manager
    sla_minutes: 60
  - name: enviar
    type: channel_send
    channel: gmail
    draft_first: true
  - name: registrar_crm
    type: db_insert
    target: hubspot.deals
events_emitted:
  - propuesta_enviada
  - cotizacion_rechazada
`,
    // ... similares para los otros 4 templates
  };
  return yamls[id] || '# Template no encontrado';
}

function renderTemplateStepsPreview(id) {
  // ASCII art simplificado de flow, NO canvas
  const tpl = MOCK.templates.find(t => t.id === id);
  return `
    <div class="step-chain">
      ${['Trigger', 'Validate', 'Consult', 'Qualify', 'Approve', 'Send', 'Log'].map((s, i) => `
        <div class="step-chip">${s}</div>
        ${i < 6 ? '<span class="step-arrow">→</span>' : ''}
      `).join('')}
    </div>`;
}
```

**Remover:**
- `WF_NODES` array (L3969-3997 aprox) — hardcodeado para una sola cotización
- `renderNodeInspector` y su lógica asociada
- SVG canvas con beziers (L~4100-4170)
- Palette drag-drop

**Justificación:** el canvas visual es Fase 2 post-beta (React Flow). Fase 1 = YAML + templates listos. Hoy el mockup muestra algo que NO se va a construir en los primeros 8 semanas — genera expectativa errónea en design partners.

---

### 2.8 `renderConexiones` (L4184-~4290)

**Cambios mínimos.** La pantalla de integraciones ya cubre Gmail/HubSpot/Drive/Amazon/WhatsApp/QuickBooks.

**Añadir:** fila de status para **Langfuse** (observability no es connector comercial, pero el usuario necesita saber que trace está activo):

```html
<div class="conn-row">
  <div class="conn-icon" style="background:#6B21A8">L</div>
  <div>
    <div class="conn-name">Langfuse Cloud Core</div>
    <div class="conn-meta">Observability · traces runtime · $29/mes</div>
  </div>
  <span class="pill pill-success pill-dot">Conectado · 100% cobertura</span>
  <button class="btn btn-ghost btn-sm" onclick="window.open('https://cloud.langfuse.com')">Abrir</button>
</div>

<div class="conn-row">
  <div class="conn-icon" style="background:#F59E0B">A</div>
  <div>
    <div class="conn-name">Arize Phoenix</div>
    <div class="conn-meta">Drift detection · $6/mes VPS</div>
  </div>
  <span class="pill pill-success pill-dot">Conectado</span>
  <button class="btn btn-ghost btn-sm">Ver dashboard</button>
</div>
```

**Remover:** nada.

---

### 2.9 `renderSettings` (L4296-~4688)

**Mantener estructura.** Esta pantalla cubre perfil de usuario / preferencias.

**Añadir sección** "Preferencias de aprobación":

```html
<div class="settings-section">
  <h3>Preferencias de aprobación</h3>
  <div class="form-row">
    <div class="form-label">Auto-aprobar drafts con confianza ≥ X%</div>
    <div class="form-input">
      <input type="number" value="90" min="80" max="99"> %
      <div class="form-hint">Solo aplica a workflows en modo EJEC·aprobación · nunca a externos sin approval explícito</div>
    </div>
  </div>
  <div class="form-row">
    <div class="form-label">Notificaciones por canal</div>
    <div class="form-input">
      <label><input type="checkbox" checked> Email — drafts urgentes (SLA <15min)</label>
      <label><input type="checkbox" checked> Slack/Teams — todos los drafts</label>
      <label><input type="checkbox"> SMS — solo rechazos y circuit breakers</label>
    </div>
  </div>
  <div class="form-row">
    <div class="form-label">Horario de aprobación</div>
    <div class="form-input">
      <input type="time" value="08:00"> a <input type="time" value="20:00">
      <div class="form-hint">Fuera de horario: drafts esperan · nunca se aprueba por ti</div>
    </div>
  </div>
</div>
```

**Remover:** nada.

---

### 2.10 `renderAdmin` (L5262-~5690) — **AÑADIR 3 SECCIONES NUEVAS**

Estructura actual: nav lateral con secciones `Plataforma`, `Seguridad`, `Gobernanza`. Mantener.

**Añadir al nav `Plataforma`:**

```javascript
// En ADMIN_TABS array
{ id: 'runtime', label: 'Runtime control', icon: 'i-kill', section: 'Plataforma' },
{ id: 'budgets', label: 'Budgets & caps', icon: 'i-layers', section: 'Plataforma' },
{ id: 'observability', label: 'Observability', icon: 'i-langfuse', section: 'Plataforma' },
```

**Nueva sección `adminRuntime()` — Kill switch + Circuit breakers:**

```javascript
function adminRuntime() {
  const ksArmed = MOCK.tenantBudget.kill_switch_armed;
  const cbRows = MOCK.circuitBreakers.map(c => `
    <div class="form-row" style="grid-template-columns:1fr 120px 130px 100px 120px;align-items:center">
      <div><code style="font-family:'JetBrains Mono',monospace;font-size:12px">${c.workflow_id}</code></div>
      <div><span class="pill ${c.state==='closed'?'pill-success':c.state==='open'?'pill-error':'pill-warning'} pill-dot">${c.state}</span></div>
      <div class="text-xs text-muted">${c.failure_count} fallos</div>
      <div class="text-xs text-muted">${c.last_failure || '—'}</div>
      <div style="text-align:right">
        ${c.state !== 'closed' ? `<button class="btn btn-ghost btn-sm" onclick="alert('Mock: reset ${c.workflow_id}')">Reset</button>` : ''}
      </div>
    </div>`).join('');

  return `
    <div class="admin-section ${ksArmed ? 'danger-zone' : ''}">
      <h3 style="font-size:16px;font-weight:600;margin-bottom:4px">Kill switch global</h3>
      <p class="text-xs text-muted" style="margin-bottom:16px">
        Detiene inmediatamente todos los workflows en ejecución · los drafts pending quedan intactos ·
        propagación <60s · auto-armed si cost z-score > 4
      </p>
      <div style="display:flex;gap:16px;align-items:center;padding:16px;background:${ksArmed?'rgba(196,74,62,.1)':'var(--bg-subtle)'};border-radius:8px">
        <svg class="ico" style="width:32px;height:32px;color:var(${ksArmed?'--error':'--text-muted'})"><use href="#i-kill"/></svg>
        <div style="flex:1">
          <div style="font-weight:600">Estado: ${ksArmed ? 'ARMADO ⚠️' : 'Inactivo'}</div>
          <div class="text-xs text-muted">
            ${ksArmed ? 'Desarmado por Owner · todos los runs detenidos' : 'Sistema operando normal'}
          </div>
        </div>
        <button class="btn ${ksArmed?'btn-secondary':'btn-danger'} btn-sm" onclick="toggleKillSwitch()">
          ${ksArmed ? 'Desarmar kill switch' : 'ARMAR kill switch'}
        </button>
      </div>
    </div>

    <div class="admin-section">
      <h3 style="font-size:16px;font-weight:600;margin-bottom:4px">Circuit breakers</h3>
      <p class="text-xs text-muted" style="margin-bottom:16px">
        Estado de circuit breakers por workflow · open = fallback activo · reset manual disponible
      </p>
      ${cbRows}
    </div>

    <div class="admin-section">
      <h3 style="font-size:16px;font-weight:600;margin-bottom:4px">Canary deployment</h3>
      <p class="text-xs text-muted" style="margin-bottom:16px">
        Tenant designado para recibir cambios de workflow antes que el resto · permite detectar deploy roto sin afectar producción
      </p>
      <div class="form-row">
        <div class="form-label">Canary tenant</div>
        <div class="form-input">
          <select>
            <option>muitowork (prod)</option>
            <option selected>marluvas-pilot (canary actual)</option>
            <option>tecmater-pilot</option>
          </select>
          <div class="form-hint">Cambios a workflows/skills se deployan primero aquí · si falla, se revierten automáticamente antes de prod</div>
        </div>
      </div>
    </div>`;
}
```

**Nueva sección `adminBudgets()`:**

```javascript
function adminBudgets() {
  const b = MOCK.tenantBudget;
  return `
    <div class="admin-section">
      <h3 style="font-size:16px;font-weight:600;margin-bottom:4px">Budget LLM por tenant</h3>
      <p class="text-xs text-muted" style="margin-bottom:16px">
        Límites diarios por tenant · detiene runs cuando se alcanza · previene runaway agent costoso
      </p>
      <div class="form-row">
        <div class="form-label">Tier Pilot (pago · design partner)</div>
        <div class="form-input"><input type="number" value="${b.daily_llm_cap_usd}" min="1"> USD/día</div>
      </div>
      <div class="form-row">
        <div class="form-label">Tier Free (evaluación · gratis)</div>
        <div class="form-input"><input type="number" value="${b.free_tier_cap_usd}" min="1"> USD/día</div>
      </div>
      <div class="form-row">
        <div class="form-label">Tier Operación (GA)</div>
        <div class="form-input"><input type="number" value="50" min="10"> USD/día</div>
      </div>
      <div class="form-row">
        <div class="form-label">Alerta al llegar a</div>
        <div class="form-input"><input type="number" value="80" min="50" max="95"> % del budget</div>
      </div>
    </div>

    <div class="admin-section">
      <h3 style="font-size:16px;font-weight:600;margin-bottom:4px">Anti-loop defaults (por agente)</h3>
      <p class="text-xs text-muted" style="margin-bottom:16px">Valores obligatorios día 1 · editable por workflow individual</p>
      <div class="form-row"><div class="form-label">max_depth (composición)</div><div class="form-input"><input value="2" style="max-width:120px"></div></div>
      <div class="form-row"><div class="form-label">max_turns (agente)</div><div class="form-input"><input value="20" style="max-width:120px"></div></div>
      <div class="form-row"><div class="form-label">max_budget_usd por run</div><div class="form-input"><input value="1.00" style="max-width:120px"></div></div>
      <div class="form-row"><div class="form-label">timeout_minutes por step</div><div class="form-input"><input value="5" style="max-width:120px"></div></div>
      <div class="form-row"><div class="form-label">circuit breaker fallos</div><div class="form-input"><input value="3" style="max-width:120px"> consecutivos</div></div>
      <div class="form-row"><div class="form-label">idempotency TTL</div><div class="form-input"><input value="7" style="max-width:120px"> días</div></div>
    </div>`;
}
```

**Nueva sección `adminObservability()`:**

```javascript
function adminObservability() {
  return `
    <div class="admin-section">
      <h3 style="font-size:16px;font-weight:600;margin-bottom:4px">Langfuse Cloud Core</h3>
      <p class="text-xs text-muted" style="margin-bottom:16px">
        Observability oficial · cobertura 100% traces · $29/mes · retención 30 días
      </p>
      <div class="form-row">
        <div class="form-label">Status</div>
        <div class="form-input">
          <span class="pill pill-success pill-dot">Conectado</span>
          <span class="text-xs text-muted" style="margin-left:8px">Último trace: hace 14s</span>
        </div>
      </div>
      <div class="form-row">
        <div class="form-label">Dashboard URL</div>
        <div class="form-input">
          <code>https://cloud.langfuse.com/project/fl-prod</code>
          <button class="btn btn-ghost btn-sm">Abrir</button>
        </div>
      </div>
      <div class="form-row">
        <div class="form-label">Tags por tenant</div>
        <div class="form-input">
          <label><input type="checkbox" checked> tenant_id</label>
          <label><input type="checkbox" checked> agent_id</label>
          <label><input type="checkbox" checked> workflow_id</label>
          <label><input type="checkbox" checked> run_id</label>
          <label><input type="checkbox" checked> step_id</label>
        </div>
      </div>
    </div>

    <div class="admin-section">
      <h3 style="font-size:16px;font-weight:600;margin-bottom:4px">Arize Phoenix (drift)</h3>
      <p class="text-xs text-muted" style="margin-bottom:16px">
        Detección de drift en embeddings y prompts · self-hosted en Hetzner · $6/mes
      </p>
      <div class="form-row">
        <div class="form-label">Status</div>
        <div class="form-input">
          <span class="pill pill-success pill-dot">Healthy</span>
          <span class="text-xs text-muted" style="margin-left:8px">Drift alert: ninguno last 24h</span>
        </div>
      </div>
      <div class="form-row">
        <div class="form-label">Umbral drift alert</div>
        <div class="form-input"><input value="0.15" step="0.01" type="number" style="max-width:120px"></div>
      </div>
    </div>

    <div class="admin-section">
      <h3 style="font-size:16px;font-weight:600;margin-bottom:4px">3 métricas críticas (Go/No-Go)</h3>
      <p class="text-xs text-muted" style="margin-bottom:16px">Alineadas con checklist §13 SPEC_WORKFLOW_ENGINE</p>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px">
        <div class="metric-critical">
          <div class="text-xs text-muted">Approval rate (7d)</div>
          <div class="metric-value" style="font-size:28px;font-weight:600;color:var(--success)">87%</div>
          <div class="text-xs">Target: ≥80% · OK</div>
        </div>
        <div class="metric-critical">
          <div class="text-xs text-muted">Cost per run (7d avg)</div>
          <div class="metric-value" style="font-size:28px;font-weight:600;color:var(--success)">$0.34</div>
          <div class="text-xs">Target: <$0.50 · OK</div>
        </div>
        <div class="metric-critical">
          <div class="text-xs text-muted">Latency P95 (7d)</div>
          <div class="metric-value" style="font-size:28px;font-weight:600;color:var(--success)">187s</div>
          <div class="text-xs">Target: <300s · OK</div>
        </div>
      </div>
    </div>`;
}
```

**Actualizar `adminSection(tab)`** dispatcher (L5307-5319):
```javascript
if (tab === 'runtime')        return adminRuntime();
if (tab === 'budgets')        return adminBudgets();
if (tab === 'observability')  return adminObservability();
```

**Remover:** nada. Las secciones existentes (overview, keys, webhooks, oauth, secrets, rates, ip, audit, data, danger) se mantienen.

**Justificación:** el Admin Console es el tablero donde Álvaro detecta runaway y actúa. Sin kill switch, circuit breakers visibles, budget caps editables y 3 métricas críticas, no hay forma de operar F1 con control. Todo esto es MUST HAVE de §13 del SPEC_WORKFLOW_ENGINE.

---

### 2.11 `renderDeliverable` (L5093-~5260)

**Cambios mínimos.** Pantalla ya funciona como preview de entregable async.

**Añadir al header** el Authority Mode + link a trace:

```html
<div class="deliverable-auth-strip" style="padding:10px 16px;background:var(--bg-subtle);border-radius:6px;margin-bottom:12px">
  ${authorityBadge(d.authority_mode || 'propose')}
  <span class="ladder-inline">${ladderPip(d.autonomy_level || 2)}</span>
  <a href="${d.trace_url}" class="btn btn-ghost btn-sm" style="margin-left:auto">
    <svg class="ico-sm ico"><use href="#i-langfuse"/></svg>Trace
  </a>
</div>
```

**Remover:** nada.

---

## 3 · Pantallas nuevas a crear

### 3.1 `renderWorkflowRuns(params)` (ruta `workflow-runs`)

Ya mencionada en §2.7. Vista full-page con filtros + tabla con drill-down Langfuse.

Rutas: `go('workflow-runs')`, `go('workflow-runs/run-001')` (detalle individual con timeline de steps).

**Campos por run en vista detalle:**
- Timeline vertical con cada step del workflow, duración, status (succeeded/failed/waiting)
- Agent invocado, tokens consumidos, cost
- Links a drafts resultantes en Bandeja
- Botón "Replay" (dry-run con mismo input)
- Link "Ver full trace en Langfuse"

### 3.2 `renderGoldSamples(agentId, skillId)` (ruta `skills/:id/gold-samples`)

Pipeline visual **Candidate → Active → Archived** para golden samples PatchRAG.

3 columnas Kanban-style:

```
┌────────────┬────────────┬────────────┐
│ Candidate  │  Active    │  Archived  │
│ (3)        │  (12)      │  (5)       │
├────────────┼────────────┼────────────┤
│ gs-019     │  gs-001    │  gs-003    │
│ [preview]  │  [preview] │  [preview] │
│ Accept ▸   │  Retire ◂  │  Revive ▸  │
└────────────┴────────────┴────────────┘
```

**Cada golden sample card tiene los 13 campos canonizados:**
1. ID (sha256 hash de input+output)
2. Skill binding
3. Input summary
4. Input full (collapsible)
5. Expected output summary
6. Expected output full (collapsible)
7. Runs matched (cuántas veces se retrieved)
8. Confidence current
9. Stage (candidate/active/archived)
10. Created by (user o auto-proposed)
11. Last updated
12. PatchRAG relevance score
13. Archived reason (si aplica)

Botones por card: `Accept · Edit · Retire · Revive · View runs`.

### 3.3 Posibles futuros (F2, no F1)

Mencionar sólo como comentario en el código (`// TODO F2`):
- Workflow Canvas visual (React Flow)
- Multi-tenant switcher en header
- A/B test de prompts
- Replay con diff vs run anterior

---

## 4 · Criterios de aceptación

Claude Code debe cumplir todo lo siguiente antes de entregar v3:

1. **`node --check faberloom_v3.html` sin errores** (memoria feedback_faberloom_prototype)
2. Ninguna referencia a `WF_NODES`, `paletteCategories`, `renderNodeInspector`, `canvas bezier` queda en el archivo (limpieza total renderWorkflows)
3. Las 14 funciones render existentes siguen respondiendo a sus rutas (no rompe navegación)
4. 3 funciones nuevas añadidas: `renderWorkflowRuns`, `renderGoldSamples`, `renderAddonTab`
5. 3 sub-pestañas nuevas en Workflows (templates/runs/yaml) con switch funcional
6. 3 sub-pestañas nuevas en Admin (runtime/budgets/observability) con switch funcional
7. 6 helpers nuevos añadidos: `authorityBadge`, `ladderPip`, `sealedOpenBadge`, `learningThermometer`, `depthBudget`, `getTemplateYaml`
8. MOCK ampliado con: `templates`, `workflowRuns`, `goldSamples`, `tenantBudget`, `circuitBreakers`, `patchesApplied`
9. MOCK.agents actualizado con: `kind`, `base_sealed_hash`, `autonomy_level`, `primary_authority_mode`, `position`
10. MOCK.drafts actualizado con: `authority_mode`, `autonomy_level`, `depth_remaining`, `budget_used_usd`, `sla_remaining_min`, `idempotency_key`, `run_id`, `trace_url`
11. CSS tokens nuevos añadidos en `:root` y dark (authority/ladder/learning/sealed/open)
12. 9 íconos nuevos en sprite SVG: `i-layers`, `i-yaml`, `i-template`, `i-fork`, `i-kill`, `i-circuit`, `i-langfuse`, `i-canary`, `i-patch`
13. Landing page no pierde el pitch — solo ajustes de texto menores
14. Ningún texto en inglés en UI (español directo, según user preferences)

---

## 5 · Orden de implementación sugerido (5 sprints de mockup · ~5 días)

| Día | Scope | Archivos |
|---|---|---|
| **1** | §1 globales: tokens CSS, helpers (authorityBadge, ladderPip, sealedOpenBadge), íconos SVG, MOCK data nuevo | bloque `<style>` + sprite + sección MOCK |
| **2** | §2.7 Workflows refactor completo (remover canvas, añadir 3-tabs templates/runs/yaml) | `renderWorkflows` + 3 helpers internos |
| **3** | §2.5 Agentes (sealed/open badges + ladder + fork) + §2.6 Skill Studio (tab Add-ons) | `renderAgentes` + `renderSkillStudio` |
| **4** | §2.2 Dashboard KPIs F1 + §2.3 Bandeja Authority + §2.4 Console strip + §2.11 Deliverable | 4 render functions |
| **5** | §2.10 Admin (runtime/budgets/observability) + §3.1 Workflow Runs + §3.2 Gold Samples | `renderAdmin` + 2 nuevas |

Cada día cierra con `node --check` verde + snapshot visual (Álvaro revisa).

---

## 6 · Checklist Go/No-Go UX (antes de entregar v3 a design partners)

- [ ] Dashboard muestra cost-per-run y budget cap visible sin clicks
- [ ] Bandeja muestra Authority Mode + SLA countdown en cada draft
- [ ] Console muestra Authority + Ladder + Depth/Budget + PatchRAG patches sin abrir drawer
- [ ] Agentes tiene badge Sealed/Open y botón Fork visible en sealed cards
- [ ] Skill Studio tiene tab Add-ons con 5 sub-secciones
- [ ] Workflows expone los 5 templates wedge sin canvas drag-drop
- [ ] YAML editor tiene Validate/Dry-run/Deploy canary buttons
- [ ] Workflow Runs tabla con link Trace a Langfuse
- [ ] Admin Runtime tiene kill switch ARMAR/desarmar + circuit breakers tabla
- [ ] Admin Budgets permite editar cap por tier (pilot/free/operación)
- [ ] Admin Observability muestra Langfuse status + 3 métricas críticas con target
- [ ] Ninguna pantalla requiere scroll horizontal en 1440px
- [ ] Modo oscuro respeta tokens nuevos (authority/ladder colors)
- [ ] Modal ⌘K task launcher sigue funcionando sin regresiones
- [ ] Navegación con `go()` sin errores en consola
- [ ] Ningún `alert()` en flujos críticos — usar pills/toasts

---

## 7 · Referencias

- `docs/SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md` §§3-5, 11-13
- `docs/SPEC_FABERLOOM_AGENT_COMPOSITION_v1.md` v1.1 §§5-8, 18
- `docs/SPEC_FABERLOOM_SKILL_COMPOSITION_v1.md` §§4-6
- `docs/SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` §§RLS, UUIDv7, observability
- `docs/archivo/kimi_swarm_3_workflows_autonomous.md` (síntesis 478 líneas)
- `docs/COWORK_DELIVERY_FABERLOOM_v3.5.md` (mockup FREEZE referente)
- Memoria `project_faberloom_workflow_engine.md` (resumen Fase 1)

---

## 8 · Registro de cambios

| Fecha | Versión | Autor | Nota |
|---|---|---|---|
| 2026-04-21 | 1.0 DRAFT | claude_cowork + alvaro | Creación post-canonización F1 (SPECs 3 gemelos) |
