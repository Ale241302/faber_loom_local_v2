## DIMENSIÓN 12 — Contracts, Compliance, Legal LATAM

### Resumen ejecutivo
Se evaluaron **+60 skills** en skills.sh, GitHub (topics: legal-tech, agent-skills, claude-code-skill), lawvable/awesome-legal-skills, skala-io/legal-skills, openaccountants/openaccountants, PSPDFKit-labs/nutrient-agent-skill, prompt-security/clawsec y listas awesome-agent-skills. **Se encontraron 7 skills directamente aplicables** para MWT/FaberLoom en esta dimensión, **3 skills parcialmente aplicables** y **6 skills descartadas**. El gap más crítico es la **ausencia total de skills de e-invoicing regulatorio LATAM** (CFDI México, NFe Brasil, DTE Costa Rica, factura electrónica Colombia) y **compliance de privacidad LATAM** (LFPDPPP MX, Ley 1581 CO, Ley 8968 CR). Solo existe cobertura para **LGPD Brasil**.

---

### Skills relevantes encontrados

| Skill | Repo | Instalación | Score MWT | Score FB | Por qué (1 línea) |
|---|---|---|---|---|---|
| **contract-review** | evolsb/claude-legal-skill | `git clone https://github.com/evolsb/claude-legal-skill ~/.claude/skills/contract-review` | **ALTO** | MEDIO | Review de contratos B2B con dataset CUAD (41 riesgos), redlines position-aware, benchmarks de mercado; mejor skill open-source de contract review. Limitación: foco US law por defecto. |
| **nutrient-document-processing** | PSPDFKit-labs/nutrient-agent-skill | `npx skills add PSPDFKit-labs/nutrient-agent-skill` | **ALTO** | **ALTO** | OCR, extracción de tablas/texto de PDFs, redacción de PII, firmas digitales (CMS/CAdES), conversión PDF↔DOCX. Esencial para procesar contratos escaneados y facturas PDF en 6 países LATAM. |
| **tender-analyzer** | somarkai/skills | `npx skills add https://github.com/somarkai/skills --skill tender-analyzer` | **ALTO** | BAJO | Parsing de pliegos de licitación (RFP/RFQ), extracción de requisitos de calificación, scoring rubrics, red-flag clauses. Útil para licitaciones públicas B2B de MWT. |
| **startup-due-diligence** | skala-io/legal-skills | `npx skills add skala-io/legal-skills` | MEDIO | MEDIO | Due diligence legal para seed/Series A: document review, cap table, red flags, report .docx. No es específico para proveedores B2B industriales pero aporta framework adaptable. |
| **legal-risk-assessment** | anthropics/knowledge-work-plugins | `npx skills add https://github.com/anthropics/knowledge-work-plugins --skill legal-risk-assessment` | MEDIO | MEDIO | Matriz severidad×probabilidad (1-5), criterios de escalación, risk register. Framework genérico pero útil para evaluar riesgos contractuales y de compliance. |
| **review-contract** | anthropics/knowledge-work-plugins | `npx skills add https://github.com/anthropics/knowledge-work-plugins --skill review-contract` | MEDIO | MEDIO | Skill oficial Anthropic para revisión de contratos: clause-by-clause analysis contra playbook de negociación, redline suggestions, issue log con owners y deadlines. |
| **vendor-due-diligence-patrick-munro** | lawvable/awesome-legal-skills | `npx skills add lawvable/awesome-legal-skills` | MEDIO | BAJO | Framework de evaluación de proveedores IT: riesgo financiero, operacional, compliance, seguridad y reputación. Checklists regulatorias (GDPR, DORA, NIS2, SOX). Adaptable a LATAM. |
| **LGPD Privacy Guardian** | metricasboss/otto | `git clone https://github.com/metricasboss/otto.git && cd otto && ./install.sh` | MEDIO | BAJO | Validación automática de código contra LGPD (Brasil) y GDPR. Detecta CPF/CNPJ en logs, tracking sin consentimiento, data minimization. Útil si MWT/FB desarrollan software para Brasil. |
| **privacy-skills-complete** | mukul975/Privacy-Data-Protection-Skills | `/plugin marketplace add mukul975/Privacy-Data-Protection-Skills && /plugin install privacy-skills-complete@privacy-data-protection-skills` | MEDIO | MEDIO | 282+ skills de privacidad incluyendo 3+ skills para LGPD (Brasil), GDPR, CCPA, HIPAA. Estructura agentskills.io con referencias y scripts. Cobertura LATAM limitada a Brasil. |
| **openaccountants/skills** | openaccountants/openaccountants | `npx add-skill openaccountant/skills` | BAJO | MEDIO | 44 skills financieros open-source (P&L, budgeting, tax prep). No son skills de e-invoicing regulatorio ni tax compliance LATAM específico. Referencia tax genérica. |
| **tender-bid-generator** | skills.volces.com | `npx skills add skills.volces.com/tender-bid-generator` | BAJO | BAJO | Generador de ofertas/licitaciones. No parsing de pliegos ni scoring de viabilidad. Genérico. |
| **kyc-analyst** | vyayasan/kyc-analyst | `git clone https://github.com/vyayasan/kyc-analyst.git` | BAJO | BAJO | KYC/AML compliance automation con 17 checkpoints HITL. Roadmap menciona "LatAm jurisdiction packs" pero aún no implementado. Early stage. |

