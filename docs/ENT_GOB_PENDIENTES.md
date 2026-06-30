# ENT_GOB_PENDIENTES
id: ENT_GOB_PENDIENTES
status: VIGENTE
visibility: [INTERNAL]
version: 16.0
stamp: VIGENTE — actualizado 2026-04-28
domain: Gobernanza (IDX_GOBERNANZA)
classification: ENTITY — Lista maestra de pendientes operativos por dominio
aplica_a: [MWT]

---

## FABERLOOM — Track activo (abierto 2026-04-14)

Nuevo producto SaaS B2B bajo Muito Work Limitada. Separado de Rana Walk. Track independiente.

> **Nota 2026-06-30 — STACK-01 resuelto:** el spike desktop SQLite/pywebview se registra como `SpaceLoom Spike E1` (no canónico) en `MANIFIESTO_APPEND_20260630_SPACELOOM_SPIKE_E1.md` y como `DEC-011` en `ENT_GOB_DECISIONES`. El track canónico sigue siendo Foundation Beta v1.3.1. Las acciones de rename/repo/domain son tracking interno del spike, no pendientes CEO-XX.

| Pendiente | Prioridad | Estado |
|-----------|-----------|--------|
| ENT_FABERLOOM_AGENT_BUILDER v1.0 indexado | P0 | ✅ DONE 2026-04-14 |
| Definir perfil empleado virtual — Gerente Financiero | P1 | PENDIENTE |
| Definir perfil empleado virtual — CEO / Gerente Comercial | P2 | PENDIENTE |
| Sprint MVP FaberLoom — Gmail OAuth + KB + Email Covey + Voice Profile | P0 | PENDIENTE — requiere decisión CEO sobre stack inicial |
| Groq vs RunPod L4 — decisión infra T1/T2 para MVP | P1 | PENDIENTE |
| ENT_FABERLOOM_INFRA.md — documentar decisiones infra (RunPod L4 $204/mes, Qwen 2.5 14B) | P2 | PENDIENTE |

### Open questions AUDIT_FABERLOOM (pre-build mockup v3.5, origen 2026-04-19 · refresh 2026-04-20)

**21 decisiones pendientes** surgidas construyendo. Bloquean cierre de SPECs FaberLoom antes de design partners. Fuente: `AUDIT_FABERLOOM_A7_CHAT_CONTRADICTIONS_v1.md` v1.1 §"Open questions to resolve before production" (post-mockup v3.5 con C17 agent lifecycle). Roadmap operativo de promoción: `PLB_FABERLOOM_KB_PROMOTION_v1.md` (target file por decisión).

| # | Pendiente | Ref | Prioridad |
|---|-----------|-----|-----------|
| 1 | Feedback taxonomy reconciliation — UI 5 radios vs A4/P6 6 códigos (drop `structure` y `scope` o exponer 6) | C1 | P0 |
| 2 | Bandeja polimórfica: 12 inbound kinds + per-kind action set | C14 | P0 |
| 3 | Chat como primitiva reusable vs destino exclusivo (embed en bandeja/skill-studio/agent-console) | C15 | P0 |
| 4 | LGPD data portability user-level (quién pide, qué incluye, frecuencia) | C16 | P0 |
| 5 | Tenant export format + retention policy | C16 | P1 |
| 6 | Approval chains: branching rules (Bruno→Ana O Carlos según monto) + escalation timeouts | C14 | P1 |
| 7 | Multi-output bundle approval: aggregate risk semantics (`max(reversibility)`) | C14 | P1 |
| 8 | Cluster scope en cross-skill propagation (A4 P12 dice 3 niveles, mock usa boolean) | C4 | P1 |
| 9 | Iteration auto-feedback policy (¿iterate dispara feedback automático?) | C5 | P1 |
| 10 | UserControlProfile structure (A5 lo nombra, nadie lo define) | C8 | P2 |
| 11 | Trigger_kind enum en AgentSpec (`word` / `event` / `schedule` para L4) | C9 | P2 |
| 12 | 5th scope pivote (business_entity_id) — decisión tras design partners ≥20-25% | C10 | P1 |
| 13 | Handoff packet UX (modal vs inline vs drag-drop al agente) | C11 | P2 |
| 14 | ModelFingerprint normalization (tabla + FK vs denormalizado por mensaje) | C12 | P2 |
| 15 | learningHeat 4º estado "gold" — formalizar en A4 o sacar de UI | C13 | P2 |
| 16 | SLA breach window semantics (single-sample vs 7 días sostenido) | C7 | P2 |
| 17 | Chat primitive: historial compartido entre standalone `/chat` y embed | C15 | P2 |
| 18 | Approval gate diferenciado para `autonomyCeiling` raise vs otros AgentSpec edits | C17 | P0 |
| 19 | Diff visual entre 2 versiones del AgentSpec (changeNote textual no alcanza) | C17 | P2 |
| 20 | Sandbox test del AgentSpec antes de publish (análogo skill-level ya existe) | C17 | P1 |
| 21 | Auto-rollback on quality regression post-publish (P13 probation logic) | C17 | P2 |

