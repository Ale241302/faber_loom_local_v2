# KIMI SWARM #5 — RAW OUTPUT | TEAM SOTA 2026 | Muito Work Limitada
# 2026-05-04 | Kimi K2.6 Swarm (12 sub-agentes paralelos)

---

## A1_ARCH — Arquitectura software

### Estado del arte 2026
| Práctica | Trade-off | Conf |
|---|---|---|
| Modular monolith + DDD + Postgres RLS + Contract-first | Single deploy, boundaries claros; isolation row-level; fuente única mocks tests | [HIGH] |
| De-microservitización (Señal) / EDA audit (Ruido) | Monolith default <50 devs; CDC resuelve 90% pre-50 tenants | [HIGH]/[MEDIA] |

### Stack SOTA top 3
| Herramienta | Uso | Trade-off | Conf |
|---|---|---|---|
| OpenAPI 3.1 + Spectral | Contract-first REST | No cubre eventos | [HIGH] |
| PostgreSQL 16 + RLS | Tenant isolation | Requiere pgbouncer + session vars | [HIGH] |
| Strangler Fig + Flags | Extracción a microservices | Dual-write temporal | [MEDIA] |

### Bloque A — Roles SOTA
| Rol | Seniority | Conf |
|---|---|---|
| Software Architect (Separado) | Staff/Principal | [HIGH] |
| Platform Engineer (Capability 1:8) | Senior+ | [HIGH] |
| API/Product Engineer (Capability/squad) | Mid-Senior | [MEDIA] |

### Bloque B — Competencias transversales
1. **DDD táctico** — Aggregates, VO, Repositories. Eval: bounded context entrevista. [HIGH]
2. **Contract-first** — Spec antes de código, lint CI, mocks. Eval: PR breaking-change detection. [HIGH]
3. **Data residency** — RLS, tenant_id en cache/DB/queue, JWT claims. Eval: audit cross-tenant leak. [HIGH]

### Anti-patterns 2026 + KPIs
| Anti-pattern | Por qué murió | KPI/SLO |
|---|---|---|
| Microservices pre-30 devs sin platform | Distributed monolith, 12 pipelines, 0 cross-tests | Ratio 1:8; deploy >1/día sin conflict |
| EDA full + event sourcing para MVP | Eventual consistency > valor | Audit 100% sync CDC; <5% async |
| Code-first API autogenerada | Drift spec/impl | 100% APIs con OpenAPI en repo pre-merge |

---

## A2_PLATFORM_ENG — Platform / IDP / DevEx

### Estado del arte 2026
| Práctica | Trade-off | Conf |
|---|---|---|
| DX Core 4 + Golden paths + TVP | Lock-in DXI holístico; defaults opt-in; 1:6–9 stream-aligned | [HIGH] |
| Agentic AI IDP (Señal) / Self-hosted <100 (Ruido) | Port $100M Serie C; managed TCO bajo | [MEDIA]/[HIGH] |

### Stack SOTA top 3
| Herramienta | Uso | Trade-off | Conf |
|---|---|---|---|
| Port | IDP SaaS agentic | Vendor lock-in | [HIGH] |
| Roadie | Managed Backstage | Menos custom | [HIGH] |
| DX (GetDX) | Medición Core 4 | DXI propietario | [MEDIA] |

### Bloque A — Roles SOTA
| Rol | Seniority | Conf |
|---|---|---|
| Platform Engineer (Dedicado) | Senior+ | [HIGH] |
| Platform PM (Dedicado) | Senior | [HIGH] |
| SRE/DevEx (Capability) | Senior+ | [MEDIA] |

### Bloque B — Competencias transversales
1. Platform-as-a-product: roadmap, adoption; hire: productos medidos. [HIGH]
2. TVP: MVP iterativo; hire: gradualidad. [HIGH]
3. Golden paths: templates opt-in; hire: libertad con defaults. [HIGH]

### Anti-patterns 2026 + KPIs
| Anti-pattern | Por qué murió | KPI/SLO |
|---|---|---|
| Backstage self-hosted <100 eng | 3–12 FTE, $1M+ | Time-to-first-service <2 sem; adoption >75% |
| DORA sin DevEx | Ignora coordinación | Core 4 + DXI quarterly |

---

## A3_AI_AGENTS — Multi-agent / agentic frameworks

### Estado del arte 2026
| Framework | Cuándo usar | Trade-off | Conf |
|---|---|---|---|
| LangGraph / CrewAI / Pydantic AI | Stateful HITL; proto role-based; single-agent type-safe | Steep curve LangChain-coupled; +48% tokens; sin HITL nativo | [HIGH] |
| MCP (Señal) / Claude SDK reemplaza (Ruido) | 78% enterprise, 9,400+ servers; v0.1.48 alpha lighter | [HIGH] |

