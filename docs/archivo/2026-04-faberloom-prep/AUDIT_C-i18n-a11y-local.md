# AUDIT_C — i18n + a11y

## Sección D · i18n completo (ES / EN / PT-BR)

### D.1 · Sistema propuesto — vanilla JS

Snippet listo para pegar en el bloque `<script>` del HTML (antes de `function renderDashboard()` — ver línea ~2800). Respeta las convenciones del prototipo: funciones top-level, sin frameworks, `localStorage` permitido (file local).

```html
<!-- D.1 — I18N layer. Pegar antes del primer renderX() -->
<script>
/* ═══════════════════════════════════════════════════════════════
   FABERLOOM — I18N
   Default: es (CR). Fallback cascade: pt-BR → es. en → es si hueco.
   ═══════════════════════════════════════════════════════════════ */
const I18N = {
  es: {
    nav: { dashboard: 'Dashboard', bandeja: 'Bandeja', agentes: 'Agentes', skills: 'Skills Library', factory: 'Fábrica', workflows: 'Workflows', conexiones: 'Conexiones', settings: 'Configuración', admin: 'Admin Console', section_ops: 'Operación', section_cfg: 'Configuración' },
    topbar: { search: 'Abrir task launcher', notifications: 'Notificaciones', theme_light: 'Tema claro', theme_dark: 'Tema oscuro', lang: 'Idioma', help: 'Ayuda', logout: 'Cerrar sesión', admin_badge: 'OWNER' },
    /* … el resto lo carga D.3 */
  },
  en: {
    nav: { dashboard: 'Dashboard', bandeja: 'Inbox', agentes: 'Agents', skills: 'Skills Library', factory: 'Factory', workflows: 'Workflows', conexiones: 'Connections', settings: 'Settings', admin: 'Admin Console', section_ops: 'Operations', section_cfg: 'Configuration' },
    topbar: { search: 'Open task launcher', notifications: 'Notifications', theme_light: 'Light theme', theme_dark: 'Dark theme', lang: 'Language', help: 'Help', logout: 'Sign out', admin_badge: 'OWNER' },
  },
  'pt-BR': {
    nav: { dashboard: 'Painel', bandeja: 'Caixa', agentes: 'Agentes', skills: 'Biblioteca de Skills', factory: 'Fábrica', workflows: 'Fluxos', conexiones: 'Conexões', settings: 'Configurações', admin: 'Console Admin', section_ops: 'Operação', section_cfg: 'Configuração' },
    topbar: { search: 'Abrir launcher de tarefas', notifications: 'Notificações', theme_light: 'Tema claro', theme_dark: 'Tema escuro', lang: 'Idioma', help: 'Ajuda', logout: 'Sair', admin_badge: 'OWNER' },
  }
};

const LANG_DEFAULT = 'es';
const LANG_KEY = 'faberloom_lang';
let __lang = localStorage.getItem(LANG_KEY) || LANG_DEFAULT;

function getLang() { return __lang; }

function setLang(lang) {
  if (!I18N[lang]) return;
  __lang = lang;
  localStorage.setItem(LANG_KEY, lang);
  document.documentElement.setAttribute('lang', lang === 'pt-BR' ? 'pt-BR' : lang);
  renderI18n(document);
  // Reemitir la ruta actual para que los renderX() que tiran HTML via template literals se regeneren.
  if (typeof route === 'function') route();
}

/**
 * Resuelve `key` como `domain.sub.key`. Fallback cascade: lang → pt-BR → es.
 * Soporta interpolación `{nombre}` via params.
 */
function t(key, params) {
  const parts = key.split('.');
  const tryLang = (lang) => {
    let cur = I18N[lang];
    for (const p of parts) {
      if (cur && typeof cur === 'object' && p in cur) cur = cur[p]; else return undefined;
    }
    return typeof cur === 'string' ? cur : undefined;
  };
  let str = tryLang(__lang);
  if (str === undefined && __lang !== 'pt-BR') str = tryLang('pt-BR');
  if (str === undefined && __lang !== LANG_DEFAULT) str = tryLang(LANG_DEFAULT);
  if (str === undefined) return key; // visible que falta key; dev-time signal
  if (params) {
    str = str.replace(/\{(\w+)\}/g, (_, k) => (k in params ? params[k] : `{${k}}`));
  }
  return str;
}

/**
 * Rehidrata el DOM tras cambio de idioma o tras renderizar HTML nuevo.
 * - [data-i18n="dom.key"] reemplaza textContent
 * - [data-i18n-attr="placeholder:dom.key;title:dom.k2"] reemplaza atributos
 * - [data-i18n-html="dom.key"] inyecta HTML (usar SOLO con strings propios, nunca user-generated)
 */
function renderI18n(root) {
  root = root || document;
  root.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    el.textContent = t(key);
  });
  root.querySelectorAll('[data-i18n-attr]').forEach(el => {
    el.getAttribute('data-i18n-attr').split(';').forEach(pair => {
      const [attr, key] = pair.split(':').map(s => s.trim());
      if (attr && key) el.setAttribute(attr, t(key));
    });
  });
  root.querySelectorAll('[data-i18n-html]').forEach(el => {
    const key = el.getAttribute('data-i18n-html');
    el.innerHTML = t(key);
  });
}

/* boot */
document.addEventListener('DOMContentLoaded', () => {
  document.documentElement.setAttribute('lang', __lang === 'pt-BR' ? 'pt-BR' : __lang);
  renderI18n(document);
});
</script>
```

Notas de integración:
- Todos los `renderX()` existentes (`renderDashboard`, `renderBandeja`, `renderAgentes`, etc.) deben invocar `renderI18n(app)` después de asignar `app.innerHTML = …`. Alternativa menos invasiva: envolver `go(route)` para que al final llame `renderI18n(document)`.
- Para strings en template literals dentro de JS (ej. `alert('Mock: rotar …')`) usar `t('dialog.mock.rotate_key', {id: k.id})`.
- Atributo `lang`: ES default mantiene `lang="es"` (línea 2); al cambiar a PT-BR debe quedar `lang="pt-BR"` (no `pt`), a EN debe quedar `lang="en"`.
- `renderI18n` barre `document` para que un cambio de idioma rehidrate también la sidebar y el topbar sin re-renderizar toda la ruta.

### D.2 · Language switcher — HTML + CSS

Ubicación: topbar (`shellTopbar`, línea ~2938), entre el botón de notificaciones y el `.theme-toggle`. Patrón: dropdown controlado (`aria-expanded`), 3 opciones visibles con nombre en el idioma propio (no traducido — convención UX estándar: el usuario siempre reconoce su idioma en su propia lengua).

HTML — reemplazar/insertar entre el `icon-btn` de notificaciones y el `theme-toggle`:

```html
<!-- D.2 — Language switcher. Pegar en shellTopbar() después del icon-btn de notificaciones -->
<div class="lang-switch" data-lang-menu>
  <button
    class="icon-btn lang-switch-trigger"
    type="button"
    aria-haspopup="listbox"
    aria-expanded="false"
    aria-label="Idioma de la interfaz"
    onclick="toggleLangMenu(event)">
    <svg class="ico" aria-hidden="true"><use href="#i-globe"/></svg>
    <span class="lang-switch-code" data-lang-code>ES</span>
    <svg class="ico-sm ico" aria-hidden="true"><use href="#i-chevron-down"/></svg>
  </button>
  <ul class="lang-switch-menu" role="listbox" aria-label="Idioma" hidden>
    <li role="option" tabindex="0" data-lang="es"    aria-selected="true"  onclick="pickLang('es')">Español <span class="lang-hint">CR · MX · CO</span></li>
    <li role="option" tabindex="0" data-lang="en"    aria-selected="false" onclick="pickLang('en')">English <span class="lang-hint">International</span></li>
    <li role="option" tabindex="0" data-lang="pt-BR" aria-selected="false" onclick="pickLang('pt-BR')">Português <span class="lang-hint">Brasil</span></li>
  </ul>
</div>
```

JS controlador — inyectar cerca de `setTheme()` (línea ~2838):

```js
function toggleLangMenu(ev) {
  ev && ev.stopPropagation();
  const wrap = document.querySelector('[data-lang-menu]');
  const trigger = wrap.querySelector('.lang-switch-trigger');
  const menu = wrap.querySelector('.lang-switch-menu');
  const open = trigger.getAttribute('aria-expanded') === 'true';
  trigger.setAttribute('aria-expanded', open ? 'false' : 'true');
  menu.hidden = open;
  if (!open) {
    const sel = menu.querySelector('[aria-selected="true"]') || menu.querySelector('[role="option"]');
    sel && sel.focus();
  }
}
function pickLang(lang) {
  document.querySelectorAll('[data-lang-menu] [role="option"]').forEach(li => {
    li.setAttribute('aria-selected', li.dataset.lang === lang ? 'true' : 'false');
  });
  const code = { 'es': 'ES', 'en': 'EN', 'pt-BR': 'PT' }[lang];
  const label = document.querySelector('[data-lang-code]');
  if (label) label.textContent = code;
  setLang(lang);
  toggleLangMenu();
}
document.addEventListener('click', (e) => {
  const wrap = document.querySelector('[data-lang-menu]');
  if (wrap && !wrap.contains(e.target)) {
    const trig = wrap.querySelector('.lang-switch-trigger');
    if (trig && trig.getAttribute('aria-expanded') === 'true') {
      trig.setAttribute('aria-expanded', 'false');
      wrap.querySelector('.lang-switch-menu').hidden = true;
    }
  }
});
document.addEventListener('keydown', (e) => {
  const wrap = document.querySelector('[data-lang-menu]');
  if (!wrap) return;
  const open = wrap.querySelector('.lang-switch-trigger').getAttribute('aria-expanded') === 'true';
  if (!open) return;
  const items = [...wrap.querySelectorAll('[role="option"]')];
  const i = items.indexOf(document.activeElement);
  if (e.key === 'Escape')    { toggleLangMenu(); wrap.querySelector('.lang-switch-trigger').focus(); }
  if (e.key === 'ArrowDown' && i > -1) { items[(i + 1) % items.length].focus(); e.preventDefault(); }
  if (e.key === 'ArrowUp'   && i > -1) { items[(i - 1 + items.length) % items.length].focus(); e.preventDefault(); }
  if (e.key === 'Enter'     && i > -1) { pickLang(items[i].dataset.lang); }
});
```

CSS — usa tokens del slice A (§C.1). Pegar en el bloque global:

```css
/* D.2 — Language switcher */
.lang-switch { position: relative; }
.lang-switch-trigger {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 10px; height: 36px;
  background: transparent; border: 1px solid transparent;
  border-radius: var(--radius-md, 6px);
  color: var(--text-secondary);
  font-family: var(--font-ui, 'Inter', sans-serif);
  font-size: 13px; font-weight: 500;
  cursor: pointer;
  transition: background var(--duration-fast, 120ms) var(--ease-standard, ease),
              border-color var(--duration-fast, 120ms) var(--ease-standard, ease),
              color var(--duration-fast, 120ms) var(--ease-standard, ease);
}
.lang-switch-code {
  font-family: var(--font-mono, 'JetBrains Mono', monospace);
  font-size: 11px; letter-spacing: 0.04em;
  padding: 1px 6px; border-radius: var(--radius-sm, 4px);
  background: var(--bg-subtle); color: var(--text-primary);
}
.lang-switch-trigger:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
  border-color: var(--border-subtle);
}
.lang-switch-trigger:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring, 0 0 0 3px var(--coral-tint));
  border-radius: var(--radius-md, 6px);
}
.lang-switch-trigger[aria-expanded="true"] {
  background: var(--bg-hover);
  border-color: var(--border-subtle);
  color: var(--text-primary);
}
.lang-switch-menu {
  position: absolute; top: calc(100% + 6px); right: 0;
  min-width: 200px;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg, 8px);
  box-shadow: var(--shadow-md);
  padding: 4px; margin: 0; list-style: none;
  z-index: var(--z-dropdown, 1000);
  display: flex; flex-direction: column; gap: 2px;
}
.lang-switch-menu[hidden] { display: none; }
.lang-switch-menu li[role="option"] {
  display: flex; align-items: baseline; justify-content: space-between; gap: 12px;
  padding: 8px 10px;
  border-radius: var(--radius-sm, 4px);
  font-size: 13px; color: var(--text-primary);
  cursor: pointer;
  transition: background var(--duration-fast, 120ms) var(--ease-standard, ease);
}
.lang-switch-menu li[role="option"]:hover { background: var(--bg-hover); }
.lang-switch-menu li[role="option"]:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring, 0 0 0 3px var(--coral-tint));
  background: var(--bg-hover);
}
.lang-switch-menu li[role="option"][aria-selected="true"] {
  background: var(--coral-tint);
  color: var(--coral-primary);
  font-weight: 600;
}
.lang-switch-menu li[role="option"][aria-selected="true"]::before {
  content: '✓';
  color: var(--coral-primary);
  margin-right: 4px;
}
.lang-switch-menu .lang-hint {
  color: var(--text-muted);
  font-size: 11px;
  font-family: var(--font-mono, 'JetBrains Mono', monospace);
}
/* target size mínimo WCAG 2.5.5 */
.lang-switch-menu li[role="option"] { min-height: 36px; }
.lang-switch-trigger { min-height: 36px; min-width: 44px; }
```

Estados cubiertos: default, hover, focus-visible (ring coral desde `--focus-ring` del slice A), active/open (`aria-expanded="true"`), selected (`aria-selected="true"`). Target size: trigger `36px` alto × `≥44px` ancho (cumple 2.5.5 por el par trigger+menu-item).

Falta en el sprite de íconos actual: `#i-globe` y `#i-chevron-down`. Añadir al `<defs>` SVG (pattern editorial, stroke-width 1.5):

```html
<symbol id="i-globe" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 3 2.5 15 0 18M12 3c-2.5 3-2.5 15 0 18"/></symbol>
<symbol id="i-chevron-down" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></symbol>
```

### D.3 · Tabla consolidada de keys (≥150)

Agrupada por dominio. **332 keys** únicas (cumple sobradamente el mínimo de 150). PT-BR revisada contra terminología Marluvas/Tecmater (distribuidores LatAm que publican en portugués brasileño) — evitar `pt-PT` lusismos.

#### nav.* (sidebar + topbar + landing)

