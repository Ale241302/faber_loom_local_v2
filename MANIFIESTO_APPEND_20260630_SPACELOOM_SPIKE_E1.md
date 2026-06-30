---
id: MANIFIESTO_APPEND_20260630_SPACELOOM_SPIKE_E1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: MANIFIESTO_APPEND
stamp: VIGENTE — 2026-06-30
aprobador: CEO
aplica_a: [FaberLoom, SpaceLoom, MWT]
relacionado:
  - PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md
  - PLB_FB_FOUNDATION_BETA_v1.md
  - IDX_FB_FOUNDATION_BETA.md
  - IDX_GOBERNANZA.md (v1.6)
  - ENT_GOB_DECISIONES.md (v2.3)
  - ENT_GOB_PENDIENTES.md (v16.0)
  - docs/MANIFIESTO_APPEND_20260501_FOUNDATION_BETA_FIRMADO.md
supersede: n/a
run_id: SPIKE-E1-2026-06-30
engine: fugu
---

# MANIFIESTO_APPEND_20260630_SPACELOOM_SPIKE_E1

## 1. Propósito de este append

Este documento registra un **artefacto de software construido fuera del track canónico** de FaberLoom Foundation Beta. Su única función es:

1. Dejar constancia de qué es, por qué existe y qué validó.
2. Evitar que el spike se confunda con el producto canónico o con SpaceLoom como pilar de marca.
3. Fijar una fecha de sunset y un criterio de archivado.
4. Extraer los aprendizajes validados y portarlos a los specs de Foundation Beta.

**No modifica los planes firmados.** No altera `PLB_FB_FOUNDATION_BETA_v1.md` ni `IDX_FB_FOUNDATION_BETA.md`. No autoriza merge de código SQLite/pywebview al canon.

---

## 2. Qué es el spike

| Atributo | Valor |
|---|---|
| Nombre registrado | **SpaceLoom Spike E1** |
| Repo de trabajo | `Ale241302/faber_loom_local_v2` (pendiente de renombrar a `faberloom-spike-e1`) |
| Path en VPS | `/opt/faber_loom` (pendiente de renombrar a `/opt/spaceloom-spike`) |
| Dominio de acceso | `app.faberloom.ai` (pendiente de migrar a `spike.faberloom.ai`) |
| Plan base | `PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md` |
| Ejecutor | Alejandro (con asistencia de agentes Kimi / fugu / Codex) |
| Fecha de inicio | 2026-06 (aproximado) |
| Fecha de cierre técnico parcial | 2026-06-30 |
| Estado funcional | SL0–SL4 cerrados formalmente; SL5 diferido; 221 tests verdes |

### Alcance cerrado (SL0–SL4)

- SL0: esqueleto FastAPI + SQLite + seed de workspaces.
- SL1a: router multi-proveedor con allowlist, budget cap, fallback y costo visible.
- SL1b: chat draft-first contra contexto del workspace.
- SL2a/b/c: workspaces + KB (MD/TXT/PDF/Excel/CSV) con citas a fuente.
- SL3a: skills / routines / agents invocables por `@nombre` y right-rail.
- SL3b/c: HITL básico (aprobar/editar/rechazar) + captura de `edit_pct`.
- SL3.5: sellado por workspace + test de fuga cross-workspace = 0.
- SL4: empaque ejecutable vía PyInstaller + pywebview (Windows).
- Login web JWT para dos usuarios admin compartiendo el mismo workspace y providers.

### Alcance explícitamente NO cerrado

- **SL5 (correo):** diferido. No hay connector multi-cuenta, no hay envío real, no existe `email_connector_enabled` en el código al momento de este append. Se documenta como falso/diferido para evitar inconsistencia con el ledger.
- Multi-tenant real: el `tenant_id` existe como campo latente, pero no hay RLS ni aislamiento a nivel de tenant.
- Autenticación robusta: JWT simple con secret en `.env`; no es OIDC ni cumple con el canon de Foundation Beta.
- Next.js / Mesa de Control: el frontend es React estático servido por FastAPI.

---

## 3. Qué NO es

Para evitar contaminación de marca y arquitectura:

- **No es "FaberLoom Etapa 1".** El track de ejecución canónico sigue siendo FaberLoom Foundation Beta v1.3.1 firmado.
- **No es "SpaceLoom" como producto.** SpaceLoom permanece como pilar de marca (home cognitivo / canvas) dentro de Foundation Beta.
- **No es una versión alternativa de Foundation Beta.** Es un spike throwaway sobre stack distinto (SQLite/pywebview/.exe).
- **No es canonizable tal como está.** No cumple los 17 ítems TIER 1 de Foundation Beta (RLS Postgres, HITL absoluto auditado, 5 roles tenant, evidence bundle, etc.).

---

## 4. Stack técnico del spike

| Capa | Tecnología | Nota |
|---|---|---|
| Backend | Python 3.13 + FastAPI + Pydantic v2 | Prototipo funcional, no productivo |
| DB | SQLite + sqlcipher3 + FTS5 | Campo `tenant_id` latente, sin RLS real |
| Frontend | React 18 UMD + Babel standalone + CSS custom | Reemplazable por Next.js 15 en canon |
| Desktop | pywebview + PyInstaller | Empaque Windows; sin firma de código |
| Auth | JWT PyJWT + `FABERLOOM_USERS` env var | Bypass local cuando no hay usuarios configurados |
| LLM | BYOK: OpenAI / Kimi / Anthropic / Google / Ollama | Keys gestionadas en `.env` y `providers.json` |
| Email | N/A | SL5 diferido |
| Deploy | Docker Compose en VPS (Ubuntu 24.04) + nginx | Configuración web del spike, no de producción |

---

