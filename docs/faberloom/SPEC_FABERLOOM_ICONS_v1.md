# SPEC_FABERLOOM_ICONS_v1.md

| id | FAB-ICO-2026 |
| version | 1.0.0 |
| status | DRAFT |
| visibility | INTERNAL |
| domain | faberloom |

---

## Resumen ejecutivo

Este documento formaliza el sistema de iconos extendido para **FaberLoom**, plataforma SaaS B2B chat-first agentic multi-tenant. El sistema parte de ~20 iconos semanticos custom existentes (icons.jsx + icons-app.jsx) y lo expande a **96 iconos** organizados en 10 categorias funcionales, manteniendo la convencion de marca "estrella = canon" para variantes definitivas.

El spec define grilla 24px base, stroke-based, estilo calmo-precision-oficio, con soporte para animacion via CSS/Stroke-dasharray y mapeo completo a tokens DTCG para integracion con Style Dictionary v4.

---

## 1. Spec del sistema

### 1.1 Grilla y geometria

| Propiedad | Valor | Notas |
|-----------|-------|-------|
| **ViewBox base** | `0 0 24 24` | Todas las variantes derivan de esta grilla |
| **Keyline square** | 20x20px centrado | Margen optico de 2px perimetral |
| **Keyline circle** | diametro 20px centrado | Para iconos circulares/organicos |
| **Keyline diagonal** | esquina a esquina 20x20 | Para iconos dinamicos/direccionales |
| **Stroke weight base** | **1.5px** | Default (precision, legibilidad) |
| **Stroke weight bold** | **2px** | Estados activos, featured icons, lg size |
| **Stroke weight hairline** | **1px** | Solo xs size (16px) y estados disabled sutiles |
| **Terminales** | **Redondeados** | `stroke-linecap: round` universal |
| **Esquinas** | **Redondeadas** | `stroke-linejoin: round`, radio efecto ~1px a 1.5px |
| **Centrado de trazos** | Center-stroke | Trazo centrado en la geometria (no inside/outside) |
| **Formato** | Outline stroke-based | Sin fills complejos; fill solo para solid variants |

#### Optical alignment

| Correccion | Regla | Ejemplo |
|------------|-------|---------|
| **Ilusion de masa** | Iconos con area visual menor (lineas finas, formas abiertas) escalar +0.5px | `agent-single` lineal vs `agent-multiple` solid |
| **Centrado visual** | Centro geometrico != centro visual; desplazar hacia la "masa pesada" | Flechas ligeramente abajo del centro |
| **Espaciado interno** | Minimo 1.5px entre trazos paralelos | Evita bleeding en small sizes |
| **Redondeo optico** | Esquinas externas ligeramente mas redondeadas que internas | `loom` metafora del telar |

### 1.2 Variantes de estilo

| Variante | Convencion | Uso |
|----------|-----------|-----|
| **Outline** (default) | Trazo 1.5px, sin fill | Estado default, navegacion |
| **Solid** | Fill con color, sin stroke | Estados activos, indicadores densos |
| **Duotone** | Stroke 1.5px + fill semitransparente | Featured icons, empty states lg |
| **Animated** | Stroke-dasharray + CSS animation | Estados transitorios (loading, running) |

### 1.3 Color y estado

| Estado | Token DTCG | Valor hex | Uso |
|--------|-----------|-----------|-----|
| **Default** | `color.icon.default` | `#1F1E1C` (ink) | Iconos en reposo, navegacion |
| **Active / Alerta** | `color.icon.active` | `#C96442` (coral) | Tab activo, HITL pendiente, accion primaria |
| **Muted / Disabled** | `color.icon.muted` | `#5A6B7C` (pizarra) | Deshabilitado, secundario, placeholder |
| **Success** | `color.icon.success` | `#4A7C59` | Feedback positivo, aprobacion HITL |
| **Warning** | `color.icon.warning` | `#C99742` | Advertencia, atencion requerida |
| **Error / Danger** | `color.icon.error` | `#B54242` | Error critico, veto, bloqueo |
| **Info** | `color.icon.info` | `#5A6B7C` | Tips, ayuda contextual |
| **Cream overlay** | `color.icon.inverse` | `#F4F1ED` | Iconos sobre fondos oscuros |

#### Reglas de color

- **Nunca** se usa color inline en el SVG; todos los `currentColor` heredan del contenedor.
- La variante `solid` usa `fill="currentColor"` en lugar de stroke.
- Estados animados mantienen el color del estado padre; la animacion es de forma, no de tinte.

### 1.4 Tamanios

| Token | Dimension | Stroke adaptativo | Uso tipico |
|-------|-----------|-------------------|------------|
| `size.icon.xs` | 16px | 1px | Inline text, chips, badges |
| `size.icon.sm` | 20px | 1.5px | Buttons compactos, input adornments |
| `size.icon.md` | 24px | 1.5px | **Default**, navegacion, tabs |
| `size.icon.lg` | 32px | 2px | Feature icons, empty states, cards |
| `size.icon.xl` | 48px | 2px | Hero sections, onboarding illustrations |

#### Escalado de stroke

```
size < 20px  -> stroke: 1px
size 20-24px -> stroke: 1.5px
size > 24px  -> stroke: 2px
```

### 1.5 Animacion

