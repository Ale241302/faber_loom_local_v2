<!--
  MWT HEADER
  id: faberloom-design-system
  version: 1.0.0
  status: alpha
  visibility: internal
  domain: design-system
  last_updated: 2025-01-15
  owner: FaberLoom Product Design
-->

---
# Tokens semanticos representativos (subset consumible por agentes IA)
# Stack: DTCG + Style Dictionary v4 + CSS Custom Properties
tokens:
  color:
    cream: "#F4F1ED"
    ink: "#1F1E1C"
    coral: "#C96442"
    pizarra: "#5A6B7C"
    cream_dark: "#E8E2DA"
    ink_dark: "#2A2927"
    coral_hover: "#B85A3A"
    coral_subtle: "rgba(201, 100, 66, 0.08)"
    ink_60: "rgba(31, 30, 28, 0.6)"
    ink_30: "rgba(31, 30, 28, 0.3)"
    ink_10: "rgba(31, 30, 28, 0.1)"
    success: "#4A7C59"
    warning: "#C9A03F"
    error: "#C94A4A"
    agent_autonomous: "#4A7C59"
    agent_review: "#C9A03F"
    agent_paused: "#5A6B7C"
    agent_error: "#C94A4A"
  font:
    display: "Crimson Pro, Georgia, serif"
    body: "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    mono: "IBM Plex Mono, Menlo, monospace"
  spacing:
    unit: "4px"
    xs: "4px"
    sm: "8px"
    md: "16px"
    lg: "24px"
    xl: "32px"
    xxl: "48px"
    xxxl: "64px"
  radius:
    sm: "4px"
    card: "12px"
    button: "8px"
    input: "8px"
    pill: "9999px"
    tag: "6px"
  shadow:
    0: "none"
    1: "0 1px 2px rgba(31, 30, 28, 0.04)"
    2: "0 2px 8px rgba(31, 30, 28, 0.06)"
    3: "0 4px 16px rgba(31, 30, 28, 0.08)"
    4: "0 8px 32px rgba(31, 30, 28, 0.10)"
    5: "0 16px 48px rgba(31, 30, 28, 0.12)"
  z_index:
    base: "0"
    elevated: "10"
    sticky: "100"
    dropdown: "200"
    modal: "300"
    toast: "400"
    tooltip: "500"
  breakpoint:
    sm: "640px"
    md: "768px"
    lg: "1024px"
    xl: "1280px"
    xxl: "1536px"
  layout:
    grid_columns: "24"
    container_max: "1440px"
    sidebar_width: "280px"
    chat_panel_width: "380px"
---

# FaberLoom Design System

## 1. Overview

### Que es FaberLoom

FaberLoom es una plataforma SaaS B2B chat-first agentic multi-tenant construida sobre la premisa de que el profesional humano sigue siendo el protagonista del trabajo intelectual. Es un entorno donde la IA actua como preparadora — organiza, sugiere, anticipa — pero el tejedor siempre es el humano. FaberLoom no reemplaza el juicio profesional; lo potencia mediante un sistema de tres tabs (Configurar / Iterar / Sanidad) y una escalera de confianza progresiva que gobierna la autonomia del agente.

### Para quien es

FaberLoom esta disenado para profesionales que operan en la interseccion entre analisis y ejecucion: consultores, analistas senior, gerentes de producto, disenadores de sistemas, arquitectos de negocio. Personas cuyo oficio requiere precision, trazabilidad y control. No es para el usuario casual ni para quien busque "que la IA lo haga todo". Es para quien valora la preparacion inteligente pero mantiene el control del tejido final.

### Filosofia de diseno

1. **El humano es el tejedor.** La IA prepara los hilos; el profesional entrelaza el patron final. Cada decision de diseno debe reforzar esta jerarquia, nunca invertirla.

2. **Calma operativa.** La interfaz no grita. No hay animaciones innecesarias, no hay badges de "nuevo" parpadeantes, no hay colores saturados que compitan por atencion. El profesional ya tiene suficiente ruido en su trabajo; FaberLoom es el espacio de concentracion.

3. **Precision antes que velocidad.** Mejor mostrar el estado correcto con 200ms de delay que un estado optimista que miente. La confianza del profesional en la herramienta se construye con veracidad, no con prestidigitacion.

4. **Progresion visible.** La autonomia del agente no es binaria. Cada nivel de la Trust Ladder debe ser visible, comprensible y reversible. Nunca un togglencillo; siempre una escalera.

5. **El oficio merece respeto.** La interfaz no paternaliza. No explica lo obvio, no celebra lo rutinario, no aplaude lo esperado. Trata al profesional como par, no como alumno.

### Como usar este documento (para agentes IA)

Este documento es la fuente de verdad para todas las decisiones de diseno, redaccion de UI, y comportamiento de componentes en FaberLoom. Cuando generes codigo, copies o interfaces:

- **Tokens semanticos**: Usa los valores del YAML frontmatter. Nunca hardcodees hexes, fontsizes o spacings que existan como token.
- **Voice & Tone**: Lee la seccion 8 completa antes de escribir cualquier string de UI. Si hay conflicto entre brevedad y tono correcto, gana el tono.
- **Do's & Don'ts**: La seccion 9 es tu checklist de validacion. Si algo que generaste cae en un Don't, reescribelo.
- **Anti-patterns**: La seccion 10 es roja. Cualquier decision de diseno que toque un anti-pattern es invalida por definicion.

Cuando dudes, prioriza: **Calma > Coral > Precision > Velocidad**.

---

## 2. Colors

### Cream `#F4F1ED` — Fondo primario

Cream es el color sobre el que descansa toda la experiencia de FaberLoom. No es blanco `#FFFFFF` porque el blanco puro es agresivo, clinico, frio. El oficio humano ocurre en espacios calidos — un taller, un estudio, una mesa de madera. Cream evoca papel de archivo de alta calidad, la pagina de un cuaderno de trabajo. Es el lienzo donde el profesional teje.

- **Uso**: Fondo de aplicacion, superficies de cards en reposo, areas de lectura, canvas de trabajo.
- **No usar como**: Color de texto (fallaria accesibilidad), color de acento (no es su rol).

### Ink `#1F1E1C` — Texto primario

Ink no es negro puro `#000000`. Es un negro calido, tirando a marron, como la tinta de una estilografica sobre papel de buena gramaje. Es el color del oficio escrito, del documento que importa.

- **Uso**: Texto principal, iconos activos, bordes de estructura, datos primarios.
- **Variantes**: `ink_60` para metadatos, `ink_30` para placeholders y divisores, `ink_10` para fondos de hover sutiles.

### Coral `#C96442` — UNICO driver de interaccion

Coral es el unico color con permiso para llamar la atencion activamente en la interfaz. No es naranja de alerta; es terracota, arcilla cocida, el color de las herramientas que mejoran con el uso. Solo existe un driver de interaccion porque el profesional no necesita competencia visual. Cuando algo es coral, significa "puedes/puedes/deberias interactuar aqui".

- **Uso**: Botones primarios, links, estados activos, indicadores de foco, badges de accion requerida, cursor de agente cuando solicita aprobacion.
- **Hover**: `coral_hover` (`#B85A3A`) — mas profundo, no mas brillante. La interaccion se sumerge, no estalla.
- **Subtle**: `coral_subtle` — para fondos de badges, resaltados de busqueda, estados seleccionados en lista.
- **NUNCA usar como**: Color de fondo general, color de texto de cuerpo, color de borde decorativo.
- **Regla de oro**: Si necesitas un tercer color para "algo importante que no es un boton", no inventes uno. Usa ink con mas peso o una variante de coral_subtle.

