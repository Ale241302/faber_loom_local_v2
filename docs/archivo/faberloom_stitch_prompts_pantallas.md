# FABERLOOM — 22 PROMPTS INDIVIDUALES PARA STITCH
**Un prompt = una pantalla. Pegar uno por uno.**

---

## BLOQUE SHELL (embebido en cada prompt — no modificar)

```
SHELL FIJO — idéntico en los 22 frames

Topbar: fondo #1E293B · borde inferior #334155
- Izquierda: punto pequeño #4338CA + "FABERLOOM" SemiBold 14px
- Centro: nombre de la vista activa como tab, subrayado 2px #4338CA
- Derecha: ícono notificaciones · ícono configuración · avatar circular

Sidebar izquierdo: fondo #1E293B · borde derecho #334155 · labels visibles
  ─ NAVEGACIÓN ──────────────────
    Consola
    Comunicaciones
    Conocimiento
    Outputs
    Skills
    ──────────────────
    Configuración
  ─ SESIÓN ACTUAL ───────────────
  ● Respuesta Ramírez #4421
    Reactivación B2B Arkano
  ─ AYER ────────────────────────
    Propuesta Constructoras
  ──────────────────────────────
  [avatar] Javier M. · javier@faberloom.io

Ítem activo en sidebar: borde izquierdo 2px #4338CA + fondo #263348 + texto #F1F5F9
Ítems inactivos: sin fondo · texto #94A3B8

Statusbar: fondo #263348 · borde superior #334155 · JetBrains Mono 10.5px · color #475569
● Listener activo  |  KB: Pedidos activos  |  Voz: Perfil personal  |  Draft · no enviado · FaberLoom nunca actúa sin permiso

Sistema de color:
#0F172A fondo principal · #1E293B superficie · #263348 elevado · #334155 borde
#F1F5F9 texto principal · #94A3B8 texto secundario · #475569 texto muted
#4338CA primary · #6366F1 draft · #16A34A aprobado · #0284C7 email · #D97706 alta urgencia · #DC2626 error

Tipografía: Inter para UI · JetBrains Mono para metadata, trust layers y statusbar
Sin gradientes · Sin emojis decorativos · Sin burbujas redondas estilo iMessage
```

---

## COPY 1 — Consola vacía (shell base)

```
Diseña el shell desktop de FaberLoom. Desktop-first, mínimo 1280px, pantalla completa.

[PEGAR BLOQUE SHELL]

Área central: fondo #0F172A · completamente vacía · sin contenido ni placeholder
El ítem activo en sidebar es "Consola"

Input bar fijo en la parte inferior del área central:
┌──────────────────────────────────────────────────────────┐
│ [ Skill: Respuesta comercial × ]  Escribe tu consulta... ▶ │
└──────────────────────────────────────────────────────────┘
Escribe / para activar un skill · Enter para enviar

Tag de skill: fondo #6366F1 al 15% + borde #6366F1 al 40% + texto #6366F1
Botón ▶: fondo #4338CA
Hint debajo: texto #475569 10.5px

Panel derecho: fondo #1E293B · borde izquierdo #334155 · siempre visible

3 tabs en la parte superior del panel:
[ Skill activo ]  [ Contexto ]  [ Fuentes ]
Tab activo: texto #F1F5F9 + borde inferior 2px #4338CA
Tab inactivo: texto #475569

Tab "Skill activo" activo — contenido:
RESPUESTA COMERCIAL               v1.4
Configurado por: Javier · 10 abr

── Instrucción activa ──────────
Al redactar respuestas a clientes
comerciales, mantener tono profesional
pero cercano...

── Patrones aprendidos ─────────
✓ Saludo sin "Estimado" — 8 veces
✓ Cierre con nombre — 12 veces
⚠ Longitud >3 párrafos — rechazado 3×

── Historial de ajustes ────────
v1.4 · "Tono más directo" · 10 abr
v1.3 · "Ajuste saludo" · 03 mar
```

---

## COPY 2 — Consola · Momento A (señal activa en contexto)

