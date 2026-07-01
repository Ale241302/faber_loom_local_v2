# Prompt Auditor Round 2 - Integracion Swarm #6 al proyecto MWT/FaberLoom

**Para:** modelo de IA externo independiente (ChatGPT, Claude.ai sesion limpia, otro)
**De:** Alvaro (CEO Muito Work Limitada)
**Pedido concreto:** Round 2 de auditoria. Round 1 lo hizo Claude (el mismo modelo que ayudo a armar el plan, sesgo conocido). Encontro 3 huecos arquitectonicos + 1 error orden tactico. **Tu trabajo: encontrar lo que Round 1 paso por alto.**

NO repetir investigacion (swarm con 80+ busquedas, 40+ casos production).
NO repetir hallazgos del Round 1 (ver ANEXO A).
SI buscar lo que Round 1 minimizo o no vio.

---

## 1. Contexto del Round 2

| Round | Auditor | Resultado |
|---|---|---|
| 1 | Claude (mismo modelo armo plan) | 3 huecos arquitectonicos + 1 error orden. Score 7.5/10. Sesgo auto-confirmacion conocido |
| **2 (este)** | **Auditor externo independiente** | **Encontrar lo que Round 1 minimizo. Score independiente** |

Round 1 identifico:
- Coordinacion firewall + retrieval no resuelta (C7 RRF puede empujar chunks medio-riesgo)
- Plan B Langfuse NO sustituye Final Pass Premium canonico
- queries_answered etiquetado como contenido cuando es metadata
- Orden B->A->C contradictorio (material ya generado en raiz OneDrive)

**Round 2 ya tiene plan v2 corregido (seccion 7). Auditar el v2, no el v1.**

---

## 2. Contexto operativo (autocontenido)

CEO **Muito Work Limitada (MWT)** Costa Rica. Construyendo **FaberLoom**, SaaS B2B LATAM para PYMEs/fabricantes. Vertical inicial: cotizacion B2B calzado seguridad. MWT primer tenant validador.

### Stack frozen
FastAPI + Pydantic AI + Supabase (Postgres 16 + pgvector + RLS) + LiteLLM + Next.js 15 + ARQ/Redis + WhatsApp Business API + Railway/Fly.io + Langfuse + Letta self-host + UUIDv7 client-side.

### MVP cerrado (Foundation Beta)
60 dias, 13 sprints firmados, 2026-04-20 -> 2026-06-14. 1 agente, 3-5 herramientas, 2 workflows (cobranza + proformas). Single-agent, NO multi-agent (MAST). Compliance LATAM CO+MX+CR+PA+BR (LGPD). 4 tiers $19-$2499/mes segun data class N0-N4.

### KB del repo
540 archivos .md (430 operativos, 110 archivados). 10 dominios. 8 tipos canonicos: ENT/PLB/SCH/LOC/POL/IDX/SKILL/LOTE + especiales SPEC/ARCH/AUDIT. Patron sync: repo canonico C:\dev\mwt-knowledge-hub + mirror OneDrive via mirror_to_onedrive.ps1 + sync_*_indexa.ps1.

---

## 3. Estado canonizado pre-swarm (NO recomendar de nuevo)

### Arquitectura agentes
- ARCH_AGENT_PRINCIPLES.md v1.5 VIGENTE: 14 principios (P0-P14, P16). 3 objetos AgentSpec/Runtime/Memory. Draft-first invariante P3. P11 clasificador 3 destinos
- SPEC_FABERLOOM_AGENT_COMPOSITION_v1.1 DRAFT: Sealed/Open dual mode. 7 dimensiones Skill vs Agent. Autonomy ladder L0-L4. Authority mode
- ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1 (P16) VIGENTE: orquestadores delgados + sub-agents atomicos
- ENT_FB_AGENT_ARCHETYPES_v1 v2.0 VIGENTE: 7 arquetipos

### Runtime e infra
- SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT v1.0 DRAFT: 20 tablas FROZEN. UUIDv7. RLS 5 settings
- SCH_FB_TASK_ENTITY v2.0 VIGENTE: tasks como entidad de primera clase. 7 estados. HITL fields
- SPEC_FB_EVENTING_AND_OUTBOX_v1 VIGENTE: 4 capas (event_log + outbox + Redis Streams + WS). SHA-chain
- ENT_PLAT_ACTION_REGISTRY v1.1 VIGENTE: 53 acciones con DPA matrix LATAM
- SPEC_FB_CONTRACT_TEST_HARNESS_v1 VIGENTE: schemathesis + 30 fixtures Ciclope + 702 assertions

