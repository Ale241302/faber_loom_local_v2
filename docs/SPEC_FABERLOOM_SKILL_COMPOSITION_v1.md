---
id: SPEC_FABERLOOM_SKILL_COMPOSITION_v1
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FABERLOOM
date: 2026-04-21
authors: CEO + arquitecto (iteración 2026-04-21)
supersedes: —
inputs:
  - ENT_FABERLOOM_AGENT_BUILDER_v1 v1.0 DRAFT (docs/ENT_FABERLOOM_AGENT_BUILDER_v1.md)
  - SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md (v1.0 DRAFT)
  - project_faberloom_agents_design.md (Skill Studio 3 capas)
  - project_faberloom_architecture.md (AgentSpec/Runtime/Memory)
  - project_faberloom_positioning.md (wedge B2B)
  - COWORK_DELIVERY_FABERLOOM_v3.5.md (D16 Skill Library bidireccional)
aplica_a: [FaberLoom]
---

# SPEC — FaberLoom Skill Composition Model v1

**Documento arquitectónico de decisión.** Define cómo se modelan skills y add-ons en FaberLoom para cubrir dos extremos simultáneamente: skills empaquetados por FaberLoom (sealed, con update channel) y skills creados por clientes (100% editables). Cero ambigüedad, una sola verdad por decisión.

Aplican reglas de KB: R1 no inventar · R2 no tocar FROZEN · R5 documentar todo cambio.

---

## 0. Alcance y estado

**Alcance:** modelo de datos para `Skill` y `Addon`, taxonomía de modos (Sealed/Open), semántica de capas, reglas de fork, update channel, pricing implications, cambios derivados sobre el Blueprint v1 y sobre el catálogo Kimi de 168 agentes.

**No cubre:** UI del Skill Studio (tratado en mockup FROZEN), marketplace externo de terceros (decisión futura), billing detallado por add-on (Ronda 3 del Blueprint).

**Estado v1.0 DRAFT.** Promoción a APPROVED requiere: (a) conciliación con el seed catalog Fase 1 (pendiente — ver §11), (b) validación de que las 4 tablas nuevas encajan en S1 sin romper UUIDv7/RLS, (c) review del Update Channel con al menos un design partner.

---

## 1. Principio rector

**Una sola entidad `Skill`** con un campo `origin` que define quién controla la capa Base. Todo lo demás (configuración, enriquecimiento, learning, add-ons) funciona idéntico sin importar el origen.

**Consecuencia:** no hay dos sistemas paralelos. Una UI, un lifecycle, un modelo de permisos, un motor de ejecución. El Skill Studio es uno solo — cambia la semántica de las capas según el modo.

---

## 2. Anatomía de un Skill: 3 capas + bindings

Las 3 capas del Skill Studio ya aprobadas se mantienen. Se formaliza qué controla quién según modo:

```
┌─────────────────────────────────────────────────────────────┐
│  SKILL                                                      │
│  origin: SEALED | OPEN                                      │
├─────────────────────────────────────────────────────────────┤
│  📦 BASE                                                    │
│     - System prompt, metodología, esquema output            │
│     - SEALED: inmutable, hash lockeado, FaberLoom controla  │
│     - OPEN: editable por el owner                           │
├─────────────────────────────────────────────────────────────┤
│  ✏️  MANUAL OVERLAY                                         │
│     - Tono, criterios propios, escalation, autoridad        │
│     - Siempre editable por el cliente                       │
│     - Diff aplicado en runtime, no toca el Base             │
├─────────────────────────────────────────────────────────────┤
│  🧠 LEARNED OVERLAY                                         │
│     - Corrections, casos resueltos, preferencias detectadas │
│     - Aprende por feedback con pipeline Candidate→Active    │
│     - El usuario puede pinnear/unpinnear/limpiar            │
└─────────────────────────────────────────────────────────────┘
              │
              ▼  many-to-many
┌─────────────────────────────────────────────────────────────┐
│  ADD-ONS (recursos compartidos del tenant)                  │
│  Entidades independientes · ver §5                          │
└─────────────────────────────────────────────────────────────┘
```

**Invariantes:**

- El Base nunca se mezcla con los overlays en storage. Se componen en runtime, cada uno con su trazabilidad.
- Manual Overlay y Learned Overlay son siempre editables por el cliente, independiente del modo del skill.
- La composición sigue siendo auditable: cada token del system prompt final sabe de qué capa viene.

---

## 3. Dos modos únicos: SEALED vs OPEN

### 3.1 Modo SEALED

