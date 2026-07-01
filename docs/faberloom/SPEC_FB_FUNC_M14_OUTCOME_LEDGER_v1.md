# SPEC_FB_FUNC_M14_OUTCOME_LEDGER_v1 -- Ficha Funcional Outcome Ledger y Aprendizaje
id: SPEC_FB_FUNC_M14_OUTCOME_LEDGER_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: SCH_FB_FUNCTIONAL_SPEC_v1.md - SPEC_FB_FUNC_M13_DRAFT_HITL_v1.md - SPEC_FB_FUNC_M10_L1_CLASSIFIER_v1.md - ENT_FB_CURATOR_OPERATING_MODEL_v1.md - ENT_FB_USER_LEARNING_MODEL_v1.md

---

## CABECERA DE FICHA

MODULO: Outcome Ledger y aprendizaje (gold sample pipeline)
SUPERFICIE: Backend / Web (tab Aprendizaje, Curator) / Desktop (senales)
SPRINT E1: S1B (ledger) -> S3 (promocion gold + thermometer)
ROLES QUE LO USAN: Owner/Admin (Curator), Supervisor (segundo aprobador N2+); Operator genera senales
DATA CLASS TIPICA: N2 (decisiones sobre outputs del tenant)

---

## DIMENSION 1 -- EXISTENCIA

### 1.1 Por que existe
Cada vez que un humano aprueba, edita o rechaza un draft genera una senal valiosa
que, sin registro estructurado, se pierde. Sin Outcome Ledger, FaberLoom no puede
mejorar: repetiria los mismos errores y nunca convertiria buenas decisiones en
gold samples. El Owner lo siente cuando el sistema "no aprende" de sus correcciones.

### 1.2 A quien le duele
Owner/Admin (Curator): necesitan datos para decidir que promover a gold. Operator:
sus decisiones deberian mejorar al agente, no evaporarse. Supervisor (E3+):
segundo aprobador para promociones N2+.

### 1.3 Cuando aparece
Cada vez que se cierra una decision humana sobre un draft (M13): aprobacion,
edicion (con diff) o rechazo (con razon).

---

## DIMENSION 2 -- PROPOSITO

### 2.1 Para que
Registrar cada decision humana sobre un output y alimentar el ciclo de aprendizaje
(Learning Thermometer + gold sample pipeline).

### 2.2 Que valor entrega
Convierte la operacion diaria en mejora del sistema; mide la madurez del
aprendizaje por agente/skill (thermometer); produce gold samples validados que
suben la calidad y bajan el costo.

### 2.3 Que pasa si no existe
No hay mejora con el tiempo; las correcciones humanas no retroalimentan; no hay
base para promover skills de shadow a active con evidencia.

---

## DIMENSION 3 -- CREACION

### 3.1 Como se crea
N/A manual: cada decision HITL (M13) escribe una entrada en el ledger con:
output_id, decision (approved/edited/rejected), diff (si edito), razon (si aplica),
confidence original, actor_role, tiempo de decision, timestamp.

### 3.2 Quien puede crearlo
El sistema escribe la entrada. El Curator (Owner/Admin) crea promociones de gold
sample a partir de candidatos.

### 3.3 Que necesita para crearse
Una decision HITL cerrada (M13); el confidence original del output; el evidence
bundle de referencia.

---

## DIMENSION 4 -- USO DIARIO

### 4.1 Como se usa en el dia a dia
El ledger se llena solo con cada decision. El Curator entra al tab Aprendizaje
(web) a revisar candidatos a gold sample y el estado del thermometer por agente.

### 4.2 Como se invoca
Escritura: automatica desde M13. Revision: tab Aprendizaje (web). Senales de
thermometer: visibles en el panel de agente del Workspace.

### 4.3 Que ve el usuario mientras ocurre
Learning Thermometer por agente: Cold (0-2) / Warm (3-5) / Hot (6+). Lista de
candidatos CANDIDATE con su diff y confidence. Para promover: vista de diff +
checks de validacion + boton aprobar (con segundo aprobador si N2+).

---

## DIMENSION 5 -- EDICION

### 5.1 Como se edita
Las entradas del ledger no se editan (registro factual). Lo editable es el estado
de un gold sample candidato: CANDIDATE -> ACTIVE (promocion) o descartado.

### 5.2 Que se puede cambiar y que no
Editable: estado del gold sample (candidate/active/deprecated). No editable: la
entrada original del ledger (decision, diff, timestamp, actor).

