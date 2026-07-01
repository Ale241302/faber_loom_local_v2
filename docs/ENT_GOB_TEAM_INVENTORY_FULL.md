# ENT_GOB_TEAM_INVENTORY_FULL — Inventario de Roles Plataforma Completa 18–24m

id: ENT_GOB_TEAM_INVENTORY_FULL
version: 2.0
status: DRAFT
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: ENT
stamp: DRAFT — 2026-05-04
aplica_a: [MWT, FaberLoom, ScanFoot]
horizonte: 18–24 meses (plataforma completa, full-time hires)
modalidad: FT only (decisión CEO 2026-05-03)
formato_origen: Markdown indexado en KB (decisión CEO 2026-05-03)
fuente_v2: Kimi Swarm #5 (12 sub-agentes paralelos · 2026-05-04 · raw en `docs/anexos/kimi_team_swarm/`)

---

## Propósito

Inventario canónico de roles full-time necesarios para construir la plataforma completa MWT + FaberLoom + ScanFoot a horizonte 18–24 meses. No es plan de hire (eso vive en `ENT_GOB_HIRING_ROADMAP_*` cuando se materialice). Es **el catálogo de qué personas hacen falta, en qué disciplina, con qué scope, y por qué**.

**v2.0:** integra hallazgos SOTA 2026 vía Kimi Swarm #5. Cierra gaps identificados en v1.0 (ver §Changelog v2.0). Roles nuevos / sub-dimensionados / re-categorizados se marcan con tag `[v2-NEW]`, `[v2-EXPANDED]`, `[v2-SPLIT]` o `[v2-RECAT]`. Las competencias transversales que el swarm devolvió viven en archivo separado: `ENT_GOB_ENGINEERING_COMPETENCIES`.

**Modalidad:** todos los roles asumen contratación full-time. Decisión CEO 2026-05-03.

**Alcance:** plataforma completa, no MVP.

## Contexto técnico (resumen — refs a SPECs canónicas)

| Producto | Estado | Stack core | Refs canónicas |
|---|---|---|---|
| **MWT / Rana Walk** | Producción Amazon FBA + B2B pilot Marluvas/Tecmater | Python, FastAPI v1.1, Postgres, AWS, Amazon SP-API, Helium 10, WhatsApp Biz API, integración SAP B2B | `ENT_PROD_*`, `IDX_MARKETPLACE`, `IDX_OPS`, `IDX_DISTRIBUCION`, `PLB_OPS_AMAZON`, `SPEC_HELIUM10_AUTOMATION` |
| **FaberLoom** | Foundation Beta planeado (13 sprints firmado v1.3.1, Sprint 1A congelado) | Next.js 15 + TanStack + Zustand · FastAPI + Pydantic v2 AI · Postgres 16 + RLS + pgvector · Redis · LiteLLM (Anthropic only) · MinIO · Caddy · Hostinger KVM 8 (Docker Compose 12 contenedores) · Langfuse + Loki + Prometheus + Grafana | `docs/faberloom/*`, `SPEC_FB_AUTH_TENANT_RBAC`, `SPEC_FB_SYSTEM_TOPOLOGY`, `PLAN_FABERLOOM_FOUNDATION_BETA_v1.3.1`, `IDX_FB_FOUNDATION_BETA` |
| **ScanFoot** | DRAFT planeación · candidato hardware HW-BANGNI-C1 · gate AC-02 pendiente | Hardware: array 1681 sensores, BLE 5.0, MCU nRF52840-equiv · Driver Python · Motor biomecánico Python · Motor recomendación · UI Electron + React · Postgres RLS · MinIO | `ENT_PROD_SCANNER`, `ENT_PLAT_SCANNER_SECURITY`, `ENT_PLAT_SCANNER_DISTRIB`, `PLB_SCANNER_DISTRIB` |
| **Plataforma compartida** | Capa cross-cutting | Action Engine (D1–D10) · LLM Routing · Autonomy Control · Knowledge River · Audit Module · POL_DATA_CLASSIFICATION N0–N4 · ARCH_AGENT_PRINCIPLES v1.5 FROZEN · pgvector | `SPEC_ACTION_ENGINE`, `SPEC_LLM_ROUTING_ARCHITECTURE`, `SPEC_AUTONOMY_CONTROL_ENGINE`, `SPEC_AUDIT_MODULE`, `SPEC_AI_GOV_GOVERNANCE_AND_ROUTING`, `POL_DATA_CLASSIFICATION`, `ARCH_AGENT_PRINCIPLES` |

## Marco de prioridades

| Prioridad | Definición | Cuándo se hire |
|---|---|---|
| **P0** | Bloquea Foundation Beta o sostiene MWT existente | Mes 0–6 |
| **P1** | Necesario para Beta → GA y para activar Scan Foot | Mes 6–12 |
| **P2** | Escalado, multi-tenant maduro, GTM B2B serio | Mes 12–18 |
| **P3** | Operación steady-state, R&D, expansion regional | Mes 18–24 |

## Marco de fases

| Fase | Meses | Hito de cierre | Headcount acumulado v2.0 |
|---|---|---|---|
| **F1 — Foundation** | 0–6 | FB Foundation Beta firmada → liberada · MWT operativo · ScanFoot AC-02 gate pasado | ~28 FTE |
| **F2 — Beta → GA** | 6–12 | FB GA con ≥10 tenants pagantes · ScanFoot piloto · MWT con forecasting+experiment runner activos | ~70 FTE |
| **F3 — Scale** | 12–18 | FB ≥30 tenants · MWT B2B Marluvas+Tecmater integrado · ScanFoot escalado | ~115 FTE |
| **F4 — Multi-producto / Steady-state** | 18–24 | Operación multi-país · compliance LATAM completa · R&D activo | ~135 FTE |

> **Diferencia v1.0 → v2.0:** +26 FTE acumulados (~109 → ~135). Razones: hardware sub-dimensionado (+5–7), AI specialty split (+2), architecture role nuevo (+1), platform engineering nuevo (+3), observability separado (+1), security split (+1), privacy engineer técnico (+1), mobile expandido (+2).

---

## 1. Leadership & Product

