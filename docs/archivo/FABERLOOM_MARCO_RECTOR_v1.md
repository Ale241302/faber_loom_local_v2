# MARCO RECTOR DE FABERLOOM
## Arquitectura de conocimiento operativo · v1.0 · 2026-04-15

---

## 1. OBJETIVO GENERAL

**Formulación única:**

> Que cualquier persona de la organización pueda producir un output correcto, alineado con la verdad operativa de la empresa, adaptado al caso y al destinatario, sin depender de que otra persona esté disponible para validar el qué decir, el cómo decirlo ni a quién decírselo.

**Por qué esta formulación y no otra:**

No dice "automatizar respuestas". Dice "producir output correcto". La diferencia es que la corrección viene del sistema (conocimiento + skill + contexto), no de la velocidad ni de la autonomía. El humano sigue siendo el que aprueba la salida externa, pero el sistema le garantiza que lo que está aprobando está bien fundamentado.

Este objetivo sirve como criterio de corte cuando hay conflicto entre módulos: si una decisión de diseño compromete la corrección del output, está mal. Si la compromete en nombre de la velocidad, peor todavía.

---

## 2. JERARQUÍA MAESTRA DE PRIORIDADES

| # | Prioridad | Justificación |
|---|-----------|--------------|
| 1 | **Integridad del conocimiento canónico** | Si la verdad operativa está corrupta o desactualizada, todo lo demás produce outputs incorrectos. No hay recovery posible aguas abajo. |
| 2 | **Corrección de visibilidad e inyección** | Un output construido con información que el destinatario no debería recibir es un fallo de gobernanza que puede tener consecuencias legales, comerciales o relacionales. La visibilidad no es acceso — es política de inyección. |
| 3 | **Calidad contextual del output** | El output correcto sin contexto específico del caso es genérico e inutilizable. El contexto del caso, del contacto y del momento es lo que convierte conocimiento en respuesta aplicable. |
| 4 | **Coherencia operativa del skill** | El skill debe razonar de forma consistente con las fuentes que tiene y los límites que se le definieron. Un skill que improvisa fuera de sus fuentes es un riesgo disfrazado de utilidad. |
| 5 | **Utilidad operativa real** | El sistema existe para producir outputs que la empresa pueda usar. Si la arquitectura es impecable pero el output no sirve, el sistema falla en su propósito. |
| 6 | **Adaptación de voz** | La voz importa para la efectividad comunicativa, pero es superficie. Nunca estructura. Un output que suena bien pero dice lo equivocado es peor que uno que suena torpe pero es correcto. |
| 7 | **Mejora continua / aprendizaje** | El sistema debe mejorar, pero el aprendizaje no controlado puede introducir drift. Va último entre los funcionales porque requiere supervisión permanente para no corromper los niveles superiores. |
| 8 | **Velocidad y UX** | Relevante para adopción. Irrelevante si los 7 anteriores fallan. La velocidad de un output incorrecto es un acelerador del daño. |

**Regla de conflicto:** cuando dos prioridades tensionan, gana la de número menor. Sin excepciones en diseño de producto. Las excepciones en implementación deben documentarse explícitamente como deuda técnica con fecha de resolución.

---

## 3. SECCIONES MAESTRAS DEL SISTEMA

| # | Sección | Problema que resuelve |
|---|---------|----------------------|
| 1 | Knowledge Engine | La verdad operativa de la empresa no está estructurada ni es confiable |
| 2 | Ingestión y Taxonomía | El conocimiento entra al sistema sin control de tipo, vigencia ni integridad |
| 3 | Policy Engine | No hay forma de controlar qué información puede usarse para construir qué output y para quién |
| 4 | Skills / Playbooks | Las personas no saben cómo razonar sobre dominios especializados fuera de su área |
| 5 | Context Engine | El sistema no sabe qué está pasando en el caso específico ni con el contacto específico |
| 6 | Perfil Operativo Personal | El sistema no sabe cómo trabaja ni cómo comunica esta persona en particular |
| 7 | Output Engine | Los outputs generados no iteran, no aprenden y no se convierten en memoria aprobada |
| 8 | Voice Layer | El output es correcto pero no suena como debería para este usuario y este destinatario |
| 9 | Nightly Maintenance Engine | El sistema acumula señales durante el día pero no las procesa de forma segura sin intervención humana constante |
| 10 | Channel Surfaces | El mismo motor de conocimiento necesita exponerse en canales distintos con formatos distintos |

---

## 4. OBJETIVO ESPECÍFICO POR SECCIÓN

---

### 1. Knowledge Engine

#### Objetivo de la sección
Mantener la verdad operativa de la organización estructurada, versionada, sin contradicciones activas y con vigencia explícita en cada pieza de conocimiento.

#### Qué problema resuelve
Las organizaciones tienen conocimiento disperso, contradictorio, implícito y perecedero. El Knowledge Engine es el único lugar donde ese conocimiento existe en forma confiable, estructurada y con trazabilidad.

#### Qué optimiza
Confiabilidad del retrieval. El sistema no busca el chunk más parecido semánticamente — busca el chunk más correcto, más vigente y con la visibilidad apropiada.

#### Qué no puede sacrificar
Integridad. Nunca puede existir un chunk contradictorio activo sin estar marcado como conflicto abierto. Nunca puede existir conocimiento canónico sin fecha de vigencia explícita.

#### Qué entradas usa
- Documentos cargados por admin (políticas, manuales, catálogos, contratos tipo)
- Validaciones humanas de conflictos resueltos
- Actualizaciones manuales aprobadas
- Propuestas del Nightly Engine (no automáticas — requieren aprobación)

#### Qué salidas produce
- Chunks recuperables por el Context Engine y los Skills
- Árbol de dependencias entre piezas de conocimiento
- Estado de vigencia por chunk
- Reporte de conflictos abiertos

#### Qué puede aprender automáticamente
- Reindexación vectorial cuando cambia la representación semántica (no el contenido)
- Detección de posibles contradicciones (propuesta, no resolución)
- Sugerencia de nuevas conexiones entre chunks (propuesta, no promoción)

#### Qué requiere validación humana
- Cualquier cambio en contenido canónico
- Resolución de conflictos
- Cambio de estado de vigencia
- Cambio de visibilidad de un chunk

#### Doctrina de la sección
**"La KB no es lo que el sistema cree que sabe. Es lo que la empresa ha decidido que es verdad."**

#### Riesgos de esta sección
- KB desactualizada que el sistema sigue usando como si fuera vigente → outputs incorrectos con apariencia de fundamento
- Conflictos sin resolver que el sistema resuelve solo en retrieval → inconsistencia no detectada
- Over-indexación en chunks recientes que hace que conocimiento antiguo pero vigente quede enterrado

#### Métricas de éxito
- % de chunks con fecha de vigencia explícita > 95%
- Conflictos abiertos sin propuesta de resolución < 5 por dominio
- Tiempo entre actualización de política y actualización del chunk correspondiente < 48h

