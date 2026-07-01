---
id: SPEC_FABERLOOM_WORKFLOW_ENGINE_v1
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FABERLOOM
date: 2026-04-21
authors: CEO + arquitecto (iteración post Kimi Swarm 3)
supersedes: —
inputs:
  - SPEC_FABERLOOM_AGENT_COMPOSITION_v1.md (v1.0 DRAFT)
  - SPEC_FABERLOOM_SKILL_COMPOSITION_v1.md (v1.0 DRAFT)
  - SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md (v1.0 DRAFT)
  - docs/archivo/kimi_swarm_3_workflows_autonomous.md (síntesis 9 dim · 200+ búsquedas · 7,643 líneas)
  - project_faberloom_architecture.md (AgentSpec/Runtime/Memory, Chat+Workflows híbrido)
  - project_faberloom_security.md (draft-first, policy engine externo)
aplica_a: [FaberLoom]
---

# SPEC — FaberLoom Workflow Engine v1

**Documento arquitectónico técnico.** Traduce las decisiones de `SPEC_FABERLOOM_AGENT_COMPOSITION_v1` y `SPEC_FABERLOOM_SKILL_COMPOSITION_v1` en stack concreto, DSL, protocolo de handoff Agente↔Workflow, mecanismos anti-loop, learning loop y observabilidad. Gemelo técnico de los dos SPEC de composición.

Aplican reglas de KB: R1 no inventar · R2 no tocar FROZEN · R5 documentar todo cambio.

---

## 0. Alcance y estado

**Alcance:** motor de ejecución de workflows embebido en FaberLoom, DSL declarativo, 4 patrones de integración Agente↔Workflow, protocolo JSON de handoff v1.0, mapeo de Authority Mode a mecanismos técnicos, mecanismos anti-loop (max depth, circuit breaker, idempotency, timeout, max iterations), learning loop Fase 1 (PatchRAG + few-shot), observabilidad (Langfuse + Phoenix), sandwich de contención (RLS + prompt + draft-first), 5 templates YAML pre-armados para wedge calzado B2B, roadmap Sprint 1-4, checklist Go/No-Go beta, presupuesto.

**No cubre:** modelo de datos de `Agent` y `Skill` (ya canónico en SPECs respectivos), UI de Agent Console (mockup FROZEN), builder visual de workflows (Fase 2 post-beta).

**Estado v1.0 DRAFT.** Promoción a APPROVED requiere: (a) validación de stack con un backend eng senior, (b) prueba de integración pg-boss + Letta + Claude SDK en ambiente staging, (c) resolución del seed Fase 1 (bloqueante compartido con SPECs de composición).

---

## 1. Principio rector

**Workflow-primero, agente-selectivo.** El workflow es la unidad de ejecución determinística, serializable y versionable. El agente LLM es un *paso* dentro del workflow (`agent-as-step`), no el orquestador. La autonomía del agente se manifiesta como modo de autoridad (SEÑALA/PROPONE/EJECUTA_CON_APROBACIÓN/EJECUTA_SOLO), no como control del flujo.

**Consecuencias:**
- El motor ejecuta DAG determinístico con pasos que pueden ser LLM-backed o no.
- El estado vive en Postgres (checkpointing nativo). Workflows dormidos no consumen compute.
- La ejecución es idempotente, reintentable y auditable.
- El agente es *invocado* por el workflow con contrato JSON explícito, no al revés.

**Regla sagrada heredada:** toda comunicación externa (email/WhatsApp/Slack a clientes, facturas, cobros) pasa por `waitForApproval()`. El modo EJECUTA_SOLO no aplica a externos, ni siquiera en L4.

---

## 2. Stack técnico Fase 1

