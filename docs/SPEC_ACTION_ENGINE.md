# SPEC_ACTION_ENGINE — Motor de Acción Medular MWT/FaberLoom
id: SPEC_ACTION_ENGINE
version: 1.3
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
type: SPEC
stamp: VIGENTE -- 2026-05-07
aprobador: CEO (delegado al Arquitecto Cowork -- sesion 2026-04-28)
aplica_a: [MWT, FaberLoom]
relacionado: SPEC_LLM_ROUTING_ARCHITECTURE.md (subcomponente) · SPEC_AUTONOMY_CONTROL_ENGINE.md (RequestOutcomeEntry feed) · SPEC_AUDIT_MODULE.md (consumido por D10) · ARCH_AGENT_PRINCIPLES.md (P3, P4, P9, P13, P14) · docs/faberloom/ENT_FB_INSIGHTS_KIMI_RUFLO_v1.md (I-RUFLO-01..09) · docs/faberloom/ENT_FB_PRICING_TIERS_v1.md · ENT_PLAT_ACTION_REGISTRY.md · SCH_ACTION_SPEC.yaml · POL_DATA_CLASSIFICATION.md · SPEC_PROMPT_CACHE_DISCIPLINE.md (D11)

---

## Declaración

El Action Engine es el módulo medular que abstrae todas las acciones del sistema (LLMs, APIs externas, tools locales, MCPs, KB access) bajo un contrato API estable, con observabilidad unificada y aplicación centralizada de policies.

**Es medular, no add-on.** Cada skill, cada agente IA, cada flujo de FaberLoom multi-tenant consume el Action Engine. Las decisiones de diseño que cementa este documento se respetan por contrato — cambiarlas después es breaking change major.

**Estrategia de implementación: contract-first, implementación incremental.** El contrato API se define hoy y permanece estable. La implementación crece detrás del contrato sin romper consumers.

---

## Por qué este documento existe

Tres problemas operativos que la arquitectura actual no resuelve:

1. **Routing distribuido en código por skill.** Cada agente decide qué LLM/API llamar con lógica hardcoded. No escala a 50+ acciones disponibles.
2. **Sin telemetría unificada.** OutcomeLedger captura per-request pero cada skill loguea distinto. No hay datos consistentes para optimizar.
3. **Multi-tenant FaberLoom requiere policy per-org centralizada.** Hoy cada PYME hereda config global sin overrides controlados.

El Action Engine resuelve los tres con una capa de abstracción que aplica los principios fundacionales (P3 Draft-first, P4 Niveles autonomía, P9 Gobernanza embebida, P13 Contención, P14 Deterministic First) de forma ejecutable, no solo declarativa.

---

## Las 11 decisiones de diseño cementadas

Cambiar cualquiera de estas requiere bump major version + 2 versiones de coexistencia + aprobación CEO explícita.

### D1 — Async-first

Todas las acciones del Engine son `async/await`. LLM calls, API externas, tool invocations devuelven coroutines. Wrapper sync disponible solo como adapter para código legacy (`action_engine.execute_sync(...)`).

**Razón:** LLMs y APIs son async natural. Forzar sync genera bottlenecks en fan-out (MoAT).

### D2 — Bypass mode obligatorio

Cada consumer puede invocar `action_engine.bypass(target_action_id, **kwargs)` para saltar policy y llamar directo a la implementación subyacente.

**Razón:** Sin bypass, debugging post-mortem es imposible. Emergencias requieren acceso directo. Bypass obligatorio = fragilidad ante el componente medular más crítico controlada.

**Restricción:** uso de bypass se loguea con flag `bypassed=true` y razón obligatoria. Auditoría posterior detecta abuso.

### D3 — Schema enforcement estricto desde v1

Cada `ActionSpec` registrado declara su `input_schema` y `output_schema` con Pydantic v2. Validación obligatoria en cada call. No hay "modo flexible" en v1.

**Razón:** Bugs distribuidos en sistema medular cuestan 10× más debuggar después que prevenir antes. Costo upfront aceptable.

### D4 — Versionado semver con deprecation cycle 2 versiones

Contract API sigue semver estricto:
- `MAJOR`: breaking change (cambia firma pública)
- `MINOR`: nuevas features compatibles
- `PATCH`: bug fixes

