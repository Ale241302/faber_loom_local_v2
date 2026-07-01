---
id: SPEC_FB_EVAL_ARENA
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FaberLoom (IDX_FB_FOUNDATION_BETA)
tipo: spec
last_review: 2026-06-02
stamp: DRAFT -- 2026-06-02 -- creado en Cowork (generated_staging), pendiente promocion a canonico
aplica_a: [FaberLoom, MWT]
---

# SPEC_FB_EVAL_ARENA -- Arena de Evaluacion Ciega y Gobernanza de Routing Multi-Proveedor / Multi-Tenant

> Feature de FaberLoom que da servicio a MWT como primer tenant. Consolida el diseno
> trabajado en sesion Cowork 2026-06-02 + el blueprint de investigacion externa
> GATEWAY-LLM-20260603-9e4a (Kimi swarm). NO edita SPEC_AI_GOV ni SPEC_LLM_ROUTING:
> los referencia y reconcilia (ver Seccion 9).

## A. Proposito

Permitir que cada workspace/tenant registre cuantas APIs de LLM quiera, evaluar su
calidad de forma ciega y objetiva contra golden sets, y enrutar cada request al mejor
resultado al menor costo -- con la decision de calidad tomada en frio (arena) y la
ejecucion en caliente (router) estrictamente separadas.

Principio rector: **la calidad se decide en la arena (offline); el router solo aplica
el ranking ya computado (online).** Nunca al reves.

## B. Reconciliacion con la KB existente (no reinventar)

| Pieza nueva de este SPEC | Se apoya en / extiende |
|---|---|
| Clasificador de tier en pre-call hook | L1 Clasificador de SPEC_LLM_ROUTING_ARCHITECTURE |
| Matriz sensibilidad x provider, fail-closed | POL_DATA_CLASSIFICATION seccion I (D9 Action Engine) |
| Allow-list + virtual keys por tenant | ENT_PLAT_LLM_ROUTING v2.0 (tenant_model_allowlist) |
| Panel de jueces ciego, familias distintas | SPEC_AI_GOV Componente 6 (dual review, regla familias distintas) |
| Golden cases / corpus | ENT_AI_GOV_GOLDEN_CORPUS_MWT (schema) + ENT_FB_RFQ_REPLAY_SET (lifecycle, split) |
| Final-pass premium online | SPEC_AI_GOV (final pass) -- aqui se generaliza como modo del motor de eval |
| Override de calidad por agente | AgentSpec de ARCH_AGENT_PRINCIPLES P1 + ModelFingerprint P13 |
| Validacion anti-cross-tenant | SPEC_TENANT_CONTAMINATION_TESTS |
| Integridad de promocion de config | POL_SYNC_MANIFEST_INTEGRITY |

## C. Componente 1 -- Registro abierto de APIs (self-service por workspace)

Cualquier endpoint OpenAI-compatible entra como un deployment. No-compatibles via
adapter LiteLLM. El registro es config-driven: agregar una API = una entrada, no codigo.

Schema de entrada:

```yaml
- label: "mi-deepseek"                  # nombre del usuario
  api_base: "https://api.deepseek.com/v1"
  credential_ref: "vault://<tenant>/deepseek_key"   # NUNCA key en claro
  model_id: "deepseek-chat"
  openai_compatible: true
  declared_jurisdiction: "CN-direct | US | EU | via-fireworks | ..."
  declared_dpa: false
  candidate_tiers: ["simple", "medium"]
  scope: workspace                      # se registra a nivel workspace
```

Compuertas obligatorias al ingresar (las unicas 2 barreras humanas; el resto lo decide
la arena):
1. **Health check** -- ping + key valida + formato de respuesta. Falla => alta rechazada.
2. **Clasificacion de jurisdiccion/DPA** -- fija su fila en la matriz de egress.
   Sin clasificar => por defecto SOLO PUBLIC (fail-closed).

Tras el alta: estado SHADOW (sin trafico productivo) y encolada en la arena. No enruta
hasta pasar el gate (Componente 2).

