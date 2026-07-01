# SPEC_FB_FUNC_M10_L1_CLASSIFIER_v1 -- Ficha Funcional L1 Classifier
id: SPEC_FB_FUNC_M10_L1_CLASSIFIER_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: SCH_FB_FUNCTIONAL_SPEC_v1.md - SPEC_FB_ROUTING_PRESETS_v1.md - ENT_FABERLOOM_INSIGHTS_FUGU_SESSION.md (FG-03) - SPEC_FB_FUNC_M11_D9_POLICY_GATE_v1.md - SPEC_FB_FUNC_M13_DRAFT_HITL_v1.md - SCH_FB_TASK_ENTITY.md

---

## CABECERA DE FICHA

MODULO: L1 Classifier (Action Engine -- Tier 0 + L1)
SUPERFICIE: Backend / Desktop (WorkLoom, modo resultado/debug)
SPRINT E1: S1B (Action Engine ejecutor + L1)
ROLES QUE LO USAN: Operator (recibe outcome), Owner/Admin (configura/clona)
DATA CLASS TIPICA: hereda del inbound (N2 default)

---

## DIMENSION 1 -- EXISTENCIA

### 1.1 Por que existe
Sin L1 el sistema no sabe que skill activar ante un inbound. Cuando Maria recibe
un mensaje, FaberLoom no distingue si es RFQ, spam, consulta de stock, follow-up
o newsletter. El L1 classifier transforma un mensaje crudo en una decision de
routing accionable con un confidence que decide si va auto o a revision humana.

### 1.2 A quien le duele
Operator: recibe items bien o mal enrutados. Owner: configura/ajusta el
classifier para que la operacion sea confiable. Supervisor (E3+): mide calidad
de clasificacion.

### 1.3 Cuando aparece
Se ejecuta automaticamente por cada feed_item recibido, inmediatamente despues
del Tier 0 deterministico y antes de crear cualquier task.

---

## DIMENSION 2 -- PROPOSITO

### 2.1 Para que
Determinar task_type + data_class + skill_id/agent_id de destino con un
confidence, routing y SLA, para decidir auto-routing vs revision humana.

### 2.2 Que valor entrega
Reduce el triage manual; aplica politicas de datos (D9, M11) antes de invocar
cualquier skill; habilita routing automatico a @cotizador, @stock_curator, etc.

### 2.3 Que pasa si no existe
Maria lee cada inbound y decide manualmente que agente/skill usar; se pierde
escalabilidad y sube el error humano.

---

## DIMENSION 3 -- CREACION

### 3.1 Como se crea
El L1 es un componente del engine. En E1 existe como skill system `classify_rfq`
seedeada en el bootstrap (origin=system, inmutable). Si el tenant necesita
variantes, Owner/Admin clonan el skill en Skill Factory y ajustan prompt/schema/
threshold dentro de los limites duros TIER 1.
Los 13 features de entrada del L1 (FG-03, fuente ENT_FABERLOOM_INSIGHTS_FUGU_SESSION):
1. task_type_confidence, 2. schema_parse_success, 3. num_documents,
4. num_counterparties, 5. jurisdiction_count, 6. data_class, 7. tenant_risk_tier,
8. estimated_tokens, 9. expected_latency, 10. business_value,
11. validator_failure_count, 12. prior_case_similarity, 13. requires_human_gate.

### 3.2 Quien puede crearlo
System lo seedea en bootstrap. Owner/Admin clonan/editan skills L1 en Skill
Factory (con sandbox obligatorio antes de promote).

### 3.3 Que necesita para crearse
Engine ejecutor genérico operativo (S1B); skill system `classify_rfq` seed; KB
del tenant con el work-type pack cargado.

---

## DIMENSION 4 -- USO DIARIO

### 4.1 Como se usa en el dia a dia
1. Llega un inbound. 2. Action Engine aplica P14 Deterministic First: reglas
Tier 0 intentan clasificar sin LLM. 3. Si Tier 0 no cubre o confidence < threshold,
escala a L1 (Haiku 4.5) usando los 13 features. 4. L1 produce un ActionContext
(task_type, data_class N0-N4, skill_id/agent_id, confidence 0-1, routing/zona,
SLA). 5. Si confidence >= 0.85 (threshold default): enruta automaticamente.
6. Si confidence < 0.85: pending_human_review en Zona 4.

### 4.2 Como se invoca
Automatico por el Action Engine en cada inbound. Manual desde Workspace:
"@router clasifica este correo".

### 4.3 Que ve el usuario mientras ocurre
Maria no ve la ejecucion interna; ve el resultado: card en Zona 4 con tipo,
confidence HIGH/LOW, SLA restante. En modo Owner/debug puede expandir "Ver como
clasifico" con el ActionContext y el aporte de cada feature.

---

## DIMENSION 5 -- EDICION

### 5.1 Como se edita
Operator: corrige la clasificacion de un item desde el detalle del feed item.
Owner/Admin: clonan `classify_rfq` y ajustan prompt template, schema output,
threshold de confidence, modelo (Haiku/Sonnet), timeout/cost cap. Sandbox
obligatorio antes de promote.

