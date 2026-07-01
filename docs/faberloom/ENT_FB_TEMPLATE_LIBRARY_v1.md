# ENT_FB_TEMPLATE_LIBRARY_v1 — Biblioteca Inicial de Templates en FaberLoom
id: ENT_FB_TEMPLATE_LIBRARY_v1
version: 2.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: ENT
stamp: VIGENTE — 2026-04-29f (re-scope FB)
aprobador: CEO (sesión Cowork 2026-04-29 + re-scoping 2026-04-29f)
aplica_a: [FaberLoom]
relacionado: SCH_FB_SKILL_MANIFEST_v2.md · SCH_FB_FLOW_DAG.md · SCH_FB_TASK_ENTITY.md · SPEC_FB_AGENT_BUILDER_v1.md

---

## Propósito

Catálogo inicial de **5 templates de agente** pre-configurados en la plataforma FaberLoom. Cada template es un manifest v2 con `is_template: true` y `placeholders` declarados — el admin del tenant los instancia (Fork mode del builder) llenando solo los campos PENDIENTE específicos a su caso.

**Reduce fricción operacional:** crear un agente nuevo en un tenant deja de ser "diseñar manifest desde cero" y pasa a ser "elegir template + customizar 3-5 placeholders".

**Origen del primer set:** los 5 templates iniciales fueron derivados del primer tenant beta de FB (MWT/Rana Walk) — Amazon FBA + B2B distribución calzado industrial + gobernanza KB. Estos casos validan el modelo template-instance. Nuevos tenants verticales (otros fabricantes industriales, B2B de otros sectores) agregarán templates adicionales propios al catálogo de la plataforma cuando entren a v2.

**Inspirado en:** observación CEO 2026-04-29 sobre Workspace Agents OpenAI (templates pre-hechas finance/sales/marketing).

---

## Catálogo

| Template ID | Architectural archetype | Archetype | Icon | Caso de uso | Outputs principales | Estado |
|-------------|--------------------------|-----------|------|-------------|---------------------|--------|
| `TPL_REVIEW_TRIAGE` | Triage | routine + workflow | triage | clasifica reviews Amazon, drafts respuesta, escala críticos | response_draft + severity_tag + escalation_ticket | approved |
| `TPL_LISTING_OPTIMIZER` | Generator | skill | generator | optimiza listings Amazon (titles, bullets, A+ Content) | listing_text + recommendations | approved |
| `TPL_LEAD_QUALIFIER_B2B` | Triage | routine + workflow | triage | califica leads B2B entrantes Gmail, drafts seguimiento | qualification_score + draft_email + crm_update | approved |
| `TPL_QUOTE_GENERATOR_B2B` | Generator | skill | generator | genera proforma para cliente B2B (Marluvas/Tecmater) | proforma_html + send_payload | approved |
| `TPL_KB_AUDITOR` | Validator | routine | validator | audita KB diaria, detecta drift, genera reporte | audit_report + drift_alerts | approved |

**Nota v1.1**: cada template ahora declara su `architectural_archetype` (ver ENT_AGENT_ARCHETYPES_V1) además del `archetype` de ejecución. El field `icon` corresponde al icon ID del catálogo (matchea iconografía Workspace Agents OpenAI por arquetipo).

Cada template vive en `docs/templates/<TPL_ID>.yaml` (formato manifest v2 completo). Este documento es el **índice + descripción**, no los manifests en sí.

---

## TPL_REVIEW_TRIAGE — Triage de Reviews Amazon

**Caso de uso:** entran reviews nuevos por webhook (n8n + Amazon SP-API). El agente:
1. Clasifica severidad (critical / negative / neutral / positive)
2. Si crítico → escala a CEO con ticket
3. Si negativo o neutro → pasa por COMPLIANCE_CHECKER → drafts respuesta
4. Si positivo → drafts agradecimiento simple

**Outputs declarados (3):**
- `response_draft` (asset, requires_human_approval) → drafts/queue
- `severity_tag` (decision, auto-persist) → episodic_memory
- `escalation_ticket` (side_effect, condition: severity == critical) → case_log/

**Placeholders al instanciar:**
- `outcome.baseline_value`: TTR review actual sin agente, en horas
- `outcome.target_at_60d`: objetivo TTR a 60 días (default `< 8`)
- `tools_mcp[0].config.amazon_seller_id`: tu seller_id en Amazon
- `tools_mcp[1].config.helium10_api_key`: opcional, para análisis sentiment avanzado

**Golden samples requeridos:** 2 (case 4-star queja, case crítico escalado).

**Budget default:** $25/mes, hard_cap $50, kill_switch enabled.

---

## TPL_LISTING_OPTIMIZER — Optimizador Listings Amazon

