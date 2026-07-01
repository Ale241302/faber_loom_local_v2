# BRIEFING CONSOLIDADO · FaberLoom · Hallazgos para indexar en `docs/`

**Fecha:** 2026-04-21
**De:** Álvaro Alfaro (CEO)
**Para:** Cowork
**Alcance:** consolida sesiones de mockup build (v1 → v3.5) + iteración Gemini + clarificaciones posteriores
**Status del mockup:** FREEZE hasta nueva autorización
**PR abierto:** https://github.com/sjoalfaro/mwt-knowledge-hub/pull/1

---

## §0 · Estado actual

- Mockup: `MWT KB/faberloom-mockup/index-standalone.html` · 461 KB · 7,935 líneas · 27 fragments · 15 módulos ruteados · 32 widgets · 30 mock collections
- i18n: ES/EN/PT-BR simétrico (407+ keys)
- Default route: `#/chat`
- AC cumulativo: 94 PASS · 1 REQUIRES-BROWSER · 0 FAIL
- Branch git: `feat/faberloom-mockup-v2-chat` (último commit `d088412`)

---

## §1 · Artefactos canónicos producidos · archivos a indexar

### Research (`MWT KB/faberloom-mockup/research/`)

| Archivo | Propósito | Indexar? |
|---|---|---|
| `A1_spec_canon.md` | Extracción canónica `SPEC_FABERLOOM_ARCHITECTURE` (3 objetos, state machine, 20 tablas FROZEN, RLS vars, audit verbs) | Como síntesis · no promueve canon nuevo |
| `A2_existing_inventory.md` | Inventario código ESM pre-fragments · obsoleto post-v3.5 | Archivable |
| `A3_dark_palette.md` | Paleta dark mode WCAG AA con cálculos luminance | Promover tokens a KB (ver D9) |
| `A4_arch_principles.md` | Extracción `ARCH_AGENT_PRINCIPLES` (P0-P13, autonomy ladder L0-L4) | Síntesis · no promueve nuevo |
| `A5_knowledge_flow.md` | Extracción `SPEC_USER_ADMIN_KNOWLEDGE_FLOW` (4 scopes, permissions, break-glass, leakage) | Síntesis · no promueve nuevo |
| `A6_reconciliation.md` | D1-D15 decisiones de implementación del mockup | Promover selectivamente (ver §3) |
| `A7_chat_contradictions.md` | **CRÍTICO** · 17 contradicciones (C1-C17) + open questions | Referencia obligatoria |
| `B0_AUDIT_METHODOLOGY.md` | Framework Service Design + UX Arch para auditar | Promover como `POL_AUDITORIA_UX.md` |
| `B1_SERVICE_BLUEPRINT.md` | 14 módulos × 4 capas + 12 inbound types + ecology map + 23 gaps | Promover ecology map |

### Verification (`MWT KB/faberloom-mockup/verification/`)

| Archivo | Resultado |
|---|---|
| `AC_v2.md` | 18/20 PASS |
| `AC_v3.md` | 48/48 PASS |
| `AC_v3_5.md` | 28/28 PASS (agent lifecycle) |
| `trazabilidad_v2.md` · `trazabilidad_v3.md` | Matrices de gaps cerrados |
| `axe_report_2026-04-19_static.md` | WCAG 2.1 AA · 0 violations esperadas |

### Delivery notes (`MWT KB/faberloom-mockup/`)

- `DELIVERY_NOTES.md` (v1) · `DELIVERY_NOTES_v2.md` · `DELIVERY_NOTES_v3.md` · `DELIVERY_NOTES_v3_5.md`
- `HANDOFF_TO_COWORK.md` (briefing anterior · sigue válido como base)
- `GEMINI_PROMPT_PACK.md` (16 prompts para iteraciones futuras)

---

## §2 · Canon CONFIRMADO · NO tocar

14 conceptos ya sólidos en la KB, no requieren edits:

1. 4 scopes knowledge (global/org/dept/user) · A5 §2.1
2. `business_entity_id` como metadata, no 5to scope · A5 §2.2
3. Roles owner/admin/operator + matrix de permisos · A5 §6
4. Break-glass 8h MFA `support_impersonation` · A5 §1.10
5. TTL learned overlay 90d (rango 30-180) · A5 §7.1
6. Leakage tests pytest gate CI · A5 §8
7. 20 tablas FROZEN (S1=9, S2=7, S3=4) · A1 §2
8. RLS session vars · A1 §1
9. Autonomy Ladder L0-L4 + thresholds globales · A4 P4
10. 3 objetos canónicos (Spec/Runtime/Memory) · A4 P1
11. State machine drafting → awaiting_approval → approved → executing → completed + branches · A4 P7
12. Draft-first absoluto · A4 P3
13. Feedback codes tone/data/structure/policy/scope/context · A4 P6
14. Thermometer 🔵🟡🔴 · Gold pipeline · A4