Cuando una feature se deprecia, debe coexistir con su reemplazo durante 2 versiones major antes de removerse.

**Razón:** Estándar industria. Predecibilidad para consumers.

### D5 — Multi-tenant first-class desde v1

Toda invocación lleva `org_context` (puede ser None para uso interno MWT). RLS aplicado a nivel Engine vía `tenant_id`, no per-skill. Routing Policy soporta overlay per-org desde día 1.

**Razón:** Retrofit de multi-tenant en sistema medular = catastrófico. FaberLoom lo necesita; MWT lo absorbe trivialmente con `org_context=None`.

### D6 — Observability JSON estructurada + OpenTelemetry-compatible

Cada call genera trace estructurado con campos: `trace_id`, `parent_id`, `action_id`, `org_context`, `latency_ms`, `cost_usd`, `bypassed`, `outcome`, `error`. Compatible con OpenTelemetry para integración futura con Langfuse/Datadog.

**Razón:** Observabilidad es la única forma de cerrar el loop con Adaptive Tuner. Cambiar formato post-hoc invalida histórico.

### D7 — Library, no Service

Action Engine se distribuye como **Python package interno** (`mwt_action_engine`). Cada consumer instancia su propio Engine. No hay servicio HTTP/gRPC central.

**Razón:** Service = SPOF medular = riesgo inaceptable. Library = falla per-call, no per-system. Performance overhead minimizado (sin network).

### D8 — Circuit breaker + fallback to direct call

Cuando una acción falla N veces consecutivas (umbral configurable, default 3), el circuit breaker se abre y el Engine retorna `EngineFailure` que el consumer puede manejar con fallback a llamada directa o degradación graciosa.

**Razón:** Sistema medular no debe parar el sistema cuando él falla. Resiliencia obligatoria.

### D9 — Data Classification Routing

Cada `ActionContext` lleva `data_classification` (N0-N4 según POL_DATA_CLASSIFICATION) y `anonymization_level` (L0-L3). El Engine rutea aplicando:

```
- N0 PUBLIC      → cualquier modelo, anonim L0 default
- N1 INTERNAL    → modelos con DPA, anonim L1 default
- N2 CONFIDENTIAL→ US/EU + DPA obligatorio, anonim L2, cost-mode OFF
- N3 DISTRIB-SCOPED→ US/EU + DPA + RLS, anonim L2, cost-mode opt-in tenant
- N4 BIOMETRIC   → US/EU exclusivo, anonim L3 obligatoria, audit completo
```

**Hard block enforcement:** si `data_classification > tenant_plan_ceiling`, el Engine retorna `PlanUpgradeRequired` antes de ejecutar. La policy se aplica en el Engine, no en cada skill — multi-tenant safe por construcción.

**Cost-mode opt-in:** tenants pueden habilitar `cost_mode_enabled: true` que permite providers no-DPA (DeepSeek, Kimi self-host) **solo para data N0/N1**. Default OFF.

**Conversation ceiling:** la sesión puede setear `conversation_ceiling` que limita el max class accesible. Si chunk recuperado supera ceiling, Engine retorna `CeilingExceeded` para que UI ofrezca elevación con audit.

**Razón:** Sin enforcement centralizado, cada skill duplicaría lógica de classification — frágil, inconsistente, no auditable. D9 cumple LGPD, Ley 1581 CO, Ley 25.326 AR como guardrail técnico.

### D10 — Audit Module Inmutable

Cada call genera `AuditEntry` inmutable con hash chain (cada entry hashea la anterior). Storage separado del operativo, retención configurable per-tenant (default 7 años Enterprise, 10+ Government).

```
AuditEntry incluye:
  - decision_provenance (input_hash, output_hash, action_chain, ceiling, anonim)
  - policy_version_pinned (snapshot de policies vigentes en ese momento)
  - hash_chain_link (sha256 de la entry anterior)
  - timestamp + signature
```

**Replay capability:** dado `audit_id`, el Engine puede reproducir la decisión que tomó (qué chunks, qué policy version, qué routing). Esto permite que auditor verifique cumplimiento contra policy del momento, no la actual.

