---
id: SPEC_FABERLOOM_AGENT_COMPOSITION_v1
version: 1.1
status: DRAFT
visibility: [INTERNAL]
domain: FABERLOOM
date: 2026-04-21
authors: CEO + arquitecto (v1.0 2026-04-21, addendum v1.1 post Kimi Swarm 3 2026-04-21)
supersedes: —
inputs:
  - SPEC_FABERLOOM_SKILL_COMPOSITION_v1.md (v1.0 DRAFT)
  - SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md (v1.0 DRAFT)
  - SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md (v1.0 DRAFT — implementación de §18 addendum)
  - ENT_FABERLOOM_AGENT_BUILDER_v1 v1.0 DRAFT (docs/ENT_FABERLOOM_AGENT_BUILDER_v1.md)
  - docs/archivo/kimi_swarm_3_workflows_autonomous.md (síntesis 9 dim validación v1.0)
  - project_faberloom_agents_design.md (Autonomy Ladder L0-L4, Thermometer, 13 campos gold sample)
  - project_faberloom_architecture.md (AgentSpec/Runtime/Memory)
  - project_faberloom_security.md (draft-first, policy engine externo)
  - COWORK_DELIVERY_FABERLOOM_v3.5.md (D12 Position↔User decouple, D17 Agent Library bidireccional)
aplica_a: [FaberLoom]
---

# SPEC — FaberLoom Agent Composition Model v1

**Documento arquitectónico de decisión.** Define cómo se modelan agentes en FaberLoom: entidad operativa que combina 1+ skills + identidad + canal + autoridad + memoria + estado de despliegue, con modo dual Sealed/Open paralelo al de skills.

Aplican reglas de KB: R1 no inventar · R2 no tocar FROZEN · R5 documentar todo cambio.

---

## 0. Alcance y estado

**Alcance:** modelo de datos para `Agent`, relación M:N `agent ↔ skill`, binding de canales, asignación a positions (D12), Autonomy Ladder L0-L4, Authority Mode, memoria de instancia, semántica de fork, update channel para sealed, pricing implications, cambios derivados.

**No cubre:** UI de Agent Console (tratado en mockup FROZEN), motor de ejecución (implementación Sprint 2-3), modelo de learning feedback detallado (ya canónico en `project_faberloom_agents_design.md`), observabilidad de agentes (sección obs del Blueprint).

**Estado v1.0 DRAFT.** Promoción a APPROVED requiere: (a) confirmación del seed catalog Fase 1 de agentes (pendiente — ver §13), (b) resolución de D12 Position↔User decoupling en el schema (bloqueante P0 del handoff Cowork), (c) review de la reconciliación Autonomy Ladder × Authority Mode con un design partner.

---

## 1. Principio rector

**Un agente es la instancia operativa** que combina capacidades (skills) con identidad (nombre, avatar, canal, persona) y estado de despliegue (position, autonomy level, memoria viva). **Una sola entidad `Agent`** con modo dual paralelo al de skills: Sealed (FaberLoom-made, update channel) u Open (cliente, 100% editable).

**Consecuencia:** misma filosofía arquitectónica que Skills. Un Agent Builder, un lifecycle, un modelo de permisos. Cambia la semántica según modo; no se duplica el sistema.

**Distinción Skill vs Agent — canónica:**

| Dimensión | Skill | Agent |
|---|---|---|
| Qué es | Capacidad reutilizable (prompt + KB + add-ons) | Instancia operativa desplegada |
| Identidad | No tiene — es abstracto | Tiene — nombre, avatar, persona, canal |
| Canal | No tiene | Tiene — email/WhatsApp/chat/portal |
| Position binding | No aplica | Requerido (D12) |
| Autonomy Ladder | No aplica | L0-L4 |
| Memoria de ejecución | No tiene (solo learned_overlay del skill) | Tiene — 3 capas (episodic/working/persistent) |
| Reutilización | Usado por N agentes | Es singular |
| Estado operativo | Statico (active/archived) | Dinámico (shadow/running/paused/error) |

**Un agente usa 1+ skills.** Si usa 1 → single-skill agent. Si usa 2+ → orchestrator agent.

---

## 2. Anatomía de un Agent

