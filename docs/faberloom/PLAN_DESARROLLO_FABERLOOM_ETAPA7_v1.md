# PLAN_DESARROLLO_FABERLOOM_ETAPA7_v1 — Autonomía nivel 3 y aprendizaje organizacional

id: PLAN_FB_ETAPA7
version: 1.0.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: PLAN
stamp: VIGENTE — 2026-07-12 — plan de la Etapa 7: subir el Autonomy Ladder a L3 interno y activar la CAPA 2 organizacional del aprendizaje
aprobador: CEO
relacionado: PLAN_FB_ROADMAP_E5_E10_v1 · SPEC_AUTONOMY_CONTROL_ENGINE · SPEC_AGENT_ARCHITECTURE_ALE · ENT_FB_USER_LEARNING_MODEL_v1 · SPEC_FB_EVAL_ARENA_v1 · ENT_FB_CURATOR_OPERATING_MODEL_v1 · ENT_FB_COMMITTEE_OPERATING_MODEL_v1

**Cláusula de re-validación:** antes de arrancar, el Arquitecto revisa este plan contra los datos reales de E5-E6 (volúmenes, tasas de aceptación, incidentes) y emite v1.1 si cambian los umbrales. Los hitos y contratos de abajo son el diseño comprometido.

---

## §0. Naturaleza y decisiones

E7 sube la autonomía SOLO donde los datos la respaldan, y convierte el aprendizaje personal (CAPA 1, E4-5) en aprendizaje organizacional (CAPA 2). La Regla Sagrada NO cambia: correo externo, WhatsApp, transacciones → draft-first SIEMPRE, en L3 igual que en L0.

**Decisiones del Arquitecto:**
- **DA7-1. L3 (AUTO_NOTIFICA) aplica ÚNICAMENTE a acciones internas** de una allowlist explícita y corta: consolidación de resúmenes KB, refresh de briefs bajo demanda del agente, creación de items WorkLoom informativos, ejecución de skills `classifier`/`validator` sin output externo. Nada que salga del tenant.
- **DA7-2.** La promoción a L3 es POR (acción, workspace), no global, y la gobierna el ACE existente extendido con `ImpactVector`/`ActionSpec` formales de la spec (`SPEC_AUTONOMY_CONTROL_ENGINE`): hard escalation, soft score, opportunity-set logging y HumanAlignmentScore por muestreo.
- **DA7-3. CAPA 2** se implementa exactamente según `ENT_FB_USER_LEARNING_MODEL_v1 §5` (transición curada CAPA 1→CAPA 2) + `ENT_FB_COMMITTEE_OPERATING_MODEL_v1` (quién decide qué entra al conocimiento organizacional). El comité en tenants pequeños = owner + curador (roles, no personas nuevas).
- **DA7-4. Eval arena primero, L3 después:** ningún skill/acción sube a L3 sin pasar por la arena (replay determinista). La arena es el freno de mano de toda esta etapa.
- **DA7-5.** `routing.mode=natural` pasa a ser DEFAULT para tenants nuevos cuando ≥5 tenants lo hayan corrido 30 días sin degradación — hito E7-5, condicionado a dato, no a fecha. Rama `e7-autonomia`.

## §1. Mapa de olas

| Ola | Hitos |
|---|---|
| 1 | E7-0 (ActionSpec/ImpactVector), E7-3 (eval arena) |
| 2 | E7-1 (L3 interno), E7-2 (CAPA 2) |
| 3 | E7-4 (consolidación asistida), E7-5 (natural por default) |
| 4 | E7-6 (acta) |

## §2. Detalle por hito

### E7-0 — Primitivos formales del ACE: ActionSpec e ImpactVector

**Objetivo:** cada acción que el agente puede ejecutar queda descrita formalmente con su impacto, para que la autonomía se decida por contrato y no por caso.