### Curaduria + Privacy + Audit
- ENT_FB_USER_LEARNING_MODEL_v1 + ENT_FB_COMMITTEE_OPERATING_MODEL_v1 VIGENTE: 2 capas
- POL_FB_KR_PRIVACY_TIERS_v1.1 + POL_DATA_CLASSIFICATION v1.2 + POL_AI_GOV_DATA_CLASS_PROVIDER v1.0 + POL_AI_GOV_FINAL_OUTPUT_QUALITY v1.0 + SPEC_AUDIT_MODULE sealed + SPEC_FB_AUTH_TENANT_RBAC_v1 VIGENTE
- **SPEC_FB_RAG_SECURITY_FIREWALL_v1 P0_APPROVED_CANDIDATE (score 9.1):** 6 componentes (parser sandbox, chunk metadata 4 scores, salted tags, retrieval policy, output firewall, P11_SECURITY_PRECHECK)

---

## 4. Decisiones cerradas no negociables (NO reabrir)

1. Single-agent en MVP (MAST evidence)
2. Letta self-host memoria
3. UUIDv7 client-side
4. Sealed/Open dual mode
5. Draft-first invariante absoluto P3
6. Curaduria 2 capas (USER + COMMITTEE k-anon >=5)
7. Charter termino tecnico interno; UI traduce por vertical
8. Foundation Beta 8 semanas firmada
9. Stack tecnico cerrado
10. Append-only estricto en audit_event/agent_run/draft_decision/connector_send_log
11. Final Pass Premium obligatorio outputs externos

---

## 5. Output Kimi Swarm #6 (resumen ejecutivo)

**D1 Hybrid Retrieval:** Phase 1 con tsvector + ts_rank_cd + pgvector HNSW + RRF Python async. NO esperar pg_textsearch. lpossamai 62%->84% precision. RRF k=60 valido B2B LATAM. NO LlamaIndex/LangChain ensemble (P99 12.20s vs 1.86s). RRF 15 lineas Python.

**D2 KB Quality:** DEFERRED DeepEval+TruLens a Fase 2 (~julio 2026). Plan B: Langfuse + ARQ jobs + LLM judge GPT-4o-mini 5% sample. Costo $0.20/mes/tenant = 0.2-0.3% MRR. Threshold: 7d precios, 30d fichas, 90d normativas. Drift cosine 0.08.

**D3 Chunking:** NO migracion masiva. Lazy migration con dual-index CREATE INDEX CONCURRENTLY. Recursive + sentence window default (400-512 tokens, 10-15% overlap). Hierarchical parent-child para POL/PLB criticos (child=256, parent=1024). queries_answered 5-10 preguntas via GPT-4.1 Nano ($0.50-1.60 corpus). Validacion via RAGAS, NO DeepEval.

**D4 CLAUDE.md:** Dual-surface CLAUDE.md (<60 lineas control) + WIKI.md (contract humano). Hooks como enforcement REAL (Anthropic envuelve CLAUDE.md con clausula dismissiva). PreToolUse + SessionStart + UserPromptSubmit. Anti-rationalization tables (Addy Osmani patron). Karpathy 4 + Reneza 6 reglas runtime.

**3 tensiones cross-dim resueltas por swarm:**
- D3 DeepEval para chunks vs D2 NO DeepEval -> RAGAS via Langfuse
- D1 GIN tsvector vs D3 dual-index -> complementarios
- D3 frontmatter extenso vs D4 <60 lineas -> aplica a CLAUDE.md no archivos KB

---

## 6. Plan de integracion v2 (CORREGIDO post Round 1)

### Cambios respecto al plan v1