### Brechas KB detectadas en handoff (PLB_FABERLOOM_KB_PROMOTION §7)

Schemas/policies/entities que **deberían existir en la KB y no existen** (descubiertos construyendo el mockup).

| # | Falta | Tipo | Prioridad |
|---|-------|------|-----------|
| B1 | `SCH_CONNECTOR_ACCOUNT.md` con enum kinds (email/messaging/marketplace/marketplace_intel/kb_source/erp/calendar/identity_provider) + per-kind config | SCH | P1 |
| B2 | `SCH_AGENT_EVENTS.md` — catálogo canónico de los 11 events que disparan agentes (manual_trigger, rfq_received, lead_inbound, etc.) + payload schema | SCH | P1 |
| B3 | `SCH_DRAFT_STATE_MACHINE.md` — state machine A4 P7 formalmente exportable (10 states + transitions + reversibility rules) | SCH | P1 |
| B4 | `SCH_OVERLAY_POLICY.md` — central para skill 3-layer (manual_overlay + learned_overlay + sealed_base) | SCH | P0 |
| B5 | `POL_NOTIFICATION_ROUTING.md` — qué eventos LIVE van a bandeja vs solo log | POL | P1 |
| B6 | `ENT_PERSONAS_OPERATIVAS.md` — Bruno (operator) / Ana (admin) / Álvaro (owner) con JTBD por persona | ENT | P2 |

### Open questions post-Kimi Swarm #4 — LLM Orchestration (origen 2026-04-21)

**18 decisiones pendientes** del CEO que destraban promoción del spec `ENT_PLAT_LLM_ROUTING v2.0` y la creación de SPECs derivados (Research Swarm, Knowledge Broker, Invocation Registry). Fuente: `archivo/kimi_swarm_4_adaptive_routing.md` + sesión cowork 2026-04-21 post-validación.

| # | Pendiente | Propuesta agente | Prioridad | Unblocks |
|---|-----------|-----------------|-----------|----------|
| Q1 | Voice profile per-tenant (F1) o per-user (F2) | per-tenant F1 (solo owner edita), per-user F2 | P0 | SPEC_SKILL_COMPOSITION §Add-on 6 · SPEC_AGENT_COMPOSITION §18 |
| Q2 | Confirmar Hostinger KVM 8 specs (8 vCPU / 32 GB / 400 GB NVMe) | SÍ | P0 | SPEC_ARCHITECTURE_BLUEPRINT infra section |
| Q3 | Confirmar región KVM (US / EU / otro) y si virgen (sin workloads previos) | CEO define | P0 | Data residency matriz `tenant_model_allowlist` |
| Q4 | Single-node F1 o HA desde día 1 | Single-node F1 con LiteLLM HA interno (2 instancias same node); multi-node F2 | P1 | SPEC_ARCHITECTURE §HA |
| Q5 | Budget operativo LLM diario por tenant (pago vs gratis) | $20 pago / $5 gratis (aplicar daily caps en pg-boss + kill switch cost z>4) | P1 | SPEC_WORKFLOW_ENGINE anti-loop |
| Q6 | Cuentas Moonshot / DeepSeek / OpenAI ya existen (API keys disponibles) | Verificar con CEO | P0 | LiteLLM config inicial |
| Q7 | CEO-ONLY data: Anthropic + Ollama only, o también Kimi / DeepSeek | Anthropic + Ollama only (no CN por default); relajar por tenant explícito vía `tenant_model_allowlist` | P0 | Hard block en §F.2 del routing |
| Q8 | Pesos score compuesto F2: global vs per-tenant | per-tenant (evita cross-tenant poisoning Kimi A4) — aprender vía regresión logística con approval target | P2 | DEC-008 F2 — no urgente |
| Q9 | Shadow testing F2: gold samples sintético vs producción real | Sintético/redactado (Kimi A4 hard block); producción real requiere consentimiento explícito tenant | P2 | DEC-008 F2 |
| Q10 | Policy changes F2: quién aprueba cambios (4-eyes + firma digital SOC 2) | CEO MWT platform-wide; owner+admin 4-eyes tenant-level | P2 | DEC-008 F2 |
| Q11 | Research Swarm F1 (sin critic) o F2 | **F1 sin critic** — invocable desde Skill Studio wizard, DSL YAML, max_depth=2, budget=$0.50, timeout=15min, max_parallel=5 | P0 | SPEC_FABERLOOM_RESEARCH_SWARM_v1 |
| Q12 | Aceptar downgrade a tiered hardcoded F1 (ref DEC-006) | SÍ — Kimi LOW confidence justifica | P0 | Canoniza DEC-006 (ya en draft) |
| Q13 | Gate para promover a adaptive F2 (ref DEC-008) | 3 tenants × 5K drafts/mes × 3 meses | P1 | Canoniza DEC-008 (ya en draft) |
| Q14 | Swarm mechanism como primitiva S1 o capability S2 | S2 semana 3 (después de handoff pg-boss + Letta Sprint 1-2 funcional) | P1 | Sprint plan FaberLoom S2 |
| Q15 | MinIO para swarm scratchpads F1 | SÍ — scratchpads (sub-agent outputs) van a MinIO con TTL 7d; index en Postgres con pointer | P1 | SPEC_WORKFLOW_ENGINE §Scratchpad |
| Q16 | Knowledge Broker F1 modes (CONSOLIDATE / BRIEF / ENRICH) | Solo CONSOLIDATE en S2; BRIEF en S3; ENRICH diferido F2 | P1 | SPEC_KNOWLEDGE_BROKER_v1 |
| Q17 | `@swarm!` skip-planner shortcut (invocación directa sin plan-confirm) | F2 — F1 siempre Plan-Confirm-Execute para seguridad | P2 | SPEC_INVOCATION_REGISTRY §shortcuts |
| Q18 | Invocation handle: editable at creation, immutable after | SÍ — naming convention `@<skill-slug>` o `@<agent-slug>` + auto-suffix si colisión (admin override) | P1 | SPEC_INVOCATION_REGISTRY §naming |

