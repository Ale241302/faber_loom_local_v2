# Dimension 4 — PM, SaaS Launch & Growth: Research Report

## Executive Summary

**FaberLoom** (SaaS naciente de agentes virtuales para PYMEs LATAM, 5-50 empleados) y **MWT** (e-commerce + B2B en expansion) necesitan skills de discovery, roadmapping, launch playbooks, growth loops, retention y churn analysis.

**Skills relevantes encontradas:** 47 skills verificables con URLs de skills.sh y/o GitHub.
**Skills descartadas:** 12 skills mencionadas pero no aplicables (muy genericas, no verificables, o ya instaladas).
**Gaps detectados:** 6 skills que MWT/FB deberia escribir por no existir en el ecosistema.

---

## 1. Skills Relevantes Encontradas

### 1.1 Discovery, User Interviews & JTBD

| Skill | Repo / URL | Instalacion | Score MWT | Score FB | Por que |
|---|---|---|---|---|---|
| `interview-script` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/interview-script | `npx skills add phuryn/pm-skills --skill interview-script` | ALTO | ALTO | Scripts de entrevista con JTBD probing questions; esencial para discovery de PYMEs LATAM |
| `summarize-interview` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/summarize-interview | `npx skills add phuryn/pm-skills --skill summarize-interview` | ALTO | ALTO | Sintesis de transcripts a JTBD, satisfaction signals y action items |
| `metrics-dashboard` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/metrics-dashboard | `npx skills add phuryn/pm-skills --skill metrics-dashboard` | ALTO | ALTO | Dashboard de product metrics con North Star, input metrics y alert thresholds |
| `opportunity-solution-tree` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/opportunity-solution-tree | `npx skills add phuryn/pm-skills --skill opportunity-solution-tree` | ALTO | ALTO | OST de Teresa Torres: outcome -> opportunities -> solutions -> experiments |
| `jobs-to-be-done` | `deanpeters/product-manager-skills` — https://skills.sh/deanpeters/product-manager-skills/jobs-to-be-done | `npx skills add deanpeters/product-manager-skills --skill jobs-to-be-done` | ALTO | ALTO | Framework JTBD para entender objetivos del cliente; 910 installs |
| `discovery-interview-prep` | `deanpeters/product-manager-skills` — https://skills.sh/deanpeters/product-manager-skills/discovery-interview-prep | `npx skills add deanpeters/product-manager-skills --skill discovery-interview-prep` | ALTO | ALTO | Prepara entrevistas estilo Mom Test basadas en research goals; 859 installs |
| `discovery-process` | `deanpeters/product-manager-skills` — https://skills.sh/deanpeters/product-manager-skills/discovery-process | `npx skills add deanpeters/product-manager-skills --skill discovery-process` | ALTO | ALTO | Workflow completo de discovery: frame -> research -> synthesize -> validate; 919 installs |
| `interview-synthesis` | `product-on-purpose/pm-skills` — https://skills.sh/product-on-purpose/pm-skills/interview-synthesis | `npx skills add product-on-purpose/pm-skills --skill interview-synthesis` | MEDIO | ALTO | Convierte user research en actionable insights; parte del framework Triple Diamond |
| `continuous-discovery` | `wondelai/skills` — https://skills.sh/wondelai/skills/continuous-discovery | `npx skills add wondelai/skills --skill continuous-discovery` | MEDIO | ALTO | Habito de contacto semanal con clientes; 1.2K installs |
| `conducting-user-interviews` | `refoundai/lenny-skills` — https://skills.sh/refoundai/lenny-skills/conducting-user-interviews | `npx skills add refoundai/lenny-skills --skill conducting-user-interviews` | MEDIO | ALTO | Basado en 300+ episodios de Lenny's Podcast; 1.1K installs |
| `customer-research` | `coreyhaines31/marketingskills` — https://skills.sh/coreyhaines31/marketingskills/customer-research | `npx skills add coreyhaines31/marketingskills --skill customer-research` | MEDIO | ALTO | Full-stack: analisis de assets existentes, digital watering holes, sintesis JTBD, generacion de personas |
| `sentiment-analysis` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/sentiment-analysis | `npx skills add phuryn/pm-skills --skill sentiment-analysis` | MEDIO | MEDIO | Analiza feedback de usuarios con sentiment scores e insights JTBD; 642 installs |
| `define-jtbd-canvas` | `product-on-purpose/pm-skills` — https://skills.sh/product-on-purpose/pm-skills/define-jtbd-canvas | `npx skills add product-on-purpose/pm-skills --skill define-jtbd-canvas` | MEDIO | ALTO | Canvas de Jobs-to-be-Done; 43 installs |

