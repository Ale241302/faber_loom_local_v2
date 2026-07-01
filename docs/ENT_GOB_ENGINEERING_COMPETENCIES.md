# ENT_GOB_ENGINEERING_COMPETENCIES — Competencias Transversales de Ingeniería SOTA 2026

id: ENT_GOB_ENGINEERING_COMPETENCIES
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: ENT
stamp: DRAFT — 2026-05-04
aplica_a: [MWT, FaberLoom, ScanFoot]
fuente_v1: Kimi Swarm #5 (12 sub-agentes paralelos · 2026-05-04 · raw en `docs/anexos/kimi_team_swarm/`)
companion: ENT_GOB_TEAM_INVENTORY_FULL v2.0+

---

## Propósito

Catálogo de **capabilities transversales** que TODO engineer del dominio debe dominar — independiente del rol específico. No reemplaza el inventario de roles (`ENT_GOB_TEAM_INVENTORY_FULL`); lo complementa con la dimensión "qué saber, no qué hacer".

**Por qué existe este archivo:** un equipo SOTA 2026 no se compone solo de roles bien dimensionados. Hay competencias que son **piso de entrada** para cualquier hire serio en esa disciplina. Si las hire no las tiene, las contrataciones se vuelven sub-óptimas aunque el headcount sea correcto. Este es el filtro de calidad por hire.

**Cómo se usa:**
1. **En entrevistas:** cada competencia tiene método de evaluación específico. Los hiring managers se preparan con estas evals.
2. **En career path:** seniority avanza cuando el hire domina ≥X competencias del catálogo, no por años.
3. **En training plan:** los gaps detectados en el equipo actual definen qué training/contratación cerrar.
4. **En architecture decisions:** las competencias dictan qué se puede construir hoy. Sin la competencia, el ADR queda diferido.

---

## Las 10 competencias transversales (Kimi S2 + ajustes)

### C1 — Contract-first Design

| Aspecto | Detalle |
|---|---|
| Definición | OpenAPI 3.1 / AsyncAPI / Protobuf como source of truth. Spec antes de código. Lint en CI (Spectral). Mocks generados de la spec. Breaking-change detection en PR. |
| Por qué SOTA 2026 | Sin contract-first, drift spec/impl es inevitable. Code-first murió en 2024-2025 (Kimi A1 [HIGH]). |
| Cómo evaluar en hire | PR con OpenAPI spec + implementación. Detectar breaking changes. Generar mocks para QA. |
| Disciplinas que aplica | Backend, Frontend, Mobile, QA, AI/Agents, Data |
| KPI | 100% APIs con OpenAPI en repo pre-merge. Cero APIs descubiertas en producción sin spec. |
| Confianza | [HIGH] |

### C2 — Multi-tenant RLS Hardening

| Aspecto | Detalle |
|---|---|
| Definición | Postgres RLS con `SET LOCAL` por transacción + `NULLIF current_setting()` defensivo. `tenant_id` propagado en cache, queue, JWT claims. PgBouncer en transaction mode (no session). Test de penetración cross-tenant en CI. |
| Por qué SOTA 2026 | Multi-tenant lógico requiere isolation defense-in-depth. Application-level checks no bastan. Kimi A1 + A5 [HIGH]. |
| Cómo evaluar en hire | Lab práctico: crear endpoint multi-tenant. Pedir simular leak tenant A→B. Pedir defense. |
| Disciplinas | Backend, DB, Security, Platform Eng |
| KPI | 0 cross-tenant leaks en tests automatizados; pool size ≤ cores×3; waiting clients = 0 |
| Confianza | [HIGH] |

### C3 — SLO Engineering

