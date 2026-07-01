# SPEC_FABERLOOM_PERSONAS_JTBD_v1.md

| id | FAB-PER-2026 |
| version | 1.0.0 |
| status | DRAFT |
| visibility | INTERNAL |
| domain | faberloom |

## Resumen ejecutivo

Esta investigacion identifica 5 personas arquetipicas del "hacedor moderno" de FaberLoom — profesionales creativos y de conocimiento que combinan oficio artesanal con herramientas digitales — y 16 JTBD maestros ranqueados por frecuencia x criticalidad. El hallazgo central: **el 70% de los profesionales creativos ocultan su uso de AI por estigma profesional** (Anthropic, 2025), y los disenadores especificamente muestran el patron emocional mas problematico: **alta frustracion con baja satisfaccion** hacia las herramientas de AI actuales. Esto representa tanto un riesgo de adopcion como una oportunidad de diferenciacion para FaberLoom si el Trust Ladder se implementa con respeto genuino por el control creativo.

---

## Definicion del "hacedor moderno"

### Quien ES

El hacedor moderno es un profesional de alto rendimiento cuyo valor economico y profesional descansa en **combinar juicio experto con ejecucion tecnica**. Es alguien que:

- Produce entregables tangibles (diseños, estrategias, codigo, piezas fisicas) para clientes exigentes
- Trabaja en equipos pequenos o solitarios donde cada persona cubre multiples roles
- Ha invertido anos desarrollando un "oficio" que define su identidad profesional
- Necesita herramientas que amplifiquen su capacidad sin reemplazar su juicio
- Mide el exito por la calidad del output y la satisfaccion del cliente, no por la velocidad pura

### Quien NO es

- **No es un operador industrial de linea de produccion**: no busca automatizar por completo su trabajo; busca eliminar fricciones
- **No es un no-code citizen developer**: tiene fluidez tecnica y espera poder "abrir el capot" cuando necesite
- **No es un early adopter desconsiderado**: evalua herramientas con escepticismo profesional antes de adoptarlas
- **No es un equipo enterprise con IT dedicado**: instala, configura y mantiene sus propias herramientas

### Diferenciadores del hacedor moderno

| Dimension | Hacedor moderno | Operador tradicional | Power user enterprise |
|-----------|-----------------|---------------------|----------------------|
| Relacion con el trabajo | Identidad profesional vinculada al oficio | Ejecucion de tareas asignadas | Optimizacion de metricas de equipo |
| Tolerancia a la autonomia de AI | Baja inicial, progresiva si hay confianza | Alta (cuanto menos haga, mejor) | Media (depende de politicas) |
| Metrica de exito | Calidad del entregable + satisfaccion cliente | Throughput + zero defect | ROI cuantificable + compliance |
| Stack tecnologico | Auto-curado, heterogeneo, cambia segun proyecto | Definido por la empresa | Estandarizado por IT |
| Decision de adopcion | Individual o por influencia de pares | Impuesta por supervisor | Comite de evaluacion |

**Confidence nivel: ALTO** — basado en estudios de Anthropic (2025), Atlassian (2026), y reportes de industria de consultoria y agencias creativas.

---

## Personas arquetipicas

### Persona 1: Diana Crespo — Directora Creativa

**Rol**: Directora Creativa / Socia en agencia boutique de branding y contenido (4-12 personas)

**Contexto**: Agencia independiente que atiende 6-10 clientes simultaneos, con proyectos que van desde identidad de marca hasta campanas digitales integrales. Diana divide su tiempo entre liderazgo creativo, revision de entregables y gestion comercial. La agencia no tiene equipo de IT; cada profesional maneja su propio stack. Factura por proyecto o retainer mensual; el margen depende directamente de la eficiencia operativa.

**Perfil psicografico**:

- **Motivaciones**: Preservar la integridad creativa de la agencia, ganar reconocimiento del industry (premios, casos de estudio), mantener autonomia profesional frente a grandes grupos publicitarios
- **Miedos**: Que el AI "aplane" el trabajo creativo haciendolo generico; perder talento senior que se siente desplazado; que los clientes descubran que usan AI y renegocien a la baja; perder el "gusto" y el criterio estetico por delegar demasiado en algoritmos
- **Aspiraciones**: Que la agencia sea conocida por ideas brillantes, no por ser "la mas rapida"; construir un equipo hibrido humano-AI donde el AI haga el trabajo de produccion y el humano el de concepcion
- **Relacion con tecnologia**: Competente pero no entusiasta. Ve la tecnologia como medio, no como fin. Prueba herramientas nuevas cuando un colega de confianza se las recomienda, no por hype. Tiene alta sensibilidad al "tokenismo de AI" (herramientas que prometen mas de lo que cumplen)

**Tech stack tipico**:

- Diseno: Figma (equipo), Adobe Creative Cloud (individual), After Effects
- Proyectos: Notion o ClickUp para tracking, Slack para comunicacion
- AI actual: ChatGPT para brainstorming, Midjourney para moodboards, ocasionalmente Firefly para retoques
- Archivos: Google Drive / Dropbox, sin DAM formal

**Jobs principales con agentes IA** (ranqueados por frecuencia):

1. **Generar y evaluar variantes creativas rapidamente** — diario — ALTA — "Cuando tengo que presentar 3 direcciones creativas al cliente, quiero que el agente prepare bases visuales/textuales de cada variante, para poder elegir y refinar en minutos en lugar de horas"
2. **Revisar y ajustar tono de marca en todos los entregables** — diario — ALTA — "Cuando el equipo genera contenido para multiples canales, quiero que el agente verifique consistencia de voz y valores de marca, para no tener que revisar manualmente cada pieza"
3. **Producir versiones adaptadas de una pieza maestra** — semanal — MEDIA — "Cuando apruebo una pieza creativa, quiero que el agente genere los cortes y adaptaciones para cada formato/plataforma, para no perder tiempo en reformato mecanico"
4. **Documentar y preservar criterios creativos de la agencia** — mensual — ALTA — "Cuando un nuevo disenador se suma o un cliente pregunta 'por que asi?', quiero que el agente tenga acceso al criterio historico de decisiones creativas, para mantener coherencia sin depender de mi memoria"
5. **Analizar performance de piezas publicadas para retroalimentar creatividad** — semanal — MEDIA — "Cuando salen metricas de engagement, quiero que el agente las traduzca a insights accionables para el equipo creativo, para cerrar el ciclo entre datos y creatividad"

**Metricas de exito** (como mide que FaberLoom funciona):

1. Tiempo de revision de entregables reducido en 40%+ sin que ella sienta que "perdio control de calidad"
2. Clientes que no detectan (ni les importa) que se uso AI en el proceso; el output se siente "hecho a mano"
3. Reduccion de rondas de revision internas de 3-4 a 1-2 por proyecto
4. Equipo creativo que reporta sentirse "apoyado, no reemplazado" por la herramienta

**Anti-jobs** (cosas que NO quiere que el agente haga):