### 5.3 Que pasa con lo generado previamente
Promover un gold sample no reescribe el ledger: agrega un registro de promocion.
Revertir un gold sample malo (ver 10) lo marca deprecated, no borra su historia.

---

## DIMENSION 6 -- MOVIMIENTO Y ESTADO

### 6.1 Como se mueve
State machine del gold sample:
```
(decision HITL) -- trigger: aprobado sin edicion + confidence HIGH, actor: system --> CANDIDATE
CANDIDATE -- trigger: Curator revisa + pasa validaciones, actor: Curator --> ACTIVE
CANDIDATE -- trigger: Curator descarta, actor: Curator --> discarded
ACTIVE -- trigger: gold sample resulta malo, actor: Curator --> deprecated
ACTIVE -- trigger: requiere segundo aprobador (N2+) faltante --> blocked_pending_second_approver
```

### 6.2 Que dispara el movimiento
Decision HITL HIGH-confidence (a CANDIDATE); revision del Curator + validaciones (a
ACTIVE); descarte; deteccion de gold malo (a deprecated).

### 6.3 Quien puede moverlo
system: crea CANDIDATE. Curator (Owner/Admin): promueve/descarta/depreca. Para
N2+: se requiere un segundo aprobador (Supervisor/otro Admin).

### 6.4 Que se notifica y a quien
Nuevo candidato: badge en tab Aprendizaje. Promocion a ACTIVE: log + notificacion
al Curator. Gold malo revertido: alerta al Curator + nota a los agentes afectados.

---

## DIMENSION 7 -- OUTPUT

### 7.1 Que produce para el usuario
Learning Thermometer por agente (Cold/Warm/Hot); lista de candidatos a gold;
historial de promociones; visibilidad de que tan "maduro" esta cada agente.

### 7.2 Que produce para el sistema
Entrada en el Outcome Ledger por cada decision; gold samples ACTIVE que alimentan
a los skills/classifier (M10); eventos de promocion; audit D10 de cada promocion
(con diff y aprobadores).

### 7.3 Donde aparece el output
Tab Aprendizaje (web); panel de agente (Workspace); pipeline de gold samples;
audit log.

### 7.4 Que formato tiene
Entrada de ledger (JSON: decision, diff, razon, confidence, actor, tiempo); gold
sample (input/output canonico + metadata de validacion); eventos canonicos.

---

## DIMENSION 8 -- ERRORES Y EXCEPCIONES

### 8.1 Que pasa si falla
Promocion sin segundo aprobador (N2+): bloqueada en
blocked_pending_second_approver hasta que un segundo rol apruebe. Validacion
fallida (schema/policy/replay/scope): la promocion se rechaza con el detalle del
check que fallo. Gold sample malo ya ACTIVE: se detecta por regresion o por
quejas; se revierte (ver 10). Escritura del ledger fallida: via outbox (M15) para
no perder la senal.

### 8.2 Como se recupera
Conseguir el segundo aprobador; corregir el candidato y re-validar; revertir el
gold malo a deprecated y re-evaluar los outputs que genero.

### 8.3 Quien se entera
Curator (Owner/Admin): candidatos, validaciones, reversiones. Supervisor: cuando
es segundo aprobador. Langfuse/Grafana: metricas de promocion/regresion.

---

## DIMENSION 9 -- APRENDIZAJE

### 9.1 Que aprende el sistema de este uso
Tasa de aprobacion sin edicion por agente (madurez); tipos de edicion mas
frecuentes (donde el agente falla); razones de rechazo; tiempo de decision
(complacencia).

### 9.2 Como mejora con el tiempo
El Learning Thermometer sube de Cold a Hot conforme se acumulan decisiones
limpias; los gold samples ACTIVE mejoran prompts/clasificador; los patrones de
edicion sugieren ajustes de skill. Ciclo de promocion: output aprobado sin edicion
+ HIGH confidence -> CANDIDATE -> Curator revisa -> ACTIVE. Validaciones antes de
ACTIVE: schema validation, policy check, replay regression, scope check, aprobacion
humana con diff. Para N2+: segundo aprobador obligatorio.

### 9.3 Que feedback da el usuario
Implicito: cada decision HITL. Explicito: el Curator aprueba/descarta candidatos
con su criterio; el segundo aprobador valida N2+.

---

## DIMENSION 10 -- ELIMINACION