#### Trade-off principal
**Completitud vs. integridad.** Una KB completa con chunks sin validar es más peligrosa que una KB pequeña pero completamente confiable. En caso de duda, menos y verificado gana sobre más y dudoso.

---

### 2. Ingestión y Taxonomía

#### Objetivo de la sección
Garantizar que cualquier pieza de conocimiento que entre al sistema lo haga con tipo correcto, visibilidad declarada, dominio asignado y estado inicial explícito.

#### Qué problema resuelve
Sin taxonomía, el sistema no puede distinguir entre una política inviolable y una nota de trabajo, entre conocimiento canónico y una preferencia personal, entre un playbook operativo y un documento de referencia externa.

#### Qué optimiza
Clasificación correcta en ingestión. El error de clasificación en este punto es el más costoso del sistema porque se propaga hacia arriba.

#### Qué no puede sacrificar
La asignación de tipo y visibilidad. Un documento sin tipo explícito no entra. Un documento sin visibilidad declarada no entra. No hay tipo "general" ni visibilidad "por defecto" sin criterio.

#### Qué entradas usa
- Documentos en cualquier formato (PDF, DOCX, texto plano, entrada manual)
- Declaración del admin sobre tipo, dominio y visibilidad
- Metadatos del documento (autor, fecha, fuente)

#### Qué salidas produce
- Chunk(s) tipificados listos para el Knowledge Engine
- Asignación de dominio y capa
- Estado inicial: DRAFT → PENDIENTE\_VALIDACIÓN → ACTIVO
- Changelog de la ingestión

#### Qué puede aprender automáticamente
- Sugerencia de tipo y dominio basada en contenido (sugerencia, no asignación)
- Detección de posibles duplicados antes de ingerir
- Propuesta de fragmentación de documentos largos

#### Qué requiere validación humana
- Asignación final de tipo
- Asignación final de visibilidad
- Activación del chunk (cambio de DRAFT a ACTIVO)
- Decisión sobre duplicado detectado

#### Doctrina de la sección
**"Si no sé qué es ni para quién es, no entra."**

#### Riesgos de esta sección
- Ingestión masiva sin validación → KB contaminada con conocimiento sin tipo ni vigencia
- Taxonomía demasiado compleja → admin abandona el proceso de ingestión
- Sugerencia de tipo mal calibrada → admin acepta sugerencias incorrectas sin revisar

#### Métricas de éxito
- % de documentos ingresados con tipo + visibilidad + dominio en ingestión > 98%
- Tiempo promedio de ingestión (desde subida hasta chunk activo) < 10 minutos para documentos simples
- % de chunks en estado DRAFT > 72h = indicador de cuello de botella en validación

#### Trade-off principal
**Facilidad de ingestión vs. rigor de clasificación.** Si el proceso es demasiado rígido, nadie alimenta la KB. Si es demasiado flexible, la KB se corrompe. El balance correcto: asistencia activa en clasificación, pero validación humana obligatoria antes de activar.

---

### 3. Policy Engine

#### Objetivo de la sección
Controlar, de forma explícita y auditable, qué información puede inyectarse en qué contexto de generación, para qué usuario, para qué output y para qué destinatario.

#### Qué problema resuelve
El problema de visibilidad no es solo "quién puede abrir el documento". Es "quién puede recibir un output construido con información de ese documento". Son preguntas distintas con respuestas potencialmente distintas.

#### Qué optimiza
Corrección de la política de inyección en tiempo de generación. No en tiempo de consulta del admin.

#### Qué no puede sacrificar
La aplicación de las restricciones de visibilidad antes de la generación, no después. Si el LLM recibe el chunk y luego decide si puede usarlo, el sistema ya falló. El filtro es pre-inferencia.

#### Qué entradas usa
- Configuración de visibilidad por chunk (desde Knowledge Engine)
- Rol y perfil del usuario solicitante
- Tipo de output solicitado (interno, borrador externo, reporte)
- Destinatario del output (si aplica)
- Canal de exposición

#### Qué salidas produce
- Conjunto de chunks autorizados para inyección en este contexto específico
- Registro de qué fue excluido y por qué (para auditoría)
- Nivel de autonomía permitido para esta combinación usuario+output+destinatario

#### Qué puede aprender automáticamente
- Nada. El Policy Engine es determinista. No aprende. No sugiere. Aplica.

#### Qué requiere validación humana
- Cualquier cambio en política de visibilidad
- Cualquier excepción a una regla establecida
- Revisión periódica del registro de exclusiones (para detectar reglas mal calibradas)

#### Doctrina de la sección
**"No importa quién puede abrir el documento. Importa quién puede recibir un output construido con él."**

#### Riesgos de esta sección
- Policy Engine con excepciones que se acumulan y crean huecos → pérdida de control
- Reglas demasiado restrictivas que hacen el sistema inutilizable → abandono
- Ausencia de log de exclusiones → imposible auditar qué se usó para construir qué

#### Métricas de éxito
- 0 instancias de chunks CEO-ONLY inyectados en outputs para usuarios sin ese acceso
- % de outputs con log de chunks usados completo = 100%
- Tiempo de respuesta del Policy Engine < 50ms (no puede ser cuello de botella)

#### Trade-off principal
**Seguridad vs. utilidad operativa.** Un Policy Engine demasiado restrictivo produce outputs sin contexto suficiente. El balance: reglas explícitas por tipo de información, no reglas por miedo general.

---

### 4. Skills / Playbooks

#### Objetivo de la sección
Proveer módulos de criterio operativo especializado que saben cómo razonar sobre un dominio específico, con fuentes declaradas, límites explícitos y aprendizaje controlado.

#### Qué problema resuelve
El conocimiento canónico dice qué es verdad. Pero no sabe cómo aplicarlo en un caso de cobranza, en una licitación, en una queja de cliente VIP o en una comunicación de RH. El skill sabe el cómo sin inventar el qué.

#### Qué optimiza
Calidad de razonamiento aplicado dentro de un dominio. El skill no es un prompt genérico — es criterio operativo con fuentes y límites declarados.

#### Qué no puede sacrificar
La distinción entre lo que el skill puede sugerir y lo que requiere autorización. Un skill que sugiere cosas fuera de su límite de autorización no es más útil — es más peligroso.

#### Qué entradas usa
- Chunks autorizados por el Policy Engine
- Definición del skill (fuentes primarias, fuentes secundarias, límites de decisión)
- Contexto del caso (desde Context Engine)
- Perfil del usuario (desde Perfil Operativo Personal)
- Instrucciones adicionales del usuario para esta invocación

#### Qué salidas produce
- Razonamiento estructurado sobre el caso
- Output sugerido (borrador, análisis, plan, respuesta)
- Lista de qué usó (fuentes) y qué no pudo resolver (gaps)
- Confianza estimada del output (basada en cobertura de fuentes, no en auto-evaluación del LLM)