| Cambio | Razon Round 1 |
|---|---|
| **Orden A -> B -> C** (no B -> A -> C) | Material ya generado en raiz OneDrive (4 sintesis + manifesto + research + roadmap). Bloquear writes con hooks ANTES de moverlo es contradictorio |
| **Anti-rationalization tables Sprint 0** (no sprint 4-5) | Cada sesion Cowork sin ellas = riesgo incidente 29-abr-style. Swarm subestimo urgencia |
| **C7 hybrid retrieval con weight por instruction_risk** | RRF puro empuja chunks medio-riesgo. Necesita penalizar por riesgo dentro del rango permitido C4 |
| **Final Pass Premium 100% obligatorio en externos** (no muestrear) | POL_AI_GOV_FINAL_OUTPUT_QUALITY exige check sincronico, no muestreo. Plan B muestrea SOLO internal_analysis |
| **SPEC_FB_RAG_SECURITY_FIREWALL bump v1.0 -> v2.0** (no v1.1) | C7 es cambio conductual mayor, no patch |
| **queries_answered como metadata** (no contenido) | NO pasa por curaduria 2 capas estandar. Gate propio: confidence > 0.80 + retrieval_score_avg para auto-aprobacion |
| **POL_FB_KR_PRIVACY_TIERS bump v1.2** | queries_answered son tenant-property, borrado propaga LGPD |
| **Hook PreToolUse con whitelist explicita** | TODO blocked = repo inoperable. Whitelist .git/, .gitignore, scripts/, hooks/, raiz no-docs/ |
| **Pipeline orden duro:** parse -> firewall -> chunking -> queries_answered | Sin orden estricto, queries pueden contaminarse de docs maliciosos |
| **hooks/config.json externo** (no hardcoded) | Cambio de primitiva = bump config, no edit codigo |

### Sprint 0 (denso post Round 1)

| Tarea | Esfuerzo | Bloquea Sprint 1 |
|---|---|---|
| Sesion Cowork: indexar 11 archivos ya generados al canonico via sync_kimi_swarm_6_indexa.ps1 | 1 sesion | NO |
| Bumpear ROADMAP_INTEGRAL_KB_4_CAPAS con 11 decisiones swarm + 7 hallazgos sorpresa | 0.5 sesion | NO |
| Bumpear CLAUDE.md a v2 (<60 lineas, Karpathy 4 + 5 reglas MWT consolidadas + multi-tenant 3 + ref WIKI.md) | 1h | SI |
| Crear WIKI.md (contract humano detallado, anti-rationalization table COMPLETA, conventions, sync protocol) | 2h | SI |
| Crear hooks/config.json + 3 hooks Python (sessionstart, pretooluse_canonical_protect con whitelist, userpromptsubmit_reminder) | 3h | SI |
| Test integracion hooks (provocar caso 29-abr-style, verificar bloqueo) | 1h | SI |
| Bumpear SPEC_FB_RAG_SECURITY_FIREWALL v1.0 -> v2.0 con C7 (hybrid retrieval con weight por instruction_risk) | 2h | SI Sprint 1 (donde se implementa C7) |
| Crear SPEC_FB_KB_QUALITY_MONITORING_v1 DRAFT (Plan B Langfuse + ARQ jobs + retry policy 2x con fallback) | 2h | NO bloquea, paralelo |
| Crear POL_CHUNKING_KB_v1 DRAFT (frontmatter schema + queries_answered como metadata + gate confidence + auto-aprobacion ENT/LOC) | 2h | SI Sprint 1 |
| Bumpear POL_FB_KR_PRIVACY_TIERS v1.1 -> v1.2 (queries_answered tenant-property, gold samples split) | 1h | NO |

**Total Sprint 0: ~14h Cowork + dev. Encaja en 2-3 sesiones.**

---

## 7. Hallazgos del Round 1 (NO repetir, referenciar)

Round 1 identifico estos hallazgos (severidad alta/media/baja). **NO los re-trabajes. Listados para que sepas que YA estan cubiertos en plan v2.**

| # | Hallazgo Round 1 | Severidad | Estado en v2 |
|---|---|---|---|
| 1 | Plan B Langfuse no sustituye Final Pass Premium | Alta | Final Pass 100% en externos, Plan B solo internal |
| 2 | RRF puede empujar chunks medio-riesgo | Alta | C7 con weight por (1-instruction_risk) |
| 3 | queries_answered sin gate confidence | Media | Gate confidence > 0.80 + auto-aprobacion ENT/LOC |
| 4 | Hook bloqueando TODO write canonico es impractical | Alta | Whitelist explicita .git/, scripts/, hooks/ |
| 5 | CLAUDE.md <60 lineas no cabe con todo propuesto | Media | Anti-rationalization COMPLETA en WIKI.md, ref desde CLAUDE.md |
| 6 | Misma raiz que P2 (firewall+retrieval) | Alta | Resuelto por #2 |
| 7 | Lazy migration debe disparar post-commit git canonico | Media | Git post-commit hook + ARQ |
| 8 | queries_answered NO es capa 1 USER (es metadata) | Media | Tratado como metadata con gate propio |
| 9 | Hooks deberian leer config externa | Baja | hooks/config.json |
| 10 | Anti-rationalization NO es principio P17 (es tecnica) | Baja | Vive en CLAUDE.md + WIKI.md, no promueve |
| 11 | Orden B->A->C contradictorio | Alta | Re-ordenado a A->B->C |
| 12 | Anti-rationalization aplica AHORA, no sprint 4-5 | Media | Movido a Sprint 0 |
| 13 | LLM judge sin retry/fallback subestima costos | Baja | Retry x2 con fallback documentado en SPEC quality monitoring |
| 14 | Pipeline orden critico: firewall ANTES de queries_answered | Alta | Orden duro: parse->firewall->chunking->queries_answered |
| 15 | requires_rescan dos fuentes truth (drift + ruleset) | Baja | OR + rescan_triggers[] array |
| 16 | queries_answered y gold samples necesitan politica borrado | Media | POL_FB_KR_PRIVACY_TIERS v1.2 con tenant-property |