| Rol | Seniority | Scope | Responsabilidad core | Reporta a | Prioridad | Fase |
|---|---|---|---|---|---|---|
| CEO (Álvaro) | C-level | Todo | Visión, estrategia, capital, decisiones FROZEN | Board | — | Existente |
| **CTO** | C-level | Compartido | Arquitectura técnica MWT+FB+Scan, AI governance, tech hiring final-pass | CEO | **P0** | F1 |
| **VP Product** | VP | Compartido | Roadmap producto, priorización entre productos, métricas de adopción | CEO | **P0** | F1 |
| **Head of Product · FaberLoom** | Senior | FB | PMF wedge cotización safety footwear, roadmap 13 sprints → GA | VP Product | **P0** | F1 |
| **Head of Product · MWT (Rana Walk + B2B)** | Senior | MWT | Roadmap Amazon FBA + B2B Marluvas/Tecmater, expansión canales | VP Product | **P1** | F1–F2 |
| **Head of Product · ScanFoot** | Senior | Scan | Roadmap hardware+app, integración con catálogo distribuidor | VP Product | **P1** | F2 |
| **COO / Chief of Staff** | C-level | Todo | Ops corporativas, finance, hiring ops, vendor mgmt | CEO | **P1** | F2 |
| **CFO** | C-level | Todo | Modelo financiero multi-producto, fundraising, treasury | CEO | **P2** | F3 |
| **General Counsel** | Senior | Todo | Contratos, IP, equity, compliance corporativa, DPA chain | CEO | **P2** | F2–F3 |
| **Platform PM** `[v2-NEW]` | Senior | Compartido | Producto interno IDP/golden paths · platform-as-a-product · adoption metrics | VP Product / VP Eng | **P1** | F2 |

**Total disciplina: 10 roles** (CEO existente + 9 hire). `[v2-NEW]` Platform PM agregado por A2 — sin él, IDP no se trata como producto y muere.

---

## 2. Architecture (cross-cutting) `[v2-NEW]`

Disciplina nueva en v2.0. Antes implícita dentro de Eng Leadership; A1 SOTA 2026 [HIGH] dice que para 60 eng + 3 productos requiere arquitecto separado del CTO.

| Rol | Seniority | Scope | Responsabilidad core | Reporta a | Prioridad | Fase |
|---|---|---|---|---|---|---|
| **Software Architect** `[v2-NEW]` | Staff/Principal | Compartido | DDD táctico + Bounded Contexts, modular monolith→microservices framework, ADR governance, contract-first (OpenAPI 3.1 + Spectral), SoT events vs APIs, strangler fig patterns | CTO | **P0** | F1 |
| **Solutions Architect** `[v2-RECAT]` | Senior | FB Enterprise + MWT B2B | Pre-sales técnico complejo (SAP/ERP custom), POCs Enterprise, integration design tenant-by-tenant | CTO o VP Eng | **P2** | F3 |

**Total disciplina: 2 roles**

> **Por qué disciplina propia:** v1.0 puso "Architect" como sub-rol de Eng Leadership genérico. SOTA 2026 (Kimi A1 [HIGH]) confirma: cross-cutting concerns (DDD/contract-first/EDA decisions) requieren un Staff Architect separado del CTO antes de los 60 eng. Más Solutions Architect dedicado para Enterprise (no se subsume en SE/CSM).

---

## 3. Engineering Leadership

| Rol | Seniority | Scope | Responsabilidad core | Reporta a | Prioridad | Fase |
|---|---|---|---|---|---|---|
| **VP Engineering** | VP | Compartido | Eng across, tech debt, ingeniería como función, hiring tech | CTO | **P0** | F1 |
| **Head of Backend** | Staff/Principal | Compartido | FastAPI, Python, Postgres, microservicios, escalado | VP Eng | **P0** | F1 |
| **Head of Frontend / Design Eng** | Staff/Principal | FB + Scan UI | Next.js 15 stack, design system FB, Mesa de Control | VP Eng | **P0** | F1 |
| **Head of AI & Agents** | Staff/Principal | Compartido | LLM routing, agent framework, AI governance ejecutiva, MLOps | VP Eng / CTO | **P0** | F1 |
| **Head of Platform Engineering** `[v2-NEW]` | Staff/Principal | Compartido | IDP, golden paths, DevEx, DORA+Core 4, Team Topologies | VP Eng | **P0** | F1 |
| **Head of DevOps / SRE** `[v2-RECAT]` | Staff/Principal | Compartido | Operations + reliability + SLOs (Platform separado) | VP Eng | **P1** | F1–F2 |
| **Head of Security** | Staff/Principal | Compartido | AppSec/CloudSec/IR/Crypto/Privacy estrategia, vulns mgmt | CTO | **P1** | F2 |
| **Head of Mobile** | Staff/Principal | Scan + futuros apps | iOS/Android/KMP, hardware integration mobile (BLE) | VP Eng | **P2** | F3 |
| **Head of Hardware / Firmware** | Staff/Principal | Scan | Embedded, BLE 5.0, MCU, firmware OEM coordination | VP Eng / CTO | **P1** | F2 |
| **Head of Data Platform** | Staff/Principal | Compartido | Postgres+pgvector, ETL/ELT, data lake, governance datos | VP Eng | **P2** | F3 |

**Total disciplina: 10 roles** (era 9 en v1.0). `[v2-NEW]` Head of Platform Eng. `[v2-RECAT]` Head of DevOps/SRE separado de Platform.

---

## 4. Backend Engineering (Python / FastAPI / Postgres)