| Capa | Herramienta | Licencia | Costo | Sprint |
|---|---|---|---|---|
| Motor workflow F1 | **pg-boss** (npm sobre Postgres) | MIT | $0 | S1 |
| Motor workflow F2 | **Inngest self-hosted** (single binary) | Apache 2.0 SDKs / SSPL server | $0 | M3-M4 |
| DSL F1 | **YAML declarativo** (CNCF Serverless Workflow DSL subset) | N/A | $0 | S1 |
| DSL F2 | **React Flow** + YAML bidireccional | MIT | $0 | post-beta |
| Agent framework | **Letta** (memoria) + **LangGraph** (checkpointing) + **Claude Agent SDK** (tool use) | MIT | $0 | S2 |
| Sandboxing | RLS + system prompt + policy engine + draft-first | N/A | $0 | S1 |
| Observabilidad | **Langfuse** Cloud Core + **Arize Phoenix** drift | MIT / Apache 2.0 | $35/mes | S2 |
| Learning loop | **PatchRAG** + few-shot con gold samples | N/A | $0 | S3 |
| Infra | Hetzner CPX21 + Postgres pgvector | — | $27-45/mes | S1 |

**Total Fase 1:** $106-132/mes (dentro del budget $150).

**Veredicto sobre alternativas:**

| Herramienta | Veredicto | Razón |
|---|---|---|
| pg-boss | ADOPTAR F1 | MIT, Postgres nativo, SKIP LOCKED exactly-once |
| Inngest | ADOPTAR F2 | Durable execution, `step.sleep(1año)`, `step.waitForEvent()` |
| Temporal | ROBAR PATRONES | Overkill, >$50/mes idle, 19.7k stars pero infra pesada |
| Windmill | NO ADOPTAR | AGPL-3.0 fuerza open-sourcear producto |
| Trigger.dev v3 | NO ADOPTAR | CRIU experimental, 4CPU/8GB min |
| OpenHands | NO ADOPTAR | Explícitamente NO multi-tenant |
| React Flow | ADOPTAR F2 | 36.3k stars, MIT, equipo full-time Berlin |
| LangGraph | ADOPTAR F1 | Checkpointing con PostgresSaver, 8% overhead |
| Claude SDK | ADOPTAR F1 | `allowed_tools` + `can_use_tool` mapea 1:1 a Authority Mode |
| Langfuse | ADOPTAR día 1 | MIT, OTel nativo Claude, cost tracking por tenant |
| E2B Pro | RESERVAR | $150/mes, activar SOLO si agente ejecuta código no confiable |

---

## 3. DSL: YAML declarativo Fase 1

Subset de CNCF Serverless Workflow DSL. Source-of-truth en tabla `workflow_templates` (Postgres), validado con JSON Schema antes de persistir. Serializable, versionable, LLM-generable.

### 3.1 Estructura base

```yaml
version: "1.0"
id: cotizacion_b2b_v1
name: "Cotización Rápida B2B"
tenant_scope: all  # o tenant_id específico
trigger:
  type: message_keyword
  channel: whatsapp
  keywords: ["cotizar", "precio", "presupuesto", "cuánto cuesta"]
  idempotency_key: "{{message.id}}"

constraints:
  timeout_budget_sec: 300
  max_depth: 2
  max_iterations: 5
  max_budget_usd: 1.0

steps:
  - id: validar_input
    type: function
    fn: parse_sku_quantity
    input: "{{trigger.message.body}}"

  - id: consultar_stock
    type: db_query
    query: "SELECT * FROM inventory WHERE sku = :sku"
    params:
      sku: "{{steps.validar_input.sku}}"

  - id: qualify
    type: agent
    agent_id: QualifyBot
    authority_mode: PROPONE
    input:
      lead: "{{trigger.contact}}"
      sku_qty: "{{steps.validar_input}}"
      stock: "{{steps.consultar_stock}}"
    output_schema:
      classification: string
      confidence: number
      draft_propuesta: string
      riesgos: array

  - id: aprobacion
    type: wait_for_approval
    approver_role: "gerente_ventas"
    input: "{{steps.qualify.draft_propuesta}}"
    sla_hours: 4
    on_timeout: notify_supervisor

  - id: enviar
    type: channel_send
    when: "{{steps.aprobacion.decision}} == 'APROBADO'"
    channel: "{{trigger.channel}}"
    to: "{{trigger.contact.id}}"
    body: "{{steps.qualify.draft_propuesta}}"

  - id: registrar_crm
    type: db_insert
    table: crm_events
    payload:
      type: propuesta_enviada
      contact_id: "{{trigger.contact.id}}"
      amount: "{{steps.qualify.draft_propuesta.total}}"

events_emitted:
  - propuesta_enviada
```

