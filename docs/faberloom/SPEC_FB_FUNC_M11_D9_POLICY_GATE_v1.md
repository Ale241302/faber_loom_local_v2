# SPEC_FB_FUNC_M11_D9_POLICY_GATE_v1 -- Ficha Funcional D9 Policy Gate
id: SPEC_FB_FUNC_M11_D9_POLICY_GATE_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: SCH_FB_FUNCTIONAL_SPEC_v1.md - SPEC_FB_RAG_SECURITY_FIREWALL_v1.md - SPEC_FB_FUNC_M10_L1_CLASSIFIER_v1.md - SPEC_FB_FUNC_M07_BOOTSTRAP_WIZARD_v1.md - SPEC_FB_FUNC_M12_AUDIT_TRAIL_v1.md - POL_FB_KR_PRIVACY_TIERS_v1.md

---

## CABECERA DE FICHA

MODULO: D9 Policy Gate (data classification routing + pre-egress)
SUPERFICIE: Backend (transversal) / Desktop (mensaje de bloqueo)
SPRINT E1: S1B (Action Engine -- D9 policy layer)
ROLES QUE LO USAN: Operator (ve el bloqueo), Owner (desbloquea via DPA)
DATA CLASS TIPICA: opera sobre N0-N4; bloquea N3/N4 sin DPA

---

## DIMENSION 1 -- EXISTENCIA

### 1.1 Por que existe
FaberLoom envia datos a un LLM provider. Sin un gate de politica, un dato N3/N4
(cliente sensible, regulado) podria salir a un provider sin DPA firmado -- una
violacion de privacidad y un kill criteria de E1. El Owner siente el riesgo
cuando un caso roza datos sensibles: necesita que el sistema bloquee solo, no que
dependa de que alguien recuerde la politica.

### 1.2 A quien le duele
Owner: responsable legal del tratamiento de datos del tenant. Operator: ve un
bloqueo y necesita entender por que y como destrabarlo. Platform admin/CEO:
responde por compliance LATAM (LGPD/Ley 1581/Ley 25.326).

### 1.3 Cuando aparece
En cada accion que vaya a enviar datos a un provider o a un canal externo:
despues de la clasificacion L1 (M10) y antes de invocar el skill, y de nuevo como
pre-egress antes de que el output salga.

---

## DIMENSION 2 -- PROPOSITO

### 2.1 Para que
Garantizar que ningun dato por encima del ceiling del plan/tenant se procese o
salga sin el DPA y los controles requeridos, sin excepcion.

### 2.2 Que valor entrega
Cumple TIER 1 (data class routing) y mitiga el riesgo top de fuga regulatoria.
Convierte la politica en un control fail-closed, no en una buena intencion.

### 2.3 Que pasa si no existe
Datos N3/N4 saldrian a un provider sin DPA; incumplimiento de DPA; kill criteria
E1 (>=1 incidente privacy = kill).

---

## DIMENSION 3 -- CREACION

### 3.1 Como se crea
El D9 es una capa de politica del Action Engine, no un objeto de UI. Se configura
en S1B:
1. Definir el ceiling de data class por plan/tenant (`tenant_plan_ceiling`).
2. Registrar el estado del DPA por tenant (firmado/no firmado).
3. Implementar el gate pre-skill: bloquea si data_class > ceiling.
4. Implementar el pre-egress scanner:
   effective_classification = max(declared, source_default, retrieved_chunks,
   pre_egress_detected).
5. Definir `PlanUpgradeRequired` como response canonico del bloqueo.

### 3.2 Quien puede crearlo
Equipo de ingenieria (S1B). El estado del DPA lo habilita el Owner (firma en
wizard, M07 paso 7) + validacion de platform admin.

### 3.3 Que necesita para crearse
Clasificacion data_class del item (M10); registro de DPA por tenant; ceiling por
plan; el pre-egress scanner con acceso al output y a los chunks recuperados.

---

## DIMENSION 4 -- USO DIARIO

### 4.1 Como se usa en el dia a dia
Transparente cuando todo esta en regla: el caso N0-N2 pasa el gate y se procesa.
Cuando aparece un dato N3/N4 sin DPA, el gate bloquea y el item se detiene con un
mensaje claro al Operator.

### 4.2 Como se invoca
Automatico: el Action Engine llama al gate antes de invocar el skill y el
pre-egress scanner antes de emitir el output. No es invocable manualmente.