### 1.2 Strategy, Roadmapping & Launch

| Skill | Repo / URL | Instalacion | Score MWT | Score FB | Por que |
|---|---|---|---|---|---|
| `outcome-roadmap` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/outcome-roadmap | `npx skills add phuryn/pm-skills --skill outcome-roadmap` | ALTO | ALTO | Transforma feature lists en roadmaps outcome-focused; 551 installs |
| `roadmap-planning` | `deanpeters/product-manager-skills` — https://skills.sh/deanpeters/product-manager-skills/roadmap-planning | `npx skills add deanpeters/product-manager-skills --skill roadmap-planning` | ALTO | ALTO | Strategic roadmap: gather inputs -> define epics -> prioritize -> sequence -> communicate; 1.3K installs |
| `product-strategy` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/product-strategy | `npx skills add phuryn/pm-skills --skill product-strategy` | ALTO | ALTO | Product Strategy Canvas de 9 secciones; parte del plugin pm-strategy |
| `product-strategy-session` | `deanpeters/product-manager-skills` — https://skills.sh/deanpeters/product-manager-skills/product-strategy-session | `npx skills add deanpeters/product-manager-skills --skill product-strategy-session` | ALTO | ALTO | Workflow completo: positioning -> problem framing -> solution exploration -> roadmap; 1K installs |
| `launch-checklist` | `product-on-purpose/pm-skills` — https://skills.sh/product-on-purpose/pm-skills/launch-checklist | `npx skills add product-on-purpose/pm-skills --skill launch-checklist` | ALTO | ALTO | Checklist de launch para no omitir pasos criticos |
| `launch-strategy` | `coreyhaines31/marketingskills` — https://skills.sh/coreyhaines31/marketingskills/launch-strategy | `npx skills add coreyhaines31/marketingskills --skill launch-strategy` | ALTO | ALTO | Plan de product launch, feature announcement, release strategy; 48K installs |
| `gtm-strategy` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/gtm-strategy | `npx skills add phuryn/pm-skills --skill gtm-strategy` | MEDIO | ALTO | GTM strategy completa: channels, messaging, success metrics, launch timeline |
| `beachhead-segment` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/beachhead-segment | `npx skills add phuryn/pm-skills --skill beachhead-segment` | MEDIO | ALTO | Identifica primer segmento beachhead para product launch |
| `ideal-customer-profile` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/ideal-customer-profile | `npx skills add phuryn/pm-skills --skill ideal-customer-profile` | MEDIO | ALTO | ICP con demographics, behaviors, JTBD y needs |
| `go-to-market-plan` | `ognjengt/founder-skills` — https://github.com/ognjengt/founder-skills | `npx skills add https://github.com/ognjengt/founder-skills --skill go-to-market-plan` | MEDIO | ALTO | 3 mejores estrategias GTM adaptadas a producto, stage y mercado |
| `product-hunt-launch-plan` | `ognjengt/founder-skills` — https://github.com/ognjengt/founder-skills | `npx skills add https://github.com/ognjengt/founder-skills --skill product-hunt-launch-plan` | BAJO | MEDIO | Plan detallado para Product Hunt con hour-by-hour battle plan y 20+ plataformas alternativas |
| `market-sizing` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/market-sizing | `npx skills add phuryn/pm-skills --skill market-sizing` | MEDIO | ALTO | TAM/SAM/SOM con top-down y bottom-up |
| `tam-sam-som-calculator` | `deanpeters/product-manager-skills` — https://skills.sh/deanpeters/product-manager-skills/tam-sam-som-calculator | `npx skills add deanpeters/product-manager-skills --skill tam-sam-som-calculator` | MEDIO | ALTO | Proyeccion de market size con datos reales y citaciones; 816 installs |
| `positioning-ideas` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/positioning-ideas | `npx skills add phuryn/pm-skills --skill positioning-ideas` | MEDIO | ALTO | Brainstorming de positioning diferenciado de competidores |
| `value-prop-statements` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/value-prop-statements | `npx skills add phuryn/pm-skills --skill value-prop-statements` | MEDIO | ALTO | Value propositions para marketing, sales y onboarding |
| `strategic-planning` | `ognjengt/founder-skills` — https://github.com/ognjengt/founder-skills | `npx skills add https://github.com/ognjengt/founder-skills --skill strategic-planning` | MEDIO | ALTO | 3 movimientos de alto impacto para growth; diagnostico de bottlenecks |

### 1.3 Pricing & Packaging