### 3.2 Tipos de step soportados Fase 1

| Tipo | Descripción | Ejemplo |
|---|---|---|
| `function` | Función pura determinística | Parseo, cálculo, validación |
| `db_query` | SELECT con RLS automático | Consulta de stock, catálogo, historial |
| `db_insert` / `db_update` | Mutación con RLS + auditoría | Crear OC, registrar evento CRM |
| `agent` | Invocación de agente LLM (§5) | QualifyBot, CollectionBot, NotifierBot |
| `wait_for_approval` | HITL gate (§5.4) | Revisión humana de draft |
| `channel_send` | Envío por canal (email/WhatsApp/SMS) | Enviar propuesta aprobada |
| `sleep` | Pausa determinística | Esperar 3 días post-entrega |
| `emit_event` | Publicar evento para cascade | `propuesta_enviada` |
| `branch` | Condicional con `when:` | if sentimiento == negativo |
| `parallel` | Fork paralelo con `join` | Notificar múltiples canales |

### 3.3 Pipeline de compilación

```
YAML template → JSON Schema validator → AST intermedio → pg-boss job graph → Postgres
```

El motor lee el AST y genera jobs pg-boss correspondientes. Cada step es un job individual con `retry` configurado. El estado de avance vive en tabla `workflow_runs` + `workflow_step_runs` con FK a `workflow_templates.id` y `workflow_templates.version`.

---

## 4. Motor de ejecución

### 4.1 Fase 1 — pg-boss

**Tablas clave (autocreadas por pg-boss):** `pgboss.job`, `pgboss.archive`, `pgboss.schedule`, `pgboss.version`.

**Tablas añadidas por FaberLoom:**
- `workflow_templates` (id, version, tenant_id NULL=global, yaml, ast_json, status)
- `workflow_runs` (id, template_id, tenant_id, trigger_payload, status, started_at, finished_at)
- `workflow_step_runs` (id, run_id, step_id, status, input, output, error, started_at, finished_at)
- `workflow_approvals` (id, run_id, step_id, approver_id, decision, comment, decided_at)

**Wrapper tenant-safe obligatorio:**

```javascript
async function with_tenant_session(tenant_id, fn) {
  const client = await pool.connect();
  try {
    await client.query(`SET LOCAL app.tenant_id = '${tenant_id}'`);
    return await fn(client);
  } finally {
    await client.query('DISCARD ALL');
    client.release();
  }
}
```

**Regla:** cada job handler recibe `tenant_id` del payload y envuelve toda operación DB en `with_tenant_session`. NUNCA filtrar tenant_id desde el browser. RLS hace el trabajo real.

### 4.2 Fase 2 — Inngest self-hosted

Agregar cuando se necesiten:
- `step.sleep("3 days")` — esperas largas sin consumo de compute
- `step.waitForEvent("invoice.paid", timeout="30 days")` — HITL con timeout largo
- Checkpointing automático con memoización de resultados de cada step
- Versionado sin migración manual

Inngest corre como single binary junto al app. Mismo Postgres, mismo VPS.

**Criterio de promoción pg-boss→Inngest:** cuando aparezca el primer workflow con `sleep > 24h` o `waitForEvent` con timeout > 7 días. No antes.

---

## 5. Protocolo Agente↔Workflow

### 5.1 Cuatro patrones de integración