---

## §3 · DECISIONES a promover a `docs/` · D1-D17

### D1 · Bandeja unificada polimórfica (12 item kinds)
- **Target:** NUEVO `SPEC_BANDEJA_UNIFIED.md`
- **Contenido:** drafts + 11 inbound types (inbound_email, inbound_msg, crm_event, alert, approval_request, escalation, feedback_reply, sla_timer, webhook, audit_alert, task) · saved-views URL pattern · per-kind action set
- **Prioridad:** P1

### D2 · Chat como primitiva, no destino
- **Target:** NUEVO `SPEC_CHAT_PRIMITIVE.md` o sección en SPEC_FABERLOOM_ARCHITECTURE
- **Contenido:** `W.chatThread` reusable en 4 contextos (standalone + bandeja-detail + skill-studio sandbox + agent-console debug)
- **Prioridad:** P2

### D3 · Action-risk registry 6 fields
- **Target:** NUEVO `SCH_ACTION_RISK.md`
- **Contenido:** `action_id` · `reversibility` (reversible_24h/reversible_cost/irreversible/irreversible_cost) · `side_effects[]` · `min_autonomy` (L0-L4) · `required_role` · `audit_class` (commercial/financial/operational/policy/meta)
- 18 acciones canónicas en mock como referencia
- **Prioridad:** P0

### D4 · Provenance chain schema
- **Target:** NUEVO `SCH_PROVENANCE.md`
- **Contenido:** `claim_id` → `evidence_span_id` → `source (sourceVersion, line, retrievalRunId)` · relación con ModelFingerprint P13
- **Prioridad:** P0

### D5 · Multi-output bundle approval
- **Target:** Extender `ARCH_AGENT_PRINCIPLES.md` P3
- **Contenido:** 1 aprobación → N actions atómicas con aggregate risk `max(reversibility)`
- **Prioridad:** P1

### D6 · Approval chains entre usuarios
- **Target:** Extender `SPEC_USER_ADMIN_KNOWLEDGE_FLOW.md` §6
- **Contenido:** states `pending/approved/waiting_previous` · comments thread · escalation timeouts · `parent_draft_id`
- **Prioridad:** P1

### D7 · AgentSpec lifecycle UX completo
- **Target:** Extender `ARCH_AGENT_PRINCIPLES.md` P1 + `SPEC_FABERLOOM_ARCHITECTURE.md` §12
- **Contenido:** create/edit/clone/pause/resume/retire · versioning inmutable · soft-delete · audit verbs: `agent_spec.created` · `.published` · `.paused` · `.resumed` · `.retired`
- **Prioridad:** P0 (ya implementado en v3.5, falta canonicalizar)

### D8 · Data portability LGPD/LFPDPPP/Ley 1581/Ley 29733
- **Target:** NUEVO `POL_DATA_PORTABILITY_LATAM.md`
- **Contenido:** user-level JSON download + tenant-level export manual+scheduled · retention 30d default · audit verbs `user.data_exported` · `tenant.exported`
- **Prioridad:** P1 (compliance legal · no negociable pre-LGPD audit)

### D9 · Dark mode tokens WCAG AA verificados
- **Target:** NUEVO `ENT_DESIGN_SYSTEM_TOKENS.md` (o extender `ENT_MARCA_IDENTIDAD.md`)
- **Contenido:** 30+ tokens con luminance math · paleta paper-under-lamp · fuente: research/A3_dark_palette.md §4 CSS block
- **Prioridad:** P0 (safe-to-promote)

### D10 · Bandeja saved-views URL pattern
- **Target:** Incluir en D1 (SPEC_BANDEJA_UNIFIED)
- **Contenido:** `?view=triage|approve|mine|team|attention|all` · sort default por urgencia · bookmark-able
- **Prioridad:** P1 (incluido en D1)

### D11 · Seats + Topología Organizacional
- **Target:** NUEVO `SCH_ORG_TOPOLOGY.md` + NUEVO `ENT_POSITION.md`
- **Contenido:** org compra N seats · topology nodes (gerentes/subgerentes/colaboradores) · entity `Position` con (id, tenantId, title, parent_position_id, department_id, allocated_seat_license, filled_by_user_id nullable)
- **Prioridad:** P1 (bloquea deployment real)