```
Diseña la consola de FaberLoom con una señal activa visible en el panel de contexto.

[PEGAR BLOQUE SHELL]

Área central: fondo #0F172A · vacía · sin mensajes
El ítem activo en sidebar es "Consola"

Input bar igual que Copy 1.

Panel derecho: tab "Contexto" activo

── Contexto activo ─────────────────
● KB: Pedidos activos
● Voz: Perfil personal activo

── Comunicaciones ──────────────────
● Distribuidora Ramírez · pedido #4421
  hace 3h · sin respuesta · ALTA URGENCIA
  [ Atender → ]

○ Inversiones Delta · consulta renovación
  hace 5h · MEDIA URGENCIA

── Patrones aprobados: 8 ───────────
── Señales activas: 2 ──────────────

La señal de Ramírez tiene borde izquierdo #D97706 y badge "ALTA URGENCIA" en texto #D97706.
La señal de Delta tiene borde #0284C7 y badge "MEDIA URGENCIA" en texto #0284C7.
El botón [ Atender → ] en texto #4338CA.
```

---

## COPY 3 — Consola · Momento B (draft propuesto, Estado 2)

```
Diseña la consola de FaberLoom en el momento en que el sistema ha generado un draft.

[PEGAR BLOQUE SHELL]

Área central: fondo #0F172A · ítem activo en sidebar "Consola"

Mensaje del usuario (alineado a la derecha):
Fondo rectangular #263348 · sin burbuja · sin cola · texto "Responde esto"

Card de draft debajo del mensaje:
┌─ ● Draft · no enviado ──────────────────────── [Editar] ─┐
│  ← borde izquierdo 2px #6366F1 · fondo #1E293B            │
│                                                             │
│  Estimado equipo de Distribuidora Ramírez,                 │
│                                                             │
│  Confirmamos que el pedido #4421 ha sido procesado         │
│  exitosamente. El envío sale mañana a primera hora.        │
│                                                             │
│  Quedamos a su disposición.                                │
│                                                             │
│  Javier M.                                                 │
│  Gestión Operativa                                         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Basado en: 2 outputs similares aprobados ·                │
│  Voz: perfil personal activo · KB: pedidos activos         │
│  [JetBrains Mono 10px #475569]                             │
├─────────────────────────────────────────────────────────────┤
│  [ Rechazar ]      [ Editar ]               [ Aprobar ]    │
└─────────────────────────────────────────────────────────────┘

Badge "● Draft · no enviado": color #6366F1 · JetBrains Mono
Botón "Aprobar": fondo #4338CA · alineado a la derecha
Botones "Rechazar" y "Editar": sin color de acento · texto secundario

Panel derecho: tab "Skill activo" activo — muestra el skill Respuesta Comercial v1.4 con instrucción activa y patrones aprendidos (igual que Copy 1).
```

---

## COPY 4 — Consola · Momento C (post-aprobación silenciosa)

```
Diseña la consola de FaberLoom después de que el usuario aprobó el draft.
Es el mismo frame que Copy 3 con 4 cambios únicamente.

[PEGAR BLOQUE SHELL]

Área central: igual que Copy 3. El card de draft con estos cambios:

1. Borde izquierdo: cambia de #6366F1 a #16A34A
2. Badge: cambia a "✓ Aprobado" en color #16A34A · JetBrains Mono
3. Los 3 botones (Rechazar, Editar, Aprobar) desaparecen completamente
4. Al pie del card aparece una línea:
   Patrón registrado silenciosamente.
   [JetBrains Mono · #475569 · sin acento]

No hay modal · no hay notificación · no hay toast · no hay animación de celebración.
El panel derecho no cambia — igual que Copy 3.
```

---

## COPY 5 — Comunicaciones · lista

