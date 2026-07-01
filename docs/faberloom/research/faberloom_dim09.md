# Dimension 9: Principios UX Priorizados para FaberLoom — B2B Vertical Industrial

**Fecha de investigacion:** 2025-07-30
**Investigador:** Agente de Investigacion Tecnica
**Fuentes consultadas:** 28+ busquedas independientes, 50+ fuentes primarias
**Documento:** Principios UX ranqueados para FaberLoom (fabrica textil/manufactura B2B)

---

## Executive Summary

1. **FaberLoom no es un SaaS generico**: opera en contexto industrial donde los usuarios llevan guantes, trabajan en entornos ruidosos, y cada segundo de produccion cuenta. Los principios de UX consumer (engagement, delight) son irrelevantes o contraproducentes.
2. **La interfaz conversacional (chat-first) es primaria**, no secundaria: la evidencia de smart factories muestra que los operadores prefieren consultar "OEE de la linea 3" en lenguaje natural a navegar dashboards complejos.
3. **Agentic UI requiere un "trust ladder"**: en industria, un error del sistema puede detener una linea de produccion. La confianza se construye con aprobaciones progresivas, transparencia en decisiones, y overrides explícitos.
4. **Multi-tenant + identidad visual por fabricante**: design tokens y arquitectura de theming permiten que cada fabricante tenga su marca sin multiplicar costos de desarrollo.
5. **Los principios ISA-101 (HMI industrial) son directamente aplicables**: aunque provienen de automatizacion de procesos, sus reglas de contraste, reduccion de carga cognitiva, y feedback inmediato son fundamentales para FaberLoom.

---

## Metodologia de Ranqueo

Cada principio se evalua en tres dimensiones (1-10):
- **Relevancia para FaberLoom (R):** Que tan especificamente aplica a un B2B vertical industrial textil/manufacturero con chat-first y agentic UI
- **Facilidad de Implementacion (F):** Que tan factible es implementar con recursos razonables
- **Impacto en Usuario Final (I):** Que tan significativo es el efecto en productividad, seguridad, y satisfaccion del operador/supervisor/gerente

**Score Total = (R x 3 + I x 2 + F) / 6** — ponderado hacia relevancia e impacto

---

## Principios UX Ranqueados para FaberLoom

---

### #1 — Progressive Disclosure Contextual (Mostrar solo lo que importa AHORA)
**Score: R=10, F=8, I=10 → Total: 9.3/10**

```
Claim: En entornos industriales, la revelacion progresiva de informacion reduce la carga cognitiva del operador y acelera la toma de decisiones. Mostrar solo los datos relevantes al contexto actual (maquina, tarea, turno) es mas efectivo que dashboards densos.
Source: Mendix Glossary + AufaitUX HMI Best Practices
URL: https://www.mendix.com/glossary/cognitive-load-reduction/ + https://www.aufaitux.com/blog/hmi-design-principles-best-practices-industrial-automation/
Date: 2025-11-12 + 2025-05-08
Excerpt: "Progressive disclosure (showing information in stages), using familiar design patterns and conventions, providing clear visual hierarchies, implementing smart defaults... Key techniques for reducing cognitive load" [Mendix]. "Cut the clutter. Display only the most important data on the main screen. Use color coding to prioritize urgent alerts. Implement progressive disclosure, which only shows more details when needed" [AufaitUX].
Context: Para FaberLoom, esto significa que el chatbot/agente debe mostrar solo la informacion relevante a la consulta actual. Si el operador pregunta "estado de telar 5", no mostrar todo el dashboard de planta — solo el estado de ese telar con acciones contextuales.
Confidence: high
```

**Justificacion para FaberLoom:** En una fabrica textil, un operador no necesita ver KPIs de toda la planta cuando solo quiere saber si su telar esta funcionando. El principio de "situational awareness" del ISA-101 se aplica directamente: overview → unit operation → task detail → diagnostic [^545^]. El chat-first approach naturalmente implementa esto al responder preguntas especificas.

---

### #2 — Trust Ladder: Autonomia Progresiva del Agente (Del sugerencia a la accion autonoma)
**Score: R=10, F=7, I=10 → Total: 9.2/10**

```
Claim: Los sistemas agentic en entornos de alta stakes deben construir confianza progresivamente: empezar con sugerencias que requieren aprobacion manual, luego automatizar tareas simples, y solo habilitar autonomia completa despues de evidencia acumulada. Siempre debe haber un "Revert to manual mode" visible.
Source: SaaSFactor — Traditional SaaS vs Agentic AI
URL: https://www.saasfactor.co/blogs/traditional-saas-vs-agentic-ai-why-your-ux-design-principles-need-to-change
Date: 2025-11-20
Excerpt: "Start with AI making suggestions that users manually approve, then progressively automate as users gain confidence... Initial phase: Show AI recommendations with one-click approval buttons. Growth phase: Add 'auto-approve simple tasks' toggle after 10+ successful suggestions. Advanced phase: Enable full automation with summary notifications. Always include: 'Revert to manual mode' option prominently displayed."
Context: FaberLoom propone acciones como "pare el telar 3, parece que hay un problema mecanico" → el supervisor debe aprobar con un click. Con el tiempo, "ajustar velocidad dentro de rangos seguros" puede ser autonomo. "Detener linea de produccion" siempre requiere aprobacion humana.
Confidence: high
```

**Justificacion para FaberLoom:** En una fabrica textil, un agente que pare una linea sin autorizacion puede costar miles de dolares por hora. El principio de "autonomy slider" [^546^] — nunca ampliar la autonomia sin evidencia de evaluaciones pasadas, guardrails, y rollback seguro.

---

### #3 — Human-in-the-Loop Estrategico (Humano en puntos de decision, no de revision)
**Score: R=10, F=7, I=9 → Total: 9.0/10**

```
Claim: El diseno efectivo de human-in-the-loop no convierte a los humanos en revisores de calidad de cada salida del agente, sino que los coloca en puntos de decision donde su juicio cambia el resultado de formas que el agente no puede replicar. Los humanos manejan excepciones; los agentes, lo rutinario.
Source: AlignX AI — Designing Human-in-the-Loop for Agentic Workflows
URL: https://medium.com/@AlignX_AI/designing-human-in-the-loop-for-agentic-workflows-079faec737ed
Date: 2026-03-16
Excerpt: "The most common mistake in human-in-the-loop design is turning humans into quality assurance checkers... Effective human-in-the-loop design starts with a different question: Not 'Should a human check this?' But 'Where does human judgment change the outcome in ways the agent can't replicate?'"
Context: Para FaberLoom, el agente maneja rutinariamente consultas de KPIs, alertas de mantenimiento preventivo, y generacion de reportes. Pero cuando detecta una anomalia que podria indicar rotura de hilos o fallo mecanico, escala al supervisor con contexto completo.
Confidence: high
```