### Stack SOTA top 3
| Herramienta | Uso | Trade-off | Conf |
|---|---|---|---|
| LangGraph + LiteLLM | Orquestación HITL, model-agnostic | Curva 1-2 semanas | [HIGH] |
| MCP servers | Tool wiring universal | Latencia remote +130ms | [HIGH] |
| Langfuse + DeepEval | Tracing + 50+ métricas pytest-native | DeepEval OSS | [HIGH] |

### Bloque A — Roles SOTA
| Rol | Seniority | Conf |
|---|---|---|
| AI Agent Architect (Separado) | Staff+ | [HIGH] |
| AI Eval / Red Team (Separado) | Senior | [HIGH] |
| Prompt Engineer (Capability) | Mid | [MEDIA] |
| LLM Ops Engineer (Separado) | Senior | [HIGH] |

### Bloque B — Competencias transversales
1. **State Management**: Checkpointing, recovery, time-travel. Eval: grafo HITL. [HIGH]
2. **Tool Governance**: MCP lifecycle, OAuth 2.1. Eval: audit shadow IT. [HIGH]
3. **HITL UX**: Draft-first, approval queues. Eval: mock N4 con 3 gates. [HIGH]

### Anti-patterns 2026 + KPIs
| Anti-pattern | Por qué murió | KPI/SLO |
|---|---|---|
| CrewAI producción regulated | Sin checkpointing determinístico | LangGraph; 99.9% resume-after-interrupt |
| Auto-ejecución sin draft-first | Trust erosion, safety incidents | 100% drafts N3+ antes write |

---

## A4_FRONTEND — Frontend 2026

### Estado del arte 2026
| Práctica | Líder | Trade-off | Conf |
|---|---|---|---|
| Next.js 15/16 RSC | Enterprise default | Vercel coupling, RSC overhead | [HIGH] |
| TanStack Start (RC) | Type-safe, Vite, explícito | No maduro producción | [MEDIA] |
| React Router v7 | Remix patterns legacy | No RSC nativo | [MEDIA] |
| Zustand (Señal) / Design Engineer rol (Señal) | ~3 KB DX probada; Figma-to-code, design systems | [HIGH] |

### Stack SOTA top 3
| Herramienta | Uso | Trade-off | Conf |
|---|---|---|---|
| Next.js 15 + Turbopack | SaaS, e-commerce | Vendor lock-in parcial | [HIGH] |
| Zustand + TanStack Query | Estado + server state | Necesita selectors Zustand | [HIGH] |
| Lighthouse CI + perf-budget | CI gates | Requiere definir SLOs | [HIGH] |

### Bloque A — Roles SOTA
| Rol | Seniority | Conf |
|---|---|---|
| Frontend Engineer (Capability base) | Mid–Staff | [HIGH] |
| Design Engineer (Separado en equipos >6 FE) | Mid–Senior | [HIGH] |
| Accessibility Specialist (Separado en scale) | Senior | [MEDIA] |

### Bloque B — Competencias transversales
1. **Performance budgets** — LCP ≤2.5s, INP ≤200ms, CLS ≤0.1; bloquear CI si se exceden. Eval: Lighthouse CI. [HIGH]
2. **Full-stack type safety** — End-to-end validación (Zod/TanStack); eval: code review boundaries. [HIGH]
3. **Agentic UI streaming** — SSE/WebSocket para LLM tokens + estados progresivos; eval: PoC. [HIGH]

### Anti-patterns 2026 + KPIs
| Anti-pattern | Por qué murió | KPI/SLO |
|---|---|---|
| `useContext` global state | Re-renders masivos, no escala | Zustand selector + INP ≤200 ms |
| WCAG como "nice to have" B2B | Ley 7600 CR Art. 50 + Directriz 036 obligan sector público; privado en riesgo | 100% WCAG 2.2 AA CI gate |

---

## A5_BACKEND — Backend Python / FastAPI

### Estado del arte 2026
| Práctica | Fortaleza | Trade-off | Conf |
|---|---|---|---|
| FastAPI v0.115+ | Default greenfield, ecosistema AI/LLM, hiring amplio | Pydantic hot-path overhead | [HIGH] |
| Litestar 2.x+ | msgspec más rápido, DI limpio, typing estricto | Comunidad pequeña, bus-factor | [HIGH] |
| Híbrido SQLAlchemy writes + asyncpg reads | ORM para transacciones, raw para lecturas hot | Doble pool, complejidad operativa | [HIGH] |
| Go/Rust reemplaza Python (Ruido) / Temporal (Señal) | Python domina AI/B2B; Go >10k RPS. Durable execution, audit trail, retries | [HIGH]/[MEDIA] |