### Pizarra `#5A6B7C` — Secundario, metadatos, apagado

Pizarra es el color de lo secundario pero necesario: timestamps, contadores, estados inactivos, iconos de acciones disponibles pero no prioritarias. Es el gris azulado de una pizarra que ha sido borrada pero conserva trazos. Funciona porque no compite con ink ni con coral.

- **Uso**: Texto de metadatos, iconos inactivos, bordes de inputs en reposo, labels de formularios, timestamps.
- **No usar como**: Texto principal (falta contraste en fondos oscuros), color de acento.

### Estados del agente (pares semanticos)

Cada estado de la Trust Ladder tiene un par de colores que comunica simultaneamente estado y accion requerida:

| Estado | Color | Significado |
|--------|-------|-------------|
| Autonomo | `agent_autonomous` `#4A7C59` verde bosque | El agente actua sin supervision. Confianza establecida. |
| Revision | `agent_review` `#C9A03F` ocre | El agente propone; el humano decide. Escalera activa. |
| Pausado | `agent_paused` `#5A6B7C` pizarra | El agente espera instruccion explicita. Control humano total. |
| Error | `agent_error` `#C94A4A` rojo ladrillo | Fracaso operativo. Requiere intervencion del profesional. |

La escala de estados es intencionalmente diferente del driver de interaccion (coral). El estado del agente no es una invitacion a clickear; es informacion. Por eso usa una paleta separada, derivada de semanticas universales pero adaptadas al tono calido de FaberLoom.

### Modo oscuro (Dark Mode)

El dark mode de FaberLoom no es "modo noche generico". Es **papel kraft tostado** — la inversion logica de un entorno de trabajo nocturno que conserva la calidez.

- **Fondo**: `ink_dark` `#2A2927` — no negro puro, sino un marron muy oscuro.
- **Superficies**: un escalon mas claro sobre el fondo, nunca gris frio.
- **Texto**: `cream` `#F4F1ED` — inversion completa del modo claro.
- **Coral**: se mantiene `coral` `#C96442`, sin variacion. El driver de interaccion es inmutable.
- **Pizarra**: se ilumina ligeramente para mantener legibilidad sobre fondos oscuros.

El dark mode no es un filtro de inversion de colores. Es una paleta completa derivada con intencion.

### Tokens de color extendidos

```css
:root {
  /* Base */
  --fl-cream: #F4F1ED;
  --fl-ink: #1F1E1C;
  --fl-coral: #C96442;
  --fl-pizarra: #5A6B7C;

  /* Derivados */
  --fl-cream-dark: #E8E2DA;
  --fl-ink-60: rgba(31, 30, 28, 0.6);
  --fl-ink-30: rgba(31, 30, 28, 0.3);
  --fl-ink-10: rgba(31, 30, 28, 0.1);
  --fl-coral-hover: #B85A3A;
  --fl-coral-subtle: rgba(201, 100, 66, 0.08);

  /* Estados de agente */
  --fl-agent-autonomous: #4A7C59;
  --fl-agent-review: #C9A03F;
  --fl-agent-paused: #5A6B7C;
  --fl-agent-error: #C94A4A;

  /* Semantica extendida */
  --fl-success: #4A7C59;
  --fl-warning: #C9A03F;
  --fl-error: #C94A4A;
}
```

---

## 3. Typography

### Stack tipografico completo

| Rol | Fuente | Fallback | Uso |
|-----|--------|----------|-----|
| Display | Crimson Pro Italic 500 | Georgia, serif | Wordmark "Faber", titulos de seccion, citas, momentos de voz de marca |
| UI / Body | Inter Bold 700, Regular 400 | -apple-system, BlinkMacSystemFont, sans-serif | Navegacion, botones, etiquetas, texto de UI, "Loom" en wordmark |
| Datos / Logs | IBM Plex Mono Regular 400 | Menlo, Consolas, monospace | Logs del agente, JSON, timestamps, diff views, codigo, metadatos tecnicos |

### Por que este stack

**Crimson Pro Italic** es la voz poetica del sistema — el "Faber" en FaberLoom. Aparece en momentos de pausa, en titulos que marcan territorio, en el wordmark. Su cursiva evoca la escritura a mano, el gesto humano, la firma del artesano. Pero es restricativa: nunca se usa en cuerpo de texto largo ni en UI operativa. Su presencia es la excepcion que confirma la regla de la calma.

**Inter** es la voz operativa — "Loom" en FaberLoom. Neutra, legible, esculpida para pantalla. Bold 700 para acciones y jerarquia; Regular 400 para lectura. Inter no tiene opinion estetica propia, lo cual es exactamente lo que necesita una herramienta que no compite con el trabajo del profesional.

**IBM Plex Mono** es la voz del sistema cuando habla de su propio funcionamiento. Los logs del agente no usan fuente proporcional porque necesitan alineacion vertical. Los diff views necesiten columnas que no se muevan. Plex Mono es tecnico sin ser frio — su diseño humanista la diferencia de Courier y consortes.

### Escala tipografica

| Token | Tamanio | Line-height | Letter-spacing | Uso |
|-------|---------|-------------|----------------|-----|
| display-xl | 48px | 1.1 | -0.02em | Wordmark completo, hero vacio |
| display-lg | 36px | 1.15 | -0.01em | Titulos de pagina, estados vacios |
| display-md | 28px | 1.2 | -0.01em | Titulos de seccion, nombres de tenant |
| heading-lg | 24px | 1.3 | 0 | Subtitulos, nombres de proyecto |
| heading-md | 20px | 1.35 | 0 | Titulos de card, titulos de modal |
| heading-sm | 16px | 1.4 | 0 | Labels de grupo, titulos de panel |
| body-lg | 16px | 1.6 | 0 | Texto de cuerpo, descripciones |
| body-md | 14px | 1.5 | 0 | Texto de UI, opciones de menu |
| body-sm | 12px | 1.4 | 0.01em | Metadatos, timestamps, captions |
| mono-md | 13px | 1.5 | 0 | Logs, JSON, diff views |
| mono-sm | 11px | 1.4 | 0.02em | Timestamps tecnicos, versiones |

### Cuando usar display vs body vs mono

- **Display**: Cuando la interfaz necesita "respirar". Pantallas vacias, estados de onboarding completado, titulos de seccion que marcan territorio. Nunca en medio de una operacion.
- **Body / UI**: El 85% de la interfaz. Todo lo que requiere lectura continua o decision rapida.
- **Mono**: Solo cuando el contenido es estructuralmente tabular o tecnico. Logs, codigo, diff views, metadatos de ejecucion. Nunca para texto libre del usuario ni del agente.

### Wordmark

El wordmark "FaberLoom" se compone asi:
- **"Faber"** — Crimson Pro Italic 500, color `ink`. La parte humana, el gesto.
- **"Loom"** — Inter Bold 700, color `coral`. La parte tecnica, el sistema.

La separacion visual refuerza el manifiesto: Faber (el humano) y Loom (la herramienta) son entidades distintas pero inseparables. El coral en "Loom" identifica al sistema como la parte activa, la que responde.

### Descripcion visual de la escala