| Rol | Seniority | Scope primario | Responsabilidad core | Prioridad | Fase |
|---|---|---|---|---|---|
| Staff Backend Engineer · FaberLoom Core | Staff | FB | Engine ejecutor genérico, SkillSpec dinámico Pydantic, RLS multitenant, async disciplinado | **P0** | F1 |
| Senior Backend Engineer · FaberLoom Action Engine | Senior | FB | Action Engine D1–D10, Audit Module D10, evidence bundle SHA-256 | **P0** | F1 |
| Senior Backend Engineer · FaberLoom Knowledge & Memory | Senior | FB | Knowledge River 5 capas L0–L4, pgvector embeddings, k-anon ≥5 organizational | **P0** | F1 |
| Senior Backend Engineer · FaberLoom Auth & RBAC | Senior | FB | FastAPI native auth, Postgres RLS hardened (SET LOCAL por tx + NULLIF current_setting), 2FA | **P0** | F1 |
| Senior Backend Engineer · FaberLoom Integrations | Senior | FB | LiteLLM gateway, Redis Streams, MinIO, WhatsApp Cloud API, Gmail OAuth | **P1** | F2 |
| Senior Backend Engineer · MWT Platform | Senior | MWT | mwt.one services, Amazon SP-API, Helium 10 automation, B2B endpoints | **P1** | F1–F2 |
| Senior Backend Engineer · MWT B2B + SAP | Senior | MWT | Integración SAP Marluvas/Tecmater, portal B2B, presupuestación, HITL workflow | **P1** | F2 |
| Senior Backend Engineer · ScanFoot Driver & Motor | Senior | Scan | Driver Python (BLE/USB), motor biomecánico (PCA/COP/Z1–Z10), motor recomendación | **P1** | F2 |
| Mid Backend Engineer × 3 | Mid | FB / MWT / Scan | Features, refactor, tests, hybrid SQL fluency (EXPLAIN, ORM vs raw) | **P2** | F2–F3 |
| Backend Engineer · Compliance Module | Senior | Compartido | Reportes LGPD/Ley 1581/Ley 8968 LATAM, anonimización determinística, DPA chain | **P2** | F3 |
| Backend Engineer · Billing & Pricing | Senior | FB | 4 tiers + add-ons modulares, Stripe integration, usage metering | **P2** | F3 |
| Data/Worker Engineer `[v2-RECAT]` | Senior | Compartido | ARQ Redis (no Celery), Temporal cuando audit-heavy + retries durables | **P1** | F2 |

**Total disciplina: ~14 backend engineers** (+1 vs v1.0). `[v2-RECAT]` Data/Worker Engineer ahora capability dedicada — Kimi A5 [HIGH] dice ARQ vence Celery 2026, Temporal para flujos durables.

---

## 5. Frontend Engineering (Next.js 15 + design system)

| Rol | Seniority | Scope primario | Responsabilidad core | Prioridad | Fase |
|---|---|---|---|---|---|
| Staff Frontend Engineer · FaberLoom Mesa de Control | Staff | FB | Mesa de Control v5 canon, HITL UI, real-time WebSocket/SSE, agentic UI streaming | **P0** | F1 |
| Senior Frontend Engineer · FaberLoom Skill/Agent Factory | Senior | FB | Wizard 5 pasos skills, wizard 4 pasos agentes, sandbox UI | **P0** | F1 |
| Senior Frontend Engineer · FaberLoom Voice & Iterar | Senior | FB | Iterar object-first, Voice Profile config, Cotización document-first | **P1** | F2 |
| **Design Engineer** `[v2-NEW]` | Senior | Compartido FB+Scan | Puente design ↔ code, design system canon, Figma-to-code, lente `SKILL_FRONTEND_TEN_PRINCIPLES_V2` aplicada en CI | **P0** | F1 |
| Senior Frontend Engineer · MWT Web | Senior | MWT | Storefront ranawalk.com, A+ content tooling, B2B portal frontend | **P1** | F2 |
| Mid Frontend Engineer × 2 | Mid | FB / MWT | Features iterativos, perf budgets (LCP ≤2.5s, INP ≤200ms, CLS ≤0.1) | **P2** | F2–F3 |
| Frontend Engineer · ScanFoot Electron UI | Senior | Scan | Electron + React, mapa calor bilateral, fit matching UI | **P1** | F2 |
| **Accessibility Specialist** `[v2-NEW]` | Senior | Compartido | WCAG 2.2 AA CI gate, Ley 7600 CR Art. 50 + Directriz 036 compliance | **P2** | F3 |

**Total disciplina: ~9 FE engineers** (+2 vs v1.0). `[v2-NEW]` Design Engineer (Kimi A4 [HIGH]: rol separado en equipos >6 FE) + Accessibility Specialist (Kimi A4 [HIGH]: WCAG obligatorio sector público CR; B2B en riesgo).

---

## 6. Mobile Engineering `[v2-EXPANDED]`

v1.0: 3 FTE genéricos (iOS/Android/cross-platform). v2.0: 5 FTE con KMP-first según Kimi A11 [HIGH] (KMP + native UI vence Flutter/RN para B2B con BLE).

| Rol | Seniority | Scope | Responsabilidad core | Prioridad | Fase |
|---|---|---|---|---|---|
| Senior iOS Engineer (Native) | Senior | Scan | App iOS Swift 6 + SwiftUI, CoreBluetooth async/await/Combine, BLE pairing real-device test | **P2** | F3 |
| Senior Android Engineer (Native) | Senior | Scan | App Android Kotlin 2.x + Compose, Kotlin Flow + Coroutines, BLE | **P2** | F3 |
| **KMP / Shared Logic Engineer** `[v2-NEW]` | Senior | Scan + futuros | Shared business logic via Kotlin Multiplatform, expect/actual, SKIE Flows→Swift | **P2** | F3 |
| **Mobile Performance Specialist** `[v2-NEW]` | Senior+ | Scan + futuros | BLE throughput, battery, startup, p99 latency BLE <50ms | **P3** | F3–F4 |
| Mid Mobile Engineer · Apps secundarias | Mid | Compartido | Mobile DevOps (Bitrise + Fastlane), privacy manifests, store releases | **P3** | F4 |

**Total disciplina: 5 mobile engineers** (+2 vs v1.0).

---

## 7. AI & Agents Engineering `[v2-EXPANDED]`

v1.0: 10 AI engineers en bloque. v2.0: split en 4 sub-roles SOTA según Kimi A3.

| Rol | Seniority | Scope | Responsabilidad core | Prioridad | Fase |
|---|---|---|---|---|---|
| **AI Agent Architect** `[v2-NEW]` | Staff+ | Compartido | Cognición · memoria · planning · HITL design · checkpointing · LangGraph orchestration design · interrupt_before patterns | **P0** | F1 |
| **AI Eval / Red Team Engineer** `[v2-NEW]` | Senior | Compartido | Adversarial testing · golden corpus · DeepEval/Langfuse pytest-native · safety agentes autónomos · jailbreak defense | **P0** | F1 |
| **LLM Ops Engineer** `[v2-NEW]` | Senior | Compartido | Token Ledger · model routing L1+L2+L3 · cost optimization · drift monitoring · prompt versioning | **P0** | F1 |
| Senior AI Engineer · Skills Platform | Senior | FB | Skill Factory, sandbox, 14 límites duros, promotion gate | **P0** | F1 |
| Senior AI Engineer · Knowledge Retrieval | Senior | Compartido | pgvector + multilingual-e5-base, RAG pipeline, retrieval quality eval, HNSW tuning | **P0** | F1 |
| Senior AI Engineer · Forecasting & Decision Models | Senior | MWT | Demand planning Rana Walk, forecasting B2B Marluvas/Tecmater | **P1** | F2 |
| Senior AI Engineer · Biomechanics ML | Senior | Scan | Modelo recomendación SKU desde perfil biomecánico, fit matching ML | **P1** | F2 |
| Senior AI Engineer · Autonomous Agent Builder | Senior | FB + MWT | Agent Factory wizard backend, tool/skill installation gate, MCP lifecycle | **P2** | F3 |
| Mid AI Engineer × 2 (Prompt Eng capability) | Mid | Compartido | Prompt engineering, fixtures, fine-tuning data prep, MCP server wiring | **P2** | F3 |