```
┌─────────────────────────────────────────────────────────────┐
│  AGENT                                                      │
│  origin: SEALED | OPEN                                      │
├─────────────────────────────────────────────────────────────┤
│  🎭 IDENTIDAD                                               │
│     - name, slug, avatar, persona_description               │
│     - trigger_word (para invocación manual)                 │
│     - tone (heredable a bindings de skills)                 │
├─────────────────────────────────────────────────────────────┤
│  🧩 SKILL BINDINGS (1+)                                     │
│     - Referencias a skills con runtime config               │
│     - Role dentro del agente: primary | fallback | specialty│
├─────────────────────────────────────────────────────────────┤
│  📡 CHANNEL BINDINGS                                        │
│     - primario: email | whatsapp | chat_interno | portal_vip│
│     - secundarios opcionales                                │
│     - credentials/handles por canal                         │
├─────────────────────────────────────────────────────────────┤
│  👥 POSITION ASSIGNMENTS                                    │
│     - Asignación a positions (NO users) — D12               │
│     - Puede ser 1 position, N positions, o tenant-wide      │
├─────────────────────────────────────────────────────────────┤
│  🎚️ AUTONOMY × AUTHORITY                                    │
│     - autonomy_level: L0..L4 (estado de despliegue)         │
│     - authority_mode: SEÑALA|PROPONE|EJEC_APROB|EJEC_SOLO   │
│     - combinación válida según matriz §6                    │
├─────────────────────────────────────────────────────────────┤
│  🧠 MEMORIA (gestionada por Letta self-host)                │
│     - Episodic: log auditable de cada interacción           │
│     - Working: contexto de sesión activa                    │
│     - Persistent: aprendizajes promovidos (Thermometer)     │
├─────────────────────────────────────────────────────────────┤
│  ⚙️  RUNTIME STATE                                          │
│     - status: shadow | running | paused | error             │
│     - last_active_at, total_runs, approval_rate, etc.       │
└─────────────────────────────────────────────────────────────┘
```

**Invariante crítico:** la identidad del agente es independiente del skill subyacente. Un agente "Laura — asistente comercial" que usa el skill `ProductMatch-EPI` no hereda el nombre/avatar del skill. El skill es una capacidad; el agente es una persona.

---

## 3. Dos modos únicos: SEALED vs OPEN

### 3.1 Agent SEALED

- **Autor:** exclusivamente FaberLoom
- **Spec:** inmutable (identidad + skill bindings + autonomy config recomendada), identificada por `spec_sealed_hash`
- **Updates:** FaberLoom puede publicar nuevas versiones de la spec. Consent explícito del admin del tenant para aplicar (ver §11 Update Channel)
- **Modificación:** imposible por el cliente. Si necesita cambiar el spec, debe **forkear**
- **Distribución:** parte del catálogo seed (Fase 1) o marketplace oficial FaberLoom futuro
- **Ownership del contrato:** FaberLoom responde por la calidad del spec

**Lo que el cliente SÍ puede hacer en un Agent Sealed (configuración de deployment):**

- Asignar `position_ids` específicos del tenant
- Configurar credenciales de canal (su cuenta de email, su WhatsApp Business)
- Ajustar `autonomy_level` dentro del rango permitido por la spec sealed
- Bindear `addons` adicionales del tenant si el spec lo permite
- Pausar, reanudar, archivar el agente
- Ver logs y aprobaciones

**Lo que NO puede hacer:**

- Cambiar qué skills usa el agente
- Cambiar `authority_mode` si la spec sealed lo limita
- Modificar identidad (nombre, persona, trigger_word)

### 3.2 Agent OPEN

- **Autor:** cliente del tenant
- **Spec:** 100% editable por el owner
- **Updates:** N/A — owner es autor
- **Modificación:** total libertad sobre identidad, skill bindings, channel bindings, autonomy, memoria, todo
- **Distribución:** dentro del tenant vía permisos (§10)
- **Ownership del contrato:** el cliente. FaberLoom no garantiza nada sobre la calidad

### 3.3 Reglas absolutas que aplican a ambos modos

Los 5 límites hardcoded (ver `ENT_FABERLOOM_AGENT_BUILDER_v1.md` §3) + la **regla sagrada** del Autonomy Ladder se aplican **independiente del modo**:

1. Cero envíos externos sin aprobación — draft-first absoluto (email, WhatsApp a cliente)
2. Cero transacciones financieras autónomas
3. Cero acceso fuera del KB scope configurado
4. Cero aprobaciones legales autónomas
5. Audit trail inmutable
6. **Regla sagrada:** correo externo, WhatsApp a clientes, Slack a clientes → siempre draft-first, el ladder no cambia esto

Estas reglas viven en el motor de ejecución, no en la config del agente. Ningún Open puede desactivarlas.

---

## 4. Enum canónico y schema

### 4.1 Tipos

```sql
CREATE TYPE agent_origin AS ENUM (
  'sealed',   -- FaberLoom-made, spec inmutable
  'open'      -- Client-made, spec editable
);

CREATE TYPE autonomy_level AS ENUM (
  'L0',   -- Shadow Mode: observa, clasifica, redacta interno, no sale al usuario
  'L1',   -- Propone siempre
  'L2',   -- Ejecuta interno de bajo impacto (etiquetas, resúmenes)
  'L3',   -- Auto + notificación (internos repetitivos y reversibles)
  'L4'    -- Auto + solo excepciones (flujos muy estrechos y probados)
);

CREATE TYPE authority_mode AS ENUM (
  'SENALA',
  'PROPONE',
  'EJECUTA_CON_APROBACION',
  'EJECUTA_SOLO'
);

CREATE TYPE agent_status AS ENUM (
  'shadow',     -- en L0, no ejecuta visible
  'running',    -- operando según autonomy_level
  'paused',     -- pausado manualmente
  'error',      -- error crítico, no ejecuta
  'archived'
);

CREATE TYPE skill_binding_role AS ENUM (
  'primary',    -- skill principal del agente
  'fallback',   -- cuando primary no tiene confianza suficiente
  'specialty'   -- para casos específicos (detectado por router interno)
);

CREATE TYPE channel_type AS ENUM (
  'email',
  'whatsapp',
  'chat_interno',
  'portal_vip'
);
```

