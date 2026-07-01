# IDX_FB_FOUNDATION_BETA - Working copy raiz workspace

id: IDX_FB_FOUNDATION_BETA
version: 1.0.3
status: VIGENTE (working copy - verdad canonica vive en `docs/faberloom/IDX_FB_FOUNDATION_BETA.md`)
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: INDEX
stamp: VIGENTE - 2026-05-17 (v1.0.1 nota aclaratoria sub-agentes; cuerpo sin cambios firmados)
aplica_a: [FaberLoom]
canonical_at: docs/faberloom/IDX_FB_FOUNDATION_BETA.md
mirror_relationship: working_copy

---

## Proposito

Este es el indice maestro del proyecto FaberLoom Foundation Beta. Lista todos los artefactos producidos durante la planeacion (sesion Cowork 2026-05-01), su status actual, y el orden recomendado de lectura para cualquier agente o persona que retome el trabajo.

**Si arrancas un chat nuevo:** copia `PROMPT_KICKOFF_FOUNDATION_BETA.md` (en raiz del workspace) como prompt inicial - ese archivo es autocontenido y trae el contexto completo.

---

## Orden de lectura recomendado

### Para retomar planeacion

1. **`PLAN_FABERLOOM_FOUNDATION_BETA_v1.3.1.md`** - contrato firmado de ejecucion (13 sprints). Empieza por aca.
2. **`IDX_FB_FOUNDATION_BETA.md`** <- este archivo. Mapa de todo.
3. **`PROMPT_KICKOFF_FOUNDATION_BETA.md`** - prompt para arrancar nuevo chat con contexto completo.
4. **`docs/anexos/kimi_skills/INVENTARIO_MWT_FABERLOOM_SKILLS.md`** - 188 skills del ecosistema skills.sh catalogadas por Kimi (referencia, no instalacion).

### Para implementacion (cuando arranque Sprint 1A)

5. **`docs/CLAUDE.md`** - reglas inquebrantables del repo
6. **`docs/RW_ROOT.md`** - taxonomia + meta-reglas KB
7. **`docs/ARCH_AGENT_PRINCIPLES.md`** - 14 principios fundacionales
8. **`docs/faberloom/SPEC_FB_AUTH_TENANT_RBAC_v1.md`** - auth canon
9. **`docs/faberloom/SPEC_FB_SYSTEM_TOPOLOGY_v1.md`** - topologia canon
10. **`docs/faberloom/SPEC_FB_TENANT_BOOTSTRAP_SEED_v1.md`** - bootstrap canon
11. **`docs/faberloom/SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1.md`** - evidence bundle 18 campos canon
12. **`docs/faberloom/ENT_FB_RFQ_EXCEPTION_TAXONOMY_v1.md`** - 15 exception codes canon
13. **`docs/faberloom/ENT_FB_RFQ_REPLAY_SET_v1.md`** - replay set canon
14. **`docs/faberloom/SPEC_FB_VOICE_HUMANIZER_v2.md`** - Voice Humanizer v2.1: en E1-E2 colapsado a bloque de estilo + few-shot gold samples; resolucion property-by-property DIFERIDA a E3+
15. **`docs/faberloom/SCH_FB_VOICE_PROFILE_v1.md`** - schema YAML del sabor user (capa L4)
16. **`docs/faberloom/SCH_FB_WS_INSTRUCTIONS_v1.md`** - DEFERRED E3+ (enmienda Voice v2.1) - schema instrucciones modulacion workspace (capa L3)
17. **`docs/faberloom/POL_FB_VOICE_RESOLUTION_v1.md`** - DEFERRED E3+ (enmienda Voice v2.1) - politica resolucion property-by-property + filtros + audit trace

---

## Artefactos del proyecto

### A. Plan y patches (en raiz del workspace)