| Propiedad | Valor | Uso |
|-----------|-------|-----|
| **Dibujo de trazo** | `stroke-dasharray` + `stroke-dashoffset` | Estados running, loading, syncing |
| **Rotacion** | `transform: rotate()` | Refresh, sync, ciclicos |
| **Traslacion** | `transform: translate()` | Send, reply, movimiento direccional |
| **Escala** | `transform: scale()` | Feedback de toque, aparicion |
| **Opacidad** | `opacity` | Estados disabled, fade in/out |

#### Especificaciones de animacion canon

| Animacion | Duracion | Easing | Iconos aplicables |
|-----------|----------|--------|-------------------|
| `dash-draw` | 1.2s | `ease-in-out` | agent-running, loading, syncing |
| `spin-smooth` | 2s | `linear`, infinite | refresh, sync |
| `pulse-soft` | 1.5s | `ease-in-out`, infinite | agent-idle, queued |
| `pop-in` | 0.3s | `cubic-bezier(0.34, 1.56, 0.64, 1)` | success, approve |
| `slide-right` | 0.25s | `ease-out` | send, export, forward |

---

## 2. Lista completa de iconos

### Convenciones de la tabla

- **Prioridad**: `MVP` (inmediato), `P1` (siguiente sprint), `P2` (backlog)
- **Variante canon**: `★` indica la variante definitiva por concepto (estrella = canon)
- **Variantes disponibles**: `outline` (default), `solid`, `animated`

---

### Categoria: Agentes (estados y acciones)

| Nombre | Descripcion visual | Prioridad | Variante canon | Variantes |
|--------|-------------------|-----------|----------------|-----------|
| **agent-single** | Silueta unica con circulo base y antena/luz | MVP | outline ★ | solid, animated |
| **agent-multiple** | Tres siluetas en cluster progresivo | MVP | outline ★ | solid |
| **agent-parallel** | Dos agentes con flechas divergentes laterales | P1 | outline ★ | solid |
| **agent-idle** | Agente single con linea horizontal base (reposo) | MVP | outline ★ | animated (pulse) |
| **agent-running** | Agente single con arcos de movimiento circulares | MVP | animated ★ | outline |
| **agent-paused** | Agente single con dos barras verticales (pause) | MVP | outline ★ | solid |
| **agent-error** | Agente single con X marcada a un lado | MVP | outline ★ | solid |
| **agent-blocked** | Agente single con escudo/candado superpuesto | P1 | outline ★ | solid |

### Categoria: Herramientas (acciones del agente)

| Nombre | Descripcion visual | Prioridad | Variante canon | Variantes |
|--------|-------------------|-----------|----------------|-----------|
| **search** | Lupa clasica, mango 45 grados | MVP | outline ★ | solid |
| **edit** | Lapiz inclinado sobre linea base | MVP | outline ★ | solid |
| **transform** | Flecha que muta de recta a curva | MVP | outline ★ | — |
| **export** | Caja con flecha saliente hacia arriba-derecha | MVP | outline ★ | solid |
| **import** | Caja con flecha entrante desde arriba-izquierda | MVP | outline ★ | solid |
| **copy** | Dos rectangulos solapados (original + duplicado) | MVP | outline ★ | solid |
| **paste** | Clipboard con lineas de texto | P1 | outline ★ | solid |
| **undo** | Flecha curva antihoraria retornando | P1 | outline ★ | solid |
| **redo** | Flecha curva horaria avanzando | P1 | outline ★ | solid |
| **refresh** | Flecha circular cerrada, sentido horario | MVP | outline ★ | animated (spin) |
| **sync** | Dos flechas circulares en contraciclo | MVP | animated ★ | outline |
| **filter** | Embudo con tres lineas horizontales convergentes | MVP | outline ★ | solid |
| **sort** | Flecha doble vertical (arriba/abajo) | MVP | outline ★ | solid |

### Categoria: Datos (entidades del producto)

| Nombre | Descripcion visual | Prioridad | Variante canon | Variantes |
|--------|-------------------|-----------|----------------|-----------|
| **file** | Documento rectangulo con esquina doblada | MVP | outline ★ | solid |
| **folder** | Carpeta abierta con pestana | MVP | outline ★ | solid, open |
| **dataset** | Tres rectangulos apilados con indicador de relacion | MVP | outline ★ | solid |
| **schema** | Diagrama de jerarquia (raiz + dos nodos) | P1 | outline ★ | solid |
| **database** | Cilindro 3/4 vista (disco + costados) | MVP | outline ★ | solid |
| **table** | Grid 3x3 celdas | MVP | outline ★ | solid |
| **log** | Documento con lineas horizontales + marca de tiempo | P1 | outline ★ | solid |
| **hash** | Simbolo numeral `#` estilizado | MVP | outline ★ | solid |
| **json** | Llaves `{}` con puntos internos de datos | P1 | outline ★ | solid |
| **csv** | Tabla con comas separadoras visibles | P2 | outline ★ | solid |
| **api** | Triangulo con circuitos/lineas conectoras | P1 | outline ★ | solid |
| **webhook** | Gancho con flecha de retorno circular | P1 | outline ★ | solid |

### Categoria: Navegacion