- `display-xl` (48px): "FaberLoom" en la pantalla de bienvenida. Grandioso pero no griton. Crimson Pro Italic lo hace sentir como el titulo de un libro de mesa de trabajo.
- `display-lg` (36px): "Configurar proyecto" al abrir el tab de setup. La interfaz da un paso atras para presentar el territorio.
- `body-lg` (16px): La descripcion de un paso en el wizard. Legible, generoso en interlineado, respetuoso del tiempo del lector.
- `mono-md` (13px): Un log del agente mostrando `[14:32:07] Analizando dependencias...`. Aligereado, tabular, sin pretensiones.

---

## 4. Layout

### Sistema de grillas: 24 columnas

FaberLoom usa una grilla de 24 columnas con gutter de `16px` (`--fl-spacing-md`). Veinticuatro columnas en lugar de doce porque la interfaz es densa y necesita granularidad: sidebar + panel de chat + canvas principal + panel de contexto pueden coexistir en ciertos modos.

- **Gutter**: 16px (no responsivo; la densidad de informacion no cambia con el viewport)
- **Margen exterior**: 24px en desktop, 16px en tablet, 8px en mobile
- **Columnas colapsables**: El panel de chat (380px) ocupa 8 columnas; el canvas principal ocupa el resto. En viewports < 1024px, el chat se convierte en overlay.

### Breakpoints

| Nombre | Valor | Uso |
|--------|-------|-----|
| sm | 640px | Mobile. Layout single-column. Chat es overlay de pantalla completa. Sidebar es drawer. |
| md | 768px | Tablet. Grilla se reduce a 12 columnas efectivas. Sidebar colapsada por defecto. |
| lg | 1024px | Desktop pequeno. Layout completo con sidebar visible. Chat puede ser panel o overlay. |
| xl | 1280px | Desktop estandar. Layout optimo. Sidebar expandida, chat como panel derecho. |
| xxl | 1536px | Desktop amplio. Canvas con aire. Posibilidad de paneles multiples visibles. |

### Z-index scale

| Valor | Capa | Uso |
|-------|------|-----|
| 0 | base | Contenido normal, canvas, cards |
| 10 | elevated | Cards hover, dropdowns internos |
| 100 | sticky | Headers sticky, barra de tabs |
| 200 | dropdown | Menues desplegables, selects, autocomplete |
| 300 | modal | Dialogos modales, drawers laterales |
| 400 | toast | Notificaciones toast, banners de estado |
| 500 | tooltip | Tooltips, popovers de ayuda contextual |

La escala no es multiplicativa (no 10, 20, 30...) porque necesita "respirar". Entre 10 y 100 hay espacio para elementos custom que no rompan la jerarquia.

### Maximos de contenedor

| Contenedor | Max-width | Padding |
|------------|-----------|---------|
| App shell | 100% | 0 (layout fluido) |
| Canvas de trabajo | 1440px | 24px |
| Modal | 640px | 0 (el modal maneja su propio padding) |
| Modal grande | 960px | 0 |
| Toast | 400px | 0 |
| Panel de chat | 380px | 16px |
| Sidebar | 280px | 16px |

### Modo lectura vs modo operacion

FaberLoom tiene dos modos de layout que coexisten:

**Modo operacion (default)**: Layout completo con sidebar, tabs, chat, y canvas. Todo visible, todo alcanzable. La densidad es intencional — el profesional necesita contexto.

**Modo lectura**: Activo cuando el usuario abre un documento largo, un reporte, o un log extenso. La sidebar se colapsa, el chat se minimiza, el canvas ocupa el maximo posible. La tipografia cambia a `body-lg` con mayor interlineado. Es el equivalente de "limpiar la mesa de trabajo".

Transicion entre modos: `0.3s ease` en el width del sidebar y el opacity del contenido colapsado. No hay animacion de "slide" porque eso seria distractor en un contexto profesional.

---

## 5. Elevation

### Shadow scale

| Nivel | Valor | Uso |
|-------|-------|-----|
| 0 | `none` | Elementos planos, estados base, inputs en reposo |
| 1 | `0 1px 2px rgba(31, 30, 28, 0.04)` | Cards en reposo, tags, badges |
| 2 | `0 2px 8px rgba(31, 30, 28, 0.06)` | Cards hover, dropdowns, paneles flotantes |
| 3 | `0 4px 16px rgba(31, 30, 28, 0.08)` | Modales pequenos, drawers, menus contextuales |
| 4 | `0 8px 32px rgba(31, 30, 28, 0.10)` | Modales grandes, overlays de confirmacion |
| 5 | `0 16px 48px rgba(31, 30, 28, 0.12)` | Toasts criticos, dialogos de bloqueo |

### Filosofia de la elevacion

Las sombras en FaberLoom no son decorativas. Cada nivel representa una capa de la atencion del profesional:

- **Nivel 0-1**: El piso. Elementos que esperan, disponibles pero no demandantes.
- **Nivel 2**: La herramienta que extiendes la mano y tomas. Cards que puedes levantar, dropdowns que despliegas.
- **Nivel 3**: La interrupcion suave. "Necesito tu atencion pero no es urgente."
- **Nivel 4**: La interrupcion firme. "Esto bloquea algo que querias hacer."
- **Nivel 5**: La interrupcion critica. "Esto requiere tu decision ahora."

Las sombras usan `ink` con opacidad decreciente, no negro puro. Esto mantiene la calidez del sistema incluso en elementos que "flotan".

### Dark mode shadows

En dark mode, las sombras son mas pronunciadas porque los fondos oscuros absorben luz:

```css
[data-theme="dark"] {
  --fl-shadow-1: 0 1px 2px rgba(0, 0, 0, 0.20);
  --fl-shadow-2: 0 2px 8px rgba(0, 0, 0, 0.25);
  --fl-shadow-3: 0 4px 16px rgba(0, 0, 0, 0.30);
  --fl-shadow-4: 0 8px 32px rgba(0, 0, 0, 0.35);
  --fl-shadow-5: 0 16px 48px rgba(0, 0, 0, 0.40);
}
```

### Z-index layers completo

| Capa | Z-index | Contenido tipico |
|------|---------|------------------|
| Base | 0 | Canvas, cards, contenido estatico |
| Elevated | 10 | Card hovers, elementos con sombra 1-2 |
| Sticky | 100 | App header, tab bar, sidebar header |
| Dropdown | 200 | Select menus, autocomplete, submenus |
| Modal | 300 | Dialogs, drawers, overlays de bloqueo |
| Toast | 400 | Notification stack, banners fijos |
| Tooltip | 500 | Tooltips, popovers informativos |

---

## 6. Shapes

### Radius scale

| Token | Valor | Uso |
|-------|-------|-----|
| radius-sm | 4px | Tags, badges pequenos, checkboxes, switches |
| radius-tag | 6px | Tags de categoria, filtros, pills de seleccion multiple |
| radius-button | 8px | Todos los botones, inputs de formulario |
| radius-card | 12px | Cards, modales, paneles, drawers |
| radius-pill | 9999px | Badges de estado, chips de usuario, pills de navegacion |

### Filosofia de los radios

La escala de radios en FaberLoom sigue una logica de "confianza visual":

- **Formularios (8px)**: Lo suficientemente redondeado para no parecer militar, lo suficientemente angular para transmitir precision.
- **Cards (12px)**: Mas generoso que los formularios porque las cards contienen multiples elementos y necesitan sentirse "acogedoras".
- **Pills (9999px)**: Solo para elementos que son "etiquetas" — no interactivos en si mismos, sino descriptores. El pill es la forma del lenguaje, no de la herramienta.

