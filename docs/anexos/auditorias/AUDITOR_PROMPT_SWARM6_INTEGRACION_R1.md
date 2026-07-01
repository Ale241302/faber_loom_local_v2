# Prompt Auditor - Integracion del Swarm #6 al proyecto MWT/FaberLoom

**Para:** modelo de IA externo en rol de auditor (ChatGPT, Claude.ai, otro)
**De:** Alvaro (CEO Muito Work Limitada)
**Pedido concreto:** auditar el plan de integracion del Kimi Swarm #6 al proyecto MWT/FaberLoom. Detectar tensiones con el estado canonizado, decisiones que paso por alto, prioridades mal calibradas. NO repetir investigacion (eso ya lo hizo el swarm). NO concordar reflexivamente.

Este prompt no es para investigar otra cosa. Es para CRITICAR un plan de integracion concreto.

---

## 1. Tu rol como auditor

Tu tarea es revisar 3 cosas:

1. **Coherencia interna del plan de integracion.** Si las 11 decisiones del swarm se aplican al proyecto sin generar contradicciones con lo canonizado.
2. **Tensiones que paso por alto.** Casos de borde, dependencias ocultas, riesgos operativos no levantados.
3. **Calibracion de prioridades.** Si el orden propuesto B -> A -> C es el correcto, o si hay otro orden con mas palanca.

NO tu tarea: investigar mejores alternativas tecnicas. Eso ya lo hizo el swarm con 80+ busquedas y 40+ casos production. Si proponer una alternativa no esta en el swarm, sustenta con caso production real 2025-2026; si no, no proponer.

---

## 2. Contexto operativo (autocontenido)

Soy CEO de **Muito Work Limitada (MWT)** en Costa Rica. Construyendo **FaberLoom**, SaaS B2B LATAM para PYMEs/fabricantes. Vertical inicial: cotizacion B2B de calzado de seguridad. MWT como primer tenant validador.

### Stack frozen

- FastAPI + Pydantic AI
- Supabase (Postgres 16 + pgvector + RLS)
- LiteLLM gateway
- Next.js 15 frontend
- ARQ + Redis (cola async)
- WhatsApp Business API canal primario
- Railway / Fly.io hosting
- Langfuse observabilidad
- Letta self-host memoria persistente
- UUIDv7 client-side identifiers

### MVP cerrado (Foundation Beta)

- 60 dias, 13 sprints firmados
- 2026-04-20 -> 2026-06-14
- 1 agente, 3-5 herramientas, 2 workflows (cobranza + proformas)
- Single-agent, NO multi-agent (decision cerrada con MAST)
- Compliance LATAM: CO + MX + CR + PA + BR (LGPD)
- 4 tiers pricing $19-$2499/mes segun data class N0-N4

### KB del repo

- 540 archivos .md (430 operativos, 110 archivados)
- 10 dominios
- 8 tipos canonicos: ENT/PLB/SCH/LOC/POL/IDX/SKILL/LOTE + especiales SPEC/ARCH/AUDIT
- Patron sync: repo canonico C:\dev\mwt-knowledge-hub + mirror OneDrive via mirror_to_onedrive.ps1 + sync_*_indexa.ps1

---

## 3. Estado canonizado pre-swarm (NO recomendar de nuevo)

Estos artefactos YA estan vigentes en el repo. NO recomendar crearlos.

### Arquitectura de agentes

| Doc | Estado | Define |
|---|---|---|
| ARCH_AGENT_PRINCIPLES.md v1.5 | VIGENTE | 14 principios fundacionales (P0-P14, P16). 3 objetos AgentSpec/Runtime/Memory. Draft-first invariante absoluto P3. P11 clasificador aprendizaje 3 destinos |
| SPEC_FABERLOOM_AGENT_COMPOSITION_v1.1 | DRAFT | Modo dual SEALED/OPEN. 7 dimensiones distincion Skill vs Agent. Identidad + canal + position binding (D12) + autonomy ladder L0-L4 + authority mode |
| ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1 | VIGENTE | P16 sub-agents atomic principle. Orquestadores delgados stateful + sub-agents atomicos stateless |
| ENT_FB_AGENT_ARCHETYPES_v1 v2.0 | VIGENTE | 7 arquetipos (Skill_package / Generator / Triage / Validator / Orchestrator / Swarm / Reactive) |

### Runtime e infra

