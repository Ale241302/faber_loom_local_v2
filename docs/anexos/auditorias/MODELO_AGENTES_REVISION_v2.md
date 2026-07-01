# Modelo de Arquitectura de Agentes IA — Solicitud de Opinión Externa (v2)

**De:** Álvaro (CEO Muito Work Limitada)
**Para:** modelo de IA externo (ChatGPT u otro)
**Versión:** 2 — incluye contexto del repo que faltaba en v1.
**Pedido concreto:** crítica honesta del modelo conceptual nuevo y de los gaps reales. NO recomendar lo que ya está canonizado en el repo (sección 5). Si tu primera reacción es proponer Task/Run/Tool/Action/Event/Eval-suite/Anti-tenancy/Multi-agent debate — leelos primero en sección 5 y movete a los gaps reales en sección 8.

---

## 1. Quién soy y contexto operativo

CEO de **Muito Work Limitada (MWT)**, Costa Rica. Tres tracks operativos:

- **Rana Walk** — marca propia de plantillas ergonómicas, vendiendo en Amazon FBA.
- **Representación B2B** — distribuyo Marluvas y Tecmater (calzado de trabajo) en industrias de México a Colombia.
- **FaberLoom** — SaaS B2B LATAM en construcción para PYMEs/fabricantes. Es lo que quiero que critiques.

KB versionada de 540 archivos `.md` (430 operativos) en repo `mwt-knowledge-hub`, mirror OneDrive para Cowork. Taxonomía de 8 tipos canónicos: ENT/PLB/SCH/LOC/POL/IDX/SKILL/LOTE + especiales SPEC/ARCH/AUDIT.

Conocimiento técnico sólido. Tono directo. No me felicites — criticá.

---

## 2. Qué es FaberLoom

### 2.1 Propuesta y target

SaaS multi-tenant para **PYMEs B2B LATAM** que delegan tareas operativas a agentes IA. No es plataforma "construya su agente". Es agente con criterio operativo repetible que escala con curaduría.

**Stack independiente** del Knowledge Hub MWT (codebase, deployment y BD separados). Identidad propia "Faber" (no Claude visible al cliente).

### 2.2 Wedge inicial cerrado

**Vertical safety_footwear** — cotización B2B de calzado de seguridad. MWT como primer tenant validador (representación Marluvas/Tecmater). 3 design partners requeridos para promoción de v1 DRAFT a APPROVED. Ventana beta cerrada: **2026-04-20 → 2026-06-14** (8 semanas, 13 sprints firmados en `PLB_FB_FOUNDATION_BETA_v1`).

Verticales candidatos post-MVP (catálogo informacional, NO compromiso v2): legal_practice, software_factory, insurance, medical_regulated, financial_advisory. Documentado en `ENT_FB_VERTICAL_CANDIDATES_v1`.

### 2.3 MVP cerrado (60 días, 8 semanas)

- **1 agente, 3-5 herramientas, 2 workflows** (cobranza + proformas).
- **Single-agent en MVP, no multi-agent.** Decisión basada en evidencia técnica, no preferencia (ver §6 Decisiones cerradas).
- Pipeline canónico de 8 fases: recepción WhatsApp → KB → acción propuesta → HITL → log → aprendizaje → mejora.
- Métrica: ROI percibido en 30 días por la PYME real.

### 2.4 Pricing y compliance

Cuatro tiers (`ENT_FABERLOOM_PRICING_TIERS` v1.0 VIGENTE):

| Plan | USD/mes | Data class ceiling | Modelos | Audit |
|---|---|---|---|---|
| Starter | $19-29 | N1 Trabajo | cualquiera con DPA | básico (1 año) |
| Pro | $59-89 | N2 (con add-on) | US/EU con DPA | detallado (5 años) |
| Enterprise | $249-399 | N3 Distribuidor-scoped | US/EU + RLS estricto | full (7 años) |
| Government | $999-2499 | N4 Privado | US/EU exclusivo | full + auditor API (10 años) |