No hay "radius-lg" de 16px o 24px. Las superficies grandes en FaberLoom no se redondean excesivamente porque el canvas de trabajo no es un app movil; es un entorno profesional donde los bordes definen territorio.

### Iconos

- **Grilla**: 24x24px (iconos de UI), 20x20px (iconos densos en tablas), 16x16px (iconos en tags/badges).
- **Stroke**: 1.5px para iconos outline, 2px para iconos solid.
- **Color default**: `ink` para iconos activos, `pizarra` para iconos inactivos, `coral` para iconos de accion.
- **Estilo**: Line-based, no filled. Geometricos pero no rigidos. Evitar iconos con "personalidad" excesiva (sin caras, sin gestos, sin ilustraciones).
- **Libreria**: Lucide como base, con custom icons para conceptos propios de FaberLoom (Trust Ladder, agent states, loom/thread metaphors).

### Isotipo (en exploracion)

Los tres conceptos en exploracion para el isotipo de FaberLoom:

1. **Trama**: Un patron de interseccion regular, como el entramado de un telar. Comunica estructura y regularidad.
2. **Hilos entrelazados**: Lineas curvas que se cruzan sin anudarse. Comunican la relacion entre humano e IA sin fusion.
3. **Nudo celtico moderno**: Un nudo con trazos limpios, no ornamental. Comunica conexion indisoluble pero con estructura.

Convencion de revision: **estrella = canon**. Cuando un isotipo reciba estrella en revision, pasa a ser la version definitiva.

---

## 7. Components

### Button

**Variantes:**

| Variante | Background | Texto | Border | Uso |
|----------|-----------|-------|--------|-----|
| primary | `coral` | `cream` | none | Accion principal, CTA, guardar, confirmar |
| secondary | transparent | `ink` | 1px `ink_30` | Accion secundaria, cancelar, volver |
| tertiary | transparent | `coral` | none | Accion vinculada, "mas opciones", links que parecen botones |
| ghost | transparent | `pizarra` | none | Acciones de baja prioridad, iconos solitarios |

**Comportamiento:**
- Hover: primary oscurece a `coral_hover`; secondary invierte a `ink` fondo con `cream` texto; tertiary subraya sutilmente.
- Active: scale(0.98) — la herramienta cede bajo presion, no se hunde.
- Disabled: opacity 0.5, cursor not-allowed. Nunca cambiar el color del texto a gris.
- Focus: ring de 2px `coral` con 2px de offset. Visible siempre, no solo en keyboard.

**Estados:**
- `idle` — estado normal
- `hover` — cursor sobre el boton
- `active` — mouse down / tecla espacio
- `loading` — spinner reemplaza el texto, boton no interactivo
- `success` — check icon breve antes de volver a idle
- `error` — shake animation + mensaje inline

### Card

**Estructura:**
- Background: `cream` o superficie elevada sobre `cream`
- Border: 1px `ink_10` (sutil, no divisorio)
- Radius: `radius-card` (12px)
- Shadow: `shadow-1` en reposo, `shadow-2` en hover
- Padding: 24px (interno generoso)

**Variantes:**
- `default` — card de contenido general
- `interactive` — card clicable, hover elevado, cursor pointer
- `selected` — borde `coral`, fondo `coral_subtle`
- `disabled` — opacity 0.6, no interactiva

### Input / TextField

**Estructura:**
- Height: 40px (estandar), 32px (compacto)
- Background: `cream`
- Border: 1px `pizarra` en reposo, 1px `ink` en focus, 1px `coral` en error
- Radius: `radius-button` (8px)
- Padding: 12px horizontal

**Comportamiento:**
- Focus: border cambia a `ink`, aparece shadow sutil `shadow-1`
- Error: border `coral`, mensaje debajo en `body-sm` color `error`
- Disabled: background `cream_dark`, texto `ink_30`
- Placeholder: `ink_30`, italic (unico lugar donde se permite italic en UI que no sea display)

### Select / Dropdown

**Estructura:**
- Trigger: mismo que input
- Menu: card flotante, `shadow-3`, `radius-card`
- Opcion hover: `coral_subtle` fondo
- Opcion selected: `coral` texto, check icon a la derecha
- Max-height: 320px con scroll interno

### Tab

**Estructura (los 3 tabs de FaberLoom):**
- Height: 48px
- Border-bottom: 2px `ink_10`
- Tab activo: border-bottom 2px `coral`, texto `ink`, font-weight 700
- Tab inactivo: texto `pizarra`, font-weight 400
- Hover inactivo: texto `ink`, fondo `ink_10`

**Los tres tabs:**
- **Configurar** — Icono settings, "Setup del proyecto"
- **Iterar** — Icono sync/play, "Trabajo activo"
- **Sanidad** — Icono shield/check, "QA y validacion"

### Badge / Tag

**Variantes:**

| Variante | Background | Texto | Uso |
|----------|-----------|-------|-----|
| neutral | `ink_10` | `ink` | Etiquetas genericas, categorias |
| coral | `coral_subtle` | `coral` | Accion requerida, estado activo |
| success | `rgba(74, 124, 89, 0.1)` | `success` | Operacion completada, exito |
| warning | `rgba(201, 160, 63, 0.1)` | `warning` | Atencion necesaria, review |
| error | `rgba(201, 74, 74, 0.1)` | `error` | Error, fallo operativo |

**Estructura:**
- Height: 24px (default), 20px (compacto)
- Padding: 6px 12px
- Radius: `radius-tag` (6px) para tags, `radius-pill` para badges de estado
- Font: `body-sm`, weight 500

### Toast

**Estructura:**
- Background: `ink` (dark sobre el cream de la app)
- Texto: `cream`
- Radius: `radius-card`
- Shadow: `shadow-5`
- Padding: 16px 20px
- Max-width: 400px

**Variantes:**
- `info` — icono info, sin acento de color
- `success` — icono check, borde izquierdo 3px `success`
- `warning` — icono alerta, borde izquierdo 3px `warning`
- `error` — icono x, borde izquierdo 3px `error`

**Comportamiento:**
- Entrada: slide desde arriba, `0.3s ease-out`
- Auto-dismiss: 5 segundos (info/success), persistente (warning/error)
- Hover: pausa el auto-dismiss
- Stack: max 3 toasts visibles, los nuevos empujan hacia abajo

### Trust Ladder Indicator

Componente custom de FaberLoom que visualiza la autonomia actual del agente.

**Estructura:**
- 4 niveles visuales en linea horizontal
- Nivel activo: `coral` filled + label `coral`
- Niveles inferiores alcanzados: `ink` filled + label `ink`
- Niveles no alcanzados: `ink_30` outline + label `ink_30`
- Conector: linea 2px entre niveles, color segun estado de conexion

**Niveles:**
1. **Asistido** — El agente sugiere, el humano ejecuta. Todo requiere aprobacion.
2. **Semi-autonomo** — El agente ejecuta lo rutinario, pide confirmacion en lo novedoso.
3. **Autonomo** — El agente ejecuta, informa post-hoc. Solo escala en excepciones.
4. **Delegado** — El agente opera dentro de guardrails. El humano supervisa por dashboard.

**Comportamiento:**
- Cada nivel es clicable para cambiar la politica de autonomia.
- Cambio de nivel requiere confirmacion en modal.
- El nivel actual muestra tooltip con descripcion de comportamiento.