| Doc | Estado | Define |
|---|---|---|
| SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT v1.0 | DRAFT | 20 tablas FROZEN (tenant, user_account, agent_spec, agent_run, audit_event SHA-chain, draft, memory_chunk, etc.). UUIDv7 client-side. RLS con 5 settings |
| SCH_FB_TASK_ENTITY v2.0 | VIGENTE | Tasks como entidad de primera clase. 7 estados, invocation_mode, run_id, parent/child_task_ids, HITL fields, SLA |
| SPEC_FB_EVENTING_AND_OUTBOX_v1 | VIGENTE | 4 capas: event_log Postgres + outbox + Redis Streams + WS fanout. SHA-chain integrity |
| ENT_PLAT_ACTION_REGISTRY v1.1 | VIGENTE | 53 acciones con accepts_data_class, side_effects, DPA matrix LATAM por proveedor LLM |
| SPEC_FB_CONTRACT_TEST_HARNESS_v1 | VIGENTE | schemathesis + 30 fixtures Ciclope + 702 assertions + Playwright E2E + axe-core a11y |

### Curaduria y aprendizaje

| Doc | Estado | Define |
|---|---|---|
| ENT_FB_USER_LEARNING_MODEL_v1 | VIGENTE | Capa 1 USUARIO. Sin k-anon. AM-driven. L2 episodic privada |
| ENT_FB_COMMITTEE_OPERATING_MODEL_v1 | VIGENTE | Capa 2 ORG. k-anon >=5 obligatorio. L3 colectivo / L4 firmado |

### Privacy + Audit

| Doc | Estado | Define |
|---|---|---|
| POL_FB_KR_PRIVACY_TIERS_v1.1 | VIGENTE | Tiers privacidad knowledge river. k-anon >=5 capa org |
| POL_FB_KNOWLEDGE_VALIDITY_AND_EXPIRY_v1 | VIGENTE | Vigencia y expiracion de chunks |
| POL_DATA_CLASSIFICATION v1.2 | VIGENTE | N0-N4 canonico (Publico/Trabajo/Confidencial/Distribuidor-scoped/Privado) |
| POL_AI_GOV_DATA_CLASS_PROVIDER v1.0 | VIGENTE | Matriz Data Class x Provider enforced en Token Ledger |
| POL_AI_GOV_FINAL_OUTPUT_QUALITY v1.0 | VIGENTE | Final Pass Premium obligatorio. Carpintero -> Final Pass con Token Ledger |
| SPEC_AUDIT_MODULE | VIGENTE (sealed) | SHA-chain integrity en audit_event |
| SPEC_FB_AUTH_TENANT_RBAC_v1 | VIGENTE | RLS Postgres + 5 settings (app.tenant_id/user_id/role/dept_ids/break_glass) |

### RAG Security (recien indexado)

| Doc | Estado | Define |
|---|---|---|
| SPEC_FB_RAG_SECURITY_FIREWALL_v1 | P0_APPROVED_CANDIDATE (score 9.1) | 6 componentes: Ingestion firewall con parser sandbox, chunk metadata 4 scores separados, instruction/data separation con salted tags, retrieval policy, output firewall con covert channels, P11_SECURITY_PRECHECK |

---

## 4. Decisiones cerradas no negociables (NO reabrir)

1. Single-agent en MVP (basado en MAST UC Berkeley NeurIPS 2025: 41-86.7% tasa fallo multi-agent)
2. Letta self-host para memoria persistente
3. UUIDv7 client-side, no ULID
4. Sealed/Open dual mode skills/agents
5. Draft-first invariante absoluto (P3 ARCH_AGENT_PRINCIPLES)
6. Curaduria 2 capas separadas (USER + COMMITTEE con k-anon >=5)
7. Charter como termino tecnico interno; UI traduce por vertical
8. Foundation Beta 8 semanas firmada (2026-04-20 -> 2026-06-14)
9. Stack tecnico cerrado (FastAPI + Supabase + LiteLLM + Next.js + ARQ)
10. Append-only estricto en audit_event/agent_run/draft_decision/connector_send_log
11. Final Pass Premium obligatorio para outputs externos

---

## 5. Output del Kimi Swarm #6 - resumen ejecutivo

Ejecutado 2026-05-07. 4 dimensiones, 4 sub-agentes paralelos, 80+ busquedas web, 40+ casos production citados.

### D1 - Hybrid Retrieval (pgvector + BM25 + RRF)