**Auditor read-only API:** endpoint separado de operación con MFA + audit-of-audit (cada acceso del auditor también se loguea). Filtros por tenant/user/fecha/action_id/policy_version.

**Compliance attestation reports:** generación periódica firmada digitalmente. Templates por estándar (ISO 27001, SOC 2, gobierno LATAM).

**Tamper detection:** validación de hash chain periódica + alerta crítica si detecta edición/eliminación. Inmutabilidad enforced a nivel storage (S3 Object Lock, Azure Immutable Blob, equivalent).

**Razón:** Convierte FaberLoom en producto vendible a sectores regulados (gobierno, banca, salud, educación, telecom). Sin D10 cementado en contract, no se puede ofrecer Enterprise/Government tier sin breaking change major posterior.

Implementación efectiva: Fase 4-5 del roadmap (post-MVP). Pero el contract API contempla `audit_id` desde v1.0 para evitar retrofit. Ver `SPEC_AUDIT_MODULE.md`.

### D11 -- Prompt Cache Discipline

Toda invocacion del Engine que use system prompt construido desde archivos Always-loaded de la KB respeta SPEC_PROMPT_CACHE_DISCIPLINE v1.0 (R1-R4):

- Volatiles al final del archivo, nunca al inicio
- `cache_control: {type: "ephemeral"}` en bloque system prompt
- Orden canonico de bloques (R3) versionado en SPEC_PROMPT_CACHE_DISCIPLINE
- TTL 5min default, 1h justificado solo en sprint LOTE activo

ActionResult expone metrica `cache_hit_ratio` per call (D6 observability).

**Razon:** ahorro proyectado $5,600/ano solo en input prefix caching, latencia TTFT -30%. Sin enforcement centralizado via Engine, cada consumer duplicaria disciplina y volatiles escondidos romperian cache silenciosamente.

**Excepcion documentada:** providers sin prompt caching nativo (DeepSeek self-host, Ollama local) operan sin D11 -- Engine retorna `cache_hit_ratio: null` para esas acciones.

---

## Contract API v1.0

```python
from typing import Optional, Any, AsyncIterator
from pydantic import BaseModel

class ActionContext(BaseModel):
    org_id: Optional[str] = None       # FaberLoom multi-tenant; None para MWT interno
    user_id: Optional[str] = None
    trace_id: str                       # auto-generado si no se provee
    parent_trace_id: Optional[str] = None
    deadline_ms: Optional[int] = None   # timeout suave
    bypass_policy: bool = False         # solo para uso D2
    # D9 — Data Classification (v1.2)
    data_classification: Literal["N0","N1","N2","N3","N4"] = "N1"   # default safe
    anonymization_level: Literal["L0","L1","L2","L3"] = "L1"
    conversation_ceiling: Optional[Literal["N0","N1","N2","N3","N4"]] = None  # opcional sesión
    tenant_plan: Literal["starter","pro","enterprise","government"] = "starter"
    addons_enabled: list[str] = []     # ej. ["confidencial_addon", "audit_addon"]

class ActionResult(BaseModel):
    success: bool
    output: Any                         # validado contra output_schema del ActionSpec
    latency_ms: int
    cost_usd: float
    action_used: str                    # ID de la acción que se ejecutó
    bypassed: bool = False
    fact_attribution: dict              # qué modelo/API generó qué dato
    confidence: float                   # 0-1, de la propia acción
    error: Optional[str] = None
    # D10 — Audit (v1.2)
    audit_id: Optional[str] = None     # ref a AuditEntry para replay
    policy_version_applied: str = "1.0"  # snapshot de policy vigente
    classification_enforced: Optional[str] = None  # qué nivel se aplicó

# D9/D10 — Excepciones tipadas (v1.2)
class PlanUpgradeRequired(Exception):
    """data_classification supera ceiling del tenant_plan actual"""
    suggested_addon: str

class CeilingExceeded(Exception):
    """chunk recuperado supera conversation_ceiling — UI debe ofrecer elevación"""
    actual_class: str
    current_ceiling: str

class ActionEngine:
    """Library, no service. Cada consumer instancia su propio Engine."""

    def __init__(
        self,
        registry: ActionRegistry,
        policy: RoutingPolicy,
        ledger: OutcomeLedger,
        org_context: Optional[OrgContext] = None,
    ): ...

    async def execute(
        self,
        intent: str,                    # qué quiere lograr (ej. "classify_invoice")
        payload: dict,                  # input data
        context: ActionContext,
    ) -> ActionResult: ...

    async def bypass(
        self,
        action_id: str,                 # qué acción específica ejecutar (D2)
        payload: dict,
        context: ActionContext,
        reason: str,                    # obligatorio para auditoría
    ) -> ActionResult: ...

    async def stream(
        self,
        intent: str,
        payload: dict,
        context: ActionContext,
    ) -> AsyncIterator[ActionEvent]: ...  # streaming response

    def execute_sync(
        self,
        intent: str,
        payload: dict,
        context: ActionContext,
    ) -> ActionResult: ...              # adapter sync para legacy
```