### Stack SOTA top 3
| Herramienta | Uso | Trade-off | Conf |
|---|---|---|---|
| FastAPI + Pydantic v2 | APIs async, validación, OpenAPI | Overhead serialización | [HIGH] |
| ARQ (Redis) | Background jobs async FastAPI | Sin workflow durable ni UI avanzada | [HIGH] |
| PgBouncer tx mode + asyncpg | Pool multi-tenant RLS | SET LOCAL por tx; disable prepared statements | [HIGH] |

### Bloque A — Roles SOTA
| Rol | Seniority | Conf |
|---|---|---|
| Platform Engineer (Python/Go) (Separado) | Senior+ | [HIGH] |
| AI Backend Engineer (Capability/Backend) | Mid-Senior | [MEDIA] |
| Data/Worker Engineer (Capability) | Senior | [HIGH] |

### Bloque B — Competencias transversales
1. **Async disciplinado**: evitar gather() sobre sessions SQLAlchemy; eval: code review greenlet leaks. [HIGH]
2. **RLS hardening**: SET LOCAL por tx + NULLIF current_setting; eval: test penetración por tenant. [HIGH]
3. **Hybrid SQL fluency**: leer EXPLAIN, decidir ORM vs raw por path; eval: benchmark endpoints reales. [HIGH]

### Anti-patterns 2026 + KPIs
| Anti-pattern | Por qué murió | KPI/SLO |
|---|---|---|
| Async SQLAlchemy para todo | Greenlet bridge 1.5–14× más lento; bulk inserts críticos | <20% paths raw SQL; p95 lectura <50ms |
| Celery en nuevo proyecto | Sin async nativo, config pesada, result backend legacy | ARQ/Temporal según complejidad; startup worker <2s |
| Session pooling sin PgBouncer | Agotamiento conexiones Postgres en multi-tenant | Pool size ≤ cores×3; waiting clients = 0 |

---

## A6_DATA — Data / lakehouse / streaming

### Estado del arte 2026
| Práctica | Trade-off | Conf |
|---|---|---|
| Iceberg default | Engine-agnostic; Delta=lock-in | [HIGH] |
| Kafka+Debezium | Audit tenant_id; Redpanda drop-in | [HIGH] |
| dbt SOTA SQLMesh challenger | 45K orgs. 9x faster | [HIGH] |
| Lakehouse todo SaaS (Ruido) / AE separado (Señal) | <1TB/día Postgres OK; DE=infra AE=modelado | [HIGH] |

### Stack SOTA top 3
| Herramienta | Uso | Trade-off | Conf |
|---|---|---|---|
| Iceberg+DuckDB | Lakehouse warm/cold | Compaction manual S3/MinIO | [HIGH] |
| Kafka+Debezium | Streaming CDC | Ops lee WAL sin carga | [HIGH] |
| dbt Core/Cloud | Transform analytics | Full-refresh caro | [HIGH] |

### Bloque A — Roles SOTA
| Rol | Seniority | Conf |
|---|---|---|
| Data Engineer (Separado) | Mid-Sr | [HIGH] |
| Analytics Engineer (Separado) | Mid-Sr | [HIGH] |
| Vector DB / AI Infra (Capability AI/ML) | Sr | [MEDIA] |

### Bloque B — Competencias transversales
1. **CDC sourcing** — WAL lag idempotency eval Debezium. [HIGH]
2. **Vector search** — HNSW tuning eval pgvector vs Qdrant. [HIGH]
3. **Incremental** — dbt pruning eval -30% compute 90d. [HIGH]

### Anti-patterns 2026 + KPIs
| Anti-pattern | Por qué murió | KPI/SLO |
|---|---|---|
| Batch nocturno | Stale no escala | CDC <1s p99 |
| Pinecone sin pgvector <10M | Lock-in 10x | pgvector p95 <50ms |

---

## A7_OBSERV — Observability / SLO / tracing

### Estado del arte 2026
| Práctica | Estado | Trade-off | Conf |
|---|---|---|---|
| OpenTelemetry + SLO-as-Code + eBPF | Estándar de facto 95% greenfield; mainstream beyond Google; 67% K8s prod Cilium+Hubble+Pixie+Beyla | Soft lock-in extensiones vendor; error budgets discipline; kernel ≥5.10 | [HIGH] |

### Stack SOTA top 3
| Herramienta | Uso | Trade-off | Conf |
|---|---|---|---|
| Grafana LGTM + OTel Collector | Full stack OSS; Loki+Tempo+Mimir | Alta carga operativa; Cloud cost similar Datadog escala | [HIGH] |
| ClickHouse-based (SigNoz/Coroot) | Alta cardinalidad, trazas/logs unificados | Tuning ingestion; menor ecosistema | [HIGH] |
| Datadog/Honeycomb | SaaS turnkey, per-host/event-based | Lock-in y billing impredecible | [HIGH] |

