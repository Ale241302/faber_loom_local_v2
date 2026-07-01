## Compliance LATAM 2026 / privacy engineering

### Estado del arte 2026
| Práctica | Trade-off | Conf |
| PE ≠ DPO | PE codifica; DPO gobierna | [HIGH] |
| DP ε=1-10 > k-anon | Garantía matemática; k-anon cae | [HIGH] |
| Compliance auto | Drata mid-market; Vanta startup; Thoropass bundled | [MEDIA] |

### Tendencias 2026–2028
| Tendencia | S/R | Razón | Conf |
| AI agents compliance | Señal | SOC 2 Type I en días | [MEDIA] |
| EU residency default | Señal | NIS2/DORA; LATAM sigue | [HIGH] |
| DPA on-chain | Ruido | Sin enforcement | [BAJA] |

### Stack SOTA top 3
| Herramienta | Uso | Trade-off | Conf |
| Drata | SOC 2/ISO evidence | No EU res; AWS/GCP OK [^140^] | [HIGH] |
| OneTrust VRM | DPA chain + VRM | Overkill <50 [^201^] | [MEDIA] |
| OpenDP | DP-SGD ML/analytics | Requiere experto [^192^] | [HIGH] |

### Bloque A — Roles SOTA
| Rol | Seniority | Scope | Sep/Cap | Justificación | Conf |
| Privacy Engineer | IC3-4 | PbD, SDK, KMS | Separado | Codifica [^166^] | [HIGH] |
| DPO | Dir | DPIA, regulator | Separado | Externo | [HIGH] |
| Privacy Architect | Staff+ | Standards | Capability | Patterns | [MEDIA] |

### Bloque B — Competencias transversales
1. DPA-as-code: whitelist versionado; PR legal+eng [^201^] [HIGH]
2. Privacy budget: trackea ε; MI tests [^192^] [HIGH]
3. Residency: BR São Paulo AWS/Oracle; MX Querétaro AWS/GCP; CO Bogotá AWS/Oracle; AR/CR local o BR/MX [^169^][^174^] [HIGH]
4. HITL N4: biométrico aprobación logueada [HIGH]

### Anti-patterns 2026 + KPIs
| Anti-pattern | Por qué murió | KPI reemplazo |
| Legal hace técnico | No operan | DPO:PE 1:1.5; pass >95% |
| k-anon única defensa | Re-id | DP ε≤8; synthetic N3-N4 [^173^] |
| SOC 2 Type II tardío | Bloquea | Type I seed; Type II Series A [^170^] |
| DPA manual | No escala | Repo central; alert 90d [^201^] |