1. **Generar ideas creativas finales sin su aprobacion activa** — "El dia que una idea se genera sola y yo solo tengo que decir 'ok', dejo de ser directora creativa y me convierto en aprobadora de algoritmos. Eso no es lo que me gusta, ni lo que mis clientes pagan."
2. **Comunicarse directamente con clientes** — "La relacion con el cliente es nuestra ventaja competitiva. Un robot no entiende la sutileza de un 'me gusta pero no se que tiene'."
3. **Aprender sus preferencias "a escondidas"** — "Si el agente cambia su comportamiento sin explicarme por que, empiezo a desconfiar. Quiero ver el diario de decisiones, no magia."

**Momento de maxima frustracion** (pain point critico):

> "Tarde 45 minutos configurando un prompt en una herramienta de AI para que generara un copy para una campana. El resultado fue... decente. Pero luego tarde otros 30 minutos reescribiendolo para que sonara como NOSOTROS y no como un chatbot. Al final no ahorre tiempo, solo lo redistribui. Y senti que estaba haciendo trampa sin el beneficio del truco."

**Momento de maxima satisfaccion** (delight potential):

> "Elegi una direccion creativa de entre tres opciones que el agente preparo. En lugar de empezar de cero, tenia un marco con tono, referencias visuales y un primer esqueleto de copy que ya capturaba la esencia. Solo tuve que pulir. Me senti como directora, no como operadora. Eso es lo que quiero."

**Quote representativo**:

> "Mi equipo no necesita mas velocidad. Necesita mas espacio para pensar. Si el AI les da eso, lo adopto manana. Si solo los hace correr mas rapido en la misma cinta, no me interesa."

**Confidence nivel: ALTO** — sustentado por estudios de Anthropic sobre stigma creativo, investigacion de Writer.com sobre identidad profesional, y reportes de agencias sobre resistencia a AI.

---

### Persona 2: Sergio Vasquez — Lead Designer

**Rol**: Lead Designer / Diseñador Senior en estudio de producto digital o branding (3-8 personas)

**Contexto**: Estudio especializado en productos digitales (UX/UI) o identidades de marca para startups y scale-ups. Sergio es el responsable tecnico-creativo: convierte briefs en sistemas de diseno, revisa el trabajo del equipo, y hace handoff a desarrollo. Trabaja con multiples proyectos simultaneos en fases diferentes (descubrimiento, diseno, handoff). No tiene tiempo para tareas repetitivas pero tampoco tolera que la calidad visual se degrade.

**Perfil psicografico**:

- **Motivaciones**: Construir sistemas de diseno elegantes y consistentes; ser reconocido por la calidad del craft; que los productos que disena "se sientan bien" al usarse
- **Miedos**: Que la AI genere "diseno genericamente aceptable" que nadie ame ni odie; perder el control sobre detalles de espaciado, tipografia y color que definen la calidad; ser visto como "el que usa AI" en lugar de "el buen disenador"
- **Aspiraciones**: Tener un "aprendiz digital" que maneje la mecanica (renombrar capas, generar variantes, documentar componentes) mientras el se concentra en interacciones, flujos y decisiones de sistema
- **Relacion con tecnologia**: Alta fluidez tecnica. Usa Figma como segunda naturaleza, conoce CSS, quizas algo de React. Espera que las herramientas sean precisas y predecibles. La inconsistencia le genera mas ansiedad que la complejidad.

> **Dato clave**: Segun el estudio de Anthropic (2025), los disenadores mostraron un patron emocional **inverso al resto de creativos**: dominados por la frustracion con satisfaccion notablemente baja. Son el segmento mas critico y menos complacido con las herramientas de AI actuales. [^76^]

**Tech stack tipico**:

- Diseno: Figma (avanzado: variables, componentes, Auto Layout), Framer para prototipos
- Comunicacion: Slack, Loom para feedback asincrono
- AI actual: Figma AI para prompts iniciales (con desconfianza), ChatGPT para UX writing, ocasionalmente Midjourney para moodboards
- Handoff: Figma Dev Mode, archivos organizados por paginas y secciones
- Productividad: Raycast o Alfred, VS Code para archivos de configuracion

**Jobs principales con agentes IA** (ranqueados por frecuencia):

1. **Preparar sistemas de diseno iniciales a partir de un concepto** — diario — ALTA — "Cuando tengo un moodboard y un brief, quiero que el agente genere una primera version del sistema de diseno (colores, tipografia, espaciado), para no partir de la pantalla en blanco"
2. **Generar y documentar variantes de componentes** — diario — MEDIA — "Cuando defino un componente base, quiero que el agente cree las variantes de estado y tamano siguiendo las reglas del sistema, para que yo no tenga que duplicar y ajustar manualmente"
3. **Verificar consistencia visual antes de handoff** — por proyecto — ALTA — "Cuando cierro una entrega, quiero que el agente escanee todas las pantallas para detectar inconsistencias de estilo, para que el desarrollador no encuentre sorpresas"
4. **Sintetizar feedback de stakeholders en acciones concretas** — semanal — MEDIA — "Cuando recibo comentarios dispersos de 5 personas en un Figma, quiero que el agente los agrupe por tema y sugiera cambios prioritizados, para no perder media hora decodificando contradicciones"
5. **Crear documentacion del sistema de diseno** — por proyecto — BAJA-MEDIA — "Cuando el sistema esta listo, quiero que el agente genere la documentacion de uso (cuando usar cada componente, reglas de combinacion), para que otros lo usen correctamente sin que yo tenga que escribir manuales"

**Metricas de exito** (como mide que FaberLoom funciona):

1. Tiempo de setup inicial de sistema de diseno reducido de 2-3 dias a <4 horas
2. Zero "inconsistencias visuales embarazosas" encontradas por desarrollo en handoff
3. Reduccion de tiempo en tareas mecanicas (renombrar, agrupar, documentar) en 60%+
4. El output del agente requiere "ajuste" en lugar de "rehacer" (>70% de reutilizacion)

**Anti-jobs** (cosas que NO quiere que el agente haga):

1. **Decidir la direccion creativa del proyecto** — "La AI no entiende el contexto de negocio, las restricciones del usuario, ni la vision del founder. Puede sugerir, pero la direccion la elijo yo."
2. **Modificar el archivo original sin rastro claro** — "Si el agente toca mi archivo, quiero ver exactamente que cambio y poder revertirlo. Un cambio 'silencioso' es un bug esperando a pasar a produccion."
3. **Generar diseno 'bonito pero incorrecto'** — "Midjourney hace imagenes hermosas que no se pueden construir. Necesito que el agente respete las restricciones tecnicas desde el minuto uno."

**Momento de maxima frustracion** (pain point critico):

> "Use Figma AI para generar una landing page a partir de un prompt. Me dio algo que SE VEIA profesional. Pero cuando empece a revisar, vi que el espaciado era inconsistente, usaba 4 tipografias diferentes, y habia componentes que parecen iguales pero no lo son. Tarde mas tiempo 'desarmando' el resultado para hacerlo mantenible que si lo hubiera hecho yo desde cero. Fue como heredar el codigo de otro: parece que funciona, pero esta lleno de deuda tecnica."