Compliance LATAM: CO + MX + CR + PA + BR (LGPD). Add-ons desbloqueables (Confidencial, Audit Pro, Compliance Pack LATAM, Multi-region Storage, Auditor API Access, SLA 99.9% / 99.95%).

### 2.5 Stack técnico cerrado

| Componente | Tecnología | Costo/mes |
|---|---|---|
| Backend API | FastAPI + Pydantic AI | $0 |
| BD | Supabase (Postgres + pgvector + RLS) | $0-25 |
| Gateway LLM | LiteLLM | $0 |
| Frontend | Next.js 15 | $0 |
| Cola | ARQ + Redis | $0-20 |
| Canal primario | WhatsApp Business API | $0-50 |
| Hosting | Railway / Fly.io | $20-50 |
| Observabilidad | Langfuse + logging estructurado | $0-50 |
| Memoria persistente | Letta self-host | incluido |
| **Total MVP** | | **$70-195/mes** |

Identifiers: **UUIDv7 client-side** (FROZEN, no ULID). PKs uuid nativas Postgres.

---

## 3. Lo que está YA canonizado en el repo (NO recomendar de nuevo)

Esta sección existe para que no recicles lo que ya está. Si tu crítica recomienda algo de esta tabla, asumí que falta refinarlo, no crearlo de cero.

### 3.1 Arquitectura de agentes — capas e identidad

| Documento | Estado | Qué define |
|---|---|---|
| `ARCH_AGENT_PRINCIPLES.md` v1.5 | VIGENTE | 14 principios fundacionales. P0 (agente ≠ prompt), P1 (3 objetos: AgentSpec/Runtime/Memory), P3 (draft-first invariante absoluto), P4 (autonomy por evidencia con thresholds), P5 (gate humano aprendizaje), P6 (feedback tipificado 6 códigos), P7 (state machine), P8 (telemetría no negociable), P9 (gobernanza embebida), P10 (handoffs estructurados), P11 (clasificador aprendizaje 3 destinos), P13 (contención), P14, P16 (sub-agents atomic). |
| `SPEC_FABERLOOM_AGENT_COMPOSITION_v1` v1.1 | DRAFT | Modo dual SEALED/OPEN paralelo skills. 7 dimensiones distinción Skill vs Agent. Identidad + canal + position binding (D12) + autonomy ladder L0-L4 + authority mode (SEÑALA / PROPONE / EJEC_APROB / EJEC_SOLO). Memoria 3 capas Letta (episodic/working/persistent). Runtime status (shadow/running/paused/error). |
| `ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1` (P16) | VIGENTE | Patrón canónico: orquestadores delgados stateful + sub-agentes atómicos stateless. -65% token cost cuantificado. Threshold cuándo NO es sub-agente (= skill_package determinista). Model routing per task. |
| `ENT_FB_AGENT_ARCHETYPES_v1` v2.0 | VIGENTE | 7 arquetipos (Skill_package / Generator / Triage / Validator / Orchestrator / Swarm / Reactive) con outcome metric típica + budget heurístico + validaciones obligatorias. |

### 3.2 Runtime e infraestructura — 20 tablas FROZEN

`SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT` v1.0 DRAFT — Sprint 1 funcional con 20 tablas FROZEN agrupadas:

| Cluster | Tablas | Para qué |
|---|---|---|
| Identity (S1) | `tenant`, `user_account`, `department`, `user_department`, `session` | Multi-tenant, jerarquía dept (parent_dept_id), RLS context vars |
| Plumbing (S1) | `event_outbox`, `inbox_message`, `audit_event`, `job_execution` | Outbox pattern, idempotency 14d TTL, audit append-only con SHA-chain, scheduler locks |
| Agents (S2) | `agent_spec`, `agent_binding`, `agent_run` | Definición versionada (status=active/superseded/revoked + supersedes_<x>_id), bindings spec↔scope↔user/dept, ejecución append-only |
| Knowledge (S2) | `memory_source`, `memory_chunk`, `memory_chunk_vector`, `overlay_policy` | Chunks versionados scope-aware, embeddings reemplazables, policies scope-override |
| Drafting (S3) | `draft`, `draft_decision` | Borrador outbound + aprobación/rechazo append-only |
| Connectors (S3) | `connector_account`, `connector_send_log` | OAuth por user (revoked_at soft), bitácora envío externo append-only |

