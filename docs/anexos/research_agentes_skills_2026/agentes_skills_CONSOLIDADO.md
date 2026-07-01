---
id: RESEARCH_AGENTES_SKILLS_CONSOLIDADO
version: 1.0
status: draft
visibility: [INTERNAL]
domain: research/agentes_skills_2026
category: generated_staging
date: 2026-06-01
author: investigador-tecnico (Cowork)
---

# Agent Skills (patron SKILL.md) - Consolidado de investigacion (junio 2026)

Sintesis cruzada de 8 sub-investigaciones (dim01..dim08). Cada dim tiene su propio .md con los bloques Claim/Source/URL/Date/Excerpt/Context/Confidence. Este documento NO repite los claims: hace tres cosas que ninguna dim individual puede hacer sola -> (1) clasifica el cuerpo de evidencia por tiers de confianza, (2) resuelve contradicciones y banderas metodologicas entre fuentes, (3) cruza las recomendaciones para dar un orden de incorporacion con dependencias explicitas.

Premisa verificada antes de arrancar: Medium es fetchable en texto completo con fecha de publicacion en `meta-article:published_time`, asi que el formato de citas con excerpts textuales es real y se cumplio. Excepcion metodologica importante en seccion 2.

---

## 1. Mapa de confianza por tiers

### TIER 1 - HIGH (convergencia oficial + multiples fuentes independientes)

Estos hallazgos estan anclados en docs oficiales de Anthropic y/o el blog de ingenieria, y corroborados por 2+ fuentes Medium/tecnicas. Se pueden tomar como base de decision sin reverificar.

| Hallazgo | Fuentes que convergen | dims |
|---|---|---|
| Skill = directorio con SKILL.md (frontmatter YAML `name`+`description` requeridos + cuerpo Markdown + recursos opcionales) | Anthropic Eng, Platform Docs, agentskills.io spec, Carrere, Paperclipped | 01,02,05,08 |
| Progressive disclosure de 3 niveles (metadata al arranque / cuerpo al activar / recursos via bash bajo demanda) | Anthropic Eng (fuente del termino), Platform Docs, SwirlAI, Pawar, skill-creator SKILL.md | 01,02,04,07,08 |
| Scripts ejecutan via bash y solo su output entra al contexto; el codigo NO consume tokens -> contexto bundleable "efectivamente ilimitado" | Anthropic Eng, Pawar, SwirlAI | 01,02,04 |
| Determinismo (script) vs no-determinismo (cuerpo interpretado por LLM); lo critico va en codigo | Anthropic Eng, Carrere, Firecrawl/Ville | 01,02,08 |
| Skill != Tool/MCP != Sub-agente != System prompt (capas distintas, se componen, no se sustituyen) | Carrere, Pawar, systemprompt.io, AI Architects | 01,03,08 |
| Estandar abierto publicado 18-dic-2025 (anuncio 16-oct-2025); adopcion cross-vendor (Codex, Copilot, VS Code, Cursor, Goose, Spring AI) | Anthropic Eng (nota oficial), Carrere, Paperclipped | 01,05,08 |
| Patron compuesto = default 2026: sub-agente Haiku + skill precargada (`skills:`) + MCP scoped | systemprompt.io, AI Architects (2 fuentes independientes convergen) | 03 |
| `context: fork` difumina la frontera skill/sub-agente (skill corre en sub-agente aislado) | mehdi.cz, alexop.dev | 03 |
| Solo el sub-agente da aislamiento real (contexto propio, modelo barato, tools restringidos); la skill hereda todo del padre | systemprompt.io, AI Architects, Carrere | 03,08 |
| Supply-chain inseguro by-design: skill hereda permiso completo del agente, sin firma/review/sandbox por defecto | Snyk ToxicSkills, arXiv 2510.26328, Anthropic Docs, Sathish Raju | 02,05,07,08 |
| Snyk: 36.82% de 3,984 skills con >=1 falla; 13.4% con issue critico; 76 payloads maliciosos confirmados | Snyk ToxicSkills (research con metodologia publicada) | 05,08 |
| Prompt injection "trivialmente simple": todo el SKILL.md es instruccion, las defensas de "instrucciones-en-datos" no aplican | arXiv 2510.26328 (paper academico, leido directo) | 08 |
| skill-creator: flujo Create/Eval/Improve/Benchmark con A/B vs baseline, 3 corridas/query, split 60/40 train/test | anthropics/skills skill-creator SKILL.md (485 lineas, leido directo) | 07 |
| La `description` es el mecanismo de triggering; el fallo dominante es "undertriggering" -> descripciones "pushy" | skill-creator SKILL.md, Firecrawl, Sathish Raju, SwirlAI | 01,02,07 |
| skills oficiales docx/xlsx/pptx/pdf existen en anthropics/skills (verificado: ya cargadas en este runtime) | Platform Docs, anthropics/skills, runtime propio | 01,06 |
| nexscope-ai/Amazon-Skills existe: 27 skills (6 production / 21 beta), MIT, soporta MX | GitHub (fetch directo verificado en consolidacion) | 06 |