#### Qué puede aprender automáticamente
- Ajuste de parámetros de retrieval basado en pares aprobados (qué chunks resultaron más útiles)
- Detección de casos frecuentes no cubiertos (propuesta al admin, no resolución automática)

#### Qué requiere validación humana
- Cualquier cambio en la definición del skill (fuentes, límites, instrucciones)
- Promoción de un ajuste sugerido a la definición activa del skill
- Activación de un nuevo skill o desactivación de uno existente

#### Doctrina de la sección
**"El skill sabe cómo razonar, no qué es verdad. La verdad viene de afuera."**

#### Riesgos de esta sección
- Skills con límites vagos que "hacen lo mejor que pueden" fuera de su dominio → creatividad no autorizada
- Skills con demasiadas fuentes → retrieval difuso, outputs genéricos
- Skills que aprenden solos su definición → drift de criterio no detectado

#### Métricas de éxito
- % de outputs de skill con fuentes declaradas completas > 95%
- % de gaps reportados (lo que el skill no pudo resolver) vs. outputs sin gap reportado → ratio indica honestidad del skill
- Tasa de edición significativa por skill (>30% de contenido cambiado = skill mal calibrado)

#### Trade-off principal
**Cobertura vs. precisión.** Un skill con muchas fuentes cubre más casos pero pierde precisión en cada uno. Un skill especializado resuelve bien casos específicos pero declina en los bordes. Decisión recomendada: skills precisos + mecanismo de escalación a skill más general cuando el especializado declina.

---

### 5. Context Engine

#### Objetivo de la sección
Recuperar y estructurar el estado actual del caso, proyecto, contacto y relación comercial relevante para esta generación específica.

#### Qué problema resuelve
Sin contexto dinámico, el sistema responde con conocimiento general como si todos los casos fueran iguales. El contexto es lo que convierte la política de cobranza en "cómo responderle a este cliente que debe 60 días desde enero".

#### Qué optimiza
Especificidad y aplicabilidad del output. El output con contexto resuelve el caso. El output sin contexto describe cómo se resuelven casos en general.

#### Qué no puede sacrificar
La separación entre contexto recuperado (hechos del caso) y conocimiento canónico (verdad de la empresa). Un hecho del caso no puede sobrescribir la política de la empresa. Puede informar cómo aplicarla, nunca si aplicarla.

#### Qué entradas usa
- Historial de interacciones aprobadas con este contacto
- Estado actual del caso/proyecto (si existe registro)
- Thread del canal actual (email, chat)
- Datos de sistemas externos si hay integración (ERP, CRM)
- Notas manuales del usuario sobre el caso
- Metadata del contacto (empresa, rol, historial de relación)

#### Qué salidas produce
- Resumen estructurado del estado del caso
- Perfil de contexto del contacto para esta generación
- Gaps de contexto detectados (lo que no se sabe y podría importar)
- Nivel de confianza del contexto (basado en frescura y completitud de los datos)

#### Qué puede aprender automáticamente
- Actualización del historial de contacto tras cada interacción aprobada
- Detección de cambios de estado (cliente que pagó, pedido que llegó, reclamo cerrado)
- Sugerencia de nuevas notas de contexto basadas en el thread

#### Qué requiere validación humana
- Cualquier cambio en el estado "oficial" del caso
- Resolución de contradicciones en el historial (datos que se contradicen entre sí)
- Integración de datos de sistemas externos (qué dato manda cuando hay discrepancia)

#### Doctrina de la sección
**"El contexto dice cómo aplicar la verdad, nunca si aplicarla."**

#### Riesgos de esta sección
- Contexto desactualizado presentado como vigente → output incorrecto con aparente fundamento
- Contradicciones en historial resueltas automáticamente de forma incorrecta
- Ausencia de log de frescura → el sistema no sabe que sus datos de contexto tienen 3 meses

#### Métricas de éxito
- % de outputs con timestamp de frescura del contexto visible en UI de aprobación
- % de gaps de contexto reportados al usuario antes de generar (no después)
- Tasa de corrección de contexto por el usuario antes de aprobar (indica qué tan bueno es el retrieval)

#### Trade-off principal
**Frescura vs. volumen.** Más historial da más contexto pero puede enterrar señales recientes. El sistema debe priorizar por recencia y relevancia, no solo por similitud semántica.

---

### 6. Perfil Operativo Personal

#### Objetivo de la sección
Mantener una representación estructurada y versionada de cómo trabaja, razona y comunica cada usuario, para que el sistema pueda adaptarse a su forma de operar sin comprometer la verdad canónica ni el criterio del skill.

#### Qué problema resuelve
Sin perfil personal, el sistema produce outputs genéricos que el usuario siempre tiene que reescribir. El perfil personal es lo que hace que después de 4 semanas el sistema parezca que "conoce al usuario".

#### Qué optimiza
Reducción de edición en outputs. Cada aprobación sin edición refuerza el perfil. Cada edición significativa genera una señal de desajuste.

#### Qué no puede sacrificar
La separación entre preferencia personal y verdad operativa. El perfil no puede hacer que el output viole conocimiento canónico ni criterio del skill. El perfil colorea la forma, nunca la sustancia.

#### Qué entradas usa
- Pares (output generado → output aprobado/editado) del usuario
- Instrucciones manuales del usuario sobre su estilo
- Configuración explícita de parámetros (formalidad, longitud, saludo, cierre)
- Canal de comunicación (el perfil puede tener variantes por canal)

#### Qué salidas produce
- Parámetros de estilo actualizados
- Ejemplos few-shot seleccionados para este usuario (pares aprobados relevantes)
- Versión del perfil con changelog

#### Qué puede aprender automáticamente
- Actualización de parámetros de estilo tras cada par aprobado
- Sugerencia de regla explícita cuando detecta patrón consistente (ej: "siempre cambia el saludo a X")

#### Qué requiere validación humana
- Activación de cualquier regla nueva propuesta
- Cambio de parámetros por encima de un threshold de impacto
- Rollback de versión del perfil

#### Doctrina de la sección
**"El perfil adapta cómo el usuario suena, no qué dice. Lo segundo lo deciden capas superiores."**

#### Riesgos de esta sección
- Perfil que aprende manías inconsistentes del usuario → output impredecible
- Perfil sin versión → imposible hacer rollback cuando el perfil derivó mal
- Perfil que interfiere con el criterio del skill → outputs que suenan bien pero razonan mal

#### Métricas de éxito
- Tasa de aprobación sin edición creciente semana a semana para el mismo usuario
- Edit distance promedio decreciente en los primeros 60 días
- % de usuarios con perfil activo (≥20 pares aprobados) que reportan "el sistema ya me conoce"

#### Trade-off principal
**Personalización vs. gobernanza.** Más personalización hace el output más adoptable por el usuario. Demasiada personalización puede hacer que el output se aleje de la voz de la empresa. El balance: personalización en capa superficial (tono, longitud, vocabulario), no en capa de razonamiento ni de verdad.

---

### 7. Output Engine