**Decision principal:** implementar Phase 1 con `tsvector` + `ts_rank_cd` + `pgvector` HNSW + RRF en Python async. NO esperar extension BM25 verdadera (pg_textsearch / pg_search requieren self-host fuera de Supabase).

**Casos production:**
- lpossamai (SaaS B2B 2026): retrieval precision 62% -> 84% (+22pp) con pgvector + tsvector + RRF
- TigerData pg_textsearch BM25: 138M docs <18min indexing
- AI Multiple benchmark: hybrid +18.5% MRR vs dense-only

**Costo:** $0 setup (nativo Supabase). Storage overhead +0.3-0.5x texto vs solo vector.

**Latencia:** p50 <10ms, p95 <20ms con 10K-100K chunks. RLS overhead ~20%.

**RRF k=60 valido para B2B LATAM** (no depende del idioma). Factor critico es tokenizacion espanol/portugues con `to_tsvector('spanish', ...)`.

**NO usar:** rank_bm25 (4.46 QPS lento), bm25s (innecesario si Postgres tiene FTS), LlamaIndex QueryFusionRetriever / LangChain EnsembleRetriever (P99 12.20s vs BM25 puro 1.86s, abstracciones pesadas).

**Implementar RRF a mano en Python (~15 lineas).** Cero dependencias.

### D2 - KB Quality Monitoring

**Decision principal:** **DEFERRED DeepEval + TruLens a Fase 2 post-MVP (~julio 2026).** Plan B en MVP: Langfuse datasets + freshness audit ARQ daily + drift sentinel ARQ monthly + user feedback via draft-first.

**Razon:** equipos 1-3 devs reportan 15-25% tiempo dev en mantenimiento de DeepEval+TruLens primeros 6 meses. Innecesario MVP.

**Costo Plan B:** ~$0.20/mes/tenant (5% sample con GPT-4o-mini judge $0.15/$0.60 por 1M tokens). Escala a 100 tenants = $20/mes = 0.2-0.3% MRR.

**Threshold staleness por tipo:** 7 dias precios, 30 dias fichas tecnicas, 90 dias normativas.

**Threshold embedding drift:** cosine distance 0.08 (no 0.10 default).

**NO usar en MVP:** DeepEval pytest suite, TruLens feedback functions, Confident AI cloud ($19.99-$49.99/seat/mes), eval online por cada query.

### D3 - Chunking strategies

**Decision principal:** NO migracion masiva. Lazy migration con dual-index `CREATE INDEX CONCURRENTLY`.

**Strategy default:** recursive chunking + sentence window. 400-512 tokens, 10-15% overlap.

**Strategy premium:** hierarchical parent-child para POL/PLB criticos. Child=256 tokens (retrieval), parent=1024 tokens (generation context).

**Query-enriched frontmatter:** `queries_answered` con 5-10 preguntas generadas via LLM (GPT-4.1 Nano via LiteLLM). Costo $0.50-1.60 para 540 archivos.

**Casos production:**
- Harvey AI legal: 30% reduccion contract review time, tool selection precision 0.8-0.9
- 47billion universities: fixed-size 61% -> hierarchical 89% accuracy
- Snowflake Finance RAG: ANLS correlation chunk-level -> generation-level

**NO usar:** semantic chunking sin min_chunk_size floor (riesgo micro-fragments 43 tokens), late chunking (requiere jina-embeddings-v3 incompatible con stack), agentic chunking (overhead computacional alto), fixed-size (deprecated produccion B2B).

**Validacion chunks:** RAGAS via Langfuse cookbook. NO DeepEval ContextualRelevancyMetric (degradacion silenciosa sin ground truth).

### D4 - CLAUDE.md patterns

**Decisiones principales:**

1. **Dual-surface CLAUDE.md + WIKI.md** (patron badwally/TheKnowledge):
   - CLAUDE.md (<60 lineas, control surface del agente)
   - WIKI.md (contract humano detallado, evoluciona con gateway)
   - Anthropic envuelve CLAUDE.md con clausula dismissiva ("ignorar si no es altamente relevante")

2. **Hooks como capa de enforcement real:**
   - SessionStart hook re-inyecta reglas tras compactacion
   - PreToolUse hook bloquea Write/Edit a paths del repo canonico
   - UserPromptSubmit hook anade ~15 tokens reminder cada prompt
   - Hook output llega como system-reminder sin framing dismissivo