**Total disciplina: ~11 AI engineers** (+1 vs v1.0). Reasignación interna importante: 3 nuevos sub-roles separados (AI Agent Architect, AI Eval/Red Team, LLM Ops).

---

## 8. Data, ML & Forecasting Engineering `[v2-EXPANDED]`

v1.0: 6 FTE con Data Engineer/Data Scientist mezclados. v2.0: split Data Engineer (infra) vs Analytics Engineer (modelado) según Kimi A6 [HIGH].

| Rol | Seniority | Scope | Responsabilidad core | Prioridad | Fase |
|---|---|---|---|---|---|
| Staff Data Engineer · Plataforma | Staff | Compartido | Postgres+CDC, ETL/ELT, data lake (Iceberg si >1TB/día), governance datos cross-tenant | **P1** | F2 |
| **Analytics Engineer** `[v2-NEW]` | Mid–Senior | Compartido | dbt Core/Cloud · transformaciones analytics · marts · semantic layer · incremental models | **P1** | F2 |
| Senior Data Scientist · Forecasting MWT | Senior | MWT | Modelos demand planning (Prophet/ARIMA/ML), pricing dynamic, experiment runner | **P1** | F2 |
| Senior Data Scientist · Biomechanics Signal | Senior | Scan | Procesamiento señal sensores (1681 capacitivos @ 50Hz), filtros, anti-noise, calibración | **P1** | F2 |
| Senior Streaming Engineer `[v2-NEW]` | Senior | Compartido | Kafka + Debezium CDC tenant-aware, audit streaming, p99 lag <1s | **P2** | F3 |
| Mid Data Engineer × 2 | Mid | Compartido | Pipelines, ingestion, data quality monitoring | **P3** | F3–F4 |

**Total disciplina: ~7 data/ML engineers** (+1 vs v1.0).

---

## 9. Hardware & Firmware Engineering (ScanFoot) `[v2-EXPANDED]`

v1.0: 3 FTE. **v2.0: 8 FTE.** Razón: Kimi A10 [HIGH] dice "team <5 FTE = imposible cubrir BLE+OTA+seguridad+PCB+test+manufactura". Producto biométrico hardware comercial requiere disciplina madura.

| Rol | Seniority | Scope | Responsabilidad core | Prioridad | Fase |
|---|---|---|---|---|---|
| **Embedded Architect** `[v2-NEW]` | Staff | Scan | nRF Connect SDK + Zephyr · MCUboot + ECDSA OTA signed · CRA 24h reporting · secure boot architecture | **P0** | F1 |
| Senior Firmware Engineer × 2 `[v2-EXPANDED]` | Senior | Scan | Firmware Rust + Embassy (preferido) o C/Zephyr · BLE 5.x stack · Devicetree/Kconfig | **P1** | F2 |
| **RF / BLE Specialist** `[v2-NEW]` | Senior | Scan | BLE 5.x mesh, antena, radio compliance, throughput optimization | **P1** | F2 |
| **Hardware Security Engineer** `[v2-NEW]` | Senior | Scan | CryptoCell-310/KMU 100% units, secure storage biométrico, HSM offline keys, attestation | **P1** | F2 |
| **HW / PCB Engineer** `[v2-NEW]` | Senior | Scan | PCB design, layout, signal integrity, BoM negotiation | **P1** | F2 |
| Manufacturing / Test Engineer | Mid | Scan | Test automation 1681 sensores, regression hardware, AC-01..AC-N gates, calibración por unidad | **P2** | F3 |

**Total disciplina: 8 hardware/firmware** (+5 vs v1.0). Roles separados según SOTA: Embedded Architect Staff es no-negociable.

---

## 10. DevOps / SRE / Platform / Observability `[v2-SPLIT]`

v1.0: 5 DevOps/SRE en bloque. v2.0: split en 3 subdisciplinas (Platform Eng + DevOps/SRE + Observability). Ratio 1 Platform Engineer : 8 stream-aligned eng según Kimi A2 [HIGH].

| Rol | Seniority | Scope | Responsabilidad core | Prioridad | Fase |
|---|---|---|---|---|---|
| **Platform Engineer × 2** `[v2-NEW]` | Senior+ | Compartido | IDP SaaS (Port o Roadie · NO Backstage self-hosted <100 eng) · golden paths · CI/CD templates · TVP (Thinnest Viable Platform) | **P0** | F1 |
| Staff DevOps Engineer · FB Infra | Staff | FB | Hostinger KVM 8 → migración K8s (E2 >100 eng), Docker Compose 12 contenedores, Caddy, backup/restore camino C | **P0** | F1 |
| **Observability / Platform Engineer** `[v2-NEW]` | Mid–Senior | Compartido | OTel Collector pipelines (sampling, tail-based, multi-backend) · SLO-as-code · Grafana LGTM stack · cardinality budgets ≤10 dim | **P1** | F2 |
| Senior DevOps Engineer · CI/CD & Release | Senior | Compartido | GitHub Actions, releases firmados Sigstore, canary, rollback playbooks | **P1** | F2 |
| Senior SRE · Reliability & Chaos | Senior | Compartido | Chaos testing (camino C demo), DR, RTO/RPO, runbooks, oncall, error budget policy | **P2** | F3 |
| DevOps Engineer · Edge / CDN | Mid | Compartido | CDN, edge cache, perf, tenant routing | **P3** | F4 |

**Total disciplina: 7 platform/devops/SRE** (+2 vs v1.0). Decisión clave Kimi A2: **IDP SaaS, no self-hosted Backstage** (3–12 FTE + $1M+ year), hasta >100 eng.

---

