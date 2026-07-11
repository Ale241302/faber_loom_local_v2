# PLAN_DESARROLLO_FABERLOOM_ETAPA4_v2 — El Agente Vivo

**id:** PLAN_FB_ETAPA4
**version:** 2.0.0
**status:** VIGENTE (reemplaza v1.0 y el ADDENDUM v1.1 — todo lo útil de ambos está integrado aquí)
**visibility:** interna
**domain:** PLATAFORMA
**Fecha:** 2026-07-10
**Autor:** Arquitecto Ejecutor (Claude), por delegación del CEO
**Verificado contra:** código real (`app/src/`, `app/static/`), `AGENTS.md`, y las specs de `docs/` y `docs/faberloom/` citadas hito por hito.
**Base de partida:** E3 cerrada (commit `8466b07`, 619 passed / 12 skipped / 0 failed, SCHEMA_VERSION=41).

---

## §0. Decisiones de arquitectura (tomadas)

| # | Decisión | Detalle |
|---|---|---|
| DA-1 | El Agente Vivo es la columna vertebral de E4 | Signup público relegado a E4-7, condicionado al gate comercial (soak E3-6) |
| DA-2 | Canal: shell web primero, WhatsApp bidireccional al final | El webhook entrante ya existe (`connectors/whatsapp_inbound.py`); el saliente es E4-6 |
| DA-3 | Nombre técnico `living_agent`; nombre visible = display name de `entity_identity` del tenant (default "Faber") | El agente ES la entidad de E3-3; no se inventa identidad paralela |
| DA-4 | Flag `routing.mode = manual \| shadow \| natural` (default `manual`) | El modo "auto" existente ≡ `natural`; `shadow` planifica sin ejecutar; promoción manual gobernada por el Autonomy Control Engine (§E4-2.6) |
| DA-5 | Briefs solo en frío (ciclo ambiental E2-5); nunca cómputo en caliente | Stale → se sirve con advertencia + se encola refresh |
| DA-6 | Guardrails E3 completos + Regla Sagrada del Autonomy Ladder | Correo externo, WhatsApp, transacción financiera → **siempre draft-first**, en cualquier nivel de autonomía (SPEC_AGENT_ARCHITECTURE_ALE §5) |
| DA-7 | El Autonomy Ladder (0-4) gobierna al planner | `shadow` = Nivel 0; `natural` opera como máximo en Nivel 2 (EJECUTA_INTERNO); nada de Nivel 3+ en E4 |
| DA-8 | Toda enmienda a una spec de la KB se versiona, nunca se viola en silencio | E4 enmienda: SPEC_E2_5 (v1.1), SPEC_FB_WORKSPACE (v2), ENT_PLAT_LLM_ROUTING (append F1-shadow) |

**Reglas:** R1-R10 de E3 siguen vigentes. Nuevas: **R11** — toda decisión del planner (shadow o natural) queda logueada con plan completo, candidatos, costos estimados y razón; **R12** — los briefs son derivados regenerables (borrarlos no pierde información de negocio); **R13** — toda tabla nueva lleva los **campos latentes** de `AGENTS.md`: `tenant_id`, `actor_id`, `actor_role_at_decision`, `routine_version`, `skill_version`, `schema_version`, `source_version`, `approved_by`, más policy RLS en `app/scripts/postgres_rls_policies.sql`, compatibilidad con el adapter dual y `Context`/`enforce_tenant_scoped` en toda query.

**Flujo de trabajo del repo (AGENTS.md):** leer `graphify-out/GRAPH_REPORT.md` antes de decisiones de arquitectura; `graphify update .` tras modificar código; UI respeta el sistema de marca de `Diseños/` (paleta `#F4F1ED/#1F1E1C/#C96442/#5A6B7C`, EB Garamond Italic para voz, Geist UI, Geist Mono datos, iconos 24×24 stroke 1.75).

---

## §1. Mapa de olas y gate

| Ola | Hitos | Resultado observable |
|---|---|---|
| 1 | E4-0, E4-1, E4-2 | El planner corre en sombra en dogfood MWT; los briefs existen; cero cambios visibles para el usuario |
| 2 | E4-3, E4-5 | El agente ejecuta pipelines mixtos multi-paso en `natural` (dogfood) y tiene memoria personal curada |
| 3 | E4-4 | La presencia única reemplaza la sección Agentes; el flujo "facturas cliente Colombia" funciona end-to-end |
| 4 | E4-6, E4-7, E4-8 | WhatsApp bidireccional, signup auto (flag apagado hasta gate), auditoría de cierre |

**Gate comercial (sin cambios):** E4-7 no se ABRE hasta: tenant externo ≥30 días, ≥10 casos reales, 0 fugas, primera factura pagada. El desarrollo de todo lo demás corre en paralelo. Pendientes humanos H1-H9 de E3: ninguno bloquea las Olas 1-3.

---

## §2. Detalle por hito

> Migraciones: SCHEMA_VERSION actual = **41**. Este plan usa v42, v43... — Fugu re-verifica al arrancar cada ola y renumera si otra rama avanzó.

---

### E4-0 — Fundaciones (interfaz de routing, flag, deudas E3)

**Objetivo:** separar PLANIFICAR de EJECUTAR en el routing sin cambiar ningún comportamiento actual, e instalar el flag de tres modos. Cerrar los dos gaps menores heredados de E3.

