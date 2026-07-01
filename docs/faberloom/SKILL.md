---
name: faberloom-designer
version: 1.0.0
description: >
  Skill para generar mocks, componentes UI y design decisions para FaberLoom
  SaaS B2B. Cubre: identidad visual (paleta cream/ink/coral/pizarra, tipografia
  Crimson Pro+Inter+IBM Plex Mono, isotipo Hilos entrelazados), sistema de tokens
  DTCG 3 capas, 96 iconos semanticos, densidad dual (lectura/operacion),
  branding multi-tenant 3 niveles, voice/tone calmo-preciso-respetuoso.
  Trigger: cuando el usuario pide generar UI, mock, componente, layout,
  icono, o decision de diseno para FaberLoom.
  Anti-trigger: no invocar para productos que no sean FaberLoom.
---

# faberloom-designer

| id | FAB-SKL-2026 |
| version | 1.0.0 |
| status | RECOMMENDED |
| domain | faberloom |

---

## 1. Trigger Guidance

### Cuando SI invocar este skill

1. El usuario pide "genera un mock de [pantalla] para FaberLoom"
2. El usuario solicita "crea un componente de [tipo]" para el design system
3. El usuario necesita "decidir como se ve [elemento]" en la interfaz
4. El usuario pide "dame el codigo/token para [componente]"
5. El usuario solicita generar un icono SVG dentro del sistema de 96 iconos
6. El usuario necesita elegir entre opciones de layout, color, o tipografia
7. El usuario pide aplicar branding multi-tenant a una superficie
8. El usuario solicita definir estados de agente o trust ladder visual
9. El usuario pide validar contraste o accesibilidad de un par color
10. El usuario necesita decidir entre modo Lectura u Operacion para una pantalla

### Cuando NO invocar este skill

1. El usuario trabaja en un producto que no es FaberLoom (usa skill generico frontend-design)
2. El usuario pide arquitectura de backend, base de datos, o infraestructura
3. El usuario solicita marketing copy, blog posts, o contenido editorial externo
4. El usuario pide analisis de negocio, pricing, o estrategia de ventas
5. El usuario necesita integracion con APIs de terceros (no diseno)
6. El usuario pide generar imagenes raster (PNG/JPG) - este skill es vector/stroke-based
7. El usuario trabaja en white-label N3 sin especificar que es para FaberLoom
8. El usuario solicita animaciones complejas que no sean CSS transitions
9. El usuario pide cambiar el isotipo canon o la paleta base (irreversibles)
10. El usuario necesita research de usuario (usar skill de UX research)

### Ejemplos de prompts que activan el skill

- "Genera el mock del dashboard de agentes para FaberLoom"
- "Como deberia verse el panel de Sanidad?"
- "Crea el componente Toast para el design system"
- "Que tokens uso para un boton primario en dark mode?"
- "Disena la tabla de logs de auditoria con hash chaining"
- "Como se ve el Trust Ladder en la UI?"
- "Genera el icono para 'agent-running'"
- "Necesito el empty state de la tabla de agentes"
- "Como aplico branding N2 al dashboard de un tenant?"
- "Valida el contraste de este par de colores"

### Ejemplos de prompts que NO activan el skill

- "Genera una landing page para mi startup" (no es FaberLoom)
- "Disena el schema de la base de datos" (backend)
- "Escribe un blog post sobre AI" (contenido editorial)
- "Como configuro Stripe Connect?" (integracion)
- "Crea un logo para mi marca" (branding externo)

---

## 2. Contexto Cargado

### 2.1 Tokens semanticos principales (mas usados)

Usa SIEMPRE estos tokens antes de hardcodear cualquier valor. Los tokens se
resuelven via Style Dictionary v4 a CSS Custom Properties.

