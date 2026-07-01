# EVAL_E0_5_VALIDATION_FUGU_ULTRA.md -- Red-Team Audit del Gate E0.5 (PLAN v6)
id: EVAL_E0_5_VALIDATION_FUGU_ULTRA
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: AUDIT
stamp: DRAFT -- 2026-06-25 08:18:01 -06:00 -- red-team del gate E0.5 sobre PLAN_DESARROLLO_FABERLOOM_v6; motor Fugu Ultra
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: PLAN_DESARROLLO_FABERLOOM_v6.md - SPEC_FB_E0_5_VALIDATION_SLICE_v1.md - SPEC_FB_FUNC_M10_L1_CLASSIFIER_v1.md - SPEC_FB_FUNC_M13_DRAFT_HITL_v1.md - docs/anexos/kimi_swarm_audit_faberloom/a9_sintesis.md - CLAUDE.md - WIKI.md
run_id: [PENDIENTE -- NO INVENTAR: el prompt trae placeholder RUN_ID sin instancia concreta]

---

## 1. Metodo

Se ejecuto red-team por debate-and-aggregation contra la recomendacion de insertar E0.5 antes de S1. Este archivo NO valida la recomendacion por defecto: primero la ataca y solo despues emite veredicto.

Fuentes leidas del repo canonico:
- `CLAUDE.md` y `WIKI.md`.
- `docs/faberloom/PLAN_DESARROLLO_FABERLOOM_v6.md`, incluida Sec.14.
- `docs/faberloom/SPEC_FB_E0_5_VALIDATION_SLICE_v1.md`.
- `docs/faberloom/SPEC_FB_FUNC_M10_L1_CLASSIFIER_v1.md`.
- `docs/faberloom/SPEC_FB_FUNC_M13_DRAFT_HITL_v1.md`.
- `docs/anexos/kimi_swarm_audit_faberloom/a9_sintesis.md`.

Regla aplicada: dato ausente = `[PENDIENTE -- NO INVENTAR]`.

---

## 2. Fase 1 -- Argumentos independientes por rol

### ROLE A -- Abogado del diablo de E0.5

Caso mas fuerte contra el gate:

1. **E0.5 no es tan barato como afirma.** Para que mida algo real necesita RFQs curados, baseline manual por caso, catalogo/precios vigentes, Voice Profile, criterio de scoring, disponibilidad de Alvaro/operador, umbrales CEO y disciplina de registro. Eso puede competir con S0, no ser solo "dias".
2. **La muestra propuesta es pequena y potencialmente sesgada.** 10-15 RFQs, incluso "semi-reales", pueden habilitar o matar meses de arquitectura con senal ruidosa. Si son golden seed de Marluvas/Tecmater, suben artificialmente send_rate y bajan edit_rate.
3. **Concierge no prueba producto.** Si Alvaro + Claude/Kimi + curacion manual hacen drafts buenos, eso no valida Tier 0, Action Engine, M11, M12, M15, RBAC, WorkLoom, evidencia usable, ni aprendizaje.
4. **Puede dar falso negativo.** E0.5 permite prompt directo sin engine, sin Tier 0, sin 13 features completos y sin WorkLoom. Si falla, no sabemos si fallo la tesis o un artefacto pobre: prompt, Voice Profile, catalogo temporal, UX inexistente.
5. **Puede dar falso positivo.** El humano sabe que esta evaluando, mira con mas cuidado que en operacion diaria y declara "lo enviaria" sin enfrentar canal real, cliente real, costo de error, SLA, friccion de envio ni pago.
6. **Bypassea invariantes que son parte del producto.** FaberLoom no vende solo texto; vende confianza: HITL absoluto, D9 fail-closed, audit D10, RLS, RBAC, outbox y tenant isolation. Un slice sin esos controles valida un producto distinto.
7. **Amenaza contract-first por contaminacion.** Aunque se declare descartable, prompts, planillas, columnas de error y evidence bundle improvisado tenderan a volverse contrato de facto para M10/M13.
8. **Confunde valor operativo con valor comercial.** Tiempo ahorrado no equivale a WTP, LOI, pago, retencion ni ventaja competitiva. El gate comercial real sigue insuficientemente adelantado.

Veredicto ROLE A: **NO-GO como hard gate en su forma actual**. Convertirlo en investigacion/dual gate con mayor rigor, o puede ser una trampa de medicion.

### ROLE B -- Defensor de E0.5

Caso mas fuerte a favor:

1. **La asimetria es real.** El SPINE M16/M08/M09/M15/M12/M11 son meses y especialistas; el loop RFQ -> draft -> HITL puede probarse con planilla y datos reales.
2. **Ataca el supuesto que puede matar el proyecto.** Si MWT no ahorra tiempo revisando drafts, RLS impecable y audit D10 no salvan el producto.
3. **Prueba el corazon de T1.** El PLAN v6 define T1 como M10 + M13; E0.5 replica inbound/RFQ -> draft -> HITL y mide tiempo, edicion, envio y fallos criticos.
4. **Evita builder trap en un contexto de stack contradictorio.** a9 y PLAN v6 documentan C1/STACK-01 y multiples contradicciones; construir plataforma antes de validar valor aumenta el riesgo de refactor y desperdicio.
5. **Produce evidencia para pendientes reales.** Puede informar C5 (bundle no-cotizacion), C6 (threshold 0.85 vs routing 3 capas) y los 13 features FG-03.
6. **No modifica formalmente el v6.** La Sec.14 solo antepone un gate; si pasa, S1 sigue con spine, contracts y tests.

Veredicto ROLE B: **GO condicionado**. No iniciar S1 hasta pasar E0.5 con RFQs reales, baseline ratificado y umbrales predefinidos.

### ROLE C -- Cazador de blind spots

Lo que no vio suficientemente ninguno:

1. **Mediana de tiempo ahorrado oculta colas peligrosas.** Un p50 positivo puede convivir con p95 negativo o 2-3 casos que destruyen confianza.
2. **`fallo_critico` binario no mide near-misses.** Si el humano detecta cinco errores graves antes de enviar, el gate podria pasar aunque la operacion pierda confianza y tiempo.
3. **`edit_rate` por lineas/edit-distance es mal proxy.** Cambiar un SKU, precio, margen, stock o equivalencia puede ser una edicion pequena con impacto maximo.
4. **RFQ real es hilo, no evento unico.** Hay aclaraciones, cambios de cantidad, negociacion, sustituciones, precio vencido y follow-ups; E0.5 mide primer draft.
5. **Falta medir abstencion inteligente.** El mejor output a veces es pedir aclaracion, escalar, declinar o bloquear por dato vencido; `send_rate` puede premiar sobre-responder.
6. **Los 13 features de M10 tienen riesgo de computabilidad y leakage.** `business_value`, `expected_latency`, `prior_case_similarity`, `validator_failure_count` y `requires_human_gate` pueden no existir antes de clasificar o depender del resultado.
7. **`data_class` puede ser circular.** Si hereda N2 por default y tambien decide N0-N4, el clasificador puede confirmar una clasificacion inicial incorrecta.
8. **No hay contrato de evaluacion.** Falta preregistro de muestreo, tuning, orden, juez, metricas, criterios de exclusion y reglas de retencion.
9. **Frescura de datos es el core oculto.** Precio, stock, margen, contratos, equivalencias y condiciones vigentes son probablemente mas importantes que redactar rapido.
10. **Evidence bundle puede ser teatro de evidencia.** Mostrar fuentes no prueba que cada campo este trazado a fuente vigente y valida.
11. **Errores por omision no estan capturados.** No afirmar algo falso no basta; se puede omitir MOQ, vigencia, impuestos, entrega, disclaimer o necesidad de confirmacion.
12. **No hay control contra soluciones simples.** Template + Excel + Gmail canned response podria capturar gran parte del valor sin SPINE ni IA.
13. **No se mide fatiga/burst HITL.** M13 asume 15-20 drafts/dia y 1-2 min por revision; E0.5 caso-a-caso no prueba colas ni complacencia.

---

## 3. Fase 2 -- Debate y agregacion

**Punto de acuerdo:** Validar valor antes de plomeria es correcto. El v6 original ponia mucha inversion antes de probar el supuesto de eficiencia del loop RFQ -> draft -> HITL.

**Punto de desacuerdo:** El E0.5 especificado no es automaticamente un test fuerte. Es barato solo si los insumos ya existen; es informativo solo si se diseña con baseline confiable, muestra representativa, umbrales pre-registrados, metricas semanticas y firewall contra reutilizacion de artefactos.

**Correccion al arbitro/Claude:** La frase "probar valor son dias" omite costos de datos, baseline, operadores, sesgo y compliance. Tambien sobrevende el bonus: E0.5 puede **informar** C5/C6/13 features, pero no resolverlos de forma canonica con 10-15 casos.

**Correccion a Fugu/Kimi:** Ambos acertaron al detectar builder trap y contradicciones de stack, pero subponderaron que el riesgo comercial de WTP/LOI no queda resuelto por tiempo_ahorrado. El gate de valor no debe confundirse con gate de pago.

