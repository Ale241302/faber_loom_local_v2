# SCH_FB_CORE_TABLES - Schemas fisicos core Sprint 1 (los 4 vacios del AUDIT modular)

id: SCH_FB_CORE_TABLES
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (IDX_FB_FOUNDATION_BETA)
type: SCH
stamp: VIGENTE -- 2026-06-12 -- resuelve vacios 2, 3, 5, 6 de AUDIT_FB_MODULAR_2026-06-11
aprobador: CEO (Alvaro) -- mandato "arregla ya" sesion 2026-06-12
aplica_a: [FaberLoom]
relacionado: AUDIT_FB_MODULAR_2026-06-11 - PLB_FB_FOUNDATION_BETA v1.3.2 (E-3 allowlist) - SPEC_FB_ROUTING_PRESETS v1 - SPEC_FB_BUILD_SEQUENCE v2.1

---

## Proposito

DDL canonico de las tablas que TODOS los modulos usan y que no tenian schema:
savings ledger (M3), gold samples (M8), conversaciones (M9), membresia de workspace
(M9/V9.1), jobs del scheduler (V9.2) y client_map para entity resolution (V2.1).
Sprint 1 las crea tal cual; cambios via migration + changelog aqui.

## Regla transversal: el lente en datos, no en UI

1. Toda tabla operativa lleva `tenant_id NOT NULL` (RLS, ya canon) **y**
   `workspace_id` (NULL solo para items globales del tenant, ej. conversaciones
   de SpaceLoom sin scope).
2. El scope del lente se aplica SIEMPRE en query server-side
   (RLS policy o WHERE) -- nunca solo como filtro de frontend.
3. Eventos de audit registran `workspace_id` ademas de `tenant_id`.

## DDL

```sql
-- M9/V9.1 - membresia: quien ve que workspace (administrados vs heredados)
CREATE TABLE workspace_members (
  tenant_id     uuid NOT NULL,
  workspace_id  uuid NOT NULL,
  user_id       uuid NOT NULL,
  role          text NOT NULL CHECK (role IN ('owner','operator')),  -- E-4: 2 roles E1
  relation      text NOT NULL CHECK (relation IN ('administrado','heredado')),
  created_at    timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (tenant_id, workspace_id, user_id)
);

-- M3/V3.1 - savings ledger: todos los modulos escriben aqui
CREATE TABLE savings_ledger (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  tenant_id     uuid NOT NULL,
  workspace_id  uuid,
  task_id       uuid NOT NULL,
  task_class    text NOT NULL,            -- cotizacion | cobranza | chat_kb | ...
  model         text NOT NULL,
  mode          text NOT NULL,            -- eco | balanceado | sport | sport_plus | boost
  tokens_in     int  NOT NULL,
  tokens_out    int  NOT NULL,
  cost_usd      numeric(10,6) NOT NULL,
  baseline_usd  numeric(10,6) NOT NULL,   -- V3.2: contrafactual ESTIMADO por tokens
                                          -- equivalentes a precio del modelo top. Declarado, no medido.
  outcome       text,                     -- approved_clean | edited | iterated | discarded | NULL pendiente
  edit_distance numeric(5,4),             -- 0..1, NULL si no aplica
  created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ON savings_ledger (tenant_id, task_class, model, created_at);

-- M8/V8.1 - gold samples: par contexto/accion aprobada (few-shot voz + golden corpus + replay)
CREATE TABLE gold_samples (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  tenant_id     uuid NOT NULL,
  workspace_id  uuid,
  task_class    text NOT NULL,
  context_in    jsonb NOT NULL,           -- input + KB refs usadas
  action_out    text  NOT NULL,           -- draft final APROBADO (post-edits)
  was_edited    boolean NOT NULL,
  edit_reason   text,                     -- dropdown del porque (tono, terminologia, ...)
  outcome_score numeric(3,2),             -- inicial 1.0 aprobado limpio; decae si replay falla
  source_task   uuid NOT NULL,
  created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ON gold_samples (tenant_id, task_class, was_edited, created_at);

-- M9/V9.3 - conversaciones: la entidad mas usada de la UI
CREATE TABLE conversations (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL,
  workspace_id  uuid,                     -- NULL = SpaceLoom global
  title         text NOT NULL,
  pinned        boolean NOT NULL DEFAULT false,
  status        text NOT NULL DEFAULT 'active' CHECK (status IN ('active','archived')),
  created_by    uuid NOT NULL,
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now()   -- lock optimista V7.2
);
CREATE TABLE conversation_messages (
  id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  conversation_id uuid NOT NULL REFERENCES conversations(id),
  tenant_id       uuid NOT NULL,
  role            text NOT NULL CHECK (role IN ('user','agent','system')),
  content         text NOT NULL,
  trace_id        text,                   -- enlaza a routing_decision + draft si los hay
  created_at      timestamptz NOT NULL DEFAULT now()
);

-- V9.2 - scheduler unico (digest 17:00, vigencias, batch promocion)
CREATE TABLE scheduled_jobs (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL,
  job_type      text NOT NULL,            -- digest | validity_check | promotion_batch
  cron_expr     text NOT NULL,
  payload       jsonb NOT NULL DEFAULT '{}',
  enabled       boolean NOT NULL DEFAULT true,
  last_run_at   timestamptz,
  last_status   text,
  created_at    timestamptz NOT NULL DEFAULT now()
);

-- M2/V2.1 - entity resolution: contacto -> workspace, alimentado por el triage
CREATE TABLE client_map (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  tenant_id     uuid NOT NULL,
  match_type    text NOT NULL CHECK (match_type IN ('domain','email','phone')),
  match_value   text NOT NULL,            -- 'sondel.cr' | 'persona@gmail.com'
  workspace_id  uuid NOT NULL,
  confidence    numeric(3,2) NOT NULL DEFAULT 1.00,
  source        text NOT NULL CHECK (source IN ('seed','triage_humano','agente_sugerido')),
  created_by    uuid,
  created_at    timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, match_type, match_value)
);
```

## Reglas de entity resolution (V2.1, version 1 pagina)

1. **Precedencia:** email exacto > dominio > telefono. Primer match gana.
2. **Dominio gana por default:** correo nuevo de dominio conocido -> workspace del
   dominio, confidence 0.9, categoria "ruteado automatico".
3. **Sin match -> triage humano.** La decision del triage ESCRIBE en client_map
   (source=triage_humano, confidence 1.0). Cada decision es un training example;
   el mismo remitente nunca se pregunta dos veces.
4. **Conflicto (mismo contacto, dos clientes):** el match email exacto resuelve;
   si no existe, triage humano obligatorio aunque el dominio matchee.
5. **Dominios genericos (gmail/hotmail/yahoo):** NUNCA matchean por dominio;
   solo email exacto o triage.
6. Seed inicial: clientes actuales de ENT_COMERCIAL_CLIENTES (dominios + contactos
   conocidos), cargado en S2 junto a la curaduria de RFQs.

## RLS pattern (referencia)

```sql
ALTER TABLE <t> ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON <t>
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
-- lente workspace: WHERE workspace_id = $scope OR (workspace_id IS NULL AND $scope_global)
-- aplicado server-side en el repositorio de queries, nunca en el cliente
```

---

Changelog:
- v1.0 (2026-06-12): Creacion. 7 tablas (members, ledger, gold_samples, conversations,
  messages, jobs, client_map) + regla transversal del lente + 6 reglas entity resolution
  + definicion operativa del baseline (estimado, V3.2). Origen: AUDIT_FB_MODULAR vacios
  2/3/5/6 + mandato CEO 2026-06-12. ASCII puro.