| Archivo | Status | Iteracion | Notas |
|---|---|---|---|
| `docs/faberloom/PLB_FB_FOUNDATION_BETA_v1.md` | **FIRMADO - CANONICO** | v1.0 (plan label v1.3.1-FIRMADO) | Contrato de ejecucion para Alejandro. 13 sprints, camino C, factories minimal con 14 limites duros, multi-canal nativo, 5 roles tenant, resiliencia full. Seccion 5.B con 3 condiciones operativas de kickoff |
| `PLAN_FABERLOOM_FOUNDATION_BETA_v1.3.1.md` (raiz) | working copy | mirror | Mirror funcional del canonico para acceso rapido CEO |
| `docs/faberloom/IDX_FB_FOUNDATION_BETA.md` | **VIGENTE - CANONICO** | v1.0 | Indice maestro del proyecto |
| `docs/faberloom/PLB_FB_KICKOFF_PROMPT_v1.md` | **VIGENTE - CANONICO** | v1.0 | Prompt autocontenido nuevas sesiones |
| `docs/MANIFIESTO_APPEND_20260501_FOUNDATION_BETA_FIRMADO.md` | **VIGENTE** | v1.0 | Traza completa iteraciones + canonizacion |
| `audit/iteraciones_foundation_beta/PLAN_FABERLOOM_BETA_INICIAL_v1.3.md` | DEPRECATED | v1.3 | Renombrado a Foundation Beta. Archivado para auditoria |
| `audit/iteraciones_foundation_beta/PLAN_FABERLOOM_BETA_INICIAL_v1.2.md` | DEPRECATED | v1.2 + v1.2.1 microcorrecciones | Archivado para auditoria - 8 sprints, base minima |
| `audit/iteraciones_foundation_beta/PLAN_FABERLOOM_BETA_INICIAL_8_SPRINTS_v1.md` | DEPRECATED | v1.0 | Plan inicial pre-canon `docs/faberloom/`. Archivado para auditoria |
| `audit/iteraciones_foundation_beta/PLAN_FABERLOOM_BETA_INICIAL_PATCH_v1.0_to_v1.1.md` | DEPRECATED | v1.1 patch | Patch v1.0->v1.1 tras leer canon `docs/faberloom/`. Archivado para auditoria |

### B. Pendientes de producir (acordados implicitamente, esperando luz verde)

| Archivo planeado | Status | Contenido |
|---|---|---|
| `PLAN_FABERLOOM_FOUNDATION_BETA_v1.3.2.md` | PENDIENTE | Patch v1.3.1 -> v1.3.2 incorporando: (a) pgvector + embedding local self-hosted (`multilingual-e5-base`); (b) 10 skills system precargadas en Library; (c) 2 skills MWT custom precargadas en tenant MWT |
| `LIBRARY_SKILLS_SYSTEM_v1.md` | PENDIENTE | SkillSpec completo (prompt + schema input/output + modelo + cost cap + timeout) de las 10 skills system Library + 2 MWT custom |
| `RECOPILAR_SKILLS_FUTURAS_v1.md` | PENDIENTE | 10 skills propias gap critico con preguntas concretas para recopilar info en proximas sesiones |
| `MANIFIESTO_APPEND_20260501_FOUNDATION_BETA_FIRMADO.md` | PENDIENTE | Traza de iteraciones v1.0 -> v1.3.1-FIRMADO para auditoria |

### C. Mockups (en `docs/anexos/mockups/`)

| Archivo | Status | Descripcion |
|---|---|---|
| `mesa_de_control_v3.html` | Historico | 3ra iteracion mockup, base v4 |
| `mesa_de_control_v4.html` | Historico | 4ta iteracion, base v5 |
| `mesa_de_control_v5.html` | **REFERENCIA** | Layout editorial-warm canonico para Mesa de Control E1 |
| `mesa_e1_faberloom.html` | **REFERENCIA** | Layout Bloomberg-terminal alternativo (hay que limpiar semantica multi-agente) |
| `mesa_styles_compare.html` | Referencia | Comparacion side-by-side e1 vs v5 |
| `mesa_styles_picker.html` | **CREADO esta sesion** | Mockup interactivo skin picker (e1/v5) + theme picker (light/dark) - para que CEO decida que skin usar en S5 |

### D. Investigacion Kimi (en `docs/anexos/kimi_skills/`)