3. **Anti-rationalization tables (Addy Osmani):** cada regla incluye tabla de excusas comunes con contra-argumentos documentados.

4. **Limite duro ~150-200 instrucciones totales** (incluyendo system prompt Claude Code que ya consume ~50). HumanLayer mantiene <60 lineas. Boris Cherny ~60-83 lineas.

5. **Patron Karpathy edit-time** (4 reglas) + 6 reglas runtime adicionales (Reneza).

**Casos production:**
- Atlassian: -45% PR cycle time con AI review
- 1mg (300 ingenieros): -31.8% review time
- Altana: 2-10x velocidad desarrollo
- Behavox: cientos de devs con Claude Code como pair programmer

### Tensiones cross-dimension resueltas por el swarm

| Tension | Resolucion |
|---|---|
| D3 queria DeepEval para validar chunks vs D2 NO DeepEval en MVP | Usar RAGAS via Langfuse cookbook, no DeepEval pytest |
| D1 indice GIN tsvector vs D3 dual-index migracion | Complementarios. GIN es FTS, dual-index es migracion chunking strategy. Conviven |
| D3 frontmatter extenso vs D4 CLAUDE.md <60 lineas | Aplica a CLAUDE.md (control surface), no a archivos KB. Frontmatter es metadata parseable |

### Costo consolidado MVP

| Tier | Costo mensual | % MRR |
|---|---|---|
| 1 tenant | ~$0.20 | 0.2-0.3% |
| 10 tenants | ~$2 | 0.2-0.3% |
| 100 tenants | ~$20 | 0.2-0.3% |

**Costo dominante = tiempo dev: ~10-15 dias distribuidos en sprints 0-5**, no dinero.

---

## 6. Mi plan de integracion (lo que vas a auditar)

### Paso 1 - Indexar el swarm al repo

Generar 4 archivos sintesis + anexos:

- `ENT_RESEARCH_KIMI_SWARM_6_HYBRID_RETRIEVAL.md`
- `ENT_RESEARCH_KIMI_SWARM_6_KB_QUALITY.md`
- `ENT_RESEARCH_KIMI_SWARM_6_CHUNKING.md`
- `ENT_RESEARCH_KIMI_SWARM_6_CLAUDE_MD.md`
- `docs/anexos/kimi_swarm_6/` con research bruto completo
- `MANIFIESTO_APPEND_20260507_KIMI_SWARM_6_INTEGRATION.md`

### Paso 2 - Bumpear roadmap integral

Actualizar `ROADMAP_INTEGRAL_KB_4_CAPAS.md`:
- Agregar swarm #6 como referencia 4
- 7 hallazgos sorpresa nuevos
- Reemplazar tabla sprints con la del swarm
- Agregar 11 decisiones cerradas nuevas
- Agregar elementos fuera de scope (pg_textsearch, semantic chunking sin floor, late chunking, agentic chunking)

### Paso 3 - SPECs nuevos a generar antes de Sprint 0

| SPEC | Status | Contenido |
|---|---|---|
| SPEC_FB_RAG_SECURITY_FIREWALL_v1.1 | bump v1.0 | Agregar componente C7: Hybrid Retrieval con tsvector + HNSW + RRF Python |
| SPEC_FB_KB_QUALITY_MONITORING_v1 | DRAFT | Plan B Langfuse-based. Freshness audit + drift sentinel + LLM judge sample 5% |
| POL_CHUNKING_KB_v1 | DRAFT | Frontmatter schema con queries_answered + chunk_strategy enum + thresholds por kb_type |
| CLAUDE.md v2 (raiz) | bump | <60 lineas, control surface. Karpathy 4 reglas + 6 runtime + KB-specific |
| WIKI.md (raiz, NUEVO) | DRAFT | Contract humano detallado. Conventions, taxonomy, sync protocol, anti-rationalization tables |
| SKILL_KB_GATEWAY_v1 | NUEVO DRAFT | Gateway pattern para writes al canonico. Validate -> lock -> execute -> log atomico |
| Hooks: hooks/sessionstart.py, hooks/pretooluse_canonical_protect.py, hooks/userpromptsubmit_reminder.py | NUEVO | Enforcement layer real |

### Paso 4 - Orden de ataque que propongo