**Reglas transversales FROZEN:**
- PK uuid nativo (UUIDv7) en todas.
- Sin FKs físicas — referencias lógicas + outbox + reconcile.
- `audit_event`, `agent_run`, `draft_decision`, `connector_send_log` append-only estricto: RLS niega UPDATE/DELETE a faber_app.
- 5 RLS settings en cada conexión: `app.tenant_id`, `app.user_id`, `app.role` (owner/admin/operator), `app.dept_ids` (csv uuid), `app.break_glass` (boolean).

### 3.3 Tasks / Cases / Runs

`SCH_FB_TASK_ENTITY` v2.0 VIGENTE — tareas como entidad de primera clase:

```sql
tasks(
  task_id uuid PK,
  agent_id, agent_version, flow_node_id,
  invocation_mode IN ('ad_hoc','scheduled','webhook','flow_node'),
  invoked_by, invoked_at, priority IN ('low','normal','high','urgent'),
  payload jsonb, expected_outputs text[],
  status IN ('queued','running','awaiting_approval','completed','failed','cancelled','timeout'),
  started_at, completed_at, expected_completion_by,  -- SLA por prioridad
  run_id, parent_task_id, child_task_ids,
  review_status IN ('pending','accepted','edit_light','rejected'),
  reviewed_by, reviewed_at, review_notes
)
```

Con `flow` como DAG separado (`SCH_FB_FLOW_DAG`): skill define qué sabe hacer, flow define cómo paso a paso, task es ejecución concreta.

### 3.4 Eventing y outbox

`SPEC_FB_EVENTING_AND_OUTBOX_v1` VIGENTE — 4 capas (NO es event_bus simple):

```
1. Event log canónico (Postgres append-only + SHA-chain integrity)
2. Outbox pattern (transaccional, garantiza at-least-once)
3. Transport bus (Redis Streams, distribución realtime + workers)
4. UI fanout (WebSocket/SSE)
```

Idempotency keys via event_id. Retention regulada per privacy tier.

### 3.5 Tools / Actions / Permissions

`ENT_PLAT_ACTION_REGISTRY` v1.1 VIGENTE — 53 acciones catalogadas con `accepts_data_class` (N0-N4), `side_effects` (none / reversible / irreversible), DPA matrix LATAM por proveedor. Categorías: `llm_provider`, `data_api`, `communication_api`, `tool_local`. Ejemplos: `llm.claude_sonnet_46`, `api.amazon_sp_api`, `comm.whatsapp_business_send`, `tool.xml_parse_dian`.

`SPEC_ACTION_ENGINE` con D9 (Data Classification enforcement) + D10. `SCH_ACTION_SPEC.yaml` v1.1 schema machine-readable. Implementación en `mwt_action_engine/registry/*.yaml`.

`POL_AI_GOV_DATA_CLASS_PROVIDER` v1.0 VIGENTE — matriz Data Class × Provider enforced en Token Ledger (`provider_allowed_by_policy`, `data_class_max_in_chain`).

### 3.6 Eval suite y contract testing

`SPEC_FB_CONTRACT_TEST_HARNESS_v1` VIGENTE — gate técnico antes de Sprint 1 + regression suite obligatoria pre-deploy:

- **Capa 1 OpenAPI conformance** — schemathesis (property-based fuzzer)
- **Capa 2 Fixtures Ciclope** — pytest custom, 30 fixtures YAML, 702 assertions, mock LLM determinístico vía LiteLLM
- **Capa 3 UI flows E2E** — Playwright + axe-core (a11y)

