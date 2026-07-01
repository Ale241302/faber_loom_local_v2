---
id: SPEC_USER_ADMIN_KNOWLEDGE_FLOW
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FABERLOOM
date: 2026-04-19
authors: CEO + arquitecto (decisión sobre gaps residuales)
inputs:
  - docs/archivo/2026-04-faberloom-prep/PROMPT_AUDITORIA_USER_ADMIN_KNOWLEDGE_FLOW_2026-04-19.md (v1) [movido 2026-04-27 audit]
  - docs/archivo/2026-04-faberloom-prep/PROMPT_AUDITORIA_v2_REPREGUNTA_2026-04-19.md (v2) [movido 2026-04-27 audit]
  - Respuesta auditor externo v1 + v2
  - ARCH_AGENT_PRINCIPLES (P11, P12, P13)
  - 3 objetos base: AgentSpec · AgentRuntime · AgentMemory
aplica_a: [SHARED]
---

# SPEC — User Admin, Directory Sync & Knowledge Flow (v1 beta)

## 0. Alcance

Define **identidad, permisos y flujo de conocimiento** para FaberLoom v1 beta (ventana 2026-04-20 → 2026-06-12).

**Cubre:**
- Modelo de usuario + directory sync + authz
- Taxonomía de conocimiento y composición de overlays
- Governance con los 3 roles actuales
- Rollback versionado y leakage tests obligatorios
- Beta slice 6-8 semanas con owners

**NO cubre (rondas futuras):**
- Billing completo (pricing, gates, metered, LATAM fiscal) — ronda 3 dedicada
- Connectors / integraciones — ronda 4 dedicada
- Simulador de precedencias (va a v1.5)
- SCIM full (va a v1.5+)
- Policy engine externo OPA/Cedar (va cuando gatille umbral operativo — §1.8)
- Certificación SOC 2 / ISO 27001 formal — ronda 5 opcional

---

## 1. Modelo de identidad

### 1.1 Decisión principal

**v1 beta: OIDC (Microsoft / Google) + manual / CSV + authz local.** SCIM no es requisito de entrada.

**Regla maestra:** *directory manda identidad; FaberLoom manda autorización.* La jerarquía del directory NO se mapea a permisos efectivos — se usa para bootstrap, sugerencias de equipo y defaults de sharing.

### 1.2 Modo de identidad por tier

| Modo | Login | Provisioning | Tier pricing |
|---|---|---|---|
| Local | Magic link / passwordless | Manual / CSV | Free / Starter |
| SSO Lite | OIDC Microsoft / Google | Manual / CSV | Growth (paid) |
| Directory Sync Read-Only | OIDC + lectura users/groups | Sync periódico | Pro (paid) |
| Full SCIM | OIDC + SCIM create/update/deprovision | Automático | Enterprise (v1.5+) |

### 1.3 Campos sincronizados desde directory

| Campo FaberLoom | Source Microsoft / Google | Source of truth |
|---|---|---|
| `external_directory_provider` | Entra / Google | directory |
| `external_user_id` | Graph id / Directory id | directory |
| `primary_email` | mail / UPN / primaryEmail | directory |
| `display_name` | displayName / name.fullName | directory |
| `given_name` | givenName | directory |
| `family_name` | surname / familyName | directory |
| `account_status` | accountEnabled / suspended, archived | directory |
| `department` | department / organizations[].department | directory |
| `job_title` | jobTitle / organizations[].title | directory |
| `location` | officeLocation, city, country / locations | directory |
| `manager_external_id` | manager/directReports / relations | directory (opcional) |
| `group_memberships` | Entra groups / Google Groups | directory |
| `org_unit_path` | orgUnitPath (Google) | hint only |
| `role_in_faberloom` | — | **local** |
| `sharing_flags` | — | **local** |
| `user_preferences` | — | **local** |

**NO se sincronizan en v1:** recovery email/phone, fotos, teléfonos personales, aliases secundarios, custom attributes abiertos.

### 1.4 State machine del usuario

Estados: `invited` · `active_local` · `active_synced` · `suspended` · `deprovisioned` · `merged_pending` · `merged` · `orphaned` · `deleted_soft`.

