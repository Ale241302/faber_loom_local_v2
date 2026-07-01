## A8_SECURITY — Security / supply chain / DevSecOps

### Estado del arte 2026
| Práctica | Estado | Trade-off | Confianza |
|----------|--------|-----------|-----------|
| Zero Trust para B2B SaaS | Table stakes enterprise [^113^] | Coste IAM/ABAC; sin él, friction en security review | [MEDIA] |
| SLSA L3-L4 supply chain | Enterprise exige L3; L4 para crítico [^109^][^110^] | Overhead CI hermético; evita inyección en build | [HIGH] |
| PQC híbrido (ML-KEM+ECDH) | Migración activa 2026-2028 [^115^][^122^] | Latencia + complejidad; HNDL obliga a empezar ya | [MEDIA] |

### Tendencias 2026–2028 (señal vs ruido)
| Tendencia | Señal/Ruido | Razón | Confianza |
|-----------|-------------|-------|-----------|
| Agentic AI pentesting (Penligent) | Señal | Reemplaza red team manual en orgs <100 eng [^112^] | [MEDIA] |
| SBOMs "vivos" con VEX | Señal | Paper SBOMs inútiles; contextual analysis reduce alert fatigue [^111^] | [HIGH] |
| PQC compliance obligatorio LATAM | Ruido (aún) | NIST/CNSA 2.0 fija 2027-2033 para NSS; LATAM sigue voluntary [^122^] | [BAJA] |

### Stack/herramientas SOTA top 3
| Herramienta | Uso | Trade-off | LATAM-readiness | Confianza |
|-------------|-----|-----------|-----------------|-----------|
| Sigstore (Cosign+Rekor+Fulcio) | Firma SBOM/provenance, verificación en registry | Dependencia de infraestructura pública; puede usar private | GitHub/GitLab nativo, operable en CR | [HIGH] |
| Kyverno/OPA Gatekeeper | Admission control: bloquea imagen sin attestation SLSA | Curva de política-as-code; necesita K8s | Cloud-native, disponible en AWS/Azure/GCP LATAM | [HIGH] |
| PTaaS agentic (Cobalt/Penligent) | Pentest continuo + compliance audit anual | Cobertura no es red team físico interno; ideal para <100 eng | Remoto, sin frontera [^112^] | [MEDIA] |

### Bloque A — Roles SOTA
| Rol | Seniority | Scope | Separado o capability | Justificación | Confianza |
|-----|-----------|-------|----------------------|---------------|-----------|
| AppSec Architect | Staff/Principal | Diseño SDLC, threat model, gates, política SAST/DAST/SCA | Separado | Strategic vs tactical; sin arquitecto, engineers implementan parches incoherentes [^117^] | [HIGH] |
| Security Engineer | Sr+/Staff | Opera pipelines, tuning, IR, cloud hardening | Separado | Ejecuta lo que arquitecto diseña; mixto genera deuda técnica [^117^][^118^] | [HIGH] |
| Product Security Engineer | Staff | Seguridad de producto multi-tenant, RBAC/ABAC, cripto | Capability dentro de AppSec | B2B SaaS requiere especialización tenant-isolation; no es genérico | [MEDIA] |

### Bloque B — Competencias transversales
1. **Threat modeling (STRIDE/LINDDUN)** — diseñar controles antes del código — evaluación: entrevista con caso multi-tenant + review de diagrama propio [HIGH]
2. **Supply chain hardening (SLSA/SBOM)** — generar provenance y verificar en admission — evaluación: lab CI/CD con Sigstore + Kyverno [HIGH]
3. **HITL + privacy-by-design (N0-N4)** — clasificación de datos y controles técnicos por nivel — evaluación: analizar un flujo de datos BIOMETRIC (ScanFoot) y proponer arquitectura [HIGH]
4. **Zero Trust IAM** — least privilege, SSO/SAML/OIDC, session revocation — evaluación: audit de config RBAC en app real [MEDIA]

### Anti-patterns 2026 + KPIs
| Anti-pattern | Por qué dejó de ser SOTA | KPI/SLO de reemplazo |
|--------------|--------------------------|----------------------|
| Security team generalista sin separación AppSec/CloudSec/IR | DevSecOps falla sin diseño estratégico; se vuelve reactivo [^117^] | Ratio AppSec Architect : Engineer 1:4; MTTR IR <4h |
| Compliance técnica enterrada en legal | Security controls no se implementan si legal no habla SDLC | 100% de gates SLSA verificados por CI; 0 excepciones manuales |
| Pentest anual puntual como única validación | Attack surface cambia en días; agentic AI explica la ventana de exposición | Cobertura continua PTaaS: 100% de releases con attestation + DAST |