### 5.2 Que se puede cambiar y que no
Editable en skill clonado: prompt, schema, threshold, modelo, timeout, cost cap
(dentro de hard caps). No editable: el skill system sellado (solo clonable); el
log de confianza original; el contenido analizado; el model fingerprint.

### 5.3 Que pasa con lo generado previamente
Corregir un item: la task anterior se cancela (`reclassified`), se crea nueva
task, evento `pattern.candidate.detected`, diff al Outcome Ledger (M14). Editar
el skill: solo afecta items nuevos; los ya clasificados no se re-procesan salvo
re-clasificacion batch forzada por Owner.

---

## DIMENSION 6 -- MOVIMIENTO Y ESTADO

### 6.1 Como se mueve
State machine del classifier:
```
idle -- trigger: feed_item recibido, actor: system --> classifying
classifying -- trigger: Tier 0 match --> classified
classifying -- trigger: Tier 0 no match, LLM OK --> classified
classifying -- trigger: LLM timeout/error --> failed
classified -- trigger: confidence >= threshold --> routed_to_task
classified -- trigger: confidence < threshold --> pending_human_review
pending_human_review -- trigger: Operator confirma, actor: Operator --> routed_to_task
pending_human_review -- trigger: Operator descarta, actor: Operator --> archived
failed -- trigger: retry OK --> classifying
failed -- trigger: retries agotados --> manual_review
```

### 6.2 Que dispara el movimiento
Automatico: reglas Tier 0, LLM call, threshold de confidence. Manual: correccion
del Operator.

### 6.3 Quien puede moverlo
system: transiciones automaticas. Operator: confirma/clasifica items inciertos.
Owner: ajusta threshold/skill.

### 6.4 Que se notifica y a quien
Item incierto (confidence < threshold): badge Zona 4 + notificacion al Operator.
Clasificacion con data class elevada (N3/N4): alerta a Owner (gate M11). Falla
del classifier: alerta P1 a Owner, DLQ si persiste.

---

## DIMENSION 7 -- OUTPUT

### 7.1 Que produce para el usuario
Card en WorkLoom con tipo de item, confidence HIGH/LOW, SLA y accion primaria
sugerida. En modo Owner: panel "Como clasifico" con el ActionContext y features.

### 7.2 Que produce para el sistema
ActionContext JSON (task_type, data_class, skill_id, agent_id, confidence,
routing, payload_normalizado). Eventos: `feed.item.dispatched`, `task.created`,
`draft.generated` (si aplica), `pattern.candidate.detected` (si se corrige).
Registros en `skill_executions` y `llm_calls`.

### 7.3 Donde aparece el output
WorkLoom Zona 4 (item clasificado); Zona 2 (draft generado); Zona 1 (si urgente);
Outcome Ledger (senales de aprendizaje, M14).

### 7.4 Que formato tiene
ActionContext JSON validado contra el schema del skill; card UI; evento canonico
(SPEC_FB_EVENTING_AND_OUTBOX, M15).

---

## DIMENSION 8 -- ERRORES Y EXCEPCIONES

### 8.1 Que pasa si falla
Confidence < threshold (0.85): item a `pending_human_review`; Maria clasifica
manual. Clasifica mal N2 como N3/N4: D9 hard-block (M11) -> `PlanUpgradeRequired`
o escala a Owner; no se procesa automaticamente. RFQ clasificado como spam: va a
spam folder, recuperable desde filtro "Spam", genera `pattern.candidate.detected`.
LLM timeout/error: 3 reintentos con backoff; fallback a Tier 0 + reglas default;
si no cubre, escala a humano.

### 8.2 Como se recupera
Re-clasificacion manual; ajuste de threshold/prompt en Skill Factory; revision de
reglas Tier 0; promocion de candidatos a reglas/gold samples desde tab
Aprendizaje (M14).

### 8.3 Quien se entera
Operator: items mal ubicados en Zona 4. Owner: alertas de config y metricas.
Sistema: Outcome Ledger, Langfuse traces, DLQ. Nivel: P1 falla del classifier;
P0 si filtra data class por encima del ceiling sin gate.

---

## DIMENSION 9 -- APRENDIZAJE

### 9.1 Que aprende el sistema de este uso
Delta entre clasificacion L1 y correccion humana; confidence vs outcome real;
tiempo de decision; frecuencia de tipos por canal/hora; patrones de spam/false
positive; valor de cada feature en aciertos vs errores.

### 9.2 Como mejora con el tiempo
Ajuste dinamico del threshold segun approval rate; reglas nuevas en Tier 0 cuando
un pattern se repite >=N veces; actualizacion del skill L1 clonado con gold
samples promovidos (M14). El modelo del classifier se versiona (ver 5/12).

### 9.3 Que feedback da el usuario
Implicito: aceptar/editar/rechazar los drafts derivados. Explicito: re-clasificar
+ dropdown de razon (tone/data/structure/policy/scope/context). Owner aprueba/
descarta candidatos en tab Aprendizaje.

---