### TIER 2 - MEDIUM (fuente unica fuerte, o medicion de autor no auditada)

Direccionalmente solidos, utiles para planear, pero NO citar como cifra dura sin reverificar.

- Mediciones de tokens de SwirlAI: metadata mediana ~80 tok/skill (rango 55-235), 17 skills = ~1,700 tok; cuerpo mediana ~2,000 tok (rango 275-8,000). Medicion del autor, no auditada por terceros. (dim02, dim04)
- "~100 tokens/skill" (Pawar) y "30-50 tokens/skill" (Firecrawl/morphllm): dispersos pero consistentes; la diferencia depende del largo real de la `description`. (dim01, dim03, dim04)
- Adopcion "32 herramientas en 90 dias" y paths divergentes por plataforma (`.claude/skills`, `.agents/skills`, `.github/skills/`, `~/.gemini/.../skills`). Fuente: Paperclipped citando a Simon Willison. (dim05)
- skills.sh (Vercel, 20-ene-2026, ~90k skills, 19 agentes) y plugin marketplace oficial Anthropic ~20-feb-2026 (55+ plugins curados). (dim05)
- Versionado: `version` NO es campo top-level del spec, va en `metadata`; pinning de plugins a commit-SHA es recomendacion, no garantia del estandar. (dim02, dim05)
- Capability skills vs Preference skills (Anthropic via The Tool Nerd); util para gobernanza (capability se deprecia si el modelo base mejora, preference es del tenant). (dim07)
- Routing a Haiku reduce ~60% del gasto Opus en tareas rutinarias (equipo de produccion systemprompt.io, no benchmark formal). (dim03)
- Anti-patron skill bloat / context rot: skill media ~1,900 tok pero cola pesada, top 1% >100k tok; 46.3% duplicados; "context rot" degrada baseline aunque este dentro del limite. (dim04)
- MarceauSolutions/amazon-seller-mcp existe y cubre SP-API (8 MCP tools, soporta MX/BR) PERO 1 commit / 1 star / v1.0.0 -> riesgo de mantenimiento alto. Verificado por fetch directo. (dim06)

### TIER 3 - LOW / [NO VERIFICADO] (no confirmable o contradice reglas internas)

No usar como base de decision. Listado para trazabilidad y para saber que reverificar si se vuelve load-bearing.

- Papers arXiv NO leidos en primario: 2602.08004 (Bosch/CMU, 40,285 skills, mediana 1,414 tok), 2602.12670 (SkillsBench), 2602.20156 (80% attack success). Todas las cifras derivadas heredan confianza baja. (NOTA: el prefijo 2602 implica feb-2026; coherente con la linea temporal, pero sin lectura directa del arXiv). dims 02,04,05,07
- Conteos de skills por marketplace: SkillsMP 500k+, LobeHub 100k+, SkillHub ~7k, agentskill.sh 44k+. Fuente unica (Virtual Uncle), sin cross-check. Tratar como orden de magnitud. (dim05)
- ClawHavoc: 335 (Virtual Uncle) vs 341 (Paperclipped) skills hostiles. Rango ~335-341. (dim05)
- Benchmark Augment Code "9K vs 15K tokens" (sub-agentes aislados vs skills que acumulan) y Newline/Dipen "25-40% menos tokens": snippets de buscador, paginas no recuperadas en cuerpo. (dim03)
- Jerarquia de memoria de 3 niveles (in-context / session-scoped / long-term vector+graph): snippet de WebSearch (mem0.ai), sin fetch directo. (dim04)
- Patrones multi-tenant silo/pool/bridge de AWS Bedrock AgentCore: sintesis de WebSearch, NO fetch directo. ADEMAS arrastra el antipatron "tenant via custom HTTP headers" que CONTRADICE la regla inquebrantable MWT (tenant fluye por context server-side, nunca por headers de cliente). Usar como taxonomia de patrones, rechazar el transporte. (dim08)
- "SKILL.md es proyecto formal del AAIF": NO confirmado. Los proyectos contribuidos al Agentic AI Foundation son MCP, AGENTS.md y Goose; la gobernanza de SKILL.md sigue de facto en agentskills.io (Anthropic). (dim05)
- Campos de frontmatter propietarios de Claude Code mas alla del spec base: `disable-model-invocation`, `paths`, `effort`, `context: fork`, `argument-hint`, `$ARGUMENTS`, `${CLAUDE_SKILL_DIR}`. Aparecen en Firecrawl/alexop.dev pero no en agentskills.io/specification. Tratar como extensiones de Claude Code, no estandar portable. (dim02, dim03, dim07)

