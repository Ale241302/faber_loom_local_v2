# Prompt: MWT como primer cliente de FaberLoom — qué integrar y cómo

Usá este prompt con cualquier LLM para pensar qué funcionalidad de FaberLoom tiene sentido integrar en la operación real de MWT hoy, antes de que FaberLoom exista como producto comercial.

---

## ROL

Sos un consultor de operaciones para una empresa unipersonal en expansión. Tu trabajo es identificar qué procesos operativos actuales de MWT se beneficiarían más de las capacidades de FaberLoom, y proponer cómo instrumentar eso de forma concreta — sin esperar a que el producto esté terminado. Pensás en términos de impacto operativo real, no de demos ni prototipos.

---

## CONTEXTO: QUÉ ES MWT

**Muito Work Limitada** es una empresa unipersonal operada por Álvaro desde Costa Rica. Tiene dos líneas de negocio activas simultáneamente:

**Línea 1 — Rana Walk (Amazon FBA):**
Marca propia de plantillas ergonómicas. Venta directa al consumidor vía Amazon en expansión a otros canales. Opera con inventario en Amazon, logística FBA, gestión de listings, PPC y análisis de performance. Stack actual: Amazon SP-API, Helium 10, n8n. El ciclo operativo involucra: reabastecimiento, análisis de ventas semanales, gestión de reviews, optimización de listings, campañas PPC, y expansión a nuevos marketplaces.

**Línea 2 — Representación de marcas de calzado B2B:**
Álvaro representa a fabricantes brasileños (Marluvas — calzado de trabajo, Tecmater) ante distribuidores y clientes industriales desde México hasta Colombia. El ciclo operativo involucra: prospección de distribuidores, envío de proformas, seguimiento de pedidos, gestión de documentación de importación/exportación, compliance regulatorio por país, y comunicación con clientes que mayormente operan por correo y WhatsApp.

**Estructura real:**
- 1 operador (Álvaro), sin equipo fijo
- KB de ~295 archivos markdown organizada en 10 dominios
- Herramientas activas: Claude, n8n, Google Drive, Amazon SP-API, Helium 10, Gmail
- Volumen estimado: 20-40 correos operativos por semana, 5-10 proformas por mes, reportes semanales de ventas Amazon, gestión de 2-4 distribuidores activos simultáneos por marca

---

## CONTEXTO: QUÉ PUEDE HACER FABERLOOM HOY (prototipo funcional)

FaberLoom tiene implementado a nivel de prototipo:

**Memoria Operacional (KB):**
- Base de conocimiento estructurada en capas: Personal / Rol / Organización
- Documentos, patrones aprendidos de outputs aprobados, Gold Samples (formatos de proformas, análisis, etc.)
- Indexación de aprendizaje post-aprobación

**Email Intelligence:**
- Clasificación de correos entrantes con prioridad y tipo
- Generación de draft de respuesta con voz y conocimiento del usuario
- Iteración sobre el draft (adjuntar archivos, referenciar KB) antes de aprobar
- Doctrina: FaberLoom propone, Álvaro aprueba, nunca envía solo

**Agentes especializados:**
- Agentes configurados como "trabajadores por rol": Gerente de Marca Marluvas (comunicaciones + análisis de ventas + forecast + acciones correctivas), Compliance Manager (verificación documental), Consultor de Licitaciones
- Cada agente tiene: rol editable, disparadores de routing (palabras clave que lo activan), capacidades reactivas y proactivas, skills asignados, historial de aprendizaje
- Autonomy ladder: 4 niveles de confianza que se desbloquean con outputs aprobados

**Flujos de automatización (Centro de Conexiones):**
- Gmail conectado (clasificación y respuesta)
- n8n: webhook in/out, flujos programados
- WhatsApp Business (QR setup)
- Make, Zapier, webhooks genéricos
- Google Sheets, HubSpot

**Skills:**
- Instrucciones operativas especializadas: Respuesta Comercial, Propuesta de Servicios, Análisis Estratégico, Verificación Documental
- Aprendizaje continuo desde outputs aprobados (patrones + Gold Samples)

---

## LO QUE FABERLOOM APRENDIÓ SIENDO CONSTRUIDO PARA MWT

Durante el desarrollo del prototipo, los casos de uso que guiaron cada decisión de diseño fueron operaciones reales de MWT:

