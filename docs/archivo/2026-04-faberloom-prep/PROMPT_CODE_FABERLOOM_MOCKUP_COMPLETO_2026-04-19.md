# PROMPT · Claude Code — FaberLoom Standalone HTML Completo

> **Para:** Claude Code (sesión nueva en `/MWT KB/`)
> **Autor:** Álvaro · CEO Muito Work · 2026-04-19
> **Objetivo:** extender `faberloom-mockup/index-standalone.html` (hoy 1482 líneas, 4 rutas) hasta **un único archivo HTML** que cubre toda la funcionalidad conversada y abre con doble clic (`file://`). Cero servidor, cero ESM, cero dependencias salvo Google Fonts CDN + axe-core CDN opcional.
> **Paralelización:** sub-agentes producen **fragmentos de texto** (HTML/CSS/JS/JSON). Thread principal ensambla el archivo único con Edits.
> **Idioma:** ES default + EN + PT-BR switch persistente.

---

## 0 · Contexto en 8 líneas (no re-explicar)

- **FaberLoom** = control-plane de agentes IA para SMB LatAm. Control plane > category theater.
- **Wedge v1:** cotización B2B calzado seguridad industrial (Marluvas/Tecmater MX/CO/CR).
- **Promesa:** draft-first absoluto + evidencia visible + autonomía evidence-gated.
- **Personas:** Owner (CEO SMB) · Admin (técnico/partner) · Operator (despacha drafts).
- **Design partners:** 3 (2 gratis + 1 pago). El HTML lo llevás a ellos como proof.
- **NO toca KB MWT.** No escribe pgvector. No llama a Claude. Solo visualiza.
- **Brand:** Georgia italic + Inter + JetBrains Mono · Coral #C96442 · Cream #F4F1ED · Warm-dark #1F1E1C · Evidence #6E1F2B.
- **Restricción dura:** TODO va en `index-standalone.html`. Un archivo. Doble clic funciona.

---

## 1 · Inputs obligatorios (leer ANTES de escribir código)

En paralelo con `Read`:

1. `/MWT KB/docs/SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` (968 líneas) — 20 tablas FROZEN, UUIDv7, RLS, scheduler, outbox, memory_chunk. **Fuente de verdad técnica.**
2. `/MWT KB/docs/SPEC_USER_ADMIN_KNOWLEDGE_FLOW_v1_BETA.md` — 4 scopes, 3 roles, OIDC+manual.
3. `/MWT KB/docs/SPEC_FABERLOOM_MVP.md` — alcance MVP.
4. `/MWT KB/docs/ARCH_AGENT_PRINCIPLES.md` — los 13 principios P1–P13.
5. `/MWT KB/PROMPT_DESIGN_FABERLOOM_MOCKUP_FULL_2026-04-19.md` — inventario visual canónico.
6. `/MWT KB/faberloom-mockup/index-standalone.html` — **base a extender, 1482 líneas**. Ya tiene: tokens light/dark, shell, router hash, 4 módulos (bandeja-detail, skill-studio, agent-console, workflows), widgets base, i18n ~120 keys, mock data básica.
7. Memorias `/.auto-memory/project_faberloom*.md` (7 archivos) + `feedback_faberloom_prototype.md`.

**Precedencia:** SPEC blueprint > PROMPT_DESIGN > standalone actual > memorias.

---

## 2 · Restricciones duras del standalone

| # | Restricción | Por qué |
|---|---|---|
| 1 | **1 solo archivo** `index-standalone.html` | Álvaro abre con doble clic; lo comparte por WhatsApp a design partner |
| 2 | **Sin ESM, sin `import`, sin `fetch`** | `file://` bloquea CORS |
| 3 | **Sin build, sin Tailwind, sin React** | Vanilla JS + CSS |
| 4 | **Mock data inline** como variable JS global `const MOCK = {...}` | Sin carga asíncrona |
| 5 | **Fuentes desde Google Fonts CDN** permitido (link ya está) | Georgia es system font |
| 6 | **axe-core CDN opcional** — botón "Validar a11y" lo carga lazy con `<script src>` al hacer click | Sin dependencia obligatoria |
| 7 | **i18n via diccionario JS inline** — 3 idiomas × 332+ keys | Sin fetch de JSON |
| 8 | **SVG inline** para iconos (lucide set) y charts | Sin imágenes externas |
| 9 | **LocalStorage permitido** para theme/lang/tenant/role persistence | Navegador moderno cualquiera |
| 10 | **Tamaño objetivo:** 8000–14000 líneas | Razonable para 1 HTML, abre rápido |

