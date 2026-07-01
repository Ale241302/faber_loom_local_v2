---
id: RESEARCH_AGENTES_SKILLS_2026_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: research/agentes_skills_2026
category: anexo_research
type: research-note
date: 2026-06-01
author: Claude (Cowork) + swarm Kimi
---

# RESEARCH_AGENTES_SKILLS_2026 - Agent Skills (patron SKILL.md) en produccion multi-tenant

Nota canonica consolidada de dos rondas de investigacion sobre Agent Skills (estado junio 2026), indexada como anexo de research. Ronda 1 (swarm Claude, 8 dimensiones, capa estrategica: que son, arquitectura, vs sub-agentes, memoria/contexto, ecosistema, catalogo MWT, evals, recomendacion). Ronda 2 (swarm Kimi, K1-K6, capa de ingenieria: auditoria de papers, multi-tenancy concreta, runtimes, evals/CI, orquestacion nativa, seguridad profunda) con su propio cross-verification. Las dos rondas son capas complementarias, no compiten. Los archivos crudos viven como anexos en esta misma carpeta (ver seccion Anexos).

---

## 1. Hallazgos consolidados (alta confianza, cruzados oficial + Medium/tecnico)

- Skill = carpeta con SKILL.md (frontmatter name+description requeridos + cuerpo Markdown + recursos). Progressive disclosure de 3 niveles (metadata al arranque ~80-100 tok/skill / cuerpo al activar <5k tok / recursos via bash bajo demanda). Scripts ejecutan sin cargar codigo al contexto.
- Determinismo (script) vs no-determinismo (cuerpo interpretado por LLM): lo critico va en codigo.
- Skill != Tool/MCP != Sub-agente != System prompt; se componen. Patron compuesto default 2026: sub-agente Haiku + skill precargada (campo skills:) + MCP scoped. `context: fork` ejecuta la skill en sub-agente aislado.
- Las skills comparten el contexto del agente y NO aislan tenants por diseno; el aislamiento real lo da el sub-agente o MCP por proceso.
- Supply-chain inseguro by-design. Snyk ToxicSkills (2026-02-05): 36.82% de 3,984 skills con >=1 falla, 13.4% criticas, 76 payloads maliciosos. Prompt injection trivial (arXiv 2510.26328): todo el SKILL.md es instruccion.
- Catalogo verificado para MWT: skills oficiales docx/xlsx/pptx/pdf (anthropics/skills); nexscope-ai/Amazon-Skills (27 skills, 6 production / 21 beta, MIT, soporta MX - VERIFICADO por fetch); MarceauSolutions/amazon-seller-mcp existe pero 1 commit / 1 star (referencia, no produccion).

Detalle por dimension: ver anexos agentes_skills_dim01..08 y agentes_skills_CONSOLIDADO.

## 2. Verificacion independiente del swarm Kimi (ronda 2)

El swarm Kimi entrego K1-K6 + CROSSVERIF (58 claims: 26 HIGH / 26 MEDIUM / 6 LOW / 0 sin verificar, 9 conflictos resueltos, auto-deteccion de errores propios) + CONSOLIDADO. Se verificaron de forma independiente los 5 claims mas cargados (y mas sospechosos por especificidad). Todos pasan:

| Claim Kimi | Veredicto | Fuente real |
|---|---|---|
| Cowork bloquea SP-API/n8n (allowlist ignorado, `allowManagedDomainsOnly: true`, 403 blocked-by-allowlist) | CONFIRMADO | anthropics/claude-code #37970 + #30112/#30861/#38984/#43472 |
| GoClaw: tenant_id NOT NULL 40+ tablas, context.Context, RLS | REAL | nextlevelbuilder/goclaw + goclaw.sh |
| SkillFortify 96.95% F1, 0% FPR, SAT-based | REAL | arXiv 2603.00195 + qualixar/skillfortify (MIT) |
| CVE-2026-25725 sandbox escape via settings.json, parche <2.1.2 | REAL | NVD + GHSA-ff64-7w26-62rf + Tenable |
| Skill-Inject ~80% ASR (BoN), 202 pares injection-task | REAL | arXiv 2602.20156 (sub. 23-feb-2026) |

Bandera unica: el consolidado de Kimi quedo fechado 2026-07-09 (un mes en el futuro; reloj/alucinacion de fecha). No invalida las citas (verificadas), pero tratar cualquier marco "a la fecha X" con cautela. Patrones de vault (Omnithium, Scalekit) son fuentes vendor MEDIUM: direccion buena, verificar herramienta antes de adoptar.

## 3. Hechos operativos nuevos que cambian el plan de accion

1. Cowork NO alcanza SP-API ni n8n hoy (bug de allowlist). Skills que toquen SP-API corren en Claude Code CLI local, NO en Cowork.
2. Gate de produccion = pass^k >= 60%, NO pass@k. Un skill con pass@5=100% y pass^5=30% es inestable e inusable en multi-tenant (t-bench: 60% pass@1 -> 25% consistencia real).
3. CVE-2026-25725: crear `.claude/settings.json` ANTES de arrancar el sandbox y estar en Claude Code >=2.1.2.
4. El gate "skill-review" ya tiene herramientas reales: mcp-scan, SkillFortify (qualixar), Cisco mcp-scanner, gVisor para terceros. No hay que inventarlo.
5. Self-generated skills no sirven (-1.3pp, SkillsBench arXiv 2602.12670): curacion humana obligatoria.
6. GoClaw es casi un reference implementation de las reglas multi-tenant MWT (tenant_id NOT NULL, context.Context, nunca headers): estudiar antes de disenar el registry de skills con RLS.

## 4. Reglas inquebrantables confirmadas / derivadas (para POL futura)

- tenant_id fluye por context server-side, NUNCA headers del cliente. Confirmado por GoClaw + AWS Lambda authorizer + broker CABP (arXiv 2603.13417). 0 fuentes contradicen la regla MWT.
- Lo critico (tenant_id, RLS, visibilidad) va en script determinista, nunca en prose interpretada por LLM.
- Multi-tenancy por aislamiento de proceso (sub-agente / MCP scoped por tenant), no por skill compartida.
- Skills de terceros NUNCA sin escaneo previo (mcp-scan + SkillFortify) y en sandbox (gVisor/Firecracker).
- Adopcion solo via registry interno allowlisted + pin a commit-hash + prohibicion de fetch remoto en runtime. Cero instalacion abierta de marketplace.

## 5. Pendiente / proximo paso

Fusionar las dos rondas en un plan maestro de implementacion (capa estrategica MWT + capa de ingenieria Kimi: registry RLS, CI gates pass^k, runtime CLI, defensa) como LOTE_SM_SPRINT con la taxonomia MWT, resolviendo los 9 conflictos que Kimi ya dejo resueltos. Primeras skills internas a construir: tenant-guard (script-first), kb-frontmatter-validator, skill-review (gate de supply-chain), kb-mirror-sync-author.

## Anexos (carpeta docs/anexos/research_agentes_skills_2026/)

Ronda 1 (Claude): agentes_skills_dim01..dim08, agentes_skills_CONSOLIDADO.
Ronda 2 (Kimi): kimi_skills_K1..K6, kimi_skills_CROSSVERIF, kimi_skills_CONSOLIDADO.
Insumo: PROMPT_KIMI_SWARM_skills_v1 (prompt raiz del swarm Kimi).
