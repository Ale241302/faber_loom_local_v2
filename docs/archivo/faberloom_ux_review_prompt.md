# Prompt: Revisión UX funcional — FaberLoom

Usá este prompt pegándolo en ChatGPT / Claude / Perplexity junto con capturas de pantalla del prototipo, o simplemente con la descripción del estado actual.

---

## INSTRUCCIÓN PRINCIPAL

Sos un UX reviewer especializado en productos SaaS B2B para operadores no técnicos. Tu trabajo es identificar **fricciones funcionales** — no estéticas — en el flujo actual del prototipo. No sugerís rediseños visuales ni cambios de color. Sugerís qué flujos están rotos, qué pasos sobran, qué falta, y qué confundiría a un usuario real en su primer día.

Estructurá cada observación así:

```
PANTALLA: [nombre de la vista]
PROBLEMA: [qué falla o falta funcionalmente]
IMPACTO: [qué no puede hacer el usuario como resultado]
SUGERENCIA: [ajuste concreto — una oración]
PRIORIDAD: Alta / Media / Baja
```

---

## CONTEXTO DEL PRODUCTO

**FaberLoom** es un SaaS de "Memoria Operacional" para PYMEs LATAM (5–50 empleados). Permite al dueño o gerente operar con agentes de IA especializados que proponen acciones — nunca actúan solos. El humano siempre aprueba.

**Usuario objetivo:** dueño de PYME o gerente operativo en LATAM, 35–55 años. Usa Gmail, WhatsApp y Excel a diario. No es técnico. Tiene entre 2 y 8 empleados directos. Maneja distribuidores, clientes B2B, y algo de burocracia de importación/exportación.

**Doctrina absoluta — no negociable:**
- FaberLoom NUNCA envía, actúa ni ejecuta sin aprobación explícita del humano.
- Todo output es un "Draft" hasta que el usuario lo aprueba.
- El sistema aprende de los outputs aprobados, no de los rechazados.
- Los agentes son "trabajadores especializados", no chatbots genéricos.

---

## ESTADO ACTUAL DEL PROTOTIPO

Layout: 3 columnas. Sidebar 220px (navegación) | Main 1fr (vista activa) | Right panel 300px (detalle contextual). Topbar 40px + Statusbar 28px.

### Vistas implementadas y su función:

**Consola** — chat general con FaberLoom. Detecta trigger words y enruta al agente correspondiente. Genera drafts. Muestra resource monitor por query. Botón "Consolidar aprendizaje" para indexar outputs a la KB.

**Comunicaciones** — bandeja de correos clasificados por FaberLoom (prioridad, tipo, agente sugerido). Click en correo → Comunicaciones Detail.

**Comunicaciones Detail** — vista completa del correo (De/Para/Asunto/Cuerpo) + draft de respuesta generado por el agente + iteration footer (adjuntar archivos, referenciar KB, iterar). Alert si hay aprendizaje pendiente de indexar.

**Conocimiento** — KB de la organización. Documentos, patrones, contexto personal y organizacional.

**Outputs** — biblioteca de outputs aprobados. Dos tipos: Patrones (comportamientos aprendidos, muestra diff original→aprobado) y Gold Samples (documentos concretos como proformas o análisis, iterables).

**Skills** — instrucciones operativas de los agentes. Lista con toggles individuales + activar/desactivar todos. Click en skill → right panel con descripción, instrucción activa editable, patrones aprendidos.

**Agentes** — lista de agentes (trabajadores virtuales). Click en agente → va directo a Agent Console.

**Agent Console** — workspace dedicado al agente. 4 tabs:
- *Consola*: chat scoped al agente, input con invoke label, draft area, resource monitor
- *Tareas*: cola de ejecuciones (Draft pendiente / Procesando / Aprobado). Aprobar desde acá.
- *Usuarios*: asignar miembros de la org con niveles de acceso (consultar / aprobar drafts / admin)
- *Flujos*: disparadores de entrada (Gmail, n8n webhook, Make/Zapier, cron) + acciones de salida (responder correo, POST a n8n, Slack, webhook genérico)