### 4.2 Tabla `agents` (principal)

```sql
CREATE TABLE agents (
  id                uuid PRIMARY KEY DEFAULT gen_uuid_v7(),
  tenant_id         uuid NOT NULL REFERENCES tenants(id),
  origin            agent_origin NOT NULL,

  -- Identidad
  name              text NOT NULL,
  slug              text NOT NULL,
  avatar_url        text,
  persona_desc      text,
  trigger_word      text,                  -- único por tenant si presente
  tone              text,                  -- heredable a skill bindings

  -- Spec (solo sealed lleva hash)
  spec_content      jsonb NOT NULL,         -- snapshot declarativo para replay
  spec_sealed_hash  text,                   -- NOT NULL si sealed, NULL si open
  spec_version      int NOT NULL DEFAULT 1,

  -- Config operativa del tenant (sobre cualquier origin)
  autonomy_level    autonomy_level NOT NULL DEFAULT 'L0',
  authority_mode    authority_mode NOT NULL DEFAULT 'PROPONE',
  status            agent_status NOT NULL DEFAULT 'shadow',

  -- Lineage
  forked_from       uuid REFERENCES agents(id),
  forked_at         timestamptz,
  forked_from_spec_hash text,

  -- Ownership
  owner_user_id     uuid REFERENCES users(id),   -- NULL para sealed
  created_at        timestamptz NOT NULL DEFAULT now(),
  updated_at        timestamptz NOT NULL DEFAULT now(),

  -- Runtime counters (actualizados por motor)
  last_active_at    timestamptz,
  total_runs        bigint NOT NULL DEFAULT 0,

  UNIQUE (tenant_id, slug),
  UNIQUE (tenant_id, trigger_word),
  CHECK (
    (origin = 'sealed' AND spec_sealed_hash IS NOT NULL) OR
    (origin = 'open'   AND spec_sealed_hash IS NULL)
  ),
  -- Matriz de validez ladder × authority (ver §6)
  CHECK (
    (autonomy_level = 'L0') OR
    (autonomy_level = 'L1' AND authority_mode IN ('SENALA','PROPONE')) OR
    (autonomy_level IN ('L2','L3') AND authority_mode IN ('PROPONE','EJECUTA_CON_APROBACION','EJECUTA_SOLO')) OR
    (autonomy_level = 'L4' AND authority_mode = 'EJECUTA_SOLO')
  )
);

ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
CREATE POLICY agents_tenant_isolation ON agents
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

### 4.3 Tabla `agent_versions` (solo sealed)

Análoga a `skill_versions`. Historial global de versiones publicadas por FaberLoom para el Update Channel.

```sql
CREATE TABLE agent_versions (
  id                uuid PRIMARY KEY DEFAULT gen_uuid_v7(),
  agent_slug        text NOT NULL,
  version           int NOT NULL,
  spec_content      jsonb NOT NULL,
  spec_sealed_hash  text NOT NULL,
  published_at      timestamptz NOT NULL DEFAULT now(),
  changelog         text,
  breaking_change   boolean NOT NULL DEFAULT false,

  UNIQUE (agent_slug, version)
);
-- Global, no tenant-scoped, no RLS.
```

### 4.4 Tabla `agent_skill_bindings`

```sql
CREATE TABLE agent_skill_bindings (
  id                uuid PRIMARY KEY DEFAULT gen_uuid_v7(),
  agent_id          uuid NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  skill_id          uuid NOT NULL REFERENCES skills(id),
  role              skill_binding_role NOT NULL DEFAULT 'primary',
  runtime_config    jsonb NOT NULL DEFAULT '{}'::jsonb,   -- overrides de tono/autoridad para este binding
  priority          int NOT NULL DEFAULT 0,
  created_at        timestamptz NOT NULL DEFAULT now(),

  UNIQUE (agent_id, skill_id)
);

-- Constraint: solo 1 binding con role='primary' por agente
CREATE UNIQUE INDEX agent_skill_bindings_one_primary
  ON agent_skill_bindings (agent_id)
  WHERE role = 'primary';

-- RLS vía agent_id → agents.tenant_id
ALTER TABLE agent_skill_bindings ENABLE ROW LEVEL SECURITY;
CREATE POLICY agent_skill_bindings_tenant ON agent_skill_bindings
  USING (EXISTS (
    SELECT 1 FROM agents a
    WHERE a.id = agent_id
      AND a.tenant_id = current_setting('app.tenant_id')::uuid
  ));