```
Diseña la vista Comunicaciones de FaberLoom. Lista priorizada de emails operativos.
No es un inbox. No hay threading. No muestra correos completos.

[PEGAR BLOQUE SHELL]

Ítem activo en sidebar: "Comunicaciones"

Header del área central:
COMUNICACIONES
Operativas    [ Filtrar... ]
Estado: ● LISTENER ACTIVO · GMAIL CONECTADO

Tabs de categoría:
[ ALTA URGENCIA: 2 ]   [ MEDIA URGENCIA: 3 ]   [ REVISADAS ]

Cards de email — de arriba hacia abajo:

┌─ [ALTA URGENCIA] ─────────────────────── hace 5.4h ─┐
│  Distribuidora Ramírez                                │
│  Pedido #4421 — solicitud de confirmación de entrega  │
│  ACCIÓN SUGERIDA: Confirmar fecha de despacho        │
│                                      [ ATENDER ]     │
└──────────────────────────────────────────────────────┘

┌─ [MEDIA URGENCIA] ────────────────────── hace 3.8h ─┐
│  Inversiones Delta                                    │
│  Aclaración sobre términos de renovación Q4          │
│  ACCIÓN SUGERIDA: Generar borrador de respuesta      │
│                                      [ REVISAR ]     │
└──────────────────────────────────────────────────────┘

┌─ [SIN PRIORIDAD] ─────────────────────── hace 1.2h ─┐
│  Constructoras Alfa                                   │
│  Solicitud de propuesta para auditoría Q3            │
│  ACCIÓN SUGERIDA: Asignar a skill Propuesta          │
│                                      [ REVISAR ]     │
└──────────────────────────────────────────────────────┘

ALTA URGENCIA: borde izq #D97706 + badge #D97706
MEDIA URGENCIA: borde izq #0284C7 + badge #0284C7
SIN PRIORIDAD: borde izq #334155 + badge #475569

Panel derecho: vacío con texto muted "Selecciona una comunicación"
```

---

## COPY 6 — Comunicaciones · email seleccionado (detalle)

```
Diseña la vista Comunicaciones con un email seleccionado y su detalle en el panel derecho.

[PEGAR BLOQUE SHELL]

Ítem activo en sidebar: "Comunicaciones"
Área central: igual que Copy 5. El card de Ramírez aparece resaltado (fondo #263348).

Panel derecho — detalle del email seleccionado:

DETALLE DE COMUNICACIÓN

Distribuidora Ramírez
Canal: Gmail · ops@ramirez.com
Recibido: hace 5.4h

── Contenido del email ──────────────
Hola Javier, necesitamos confirmar
la entrega del pedido #4421 para
esta semana. El cliente final ya
está preguntando. ¿Podés confirmar?

⚠ A 2 horas excederá umbral SLA.

── Contexto relacionado en KB ───────
📄 Protocolo de Pedidos Activos
  Procedimiento para confirmación...
📄 Historial Ramírez Q3
  3 pedidos previos · sin incidencias

── Historial de esta cuenta ─────────
Pedido #4389 · 15 mar · entregado
Pedido #4401 · 02 abr · entregado

── Draft sugerido ────────────────────
[Vista previa primeras 2 líneas...]
● Draft · no enviado

[ ABRIR EN CONSOLA CON DRAFT ]
[ EXTRAER APRENDIZAJE          ]
[ IGNORAR                      ]

"ABRIR EN CONSOLA CON DRAFT": fondo #4338CA
"EXTRAER APRENDIZAJE": borde #334155 · texto #94A3B8
"IGNORAR": texto #475569 sin acento
```

---

## COPY 7 — Comunicaciones · chat contextual + upload