Eventos gatillo: `invite_sent` · `invite_accepted` · `oidc_login_linked` · `csv_imported` · `directory_sync_upserted` · `directory_disabled` · `admin_suspended` · `merge_requested` · `merge_confirmed` · `merge_reverted` · `directory_unreachable` · `relinked` · `soft_deleted`.

### 1.5 Precedencia manual vs synced

| Campo | Gana | Regla |
|---|---|---|
| Existencia del usuario vinculado | directory | Si desaparece del directory → `orphaned` o `deprovisioned` |
| Email primario | directory | Salvo cuenta local no vinculada |
| Nombre / depto / cargo / location | directory | Override local solo en UI, no persiste sobre sync |
| Rol en FaberLoom | local | Nunca heredado 1:1 desde groups / OUs |
| Permisos de knowledge | local | No reflejar jerarquía como permiso efectivo |
| Preferencias personales | local | Siempre |
| Credenciales de canal | local | Siempre |
| Flags de sensibilidad / sharing | local | Siempre |

### 1.6 Merge manual → synced

1. Intento match por `primary_email`
2. Si hay match, crear `merged_pending`
3. Mostrar diff de campos
4. Confirmación explícita del admin
5. Mantener `merge_event` reversible por 30 días
6. Persistir vínculo por `external_user_id`, no por email

### 1.7 Offboarding

Cuando el usuario sale:
- `user-private knowledge` → read-locked, no se comparte auto
- `candidate learnings` → cola de revisión del admin
- Credenciales personales → revocadas o `disconnected`
- Firma / tono personal → NO se promueven
- Ownership de drafts y audit trail → se conserva
- Contenido reusable → solo sale por promote-up explícito
- Retention post-deprovision → 90 días soft-delete antes de hard-purge (override por política del workspace según LGPD/LFPDPPP)

### 1.8 ERD mínimo

```
user_account (id PK, org_id, email, status, created_at)
  UNIQUE (org_id, email)
  INDEX (org_id, status)

user_sync_state (id PK, user_id FK→user_account, provider, external_user_id, last_sync_at)
  UNIQUE (provider, external_user_id)
  INDEX (user_id)

membership (id PK, user_id FK, org_id, team_key, role_in_faberloom)
  UNIQUE (org_id, user_id)
  INDEX (org_id, team_key)

override_flags (id PK, user_id FK, key, value)
  UNIQUE (user_id, key)

merge_event (id PK, user_id, target_sync_state_id, created_at, reverted_at)
  INDEX (user_id, created_at)

group_link (id PK, org_id, provider, provider_group_id, name)
  UNIQUE (provider, provider_group_id)

group_membership (id PK, group_link_id FK, user_id FK)
  UNIQUE (group_link_id, user_id)

emergency_access_account (id PK, org_id, is_active, created_at)
  INDEX (org_id, is_active)
```

### 1.9 RLS Supabase sin policy engine externo

**v1: Postgres RLS nativo.** Tres reglas:
1. Tablas flatten: `membership`, `group_membership`, `content_acl`
2. Helper functions SQL chicas y estables
3. Políticas por tabla, no combinaciones exóticas scope × rol × feature × source
4. Envolver `auth.uid()` / `auth.jwt()` en `select` para que el planner cachee por statement
5. Indexar columnas usadas por RLS

**Umbral de pivote a OPA / Cedar** (migrar cuando se cumpla *cualquiera*):
- >30 políticas RLS distintas en una sola tabla
- p95 latencia retrieval > 300ms sostenido 7 días
- Formalización de 4+1 scope que multiplica combinatoria

### 1.10 Directory caído / tenant perdido

- 1 cuenta `Tenant Owner` break-glass por org, creada en onboarding, fuera de Entra / Google
- MFA fuerte + uso auditado
- Si OIDC falla: break-glass entra en modo "admin only" — ve config, exporta, desactiva sync, relinkea. NO usa esa vía para operación normal del agente
- FaberLoom plataforma mantiene sus propias cuentas de emergencia separadas del cliente

### 1.11 Targets de latencia (beta)

| Paso | Queries | p95 target |
|---|---|---|
| Resolver actor + memberships | 1 | 5-15 ms |
| Cargar overlays no vectoriales activos | 1 | 5-20 ms |
| Vector retrieval con ACL + top-k | 1 | 30-120 ms |
| Hydrate docs/examples | 1 | 10-40 ms |
| Write audit trace async | 0 síncrona | <10 ms |

