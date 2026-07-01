# EVAL_E0_5_VALIDATION_KIMI.md -- Red-Team Audit del Gate E0.5 (v6)
id: EVAL_E0_5_VALIDATION_KIMI
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: AUDIT
stamp: DRAFT -- 2026-06-25 -- red-team del gate E0.5 sobre PLAN_DESARROLLO_FABERLOOM_v6; motor Kimi
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: PLAN_DESARROLLO_FABERLOOM_v6.md - SPEC_FB_E0_5_VALIDATION_SLICE_v1.md - SPEC_FB_FUNC_M10_L1_CLASSIFIER_v1.md - SPEC_FB_FUNC_M13_DRAFT_HITL_v1.md - docs/anexos/kimi_swarm_audit_faberloom/a9_sintesis.md - CLAUDE.md - WIKI.md [PENDIENTE -- NO INVENTAR: WIKI.md no localizado en repo]

---

## 1. Metodo

Se aplico el protocolo de debate-and-aggregation con tres roles mutuamente excluyentes:

- **ROLE A -- Abogado del diablo de E0.5:** construye el caso mas fuerte EN CONTRA del gate.
- **ROLE B -- Defensor de E0.5:** construye el caso a FAVOR con evidencia del repo.
- **ROLE C -- Cazador de blind spots:** senala lo que NO vieron Claude, Fugu ni Kimi.

Fuentes leidas: `PLAN_DESARROLLO_FABERLOOM_v6.md` (incl. enmienda Sec.14), `SPEC_FB_E0_5_VALIDATION_SLICE_v1.md`, `SPEC_FB_FUNC_M10_L1_CLASSIFIER_v1.md`, `SPEC_FB_FUNC_M13_DRAFT_HITL_v1.md`, `docs/anexos/kimi_swarm_audit_faberloom/a9_sintesis.md`, `CLAUDE.md`. `WIKI.md` no fue localizado; se marca [PENDIENTE -- NO INVENTAR].

---

## 2. Fase 1 -- Argumentos por rol

### ROLE A -- Abogado del diablo: caso contra E0.5

1. **Mide eficiencia interna, no PMF.** El supuesto que realmente mata un SaaS B2B no es si un operador tarda 2 minutos menos; es si alguien paga o firma una LOI. E0.5 no incluye WTP/LOI; por eso es un proxy debil del riesgo comercial.
2. **Costo oculto y sesgo de medicion.** "Dias" ignora la curacion de 10-15 RFQs reales, la obtencion del baseline manual y la disponibilidad del CEO/Alvaro. Medir a un solo operador consciente del cronometro (efecto Hawthorne) produce un baseline inestable. Un operador experto puede parecer que "no ahorra nada" porque ya escribe rapido; un novato puede ahorrar mucho pero no representa el perfil real.
3. **Falso negativo por artefacto vs. supuesto.** Si el slice falla, no se sabe si falla la tesis (IA + HITL no sirve) o si fallo el prompt, el Voice Profile basico o el catalogo cargado a mano. Matar el proyecto por un mal experimento es mas costoso que rehacer el experimento.
4. **Falso positivo por muestra curada.** Los RFQs "golden seed" pre-seleccionados por el CEO probablemente son los mas limpios y repetitivos. Eso no refleja la variabilidad real: spam, follow-ups, RFQs incompletos, adjuntos, idioma mixto. El send_rate/edit_rate del slice puede ser artificialmente bueno.
5. **Trabajo tirable que contamina.** Aunque se declare "descartable", la presion real es reutilizar los prompts, el Voice Profile y los scripts del slice. Eso erosiona la disciplina contract-first del v6 y puede cristalizar decisiones prematuras de C5/C6/FG-03.
6. **Dejar el riesgo comercial para E2.5 sigue siendo una trampa.** Si E0.5 pasa y E2.5 falla, se habran invertido meses en el SPINE para un producto que nadie compra. E0.5 adelanta el gate tecnico, no el gate de negocio.
7. **Existen tests mas baratos y mas informativos.** Una descomposicion del tiempo manual actual de Alvaro (cuanto es buscar info vs. redactar) y 3-5 entrevistas de WTP con clientes de MWT matarian o validarian el proyecto antes de tocar un LLM.

### ROLE B -- Defensor de E0.5: caso a favor