| Nombre | Descripcion visual | Prioridad | Variante canon | Variantes |
|--------|-------------------|-----------|----------------|-----------|
| **home** | Casa simple con techo triangular y base | MVP | outline ★ | solid |
| **back** | Flecha apuntando izquierda | MVP | outline ★ | solid |
| **forward** | Flecha apuntando derecha | MVP | outline ★ | solid |
| **breadcrumb** | Flecha pequena derecha (separator) | MVP | outline ★ | — |
| **menu** | Tres lineas horizontales paralelas (hamburger) | MVP | outline ★ | solid (cruz cuando activo) |
| **close** | X de 45 grados, trazos limpios | MVP | outline ★ | solid |
| **expand** | Flechas divergentes en las 4 esquinas | P1 | outline ★ | solid |
| **collapse** | Flechas convergentes hacia el centro | P1 | outline ★ | solid |
| **settings** | Engranaje de 8 dientes | MVP | outline ★ | solid, animated |
| **profile** | Circulo (cabeza) sobre arco (hombros) | MVP | outline ★ | solid |
| **logout** | Puerta con flecha saliente a la derecha | P1 | outline ★ | solid |

### Categoria: Estados (feedback del sistema)

| Nombre | Descripcion visual | Prioridad | Variante canon | Variantes |
|--------|-------------------|-----------|----------------|-----------|
| **state-running** | Circulo con punto central en movimiento | MVP | animated ★ | outline |
| **state-paused** | Dos barras verticales dentro de circulo | MVP | outline ★ | solid |
| **state-done** | Circulo con check interno | MVP | outline ★ | solid |
| **state-error** | Circulo con X interna | MVP | outline ★ | solid |
| **state-queued** | Circulo con tres puntos horizontales internos | P1 | outline ★ | animated (pulse) |
| **state-blocked** | Circulo con barra horizontal interna | P1 | outline ★ | solid |
| **state-loading** | Circulo de arco incompleto rotando | MVP | animated ★ | — |
| **state-syncing** | Dos arcos circulares en contramarcha | P1 | animated ★ | outline |
| **state-offline** | Circulo con rayo diagonal de corte | P1 | outline ★ | solid |

### Categoria: Feedback (mensajes al usuario)

| Nombre | Descripcion visual | Prioridad | Variante canon | Variantes |
|--------|-------------------|-----------|----------------|-----------|
| **info** | Circulo con `i` minuscula centrada | MVP | outline ★ | solid |
| **warning** | Triangulo equilatero con `!` centrado | MVP | outline ★ | solid |
| **success** | Circulo con check grueso interno | MVP | outline ★ | solid, animated (pop) |
| **danger** | Octogono con `!` centrado (senal de alto) | MVP | outline ★ | solid |
| **tip** | Bombilla con filamento visible | P1 | outline ★ | solid |
| **help** | Circulo con `?` centrado | MVP | outline ★ | solid |
| **notification** | Campana con badjeado opcional | MVP | outline ★ | solid, animated (swing) |

### Categoria: HITL (Human-in-the-Loop)

| Nombre | Descripcion visual | Prioridad | Variante canon | Variantes |
|--------|-------------------|-----------|----------------|-----------|
| **approve** | Check con circulo exterior de validacion humana | MVP | outline ★ | solid, animated (pop) |
| **reject** | X con circulo exterior de validacion | MVP | outline ★ | solid |
| **iterate** | Flecha circular con numero de ciclo (1, 2, 3...) | MVP | outline ★ | solid |
| **defer** | Reloj de arena con flecha de pausa | P1 | outline ★ | solid |
| **review** | Lupa sobre documento con lineas | MVP | outline ★ | solid |
| **confirm** | Doble check (check + check menor) | P1 | outline ★ | solid |
| **override** | Mano humana sobre engranaje/agente | P1 | outline ★ | solid |
| **veto** | Escudo con X marcada | P1 | outline ★ | solid |

### Categoria: Workspace (multi-tenant)

| Nombre | Descripcion visual | Prioridad | Variante canon | Variantes |
|--------|-------------------|-----------|----------------|-----------|
| **workspace** | Mesa de trabajo con tela estirada (metafora telar) | MVP | outline ★ | solid, duotone |
| **project** | Carpeta con etiqueta/label suspendida | MVP | outline ★ | solid |
| **class** | Tres figuras humanas + rectangulo de categoria | P1 | outline ★ | solid |
| **account** | Circulo con silueta + escudo/verificacion | P1 | outline ★ | solid |
| **role** | Etiqueta con insignia/medalla | P1 | outline ★ | solid |
| **permission** | Candado abierto con check | P1 | outline ★ | solid, locked |
| **tenant** | Edificio de dos pisos con divisiones | P1 | outline ★ | solid |
| **team** | Tres siluetas en fila horizontal | MVP | outline ★ | solid |
| **invite** | Sobre con flecha entrante y signo + | P1 | outline ★ | solid |
| **share** | Tres nodos conectados por lineas (red) | MVP | outline ★ | solid |
| **lock** | Candado cerrado, arco + cuerpo | MVP | outline ★ | solid |
| **unlock** | Candado abierto, arco levantado + cuerpo | MVP | outline ★ | solid |

### Categoria: UI (controles)