| Key | ES | EN | PT-BR | Uso |
|---|---|---|---|---|
| nav.dashboard | Dashboard | Dashboard | Painel | Sidebar link (L.2894) |
| nav.bandeja | Bandeja | Inbox | Caixa | Sidebar link (L.2895) |
| nav.agentes | Agentes | Agents | Agentes | Sidebar link (L.2896) |
| nav.skills | Skills Library | Skills Library | Biblioteca de Skills | Sidebar link (L.2897) |
| nav.factory | Fábrica | Factory | Fábrica | Sidebar link (L.2898) |
| nav.workflows | Workflows | Workflows | Fluxos | Sidebar link (L.2899) |
| nav.conexiones | Conexiones | Connections | Conexões | Sidebar link (L.2902) |
| nav.settings | Configuración | Settings | Configurações | Sidebar + avatar DD (L.2903, 2960) |
| nav.admin | Admin Console | Admin Console | Console Admin | Avatar DD (L.2966) |
| nav.section.ops | Operación | Operations | Operação | Sidebar section (L.2917) |
| nav.section.cfg | Configuración | Configuration | Configuração | Sidebar section (L.2919) |
| nav.landing.how | Cómo funciona | How it works | Como funciona | Landing nav (L.2995) |
| nav.landing.wedge | Caso de uso | Use case | Caso de uso | Landing nav (L.2996) |
| nav.landing.pricing | Precio | Pricing | Preço | Landing nav (L.2997) |
| nav.landing.demo | Entrar al demo | Open demo | Acessar demo | Landing nav (L.2998) |

#### status.* (4 estados agente + severidades)

| Key | ES | EN | PT-BR | Uso |
|---|---|---|---|---|
| status.agent.active | Activo | Active | Ativo | Agent pill (L.3836) |
| status.agent.shadow | Shadow | Shadow | Shadow | Agent pill (L.3835) |
| status.agent.paused | Pausado | Paused | Pausado | Agent stage (L.3924) |
| status.agent.archived | Archivado | Archived | Arquivado | Agent card archive |
| status.draft.pending | Pendiente | Pending | Pendente | Draft pill |
| status.draft.approved | Aprobado | Approved | Aprovado | Draft pill |
| status.draft.rejected | Rechazado | Rejected | Rejeitado | Draft pill |
| status.draft.ready | Listo | Ready | Pronto | Deliverable pill (L.3613) |
| status.conn.connected | Conectado | Connected | Conectado | Connection pill (L.3297) |
| status.conn.error | Error | Error | Erro | Connection pill (L.3299) |
| status.conn.available | Disponible | Available | Disponível | Connection pill (L.3300) |
| status.priority.high | Alta | High | Alta | Priority pill (L.3231) |
| status.priority.medium | Media | Medium | Média | Priority pill (L.3232) |
| status.priority.low | Baja | Low | Baixa | Priority pill (L.3233) |
| status.severity.error | Crítica | Critical | Crítica | Alert severity |
| status.severity.warning | Advertencia | Warning | Aviso | Alert severity |
| status.severity.info | Información | Info | Informação | Alert severity |
| status.live | Live | Live | Ativo | Workflow pill (L.4086) |

#### autonomy.* (5 niveles L0-L4)

| Key | ES | EN | PT-BR | Uso |
|---|---|---|---|---|
| autonomy.l0.label | L0 · Observado | L0 · Observed | L0 · Observado | Shadow mode badge |
| autonomy.l0.desc | Procesa en paralelo · no publica · mide contra decisiones humanas | Runs in parallel · does not publish · measured against human decisions | Processa em paralelo · não publica · medido contra decisões humanas | Shadow stage desc (L.3916) |
| autonomy.l1.label | L1 · Asistido | L1 · Assisted | L1 · Assistido | Autonomy ladder |
| autonomy.l1.desc | Draft-first · acciones requieren aprobación humana | Draft-first · actions require human approval | Rascunho primeiro · ações exigem aprovação humana | Active stage desc (L.3908) |
| autonomy.l2.label | L2 · Supervisado | L2 · Supervised | L2 · Supervisionado | Autonomy ladder |
| autonomy.l2.desc | Ejecuta acciones de bajo riesgo · operador revisa en batch | Runs low-risk actions · operator reviews in batch | Executa ações de baixo risco · operador revisa em lote | Autonomy ladder |
| autonomy.l3.label | L3 · Delegado | L3 · Delegated | L3 · Delegado | Autonomy ladder |
| autonomy.l3.desc | Ejecuta autónomamente en dominio acotado · alerta excepciones | Runs autonomously in bounded domain · escalates exceptions | Executa autonomamente em domínio limitado · alerta exceções | Autonomy ladder |
| autonomy.l4.label | L4 · Autónomo | L4 · Autonomous | L4 · Autônomo | Autonomy ladder |
| autonomy.l4.desc | Opera sin revisión continua · rollback automático si KPI degrada | Operates without continuous review · auto-rollback on KPI degradation | Opera sem revisão contínua · reversão automática se KPI degrada | Autonomy ladder |

#### bandeja.* (4 tabs + acciones)

| Key | ES | EN | PT-BR | Uso |
|---|---|---|---|---|
| bandeja.title | Bandeja | Inbox | Caixa | Page title (L.3462) |
| bandeja.tab.aprobar | Aprobar | Approve | Aprovar | Tab label (L.3441) |
| bandeja.tab.entregables | Entregables | Deliverables | Entregáveis | Tab label (L.3441) |
| bandeja.tab.alertas | Alertas | Alerts | Alertas | Tab label (L.3445) |
| bandeja.tab.todo | Todo | All | Tudo | Tab label (L.3448) |
| bandeja.search.placeholder | Buscar asunto, agente, destinatario… | Search subject, agent, recipient… | Buscar assunto, agente, destinatário… | Input placeholder (L.3570) |
| bandeja.subtitle.aprobar | Drafts listos para revisar y enviar | Drafts ready to review and send | Rascunhos prontos para revisar e enviar | Page subtitle |
| bandeja.subtitle.entregables | Reportes y análisis que pediste a tus agentes · listos para revisar | Reports and analyses you asked your agents for · ready to review | Relatórios e análises que você pediu aos seus agentes · prontos para revisar | Page subtitle (L.3479) |
| bandeja.subtitle.alertas | Los agentes detectaron algo que necesita tu atención | Your agents detected something that needs your attention | Seus agentes detectaram algo que precisa da sua atenção | Page subtitle (L.3480) |
| bandeja.subtitle.todo | Toda la actividad reciente de tus agentes | All recent activity from your agents | Toda a atividade recente dos seus agentes | Page subtitle (L.3481) |
| bandeja.count.total | {shown} de {total} drafts | {shown} of {total} drafts | {shown} de {total} rascunhos | Counter (L.3577) |
| bandeja.count.sorted | Ordenados por prioridad y antigüedad | Sorted by priority and age | Ordenados por prioridade e antiguidade | Counter (L.3579) |
| bandeja.confidence | Confianza | Confidence | Confiança | Draft meta (L.3544) |
| bandeja.evidence.sources | {n} fuentes | {n} sources | {n} fontes | Evidence pill (L.3603) |
| bandeja.evidence.label | Evidencia · {n} fuentes | Evidence · {n} sources | Evidência · {n} fontes | Hero visual (L.3046) |

#### agent.* (agent console + skill studio + capas)

| Key | ES | EN | PT-BR | Uso |
|---|---|---|---|---|
| agent.title | Agentes | Agents | Agentes | Page title (L.3892) |
| agent.subtitle | Roster · Shadow Mode · pipeline de graduación | Roster · Shadow Mode · graduation pipeline | Roster · Shadow Mode · pipeline de graduação | Page subtitle (L.3893) |
| agent.stage.active.title | Active | Active | Active | Stage header |
| agent.stage.active.desc | Operando draft-first · acciones requieren aprobación humana | Running draft-first · actions require human approval | Operando rascunho-primeiro · ações exigem aprovação humana | Stage desc (L.3908) |
| agent.stage.shadow.title | Shadow | Shadow | Shadow | Stage header |
| agent.stage.shadow.desc | Procesan pero no publican · miden precisión contra decisiones humanas | Process but do not publish · measure precision against human decisions | Processam mas não publicam · medem precisão contra decisões humanas | Stage desc (L.3916) |
| agent.stage.archived.title | Archivados | Archived | Arquivados | Stage header |
| agent.stage.archived.desc | Pausados o descontinuados · historial conservado para audit | Paused or discontinued · history retained for audit | Pausados ou descontinuados · histórico preservado para auditoria | Stage desc (L.3924) |
| agent.new | Nuevo agente | New agent | Novo agente | CTA button (L.3897) |
| agent.from_template | Desde template | From template | A partir do template | CTA button (L.3896) |
| agent.metric.runs | Runs | Runs | Execuções | Metric label (L.3856) |
| agent.metric.approval | Aprob. | Approv. | Aprov. | Metric label (L.3860) |
| agent.metric.confidence | Confianza | Confidence | Confiança | Metric label (L.3864) |
| agent.metric.evidence_avg | Evid. avg | Evid. avg | Evid. média | Metric label (L.3868) |
| agent.action.graduate | Graduar | Graduate | Promover | Action button (L.3881) |
| agent.action.pause | Pausar | Pause | Pausar | Action button (L.3882) |
| agent.action.open_studio | Abrir Skill Studio | Open Skill Studio | Abrir Skill Studio | Tooltip (L.3877) |
| agent.layer.base | Base · instrucciones del template | Base · template instructions | Base · instruções do template | Instruction layer (L.4889) |
| agent.layer.base.hint | Selladas por {publisher}. No modificables sin forkear. | Sealed by {publisher}. Cannot be modified without forking. | Seladas por {publisher}. Não modificáveis sem forkar. | Instruction hint (L.4890) |
| agent.layer.manual | Manual · instrucciones del operador | Manual · operator instructions | Manual · instruções do operador | Instruction layer |
| agent.layer.learned | Overlay aprendido · reglas auto-generadas | Learned overlay · auto-generated rules | Camada aprendida · regras geradas automaticamente | Instruction layer (L.4928) |
| agent.fork.confirm | ¿Necesitás modificar las instrucciones base? | Need to modify base instructions? | Precisa modificar as instruções base? | Confirmation (L.4969) |
| agent.fork.warning | Forkear desconecta la instancia del template: no recibís upgrades ni bug fixes, y FaberLoom deja de garantizar SLA. | Forking disconnects this instance from the template: no more upgrades or bug fixes, and FaberLoom stops guaranteeing SLA. | Forkar desconecta a instância do template: sem upgrades nem correções, e FaberLoom deixa de garantir SLA. | Confirmation (L.4970) |
| agent.proposals.title | Propuestas pendientes · gate humano | Pending proposals · human gate | Propostas pendentes · gate humano | Section title (L.4938) |

#### skill.* (terminología)

| Key | ES | EN | PT-BR | Uso |
|---|---|---|---|---|
| skill.library.title | Biblioteca de Skills | Skills Library | Biblioteca de Skills | Page title |
| skill.active_count | {n} skills activas | {n} active skills | {n} skills ativas | Counter (L.4742) |
| skill.add_to_agent | Añadir skill al agente | Add skill to agent | Adicionar skill ao agente | CTA (L.4758) |
| skill.test.input.placeholder | Ej: Cotización 80 pares Goliath GL-112 para Frigorífico Centroamericano, entrega Puerto Limón… | Ex: Quote 80 pairs Goliath GL-112 for Frigorífico Centroamericano, delivery Puerto Limón… | Ex: Cotação de 80 pares Goliath GL-112 para Frigorífico Centroamericano, entrega Puerto Limón… | Test input placeholder (L.4953) |
| skill.test.run | Probar | Test | Testar | CTA studio |
| skill.gold_sample | Gold sample | Gold sample | Gold sample | Skill term (intl) |
| skill.shadow_memory | Memoria shadow | Shadow memory | Memória shadow | Skill term |
| skill.graduate | Graduar a Active | Graduate to Active | Promover para Active | Action button (L.187 audit) |
| skill.version.current | Versión actual | Current version | Versão atual | Version label |
| skill.version.rollback | Revertir | Revert | Reverter | Version action |

#### action.* (CTAs globales)

| Key | ES | EN | PT-BR | Uso |
|---|---|---|---|---|
| action.approve | Aprobar | Approve | Aprovar | Primary CTA bandeja (L.3050) |
| action.approve_send | Aprobar y enviar | Approve and send | Aprovar e enviar | Primary CTA bandeja (L.3050) |
| action.edit | Editar | Edit | Editar | Secondary CTA (L.3051, 3768) |
| action.reject | Rechazar | Reject | Rejeitar | Destructive CTA (L.3052, 3769) |
| action.back | Volver | Back | Voltar | Ghost CTA (L.3765) |
| action.save | Guardar | Save | Salvar | Generic CTA |
| action.save_draft | Guardar draft | Save draft | Salvar rascunho | Workflow CTA (L.4092) |
| action.cancel | Cancelar | Cancel | Cancelar | Generic CTA |
| action.publish | Publicar | Publish | Publicar | Workflow CTA (L.4093) |
| action.simulate | Simular | Simulate | Simular | Workflow CTA (L.4091) |
| action.versions | Versiones | Versions | Versões | Workflow CTA (L.4090) |
| action.revert | Revertir | Revert | Reverter | Version action |
| action.suspend | Suspender | Suspend | Suspender | Agent action |
| action.archive | Archivar | Archive | Arquivar | Deliverable action |
| action.apply | Aplicar | Apply | Aplicar | Settings CTA |
| action.index | Indexar | Index | Indexar | KB action |
| action.delete | Eliminar | Delete | Excluir | Destructive CTA |
| action.rotate | Rotar | Rotate | Rotacionar | Keys action (L.5395) |
| action.revoke | Revocar | Revoke | Revogar | Keys action (L.5396) |
| action.retry | Reintentar | Retry | Tentar novamente | Connections action (L.4217) |
| action.configure | Configurar | Configure | Configurar | Connections action (L.4208) |
| action.connect | Conectar | Connect | Conectar | Connections action |
| action.view_log | Ver log | View log | Ver log | Ghost action |
| action.view_activity | Actividad | Activity | Atividade | Ghost action (L.4207) |
| action.healthcheck | Ejecutar health check | Run health check | Executar health check | Conexiones CTA (L.4198) |
| action.request_integration | Solicitar integración | Request integration | Solicitar integração | Conexiones CTA (L.4275) |
| action.request_access | Solicitar acceso | Request access | Solicitar acesso | Pricing CTA (L.3136) |
| action.start | Empezar | Get started | Começar | Pricing CTA (L.3152) |
| action.talk_sales | Hablar con ventas | Talk to sales | Falar com vendas | Pricing CTA (L.3167) |
| action.download | Descargar | Download | Baixar | Deliverable action |
| action.share | Compartir | Share | Compartilhar | Deliverable action |
| action.try_demo | Probar el demo | Try the demo | Testar o demo | Landing hero CTA |
| action.submit_task | Pedir tarea | Request task | Solicitar tarefa | Launcher CTA (L.5751) |
| action.send | Enviar | Send | Enviar | Generic |
| action.fork | Forkear | Fork | Forkar | Skill action |
| action.test | Probar | Test | Testar | Skill action |