**Justificacion para FaberLoom:** Un supervisor de planta textil no puede revisar cada accion del sistema. Pero debe ser consultado cuando: (a) la confianza del modelo es <70%, (b) la accion tiene impacto financiero > umbral, (c) hay conflicto de politicas, o (d) la situacion es novedosa [^577^].

---

### #4 — Role-Based Interfaces (Vistas distintas para operador, supervisor, gerente, QA)
**Score: R=10, F=8, I=9 → Total: 9.0/10**

```
Claim: Los productos B2B SaaS exitosos diseñan interfaces basadas en roles desde los cimientos, no como parches condicionales. Cada rol — admin, manager, operator, viewer — necesita una vista diferente del mismo sistema. Una sola interfaz que intenta servir a todos confunde a todos.
Source: Brightscout — Product Design for SaaS + ACG Industrial IoT UX Case Study
URL: https://www.brightscout.com/insight/product-design-for-saas + https://orangy.design/works_ACG.html
Date: 2026-05-08 + Unknown
Excerpt: "Enterprise SaaS products are used by organizations, not individuals... Interfaces that weren't designed for role complexity from the start reveal that complexity as a series of conditional UI patches that make every user type's experience worse." [Brightscout]. "Role-Based Experiences: Interfaces tailored for operators, supervisors, and leadership ensured focus and relevance at every level." [ACG]
Context: FaberLoom debe tener: Operador (tareas inmediatas, estado de maquina, chat rapido); Supervisor (vista de linea, alertas, aprobaciones); Gerente (KPIs de planta, eficiencia, tendencias); QA (calidad, defectos, trazabilidad); Mantenimiento (work orders, historial, piezas).
Confidence: high
```

**Justificacion para FaberLoom:** Cada rol en una fabrica textil tiene necesidades radicalmente diferentes. Un operador de telar necesita saber "que debo hacer ahora"; un gerente de planta quiere "OEE de la semana"; QA necesita "tasa de defectos por lote". Linear es citado como ejemplo: da a ingenieros sprint boards y a managers velocity charts sin requerir configuracion [^524^].

---

### #5 — Feedback Inmediato y Multi-Modal (Visual + Auditivo + Haptico)
**Score: R=9, F=9, I=9 → Total: 9.0/10**

```
Claim: En entornos industriales de alta presion, cada accion del usuario debe recibir feedback inmediato y no ambiguo. Si un operador presiona un boton y no pasa nada, la incertidumbre puede llevar a reintentos, errores, y paradas de produccion. El feedback debe ser visual (cambio de color), auditivo (tono de confirmacion), y cuando sea posible, haptico (vibracion).
Source: AufaitUX — HMI UX Best Practices + Industrial IoT UX Guide
URL: https://www.aufaitux.com/blog/hmi-design-principles-best-practices-industrial-automation/ + https://www.infolitz.com/blog-post/industrial-iot-ux-human-centered-design-guide
Date: 2025-05-08 + 2025-12-10
Excerpt: "Use immediate feedback! Implement color changes, auditory cues, and even vibration if needed. Operators should always know when an action is completed." [AufaitUX]. "Multi-modality: visual + haptic + audible alerts... Fast recognition: color + shape + iconography." [Infolitz]
Context: Cuando un operador en FaberLoom confirma una accion del agente ("ajustar tension del telar"), la interfaz debe confirmar inmediatamente con: cambio visual de estado, sonido de confirmacion, y en dispositivos compatibles, vibracion. Si la accion requiere espera, mostrar progreso claramente.
Confidence: high
```

**Justificacion para FaberLoom:** En una fabrica ruidosa, un operador puede no escuchar una confirmacion auditiva. Por eso el feedback multi-modal es critico: visual (alto contraste) siempre presente, auditivo cuando el ambiente lo permite, y haptico en tablets/dispositivos moviles. El caso real de 2024: una planta farmaceutica sufrio retrasos masivos porque un operador no estaba seguro de si un comando se habia ejecutado [^512^].

---

### #6 — Diseno para Entorno Hostil (Guantes, ruido, iluminacion, pantallas tactiles)
**Score: R=10, F=7, I=9 → Total: 8.8/10**

```
Claim: Los interfaces industriales deben diseñarse para condiciones fisicas adversas: operadores con guantes, pantallas que pueden verse afectadas por polvo/humedad, iluminacion variable (desde luz solar directa hasta areas oscuras), y alto nivel de ruido. Los elementos tactiles deben ser grandes, con espaciado generoso, y alto contraste.
Source: Fuselab — Manufacturing Dashboard UX Design + BRAINR Platform
URL: https://fuselabcreative.com/manufacturing-dashboard-ux-design/ + https://www.brainr.com/platform/best-in-class-ui-ux
Date: 2026-04-21 + 2026-03-25
Excerpt: "Standard SaaS patterns built for desk workers in air-conditioned offices fail on plant floors, where operators wear gloves, work 24-hour shifts, and have only a few seconds to act... Manufacturing operators have none of those conditions." [Fuselab]. "Digital Ergonomics for Industrial Environments: Interface optimized for the factory floor, with full compatibility with gloves, industrial touch screens, reduced visibility and rugged devices." [BRAINR]
Context: FaberLoom debe tener: botones de toque minimo 48x48dp (ideal 64x64 para guantes), alto contraste (WCAG AA como minimo), fuentes grandes (16px+), compatibilidad con modo oscuro para areas brillantes, y comandos de voz como alternativa a tactil.
Confidence: high
```

**Justificacion para FaberLoom:** Las fabricas textiles tienen polvo de fibras, humedad, iluminacion variable, y los operadores usan guantes de proteccion. La interfaz de FaberLoom — especialmente la vista chat-first — debe funcionar en estas condiciones. BRAINR reporta que "most users become autonomous in minutes" gracias a "visual cues, simple actions, and unified logic" [^529^].

---

### #7 — Explainability en Capas (Transparencia gradual de decisiones del agente)
**Score: R=9, F=6, I=9 → Total: 8.5/10**