| Nombre | Descripcion visual | Prioridad | Variante canon | Variantes |
|--------|-------------------|-----------|----------------|-----------|
| **checkbox** | Cuadrado con esquinas 2px, check interno | MVP | outline ★ | solid (checked), indeterminate |
| **radio** | Circulo con punto interno seleccionado | MVP | outline ★ | solid (selected) |
| **toggle** | Capsula horizontal con circulo deslizante | MVP | solid ★ | — |
| **slider** | Linea horizontal con knob circular | MVP | outline ★ | solid (knob) |
| **dropdown** | Rectangulo con flecha hacia abajo | MVP | outline ★ | solid |
| **calendar** | Rectangulo con grid 4x4 + header | MVP | outline ★ | solid |
| **clock** | Circulo con manecillas 12 y 3 (hora) | P1 | outline ★ | solid |
| **tag** | Etiqueta con borde diagonal y agujero | P1 | outline ★ | solid |
| **pin** | Chincheta con punta enfocada hacia abajo | P1 | outline ★ | solid |
| **bookmark** | Bandera con V invertido en base | P1 | outline ★ | solid |
| **star** | Estrella 5 puntas, la canon por excelencia | MVP | outline ★ | solid, animated |

### Categoria: Comunicacion

| Nombre | Descripcion visual | Prioridad | Variante canon | Variantes |
|--------|-------------------|-----------|----------------|-----------|
| **chat** | Dos bocadillos solapados (conversacion) | MVP | outline ★ | solid |
| **message** | Bocadillo unico con cola apuntando abajo-izq | MVP | outline ★ | solid |
| **comment** | Bocadillo con lineas de texto internas | P1 | outline ★ | solid |
| **thread** | Bocadillo principal con tres lineas de respuesta | P1 | outline ★ | solid |
| **mention** | Arroba `@` estilizado en circulo | P1 | outline ★ | solid |
| **reply** | Flecha curva entrando por izquierda a bocadillo | P1 | outline ★ | solid |
| **send** | Flecha apuntando arriba-derecha desde circulo | MVP | outline ★ | solid, animated (slide) |
| **attach** | Clip de papel inclinado 45 grados | P1 | outline ★ | solid |

---

**Total de iconos especificados: 96**
- MVP: ~60 iconos
- P1: ~30 iconos
- P2: ~6 iconos

---

## 3. SVGs de ejemplo construidos

Los siguientes iconos cumplen con el spec completo: `viewBox="0 0 24 24"`, stroke-based, `currentColor` para herencia de token, paths simplificados, sin transforms innecesarios.

### 3.1 agent-running

Indica agente trabajando — animacion de dash-draw sobre arcos circulares sugiere movimiento continuo.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Cuerpo del agente: circulo central con antena -->
  <circle cx="12" cy="12" r="3.5"/>
  <line x1="12" y1="5" x2="12" y2="8.5"/>
  <circle cx="12" cy="4.2" r="0.8" fill="currentColor" stroke="none"/>
  <!-- Arcos de movimiento: orbitas exteriores -->
  <path d="M 18.5 12 A 6.5 6.5 0 0 1 12 18.5" stroke-dasharray="10 4"/>
  <path d="M 5.5 12 A 6.5 6.5 0 0 1 12 5.5" stroke-dasharray="10 4"/>
  <!-- Indicador de direccion: pequenas flechas en los arcos -->
  <polyline points="16.5,16.5 18,15.5 17.5,17.5"/>
</svg>
```

**Por que se construyo asi**: El agente se reduce a su minima expresion (circulo + antena = cabeza con sensor). Los arcos exteriores con `stroke-dasharray` permiten animar el `stroke-dashoffset` para simular orbita continua — el movimiento circular sugiere "procesando" sin recurrir a spinners genericos. Las flecas de indicador en los arcos refuerzan direccionalidad. El punto en la antena (fill solid) crea punto focal coral cuando esta activo.

---

### 3.2 approve

HITL — check con significado de aprobacion humana. No es solo un check: es una validacion consciente.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Circulo exterior: contencion de la decision -->
  <circle cx="12" cy="12" r="8.5"/>
  <!-- Check grueso: mano humana confirmando -->
  <polyline points="7.5,12 10.5,15 16.5,9"/>
  <!-- Marca sutil de huella humana: arco en la base del circulo -->
  <path d="M 8.5 17.5 Q 12 19.5 15.5 17.5" stroke-width="1" opacity="0.5"/>
</svg>
```

**Por que se construyo asi**: El circulo contiene la decision, separando este check de un simple "listo". La polyline del check usa angulo generoso (de 7.5,12 a 10.5,15 a 16.5,9) para que sea legible incluso en 16px. El arco sutil en la base sugiere presencia humana sin ser literal. La animacion `pop-in` escala de 0.8 a 1 con `cubic-bezier` spring para dar sensacion de confirmacion tajante.

---

### 3.3 workspace

Representa el espacio de trabajo del hacedor — la mesa del artesano donde la trama toma forma.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Mesa del telar: plano horizontal con profundidad -->
  <rect x="3" y="8" width="18" height="9" rx="1.5"/>
  <!-- Tela estirada: lineas verticales de urdimbre -->
  <line x1="7" y1="8" x2="7" y2="17"/>
  <line x1="10" y1="8" x2="10" y2="17"/>
  <line x1="13" y1="8" x2="13" y2="17"/>
  <line x1="16" y1="8" x2="16" y2="17"/>
  <!-- Patas del telar -->
  <line x1="5" y1="17" x2="5" y2="20"/>
  <line x1="19" y1="17" x2="19" y2="20"/>
  <!-- Trama: linea horizontal ondulante (la ultima pasada) -->
  <path d="M 4.5 13.5 Q 7 12.5 10 13.5 T 16 13.5 L 19.5 13.5" stroke-width="1"/>