### Bloque A — Roles SOTA
| Rol | Seniority | Conf |
|---|---|---|
| Observability/Platform Engineer (Separado de SRE; SRE consume, este construye) | Mid-Senior (5+) | [HIGH] |
| Reliability Platform Engineer (Capability/SRE moderno) | Senior | [HIGH] |

### Bloque B — Competencias transversales
1. **OTel Collector architecture** — diseñar pipelines sampling, tail-based filtering, multi-backend routing; eval: diseño pipeline alta cardinalidad. [HIGH]
2. **SLO engineering** — definir SLIs de user journey real, no CPU; eval: propuesta SLO + error budget policy. [HIGH]
3. **eBPF fluency** — entender límites kernel, CO-RE, networking vs observability; eval: troubleshooting Cilium/Hubble. [MEDIA]

### Anti-patterns 2026 + KPIs
| Anti-pattern | Por qué murió | KPI/SLO |
|---|---|---|
| Dashboards sin SLOs (monitoring) | Alert fatigue; no vincula user impact | ≤3 alertas SLO-based/servicio; error budget burn <2%/mes |
| Métricas con user_id/UUID en labels | Cardinality explosion, costo impredecible | Cardinality budget/servicio; 100% métricas ≤10 dimensiones |
| Instrumentación propietaria vendor-locked | OTel es default; migrar cuesta meses | 100% nuevos servicios OTel SDK nativo; 0 agentes propietarios greenfield |
| Retención uniforme "guardar todo" | Costo insostenible; análisis forense ineficiente | Tiered retention: 7 días full, 30 días agregado, 90+ días SLI-only |

---

## A8_SECURITY — Security / supply chain

### Estado del arte 2026
| Práctica | Estado | Trade-off | Conf |
|---|---|---|---|
| Zero Trust + SLSA L3-L4 + PQC híbrido | Table stakes enterprise; Enterprise exige L3-L4; Migración activa 2026-2028 | Coste IAM/ABAC; overhead CI hermético; latencia + complejidad PQC | [MEDIA]/[HIGH] |

### Stack SOTA top 3
| Herramienta | Uso | Trade-off | Conf |
|---|---|---|---|
| Sigstore (Cosign+Rekor+Fulcio) | Firma SBOM/provenance, verificación registry | Dependencia infra pública; puede usar private | [HIGH] |
| Kyverno/OPA Gatekeeper | Admission control: bloquea imagen sin attestation SLSA | Curva política-as-code; necesita K8s | [HIGH] |
| PTaaS agentic (Cobalt) | Pentest continuo + compliance audit anual | No es red team interno; ideal <100 eng | [MEDIA] |

### Bloque A — Roles SOTA
| Rol | Seniority | Conf |
|---|---|---|
| AppSec Architect (Separado) | Staff/Principal | [HIGH] |
| Security Engineer (Separado) | Sr+/Staff | [HIGH] |
| Product Security Engineer (Capability/AppSec) | Staff | [MEDIA] |

### Bloque B — Competencias transversales
1. **Threat modeling (STRIDE/LINDDUN)** — diseñar controles antes del código — eval: entrevista caso multi-tenant + review diagrama propio. [HIGH]
2. **Supply chain hardening (SLSA/SBOM)** — generar provenance y verificar en admission — eval: lab CI/CD Sigstore + Kyverno. [HIGH]
3. **HITL + privacy-by-design (N0-N4)** — clasificación datos y controles técnicos por nivel — eval: analizar flujo BIOMETRIC ScanFoot y proponer arquitectura. [HIGH]
4. **Zero Trust IAM** — least privilege, SSO/SAML/OIDC, session revocation — eval: audit config RBAC app real. [MEDIA]

### Anti-patterns 2026 + KPIs
| Anti-pattern | Por qué murió | KPI/SLO |
|---|---|---|
| Security team generalista sin separación AppSec/CloudSec/IR | DevSecOps falla sin diseño estratégico; se vuelve reactivo | Ratio AppSec Architect : Engineer 1:4; MTTR IR <4h |
| Compliance técnica enterrada en legal | Security controls no se implementan si legal no habla SDLC | 100% gates SLSA verificados por CI; 0 excepciones manuales |
| Pentest anual puntual como única validación | Attack surface cambia en días; agentic AI explica ventana de exposición | Cobertura continua PTaaS: 100% releases con attestation + DAST |

---

## A9_COMPLIANCE — Compliance LATAM / privacy engineering

### Estado del arte 2026
| Práctica | Trade-off | Conf |
| PE ≠ DPO | PE codifica; DPO gobierna | [HIGH] |
| DP ε=1-10 > k-anon | Garantía matemática; k-anon cae | [HIGH] |
| Compliance auto | Drata mid-market; Vanta startup; Thoropass bundled | [MEDIA] |
| AI agents compliance | Señal: SOC 2 Type I en días | [MEDIA] |
| EU residency default | Señal: NIS2/DORA; LATAM sigue | [HIGH] |
| DPA on-chain | Ruido: Sin enforcement | [BAJA] |