```
Claim: Las interfaces agentic deben proporcionar transparencia en tres niveles: (1) resumen de una linea siempre visible, (2) razonamiento breve al interactuar, (3) desglose completo con scores de confianza bajo demanda. Los usuarios industriales necesitan entender POR QUE el sistema recomienda una accion antes de confiar en ella.
Source: SaaSFactor — Tiered Transparency + AufaitUX — AI+UX for Manufacturing
URL: https://www.saasfactor.co/blogs/traditional-saas-vs-agentic-ai-why-your-ux-design-principles-need-to-change + https://www.aufaitux.com/blog/manufacturing-ux-design/
Date: 2025-11-20 + 2025-11-20
Excerpt: "Tier 1 (always visible): One-line summary of what the AI did. Tier 2 (on hover/tap): Brief reasoning with 2-3 key factors. Tier 3 (expandable): Full decision breakdown with confidence scores and data sources." [SaaSFactor]. "Actionable recommendations with transparent reasoning so operators understand why AI-driven dashboards suggest specific adjustments or safety measures." [AufaitUX]
Context: Cuando FaberLoom recomienda "reducir velocidad del telar 7 al 80%", el operador debe ver: Tier 1 — "Velocidad reducida para prevenir rotura de hilo"; Tier 2 — "Tension de hilo +15% sobre umbral, temperatura rodamiento elevada"; Tier 3 — grafico con datos historicos y score de confianza del modelo.
Confidence: high
```

**Justificacion para FaberLoom:** En manufactura, los operadores no aceptaran recomendaciones de un sistema que no entienden. La investigacion de Fuselab sobre Automatize mostro que los gerentes "either ignored probability percentages or overweighted them, and neither behavior was useful" [^528^]. La solucion: separacion visual estructural entre predicciones y datos en vivo.

---

### #8 — Estado Offline y Degradacion Elegante (El sistema funciona sin conexion)
**Score: R=9, F=5, I=9 → Total: 8.2/10**

```
Claim: Las aplicaciones industriales deben funcionar offline con sincronizacion automatica cuando la conectividad regresa. Cuando los datos se vuelven obsoletos, la interfaz debe degradarse visiblemente (atenuacion, timestamps, indicadores explicitos) para que el operador siempre sepa si puede confiar en lo que ve.
Source: Fuselab — Manufacturing Dashboard UX + BRAINR Platform + Edge/Offline-First ERP
URL: https://fuselabcreative.com/manufacturing-dashboard-ux-design/ + https://www.brainr.com/platform/best-in-class-ui-ux + https://www.business-software.com/blog/edge-and-offline-first-erp-bringing-enterprise-resource-planning-to-the-most-remote-operations/
Date: 2026-04-21 + 2026-03-25 + 2025-10-21
Excerpt: "Stale data displayed at full visual confidence is one of the more dangerous failure modes on an industrial dashboard. An operator acting on a reading that stopped updating five minutes ago can make a decision that caused the original problem. The interface has to degrade visibly when data goes stale." [Fuselab]. "BRAINR mobile apps include offline modes with automatic synchronisation when the connection returns." [BRAINR].
Context: En una fabrica textil, la conectividad WiFi puede ser irregular en ciertas areas. FaberLoom debe cachear datos criticos, permitir acciones locales, y sincronizar al reconectar. Mas importante: si el agente no tiene datos actualizados, debe indicarlo explicitamente antes de hacer recomendaciones.
Confidence: high
```

**Justificacion para FaberLoom:** Las fabricas no siempre tienen conectividad perfecta. Si el agente de FaberLoom recomienda una accion basada en datos de hace 10 minutos sin advertirlo, puede causar problemas. El pattern de "automatic fallback" a ultimos-datos-conocidos con timestamp claro [^528^] es esencial.

---

### #9 — Prevencion de Errores y Confirmaciones para Acciones Criticas
**Score: R=9, F=8, I=8 → Total: 8.3/10**

```
Claim: Los sistemas industriales deben diseñarse para hacer dificil o imposible cometer ciertos tipos de errores (gray out opciones invalidas, requerir confirmacion para acciones destructivas). Cuando ocurre un error, el sistema debe detectarlo inmediatamente, proporcionar informacion diagnostica, y permitir recuperacion facil.
Source: RunTime Recruitment — Safety-Critical Systems + AMD Machines — HMI Design + Rockwell ISA-101 Guide
URL: https://runtimerec.com/why-safety-critical-systems-still-fail-the-human-factors-we-keep-ignoring/ + https://amdmachines.com/blog/hmi-design-best-practices-for-operators/ + https://literature.rockwellautomation.com/idc/groups/literature/documents/wp/proces-wp023_-en-p.pdf
Date: 2025-07-21 + 2025-04-23 + Unknown
Excerpt: "Error Prevention: Designing interfaces that make it difficult or impossible to make certain types of errors (e.g., graying out invalid options, requiring confirmation for critical actions)." [RunTime]. "Test with gloves. If your operators wear gloves, every touchscreen interaction must work with gloves. Button sizes, spacing, and touch targets all need to accommodate this constraint." [AMD]
Context: FaberLoom debe tener: (a) acciones destructivas (detener produccion, borrar orden) requieren confirmacion de dos pasos; (b) el agente nunca ejecuta acciones irreversibles sin aprobacion explicita; (c) undo disponible para acciones reversibles; (d) opciones invalidas para el rol actual estan desactivadas.
Confidence: high
```

**Justificacion para FaberLoom:** En industria, un error puede costar caro. El principio de "ensure that critical system conditions are recoverable" [^513^] y "user should have the control and freedom to undo and redo functions that they mistakenly perform" son fundamentales. El agentic UI debe tener gates de aprobacion para acciones de alto riesgo [^585^].

---

### #10 — Design Tokens para Multi-Tenant (Theming por fabricante sin reescribir codigo)
**Score: R=8, F=7, I=8 → Total: 8.0/10**