**Caso de uso:** CEO selecciona ASIN candidato. El agente:
1. Lee specs producto + brand voice + claims permitidos
2. Genera variantes de title, bullets, descripción
3. Aplica POL_BRAND_VOICE + POL_AMAZON_TOS + POL_CLAIMS_SCANNER
4. Retorna 2-3 propuestas + scoring estimado

**Outputs declarados (2):**
- `listing_text` (asset, requires_human_approval) → listings/proposals/
- `recommendations` (learning) → episodic_memory para gold sample futuro

**Placeholders al instanciar:**
- `outcome.baseline_value`: conversion rate ASIN actual (%)
- `outcome.target_at_60d`: lift esperado (default `+5%`)
- `inputs.kb_refs`: ENT_PROD_<X> específicos del catálogo
- `inputs.kb_refs[]`: LOC_<idioma> según marketplace target

**Golden samples requeridos:** 1+ por marketplace (ES_MX, ES_US, EN_US).

**Budget default:** $30/mes, hard_cap $60.

---

## TPL_LEAD_QUALIFIER_B2B — Calificador Leads B2B

**Caso de uso:** entra email a inbox B2B (Gmail webhook). El agente:
1. Parsea remitente, empresa, intención, volumen estimado
2. Compara contra criterios de calificación (industria, geo, fit Marluvas/Tecmater)
3. Asigna score (A/B/C/D)
4. Si A o B → drafts email seguimiento
5. Si C/D → drafts respuesta cortés con redirección
6. Actualiza CRM (Marluvas portal o equivalente)

**Outputs declarados (3):**
- `qualification_score` (decision) → episodic_memory + dashboard
- `draft_email` (asset, requires_human_approval) → drafts/queue
- `crm_update` (side_effect) → CRM via API

**Placeholders al instanciar:**
- `outcome.baseline_value`: lead-to-quote rate actual (%)
- `outcome.target_at_60d`: mejora esperada (default `+10%`)
- `inputs.kb_refs[]`: ENT_COMERCIAL_CLIENTES + perfiles de cliente ideal
- `tools_mcp[].config.gmail_account`: cuenta de email del comercial
- `tools_mcp[].config.crm_endpoint`: URL del CRM

**Golden samples requeridos:** 2 (lead alta calidad, lead a redirigir).

**Budget default:** $20/mes, hard_cap $40.

---

## TPL_QUOTE_GENERATOR_B2B — Generador Proforma B2B

**Caso de uso:** CEO o comercial declara cliente + items + cantidades. El agente:
1. Lee perfil cliente (modo broker/trader/reseller, pricing tier, condiciones)
2. Aplica ENT_COMERCIAL_PRICING + descuentos por volumen
3. Reusa golden sample de proforma exitosa similar
4. Genera HTML dual-view (CEO mode interno + client mode externo)
5. Genera payload para envío email/WhatsApp

**Outputs declarados (2):**
- `proforma_html` (asset, requires_human_approval) → proformas/draft/
- `send_payload` (side_effect, condition: ceo_approves) → email/WhatsApp via API

**Placeholders al instanciar:**
- `outcome.baseline_value`: tiempo armar proforma manual (minutos)
- `outcome.target_at_60d`: tiempo objetivo (default `< 5 min`)
- `inputs.kb_refs[]`: ENT_COMERCIAL_PRICING + ENT_COMERCIAL_MODELOS
- `tools_mcp[].config.proforma_template_id`: PF_0000-2026_GOLDEN

**Golden samples requeridos:** 1 por modo (broker / trader / reseller).

**Budget default:** $15/mes, hard_cap $30.

---

## TPL_KB_AUDITOR — Auditor KB diario

**Caso de uso:** Celery Beat dispara diariamente a las 06:00 CR. El agente:
1. Recorre archivos KB modificados últimas 24h
2. Aplica V1-V9 checks (formato, headers, dependency graph, FROZEN intactos)
3. Detecta drift (archivos sin update >90 días, dependencias rotas)
4. Genera reporte score X/10 + hallazgos P0-P2
5. Si P0 o score < 7 → notifica CEO

**Outputs declarados (2):**
- `audit_report` (asset) → reportes/audit/<fecha>.md
- `drift_alerts` (side_effect, condition: score < 7 OR p0_count > 0) → notify_ceo

**Placeholders al instanciar:**
- `outcome.baseline_value`: KB drift score actual (semilla)
- `outcome.target_at_60d`: drift score objetivo (default `> 8/10`)
- `tools_mcp[].config.notify_channel`: email | slack | webhook

**Golden samples requeridos:** 1 (audit_report formato canónico).

**Budget default:** $5/mes, hard_cap $15. Cron diario, no webhook.

---