| Token | Light | Dark | Uso |
|-------|-------|------|-----|
| `color.surface.page` | `#f4f1ed` | `#181816` | Fondo de pagina |
| `color.surface.card` | `#fcfbfa` | `#1c1b19` | Fondo de card |
| `color.surface.elevated` | `#ffffff` | `#1f1e1c` | Modales, dropdowns |
| `color.text.primary` | `#1f1e1c` | `#f0ece6` | Texto principal |
| `color.text.secondary` | `#5a6b7c` | `#c8c2ba` | Metadatos, subtitulos |
| `color.text.muted` | `#8a847d` | `#948e86` | Placeholders, captions |
| `color.text.inverse` | `#ffffff` | `#1f1e1c` | Texto sobre fondos oscuros/accent |
| `color.accent.primary` | `#c96442` | `#e18c69` | Botones, links, foco |
| `color.accent.primary-hover` | `#b75b3c` | `#f4a88a` | Hover de accent |
| `color.accent.primary-subtle` | `#f6e6de` | `#37261e` | Fondo de seleccion |
| `color.accent.secondary` | `#5a6b7c` | `#a0afbe` | Tags, info badges |
| `color.border.default` | `#dad6d1` | `#4e4a46` | Bordes de cards, tablas |
| `color.border.focus` | `#c96442` | `#e18c69` | Focus ring |
| `color.state.hover` | `#f7f5f3` | `#4e4a46` | Hover en filas/listas |
| `color.state.selected` | `#f6e6de` | `#37261e` | Estado seleccionado |
| `color.state.disabled` | `#ebe8e4` | `#2d2a26` | Elementos deshabilitados |
| `shadow.card` | `0 2px 8px rgba(31,30,28,0.06)` | dark variant | Elevacion de cards |
| `shadow.modal` | `0 8px 24px rgba(31,30,28,0.12)` | dark variant | Elevacion de modales |

Tokens tipograficos semanticos:

| Token | Fuente | Peso | Size | Line-height | Uso |
|-------|--------|------|------|-------------|-----|
| `typography.display.hero` | Crimson Pro | 500 italic | 60px | 1.15 | Hero landing |
| `typography.display.section` | Crimson Pro | 500 italic | 48px | 1.2 | Titulos de seccion |
| `typography.heading.xl` | Inter | 600 | 30px | 1.3 | Titulos de pagina |
| `typography.heading.lg` | Inter | 600 | 24px | 1.3 | Dialog titles |
| `typography.heading.md` | Inter | 600 | 20px | 1.35 | Subsection titles |
| `typography.body.lg` | Inter | 400 | 18px | 1.625 | Lectura larga |
| `typography.body.base` | Inter | 400 | 16px | 1.5 | Body estandar |
| `typography.body.sm` | Inter | 400 | 14px | 1.5 | Descripciones secundarias |
| `typography.label` | Inter | 500 | 14px | 1.25 | Labels de form |
| `typography.caption` | Inter | 400 | 12px | 1.5 | Timestamps, metadata |
| `typography.mono.base` | IBM Plex Mono | 400 | 14px | 1.5 | Logs, codigo |
| `typography.mono.sm` | IBM Plex Mono | 400 | 12px | 1.5 | Timestamps tecnicos |

### 2.2 Stack tipografico con roles

| Rol | Fuente | Pesos | Uso | Restriccion |
|-----|--------|-------|-----|-------------|
| Display | Crimson Pro Italic 500 | 400, 500, 600 | Wordmark "Faber", titulos de seccion editorial, citas, empty states | NUNCA en UI operativa, tablas, ni forms |
| UI / Body | Inter | 400, 500, 600, 700 | Todo texto de interfaz, body, labels, botones | NUNCA en weight < 400 ni > 700 |
| Mono / Datos | IBM Plex Mono | 400, 500 | Logs, JSON, timestamps, codigo, hashes | NUNCA para texto libre de usuario o agente |

**Wordmark canon**: "Faber" en Crimson Pro Italic 500 + "Loom" en Inter Bold 700 coral.
Irreversible. Confidence: ALTO.

### 2.3 Voice/tone (3 principios + 5 ejemplos Si/No)

**Principios no-negociables:**

1. **Calmo, nunca euforico.** FaberLoom no celebra lo obvio, no se emociona con lo
   rutinario, no aplaude lo esperado. "Listo." es suficiente para una tarea completada.
2. **Preciso, nunca vago.** Cada palabra tiene un proposito. "14 registros excluidos"
   en vez de "varios registros". Numeros especificos, timestamps exactos.
3. **Respetuoso del oficio, nunca paternalista.** El profesional sabe. FaberLoom ayuda,
   no instruye. No explica lo obvio, no celebra lo rutinario.

**Ejemplos Si / No:**

| Contexto | Si (FaberLoom) | No (como NO habla) |
|----------|---------------|-------------------|
| Tarea completada | "Tarea completada en 12 minutos." | "Increible! Termine super rapido!" |
| Error | "Error de conexion. Status 503. Reintentando en 30s." | "Ups! Algo salio mal... lo siento!" |
| Onboarding | "Configuremos tu primer proyecto. Tres pasos." | "Bienvenido a bordo! Vamos a hacer magia!" |
| Pedir input | "Confirma el mapeo de campos antes de continuar." | "No se que hacer aqui... ayudame?" |
| Nuevo feature | "Nuevo: export en formato Parquet. Disponible en Exportar." | "Nueva funcion super emocionante!" |

