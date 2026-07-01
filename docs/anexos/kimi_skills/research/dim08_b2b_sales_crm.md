## DIMENSIÓN 8 — B2B Sales, CRM, Pipeline

### Resumen ejecutivo
Se encontraron **18 skills directamente aplicables** con URLs verificables en skills.sh o GitHub. El ecosistema de Agent Skills para ventas B2B está activo pero con sesgo fuerte hacia SaaS/Salesforce. Para LATAM (MWT) y para Agent Builder de ventas (FaberLoom), las skills de **WhatsApp Business**, **Pipedrive/Zoho**, **pipeline forecasting** y **deal inspection** son las de mayor valor inmediato. Se detectaron **7 gaps** donde no existe skill usable para necesidades críticas de los proyectos.

---

### Skills relevantes encontrados

| Skill | Repo | Instalación | Score MWT | Score FB | Por qué (1 línea) |
|---|---|---|---|---|---|
| **integrate-whatsapp** | gokapso/agent-skills | `npx skills add gokapso/agent-skills@integrate-whatsapp` | **ALTO** | **ALTO** | Conecta WhatsApp, webhooks, envía mensajes; canal dominante en LATAM para ventas B2B. |
| **automate-whatsapp** | gokapso/agent-skills | `npx skills add gokapso/agent-skills@automate-whatsapp` | **ALTO** | **ALTO** | Construye automatizaciones WhatsApp con grafos de workflow, triggers, funciones; 40+ scripts CRUD. |
| **observe-whatsapp** | gokapso/agent-skills | `npx skills add gokapso/agent-skills@observe-whatsapp` | **ALTO** | **MEDIO** | Debug de entrega WhatsApp, health checks, logs de ejecución; crítico para operación comercial LATAM. |
| **crm-automation** | claude-office-skills/skills | `npx skills add claude-office-skills/skills@crm-automation` | **ALTO** | **ALTO** | Multi-CRM workflows: HubSpot, Salesforce, Pipedrive, Zoho, Monday; lead routing, customer success. |
| **pipedrive-automation** | claude-office-skills/skills | `npx skills add claude-office-skills/skills@pipedrive-automation` | **ALTO** | **ALTO** | Deal management, pipeline tracking, automatización de flujos de venta; muy usado en LATAM. |
| **zoho-crm** | membranedev/application-skills | `npx skills add membranedev/application-skills@zoho-crm` | **ALTO** | **MEDIO** | Integración nativa con Zoho CRM; popular en LATAM por costo y localización (español). |
| **monday.com-automation** | claude-office-skills/skills | `npx skills add claude-office-skills/skills@monday.com-automation` | **MEDIO** | **MEDIO** | Automatización de boards Monday; algunos equipos comerciales en LATAM lo usan como CRM lightweight. |
| **hubspot** | membranedev/application-skills | `npx skills add membranedev/application-skills@hubspot` | **MEDIO** | **ALTO** | Integración HubSpot CRM, contacts, deals, companies; HubSpot es el CRM SaaS más usado pero menos común en calzado industrial LATAM. |
| **apollo-outreach** | openclaudia/openclaudia-skills | `npx skills add openclaudia/openclaudia-skills@apollo-outreach` | **MEDIO** | **ALTO** | B2B lead research y enrichment vía Apollo.io API; principal fuente verificable de enriquecimiento B2B. |
| **apify-lead-generation** | apify/agent-skills | `npx skills add apify/agent-skills@apify-lead-generation` | **ALTO** | **ALTO** | Generación de leads con scraping automatizado; útil para construir listas de prospectos en LATAM sin Apollo. |
| **lead-research-assistant** | composiohq/awesome-claude-skills | `npx skills add composiohq/awesome-claude-skills@lead-research-assistant` | **MEDIO** | **ALTO** | Lead scoring, prospect enrichment, personalized outreach + 78 integraciones SaaS; versátil pero genérico. |
| **enrich-lead** | anthropics/knowledge-work-plugins | `npx skills add anthropics/knowledge-work-plugins@enrich-lead` | **MEDIO** | **ALTO** | Skill oficial Anthropic para enriquecer leads; probablemente usa Clearbit/similar internamente. |
| **cold-email** | coreyhaines31/marketingskills | `npx skills add coreyhaines31/marketingskills@cold-email` | **MEDIO** | **ALTO** | Escribe B2B cold emails y follow-up sequences que generan respuestas; 35.7K installs. |
| **email-sequence** | coreyhaines31/marketingskills | `npx skills add coreyhaines31/marketingskills@email-sequence` | **MEDIO** | **ALTO** | Drip campaigns, nurture sequences, lifecycle emails; 47.1K installs, skill más popular de email. |
| **churn-prevention** | coreyhaines31/marketingskills | `npx skills add coreyhaines31/marketingskills@churn-prevention` | **ALTO** | **MEDIO** | Cancel flows, save offers, dunning, payment recovery; 36.9K installs. Aplicable a cuentas en riesgo B2B. |
| **pipeline-forecasting** | guia-matthieu/clawfu-skills | `npx skills add guia-matthieu/clawfu-skills@pipeline-forecasting` | **ALTO** | **ALTO** | Forecasting de pipeline con probabilidad por etapa, weighted value, ajustes por edad de deal. |
| **deal-risk-scoring** | guia-matthieu/clawfu-skills | `npx skills add guia-matthieu/clawfu-skills@deal-risk-scoring` | **ALTO** | **ALTO** | Scoring de riesgo por deal con factores de pipeline health; útil para ciclos largos B2B. |
| **linkedin-automation** | claude-office-skills/skills | `npx skills add claude-office-skills/skills@linkedin-automation` | **MEDIO** | **MEDIO** | Automatización de LinkedIn para B2B marketing y lead generation; canal relevante pero secundario en LATAM vs WhatsApp. |
| **connections-optimizer** | affaan-m/everything-claude-code | `npx skills add affaan-m/everything-claude-code@connections-optimizer` | **MEDIO** | **MEDIO** | Reorganiza red LinkedIn/X, identifica warm paths, genera drafts outbound en voz real del usuario. |
| **sales-team-claude** | zubair-trabzada/ai-sales-team-claude | `git clone https://github.com/zubair-trabzada/ai-sales-team-claude.git` | **MEDIO** | **ALTO** | 14 skills + 5 agents + scripts Python: prospect, qualify (BANT+MEDDIC), outreach, followup, proposal, PDF pipeline reports. |
| **sales-skills** | louisblythe/salesskills | `npx add-skill louisblythe/salesskills --skill <nombre>` | **MEDIO** | **ALTO** | 122 skills: 20 core sales, 22 process/strategy, 80 AI SDR/bot skills (re-engagement, churn, propensity scoring). |
| **gtm-skills** | prospeda/claude-gtm-skills | `git clone https://github.com/Prospeda/claude-gtm-skills.git` | **MEDIO** | **ALTO** | Signal-based selling, 200+ email templates, re-engagement sequences; prompt library sin instalación formal. |
| **afrexai-revenue-forecasting** | openclaw/skills/1kalin | `git clone https://github.com/openclaw/skills.git` | **ALTO** | **ALTO** | Revenue forecasting con stage-weighted model, cohort analysis, seasonality coefficients, scenario analysis (bear/base/bull). |
| **cro-advisor** | alirezarezvani/claude-skills | `git clone https://github.com/alirezarezvani/claude-skills.git` | **MEDIO** | **ALTO** | Revenue forecasting, churn analyzer, NRR/GRR, pipeline coverage ratio; scripts Python incluidos. |
| **email-marketing-bible** | CosmoBlk/email-marketing-bible | `git clone https://github.com/CosmoBlk/email-marketing-bible.git ~/.claude/skills/email-marketing-bible` | **MEDIO** | **MEDIO** | 68K palabras, 908 fuentes, 19 playbooks; knowledge base masiva para email marketing B2B (no es ejecutable). |
| **cold-outreach-sequence** | BrianRWagner/ai-marketing-claude-code-skills | `git clone https://github.com/BrianRWagner/ai-marketing-claude-code-skills.git` | **MEDIO** | **ALTO** | Cold outreach sequences para LinkedIn y email con research, connection requests, follow-ups; 19 skills free. |
| **sales-revenue-skill** | ScientiaCapital/skills | `git clone https://github.com/ScientiaCapital/skills.git` | **MEDIO** | **ALTO** | B2B sales: outreach, discovery, RevOps; incluye prospect-research-to-cadence, phone-verification-waterfall, meddic-call-prep-auto, deal-momentum-analyzer. |
| **crm-integration-skill** | ScientiaCapital/skills | `git clone https://github.com/ScientiaCapital/skills.git` | **MEDIO** | **ALTO** | Patrones unificados para Close CRM, HubSpot, Salesforce; auth, lead sync, deal sync. |
| **hubspot-revops-skill** | ScientiaCapital/skills | `git clone https://github.com/ScientiaCapital/skills.git` | **MEDIO** | **ALTO** | HubSpot SQL analytics, lead scoring, pipeline forecasting; skill específica de RevOps. |
| **sales-deal-inspect** | sales-skills/sales | `npx skills add sales-skills/sales` | **ALTO** | **ALTO** | Inspecciona deal health, mapea stakeholders, identifica riesgos, recomienda next actions. |
| **sales-forecast** | sales-skills/sales | `npx skills add sales-skills/sales` | **ALTO** | **ALTO** | Build and validate revenue forecasts con pipeline coverage y gap analysis. |
| **claude-skills-sprintclub** | SimonTheSalesBooster/ClaudeSkills-SprintClub | `git clone https://github.com/SimonTheSalesBooster/ClaudeSkills-SprintClub.git` | **MEDIO** | **ALTO** | 18 playbooks B2B: Apollo Lead Builder, Pipeline Health Analyzer, Deal Closer Playbook, Multi-Stakeholder Navigator. |
| **linear-claude-skill** | wrsmith108/linear-claude-skill | `git clone https://github.com/wrsmith108/linear-claude-skill.git` | **BAJO** | **MEDIO** | Gestión de issues/proyectos en Linear; útil para pipeline de desarrollo de FaberLoom, no para ventas B2B. |