| Aspecto | Detalle |
|---|---|
| Definición | SLIs definidos sobre user journey real (no CPU/memoria). Error budgets calculados. Burn-rate alerts. Error budget policy escrito (qué pasa cuando se quema). Tail-based sampling en OTel. |
| Por qué SOTA 2026 | "Dashboards sin SLOs" murió. Alert fatigue masivo. Kimi A7 [HIGH]: ≤3 alertas SLO-based/servicio. |
| Cómo evaluar en hire | Pedir propuesta SLO + error budget policy para FB Mesa de Control endpoint. Defender SLI elegido. |
| Disciplinas | Backend, SRE, Observability, QA, Platform Eng |
| KPI | error budget burn <2%/mes; ≤3 alertas SLO-based/servicio |
| Confianza | [HIGH] |

### C4 — HITL + Draft-first

| Aspecto | Detalle |
|---|---|
| Definición | Output N3+ requiere aprobación humana logueada con `actor_role_at_decision`. Nunca auto-write a sistema externo sin gate. `interrupt_before` en LangGraph. Approval queues con timeout y degradación graceful. |
| Por qué SOTA 2026 | ARCH_AGENT_PRINCIPLES P3 FROZEN. Trust erosion + safety incidents si auto-execute sin draft-first. Kimi A3 [HIGH]. |
| Cómo evaluar en hire | Mock con clasificación N4 biométrico. 3 gates HITL. Pedir diseño + estado machine + recovery interrupt. |
| Disciplinas | AI/Agents, Backend, Frontend, Compliance |
| KPI | 100% drafts N3+ antes write; 99.9% resume-after-interrupt |
| Confianza | [HIGH] |

### C5 — Threat Modeling (STRIDE / LINDDUN)

| Aspecto | Detalle |
|---|---|
| Definición | Diseño de controles antes del código. STRIDE para amenazas, LINDDUN para privacy. Diagramas DFD por bounded context. Mapeo controles → POL_DATA_CLASSIFICATION (N0–N4). |
| Por qué SOTA 2026 | Security generalista reactivo murió. Threat modeling preventivo es mandatory enterprise. Kimi A8 [HIGH]. |
| Cómo evaluar en hire | Caso multi-tenant ScanFoot (BIOMETRIC N4). Pedir DFD + amenazas STRIDE + controles + qué viola si saltan gate. |
| Disciplinas | Security, Backend, AI/Agents, Hardware, Architecture |
| KPI | 100% nuevas features con threat model; 0 incidents derivados de gaps no modelados |
| Confianza | [HIGH] |

### C6 — Observability-driven Debugging

| Aspecto | Detalle |
|---|---|
| Definición | Tracing + métricas + logs unificados. Correlación request-id end-to-end. Tail-based sampling. Cardinality budget (≤10 dimensiones por métrica). Sin user_id/UUID en labels. Pipelines OTel multi-backend. |
| Por qué SOTA 2026 | Cardinality explosion = costo impredecible. OTel default greenfield 95% según Kimi A7 [HIGH]. |
| Cómo evaluar en hire | Debug cross-service simulado. Pedir trace específico. Detectar cardinality issue en métrica propuesta. |
| Disciplinas | Backend, Frontend, SRE, QA, Platform Eng |
| KPI | 100% requests con trace-id propagado; cardinality budget respetado |
| Confianza | [HIGH] |

### C7 — Supply Chain Hardening (SLSA / SBOM)

| Aspecto | Detalle |
|---|---|
| Definición | SBOM generado por build (CycloneDX/SPDX). Provenance attestation SLSA L3-L4. Sigstore (Cosign + Rekor + Fulcio) firma. Kyverno/OPA Gatekeeper como admission control: bloquea imagen sin attestation. |
| Por qué SOTA 2026 | SLSA L3-L4 es enterprise table stakes 2026. CRA UE + tendencia LATAM. Kimi A8 [HIGH]. |
| Cómo evaluar en hire | Lab CI/CD con Sigstore + Kyverno. Pedir bloqueo de imagen sin attestation. Verificar provenance. |
| Disciplinas | Security, DevOps, Platform Eng |
| KPI | 100% imagenes prod con attestation SLSA L3+; 0 deploys sin verificación |
| Confianza | [HIGH] |