CI/CD: GitHub Actions. Run en cada PR backend.

### 3.7 Knowledge River — modelo de aprendizaje 2 capas

`ENT_FB_USER_LEARNING_MODEL_v1` (capa 1 USUARIO) + `ENT_FB_COMMITTEE_OPERATING_MODEL_v1` (capa 2 ORG) + `SPEC_FB_KNOWLEDGE_RIVER_v1.1`:

| Aspecto | CAPA 1 USUARIO | CAPA 2 ORG |
|---|---|---|
| Actor | AM individual | Comité (curador + reviewers) |
| Decide | qué aprende SU agente personal | qué se vuelve pattern organizacional |
| Cadencia | AM-driven | semanal/mensual |
| Memoria target | L2 episódica privada | L3 colectivo / L4 firmado |
| Privacidad | sin k-anon (es su data) | k-anon ≥5 obligatorio |
| UI | Mesa de Control AM-view | pantalla rol Gobernanza separada |

P11 ARCH_AGENT_PRINCIPLES — clasificador aprendizaje 3 destinos por evento:
- **CONTEXTO** (hecho organizacional ausente)
- **SKILL_REFINEMENT** (regla comportamiento mal aplicada/ausente)
- **GOLD_SAMPLE** (output aprobado con ≤20% edición)

Implementación: prompt estructurado sobre Claude Haiku 4.5 con structured outputs. Confidence < 0.80 → human gate sin proponer. Latencia objetivo <1500ms p95. Costo <$0.005/evento.

Signals que disparan candidate: `accepted_clean`, `edit_heavy` (>20% texto + diff), `rejected` con razón tipificada (6 códigos: tone/data/structure/policy/scope/context), `iteration_correction`. Patrón = signal repetido ≥3 ocasiones similares.

### 3.8 Privacy y RBAC

| Doc | Define |
|---|---|
| `SPEC_FB_AUTH_TENANT_RBAC_v1` | RLS Postgres con 5 settings, roles owner/admin/operator |
| `POL_FB_KR_PRIVACY_TIERS_v1.1` | Tiers privacidad knowledge river, k-anon ≥5 capa org |
| `POL_FB_KNOWLEDGE_VALIDITY_AND_EXPIRY_v1` | Vigencia y expiración de chunks de KB |
| `POL_DATA_CLASSIFICATION` v1.2 VIGENTE | N0-N4 canónico (Público/Trabajo/Confidencial/Distribuidor-scoped/Privado) |
| `POL_FABERLOOM_SURFACE_CONTRACT` | Contrato de superficie del producto |
| `POL_FB_OUTCOME_ACCOUNTABILITY` | Accountability de outcomes |

### 3.9 Audit

`SPEC_AUDIT_MODULE` (sealed) — SHA-chain integrity en `audit_event`. Cada propuesta del clasificador P11 genera trace en observability + AuditEntry si propone destino N2+.

### 3.10 Identity y position binding

`SPEC_FB_AGENT_COMPOSITION` decisión D12 — agentes asignados a `position`, NO a users directos. Permite rotación de personal sin re-binding.

`SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1` (18 campos canon) — contrato intermedio estructurado entre agentes/skills (no se pasa texto bonito).

`SCH_AI_GOV_HANDOFF_DRAFT` — schema handoff Carpintero → Final Pass para Dual Review con `final_pass_required/executed/shortcut_reason` en Token Ledger.

`ENT_FB_RFQ_EXCEPTION_TAXONOMY_v1` (15 exception codes) + `ENT_FB_RFQ_REPLAY_SET_v1.1` (replay set 2 etapas validación).

---

## 4. Decisiones cerradas no negociables

Estas decisiones tienen evidencia técnica documentada. No son preferencia. NO me digas que reconsidere ninguna sin contraevidencia equivalente.