- **Autor:** exclusivamente FaberLoom
- **Base:** inmutable, identificada por `base_sealed_hash`
- **Updates:** FaberLoom puede publicar nuevas versiones del Base. No se aplican automáticamente. Requieren consent explícito del admin del tenant (ver §7 Update Channel)
- **Modificación del Base:** imposible por el cliente. Si necesita cambiar el Base, debe **forkear** (ver §6)
- **Distribución:** viene como parte del catálogo seed de FaberLoom (Fase 1) o del marketplace oficial de FaberLoom cuando exista
- **Ownership del contrato:** FaberLoom responde por la calidad del Base. Es el "producto" que vendemos

### 3.2 Modo OPEN

- **Autor:** cliente del tenant (usuario individual o admin)
- **Base:** totalmente editable por el owner en cualquier momento
- **Updates:** N/A — el owner es el autor. No hay update channel
- **Modificación:** 100% libre en todas las facetas: prompt base, schema de output, triggers, canales, tono, autoridad, escalation, límites, add-ons bindeados
- **Distribución:** dentro del tenant. El owner puede compartirlo con otros usuarios del mismo tenant vía permisos (ver §8). No hay distribución cross-tenant nativa en Fase 1
- **Ownership del contrato:** el cliente. FaberLoom no garantiza nada sobre la calidad de un Open

### 3.3 Qué significa "100% open en todas sus facetas"

El owner de un skill Open puede, sin restricción:

- Reescribir el system prompt y la metodología entera
- Cambiar el schema de output (estructura, campos, formato)
- Agregar, quitar, reemplazar add-ons
- Modificar triggers, canales, tono, autoridad, escalation, límites
- Exportarlo como YAML (portable)
- Duplicarlo, archivarlo, borrarlo
- Versionarlo con lógica propia

**FaberLoom no puede empujar updates a un Open.** No tiene derecho sobre él. El cliente es dueño absoluto.

### 3.4 Reglas absolutas que aplican a ambos modos

Los 5 límites hardcoded del producto (ver `ENT_FABERLOOM_AGENT_BUILDER_v1.md` §3) aplican **independiente del modo**. Un Open no puede desactivar:

1. Cero envíos externos sin aprobación
2. Cero transacciones financieras autónomas
3. Cero acceso fuera del KB scope configurado
4. Cero aprobaciones legales autónomas
5. Audit trail inmutable

Estos límites viven en el motor de ejecución, no en la config del skill.

---

## 4. Enum canónico y schema

### 4.1 Tipo

```sql
CREATE TYPE skill_origin AS ENUM (
  'sealed',   -- FaberLoom-made, inmutable base
  'open'      -- Client-made, base editable
);
```

**Importante:** en Fase 1 el enum tiene solo 2 valores. Decisiones futuras (marketplace de terceros, partner-sealed) extenderán el enum sin romper compatibilidad — Postgres `ALTER TYPE ... ADD VALUE` es forward-compatible.

### 4.2 Tabla `skills`

```sql
CREATE TABLE skills (
  id              uuid PRIMARY KEY DEFAULT gen_uuid_v7(),
  tenant_id       uuid NOT NULL REFERENCES tenants(id),
  origin          skill_origin NOT NULL,
  name            text NOT NULL,
  slug            text NOT NULL,

  -- Base layer
  base_content    jsonb NOT NULL,        -- system prompt, schema, metodología
  base_sealed_hash text,                 -- NOT NULL si origin='sealed', NULL si 'open'
  base_version    int NOT NULL DEFAULT 1,

  -- Overlays (storage separado, NO mezclado con base)
  manual_overlay  jsonb NOT NULL DEFAULT '{}'::jsonb,
  learned_overlay jsonb NOT NULL DEFAULT '{}'::jsonb,

  -- Lineage
  forked_from     uuid REFERENCES skills(id),
  forked_at       timestamptz,
  forked_from_base_hash text,            -- hash del Base en el momento del fork, para trazabilidad

  -- Ownership / permisos
  owner_user_id   uuid REFERENCES users(id),   -- NULL para sealed (FaberLoom implícito)
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now(),

  -- Estado
  status          text NOT NULL DEFAULT 'draft',   -- draft|active|archived
  autonomy_level  int NOT NULL DEFAULT 0,           -- L0..L4 (shadow → full)

  UNIQUE (tenant_id, slug),
  CHECK (
    (origin = 'sealed' AND base_sealed_hash IS NOT NULL) OR
    (origin = 'open'   AND base_sealed_hash IS NULL)
  )
);

-- RLS por tenant (firma estándar del Blueprint §1)
ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
CREATE POLICY skills_tenant_isolation ON skills
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

### 4.3 Tabla `skill_versions` (solo sealed)

Para el Update Channel. Mantiene el historial de versiones publicadas del Base para skills sealed.

```sql
CREATE TABLE skill_versions (
  id              uuid PRIMARY KEY DEFAULT gen_uuid_v7(),
  skill_slug      text NOT NULL,         -- ej. 'faberloom.track_bot'
  version         int NOT NULL,
  base_content    jsonb NOT NULL,
  base_sealed_hash text NOT NULL,
  published_at    timestamptz NOT NULL DEFAULT now(),
  changelog       text,
  breaking_change boolean NOT NULL DEFAULT false,

  UNIQUE (skill_slug, version)
);
-- Esta tabla es global (no tenant-scoped) porque los sealed son globales.
-- No lleva RLS. Acceso read-only desde todos los tenants.
```

---

## 5. Add-ons como entidades de primer nivel

Los add-ons no viven dentro del skill. Viven a nivel `tenant` y se bindean a uno o más skills vía `skill_addon_bindings`.

### 5.1 Taxonomía de tipos

```sql
CREATE TYPE addon_type AS ENUM (
  'golden_samples',    -- library de ejemplos input/output
  'static_kb',         -- binding a KB estática del tenant
  'living_corpus',     -- fuente externa con re-ingesta programada
  'tool_pack',         -- APIs/funciones invocables
  'memory_profile'     -- memoria de casos + feedback del usuario
);

