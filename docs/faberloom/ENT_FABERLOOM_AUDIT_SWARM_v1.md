AGENTE 9 — SINTETIZADOR CROSS-AGENTE
==================

RESUMEN EJECUTIVO
-----------------
El swarm coincide en que FaberLoom tiene una arquitectura de diseño sólida (HITL absoluto, RLS, audit trail D10, wedge MWT/Marluvas), pero **no existe una fuente de verdad ejecutable única** para Foundation Beta. Los agentes técnicos (A1, A2, A8), de seguridad (A5), de producto (A6) y competidor (A7) señalan que el proyecto arrastra **contradicciones de stack, forma de producto y especificaciones faltantes** que bloquean el inicio de la implementación. El riesgo principal es construir sobre planos incompatibles y descubrir el conflicto en la semana 4-5 con un refactor costoso. La fortaleza principal es el consenso cross-agente en que el principio "draft-first absoluto" es el diferenciador correcto y debe preservarse a toda costa.

SINTESIS CROSS-AGENTE
=====================

Top 5 problemas identificados por más de un agente
---------------------------------------------------

1. **Fuente de verdad duplicada y stack contradictorio**
   - **Agentes:** A1, A2, A5, A8.
   - **Problema:** Existen al menos dos planes vigentes incompatibles: `PLB_FB_FOUNDATION_BETA_v1` (SaaS server-first, FastAPI + Next.js + Postgres + Redis + Celery + LiteLLM Proxy, 13 sprints) y `PLAN_DESARROLLO_FABERLOOM_v5` (desktop/web dual, FastAPI + LiteLLM lib, 13-16 semanas). A1 añade una tercera contradicción interna: Django + Celery + Redis (MWT/ENT_PLAT_INFRA) vs FastAPI + RabbitMQ + ARQ/pgboss (blueprint FaberLoom).
   - **Por qué es crítico:** Un backend/frontend developer no puede empezar a escribir código sin saber qué framework, broker de tareas, gateway LLM y forma de despliegue usar. A8 advierte que arrancar S1A con esta dualidad garantiza refactor masivo en semanas 4-5.
   - **Evidencia concreta:** A8 cita que Foundation Beta fija 12 contenedores Docker Compose con LiteLLM Proxy, mientras `PLAN_DESARROLLO_FABERLOOM_v5` y `SPEC_FB_AGENT_BUILDER_v1` asumen LiteLLM lib y desktop-first con 15 contenedores. A1 cita `DEC-001` que dice "Sin event bus, sin microservicios, sin Celery workers en MVP", mientras `ENT_PLAT_INFRA.md` y `PLAN_DESARROLLO_FABERLOOM_v4.md` listan Celery.

2. **Automatizaciones sin especificación ni entidad unificada**
   - **Agentes:** A1, A2, A8.
   - **Problema:** No existe una tabla `automations`/`automation_runs` con shape único, ni endpoints REST ni eventos WebSocket para la Zona 5 de la Mesa de Control.
   - **Por qué es crítico:** Bloquea la Zona 5 de la Mesa, el Routine Hub del Workspace y cualquier scheduler unificado. A2 lo marca como P0 que bloquea S5/S7.
   - **Evidencia concreta:** A1 encuentra solo `scheduled_jobs`, `job_execution` (sin `tenant_id`) y `workflow_runs` sin FK ni RLS común. A2 verifica que `SPEC_FB_INTEGRATION_LAYER_v1.md` no incluye `/api/v1/automations` y los 28 eventos WS canónicos no incluyen `automation.enabled/disabled/triggered`. A8 señala que `ENT_PLAT_AUTOMATIONS.md` es VIGENTE pero genérico y no define integración con rutinas de FaberLoom.