| Decisión | Razón |
|---|---|
| **Single-agent en MVP, NO multi-agent** | (a) MAST UC Berkeley NeurIPS 2025: 41-86.7% tasa fallo en multi-agente sobre 1,642 trazas con Cohen's Kappa = 0.88. (b) Single-agent iguala multi-agent en razonamiento multi-hop bajo igual presupuesto tokens (NeurIPS 2025, Data Processing Inequality). (c) Confiabilidad compuesta degrada exponencial: 10 handoffs al 99% = 90.4%; 20 handoffs al 95% = 35.8%. Costo multi-agent 2-5× tokens. Equipo 1-3 devs no puede depurar coordinación inter-agente mientras valida hipótesis de mercado. |
| **Modo dual Sealed (FaberLoom-made, update channel) / Open (cliente, 100% editable)** | Marketplace + custom sin duplicar sistema. Misma arquitectura, semántica diferente. |
| **Memoria persistente con Letta self-host** | Watch-list activa para CF Agent Memory. Letta provee 3 capas episodic/working/persistent. |
| **UUIDv7 client-side, no ULID** | Time-ordered + lex-sortable + tipo uuid nativo Postgres 16. Índice 16 bytes vs 26. RLS casts `::uuid` funcionan sin reescrituras. |
| **Sub-agents stateless, orquestador stateful** | P16 atomic agents principle. Token cost reduction -65%. Audit precision granular. Learning concentration (DRAFT_WRITER recibe pool TODOS los AMs → corpus mejor). Model routing per task (Haiku para clasificadores, Sonnet para creatividad). |
| **Draft-first invariante absoluto (P3)** | Cero envío externo autónomo en ningún nivel del autonomy ladder. CEO declaración 2026-04-28: P3 invariante absoluto, no admite excepción runtime ni override CEO ad-hoc. |
| **Autonomy por evidencia, no configuración** | P4: thresholds duros (≥10 ejecuciones nivel actual, ≥80% approval, ≥60% edit-light, ≤10% rejection, ≥14 días sin error grave, AgentMemory activa, aprobación CEO). Degradación automática si rejection >30% en últimas 5. |
| **Curaduría 2 capas separadas** | Capa 1 USUARIO (AM con sus agentes, sin k-anon) + Capa 2 ORG (comité, k-anon ≥5 obligatorio). Insight ChatGPT R5 ya integrado: "el error era tratar curador como rol universal — no lo es". |
| **Foundation Beta 8 semanas firmada** | 2026-04-20 → 2026-06-14. 13 sprints. `PLB_FB_FOUNDATION_BETA_v1` FIRMADO CANÓNICO. |
| **Agentes asignados a positions, no users (D12)** | Rotación de personal sin re-binding. |
| **Append-only estricto en audit/draft_decision/connector_send_log/agent_run** | RLS niega UPDATE/DELETE a faber_app. |
| **Final Pass Premium obligatorio** | `POL_AI_GOV_FINAL_OUTPUT_QUALITY` — Carpintero → Final Pass con Token Ledger. Shortcut solo con razón documentada. |

---

## 5. Modelo conceptual nuevo en discusión (lo que pido critiques)

Esto es lo que estoy proponiendo agregar/refinar. Es lo que necesita opinión.

### 5.1 Cinco primitivas semánticas

```
Conocimiento  → factual, citable, estable. Ejemplo: precio MGN-50, jurisprudencia, specs producto.
Contexto      → lente que define cómo se usa el conocimiento. Ejemplo: "este cliente prefiere conciliar".
Skill         → habilidad atómica con contract input/output. Verbo: redactar_proforma.
Agente        → ejecutor con varios skills coordinados internamente. Persona-rol.
Workspace     → scope contextual con propósito declarado (mandato).
```

### 5.2 Cinco sabores de Contexto (tipo de archivo `CTX_` a crear)