---

## Tres escenarios de uso (cubren 90% de casos)

### Escenario 1 — LLM call (research interno MWT)

```python
result = await engine.execute(
    intent="research_brief_synthesis",
    payload={"brief": "...", "tier": "MEDIUM"},
    context=ActionContext(trace_id=uuid4()),
)
# Engine resuelve: tier=MEDIUM → fan-out a 3 modelos baratos + integrador
# Retorna síntesis ejecutiva con fact_attribution
```

### Escenario 2 — API externa (FaberLoom cobranza)

```python
result = await engine.execute(
    intent="parse_electronic_invoice",
    payload={"document": xml_bytes, "country_hint": "CO"},
    context=ActionContext(org_id="acme_corp_co", trace_id=uuid4()),
)
# Engine resuelve: Tier 0 deterministic primero (P14)
#   → si confidence < threshold, escala a Haiku 4.5
#   → si Haiku confidence < threshold, escala a Human Gate
# RLS aplicado por org_id
```

### Escenario 3 — Tool local con bypass (debugging)

```python
result = await engine.bypass(
    action_id="local.regex_extract_amount",
    payload={"text": "Total: $1,234.56"},
    context=ActionContext(trace_id=uuid4()),
    reason="debugging Tier 0 regression sprint 12",
)
# Bypass salta policy, ejecuta directo. Log con bypassed=true.
```

---

## Subsistemas aplicados (cómo encajan otros patrones)

### MoAT (Mixture of Agents Tiered) como Routing Policy

El MoAT (LIGHT/MEDIUM/EXTREME) es la Routing Policy default para `intent` de tipo research. No es un sistema separado — es configuración del Engine.

```yaml
# routing_policy.yaml fragmento
intent_routing:
  research_*:
    LIGHT:
      action_chain: [single_shot_haiku_45]
    MEDIUM:
      action_chain:
        - fanout: [deepseek_v4_flash, gemini_25_flash, gpt_55_mini]
        - integrator: claude_sonnet_46
    EXTREME:
      action_chain:
        - decompose: claude_sonnet_46
        - fanout: [kimi_k2_6_swarm, deepseek_v4_pro, gemini_3_pro]
        - cross_verify: kimi_k2_6_swarm
        - synthesize: claude_opus_47
```

### Carpintería/Calidad como tagging de ActionSpec

Cada `ActionSpec` declara `tier_hint: "carpenteria" | "calidad"`. La Routing Policy puede priorizar carpintería en modelos baratos y calidad en premium.

### P14 Deterministic First → action_chain ordering

El orden por default en cualquier `action_chain` de la Routing Policy es:
1. Acciones determinísticas (regex, parsers, lookups)
2. Acciones LLM
3. Acciones con Human Gate

Esto es la encarnación ejecutable de P14.

### P3 Draft-first → side_effects gating

`ActionSpec.side_effects` puede ser `none | reversible | irreversible`. Cualquier acción con `side_effects: irreversible` (envío email externo, transferencia, etc.) requiere aprobación humana antes de ejecutar.

### P13 Contención → multi-tenant Engine

Cada `org_context` instancia un Engine con su propia `RoutingPolicy` overlay y RLS aplicado. Memoria entre orgs no se transfiere.

### ModelFingerprint → Capability Map drift detection

