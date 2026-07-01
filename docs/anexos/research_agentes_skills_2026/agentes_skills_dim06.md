---
id: RESEARCH_AGENTES_SKILLS_DIM06
version: 1.0
status: draft
visibility: [INTERNAL]
domain: research/agentes_skills_2026
category: generated_staging
date: 2026-06-01
author: investigador-tecnico (Cowork)
---

# dim06 — Catalogo de Skills para Incorporar (Agent Skills / patron SKILL.md)

## Resumen

Investigacion de skills CONCRETAS (patron `SKILL.md`, estandar abierto desde dic-2025, adoptado por Claude Code, Cowork, Codex y ChatGPT) para los 4 frentes de Muito Work Limitada: (a) ventas B2B calzado industrial, (b) e-commerce Amazon FBA, (c) generacion de documentos, (d) ops/gobernanza KB.

Hallazgo central: el ecosistema de skills publicas maduro a junio-2026. Para **documentos** y **Amazon FBA** existen catalogos publicos verificables que cubren la mayoria de necesidades casi sin build. Para **ventas B2B de EPP/calzado de seguridad con compliance LATAM** y para **gobernanza del KB MWT** (frontmatter, taxonomia, sync) NO hay equivalente publico que encaje — son build propio. Esto es esperable: ambos encierran conocimiento propietario (normas EPP por pais, reglas inquebrantables MWT, protocolo sync canonico).

**Total: 23 skills propuestas. 13 con equivalente publico verificado (reusar/forkear). 10 build propio sin equivalente publico verificado.**

Convencion de evidencia: claims de hechos usan bloque Claim/Source. Recomendaciones de build llevan `[RECOMENDACION — juicio del analista]`.

---

### Evidencia base del ecosistema (claims verificados)

**Claim:** Anthropic publica skills oficiales para docx, xlsx, pptx y pdf en su repo publico.
**Source:** anthropics/skills (GitHub) — subcarpetas `skills/docx`, `skills/xlsx`, `skills/pptx`, `skills/pdf`
**URL:** https://github.com/anthropics/skills
**Date:** consultado 2026-06-01
**Excerpt:** "the document creation & editing skills that power Claude's document capabilities in the skills/docx, skills/pdf, skills/pptx, and skills/xlsx subfolders". Instalables via `/plugin install document-skills@anthropic-agent-skills`. Licencia source-available (no Apache 2.0 como el resto del repo).
**Context:** Son exactamente las mismas skills que el entorno Cowork de MWT ya tiene cargadas (anthropic-skills:docx, :xlsx, :pptx, :pdf). Confirmado en este mismo runtime.
**Confidence:** Alta.

**Claim:** Existe catalogo publico de skills para vendedores Amazon (keyword research, listing, FBA, PPC, review analysis, competencia).
**Source:** nexscope-ai/Amazon-Skills (GitHub), licencia MIT
**URL:** https://github.com/nexscope-ai/Amazon-Skills
**Date:** consultado 2026-06-01
**Excerpt:** 27 skills (6 production-ready / 21 beta): amazon-keyword-research, amazon-listing-optimization (audit + 8-dimension scoring + competitor ASIN), amazon-fba-calculator, amazon-ppc-campaign, amazon-review-analyzer, amazon-competitor-analysis, amazon-sales-estimator, etc. 12 marketplaces incluido MX. Instala con `npx skills add nexscope-ai/Amazon-Skills`.
**Context:** Usan "publicly available data — no API key". NO se conectan a SP-API; son skills de razonamiento/prompt, no de integracion de datos en vivo. Para datos en vivo se necesita un MCP SP-API aparte.
**Confidence:** Alta.

**Claim:** Existe MCP server publico para Amazon Seller Central via SP-API operable desde Claude.
**Source:** MarceauSolutions/amazon-seller-mcp (GitHub)
**URL:** https://github.com/MarceauSolutions/amazon-seller-mcp
**Date:** consultado 2026-06-01
**Excerpt:** "Amazon Seller Central operations via SP-API - MCP server for Claude Desktop ... Core SP-API client, FBA fee calculations, inventory optimizer, OAuth server".
**Context:** Esto es un MCP (capa de datos en vivo), no una skill. Las skills de Amazon (arriba) razonan; el MCP trae reports/inventory/pricing reales de la cuenta. Se complementan.
**Confidence:** Media-alta (verificar mantenimiento y cobertura de endpoints antes de adoptar).

