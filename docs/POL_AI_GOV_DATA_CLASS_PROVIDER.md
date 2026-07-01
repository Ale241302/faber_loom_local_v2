# POL_AI_GOV_DATA_CLASS_PROVIDER — Matriz Data Classification x Proveedor LLM
id: POL_AI_GOV_DATA_CLASS_PROVIDER
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: POL
subfamilia: AI_GOV (subdominio conceptual bajo Plataforma; indexado en IDX_GOBERNANZA por convencion KB)
stamp: VIGENTE — 2026-05-01
aprobador: CEO
aplica_a: [MWT, FaberLoom]
refs: POL_DATA_CLASSIFICATION (N0..N4 canonico) · POL_VISIBILIDAD · ENT_PLAT_ACTION_REGISTRY (catalogo proveedores con accepts_data_class) · SPEC_LLM_ROUTING_ARCHITECTURE v1.3 (Token Ledger campos provider_allowed_by_policy, data_class_max_in_chain) · SPEC_AUDIT_MODULE (audit_event en violaciones) · ARCH_AGENT_PRINCIPLES P9 (gobernanza embebida) P13 (contencion)

---

## A. Proposito

Define que proveedor LLM puede tocar que tier de data clasificacion. Cierra el hueco entre la definicion de tiers (POL_DATA_CLASSIFICATION) y el inventario de proveedores (ENT_PLAT_ACTION_REGISTRY) con una **regla ejecutable**: la matriz que el Action Engine consulta antes de despachar cualquier llamada LLM.

Sin esta policy, el inventario lista que proveedor "acepta" que tier pero nadie hace cumplir el limite. Esta policy convierte el campo `accepts_data_class` en obligacion.

---

## B. Tiers de data classification (referencia POL_DATA_CLASSIFICATION)

| Tier | Etiqueta | Ejemplos representativos del scope IA |
|------|---------|---------------------------------------|
| N0 | [PUBLIC] | Catalogo, copy publico, FAQ, contenido marketing aprobado |
| N1 | [INTERNAL] | Estrategia interna, playbooks, drafts no publicados, metricas internas |
| N2 | [CONFIDENTIAL] | Pricing fabrica, margenes, modelos financieros, contratos no firmados |
| N3 | [DISTRIBUTOR-SCOPED] | Datos de cliente B2B con NDA, datos de PYMEs FaberLoom, escaneos del distribuidor |
| N4 | [BIOMETRIC] | Escaneos plantares, perfiles biomecanicos, datos personales sensibles |

---

## C. Categorias de proveedor

| Categoria | Definicion | DPA LATAM |
|-----------|-----------|-----------|
| **DPA-FULL** | Proveedor con DPA firmado MWT/FaberLoom + residencia data EE.UU./EU + auditoria SOC2/ISO27001 | Si |
| **DPA-COMERCIAL** | Proveedor comercial sin DPA propio MWT pero con T&C estandar y residencia disclosed | Parcial |
| **NO-DPA-MANAGED** | Servicio managed sin DPA, residencia desconocida o jurisdiccion no aprobada (China, Rusia) | No |
| **SELF-HOST-OPEN** | Modelo open-weights desplegado en infra propia MWT/FaberLoom | Si (DPA propio) |

Mapeo del catalogo actual (extraido de ENT_PLAT_ACTION_REGISTRY a 2026-05-01):

| action_id | Categoria |
|-----------|-----------|
| `llm.claude_opus_47` · `llm.claude_sonnet_46` · `llm.haiku_45` | DPA-FULL |
| `llm.gpt_55` · `llm.gpt_55_pro` · `llm.gpt_55_mini` | DPA-FULL |
| `llm.gemini_31_pro` · `llm.gemini_25_flash` | DPA-FULL |
| `llm.deepseek_v4_pro` · `llm.deepseek_v4_flash` | NO-DPA-MANAGED |
| `llm.kimi_k2_6` · `llm.kimi_k2_6_swarm` (Moonshot managed) | NO-DPA-MANAGED |
| `llm.kimi_k2_6_self` (self-host MIT) | SELF-HOST-OPEN |

El catalogo en ENT_PLAT_ACTION_REGISTRY es la **fuente unica de verdad** del estado actual. Esta matriz se actualiza cuando el catalogo cambia (alta/baja de proveedor).

---

## D. Matriz autoritativa data_class x categoria

| | N0 [PUBLIC] | N1 [INTERNAL] | N2 [CONFIDENTIAL] | N3 [DISTRIBUTOR-SCOPED] | N4 [BIOMETRIC] |
|---|:---:|:---:|:---:|:---:|:---:|
| **DPA-FULL** | OK | OK | OK | OK | OK |
| **DPA-COMERCIAL** | OK | OK | Solo con cost-mode opt-in CEO + audit | NO | NO |
| **NO-DPA-MANAGED** | OK | OK con cost-mode opt-in | NO | NO | NO |
| **SELF-HOST-OPEN** | OK | OK | OK | OK | OK (con cifrado en reposo verificado) |