**Worst case síncrono beta: 4 queries, 55-195 ms antes del LLM.**
**Worst case degradado (RLS con joins malos): 250-450 ms → gatilla alerta.**

Cache TTLs:
- `effective_membership_cache`: 5 min
- `overlay_manifest_cache`: 60 s
- `top-k retrieval cache`: 30-60 s por `(org, actor, skill, business_entity_id, query_hash)`
- NO cachear respuestas finales con user-private mezclado salvo scope exacto

---

## 2. Taxonomía de conocimiento

### 2.1 v1 beta: 4 niveles

1. `global` — FaberLoom base sealed
2. `org` — admin org sube
3. `dept` — admin depto sube o hereda
4. `user` — usuario autoría + sistema aprende (UserControlProfile)

### 2.2 Conocimiento por cliente / cuenta / oportunidad

**NO es 5º scope formal en v1.** Vive como metadata en `AgentMemory`:
- `scope_level = org | dept | user`
- `business_entity_type = account | opportunity | ticket | customer`
- `business_entity_id = nullable`
- `sharing_mode = private | dept_shared | org_shared`

### 2.3 Criterio de pivote a 4+1 (v1.5)

Formalizar 5º scope solo si en los primeros 3 design partners **≥20-25% del conocimiento útil** resulta ser "por cliente / cuenta / oportunidad".

### 2.4 Storage por tipo

| Tipo | Dónde vive | Indexado vectorial |
|---|---|---|
| Base sealed | `agent_spec_base` | parcial |
| Overlay manual org | `agent_spec_overlay_manual` | no todo |
| Overlay aprendido | `agent_spec_overlay_learned` | no todo |
| Contexto documental | `memory_document` + `memory_chunk` | sí |
| Gold samples | `memory_example` | sí, tag especial |
| User control prefs | `user_control_profile` | no |
| Business-context items | `memory_chunk` con `business_entity_*` | sí |

### 2.5 Migration path 4 → 4+1 (si se decide en v1.5)

Preparar desde v1 columnas nullable:
- `business_entity_type`
- `business_entity_id`

Si se formaliza en v1.5:
1. Backfill de tags existentes a tabla nueva `memory_scope_binding`
2. Dual-write por 1 sprint
3. Dual-read detrás de feature flag
4. Reindex incremental, no full reindex
5. Cutover cuando recall / ACL den igual

**Zero-downtime posible** si el binding existe como metadata desde v1.

---

## 3. Algoritmo de composición de overlays

```
1. Resolver actor = usuario + rol + memberships locales
2. Resolver effective_scope = global + org + dept(s) + user
3. Aplicar ACL = tenant filter + scope filter + sharing filter + (opcional) business_entity filter
4. Cargar guardrails no vectoriales:
     base sealed
     + org manual active
     + dept manual active
     + user control prefs
5. Recuperar contexto vectorial:
     top-k chunks por ACL
     rerank
     top examples/gold samples
6. Componer por tipo (tabla §4)
7. Generar draft
8. Escribir decision trace resumido (async)
```

---

## 4. Precedencia por tipo de conocimiento

| Tipo | Orden efectivo |
|---|---|
| Guardrail / legal / promesa mínima | `base sealed > org > dept > user` |
| Política comercial | `org > dept > user` |
| Formato local (moneda, IVA, idioma) | `dept > org > user > base` |
| Voz / saludo / firma | `user > dept > org > base` |
| Gold samples | `same-scope > parent-scope > global` |
| Retrieval ACL | intersección, no override |

---

## 5. P12 cross-skill operacionalizado

| Caso | ¿Auto? | ¿Review? |
|---|---|---|
| user → mismo user, skill impactado marcado | Sí | No |
| dept → mismo dept, skill impactado marcado | Sí | No |
| org → misma org, skill impactado marcado | Sí | No |
| user → otro user del mismo dept | No | Sí |
| dept MX → dept CR | No | Sí |
| dept → org | No | Sí |
| org → dept | Sí (si herencia manual activa) | No |

