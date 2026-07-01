# Inventario Priorizado de Agent Skills para MWT y FaberLoom

## Fecha: 2026-05-01
## Ejecutor: Kimi K2.5 Swarm — 12 dimensiones paralelas + consolidación

---

## DIMENSIÓN 1 — Workflow & Disciplina de Agentes

### Skills relevantes (consolidadas)

| Skill | Repo | Instalación | Score MWT | Score FB | Aplica también en |
|---|---|---|---|---|---|
| `ask-questions-if-underspecified` | trailofbits/skills | `npx skills add trailofbits/skills -s ask-questions-if-underspecified` | ALTO | ALTO | — |
| `planning` | iliaal/ai-skills | `npx skills add iliaal/ai-skills -s planning` | ALTO | ALTO | — |
| `reflect` | iliaal/ai-skills | `npx skills add iliaal/ai-skills -s reflect` | ALTO | ALTO | — |
| `file-todos` | iliaal/ai-skills | `npx skills add iliaal/ai-skills -s file-todos` | ALTO | ALTO | — |
| `code-review` | iliaal/ai-skills | `npx skills add iliaal/ai-skills -s code-review` | ALTO | ALTO | — |
| `sdd:plan` | neolabhq/context-engineering-kit | `npx skills add neolabhq/context-engineering-kit` | ALTO | ALTO | — |
| `sdd:implement` | neolabhq/context-engineering-kit | `npx skills add neolabhq/context-engineering-kit` | ALTO | ALTO | — |
| `reflexion:reflect` | neolabhq/context-engineering-kit | `npx skills add neolabhq/context-engineering-kit` | ALTO | ALTO | — |
| `tdd` | mattpocock/skills | `npx skills add mattpocock/skills -s tdd` | ALTO | ALTO | D10 |
| `qa` | mattpocock/skills | `npx skills add mattpocock/skills -s qa` | ALTO | ALTO | — |
| `prd-to-plan` | mattpocock/skills | `npx skills add mattpocock/skills -s prd-to-plan` | ALTO | ALTO | — |
| `prd-to-issues` | mattpocock/skills | `npx skills add mattpocock/skills -s prd-to-issues` | ALTO | ALTO | — |
| `triage` | mattpocock/skills | `npx skills add mattpocock/skills -s triage` | ALTO | ALTO | — |
| `eval-audit` | hamelsmu/evals-skills | `npx skills add hamelsmu/evals-skills -s eval-audit` | ALTO | ALTO | D10 |
| `error-analysis` | hamelsmu/evals-skills | `npx skills add hamelsmu/evals-skills -s error-analysis` | ALTO | ALTO | D10 |
| `write-judge-prompt` | hamelsmu/evals-skills | `npx skills add hamelsmu/evals-skills -s write-judge-prompt` | ALTO | ALTO | D10 |
| `model-hierarchy` | zscole/model-hierarchy-skill | `npx skills add zscole/model-hierarchy-skill` | ALTO | ALTO | D9 |
| `clawsec-suite` | prompt-security/clawsec | `npx skills add prompt-security/clawsec` | ALTO | ALTO | — |
| `condition-based-waiting` | obra/superpowers-skills | `npx skills add obra/superpowers-skills` | ALTO | ALTO | — |
| `review` | garrytan/gstack | `npx skills add garrytan/gstack -s review` | ALTO | ALTO | D10 |

### Gaps detectados (skills propias a escribir)

| Nombre propuesto | Justificación | Para | Prioridad |
|---|---|---|---|
| `mwt/agent-regression-suite` | No existe skill pura de regression testing para agentes coding con trazas. | Ambos | ALTA |
| `mwt/cost-governance-skill` | Solo model-hierarchy cubre routing. No hay rate limiting, quota tracking, budget alerts. | Ambos | ALTA |
| `mwt/handoff-contract-skill` | No existe skill de handoff contracts con schemas formales de input/output. | FB | ALTA |
| `mwt/agent-observability-skill` | No hay skill de observabilidad de agentes (logs estructurados, trazas, métricas). | Ambos | MEDIO |
| `mwt/kb-refresh-governance` | MWT tiene 430 archivos. No hay skill de governance de KB (refresh, archival, freshness). | MWT | MEDIO |
| `mwt/tenant-isolation-governance` | FaberLoom tiene 4 capas de visibilidad. No hay skill de tenant isolation governance. | FB | ALTA |

### Caveats técnicos

- obra/superpowers vs obra/superpowers-skills son repos SEPARADOS. El primero ya está instalado (14 skills, 921.7K installs). El segundo tiene 31 skills adicionales (439 installs). No hay conflicto de paths.
- NeoLabHQ context-engineering-kit tiene 133 skills en un solo repo. Instalación monolítica que carga 133 descripciones en startup. Monitorear trigger precision.
- mattpocock/skills tiene 365.3K installs. Algunas skills son opinionadas (`grill-me`, `caveman`). Recomendación: instalar selectivamente con `-s <skill>`.
- garrytan/gstack tiene 53 skills diseñados para un equipo de ingeniería virtual completo. Skills como `office-hours` requieren `AGENTS.md` de contexto previo.
- prompt-security/clawsec: priorizar `clawsec-suite`, `openclaw-audit-watchdog`, `soul-guardian`. Skills con <15 installs pueden ser inmaduras.

---

## DIMENSIÓN 2 — Marketing, SEO, Copy, CRO

### Skills relevantes (consolidadas)

| Skill | Repo | Instalación | Score MWT | Score FB | Aplica también en |
|---|---|---|---|---|---|
| `copywriting` | coreyhaines31/marketingskills | `npx skills add coreyhaines31/marketingskills --skill copywriting` | ALTO | ALTO | — |
| `cold-email` | coreyhaines31/marketingskills | `npx skills add coreyhaines31/marketingskills --skill cold-email` | ALTO | ALTO | D8 |
| `pricing-strategy` | coreyhaines31/marketingskills | `npx skills add coreyhaines31/marketingskills --skill pricing-strategy` | ALTO | ALTO | D4 |
| `product-marketing-context` | coreyhaines31/marketingskills | `npx skills add coreyhaines31/marketingskills --skill product-marketing-context` | ALTO | ALTO | — |
| `amazon-listing-optimization` | nexscope-ai/Amazon-Skills | `npx skills add nexscope-ai/Amazon-Skills --skill amazon-listing-optimization -g` | ALTO | MEDIO | D5 |
| `amazon-keyword-research` | nexscope-ai/Amazon-Skills | `npx skills add nexscope-ai/Amazon-Skills --skill amazon-keyword-research -g` | ALTO | MEDIO | D5 |
| `amazon-fba-calculator` | nexscope-ai/Amazon-Skills | `npx skills add nexscope-ai/Amazon-Skills --skill amazon-fba-calculator -g` | ALTO | BAJO | D5 |
| `amazon-search-optimization` | nexscope-ai/Amazon-Skills | `npx skills add nexscope-ai/Amazon-Skills --skill amazon-search-optimization -g` | ALTO | BAJO | — |
| `amazon-a-plus-content` | nexscope-ai/Amazon-Skills | `npx skills add nexscope-ai/Amazon-Skills --skill amazon-a-plus-content -g` | ALTO | BAJO | — |
| `amazon-listing-images` | nexscope-ai/Amazon-Skills | `npx skills add nexscope-ai/Amazon-Skills --skill amazon-listing-images -g` | ALTO | BAJO | — |
| `sales-enablement` | coreyhaines31/marketingskills | `npx skills add coreyhaines31/marketingskills --skill sales-enablement` | ALTO | MEDIO | — |
| `competitor-profiling` | coreyhaines31/marketingskills | `npx skills add coreyhaines31/marketingskills --skill competitor-profiling` | ALTO | MEDIO | — |
| `customer-research` | coreyhaines31/marketingskills | `npx skills add coreyhaines31/marketingskills --skill customer-research` | ALTO | MEDIO | — |
| `email-sequence` | coreyhaines31/marketingskills | `npx skills add coreyhaines31/marketingskills --skill email-sequence` | MEDIO | ALTO | D8 |
| `seo-audit` | coreyhaines31/marketingskills | `npx skills add coreyhaines31/marketingskills --skill seo-audit` | MEDIO | ALTO | — |
| `schema-markup` | coreyhaines31/marketingskills | `npx skills add coreyhaines31/marketingskills --skill schema-markup` | MEDIO | ALTO | — |
| `page-cro` | coreyhaines31/marketingskills | `npx skills add coreyhaines31/marketingskills --skill page-cro` | MEDIO | ALTO | — |
| `ab-test-setup` | coreyhaines31/marketingskills | `npx skills add coreyhaines31/marketingskills --skill ab-test-setup` | MEDIO | ALTO | — |
| `claude-seo` | AgriciDaniel/claude-seo | `git clone --depth 1 https://github.com/AgriciDaniel/claude-seo.git && bash claude-seo/install.sh` | MEDIO | ALTO | — |
| `seo-geo-claude-skills` | aaron-he-zhu/seo-geo-claude-skills | `npx skills add aaron-he-zhu/seo-geo-claude-skills` | MEDIO | ALTO | — |

### Gaps detectados (skills propias a escribir)

| Nombre propuesto | Justificación | Para | Prioridad |
|---|---|---|---|
| `amazon-latam-listing` | Ninguna skill cubre Amazon México, Brasil, Colombia. Rana Walk necesita español neutro/portugués. | MWT | ALTA |
| `b2b-industrial-outreach-latam` | No existe cold outreach B2B específico para LATAM industrial (calzado, EPP). | MWT | ALTA |
| `pricing-b2b-distribution` | Pricing-strategy existente es 100% SaaS-centric. No cubre pricing B2B distribución industrial. | MWT | ALTA |
| `faberloom-positioning` | FaberLoom necesita documento de posicionamiento específico vs competidores genéricos. | FB | ALTA |
| `landing-saas-latam` | Landing page skill existente genera TSX/Tailwind genérico. Falta copy LATAM, precios MXN/COP/CLP. | FB | MEDIA |
| `seo-local-latam` | Ninguna skill de SEO cubre SEO local para LATAM (Google My Business español, citas locales). | FB | MEDIA |

### Caveats técnicos

