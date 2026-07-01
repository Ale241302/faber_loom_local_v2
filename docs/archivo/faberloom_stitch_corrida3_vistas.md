# FABERLOOM — CORRIDA 3: VISTAS SECUNDARIAS
**Para pegar directo en Stitch · Requiere haber ejecutado Corridas 1 y 2 primero**

---

Toma el shell y el color system de las corridas anteriores y diseña las 3 vistas secundarias de FaberLoom.

**Lo que debes diseñar: 3 vistas distintas, cada una con su área principal y su panel derecho. Mismo shell, misma identidad visual.**

---

## Contexto del producto

FaberLoom es Operational Memory para PYMEs. El conocimiento vive en KB gobernada. Las señales vienen del email. Los outputs son el historial de aprendizaje. Estas 3 vistas son las superficies de gestión — no de conversación.

---

## Vista A — Señales

### Propósito
Lista priorizada de señales operativas extraídas del email. **No es un inbox. No tiene threading. No muestra correos completos.**

### Área principal

Header:
```
SEÑALES
Operativas    [ Filtrar señales... ]

Estado: ● LISTENER ACTIVO · EMAIL PROCESADO
```

Tabs de categoría:
```
[ ALTA URGENCIA: 2 ]   [ MEDIA URGENCIA: 3 ]   [ REVISADAS ]
```

Cards de señal — uno por señal, de arriba hacia abajo:

```
┌─ [ALTA URGENCIA] ───────────────────── hace 5.4h sin respuesta ─┐
│  Logística Global S.A.                                            │
│  Retraso crítico en despacho aduanero — Sector Norte             │
│  ACCIÓN SUGERIDA: Escalar a Gerencia de Operaciones              │
│                                              [ ATENDER AHORA ]   │
└──────────────────────────────────────────────────────────────────┘

┌─ [MEDIA URGENCIA] ──────────────────── hace 3.8h sin respuesta ─┐
│  Inversiones Delta                                               │
│  Solicitud de aclaración sobre términos de renovación            │
│  ACCIÓN SUGERIDA: Generar borrador de respuesta técnica          │
│                                              [ REVISAR ]         │
└──────────────────────────────────────────────────────────────────┘
```

Tratamiento visual de urgencia:
- `ALTA URGENCIA`: borde izquierdo del card en `#D97706` + badge texto `#D97706`
- `MEDIA URGENCIA`: borde izquierdo del card en `#0284C7` + badge texto `#0284C7`
- `SIN PATRÓN`: borde en `#334155` + badge texto `#475569`

### Panel derecho — al seleccionar una señal

```
DETALLE DE SEÑAL

Logística Global S.A.
Canal: SMTP/TLS · Email corporativo
Email: ops@lgint.com

── Señal ────────────────────────────
Se detecta un retraso crítico en el
despacho aduanero del Sector Norte.
El sistema enviado 3 alertas internas
sin obtener respuesta.

⚠ A 4 horas excederá umbral SLA.

── Contexto relacionado en KB ───────
Protocolo de Escalada Nivel 4
  Procedimiento para incidencias críticas...

── Historial de incidencias ─────────
Incidencia #422 · 25/02
Retraso Aduana Valencia · 25/01

── Draft sugerido ───────────────────
[Vista previa de las primeras 2 líneas]
● Draft · no enviado

[ ABRIR EN CONSOLA CON DRAFT ]
[ IGNORAR SEÑAL               ]
```

"ABRIR EN CONSOLA CON DRAFT" en `#4338CA`. "IGNORAR SEÑAL" en texto secundario sin acento.

---

## Vista B — Conocimiento

### Propósito
Repositorio de KB en 3 capas. **No wiki. No árbol de carpetas. La búsqueda semántica es la entrada principal.**

### Área principal

Header con tabs:
```
CONOCIMIENTO

[ Explorar ]  [ Recientes ]  [ Borradores ]  [ 🔍 Búsqueda semántica ]
```

3 cards de capa en la parte superior:

```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  Personal        │  │  Rol             │  │  Organización    │
│  148 entradas    │  │  52 entradas     │  │  89 entradas     │
│                  │  │                  │  │                  │
│  Contexto        │  │  Protocolos de   │  │  Directrices     │
│  individual y    │  │  función y       │  │  corporativas    │
│  preferencias    │  │  responsabilidad │  │  y visión        │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

Card seleccionado: borde `#4338CA` + fondo `#263348`.

Lista de entradas debajo de los cards:
```
TÍTULO DEL ACTIVO             FECHA          ACTUALIZADO   APROBADO
──────────────────────────────────────────────────────────────────
📄 Protocolo Escalada Nivel 4  26 JUL 2025   31ms ago      A. Villarreal
📄 Directiva Seguridad 2024    13 MAY 2024   07:18 ago     E. Sotomayor
📄 Preferencias Interfaz       Reciente      35ms ago      Sistema
```