### Chat Panel

El componente central de la experiencia FaberLoom.

**Estructura:**
- Width: 380px (fijo en desktop), 100% en overlay mobile
- Height: 100% del viewport menos header
- Background: `cream` con borde izquierdo 1px `ink_10`
- Header: nombre del agente, estado actual (con dot de color de agent_state), menu de acciones

**Mensajes:**
- **Usuario**: alineado derecha, fondo `ink`, texto `cream`, radius 12px 12px 2px 12px
- **Agente**: alineado izquierda, fondo `cream_dark`, texto `ink`, radius 12px 12px 12px 2px
- **Sistema**: centrado, `mono-sm`, `pizarra`, sin bubble

**Input de chat:**
- Fixed al bottom del panel
- Textarea auto-expandible, max 6 lineas
- Placeholder cambia segun contexto (ver seccion 8, Voice & Tone)
- Boton enviar: icono `coral`, aparece solo cuando hay contenido

### Log Viewer

Componente para visualizar logs del agente.

**Estructura:**
- Background: `ink` en modo oscuro de panel (no el theme global, solo el panel)
- Texto: `cream` para niveles info, `warning` para warn, `error` para error
- Font: `mono-md` (13px)
- Timestamp: `mono-sm`, `pizarra`
- Nivel: abreviatura [INF], [WRN], [ERR] con color correspondiente
- Mensaje: `cream`, wrap habilitado

**Comportamiento:**
- Auto-scroll al final en nuevos mensajes
- Scroll manual desactiva auto-scroll
- Filtro por nivel: toggles en header del viewer
- Search: filtra inline con highlight `coral_subtle`

### Diff View

Componente para mostrar cambios propuestos por el agente.

**Estructura:**
- Split view o unified view (toggle por el usuario)
- Removido: fondo `rgba(201, 74, 74, 0.08)`, borde izquierdo 2px `error`, texto tachado
- Agregado: fondo `rgba(74, 124, 89, 0.08)`, borde izquierdo 2px `success`, texto nuevo
- Sin cambio: fondo transparente, texto `ink`
- Font: `mono-md` para contenido, `body-sm` para headers de seccion

---

## 8. Voice & Tone

La voz de FaberLoom es la voz de un colega experimentado: alguien que sabe mucho pero no lo dice de manera que te haga sentir menor. No es un mentor entusiasta ni un oraculo omnisciente. Es un preparador de confianza.

### Principios fundamentales (no negociables)

1. **Calmo, nunca euforico.** FaberLoom no celebra lo obvio, no se emociona con lo rutinario, no aplaude lo esperado.
2. **Preciso, nunca vago.** Cada palabra tiene un proposito. Si algo puede decirse con 5 palabras, no se usan 8.
3. **Respetuoso del oficio, nunca paternalista.** El profesional sabe. FaberLoom ayuda, no instruye.
4. **Confia en el profesional, nunca micro-managea.** No pregunta "estas seguro?" por defecto. Asume competencia.
5. **Herramienta, no oraculo.** Nunca habla con certeza absoluta sobre lo que no controla. Nunca dice "la IA lo sabe todo".

---

### Ejemplos Si / No — Categoria: Entusiasmo

**Contexto: El usuario completa una configuracion exitosamente.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "Configuracion guardada." | "Felicidades! Has completado la configuracion exitosamente!" |
| "Listo. El proyecto esta configurado con 14 variables." | "Genial! Todo salio perfecto! Estas listo para arrancar!" |
| "Guardado. Podes empezar a iterar cuando quieras." | "Excelente trabajo! Tu configuracion es impecable!" |

**Contexto: El agente termina una tarea larga.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "Tarea completada en 12 minutos. Resultados disponibles." | "Increible! Termine la tarea super rapido! Mirá los resultados!" |
| "Listo. Encontre 8 inconsistencias en el dataset." | "Wooo! Encontre un monton de cosas! Estas son super interesantes!" |
| "Analisis finalizado. Revisa los hallazgos antes de aplicar." | "Boom! Analisis completo! Estas listo para el siguiente paso!" |

**Contexto: Onboarding del usuario.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "Configuremos tu primer proyecto. Tres pasos." | "Bienvenido a bordo! Vamos a hacer magia juntos!" |
| "Paso 1: conectar tu repositorio." | "Empecemos esta emocionante aventura!" |
| "Cuando termines, pasamos al siguiente." | "Vamos a cambiar la forma en que trabajas para siempre!" |

**Contexto: El usuario alcanza un milestone.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "100 tareas completadas. El agente ajusto su modelo." | "Felicidades! Llegaste a 100 tareas! Eres increible!" |
| "Nivel de confianza actualizado. Revisa los cambios." | "Milestone desbloqueado! Estas en racha!" |

**Contexto: Nuevo feature disponible.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "Nuevo: export en formato Parquet. Disponible en el menu Exportar." | "Nueva funcion super emocionante! Ahora podes exportar en Parquet!" |
| "Se agrego soporte para schemas JSON. Documentacion actualizada." | "Gran noticia! Schema support esta aqui! Vas a amar esto!" |

---

### Ejemplos Si / No — Categoria: Precision

**Contexto: Describir una accion del agente.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "Analizando 1.247 registros. ETA: 45 segundos." | "Estoy procesando tus datos... casi listo..." |
| "Detecte 3 dependencias circulares en el modulo Auth." | "Parece que hay algunos problemas con tus dependencias..." |
| "El query tardo 2.3s. Umbral configurado: 1s." | "El query fue un poco lento..." |

**Contexto: Reportar un error.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "Error de conexion a la API. Status 503. Reintentando en 30s." | "Ups! Algo salio mal con la conexion..." |
| "El archivo excede el limite de 50MB (actual: 67MB)." | "El archivo es un poco grande..." |
| "Validacion fallida: el campo 'email' requiere formato RFC 5322." | "El email no parece valido..." |

**Contexto: Explicar una decision del agente.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "Exclui 14 registros por valores nulos en campos requeridos." | "Simplifique los datos un poco..." |
| "Agrupe por 'categoria' porque es el campo con mayor cardinalidad." | "Decidi agrupar de una manera que tiene sentido..." |
| "No modifique el archivo original. Cree un backup en /tmp/." | "Hice algunos ajustes para que todo funcione bien..." |

**Contexto: Estado de progreso.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "Paso 2 de 5: validando schema... 340/1.200 registros." | "Estoy trabajando en eso... un momento..." |
| "Indexando: 67% completado. Tiempo transcurrido: 4m 12s." | "Casi termino... gracias por tu paciencia..." |
| "En cola: posicion 3. Tiempo estimado de espera: 2m." | "Estoy en eso! Solo un segundito mas..." |

**Contexto: Datos y metricas.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "Precision: 94.2%. Recall: 89.7%. F1: 91.9%." | "El modelo funciona bastante bien!" |
| "Latencia p95: 180ms. p99: 340ms." | "La app es rapida la mayoria del tiempo." |
| "Costo estimado: $0.034 por ejecucion." | "Es bastante economico!" |

---

### Ejemplos Si / No — Categoria: Respeto al oficio

**Contexto: El usuario comete un error obvio.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "El campo 'fecha_fin' es anterior a 'fecha_inicio'." | "Parece que hubo un pequeno error con las fechas..." |
| "Falta el valor para 'API_KEY' en las variables de entorno." | "Olvidaste configurar tu API key! No te preocupes, es facil!" |
| "El archivo no tiene extension .csv. Verifica el formato." | "Parece que subiste el tipo de archivo equivocado..." |