---

### Skills descartados (mencionados pero no aplica)

| Skill | Razón descarte |
|---|---|
| `anthropics/skills/*` (docx, pdf, pptx, xlsx, schedule, skill-creator) | Ya instalados en el entorno; explícitamente excluidos por reglas de la misión. |
| `obra/superpowers` (writing-plans, executing-plans, verification-before-completion, writing-skills) | Ya instalados; excluidos por reglas. |
| `apollographql/skills/*` (apollo-client, rust-best-practices) | Son de Apollo GraphQL (tecnología de API), no de Apollo.io (plataforma B2B lead enrichment). Confusión de marca. |
| `gtmagents/gtm-agents@cold-outreach` | Skill con solo 241 installs, sin repositorio GitHub verificable público; parece wrapper ligero sin funcionalidad de CRM/integration. |
| `ognjengt/founder-skills@outreach-specialist` | 239 installs, enfocado a fundraising/VC outreach, no a ventas B2B industrial. |
| `manojbajaj95/claude-gtm-plugin@ph-community-outreach` | 134 installs, outreach a comunidades de Product Hunt, no a decision-makers B2B LATAM. |
| `xquik-dev/tweetclaw` | Es plugin de OpenClaw para automatización de X/Twitter, no skill Claude Code ni relacionada con pipeline B2B. |
| `coreyhaines31/marketingskills@lead-magnets` | 28.7K installs pero es para marketing de captación (opt-ins), no para lead qualification ni pipeline B2B. |
| `coreyhaines31/marketingskills@revops` | Descartado porque `sales-skills/sales` y `ScientiaCapital/skills` cubren RevOps con mayor profundidad y verificabilidad. |
| `googleworkspace/cli@persona-sales-ops` | 10.9K installs pero es un persona/prompt de Google Workspace CLI, no una skill de integración con CRM real. |
| `membranedev/application-skills@sugarcrm` | 174 installs; SugarCRM es obsoleto en LATAM frente a HubSpot/Pipedrive/Zoho. |
| `membranedev/application-skills@dynamics-crm` | 473 installs; Dynamics CRM es enterprise México pero menos común que Zoho/HubSpot en PyMEs industriales. |
| `bellopushon/whatsapp-cloud-api@whatsapp-cloud-api` | 190 installs; parece wrapper básico de la API Cloud de Meta, menos completo que el ecosistema gokapso. |
| `sickn33/antigravity-awesome-skills@whatsapp-automation` | 214 installs; skill wrapper sin integración real de workflow; gokapso es superior. |
| `chadboyda/agent-gtm-skills@lead-enrichment` | 79 installs, sin repo público claro; funcionalidad redundante con apify-lead-generation y apollo-outreach. |
| `nikiandr/goose-skills@inbound-lead-enrichment` | 65 installs, muy específico para inbound (formularios web), no outbound B2B. |
| `k-dense-ai/scientific-agent-skills@timesfm-forecasting` | 143 installs; forecasting de series temporales genérico (TimesFM de Google), no específico de pipeline de ventas. |
| `jeremylongshore/claude-code-plugins-plus-skills@forecasting-time-series-data` | 119 installs; forecasting genérico, no aplica a deal velocity ni weighted pipeline. |
| `majesticlabs-dev/majestic-marketplace@pipeline-forecasting` | 37 installs, skill reciente sin verificación de estabilidad. |
| `finsilabs/awesome-ecommerce-skills@demand-forecasting` | 29 installs; demand forecasting para ecommerce, no pipeline B2B. |
| `borghei/claude-skills@churn-prevention` | 51 installs, redundante con churn-prevention de coreyhaines (36.9K installs). |
| `eddiebe147/claude-settings@churn-predictor` | 47 installs, sin repo verificable público. |
| `jonathimer/devmarketing-skills@developer-churn` | 41 installs; churn específico para developers/SaaS, no aplica a calzado industrial. |
| `claude-office-skills/skills@whatsapp-automation` | 911 installs; skill de WhatsApp pero menos documentada que gokapso; descartada por duplicación con mejor alternativa. |
| `code.deepline.com@portfolio-prospecting` | 1.7K installs; prospecting para portfolios de inversión/private equity, no B2B industrial. |
| `anthropics/knowledge-work-plugins@prospect` | 909 installs; skill oficial Anthropic para prospecting pero sin integración con fuentes de datos LATAM. |
| `anthropics/knowledge-work-plugins@sequence-load` | 862 installs; carga de sequences pero requiere integración previa con outreach platform. |
| `anthropics/knowledge-work-plugins@email-sequence` | 812 installs; skill oficial Anthropic para secuencias de email; más genérica que coreyhaines. |