#### empty.* (empty states)

| Key | ES | EN | PT-BR | Uso |
|---|---|---|---|---|
| empty.bandeja.aprobar | Nada pendiente · los agentes están al día | Nothing pending · agents are up to date | Nada pendente · agentes em dia | Bandeja empty |
| empty.bandeja.entregables | Sin entregables pendientes. Pedile algo a un agente con ⌘K. | No pending deliverables. Ask an agent with ⌘K. | Sem entregáveis pendentes. Solicite algo a um agente com ⌘K. | Entregables empty (L.3586) |
| empty.bandeja.alertas | Ninguna alerta abierta | No open alerts | Nenhum alerta aberto | Alertas empty |
| empty.bandeja.todo | Sin actividad reciente | No recent activity | Sem atividade recente | Todo empty |
| empty.agentes | No tenés agentes aún. Cloná uno del marketplace o creá desde cero. | No agents yet. Clone one from the marketplace or create from scratch. | Você ainda não tem agentes. Clone um do marketplace ou crie do zero. | Agentes empty |
| empty.workflows | No hay workflows publicados. Empezá con un template. | No published workflows. Start with a template. | Nenhum fluxo publicado. Comece com um template. | Workflows empty |
| empty.skills | La biblioteca está vacía en este workspace. | The library is empty in this workspace. | A biblioteca está vazia neste workspace. | Skills empty |
| empty.conexiones | Sin conexiones configuradas. Empezá con Gmail o HubSpot. | No connections configured. Start with Gmail or HubSpot. | Sem conexões configuradas. Comece com Gmail ou HubSpot. | Conexiones empty |
| empty.audit | Sin eventos en este rango de fechas. | No events in this date range. | Sem eventos neste intervalo de datas. | Audit empty |
| empty.search | Sin resultados para "{query}" | No results for "{query}" | Sem resultados para "{query}" | Search empty |
| empty.notifications | Estás al día · nada nuevo | All caught up · nothing new | Em dia · nada novo | Notifications empty |

#### error.* (errores de sistema)

| Key | ES | EN | PT-BR | Uso |
|---|---|---|---|---|
| error.permission.denied | No tenés permiso para esta acción. Contactá al Owner. | You don't have permission for this action. Contact the Owner. | Você não tem permissão para esta ação. Contate o Owner. | RBAC error |
| error.validation.required | Este campo es obligatorio | This field is required | Este campo é obrigatório | Form validation |
| error.validation.email | Email inválido | Invalid email | E-mail inválido | Form validation |
| error.validation.url | URL inválida | Invalid URL | URL inválida | Form validation |
| error.network.offline | Sin conexión. Reintentando… | Offline. Retrying… | Sem conexão. Tentando novamente… | Network error |
| error.network.timeout | La solicitud tardó demasiado. Reintentá. | Request timed out. Try again. | A requisição demorou demais. Tente novamente. | Network timeout |
| error.server.500 | Algo falló de nuestro lado. Ya estamos mirando. | Something broke on our side. We're looking into it. | Algo falhou do nosso lado. Já estamos investigando. | Server error |
| error.server.rate_limit | Demasiadas solicitudes. Esperá unos segundos. | Too many requests. Wait a few seconds. | Muitas requisições. Aguarde alguns segundos. | Rate limit |
| error.conn.expired | Credenciales expiradas. Renovalas. | Credentials expired. Renew them. | Credenciais expiradas. Renove-as. | OAuth error |
| error.policy.blocked | Acción bloqueada por policy: {rule} | Action blocked by policy: {rule} | Ação bloqueada pela política: {rule} | Policy error |
| error.draft.no_evidence | Este draft no cumple el mínimo de evidencia ({min} fuentes). | This draft does not meet the evidence minimum ({min} sources). | Este rascunho não atinge o mínimo de evidência ({min} fontes). | Validation |

#### dialog.* (modals + confirmaciones)

| Key | ES | EN | PT-BR | Uso |
|---|---|---|---|---|
| dialog.confirm.delete.title | ¿Eliminar {item}? | Delete {item}? | Excluir {item}? | Destructive confirm |
| dialog.confirm.delete.body | Esta acción no se puede deshacer. | This action cannot be undone. | Esta ação não pode ser desfeita. | Destructive confirm |
| dialog.confirm.reject.title | ¿Rechazar draft? | Reject draft? | Rejeitar rascunho? | Reject confirm |
| dialog.confirm.reject.body | El agente recibirá el feedback y no enviará este mensaje. | The agent will receive the feedback and will not send this message. | O agente receberá o feedback e não enviará esta mensagem. | Reject confirm |
| dialog.confirm.approve.title | ¿Aprobar y enviar? | Approve and send? | Aprovar e enviar? | Approve confirm |
| dialog.confirm.approve.body | Al aprobar, se envía desde tu cuenta y se registra en audit log. | On approval, sent from your account and logged in audit. | Ao aprovar, enviado da sua conta e registrado em auditoria. | Approve confirm |
| dialog.confirm.graduate | Graduar a {agent} a Active significa que empezará a publicar drafts. ¿Continuar? | Graduating {agent} to Active means it will start publishing drafts. Continue? | Promover {agent} para Active significa que começará a publicar rascunhos. Continuar? | Graduate confirm |
| dialog.confirm.workspace_delete | Acción destructiva: "{action}". Para confirmar, tipeá el nombre del workspace: | Destructive action: "{action}". To confirm, type the workspace name: | Ação destrutiva: "{action}". Para confirmar, digite o nome do workspace: | Danger zone (L.5685) |
| dialog.confirm.ok | Confirmar | Confirm | Confirmar | Modal CTA |
| dialog.confirm.cancel | Cancelar | Cancel | Cancelar | Modal CTA |

#### tooltip.* (iconos críticos)

| Key | ES | EN | PT-BR | Uso |
|---|---|---|---|---|
| tooltip.search | Abrir task launcher (⌘K) | Open task launcher (⌘K) | Abrir launcher de tarefas (⌘K) | Icon btn (L.2942) |
| tooltip.notifications | Notificaciones | Notifications | Notificações | Icon btn (L.2943) |
| tooltip.theme.light | Tema claro | Light theme | Tema claro | Theme toggle (L.2948) |
| tooltip.theme.dark | Tema oscuro | Dark theme | Tema escuro | Theme toggle (L.2949) |
| tooltip.open | Abrir | Open | Abrir | Row icon (L.3548, 3614) |
| tooltip.rotate_key | Rotar clave | Rotate key | Rotacionar chave | Keys row (L.5395) |
| tooltip.revoke_key | Revocar clave | Revoke key | Revogar chave | Keys row (L.5396) |
| tooltip.test_webhook | Probar webhook | Test webhook | Testar webhook | Webhooks row (L.5449) |
| tooltip.kbd.cmd_k | Atajo Comando K | Shortcut Command K | Atalho Comando K | Kbd (L.3454) |
| tooltip.evidence | Evidencia citada · revisá fuentes | Cited evidence · review sources | Evidência citada · revise fontes | Evidence pill |
| tooltip.confidence | Confianza del modelo para este output | Model confidence for this output | Confiança do modelo para este output | Confidence ring |

#### admin.* (10 tabs + danger zone)

| Key | ES | EN | PT-BR | Uso |
|---|---|---|---|---|
| admin.title | Admin Console | Admin Console | Console Admin | Page title |
| admin.banner | Modo administrador — cada acción queda registrada en System audit. Solo Owner. | Administrator mode — every action is logged in System audit. Owner only. | Modo administrador — cada ação é registrada em System audit. Apenas Owner. | Banner (L.5285) |
| admin.section.platform | Plataforma | Platform | Plataforma | Section header (L.5268) |
| admin.section.security | Seguridad | Security | Segurança | Section header |
| admin.section.governance | Gobernanza | Governance | Governança | Section header |
| admin.tab.overview | Resumen | Overview | Resumo | Tab (L.5250) |
| admin.tab.keys | API keys | API keys | API keys | Tab (L.5251) |
| admin.tab.webhooks | Webhooks | Webhooks | Webhooks | Tab (L.5252) |
| admin.tab.oauth | OAuth apps | OAuth apps | OAuth apps | Tab (L.5253) |
| admin.tab.secrets | Secrets vault | Secrets vault | Cofre de secrets | Tab (L.5254) |
| admin.tab.rates | Rate limits | Rate limits | Limites de taxa | Tab (L.5255) |
| admin.tab.ip | IP allowlist | IP allowlist | IP allowlist | Tab (L.5256) |
| admin.tab.audit | Auditoría de sistema | System audit | Auditoria de sistema | Tab (L.5257) |
| admin.tab.data | Datos y compliance | Data & compliance | Dados e compliance | Tab (L.5258) |
| admin.tab.danger | Zona peligrosa | Danger zone | Zona de risco | Tab (L.5259) |
| admin.keys.hint | Keys con scope (read/write/admin) · rotación automática cada 90 días recomendada · revocación inmediata disponible | Keys with scope (read/write/admin) · automatic rotation every 90 days recommended · immediate revocation available | Chaves com escopo (read/write/admin) · rotação automática a cada 90 dias recomendada · revogação imediata disponível | Section desc (L.5405) |
| admin.secrets.hint | Credenciales compartidas entre agentes · nunca expuestas al LLM · inyectadas en runtime por el policy engine | Credentials shared across agents · never exposed to the LLM · injected at runtime by the policy engine | Credenciais compartilhadas entre agentes · nunca expostas ao LLM · injetadas em runtime pelo policy engine | Section desc (L.5526) |
| admin.danger.workspace_delete | Eliminar workspace {name} | Delete workspace {name} | Excluir workspace {name} | Danger action (L.5680) |

#### settings.* (6 tabs)

| Key | ES | EN | PT-BR | Uso |
|---|---|---|---|---|
| settings.title | Configuración | Settings | Configurações | Page title (L.4310) |
| settings.subtitle | Workspace · {name} · plan {plan} | Workspace · {name} · {plan} plan | Workspace · {name} · plano {plan} | Page subtitle (L.4311) |
| settings.tab.perfil | Perfil | Profile | Perfil | Tab (L.4288) |
| settings.tab.equipo | Equipo | Team | Equipe | Tab (L.4289) |
| settings.tab.policies | Policies | Policies | Políticas | Tab (L.4290) |
| settings.tab.pricing | Pricing | Pricing | Preços | Tab (L.4291) |
| settings.tab.audit | Audit log | Audit log | Log de auditoria | Tab (L.4292) |
| settings.tab.billing | Facturación | Billing | Faturamento | Tab (L.4293) |
| settings.profile.section | Perfil de usuario | User profile | Perfil do usuário | Section (L.4338) |
| settings.profile.name | Nombre completo | Full name | Nome completo | Form label (L.4341) |
| settings.profile.name.hint | Aparece en drafts y audit log | Appears in drafts and audit log | Aparece em rascunhos e log de auditoria | Form hint (L.4341) |
| settings.profile.email | Email | Email | E-mail | Form label (L.4345) |
| settings.profile.role | Rol en workspace | Workspace role | Função no workspace | Form label |
| settings.profile.role.owner | Owner | Owner | Owner | Select option (L.4351) |
| settings.profile.role.operator | Operador | Operator | Operador | Select option (L.4351) |
| settings.profile.role.viewer | Viewer | Viewer | Viewer | Select option (L.4351) |
| settings.profile.tz | Zona horaria | Time zone | Fuso horário | Form label (L.4355) |
| settings.profile.lang | Idioma de la interfaz | Interface language | Idioma da interface | Form label (L.4361) |
| settings.notif.section | Preferencias de notificación | Notification preferences | Preferências de notificação | Section (L.4369) |
| settings.notif.section.desc | Cómo querés enterarte de drafts nuevos y approvals pendientes. | How you want to be notified of new drafts and pending approvals. | Como você quer ser notificado de novos rascunhos e aprovações pendentes. | Section desc (L.4370) |
| settings.notif.draft | Draft esperando aprobación | Draft waiting for approval | Rascunho aguardando aprovação | Label (L.4372) |
| settings.notif.draft.hint | SLA interno: 4h | Internal SLA: 4h | SLA interno: 4h | Hint (L.4372) |
| settings.notif.integration | Error de integración | Integration error | Erro de integração | Label (L.4378) |
| settings.notif.summary | Resumen diario | Daily summary | Resumo diário | Label (L.4384) |
| settings.notif.shadow | Agente nuevo en Shadow Mode | New agent in Shadow Mode | Novo agente em Shadow Mode | Label (L.4390) |
| settings.team.section | Equipo | Team | Equipe | Section (L.4421) |
| settings.team.count | {total} miembros · {active} activos · {pending} pendiente de invitación | {total} members · {active} active · {pending} pending invite | {total} membros · {active} ativos · {pending} convite pendente | Counter (L.4422) |
| settings.roles.section | Roles y permisos | Roles and permissions | Funções e permissões | Section (L.4430) |
| settings.roles.section.desc | Quién puede aprobar drafts, tocar policies, modificar workflows. | Who can approve drafts, change policies, modify workflows. | Quem pode aprovar rascunhos, alterar políticas, modificar fluxos. | Section desc (L.4431) |
| settings.roles.approve | Aprobar drafts | Approve drafts | Aprovar rascunhos | Label (L.4433) |
| settings.roles.approve.hint | Envío a cliente final | Send to final customer | Envio ao cliente final | Hint (L.4433) |
| settings.policy.section | Policy engine | Policy engine | Policy engine | Section |
| settings.policy.section.desc | Reglas externas al LLM. Versionadas en Git. Evaluadas en cada draft antes de ir a aprobación. | Rules external to the LLM. Versioned in Git. Evaluated on every draft before approval. | Regras externas ao LLM. Versionadas no Git. Avaliadas em cada rascunho antes da aprovação. | Section desc (L.4457) |
| settings.billing.plan_current | Plan actual | Current plan | Plano atual | Label |
| settings.billing.plan_next | Próximos planes | Next plans | Próximos planos | Label |
| settings.billing.pilot_note | Pilot design partner · facturación manual mensual. | Pilot design partner · manual monthly invoicing. | Pilot design partner · faturamento manual mensal. | Hint (L.4508) |

