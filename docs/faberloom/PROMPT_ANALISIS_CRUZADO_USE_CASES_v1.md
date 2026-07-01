# BRIEF - ANALISIS CRUZADO DE CASOS DE USO FABERLOOM - v1

**para:** asistente con capacidad de research/web + generacion de documentos.
**insumo (adjunto):** `ENT_FB_USE_CASE_CATALOG_v1.md` (58 casos ancla + esquema). Es semilla, NO techo.
**objetivo:** expandir, mapear competencia, reagrupar, puntuar impacto/viabilidad y cruzar todo para decidir el beachhead de FaberLoom.

FaberLoom = telar de copilotos: workspace heredable que se autoenriquece (HITL obligatorio + grounding + memoria + gobernanza). No es app por profesion; es la plataforma sobre la que un experto-cuello-de-botella teje su copiloto. Lee el catalogo antes de empezar.

---

## 1. Tareas (en orden)

**T1 - Expandir desde tu criterio.** Toma los 58 como piso. Agrega casos que yo NO vi (puntos ciegos), apuntando a ~120-150 unicos netos. No relleno: cada caso debe ser trabajo entrante repetitivo -> artefacto con responsabilidad -> requiere aprobacion humana -> deposita conocimiento. Si un caso no cumple los cuatro, no entra.

**T2 - Rastrear competidores (lo central).** Por cada familia y por los casos mas valiosos, identifica quien YA hace algo en esa linea:
- horizontales (ChatGPT/Enterprise, Glean, Microsoft Copilot, Notion AI, Gemini)
- verticales por profesion (ej. legal: Harvey, CoCounsel, Robin AI; contable: Pilot, Puzzle, Digits; soporte: Intercom Fin, Decagon; ventas: Clay, etc.)
Para cada competidor: que hace exactamente, modelo/precio si es publico, y el GAP que FaberLoom explota (o admitir que no hay gap). CITA fuente. Si no encontras, marca `[PENDIENTE-VERIFICAR]`. NO inventes competidores ni precios.

**T3 - Reagrupar familias con criterio (creativo).** Las 6 familias actuales son por industria. Propone 1-2 taxonomias alternativas mas utiles para decidir (ej: por forma-de-trabajo; por buyer+presupuesto+dolor; por fuerza de moat). Argumenta cual sirve mejor y reasigna los casos a esa.

**T4 - Puntuar impacto y viabilidad (rubricas abajo, no a ojo).** Por caso (o por cluster si son muchos): Impacto 1-5, Viabilidad 1-5, y score_beachhead = Impacto x Viabilidad. Justifica en 1 linea.

**T5 - Analisis cruzado (lo que mas quiero).**
- Matriz 2x2 Impacto x Viabilidad con los cuadrantes nombrados (ej: "Beachhead" alto-alto / "Apuesta" alto-bajo / "Relleno" bajo-alto / "Descartar" bajo-bajo).
- Heatmap de densidad de compliance por familia (cuantos ALTO de AI Act + sectoriales US).
- Mapa de espacio en blanco: casos de impacto alto + competidor debil/ausente + (bonus) AI Act ALTO donde el HITL+audit de FaberLoom es practicamente obligatorio. Eso es donde ChatGPT esta prohibido y el incumbente no llego: el wedge.

**T6 - Sintesis.** Top 10 beachhead rankeados, cada uno con "por que ahora / por que FaberLoom / por que no ChatGPT". Y 3 hallazgos contraintuitivos (donde el dato te sorprendio).

---

## 2. Rubricas (anclas 1-5, para que el score no sea arbitrario)

**Impacto** = frecuencia del dolor x horas ahorradas x WTP x cantidad de profesionales con ese dolor.
- 1 = dolor raro, ahorra minutos, sin presupuesto.
- 3 = dolor semanal, ahorra horas, presupuesto moderado, mercado mediano.
- 5 = dolor diario, ahorra muchas horas, paga bien, mercado grande.

**Viabilidad** = facilidad de build x (inverso del) drag regulatorio x (inverso del) cold-start x accesibilidad GTM x disponibilidad de datos para grounding.
- 1 = build complejo, regulacion brutal, cold-start largo, buyer inalcanzable, sin datos.
- 3 = build medio, regulacion manejable, cold-start medio, buyer alcanzable.
- 5 = build simple sobre el telar, regulacion ligera o ya cubierta por HITL, valor inmediato, buyer accesible, datos a mano.

---

## 3. Entregable (asi lo quiero, exactamente)

Dos piezas, en markdown (que se pueda mergear de vuelta a la KB), nada de slides por ahora:

**A) Tabla maestra** (una fila por caso, columnas reusables como CSV, en este orden):
```
id | familia_original | familia_reagrupada | industria_pro | uso | NEVER | compliance_US | compliance_EU_AIActTier | competidor_principal | que_hace | gap_FaberLoom | impacto_1a5 | viabilidad_1a5 | score_beachhead | fuente
```

**B) Sintesis ejecutiva (1-2 paginas):** la matriz 2x2, el heatmap de compliance, el mapa de espacio en blanco, el Top 10 beachhead, y los 3 hallazgos contraintuitivos. Prosa directa, tablas para comparar, sin relleno corporativo.

Reglas duras del entregable:
- Competidores y precios: citados o `[PENDIENTE-VERIFICAR]`. Cero invencion.
- Compliance: orientativo, no asesoria legal; marca lo dudoso.
- Honestidad sobre donde FaberLoom NO gana: si en una linea el incumbente ya domina, decilo. El valor del ejercicio es el espacio en blanco, no inflar el TAM.
- Si un cluster no da casos de calidad, dejalo corto y anota el gap. No rellenar para llegar a un numero.

---

## 4. Como te lo devuelvo a mi (Alvaro)

Pegame las dos piezas (tabla maestra + sintesis). Yo las consolido con el catalogo ancla en `ENT_FB_USE_CASE_CATALOG_v2.md`, dedupe, y append a `MANIFIESTO_CAMBIOS_v2`. Si la tabla es muy grande, mandala en bloques por familia reagrupada.
