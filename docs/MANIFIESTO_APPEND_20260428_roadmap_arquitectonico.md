# MANIFIESTO_APPEND — Roadmap Arquitectónico FaberLoom
aplica_a: [SHARED]

**Fecha:** 2026-04-28
**Sesión:** Diseño post-cierre del CORE — Anillo 1 al Anillo 6
**Status:** **DRAFT — diseño propuesto, no cementado**

---

## Naturaleza de este documento

Este documento es **complementario** al cierre formal del CORE
(`MANIFIESTO_APPEND_20260428_core_blindado.md` con tag `core-v1.0-blindado`).

A diferencia del cierre formal — que tiene validación dual ChatGPT 5.5 +
Kimi K2.6 con threshold ≥8.5 — este documento:

- Está en **status DRAFT explícito**
- **No requiere tag git**
- **No tiene validación externa** todavía
- Captura propuestas arquitectónicas emergentes de la sesión 2026-04-28
- Es **input para próxima ronda de auditorías** (Anillo 1+2 con misma
  metodología iterativa)

**Por qué se documenta ahora:** la sesión generó 8 propuestas arquitectónicas
maduras que conviene cementar como artefacto auditable antes de que se
diluyan en conversaciones posteriores. Cuando se audite Anillo 1+2, este
documento es el bundle base.

---

## Contexto del producto

FaberLoom es un SaaS multi-tenant para PYMEs LATAM con agentes IA
graduables (L0-L4). Tiers Starter $29 → Pro $79 → Enterprise $299 →
Government $999+. Wedge inicial: cobranza + proformas con WhatsApp
Business como canal primario. Stack: Postgres + RLS + pg-boss + Letta +
Action Engine + LiteLLM. CORE blindado el 2026-04-28 (ARCH v1.5 +
POL_DATA v1.4).

Los 8 bloques de este documento se construyen **sobre el CORE blindado**
sin modificarlo. Cada bloque declara explícitamente qué principios
canónicos del CORE soporta su diseño.

---

## Bloque 4 — Modelo de identidad nativo + federación opcional

### Principio
FaberLoom es su propio IdP nativo cuando el tenant no tiene IdP moderno
(70% del wedge LATAM PYME tiene correo hosteado tipo Hostinger/cPanel/
Zimbra sin estructura organizacional). Federación SSO/SCIM con
Workspace/M365 es **capa opcional encima** del modelo nativo.

### Patrón escalonado por tier

**Nivel 1 — Roles predefinidos (Starter $29 — sin sync IdP):**
- 5 roles fijos: `owner`, `admin`, `manager`, `employee`, `external`
- Lista plana de usuarios, manager attribute, áreas opcionales
- Magic link via email + validación DNS TXT del dominio del tenant
- Cero dependencia de Workspace/M365

**Nivel 2 — Roles + Groups + Manager (Pro $79 — sync opcional):**
- Custom groups hasta 20 por tenant
- Manager hierarchy hasta 3 niveles
- OUs simples hasta 3 niveles
- Sync OAuth diario opcional con Google Workspace o M365

**Nivel 3 — SCIM 2.0 + OUs ilimitadas + Custom roles (Enterprise+):**
- Provisioning SCIM 2.0 (Workspace/M365/Okta/Azure AD/Auth0)
- OU jerárquica espejo del IdP
- Custom roles con permission matrix granular
- Audit log obligatorio + re-certificación trimestral (Government)

### Schema técnico (Anillo 4)
```
tenant_user, tenant_area, tenant_group, tenant_user_group,
tenant_role, tenant_role_assignment
```

### Validación de dominio
DNS TXT record + magic link a buzón existente + verificación SMTP.

### Federación opcional
Login federado SSO (OIDC/SAML), sync de directorio diario via OAuth (Pro),
SCIM 2.0 push automático (Enterprise+).

### Conexión con CORE blindado
- P13 jerarquía intra-tenant — el modelo de identidad provee los roles
  del consultante para pre-filtering
- humano_responsable del glosario — resuelve ocupante de position
  desde tenant_user

---

## Bloque 5 — Matriz 2 access_matrix per-agente