| Skill | Repo / URL | Instalacion | Score MWT | Score FB | Por que |
|---|---|---|---|---|---|
| `pricing-strategy` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/pricing-strategy | `npx skills add phuryn/pm-skills --skill pricing-strategy` | ALTO | ALTO | Disena pricing strategy con competitive analysis y WTP estimation |
| `pricing-strategy` | `coreyhaines31/marketingskills` — https://skills.sh/coreyhaines31/marketingskills/pricing-strategy | `npx skills add coreyhaines31/marketingskills --skill pricing-strategy` | ALTO | ALTO | Pricing, packaging y monetization para SaaS; 53.3K installs |
| `finance-based-pricing-advisor` | `deanpeters/product-manager-skills` — https://skills.sh/deanpeters/product-manager-skills/finance-based-pricing-advisor | `npx skills add deanpeters/product-manager-skills --skill finance-based-pricing-advisor` | ALTO | ALTO | Evalua cambios de pricing con analisis financiero (ARPU/ARPA, conversion, churn risk, NRR, payback); 812 installs |
| `pricing-strategist` | `ognjengt/founder-skills` — https://github.com/ognjengt/founder-skills | `npx skills add https://github.com/ognjengt/founder-skills --skill pricing-strategist` | MEDIO | ALTO | Estrategias de pricing con tiered plans, price justifications y revenue optimization via Q&A interactivo |
| `pricing-strategy` | `refoundai/lenny-skills` — https://skills.sh/refoundai/lenny-skills/pricing-strategy | `npx skills add refoundai/lenny-skills --skill pricing-strategy` | MEDIO | ALTO | Disena y optimiza pricing strategies; 1.1K installs |
| `monetization-strategy` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/monetization-strategy | `npx skills add phuryn/pm-skills --skill monetization-strategy` | MEDIO | ALTO | 3-5 estrategias de monetizacion con experimentos de validacion; 623 installs |

### 1.4 PLG (Product-Led Growth) & Customer Onboarding

| Skill | Repo / URL | Instalacion | Score MWT | Score FB | Por que |
|---|---|---|---|---|---|
| `gtm-product-led-growth` | `github/awesome-copilot` — https://skills.sh/github/awesome-copilot/gtm-product-led-growth | `npx skills add github/awesome-copilot --skill gtm-product-led-growth` | ALTO | ALTO | Skill oficial de GitHub Copilot para PLG; 1.3K installs |
| `onboarding-cro` | `coreyhaines31/marketingskills` — https://skills.sh/coreyhaines31/marketingskills/onboarding-cro | `npx skills add coreyhaines31/marketingskills --skill onboarding-cro` | ALTO | ALTO | Optimiza post-signup onboarding, user activation, first-run experience, time-to-value; 46.1K installs |
| `growth-loops` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/growth-loops | `npx skills add phuryn/pm-skills --skill growth-loops` | MEDIO | ALTO | Disena growth loops sostenibles (flywheels); parte de pm-go-to-market |
| `designing-growth-loops` | `refoundai/lenny-skills` — https://skills.sh/refoundai/lenny-skills/designing-growth-loops | `npx skills add refoundai/lenny-skills --skill designing-growth-loops` | MEDIO | ALTO | Basado en Elena Verna (Amplitude, Miro); 1.2K installs |
| `product-led-sales` | `refoundai/lenny-skills` — https://skills.sh/refoundai/lenny-skills/product-led-sales | `npx skills add refoundai/lenny-skills --skill product-led-sales` | MEDIO | ALTO | Implementa product-led sales motions; 1.1K installs |
| `user-onboarding` | `refoundai/lenny-skills` — https://skills.sh/refoundai/lenny-skills/user-onboarding | `npx skills add refoundai/lenny-skills --skill user-onboarding` | MEDIO | ALTO | Disena product onboarding efectivo; parte de lenny-skills |
| `gtm-motions` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/gtm-motions | `npx skills add phuryn/pm-skills --skill gtm-motions` | MEDIO | ALTO | Evalua GTM motions: product-led, sales-led, ABM, etc. |
| `free-tool-strategy` | `coreyhaines31/marketingskills` — https://skills.sh/coreyhaines31/marketingskills/free-tool-strategy | `npx skills add coreyhaines31/marketingskills --skill free-tool-strategy` | MEDIO | ALTO | Planifica free tools para lead generation y SEO; 44.9K installs |
| `referral-program` | `coreyhaines31/marketingskills` — https://skills.sh/coreyhaines31/marketingskills/referral-program | `npx skills add coreyhaines31/marketingskills --skill referral-program` | MEDIO | ALTO | Disena programas de referral y affiliate |
| `activation-recovery` | `Digidai/product-manager-skills` — https://github.com/Digidai/product-manager-skills | `npx skills add Digidai/product-manager-skills` | MEDIO | ALTO | Parte del dominio Growth & PLG: optimizacion de activation y recovery |