**Bloqueo principal:** Q1, Q2, Q3, Q6, Q7, Q11, Q12 son P0 y destraban la mayoría de los SPECs derivados. Agente sugiere batch de respuestas CEO en una sesión única para acelerar.

---

## Sprint 9 — UI Batch (✅ DONE v2.0 — 2026-03-16)

**Objetivo:** construir todos los módulos de consola UI que tienen backend ya funcional. Sprint puramente frontend (AG-03). Sin nuevos endpoints POST — solo consumo de APIs existentes salvo excepciones anotadas.

**Bloqueador:** Sprint 8 DONE (MWTUser + JWT — PLT-02 depende de esto).

**Orden de ejecución dentro del sprint:**

| Orden | ID | Módulo | Dependencia interna | Notas |
|-------|----|--------|--------------------|----|
| 1 | PLT-06 | Liquidación Marluvas UI | Ninguna | Backend Sprints 1–5. P0 operacional. |
| 2 | PLT-04 | Nodos Logísticos UI | Ninguna | Backend Sprint 5. Debe ir antes que Transfers. |
| 3 | PLT-05 | Transfers UI | PLT-04 (Nodos) | Backend Sprint 5–6. Depende de Nodos en UI. |
| 4 | PLT-02 | Usuarios UI | Sprint 8 backend | Gestión multi-usuario. Depende de MWTUser. |
| 5 | PLT-03 | Clientes UI | Ninguna | Endpoint GET ya existe. CRUD en UI. |
| 6 | PLT-07 | Brands UI | Ninguna | Backend existe. |

**Excluido de Sprint 9 → Sprint 10:**
- PLT-09 Módulo Productos (depende de Brands + Nodos completados)
- PLT-10 Módulo Inventario (depende de Productos + Nodos)

**Estado:** lista definida — LOTE_SM_SPRINT9.md por crear (post-aprobación Sprint 8).

---

---

## Detalle técnico apps Django — estado verificado

Fuente: verificación directa con Alejandro 2026-03-12. Fusionado desde ENT_PLAT_MODULOS_PENDIENTES (DEPRECATED).

### Apps Django — estado real

| App | Backend | Frontend consola | Notas |
|-----|---------|-----------------|-------|
| `expedientes` | ✅ 39 endpoints | ✅ Sprint 7 completo | Operativo |
| `brands` | ✅ Existe (fixtures + generate_brands_fixtures.py) | ❌ Sin UI | Backend confirmado. Leer models.py antes de implementar UI |
| `transfers` | ✅ Existe app (C30–C35) | ❌ Sin UI | Backend completo |
| `liquidations` | ✅ Existe app (C25–C28) | ❌ Sin UI | Backend completo |
| `qr` | ✅ Existe app + resolver | ❌ Sin UI consola CEO | Backend completo |
| `core` | ✅ Base | — | |
| `integrations` | ✅ Existe | — | |

### Apps Django AUSENTES — deben crearse

| App | Sprint | Bloqueador |
|-----|--------|-----------|
| `users` (MWTUser extendido) | 8 | **En construcción** — LOTE_SM_SPRINT8 Pilar A |
| `permission_groups` | 8 | **En construcción** — LOTE_SM_SPRINT8 Pilar A |
| `knowledge` | 8 | **En construcción** — LOTE_SM_SPRINT8 Pilar B |
| `clients` (app dedicada) | 9 | Endpoint GET ya existe en expedientes |
| `nodes` (LogisticNode) | 9 | Referenciado en transfers, sin app dedicada |
| `products` | 10 | Prerequisito: Brands UI + Nodes |
| `inventory` | 11 | Prerequisito: Products + Nodes |

---

## Convenciones para Sprint 9+

- Backend: DRF · ModelViewSet o APIView · JWT auth
- Frontend: Next.js 14 App Router · `[lang]/(mwt)/(dashboard)/{modulo}/`
- Formularios: Drawer lateral (CRUD) · Página nueva (formularios complejos)
- Todos los modelos: UUID pk · is_active · created_at · updated_at · deleted_at (soft delete)
- RBAC: CEO = superuser en MVP · guards reales post-Sprint 8