**Momento de maxima satisfaccion** (delight potential):

> "Dije 'prepara las 8 variantes de estado para este boton siguiendo el sistema' y el agente las genero en 30 segundos. Todas consistentes. Todas nombradas correctamente. Yo solo revise y aprobe. Ese tipo de tarea es puro trabajo mecanico que me quita tiempo para pensar en el flujo de usuario. Si el AI se queda con eso, soy feliz."

**Quote representativo**:

> "No quiero un AI que 'disene'. Quiero un intern que nunca se cansa de las tareas aburridas y que siempre sigue las reglas que yo le puse. La creatividad la dejo para mi."

**Confidence nivel: ALTO** — sustentado por el estudio de Anthropic sobre frustracion de disenadores, investigacion de Atlassian sobre trust en AI, y patrones de uso documentados de Figma AI.

---

### Persona 3: Camila Renau — Socia Consultora

**Rol**: Socia / Directora en consultora boutique de estrategia y transformacion digital (2-6 personas)

**Contexto**: Consultora independiente que asesora a empresas medianas en transformacion digital, estrategia de producto y optimizacion operativa. Camila factura por hora o por proyecto cerrado; su margen depende de la eficiencia con la que convierte investigacion en insights y propuestas. No tiene equipo de analistas dedicados; ella misma hace la mayor parte del trabajo de investigacion y sintesis. Sus clientes pagan por su juicio estrategico, no por la cantidad de horas que invierte.

**Perfil psicografico**:

- **Motivaciones**: Ser percibida como "la voz que ordena el caos" para sus clientes; construir una consultora que escale sin depender exclusivamente de su tiempo; generar IP reusable (frameworks, metodologias) que aumente el multiplicador de valor
- **Miedos**: Entregar un analisis con un dato incorrecto que desconfie al cliente; perder horas en tareas de produccion (formato de presentaciones, organizacion de notas) que no generan valor facturable; que el AI produzca algo que "suena bien pero esta mal" y ella no lo detecte
- **Aspiraciones**: Tener un "equipo de investigacion virtual" que le entregue borradores estructurados que ella refine con su juicio; pasar de "artesana del dato" a "arquitecta del insight"
- **Relacion con tecnologia**: Pragmatica. No le interesa la tecnologia per se; le interesa el resultado. Es de las primeras en probar herramientas nuevas si resuelven un dolor especifico, pero abandona rapido si no generan ROI claro. Prefiere pocas herramientas bien integradas a un stack fragmentado.

> **Dato clave**: Los consultores pierden un promedio de **8.2 horas por semana** buscando o recreando informacion, lo que cuesta a las organizaciones **$1.8 trillones anualmente** en productividad perdida. El 47% de los trabajadores digitales lucha por encontrar lo que necesitan. [^70^]

**Tech stack tipico**:

- Investigacion: Perplexity AI, ChatGPT, Google Scholar, bases de datos sectoriales
- Documentos: Notion (wiki del cliente), Google Docs, Microsoft Office para entregables formales
- Presentaciones: Gamma, Google Slides, PowerPoint
- Productividad: Otter.ai para transcripciones, Calendly, Stripe para facturacion
- AI actual: ChatGPT con "canales" separados por cliente, Claude para analisis de documentos largos

**Jobs principales con agentes IA** (ranqueados por frecuencia):

1. **Sintetizar investigacion de multiples fuentes en estructuras accionables** — diario — ALTA — "Cuando termino una ronda de entrevistas y lectura de fuentes, quiero que el agente organice los hallazgos en temas con citas y evidencia, para poder enfocarme en el analisis en lugar de en el ordenamiento"
2. **Generar propuestas de proyecto a partir de conversaciones previas** — semanal — ALTA — "Cuando tengo notas de 2-3 reuniones con un prospecto, quiero que el agente estructure una propuesta con alcance, metodologia y estimacion, para no partir de cero cada vez"
3. **Mantener coherencia entre entregables sucesivos del mismo cliente** — semanal — MEDIA — "Cuando preparo un nuevo entregable, quiero que el agente revise contra todos los documentos previos para detectar contradicciones o cambios de posicion, para no contradecirme entre reuniones"
4. **Documentar y recuperar insights de proyectos anteriores** — mensual — MEDIA — "Cuando enfrento un nuevo proyecto similar a uno pasado, quiero que el agente busque en mi historial y recupere frameworks, datos relevantes y lecciones aprendidas, para no reinventar la rueda"
5. **Preparar resumenes ejecutivos adaptados a cada stakeholder** — diario — MEDIA — "Cuando tengo un analisis detallado, quiero que el agente genere versiones resumidas adaptadas al nivel de detalle que necesita cada interlocutor (CEO vs. manager operativo), para que todos reciban el mensaje correcto"

**Metricas de exito** (como mide que FaberLoom funciona):

1. Tiempo de preparacion de propuestas reducido de 2 dias a <4 horas
2. Zero errores factuales en entregables asistidos por AI (verificados por ella)
3. Incremento de "proyectos simultaneos gestionables" de 3 a 5 sin bajar calidad
4. Clientes que mencionan "la velocidad de respuesta" como diferenciador en referencias

**Anti-jobs** (cosas que NO quiere que el agente haga):

1. **Fabricar datos o citas inexistentes** — "Una cita falsa o un dato inventado destruye mi reputacion. Prefiero que el agente diga 'no encontre evidencia' a que alucine una estadistica."
2. **Tomar decisiones estrategicas sin su validacion** — "El AI puede sugerer una estrategia, pero yo soy la que conozco al cliente, su cultura, sus limitaciones politicas. La decision es humana."
3. **Exponer informacion de un cliente en el contexto de otro** — "Trabajo con competidores indirectos. La confidencialidad no es negociable. Un solo leak y mi consultora termina."

**Momento de maxima frustracion** (pain point critico):

> "Pedile a ChatGPT que resumiera 20 paginas de notas de entrevista en temas. Lo hizo. Pero cuando fui a verificar, habia fusionado dos conceptos distintos en uno, eliminando una nuance critica que cambiaba el diagnostico. Si no revisaba palabra por palabra, entregaba un analisis incorrecto. La 'eficiencia' se convirtio en riesgo."

**Momento de maxima satisfaccion** (delight potential):

> "Le di las notas de tres reuniones con un prospecto, y el agente me entrego un borrador de propuesta con la estructura que yo uso, los temas mencionados, y una estimacion razonable de alcance. Yo solo ajuste el tono y agregue mi perspectiva estrategica. Lo envie esa misma tarde en lugar de dos dias despues. Ganamos el proyecto."

**Quote representativo**:

> "Mis clientes pagan por mi juicio, no por mi velocidad de escritura. El AI que necesito es el que me deje pensar mas y escribir menos."