**NO valer:**
- `<link rel="stylesheet" href="./...">` → todo CSS inline en `<style>`.
- `<script src="./...">` → todo JS inline en `<script>`.
- `localStorage.getItem` sin fallback a memoria → algunos browsers con `file://` pueden bloquear; envolver.

---

## 3 · Arquitectura de ejecución — sub-agentes paralelos → ensamblaje

Usá `Agent` tool con `subagent_type: "general-purpose"`. Enviá los 3 batches **cada uno en un solo mensaje** con los tool calls en paralelo.

### Fase 1 · Research (Batch A · 3 sub-agentes)

| Sub-agente | Output | Formato |
|---|---|---|
| A1 · spec-brief | Brief 2000 palabras con 20 tablas resumidas, scopes RLS, state machine 9 estados, autonomy L0-L4 + criterio textual, provenance schema, action-risk registry, workflow state ledger, consolidation pipeline | markdown → `/tmp/fl_brief.md` |
| A2 · gap-audit | Matriz "está vs falta" contra 13 rutas + 3 overlays + 10 widgets + 332 keys i18n sobre el standalone actual (1482 líneas). Output tabla con columnas: ruta/widget, estado actual (stub/parcial/completo/inexistente), qué agregar | markdown → `/tmp/fl_gap.md` |
| A3 · data-seed | Genera `MOCK` JS object completo con: 3 tenants (Marluvas MX, Tecmater CO, Distribuidor CR), 5 usuarios × 3 roles, 7 departamentos, 3 business_entities, 6 agentes con Spec/Runtime/Memory, 14 drafts con provenance (6 claims en dr_001), 50+ runs con state ledger, 20 gold samples, 7 consolidaciones (1 hot), 300+ audit events, 12 action-risk entries, 40 feedbacks tipificados | JS válido → `/tmp/fl_mock.js` |

### Fase 2 · Fragmentos (Batch B · 9 sub-agentes paralelos)

Cada uno recibe: brief A1 + gap A2 + seed A3 + tokens del standalone actual + el contrato de módulo del §4. **Output = string JavaScript** con funciones `mount(slot, ctx)` y `unmount()` + CSS scoped con prefijo `.m-{id}-*`.

| # | Sub-agente | Entrega | Acceptance |
|---|---|---|---|
| B1 | landing | ~200 líneas | Hero Georgia 56 + 3 value cards + CTA único + dot-grid 6% |
| B2 | dashboard | ~350 líneas | 4 KPI cards + tabla "requieren atención" (5 rows) + "próximo unlock" + timeline editorial 8 items |
| B3 | bandeja-list | ~300 líneas | Filtros sticky + 14 items con action-risk badge + empty state |
| B4 | agentes-list | ~350 líneas | Tabla sticky 6 agentes con autonomy stepper L0-L4, KPIs 7d, próximo unlock textual |
| B5 | conexiones | ~250 líneas | Grid 4 cols con 8 conectores + estados + OAuth flow stub |
| B6 | settings | ~300 líneas | 2 cols nav + form (6 secciones: Perfil/Notif/Idioma/Tema/Atajos/Privacidad) |
| B7 | admin | ~800 líneas | 3 grupos × 10 tabs (Personas: Usuarios/Roles/Invitaciones · Operación: Policies/Aprobaciones/SLAs · Plataforma: KB/Conectores/Auditoría/Billing) + breadcrumb sticky |
| B8 | admin-autonomy | ~400 líneas | Selector agente + curva aprobación SVG line 90d + donut correcciones + tabla "tipos que fallan" + CTA promover disabled con tooltip |
| B9 | factory | ~300 líneas | Wizard 3 pasos (plantilla → config → confirmación) + stepper sticky + default L0 Shadow |