---

## 8. Tu auditoria Round 2 - lo que necesito que critiques

Foco: **lo que Round 1 minimizo o no vio.**

### 8.1 Tensiones que pueden seguir en plan v2

1. **C7 con weight por (1-instruction_risk):** Round 1 propuso esto pero no especifico el `weight` factor. Si weight=0.5, chunk con risk=0.3 pierde 15% de score. Si weight=2.0, pierde 60%. **¿Cual es el factor correcto? ¿Hay riesgo de que weight muy alto descarte chunks legitimos por temas tabu (ej. "denuncia laboral" tiene high relevance + medium risk)?**

2. **Whitelist hook PreToolUse:** Round 1 listo .git/, scripts/, hooks/, raiz no-docs/. **¿Que falta en esa whitelist? ¿Que pasa con archivos como CLAUDE.md, WIKI.md, README.md que viven en raiz canonica? ¿Son docs/ o no-docs/? Si CLAUDE.md esta en raiz NO-docs/, el hook permite escribirlo desde Cowork? Eso defeats the purpose.**

3. **Pipeline orden duro:** Round 1 dijo parse->firewall->chunking->queries_answered. **¿Hay race conditions runtime real? Si firewall toma 30s para parser sandbox y chunking 5s, ¿se pueden paralelizar partes? ¿Que pasa si firewall falla pero chunking ya empezo en otra task ARQ?**

4. **queries_answered como metadata + tenant-property:** Round 1 dijo borrado propaga. **¿Como se exporta cuando tenant solicita portabilidad LGPD? ¿Formato? ¿Incluye solo las queries del tenant o tambien las que el sistema infirio sobre el tenant? ¿Hay diferencia legal entre "queries que el LLM genero leyendo MIS docs" y "queries que el LLM genero sobre MI"?**

5. **Anti-rationalization tables Sprint 0:** Round 1 movio a Sprint 0. **¿Como se actualizan cuando aparecen nuevas excusas? Si despues de 3 sesiones Cowork detecta una excusa nueva ("voy a verificar despues"), ¿hay flujo curaduria para agregar a la tabla? ¿O queda estatica como las 10 actuales?**

### 8.2 Decisiones diferidas que Round 1 valido como diferibles

6. **DeepEval+TruLens a Fase 2:** Round 1 valido. **¿Pero hay caso donde Plan B falla y necesitas DeepEval YA? Ejemplo: 1 tenant high-stakes (Government tier $999-2499) entra antes de Fase 2. ¿Plan B muestreo 5% es suficiente para auditoria regulatoria? ¿Hay obligacion contractual o regulatoria que el muestreo no cumple?**

7. **MCP gateway diferido:** Round 1 acepto diferir. **¿Pero si el equipo crece a 3 devs durante Foundation Beta (no post-MVP), el gateway pattern del swarm D4 (badwally/TheKnowledge) deberia implementarse YA o el SKILL_KB_GATEWAY draft cubre? ¿Hay plan B sin gateway si 2 devs editan canonico simultaneamente?**

8. **Late chunking diferido (incompatible jina-embeddings-v3):** Round 1 acepto. **¿Cuando OpenAI o Anthropic saquen embedding con late chunking equivalente (probable fines 2026), el plan tiene mecanismo para evaluar migracion o queda como deuda permanente?**

### 8.3 Preguntas especificas que Round 1 NO hizo

9. **Bump SPEC_FB_RAG_SECURITY_FIREWALL v1.0 -> v2.0:** Round 1 propuso v2.0 por cambio conductual. **¿Es bump correcto? POL_DETERMINISMO §1 v1.2 fuente unica conteos. ¿Bump a v2.0 invalida todas las metricas/tests del v1.0? ¿O retrocompat con flag de version?**