| Tipo | Vive en | Mutabilidad | Ejemplo |
|---|---|---|---|
| **CTX base de skill/agente** | Definición versionada del skill | Bump por release | "Skill `redactar_demanda` usa estilo formal, estructura X" |
| **CTX organizacional** | Catálogo org versionado | Bump por curaduría organizacional (capa 2) | "En este bufete priorizamos sala constitucional" |
| **CTX workspace** | Workspace mismo | Mutable durante vida del workspace | "Cliente Sondel, contrato 2024, prefiere conciliar" |
| **CTX usuario** | Memoria del usuario | Mutable por usuario (capa 1) | "Este AM siempre rechaza opción polímero EVA" |
| **CTX vivo (sesión)** | Runtime, transient | Por hilo | "Hoy redacto réplica para audiencia jueves" |

Inyección al agente en orden: **base → org → workspace → usuario → vivo**.

### 5.3 Workspace como primitiva con MANDATO

Anatomía propuesta:

```yaml
id: WS_SONDEL
type: WS
status: ACTIVO
visibility: [PARTNER_B2B]

## Mandato
proposito: representar a Sondel en cuenta MWT, materia comercial
scope_incluye: [cotizaciones, proformas, reclamos, escalación técnica]
scope_excluye: [contratos legales, decisiones financieras]
autoridad: [proponer cotizaciones; aprobación CEO para >$5K]
vigencia: 2026-01-01 → 2026-12-31 (renovable)
constraints: POL_DETERMINISMO, POL_VISIBILIDAD, contrato representación

## Agentes/skills disponibles
## KB del workspace
## Pool de candidatos local
## Outputs producidos
```

### 5.4 Patrón doble workspace por cliente

| Tipo | Ubicación | Rol | Curado por |
|---|---|---|---|
| **WS_ORG_SONDEL** | Catálogo org | Maestro del cliente: historia, contratos, doctrina aplicada, lecciones acumuladas | Curaduría organizacional (capa 2 ya canónica) |
| **WS_OP_SONDEL** | Operativo local del operador | Día-a-día: tareas activas, drafts en curso | Operador (capa 1 ya canónica), promoción a WS_ORG vía curaduría capa 2 |

`WS_OP_SONDEL` hereda al crearse del `WS_ORG_SONDEL`. Aprendizajes operativos suben vía curaduría al maestro del cliente. Aprendizajes transversales suben al CTX/KB org general anonimizado.

### 5.5 Curaduría — extensión del clasificador P11 con dimensión de alcance

P11 ya tiene 3 destinos (CONTEXTO/SKILL_REFINEMENT/GOLD_SAMPLE). Lo que propongo agregar es **alcance**:

```
DESTINO × ALCANCE:

  Personal     → CTX usuario (capa 1, sólo me afecta a mí)
  Local        → CTX workspace (sólo este scope)
  Cliente      → CTX/KB del WS_ORG_<cliente> (cura: dueño del cliente)
  Org          → Catálogo org (cura: comité capa 2 con k-anon ≥5)
  Marketplace  → Template público (cura: anonimización + revisión upstream)

Cada subida de nivel = gate humano + audit + bump de versión.
```

### 5.6 Niveles de herencia (cascada)

```
NIVEL 1 — MARKETPLACE (público, curado upstream)         [post-MVP]
NIVEL 2 — CATÁLOGO ORG (curado, capa 2 org)              [parcial: Sealed mode existe]
NIVEL 3 — WORKSPACE LOCAL (operativo)                    [GAP: no existe primitiva]
NIVEL 4 — SUB-AGENTE/SUB-SKILL AD-HOC (vida atada al WS) [parcial: P16 sub-agents existe]
```

Operación instanciar (reference) vs forkear (copy). Default: instanciar para mantener determinismo.

---

## 6. Cómo encaja con lo existente (mapeo)

