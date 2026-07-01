---
id: RESEARCH_AGENTES_CONSOLIDADO_2026_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma
type: research-note
stamp: VIGENTE 2026-06-01
fecha: 2026-06-01
agente: Cowork (consolidacion) + swarm Kimi (4 ejes con citacion verificable) + swarm Claude (research previo)
metodo: Investigacion paralela en 2 modelos (Kimi K2 + Claude sub-agentes), cross-verification por tiers de confianza, reconciliacion de conflictos
fuente: Repos GitHub, docs oficiales (Anthropic, LangChain), papers arXiv, benchmarks. Citas con URL/fecha/excerpt en los reportes Kimi fuente.
alcance: 4 ejes - memoria, context engineering, LangGraph, SDR B2B + insights cruzados + zonas de conflicto
nota: Sintesis de fuentes externas. NO contiene datos operativos MWT. Documento de decision de arquitectura.
reemplaza_parcial: RESEARCH_AGENTES_DEEP_DIVE_2026_v1 (incorpora correcciones; ver seccion "Correcciones")
relacionado_con:
  - RESEARCH_AGENTES_MEDIUM_ABR_MAY_2026_v1
  - RESEARCH_AGENTES_DEEP_DIVE_2026_v1
  - ARCH_AGENT_PRINCIPLES
  - SPEC_FB_AGENT_RUNTIME_STACK_v1
  - ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1
---

# Consolidado: Arquitectura de Agentes IA (2026)

Documento canonico que reconcilia dos investigaciones paralelas: un swarm de Kimi (4 ejes con citacion Claim/Source/URL/Date/Excerpt/Confidence + cross-verification + 10 insights cruzados) y un swarm de sub-agentes Claude (deep dive previo). Donde hubo conflicto, se documenta y se marca el nivel de confianza. Los reportes fuente de Kimi son mas rigurosos en trazabilidad y se tratan como la version primaria de los 4 ejes.

## TL;DR - Decisiones con nivel de confianza

| Eje | Recomendacion | Confianza | Cambio vs deep dive previo |
|-----|---------------|-----------|----------------------------|
| Memoria | **Mem0 self-hosted + Qdrant** (hot path). LangMem solo background (latencia ~60s). Graphiti/Zep si se necesita razonamiento temporal. | Alta | Refinado: grafo Mem0 tras paywall; LangMem descartado para sincrono por latencia, no por madurez |
| Context engineering | Estatico cacheado + dinamico en cola + **Restatement** (repeticion de prompt, formalizado por Google). Compactar a 60-70%. | Alta | Refinado: Restatement NO sirve en reasoning models; LLMLingua para comprimir |
| Orquestador | **LangGraph + Temporal** (patron prod). Pero arrancar SIN Temporal/Redis/LangSmith por costo. | Alta | Refinado: checkpointing != durable execution; race conditions horizontales necesitan Redis locks |
| SDR B2B | WhatsApp-first + RAG anclado a catalogo. Foco en **reactivacion/recompra**, no prospeccion fria. | Media-alta | Corregido: Apollo/ZoomInfo NO cubren compradores industriales LATAM; recambio 6-12m hace retencion > adquisicion |

## Correcciones al deep dive previo (RESEARCH_AGENTES_DEEP_DIVE_2026_v1)

1. **Mem0 grafo (Mem0g) esta detras de paywall ($249/mo, tier Pro), y no existe en OSS.** El deep dive no lo capto. Para grafo, Zep Flex (~$25/mo) es ~10x mas barato. Mem0 OSS = vector + KV, sin grafo.
2. **LangMem tiene ~300x la latencia de Mem0** (p95 ~60s vs ~200ms; Atlan citando arXiv:2504.19413). Se descarta para retrieval sincrono no por inmadurez sino por latencia. Sirve solo como background manager.
3. **LangGraph checkpointing != durable execution automatico.** Requiere deteccion manual de fallo + re-invocation. Ademas, en deployments horizontales hay race conditions (dos workers cargan el mismo checkpoint) que exigen Redis locks por thread_id (solucion en blogs, no en docs oficiales).
4. **Apollo + Clay NO es base suficiente para calzado industrial MX-CO.** La mayoria de compradores industriales LATAM no estan en Apollo/ZoomInfo. La estrategia correcta es waterfall enrichment via Clay con fuentes locales + foco en cuentas existentes.