## DIMENSION 10 -- ELIMINACION

### 10.1 Como se elimina
El L1 es componente del sistema; el skill system `classify_rfq` no se elimina. Un
skill L1 clonado puede pausarse (deja de usarse) o deprecarse (no invocable, queda
en historico). FaberLoom depreca, no borra.

### 10.2 Que pasa con lo que dependia
Si se pausa/depreca un skill L1 clonado, los items usan el skill system default o
el siguiente activo. Las ejecuciones historicas quedan en `skill_executions`.

### 10.3 Es reversible
Pausar es reversible. Deprecar es reversible por Owner si no hay incompatibilidad
de schema.

---

## DIMENSION 11 -- RELACIONES

### 11.1 Con que se relaciona
Recibe de: inbound/feed_item, Action Engine Tier 0. Alimenta a: L2 Dispatcher,
creacion de task, WorkLoom, Outcome Ledger (M14), D9 Policy Gate (M11). Depende
de: Skill Factory (config), KB (contexto), Action Engine (politicas).

### 11.2 En que orden
feed_item -> Tier 0 deterministic -> L1 classifier (13 features) -> ActionContext
-> D9 Policy Gate (M11) -> L2 Dispatcher -> task -> skill execution -> draft (M13).

### 11.3 Que rompe si este modulo falla
Sin L1, todo inbound queda sin clasificar y se acumula en Zona 4; si clasifica
mal, los drafts van al skill/agente equivocado (corregible en HITL pero con
friccion).

---

## DIMENSION 12 -- COMPLIANCE Y SEGURIDAD

### 12.1 Quien puede verlo
Operator: el resultado en su card. Owner/Admin: config del skill, metricas,
debug. Viewer (E3+): solo historial. Todo filtrado por tenant_id (RLS).

### 12.2 Que queda en el audit trail D10
tenant_id, user_id (null si system), actor_role_at_decision (SYSTEM u OPERATOR si
corrige), action (feed.item.dispatched / task.created / pattern.candidate.detected),
resource_id (feed_item_id/task_id), data_class (heredado, N2 tipico),
model_provider (Anthropic), model_id (haiku-4.5), model_version,
human_gate_required (false en clasificacion; true si genera draft),
human_approver_id (null), timestamp, sha_chain.

### 12.3 Que restricciones de datos aplican
P14 Deterministic First (Tier 0 antes que LLM); D9 routing (N3/N4 hard-block si
supera ceiling, M11); skill L1 limitado a tipo classifier (sin tools externas,
sin HTTP, sin code exec, timeout y cost cap acotados, TIER 1); Anthropic-only con
DPA. Donde vive el modelo / versionado / rollback: el skill L1 es markdown
versionado (prompt+schema+threshold) en Skill Factory; cada promote crea version;
rollback = volver a la version ACTIVE previa (shadow->active con sandbox).

---

## DIMENSION 13 -- DESKTOP vs WEB

### 13.1 En cual superficie vive
Backend: la clasificacion ocurre en el servidor. Desktop (WorkLoom): Maria ve el
resultado. Web (Skill Factory): Owner/Admin configuran/clonan el skill L1.

### 13.2 Diferencias entre desktop y web
Desktop: operacion, correccion por item, visualizacion del outcome. Web: config
del skill, sandbox test, promote, historial de versiones.

### 13.3 Offline y sincronizacion
La clasificacion es backend; el desktop recibe el resultado por WebSocket (M15).
Offline no se clasifica; al reconectar se reciben los eventos acumulados (<=24h)
con last_event_id (M19).

---

## PENDIENTES que requieren decision CEO

1. [PENDIENTE -- SPEC_LLM_ROUTING_ARCHITECTURE L1] FG-03 indica agregar los 13
   features al SPEC_LLM_ROUTING en su proximo bump; confirmar pesos/normalizacion
   por feature.
2. [PENDIENTE] Definir donde vive y como se versiona el modelo del classifier si
   en algun momento deja de ser solo prompt-based (ej. un clasificador entrenado).
3. [PENDIENTE -- SPEC_FB_ROUTING_PRESETS_v1] Confirmar interaccion del threshold
   0.85 con el routing de 3 capas (ECU/preset/curva).

## CONTRADICCIONES DETECTADAS CON LA KB

1. "13 features" del prompt: localizados en ENT_FABERLOOM_INSIGHTS_FUGU_SESSION
   FG-03 (no en docs/faberloom). Se usan tal cual; pendiente su indexacion formal
   en SPEC_LLM_ROUTING_ARCHITECTURE.
2. EVAL_ARENA vs routing 3 capas: SPEC_FB_EVAL_ARENA_v1 existe, pero el estado
   actual (memoria de proyecto) indica que routing 3 capas + fabrica de niveles
   reemplaza EVAL_ARENA. La ficha no asume EVAL_ARENA; requiere confirmacion.

---

Changelog:
- v1.0 (2026-06-24): Creacion. Ficha funcional 13 dimensiones del L1 Classifier.
  13 features de FG-03; threshold 0.85; pending_human_review; versionado por
  Skill Factory.