| Concepto modelo nuevo | Estado en repo |
|---|---|
| Skill atómico | `SKILL_*` 13 archivos VIGENTE + `SCH_FB_SKILL_MANIFEST_v2` |
| Agente compuesto | `SPEC_FB_AGENT_COMPOSITION_v1.1` Sealed/Open + 7 archetypes |
| Sub-agente atómico | `ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1` P16 |
| Conocimiento factual | `ENT_*` 104 archivos + `memory_chunk` tabla |
| **Workspace primitiva** | **GAP: no existe `WS_`** |
| Mandato | **GAP: ningún equivalente formal** |
| **5 sabores de CTX** | **GAP: contexto se infiere de PLB/POL/SKILL kb_refs, no formal** |
| Curaduría 5 alcances | Parcial — existe Personal (capa 1) y Org (capa 2). Falta Local/Cliente/Marketplace formales |
| Doble workspace cliente | GAP — no existe el patrón |
| Herencia cascada | Parcial — Sealed/Open existe; cascada formal no |
| Anti-samples / cuarentena | **GAP: P11 tiene 3 destinos, no negativos (REJECTED/QUARANTINED/ANTI_PATTERN)** |
| Resolución conflictos cross-capa | **GAP: no hay engine formal de resolución** |
| Outcome-based learning triggers | Parcial — signals inmediatos están (accepted_clean, edit_heavy, rejected). Outcome de negocio (cotización ganada, ticket no-reabierto, SLA cumplido) no |
| Sanitización RAG anti-prompt-injection | **GAP: RLS protege tenant boundary, pero docs cargados al KB no tienen sanitización formal contra prompt injection** |

---

## 7. Lo que NO necesito de la opinión externa

- Que recomiendes Task/Run/Tool/Action/Event/Eval-suite/Multi-agent-debate/RBAC. **Existen, leelos en sección 3.**
- Que reconsiderás single-agent en MVP. **Decisión cerrada con evidencia.**
- Que recomendés Letta o memoria 3 capas. **Está canonizado.**
- Que sugieras separar Skill de Tool. **Ya está separado en `ENT_PLAT_ACTION_REGISTRY` + `SCH_FB_SKILL_MANIFEST`.**
- Que recomendés contract testing / eval suite / regression. **`SPEC_FB_CONTRACT_TEST_HARNESS_v1` con 702 assertions.**
- Que recomendés separar curaduría personal vs org. **`USER_LEARNING_MODEL` + `COMMITTEE_OPERATING_MODEL` ya separados.**
- Que sugieras audit con SHA-chain. **`SPEC_AUDIT_MODULE` sealed + audit_event append-only.**
- Marketing-talk, frameworks genéricos, libros básicos.

---

## 8. Gaps reales donde busco opinión específica

### 8.1 Workspace como primitiva

Hoy en repo: `task` existe, `flow` existe, `agent` existe, `position` existe (D12). NO existe contenedor scope con mandato que herede a tareas/flows/agentes y tenga su propio pool de candidatos local + KB local + outputs propios.

**Preguntas:**
- ¿Workspace debe ser primitiva o composición de las existentes (position + flow + tasks bundled)?
- ¿Debe tener tipo `WS_*.md` en taxonomía KB o solo objeto runtime en BD?
- ¿Cómo se relaciona con `position` (D12)? Workspace = position + scope contextual?
- Propuse `MANDATO` como nombre del contexto fundacional. ¿Mejor término universal sabiendo que vertical primario es safety_footwear pero después legal_practice / software_factory?

### 8.2 CTX granular

Mi propuesta de 5 sabores (base/org/workspace/usuario/vivo) — ¿son los correctos? ¿Faltan? ¿Sobran? Específicamente sospecho de:
- Distinción **Doctrine vs Style vs Preference** (¿son CTX distintos?)
- ¿Constraints inquebrantables (POL) son un sabor de CTX o categoría aparte?
- ¿CTX vivo de sesión debe persistir en BD o sólo memoria runtime?
- Inyección al agente: ¿bundle compilado con hashes/fuentes/autoridad o capas separadas?

### 8.3 Resolución de conflictos cross-capa

Si CTX org dice A, CTX workspace dice B y CTX usuario dice C — ¿quién gana?