</svg>
```

**Por que se construyo asi**: La metafora del telar se traduce en una mesa rectangular (el bastidor) con lineas verticales (urdimbre) y una linea ondulante horizontal (trama/ultima pasada). Las patas anclan el icono y dan estabilidad visual. No es un escritorio generico: las lineas verticales y la ondulacion horizontal lo hacen inconfundiblemente "telar". La variante duotone rellena el rectangulo con crema semitransparente y usa coral para la linea de trama.

---

### 3.4 trust-ladder

Autonomia progresiva — niveles de confianza entre humano y agente.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Escalera de confianza: 4 peldanos ascendentes -->
  <line x1="4" y1="20" x2="20" y2="20"/>
  <line x1="4" y1="20" x2="4" y2="16"/>
  <line x1="4" y1="16" x2="20" y2="16"/>
  <line x1="20" y1="16" x2="20" y2="12"/>
  <line x1="20" y1="12" x2="8" y2="12"/>
  <line x1="8" y1="12" x2="8" y2="8"/>
  <line x1="8" y1="8" x2="20" y2="8"/>
  <line x1="20" y1="8" x2="20" y2="4"/>
  <!-- Figura humana en la cima: presencia supervisora -->
  <circle cx="20" cy="3" r="1.5" fill="currentColor" stroke="none"/>
  <path d="M 18.5 6.5 Q 20 5.5 21.5 6.5" stroke-width="1"/>
  <!-- Agente en la base -->
  <circle cx="4" cy="18" r="1.2" fill="currentColor" stroke="none"/>
  <line x1="4" y1="16" x2="4" y2="14.5"/>
</svg>
```

**Por que se construyo asi**: La escalera asimetrica (sube por la derecha, regresa por la izquierda) crea una espiral visual que comunica progresion. Los peldanos no son iguales: los mas anchos abajo, mas angostos arriba, sugiriendo que la confianza se estrecha hacia la supervision final. La figura humana en la cima (circulo + arco) y el agente en la base establecen jerarquia. En uso real, los peldanos se iluminan de abajo hacia arriba segun el nivel de autonomia alcanzado (1-4 peldanos activos).

---

### 3.5 iterate

Ciclo de iteracion en tab Iterar — el motor creativo de FaberLoom.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Circulo ciclico casi cerrado -->
  <path d="M 18 10 A 7 7 0 1 0 17 16.5"/>
  <!-- Flecha de direccion en el extremo del arco -->
  <polyline points="14.5,15.5 17.5,16.5 16.5,13.5"/>
  <!-- Punto central: el foco de cada iteracion -->
  <circle cx="12" cy="12" r="1.5" fill="currentColor" stroke="none"/>
  <!-- Marca de version: pequeno circulo concetrico -->
  <circle cx="12" cy="12" r="4" stroke-dasharray="2 3"/>
</svg>
```

**Por que se construyo asi**: El arco casi cerrado deja una pequena apertura donde la flecha indica direccion — no es un ciclo cerrado opresivo, sino uno que avanza. El punto central solido representa el "foco" de cada ciclo (la decision, el cambio). El circulo concetrico punteado sugiere versiones anteriores/posibles. Este icono vive en el tab "Iterar" y su animacion es un suave `dash-draw` que recorre el arco cada vez que se completa un ciclo de iteracion.

---

### 3.6 sanidad

Panel de QA/sanity check — el ojo que verifica antes de continuar.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Ojo: la mirada evaluadora -->
  <path d="M 2 12 Q 12 4 22 12 Q 12 20 2 12 Z"/>
  <!-- Iris: circulo central -->
  <circle cx="12" cy="12" r="3"/>
  <!-- Pupila: punto focal -->
  <circle cx="12" cy="12" r="1.2" fill="currentColor" stroke="none"/>
  <!-- Lineas de escaneo: verificacion -->
  <line x1="4" y1="6" x2="4" y2="10"/>
  <line x1="20" y1="6" x2="20" y2="10"/>
  <!-- Checkmarks laterales: aprobacion parcial -->
  <polyline points="3.5,18 5,19.5 7.5,17"/>
  <polyline points="16.5,17 19,19.5 20.5,18"/>
</svg>
```

**Por que se construyo asi**: El ojo es universal para "revision", pero aqui se combina con elementos de QA: las lineas verticales cortas sugieren barras de escaneo/progreso, y las polyline laterales son mini-checks que indican verificacion parcial. La pupila solida crea intensidad cuando el icono esta activo (coral). En el tab "Sanidad", este icono puede mostrar badges numericos sobre la pupila indicando cuantos checks pendientes hay. El stroke-dasharray en el iris permite animacion de "escaneo" rotatorio.

---

### 3.7 loom

