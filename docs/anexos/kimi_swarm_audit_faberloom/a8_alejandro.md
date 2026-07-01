# Auditoría FaberLoom Foundation Beta — Agente 8 (Alejandro / Integrador)

**Repo canónico:** `C:/dev/mwt-knowledge-hub/`  
**Reporte:** `faberloom_audit_a8_alejandro.md`  
**Fecha:** 2026-06-24  
**Auditor:** Agente 8 — Integrador / Alejandro  
**Scope:** Plan `PLB_FB_FOUNDATION_BETA_v1` (13 sprints, Foundation Beta). No se implementa código; solo se audita ejecutabilidad desde la perspectiva del developer encargado de integrar backend, frontend, agentes y operaciones.

---

## 1. Resumen ejecutivo

La base de conocimiento de FaberLoom tiene **dos planes vigentes que se contradicen en forma de producto, stack y timeline**. Como integrador no puedo construir simultáneamente el Foundation Beta firmado (SaaS server-first, 13 sprints, FastAPI+Next.js+Postgres+Redis+Celery+LiteLLM Proxy) y el `PLAN_DESARROLLO_FABERLOOM_v5` (desktop/web dual, FastAPI+LiteLLM lib, 13-16 semanas, dataset de verdad E0). Necesito una única fuente de verdad antes de escribir la primera migración.

Además, varios specs que Foundation Beta asume como entrada están en estado DRAFT, STUB o simplemente no existen en el repo. Eso convierte sprints teóricamente factibles en bloqueados por especificación incompleta.

### Top 3 hallazgos críticos

1. **P0 — Fuente de verdad duplicada/conflictiva.** `PLB_FB_FOUNDATION_BETA_v1` (FIRMADO 2026-05-01) y `PLAN_DESARROLLO_FABERLOOM_v5` (2026-06-22) definen formas de producto, stacks y timelines incompatibles. El primero es el contrato firmado; el segundo dice que `SPEC_FB_BUILD_SEQUENCE_v3` queda "superseded en orden/timeline". Esto bloquea cualquier estimación y asignación de recursos.
2. **P0 — Stack tecnológico no alineado.** Foundation Beta fija LiteLLM **Proxy** + Next.js + Celery + 12 contenedores Docker Compose. El plan v5 y `SPEC_FB_AGENT_BUILDER_v1` asumen LiteLLM **lib** (o Proxy como opción), desktop-first, y 15 contenedores. Eligen diferentes caminos para el gateway LLM, el frontend y la orquestación de tareas.
3. **P1 — Especificaciones de entrada incompletas.** `ENT_PLAT_OBSERVABILIDAD.md` es un STUB vacío; `SPEC_FABERLOOM_SKILL_COMPOSITION_v1` es DRAFT sin seed catalog aprobado; `POL_FB_OUTCOME_ACCOUNTABILITY.md` está referenciado por todos los specs de SHADOW/graduación pero **no existe** en el repo. Sin ellos, S1B, S4 y S8-S10 no tienen criterios de hecho auditable.

**Recomendación inmediata:** antes de arrancar S1A, CEO debe ratificar una sola fuente de verdad, resolver el conflicto de forma de producto, y producir los specs bloqueantes. De lo contrario el riesgo de refactor masivo en la semana 4-5 es alto.

---

## 2. Sprints auditados

### S1A — Backend Core (Semanas 1-2)

**P1: ¿Qué se construye y cuál es la entrega funcional mínima?**

Se levanta la plataforma base: API en FastAPI, Postgres con ~20 tablas canon (`SCH_FB_CORE_TABLES_v1`), RLS por tenant, UUIDv7, tabla de audit inmutable, autenticación (JWT + OAuth Google), Redis Streams, Celery (worker + scheduler), LiteLLM Proxy como gateway a Anthropic, Nginx, y Docker Compose con 8 contenedores core. Se entrega un seed mínimo de tenants, roles y usuarios, y tests de integración que validen auth, RLS y audit.

**P2: ¿Qué decisiones arquitectónicas y de stack están fijadas (o pendientes) para este sprint?**

- **Fijadas en contrato firmado:** FastAPI + Next.js + Postgres + Redis + Celery + LiteLLM Proxy + Anthropic-only; hosting Hostinger KVM 8; RLS obligatorio; single-tenant lógico con `tenant_id` en data desde día 1; worker queue congelado para E1 (`MANIFIESTO_APPEND_20260501_FOUNDATION_BETA_FIRMADO`, condición A).
- **Pendiente:** elección explícita del worker queue (Celery es la asumida, pero el plan dice "congelado en S1A"). LiteLLM Proxy vs lib no está resuelto ante el conflicto con `PLAN_DESARROLLO_FABERLOOM_v5`.
- **Deuda técnica identificada:** el schema de skills usa namespace `metadata.mwt.*` en lugar de `metadata.fbl.*` (`SCH_FB_SKILL_MANIFEST_v2`, `SPEC_FB_AGENT_BUILDER_v1` D5). Migrar ahora es barato; dejarlo lo hace costoso en S11.

**P3: ¿Qué riesgos de implementación ve el integrador y qué mitigación propone?**

