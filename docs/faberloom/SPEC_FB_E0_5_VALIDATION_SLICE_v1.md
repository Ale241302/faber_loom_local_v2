# SPEC_FB_E0_5_VALIDATION_SLICE_v1 -- Secuencia de Validacion pre-build (interno-primero)
id: SPEC_FB_E0_5_VALIDATION_SLICE_v1
version: 1.1
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE -- 2026-06-25 -- v1.1 endurecida por triple filtro (Claude+Kimi+Fugu); scope interno-primero
aprobador: CEO
aplica_a: [FaberLoom, MWT]
relacionado: PLAN_DESARROLLO_FABERLOOM_v6.md - EVAL_E0_5_VALIDATION_KIMI.md - EVAL_E0_5_VALIDATION_FUGU_ULTRA.md - SPEC_FB_FUNC_M10_L1_CLASSIFIER_v1.md - SPEC_FB_FUNC_M13_DRAFT_HITL_v1.md - SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1.md - docs/anexos/kimi_swarm_audit_faberloom/a9_sintesis.md

---

## 0. Decision de scope (CEO 2026-06-25): INTERNO-PRIMERO, despues sacarlo

FaberLoom se construye primero como herramienta INTERNA de MWT (operacion
Marluvas/Tecmater/Rana Walk). Recien tras probar funcionalidad con valor real se
externaliza ("sacarlo") como producto.

Implicancia dura:
- El SPINE multi-tenant del PLAN_DESARROLLO_FABERLOOM_v6 (M16 RLS 7 capas, aislamiento,
  M08/M09/M15/M12 a escala SaaS) NO se construye ahora: es la fase de externalizacion.
- El build de AHORA es un slice single-tenant interno del loop RFQ -> draft -> HITL.
- El v6 queda como PLANO de la externalizacion futura, no como el proximo build.
- El gate comercial EXTERNO (WTP/LOI de PYME ajena) se MUEVE al punto de "sacarlo",
  no es pre-S1. Antes de externalizar: demanda externa probada + spine.

Esta v1.1 reemplaza el E0.5 suelto (v1.0) por una SECUENCIA de gates pre-build,
endurecida por el red-team de Kimi y Fugu (ambos: MATIZADO). Ver EVAL_E0_5_*.

---

## 1. Proposito

Probar, lo mas barato posible y ANTES de construir, los dos supuestos que pueden
matar el proyecto interno:
1. Que los datos comerciales (precio/stock/margen/equivalencias/contratos) son
   confiables y vigentes -- si estan stale, la IA acelera errores.
2. Que el loop RFQ -> draft IA -> HITL ahorra tiempo NETO real a MWT y le gana a
   un baseline tonto (template + Excel + respuesta canned).

Correccion asumida del triple filtro: "validar es dias" omite costo de datos,
baseline, operador y sesgo. E0.5 INFORMA C5/C6/13-features; NO los resuelve con
10-15 casos. No es gratis ni canonico: es senal preliminar dirigida.

---

## 2. Secuencia de gates pre-build (en orden)

| Gate | Que prueba | Kill si |
|---|---|---|
| E0.1 Data readiness | catalogo/precios/stock/margen/equivalencias/contratos verificables y vigentes, con fuente por campo | verificar el dato cuesta tanto como responder a mano |
| E0.2 Protocolo de evaluacion | muestra estratificada, holdout ciego, juez independiente, metricas ponderadas, reglas de tuning y retencion -- pre-registrado ANTES de correr | no se puede congelar el protocolo (medicion sin contrato = teatro) |
| E0.5 Valor tecnico interno | shadow-replay: ahorro NETO de tiempo (incluye costo LLM/draft), diff semantico, accion-correcta, catch-rate humano, vs baseline tonto | sin ahorro neto, o no le gana al template, o edit semantico alto |
| E0.6 Safety / HITL catch-rate | bajo carga (burst), el humano detecta errores sembrados | ahorro positivo pero catch-rate bajo (gana velocidad, pierde confianza) |
| E0.25 Comercial EXTERNO | [DIFERIDO a "sacarlo"] >=1 LOI/pago/piloto de PYME ajena | -- gatea la externalizacion + el spine v6, NO el build interno |

Regla: el build interno arranca si pasan E0.1 + E0.5 + E0.6 (con E0.2 como
contrato). E0.25 no aplica al build interno; aplica a la decision de externalizar.

## 3. E0.1 -- Data readiness (gate 1)
Por cada campo critico (precio, stock, margen, lead time, equivalencia tecnica,
contrato/condiciones, vigencia): fuente identificada, vigente y verificable, con
mecanismo de actualizacion. Entregable: matriz campo -> fuente -> frescura ->
fallback. Kill si verificar el dato cuesta tanto como responder a mano (entonces el
cuello no es redactar, es el dato).

## 4. E0.2 -- Protocolo de evaluacion (contrato, antes de correr)
Pre-registrar: set de RFQs y su estratificacion (facil/medio/dificil/incompleto/
follow-up-no-cotizacion/ruidoso); holdout ciego (3-5 casos); juez (idealmente 2do
revisor independiente); metricas y pesos; reglas de tuning (cuantas iteraciones de
prompt se permiten); retencion/seguridad de datos reales. Sin este contrato, E0.5 no
corre.

## 5. E0.5 -- Valor tecnico interno (gate 2)
Metodo preferido: SHADOW-REPLAY sobre RFQs ya respondidos (ocultar la respuesta
enviada, generar draft, comparar contra lo realmente enviado). Sin Hawthorne, sin
riesgo de envio, usa data historica.
Controles obligatorios:
- Baseline tonto: Manual vs Template/Macro/Excel vs IA, mismos RFQs. La IA debe
  GANARLE al template, no solo al folio en blanco.
