---
id: LOTE_SM_SPRINT_SKILLS_MT_v1
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: research/agentes_skills_2026
category: generated_staging
type: LOTE_SM_SPRINT
date: 2026-06-01
author: Claude (Cowork)
sustento: RESEARCH_AGENTES_SKILLS_2026_v1 (ronda Claude 8 dims + ronda Kimi K1-K6 + CROSSVERIF)
---

# LOTE_SM_SPRINT_SKILLS_MT_v1 - Sprint 1: Foundations de Skills Multi-Tenant

## Objetivo del sprint

Dejar de operar skills sin guardrails. Al cierre: (1) base de gobernanza (registry RLS + CI de seguridad + vault por tenant), (2) las 3 primeras skills internas que codifican reglas MWT, (3) SP-API operando en Claude Code CLI (no Cowork). Duracion estimada: 2 semanas. Es el Sprint 1 de un roadmap de 3 (ver Apendice).

Tesis (de la investigacion): las skills dan eficiencia de contexto y consistencia, pero NO aislan tenants ni traen seguridad por defecto. El valor para MWT es interno y gobernado, no la libreria publica. Por eso se construyen guardrails ANTES de cualquier skill de marketplace.

## Principio rector

Adoptar SKILL.md solo como capa de conocimiento interno gobernado. Cero instalacion abierta desde marketplace. Lo critico (tenant_id, RLS, visibilidad, compliance) va en SCRIPT determinista, nunca en prose interpretada por LLM. Aislamiento por proceso (sub-agente / MCP scoped), no por skill compartida.

---

## Bloque A - Guardrails Fase 0 (NO negociable, va primero)

