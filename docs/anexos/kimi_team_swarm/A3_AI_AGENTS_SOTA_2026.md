## A3_AI_AGENTS — Multi-agent / agentic frameworks SOTA

### Estado del arte 2026
| Framework | Cuándo usar | Trade-off | Conf |
|---|---|---|---|
| LangGraph v1.0.10 | Stateful, HITL (`interrupt_before`), audit | Steep curve, LangChain-coupled | [HIGH] |
| CrewAI v1.10.1 | Proto role-based multi-agent | Menor control, +48% tokens | [HIGH] |
| Pydantic AI | Single-agent type-safe FastAPI | Sin HITL nativo; ideal E1 | [HIGH] |

### Tendencias 2026–2028
| Tendencia | Señal/Ruido | Razón | Conf |
|---|---|---|---|
| MCP infraestructura | Señal | 78% enterprise, 9,400+ servers, Linux Foundation | [HIGH] |
| A2A orquestación | Señal | 42% CTOs planean MCP+A2A | [MEDIA] |
| Claude SDK reemplaza terceros | Ruido | v0.1.48 alpha, Claude-only, lighter orchestration | [HIGH] |

### Stack SOTA top 3
| Herramienta | Uso | Trade-off | Conf |
|---|---|---|---|
| LangGraph + LiteLLM | Orquestación HITL, model-agnostic | Curva 1-2 semanas | [HIGH] |
| MCP servers | Tool wiring universal | Latencia remote +130ms | [HIGH] |
| Langfuse + DeepEval | Tracing + 50+ métricas pytest-native | DeepEval OSS | [HIGH] |

### Bloque A — Roles SOTA
| Rol | Seniority | Scope | Tipo | Conf |
|---|---|---|---|---|
| AI Agent Architect | Staff+ | Cognición, memoria, planning | Separado | [HIGH] |
| AI Eval / Red Team | Senior | Métricas, adversarial, golden | Separado | [HIGH] |
| Prompt Engineer | Mid | Versionado, guardrails | Capability | [MEDIA] |
| LLM Ops Engineer | Senior | Deploy, monitor, checkpointing | Separado | [HIGH] |

### Bloque B — Competencias transversales
1. **State Management**: Checkpointing, recovery, time-travel. Eval: grafo HITL. [HIGH]
2. **Tool Governance**: MCP lifecycle, OAuth 2.1. Eval: audit shadow IT. [HIGH]
3. **HITL UX**: Draft-first, approval queues. Eval: mock N4 con 3 gates. [HIGH]

### Anti-patterns 2026 + KPIs
| Anti-pattern | Por qué murió | KPI/SLO |
|---|---|---|
| CrewAI producción regulated | Sin checkpointing determinístico | LangGraph; 99.9% resume-after-interrupt |
| Auto-ejecución sin draft-first | Trust erosion, safety incidents | 100% drafts N3+ antes write |