| Archivo | Tipo | Notas |
|---|---|---|
| `INVENTARIO_MWT_FABERLOOM_SKILLS.md` | INVENTARIO | 188 skills consolidadas del ecosistema skills.sh categorizadas para MWT/FB. Fuente para identificar gaps propios |
| `plan.md` | Plan trabajo Kimi | Contexto del analisis |
| `research/dim01_workflow_disciplina.md` | Research D1 | Workflow + disciplina |
| `research/dim02_marketing_seo_copy.md` | Research D2 | Marketing + SEO + copywriting |
| `research/dim03_browser_scraping.md` | Research D3 | Browser automation + scraping |
| `research/dim04_pm_saas_growth.md` | Research D4 | PM + SaaS growth |
| `research/dim05_ecommerce_amazon_fba.md` | Research D5 | Ecommerce + Amazon FBA |
| `research/dim06_document_processing_b2b.md` | Research D6 | Document processing B2B |
| `research/dim07_knowledge_rag_vector.md` | Research D7 | Knowledge + RAG + vector |
| `research/dim08_b2b_sales_crm.md` | Research D8 | B2B sales + CRM |
| `research/dim09_multi_agent_orchestration.md` | Research D9 | Multi-agent orchestration (PARA REFERENCIA, NO IMPLEMENTAR - viola single-agent E1) |
| `research/dim10_code_quality_backend.md` | Research D10 | Code quality + backend |
| `research/dim11_data_analysis_forecasting.md` | Research D11 | Data analysis + forecasting |
| `research/dim12_compliance_legal_latam.md` | Research D12 | Compliance + legal LATAM |

---

## Trazabilidad de iteraciones del plan

| Version | Fecha | Hito | Producido por |
|---|---|---|---|
| v1.0 | 2026-05-01 | Plan inicial 8 sprints - pre-canon `docs/faberloom/` | Cowork sesion 1 |
| v1.1 | 2026-05-01 | Patch tras leer 6 specs canon `docs/faberloom/` (auth, topology, seed, evidence bundle, exception taxonomy, replay set) | Cowork tras review CEO |
| v1.2 | 2026-05-01 | Consolidado autocontenido - TIER 1 a 12 items firmados - Hostinger KVM 8 confirmado | Cowork tras feedback CEO |
| v1.2.1 | 2026-05-01 | Microcorrecciones editoriales (fallback Telegram out, schema 11 tablas, replay_set no bloquea S1) | Cowork tras review CEO |
| v1.3 | 2026-05-01 | Re-scope CEO: factories minimal + multi-usuario + multi-email + Voice Profile + resiliencia C, 13 sem | Cowork tras input CEO |
| v1.3.1 | 2026-05-01 | Renombre a Foundation Beta + 14 limites duros Skill Factory + Sprint 1A/1B + correcciones | Cowork tras review cruzada CEO+ChatGPT |
| **v1.3.1-FIRMADO** | **2026-05-01** | **CEO firma + 3 condiciones operativas kickoff (worker queue congelado S1A, Resend <5%, restore test pre-S10)** | Cierre sesion |
| v1.3.2 (pendiente) | TBD | + pgvector embedding local + 10 skills system Library + 2 skills MWT custom | Pendiente luz verde CEO |

---

## Resumen ejecutivo del plan firmado

### Identidad

- **Nombre:** FaberLoom Foundation Beta (no "Beta Inicial")
- **Plazo:** 13 sprints x 1 semana = 13 semanas
- **Alcance:** plataforma configurable para PYME B2B con multi-email, multi-usuario, Voice Profile, factories minimal, resiliencia C
- **Wedge unico:** cotizacion safety footwear B2B con HITL absoluto
- **Testers:** 5 usuarios (1 tenant MWT con CEO+Alejandro, 3 tenants amigos)

### Stack

- **Hosting:** Hostinger KVM 8 + Docker Compose 12 containers
- **Backend:** FastAPI + Pydantic AI + worker (Celery o ARQ - Alejandro elige <1 dia, congelado S1A)
- **DB:** Postgres 16 + RLS + pg_trgm + FTS + **pgvector con embedding local** (pendiente v1.3.2)
- **Frontend:** Next.js 15
- **LLM:** LiteLLM gateway -> Anthropic only (Sonnet 4.6 + Haiku 4.5)
- **Email:** Gmail OAuth + IMAP/SMTP custom + Resend fallback (<5% mensual)
- **WhatsApp:** Meta Cloud API directo, cuenta unica MWT
- **Observabilidad:** Langfuse + Loki + Prometheus + Grafana
- **Storage:** filesystem KVM + MinIO + backup pg_dump diario + rsync S3 externo

### Arquitectura