**Contexto real en el repo:**
- `app/src/routing/auto_dispatcher.py` — `run_auto_chain()` (planifica Y ejecuta mezclados), `_build_plan()` (planner con modelo barato, atajo canónico PDF→resumen→imagen), `_execute_step()`, `_render_step_input()` (handoff de artefactos entre pasos), `_estimate_complexity()`.
- `app/src/routing/catalog.py` — `resolve_model_for_capability()` (contrato F1 tiered DEC-006: CHEAPEST_FIRST/BEST_FIRST/mejor-valor por complejidad; checks de ventana de contexto y budget; la prioridad manual del admin NO participa en auto), `MODEL_QUALITY`, `DEFAULT_MODEL_CAPABILITIES`.
- `app/src/routing/policy.py` — `is_auto_mode_allowed()` con doble gate: env `FABERLOOM_AUTO_MODE_ENABLED` (default false) + `routing.auto_dispatch` por workspace.
- `app/src/config_cascade.py` — `DEFAULTS` con `routing.auto_dispatch=False`, `routing.max_budget_usd=2.0`, `routing.max_steps=4`, `routing.byo_mode="hibrido"`.
- Endpoint del modo auto: `POST /api/workspaces/{ws}/chats/{chat_id}/auto` (`api.py:1899`).
- Specs que gobiernan: `docs/ENT_PLAT_LLM_ROUTING.md` (§D/§F contrato F1 tiered), `docs/SPEC_LLM_ROUTING_ARCHITECTURE.md`.

**Tareas:**

0.1 **Flag `routing.mode`.** Añadir a `config_cascade.DEFAULTS`: `"routing.mode": "manual"`. Resolución user > workspace > tenant > default (mecanismo existente). Editable por owner/admin vía el settings API existente (`e3_3_router.py` / settings cascade). Compatibilidad: `is_auto_mode_allowed()` se reescribe para que `FABERLOOM_AUTO_MODE_ENABLED + routing.auto_dispatch=true` ≡ `routing.mode="natural"` en ese workspace (precedencia documentada: flag explícito gana sobre el mapeo legacy; el env var queda DEPRECATED con warning en logs y nota en `docs/ENT_PLAT_LLM_ROUTING.md`).

0.2 **Interfaz `TaskDispatcher`.** Nuevo `app/src/routing/dispatcher_base.py`:
```python
@dataclass
class DispatchStep:
    step_id: str; capability: str; task: str; prompt: str; complexity: str
    model_candidates: list[dict]  # [{provider_slug, model, est_input_tokens, est_cost_usd, quality}]
    chosen: dict | None; reason: str; inputs_from: str | None  # step_id anterior
@dataclass
class DispatchPlan:
    steps: list[DispatchStep]; est_total_cost_usd: float; planner_cost_usd: float
class TaskDispatcher(Protocol):
    def plan(self, ctx, conn, *, user_request, attachments, policy) -> DispatchPlan: ...
```
Refactor de `run_auto_chain`: extraer la planificación a `NaturalPlanner.plan()` (que envuelve `_build_plan` + la resolución de modelo por paso) y dejar la ejecución como `execute_plan(ctx, conn, plan, ...)`. **La lógica interna no cambia** — es un refactor de separación con test de regresión bit-a-bit (mismo request auto → mismo plan, mismos modelos, mismo output con seeds mockeados).

0.3 **Gap E3-3 — presigned URL cross-tenant.** Test en la contamination suite: con el `ObjectStore` dual (MinIO + memoria, ver `storage.py`), verificar que una URL/lectura firmada de un objeto bajo `t-A/ws-X/...` es imposible desde `Context(tenant_id="B")`. Si hay docker disponible en CI usar MinIO efímero; si no, mock del cliente S3 con aserciones sobre el prefijo resuelto.

0.4 **Gap E3-1 — smoke de restore.** `app/scripts/backup_restore_smoke.py`: localiza el backup más reciente (ruta de `backup.py`), restaura a BD temporal, compara conteos de tablas críticas (`fnd_tenants`, `workspace`, `kb_source`, `manual_invoice`, `usage_record`), escribe reporte a `docs/audits/BACKUP_SMOKE_<fecha>.md`. Documentar el cron sugerido en `docs/OPERACION_VPS_E3.md`.

**Archivos:** crear `routing/dispatcher_base.py`, `scripts/backup_restore_smoke.py`, tests. Modificar `routing/auto_dispatcher.py`, `routing/policy.py`, `config_cascade.py`, `docs/ENT_PLAT_LLM_ROUTING.md` (append: deprecación del env var + flag de 3 modos), `docs/OPERACION_VPS_E3.md`.
**Migraciones:** ninguna.
**Tests:** `test_e4_0_dispatcher_interface.py` (plan() devuelve DispatchPlan válido; steps encadenados con inputs_from), `test_e4_0_regression_auto.py` (bit-a-bit pre/post refactor), `test_e4_0_mode_flag.py` (mapeo legacy env→natural; precedencia; default manual), `test_e4_0_presigned_cross_tenant.py`, `test_e4_0_backup_smoke.py` (contra fixture sintética).
**DoD:** suite 0 failed / passed >619; comportamiento de `manual` y del auto legacy idéntico a hoy; ambos gaps E3 cerrados con test.
**Esfuerzo estimado:** 1 sesión Fugu.

---

### E4-1 — Workspace briefs (awareness dentro de la Entidad Viva E2-5)

**Objetivo:** que el agente pueda responder "¿qué hay en X workspace?" a nivel tenant, desde datos precalculados nivel INDEX, sin escanear en caliente y sin filtrar nada sellado.

**Contexto real en el repo:**
- `docs/SPEC_E2_5_ENTIDAD_VIVA.md` — el ciclo ambiental: Ambient Orchestrator con fases collect→score→dedup→propose→audit, tool allowlist DURA (`read_workspace`, `read_kb`, `read_inbox`, `create_workloom_item`; cualquier otro tool = P0), budget 5% del router diario, ventana 06:00-22:00 America/Bogota, kill switches global/workspace, dedup 24h, circuit breakers de utilidad y costo.
- `app/src/ambient.py` — `_scheduled_tenant_ids()`, `_run_tenant_schedule()`, detectores en `ambient_detectors.py`.
- `app/src/key_broker.py` — `resolve_read_level(..., default=CONTENT) -> (KeyLevel, sealed)`: CLOSED/INDEX/CONTENT; espacio con política CONTENT expone solo INDEX a quien no es approver.
- `docs/POL_VISIBILIDAD.md` y `docs/faberloom/POL_FB_KR_PRIVACY_TIERS_v1.md` — reglas de visibilidad y tiers de privacidad del conocimiento.
- SPEC_FB_WORKSPACE_v1 §3 "Contexto activo": el panel derecho ya contempla un footer de contexto (knowledge cargado, caso activo, freshness, tokens) — el brief es la fuente natural de ese footer a nivel tenant.