### Fase 3 · Widgets arquitectónicos (Batch C · 5 sub-agentes paralelos)

| # | Sub-agente | Entrega | Acceptance |
|---|---|---|---|
| C1 | launcher-overlay ⌘K | ~200 líneas | `role="dialog"` + focus trap + Esc cierra + input 18px + keyboard nav + grupos (Acciones/Agentes/Drafts/Conexiones/KB) |
| C2 | feedback-modal | ~150 líneas | 5 razones tipificadas (claim sin evidencia/tono/dato/acción riesgosa/otro) con íconos + checkboxes + textarea + emit `bus('feedback:submit')` |
| C3 | consolidation-modal | ~250 líneas | 4 secciones (learned/applies/impact/confirm) + eje 3D tipo×alcance×cross-skill con checkboxes por skill + header 🔴 badge + contador patrones |
| C4 | schema-explorer | ~400 líneas | 20 tablas agrupadas por módulo (Identity/Bus/Audit/Scheduler/Agents/Memory/Drafting/Connectors) + click tabla → panel derecho con DDL JetBrains Mono + policy RLS text + SET LOCAL ejemplo |
| C5 | workflow-ledger + provenance-tree | ~300 líneas | Timeline SVG del run con pasos/estados/approvals/errores/costo + árbol provenance visible en bandeja-detail panel Provenance tab (cross-link con highlight) |

### Fase 4 · Ensamblaje (thread principal)

1. **Leer** estado actual del standalone (1482 líneas) para saber dónde insertar.
2. **Editar** el archivo con secciones marcadas por bloques comentados:
   ```
   /* ==================== TOKENS EXTENDIDOS ==================== */
   /* ==================== WIDGETS v2 ==================== */
   /* ==================== MÓDULOS · LANDING ==================== */
   ...
   ```
3. **Inyectar** mock data ampliada reemplazando la variable `MOCK` existente.
4. **Inyectar** i18n ampliado (3 × 332+ keys).
5. **Extender** sidebar NAV de 8 → 13 items + topbar con tenant/role switcher.
6. **Extender** router para las 13 rutas + overlays.
7. **Validar** con Node `--check` el JS extraído y axe-core runtime en las rutas clave.

### Fase 5 · Verificación (thread principal)

- `node --check` sobre JS extraído en `/tmp/fl_extracted.js`.
- Smoke manual: abrir el HTML en file:// y verificar que cada ruta monta.
- Conteo de líneas final (`wc -l`) debe estar entre 8000 y 14000.
- axe-core violations críticas en bandeja-detail/dashboard/admin: 0.

---

## 4 · Contrato de módulo dentro del HTML único

Cada módulo se registra en un `const MODULES = {}` global:

```js
MODULES.landing = {
  meta: { id: 'landing', route: '#/', i18nDomain: 'landing',
          needsTenant: false, needsRole: ['Owner','Admin','Operator'] },
  mount(slot, ctx) {
    // ctx = { params, query, navigate, bus, store, i18n, data, tenant, role }
    slot.innerHTML = `
      <section class="m-landing" data-i18n-scope="landing">
        <h1 class="t-display-xl" data-i18n="landing.hero.title"></h1>
        ...
      </section>`;
    ctx.i18n.apply(slot);
    // listeners
    const cleanup = () => { /* remove listeners */ };
    return { unmount: cleanup };
  }
};
```

**Reglas del contrato:**

1. Sin imports entre módulos. Comunicación vía `bus.emit/on`.
2. Estado compartido solo vía `store` versionado (`faberloom.v1.*`), con fallback a memoria si localStorage falla.
3. CSS scoped con prefijo `.m-{id}-*` o BEM.
4. Router envuelve cada mount en try/catch → `renderDegradedCard(id, err, retry)`.
5. Cada módulo maneja los 4 `view-state`: loaded/empty/loading/error.
6. Todo texto user-facing con `data-i18n="key"` + llamar a `ctx.i18n.apply(slot)` tras render.
7. Todo botón icon-only con `aria-label`.
8. Todo landmark con `role` apropiado.
9. Todo interactivo con `:focus-visible` outline 2px coral offset 2px.
10. `prefers-reduced-motion` apaga animaciones decorativas.