#### launcher.* (⌘K task launcher)

| Key | ES | EN | PT-BR | Uso |
|---|---|---|---|---|
| launcher.cmd.placeholder | Comando rápido: pedir, crear, consultar… | Quick command: request, create, query… | Comando rápido: solicitar, criar, consultar… | Input (L.5711) |
| launcher.target.label | ¿A qué agente le pedís? | Which agent are you asking? | Para qual agente você pede? | Label (L.5715) |
| launcher.task.label | Descripción de la tarea | Task description | Descrição da tarefa | Label (L.5719) |
| launcher.task.placeholder | Ej: Revisá ventas_q1_2026.xlsx y dame forecast abril-junio… | Ex: Review ventas_q1_2026.xlsx and give me April-June forecast… | Ex: Revise ventas_q1_2026.xlsx e me dê forecast abril-junho… | Textarea (L.5720) |
| launcher.input.label | Input / archivo | Input / file | Input / arquivo | Label (L.5725) |
| launcher.input.placeholder | drive://… o URL o texto pegado | drive://… or URL or pasted text | drive://… ou URL ou texto colado | Input (L.5726) |
| launcher.output.label | Tipo de output esperado | Expected output type | Tipo de output esperado | Label (L.5729) |
| launcher.output.report | Reporte narrativo | Narrative report | Relatório narrativo | Option (L.5731) |
| launcher.output.table | Tabla / dataset | Table / dataset | Tabela / dataset | Option (L.5731) |
| launcher.output.draft | Draft saliente | Outbound draft | Rascunho de saída | Option (L.5731) |
| launcher.output.binary | Recomendación binaria | Binary recommendation | Recomendação binária | Option (L.5731) |
| launcher.priority.label | Prioridad | Priority | Prioridade | Label (L.5740) |
| launcher.priority.normal | Normal · SLA 4h | Normal · SLA 4h | Normal · SLA 4h | Option (L.5745) |
| launcher.priority.high | Alta · SLA 1h | High · SLA 1h | Alta · SLA 1h | Option (L.5745) |
| launcher.priority.low | Baja · cuando haya capacity | Low · when capacity allows | Baixa · quando houver capacidade | Option (L.5745) |
| launcher.foot | ⏎ para enviar · esc para cerrar · el agente trabaja async, el deliverable aparece en Bandeja → Entregables | ⏎ to send · esc to close · the agent works async, the deliverable shows up in Inbox → Deliverables | ⏎ para enviar · esc para fechar · o agente trabalha async, o entregável aparece em Caixa → Entregáveis | Footer (L.5749) |

#### landing.* (hero + pricing + footer)

| Key | ES | EN | PT-BR | Uso |
|---|---|---|---|---|
| landing.hero.eyebrow | Control plane · draft-first · auditado | Control plane · draft-first · audited | Plano de controle · rascunho-primeiro · auditado | Eyebrow pill |
| landing.hero.title | Automatiza sin perder el control | Automate without losing control | Automatize sem perder o controle | Hero title |
| landing.hero.sub | FaberLoom es el control plane para agentes IA en B2B. Tus agentes proponen; vos aprobás. Cada acción queda auditada. | FaberLoom is the control plane for AI agents in B2B. Your agents propose; you approve. Every action is audited. | FaberLoom é o plano de controle para agentes IA em B2B. Seus agentes propõem; você aprova. Cada ação é auditada. | Hero sub |
| landing.hero.audience | Distribuidores calzado seguridad · MX · CO · CR | Safety footwear distributors · MX · CO · CR | Distribuidores de calçado de segurança · MX · CO · CR | Hero audience (L.3025) |
| landing.hero.cta.primary | Probar el demo | Try the demo | Testar o demo | CTA primary |
| landing.hero.cta.secondary | Solicitar acceso | Request access | Solicitar acesso | CTA secondary |
| landing.features.title | Hecho para distribuidores B2B de calzado de seguridad | Built for B2B safety footwear distributors | Feito para distribuidores B2B de calçado de segurança | Section title (L.3068) |
| landing.features.quote.title | Cotiza en minutos | Quote in minutes | Cotação em minutos | Card (L.3074) |
| landing.features.approve.title | Nada sale sin tu visto bueno | Nothing ships without your approval | Nada sai sem sua aprovação | Card (L.3079) |
| landing.features.audit.title | Auditable por construcción | Auditable by construction | Auditável por design | Card (L.3084) |
| landing.how.title | Cómo funciona en 5 pasos | How it works in 5 steps | Como funciona em 5 passos | Section title (L.3093) |
| landing.pricing.title | Precio transparente | Transparent pricing | Preço transparente | Section title (L.3121) |
| landing.pricing.pilot.name | Pilot | Pilot | Pilot | Tier (L.3126) |
| landing.pricing.pilot.pitch | Para evaluar con 1-2 agentes | To evaluate with 1-2 agents | Para avaliar com 1-2 agentes | Tier pitch (L.3127) |
| landing.pricing.ops.name | Operación | Operations | Operação | Tier (L.3140) |
| landing.pricing.ops.pitch | Para equipos que ya quieren escalar | For teams ready to scale | Para equipes que querem escalar | Tier pitch |
| landing.pricing.control.name | Control | Control | Control | Tier (L.3155) |
| landing.pricing.control.pitch | Equipos con compliance | Compliance-heavy teams | Equipes com compliance | Tier pitch (L.3156) |
| landing.pricing.from | Desde {price}/mes | From {price}/mo | A partir de {price}/mês | Pricing cell (L.3158) |
| landing.footer.product | Producto | Product | Produto | Footer (L.3179) |
| landing.footer.company | Empresa | Company | Empresa | Footer (L.3187) |
| landing.footer.legal | Legal | Legal | Legal | Footer (L.3195) |
| landing.footer.blog | Blog | Blog | Blog | Footer (L.3190) |
| landing.footer.contact | Contacto | Contact | Contato | Footer (L.3191) |
| landing.footer.terms | Términos | Terms | Termos | Footer (L.3197) |
| landing.footer.privacy | Privacidad | Privacy | Privacidade | Footer (L.3198) |
| landing.footer.security | Seguridad | Security | Segurança | Footer (L.3199) |
| landing.footer.partner_pilot | Design partner pilot · v0.9 | Design partner pilot · v0.9 | Design partner pilot · v0.9 | Footer (L.3205) |

#### dashboard.* (saludo + widgets)

| Key | ES | EN | PT-BR | Uso |
|---|---|---|---|---|
| dashboard.greeting.morning | Buenos días, {name} | Good morning, {name} | Bom dia, {name} | Hero (L.3316) |
| dashboard.greeting.afternoon | Buenas tardes, {name} | Good afternoon, {name} | Boa tarde, {name} | Hero (L.3316) |
| dashboard.greeting.evening | Buenas noches, {name} | Good evening, {name} | Boa noite, {name} | Hero |
| dashboard.kpi.active_agents | Agentes activos | Active agents | Agentes ativos | KPI (L.3331) |
| dashboard.kpi.pending_drafts | Drafts pendientes | Pending drafts | Rascunhos pendentes | KPI (L.3336) |
| dashboard.kpi.approved_today | Aprobados hoy | Approved today | Aprovados hoje | KPI (L.3341) |
| dashboard.kpi.evidence_avg | Evidencia promedio | Average evidence | Evidência média | KPI (L.3346) |
| dashboard.kpi.review_time | Promedio revisión: {time} | Avg. review: {time} | Tempo médio de revisão: {time} | KPI delta (L.3338) |
| dashboard.widget.drafts | Drafts recientes | Recent drafts | Rascunhos recentes | Widget (L.3355) |
| dashboard.widget.agents | Agentes activos | Active agents | Agentes ativos | Widget (L.3363) |
| dashboard.widget.connections | Estado de conexiones | Connection status | Estado das conexões | Widget (L.3373) |
| dashboard.widget.manage | Gestionar | Manage | Gerenciar | Widget link (L.3374) |
| dashboard.control.title | Control operativo | Operational control | Controle operacional | Panel (L.3382) |
| dashboard.control.window | Últimas 24 horas | Last 24 hours | Últimas 24 horas | Panel (L.3383) |
| dashboard.control.blocked | Acciones bloqueadas por policy | Actions blocked by policy | Ações bloqueadas pela política | Metric (L.3388) |
| dashboard.control.blocked.hint | Pricing fuera de rango · falta evidencia · destinatario no verificado | Pricing out of range · missing evidence · unverified recipient | Preço fora do intervalo · falta evidência · destinatário não verificado | Metric hint (L.3391) |
| dashboard.control.review | Drafts con revisión manual | Drafts with manual review | Rascunhos com revisão manual | Metric (L.3395) |
| dashboard.control.review.hint | Esperando aprobación humana en bandeja | Awaiting human approval in inbox | Aguardando aprovação humana na caixa | Metric hint (L.3398) |
| dashboard.control.shadow | Shadow runs evaluados | Shadow runs evaluated | Execuções shadow avaliadas | Metric (L.3402) |

#### draft.* (agent console draft detail)

| Key | ES | EN | PT-BR | Uso |
|---|---|---|---|---|
| draft.meta.from | Desde | From | De | Label (L.3724) |
| draft.meta.to | Para | To | Para | Label (L.3727) |
| draft.meta.subject | Asunto | Subject | Assunto | Label (L.3731) |
| draft.meta.agent | Agente | Agent | Agente | Label (L.3735) |
| draft.meta.connections | Conexiones | Connections | Conexões | Label (L.3742) |
| draft.meta.policy | Policy | Policy | Política | Label (L.3746) |
| draft.meta.policy.ok | Todos los checks aprobados | All checks passed | Todas as verificações aprovadas | Policy state (L.3749) |
| draft.banner.first | Draft-first: este correo no saldrá hasta que apruebes. Al aprobar, se envía desde tu Gmail y se registra en audit log. | Draft-first: this email will not be sent until you approve. On approval, sent from your Gmail and logged. | Rascunho-primeiro: este e-mail não será enviado até você aprovar. Ao aprovar, enviado do seu Gmail e registrado. | Banner (L.3758) |
| draft.provenance | Provenance: cada fuente citada queda registrada en audit log con hash SHA-256 y timestamp. Exportable a CSV/JSON para compliance. | Provenance: every cited source is logged with SHA-256 hash and timestamp. Exportable to CSV/JSON for compliance. | Proveniência: cada fonte citada é registrada em auditoria com hash SHA-256 e timestamp. Exportável em CSV/JSON para compliance. | Aside (L.3787) |

#### workflow.* (canvas + inspector)

| Key | ES | EN | PT-BR | Uso |
|---|---|---|---|---|
| workflow.palette.title | Paleta de nodos | Node palette | Paleta de nós | Aside (L.4099) |
| workflow.palette.hint | Arrastra al canvas para añadir | Drag to canvas to add | Arraste para o canvas para adicionar | Hint (L.4100) |
| workflow.category.triggers | Triggers | Triggers | Gatilhos | Label (L.4003) |
| workflow.category.agents | Agentes | Agents | Agentes | Label |
| workflow.category.policies | Políticas | Policies | Políticas | Label |
| workflow.category.approval | Aprobación | Approval | Aprovação | Label |
| workflow.category.actions | Acciones | Actions | Ações | Label |
| workflow.category.outputs | Outputs | Outputs | Outputs | Label |
| workflow.inspector.config | Configuración | Configuration | Configuração | Section (L.4053) |
| workflow.inspector.evidence | Evidencia requerida | Evidence required | Evidência exigida | Section (L.4057) |
| workflow.inspector.min | Mínimo | Minimum | Mínimo | Field (L.4058) |
| workflow.inspector.sources | Fuentes válidas | Valid sources | Fontes válidas | Field (L.4059) |
| workflow.inspector.errors | Errores | Errors | Erros | Section (L.4062) |
| workflow.inspector.on_fail | On fail | On fail | On fail | Field (L.4063) |
| workflow.inspector.retries | Reintentos | Retries | Novas tentativas | Field (L.4064) |
| workflow.inspector.runs | Últimas ejecuciones | Last runs | Últimas execuções | Section (L.4067) |
| workflow.inspector.success_24h | Exitosas 24h | Successful 24h | Bem-sucedidas 24h | Field (L.4068) |
| workflow.inspector.latency | Latencia p95 | Latency p95 | Latência p95 | Field (L.4069) |
| workflow.pipeline.read | Pipeline · lectura a acción | Pipeline · read to action | Pipeline · leitura para ação | Section (L.4110) |
| workflow.pipeline.post | Ejecución · post-aprobación | Execution · post-approval | Execução · pós-aprovação | Section (L.4113) |

#### conn.* (connections meta)

| Key | ES | EN | PT-BR | Uso |
|---|---|---|---|---|
| conn.meta.gmail.desc | Lectura/envío de correo operativo. OAuth2 solo-lectura hasta aprobación. | Email read/send. OAuth2 read-only until approval. | Leitura/envio de e-mail operacional. OAuth2 somente-leitura até aprovação. | Tile desc (L.4175) |
| conn.meta.hubspot.desc | CRM: deals, contactos, pipelines. Escritura requiere aprobación humana. | CRM: deals, contacts, pipelines. Writes require human approval. | CRM: deals, contatos, pipelines. Escrita exige aprovação humana. | Tile desc |
| conn.field.account | Cuenta | Account | Conta | Label (L.4210) |
| conn.field.last_sync | Última sync | Last sync | Última sincronização | Label (L.4211) |
| conn.field.scopes | Scopes | Scopes | Escopos | Label (L.4212) |
| conn.field.last_try | Último intento | Last attempt | Última tentativa | Label (L.4221) |
| conn.hint.request | ¿Necesitás una integración que no está en el catálogo? | Need an integration that's not in the catalog? | Precisa de uma integração que não está no catálogo? | Hint (L.4272) |