---

## Módulos ejecutados en Sprint 6 — NO pendientes

Los siguientes módulos estaban en la lista original pero fueron completados en Sprint 6 (DONE 2026-03-12):

| Módulo | Estado | Referencia |
|--------|--------|------------|
| Consola QR (UI + backend) | ✅ DONE Sprint 6 | LOTE_SM_SPRINT6 Item 6 |
| Rana Walk en mwt.one (brand config, expedientes, artefactos, transfers) | ✅ DONE Sprint 6 | LOTE_SM_SPRINT6 Items 1–3 |
| go.ranawalk.com DNS resolution (CNAME + Nginx + SSL) | ✅ DONE Sprint 6 | LOTE_SM_SPRINT6 Item 7 |

---

## Pendientes Plataforma — tabla maestra

| ID | Dominio | Pendiente | Estado | Bloqueador | Sprint |
|----|---------|-----------|--------|-----------|--------|
| PLT-01 | Plataforma | Paperless-ngx webhook bidireccional (Paperless → Django con OCR) | Integración lista, webhook NO activo | Confirmar soporte webhook en versión instalada de Paperless-ngx | Post-Sprint 9 |
| PLT-02 | Plataforma | Usuarios UI — gestión multi-usuario en consola | ✅ DONE Sprint 9 | Sprint 8 MWTUser | Sprint 9 |
| PLT-03 | Plataforma | Clientes UI — CRUD dedicado | ✅ DONE Sprint 9 | Ninguno | Sprint 9 |
| PLT-04 | Plataforma | Nodos Logísticos UI | ✅ DONE Sprint 9 | Ninguno | Sprint 9 |
| PLT-05 | Plataforma | Transfers UI | ✅ DONE Sprint 9 | PLT-04 | Sprint 9 |
| PLT-06 | Plataforma | Liquidación Marluvas UI | ✅ DONE Sprint 9 | Ninguno | Sprint 9 |
| PLT-07 | Plataforma | Brands UI | ✅ DONE Sprint 9 | Ninguno | Sprint 9 |
| PLT-08 | Plataforma | Consola QR UI | ✅ DONE Sprint 6 | — | — |
| PLT-09 | Plataforma | Módulo Productos | Pendiente | PLT-04 + PLT-07 | Sprint 11 |
| PLT-10 | Plataforma | Módulo Inventario | Pendiente | PLT-09 | Sprint 11 |
| PLT-11 | Plataforma | Sprint 9.1 — UI fixes (globals.css, Sidebar, ConfirmDialog, FormModal, states, pipeline, nodos, brands, clientes) | ✅ DONE Sprint 9.1 | PLT-02..07 | Sprint 9.1 |
| PLT-12 | Plataforma | Sprint 10 — Acordeón expedientes + Dashboard + Security | DRAFT | PLT-11 | Sprint 10 |
| PLT-13 | Plataforma | Sprint 10 security: rate limiting, CORS, JWT rotation | DRAFT | PLT-11 | Sprint 10 |

---

**Aclaración S6-10:** Dashboard P&L no es pendiente. Es la vista financiera S4-05 ya existente.

---

## Pendientes CEO — sesión 2026-03-14