### D12 · Desacoplamiento Position ↔ User · EL GRANDE
- **Target:** Extender `ARCH_AGENT_PRINCIPLES.md` P1 + `SPEC_FABERLOOM_ARCHITECTURE.md` §4.1
- **Contenido:** AgentMemory · agent_spec_overlay_learned · skills asignadas pertenecen a `position_id` (UUID estable), NO a `user_id`. User bindea temporalmente. Añadir `position_id` column en `memory_chunk`.
- **Prioridad:** P0 · **CAMBIO DE SCHEMA** · resolver ANTES de construir skills/agents reales

### D13 · Protocolo de Herencia / Sucesión de Posición
- **Target:** NUEVO `POL_POSITION_SUCCESSION.md`
- **Contenido:** nuevo ocupante hereda: AgentMemory acumulada · skills + overlays manuales · historial runs · patterns aprendidos. Audit verbs nuevos: `position.occupant_changed` · `position.succession_completed`
- **Open pregunta:** overlap period vs switchover instantáneo
- **Prioridad:** P1

### D14 · Directory Sync M365/Google Workspace (topology, no solo SSO)
- **Target:** Extender `SPEC_USER_ADMIN_KNOWLEDGE_FLOW.md` §1 + NUEVO `SCH_DIRECTORY_SYNC.md`
- **Contenido:** leer jerarquía/grupos/departamentos del directorio corporativo · auto-generar Position graph · refresh cron + conflict resolution manual vs directory
- **Prioridad:** P1

### D15 · Modularidad estricta distribuida · promovido de v1.5 a v1 P0
- **Target:** Extender `SPEC_FABERLOOM_ARCHITECTURE.md` como principio arquitectónico
- **Contenido:** cada módulo con ciclo de vida + versionamiento independiente · `module.version` + audit log propio · plantilla ADR obligatoria por cambio cross-módulo
- **Prioridad:** P0

### D16 · Skill Library + Factory bidireccional
- **Target:** NUEVO `SCH_SKILL_LIBRARY.md` + NUEVO `POL_MARKETPLACE_PUBLISHING.md`
- **Contenido:**
  - **Nivel 1 FaberLoom:** Skill Factory (interno, proceso de creación) → Skill Library (catálogo importable por todos los tenants)
  - **Nivel 2 Tenant:** Skill Studio (crea skills propias) · Import from Library · Publish back to Library (con review de FaberLoom staff)
  - Audit verbs: `skill.imported_from_library` · `skill.published_to_library` · `skill.fork_from_library` · `skill_library.published`
  - Permissions delta: Publish tenant→library requiere Owner (no Admin por default)
- **Prioridad:** P1 (sin library los tenants nuevos no tienen onboarding inmediato)

### D17 · Agent Library + Factory bidireccional (extensión de D16)
- **Target:** NUEVO `SCH_AGENT_LIBRARY.md`
- **Contenido:** mismo patrón que D16 aplicado a agentes. FaberLoom publica "starter agents" (Cotizador B2B LATAM starter · Compliance ISO checker · Sales triage L2) con skills pre-asignadas + kb_refs típicas + escalation_policy sugerida + autonomyCeiling recomendado. Tenants importan/forkean/publican.
- **Prioridad:** P1

---

## §4 · EDITS menores a docs existentes · U1-U11

| # | Doc | Edit |
|---|---|---|
| U1 | `ARCH_AGENT_PRINCIPLES.md` P1 | +AgentSpec versioning · lifecycle states (shadow/active/paused/retired) · `triggerKind` enum (word/event/schedule) |
| U2 | `ARCH_AGENT_PRINCIPLES.md` P11 | Nota iteration auto-feedback policy (cuando user itera, ¿counts como feedback automático?) |
| U3 | `ARCH_AGENT_PRINCIPLES.md` P12 | Definir qué define "cluster" (3 niveles cross-skill propagation: skill/cluster/org) |
| U4 | `ARCH_AGENT_PRINCIPLES.md` P6 | Tabla mapping UI 5 razones ↔ P6 6 codes internos |
| U5 | `SPEC_FABERLOOM_ARCHITECTURE.md` §8 | Clarificar SLO p95 single-sample vs sustained-window (7d) |
| U6 | `SPEC_USER_ADMIN_KNOWLEDGE_FLOW.md` §6 | Añadir rows: Crear agente · Editar AgentSpec · Pausar/Retirar (Owner/Admin sí · Operator no) |
| U7 | `SPEC_USER_ADMIN_KNOWLEDGE_FLOW.md` §10.1 | Mecanismo de export user-level + tenant-level |
| U8 | `SPEC_FABERLOOM_ARCHITECTURE.md` §12 audit_event enum | Verbs nuevos: `agent_spec.paused` · `.resumed` · `tenant.config_changed` · `tenant.exported` · `user.data_exported` · `connector.enabled` · `memory_chunk.promoted` · `position.occupant_changed` · `skill.imported_from_library` · `skill.published_to_library` |
| U9 | `ARCH_AGENT_PRINCIPLES.md` P4 | Autonomy progression es por `position_id` · NO por `user_id` (post D12) |
| U10 | `SPEC_USER_ADMIN_KNOWLEDGE_FLOW.md` §1 | Directory integration extended (D14) |
| U11 | `SPEC_FABERLOOM_ARCHITECTURE.md` §15 | Promover "modular distributed" de v1.5 defer → v1 MUST-HAVE (D15) |