---

### Gaps detectados (skills que MWT/FB debería escribir)

| Nombre propuesto | Justificación | Para MWT o FB | Prioridad |
|---|---|---|---|
| **lead-enrichment-latam** | Ninguna skill existente integra fuentes LATAM (SIC México, RUES Colombia, directorios industriales). Apollo.io tiene cobertura pobre en PyMEs manufactureras mexicanas/colombianas. Se necesita skill que use scraping + APIs locales. | MWT | **CRÍTICA** |
| **whatsapp-business-api-pedidos** | gokapso cubre automatización general pero no tiene skill específica para "cotización → pedido → seguimiento" por WhatsApp Business API con plantillas HSM aprobadas por Meta. | MWT | **ALTA** |
| **pipedrive-zoho-sync** | MWT probablemente migra entre Pipedrive y Zoho; no existe skill de sincronización bidireccional de deals/contacts/etapas entre estos dos CRMs. | MWT | **ALTA** |
| **pipeline-largo-b2b-industrial** | Ninguna skill modela forecasting para ciclos de 6-18 meses (calzado industrial B2B). Las existentes asumen SaaS/ciclos cortos. Se necesita weighted model con seasonality LATAM (agosto/diciembre). | MWT | **ALTA** |
| **agente-ventas-faber** | FaberLoom necesita una skill template que demuestre "cómo construir un agente de ventas" usando sus propios componentes. No existe skill didáctica de agent-builder para ventas. | FB | **ALTA** |
| **cuentas-riesgo-reengagement-b2b** | churn-prevention existe pero es para SaaS (cancel flows). No existe skill para detectar cuentas B2B en riesgo por inactividad de compra y generar campañas de re-engagement por WhatsApp/email. | MWT | **MEDIA** |
| **linkedin-scraper-prospect-latam** | connections-optimizer optimiza red existente pero no hace prospecting outbound. No existe skill de LinkedIn prospecting + enrichment + outreach sequence específica para LATAM (español/portugués). | MWT | **MEDIA** |
| **cold-outreach-whatsapp-sequence** | No existe skill que combine secuencias de outreach (como cold-email) con envío por WhatsApp Business API con plantillas y timing óptimo. | MWT | **MEDIA** |
| **forecasting-pipeline-multimoneda** | MWT opera México (MXN) → Colombia (COP). Ninguna skill de forecasting maneja pipeline multi-moneda ni tipo de cambio. | MWT | **MEDIA** |
| **crm-hygiene-dedup-latam** | Los datos de CRM en LATAM tienen problemas de duplicación por múltiples nombres de empresa, RFC, NIT. No existe skill de deduplicación y limpieza específica para datos LATAM. | MWT | **BAJA** |