## 5. Aprendizajes validados a portar al canon

El valor del spike no está en su código, sino en las decisiones de producto y arquitectura que demostró ser implementables. Se extraen y se incorporan a los specs de Foundation Beta:

| # | Aprendizaje | Spec destino | Acción |
|---|---|---|---|
| 1 | Umbral `edit_pct ≤ 0.2` como criterio de promoción gold | `SPEC_FB_FUNC_M13_DRAFT_HITL_v1` | Añadir gate numérico |
| 2 | Promoción shadow → active solo por Owner/Admin | `SPEC_FB_FUNC_M09_RBAC_v1` + `SPEC_FB_FUNC_M13_DRAFT_HITL_v1` | Documentar permiso |
| 3 | `confirmation_token + idempotency_key` obligatorios para envíos externos | `SPEC_FB_FUNC_M15_OUTBOX_STREAMS_v1` | Añadir a contrato de outbox |
| 4 | Provider allowlist / budget cap / fallback como requisitos del router mínimo | `SPEC_FB_ROUTING_PRESETS_v1` | Reforzar requisitos E1 |
| 5 | Workspace sealing: test de fuga cross-workspace = 0 antes de cargar datos de múltiples clientes | `SPEC_FB_FUNC_M16_TENANT_ISOLATION_v1` | Añadir como DoD de aislamiento |
| 6 | Campos de versión (`routine_version`, `skill_version`, `source_version`) deben copiarse al ejecutar | `SCH_FB_SKILL_MANIFEST_v2` + `SPEC_FB_FUNC_M14_OUTCOME_LEDGER_v1` | Asegurar trazabilidad reproducible |
| 7 | HITL absoluto es implementable: cero envío sin aprobación explícita | `PLB_FB_FOUNDATION_BETA_v1.md` TIER 1 #2 | Refuerzo de principio |

---

## 6. Estado de SL5 (correo)

**Decisión:** SL5 se mantiene **diferido** en el spike.

**Razón:** El correo no es necesario para el dogfood interno actual (se puede copiar/pegar a mano), y construir un connector IMAP/SMTP real requiere credenciales rotadas, manejo de injection y envío HITL — todo eso pertenece al track canónico de Foundation Beta, no a este spike.

**Corrección del ledger:** El flag `email_connector_enabled=false` no existe en el código al 2026-06-30. Se resuelve de una de dos formas:

- **Opción A (recomendada):** Agregar el flag explícito en el código con valor `false` y documentar que SL5 está diferido.
- **Opción B:** Corregir el ledger donde se mencione el flag como existente, aclarando que es un requisito futuro, no una feature presente.

La opción A se aplicará salvo indicación en contrario.

---

## 7. Criterio de sunset / archivado

El spike tiene vida útil mientras Foundation Beta no entregue un reemplazo funcional equivalente para el dogfood interno de MWT. El criterio de sunset es:

> **El spike se archiva cuando Foundation Beta complete el SPINE serial (M16–M07) y entregue un tenant MWT operativo con chat + KB + HITL básico usable por Alvaro.**

A partir de ese momento:

1. Se congela el repo del spike.
2. Se redirige `spike.faberloom.ai` a una landing de "sunset" o se apaga.
3. Se migran los datos de MWT del spike al tenant canónico (manualmente, no automatizado).
4. Se archiva este MANIFIESTO_APPEND en `audit/spikes/`.

---

## 8. Acciones derivadas

| # | Acción | Responsable | Estado |
|---|---|---|---|
| 1 | Renombrar repo `faber_loom_local_v2` → `faberloom-spike-e1` | Alejandro | Pendiente |
| 2 | Renombrar path VPS `/opt/faber_loom` → `/opt/spaceloom-spike` | Alejandro | Pendiente |
| 3 | Migrar dominio `app.faberloom.ai` → `spike.faberloom.ai` | Alejandro | Pendiente |
| 4 | Agregar `email_connector_enabled=false` en el código o corregir ledger | Alejandro | Pendiente |
| 5 | Crear `SPEC_FB_SPIKE_E1_LESSONS_LEARNED_v1.md` con los 7 aprendizajes | Alejandro / fugu | Pendiente |
| 6 | Portar aprendizajes a los specs canónicos de Foundation Beta | Alejandro | Pendiente |
| 7 | Notificar a Alvaro que el login actual es spike interno, no producto | Alejandro | Pendiente |
| 8 | Retomar ejecución de Foundation Beta SPINE serial | Alejandro | Bloqueado por E0/STACK-01 hasta confirmación CEO |

---

## 9. Relación con la decisión E0 / STACK-01

Este append resuelve STACK-01 de la siguiente manera:

- **STACK-01:** ¿el spike desktop se archiva y Alejandro ejecuta Foundation Beta canónico en Postgres, o se reconcilian los dos tracks?
- **Respuesta:** Se archiva **eventualmente**, pero se mantiene como dogfood interno mientras Foundation Beta no tenga reemplazo funcional. No se reconcilian stacks. El track de ejecución único y canónico es Foundation Beta v1.3.1.

La decisión CEO pendiente sigue siendo **confirmar el calendario y recursos de Foundation Beta** (8–10 semanas dogfood recortado vs 14–18 semanas distribuible), pero ya no está bloqueada por la existencia del spike.

---

## 10. Firmas

| Rol | Nombre | Fecha |
|---|---|---|
| Ejecutor técnico | Alejandro | 2026-06-30 |
| Aprobador | CEO (Alvaro) | Pendiente confirmación |

---

## Changelog

- **v1.0 (2026-06-30):** Creación. Registro del spike, decisión (A) matizada como dogfood interno, aprendizajes a portar, SL5 diferido, criterio de sunset y acciones derivadas.