**Consenso:** E0.5 sobrevive como principio, pero necesita ser endurecido. En forma actual, la decision correcta es **MATIZADA**: no eliminar E0.5, pero tampoco aceptarlo como hard gate limpio sin agregar gate comercial, readiness de datos, contrato de evaluacion, metricas de correccion verificable y firewall contract-first.

---

## 4. Fase 3 -- Respuestas especificas

### Q1. La asimetria costo (spine=meses, validacion=dias) -- valida, o hay costo oculto?

**HALLAZGO:** La asimetria es direccionalmente valida: el SPINE requiere meses de infraestructura transversal, mientras que un slice RFQ -> draft -> HITL puede probarse con herramientas ligeras. Pero hay costo oculto material: preparar RFQs reales, baseline manual por caso, catalogo/precios vigentes, Voice Profile, criterios de medicion, disponibilidad del operador y ratificacion de umbrales CEO. Ademas, el gate propuesto usa mediana de tiempo y edit_rate simple: puede ocultar p95 negativo, near-misses criticos y ediciones semanticas pequenas pero comercialmente graves.

**RIESGO:** P1.

**RECOMENDACION:** Mantener E0.5, pero no venderlo como "gratis". Pre-registrar protocolo: set de RFQs, baseline historico si existe, cronometraje, operador(es), catalogo usado, umbrales, criterio de fallo y reglas de tuning. Reportar p50/p75/p95/worst-case, `critical_generated_rate`, `human_catch_rate`, severidad por campo y diff semantico ponderado (SKU, cantidad, precio, margen, stock, lead time, equivalencia, impuestos/envio, vigencia, tono). Si solo hay un operador, marcar el resultado como evidencia preliminar.

### Q2. Un slice single-tenant DESCARTABLE prueba de verdad el supuesto, o el valor real solo emerge con volumen / integracion / multi-tenant?

**HALLAZGO:** Prueba solo una version estrecha del supuesto: si drafts asistidos pueden ahorrar tiempo en RFQs MWT bajo condiciones controladas. No prueba volumen, aprendizaje, integracion de canal, WorkLoom, RBAC, D9/D10, ni multi-tenant. Puede dar falso positivo si la muestra es limpia y concierge; puede dar falso negativo si falla por falta de UX, Voice Profile pobre o catalogo incompleto. Tampoco prueba el ciclo comercial completo: RFQs suelen ser threads con aclaraciones, cambios, negociacion, sustituciones y follow-ups, no eventos unicos. `send_rate` puede premiar una mala conducta: responder cuando lo correcto era pedir aclaracion o abstenerse.

**RIESGO:** P0/P1. P0 si el resultado se usa para matar o habilitar SPINE sin diagnostico; P1 si se usa como senal preliminar.

**RECOMENDACION:** Estratificar RFQs: faciles, medios, dificiles, incompletos, follow-ups/no-cotizacion, adjuntos y ruidosos. Agregar replay de threads historicos completos hasta respuesta/cierre si existen. Medir `appropriate_next_action_rate`: cotizar / pedir dato / escalar / declinar / no responder. Usar segundo revisor ciego y verificacion contra fuente oficial para precio, stock, contrato, margen y ficha tecnica. Interpretar PASA como "vale construir S1 para validar en producto", no como "producto validado". Interpretar FALLA como "diagnostico obligatorio", no kill automatico si la causa fue artefacto del slice.

### Q3. Insertar E0.5 rompe algo del contract-first o del orden del spine? Genera trabajo tirable que despues estorba?

**HALLAZGO:** No rompe formalmente el orden del v6 porque se declara no-productivo, descartable y pre-S1. Operativamente si puede debilitar contract-first: valida comportamiento antes de contratos, bypassea invariantes fail-closed y puede crear contratos fantasma en prompts, planillas, formato de draft, categorias de error y bundle improvisado. Tambien existe riesgo de manejar datos reales sin D9/D10/RBAC/RLS formal. Blind spot adicional: M10 contiene features que podrian no ser computables en el momento de clasificar o tener target leakage, y `data_class` como input/output puede crear circularidad si no se separan fuente inicial y decision final.

**RIESGO:** P1.

**RECOMENDACION:** Crear un firewall E0.5: artefactos marcados `E0_5_NO_PROMOTE`, ningun script/prompt se migra a runtime, datos y resultados se traducen despues a fixtures contract-first (`ActionContext`, `DraftOutput`, `PolicyDecision`, `OutcomeEntry`) con schemas versionados. Agregar matriz feature -> fuente -> momento disponible -> fallback -> costo -> riesgo si falta. Separar `data_class_initial` de `data_class_final/pre_egress`. Añadir contrato de evaluacion preregistrado antes de correr.