```
Diseña la vista Comunicaciones con el panel de chat contextual activo dentro del detalle del email.

[PEGAR BLOQUE SHELL]

Ítem activo en sidebar: "Comunicaciones"
Área central: igual que Copy 5 con el card de Ramírez resaltado.

Panel derecho — dividido en dos secciones:

SECCIÓN SUPERIOR (60% del panel):
Mismo contenido del email que Copy 6 (remitente, contenido, contexto KB).

SECCIÓN INFERIOR (40% del panel) — chat contextual:
──────────────────────────────────────
CONTEXTO DE RESPUESTA

[mensaje del sistema, alineado izq, fondo #0F172A]:
Tengo contexto de 3 pedidos previos.
¿Querés que ajuste el tono o los datos?

[mensaje del usuario, alineado derecha, fondo #263348]:
Agregá la fecha exacta del pedido anterior

[mensaje del sistema]:
Entendido. Draft actualizado con fecha
del pedido #4389 (15 mar).

──────────────────────────────────────
[ 📎 Subir archivo ] [ Escribe aquí... ] [▶]

Botón 📎: sin acento · texto #94A3B8
Input de texto: fondo #0F172A · sin borde propio
Botón ▶: fondo #4338CA

[ EXTRAER APRENDIZAJE DE ESTE CONTEXTO ]
Botón secundario debajo del input · borde #334155 · texto #94A3B8
```

---

## COPY 8 — Conocimiento · lista de recursos

```
Diseña la vista Conocimiento de FaberLoom. Repositorio de recursos de contexto en 3 capas.
No wiki. No árbol de carpetas.

[PEGAR BLOQUE SHELL]

Ítem activo en sidebar: "Conocimiento"

Header:
CONOCIMIENTO
[ Explorar ]  [ Recientes ]  [ Borradores ]  [ 🔍 Búsqueda semántica ]

3 cards de capa en la parte superior:
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  Personal        │  │  Rol             │  │  Organización    │
│  148 recursos    │  │  52 recursos     │  │  89 recursos     │
│  Contexto        │  │  Protocolos de   │  │  Directrices     │
│  individual y    │  │  función y       │  │  corporativas    │
│  preferencias    │  │  responsabilidad │  │  y visión        │
└──────────────────┘  └──────────────────┘  └──────────────────┘

Card seleccionado (Personal): borde #4338CA + fondo #263348
Cards no seleccionados: borde #334155 + fondo #1E293B

Botón de acción flotante arriba a la derecha:
[ + Añadir recurso ]  fondo #4338CA

Lista de recursos debajo:
NOMBRE                        FECHA          ACTUALIZADO    ESTADO
─────────────────────────────────────────────────────────────────
📄 Preferencias de respuesta  Reciente       35ms ago       Activo
📄 Historial clientes Q1      14 ene 2025    07:18 ago      Activo
📄 Manual de operaciones       13 may 2024   2d ago         Activo

Cada fila tiene al extremo derecho: ícono de borrar (🗑) en #475569 — visible en hover.

Panel derecho: vacío con texto muted "Selecciona un recurso"
```

---

## COPY 9 — Conocimiento · recurso seleccionado

```
Diseña la vista Conocimiento con un recurso seleccionado y su detalle en el panel derecho.

[PEGAR BLOQUE SHELL]

Ítem activo en sidebar: "Conocimiento"
Área central: igual que Copy 8. La fila "Preferencias de respuesta" resaltada.

Panel derecho:

PREFERENCIAS DE RESPUESTA
Capa: Personal · v2.1
Añadido por: Javier · 14 oct 2025
Estado: ● Indexado · activo en vector store

── Contenido completo ───────────────
Al responder a clientes, evitar
el uso de "Estimado". Preferir
saludo por nombre cuando se conoce.
Cierre siempre con nombre propio...
[scrolleable]

── Usado en ─────────────────────────
8 outputs aprobados usaron este recurso.
Patrón detectado: tono más directo.

── Historial de versiones ───────────
v2.1 · "Ajuste saludo" · 14 oct
v2.0 · "Añadido cierre" · 03 sep
v1.0 · "Versión inicial" · 15 ene

[ EDITAR DOCUMENTO  ]
[ ELIMINAR RECURSO  ]

"EDITAR DOCUMENTO": borde #334155 · texto #94A3B8
"ELIMINAR RECURSO": texto #DC2626 sin fondo · pequeño · al pie
```

---

## COPY 10 — Conocimiento · subiendo e indexando

