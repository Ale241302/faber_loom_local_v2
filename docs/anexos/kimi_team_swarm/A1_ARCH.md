## A1_ARCH — Arquitectura de software moderna

### Estado del arte 2026
| Práctica | Resuelve | Trade-off | Confianza |
|---|---|---|---|
| Modular monolith + DDD | Single deploy, boundaries claros, path a microservices | Disciplina de interfaces internas | [HIGH] |
| Postgres RLS multi-tenant | Isolation row-level, costo bajo, operable | Bug en policy = breach total | [HIGH] |
| Contract-first OpenAPI | Fuente única, mocks, tests paralelos | Overhead de specs | [HIGH] |

### Tendencias 2026–2028
| Tendencia | Señal/ruido | Razón | Confianza |
|---|---|---|---|
| De-microservitización | Señal | FinOps + fatiga; monolith default <50 devs [^15^] | [HIGH] |
| EDA obligatorio para audit | Ruido | CDC + audit tables resuelven 90% pre-50 tenants [^65^] | [MEDIA] |
| AsyncAPI standard único | Ruido | OpenAPI gana sync; AsyncAPI complementa eventos [^44^] | [MEDIA] |
| ADRs como código | Señal | Lifecycle Proposed→Superseded, IA-aware [^30^] | [HIGH] |
| Context maps obsoletos | Ruido | Vigentes; complementados por Event Storming [^42^] | [HIGH] |

### Stack SOTA top 3
| Herramienta | Uso | Trade-off | LATAM-readiness | Confianza |
|---|---|---|---|---|
| OpenAPI 3.1 + Spectral | Contract-first REST | No cubre eventos | Alta (Git, CI free) | [HIGH] |
| PostgreSQL 16 + RLS | Tenant isolation | Requiere pgbouncer + session vars | Alta (doc amplia) | [HIGH] |
| Strangler Fig + Flags | Extracción a microservices | Dual-write temporal | Media (experiencia escasa) | [MEDIA] |

### Bloque A — Roles SOTA
| Rol | Seniority | Scope | Tipo | Justificación | Confianza |
|---|---|---|---|---|---|
| Software Architect | Staff/Principal | DDD, ADRs, stack | Separado | Sin arquitectura dedicada = deuda estructural [^12^] | [HIGH] |
| Platform Engineer | Senior+ | IDP, CI/CD, RLS | Capability 1:8 [^36^] | Reduce cognitive load de stream teams | [HIGH] |
| API/Product Engineer | Mid-Senior | Contract-first, DX | Capability por squad | API-first orgs generan +43% revenue [^43^] | [MEDIA] |

### Bloque B — Competencias transversales
1. **DDD táctico** — Aggregates, VO, Repositories. Eval: bounded context en entrevista. [HIGH]
2. **Contract-first** — Spec antes de código, lint CI, mocks. Eval: PR con breaking-change detection. [HIGH]
3. **Observabilidad** — Tracing + métricas + logs. Eval: debug incidente cross-service simulado. [MEDIA]
4. **Data residency** — RLS, tenant_id en cache/DB/queue, JWT claims. Eval: audit cross-tenant leak. [HIGH]

### Anti-patterns 2026 + KPIs
| Anti-pattern | Por qué murió | KPI/SLO de reemplazo |
|---|---|---|
| Microservices pre-30 devs sin platform | Distributed monolith, 12 pipelines, 0 cross-tests [^12^] | Ratio 1:8; deploy >1/día sin conflict |
| EDA full + event sourcing para MVP | Eventual consistency > valor [^66^] | Audit 100% sync CDC; <5% async |
| Code-first API autogenerada | Drift spec/impl [^31^] | 100% APIs con OpenAPI en repo pre-merge |
| Context map estático desconectado | Se desincroniza del código | ADR-XXX + diagrama en repo; review semestral |