3. **RLS y aislamiento multi-tenant no implementados/insuficientes**
   - **Agentes:** A1, A5, A7, A8.
   - **Problema:** El diseño de RLS existe en papel, pero solo `memory_chunk` tiene policy detallada; el resto de tablas tienen policy genérica o no tienen `tenant_id`, y el plan vigente prioriza desktop single-user con SQLite.
   - **Por qué es crítico:** Sin RLS real no se puede vender a clientes regulados ni garantizar que un tenant no vea datos de otro. A5 declara que no está listo para banca, gobierno ni hospitales.
   - **Evidencia concreta:** A1 documenta que faltan políticas para `tasks`, `automations`, `audit_event`, `job_execution` y la capa Letta. A5 contrasta `SPEC_FB_AUTH_TENANT_RBAC_v1 §3.2` (exige RLS en todas las tablas tenant-scoped) contra `PLAN_DESARROLLO_FABERLOOM_v5 §2.2` (desktop single-user local-first con SQLite). A8 lista 20 tablas canon en `SCH_FB_CORE_TABLES_v1` que requieren RLS en S1A.

4. **Action Engine / PolicyGate / Audit trail D10 son contratos sin implementación**
   - **Agentes:** A1, A5, A7, A8.
   - **Problema:** El Action Engine, el hard block D9 por data classification y el audit trail inmutable D10 están especificados pero no codificados. `SPEC_AUDIT_MODULE.md` está planificado para Fase 4-5 post-MVP.
   - **Por qué es crítico:** Sin PolicyGate cada skill podría rutear datos N3/N4 a proveedores sin DPA; sin D10 no hay trazabilidad regulatoria ni replay. A5 lo califica como no listo para venta regulada.
   - **Evidencia concreta:** A1 señala que no existe DDL de `OutcomeLedger` ni módulo Django/FastAPI concreto. A5 cita que `SPEC_AUDIT_MODULE v1.1` define hash chain y storage tiers, pero el roadmap lo deja para Fase 4-5. A7 destaca que D10 es overkill para el ICP de $79/mes si no hay clientes Enterprise/Government.

5. **Especificaciones de entrada faltantes o en estado STUB/DRAFT**
   - **Agentes:** A2, A8.
   - **Problema:** Varios documentos que Foundation Beta asume como entrada no existen o están vacíos: `SPEC_FABERLOOM_MVP.md`, `SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md`, `SPEC_FABERLOOM_AGENT_COMPOSITION_v1.md`, `POL_FB_OUTCOME_ACCOUNTABILITY.md`, `ENT_PLAT_OBSERVABILIDAD.md` (stub vacío), `SPEC_FB_VOICE_BOOTSTRAP_v1`.
   - **Por qué es crítico:** Bloquean sprints enteros. Sin `POL_FB_OUTCOME_ACCOUNTABILITY.md` no hay criterios objetivos de graduación SHADOW (S8-S10). Sin observabilidad no se pueden definir SLIs/SLOs ni alertas (S1B).
   - **Evidencia concreta:** A2 confirma que los tres specs del prompt no existen en las rutas indicadas; su contenido está disperso. A8 verifica que `POL_FB_OUTCOME_ACCOUNTABILITY.md` es citado por `SCH_FB_SKILL_MANIFEST_v2`, `SPEC_FB_AGENT_BUILDER_v1` y `SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1`, pero el archivo no existe. A8 también documenta que `ENT_PLAT_OBSERVABILIDAD.md` es un STUB sin SLIs/SLOs.

Top 5 fortalezas confirmadas por más de un agente
--------------------------------------------------

1. **HITL absoluto / draft-first como diferenciador central**
   - **Agentes:** A3, A4, A5, A6, A7.
   - **Por qué importa:** Es el único diferenciador que los usuarios finales (María, Carlos), seguridad, producto y competidor validan como correcto. Reduce riesgo de errores comerciales graves, genera señales de aprendizaje y es defensible frente a auto-ejecución de Meta/HubSpot/Microsoft.

2. **Arquitectura de aislamiento multi-tenant bien pensada en papel**
   - **Agentes:** A1, A5, A7.
   - **Por qué importa:** RLS como source of truth, data classification N0-N4, pre-filtering en retrieval y P13 (aislamiento absoluto del aprendizaje) son un diseño sólido. Una vez implementado, es un diferenciador frente a Fengu, OpenAI Workspace Agents y soluciones genéricas.

3. **Wedge real con MWT/Marluvas (calzado de seguridad industrial)**
   - **Agentes:** A6, A7.
   - **Por qué importa:** Es un caso de uso angosto, repetible y de alto volumen con dataset propio sin costo de adquisición. Permite validar el loop RFQ → cotización → HITL → envío con datos reales desde el primer día.