## Cómo el CEO instancia un template (Fork mode)

```
1. CEO en dashboard portal.mwt.one/agents/new
2. Lista de templates disponibles (5 + futuros)
3. CEO elige TPL_REVIEW_TRIAGE
4. Builder muestra wizard con cada placeholder:
   - "TTR review actual sin agente, en horas?" → CEO escribe: 28
   - "Objetivo TTR a 60 días?" → CEO escribe: < 8
   - "Tu seller_id Amazon?" → CEO escribe: A1XXXXX
   - "API key Helium 10? (opcional)" → CEO skip o escribe
5. Builder valida placeholders + compila manifest
6. Manifest queda en SHADOW listo para empezar Fase 3 SHADOW 30 días
7. SKILL_RW_REVIEW_TRIAGE_001 (instancia derivada de template) viva en KB
```

El template original (TPL_REVIEW_TRIAGE) **no se modifica**. Cada Fork crea una instancia nueva con id derivado (`<TPL_ID>_<sequence>` o nombre custom CEO).

---

## Lifecycle del template

```
draft ──→ approved ──→ deprecated ──→ archived
            │
            └──→ (template patch) ──→ approved (v+1)
```

Cuando un template se patcha (cambio de schema, nueva versión):
- Las instancias derivadas con `forks_from: TPL_REVIEW_TRIAGE@1.0` quedan en versión vieja
- El builder propone re-fork de instancias afectadas (Patch broadcast — vista que mockeamos)
- CEO decide migrar o dejar versión congelada

---

## Roadmap templates v2+

Cuando MWT v1 madure:

| Template propuesto | Dominio | Trigger esperado |
|--------------------|---------|------------------|
| `TPL_DEMAND_FORECASTER` | distribución | después de 1er SKILL graduado |
| `TPL_COMPLIANCE_GATE` | gobernanza | cuando ≥3 SKILLs requieran validación POL |
| `TPL_HUMANIZE_RESPONSE` | comercial | cuando se necesite voice unification cross-canal |
| `TPL_CLIENT_SERVICE_MULTILINGUAL` | comercial | cuando ES/PT B2B madure |

Para FaberLoom (futuro): biblioteca distinta orientada a fabricantes (TPL_PRICING_REVIEW, TPL_INVENTORY_TRIAGE, TPL_QUALITY_ALERT, etc.).

---

## Política de templates

| Regla | Aplicación |
|-------|------------|
| Templates mantenidos por CEO solamente | governance: `template_metadata.maintained_by: ceo` |
| Templates `status: approved` son únicos forkeables | `status: draft` solo CEO puede forkear |
| Templates con `placeholders[].required: true` no compilan sin valor | validación 19 SCH_SKILL_MANIFEST_V2 |
| Templates incluyen golden_samples obligatorios al menos para outputs `kind: asset` | validación 17 SCH_SKILL_MANIFEST_V2 |
| Forks heredan version del template; auto-update opt-in | manifesto declarado en cada fork |

---

## Estado de los manifests reales

A la fecha 2026-04-29, los 5 manifests YAML de templates están **PENDIENTE — escribir** en `docs/faberloom/templates/<TPL_ID>.yaml`. Este documento es el catálogo + spec; los manifests se crean en Fase 1 del `SPEC_FB_AGENT_BUILDER_v1`, junto con la migración de SKILL_RW_REVIEW_TRIAGE del primer tenant MWT (que será fork de TPL_REVIEW_TRIAGE).

Orden de escritura recomendado:
1. TPL_REVIEW_TRIAGE (Fase 1 — primer fork será el SKILL real)
2. TPL_QUOTE_GENERATOR_B2B (alta prioridad operacional)
3. TPL_LEAD_QUALIFIER_B2B
4. TPL_KB_AUDITOR
5. TPL_LISTING_OPTIMIZER

---

Stamp: VIGENTE — 2026-04-29f (re-scope FB)

Changelog:
- v1.0 (2026-04-29b): creación con scope MWT-only erróneo. Catálogo de 5 templates iniciales con archetype, outputs principales, placeholders, golden samples requeridos, budget default. Política de governance.
- v1.1 (2026-04-29c): agregado `architectural_archetype` y `icon` a cada template del catálogo. UI futura del builder agrupa templates por arquetipo (cards visuales con icon).
- **v2.0 (2026-04-29f): re-scope completo a FaberLoom. Renombrado ENT_TEMPLATE_LIBRARY_V1 → ENT_FB_TEMPLATE_LIBRARY_v1. Los 5 templates iniciales fueron derivados del primer tenant beta MWT/Rana Walk; son el set inicial de la plataforma FB. Nuevos tenants verticales agregarán templates propios. Aprobador: CEO sesión re-scoping 2026-04-29f.**