```

### 4.5 Tabla `agent_channel_bindings`

```sql
CREATE TABLE agent_channel_bindings (
  id                uuid PRIMARY KEY DEFAULT gen_uuid_v7(),
  agent_id          uuid NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  channel           channel_type NOT NULL,
  is_primary        boolean NOT NULL DEFAULT false,
  handle            text,                  -- ej. "laura@firma.cr", "+50688887777"
  credentials_ref   text,                  -- referencia a secret store (no plaintext)
  config            jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at        timestamptz NOT NULL DEFAULT now(),

  UNIQUE (agent_id, channel)
);

-- Exactamente 1 primary por agente
CREATE UNIQUE INDEX agent_channel_bindings_one_primary
  ON agent_channel_bindings (agent_id)
  WHERE is_primary = true;

ALTER TABLE agent_channel_bindings ENABLE ROW LEVEL SECURITY;
CREATE POLICY agent_channel_bindings_tenant ON agent_channel_bindings
  USING (EXISTS (
    SELECT 1 FROM agents a
    WHERE a.id = agent_id
      AND a.tenant_id = current_setting('app.tenant_id')::uuid
  ));
```

### 4.6 Tabla `agent_position_assignments` (D12 — position-scoped, NO user-scoped)

```sql
CREATE TABLE agent_position_assignments (
  id                uuid PRIMARY KEY DEFAULT gen_uuid_v7(),
  agent_id          uuid NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  position_id       uuid REFERENCES positions(id),          -- NULL = tenant-wide
  scope             text NOT NULL DEFAULT 'position',        -- position | tenant_wide
  assigned_at       timestamptz NOT NULL DEFAULT now(),
  assigned_by       uuid REFERENCES users(id),

  UNIQUE (agent_id, position_id),
  CHECK (
    (scope = 'position' AND position_id IS NOT NULL) OR
    (scope = 'tenant_wide' AND position_id IS NULL)
  )
);

-- RLS vía agent_id → agents.tenant_id
ALTER TABLE agent_position_assignments ENABLE ROW LEVEL SECURITY;
CREATE POLICY agent_position_assignments_tenant ON agent_position_assignments
  USING (EXISTS (
    SELECT 1 FROM agents a
    WHERE a.id = agent_id
      AND a.tenant_id = current_setting('app.tenant_id')::uuid
  ));