Botón ⚙ Configurar → abre panel lateral con 3 tabs:
- *Perfil*: rol editable, capacidades, disparadores de routing (editables), datos de entrada, autonomy ladder
- *Aprendizaje*: resumen de qué sabe, patrones aprobados, gold samples asociados, KB que usa
- *Skills*: skills asignados con toggle + catálogo para agregar nuevos (admin only)

**Autonomy Ladder** (dentro del perfil del agente): 4 pasos — Nivel 0: Propone siempre | Nivel 1: Ejecuta bajo impacto (10 outputs sin edición) | Nivel 2: Auto + notificación (25 outputs + 30 días) | Nivel 3: Auto + excepciones (50 outputs + activado por CEO). Visualizado como barra horizontal con progress bar hacia el siguiente nivel.

**Centro de Conexiones** — nav item en sidebar. 3 secciones con cards:
- *Canales*: Gmail (conectado), WhatsApp Business (QR setup), Slack, Telegram
- *Flujos*: n8n (conectado, 2 flujos activos), Webhook genérico (activo), Make, Zapier
- *CRM y datos*: Google Sheets, HubSpot
Click en card → right panel con stats de actividad, config, URLs de webhook para copiar, o flujo de setup.

**Configuración** — General / Skills / Integraciones / Organización.

---

## QUÉ REVISAR — PREGUNTAS GUÍA

Respondé cada una con observaciones concretas si encontrás un problema, o confirmá si está bien resuelto:

1. **Onboarding y primer uso**: ¿Un usuario nuevo que nunca usó FaberLoom sabe por dónde empezar? ¿Hay un flujo claro de "primer paso"?

2. **Flujo de aprobación de drafts**: ¿Es claro en todo momento qué está pendiente de aprobación? ¿Puede el usuario perder un draft sin darse cuenta?

3. **Modelo de agentes**: ¿La metáfora de "trabajador especializado" es comprensible para un no-técnico? ¿El flujo card → consola es intuitivo? ¿El tab Flujos es demasiado técnico para el usuario objetivo?

4. **Aprendizaje acumulado**: ¿Queda claro cómo el sistema aprende? ¿El usuario entiende la diferencia entre Patrón y Gold Sample? ¿Sabe cuándo y cómo indexar aprendizaje?

5. **Autonomy Ladder**: ¿La metáfora de "confianza ganada" es comprensible? ¿Los requisitos para subir de nivel son creíbles para el usuario? ¿El riesgo de darle más autonomía al agente está suficientemente claro?

6. **Centro de Conexiones**: ¿Un dueño de PYME entiende qué hace cada integración? ¿El flujo de conectar WhatsApp (QR) es suficientemente guiado? ¿Es obvio qué pasa con los datos cuando conectás?

7. **Navegación general**: ¿El sidebar comunica bien la jerarquía de funciones? ¿Hay vistas que deberían estar más o menos accesibles? ¿El right panel siempre aporta contexto útil o a veces estorba?

8. **Confianza y control**: ¿El usuario siente en todo momento que tiene el control? ¿Hay algún punto donde el sistema parece actuar solo sin que quede claro? ¿El statusbar ("FaberLoom nunca actúa sin permiso") es suficiente o hay que reforzarlo en más puntos?

9. **Gaps funcionales evidentes**: ¿Hay alguna acción obvia que un usuario querría hacer y que no está disponible en ninguna vista?

10. **Simplicidad vs. potencia**: ¿Hay alguna vista o tab que esté sobrediseñada para el usuario objetivo (dueño de PYME no técnico)? ¿Qué simplificarías sin perder funcionalidad real?

---

## RESTRICCIONES — NO SUGERIR

- No sugerir cambios de colores, tipografía o espaciado — el diseño visual es intencional y está bloqueado.
- No sugerir eliminar la doctrina draft-first — es el núcleo del producto.
- No sugerir simplificar los agentes a chatbots genéricos — la especialización es el diferenciador.
- No sugerir cambios de precio o modelo de negocio.
- No inventar features que no tengan relación con el problema operativo del usuario objetivo.

---

## OUTPUT ESPERADO

1. Lista de observaciones en el formato definido arriba, ordenadas por prioridad.
2. Al final: top 3 ajustes que tendrían el mayor impacto en la experiencia del primer usuario.
3. Una pregunta que te quedó sin responder sobre el producto y que, de responderla, cambiaría tus recomendaciones.
