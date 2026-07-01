# ENT_GOB_AGENTES — Registro de Agentes del Sistema
id: ENT_GOB_AGENTES
version: 2.2
status: DRAFT
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
aplica_a: [MWT]

---

## A. Propósito

Registro de agentes que operan sobre la KB. Define identidad, alcance, y herramientas de cada uno. Dos nomenclaturas coexisten:
- **RW-***: roles conceptuales (qué función cumplen)
- **AG-***: asignaciones operativas en LOTEs (quién ejecuta qué sprint)

Un AG puede cubrir múltiples RW (ej: Alejandro = AG-02 Copy + AG-07 Dev frontend).

---

## B. Agentes por rol

### RW-Ops (AG: [PENDIENTE — CEO asignar])
- **Rol:** Operaciones, expedientes, logística
- **Dominio:** IDX_OPS
- **PLBs:** PLB_OPS_AMAZON
- **Policies clave:** POL_DETERMINISMO, POL_STAMP, POL_INMUTABILIDAD
- **Herramientas:** Sistema de expedientes, State Machine, ENT_OPS_*

### RW-Copy / AG-02 (Alejandro)
- **Rol:** Contenido, listings Amazon, A+ Content, copy web
- **Dominio:** IDX_MARKETPLACE
- **PLBs:** PLB_COPY, PLB_INDEXACION
- **Policies clave:** POL_ROGERS, POL_CLAIMS_SCANNER, POL_NUNCA_TRADUCIR
- **Herramientas:** SCH_LISTING_AMAZON, SCH_APLUS_CONTENT, LOC_*
- **Nota:** Alejandro también opera como AG-07 (Dev frontend) en sprints de plataforma

### RW-Ads (AG: [PENDIENTE — CEO asignar])
- **Rol:** Publicidad Amazon PPC, campañas
- **Dominio:** IDX_MARKETPLACE
- **PLBs:** PLB_ADS
- **Policies clave:** POL_DETERMINISMO
- **Herramientas:** Amazon Advertising Console, Helium 10

### RW-Compliance (AG: [PENDIENTE — CEO asignar])
- **Rol:** Cumplimiento regulatorio, ISO, claims
- **Dominio:** IDX_COMPLIANCE
- **PLBs:** PLB_AUDIT_ISO
- **Policies clave:** POL_ROGERS, POL_CLAIMS_SCANNER, POL_CONSENTIMIENTO
- **Herramientas:** ENT_COMP_*, SCH_ISO_AUDIT_PACK

### RW-Growth (AG: [PENDIENTE — CEO asignar])
- **Rol:** Estrategia de crecimiento, expansión de mercados
- **Dominio:** IDX_MERCADOS, IDX_DISTRIBUCION
- **PLBs:** PLB_GROWTH, PLB_EXPERIMENTACION
- **Policies clave:** POL_IDEA_EVAL
- **Herramientas:** ENT_MERCADO_*, ENT_PROD_LANZAMIENTO

### RW-Support (AG: [PENDIENTE — CEO asignar])
- **Rol:** Soporte al cliente
- **Dominio:** IDX_MARKETPLACE
- **PLBs:** PLB_SUPPORT
- **Policies clave:** POL_DETERMINISMO
- **Herramientas:** Amazon Buyer Messages

### AG-03 (Dev Backend)
- **Rol:** Desarrollo backend, API, state machine
- **Dominio:** IDX_PLATAFORMA
- **PLBs:** PLB_API, PLB_QA
- **Asignación:** Sprints de plataforma (LOTE_SM_SPRINT*)
- **Herramientas:** Django, DRF, PostgreSQL


### AG-01 (Architect)
- **Rol:** Arquitectura de sistema, diseño de sprints, validación técnica
- **Dominio:** IDX_PLATAFORMA
- **PLBs:** PLB_ARCHITECT
- **Asignación:** Diseño de sprints, revisión de arquitectura
- **Herramientas:** RW_ROOT, SCHEMA_REGISTRY, DEPENDENCY_GRAPH

### AG-06 (QA)
- **Rol:** Control de calidad, testing, validación de entregables
- **Dominio:** IDX_PLATAFORMA
- **PLBs:** PLB_QA
- **Asignación:** Validación post-sprint
- **Herramientas:** health_check.sh, PLB_AUDIT

---

## C. Reconciliación nomenclaturas