**Tareas:**
1. Implementar los primitivos de `SPEC_AUTONOMY_CONTROL_ENGINE` en `app/src/living_agent/action_registry.py`: `ActionSpec` (id, descripción, scope interno/externo, reversibilidad, datos que toca) e `ImpactVector` (dimensiones y pesos de la spec — usar los weights del documento; si la spec deja pesos abiertos, fijarlos en `living_agent/constants.py` con los defaults de la spec y comentario de origen).
2. Registrar TODAS las acciones actuales del agente (pasos del orquestador, primitives de skills, escrituras del ambiental) en el registro, cada una con su ActionSpec. Acción no registrada = no ejecutable en L≥2 (fail-closed).
3. Cómputo de impacto efectivo + gates por nivel (spec §"Gates por nivel"): función `max_autonomy_for(action_spec) -> int` usada por el orquestador ANTES de cada paso. Regla absoluta de Nivel 2 de la spec implementada literal.
4. Tabla `action_execution_log` (migración vN, campos latentes+RLS): toda ejecución L≥2 con action_id, nivel, impacto computado, resultado — el opportunity-set logging de la spec (también loguear cuando el agente PUDO actuar y no lo hizo por nivel insuficiente, para medir el costo de la prudencia).

**Archivos:** `living_agent/action_registry.py`, `living_agent/constants.py`, `orchestrator.py` (gate por paso), `models.py`, `postgres_rls_policies.sql`.
**Tests:** `test_e7_0_action_registry.py` (acción no registrada bloqueada en L≥2; impacto computado estable; regla absoluta L2), `test_e7_0_opportunity_log.py`.
**DoD:** inventario completo de acciones con spec; orquestador gateado por registro. **Esfuerzo:** 2-3 sesiones Fugu.

### E7-1 — Autonomy Ladder Nivel 3 (AUTO_NOTIFICA) interno

**Objetivo:** acciones internas maduras se ejecutan sin aprobación previa y notifican post-hecho — con reversa de un clic.

**Tareas:**
1. Allowlist L3 (DA7-1) en `living_agent/constants.py` — corta, explícita, con changelog para cada adición.
2. Promoción por (acción, workspace): extender `autonomy.py` con `evaluate_action_promotion(action_id, workspace)` usando los criterios de la spec (ejemplo L2→L3 de la spec: N ejecuciones L2 con tasa de aprobación humana ≥ umbral, 0 reversiones, HumanAlignmentScore del muestreo ≥ umbral) + Oscillation Counter reusado. Promoción manual con token (patrón existente); degradación automática por reversión o alignment bajo.
3. Notificación post-hecho: cada ejecución L3 crea un item WorkLoom informativo tipo `auto_executed` con botón **[Revertir]** — toda acción L3 DEBE tener implementada su reversa (`ActionSpec.reversible=true` es requisito de entrada a la allowlist; la reversa se implementa junto con la promoción de la acción: p.ej. consolidación KB → archivar el bloque consolidado y restaurar el anterior).
4. UI: en el tab "Estado del Agente Vivo", sección de niveles por acción del workspace (qué hace solo, qué propone, qué notifica) — transparencia total al usuario.
5. HumanAlignmentScore operativo: muestreo semanal (el ciclo ambiental selecciona N ejecuciones L3 al azar → item WorkLoom "califica esta acción" con feedback tipificado) alimentando el score.

**Archivos:** `autonomy.py`, `orchestrator.py` (rutas L3 + notificación), `workloom.py` (tipo auto_executed + revert), `app.jsx` (tab estado + calificación), migración vN+1 si hace falta (preferir tablas existentes).
**Tests:** `test_e7_1_l3_allowlist.py` (fuera de allowlist jamás L3; externo jamás L3 — Regla Sagrada test explícito), `test_e7_1_revert.py` (toda acción L3 revierte limpio), `test_e7_1_degradation.py` (reversión humana degrada la acción), `test_e7_1_alignment_sampling.py`.
**DoD:** ≥2 acciones internas corriendo en L3 en dogfood con 0 reversiones no intencionales durante 2 semanas. **Esfuerzo:** 3 sesiones Fugu + 2 semanas operación.