**Confidence nivel: ALTO** — sustentado por datos de StratEngineAI, investigacion sobre knowledge management en consultoras, y reportes de productividad de consultores independientes.

---

### Persona 4: Tomas Weber — Lead Maker

**Rol**: Fundador / Lead Maker en taller de fabricacion digital y prototipado (2-5 personas)

**Contexto**: Taller boutique que combina fabricacion digital (impresion 3D, CNC, corte laser) con electronica e IoT para crear productos fisicos custom: desde prototipos para startups hasta instalaciones interactivas para espacios comerciales. Tomas divide su tiempo entre disenar soluciones tecnicas, operar maquinas, y coordinar con clientes que a menudo no tienen el lenguaje tecnico para describir lo que quieren. Cada proyecto es distinto; la repeticion es minima.

**Perfil psicografico**:

- **Motivaciones**: Resolver problemas fisicos complejos con soluciones elegantes; que el taller sea reconocido por la calidad del oficio tecnico; construir una practica sostenible sin convertirse en fabrica
- **Miedos**: Que un error en el proceso digital-physical produzca material desperdiciado o danos en maquinaria; perder el "toque artesanal" que diferencia su taller de una fabrica; que la AI subestime la complejidad de la fabricacion fisica
- **Aspiraciones**: Tener un sistema que documente cada proyecto de forma que sea reproducible y mejorable; reducir el tiempo de "traduccion" entre lo que pide el cliente y lo que hay que fabricar
- **Relacion con tecnologia**: Hibrida fisica-digital. Domina CAD/CAM, programacion de microcontroladores, y workflow de fabrication digital. Es escéptico de herramientas que no entiendan las restricciones fisicas (materiales, tolerancias, tiempos de maquina). Valida todo en el mundo fisico antes de confiar.

> **Dato clave**: La investigacion de CHI 2024 sobre Tandem muestra que los workflows de fabricacion digital sufren de tres problemas: (1) multiples herramientas de software interdependientes sin entorno unificado, (2) dificultad para sincronizar ajustes fisicos con parametros digitales, y (3) precondiciones implicitas que solo se aprenden por error. [^6^]

**Tech stack tipico**:

- CAD/CAM: Autodesk Fusion 360, Rhino, o SolidWorks
- Fabricacion: Ultimaker Cura, LaserGRBL, firmware de CNC
- Electronica: Arduino IDE, PlatformIO, EasyEDA
- Proyectos: Notion o spreadsheet simple, WhatsApp/Telegram con clientes
- Documentacion: Fotos con telefono, notas dispersas, GitHub para firmware

**Jobs principales con agentes IA** (ranqueados por frecuencia):

1. **Traducir requerimientos del cliente en especificaciones tecnicas** — por proyecto — ALTA — "Cuando un cliente dice 'quiero algo que se mueva cuando la gente se acerque', quiero que el agente me ayude a estructurar las opciones tecnicas (sensores, actuadores, materiales) con pros/contras estimados, para acelerar la fase de definicion"
2. **Documentar workflows de fabricacion para reproducibilidad** — por proyecto — ALTA — "Cuando desarrollo un proceso nuevo, quiero que el agente registre los parametros, ajustes y gotchas en un formato estandarizado, para que el proximo proyecto similar no parta de cero"
3. **Verificar que los archivos de fabricacion coinciden con la intencion de diseno** — diario durante produccion — ALTA — "Cuando preparo G-code o archivos de corte, quiero que el agente compare contra el modelo original y alerte sobre discrepancias (escalas, orientaciones, tolerancias), para evitar errores costosos en maquina"
4. **Coordinar comunicacion con clientes no tecnicos** — semanal — MEDIA — "Cuando tengo que explicarle a un cliente por que algo es complejo o costoso, quiero que el agente me ayude a traducirlo a lenguaje claro sin perder precision tecnica, para que entiendan el valor sin sentirse ignorantes"
5. **Gestionar inventario y compras de materiales** — semanal — BAJA — "Cuando planifico los materiales para los proyectos activos, quiero que el agente cruce requerimientos contra stock existente y genere listas de compra, para no quedarme sin material a mitad de un trabajo urgente"

**Metricas de exito** (como mide que FaberLoom funciona):

1. Reduccion de errores de fabricacion (piezas defectuosas, cortes incorrectos) en 50%+
2. Tiempo de "onboarding" de un nuevo proyecto reducido de 1-2 dias a <4 horas
3. Clientes que entienden y aprueban especificaciones tecnicas sin rondas interminables de preguntas
4. Biblioteca de procesos documentada y buscable que se reutiliza activamente

**Anti-jobs** (cosas que NO quiere que el agente haga):

1. **Modificar parametros de maquina sin confirmacion explicita** — "Un feed rate equivocado puede romper una fresa de $200 o peor, lesionar a alguien. Nada de la AI se ejecuta directamente en maquina sin mi visto bueno."
2. **Simplificar problemas tecnicos hasta hacerlos incorrectos** — "Decir 'usen un sensor de movimiento' es como decir 'usen un medicamento'. Hay 50 tipos, cada uno con restricciones. La simplificacion puede ser peligrosa."
3. **Ignorar las restricciones fisicas del mundo real** — "El software trabaja con numeros perfectos. El mundo fisico tiene tolerancias, expansion termica, desgaste. Si la AI no entiende eso, sus sugerencias son inutiles."

**Momento de maxima frustracion** (pain point critico):

> "Un cliente pidio una 'caja con luz'. Me tomo 3 idas y vueltas por WhatsApp entender que queria un display iluminado para un producto cosmetic. Si hubiera tenido una forma de traducir 'caja con luz' a las 5 opciones tecnicas posibles con imagenes y rangos de precio, hubieramos ahorrado una semana. En lugar de eso, fui dibujando en la marcha."

**Momento de maxima satisfaccion** (delight potential):

> "Documente el proceso de 'fresado de dos caras con alineacion por pasadores' con el agente. Dos meses despues, un proyecto similar llego. El agente recupero la documentacion, adapto los parametros al nuevo material, y genero un checklist de verificacion. Lo hice en 3 horas en lugar de 2 dias. Y salio perfecto a la primera."

**Quote representativo**:

> "En mi taller, el error cuesta plata real y tiempo real. No tengo paciencia para herramientas que viven en un mundo teorico. Muestrame que entendes el taller, y te dejo ayudarme."

**Confidence nivel: MEDIO-ALTO** — basado en investigacion academica (CHI 2024), plataformas como MakerStudio, y patrones de makerspaces documentados. Menos datos de mercado directo que otros segmentos.

---

### Persona 5: Valentina Rojas — Freelancer Senior

**Rol**: Freelancer Senior de diseno y desarrollo web (independiente, 1 persona)

**Contexto**: Valentina trabaja sola, atendiendo 4-8 clientes simultaneos de tamano medio (startups, pequenos negocios, otros freelancers que necesitan apoyo). Hace de todo: diseno visual, UX/UI, desarrollo frontend, y ocasionalmente consultoria estrategica. No tiene margen para dedicar tiempo a herramientas que no generen output facturable inmediato. Su reputacion es su activo mas valioso; un proyecto mal entregado puede costarle referencias.

