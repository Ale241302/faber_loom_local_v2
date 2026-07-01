# SPEC_FABERLOOM_ISOTIPO_DECISION_v1.md

| id | FAB-ISO-2026 |
| version | 1.0.0 |
| status | DRAFT → RECOMMENDED |
| visibility | INTERNAL |
| domain | faberloom |

## Resumen ejecutivo

Tras evaluar los tres isotipos en exploracion (Trama, Hilos entrelazados, Nudo celtico moderno) bajo seis criterios cuantificables centrados en viabilidad tecnica, coherencia de marca y diferenciacion de mercado, **Hilos entrelazados** emerge como la opcion recomendada con una puntuacion total de 24/30. Este isotipo logra el mejor equilibrio entre asociacion semantica con el concepto de "telar" (el hacedor que teje), coherencia tipografica con el wordmark dual (serif italic + sans bold), y capacidad de transformarse en un progress indicator animado que se siente parte del mismo sistema visual. Las otras dos opciones (Trama y Nudo celtico moderno) empatan en 20/30 pero presentan debilidades criticas: Trama sufre de falta de originalidad frente a la saturacion de iconos grid en el mercado SaaS, mientras que el Nudo celtico moderno arrastra connotaciones sobreusadas de "conectividad generica" y ofrece menor expresividad en animacion.

## Tabla comparativa

| Criterio | Trama | Hilos entrelazados | Nudo celtico moderno |
|---|---|---|---|
| 1. Reconocimiento a 16/24/32px | 2 | 3 | 4 |
| 2. Asociacion semantica | 4 | 5 | 3 |
| 3. Reproducibilidad | 5 | 4 | 5 |
| 4. Escalabilidad como progress indicator | 4 | 5 | 3 |
| 5. Originalidad vs saturacion de mercado | 2 | 3 | 2 |
| 6. Coherencia con wordmark | 3 | 4 | 3 |
| **TOTAL** | **20** | **24** | **20** |

## Analisis por isotipo

### 1. Trama

**Puntuaciones por criterio con justificacion:**

- **Reconocimiento a 16/24/32px: 2/5.** A 16px, un grid de intersecciones se reduce a un patron de cuadrados o puntos que es funcionalmente indistinguible de un icono generico de "grid" o "layout" de cualquier sistema de design (Figma, Sketch, Notion). A 24px mejora marginalmente. A 32px las intersecciones comienzan a leerse como trama, pero el limite entre "tejido" y "cuadricula de Excel" sigue siendo tenue. No tiene silueta propia.

- **Asociacion semantica: 4/5.** La relacion con "telar" es directa e inmediata: una trama es literalmente el producto de un telar. Sin embargo, pierde un punto porque funciona mejor como metafora de "resultado" (el tejido ya hecho) que de "proceso" (el acto de tejer). Para un producto cuyo mantra es "la IA prepara, vos tejes", esto es un desfase semantico relevante.

- **Reproducibilidad: 5/5.** Es el mejor de los tres en este eje. Líneas rectas, intersecciones limpias, monocromo impecable. Funciona en ink sobre cream, coral sobre cream, cream sobre ink, y cualquier combinacion intermedia. No depende de grosores de linea criticos ni de curvas que se degraden a baja resolucion.

- **Escalabilidad como progress indicator: 4/5.** La trama que se "teje" progresivamente — aparicion secuencial de intersecciones o filas que se completan — es visualmente coherente y tecnicamente simple de implementar (stroke-dasharray, opacidad por celda). Pierde un punto porque la animacion de un grid tiende a ser mecanica, casi industrial, y menos "organica" que hilos en movimiento. Puede sentirse como una planilla de calculo cargando, no como un artesano trabajando.

- **Originalidad vs saturacion de mercado: 2/5.** Este es el talon de Aquiles. Notion usa bloques grid. Linear usa gradientes abstractos pero muchos SaaS de productividad recurren a grids como iconos genericos. Un patron de trama, sin mayor distincion, puede confundirse con un icono de "spreadsheet", "table", o "database" a primera vista. No genera el "reconocimiento instantaneo de marca" que requiere un isotipo en el tier de Vercel, Raycast o Framer.

- **Coherencia con wordmark: 3/5.** El grid geometrico y ortogonal contrasta fuertemente con la curvatura y el flow de Crimson Pro Italic en "Faber". No compite abiertamente, pero tampoco dialoga. Es un vecino silencioso, no un companero. La combinacion funciona sin brillar.