El checkbox de skill impactado sigue siendo la puerta. Lo que se cierra es el radio de auto-propagación — no se viola `private-by-default`.

### 5.1 Promote-up permitido vs prohibido

| Tipo | User→Dept | Dept→Org | Nota |
|---|---|---|---|
| Gold sample reusable | Sí | Sí | Con revisión humana |
| Patrón de objeción frecuente | Sí | Sí | Sanitización obligatoria |
| Formato de cotización | Sí | Sí | — |
| Tono personal / saludo | **No** | **No** | Queda en user |
| Firma | **No** | **No** | Configuración, no knowledge |
| Credenciales | **No** | **No** | Nunca |
| PII / secretos | **No** | **No** | Nunca |
| Aprendizaje atado a cliente puntual | No auto | No auto | Usar `business_entity_id` |

---

## 6. Matriz de governance (3 roles actuales)

| Permiso | Tenant Owner | Admin | Operator |
|---|---|---|---|
| Configurar identity mode | Sí | Sí | No |
| Conectar/desconectar directory | Sí | Sí | No |
| Invitar/suspender usuarios | Sí | Sí | No |
| Asignar `role_in_faberloom` | Sí | Sí | No |
| Crear/editar org knowledge | Sí | Sí | No |
| Crear/editar dept knowledge | Sí | Sí | Sí (solo su dept) |
| Crear/editar user-private | Sí (propio) | Sí (propio) | Sí (propio) |
| Leer user-private ajeno | No por default | No por default | No |
| Aprobar promote-up user→dept | Sí | Sí | No |
| Aprobar promote-up dept→org | Sí | Sí | No |
| Revocar knowledge compartido | Sí | Sí | No |
| Activar/desactivar cross-skill propagation | Sí | Sí | No |
| Ver audit log resumido | Sí | Sí | No |
| Ver audit log técnico | Sí | Sí | No |
| Exportar conocimiento org | Sí | Sí | No |
| Usar break-glass recovery | Sí | No | No |
| Rollback de sharing/promoción | Sí | Sí | No |
| Impersonación de soporte | Sí (time-bound) | Sí (time-bound) | No |

### 6.1 Permisos temporales / delegables

| Permiso | Otorga | Duración |
|---|---|---|
| `can_approve_promotion` | Tenant Owner | 7 días |
| `can_view_audit_technical` | Tenant Owner | 24 h |
| `support_impersonation` | Tenant Owner | 8 h |
| `can_manage_directory_sync` | Tenant Owner | 24 h |
| `can_rollback_sharing` | Tenant Owner | 24 h |

### 6.2 Controles anti-Admin-dios

- User-private access: denegado por default
- Impersonación: permiso temporal ≤8 h
- Lectura de conversaciones privadas: solo con motivo + log
- Export de user-private: prohibido
- Promote-up: requiere comentario de aprobación
- Rollback: siempre auditado

**`Knowledge Reviewer` NO es rol formal en v1.** Si hace falta, permiso granular `can_approve_promotion` sobre Admin.

### 6.3 Taxonomía de sensibilidad (ortogonal al scope)

- `public_internal` — visible dentro de la org sin restricción
- `restricted` — visible bajo ACL explícita
- `confidential` — visible solo a Tenant Owner + auditables
- `pii` — nunca auto-share, sanitización obligatoria pre-promote
- `channel_secret` — nunca compartido, vive en vault

---

## 7. Rollback versionado

**Regla: no borrar chunks promovidos, versionarlos.**

- `memory_chunk.status = active | superseded | revoked`
- `supersedes_chunk_id`
- `visibility_active = false` saca del retrieval
- Reindex incremental async
- `promotion_event` y `revocation_event` auditan lineage

### 7.1 TTL de revisión para learned overlays

**Default: 90 días** de reuse antes de marcar para revisión.

Justificación: ciclo típico de cotización B2B calzado seguridad (30-60 días lead→cierre + siguiente trimestre) cubre un ciclo completo de validación. 30 días es corto (patrón estacional se reinicia sin signal). 180 días es largo (diluye signal).

**Configurable por skill en rango 30-180:**
- Skills volátiles (campañas estacionales): 30 días
- Skills estables (compliance, fiscal): 180 días
- Skills de cotización B2B: 90 días (default)