### 2.4 Isotipo canon

**Nombre**: Hilos entrelazados
**Puntuacion**: 24/30 (ganador sobre Trama 20/30 y Nudo celtico 20/30)
**Descripcion**: Dos paths curvos (cubic bezier) que se cruzan en el centro.
Cada path tiene gaps calculados en los puntos de interseccion para simular
"por encima/por debajo". stroke-linecap y stroke-linejoin: round.

**Cuando usar:**
- Favicon multi-resolucion (16x16, 24x24, 32x32)
- Header impreso (facturas, contratos)
- App icon (iOS, Android, macOS, Windows)
- Splash screen y onboarding
- Como progress indicator animado (stroke-dashoffset, 1.2s ciclo)

**Variantes:**
- A. Monocromo: ink sobre cream / cream sobre ink (gap en cruces)
- B. Color: coral #C96442 sobre cream (bicolor: coral + pizarra en cruces)
- C. Dark mode: cream sobre ink, coral como acento puntual (80/20)

**Confidence**: ALTO

### 2.5 Paleta (4 colores + significado semantico)

| Color | Hex | Significado | Uso | NUNCA |
|-------|-----|-------------|-----|-------|
| **Cream** | `#F4F1ED` | Lienzo del profesional. Papel kraft de archivo. Fondo base de toda la experiencia. | Fondo pagina, superficies cards, areas de lectura | Como color de texto, como acento, fondo de seccion con coral encima |
| **Ink** | `#1F1E1C` | Tinta de estilografica. Negro calido con undertone olive. Oficio escrito. | Texto principal, iconos activos, bordes estructura, datos primarios | Puro `#000000` es prohibido |
| **Coral** | `#C96442` | UNICO driver de interaccion. Terracota, arcilla cocida. Herramientas que mejoran con uso. | Botones primarios, links, estados activos, focus rings, badges de accion | Fondo general, texto de cuerpo, borde decorativo. No exceder 5% superficie visible en modo Operacion |
| **Pizarra** | `#5A6B7C` | Lo secundario pero necesario. Pizarra borrada con trazos. No compite. | Metadatos, iconos inactivos, bordes reposo, labels, timestamps | Texto principal (falta contraste en fondos oscuros), como acento |

**Estados funcionales derivados** (no son branding, son semantica):
- Success: `#4e8a66` (sage green)
- Warning: `#c48e48` (amber)
- Danger: `#a8443a` (brick red)
- Info: `#527694` (steel blue)

### 2.6 Patterns no-negociables (reglas duras)

1. **Coral es el UNICO driver de interaccion.** Si necesitas un tercer color para
   "algo importante que no es un boton", usa ink con mas peso o coral-subtle.
2. **Grilla de 24 columnas**, gutter 16px. No 12 columnas. No gutters variables.
3. **Tipografia display (Crimson Pro) NUNCA en tablas, forms, ni UI operativa.**
   Solo en H1-H3 editorial, empty states, citas.
4. **Fuente mono NUNCA para texto libre.** Solo logs, JSON, timestamps, codigo.
5. **Cream SIEMPRE es el fondo base.** Blanco puro `#FFFFFF` esta prohibido.
6. **Negro puro `#000000` esta prohibido.** Ink `#1F1E1C` es el maximo oscuro.
7. **Focus ring visible SIEMPRE** (2px coral, 2px offset), no solo en keyboard.
8. **Transiciones: 0.2s ease estados, 0.3s ease layout.** Nada de bounce, elastic.
9. **Todos los pares bg/fg deben pasar WCAG AA 4.5:1 minimo.**
10. **Convencion: estrella = canon.** La variante marcada con `*` es la definitiva.

### 2.7 Anti-patterns (que NUNCA hacer)