1. **Asimetria real.** El SPINE (M16/M08/M09/M15/M12/M11) son meses de trabajo distribuido y especializado. E0.5 puede correr con una planilla y acceso a Claude/Kimi. La relacion costo/informacion es favorable.
2. **Ataca el supuesto central del plan.** El v6 asume que el loop RFQ -> draft -> HITL ahorra tiempo real en un caso B2B de MWT. Si ese supuesto es falso, todo el resto es plomeria sobre un producto que no genera valor. Es logico probarlo primero.
3. **Es explicitamente descartable.** La especificacion no lo confunde con MVP ni producto. No requiere RLS, multi-tenant, audit, Electron ni RBAC. Eso evita que el equipo se distraiga construyendo infraestructura antes de saber si vale la pena.
4. **De-riesga T1 con datos reales.** E0.5 resuelve parcialmente C5 (evidence bundle no-cotizacion), C6 (threshold 0.85 vs routing 3 capas) y los pesos de los 13 features FG-03 -- todos pendientes CEO que hoy son adivinanzas.
5. **No rompe el orden del v6.** Solo antepone un gate. Si FALLA, se mata antes de escribir SPINE. Si PASA, S1 arranca con evidencia de valor.
6. **Mantiene E2.5 como gate posterior.** El gate comercial no desaparece; solo se reordena. Probar primero que la maquina funciona y luego que alguien paga es razonable.

### ROLE C -- Blind spots que no vio ninguno (Claude, Fugu, Kimi)

1. **Costo por draft no medido.** E0.5 mide `tiempo_ahorrado` pero no el costo de LLM/infra por draft. Un ahorro de 5 minutos por operador a $0.50 por draft puede ser economicamente inviable para MWT. El "valor real" es ahorro neto, no solo tiempo.
2. **Adopcion / cambio de habitos del operador.** Un draft perfecto no garantiza que Maria lo use. Si el operador desconfia o prefiere redactar manual, el send_rate real en produccion sera bajo. E0.5 no mide friccion de adopcion.
3. **Canal real no probado.** El slice puede "pegar texto" de un email; no conecta WhatsApp/Gmail/SMTP real. El valor depende de la integracion con el canal por donde llegan los RFQs. Friction del canal no esta en las metricas.
4. **Tamanio de muestra vs. calibracion.** 10-15 RFQs son insuficientes para calibrar 13 features, un threshold de 0.85 y routing de 3 capas. Correr E0.5 para "resolver" C6/FG-03 conduce a sobreajuste si se toman esos numeros como definitivos.
5. **Falta de un gate de WTP/LOI previo.** Ninguno propuso un E0.25 comercial antes del E0.5 tecnico. Si nadie paga, el resultado del slice es irrelevante.
6. **Riesgo de reutilizacion de descartables.** Se asume que el equipo respetara "codigo descartable". La experiencia muestra que los prompts y perfiles del slice migran al producto por inercia, generando deuda tecnica.
7. **Baseline historico vs. medido.** E0.5 propone cronometrar el manual; lo mas confiable seria usar tiempos historicos de respuesta ya registrados en MWT. El cronometro manual es propenso a sesgos.
8. **Evidence bundle no-cotizacion requiere RFQs no-cotizacion.** El "bonus" de resolver C5 solo funciona si el set incluye follow-ups/consultas, no solo RFQs de cotizacion. El SPEC no lo exige.
9. **Muestra single-tenant MWT no prueba transferibilidad.** El adapter pattern y el valor como plataforma se validan con un segundo work-type pack o vertical. E0.5 no prueba que FaberLoom sea mas que una herramienta de calzado.
10. **El supuesto real puede ser el Voice Profile, no el loop.** Si el draft falla, la causa raiz puede ser que el Voice Profile basico no captura el tono de MWT, no que IA + HITL sea inviable. E0.5 no separa esas variables.

---

## 3. Fase 2 -- Debate cruzado

- **A vs. B:** La asimetria costo es real pero no tan limpia. E0.5 puede ser "dias" de ejecucion solo si el CEO/Alvaro ya tienen los RFQs y el baseline listos; de lo contrario es semanas. Aun asi, sigue siendo ordenes de magnitud mas barato que el SPINE.
- **A vs. B:** E0.5 no es PMF, pero tampoco pretende serlo. El defensor dice que E2.5 sigue ahi. El abogado del diablo replica que E2.5 post-SPINE deja el riesgo comercial para despues de meses de inversion.
- **C interviene:** Tanto A como B subestiman el riesgo de reutilizar descartables y de calibrar con muestras pequenas. Tampoco vieron la necesidad de un gate comercial mas temprano.
- **Consenso parcial:** E0.5 es una idea direccionalmente correcta pero **insuficiente y fragil tal como esta**. Necesita complementos para no ser una trampa disfrazada de prudencia.

---

## 4. Fase 3 -- Respuestas a las seis preguntas

### Q1. La asimetria costo (spine=meses, validacion=dias) -- valida, o hay costo oculto?

**HALLAZGO:** La asimetria es direccionalmente valida: el SPINE requiere meses de trabajo especializado (M16/M08/M09/M15/M12/M11) mientras que E0.5 puede correr con infraestructura minima. Sin embargo, el SPEC subestima los costos de preparacion: curacion de RFQs reales, obtencion de un baseline manual confiable, disponibilidad del CEO/Alvaro y construccion de un Voice Profile/catalogo temporal. Ademas, medir con un solo operador y un cronometro introduce sesgos importantes (efecto Hawthorne, variabilidad entre operadores).