### 7.2 Sanitización antes de promover

Pipeline obligatorio pre-promote-up:
1. Regex scan de PII (email, teléfono, CURP/RFC/CPF/CC)
2. Redacción de nombres propios no autorizados
3. Redacción de referencias a `business_entity_id` específicas si el target es scope superior
4. Quita secretos de canal (API keys, OAuth tokens embebidos)
5. Review humano obligatorio si confidence_score sanitizer < 0.95

---

## 8. Leakage tests obligatorios

**Suite `tests/leakage/` en pytest. Gate CI pre-release. Si falla, no hay merge a main.**

Casos mínimos v1:

1. Usuario org A jamás ve chunk org B
2. User-private no aparece a otro user de la misma org
3. Dept MX no recupera dept CO
4. Org-shared aparece a users autorizados
5. `business_entity_id` filtra correctamente
6. Promote-up revocado deja de salir en top-k
7. Fallback de admin no abre user-private
8. Cross-skill no salta de scope sin review
9. P12 cross-dept no hace auto-propagación (solo review)
10. `business_entity_id` con ACL distinta filtra correctamente aunque dept match

**Aprobación de excepciones:** Tenant Owner (Álvaro) explícito, documentado.
**Definition of Done** de cualquier PR que toque `ACL`, `RLS` o `memory_chunk`: "leakage suite green".

---

## 9. UI implicada

### 9.1 v1 beta — 2 pantallas imprescindibles

**Identity & Access Setup:**
- Modo identity (Local / OIDC / Directory read-only)
- Usuarios, estado, merge queue, break-glass

**Knowledge Registry:**
- Listado por scope (`global / org / dept / user`)
- Status (`candidate / active / archived / revoked`)
- Sharing
- Promote-up / rollback

### 9.2 v1.5 (post-beta)

- Promotion Queue
- Audit Log técnico profundo
- Overlay Resolver profundo
- Directory Mapping diff viewer
- Sandbox / preview antes de commit

### 9.3 Overlay Resolver — dónde vive

**Ambos, nivel distinto:**
- Agent Console → panel chico "¿Por qué salió así?"
- Admin Panel → vista profunda con precedence y fuentes

### 9.4 UX de permisos

**Progressive disclosure. NO matriz completa de 60+ celdas por default.**

Patrón:
1. Presets
2. Excepciones
3. Diff / preview
4. Audit trail

Matriz completa como vista avanzada, no home screen.

### 9.5 Time-to-first-value

**Target: 12 clicks (sin directory sync) / 17 clicks (con OIDC). ≤7 min onboarding guiado.**

| Paso | Clicks objetivo |
|---|---|
| Crear workspace / entrar | 1 |
| Elegir modo identity | 1 |
| Invitar usuarios o CSV | 2 |
| Crear primer agent | 2 |
| Subir 1 catálogo / 1 política | 2 |
| Marcar 1 skill impactado | 1 |
| Correr test prompt | 1 |
| Abrir primer draft | 1 |
| Confirmar source preview | 2 |

**Instrumentación:** cada paso = evento en PostHog (o equivalente open-source).
- Funnel `onboarding_completion` con target ≥40% llega a "confirmar source preview" en primera sesión
- Abandono >50% en un paso = bug UX prioridad P0
- Reporte semanal al equipo

### 9.6 Rollback UX

**≤3 clicks:**
1. Abrir item
2. "Revert sharing" o "Revoke promotion"
3. Confirmar

Señal visual post-rollback: badge `Revoked` + timestamp + actor + preview "ya no participa en retrieval".

### 9.7 Audit log — qué ve quién

**Negocio / CEO:**
- Quién compartió qué
- Cuándo
- Desde qué scope a cuál
- Rollback sí/no
- Impacto estimado en drafts

**Soporte interno:**
- query_id
- policy path
- top-k ids
- ACL evaluation
- merge ids / sync ids

### 9.8 Verbos UI para P11/P12

- Guardar como contexto
- Convertir en patrón
- Promover
- Propagar a skills marcadas (discreto)

---

## 10. Baseline regulatorio LATAM

### 10.1 Países v1