1. **Coral como color de fondo.** Pierde su capacidad de senalar interaccion.
2. **Celebracion excesiva.** No confetti, no badges "Excelente!", no animaciones por tareas rutinarias.
3. **Faux-amistad.** No emojis en UI, no exclamaciones multiples, no "colega de cafeteria".
4. **Dark mode como filtro de inversion.** Es paleta derivada con intencion: papel kraft tostado.
5. **Personificacion del agente.** No nombres propios, no avatares humanos, no "yo".
6. **Micro-managing por defecto.** No "estas seguro?" para acciones reversibles.
7. **Language inflation.** 5 palabras cuando 5 alcanzan. Sin superlativos.
8. **Inventar colores nuevos.** Los 4 colores base + derivados funcionales cubren todo.
9. **Layout de app movil en desktop.** FaberLoom es herramienta profesional de densidad media-alta.
10. **Animacion como decoracion.** Cada animacion debe tener proposito comunicativo.
11. **Tooltips que explican lo obvio.** "Click para guardar" sobre boton Guardar.
12. **Voz inconsistente entre plataformas.** El agente habla igual en chat, toasts, y emails.

---

## 3. Quick Reference

### 3.1 Tabla de decision rapida: "Si necesitas X, usa Y"

| Si necesitas... | Usa... | Token clave |
|-----------------|--------|-------------|
| Fondo de pagina | Cream `#F4F1ED` | `color.surface.page` |
| Texto principal | Ink `#1F1E1C` | `color.text.primary` |
| Boton primario | Coral `#C96442` + blanco | `button.primary.bg` |
| Boton secundario | Transparente + ink borde | `button.secondary.bg` |
| Link | Coral `#C96442` | `color.text.link` |
| Metadatos/timestamp | Pizarra `#5A6B7C` | `color.text.secondary` |
| Fondo de card | Cream claro `#fcfbfa` | `color.surface.card` |
| Estado hover | Neutral-100 `#f7f5f3` | `color.state.hover` |
| Estado seleccionado | Coral-100 `#f6e6de` | `color.state.selected` |
| Error | Danger `#a8443a` | `color.functional.danger.500` |
| Success | Sage `#4e8a66` | `color.functional.success.500` |
| Warning | Amber `#c48e48` | `color.functional.warning.500` |
| Info | Steel blue `#527694` | `color.functional.info.500` |
| Focus ring | Coral 2px + 2px offset | `color.border.focus` |
| Shadow card | Sutil 0 2px 8px | `shadow.card` |
| Shadow modal | Elevado 0 8px 24px | `shadow.modal` |
| Icono activo | Ink `#1F1E1C` | `color.icon.default` |
| Icono inactivo | Pizarra `#5A6B7C` | `color.icon.muted` |
| Icono accion | Coral `#C96442` | `color.icon.active` |
| Display / Hero | Crimson Pro Italic 500 | `typography.display.hero` |
| Body / UI | Inter 400-700 | `typography.body.base` |
| Logs / Datos | IBM Plex Mono 400 | `typography.mono.base` |

### 3.2 Modo Lectura vs Modo Operacion

**Regla de oro:** Si el usuario toma >3 decisiones/minuto, es Operacion.
Si comprende antes de actuar, es Lectura.

| Criterio | Modo Lectura | Modo Operacion |
|----------|-------------|----------------|
| **Proposito** | Reflexion, evaluacion, absorcion | Accion, configuracion, monitoreo |
| **Contexto** | Landing, docs, onboarding, reportes ejecutivos, empty states informativos | Dashboard, tablas, forms, logs, Sanidad, command palette |
| **Espaciado seccion** | 48px | 24px |
| **Espaciado bloque** | 32px | 16px |
| **Line-height body** | 1.65 (relaxed) | 1.5 (normal) |
| **Tipografia headings** | Crimson Pro Italic 500, 48-64px | Inter 700, 24-28px |
| **Tipografia body** | Inter 400, 18-20px | Inter 400, 13-14px |
| **Uso de coral** | Hasta 15% (CTAs, acentos decorativos) | Max 5% (solo acciones) |
| **Animacion** | 400-600ms, fade-up 24px | 150-200ms, functional |
| **Componentes** | Cards amplias (32-48px pad), heroes, quotes, timelines | Tablas densas (44px fila), inputs 36px, bulk actions |

**Transicion:** Fade 300ms en width y opacity. Nunca slide/bounce.

### 3.3 Tokens de agente estados

Los 6 estados del ciclo de vida de un agente FaberLoom:

| Estado | Background | Foreground | Border | Significado | Icono |
|--------|-----------|-----------|--------|-------------|-------|
| **idle** | `#e8e4e1` blue-gray mist | `#4b5a69` dark slate | `#8291a0` | Agente disponible, no procesa | Circulo vacio |
| **running** | `#f6e6de` coral tint | `#87432c` deep coral | `#d88e75` | Agente trabajando activamente | Spinner/arcos |
| **waiting** | `#f4eadb` amber tint | `#735023` dark amber | `#c48e48` | Espera input usuario (HITL) | Reloj de arena |
| **success** | `#e0e9e0` sage tint | `#376249` deep sage | `#7faa8f` | Tarea completada exitosamente | Check circulo |
| **error** | `#f0ddd9` brick tint | `#612721` deep brick | `#c0776f` | Fallo, necesita atencion | X circulo |
| **blocked** | `#ebe8e4` neutral gray | `#4e4a46` dark warm gray | `#8a847d` | Bloqueado por politica/confianza | Barra horizontal |

**Uso visual:**
- Badge: 8px pill con bg + fg, icono 16px al inicio
- Timeline: barras verticales conectoras con border color
- Log: texto mono con prefijo de estado (icono + label)
- Chat bubble: border-left 3px solid en color del estado

### 3.4 Branding level (N1/N2/N3): cuando aplica cada uno

| Nivel | Nombre | Cuando aplica | Tokens FaberLoom | Tokens tenant |
|-------|--------|---------------|------------------|---------------|
| **N1** | Full FaberLoom | Billing, settings globales, help/docs, onboarding, login/signup, admin de org | TODOS | NINGUNO |
| **N2** | Co-Branded | Dashboard interno, sidebar header, reportes internos, canvas workspace, settings workspace | Estructura + neutrales | Logo + nombre + accent tenant |
| **N3** | White-Label | Reportes externos, portal de cliente, embeddings, dashboard publico | Estructura minima | TODOS |

**Regla de oro N2 (resolucion conflicto coral vs tenant-accent):**
- Accion del DOMINIO del tenant (su negocio, datos, workflows) -> `accent-tenant`
- Accion del DOMINIO de FaberLoom (plataforma, billing, ayuda) -> `coral`

**N3:** Coral se elimina por completo. "Powered by FaberLoom" es opt-in y monocromatico gris.

---

## 4. Ejemplos de Uso

### Ejemplo 1: Generar mock del dashboard de agentes

**Input:** "Genera el mock del tab Iterar - dashboard de 50 agentes en paralelo para FaberLoom. Modo Operacion."

**Output esperado:**
- Layout de 24 columnas: sidebar 240px colapsable, header 56px, main area con tabla
- Tabla densa: filas 44px, header sticky `#EEEBE6`, filas alternadas `#F4F1ED`/`#FAF9F7`
- Columnas: checkbox, Nombre, Estado, Tenant, Ultima ejecucion, Acciones
- Estados de agente con badges coloreados segun tokens de agente (idle/running/waiting/success/error/blocked)
- Filtros rapidos por estado: tabs con contadores ("Todos", "Running (12)", "Error (3)")
- Barra de bulk actions flotante (slide-up 150ms) al seleccionar filas
- Acciones inline en hover: iconos 16px con tooltip
- Log stream en tiempo real: IBM Plex Mono 11px, colores por nivel
- Search bar global: input 44px alto, icono lupa, debounce 200ms

**Razonamiento:**
- Modo Operacion: tipografia Inter 13-14px, spacing 8-16px, tablas densas
- Grilla 24 cols para granularidad con sidebar + contenido
- Estados de agente usan tokens semanticos definidos (no colores arbitrarios)
- Acciones inline en hover para no saturar la tabla visualmente
- Bulk actions flotante porque seleccion multiple es operacion frecuente
- Log en mono porque es contenido tecnico estructural

**Confidence:** ALTO

---

### Ejemplo 2: Crear componente Toast

**Input:** "Crea el componente Toast para FaberLoom con las 4 variantes (success, warning, error, info). Modo Operacion."

**Output esperado:**
- Posicion: top-right, 16px margen, max 3 simultaneos (stack 8px)
- Width: 360px. Fondo: cream `#FAF9F7`. Border-left: 3px segun tipo.
- Shadow: `shadow.3` (0 4px 16px rgba(31,30,28,0.08))
- Icono tipo 16px a la izquierda (del sistema de 96 iconos)
- Titulo: Inter 13px 600. Mensaje: Inter 12px 400.
- Close: x 14px derecha. Auto-dismiss: 5s (excepto error: manual).
- Progreso bar fina abajo indicando tiempo restante.
- Animacion: slide-in desde derecha 200ms, fade-out 150ms.
- Variantes:
  - `info`: icono info, sin acento extra
  - `success`: icono check, border-left 3px success `#4e8a66`
  - `warning`: icono alerta, border-left 3px warning `#c48e48`
  - `error`: icono x, border-left 3px danger `#a8443a`