**Perfil psicografico**:

- **Motivaciones**: Mantener independencia y autonomia profesional; seleccionar proyectos interesantes en lugar de acceptar todo por dinero; tener una vida mas alla del trabajo (no trabajar 60 horas semanales)
- **Miedos**: Que los clientes perciban que usa AI como "hacer trampa"; perder el control de calidad por delegar demasiado; quedarse obsoleta frente a freelancers mas jovenes que adoptan AI sin su escepticismo; la fragmentacion de herramientas que la hace pasar mas tiempo administrando que creando
- **Aspiraciones**: Tener un "socio digital" que maneje la parte operativa (seguimiento de proyectos, comunicacion de rutina, documentacion) mientras ella se enfoca en el trabajo creativo-tecnico; poder escalar su practica sin contratar
- **Relacion con tecnologia**: Muy fluida, pero **selectiva**. Prueba muchas herramientas pero adopta pocas. Su criterio de adopcion es: "me ahorra tiempo NETO (incluyendo el de aprenderla y configurarla)". Tiene aversion al vendor lock-in y a las suscripciones que se acumulan. Espera que las herramientas "simplemente funcionen" sin configuracion extensa.

> **Dato clave**: Los freelancers que adoptaron AI reportan ahorros de 8-15 horas semanales, pero el 69% de los trabajadores ocultan su uso de AI por estigma social. El 55% siente ansiedad sobre el impacto del AI en su futuro laboral. [^13^] [^68^]

**Tech stack tipico**:

- Diseno: Figma, ocasionalmente Adobe Illustrator
- Desarrollo: VS Code, GitHub, Vercel o Netlify
- Comunicacion: Slack con clientes, email, calendly
- Productividad: Notion personal, Trello o similar liviano
- AI actual: ChatGPT para brainstorming y debugging, GitHub Copilot para codigo, ocasionalmente Midjourney
- Facturacion: Stripe, Payoneer, o transferencia bancaria

**Jobs principales con agentes IA** (ranqueados por frecuencia):

1. **Mantener contexto de multiples proyectos sin mezclar informacion** — diario — ALTA — "Cuando cambio entre el proyecto A y el proyecto B, quiero que el agente recuerde donde quede y que es lo proximo en cada uno, para no perder 15 minutos 'volviendo a entrar' cada vez"
2. **Generar propuestas y estimaciones rapidamente** — semanal — ALTA — "Cuando llega una consulta nueva, quiero que el agente me ayude a estructurar un alcance y una estimacion basada en proyectos similares previos, para responder en horas en lugar de dias"
3. **Documentar entregables para handoff al cliente** — por proyecto — MEDIA — "Cuando entrego un sitio o un diseno, quiero que el agente genere la documentacion de uso (como actualizar, que no tocar, FAQ basica), para no tener que escribir manuales tecnicos que nadie lee"
4. **Seguimiento de comunicacion con clientes sin que se caiga nada** — diario — MEDIA — "Cuando un cliente pregunta 'como venimos?' o 'que paso con eso que dije?', quiero que el agente tenga el estado actualizado para responder rapido y preciso, para que sientan que los tengo presentes"
5. **Identificar oportunidades de up-sell o extension de proyecto** — mensual — BAJA-MEDIA — "Cuando reviso el estado de los proyectos activos, quiero que el agente sugiera donde hay oportunidad de ofrecer un servicio adicional, para aumentar ingresos sin ser agresiva"

**Metricas de exito** (como mide que FaberLoom funciona):

1. Tiempo semanal en tareas administrativas (seguimiento, documentacion, propuestas) reducido de 15-20h a <8h
2. Clientes que reportan "se siente como tener un equipo, no una persona"
3. Capacidad de atender 1-2 clientes adicionales sin aumentar horas trabajadas
4. Zero "se me cayo" en compromisos o comunicaciones con clientes

**Anti-jobs** (cosas que NO quiere que el agente haga):

1. **Comunicarse con clientes en su nombre sin review previo** — "Mi voz es mi marca. Un email que suena a chatbot me quema la relacion que tarde meses en construir."
2. **Hacer commitmenents de plazo o alcance sin su aprobacion** — "Solo yo se cuanto me cuesta hacer algo bien. La AI no siente la fatiga, no conoce mi calendario personal, no entiende 'no me apetece trabajar este finde'."
3. **Acumular otra suscripcion sin ROI claro** — "Ya pago por Figma, GitHub, ChatGPT, Notion, y Vercel. Cada nuevo $20/mes necesita justificarse en las primeras dos semanas o lo cancelo."

**Momento de maxima frustracion** (pain point critico):

> "Tengo 6 proyectos activos, 4 herramientas de productividad, y 3 suscripciones de AI que pago y uso a medias. Pasaba mas tiempo decidendo en cual herramienta registraba una tarea que haciendo la tarea en si. La fragmentacion es mi mayor enemigo. Necesito menos herramientas, no mas."

**Momento de maxima satisfaccion** (delight potential):

> "Le dije al agente 'prepara un resumen de estado para los 6 clientes' y en 5 minutos tenia 6 mensajes claros, con lo que se hizo, lo que viene, y lo que necesito de ellos. Los envie todos antes del almuerzo. Un viernes. Ese finde descanse sin culpa."

**Quote representativo**:

> "No quiero ser una empresa de una persona. Quiero ser una persona que produce como una empresa. El AI puede ser mi equipo invisible, pero yo sigo siendo la que firma el trabajo."

**Confidence nivel: ALTO** — sustentado por multiples estudios sobre freelancers y AI, datos de McKinsey sobre productividad, y patrones bien documentados de adopcion de SaaS por trabajadores independientes.

---

## JTBD maestros ranqueados

### Metodologia de ranqueo

Cada JTBD se puntua en dos dimensiones (1-5):
- **Frecuencia**: 1=esporadico, 5=diario
- **Criticalidad**: 1=nice-to-have, 5=bloqueante si no se resuelve

El score final = Frecuencia x Criticalidad (rango 1-25).