#### Objetivo de la sección
Gestionar el ciclo completo de un output: generación, iteración, aprobación, envío y conversión en memoria aprobada para aprendizaje futuro.

#### Qué problema resuelve
Sin un ciclo completo, los outputs aprobados se pierden. El valor de cada interacción no se acumula en el sistema. El aprendizaje no ocurre.

#### Qué optimiza
Tasa de conversión de outputs en memoria aprobada útil. Cada aprobación (con o sin edición) debe producir una señal de aprendizaje usable por el sistema.

#### Qué no puede sacrificar
La doctrina de aprobación humana para toda salida externa. En v1, ningún output sale hacia un destinatario externo sin aprobación explícita. El Output Engine no tiene función "AUTO_SEND". Si aparece en el código, es un bug de diseño.

#### Qué entradas usa
- Output generado por el skill con el contexto del caso
- Ediciones del usuario (si aplica)
- Decisión de aprobación/rechazo
- Notas del usuario sobre por qué rechazó o editó

#### Qué salidas produce
- Output listo para envío (en el canal correspondiente)
- Par aprobado para la memoria del sistema
- Señal de ajuste para el skill, el perfil y el contexto (según tipo de edición)
- Registro inmutable de la aprobación (quién, cuándo, qué se modificó)

#### Qué puede aprender automáticamente
- Clasificación del tipo de edición (estilo, contenido, corrección de hecho)
- Actualización del perfil personal con la señal de edición
- Propuesta de actualización del skill si el patrón de edición es recurrente

#### Qué requiere validación humana
- Toda salida externa
- Toda promoción de señal de edición a cambio en definición del skill
- Toda resolución de contradicción entre output aprobado y conocimiento canónico

#### Doctrina de la sección
**"Aprobar no es solo enviar. Aprobar es enseñar."**

#### Riesgos de esta sección
- Aprobaciones sin extracción de señal de aprendizaje → el sistema no mejora
- Señales de edición mal clasificadas → el sistema aprende lo equivocado
- Output Engine que permite salida sin aprobación en "modo urgente" → ruptura de doctrina

#### Métricas de éxito
- % de outputs aprobados que generan par de memoria clasificado correctamente > 90%
- Tiempo entre aprobación y conversión en par disponible para retrieval < 5 minutos
- Tasa de aprobación sin edición: trending up semana a semana por usuario activo

#### Trade-off principal
**Velocidad de aprobación vs. calidad de la señal de aprendizaje.** Un proceso de aprobación muy rápido produce menos señal de aprendizaje (el usuario aprueba sin reflexionar). Un proceso con mucha fricción produce mejor señal pero menor adopción. El balance: aprobación simple pero con captura automática de ediciones como señal implícita.

---

### 8. Voice Layer

#### Objetivo de la sección
Ajustar la forma expresiva del output — tono, registro, longitud, vocabulario — según la combinación de usuario, contacto y situación, dentro de los límites que imponen las capas superiores.

#### Qué problema resuelve
Un output correcto que suena a robot o que suena inapropiado para el destinatario tiene menor probabilidad de ser enviado sin edición y genera rechazo de uso del sistema.

#### Qué optimiza
Adopción. Un output que suena como el usuario habría escrito tiene más probabilidad de ser aprobado sin edición.

#### Qué no puede sacrificar
La jerarquía. La voz no puede hacer que el output viole conocimiento canónico, ignore el criterio del skill o contradiga el contexto del caso. La voz es la última capa de transformación, no la primera.

#### Qué entradas usa
- Perfil de voz del usuario (desde Perfil Operativo Personal)
- Perfil de contacto (desde Context Engine)
- Tipo de situación (formal, urgente, relacional, técnica)
- Canal de salida (email, chat interno, WhatsApp)
- Output base generado por el skill

#### Qué salidas produce
- Output con ajuste de voz aplicado
- Parámetros usados (para auditoría y rollback)

#### Qué puede aprender automáticamente
- Actualización del perfil de contacto tras interacciones aprobadas
- Detección de inconsistencias de voz entre outputs del mismo usuario

#### Qué requiere validación humana
- Cualquier perfil de contacto nuevo
- Cambios en parámetros de voz que afectan múltiples outputs futuros

#### Doctrina de la sección
**"La voz adapta la forma, nunca la verdad."**

#### Riesgos de esta sección
- Voice Layer que se activa antes de las capas superiores → manías del usuario por encima de la verdad
- Perfil de contacto desactualizado → voz inapropiada para el estado actual de la relación
- Over-personalización que hace el output detectablemente "forzado"

#### Métricas de éxito
- % de ediciones de tipo "estilo" vs. "contenido": si la mayoría son de estilo, la voz está mal calibrada
- Tasa de rechazo de outputs bien fundamentados pero mal expresados: debe tender a cero

#### Trade-off principal
**Consistencia de marca vs. personalización individual.** La empresa quiere que todos sus outputs suenen consistentemente profesionales. El usuario quiere que el output suene como él. El balance: parámetros de voz dentro de un rango definido por la empresa, no sin límites.

---

### 9. Nightly Maintenance Engine

#### Objetivo de la sección
Procesar las señales acumuladas durante el día para reorganizar, reindenxar, detectar problemas y proponer mejoras al sistema, sin corromper la verdad canónica ni aplicar cambios no aprobados.

#### Qué problema resuelve
Durante el día el sistema opera. No tiene tiempo de consolidar, proponer y mejorar. De noche tiene recursos y puede hacerlo con seguridad, pero solo si tiene reglas explícitas sobre qué puede y qué no puede tocar.

#### Qué optimiza
Calidad del retrieval y coherencia del sistema a lo largo del tiempo, sin intervención humana permanente.

#### Qué no puede sacrificar
La separación entre conocimiento real y representación vectorial. Actualizar los vectores no es lo mismo que actualizar el contenido. Reorganizar el índice no es lo mismo que cambiar la verdad.

#### Entradas del proceso nocturno
- Log de pares aprobados del día
- Log de gaps reportados por skills
- Log de ediciones significativas
- Log de chunks con baja tasa de uso o retrieval fallido
- Señales de posibles contradicciones detectadas durante el día
- Métricas de frescura del contexto

#### Distinción crítica de estados

| Estado | Descripción | Puede aplicarse automáticamente |
|--------|-------------|--------------------------------|
| OBSERVADO | Señal detectada, aún sin clasificar | Sí — solo lectura |
| PROPUESTO | Cambio o mejora sugerida por el sistema | No — requiere aprobación |
| VALIDADO | Propuesta aprobada por humano | Sí — puede promover |
| PROMOVIDO | Cambio aplicado al sistema | Sí — con log |
| RECHAZADO | Propuesta denegada por humano | Sí — archivado, no eliminado |
| ARCHIVADO | Señal procesada sin acción | Sí — solo lectura |

