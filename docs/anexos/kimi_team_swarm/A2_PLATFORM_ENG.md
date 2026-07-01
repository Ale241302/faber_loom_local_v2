## A2_PLATFORM_ENG — Platform Engineering / IDP / DevEx

### Estado del arte 2026
| Práctica/framework | Trade-off | Confianza |
| DX Core 4 [^21^] | Lock-in DXI; holístico | [HIGH] |
| Golden paths [^48^] | Defaults opt-in | [HIGH] |
| Team Topologies TVP [^46^] | 1:6–9 stream-aligned | [HIGH] |

### Tendencias 2026–2028
| Tendencia | S/R | Razón | Confianza |
| Agentic AI IDP (Port) [^1^] | Señal | $100M Serie C | [MEDIA] |
| Self-hosted <100 eng | Ruido | Managed TCO bajo [^5^] | [HIGH] |
| DORA obsoleto | Ruido | Input en Core 4 [^23^] | [HIGH] |

### Stack/herramientas SOTA top 3
| Herramienta | Uso | Trade-off | LATAM-readiness | Confianza |
| Port | IDP SaaS agentic | Vendor lock-in [^1^] | Residencia regional | [HIGH] |
| Roadie | Managed Backstage | Menos custom [^5^] | Controlado | [HIGH] |
| DX (GetDX) | Medición Core 4 | DXI propietario [^22^] | Verificar | [MEDIA] |

### Bloque A — Roles SOTA
| Rol | Seniority | Scope | Tipo | Justificación | Confianza |
| Platform Engineer | Senior+ | Golden paths, IDP | Dedicado | Umbral ~50 eng [^50^] | [HIGH] |
| Platform PM | Senior | Roadmap, adoption | Dedicado | Product mindset [^45^] | [HIGH] |
| SRE/DevEx | Senior+ | Observabilidad | Capability | Part-time a 60 [^62^] | [MEDIA] |

### Bloque B — Competencias transversales
1. Platform-as-a-product: roadmap, adoption [^45^]; hire: productos medidos. [HIGH]
2. TVP: MVP iterativo [^46^]; hire: gradualidad. [HIGH]
3. Golden paths: templates opt-in [^48^]; hire: libertad con defaults. [HIGH]

### Anti-patterns 2026 + KPIs
| Anti-pattern | Por qué murió | KPI/SLO reemplazo |
| Backstage self-hosted <100 eng [^3^][^5^] | 3–12 FTE, $1M+ | Time-to-first-service <2 sem; adoption >75 |
| DORA sin DevEx [^23^] | Ignora coordinación | Core 4 + DXI quarterly [^21^] |
| Platform reactivo sin mandato [^50^] | 45.5% reactivos | % roadmap >70 [^62^] |