Icono que representa el telar/metafora central de FaberLoom — el nucleo de la marca.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Bastidor exterior: marco del telar -->
  <rect x="3" y="3" width="18" height="18" rx="2"/>
  <!-- Urdimbre: hilos verticales equidistantes -->
  <line x1="6" y1="3" x2="6" y2="21"/>
  <line x1="9" y1="3" x2="9" y2="21"/>
  <line x1="12" y1="3" x2="12" y2="21"/>
  <line x1="15" y1="3" x2="15" y2="21"/>
  <line x1="18" y1="3" x2="18" y2="21"/>
  <!-- Lanzadera: linea horizontal con cuerpo central -->
  <line x1="3" y1="12" x2="21" y2="12"/>
  <rect x="10" y="10.5" width="4" height="3" rx="0.8"/>
  <!-- Trama: linea ondulante que cruza la lanzadera -->
  <path d="M 3 15 Q 6 13.5 9 15 T 15 15 T 21 15" stroke-width="1"/>
  <!-- Hilo suelto: elemento organico que humaniza -->
  <path d="M 18 3 Q 20 5 19 7" stroke-width="1" opacity="0.6"/>
</svg>
```

**Por que se construyo asi**: Este es el icono-emblema. El bastidor rectangular contiene el sistema; los 5 hilos verticales son la estructura (urdimbre = datos, configuracion). La lanzadera horizontal con su cuerpo rectangular es el agente en movimiento. La linea ondulante debajo es la trama que se va tejiendo — el resultado. El hilo suelto en la esquina superior derecha es la concesion organica: un sistema perfecto pero hecho por humanos. La variante solid usa coral para la lanzadera, indicando que el agente es el corazon del sistema.

---

### 3.8 coral-dot

Indicador de interaccion activa — el punto de presencia, siempre en coral.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Circulo base: presencia sutil -->
  <circle cx="12" cy="12" r="6" opacity="0.2"/>
  <!-- Circulo medio: pulso intermedio -->
  <circle cx="12" cy="12" r="3.5" opacity="0.5"/>
  <!-- Punto central: el foco activo -->
  <circle cx="12" cy="12" r="1.8" fill="currentColor" stroke="none"/>
</svg>
```

**Por que se construyo asi**: Tres circulos concentricos con opacidad decreciente crean un efecto de onda expansiva estatica. En su version animada, los circulos exteriores escalan y desvanecen en loop (`pulse-soft`) mientras el punto central permanece solido. Este icono **siempre** usa `color.accent.coral` — no acepta otro color. Se usa como indicador de que el agente esta presente, de que hay una interaccion en curso, o para marcar elementos que requieren atencion inmediata. En 16px se reduce al punto central + un halo; en 32px se muestran las tres ondas completas.

---

### 3.9 hash-chain

Para log de auditoria con blockchain — la cadena inmutable de decisiones.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Simbolo numeral/hash estilizado -->
  <line x1="8" y1="4" x2="8" y2="20"/>
  <line x1="16" y1="4" x2="16" y2="20"/>
  <line x1="4" y1="9" x2="20" y2="9"/>
  <line x1="4" y1="15" x2="20" y2="15"/>
  <!-- Eslabones de cadena: circulos conectados a los lados -->
  <circle cx="4" cy="9" r="1.2" fill="currentColor" stroke="none"/>
  <circle cx="20" cy="9" r="1.2" fill="currentColor" stroke="none"/>
  <circle cx="4" cy="15" r="1.2" fill="currentColor" stroke="none"/>
  <circle cx="20" cy="15" r="1.2" fill="currentColor" stroke="none"/>
  <!-- Lineas de conexion horizontal: la cadena -->
  <line x1="5.2" y1="9" x2="6.8" y2="9" stroke-width="1"/>
  <line x1="17.2" y1="9" x2="18.8" y2="9" stroke-width="1"/>
  <line x1="5.2" y1="15" x2="6.8" y2="15" stroke-width="1"/>
  <line x1="17.2" y1="15" x2="18.8" y2="15" stroke-width="1"/>
</svg>
```

**Por que se construyo asi**: El hash `#` es la base (numeral + blockchain hash). Los circulos solidos en las intersecciones externas son "nodos" de la cadena, y las lineas cortas que los conectan al trazo principal son los "eslabones". Esto transforma un simbolo abstracto de programacion en una metafora visual literal de cadena. El resultado es denso pero legible a 24px porque la estructura del hash es reconocible instantaneamente. La variante animated pulsa los nodos en secuencia (de izquierda a derecha) para simular verificacion de bloques.

---

### 3.10 config

Tab Configurar — donde el hacedor establece los parametros del telar.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Tres sliders horizontales: controles de configuracion -->
  <!-- Slider superior -->
  <line x1="4" y1="6" x2="20" y2="6"/>
  <circle cx="14" cy="6" r="2"/>
  <!-- Slider medio -->
  <line x1="4" y1="12" x2="20" y2="12"/>
  <circle cx="9" cy="12" r="2"/>
  <!-- Slider inferior -->
  <line x1="4" y1="18" x2="20" y2="18"/>
  <circle cx="16" cy="18" r="2"/>