| ID | Pendiente | Tipo | Impacto en score | Referencia |
|----|-----------|------|-----------------|------------|
| CEO-01 | **VENCE 2026-06-30** Promover ~14 DRAFTs maduros a VIGENTE | Decisión | +0.3 | R-V1 en REPORTE auditoría v3 |
| CEO-02 | ~~Definir umbrales triggers T2-T5~~ | Decisión | ✅ DONE | Perplexity Prompt 2 — datos de mercado |
| CEO-03 | ~~Evaluar P×I de 6 riesgos estratégicos~~ | Decisión | ✅ DONE | Perplexity Prompt 1 — P×I con datos |
| CEO-04 | **VENCE 2026-06-30** Cargar snapshot datos Seller Central (guía lista en B3b) | Datos | ⏳ CEO ejecutar | Perplexity Prompt 8 — checklist 1.5h |
| CEO-05 | **VENCE 2026-06-30** Completar fechas/alternativas en ADRs DEC-002 a DEC-006 | Trazabilidad | +0.1 | ENT_GOB_DECISIONES §B |
| CEO-06 | **VENCE 2026-06-30** Pasar docs RW_0X originales para expandir 5 PLBs outline | Contenido | ⚠️ PARCIAL | R-V3 + PLB_COPY/ADS/OPS/GROWTH/SUPPORT. Nota: Bloques 1-5 (v4.3) crearon frameworks en PLB_OPS_AMAZON, ENT_COMP_AMAZON, ENT_MKT_COMPETENCIA, ENT_MKT_KEYWORDS. Migración contenido RW_0X a PLBs sigue pendiente. |
| CEO-07 | **VENCE 2026-06-30** Completar REPORTE_REVISION_DIRECCION_Q1_2026 (riesgos + decisiones) | Gobernanza | +0.1 | REPORTE_REVISION_DIRECCION_Q1_2026 |
| CEO-08 | ~~Aprobar Sprint 8 DRAFT → FROZEN~~ | Sprint | ✅ DONE | LOTE_SM_SPRINT8 DONE v4.0 |
| CEO-09 | ~~Fix health_check.sh: score floor a 0~~ | Técnico | ✅ DONE | Sesión 2026-03-15 |
| CEO-10 | ~~Fix health_check.sh: detectar refs sin .md~~ | Técnico | ✅ DONE | Sesión 2026-03-15 |
| CEO-11 | ~~Sprint 8 guardia: considerar solo usuarios activos~~ | Técnico | ✅ DONE | Sesión 2026-03-15 |
| CEO-12 | Fix error 500 en /api/knowledge/ask/ | Técnico | ✅ DONE Sprint 24 — knowledge pipeline dual routing | ENT_PLAT_CANALES_CLIENTE.Z1 |
| CEO-13 | Carga inicial de .md en pgvector | Técnico | ✅ DONE Sprint 24 — knowledge pipeline implementado | ENT_PLAT_CANALES_CLIENTE.Z2 |
| CEO-14 | **VENCE 2026-06-30** Setup WhatsApp Business API (Meta) | Integración | Canal B2B P2 | ENT_PLAT_CANALES_CLIENTE.Z3 |
| CEO-15 | **VENCE 2026-06-30** Decidir artifacts visibles para clientes (ART-06, ART-08) | Decisión | PLB_INTERACCION_CLIENTE.D completo |
| CEO-16 | **VENCE 2026-06-30** Decidir notificaciones proactivas: cuáles transiciones, cuál canal | Decisión | ENT_PLAT_CANALES_CLIENTE.E |
| CEO-17 | Ale verifica estado real de TODOS los [PENDIENTE] en ENT_PLAT_SEGURIDAD | Seguridad | ✅ DONE Sprint 27 — ENT_PLAT_SEGURIDAD v2.1, 0 [PENDIENTE] sin clasificar. TruffleHog 0 hallazgos. | ENT_PLAT_SEGURIDAD.Z1 |
| CEO-18 | Rate limiting Nginx + Django (antes de abrir B2B) | Seguridad | ✅ DONE Sprint 24 — zones Nginx + DRF throttle | ENT_PLAT_SEGURIDAD.Z2 |
| CEO-19 | Secrets audit: verificar .env, rotación, no en Git | Seguridad | ✅ DONE Sprint 27 — TruffleHog 0 hallazgos. .env chmod 600. Redis requirepass. 13 secrets documentados en ENT_PLAT_SEGURIDAD.B4. | ENT_PLAT_SEGURIDAD.Z3 |
| CEO-20 | Signed URLs MinIO para documentos (antes de B2B) | Seguridad | ✅ DONE Sprint 24 — presigned URLs TTL 15min + log emisión | ENT_PLAT_SEGURIDAD.Z4 |
| CEO-21 | Redis requirepass + JWT expiry/rotation/blacklisting | Seguridad | ✅ DONE Sprint 24 — JWT blacklist + rotation + 30min expiry | ENT_PLAT_SEGURIDAD.Z5+Z6 |
| CEO-22 | **VENCE 2026-06-30** Crear formulário consentimiento LGPD scanner BR | Legal | ENT_COMP_REGULATORIO.B3 |
| CEO-23 | **VENCE 2026-06-30** Confirmar con asesor legal BR si sticker CDC Art.31 cumple como etiqueta complementar | Legal | ENT_COMP_REGULATORIO.B5, ENT_OPS_EMPAQUE_FISICO |
| CEO-24 | **VENCE 2026-06-30** PLT-11: Módulo LLM Intelligence (key vault + model registry + routing + dashboard costos) | Plataforma | ENT_PLAT_LLM_ROUTING — Sprint 11-12 |
| CEO-25 | ⚠️ **VENCE 2026-05-30** Actualizar POL_ROGERS para incluir MAN y ORC (actualmente solo lista GOL, BIS) | Compliance | ENT_COMP_CLAIMS.C1 — PORON disclaimer aplica a 4 productos |
| CEO-26 | ⚠️ **VENCE 2026-05-30** Actualizar ENT_MARCA_SELLO para incluir MAN y ORC (B4 presente en ambas entities) | Marca | ENT_COMP_CLAIMS.C2 |
| CEO-27 | ⚠️ **VENCE 2026-05-30** Obtener texto disclaimer Rogers Corp para PORON® XRD | Compliance | ENT_COMP_ROGERS vacío — texto necesario para fichas técnicas y listings |
| CEO-28 | ~~Elegir email provider~~ | Plataforma | ✅ DONE Sprint 26 — SMTP elegido |
| CEO-29 | **VENCE 2026-06-30** Corregir `buscar_refs` en prompt de higiene — usar `grep -r --include='*.md' --include='*.sh'` en lugar de glob `*.md *.sh` para alcanzar subdirectorios (archivo/). Verificado post-hoc en KB Hygiene v4.7.0: 0 refs rotas en archivo/. Fix preventivo para próxima operación. | KB-Ops | MANIFIESTO_APPEND_20260413_KB_HYGIENE — hallazgo P4 auditoría externa |
| CEO-30 | **VENCE 2026-06-30** Decidir enforcement consolidado POL_STAMP + POL_CHANGELOG → POL_VERSIONADO. STAMP=SOFT, CHANGELOG=HARD. Auditor externo sugiere heredar HARD (el más restrictivo). Requiere decisión CEO antes de ejecutar consolidación. | Gobernanza | KB Hygiene v4.7.0 — F3 vetada por enforcement diferente |
| CEO-31 | **VENCE 2026-06-30** Decisión sobre 7 STUBs vetados por FROZEN: PLB_API, PLB_ARCHITECT, PLB_DEVOPS, PLB_FRONTEND, PLB_INTEGRATION, PLB_MIGRATION, PLB_QA — referenciados por PLB_ORCHESTRATOR. Opciones: (a) mantener estado actual como intención documentada, (b) actualizar PLB_ORCHESTRATOR + eliminar STUBs, (c) crear contenido real en sprints futuros. | KB-Ops | KB Hygiene v4.7.0 — F2 |
| CEO-32 | ⚠️ **VENCE 2026-05-30** Remediar **14 leaks CEO_ONLY** detectados (10 originales B0 audit + 4 nuevos AUDIT 2026-04-27): **(A) PUBLIC + ceo_only_sections (10 originales)** — 9 PRODUCTO (ENT_PROD_ORC, ENT_PROD_MAN, ENT_PROD_ORB, ENT_PROD_GOL, ENT_PROD_VEL, ENT_PROD_BIS, ENT_PROD_LEO, ENT_PROD_COLORES, ENT_PROD_LANZAMIENTO) + 1 DISTRIBUCION (ENT_DIST_DISTRIBUIDORES). **(B) INTERNAL + ceo_only_sections (4 nuevos)** — ENT_PLAT_CONTRATO_NODO [B], ENT_PLAT_LEGAL_ENTITY [C], ENT_PLAT_LLM_ROUTING [D], ENT_PROD_SCANNER_MERCADO [C, D], PLB_SCANNER_DISTRIB [H, I]. Conflicto de tier: secciones más restrictivas que el padre. Opciones: (a) bumpear visibility del archivo al tier más alto (pierde consumo externo), (b) extraer secciones sensibles a archivo `*_CEO.md` paralelo y dejar padre limpio. Tier B (INTERNAL) menos crítico que tier A (PUBLIC) pero igual viola POL_VISIBILIDAD. Remediación scope B3 PRODUCTO + B8 DISTRIBUCION + B10 PLATAFORMA. | Compliance/Seguridad | audit/ceo_only_audit.md 2026-04-18 + AUDIT 2026-04-27 |
| CEO-33 | **VENCE 2026-06-30** Aplicar batch_order_v2 (B1a/B1b/B1c/B2..B11) según audit/KB_MIGRATION_PLAN.md. Orden forzado por dependencias: B1a (SSOTs sync) → B1b (POL hygiene) → B1c (9 efímeros consolidar) → dominios. Comando CEO: `indexa B1a` para reanudar. | KB-Ops | audit/progress.json batch_order_v2 |
| CEO-34 | **VENCE 2026-06-30** Decidir piloto Letta self-hosted en profile `mwt-sprint-active` (4 semanas, esfuerzo 4-6h Ale). Stack memoria operativa agentes. Si sí → asignar sprint y definir baseline tokens. | Plataforma | ENT_PLAT_MEMORY_STACK §E2 |
| CEO-35 | **VENCE 2026-06-30** Reevaluar Cloudflare Agent Memory cuando salga de private beta (waitlist sin compromiso, sin precio público aún). Reevaluación contra Letta cuando haya pricing GA. | Plataforma | ENT_PLAT_MEMORY_STACK §C2 |
| CEO-36 | **DEFERRED — gates G1-G4 (decisión arquitecto 2026-04-28)** Jarvis Orchestrator: agente conversacional persistente per-user que cruza sub-agentes y ejecuta rutinas re-evaluables sobre Action Engine. Plan 3 fases (F1 reactivo / F2 rutinas+memoria episódica / F3 proactivo+multi-tenant). **Estado:** diferido — pre-reqs no cumplidos en 2026-04-28: Engine runtime ❌ (solo contrato v1.2), memoria persistente ❌ (Letta DRAFT). **Gates de reapertura:** G1 Action Engine runtime passthrough en prod + ≥3 skills MWT migradas · G2 memoria persistente operativa (Letta o equivalente) · G3 FaberLoom MVP fuera de path crítico Engine · G4 OutcomeLedger ≥1000 decisiones loggeadas. Estimado calendario para reabrir: 8-12 semanas. **Decisión formal:** DEC-010 en ENT_GOB_DECISIONES. | Idea/Arquitectura DEFERRED | DEC-010 · MANIFIESTO_APPEND_20260428_JARVIS_IDEA · Conversación CEO 2026-04-28 |
| CEO-37 | **VENCE 2026-05-15** Captura formal de **rutinas mentales CEO** en lenguaje natural — sesión Cowork 90-120 min. Output: `ENT_GOB_RUTINAS_CEO.md` (CEO-ONLY) con N rutinas estructuradas (`routine_id + trigger + steps + actions invocadas`). **Por qué antes del build de Jarvis:** (a) valida hipótesis 5-9h/sem orquestación mental con datos reales, (b) genera corpus que Jarvis F1 ejecutará, (c) detecta cuáles rutinas pueden automatizarse YA con n8n + Action Engine passthrough sem 3 (captura 30-40% del valor por 2% del costo), (d) clasifica rutinas re-evaluables (Jarvis-fit) vs deterministas (n8n-fit). **Costo:** 2-3h CEO + 1h arquitecto. **Bloquea:** decisión final sobre build Jarvis F1 (refuerza gate G4). | Captura/Arquitectura | DEC-010 §recomendación intermedia |