### 10.1 Como se elimina
Las entradas del ledger no se borran. Un gold sample malo se revierte: se marca
deprecated, sale del pipeline activo, y se re-evaluan los outputs que pudo haber
influido. Reversion de un gold sample malo = deprecate + nota de causa + revision
de impacto, nunca borrado silencioso.

### 10.2 Que pasa con lo que dependia
Al deprecar un gold sample, el skill/classifier deja de usarlo; si genero outputs
cuestionables, se marcan para revision. Las entradas del ledger asociadas quedan.

### 10.3 Es reversible
Deprecar un gold sample es reversible (re-promover si se confirma que era bueno,
con nueva validacion). Las entradas del ledger son inmutables.

---

## DIMENSION 11 -- RELACIONES

### 11.1 Con que se relaciona
Recibe de: M13 (decisiones HITL + diffs), M10 (correcciones de clasificacion).
Alimenta a: skills/classifier (gold samples ACTIVE), Learning Thermometer, Curator
(ENT_FB_CURATOR_OPERATING_MODEL), UserControlProfile (ENT_FB_USER_LEARNING_MODEL).
Depende de: M15 (eventos/outbox), M12 (audit de promociones).

### 11.2 En que orden
M13 decide -> Outcome Ledger registra -> (HIGH+sin edicion) CANDIDATE -> Curator +
validaciones -> ACTIVE -> mejora M10/skills. Reversion cuando se detecta gold malo.

### 11.3 Que rompe si este modulo falla
Sin ledger no hay aprendizaje ni gold samples; los skills no maduran; el
thermometer no existe; la autonomia nunca se "gana" (M17/autonomy ladder).

---

## DIMENSION 12 -- COMPLIANCE Y SEGURIDAD

### 12.1 Quien puede verlo
Curator (Owner/Admin): ledger y candidatos del tenant. Supervisor: lo que aprueba.
Operator: sus propias senales. Nunca cross-tenant: gold samples y ledger scoped por
tenant (la promocion cross-tenant, si existe, pasa por k-anon, fuera de E1).

### 12.2 Que queda en el audit trail D10
tenant_id, case_id, output_id, action (gold.candidate.created / gold.promoted /
gold.deprecated), diff_hash, confidence, human_approver_id (Curator),
second_approver_id (si N2+), data_class, timestamp, sha_chain. Cada promocion se
audita con su diff.

### 12.3 Que restricciones de datos aplican
Validaciones obligatorias antes de ACTIVE (schema/policy/replay/scope + aprobacion
humana con diff); segundo aprobador para N2+; gold samples scoped por tenant; el
contenido sensible se referencia por hash en audit; RLS (M16).

---

## DIMENSION 13 -- DESKTOP vs WEB

### 13.1 En cual superficie vive
Backend (el ledger). Web: tab Aprendizaje del Curator (revision y promocion).
Desktop: las senales se generan al decidir (M13) y el thermometer se ve en el
panel de agente del Workspace.

### 13.2 Diferencias entre desktop y web
Web: promocion de gold, validaciones, segundo aprobador. Desktop: generacion de
senales y visualizacion del estado de aprendizaje; no se promueve gold desde
desktop en E1.

### 13.3 Offline y sincronizacion
Las senales se generan al cerrar una decision HITL (que requiere conexion, M13).
La promocion de gold es server-side. Offline no se promueve ni se valida.

---

## PENDIENTES que requieren decision CEO

1. [PENDIENTE -- ENT_FB_USER_LEARNING_MODEL_v1] Confirmar los umbrales exactos del
   Learning Thermometer (Cold 0-2 / Warm 3-5 / Hot 6+) y que cuenta como "1".
2. [PENDIENTE -- ENT_FB_CURATOR_OPERATING_MODEL_v1] Definir quien puede ser segundo
   aprobador para N2+ (Supervisor, otro Admin, CEO).
3. [PENDIENTE] Definir el criterio automatico que marca un gold sample ACTIVE como
   "malo" (regresion, tasa de edicion posterior, quejas).

## CONTRADICCIONES DETECTADAS CON LA KB

1. Sin contradicciones nuevas detectadas. El ciclo CANDIDATE -> Curator -> ACTIVE y
   el segundo aprobador N2+ son consistentes con el modelo de Curator existente.

---

Changelog:
- v1.0 (2026-06-24): Creacion. Ficha funcional 13 dimensiones del Outcome Ledger.
  Learning Thermometer Cold/Warm/Hot; pipeline gold sample CANDIDATE->ACTIVE con 5
  validaciones; segundo aprobador N2+; reversion de gold malo.