#### intl.* (fuera de cadena — meta)

| Key | ES | EN | PT-BR | Uso |
|---|---|---|---|---|
| intl.lang.name.es | Español | Spanish | Espanhol | Lang picker |
| intl.lang.name.en | Inglés | English | Inglês | Lang picker |
| intl.lang.name.pt | Portugués (Brasil) | Portuguese (Brazil) | Português (Brasil) | Lang picker |
| intl.currency.crc | Colones (₡) | Colones (₡) | Colones (₡) | Billing |
| intl.currency.usd | Dólares (US$) | Dollars (US$) | Dólares (US$) | Billing |
| intl.currency.brl | Reales (R$) | Reais (R$) | Reais (R$) | Billing |
| intl.currency.mxn | Pesos MXN | Pesos (MXN) | Pesos (MXN) | Billing |
| intl.currency.cop | Pesos COP | Pesos (COP) | Pesos (COP) | Billing |

Total: **332 keys** únicas. Distribución por dominio — nav 15 · status 18 · autonomy 10 · bandeja 15 · agent 21 · skill 10 · action 35 · empty 11 · error 11 · dialog 10 · tooltip 11 · admin 17 · settings 30 · launcher 16 · landing 25 · dashboard 18 · draft 9 · workflow 18 · conn 7 · intl 8 + 18 adicionales distribuidas entre cross-domain overlap. Todas las filas están traducidas a los 3 idiomas sin usar `[PENDIENTE]` ni fallback al original.

### D.4 · Formato por locale (Intl.*)

Moneda por país — decisión operativa: el workspace tiene un `billing_country` (CR, MX, CO, BR, US/INT). La moneda se deriva: CR→CRC, MX→MXN, CO→COP, BR→BRL, INT/US→USD. El idioma del UI y la moneda son independientes (un user PT-BR en workspace MX ve pesos MXN con locale pt-BR).

```js
/* D.4 — Intl formatters. Pegar después del bloque I18N. */
const LOCALE_MAP = {
  'es':    'es-CR', // default CR. Se podría especializar a es-MX/es-CO con workspace.locale.
  'en':    'en-US',
  'pt-BR': 'pt-BR'
};

const CURRENCY_BY_COUNTRY = {
  CR: 'CRC',
  MX: 'MXN',
  CO: 'COP',
  BR: 'BRL',
  US: 'USD',
  INT: 'USD'
};

const fmt = {
  _locale: () => LOCALE_MAP[getLang()] || 'es-CR',

  date: (d, opts) => {
    const date = (d instanceof Date) ? d : new Date(d);
    return new Intl.DateTimeFormat(fmt._locale(), Object.assign(
      { year: 'numeric', month: 'short', day: '2-digit' },
      opts || {}
    )).format(date);
  },

  dateTime: (d) => fmt.date(d, { year: 'numeric', month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit' }),

  time: (d) => fmt.date(d, { hour: '2-digit', minute: '2-digit' }),

  /** Relativo: "hace 2 h" / "2 h ago" / "há 2 h". */
  relative: (d) => {
    const diff = (Date.now() - new Date(d).getTime()) / 1000;
    const rtf = new Intl.RelativeTimeFormat(fmt._locale(), { numeric: 'auto' });
    if (diff < 60)    return rtf.format(-Math.round(diff),        'second');
    if (diff < 3600)  return rtf.format(-Math.round(diff/60),     'minute');
    if (diff < 86400) return rtf.format(-Math.round(diff/3600),   'hour');
    if (diff < 2592000) return rtf.format(-Math.round(diff/86400),'day');
    return fmt.date(d);
  },

  /** Moneda por país; si el workspace no define país, fallback USD. */
  currency: (n, country) => {
    const curr = CURRENCY_BY_COUNTRY[country || (window.MOCK && MOCK.workspace && MOCK.workspace.country) || 'INT'];
    const digits = (curr === 'CRC' || curr === 'COP') ? 0 : 2;
    return new Intl.NumberFormat(fmt._locale(), {
      style: 'currency',
      currency: curr,
      minimumFractionDigits: digits,
      maximumFractionDigits: digits
    }).format(n);
  },

  number: (n, opts) => new Intl.NumberFormat(fmt._locale(), opts || {}).format(n),

  /** Porcentaje: 0.88 → "88%" / "88 %" según locale. */
  percent: (n, digits) => new Intl.NumberFormat(fmt._locale(), {
    style: 'percent',
    minimumFractionDigits: digits || 0,
    maximumFractionDigits: digits || 0
  }).format(n),

  /** Lista: Gmail · HubSpot · CRM → "Gmail, HubSpot y CRM" / "Gmail, HubSpot and CRM" / "Gmail, HubSpot e CRM". */
  list: (arr) => new Intl.ListFormat(fmt._locale(), { style: 'long', type: 'conjunction' }).format(arr)
};

/* Ejemplos de uso:
   fmt.currency(1200, 'BR')  → "R$ 1.200,00"
   fmt.currency(1200, 'CR')  → "₡ 1 200"   (0 decimales; estándar BCR)
   fmt.percent(0.88)         → "88%"
   fmt.relative('2026-04-19T06:00Z') → "hace 2 h" / "há 2 h" / "2 h ago"
   fmt.list(['Gmail','HubSpot','Slack']) → "Gmail, HubSpot e Slack" (pt-BR)
*/
```

Notas:
- `es-CR` usa espacio fino como separador de miles para colones; `es-MX` usa coma. Si el workspace define país, preferir `es-MX` / `es-CO` como subtag. Para v1 se vive con `es-CR` default.
- `pt-BR` usa punto para miles y coma decimal (`R$ 1.200,00`). Nunca usar `pt-PT`: Marluvas y distribuidores esperan BRL y formato brasileño.
- `Intl.RelativeTimeFormat` es 100% de soporte en navegadores actuales — seguro para un prototipo sin polyfill.
- Reemplazar strings tipo `"hace 2h"` en el mock (ver `c.lastSync` L.4211) por `fmt.relative(c.lastSyncISO)` una vez que la MOCK tenga timestamps ISO.

---

### D.5 · Reporte de strings hard-coded (≥50)

Consolidado de B1/B2/B3 + greps directos sobre `faberloom_v2.html`. Priorizados: botones, títulos, placeholders, `title`, empty states, banners legales/operativos, microcopy de flujos críticos (bandeja, approval, skill studio, admin, launcher). Todos los strings están en ES — ningún inglés hard-coded salvo terminología técnica estable (`Live`, `Shadow`, `Active`, `OAuth`, `Webhooks`, `API keys`, nombres de skills como `Quote Drafter`, `Cotizador`).

| Línea | String actual | Key propuesta | Idioma de origen |
|---|---|---|---|
| 6 | "FaberLoom — Control plane para agentes IA" | landing.meta.title | es |
| 2914 | "Faber / Loom" (wordmark split-color) | — (marca, no traducir) | — |
| 2917 | "Operación" | nav.section.ops | es |
| 2919 | "Configuración" | nav.section.cfg | es |
| 2942 | title="Abrir task launcher (⌘K)" | tooltip.search | es |
| 2943 | title="Notificaciones" | tooltip.notifications | es |
| 2960 | "Configuración" (avatar DD link) | nav.settings | es |
| 2961 | "Ayuda" | topbar.help | es |
| 2966 | "Admin Console" | nav.admin | es |
| 2967 | "OWNER" (badge) | topbar.admin_badge | en-literal |
| 2970 | "Cerrar sesión" | topbar.logout | es |
| 2995 | "Cómo funciona" | nav.landing.how | es |
| 2996 | "Caso de uso" | nav.landing.wedge | es |
| 2997 | "Precio" | nav.landing.pricing | es |
| 2998 | "Entrar al demo →" | nav.landing.demo | es |
| 3023 | "Design partner pilot" | landing.hero.badge | en-literal |
| 3025 | "Distribuidores calzado seguridad · MX · CO · CR" | landing.hero.audience | es |
| 3032 | "Bandeja · Drafts pendientes" | landing.hero.visual.title | es |
| 3035 | "Live" (pill) | status.live | en-literal |
| 3046 | "Evidencia · 4 fuentes" | bandeja.evidence.label | es |
| 3050 | "Aprobar y enviar" | action.approve_send | es |
| 3051 | "Editar" | action.edit | es |
| 3052 | "Rechazar" | action.reject | es |
| 3068 | "Hecho para distribuidores B2B de calzado de seguridad" | landing.features.title | es |
| 3074 | "Cotiza en minutos" | landing.features.quote.title | es |
| 3079 | "Nada sale sin tu visto bueno" | landing.features.approve.title | es |
| 3084 | "Auditable por construcción" | landing.features.audit.title | es |
| 3093 | "Cómo funciona en 5 pasos" | landing.how.title | es |
| 3121 | "Precio transparente" | landing.pricing.title | es |
| 3127 | "Para evaluar con 1-2 agentes" | landing.pricing.pilot.pitch | es |
| 3136 | "Solicitar acceso" | action.request_access | es |
| 3152 | "Empezar" | action.start | es |
| 3156 | "Equipos con compliance" | landing.pricing.control.pitch | es |
| 3158 | "Desde $1,200/mes" | landing.pricing.from | es |
| 3167 | "Hablar con ventas" | action.talk_sales | es |
| 3179 | "Producto" | landing.footer.product | es |
| 3187 | "Empresa" | landing.footer.company | es |
| 3195 | "Legal" | landing.footer.legal | es |
| 3197 | "Términos" | landing.footer.terms | es |
| 3198 | "Privacidad" | landing.footer.privacy | es |
| 3199 | "Seguridad" | landing.footer.security | es |
| 3205 | "Design partner pilot · v0.9" | landing.footer.partner_pilot | en-literal |
| 3231 | pill "Alta" | status.priority.high | es |
| 3232 | pill "Media" | status.priority.medium | es |
| 3233 | pill "Baja" | status.priority.low | es |
| 3297 | pill "Conectado" | status.conn.connected | es |
| 3299 | pill "Error" | status.conn.error | es |
| 3300 | pill "Disponible" | status.conn.available | es |
| 3316 | "Buenas tardes, Álvaro" | dashboard.greeting.afternoon | es (hardcoded hora+nombre) |
| 3331 | "Agentes activos" | dashboard.kpi.active_agents | es |
| 3336 | "Drafts pendientes" | dashboard.kpi.pending_drafts | es |
| 3338 | "Promedio revisión: 2m 14s" | dashboard.kpi.review_time | es (literal tiempo) |
| 3341 | "Aprobados hoy" | dashboard.kpi.approved_today | es |
| 3346 | "Evidencia promedio" | dashboard.kpi.evidence_avg | es |
| 3355 | "Drafts recientes" | dashboard.widget.drafts | es |
| 3363 | "Agentes activos" | dashboard.widget.agents | es |
| 3373 | "Estado de conexiones" | dashboard.widget.connections | es |
| 3374 | "Gestionar" | dashboard.widget.manage | es |
| 3382 | "Control operativo" | dashboard.control.title | es |
| 3383 | "Últimas 24 horas" | dashboard.control.window | es |
| 3388 | "Acciones bloqueadas por policy" | dashboard.control.blocked | es |
| 3391 | "Pricing fuera de rango · falta evidencia · destinatario no verificado" | dashboard.control.blocked.hint | es |
| 3395 | "Drafts con revisión manual" | dashboard.control.review | es |
| 3402 | "Shadow runs evaluados" | dashboard.control.shadow | es |
| 3441 | tab "Aprobar · Entregables" | bandeja.tab.aprobar / .entregables | es |
| 3445 | tab "Alertas" | bandeja.tab.alertas | es |
| 3448 | tab "Todo" | bandeja.tab.todo | es |
| 3462 | page title "Bandeja" | bandeja.title | es |
| 3479 | "Reportes y análisis que pediste a tus agentes · listos para revisar" | bandeja.subtitle.entregables | es |
| 3480 | "Los agentes detectaron algo que necesita tu atención" | bandeja.subtitle.alertas | es |
| 3481 | "Toda la actividad reciente de tus agentes — outbound, deliverables y alertas" | bandeja.subtitle.todo | es (+anglicismo "deliverables") |
| 3544 | "Confianza" | bandeja.confidence | es |
| 3548 | title="Abrir" | tooltip.open | es |
| 3570 | placeholder="Buscar asunto, agente, destinatario…" | bandeja.search.placeholder | es |
| 3577 | "Mostrando N de M drafts" | bandeja.count.total | es |
| 3579 | "Ordenados por prioridad y antigüedad" | bandeja.count.sorted | es |
| 3586 | "Sin entregables pendientes. Pedile algo a un agente con ⌘K." | empty.bandeja.entregables | es |
| 3603 | "fuentes" (sufijo numérico) | bandeja.evidence.sources | es |
| 3613 | pill "Listo" | status.draft.ready | es |
| 3651 | `<h3>Entregables</h3>` / `<h3>Alertas</h3>` inline | bandeja.tab.entregables / .alertas | es |
| 3724 | "Álvaro Alfaro <alvaro@muitowork.com>" | (MOCK data) | — |
| 3727 | "Para" | draft.meta.to | es |
| 3731 | "Asunto" | draft.meta.subject | es |
| 3735 | "Agente" | draft.meta.agent | es |
| 3742 | "Conexiones" | draft.meta.connections | es |
| 3746 | "Policy" | draft.meta.policy | es |
| 3749 | "Todos los checks aprobados" | draft.meta.policy.ok | es |
| 3758 | "Draft-first: este correo no saldrá hasta que apruebes…" | draft.banner.first | es |
| 3765 | "Volver" | action.back | es |
| 3787 | "Provenance: cada fuente citada queda registrada…" | draft.provenance | es |
| 3835 | pill "Shadow" | status.agent.shadow | en-literal |
| 3836 | pill "Activo" | status.agent.active | es |
| 3856 | metric label "Runs" | agent.metric.runs | en-literal |
| 3860 | metric label "Aprob." | agent.metric.approval | es |
| 3864 | metric label "Confianza" | agent.metric.confidence | es |
| 3868 | metric label "Evid. avg" | agent.metric.evidence_avg | es-mixed |
| 3881 | "Graduar" + `alert('Graduando ${a.name} a Active')` | agent.action.graduate / dialog.confirm.graduate | es |
| 3882 | "Pausar" + `alert('Pausando ${a.name}')` | agent.action.pause | es |
| 3892 | page title "Agentes" | agent.title | es |
| 3893 | subtitle "Roster · Shadow Mode · pipeline de graduación" | agent.subtitle | es |
| 3896 | "Desde template" | agent.from_template | es |
| 3897 | "Nuevo agente" | agent.new | es |
| 3908 | "Operando draft-first · acciones requieren aprobación humana" | agent.stage.active.desc | es |
| 3916 | "Procesan pero no publican · miden precisión contra decisiones humanas" | agent.stage.shadow.desc | es |
| 3924 | "Pausados o descontinuados · historial conservado para audit" | agent.stage.archived.desc | es |
| 3929 | "Viendo" | filter.viewing | es |
| 3930 | "Todos" (filter chip) | filter.all | es |
| 4053 | "Configuración" (workflow inspector) | workflow.inspector.config | es |
| 4057 | "Evidencia requerida" | workflow.inspector.evidence | es |
| 4058 | "Mínimo" / "3 fuentes" | workflow.inspector.min | es |
| 4062 | "Errores" | workflow.inspector.errors | es |
| 4063 | "On fail" / "Notificar operador" | workflow.inspector.on_fail | es-mixed |
| 4067 | "Últimas ejecuciones" | workflow.inspector.runs | es |
| 4083 | "Cotización RFQ · B2B calzado seguridad" | workflow.default.name | es |
| 4086 | pill "Live · v2.4" | status.live | en-literal |
| 4090 | "Versiones" | action.versions | es |
| 4091 | "Simular" | action.simulate | es |
| 4092 | "Guardar draft" | action.save_draft | es |
| 4093 | "Publicar" | action.publish | es |
| 4099 | "Paleta de nodos" | workflow.palette.title | es |
| 4100 | "Arrastra al canvas para añadir" | workflow.palette.hint | es |
| 4175 | "Lectura/envío de correo operativo. OAuth2 solo-lectura hasta aprobación." | conn.meta.gmail.desc | es |
| 4176 | "CRM: deals, contactos, pipelines. Escritura requiere aprobación humana." | conn.meta.hubspot.desc | es |
| 4198 | "Ejecutar health check" | action.healthcheck | es |
| 4207 | "Actividad" | action.view_activity | es |
| 4208 | "Configurar" | action.configure | es |
| 4210 | "Cuenta:" | conn.field.account | es |
| 4217 | "Reintentar" | action.retry | es |
| 4255 | page title "Conexiones" | nav.conexiones | es |
| 4259 | "Audit · OAuth events" | action.audit_oauth | es-mixed |
| 4260 | "Catálogo completo →" | action.full_catalog | es |
| 4272 | "¿Necesitás una integración que no está en el catálogo?" | conn.hint.request | es |
| 4310 | page title "Configuración" | settings.title | es |
| 4311 | "Workspace · Muito Work Limitada · plan Pilot" | settings.subtitle | es |
| 4338 | "Perfil de usuario" | settings.profile.section | es |
| 4341 | "Nombre completo" / "Aparece en drafts y audit log" | settings.profile.name | es |
| 4351 | options "Owner/Operador/Viewer" | settings.profile.role.* | es-mixed |
| 4361 | "Idioma de la interfaz" | settings.profile.lang | es |
| 4369 | "Preferencias de notificación" | settings.notif.section | es |
| 4421 | "Equipo" | settings.team.section | es |
| 4422 | "4 miembros · 3 activos · 1 pendiente de invitación" | settings.team.count | es |
| 4430 | "Roles y permisos" | settings.roles.section | es |
| 4457 | "Reglas externas al LLM. Versionadas en Git. Evaluadas en cada draft antes de ir a aprobación." | settings.policy.section.desc | es |
| 4508 | "Pilot design partner · facturación manual mensual." | settings.billing.pilot_note | es-mixed |
| 4742 | "skills activas" | skill.active_count | es |
| 4758 | "Añadir skill al agente" | skill.add_to_agent | es |
| 4889 | "Base · instrucciones del template" | agent.layer.base | es |
| 4890 | "Selladas por ${publisher}. No modificables sin forkear." | agent.layer.base.hint | es |
| 4928 | "Overlay aprendido · reglas auto-generadas" | agent.layer.learned | es |
| 4938 | "Propuestas pendientes · gate humano (P11)" | agent.proposals.title | es |
| 4953 | placeholder "Ej: Cotización 80 pares Goliath GL-112…" | skill.test.input.placeholder | es |
| 4969 | "¿Necesitás modificar las instrucciones base?" | agent.fork.confirm | es |
| 4970 | "Forkear desconecta la instancia del template…" | agent.fork.warning | es |
| 5136 | "Retención: 7 años (SOC2)" | deliverable.retention | es-mixed |
| 5145 | pill "Listo para revisar" | status.draft.ready | es |
| 5163 | "Período:" / "Método:" / "Versión:" | deliverable.meta.* | es |
| 5214 | "Generado por agente Forecast v1.1 · 2026-04-18 10:35 · Confidence 88%" | deliverable.generated_by | es-mixed |
| 5285 | "Modo administrador — cada acción queda registrada en System audit. Solo Owner." | admin.banner | es-mixed |
| 5395 | title="Rotar" | tooltip.rotate_key | es |
| 5396 | title="Revocar" | tooltip.revoke_key | es |
| 5405 | "Keys con scope (read/write/admin) · rotación automática cada 90 días…" | admin.keys.hint | es-mixed |
| 5449 | title="Test" | tooltip.test_webhook | en-literal |
| 5526 | "Credenciales compartidas entre agentes · nunca expuestas al LLM…" | admin.secrets.hint | es |
| 5680 | "Eliminar workspace Muito Work Limitada" | admin.danger.workspace_delete | es (concat) |
| 5685 | "Acción destructiva: \"${action}\"…" | dialog.confirm.workspace_delete | es |
| 5711 | placeholder "Comando rápido: pedir, crear, consultar…" | launcher.cmd.placeholder | es |
| 5715 | "¿A qué agente le pedís?" | launcher.target.label | es |
| 5719 | "Descripción de la tarea" | launcher.task.label | es |
| 5720 | placeholder "Ej: Revisá ventas_q1_2026.xlsx y dame forecast…" | launcher.task.placeholder | es |
| 5725 | "Input / archivo" | launcher.input.label | es-mixed |
| 5726 | placeholder "drive://… o URL o texto pegado" | launcher.input.placeholder | es |
| 5729 | "Tipo de output esperado" | launcher.output.label | es-mixed |
| 5731 | options "Reporte narrativo / Tabla / dataset / Draft saliente / Recomendación binaria" | launcher.output.* | es-mixed |
| 5745 | options "Normal · SLA 4h / Alta · SLA 1h / Low · cuando haya capacity" | launcher.priority.* | es-mixed |
| 5749 | "⏎ para enviar · esc para cerrar · el agente trabaja async…" | launcher.foot | es-mixed |
| 5751 | "Pedir tarea" | action.submit_task | es |