| # | Patrón | Cuándo usar | Complejidad |
|---|---|---|---|
| 1 | **Agent-as-step** | Paso dentro de workflow que requiere razonamiento. **Dominante en Fase 1.** | Media |
| 2 | **Chat-launches-workflow** | Usuario conversa → agente dispara workflow async → reporta progreso | Media |
| 3 | **Event-driven notifier** | Workflow termina → evento → agente decide canal/tono | Media-Baja |
| 4 | **Human-in-the-loop gate** | `waitForApproval()` en pasos con side-effects externos. **Regla sagrada.** | Baja-Media |

El **80% de los workflows Fase 1** usan cadena compuesta: Chat (1) → Agent-as-step (2) → HITL (4) → Event notifier (3). Todos con `depth_remaining=2`.

### 5.2 Protocolo JSON de handoff v1.0

**Request (workflow → agente):**

```json
{
  "session": {
    "run_id": "uuidv7",
    "tenant_id": "uuidv7",
    "workflow_id": "cotizacion_b2b_v1",
    "step_id": "qualify",
    "invoked_at": "2026-04-21T14:23:11Z"
  },
  "agent": {
    "id": "QualifyBot",
    "version": "1.2.0",
    "authority_mode": "PROPONE",
    "autonomy_level": "L1"
  },
  "constraints": {
    "depth_remaining": 2,
    "max_tool_calls": 10,
    "max_turns": 20,
    "max_budget_usd": 1.0,
    "timeout_sec": 90
  },
  "input": {
    "lead": { "...": "..." },
    "sku_qty": { "...": "..." },
    "stock": { "...": "..." }
  },
  "memory_scope": "mem:agent:QualifyBot:working"
}
```

**Response (agente → workflow):**

```json
{
  "agent_result": {
    "status": "ok",
    "classification": "lead_calificado",
    "confidence": 0.92,
    "output": {
      "draft_propuesta": "...",
      "riesgos": ["..."]
    },
    "tool_calls": [...],
    "tokens_used": 3421,
    "cost_usd": 0.024,
    "duration_ms": 1840
  },
  "trace_id": "langfuse-trace-xyz",
  "next_action": "wait_for_approval"
}
```

### 5.3 Mapeo Authority Mode → mecanismos técnicos

| Authority Mode | Mecanismo Claude SDK | Efecto |
|---|---|---|
| **SEÑALA** | `allowed_tools: ["read_*"]` solamente | Output va a bandeja como observación. No genera draft. |
| **PROPONE** | `allowed_tools: ["read_*", "draft_*"]` | Output va a bandeja como draft editable. No se envía. |
| **EJECUTA_CON_APROBACIÓN** | `allowed_tools: [...*...]` + `waitForApproval()` obligatorio | Draft + gate humano antes de side-effect. |
| **EJECUTA_SOLO** | `allowed_tools: [...*...]`, sin gate | Ejecuta y notifica. **PROHIBIDO para canales externos.** |

**Tabla de configuración:** `agent_authority_config (agent_id, tool_pattern, mode)`. Cambiar modo = UPDATE, no deploy. `<1s` propagación.

### 5.4 `waitForApproval()` — Fase 1 (polling)

```javascript
async function waitForApproval({ run_id, step_id, approver_role, input, sla_hours, on_timeout }) {
  const approval_id = await db.insert('workflow_approvals', {
    run_id, step_id, approver_role, input, status: 'pending',
    sla_deadline: new Date(Date.now() + sla_hours * 3600 * 1000)
  });
  await notify_approver(approver_role, approval_id, input);
  // Fase 1: polling con pg-boss delay queue
  return await boss.send('check_approval', { approval_id }, { startAfter: 10 });
}
```

En Fase 2 (Inngest): `const decision = await step.waitForEvent('approval.decided', { timeout: '4h', match: 'data.approval_id == approval_id' })`.

---

## 6. Mecanismos anti-loop (obligatorios día 1)