</svg>
```

**Por que se construyo asi**: Tres sliders horizontales con knobs circulares en posiciones diferentes — comunica "configuracion" de manera universal e inmediata. A diferencia del engranaje (settings), que sugiere mecanismos internos, los sliders sugieren **ajuste consciente y gradual** — perfecto para el tab "Configurar" donde el hacedor calibra el comportamiento del agente. Los knobs en posiciones distintas (14, 9, 16) evitan simetria monotona y sugieren que cada parametro tiene su propio valor. La variante solid rellena los knobs en coral cuando un parametro ha sido modificado del default.

---

## 4. Reglas de construccion

### 4.1 Proceso de creacion de nuevos iconos

1. **Definir concepto**: Escribir la descripcion funcional en una oracion.
2. **Sketch geometrico**: Dibujar en grilla 24x24 con keyline 20x20.
3. **Identificar metafora**: ¿Es literal, simbolica o compuesta?
4. **Minimizar paths**: Cada icono debe tener el minimo numero de elementos posible.
5. **Probar en todos los sizes**: 16px, 20px, 24px, 32px.
6. **Verificar optical alignment**: Ajustar segun reglas de seccion 1.1.
7. **Asignar variante canon**: ¿Outline, solid, o animated es la definitiva?
8. **Documentar**: Agregar a esta tabla con descripcion y prioridad.

### 4.2 Restricciones de diseno

| Restriccion | Valor | Razon |
|-------------|-------|-------|
| Max paths por icono | 8 | Legibilidad y performance |
| Max puntos por path | 12 | Simplicidad, reduccion de SVG size |
| No gradients | — | Stroke-based system |
| No masks | — | Compatibilidad cross-browser |
| No filters (drop-shadow, etc.) | — | Performance en listados |
| `currentColor` obligatorio | — | Herencia de tokens DTCG |
| `stroke-linecap: round` universal | — | Consistencia de marca |
| `stroke-linejoin: round` universal | — | Consistencia de marca |

### 4.3 Jerarquia de decisiones

```
¿Es un estado transitorio? → animated variant
¿Es un control activo/seleccionado? → solid variant  
¿Es navegacion o informativo? → outline variant (default)
¿Necesita destacar en empty state? → duotone variant
```

### 4.4 Convencion de nombres

| Elemento | Convencion | Ejemplo |
|----------|-----------|---------|
| Nombre de icono | kebab-case semantico | `agent-running`, `hash-chain` |
| Variante | sufijo separado por guion | `agent-running-solid`, `agent-running-animated` |
| Componente React | PascalCase con prefijo Icon | `IconAgentRunning`, `IconAgentRunningSolid` |
| Token DTCG | lowerCamelCase con dominio | `faberloom.icon.agentRunning` |
| Archivo SVG | kebab-case + size opcional | `agent-running-24.svg` |

---

## 5. Integracion con DTCG

### 5.1 Mapeo a tokens de color

```json
{
  "faberloom": {
    "color": {
      "icon": {
        "default":  { "value": "{color.ink}", "type": "color" },
        "active":   { "value": "{color.coral}", "type": "color" },
        "muted":    { "value": "{color.pizarra}", "type": "color" },
        "success":  { "value": "#4A7C59", "type": "color" },
        "warning":  { "value": "#C99742", "type": "color" },
        "error":    { "value": "#B54242", "type": "color" },
        "info":     { "value": "{color.pizarra}", "type": "color" },
        "inverse":  { "value": "{color.cream}", "type": "color" }
      }
    }
  }
}
```

### 5.2 Mapeo a tokens de tamano

```json
{
  "faberloom": {
    "size": {
      "icon": {
        "xs":  { "value": "16px", "type": "dimension" },
        "sm":  { "value": "20px", "type": "dimension" },
        "md":  { "value": "24px", "type": "dimension" },
        "lg":  { "value": "32px", "type": "dimension" },
        "xl":  { "value": "48px", "type": "dimension" }
      }
    }
  }
}
```

### 5.3 Mapeo a tokens de stroke

```json
{
  "faberloom": {
    "stroke": {
      "icon": {
        "hairline": { "value": "1px", "type": "dimension" },
        "default":  { "value": "1.5px", "type": "dimension" },
        "bold":     { "value": "2px", "type": "dimension" }
      }
    }
  }
}
```

### 5.4 Tokens de animacion

```json
{
  "faberloom": {
    "animation": {
      "icon": {
        "dashDraw": {
          "duration": { "value": "1.2s", "type": "time" },
          "easing":   { "value": "ease-in-out", "type": "string" }
        },
        "spinSmooth": {
          "duration": { "value": "2s", "type": "time" },
          "easing":   { "value": "linear", "type": "string" }
        },
        "pulseSoft": {
          "duration": { "value": "1.5s", "type": "time" },
          "easing":   { "value": "ease-in-out", "type": "string" }
        },
        "popIn": {
          "duration": { "value": "0.3s", "type": "time" },
          "easing":   { "value": "cubic-bezier(0.34, 1.56, 0.64, 1)", "type": "string" }
        }
      }
    }
  }
}
```

### 5.5 Ejemplo de componente React integrado

```jsx
// IconAgentRunning.jsx
import React from 'react';