### Principio
La matriz RBAC clásica (matriz 1, tipo MWT.ONE Roles y Permisos) cubre
**administración del agente como entidad**. Pero un agente IA tiene
una segunda dimensión que no encaja en CRUD: **a quién responde y qué
le muestra a cada uno**. Esa es la **matriz 2 access_matrix**, definida
**per-agente** en su AgentSpec.

### Dos matrices distintas
**Matriz 1 (RBAC clásico, en MWT.ONE):**
| Rol | Crear | Leer | Actualizar Spec | Eliminar | Subir autonomy |
|-----|-------|------|-----------------|----------|----------------|

**Matriz 2 (per-agente, dentro de AgentSpec):**
| Rol consultante | Ve disponible | Invoca | Datos propios | Datos terceros | Step-up |
|-----------------|---------------|--------|---------------|----------------|---------|

### Por qué no se puede mezclar
"Leer" significa cosas distintas (ver config / invocar / ver respuestas).
"Crear" colapsa 2 acciones (crear agente / crear conversación con agente).
La matriz CRUD pierde la dimensión "datos del consultante".

### Schema técnico (Anillo 2)
```yaml
AgentSpec.access_matrix:
  visible_to: [group_ids, role_ids]
  invokable_by: [group_ids, role_ids]
  data_propios_acceso:
    rule_default: N1
    rule_step_up_B: [N2, N3]
    rule_step_up_C: [N4, formal_documents]
  data_terceros_acceso:
    role:manager: ver datos N1 de sus reports directos
    role:director_rrhh: ver N3 full org
    role:owner: full
  autonomy_max_per_role:
    employee: L1
    manager: L1
    director_rrhh: L2
    owner: L4
```

### Conexión con CORE blindado
- P13 jerarquía intra-tenant — declara estructura de access_matrix
- Pre-filtering en retrieval — consume la matriz al construir contexto
- Step-up auth Niveles A/B/C — referenciados desde access_matrix

---

## Bloque 6 — Módulo de Administración del Tenant (8 tabs)

### Estructura
```
FaberLoom Console / Tenant Admin
├─ 1. Equipo y Jerarquía       (matriz 1 RBAC + identidad nativa/federada)
├─ 2. Agentes y Skills         (lista, status, autonomy ladder)
├─ 3. Consumo y Costos         (tokens, USD, predicción, cost-mode savings)
├─ 4. Productividad y ROI      (Tipo A/B/C, tiempo ahorrado, $$ activado)
├─ 5. Aprendizaje y Calidad    (gold samples, approval trend, candidates)
├─ 6. Auditoría y Compliance   (logs inmutables, step-up events,
│                                reportes regulatorios LGPD/Ley 1581/etc)
├─ 7. Configuración            (tier, add-ons, integraciones, dominio)
└─ 8. Conocimiento del tenant  (Hallazgos — ver Bloque 9)
```

### Dashboard inicial obligatorio
Vista resumen del mes con: ROI, adopción, agentes activos, consumo,
aprendizaje, compliance. El owner ve en 30 segundos si vale la pena
renovar.

### Backing técnico (ya en CORE)
- Action Engine D6 observability provee data raw
- OutcomeLedger persiste cada trace
- P5 + P6 + P8 + P11 generan métricas de calidad
- SPEC_AUDIT_MODULE D10 provee logs inmutables

### Diferenciador comercial vs Claude.ai/ChatGPT
Tabs 4 (ROI) + 5 (Aprendizaje) + 8 (Conocimiento) **no existen en
consolas IA generales**. Justifican pricing tiered y retención
mes-a-mes.

### Priorización para implementación
Tabs 1-2-3 son obligatorios MVP (sin esos no hay producto). Tabs 4-5
son los **diferenciadores comerciales** que justifican Pro+. Tabs
6-7-8 emergen con tiempo y feedback. **No construir los 8 en paralelo.**

---

## Bloque 6.bis — Sistema de KPIs editables con integridad histórica

### Principio
Los KPIs son artefactos vivos que evolucionan. La realidad cambia
(salarios, procesos, equipos). Pero la edición libre rompe integridad
histórica. Solución: **versionado obligatorio + corte temporal limpio**.