- Instalación múltiple de coreyhaines31/marketingskills: 30+ skills en subdirectorios. Se puede instalar completo o skill-by-skill.
- AgriciDaniel/claude-seo requiere Python 3.10+ y puede conflictuar con paths de `anthropic-skills/seo` si existe.
- aaron-he-zhu/seo-geo-claude-skills usa shell scripts 100% (no Python). Requiere compatibilidad con Agent Skills spec.
- nexscope-ai/Amazon-Skills: 51 skills, muchas en Beta. Available (✅): amazon-keyword-research, amazon-listing-optimization, amazon-fba-calculator, amazon-ppc-campaign, amazon-sales-estimator, tariff-calculator-amazon.
- Sin skills nativas en español/portugués. Todas las skills están en inglés. Requiere prompts de contexto explícitos.

---

## DIMENSIÓN 3 — Browser Automation, Scraping, Research

### Skills relevantes (consolidadas)

| Skill | Repo | Instalación | Score MWT | Score FB | Aplica también en |
|---|---|---|---|---|---|
| `agent-browser` | vercel-labs/agent-browser | `npx skills add vercel-labs/agent-browser` | ALTO | ALTO | — |
| `browser-use` | browser-use/browser-use | `npx skills add browser-use/browser-use@browser-use` | ALTO | ALTO | — |
| `browserbase/skills` | browserbase/skills | `npx skills add browserbase/skills` | ALTO | ALTO | — |
| `apify-ecommerce` | apify/agent-skills | `npx skills add apify/agent-skills` | ALTO | MEDIO | — |
| `apify-competitor-intelligence` | apify/awesome-skills | `npx skills add apify/awesome-skills` | ALTO | MEDIO | — |
| `competitor-price-tracker` | onewave-ai/claude-skills | `npx skills add onewave-ai/claude-skills --skill competitor-price-tracker` | ALTO | MEDIO | — |
| `tavily-research` | tavily-ai/skills | `npx skills add tavily-ai/skills --all` | MEDIO | ALTO | — |
| `firecrawl-scrape` | firecrawl/cli | `npx skills add firecrawl/cli --skill firecrawl-scrape` | MEDIO | ALTO | — |
| `firecrawl-crawl` | firecrawl/cli | `npx skills add firecrawl/cli --skill firecrawl-crawl` | MEDIO | ALTO | — |
| `deep-research-199bio` | 199-biotechnologies/claude-deep-research-skill | `git clone https://github.com/199-biotechnologies/claude-deep-research-skill.git ~/.claude/skills/deep-research` | MEDIO | ALTO | — |
| `apify-brand-reputation-monitoring` | apify/awesome-skills | `npx skills add apify/awesome-skills` | MEDIO | ALTO | — |
| `last30days` | mvanhorn/last30days-skill | `/plugin marketplace add mvanhorn/last30days-skill` | MEDIO | MEDIO | — |
| `lackeyjb/playwright-skill` | lackeyjb/playwright-skill | `/plugin marketplace add lackeyjb/playwright-skill` | MEDIO | MEDIO | — |
| `dev-browser` | SawyerHood/dev-browser | `/plugin marketplace add sawyerhood/dev-browser` | MEDIO | MEDIO | — |

### Gaps detectados (skills propias a escribir)

| Nombre propuesto | Justificación | Para | Prioridad |
|---|---|---|---|
| `amazon-fba-competitive-monitor` | Amazon prohíbe scraping directo. Se necesita skill con Keepa API + screenshot sin violar ToS. | MWT | ALTA |
| `mercado-libre-scraper-latam` | No existe skill robusto para scraping de Mercado Libre (MLA, MLB, MLM). | FB+MWT | ALTA |
| `b2b-competitor-site-monitor` | Monitoreo de cambios en sitios corporativos B2B: productos, PDFs, precios. | MWT | ALTA |
| `html-to-json-extractor` | No hay skill puro de HTML→JSON con schema configurable. | FB+MWT | MEDIA |
| `latam-market-research-agent` | Variante localizada de deep-research que prioriza fuentes LATAM. | FB | MEDIA |
| `price-alert-scheduler` | Skill que combina competitor-price-tracker + scheduling periódico. | MWT | MEDIA |

### Caveats técnicos

- Amazon ToS: prohíbe scraping directo. Usar Apify o browserbase con rate limiting conservador. Riesgo de suspensión de cuenta si se scrapea desde IPs vinculadas a cuenta de vendedor MWT.
- Cloudflare/DataDome/PerimeterX: agent-browser (Vercel) no tiene anti-bot nativo. Para sitios protegidos, usar obligatoriamente browserbase/skills o browser-use/cloud.
- Costos: Browserbase $5-20/mes para 50 URLs/día. Apify pay-per-result (~$0.001-0.01/página). Tavily tier gratuito 1000 créditos/mes.
- deep-research (sanjay3290): usa Gemini Deep Research API ($2-5 por tarea, timeout 60 min). No es gratuito.
- Vacío total: no hay skill robusto de Mercado Libre en el ecosistema. LATAM e-commerce requiere skill custom o Apify Actors.

---

## DIMENSIÓN 4 — PM, SaaS Launch & Growth

### Skills relevantes (consolidadas)

| Skill | Repo | Instalación | Score MWT | Score FB | Aplica también en |
|---|---|---|---|---|---|
| `interview-script` | phuryn/pm-skills | `npx skills add phuryn/pm-skills --skill interview-script` | ALTO | ALTO | — |
| `summarize-interview` | phuryn/pm-skills | `npx skills add phuryn/pm-skills --skill summarize-interview` | ALTO | ALTO | — |
| `metrics-dashboard` | phuryn/pm-skills | `npx skills add phuryn/pm-skills --skill metrics-dashboard` | ALTO | ALTO | — |
| `opportunity-solution-tree` | phuryn/pm-skills | `npx skills add phuryn/pm-skills --skill opportunity-solution-tree` | ALTO | ALTO | — |
| `jobs-to-be-done` | deanpeters/product-manager-skills | `npx skills add deanpeters/product-manager-skills --skill jobs-to-be-done` | ALTO | ALTO | — |
| `discovery-interview-prep` | deanpeters/product-manager-skills | `npx skills add deanpeters/product-manager-skills --skill discovery-interview-prep` | ALTO | ALTO | — |
| `discovery-process` | deanpeters/product-manager-skills | `npx skills add deanpeters/product-manager-skills --skill discovery-process` | ALTO | ALTO | — |
| `outcome-roadmap` | phuryn/pm-skills | `npx skills add phuryn/pm-skills --skill outcome-roadmap` | ALTO | ALTO | — |
| `roadmap-planning` | deanpeters/product-manager-skills | `npx skills add deanpeters/product-manager-skills --skill roadmap-planning` | ALTO | ALTO | — |
| `product-strategy` | phuryn/pm-skills | `npx skills add phuryn/pm-skills --skill product-strategy` | ALTO | ALTO | — |
| `product-strategy-session` | deanpeters/product-manager-skills | `npx skills add deanpeters/product-manager-skills --skill product-strategy-session` | ALTO | ALTO | — |
| `launch-checklist` | product-on-purpose/pm-skills | `npx skills add product-on-purpose/pm-skills --skill launch-checklist` | ALTO | ALTO | — |
| `launch-strategy` | coreyhaines31/marketingskills | `npx skills add coreyhaines31/marketingskills --skill launch-strategy` | ALTO | ALTO | — |
| `pricing-strategy` | phuryn/pm-skills | `npx skills add phuryn/pm-skills --skill pricing-strategy` | ALTO | ALTO | D2 |
| `finance-based-pricing-advisor` | deanpeters/product-manager-skills | `npx skills add deanpeters/product-manager-skills --skill finance-based-pricing-advisor` | ALTO | ALTO | — |
| `gtm-product-led-growth` | github/awesome-copilot | `npx skills add github/awesome-copilot --skill gtm-product-led-growth` | ALTO | ALTO | — |
| `onboarding-cro` | coreyhaines31/marketingskills | `npx skills add coreyhaines31/marketingskills --skill onboarding-cro` | ALTO | ALTO | — |
| `churn-prevention` | coreyhaines31/marketingskills | `npx skills add coreyhaines31/marketingskills --skill churn-prevention` | ALTO | ALTO | D8 |
| `saas-revenue-growth-metrics` | deanpeters/product-manager-skills | `npx skills add deanpeters/product-manager-skills --skill saas-revenue-growth-metrics` | ALTO | ALTO | — |
| `saas-economics-efficiency-metrics` | deanpeters/product-manager-skills | `npx skills add deanpeters/product-manager-skills --skill saas-economics-efficiency-metrics` | ALTO | ALTO | — |

### Gaps detectados (skills propias a escribir)

| Nombre propuesto | Justificación | Para | Prioridad |
|---|---|---|---|
| `latam-pyme-discovery` | Ninguna skill para discovery en contexto LATAM (idioma, cultura de pago, WhatsApp). | FB | ALTA |
| `saas-pyme-pricing-latam` | Ninguna skill considera pricing PYME LATAM: MXN/COP/ARS, facturación electrónica. | FB | ALTA |
| `agent-onboarding-playbook` | FaberLoom vende agentes virtuales. Necesita playbook de onboarding específico. | FB | ALTA |
| `pyme-retention-churn-ladder` | Ninguna skill modela churn específico de PYMEs LATAM. | FB | ALTA |
| `ecommerce-b2b-expansion-roadmap` | MWT necesita skill para roadmapping expansión e-commerce + B2B LATAM. | MWT | MEDIA |
| `growth-loop-whatsapp-latam` | Ninguna skill modela growth loops vía WhatsApp Business API (dominante LATAM). | FB | MEDIA |

### Caveats técnicos

- Pricing: existen 5 skills de pricing. Recomendación: `coreyhaines31/pricing-strategy` (53.3K installs) + `deanpeters/finance-based-pricing-advisor`.
- Roadmapping: 3 skills. Recomendación: `deanpeters/roadmap-planning` (1.3K installs) + `phuryn/outcome-roadmap`.
- OST: 3 skills. Recomendación: `deanpeters/opportunity-solution-tree` (833 installs, interactivo).
- Churn/retention: `coreyhaines31/churn-prevention` es más completo para SaaS (36.9K installs). `deanpeters/saas-revenue-growth-metrics` complementario.
- product-on-purpose/pm-skills tuvo bug YAML frontmatter en v2.10.x (corregido en v2.11.1).