---

### Decisiones Sprint 26 (DEC-S26-*) — ✅ DONE 2026-04-10

| ID | Decisión | Resultado |
|----|----------|-----------|
| DEC-S26-01 | Email provider | SMTP elegido |
| DEC-S26-02 | `contact_email` nullable o requerido | Nullable — skip si null |
| DEC-S26-03 | Transiciones que disparan email | C1, producción, despacho, entrega, pago verified/rejected/released, overdue |
| DEC-S26-04 | Gracia cobranza | `payment_grace_days` de ClientSubsidiary; default 30 si null |
| DEC-S26-05 | Cobranza Mode C | CEO recibe si Mode C; cliente si Mode B |

---

---

### Pendientes Sprint 27 → siguiente sprint [DECISION_CEO]

| ID | Pendiente | Origen |
|----|-----------|--------|
| DEC-S27-01 | Confirmar RTO=4h o ajustar | RESUMEN_SPRINT27 §4 |
| DEC-S27-02 | Activar cleanup retención 30 días en backup_mwt.sh (línea 120) | RESUMEN_SPRINT27 §4 |
| DEC-S27-03 | Configurar canal push real en health_check_cron.sh (ntfy/Telegram/webhook) | RESUMEN_SPRINT27 §4 |
| DEC-S27-04 | GPG encryption del dump: definir CEO_GPG_KEY_ID y descomentar bloque | RESUMEN_SPRINT27 §4 |
| DEC-S27-05 | Actualizar identidad git en servidor (user.name + user.email) | RESUMEN_SPRINT27 §4 |