**Tareas:**

1.1 **Enmienda de spec PRIMERO.** `docs/SPEC_E2_5_ENTIDAD_VIVA.md` → v1.1: añadir `write_workspace_brief` a la allowlist (§9) con justificación: dato **derivado regenerable** (R12), sin efecto externo, sin irreversibilidad; el brief writer no toca KB/rutinas/correo. Changelog en la spec. Sin la enmienda commiteada, no tocar la allowlist.

1.2 **Tabla `workspace_brief` (v42).** PK `(tenant_id, workspace_id)`; columnas: `brief_json`, `computed_at`, `source_counts_json` (docs/mails/facturas/runs/chats contados), `staleness_policy_json` (`{max_age_h: 24, max_writes: 50}`), `generation_cost_usd`, `version` (incremental), `stale` (bool derivado en lectura, no almacenado) + campos latentes (R13) + índices + RLS.

1.3 **Generador** `app/src/living_agent/briefs.py` — `build_workspace_brief(ctx, conn, workspace_id) -> dict`:
- Consulta `resolve_read_level` por espacio ANTES de leer nada; espacio CLOSED → el brief registra `{"sealed": true, "object_count": N}` y nada más.
- Contenido nivel INDEX únicamente: conteos por tipo, títulos/punteros recientes que el nivel permita, entidades frecuentes extraídas de TÍTULOS (nunca de cuerpos), facturas abiertas (número+estado+monto agregado, no líneas), rutinas activas y último run, actividad reciente (N eventos del audit).
- El contenido de documentos se trata como DATOS, jamás como instrucciones (guardia anti-injection: el generador no pasa cuerpos de documentos al LLM; si en el futuro resume títulos con LLM, sanitiza con `security/injection.py`).
- CEO-only y `ceo_only_sections` jamás entran a `brief_json` (cruce con POL_VISIBILIDAD).

1.4 **Integración con el Ambient Orchestrator.** El refresh corre como tarea del ciclo existente en `ambient.py`: respeta ventana, budget (%), kill switches y backoff de la spec E2-5; dispara cuando `computed_at > max_age_h` o el contador de escrituras del workspace supera `max_writes` (contador barato desde audit/outbox). Costo al ledger como categoría `living_agent.brief`. **Ningún endpoint computa briefs en caliente.**

1.5 **API.** `GET /api/tenants/{tenant_id}/briefs` (lista los briefs de los workspaces que el usuario puede ver según rol/membresía — reutilizar el mismo filtro de visibilidad del listado de workspaces) y `GET /api/workspaces/{ws}/brief`. Respuesta incluye `computed_at`, `stale` y `version`. Si no existe brief aún: 200 con `{"pending": true}` y encolado — no 404, no generación inline.

1.6 **UI mínima.** En `app/static/js/app.jsx`, el footer "Contexto activo" del panel del chat (SpaceView) muestra freshness del brief del workspace activo. Nada más en esta ola.

**Archivos:** crear `living_agent/__init__.py`, `living_agent/briefs.py`; modificar `models.py` (v42), `postgres_rls_policies.sql`, `ambient.py`, `ledger.py`, `api.py` o router nuevo `living_agent/router.py`, `app.jsx` (footer), `docs/SPEC_E2_5_ENTIDAD_VIVA.md` (v1.1).
**Tests:** `test_e4_1_briefs.py` (conteos exactos con datos sintéticos; brief versiona e incrementa), `test_e4_1_briefs_visibility.py` (CLOSED→sealed-only; CONTENT-space→INDEX para no-approver; CEO-only ausente; cross-tenant imposible; usuario sin membresía no ve el brief), `test_e4_1_briefs_cold_only.py` (el endpoint jamás genera; stale→pending/advertencia), `test_e4_1_briefs_ambient.py` (kill switch corta el refresh; budget respeta el % del ciclo).
**DoD:** brief correcto, frío, invisible para quien no debe, y el ciclo ambiental lo mantiene solo.
**Esfuerzo:** 1-2 sesiones Fugu.

---

### E4-2 — Planner instrumentado: shadow, track record y gobernanza de promoción

**Objetivo:** dar confianza medible al routing natural existente: log de toda decisión, modo sombra comparativo, aprendizaje del track record, y promoción a `natural` gobernada por el Autonomy Control Engine — no por fe.

**Contexto real en el repo:**
- El planner y la selección por complejidad/costo YA existen (ver E4-0). Lo que NO existe: persistencia de la decisión, comparación contra el camino manual, feedback de track record en `_score`, y criterio formal de promoción.
- `docs/SPEC_AUTONOMY_CONTROL_ENGINE.md` — primitivos `ImpactVector`, `ActionSpec`, escalación hard/soft, **lógica de promoción con opportunity-set logging** (loguear también las oportunidades donde el agente NO actuó, para medir qué se habría ganado), **Oscillation Counter** (anti-complacencia) y `HumanAlignmentScore`. Este documento ES el marco de promoción shadow→natural.
- `app/src/skill_primitives.py` — `update_track_record`, `autonomy_ceiling` (C0-5): el mecanismo de track record ya existe para skills; se generaliza a (capability, modelo).
- `usage_record` ya registra `chain_id` y costo por paso (db.py).

**Tareas:**

2.1 **Tabla `planner_decision_log` (v43).** Columnas: `id`, `tenant_id`, `workspace_id`, `chain_id`/`task_ref`, `mode` (`shadow|natural`), `plan_json` (el `DispatchPlan` serializado: pasos, candidatos con est_tokens/est_cost/quality, elegido, razón), `actual_outcome_json` (para shadow: qué modelo usó el camino real y su costo; para natural: costo/latencia/aceptación reales), `correlation_id` (contrato AuditWriter), `created_at` + campos latentes + RLS + índices por tenant/mode/created_at. **R11: el flujo auto existente también escribe aquí desde ya**, no solo el shadow.