4. **Diseño de audit trail inmutable D10**
   - **Agentes:** A1, A5, A7.
   - **Por qué importa:** Hash chain, storage tiers, auditor read-only API y attestation reports son correctos para sectores regulados. Aunque A7 señala que es overkill para PYMEs $79, es un activo de venta Enterprise/Government una vez implementado.

5. **Adapter pattern / work-type packs / Skill Manifest v2**
   - **Agentes:** A6, A7, A8.
   - **Por qué importa:** Permiten separar core universal de dominio específico y evitar overfit a MWT. Si se valida con un segundo work-type pack, evita que FaberLoom sea solo una herramienta de cotización de calzado.

3 decisiones que el CEO debe tomar antes de continuar
-----------------------------------------------------

1. **Ratificar UNA fuente de verdad de producto, stack y forma de despliegue**
   - **Decisión:** Elegir entre `PLB_FB_FOUNDATION_BETA_v1` (SaaS server-first) o `PLAN_DESARROLLO_FABERLOOM_v5` (desktop/web dual), y entre Celery/Redis vs RabbitMQ/ARQ/pgboss, y entre LiteLLM Proxy vs lib.
   - **Consecuencia de no tomarla:** Los developers no pueden iniciar S1A sin riesgo de refactor masivo en semanas 4-5. A1 y A8 advierten que se construirá sobre cimientos incompatibles.
   - **Owner sugerido:** CEO / CTO.
   - **Deadline sugerido:** Antes del kickoff de S1A (día 0).

2. **Definir el scope real de Foundation Beta: ¿5 tenants amigos reales o single-tenant MWT?**
   - **Decisión:** Resolver la tensión entre Foundation Beta (5 tenants amigos con RLS) y `SPEC_FB_AGENT_BUILDER_v1` D1 (FB v1 single-tenant beta MWT; multi-tenant productivo en v2).
   - **Consecuencia de no tomarla:** Impacta RLS, hosting (KVM 8), pricing por usuario, modelo de datos y costos. A8 documenta que esta ambigüedad bloquea S11-S13.
   - **Owner sugerido:** CEO / CPO.
   - **Deadline sugerido:** Antes de finalizar S1A (semana 2).

3. **Aprobar el seed catalog de skills y la política de outcome accountability**
   - **Decisión:** Elegir opción A/B/C del seed catalog en `SPEC_FABERLOOM_SKILL_COMPOSITION_v1` §11 y redactar `POL_FB_OUTCOME_ACCOUNTABILITY.md` con thresholds de graduación SHADOW.
   - **Consecuencia de no tomarla:** S4 (Skill Factory) no puede poblar la DB y S8-S10 no tienen criterios objetivos para graduar agentes de SHADOW a ACTIVE. A8 lo marca como P0 bloqueante.
   - **Owner sugerido:** CEO / Product Lead.
   - **Deadline sugerido:** Semana 3 (antes de S4).

Mapa de dependencias críticas para Foundation Beta
---------------------------------------------------

| Orden | Dependencia | Sprint / Agente que la necesita | Qué la bloquea |
|-------|-------------|----------------------------------|----------------|
| 1 | Fuente de verdad única (plan + stack) | S1A (A8, A1) | Conflicto Foundation Beta vs PLAN v5; LiteLLM Proxy vs lib; Celery vs RabbitMQ/ARQ |
| 2 | Especificación de observabilidad (`ENT_PLAT_OBSERVABILIDAD.md`) | S1B (A8) | Documento STUB vacío; sin SLIs/SLOs ni alertas |
| 3 | Modelo de tenant/workspace/roles | S1A-S3 (A8, A1, A2) | ¿5 tenants amigos reales o clientes dentro de tenant MWT? ¿5 roles o simplificación a 2? |
| 4 | RLS completa en ~20 tablas canon | S1A (A1, A8) | Solo `memory_chunk` tiene policy detallada; faltan policies para tasks, automations, audit_event |
| 5 | Action Engine + PolicyGate D9 + audit D10 | S2-S5 (A1, A5, A8) | Son contratos sin implementación; D10 post-MVP en roadmap |
| 6 | Seed catalog de skills aprobado | S4 (A8) | `SPEC_FABERLOOM_SKILL_COMPOSITION_v1` §11 presenta opciones A/B/C sin decisión CEO |
| 7 | Endpoints REST + eventos WS de automatizaciones | S5/S7 (A2, A1) | No existe tabla `automations`/`automation_runs` ni spec de Zona 5 |
| 8 | File upload endpoints | S3-S5 (A2) | `SPEC_FB_INTEGRATION_LAYER_v1` §11 los lista como diferidos |
| 9 | Algoritmo de detección de 3 modos del Workspace | S5/S7 (A2) | `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1` §8.5 los describe conceptualmente sin parser |
| 10 | Política de outcome accountability | S8-S10 (A8) | `POL_FB_OUTCOME_ACCOUNTABILITY.md` no existe en el repo |