---

## 2. Banderas metodologicas (leer antes de confiar en una dim concreta)

1. **dim03 no pudo fetchear Medium.** En esa sesion, todos los fetch a medium.com devolvieron cuerpo vacio (bloqueo server-side intermitente; dim01/dim02/dim04/dim05 si lograron fetchear Medium). dim03 compenso con fuentes tecnicas independientes de alta calidad recuperadas en full-text (systemprompt.io, theaiarchitects.com, mehdi.cz, alexop.dev, morphllm, callsphere) y marco como [NO VERIFICADO] lo que solo venia de snippets. Consecuencia: la cobertura "Medium primario" de dim03 es delgada, pero sus fuentes son solidas y verificadas. No es un defecto de rigor, es una sustitucion de fuente declarada.

2. **dim05 tiene varios excerpts via "WebSearch sintetizado".** Claims 2, 3, 11, 12 y 14 de dim05 citan paginas (cased/claude-code-plugins, morphllm, gHacks, Claude Code Docs, obra/superpowers) cuyo excerpt proviene de la sintesis del buscador, no de fetch directo linea-a-linea. El riesgo es que esos "Excerpt" sean parafrasis, no cita textual exacta. Marcados confidence medium por el propio agente. Reverificar por fetch antes de citarlos como verbatim.

3. **dim08 claim 15 (AWS multi-tenant) contradice una regla MWT.** El agente lo detecto y lo marco. Importante: la recomendacion final de dim08 YA corrige esto (rechaza tenant-via-headers explicitamente). No hay inconsistencia interna; la fuente externa es la que arrastra el antipatron.

4. **El unico arXiv leido en primario es 2510.26328** (prompt injection, dim08). Los otros tres ids arXiv son [NO VERIFICADO]. Cualquier cifra que cite "el estudio de 40k skills" debe llevar esa salvedad.

5. **Cero invencion de repos.** Los dos repos mas load-bearing del catalogo (nexscope-ai/Amazon-Skills y MarceauSolutions/amazon-seller-mcp) fueron verificados por fetch directo en la consolidacion: ambos existen y el conteo (27 skills) y cobertura (SP-API, MX) coinciden. Los repos restantes del dim06 (sales-skills/sales, alirezarezvani/claude-skills, czlonkowski/n8n-skills+n8n-mcp, anthropics/skills) quedan pendientes de spot-check antes de adoptar, pero anthropics/skills y czlonkowski son conocidos y de bajo riesgo.

---

## 3. Sintesis cruzada: que skills se refuerzan, que depende de que

El catalogo de dim06 (23 skills propuestas) cobra sentido real cuando se mapea con la arquitectura de dim01/dim03/dim08. Tres clusters con dependencias internas:

### Cluster A - Motor de documentos (base, sin dependencias)
`docx` + `xlsx` + `pptx` + `pdf` (oficiales Anthropic, ya cargadas).
- Son el **output engine** del que cuelgan: `cotizacion-calzado-industrial` (a2), `ficha-tecnica-modelo` (a4), `comparativo-modelos` (a5), y todo reporte de los frentes Amazon/B2B.
- Regla de no-duplicacion: la logica de documento vive aqui; las skills de dominio solo aportan los datos. No reescribir generacion de docx/xlsx dentro de otra skill.