---

## Eje A - Memoria

### Comparativa (datos verificados Kimi, jun 2026)

| Dimension | Mem0 | Zep/Graphiti | Letta | LangMem |
|-----------|------|--------------|-------|---------|
| Modelo | Vector + KV (+grafo Mem0g Pro $249/mo) | KG temporal bi-temporal (Neo4j) | 3 tiers OS (core/recall/archival), agent-managed | Semantica/episodica/procedural, LangGraph Store |
| Extraccion | Pipeline LLM + ciclo A.U.D.N. (Add/Update/Delete/Noop) | Grafo incremental, invalida facts por contradiccion (t_valid/t_invalid) | Agente decide via tool calls (consume tokens) | LLM manager (hot + background) |
| Latencia retrieval | ~200ms p95 | sub-200ms (Cloud) | variable (tool calls) | ~60s p95 (solo background) |
| Multi-tenant | user_id/agent_id/org_id (storage-layer) | group_id; Cloud nativo | manual (orientado multi-agent) | namespace tuples (org/user/thread) + RLS, el mas maduro |
| MCP | OpenMemory MCP (beta) | Graphiti MCP v1.0 (Nov 2025, produccion) | no nativo | no (via LangGraph tools) |
| LangGraph | via REST (no nativo) | via MCP/REST | ecosistema propio | first-class nativo |
| Costo self-hosted ~100K mem/mes | $200-300 infra (sin grafo) | $200-300 infra (con grafo temporal) | $100-200 | $100-200 (LangGraph-only) |

### Hallazgos clave
- **Benchmarks vendor-disputed, sin fuente unica de verdad.** Mem0 reporta 92.5% LoCoMo; terceros 62-68%. Zep reporto 84% -> Mem0 lo corrigio a 58.44% -> Zep replico 75.14%. Las unidades difieren (tokens/retrieval vs tokens/conversation). CONCLUSION: medir con datos propios, no con cifras de vendor.
- **Write-time gating > read-time filtering** (paper Zahn & Chana, arXiv:2603.15994): 100% vs 13% accuracy en adversarial; a 8:1 distractores read-time colapsa a 0%, write-time mantiene 100%. Mem0 ya lo implementa parcialmente (ciclo A.U.D.N.).
- **Zep tiene el modelo temporal mas completo** (bi-temporal: event time + ingestion time, invalidacion automatica). Ningun otro se acerca.

### Recomendacion
**Mem0 self-hosted + Qdrant** como hot path (retrieval interactivo ~200ms). Aislamiento: `user_id = "{tenant_id}:{user_id}"` + `metadata.tenant_id` + filtro storage-layer + RLS en PostgreSQL/Qdrant. **LangMem** opcional como background manager (consolidar insights post-conversacion). **Zep/Graphiti** solo si un caso exige razonamiento temporal (estado del cliente en el tiempo). **Letta** descartado para interactivo (cada operacion de memoria consume tokens y sube latencia).

---

## Eje B - Context engineering / Restatement

### Fundamento (verificado)
- **Context length degrada performance 13.9%-85% incluso con retrieval perfecto** (Du et al., arXiv:2510.05381, 91+ citas) - degrada aun reemplazando tokens irrelevantes por whitespace. Databricks Mosaic: precision cae tras 32K tokens.
- **Lost in the Middle** (Liu et al., Stanford/TACL 2024): curva U de atencion, el medio se ignora.
- Anthropic formaliza context engineering como la progresion natural del prompt engineering (curar el set optimo de tokens en inferencia).