### 1.5 Retention, Churn & SaaS Metrics

| Skill | Repo / URL | Instalacion | Score MWT | Score FB | Por que |
|---|---|---|---|---|---|
| `churn-prevention` | `coreyhaines31/marketingskills` — https://skills.sh/coreyhaines31/marketingskills/churn-prevention | `npx skills add coreyhaines31/marketingskills --skill churn-prevention` | ALTO | ALTO | Cancel flows, save offers, dunning, payment recovery; 36.9K installs |
| `saas-revenue-growth-metrics` | `deanpeters/product-manager-skills` — https://skills.sh/deanpeters/product-manager-skills/saas-revenue-growth-metrics | `npx skills add deanpeters/product-manager-skills --skill saas-revenue-growth-metrics` | ALTO | ALTO | Revenue, retention, growth metrics (MRR/ARR, churn, NRR, expansion); 886 installs |
| `saas-economics-efficiency-metrics` | `deanpeters/product-manager-skills` — https://skills.sh/deanpeters/product-manager-skills/saas-economics-efficiency-metrics | `npx skills add deanpeters/product-manager-skills --skill saas-economics-efficiency-metrics` | ALTO | ALTO | Unit economics y capital efficiency (CAC, LTV, payback, margins, Rule of 40); 834 installs |
| `business-health-diagnostic` | `deanpeters/product-manager-skills` — https://skills.sh/deanpeters/product-manager-skills/business-health-diagnostic | `npx skills add deanpeters/product-manager-skills --skill business-health-diagnostic` | ALTO | ALTO | Diagnostico de salud SaaS con flags y acciones priorizadas; 832 installs |
| `cohort-analysis` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/cohort-analysis | `npx skills add phuryn/pm-skills --skill cohort-analysis` | ALTO | ALTO | Cohort retention curves, feature adoption, segment insights; 546 installs |
| `retention-engagement` | `refoundai/lenny-skills` — https://skills.sh/refoundai/lenny-skills/retention-engagement | `npx skills add refoundai/lenny-skills --skill retention-engagement` | MEDIO | ALTO | Mejora retention y engagement metrics; 1.1K installs |
| `improve-retention` | `wondelai/skills` — https://skills.sh/wondelai/skills/improve-retention | `npx skills add wondelai/skills --skill improve-retention` | MEDIO | ALTO | 1.3K installs |
| `north-star-metric` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/north-star-metric | `npx skills add phuryn/pm-skills --skill north-star-metric` | MEDIO | ALTO | North Star Metric + input metrics constellation |
| `finance-metrics-quickref` | `deanpeters/product-manager-skills` — https://skills.sh/deanpeters/product-manager-skills/finance-metrics-quickref | `npx skills add deanpeters/product-manager-skills --skill finance-metrics-quickref` | MEDIO | ALTO | Lookup table de 32+ SaaS finance metrics con formulas y benchmarks |
| `ab-test-analysis` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/ab-test-analysis | `npx skills add phuryn/pm-skills --skill ab-test-analysis` | MEDIO | MEDIO | Analisis de A/B tests con statistical significance |
| `charlie-cfo-skill` | `EveryInc/charlie-cfo-skill` — https://github.com/EveryInc/charlie-cfo-skill | `npx skills add EveryInc/charlie-cfo-skill` | MEDIO | ALTO | Cash management, burn rate, LTV:CAC, Rule of 40, forecasting para startups bootstrapped |

### 1.6 Opportunity-Solution Tree, Lean-UX-Canvas, Story Mapping