#### Qué sí puede hacerse automáticamente
- Reindexación vectorial de chunks con representación desactualizada (sin cambiar el contenido)
- Reorganización de índices de retrieval para mejorar velocidad
- Actualización de métricas de uso de chunks
- Marcado de chunks sin uso en 90 días como "candidato a revisión" (no a borrado)
- Actualización de perfiles de voz con señales del día (si la señal es consistente y el threshold se supera)
- Generación del reporte de la mañana

#### Qué no puede hacerse automáticamente
- Cambiar el contenido de ningún chunk canónico
- Cambiar visibilidad de ningún chunk
- Borrar ningún chunk (ni marcarlo como inactivo)
- Resolver conflictos entre piezas de conocimiento
- Activar propuestas rechazadas previamente
- Cambiar la definición de ningún skill
- Cambiar políticas del Policy Engine

#### Qué va a rollback automático
- Cualquier reindexación que produzca degradación medible en recall (comparado con baseline)
- Cualquier actualización de perfil que produzca aumento en tasa de rechazo de outputs

#### Reporte de la mañana (obligatorio)
El sistema produce cada mañana un reporte estructurado con:
1. Resumen de actividad del día anterior (outputs generados, aprobados, rechazados)
2. Propuestas pendientes de validación (con descripción y evidencia)
3. Alertas de integridad (conflictos detectados, chunks expirados, gaps frecuentes)
4. Estado del Knowledge Engine (salud del índice, frescura promedio)
5. Top 3 skills con mayor tasa de edición (posibles candidatos a recalibración)

#### Doctrina de la sección
**"De noche consolida y propone. Nunca reescribe la verdad en silencio."**

#### Riesgos de esta sección
- Nightly Engine que interpreta "mejorar" como "cambiar contenido" → corrupción silenciosa de la KB
- Propuestas que se acumulan sin ser revisadas → admin deja de abrir el reporte → sistema que propone pero no mejora
- Rollback no implementado → no hay recovery cuando una actualización automática degrada el sistema

#### Métricas de éxito
- % de propuestas del Nightly Engine que reciben revisión en < 48h
- Tasa de aceptación de propuestas del Nightly Engine > 60% (si es menor, el engine está proponiendo cosas de baja calidad)
- 0 cambios en contenido canónico sin log de aprobación humana

#### Trade-off principal
**Mejora continua vs. drift.** Más autonomía nocturna produce mejoras más rápidas pero más oportunidades de drift. La solución no es minimizar la autonomía — es maximizar la trazabilidad de lo que el engine hace automáticamente.

---

### 10. Channel Surfaces

#### Objetivo de la sección
Exponer el Knowledge Engine, los skills y el Output Engine en los canales donde la empresa ya trabaja, con el formato y las restricciones propias de cada canal.

#### Qué problema resuelve
El mismo output no puede presentarse igual en un email corporativo, un mensaje de chat interno, una notificación de WhatsApp o un portal externo. El canal impone restricciones de formato, longitud, tono y protocolo que son independientes del contenido.

#### Qué optimiza
Adoptabilidad del output por canal. Un output correcto que llega en el formato incorrecto se rechaza por razones de forma, no de fondo.

#### Qué no puede sacrificar
La consistencia del Knowledge Engine subyacente. El mismo caso procesado en email y en chat debe producir outputs con el mismo fundamento. La diferencia es el formato, no la verdad.

#### Entradas del canal
- Output base del Output Engine
- Restricciones del canal (longitud máxima, formato, protocolo)
- Configuración del canal (cuenta conectada, modo de entrega del draft)
- Historial del thread en ese canal

#### Salidas del canal
- Draft formateado para el canal específico
- Método de entrega del draft (IMAP APPEND, API de draft, UI interno)
- Estado de entrega confirmado

#### Qué puede aprender automáticamente
- Preferencias de formato por canal del usuario (si siempre acorta los emails, el canal aprende)

#### Qué requiere validación humana
- Activación de nuevo canal
- Configuración de credenciales del canal
- Toda salida hacia destinatario externo

#### Doctrina de la sección
**"El canal cambia la forma. El Knowledge Engine decide el fondo."**

#### Riesgos de esta sección
- Canal que modifica el contenido además del formato → outputs distintos según canal sin razón de conocimiento
- Canal que permite salida sin pasar por aprobación (bug de integración) → ruptura de doctrina
- Proliferación de canales antes de estabilizar el Knowledge Engine → complejidad sin valor

#### Métricas de éxito
- % de drafts entregados exitosamente al canal (sin fallo técnico) > 99%
- % de outputs que llegan al canal habiendo pasado por aprobación = 100%
- Tiempo entre aprobación y disponibilidad del draft en el canal < 30 segundos

#### Trade-off principal
**Proliferación de canales vs. profundidad del motor.** Cada nuevo canal es engineering de integración. Ese esfuerzo se sustrae del motor de conocimiento. Decisión recomendada: 1 canal funcionando impecablemente vale más que 4 canales mediocres.

---

## 5. MODELO DE HERENCIA Y SOBRESCRITURA

### Jerarquía de capas

```
┌─────────────────────────────────────────────────────┐
│ 1. CONOCIMIENTO CANÓNICO DE EMPRESA (L0–L3)         │ ← INVIOLABLE
│    Políticas, precios, procesos, contratos tipo,    │
│    restricciones legales, catálogo, condiciones     │
└────────────────────┬────────────────────────────────┘
                     │ hereda (recibe como verdad base)
┌────────────────────▼────────────────────────────────┐
│ 2. CONOCIMIENTO ORGANIZACIONAL POR FUNCIÓN          │ ← INVIOLABLE en su dominio
│    Cómo opera el área de ventas, de RH, de ops      │
│    Protocolos por función                           │
└────────────────────┬────────────────────────────────┘
                     │ usa como fuente primaria
┌────────────────────▼────────────────────────────────┐
│ 3. SKILL EXPERTO REUTILIZABLE                       │ ← INVIOLABLE en su razonamiento
│    Cómo razonar sobre cobranza, licitaciones, RH    │
│    Fuentes declaradas, límites explícitos           │
└────────────────────┬────────────────────────────────┘
                     │ se instancia con
┌────────────────────▼────────────────────────────────┐
│ 4. CONTEXTO DE CASO / PROYECTO                      │ ← Modifica APLICACIÓN, no doctrina
│    Estado actual del caso específico                │
│    Historial de interacciones relevantes            │
└────────────────────┬────────────────────────────────┘
                     │ coloreado por
┌────────────────────▼────────────────────────────────┐
│ 5. PERFIL OPERATIVO PERSONAL DEL USUARIO            │ ← Modifica PRESENTACIÓN, no razonamiento
│    Cómo trabaja y piensa este usuario               │
│    Preferencias de proceso, no de verdad            │
└────────────────────┬────────────────────────────────┘
                     │ ajustado por
┌────────────────────▼────────────────────────────────┐
│ 6. PERFIL DE CONTACTO                               │ ← Ajuste RELACIONAL, no operativo
│    Cómo hablarle a este destinatario específico     │
│    Historial de relación, sensibilidades            │
└────────────────────┬────────────────────────────────┘
                     │ expresado mediante
┌────────────────────▼────────────────────────────────┐
│ 7. VOZ ADAPTATIVA                                   │ ← SUPERFICIE, no estructura
│    Tono, registro, longitud, vocabulario            │
│    La última transformación antes del output        │
└─────────────────────────────────────────────────────┘
```