| Opcion | Justificacion | Mi recomendacion |
|---|---|---|
| A. Indexar swarm + bumpear roadmap primero | Fija contexto entre sesiones | Segundo |
| **B. CLAUDE.md v2 + WIKI.md + hooks PreToolUse** | Mayor palanca para todo lo siguiente. Previene incidente 29-abr (11 archivos FB en docs/ raiz) tecnicamente, no por buena voluntad | **Primero** |
| C. Schema hibrido pgvector + tsvector | Cambio mas rapido (3-4 horas) que desbloquea retrieval real | Tercero |

Mi recomendacion: **B -> A -> C**. Razon: sin hooks de enforcement, todo lo siguiente que ejecute Cowork puede repetir incidentes. Con hooks PreToolUse bloqueando writes al canonico, riesgo se elimina tecnicamente.

---

## 7. Tu auditoria - lo que necesito que critiques

Por favor, responde a las siguientes preguntas con criterio. Si una respuesta es "esta bien", decime que NO encontraste para criticar y por que.

### 7.1 Coherencia con lo canonizado

1. **DeepEval/TruLens DEFERRED a Fase 2.** SPEC_FB_CONTRACT_TEST_HARNESS_v1 ya tiene 30 fixtures Ciclope + 702 assertions. POL_AI_GOV_FINAL_OUTPUT_QUALITY exige Final Pass Premium. **¿Plan B Langfuse + ARQ jobs es suficiente o estoy creando un gap de calidad que va a explotar antes de Fase 2?**

2. **tsvector + HNSW + RRF para hybrid retrieval.** Mi SPEC_FB_RAG_SECURITY_FIREWALL_v1 cubre security (parser sandbox, salted tags, output firewall). Esta nueva capa de retrieval **¿requiere bumpear el SPEC RAG a v1.1 con C7 nuevo o requiere SPEC nuevo? ¿Hay tension entre el filtrado de chunks por content_risk_score (firewall) y el ranking por ts_rank_cd + cosine (retrieval)?**

3. **Frontmatter `queries_answered` con 5-10 preguntas via LLM.** P11 ARCH_AGENT_PRINCIPLES dice que el clasificador de aprendizaje a 3 destinos requiere prompt estructurado sobre Claude Haiku 4.5 con confidence threshold 0.80. **¿La generacion de queries para chunking debe pasar por el mismo gate o es separada? Si Cowork genera queries que no pasan threshold, ¿que pasa?**

4. **Hooks PreToolUse para bloquear writes al canonico.** Mi setup actual: Cowork escribe en OneDrive mirror, sync_*_indexa.ps1 mueve al canonico C:\dev\mwt-knowledge-hub. **¿El hook deberia bloquear el path del canonico o validar que el write venga del sync script? ¿Que pasa si el dev legitimamente necesita escribir directo al canonico (ej. configurar git, agregar .gitignore)?**

5. **CLAUDE.md <60 lineas + WIKI.md detallado.** Mi CLAUDE.md actual tiene 6 reglas inquebrantables + scope FaberLoom + 8 tipos taxonomia. **¿Todo eso cabe en <60 lineas o hay que partir? ¿Como se mantiene sincronizado CLAUDE.md (control) con WIKI.md (contract) cuando un cambio afecta ambos?**

### 7.2 Tensiones que pude haber pasado por alto

6. **RAG Firewall + Hybrid retrieval.** El firewall filtra chunks con `instruction_risk > 0.3` para output_external. ¿El BM25 puede traer chunks malicios que el firewall ya descarto si el operador hace una query con palabras especificas? **¿Hay manera de que el firewall y el retrieval se contradigan?**

7. **Lazy migration chunking + sync canonico.** Plan: cada archivo editado se re-chunkea. Pero los archivos viven en repo canonico, Cowork no escribe ahi. **¿La re-chunking dispara desde el sync script o desde un job ARQ que monitorea cambios? ¿Quien ordena?**

8. **`queries_answered` en frontmatter + curaduria 2 capas.** Las queries son contenido nuevo en cada archivo. **¿Pasa por curaduria USER (capa 1) o COMMITTEE (capa 2)? Si Cowork genera queries con LLM y un operador junior aprueba, ¿se promueve a CTX org o queda local?**

9. **Hooks layer + Charter/Mandato/CTX granular.** Estamos por agregar primitivas WS_, CTX_*, AGT_. Los hooks PreToolUse necesitan saber que prefijos son validos. **¿Los hooks se actualizan con cada nueva primitiva o son agnosticos del prefijo? Si son agnosticos, ¿como aprenden nuevas reglas?**