**Claim:** Existen skills publicas de ventas/outbound B2B y de cold email.
**Source:** sales-skills/sales (GitHub) y alirezarezvani/claude-skills (marketing-skill/cold-email)
**URL:** https://github.com/sales-skills/sales — https://github.com/alirezarezvani/claude-skills/blob/main/marketing-skill/cold-email/SKILL.md
**Date:** consultado 2026-06-01
**Excerpt:** sales-skills cubre "CRM, outbound, note-takers, enrichment, email marketing". cold-email se dispara con "cold outreach, prospecting emails, SDR emails, follow-up sequence" y busca emails "that sound like a thoughtful human ... and actually get replies".
**Context:** Utiles como base de outreach generico. NINGUNA contiene conocimiento de EPP/calzado de seguridad ni compliance LATAM — eso es la capa propietaria a construir encima.
**Confidence:** Alta.

**Claim:** Existen skills publicas para construir/depurar workflows n8n y un MCP n8n.
**Source:** czlonkowski/n8n-skills y czlonkowski/n8n-mcp (GitHub)
**URL:** https://github.com/czlonkowski/n8n-skills — https://github.com/czlonkowski/n8n-mcp
**Date:** consultado 2026-06-01
**Excerpt:** n8n-skills = "n8n skillset for Claude Code to build flawless n8n workflows" (7 skills complementarias); n8n-mcp expone "1,851 workflow automation nodes".
**Context:** Relevante para automatizar el pegamento entre Amazon, Drive, KB y los agentes MWT. No es de los 4 frentes core pero habilita los sync/ops.
**Confidence:** Alta.

---

## (a) Ventas / Representacion B2B — calzado industrial (Marluvas, Tecmater)

Aqui el ecosistema publico aporta el "esqueleto" de outreach/CRM, pero todo el valor diferencial (normas EPP por pais, fichas tecnicas de modelo, comparativos) es propietario.

| # | Skill | Equiv. publico | Complejidad | ROI | Dependencias |
|---|-------|----------------|-------------|-----|--------------|
| a1 | outreach-b2b-epp | Parcial (sales-skills/sales, cold-email) | Baja-media | Alto | KB ENT_COMERCIAL_CLIENTES; opcional MCP CRM |
| a2 | cotizacion-calzado-industrial | Build propio | Media | Alto | xlsx skill; ENT pricing/listas |
| a3 | compliance-epp-latam | Build propio [NO VERIFICADO] | Alta | Alto | KB normativo (build) |
| a4 | ficha-tecnica-modelo | Build propio | Media | Medio | docx/pdf skill; ENT catalogo Marluvas/Tecmater |
| a5 | comparativo-modelos | Build propio | Baja-media | Medio | xlsx skill; a4 |

**a1 — outreach-b2b-epp.** Secuencias de prospeccion a distribuidores/compradores de seguridad industrial en Colombia, contextualizadas al pitch MWT como representante. *Build vs existente:* forkear `sales-skills/sales` + `cold-email` y sobreponer ICP de EPP. *Complejidad:* baja-media. *ROI:* alto — habilita el canal nuevo Colombia. *Dependencias:* perfiles en `ENT_COMERCIAL_CLIENTES`; opcional MCP de CRM/email.

**a2 — cotizacion-calzado-industrial.** Genera cotizacion estructurada (modelo, talla, norma cumplida, precio, lead time, Incoterm) en xlsx/pdf. *Build vs existente:* `[RECOMENDACION — juicio del analista]` build propio; la skill xlsx oficial es el motor de salida, la logica de pricing y line-items es MWT. *Complejidad:* media. *ROI:* alto — toca cada deal. *Dependencias:* skill xlsx oficial; listas de precio en KB.

**a3 — compliance-epp-latam.** Mapea modelo de calzado contra normas aplicables (p.ej. familias EN ISO 20345 / ASTM F2413 / NTC colombianas) y marca gaps de certificacion para importar MX->CO. *Build vs existente:* `build propio — sin equivalente publico verificado [NO VERIFICADO]`. *Complejidad:* alta (requiere construir el KB normativo y validarlo con un experto; riesgo de alucinacion regulatoria — no inventar). *ROI:* alto — el compliance es barrera de entrada y diferenciador. *Dependencias:* base normativa curada (build).

**a4 — ficha-tecnica-modelo.** Produce ficha tecnica comercial por modelo (materiales, protecciones, certificaciones, casos de uso) en docx/pdf. *Build vs existente:* build propio sobre skill docx/pdf oficial. *Complejidad:* media. *ROI:* medio. *Dependencias:* docx/pdf oficiales; catalogo en KB; idealmente a3 para la fila de normas.