---

## DIMENSIÓN 5 — E-commerce y Amazon FBA

### Skills relevantes (consolidadas)

| Skill | Repo | Instalación | Score MWT | Score FB | Aplica también en |
|---|---|---|---|---|---|
| `amazon-keyword-research` | nexscope-ai/Amazon-Skills | `npx skills add nexscope-ai/Amazon-Skills --skill amazon-keyword-research -g` | ALTO | MEDIO | D2 |
| `amazon-listing-optimization` | nexscope-ai/Amazon-Skills | `npx skills add nexscope-ai/Amazon-Skills --skill amazon-listing-optimization -g` | ALTO | MEDIO | D2 |
| `amazon-fba-calculator` | nexscope-ai/Amazon-Skills | `npx skills add nexscope-ai/Amazon-Skills --skill amazon-fba-calculator -g` | ALTO | BAJO | D2 |
| `amazon-ppc-campaign` | nexscope-ai/Amazon-Skills | `npx skills add nexscope-ai/Amazon-Skills --skill amazon-ppc-campaign -g` | ALTO | BAJO | — |
| `amazon-sales-estimator` | nexscope-ai/Amazon-Skills | `npx skills add nexscope-ai/Amazon-Skills --skill amazon-sales-estimator -g` | ALTO | BAJO | — |
| `amazon-global-selling` | nexscope-ai/Amazon-Skills | `npx skills add nexscope-ai/Amazon-Skills --skill amazon-global-selling -g` | ALTO | MEDIO | — |
| `amazon-review-analyzer` | nexscope-ai/Amazon-Skills | `npx skills add nexscope-ai/Amazon-Skills --skill amazon-review-analyzer -g` | ALTO | MEDIO | — |
| `claude-ecom` | takechanman1228/claude-ecom | `curl -fsSL https://raw.githubusercontent.com/takechanman1228/claude-ecom/v0.1.3/install.sh \| bash` | ALTO | ALTO | D11 |
| `inventory-demand-planning` | affaan-m/everything-claude-code | `npx skills add https://github.com/affaan-m/everything-claude-code --skill inventory-demand-planning` | ALTO | BAJO | D11 |
| `brand-monitoring` | nexscope-ai/eCommerce-Skills | `npx skills add nexscope-ai/ecommerce-skills --skill brand-monitoring` | MEDIO | ALTO | — |
| `review-monitoring` | nexscope-ai/eCommerce-Skills | `npx skills add nexscope-ai/ecommerce-skills --skill review-monitoring` | MEDIO | ALTO | — |
| `amazon-brand-analytics` | nexscope-ai/Amazon-Skills | `npx skills add nexscope-ai/Amazon-Skills --skill amazon-brand-analytics -g` | MEDIO | BAJO | — |
| `amazon-competitor-analysis` | nexscope-ai/Amazon-Skills | `npx skills add nexscope-ai/Amazon-Skills --skill amazon-competitor-analysis -g` | MEDIO | BAJO | — |
| `amazon-advertising-strategy` | nexscope-ai/Amazon-Skills | `npx skills add nexscope-ai/Amazon-Skills --skill amazon-advertising-strategy -g` | MEDIO | BAJO | — |
| `amazon-negative-keywords` | nexscope-ai/Amazon-Skills | `npx skills add nexscope-ai/Amazon-Skills --skill amazon-negative-keywords -g` | MEDIO | BAJO | — |
| `amazon-buy-box` | nexscope-ai/Amazon-Skills | `npx skills add nexscope-ai/Amazon-Skills --skill amazon-buy-box -g` | MEDIO | BAJO | — |
| `amazon-repricing-strategy` | nexscope-ai/Amazon-Skills | `npx skills add nexscope-ai/Amazon-Skills --skill amazon-repricing-strategy -g` | MEDIO | BAJO | — |
| `tariff-calculator-amazon` | nexscope-ai/Amazon-Skills | `npx skills add nexscope-ai/Amazon-Skills --skill tariff-calculator-amazon -g` | MEDIO | BAJO | — |
| `amazon-a-plus-content` | nexscope-ai/Amazon-Skills | `npx skills add nexscope-ai/Amazon-Skills --skill amazon-a-plus-content -g` | MEDIO | BAJO | D2 |
| `amazon-search-optimization` | nexscope-ai/Amazon-Skills | `npx skills add nexscope-ai/Amazon-Skills --skill amazon-search-optimization -g` | MEDIO | BAJO | D2 |

### Gaps detectados (skills propias a escribir)

| Nombre propuesto | Justificación | Para | Prioridad |
|---|---|---|---|
| `mwt-helium10-bridge` | Helium 10 es stack actual de MWT. No hay skill que consuma Helium 10 API. | MWT | ALTA |
| `mwt-mercado-libre-listings` | Expansión MWT a Mercado Libre CR/MX/BR. No existe skill. | MWT | ALTA |
| `mwt-fba-restock-forecaster` | Skill que tome Business Reports CSV + FBA Inventory Report y genere restock recommendations. | MWT | ALTA |
| `mwt-amazon-review-responder` | Auto-generate review response templates en español/inglés/portugués. | MWT | MEDIA |
| `mwt-amazon-business-reports-analyzer` | Skill específica para CSV de Amazon Business Reports. | MWT | MEDIA |
| `mwt-parent-child-asin-manager` | Gestión de variaciones parent/child ASINs: creación, auditoría, suppression fix. | MWT | MEDIA |

### Caveats técnicos

- Nexscope skills son texto plano (markdown instructions). No ejecutan código ni llaman APIs. No reemplazan Helium 10, Jungle Scout o SP-API.
- Instalación nexscope-ai: `npx skills add nexscope-ai/Amazon-Skills -g` instala TODAS las 51 skills (~2MB). O individuales con `--skill <name>`.
- claude-ecom requiere Python 3.10+. Instala venv privado. Requiere CSV con columnas mínimas: order_id, order_date, customer_id, revenue.
- MarceauSolutions/amazon-seller-mcp es MCP server (no skill). Requiere SP-API OAuth. Solo 1 star, proyecto temprano, riesgo de abandono.
- Security audits nexscope: `amazon-keyword-research` tiene Gen Agent Trust Hub Fail, Socket Warn, Snyk Warn (scraping web de Amazon autocomplete).
- Sin skills de Shopify-Mercado Libre bridge: ecosistema skills.sh tiene 0 skills de Mercado Libre.

---

## DIMENSIÓN 6 — Document Processing y B2B Workflow

### Skills relevantes (consolidadas)

| Skill | Repo | Instalación | Score MWT | Score FB | Aplica también en |
|---|---|---|---|---|---|
| `kreuzberg` | kreuzberg-dev/kreuzberg | `npx skills add kreuzberg-dev/kreuzberg` | ALTO | ALTO | — |
| `nutrient-document-processing` | PSPDFKit-labs/nutrient-agent-skill | `npx skills add PSPDFKit-labs/nutrient-agent-skill` | ALTO | ALTO | D12 |
| `excel-automation` | daymade/claude-code-skills | `claude plugin install excel-automation@daymade-skills` | ALTO | ALTO | D11 |
| `invoice-generator` | tmigone/skills | `npx skills add tmigone/invoice-generator` | ALTO | MEDIO | — |
| `table-extractor` | claude-office-skills/skills | `npx skills add claude-office-skills/skills --skill table-extractor` | ALTO | BAJO | — |
| `pdf-creator` | daymade/claude-code-skills | `claude plugin install daymade-docs@daymade-skills` | MEDIO | ALTO | — |
| `doc-to-markdown` | daymade/claude-code-skills | `claude plugin install daymade-docs@daymade-skills` | MEDIO | MEDIO | — |
| `contract-review` | claude-office-skills/skills | `npx skills add claude-office-skills/skills --skill contract-review` | MEDIO | BAJO | D12 |
| `invoice-organizer` | ComposioHQ/awesome-claude-skills | `npx skills add ComposioHQ/awesome-claude-skills --skill invoice-organizer` | MEDIO | BAJO | — |
| `pdf-ocr` | claude-office-skills/skills | `npx skills add claude-office-skills/skills --skill pdf-ocr` | MEDIO | ALTO | — |
| `doc-parser` | claude-office-skills/skills | `npx skills add claude-office-skills/skills --skill doc-parser` | MEDIO | ALTO | — |
| `translate-book` | deusyu/translate-book | `npx skills add deusyu/translate-book` | MEDIO | BAJO | — |
| `charlie-cfo-skill` | EveryInc/charlie-cfo-skill | `npx skills add EveryInc/charlie-cfo-skill` | ALTO | BAJO | D4, D11 |
| `awesome-legal-skills` | lawvable/awesome-legal-skills | `git clone https://github.com/lawvable/awesome-legal-skills.git` | MEDIO | BAJO | — |
| `contract-review-cuad` | evolsb/claude-legal-skill | `git clone https://github.com/evolsb/claude-legal-skill ~/.claude/skills/contract-review` | ALTO | MEDIO | D12 |

### Gaps detectados (skills propias a escribir)

| Nombre propuesto | Justificación | Para | Prioridad |
|---|---|---|---|
| `ficha-tecnica-extractor` | P0 — Ningún skill extrae especificaciones técnicas de calzado industrial desde PDFs. | MWT | P0 |
| `cotizacion-b2b-marluvas` | P0 — No existe skill que genere cotizaciones parametrizadas con templates de marca. | MWT | P0 |
| `licitaciones-latam-parser` | P1 — Cero skills para parsear licitaciones públicas de Compranet, SECOP, ChileCompra. | MWT | P1 |
| `conciliacion-po-factura-remision` | P1 — No existe skill de 3-way matching para flujo B2B brasileño. | MWT | P1 |
| `invoice-parser-latam` | P1 — Ningún skill maneja layout de notas fiscales brasileñas (NF-e), CFDI México. | MWT | P1 |
| `docx-template-autofill` | P2 — No hay skill que orqueste autofill de templates DOCX con datos de fichas técnicas. | FB | P2 |

### Caveats técnicos