---

## §5 · Docs operacionales a CREAR · O1-O6

| # | Nuevo doc | Propósito |
|---|---|---|
| O1 | `POL_AUDITORIA_UX.md` | Framework B0 · proceso de auditoría UX · cadencia mensual |
| O2 | `ENT_PLAT_BOUNDARIES.md` | Service ecology map · 11 sistemas externos + nivel integración |
| O3 | `SCH_AGENT_SPEC_VERSIONING.md` | Schema versioning · `supersedes_spec_id` · rollback forward-only · audit on publish |
| O4 | `SCH_SKILL_LIBRARY.md` | Schema del catálogo global (D16) |
| O5 | `SCH_AGENT_LIBRARY.md` | Schema del catálogo de agentes (D17) |
| O6 | `POL_MARKETPLACE_PUBLISHING.md` | Criterios de aprobación para marketplace bidireccional (D16+D17) |

---

## §6 · OPEN QUESTIONS · C1-C23 · NO promover a canon sin resolución

| # | Pregunta | Prioridad |
|---|---|---|
| C1 | Feedback taxonomy 5 UI vs 6 codes P6 · ¿reconciliar? | Alta |
| C2 | Sealed como kind UI-only de PatternBadge | Baja (no canon) |
| C3 | GroundedIn vs Evidence tab · distinctness | Media |
| C4 | Cluster scope definition · ¿qué define un cluster? | Media |
| C5 | Iteration auto-feedback policy · ¿counts automático? | Alta |
| C6 | Synthetic IDs `cv_live_/msg_live_` aceptable en mockup | Baja |
| C7 | SLA breach window · single-sample vs sustained 7d | Alta |
| C8 | UserControlProfile structure · spec no escrito | Media |
| C9 | `trigger_kind` enum formalization | Alta |
| C10 | 5th scope pivote · esperar design partners | Media (bloqueado por evidencia) |
| C11 | Handoff packet UX standardization | Media |
| C12 | ModelFingerprint normalization policy | Media |
| C13 | LearningHeat 4to estado "gold" | Baja |
| C14 | Approval chains branching + escalation timeouts | Alta |
| C15 | Chat primitive multi-agent per thread | Baja (futuro) |
| C16 | Data portability mechanism specifics | Alta (bloqueante compliance) |
| C17 | Approval gate raise `autonomyCeiling` vs otros edits | Alta |
| C18 | Default route dinámico por rol (operators→bandeja, CEO→dashboard) · NO promover sin validación user real | Media |
| C19 | Sidebar "lean" · colapsar 6 módulos Gestión en 1 nodo · NO promover sin test con Ana real | Media |
| C20 | Kill Design System del sidebar → ruta `/_design` oculta · safe-to-promote (polish) | Baja · ready |
| C21 | Agent Console redesign · 6 tabs → 3-4? Fusionar Skills+Memoria + Logs+Versioning? | Media |
| C22 | Agent Create Wizard redesign · import-from-library como default path vs 5-step scratch | Alta (ligado a D17) |
| C23 | Knowledge Graph Module · visualización tipo Obsidian de relaciones existentes · v1 vs v1.5? | Baja · módulo nuevo P2 |

---

## §7 · NO promover · hallucinations de Gemini

Estas aparecen en docs generados por Gemini pero NO están en canon ni fueron decisiones validadas. Si Cowork las ve en futuras entregas, pedir contexto antes de promover:

1. "Dashboard de Adopción de Inteligencia" · módulo inventado · no existe en v3.5 ni A1-A7
2. "Métricas de Ahorro $/hs-hombre" · requiere baseline no disponible · imposible medir en v1
3. "Propagación de Éxito automática" · contradice A4 P12 (gate humano mandatorio)
4. "Biblioteca Global de Skills como entidad separada del Skill Studio" · obsolete tras D16 (library es complemento, no reemplazo)
5. "FaberLoom OS / Sistema Operativo Organizacional" · vocabulario marketing, no canon técnico
6. "Umbral de confianza para auto-ejecución" · contradice A4 P3 "draft-first absoluto"
7. "Consola de Trazabilidad" (como entidad nueva) · es rename confuso de provenance chain existente