---

## 5 · Data seed `MOCK` — forma obligatoria

El sub-agente A3 produce un objeto JS único declarado como:

```js
const MOCK = {
  tenants: [...],         // 3 entries
  users: [...],           // 5 entries con roles
  departments: [...],     // 7 entries
  businessEntities: [...], // 3 entries
  agents: [...],          // 6 agents con {spec, runtime, memory}
  skills: {...},          // keyed by skill_id
  drafts: [...],          // 14 drafts, dr_001 tiene 6 claims con provenance
  runs: [...],            // 50+ runs con state ledger completo
  consolidations: [...],  // 7, 1 hot en sk_cotizar
  feedbacks: [...],       // 40 tipificados
  auditEvents: [...],     // 300+ de últimos 30d
  actions: [...],         // 12 en action-risk registry
  goldSamples: [...],     // 20 con 13 campos c/u
  connectors: [...],      // 8 (Gmail/SAP/Hubspot/WhatsApp/Slack/Sheets/n8n/Make)
  policies: [...],        // JSON/YAML read-only en admin
  jobs: [...],            // 10 operativos con job_execution timeline
  alerts: [...],          // 5 configuradas
  tables: [...]           // 20 FROZEN tablas con DDL + RLS policies (para Schema Explorer)
};
```

### Reglas del seed:

- **IDs UUIDv7-style:** pattern `'018f2b8c-xxxx-7xxx-xxxx-xxxxxxxxxxxx'` (no ULID).
- **Sin inventar datos operativos reales** de Marluvas/Tecmater. Usar nombres genéricos tipo "Constructora Andes", "Minera del Valle", "Industria Norte".
- **Todo timestamp en UTC ISO.** Último mes coherente (fecha actual: 2026-04-19, rango: 2026-03-20 → 2026-04-19).
- **Montos en USD y COP/MXN/CRC** según tenant, con símbolo.
- **dr_001 es el demo-crítico.** Tiene 6 claims con provenance completa — mantener el existente y solo mejorarlo si hace falta.

---

## 6 · Extensión del sidebar y topbar

**Sidebar final (13 items en 3 bloques):**

```
PRINCIPAL
  ◈ Dashboard          #/dashboard
  ◧ Bandeja            #/bandeja
  ◔ Agentes            #/agentes
CONSTRUCCIÓN
  ◇ Skills             (acceso desde Agente > tab Skills)
  ◫ Workflows          #/workflows
  ⬡ Factory            #/factory
  ◉ Conexiones         #/conexiones
────
GESTIÓN
  ◎ Admin              #/admin     (Owner/Admin only)
  ⊡ Autonomy           #/admin/autonomy-evidence (Owner/Admin only)
  ◐ Settings           #/settings
```

**Topbar final (en orden):**

```
[logo + wordmark "FaberLoom"] [⌘K palette]  ........
  [🏢 tenant▼] [👤 role▼] [🌐 lang▼] [◐ theme] [♿ a11y-validate] [⚙ user-menu]
```

Banner demo persistente (1 línea discreta abajo del topbar o arriba del main):
"Mockup · data sintética · no conecta a sistemas reales"

---

## 7 · i18n — estructura del diccionario inline

```js
const I18N = {
  es: {
    nav: { dashboard:'Panel', bandeja:'Bandeja', agentes:'Agentes', ... },
    status: { loaded:'Cargado', empty:'Vacío', loading:'Cargando', error:'Error' },
    autonomy: { L0:'Shadow', L1:'Propone', L2:'Auto-bajo', ... },
    ...
  },
  en: { nav: { dashboard:'Dashboard', ... }, ... },
  'pt-BR': { nav: { dashboard:'Painel', ... }, ... }
};
```

20 dominios mínimos: `nav · status · autonomy · bandeja · agent · skill · action · empty · error · dialog · tooltip · admin · settings · launcher · landing · dashboard · draft · workflow · conn · intl`.

332+ keys por idioma. Switch persistente en `localStorage.getItem('faberloom.v1.lang')` con fallback a memoria si bloqueado.