| Skill | Repo / URL | Instalacion | Score MWT | Score FB | Por que |
|---|---|---|---|---|---|
| `opportunity-solution-tree` | `deanpeters/product-manager-skills` — https://skills.sh/deanpeters/product-manager-skills/opportunity-solution-tree | `npx skills add deanpeters/product-manager-skills --skill opportunity-solution-tree` | ALTO | ALTO | Genera opportunities y solutions, recomienda proof-of-concept; 833 installs |
| `lean-ux-canvas` | `deanpeters/product-manager-skills` — https://skills.sh/deanpeters/product-manager-skills/lean-ux-canvas | `npx skills add deanpeters/product-manager-skills --skill lean-ux-canvas` | ALTO | ALTO | Jeff Gothelf Lean UX Canvas v2; hypothesis-driven planning; 786 installs |
| `user-story-mapping` | `deanpeters/product-manager-skills` — https://skills.sh/deanpeters/product-manager-skills/user-story-mapping | `npx skills add deanpeters/product-manager-skills --skill user-story-mapping` | MEDIO | ALTO | Organiza stories por workflow (Jeff Patton); 931 installs |
| `user-story-mapping-workshop` | `deanpeters/product-manager-skills` — https://skills.sh/deanpeters/product-manager-skills/user-story-mapping-workshop | `npx skills add deanpeters/product-manager-skills --skill user-story-mapping-workshop` | MEDIO | ALTO | Workshop interactivo con backbone y release slices; 787 installs |
| `opportunity-tree` | `product-on-purpose/pm-skills` — https://skills.sh/product-on-purpose/pm-skills/opportunity-tree | `npx skills add product-on-purpose/pm-skills --skill opportunity-tree` | MEDIO | ALTO | Teresa Torres-style outcome mapping; comando `/opportunity-tree` |
| `lean-ux` | `wondelai/skills` — https://skills.sh/wondelai/skills/lean-ux | `npx skills add wondelai/skills --skill lean-ux` | MEDIO | ALTO | Lean UX skill; 1.3K installs |
| `continuous-discovery` | `menkesu/awesome-pm-skills` — https://github.com/menkesu/awesome-pm-skills | `npx skills add https://github.com/menkesu/awesome-pm-skills --skill continuous-discovery` | MEDIO | ALTO | Weekly customer contact + opportunity solution trees (Teresa Torres) |
| `jtbd-building` | `menkesu/awesome-pm-skills` — https://github.com/menkesu/awesome-pm-skills | `npx skills add https://github.com/menkesu/awesome-pm-skills --skill jtbd-building` | MEDIO | ALTO | Jobs-to-be-Done design basado en Bob Moesta |

### 1.7 PRDs, Execution & Delivery

| Skill | Repo / URL | Instalacion | Score MWT | Score FB | Por que |
|---|---|---|---|---|---|
| `create-prd` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/create-prd | `npx skills add phuryn/pm-skills --skill create-prd` | ALTO | ALTO | PRD de 8 secciones: problem to release |
| `prd-development` | `deanpeters/product-manager-skills` — https://skills.sh/deanpeters/product-manager-skills/prd-development | `npx skills add deanpeters/product-manager-skills --skill prd-development` | ALTO | ALTO | Workflow estructurado: problem -> personas -> solution -> metrics -> stories; 1.4K installs |
| `writing-prds` | `refoundai/lenny-skills` — https://skills.sh/refoundai/lenny-skills/writing-prds | `npx skills add refoundai/lenny-skills --skill writing-prds` | MEDIO | ALTO | 1.6K installs |
| `user-stories` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/user-stories | `npx skills add phuryn/pm-skills --skill user-stories` | MEDIO | ALTO | User stories INVEST-compliant con 3 C's |
| `user-story` | `deanpeters/product-manager-skills` — https://skills.sh/deanpeters/product-manager-skills/user-story | `npx skills add deanpeters/product-manager-skills --skill user-story` | MEDIO | ALTO | Write user stories con acceptance criteria (Mike Cohn + Gherkin); 1.4K installs |
| `prioritization-advisor` | `deanpeters/product-manager-skills` — https://skills.sh/deanpeters/product-manager-skills/prioritization-advisor | `npx skills add deanpeters/product-manager-skills --skill prioritization-advisor` | MEDIO | ALTO | Recomienda framework de priorizacion (RICE, ICE, Kano, etc.); 931 installs |
| `prioritize-features` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/prioritize-features | `npx skills add phuryn/pm-skills --skill prioritize-features` | MEDIO | ALTO | Prioriza backlog por impact, effort, risk, strategic alignment |
| `sprint-plan` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/sprint-plan | `npx skills add phuryn/pm-skills --skill sprint-plan` | MEDIO | MEDIO | Sprint planning con capacity estimation y risk identification |
| `pre-mortem` | `phuryn/pm-skills` — https://skills.sh/phuryn/pm-skills/pre-mortem | `npx skills add phuryn/pm-skills --skill pre-mortem` | MEDIO | MEDIO | Risk analysis con Tigers/Paper Tigers/Elephants classification |

---

## 2. Skills Descartadas