---

Origen: AUDITORIA_SPRINTS_20260312.md + respuestas directas Alejandro 2026-03-12
Actualizado: 2026-04-28 — CEO-36 Jarvis Orchestrator status: EVALUACION → DEFERRED gates G1-G4 (decisión arquitecto). +CEO-37 captura rutinas mentales (VENCE 2026-05-15). Bump v15.0→v16.0. Anteriores: v15.0 (2026-04-28 +CEO-36 idea), v14.0 (2026-04-27 housekeeping AUDIT), v13.0 (2026-04-21, +Open questions post-Kimi Swarm #4 LLM Orchestration Q1-Q18), v12.0 (2026-04-19, +CEO-34/CEO-35 memory stack agentes).

Changelog:
- v3.x: versiones anteriores sin campo version: declarado
- v4.0: campo version: agregado para cumplir estándar de entities (Obs.2 diagnóstico 2026-03-13)
- v5.0 (2026-03-14): fusión contenido ENT_PLAT_MODULOS_PENDIENTES (apps Django + convenciones Sprint 9+). Fix POL_DETERMINISMO.
- v6.0 (2026-03-14): +pendientes CEO sesión auditoría (8 items). Indexación final v3.9.
- v8.0 (2026-03-15): CEO-06 marcado PARCIAL (frameworks creados en v4.3, migración RW_0X sigue pendiente).
- v8.1 (2026-03-15): +5 pendientes canal B2B (CEO-12 a CEO-16). Fix 500 knowledge, carga pgvector, WhatsApp API, artifacts visibles, notificaciones proactivas.
- v8.2 (2026-03-15): +6 pendientes seguridad y legal (CEO-17 a CEO-22). Audit seguridad con Ale INMEDIATO. Rate limiting, secrets, signed URLs, Redis, LGPD. Trigger: ENT_PLAT_SEGURIDAD v1.0 + auditoría triangulada.
- v9.0 (2026-03-16): CEO-08 DONE. PLT-02 a PLT-07 DONE (Sprint 9). +PLT-11/12/13. Apps Django actualizadas.
- v9.1 (2026-03-17): PLT-11 DONE (Sprint 9.1). PLT-12 desbloqueado.
- v10.0 (2026-03-18): +DT-01 a DT-28 (deuda técnica codebase). PLT-09 → Sprint 11.
- v10.1 (2026-03-18): +CEO-23 (legal BR sticker CDC Art.31), +CEO-24 (PLT-11 LLM Intelligence Module). Consolidación patches.
- v10.2 (2026-03-18): +LOTE_SM_SPRINT0 creado (ref rota resuelta). +PLB_RISK_ASSESSMENT STUB. +ENT_PLAT_SCANNER_SECURITY STUB. 3 refs rotas → 0.
- v10.3 (2026-03-18): LOTE_SM_SPRINT10 materializado. PLB domain mismatches corregidos. Stamps normalizados.
- v11.0 (2026-03-18): consolidación.
- v11.1 (2026-04-03): +CEO-25 (POL_ROGERS → incluir MAN/ORC), +CEO-26 (ENT_MARCA_SELLO → incluir MAN/ORC), +CEO-27 (texto disclaimer Rogers Corp). Trigger: preparación fichas técnicas + ENT_COMP_CLAIMS v1.0.
- v11.2 (2026-04-08): CEO-12,
- v12.0 (2026-04-19): +CEO-34 Letta piloto, +CEO-35 CF Agent Memory watch. ENT_PLAT_MEMORY_STACK v1.0 DRAFT.
- v13.0 (2026-04-21): +Open questions post-Kimi Swarm #4 LLM Orchestration (Q1-Q18).
- v14.0 (2026-04-27): housekeeping AUDIT 2026-04-27 (higiene raíz, faberloom-mockup → archivo, headers IDX, CEO-32 update +4 leaks INTERNAL).
- v15.0 (2026-04-28): +CEO-36 Jarvis Orchestrator (idea/evaluación arquitectura — agente conversacional persistente per-user sobre Action Engine, plan 3 fases, decisión pendiente CEO build/defer/descartar).
- v18.0 (2026-06-24): +CEO-38/39/40/41 compliance LATAM items 9-12 (FG-05 sesion Fugu).
- - v17.0 (2026-06-24): +Q19 L1 clasificador embeddings vs LLM generativo (P1) +Q20 L2.5 advisory hybrid Fase 2 (P0). Origen: Kimi Swarm #7 Fugu.
- v16.0 (2026-04-28): CEO-36 status EVALUACION_CEO → DEFERRED gates G1-G4 (decisión arquitecto). +CEO-37 captura rutinas mentales CEO (precondicion al build de Jarvis). Decisión formal en DEC-010.
### Q19 — ¿L1 como LLM generativo (Haiku) o clasificador sobre embeddings?
**Prioridad:** P1
**Origen:** Kimi Swarm #7 (ENT_FABERLOOM_INSIGHTS_KIMI_FUGU — F01)
**Contexto:** TRINITY usa SLM 0.6B con softmax sobre hidden states — un forward pass,
sin generación de texto. FaberLoom planea Haiku para L1, ~10x más caro en latencia/costo
para clasificación categórica. En MVP Haiku es aceptable como proxy.
**Propuesta:** Evaluar migración L1 a clasificador sobre embeddings pgvector para Fase 2.
Decisión debe tomarse antes de Gate F2.
**Unblocks:** SPEC_LLM_ROUTING_ARCHITECTURE §L1 Fase 2 · cost optimization Token Ledger

### Q20 — ¿L2.5 advisory hybrid como resolución Fase 2 routing?
**Prioridad:** P0
**Origen:** Kimi Swarm #7 (ENT_FABERLOOM_INSIGHTS_KIMI_FUGU — F06) · paper ACAR arXiv:2602.21231
**Contexto:** Paper ACAR propone hybrid approach: capa determinística como veto inmutable
+ capa learned que sugiere pero no impone. Resuelve tensión auditabilidad/adaptación sin
activar ModelFingerprint (P13) porque el veto determinístico L1 permanece intacto.
**Propuesta:** Para Fase 2 SPEC_LLM_ROUTING_ARCHITECTURE: L2.5 advisory que sugiere
modelo/modo basado en Token Ledger. Sugerencia rechazable por L1 sin log de error.
L1 conserva veto absoluto.
**Unblocks:** DEC-008 (Adaptive Routing Fase 2) · SPEC_LLM_ROUTING_ARCHITECTURE v2.0

### Compliance LATAM pendientes post-Fugu session (items 9-12)
**Origen:** ENT_FABERLOOM_INSIGHTS_FUGU_SESSION FG-05 · 2026-06-24

**CEO-38** No-training controls por provider
**Prioridad:** P1
Configurar ZDR (Zero Data Retention) explicitamente con cada provider en LiteLLM.
No depender del opt-out de intermediarios (Fugu cubre solo a Sakana, no a subproviders).

**CEO-39** DPA/subprocessor registry
**Prioridad:** P1
Registro formal de DPAs firmados por provider con data_class permitida y region.
Base para tenant_model_allowlist y auditoria regulatoria LATAM.

**CEO-40** Deletion/retention workflows
**Prioridad:** P2
Flujos de borrado y retencion de datos por tenant. Requerido para LGPD Art 15,
Ley 1581 Art 17, LFPDPPP Art 11, Ley 8968 Art 9.

**CEO-41** Breach notification procedures
**Prioridad:** P2
Procedimiento de notificacion ante brechas. Plazo LGPD: 72h a ANPD.
Equivalente en CO/MX/CR pendiente de verificacion con abogado.