```
Diseña la vista Conocimiento en el momento en que un recurso está siendo subido e indexado.

[PEGAR BLOQUE SHELL]

Ítem activo en sidebar: "Conocimiento"
Área central: igual que Copy 8.

En la parte superior del área central, debajo del header, aparece una barra de proceso:

┌────────────────────────────────────────────────────────────┐
│  ⟳ Indexando: "Contrato Marco Ramírez.pdf"                 │
│  Descomponiendo en fragmentos · Vectorizando · 67%         │
│  ████████████░░░░░░                                        │
└────────────────────────────────────────────────────────────┘

El color de la barra de progreso es #4338CA.
El texto "Indexando" en JetBrains Mono #94A3B8.
El porcentaje 67% en #F1F5F9.

Cuando termine, la barra desaparece y el recurso aparece en la lista con badge "Activo".
(Mostrar el estado intermedio: 67% en progreso.)

Panel derecho: vacío durante la indexación con texto muted "Indexando recurso..."
```

---

## COPY 11 — Conocimiento · edición inline

```
Diseña la vista Conocimiento con un recurso en modo edición inline en el panel derecho.

[PEGAR BLOQUE SHELL]

Ítem activo en sidebar: "Conocimiento"
Área central: igual que Copy 8. La fila "Preferencias de respuesta" resaltada.

Panel derecho — modo edición:

EDITANDO: PREFERENCIAS DE RESPUESTA
Capa: Personal · v2.1 → guardará como v2.2

── Editor ────────────────────────────
┌─────────────────────────────────────┐
│ Al responder a clientes, evitar     │
│ el uso de "Estimado". Preferir      │
│ saludo por nombre cuando se conoce. │
│ Cierre siempre con nombre propio... │
│                                     │
│ [cursor activo visible]             │
└─────────────────────────────────────┘
Fondo del editor: #0F172A · borde #334155 · texto #F1F5F9

[ GUARDAR CAMBIO ]    [ CANCELAR ]

"GUARDAR CAMBIO": fondo #4338CA
"CANCELAR": texto #475569 sin acento

Nota debajo en JetBrains Mono #475569:
Guardar actualizará el vector store automáticamente.
```

---

## COPY 12 — Outputs · lista

```
Diseña la vista Outputs Aprobados de FaberLoom. Repositorio de aprendizaje operativo.
No dashboard. Sin métricas globales. Sin gráficos.

[PEGAR BLOQUE SHELL]

Ítem activo en sidebar: "Outputs"

Header:
OUTPUTS APROBADOS
Repositorio Operacional

Filtros en una línea:
[ Todos los skills ▾ ]  [ mm/dd/yyyy ]  [ Contacto... ]  [ Todos los estados ▾ ]

Cards de output — uno por fila:

┌──────────────────────────────────── [PATRÓN APRENDIDO ✓] ─┐
│  Respuesta Comercial · Distribuidora Ramírez · pedido #4421 │
│  Aprobado por: Javier · hace 3 días                         │
│  Cambios: saludo, fecha de entrega                          │
└──────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────── [SIN PATRÓN] ──┐
│  Análisis Estratégico · Constructoras Alfa · Auditoría Q3   │
│  Aprobado por: Elena · hace 5 días                          │
│  Cambios: estructura, datos financieros                     │
└──────────────────────────────────────────────────────────────┘

Badge "PATRÓN APRENDIDO": #16A34A
Badge "SIN PATRÓN": #475569

Cada card tiene al extremo derecho ícono de borrar 🗑 en #475569, visible en hover.

Panel derecho: vacío con texto muted "Selecciona un output"
```

---

## COPY 13 — Outputs · output seleccionado (diff view)