**Regla crítica:** cero strings en español hardcoded en el HTML. Todo via `data-i18n="dominio.key"` resuelto por `i18n.apply(root)` tras cada render.

---

## 8 · Criterios de aceptación (25 binarios)

Al terminar, **los 25 ítems en verde**:

1. [ ] 13 rutas del sidebar navegables (ninguna 404).
2. [ ] Cada módulo responde a 4 view-states (loaded/empty/loading/error).
3. [ ] Sidebar oculta Admin/Autonomy para rol Operator.
4. [ ] Tenant switcher cambia data visible (3 tenants con data independiente).
5. [ ] Role switcher cambia sidebar + CTAs permitidos.
6. [ ] ⌘K overlay con focus trap real, Esc cierra, keyboard nav.
7. [ ] Provenance: hover `E1` highlightea span en panel derecho (ya existe, no romper).
8. [ ] Feedback modal con 5 razones emite al bus con payload completo.
9. [ ] Consolidation modal con 4 secciones + preview before/after.
10. [ ] Learning Thermometer en Skill Studio + Agent Console Resumen.
11. [ ] Autonomy Ladder visible en 3 pantallas (Agent Console + Admin Autonomy + Agentes List).
12. [ ] Action-risk badge en Bandeja + drafts + nodos Workflow.
13. [ ] Workflow State Ledger timeline en Agent Console Logs expandible por paso.
14. [ ] Schema Explorer en Admin/Plataforma con las 20 tablas + RLS policies visibles.
15. [ ] Audit log con 300+ eventos filtrables + exportable a CSV.
16. [ ] Admin/Personas con impersonación + BreakGlassBanner activable con timer 8h.
17. [ ] Factory wizard 3 pasos + validación + default L0 Shadow.
18. [ ] Light + dark paritarios (verificar axe sobre bandeja-detail/admin/dashboard en ambos temas = 0 críticos).
19. [ ] 3 idiomas con switch persistente y ≥332 keys.
20. [ ] Skip-link al `<main>` enfocable con Tab como primer tab stop.
21. [ ] `node --check` verde sobre JS extraído del HTML.
22. [ ] Error boundary: forzar `throw` en mount de un módulo NO tumba el shell.
23. [ ] Design system showcase en ruta `#/design-system` (opcional) o tab interno muestra todos los tokens + tipografía + widgets en light+dark.
24. [ ] El archivo abre correctamente con `file://` (doble clic) — sin warnings de CORS en consola.
25. [ ] Tamaño final entre 8000–14000 líneas, tiempo de carga inicial <2s en un laptop normal.

---

## 9 · Verificación (obligatoria antes de cerrar)

```bash
# 1. Extraer JS y verificar syntax
cd "/sessions/dazzling-funny-wright/mnt/MWT KB/faberloom-mockup"
awk '/<script>/,/<\/script>/' index-standalone.html | grep -v '^<script' | grep -v '^</script' > /tmp/fl_extracted.js
node --check /tmp/fl_extracted.js && echo "✓ JS syntax OK"

# 2. Contar líneas
wc -l index-standalone.html

# 3. Grep de rutas registradas
grep -cE "route:\s*'#/" index-standalone.html
# Debe ser ≥13

# 4. Grep de i18n keys (suma aproximada)
grep -cE "data-i18n=" index-standalone.html
# Debe ser ≥200 aplicaciones (muchos elementos usan la misma key)

# 5. Smoke check: abrir en Chrome/Firefox con file://
# Verificar manualmente en terminal:
# - Sidebar muestra 13 items
# - Click a dashboard → carga sin error en consola
# - ⌘K abre launcher
# - Theme toggle funciona
# - Tenant switcher cambia data
```

**Output esperado al terminar (pegar en chat):**