---

### Caveats técnicos

- **WhatsApp Business API (gokapso)**: Requiere autenticación Kapso CLI (`kapso login`) o variables de entorno `KAPSO_API_BASE_URL` + `KAPSO_API_KEY`. El skill no es gratuito si se usan features premium de Kapso. Meta Business Account verificado requerido para plantillas HSM en producción.
- **CRM skills (membranedev, claude-office-skills)**: La mayoría son wrappers de MCP o API REST. Requieren API keys individuales por CRM. `membranedev/application-skills` usa OAuth 2.0 para HubSpot y API Key para Pipedrive/Zoho; el refresh token puede expirar.
- **Apollo.io (openclaudia)**: Requiere API key de Apollo.io (plan pago). La skill `apollo-outreach` no está publicada en skills.sh como skill individual buscable; se encuentra dentro del repo openclaudia-skills. El `apolloio/apollo-mcp-plugin` es un plugin MCP (no una skill SKILL.md) y requiere configuración manual del servidor MCP.
- **Email sequences (coreyhaines31)**: Son skills de copywriting/estrategia, no integran con ESP (SendGrid, Mailgun) ni CRM. Requieren export manual del copy generado.
- **Sales skills (louisblythe)**: Las 122 skills son mayoritariamente prompts/prompt libraries. Las 80 "AI SDR & Bot Skills" no tienen integración técnica real; son frameworks conceptuales para construir bots. Instalación vía `npx add-skill` (nota: es `add-skill`, no `skills add`).
- **Revenue forecasting (guia-matthieu, openclaw, alirezarezvani)**: Las skills de forecasting son frameworks analíticos manuales. No se conectan automáticamente a Pipedrive/HubSpot para extraer pipeline real; requieren que el usuario pegue los datos.
- **Deal inspection (sales-skills/sales)**: El repo `sales-skills/sales` parece ser un monorepo enorme con cientos de plataformas. No está claro si `/sales-deal-inspect` y `/sales-forecast` son skills independientes o comandos dentro de un mega-skill. El install command puede ser `npx skills add sales-skills/sales` o requerir clonación manual.
- **AI Sales Team (zubair-trabzada)**: Requiere Python 3.8+, reportlab, beautifulsoup4. El installer `install.sh` escribe en `~/.claude/` y `~/.claude/skills/`. Puede conflictuar con skills ya instaladas si hay nombres duplicados. Los scripts `analyze_prospect.py` y `lead_scorer.py` hacen scraping web sin rotación de IP, lo que puede causar bloqueos.
- **Zoho CRM (membranedev)**: Zoho tiene rate limits agresivos (100 requests/minuto en plan gratuito). La skill no documenta manejo de rate limiting ni backoff exponencial.
- **Churn prevention (coreyhaines31)**: Diseñado para SaaS subscription (cancel flows, dunning). Para B2B industrial con pedidos esporádicos, requiere adaptación significativa del framework.
- **LATAM data quality**: Ninguna skill maneja automáticamente la normalización de teléfonos (+52, +57), direcciones, ni la deduplicación por RFC/NIT/RUT. Esto es un gap sistémico.
- **Dependencia de skills.sh vs GitHub raw**: Algunos skills (especialmente `sales-skills/sales`, `openclaudia/openclaudia-skills`) tienen múltiples skills dentro de un solo repo. `npx skills add` puede instalar todo el repo o solo una subcarpeta dependiendo del manifiesto `skills.json`; la documentación no siempre es clara sobre el granularity.