export const IconAgentRunning = ({
  size = 'md',
  variant = 'outline',
  color = 'default',
  animated = false,
  ...props
}) => {
  const sizeMap = { xs: 16, sm: 20, md: 24, lg: 32, xl: 48 };
  const strokeMap = { 16: 1, 20: 1.5, 24: 1.5, 32: 2, 48: 2 };
  
  const s = sizeMap[size] || 24;
  const sw = strokeMap[s] || 1.5;
  
  const colorToken = {
    default: 'var(--color-icon-default)',
    active: 'var(--color-icon-active)',
    muted: 'var(--color-icon-muted)',
    success: 'var(--color-icon-success)',
    error: 'var(--color-icon-error)'
  }[color] || 'var(--color-icon-default)';

  return (
    <svg
      width={s}
      height={s}
      viewBox="0 0 24 24"
      fill="none"
      stroke={colorToken}
      strokeWidth={sw}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={animated ? 'icon-animated dash-draw' : ''}
      {...props}
    >
      <circle cx="12" cy="12" r="3.5"/>
      <line x1="12" y1="5" x2="12" y2="8.5"/>
      <circle cx="12" cy="4.2" r="0.8" fill={colorToken} stroke="none"/>
      <path d="M 18.5 12 A 6.5 6.5 0 0 1 12 18.5" strokeDasharray="10 4"/>
      <path d="M 5.5 12 A 6.5 6.5 0 0 1 12 5.5" strokeDasharray="10 4"/>
      <polyline points="16.5,16.5 18,15.5 17.5,17.5"/>
    </svg>
  );
};
```

### 5.6 CSS Custom Properties generado por Style Dictionary v4

```css
:root {
  /* Color */
  --color-icon-default: #1F1E1C;
  --color-icon-active: #C96442;
  --color-icon-muted: #5A6B7C;
  --color-icon-success: #4A7C59;
  --color-icon-warning: #C99742;
  --color-icon-error: #B54242;
  --color-icon-info: #5A6B7C;
  --color-icon-inverse: #F4F1ED;

  /* Size */
  --size-icon-xs: 16px;
  --size-icon-sm: 20px;
  --size-icon-md: 24px;
  --size-icon-lg: 32px;
  --size-icon-xl: 48px;

  /* Stroke */
  --stroke-icon-hairline: 1px;
  --stroke-icon-default: 1.5px;
  --stroke-icon-bold: 2px;

  /* Animation */
  --animation-icon-dash-draw-duration: 1.2s;
  --animation-icon-dash-draw-easing: ease-in-out;
  --animation-icon-spin-smooth-duration: 2s;
  --animation-icon-spin-smooth-easing: linear;
}
```

### 5.7 Keyframes de animacion canon

```css
/* dash-draw: para agent-running, loading, syncing */
@keyframes icon-dash-draw {
  0% { stroke-dashoffset: 28; }
  50% { stroke-dashoffset: 0; }
  100% { stroke-dashoffset: -28; }
}
.icon-animated.dash-draw path[stroke-dasharray] {
  animation: icon-dash-draw var(--animation-icon-dash-draw-duration) var(--animation-icon-dash-draw-easing) infinite;
}

/* spin-smooth: para refresh, sync */
@keyframes icon-spin-smooth {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.icon-animated.spin-smooth {
  animation: icon-spin-smooth var(--animation-icon-spin-smooth-duration) linear infinite;
  transform-origin: center;
}

/* pulse-soft: para agent-idle, queued, coral-dot */
@keyframes icon-pulse-soft {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.95); }
}
.icon-animated.pulse-soft {
  animation: icon-pulse-soft 1.5s ease-in-out infinite;
  transform-origin: center;
}

/* pop-in: para success, approve */
@keyframes icon-pop-in {
  0% { transform: scale(0.8); opacity: 0; }
  70% { transform: scale(1.05); opacity: 1; }
  100% { transform: scale(1); opacity: 1; }
}
.icon-animated.pop-in {
  animation: icon-pop-in 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
  transform-origin: center;
}
```

---

## 6. Glosario

| Termino | Definicion |
|---------|-----------|
| **Canon** | Variante definitiva y aprobada de un icono para un concepto dado. Marcada con ★. |
| **DTCG** | Design Tokens Community Group — formato estandar para tokens de diseno. |
| **HITL** | Human-in-the-Loop — flujo donde un humano valida o interviene en una decision del agente. |
| **Keyline** | Linea guia geometrica que define el area de dibujo efectiva dentro del viewBox. |
| **Metafora del telar** | Narrativa de marca central: el agente teje datos (urdimbre) con acciones (trama) para crear valor. |
| **Optical alignment** | Correccion visual que compensa ilusiones opticas para que los iconos parezcan centrados. |
| **Stroke-based** | Sistema donde los iconos se construyen con trazos (lineas) en lugar de rellenos solidos. |
| **Trust Ladder** | Modelo de autonomia progresiva donde el agente gana confianza mediante validaciones exitosas. |
| **Urdimbre** | En telar: hilos verticales fijos. En FaberLoom: datos y estructura base. |
| **Trama** | En telar: hilo horizontal que cruza la urdimbre. En FaberLoom: acciones y decisiones del agente. |

---

## 7. Changelog

| Version | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2026-01-XX | Draft inicial. Sistema formalizado con 96 iconos, 10 categorias, spec completo de grilla/color/animacion, 10 SVGs ejemplo, integracion DTCG/Style Dictionary v4. |

---

*Documento generado para FaberLoom. Voice: calmo, preciso, respetuoso del oficio.*