### Q4. Hay un test MAS BARATO o MAS INFORMATIVO que E0.5 para el mismo supuesto?

**HALLAZGO:** Si, o al menos complementos mejores:

1. **E0.1 Data readiness:** validar que catalogo, precios, stock, margen, contratos, equivalencias y condiciones comerciales son confiables y actualizables.
2. **E0.2 Evaluation protocol lock:** congelar muestra, holdout, juez, metricas ponderadas, adversarial cases, reglas de tuning y retencion de datos.
3. **E0.25 comercial:** conseguir >=1 LOI/pago/intencion firmada de MWT o cliente piloto antes de S1.
4. **Replay shadow historico:** tomar RFQs ya respondidos, ocultar la respuesta enviada, generar drafts y comparar contra la respuesta real enviada y resultado comercial.
5. **Descomposicion manual del tiempo:** medir que parte del proceso actual es busqueda de precio/stock/equivalencia vs redaccion. Si la redaccion es poca, IA de draft tiene techo bajo.
6. **Control simple:** comparar Manual vs Template/Macro vs IA, mismos RFQs y operador. Quizas plantilla + Excel + Gmail canned response captura 70% del valor.
7. **Canary adversarial set:** precio vencido, SKU inexistente, contrato especial, stock ambiguo, margen negativo, sustitucion tecnica falsa.
8. **Burst/fatigue HITL:** 20 drafts mixtos en una sesion; medir errores, tiempo por caso, aprobacion automatica y fatiga.

**RIESGO:** P1.

**RECOMENDACION:** No reemplazar E0.5 por un unico test alternativo; fortalecerlo como paquete secuencial: E0.1 data readiness + E0.2 protocolo + E0.25 comercial + replay shadow + slice tecnico controlado + burst/canaries. Si el tiempo es minimo, primero correr E0.1/E0.2/E0.25 y replay historico; son mas baratos que montar un slice interactivo.

### Q5. Que supuesto del v6 NO queda cubierto NI por E0.5 NI por el spine? (blind spot real)

**HALLAZGO:** El blind spot P0 es **demanda comercial / WTP / PMF**. Ni E0.5 ni el SPINE prueban que alguien pague, firme LOI o cambie su operacion por FaberLoom. Pero el blind spot tecnico-operativo mas importante es **frescura y verificabilidad de datos comerciales**: si precio, stock, margen, equivalencias, contratos o condiciones estan stale, la IA acelera errores. Otros supuestos no cubiertos:

- Unit economics: ahorro neto despues de costo LLM/infra/soporte.
- Adopcion del operador y complacencia en uso repetido.
- Canal real de entrada/salida y friccion de integracion.
- Evidence bundle como trazabilidad real campo-a-fuente, no teatro de evidencia.
- Omisiones criticas: MOQ, vigencia, impuestos, entrega, disclaimers, alternativas o necesidad de confirmacion.
- Politica comercial: margen minimo, descuentos, contrato especial, historial del cliente.
- Aprendizaje/moat: si M14/gold samples mejoran realmente sin contaminarse con aprobaciones erroneas.
- Transferibilidad a un segundo work-type pack/vertical.
- Calidad de cliente: respuesta, conversion, errores evitados, retrabajo.
- Seguridad y compliance del experimento con datos reales.

**RIESGO:** P0.

**RECOMENDACION:** Agregar gates antes de S1: (1) comercial/economico: al menos 1 compromiso explicito inicial + estimacion de valor neto por draft; (2) data readiness: fuente verificable y vigente por campo critico; (3) source-to-field audit: cada precio/SKU/lead time/margen apunta a fuente vigente; (4) checklist de omisiones criticas por tipo de RFQ. Mantener E2.5 >=3 LOI como gate de expansion, pero no permitir SPINE completo sin señal comercial minima y datos comerciales confiables.

### Q6. El gate de valor en E0.5 vs E2.5 -- hay razon para que el gate comercial (LOI/pago) deba ir antes que el de tiempo-ahorrado, o al reves?

**HALLAZGO:** El plan dice que eleva el gate de valor de E2.5 a E0.5, pero el SPEC E0.5 mide eficiencia operativa, no LOI/pago. Eso es una confusion de categorias: tiempo_ahorrado puede ser valor de usuario, pero no valor comercial. Hay razon para poner gate comercial antes o en paralelo: si nadie paga, el ahorro de tiempo no justifica meses de SPINE; si alguien firma LOI/pago pero E0.5 falla, hay demanda pero la solucion debe replantearse antes de construir. Ademas, antes de cualquier loop tecnico falta readiness de datos y protocolo de evaluacion; si los datos no estan listos, E0.5 solo prueba capacidad de improvisacion.