2.2 **Modo shadow.** En `POST /chats/{chat_id}/completions` (camino manual/presets): cuando `routing.mode="shadow"`, tras responder al usuario por el camino normal, se encola (async, fuera de la latencia percibida) una corrida de `NaturalPlanner.plan()` que SOLO planifica — nunca ejecuta pasos, nunca consume budget de ejecución. Su único costo es el paso de planning (modelo cheap), registrado como `living_agent.shadow_plan` y contado dentro del budget ambiental del tenant (mismo pool del 5% — el shadow es observación, como los detectores). `actual_outcome_json` guarda qué hizo el camino real para comparación.

2.3 **Track record feedback.** Nueva tabla o extensión: acumulado de aceptación por `(tenant_id, capability, provider_slug, model)` alimentado por el feedback existente (aceptación/regeneración de outputs, `update_track_record` como referencia de diseño). `resolve_model_for_capability._score` incorpora el ajuste SOLO cuando `routing.mode != "manual"`: aceptación ≥0.90 → bonus de orden; <0.70 con ≥20 muestras → descarte del candidato para esa capability. Umbrales en `living_agent/constants.py` (junto a los de promoción de packs si hoy están inline — extraer, no duplicar).

2.4 **Shadow report.** `GET /api/tenants/{tenant_id}/routing/shadow-report?days=14` (owner/admin): distribución de modelos elegidos por el planner vs los realmente usados, costo estimado vs costo real, ahorro proyectado, nº de decisiones, discrepancias notables (planner eligió capability distinta), y las métricas del Autonomy Control Engine (§2.6). platform_admin: solo agregados sin prompts (R9).

2.5 **Vista UI.** Nueva entrada en el rail admin (acordeón "Tenant", junto a "Router / Proveedores"): "Routing en sombra" → componente `app/static/js/routing_shadow.jsx` (patrón de `promotion_readiness.jsx`: fetch + tabla + tiles). Marca de `Diseños/` (leer `SKILL_FRONTEND_TEN_PRINCIPLES_V2` antes de tocar UI).

2.6 **Gobernanza de promoción (Autonomy Control Engine aplicado).** Documento `docs/faberloom/PLB_FB_E4_ROUTING_NATURAL_v1.md` + implementación mínima:
- Mapeo al Autonomy Ladder: `shadow` = Nivel 0 (observa, no sale al usuario); `natural` = Nivel 2 máximo (ejecuta interno); pasos con efecto externo SIEMPRE draft-first (Regla Sagrada, DA-6) — el orquestador de E4-3 lo garantiza.
- Criterios de promoción por workspace (del ACE): ≥2 semanas u ≥N=50 decisiones shadow; ahorro proyectado ≥0; 0 decisiones "absurdas" en revisión manual del curador (checklist en el PLB); **Oscillation Counter**: si un workspace promovido a natural se degrada 2 veces (rollback por métricas), queda en cooldown de 30 días antes de re-promover.
- Degradación automática (sin aprobación): si el costo real supera el estimado >150% en una ventana, o la tasa de regeneración de outputs sube >X% vs baseline manual → el workspace vuelve solo a `shadow` y se audita `living_agent.routing.degraded`.
- La promoción es SIEMPRE acción manual del owner/curador con confirmation_token (patrón `promote_pack`).

**Archivos:** crear `living_agent/planner.py` (envuelve al NaturalPlanner de E4-0 con logging), `living_agent/constants.py`, `static/js/routing_shadow.jsx`, `docs/faberloom/PLB_FB_E4_ROUTING_NATURAL_v1.md`; modificar `models.py` (v43), `postgres_rls_policies.sql`, `api.py` (hook shadow en completions + endpoints), `routing/catalog.py` (_score con feedback), `app.jsx` (rail), `index.html` (script tag).
**Tests:** `test_e4_2_decision_log.py` (natural y shadow escriben plan completo con correlation_id), `test_e4_2_shadow_no_side_effects.py` (respuesta, costo de ejecución y latencia del camino real idénticos con shadow on/off), `test_e4_2_track_record_feedback.py` (≥0.90 prefiere; <0.70 con muestras descarta; modo manual intacto), `test_e4_2_shadow_report.py` (agregados correctos; platform_admin sin prompts), `test_e4_2_degradation.py` (overrun→vuelve a shadow+audit; oscillation counter).
**DoD:** dogfood MWT en `shadow`; el reporte muestra comparaciones reales; la promoción y degradación funcionan gobernadas.
**Esfuerzo:** 2 sesiones Fugu.

---

### E4-3 — Orquestación multi-paso con handoff, HITL y kill (el agente ejecuta)

**Objetivo:** que `natural` ejecute planes de N pasos con artefactos que viajan entre modelos, pausas HITL a mitad de cadena, kill switch por tarea y costo agregado — la mecánica del ejemplo canónico "lee el PDF, resume, genera imagen".

**Contexto real en el repo:**
- `run_auto_chain` YA ejecuta cadenas (`start_chain`, `_execute_step`, `_render_step_input`, `_execute_openai_image_step`) y `usage_record` registra `chain_id` + costo por paso. **Paso 0 del hito: inventariar qué persiste hoy la cadena** (¿tabla propia o solo usage_record?) y decidir extender vs crear — documentando la decisión.
- HITL patrón existente: `skill_requires_hitl` (skills.py), draft-first del correo (smtp confirmation_token), `foundation/m13_draft_hitl.py`.
- WorkLoom (`workloom.py`: `assign_workloom_item`, `list_workloom_items`) — donde el usuario opera y aprueba (SPEC_FB_WORKSPACE: "WorkLoom = TRABAJO del día").
- Cifrado de objetos por tenant: `storage.py` `encrypt_object_payload` (`FLENC1:`).
- `docs/faberloom/SCH_FB_TASK_ENTITY.md` — el schema canónico de "task" de la KB: usarlo como contrato de columnas donde aplique.

**Tareas:**