```
STANDALONE HTML COMPLETO — FaberLoom v2

Archivo: /MWT KB/faberloom-mockup/index-standalone.html
Líneas: 11,247
JS extraído: node --check ✓ OK
Rutas registradas: 13 + 3 overlays
i18n keys: 341 × 3 idiomas = 1023 keys totales
Tamaño en disco: 480 KB

Criterios: ✅ 24/25  (item 18 axe: 2 warnings menores en admin dark — ver TODO)

TODOs diferidos a v2 post-partners:
- [M] Drag & drop real en workflows palette (hoy solo drag preview)
- [S] Export consolidación aprobada a CSV (hoy solo bus event)
- [S] 2 axe warnings dark mode admin — contraste label secundario

Archivo listo para doble clic. Abre en Chrome/Firefox/Safari file:// sin warnings.

Siguiente paso sugerido:
Abrirlo con cada design partner en screen share, capturar feedback
vía el modal de 5 razones, validar que flujo de aprobación es
comprensible sin training.
```

---

## 10 · Reglas inquebrantables del run

1. **No reescribir lo que funciona.** Los 4 módulos existentes (bandeja-detail, skill-studio, agent-console, workflows) se mantienen. Solo se extienden si les falta algo del §8.
2. **No inventar datos operativos reales.** Campos `[MOCK]` explícitos donde falta.
3. **No tocar KB MWT ni escribir a `/docs/`.**
4. **No tocar FROZENs del SPEC.** IDs UUIDv7 pattern.
5. **No agregar frameworks.** Vanilla JS + CSS + SVG inline.
6. **No emoji decorativos.** Solo thermometer 🔵🟡🔴 + status icons semánticos de lucide/feather inline.
7. **Si dudás:** default restrictivo. Autopilot off. Aprobación humana on. Evidencia visible.
8. **Timeboxed:** si un sub-agente excede 15 min, asumí fallo y reasigná.
9. **Un solo archivo.** Si tenés tentación de crear `.css` o `.js` externo, parar: inyectalo al HTML.

---

## 11 · Apéndice A · Cobertura conceptual (trazabilidad completa)

Matriz: cada concepto del SPEC tiene que tener un lugar en el HTML donde vive. Si falta uno, el mockup no prueba el sistema entero.

| Concepto SPEC | Dónde vive en el HTML | Trazado |
|---|---|---|
| UUIDv7 mock IDs | Todos los IDs de `MOCK` | ✅ |
| 20 tablas FROZEN v1 | Schema Explorer en Admin/Plataforma | ✅ |
| Sin FKs + outbox pattern | Schema Explorer muestra outbox + inbox + eventos | ✅ |
| RLS session-scoped | Schema Explorer muestra policy text + Role Switcher demuestra efecto | ✅ |
| 4 scopes + business_entity_id | Skill Studio sidebar + draft evidence indica scope | ✅ |
| 3 roles | Role switcher + UI responde | ✅ |
| Private-by-default | Admin/Personas banner aclara | ✅ |
| 3 objetos Spec/Runtime/Memory | Agent Console 4 tabs (Resumen=Runtime, Skills=Spec, Memoria=Memory, Logs=Ledger) | ✅ |
| State machine 9 estados | Agent Console Resumen + Workflow ledger | ✅ |
| Event-driven learning | Feedback modal → bus → Consolidation → Skill Studio overlay aprendido | ✅ |
| Autonomy ladder + criterio textual | Agent Console Resumen + Admin Autonomy + tabla Agentes | ✅ |
| Action-risk registry 12+ entries | Badge en Bandeja + lista completa en Admin/Plataforma | ✅ |
| Provenance schema | Bandeja detail Evidencia tab + Provenance Tree | ✅ |
| Workflow state ledger | Agent Console Logs expandible por paso | ✅ |
| Draft-first absoluto | Bandeja entera + footer sticky 3 botones + sin CTAs envío directo | ✅ |
| Feedback tipificado 5 razones | Feedback modal desde Bandeja detail | ✅ |
| Consolidation Candidate/Active/Archived | Consolidation modal + Skill Studio overlay aprendido | ✅ |
| Learning thermometer + modal | Widget en Skill Studio + Agent Console Resumen | ✅ |
| OIDC + manual + CSV | Admin/Personas/Usuarios botón "Invitar" 3 tabs | ✅ |
| Break-glass 8h MFA | Admin/Personas "Impersonar" → BreakGlassBanner timer | ✅ |
| TTL learned overlays 90d | Skill Studio "Caduca en N días" por overlay | ✅ |
| Scheduler `job_execution UNIQUE` | Admin/Plataforma Schema Explorer tabla + Jobs timeline | ✅ |
| Backup RPO 24h/RTO 2h | Admin/Plataforma card Backup con última ejecución + restore test | ✅ |
| Obs 3 dashboards + 5 alertas | Admin/Plataforma 3 cards embed + Alertas tab con 5 | ✅ |
| SMTP Postmark | Admin/Plataforma Conectores admin muestra entry configurada | ✅ |
| 8 métricas mínimas Prometheus | Dashboard + Admin Plataforma cards | ✅ |
| Leakage tests CI gate | Admin/Plataforma Policies pane "10/10 green · last run 2h ago" | ✅ |
| Beta slice 8 semanas | Admin/Plataforma Release rings tab con calendar S1–S4 | ✅ |
| Wedge cotización calzado | Data seed realista + drafts con specs ASTM | ✅ |
| i18n 332+ keys × 3 idiomas | Diccionario inline, switch topbar persistente | ✅ |
| A11y AA + axe runtime | Botón "Validar" topbar + focus-visible + skip-link | ✅ |
| Modularidad con error boundary | Shell try/catch por módulo + DegradedCard renderizado | ✅ |