```

**Clave D12:** `position_id` apunta a `positions`, NO a `users`. Cuando una position queda vacante por turnover, el agente sigue operando — solo cambia el destinatario humano de sus aprobaciones/escalamientos. Esta decisión es **bloqueante P0** antes de materializar agentes reales.

---

## 5. Componentes del runtime (no nuevas tablas)

### 5.1 Runtime counters

Viven como columnas en `agents` para perf de lectura en dashboards:

- `last_active_at`
- `total_runs`

Otros KPIs computados (approval_rate, edit_light_rate, tiempo_ahorrado, repeat_use) viven en una tabla `agent_metrics_daily` derivada del stream de eventos — tratada en sección de observabilidad del Blueprint, no aquí.

### 5.2 Memoria

Gestionada por Letta self-host (decisión del memory stack canónica). El agente referencia un `memory_context_id` por namespace:

- `mem:agent:{agent_id}:episodic`
- `mem:agent:{agent_id}:working`
- `mem:agent:{agent_id}:persistent`

No necesita tabla Postgres para la memoria misma — está en Letta. La tabla `agents` guarda solo el identificador de namespace. La promoción Working→Persistent ocurre vía el **Learning Thermometer** (🔵🟡🔴) ya canónico; no se escribe a Persistent sin consent.

---

## 6. Matriz Autonomy Ladder × Authority Mode

Dos dimensiones ortogonales:

- **Autonomy Level (L0-L4)** = estado de despliegue del agente (lifecycle)
- **Authority Mode** = tipo de acción máxima permitida (qué puede hacer)

Combinaciones válidas (hardcoded en el CHECK constraint de `agents`):

| Ladder | Authority permitido | Resultado operativo |
|---|---|---|
| **L0 Shadow** | (cualquiera, pero no aplica) | Observa, redacta interno, **no envía output al usuario**. Estado de onboarding obligatorio. |
| **L1 Propone** | SEÑALA, PROPONE | Alerta/genera draft, nunca ejecuta |
| **L2 Ejec. interno** | PROPONE, EJECUTA_CON_APROBACION, EJECUTA_SOLO | Solo internos de bajo impacto (etiquetas, resúmenes). Externos siguen draft-first |
| **L3 Auto + notif** | PROPONE, EJECUTA_CON_APROBACION, EJECUTA_SOLO | Internos reversibles automáticos + notifica. Externos draft-first |
| **L4 Auto + excep** | EJECUTA_SOLO | Flujos estrechos y probados. Solo escala en excepciones. Doble consent para promover. Externos draft-first |

**Regla sagrada universal:** externos (email a clientes, WhatsApp externo, Slack externo) siempre draft-first. Ni L4 cambia esto. Está hardcoded en el motor.

**Promoción de nivel:**

- L0 → L1: requiere shadow mínimo de 20 runs aprobados con ≥70% approval rate
- L1 → L2: admin del tenant, mínimo 50 runs en L1 con ≥80% approval
- L2 → L3: admin, 100 runs en L2 con ≥85% approval + zero incidentes 30 días
- L3 → L4: **doble consent** (admin + owner de org) + review manual del spec + límite estricto de scope

Estas reglas viven en el motor. No se configuran por skill/agente.

---

## 7. Semántica de Fork

### 7.1 Fork de SEALED → resultado OPEN

Único path para modificar el spec de un agente sealed. Consecuencias:

- Se copia `spec_content` actual como spec del nuevo Open
- Se copian `agent_skill_bindings` por defecto (opt-out disponible)
- Se copian `agent_channel_bindings` (opt-out disponible — generalmente se querrá re-configurar credenciales)
- Se copian `agent_position_assignments` por defecto (opt-out)
- `autonomy_level` se resetea a **L0 Shadow** en el fork — el shadow period se reinicia por seguridad
- Memoria: los namespaces Episodic/Working/Persistent son nuevos (no se hereda memoria de instancia)
- Se pierde el update channel del sealed original
- `forked_from` y `forked_from_spec_hash` se llenan

### 7.2 Fork de OPEN → clone (también Open)

Mismo contenido, nuevo `id`, `owner_user_id` puede cambiar. `autonomy_level` se resetea a L0.

### 7.3 UI hint

Agent Builder debe ser explícito: "forkear rompe vínculo con FaberLoom, reinicia shadow period, y aísla memoria. Es una copia nueva." El agente original sigue intacto.

---

## 8. Update Channel (solo SEALED)

Análogo al de Skills pero con consideraciones específicas:

1. FaberLoom publica `agent_versions` con nueva versión del slug
2. Job detecta para cada tenant con ese agente activo
3. Notificación al admin: "Update TrackBot v1.0 → v1.1. Cambios: [diff]. ¿Aceptar?"
4. Opciones:
   - **Aceptar:** `spec_content` + `spec_sealed_hash` se actualizan. Config de deployment (position, canal, credentials, autonomy_level) se preserva. Memoria se preserva
   - **Rechazar:** queda en versión actual
   - **Forkear:** conversión a Open tomando la versión actual
5. **Si el update cambia qué skills usa el agente**: se marca como breaking change. Requiere doble consent. Por seguridad, el autonomy_level se resetea a L0 Shadow tras la actualización — hay que volver a probar

### 8.1 Conflict handling

Si el update modifica el rango permitido de `authority_mode` y el tenant tiene configurado uno ya no permitido:

- Update no se aplica automáticamente
- Se marca `needs_attention`
- Admin reconcilia manualmente

---

## 9. Tipología emergente de agentes

No es etiqueta rígida del schema — propiedad derivable del shape del agente:

| Shape | Nombre | Ejemplo |
|---|---|---|
| 1 skill bindeado, rol `primary` | **Single-skill agent** | TrackBot |
| 2+ skills bindeados, rol primary + fallback/specialty | **Orchestrator agent** | Laura (ProductMatch + QualifyBot + ProposalBot) |
| 1+ skills + subscripción a eventos de otros agentes | **Hub agent** | EmailIntelBot (escucha bandeja, dispara CompraBot, CollectionBot, etc.) |
| Orchestrator + todos los add-ons y memoria persistente robusta | **Expert agent** | ComplianceAnalyst en firma legal |

La distinción Hub vs Orchestrator es operativa:
- Orchestrator: recibe input directo, decide qué skill usar internamente
- Hub: escucha stream de eventos (inbox, webhook, schedule), enruta a otros agentes

Ambos se modelan igual en el schema. La diferencia está en los triggers configurados.

---

## 10. Sharing y permisos (scope Fase 1)

Permisos sobre un agente:

| Nivel | Ver | Invocar | Editar spec | Editar config deploy | Cambiar autonomy | Ver logs |
|---|---|---|---|---|---|---|
| Owner | ✅ | ✅ | ✅ (si open) | ✅ | ✅ | ✅ |
| Admin (del tenant) | ✅ | ✅ | ❌ (si sealed) | ✅ | ✅ | ✅ |
| Assignee (de la position) | ✅ | ✅ | ❌ | parcial | ❌ | ✅ parcial |
| Auditor | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ full |

Tabla `agent_permissions` entra en S2. En Fase 1 simple: asignación a position implica nivel Assignee automáticamente.

---

## 11. Pricing implications

Extensión del pricing ya propuesto en `SPEC_FABERLOOM_SKILL_COMPOSITION_v1` §10:

| Plan | Agentes activos | Modos | Shapes permitidos | Autonomy máximo |
|---|---|---|---|---|
| Starter $99 | 3 | Sealed only | Single-skill only | L2 |
| Professional $199 | 10 | Sealed + Open | Single + Orchestrator hasta 3 skills | L3 |
| Enterprise $299 | Ilimitado | Sealed + Open + Fork | Todos incluyendo Hub | L4 |

**Principio:** el plan gobierna capacidades de despliegue, no solo cuota. El costo operativo (tokens + add-ons del skill subyacente) se cobra aparte según `SPEC_SKILL_COMPOSITION` §10.

**Ronda 3** del Blueprint debe ratificar unit-economics.

---

## 12. Relación con el catálogo de 168 agentes (Kimi)

El catálogo de `ENT_FABERLOOM_AGENT_BUILDER_v1.md` describe **168 agentes posibles** a nivel conceptual. Este SPEC define **cómo se modelan técnicamente**. Mapeo:

- Cada agente del catálogo Kimi es un candidato a Agent Sealed si FaberLoom decide empaquetarlo
- O es un patrón de referencia que el cliente reproduce como Agent Open combinando skills propios

El catálogo se mantiene como referencia (no como promesa de implementación). El seed Fase 1 empaquetará **3 de los 168** como sealed (ver §13).

**Los 6 agentes LATAM-específicos** del catálogo (ExpedienteBot, TiposDeCambioBot, ProductMatch-EPI, LicitaciónBot, DistribuidorBot, HonorariosBot) son candidatos preferentes a sealed por ser diferenciadores competitivos. ProductMatch-EPI específicamente encaja con el wedge Marluvas/Tecmater.

---

## 13. Seed catalog Fase 1 — qué queda pendiente

Con este modelo, el seed Fase 1 es:

- 3 agentes `sealed` pre-configurados (hechos por FaberLoom)
- Cada uno empaquetado con skill bindings default, channel default, autonomy_level=L0 obligatorio al instalar
- Los clientes pueden crear agentes `open` desde día 1 en Agent Builder

**Pendiente de confirmar** (bloqueo previo a promover SPEC a APPROVED):

- ¿Qué 3 agentes sealed al seed? Opciones (en paralelo con las de skills):
  - **A** genérico Kimi: TrackBot · InfoBot · DailyBriefBot
  - **B** wedge: ProductMatch-EPI · QualifyBot · ProposalBot
  - **C** híbrido (recomendación arquitecto): ProductMatch-EPI · InfoBot · DailyBriefBot

Decide el CEO. El SPEC no bloquea — el modelo soporta cualquiera.

**Correspondencia con seed de Skills:** para minimizar complejidad, los 3 agentes sealed deberían usar **exactamente los 3 skills sealed del seed** — un agente por skill, single-skill agent shape, L0 por default. Esto simplifica onboarding y demo.

---

## 14. Lo que queda abierto (no bloquea Fase 1)

1. **Orquestación declarativa multi-agente.** Cuando un agente dispara a otro (ej. EmailIntelBot → CompraBot). Patrón Hub. En Fase 1 se modela como trigger config; en Fase 2 puede requerir grafo formal de dependencias con schema propio.

2. **Cross-tenant agent marketplace.** Compartir agentes Open entre tenants. Fase 2+. Requiere modelo de licencia y responsabilidad.

3. **Auto-promotion de autonomy level.** Que el sistema sugiera automáticamente promover L1→L2→L3 cuando se cumplen las métricas. En Fase 1 es manual. Fase 2+.

4. **Multi-channel agent.** Un agente que actúa en email + WhatsApp + chat simultáneamente con coherencia. En Fase 1 soportamos múltiples channel bindings pero el motor ejecuta por canal separado; una memoria unificada cross-channel es Fase 2.

5. **Agent-to-agent handoff.** Transferir un caso de un agente a otro (ej. QualifyBot califica y pasa a ProposalBot). Fase 2.

---

## 15. Cambios disparados en otros documentos

1. **`SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md`** — Sprint 1 de S1 sube de **13 a 18 tablas** con: `agents`, `agent_versions`, `agent_skill_bindings`, `agent_channel_bindings`, `agent_position_assignments`. Actualizar §2 Schema y §4 Sprint 1. Nota: S1=9 base + 4 skills (SPEC_SKILL_COMPOSITION) + 5 agents (este SPEC) = 18.

2. **`ENT_FABERLOOM_AGENT_BUILDER_v1.md` (en archivo)** — promover a `docs/` activo. Agregar nota de cabecera referenciando este SPEC como autoridad canónica del modelo técnico. El catálogo de 168 agentes se mantiene como referencia del universo de agentes posibles; este SPEC define la mecánica.

3. **Mockup FaberLoom v3.5 (FROZEN)** — cuando salga del freeze, verificar que Agent Console muestre modo (sealed/open), permita configurar autonomy_level con wizard L0→L1→L2→L3→L4, y exponga el Learning Thermometer por agente.

4. **`COWORK_DELIVERY_FABERLOOM_v3.5.md`** — agregar a §3 decisiones:
   - **D19:** Modelo composable de Agents (este SPEC) — modo dual Sealed/Open paralelo a Skills
   - **D20:** Matriz válida Ladder × Authority (hardcoded via CHECK constraint)

5. **`project_faberloom_architecture.md`** (memoria) — actualizar la descripción de AgentSpec para citar este SPEC como fuente técnica canónica. El modelo AgentSpec/Runtime/Memory original sigue vigente conceptualmente; el schema concreto vive aquí.

6. **D12 del handoff** — este SPEC materializa la decisión de position decoupling en la tabla `agent_position_assignments`. Con esto D12 deja de ser bloqueante conceptual y pasa a ser tarea de implementación del Sprint 1.

---

## 16. Registro de cambios

| Fecha | Versión | Cambio |
|---|---|---|
| 2026-04-21 | 1.0 DRAFT | Primera emisión. Modo dual Sealed/Open · matriz Ladder×Authority · 5 tablas nuevas S1 · position binding D12 resuelto · fork resetea a L0. Autoridad: CEO + arquitecto. |
| 2026-04-21 | 1.1 DRAFT | Addendum §18 post Kimi Swarm 3: referencias cruzadas al nuevo SPEC_WORKFLOW_ENGINE_v1 para Workflow Engine, Agent↔Workflow Protocol, Learning Loop. Sin cambios al modelo de datos ni al diseño canónico. Validación externa HIGH confidence del modelo v1.0. |

---

## 17. Referencias y linaje

- `docs/SPEC_FABERLOOM_SKILL_COMPOSITION_v1.md` — modelo gemelo para skills (pattern idéntico)
- `docs/SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` — schema base, RLS, UUIDv7, Letta self-host
- `docs/archivo/ENT_FABERLOOM_AGENT_BUILDER_v1.md` — catálogo 168 agentes Kimi (referencia)
- `.auto-memory/project_faberloom_agents_design.md` — Autonomy Ladder L0-L4, 13 campos gold sample, Learning Thermometer, 6 KPIs tab Usuarios
- `.auto-memory/project_faberloom_architecture.md` — AgentSpec/Runtime/Memory conceptual original
- `.auto-memory/project_faberloom_cowork_handoff.md` — D12 Position↔User decouple, D17 Agent Library bidireccional
- `.auto-memory/project_faberloom_security.md` — draft-first, policy engine externo
- `docs/SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md` — motor de ejecución, DSL YAML, protocolo handoff, anti-loop, learning loop, obs
- `docs/archivo/kimi_swarm_3_workflows_autonomous.md` — síntesis Kimi Swarm 3 (validación externa v1.0)

---

## 18. Addendum v1.1 — Gaps resueltos por SPEC_WORKFLOW_ENGINE_v1

**Contexto.** Kimi Swarm 3 (9 dimensiones · 200+ búsquedas · 7,643 líneas de evidencia) validó con HIGH confidence que el diseño arquitectónico de v1.0 es sólido. Los gaps detectados no son errores de diseño sino decisiones de implementación pendientes. La recomendación confirmada es: **no reescribir v1.0, crear un SPEC técnico gemelo** (`SPEC_FABERLOOM_WORKFLOW_ENGINE_v1`) que traduce cada decisión conceptual a implementación concreta.

### 18.1 Gap #1 — Workflow Execution Engine

**Qué no definía v1.0.** Describe 168 agentes, áreas funcionales, 4 modos de autoridad, pero no QUÉ ejecuta los workflows ni CÓMO se serializan.

**Resolución (ver WORKFLOW_ENGINE §2-§4):**
- Motor Fase 1: **pg-boss** (npm sobre Postgres existente, SKIP LOCKED exactly-once, MIT).
- Motor Fase 2: **Inngest self-hosted** (durable execution, `step.sleep`, `step.waitForEvent`).
- DSL Fase 1: **YAML declarativo** (subset CNCF Serverless Workflow DSL), source-of-truth en `workflow_templates`.
- DSL Fase 2: **React Flow** + YAML bidireccional (post-beta).
- Pipeline: YAML → JSON Schema validator → AST intermedio → pg-boss job graph → Postgres.

### 18.2 Gap #2 — Agent↔Workflow Integration Protocol

**Qué no definía v1.0.** Describe modos de autoridad como abstracción de producto pero no cómo se implementan técnicamente ni el contrato JSON de comunicación.

**Resolución (ver WORKFLOW_ENGINE §5):**
- **4 patrones de integración:** agent-as-step (dominante), chat-launches-workflow, event-driven notifier, human-in-the-loop gate.
- **Protocolo JSON v1.0** de handoff con campos obligatorios: `session.*`, `agent.*`, `constraints.*` (depth_remaining, max_tool_calls, max_turns, max_budget_usd, timeout_sec), `input`, `memory_scope`.
- **Mapeo Authority Mode → mecanismos Claude SDK:**
  * SEÑALA = `allowed_tools: ["read_*"]` solamente
  * PROPONE = `allowed_tools: ["read_*", "draft_*"]`
  * EJECUTA_CON_APROBACIÓN = `allowed_tools: [*]` + `waitForApproval()` obligatorio
  * EJECUTA_SOLO = `allowed_tools: [*]` sin gate, **prohibido en canales externos (regla sagrada)**
- **Tabla `agent_authority_config`** (agent_id × tool × mode). Cambiar modo = UPDATE, no deploy.
- **Mecanismos anti-loop obligatorios día 1:** max_depth=2, circuit_breaker 3 fallos → fallback, idempotency keys TTL 7d, timeout budget 5min, max_turns=20, max_budget_usd=$1, token burn 10k, daily caps ($20 pago / $5 gratis), kill switch z-score>4.

### 18.3 Gap #3 — Learning Loop

**Qué no definía v1.0.** Describe gold samples como concepto pero no el pipeline de feedback, la técnica de aprendizaje, ni la UI de captura.

**Resolución (ver WORKFLOW_ENGINE §7):**
- **Fase 1:** **PatchRAG** (correcciones sanitizadas como patches embebidos en pgvector, retrieval híbrido en cada query) + **few-shot dinámico** con gold samples. Inference-time learning, sin retraining, sin GPU. Lag <5s post-promoción. 62.3% accuracy promedio (paper arXiv 2026).
- **Fase 2:** **LoRA selectivo** por tenant (≥50 gold samples), **DP-LoRA federado** cross-tenant (≥10 tenants, epsilon 3-6).
- **UI feedback:** thumbs up/down <2s con micro-dropdown de razón, diff capture automático, banner "Guardar como gold sample" 1-click visible <1s post-edición.
- **Pipeline:** Candidate → Active → Archived/Reverted (ya canónico en `project_faberloom_agents_design.md`, no cambia).

### 18.4 Cambios al schema inducidos por WORKFLOW_ENGINE

El SPEC_WORKFLOW_ENGINE_v1 introduce **6 tablas adicionales** al Sprint 1 que no están en las 18 de v1.0 de este SPEC:

| Tabla | Propósito |
|---|---|
| `workflow_templates` | YAML + AST, versionado, tenant_scope |
| `workflow_runs` | Instancias de ejecución |
| `workflow_step_runs` | Estado por step, input/output/error |
| `workflow_approvals` | HITL gates con SLA |
| `agent_authority_config` | Override de modo de autoridad por agent×tool |
| `workflow_circuit_state` | Estado de circuit breaker |

**Conteo S1 actualizado:** 18 (v1.0) + 6 (engine) = **24 tablas en Sprint 1**.

Este recount debe reflejarse en `SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT` cuando se actualice a v1.1.

### 18.5 Qué NO cambia de v1.0

- Modelo de datos de `agents`, `agent_versions`, `agent_skill_bindings`, `agent_channel_bindings`, `agent_position_assignments` — intacto.
- Enum `agent_origin` (sealed/open) — intacto.
- Matriz Ladder × Authority hardcoded en CHECK constraint — intacta.
- Regla sagrada (externos siempre draft-first, ni L4 lo cambia) — intacta, ahora explicitada como mapeo técnico en §18.2.
- Memoria Letta por agente con namespaces `mem:agent:{id}:episodic|working|persistent` — intacta.
- Fork sealed→open con reset a L0 Shadow + memoria no heredada — intacto.
- Promoción autonomy (L0→L1 ≥20 runs 70%, L1→L2 admin+50 runs 80%, etc.) — intacta.
- Tipología emergente (Single-skill · Orchestrator · Hub · Expert) — intacta.
- Pricing extendido ($99 / $199 / $299) — intacto.

### 18.6 Validación externa (Kimi Swarm 3)

| Aspecto v1.0 | Confianza Kimi | Evidencia |
|---|---|---|
| Modo dual Sealed/Open paralelo a Skills | HIGH | Patrón adoptado por plataformas con marketplace + custom |
| Matriz Ladder × Authority ortogonales | HIGH | Mapea 1:1 a Claude SDK `allowed_tools` + `can_use_tool` |
| D12 Position decoupling | HIGH | Necesario para escalar multi-tenant con RBAC flexible |
| Memoria Letta per-agent | HIGH | Letta ya en stack, self-host, namespaces compatibles |
| Draft-first para externos | HIGH | Patrón industria (Microsoft Copilot, Intercom Fin) |
| Tipología emergente no rígida | HIGH | Alineado con CNCF Serverless Workflow + agentic patterns |

**Veredicto:** 0 cambios al diseño, 6 tablas nuevas a S1 por el motor, nuevo SPEC técnico gemelo como referencia de implementación.


*SPEC_FABERLOOM_AGENT_COMPOSITION_v1.0 DRAFT — Muito Work Limitada · 2026-04-21*