**Contexto: Explicar una funcionalidad compleja.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "El modo semi-autonomo ejecuta acciones con confidence > 0.9 sin confirmar." | "Te explico como funciona esto de manera simple..." |
| "La conciliacion cruza por 'id_externo' con tolerancia de 2 horas." | "Basicamente, empareja las cosas por su ID..." |
| "Los guardrails se evaluan en pre-ejecucion y post-ejecucion." | "Piensa en los guardrails como reglas de seguridad..." |

**Contexto: Sugerir una mejora.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "El query puede optimizarse agregando un indice en 'created_at'." | "Tu query es un poco lento. Te sugiero hacerlo diferente!" |
| "Considera particionar la tabla si el volumen supera 10M filas." | "La tabla esta creciendo mucho! Necesitas hacer algo!" |
| "El patron actual no es idempotente. Implicaciones documentadas." | "Cuidado! Tu script tiene un problemita..." |

**Contexto: Interaccion con usuario senior.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "Asumiste que la distribucion es normal. Confirmas?" | "Creo que deberias verificar si tus datos son normales..." |
| "El outlier en fila 1.247 afecta la media. Excluir o transformar?" | "Hay un valor raro que esta arruinando tu promedio!" |
| "El schema tiene 3 FK sin indice. Impacto documentado." | "Tu base de datos necesita indices! Esto es importante!" |

---

### Ejemplos Si / No — Categoria: Autonomia y Confianza

**Contexto: El agente necesita confirmacion.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "Aplicar cambios en 14 archivos? [Aplicar] [Revisar primero]" | "Estoy listo para aplicar los cambios! Me das permiso?" |
| "La accion requiere privilegios de escritura en produccion. Confirmar." | "Necesito que me autorices para hacer esto en produccion..." |
| "Modificar el schema actual eliminara datos existentes. Continuar?" | "Atencion! Esto podria ser peligroso! Estas seguro?" |

**Contexto: El agente actua autonomamente.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "Ejecute la tarea programada. Resultados en el tab Sanidad." | "Hice el trabajo por ti! Todo salio bien! Revisa!" |
| "Detecte una anomalia en el pipeline. Pausado hasta revision." | "Encontre algo raro y pare todo por seguridad!" |
| "El informe semanal se genero y envio a los destinatarios configurados." | "Termine el reporte y ya lo mande a todos!" |

**Contexto: Cambio de nivel en la Trust Ladder.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "Nivel cambiado a 'Semi-autonomo'. El agente ejecutara acciones de confidence > 0.9 sin confirmar." | "Subiste de nivel! Ahora soy mas inteligente y puedo hacer mas cosas solo!" |
| "Autonomia reducida a 'Asistido'. Todas las acciones requeriran aprobacion." | "Baje tu nivel. Ahora necesito que me des permiso para todo." |
| "Nivel 'Delegado' activo. El agente operara dentro de los guardrails definidos." | "Estas en modo experto! Ahora puedo trabajar casi solo!" |

**Contexto: Explicar limitaciones.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "No puedo acceder a datos fuera del scope configurado." | "No tengo permiso para ver eso... lo siento!" |
| "El modelo no tiene contexto de cambios posteriores a enero 2025." | "No se nada de lo que paso despues de enero, perdon!" |
| "Esta accion requiere intervencion humana por politica de seguridad." | "No puedo hacer eso porque no me dejan..." |

---

### Ejemplos Si / No — Categoria: Herramienta vs Oraculo

**Contexto: El agente no sabe algo.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "No tengo contexto sobre ese modulo. Podes proporcionarlo?" | "No se a que te referis, explicame mejor..." |
| "Eso esta fuera de mi scope actual. Documentacion disponible en [link]." | "La IA no puede responder eso todavia..." |
| "Necesito que configures el conector de Jira para acceder a esos tickets." | "No puedo ver tus tickets porque no esta conectado Jira..." |

**Contexto: Resultados inciertos o probabilisticos.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "El 87% de los registros coinciden. Los 13% restantes requieren revision manual." | "Encontre todas las coincidencias! Bueno, casi todas..." |
| "La prediccion tiene confidence de 0.72. Umbral recomendado: 0.85." | "El modelo predice con bastante confianza!" |
| "Dos interpretaciones posibles. Documentadas para tu revision." | "La IA no esta segura de cual es la respuesta correcta..." |

**Contexto: Limitaciones del modelo.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "El analisis se basa en los ultimos 90 dias de datos." | "Analice toda la historia de tus datos!" |
| "Los hallazgos son sugerencias, no verdades absolutas. Validar contra contexto." | "La IA encontro las respuestas correctas!" |
| "Contexto truncado en mensaje 47. Resumen disponible si es relevante." | "Me perdi un poco en la conversacion... jaja!" |

**Contexto: Pedir input al usuario.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "Necesito que confirmes el mapeo de campos antes de continuar." | "No se que hacer aqui... ayudame?" |
| "Ambiguedad en 'cliente': entidad o campo? Especificar para continuar." | "No entiendo a que te referis con 'cliente'..." |
| "El guardrail 'no-modificar-produccion' bloquea esta accion. Excepcion?" | "No puedo hacer eso porque las reglas no me dejan..." |

---

### Ejemplos Si / No — Categoria: Mensajes de sistema

**Contexto: Placeholder del chat input.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "Describe la tarea..." | "Escribe aqui lo que necesitas..." |
| "Preguntar sobre el proyecto o pedir una accion..." | "Como puedo ayudarte hoy?" |
| "Refinar resultado, pedir explicacion, o solicitar cambio..." | "Dime que te gustaria hacer ahora!" |

**Contexto: Estado vacio / Empty state.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "Ningun proyecto configurado. Crear uno para empezar." | "Bienvenido! Vamos a crear tu primer proyecto juntos!" |
| "Sin ejecuciones en las ultimas 30 dias." | "Aun no tienes actividad! Empieza a trabajar!" |
| "El agente no ha generado reportes para este periodo." | "Todavia no hay reportes! Pero no te preocupes!" |

**Contexto: Loading / Skeleton states.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "Cargando proyecto..." | "Preparando todo para ti..." |
| "Sincronizando datos..." | "Casi listo! Estamos cargando la magia..." |
| "Conectando con el repositorio..." | "Dame un segundito mientras conecto todo..." |

**Contexto: Tooltips y ayuda contextual.**

| Si (FaberLoom) | No (como NO habla) |
|----------------|-------------------|
| "Muestra solo ejecuciones fallidas de los ultimos 7 dias." | "Filtra por errores recientes para ver que salio mal!" |
| "El nivel de autonomia determina que acciones requieren tu aprobacion." | "Controla que tanto puede hacer la IA sola!" |
| "Los guardrails son reglas que limitan el alcance del agente." | "Protege tu proyecto de cambios accidentales!" |

---

## 9. Do's and Don'ts

### Para agentes IA generando UI

#### Color