### C8 — Performance Budgets

| Aspecto | Detalle |
|---|---|
| Definición | Web Vitals: LCP ≤2.5s, INP ≤200ms, CLS ≤0.1. CI gate Lighthouse / Lighthouse CI. Performance budget archivo en repo. PR que excede budget bloquea merge. |
| Por qué SOTA 2026 | Performance budgets como práctica obligatoria 2026. Sin ellos, performance se degrada silenciosamente. Kimi A4 [HIGH]. |
| Cómo evaluar en hire | PR existente excede budget. Pedir fix + propuesta budget revisado. Defender trade-off. |
| Disciplinas | Frontend, Mobile, Backend |
| KPI | 100% releases pasan Lighthouse CI; INP ≤200ms p95; LCP ≤2.5s p95 |
| Confianza | [HIGH] |

### C9 — Property-based / Contract Testing

| Aspecto | Detalle |
|---|---|
| Definición | Property-based testing (Hypothesis Python · fast-check JS) para invariantes. Contract testing (Pact · PactFlow · Schemathesis FastAPI) entre services. Mutation testing >60% (mutmut · Stryker). Trophy testing pyramid (no Pyramid clásico). |
| Por qué SOTA 2026 | E2E cross-service único = flaky. Pact + property-based reemplazan según Kimi A12 [HIGH]. |
| Cómo evaluar en hire | PR con property-based test + contract verification entre 2 services. Defender invariantes. |
| Disciplinas | QA, Backend, Frontend, Mobile |
| KPI | Pact verification 100%; mutation >60%; integration >80% |
| Confianza | [HIGH] |

### C10 — DPA-as-code + Privacy Budget

| Aspecto | Detalle |
|---|---|
| Definición | Repo central con DPA chains versionados (whitelist). PR requiere review legal + eng. Privacy budget (ε en Differential Privacy) trackeado. ε≤8 alarma. Alertas a 90 días para renovación DPA. Synthetic data N3-N4 usando OpenDP. |
| Por qué SOTA 2026 | k-anonymity como única defensa cayó (re-identification). DP ε=1-10 con garantía matemática. Kimi A9 [HIGH]. |
| Cómo evaluar en hire | Repo con 5 DPA chains. Pedir PR de actualización. Detectar gap legal. Aplicar DP a query con ε=2. |
| Disciplinas | Compliance, Backend, Legal, AI/Agents |
| KPI | 100% DPA chains versionados; ε ≤8 enforcement; 0 DPAs vencidos en producción |
| Confianza | [HIGH] |

---

## Mapeo competencias × disciplinas

| Competencia | Backend | Frontend | Mobile | AI/Agents | Data/ML | Hardware | Security | DevOps/SRE | QA | DB | Compliance | Architecture |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 Contract-first | ●●● | ●●● | ●●● | ●●● | ●● | ● | ●● | ●● | ●●● | ● | ● | ●●● |
| C2 RLS Hardening | ●●● | ● | — | ●● | ●●● | — | ●●● | ●● | ●● | ●●● | ●● | ●●● |
| C3 SLO Engineering | ●●● | ●● | ●● | ●● | ●● | ● | ●● | ●●● | ●●● | ●● | — | ●●● |
| C4 HITL + Draft-first | ●● | ●● | ●● | ●●● | ●● | — | ●●● | — | ●● | — | ●●● | ●● |
| C5 Threat Modeling | ●● | ● | ● | ●● | ● | ●● | ●●● | ●● | ● | ●● | ●● | ●●● |
| C6 Observability | ●●● | ●● | ●● | ●● | ●● | ● | ●● | ●●● | ●●● | ●● | — | ●● |
| C7 Supply Chain | ●● | ● | ● | ● | ● | ●●● | ●●● | ●●● | ● | — | ●● | ●● |
| C8 Performance Budgets | ●● | ●●● | ●●● | ● | ● | ●● | — | ●● | ●● | ●● | — | ●● |
| C9 Property/Contract | ●●● | ●●● | ●● | ●●● | ●● | ●● | ● | ● | ●●● | ●● | — | ●● |
| C10 DPA-as-code | ●● | ● | ● | ●●● | ●● | ●● | ●● | ●● | ● | ●● | ●●● | ●● |