**Razonamiento:**
- Modo Operacion: componente funcional, animaciones rapidas (200ms)
- Border-left para variante en lugar de fondo coloreado (mantiene calma)
- Auto-dismiss diferenciado: error manual porque requiere atencion
- Progreso bar para feedback temporal en success/info/warning
- Stack max 3 para no abrumar al usuario con notificaciones
- Cream como fondo, no blanco puro, consistente con superficie elevated

**Confidence:** ALTO

---

### Ejemplo 3: Empty state de tabla de agentes

**Input:** "Disena el empty state para la tabla de agentes cuando el usuario no tiene agentes configurados todavia."

**Output esperado:**
- Modo Lectura: ilustracion + "Comenza creando tu primer agente" + CTA coral
- Ilustracion: line-art minimalista del isotipo (hilos entrelazados) en pizarra 20% opacity
- Tamano: 120px de alto
- Titulo: Crimson Pro Italic 500, 24px, ink: "Todavia no hay hilos en este telar"
- Descripcion: Inter 400, 14px, ink-60%: "Crea tu primer agente para empezar a tejer. La IA prepara, vos decis."
- CTA: Boton primario coral "Crear agente" + link secundario "Ver documentacion"
- Padding generoso: 48px vertical

**Razonamiento:**
- Empty state de primera vez = Modo Lectura (educar, no operar)
- Crimson Pro Italic apropiado para display en empty state (no UI operativa)
- Metafora del telar consistente con brand narrative
- Dos acciones: primaria (CTA coral) y secundaria (link)
- Ilustracion sutil en pizarra para no competir con el CTA coral
- Descripcion corta que refuerza el manifiesto de marca

**Confidence:** ALTO

---

### Ejemplo 4: Trust Ladder visual indicator

**Input:** "Como se visualiza el Trust Ladder (autonomia progresiva) en la UI?"

**Output esperado:**
- Componente custom: 4 niveles visuales en linea horizontal
- Nivel activo: coral filled + label coral
- Niveles inferiores alcanzados: ink filled + label ink
- Niveles no alcanzados: ink-30 outline + label ink-30
- Conector: linea 2px entre niveles, color segun estado de conexion
- Niveles:
  1. **Asistido** - Agente sugiere, humano ejecuta. Todo requiere aprobacion.
  2. **Semi-autonomo** - Agente ejecuta lo rutinario, pide confirmacion en lo novedoso.
  3. **Autonomo** - Agente ejecuta, informa post-hoc. Solo escala en excepciones.
  4. **Delegado** - Agente opera dentro de guardrails. Humano supervisa por dashboard.
- Comportamiento:
  - Cada nivel es clicable para cambiar la politica de autonomia
  - Cambio de nivel requiere confirmacion en modal
  - Nivel actual muestra tooltip con descripcion de comportamiento

**Razonamiento:**
- 4 niveles en lugar de toggle binario (on/off) porque la autonomia es progresiva
- Visualizacion horizontal con conector porque sugiere "escalera" progresiva
- Coral solo para el nivel activo, no para todos (restriccion de acento)
- Clickable porque el usuario debe poder cambiar su nivel de confianza
- Confirmacion en modal porque cambiar autonomia tiene consecuencias
- Tooltip educativo sin ser paternalista (describe comportamiento, no instruye)

**Confidence:** ALTO

---

### Ejemplo 5: Aplicar branding N2 al dashboard de un tenant

**Input:** "El tenant 'Acme Co' tiene accent color `#0284c7` (azul). Muestra como se ve el dashboard en branding N2."

**Output esperado:**
- Chrome de FaberLoom mantiene coral: sidebar navigation, settings icon, help link
- Contenido del tenant usa azul `#0284c7`:
  - Boton "Generar reporte": bg azul, texto blanco
  - Link "Ver analisis": azul
  - CTA de workflow: azul
  - Focus en inputs del workspace: azul
  - Badges de accion del negocio: azul-subtle bg + azul texto
- Sidebar header: logo de Acme Co + nombre del tenant
- Fondo base: cream `#F4F1ED` (se mantiene)
- Texto: ink `#1F1E1C` (se mantiene)
- Estados de agente: mismos colores semanticos (no cambian con tenant-accent)