| # | Tarea | Sustento | Done cuando | Dep |
|---|-------|----------|-------------|-----|
| A1 | Registry de skills con RLS: tabla `skill_registry` (tenant_id NOT NULL, skill_type, status, visibility, content_hash SHA-256) + RLS policy `tenant_id = current_setting('app.tenant_id')` | K2 (GoClaw 40+ tablas tenant_id NOT NULL; reference impl de reglas MWT) | tabla + policy creadas; test cross-tenant: tenant B NO ve skills de tenant A (rojo->verde) | - |
| A2 | CI de seguridad de skills: GitHub Action en `skills/**` con `mcp-scan` + `skillfortify scan` (`--fail-on-warning`) | K6 (Snyk 36.82% fallas; SkillFortify 96.95% F1 arXiv 2603.00195) | PR con skill insegura se bloquea; top-skills propias pasan | - |
| A3 | Hardening runtime: `.claude/settings.json` commiteado ANTES de arrancar sandbox + Claude Code >= 2.1.2 + deny rules para tools destructivos SP-API | K3/K6 (CVE-2026-25725, CVSS 7.7, sandbox escape via settings.json) | version verificada >=2.1.2; settings.json en repo; deny `deleteListing`/`updatePrice batch>10` | - |
| A4 | Migrar skills SP-API de Cowork a Claude Code CLI local | K3 (#37970: Cowork bloquea dominios no-allowlist; SP-API/n8n inalcanzables) | skill SP-API corre en CLI contra sellingpartnerapi; Cowork descartado para SP-API/n8n | - |
| A5 | Vault de credenciales por tenant: lookup `(tenant_id, tool_name)` con KMS keys por tenant; credenciales efimeras | K2 (Descope: agentes sin API keys de larga vida; Omnithium: nunca env vars) | credenciales SP-API por tenant via vault; CERO env vars globales | A1 |

**Guardrails A (inquebrantables):** tenant_id NOT NULL en toda tabla aislable; tenant fluye por context server-side, NUNCA headers de cliente; credenciales efimeras, nunca long-lived; network egress deny-by-default + allowlist por tenant.

---

## Bloque B - Primeras skills internas Fase 1 (codifican TUS reglas)

| # | Skill | Que hace | Sustento | Done cuando | Dep |
|---|-------|----------|----------|-------------|-----|
| B1 | `tenant-guard` (skill + script determinista) | Valida tenant_id, RLS y visibilidad (PUBLIC/PARTNER_B2B/INTERNAL/CEO-ONLY) en SCRIPT, no en prose | dim08/T2 (compliance nunca interpretado por LLM); riesgo #1 multi-tenant | script valida aislamiento; eval pass^5 >= 60%; test cross-tenant en rojo->verde | A1 |
| B2 | `kb-frontmatter-validator` | Valida headers obligatorios (id/version/status/visibility/domain) en ENT/PLB/POL/SCH/LOC/IDX/SKILL antes de promover | dim06 d1 (previene el error de indexado mas frecuente) | detecta header faltante en archivo de prueba; corre en pre-commit/CI | - |
| B3 | `skill-review` (meta-skill, gate de supply-chain) | Checa SKILL.md entrante contra taxonomia Snyk (injection, secrets, suspicious download, unverifiable deps) | dim08/K6 (91% de maliciosas combinan injection + malware) | bloquea skill con patron inseguro en CI; integra A2 | A2 |

**Nota de curacion:** self-generated skills NO se aceptan sin revision humana (K1: -1.3pp). Toda skill entra por PR + review + A2.

---

## Bloque C - Evals y observabilidad (Fase 1)

| # | Tarea | Sustento | Done cuando |
|---|-------|----------|-------------|
| C1 | Pipeline `skillgrade` con 3 gates: smoke (pass@5 >= 70%) -> PR eval (pass@5 >= 80%) -> regression (**pass^5 >= 60%**) | K4 (t-bench: 60% pass@1 -> 25% consistencia real; pass^k es la metrica de produccion) | pipeline corre en PR; gate regression usa pass^k, no pass@k |
| C2 | OpenTelemetry: `CLAUDE_CODE_ENABLE_TELEMETRY=1` + alertas (token/skill >2x, fallo >3x, auth errors SP-API) | K4 (token.usage segmentable por skill.name) | metricas por skill.name visibles; alertas activas |

**Guardrail C:** pass^k < 60% => NUNCA deploy a produccion. SKILL.md nunca > 10,000 tokens.

---

## Bloque D - Contrato e interface de skills

Hallazgo (sesion): el envoltorio SKILL.md es uniforme, pero la interface de interaccion NO (modo de invocacion, args, scripts vs prose, runtime). A diferencia de MCP, no hay schema de I/O tipado: la "interface" de una skill es convencion en prose. Para multi-tenant el contrato hay que imponerlo por encima del estandar.

| # | Tarea | Que define | Done cuando | Dep |
|---|-------|-----------|-------------|-----|
| D1 | Crear `SCH_SKILL_INVOCATION_v1` | Contrato tipado de invocacion/output para skills internas MWT: inputs declarados, shape de output, modo de invocacion estampado (auto vs explicita) | toda skill interna valida contra el schema en build; rechazo si no cumple | B1-B3 |
| D2 | Crear `SPEC_FB_SKILL_FACTORY_v1` | Factory opinado con 2 perfiles de salida: `mwt-internal` (contrato estricto, scripts con firma, no portable) y `portable` (SKILL.md estandar puro). Contrato base invariante (SCH + seguridad + evals) NO override-able por tenant; overrides per-tenant (skills enabled / tools / creds) en su propio scope. Pipeline de build con mcp-scan + skillfortify + evals embebidos. Rechazo de combos runtime imposibles (ej. skill SP-API en Cowork) | spec aprobada; el factory produce skills que nacen escaneadas, con eval (pass^k) y contrato; perfil elegible por skill | A1, A2, C1, D1 |

**Regla del factory:** es el punto donde se colapsa la variabilidad del estandar abierto en el perfil MWT. Lo critico (tenant_id, validacion, visibilidad) SIEMPRE como script con firma tipada, nunca como prose interpretada.

---

## Criterios de exito del sprint

1. Registry RLS: test de aislamiento cross-tenant pasa (tenant B no ve skills de A).
2. CI bloquea skills inseguras (mcp-scan + SkillFortify activos en PR).
3. SP-API opera en Claude Code CLI; Cowork formalmente descartado para SP-API/n8n.
4. `tenant-guard`, `kb-frontmatter-validator`, `skill-review` en repo, cada una con eval (pass^5 >= 60%).
5. Cero credenciales de tenant en env vars; todas via vault.
6. Claude Code >= 2.1.2 con settings.json hardening en todos los runners.

## Decisiones CEO requeridas antes de arrancar

- DEC-1: confirmar Postgres + RLS como store del registry de skills (default propuesto; alinea con stack existente).
- DEC-2: confirmar Claude Code CLI local como runtime de skills SP-API (Cowork queda fuera para esos dominios).
- DEC-3: confirmar tooling de vault (KMS por tenant) y de CI security (mcp-scan + SkillFortify).
- DEC-4: confirmar gate de produccion pass^k >= 60% como politica.
- DEC-5: definir si skills genericas de conocimiento salen en perfil `portable` (cross-vendor) o todo en `mwt-internal` (control > portabilidad). Default propuesto: mwt-internal para lo critico, portable para conocimiento no sensible.

## Reglas MWT respetadas

No toca FROZEN (ENT_OPS_STATE_MACHINE, PLB_ORCHESTRATOR solo referenciados). Headers obligatorios en toda skill/POL nueva. Visibilidad enforced. Cambios via PR (este sprint no modifica POL VIGENTE; al promoverse, B1-B3 nacen como SKILL_ DRAFT hasta validacion).

---

## Apendice - Roadmap (fases siguientes, fuera de este sprint)

- **Sprint 2 (Hardening, mes 2):** sandbox gVisor/Firecracker para skills de terceros; OpenSSF Model Signing (firmar skills propias); sub-agentes con tenant context precargado (patron sp-analyst: model haiku + skills: + mcpServers scoped + disallowedTools); skill-creator v2 (eval+improve sobre skills SP-API).
- **Sprint 3 (Dominio, mes 3):** skills de dominio operativo (Helium 10 workflow, cotizacion-calzado-industrial, n8n-workflow-builder); SP-API en vivo robusto multi-tenant.
- **Proyecto aparte (no sprint):** `compliance-epp-latam` (normas EN ISO 20345 / ASTM F2413 / NTC colombianas). Requiere KB normativo curado + validacion experta; riesgo de alucinacion regulatoria. Candidato a swarm propio (ver PROMPT_KIMI_SWARM separado pendiente).

## Conflictos heredados (ya resueltos por CROSSVERIF Kimi)

Cowork vs skills SP-API -> prevalece K3 (CLI). deny rules como unica capa -> +PreToolUse hooks (bug marzo 2026). Docker vs microVM -> Docker para skills propias revisadas, gVisor/Firecracker para terceros. Detalle en kimi_skills_CROSSVERIF.md.