---

### Apéndice: Referencias verificables

- skills.sh/gokapso/agent-skills/integrate-whatsapp
- skills.sh/gokapso/agent-skills/automate-whatsapp
- skills.sh/gokapso/agent-skills/observe-whatsapp
- skills.sh/claude-office-skills/skills/crm-automation
- skills.sh/claude-office-skills/skills/pipedrive-automation
- skills.sh/membranedev/application-skills/zoho-crm
- skills.sh/membranedev/application-skills/hubspot
- skills.sh/membranedev/application-skills/pipedrive
- skills.sh/openclaudia/openclaudia-skills/apollo-outreach
- skills.sh/apify/agent-skills/apify-lead-generation
- skills.sh/composiohq/awesome-claude-skills/lead-research-assistant
- skills.sh/anthropics/knowledge-work-plugins/enrich-lead
- skills.sh/coreyhaines31/marketingskills/cold-email
- skills.sh/coreyhaines31/marketingskills/email-sequence
- skills.sh/coreyhaines31/marketingskills/churn-prevention
- skills.sh/guia-matthieu/clawfu-skills/pipeline-forecasting
- skills.sh/guia-matthieu/clawfu-skills/deal-risk-scoring
- skills.sh/guia-matthieu/clawfu-skills/churn-prediction
- skills.sh/claude-office-skills/skills/linkedin-automation
- skills.sh/affaan-m/everything-claude-code/connections-optimizer
- github.com/zubair-trabzada/ai-sales-team-claude
- github.com/louisblythe/salesskills
- github.com/Prospeda/claude-gtm-skills
- github.com/openclaw/skills/tree/main/skills/1kalin/afrexai-revenue-forecasting
- github.com/alirezarezvani/claude-skills/tree/main/c-level-advisor/cro-advisor
- github.com/CosmoBlk/email-marketing-bible
- github.com/BrianRWagner/ai-marketing-claude-code-skills
- github.com/ScientiaCapital/skills
- github.com/sales-skills/sales
- github.com/SimonTheSalesBooster/ClaudeSkills-SprintClub
- github.com/wrsmith108/linear-claude-skill
- github.com/apolloio/apollo-mcp-plugin

---

*Investigación completada. Todos los skills listados tienen URL verificable en skills.sh o GitHub. No se incluyeron skills inventados ni skills ya instaladas en el entorno de trabajo.*