### Reglas de sobrescritura

| Capa | ¿Puede el usuario sobrescribirla? | ¿Puede el admin sobrescribirla? | Versionada |
|------|----------------------------------|--------------------------------|-----------|
| 1. Canónico empresa | No | Sí, con aprobación y log | Sí |
| 2. Org por función | No (en uso) | Sí, con aprobación y log | Sí |
| 3. Skill experto | No (reglas) | Sí (definición del skill) | Sí |
| 4. Contexto caso | Sí (notas manuales) | Sí | No (es estado dinámico) |
| 5. Perfil personal | Sí (config explícita) | No (es del usuario) | Sí |
| 6. Perfil contacto | Sí (notas y config) | No | Sí |
| 7. Voz adaptativa | Sí (parámetros) | Parcial (rango permitido) | Sí |

### Qué manda cuando hay conflicto

**Regla única:** la capa de número menor siempre gana.

Si el perfil personal del usuario (capa 5) instruye al sistema a prometer un descuento que viola la política comercial (capa 1), la capa 1 gana. El sistema genera el output con el descuento permitido y notifica el conflicto al usuario.

Si el perfil de contacto (capa 6) indica que "a este cliente hay que ser muy directo" pero el skill de cobranza (capa 3) requiere un tono específico por ser una deuda crítica, el skill gana. El perfil de contacto ajusta dentro de lo que el skill permite.

### Qué debe quedar fuera de vectores

- Todo chunk con visibilidad CEO-ONLY
- Perfiles operativos personales de usuarios (son datos propios del usuario, no conocimiento organizacional)
- Perfiles de contacto con información sensible de relaciones comerciales (pueden ir a vectores con filtro de acceso, no sin filtro)
- Logs de aprobación y registro inmutable (son audit trail, no conocimiento recuperable)

---

## 6. MODELO DE VISIBILIDAD Y EXPOSICIÓN

### Las cuatro preguntas que visibilidad debe responder

El error más común en modelos de visibilidad es reducirlos a "quién puede abrir el documento". FaberLoom distingue explícitamente cuatro preguntas distintas:

| Dimensión | Pregunta | Por qué importa |
|-----------|----------|-----------------|
| **Consulta** | ¿Quién puede leer este documento directamente? | Control de acceso básico |
| **Inyección** | ¿En qué generación puede usarse este chunk como contexto? | Evita que información restringida llegue al LLM en contextos no autorizados |
| **Recepción** | ¿Quién puede recibir un output cuya respuesta fue construida con este chunk? | El destinatario del output puede no tener permiso de consulta directa, pero puede recibir la conclusión |
| **Aprobación** | ¿Quién puede aprobar una salida externa basada en este chunk? | Algunos outputs requieren un nivel de autoridad para ser aprobados, no solo revisados |

### Aplicación por tipo de información

#### Información Personal (vacaciones, aguinaldo, situación laboral individual)

| Dimensión | Regla |
|-----------|-------|
| Consulta | Solo el empleado en cuestión y el admin de RH |
| Inyección | Solo en contextos donde el agente está respondiendo a/sobre ese empleado específico |
| Recepción | Solo el empleado en cuestión y quienes tienen autoridad sobre él |
| Aprobación | Admin de RH o gerente directo para comunicaciones externas |
| Vectores | No. Información personal no va a pgvector. |

#### Información General (políticas internas, procesos, FAQs)

| Dimensión | Regla |
|-----------|-------|
| Consulta | Todos los usuarios internos con acceso al sistema |
| Inyección | Cualquier generación para usuario interno o borrador para externo |
| Recepción | Cualquier destinatario para quien el output sea apropiado |
| Aprobación | Cualquier usuario con rol de aprobación |
| Vectores | Sí, capa L0 y L1 accesibles según rol |

#### Información Delicada (compliance, pricing real, márgenes, decisiones estratégicas)

| Dimensión | Regla |
|-----------|-------|
| Consulta | Admin y roles explícitamente autorizados |
| Inyección | Solo en generaciones para usuarios con acceso a esa capa |
| Recepción | Depende del tipo de output: interno vs. externo. Nunca directamente en output externo. Puede informar razonamiento interno. |
| Aprobación | Solo rol con autoridad equivalente al nivel de la información |
| Vectores | L2 con filtro de acceso. L3 fuera de vectores. |

#### Por Caso/Proyecto (licitaciones, reclamos, expedientes, auditorías)

| Dimensión | Regla |
|-----------|-------|
| Consulta | Equipo asignado al caso |
| Inyección | Solo en generaciones relacionadas con ese caso específico |
| Recepción | Partes del caso con autorización explícita |
| Aprobación | Líder del caso o rol con autoridad sobre el caso |
| Vectores | Contexto del caso en índice separado por caso, no en índice general |

---

## 7. CASOS DE APLICACIÓN OBLIGATORIOS

---

### Caso 1 — RH: Vacaciones / Aguinaldo / Política Laboral

**Conocimiento canónico:**
Política de vacaciones de la empresa (días por año, proceso de solicitud, aprobación requerida), montos y fechas de aguinaldo según contrato tipo, restricciones legales aplicables al país.

**Skill experto:**
Skill de Comunicación RH. Sabe cómo redactar comunicaciones de RH que sean claras, no generen ambigüedad legal, y mantengan el tono apropiado para la relación laboral. Sabe qué promesas no puede hacer (condiciones individuales, excepciones a política).

**Contexto del caso:**
Saldo de días disponibles de este empleado específico, fecha de última solicitud aprobada, si hay conflicto con otros en el mismo equipo, historial de comunicaciones previas sobre el tema.

**Preferencia personal:**
El gerente de RH prefiere comunicaciones directas y breves. No usa fórmulas de cortesía extensas.

**Perfil de contacto:**
Este empleado específico ha mostrado sensibilidad en comunicaciones anteriores. Prefiere explicaciones con razón incluida, no solo instrucciones.

**Salida esperada:**
Borrador de respuesta a solicitud de vacaciones, con el estado de aprobación, la razón si aplica, y los próximos pasos. Tono directo pero con razón incluida por el perfil del contacto.

**Visibilidad:**
El saldo de días del empleado no va en un output visible para terceros. La política general de vacaciones puede mencionarse si es relevante para la respuesta.

**Qué no debe permitirse:**
Prometer excepciones a la política sin autorización explícita. Mencionar el saldo de días de otros empleados. Comprometer fechas sin verificar disponibilidad del equipo.

---

### Caso 2 — Compliance: Normas Generales vs. Casos Sensibles