- Nutrient API key requerida (producto comercial). Freemium: 1000 documentos/mes. Sin API key el skill no opera.
- Kreuzberg licencia: Elastic License 2.0 (ELv2), no MIT/Apache. Restricciones en uso como servicio gestionado. Verificar compatibilidad modelo de negocio FaberLoom.
- Kreuzberg dependencias: OCR requiere backends adicionales (`pip install kreuzberg[easyocr]`, Tesseract). Requiere `tesseract-ocr-spa`, `tesseract-ocr-por` para LATAM.
- daymade skills vía plugin de Claude Code (`claude plugin install`), no `npx skills add`. Pueden no ser portables a Codex/Cursor.
- claude-office-skills: colección de 136+ skills sin packaging unificado. `install.sh` copia carpetas masivamente. Riesgo de bloat de contexto.
- Camelot (table-extractor): extrae tablas basado en líneas/bordes. Si fichas técnicas usan tablas sin bordes, fallará.
- Conflictos: `kreuzberg` y `nutrient-agent-skill` compiten por mismo trigger. Definir `CLAUDE.md` con reglas de precedencia.

---

## DIMENSIÓN 7 — Knowledge Management, RAG, Vector DBs

### Skills relevantes (consolidadas)

| Skill | Repo | Instalación | Score MWT | Score FB | Aplica también en |
|---|---|---|---|---|---|
| `rag-architect` | alirezarezvani/claude-skills | `/plugin install engineering-advanced-skills@claude-code-skills` | ALTO | ALTO | — |
| `llm-wiki` | alirezarezvani/claude-skills | `Bundle engineering-advanced-skills` | ALTO | MEDIO | — |
| `vault-health` | DavidROliverBA/Daves-Claude-Code-Skills | `cp skills/vault-health/*.md .claude/skills/` | ALTO | MEDIO | — |
| `supabase-postgres-best-practices` | supabase/agent-skills | `npx skills add supabase/agent-skills` | MEDIO | ALTO | D10 |
| `postgres-semantic-search` | laguagu/claude-code-nextjs-skills | `Copiar carpeta postgres-semantic-search a .claude/skills/` | MEDIO | ALTO | — |
| `evaluate-rag` | hamelsmu/evals-skills | `npx skills add https://github.com/hamelsmu/evals-skills` | MEDIO | ALTO | D10 |
| `database-schema-designer` | alirezarezvani/claude-skills | `Bundle engineering-advanced-skills` | BAJO | ALTO | — |
| `qdrant/skills` | qdrant/skills | `npx skills add qdrant/skills` | BAJO | ALTO | — |
| `claude-memory-skill` | hanfang/claude-memory-skill | `git clone https://github.com/hanfang/claude-memory-skill.git` | MEDIO | MEDIO | — |
| `context-engineering-advisor` | deanpeters/Product-Manager-Skills | `Copiar carpeta a .claude/skills/` | MEDIO | ALTO | — |

### Gaps detectados (skills propias a escribir)

| Nombre propuesto | Justificación | Para | Prioridad |
|---|---|---|---|
| `mwt-kb-librarian` | MWT tiene 430 archivos con 8 taxonomías. Necesita skill que entienda el esquema de frontmatter. | MWT | ALTA |
| `faberloom-pgvector-tenant-isolation` | FaberLoom usa pgvector multi-tenant. Necesita skill que codifique RLS + embedding ownership. | FB | ALTA |
| `faberloom-hybrid-search-pgvector` | Skill específica para hybrid search (BM25 + pgvector + RRF) en Supabase. | FB | ALTA |
| `markdown-kb-validator` | Validador de KB markdown con frontmatter schema por tipo de nota, links internos, freshness. | MWT | ALTA |
| `rag-retrieval-evaluator` | Skill para evaluar retrieval: recall@k, MRR, NDCG contra golden dataset. | FB | MEDIA |
| `embedding-chunking-strategist` | Skill que guíe selección de estrategias de chunking y embedding models. | FB | MEDIA |

### Caveats técnicos

- alirezarezvani/claude-skills se instala como marketplace bundle (~25 skills). No individuales vía `npx skills add` a menos que se copien carpetas manualmente. Puede saturar context window.
- Vault Health frontmatter-validator es hook de `PostToolUse`, no slash command. Requiere configuración previa de `NOTE_SCHEMAS`.
- hanfang/claude-memory-skill no está en skills.sh. Se instala vía `git clone` manual. 2.1K stars, activamente mantenido.
- hamelsmu/evals-skills no está en skills.sh. Se instala vía `npx skills add https://github.com/hamelsmu/evals-skills`.
- qdrant/skills es Qdrant-specific. Conceptos transferibles a pgvector/Supabase pero implementaciones no.
- supabase-postgres-best-practices no menciona pgvector. Cubre RLS, performance, schema design — Postgres general.
- Conflictos: `llm-wiki` y `Vault Health` operan sobre vaults markdown. Pueden tener triggers superpuestos. Usar `llm-wiki` para ingestion/síntesis y `Vault Health` para validación.

---

## DIMENSIÓN 8 — B2B Sales, CRM, Pipeline

### Skills relevantes (consolidadas)

| Skill | Repo | Instalación | Score MWT | Score FB | Aplica también en |
|---|---|---|---|---|---|
| `integrate-whatsapp` | gokapso/agent-skills | `npx skills add gokapso/agent-skills@integrate-whatsapp` | ALTO | ALTO | — |
| `automate-whatsapp` | gokapso/agent-skills | `npx skills add gokapso/agent-skills@automate-whatsapp` | ALTO | ALTO | — |
| `crm-automation` | claude-office-skills/skills | `npx skills add claude-office-skills/skills@crm-automation` | ALTO | ALTO | — |
| `pipedrive-automation` | claude-office-skills/skills | `npx skills add claude-office-skills/skills@pipedrive-automation` | ALTO | ALTO | — |
| `zoho-crm` | membranedev/application-skills | `npx skills add membranedev/application-skills@zoho-crm` | ALTO | MEDIO | — |
| `pipeline-forecasting` | guia-matthieu/clawfu-skills | `npx skills add guia-matthieu/clawfu-skills@pipeline-forecasting` | ALTO | ALTO | — |
| `deal-risk-scoring` | guia-matthieu/clawfu-skills | `npx skills add guia-matthieu/clawfu-skills@deal-risk-scoring` | ALTO | ALTO | — |
| `sales-deal-inspect` | sales-skills/sales | `npx skills add sales-skills/sales` | ALTO | ALTO | — |
| `sales-forecast` | sales-skills/sales | `npx skills add sales-skills/sales` | ALTO | ALTO | — |
| `apify-lead-generation` | apify/agent-skills | `npx skills add apify/agent-skills@apify-lead-generation` | ALTO | ALTO | — |
| `afrexai-revenue-forecasting` | openclaw/skills | `git clone https://github.com/openclaw/skills.git` | ALTO | ALTO | — |
| `observe-whatsapp` | gokapso/agent-skills | `npx skills add gokapso/agent-skills@observe-whatsapp` | ALTO | MEDIO | — |
| `hubspot` | membranedev/application-skills | `npx skills add membranedev/application-skills@hubspot` | MEDIO | ALTO | — |
| `apollo-outreach` | openclaudia/openclaudia-skills | `npx skills add openclaudia/openclaudia-skills@apollo-outreach` | MEDIO | ALTO | — |
| `lead-research-assistant` | composiohq/awesome-claude-skills | `npx skills add composiohq/awesome-claude-skills@lead-research-assistant` | MEDIO | ALTO | — |
| `enrich-lead` | anthropics/knowledge-work-plugins | `npx skills add anthropics/knowledge-work-plugins@enrich-lead` | MEDIO | ALTO | — |
| `cold-email` | coreyhaines31/marketingskills | `npx skills add coreyhaines31/marketingskills@cold-email` | ALTO | ALTO | D2 |
| `email-sequence` | coreyhaines31/marketingskills | `npx skills add coreyhaines31/marketingskills@email-sequence` | MEDIO | ALTO | D2 |
| `churn-prevention` | coreyhaines31/marketingskills | `npx skills add coreyhaines31/marketingskills@churn-prevention` | ALTO | ALTO | D4 |
| `sales-team-claude` | zubair-trabzada/ai-sales-team-claude | `git clone https://github.com/zubair-trabzada/ai-sales-team-claude.git` | MEDIO | ALTO | — |

### Gaps detectados (skills propias a escribir)

| Nombre propuesto | Justificación | Para | Prioridad |
|---|---|---|---|
| `lead-enrichment-latam` | CRÍTICA — Ninguna skill integra fuentes LATAM. Apollo.io cobertura pobre en PyMEs manufactureras. | MWT | CRÍTICA |
| `whatsapp-business-api-pedidos` | gokapso cubre automatización general pero no skill específica cotización→pedido→seguimiento. | MWT | ALTA |
| `pipedrive-zoho-sync` | MWT probablemente migra entre Pipedrive y Zoho. No existe skill de sincronización bidireccional. | MWT | ALTA |
| `pipeline-largo-b2b-industrial` | Ninguna skill modela forecasting para ciclos de 6-18 meses (calzado industrial B2B). | MWT | ALTA |
| `agente-ventas-faber` | FaberLoom necesita skill template de agente de ventas usando sus componentes. | FB | ALTA |
| `cuentas-riesgo-reengagement-b2b` | No existe skill para detectar cuentas B2B en riesgo por inactividad. | MWT | MEDIA |
| `linkedin-scraper-prospect-latam` | No existe skill de LinkedIn prospecting + enrichment + outreach para LATAM. | MWT | MEDIA |
| `cold-outreach-whatsapp-sequence` | No existe skill que combine outreach sequences con WhatsApp Business API. | MWT | MEDIA |
| `forecasting-pipeline-multimoneda` | MWT opera MXN→COP. Ninguna skill maneja pipeline multi-moneda. | MWT | MEDIA |

### Caveats técnicos

- WhatsApp Business API (gokapso): requiere autenticación Kapso CLI o variables de entorno. Meta Business Account verificado requerido para plantillas HSM en producción.
- CRM skills requieren API keys individuales. membranedev usa OAuth 2.0 (refresh token puede expirar). Zoho rate limits: 100 requests/minuto en plan gratuito.
- Apollo.io requiere API key de plan pago. skill `apollo-outreach` no está publicada en skills.sh como skill individual buscable.
- Email sequences (coreyhaines31) son copywriting/estrategia, no integran con ESP ni CRM. Requieren export manual.
- Revenue forecasting skills son frameworks analíticos manuales. No se conectan automáticamente a Pipedrive/HubSpot.
- AI Sales Team (zubair-trabzada): scripts hacen scraping web sin rotación de IP, pueden causar bloqueos.
- Ninguna skill maneja normalización automática de teléfonos LATAM (+52, +57), direcciones, ni deduplicación por RFC/NIT/RUT.