### Stack SOTA top 3
| Herramienta | Uso | Trade-off | Conf |
|---|---|---|---|
| Drata | SOC 2/ISO evidence | No EU res; AWS/GCP OK | [HIGH] |
| OneTrust VRM | DPA chain + VRM | Overkill <50 | [MEDIA] |
| OpenDP | DP-SGD ML/analytics | Requiere experto | [HIGH] |

### Bloque A — Roles SOTA
| Rol | Seniority | Conf |
|---|---|---|
| Privacy Engineer (Separado) | IC3-4 | [HIGH] |
| DPO (Separado) | Dir | [HIGH] |
| Privacy Architect (Capability) | Staff+ | [MEDIA] |

### Bloque B — Competencias transversales
1. DPA-as-code: whitelist versionado; PR legal+eng. [HIGH]
2. Privacy budget: trackea ε; MI tests. [HIGH]
3. Residency: BR São Paulo AWS/Oracle; MX Querétaro AWS/GCP; CO Bogotá AWS/Oracle; AR/CR local o BR/MX. [HIGH]
4. HITL N4: biométrico aprobación logueada. [HIGH]

### Anti-patterns 2026 + KPIs
| Anti-pattern | Por qué murió | KPI reemplazo |
|---|---|---|
| Legal hace técnico | No operan | DPO:PE 1:1.5; pass >95% |
| k-anon única defensa | Re-id | DP ε≤8; synthetic N3-N4 |
| SOC 2 Type II tardío | Bloquea | Type I seed; Type II Series A |

---

## A10_HW_IOT — Hardware / BLE / OTA / device mgmt

### Estado del arte 2026
| Práctica | Líder | Trade-off | Conf |
| Rust+Embassy | STM32/Nordic/ESP32 prod | 5-6 sem curva; no cert DO-178C | [HIGH] |
| nRF Connect SDK/Zephyr | Stack oficial Nordic 2026 | Más abstracción que nRF5 legacy | [HIGH] |
| MCUboot+ECDSA firmado | Estándar OTA 2026 | Requiere HSM offline claves | [HIGH] |

### Stack SOTA top 3
| Herramienta | Uso | Trade-off | Conf |
| nRF Connect SDK + MCUboot | BLE+OTA nRF54/nRF52 | Curva Zephyr/Kconfig | [HIGH] |
| Memfault | Fleet debug+OTA RTOS | Precio escalable; Zephyr preview | [MEDIA] |
| probe-rs + cargo-embed | Debug/flasheo Rust | Reemplaza JLink/OpenOCD | [HIGH] |

### Bloque A — Roles SOTA
| Rol | Seniority | Conf |
| Embedded Architect (Separado) | Staff | [HIGH] |
| Firmware Engineer (2× mín) | Senior | [HIGH] |
| RF/BLE Specialist (Separado) | Senior | [HIGH] |
| Security Engineer (Separado) | Senior | [HIGH] |
| HW/PCB Engineer (Separado) | Senior | [HIGH] |
| Manufacturing/Test (Separado) | Mid | [MEDIA] |

### Bloque B — Competencias transversales
1. **Rust/C interop** — FFI migración gradual; eval: proyecto STM32H7. [HIGH]
2. **Seguridad firmware** — Secure boot, OTA signed, SBOM; CRA 24h reporte. [HIGH]
3. **Devicetree/Zephyr** — Overlays, Kconfig, Partition Manager; obligatorio NCS. [HIGH]

### Anti-patterns 2026 + KPIs
| Anti-pattern | Por qué murió | KPI/SLO |
|---|---|---|
| nRF5 SDK legacy | Maintenance mode, sin nRF54 | 100% builds NCS/Zephyr by Q3 |
| OTA sin firma | CRA/RED prohíben; MITM/brick | 100% ECDSA firmado + rollback |
| Equipo <5 FTE HW/FW | Imposible BLE+OTA+seg+PCB+test | 8-10 FTE antes AC-02 gate |
| Biométricos sin cifrado hw | Secure storage mandatory CRA I | CryptoCell-310/KMU 100% units |

---

## A11_MOBILE — Mobile iOS/Android

### Estado del arte 2026
| # | Hallazgo SOTA | Conf |
| 1 | KMP + Native UI gana B2B BLE: lógica compartida, UI nativa, acceso directo CoreBluetooth | [HIGH] |
| 2 | Bitrise/Codemagic + Fastlane. Xcode Cloud solo iOS, limitado | [HIGH] |
| 3 | Privacy manifests obligatorio mayo 2024. B2B declara APIs sensibles + SDK signatures | [HIGH] |
| 4 | Mobile Performance Specialist emerge — hiring trends 2025 | [MEDIA] |
| 5 | iOS: CoreBluetooth async/await/Combine; Android: Kotlin Flow + Coroutines; SKIE Flows→Swift | [HIGH] |
| 6 | Maestro E2E cross-platform (<1% flakiness, YAML, <15m) | [HIGH] |
| KMP default B2B hardware (Señal) / Flutter declina B2B (Ruido) | Acceso nativo BLE, shared logic, no bridge overhead / Engine overhead, plugin fragilidad | [HIGH]/[MEDIA] |