- >=2 perfiles de operador si es posible; registrar operador por caso.
- Holdout ciego para validar tras el tuning de prompts.
Metricas (no las de v1.0, corregidas por el triple filtro):
- ahorro_neto_tiempo = baseline - (revisar+editar+enviar), MENOS costo_LLM_por_draft.
- edit_semantico_ponderado: peso alto a SKU/cantidad/precio/margen/stock/lead time/
  equivalencia/impuestos/vigencia; bajo a tono. (edit_rate por lineas NO sirve.)
- accion_correcta_rate: el output correcto puede ser cotizar / pedir dato / escalar /
  declinar / no responder. send_rate solo premia sobre-responder.
- human_catch_rate y critical_generated_rate: errores criticos generados y si el
  humano los atrapo. fallo_critico binario no alcanza (ignora near-misses).
Reportar p50/p75/p95/worst-case (la mediana esconde colas que destruyen confianza).

## 6. E0.6 -- Safety / HITL catch-rate (gate 3)
Burst test: ~20 drafts mixtos en una sesion con errores sembrados. Medir si el
humano los detecta bajo carga y fatiga (M13 asume 15-20 drafts/dia, 1-2 min c/u).
Kill si hay ahorro de tiempo pero el catch-rate cae: gana velocidad, pierde confianza.

## 7. Diagnostico obligatorio (no kill automatico)
Si E0.5/E0.6 FALLAN: diagnostico antes de matar -- fue la TESIS (IA+HITL no sirve) o
un ARTEFACTO del slice (prompt pobre, Voice Profile basico, catalogo incompleto, UX
inexistente)? Matar el proyecto por un mal experimento es mas caro que rehacerlo.

## 8. Firewall contract-first (anti-contaminacion)
Todo artefacto del slice se marca `E0_5_NO_PROMOTE`. Prohibido migrar prompts/
scripts/planillas/columnas de error al repo productivo. Solo los APRENDIZAJES pasan,
y se traducen a fixtures contract-first versionados (ActionContext, DraftOutput,
PolicyDecision, OutcomeEntry) en las fichas formales. E0.5 INFORMA C5/C6/13-features;
la decision canonica vive en M10/M13 con datos como input, no como verdad final.

## 9. Hallazgo del red-team a llevar a M10 [PENDIENTE -- decision CEO]
Fugu detecto en M10: varios de los 13 features (business_value, prior_case_similarity,
requires_human_gate, expected_latency, validator_failure_count) pueden no existir
ANTES de clasificar o depender del resultado (target leakage); y data_class es
circular (input y output). Separar data_class_initial de data_class_final/pre_egress.
Esto es un bug de spec de M10 -- registrar como pendiente en SPEC_FB_FUNC_M10.

## 10. Pendientes CEO
1. [PENDIENTE] Set de RFQs reales + estratificacion + holdout; fuente del baseline
   (historico de MWT preferido sobre cronometro).
2. [PENDIENTE] Umbrales exactos de PASA/FALLA por gate (ahorro neto minimo, catch-rate
   minimo, cuanto debe ganarle al template).
3. [PENDIENTE] Quien corre la secuencia y en cuanto tiempo (incluir costo de E0.1/E0.2).
4. [PENDIENTE] Punto de disparo de E0.25 externo (cuando se decide "sacarlo").

---

Changelog:
- v1.1 (2026-06-25): Endurecida por triple filtro (Claude arbitro + red-team Kimi +
  Fugu, ambos MATIZADO). Scope INTERNO-PRIMERO (decision CEO): spine v6 diferido a
  externalizacion. E0.5 suelto -> secuencia E0.1/E0.2/E0.5/E0.6 + E0.25 externo diferido.
  Shadow-replay, baseline tonto, diff semantico, accion-correcta, catch-rate, firewall
  NO_PROMOTE, diagnostico-no-kill. Hallazgo de target leakage en M10 a registrar.
- v1.0 (2026-06-25): Creacion. Gate E0.5 single (superseded por v1.1).

---

## 11. ENMIENDA v1.2 (2026-06-25) -- E0.5 interno: adopcion, no cronometro

Decision CEO (2026-06-25): en el contexto interno solo-fundador, el gate E0.5 NO se
corre como protocolo de metricas cronometradas. Cuando el operador, el que decide y el
dueno del dato son la misma persona, ese aparato es teatro de evidencia. Ademas,
cronometrar deforma el numero (Hawthorne) y mirar el reloj no es trabajar.

Metodo por defecto -- DOGFOODING:
- Usar el tool en los RFQs reales que entran, 1-2 semanas, sin medir tiempos.
- Senal = ADOPCION: si tras 10-15 RFQs reales seguis agarrando el tool, paso; si lo
  dejaste de usar sin pensarlo, no paso. La conducta es la metrica, no el reloj.

NO-NEGOCIABLE (no es medir, es mirar): verificar que los datos duros del draft estan
bien -- precio, stock, equivalencia tecnica. Es el modo de falla silencioso (draft
fluido con precio vencido = promesa comercial falsa, R2 Riesgo 2). Ya se hace antes de
enviar al cliente; no es trabajo extra.

Las metricas formales de Sec.5 (shadow-replay, diff semantico, p95, catch-rate, >=2
operadores) quedan RESERVADAS para cuando suben las apuestas: GO/NO-GO de construir el
spine, externalizacion, o cuando la adopcion sale ambigua y hay que desagregar por que.

Changelog (cont.):
- v1.2 (2026-06-25): E0.5 interno por adopcion (dogfooding 1-2 semanas), no cronometro;
  unico no-negociable = verificar datos duros. Metricas formales reservadas para alta
  apuesta o resultado ambiguo.