### Cluster B - Amazon FBA (se refuerzan en cadena, datos en vivo aparte)
- `amazon-keyword-research` (b2) alimenta -> `amazon-listing-optimization` (b1).
- `amazon-review-analyzer` (b3) alimenta -> mejora de producto ergonomico Rana Walk y -> a1 (insumos de mensaje).
- b1-b6 razonan con datos publicos. La **capa de datos en vivo** es `sp-api-reports` (b7), que es un MCP, no una skill, y de la que dependen para no "razonar a ciegas".
- Dependencia critica + riesgo: b7 apunta a MarceauSolutions/amazon-seller-mcp (Tier 2, repo inmaduro de 1 commit). Decision: usarlo como **referencia de implementacion**, no como dependencia de produccion; envolver SP-API propio o forkear y mantener. `helium10-workflow` (b8) no tiene equivalente publico -> build propio via export CSV / n8n.

### Cluster C - Gobernanza KB + aislamiento (build propio, prerequisito de todo lo demas en multi-tenant)
- `tenant-guard` (dim08 Fase 1): logica de `tenant_id`/RLS/visibilidad en **script determinista**, no en prose. Es el #1 porque las skills comparten contexto y NO aislan tenants por diseno (Tier 1).
- `kb-frontmatter-validator` (d1), `kb-taxonomy-classifier` (d2), `kb-changelog-indexa` (d3), `kb-mirror-sync-author` (d4), `kb-visibility-guard` (d5): codifican las reglas inquebrantables MWT. Sin equivalente publico (son propietarias por definicion). d4 condensa lecciones de sync ya pagadas (ver MEMORY: ASCII puro, Push-Location a canonico, robocopy exit>=8, $LASTEXITCODE, Pop-Location seguro).
- `skill-review` (meta-skill): gate de supply-chain interno que checa SKILL.md entrantes contra la taxonomia de Snyk. Depende de la evidencia de Tier 1 sobre supply-chain.

Cruce clave: **Cluster C es prerequisito de gobernanza para incorporar nada de Cluster B/A en una plataforma multi-tenant.** No es el frente de mayor ROI comercial inmediato, pero es el que evita que un skill de marketplace (1-en-8 con issue critico) o una skill compartida mal aislada filtre datos entre tenants.

---

## 4. Orden de incorporacion recomendado (prescriptivo)

Derivado de cruzar ROI/esfuerzo de dim06 con los guardrails de dim08 y las dependencias de seccion 3. La logica: lo gratis-y-seguro primero, los guardrails de gobernanza en paralelo, la integracion pesada despues, el riesgo regulatorio al final.

| Orden | Que | Cluster | Build vs existente | Por que en este momento |
|---|---|---|---|---|
| **Fase 0** | Guardrails de plataforma: registry interno allowlisted, pin obligatorio a commit-hash, prohibir fetch remoto en runtime (`curl\|bash`), hardening de aprobaciones (no "Don't ask again" para red), sandbox de red allowlist | C (infra) | Build propio | No negociable. La evidencia Tier 1 muestra explotacion activa y barrera de publicacion nula. Sin esto, cualquier skill de terceros es riesgo no acotado. |
| **1** | Activar docx + xlsx oficiales | A | Existente | Cero build, ya cargadas. Motor de cotizaciones/fichas. |
| **2** | tenant-guard (script-first) | C | Build propio | Riesgo #1 multi-tenant; el estandar no lo resuelve. Va antes que cualquier skill compartida. |
| **3** | nexscope amazon: listing-optimization (b1) + keyword-research (b2) + review-analyzer (b3) | B | Existente (MIT, 27 skills, soporta MX, revisado) | Quick wins de alto ROI para Rana Walk; bajo riesgo, repo verificado. Pasan igual por el gate de Fase 0. |
| **4** | kb-frontmatter-validator (d1) + skill-review meta-skill | C | Build propio | Baratos, alto retorno de consistencia; skill-review cierra el gate de supply-chain interno. |
| **5** | kb-mirror-sync-author (d4) | C | Build propio | Cada sesion Cowork termina en sync; condensa lecciones ya pagadas. |
| **6** | cotizacion-calzado-industrial (a2) sobre xlsx | A+B2B | Build sobre existente | Toca cada deal del canal Colombia; ROI por operacion. |
| **7** | SP-API en vivo (b7): NO adoptar el MCP inmaduro como dependencia; envolver/forkear propio con multi-tenant + RLS | B | Build (referencia: amazon-seller-mcp) | Da sentido a b1-b6, pero el repo publico es 1-commit; tratar como referencia, no produccion. |
| **8** | helium10-workflow (b8), n8n-workflow-builder (d6), fichas/comparativos (a4/a5) | B/A | Mixto | Exprimir stack existente una vez probado el gate. |
| **Proyecto** | compliance-epp-latam (a3) | B2B | Build propio + validacion experta | ROI alto pero riesgo de alucinacion regulatoria; KB normativo curado, no quick win. Fuera del orden lineal. |