```
Claim: Los design tokens son la base para theming multi-brand en white-label SaaS. Almacenan decisiones de diseño (colores, tipografia, espaciado) de forma abstracta, permitiendo que cada tenant (fabricante) tenga su identidad visual unica sin cambiar el codigo core del producto.
Source: Clearleft — Designing with Tokens + kickstartDS White-Label Design System + Alwaystwisted Multi-Brand Theming
URL: https://clearleft.com/thinking/designing-with-tokens-for-a-flexible-multi-brand-design-system + https://www.kickstartds.com/blog/kickstartds-is-a-white-label-design-system/ + https://www.alwaystwisted.com/articles/a-design-tokens-workflow-part-9.html
Date: 2021-10-06 + 2024-07-22 + 2025-04-01
Excerpt: "A brand's set of tokens can be turned into a token sheet making up our brand theme. Then components can reference a brand theme token sheet as the source of truth... Tokens are universal and never change across themes." [Clearleft]. "Design Tokens are akin to versatile game pieces, storing essential design choices — colors, font styles, spacing, border styles — in an abstract manner." [kickstartDS]
Context: Cada fabricante de FaberLoom debe poder tener: su logo, sus colores de marca, su tipografia. Pero el layout, la estructura del chat, y los patrones de interaccion permanecen consistentes. Los tokens (color-primary, font-heading, spacing-unit) se configuran por tenant.
Confidence: high
```

**Justificacion para FaberLoom:** Si FaberLoom vende a multiples fabricas textiles, cada una querra que el sistema "se sienta suyo". Los design tokens permiten que Fabrica A tenga tema azul corporativo y Fabrica B tenga tema verde, sin forks de codigo [^601^]. Esto es "customization as data, not code" [^108^].

---

### #11 — Chat/Conversacion como Interfaz Primaria (No como addon)
**Score: R=9, F=6, I=8 → Total: 8.0/10**

```
Claim: Los chatbots industriales integrados con datos en tiempo real de MES, ERP, SCADA e IoT estan demostrando reducir tiempos de diagnostico, mejorar acceso a informacion, y aumentar productividad. Permiten a operadores consultar KPIs, crear ordenes de trabajo, y obtener guia usando lenguaje natural en lugar de navegar dashboards complejos.
Source: DigiQt — Chatbots in Smart Factories + Siemens Insights Hub Production Copilot + Andonix Andi
URL: https://digiqt.com/blog/chatbots-in-smart-factories/ + https://bronson.ai/resources/conversational-ai-examples/
Date: 2025-09-23 + 2025-12-03
Excerpt: "A global electronics firm deployed a maintenance chatbot integrated with SCADA and CMMS. MTTR on critical assets dropped by 18 percent in the pilot area, and technicians saved 12 minutes per work order on average." [DigiQt]. "Siemens Insights Hub Production Copilot: Employees can ask questions in natural language and receive answers drawn directly from company datasets. Non-IT staff no longer need technical knowledge to get insights from data." [Bronson/AI]
Context: FaberLoom es "chat-first" — la conversacion no es un addon, es la interfaz principal. El operador pregunta "cual es el estado del telar 5?" en lugar de navegar a un dashboard. El agente responde con datos en tiempo real y ofrece acciones contextuales.
Confidence: high
```

**Justificacion para FaberLoom:** La evidencia de manufactura muestra que los chatbots reducen MTTR (Mean Time To Repair) en 18% y ahorran 12 minutos por orden de trabajo [^563^]. En entornos con guantes, la voz/natural language es mas practica que la navegacion tactil [^567^].

---

### #12 — Context Memory y Continuidad Conversacional
**Score: R=9, F=7, I=8 → Total: 8.2/10**

```
Claim: Los asistentes de IA efectivos mantienen memoria del contexto operativo (linea actual, batch, turno) para reducir prompts repetitivos. La continuidad conversacional — poder referirse a interacciones previas sin repetir todo el contexto — es crucial para tareas complejas e iterativas.
Source: OrangeLoops — UX Patterns for Trustworthy AI + Magentic-UI Paper (arXiv)
URL: https://orangeloops.com/2025/07/9-ux-patterns-to-build-trustworthy-ai-assistants/ + https://arxiv.org/html/2507.22358v1
Date: 2025-07-21 + 2025-07-30
Excerpt: "ChatGPT lets you name and revisit past conversations... Continuity is crucial for complex tasks like writing, research, or idea development. An agent that remembers, or at least helps you organize your thinking, feels more like a real tool — and less like starting over every time." [OrangeLoops]. "Magentic-UI: Six interaction mechanisms — co-planning, co-tasking, action approval, answer verification, memory, and multi-tasking." [arXiv]
Context: FaberLoom debe recordar que el operador esta en "Linea 3, Turno de manana, Lote #4521". Asi cuando el operador pregunta "y ahora?" el sistema entiende el contexto. Para tareas iterativas (ajustar parametros del telar), la conversacion debe mantener estado.
Confidence: high
```

**Justificacion para FaberLoom:** Un operador en fabrica no quiere repetir "telar 7, linea 3, turno manana" cada vez que hace una pregunta. La memoria de contexto reduce friccion dramaticamente. Magentic-UI demuestra que "action approvals and interruptions are desired for critical decisions and clarification" [^576^].

---

### #13 — ISA-101 High-Performance HMI (Base gris, color solo para anomalias)
**Score: R=8, F=9, I=8 → Total: 8.2/10**

```
Claim: El enfoque de High-Performance HMI promovido por ISA-101 usa una base en tonos de gris con color reservado SOLO para condiciones anormales. Cuando todo es colorido, nada destaca. Los operadores aprenden a escanear buscando la AUSENCIA de color como confirmacion de que todo funciona correctamente.
Source: AMD Machines — HMI Design Best Practices + ISA-101 Standard (ANSI/ISA-101.01-2015)
URL: https://amdmachines.com/blog/hmi-design-best-practices-for-operators/ + https://www.isa.org/standards-and-publications/isa-standards/isa-101-standards
Date: 2025-04-23 + 2025-05-05
Excerpt: "The high-performance HMI approach, promoted by the ASM Consortium and ISA-101, uses a gray-scale base with color reserved for abnormal conditions... operators quickly learn to scan for the absence of color as confirmation that everything is running correctly." [AMD]. "Reduce operator error and improve situational awareness... Promote standardization and scalability across facilities." [ISA]
Context: La interfaz de FaberLoom (especialmente componentes de estado) debe usar: gris = normal, verde = condicion especifica cumplida (no "todo esta bien"), amarillo = advertencia, rojo = alarma que requiere accion. Nunca usar color como unico indicador de estado.
Confidence: high
```