**Razonamiento:**
- Regla contextual N2: dominio del tenant = accent-tenant, dominio de FaberLoom = coral
- Los botones de accion de negocio (generar reporte, ver analisis) pertenecen al tenant
- La navegacion global pertenece a FaberLoom, se queda coral
- Estados de agente son semantica funcional, no branding - no cambian
- Cream e ink se mantienen como base neutra
- Logo del tenant en sidebar header para sentido de "espacio propio"

**Confidence:** MEDIO-ALTO

---

## 5. Referencias a Archivos Canonicos

Cuando necesites profundizar mas alla de este skill, lee los archivos en este orden:

| Orden | Archivo | Path relativo | Que contiene |
|-------|---------|---------------|-------------|
| 1 | DESIGN.md (Google Labs format) | `DESIGN_FABERLOOM_v1.md` | Fuerza de verdad completa: colores, tipografia, layout, elevacion, formas, componentes (Button, Card, Input, Select, Tab, Badge, Toast, Trust Ladder, Chat Panel, Log Viewer, Diff View), Voice & Tone con ejemplos Si/No completos, Do's & Don'ts, 12 Anti-patterns |
| 2 | Tokens semanticos | `tokens/semantic.dtcg.json` | Tokens semanticos con light/dark modes: surface, text, accent, border, state, agent states. Incluye typography semantic compositions |
| 3 | Tokens base | `tokens/base.dtcg.json` | Primitivas: color ramps (cream 50-900, ink 50-900, coral 50-900, pizarra 50-900, neutral 0-1000, functional success/warning/danger/info 50-900, agent state quads), space (4px grid), radius, typography family/weight/size/line-height/letter-spacing, shadow (5 levels + dark variants), motion (duration + easing), opacity, z-index |
| 4 | Tokens de componentes | `tokens/components.dtcg.json` | Tokens por componente: button (primary/secondary/ghost con 5 estados cada uno), input, card, badge, tab, dialog, toast, tooltip, table, sidebar, chat bubble |
| 5 | Personas y JTBD | `SPEC_FABERLOOM_PERSONAS_JTBD_v1.md` | 5 personas arquetipicas (Diana, Sergio, Camila, Tomas, Valentina) con perfiles psicograficos completos, tech stacks, jobs principales, anti-jobs, metricas de exito. 16 JTBD maestros ranqueados por frecuencia x criticalidad |
| 6 | Spec de iconos | `SPEC_FABERLOOM_ICONS_v1.md` | Sistema de 96 iconos en 10 categorias (Agentes, Herramientas, Datos, Navegacion, Estados, Feedback, HITL, Workspace, UI, Comunicacion). Spec de grilla 24px, stroke 1.5px, currentColor, 5 tamanios (16-48px), 4 variantes (outline/solid/duotone/animated), 5 animaciones canon, SVGs de ejemplo construidos |
| 7 | Spec de isotipo | `SPEC_FABERLOOM_ISOTIPO_DECISION_v1.md` | Decision del isotipo Hilos entrelazados (24/30): analisis comparativo, 3 variantes de aplicacion, SVG paths, animacion como progress indicator, variantes prohibidas |
| 8 | Spec de tipografia | `SPEC_FABERLOOM_TYPOGRAPHY_v1.md` | Stack completo con 11 fuentes auditadas, tabla de uso por contexto, evaluacion comparativa, variable fonts, estrategia de carga con preload, fallback stacks, DTCG mapping |
| 9 | Spec de UI density | `SPEC_FABERLOOM_UI_DENSITY_v1.md` | Sistema dual Lectura/Operacion con specs completas de espaciado, tipografia, color, componentes. Componentes ranqueados MVP/V1/V2. Reglas de implementacion para agentes IA |
| 10 | Spec de multi-tenant branding | `SPEC_FABERLOOM_MULTITENANT_BRANDING_v1.md` | 3 niveles de branding (N1/N2/N3), resolucion del conflicto coral vs tenant-accent, arquitectura de tokens con fallback, implementacion CSS Custom Properties con data-tenant |
| 11 | Spec de tokens | `SPEC_FABERLOOM_TOKENS_v1.md` | Documentacion del sistema de 471 tokens, validacion de contraste WCAG, reglas de extension, jerarquia de referencias |
| 12 | Spec de referencias visuales | `SPEC_FABERLOOM_VISUAL_REFERENCES_v1.md` | 15 referencias positivas (Linear, Vercel, Framer, Notion, Raycast, etc.) con score por aspecto. 12 anti-referencias (Canva, ClickUp, Monday, Asana, etc.) con lecciones. Moodboard sintetizado |
| 13 | Skills research | `SPEC_FABERLOOM_SKILLS_RESEARCH_v1.md` | 40 skills publicas auditadas, top 10 detallados, fragmentos copiables con licencia, anti-patterns de skills, gap analysis |