---

## §8 · KB GAPS detectados · docs que deberían existir

Schemas/entities faltantes que surgieron durante el build:

1. `SCH_CONNECTOR_ACCOUNT.md` · schema FROZEN connectors con kinds enumerados (email/messaging/marketplace/kb_source/erp/calendar/identity_provider)
2. `SCH_AGENT_EVENTS.md` · catálogo canónico de events que disparan agentes (11+ actualmente hardcoded en wizard)
3. `SCH_DRAFT_STATE_MACHINE.md` · state machine formal con 10 states + transitions table + reversibility rules
4. `SCH_OVERLAY_POLICY.md` · structure `manual_overlay` + `learned_overlay` + `sealed_base` relations
5. `POL_NOTIFICATION_ROUTING.md` · qué eventos live van a bandeja vs solo log
6. `ENT_PERSONAS_OPERATIVAS.md` · personas canon (Bruno/Ana/Álvaro) con JTBD por persona

---

## §9 · ACCIONES prioritizadas · roadmap sugerido

### P0 · Esta semana (pre-demo 2026-04-22 Marluvas/Tecmater)

1. **D12** (Position vs User decoupling) · cambio de schema · bloqueante · arrancar primero
2. **D7** (AgentSpec lifecycle canonicalization) · consistency mockup ↔ canon
3. **D9** (Dark palette tokens) · safe-to-promote · polish visual
4. **D15** (Modularidad P0) · promover de deferred · baseline arquitectónico
5. **C20** (Kill Design System sidebar) · safe-to-promote
6. **C1** (Feedback taxonomy reconciliation) · decisión corta · desbloquea P6 edits

### P1 · Próximas 2 semanas (pre-beta-cut 2026-06-14)

1. **D1** (Bandeja unified spec) · módulo central
2. **D3 + D4** (action-risk + provenance schemas) · canon técnico
3. **D5 + D6** (bundle + approval chains) · workflow multi-actor
4. **D8** (data portability LGPD) · compliance legal
5. **D11 + D13 + D14** (topology + herencia + directory sync) · enterprise readiness
6. **D16 + D17** (Skill Library + Agent Library) · onboarding tractable
7. **U1-U11** · edits a docs existentes
8. **O1-O6** · nuevos docs operacionales
9. **C5, C7, C9, C16, C17, C22, C14** (open questions high-priority) · resolución con Álvaro

### P2 · Post-validación con design partners

1. **C18, C19, C21, C23** · validar con Ana/Bruno reales antes de decidir
2. **KB gaps** (schemas faltantes §8) · cerrar deuda técnica
3. **D2** · Chat primitive spec · consolidar patrón

### P3 · Iteración continua

1. Resolver open questions baja prioridad (C2, C3, C6, C13, C15)
2. Mantener `research/A7` como log vivo

---

## §10 · Reglas de engagement para Cowork

- No tocar `MWT KB/faberloom-mockup/` · es artefacto FROZEN
- Toda nueva decisión pasa primero por `research/A7` como contradicción → después de validación → promover a `docs/`
- No re-litigar los 14 confirmed en §2
- Cualquier cosa que aparezca en docs de Gemini (como el PDF "Especificación de Ingeniería") · verificar contra §7 hallucinations antes de procesar
- Preguntarle a Álvaro si algún item de §6 open questions requiere decisión
- Mantener `HANDOFF_TO_COWORK.md` como base · este briefing extiende, no reemplaza

---

## §11 · Quick reference · rutas

| Concepto | Path |
|---|---|
| Mockup deliverable | `MWT KB/faberloom-mockup/index-standalone.html` |
| Decisiones tomadas | `MWT KB/faberloom-mockup/research/A6_reconciliation.md` |
| Contradicciones/open questions | `MWT KB/faberloom-mockup/research/A7_chat_contradictions.md` |
| Service blueprint | `MWT KB/faberloom-mockup/research/B1_SERVICE_BLUEPRINT.md` |
| Handoff previo | `MWT KB/faberloom-mockup/HANDOFF_TO_COWORK.md` |
| Canon target | `MWT KB/docs/` |
| PR | https://github.com/sjoalfaro/mwt-knowledge-hub/pull/1 |

---

**Fin del briefing.** Ante duda sobre cualquier item, referenciar A7/B1 en el mockup folder o pedir contexto a Álvaro.