**RIESGO:** P1 -- no bloquea, pero distorsiona la decision si se interpreta E0.5 como "gratis".

**RECOMENDACION:**
- Fijar el baseline preferentemente con datos historicos de MWT, no solo cronometro.
- Usar al menos 2 operadores con perfiles distintos y registrar el operador por caso.
- Incluir el tiempo de preparacion en la estimacion; no llamarlo "dias" si requiere semanas de curacion.
- Documentar metadatos del experimento (quien cura, quien corre, como se cronometra).

---

### Q2. Un slice single-tenant DESCARTABLE prueba de verdad el supuesto, o el valor solo emerge con volumen/integracion/multi-tenant?

**HALLAZGO:** El slice prueba el supuesto de forma parcial y con sesgos de muestra. El riesgo de falso positivo es alto si los 10-15 RFQs son "golden seed" curados y limpios: el send_rate/edit_rate seran artificialmente buenos. El riesgo de falso negativo tambien es alto: si el prompt, el Voice Profile basico o el catalogo temporal estan mal, el slice falla aunque la tesis sea valida. El valor real de FaberLoom depende de volumen, integracion con canales reales, WorkLoom, evidence bundle, aprendizaje y adopcion del operador; ninguno de esos factores esta en E0.5.

**RIESGO:** P1/P0 -- falso positivo puede autorizar meses de SPINE para un producto que no escala; falso negativo puede matar una tesis valida.

**RECOMENDACION:**
- Estratificar la muestra: faciles / medios / dificiles / ruidosos (spam, incompletos, follow-ups).
- Incluir RFQs no-cotizacion para validar de verdad C5.
- Si FALLA, exigir un diagnostico: ?fue concepto o fue implementacion del slice? No matar automaticamente.
- Usar holdout: dejar 3-5 RFQs para validar a ciegas despues del ajuste de prompts.

---

### Q3. Insertar E0.5 rompe algo del contract-first o del orden del spine? Genera trabajo tirable que despues estorba?

**HALLAZGO:** E0.5 no rompe formalmente el orden del SPINE ni el contract-first, porque no construye modulos del v6. Sin embargo, introduce un riesgo de contaminacion: prompts, Voice Profile y posibles scripts del slice pueden migrar al producto por inercia, erosionando la disciplina de contratos versionados. Tambien puede adelantar decisiones de C5/C6/FG-03 sin los contratos congelados que el v6 exige.

**RIESGO:** P1 -- riesgo de deuda tecnica y decisiones prematuras.

**RECOMENDACION:**
- Versionar todo artefacto del slice como `E0.5-DRAFT-NO-PROMOTE`.
- Prohibir explicitamente merge de codigo/prompts del slice al repo productivo.
- Resolver C5/C6/FG-03 en las fichas formales (M10/M13) con los datos de E0.5 como input, no como decision final.

---

### Q4. Hay un test MAS BARATO o MAS INFORMATIVO que E0.5 para el mismo supuesto?

**HALLAZGO:** Si. Existen tests mas baratos y mas informativos que el supuesto central:
- **Descomposicion del tiempo manual actual:** medir cuanto de la respuesta a un RFQ es busqueda de info vs. redaccion. Si la redaccion es una fraccion pequena, el techo de ahorro de IA es bajo.
- **Entrevistas de WTP/PMF con 3-5 clientes de MWT:** responden si el problema vale dinero, algo que E0.5 no mide.
- **Shadow mode / asistente paralelo:** generar drafts sin enviarlos y comparar con lo que envio el humano. Mide calidad sin riesgo de envio ni HITL.
- **A/B cruzado de operadores:** mismo RFQ resuelto manual y con draft por varios operadores, separando variabilidad humana del efecto del draft.

**RIESGO:** P1 -- si se omite, se puede invertir en E0.5 cuando un test mas barato hubiera matado/validado antes.

**RECOMENDACION:**
- Correr en paralelo (o antes) un E0.25 comercial: carta de intencion/LOI/pago de MWT o clientes clave.
- Hacer shadow mode con 10-20 RFQs ya respondidos; medir edit_distance vs. respuesta enviada real.
- Entrevistar a clientes sobre valor percibido y disposicion a pagar.

---

### Q5. Que supuesto del v6 NO queda cubierto NI por E0.5 NI por el spine? (blind spot real)