### 3 niveles de granularidad

| Nivel | Qué se mide | Pregunta que responde |
|-------|-------------|----------------------|
| Workflow / Skill | ROI Tipo A/B/C, baseline, ahorro por workflow, TTG | "¿Vale la pena el workflow X?" |
| Agente | Approval rate, autonomy_level, gold samples, costo tokens | "¿Está mejorando este agente?" |
| Usuario | Adopción, productividad personal, workflows usados | "¿El usuario aprovecha el producto?" |

### 3 categorías de KPIs por su naturaleza

| Categoría | Quién mide | Editable | Ejemplo |
|-----------|------------|----------|---------|
| `system_fixed` | Sistema (telemetría P8) | NO | approval_rate, latency, cost |
| `client_declared` | Cliente declara onboarding | SÍ con audit | baseline_minutes_manual, hourly_rate |
| `client_custom` | Cliente crea desde cero | SÍ libre | "Tasa de respuesta", "Mood score" |

### Reglas de integridad histórica (no negociables)
1. Edición de baseline ≠ rewriting histórico. Edición crea **nueva
   versión** con `effective_from = now()`. Métricas anteriores
   permanecen atadas a versión que estaba vigente cuando sucedieron.
2. Ejecuciones se cementan al `kpi_value_version_id` activo en su
   momento. Append-only inmutable.
3. Cambio de baseline requiere **razón documentada** obligatoria.
4. Histórico siempre legible: "Último cambio: [fecha] · ✏️ Ver historial".
5. Sistema sugiere recalibración periódica (6 meses), no obligatoria.

### Edición de KPI = Hallazgo (hereda Bloque 9)
Cada edición de KPI cliente_declarado/cliente_custom es un Hallazgo
tipo `kpi_actualizado`. Pasa por pipeline P5 + AuditEntry inmutable +
propagación P12 si afecta múltiples skills. Cero mecánica nueva.

### Editabilidad escalonada por tier
| Tier | KPIs editables permitidos |
|------|--------------------------|
| Starter | Solo `client_declared` básicos en 5 workflows |
| Pro | + `client_custom` hasta 10 por tenant |
| Enterprise | + `client_custom` ilimitados + fórmulas custom + alertas |
| Government | + auditables con cadena de aprobación |

### Schema técnico (Anillo 2)
```sql
kpi_definition (id, tenant_id, level, category, formula_jsonb, ...)
kpi_value_version (id, definition_id, scope_id, version_number,
                   effective_from, effective_until, reason_for_change,
                   hallazgo_id, ...)
kpi_measurement (id, definition_id, scope_id,
                 kpi_value_version_id_active_when, measured_value,
                 measured_at, data_source)  -- append-only inmutable
```

### Conexión con CORE blindado
- R3 (no eliminar contenido aprobado) — versionado en lugar de rewriting
- R1 (no inventar) — cliente declara, sistema mide objetivo
- P11 (clasificador 3 destinos) — cada cambio es Hallazgo
- D10 (audit chain) — AuditEntry inmutable por cambio

---

## Bloque 6.ter — Vista de productividad personal del usuario

### Principio
El admin del tenant ve a Ana. Pero **Ana también necesita ver a Ana**.
La adopción y retención dependen de que el usuario individual perciba
el valor que el producto le da personalmente. Si solo el dueño ve los
beneficios, los empleados resisten o saboteen el uso.

### Vista propia del usuario — accesible en cualquier tier
Cada usuario tiene su tab "Mi productividad" con su propia trayectoria:

```
┌──────────────────────────────────────────────────────────┐
│ Mi productividad — Ana Gómez                             │
│ Activa desde: 2026-03-01 · 47 días en FaberLoom         │
├──────────────────────────────────────────────────────────┤
│                                                           │
│ TIEMPO RECUPERADO ESTE MES                                │
│ 18.5 horas equivalentes                                   │
│ ▆▆▆▆▆▆▆▆▆▆▇▇▇▇▇▇▇▇▇▇  (vs 12.4h mes pasado · +49%)     │
│                                                           │
│ EQUIVALENCIA                                              │
│ A tu rate ($15/h): $278 ahorrados                        │
│ Equivale a: 2 días laborales completos                   │
│                                                           │
│ TUS WORKFLOWS MÁS ÚTILES                                  │
│ 1. Cobranza día 7        32 ejec    $171 ahorrado        │
│ 2. Proforma rápida       15 ejec    $74 ahorrado         │
│ 3. Recordatorio cliente  9 ejec     $33 ahorrado         │
│                                                           │
│ TRAYECTORIA                                               │
│ Día 1:  Aprendiendo el producto                          │
│ Día 7:  Primera cobranza completada (7 min)              │
│ Día 14: Cobranza promedio bajó a 4 min                   │
│ Día 30: Cobranza promedio en 3.4 min · 93% sin edición   │
│                                                           │
│ ESTÁS MEJORANDO                                           │
│ Aprobación de tus drafts: 78% → 93% (en 30 días)         │
│ Edición ligera: 65% → 85%                                │
│                                                           │
│ COMPARADO CON TU EQUIPO                                   │
│ Top 3 usuarios por tiempo ahorrado en Marluvas:          │
│   1. Ana Gómez       18.5h ← vos                         │
│   2. Carlos Mejía    12.2h                               │
│   3. Pedro Ruiz      8.1h                                │
│                                                           │
│ ⭐ Tu satisfacción con FaberLoom: ⭐⭐⭐⭐ (editable)      │
└──────────────────────────────────────────────────────────┘
```

### Métricas que muestra esta vista
| Métrica | Origen |
|---------|--------|
| Tiempo recuperado mensual | Suma de ahorros de workflows que el usuario aprobó |
| Equivalencia $$ | Tiempo × hourly_rate del rol del usuario |
| Comparación mes a mes | Histórico de kpi_measurement |
| Trayectoria personal | Eventos clave + métricas evolucionando |
| Mejora propia | Approval rate / edit-light rate del usuario evolucionando |
| Ranking interno (opcional) | Top usuarios del tenant — opt-in del admin |
| Satisfacción (autoeval) | Hallazgo tipo `kpi_propuesto` editable por el usuario |

### Por qué importa para el negocio
| Sin vista personal del usuario | Con vista personal del usuario |
|-------------------------------|-------------------------------|
| Solo el owner ve valor | Cada empleado ve valor propio |
| Empleados resisten herramientas que les "controlan" | Empleados defienden herramienta que les ayuda |
| Renovación depende solo del dueño | Renovación tiene defensores en todo el equipo |
| Adopción asimétrica (algunos sí, otros no) | Gamificación natural por ranking interno |
| Time to first personal value desconocido | Métrica medible y mejorable |

### Privacidad y permisos
- Cada usuario solo ve **su propia** vista (scope=user_self)
- Comparación con equipo es **opt-in del admin del tenant** — el admin
  puede deshabilitarla si genera ambiente competitivo no deseado
- Datos del usuario están protegidos por step-up auth (Bloque CORE
  v1.5 P13) si se vuelve N3 (ej. ranking de productividad puede ser
  considerado dato sensible laboral en algunos países)

### Schema técnico (Anillo 2)
```sql
user_productivity_snapshot (
  id, tenant_id, user_id, period_month,
  total_time_saved_min, total_value_usd,
  workflows_used_count, top_workflows_jsonb,
  approval_rate, edit_light_rate,
  satisfaction_self_rating,            -- 1-5 ⭐
  generated_at
)  -- snapshot mensual append-only
```

### Conexión con CORE blindado
- P13 jerarquía intra-tenant — usuario solo ve datos propios
- Step-up auth — si datos comparativos son N3
- P8 telemetría obligatoria — alimenta directamente
- R1 no inventar — métricas son medidas, no estimadas

---

## Bloque 7 — Patrón ROI riguroso con 3 tipos de valor

### Principio
La IA aporta 3 tipos de valor distintos que no se pueden mezclar en
una sola métrica. Cada uno tiene mecánica de captura y métrica
diferenciada.

### Las 3 categorías

**Tipo A — Automatización**
- Cliente ya hace el proceso manualmente
- Captura: `baseline_minutes_real` + `hourly_rate`
- Métrica: ahorro = (baseline - tiempo_agente) × ejecuciones
- Pricing: incluido desde Starter $29