### Stack SOTA top 3
| Herramienta | Uso | Trade-off | Conf |
| KMP + SKIE | Shared logic + native UI binding | Curva Gradle expect/actual | [HIGH] |
| Bitrise + Fastlane | CI/CD mobile + store deploy | Costo escalable, SaaS global | [HIGH] |
| Maestro | E2E cross-platform | YAML simple, no código infra test | [HIGH] |

### Bloque A — Roles SOTA
| Rol | Seniority | Conf |
| Mobile Engineer (iOS) (Capability) | Mid-Senior | [HIGH] |
| Mobile Engineer (Android) (Capability) | Mid-Senior | [HIGH] |
| Mobile Performance Specialist (Separado en >6 mobile) | Senior+ | [MEDIA] |

### Bloque B — Competencias transversales
1. **BLE lifecycle management** — scanning, pairing, MTU negotiation, background modes. Eval: debug session hardware real. [HIGH]
2. **Privacy manifest compliance** — declaración APIs sensibles, SDK signatures, NSPrivacyTracking. Eval: audit App Store rejection risk. [HIGH]
3. **KMP boundary design** — expect/actual, SKIE interop, no business logic en UI layer. Eval: code review shared module. [HIGH]

### Anti-patterns 2026 + KPIs
| Anti-pattern | Por qué murió | KPI/SLO |
|---|---|---|
| Flutter para hardware BLE nativo | Plugin bridge latency, plugin abandonment | KMP + native UI; BLE p99 latency <50ms |
| React Native para B2B biometric | Bridge overhead, security audit failures, native module fragility | Native o KMP; 100% N4 data en native crypto |
| Testing solo emulador sin hardware real | BLE behavior diverge 40%+ en emulador | 80% test BLE en device físico; flakiness <2% |

---

## A12_QA_REL — QA / testing / chaos / reliability

### Estado del arte 2026
| Práctica | Líder | Tradeoff | Conf |
| Trophy / Pyramid | | Trophy más infra; Pyramid omite integración | [HIGH] |
| Contract testing | Pact/Schemathesis | 2 sem; elimina E2E | [HIGH] |
| Property-based | Hypothesis 50x; fast-check 10M | Curva alta; no reemplaza | [HIGH] |

### Stack SOTA top 3
| Herramienta | Uso | Tradeoff | Conf |
| Pact + PactFlow | Contract B2B | Java/JS maduro; Python menos | [HIGH] |
| Schemathesis | FastAPI OpenAPI | Auto; sin UI | [HIGH] |
| Grafana Faro + Synthetic | RUM Next.js/FastAPI | Self-hosted | [HIGH] |

### Bloque A — Roles SOTA
| Rol | Seniority | Conf |
| SRE / Reliability (Capability) | Senior+ | [HIGH] |
| Chaos Engineer (Capability) | Mid+ | [MEDIA] |
| SDET / QA Auto (Capability) | Mid | [MEDIA] |

### Bloque B — Competencias
1. **Contract testing**: PR contract+broker. [HIGH]
2. **Observability-driven**: SLI/RED en CR. [HIGH]
3. **Chaos design**: Game day, blast radius. [MEDIA]
4. **Property-based**: Invariantes PBT. [HIGH]

### Anti-patterns 2026 + KPIs
| Anti-pattern | Por qué murió | KPI reemplazo |
|---|---|---|
| 80% unit en glue code | Trophy: integración primero | Mutation >60%, integration >80% |
| E2E cross-service único | Flaky; contract reemplaza | Pact verification 100% |

---

# SÍNTESIS FINAL DEL SWARM