| ID | Job statement | Frec | Crit | Score | Personas | Estado FaberLoom | Confidence |
|----|---------------|------|------|-------|----------|-----------------|------------|
| JTBD-01 | Cuando recibo un brief o solicitud de un cliente, quiero sintetizar requerimientos dispersos en una estructura clara con acciones prioritizadas, para no perder horas decodificando lo que realmente necesitan | Diaria | Alta | 25 | P1, P2, P3, P4, P5 | Parcial (chat puede ayudar, falta template de brief) | ALTO |
| JTBD-02 | Cuando debo entregar un output creativo o estrategico, quiero que el agente prepare un borrador estructurado basado en mi estilo y criterios previos, para poder refinar en lugar de empezar de cero | Diaria | Alta | 25 | P1, P2, P3, P5 | Parcial (necesita memoria de estilo por tenant) | ALTO |
| JTBD-03 | Cuando tengo multiples proyectos activos, quiero mantener el contexto de cada uno sin mezclar informacion, para cambiar entre ellos sin perder 15 minutos "volviendo a entrar" | Diaria | Alta | 25 | P3, P5, P1 | No cubierto (falta gestion de contexto multi-proyecto) | ALTO |
| JTBD-04 | Cuando reviso entregables de mi equipo o de un agente AI, quiero verificar consistencia contra los criterios de calidad y estilo definidos, para asegurar que todo lo que sale lleva nuestra firma | Diaria | Alta | 25 | P1, P2 | Parcial (Sanidad tab puede cubrir, falta definicion) | MEDIO |
| JTBD-05 | Cuando finalizo una pieza creativa o entregable maestro, quiero generar las adaptaciones para cada formato, canal o stakeholder, para no perder tiempo en reformato mecanico | Semanal | Alta | 20 | P1, P2, P3, P5 | Parcial (Iterar tab puede ayudar) | ALTO |
| JTBD-06 | Cuando acumulo investigacion, notas o feedback de multiples fuentes, quiero organizarlos en temas accionables con citas, para enfocarme en analisis en lugar de ordenamiento | Semanal | Alta | 20 | P3, P5, P1 | Parcial (chat + posible integracion) | ALTO |
| JTBD-07 | Cuando preparo una propuesta comercial o estimacion, quiero estructurarla rapidamente basada en conversaciones previas y proyectos similares, para responder a prospectos en horas en lugar de dias | Semanal | Alta | 20 | P3, P5, P4 | No cubierto (falta template de proposal) | ALTO |
| JTBD-08 | Cuando recibo feedback de multiples stakeholders, quiero que se agrupe por tema, se detecten contradicciones, y se sugieran cambios prioritizados, para no perder tiempo en reuniones de alineacion interminables | Semanal | Media | 15 | P1, P2, P3 | No cubierto (falta modulo de feedback synthesis) | MEDIO |
| JTBD-09 | Cuando cierro una fase de proyecto, quiero documentar el proceso, decisiones y "gotchas" en un formato estandarizado buscable, para que el proximo proyecto similar no parta de cero | Por proyecto | Alta | 15 | P4, P3, P5 | No cubierto (falta knowledge base por tenant) | MEDIO |
| JTBD-10 | Cuando preparo archivos para produccion o handoff, quiero verificar que los outputs coinciden con la intencion original (escalas, formatos, parametros), para evitar errores costosos en la etapa final | Diaria (en produccion) | Alta | 20 | P4, P2 | No cubierto (falta modulo de QA tecnico) | MEDIO |
| JTBD-11 | Cuando trabajo con informacion confidencial de multiples clientes, quiero garantizar que los datos de un tenant nunca se mezclen ni filtren a otro, para preservar confidencialidad y cumplir contratos | Diaria | Alta | 25 | P3, P5, P1 | Cubierto (arquitectura multi-tenant) | ALTO |
| JTBD-12 | Cuando exploro una nueva direccion creativa o estrategica, quiero que el agente prepare opciones estructuradas con pros/contras y referencias, para tomar decisiones informadas sin analisis-paralysis | Semanal | Media | 15 | P1, P3, P4 | Parcial (chat puede ayudar) | ALTO |
| JTBD-13 | Cuando comunico con clientes no tecnicos, quiero traducir conceptos complejos a lenguaje claro sin perder precision, para que entiendan el valor sin sentirse ignorantes | Semanal | Media | 15 | P4, P3, P5 | Parcial (chat puede ayudar) | MEDIO |
| JTBD-14 | Cuando reviso metricas o datos de performance, quiero que se traduzcan a insights accionables para el trabajo creativo o estrategico, para cerrar el ciclo entre datos y decisiones | Semanal | Media | 15 | P1, P3 | No cubierto (falta integracion con analytics) | BAJO |
| JTBD-15 | Cuando detecto un cambio necesario en un proyecto activo, quiero que el agente evalue el impacto en el resto del sistema y alerte sobre efectos colaterales, para no romper algo sin darme cuenta | Semanal | Media | 15 | P2, P4 | No cubierto (falta impact analysis) | MEDIO |
| JTBD-16 | Cuando un nuevo colaborador se suma al proyecto, quiero que el agente le entregue el contexto relevante, reglas del proyecto y estado actual, para que pueda contribuir sin que yo invierta tiempo en onboarding | Esporadica | Media | 10 | P1, P2, P3 | No cubierto (falta onboarding assistant) | MEDIO |

### Analisis del portafolio JTBD

- **Cubierto o parcialmente cubierto por la arquitectura actual**: JTBD-01, 02, 04, 05, 06, 11, 12 (7 de 16)
- **No cubierto (oportunidades de roadmap)**: JTBD-03, 07, 08, 09, 10, 13, 14, 15, 16 (9 de 16)
- **Score total acumulado**: 310 puntos (maximo posible: 400)
- **Densidad en el top 5**: Los 5 JTBD de mayor score representan 115 de 310 puntos (37%), indicando que hay un nucleo duro de jobs de alta frecuencia/criticalidad que deberian ser prioridad absoluta de producto.

---

## Implicaciones de diseno

### Principios derivados de las personas

| Principio | Fuente | Implicacion en FaberLoom |
|-----------|--------|-------------------------|
| **El control visible es mas importante que la velocidad oculta** | P1, P2: el miedo a perder el oficio supera al deseo de ir rapido | El Trust Ladder debe ser explicito y visible en cada interaccion. El usuario siempre sabe en que nivel esta el agente y que va a hacer antes de hacerlo. |
| **La AI debe "mostrar su trabajo", no solo su resultado** | P3, P4: la confianza se construye con transparencia, no con output perfecto | Cada sugerencia del agente debe incluir: que hizo, por que lo hizo, y que parte necesita validacion humana. Sin esto, las personas de alto craft desconfian. |
| **El contexto multi-proyecto no es feature, es tabla de salvacion** | P3, P5: la fragmentacion de contexto es el dolor #1 de independientes | La arquitectura de "tenant = workspace" debe soportar multiples proyectos activos con aislamiento de contexto perfecto. El agente nunca mezcla informacion entre proyectos. |
| **La calidad del output se mide por lo que NO hay que rehacer** | P2, P4: "rehacer" es peor que "no usar AI" | El modulo de Sanidad no es un "nice to have". Es la garantia de que el output del agente cumple los estandares del tenant. Sin Sanidad, el Iterar tab es riesgoso. |
| **La AI disuelta es mas confiable que la AI presentada** | P1, P2: los "agentes" generan ansiedad; las capacidades integradas no | Segun Atlassian, disolver los agentes en "skills" integrados al flujo reduce ansiedad y aumenta adopcion. El chat-first de FaberLoom debe sentirse como "capacidades que invoco", no como "un ser que me ayuda". |
| **La memoria del estilo es el diferenciador** | P1, P2, P3: "que ya sepa como trabajamos" es el deseo unanime | La capacidad de FaberLoom para aprender y recordar el estilo, criterios y preferencias de cada tenant (no genericamente, no cross-tenant) es el diferenciador core frente a ChatGPT generico. |