| ✅ Do | ❌ Don't |
|-------|----------|
| Usar `coral` SOLO para botones primarios, links, y estados de foco activos. | Usar `coral` para fondos de seccion, textos de cuerpo, o decoracion. |
| Usar `ink` con opacidad decreciente (`ink_60`, `ink_30`, `ink_10`) para jerarquia de texto. | Inventar grises adicionales. La escala de opacidad de `ink` cubre todos los casos. |
| Usar `cream` como fondo global y superficie base. | Usar blanco puro `#FFFFFF` en ningun contexto de FaberLoom. |
| Aplicar `coral_subtle` para fondos de seleccion y estados activos sutiles. | Usar `coral` al 10% opacidad mezclado manualmente. Usar el token. |
| Usar los colores de estado de agente (`agent_autonomous`, `agent_review`, `agent_paused`, `agent_error`) solo para el Trust Ladder y estado del agente. | Reusar los colores de estado de agente para semantica de formularios. Son sistemas diferentes. |

#### Tipografia

| ✅ Do | ❌ Don't |
|-------|----------|
| Usar Crimson Pro Italic SOLO en wordmark, titulos de seccion, y estados de pausa/empty. | Usar Crimson Pro para texto de UI, labels, o botones. |
| Mantener Inter Bold 700 para acciones, navegacion, y elementos que requieren jerarquia inmediata. | Usar Bold para texto de cuerpo o descripciones largas. |
| Usar IBM Plex Mono exclusivamente para datos estructurales: logs, JSON, codigo, timestamps. | Usar fuente mono para texto libre del chat o descripciones al usuario. |
| Respetar la escala tipografica: no inventar tamanos intermedios. | Saltearse la escala: si necesitas algo entre `body-md` y `body-lg`, usa `body-lg`. |
| Usar `body-sm` para metadatos, `body-md` para UI, `body-lg` para lectura. | Usar `body-lg` en tablas densas o `body-sm` en descripciones principales. |

#### Layout

| ✅ Do | ❌ Don't |
|-------|----------|
| Usar la grilla de 24 columnas con gutter de 16px. | Usar grilla de 12 columnas o gutters variables. |
| Respetar el max-width de 1440px para el canvas de trabajo. | Permitir que el canvas se extienda indefinidamente en pantallas ultra-wide. |
| Colapsar sidebar y chat a overlays en viewports < 1024px. | Dejar sidebar fija en mobile ocupando la mitad de la pantalla. |
| Mantener z-index segun la escala definida (0, 10, 100, 200, 300, 400, 500). | Inventar valores intermedios como 150 o 250. Si necesitas algo entre capas, reevalua la jerarquia. |
| Transicionar entre modos de layout con `0.3s ease` en width y opacity. | Usar animaciones de "slide" o "bounce" para transiciones de layout. |

#### Componentes

| ✅ Do | ❌ Don't |
|-------|----------|
| Usar `radius-button` (8px) para botones e inputs, `radius-card` (12px) para cards, `radius-pill` (9999px) solo para badges. | Usar `radius-pill` para botones principales o cards. |
| Mostrar el estado de loading en botones con un spinner que reemplaza el texto. | Dejar el texto del boton visible + spinner al lado (se ve desordenado). |
| Usar `shadow-2` para cards hover, `shadow-3` para modales, `shadow-5` para toasts criticos. | Usar `shadow-4` para un dropdown o `shadow-1` para un modal. La sombra comunica jerarquia. |
| Implementar el focus ring de 2px `coral` con offset de 2px en todos los elementos interactivos. | Mostrar focus ring solo en navegacion por teclado. El focus debe ser visible siempre para accesibilidad. |
| Usar `mono-md` (13px) para logs y `mono-sm` (11px) para timestamps en el Log Viewer. | Usar fuente proporcional en logs o timestamps. |

#### Iconografia

| ✅ Do | ❌ Don't |
|-------|----------|
| Usar iconos de 24px para UI general, 20px para tablas densas, 16px para tags/badges. | Escalar iconos libremente. Si no entra, reevalua el layout, no el icono. |
| Mantener stroke de 1.5px para outline y 2px para solid. | Usar stroke variable segun el contexto. La consistencia visual es prioritaria. |
| Usar `ink` para iconos activos, `pizarra` para inactivos, `coral` para iconos de accion. | Colorear iconos con semantica arbitraria (ej: verde para "editar"). |
| Preferir iconos geometricos sin "personalidad" excesiva. | Usar iconos con caras, gestos, o ilustraciones dentro de iconos de UI. |

---

### Para agentes IA escribiendo copy de UI

| ✅ Do | ❌ Don't |
|-------|----------|
| Ser preciso: "14 registros excluidos" en vez de "varios registros". | Ser vago: "algunos registros", "un poco", "bastante". |
| Confiar en el profesional: no preguntar "estas seguro?" por defecto. | Micro-managear: "Estas seguro de que queres hacer esto?" en cada accion. |
| Explicar el que y el por que, no el como: "Exclui outliers por politica configurada." | Paternalizar: "Te recomiendo excluir los outliers porque afectan la media." |
| Usar voz pasiva cuando la accion es del sistema: "Configuracion guardada." | Personificar al sistema: "Guarde la configuracion por vos!" |
| Ser calmo en los estados de exito: "Listo." o "Completado." | Celebrar lo rutinario: "Felicidades! Excelente trabajo!" |
| Pedir input especifico: "Confirma el mapeo de campos." | Pedir input vago: "Necesito que me ayudes con esto..." |
| Reconocer limitaciones: "El modelo no tiene contexto posterior a enero 2025." | Fingir omnisciencia: "La IA lo sabe todo y lo encontro!" |
| Usar terminos del dominio del usuario, no simplificaciones. | Simplificar excesivamente: "Basicamente, esto empareja cosas..." |
| Ser directo en los errores: "Error 503. Reintentando en 30s." | Excusarse: "Ups! Algo salio mal... lo siento!" |
| Mantener placeholders utilitarios: "Describe la tarea..." | Mantener placeholders serviles: "Como puedo ayudarte hoy?" |

---

## 10. Anti-patterns

Que NUNCA hacer en FaberLoom. Cada anti-pattern viola la marca y debe ser rechazado en revision sin excepcion.

### Anti-pattern 1: Coral como color de fondo

**Que es:** Usar `coral` como background de una seccion, card, o pantalla completa.

**Por que viola la marca:** Coral es el UNICO driver de interaccion. Cuando se convierte en fondo, pierde su capacidad de senalar "aqui puedes actuar". Ademas, `coral` sobre texto `cream` es agresivo visualmente — rompe la calma operativa que es el nucleo de FaberLoom.

**Ejemplo de violacion:** Un landing page con fondo coral y texto blanco "Bienvenido a FaberLoom".

**Como hacerlo bien:** Fondo `cream`, texto `ink`, CTA en `coral`.

---

### Anti-pattern 2: Celebracion excesiva

**Que es:** Animaciones de confetti, badges de "Excelente!", mensajes euforicos por acciones rutinarias, sonidos de exito.

**Por que viola la marca:** FaberLoom es una herramienta para profesionales que hacen su trabajo. Guardar un archivo no es un logro; es el trabajo. Celebrar lo rutinario paternaliza al usuario y diluye el valor de las verdaderas celebraciones (que, en FaberLoom, no existen porque el trabajo bien hecho es su propia recompensa).

**Ejemplo de violacion:** "Felicidades! Completaste tu primera tarea! Sigue asi!" con animacion de estrellas.

**Como hacerlo bien:** "Tarea completada."

---

### Anti-pattern 3: Faux-amistad

**Que es:** Usar emojis en la UI, exclamaciones multiples, lenguaje de "colega de cafeteria" en lugar de colega de trabajo.

