# FABERLOOM — CORRIDA 1: SHELL DEL PRODUCTO
**Para pegar directo en Stitch · No mezclar con otras corridas**

---

Diseña el shell desktop de **FaberLoom**, una aplicación de Operational Memory para PYMEs. Desktop-first. Mínimo 1280px. Pantalla completa.

**Lo que debes diseñar en esta corrida: solo el contenedor y la estructura. Sin conversaciones, sin contenido real, sin datos.**

---

## Layout — 3 columnas fijas

La aplicación tiene siempre esta estructura:

```
[ TOPBAR ]
[ SIDEBAR IZQUIERDO | CONSOLA CENTRAL | PANEL DERECHO ]
[ STATUSBAR ]
```

---

## Topbar

Franja horizontal superior. Fondo `#1E293B`. Borde inferior `#334155`.

- **Izquierda:** punto pequeño en `#4338CA` + texto "FABERLOOM" en SemiBold 14px
- **Centro:** tabs de navegación activa de la vista actual
- **Derecha:** ícono de notificaciones · ícono de configuración · avatar circular del usuario

---

## Sidebar izquierdo

Fondo `#1E293B`. Borde derecho `#334155`. Expandido con labels visibles por defecto.

Estructura de arriba hacia abajo:

```
─ NAVEGACIÓN ─────────────────────
▶ Consola                          ← ítem activo
  Outputs aprobados
  Señales                          [badge numérico si hay señales]
  Conocimiento
  ──────────────────────────────
  Organización
  Configuración

─ SESIÓN ACTUAL ───────────────────
● Respuesta Ramírez #4421          ← activa: punto en #4338CA
  Reactivación B2B Arkano
  Seguimiento SLA Delta

─ AYER ────────────────────────────
  Propuesta Constructoras
  Cobro Inversiones Delta

  Ver historial completo →

──────────────────────────────────
[avatar]  Javier M.
          javier@faberloom.io
```

**Ítem de nav activo:** borde izquierdo 2px en `#4338CA` + fondo `#263348` + texto `#F1F5F9`.

**Ítem de nav inactivo:** sin fondo · texto `#94A3B8`.

**Conversación activa:** punto relleno en `#4338CA` + texto `#94A3B8`.

**Conversaciones inactivas:** punto vacío en `#334155` + texto `#475569`.

---

## Consola central

Fondo `#0F172A`. Ocupa todo el espacio entre sidebar y panel derecho.

**Área de mensajes:** espacio vacío y scrolleable. Sin contenido en esta corrida.

**Input bar — fijo en la parte inferior:**

```
┌──────────────────────────────────────────────────────────┐
│ [Skill: Respuesta comercial ×]  Escribe tu consulta... ▶ │
└──────────────────────────────────────────────────────────┘
Escribe / para activar un skill · Enter para enviar
```

- El tag de skill tiene fondo semitransparente `#6366F1` al 15% + borde `#6366F1` al 40% + texto `#6366F1`
- El "×" del tag es clickeable para quitar el skill
- El campo de texto es simple, sin borde propio
- El botón enviar `▶` tiene fondo `#4338CA`
- El hint debajo es texto `#475569` en 10.5px

---

## Panel derecho

Fondo `#1E293B`. Borde izquierdo `#334155`. Siempre visible. No desaparece.

**3 tabs en la parte superior:**

```
[ Skill activo ]  [ Contexto ]  [ Fuentes ]
```

Tab activo: texto `#F1F5F9` + borde inferior 2px `#4338CA`.
Tab inactivo: texto `#475569`.

**Contenido placeholder de cada tab en esta corrida:**

Tab "Skill activo":
```
NOMBRE DEL SKILL                  v1.4
Configurado por: Usuario · fecha

── Instrucción activa ──────────
[Texto de la instrucción aquí]

── Patrones aprendidos ─────────
✓ Patrón ejemplo — N veces
⚠ Patrón rechazado — N veces

── Historial de ajustes ────────
v1.4 · "Descripción" · fecha
```

Tab "Contexto":
```
── Contexto activo ─────────────
● KB: Nombre de la KB
● Voz: Perfil personal activo

── Señales relacionadas ────────
[Señal 1: remitente · tema · Xh]
[Señal 2: remitente · tema · Xh]

── Outputs similares ───────────
→ Output similar 1
→ Output similar 2
```

Tab "Fuentes":
```
── Fuentes del último output ───

KB Organización
  Nombre de entrada usada

Outputs similares
  N aprobados con perfil similar

── Parámetros de salida ────────
modelo:    Helios Neural
voz:       Perfil personal activo
estructura: Formal · Párrafos cortos
```

**Nota:** nunca JSON crudo en este panel. Siempre texto legible.

---

## Statusbar

Franja inferior. Fondo `#263348`. Borde superior `#334155`. Fuente JetBrains Mono 10.5px. Color `#475569`.

```
● Listener activo  |  KB: Pedidos activos  |  Voz: Perfil personal  |  [extremo derecho:] Draft · no enviado · FaberLoom nunca actúa sin permiso
```

Siempre visible. En todas las vistas.

---

## Sistema de color completo

| Token | Hex | Uso |
|-------|-----|-----|
| Fondo principal | `#0F172A` | Toda la app |
| Superficie | `#1E293B` | Sidebar, panel, input |
| Elevado | `#263348` | Hover, dropdowns, Estado 3 |
| Borde | `#334155` | Divisores, bordes |
| Texto principal | `#F1F5F9` | Todo el texto principal |
| Texto secundario | `#94A3B8` | Labels, metadata |
| Texto muted | `#475569` | Placeholders, hints |
| Primary | `#4338CA` | Acciones, nav activo |
| Primary hover | `#3730A3` | Hover sobre primary |
| Draft | `#6366F1` | Estado de propuesta |
| Aprobado | `#16A34A` | Post-aprobación |
| Señal | `#0284C7` | Email signals |
| Warning | `#D97706` | Alertas |
| Bloqueado | `#DC2626` | Errores, límites |

---

## Tipografía

- **UI general:** Inter Regular (400) y Medium (500)
- **Metadata, trust layers, referencias:** JetBrains Mono Regular (400)
- Sin serif. Sin decorativa. Sin rounded-playful.

---

## Anti-patrones — nunca en ninguna pantalla

- Sin dashboard con métricas o gráficos
- Sin árbol de carpetas o estructura wiki
- Sin chat bubbles redondas con cola estilo iMessage
- Sin iconografía con emojis o íconos de relleno colorido
- Sin gradientes ni colores neón
- Sin mobile o responsive

---

**Resultado esperado de esta corrida:**
El shell vacío de la aplicación con estructura, jerarquía visual, color system y tipografía correctamente establecidos. Sin datos reales. Sin interacciones complejas. Solo la estructura que sirve de base para las siguientes corridas.