**RIESGO:** P1/P0. P1 por timing de decision; P0 si se construye SPINE sin demanda real o con datos comerciales stale.

**RECOMENDACION:** Convertir el gate pre-S1 en secuencia minima:
- **E0.1 Data readiness:** catalogo, precios, stock, margen, contratos, equivalencias y condiciones con fuente vigente. Kill si verificar datos toma tanto como responder manualmente.
- **E0.2 Evaluation protocol lock:** muestreo estratificado, holdout, juez independiente, metricas ponderadas, adversarial cases, reglas de tuning y retencion de datos.
- **E0.25 Comercial:** >=1 LOI/pago/intencion firme de piloto o sponsor MWT con valor esperado y criterio de exito. [PENDIENTE -- NO INVENTAR: umbral exacto CEO].
- **E0.5 Tecnico:** ahorro de tiempo + edit_rate semantico + send/abstain correcto + catch-rate humano + 0 fallos criticos no detectados, con protocolo mejorado.
- **E0.6 Safety/HITL catch-rate:** medir si el humano detecta errores sembrados bajo carga; kill si ahorro positivo pero catch-rate bajo.

E2.5 mantiene >=3 LOI antes de E3/multi-tenant externo; no sustituye el gate temprano.

---

## 5. Cierre

### VEREDICTO sobre E0.5 = MATIZADO

E0.5 sigue en pie como principio: validar valor antes de plomeria es correcto y reduce builder trap. Pero el E0.5 actual es insuficiente como hard gate porque puede dar señal sesgada, no comercial y no contract-first; debe endurecerse con data readiness, contrato de evaluacion, E0.25 comercial, metricas de correccion verificable, safety/catch-rate y firewall contra artefactos descartables.

### BLIND SPOTS

1. PMF/WTP/LOI antes de SPINE.
2. Unit economics por draft.
3. Frescura y verificabilidad de catalogo, precios, stock, equivalencias, contratos y margen.
4. Adopcion real del operador y complacencia bajo carga.
5. Canal real de entrada/salida.
6. Evidence bundle como trazabilidad campo-a-fuente, no teatro.
7. Omisiones criticas no capturadas por `fallo_critico` binario.
8. `edit_rate` simple vs diff semantico ponderado.
9. Sobreajuste de 10-15 casos a 13 features y threshold 0.85.
10. Computabilidad/target leakage de features de M10.
11. Transferibilidad a segundo work-type pack/vertical.
12. Control contra soluciones simples (template/macro/Excel).
13. Reutilizacion accidental de codigo/prompts descartables.
14. Seguridad/compliance del experimento con datos reales.
15. Medicion de respuesta/cierre/retrabajo del cliente, no solo "lo enviaria".

### ALTERNATIVA mas fuerte

**Secuencia pre-S1 endurecida:**

1. **E0.1 -- Data readiness:** fuentes vigentes y verificables para campos comerciales criticos.
2. **E0.2 -- Evaluation protocol lock:** protocolo preregistrado, muestra estratificada, holdout, jueces, tuning y metricas.
3. **E0.25 -- Comercial:** al menos una señal comercial explicita (LOI/pago/intencion firme de piloto/sponsor MWT) y estimacion de valor neto esperado.
4. **E0.5 -- Tecnico mejorado:** replay shadow + slice descartable con muestra estratificada, baseline historico o protocolo cronometrado, >=2 perfiles de operador si es posible, holdout ciego, costo por draft, red-team de fallos criticos, abstencion correcta, source-to-field audit y outputs convertidos en fixtures contract-first.
5. **E0.6 -- Safety/HITL catch-rate:** burst test con errores sembrados para probar si el humano detecta fallos bajo carga.
6. **Firewall:** todo artefacto del slice queda `NO_PROMOTE`; solo los aprendizajes pasan por specs/versiones formales.

Si estos gates pasan, iniciar S1. Si falla E0.25, no construir SPINE. Si falla E0.5/E0.6, diagnosticar causa y replanear antes de SPINE.

### Nivel de confianza

**MEDIA.** La direccion de E0.5 es robusta, pero la conclusion depende de insumos aun pendientes: RFQs reales, baseline, umbrales CEO, operador(es), disponibilidad de datos historicos, readiness de catalogo/precios/stock y existencia de señales comerciales.

---

Changelog:
- v1.0 (2026-06-25): Red-team audit Fugu Ultra del criterio E0.5. Veredicto MATIZADO; recomienda secuencia pre-S1 E0.1/E0.2/E0.25/E0.5/E0.6 + firewall contract-first.