3.1 **Persistencia de la tarea (v44).** Según el inventario del paso 0: extender la persistencia de chains o crear `agent_task` + `agent_task_step` alineadas a `SCH_FB_TASK_ENTITY`. Mínimo requerido: task con `status` (`planned|running|paused_hitl|completed|killed|failed|degraded`), `plan_id` (FK a `planner_decision_log`), costo total; step con `capability`, `model_used`, `input_ref`, `output_ref`, `evidence_id`, `cost_usd`, `status`. Campos latentes + RLS.

3.2 **Artefactos de handoff.** El output intermedio de cada paso (p.ej. el resumen) se materializa como objeto en el `ObjectStore` bajo el prefijo del workspace, cifrado con la data key del tenant (mecanismo existente), y `output_ref` apunta ahí. El paso siguiente recibe el artefacto vía `_render_step_input` extendido. Evidence bundle por paso (reusar `attach_evidence`/`external_evidence` de C0-7).

3.3 **HITL a mitad de cadena.** Antes de ejecutar cada paso, el orquestador evalúa si el paso tiene efecto externo (misma lógica de `skill_requires_hitl` generalizada: capability de envío, destino externo, tool fuera de allowlist). Si sí → task pasa a `paused_hitl`, se crea **item de WorkLoom** con el draft y la evidencia (el usuario aprueba DONDE ya aprueba todo), y la cadena solo continúa con confirmation_token. Regla Sagrada: esto NO es configurable por autonomía.

3.4 **Kill y budget.** Kill switch por task (`POST /api/workspaces/{ws}/agent-tasks/{id}/kill`) + el kill ambiental del tenant corta también tasks en curso en su siguiente checkpoint (patrón E2-5 §6). Validación de budget ANTES de ejecutar (plan completo vs `enforce_budget`) y DURANTE (acumulado real; >150% del estimado → degradación de modelos restantes o corte fail-closed con estado `degraded`/`failed`, decisión logueada).

3.5 **Ledger.** La task es UNA entrada agregada con desglose por paso: extender `usage_record` con `task_id` (nullable) o vista de agregación por `chain_id` — elegir lo que menos toque el esquema; el costo aparece en el health dashboard del tenant (categoría `living_agent.tasks`).

3.6 **UI.** `static/js/agent_tasks.jsx`: lista + detalle de task (pasos con estado/modelo/costo, botón kill, botón aprobar HITL que enlaza al item de WorkLoom). Entrada en el rail junto a WorkLoom. El composer del chat muestra "el agente está trabajando: paso 2/3 (generando imagen)" vía el patrón realtime existente (`SPEC_FB_FRONTEND_REALTIME_STATE_v1`).

3.7 **Habilitar natural multi-paso.** Quitar el gating de 1 paso de la Ola 1. Los pasos internos (texto, resumen, KB) corren solos en Nivel 2; los externos siempre draft-first.

**Tests:** `test_e4_3_orchestrator.py` (pipeline 2 pasos, 2 modelos, artefacto íntegro entre pasos, cifrado verificado), `test_e4_3_hitl_pause.py` (paso externo→paused_hitl→item WorkLoom→token→continúa; sin token jamás), `test_e4_3_kill_budget.py` (kill a mitad deja estado consistente y costo parcial; overrun corta fail-closed), `test_e4_3_ledger.py` (agregación por task correcta), `test_e4_3_isolation.py` (tasks y artefactos cross-tenant imposibles).
**DoD:** demo en dogfood: "resume este PDF y genera una imagen del resumen" end-to-end con 2 modelos y costo agregado visible; un paso de correo queda en WorkLoom esperando aprobación.
**Esfuerzo:** 2-3 sesiones Fugu.

---

### E4-5 — Memoria viva (CAPA 1 personal, sobre M17)

**Objetivo:** que el agente crezca con cada usuario y tenant: detecta patrones, los propone, el humano cura, la memoria se usa en la siguiente conversación. **Diseño ya especificado en la KB — implementarlo, no inventarlo.**

**Contexto real en el repo:**
- `app/src/foundation/m17_memory.py` — YA existe la API de bloques: `upsert_block`, `recall`, `list_blocks`, `list_namespaces`, `archive_block` sobre `fnd_memory_blocks` (namespace jerárquico + tenant_id). Es la implementación M17 (Letta-style, ver `SPEC_FB_FUNC_M17_MEMORY_LETTA_v1` y `ENT_PLAT_MEMORY_STACK` §D: 3 capas, working memory efímera / operativa / KB canónica).
- `docs/faberloom/ENT_FB_USER_LEARNING_MODEL_v1.md` — **la spec de este hito**: curaduría personal CAPA 1 (detección automática de patterns → notificación al AM → vista de revisión → acciones aprobar/mantener/descartar → memoria L2 episódica PRIVADA → rollback personal), reglas inquebrantables (§7), qué NUNCA hace (§4), transición CAPA 1→CAPA 2 organizacional (§5).
- `docs/SPEC_AGENT_ARCHITECTURE_ALE.md` §6-7 — **Termómetro de Aprendizaje** (widget frío/tibio/caliente por outputs sin consolidar; modal "Indexar Aprendizaje" con patrones/correcciones/gold candidates y acciones Confirmar/Editar/Descartar; NUNCA auto-promueve desde thumbs up) + **feedback tipificado** (no texto libre).
- SPEC_FB_WORKSPACE §6: working memory efímera se descarta al cerrar conversación; nada pasa a persistente sin gate humano.

**Tareas:**

5.1 **Namespaces.** Convención sobre `fnd_memory_blocks`: `living_agent/{tenant}/{user_id}/personal/...` (CAPA 1 privada del usuario) y `living_agent/{tenant}/shared/{dominio}/...` (CAPA 2, solo vía transición curada §5). Visibilidad: la memoria personal de un usuario JAMÁS se inyecta en conversaciones de otro usuario; CEO-only respeta visibilidad.

5.2 **Detección de patterns.** Detector nuevo del ciclo ambiental (`ambient_detectors.py`, dentro de la allowlist read-only): analiza los últimos N feedbacks tipificados y correcciones del usuario, produce candidatos de memoria como `ambient_proposal` (arquitectura E2-5 intacta: el detector NO escribe memoria, propone).