| Riesgo | Mitigación |
|--------|-----------|
| RLS en 20 tablas con migraciones complejas | Migración template con `app.tenant_id`, tests de políticas por tabla, no hardcodear tenant_id en queries. |
| LiteLLM Proxy como servicio adicional en KVM 8 | Dimensionar RAM/CPU y establecer límites; si se opta por lib, decidirlo en S1A, no en S5. |
| Worker queue "congelado" sin evaluación documentada | Escribir ADR mínimo que justifique Celery vs ARQ/RQ; cualquier cambio posterior requiere aprobación CEO. |
| Conflicto Foundation Beta vs plan v5 | **Resolver antes de S1A.** No es riesgo técnico, es riesgo de dirección. |

**P4: ¿Qué criterios de "hecho" son auditablesm y qué evidencia se debe generar?**

- [ ] `docker compose up` levanta los 8 contenedores core sin errores.
- [ ] Suite de tests de integración pasa: auth, RLS, audit log, CRUD tenant.
- [ ] LiteLLM Proxy enruta una llamada de prueba a Anthropic y se registra en logs.
- [ ] Migraciones de base de datos son reproducibles en una base limpia (`alembic upgrade head`).
- [ ] Documento ADR del worker queue firmado.

**Pregunta crítica — ¿Qué está underspecified y bloquea la implementación?**

¿Qué pasa si durante S1A se decide adoptar LiteLLM(lib) o el enfoque desktop-first del plan v5? No existe un mecanismo de reconciliación formal con Foundation Beta. Necesito una decisión CEO que unifique la fuente de verdad **antes** de crear la primera migración, o el sprint se convierte en un refactor continuo.

---

### S1B — Observabilidad y Resiliencia (Semanas 3-4)

**P1: ¿Qué se construye y cuál es la entrega funcional mínima?**

Se añaden 4 contenedores de observabilidad (MinIO, Loki, Prometheus, Grafana), se centraliza logging, se configuran métricas base, backups automáticos y un restore test. También se congela definitivamente el worker queue para E1. La entrega mínima es tener visibilidad operativa de los logs y métricas de la plataforma, y garantizar que se puede restaurar un backup.

**P2: ¿Qué decisiones arquitectónicas y de stack están fijadas (o pendientes) para este sprint?**

- **Fijadas:** stack de observabilidad (MinIO/Loki/Prometheus/Grafana); restore test demostrado antes de S10; worker queue congelado.
- **Pendiente:** `ENT_PLAT_OBSERVABILIDAD.md` es un STUB vacío (`status: STUB — sin contenido`). No hay SLIs/SLOs, alertas, retención ni runbooks.

**P3: ¿Qué riesgos de implementación ve el integrador y qué mitigación propone?**

| Riesgo | Mitigación |
|--------|-----------|
| `ENT_PLAT_OBSERVABILIDAD.md` vacío | Redactar spec mínimo en S1A con SLIs (latencia, error rate, costo LLM), alertas y retención. |
| Presión de recursos en KVM 8 (12+4=16 contenedores) | Definir límites de CPU/memoria por contenedor; evaluar si KVM 8 sigue siendo viable con todos los servicios. |
| Restore test sin política de backup | Definir frecuencia, destino y retención de backups en S1A; automatizar restore test en staging. |
| Loki/MinIO sin planeamiento de storage | Estimar volúmenes de logs y métricas; configurar rotación. |

**P4: ¿Qué criterios de "hecho" son auditablesm y qué evidencia se debe generar?**

- [ ] Grafana accesible con dashboards de CPU, memoria, discos y latencia API.
- [ ] Loki centraliza logs de todos los contenedores; se puede buscar por `trace_id`.
- [ ] Restore test pasa en ambiente de staging con evidencia documentada.
- [ ] Alertas básicas configuradas (API down, error rate >1%, disco >80%).
- [ ] Spec `ENT_PLAT_OBSERVABILIDAD.md` actualizado a VIGENTE.

**Pregunta crítica — ¿Qué está underspecified y bloquea la implementación?**

¿Dónde está la especificación de observabilidad más allá del listado de contenedores? `ENT_PLAT_OBSERVABILIDAD.md` es un stub; sin SLIs/SLOs, runbooks y criterios de alerta, S1B no se puede auditar objetivamente.

---

### S2 — Inbound, Email y Voice Profile (Semanas 5-6)

**P1: ¿Qué se construye y cuál es la entrega funcional mínima?**

Se implementa la capa de entrada y salida de mensajes: Gmail OAuth nativo, soporte IMAP/SMTP custom, Resend como relay outbound limitado al <5% del volumen mensual, Voice Profile (persona, tono, glosario, saludo y firma por usuario), y la base para canales adicionales (WhatsApp/webhook). La entrega mínima es recibir y enviar email real con identidad del tenant y voz consistente.

**P2: ¿Qué decisiones arquitectónicas y de stack están fijadas (o pendientes) para este sprint?**