### E7-2 — CAPA 2: aprendizaje organizacional

**Objetivo:** lo que un usuario enseñó al agente puede volverse conocimiento del tenant — con comité, no por ósmosis.

**Tareas:**
1. Implementar la transición de `ENT_FB_USER_LEARNING_MODEL_v1 §5`: desde la vista de memorias CAPA 1, el usuario u owner propone "elevar a organizacional" → cola de revisión del comité (owner+curador, roles de `ENT_FB_COMMITTEE_OPERATING_MODEL_v1`) → aprobación de AMBOS roles (second-gate, patrón gold existente: `verified_by ≠ approved_by`) → el bloque se copia al namespace `living_agent/{tenant}/shared/{dominio}` con `approved_by` y visibilidad elegida.
2. Reglas duras (spec §7 del learning model): NUNCA auto-elevación; la memoria personal original queda intacta (la copia org es independiente); rollback org no toca la personal; CEO-only respeta visibilidad.
3. Conflictos: si una memoria org contradice una personal, la PERSONAL gana para ese usuario (su corrección es más específica) y el conflicto se reporta como candidato de revisión — decisión DA7-6, documentada en el doc de la KB.
4. UI: cola del comité (vista para owner/curador), badge en memorias elevadas, historial de decisiones.
5. Actualizar `ENT_FB_USER_LEARNING_MODEL` → v2 documentando la implementación real (as-built) con changelog.

**Archivos:** `living_agent/memory.py` (elevación+conflictos), `api.py` (cola comité), `app.jsx` (vistas), `docs/faberloom/ENT_FB_USER_LEARNING_MODEL_v2.md`.
**Tests:** `test_e7_2_capa2_second_gate.py` (dos roles distintos obligatorios), `test_e7_2_capa2_privacy.py` (personal intacta; org respeta visibilidad; cross-tenant imposible), `test_e7_2_conflict_resolution.py` (personal gana + reporte).
**DoD:** flujo completo en dogfood: una corrección personal elevada por el comité cambia el comportamiento para OTRO usuario del tenant. **Esfuerzo:** 2-3 sesiones Fugu.

### E7-3 — Eval arena (el freno de mano)

**Objetivo:** replay determinista que mide skills y acciones ANTES de subirles autonomía y en cada release.

**Tareas:**
1. Implementar sobre `SPEC_FB_EVAL_ARENA_v1`: `app/src/eval_arena.py` — corre un `replay set` (casos congelados: input + output esperado + criterios) contra la versión actual de un skill/acción, con proveedores MOCKEADOS por cassettes (respuestas grabadas; cero costo LLM en CI) y scoring por criterios (exactitud de campos citados, formato, HITL disparado cuando debe).
2. Replay sets iniciales: (a) `ENT_FB_RFQ_REPLAY_SET_v1` de la KB (ya existe como datos), (b) los golden cases approved+verified de PACK 1/3 (reutilizarlos como replays automáticos — ya son casos congelados con evidencia), (c) 5 casos del flujo canónico del agente (facturas-Colombia y variantes).
3. Integración: comando `python -m app.src.eval_arena run --set <name>` + job de CI que corre la arena en cada PR que toque `living_agent/`, `skills*`, `routing/` — regresión de arena = PR bloqueado (GitHub Actions en `.github/`).
4. Gate de autonomía: `evaluate_action_promotion` (E7-1) y `promote_pack` exigen arena verde del set correspondiente como precondición adicional.

**Archivos:** `app/src/eval_arena.py`, `app/tests/replay_sets/` (datos), `.github/workflows/eval_arena.yml`, hooks en `autonomy.py`/`skills.py`.
**Tests:** `test_e7_3_arena_engine.py` (scoring determinista; cassettes sin red; caso que degrada falla el run), `test_e7_3_arena_gates.py` (promoción bloqueada sin arena verde).
**DoD:** arena corriendo en CI; los 3 sets iniciales verdes; primera promoción L3 pasó por arena. **Esfuerzo:** 3 sesiones Fugu.