### Implicaciones especificas por tab

**Configurar (Setup)**
- Debe incluir un "cuestionario de estilo" que capture la voz, criterios de calidad y restricciones del tenant
- El Trust Ladder se configura aqui: el usuario define en que nivel empieza el agente y que acciones requieren aprobacion
- Debe ser posible "importar" ejemplos previos de trabajo para que el agente aprenda el estilo

**Iterar (Trabajo)**
- Cada iteracion debe empezar con una propuesta clara que el usuario pueda aceptar, modificar o rechazar
- El contexto debe ser por proyecto, con aislamiento garantizado
- Las acciones del agente deben dejar rastro auditable (diario de decisiones)

**Sanidad (Revision/QA)**
- No es opcional ni posterior; es parte del workflow. El usuario puede invocar Sanidad en cualquier momento
- Debe verificar tanto consistencia interna (contra el estilo del tenant) como consistencia externa (contra entregables previos)
- Los resultados de Sanidad deben ser accionables: no "hay un error" sino "en la seccion X, el tono difiere del criterio Y; sugiero Z"

---

## Anti-patterns a evitar

Basados en los anti-jobs y momentos de maxima frustracion de las 5 personas:

### 1. **El "Magico Black Box" (Anti-pattern: opacidad)**
El agente hace algo y el usuario no entiende como ni por que. Las personas P1, P2 y P3 mencionan explicitamente que esto destruye la confianza.
- **Como se manifiesta**: Output sin explicacion, cambios sin contexto, decisiones sin trazabilidad
- **Consecuencia**: El usuario desconfia y vuelve a hacer todo manualmente (el agente se convierte en costo, no en valor)
- **Mitigacion en FaberLoom**: Toda accion del agente muestra: (a) que hizo, (b) por que lo hizo, (c) que parte requiere validacion humana

### 2. **El "Intern Sobresaliente" (Anti-pattern: sobre-autonomia)**
El agente es tan proactivo que toma decisiones que el usuario queria tomar. P1 y P2 lo odian: "el dia que una idea se genera sola, dejo de ser directora creativa."
- **Como se manifiesta**: Sugerencias que sienten como imposiciones, acciones automaticas que el usuario no aprobo, "me adivino" pero en realidad "me ignoro"
- **Consecuencia**: El usuario se siente desplazado, no apoyado. Resistencia activa a la adopcion.
- **Mitigacion en FaberLoom**: El Trust Ladder nunca avanza sin confirmacion explicita. En niveles bajos, todo es "sugiero y espero". En niveles altos, el usuario definio los guardarrailes.

### 3. **El "Chatbot Generico" (Anti-pattern: falta de memoria de estilo)**
El agente produce output que "suena a AI" porque no ha aprendido el estilo especifico del tenant. P1, P2, P3 y P5 lo mencionan como frustracion critica.
- **Como se manifiesta**: Copy que suena a ChatGPT, diseno que parece template, analisis que falta la "voz" del consultor
- **Consecuencia**: El usuario gana tiempo mecanico pero pierde tiempo en "despersonalizar" el output. ROI negativo.
- **Mitigacion en FaberLoom**: El onboarding de cada tenant incluye captura explicita de estilo. El agente nunca genera output sin contexto de estilo. La Sanidad tab verifica "voz de marca" como criterio.

### 4. **El "Mezclador de Contextos" (Anti-pattern: cross-contamination)**
El agente mezcla informacion entre proyectos o clientes. P3 lo define como existencial: "Un solo leak y mi consultora termina."
- **Como se manifiesta**: Referencias a proyecto A en una conversacion sobre proyecto B, sugerencias basadas en datos de otro cliente, "confusion" del agente sobre a que proyecto pertenece un archivo
- **Consecuencia**: Violacion de confidencialidad, perdida de credibilidad, riesgo legal
- **Mitigacion en FaberLoom**: Arquitectura multi-tenant con aislamiento fisico de datos. El agente nunca tiene acceso a datos de otro tenant. Los proyectos dentro de un tenant deben tener contexto separado por defecto.

### 5. **El "Todologo Inutil" (Anti-pattern: amplia pero superficial)**
El agente intenta hacer de todo pero nada bien. P4 y P5 lo sufren: "simplifica hasta hacerlo incorrecto", "me da 50 opciones genericas en lugar de 3 especificas."
- **Como se manifiesta**: Respuestas largas y genericas, sugerencias que no aplican al contexto especifico, "podrias hacer X, Y, Z o A, B, C" sin recomendacion
- **Consecuencia**: El usuario gasta tiempo filtrando ruido. La herramienta se percibe como "mas trabajo, no menos".
- **Mitigacion en FaberLoom**: El agente debe ser explicito sobre lo que SABE y lo que NO SABE. Las sugerencias deben ser pocas, justificadas, y accionables. El modulo de Sanidad debe detectar cuando el output es demasiado generico.

---

## Referencias y fuentes

### Estudios academicos e investigacion primaria

1. Anthropic (2025). "Introducing Anthropic Interviewer" — Estudio de 1,250 profesionales sobre uso y percepcion de AI. Hallazgo clave: 70% de creativos ocultan uso de AI; disenadores muestran alta frustracion y baja satisfaccion.
   - URL: https://www.anthropic.com/research/anthropic-interviewer [^76^]

2. The Decoder (2025). "70% of creative professionals hide AI use from colleagues due to stigma, Anthropic study finds" — Analisis del estudio Anthropic con citas directas de participantes.
   - URL: https://the-decoder.com/70-of-creative-professionals-hide-ai-use-from-colleagues-due-to-stigma-anthropic-study-finds/ [^13^]

3. Final Round AI (2025). "Anthropic Study Finds Most Workers Use AI Daily, but 69 Percent Hide It at Work" — Sintesis de hallazgos sobre ansiedad laboral y AI.
   - URL: https://www.finalroundai.com/blog/anthropic-interviewer-study [^68^]

4. ACM CHI 2024. "Tandem: Reproducible Digital Fabrication Workflows as Multimodal Programs" — Investigacion sobre workflows de fabricacion digital y sus desafios de reproducibilidad.
   - URL: https://dl.acm.org/doi/10.1145/3613904.3642751 [^6^]

### Industria y producto

5. Atlassian (2026). "Driving AI adoption through trust: Insights from Atlassian designer Rachel Shepard" — Principios de diseno para AI: disolver agentes en skills, reducir ansiedad, no espejar arquitectura en UX.
   - URL: https://www.atlassian.com/blog/design/ai-adoption-through-trust-rachel-shepard [^105^]

6. Profasee. "Trust Ladder — Amazon Seller Glossary" — Definicion del modelo de Trust Ladder con sus 4 niveles (observe → approval-required → category-autonomous → fully autonomous).
   - URL: https://profasee.com/glossary/trust-ladder/ [^9^]

