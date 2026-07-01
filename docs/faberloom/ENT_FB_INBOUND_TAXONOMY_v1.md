# ENT_FB_INBOUND_TAXONOMY_v1 -- 13 tipos de inbound FaberLoom
id: ENT_FB_INBOUND_TAXONOMY_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: ENT
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: ENT_FB_DECISIONES_E1_v1.md · SPEC_FB_EVENTING_AND_OUTBOX_v1.md · SPEC_ACTION_ENGINE.md

---

## Declaracion

Todo trabajo entra por alguno de los 13 tipos de inbound.
FaberLoom es omnicanal desde S1A (ENT_FB_DECISIONES_E1_v1 D1).
El Action Engine normaliza todo a feed_item con source declarado.

---

## 1. Los 13 tipos

### Categoria A -- Pasivo externo

# | Origen | Evento | Destino WorkLoom | Sprint
1 | WhatsApp BSP cliente | feed.item.received source=whatsapp | Listo para revisar | S1A
2 | Gmail/IMAP email | feed.item.received source=email | Listo para revisar | S1A
3 | Webhook SP-API/ERP/CRM | feed.item.received source=webhook | skill segun source | S2
4 | Scheduler cron/SLA | automation trigger | rutina Proceso | S3

### Categoria B -- Pasivo interno

# | Origen | Evento | Destino WorkLoom | Sprint
5 | Agente draft generado | draft.generated | Listo para revisar | S1B
6 | Otro usuario approval | feed.item.received source=internal | Listo para revisar | S5
7 | Agente escalacion | agent.alarma | Critico | S3
8 | Audit worker alert | feed.item.received source=audit | Critico (Owner/Admin) | S6
9 | Rutina disparada | automation_run.completed | Listo para revisar si accionable | S7
10 | Task asignada | feed.item.received source=task_assign | Listo para revisar | S5
11 | SLA breach / freshness | freshness.violation | Critico | S3

### Categoria C -- Activo usuario

# | Origen | Evento | Destino WorkLoom | Sprint
12 | Upload archivo Workspace | feed.item.received source=workspace_upload | L1 clasifica | S7
13 | Inicio tarea Workspace | task (invocation_mode=ad_hoc) | WorkLoom o directo | S7

---

## 2. Flujo procesamiento

### Tipos 1-3 (canal externo)
MCP connector dumb pipe (max 5 nodos, sin LLM, sin logica negocio)
--> Action Engine ActionContext
--> P14: Tier 0 deterministic --> L1 Classifier si no resuelve
--> D9 Policy Gate: N3/N4 sin DPA = HARD BLOCK
--> L2 Dispatcher --> L3 Prompt Compiler --> Skill execution
--> WorkLoom si requires_human_gate=true
--> Audit D10 (siempre)

### Tipo 4 (scheduler)
Celery Beat --> worker-agent --> pre_condition deterministica
--> Action Engine (mismo path que 1-3)
--> WorkLoom si accionable / log si ruido

### Tipos 5-11 (interno)
Sistema genera evento --> Redis Streams --> worker-default
--> segun event_type: Listo para revisar o Critico
--> WebSocket push --> Electron actualiza sin reload

### Tipos 12-13 (usuario activo)
Upload --> MinIO --> L1 clasifica --> Action Engine
Tarea --> task ad_hoc --> Action Engine

---

## 3. Matriz evento --> columna kanban WorkLoom

draft.generated           --> Listo para revisar    badge
agent.alarma              --> Critico               Telegram
freshness.violation       --> Critico               Telegram
feed.item.received externo --> Listo para revisar   badge
automation_run accionable --> Listo para revisar    badge
automation_run ruido      --> NO va a WorkLoom      log only
cost.threshold            --> Critico               Telegram + email Owner
sha_chain.broken          --> Critico P0            Telegram inmediato

---

## 4. Data class por canal

WhatsApp cliente  --> N2 default, puede subir a N3
Gmail cliente     --> N2 default, puede subir a N3
SP-API Amazon     --> N1 default, puede subir a N2
ERP/SAP externo   --> N3 default, puede subir a N4
Workspace upload  --> L1 infiere N0-N4
Internal user     --> N1 default, puede subir a N2

Data class se hereda: inbound --> feed_item --> task --> draft --> audit D10.
Si L1 detecta N3/N4: D9 hard block antes de cualquier LLM call.

---

## 5. MCP connectors E1

mcp_gmail:     Gmail OAuth watch + IMAP poll + normalizacion
mcp_whatsapp:  WhatsApp BSP webhook + template messages
mcp_webhook:   webhook generico con HMAC validation
mcp_scheduler: Celery Beat + cron expressions

Reglas de todos los connectors:
  Max 5 nodos por connector
  Sin LLM en el connector
  Sin logica de negocio (detect + extract + dispatch unicamente)
  Toda clasificacion vive en Action Engine

Conectores E2+: mcp_sp_api, mcp_sap, mcp_tiktok, mcp_telegram_external

---
Changelog:
- v1.0 (2026-06-24): Creacion. 13 tipos en 3 categorias.
  Flujo por categoria. Matriz evento->kanban. Data class por canal.
  MCP connectors E1. Cubre gap G3. Alineado con D1 (omnicanal) D3 (kanban).