### E7-4 — Consolidación asistida del termómetro

**Objetivo:** el modal "Indexar Aprendizaje" (E4-5) pasa de listar candidatos a proponer consolidaciones redactadas listas para editar/confirmar — el agente hace el borrador del aprendizaje, el humano decide.

**Tareas:**
1. En `living_agent/memory.py`: al abrir el modal, un paso de modelo barato agrupa los eventos no consolidados en propuestas redactadas (patrón detectado, regla sugerida, gold candidate con preview) — usando el planner/presupuesto existente; costo a `living_agent.learning`.
2. Acciones del modal sin cambios (Confirmar/Editar/Descartar — jamás auto). Confirmar escribe a CAPA 1; la elevación a CAPA 2 sigue el flujo E7-2.
3. Métricas: tasa de confirmación de propuestas (si <30% sostenido, el detector se recalibra — umbral en constants).

**Tests:** `test_e7_4_assisted_consolidation.py` (propuesta redactada desde eventos sintéticos; nada se escribe sin confirmar; presupuesto respetado).
**DoD:** en dogfood, ≥50% de las consolidaciones semanales se hacen vía propuestas asistidas. **Esfuerzo:** 1-2 sesiones Fugu.

### E7-5 — Natural por default (condicionado a dato)

**Objetivo:** los tenants nuevos nacen con el routing inteligente.

**Tareas:** cuando ≥5 tenants hayan corrido `natural` 30 días sin degradación automática (dato del `planner_decision_log` agregado): cambiar el default de `routing.mode` a `natural` SOLO para tenants nuevos (bootstrap seed), manteniendo `manual` como opción visible; los existentes no cambian sin su acción. Documentar en `ENT_PLAT_LLM_ROUTING` (append + changelog). Test: `test_e7_5_default_natural_new_tenants.py`.
**DoD:** condición de dato cumplida y default cambiado; tenants existentes intactos. **Esfuerzo:** ½ sesión Fugu (el trabajo es esperar el dato).

### E7-6 — Acta y cierre

Contamination + arena completas verdes; `docs/audits/ACTA_ETAPA7_<fecha>.md`; merge a main + tag `e7-cierre` + deploy desde main; bloques KB actualizados (IDX, ENT_GOB_PENDIENTES, ARCH_FB_LIVING_AGENT → v2 con L3/CAPA 2).

## §3. Riesgos P0

| Riesgo | Mitigación |
|---|---|
| L3 ejecuta algo externo | Allowlist corta + test explícito de Regla Sagrada + ActionSpec.scope gate + arena |
| Acción L3 sin reversa limpia | Reversibilidad es REQUISITO de entrada a la allowlist; test por acción |
| CAPA 2 propaga un error personal a todo el tenant | Second-gate de dos roles + rollback org independiente + conflicto lo gana la personal |
| Prompt injection escala con la autonomía (84% éxito en sistemas agénticos, per spec ACE) | Arena incluye casos adversariales; contenido=datos en todo el pipeline; muestreo de alignment |
| La arena se vuelve teatro (sets triviales) | Los sets nacen de casos REALES (golden verificados + RFQ replay); cada incidente de producción agrega su caso al set |

## §4. Gate de salida

≥2 acciones L3 estables 30 días con 0 reversiones no intencionales; CAPA 2 operando con ≥5 elevaciones aprobadas en tenants reales; arena en CI bloqueando regresiones; natural default para nuevos (o su condición de dato documentada como no alcanzada aún — en cuyo caso E7 cierra y E7-5 pasa a operación continua); acta commiteada.

## Changelog

- v1.0.0 (2026-07-12): Creación. Decisiones DA7-1..DA7-6; arena como precondición de toda subida de autonomía.