**Tipo B — Activación**
- Cliente reconoce proceso posible pero no lo hace (limitación de
  costo/tiempo/personal)
- Captura: `baseline_minutes_estimated` (refinado iterativamente) +
  `potential_executions_per_month` + `unit_value_declared`
- Métrica: valor activado = ejecuciones reales × valor unitario
- Pricing: justifica upsell a Pro $79

**Tipo C — Descubrimiento**
- Cliente reconoce proceso no factible manual (volumen/velocidad/
  complejidad/datos no observables)
- Captura: `enabled_decision_description` + `decision_value_declared` +
  `validation_methodology`
- Métrica: valor habilitado × factor_confianza (0.3-0.8 según
  validación contrafactual)
- Pricing: justifica Enterprise $299+ y Government

### Onboarding diferenciado
```
Pregunta inicial: "¿Hacés este proceso hoy?"
  Sí manual          → Tipo A
  No, podría         → Tipo B (con captura de razón de no-hacerlo)
  No es factible     → Tipo C (con captura de valor habilitado)
```

### "Reloj del ROI" arranca en primer Golden Sample
- Fase de onboarding: cliente declara baseline
- Fase de iteración: tracking sin contar como ahorro (es inversión)
- Primer Gold Sample validado: ROI clock starts
- Producción: cada ejecución suma al ahorro acumulado
- Break-even visible cuando ahorro acumulado = inversión inicial

### Schema técnico (Anillo 2)
```sql
process_baseline (
  workflow_id, tenant_id, declared_at, declared_by,
  process_type ENUM ('A', 'B', 'C'),
  -- Campos diferenciados según tipo
  baseline_minutes_real, hourly_rate_usd,                     -- Tipo A
  baseline_minutes_estimated, baseline_recalibration_history,
  reason_not_doing_today, potential_executions_per_month,
  unit_value_declared_usd,                                    -- Tipo B
  why_not_feasible_manually, enabled_decision_description,
  decision_value_declared_usd, measurement_methodology,
  validation_required                                          -- Tipo C
)

training_iteration (...)   -- fase pre-gold sample, append-only
execution_metric (...)     -- fase producción, append-only inmutable
```

### Honestidad metodológica obligatoria
- Caveat visible en dashboard: "Baseline declarado el [fecha] —
  Recalibrar"
- Inversión inicial NO escondida, mostrada explícita
- Tipo C separado de A+B con factor confianza visible
- R1 no inventar: cliente declara baselines, sistema mide tiempos reales

### Diferenciador comercial
Argumento de upsell tier-by-tier: "Starter te ahorra. Pro te activa.
Enterprise te descubre. Government te valida."

### Conexión con CORE blindado
- R1 no inventar — todo es declarado por cliente o medido
- P5 termómetro — refinamiento iterativo del baseline en Tipo B
- P14 deterministic-first — validación contrafactual de Tipo C
- P9 gobernanza embebida — caveats metodológicos como gate

---

## Bloque 8 — Patrón Agent Builder — meta-agente con 3 capas

### Concepto
El primer agente que conoce un cliente de FaberLoom es el **Agent
Builder** — un agente SEALED publicado por FaberLoom que crea otros
agentes mediante conversación. Reemplaza formulario de configuración
con entrevista guiada.

### Arquitectura en 3 capas (heredada de SPEC_FABERLOOM_SKILL_COMPOSITION)

**BASE (Sealed — FaberLoom controla):**
- System prompt + metodología
- Conocimiento del protocolo de iniciación
- Templates de AgentSpec
- Reglas hardcoded (P3, R1, P5, P11)
- Update Channel: cliente acepta/rechaza/forkea (idéntico a Skill SEALED)

**MANUAL OVERLAY (per-tenant, admin edita):**
- Glosario interno del tenant
- Convenciones de naming
- Reglas específicas del tenant

**LEARNED OVERLAY (per-tenant, P13 aislado):**
- Hallazgos de iteraciones previas
- Patrones de cómo el cliente describe procesos
- Dominios ya descubiertos en este tenant
- Estilo de comunicación per-usuario
- Glosario del tenant detectado automáticamente