- **Fijadas:** multi-email nativo; Resend <5% outbound mensual; DPA requerido antes de S10 o limitar a mensajes no sensibles; Voice Profile completo (TIER 1 #14) pero con enmienda v2.1 que colapsa E1-E2 a bloque de estilo + few-shot de gold samples + filtros post-generación (`SPEC_FB_VOICE_HUMANIZER_v2`).
- **Pendiente:** `ENT_PLAT_CANALES_CLIENTE.md` está en DRAFT y prioriza Portal B2B como P1, con bloqueadores técnicos (error 500 en `/api/knowledge/ask/`, carga inicial pgvector). Eso contradice el enfoque email-first de Foundation Beta.

**P3: ¿Qué riesgos de implementación ve el integrador y qué mitigación propone?**

| Riesgo | Mitigación |
|--------|-----------|
| Prioridad de canales mal alineada (Portal vs email) | Acotar S2 a email/Gmail/Resend; dejar Portal B2B como spike posterior. |
| Resend <5% difícil de medir sin métricas de S1B | Contador diario en DB + alerta al acercarse al 5%; reporte semanal. |
| Aprobación Google OAuth para FaberLoom puede demorar | Iniciar trámite en S1A (compromiso CEO inmediato del manifiesto). |
| WhatsApp Cloud API requiere aprobación Meta y tabla de mapeo | Diferir a S7 o tratar como canal opcional; no bloquear S2. |
| Voice Profile v2.1 requiere `SPEC_FB_VOICE_BOOTSTRAP_v1` pendiente | Redactar bootstrap antes de S2; sin él no se puede inicializar el perfil. |

**P4: ¿Qué criterios de "hecho" son auditablesm y qué evidencia se debe generar?**

- [ ] Envío y recepción real de email con Gmail OAuth en ambiente de prueba.
- [ ] Resend envía <5% del volumen mensual medido con evidencia.
- [ ] Voice Profile inyecta bloque de estilo en system prompt y aplica filtros de banned phrases/glosario.
- [ ] Cada email inbound/outbound genera audit log con `trace_id`.
- [ ] DPA en borrador o decisión explícita de limitar datos sensibles.

**Pregunta crítica — ¿Qué está underspecified y bloquea la implementación?**

¿El inbound principal es Gmail/IMAP o un webhook/portal genérico? `ENT_PLAT_CANALES_CLIENTE.md` prioriza Portal B2B como P1, mientras Foundation Beta prioriza email. Eso cambia la arquitectura de triggers y la forma en que llegan los datos a los agentes.

---

### S3 — Mesa de Control UI (Semanas 7-8)

**P1: ¿Qué se construye y cuál es la entrega funcional mínima?**

Se construye la interfaz principal (Mesa de Control) en Next.js App Router: login, selección de workspace/rol, feed de items, bandeja de drafts pendientes, flujo approve/edit/reject con HITL absoluto, y vistas de agentes/runs. La entrega mínima es que un AM pueda ver drafts generados por un agente, editarlos y aprobar/rechazar, con estado sincronizado con el backend.

**P2: ¿Qué decisiones arquitectónicas y de stack están fijadas (o pendientes) para este sprint?**

- **Fijadas:** Next.js App Router + React Server Components; TanStack Query v5 para server-state; Zustand para UI-state local; WebSocket nativo con hook `useFaberloomWS`; React Hook Form + Zod; optimistic updates con rollback (`SPEC_FB_FRONTEND_REALTIME_STATE_v1`).
- **Fijadas:** HITL absoluto — todo output cliente-facing pasa por Mesa como draft pendiente (`ARCH_AGENT_PRINCIPLES` P3, Foundation Beta TIER 1 #2).
- **Pendiente:** número real de roles E1. Foundation Beta TIER 1 #7 fija 5 roles (admin, operator, viewer, auditor, service-account), pero no hay un spec de RBAC detallado para Foundation Beta.

**P3: ¿Qué riesgos de implementación ve el integrador y qué mitigación propone?**

| Riesgo | Mitigación |
|--------|-----------|
| Race entre optimistic update y evento WS | Implementar reconciliación server-truth: onError invalida query; onSettled re-invalida. |
| WebSocket reconnect y `last_event_id` | Test automatizado de desconexión/reconexión y gap >24h (`sync_required`). |
| HITL absoluto sin cola persistente offline | Persistir acciones en tabla tasks; no depender solo de estado WS. |
| 5 roles aumentan complejidad de UI/permisos | Validar si E1 realmente necesita 5 roles; si no, simplificar a admin/operator y diferir auditor. |
| Performance targets exigentes | Medir Lighthouse/CLS desde el primer prototipo; no dejarlo para el final. |

**P4: ¿Qué criterios de "hecho" son auditablesm y qué evidencia se debe generar?**

- [ ] Lighthouse TTI <2.5s, LCP <1.5s, CLS <0.1 en página principal.
- [ ] WS message handler latency <16ms p95.
- [ ] Flujo approve/edit/reject persiste en DB y genera audit log.
- [ ] Optimistic update visual response <100ms.
- [ ] Todos los outputs `kind: asset` con destino externo pasan por Mesa antes de envío.

**Pregunta crítica — ¿Qué está underspecified y bloquea la implementación?**

¿Cuántos roles implementa realmente E1? El contrato dice 5, pero si el tenant MWT solo tiene CEO/AM, implementar 5 roles con permisos diferenciados es sobrediseño. Necesito confirmación de qué roles son obligatorios en la beta.

---

### S4 — Skill Factory y Seed Catalog (Semanas 9-10)

**P1: ¿Qué se construye y cuál es la entrega funcional mínima?**

Se implementa el Skill Studio: modelo de datos de skills (`skills`, `skill_versions`, `addons`, `skill_addon_bindings`), 3 capas (Base, Manual Overlay, Learned Overlay), 12 skills system precargadas + 2 skills custom MWT, validaciones de manifest, RLS, y UI básica de edición. La entrega mínima es poder crear/instanciar un skill, editar su manual overlay, y que el sistema valide el manifest.

**P2: ¿Qué decisiones arquitectónicas y de stack están fijadas (o pendientes) para este sprint?**

- **Fijadas:** entidad `Skill` única con campo `origin` (`sealed`/`open`); add-ons como entidades separadas; Base inmutable para sealed; overlays editables; fork de sealed → open; golden samples obligatorios para outputs `kind: asset` (`SPEC_FABERLOOM_SKILL_COMPOSITION_v1`).
- **Fijadas:** schema v2 con `metadata.mwt.*` extendiendo SKILL.md; validaciones build-time (`SCH_FB_SKILL_MANIFEST_v2`).
- **Pendiente:** el SPEC de composición es DRAFT y **no tiene seed catalog aprobado**. §11 presenta opciones A/B/C sin decisión CEO. Sin seed, no se puede poblar la DB.

**P3: ¿Qué riesgos de implementación ve el integrador y qué mitigación propone?**

| Riesgo | Mitigación |
|--------|-----------|
| Seed catalog no decidido | CEO debe elegir opción A/B/C antes de S4; sin eso no se diseña el contenido de las tablas. |
| 12+2 skills en un sprint es scope inflado | Priorizar 3-5 skills críticos (ej. triage, proforma, compliance); el resto como stubs aprobados. |
| Namespace `metadata.mwt.*` | Renombrar a `metadata.fbl.*` en S1A o mantener alias permanente; no dejar deuda latente. |
| Migración de 10 skills legacy a v2 | Hacerla progresiva; no intentar migrar todas en S4. |
| Add-ons con costo de ingesta | Definir unit economics básicos antes de habilitar `living_corpus`. |

**P4: ¿Qué criterios de "hecho" son auditablesm y qué evidencia se debe generar?**

- [ ] 12 system + 2 MWT skills cargados en DB (aunque algunos sean stubs).
- [ ] Skill Studio permite editar manual overlay sin tocar Base.
- [ ] Validación de manifest pasa para cada skill seed.
- [ ] Fork de sealed crea open con `forked_from` y trazabilidad.
- [ ] RLS impide que un tenant vea skills de otro.

**Pregunta crítica — ¿Qué está underspecified y bloquea la implementación?**

¿Qué 3 skills concretos forman el seed de Fase 1? `SPEC_FABERLOOM_SKILL_COMPOSITION_v1` §11 lista opciones A/B/C sin decisión. Sin seed aprobado no se puede diseñar la DB, ni los placeholders, ni los golden samples.

---

### S5 — Agent Factory y Orquestación (Semanas 11-12)

**P1: ¿Qué se construye y cuál es la entrega funcional mínima?**

Se construye el Agent Factory: orquestador delgado, cadena lineal de skills, templates (`TPL_REVIEW_TRIAGE`, `TPL_QUOTE_GENERATOR_B2B`, `TPL_LEAD_QUALIFIER_B2B`), validaciones por arquetipo arquitectónico, `skills_imports`, flow DAG declarativo, y tasks como entidad de primera clase. La entrega mínima es instanciar un agente a partir de un template, ejecutar su cadena lineal, y que cada paso genere una task trazable.

**P2: ¿Qué decisiones arquitectónicas y de stack están fijadas (o pendientes) para este sprint?**

- **Fijadas:** single-agent por task (TIER 1 #15); no sub-agentes en runtime E1; architectural archetype obligatorio (`ENT_FB_AGENT_ARCHETYPES_v1`); outputs plural; kill switch; conector dumb / agent smart (`SPEC_FB_AGENT_BUILDER_v1` D16).
- **Fijadas:** tareas como entidad `tasks` con state machine (queued → running → awaiting_approval → completed/failed/cancelled/timeout) (`SCH_FB_TASK_ENTITY`).
- **Pendiente:** `SPEC_FB_AGENT_BUILDER_v1` asume como primer agente objetivo `SKILL_RW_REVIEW_TRIAGE` de MWT/Rana Walk, mientras Foundation Beta apunta al wedge de cotización B2B (safety footwear). Hay tensión en el orden de agentes y los datos operacionales necesarios.

**P3: ¿Qué riesgos de implementación ve el integrador y qué mitigación propone?**

| Riesgo | Mitigación |
|--------|-----------|
| Orden de agentes contradictorio | Alinear con CEO: si el wedge es cotización B2B, priorizar `TPL_QUOTE_GENERATOR_B2B`; si es reviews, priorizar `TPL_REVIEW_TRIAGE`. |
| DAG declarativo sin UI visual | Proveer editor YAML/JSON en Mesa con validación build-time; documentar schema. |
| Skill_package vs agent en migración legacy | Clasificar cada skill legacy en una de las dos categorías antes de migrar. |
| Cadena lineal con skills imports | Validar ciclos de imports y versiones en build-time. |
| Kill switch sin acción definida | Implementar auto-pause y notificación CEO cuando se dispare. |

**P4: ¿Qué criterios de "hecho" son auditablesm y qué evidencia se debe generar?**

- [ ] Al menos 3 templates funcionan end-to-end (instanciación → ejecución → task).
- [ ] Orquestador respeta cadena lineal y no invoca sub-agentes.
- [ ] Tasks persisten con state machine en DB y son visibles en Mesa.
- [ ] Validaciones build-time (28 reglas de `SCH_FB_SKILL_MANIFEST_v2`) ejecutándose en CI.
- [ ] Cada template tiene golden samples para outputs `kind: asset`.

**Pregunta crítica — ¿Qué está underspecified y bloquea la implementación?**

¿El primer agente objetivo es cotización B2B (Foundation Beta wedge) o review triage (Agent Builder plan)? Esto determina qué templates, datos operacionales y métricas se preparan en S4-S5, y qué éxito se mide en S8-S10.

---

### S6 — StackLoom, Knowledge Atlas y Knowledge River (Semanas 13-14)

**P1: ¿Qué se construye y cuál es la entrega funcional mínima?**

Se implementa el sistema de conocimiento: Knowledge Atlas con 7 vistas y 11 tipos de nodo, Knowledge River con capas L0-L4, Context Pack Trace que reduce tokens vs retrieval naive, freshness de fuentes source-of-truth, y governance/audit de candidatos. La entrega mínima es tener un grafo navegable de conocimiento del tenant, con al menos L0-L2 operativos y trazabilidad de qué entra en el contexto de un run.

**P2: ¿Qué decisiones arquitectónicas y de stack están fijadas (o pendientes) para este sprint?**

- **Fijadas:** Knowledge Atlas como consola medular (`SPEC_FB_KNOWLEDGE_ATLAS_v1`); Knowledge River en 2 capas separadas (usuario L0-L2, organización L3-L4) sin auto-promote; `k-anon ≥ 5` para L3/L4; Context Pack Trace con pipeline RUN→ROUTER→SOURCES→BUILDER→COMPILER→LEDGER→AUDIT (`SPEC_FB_KNOWLEDGE_RIVER_v1`).
- **Fijadas:** 14 fuentes source-of-truth con freshness SLA (`SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1`).
- **Pendiente:** backend de nodes/edges no está detallado; `SPEC_FB_DATA_MODEL_v1` es la referencia pero no especifica un graph store.

**P3: ¿Qué riesgos de implementación ve el integrador y qué mitigación propone?**

| Riesgo | Mitigación |
|--------|-----------|
| Scope visual muy ambicioso para un sprint | Entregar Atlas MVP: 2-3 vistas (Atlas básico + River + Governance) y grafo simple; dejar inspector completo para E2. |
| k-anon ≥5 imposible con 1 AM en MWT | Mantener capa 2 dormida hasta multi-AM; no forzar L3/L4 sin usuarios suficientes. |
| Backend de grafos no definido | Decidir si se usa Postgres adjacency list, pgvector, o graph DB; documentar en ADR. |
| 14 fuentes source-of-truth | Priorizar 5 fuentes críticas para el wedge; las demás como backlog. |
| Curador overhead | Si MWT v1 tiene un solo curador, simplificar gobernanza a modo A (curador único). |

**P4: ¿Qué criterios de "hecho" son auditablesm y qué evidencia se debe generar?**

- [ ] Atlas muestra nodos y edges para L0-L2 de al menos 1 template.
- [ ] River L0-L2 fluye con al menos 1 skill y 1 gold sample.
- [ ] Context Pack Trace reduce tokens >50% vs naive retrieval para un caso de prueba.
- [ ] Freshness SLA medible para 5+ fuentes críticas.
- [ ] Audit log de cambios en L4 (firmas) inmutable.

**Pregunta crítica — ¿Qué está underspecified y bloquea la implementación?**

¿Cuál es el backend de grafos? `SPEC_FB_KNOWLEDGE_ATLAS_v1` §11 dice que el backend de nodes/edges vive en `SPEC_FB_DATA_MODEL_v1`, pero no se encontró especificación de un graph store. Sin decidir si se usa Postgres adjacency list, pgvector, Neo4j o similar, no se puede implementar el grafo SVG navegable.

---

### S7 — Workspace Conversacional, Modos y Rutinas (Semanas 15-16)

**P1: ¿Qué se construye y cuál es la entrega funcional mínima?**

Se implementa el workspace conversacional: workspace asociado a una cuenta/cliente, 3 modos de operación (assistant, supervisor, autopilot), rutinas programadas, automatizaciones ancladas a entidades, y Voice Humanizer simplificado. La entrega mínima es que un usuario pueda abrir un workspace, pedirle una acción al sistema en modo assistant, y recibir un draft para aprobación.

**P2: ¿Qué decisiones arquitectónicas y de stack están fijadas (o pendientes) para este sprint?**

- **Fijadas:** workspace = cuenta (modelo `workspaces=cuenta`, CEO 2026-05-07); todo workspace tiene `controlled_by` user obligatorio; 3 modos con HITL absoluto; autopilot bounded (`SPEC_FB_VOICE_HUMANIZER_v2` §6, `PLB_FB_FOUNDATION_BETA_v1`).
- **Fijadas:** Voice Humanizer E1-E2 colapsado a bloque de estilo + few-shot + filtros; resolución property-by-property diferida a E3+.
- **Pendiente:** `ENT_PLAT_AUTOMATIONS.md` es VIGENTE pero genérico; no define integración específica con rutinas de FaberLoom ni con `SCH_FB_FLOW_DAG`.

**P3: ¿Qué riesgos de implementación ve el integrador y qué mitigación propone?**

| Riesgo | Mitigación |
|--------|-----------|
| Modelo de workspace ambiguo (cuenta vs cliente vs usuario) | Definir modelo de datos claro en S5: 1 workspace = 1 cuenta B2B; owner = `controlled_by` user. |
| 3 modos aumentan superficie de UI y runtime | Implementar assistant primero; supervisor luego; autopilot con kill switch y solo si hay evidencia. |
| Rutinas requieren cron + task engine | Reutilizar Celery beat + tabla tasks; definir schema de triggers `cron`. |
| Automatizaciones con impacto financiero | Forzar `requires_approval=true` y CEO approval antes de activar (`ENT_PLAT_AUTOMATIONS.md` D2). |
| WhatsApp como canal P2 | No bloquear S7; tratar como spike opcional. |

**P4: ¿Qué criterios de "hecho" son auditablesm y qué evidencia se debe generar?**

- [ ] Workspace tiene `controlled_by` user obligatorio en DB.
- [ ] Modo assistant genera drafts y los envía a Mesa para aprobación.
- [ ] Rutina se dispara por cron y crea una task trazable.
- [ ] Automatización con impacto financiero requiere aprobación CEO registrada.
- [ ] Voice Humanizer aplica bloque de estilo + filtros en outputs de workspace.

**Pregunta crítica — ¿Qué está underspecified y bloquea la implementación?**

¿Qué es exactamente un "workspace" en la base de datos? Hay tensión entre workspace=cuenta, workspace=cliente B2B del tenant, y workspace de usuario. Sin modelo de datos claro y relación con `accounts`, `contacts` y `legal_entities`, S7 no puede arrancar.

---

### S8-S10 — SHADOW, Evidencia y Graduación (Semanas 17-19)

**P1: ¿Qué se construye y cuál es la entrega funcional mínima?**

Se ejecutan 3 agentes en modo SHADOW con datos reales del tenant (Review Triage, Lead Qualifier, Quote Generator), se acumula evidencia, se miden métricas L0-L5, y se decide graduación a ACTIVE según outcome accountability. La entrega mínima es un dashboard de evidencia con métricas por agente y un informe de graduación con recomendación.

**P2: ¿Qué decisiones arquitectónicas y de stack están fijadas (o pendientes) para este sprint?**

- **Fijadas:** P3 draft-first absoluto; P4 autonomía por evidencia; P15 outcome accountability con métricas send-rate, close-rate, SLA compliance, ponderadas por severity (`SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1`, `ARCH_AGENT_PRINCIPLES`).
- **Fijadas:** SHADOW 30 días mínimo; promotion criteria: runs ≥100, acceptance ≥0.90, schema compliance ≥0.99, etc. (`SCH_FB_SKILL_MANIFEST_v2`).
- **Pendiente:** `POL_FB_OUTCOME_ACCOUNTABILITY.md` está referenciado pero **no existe** en el repo.

**P3: ¿Qué riesgos de implementación ve el integrador y qué mitigación propone?**

| Riesgo | Mitigación |
|--------|-----------|
| `POL_FB_OUTCOME_ACCOUNTABILITY.md` no existe | Redactar política antes de S8 con thresholds, cadencia de medición y responsables. |
| 3 agentes × 30 días SHADOW no caben secuencialmente en 3 sprints | Paralelizar SHADOW o reducir a 1-2 agentes críticos; extender timeline si es necesario. |
| Baseline manual no realizado | Ejecutar Sem 0 baseline manual antes de SHADOW; sin baseline no hay contrafactual. |
| Métricas L5 requieren integración con sistemas operacionales (SAP, Amazon) | Asegurar conectores en S2-S5 antes de medir outcome. |
| Acceptance rate alto (0.90) puede ser poco realista para arranque | Calibrar thresholds con CEO; usar SHADOW para aprender, no solo para pasar. |

**P4: ¿Qué criterios de "hecho" son auditablesm y qué evidencia se debe generar?**

- [ ] Dataset ≥100 runs por agente en SHADOW.
- [ ] Métricas L0-L5 visibles en dashboard.
- [ ] Acceptance rate, schema compliance y costo dentro de umbrales declarados.
- [ ] Outcome metric se mueve vs baseline documentado.
- [ ] Reporte de graduación con recomendación SHADOW→ACTIVE firmado.

**Pregunta crítica — ¿Qué está underspecified y bloquea la implementación?**

¿Dónde está `POL_FB_OUTCOME_ACCOUNTABILITY.md`? Todos los specs de SHADOW y graduación lo citan, pero el archivo no existe. Sin thresholds formales de graduación, SHADOW no produce una decisión objetiva.

---

### S11-S13 — Beta con Amigos, Multi-tenant y Operaciones (Semanas 20-22)

**P1: ¿Qué se construye y cuál es la entrega funcional mínima?**

Se abre la beta con 5 tenants amigos: onboarding, multi-tenant lógico validado, DPA legal, operaciones (runbooks, soporte), métricas de uso, y roadmap v2. La entrega mínima es tener 5 tenants provisionados con RLS, datos reales no sensibles (o con DPA), y un procedimiento de soporte/escalación documentado.

**P2: ¿Qué decisiones arquitectónicas y de stack están fijadas (o pendientes) para este sprint?**

- **Fijadas:** multi-tenant lógico vía `tenant_id` desde día 1; no multi-tenant cripto/A2A/profile system en E1 (`SPEC_FB_AGENT_BUILDER_v1` D1); DPA antes de S10 o limitar a mensajes no sensibles; restore test demostrado pre-S10; data classification N0-N2 en Foundation Beta, N3/N4 con DPA (`POL_DATA_CLASSIFICATION`).
- **Pendiente:** el plan habla de 5 tenants amigos, pero `SPEC_FB_AGENT_BUILDER_v1` D1 dice "FB v1 single-tenant beta (MWT primer tenant)" y multi-tenant productivo queda para v2 con segundo tenant pagante.

**P3: ¿Qué riesgos de implementación ve el integrador y qué mitigación propone?**

| Riesgo | Mitigación |
|--------|-----------|
| Tensión "5 tenants amigos" vs "single-tenant beta MWT" | Definir si son workspaces/clientes dentro del tenant MWT o tenants reales. Impacta RLS, hosting y pricing. |
| DPA legal no redactado | Iniciar redacción en S1A/S2; sin DPA, bloquear datos N3/N4. |
| Capacidad de KVM 8 con 5 tenants | Estimar carga; evaluar escalado vertical o migración si es necesario. |
| Onboarding sin runbook | Crear checklist de provisionamiento, seed de skills y voice profile por tenant. |
| Soporte/escalación no definido | Definir canal de soporte, SLA de respuesta y runbook de incidentes P0/P1. |

**P4: ¿Qué criterios de "hecho" son auditablesm y qué evidencia se debe generar?**

- [ ] 5 tenants amigos provisionados con RLS activo.
- [ ] DPA firmado o evidencia de limitación a datos N0-N2.
- [ ] Restore test demostrado en producción con documentación.
- [ ] Runbooks de incidentes, escalación y onboarding publicados.
- [ ] Métricas de uso por tenant disponibles en dashboard.

**Pregunta crítica — ¿Qué está underspecified y bloquea la implementación?**

¿Los 5 tenants amigos son multi-tenant reales o 5 workspaces/clientes dentro del tenant MWT? Foundation Beta habla de 5 tenants amigos, pero `SPEC_FB_AGENT_BUILDER_v1` D1 fija FB v1 como single-tenant beta (MWT). Esto es un conflicto de arquitectura, costos y modelo de datos que debe resolverse antes de S11.

---

## 3. Hallazgos priorizados

### P0 — Bloqueantes (no se puede empezar implementación sin resolver)

1. **Fuente de verdad duplicada/conflictiva.** `PLB_FB_FOUNDATION_BETA_v1` (FIRMADO, SaaS server-first, 13 sprints) vs `PLAN_DESARROLLO_FABERLOOM_v5` (DRAFT listo para ratificación, desktop/web dual, 13-16 semanas). Conflictos en definición de producto, stack, timeline y forma de despliegue.
2. **Stack tecnológico no alineado.** Foundation Beta: FastAPI + Next.js + Postgres + Redis + Celery + LiteLLM **Proxy** + 12 contenedores. Plan v5 / Agent Builder: FastAPI + LiteLLM **lib** + desktop app + 15 contenedores. Decisiones incompatibles para gateway LLM y frontend.
3. **Ausencia de política de outcome accountability.** `POL_FB_OUTCOME_ACCOUNTABILITY.md` es citado por `SCH_FB_SKILL_MANIFEST_v2`, `SPEC_FB_AGENT_BUILDER_v1` y `SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1`, pero **no existe** en el repo. Bloquea S8-S10.
4. **Seed catalog no decidido.** `SPEC_FABERLOOM_SKILL_COMPOSITION_v1` (DRAFT) §11 presenta 3 opciones (A/B/C) sin decisión CEO. Bloquea diseño de tablas y contenido de S4.

### P1 — Alto riesgo (puede retrasar o desviar)

1. `ENT_PLAT_OBSERVABILIDAD.md` es STUB vacío; S1B carece de especificación de SLIs/SLOs, alertas y runbooks.
2. `ENT_PLAT_CANALES_CLIENTE.md` es DRAFT con bloqueadores técnicos y prioridad Portal vs email; puede desviar S2 hacia un canal no priorizado por Foundation Beta.
3. Namespace `metadata.mwt.*` en lugar de `metadata.fbl.*`; deuda técnica que dificulta multi-tenant y confunde a nuevos developers.
4. `SPEC_FB_VOICE_BOOTSTRAP_v1` y `POL_FB_VOICE_LEARNING_v1` están pendientes; Voice Profile E1-E2 depende del bootstrap.
5. Backend de grafos de Knowledge Atlas no especificado; bloquea implementación del grafo SVG en S6.
6. Número real de roles E1 no confirmado: 5 roles del contrato vs posible simplificación operativa.

### P2 — Medio/bajo riesgo (seguimiento)

1. Varios archivos tienen frontmatter incompleto (reportado en `REPORTE_FB_STD_2026-06-23`).
2. Referencias colgantes/legacy parcialmente corregidas por FB-STD; persisten algunas wildcards y rutas históricas.
3. Deuda de migración de 10 skills legacy a manifest v2; no bloquea E1 si se hace progresivamente.
4. WhatsApp Cloud API y aprobación Meta no están en el roadmap detallado.
5. Pricing de skills/agentes tiene múltiples `$XXX [PENDIENTE]`.
6. `SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1` tiene pendientes de pricing y rate limiting.

---

## 4. Recomendaciones del integrador

1. **Congelar la fuente de verdad.** CEO debe ratificar `PLB_FB_FOUNDATION_BETA_v1` como plan de ejecución **o** aprobar `PLAN_DESARROLLO_FABERLOOM_v5` con un delta formal que explique qué pasa con Foundation Beta (¿se archiva? ¿se fusiona?). Hasta entonces, no se puede estimar ni asignar tareas.
2. **Producir specs bloqueantes antes de S1A:**
   - `POL_FB_OUTCOME_ACCOUNTABILITY.md` (thresholds de graduación).
   - `ENT_PLAT_OBSERVABILIDAD.md` (SLIs/SLOs, alertas, runbooks).
   - `SPEC_FB_VOICE_BOOTSTRAP_v1` (inicialización del perfil de voz).
   - Decisión CEO del seed catalog de skills (opción A/B/C).
3. **Resolver ambigüedades de modelo de datos:**
   - ¿Workspace = cuenta? ¿Tenant amigo = tenant real o cliente de MWT?
   - ¿5 roles E1 o simplificación a 2?
4. **Renombrar namespace `metadata.mwt.*` a `metadata.fbl.*` en S1A.** Incluir alias backward-compatible si es necesario, pero no propagar la deuda.
5. **Simplificar S6.** Entregar Atlas MVP (2-3 vistas) y no forzar L3/L4 hasta tener múltiples AMs. Decidir backend de grafos en S5.
6. **Realista con SHADOW.** 3 agentes × 30 días no caben en 3 sprints secuenciales. Opciones: paralelizar, reducir a 1-2 agentes, o extender timeline. Antes de SHADOW, ejecutar Sem 0 baseline manual.
7. **Definir DPA y data classification desde S1A.** Si los tenants amigos manejarán datos N3/N4, el DPA debe estar en curso; si no, acotar Foundation Beta a N0-N2 explícitamente.

---

## 5. Documentos auditados (referencias clave)

- `docs/PLB_FB_FOUNDATION_BETA_v1.md` — plan ejecutable 13 sprints (FIRMADO).
- `docs/PLAN_DESARROLLO_FABERLOOM_v5.md` — plan alternativo desktop/web dual.
- `docs/MANIFIESTO_APPEND_20260501_FOUNDATION_BETA_FIRMADO.md` — trazabilidad del contrato firmado.
- `docs/ARCH_AGENT_PRINCIPLES.md` — principios P0-P17.
- `docs/SPEC_ACTION_ENGINE.md` — motor de acciones.
- `docs/SPEC_FB_AGENT_BUILDER_v1.md` — 19 decisiones D1-D19 y plan 12 semanas.
- `docs/SPEC_FABERLOOM_SKILL_COMPOSITION_v1.md` — modelo sealed/open + add-ons (DRAFT).
- `docs/SCH_FB_SKILL_MANIFEST_v2.md` — schema de manifest v2.
- `docs/SPEC_FB_FRONTEND_REALTIME_STATE_v1.md` — estado frontend y WS.
- `docs/SPEC_FB_VOICE_HUMANIZER_v2.md` — voz con enmienda v2.1.
- `docs/SPEC_FB_KNOWLEDGE_ATLAS_v1.md` — consola de conocimiento.
- `docs/SPEC_FB_KNOWLEDGE_RIVER_v1.md` — modelo L0-L4 y gobernanza.
- `docs/SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1.md` — vertical AM y métricas 90d.
- `docs/ENT_PLAT_CANALES_CLIENTE.md` — canales B2B (DRAFT).
- `docs/ENT_PLAT_OBSERVABILIDAD.md` — stub vacío.
- `docs/ENT_PLAT_AUTOMATIONS.md` — automatizaciones genéricas.
- `docs/REPORTE_FB_STD_2026-06-23.md` — reporte de estandarización y conflictos.

---

*Fin del reporte.*