Limite real del self-service: no la cantidad sino el costo de evaluacion. Evaluacion
**incremental** (solo la API nueva contra el golden set) + presupuesto de eval por tenant
(Decision D1). El gate es el portero: una API mala no degrada produccion, solo no enruta.

## D. Componente 2 -- Motor de evaluacion (un motor, dos modos)

Misma rubrica, misma definicion de calidad, misma infra. Dos modos:

- **Modo ARENA (offline, batch):** rankea TODOS los modelos a mano contra el golden set.
  Produce la tabla `provider x tier x tenant -> {quality, schema_rate, uptime, latencia, costo, gate_pass}`
  que lee el router. Corre semanal + al registrar API nueva + al cambiar precios.
- **Modo FINAL-PASS (online, single output):** valida UN output en caliente antes de
  entregarlo, contra la misma rubrica. Es el "final pass premium" de SPEC_AI_GOV
  generalizado. Se dispara solo en tareas que lo declaran (alto stakes).

### D.1 Escalera de grading (barato -> caro)

| Metodo | Costo | Mide | Tier |
|---|---|---|---|
| Schema-conformance | gratis | valida el SCH_ | todos (primer filtro) |
| Assertions deterministas | gratis | exact/regex/json-path/rango | tareas verificables |
| LLM-as-judge + rubrica | medio | calidad subjetiva | reasoning/agentic (muestreado) |
| Human spot-check | caro | ground truth; calibra al juez | 1-5% |

Regla: lo que falla schema NO se manda al juez (ahi esta el ahorro).

### D.2 Evaluacion ciega (doble ciego)

1. Cada modelo candidato genera su respuesta.
2. El harness asigna labels OPACOS y ALEATORIOS por caso (resp_A, resp_B, ... rotados).
3. El mapeo {label -> modelo} se sella aparte.
4. El panel de jueces puntua solo los labels, contra la rubrica.
5. Recien post-scoring se des-sella y se agrega.

Mitigaciones de sesgo:
- **Self-preference:** el ciego lo neutraliza; ademas un juez nunca debe ser el unico de
  su familia evaluando a su familia.
- **Position bias:** randomizar orden y letra por caso.
- **Verbosity bias:** la rubrica separa forma de fondo; normalizar por longitud.

### D.3 Panel de jueces (familias distintas)

Es el dual review de SPEC_AI_GOV. Default operativo: Opus 4.8 + GPT-5.5 + Gemini 5.5
(familias distintas). Agregacion por **mediana** (resiste outliers). Baja concordancia
entre jueces => flag a human review. Al des-sellar, se mide si un juez favorecio lo suyo.

Escalonamiento por costo: arrancar con 1 juez fuerte ciego (pairwise) para el ranking;
subir a panel de 3 familias solo para decisiones de promocion de provider y tier agentic.

### D.4 Formatos: Elo + gate absoluto

- **Pairwise ciego + Elo:** ranking relativo "quien es mejor" por tier.
- **Scoring absoluto + rubrica:** pasa/no pasa el umbral del tier (el GATE).

El router usa ambos: gate para filtrar, Elo para desempatar.

## E. Componente 3 -- Golden sets (scope workspace, heredables al tenant)

Los golden sets viven a nivel **workspace**. Un tenant puede heredar golden sets de
workspaces superiores (los "heredados"). Misma cascada de herencia que la config (Comp. 4).

- **Datos: sinteticos representativos (sample info), no reales sensibles.** El corpus NO
  contiene N3/N4 raw. PF_2453 (proforma triangular) se incorpora como caso #1 **sintetizado**
  (estructura y logica reales; numeros, nombres y cedulas ficticios).
- **Schema del golden_case:** el de ENT_AI_GOV_GOLDEN_CORPUS_MWT (id, tenant_id, version,
  query, expected/rubrica, asserts, weight, provenance, data_classification N0-N2).
- **Construccion:** auto-add desde produccion como `candidate` (lifecycle de
  ENT_FB_RFQ_REPLAY_SET), validacion humana a `active`, split fairness preservado
  (regla R4: la rotacion no puede limpiar los casos incomodos), >= 20% edge cases.