```
Diseña la vista Outputs con un output seleccionado y el diff en el panel derecho.

[PEGAR BLOQUE SHELL]

Ítem activo en sidebar: "Outputs"
Área central: igual que Copy 12. El primer card resaltado.

Panel derecho:

DETALLE DE APRENDIZAJE
Distribuidora Ramírez · 14 oct 2025
Skill: Respuesta Comercial

── Draft original ───────────────────
"Estimado equipo de Distribuidora
Ramírez, confirmamos la recepción del
pedido #4421. La fecha estimada de
entrega es el 28 de octubre..."

                  ↓

── Versión aprobada ─────────────────
"Hola equipo Ramírez, confirmamos que
el pedido #4421 ya fue procesado.
La entrega sale mañana."

── Qué cambió ───────────────────────
Saludo:    "Estimado" → "Hola equipo"   [estilo]
Fecha:     genérica → específica        [contenido]
Longitud:  reducida significativamente  [estilo]

── Estado de aprendizaje ────────────
✓ PATRÓN DETECTADO
El sistema identificó este cambio
como patrón en respuestas comerciales.

[ Marcar como excepción ]
─────────────────────────────────────
¿La instrucción necesita ajuste?
[ Ajustar instrucción del skill → ]
─────────────────────────────────────
[ Eliminar output ]
"Eliminar output": texto #DC2626 · pequeño · sin fondo
```

---

## COPY 14 — Outputs · ajustar instrucción del skill (editor inline)

```
Diseña la vista Outputs con el panel derecho convertido en editor de instrucción del skill.
El usuario hizo click en "Ajustar instrucción del skill" desde Copy 13.

[PEGAR BLOQUE SHELL]

Ítem activo en sidebar: "Outputs"
Área central: igual que Copy 12.

Panel derecho — transformado en editor:

EDITANDO INSTRUCCIÓN DEL SKILL
Skill: Respuesta Comercial · v1.4 → guardará como v1.5
Desde: Output · Distribuidora Ramírez · 14 oct

── Instrucción actual ────────────────
┌─────────────────────────────────────┐
│ Al redactar respuestas comerciales, │
│ mantener tono profesional pero      │
│ cercano. Evitar "Estimado". Usar    │
│ saludo por nombre cuando disponible │
│ [cursor activo]                     │
└─────────────────────────────────────┘
Fondo #0F172A · borde #334155

[ GUARDAR Y SUBIR VERSIÓN ]    [ CANCELAR ]

"GUARDAR Y SUBIR VERSIÓN": fondo #4338CA
"CANCELAR": texto #475569

Nota al pie en JetBrains Mono #475569:
v1.5 · cambio vinculado a output #4421
```

---

## COPY 15 — Skills · lista

```
Diseña la vista Skills de FaberLoom. Lista de skills configurados por el usuario.

[PEGAR BLOQUE SHELL]

Ítem activo en sidebar: "Skills"

Header:
SKILLS
Instrucciones configuradas por vos

Botón arriba a la derecha: [ + Nuevo skill ]  fondo #4338CA

Lista de skills:

┌────────────────────────────────────────────────────────────┐
│  Respuesta Comercial              v1.4 · Activo             │
│  Configurado por: Javier · 10 abr                           │
│  8 patrones aprendidos · usado 34 veces                     │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  Análisis Estratégico             v1.1 · Activo             │
│  Configurado por: Elena · 22 mar                            │
│  2 patrones aprendidos · usado 12 veces                     │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  Propuesta de Servicios           v1.0 · Activo             │
│  Configurado por: Javier · 15 ene                           │
│  Sin patrones aún · usado 3 veces                           │
└────────────────────────────────────────────────────────────┘

Panel derecho: vacío con texto muted "Selecciona un skill"
```

---

## COPY 16 — Skills · detalle de skill

```
Diseña la vista Skills con un skill seleccionado y su detalle en el panel derecho.

[PEGAR BLOQUE SHELL]

Ítem activo en sidebar: "Skills"
Área central: igual que Copy 15. El primer skill resaltado.

Panel derecho:

RESPUESTA COMERCIAL
v1.4 · Activo · configurado por Javier

── Instrucción activa ──────────────
Al redactar respuestas a clientes
comerciales, mantener tono profesional
pero cercano. Evitar "Estimado".
Confirmar datos del pedido antes de
comprometerse a fechas.

── Recursos vinculados ─────────────
📄 Preferencias de respuesta
📄 Historial clientes Q1
📄 Protocolo de pedidos activos

── Patrones aprendidos ─────────────
✓ Saludo sin "Estimado" — 8 veces
✓ Cierre con nombre propio — 12 veces
⚠ Longitud >3 párrafos — rechazado 3×

── Historial de instrucción ─────────
v1.4 · "Tono más directo" · 10 abr
v1.3 · "Ajuste saludo" · 03 mar
v1.2 · "Confirmación de datos" · 15 ene
v1.1 · "Primera revisión" · 03 ene
v1.0 · "Versión inicial" · 15 dic

[ EDITAR INSTRUCCIÓN ]
[ DESACTIVAR SKILL   ]

"EDITAR INSTRUCCIÓN": borde #334155 · texto #94A3B8
"DESACTIVAR SKILL": texto #475569 sin acento
```