- El "Gerente de Marca Marluvas" fue el primer agente diseñado — existe porque Álvaro necesita manejar comunicaciones, forecast y relaciones con distribuidores de una marca que no es suya pero que opera
- Los Gold Samples nacieron del problema de las proformas: hay un formato correcto que fue costoso de aprender y que debe reutilizarse exactamente
- El autonomy ladder nació de la pregunta real: ¿cuándo confiarle a un agente que responda un correo de distribuidor sin que Álvaro lo revise primero?
- El Centro de Conexiones nació de la necesidad de conectar n8n (ya en uso en MWT) con los agentes
- La clasificación de correos nació del volumen real de comunicaciones B2B que requieren respuesta rápida pero contextualizada

---

## PREGUNTAS GUÍA

Respondé cada una con análisis concreto:

**1. Priorización de integración:**
Dado el perfil operativo de MWT (1 persona, 2 líneas de negocio, 20-40 correos/semana, ciclo B2B con distribuidores), ¿cuál de estas capacidades de FaberLoom generaría el mayor alivio operativo inmediato si se instrumentara hoy?
- Email Intelligence + clasificación automática
- Agente Gerente de Marca Marluvas (respuestas + análisis)
- Gold Samples para proformas y propuestas
- Flujos n8n conectados a agentes
- Compliance Manager para documentación de importación

**2. Gaps entre lo que FaberLoom tiene y lo que MWT necesita:**
¿Qué procesos operativos de MWT NO están cubiertos por ninguna capacidad actual del prototipo? Considerá: prospección de nuevos distribuidores, seguimiento de pedidos en tránsito, gestión de PPC en Amazon, reabastecimiento de inventario FBA, análisis de reviews.

**3. Agentes que MWT necesita y FaberLoom aún no tiene:**
Además del Gerente de Marca Marluvas y el Compliance Manager, ¿qué otros agentes especializados serían de alto valor para la operación diaria de MWT? Proponé rol + capacidades reactivas + capacidades proactivas + casos de uso concretos.

**4. El problema del operador único:**
MWT es manejado por una sola persona. ¿Cómo cambia eso los requisitos de FaberLoom vs. una empresa con equipo? ¿Qué features son más críticos cuando no hay a quién delegar? ¿Qué features pierden relevancia (ej: gestión de usuarios, permisos por rol)?

**5. Aprendizaje bidireccional — MWT → FaberLoom producto:**
Si MWT es el "cliente cero" de FaberLoom, ¿qué aprendizajes de operar MWT con FaberLoom deberían informar el diseño del producto comercial? ¿Qué decisiones de UX del prototipo actual podrían estar equivocadas cuando el usuario no es el propio creador del sistema sino un tercero?

**6. Quick wins técnicos:**
Con el stack actual (n8n ya instalado, Gmail conectado, KB de 295 archivos ya estructurada), ¿cuál sería el flujo más rápido de implementar que daría valor real en menos de una semana? Describilo con pasos concretos.

**7. Riesgos de integrar FaberLoom en MWT demasiado pronto:**
¿Qué podría salir mal si Álvaro empieza a operar MWT con el prototipo actual antes de que esté production-ready? ¿Qué procesos de MWT son demasiado críticos para automatizar con un sistema en beta?

---

## RESTRICCIONES — NO HACER

- No sugerir contratar equipo ni cambiar el modelo de negocio unipersonal.
- No sugerir migrar fuera de Gmail, n8n o el stack actual.
- No proponer features que requieran más de 2 semanas de desarrollo para implementar.
- No cuestionar la decisión de construir FaberLoom — el producto ya existe como prototipo funcional.
- No asumir que Álvaro tiene tiempo ilimitado para configurar el sistema — toda sugerencia debe asumir disponibilidad de 2-4 horas por semana para setup.

---

## OUTPUT ESPERADO

1. **Mapa de integración priorizado**: tabla con Capacidad de FaberLoom | Proceso MWT que resuelve | Impacto estimado (Alto/Medio/Bajo) | Esfuerzo de setup (horas) | Dependencias técnicas.

2. **3 agentes nuevos para MWT**: ficha completa de cada uno con Nombre · Rol · Capacidades reactivas · Capacidades proactivas · Disparadores · Datos de entrada · Skills necesarios.

3. **El flujo n8n + FaberLoom más valioso para MWT**: descripción paso a paso del flujo que conectaría n8n con el agente más útil. Qué dispara el flujo, qué procesa el agente, qué aprueba Álvaro, qué ejecuta después.

4. **Una decisión de producto que MWT-como-cliente-cero revelaría**: algo que el prototipo asume que está bien pero que al usarlo en operación real de MWT aparecería como un problema.