### 4.3 Que ve el usuario mientras ocurre
Caso normal: nada (pasa silencioso). Caso bloqueado: card con badge "Bloqueado
por politica de datos" + explicacion ("este caso contiene datos N3 y el tenant no
tiene DPA firmado para procesarlos") + accion sugerida ("firmar DPA" si es Owner;
"escalar al Owner" si es Operator). Nunca un boton de override.

---

## DIMENSION 5 -- EDICION

### 5.1 Como se edita
La politica no se edita por caso. Se cambia el estado habilitante: el Owner firma
el DPA (M07) -> sube el ceiling efectivo del tenant para N3. El ceiling del plan
se cambia con upgrade de plan.

### 5.2 Que se puede cambiar y que no
Editable: estado del DPA (firma), plan/ceiling del tenant. No editable: la regla
de hard-block (sellada, sin override CEO ni bypass); la formula de
effective_classification; el comportamiento fail-closed.

### 5.3 Que pasa con lo generado previamente
Firmar el DPA no desbloquea retroactivamente outputs ya bloqueados de forma
silenciosa: los items bloqueados se reprocesan explicitamente. Un bloqueo pasado
queda en audit aunque luego se firme el DPA.

---

## DIMENSION 6 -- MOVIMIENTO Y ESTADO

### 6.1 Como se mueve
State machine del gate por item:
```
evaluating -- trigger: data_class <= ceiling, actor: system --> passed
evaluating -- trigger: data_class > ceiling sin DPA, actor: system --> blocked (PlanUpgradeRequired)
blocked -- trigger: Owner firma DPA / upgrade de plan, actor: Owner --> re_evaluating
re_evaluating -- trigger: ahora data_class <= ceiling --> passed
passed -- trigger: pre-egress detecta clase mayor, actor: system --> blocked (ClassificationMismatch)
```

### 6.2 Que dispara el movimiento
Evaluacion pre-skill; firma de DPA/upgrade; deteccion del pre-egress scanner.

### 6.3 Quien puede moverlo
system: evalua y bloquea. Owner: habilita (DPA/plan). Nadie puede forzar `passed`
sin cumplir la condicion (no hay override).

### 6.4 Que se notifica y a quien
Bloqueo N3/N4: badge al Operator + alerta al Owner con motivo y como destrabar.
ClassificationMismatch (dato ya salio): alerta P0 a Owner + platform admin +
runbook (ver 8).

---

## DIMENSION 7 -- OUTPUT

### 7.1 Que produce para el usuario
Caso permitido: el flujo continua. Caso bloqueado: mensaje claro de bloqueo con
motivo y ruta de desbloqueo (firmar DPA / upgrade), sin opcion de override.

### 7.2 Que produce para el sistema
Response `PlanUpgradeRequired` (bloqueo) o paso al siguiente stage. Evento
`policy.gate.blocked` / `policy.gate.passed`; en pre-egress mismatch,
`policy.classification_mismatch`. Audit D10 obligatorio con la decision del gate.

### 7.3 Donde aparece el output
WorkLoom (card de bloqueo, Zona 1 si urgente); audit log; logs de compliance.

### 7.4 Que formato tiene
Response canonico JSON (`PlanUpgradeRequired` con motivo y clase detectada);
evento canonico con SHA-chain; entrada de audit.

---

## DIMENSION 8 -- ERRORES Y EXCEPCIONES

### 8.1 Que pasa si falla
Dato N3/N4 sin DPA: hard-block, `PlanUpgradeRequired`, item detenido y escalado
al Owner. Pre-egress detecta una clase mayor que la declarada
(ClassificationMismatch): si el dato AUN no salio, se bloquea; si YA salio al
provider, se dispara el runbook (8.2). El gate falla-closed: si el scanner no
puede evaluar, bloquea (no deja pasar por duda).

### 8.2 Como se recupera
Bloqueo por falta de DPA: el Owner firma el DPA (wizard S10/M07) o sube de plan;
el item se re-evalua explicitamente. Runbook ClassificationMismatch (datos ya
salieron a provider): 1. Marcar el caso como incidente P0. 2. Identificar que
chunks/datos salieron y a que provider. 3. Verificar el DPA/no-training del
provider para ese dato. 4. Solicitar deletion al provider segun DPA. 5. Notificar
al Owner y registrar en el registry de incidentes. 6. Ajustar la clasificacion de
la fuente que subdeclaro para que no se repita.

### 8.3 Quien se entera
Operator: el bloqueo. Owner: motivo + ruta de desbloqueo. Platform admin/CEO +
auditor: ClassificationMismatch (P0). Langfuse/Grafana: tasa de bloqueos.

---

## DIMENSION 9 -- APRENDIZAJE