- 5 roles tenant: Owner / Admin / Operator / Supervisor / Viewer
- Engine ejecutor generico que lee SkillSpec de DB con Pydantic dinamico
- Multiples agentes configurables por tenant con ejecucion single-agent por task (NO multi-agente, NO sub-agentes JERARQUICOS EN RUNTIME, NO orquestacion entre agentes principales)
- Skill Factory minimal (wizard 5 pasos + sandbox + 14 limites duros)
- Agent Factory minimal (wizard 4 pasos)
- Voice Profile completo (persona + tono + glosario + saludo + firma por user)
- Resiliencia C: circuit breakers + retry + DLQ + skill+agent fault isolation + chaos tests + aislamiento por tenant en worker

### Workflow E1

```
WhatsApp/Email entrante -> Tier 0 deterministic -> classify_rfq (Haiku) -> 
retrieve_kb (FTS+pg_trgm+pgvector) -> generate_quote (Sonnet) -> 
format_output (Sonnet) -> HITL Mesa de Control -> operator APROBAR/EDITAR/RECHAZAR -> 
envio desde buzon origen del tenant
```

SLO: P95 inbound->pending < 12s. Costo medio < USD 0.30/cotizacion. Disponibilidad >=95%.

### Metricas y kill criteria

Gate de salida E1 requiere:
- >=4/5 testers >=10 tareas en sem 6
- >=4/5 testers usan sin insistencia CEO 4 sem consecutivas
- >=60% aprobados sin edits ultimas 30
- Costo <USD 0.50/tarea
- 0 incidentes privacy/irreversibles
- >=5x reduccion tiempo
- Disponibilidad >=95%
- >=2/3 tenants amigos crearon >=1 agente o skill custom

8 kill criteria explicitos en plan v1.3.1 seccion 4.

---

## TIER 1 - 17 items inquebrantables (resumen)

1. RLS Postgres por tenant
2. HITL absoluto cero auto-send
3. N0-N2 only
4. Audit log append-only con actor_role_at_decision
5. Evidence bundle 8+5 campos + SHA-256
6. Token Ledger simple
7. 5 roles tenant activos
8. Backup diario + restore test demostrado
9. 10-15 RFQs golden CEO
10. Anthropic-only
11. Mesa de Control limpia (sin multi-agente, pool L3, k-anon)
12. Metrica salida: >=4/5 testers usan sin insistencia 4 sem
13. Multi-email nativo (Gmail OAuth + IMAP custom)
14. Voice Profile completo
15. Agent Factory + regla single-agent por task
16. Skill Factory con 14 limites duros
17. Resiliencia full (camino C)

**Pendiente (v1.3.2):** TIER 1 #18 = pgvector + embedding local self-hosted

---

## Decisiones CEO firmadas (kickoff Sprint 1A)

20+1 decisiones documentadas en plan v1.3.1 seccion 5. Las criticas:

1. Hostinger KVM 8 - no reabrir
2. Anthropic-only LLM - no OpenAI/Voyage/Whisper sin MANIFIESTO_APPEND
3. 5 roles tenant - Owner/Admin/Operator/Supervisor/Viewer
4. Email outbound desde buzon origen (no `noreply@faberloom.io`)
5. Voice Profile - persona+tono+glosario+saludo por tenant; firma por user
6. Agent Factory - multiples agentes configurables, single-agent por task
7. Skill Factory - clonar/zero + sandbox obligatorio + 14 limites duros + promote solo Owner/Admin
8. Engine ejecutor - Pydantic dinamico + timeout + cost cap + sin tools externas
9. Resiliencia camino C completo
10. Plazo 13 semanas
11. Workflow validado E1 - solo cotizacion safety footwear B2B
12. Replay set - 10-15 S3, 40 S8 obj, 60 gate E2
13. Worker queue - Alejandro elige Celery o ARQ, congelado S1A
14. Resend fallback - <5% outbound mensual
15. Restore test - demostrado antes de S10

---

## Restricciones inquebrantables (no reabrir)

- Hosting (Hostinger KVM 8)
- Stack (FastAPI + Next.js + Postgres + Redis + LiteLLM + Anthropic)
- Wedge safety footwear
- Anthropic-only
- HITL absoluto
- Single-agent por task
- No DMS
- No AI_GOV runtime
- No sub-agentes JERARQUICOS EN RUNTIME (ver nota aclaratoria abajo)
- No marketplace cross-tenant
- No skills compartidas entre tenants
- No tools externas en skills
- No code execution
- No HTTP externo en runtime de skills
- No cross-tenant access

### Nota aclaratoria sub-agentes (v1.0.1 - 2026-05-17)