10. **Anti-rationalization tables (D4) + 14 principios ARCH (P0-P14, P16).** El swarm propone tablas de excusas comunes. **¿Estas tablas conviven con los principios ya canonicos o los reemplazan? ¿Anti-rationalization es un principio P17 nuevo o vive en otro lado?**

### 7.3 Calibracion de prioridades

11. **¿B -> A -> C es el orden correcto?** O **¿debo:**
    - **A primero (indexar swarm)** para que nadie pierda contexto entre sesiones, antes de cambiar enforcement
    - **C primero (schema retrieval)** porque es el cambio mas rapido y prueba inmediatamente que el plan funciona
    - **B + C en paralelo** porque son dominios distintos (Claude Code config vs Postgres schema)

12. **¿Hay decisiones del swarm que estoy diferiendo cuando deberia hacerlas YA?** Ejemplo: anti-rationalization tables aplican a Cowork sessions actuales. Si las difiero a "Sprint 4-5: Anti-rationalization + KB skills" como dice la tabla del swarm, estoy aceptando 4 sprints mas con el comportamiento actual de Cowork.

13. **¿Los costos consolidados de $0.20-$20/mes son creibles** o el swarm subestimo algo? Especificamente:
    - Storage overhead +0.3-0.5x texto en tsvector ¿escala bien con 100 tenants?
    - GPT-4o-mini judge para 5% sample ¿se mantiene ese precio en 6 meses?
    - LLM judge cost de $0.01-0.10 por evaluacion ¿incluye retry/fallback?

### 7.4 Casos de borde

14. **Operator junior subiendo doc al KB del tenant Sondel:**
    - Cowork detecta el upload via hook?
    - Aplica firewall (security) + chunking (D3) + queries_answered (D3) en orden correcto?
    - Si el doc tiene injection, queda quarantined; pero ¿que pasa con el frontmatter generado por LLM si el doc original era malicioso?

15. **Re-embed por drift detection (ARQ mensual):**
    - Detecta que 5% de chunks tienen drift > 0.08
    - Marca requires_rescan=TRUE
    - Pero ¿como se comunica con el firewall cuyo `firewall_ruleset_hash` tambien dispara requires_rescan?
    - ¿Hay 2 fuentes de truth para "este chunk necesita re-procesar"?

16. **Tenant cancela contrato (LGPD/Ley 8968):**
    - Borrado propaga a chunks + embeddings + quarantine + memoria + audit logs (con redaction)
    - Pero **¿que pasa con los `queries_answered` generados con LLM?** Si el tenant pago por la generacion, ¿son del tenant o de FaberLoom?
    - ¿Los gold samples derivados de outputs del tenant se borran tambien?

---

## 8. Formato de respuesta esperado

Tabla principal:

| Pregunta # | Hallazgo | Severidad (alta/media/baja) | Recomendacion concreta |
|---|---|---|---|

Mas prosa libre para tensiones inter-pregunta (ej: pregunta 6 + pregunta 14 son la misma raiz).

Al final:

```
## Veredicto del auditor

- ¿Plan integracion coherente con canonizado? [SI/PARCIAL/NO + razon]
- ¿Orden B -> A -> C correcto? [SI/RE-ORDENAR a X-Y-Z + razon]
- ¿Que paso por alto el plan? [bullets]
- ¿Que decision del swarm subestime en mi plan? [bullets]
- ¿Hay riesgo bloqueante para Sprint 0? [SI con detalle / NO]
- Score plan integracion: X.X / 10
```

NO concesiones. NO tablas vacias. Si todo te parece bien, decime explicitamente que NO encontraste para criticar y por que.

---

## 9. Lo que NO necesito

- Investigacion alternativa al swarm (ya tiene 80+ busquedas y 40+ casos production)
- Sugerir cambios al stack frozen
- Reconsiderar decisiones cerradas seccion 4
- Marketing-talk
- Listas neutrales sin recomendacion
- Score >= 9 reflexivo

## 10. Lo que SI necesito

- Tensiones entre swarm y canonizado (seccion 3)
- Casos de borde no obvios (seccion 7.4)
- Calibracion del orden B -> A -> C
- Costos del swarm validados o cuestionados
- Decisiones que estoy diferiendo cuando deberia hacer YA

---

**Fin del prompt auditor.**