## S1 — TOP-10 ROLES INDISPENSABLES
1. **Software Architect** (A1, Staff/Principal, P0, [HIGH]) — Arquitectura dedicada evita deuda estructural a 60 eng.
2. **Privacy Engineer** (A9, IC3-4, P0, [HIGH]) — Codifica PbD, RLS, KMS, DP; DPO no escribe código.
3. **AppSec Architect** (A8, Staff/Principal, P0, [HIGH]) — SDLC, threat model, gates; sin él DevSecOps reactivo.
4. **Platform Engineer** (A2, Senior+, P0, [HIGH]) — IDP, golden paths, CI/CD; umbral ~50 eng, MWT 25→60.
5. **AI Agent Architect** (A3, Staff+, P1, [HIGH]) — Cognición, memoria, planning, HITL; no es backend común.
6. **Observability Engineer** (A7, Mid-Senior, P1, [HIGH]) — Plataforma OTel, SLOs-as-code; SRE consume, este construye.
7. **Embedded Architect** (A10, Staff, P1, [HIGH]) — MCUboot, BLE, OTA segura; sin él ScanFoot no pasa AC-02.
8. **AI Eval / Red Team** (A3, Senior, P1, [HIGH]) — Adversarial, golden corpus, safety agentes autónomos.
9. **Analytics Engineer** (A6, Mid-Senior, P1, [HIGH]) — dbt, diferenciado de Data Engineer; MWT tiene 0.
10. **Mobile Performance Specialist** (A11, Senior+, P2, [MEDIA]) — BLE throughput, battery, startup; hardware biometric.

## S2 — TOP-10 COMPETENCIAS TRANSVERSALES
1. **Contract-first design** [HIGH] — OpenAPI/AsyncAPI antes de código, lint CI, mocks, breaking-change detection. Eval: PR spec + implementación; review drift. Disc: Backend, Frontend, Mobile, QA.
2. **Multi-tenant RLS hardening** [HIGH] — SET LOCAL por tx, tenant_id en cache/DB/queue/JWT, test penetración cross-tenant. Eval: Lab leak tenant A→B. Disc: Backend, DB, Security, Platform.
3. **SLO engineering** [HIGH] — SLIs user journey real (no CPU), error budgets, burn-rate alerts. Eval: Propuesta SLO + error budget policy. Disc: Backend, SRE, Observability, QA.
4. **HITL + draft-first** [HIGH] — Output N3+ requiere aprobación humana logueada; nunca auto-write. Eval: Mock N4 con 3 gates. Disc: AI/ML, Backend, Frontend, Compliance.
5. **Threat modeling** [HIGH] — STRIDE/LINDDUN antes del código; controles por N0-N4. Eval: Entrevista caso multi-tenant + review diagrama. Disc: Security, Backend, AI/ML, Hardware.
6. **Observability-driven debugging** [HIGH] — Tracing + métricas + logs; tail-based sampling; correlación request-id. Eval: Debug cross-service simulado. Disc: Backend, Frontend, SRE, QA.
7. **Supply chain hardening** [HIGH] — SBOM + provenance + attestation SLSA; Sigstore/Cosign; admission control. Eval: Lab CI/CD Sigstore + Kyverno. Disc: Security, DevOps, Platform.
8. **Performance budgets** [HIGH] — LCP ≤2.5s, INP ≤200ms, CLS ≤0.1; CI gate Lighthouse. Eval: PR excede budget + propone fix. Disc: Frontend, Mobile, Backend.
9. **Property-based / contract testing** [HIGH] — Invariantes automáticas; Pact broker; Schemathesis contra OpenAPI. Eval: PR PBT + contract verification. Disc: QA, Backend, Frontend.
10. **DPA-as-code + privacy budget** [HIGH] — Whitelist versionado; trackear ε DP; alertas 90d. Eval: Repo central DPA chains versionados. Disc: Compliance, Backend, Legal.

## S3 — TOP-5 ANTI-PATTERNS 2026
1. **Microservices pre-30 devs sin platform** [HIGH] — Distributed monolith, 12 pipelines, 0 cross-tests, cognitive overload. Reemplazo: Modular monolith + DDD; cortar con platform ratio 1:8.
2. **Security team generalista** [HIGH] — DevSecOps reactivo, parches incoherentes, sin threat modeling. Reemplazo: AppSec Architect 1:4 ratio + Security Engineer ejecutor.
3. **Compliance técnica enterrada en legal** [HIGH] — Security controls no se implementan; DPO no habla SDLC. Reemplazo: Privacy Engineer + DPO separado; gates CI verificados.
4. **Auto-ejecución agentes sin draft-first** [HIGH] — Trust erosion, safety incidents, N4 biometric sin aprobación = liability. Reemplazo: 100% drafts N3+ antes write; interrupt_before LangGraph.
5. **Hardware team <5 FTE biométrico** [HIGH] — Imposible cubrir BLE+OTA+seguridad+PCB+test+manufactura. Reemplazo: 8-10 FTE antes AC-02; Embedded Architect Staff.

