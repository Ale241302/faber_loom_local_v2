# PROMPT KIMI SWARM - CASOS DE USO FABERLOOM - v2 (divergencia por lente + convergencia/cruce)

**uso:** dirigir un despliegue multiagente Kimi en DOS fases. Fase A diverge por lentes que se
SOLAPAN a proposito; Fase B converge: los puntos de encuentro entre agentes son la senal de
beachhead. La diversidad no importa en A; el solapamiento es el insumo de B.
**semilla obligatoria (adjuntar a cada agente):** `ENT_FB_USE_CASE_CATALOG_v1.md` (58 casos + esquema).
**direccion (hacia donde lo llevo):** encontrar el espacio en blanco = impacto alto + competidor ausente
+ (bonus) AI Act ALTO donde el HITL/audit de FaberLoom es casi obligatorio. Ahi ChatGPT esta prohibido
y el incumbente no llego. Ese es el objetivo, no "200 casos".

> Reglas Kimi (NO quitar): ancla en palabras sueltas e ignora contexto. Cada agente lleva (1) titulo
> de dominio linea 1, (2) guard de alcance, (3) RUN_ID, (4) prohibicion de palabras ambiguas,
> (5) "si dudas, detente". El solapamiento entre lentes es DESEADO; no lo trates como error.

---

## 0. Como correr

1. Adjuntar la semilla a CADA agente.
2. FASE A: lanzar los 5 agentes-lente (seccion 2) en paralelo. Cada uno escanea TODAS las industrias desde su lente y devuelve sus ~35 casos top. El solapamiento entre lentes es el punto.
3. FASE B: lanzar 1 agente agregador (seccion 3) que recibe las 5 salidas + la semilla, detecta convergencia, cruza y entrega.
4. (Opcional) FASE B2: un segundo agregador independiente repite el cruce; si coincide con B en el Top 10, el Top esta validado por doble pasada.

FaberLoom = telar de copilotos: workspace heredable que se autoenriquece, HITL obligatorio, grounding, memoria, gobernanza. No es app por profesion. Leer la semilla antes de empezar.

---

## 1. Guardrails globales (todo agente)

- Cada caso = trabajo entrante repetitivo -> artefacto del que el profesional es RESPONSABLE -> requiere aprobacion humana -> deposita conocimiento reutilizable. Si falla uno de los cuatro, no entra.
- Cada caso lleva NEVER autonomo obligatorio (firmar/enviar/mover/decidir/presentar).
- NO inventar leyes ni competidores. Sin certeza -> `[PENDIENTE-VERIFICAR]`.
- Palabras prohibidas (ambiguas): "varios", "etc", "entre otros", "gestion general", "soluciones".
- Salida = SOLO filas pipe-delimited (Fase A) o las secciones pedidas (Fase B). Cero prosa extra.
- El solapamiento con otros lentes y con la semilla es DESEADO: re-surgir un mismo caso cuenta como convergencia, no como duplicado a borrar.
- Si dudas del alcance, detente y pregunta.

---

## 2. FASE A - Agentes-lente (5 agentes, escanean TODAS las industrias)

Cada lente puntua desde SU angulo. Mismo caso visto por varios lentes = senal fuerte.

| Lente | RUN_ID | Mandato (que casos prioriza) |
|---|---|---|
| L1 Operador | UC-L1-oper-20260615 | maximo ahorro de horas, dolor diario, alto volumen de trabajo repetitivo |
| L2 Compliance-obliga | UC-L2-compliance-20260615 | donde AI Act ALTO o sectorial US (HIPAA/FINRA/FDCPA/FERPA/UPL) hace casi obligatorio el HITL+audit |
| L3 Espacio en blanco | UC-L3-whitespace-20260615 | donde NO hay incumbente IA fuerte (ni horizontal ni vertical); el competidor es debil o ausente |
| L4 Bolsillo/buyer | UC-L4-wtp-20260615 | donde hay presupuesto real y habito de comprar software (WTP alto) |
| L5 GTM/founder | UC-L5-gtm-20260615 | donde el beachhead es alcanzable: cold-start corto, canal accesible, valor inmediato |

### Template Fase A (pegar, reemplazar <LENTE>, <MANDATO>, <RUN_ID>)

```
CASOS DE USO FABERLOOM - LENTE: <LENTE>      # LINEA 1 = DOMINIO. NO BORRAR NI MOVER.
RUN_ID: <RUN_ID>

CONTEXTO (semilla adjunta): ENT_FB_USE_CASE_CATALOG_v1.md (esquema + 58 casos). Imita el esquema.
Puedes re-surgir casos de la semilla o de otros lentes: el solapamiento es deseado.

TU LENTE: prioriza casos segun <MANDATO>. Escanea TODAS las industrias, no una sola.

ALCANCE:
- Devuelve tus 35 casos TOP segun tu lente (de cualquier industria).
- Cada caso = trabajo entrante repetitivo -> artefacto con responsabilidad -> HITL -> deposita conocimiento.
- NEVER autonomo obligatorio. NO inventes leyes/competidores; sin certeza [PENDIENTE-VERIFICAR].
- NO uses: varios, etc, entre otros, gestion general, soluciones.

FORMATO (una fila por caso, pipe-delimited, este orden EXACTO):
id | industria_pro | workspace->hereda | trigger->uso->deposita | NEVER | compliance_US | compliance_EU_AIActTier | competidor_si_conoces | score_de_mi_lente_1a5 | por_que_segun_mi_lente

REGLAS:
- id: <RUN_ID>-NN
- score_de_mi_lente: 1-5 segun TU mandato (no impacto/viabilidad global; eso lo hace Fase B).
- competidor: solo si lo conoces con certeza; si no, [PENDIENTE-VERIFICAR].

ENTREGA: 35 filas. Nada mas. Si dudas, detente y pregunta.
```