| Mecanismo | Valor default | Implementación |
|---|---|---|
| **Max depth counter** | `depth_remaining: 2` | Workflow → agente → NO más agentes. Decremento en cada handoff. |
| **Circuit breaker** | 3 fallos consecutivos → fallback template estático | Reintentar en 1h. Estado en `workflow_circuit_state`. |
| **Idempotency keys** | Todo trigger con key única, TTL 7 días | `UNIQUE(idempotency_key)` + `ON CONFLICT DO NOTHING` |
| **Timeout budget** | 5 min por sesión completa | Distribuido: workflow 3min + agente 1.5min + notif 30s |
| **Max iterations** | 5 contactos por factura (cobranza) | Intento #5 → escalamiento forzoso |
| **Max turns (LLM)** | 20 por query (Claude SDK) | Hard stop |
| **Max budget USD** | $1.00 por query, $20/día tenant pago, $5/día gratis | Kill switch por z-score > 4 |
| **Max token burn** | 10,000 tokens por sesión | Cortar antes de respuesta |

**Todos los mecanismos se activan ANTES de que el LLM responda, no después.**

---

## 7. Learning Loop Fase 1

### 7.1 PatchRAG + few-shot dinámico

- **Correcciones del usuario** se sanitizan (PII strip, dedup) y se almacenan como *patches* embebidos en pgvector.
- En cada nueva query del mismo agente, retrieval híbrido (semantic + metadata) trae patches relevantes + gold samples al contexto.
- Inference-time learning, sin retraining, sin GPU. Lag <5 segundos post-promoción.
- PatchRAG: 62.3% accuracy promedio vs baselines basados en entrenamiento (paper arXiv 2026).

### 7.2 UI de feedback (S3)

- **Thumbs up/down** en cada output, <2s con micro-dropdown de razón (tono / dato / fuente / acción / falta contexto).
- **Diff capture** automático cuando el usuario edita el output.
- **Banner "Guardar como gold sample"** visible en <1s post-edición, 1-click (13 campos ya canónicos en `project_faberloom_agents_design.md`).
- **Pipeline:** Candidate → Active → Archived/Reverted. Nunca promoción directa desde thumbs up.

### 7.3 Cross-tenant (Fase 2)

- **F2 inicial:** schema-level insights anonimizados (qué tipo de correcciones son frecuentes, no qué contenido).
- **F2 avanzado:** DP-LoRA federado con epsilon 3-6 (differential privacy).
- Nunca enviar gold samples raw cross-tenant.

### 7.4 Umbrales

- PatchRAG: sin umbral, disponible tras 1 corrección validada.
- LoRA selectivo por tenant: esperar ≥50 gold samples.
- DP-LoRA federado: esperar ≥10 tenants activos con ≥50 gold samples cada uno.

---

## 8. Observabilidad

### 8.1 Langfuse desde día 1

- SDK con `@observe` decorator en cada llamada LLM.
- Tags obligatorios: `tenant_id`, `agent_id`, `workflow_id`, `run_id`, `step_id`, `authority_mode`, `version`.
- Cost tracking por tenant/agente/workflow.
- Trace-level con version tag para canary y rollback.

### 8.2 Arize Phoenix para drift

- Embedding drift detection en KB chunks y gold samples.
- Alerta cuando la distribución de embeddings de queries diverge del baseline (proxy para cambio de uso).

### 8.3 Métricas críticas (Sprint 2)

| Métrica | Threshold alerta | Acción |
|---|---|---|
| Approval rate del agente (24h) | <85% | Alerta P1 Slack |
| Cost per run (P95) | >$0.50 | Alerta P2 + revisión prompt |
| Latency P95 workflow | >5min | Alerta P1 |
| Token cost z-score | >4 | **Kill switch automático**, pausa tenant |
| Cross-tenant leak attempts | >0 | Alerta P0 crítica |
| User correction rate | >15% | Alerta P2, candidato a gold sample review |
| Loop detection trips | >0 | Alerta P0, auditoría |

---

## 9. Sandwich de contención

**Principio:** múltiples capas débiles gratuitas > una capa fuerte costosa.

