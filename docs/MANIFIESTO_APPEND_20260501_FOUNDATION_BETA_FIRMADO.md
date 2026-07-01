# MANIFIESTO_APPEND — Foundation Beta firmada

id: MANIFIESTO_APPEND_20260501_FOUNDATION_BETA_FIRMADO
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: MANIFIESTO_APPEND
stamp: VIGENTE — 2026-05-01
aprobador: CEO (Alvaro)
owner: CEO
fecha_evento: 2026-05-01
fuente: Sesión Cowork 2026-05-01 — iteración de planeación FaberLoom Foundation Beta
aplica_a: [FaberLoom]
relacionado: PLB_FB_FOUNDATION_BETA v1.0 · IDX_FB_FOUNDATION_BETA v1.0 · PLB_FB_KICKOFF_PROMPT v1.0

---

## Resumen del evento

Sesión Cowork 2026-05-01 produjo el plan ejecutable de FaberLoom Foundation Beta a través de 7 iteraciones (v1.0 → v1.3.1-FIRMADO). El plan fue revisado de forma cruzada por CEO + ChatGPT antes de firma final. Tres artefactos canónicos quedan promovidos al repo bajo `docs/faberloom/`:

1. `PLB_FB_FOUNDATION_BETA_v1.md` (plan ejecutable 13 sprints)
2. `IDX_FB_FOUNDATION_BETA.md` (índice maestro del proyecto)
3. `PLB_FB_KICKOFF_PROMPT_v1.md` (prompt autocontenido para nuevas sesiones)

Cuatro artefactos de iteración previos quedan archivados en `audit/iteraciones_foundation_beta/` para auditoría.

---

## Trazabilidad de iteraciones

| Versión | Fecha | Hito | Producido por | Status final |
|---|---|---|---|---|
| v1.0 | 2026-05-01 | Plan inicial 8 sprints — pre-canon `docs/faberloom/` | Cowork sesión 1 | DEPRECATED — archivado |
| v1.1 | 2026-05-01 | Patch tras leer 6 specs canon `docs/faberloom/` (auth, topology, seed, evidence bundle, exception taxonomy, replay set) | Cowork tras review CEO | DEPRECATED — archivado |
| v1.2 | 2026-05-01 | Consolidado autocontenido — TIER 1 a 12 ítems firmados — Hostinger KVM 8 confirmado | Cowork tras feedback CEO | DEPRECATED — archivado |
| v1.2.1 | 2026-05-01 | Microcorrecciones editoriales (fallback Telegram out, schema 11 tablas, replay_set no bloquea S1) | Cowork tras review CEO | DEPRECATED — incluido en v1.2 archivado |
| v1.3 | 2026-05-01 | Re-scope CEO: factories minimal + multi-usuario + multi-email + Voice Profile + resiliencia C, 13 sem | Cowork tras input CEO | DEPRECATED — archivado |
| v1.3.1 | 2026-05-01 | Renombre a Foundation Beta + 14 límites duros Skill Factory + Sprint 1A/1B + correcciones | Cowork tras review cruzada CEO+ChatGPT | RC pre-firma |
| **v1.3.1-FIRMADO** | **2026-05-01** | **CEO firma + 3 condiciones operativas kickoff (worker queue congelado S1A, Resend <5%, restore test pre-S10)** | Cierre sesión | **FIRMADO — promovido a canon** |

---

## Cambios al árbol de archivos

### Promovidos a canon (`docs/faberloom/`)

| Archivo nuevo | Tipo | Contenido |
|---|---|---|
| `docs/faberloom/PLB_FB_FOUNDATION_BETA_v1.md` | PLB | Plan ejecutable 13 sprints — id `PLB_FB_FOUNDATION_BETA` v1.0 status FIRMADO. Plan label interno `v1.3.1-FIRMADO` |
| `docs/faberloom/IDX_FB_FOUNDATION_BETA.md` | IDX | Índice maestro del proyecto — id `IDX_FB_FOUNDATION_BETA` v1.0 status VIGENTE |
| `docs/faberloom/PLB_FB_KICKOFF_PROMPT_v1.md` | PLB | Prompt autocontenido para sesión nueva — id `PLB_FB_KICKOFF_PROMPT` v1.0 status VIGENTE |

### Archivados (`audit/iteraciones_foundation_beta/`)

| Archivo archivado | Versión |
|---|---|
| `PLAN_FABERLOOM_BETA_INICIAL_8_SPRINTS_v1.md` | v1.0 |
| `PLAN_FABERLOOM_BETA_INICIAL_PATCH_v1.0_to_v1.1.md` | v1.1 patch |
| `PLAN_FABERLOOM_BETA_INICIAL_v1.2.md` | v1.2 + v1.2.1 |
| `PLAN_FABERLOOM_BETA_INICIAL_v1.3.md` | v1.3 |