**Fortalezas:**
1. Reproducibilidad tecnica perfecta — funciona en cualquier medio, cualquier color, cualquier resolucion.
2. Implementacion como SVG y favicon es trivial (rectas, no curvas).
3. Asociacion con "telar" es literal y universalmente comprensible.

**Debilidades:**
1. Silueta indistinguible de iconos genericos de grid/layout a tamanos pequenos.
2. Animacion como loader tiende a leerse mecanica/industrial, no artesanal.
3. No genera diferenciacion frente a la saturacion de grids en SaaS B2B.

**Confidence: medio.** La logica tecnica es solida, pero el riesgo de genericidad es alto y dificil de mitigar sin redisenar el concepto.

---

### 2. Hilos entrelazados

**Puntuaciones por criterio con justificacion:**

- **Reconocimiento a 16/24/32px: 3/5.** A 16px, las lineas curvas que se cruzan pueden reducirse a una forma abstracta que evoca una "S" estilizada o un nudo simplificado. No es perfecto — pierde detalle del "entrelazado" propiamente dicho. A 24px emergen los cruces y la sensacion de profundidad. A 32px se lee claramente como hilos que se tejen. La forma tiene suficiente silueta propia (no es un circulo, no es un triangulo, no es una letra) como para generar reconocimiento con exposicion repetida.

- **Asociacion semantica: 5/5.** Este es el criterio ganador. Las lineas que se cruzan y entrelazan evocan directamente el acto de tejer — no el producto final, sino el proceso. "La IA prepara, vos tejes" se vuelve visible: los hilos son las lineas de trabajo, el cruce es la decision del profesional. La metafora es clara sin ser obvia (no es un dibujo de telar realista) y funciona en multiples niveles de lectura: tejido textil, tejido de codigo, tejido de ideas.

- **Reproducibilidad: 4/5.** Funciona bien en monocromo (ink) y en color (coral sobre cream). Las curvas requieren atencion al grosor de linea — a tamanos muy pequenos, hilos demasiado finos se pierden. En dark mode (cream sobre ink) las curvas brillan con naturalidad. Pierde un punto porque, a diferencia de Trama, el grosor de los trazos si importa: hay un "sweet spot" que debe respetarse.

- **Escalabilidad como progress indicator: 5/5.** Hilos que se deslizan, cruzan y entrelazan progresivamente es la animacion mas coherente con la identidad de marca. Puede implementarse como: (a) dos lineas que se aproximan y entrelazan, (b) un hilo continuo que se va tejiendo a si mismo, o (c) cruces que aparecen secuencialmente. La metafora del "tejer en progreso" es exactamente lo que un usuario quiere ver mientras FaberLoom "prepara" el trabajo. No hay animacion mas alineada con el manifiesto de marca.

- **Originalidad vs saturacion de mercado: 3/5.** Hilos entrelazados no es un territorio virgen — existe en branding textil, en logos de "conexion" y en algunos productos de colaboracion. Sin embargo, ninguno de los competidores de referencia (Linear, Vercel, Notion, Framer, Cursor, Raycast, Arc, Resend, Attio) usa este lenguaje. Se diferencia claramente de las geometrias puras (triangulos, arcos, flechas) y de las letras estilizadas. El riesgo de confusion es bajo; el riesgo de "parecerse a algo que ya existe" es moderado pero manejable con un tratamiento visual distintivo (grosor, curvatura, angulo de cruce).

- **Coherencia con wordmark: 4/5.** Las curvas dinamicas de los hilos dialogan bien con la fluidez de Crimson Pro Italic en "Faber" — ambos comparten un cierto "movimiento calligrafico". A su vez, la energia de los hilos cruza con la solidez de Inter Bold en "Loom", creando un sistema de tres elementos (serif + sans + isotipo) que funciona como triangulo compositivo. No es perfecto (las curvas del isotipo son mas organicas que las rectas de Inter), pero es el mejor match de los tres.

**Fortalezas:**
1. Asociacion semantica perfecta con el acto de tejer — alinea con el manifiesto de marca.
2. Animacion como progress indicator es la mas expresiva y coherente del set.
3. Se diferencia claramente de la geometria pura de los competidores de referencia.

**Debilidades:**
1. A 16px pierde parte del "entrelazado", requiere diseno cuidadoso del grosor de linea.
2. El grosor de los hilos debe mantenerse dentro de un rango estrecho para legibilidad multi-resolucion.
3. Existe riesgo moderado de evocar branding textil tradicional si el tratamiento no es moderno suficiente.