Cuando un modelo cambia (ej. Haiku 4.5 → Haiku 5.0), el Capability Map detecta cosine similarity con histórico. Si <0.2, la capability se marca como `cold_start` y la Routing Policy degrada confidence hasta revalidación.

---

## Failure modes y resiliencia

| Modo de falla | Comportamiento del Engine | Acción del consumer |
|---|---|---|
| Acción específica falla | Circuit breaker incrementa contador | Continuar con fallback chain |
| Circuit breaker abierto (N fallos) | Retorna `EngineFailure(reason="breaker_open")` | Decidir entre llamada directa o degradación |
| Engine completamente caído | Excepción `EngineUnavailable` | Bypass mode + logging para audit |
| Schema validation falla en input | `ValidationError` antes de ejecutar | Consumer debe corregir payload |
| Schema validation falla en output | Acción se marca `success=False, error=...` | Consumer recibe error tipado |
| Timeout `deadline_ms` excedido | Acción cancelada, `error="deadline_exceeded"` | Reintentar con timeout mayor o fallback |
| Rate limit del provider externo | Engine espera + retry exponencial hasta 3× | Si persiste, marca `error="rate_limited"` |
| Cost budget por org excedido | Retorna `error="budget_exceeded"` | Consumer escala a CEO o degrada |

**Garantía core:** el Action Engine NUNCA bloquea al consumer indefinidamente. Toda llamada termina en éxito, error tipado, o timeout configurable.

---

## Observability schema (D6)

Cada `ActionResult` genera un trace con esta estructura:

```json
{
  "trace_id": "uuid",
  "parent_trace_id": "uuid|null",
  "intent": "research_brief_synthesis",
  "action_used": "claude_opus_47",
  "action_chain": ["sonnet_46", "kimi_k2_6_swarm", "claude_opus_47"],
  "org_context": "acme_corp_co|null",
  "user_context": "uuid|null",
  "input_hash": "sha256",
  "output_hash": "sha256",
  "latency_ms": 12450,
  "cost_usd": 0.0341,
  "bypassed": false,
  "outcome": "success|error|timeout|rate_limited|budget_exceeded",
  "error_detail": "...|null",
  "fact_attribution": {
    "fact_1": "kimi_k2_6_swarm",
    "fact_2": "claude_opus_47"
  },
  "confidence": 0.85,
  "policy_version": "1.0",
  "engine_version": "1.0.0",
  "timestamp": "2026-04-28T14:30:00Z"
}
```

Compatible con OpenTelemetry semantic conventions. Exportable a Langfuse, Datadog, o cualquier observability backend.

---

## Roadmap de implementación

### Semana 1-2 — Diseño cerrado (este documento + dependencias)

- ✅ SPEC_ACTION_ENGINE.md v1.0 (este doc)
- ✅ SCH_ACTION_SPEC.yaml
- ✅ ENT_PLAT_ACTION_REGISTRY.md (catálogo inicial vacío)
- Spike de 1 día por consumer principal (AG-01, AG-02, AG-06, AG-07, FaberLoom MVP) — validar que Contract API sirve

### Semana 3 — Implementación trivial ("passthrough mode")

- `mwt_action_engine` package Python con Contract API completa
- Implementación: cada `execute()` llama directo a la API subyacente (no routing inteligente)
- Logging completo a OutcomeLedger desde día 1
- FaberLoom MVP arranca aquí — usa Action Engine desde día 1

### Semana 4-9 — Implementación real crece detrás del contrato

- Registry y Capability Map se llenan progresivamente
- Routing rule-based reemplaza passthrough (intent-based)
- Circuit breaker + retry + observability completa
- MWT skills migran 1 por semana a usar el Engine

### Semana 10+ — Features avanzados (post-MVP FaberLoom)

- Routing Policy declarativa en YAML
- Adaptive Tuner consume OutcomeLedger
- Capability drift detection con ModelFingerprint
- Per-org overrides FaberLoom

---

## Triggers de aborto / pivot

Si alguna de estas condiciones se cumple, escalar a CEO antes de continuar:

| Trigger | Acción correctiva |
|---|---|
| Sem 2: Contract API no convence a 2+ consumers en spike | Volver a sem 1, redefinir |
| Sem 3: Implementación trivial >5 días | Algo del contrato está mal definido |
| Sem 6: FaberLoom MVP bloqueado por gap del Engine | Relajar disciplina contrato congelado, abrir v1.1 |
| Sem 9: Action Engine sin Capability Map útil | Revisar prioridades del backlog |
| Performance overhead >10ms p99 | Stop ship hasta resolver. <5ms es target, >10ms es regresión inaceptable |

---

## Lo que el Action Engine NO es

- **No es un framework de agentes.** AgentSpec / AgentRuntime / AgentMemory siguen siendo la abstracción de agente (P1). El Engine es el plano de control de **acciones**, no de agentes.
- **No es un service mesh.** Es library, no servicio (D7).
- **No es un reemplazo de LiteLLM.** LiteLLM se vuelve adapter dentro del Execution Layer del Engine.
- **No es opcional.** Una vez en producción, todas las acciones pasan por el Engine. Bypass es para emergencias auditables, no uso normal.
- **No reemplaza orquestación humana.** PLB_ORCHESTRATOR (FROZEN) define orquestación humana CEO-driven. El Engine es la pieza técnica que la complementa.

---

## Limitaciones conocidas v1.0

| Limitación | Mitigación |
|---|---|
| Cold start del Adaptive Tuner (sem 10+) | Rule-based routing cubre primeros 6 meses, ModelFingerprint maneja drift |
| Capability Map se llena manualmente | Acceptable en v1, automatización via introspection en v2 |
| No soporta workflows multi-step nativos en v1 | Consumers componen vía múltiples `execute()` calls. Workflow engine es candidato a v2 |
| Per-org policy overlay es manual | OK para FaberLoom MVP (10-50 PYMEs), automatización en v2 con dashboard |
| Schema migration entre versiones es manual | Documentado por release notes, automatización es v2 |

---

## Anexo — Mapeo a archivos existentes en KB

| Archivo MWT actual | Cambio post Action Engine |
|---|---|
| `SPEC_LLM_ROUTING_ARCHITECTURE` v1.1 | Pasa a v1.2 — marcado como **subcomponente** del Action Engine. L1/L2/L3 sigue válido pero ejecuta dentro del Engine |
| `SPEC_AUTONOMY_CONTROL_ENGINE` v1.2 | RequestOutcomeEntry alimenta directamente el OutcomeLedger del Engine. Sin cambio de schema |
| `ARCH_AGENT_PRINCIPLES` v1.3 | Sin cambio — los principios siguen igual, ahora se aplican vía Engine |
| `PLB_ORCHESTRATOR` (FROZEN) | Sin cambio — orquestación humana coexiste con Engine técnico |
| `SCH_SKILL.md` | v2 (futuro) puede declarar dependencies del Action Engine en AgentSpec |
| `DEPENDENCY_GRAPH.md` | Action Engine como nodo central, dependencias hacia él desde skills |
| LiteLLM en stack | Adapter dentro del Execution Layer del Engine |

---

Changelog:
- v1.3 (2026-05-07): +D11 Prompt Cache Discipline. Origen: DEC-009 + SPEC_PROMPT_CACHE_DISCIPLINE v1.0 (HANDOFF 28-abr actualizado post Sprint 0). Sin breaking change -- D11 es disciplina, no cambio de contrato.
- v1.2 (2026-04-28): +D9 Data Classification Routing + D10 Audit Module Inmutable. ActionContext extendido con data_classification/anonymization_level/conversation_ceiling/tenant_plan/addons_enabled. ActionResult extendido con audit_id/policy_version_applied/classification_enforced. Excepciones tipadas: PlanUpgradeRequired, CeilingExceeded. Origen: discusión perfil PYME + competencia Claude.ai/ChatGPT + tiers comerciales + auditoría para sectores regulados (gobierno, banca, salud).
- v1.1 (2026-04-28): +referencia POL_DATA_CLASSIFICATION en relacionado.
- v1.0 (2026-04-28): Creación. Decisión arquitectónica D (contract-first, implementación incremental). 8 decisiones cementadas. Roadmap 9 semanas. Trigger CEO `indexa de una vez` post discusión MoAT + carpintería/calidad + Action Engine medular.