**a5 — comparativo-modelos.** Tabla comparativa multi-modelo (propio vs competencia o entre lineas Marluvas/Tecmater) para cerrar venta consultiva. *Build vs existente:* build propio. *Complejidad:* baja-media. *ROI:* medio. *Dependencias:* xlsx oficial; reutiliza datos de a4.

---

## (b) E-commerce Amazon FBA (Rana Walk)

Frente con MEJOR cobertura publica. La mayoria son reusar/forkear desde nexscope-ai/Amazon-Skills. La pieza que falta es la capa de datos en vivo (SP-API / Helium 10), que es MCP, no skill.

| # | Skill | Equiv. publico | Complejidad | ROI | Dependencias |
|---|-------|----------------|-------------|-----|--------------|
| b1 | amazon-listing-optimization | Si (nexscope-ai) | Baja | Alto | — (skill standalone) |
| b2 | amazon-keyword-research | Si (nexscope-ai) | Baja | Alto | opcional Helium 10 |
| b3 | amazon-review-analyzer | Si (nexscope-ai) | Baja | Alto | — |
| b4 | amazon-competitor-analysis | Si (nexscope-ai) | Baja | Medio | — |
| b5 | amazon-fba-calculator | Si (nexscope-ai) | Baja | Medio | — |
| b6 | amazon-ppc-campaign | Si (nexscope-ai) | Baja | Medio | — |
| b7 | sp-api-reports (datos en vivo) | MCP, no skill (MarceauSolutions) | Alta | Alto | SP-API creds; MCP |
| b8 | helium10-workflow | Build propio [NO VERIFICADO] | Media | Medio | export H10 / MCP H10 |

**b1 — amazon-listing-optimization.** Crea o audita listings con scoring 8-dimensiones y analisis de ASIN competidor. *Build vs existente:* **existente — usar tal cual** `nexscope-ai/Amazon-Skills/amazon-listing-optimization` (production-ready, MIT). *Complejidad:* baja (instalar). *ROI:* alto — impacto directo en conversion Rana Walk. *Dependencias:* ninguna; soporta marketplace MX/US.

**b2 — amazon-keyword-research.** Mineria de long-tail desde autocomplete, competencia, estacionalidad. *Build vs existente:* existente (nexscope-ai). *Complejidad:* baja. *ROI:* alto. *Dependencias:* opcional Helium 10 para volumenes reales (la skill sola usa datos publicos).

**b3 — amazon-review-analyzer.** Sentiment, quejas recurrentes, feature requests de reviews propias y de competencia. *Build vs existente:* existente (nexscope-ai). *Complejidad:* baja. *ROI:* alto — feedback de producto para plantillas ergonomicas. *Dependencias:* ninguna.

**b4 — amazon-competitor-analysis.** Analisis de listing/pricing/reviews/ads de competidores. *Build vs existente:* existente (nexscope-ai, beta). *Complejidad:* baja. *ROI:* medio. *Dependencias:* ninguna.

**b5 — amazon-fba-calculator.** Desglose de fees y margen neto. *Build vs existente:* existente (nexscope-ai, production-ready). *Complejidad:* baja. *ROI:* medio. *Dependencias:* ninguna.

**b6 — amazon-ppc-campaign.** Estructura campañas PPC, calcula ACoS objetivo, agrupa keywords. *Build vs existente:* existente (nexscope-ai, production-ready). *Complejidad:* baja. *ROI:* medio. *Dependencias:* ninguna.

**b7 — sp-api-reports (capa de datos en vivo).** Trae inventory, pricing y reports reales de la cuenta Seller Central. *Build vs existente:* **es un MCP, no una skill** — adoptar `MarceauSolutions/amazon-seller-mcp` y envolverlo en una skill fina que oriente al agente sobre que reports pedir. *Complejidad:* alta (OAuth SP-API, roles, rate limits). *ROI:* alto — sin datos en vivo las skills b1-b6 razonan a ciegas. *Dependencias:* credenciales SP-API; MCP corriendo; multi-tenant (un set de creds por tenant, RLS).

**b8 — helium10-workflow.** Orquesta exports de Helium 10 (Cerebro/Magnet/Black Box) hacia el flujo de keyword/listing. *Build vs existente:* `build propio — sin skill ni MCP H10 publico verificado [NO VERIFICADO]`. *Complejidad:* media (H10 no expone API abierta amplia; probablemente via export CSV). *ROI:* medio — H10 ya esta en el stack, vale exprimirlo. *Dependencias:* export H10 o automatizacion n8n.

---

## (c) Generacion de documentos

Frente RESUELTO por Anthropic. No construir nada; instalar las skills oficiales. Ya estan cargadas en el Cowork de MWT.