HALLAZGOS POR AGENTE
====================

- **Agente 1 (Developer Backend):** Detecta que la KB tiene contratos sólidos (Action Engine, Skill Manifest v2, RLS/pgvector, Audit Module) pero dos stacks contradictorios (Django+Celery+Redis vs FastAPI+RabbitMQ+ARQ), tablas faltantes (`automations`/`automation_runs`), Action Engine sin implementación concreta, WebSocket no especificado y RLS incompleta más allá de `memory_chunk`.

- **Agente 2 (Developer Frontend):** Confirma una arquitectura de estado frontend sólida (TanStack Query + Zustand + WebSocket), pero bloquea S5/S7 por: specs obligatorios del prompt que no existen, Zona 5 Automatizaciones sin endpoints WS/REST, algoritmo de 3 modos del Workspace no especificado, file-upload endpoints diferidos y estados de WorkLoom no canonicalizados.

- **Agente 3 (Usuario Administrativo):** Valora el HITL absoluto y la Mesa de Control, pero advierte que el lenguaje técnico del primer día ("vertical_spec_object", "SANDBOX", "promote") asustará a usuarios como María; necesita onboarding en español de oficina, doble confirmación antes de enviar, y traducción humana de la pestaña "Evidencia".

- **Agente 4 (CEO PYME):** Considera interesante la promesa de control y el precio $79/mes, pero bloquea la compra si el onboarding requiere IT/SAP, si la IA se equivoca en datos críticos (SKU, precio, lead time) o si los add-ons ocultan un costo real mayor; necesita ver valor concreto en 2 semanas.

- **Agente 5 (Seguridad/Compliance):** Veredicto: NO se puede vender hoy a bancos, gobiernos u hospitales. Los controles D9, D10, RLS, PII scanner, DPA registry y breach notification son diseño sin implementación; además, el plan vigente prioriza desktop single-user, incompatible con requisitos enterprise/government.

- **Agente 6 (Product Manager):** El riesgo principal no es técnico sino de priorización y validación comercial. VCT mide eficiencia, no PMF; las 8 kill conditions no incluyen WTP/pago; hay tensión de canal no resuelta (WhatsApp vs email-first); y el adapter pattern no se ejercita con un segundo work-type pack antes de S13.

- **Agente 7 (Competidor/Crítico):** Los diferenciadores técnicos (StackLoom, D10, voice property-by-property) están aplazados a E3+/Fase 4-5, por lo que en E1 FaberLoom es esencialmente un RAG con HITL replicable por Meta/Microsoft/HubSpot. El precio $79/mes es vulnerable a freemium y el moat de gold samples aún no está validado.

- **Agente 8 (Integrador/Alejandro):** Como integrador no puede construir con dos planes contradictorios. P0: fuente de verdad duplicada, stack no alineado, `POL_FB_OUTCOME_ACCOUNTABILITY.md` inexistente y seed catalog no decidido. P1: observabilidad stub, canales cliente DRAFT con prioridad Portal vs email, namespace `metadata.mwt.*`, y backend de grafos no definido.

RECOMENDACIONES PRIORITARIAS
============================

P0 (bloquea Foundation Beta)
----------------------------