| País | Regulación | Requisito técnico | Decisión producto v1 |
|---|---|---|---|
| Brasil | LGPD + ANPD activa 2025-2027 | Minimización, base legal, separación datos personales/sensibles, trazabilidad | Opt-in para conversaciones privadas en learning; redacción/sanitización pre-promote; export/delete por org |
| México | LFPDPPP vigente 2025 para particulares | Aviso privacidad, consentimiento según categoría, ARCO | Centro de privacidad básico: export, delete intake, retention visible, registro finalidades |
| Colombia | Ley 1581 + SIC | Distinguir dato personal de dato corporativo; autorización cuando identifica persona natural | No asumir correo corporativo = libre; tratar nombre+correo+historial+estilo como dato personal si identifica persona |

**Perú** (Ley 29733 + reglamento 2025) al pipeline cercano — sube al top 3 si Perú entra temprano.

### 10.2 Cross-LATAM v1

- DPA estándar
- Retention policy simple por workspace
- Audit log de sharing / promotions
- Toggle explícito de conversation-learning

### 10.3 Consentimiento vs contrato / interés legítimo

- Artefactos internos operativos: contrato / interés legítimo alcanza
- Conversaciones privadas del usuario con agentes: **opt-in obligatorio**
- PII sensible / salud / biométricos / secretos: **fuera de auto-share**
- Prospecting comercial: cuidado si data viene de conversación y no de proceso contractual

### 10.4 Mínimo legal-operativo para beta

1. DPA estándar
2. Retention policy por workspace
3. Export/delete a nivel org
4. Audit log de sharing/promotions
5. Inventario básico de fuentes
6. Base legal/documentación interna para learning desde conversaciones
7. Incident/security contact (email + Slack)

### 10.5 Workarounds

**Tolerables 90 días:**
- Export/delete semi-manual por soporte (con SLA documentado)
- Country pack legal simplificado
- Directory sync solo read-only

**NO tolerables (bloquean launch):**
- Sin rollback de knowledge sharing
- Sin separación knowledge / credenciales
- Sin toggle explícito para learning desde conversaciones
- Sin RLS y sin filtros tenant / scope

### 10.6 Export format

- **Conocimiento textual:** Markdown (portable, humano, compatible Notion/Obsidian)
- **Metadata:** JSON (scope, ACL, precedencia, timestamps)
- **Embeddings:** NO exportados (derivados regenerables, atan al modelo)
- **Delivery:** endpoint async `/api/export/org/{org_id}` → job → email con link temporal (TTL 72h)

---

## 11. Beta slice 6-8 semanas

**Ventana:** 2026-04-20 → 2026-06-12

### Semana 1-2 — Owner: Product + Backend

- Modelo 4 niveles fijo
- `business_entity_id` como metadata en `AgentMemory`
- `private-by-default`
- Tablas `user_account`, `user_sync_state`, `membership`, `override_flags`, `merge_event`, `group_link`, `group_membership`, `emergency_access_account`
- Solo 3 roles actuales

### Semana 3-4 — Owner: Backend + Frontend

- Local + OIDC login
- Invite / suspend / merge queue
- Knowledge Registry v1
- Promote-up user→dept / dept→org con sanitización pre-promote
- Rollback de sharing/promoción
- Audit log resumido

### Semana 5-6 — Owner: Backend

- Retrieval con ACL + scope + `business_entity_id`
- P12 acotado a mismo scope + checkbox
- Break-glass local por org
- Suite `tests/leakage/` 10 casos, CI gate
- Cache `effective_membership` + `overlay_manifest` + `top-k retrieval`

### Semana 7-8 — Owner: Frontend + PM

- Panel "¿Por qué salió así?"
- Onboarding guiado (embudo 9 pasos instrumentado)
- Export org-level básico (Markdown + JSON)
- Privacy toggles para conversation-learning
- Métricas visibles en Admin: synced users / licensed seats / active seats 30d

### NO shippear en v1

- SCIM full
- Roles nuevos formales (`Dept Manager`, `Knowledge Reviewer`)
- Quinto scope formal
- OPA / Cedar
- Auto-share intra-dept por default
- Sandbox / policy simulator avanzado
- Heredar permisos efectivos desde OUs / groups

### v1.5 (post-beta, condicionado a data de 3 design partners)