5.3 **Curaduría (el gate humano).** Vista de revisión personal (ENT_FB_USER_LEARNING_MODEL §3.3): el usuario ve candidatos con evidencia y decide aprobar/mantener/descartar. Aprobar → `upsert_block` en su namespace personal con `approved_by` (campo latente). Rollback personal: `archive_block` + el bloque archivado deja de inyectarse de inmediato.

5.4 **Inyección.** En `completions`/`invoke`/orquestador: `recall(namespace personal del usuario + shared del dominio activo)` acotado por tokens (top-K, presupuesto de contexto según `POL_CONTEXT_BUDGET`), inyectado como bloque de sistema claramente delimitado como memoria (nunca como instrucción de mayor autoridad que las políticas).

5.5 **Termómetro de Aprendizaje.** Widget bottom-right en SpaceView (spec §6 de SPEC_AGENT_ARCHITECTURE_ALE): contador de outputs sin consolidar → modal "Indexar Aprendizaje" listando los candidatos del detector → acciones. Feedback tipificado en los outputs del chat (chips: correcto/tono/dato erróneo/formato — según §7), que alimenta el track record (E4-2.3) y el detector (5.2).

5.6 **Higiene.** `GET/DELETE /api/tenants/{t}/agent/memories` (el usuario ve/borra las suyas; owner ve/borra las shared). TTL opcional por tipo.

**Tests:** `test_e4_5_memory_capa1.py` (candidato→aprobar→recall lo devuelve→rollback lo saca), `test_e4_5_memory_privacy.py` (memoria personal invisible para otro usuario; shared respeta visibilidad; cross-tenant imposible), `test_e4_5_no_auto_promote.py` (thumbs up NUNCA escribe memoria; solo el gate), `test_e4_5_thermometer.py` (conteo y estados), `test_e4_5_injection_budget.py` (recall respeta presupuesto de tokens).
**DoD:** el flujo completo de ENT_FB_USER_LEARNING_MODEL §3 funciona; una corrección del usuario aprobada cambia el comportamiento en la siguiente conversación.
**Esfuerzo:** 2 sesiones Fugu.

---

### E4-4 — Presencia única (el Agente Vivo reemplaza la sección Agentes)

**Objetivo:** una sola presencia conversacional por tenant: en el chat general "mira por encima" con briefs (INDEX); al profundizar entra al workspace (CONTENT con la autoridad del usuario). Muere la sección "Agentes" como lista visible al usuario final.

**Contexto real en el repo:**
- Navegación actual (`app.jsx`): rail con FaberLoom (`nav="space"` → SpaceView = chat por workspace), Inbox, WorkLoom, StackLoom, KB, Gold; en modo admin: acordeón "Capacidades" con **Skills y Agentes** (`nav === "agents"`, línea ~366), Router/Proveedores, Facturación, Salud, Audit, Config cascada, Promoción de packs.
- Chats HOY son por workspace (`/api/workspaces/{ws}/chats/...`). El chat general del tenant no existe.
- `docs/SPEC_QUERY_PROCESSING_PIPELINE.md` — el pipeline objetivo por fases (recepción→carga de contexto→detección de intención→skill matching→...) con secciones "En FaberLoom (target)": es el contrato de cómo la presencia procesa cada mensaje.
- `docs/faberloom/SPEC_FB_WORKSPACE_v1.md` — 3 modos auto-detectados (OPERACIONAL/AUTOMATIZACIÓN/CONSTRUCCIÓN), panel derecho con Tab Agentes/Skills/Aprendizaje, composer con @menciones.
- `entity_identity` (E3-3) — identidad inmutable por tenant; bootstrap seed en `platform_admin._bootstrap_approved_tenant`.

**Tareas:**

4.1 **Enmienda de spec PRIMERO.** `SPEC_FB_WORKSPACE_v1` → **v2**: (a) el Tab Agentes del panel derecho se reemplaza por "Tab Agente" (estado del Agente Vivo: qué capacidades/skills tiene activas, tasks en curso, termómetro); (b) se añade el "chat general del tenant" como superficie nueva; (c) los 3 modos se mantienen — el Agente Vivo ES quien los detecta; (d) las @menciones de agentes pasan a @menciones de CAPACIDADES/skills. Aprobador: CEO. Sin spec v2 commiteada no se toca la UI.

4.2 **Chat general del tenant.** Decisión de diseño: se implementa como **workspace de sistema** `ws-general` creado por el bootstrap seed en cada tenant (reutiliza TODO el stack de chats/completions/RLS existente; evita cirugía sobre tablas de chat). Marcado `workspace.kind="tenant_general"` (columna nueva v45 con default `"standard"`). El RLS y los prefijos MinIO funcionan sin cambios.

4.3 **Presencia** `app/src/living_agent/presence.py`:
- Resolución de intención por mensaje (modelo cheap, mismo presupuesto que el planner): ¿pregunta sobre contenido de workspaces (→briefs)? ¿profundización (→workspace concreto)? ¿tarea (→planner/orquestador)? ¿conversación simple? — implementando las fases de SPEC_QUERY_PROCESSING_PIPELINE.
- Nivel general: responde SOLO desde `workspace_brief` de los workspaces visibles al usuario + memoria (E4-5). Sin fuente → "no lo sé; ¿quieres que entre al workspace X?" (R1: cero relleno).
- Profundización: resuelve el workspace objetivo, lee vía el camino normal (key broker media; **la autoridad es la del usuario que pregunta** — el agente jamás eleva privilegios), responde citando fuente. La negativa ante espacio sin acceso sigue POL_VISIBILIDAD (no revelar existencia de lo sellado más allá de lo que INDEX permita).
- Identidad: el system prompt se construye desde `entity_identity` (nombre, tono) + `SCH_FB_WS_INSTRUCTIONS` del workspace activo. Auditoría por respuesta general: `living_agent.read` (qué briefs, a qué nivel) con correlation_id.