Necesito un engine formal con:
- Precedencia (especificidad)
- Autoridad normativa (compliance > preferencia)
- Vigencia
- Confidence
- Fuente
- Política de desempate

¿Diseño existente que valga referenciar? ¿Riesgos típicos de implementar mal este engine?

### 8.4 Anti-samples / aprendizaje defensivo

P11 clasifica a 3 destinos positivos. Falta:
- `REJECTED_LEARNING` — explicitamente no aprender esto
- `ANTI_PATTERN` — patrón a bloquear
- `LOCAL_EXCEPTION` — excepción de scope acotado
- `TEMPORARY_NOTE` — vigencia limitada
- `EXPIRED` — fecha de cierre
- `QUARANTINED` — bajo revisión por contradicción

¿Cuál de estos vale la pena formalizar? ¿Cómo evitar que el sistema solo "aprenda" y nunca "olvide"?

### 8.5 Outcome-based learning triggers

Hoy en `USER_LEARNING_MODEL` los signals son inmediatos: accepted_clean, edit_heavy, rejected, iteration_correction.

Falta outcome de negocio: cotización convertida a venta, ticket no-reabierto en 30 días, SLA cumplido, sin escalación, no-retrabajo, ausencia de queja.

**Preguntas:**
- ¿Cómo modelar outcomes diferidos (resultado a 30 días) sin perder traza al output original?
- ¿Es un nuevo tipo de evento o extensión del existente?
- ¿Cómo evitar que output exitoso "por casualidad" promueva un patrón malo?

### 8.6 Sanitización RAG anti-prompt-injection

Multi-tenant + KB cargada por cliente + agentes que consumen esa KB = superficie de prompt injection. Hoy `POL_FB_KR_PRIVACY_TIERS` protege privacidad pero no veo SPEC explícito de:

- Sanitización de docs subidos al KB del tenant
- Separación instruction/data en RAG retrieval
- Source trust scoring por chunk
- Detección de instrucciones embedded en docs (no solo PII)
- Tenant boundary checks en cross-tenant aggregations (k-anon ≥5 capa org no es suficiente — el patrón anonimizado puede revelar estrategia)
- Policy firewall en outputs

**Pregunta:** ¿qué SPEC mínimo agregar antes de aceptar primer cliente real con docs sensibles?

### 8.7 Marketplace lifecycle (post-MVP, baja urgencia pero quiero el ángulo)

Hoy `POL_AI_GOV_SKILL_INSTALLATION` cubre skills externas (Anthropic SDK). Para marketplace propio FB falta:
- Publish / Certify / Deprecate / Revoke flow
- Versionado semántico patch/minor/major/security con políticas de adopción distintas
- License + compatibility matrix
- Pinned vs floating references vs auto-patch only
- Eval suite obligatoria pre-publish
- Threat model contra templates marketplace contaminados

**Pregunta:** ¿qué patrones de marketplace de templates AI conocés que sean buena referencia?

---

## 9. Lo que SÍ necesito

- **Huecos reales** en los gaps de §8.
- **Tensiones entre las decisiones cerradas de §4 y los gaps de §8.** Si una decisión cerrada hace imposible un gap, decímelo.
- **Patrones conocidos** que aplican a §8 que no estoy considerando.
- **Riesgos de implementación** específicos a multi-tenant + LLM + LATAM compliance.
- **Casos de borde**: workspaces enormes, organizaciones jerárquicas, sub-organizaciones, cross-org collaboration entre tenants.
- **Trade-offs no evaluados** que podrías ver con experiencia producción.

---

## 10. Formato de respuesta esperado

Tabla de hallazgos:

| Gap (§8.X) | Hallazgo | Severidad (alta/media/baja) | Recomendación concreta | Patrón conocido aplicable |
|---|---|---|---|---|

Más prosa libre para tensiones cross-gap. NO tablas vacías ni concesiones reflexivas. Si todo te parece bien — decime explícitamente qué no encontraste para criticar y por qué.

Gracias por la honestidad.

---

**Fin del documento.**