**Glosario:**
- **OK** = permitido sin override.
- **cost-mode opt-in** = CEO autoriza explicitamente para esta org/skill, queda registrado en audit_event, expira en 90 dias.
- **NO** = bloqueado. El Action Engine debe rechazar antes de despachar. Override solo via override_chain del Engine con audit obligatorio (ver POL_INMUTABILIDAD §override).

---

## E. Regla de orquestador asimetrico (palanca de costo critica)

Un proveedor NO-DPA-MANAGED puede actuar como **orquestador** de una cadena que toca data N2-N4 si y solo si se cumplen las cuatro condiciones:

1. El orquestador recibe SOLO metadata, instrucciones de fan-out, y resumenes anonimizados — nunca payload raw del tier alto.
2. Los carpinteros que tocan raw N2-N4 son provedores DPA-FULL o SELF-HOST-OPEN.
3. El final pass que entrega al usuario es DPA-FULL o SELF-HOST-OPEN (ver POL_AI_GOV_FINAL_OUTPUT_QUALITY).
4. La asimetria queda registrada en el ledger: el `data_classification` del entry del orquestador es N0/N1, el `data_class_max_in_chain` refleja el tier real procesado.

**Por que esta regla:** Kimi K2 / Moonshot es 50-100x mas barato que Opus pero esta hosted en China sin DPA. Como orquestador (que solo ve metadata de tareas) la categoria de data es N0/N1 incluso en chains que procesan N3. Esta es la unica razon arquitectonica para usarlo. Sin la asimetria registrada, el proveedor barato es ilegal de usar para clientes B2B con NDA.

**Anti-patron prohibido:** pasar al orquestador el "contexto completo del cliente" para que decida fan-out. Ese contexto incluye N3 y la chain falla compliance. El orquestador recibe `task_descriptor` (N0/N1), no `raw_client_data`.

---

## F. Cost-mode opt-in (procedimiento)

Algunas tareas no criticas de N1/N2 pueden ejecutarse en NO-DPA-MANAGED si el ahorro lo justifica. Procedimiento obligatorio:

1. Solicitud documentada: `request_id`, `skill_id`, `expected_savings_usd_30d`, `data_class`, `provider_proposed`.
2. CEO firma override_chain en audit_event con `override_reason: "cost_mode_opt_in"`.
3. Vigencia maxima 90 dias. Renovacion requiere nueva firma.
4. Reportable mensual: outputs producidos bajo cost-mode quedan tagueados en el ledger; auditoria mensual revisa drift.
5. Revocable inmediatamente si: (a) drift de quality >15% vs DPA-FULL baseline, (b) incidente de privacy, (c) cambio en T&C del proveedor.

---

## G. Enforcement

El Action Engine consulta esta policy antes de cada llamada LLM via:

```python
def is_provider_allowed(provider_action_id: str, data_class: str, org_id: str) -> bool:
    category = action_registry.get_category(provider_action_id)
    matrix_decision = POL_AI_GOV_DATA_CLASS_PROVIDER.matrix[category][data_class]

    if matrix_decision == "OK":
        return True
    if matrix_decision == "NO":
        return False
    if matrix_decision == "cost_mode":
        return audit_module.has_active_override(org_id, provider_action_id, ttl_days=90)
```

Cada llamada LLM emite un `ledger_entry` con `provider_allowed_by_policy: bool`. Si `false`, el Engine debio rechazar antes; un entry con `false` en el ledger es bug critico que dispara alerta P0.

---

## H. Acciones prohibidas

1. **Bypass del Engine:** ningun skill/agente llama directo a un SDK de proveedor. Solo via `action_engine.execute(intent="llm_call", ...)`. Llamadas directas son violacion.
2. **Inferencia de tier:** ningun skill "decide" que su request es N0 cuando los inputs son N3. La clasificacion la asigna el clasificador upstream o el llamador con auditoria.
3. **Cache de output cross-tier:** un output producido sobre N3 no se reusa para responder N0 a otro tenant. RLS por org_id se mantiene en todas las capas.
4. **Pasar raw N3/N4 al orquestador NO-DPA:** ver §E. Es la violacion mas comun y la mas grave.
5. **Override sin expiracion:** cost-mode opt-in eterno no existe. Maximo 90 dias renovables.

---

## I. Revision

- Trigger automatico: alta o baja de proveedor en ENT_PLAT_ACTION_REGISTRY.
- Trigger calendarico: trimestral.
- Owner: CEO con apoyo del Arquitecto Cowork.
- Cualquier cambio a la matriz (§D) requiere actualizar `provider_policy_version` que el ledger registra. Versiones historicas se preservan para auditoria retrospectiva.

---

Changelog:
- v1.0 (2026-05-01): Creacion. Matriz autoritativa data_class x categoria de proveedor. Regla de orquestador asimetrico. Procedimiento cost-mode opt-in. Enforcement via Action Engine + Token Ledger campo `provider_allowed_by_policy`. Origen: sesion AI_GOV 2026-05-01.