7. GitHub/Anthropics (2026). "Feature Idea — Trust Calibration and Progressive Autonomy Model" — Propuesta de modelo de autonomia progresiva domain-scoped para Claude.
   - URL: https://github.com/anthropics/claude-code/issues/47183 [^12^]

8. Writer.com (2026). "The conversation that actually drives AI adoption: Three fears every CMO must address" — Fear #2: Identity and professional pride en creativos.
   - URL: https://writer.com/blog/having-the-ai-conversation/ [^83^]

9. UX Matters (2025). "AI: A Creative Partner, Not a Threat" — Analisis de las tres fuentes de ansiedad en disenadores: perdida de control, velocidad vs. craft, inseguridad laboral.
   - URL: https://www.uxmatters.com/mt/archives/2025/09/ai-a-creative-partner-not-a-threat.php [^88^]

### Consultoria y productividad

10. StratEngineAI (2026). "Top AI Tools for Consultant Knowledge Management 2025" — Dato de 8.2 horas/semana perdidas en busqueda de informacion y $1.8T anuales en productividad.
    - URL: https://stratengineai.com/blog/best-ai-tools-consultant-knowledge-management [^70^]

11. MindStudio (2026). "How a Consulting Firm Uses AI Agents with Clients" — Caso de Thompson Advisory: 70% reduccion en tiempo administrativo, 3x capacidad por consultor.
    - URL: https://www.mindstudio.ai/blog/consulting-firm-client-agents/ [^82^]

12. Finantrix (2026). "Knowledge Management Platforms for Consulting Firms" — 35-45% faster proposal development con plataformas de KM.
    - URL: https://www.finantrix.com/buyer-guides/knowledge-management-platforms-consulting-firms [^75^]

### Agencias y creativos

13. Creative Salon (2023). "Publicis CEO Arthur Sadoun: We're not seeing fear and resistance to AI" — Perspectiva de holding company sobre integracion de AI en agencias creativas.
    - URL: https://creative.salon/example/articles/arthur-sadoun-pre-cannes-q-a-2024 [^95^]

14. DesignMonks (2025). "Best AI Agents for Designing: Tools, Workflows, & Use Cases" — Workflows multi-agente en diseno: research → wireframe → UI → assets → dev handoff.
    - URL: https://www.designmonks.co/blog/best-ai-agents-for-designing [^4^]

15. Medium/Makotokern (2025). "AI Agents Transforming Design and Development Workflows" — Reduccion de 60-80% en timelines de proyecto con AI en 2024-2025.
    - URL: https://makotokern-iiimpact.medium.com/ai-agents-transforming-design-and-development-workflows-3045861fee9c [^2^]

### Freelancers y makers

16. Crawlq AI (2025). "5 Generative AI Tools to Conquer Freelance Challenges" — 20-30% incremento de productividad con AI en freelancers segun McKinsey.
    - URL: https://crawlq.ai/5-generative-ai-tools-to-conquer-freelance-challenges/ [^8^]

17. Useme (2026). "Freelancing with AI in 2026: Tools, Skills & Strategies" — Errores comunes de freelancers con AI y presupuesto tipico de $50-150/mes en herramientas.
    - URL: https://useme.com/en/blog/freelancing-with-ai-in-2026/ [^10^]

18. MakerStudio. "The Vector Graphics Editor for Digital Fabrication" — Software para flujo de trabajo de fabricacion digital: embroidery, laser, CNC, vinyl.
    - URL: https://www.makerstud.io/en/ [^11^]

19. Digital Fabrication Lab. "Digital Fabrication Makerspace" — Stack de herramientas de fabricacion digital y su workflow tipico.
    - URL: https://www.digitalfabricationlab.com/Pages/Equipment.html [^5^]

### Developer Experience (para principios de diseno)

20. First Round Review (2025). "Vercel's Path to Product-Market Fit" — Enfoque en developer experience como growth engine: zero-config, previews, colaboracion.
    - URL: https://review.firstround.com/vercels-path-to-product-market-fit/ [^80^]

21. Reo.dev (2025). "How Developer Experience Powered Vercel's $200M+ Growth" — DX como moat: "focus beats breadth in early GTM".
    - URL: https://www.reo.dev/blog/how-developer-experience-powered-vercels-200m-growth [^79^]

22. Addy Osmani. "Developer Experience Book" — Principios DX: minimize switching contexts, "you are a chef cooking for chefs", optimize TTC.
    - URL: https://addyosmani.com/dx/ [^72^]

### JTBD y frameworks

23. Strategyn. "Jobs-to-be-Done Examples and Applications" — Reglas para job statements: customer-centric, functional, think bigger than product function.
    - URL: https://strategyn.com/jobs-to-be-done/jobs-to-be-done-examples/ [^89^]

24. Product Coalition / Medium (2022). "Understanding Customer Needs: The 'Jobs-to-be-Done' (JTBD) Framework" — Ecuacion del job statement: When [situation] + wants to [motivation] + so that [outcome].
    - URL: https://medium.productcoalition.com/the-ultimate-guide-to-jtbd-framework-and-how-to-apply-it-f6b54e6e7293 [^94^]

25. User Interviews (2026). "Jobs to Be Done (JTBD) in UX Research" — Templates y ejemplos de aplicacion de JTBD.
    - URL: https://www.userinterviews.com/ux-research-field-guide-chapter/jobs-to-be-done-jtbd-framework [^93^]

---

## Apendice: Matriz de priorizacion de JTBD para roadmap

Para facilitar la planificacion de producto, los 16 JTBD se agrupan por prioridad:

### Prioridad 1 (Score 20-25): Nucleo critico — Q1-Q2
- JTBD-01: Sintetizar requerimientos
- JTBD-02: Preparar borradores estructurados
- JTBD-03: Mantener contexto multi-proyecto
- JTBD-04: Verificar consistencia de entregables
- JTBD-05: Generar adaptaciones de pieza maestra
- JTBD-07: Generar propuestas y estimaciones
- JTBD-10: Verificar outputs tecnicos antes de produccion
- JTBD-11: Garantizar aislamiento multi-tenant (ya cubierto)

### Prioridad 2 (Score 12-20): Expansion — Q2-Q3
- JTBD-06: Organizar investigacion
- JTBD-08: Sintetizar feedback de stakeholders
- JTBD-09: Documentar procesos para reutilizacion
- JTBD-12: Explorar opciones estructuradas
- JTBD-13: Traducir a lenguaje no tecnico
- JTBD-15: Analisis de impacto de cambios

### Prioridad 3 (Score <12): Diferenciacion — Q3+
- JTBD-14: Traducir metricas a insights creativos
- JTBD-16: Onboarding de nuevos colaboradores

---

*Documento generado en base a investigacion de fuentes publicas (2024-2026). Las personas son arquetipicas y sinteticas; no sustituyen entrevistas directas con usuarios reales de FaberLoom. Confidence general: ALTO para P1/P2/P3/P5, MEDIO-ALTO para P4.*