---

## DIMENSIÓN 9 — Multi-Agent Orchestration y Handoff

### Skills relevantes (consolidadas)

| Skill | Repo | Instalación | Score MWT | Score FB | Aplica también en |
|---|---|---|---|---|---|
| `on-call-handoff-patterns` | wshobson/agents | `npx skills add wshobson/agents --skill on-call-handoff-patterns` | ALTO | ALTO | — |
| `session-handoff` | softaworks/agent-toolkit | `npx skills add softaworks/agent-toolkit --skill session-handoff` | ALTO | ALTO | — |
| `handoff` | boshu2/agentops | `npx skills add boshu2/agentops --skill handoff` | ALTO | ALTO | — |
| `swarm-planner` | am-will/swarms | `npx skills add am-will/swarms` | ALTO | MEDIO | — |
| `parallel-task` | am-will/swarms | `npx skills add am-will/swarms` | ALTO | MEDIO | — |
| `langgraph-human-in-the-loop` | langchain-ai/langchain-skills | `npx skills add langchain-ai/langchain-skills --skill langgraph-human-in-the-loop` | ALTO | ALTO | — |
| `deep-agents-orchestration` | langchain-ai/langchain-skills | `npx skills add langchain-ai/langchain-skills --skill deep-agents-orchestration` | MEDIO | ALTO | — |
| `workflow-orchestration-patterns` | wshobson/agents | `npx skills add wshobson/agents --skill workflow-orchestration-patterns` | MEDIO | MEDIO | — |
| `saga-orchestration` | wshobson/agents | `npx skills add wshobson/agents --skill saga-orchestration` | MEDIO | BAJO | — |
| `multi-agent-orchestration` | qodex-ai/ai-agent-skills | `npx skills add qodex-ai/ai-agent-skills --skill multi-agent-orchestration` | MEDIO | MEDIO | — |
| `swarm` | boshu2/agentops | `npx skills add boshu2/agentops --skill swarm` | MEDIO | MEDIO | — |
| `model-hierarchy` | zscole/model-hierarchy-skill | `npx skills add zscole/model-hierarchy-skill --skill model-hierarchy` | ALTO | ALTO | D1 |
| `recursive-decomposition` | massimodeluisa/recursive-decomposition-skill | `npx skills add massimodeluisa/recursive-decomposition-skill --skill recursive-decomposition` | MEDIO | ALTO | D1 |
| `orchestrating-swarms` | everyinc/compound-engineering-plugin | `npx skills add everyinc/compound-engineering-plugin --skill orchestrating-swarms` | MEDIO | MEDIO | — |

### Gaps detectados (skills propias a escribir)

| Nombre propuesto | Justificación | Para | Prioridad |
|---|---|---|---|
| `mwt-orchestrator-bridge` | MWT tiene PLB_ORCHESTRATOR congelado. No existe skill puente entre orquestador moderno y sistema heredado. | MWT | ALTA |
| `faber-loom-role-router` | FaberLoom tiene agentes por rol. No existe router inteligente basado en KB, tono y canal. | FB | ALTA |
| `context-preservation-handoff` | Ninguna skill maneja preservación de estado de ejecución de máquina de estado. | Ambos | ALTA |
| `escalation-supervisor` | Ninguna skill implementa patrón supervisor con escalamiento automático. | FB | MEDIA |
| `hito-governance-gate` | HITL existentes se centran en aprobación técnica. Se necesita skill para decisiones de negocio críticas. | FB | MEDIA |
| `cross-framework-orchestrator` | Todas las skills de orquestación están atadas a un framework. No existe skill agnóstica. | Ambos | BAJA |

### Caveats técnicos

- Conflictos de orquestador: `PLB_ORCHESTRATOR` (MWT) y sistema nativo de FaberLoom podrían entrar en conflicto con orquestadores externos. Adoptar como inspiración o implementar capa de adaptación.
- Dependencias de framework: `deep-agents-orchestration` y `langgraph-human-in-the-loop` requieren proyecto construido sobre LangGraph.
- am-will/swarms no aparece en búsqueda de skills.sh. Puede estar en desarrollo temprano o falta de mantenimiento.
- qodex-ai/ai-agent-skills tiene auditoría Gen Agent Trust Hub con estado 'Fail'. Bandera roja para producción sin revisión previa.
- boshu2/agentops se instala como marketplace de plugins (`claude plugin marketplace add`), no como skill individual de skills.sh.
- Ejecución de swarms depende de capacidad del entorno para generar subagentes. Característica experimental en algunos runtimes.
- Persistencia de estado: la mayoría de skills de handoff se basan en archivos locales. En entorno distribuido puede causar problemas de concurrencia.

---

## DIMENSIÓN 10 — Code Quality, Backend, Testing

### Skills relevantes (consolidadas)

| Skill | Repo | Instalación | Score MWT | Score FB | Aplica también en |
|---|---|---|---|---|---|
| `supabase-postgres-best-practices` | supabase/agent-skills | `npx skills add supabase/agent-skills --skill supabase-postgres-best-practices` | MEDIO | ALTO | D7 |
| `fastapi-python` | mindrally/skills | `npx skills add https://github.com/mindrally/skills --skill fastapi-python` | MEDIO | ALTO | — |
| `fastapi-jez` | jezweb/claude-skills | `npx skills add https://github.com/jezweb/claude-skills --skill fastapi` | MEDIO | ALTO | — |
| `pgvector-semantic-search` | timescale/pg-aiguide | `npx skills add https://github.com/timescale/pg-aiguide --skill pgvector-semantic-search` | MEDIO | ALTO | — |
| `pydantic-ai-agent-creation` | existential-birds/beagle | `npx skills add https://github.com/existential-birds/beagle --skill pydantic-ai-agent-creation` | MEDIO | ALTO | — |
| `sdd` | NeoLabHQ/context-engineering-kit | `npx skills add NeoLabHQ/context-engineering-kit` | ALTO | ALTO | D1 |
| `tdd` | NeoLabHQ/context-engineering-kit | `npx skills add NeoLabHQ/context-engineering-kit` | ALTO | ALTO | D1 |
| `reflexion` | NeoLabHQ/context-engineering-kit | `npx skills add NeoLabHQ/context-engineering-kit` | ALTO | MEDIO | D1 |
| `review` | NeoLabHQ/context-engineering-kit | `npx skills add NeoLabHQ/context-engineering-kit` | ALTO | ALTO | D1 |
| `eval-audit` | hamelsmu/evals-skills | `npx skills add https://github.com/hamelsmu/evals-skills --skill eval-audit` | ALTO | ALTO | D1 |
| `error-analysis` | hamelsmu/evals-skills | `npx skills add https://github.com/hamelsmu/evals-skills --skill error-analysis` | ALTO | ALTO | D1 |
| `evaluate-rag` | hamelsmu/evals-skills | `npx skills add https://github.com/hamelsmu/evals-skills --skill evaluate-rag` | ALTO | ALTO | D7 |
| `write-judge-prompt` | hamelsmu/evals-skills | `npx skills add https://github.com/hamelsmu/evals-skills --skill write-judge-prompt` | ALTO | ALTO | D1 |
| `promptfoo-evals` | promptfoo/promptfoo | `/plugin install promptfoo-evals@promptfoo` | ALTO | ALTO | — |
| `python-type-safety` | wshobson/agents | `npx skills add https://github.com/wshobson/agents --skill python-type-safety` | BAJO | ALTO | — |
| `python-testing-patterns` | wshobson/agents | `npx skills add https://github.com/wshobson/agents --skill python-testing-patterns` | BAJO | ALTO | — |
| `pytest-coverage` | github/awesome-copilot | `npx skills add https://github.com/github/awesome-copilot --skill pytest-coverage` | BAJO | MEDIO | — |
| `python-observability` | wshobson/agents | `npx skills add https://github.com/wshobson/agents --skill python-observability` | BAJO | MEDIO | — |

### Gaps detectados (skills propias a escribir)

| Nombre propuesto | Justificación | Para | Prioridad |
|---|---|---|---|
| `pydantic-ai-debugging-tracing` | Ninguna skill cubre debugging de agents Pydantic AI (tool calls, validation, retries). | FB | ALTA |
| `fastapi-pydantic-ai-integration` | Skill que una FastAPI + Pydantic AI: endpoints que orquestan agents, streaming SSE. | FB | ALTA |
| `supabase-py-sdk` | La skill supabase-postgres cubre SQL/Postgres pero no el SDK Python (supabase-py). | FB | ALTA |
| `rls-testing-automation` | No existe skill para testear políticas RLS de Supabase/Postgres con datos sintéticos. | FB | ALTA |
| `pgvector-pydantic-ai` | Skill que una pgvector con Pydantic AI: embeddings, similarity search, hybrid RRF. | FB | ALTA |
| `json-schema-contract-testing` | FaberLoom es contract-first. Ninguna skill cubre testing automatizado de contratos API. | FB | MEDIA |
| `action-engine-eval` | Skill para evaluar Action Engine: schema compliance, tool calling correctness. | FB | MEDIA |
| `mypy-strict-config` | python-type-safety menciona mypy pero no tiene skill dedicada a configurar mypy --strict. | FB | MEDIA |
| `pyright-ci-integration` | Skill para integrar pyright/mypy en CI con GitHub Actions. | FB | MEDIA |

### Caveats técnicos

- obra/superpowers ya cubre TDD, debugging, verification. No instalar NeoLabHQ/tdd ni mattpocock/tdd si el objetivo es evitar conflicto de metodologías.
- NeoLabHQ skills usan plugin marketplace de Claude Code (`/plugin marketplace add`). En otros agentes usar `npx skills add`.
- hamelsmu/evals-skills no está en skills.sh. Instalación directa desde GitHub.
- promptfoo-evals skill requiere `promptfoo` CLI instalado (`npm install -g promptfoo`).
- mattpocock/skills son TypeScript-first. Aplicables a Python solo parcialmente.
- pgvector-semantic-search de timescale: solo 293 installs. Skill relativamente nueva.
- pydantic-ai-agent-creation: solo 194 installs, 55 stars. Skill muy nueva. Requiere validación práctica.
- Sin skills de DeepEval o Braintrust como agent skills maduras. Son plataformas de evaluación, no skills instalables.

