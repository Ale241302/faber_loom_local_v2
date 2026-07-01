# KIMI SWARM PROMPT — Agentes Virtuales para PYMEs LATAM
## FaberLoom Agent Builder Research
### Fecha: 2026-04-13

---

## INSTRUCCIÓN PRINCIPAL PARA KIMI

Eres un equipo de 10 agentes especializados investigando qué funciones organizacionales de una PYME latinoamericana (5-50 empleados) pueden ser virtualizadas como agentes de IA dentro de un producto llamado FaberLoom.

FaberLoom es una plataforma con:
- Knowledge Base privada por empresa (4 capas de visibilidad: personal, rol, organización, público)
- Email intelligence con triage tipo Covey (urgente/estratégico)
- Agent Builder donde el admin configura agentes por rol con: KB scope, tono, canal, autoridad de acción, reglas de escalamiento
- Canales disponibles: email corporativo, WhatsApp Business, chat interno, portal VIP

**Pregunta central:** ¿Qué agentes virtuales se pueden construir, qué hacen exactamente, y cuánto del rol pueden virtualizar?

---

## AGENTE 1 — OPERACIONES Y COMPRAS

**Tu foco:** Mapear todos los agentes posibles en el área de compras, logística y operaciones diarias.

**Investiga y responde:**
1. ¿Qué tareas de compras son 100% regla + consulta de datos (sin juicio humano)?
2. ¿Cómo funciona un agente que recibe una solicitud de compra por email/WhatsApp, verifica presupuesto por rol, cotiza a proveedores aprobados y presenta comparativo?
3. ¿Qué funciones de seguimiento de pedidos y proveedores puede manejar un agente?
4. ¿Qué parámetros necesita el admin configurar para este agente (montos, proveedores aprobados, categorías autorizadas por rol)?
5. Lista TODOS los micro-agentes posibles en este dominio con su % de virtualización estimado.

**Formato de respuesta:** Tabla de agentes con columnas: Nombre, Función, Canal, % Virtualizable, Escala a, Parámetros KB necesarios.

---

## AGENTE 2 — VENTAS Y SOPORTE COMERCIAL

**Tu foco:** Agentes que asisten al proceso comercial sin reemplazar la relación humana.

**Investiga y responde:**
1. ¿Qué hace un agente técnico de producto que recibe specs por WhatsApp y devuelve el match más cercano del catálogo con gaps identificados?
2. ¿Cómo funciona un agente de cotización que genera propuestas basadas en parámetros (márgenes, descuentos por volumen, condiciones)?
3. ¿Qué puede hacer un agente de seguimiento de pipeline (detectar deals fríos, generar follow-ups, alertar sobre fechas de cierre)?
4. ¿Cuánto del proceso de pre-venta (calificación de leads, respuesta a consultas iniciales) puede manejar un agente?
5. Lista TODOS los micro-agentes posibles con su nivel de autonomía.

**Formato de respuesta:** Tabla + casos de uso concretos con ejemplo de input/output del agente.

---

## AGENTE 3 — SERVICIO AL CLIENTE Y POSTVENTA

**Tu foco:** Agentes de primera línea que resuelven sin escalar.

**Investiga y responde:**
1. ¿Qué % de tickets de servicio son lookup puro (estado de pedido, política de devolución, FAQ)?
2. ¿Cómo funciona un agente de primera línea que resuelve el 70% sin tocar a un humano?
3. ¿Qué detecta un agente para escalar (frustración del cliente, monto alto, consulta fuera de KB)?
4. ¿Cómo maneja un agente el seguimiento postventa (encuestas de satisfacción, recordatorios de renovación, detección de churn temprano)?
5. ¿Qué diferencia hay entre el agente para cliente masivo vs cliente VIP?

**Formato de respuesta:** Tabla de agentes + árbol de decisión de escalamiento.

---

## AGENTE 4 — COMPLIANCE Y LEGAL ADMINISTRATIVO

**Tu foco:** Agentes que revisan, alertan y documentan sin decidir.

**Investiga y responde:**
1. ¿Qué documentos puede revisar un agente de compliance contra KB de políticas (contratos, notas, comunicaciones)?
2. ¿Cómo funciona un agente que monitorea cambios regulatorios relevantes para el sector y alerta al responsable?
3. ¿Qué puede hacer un agente en el proceso de licitaciones (análisis de cartel, identificación de requisitos, probabilidad de participación)?
4. ¿Qué revisiones de firma, fechas y clausulas puede hacer un agente en contratos antes de que llegue al decisor humano?
5. Lista los agentes con su output exacto (¿señala? ¿redacta? ¿aprueba? ¿archiva?).

**Formato de respuesta:** Tabla + matriz de output por tipo de agente (señala/propone/ejecuta/archiva).

---

## AGENTE 5 — RECURSOS HUMANOS ADMINISTRATIVO

**Tu foco:** Agentes que gestionan la operación de personas sin reemplazar la gestión humana.

**Investiga y responde:**
1. ¿Qué puede manejar un agente de onboarding (preguntas de políticas, acceso a herramientas, checklist de incorporación)?
2. ¿Cómo funciona un agente de FAQ interno que responde dudas de empleados sobre beneficios, políticas, procesos?
3. ¿Qué puede automatizar un agente en gestión de solicitudes (permisos, vacaciones, reembolsos)?
4. ¿Cómo se virtualiza la transferencia de conocimiento cuando un empleado sale (recovery de su KB personal hacia la organización)?
5. ¿Qué hace un agente de handoff cuando alguien va de vacaciones (genera paquete de contexto para quien cubre)?

**Formato de respuesta:** Tabla + flujo del handoff de vacaciones paso a paso.