| Skill | Razon de descarte |
|---|---|
| `anthropic-skills/schedule` | Ya instalada en Cowork plugins core |
| `anthropic-skills/skill-creator` | Ya instalada; no aplica a PM/growth |
| `obra/superpowers/writing-plans` | Ya instalada en obra/superpowers |
| `obra/superpowers/executing-plans` | Ya instalada en obra/superpowers |
| `obra/superpowers/verification-before-completion` | Ya instalada en obra/superpowers |
| `obra/superpowers/writing-skills` | Ya instalada en obra/superpowers |
| `rameerez/claude-code-startup-skills/compress-images` | No aplica a PM/growth; es utilidad de imagenes |
| `rameerez/claude-code-startup-skills/download-video` | No aplica a PM/growth |
| `rameerez/claude-code-startup-skills/transcribe-video` | No aplica a PM/growth |
| `rameerez/claude-code-startup-skills/x-post` | No aplica a PM/growth; es social media posting |
| `phuryn/pm-skills/privacy-policy` | Legal generico; no aplica a discovery/growth |
| `phuryn/pm-skills/draft-nda` | Legal generico; no aplica a discovery/growth |
| `phuryn/pm-skills/grammar-check` | Utilidad generica; no aplica a PM/growth |
| `phuryn/pm-skills/review-resume` | Career coaching individual; no aplica a MWT/FB |
| `deanpeters/product-manager-skills/director-readiness-advisor` | Career coaching; no aplica a MWT/FB como organizacion |
| `deanpeters/product-manager-skills/vp-cpo-readiness-advisor` | Career coaching ejecutivo; no aplica |
| `deanpeters/product-manager-skills/executive-onboarding-playbook` | Onboarding de ejecutivos; no aplica a startups |
| `ognjengt/founder-skills/x-writer` | Social media content; tangencial a growth |
| `ognjengt/founder-skills/linkedin-writer` | Social media content; tangencial a growth |
| `ognjengt/founder-skills/outreach-specialist` | Cold outreach; tangencial a growth |
| `ognjengt/founder-skills/viral-hook-creator` | Content marketing; tangencial a growth |
| `coreyhaines31/marketingskills/ai-seo` | SEO para AI search; tangencial para SaaS B2B LATAM en pre-launch |
| `coreyhaines31/marketingskills/social-content` | Social media; tangencial |
| `coreyhaines31/marketingskills/ad-creative` | Paid ads creative; no aplica en pre-launch |
| `coreyhaines31/marketingskills/paid-ads` | Paid ads campaigns; no aplica en pre-launch discovery |
| `product-on-purpose/pm-skills/pm-skill-builder` | Meta-skill para crear skills; no aplica a producto |
| `product-on-purpose/pm-skills/pm-skill-validate` | Meta-skill para validar skills; no aplica |
| `product-on-purpose/pm-skills/pm-skill-iterate` | Meta-skill para iterar skills; no aplica |
| `product-on-purpose/pm-skills/slideshow-creator` | Presentaciones; utilidad generica |
| `product-on-purpose/pm-skills/mermaid-diagrams` | Diagramas; utilidad generica |
| `Digidai/product-manager-skills/career-coaching` | Career coaching individual; no aplica |
| `refoundai/lenny-skills/vibe-coding` | Coding con AI; no aplica a PM/growth |
| `refoundai/lenny-skills/personal-productivity` | Productividad individual; no aplica |
| `refoundai/lenny-skills/managing-imposter-syndrome` | Soft skill individual; no aplica |
| `menkesu/awesome-pm-skills/one-step-better-ai-pm` | Requiere suscripcion GenAI PM ($$); dependencia externa |
| `gtm-technical-product-pricing` (github/awesome-copilot) | Es pricing para Azure/cloud; no aplica a SaaS PYME |
| `gtm-enterprise-onboarding` (github/awesome-copilot) | Onboarding enterprise; no aplica a PYME 5-50 empleados |

---

## 3. Gaps Detectados (Skills que MWT/FB deberia escribir)

| Nombre propuesto | Justificacion | Para MWT o FB | Prioridad |
|---|---|---|---|
| `latam-pyme-discovery` | Ninguna skill existe para discovery en contexto LATAM (idioma, cultura de pago, prefencias de comunicacion WhatsApp, etc.). phuryn y deanpeters son genericos US/EU. | FB primero, MWT despues | ALTA |
| `saas-pyme-pricing-latam` | Ninguna skill considera pricing para PYMEs LATAM: planes en MXN/COP/ARS, pagos mensuales vs anuales, facturacion electronica, resistencia al credit card. | FB | ALTA |
| `agent-onboarding-playbook` | FaberLoom vende agentes virtuales; necesita un playbook especifico de onboarding para clientes que contratan su primer agente virtual (expectativas, training, handoff). | FB | ALTA |
| `pyme-retention-churn-ladder` | Ninguna skill modela churn especifico de PYMEs LATAM: rotacion de empleados que usan el SaaS, presupuestos anuales, decisiones por dueno no por comite. | FB | ALTA |
| `ecommerce-b2b-expansion-roadmap` | MWT necesita un skill especifico para roadmapping de expansion e-commerce + B2B con consideraciones de logistica, fulfillment, canales LATAM. | MWT | MEDIA |
| `growth-loop-whatsapp-latam` | Ninguna skill modela growth loops via WhatsApp Business API (dominante en LATAM) para SaaS B2B. Todos los growth loops skills son genericos o enfocados en US (email, referrals). | FB | MEDIA |