- **Aislamiento:** un golden set de un tenant nunca se evalua contra modelos no
  autorizados de ese tenant; nunca se mezcla con otro tenant sin k-anon.

Estado actual del corpus: VACIO (esqueleto definido). Arranque recomendado: 10-15 casos
reales sinteticos de UNA tarea (bullets Rana Walk o proforma B2B) para correr el loop;
escalar a 50-100 despues. El metodo ya existe; falta el trabajo de curacion.

## F. Componente 4 -- Routing y herencia de configuracion

### F.1 Jerarquia de precedencia en runtime (mas especifico gana)

```
request
  1. AUTH + CONTEXTO     tenant_id + data_classification desde JWT claim (NUNCA headers)
  2. pre_call_hook(<20ms): clasifica TIER; arma ALLOW-LIST =
        providers_del_tenant INTERSECT providers_por_data_class INTERSECT providers_del_tier
        ambiguo o no-resoluble => DENIEGA (fail-closed)
  3. SESSION PINNING     si la sesion ya tiene provider, mantenerlo
  4. SCORING (GATE+min-cost) sobre la allow-list, con metricas de la arena
  5. DISPATCH            fallback chain validada en CI: nunca sale de la allow-list
  6. POST-CALL           Token Ledger: costo + governance + savings (Comp. 6); audit inmutable
```

### F.2 Herencia de configuracion (cascada)

```
Global > Org(tenant) > Team > Workspace > Agente(AgentSpec) > Key > Request
```

Un tenant/workspace/agente **hereda** el ruteo de las capas superiores out-of-the-box y
puede ajustarlo en su scope si su rol (RBAC, SPEC_FB_AUTH_TENANT_RBAC) lo permite.

### F.3 Regla del override: solo endurece, nunca relaja

| Clase de parametro | Override del tenant/workspace/agente | Direccion |
|---|---|---|
| Seguridad / egress (matriz data_class x provider, fail-closed, hard-blocks) | si, con permiso | SOLO mas restrictivo |
| Preferencia (modelo preferido por tier, budget, umbral de calidad, pinning) | si, con permiso | ambas, dentro del ceiling de la org |

`model access = interseccion (key AND team AND org)`: nunca se amplia mas alla del ceiling,
solo se recorta. Budgets: mas restrictivo gana.

### F.4 Override de calidad por workspace/agente

El umbral de calidad (gate) es ajustable hasta el nivel de AgentSpec:

```yaml
agent: proforma_builder_b2b
  inherits: tenant.<tenant>
  routing_override:
    min_quality: 0.95          # sube el gate -> solo premium sirve a este agente
    force_tier: reasoning
    rationale: "numeros que deben cuadrar; cero tolerancia a error"
```

Subir calidad = endurecer = permitido. Bajar el gate de seguridad o habilitar un provider
bloqueado por egress = RECHAZADO aunque el rol sea admin.

## G. Componente 5 -- Disponibilidad y BYO-keys

Dos capas de disponibilidad distintas:
- **Gateway (LiteLLM HA):** compartida, MWT/FaberLoom la garantiza.
- **Providers/modelos:** cuando un tenant trae BYO-keys, **hereda** los rate limits, cuota
  y uptime de SUS APIs. El sistema no da mas SLA que el que la API aportada permite.

Aislamiento: la salud de las APIs del tenant A no afecta a B (circuit breakers y cooldowns
per-tenant-deployment).

Fallback cuando la API propia cae (Decision D2):
- **Estricto (default):** sin fallback fuera de sus APIs; cumple "solo mis IAs".
- **Hibrido (opt-in):** fallback al pool global con billing y governance distintos.

## H. Componente 6 -- Savings Ledger (efectos del router vs IA de referencia)

Por cada request, ademas del costo real, se registra el contrafactual:

```
modelo_real + costo_real + gate_passed
baseline_model + costo_baseline      (cuanto habria costado con la IA de referencia)
ahorro = costo_baseline - costo_real
```

- **Baseline canonico (Decision D4): premium occidental fijo** (Opus/GPT-5). Reporta:
  "calidad >= gate al X% del costo de mandar todo a premium". Vista secundaria opcional:
  vs status quo.