---

## DIMENSIÓN 11 — Data Analysis, Reporting, Forecasting

### Skills relevantes (consolidadas)

| Skill | Repo | Instalación | Score MWT | Score FB | Aplica también en |
|---|---|---|---|---|---|
| `csv-data-summarizer` | coffeefuelbump/csv-data-summarizer-claude-skill | `npx skills add https://github.com/coffeefuelbump/csv-data-summarizer-claude-skill --skill csv-data-summarizer` | ALTO | ALTO | — |
| `data-analytics-skills` | nimrodfisher/data-analytics-skills | `Clonar repo → .claude/skills/` | ALTO | ALTO | — |
| `data-analysis-skill` | dongzhang84/data-analysis-skill | `Clonar repo → .claude/skills/data-analysis/` | ALTO | ALTO | — |
| `claude-ecom` | takechanman1228/claude-ecom | `curl -fsSL https://raw.githubusercontent.com/takechanman1228/claude-ecom/v0.1.3/install.sh \| bash` | ALTO | ALTO | D5 |
| `timesfm-forecasting` | k-dense-ai/scientific-agent-skills | `npx skills add https://github.com/k-dense-ai/scientific-agent-skills --skill timesfm-forecasting` | ALTO | ALTO | — |
| `charlie-cfo-skill` | EveryInc/charlie-cfo-skill | `npx skills add everyinc/charlie-cfo-skill` | ALTO | MEDIO | D4, D6 |
| `demand-forecasting` | finsilabs/awesome-ecommerce-skills | `npx skills add https://github.com/finsilabs/awesome-ecommerce-skills --skill demand-forecasting` | ALTO | BAJO | — |
| `inventory-demand-planning` | affaan-m/everything-claude-code | `npx skills add https://github.com/affaan-m/everything-claude-code --skill inventory-demand-planning` | ALTO | BAJO | D5 |
| `cohort-analysis` | phuryn/pm-skills | `npx skills add https://github.com/phuryn/pm-skills --skill cohort-analysis` | MEDIO | ALTO | D4 |
| `churn-prediction` | guia-matthieu/clawfu-skills | `npx skills add https://github.com/guia-matthieu/clawfu-skills --skill churn-prediction` | MEDIO | ALTO | — |
| `anomaly-detector` | majesticlabs-dev/majestic-marketplace | `npx skills add https://github.com/majesticlabs-dev/majestic-marketplace --skill anomaly-detector` | MEDIO | MEDIO | — |
| `scikit-survival` | davila7/claude-code-templates | `npx skills add https://github.com/davila7/claude-code-templates --skill scikit-survival` | BAJO | ALTO | — |
| `gws-sheets` | googleworkspace/cli | `npx skills add https://github.com/googleworkspace/cli --skill gws-sheets` | MEDIO | MEDIO | — |
| `excel-automation` | claude-office-skills/skills | `npx skills add https://github.com/claude-office-skills/skills --skill excel-automation` | MEDIO | BAJO | D6 |

### Gaps detectados (skills propias a escribir)

| Nombre propuesto | Justificación | Para | Prioridad |
|---|---|---|---|
| `mwt-amazon-fba-analytics` | Ningún skill hace análisis nativo de datos Amazon Seller Central + FBA. | MWT | ALTA |
| `mwt-demand-forecasting-fba` | Ninguno está calibrado para particularidades FBA: lead times, storage limits, Prime Day. | MWT | ALTA |
| `mwt-anomaly-detection-returns` | Detectar spikes de devoluciones, drops de conversión por ASIN. Sin contexto Amazon. | MWT | ALTA |
| `faberloom-product-analytics` | FaberLoom necesita analytics nativo: feature adoption, engagement, retention. | FB | ALTA |
| `faberloom-survival-churn` | Skill combinado survival analysis + churn prediction con datos específicos FaberLoom. | FB | ALTA |
| `mwt-b2b-sales-forecasting` | MWT opera B2B además de FBA. Necesita forecasting de pipeline B2B. | MWT | MEDIO |
| `mwt-automated-reporting` | Skill que genere reportes semanales con KPIs: ventas, ACOS, BSR, devoluciones. | MWT | MEDIO |
| `faberloom-cohort-feature-adoption` | Cohort analysis específico para adopción de features en FaberLoom. | FB | MEDIO |

### Caveats técnicos

- timesfm-forecasting requiere ~1.5 GB RAM en CPU. Modelo 500M params necesita ~32 GB RAM. Snyk Warn en audit. Univariate only.
- claude-ecom: instalación manual. No está empaquetado como skill de skills.sh. Última actualización marzo 2026.
- data-analysis-skill requiere Python 3.8+ con pandas, openpyxl, tabulate, chardet y Node.js 18+ con puppeteer, pptxgenjs.
- data-analytics-skills (nimrodfisher): instalación manual copiando skills individuales. No hay `npx skills add` para toda la colección.
- anomaly-detector: 44 installs/semana, 37 stars. Madurez limitada.
- charlie-cfo-skill: 222 installs. Framework de consulta/guía, no skill con scripts de procesamiento.
- csv-data-summarizer: Snyk Warn. Genera visualizaciones con matplotlib — calidad visual básica. No soporta Excel nativamente.
- Conflictos: `anthropic-skills/xlsx` ya instalado. `excel-automation` de claude-office-skills podría solaparse.
- Dependencias comunes: múltiples skills requieren pandas, matplotlib, scikit-learn. Conflictos de versión si no se usa venv dedicado.

---

## DIMENSIÓN 12 — Contracts, Compliance, Legal LATAM

### Skills relevantes (consolidadas)

| Skill | Repo | Instalación | Score MWT | Score FB | Aplica también en |
|---|---|---|---|---|---|
| `nutrient-document-processing` | PSPDFKit-labs/nutrient-agent-skill | `npx skills add PSPDFKit-labs/nutrient-agent-skill` | ALTO | ALTO | D6 |
| `contract-review-cuad` | evolsb/claude-legal-skill | `git clone https://github.com/evolsb/claude-legal-skill ~/.claude/skills/contract-review` | ALTO | MEDIO | D6 |
| `tender-analyzer` | somarkai/skills | `npx skills add https://github.com/somarkai/skills --skill tender-analyzer` | ALTO | BAJO | — |
| `contract-review` | claude-office-skills/skills | `npx skills add claude-office-skills/skills --skill contract-review` | MEDIO | BAJO | D6 |
| `review-contract` | anthropics/knowledge-work-plugins | `npx skills add https://github.com/anthropics/knowledge-work-plugins --skill review-contract` | MEDIO | MEDIO | — |
| `legal-risk-assessment` | anthropics/knowledge-work-plugins | `npx skills add https://github.com/anthropics/knowledge-work-plugins --skill legal-risk-assessment` | MEDIO | MEDIO | — |
| `startup-due-diligence` | skala-io/legal-skills | `npx skills add skala-io/legal-skills` | MEDIO | MEDIO | — |
| `vendor-due-diligence` | lawvable/awesome-legal-skills | `npx skills add lawvable/awesome-legal-skills` | MEDIO | BAJO | — |
| `lgpd-privacy-guardian` | metricasboss/otto | `git clone https://github.com/metricasboss/otto.git` | MEDIO | BAJO | — |
| `privacy-skills-complete` | mukul975/Privacy-Data-Protection-Skills | `/plugin marketplace add mukul975/Privacy-Data-Protection-Skills` | MEDIO | MEDIO | — |

### Gaps detectados (skills propias a escribir)

| Nombre propuesto | Justificación | Para | Prioridad |
|---|---|---|---|
| `e-invoice-cfdi-mexico` | Validación CFDI 4.0. México mercado clave. Cero skills de e-invoicing LATAM. | MWT | CRÍTICA |
| `e-invoice-nfe-brasil` | NFe modelo 55, NFC-e. Brasil mercado top-3 de MWT. | MWT | CRÍTICA |
| `e-invoice-dte-costa-rica` | DTE ante Ministerio de Hacienda CR. | MWT | CRÍTICA |
| `e-invoice-colombia` | Factura electrónica UBL 2.1 / DIAN. | MWT | CRÍTICA |
| `compliance-lfpdppp-mexico` | Ley Federal Protección Datos Personales México. Ninguna skill cubre. | MWT+FB | ALTA |
| `compliance-ley1581-colombia` | Ley 1581 de 2012 + Decreto 1377. Colombia. | MWT+FB | ALTA |
| `compliance-ley8968-costa-rica` | Ley 8968 Protección Datos Personales Costa Rica. | MWT+FB | ALTA |
| `contract-review-b2b-latam` | Review contratos B2B bajo derecho mercantil latinoamericano. | MWT | ALTA |
| `due-diligence-proveedor-b2b-latam` | Evaluación proveedores industriales LATAM: RUC/RUT, registro sanitario, ISO. | MWT | ALTA |
| `licitaciones-publicas-latam` | Parsing pliegos CompraNet, SECOP, Mercado Público. | MWT | MEDIA |
| `tax-compliance-latam` | Tax compliance B2B: retenciones, DIOT México, validación NIT/RUC. | MWT | MEDIA |
| `redlining-contracts-docx` | Orquestar docx (ya instalado) para generar redlines con tracked changes. | MWT | MEDIA |
| `lgpd-full-compliance` | Expandir skills LGPD actuales a set completo: DPIA, derechos titular. | MWT+FB | MEDIA |

### Caveats técnicos