CREATE TYPE addon_source AS ENUM (
  'self_managed',         -- el cliente lo construyó/mantiene
  'faberloom_curated'     -- FaberLoom lo provee (ej. corpus legal CR básico)
);
```

### 5.2 Tabla `addons`

```sql
CREATE TABLE addons (
  id              uuid PRIMARY KEY DEFAULT gen_uuid_v7(),
  tenant_id       uuid NOT NULL REFERENCES tenants(id),
  type            addon_type NOT NULL,
  source          addon_source NOT NULL,
  name            text NOT NULL,
  config          jsonb NOT NULL,          -- schema depende de type
  refresh_cadence text,                    -- cron, solo living_corpus
  last_refreshed_at timestamptz,
  cost_tier       int NOT NULL DEFAULT 0,  -- 0=free, 1=pro, 2=enterprise
  status          text NOT NULL DEFAULT 'active',
  created_at      timestamptz NOT NULL DEFAULT now(),

  UNIQUE (tenant_id, name)
);

ALTER TABLE addons ENABLE ROW LEVEL SECURITY;
CREATE POLICY addons_tenant_isolation ON addons
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

### 5.3 Tabla `skill_addon_bindings`

```sql
CREATE TABLE skill_addon_bindings (
  skill_id        uuid NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
  addon_id        uuid NOT NULL REFERENCES addons(id) ON DELETE CASCADE,
  binding_config  jsonb NOT NULL DEFAULT '{}'::jsonb,   -- weight, priority, scope overrides
  created_at      timestamptz NOT NULL DEFAULT now(),

  PRIMARY KEY (skill_id, addon_id)
);

-- RLS vía skill_id → skills.tenant_id
ALTER TABLE skill_addon_bindings ENABLE ROW LEVEL SECURITY;
CREATE POLICY skill_addon_bindings_tenant ON skill_addon_bindings
  USING (EXISTS (
    SELECT 1 FROM skills s
    WHERE s.id = skill_id
      AND s.tenant_id = current_setting('app.tenant_id')::uuid
  ));
```

### 5.4 Por qué add-ons separados es correcto

1. **No duplicar costo de ingesta.** Si un tenant tiene 5 skills que usan jurisprudencia CR, ingestamos una sola vez.
2. **Pricing independiente.** Un Living Corpus tiene costo real de ingesta+storage+refresh. Se cobra por addon activo en el tenant, no por skill.
3. **Marketplace de add-ons existe sin marketplace de skills.** Se puede publicar "Corpus VUCE Colombia" como add-on sin tener que publicar también un skill que lo consuma.
4. **Fork preserva add-ons.** Al forkear un sealed, los bindings de add-ons se copian — solo cambia el Base.

---

## 6. Semántica de Fork

### 6.1 Fork de SEALED → resultado OPEN

Es el único path para modificar el Base de un sealed. Consecuencias:

- Se copia el `base_content` actual + `manual_overlay` actual como nuevo `base_content` del Open resultante
- Se resetea `manual_overlay` a `{}` en el fork (si quiere, el usuario puede volver a aplicar diff)
- Se copia `learned_overlay` opcionalmente (flag del wizard de fork)
- Se copian los `skill_addon_bindings` por defecto (opt-out per-binding disponible)
- Se pierde el update channel: el fork ya no recibe patches del sealed original
- `forked_from` y `forked_from_base_hash` se llenan para trazabilidad

### 6.2 Fork de OPEN → resultado OPEN (duplicate)

Es un clone. Sin ceremonia. Nuevo `owner_user_id`, nuevo `id`, mismo contenido. Útil para experimentar sin tocar el original.

### 6.3 UI hint

El Skill Studio debe ser explícito con el usuario antes de forkear un sealed: "vas a perder updates automáticos de FaberLoom. Esta copia queda 100% bajo tu control." El fork no es destructivo — el original sigue intacto.

---

## 7. Update Channel (solo SEALED)

### 7.1 Flujo

1. FaberLoom publica `skill_versions` con version N+1 del slug
2. Un job detecta que hay versión nueva para cada tenant que tiene el skill activo
3. Se inserta una notificación en `skill_update_pending` (tabla operativa, no detallada aquí) con el diff resumido
4. El admin del tenant recibe alerta en la UI: "Update disponible v1.0 → v1.1 para TrackBot. Cambios: [diff resumido]. ¿Aceptar?"
5. Decisiones posibles:
   - **Aceptar:** `base_content` + `base_sealed_hash` se actualizan en la row del skill del tenant. `manual_overlay` y `learned_overlay` se preservan
   - **Rechazar:** queda en versión N hasta próximo aviso. La notificación se archiva
   - **Forkear:** conversión del sealed a open, tomando como base la versión N actual (ver §6.1)

### 7.2 Conflict handling

Si el diff de la versión nueva del Base rompe algo del `manual_overlay` (ej. elimina un campo que el overlay referencia):

- El sistema no aplica automáticamente
- Se marca el skill como `needs_attention`
- Se ofrece al admin un wizard de reconciliación
- El skill sigue funcionando en su versión actual mientras se resuelve

### 7.3 Breaking changes

Las versiones con `breaking_change = true` requieren consent explícito doble (admin + owner de org) y no pueden auto-aplicarse nunca, aunque el tenant tenga auto-updates habilitados.

---

## 8. Sharing y permisos (scope Fase 1)

Un skill Open puede compartirse dentro del mismo tenant. No hay sharing cross-tenant nativo en Fase 1. Los permisos son:

| Nivel | Puede ver | Puede ejecutar | Puede editar Base | Puede editar overlays | Puede bindear add-ons |
|---|---|---|---|---|---|
| Owner | ✅ | ✅ | ✅ (si open) | ✅ | ✅ |
| Editor | ✅ | ✅ | ❌ | ✅ (manual) | ✅ |
| Runner | ✅ | ✅ | ❌ | ❌ | ❌ |
| Auditor | ✅ (read-only + logs) | ❌ | ❌ | ❌ | ❌ |

La tabla `skill_permissions` (no detallada aquí, entra en S2) implementa esto. Para sealed, solo existen permisos de nivel Runner y Editor (nadie puede editar el Base — ni el admin del tenant).

---

## 9. Tipología T1-T4 como propiedad emergente

La clasificación Template/Policy/Living/Expert (ver mensaje de diseño 2026-04-21) **no es una etiqueta rígida del schema**. Es una propiedad emergente del conjunto de add-ons bindeados:

| Combinación de add-ons activos | Tipo emergente |
|---|---|
| Solo `golden_samples` | T1 Template |
| `golden_samples` + `static_kb` | T2 Policy |
| Lo anterior + `living_corpus` | T3 Living |
| Todo lo anterior + `memory_profile` + `tool_pack` | T4 Expert |

El backend calcula el tipo efectivo en runtime para decisiones de pricing, throttling y shadow mode. Un skill que empieza como T2 y se le agrega un Living Corpus se vuelve T3 automáticamente — paga lo que corresponde, sin migración.

---

## 10. Implicaciones de pricing

El modelo de planes del catálogo Kimi (Starter $99 / Professional $199 / Enterprise $299) se replantea así:

| Plan | Skills activos | Modos permitidos | Add-ons habilitados | Corpus incluidos |
|---|---|---|---|---|
| Starter | 3 | Sealed only | `golden_samples`, `static_kb` (self_managed) | — |
| Professional | 10 | Sealed + Open | + `living_corpus` (self_managed), `tool_pack` básico | 1 corpus faberloom_curated |
| Enterprise | Ilimitado | Sealed + Open + Fork | Todos | 3 corpus faberloom_curated |