### Protocolo de iniciación — 8 fases (recomendación: arrancar con 4 en MVP)
1. Triage (¿está en mi base sealed o es dominio nuevo?)
2. Indagación (objetivo + tipo + contexto + restricciones)
3. Validación de comprensión (cliente confirma reformulación)
4. Almacenamiento de hallazgos (4 destinos diferenciados — Bloque 9)
5. Generación AgentSpec DRAFT
6. Review con usuario [v2 — extensión post-MVP]
7. Iteración hasta Golden Sample (P5 + P11) [v2]
8. Promoción + actualización LEARNED OVERLAY [v2]

**MVP arranca con Fases 1-3 + 5.** Resto se expande con feedback real.

### Modo express vs profundo
El Builder debe tener:
- **Modo express** (5 minutos, captura solo crítico, refinamiento
  iterativo después) — default para PYME chica
- **Modo profundo** (20 minutos, protocolo completo) — opt-in para
  setup serio

### KPIs del Builder mismo (auto-mejora)
- Time to Spec (<20 min objetivo)
- Time to Golden Sample (TTG)
- % conversaciones que llegan a Spec
- % Specs que llegan a Gold Sample
- Re-trabajos post Spec
- Reducción de TTG con cada iniciación en mismo tenant

### Schema técnico (Anillo 2)
```sql
discovery_session (
  id, tenant_id, initiated_by_user_id, builder_agent_id,
  current_phase, status, resulting_agent_id,
  conversation_log (jsonb), hallazgos_extraidos (jsonb),
  total_turns, total_duration_min, user_corrections_count,
  domain_detected, ...
)
```

### Aislamiento P13 respetado
LEARNED OVERLAY del Builder es per-tenant exclusivamente. No hay global
learning del Builder cross-tenant. Update del Sealed (FaberLoom)
preserva ambas overlays per-tenant.

### Diferenciador comercial defensivo
Cliente acumula activo único (LEARNED OVERLAY) que no es transferible —
alto switching cost. TTG baja con cada agente creado. Onboarding
conversacional vs formulario competidores. Time to first value <48h,
ROI visible <7 días.

### Conexión con CORE blindado
- Todos P0-P14 (es un agente más, sealed)
- SPEC_FABERLOOM_SKILL_COMPOSITION (modelo Sealed/Open)
- P5 + P11 (coordinación de iteración)
- P13 (aislamiento per-tenant)
- D10 (discovery_session inmutable)

---

## Bloque 9 — Patrón Hallazgo — primitiva unificada

### Principio
Toda interacción del producto que descubra información relevante (hechos,
reglas, convenciones, excepciones, insights, riesgos, KPIs propuestos)
materializa el descubrimiento como entidad `Hallazgo` con API uniforme.
**Cero documentación ad-hoc por feature.**

### Fuentes posibles (uniformes via API)
- `agent_builder` (Fase 4 del protocolo de iniciación — Bloque 8)
- `agent_runtime` (correcciones P6, rechazos, gold samples)
- `admin_action` (configuración manual)
- `user_feedback` (thumbs, reportes)
- `observability_alert` (drops de approval, anomalías)
- `audit_event` (detecciones del Action Engine)
- `external_event` (calendar, mail, integraciones)

### Tipos de Hallazgo
- `hecho_org` (organizational fact)
- `regla_negocio` (business rule)
- `convencion` (naming/style convention)
- `excepcion` (documented exception)
- `insight_operacional` (operational insight)
- `riesgo_detectado` (detected risk)
- `kpi_propuesto` (suggested metric)
- `kpi_actualizado` (KPI value change — Bloque 6.bis)

### Pipeline obligatorio (P5 + P11 + P12 canónicos)
```
[Cualquier interacción] → capture_hallazgo()
                              ↓
                       status: CANDIDATE
                              ↓
              [Cola de revisión del humano_responsable]
                              ↓
                Modal P11 muestra tipo / scope / destino
                              ↓
              Humano confirma / cambia / descarta (P5 gate)
                              ↓
                 status: ACTIVE en destino correspondiente
                              ↓
        Disponible para retrieval con pre-filtering por permisos
```