- evolsb/claude-legal-skill foco en US law por defecto. Para LATAM requiere adaptación del SKILL.md.
- PSPDFKit-labs/nutrient-agent-skill requiere API key Nutrient. Para procesamiento masivo en 6 países se necesitará plan pago. Redacción de PII es irreversible.
- skala-io/legal-skills/startup-due-diligence diseñado para startups VC (seed/Series A). Requiere adaptación manual para contratos de distribución industrial.
- somarkai/skills/tender-analyzer requiere parsing previo con SoMark (servicio externo). Sin SoMark, pierde precisión. Solo 17 installs/semana.
- metricasboss/otto es herramienta de hooks de pre-commit para código, no para documentos legales. Útil solo si desarrollan software con datos personales brasileños.
- mukul975/Privacy-Data-Protection-Skills: solo 3+ skills para LGPD vs 50+ para GDPR. Calidad no verificada como Q1.
- openaccountants/openaccountants: skills calificados mayormente como Q3 (AI-drafted), no Q1. Sin verificación cobertura LATAM.
- vyayasan/kyc-analyst: early stage. Solo 5 stagegates de 17 son automáticos. Resto requiere HITL constante.
- Conflictos: `nutrient-agent-skill` y `anthropics/skills/pdf` pueden solaparse. Usar nutrient para operaciones avanzadas y anthropic/pdf para lectura simple.

---

## CROSS-VERIFICATION CONSOLIDADA

### Skills duplicadas entre dimensiones (una sola entrada consolidada)

| Skill | Repo | Score MWT | Score FB | Dimensiones donde aplica | Recomendación |
|---|---|---|---|---|---|
| `amazon-fba-calculator` | nexscope-ai/Amazon-Skills | ALTO | BAJO | D2, D5 | Evaluar según necesidad específica |
| `amazon-keyword-research` | nexscope-ai/Amazon-Skills | ALTO | MEDIO | D2, D5 | Instalar para MWT — prioridad alta |
| `amazon-listing-optimization` | nexscope-ai/Amazon-Skills | ALTO | MEDIO | D2, D5 | Instalar para MWT — prioridad alta |
| `charlie-cfo-skill` | EveryInc/charlie-cfo-skill | ALTO | ALTO | D4, D6, D11 | Instalar YA — aplica a ambos proyectos |
| `churn-prevention` | coreyhaines31/marketingskills | ALTO | ALTO | D4, D8 | Instalar YA — aplica a ambos proyectos |
| `claude-ecom` | takechanman1228/claude-ecom | ALTO | ALTO | D5, D11 | Instalar YA — aplica a ambos proyectos |
| `cohort-analysis` | phuryn/pm-skills | ALTO | ALTO | D4, D11 | Instalar YA — aplica a ambos proyectos |
| `cold-email` | coreyhaines31/marketingskills | ALTO | ALTO | D2, D8 | Instalar YA — aplica a ambos proyectos |
| `contract-review` | claude-office-skills/skills | MEDIO | MEDIO | D6, D12 | Evaluar según necesidad específica |
| `contract-review-cuad` | evolsb/claude-legal-skill | ALTO | MEDIO | D6, D12 | Instalar para MWT — prioridad alta |
| `email-sequence` | coreyhaines31/marketingskills | MEDIO | ALTO | D2, D8 | Instalar para FaberLoom — prioridad alta |
| `error-analysis` | hamelsmu/evals-skills | ALTO | ALTO | D1, D10 | Instalar YA — aplica a ambos proyectos |
| `eval-audit` | hamelsmu/evals-skills | ALTO | ALTO | D1, D10 | Instalar YA — aplica a ambos proyectos |
| `evaluate-rag` | hamelsmu/evals-skills | ALTO | ALTO | D7, D10 | Instalar YA — aplica a ambos proyectos |
| `excel-automation` | daymade/claude-code-skills | ALTO | ALTO | D6, D11 | Instalar YA — aplica a ambos proyectos |
| `inventory-demand-planning` | affaan-m/everything-claude-code | ALTO | BAJO | D5, D11 | Instalar para MWT — prioridad alta |
| `model-hierarchy` | zscole/model-hierarchy-skill | ALTO | ALTO | D1, D9 | Instalar YA — aplica a ambos proyectos |
| `nutrient-document-processing` | PSPDFKit-labs/nutrient-agent-skill | ALTO | ALTO | D6, D12 | Instalar YA — aplica a ambos proyectos |
| `pricing-strategy` | coreyhaines31/marketingskills | ALTO | ALTO | D2, D4 | Instalar YA — aplica a ambos proyectos |
| `qa` | mattpocock/skills | ALTO | ALTO | D1 | Instalar YA — aplica a ambos proyectos |
| `recursive-decomposition` | massimodeluisa/recursive-decomposition-skill | MEDIO | ALTO | D1, D9 | Instalar para FaberLoom — prioridad alta |
| `review` | garrytan/gstack | ALTO | ALTO | D1, D10 | Instalar YA — aplica a ambos proyectos |
| `supabase-postgres-best-practices` | supabase/agent-skills | MEDIO | ALTO | D7, D10 | Instalar para FaberLoom — prioridad alta |
| `tdd` | mattpocock/skills | ALTO | ALTO | D1, D10 | Instalar YA — aplica a ambos proyectos |
| `write-judge-prompt` | hamelsmu/evals-skills | ALTO | ALTO | D1, D10 | Instalar YA — aplica a ambos proyectos |

**Nota de consolidación:** Las skills duplicadas arriba fueron re-scoreadas con visión global. Si una skill era MEDIO en su dimensión original pero tapa un gap crítico de otra dimensión, su score se elevó a ALTO. El score final es el máximo de todas las dimensiones donde aparece.

---

### Top 10 Skills para instalar YA

| # | Skill | Repo | Comando install | Resuelve para | Esfuerzo |
|---|---|---|---|---|---|
| 1 | `ask-questions-if-underspecified` | trailofbits/skills | `npx skills add trailofbits/skills -s ask-questions-if-underspecified` | Previene rework: fuerza al agente a clarificar requisitos ambiguos antes de actuar. Reduce errores en 35+ agentes MWT y en Agent Builder de FaberLoom. | Bajo |
| 2 | `file-todos` | iliaal/ai-skills | `npx skills add iliaal/ai-skills -s file-todos` | Gestión atómica de tareas con trazabilidad completa del ciclo plan→execute→verify. Portable a todos los agentes de ambos proyectos. | Bajo |
| 3 | `copywriting` | coreyhaines31/marketingskills | `npx skills add coreyhaines31/marketingskills --skill copywriting` | Copy de conversión para landing pages de FaberLoom, listings de Amazon MWT, emails B2B y propuestas comerciales. Framework PAS/AIDA/BAB. | Bajo |
| 4 | `kreuzberg` | kreuzberg-dev/kreuzberg | `npx skills add kreuzberg-dev/kreuzberg` | OCR multiformato + extracción de tablas de catálogos PDF de calzado industrial (Marluvas/Tecmater). Core Rust, 97+ formatos. P0 para MWT B2B. | Medio |
| 5 | `browserbase/skills` | browserbase/skills | `npx skills add browserbase/skills` | Anti-bot stealth + CAPTCHA solving + proxies residenciales para scraping comercial de competidores y research de mercado LATAM sin bloqueos. | Medio |
| 6 | `integrate-whatsapp` | gokapso/agent-skills | `npx skills add gokapso/agent-skills@integrate-whatsapp` | Canal dominante B2B en LATAM. Conecta WhatsApp Business API para cotizaciones, pedidos y seguimiento. Esencial para MWT y para FaberLoom agentes virtuales. | Medio |
| 7 | `csv-data-summarizer` | coffeefuelbump/csv-data-summarizer-claude-skill | `npx skills add https://github.com/coffeefuelbump/csv-data-summarizer-claude-skill --skill csv-data-summarizer` | Análisis automático de CSV sin intervención: stats, visualizaciones context-aware, time-series. Aplica a ventas Amazon, pipeline B2B, métricas FaberLoom. | Bajo |
| 8 | `vault-health` | DavidROliverBA/Daves-Claude-Code-Skills | `cp skills/vault-health/*.md .claude/skills/` | Validación de KB markdown MWT (430 archivos): broken wiki-links, orphans, frontmatter YAML, auto-tagging, quality reports. Evita degradación silenciosa de la KB. | Bajo |
| 9 | `supabase-postgres-best-practices` | supabase/agent-skills | `npx skills add supabase/agent-skills` | 30 reglas de Supabase para query performance, RLS policies, schema design, SQL debugging. Crítico para FaberLoom con pgvector multi-tenant. | Bajo |
| 10 | `eval-audit` | hamelsmu/evals-skills | `npx skills add https://github.com/hamelsmu/evals-skills --skill eval-audit` | Audita pipelines de evaluación LLM, detecta problemas metodológicos y prioriza fixes. Base para regression suites de agentes FaberLoom y quality gates MWT. | Medio |

**Criterios aplicados:** Score global ALTO para al menos un proyecto, comando de instalación verificado, no conflicto con skills ya instaladas (`anthropic-skills/*`, `obra/superpowers`, Cowork core), esfuerzo bajo o medio preferido.

---

### Top 5 Gaps para escribir como skill propia

| # | Nombre propuesto | Justificación | Scope de la skill | Prioridad |
|---|---|---|---|---|
| 1 | `ficha-tecnica-extractor` | P0 para MWT B2B. Ningún skill del ecosistema extrae automáticamente especificaciones técnicas de calzado industrial (normas SRA, puntera de acero, suela PU/nitrilo, CA/EP de Brasil) desde catálogos PDF de Marluvas/Tecmater. Kreuzberg y Nutrient extraen texto/tablas genéricas, pero no entienden el dominio del calzado de seguridad. | Skill que orqueste Kreuzberg + schema de extracción específico de calzado: tallas, materiales, normas técnicas, certificaciones. Output estructurado JSON con validación contra catálogo maestro. | P0 — Crítica |
| 2 | `mwt-amazon-sp-api-connector` | MWT tiene credenciales SP-API pero ninguna skill de skills.sh integra SP-API como skill nativa. El MCP de MarceauSolutions existe pero es un runtime externo, no una skill de Claude Code. Sin esto, los agentes no pueden operar datos reales de Amazon (inventory, orders, pricing) de forma nativa. | Skill wrapper SP-API dentro del framework de skills: autenticación OAuth, throttling management, endpoints clásicos (inventory, orders, reports), error handling por código de error Amazon, data freshness validation. | P0 — Crítica |
| 3 | `faberloom-pgvector-tenant-isolation` | FaberLoom usa pgvector multi-tenant con 4 capas de visibilidad. Necesita un skill que codifique el patrón exacto de RLS + row-level embedding ownership + query filtering por organization_id/role/user_id. Supabase-postgres cubre RLS general pero no este patrón híbrido vectorial. | Skill de agente con slash commands que implemente: RLS policies para embeddings, ownership por tenant, hybrid search con filtrado, migraciones de schema, seed data multi-tenant. Basado en Supabase + pgvector + SQLAlchemy. | P0 — Crítica |
| 4 | `lead-enrichment-latam` | CRÍTICA para B2B LATAM. Apollo.io tiene cobertura pobre en PyMEs manufactureras mexicanas/colombianas. No existe skill que integre fuentes LATAM (SIC México, RUES Colombia, directorios industriales) para enriquecer leads B2B de calzado de seguridad/EPP. | Skill que combine scraping ético de directorios locales + APIs públicas + validación telefónica/WhatsApp. Normalización de nombres de empresa, RFC/NIT/RUT, teléfonos +52/+57. Export a Pipedrive/Zoho. | P1 — Alta |
| 5 | `e-invoice-cfdi-mexico` | México es mercado clave para MWT. No existe skill de e-invoicing LATAM en todo el ecosistema de skills.sh. CFDI 4.0, complemento carta porte, retenciones, addendas son obligatorios para operación B2B en México. Similar gap para NFe Brasil y DTE Costa Rica. | Skill que valide XML CFDI 4.0 contra esquema SAT, extraiga datos fiscales (RFC, UUID, total, impuestos), detecte inconsistencias, genere resúmenes para conciliación contable. Extensible a NFe y DTE. | P1 — Alta |