## 11. Security Engineering `[v2-SPLIT]`

v1.0: 5 security generales. v2.0: split AppSec Architect / Security Engineer / Product Security según Kimi A8 [HIGH] (ratio AppSec Architect : Engineer 1:4).

| Rol | Seniority | Scope | Responsabilidad core | Prioridad | Fase |
|---|---|---|---|---|---|
| **AppSec Architect** `[v2-NEW separado]` | Staff/Principal | FB + MWT + Scan | SDLC + threat modeling (STRIDE/LINDDUN) + supply chain hardening (SLSA L3-L4 · SBOM · sigstore/cosign + Kyverno admission control) · zero trust architecture | **P1** | F2 |
| Senior Security Engineer × 2 `[v2-EXPANDED]` | Senior+/Staff | Compartido | Secure SDLC ejecución · OWASP · secrets mgmt · dependency scanning · pentesting interno · IR triage | **P1** | F2 |
| **Product Security Engineer** `[v2-NEW]` | Staff | FB + MWT | Capability dentro de AppSec · feature security review · privacy enforcement · agentic AI safety guardrails | **P2** | F3 |
| Senior Cloud Security Engineer | Senior | Compartido | Cloud posture (AWS + Hostinger), IAM, network segmentation, KMS, key rotation, PQC híbrido roadmap | **P2** | F3 |
| Senior Security Engineer · Identity & Access | Senior | Compartido | OAuth, SSO B2B (SAML/OIDC), 2FA, session mgmt, JWT hardening, ABAC/least privilege | **P2** | F3 |
| Incident Response & Detection Engineer | Senior | Compartido | SIEM básico, playbooks IR, forensics, vulnerability mgmt, MTTR <4h | **P3** | F3–F4 |

**Total disciplina: 7 security engineers** (+2 vs v1.0).

---

## 12. Compliance, Privacy & Legal `[v2-EXPANDED]`

v1.0: 5 compliance (DPO + Compliance Officer + Regulatory + Legal + Compliance Engineer). v2.0: agrega **Privacy Engineer técnico** separado del DPO según Kimi A9 [HIGH] ("PE codifica; DPO gobierna · ratio DPO:PE 1:1.5").

| Rol | Seniority | Scope | Responsabilidad core | Prioridad | Fase |
|---|---|---|---|---|---|
| **Privacy Engineer** `[v2-NEW]` | IC3-4 | Compartido | Codifica PbD · RLS · KMS · Differential Privacy (ε≤8 · OpenDP) · DPA-as-code (whitelist versionado, PR legal+eng) · privacy budget tracking | **P1** | F2 |
| **DPO / Privacy Officer LATAM** `[v2-RECAT]` | Senior | Compartido | LGPD (BR), Ley 1581 (CO), Ley 8968 (CR), Ley 25.326 (AR), DPA chain governance, ROPA, residency contratos vigentes Q2/Q4 | **P1** | F2 |
| **Compliance Officer · SaaS B2B** | Senior | FB | SOC 2 Type I (3-6m vía Drata) → Type II (Series A) · ISO 27001 aspiracional · vendor compliance | **P2** | F3 |
| **Privacy Architect** `[v2-NEW capability]` | Staff+ | Compartido | Capability dentro de AppSec/Compliance · diseño N0–N4 enforcement · biometric residency BR São Paulo / MX Querétaro / CO Bogotá / AR-CR fallback BR | **P2** | F3 |
| **Regulatory Specialist · Hardware/Wellness** | Senior | Scan + MWT | CE, RoHS, FCC Part 15 (BLE), ANATEL, claims footwear LATAM, no-FDA stance, CRA 24h reporting | **P1** | F2 |
| **Legal Counsel · Comercial** | Senior | Compartido | Contratos B2B, distribución LATAM, equity, IP, sociedades MX/CO/CR/BR | **P2** | F3 |
| **Compliance Engineer (técnico)** | Senior | Compartido | Implementación POL_DATA_CLASSIFICATION, audit log queries, reportes regulatorios automatizados, Drata workflow | **P2** | F3 |

**Total disciplina: 7 compliance/legal** (+2 vs v1.0).

---

## 13. Design (UX / UI / Research / Brand)

| Rol | Seniority | Scope | Responsabilidad core | Prioridad | Fase |
|---|---|---|---|---|---|
| **Head of Design** | Staff/Principal | Compartido | Design system unificado, principios UX, lead hiring design | **P0** | F1 |
| Senior Product Designer · FaberLoom | Senior | FB | Mesa de Control, Iterar, Cotización, Skill/Agent Factory, lente `SKILL_FRONTEND_TEN_PRINCIPLES_V2` aplicada | **P0** | F1 |
| Senior Product Designer · ScanFoot | Senior | Scan | UI Electron, mobile apps, hardware↔UI feedback loops | **P1** | F2 |
| UX Researcher | Senior | Compartido | Entrevistas tenants FB, distribuidores Scan, B2B Marluvas/Tecmater, usability tests | **P1** | F2 |
| UI Designer · Design System | Mid | Compartido | Componentes, tokens, ilustración, micro-interacciones | **P2** | F3 |
| Brand & Marketing Designer | Senior | MWT + FB | Rana Walk brand evolution, FB landing/marketing, comms B2B | **P2** | F3 |
| Content Designer / UX Writer | Mid | Compartido | Copy producto, voice & tone (existe `SKILL_HUMANIZE_BRAND` + `SKILL_HUMANIZE_COMMS`) | **P2** | F3 |

**Total disciplina: 7 design** (sin cambio vs v1.0).

> Nota Kimi A4: Design Engineer movido a §5 Frontend (puente design↔code).

---

## 14. QA / Testing / Quality `[v2-EXPANDED]`