**Confidence: alto.** El liderazgo en los criterios mas importantes (asociacion semantica, animacion, coherencia) supera con creces las debilidades tecnicas manejables.

---

### 3. Nudo celtico moderno

**Puntuaciones por criterio con justificacion:**

- **Reconocimiento a 16/24/32px: 4/5.** De los tres, el nudo celtico tiene la silueta mas fuerte a 16px: una forma circular cerrada con lineas internas es inmediatamente reconocible como "algo" (un nudo, una roseta, un emblema). No se confunde con grids ni con letras. A 24px y 32px el entramado interno se lee con claridad. Es el mejor favicon candidato en terminos de silueta pura.

- **Asociacion semantica: 3/5.** El nudo sugiere "interconexion" y "continuidad sin fin", que es metaforicamente relevante para un producto de flujo de trabajo. Sin embargo, el vinculo con "telar" es indirecto: un nudo no es un tejido. Se lee mas como "union" o "eternidad" que como "hacedor tejiendo". Para un publico de studios de diseno y agencias creativas, el nudo celta arrastra connotaciones de "artesanía folk" o "misticismo irlandes" que pueden desviar la lectura del posicionamiento deseado (moderno, preciso, profesional).

- **Reproducibilidad: 5/5.** Lineas continuas, curvas suaves, monocromo excelente. Al igual que Trama, el nudo funciona en cualquier combinacion de la paleta sin perdida de informacion. No depende de colores para transmitir su estructura — la forma lo es todo.

- **Escalabilidad como progress indicator: 3/5.** Un nudo que se "aprieta" o se dibuja progresivamente es visualmente interesante pero menos dinamico que hilos en movimiento. La animacion tiende a leerse como "construccion de una forma estatica" en lugar de "proceso continuo de tejido". Puede funcionar como un "draw-on" SVG, pero no tiene la misma resonancia con el concepto de "la IA esta preparando, vos estas tejiendo".

- **Originalidad vs saturacion de mercado: 2/5.** Los nudos celtas y sus variantes geometricas estan sobredeterminados en branding: desde productos de wellness hasta startups de "conectividad" pasando por cervezas artesanales. Spotify utilizo una variante de nudo interconectado. El riesgo de asociaciones no deseadas ("zen", "artesanía rustica", "movimiento New Age") es real, especialmente para un SaaS B2B dirigido a studios de diseno sofisticados. No hay un competidor directo en la lista de referencia que use nudos, pero el territorio visual esta saturado en cultura visual general.

- **Coherencia con wordmark: 3/5.** La geometría circular del nudo no dialoga especialmente bien ni con la horizontalidad del wordmark ni con la dicotomía serif/sans. Es un tercer elemento que coexiste pero no enriquece. Funciona como sello/emblema complementario, no como extension del sistema tipografico.

**Fortalezas:**
1. Silueta inmejorable a 16px — forma circular cerrada reconocible al instante.
2. Reproducibilidad perfecta en cualquier combinacion de color y resolucion.
3. Monocromo impecable, ideal para impresion y usos restrictivos.

**Debilidades:**
1. Vinculo con "telar/tejido" es metaforico y debil — "interconexion" no es "hacedor tejiendo".
2. Riesgo de connotaciones no deseadas (folk, misticismo, wellness) en el publico objetivo.
3. Animacion como progress indicator es estatica, menos alineada con el manifiesto de marca.

**Confidence: bajo.** Aunque tecnicamente solido, los riesgos de lectura semantica y de saturacion cultural superan las ventajas de silueta. Requeriria un tratamiento visual tan moderno y distante del nudo celta tradicional que, en la practica, terminaria pareciendose a la opcion 2 (hilos entrelazados) pero con una restriccion geometrica (circular) que limita su expresividad.

## Recomendacion final

- **Isotipo seleccionado:** Hilos entrelazados
- **Puntuacion total:** 24/30
- **Justificacion:** Hilos entrelazados lidera en los dos criterios mas alineados con la identidad de FaberLoom: asociacion semantica con el acto de tejer (5/5) y capacidad de transformarse en un progress indicator que materializa el manifiesto de marca (5/5). Su coherencia con el wordmark dual (4/5) lo convierte en un sistema visual integrado, no en un adjunto. Las debilidades (legibilidad a 16px, sensibilidad al grosor de linea) son tecnicamente manejables mediante diseno cuidadoso del SVG y definicion de grosores minimos en el design system. La alternativa Trama es tecnicamente perfecta pero genericamente indistinguible; el Nudo celtico tiene silueta fuerte pero arrastra connotaciones que desvian del posicionamiento.
- **Confidence: alto**