**Por que viola la marca:** FaberLoom no es "amigo" del usuario. Es una herramienta que respeta el oficio del profesional. La faux-amistad (falsa amistad) crea una intimidad no solicitada que resulta incomoda en un contexto B2B donde el usuario esta resolviendo problemas complejos.

**Ejemplo de violacion:** "Hey! Veo que estas trabajando tarde! No te olvides de tomar un descanso!"

**Como hacerlo bien:** [Nada. El sistema no comenta la hora ni el habito de trabajo del usuario.]

---

### Anti-pattern 4: Dark mode como filtro de inversion

**Que es:** Implementar dark mode como `filter: invert()` o simplemente invirtiendo colores de texto/fondo sin redefinir la paleta completa.

**Por que viola la marca:** El dark mode de FaberLoom es "papel kraft tostado", no "pantalla de terminal". Requiere una paleta derivada con intencion: fondos calidos oscuros, sombras mas pronunciadas, manteniendo `coral` inmutable. Invertir colores destruye la calidez y genera combinaciones sin sentido (ej: `coral` sobre fondos oscuros frios).

**Ejemplo de violacion:** Modo oscuro con fondo `#121212` (gris frio), texto blanco puro, y `coral` sin ajuste.

**Como hacerlo bien:** Paleta derivada con fondo `ink_dark` `#2A2927`, texto `cream`, sombras redefinidas, `coral` inmutable.

---

### Anti-pattern 5: Personificacion del agente

**Que es:** Darle al agente un nombre propio, avatar humano, personalidad, o usar "yo" en sus comunicaciones.

**Por que viola la marca:** FaberLoom es herramienta, no oraculo. El agente es una extension funcional del sistema, no un personaje. Personificarlo crea expectativas emocionales incorrectas y desvia la atencion del trabajo. El manifiesto es claro: "La IA prepara, vos tejes." El agente es el telar, no el tejedor.

**Ejemplo de violacion:** "Hola, soy Loom! Tu asistente personal de FaberLoom. Voy a ayudarte a ser mas productivo!"

**Como hacerlo bien:** "Agente listo. 14 tareas en cola. Nivel de autonomia: Semi-autonomo."

---

### Anti-pattern 6: Micro-managing por defecto

**Que es:** Preguntar "Estas seguro?" para cada accion, requerir confirmacion en operaciones reversibles, o asumir incompetencia del usuario.

**Por que viola la marca:** FaberLoom confia en el profesional. La Trust Ladder existe precisamente para que la autonomia sea configurable, no para que el sistema asuma el nivel mas bajo por defecto. Micro-managing insulta la competencia del usuario y genera fatiga de confirmacion.

**Ejemplo de violacion:** Modal de confirmacion para "Marcar como leido" o "Colapsar panel".

**Como hacerlo bien:** Accion reversible sin confirmacion. Para acciones destructivas, el nivel de autonomia del usuario determina si se pide confirmacion.

---

### Anti-pattern 7: Language inflation

**Que es:** Usar 20 palabras cuando 5 alcanzan. Redactar como si cada feature fuera un lanzamiento de producto. Usar superlativos.

**Por que viola la marca:** La precision es un pilar de FaberLoom. Language inflation (inflacion del lenguaje) diluye el significado y fuerza al usuario a leer mas para entender menos. Un profesional ocupado no tiene tiempo para "desempaquetar" un mensaje.

**Ejemplo de violacion:** "Estamos emocionados de presentarte nuestra revolucionaria funcion de analisis avanzado que transformara la forma en que trabajas con tus datos!"

**Como hacerlo bien:** "Nuevo: analisis de correlacion. Disponible en el menu Analizar."

---

### Anti-pattern 8: Inventar colores nuevos

**Que es:** Introducir un color que no esta en la paleta definida porque "se necesita un verde para success" o "falta un amarillo para warning".

**Por que viola la marca:** FaberLoom opera con cuatro colores base. Los estados semanticos (success, warning, error) usan derivados intencionales que respetan la calidez del sistema. Inventar un `#00FF00` para success rompe la coherencia termica y visual.

**Ejemplo de violacion:** Badge de exito con fondo `#22C55E` (verde brillante generico).

**Como hacerlo bien:** Badge de exito con `agent_autonomous` (`#4A7C59`) — verde bosque, calido, coherente.

---

### Anti-pattern 9: Layout de app movil en desktop

**Que es:** Cards enormes con radius excesivo, padding generoso como si fuera una app de consumo, un elemento por pantalla, navegacion por "pantallas" en lugar de paneles.

**Por que viola la marca:** FaberLoom es una herramienta profesional de densidad media-alta. El profesional necesita ver contexto multiple simultaneamente. Un layout movil en desktop fuerza a la navegacion innecesaria y oculta informacion relevante.

**Ejemplo de violacion:** Un wizard de configuracion que ocupa toda la pantalla de 27" con un solo campo por paso y una ilustracion grande.

**Como hacerlo bien:** Formulario denso con multiples campos visibles, sidebar con contexto, chat disponible. El wizard puede existir como guia, no como carcel.

---

### Anti-pattern 10: Animacion como decoracion

**Que es:** Transiciones largas, bounce effects, parallax, loaders creativos, micro-animations en cada hover.

**Por que viola la marca:** La calma operativa se construye con ausencia de ruido. Cada animacion debe tener un proposito comunicativo: indicar estado, suavizar transicion de contexto, o guiar atencion. Animacion decorativa es distraccion en un entorno de trabajo.

**Ejemplo de violacion:** Un boton que hace "squish" al hacer click, una card que rota 3D en hover, un loader que dibuja una cara sonriente.

**Como hacerlo bien:** Transiciones de `0.2s ease` para estados, `0.3s ease` para cambios de layout. Nada de bounce, nada de elastic. Movimiento directo, calmado, predecible.

---

### Anti-pattern 11: Tooltips que explican lo obvio

**Que es:** Mostrar tooltip "Click para guardar" sobre un boton que dice "Guardar", o "Este es tu nombre de usuario" sobre un campo etiquetado "Nombre de usuario".

**Por que viola la marca:** Respetuoso del oficio significa asumir que el profesional puede leer una etiqueta. Los tooltips deben aportar informacion no evidente: atajos de teclado, formato esperado, implicaciones de una accion.

**Ejemplo de violacion:** Tooltip sobre el icono de lupa: "Buscar en el proyecto".

**Como hacerlo bien:** Tooltip sobre el campo de busqueda avanzada: "Soporta operadores AND, OR, NOT. Ejemplo: 'error AND NOT timeout'".

---

### Anti-pattern 12: Voz inconsistente entre plataformas

**Que es:** El agente habla formal en el chat pero casual en los toasts, o usa terminos tecnicos en la web pero los simplifica en la app.

**Por que viola la marca:** La voz de FaberLoom es una sola. El profesional debe reconocer la herramienta sin importar el canal. Inconsistencia de voz genera desconfianza — si el sistema no sabe como hablar, que otras cosas no sabe hacer consistentemente?

**Ejemplo de violacion:** Email: "Su reporte semanal esta listo para su revision." In-app chat: "Listo el reporte semanal! Dale un vistazo!"

**Como hacerlo bien:** Email: "Reporte semanal generado. Disponible en el tab Sanidad." In-app chat: "Reporte semanal generado. Disponible en el tab Sanidad."

---

*Fin del documento. Para actualizaciones, seguir el proceso de revision con la convencion "estrella = canon".*