---

### Skills descartados (mencionados pero no aplica)

| Skill / Repo | Razón descarte |
|---|---|
| `anthropics/skills/*` (docx, pdf, pptx, xlsx, schedule, skill-creator) | Ya instalados explícitamente en MWT/FB. No se pueden recomendar de nuevo. |
| `lawvable/awesome-legal-skills` — skills de derecho francés/UE | `assignation-refere-*`, `notification-licenciement-*`, `requete-cph-licenciement-*`, `politique-cookies-*`, `politique-lanceur-alerte-*` son específicas de jurisdicción francesa. No aplican a LATAM. |
| `claude-office-skills/skills/invoice-*` (generator, template, automation, organizer) | Skills de facturación genérica (templates visuales, organización). No implementan e-invoicing regulatorio ni validación fiscal LATAM. |
| `composiohq/awesome-claude-skills/invoice-organizer` | Organizador de facturas genérico. Sin conexión a CFDI, NFe, DTE ni validación tributaria. |
| `kazukinagata/shinkoku/reading-invoice` | Skill japonés (Shinkoku = tax return JP). No aplica a LATAM. |
| `skills-il/tax-and-finance/israeli-e-invoice` | Skill de e-invoice para Israel (ejemplo de e-invoicing existente). No aplica a LATAM pero sirve como referencia de formato skill. |
| `aradotso/trending-skills/legalize-es-spanish-legislation` | Legislación española (España), no LATAM fiscal/comercial. |
| `cat-xierluo/legal-skills/multi-search` | Búsqueda legal genérica multi-jurisdicción. No aporta valor diferencial sobre búsqueda web estándar para LATAM. |
| `wshobson/agents/employment-contract-templates` | Templates de contratos de empleo, no contratos B2B comerciales que opera MWT. |
| `langgenius/dify/orpc-contract-first` | Contratos de API (OpenAPI/RPC), no contratos legales comerciales. |
| `aj-geddes/useful-ai-prompts/api-contract-testing` | Testing de contratos API, no revisión legal de acuerdos comerciales. |
| `microsoft/azure-skills/azure-compliance` | Compliance de Azure cloud (SOX, GDPR, ISO 27001). No regulatorio LATAM específico. |
| `trailofbits/skills/spec-to-code-compliance` | Cumplimiento de especificaciones a código (seguridad). No legal/compliance fiscal. |
| `affaan-m/everything-claude-code/customs-trade-compliance` | Compliance aduanero/customs. No e-invoicing ni privacidad LATAM. |
| `supercent-io/skills-template/ai-tool-compliance` | Compliance de herramientas AI. No aplica a operación B2B LATAM. |
| `wshobson/agents/accessibility-compliance`, `pci-compliance` | Accesibilidad web y PCI-DSS. No regulatorio LATAM focal de esta dimensión. |
| `prompt-security/clawsec` | Suite de seguridad de skills (drift detection, advisories). No es skill legal ni de compliance fiscal. |
| `davila7/claude-code-templates/regulatory-affairs-head` | Template de persona de regulatory affairs genérico. No skill estructurada con workflows. |
| `absolutelyskilled/absolutelyskilled/regulatory-compliance` | Skill genérica de compliance regulatorio. Sin especificidad LATAM ni verificación de calidad. |