| Capa | Mecanismo | Costo | Efecto |
|---|---|---|---|
| 1 | **Postgres RLS** con `FORCE ROW LEVEL SECURITY` + `SET app.tenant_id` server-side | $0 | Elimina cross-tenant data leak en vector search y queries |
| 2 | **System prompt** con reglas hardcoded + policy engine custom | $0 | Previene comunicación inapropiada antes del LLM |
| 3 | **Draft-first** para todo canal externo (email/WhatsApp/Slack/factura/cobro) | $0 | HITL gate obligatorio, ni L4 lo elude |
| 4 | **seccomp + Landlock** (Linux nativo) para parseo de archivos subidos | $0 | Sandbox de proceso para código no confiable |
| 5 | **E2B Pro / Firecracker microVM** SOLO si agente ejecuta código no confiable | $150/mes | Reservado para Fase 2 si aparece el caso |

**Anti-patrones prohibidos:**
- Post-filtering por tenant_id (el LLM ya vio todo antes del filtro).
- Filtrar tenant_id desde browser/cliente.
- Agente que puede llamar a `channel_send` sin pasar por `waitForApproval` para externos.

---

## 10. Top 3 riesgos + mitigación

| # | Riesgo | Prob | Impacto | Mitigación | Deadline |
|---|---|---|---|---|---|
| 1 | **Runaway agent** quema budget LLM | 30% | Crítico ($150 en horas) | Triple contención: `max_turns=20` + `max_budget_usd=1` + token burn + daily caps + kill switch z-score>4 | S2 sem 4 |
| 2 | **Cross-tenant data leak** via vector search | 20% | Crítico (LGPD/LPDP liability) | Pre-filtering RLS obligatorio + `FORCE` + `SET app.tenant_id` server + `DISCARD ALL` en pool | S1 sem 2 |
| 3 | **Deploy roto en beta** sin detección | 35% | Alto | Tenant-level canary (Marluvas pago) + feature flag rollback <60s + 50 golden test cases en CI + alerta approval rate <85% en 24h | S2 sem 4 |

---

## 11. Roadmap Sprint 1-4 (8 semanas beta)

### Sprint 1 (S1-S2) — Infra + Motor Base

| # | Decisión | Deadline | Criterio éxito |
|---|---|---|---|
| 1.1 | `npm install pg-boss`, tablas auto, pool integrado | Día 3 | Job "welcome_email" ejecuta ok |
| 1.2 | `with_tenant_session()` wrapper con RLS + DISCARD ALL | Día 5 | Test RLS: 0 leaks en 100 queries cruzadas |
| 1.3 | Schema YAML + validador JSON Schema | Día 7 | YAML ejemplo valida, genera AST correcto |
| 1.4 | 3 templates cargados (cotización, cobranza, stock) | Día 8 | Listables por API, activables por tenant |
| 1.5 | Endpoint REST listar/activar templates | Día 10 | 1 llamada API activa template |
| 1.6 | RLS en `knowledge_base_chunks`, `emails`, `tickets`, `contacts`, `invoices` | Día 12 | 100% tablas tenant-scoped con FORCE |

### Sprint 2 (S3-S4) — Agentes + HITL + Observabilidad

| # | Decisión | Deadline | Criterio éxito |
|---|---|---|---|
| 2.1 | Letta + pg-boss handoff JSON v1.0 | Día 15 | Handoff ok con output estructurado |
| 2.2 | Tabla `agent_authority_config` | Día 17 | Cambio de modo <1s, sin deploy |
| 2.3 | QualifyBot agent-as-step | Día 19 | JSON válido con clasificación + draft |
| 2.4 | `waitForApproval()` con polling | Día 21 | Pausa → aprueba → continúa en <5s |
| 2.5 | Langfuse `@observe` + tags obligatorios | Día 23 | 100% LLM calls trazados |
| 2.6 | 3 métricas + alertas Slack | Día 24 | Alertas disparan en thresholds |
| 2.7 | Kill switch feature flag | Día 26 | Rollback 100% tráfico <60s |

### Sprint 3 (S5-S6) — Cobranza + Defensas + Learning Loop