---

## 6. Decisiones Arquitecturales Irreversibles

Estas decisiones no se pueden cambiar facilmente post-launch. El skill debe respetarlas siempre.

| # | Decision | Por que es irreversible | Confidence |
|---|----------|------------------------|------------|
| 1 | **Crimson Pro Italic 500 para wordmark "Faber"** | Requiere redisenar logo, favicon, assets de marca, templates. Ligada al isotipo. | ALTO |
| 2 | **Los 4 colores base (cream, ink, coral, pizarra)** | Los tokens semanticos y componentes derivan de estas ramps. Cambiar un color base invalida ~300 tokens. | ALTO |
| 3 | **Coral como UNICO driver de interaccion** | Todos los componentes asumen esta regla. Introducir un segundo acento rompe la jerarquia visual construida. | ALTO |
| 4 | **Stack tipografico Crimson Pro + Inter + IBM Plex Mono** | Los tokens tipograficos semanticos se componen de estas 3 familias. Cambiar requiere redefinir ~50 tokens de typography. | ALTO |
| 5 | **Sistema de tokens DTCG de 3 capas (base -> semantic -> components)** | Los componentes referencian semantic, que referencia base. Invertir esta jerarquia rompe todo el pipeline de Style Dictionary. | ALTO |
| 6 | **Isotipo Hilos entrelazados** | Assets de favicon, app icon, splash screen, y animacion de progress indicator dependen de este SVG especifico. | ALTO |
| 7 | **Estructura de 3 niveles de branding (N1/N2/N3)** | Requiere re-mapear todas las superficies de la app y re-configurar tenants post-launch. | ALTO |
| 8 | **Formato JSON schema de tenant branding** | Breaking change en API de branding, migracion de configs de tenant. | MEDIO-ALTO |
| 9 | **96 iconos stroke-based con currentColor** | Todos los componentes usan iconos con herencia de color via currentColor. Cambiar a fill-based invalida el sistema. | MEDIO-ALTO |
| 10 | **Convencion "estrella = canon"** | La marca de variante canon (`*`) esta en documentacion, specs, y potencialmente en codigo. Cambiar la convencion genera confusion. | MEDIO |

---

## 7. Extension y Mantenimiento

### Como extender el skill con nuevos componentes

1. Definir el componente en `tokens/components.dtcg.json` con TODOS los estados
   (default, hover, active, focus, disabled)
2. Referenciar tokens semanticos, nunca base directamente
3. Validar contraste de todos los pares bg/fg antes de commitear
4. Documentar en `DESIGN_FABERLOOM_v1.md` seccion Components
5. Actualizar este SKILL.md en la seccion 3.1 (tabla de decision rapida)
6. Version bump del skill segun formato de changelog

### Como agregar nuevos tokens

1. Agregar el HEX base a `$metadata.customColors` (documentacion)
2. Generar ramp 50-900 en `tokens/base.dtcg.json` -> `color.{nombre}`
3. Crear tokens semanticos en `tokens/semantic.dtcg.json` si es color funcional
4. Validar contraste de todos los pares bg/fg
5. Seguir la jerarquia: components -> semantic -> base (CORRECTO),
   nunca semantic -> components ni base -> cualquier otra capa

### Formato de changelog

```
| Version | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0.0 | 2026-01-15 | Release inicial. Skill empaquetado con 13 specs, 471 tokens, 96 iconos, 5 personas, 16 JTBD. | faberloom-designer |
| 1.1.0 | YYYY-MM-DD | Descripcion concisa del cambio. Referencia a spec actualizado. | autor |
```

Reglas de versionado:
- **MAJOR (X.0.0):** Cambio en decision arquitectural irreversible, cambio de isotipo, cambio de paleta base
- **MINOR (x.Y.0):** Nuevo componente, nuevo token semantico, nueva categoria de iconos, extension de skill
- **PATCH (x.y.Z):** Correccion de tokens, ajuste de valores, fix de contraste, mejora de documentacion

---

*Skill empaquetado para FaberLoom. Convencion: estrella = canon.*
*Para consultas, profundizar en los archivos canonicos listados en la seccion 5.*
*Prioridad de decision cuando hay conflicto: Calma > Coral > Precision > Velocidad.*