| Rol | Seniority | Scope | Responsabilidad core | Prioridad | Fase |
|---|---|---|---|---|---|
| **Head of Quality** | Staff | Compartido | Trophy testing strategy 2026 (revisado), contract testing primary, fixtures (no entrenan) | **P1** | F2 |
| Senior QA Automation Engineer · FB | Senior | FB | Pytest + Playwright, fixtures Ciclope, Schemathesis FastAPI, regression CI | **P0** | F1 |
| Senior QA Automation Engineer · MWT + Scan | Senior | MWT + Scan | Tests Amazon SP-API contracts, hardware acceptance gates AC-*, B2B integration | **P1** | F2 |
| **Contract Testing Engineer** `[v2-NEW capability]` | Senior | Compartido | Pact + PactFlow B2B, broker workflow, breaking-change detection PR | **P1** | F2 |
| **Property-Based Testing Engineer** `[v2-NEW capability]` | Senior | Compartido | Hypothesis Python + fast-check JS, invariantes, mutation testing >60% | **P2** | F3 |
| QA Engineer · Compliance & Audit | Senior | Compartido | Tests audit log integridad SHA-chain, RLS multitenant cross-tenant tests | **P2** | F3 |
| **Chaos Engineer** `[v2-NEW]` | Mid+ | Compartido | Game day, blast radius, LitmusChaos, error budget exercises | **P2** | F3 |
| Mobile QA · Maestro E2E | Mid | Scan + futuros | Maestro YAML cross-platform, hardware real device test (80% BLE) | **P2** | F3 |
| Mid QA Engineer × 2 | Mid | Compartido | Manual exploratory, regression, bug triage | **P2** | F3 |

**Total disciplina: 10 QA** (+3 vs v1.0).

---

## 15. Database / Data Platform

| Rol | Seniority | Scope | Responsabilidad core | Prioridad | Fase |
|---|---|---|---|---|---|
| Senior Database Engineer · Postgres + RLS | Senior | Compartido | Postgres 16, RLS multitenant hardened (SET LOCAL + NULLIF · pgbouncer tx mode), indexing, query perf, pgvector tuning <10M | **P1** | F2 |
| Senior Database Engineer · Migrations & Schema | Senior | Compartido | Migrations, sealed schemas (POL_DATA_CLASSIFICATION v1.4 sealed), backward compat | **P2** | F3 |
| Database Reliability Engineer | Senior | Compartido | Backup/restore (pg_dump diario + rsync S3), replication, HA Postgres roadmap | **P2** | F3 |

**Total disciplina: 3 DB** (sin cambio vs v1.0).

---

## 16. Customer Success & Support

| Rol | Seniority | Scope | Responsabilidad core | Prioridad | Fase |
|---|---|---|---|---|---|
| **Head of Customer Success** | Senior | FB + Scan distribuidores | Onboarding tenants, retention, upsell, customer health score | **P1** | F2 |
| Senior CSM · FaberLoom Enterprise | Senior | FB | Tenants Pro/Enterprise, QBRs, expansion revenue | **P2** | F3 |
| CSM · FaberLoom SMB | Mid | FB | Tenants Starter, automation onboarding, pooled CS | **P2** | F3 |
| Senior Solutions Engineer · FB | Senior | FB | Pre-sales técnico (cubierto parcial por Solutions Architect §2), POCs Enterprise tier 1 | **P2** | F3 |
| **Implementation Engineer** `[v2-NEW]` | Senior | FB + MWT B2B | Integraciones SAP/ERP custom on-boarding tenant, white-glove first 30 days | **P2** | F3 |
| Support Engineer · Tier 2 | Mid | Compartido | Bug triage, escalación a eng, runbooks | **P2** | F3 |
| Distributor Success Manager · ScanFoot | Senior | Scan | Onboarding distribuidores, training, hardware support coordination | **P2** | F3 |

**Total disciplina: 7 customer success** (+1 vs v1.0).

---

## 17. Sales & GTM

| Rol | Seniority | Scope | Responsabilidad core | Prioridad | Fase |
|---|---|---|---|---|---|
| **Head of Sales / VP Revenue** | VP | Compartido | Estrategia GTM cross-product, pricing, partnerships LATAM | **P2** | F3 |
| Senior Account Executive · FaberLoom Enterprise LATAM | Senior | FB | Fabricantes calzado/textil/etc · pipeline 50+ accounts | **P2** | F3 |
| Account Executive · FaberLoom Mid-market | Mid | FB | Tenants Starter+Pro, inbound, demos, contracts | **P2** | F3 |
| BDR / SDR × 2 | Junior–Mid | FB | Outbound, prospecting, cold outreach, LinkedIn | **P3** | F3–F4 |
| Senior Account Manager · MWT B2B | Senior | MWT | Marluvas, Tecmater, expansion México→Colombia, key accounts | **P1** | F2 |
| Marketplace Manager · Rana Walk | Senior | MWT | Amazon FBA optimization, expansión a Mercado Libre/Shopify, Helium 10 ops | **P1** | F2 |
| **Head of Marketing** | Senior | Compartido | Demand gen FB, brand Rana Walk, content, events | **P2** | F3 |
| **Product Marketing Manager** `[v2-NEW]` | Senior | FB | Positioning, launches, pricing comms, sales enablement | **P2** | F3 |
| Content Marketing Manager | Mid | FB | Blog, casos de éxito, SEO, lead magnets | **P3** | F4 |
| Performance Marketing Manager | Mid | MWT (Rana Walk) | Amazon Ads, Google Ads, Meta Ads, attribution | **P2** | F3 |

**Total disciplina: 11 sales/GTM** (+1 vs v1.0).

---

## 18. Operations

| Rol | Seniority | Scope | Responsabilidad core | Prioridad | Fase |
|---|---|---|---|---|---|
| **Head of Operations** | Senior | MWT + Scan | Amazon FBA ops, B2B fulfillment, hardware logistics (Scan) | **P1** | F2 |
| Senior Amazon FBA Ops Specialist | Senior | MWT | Inventory planning, shipments USA/MX/BR, ODR/LSR/VTR mgmt | **P1** | F2 |
| Procurement & Supply Chain Manager | Senior | MWT + Scan | Compras LATAM, manufacturing scan hardware, freight | **P2** | F3 |
| Logistics Coordinator B2B | Mid | MWT | Marluvas/Tecmater fulfillment LATAM, aduanas, 3PLs | **P2** | F3 |
| Operations Analyst | Mid | Compartido | KPIs, reporting, process improvement | **P3** | F3–F4 |

**Total disciplina: 5 ops** (sin cambio vs v1.0).

---

## 19. People / HR / Talent

| Rol | Seniority | Scope | Responsabilidad core | Prioridad | Fase |
|---|---|---|---|---|---|
| **Head of People / HR Lead** | Senior | Todo | Hiring strategy, comp+benefits LATAM, performance, retention | **P1** | F2 |
| Senior Tech Recruiter | Senior | Todo | Sourcing eng/AI/security senior LATAM+remoto | **P1** | F2 |
| People Operations Specialist | Mid | Todo | Onboarding, payroll multi-país, employment LATAM | **P2** | F3 |
| Tech Recruiter | Mid | Todo | Mid-level eng, design, sales recruiting | **P2** | F3 |