### Destinos de promoción (heredados de P11)
- `contexto_org` → pgvector namespace tenant
- `agent_memory` → AgentMemory de skill específico
- `manual_overlay` → MANUAL OVERLAY de skill o agente
- `gold_sample` → AgentMemory como gold sample

### UI — Tab 8 del módulo admin: "Conocimiento del tenant"
- Candidates esperando revisión (termómetro 🔴🟡🔵)
- Activos por tipo / origen / scope
- Buscador de conocimiento del tenant
- Top contribuidores (Builder, agentes, admin)
- Histórico de superseded/archived

### Riesgo arquitectónico crítico que cuidar
**UX de revisión debe ser baja fricción.** Si revisar un Hallazgo toma
>30 segundos, el cliente abandona el termómetro y los candidates se
acumulan, anulando el sistema. **Diseñar la UX de revisión antes que
el schema técnico.**

### Schema técnico (Anillo 2)
```sql
hallazgo (
  id, tenant_id, captured_at, captured_by_user_id,
  source, source_ref, tipo,
  contenido_texto, contenido_estructurado (jsonb), ejemplos (jsonb),
  classification, scope, skill_ids_afectados, areas_aplicables,
  status, promovido_por_user_id, promovido_at, destino_promocion,
  supersedes_hallazgo_id, confirma_hallazgo_id, contradice_hallazgo_id,
  retention_until, audit_entry_id, visibility
)
hallazgo_review_queue, hallazgo_audit, hallazgo_embedding,
hallazgo_revision_history
```

### Propiedades heredadas del CORE
- Aislamiento per-tenant (P13)
- Classification N0-N4 (POL_DATA_CLASSIFICATION §I)
- Pre-filtering en retrieval (P13 v1.5)
- Step-up auth para hallazgos N3+ (P13)
- AuditEntry inmutable (D10)
- Retention por classification (POL §M)
- Visibility por tier (POL_VISIBILIDAD)

### Diferenciador comercial — anti-churn definitivo
El cliente ve crecer su patrimonio de conocimiento. 134 hallazgos
activos = activo único no transferible. Switching cost máximo: irse
de FaberLoom = perder esto.

---

## Síntesis arquitectónica

### Mapa de los 8 bloques en el modelo de anillos