**Criterios aplicados:** Impacto operativo inmediato si se resuelve, no existe alternativa viable en el ecosistema, construible con el stack actual (Python/Pydantic AI, Claude Code).

---

### Conflict Zones

#### 1. Skills que se contradicen entre sí (mismo dominio, instrucciones diferentes)

| Conflicto | Skills involucradas | Recomendación |
|---|---|---|
| **TDD workflow** | `obra/superpowers:test-driven-development` (ya instalado) vs `mattpocock/skills:tdd` vs `NeoLabHQ/context-engineering-kit:tdd` vs `iliaal/ai-skills:writing-tests` | Elegir **UNO**. Sugerencia: quedarse con `obra/superpowers` ya instalado. `NeoLabHQ/tdd` añade comandos slash con subagents si se necesita explícito. |
| **SEO audit** | `coreyhaines31/marketingskills:seo-audit` vs `AgriciDaniel/claude-seo` (19 sub-skills) vs `aaron-he-zhu/seo-geo-claude-skills` (20 skills) | Instalar **solo uno**. Sugerencia: `AgriciDaniel/claude-seo` para depth técnico, o `aaron-he-zhu` para bundle completo. |
| **Code review** | `obra/superpowers:requesting-code-review` (ya instalado) vs `iliaal/ai-skills:code-review` vs `garrytan/gstack:review` vs `NeoLabHQ/context-engineering-kit:review` | `obra/superpowers` cubre el 80%. `iliaal:code-review` complementa con disciplina estructurada. `garrytan:review` añade browser testing. Elegir 1-2 máximo. |
| **PDF processing** | `anthropic-skills/pdf` (ya instalado) vs `kreuzberg-dev/kreuzberg` vs `PSPDFKit-labs/nutrient-agent-skill` vs `claude-office-skills/pdf-ocr` | Usar `anthropic/pdf` para lectura simple, `kreuzberg` para extracción de tablas OCR, `nutrient` para operaciones avanzadas (firma, redacción PII). Definir precedencia en `CLAUDE.md`. |
| **Churn/retention** | `coreyhaines31/marketingskills:churn-prevention` vs `guia-matthieu/clawfu-skills:churn-prediction` vs `phuryn/pm-skills:cohort-analysis` vs `davila7:scikit-survival` | `coreyhaines31:churn-prevention` es más completo para SaaS (36.9K installs). `guia-matthieu:churn-prediction` para detección temprana. `phuryn:cohort-analysis` para análisis de retención. |
| **WhatsApp automation** | `gokapso/agent-skills:integrate-whatsapp/automate-whatsapp/observe-whatsapp` vs `claude-office-skills/skills:whatsapp-automation` vs `bellopushon:whatsapp-cloud-api` | `gokapso` es el ecosistema más completo y maduro para LATAM. Priorizar sobre alternativas. |
| **Handoff/session** | `softaworks/agent-toolkit:session-handoff` vs `boshu2/agentops:handoff` vs `wshobson/agents:on-call-handoff-patterns` vs `obra/superpowers:dispatching-parallel-agents` (ya instalado) | `softaworks:session-handoff` para continuidad entre sesiones de agente. `wshobson:on-call-handoff-patterns` para equipos de agentes por rol. `obra/superpowers` ya cubre dispatching paralelo. |

#### 2. Skills que duplican funcionalidad de plugins ya instalados

| Ya instalado | Skill que duplica | Acción |
|---|---|---|
| `anthropic-skills/pdf` | `kreuzberg`, `nutrient`, `claude-office/pdf-ocr` | Coexistencia con precedencia definida en `CLAUDE.md`. `anthropic/pdf` → lectura simple; `kreuzberg` → tablas OCR; `nutrient` → firma/redacción. |
| `anthropic-skills/xlsx` | `daymade:excel-automation`, `claude-office:excel-automation` | `anthropic/xlsx` cubre lectura/escritura básica. Instalar `daymade/excel-automation` solo si se necesita automatización avanzada (macros, VBA, AppleScript). |
| `obra/superpowers:writing-plans` | `iliaal:planning`, `garrytan:plan-eng-review`, `mattpocock:prd-to-plan` | `obra/superpowers` ya cubre planificación. `iliaal:planning` añade behavioral discipline. `mattpocock:prd-to-plan` puente PRD→plan. Elegir 0-1 adicional. |
| `obra/superpowers:verification-before-completion` | `iliaal:reflect`, `NeoLabHQ:reflexion:reflect`, `garrytan:guard` | `obra` ya cubre verificación. `iliaal:reflect` añade self-reflection post-ejecución. `garrytan:guard` añade guardrails de calidad. Elegir 0-1 adicional. |
| `obra/superpowers:executing-plans` | `am-will/swarms:swarm-planner/parallel-task`, `NeoLabHQ:sdd:implement`, `garrytan:ship` | `obra` ya cubre ejecución. `am-will/swarms` añade ejecución paralela con dependencias. `garrytan:ship` añade release discipline. |

#### 3. Skills cuyo licensing puede ser problema comercial

| Skill | Licencia | Riesgo | Recomendación |
|---|---|---|---|
| `kreuzberg-dev/kreuzberg` | Elastic License 2.0 (ELv2) | Restricciones en uso como servicio gestionado. FaberLoom podría ofrecer procesamiento de documentos como feature del SaaS. | Verificar con legal si FaberLoom puede usar Kreuzberg para procesar documentos de clientes PYMEs en su infraestructura. Alternativa: `nutrient` (comercial, API key) o construir skill propia sobre Tesseract/PaddleOCR (Apache 2.0). |
| `PSPDFKit-labs/nutrient-agent-skill` | Comercial (API key Nutrient) | Costo por documento procesado. 1000 docs/mes en freemium. | Evaluar volumen esperado de procesamiento MWT + FaberLoom. Si >1000 docs/mes, presupuestar plan pago. No es self-hosted. |
| `daymade/claude-code-skills` | Desconocida / Plugin marketplace | Instalación vía `claude plugin install`, no `npx skills add`. Puede no ser portable a Codex/Cursor. | Usar solo si el proyecto es Claude Code-only. Para multi-agente (Codex/Cursor), preferir skills.sh estándar. |
| `alirezarezvani/claude-skills` | MIT (skills), pero marketplace bundle | Instalación vía `/plugin marketplace add`. No está indexado en skills.sh. | 43 skills de marketing útiles pero dependencia del plugin system de Claude Code. Evaluar portabilidad antes de invertir en adopción. |
| `apify/awesome-skills:apify-competitor-intelligence` | Apify commercial (pay-per-result) | Depende de Apify Actors que cobran por ejecución. | Presupuestar uso. Para scraping competitivo a baja escala, `browserbase/skills` puede ser más predecible en costos. |

---

### Recomendación final

Instalar primero las **3 skills de workflow universal** (`ask-questions-if-underspecified`, `file-todos`, `copywriting`) que tienen esfuerzo bajo y beneficio inmediato para ambos proyectos. A continuación, priorizar `kreuzberg` (P0 para MWT B2B) y `browserbase/skills` (research/scraping comercial). En paralelo, instalar `integrate-whatsapp` para activar el canal dominante B2B en LATAM. Para FaberLoom, `supabase-postgres-best-practices` y `vault-health` sientan las bases de backend multi-tenant y mantenimiento de KB. Simultáneamente, iniciar la escritura de las **5 skills propias prioritarias**: `ficha-tecnica-extractor` y `mwt-amazon-sp-api-connector` desbloquean operación crítica de MWT; `faberloom-pgvector-tenant-isolation` es core del producto SaaS; `lead-enrichment-latam` y `e-invoice-cfdi-mexico` cubren gaps legales y comerciales sin alternativa en el mercado. Ignorar de momento skills de frameworks no adoptados (CrewAI, AutoGen), skills con <50 installs sin tracción, y cualquier skill que requiera migración de stack (LangGraph) a menos que FaberLoom decida adoptarlo explícitamente. Finalmente, resolver los Conflict Zones de TDD y SEO audit antes de instalar múltiples skills del mismo dominio, documentando la precedencia en un `CLAUDE.md` de proyecto.

---

### Notas metodológicas de la consolidación

- **12 dimensiones investigadas en paralelo** por agentes especializados.
- **213 skills** identificadas en los reportes individuales.
- **188 skills consolidadas** tras deduplicación (25 apariciones duplicadas eliminadas).
- **100 gaps** detectados a lo largo de las 12 dimensiones.
- **Re-scoring global** aplicado: 24 skills fueron elevadas de MEDIO a ALTO al tapar gaps críticos de otras dimensiones.
- **Skills ya instaladas excluidas**: `anthropic-skills/*` (docx, pdf, pptx, xlsx, schedule, skill-creator), `obra/superpowers` (writing-plans, executing-plans, verification-before-completion, writing-skills), Cowork plugins core.