**Total disciplina: 4 people** (sin cambio vs v1.0).

---

## 20. Finance & Admin

| Rol | Seniority | Scope | Responsabilidad core | Prioridad | Fase |
|---|---|---|---|---|---|
| Senior Finance Manager / Controller | Senior | Todo | Books, AR/AP, multi-país (CR/MX/CO/BR), tax, audit | **P1** | F2 |
| FP&A Analyst | Mid | Todo | Forecasts financieros, modelo SaaS metrics (ARR, NRR, CAC, LTV) | **P2** | F3 |
| Accounting Specialist · LATAM | Mid | Todo | Contabilidad multi-país, fiscalía LATAM | **P2** | F3 |

**Total disciplina: 3 finance** (CFO ya en §1).

---

## Resumen de headcount por fase v2.0

| Disciplina | F1 (0–6m) | F2 (6–12m) | F3 (12–18m) | F4 (18–24m) | Total 24m | Δ v1.0 |
|---|---|---|---|---|---|---|
| 1. Leadership & Product | 3 | +3 | +2 | +1 | 9 (+CEO existente) | +1 |
| 2. **Architecture (NEW)** | 1 | +1 | 0 | 0 | 2 | **+2** |
| 3. Engineering Leadership | 5 | +2 | +2 | +1 | 10 | +1 |
| 4. Backend Engineering | 5 | +5 | +3 | +1 | 14 | +1 |
| 5. Frontend Engineering | 5 | +2 | +2 | 0 | 9 | +2 |
| 6. Mobile Engineering | 0 | 0 | +3 | +2 | 5 | +2 |
| 7. AI & Agents | 6 | +3 | +2 | 0 | 11 | +1 |
| 8. Data/ML/Forecasting | 0 | +4 | +2 | +1 | 7 | +1 |
| 9. **Hardware/Firmware (EXPANDED)** | 1 | +5 | +2 | 0 | 8 | **+5** |
| 10. **DevOps/SRE/Platform/Observ (SPLIT)** | 3 | +3 | +1 | 0 | 7 | +2 |
| 11. **Security (SPLIT)** | 0 | +3 | +3 | +1 | 7 | +2 |
| 12. Compliance/Privacy/Legal | 0 | +3 | +4 | 0 | 7 | +2 |
| 13. Design | 2 | +2 | +3 | 0 | 7 | 0 |
| 14. **QA/Testing (EXPANDED)** | 1 | +3 | +5 | +1 | 10 | +3 |
| 15. DB/Data Platform | 0 | +1 | +2 | 0 | 3 | 0 |
| 16. Customer Success | 0 | +1 | +6 | 0 | 7 | +1 |
| 17. Sales & GTM | 0 | +2 | +7 | +2 | 11 | +1 |
| 18. Operations | 0 | +2 | +2 | +1 | 5 | 0 |
| 19. People / HR | 0 | +2 | +2 | 0 | 4 | 0 |
| 20. Finance & Admin | 0 | +1 | +2 | 0 | 3 | 0 |
| **Total acumulado** | **~28** | **~70** | **~115** | **~135 FTE** | **~135 FTE** | **+26** |

**Diferencia v1.0 → v2.0: +26 FTE** distribuidos prioritariamente en Hardware (+5), QA (+3), AI specialty (+1, con 3 sub-roles new), Mobile (+2), Frontend (+2), DevOps/Platform (+2), Security (+2), Compliance (+2), Architecture (+2 disciplina nueva).

---

## Top-10 roles indispensables (Kimi S1)

Roles que NO estaban en v1.0 o estaban sub-dimensionados — orden de hire estratégico:

| # | Rol | Disciplina | Seniority | Fase | Prioridad | Por qué no se puede diferir |
|---|---|---|---|---|---|---|
| 1 | Software Architect | §2 Architecture | Staff/Principal | F1 | **P0** | Sin él, deuda estructural a 60 eng se vuelve irreversible |
| 2 | Privacy Engineer | §12 Compliance | IC3-4 | F2 | **P0** | Codifica PbD; DPO no escribe código. Sin PE no hay enforcement N4 |
| 3 | AppSec Architect | §11 Security | Staff/Principal | F2 | **P0** | SDLC + threat model + gates. Sin él DevSecOps reactivo |
| 4 | Platform Engineer × 2 | §10 DevOps/Platform | Senior+ | F1 | **P0** | IDP + golden paths. Umbral 50 eng llegará en F2 |
| 5 | AI Agent Architect | §7 AI/Agents | Staff+ | F1 | **P0** | Cognición + memoria + planning + HITL. No es backend común |
| 6 | Observability Engineer | §10 DevOps/Platform | Mid–Senior | F2 | **P1** | Plataforma OTel + SLOs-as-code. SRE consume, este construye |
| 7 | Embedded Architect | §9 Hardware | Staff | F1 | **P1** | Sin él ScanFoot no pasa AC-02 gate |
| 8 | AI Eval / Red Team | §7 AI/Agents | Senior | F1 | **P1** | Adversarial + golden corpus + safety agentes autónomos |
| 9 | Analytics Engineer | §8 Data/ML | Mid–Senior | F2 | **P1** | dbt diferenciado de Data Engineer. MWT tiene 0 |
| 10 | Mobile Performance Specialist | §6 Mobile | Senior+ | F3 | **P2** | BLE throughput + battery + p99 <50ms para hardware biometric |

---

## Lo que falta / pendientes / "no sé qué quedará"

(Heredado de v1.0, validado contra Kimi swarm — sin cambios materiales.)

| Función | Por qué podría ser necesaria | Recomendación |
|---|---|---|
| **DevRel / Developer Relations** | Si FB abre Skills SDK público | **Diferir a F4** |
| **Technical Writer / Documentation** | Docs públicas FB API/integration | **F3 (1 persona)** |
| **Localization Manager / i18n Lead** | LATAM: ES/PT-BR/EN | **F3 (1 persona)** |
| **Hardware Industrial Designer** | Si ScanFoot evoluciona OEM → producto MWT-branded | **Diferir post-F4** |
| **AI Safety / Red Team** | Cubierto en §7 AI Eval/Red Team Engineer `[v2 RESUELTO]` | **F1 ahora** |
| **Procurement Hardware Sourcing China** | Negociación directa Bangni/Maxrays | **Cubierto en §18 Procurement** |
| **Community Manager (Rana Walk)** | Reviews Amazon, redes sociales B2C | **F3 (1 persona dentro de Marketing)** |
| **Field Sales LATAM** | Reps físicos visitando fabricantes | **Diferir post-F4** |
| **Government Relations / Public Affairs** | FB Government tier ($2499/mes) | **Diferir** |
| **Trust & Safety** | Pool colectivo k-anon ≥5 (KR L3) | **F4** |
| **Internal Tools Engineering** | Cubierto distribuido en §4 Backend / §10 Platform | **Si team interno >50: 1 dedicado** |