La restriccion "No sub-agentes" se refiere especificamente a **composicion jerarquica orquestada en runtime entre agentes principales** durante E1. NO niega la existencia de los 10 **sub-agentes atomicos** canonizados en `ENT_FB_SUB_AGENTS_LIBRARY_v1.md` y el principio P16 (`ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1.md`).

Reconciliacion completa en `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1.md` seccion 3.1:

- **E1 (operativo hoy):** los 10 sub-agentes existen como **standalone individuales** invocables uno a la vez. Cadena lineal de skills via flow DAG (`SCH_FB_FLOW_DAG.md` v2.0) es la composicion permitida.
- **E2 (habilitable):** composicion jerarquica AG_PRINCIPAL -> [AG_SUB_*] con `feature_flag.allow_agent_composition=true` per-tenant. Max 2 niveles (P16). Sub-agente invocando sub-agente sigue bloqueado permanentemente (NeurIPS 2025 MAST 41-86.7% fallo).
- **E3+ (evaluable):** orquestacion cross-agent (un agente principal llamando otro) con governance Comite.

Drift entre esta restriccion y P16 documentado en `AUDIT_NEXOS_AI_DELTAS_v1_1.md` seccion 4 drift #3.

---

## Proximos pasos concretos

### Inmediato (esta semana, antes de kickoff Sprint 1A)

1. CEO confirma 3 amigos B2B con incentivo + commitment verbal
2. CEO inicia tramite WhatsApp Business MWT con Meta (3-7 dias)
3. CEO inicia tramite Google OAuth approval para FaberLoom (1-2 sem)
4. CEO inicia redaccion DPA legal con abogado (entrega target inicio S10)
5. CEO pre-cura `client_map.xlsx` MWT - entrega lunes S4

### Pendiente para Cowork (proxima sesion)

1. Producir `PLAN_FABERLOOM_FOUNDATION_BETA_v1.3.2.md` con +pgvector embedding local +10 skills system +2 skills MWT custom
2. Producir `LIBRARY_SKILLS_SYSTEM_v1.md` con SkillSpec completo de las 10 skills (prompt + schema + modelo + cost cap + timeout)
3. Producir `RECOPILAR_SKILLS_FUTURAS_v1.md` con 10 skills gap critico + preguntas
4. Producir `MANIFIESTO_APPEND_20260501_FOUNDATION_BETA_FIRMADO.md` con traza iteraciones

### Implementacion (cuando arranque Sprint 1A)

Ver Sprint 1A en plan v1.3.1 seccion 3.

---

## Notas para proxima sesion / chat nuevo

Si retomas trabajo:

1. **Leer primero:** `PLAN_FABERLOOM_FOUNDATION_BETA_v1.3.1.md` completo
2. **Leer este indice:** `IDX_FB_FOUNDATION_BETA.md` (este archivo)
3. **Leer SPEC reconciliacion E1/E2:** `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1.md` para entender las restricciones operativas vs capacidades arquitectonicas
4. **Si vas a tocar shell/UI:** revisar `POL_FABERLOOM_SURFACE_CONTRACT.md` v0.2 (nota alineacion naming Workspace=SpaceLoom)

---

## Changelog

| Version | Fecha | Cambio |
|---|---|---|
| v1.0.3 | 2026-06-23 | FB-STD-CODEX-2026-06-23-01: fix mecánico de refs colgantes `docs/*` → `docs/faberloom/*` para seis artefactos canon. |
| v1.0.2 | 2026-06-15 | AUDIT-ROUTING-2026-06-14: corregido id INDEX_FABERLOOM_FOUNDATION_BETA → IDX_FB_FOUNDATION_BETA. v1.0.1 → v1.0.2. |
| v1.0 | 2026-05-01 | Indice maestro inicial post plan firmado v1.3.1-FIRMADO. Archivo termina abruptamente en seccion "Notas proxima sesion" (truncamiento detectado 2026-05-17, no se arregla en este patch para minimizar scope) |
| v1.0.1 | 2026-05-17 | Nota aclaratoria al item "No sub-agentes" referenciando P16 + ENT_FB_SUB_AGENTS_LIBRARY_v1 + SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1. Cuerpo firmado del v1.0 sin cambios. Completado el truncamiento de "Notas proxima sesion" con bullets 2-4. Drift documentado en AUDIT_NEXOS_AI_DELTAS_v1_1 drift #3 |