### Restatement - formalizado con matiz critico
- **Google Research (Leviathan, Kalman, Matias; arXiv:2512.14982):** repetir el prompt (`<QUERY>` -> `<QUERY><QUERY>`) simula atencion bidireccional en arquitectura causal. Gana 47/70 benchmarks, 0 perdidas. Gemini Flash-Lite salto de 21% a 97% en retrieval medio-de-lista. NO aumenta latencia (solo alarga el prefill paralelizable).
- **MATIZ CLAVE: NO funciona en reasoning models** (o3, Claude thinking) - su chain-of-thought ya restatea internamente (5 wins, 22 ties). Aplicar restatement solo en modelos no-reasoning.
- Ya en produccion: Claude Code inyecta `<system-reminder>` y `<long_conversation_reminder>` para combatir instruction drift; OpenAI recomienda repetir instrucciones antes y despues del contenido.

### Prefix caching
- Anthropic: cache read = 0.1x input tokens (90% descuento). OpenAI: -80% latencia, -50% costo input. Requiere prefijo identico byte-a-byte (orden tools -> system -> messages). Tocar el system prompt entre turnos invalida el cache.

### Recomendacion implementable
1. Estatico (instrucciones, reglas, tool defs) AL PRINCIPIO con `cache_control`. Dinamico (input, tool outputs, estado) AL FINAL.
2. Prefix caching siempre que el prefijo estable sea >1K tokens reutilizado.
3. Auto-compaction a ~60-70% del window (no esperar al 95%), con directiva explicita de que preservar.
4. Restatement (repeticion) solo en modelos no-reasoning.
5. Scratchpad con XML tags (`<thinking>`, `<action>`, `<observation>`) - sirve ademas de audit trail.
6. LLMLingua para comprimir RAG context (2-20x, <2% degradacion) antes de enviar.
7. Medir el needle-in-haystack real de tu agente: el limite practico no es el context window anunciado.

---

## Eje C - LangGraph

### Estado y capacidades (verificado)
- ~400 empresas en produccion, 34.5M+ downloads/mes PyPI (Klarna, Uber, LinkedIn, JPMorgan). v1.0 GA oct 2025.
- Checkpointing (PostgreSQL prod), time-travel/replay (unico en el ecosistema), HITL nativo (`interrupt()` desde 0.2.31).
- Princeton HAL: el scaffold mueve performance hasta 30 puntos (mismo Claude Opus 4: 64.9% vs 57.6%). CrewAI ~3x token overhead.

### Limites sin resolver
- **Checkpointing != durable execution.** No hay recovery automatico (DLQ, fallback, re-invocation) - requiere capa adicional (Temporal).
- **Race conditions horizontales:** dos workers, mismo checkpoint -> Redis locks por thread_id.
- MCP via integraciones community (no nativo en core); A2A en desarrollo (Google ADK lidera).
- Version churn (breaking changes frecuentes de LangChain), type safety solo TypedDict (no runtime como Pydantic AI), costo standby LangGraph Platform ($0.0036/min idle).

### Recomendacion
**LangGraph para razonamiento + Temporal para durabilidad** es el patron de produccion (Temporal cuando el workflow >30s o toca 3+ sistemas externos; son complementarios, no sustitutos). Backend: PostgreSQL (checkpointer) + Redis (locks). PERO ver insight de costo: arrancar SIN Temporal/Redis/LangSmith hasta que el costo de un fallo supere el de la infra. Multi-tenancy se implementa a mano (thread_id = `{tenant_id}:{conversation_id}` + RLS).

---

## Eje D - SDR B2B (calzado industrial MX-CO)

