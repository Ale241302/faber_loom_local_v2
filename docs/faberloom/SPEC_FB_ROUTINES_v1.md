# SPEC_FB_ROUTINES_v1 -- Agentes de Proceso: Rutinas y Automatizaciones
id: SPEC_FB_ROUTINES_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: ENT_FB_DECISIONES_E1_v1.md

---

## Declaracion

Las rutinas son agentes de categoria Proceso disparados por eventos
o cron, no por invocacion humana directa.
Ejemplos: @seguidor @kb_audit @stock_refresh @margin_drift

Creacion en E1:
1. Workspace conversacional (modo Automatizacion-futuro)
2. Agent Factory (web, Owner/Admin)

Regla sagrada: ninguna rutina envia comunicacion externa sin
aprobacion humana. Aplica a TODOS los niveles de autonomy_ceiling.

---

## 1. Tablas DB

### automations
tenant_id uuid NOT NULL (RLS)
agent_id uuid NOT NULL REFERENCES agents(id)
name text NOT NULL
trigger_kind text CHECK IN (cron,webhook,event,signal,channel_keyword)
trigger_config jsonb NOT NULL
pre_condition jsonb
skill_id text
autonomy_ceiling text DEFAULT PROPONE
  CHECK IN (PROPONE,EJECUTA_INTERNO,AUTO_NOTIFICA,AUTO_EXCEPCIONES)
status text DEFAULT sandbox
  CHECK IN (sandbox,active,paused,failed,deprecated)
requires_approval boolean DEFAULT true
consecutive_failures int DEFAULT 0
signal_to_noise_ratio float
alert_channel text DEFAULT telegram
UNIQUE (tenant_id, name)
RLS: tenant_id = current_setting(app.tenant_id)

trigger_config ejemplos:
  cron:    { schedule: 0 6 * * *, timezone: America/Costa_Rica }
  webhook: { endpoint: /api/webhooks/sp-api, source: sp-api }
  event:   { event_type: feed.item.received, filter: {} }
  keyword: { channel: whatsapp, keywords: [urgente, RFQ] }

### automation_runs
automation_id uuid REFERENCES automations(id)
tenant_id uuid NOT NULL (RLS)
task_id uuid REFERENCES tasks(task_id)
triggered_at timestamptz DEFAULT now()
status text CHECK IN (running,completed,failed,skipped,timeout)
output_accionable boolean
duration_ms int
cost_usd float
audit_id uuid
UNIQUE (automation_id, triggered_at)

---

## 2. Lifecycle

sandbox --> active:    Owner/Admin aprueba
active --> paused:     switch OFF en Workspace Tab Agentes
active --> failed:     consecutive_failures >= 3
failed --> active:     Owner reactiva manualmente
any --> deprecated:    Owner retira

Regla si ceiling AUTO_NOTIFICA o AUTO_EXCEPCIONES:
  minimo 3 runs exitosos en SANDBOX revisados por humano antes de promover

---

## 3. Creacion conversacional

Palabras clave que detectan modo AUTOMATIZACION-FUTURO:
  cuando llegue, cuando reciba, si llega, cada dia, todos los lunes,
  automaticamente, sin que yo tenga que, avisame si

Flujo:
1. Usuario escribe frase en Workspace composer
2. Sistema detecta modo AUTOMATIZACION-FUTURO
3. LLM genera propuesta: trigger_kind, trigger_config, skill,
   autonomy_ceiling PROPONE por default
4. Card de propuesta: [Nombre] [Trigger] [Skill] [Autonomia] [Crear Sandbox]
5. Usuario confirma o ajusta
6. status=sandbox --> WorkLoom kanban Listo para revisar
7. Owner/Admin aprueba --> status=active
   Trigger registrado en Celery Beat o webhook registry

Ejemplo A: Cuando llegue correo urgente de cliente nuevo avisame
  trigger_kind: channel_keyword
  trigger_config: channel=gmail, keywords=[urgente], sender=not_in_kb
  skill: SKILL_CLIENT_SERVICE, ceiling: PROPONE, alert: telegram

Ejemplo B: Cada lunes 8am revisar RFQs sin responder mas de 48h
  trigger_kind: cron
  trigger_config: schedule=0 8 * * 1, timezone=America/Costa_Rica
  skill: @kb_audit, ceiling: AUTO_NOTIFICA

---

## 4. Ejecucion

Trigger dispara --> Celery worker-agent recibe job
with_tenant_session(tenant_id):
  1. Cargar automation + pre_condition
  2. Evaluar pre_condition (deterministica, sin LLM)
     falla --> status=skipped, log, no molesta
  3. Crear task (invocation_mode=scheduled o webhook)
  4. Ejecutar skill/flow via Action Engine
  5. Evaluar output:
     accionable --> WorkLoom segun autonomy_ceiling
     ruido --> log + update signal_to_noise_ratio
  6. Update automation_runs + consecutive_failures
  7. consecutive_failures >= 3 --> status=failed + alerta
  8. Audit trail D10

Destino por ceiling:
  PROPONE:          WorkLoom Listo para revisar (siempre)
  EJECUTA_INTERNO:  WorkLoom solo si excepcion
  AUTO_NOTIFICA:    ejecuta + notifica alert_channel
  AUTO_EXCEPCIONES: silencioso, WorkLoom solo si error

---

## 5. Idempotencia

UNIQUE (automation_id, triggered_at) en automation_runs.
Para webhooks: dedup ventana deduplication_window_h horas (default 24h).

---

## 6. Panel Workspace Tab Agentes

Sub-seccion Proceso en Tab Agentes del panel derecho Workspace:

@seguidor_rfq  active  cron 06:00  2h  OK  [ON]  [config]
@kb_audit      active  cron 06:00  2h  OK  [ON]  [config]
@stock_refresh active  webhook    15m  OK  [ON]  [config]
@margin_drift  paused  cron 08:00  --  --  [OFF] [config]
@nueva_rutina  sandbox --          --  --  [Revisar]

[+ Nueva automatizacion] --> Workspace modo Automatizacion

---

## 7. Metricas

signal_to_noise_ratio = runs con output_accionable / total_runs
  >= 0.7: saludable
  0.3-0.7: revisar trigger
  < 0.3: candidata a ajuste o deprecacion

---
Changelog:
- v1.0 (2026-06-24): Creacion. Cubre gap G1.
  Alineado con ENT_FB_DECISIONES_E1_v1 D3/D4.