| # | Decisión | Deadline | Criterio éxito |
|---|---|---|---|
| 3.1 | CollectionBot agent-as-step | Día 29 | Draft tono apropiado por segmento |
| 3.2 | Circuit breaker 3 fallos → fallback | Día 31 | Testeado con simulación |
| 3.3 | Max depth counter + timeout budget | Día 33 | depth=0 rechazado, timeout aborta graceful |
| 3.4 | Idempotency keys con TTL 7d | Día 35 | Dup ignorado sin side-effects |
| 3.5 | Thumbs up/down + razón | Día 37 | >80% outputs con feedback primera semana |
| 3.6 | Diff capture + banner gold sample | Día 40 | Banner <1s post-edición |
| 3.7 | PatchRAG con pgvector | Día 42 | Corrección retrievable <5s |

### Sprint 4 (S7-S8) — Integración + Beta Ready

| # | Decisión | Deadline | Criterio éxito |
|---|---|---|---|
| 4.1 | 50 golden test cases end-to-end | Día 45 | >95% pasan, 0 regresiones críticas |
| 4.2 | Testing 3 design partners | Día 48 | 3/3 partners con workflow activo |
| 4.3 | Ajuste prompts | Día 50 | Approval rate >85% en datos reales |
| 4.4 | Docs + guía operación partners | Día 52 | Aprobado por equipo |
| 4.5 | Deploy prod con monitoreo 24/7 | Día 53 | 48h sin alertas P0/P1 |
| 4.6 | Revisión sprint + KPIs baseline | Día 56 | Reporte con métricas base |

---

## 12. 5 Templates YAML Fase 1 (wedge Marluvas/Tecmater)

| # | Template | Agente | Authority | Aprobación humana | SLA |
|---|---|---|---|---|---|
| 1 | **Cotización Rápida B2B** | QualifyBot (Ventas) | PROPONE | SÍ — gerente ventas | <2min a bandeja, <5min a cliente |
| 2 | **Cobranza Inteligente** | CollectionBot (Cobranza) | PROPONE | SÍ — supervisor (auto-approve si monto<$5k MXN AND conf>0.85 AND tono!=ultimátum) | <4h supervisor, fallback tono suave |
| 3 | **Alerta Stock Bajo** | Ninguno (determinístico) | N/A | SÍ — admin confirma OC | <1min alerta, <5min a proveedor |
| 4 | **Bienvenida Nuevos Clientes** | NotifierBot (template pre-aprobado) | EJECUTA_SOLO | NO (template sin LLM) | <30s post-registro |
| 5 | **Seguimiento Post-Venta** | SurveyBot (Servicio) | EJECUTA_CON_APROBACIÓN → EJECUTA_SOLO tras 5 envíos con >90% thumbs up | SÍ primeras 5, NO después | 3 días post-entrega |

**Detalle completo** en Sección 5 de `docs/archivo/kimi_swarm_3_workflows_autonomous.md`.

---

## 13. Checklist Go/No-Go Beta

### Técnicos (MUST HAVE, sin excepciones)

| # | Criterio | Threshold |
|---|---|---|
| 13.1 | pg-boss sin pérdida de mensajes | 100% delivery en 100 jobs |
| 13.2 | RLS previene cross-tenant | 0 leaks en 50 queries × tenant |
| 13.3 | Workflow cotización end-to-end | P95 <5 min |
| 13.4 | HITL pausa/reanuda | 100% success 3 aprobadores |
| 13.5 | Kill switch reversión | <60s |
| 13.6 | Loop detection | 100% bloqueo en 3 escenarios |
| 13.7 | Langfuse cobertura LLM calls | 100% con metadata |

### Producto (MUST HAVE)

| # | Criterio | Threshold |
|---|---|---|
| 13.8 | 3 design partners con workflow activo | 3/3 |
| 13.9 | Time-to-first-workflow admin no-técnico 45+ | <3 min |
| 13.10 | Approval rate primera semana | >80% |
| 13.11 | 0 comunicaciones externas sin HITL | 0 incidentes |
| 13.12 | Costo por run | <$0.50 |

### UX (SHOULD HAVE, flexible — 2/3)