### Realidad del mercado (verificado)
- Mercado calzado industrial Colombia: ~$52.56M USD (2025) -> $104.9M (2034), CAGR 7.94% [proyeccion a 8 anos, baja confianza]. Mexico 2do de LATAM.
- Demanda inelastica por obligacion legal del empleador (NOM-017-STPS-2008 Mexico; Resoluciones Min. Trabajo Colombia). **Recambio cada 6-12 meses -> retencion > adquisicion fria.**
- Compradores heterogeneos: grandes cuentas compran directo (CEMEX, Grupo Mexico, Ecopetrol, Grupo Argos); PYMEs via distribuidores; canal fragmentado (distribuidores regionales + tiendas de seguridad industrial).
- **Datos B2B industriales LATAM escasos en Apollo/ZoomInfo** -> waterfall enrichment via Clay con fuentes locales.

### Canal y compliance
- **WhatsApp es el canal dominante** (94.3% penetracion MX, 85%+ CO; conversion 5-15%, 3-5x email). Costo: ~$0.0144/msg Colombia, ~$0.0351/msg Mexico.
- Opt-in obligatorio: LFPDPPP + PROFECO (Mexico), Ley 1581/2012 + SIC (Colombia). **EU AI Act (ago 2026):** disclosure de IA en outbound + label machine-readable.
- Modelo hibrido AI+humano supera AI-only (2.3x revenue con 63% menos reuniones). SaaStr: 15-20h/semana de supervision para calibrar.

### Guardrails (critico)
RAG anclado a catalogo verificado (`catalog.json`: modelo, SKU, normas CON certificado real, tallas, lead time). Umbral de confianza (<0.75 -> "verifico con el equipo" + escala). Lista blanca de certificaciones (mencion fuera de lista -> escala forzado). Un agente que inventa certificacion ATEX = responsabilidad legal.

### Recomendacion
Foco en **reactivacion/recompra de cuentas existentes** (no prospeccion fria), WhatsApp-first, supervision humana alta al inicio. Stack minimo viable que encaje en presupuesto (ver insight 6): LangGraph + PostgreSQL single-instance + Mem0 OSS + Qdrant, SIN Temporal/Redis/LangSmith. El activo critico es el `catalog.json` - invertir 1 semana antes de tocar outreach.

---

## Insights cruzados (los mas accionables)

1. **Cadena causal write-time gating -> menos alucinaciones (3 ejes).** Almacenar sin gating mete ruido en retrieval -> empeora "lost in the middle" -> el LLM adivina entre ruido -> alucina. Gating al escribir reduce ruido -> mejora atencion -> baja alucinaciones. Mem0 (A.U.D.N.) ya lo hace.
2. **Desacoplar el SDR del grafo core (C+D).** El orquestador core (multi-tenant, durable) evoluciona lento; el SDR itera rapido (SaaStr: 47 iteraciones para calibrar). Si el SDR es un nodo del grafo principal, cada iteracion exige redeploy del orquestador. Correcto: SDR como sub-agente MCP/A2A desplegable independiente.
3. **Costo real vs presupuesto (A+C+D).** Arquitectura "correcta" completa (Mem0+LangGraph+Temporal+PostgreSQL+Redis+LangSmith) = ~$800-2000/mes infra. Budget SDR MX-CO ano 1 ~$22K-47K -> infra seria 20-50% del budget. Arrancar lean: sin Temporal/Redis/LangSmith; agregar cuando el costo de un fallo lo justifique.
4. **WhatsApp diluye el prefix caching (B+D).** System prompt corto + historial unico por thread = cache hit rate bajo. Para WhatsApp SDR la optimizacion de costo no es caching sino LLMLingua + modelos ligeros (Haiku/Flash) para follow-ups rutinarios.
5. **Sin benchmarks independientes en memoria NI en SDR (A+D).** El campo carece de metrologia. Construir benchmark interno propio (meeting-to-opportunity, tasa de alucinacion, CAC real vs baseline humano); no usar cifras de vendor para justificar ROI.
6. **Audit trail nativo = compliance EU AI Act anticipado (B+C+D).** Scratchpad ReAct (XML) + checkpointing LangGraph ya generan traza completa de cada decision. Disenar con scratchpad + checkpoints desde dia 1 resuelve explicabilidad antes de que sea obligatoria.
7. **"Filter early, filter often" - 4 filtros en serie (A+C).** SDR optimo filtra en 4 capas: (1) leads por ICP antes de enriquecer, (2) datos enriquecidos (salience-gated) antes de almacenar, (3) historial (input filters) antes del LLM, (4) output (guardrails) antes del prospecto.
8. **Formar el equipo en LangGraph ANTES del piloto (C+D).** 1-2 semanas de ramp. Hacerlo durante la Fase 1 del SDR convierte el piloto en experimento de framework, no de producto.