---

## COPY 17 — Voz del cliente · perfil y ejemplos

```
Diseña la vista de Voz del cliente en FaberLoom. Muestra los ejemplos de voz detectada de un cliente.
Esta vista se abre al hacer click en el nombre del cliente desde un output o comunicación.

[PEGAR BLOQUE SHELL]

Ítem activo en sidebar: "Conocimiento" (la voz vive dentro del conocimiento personal)
Tab activo en el área central: [ Voz ]

Header:
VOZ DETECTADA
Distribuidora Ramírez
Aprendida desde: 12 outputs aprobados · actualizada hace 3 días

Área central dividida en dos columnas:

COLUMNA IZQUIERDA — Ejemplos con voz:
── Cómo respondería CON esta voz ────
"Hola equipo Ramírez, el pedido #4421
ya salió. La entrega es mañana.
Cualquier duda, escribinos."

"Perfecto Marcos, confirmado para
el jueves. Te mando el tracking
en cuanto esté disponible."

COLUMNA DERECHA — Sin voz (baseline):
── Cómo respondería SIN esta voz ────
"Estimado equipo de Distribuidora
Ramírez, confirmamos el despacho del
pedido #4421 programado para el día
de mañana. Atentamente."

"Estimado Marcos, confirmamos la
fecha de entrega para el jueves
próximo. Quedamos a disposición."

Diferencias detectadas debajo de ambas columnas:
Tono:     Formal → Directo y cercano
Saludo:   "Estimado" → nombre propio
Cierre:   Protocolar → Natural

Panel derecho:
[ Probar esta voz → ]  fondo #4338CA
```

---

## COPY 18 — Voz del cliente · consola de prueba

```
Diseña la consola de prueba de voz en FaberLoom. El usuario puede probar cómo sonaría
una respuesta con y sin la voz del cliente antes de usarla en producción.

[PEGAR BLOQUE SHELL]

Ítem activo en sidebar: "Conocimiento"

Header del área central:
CONSOLA DE VOZ
Probando: Distribuidora Ramírez
Voz activa: ● ON

Área central — dos paneles lado a lado:

PANEL IZQUIERDO (input):
Escribe un mensaje o contexto para probar:
┌─────────────────────────────────────┐
│ Confirmar entrega del pedido #4421  │
│ para esta semana.                   │
│                                     │
└─────────────────────────────────────┘
[ GENERAR COMPARACIÓN ]  fondo #4338CA

PANEL DERECHO (output — aparece después de generar):
── CON voz Ramírez ──────────────────
"Hola equipo, confirmado para el
jueves. Les aviso cuando salga."

── SIN voz (baseline) ───────────────
"Estimado equipo, confirmamos la
entrega para el jueves próximo."

Toggle en la parte superior del panel derecho:
[ CON VOZ ●━━━━━━━━━━ SIN VOZ ]

Panel derecho de la app (sidebar derecho habitual):
Muestra el perfil de voz de Ramírez con los patrones detectados.
```

---

## COPY 19 — Configuración · conectar Gmail