- Directory sync read-only más completo
- Preview antes de promote / share
- Export más fino
- Mejores diffs de merge
- Object scope formal si ≥20-25% del conocimiento útil es por cliente

### v2.0

- SCIM full
- Gobernanza avanzada
- Simulador de precedencias
- Lineage / audit técnico profundo
- Posible 4+1 formal

---

## 12. Decisiones post-auditor (gaps residuales cerrados por arquitecto)

| # | Gap | Decisión | Justificación |
|---|---|---|---|
| 1 | TTL learned overlays | **90 días default**, configurable 30-180 por skill | Ciclo B2B calzado 30-60d + cierre trimestre; 30d corto, 180d diluye |
| 2 | Pivote RLS → policy engine | OR: >30 políticas/tabla · p95 >300ms 7d sostenidos · 4+1 formal | Umbral numérico explícito, evita "ya veremos" |
| 3 | Leakage tests automation | Pytest suite, CI gate pre-release, DoD obligatorio en PRs de ACL/RLS/memory_chunk | P13 inquebrantable = suite, no buena fe |
| 4 | Seat counting billing | **Active 30d** (no licensed). Transparencia: mostrar los 3 números | PYME LATAM sensible a cobrar gente que no usa; detalle completo en ronda billing |
| 5 | TTFV instrumentation | Embudo 9 pasos en PostHog, target ≥40% completion, >50% abandono = P0 | Sin analytics, 12 clicks es aspiracional |
| 6 | Export format | Markdown + JSON metadata, NO embeddings | Portable humano; embeddings regenerables y atan al modelo |
| 7 | SOC 2 no-regrets | 7 controles día 1 (ver §12.1) | No certificar ya, no pintarnos en esquina |

### 12.1 SOC 2 / ISO 27001 no-regrets (v1 no certifica, pero prepara)

1. **Audit log estructurado:** `actor, action, resource, before_state, after_state, timestamp` — obligatorio en sharing / promotion / role change
2. **Separación lógica `env: dev | staging | prod`** en todos los datos
3. **Secrets en vault** (Supabase Vault) desde día 1 — NUNCA env vars
4. **Change management:** merge a main requiere 1 reviewer + CI green
5. **Data retention policy** documentada por workspace (no hardcoded)
6. **Incident response:** email + Slack channel dedicado
7. **Modelo de auth preparado para SSO / MFA platform-wide** (activación v1.5+)

---

## 13. Rondas futuras pendientes

**Ronda 3 — Billing & Cost Control (prioritaria, próxima).**
Definir pricing concreto, tier gates exactos, metered vs flat por skill, LATAM fiscal (CFDI MX, FE CR, DIAN CO, NF-e BR), free trial, grandfathering, churn protection, connection al Autonomy Ladder (más autonomía = más valor = más caro).

**Ronda 4 — Connectors & Integrations.**
Taxonomía de conectores soportados v1 (Email, Calendar, WhatsApp Business, Slack, Drive / SharePoint, CRM, ERP, Amazon SP-API, webhook custom), OAuth vs API key vs service account, marketplace vs custom, scoping por conector (knowledge_user vs knowledge_org), cost attribution (acopla con ronda 3), ciclo de vida (install / revoke / orphan), draft-first vs connectors bidireccionales, data residency post-revoke.

**Ronda 5 (opcional) — Compliance formal.**
SOC 2 / ISO 27001 preparation timeline, auditor externo, tooling (Drata / Vanta), gap assessment.

---

## 14. Churn signals detectables desde Admin Panel

Tres comportamientos de administración que predicen cancelación:

1. `0 promotions` en 30 días → adopción estancada, no están capturando valor
2. Connector configurado con errores sin remediar por 7 días → fricción no resuelta
3. Admin nunca abrió Knowledge Registry / audit log post-onboarding → no están gobernando

**Acción Customer Success:** nudge in-app al día 14, llamada CSM al día 30, in-product tutorial al día 45 si persiste.

---

## 15. Changelog

- **v1.0 (2026-04-19)** — Primera versión. Consolida 2 rondas de auditoría externa (v1 + v2) + decisiones arquitecto sobre 7 gaps residuales. Status: DRAFT. Próximo paso: 