13.13 activación template sin ayuda · 13.14 error <30s a resolver · 13.15 thumbs usado >30%

### Negocio (NICE TO HAVE)

13.16 partner pago renueva mes 2 · 13.17 stack <$150 primera beta · 13.18 0 incidentes seguridad

**Regla decisión:** GO = 100% técnicos + 100% producto + ≥2/3 UX. NO-GO = cualquier MUST HAVE no cumplido.

---

## 14. Presupuesto mensual

### Escenario base

| Componente | Mes 1 | Mes 3 | Mes 6 | Mes 12 |
|---|---|---|---|---|
| Hetzner CPX21 | $15 | $15 | $15 | $30 |
| Postgres + pgvector | $20 | $20 | $20 | $35 |
| LLM API Claude (3 partners) | $40 | $60 | $80 | $150 |
| Langfuse Cloud Core | $29 | $29 | $29 | $49 |
| Arize Phoenix self-host | $0 | $6 | $6 | $6 |
| AWS Secrets Manager | $2 | $2 | $2 | $4 |
| **TOTAL** | **$106** | **$132** | **$152** | **$274** |

Escenario optimista $57-142/mes · Pesimista $172-603/mes (incluye E2B Pro $150 si se activa VM sandbox).

---

## 15. Impacto en SPECs existentes

| SPEC | Cambio | Versión |
|---|---|---|
| `SPEC_FABERLOOM_AGENT_COMPOSITION_v1` | Agregar 3 secciones: Workflow Execution Engine (referencia este SPEC), Agent↔Workflow Integration Protocol (referencia §5), Learning Loop (referencia §7). **No reescribir, addendum v1.1.** | 1.0 → 1.1 |
| `SPEC_FABERLOOM_SKILL_COMPOSITION_v1` | Sin cambios en diseño. Validado por swarm. | 1.0 |
| `SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT` | Agregar tablas nuevas al conteo S1: `workflow_templates`, `workflow_runs`, `workflow_step_runs`, `workflow_approvals`, `agent_authority_config`, `workflow_circuit_state` = **+6 tablas**. Total S1: 18 (anterior) + 6 = **24 tablas**. | 1.0 → 1.1 |

---

## 16. Dependencias entre SPECs

```
SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT (infra, UUIDv7, RLS, obs)
  ├─ SPEC_FABERLOOM_SKILL_COMPOSITION_v1 (modelo Skill)
  │    └─ SPEC_FABERLOOM_AGENT_COMPOSITION_v1 (modelo Agent, bindings a Skills)
  │         └─ SPEC_FABERLOOM_WORKFLOW_ENGINE_v1 (este SPEC — motor, DSL, handoff, runtime)
  └─ SPEC_FABERLOOM_USER_ADMIN_KNOWLEDGE_FLOW_v1_BETA (permisos, KB flow)
```

---

## 17. Pendientes P0 que desbloquean APPROVED

- [ ] Validación stack con backend eng senior (mirar licencias, compatibilidad de versiones)
- [ ] Prueba de integración pg-boss + Letta + Claude SDK en staging
- [ ] Resolución seed Fase 1 (3 skills sealed + 3 agents sealed — bloqueante compartido con SPECs de composición)
- [ ] D12 Position↔User decoupling implementado en schema (bloqueante P0 handoff Cowork, ya en tarea S1)
- [ ] ADR explícito "pg-boss vs Temporal vs Inngest" archivado
- [ ] Confirmación CEO sobre budget LLM diario por tenant ($20 pago / $5 gratis)

---

## Changelog

- **2026-04-21 v1.0 DRAFT** — Creación inicial. Basado en Kimi Swarm 3 (9 dim · 200+ búsquedas · 7,643 líneas). Stack pg-boss→Inngest, YAML DSL, 4 patrones handoff, protocolo JSON v1.0, sandwich de contención, PatchRAG learning loop, Langfuse obs, 5 templates wedge, roadmap 8 semanas, checklist Go/No-Go, presupuesto $106-132/mes base.