4.4 **UI.**
- Rail: "FaberLoom" (space) pasa a ser el chat del Agente Vivo del workspace activo + entrada nueva arriba "— {display_name del agente}" para el chat general del tenant.
- **Eliminar `RailItem "Agentes"`** del acordeón Capacidades (app.jsx ~366) y la `AgentsView` de usuario final; el catálogo/fábrica queda accesible SOLO para rol curador/admin como "Fábrica de skills" (renombrar la entrada, no borrar el código de la fábrica).
- Panel derecho según spec v2: Tab Agente (estado, tasks en curso con link a agent_tasks, termómetro E4-5), Tab Skills (igual), Tab Aprendizaje (igual).
- Bootstrap: display name del agente en onboarding (default "Faber"); editable solo vía el flujo de identidad E3-3 (owner distinto + token).

4.5 **platform_admin.** Verificación explícita de que nada del agente (chat general, briefs, memorias, tasks) es accesible a platform_admin más allá de agregados (R9).

**Tests:** `test_e4_4_presence_general.py` (pregunta general responde desde briefs, auditado, sin tocar CONTENT), `test_e4_4_presence_deepdive.py` (profundizar lee CONTENT solo con derecho del usuario; sin derecho → negativa correcta según política), `test_e4_4_no_privilege_elevation.py`, `test_e4_4_general_workspace.py` (ws-general creado en bootstrap; RLS intacto; no aparece en listados como workspace normal), `test_e4_4_canonical_flow.py` (**el ejemplo del CEO**: workspaces con facturas sintéticas → "¿qué facturas tengo del cliente Colombia?" → lista desde brief → "muéstrame la #X" → la trae del workspace), `test_e4_4_platform_admin_blocked.py`.
**DoD:** el flujo canónico pasa end-to-end; la sección Agentes no existe para usuario final; dogfood MWT opera ≥1 semana solo con la presencia antes de la Ola 4.
**Esfuerzo:** 3 sesiones Fugu (la más grande: backend + UI + spec).

---

### E4-6 — Canal WhatsApp bidireccional

**Objetivo:** el agente responde por WhatsApp — siempre draft-first (Regla Sagrada; sin excepciones en E4).

**Contexto real:** `connectors/whatsapp_inbound.py` ya implementa GET challenge + firma HMAC + flag por tenant → `capture_informal_interaction`. Falta el saliente y el enlace con la presencia.

**Tareas:** 6.1 `connectors/whatsapp_outbound.py`: cliente Cloud API (send message + template), secrets por tenant en `TenantSecretStore` (`connectors/whatsapp/*`), `confirmation_token` determinista (patrón smtp.py), endpoints reales `[PENDIENTE — NO INVENTAR]` hasta credenciales del tenant, fail-closed sin config. 6.2 Flujo: entrante → presencia (E4-4) genera draft de respuesta → **item de WorkLoom** (cola HITL unificada con correo) → aprobación con token → envío. 6.3 Ventana de 24h y plantillas: fuera de ventana solo templates aprobados (los templates del tenant son config, no código); modelar `session_message vs template` en el conector. 6.4 UI: la cola de aprobación de WorkLoom muestra el canal (correo/WhatsApp) y el preview.
**Tests:** `test_e4_6_whatsapp_outbound.py` (jamás envía sin token; fail-closed sin secrets; ventana 24h exige template; aislamiento de secrets), `test_e4_6_channel_flow.py` (entrante→draft→WorkLoom→aprobación→transporte mock).
**DoD:** conversación completa simulada con transporte mockeado; activar en real = configurar secrets.
**Esfuerzo:** 1-2 sesiones Fugu.

---

### E4-7 — Signup público GA (gated)

**Objetivo:** registro sin aprobación manual, con defensas, listo para ENCENDER cuando el gate esté verde.

**Tareas:** 7.1 Config de plataforma `signup.approval = manual|auto` (default `manual`); en auto: email verificado → tenant `active` + bootstrap seed (incluye `ws-general` + identidad del agente) sin tocar el flujo `pending_approval`. 7.2 Defensas: rate limit por IP (existe) + límite global signups/día + captcha (proveedor `[PENDIENTE — NO INVENTAR]`, decidir al abrir) + lista de dominios desechables en config + suspensión automática por exceso de plan (fail-closed existe). 7.3 Onboarding self-serve: el primer mensaje del Agente Vivo en el chat general ES el onboarding (qué sabe hacer, cómo conectar correo, cómo subir archivos). 7.4 `docs/faberloom/PLB_FB_E4_APERTURA_SIGNUP_v1.md`: checklist de apertura (gate §1 con evidencia, H1/H3 ejecutados, monitoreo, rollback = flag a manual).
**Tests:** `test_e4_7_signup_auto.py` (auto end-to-end; manual intacto; límite global corta; tenant nuevo recibe agente + ws-general).
**DoD:** funcional tras flag; la apertura real es decisión manual con checklist.
**Esfuerzo:** 1 sesión Fugu.

---

### E4-8 — Hardening y auditoría de cierre

**Objetivo:** cerrar E4 con la disciplina de E3.

**Tareas:** 8.1 Contamination suite E4 (`test_e4_8_contamination_e4.py`): briefs, memorias, decision logs, tasks, artefactos de handoff, chat general — cross-tenant y cross-visibilidad en un agregador. 8.2 Injection: documento adversarial en un workspace no altera el brief ni la respuesta general (`test_e4_8_brief_injection.py`, usando `security/injection.py`); mensajes WhatsApp adversariales; el chat general como superficie de ataque (pase contra `ENT_PLAT_SEGURIDAD` y `SPEC_FB_RAG_SECURITY_FIREWALL_v1`). 8.3 Health dashboard: sección del agente (briefs frescos/stale, tasks por estado, costo `living_agent.*`, memoria: bloques activos) en `health_dashboard.py` + `.jsx`. 8.4 Métricas del ACE en el shadow-report: HumanAlignmentScore (muestreo de decisiones evaluadas por el curador) y oscilaciones. 8.5 Auditoría `docs/audits/AUDIT_E4_CIERRE_<fecha>.md` (formato E3: semáforo, evidencia por archivo, suite, pendientes humanos) + `docs/faberloom/ARCH_FB_LIVING_AGENT_v1.md` (arquitectura as-built) + bloques KB para `ENT_GOB_PENDIENTES` y los IDX afectados (gate de indexación del proyecto Knowledge).
**DoD:** 0 failed; passed estrictamente mayor que al inicio de E4; adversariales verdes; documentación KB entregada.
**Esfuerzo:** 1-2 sesiones Fugu.