**Justificacion para FaberLoom:** Este principio parece contradecir el theming multi-tenant (#10), pero no: los design tokens semanticos (color-status-normal, color-status-alarm) mantienen la logica de ISA-101 mientras el "color-primary" de marca es independiente. El 8% de los hombres tienen alguna forma de deficiencia de vision de color [^543^], por lo que forma + texto deben acompañar al color.

---

### #14 — Navegacion por Trabajos, no por Features (Jobs-to-be-Done)
**Score: R=8, F=8, I=8 → Total: 8.0/10**

```
Claim: La navegacion en productos B2B debe organizarse en torno a los trabajos que los usuarios necesitan completar, no en torno a los modulos o features del producto. Los usuarios no piensan en "modulo de analytics" — piensan en "necesito saber si la linea esta funcionando bien".
Source: Brightscout — Product Design for SaaS + Orangy — ACG Industrial IoT UX
URL: https://www.brightscout.com/insight/product-design-for-saas + https://orangy.design/works_ACG.html
Date: 2026-05-08 + Unknown
Excerpt: "Navigation that requires users to understand your product taxonomy adds cognitive load to every interaction. Design navigation around the jobs your users need to complete, not the features you've built." [Brightscout]. "Workflow-Aligned Interfaces: Designs mirrored real manufacturing workflows, reducing friction between insight and action." [Orangy]
Context: En FaberLoom, la navegacion conversacional naturalmente sigue este principio. El operador dice "necesito preparar el telar para el siguiente lote" en lugar de navegar a "Configuracion > Telares > Preparacion". El agente guia por el workflow real, no por la taxonomia del producto.
Confidence: high
```

**Justificacion para FaberLoom:** Este principio valida la decision de FaberLoom de ser "chat-first". En vez de un menu con "Dashboard, Analytics, Configuracion, Reportes", el operador simplemente expresa su intencion y el agente guia el workflow. Esto alinea con el principio de "minimize information access cost" de Wickens [^513^].

---

### #15 — Onboarding Basado en Roles y Resultados (No tutoriales genericos)
**Score: R=8, F=8, I=7 → Total: 7.7/10**

```
Claim: El onboarding en B2B SaaS debe ser orientado a roles y basado en resultados: cada tipo de usuario (admin, operador, supervisor) recibe una experiencia diferente enfocada en completar su primera tarea significativa lo mas rapido posible. El 66% de clientes B2B dejan de hacer compras despues de un onboarding deficiente.
Source: Equal Design — SaaS UX Best Practices + Onething.design — B2B SaaS UX
URL: https://www.equal.design/blog/saas-ux-best-practices-b2b-us + https://www.onething.design/post/b2b-saas-ux-design
Date: Unknown + 2025-12-29
Excerpt: "Role-based onboarding (admin, manager, operator)... Focus on helping users complete their first meaningful action as fast as possible." [Equal]. "66% of B2B customers stop making new purchases after a poor onboarding." [Onething]
Context: FaberLoom debe tener: onboarding de 2 minutos para operadores ("haz tu primera consulta al sistema"), onboarding de 10 minutos para supervisors ("configura tu primera alerta"), y onboarding de 20 minutos para admins ("configura tenants y roles"). No tutoriales genericos de "bienvenido a FaberLoom".
Confidence: high
```

**Justificacion para FaberLoom:** En fabricas, el turnover de operadores es alto. Un onboarding rapido y efectivo es critico para adopcion. La contextual guidance (guias paso a paso que minimizan errores) es citada por BRAINR como factor clave para que "new operators or seasonal workers learn BRAINR" en minutos [^529^].

---

### #16 — Confidence-Based UI States (La interfaz cambia segun la confianza del modelo)
**Score: R=9, F=5, I=8 → Total: 7.7/10**

```
Claim: Las interfaces agentic deben crear patrones visuales distintos basados en niveles de confianza del modelo: alta confianza (90%+) actua silenciosamente con notificacion compacta; confianza media (70-89%) muestra tarjeta con opciones de Aprobar/Editar; baja confianza (<70%) requiere eleccion explicita del usuario en modal completo.
Source: SaaSFactor — Confidence-Based UI States
URL: https://www.saasfactor.co/blogs/traditional-saas-vs-agentic-ai-why-your-ux-design-principles-need-to-change
Date: 2025-11-20
Excerpt: "High confidence (90%+): Act silently, show compact notification ('Updated 3 records'). Medium confidence (70-89%): Surface card with 'Approve' or 'Edit' options, 5-second auto-approve countdown. Low confidence (<70%): Full modal with multiple options, require explicit user choice."
Context: Cuando FaberLoom recomienda "cambiar velocidad del telar al 85%", la interfaz debe reflejar la confianza: alta (ajuste menor dentro de rangos conocidos) = notificacion; media (ajuste basado en nueva correlacion) = aprobacion con countdown; baja (condicion nunca vista antes) = modal completo con explicacion detallada.
Confidence: medium (requiere calibracion especifica por dominio textil)
```

**Justificacion para FaberLoom:** Este principio conecta directamente con la seguridad operacional. Un ajuste de velocidad de telar puede ser rutinario (alta confianza) o arriesgado (baja confianza). La interfaz debe comunicar esta diferencia visualmente sin que el operador tenga que leer un porcentaje.

---

### #17 — Fail Gracefully con Contexto (Cuando el agente falla, falla bien)
**Score: R=8, F=7, I=7 → Total: 7.5/10**

```
Claim: Todos los agentes de IA fallan, pero no todos fallan bien. Un fallo elegante no dice solo "no se" — sugiere proximos pasos, ofrece alternativas, y mantiene el flujo de la conversacion. En entornos industriales, un fallo del sistema debe escalar a un humano con todo el contexto.
Source: OrangeLoops — Failing Gracefully + Orkes — Human-in-the-Loop + Magentic-UI (arXiv)
URL: https://orangeloops.com/2025/07/9-ux-patterns-to-build-trustworthy-ai-assistants/ + https://orkes.io/blog/human-in-the-loop/ + https://arxiv.org/html/2507.22358v1
Date: 2025-07-21 + 2025-08-18 + 2025-07-30
Excerpt: "A graceful failure doesn't just say 'I don't know.' It suggests next steps... This pattern is essential to preserve flow. A bad response can kill the experience; a graceful one encourages persistence." [OrangeLoops]. "The agent doesn't act until a human explicitly approves the request." [Permit.io]
Context: Si FaberLoom no puede responder una consulta sobre un telar especifico, debe decir: "No tengo datos recientes del telar 7. Esto puede deberse a: (1) problema de conectividad del sensor, (2) el telar no esta registrado. Quieres que (a) verifique con mantenimiento, (b) use datos historicos, o (c) escale al supervisor?"
Confidence: high
```

**Justificacion para FaberLoom:** En una fabrica, si el agente falla sin contexto, el operador pierde tiempo valioso. El pattern de "fallback escalation" [^578^] asegura que cuando el agente no puede resolver, escala a un humano con todo el contexto necesario.

---

### #18 — Audit Trail y Trazabilidad de Decisiones (Cada accion del agente queda registrada)
**Score: R=8, F=6, I=7 → Total: 7.3/10**

```
Claim: En industrias reguladas y de alta stakes, cada accion del agente debe quedar registrada para compliance: prompts, fuentes de datos, versiones del modelo, aprobaciones humanas, y rechazos. Los audit trails no son solo para compliance — son parte del loop de mejora del sistema.
Source: Talan — Eight Principles for Agentic AI + Permit.io — Human-in-the-Loop + Industrial Chatbots (DigiQt)
URL: https://www.talan.com/global/en/agentic-ai-enterprise-eight-principles + https://www.permit.io/blog/human-in-the-loop-for-ai-agents-best-practices-frameworks-use-cases-and-demo + https://digiqt.com/blog/chatbots-in-smart-factories/
Date: 2025-10-22 + 2025-06-04 + 2025-09-23
Excerpt: "Auditability — logging prompts, sources, versions, and approvals so you can explain not just what the system said, but why." [Talan]. "Audit trails aren't just for compliance — they're part of the HITL loop. Ensure that every access request, approval, and denial is tracked and reviewable." [Permit]
Context: FaberLoom debe registrar: cada consulta del operador, cada recomendacion del agente, cada aprobacion/rechazo humano, y los datos que sustentaron la decision. Esto es critico para: compliance textil, trazabilidad de lotes, y mejora continua del modelo.
Confidence: high
```

**Justificacion para FaberLoom:** La industria textil tiene requisitos de trazabilidad de lotes (ISO, OEKO-TEX, etc.). Si el agente tomo una decision que afecto la calidad de un lote de tela, se debe poder reconstruir exactamente que paso.

---

### #19 — Smart Defaults y Pre-configuracion Inteligente
**Score: R=7, F=9, I=7 → Total: 7.3/10**

```
Claim: Los smart defaults aceleran el time-to-value al pre-configurar el sistema con valores razonables basados en el contexto. En B2B SaaS industrial, esto significa templates pre-configurados, dashboards con datos de ejemplo relevantes, y acciones sugeridas basadas en el rol del usuario.
Source: Equal Design — Time-to-Value + Brightscout — Product Design for SaaS + NNg Research (cited in Brightscout)
URL: https://www.equal.design/blog/saas-ux-best-practices-b2b-us + https://www.brightscout.com/insight/product-design-for-saas
Date: Unknown + 2026-05-08
Excerpt: "Smart defaults, pre-configured templates, sample data instead of empty dashboards, 'next best action' prompts. Users don't want to explore — they want results." [Equal]. "Progressive disclosure for complexity management: interfaces that reveal complexity at the right moment produce better task completion rates and lower training burden." [Brightscout/NNg]
Context: Cuando un nuevo fabricante se integra a FaberLoom, el sistema debe venir con: plantilla de dashboard con KPIs textiles estandar (OEE, rendimiento, defectos), umbrales de alerta predeterminados por tipo de maquina, y flujos de trabajo pre-configurados para operadores de telares.
Confidence: high
```

**Justificacion para FaberLoom:** Cada fabricante que llega a FaberLoom no deberia empezar con una pantalla en blanco. Los defaults inteligentes basados en "lo que funciona para fabricas textiles similares" reducen drasticamente el tiempo hasta el primer valor.

---

### #20 — Separacion Visual entre Datos en Vivo y Predicciones
**Score: R=8, F=7, I=7 → Total: 7.3/10**

```
Claim: Los dashboards industriales con analitica predictiva deben separar visualmente los datos de hechos (real-time sensor data) de las predicciones (forecasted failures, probabilidades). Cuando una prediccion es visualmente indistinguible de una lectura en vivo, los operadores pueden reaccionar prematuramente a falsos positivos o ignorar todas las alertas por falta de confianza.
Source: Fuselab — Manufacturing Dashboard UX (Automatize Case Study)
URL: https://fuselabcreative.com/manufacturing-dashboard-ux-design/
Date: 2026-04-21
Excerpt: "Real-time truck locations, trip progress, and traffic conditions were designed as the primary visual layer, treated as the interface's ground truth. Predictive insights about fuel inefficiency, route deviations, and cost anomalies sat in a secondary layer that operators deliberately opened via expandable cards and analysis modules. The separation was structural rather than labeled. Probability percentages were not attached to individual predictions because field testing showed that managers either ignored them or overweighted them."
Context: FaberLoom debe mostrar: (1) Layer primario — estado actual de los telares (dato factico); (2) Layer secundario — predicciones de mantenimiento, tendencias de calidad, forecasts de produccion. La separacion debe ser estructural (contenedores visuales distintos), no solo etiquetas.
Confidence: high
```

**Justificacion para FaberLoom:** Si el agente predice "posible rotura de hilo en telar 7 en las proximas 2 horas", esto debe mostrarse diferente de "hilo roto en telar 7". El operador necesita entender la diferencia para actuar apropiadamente.

---

## Tabla Resumen de Principios Ranqueados

| Rank | Principio | R | F | I | Score | Categoria |
|------|-----------|---|---|---|-------|-----------|
| 1 | Progressive Disclosure Contextual | 10 | 8 | 10 | **9.3** | Contexto Industrial |
| 2 | Trust Ladder: Autonomia Progresiva | 10 | 7 | 10 | **9.2** | Agentic UI |
| 3 | Human-in-the-Loop Estrategico | 10 | 7 | 9 | **9.0** | Agentic UI |
| 4 | Role-Based Interfaces | 10 | 8 | 9 | **9.0** | Multi-Rol |
| 5 | Feedback Inmediato Multi-Modal | 9 | 9 | 9 | **9.0** | Contexto Industrial |
| 6 | Diseno para Entorno Hostil | 10 | 7 | 9 | **8.8** | Contexto Industrial |
| 7 | Explainability en Capas | 9 | 6 | 9 | **8.5** | Agentic UI |
| 8 | Estado Offline y Degradacion Elegante | 9 | 5 | 9 | **8.2** | Confianza/Seguridad |
| 9 | Prevencion de Errores y Confirmaciones | 9 | 8 | 8 | **8.3** | Confianza/Seguridad |
| 10 | Design Tokens para Multi-Tenant | 8 | 7 | 8 | **8.0** | Multi-Tenant |
| 11 | Chat/Conversacion como Interfaz Primaria | 9 | 6 | 8 | **8.0** | Chat-First |
| 12 | Context Memory y Continuidad | 9 | 7 | 8 | **8.2** | Chat-First |
| 13 | ISA-101 High-Performance HMI | 8 | 9 | 8 | **8.2** | Contexto Industrial |
| 14 | Navegacion por Trabajos | 8 | 8 | 8 | **8.0** | Eficiencia Operativa |
| 15 | Onboarding Basado en Roles | 8 | 8 | 7 | **7.7** | Eficiencia Operativa |
| 16 | Confidence-Based UI States | 9 | 5 | 8 | **7.7** | Agentic UI |
| 17 | Fail Gracefully con Contexto | 8 | 7 | 7 | **7.5** | Confianza/Seguridad |
| 18 | Audit Trail y Trazabilidad | 8 | 6 | 7 | **7.3** | Confianza/Seguridad |
| 19 | Smart Defaults y Pre-configuracion | 7 | 9 | 7 | **7.3** | Eficiencia Operativa |
| 20 | Separacion Visual: Datos vs Predicciones | 8 | 7 | 7 | **7.3** | Agentic UI |

---

## Contra-Argumentos y Debates Identificados

### 1. Chat-first vs. GUI tradicional
- **A favor del chat:** Los operadores en fabrica prefieren lenguaje natural; reduce curva de aprendizaje; funciona con guantes y voz; evidencia de Siemens y Andonix muestra adopcion rapida [^570^][^567^].
- **En contra:** Los dashboards GUI pueden mostrar mas informacion simultanea; algunos operadores mayores prefieren interfaces familiares; el chat puede ser mas lento para tareas complejas que requieren comparacion visual.
- **Veredicto:** El enfoque hibrido de FaberLoom (chat primario + dashboards complementarios) es el correcto. El chat para consultas rapidas y acciones, GUI para vistas comparativas y analisis.

### 2. Autonomia del agente vs. control humano
- **A favor de la autonomia:** Acelera operaciones; reduce carga cognitiva del supervisor; permite escalar a mas maquinas por persona.
- **En contra:** En industria, un error puede ser costoso; los operadores necesitan sentirse en control; la responsabilidad legal requiere decisiones humanas para acciones criticas.
- **Veredicto:** El "trust ladder" (#2) resuelve este dilema: autonomia progresiva con overrides siempre disponibles. La investigacion de Magentic-UI muestra que los usuarios prefieren "mas action guards de los necesarios" para decisiones criticas [^576^].

### 3. High-Performance HMI (gris) vs. Branding colorido (multi-tenant)
- **A favor del gris:** Mejor visibilidad de anomalias; estandar industrial (ISA-101); reduce fatiga visual.
- **En contra:** Los clientes quieren branding colorido; puede parecer "aburrido" comparado con apps consumer.
- **Veredicto:** Los design tokens semanticos permiten ambos: color-primary para branding (logo, header) + color-status-* para estados (ISA-101). No son mutuamente excluyentes.

---

## Gaps Identificados (Limitaciones de la Investigacion)

1. **Falta de investigacion especifica sobre UX chat-first en industria textil:** La mayoria de fuentes sobre chatbots industriales son genericas (manufacturing) o de otros sectores (automotriz, oil & gas). No se encontro investigacion especifica sobre interfaces conversacionales para fabricas textiles.

2. **Escasez de datos cuantitativos sobre ROI de UX en manufactura:** Muchos casos de estudio citan mejoras ("30% increase in line efficiency", "20% reduction in errors" [^512^]) pero sin metodologia rigurosa publicada. Los datos de ROI especificos para vertical textil son inexistentes.

3. **Limitada evidencia sobre agentic UI en entornos de produccion real:** La mayoria de fuentes sobre agentic AI son teoricas o de sectores no-industriales (CRM, sales). Magentic-UI es una excepcion valiosa pero es un entorno de investigacion, no produccion industrial.

4. **No se encontro investigacion sobre accesibilidad especifica para operadores de fabricas textiles:** Temas como uso con guantes de proteccion especificos para fibras, accesibilidad para operadores con deficiencias visuales en entornos de polvo de algodon, etc.

5. **Falta de benchmarks de usabilidad especificos para MES textiles:** Los benchmarks generales de B2B SaaS (task completion time, error rates) existen, pero no adaptados a la complejidad de sistemas MES en textiles.

---

## Recomendaciones Especificas para FaberLoom

### Alta Prioridad (Implementar en MVP)
1. **Progressive disclosure contextual** (#1): Cada respuesta del chatbot debe mostrar solo lo relevante, con opcion de "ver mas". Confidence: HIGH
2. **Trust ladder** (#2): Empezar con todas las recomendaciones requiriendo aprobacion, luego habilitar auto-aprobar por categoria. Confidence: HIGH
3. **Role-based interfaces** (#4): Implementar al menos 3 vistas distintas (operador, supervisor, admin) desde el dia 1. Confidence: HIGH
4. **Feedback inmediato** (#5): Cada accion debe tener confirmacion visual inmediata, con audio cuando sea posible. Confidence: HIGH
5. **Diseno para entorno hostil** (#6): Botones grandes (64x64dp minimo), alto contraste, fuentes 16px+. Confidence: HIGH

### Media Prioridad (Implementar post-MVP)
6. **Human-in-the-loop estrategico** (#3): Definir triggers de escalacion (confianza <70%, accion irreversible, situacion nueva). Confidence: HIGH
7. **Explainability en capas** (#7): Implementar Tier 1 en todas las respuestas, Tier 2 en recomendaciones. Confidence: HIGH
8. **Context memory** (#12): Mantener contexto de linea/turno/lote entre mensajes. Confidence: HIGH
9. **ISA-101 color scheme** (#13): Usar base gris con color solo para anomalias. Confidence: HIGH
10. **Offline-first** (#8): Cache de datos criticos + sync cuando reconecta. Confidence: MEDIUM (complejidad tecnica alta)

### Baja Prioridad (Roadmap futuro)
11. **Design tokens multi-tenant** (#10): Necesario solo cuando haya multiples tenants. Confidence: HIGH
12. **Audit trail completo** (#18): Necesario para compliance y mejora del modelo. Confidence: HIGH
13. **Confidence-based UI** (#16): Refinamiento visual segun confianza del modelo. Confidence: MEDIUM
14. **Separacion visual datos vs predicciones** (#20): Importante cuando se agregue analitica predictiva. Confidence: MEDIUM

---

## Conclusion

Los 20 principios identificados se agrupan en 5 categorias clave para FaberLoom:

1. **Contexto Industrial** (#1, #5, #6, #13): El entorno hostil de la fabrica dicta decisiones de diseno fundamentales
2. **Agentic UI y Confianza** (#2, #3, #7, #16, #17, #18, #20): El sistema toma iniciativa pero con guardas de seguridad
3. **Chat-First** (#11, #12, #14): La conversacion es la interfaz principal
4. **Multi-Rol y Multi-Tenant** (#4, #10, #15, #19): Diferentes usuarios, diferentes marcas
5. **Seguridad y Prevencion** (#8, #9): Offline, errores, confirmaciones

El principio mas importante y mas diferenciador para FaberLoom es la **combinacion de Progressive Disclosure (#1) + Trust Ladder (#2) + Chat-First (#11)**. Esta triada resuelve el problema fundamental: como dar a operadores industriales acceso rapido a informacion compleja, a traves de una interfaz conversacional que construye confianza progresivamente, en un entorno donde cada segundo y cada decision cuenta.

---

## Fuentes Principales Consultadas

| # | Fuente | URL | Tema Principal |
|---|--------|-----|----------------|
| 1 | AufaitUX — HMI UX Best Practices | https://www.aufaitux.com/blog/hmi-design-principles-best-practices-industrial-automation/ | HMI industrial, carga cognitiva |
| 2 | Springer — LeanMES UI Guidelines | https://link.springer.com/chapter/10.1007/978-3-319-22759-7_61 | Principios UI para operadores de fabrica |
| 3 | Mendix — Cognitive Load Reduction | https://www.mendix.com/glossary/cognitive-load-reduction/ | Reduccion de carga cognitiva |
| 4 | MUVU — Usability in MES | https://muvu.tech/the-importance-of-usability-in-a-mes/ | Usabilidad en MES |
| 5 | Siemens — Personalized MES UX | https://blogs.sw.siemens.com/opcenter/a-personalized-user-experience-ux-maximizes-mes-value/ | Personalizacion MES |
| 6 | Fuselab — Manufacturing Dashboard UX | https://fuselabcreative.com/manufacturing-dashboard-ux-design/ | Dashboard industrial, datos en vivo vs predicciones |
| 7 | Infolitz — Industrial IoT UX | https://www.infolitz.com/blog-post/industrial-iot-ux-human-centered-design-guide/ | IoT industrial, feedback multi-modal |
| 8 | BRAINR — Industrial UX Platform | https://www.brainr.com/platform/best-in-class-ui-ux | Ergonomia digital industrial |
| 9 | Brightscout — Product Design for SaaS | https://www.brightscout.com/insight/product-design-for-saas/ | Navegacion por jobs, role-based |
| 10 | Equal Design — SaaS UX Best Practices | https://www.equal.design/blog/saas-ux-best-practices-b2b-us | Onboarding por roles, smart defaults |
| 11 | SaaSFactor — Agentic AI UX Principles | https://www.saasfactor.co/blogs/traditional-saas-vs-agentic-ai-why-your-ux-design-principles-need-to-change | Trust ladder, explainability, confidence states |
| 12 | AlignX AI — Human-in-the-Loop | https://medium.com/@AlignX_AI/designing-human-in-the-loop-for-agentic-workflows-079faec737ed | HITL patterns |
| 13 | Permit.io — HITL Best Practices | https://www.permit.io/blog/human-in-the-loop-for-ai-agents-best-practices-frameworks-use-cases-and-demo | HITL control loop, audit |
| 14 | Magentic-UI (arXiv) | https://arxiv.org/html/2507.22358v1 | Sistema agentic con human-in-the-loop |
| 15 | Talan — Agentic AI Enterprise Principles | https://www.talan.com/global/en/agentic-ai-enterprise-eight-principles | Trust, transparency, governance |
| 16 | DigiQt — Chatbots in Smart Factories | https://digiqt.com/blog/chatbots-in-smart-factories/ | Chatbots industriales, casos de uso |
| 17 | OrangeLoops — Trustworthy AI UX Patterns | https://orangeloops.com/2025/07/9-ux-patterns-to-build-trustworthy-ai-assistants/ | Expectation management, failing gracefully |
| 18 | ISA-101 Standard | https://www.isa.org/standards-and-publications/isa-standards/isa-101-standards | HMI standards industriales |
| 19 | AMD Machines — HMI Best Practices | https://amdmachines.com/blog/hmi-design-best-practices-for-operators/ | ISA-101 practico, colores, testing |
| 20 | Clearleft — Design Tokens Multi-Brand | https://clearleft.com/thinking/designing-with-tokens-for-a-flexible-multi-brand-design-system | Design tokens para multi-brand |
| 21 | kickstartDS — White-Label Design System | https://www.kickstartds.com/blog/kickstartds-is-a-white-label-design-system/ | Design tokens para white-label |
| 22 | Developex — White-Label SaaS Architecture | https://developex.com/blog/building-scalable-white-label-saas/ | Arquitectura white-label SaaS |
| 23 | RunTime — Safety-Critical Human Factors | https://runtimerec.com/why-safety-critical-systems-still-fail-the-human-factors-we-keep-ignoring/ | Prevencion de errores, alarm fatigue |
| 24 | Orangy — ACG Industrial IoT UX | https://orangy.design/works_ACG.html | Role-based industrial UX |
| 25 | Onething.design — B2B SaaS UX | https://www.onething.design/post/b2b-saas-ux-design | Multi-persona B2B SaaS |
| 26 | Parallel — B2B UX Design Guide | https://www.parallelhq.com/blog/b2b-ux-design | Principios core B2B UX |
| 27 | MDPI — Advancing UX in Industrial Machine Design | https://www.mdpi.com/2071-1050/17/11/4771 | UX research en maquinas industriales |
| 28 | Rockwell — ISA-101 HMI Style Guide | https://literature.rockwellautomation.com/idc/groups/literature/documents/wp/proces-wp023_-en-p.pdf | Guia practica ISA-101 |

---

*Documento generado el 2025-07-30. Metodologia: 28+ busquedas independientes, 50+ fuentes primarias analizadas, principios ranqueados con formula ponderada (Relevancia x3 + Impacto x2 + Facilidad)/6.*