---

## 3. FASE B - Agregador (convergencia + cruce + entregable)

Recibe: las 5 salidas de Fase A (~175 filas, con solapamiento) + la semilla (58).

```
ANALISIS CRUZADO CASOS DE USO FABERLOOM - AGREGADOR      # LINEA 1 = DOMINIO. NO BORRAR.
RUN_ID: UC-AGG-20260615

INSUMO: 5 salidas de lente (L1..L5) + semilla de 58 casos.

TAREAS (en orden):
1. CLUSTER: agrupa casos identicos o casi-identicos (mismo trigger+industria) aunque varie la redaccion.
   Por cluster calcula convergencia = cuantos lentes distintos (+semilla) lo surgieron. 1..6.
2. SCORE GLOBAL por cluster: Impacto 1-5 y Viabilidad 1-5 (rubricas abajo). score_beachhead = Impacto x Viabilidad.
3. COMPETENCIA: consolida el competidor por cluster (horizontal y/o vertical), que hace, y el gap de FaberLoom.
   Sin certeza -> [PENDIENTE-VERIFICAR]. NO inventar.
4. REAGRUPAR FAMILIAS: propone 1-2 taxonomias mas utiles que "por industria" (ej: por forma-de-trabajo,
   por buyer+presupuesto+dolor, por fuerza de moat). Elige la mejor y reasigna.
5. CRUCE (lo central):
   - Matriz 2x2 Impacto x Viabilidad, cuadrantes nombrados (Beachhead / Apuesta / Relleno / Descartar).
   - Heatmap de densidad de compliance por familia reagrupada (conteo de AI Act ALTO + sectoriales US).
   - Mapa de ESPACIO EN BLANCO: clusters con impacto alto + competidor debil/ausente + (bonus) AI Act ALTO.
   - Senal de convergencia: marca los clusters con convergencia >=3 (varios lentes coincidieron) como
     beachhead robustos. Convergencia alta + score alto = la apuesta.
6. SINTESIS: Top 10 por (convergencia x score_beachhead), cada uno con "por que ahora / por que FaberLoom /
   por que no ChatGPT". Mas 3 hallazgos contraintuitivos.

RUBRICAS:
- Impacto = frecuencia del dolor x horas ahorradas x WTP x cantidad de profesionales. 1 raro/minutos/sin pago; 3 semanal/horas/medio; 5 diario/muchas horas/paga bien/mercado grande.
- Viabilidad = facilidad de build x (inverso) drag regulatorio x (inverso) cold-start x accesibilidad GTM x datos para grounding. 1 todo en contra; 5 simple sobre el telar, regulacion ligera o cubierta por HITL, valor inmediato, buyer accesible.

ENTREGABLE (markdown, dos piezas):
A) TABLA MAESTRA, una fila por cluster:
   id | familia_reagrupada | industria_pro | uso | NEVER | compliance_US | compliance_EU_AIActTier | convergencia_1a6 | competidor | gap_FaberLoom | impacto_1a5 | viabilidad_1a5 | score_beachhead | fuente
B) SINTESIS (1-2 pag): la matriz 2x2, el heatmap, el mapa de espacio en blanco, el Top 10, y 3 hallazgos contraintuitivos.

REGLAS DURAS:
- Honestidad donde FaberLoom NO gana: si un incumbente ya domina un cluster, decirlo.
- Compliance orientativo, no asesoria legal; marcar lo dudoso.
- No inflar: si un cluster es debil, fuera. La convergencia y el espacio en blanco mandan, no el conteo.
```

---

## 4. Como me lo devuelven a mi (Alvaro)

Pegame el entregable de Fase B (tabla maestra + sintesis). Lo consolido en `ENT_FB_USE_CASE_CATALOG_v2.md`
(extiende v1, agrupado por la familia reagrupada, con columnas convergencia/competidor/scores), dedupe final,
y append a `MANIFIESTO_CAMBIOS_v2`. Si corres Fase B2 (segundo agregador), mandame ambos Top 10 y comparo convergencia entre agregadores.

## 5. Notas

- Si los agentes Kimi no tienen web, los competidores salen [PENDIENTE-VERIFICAR] y se validan despues (Claude/CLI con web). El resto del ejercicio (convergencia, scoring, cruce) no necesita web.
- Este prompt supersede el flujo sharded-por-industria de PROMPT_KIMI_SWARM_USE_CASES_v1: alli la cobertura mandaba; aca manda la convergencia. Si quieres ambas, corre v1 (cobertura ancha) y v2 (senal por convergencia) y yo fusiono.