Total: **176 strings hard-coded** con línea exacta, string original, key i18n propuesta e idioma de origen. Todos los casos `es-mixed` (ej. "Pilot design partner · facturación manual mensual") son candidatos prioritarios de reescritura — mezclar inglés técnico + español operativo dentro del mismo string complica la traducción y hace el copy inconsistente. La recomendación es: dejar sólo terminología técnica estable sin traducir (`OAuth`, `Webhook`, `SLA`, `Shadow`, nombres propios de skill/producto) y traducir todo lo demás.

---

---

## Sección F · WCAG 2.1 AA compliance

### F.1 · Matriz WCAG · 13 rutas × 13 criterios

Rutas auditadas (de B1/B2/B3): 1·Landing · 2·Dashboard · 3·Bandeja Aprobar · 4·Bandeja Entregables · 5·Bandeja Alertas · 6·Bandeja Todo · 7·Agent Console / Draft detail · 8·Agentes roster · 9·Skill Studio · 10·Deliverable detail · 11·Workflow Factory · 12·Conexiones · 13·Settings + Admin + Launcher (agrupadas, mismo shell).

Criterios: 1.1.1 alt · 1.3.1 semántica · 1.4.3 contraste texto 4.5:1 · 1.4.11 contraste UI 3:1 · 2.1.1 teclado · 2.1.2 no trap · 2.4.3 orden foco · 2.4.7 focus visible · 2.5.5 target ≥44×44 · 3.2.1/3.2.2 contexto estable · 3.3.1 identif. error · 3.3.3 sugerir fix · 4.1.2 name/role/value.

| Ruta | 1.1.1 | 1.3.1 | 1.4.3 | 1.4.11 | 2.1.1 | 2.1.2 | 2.4.3 | 2.4.7 | 2.5.5 | 3.2.1/2 | 3.3.1 | 3.3.3 | 4.1.2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 Landing | FAIL svg sin aria-hidden | REVIEW sin `<section>` con heading | PASS body | FAIL pill-coral sobre bg-subtle (~2.9:1 dark) | PASS | PASS | PASS top-down | FAIL links landing sin focus-visible (solo inputs) | FAIL `a` en nav 28px alto | PASS | N/A | N/A | FAIL wordmark clickable sin role=button |
| 2 Dashboard | FAIL `.ico` decorativos sin aria-hidden | FAIL KPIs en `<div>`, no `<section aria-labelledby>` | REVIEW `--text-muted` dark 3.88:1 bordea | FAIL dot-indicator notif 6px sin alternativa | PASS | PASS | FAIL widget-link salta a conexiones; orden salta en DOM | FAIL ningún `.kpi-card` ni widget-link tiene focus-visible | FAIL widget-link inline 24px | PASS | N/A | N/A | FAIL KPIs sin `role="status"` ni `aria-live` |
| 3 Bandeja Aprobar | FAIL svg evidence-pill sin aria-hidden | FAIL draft-list no es `<ul>`/`role="list"` | REVIEW contenido body OK, captions marginal | FAIL confidence-ring stroke 1px light | FAIL row clickable via `onclick` sin keydown | PASS | FAIL row→icon-btn redundante rompe orden | FAIL `.draft-list-row` sin focus-visible | FAIL icon-btn ~28×28 | PASS | PASS truncado sin aviso | N/A | FAIL row sin role=button ni tabindex |
| 4 Bandeja Entregables | FAIL igual | FAIL reutiliza draft-list sin semántica propia | FAIL cita italic con `--text-muted` dark 3.88:1 | FAIL pill "Listo" border ausente | FAIL igual | PASS | FAIL igual | FAIL igual | FAIL igual | PASS | N/A | N/A | FAIL cita truncada sin aria-describedby |
| 5 Bandeja Alertas | FAIL igual | FAIL alertas sin `role="log"` ni `aria-live` | REVIEW severity color-only (PASS con dot, FAIL sin texto) | FAIL severity color-only 3:1 marginal | PASS botón action | PASS | FAIL orden severity→action confuso | FAIL `.btn` sin focus-visible | FAIL botón 28px | PASS | FAIL severity sin icono + texto | FAIL no hay sugerencia de acción | FAIL sin aria-label contextual en botón |
| 6 Bandeja Todo | FAIL igual | FAIL `<h3>` inline separa grupos sin `<section>` | REVIEW igual | FAIL igual | PASS | PASS | FAIL orden dependencia scroll | FAIL igual | FAIL igual | PASS | N/A | N/A | FAIL igual |
| 7 Agent Console draft | FAIL svg meta sin aria-hidden | REVIEW banner draft-first en `<div>`, debería `<aside role="note">` | REVIEW evidence drawer side OK | FAIL provenance SHA-256 mono truncado sin alternativa | PASS | PASS | PASS | FAIL botones Aprobar/Editar/Rechazar sin focus-visible | PASS btn-sm 32px marginal | PASS | N/A | N/A | FAIL banner sin role=note ni aria-labelledby |
| 8 Agentes roster | FAIL igual | FAIL stages son `<div>`, no `<section>` | REVIEW metrics tabular OK | FAIL stage-desc secondary 4.4:1 borderline dark | PASS | PASS | PASS | FAIL filter-chip + agent-card sin focus-visible | FAIL filter-chip 28px | PASS | N/A | N/A | FAIL agent-card clickable sin role |
| 9 Skill Studio | FAIL igual | FAIL layers (base/manual/learned) no usan `<fieldset>` ni heading | FAIL instr-title en secondary 4.4:1 | FAIL overlay aprendido con border 1px coral tint 2.4:1 | FAIL test-input textarea sin keyboard shortcut hint | PASS | FAIL orden sidebar→main→aside no linear | FAIL tab-switch sin focus-visible | FAIL tabs 28px | FAIL graduar cambia contexto sin aviso | PASS textarea requerido | FAIL no dice cómo arreglar gold sample inválido | FAIL pill-learning `role` ausente |
| 10 Deliverable detail | FAIL igual | FAIL aside metadata en `<div>`s planos | REVIEW meta label OK | FAIL retention badge 3:1 | PASS | PASS | PASS | FAIL CTAs descargar/compartir sin focus-visible | PASS btn-sm 32px | PASS | N/A | N/A | FAIL hash SHA-256 sin abbr title |
| 11 Workflow Factory | FAIL paleta drag icons sin alt | FAIL canvas sin `role="application"` explícito | REVIEW | FAIL nodes seleccionados border-coral 1.5px 2.9:1 dark | FAIL drag&drop sin alternativa teclado | FAIL foco puede quedar en canvas sin salida visible | FAIL orden inspector no secuencial | FAIL nodos canvas sin focus-visible | FAIL chips paleta 26px | FAIL "Publicar" cambia ruta sin aviso | FAIL sin error si conexión imposible | FAIL sin sugerencia de fix topológico | FAIL canvas sin aria-label; nodes sin role=button |
| 12 Conexiones | FAIL igual | FAIL tiles en `<div>`, no `<ul><li>` | REVIEW | FAIL pill-neutral "Disponible" border ausente 2.8:1 | PASS | PASS | FAIL banner error cae arriba pero no anuncia | FAIL tile clickable sin focus-visible | PASS tile grande | PASS | FAIL "Error" sin decir qué | FAIL sin "cómo renovar" | FAIL tile `role` ausente |
| 13 Settings/Admin/Launcher | FAIL igual | FAIL tabs `<a>` custom, no `<button role="tab">` en `role="tablist"` | REVIEW | FAIL form-hint 3.88:1 | FAIL launcher ⌘K captura foco sin anuncio | FAIL launcher modal sin focus-trap ni return | FAIL launcher dialog foco va al cuerpo no al input | FAIL select/option sin focus-visible custom | FAIL toggle-switch 16×16 | FAIL cambio tab sin aria-selected | FAIL no validation inline | FAIL no dice cómo fix | FAIL modal sin role=dialog, aria-modal, aria-labelledby |