---

## Riesgos del plan

| Riesgo | Severidad | Mitigación |
|---|---|---|
| Hiring 135 FTE en 24m sin funding suficiente → quemar runway | P0 | Phasing estricto F1→F4, gates de revenue per fase |
| Centralización single CTO bottleneck en F1 | P1 | Hire VP Eng + Software Architect + 5 Heads en F1 paralelo |
| Compliance LATAM se convierte en blocker GA | P1 | Privacy Engineer **+** DPO en F2, no F3. Privacy by design desde F1 |
| Hardware Scan (manufacturing China) sin liaison local | P1 | Embedded Architect F1, Hardware Ops F2. Visitas in-person Bangni/Shenzhen |
| Multitenant security incident pre-SOC 2 | P0 | AppSec Architect Staff en F2 obligatorio, threat modeling Sprint 1A FB |
| Burnout founder/CTO carga inicial | P1 | COO/Chief of Staff en F2 |
| Hiring senior remoto LATAM compite con USA/EU comp | P1 | Tech Recruiter dedicado F2, comp benchmark LATAM-remoto realista |
| **Microservices premature (anti-pattern Kimi S3 #1)** `[v2-NEW]` | P0 | Software Architect mandata modular monolith hasta umbral 1:8 platform ratio |
| **Hardware <5 FTE imposible (anti-pattern Kimi S3 #5)** `[v2-NEW]` | P0 | 8 FTE antes AC-02 gate. Sin esto producto biométrico no escala |

---

## Próximos pasos

| Prioridad | Item | Bloqueo | Dueño |
|---|---|---|---|
| **P0** | Validar v2.0 con CEO | Lectura | CEO |
| **P0** | Decidir orden exacto de hire F1 — 28 FTE simultáneos imposible | v2.0 aprobado | CEO + futuro CTO |
| **P0** | Crear `ENT_GOB_HIRING_ROADMAP_F1` con candidatos concretos, fechas, comp ranges | v2.0 aprobado | CEO + (futuro) Head of People |
| P1 | Crear `ENT_GOB_COMP_BANDS_LATAM` con bandas salariales | Roadmap firmado | Head of People |
| P1 | Crear `POL_HIRING_GATES` con gates revenue/runway per fase | F1 cerrado | CEO + CFO |
| P1 | Reconciliar `ENT_GOB_PENDIENTES` con roles del v2.0 | v2.0 VIGENTE | CEO |
| P2 | Convertir disciplinas críticas a archivos `ENT_GOB_DISCIPLINE_*` con detalle JD/criterios/comp | Roadmap iterando | Head of People |

---

## Changelog

- **v2.0 — 2026-05-04 (CEO + Cowork + Kimi Swarm #5):** integra hallazgos SOTA 2026 vía 12 sub-agentes Kimi K2.6 paralelos. Cambios:
  - **Disciplina nueva 2 — Architecture:** Software Architect Staff/Principal + Solutions Architect (recategorizado de v1.0 §1).
  - **Disciplina 3 — Eng Leadership:** +Head of Platform Engineering (de v1.0 §2 implícito a explícito), Head of DevOps/SRE recategorizado.
  - **Disciplina 5 — Frontend:** +Design Engineer, +Accessibility Specialist.
  - **Disciplina 6 — Mobile:** expandido 3→5. KMP + iOS Native + Android Native + KMP Shared Logic + Mobile Performance Specialist (Kimi A11 [HIGH]: KMP vence Flutter/RN B2B BLE).
  - **Disciplina 7 — AI & Agents:** split en 4 sub-roles (AI Agent Architect Staff+, AI Eval/Red Team Senior, LLM Ops Senior, Prompt Eng como capability).
  - **Disciplina 8 — Data/ML:** split Data Engineer vs Analytics Engineer (Kimi A6 [HIGH]). +Streaming Engineer.
  - **Disciplina 9 — Hardware:** **expandido 3→8 FTE** (Kimi A10 [HIGH]: equipo <5 FTE imposible). +Embedded Architect Staff, RF/BLE Specialist, HW Security Engineer, HW/PCB Engineer, Manufacturing/Test.
  - **Disciplina 10 — DevOps/Platform/Observability:** split en 3 subdisciplinas. +2 Platform Engineers (Port o Roadie SaaS · NO Backstage self-hosted), +Observability/Platform Engineer (separado de SRE).
  - **Disciplina 11 — Security:** split AppSec Architect Staff/Principal + Security Engineers Sr+ + Product Security capability.
  - **Disciplina 12 — Compliance:** +Privacy Engineer IC3-4 separado de DPO (Kimi A9 [HIGH]: ratio 1:1.5).
  - **Disciplina 14 — QA:** +Contract Testing Engineer, +Property-Based Testing Engineer, +Chaos Engineer, +Mobile QA Maestro.
  - **Disciplina 16 — Customer Success:** +Implementation Engineer.
  - **Disciplina 17 — GTM:** +Product Marketing Manager.
  - **Headcount total:** ~109 → ~135 FTE objetivo a 24m (+26).
  - **Anti-patterns 2026 nuevos en §Riesgos:** microservices pre-30 devs, hardware <5 FTE.
  - **Top-10 roles indispensables:** sección nueva con orden estratégico de hire.
  - **AI Safety:** marcado como `[v2 RESUELTO]` — cubierto por AI Eval/Red Team Engineer §7.
  - **Status sigue DRAFT:** requiere validación CEO antes de promover a VIGENTE.

- **v1.0 — 2026-05-03 (CEO):** creación inicial. Inventario plataforma completa 18–24m, 19 disciplinas, ~109 FTE objetivo a 24m, full-time only. Refs: explore agent KB scan + project instructions + decisión CEO 2026-05-03.