| # | Skill | Equiv. publico | Complejidad | ROI | Dependencias |
|---|-------|----------------|-------------|-----|--------------|
| c1 | docx (oficial Anthropic) | Si — oficial | Baja | Alto | — |
| c2 | xlsx (oficial Anthropic) | Si — oficial | Baja | Alto | — |
| c3 | pptx (oficial Anthropic) | Si — oficial | Baja | Medio | — |
| c4 | pdf (oficial Anthropic) | Si — oficial | Baja | Medio | — |

**c1-c4 — docx / xlsx / pptx / pdf.** Crear/editar Word, Excel, PowerPoint, PDF con formato profesional (TOC, headers, tablas, charts sin errores de formula, OCR, merge/split). *Build vs existente:* **existentes — oficiales Anthropic** (`anthropics/skills`, source-available). Ya disponibles en este runtime como `anthropic-skills:docx/:xlsx/:pptx/:pdf`. *Complejidad:* baja (cero build). *ROI:* alto para xlsx/docx (cotizaciones a2, fichas a4, reportes Amazon); medio para pptx/pdf. *Dependencias:* ninguna. *Nota:* son el motor de salida de a2, a4, a5 y de los reportes de los frentes a/b — no duplicar logica de documentos en otras skills.

---

## (d) Ops / Gobernanza de KB

Frente 100% build propio: encierra las reglas inquebrantables MWT, la taxonomia de 8 tipos, los headers obligatorios y el protocolo sync canonico. NO existe skill publica que conozca estas reglas (por definicion son propietarias). El unico apoyo externo es n8n para el pegamento de automatizacion.

| # | Skill | Equiv. publico | Complejidad | ROI | Dependencias |
|---|-------|----------------|-------------|-----|--------------|
| d1 | kb-frontmatter-validator | Build propio [NO VERIFICADO] | Baja-media | Alto | reglas headers MWT |
| d2 | kb-taxonomy-classifier | Build propio [NO VERIFICADO] | Media | Alto | taxonomia 8 tipos |
| d3 | kb-changelog-indexa | Build propio [NO VERIFICADO] | Media | Alto | MANIFIESTO_CAMBIOS_v2 |
| d4 | kb-mirror-sync-author | Build propio [NO VERIFICADO] | Alta | Alto | sync_*_indexa.ps1; PowerShell |
| d5 | kb-visibility-guard | Build propio [NO VERIFICADO] | Media | Alto | reglas PUBLIC/.../CEO-ONLY |
| d6 | n8n-workflow-builder | Si (czlonkowski/n8n-skills) | Media | Medio | n8n-mcp |

**d1 — kb-frontmatter-validator.** Valida que ENT/PLB/POL/SCH/LOC/IDX/SKILL tengan `id`, `version`, `status`, `visibility`, `domain` antes de promover. *Build vs existente:* `build propio — sin equivalente publico verificado [NO VERIFICADO]`; las skills genericas de frontmatter validan name/description de SKILL.md, no el schema MWT. *Complejidad:* baja-media. *ROI:* alto — previene el error mas comun de indexado. *Dependencias:* reglas headers (CLAUDE.md/WIKI.md).

**d2 — kb-taxonomy-classifier.** Sugiere el tipo correcto (ENT vs PLB vs SCH...) y bloquea mezclas de tipo. *Build vs existente:* build propio [NO VERIFICADO]. *Complejidad:* media. *ROI:* alto — la taxonomia es columna vertebral del KB. *Dependencias:* definicion de los 8 tipos + especiales.

**d3 — kb-changelog-indexa.** Genera changelog del archivo + append a `MANIFIESTO_CAMBIOS_v2` siguiendo POL_EPHEMERAL_OUTPUT (BATCH directo, sin MANIFIESTO_APPEND fisico; metadatos-only si el archivo es CEO-ONLY). *Build vs existente:* build propio [NO VERIFICADO]. *Complejidad:* media. *ROI:* alto — automatiza paso obligatorio y propenso a olvido. *Dependencias:* convenciones de commit MWT; memoria de reglas indexado.