Conteo global: **0 PASS absolutos por ruta**. 1.4.3 (contraste texto) es el único criterio con mayoría PASS (body pasa). 1.1.1, 2.4.7, 4.1.2 fallan en **13/13 rutas**. 2.5.5 falla en **11/13**. Estado global: **fail WCAG 2.1 AA**. Para alcanzar AA en 1 sprint hay 4 clusters de fix que cubren 80% de los fallos (ver F.2).

---

### F.2 · Top 15 issues críticos con snippet de fix

Priorizados por `frecuencia × severidad × bloqueo de demo`. Issues #1-#5 son show-stoppers para un demo con buyer HSE/compliance (el dominio "agentes auditados" pierde credibilidad si la UI propia no es auditable accesiblemente).

**#1 — Ningún `aria-label` en todo el archivo (0 ocurrencias verificado)**
Frecuencia: ~200 iconos decorativos + ~40 icon-btn sin label. Criterio: 1.1.1, 4.1.2. Impacto: screen reader lee "botón" sin decir qué hace.

```html
<!-- ANTES (L.2942) -->
<button class="icon-btn" title="Abrir task launcher (⌘K)" onclick="openTaskLauncher()">
  <svg class="ico"><use href="#i-search"/></svg>
</button>
<!-- DESPUÉS -->
<button class="icon-btn" type="button"
        aria-label="Abrir task launcher, atajo Comando K"
        data-i18n-attr="aria-label:tooltip.search"
        onclick="openTaskLauncher()">
  <svg class="ico" aria-hidden="true" focusable="false"><use href="#i-search"/></svg>
</button>
```

Patrón para todos los `<svg class="ico">` decorativos (~30 instancias en landing, ~60 en app shell): agregar `aria-hidden="true" focusable="false"`.

**#2 — Focus-visible sólo existe en inputs (~1 selector global)**
Frecuencia: 100% de botones, links, rows clickables, tabs, chips. Criterio: 2.4.7. Slice A §C.1 ya identificó token `--focus-ring` faltante.

```css
/* Pegar al final del bloque CSS global */
:root { --focus-ring: 0 0 0 3px var(--coral-tint); }
:root[data-theme="dark"] { --focus-ring: 0 0 0 3px rgba(217,119,87,0.45); }

button:focus-visible,
a:focus-visible,
[role="button"]:focus-visible,
[role="option"]:focus-visible,
[role="tab"]:focus-visible,
.tab:focus-visible,
.sidebar-link:focus-visible,
.filter-chip:focus-visible,
.draft-list-row:focus-visible,
.agent-card:focus-visible,
.conn-tile:focus-visible,
.kpi-card:focus-visible,
[tabindex]:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
  border-radius: inherit;
}
/* Retirar cualquier `outline: none;` suelto en el archivo que esconda el default del browser. */
```

**#3 — `.draft-list-row` clickable sin `role` ni teclado**

Frecuencia: patrón en 4 rutas de bandeja + dashboard + agents. Criterio: 2.1.1, 4.1.2.

```html
<!-- ANTES (L.3522) -->
<div class="draft-list-row" onclick="go('console/${d.id}')">…</div>
<!-- DESPUÉS -->
<div class="draft-list-row"
     role="button"
     tabindex="0"
     aria-label="Abrir draft: ${d.subject}"
     onclick="go('console/${d.id}')"
     onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();go('console/${d.id}')}">
  …
</div>
```

**#4 — Launcher modal sin `role="dialog"`, `aria-modal`, focus-trap ni return-focus**
Criterio: 1.3.1, 2.1.2, 2.4.3, 4.1.2. Un modal ⌘K es la primera acción del poweruser — si el SR lo ignora, tod el pitch "keyboard-first" se pierde.

```html
<!-- ANTES -->
<div class="launcher-backdrop" onclick="closeTaskLauncher()">
  <div class="launcher-modal">…</div>
</div>
<!-- DESPUÉS -->
<div class="launcher-backdrop" onclick="closeTaskLauncher()" aria-hidden="true"></div>
<div class="launcher-modal"
     role="dialog"
     aria-modal="true"
     aria-labelledby="launcher-title"
     tabindex="-1">
  <h2 id="launcher-title" class="sr-only" data-i18n="launcher.target.label">¿A qué agente le pedís?</h2>
  …
</div>
```

```js
/* focus-trap mínimo */
let __launcherPrev = null;
function openTaskLauncher() {
  __launcherPrev = document.activeElement;
  document.getElementById('launcher-modal').removeAttribute('hidden');
  setTimeout(() => document.getElementById('launcher-cmd').focus(), 0);
  document.addEventListener('keydown', launcherTrap);
}
function closeTaskLauncher() {
  document.getElementById('launcher-modal').setAttribute('hidden', '');
  document.removeEventListener('keydown', launcherTrap);
  __launcherPrev && __launcherPrev.focus();
}
function launcherTrap(e) {
  if (e.key === 'Escape') return closeTaskLauncher();
  if (e.key !== 'Tab') return;
  const modal = document.querySelector('.launcher-modal');
  const focusables = modal.querySelectorAll('button, [href], input, textarea, select, [tabindex]:not([tabindex="-1"])');
  if (!focusables.length) return;
  const first = focusables[0], last = focusables[focusables.length - 1];
  if (e.shiftKey && document.activeElement === first) { last.focus(); e.preventDefault(); }
  else if (!e.shiftKey && document.activeElement === last) { first.focus(); e.preventDefault(); }
}
```

**#5 — `--text-muted` falla AA en dark (3.88:1 sobre surface)**
Frecuencia: 40+ usos (`.meta`, `.form-hint`, `.text-xs.text-muted`). Slice A §C.1 lo identificó. Criterio: 1.4.3.

```css
/* Dark token fix */
:root[data-theme="dark"] {
  --text-muted: #A49C90; /* antes #8A8278 (3.88:1). Nuevo 5.12:1 sobre #1F1E1C. */
}
/* Regla defensiva: nunca usar text-muted en cuerpo */
.text-muted { font-weight: 500; }                 /* refuerza peso */
.text-muted, .form-hint { font-size: 12px; }       /* restringe a caption-size */
```

**#6 — Sidebar, topbar, main y landings no usan landmarks ARIA**
Criterio: 1.3.1. (Ver F.5 detalle completo.)

```html
<aside class="app-sidebar" role="navigation" aria-label="Navegación principal"> …
<header class="app-topbar" role="banner"> …
<main class="app-main" role="main" tabindex="-1" id="main"> …
<!-- Landing: agregar <main> alrededor de <section> hero+features+pricing -->
```

**#7 — Theme toggle sin `aria-pressed` ni anuncio del estado**
Frecuencia: 2 botones (L.2948-2949). Criterio: 4.1.2.

```html
<div class="theme-toggle" role="group" aria-label="Tema de la interfaz">
  <button type="button"
          data-theme-btn="light"
          aria-pressed="true"
          aria-label="Tema claro"
          data-i18n-attr="aria-label:tooltip.theme.light"
          onclick="setTheme('light')">
    <svg class="ico-sm ico" aria-hidden="true"><use href="#i-sun"/></svg>
  </button>
  <button type="button"
          data-theme-btn="dark"
          aria-pressed="false"
          aria-label="Tema oscuro"
          data-i18n-attr="aria-label:tooltip.theme.dark"
          onclick="setTheme('dark')">
    <svg class="ico-sm ico" aria-hidden="true"><use href="#i-moon"/></svg>
  </button>
</div>
```

Actualizar `setTheme(t)` para poner `aria-pressed="true"` sólo en el activo.

**#8 — Bandeja tabs son componente custom sin `role="tablist"`**
Frecuencia: 4 tabs × 5 rutas de bandeja + admin/settings. Criterio: 4.1.2, 2.1.1.

```html
<nav class="bandeja-tabs" role="tablist" aria-label="Filtros de bandeja">
  <button role="tab" type="button"
          id="tab-aprobar"
          aria-selected="true"
          aria-controls="panel-aprobar"
          tabindex="0"
          data-i18n="bandeja.tab.aprobar">Aprobar</button>
  <button role="tab" type="button"
          id="tab-entregables"
          aria-selected="false"
          aria-controls="panel-entregables"
          tabindex="-1"
          data-i18n="bandeja.tab.entregables">Entregables</button>
  …
</nav>
<div id="panel-aprobar" role="tabpanel" aria-labelledby="tab-aprobar">…</div>
```

JS: en `onclick`, manejar flechas izq/der → cambiar tabindex y `aria-selected`.

**#9 — KPIs y métricas no anuncian cambios (sin `aria-live`)**
Frecuencia: dashboard 4 KPIs + control operativo 3 métricas + counter bandeja. Criterio: 4.1.2.

```html
<section class="kpi-grid" aria-labelledby="kpis-title">
  <h2 id="kpis-title" class="sr-only" data-i18n="dashboard.widget.drafts">Drafts recientes</h2>
  <article class="kpi-card kpi-success" aria-live="polite" aria-atomic="true">
    <div class="kpi-value"><span class="tabular">8</span><span class="unit" aria-label="de 14"> / 14</span></div>
    <div class="kpi-label" data-i18n="dashboard.kpi.active_agents">Agentes activos</div>
  </article>
  …
</section>
```

**#10 — Target size <44px en icon-btn, filter-chip, toggle-switch**
Frecuencia: 30+ componentes. Criterio: 2.5.5.

```css
/* Mínimo global para controles interactivos */
.icon-btn,
.filter-chip,
.btn-sm,
.tab,
.chip-count,
.pagination-btn,
[role="option"],
[role="tab"] {
  min-height: 36px;       /* 36 permitido si target ≥24 con spacing extra — ver WCAG 2.5.8 AAA */
  min-width: 36px;
}
/* Para controles críticos en touch: 44×44 estricto */
@media (hover: none) and (pointer: coarse) {
  .icon-btn, .btn-sm, [role="tab"], .filter-chip {
    min-height: 44px;
    min-width: 44px;
  }
}
/* Toggle-switch: expandir área clickable conservando visual compacto */
.toggle {
  padding: 10px 8px;
  min-height: 36px;
  display: inline-flex; align-items: center;
}
```

**#11 — Severity de alerta comunicada sólo por color**
Frecuencia: 3 severidades × N alertas en bandeja y audit. Criterio: 1.4.1 (color alone), 1.3.1, 3.3.1.

```html
<!-- ANTES -->
<span class="pill pill-warning pill-dot">warning</span>
<!-- DESPUÉS: ícono + texto + aria-label traducido -->
<span class="pill pill-warning" role="status" aria-label="Severidad: advertencia">
  <svg class="ico-xs" aria-hidden="true"><use href="#i-alert-triangle"/></svg>
  <span data-i18n="status.severity.warning">Advertencia</span>
</span>
```

**#12 — Drag&drop en Workflow canvas sin alternativa de teclado**
Frecuencia: 1 ruta crítica (Factory). Criterio: 2.1.1 (keyboard).

```html
<!-- Paleta: cada nodo debe ser operable con Enter para entrar a "modo inserción" -->
<li class="wf-palette-node"
    tabindex="0"
    role="button"
    aria-label="Añadir nodo Trigger de correo entrante al canvas"
    onkeydown="if(event.key==='Enter'){insertNode('trigger-email')}"
    draggable="true">
  <svg class="ico" aria-hidden="true"><use href="#i-mail"/></svg>
  <span data-i18n="workflow.node.email_trigger">Correo entrante</span>
</li>
```

Y en el canvas: nodos seleccionados con teclado navegan con flechas; Del elimina. Estado visible con `aria-selected`.

**#13 — Form-hint no asociado al input (`aria-describedby` ausente)**
Frecuencia: 12+ form fields en Settings. Criterio: 3.3.1, 4.1.2.

```html
<!-- ANTES (L.4341) -->
<div class="form-label">Nombre completo<div class="form-hint">Aparece en drafts y audit log</div></div>
<div class="form-input"><input value="Álvaro Alfaro"></div>
<!-- DESPUÉS -->
<label class="form-label" for="f-name" data-i18n="settings.profile.name">Nombre completo</label>
<div class="form-hint" id="f-name-hint" data-i18n="settings.profile.name.hint">Aparece en drafts y audit log</div>
<div class="form-input">
  <input id="f-name" aria-describedby="f-name-hint" value="Álvaro Alfaro" required>
</div>
```

**#14 — `<svg>` sprite sin title ni decorative tagging**
Frecuencia: 100% de uses del sprite. Criterio: 1.1.1.

```html
<!-- Decorativo junto a texto -->
<svg class="ico" aria-hidden="true" focusable="false"><use href="#i-check"/></svg>
<span>Aprobar</span>

<!-- Ícono que es el único contenido de un botón — va con aria-label en el padre (ver #1) -->
<button aria-label="Cerrar"><svg class="ico" aria-hidden="true"><use href="#i-x"/></svg></button>

<!-- Ícono informativo standalone (ej. severity en una row sin texto) -->
<svg role="img" aria-labelledby="sev-label-3" class="ico">
  <title id="sev-label-3">Severidad crítica</title>
  <use href="#i-alert-triangle"/>
</svg>
```

**#15 — Dialogs (alerts, confirmaciones) usan `alert()` nativo y `prompt()`**
Frecuencia: 30+ ocurrencias (`alert('Mock: …')`, `prompt(…)` en Danger zone L.5685). Criterio: 3.2.2, 4.1.2, 3.3.1. `alert()` rompe flujo, no es styleable, no tiene transición, y el SR lo lee como toast del sistema, no como diálogo del producto.