## Zonas de conflicto sin resolver
- **LoCoMo Mem0 92.5% vs terceros 62-68%:** persistente. Mem0 uso algoritmo nuevo (abr 2026) no replicado; unidades de medicion difieren. Evaluar con datos propios.
- **LangGraph + Temporal: complementarios** (Temporal = execution/durabilidad; LangGraph = reasoning/tool-routing), no sustitutos.
- **MCP en LangGraph:** funciona via community integration, no es native-first como Pydantic AI/OpenAI SDK. Hay "abstraction cost".
- **Context Length Tax intrinseco:** Du et al. demostro que la longitud degrada aun con retrieval perfecto; causa raiz no entendida. Mitigacion parcial: recite-then-solve (+4% RULER).

## Implicaciones para MWT / FaberLoom
(Validar contra ARCH_AGENT_PRINCIPLES y SPEC_FB_AGENT_RUNTIME_STACK_v1)
- **Mem0 self-hosted** como capa de memoria de la plataforma (aislamiento tenant nativo, ~200ms). Prueba acotada.
- **Restatement** al runtime, con la regla de NO aplicarlo en modelos de razonamiento.
- **LangGraph como orquestador**, arrancando lean (sin Temporal/Redis/LangSmith) y con spec de namespacing tenant + Redis locks documentado para cuando escale horizontal.
- **SDR como sub-agente desacoplado** (MCP/A2A), foco recompra Marluvas/Tecmater, empezando por el `catalog.json`.
- Presupuestar **benchmark interno** antes de confiar en cifras de vendor.

## Fuentes clave (verificadas en reportes Kimi fuente)
- Memoria: github.com/mem0ai/mem0 ; github.com/getzep/graphiti ; arxiv.org/abs/2501.13956 (Zep) ; arxiv.org/abs/2603.15994 (write-time gating, Zahn & Chana) ; atlan.com (LangGraph Memory vs Mem0)
- Context: anthropic.com/engineering/effective-context-engineering-for-ai-agents ; arxiv.org/abs/2510.05381 (Du et al.) ; arxiv.org/abs/2512.14982 (Google, prompt repetition) ; Liu et al. Lost in the Middle (TACL 2024) ; docs Anthropic prompt caching
- LangGraph: github.com/langchain-ai/langgraph ; Princeton HAL ; Cordum.io / Temporal (patron LangGraph+Temporal)
- SDR: deepmarketinsights.com (mercado CO) ; Mazkara (WhatsApp LATAM) ; SaaStr / Product Growth (caso AI SDR) ; marco legal LFPDPPP / Ley 1581 / EU AI Act
- Reportes fuente (subidos por CEO, swarm Kimi): agentes_memoria_dim01, agentes_context_engineering_dim02, agentes_langgraph_prod_dim03, agentes_sdr_b2b_dim04, cross_verification, insight.

## Changelog
- v1.0 (2026-06-01): Creacion. Consolidacion de swarm Kimi (4 ejes + cross-verification + insights) reconciliado con deep dive Claude previo. Incorpora 4 correcciones. Autor: Cowork. Pendiente indexar a docs/ canonico via sync si el CEO lo aprueba.