### 9.1 Que aprende el sistema de este uso
Frecuencia de bloqueos por tipo de dato; fuentes que subdeclaran clasificacion
(detectadas por el pre-egress); tenants que chocan seguido contra el ceiling.

### 9.2 Como mejora con el tiempo
Ajusta los defaults de clasificacion de fuentes que reincidieron en mismatch;
sugiere al Owner upgrade/DPA cuando el patron de bloqueos lo justifica. La regla
de bloqueo no se relaja con el aprendizaje.

### 9.3 Que feedback da el usuario
Implicito: el Owner firma DPA o sube plan ante bloqueos recurrentes. Explicito:
reporte de falso positivo de clasificacion (revisa el default de la fuente, no
abre bypass).

---

## DIMENSION 10 -- ELIMINACION

### 10.1 Como se elimina
El gate D9 no se elimina ni se desactiva: es un control fail-closed permanente.
Solo cambian sus entradas (DPA, ceiling).

### 10.2 Que pasa con lo que dependia
N/A -- es infraestructura de politica; todo el procesamiento depende de pasar el
gate.

### 10.3 Es reversible
N/A -- no se puede apagar.

---

## DIMENSION 11 -- RELACIONES

### 11.1 Con que se relaciona
Depende de: M10 (data_class del item), registro de DPA (M07), RAG security
firewall (chunks recuperados), ceiling de plan. Alimenta a: skill execution
(solo si pasa), M12 (audit del gate), M07 (la firma de DPA lo habilita).

### 11.2 En que orden
M10 clasifica -> D9 gate pre-skill -> (si pasa) skill execution -> pre-egress
scanner -> (si pasa) egress del output. El DPA del wizard (M07) habilita N3.

### 11.3 Que rompe si este modulo falla
Si el gate se cae abierto, datos sensibles podrian salir sin DPA -> kill criteria.
Por eso es fail-closed: si no puede evaluar, bloquea.

---

## DIMENSION 12 -- COMPLIANCE Y SEGURIDAD

### 12.1 Quien puede verlo
Operator: el bloqueo de sus items. Owner/platform admin: politica, estado de DPA,
incidentes. Auditor: log completo de decisiones del gate. Nunca cross-tenant.

### 12.2 Que queda en el audit trail D10
tenant_id, case_id, action (policy.gate.blocked / policy.gate.passed /
policy.classification_mismatch), data_class (declarada y effective),
model_provider/model_id, human_gate_required, human_approver_id (Owner si firma),
timestamp, sha_chain. Todo bloqueo y todo mismatch quedan registrados.

### 12.3 Que restricciones de datos aplican
N3/N4 hard-block sin DPA; sin override CEO ni bypass de ningun tipo;
effective_classification = max(declared, source_default, retrieved_chunks,
pre_egress_detected); Anthropic-only con DPA; comportamiento fail-closed.

---

## DIMENSION 13 -- DESKTOP vs WEB

### 13.1 En cual superficie vive
Backend (el gate corre en el servidor, transversal). Desktop: muestra el mensaje
de bloqueo al Operator. Web: el Owner ve el estado de DPA/plan y firma el DPA.

### 13.2 Diferencias entre desktop y web
Desktop: solo consume el resultado (bloqueo/paso). Web: gestion del habilitante
(DPA, plan) y revision de incidentes.

### 13.3 Offline y sincronizacion
El gate corre server-side; offline no se procesa nada que requiera el gate. No
hay evaluacion de politica en cliente (no se puede confiar al cliente la decision
de compliance).

---

## PENDIENTES que requieren decision CEO

1. [PENDIENTE -- POL_FB_KR_PRIVACY_TIERS_v1 / POL_DATA_CLASSIFICATION] Confirmar el
   mapeo exacto N0-N4 -> ceiling por plan/tier.
2. [PENDIENTE] Definir el provider de deletion-on-request y el SLA del runbook
   ClassificationMismatch.
3. [PENDIENTE -- SPEC_FB_RAG_SECURITY_FIREWALL_v1] Confirmar como el pre-egress
   scanner detecta clase en chunks recuperados (heuristica vs modelo).

## CONTRADICCIONES DETECTADAS CON LA KB

1. Sin contradicciones nuevas detectadas. El hard-block N3/N4 sin override es
   consistente con TIER 1 y con el kill criteria de privacy de E1.

---

Changelog:
- v1.0 (2026-06-24): Creacion. Ficha funcional 13 dimensiones del D9 Policy Gate.
  Hard-block N3/N4 sin DPA, PlanUpgradeRequired, pre-egress scanner con
  effective_classification, runbook ClassificationMismatch, fail-closed.