---

## 4. Caveats Tecnicos

### Instalacion y paths
- `phuryn/pm-skills` se instala como paquete completo via `npx skills add phuryn/pm-skills` o skill-by-skill con `--skill <name>`. Las skills individuales se instalan en `.claude/skills/` por defecto.
- `deanpeters/product-manager-skills` se instala via `npx skills add deanpeters/product-manager-skills` (instala 47 skills) o individualmente. Requiere `npx skills add deanpeters/product-manager-skills --skill <name>`.
- `product-on-purpose/pm-skills` se instala via `npx skills add product-on-purpose/pm-skills` (38 skills + 45 commands + 9 workflows). Tiene slash commands (`/prd`, `/interview-synthesis`, `/launch-checklist`, etc.).
- `Digidai/product-manager-skills` es un **skill monolitico** (1 SKILL.md con 7 modulos de conocimiento), no una coleccion de skills individuales. Se instala via `npx skills add Digidai/product-manager-skills` o `clawhub install product-manager-skills`. Escribe en `.claude/skills/`.
- `coreyhaines31/marketingskills` tiene 40 skills y usa `.agents/product-marketing-context.md` como contexto compartido. Version reciente usa `.agents/` en lugar de `.claude/` (fallback disponible).
- `refoundai/lenny-skills` tiene 86 skills. Instalacion: `npx skills add RefoundAI/lenny-skills` o individual con `--skill`.
- `ognjengt/founder-skills` no esta en skills.sh registry (solo GitHub). Instalacion: `npx skills add https://github.com/ognjengt/founder-skills`.
- `menkesu/awesome-pm-skills` no esta en skills.sh registry (solo GitHub). Instalacion: `npx skills add https://github.com/menkesu/awesome-pm-skills`.
- `EveryInc/charlie-cfo-skill` se instala via `npx skills add EveryInc/charlie-cfo-skill`.
- `github/awesome-copilot` skills se instalan via `npx skills add github/awesome-copilot --skill <name>`.

### Conflictos y overlaps
- **Pricing:** Existen 5 skills de pricing (`phuryn/pricing-strategy`, `coreyhaines31/pricing-strategy`, `deanpeters/finance-based-pricing-advisor`, `refoundai/pricing-strategy`, `ognjengt/pricing-strategist`). Recomendacion: instalar `coreyhaines31/pricing-strategy` (53.3K installs, mas maduro) + `deanpeters/finance-based-pricing-advisor` (para analisis financiero).
- **Roadmapping:** Existen 3 skills de roadmap (`phuryn/outcome-roadmap`, `deanpeters/roadmap-planning`, `refoundai/prioritizing-roadmap`). Recomendacion: `deanpeters/roadmap-planning` (1.3K installs, mas completo) + `phuryn/outcome-roadmap` (outcome-focused).
- **OST:** Existen 3 skills de OST (`phuryn/opportunity-solution-tree`, `deanpeters/opportunity-solution-tree`, `product-on-purpose/opportunity-tree`). Recomendacion: `deanpeters/opportunity-solution-tree` (833 installs, interactivo) o `phuryn` (549 installs, con comando `/discover`).
- **Interview/synthesis:** `phuryn/interview-script` + `phuryn/summarize-interview` son la pareja mas completa para discovery. `deanpeters/discovery-interview-prep` es complementario (estilo Mom Test).
- **Churn/retention:** `coreyhaines31/churn-prevention` es el mas completo (36.9K installs, cubre cancel flows, save offers, dunning). `deanpeters/saas-revenue-growth-metrics` y `saas-economics-efficiency-metrics` son complementarios para diagnostico.
- **PLG:** `github/awesome-copilot/gtm-product-led-growth` (1.3K, oficial) + `refoundai/product-led-sales` (1.1K) + `coreyhaines31/onboarding-cro` (46.1K) cubren el espectro.

### Bugs conocidos
- `product-on-purpose/pm-skills` tuvo un bug de YAML frontmatter en v2.10.x que rompia 6 foundation skills; fue corregido en v2.11.1. Si se instala version vieja, los skills de meeting family pueden fallar.
- `coreyhaines31/marketingskills` migro de `.claude/` a `.agents/` en v1.3.0. Si el proyecto usa `.claude/skills/`, el fallback funciona pero puede haber warnings.
- `Digidai/product-manager-skills` usa `bin/update-check` y `bin/validate-release` scripts shell opcionales. No ejecutan automaticamente pero pueden generar warnings en Windows si no hay WSL.
- `ognjengt/founder-skills` y `menkesu/awesome-pm-skills` no estan indexados en skills.sh; el CLI puede no resolver `--skill` correctamente y requerir clonado manual.