| AG-ID | Nombre | Roles RW | Sprints asignados |
|-------|--------|----------|-------------------|
| AG-02 | Alejandro | RW-Copy | LOTEs 1-7 (Copy + API) |
| AG-03 | [PENDIENTE] | Dev Backend | LOTEs 1-7 (Backend) |
| AG-07 | Alejandro | Dev Frontend | LOTEs 8-9 (UI) |
| [PENDIENTE] | [CEO asignar] | RW-Ops | — |
| [PENDIENTE] | [CEO asignar] | RW-Ads | — |
| [PENDIENTE] | [CEO asignar] | RW-Compliance | — |
| [PENDIENTE] | [CEO asignar] | RW-Growth | — |
| [PENDIENTE] | [CEO asignar] | RW-Support | — |
| AG-01 | [PENDIENTE] | Architect | LOTEs 1-2 (diseño) |
| AG-06 | [PENDIENTE] | QA | LOTEs 1-7 (validación) |

---

---

## D. Modelo de 5 Agentes — Validado en sesión 2026-03-14/15

| Agente | Rol | Cuándo | Fortaleza validada |
|--------|-----|--------|-------------------|
| Claude (Opus) | Arquitecto ejecutor | Cada sesión | Construye, corrige, ensambla. No puede auditar lo que construyó en la misma sesión |
| Perplexity | Auditor de continuidad | Post-sesión / cada 2-3 semanas | Contexto acumulado, tracking entre sesiones, detección de regresiones |
| ChatGPT | Auditor de punto ciego | Cada milestone / cada 6 semanas | Ojos frescos sin contexto, encuentra lo que otros normalizan |
| Gemini | Investigador externo | Por pregunta de research | Regulatorio, mercado, benchmarks. Hallazgos se indexan como [HALLAZGO LLM] |
| DeepSeek | Revisor técnico | Post-sprint / entrega de código | Code review, validación specs vs implementación, bugs en scripts |

### Ciclo operativo
CEO opera → Claude ejecuta → Perplexity verifica continuidad → cada milestone ChatGPT audita → DeepSeek revisa código → hallazgos vuelven a Claude → Perplexity verifica fixes

### Principio
Cinco agentes, cinco roles, cero solapamiento. Cada uno entra cuando su fortaleza específica es la que hace falta.

---

## E. Agentes de servicio B2B (nomenclatura SVC-*)

Agentes autónomos que interactúan con clientes. Conceptualmente separados de los agentes internos (AG-*, RW-*) y del modelo de 5 agentes IA del CEO (sección D).

| Nomenclatura | Tipo | Audiencia |
|-------------|------|-----------|
| AG-* / RW-* | Personas o LLMs que ayudan al CEO | Interna |
| Sección D | 5 agentes IA del CEO | Interna |
| **SVC-*** | **Agentes autónomos de servicio al cliente** | **Externa (clientes B2B)** |

### SVC-01: Asistente de expedientes

- **Tipo:** AI Middleware autónomo (mwt-knowledge container)
- **Opera:** 24/7, sin intervención humana para consultas estándar
- **Canales:** portal B2B (P1), WhatsApp (P2 — futuro), email (P3 — futuro)
- **Permisos:** hereda JWT del cliente. VIEW_EXPEDIENTES_OWN, DOWNLOAD_DOCUMENTS, ASK_KNOWLEDGE_PRODUCTS, ASK_KNOWLEDGE_OPS
- **Fuentes de datos:** PostgreSQL directo (expedientes OWN) + pgvector (knowledge PUBLIC)
- **Limitaciones:** no negocia, no cotiza, no modifica datos, no revela CEO-ONLY, no accede datos de otros clientes
- **Escalamiento:** notifica CEO inmediatamente cuando intención fuera de scope
- **Idiomas:** ES (Tecmater/CR), PT-BR (Sondel-Marluvas/BR). Ref → ENT_PLAT_CANALES_CLIENTE.D
- **Ref → PLB_INTERACCION_CLIENTE** para reglas completas de interacción
- **Ref → ENT_PLAT_CANALES_CLIENTE** para canales y auth
- **Ref → ENT_PLAT_KNOWLEDGE.E3** para routing de consultas

### SVC-02, SVC-03... [PENDIENTE — se crean cuando haya más servicios B2B autónomos]

---
Changelog:
- v0.1 (2026-03-14): STUB original.
- v1.0 (2026-03-14): expandido con registro de 7 roles + reconciliación AG/RW (F-4).
- v2.1 (2026-03-15): +sección E "Agentes de servicio B2B" con nomenclatura SVC-*. SVC-01 Asistente de expedientes. Iteración Claude↔Perplexity aprobada.
- v2.2 (2026-04-01): PLB_OPS absorbido en PLB_OPS_AMAZON. PLB_COMPLIANCE eliminado. Depuración Q2-2026.