## S4 — TOP-5 INVERSIONES DE PLATAFORMA
1. **Platform Engineer + IDP (Port/Roadie)** [HIGH] — ROI: -40% time-to-first-service, +75% golden path adoption. Mes 1-2. Dep: Software Architect definido.
2. **Privacy Engineer + Drata auto-compliance** [HIGH] — ROI: SOC 2 Type I en 3-6 meses vs 12-18 manual; desbloquea enterprise sales. Mes 1-3. Dep: DPO redefinido.
3. **Observability Engineer + OTel + SLO-as-code** [HIGH] — ROI: -60% MTTR, alert fatigue → 3 SLO-based alerts/servicio. Mes 2-4. Dep: Grafana stack existe; upgrade a LGTM.
4. **LangGraph + MCP + AI Eval/Red Team** [HIGH] — ROI: HITL determinístico, 99.9% resume-after-interrupt, safety N4. Mes 3-6. Dep: AI Agent Architect a bordo.
5. **nRF Connect SDK + Memfault + secure boot** [HIGH] — ROI: OTA signed, fleet debug, CRA compliance; reduce 50% time-to-AC-02. Mes 4-8. Dep: Embedded Architect + 2× Firmware Engineer.

## S5 — META: GAPS DE INVENTARIO v1.0 DETECTADOS
1. **Falta arquitectura técnica** — SOTA: Software Architect Staff/Principal non-negotiable <60 eng; resto capabilities, no roles separados en 24m. Rec: 1 Software Architect Staff; demás capabilities por dominio.
2. **Falta Platform Engineering / IDP / DevEx** — SOTA: Platform team umbral ~50 eng; IDP SaaS (Port/Roadie) vence self-hosted <100 eng. Rec: 2 Platform Engineers Senior+, 1 Platform PM; IDP SaaS, no Backstage self-hosted.
3. **Falta specialty engineering** — SOTA: Observability Engineer rol separado de SRE en 2026; eBPF maduro; K8s no obligatorio Docker Compose. Rec: 1 Observability/Platform Engineer Mid-Senior; K8s pospuesto a E2 (>100 eng).
4. **Mobile no separa native vs cross-platform** — SOTA: KMP + native UI SOTA 2026 B2B hardware BLE; Flutter/RN overhead bridge y fragilidad plugins. Rec: iOS Native + Android Native + KMP shared logic; 3→5 FTE.
5. **Hardware sub-dimensionado (3 vs ~10 FTE)** — SOTA: 6 roles HW team clase mundial: Embedded Architect, 2× Firmware, RF/BLE, Security HW, HW/PCB, Manufacturing. CRA 2026 obliga reporting 24h. Rec: 3→8-10 FTE antes AC-02; 6 roles separados; priorizar Embedded Architect Staff.
6. **Security no separa AppSec/CloudSec/IR/Crypto/Privacy** — SOTA: AppSec Architect Staff + Security Engineer Sr+/Staff + Product Security Engineer separación clara; generalista = reactivo. Rec: 1 AppSec Architect, 2 Security Engineers; Privacy Engineer va en Compliance.
7. **Data sin Analytics Eng / Streaming / Lakehouse Architect** — SOTA: Analytics Engineer separado de Data Engineer SOTA 2026; lakehouse solo >1TB/día; pgvector OK <10M. Rec: 1 Analytics Engineer; Data Engineer mantiene CDC; sin Lakehouse Architect hasta E2.
8. **AI/ML sin MLOps / Prompt Eng / LLM Evaluator** — SOTA: AI Agent Architect Staff + AI Eval/Red Team Senior + LLM Ops Senior roles separados; Prompt Engineer capability mid. Rec: 1 AI Agent Architect, 1 AI Eval/Red Team, 1 LLM Ops; Prompt Engineer capability AI/ML.
9. **Compliance técnica enterrada en legal** — SOTA: Privacy Engineer (IC3-4) separado de DPO (legal/dir); codifica PbD, SDK, KMS, DP. Rec: 1 Privacy Engineer; DPO redefine scope regulatorio/legal puro; ratio DPO:PE 1:1.5.
10. **AI Safety no listado** — SOTA: HITL absoluto + draft-first + AI Eval/Red Team + interrupt_before = mínimo viable safety; sin AI Safety no se puede N4. Rec: AI Safety capability transversal obligatoria; crear AI Eval/Red Team role dedicado.

---

## PÁRRAFO DE CONFIANZA GLOBAL

**Confiabilidad:** 70% [HIGH] de docs canónicos (OTel spec, PostgreSQL, FastAPI, LangGraph, SLSA, CRA/RED, IEEE papers k-anon vs DP). 25% [MEDIA] consenso comunidad (Gartner, LinkedIn hiring 2025, Series C Port). 5% [BAJA] proyecciones emergentes (DPA on-chain, PQC LATAM, WebTransport 2026).

**Validación humana requerida:** (1) Vendor lock-in evaluar data residency LATAM por proveedor. (2) Presupuesto hardware (8-10 FTE) validar contra roadmap ScanFoot y unit economics. (3) LangGraph vs in-house HITL absoluto necesita PoC 2 semanas con interrupt_before real. (4) Cálculo ε DP pool colectivo requiere revisión estadístico; ε≤8 es heurística. (5) LATAM cloud residency verificar contratos vigentes AWS/GCP/Oracle Q2 2026.