```
Diseña la pantalla de conexión de Gmail en FaberLoom. Es el primer paso del onboarding.

[PEGAR BLOQUE SHELL]

Ítem activo en sidebar: "Configuración"
Sub-ítem activo: "Integraciones"

Área central — centrada verticalmente:

CONECTAR CORREO ELECTRÓNICO
Para que FaberLoom pueda detectar comunicaciones
operativas, necesita acceso a tu Gmail.

┌────────────────────────────────────────────────────────────┐
│                                                             │
│  Gmail                                                      │
│  javier@faberloom.io                                           │
│                                                             │
│  FaberLoom solo lee. Nunca envía por su cuenta.               │
│  Podés revocar el acceso en cualquier momento.              │
│                                                             │
│                    [ CONECTAR CON GOOGLE ]                  │
│                                                             │
└────────────────────────────────────────────────────────────┘

Botón "CONECTAR CON GOOGLE": fondo #4338CA · ancho completo del card

Debajo del card, texto pequeño en JetBrains Mono #475569:
FaberLoom nunca actúa sin permiso. El listener solo lee y clasifica.

Estado post-conexión (mostrar como segundo frame opcional):
● Gmail conectado · javier@faberloom.io
Listener activo desde hace 2 min · 3 comunicaciones detectadas
[ Ir a Comunicaciones → ]

Panel derecho: vacío durante la conexión
```

---

## COPY 20 — Configuración · general

```
Diseña la pantalla de Configuración general de FaberLoom.

[PEGAR BLOQUE SHELL]

Ítem activo en sidebar: "Configuración"

Navegación interna (tabs horizontales en el área central):
[ General ]  [ Skills ]  [ Integraciones ]  [ Organización ]
Tab activo "General": subrayado 2px #4338CA

Área central — secciones apiladas:

── Perfil ───────────────────────────
Nombre: Javier M.
Email: javier@faberloom.io
Rol: Operaciones
[ Editar perfil ]

── Voz personal ─────────────────────
Estado: ● Activa · aprendida desde 34 outputs
Última actualización: hace 3 días
[ Ver mi voz → ]

── Preferencias de respuesta ────────
Idioma: Español
Tono base: Profesional-cercano
Longitud preferida: Respuestas cortas
[ Editar preferencias ]

── Organización ─────────────────────
FaberLoom Demo S.A.
Plan: Profesional · $199/mes
[ Ver plan ]

Panel derecho: vacío
```

---

## COPY 21 — Configuración · Skills (lista editable)

```
Diseña la pantalla de Configuración de Skills — vista compacta de gestión.

[PEGAR BLOQUE SHELL]

Ítem activo en sidebar: "Configuración"
Tab activo en área central: "Skills"

Lista de skills con controles de gestión:

NOMBRE                    VERSIÓN    ESTADO      USO
──────────────────────────────────────────────────────
Respuesta Comercial       v1.4       ● Activo    34×
Análisis Estratégico      v1.1       ● Activo    12×
Propuesta de Servicios    v1.0       ● Activo     3×

Cada fila tiene al extremo derecho:
[ Editar ]  [ ··· ]
"Editar" en texto #4338CA · "···" muestra opciones: duplicar, desactivar, eliminar

Botón al pie de la lista:
[ + Crear nuevo skill ]  fondo #4338CA

Panel derecho: vacío
```

---

## COPY 22 — Estado vacío · primera vez (onboarding)

```
Diseña el estado inicial de FaberLoom cuando el usuario aún no tiene datos.
Es la pantalla que ve alguien que acaba de crear su cuenta.

[PEGAR BLOQUE SHELL]

Ítem activo en sidebar: "Consola"

Área central — centrada vertical y horizontalmente:

FABERLOOM
punto #4338CA

Tu memoria operativa está vacía.
Empezá conectando tu correo.
[texto #94A3B8]

┌────────────────────────────────┐
│  1. Conectar Gmail             │
│     → Detectar comunicaciones  │
├────────────────────────────────┤
│  2. Crear tu primer skill      │
│     → Definir cómo responder   │
├────────────────────────────────┤
│  3. Aprobar tu primer draft    │
│     → Empezar a aprender       │
└────────────────────────────────┘

[ CONECTAR GMAIL ]  fondo #4338CA

Texto al pie en JetBrains Mono #475569:
FaberLoom nunca actúa solo. Vos decidís siempre.

Panel derecho: vacío · sin tabs visibles
```