---

## §3. Riesgos P0

| Riesgo | Mitigación |
|---|---|
| Brief filtra contenido sellado/CEO-only | Generador consulta key broker ANTES de leer; INDEX-only; títulos nunca cuerpos; tests E4-1/E4-8 |
| Cross-tenant vía superficies nuevas (briefs/memoria/tasks/chat general) | RLS + Context + campos latentes en todo; contamination E4 por hito |
| Planner quema presupuesto en natural | Validación pre-ejecución vs budget; degradación automática >150%; shadow primero; Oscillation Counter; rollback por flag |
| Prompt injection (documento → brief; WhatsApp → presencia) | Contenido = datos, jamás instrucciones; `security/injection.py`; tests adversariales E4-8; regla E2-5 §16.2 |
| Regresión del routing manual | `manual` intacto tras la interfaz; regresión bit-a-bit en E4-0; shadow sin efectos (test dedicado) |
| El agente inventa ("sabe" sin fuente) | R1: toda afirmación cita brief o contenido leído; sin fuente → ofrece profundizar |
| Elevación de privilegios vía el agente | La autoridad SIEMPRE es la del usuario; test dedicado E4-4 |
| Muerte de sección Agentes rompe al curador | Fábrica/catálogo intactos para rol curador; solo cambia la superficie de usuario final; spec v2 aprobada antes de tocar UI |
| Memoria auto-promovida (complacencia) | Gate humano SIEMPRE (ENT_FB_USER_LEARNING_MODEL §7; thumbs up jamás escribe memoria) |

## §4. Qué NO está en E4

Nivel 3+ del Autonomy Ladder (auto-notifica/auto-excepciones); auto-send de WhatsApp; promoción automática de packs o de routing; e-factura real sin certificados (H4+H5); federación de agentes entre tenants; CAPA 2 organizacional completa del learning model (solo la transición curada mínima); Letta como servicio separado (M17 sobre `fnd_memory_blocks` es suficiente en E4 — `ENT_PLAT_MEMORY_STACK` E2 se re-evalúa en E5); cualquier relajación de HITL/budget/visibilidad.

---

## ANEXO — Prompt para Fugu: OLA 1 (E4-0 → E4-1 → E4-2)

```text
Fugu: arranca la ETAPA 4 de faber_loom_local_vv2. Rama nueva: e4-agente-vivo. Plan rector: Plan/PLAN_DESARROLLO_FABERLOOM_ETAPA4_v2.md (cópialo al repo desde el documento adjunto del CEO si aún no está). Sigue AGENTS.md: lee graphify-out/GRAPH_REPORT.md antes de decisiones de arquitectura y corre `graphify update .` tras modificar código.

ALCANCE: SOLO Ola 1 = E4-0, E4-1, E4-2, exactamente como los especifica el plan v2 (tareas, contratos, archivos, tests y DoD de cada hito). NO implementes E4-3 en adelante. El plan v2 manda; si difiere del código real, adapta y documenta la discrepancia.

REGLAS: R1-R10 de E3 + R11 (toda decisión del planner logueada con plan completo y correlation_id) + R12 (briefs regenerables) + R13 (campos latentes de AGENTS.md + RLS + adapter dual + Context/enforce_tenant_scoped en toda tabla/query nueva). Migraciones desde v42 (SCHEMA_VERSION=41 — re-verifica). Suite base 619 passed / 12 skipped / 0 failed: 0 failed siempre, passed solo sube, verificado al cierre de CADA hito antes de pasar al siguiente. Commit atómico por hito (E4-0, E4-1, E4-2) con changelog.

HECHOS VERIFICADOS (no los re-descubras): el planner multi-paso ya existe (run_auto_chain/_build_plan, atajo PDF→resumen→imagen); la selección por complejidad/costo ya existe (resolve_model_for_capability, DEC-006 — la prioridad manual NO participa en auto); el doble gate actual es FABERLOOM_AUTO_MODE_ENABLED + routing.auto_dispatch; key_broker.resolve_read_level(default=CONTENT) devuelve (nivel, sealed); el ciclo ambiental es SPEC_E2_5 con tool allowlist DURA; m17_memory.py ya tiene upsert/recall/archive.

PUNTOS NO NEGOCIABLES DE LA OLA:
- E4-0: regresión bit-a-bit del auto legacy y del modo manual tras el refactor a TaskDispatcher.
- E4-1: enmendar SPEC_E2_5 a v1.1 (allowlist + write_workspace_brief, con justificación R12 y changelog) ANTES de tocar la allowlist; briefs INDEX-only vía key broker; refresh SOLO desde el ciclo ambiental; el endpoint jamás genera.
- E4-2: shadow corre async y JAMÁS altera respuesta/costo/latencia del camino real (test dedicado); track record feedback solo en modos shadow/natural con umbrales en living_agent/constants.py; promoción/degradación gobernadas por el PLB nuevo (mapeo Autonomy Ladder: shadow=L0, natural≤L2; Regla Sagrada intocable); degradación automática por overrun >150% con audit.

CIERRE DE LA OLA: suite completa verde; workspace dogfood MWT en routing.mode="shadow"; graphify update .; docs/audits/AUDIT_E4_OLA1_<fecha>.md con el formato de las auditorías E3 (evidencia por archivo, tests nuevos con conteos, discrepancias con el plan, pendiente para Ola 2). Si algo es imposible sin violar R1-R13: documenta y sigue, no improvises.

Empieza verificando SCHEMA_VERSION y leyendo el GRAPH_REPORT.
```

*Las Olas 2-4 se ordenan con prompts derivados de este plan, una por vez, tras revisar la auditoría de la ola anterior.*