Sin árbol. Sin jerarquía de folders. Lista plana con filtro por capa.

### Panel derecho — al seleccionar una entrada

```
PROTOCOLO DE ESCALADA NIVEL 4
Capa: Organización · v1.4
Aprobado por: Álvaro Villarreal · 14 oct 2025

── Contenido completo ───────────────
[Texto completo de la entrada,
scrolleable hacia abajo si es largo]

── Patrones aprendidos desde esta entrada ─
3 outputs aprobados usaron esta entrada.
Cambio recurrente: tono más formal detectado.

── Historial de cambios ─────────────
v1.4 · "Actualización protocolo" · 14 oct
v1.3 · "Ajuste por caso cliente" · 03 sep
v1.2 · "Revisión inicial" · 15 ene

[ EDITAR DOCUMENTO  ]
[ SUGERIR CAMBIO    ]
```

"EDITAR DOCUMENTO" abre edición inline en el mismo panel — no modal.
"SUGERIR CAMBIO" muestra un campo de texto: "¿Qué debería cambiar y por qué?" + botón "Enviar sugerencia".

---

## Vista C — Outputs Aprobados

### Propósito
Repositorio de aprendizaje operativo. **No dashboard. Sin métricas globales. Sin gráficos. Lista de trabajo estructurado.**

### Área principal

Header:
```
OUTPUTS APROBADOS
Repositorio Operacional · Lista de Trabajo
```

Filtros en una línea:
```
[ Todos los skills ▾ ]  [ mm/dd/yyyy ]  [ Contacto... ]  [ Todos los estados ▾ ]  [ FILTRAR ]
```

Cards de output — uno por trabajo aprobado:

```
┌────────────────────────────────────────── [PATRÓN APRENDIDO ✓] ─┐
│  Respuesta Comercial · Distribuidora Ramírez · pedido #4421      │
│  Aprobado por: Álvaro · hace 3 días                              │
│  Cambios: saludo, fecha de entrega                               │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────── [SIN PATRÓN] ┐
│  Análisis Estratégico · Constructoras Alfa · Auditoría Q3        │
│  Aprobado por: Elena · hace 5 días                               │
│  Cambios: estructura, datos financieros                           │
└──────────────────────────────────────────────────────────────────┘
```

Badge `PATRÓN APRENDIDO` en `#16A34A`. Badge `SIN PATRÓN` en `#475569`.

### Panel derecho — al seleccionar un output

```
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
La entrega sale mañana en la mañana."

── Qué cambió ───────────────────────
Saludo:    "Estimado" → "Hola equipo"   [estilo]
Fecha:     genérica → específica        [contenido]
Longitud:  reducida significativamente  [estilo]

── Estado de aprendizaje ────────────
✓ PATRÓN DETECTADO
El sistema identificó este cambio como
patrón en respuestas comerciales.

[ Marcar como excepción ]

─────────────────────────────────────
¿La instrucción necesita ajuste?
[ Ajustar instrucción del skill → ]

─────────────────────────────────────
[ Ver historial de cambios ]
[ Compartir recurso         ]
```

**"Marcar como excepción":** el badge cambia a "EXCEPCIÓN — no aprendido" en `#475569`. El sistema deja de contar ese output como patrón.

**"Ajustar instrucción del skill":** el panel se transforma en editor inline del skill. Al guardar, el skill sube de versión y el panel vuelve al detalle del output.

---

## Reglas visuales para las 3 vistas

- Las 3 vistas usan el mismo sidebar, topbar y statusbar del shell
- Las 3 tienen panel derecho siempre visible con el detalle del ítem seleccionado
- Las 3 usan el mismo sistema de color sin excepciones
- Ninguna vista tiene dashboard, métricas globales ni gráficos

---

## Anti-patrones específicos de cada vista

**Señales:**
- No mostrar correos completos
- No inbox con threading o conversaciones
- No lista de emails sin priorización operativa

**Conocimiento:**
- No árbol de carpetas expandible
- No estructura tipo wiki con sidebar de navegación propia
- No tabla de base de datos con columnas técnicas

**Outputs Aprobados:**
- No tabla con estadísticas globales (total de outputs, porcentajes de precisión)
- No gráficos de uso o actividad
- No feed de conversación estilo chat

---

**Resultado esperado de esta corrida:**
3 vistas completas con el mismo shell y color system. Cada una muestra su área principal con ítems de ejemplo + panel derecho con el detalle del ítem seleccionado. La identidad visual debe ser idéntica entre las 3 vistas y consistente con las corridas anteriores.