**Conocimiento canónico (normas generales):**
Marco regulatorio aplicable al negocio, requisitos de documentación, plazos de presentación, organismos competentes. Visibilidad: INTERNAL.

**Conocimiento canónico (casos sensibles):**
Situaciones de incumplimiento previas, acuerdos con organismos reguladores, decisiones estratégicas de compliance. Visibilidad: CEO-ONLY. Fuera de vectores.

**Skill experto:**
Skill de Compliance. Sabe distinguir entre consulta informativa (puede responder con norma general) y caso activo con riesgo regulatorio (debe escalar, no resolver). Nunca improvisa interpretación legal — cita fuente o dice que no puede.

**Contexto del caso:**
Si es consulta general o caso específico activo. Si hay precedente relevante. Si el caso involucra conocimiento sensible (CEO-ONLY).

**Salida esperada para consulta general:**
Respuesta con la norma aplicable, la fuente, y los próximos pasos procedimentales. No interpretación legal.

**Salida esperada para caso sensible:**
El skill declina generar el output y escala: "Este caso involucra contexto que requiere revisión directa. No genero borrador sin que el nivel correspondiente revise el contexto completo."

**Qué no debe permitirse:**
Inyectar información CEO-ONLY en outputs para usuarios sin ese acceso. Interpretar normas fuera de lo que dice la fuente citada. Generar borrador de respuesta a organismo regulador sin aprobación del nivel con autoridad.

---

### Caso 3 — Licitaciones: Skill Normativo + Skill Contratación + Proyecto Específico

**Conocimiento canónico:**
Marco legal de contratación pública del país (ley de contratación administrativa, umbrales, requisitos). Conocimiento de la empresa sobre sus capacidades y condiciones. Visibilidad: INTERNAL + PARTNER_B2B según lo que se comparte.

**Skills aplicados (combinación):**
- Skill Normativo País: sabe el marco legal de contratación para esa jurisdicción. Fuente: normativa pública.
- Skill Contratación Administrativa: sabe el proceso, los documentos, los plazos, los riesgos. Fuente: KB interna + normativa.
- Ambos skills se combinan para este caso. El sistema debe ser capaz de invocar los dos y resolver conflictos entre sus criterios.

**Contexto del caso (proyecto específico):**
Número de licitación, entidad contratante, pliego de condiciones, estado del proceso, documentos presentados, interlocutores identificados. Visibilidad: INTERNAL al equipo del proyecto.

**Salida esperada:**
Borrador de comunicación con la entidad contratante, aclaraciones técnicas, o respuesta a observaciones. Con citas de la normativa cuando corresponde.

**Qué no debe permitirse:**
Comprometer condiciones fuera de lo declarado en el pliego. Generar respuesta jurídica sin revisión legal. Compartir información del proyecto con usuarios fuera del equipo asignado al caso.

**Separación de contextos:**
El índice vectorial de este proyecto está separado del índice general. Un usuario de ventas no accede al contexto de licitaciones en curso.

---

### Caso 4 — Cobranza / Relación con Cliente Específico

**Conocimiento canónico:**
Política de crédito (plazos, límites, proceso de escalación), política de descuentos (umbrales por nivel de autorización), condiciones contractuales de este tipo de cliente.

**Skill experto:**
Skill de Cobranza. Sabe qué ofrecer según días de mora (recordatorio amable < 15 días, solicitud formal 15–45, escalación > 45). Conoce los scripts aprobados para cada etapa. Sabe qué no puede ofrecer sin autorización.

**Contexto del caso:**
Días de mora, monto, historial de pagos de este cliente, promesas anteriores (si las hay), estado del pedido asociado (si hay deuda ligada a una entrega pendiente).

**Preferencia personal:**
El vendedor que maneja esta cuenta prefiere un tono directo pero sin perder la relación.

**Perfil de contacto:**
Este cliente ha pagado siempre antes de día 30. Esta es una situación inusual. El perfil indica que responde bien a comunicaciones que reconocen su historial.

**Salida esperada:**
Recordatorio de deuda que reconoce el buen historial del cliente, menciona el monto específico, ofrece confirmación de recepción de factura como primer paso, con tono directo pero relacional.

**Qué no debe permitirse:**
Ofrecer descuento sobre el umbral sin autorización. Amenazar con acción legal sin autorización del área jurídica. Comprometer próximas condiciones de crédito sin autorización. Mencionar la situación de otros clientes.

---

## 8. NIGHTLY KNOWLEDGE MAINTENANCE ENGINE (detalle completo)

### Distinción fundamental de tres capas de conocimiento

```
Conocimiento Real          → el contenido de los chunks (texto, reglas, datos)
                              Solo cambia por decisión humana aprobada.

Representación Vectorial   → el embedding del contenido en pgvector
                              Puede actualizarse automáticamente cuando
                              cambia el modelo de embedding o el índice.
                              No es "el conocimiento" — es su representación matemática.

Memoria Derivada           → pares aprobados, patrones de uso, señales de edición
                              Puede actualizarse automáticamente con controles.
                              No es la fuente de verdad — es el registro de uso.
```

**La confusión entre estas tres capas es el riesgo principal del Nightly Engine.** Un sistema que actualiza la representación vectorial correctamente pero toca el contenido en el proceso está corrompiendo la KB aunque técnicamente "solo reindexó".

### Qué procesa el Nightly Engine

**1. Consolidación de señales del día**
- Clasificar las ediciones del día: ¿fueron de estilo, de contenido, de corrección de hecho?
- Agrupar gaps frecuentes reportados por skills: ¿qué preguntaron los usuarios que el sistema no pudo responder?
- Registrar chunks con retrieval fallido o baja relevancia calificada

**2. Propuestas (nunca aplicaciones automáticas)**
- Si 3+ usuarios en el mismo día editaron el mismo tipo de output del mismo skill en la misma dirección → propuesta de ajuste al skill
- Si un chunk fue marcado como "no relevante" en 5+ retrievals → propuesta de revisión o archivo
- Si se detecta posible contradicción entre dos chunks activos → propuesta de revisión de conflicto
- Si un perfil de voz muestra drift consistente (los últimos 20 outputs todos editados en la misma dirección) → propuesta de actualización de parámetro

**3. Operaciones automáticas permitidas**
- Reindexar vectores de chunks cuyo contenido no cambió pero cuyo embedding se desactualizó
- Actualizar métricas de uso y frescura
- Generar el reporte de la mañana
- Marcar chunks sin uso en 90 días como "candidatos a revisión" (no como inactivos)
- Actualizar parámetros de retrieval (pesos de campos, umbrales de similitud) si hay evidencia de degradación

**4. Operaciones prohibidas en cualquier circunstancia**
- Modificar el contenido de ningún chunk
- Cambiar la visibilidad de ningún chunk
- Resolver conflictos entre piezas de conocimiento
- Activar o desactivar skills
- Promover propuestas rechazadas previamente bajo ningún criterio

### Ciclo de vida de una propuesta