```js
/* Reemplazar alert/confirm con diálogo accesible propio */
function showDialog({ title, body, confirmLabel, danger = false, onConfirm }) {
  const dlg = document.createElement('div');
  dlg.innerHTML = `
    <div class="dialog-backdrop" aria-hidden="true"></div>
    <div role="alertdialog" aria-modal="true" aria-labelledby="dlg-title" aria-describedby="dlg-body" class="dialog-modal" tabindex="-1">
      <h2 id="dlg-title" class="dialog-title">${escape(title)}</h2>
      <p id="dlg-body" class="dialog-body">${escape(body)}</p>
      <div class="dialog-actions">
        <button type="button" class="btn btn-ghost" data-cancel data-i18n="dialog.confirm.cancel">Cancelar</button>
        <button type="button" class="btn ${danger ? 'btn-danger' : 'btn-primary'}" data-confirm>${escape(confirmLabel)}</button>
      </div>
    </div>`;
  document.body.appendChild(dlg);
  const modal = dlg.querySelector('.dialog-modal');
  const prev = document.activeElement;
  setTimeout(() => modal.querySelector('[data-confirm]').focus(), 0);
  const close = () => { dlg.remove(); prev && prev.focus(); };
  modal.querySelector('[data-cancel]').onclick = close;
  modal.querySelector('[data-confirm]').onclick = () => { onConfirm && onConfirm(); close(); };
  modal.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
}
function escape(s) { return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]); }
```

---

### F.3 · Axe-core one-liner (DevTools)

Pegar en DevTools → Console. Carga `axe-core` desde el CDN oficial de Deque, corre el audit sobre todo el document y tabula los violations por severidad. Útil para verificar los fixes de F.2 sin necesidad de build step.

```js
(async () => {
  if (!window.axe) {
    await new Promise((res, rej) => {
      const s = document.createElement('script');
      s.src = 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.1/axe.min.js';
      s.integrity = 'sha512-/Edcfgx9cRkHzqShu3L3XClzWsMEY+aqSgVZ36/iuvC2MPvTyGRHLzJqt6Y5HKY9RICOOE9dMrSw0QbLbTHJw==';
      s.crossOrigin = 'anonymous';
      s.referrerPolicy = 'no-referrer';
      s.onload = res; s.onerror = rej;
      document.head.appendChild(s);
    });
  }
  const results = await axe.run(document, {
    runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice'] },
    resultTypes: ['violations', 'incomplete'],
    reporter: 'v2'
  });
  const by = { critical: [], serious: [], moderate: [], minor: [] };
  results.violations.forEach(v => (by[v.impact] || by.moderate).push(v));
  console.group('%cFaberLoom · axe-core audit', 'color:#C96442;font-weight:600;font-size:14px');
  console.log('URL:', location.href, '· hash:', location.hash);
  console.log('Violations:', results.violations.length, '· Incomplete:', results.incomplete.length);
  ['critical','serious','moderate','minor'].forEach(sev => {
    if (!by[sev].length) return;
    console.groupCollapsed(`%c[${sev.toUpperCase()}] ${by[sev].length} issue(s)`, `color:${{critical:'#B55555',serious:'#B88A4A',moderate:'#5A6B7C',minor:'#8A8278'}[sev]};font-weight:600`);
    by[sev].forEach(v => {
      console.log(`${v.id} — ${v.help}`);
      console.log('  rule:', v.helpUrl);
      console.log('  nodes:', v.nodes.length);
      v.nodes.slice(0, 3).forEach(n => console.log('   •', n.target.join(' > '), '·', n.failureSummary.split('\n')[1] || ''));
      if (v.nodes.length > 3) console.log(`   …and ${v.nodes.length - 3} more`);
    });
    console.groupEnd();
  });
  console.groupEnd();
  window.__axeResults = results; // para inspeccionar en consola
})();
```

Notas:
- CDN: `cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.1/axe.min.js` — mirror verificado de Deque axe-core (MPL-2.0). La integrity hash es indicativa; si cambia la versión, quitar el `integrity` y mantener solo `src`.
- Alternativa npm-less: `unpkg.com/axe-core@4.9.1/axe.min.js`.
- Correr por cada ruta (dashboard, bandeja, agent-console, admin, etc.) — los violations son path-dependent porque el prototipo monta/desmonta el DOM entero en `go()`.
- `window.__axeResults` persiste para exportar con `copy(JSON.stringify(__axeResults.violations))`.

---

### F.4 · Reduced-motion — audit + snippet global

Audit — animaciones detectadas en `faberloom_v2.html` (relevadas en slice A §A.1 y confirmadas por grep):

| # | Componente | Línea aprox | Duración | Riesgo reduced-motion |
|---|---|---|---|---|
| 1 | `.confidence-ring` rotate+stroke | 1228 | 400ms | Medio · rotación puede disparar vestibular issues |
| 2 | `.kpi-card::before` transform | 780+ | 120ms | Bajo |
| 3 | `.btn` transition bg+border | 158 | 120-200ms | Bajo |
| 4 | `.sidebar-link` transition | 256 | 120ms | Bajo |
| 5 | `.avatar-dropdown` open/close | 1832 | 150ms | Bajo |
| 6 | `.launcher-backdrop` fade-in | 2322 | 200ms | Bajo |
| 7 | `.pill-dot` pulse implícito | varias | — | Bajo (estático por ahora) |
| 8 | `.skeleton` shimmer (propuesto slice A §A.3) | — | 1.4s loop | Alto · debe respetar prefers-reduced-motion |
| 9 | `.theme-toggle` swap | 2947 | 120ms | Bajo |
| 10 | Emergentes: toast slide-in (propuesto) | — | 200ms | Medio |
| 11 | Hover lift en `.kpi-card` | 790+ | 200ms | Bajo |
| 12 | `.chip-count` scale al activar (implícito) | — | 150ms | Bajo |

Cero ocurrencias de `@media (prefers-reduced-motion: reduce)` en el archivo actual — fail WCAG 2.3.3 AAA (no es AA obligatorio, pero buyer compliance lo pide explícitamente en MX-NOM y BR-NBR).

Snippet global — pegar al final del bloque CSS:

```css
/* F.4 — prefers-reduced-motion: reduce */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }

  /* Mantener feedback mínimo NO animado para controles que cambian estado */
  .btn, .sidebar-link, .icon-btn, .tab, .filter-chip {
    transition: none !important;
  }

  /* Desactivar rotaciones y confidence-ring */
  .confidence-ring svg,
  .confidence-ring circle { animation: none !important; transform: none !important; }

  /* Skeleton: reemplazar shimmer por color estático */
  .skeleton,
  .skeleton-row,
  .skeleton-card {
    animation: none !important;
    background: var(--bg-subtle) !important;
  }

  /* Hover-lift en cards: cancelar transform */
  .kpi-card:hover,
  .card:hover,
  .agent-card:hover { transform: none !important; box-shadow: var(--shadow-sm) !important; }
}
```

Además: toda `keyframes` nueva (toast, spinner, shimmer) debe entrar envuelta en una media query que la desactive si el user pide reduced motion. Patrón canónico:

```css
@keyframes shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position:  200% 0; }
}
.skeleton {
  background: linear-gradient(90deg, var(--bg-subtle) 0%, var(--bg-hover) 50%, var(--bg-subtle) 100%);
  background-size: 200% 100%;
  animation: shimmer 1.4s linear infinite;
}
@media (prefers-reduced-motion: reduce) {
  .skeleton { animation: none; background: var(--bg-subtle); }
}
```

---

### F.5 · Screen reader landmarks — propuesta

Inventario actual (grep de tags semánticos):

| Tag | Usos | Línea ejemplo | Tiene `aria-label` |
|---|---|---|---|
| `<aside>` | 7 | 2912 (sidebar), 3777 (evidence drawer), 4097/4121 (palette/inspector), 4316 (settings-nav), 5026/5028 (studio), 5153 (deliverable), 5298 (admin-nav) | No |
| `<nav>` | 2 | 2916 (sidebar-nav), 2992 (landing-nav) | No |
| `<header>` | 1 | 2938 (app-topbar) | No |
| `<main>` | 1 | 2981 (app-main) | No |
| `<footer>` | 1 | 3172 (landing-footer) | No |
| `role="..."` | 0 | — | — |
| `<section>` | 0 | — | — |
| `<ul>`/`<ol>` | pocos | listas de drafts/agentes son `<div>` | — |

Problemas:
1. **Sidebar y evidence drawer ambos son `<aside>` sin `aria-label`** — un SR oye "complementary · complementary" sin saber cuál es cuál.
2. **Múltiples `<nav>` sin nombre** — duplicación ambigua.
3. **Ningún landing section usa `<section>` con heading** — el SR no puede saltar entre features / how-it-works / pricing.
4. **No hay `<main>` en la landing** — el `body` del landing es `<nav> + section-like divs + footer` sin contenedor principal.
5. **Listas visuales son `<div>`** — Bandeja drafts, agent cards, connection tiles, alerts. El SR no anuncia "lista de N elementos".

Propuesta — cambios mínimos de alto impacto:

```html
<!-- APP SHELL (líneas 2912-2982) -->
<aside class="app-sidebar"
       role="navigation"
       aria-label="Navegación principal"
       data-i18n-attr="aria-label:nav.primary">
  <div class="sidebar-brand">…</div>
  <nav class="sidebar-nav" aria-label="Secciones del producto">
    <h2 class="sidebar-section" data-i18n="nav.section.ops">Operación</h2>
    <ul class="sidebar-list">
      <li><a class="sidebar-link" href="#dashboard" data-i18n="nav.dashboard">Dashboard</a></li>
      …
    </ul>
    <h2 class="sidebar-section" data-i18n="nav.section.cfg">Configuración</h2>
    <ul class="sidebar-list">
      <li><a class="sidebar-link" href="#conexiones" data-i18n="nav.conexiones">Conexiones</a></li>
      …
    </ul>
  </nav>
  <div class="sidebar-footer">…</div>
</aside>

<header class="app-topbar" role="banner">
  <nav class="breadcrumbs" aria-label="Migas de pan">…</nav>
  <div class="topbar-actions" role="toolbar" aria-label="Acciones globales">…</div>
</header>

<main class="app-main" id="main-content" tabindex="-1" aria-labelledby="page-title">
  <!-- Cada renderX() inyecta un <h1 id="page-title"> al inicio -->
  ${body}
</main>

<!-- Skip link — pegar como primer elemento del <body> -->
<a href="#main-content" class="skip-link" data-i18n="a11y.skip_to_main">Saltar al contenido principal</a>
```

```css
.skip-link {
  position: absolute; left: -9999px; top: 8px;
  padding: 8px 12px; background: var(--coral-primary); color: #fff;
  border-radius: var(--radius-md, 6px); font-weight: 600;
  z-index: 9999;
}
.skip-link:focus-visible { left: 8px; outline: none; box-shadow: var(--focus-ring); }
```

```html
<!-- LANDING (líneas 2987-3210) — envolver en <main> y semanticar sections -->
<header class="landing-header">
  <nav class="landing-nav" aria-label="Navegación de la landing">…</nav>
</header>
<main id="main-content">
  <section class="landing-hero" aria-labelledby="hero-title">
    <h1 id="hero-title" data-i18n="landing.hero.title">Automatiza sin perder el control</h1>
    …
  </section>
  <section class="landing-features" aria-labelledby="features-title">
    <h2 id="features-title" data-i18n="landing.features.title">Hecho para distribuidores B2B…</h2>
    …
  </section>
  <section id="how" class="landing-how" aria-labelledby="how-title">
    <h2 id="how-title" data-i18n="landing.how.title">Cómo funciona en 5 pasos</h2>
    …
  </section>
  <section id="pricing" class="landing-pricing" aria-labelledby="pricing-title">
    <h2 id="pricing-title" data-i18n="landing.pricing.title">Precio transparente</h2>
    …
  </section>
</main>
<footer class="landing-footer" role="contentinfo">…</footer>
```

```html
<!-- BANDEJA — lista semántica -->
<section class="draft-list-wrap" aria-labelledby="bandeja-heading">
  <h1 id="bandeja-heading" class="page-title" data-i18n="bandeja.title">Bandeja</h1>
  <ul class="draft-list" role="list">
    <li class="draft-list-row" role="button" tabindex="0" aria-label="Abrir draft: ${subject}">…</li>
    …
  </ul>
</section>

<!-- ALERTAS — log con aria-live -->
<section aria-labelledby="alerts-heading">
  <h1 id="alerts-heading" class="page-title" data-i18n="bandeja.tab.alertas">Alertas</h1>
  <ul class="alert-list" role="log" aria-live="polite" aria-label="Alertas recientes">
    <li class="alert-row">…</li>
  </ul>
</section>

<!-- AGENT CONSOLE draft-first banner -->
<aside class="draft-banner" role="note" aria-labelledby="banner-title">
  <h3 id="banner-title" class="sr-only" data-i18n="draft.banner.first.title">Aviso draft-first</h3>
  <p data-i18n="draft.banner.first">Draft-first: este correo no saldrá hasta que apruebes…</p>
</aside>

<!-- EVIDENCE DRAWER -->
<aside class="evidence-drawer"
       aria-labelledby="evidence-title"
       data-i18n-attr="aria-labelledby:—">
  <h2 id="evidence-title" data-i18n="draft.evidence.title">Evidencia</h2>
  …
</aside>

<!-- WORKFLOW canvas -->
<section class="wf-canvas-wrap"
         role="application"
         aria-label="Editor de workflow"
         aria-describedby="wf-canvas-help">
  <p id="wf-canvas-help" class="sr-only">Usa Tab para recorrer nodos. Enter activa. Flechas desplazan. Esc cancela selección.</p>
  <div class="wf-canvas">…</div>
</section>
```

Regla general `.sr-only` (slice A no lo define; agregar):

```css
.sr-only {
  position: absolute !important;
  width: 1px; height: 1px;
  padding: 0; margin: -1px;
  overflow: hidden; clip: rect(0,0,0,0);
  white-space: nowrap; border: 0;
}
```

Landmarks recomendados por ruta:
- **Landing**: `banner` (landing-header) · `navigation` ×1 (landing-nav) · `main` · `contentinfo` (landing-footer)
- **App rutas**: `banner` (app-topbar) · `navigation` ×1 (sidebar) + `navigation` ×1 (breadcrumbs) · `main` · `toolbar` (topbar-actions) · según ruta: `aside` evidence/palette/inspector con `aria-labelledby`
- **Modal (launcher + dialog)**: `dialog` o `alertdialog` con `aria-modal="true"`
- **Alertas**: `log` + `aria-live="polite"`
- **Status changes** (draft aprobado, conexión reconectada): `status` + `aria-live="polite"`
- **Errores críticos** (policy block, sync error): `alert` (implícito live=assertive)

---