1. **Congelar una única fuente de verdad antes de S1A.** CEO debe ratificar `PLB_FB_FOUNDATION_BETA_v1` o aprobar `PLAN_DESARROLLO_FABERLOOM_v5` con un delta formal que explique qué pasa con el contrato firmado. Sin esto no se puede estimar ni asignar tareas (A1, A8).
2. **Resolver el stack tecnológico:** framework backend (Django vs FastAPI), broker/workers (Celery+Redis vs RabbitMQ+ARQ/pgboss), gateway LLM (LiteLLM Proxy vs lib), y forma de despliegue (SaaS server vs desktop local-first) (A1, A8).
3. **Definir el modelo de tenant/workspace/roles:** ¿5 tenants amigos reales o clientes dentro del tenant MWT? ¿5 roles E1 o simplificación operativa? (A8, A2).
4. **Producir `POL_FB_OUTCOME_ACCOUNTABILITY.md` y aprobar seed catalog de skills (opción A/B/C)** antes de S4 y S8-S10 (A8).
5. **Diseñar e implementar la entidad `automations`/`automation_runs`** con endpoints REST, eventos WS, FK, RLS e índices, o unificar `scheduled_jobs` + `job_execution` + `workflow_runs` bajo un modelo común (A1, A2, A8).
6. **Implementar RLS completa** en las ~20 tablas canon con `FORCE ROW LEVEL SECURITY`, no solo en `memory_chunk` (A1, A5, A8).
7. **Codificar Action Engine + PolicyGate D9 + audit D10** como runtime, no solo como contratos; al menos un audit log append-only operacional desde S1A (A1, A5, A8).

P1 (importante)
---------------

1. **Especificar el protocolo WebSocket completo:** auth en handshake, heartbeat, reconexión, invalidación de sesión, rooms/channels por tenant, y eventos faltantes (`automation.enabled/disabled/triggered`, `draft.reassigned`, `task.delegated`) (A1, A2).
2. **Producir endpoints de file upload** con límites, MIME allowlist, destinos (`workspace_attachment`, `kb_candidate`, `mesa_evidence`) y progreso (A2).
3. **Definir el algoritmo de detección de los 3 modos del Workspace** (Operar/Automatizar/Construir) y el body del chat por modo (A2).
4. **Redactar `ENT_PLAT_OBSERVABILIDAD.md` a VIGENTE** con SLIs/SLOs, alertas, retención y runbooks antes de S1B (A8).
5. **Canonicalizar los estados de WorkLoom** en un único documento y actualizar `PLAN_DESARROLLO_FABERLOOM_v5` o `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1` con nota de supersede (A2).
6. **Vincular métricas de Foundation Beta a validación comercial:** añadir kill condition de WTP/pago y experimento de ancla de precio en E2.5 (A6).
7. **Resolver tensión de canal:** si el vertical opera por WhatsApp, validar con WhatsApp; si no es posible, documentar el sesgo de email-first (A6, A7).
8. **Iniciar DPA registry y data classification operativa** para no bloquear datos N3/N4 en S10-S11 (A5, A8).

P2 (mejora)
-----------

1. **Renombrar namespace `metadata.mwt.*` a `metadata.fbl.*`** en S1A para evitar deuda técnica (A1, A8).
2. **Simplificar lenguaje técnico en onboarding** y traducir "Evidencia" a "¿de dónde sacó cada dato?" para usuarios no técnicos (A3, A4).
3. **Producir mocks faltantes:** Mesa de Control v6 con 5 zonas, Workspace en modo Automatización/Construcción, y SpaceLoom E1 desktop (A2).
4. **Definir endpoint y schema de Contexto Activo** (`GET /api/v1/context` o similar) para evitar que cada surface invente su propio `context_pack` (A2).
5. **Diseñar Voice Profile bootstrap simplificado** con 3 preguntas iniciales y ajuste automático con el uso (A3, A8).
6. **Planear benchmark de pgvector + RLS** y plan B (Pinecone/Qdrant) antes de comprometer arquitectura multi-tenant a escala (A7, A1).
7. **Documentar procedimiento de notificación de brechas** (`PLB_INCIDENT_RESPONSE`) con tiempos por jurisdicción y RACI (A5).

---

*Reporte generado por Agente 9 — Sintetizador Cross-Agente.*
*Fuentes: reportes de A1-A8. No se consultó el repo canónico.*