## 3 variantes de aplicacion

### A. Monocromo (ink sobre cream / cream sobre ink)

**Descripcion de como se adapta:**
Los hilos se renderizan como trazos de un solo color (ink #1F1E1C sobre fondo cream, o cream #F4F1ED sobre fondo ink). El entrelazado se resuelve mediante interrupciones estrategicas de las lineas (gap en el cruce) para simular "por encima/por debajo" sin necesidad de color de relleno. El grosor de linea principal es 2px en la version estandar (32px) y se escala proporcionalmente: 1.5px a 24px, 1px a 16px. No hay degradados, no hay sombras, no hay tramas de fondo.

**Uso:**
- Favicon .ico (16x16, 32x32, multi-resolucion)
- Header impreso (facturas, contratos, documentacion)
- Situaciones de 1-color (serigrafía, grabado laser, tinta de sello)
- Contextos de baja resolucion donde el coral no puede usarse

### B. Color (coral #C96442 sobre cream #F4F1ED)

**Descripcion:**
Los hilos se renderizan en coral solido (#C96442) sobre fondo cream (#F4F1ED). El entrelazado puede resolverse de dos maneras: (a) monocromo coral con gaps en cruces, o (b) variante de dos tonos donde un "hilo" es coral y el otro es pizarra (#5A6B7C), alternando en los cruces. La version bicolor es la preferida para aplicaciones de branding principal porque refuerza la metafora de "dos hilos" (humano + IA) que se entrelazan.

**Uso:**
- App icon (iOS, Android, macOS, Windows)
- Branding principal (web, landing, pitch deck)
- Splash screen y pantallas de onboarding
- Stickers, merch, senalizacion de espacio fisico (si aplica)

### C. Dark mode (cream #F4F1ED sobre ink #1F1E1C, con coral como acento)

**Descripcion:**
En dark mode, los hilos principales son cream (#F4F1ED) sobre fondo ink (#1F1E1C). El coral (#C96442) funciona como acento puntual: puede iluminar un punto de cruce especifico, indicar el "hilo activo" en la animacion de progress, o resaltar una porcion del entrelazado. La proporcion es 80% cream / 20% coral para no competir con el wordmark que usa coral en "Loom". El entrelazado se resuelve con gaps o con sombra sutil (ink mas claro, #2A2927) para dar profundidad sin salir de la paleta.

**Uso:**
- Dark mode editorial (blog, documentacion, help center)
- OLED (interfaces de la app en modo oscuro)
- Preferencia del usuario (sistema operativo en dark mode)
- Contextos de presentacion (proyeccion, pantallas de alto contraste)

## Notas de implementacion para ingenieria

### SVG (viewBox, paths principales)

- **viewBox recomendado:** `0 0 32 32` para la base, exportando a 16x16, 24x24 y 32x32.
- **Estructura:** Dos paths curvos (cubic bezier) que se cruzan en el centro. Cada path tiene gaps calculados en los puntos de interseccion para simular entrelazado.
- **Path principal (hilo 1):** Curva que entra desde top-left, describe un arco suave hacia bottom-right, pasando por el centro.
- **Path principal (hilo 2):** Curva que entra desde top-right, describe un arco suave hacia bottom-left, cruzando el hilo 1.
- **Gaps en intersecciones:** Calcular los puntos de cruce exactos (t parameter en la curva) y usar `stroke-dasharray` con valores precisos para crear la interrupcion. Alternativa: dibujar cada tramo como path separado sin necesidad de dasharray.
- **stroke-linecap:** `round` obligatorio. `square` o `butt` rompen la ilusion de hilo continuo.
- **stroke-linejoin:** `round`.

### Optimizacion para favicon multi-resolucion

- Generar `.ico` con tres frames: 16x16 (1px stroke), 24x24 (1.5px stroke), 32x32 (2px stroke).
- Para 16x16: simplificar la curva a menos puntos de control. El cruce debe ser claro incluso con 1px de resolucion. Considerar version simplificada donde los hilos se cruzan en "X" suavizada en lugar de curva completa.
- Usar `favicon.ico` (multi-res) + `favicon-32x32.png` + `favicon-16x16.png` + `apple-touch-icon.png` (180x180, curva completa con 4px stroke).
- `svg` inline para el header de la app (cambia de color segun tema sin necesidad de nuevo asset).

### Animacion como progress indicator

- **Que animar:** `stroke-dashoffset` de los dos paths principales.
- **Tecnica:** Cada path comienza con `stroke-dasharray: 0 [total-length]` y anima a `[total-length] 0`. Los dos paths se desfasan 180 grados (uno comienza cuando el otro esta en la mitad).
- **Duracion recomendada:** 1.2s ciclo completo (ritmo calmado, acorde al voice/tone "calmo, preciso"). Easing: `ease-in-out` para inicio suave, o `cubic-bezier(0.4, 0, 0.2, 1)` para aceleracion controlada.
- **Variante secuencial:** En lugar de ambos hilos simultaneos, el hilo 1 se dibuja completamente (0.6s), luego el hilo 2 se entrelaza (0.6s), creando la ilusion de "tejido en progreso". Esta variante es la preferida para estados de carga larga (initial load, importacion de proyecto).
- **Accesibilidad:** Respetar `prefers-reduced-motion: reduce` — en ese caso, mostrar isotipo estatico sin animacion.

### Variantes que NO hacer (explicitamente prohibidas)

1. **NO gradientes.** Ni lineales ni radiales. La paleta de FaberLoom es plana y el isotipo debe respetar eso. Un gradiente en los hilos los haria parecer filamentos de luz o cables opticos, desviando la lectura.
2. **NO sombras, glows, dropshadows.** El voice/tone es "calmo, preciso", no "tecnologico futurista". Un glow coral competiria visualmente con el wordmark y romperia la restriccion de 1-color en impresion.
3. **NO version 3D/extrusionada.** No hay contexto de uso que justifique una version tridimensional. El producto es SaaS, no packaging fisico.
4. **NO animacion de "girar" o "orbitar".** Los hilos no son un planeta ni una particula. La animacion debe ser "tejer", no "orbitar". Rotar el isotipo como spinner generico rompe la coherencia semantica.
5. **NO cambiar el angulo de entrelazado por capricho.** El cruce debe mantenerse consistente (mismo angulo, mismo punto de interseccion) en todas las aplicaciones. No crear versiones donde los hilos son paralelos, verticales, o forman otra letra.
6. **NO usar como contenedor de otros iconos.** El isotipo no debe funcionar como "circulo de fondo" sobre el cual se superpone una letra, un check, o un numero. Es un isotipo autonomo.

## Riesgos y mitigaciones

| Riesgo | Severidad | Mitigacion |
|---|---|---|
| A 16px el entrelazado no se lee y parece una forma abstracta generica | Media | Disenar version simplificada especifica para 16x16 donde los hilos forman una "X" suavizada con un punto de cruce claro. Probar en dispositivos reales antes de shippear. |
| Hilos entrelazados puede evocar branding textil tradicional (moda, telas, upholstery) | Media | Tratamiento visual moderno: curvas controladas (no organicas excesivas), angulo de cruce geometrico (no aleatorio), grosor uniforme (no variacion de peso). Evitar texturas de "hilo" ( fibras, deshilachado). |
| Animacion de progress indicator puede sentirse lenta si la duracion es 1.2s en contextos de espera corta | Baja | Tener dos variantes de velocidad: 0.8s para micro-loading (botones, tabs) y 1.2s para macro-loading (pantalla completa). Ambas con el mismo easing. |
| Existe riesgo de que, sin contexto del wordmark, el isotipo solo no evoque "FaberLoom" | Media | Aceptable para un isotipo — el reconocimiento se construye con exposicion repetida. El isotipo + wordmark deben aparecer juntos en los primeros 6 touchpoints del usuario. Luego el isotipo solo funciona como ancla. |
| El grosor de linea optimo para 32px puede ser demasiado grueso para 180px (app icon) | Baja | Definir grosor relativo al viewBox, no absoluto en px. El stroke debe ser ~6% del viewBox (1.8px en 32, 10px en 180). Esto se gestiona automaticamente si el SVG usa viewBox correctamente. |
| Competidores futuros podrian adoptar lenguaje de "hilos/tejido" | Baja | No mitigable por diseno. La defensa es la velocidad de construccion de marca: FaberLoom debe asociar "hilos entrelazados" con su producto antes de que otros entren al territorio. Priorizar visibilidad del isotipo en el launch. |