Leyenda: ●●● obligatoria · ●● fuerte ventaja · ● nice-to-have · — no aplica

---

## Anti-patterns 2026 (Kimi S3)

Estos son los 5 anti-patterns que MWT/FB/Scan deben evitar a toda costa. Cada uno está conectado a una o más competencias.

| # | Anti-pattern | Por qué dejó de ser SOTA | Reemplazo | Competencia que lo detecta |
|---|---|---|---|---|
| 1 | Microservices pre-30 devs sin platform | Distributed monolith, 12 pipelines, 0 cross-tests, cognitive overload | Modular monolith + DDD; ratio 1:8 platform | C1 (contract-first), C3 (SLO eng) |
| 2 | Security team generalista | DevSecOps reactivo, parches incoherentes, sin threat modeling | AppSec Architect 1:4 + Security Engineer ejecutor | C5 (threat modeling), C7 (supply chain) |
| 3 | Compliance técnica enterrada en legal | Security controls no se implementan; DPO no habla SDLC | Privacy Engineer + DPO separado; gates CI verificados | C10 (DPA-as-code) |
| 4 | Auto-ejecución agentes sin draft-first | Trust erosion, safety incidents, N4 biometric sin aprobación = liability | 100% drafts N3+ antes write; interrupt_before LangGraph | C4 (HITL + draft-first) |
| 5 | Hardware team <5 FTE biométrico | Imposible cubrir BLE+OTA+seguridad+PCB+test+manufactura | 8-10 FTE antes AC-02; Embedded Architect Staff | (cubierto por inventario v2.0 §9) |

---

## Cómo este archivo informa hiring

| Stage hiring | Cómo se usa |
|---|---|
| **Job Description** | Cada JD lista las 3-5 competencias core de la disciplina (de la matriz × arriba). |
| **Screening** | Recruiter filtra por menciones explícitas (CV / GitHub / portfolio). |
| **Technical interview** | Hiring manager prepara una pregunta tipo "evaluación" del catálogo por competencia core. |
| **Architecture round** | Para Senior+ y Staff+, mock real con DFD + threat model + SLO. Mide C1+C3+C5. |
| **Reference check** | Validar que la persona realmente operó (no solo conoció) la competencia. |
| **Onboarding gap detection** | Primeros 90 días, EM identifica qué competencias del rol faltan y arma plan training. |

---

## Pendientes de iteración

| Prioridad | Item | Bloqueo |
|---|---|---|
| P1 | Validar v1.0 con CEO + Head of People (cuando exista) | Lectura |
| P1 | Agregar 5-7 competencias nivel **junior** (entry-level) — actuales son senior+ | Validación v1.0 |
| P2 | Agregar competencias de **liderazgo** (EM/Tech Lead/Staff Plus) — separadas de tech depth | Career path defined |
| P2 | Agregar evals concretas codificadas (ej. coding challenge repo + rubric) | Hiring roadmap concreto |
| P3 | Convertir cada competencia a archivo `ENT_GOB_COMP_{C##}.md` con detalle profundo (criterios, rubrics, banco de preguntas) | v1.0 VIGENTE |

---

## Changelog

- **v1.0 — 2026-05-04 (CEO + Cowork + Kimi Swarm #5):** creación inicial. 10 competencias transversales SOTA 2026 derivadas de Kimi S2. Companion file de `ENT_GOB_TEAM_INVENTORY_FULL` v2.0. Status DRAFT requiere validación CEO. Ámbito: senior+ engineering. Junior y liderazgo pendientes en v2.0.