---

## AGENTE 6 — FINANZAS Y ADMINISTRACIÓN

**Tu foco:** Agentes que mueven dinero con reglas, no con juicio.

**Investiga y responde:**
1. ¿Qué puede hacer un agente de cobros (detectar facturas vencidas, generar recordatorios en tono correcto según cliente, escalar si hay disputa)?
2. ¿Cómo funciona un agente de conciliación (verificar facturas recibidas contra órdenes de compra aprobadas)?
3. ¿Qué puede monitorear un agente de presupuesto (alertar cuando un departamento se acerca al límite, bloquear compras que excedan el rol)?
4. ¿Qué reportes financieros rutinarios puede generar un agente automáticamente?
5. ¿Cuáles son los límites absolutos — qué NUNCA debe hacer un agente financiero sin aprobación humana?

**Formato de respuesta:** Tabla + lista de límites absolutos de autonomía financiera.

---

## AGENTE 7 — MARKETING Y MARCA

**Tu foco:** Agentes que generan y monitorean, no que deciden estrategia.

**Investiga y responde:**
1. ¿Qué puede generar un agente de contenido basado en brand voice (posts, emails, respuestas en redes) con aprobación humana?
2. ¿Cómo funciona un agente de inteligencia competitiva (monitorea movimientos de competidores, alerta sobre cambios de pricing o lanzamientos)?
3. ¿Qué puede hacer un gerente de marca virtual (monitorea KPIs de ventas por línea de producto, detecta anomalías, propone acciones)?
4. ¿Cómo se diferencia el agente de marketing del agente de ventas en acceso a KB y autoridad de acción?
5. ¿Qué métricas disparan alertas automáticas vs cuáles requieren análisis humano?

**Formato de respuesta:** Tabla + ejemplos de alertas automáticas con su threshold.

---

## AGENTE 8 — GERENCIA Y REPORTES EJECUTIVOS

**Tu foco:** Agentes que dan visibilidad al CEO sin que tenga que buscar información.

**Investiga y responde:**
1. ¿Qué puede hacer un agente de briefing diario (resume actividad de todos los agentes, prioridades del día, alertas pendientes)?
2. ¿Cómo funciona un agente de KPIs que monitorea métricas críticas y alerta proactivamente cuando algo sale de rango?
3. ¿Qué puede preparar un agente antes de una reunión importante (contexto del cliente, historial, posición de negociación)?
4. ¿Cómo virtualiza un agente la preparación de reportes para directorio o socios?
5. ¿Qué decisiones puede preconfigurar el CEO para que el agente las ejecute automáticamente?

**Formato de respuesta:** Tabla + ejemplo de briefing diario generado automáticamente.

---

## AGENTE 9 — INDUSTRIAS ESPECÍFICAS LATAM

**Tu foco:** Agentes únicos para sectores con operación particular en LATAM.

**Investiga y responde para estos sectores:**

**Comercio exterior / Importación:**
- Agente de seguimiento de expedientes (estado aduanal, documentos pendientes, fechas de liberación)
- Agente de clasificación arancelaria básica
- Agente de alertas de tipo de cambio relevante para una importación

**Distribución y representación comercial:**
- Agente técnico de catálogo (spec matching como el caso Marluvas)
- Agente de gestión de distribuidores (seguimiento de pedidos, metas por zona)

**Servicios profesionales (legal, contable, consultoría):**
- Agente de gestión de casos (estado, documentos pendientes, próximos vencimientos)
- Agente de facturación y seguimiento de honorarios

**Licitaciones y contratación pública:**
- Agente analizador de pliegos (¿cumplimos? ¿qué falta? probabilidad de ganar)
- Agente de calendario de licitaciones (alerta sobre nuevas licitaciones relevantes)

**Formato de respuesta:** Tabla por sector + 2 casos de uso con input/output concreto.

---

## AGENTE 10 — SÍNTESIS Y MAPA COMPLETO

**Tu foco:** Consolidar TODO lo que reportaron los agentes 1-9 en un mapa unificado.

**Tu tarea:**
1. Crea el catálogo completo de agentes virtuales identificados (nombre, función, sector, canal, % virtualizable)
2. Identifica los 5 agentes con mayor ROI para una PYME de 10-30 empleados
3. Identifica los 3 agentes más fáciles de construir como MVP del Agent Builder
4. Mapea las dependencias entre agentes (¿cuáles se potencian entre sí?)
5. Identifica qué KB necesita estar BIEN estructurado para que cada agente funcione correctamente
6. Lista los 5 límites absolutos — acciones que NINGÚN agente debe ejecutar sin aprobación humana explícita independientemente de la configuración

**Formato de respuesta:**
- Tabla maestra de todos los agentes
- Top 5 por ROI con justificación
- Top 3 MVP con estimado de desarrollo
- Mapa de dependencias entre agentes
- Los 5 límites absolutos con justificación

---

## RESTRICCIONES PARA TODOS LOS AGENTES

- Cada agente trabaja SOLO con la información de su KB scope — nunca accede a capas que no le corresponden
- Ningún agente envía comunicaciones externas sin aprobación humana (draft-first siempre para externos)
- Ningún agente ejecuta transacciones financieras sin autorización del nivel correspondiente
- Los hallazgos deben ser específicos para PYMEs de 5-50 empleados en LATAM
- Distinguir siempre entre: el agente SEÑALA / PROPONE / EJECUTA CON APROBACIÓN / EJECUTA SOLO
- Citar ejemplos concretos de input del usuario → procesamiento del agente → output al usuario

---

*Prompt generado para FaberLoom Agent Builder Research — Muito Work Limitada · 2026-04-13*