Si todas las filas quedan trazadas, el HTML **prueba la arquitectura entera en una demo navegable de un solo archivo**. Ese es el objetivo.

---

## 12 · Apéndice B · Glosario (para no perderse)

- **AgentSpec** = contrato estático (rol, skills, autonomy_ceiling, policies).
- **AgentRuntime** = estado dinámico (state machine, tarea activa, confianza).
- **AgentMemory** = acumulado (sender profiles, gold samples, KB asignada).
- **Autonomy Ladder** = L0 Shadow · L1 Propone · L2 Auto-bajo · L3 Auto+notif · L4 Auto+excepciones. Criterio textual de unlock por nivel.
- **Draft-first** = ningún outbound sin aprobación humana.
- **Provenance** = `claim_id → evidence_span_id → source_version → retrieval_run_id`.
- **Action-risk** = metadata estructurada por action (risk_class, approval_mode, reversible, customer_visible, financial_impact, source_of_truth).
- **Workflow state ledger** = persistencia de cada run con versiones, approvals, errores, evidencias, costo.
- **Learning Thermometer** = 🔵 Frío 0–2 · 🟡 Tibio 3–5 · 🔴 Caliente 6+.
- **Consolidation pipeline** = Candidate → Active → Archived/Reverted, CEO-gated.
- **Feedback tipificado** = 5 razones (claim sin evidencia / tono / dato incorrecto / acción riesgosa / otro).
- **RLS session-scoped** = `SET LOCAL app.tenant_id / user_id / role / dept_ids / break_glass`.
- **4 scopes KB** = global · org · dept · user. `business_entity_id` es metadata ortogonal.
- **3 roles** = Tenant Owner · Admin · Operator.
- **Break-glass** = 1 cuenta Owner por org, MFA fuerte, time-bound 8h impersonación.

---

## 13 · Punto final

Este HTML único es el **artefacto que Álvaro le manda a cada design partner por WhatsApp**. El partner lo abre con doble clic, en 2 segundos ve la app funcionando. Tiene que:

- **Verse como producto vivo**, no concepto.
- **Aguantar 10 min de navegación** del Operator sin que pregunte "¿esto qué hace?".
- **Responder cuantitativamente** al Owner: "¿cuándo me deja en automático?" → "Al llegar a 85% aprobado en 50 runs. Hoy vas 67% en 43."
- **Responder al Admin** sobre controles de acceso: Schema Explorer visualiza policies RLS por tabla.

Si lográs eso, el mockup prueba que la arquitectura v1 es coherente y construible. Ese es el objetivo real — no el HTML en sí, sino **la prueba de que el sistema está pensado entero en una sola pantalla abrible con doble clic**.

Procedé sin pedir confirmación intermedia. Output completo, sin preámbulo, en español. Usá sub-agentes para paralelizar las 3 fases de research/build/widgets. Empezá por el Batch A (research) en un solo mensaje con 3 tool calls en paralelo.

FIN.