---

## 5. Recomendacion directa (juicio del analista)

Para una plataforma multi-tenant de agentes en produccion como la de MWT/FaberLoom, la conclusion que sale de cruzar las 8 dims es una y prescriptiva:

**Adoptar SKILL.md como capa de conocimiento INTERNO gobernado, nunca como canal de instalacion abierto desde marketplace.** El valor de las skills para ustedes es interno (consistencia, eficiencia de contexto via progressive disclosure, auditabilidad en Git, scripts deterministas para lo critico), no la libreria publica. La evidencia Tier 1 es inequivoca en dos puntos que definen la postura: (a) el ecosistema publico esta bajo ataque activo con ~1-en-8 probabilidad de issue critico y barrera de publicacion casi nula; (b) las skills comparten el contexto del agente y por diseno NO aislan tenants -el aislamiento real lo dan sub-agentes o MCP por proceso, no la skill.

De ahi, tres decisiones arquitectonicas que no deberian debatirse mas:

1. **Lo critico va en codigo, no en prose.** `tenant_id`, RLS, visibilidad (PUBLIC/PARTNER_B2B/INTERNAL/CEO-ONLY) y validaciones de compliance van en scripts deterministas bundleados, nunca en el cuerpo Markdown interpretado por LLM. El cuerpo es para el juicio contextual; el script para lo que debe ser repetible y auditable.

2. **Multi-tenancy por aislamiento de proceso, no por skill compartida.** Logica critica de negocio por tenant -> sub-agente o MCP scoped por tenant. Skills compartidas (pool) solo para conocimiento generico no sensible. El `tenant_id` fluye server-side por context, rechazando explicitamente el antipatron de tenant-via-headers que arrastra la guia AWS.

3. **Primero construir lo que codifica TUS reglas, no comprar lo del mercado.** Las primeras skills propias deben ser las de gobernanza (tenant-guard, kb-frontmatter-validator, skill-review, kb-mirror-sync-author): convierten un vector de supply-chain en un activo de gobernanza auditable. Las skills de Amazon de nexscope (MIT, verificadas) son el unico "comprado" de bajo riesgo que entra temprano, y aun asi pasa por el gate de Fase 0.

El patron tecnico a estandarizar internamente es el **compuesto 2026**: sub-agente Haiku + skill precargada (campo `skills:`) + MCP scoped. Da las tres dimensiones de scope que un multi-tenant necesita a la vez -scope de acceso (MCP), scope de costo (modelo) y scope de proposito/permisos (tools restringidos del sub-agente)- que una skill sola no puede dar.

---

## 6. Lo que queda sin resolver (vigilar)

- **No hay benchmark estandar de calidad de skills** (la industria mide por observability/traces, no por evals; gap 89% vs 52%). Implica construir tus propios evals con skill-creator desde el dia 1.
- **Versionado y dependencias entre skills sin estandar:** `version` no es top-level, no hay lockfile, skills con fetch remoto pueden mutar post-review. Pinning a commit-hash es manual.
- **Determinismo no declarable:** el spec no permite marcar "esta seccion DEBE ejecutarse como codigo". El unico determinismo viene de mover la logica a script; `allowed-tools` sigue experimental.
- **Gobernanza de terceros sin attestation/firma:** el escaneo con LLM hereda su propia superficie de jailbreak; es paliativo, no solucion.

---

## Indice de dimensiones

- agentes_skills_dim01.md - Que son las Skills (definicion, origen, Skill vs Tool/MCP/Sub-agente/Plugin/System prompt)
- agentes_skills_dim02.md - Arquitectura (SKILL.md, frontmatter, 3 tiers, versionado, scripts, determinista vs LLM)
- agentes_skills_dim03.md - Skills vs Sub-agentes (context: fork, patron compuesto, costo, paralelismo)
- agentes_skills_dim04.md - Skills + memoria + context engineering (KV-cache, prefijo estable, skill bloat)
- agentes_skills_dim05.md - Ecosistema / marketplaces (plugins, skills.sh, adopcion, supply-chain Snyk)
- agentes_skills_dim06.md - Catalogo de skills para incorporar (23 skills, 4 frentes, Top 8)
- agentes_skills_dim07.md - Construir y evaluar (skill-creator, evals, triggering, anti-patrones)
- agentes_skills_dim08.md - Hallazgos, tradeoffs, no resuelto, recomendacion multi-tenant