**HALLAZGO:** El blind spot mas grande es la **PMF/WTP (product-market fit / disposicion a pagar)**. Ni E0.5 ni el SPINE prueban si alguien pagara por FaberLoom. Otros supuestos no cubiertos:
- **Adopcion del operador:** un draft bueno no garantiza que el operador lo use.
- **Integracion con canales reales:** WhatsApp/email/SMTP como punto de entrada/salida.
- **Aprendizaje y moat:** si el sistema no mejora con gold samples, es vulnerable a competidores.
- **Costo economico neto:** ahorro de tiempo vs. costo de LLM/infra.
- **Transferibilidad a otros verticales:** FaberLoom como plataforma vs. herramienta de calzado.
- **Canales ruidosos:** spam, follow-ups, RFQs incompletos.

**RIESGO:** P0 -- si nadie paga, todo el proyecto es inviable independentemente del tiempo ahorrado.

**RECOMENDACION:**
- Agregar un gate comercial E0.25 antes o junto a E0.5.
- Incluir en E0.5 una estimacion de costo por draft y un proxy de adopcion (enviaria sin editar / con retoque / no).
- Planear un segundo work-type pack o vertical como parte de E2/E3 para validar transferibilidad.

---

### Q6. El gate de valor en E0.5 vs E2.5 -- hay razon para que el gate comercial (LOI/pago) deba ir antes que el de tiempo-ahorrado, o al reves?

**HALLAZGO:** Hay argumentos fuertes para poner el gate comercial **antes o al menos en paralelo**. Si nadie paga, no importa cuanto tiempo se ahorre; si hay LOI/pago, el tiempo ahorrado es un multiplicador, no el unico factor. Subir el gate de valor de E2.5 a E0.5 es correcto, pero E0.5 lo hace con una metrica tecnica (tiempo_ahorrado) y deja la LOI para despues del SPINE. Eso perpetua la trampa: se construye plomeria antes de saber si hay mercado.

**RIESGO:** P1 -- riesgo de invertir en SPINE para un producto sin demanda comercial verificada.

**RECOMENDACION:**
- Convertir E0.5 en un **dual gate**: E0.25 (compromiso comercial: >=1 LOI o pago intencion de MWT/clientes) + E0.5 (validacion tecnica del loop).
- Si E0.25 falla, no se corre E0.5 ni se toca SPINE.
- Si E0.25 pasa pero E0.5 falla, se mata o se replantea el producto antes de SPINE.

---

## 5. Cierre -- Veredicto

### VEREDICTO: MATIZADO

E0.5 es **direccionalmente correcto** (validar valor antes de plomeria) pero **insuficiente y fragil** tal como esta propuesto. No debe ejecutarse en su forma pura porque corre el riesgo de autorizar meses de SPINE sobre una base tecnica sin confirmacion comercial, y porque sus metricas pueden dar tanto falsos positivos (muestra curada, un solo operador) como falsos negativos (artefacto malo vs. tesis mala).

### BLIND SPOTS (lista priorizada)

1. **PMF/WTP:** nadie valido si MWT o clientes pagarian/pilotarian antes de construir.
2. **Costo neto por draft:** tiempo ahorrado no es valor si el costo LLM/infra se come el margen.
3. **Adopcion del operador:** un draft perfecto no se usa si Maria no confia o cambia de habito.
4. **Canal real:** E0.5 no conecta WhatsApp/email productivo; ignora friction del canal.
5. **Reutilizacion de descartables:** riesgo real de que prompts/artefactos del slice migren al producto.
6. **Sobreajuste por muestra pequena:** 10-15 RFQs no calibran 13 features ni threshold 0.85.
7. **Baseline medido vs. historico:** el cronometro manual sesga el resultado.
8. **Transferibilidad:** sin segundo vertical, FaberLoom puede ser solo una herramienta de calzado.
9. **Falso negativo por artefacto:** fallar el slice no implica fallar la tesis.
10. **Evidence bundle no-cotizacion:** requiere RFQs no-cotizacion, no solo cotizaciones.

### ALTERNATIVA mas fuerte

**Dual gate pre-S1:**
- **E0.25 -- Gate comercial:** obtener >=1 LOI o carta de intencion/pago de MWT o clientes piloto. Si falla, no se avanza.
- **E0.5 -- Gate tecnico mejorado:** slice single-tenant descartable con muestra estratificada (facil/medio/dificil/ruidoso), baseline historico, >=2 operadores, medicion de costo por draft, shadow mode/A/B cruzado, y firewall contra reutilizacion de artefactos.
- Si ambos pasan, arranca S1. Si cualquiera falla, se mata/replanta antes del SPINE.

### Nivel de confianza

**MEDIA.** El principio "validar valor antes de plomeria" es robusto, pero la especificacion actual de E0.5 tiene demasiados agujeros de medicion y deja fuera el riesgo comercial principal.

---

Changelog:
- v1.0 (2026-06-25): Red-team audit del gate E0.5. Veredicto MATIZADO; propuesta de dual gate E0.25 + E0.5 mejorado.