**d4 — kb-mirror-sync-author.** Genera `sync_<tema>_indexa.ps1` correcto: Copy-Item explicito, Push-Location a canonico, ASCII puro, robocopy exit >=8 como fallo, validar por $LASTEXITCODE (no ErrorActionPreference Stop), Pop-Location seguro. *Build vs existente:* `build propio — sin equivalente publico verificado [NO VERIFICADO]`; condensa varias lecciones ya aprendidas (ver MEMORY). *Complejidad:* alta (muchos gotchas PowerShell 5 / OneDrive). *ROI:* alto — cada sesion Cowork termina en un sync; los errores cuestan tiempo. *Dependencias:* mirror_to_onedrive.ps1; PowerShell Windows. *Nota gobernanza:* NO puede tocar `control_surface` (hooks/*).

**d5 — kb-visibility-guard.** Verifica que contenido CEO-ONLY no se filtre a archivos PUBLIC/INTERNAL sin `ceo_only_sections`, y que el append a CAMBIOS_v2 sobre CEO-ONLY sea solo metadatos. *Build vs existente:* build propio [NO VERIFICADO]. *Complejidad:* media. *ROI:* alto — riesgo de fuga de datos sensibles (EEFF, cedulas). *Dependencias:* matriz de visibilidad MWT.

**d6 — n8n-workflow-builder.** Construye/depura workflows n8n (sync Amazon->Drive->KB, alertas). *Build vs existente:* **existente — usar** `czlonkowski/n8n-skills` (7 skills) + `n8n-mcp`. *Complejidad:* media (instalar MCP). *ROI:* medio. *Dependencias:* n8n-mcp; instancia n8n.

---

## Top 8 priorizado global

Criterio: ROI alto x esfuerzo bajo primero; luego habilitadores de alto valor aunque cuesten mas.

| Rank | Skill | Frente | Build vs existente | Complejidad | ROI | Por que ahora |
|------|-------|--------|--------------------|-------------|-----|---------------|
| 1 | docx + xlsx (c1, c2) | docs | **Existente oficial** | Baja | Alto | Cero build, ya cargadas; motor de cotizaciones y fichas. Activar ya. |
| 2 | amazon-listing-optimization (b1) | FBA | **Existente** (nexscope) | Baja | Alto | Production-ready, MIT, soporta MX. Impacto directo en ventas Rana Walk. |
| 3 | amazon-keyword-research (b2) | FBA | **Existente** (nexscope) | Baja | Alto | Alimenta b1; quick win. |
| 4 | kb-frontmatter-validator (d1) | ops | Build propio | Baja-media | Alto | Previene el error de indexado mas frecuente; barato de construir. |
| 5 | amazon-review-analyzer (b3) | FBA | **Existente** (nexscope) | Baja | Alto | Voz de cliente -> mejora de producto ergonomico. |
| 6 | cotizacion-calzado-industrial (a2) | B2B | Build sobre xlsx oficial | Media | Alto | Toca cada deal del canal Colombia; ROI por operacion. |
| 7 | kb-mirror-sync-author (d4) | ops | Build propio | Alta | Alto | Cada sesion Cowork termina en sync; condensa lecciones ya pagadas. |
| 8 | sp-api-reports / amazon-seller-mcp (b7) | FBA | **Existente** (MCP) + skill fina | Alta | Alto | Datos en vivo que dan sentido a b1-b6; multi-tenant con RLS. |

**Lectura estrategica:** arranca con lo gratis-y-listo (1-3, 5), construye en paralelo las dos piezas de gobernanza baratas y de alto retorno (4, 7), y reserva los proyectos de integracion (8 SP-API, mas adelante a3 compliance EPP) para cuando haya ancho de banda. compliance-epp-latam (a3) queda fuera del Top 8 por complejidad/riesgo regulatorio pese a su ROI alto: requiere KB normativo curado y validacion experta — planear como proyecto, no como quick win.

---

## Fuentes

- anthropics/skills (docx/xlsx/pptx/pdf oficiales) — https://github.com/anthropics/skills
- nexscope-ai/Amazon-Skills (27 skills FBA, MIT) — https://github.com/nexscope-ai/Amazon-Skills
- MarceauSolutions/amazon-seller-mcp (SP-API MCP) — https://github.com/MarceauSolutions/amazon-seller-mcp
- sales-skills/sales (outbound/CRM) — https://github.com/sales-skills/sales
- alirezarezvani/claude-skills (cold-email) — https://github.com/alirezarezvani/claude-skills
- czlonkowski/n8n-skills + n8n-mcp — https://github.com/czlonkowski/n8n-skills / https://github.com/czlonkowski/n8n-mcp
- SKILL.md spec / frontmatter — https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Marketplaces de descubrimiento — https://skillsmp.com / https://github.com/VoltAgent/awesome-agent-skills

> Nota de no-invencion: las skills marcadas `[NO VERIFICADO]` son recomendaciones de build propio del analista; no se encontro repo/skill publico que las cubra. No se inventaron nombres de repos ni skills. Verificar mantenimiento de amazon-seller-mcp y cobertura real de endpoints SP-API antes de comprometer el frente b7.