### Working copies en raíz workspace (mirror funcional)

Mantenidos como duplicados de las versiones canon para acceso rápido CEO durante operación día a día:

- `PLAN_FABERLOOM_FOUNDATION_BETA_v1.3.1.md`
- `INDEX_FABERLOOM_FOUNDATION_BETA.md`
- `PROMPT_KICKOFF_FOUNDATION_BETA.md`

**Verdad canónica vive en `docs/faberloom/`.** Si hay divergencia, gana el archivo canónico.

---

## Decisiones críticas firmadas (v1.3.1)

### TIER 1 — 17 ítems inquebrantables

Documentados en `PLB_FB_FOUNDATION_BETA_v1.md` §"Tiers de cumplimiento canon".

- 14 límites duros Skill Factory (TIER 1 #16)
- Regla single-agent por task (TIER 1 #15)
- Resiliencia camino C completo (TIER 1 #17)
- Multi-email nativo Gmail OAuth + IMAP/SMTP custom (TIER 1 #13)
- Voice Profile completo (TIER 1 #14)
- 5 roles tenant (TIER 1 #7)
- HITL absoluto (TIER 1 #2)
- Anthropic-only (TIER 1 #10)
- Wedge único safety footwear (clarificado en TIER 1 #11)

### Pendiente firma post-v1.3.1 (acordado implícitamente)

Iteración post-firma identificó tres ajustes acordados que se patcharán a v1.3.2 (no firmado aún):

1. **TIER 1 #18:** pgvector + embedding local self-hosted (`multilingual-e5-base`) — habilita reducción 30-50% tokens IA + caching semántico, mantiene Anthropic-only
2. **Library Skills System E1:** 10 skills system precargadas (origin='system', inmutables, clonables) + 2 skills MWT custom precargadas en tenant MWT
3. **Aclaración formal:** ecosistema skills.sh (188 skills catalogadas por Kimi) queda como referencia, no instalación E1

### 3 condiciones operativas de kickoff (Sección 5.B del plan)

| # | Condición |
|---|---|
| A | Worker queue elegido en Sprint 1A — congelado para E1 |
| B | Resend con límite <5% outbound mensual + DPA cubierto antes S10 o limitar a mensajes no sensibles |
| C | Restore test demostrado antes de S10 (apertura beta con datos reales) |

---

## Restricciones inquebrantables (no reabrir)

Lista canónica documentada en `PLB_FB_FOUNDATION_BETA_v1.md` §7:

- Hosting Hostinger KVM 8
- Stack canónico (FastAPI + Next.js + Postgres + Redis + LiteLLM + Anthropic)
- Wedge safety footwear B2B
- Anthropic-only para LLM
- HITL absoluto
- Single-agent por task
- No DMS
- No AI_GOV runtime
- No sub-agentes
- No marketplace cross-tenant
- No skills compartidas entre tenants
- No tools externas en skills
- No code execution en skills
- No HTTP externo en runtime de skills
- No cross-tenant access desde engine

---

## Próximos pasos

### Inmediato (CEO esta semana)

1. Confirmar 3 amigos B2B con incentivo + commitment verbal
2. Iniciar trámite WhatsApp Business MWT con Meta
3. Iniciar trámite Google OAuth approval para FaberLoom
4. Iniciar redacción DPA legal
5. Pre-curar `client_map.xlsx` MWT (entrega lunes S4)

### Próxima sesión Cowork (pendiente)

1. Producir `PLB_FB_FOUNDATION_BETA_v1.1.md` patch con +pgvector embedding local +12 skills system Library
2. Producir `LIBRARY_FB_SKILLS_SYSTEM_v1.md` con SkillSpec completo de las 12 skills
3. Producir `RECOPILAR_FB_SKILLS_FUTURAS_v1.md` con 10 skills gap crítico + preguntas

### Implementación (cuando arranque Sprint 1A)

Ver `PLB_FB_FOUNDATION_BETA_v1.md` §3 para 13 sprints detallados.

---

## Anexos relacionados (en `docs/anexos/`)

- `mockups/` — 6 archivos HTML mockups de la mesa de control + skin picker interactivo
- `kimi_skills/` — INVENTARIO de 188 skills del ecosistema skills.sh + 12 archivos de research dimensiones (D1-D12)

---

Changelog:
- v1.0 (2026-05-01): Creación. Indexa la promoción a canon de la sesión Cowork 2026-05-01 que produjo `PLB_FB_FOUNDATION_BETA v1.0` (status FIRMADO, plan label v1.3.1-FIRMADO) + `IDX_FB_FOUNDATION_BETA v1.0` + `PLB_FB_KICKOFF_PROMPT v1.0`. Documenta archivado de 4 versiones previas en `audit/iteraciones_foundation_beta/`. Lista los pendientes para próxima sesión y compromisos CEO inmediatos.