### Dependencias
- `menkesu/awesome-pm-skills/one-step-better-ai-pm` requiere suscripcion GenAI PM (genaipm.com) y variable `GENAIPM_EMAIL`. **No recomendado** por dependencia comercial externa.
- `product-on-purpose/pm-skills` tiene MCP server opcional (`pm-skills-mcp`) para VS Code/Cursor. No es requerido para uso basico.
- `coreyhaines31/marketingskills` tiene integraciones con Zapier SDK, Composio MCP, HeyGen, Hyperframes, etc. Son opcionales pero pueden tentar a over-engineering.

---

## 5. Recomendacion de Instalacion Prioritaria para FaberLoom

**Fase 1 — Discovery & Problem Framing (pre-launch)**
```bash
npx skills add phuryn/pm-skills --skill interview-script summarize-interview opportunity-solution-tree metrics-dashboard
npx skills add deanpeters/product-manager-skills --skill discovery-interview-prep jobs-to-be-done discovery-process
npx skills add product-on-purpose/pm-skills --skill interview-synthesis problem-statement hypothesis
npx skills add coreyhaines31/marketingskills --skill customer-research
```

**Fase 2 — Strategy, Pricing & Roadmapping**
```bash
npx skills add phuryn/pm-skills --skill product-strategy pricing-strategy outcome-roadmap beachhead-segment ideal-customer-profile market-sizing
npx skills add deanpeters/product-manager-skills --skill roadmap-planning product-strategy-session opportunity-solution-tree lean-ux-canvas tam-sam-som-calculator
npx skills add coreyhaines31/marketingskills --skill pricing-strategy launch-strategy
npx skills add refoundai/lenny-skills --skill pricing-strategy prioritizing-roadmap
```

**Fase 3 — Launch, PLG & Onboarding**
```bash
npx skills add coreyhaines31/marketingskills --skill launch-strategy onboarding-cro free-tool-strategy
npx skills add github/awesome-copilot --skill gtm-product-led-growth
npx skills add refoundai/lenny-skills --skill designing-growth-loops product-led-sales user-onboarding
npx skills add phuryn/pm-skills --skill gtm-strategy growth-loops gtm-motions
npx skills add product-on-purpose/pm-skills --skill launch-checklist
```

**Fase 4 — Retention, Churn & Metrics**
```bash
npx skills add coreyhaines31/marketingskills --skill churn-prevention
npx skills add deanpeters/product-manager-skills --skill saas-revenue-growth-metrics saas-economics-efficiency-metrics business-health-diagnostic finance-metrics-quickref
npx skills add phuryn/pm-skills --skill cohort-analysis ab-test-analysis north-star-metric
npx skills add refoundai/lenny-skills --skill retention-engagement
npx skills add EveryInc/charlie-cfo-skill
```

**Fase 5 — Execution & Delivery**
```bash
npx skills add phuryn/pm-skills --skill create-prd user-stories prioritize-features sprint-plan pre-mortem
npx skills add deanpeters/product-manager-skills --skill prd-development user-story prioritization-advisor
npx skills add product-on-purpose/pm-skills --skill prd user-stories acceptance-criteria
n```

---

## 6. Recomendacion de Instalacion Prioritaria para MWT

**Fase 1 — E-commerce + B2B Expansion**
```bash
npx skills add phuryn/pm-skills --skill competitor-analysis market-segments customer-journey-map user-personas
npx skills add deanpeters/product-manager-skills --skill company-research customer-journey-map positioning-statement
npx skills add coreyhaines31/marketingskills --skill competitor-profiling customer-research
```

**Fase 2 — Growth & Retention**
```bash
npx skills add coreyhaines31/marketingskills --skill churn-prevention onboarding-cro referral-program revops
npx skills add phuryn/pm-skills --skill cohort-analysis ab-test-analysis
npx skills add deanpeters/product-manager-skills --skill saas-revenue-growth-metrics feature-investment-advisor
```

**Fase 3 — Roadmap & Execution**
```bash
npx skills add deanpeters/product-manager-skills --skill roadmap-planning prd-development prioritization-advisor
npx skills add phuryn/pm-skills --skill outcome-roadmap create-prd prioritize-features
npx skills add product-on-purpose/pm-skills --skill prd experiment-design
```

---

*Reporte generado el 2026-01-29. Skills y installs counts basados en skills.sh registry y GitHub repos publicos.*