```
Señal detectada
    ↓
OBSERVADO (24h máximo — si no se clasifica, se archiva automáticamente)
    ↓
[Clasificación automática del tipo de señal]
    ↓
PROPUESTO (entra al reporte de la mañana para el admin)
    ↓
         ├── Admin aprueba → VALIDADO → PROMOVIDO (se aplica el cambio)
         ├── Admin rechaza → RECHAZADO → ARCHIVADO (con razón si la provee)
         └── Admin no revisa en 72h → PENDIENTE_URGENTE (escalación en reporte)
```

### Reporte de la mañana — estructura obligatoria

```
REPORTE DIARIO DEL SISTEMA — [fecha]

RESUMEN DE ACTIVIDAD
- Outputs generados: N
- Outputs aprobados sin edición: N (X%)
- Outputs editados: N (X% de edición promedio)
- Outputs rechazados: N
- Pares de memoria generados: N

PROPUESTAS PENDIENTES (requieren decisión)
1. [Tipo: skill / chunk / perfil] — [descripción] — [evidencia: N señales]
...

ALERTAS DE INTEGRIDAD
- Conflictos detectados sin resolver: [lista]
- Chunks expirados o sin revisión > 90 días: [lista]
- Gaps frecuentes sin cobertura en KB: [lista]

ESTADO DEL KNOWLEDGE ENGINE
- Chunks activos: N
- Chunks candidatos a revisión: N
- Índice vectorial: [OK / degradado / en reindexación]
- Frescura promedio del contexto: [X días]

TOP 3 SKILLS POR TASA DE EDICIÓN
1. [Skill] — [X% de outputs editados] — [tipo de edición más frecuente]
...
```

---

## 9. CRÍTICA BRUTAL DEL MARCO

### Lo más fuerte del enfoque

**La jerarquía de capas con regla de conflicto explícita es el diferencial real.**
La mayoría de los productos de IA empresarial no tienen una jerarquía de prioridad declarada. Cuando hay conflicto entre personalización y gobernanza, entre velocidad y corrección, entre lo que el usuario quiere y lo que la empresa permite, esos productos improvisan la resolución en cada caso. Eso produce comportamiento inconsistente que destruye la confianza.

Este marco resuelve eso antes de que ocurra. La regla "gana la capa de número menor" es simple, determinista y auditable. Es el tipo de principio que puede explicársele al cliente, implementarlo en código y verificarlo en producción.

**La distinción entre conocimiento real, representación vectorial y memoria derivada es arquitectura seria.**
El 80% de los proyectos que usan pgvector tratan los vectores como si fueran la fuente de verdad. No lo son. Este marco lo dice explícitamente y construye el Nightly Engine sobre esa distinción. Eso evita la clase de corrupción silenciosa que mata la confiabilidad del sistema a los 6 meses de operación.

**El modelo de visibilidad de 4 dimensiones es correcto y raro.**
Casi ningún producto distingue entre "quién puede consultar" y "quién puede recibir un output basado en eso". Esa distinción es fundamental en contextos B2B donde la información confidencial de la empresa puede informar razonamiento interno sin jamás aparecer en la superficie del output externo.

### Lo más débil o ingenuo

**El Nightly Engine asume que el admin va a revisar el reporte de la mañana.**
En una PYME de 10 personas, el admin probablemente no tiene un ritual diario de revisión de reportes del sistema. Después de las primeras dos semanas, el reporte va a acumularse sin revisión. Las propuestas se van a quedar en PROPUESTO indefinidamente. El sistema va a dejar de mejorar no por falla técnica sino por ausencia de atención humana.

La solución no está descrita en este marco y necesita estarlo: o las propuestas tienen un mecanismo de degradación (si no se revisan en N días, se archivan con flag) o el sistema tiene un canal de notificación push que haga que el reporte llegue donde el admin ya está mirando (email, WhatsApp).

**La combinación de skills no tiene protocolo de conflicto.**
El caso 3 (licitaciones) menciona "el sistema debe ser capaz de invocar los dos skills y resolver conflictos entre sus criterios". Eso está dicho como si fuera simple. No lo es. Cuando el Skill Normativo País dice X y el Skill Contratación Administrativa dice Y sobre el mismo punto, el sistema necesita un árbitro. Este marco no define ese árbitro.

**El ICP sigue siendo difuso.**
Este marco es arquitectonicamente correcto para una organización que tiene: un admin técnicamente capaz, volumen de comunicación externa repetitiva suficiente, y disposición a invertir en configurar el Knowledge Engine. Eso excluye implícitamente a muchas PYMEs pequeñas. El marco debería decirlo explícitamente en lugar de asumir que el producto funciona para cualquier PYME de 5–50 personas.

**La complejidad de la solución todavía supera la complejidad del problema que resuelve para el segmento de entrada.**
Para una PYME que hoy responde emails con una sola persona, este marco es una central nuclear para calentar café. Es el marco correcto para lo que FaberLoom debe ser a largo plazo. No necesariamente para lo que necesita ser el día 1.

### Lo que falta para que esto sea un producto, no solo una arquitectura

**1. Un mecanismo de warm start real.** El marco describe el sistema en estado maduro. Necesita describir el estado de día 1: qué tiene el sistema antes de que exista ningún par aprobado, ningún perfil de contacto, ningún historial. Qué valor produce el sistema en ese estado y cómo se lo presenta al usuario sin que parezca un sistema vacío.

**2. Una definición de MVP que use este marco para decir qué NO construir.** Este marco describe 10 secciones. No todas se construyen el día 1. El marco debería incluir una tabla explícita de qué secciones son v1, cuáles son v2 y cuáles son v3, con el criterio de qué evidencia de mercado desbloquea cada expansión.

**3. Un protocolo de conflicto entre skills.** Descrito arriba. Sin él, los casos de uso complejos (licitaciones, compliance con múltiples jurisdicciones) no pueden implementarse de forma determinista.

**4. La respuesta a: ¿qué pasa cuando el Knowledge Engine no tiene suficiente información para responder bien?** El marco dice que el skill reporta gaps. Pero no define qué hace el sistema con eso en el momento de la generación: ¿genera igual con advertencia? ¿declina? ¿pide más contexto al usuario? Esa lógica necesita estar en el marco, no en el código.

### La decisión más importante que debería tomar ahora

**Definir el primer caso de uso completamente operativo — no el más impresionante, sino el más cerrado.**

No el sistema completo. No el Knowledge Engine en toda su profundidad. Un caso de uso donde todas las piezas del marco estén activas pero en su versión mínima: un skill, un tipo de documento en la KB, un canal, un tipo de output, un tipo de destinatario.

Ese caso de uso completo y funcionando con 3 clientes reales le va a decir más sobre qué parte del marco es correcto y qué parte es teoría que cualquier análisis adicional.

El marco es la brújula. El primer caso de uso completo es la primera vez que la usas y descubres si apunta bien.

---

*Marco Rector de FaberLoom — v1.0 · Arquitectura de conocimiento operativo*
*Generado: 2026-04-15*