**Principio:** el plan gobierna capacidades, no una cuota rígida. Los skills Open no cuentan por "$ por agente" — cuentan por costo real de ejecución (tokens) + add-ons activos.

**Nota:** esto es una propuesta. La Ronda 3 del Blueprint v1 debe ratificarlo con análisis unit-economics.

---

## 11. Seed catalog Fase 1 — qué queda pendiente de decidir

Con este modelo, el seed de Fase 1 es:

- 3 skills `sealed` pre-cargados (hechos por FaberLoom)
- N add-ons `faberloom_curated` que los skills usan
- Los clientes pueden crear skills `open` desde día 1 en Skill Studio

**Pendiente de confirmar** (bloqueo previo a promover este SPEC a APPROVED):

- ¿Qué 3 skills concretos del catálogo Kimi son el seed? Opciones según mensaje 2026-04-21:
  - **A** (MVP Kimi genérico): TrackBot + InfoBot + DailyBriefBot
  - **B** (Wedge Marluvas/Tecmater): ProductMatch-EPI + QualifyBot + ProposalBot
  - **C** (Híbrido recomendado por arquitecto): ProductMatch-EPI + InfoBot + DailyBriefBot

La decisión la toma el CEO. Este SPEC no la bloquea — el modelo soporta cualquiera de las tres.

---

## 12. Qué queda abierto (decisiones futuras, no bloquean Fase 1)

1. **Marketplace externo de terceros.** Cuando un publisher no-FaberLoom quiera publicar skills comercialmente. Extiende el enum `skill_origin` con un nuevo valor (`partner_sealed` o similar) sin romper compatibilidad.

2. **Sharing cross-tenant de Open skills.** Un tenant que quiere distribuir su skill Open a otros tenants. Requiere modelo de licencia + pricing + responsabilidad legal. Fase 2+.

3. **Convert Open → Sealed.** Un cliente que quiere venderle su skill a FaberLoom para que lo empaquetemos. Es proceso de negocio, no arquitectura. Flujo: FaberLoom revisa, reescribe, publica como nuevo sealed. El original queda intacto.

4. **Auto-updates de sealed.** Flag por tenant o por skill para aceptar automáticamente versiones no-breaking. Fase 2, requiere feedback operativo de los primeros 3 design partners.

---

## 13. Cambios disparados en otros documentos

1. **`SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md`** — Sprint 1 de S1 sube de 9 a **13 tablas** con: `skills`, `skill_versions`, `addons`, `skill_addon_bindings`. Actualizar §2 Schema y §4 Sprint 1.

2. **`ENT_FABERLOOM_AGENT_BUILDER_v1.md` (en archivo)** — promover a `docs/` activo. Agregarle nota de cabecera referenciando este SPEC como autoridad canónica del modelo de composición. El catálogo de 168 agentes se mantiene como referencia del catálogo de skills posibles; este SPEC define cómo se modelan técnicamente.

3. **Mockup FaberLoom v3.5 (FROZEN)** — cuando salga del freeze, revisar que Skill Studio UI muestre el modo (sealed/open) claramente y que el flujo de Fork exista como wizard explícito.

4. **`COWORK_DELIVERY_FABERLOOM_v3.5.md`** — agregar a §3 D18 nueva decisión: "Modelo de composición Skill Sealed/Open + Add-ons separados. Ver SPEC_FABERLOOM_SKILL_COMPOSITION_v1."

5. **Pricing page cuando se diseñe** — usar el modelo de §10 como base, no "agentes por plan."

---

## 14. Registro de cambios

| Fecha | Versión | Cambio |
|---|---|---|
| 2026-04-21 | 1.0 DRAFT | Primera emisión. Decisión arquitectónica de modo dual Sealed/Open + Add-ons como entidades de primer nivel. Autoridad: CEO + arquitecto. |

---

## 15. Referencias y linaje

- `docs/archivo/ENT_FABERLOOM_AGENT_BUILDER_v1.md` — catálogo 168 agentes (Kimi Swarm 2026-04-13)
- `docs/SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` — schema S1/S2/S3, RLS, UUIDv7
- `.auto-memory/project_faberloom_agents_design.md` — Skill Studio 3 capas original
- `.auto-memory/project_faberloom_architecture.md` — AgentSpec/Runtime/Memory
- `.auto-memory/project_faberloom_cowork_handoff.md` — D12 decouple Position↔User, D16 Skill Library bidireccional

*SPEC_FABERLOOM_SKILL_COMPOSITION_v1.0 DRAFT — Muito Work Limitada · 2026-04-21*