```
┌──────────────────────────────────────────────────────┐
│ ANILLO 7 — COMPLIANCE  (envuelve todo)               │
│  Tab 6 Auditoría · LGPD · ISO · Government tier      │
│  ┌────────────────────────────────────────────────┐  │
│  │ ANILLO 6 — COMERCIAL                           │  │
│  │  Pricing tier escalonado por bloque            │  │
│  │  ┌──────────────────────────────────────────┐  │  │
│  │  │ ANILLO 5 — PRODUCTO                      │  │  │
│  │  │  Bloque 6 (8 tabs) · 6.bis · 6.ter       │  │  │
│  │  │  Bloque 8 Agent Builder (UI conversac.) │  │  │
│  │  │  ┌────────────────────────────────────┐  │  │  │
│  │  │  │ ANILLO 4 — INFRA                   │  │  │  │
│  │  │  │  Bloque 4 (identidad nativa+fed)   │  │  │  │
│  │  │  │  ┌──────────────────────────────┐  │  │  │  │
│  │  │  │  │ ANILLO 3 — EJECUCIÓN         │  │  │  │  │
│  │  │  │  │  Bloque 7 (process_baseline) │  │  │  │  │
│  │  │  │  │  Bloque 9 (capture_hallazgo) │  │  │  │  │
│  │  │  │  │  ┌────────────────────────┐  │  │  │  │  │
│  │  │  │  │  │ ANILLO 2 — COMPOSICIÓN │  │  │  │  │  │
│  │  │  │  │  │  Bloque 5 access_matrix│  │  │  │  │  │
│  │  │  │  │  │  Bloque 6.bis KPIs     │  │  │  │  │  │
│  │  │  │  │  │  Bloque 8 schemas      │  │  │  │  │  │
│  │  │  │  │  │  Bloque 9 schemas      │  │  │  │  │  │
│  │  │  │  │  │  ┌──────────────────┐  │  │  │  │  │  │
│  │  │  │  │  │  │ ANILLO 1         │  │  │  │  │  │  │
│  │  │  │  │  │  │ CONTRATOS ya     │  │  │  │  │  │  │
│  │  │  │  │  │  │ vigentes:        │  │  │  │  │  │  │
│  │  │  │  │  │  │ Action Engine    │  │  │  │  │  │  │
│  │  │  │  │  │  │ Audit Module     │  │  │  │  │  │  │
│  │  │  │  │  │  │  ┌────────────┐  │  │  │  │  │  │  │
│  │  │  │  │  │  │  │ ANILLO 0   │  │  │  │  │  │  │  │
│  │  │  │  │  │  │  │ CORE       │  │  │  │  │  │  │  │
│  │  │  │  │  │  │  │ BLINDADO ✅│  │  │  │  │  │  │  │
│  │  │  │  │  │  │  └────────────┘  │  │  │  │  │  │  │
│  │  │  │  │  │  └──────────────────┘  │  │  │  │  │  │
│  │  │  │  │  └────────────────────────┘  │  │  │  │  │
│  │  │  │  └──────────────────────────────┘  │  │  │  │
│  │  │  └────────────────────────────────────┘  │  │  │
│  │  └──────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

### Cero modificaciones al CORE blindado
**Cada uno de los 8 bloques se construye sobre el CORE sin modificarlo.**
Los principios canónicos son las primitivas; estos bloques son sus
materializaciones.

---

## Próximos pasos de validación

### Auditoría Anillo 1 (próxima sesión recomendada)
- SPEC_ACTION_ENGINE v1.2 + SPEC_AUDIT_MODULE v1.0
- Misma metodología iterativa: ChatGPT 5.5 + Kimi K2.6 paralelos,
  threshold ≥8.5, 0 BLOCKERs
- Bundle base = los 2 SPECs + extractos relevantes del CORE blindado

### Auditoría Anillo 2 (después de Anillo 1)
Bundle propuesto:
- Este documento de roadmap arquitectónico (Bloques 4-9)
- SPEC_FABERLOOM_SKILL_COMPOSITION v1.0
- SPEC_FABERLOOM_AGENT_COMPOSITION v1.1
- SPEC_FABERLOOM_WORKFLOW_ENGINE v1.0

Auditoría stress-tests los 8 bloques contra coherencia interna,
compatibilidad con CORE blindado, edge cases, y operabilidad.

### Resoluciones residuales del CORE (de iter 3 auditores)
A revisar durante auditoría Anillo 1+2:
1. Catalogar `error_class` y "IP estable" en glosario formal
2. Sensor de detección de memory leak entre workers (SPEC_AUDIT_MODULE)
3. Playbook de des-identificación irreversible para promoción N2+
   a Org-wide (P12)

---

## Status del documento

| Aspecto | Estado |
|---------|--------|
| Status | DRAFT |
| Validación externa | Ninguna todavía |
| Tag git | No aplica (no es cierre formal) |
| Aprobador conceptual | CEO (sesión 2026-04-28) |
| Aprobación arquitectónica formal | Pendiente — auditoría Anillo 1+2 |
| Modificaciones al CORE | Cero — todos los bloques se construyen sobre |

---

## Origen del documento

Sesión Cowork "MWT Knowledge" 2026-04-28 — sesión de diseño post-cierre
formal del CORE. CEO (Álvaro) y arquitecto (Claude Sonnet 4.6) iteraron
sobre arquitectura de anillos exteriores. Decisiones clave de la sesión:

- Separación de matrices RBAC (admin) vs access_matrix (per-agente)
- Modelo de identidad nativo + federación opcional (no SCIM-first)
- Tipo A/B/C de valor con onboarding diferenciado
- Reloj del ROI desde primer Golden Sample (no desde instalación)
- Builder con 3 capas + protocolo de iniciación + LEARNED OVERLAY per-tenant
- Hallazgo como primitiva unificada (cero documentación ad-hoc)
- KPIs con versionado obligatorio + integridad histórica
- Vista personal del usuario para adopción + retención