10. **hooks/config.json:** Round 1 propuso config externa. **¿Quien edita ese archivo? ¿Hooks pueden writable hooks/config.json (recursividad)? ¿Versionado del config?**

11. **Coordinacion swarm.indexa con sesion Cowork:** El plan v2 dice Sprint 0 incluye sesion Cowork con sync_kimi_swarm_6_indexa.ps1. **¿La sesion Cowork tiene los hooks PreToolUse instalados ANTES de la sesion (paso B) o el sync se hace ANTES de instalar hooks (paso A)? Hay dependencia circular si A->B->C estricto. ¿Como se rompe?**

12. **Costos consolidados $0.20-$20/mes:** Round 1 valido pero menciono que retry x3 multiplica 3-10x. **Plan v2 documenta retry x2 + fallback. ¿Multiplicador real es 2x o subestimado? ¿Hay mediciones empiricas en swarm o es estimacion?**

### 8.4 Casos de borde que Round 1 cubrio parcialmente

13. **Operator junior subiendo doc:** Round 1 dijo orden firewall->chunking->queries_answered. **Pero ¿que pasa si la red entre Cowork y firewall sandbox cae mid-pipeline? ¿Doc queda en limbo? ¿Hay rollback automatico? ¿queries_answered se generan parcialmente?**

14. **Tenant cancela contrato + LGPD borrado:** Round 1 dijo queries_answered son tenant-property. **¿Pero los embeddings de chunks contaminados (que pasaron firewall pero quedaron quarantined) tambien se borran? ¿Hay backup de quarantine que sobrevive al borrado?**

15. **Cowork escribe en mirror OneDrive durante outage canonico:** Si C:\dev\mwt-knowledge-hub no esta accesible (ej. SSD corrupto), Cowork sigue escribiendo en mirror. ¿El sync fallara cuando vuelva? ¿Hay reconciliacion automatica? ¿O se acepta perder cambios?

16. **Anti-rationalization table contiene "Mi cambio es mejor que el existente":** Es excusa valida tecnicamente en algunos casos (mejora real). ¿Como distingue el agente entre falsa rationalization y mejora legitima? Round 1 no lo cubrio.

---

## 9. Formato respuesta esperado

Tabla principal:

| # | Hallazgo Round 2 | Severidad (alta/media/baja) | Recomendacion concreta | Pasado por alto en Round 1? (SI/NO/PARCIAL) |
|---|---|---|---|---|

Mas prosa libre para tensiones inter-pregunta.

Al final:

```
## Veredicto Round 2

- ¿Plan v2 cierra los huecos del Round 1? [SI/PARCIAL/NO + razon]
- ¿Round 1 minimizo algo critico? [bullets]
- ¿Hay tensiones nuevas en plan v2 que no existian en v1? [bullets]
- ¿Score 7.5/10 del Round 1 es alto, bajo o correcto? [Mi score: X.X / 10]
- ¿Riesgo bloqueante Sprint 0 sigue? [SI con detalle / NO]
- Recomendacion final: ¿Sprint 0 puede arrancar? [SI/NO/CONDICIONAL]
```

NO concesiones. NO score >= 9 reflexivo. Si todo te parece bien, decime explicitamente que NO encontraste para criticar y por que.

---

## 10. Lo que NO necesito

- Repetir hallazgos del Round 1 (anexo A)
- Investigacion alternativa al swarm
- Sugerir cambios al stack frozen
- Reconsiderar decisiones cerradas seccion 4
- Marketing-talk
- Listas neutrales sin recomendacion

## 11. Lo que SI necesito

- Lo que Round 1 minimizo o no vio
- Tensiones nuevas en plan v2 (que no existian en v1)
- Calibracion de mi score 7.5 (¿alto, bajo, correcto?)
- Casos de borde Round 1 cubrio solo parcialmente
- Decisiones diferidas que parecen seguras pero tienen trampa

---

## ANEXO A: 16 hallazgos Round 1 (referencia, NO auditar de nuevo)

[Ver seccion 7 arriba para tabla completa]

Round 1 score: 7.5/10
Round 1 veredicto: PARCIAL coherente con canonizado. Re-ordenar B->A->C a A->B->C. 3 huecos arquitectonicos identificados. Riesgo bloqueante Sprint 0 = SI antes de aplicar correcciones. Plan v2 (este documento) ya aplica las correcciones.

---

**Fin del prompt auditor Round 2.**