---

### Gaps detectados (skills que MWT/FB debería escribir)

| Nombre propuesto | Justificación | Para MWT o FB | Prioridad |
|---|---|---|---|
| **e-invoice-cfdi-mexico** | Validación de CFDI 4.0 (Complemento de carta porte, retenciones, addendas). México es mercado clave para MWT. No existe skill de e-invoicing LATAM en todo el ecosistema. | MWT | **CRÍTICA** |
| **e-invoice-nfe-brasil** | NFe (Nota Fiscal Eletrônica) modelo 55, NFC-e, manifestação do destinatário. Brasil es mercado top-3 de MWT. | MWT | **CRÍTICA** |
| **e-invoice-dte-costa-rica** | DTE (Documento Tributario Electrónico) para factura electrónica ante Ministerio de Hacienda CR. | MWT | **CRÍTICA** |
| **e-invoice-colombia** | Factura electrónica UBL 2.1 / DIAN, notas débito/crédito, Radian. | MWT | **CRÍTICA** |
| **compliance-lfpdppp-mexico** | Ley Federal de Protección de Datos Personales en Posesión de Particulares (México). Ninguna skill cubre LFPDPPP. | MWT + FB | **ALTA** |
| **compliance-ley1581-colombia** | Ley 1581 de 2012 (Protección de datos personales) + Decreto 1377. Necesario para operación en Colombia. | MWT + FB | **ALTA** |
| **compliance-ley8968-costa-rica** | Ley 8968 de Protección de Datos Personales (Costa Rica). Ninguna skill existente. | MWT + FB | **ALTA** |
| **contract-review-b2b-latam** | Review de contratos B2B bajo derecho mercantil latinoamericano (México, Colombia, Costa Rica, Centroamérica). Diferente del foco US/EU de skills existentes. Incluir: garantías, resolución de contratos, incumplimiento, ley aplicable, arbitraje local. | MWT | **ALTA** |
| **due-diligence-proveedor-b2b-latam** | Framework de evaluación de proveedores industriales (EPP, calzado de seguridad, materiales) en LATAM: verificación RUC/RUT, registro sanitario, licencias ambientales, certificaciones ISO, antecedentes judiciales. | MWT | **ALTA** |
| **licitaciones-publicas-latam** | Parsing de pliegos de licitación de plataformas específicas: CompraNet (México), SECOP (Colombia), Mercado Público (Costa Rica). Scoring de viabilidad técnica-económica y checklist de elegibilidad. | MWT | **MEDIA** |
| **tax-compliance-latam** | Skills de tax compliance para transacciones B2B: retenciones en la fuente (IVA, renta), novedades fiscales por país, validación de NIT/RUC/RUT, reportes DIOT (México). | MWT | **MEDIA** |
| **redlining-contracts-docx** | Skill que orqueste `anthropics/skills/docx` (ya instalado) para generar redlines con tracked changes en Word a partir del output de `evolsb/claude-legal-skill`. No existe skill de integración. | MWT | **MEDIA** |
| **lgpd-full-compliance** | Expandir las 3 skills actuales de LGPD (mukul975/otto) a un set completo: DPIA, registro de operaciones, derechos del titular, transferencia internacional, naming authority. Brasil es mercado grande de MWT. | MWT + FB | **MEDIA** |
| **e-invoice-panama** | Factura electrónica Panama (RUC + DGI). Menor volumen pero mercado en crecimiento para MWT. | MWT | **BAJA** |
| **e-invoice-guatemala-nicaragua** | Factura electrónica SAT Guatemala/DGI Nicaragua. Mercados emergentes. | MWT | **BAJA** |

---

### Caveats técnicos