- **4 efectos a documentar:** costo, calidad (delta de quality_score), latencia, disponibilidad
  (requests salvados por fallback).
- **Regla de oro:** nunca reportar ahorro sin la columna "calidad mantenida". Ahorro sin
  calidad equivalente es teatro.
- **Honestidades (marcar como estimacion):** el contrafactual es hipotetico (asume mismo
  resultado al primer intento); los tokens difieren entre modelos (estimar los del baseline,
  no copiar los del real) -- declarar [SUPUESTO].
- Override deliberado (Comp. F.4) se distingue en el ledger: un agente forzado a premium
  "no ahorra" por decision, no por fallo del router (campo rationale).

Vive en el Token Ledger de SPEC_LLM_ROUTING como campos adicionales (counterfactual_cost,
savings, quality_maintained).

## I. Componente 7 -- MCP FaberLoom-en-MWT (roadmap)

FaberLoom expone sus capacidades (registro de APIs, arena, routing, savings) via un
servidor MCP para que la operacion MWT (Cowork, Claude Code, n8n) las consuma de forma
transparente -- MWT como primer tenant que usa FaberLoom sin friccion de integracion.
[PENDIENTE -- definir superficie del MCP: tools expuestos, auth por tenant, contrato].

## J. Decisiones (default de experto, ajustables por CEO)

| # | Decision | Default fijado | Razon |
|---|---|---|---|
| D1 | Presupuesto de evaluacion | **por tenant** (batch de sistema lo paga FaberLoom) | self-service ilimitado solo es sostenible si quien mete APIs paga su eval |
| D2 | Fallback BYO-keys | **estricto por default, hibrido opt-in** | respeta "solo mis IAs" y jurisdiccion; no factura tokens no autorizados |
| D3 | Score del juez | **gate + metrica de negocio en el ledger** | persistir es barato y trackear calidad en el tiempo detecta drift |
| D4 | Baseline del savings | **premium fijo (Opus/GPT-5)** + vista opcional status quo | es el baseline que defiende el caso ante CEO y cliente |

## K. Gaps y pendientes

| Gap | Estado |
|---|---|
| Corpus golden vacio | trabajo de curacion humana pendiente (sprint dedicado) |
| Calibracion de umbrales del gate (0.60-0.90) | [SUPUESTO] valores de Kimi; calibrar contra resultado de negocio |
| Definicion objetivable de "A+" para tareas generativas | rubrica por tarea pendiente (separar forma de fondo) |
| Superficie del MCP FaberLoom-en-MWT | [PENDIENTE -- Comp. I] |
| Frecuencia exacta del batch de arena | [SUPUESTO] semanal + triggers; ajustar con volumen real |

## L. Reglas inquebrantables

1. La calidad se decide en la arena (offline); el router solo aplica el ranking. No juzgar calidad en el hot path.
2. Toda API nueva entra SHADOW; no enruta hasta pasar el gate.
3. Egress fail-closed: sin clasificacion => solo PUBLIC. El override nunca relaja seguridad, solo endurece.
4. Evaluacion ciega siempre; el juez no ve el origen del output.
5. Golden cases con datos sinteticos; nunca N3/N4 raw.
6. Aislamiento multi-tenant: golden sets, credenciales y metricas no se filtran entre tenants (validar con SPEC_TENANT_CONTAMINATION_TESTS).
7. Nunca reportar ahorro sin calidad mantenida.

---

Changelog:
- v1.0 (2026-06-02): Creacion. Consolida sesion de diseno Cowork 2026-06-02 + blueprint
  externo GATEWAY-LLM-20260603-9e4a. 7 componentes + 4 decisiones de experto. Scope
  FaberLoom (da servicio a MWT). DRAFT en generated_staging, pendiente promocion a canonico
  via sync + indexacion en IDX_FB_FOUNDATION_BETA + append a MANIFIESTO_CAMBIOS_v2. No edita
  SPEC_AI_GOV ni SPEC_LLM_ROUTING (los referencia). ASCII puro.