- **`evolsb/claude-legal-skill` (contract-review)**: Foco en US law por defecto. Para uso en LATAM requiere adaptación del SKILL.md o instrucciones explícitas de jurisdicción en cada prompt. No genera tracked-changes `.docx` nativamente; requiere `legal-redline-tools` (pip install) como paso posterior.
- **`PSPDFKit-labs/nutrient-agent-skill`**: Requiere API key de Nutrient (freemium: 1,000 documentos/mes). Para procesamiento masivo de contratos/facturas en 6 países se necesitará plan pago. Depende de `uv` (Python 3.10+) y conexión a API externa. La redacción de PII es irreversible (destruye datos originales en el PDF).
- **`anthropics/knowledge-work-plugins/review-contract`**: Skill oficial de Anthropic. No está en la lista de skills ya instaladas (la lista menciona `anthropics/skills/*`, que es el repo de skills básicas de Anthropic, no `anthropics/knowledge-work-plugins`). Instalación segura.
- **`skala-io/legal-skills/startup-due-diligence`**: Diseñado para startups VC (seed/Series A). Los document templates son para cap tables, SAFEs, board resolutions — no para contratos de distribución industrial B2B. Requiere adaptación manual de templates.
- **`somarkai/skills/tender-analyzer`**: Requiere parsing previo con SoMark (servicio externo de recuperación de estructura de documentos). Sin SoMark, el skill pierde precisión en tablas y anexos escaneados. Solo 17 installs/semana, skill joven.
- **`metricasboss/otto`**: Es una herramienta de hooks de pre-commit para código, no para documentos legales o políticas de privacidad redactadas en prosa. Útil solo si MWT/FB desarrollan software con datos personales brasileños.
- **`mukul975/Privacy-Data-Protection-Skills`**: Solo 3+ skills para LGPD vs 50+ para GDPR. Calidad no verificada como Q1 (battle-tested) para LATAM. Requiere marketplace plugin de Claude Code (`/plugin marketplace add ...`).
- **`openaccountants/openaccountants`**: Skills calificados mayormente como Q3 (AI-drafted), no Q1 (practitioner sign-off). Sin verificación de cobertura LATAM específica. Útil como punto de partida para tax skills pero no como skill de producción sin revisión contable local.
- **`vyayasan/kyc-analyst`**: Early stage (roadmap menciona LatAm pero no implementado). Requiere Claude Cowork o Claude Code + Python dependencies (fpdf2, openpyxl). No es una skill propiamente tal sino un plugin con comandos slash. Solo 5 stagegates de 17 son automáticos; el resto requiere HITL constante.
- **Conflictos potenciales**: `nutrient-agent-skill` y `anthropics/skills/pdf` (ya instalado) pueden solaparse en extracción de texto de PDFs. Recomendación: usar `nutrient` para operaciones avanzadas (OCR, redacción, firmas) y `anthropics/pdf` para lectura simple.

---

### Fuentes consultadas
- skills.sh (búsquedas: legal, contract, compliance, invoice, tax, regulatory, privacy, tender, due-diligence)
- GitHub: `lawvable/awesome-legal-skills`, `skala-io/legal-skills`, `evolsb/claude-legal-skill`, `PSPDFKit-labs/nutrient-agent-skill`, `metricasboss/otto`, `mukul975/Privacy-Data-Protection-Skills`, `vyayasan/kyc-analyst`, `openaccountants/openaccountants`, `somarkai/skills`, `Sushegaad/Claude-Skills-Governance-Risk-and-Compliance`, `alirezarezvani/claude-skills`
- GitHub topics: legal-tech, agent-skills, claude-code-skill, procurement, nutrient
- Búsquedas web: e-invoicing LATAM skills, CFDI skill.md, NFe skill.md, factura electrónica Colombia skill.md

---

### Rúbrica de evaluación usada
| Score | Criterio |
|---|---|
| **ALTO** | Skill verificada, instalable, cubre necesidad core de MWT/FB, URL confirmada |
| **MEDIO** | Skill verificada pero genérica (requiere adaptación LATAM) o cobertura parcial |
| **BAJO** | Skill verificada pero muy nicho, early-stage, o valor limitado para los proyectos |
| **NO APLICA** | Ya instalada, fuera de scope, o inventada |
