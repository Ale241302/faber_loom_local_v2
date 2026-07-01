# SPEC FABERLOOM UI DENSITY v1.0.0

| id | FAB-UI-2026 |
|----|-------------|
| version | 1.0.0 |
| status | DRAFT |
| visibility | INTERNAL |
| domain | faberloom |
| author | AI Agent — Design Systems |
| date | 2026-01-15 |
| confidence | HIGH |

---

## Resumen ejecutivo

FaberLoom es un SaaS B2B chat-first agentic multi-tenant que opera en tres tabs (Configurar / Iterar / Sanidad) con un Trust Ladder de autonomia progresiva. El Brand Book v2 2026 define una voz calma, precisa y respetuosa del oficio — el telar del hacedor moderno donde "la IA prepara, vos tejes."

Este documento cierra el gap critico entre la marca editorial (ya definida) y la interfaz operativa del producto real: tablas densas, formularios complejos, filtros avanzados, estados de carga, logs de auditoria y scorecards de sanidad. Define un **sistema de densidad dual** que permite a FaberLoom transitar entre momentos de lectura reflexiva (landing, manifiesto, reportes ejecutivos) y momentos de operacion intensiva (dashboards, tablas de 1000+ filas, configuracion de agentes) sin quebrar la coherencia de marca ni la voz del producto.

El sistema prioriza componentes MVP para lanzamiento inmediato, ordena V1 y V2 en roadmap, y establece reglas de implementacion para que agentes IA generen interfaces consistentes en ambos modos de densidad.

---

## Sistema de densidad dual

### Filosofia fundamental

FaberLoom tiene dos registros, no dos productos. El mismo telar teje en dos ritmos: el ritmo pausado de la reflexion y el ritmo rapido de la accion. La densidad no es una opcion de usuario — es una decision de diseno que el sistema toma por contexto. El usuario no elige "modo denso" o "modo espacioso"; el producto selecciona el registro apropiado segun la tarea, el momento y el estado mental esperado.

La transicion entre modos debe ser imperceptible en terminos de marca pero evidente en terminos de funcionalidad. Siempre se siente a FaberLoom; nunca se siente que se cambio de producto.

### Modo Lectura

**Proposito:** Espacios de reflexion, evaluacion y absorcion de informacion. Momentos donde el hacedor moderno lee, comprende y decide.

**Cuando se usa:**
- Landing page y paginas de marketing
- Manifiesto y contenido editorial
- Documentacion y guias de usuario
- Onboarding inicial (pasos 1-3)
- Reportes ejecutivos exportados
- Pantallas de "empty state" informativas
- Modales de confirmacion importantes (delete tenant, revoke access)
- Vista previa de configuraciones antes de aplicar

**Espaciado:**

| Elemento | Valor | Token |
|----------|-------|-------|
| Seccion a seccion | 48px | `--space-section-lg` |
| Bloque a bloque | 32px | `--space-block-lg` |
| Elemento a elemento | 24px | `--space-element-lg` |
| Parrafo interno | 20px line-height | `--leading-relaxed` |
| Padding horizontal pagina | 64px (desktop), 24px (mobile) | `--page-gutter-lg` |

**Tipografia:**

| Rol | Fuente | Peso | Tamaño | Line-height |
|-----|--------|------|--------|-------------|
| H1 display | Crimson Pro Italic | 500 | 48-64px | 1.15 |
| H2 section | Crimson Pro Italic | 500 | 36-40px | 1.2 |
| H3 block | Crimson Pro Italic | 500 | 28-32px | 1.25 |
| Body grande | Inter | 400 | 18-20px | 1.7 |
| Body estandar | Inter | 400 | 16px | 1.6 |
| Caption / meta | Inter | 400 | 14px | 1.5 |
| Monospace (logs) | JetBrains Mono | 400 | 14px | 1.6 |

**Color — brand-forward:**

| Rol | Valor | Uso |
|-----|-------|-----|
| Fondo primario | cream `#F4F1ED` | 80%+ de la superficie |
| Fondo secundario | cream dark `#E8E4DE` | secciones alternadas |
| Texto primario | ink `#1F1E1C` | 90%+ del texto |
| Acento activo | coral `#C96442` | CTAs, links, estados activos |
| Acento sutil | coral 15% opacity | highlights, selecciones suaves |
| Texto secundario | ink 60% `#1F1E1C99` | captions, metadata |
| Borde sutil | ink 10% `#1F1E1C1A` | divisores, bordes de cards |
| Pizarra | `#5A6B7C` | badges informativos, iconos secundarios |
| Superficie inversa | ink `#1F1E1C` | secciones hero, dark mode editorial |

**Componentes tipicos:**
- Cards amplias con padding generoso (32-48px)
- Hero sections con imagen de fondo o gradiente sutil
- Quote blocks con borde lateral coral y serif italic
- Feature grids con icono grande + titulo + descripcion
- Timeline vertical para onboarding steps
- Estadisticas en grandes numeros display
- Graficos de area grandes con leyendas claras

**Animacion:**
- Transiciones suaves: 400-600ms, easing `cubic-bezier(0.25, 0.1, 0.25, 1)`
- Entrada de elementos: fade-up de 24px, stagger 100ms
- Hover en cards: elevacion sutil (shadow), scale 1.01

**Confidence level: HIGH** — El Brand Book v2 ya define esta direccion; esta especificacion la hace operativa.

---

### Modo Operacion

**Proposito:** Espacios de accion, configuracion y monitoreo intensivo. Momentos donde el hacedor moderno ejecuta, ajusta y supervisa.

**Cuando se usa:**
- Dashboard principal (tab Iterar)
- Tablas de agentes, tenants, usuarios
- Formularios de configuracion (tab Configurar)
- Logs de auditoria y streams en tiempo real
- Panel de Sanidad (scorecards, checks)
- Modales rapidos de confirmacion (delete file, discard changes)
- Tooltips, dropdowns, menus contextuales
- Estados de carga y skeletons
- Command palette / Spotlight search

**Espaciado:**

| Elemento | Valor | Token |
|----------|-------|-------|
| Seccion a seccion | 24px | `--space-section-sm` |
| Bloque a bloque | 16px | `--space-block-sm` |
| Elemento a elemento | 8-12px | `--space-element-sm` |
| Line-height texto | 1.4-1.5 estandar | `--leading-normal` |
| Padding horizontal pagina | 24px (desktop), 16px (mobile) | `--page-gutter-sm` |
| Padding interno celdas tabla | 10px 12px | `--cell-padding` |
| Gap entre botones de accion | 8px | `--action-gap` |

**Tipografia:**

| Rol | Fuente | Peso | Tamaño | Line-height |
|-----|--------|------|--------|-------------|
| H1 pagina | Inter | 700 | 24-28px | 1.3 |
| H2 seccion | Inter | 700 | 18-20px | 1.35 |
| H3 subseccion | Inter | 600 | 14-16px | 1.4 |
| Body | Inter | 400 | 13-14px | 1.5 |
| Tabla / data | Inter | 400 | 12-13px | 1.4 |
| Monospace (logs, hashes) | JetBrains Mono | 400 | 11-12px | 1.4 |
| Label / caption | Inter | 500 | 11-12px | 1.3 |
| Badge / pill | Inter | 600 | 10-11px | 1.2 |

**Color — brand-discreet:**

| Rol | Valor | Uso |
|-----|-------|-----|
| Fondo primario | cream `#F4F1ED` | 70% de la superficie |
| Fondo secundario | `#EEEBE6` | sidebars, panels, headers de tabla |
| Fondo terciario | `#E5E2DC` | filas alternadas, hover sutil |
| Superficie elevada | `#FAF9F7` | modales, drawers, dropdowns |
| Texto primario | ink `#1F1E1C` | labels, datos importantes |
| Texto secundario | ink 65% `#1F1E1CA6` | metadata, timestamps |
| Texto terciario | ink 40% `#1F1E1C66` | placeholders, hints |
| Borde estandar | ink 12% `#1F1E1C1F` | bordes de tabla, inputs |
| Borde activo | coral `#C96442` | input focus, accion primaria |
| Acento accion | coral `#C96442` | solo para botones primarios y estados activos |
| Acento hover | `#B55634` | coral oscurecido 10% |
| Estado success | `#2D7A5F` | check pass, agent success |
| Estado warning | `#C9962E` | warning, retry pending |
| Estado error | `#A94442` | error, fail, blocked |
| Estado info | `#4A7FB5` | info badges, hints |
| Pizarra funcional | `#5A6B7C` | iconos de accion, secondary nav |

**Componentes tipicos:**
- Tablas densas con filas de 40-44px de alto
- Inputs compactos de 36px de alto
- Botones de accion inline (icono + texto corto)
- Fila de filtros sticky sobre tabla
- Bulk actions bar flotante sobre seleccion
- Sidebar collapsible de 240px (expandido) / 56px (colapsado)
- Tabs primarios con underline coral activo
- Badge/pill con colores de estado semanticos
- Log stream con scroll autoscroll y pausa manual
- Progress bars finos (4px de alto)

**Animacion:**
- Transiciones funcionales: 150-200ms, easing `cubic-bezier(0.4, 0, 0.2, 1)`
- Hover en filas de tabla: background-color 100ms
- Aparecer de toasts: slide-in desde arriba 200ms
- Skeleton pulse: 1.5s ease-in-out infinite

**Confidence level: HIGH** — Deriva directamente del Brand Book aplicado a contextos operativos de alta densidad.

---

### Criterios de seleccion de modo

| Contexto | Modo recomendado | Justificacion | Excepciones |
|----------|------------------|---------------|-------------|
| Landing page, marketing | Lectura | El usuario evalua, no opera | Calculadora ROI puede ser Operacion |
| Onboarding pasos 1-3 | Lectura | El usuario aprende el producto | Paso de "conectar primera fuente" es Operacion |
| Dashboard principal | Operacion | Monitoreo de 50+ agentes | Tour guiado overlay es Lectura |
| Tabla de agentes | Operacion | Densidad de datos, acciones rapidas | Reporte exportado es Lectura |
| Configuracion de agente | Operacion | Formularios tecnicos, validaciones | Preview del agente configurado es Lectura |
| Log de auditoria | Operacion | Datos crudos, timestamps, hashes | Reporte de compliance exportado es Lectura |
| Panel Sanidad | Operacion | Scorecard con metricas, checks | Explicacion de metrica en tooltip/modal es Lectura |
| Reporte ejecutivo | Lectura | Resumen para stakeholders | Drill-down a datos crudos es Operacion |
| Empty state (primera vez) | Lectura | Educar al usuario, siguiente paso | Empty state de tabla filtrada es Operacion |
| Modal de confirmacion | Mix: titulo en Lectura, accion en Operacion | Respetar la gravedad, facilitar la accion | — |
| Documentacion | Lectura | Leer y comprender | Snippets de codigo son Operacion |
| Command palette | Operacion | Busqueda rapida, accion inmediata | — |
| Error boundary (404/500) | Lectura | Calmar al usuario, guiar a recuperacion | — |

**Regla de oro:** Si el usuario necesita tomar mas de 3 decisiones por minuto, es Operacion. Si el usuario necesita comprender antes de actuar, es Lectura.

---

### Transicion entre modos

La transicion entre modos de densidad no debe ser un cambio de "tema" ni requerir recarga de pagina. Es una gradacion controlada que respeta la atencion del usuario.

**Transicion suave (mismo contexto):**
- Dentro del tab Iterar: el usuario pasa del dashboard (Operacion) a un reporte exportado (Lectura) via un boton "Generar reporte". La transicion usa un fade 300ms, mantiene el sidebar y header, y expande el padding/margenes. La tipografia escala gradualmente (12px → 14px → 16px).
- Dentro del tab Configurar: el usuario configura un agente (Operacion) y abre el preview (Lectura). El panel de preview se abre como drawer lateral con modo Lectura completo dentro del drawer.

**Transicion estructural (cambio de tab):**
- Cambio de Iterar (Operacion) a Sanidad (Operacion): no hay transicion de modo, solo cambio de contenido. Tabs cambian con slide horizontal 200ms.
- Cambio de cualquier tab a Documentacion (Lectura): el sidebar se colapsa automaticamente, el main content area se expande, padding aumenta a 64px. Transicion: 400ms ease.

**Mantenimiento de marca durante transicion:**
- El coral nunca desaparece completamente. En Operacion aparece en el tab activo, botones primarios, y estados de accion. En Lectura aparece en headlines, CTAs, y acentos decorativos.
- El cream `#F4F1ED` siempre es el fondo base en ambos modos. No hay "modo oscuro" de operacion.
- El serif italic (Crimson Pro) siempre esta presente: en Lectura como fuente principal de display, en Operacion restringido a titulos de pagina (H1) y estados empty/celebratorios.
- El isotipo de FaberLoom siempre visible en el sidebar/header, sin cambios entre modos.

**Anti-patterns a evitar:**
- ❌ Boton de "toggle modo compacto/espacioso" — el modo es contextual, no preferencia
- ❌ Cambio de paleta de colores completa entre modos
- ❌ Diferente iconografia o lenguaje visual
- ❌ Transiciones que ocultan informacion funcional (sidebar colapsado sin accesso rapido)
- ❌ Modo Operacion con fondo blanco puro `#FFFFFF` — siempre cream base

**Confidence level: HIGH** — Los criterios son claros y las transiciones siguen principios establecidos de diseno de sistemas.



---

## Componentes ranqueados

### Convenciones de prioridad

| Prioridad | Significado | Timeline |
|-----------|-------------|----------|
| **MVP** | Bloqueante para launch. Sin esto, el producto no funciona. | Semanas 1-4 |
| **V1** | Esperado por usuarios power-user. Mejora retencion. | Meses 2-3 |
| **V2** | Diferenciador competitivo. Delight y eficiencia avanzada. | Meses 4-6 |

### Estados base (aplicables a todos los componentes)

Cada componente en esta especificacion debe implementar los siguientes estados:

| Estado | Definicion | Implementacion minima |
|--------|------------|----------------------|
| **Default** | Estado inicial al renderizar | Estilos base del componente |
| **Hover** | Cursor sobre el componente | Cambio de fondo (5-8% opacidad ink) o borde (coral 50% opacity), cursor pointer |
| **Active / Selected** | Componente activado o seleccionado | Fondo coral 10%, borde coral solido, texto ink |
| **Focus (keyboard)** | Navegacion por teclado | Outline 2px coral, offset 2px, sin box-shadow |
| **Disabled** | Componente no interactivo | Opacidad 40%, cursor not-allowed, sin eventos |
| **Loading** | Esperando datos o accion | Skeleton animado o spinner inline, mantener layout |
| **Error** | Fallo de validacion o carga | Borde error solido, icono error, mensaje abajo en rojo suave |
| **Empty** | Sin contenido para mostrar | Ilustracion sutil + texto guia + CTA de accion |

---

### Tablas y datos

| Componente | Prioridad | Modo | Spec |
|------------|-----------|------|------|
| **Tabla basica (10 rows)** | MVP | Operacion | Tabla estandar HTML5 reforzada: header sticky con fondo `#EEEBE6`, filas 44px alto, celdas padding 10px 12px, bordes horizontales 1px `#1F1E1C1F`, filas alternadas `#F4F1ED` / `#FAF9F7`, hover fila `#E5E2DC`. Texto: Inter 13px. Header: Inter 11px 500 uppercase tracking 0.5px. Sin columna de acciones por defecto. |
| **Tabla con paginacion (100 rows)** | MVP | Operacion | Extends tabla basica. Paginacion abajo: 50 items por defecto, opciones 25/50/100. Controles: prev/next, first/last, page number input. Info: "Mostrando 1-50 de 247 agentes". Paginacion fija al footer del contenedor. Estado loading: skeleton de 10 filas. |
| **Tabla virtualizada (1000+ rows)** | V1 | Operacion | Virtualizacion con react-window o similar. Filas visibles: ~20 viewport. Buffer: 5 filas arriba/abajo. Scroll suave nativo. Fila placeholder durante scroll rapido: rectangulo gris con brillo animado. Altura fija por fila (44px) obligatoria. Header siempre visible (position sticky). |
| **Fila expandible (detalle de agente)** | MVP | Operacion | Icono chevron derecha en primera columna. Click expande fila a 200px alto mostrando panel con tabs: Logs / Config / Variables. Transicion: 200ms height. Solo una fila expandida a la vez (auto-colapsa otras). Fila expandida: fondo `#FAF9F7`, borde inferior coral 2px. |
| **Fila con acciones inline** | MVP | Operacion | Columna acciones al final (right-aligned). Default: invisible. Hover fila: acciones aparecen (fade-in 100ms). Acciones: iconos 16px con tooltip (pause, edit, logs, delete). Dropdown "..." para acciones secundarias. Acciones destructivas (delete) en coral oscurecido. |
| **Bulk actions bar** | MVP | Operacion | Barra flotante aparece al seleccionar >=1 fila via checkbox. Posicion: sticky bottom, 16px de margen, centrada, max-width 600px. Fondo: ink `#1F1E1C`, texto cream. Muestra: "N seleccionados" + acciones (pause, resume, restart, delete) + deselect all. Animacion: slide-up 150ms. |
| **Column resizing** | V1 | Operacion | Handle de resize en borde derecho de header celda. Cursor: col-resize. Min-width: 80px. Max-width: 600px. Persistir widths en localStorage por tabla. Indicador visual de limite: linea punteada coral mientras se arrastra. |
| **Column reordering** | V1 | Operacion | Drag-and-drop de headers. Ghost: header semi-transparente. Drop target: linea coral 2px entre columnas. Persistir orden en localStorage. No permitir reposicionar columna de checkbox ni acciones. |
| **Sorting indicators** | MVP | Operacion | Header clickeable para sort. Icono: flecha arriba/abajo 12px. Estado default: flecha gris 30% opacity. Ascendente: flecha arriba coral solida. Descendente: flecha abajo coral solida. Multi-sort: cmd/ctrl+click, badges indican orden (1, 2, 3). |
| **Empty state de tabla** | MVP | Mix | Contexto dependiente: (a) tabla sin datos nunca usada → modo Lectura: ilustracion + "Comenza creando tu primer agente" + CTA coral grande; (b) tabla filtrada sin resultados → modo Operacion: icono search 48px gris + "Ningun agente coincide con los filtros" + boton "Limpiar filtros". |
| **Loading skeleton de tabla** | MVP | Operacion | 10 filas de placeholder. Cada fila: rectangulo gris `#E5E2DC` en cada celda, width 60-90% variado. Animacion: shimmer sweep de izquierda a derecha, 1.5s ease-in-out infinite. Mantener estructura de columnas del header. Reemplazar paginacion por rectangulo ancho 200px. |
| **Error boundary de tabla** | MVP | Mix | Fallback UI si la tabla falla al cargar. Modo Lectura para calmness: icono warning en pizarra, titulo "No pudimos cargar los datos", descripcion tecnica colapsable, boton "Reintentar" coral, link "Contactar soporte". No mostrar stack trace por defecto. |

**Confidence level: HIGH** — Tablas son el core del producto; estas specs derivan de necesidades de 50+ agentes en paralelo.

---

### Formularios

| Componente | Prioridad | Modo | Spec |
|------------|-----------|------|------|
| **Input text con validacion** | MVP | Operacion | Height 36px. Padding 8px 12px. Border 1px `#1F1E1C1F`, border-radius 6px. Fondo `#FAF9F7`. Focus: border coral, shadow 0 0 0 3px coral 15%. Placeholder: ink 40%. Validacion: mensaje debajo 11px, color error. Icono estado (check/error) dentro del input a la derecha. |
| **Input con icono (search, password)** | MVP | Operacion | Icono 16px a la izquierda, padding-left 36px. Icono color ink 40%. Focus: icono pasa a coral. Password: icono ojo derecha, toggle visibilidad. Search: icono lupa + clear button (x) aparece al escribir. |
| **Textarea** | MVP | Operacion | Min-height 80px, max-height 400px, auto-resize opcional. Misma base que input text. Counter de caracteres debajo si hay limite. Scrollbar custom: 6px ancho, fondo transparente, thumb `#C4C0BA`. |
| **Select / Dropdown** | MVP | Operacion | Trigger: igual que input con chevron abajo 12px derecha. Dropdown: overlay, max-height 280px, scroll interno. Items: 36px alto, hover `#E5E2DC`, seleccionado fondo coral 10% + check icon izquierda. Grupos: header con label uppercase 10px ink 50%. |
| **Combobox (autocomplete)** | V1 | Operacion | Input + dropdown filtrado en tiempo real. Debounce: 150ms. Highlight de match en texto: fondo coral 20% bold. Crear opcion nueva al final si no hay match: "+ Crear 'texto'". Loading: spinner 14px dentro del input. |
| **Multi-select** | MVP | Operacion | Tags/chips dentro del input. Chip: fondo `#E5E2DC`, texto ink, x para remover, altura 24px. Input se expande verticalmente. Dropdown con checkboxes. "N seleccionados" cuando hay >3. Select all / clear all en dropdown header. |
| **Checkbox** | MVP | Operacion | 16x16px, border 1.5px ink 30%, border-radius 3px. Checked: fondo coral, border coral, check blanco. Indeterminate: fondo coral, linea blanca horizontal. Focus: outline coral. Grupo: label opcional arriba, stack vertical 8px gap. |
| **Radio** | MVP | Operacion | 16px diametro, border 1.5px ink 30%. Selected: punto interno 8px coral. Grupo: horizontal o vertical. Mutually exclusive. |
| **Toggle (switch)** | MVP | Operacion | 40x22px track, border-radius 11px. Off: fondo `#C4C0BA`, knob 18px blanco. On: fondo coral, knob desplazado 18px derecha. Transicion: 150ms ease-in-out. Label a la derecha 12px Inter 500. |
| **Slider** | V1 | Operacion | Track: 4px alto, fondo `#C4C0BA`, fill coral. Thumb: 16px circulo blanco, border 2px coral, shadow sutil. Tooltip con valor sobre thumb al arrastrar. Range dual para min/max. |
| **Date picker** | V1 | Operacion | Input que abre calendario overlay. Calendario: 280px ancho, header con mes/anio navegable. Dias: 36px celdas cuadradas. Hoy: borde coral. Seleccionado: fondo coral blanco. Rango: fondo coral 20% entre inicio y fin. Presets: "Hoy", "Ultimos 7 dias", "Este mes". |
| **File upload / dropzone** | MVP | Operacion | Area 120px alto, border 2px dashed `#C4C0BA`, border-radius 8px. Icono upload 32px pizarra. Texto: "Arrastra archivos o click para seleccionar". Drag over: border coral, fondo coral 5%. Progreso: barra fina coral con porcentaje. Multiple files: lista con nombre, size, progress individual, x para cancelar. |
| **Form multi-step (wizard)** | MVP | Mix | Header: pasos con indicador de progreso (linea + circulos). Circulo: 28px, activo=coral, completado=check coral, pendiente=gris. Contenido: modo Operacion (formularios compactos). Titulo de paso: modo Lectura (Crimson Pro 24px). Botones: "Atras" secondary, "Siguiente / Finalizar" primary coral. Validacion por paso antes de avanzar. |
| **Form inline (editing en tabla)** | V1 | Operacion | Doble click o icono lapiz activa edicion. Celda se convierte en input 32px alto. Enter = guardar, Escape = cancelar. Valor cambiado: fondo coral 5%, borde izquierdo coral 2px indicando dirty. Guardado exitoso: check verde breve 1s. Error: mensaje tooltip debajo. |
| **Validation errors** | MVP | Operacion | Mensaje debajo del input: Inter 11px, color error `#A94442`, icono warning 12px. Input: border error. Form-level errors: banner arriba del form con resumen. Campo-level: al blur (no en cada keystroke). Submit: scroll al primer error. |
| **Form empty state** | V2 | Lectura | Cuando un formulario se carga sin secciones configuradas (ej: form builder vacio). Ilustracion de telar incompleto. Titulo serif italic: "Cada tejido empieza con un hilo". Descripcion: guia para agregar primer campo. CTA coral grande. |

**Confidence level: HIGH** — Formularios son el segundo pilar despues de tablas; la especificacion cubre desde input basico hasta patrones complejos de edicion inline.

---

### Filtros y busqueda

| Componente | Prioridad | Modo | Spec |
|------------|-----------|------|------|
| **Search bar global** | MVP | Operacion | Input 44px alto, ancho completo del header o max 480px. Icono lupa 18px izquierda. Placeholder: "Buscar agentes, tenants, configuraciones...". Clear button (x) al escribir. Cmd+K shortcut. Debounce 200ms. Resultados en dropdown agrupados por categoria. |
| **Filtro lateral (panel)** | MVP | Operacion | Panel deslizable desde derecha, width 320px, fondo `#FAF9F7`, shadow -4px 0 24px rgba(0,0,0,0.08). Header: "Filtros" + contador de activos + limpiar todo. Secciones colapsables. Footer fijo: "Aplicar N filtros" coral primary. Cerrar: x o click afuera o Escape. |
| **Filtro inline (chips)** | MVP | Operacion | Barra debajo del header de pagina. Chips activos: fondo coral 10%, border coral, texto ink, x para remover. Chip "+ Agregar filtro" abre dropdown de opciones. Scroll horizontal si excede ancho. Max 5 chips visibles, resto en "+N". |
| **Filtro avanzado (query builder)** | V2 | Operacion | Interfaz de condiciones: campo + operador + valor. Filas apilables verticalmente con AND/OR entre ellas. Operadores: es, no es, contiene, empieza con, mayor que, menor que, entre, esta vacio. Grupos con parentesis visuales (indentacion + borde izquierdo). Preview de resultados en vivo. Guardar como filtro guardado. |
| **Saved filters** | V1 | Operacion | Dropdown "Filtros guardados" con lista de filtros previamente salvados. Item: nombre + cantidad de condiciones + usuario + fecha. Acciones: aplicar, renombrar, duplicar, eliminar. Default filters marcados con estrella. Compartidos entre team vs personales. |
| **Search results empty** | MVP | Mix | Si busqueda global sin resultados: modo Lectura — "No encontramos resultados para 'query'" + sugerencias de busqueda + links rapidos. Si filtro de tabla sin resultados: modo Operacion — "Ningun resultado con estos filtros" + boton limpiar. |

**Confidence level: HIGH** — Filtros son esenciales para manejar 50+ agentes y multi-tenant; query builder es V2 porque los filtros basicos cubren 80% de casos.



---

### Feedback y estados

| Componente | Prioridad | Modo | Spec |
|------------|-----------|------|------|
| **Toast (success, warning, error, info)** | MVP | Operacion | Posicion: top-right, 16px de margen, max 3 simultaneos (stack 8px). Width: 360px. Fondo: cream `#FAF9F7`, border izquierdo 3px segun tipo, shadow 0 4px 12px rgba(0,0,0,0.08). Icono tipo 16px izquierda. Titulo: Inter 13px 600. Mensaje: Inter 12px 400. Close: x 14px derecha. Auto-dismiss: 5s (excepto error: manual). Progreso bar fina abajo indicando tiempo restante. Animacion: slide-in desde derecha 200ms, fade-out 150ms. |
| **Modal / Dialog (confirm)** | MVP | Mix | Overlay: fondo ink 40% opacity. Panel centrado: max-width 420px, fondo cream, border-radius 8px, padding 24px. Icono tipo 48px centrado arriba (warning coral para destructivo, info pizarra para informativo). Titulo: Inter 18px 700. Mensaje: Inter 14px 400 ink 80%. Acciones: derecha-alineadas, cancel secondary outline, confirm primary coral (destructivo=coral oscurecido). Cerrar: x arriba-derecha, Escape, click overlay. Animacion: fade-in overlay 150ms, panel scale 0.95→1 + fade 200ms. |
| **Modal / Dialog (form)** | MVP | Operacion | Overlay igual. Panel: max-width 560px, max-height 80vh, scroll interno. Header fijo con titulo + x. Body con formulario. Footer fijo: acciones. Pasos de wizard soportados. Validacion inline. No cerrar al click overlay si hay cambios sin guardar (dirty check). |
| **Modal / Dialog (info)** | V1 | Lectura | Panel mas amplio: max-width 640px. Contenido editorial permitido. Titulo: Crimson Pro 28px italic. Puede incluir imagenes, diagramas. Cerrar: multiple vias. No footer de accion obligatorio. |
| **Drawer / Sidebar panel** | MVP | Operacion | Panel deslizable desde derecha, width 400px (small), 560px (medium), 720px (large). Overlay opcional (click cierra). Header fijo: titulo + x + acciones. Body scrollable. Footer fijo con acciones primarias. Usado para: detalle de agente, edicion de configuracion, preview. Animacion: slide desde derecha 250ms `cubic-bezier(0.4, 0, 0.2, 1)`. |
| **Tooltip** | MVP | Operacion | Fondo ink `#1F1E1C`, texto cream 12px Inter 400. Padding 6px 10px. Border-radius 4px. Flecha 6px apuntando al trigger. Delay: 400ms aparicion, instant desaparicion. Max-width: 240px. Posicion: auto (arriba por defecto, flips si no hay espacio). Z-index alto. |
| **Popover / Dropdown menu** | MVP | Operacion | Panel flotante ligado a trigger. Min-width: 180px, max-width: 320px. Fondo `#FAF9F7`, shadow 0 4px 16px rgba(0,0,0,0.1), border-radius 6px. Items: 36px alto, padding 8px 12px, hover `#E5E2DC`. Separadores: 1px ink 8%. Checkmark para items seleccionados. Keyboard: arrow keys, Enter, Escape. |
| **Loading spinner (agente trabajando)** | MVP | Mix | SVG animado, 24px (inline), 48px (pagina). Track: ink 10%. Indicator: coral. Velocidad: 0.8s/rotacion. Variante "agente trabajando": icono de telar miniatura con hilos animados (3 lineas ondulando). Variante "global": pantalla completa con logo FaberLoom centrado + spinner + texto "Preparando el telar..." en Crimson Pro italic 18px (modo Lectura dentro de contexto Operacion). |
| **Skeleton (carga de contenido)** | MVP | Operacion | Rectangulos redondeados 4px en lugar de contenido real. Colores: fondo `#E5E2DC`, highlight `#EEEBE6` animado. Variantes: texto (height 12-16px), avatar (circulo), card (rectangulo grande), tabla (estructura de filas/columnas). Animacion: shimmer sweep 1.5s ease-in-out infinite. Nunca usar spinners donde se espera skeleton (mantiene layout). |
| **Empty state (generico)** | MVP | Mix | Ilustracion minimalista line-art (telar, hilo, aguja) en pizarra 20% opacity. Titulo: Inter 16px 600. Descripcion: Inter 13px 400 ink 60%. CTA coral si hay accion posible. Sin CTA si es estado transitorio. Modo Lectura cuando es primera vez; modo Operacion cuando es resultado de filtro/busqueda. |
| **Empty state (por categoria)** | V1 | Mix | Variantes especializadas: (a) No agentes: "Todavia no tejiste ningun agente"; (b) No tenants: "Tu taller esta vacio"; (c) No logs: "Sin registros todavia"; (d) No alerts: "Todo en orden — por ahora". Cada uno con icono tematico y CTA especifico. |
| **Error boundary (fallback UI)** | MVP | Mix | Pantalla completa o seccion aislada. Icono warning grande pizarra. Titulo: "Algo se enredo" (modo Lectura: serif italic) o "Error de carga" (modo Operacion). Descripcion: mensaje amigable + detalle tecnico colapsable. Acciones: "Reintentar" coral, "Volver al inicio", "Contactar soporte". Estado: detalle tecnico colapsado por defecto. |
| **Progress bar / Step indicator** | MVP | Operacion | Track: 4px alto, fondo `#C4C0BA`. Fill: coral. Variantes: determinada (porcentaje), indeterminada (shimmer). Step indicator: circulos conectados por linea. Circulo: 24px, activo=coral+numero blanco, completado=coral+check, pendiente=gris. Labels debajo: Inter 11px. |
| **Badge / Tag / Pill** | MVP | Operacion | Height 20px, padding 2px 10px, border-radius 10px. Variantes: default (fondo `#E5E2DC`, texto ink), coral (fondo coral 15%, texto coral oscuro), success (fondo `#2D7A5F15`, texto `#2D7A5F`), warning (fondo `#C9962E15`, texto `#C9962E`), error (fondo `#A9444215`, texto `#A94442`), info (fondo `#4A7FB515`, texto `#4A7FB5`). Dismissible: x 10px al final. |
| **Banner (warning, maintenance, announcement)** | MVP | Mix | Barra horizontal full-width, height 40px. Warning: fondo `#C9962E15`, borde inferior `#C9962E`, icono warning 16px. Maintenance: fondo pizarra 15%, borde pizarra. Announcement: fondo coral 10%, borde coral. Texto: Inter 13px centrado. CTA inline si aplica. Dismissible: x derecha. Sticky debajo del header. |

**Confidence level: HIGH** — Estados de feedback son criticos para un producto agentic donde el usuario delega control; deben comunicar confianza y claridad.

---

### Navegacion

| Componente | Prioridad | Modo | Spec |
|------------|-----------|------|------|
| **Sidebar (collapsible)** | MVP | Operacion | Width expandido: 240px. Colapsado: 56px (iconos solo). Fondo: `#EEEBE6`. Header: isotipo FaberLoom 32px + wordmark (expandido). Secciones: tenant switcher, nav principal (Configurar/Iterar/Sanidad), utilidades (settings, help, logout). Item nav: 40px alto, icono 20px + label 13px, border-radius 6px, hover `#E5E2DC`, activo fondo coral 10% + border-left coral 3px + icono/texto coral. Separadores: 1px ink 8%. Toggle colapsar: chevron al final del sidebar. Persistir estado en localStorage. Animacion: width 250ms ease. |
| **Top nav / Header** | MVP | Operacion | Height 56px, fondo cream `#F4F1ED`, border-bottom 1px ink 8%. Zona izquierda: breadcrumb o titulo de pagina (Inter 16px 600). Zona centro: search bar global (max 480px, oculta en <1024px). Zona derecha: notificaciones (bell icono con dot rojo si hay), avatar usuario (32px circulo, iniciales si no hay foto), dropdown menu. Sticky top. |
| **Breadcrumbs** | MVP | Operacion | Inter 13px 400. Separador: "/" 12px ink 30%. Ultimo item: ink 100% (no link). Items anteriores: ink 60%, hover ink 100% + underline. Max items: 4, si mas: ellipsis con dropdown de items intermedios. En sidebar colapsado: breadcrumbs se mueven al main content area debajo del header. |
| **Tabs (primary)** | MVP | Operacion | Altura 40px. Labels: Inter 13px 500. Indicador activo: linea coral 2px debajo del label, width = label width. Inactivo: ink 50%. Hover inactivo: ink 80%. Tab list: border-bottom 1px ink 8%. Overflow: scroll horizontal con fade indicators, dropdown "Mas" si >5 tabs. Tabs principales del producto (Configurar/Iterar/Sanidad) usan variant primary prominente. |
| **Tabs (secondary)** | MVP | Operacion | Altura 32px. Labels: Inter 12px 500. Fondo: `#E5E2DC`, border-radius 6px (pill style). Activo: fondo cream, shadow sutil, texto ink. Inactivo: texto ink 50%. Usado para subtabs dentro de un tab principal (ej: dentro de Iterar: Agentes/Metrics/Logs). |
| **Tabs (overflow)** | V1 | Operacion | Cuando tabs exceden ancho: fade indicators a izquierda/derecha. Scroll nativo oculto. Contador de tabs ocultos en badge "+N" al final. Dropdown al click en "+N" con lista de tabs restantes. Indicador activo siempre visible (scroll automatico para mantenerlo en viewport). |
| **Pagination** | MVP | Operacion | Controles: "Anterior" / "Siguiente" con iconos flecha, numeros de pagina (max 5 visibles + first/last + ellipsis), input de pagina directa. Botones: 32px cuadrados, border-radius 4px. Activo: fondo coral, texto blanco. Inactivo: hover `#E5E2DC`. Info: "Pagina N de M" opcional. |
| **Command palette / Spotlight search** | V1 | Operacion | Overlay full-screen fondo ink 30%. Panel centrado: max-width 600px, max-height 480px, fondo cream, border-radius 8px. Input en top: 48px, icono search 18px, placeholder "Que queres hacer?". Resultados agrupados por categoria con iconos. Navegacion: arrow keys, Enter selecciona, Escape cierra. Recent commands al inicio. Acciones contextuales segun pagina actual. Shortcut: Cmd+K siempre visible en header. |

**Confidence level: HIGH** — Navegacion es el esqueleto del producto; sidebar + tabs primarios ya estan implicitos en el modelo de 3 tabs de FaberLoom.



---

## Patterns especificos de FaberLoom

### Lista de 50 agentes en paralelo

**Proposito:** El nucleo operativo del tab Iterar. Permitir al hacedor moderno ver, filtrar, monitorear y actuar sobre decenas de agentes simultaneos con minima friccion.

#### Wireframe textual

```
+--------------------------------------------------------------------------+
| [Sidebar]  |  Header: Agentes                              [Q Search] [N]|
|            |  Breadcrumb: Iterar / Agentes                                |
| [Isotipo]  |                                                              |
|            |  +------------------------------------------------------+   |
| Configurar |  | [Todos] [Corriendo] [Pausados] [Con error] [Bloque..]|   |
| [Iterar]   |  +------------------------------------------------------+   |
| Sanidad    |                                                              |
|            |  [Checkbox] [Nombre        v] [Estado v] [Tenant v] [U..  |
| [Agentes]  |  +------------------------------------------------------+   |
| [Metrics]  |  |  | Nombre        | Estado    | Tenant   | Ult exec | A |   |
| [Logs]     |  |--+---------------+-----------+----------+----------+---|   |
|            |  |  | DataSync-N... | Running   | Acme Co  | 12s ago  |...|   |
|            |  |  | WebScraper... | Success   | Beta LLC | 2m ago   |...|   |
|            |  |  | EmailClas...  | Error     | Acme Co  | 5m ago   |...|   |
|            |  |  | ReportGen...  | Waiting   | Gamma In | 15m ago  |...|   |
|            |  |  | + 46 mas... (scroll virtualizado)                    |   |
|            |  |--+---------------+-----------+----------+----------+---|   |
|            |  |  Mostrando 50 de 247 agentes  [1] [2] [3] ... [25] [>]|   |
|            |  +------------------------------------------------------+   |
|            |                                                              |
|            |  [Bulk bar flotante: 12 seleccionados  [Pausar] [Reiniciar] |
|            |   [Eliminar] [Cancelar] ]  ← aparece al seleccionar        |
|            |                                                              |
+--------------------------------------------------------------------------+

Fila expandida (ej: EmailClassifier-01):
+--------------------------------------------------------------------------+
|  | EmailClassifier-01 | Error  | Acme Co  | 5m ago  | [...]            |
|  +---------------------------------------------------------------------+ |
|  | [Logs] [Config] [Variables]                                    [X] | |
|  |---------------------------------------------------------------------| |
|  | 2026-01-15 14:32:01 ERROR Connection timeout to imap.acme.co:993   | |
|  | 2026-01-15 14:32:00 INFO  Retrying (3/3)...                       | |
|  | 2026-01-15 14:31:55 WARN  Rate limit detected, backing off 5s      | |
|  | 2026-01-15 14:31:50 INFO  Connecting to imap.acme.co...            | |
|  |                                                                    | |
|  | [Ver logs completos →]          [Reintentar ahora] [Editar config] | |
+--------------------------------------------------------------------------+

Drawer de detalle (al hacer click en nombre o "Ver detalle"):
+--------------------------------------------------+------------+-------------+
|                                                  |  Detail: EmailClassifier   |
|  (tabla de agentes sigue visible atras,           |  ======================    |
|   con overlay semi-transparente)                  |                            |
|                                                  |  Estado: [Error] [Retry]   |
|                                                  |  Tenant: Acme Co           |
|                                                  |  Creado: 2026-01-10        |
|                                                  |  Version: v1.2.3           |
|                                                  |                            |
|                                                  |  --- Metricas ---          |
|                                                  |  Exec hoy: 247 | OK: 198   |
|                                                  |  Errores: 12   | Avg: 3.2s |
|                                                  |                            |
|                                                  |  --- Log tail (50 lines)   |
|                                                  |  [stream en tiempo real]   |
|                                                  |                            |
|                                                  |  [Editar] [Pausar] [Logs]  |
+--------------------------------------------------+----------------------------+
```

#### Especificacion completa

**Estados de agente (maquina de estados visual):**

| Estado | Color | Icono | Animacion | Significado |
|--------|-------|-------|-----------|-------------|
| **Idle** | ink 40% | circulo vacio | ninguna | Agente configurado, nunca ejecutado |
| **Running** | coral | spinner 12px | rotacion continua | Agente ejecutando tarea ahora |
| **Waiting** | `#C9962E` | reloj de arena | pulse suave 2s | Agente en cola, esperando recurso |
| **Success** | `#2D7A5F` | check circulo | ninguna | Ultima ejecucion exitosa |
| **Error** | `#A94442` | x circulo | shake breve al aparecer | Ultima ejecucion fallo |
| **Blocked** | `#5A6B7C` | candado | ninguna | Agente bloqueado por dependencia o permiso |
| **Paused** | ink 60% | pause circulo | ninguna | Agente pausado manualmente |

**Filtros rapidos por estado:**
- Tabs de filtro justo debajo del titulo de pagina
- Cada tab muestra contador (e.g., "Con error (12)")
- "Todos" es el default
- Filtros son OR exclusivo (un solo estado a la vez, o todos)
- Al cambiar de tab, tabla se refresca con skeleton 300ms

**Acciones bulk:**
- Checkbox en header selecciona todas las visibles (pagina actual)
- Checkbox en header con menu desplegable: "Seleccionar todos (247)" o "Solo visibles (50)"
- Barra flotante aparece al seleccionar >=1: slide-up desde bottom 150ms
- Acciones disponibles dependen de seleccion:
  - Mix de estados: [Pausar] [Eliminar]
  - Algunos Running: [Pausar] [Eliminar]
  - Algunos Paused: [Reanudar] [Eliminar]
  - Algunos Error: [Reintentar] [Pausar] [Eliminar]
  - Todos seleccionados: todas las acciones aplicables
- Accion destructiva (Eliminar): confirm modal con nombre de agentes listados (max 5, luego "y N mas")

**Detail panel (drawer):**
- Se abre al click en nombre de agente o icono "expand"
- Width: 480px
- Header: nombre del agente + estado badge + acciones inline
- Tabs: Overview / Logs / Config / Variables / History
- Overview: metricas clave en mini-cards 2x2, sparkline de ejecuciones ultimas 24h, info basica
- Logs: stream en tiempo real (WebSocket), auto-scroll hasta que usuario haga scroll manual, boton "Resumir auto-scroll" si se detuvo
- Config: formulario de configuracion del agente (json editable con syntax highlighting, o form fields si hay schema)
- Variables: tabla de variables de entorno, editable inline
- History: tabla de ejecuciones pasadas con timestamp, duracion, estado, link a logs de esa ejecucion

**Log stream en tiempo real:**
- Fuente: JetBrains Mono 11px, line-height 1.5
- Colores: timestamp gris 50%, level INFO ink, WARN `#C9962E`, ERROR `#A94442`, DEBUG ink 40%
- Altura: min 200px, max 500px dentro de drawer, scroll interno
- Auto-scroll: siempre a menos que usuario scrollee manualmente
- Pause: click en area de logs pausa stream; icono "play" aparece para reanudar
- Busqueda: Ctrl+F abre buscador inline que filtra lineas visibles
- Export: boton "Exportar" descarga .log file

**Confidence level: HIGH** — Este es el pattern mas critico del producto; 50 agentes en paralelo es el core value proposition.

---

### Dashboard multi-tenant

**Proposito:** Permitir a usuarios con acceso a multiples tenants/workspaces (agencias, consultoras, equipos) switchear, monitorear y administrar cada uno sin perder contexto.

#### Wireframe textual

```
+--------------------------------------------------------------------------+
| [Sidebar]  |  Header: Dashboard Acme Co            [Q] [Bell.] [A] [v] |
|            |                                                              |
| [Isotipo]  |  +--------------+  +--------------+  +------------------+  |
|            |  |  Tenant      |  |  Agente activo|  |  Alertas activas  |  |
|            |  |  Switcher    |  |  mas rapido   |  |                  |  |
|            |  |              |  |               |  |  [2] Warning    |  |
|            |  | [Acme Co  v] |  | DataSync-Pro  |  |  [1] Error      |  |
|            |  |              |  | 2.3s avg exec |  |                  |  |
|            |  | Plan: Pro    |  |               |  | [Ver todo →]    |  |
|            |  | 12/50 agents |  | [Ver detalle] |  |                  |  |
|            |  |              |  |               |  +------------------+  |
| Configurar |  +--------------+  +--------------+                       |
| [Iterar]   |  +--------------+  +--------------+  +------------------+  |
| Sanidad    |  |  Agentes hoy |  |  Exec rate   |  |  Health score    |  |
|            |  |              |  |              |  |                  |  |
|            |  |  1,247       |  |  ████████    |  |  [=======84%]   |  |
|            |  |  ejecuciones |  |  98.2% OK    |  |  Ultimo check    |  |
|            |  |              |  |  1.8% Error  |  |  hace 12 min    |  |
|            |  | [+12% vs ayer]|  |              |  |                  |  |
|            |  +--------------+  +--------------+  +------------------+  |
|            |                                                              |
|            |  +------------------------------------------------------+   |
|            |  |  Tabla: Agentes recientes                            |   |
|            |  |  (ultimas 10 ejecuciones con status)                 |   |
|            |  |  [Ver todos los agentes →]                            |   |
|            |  +------------------------------------------------------+   |
|            |                                                              |
|            |  +------------------------------------------------------+   |
|            |  |  Timeline: Actividad reciente por tenant             |   |
|            |  |  [mini sparklines apilados por tenant]               |   |
|            |  +------------------------------------------------------+   |
|            |                                                              |
+--------------------------------------------------------------------------+

Tenant Switcher (dropdown abierto):
+--------------------------------------------------------------------------+
|  Acme Co                                            [v] Active          |
|  --------------------------                                            |
|  [Q Buscar tenants...]                                                 |
|  --------------------------                                            |
|  [A] Acme Co              Plan Pro    12/50 agents    [Check] Active  |
|  [B] Beta LLC             Plan Team   8/25 agents     [Check]         |
|  [G] Gamma Inc            Pro Trial   3/10 agents     [Check]         |
|  [D] Delta Studio         Plan Pro    47/50 agents    [!] Warning    |
|  --------------------------                                            |
|  [+ Crear nuevo tenant]                                                |
|  [Gestionar tenants →]                                                 |
+--------------------------------------------------------------------------+

Overview por tenant (vista administrativa):
+--------------------------------------------------------------------------+
| Tabla: Tenants                                                          |
|                                                                         |
| Tenant       | Plan  | Agentes | Exec 24h | Health | Alerts | Acciones  |
|--------------+-------+---------+----------+--------+--------+-----------|
| Acme Co      | Pro   | 12/50   | 1,247    | 94%    | 2W 0E  | [...]     |
| Beta LLC     | Team  | 8/25    | 843      | 87%    | 1W 1E  | [...]     |
| Gamma Inc    | Trial | 3/10    | 156      | 100%   | 0      | [...]     |
| Delta Studio | Pro   | 47/50   | 4,521    | 76%    | 5W 3E  | [...]     |
|              |       |         |          |        |        |           |
| [Export CSV]                                    [Ver detalle de cada →] |
+--------------------------------------------------------------------------+
```

#### Especificacion completa

**Tenant / Workspace switcher:**
- Ubicacion: sidebar header (expandido) o top-nav (colapsado)
- Trigger: click en nombre actual del tenant + chevron
- Dropdown: lista de tenants con acceso, ordenados por recencia de uso
- Cada item: inicial coloreada (generada por hash del nombre), nombre, plan, uso (agentes/limite)
- Tenant activo: checkmark coral, fondo coral 5%
- Busqueda: filtra tenants si hay >5
- Acciones footer: "Crear nuevo tenant" (modal form), "Gestionar tenants" (vista admin)
- Cambio de tenant: recarga completa del dashboard con skeleton global, 300ms transition
- Persistencia: ultimo tenant activo en localStorage

**Overview de uso por tenant:**
- Cards KPI en fila: Total ejecuciones hoy, tasa de exito, agentes activos, health score promedio
- Sparkline en cada card: variacion ultimas 24h
- Variacion vs periodo anterior: badge +/- con porcentaje, color verde/rojo
- Tabla de agentes recientes: ultimas 10 ejecuciones con timestamp, agente, estado, duracion

**Alertas por tenant:**
- Card dedicada en dashboard con contadores por severidad
- Warning: `#C9962E` badge — agentes con errores intermitentes, rate limit, etc.
- Error: `#A94442` badge — agentes con fallos consecutivos, configuracion invalida, etc.
- Info: `#4A7FB5` badge — anuncios de limite de plan proximo, etc.
- Cada alerta: clickable, abre drawer con detalle y accion sugerida
- Alertas agrupadas por tipo: "3 agentes con error de conexion" en lugar de 3 alertas individuales

**Configuracion por tenant:**
- Vista accesible desde switcher → "Gestionar tenants"
- Tabla de tenants con: nombre, plan, limite agentes, usuarios, fecha creacion, estado
- Acciones: editar nombre/plan, pausar tenant (suspende todos sus agentes), eliminar (con confirmacion extrema)
- Configuracion de billing y plan
- Invitacion de usuarios por tenant (email + rol)
- Logo/branding por tenant (opcional, V2)

**Seguridad y aislamiento visual:**
- Cada tenant tiene color generado deterministicamente por hash del nombre (usado en avatares y badges)
- Datos de un tenant nunca se mezclan visualmente con otro
- Al cambiar de tenant, titulo de pagina y favicon indicator se actualizan
- Banner opcional si el tenant esta en plan trial con dias restantes

**Confidence level: HIGH** — Multi-tenancy es un requisito B2B fundamental; esta spec cubre las necesidades de agencias y consultoras.



---

### Log de auditoria con hash chaining

**Proposito:** Proporcionar una trazabilidad completa e inmutable de todas las acciones en FaberLoom. Cada evento se registra con un hash que encadena con el hash anterior, formando una cadena verificable. Es diferenciador competitivo para compliance (SOC2, ISO27001) y genera confianza en el Trust Ladder.

#### Wireframe textual

```
+--------------------------------------------------------------------------+
| [Sidebar]  |  Header: Auditoria                               [Q] [N] [A]|
|            |                                                              |
| [Isotipo]  |  Breadcrumb: Configurar / Seguridad / Auditoria            |
|            |                                                              |
| Configurar |  +------------------------------------------------------+   |
| [Iterar]   |  | Filtros: [Evento v] [Actor v] [Fecha range] [Tenant v]  |
| Sanidad    |  | [Aplicar] [Guardar filtro] [Exportar CSV]              |   |
|            |  +------------------------------------------------------+   |
|            |                                                              |
|            |  Hash chain integrity: [Verificado] Ultimo bloque: #184,729|
|            |  hace 3s  [Verificar cadena completa]                      |
|            |                                                              |
|            |  +------------------------------------------------------+   |
|            |  | #     | Timestamp       | Actor     | Accion       | Hash|
|            |  |-------+-----------------+-----------+--------------+-----|
|            |  |184729 | 2026-01-15 14:32| juan@acme | AGENT_UPDATE | a3f7|
|            |  |184728 | 2026-01-15 14:31| system    | AGENT_EXEC   | 9e2b|
|            |  |184727 | 2026-01-15 14:31| maria@bet | TENANT_CONFIG| 5d1c|
|            |  |184726 | 2026-01-15 14:30| system    | AGENT_ERROR  | 8a4e|
|            |  |184725 | 2026-01-15 14:28| juan@acme | USER_LOGIN   | 2f09|
|            |  |  ... scroll virtualizado (1000+ eventos/min en peak)   |
|            |  |       |                 |           |              |     |
|            |  +------------------------------------------------------+   |
|            |                                                              |
|            |  Mostrando 1-50 de 184,729 eventos    [1][2][3]...[3695][>]|
|            |                                                              |
+--------------------------------------------------------------------------+

Fila expandida (evento #184729 - AGENT_UPDATE):
+--------------------------------------------------------------------------+
| #184729 | 2026-01-15 14:32:01 | juan@acme.co | AGENT_UPDATE | a3f7..e2  |
| +-----------------------------------------------------------------------+|
| | Bloque #184729                                                         ||
| | =====================================================================  ||
| | Timestamp:   2026-01-15 14:32:01.247 UTC                               ||
| | Actor:       juan@acme.co (ID: user_8a3f, Rol: Admin)                  ||
| | IP:          203.0.113.42                                              ||
| | User Agent:  Mozilla/5.0 (FaberLoom Web App)                           ||
| | Accion:      AGENT_UPDATE                                              ||
| | Target:      agent_EmailClassifier_01 (Tenant: Acme Co)                ||
| | Cambios:    [diff JSON, colapsable]                                    ||
| |   - config.timeout: 30 → 45                                            ||
| |   - config.retryPolicy: "linear" → "exponential"                       ||
| |                                                                        ||
| | Hash anterior:  9e2b..1a  (#184728)                                    ||
| | Hash propio:    a3f7..e2  (SHA-256 truncado)                           ||
| | Hash encadenado: c8d1..4f  (SHA-256(prev_hash + data))                ||
| |                                                                        ||
| | [Verificar este bloque]  [Copiar hash]  [Ver bloque anterior]          ||
| +-----------------------------------------------------------------------+|
+--------------------------------------------------------------------------+

Visualizacion de cadena de hashes (vista alternativa):
+--------------------------------------------------------------------------+
|                                                                          |
|  [Genesis] <-- #1 <-- #2 <-- ... <-- [#184725] <-- [#184726] <-- [...]  |
|    block     block   block           [user_lgn]  [agt_err]              |
|              |        |                                              |
|              |        +--- AGENT_CREATE (maria@beta)                   |
|              +--- USER_INVITE (admin@acme)                              |
|                                                                          |
|  Cada bloque: rectangulo con numero, tipo de evento (icono), timestamp. |
|  Conexiones: lineas curvas con hash truncado en tooltip al hover.       |
|  Bloques sospechosos (hash mismatch): borde rojo, animacion pulse.      |
|                                                                          |
|  [Vista tabla] [Vista cadena] [Verificar integridad]                    |
|                                                                          |
+--------------------------------------------------------------------------+
```

#### Especificacion completa

**Tabla de eventos:**
- Columnas: # (numero de bloque), Timestamp (ISO 8601, local TZ), Actor (email o "system"), Accion (tipo de evento), Target (objeto afectado), Hash (SHA-256 truncado a 8 chars)
- Fila: 44px alto, monospace para # y hash, Inter para resto
- Timestamp: formato relativo por defecto ("hace 3s", "hace 2m"), tooltip con absoluto
- Actor: avatar 20px con iniciales + email. "system" con icono engranaje
- Accion: badge con tipo, colores semanticos segun categoria (AUTH, AGENT, TENANT, USER, BILLING)
- Hash: texto monospace 11px, color ink 60%, tooltip con hash completo al hover

**Tipos de evento (categorias y colores):**

| Categoria | Eventos tipicos | Color badge |
|-----------|-----------------|-------------|
| AUTH | USER_LOGIN, USER_LOGOUT, SESSION_EXPIRED | `#4A7FB5` |
| AGENT | AGENT_CREATE, AGENT_UPDATE, AGENT_DELETE, AGENT_EXEC, AGENT_ERROR | coral `#C96442` |
| TENANT | TENANT_CREATE, TENANT_CONFIG, TENANT_PAUSE, TENANT_DELETE | `#5A6B7C` |
| USER | USER_INVITE, USER_ROLE_CHANGE, USER_REMOVE | ink 60% |
| BILLING | PLAN_CHANGE, PAYMENT_SUCCESS, PAYMENT_FAILED | `#2D7A5F` |
| SYSTEM | BACKUP_COMPLETE, MAINTENANCE_MODE, HASH_VERIFICATION | ink 40% |

**Visualizacion de cadena de hashes:**
- Vista alternativa a la tabla: diagrama horizontal de bloques conectados
- Cada bloque: rectangulo 120x48px, border-radius 4px, fondo `#FAF9F7`, borde 1px ink 12%
- Contenido: numero de bloque grande arriba, tipo de evento abajo con icono
- Conexiones: lineas SVG curvas entre bloques, flecha a la derecha
- Hash de conexion: visible en tooltip al hover de cada linea
- Zoom: scroll wheel para zoom in/out, drag para pan
- Navegacion rapida: input "Ir a bloque #" para saltar
- Bloques recientes a la derecha, genesis a la izquierda
- Bloque con hash mismatch (verificacion fallida): borde `#A94442` 2px, animacion pulse rojo

**Filtro por tipo de evento:**
- Filtro inline chips: AUTH, AGENT, TENANT, USER, BILLING, SYSTEM
- Filtro por actor: combobox con emails de usuarios del tenant
- Filtro por fecha: date range picker con presets (hoy, ultima semana, ultimo mes)
- Filtro por tenant (solo vista super-admin): dropdown de tenants
- Filtros combinables con AND

**Export:**
- Formatos: CSV, JSON, JSONL
- Rango: respetando filtros aplicados
- Hash completo incluido en export (no truncado)
- Max export: 100,000 eventos por archivo (paginado si mas)
- Procesamiento async: si >10,000 eventos, se genera en background y se notifica via email/toast

**Verificacion de integridad:**
- Boton "Verificar cadena" inicia proceso de validacion de todos los hashes
- Progreso: modal con barra de progreso y bloques verificados por segundo
- Resultado: verde "Cadena verificada — N bloques, 0 inconsistencias" o rojo "Inconsistencia detectada en bloque #X"
- Verificacion continua: badge en header indica estado de ultima verificacion
- Si se detecta inconsistencia: banner de emergencia en todo el producto, notificacion a admins

**Confidence level: HIGH** — El hash chaining es diferenciador clave para compliance y trust; la implementacion es tecnica pero la UI debe mantenerse simple y confiable.

---

### Panel Sanidad (QA / Scorecard)

**Proposito:** El tab Sanidad es donde el hacedor moderno verifica que todo funciona correctamente. Muestra un scorecard con metricas de calidad, checks automatizados, historial de scores y acciones correctivas sugeridas. Es el lugar donde la autonomia progresiva del Trust Ladder se valida.

#### Wireframe textual

```
+--------------------------------------------------------------------------+
| [Sidebar]  |  Header: Sanidad                                    [Q] [A] |
|            |                                                              |
| [Isotipo]  |  +------------------------------------------------------+   |
|            |  |  Sanidad general: [==========84%] Bueno               |   |
|            |  |  Ultimo check: hace 12 minutos | Proximo: en 48 min   |   |
|            |  |  [Ejecutar check ahora]  [Ver historial →]            |   |
|            |  +------------------------------------------------------+   |
|            |                                                              |
| Configurar |  +------------------+  +------------------+  +------------+ |
| [Iterar]   |  |  Confiabilidad   |  |  Rendimiento     |  |  Seguridad | |
| [Sanidad]  |  |                  |  |                  |  |            | |
|            |  |  [====92%]       |  |  [====67%]       |  | [====95%]  | |
|            |  |  11/12 pass      |  |  8/12 pass       |  |  10/10 pass| |
|            |  |  1 warning       |  |  3 warning       |  |  0 warning | |
|            |  |  0 fail          |  |  1 fail          |  |  0 fail    | |
|            |  |                  |  |                  |  |            | |
|            |  | [Ver checks →]   |  | [Ver checks →]   |  | [Ver checks→| |
|            |  +------------------+  +------------------+  +------------+ |
|            |                                                              |
|            |  +------------------------------------------------------+   |
|            |  |  Checks recientes (ultimas 24h)                      |   |
|            |  |  [Timeline con puntos de color: verde/amarillo/rojo] |   |
|            |  +------------------------------------------------------+   |
|            |                                                              |
|            |  +------------------------------------------------------+   |
|            |  |  Tabla de checks                                     |   |
|            |  |                                                      |   |
|            |  | Check              | Categoria  | Estado | Score | A.. |   |
|            |  |--------------------+------------+--------+-------+-----|   |
|            |  | Agent timeout conf | Rendimiento| FAIL   | 45%   | [...]|  |
|            |  | DB connection pool | Rendimiento| WARN   | 72%   | [...]|  |
|            |  | API rate limits    | Confiab..  | PASS   | 98%   | [...]|  |
|            |  | Error retry logic  | Confiab..  | PASS   | 100%  | [...]|  |
|            |  | Secret rotation    | Seguridad  | PASS   | 95%   | [...]|  |
|            |  | TLS cert expiry    | Seguridad  | PASS   | 87d   | [...]|  |
|            |  | ...                                                |   |
|            |  +------------------------------------------------------+   |
|            |                                                              |
+--------------------------------------------------------------------------+

Detalle de check (drawer):
+--------------------------------------------------+------------+-------------+
|                                                  | Check: Agent timeout conf  |
|  (tabla de checks visible atras)                 | =========================  |
|                                                  |                            |
|                                                  | Estado: [FAIL]             |
|                                                  | Score: 45%                 |
|                                                  | Categoria: Rendimiento     |
|                                                  |                            |
|                                                  | --- Descripcion ---        |
|                                                  | Los agentes estan config.. |
|                                                  | con timeout de 30s pero el |
|                                                  | 90% de las ejecuciones     |
|                                                  | necesitan >45s.            |
|                                                  |                            |
|                                                  | --- Historial (7 dias) --- |
|                                                  | [sparkline: bajando]       |
|                                                  | Lun: 82% → Dom: 45%        |
|                                                  |                            |
|                                                  | --- Accion correctiva ---  |
|                                                  | [!] Aumentar timeout a 60s |
|                                                  |     [Aplicar ahora]        |
|                                                  |                            |
|                                                  | [Ignorar este check]       |
|                                                  | [Ver documentacion →]      |
+--------------------------------------------------+----------------------------+
```

#### Especificacion completa

**Scorecard general:**
- Score principal: porcentaje grande (Inter 48px 700) con color segun rango
- Barra de progreso: 8px alto, full width del card, degradado sutil
- Rango de colores: 90-100% `#2D7A5F` (Excelente), 75-89% `#C9962E` (Bueno), 50-74% coral (Regular), 0-49% `#A94442` (Critico)
- Metadata: ultimo check (timestamp relativo), proximo check programado, frecuencia (cada 1h por defecto)
- Accion: "Ejecutar check ahora" (primary coral), "Ver historial" (secondary link)

**Score por categoria:**
- 3-5 categorias configurables (default: Confiabilidad, Rendimiento, Seguridad, Mantenibilidad)
- Cada categoria: card con score, conteo de pass/warning/fail, lista de checks que lo componen
- Score de categoria: promedio ponderado de sus checks
- Orden: categorias con fail primero, luego warning, luego pass

**Checks individuales:**
- Tabla con: nombre del check, categoria, estado, score/valor, ultima ejecucion, acciones
- Estado visual:

| Estado | Icono | Color | Significado |
|--------|-------|-------|-------------|
| **Pass** | check circulo relleno | `#2D7A5F` | Check exitoso, dentro de umbrales |
| **Warning** | signo exclamacion triangulo | `#C9962E` | Cerca del limite o degradacion detectada |
| **Fail** | x circulo | `#A94442` | Fuera de umbrales, accion requerida |
| **Skipped** | circulo punteado | ink 30% | No aplica o no se pudo ejecutar |
| **Running** | spinner | coral | Ejecutandose ahora |

- Score: porcentaje para checks cuantitativos, valor absoluto para cualitativos (ej: "87 dias" para certificado TLS)
- Filtros: por categoria, por estado, por severidad

**Detalle de cada check (drawer):**
- Header: nombre + estado badge + score
- Descripcion: que mide este check y por que importa (modo Lectura: texto explicativo, 14px line-height 1.6)
- Umbrales: tabla con umbrales configurados (warning en X, fail en Y)
- Resultado actual: valor medido + comparacion con umbrales
- Historial: sparkline de los ultimos 7-30 dias, tabla de ejecuciones con fecha y score
- Accion correctiva sugerida:
  - Si pass: "Todo en orden. Revisa el historial para detectar degradaciones tempranas."
  - Si warning: "Atencion: [descripcion del riesgo]. Sugerencia: [accion concreta]."
  - Si fail: "Accion requerida: [descripcion del problema]. [Boton para aplicar fix automatico si disponible] o [Link a documentacion para fix manual]."
- Acciones: "Aplicar sugerencia" (si hay fix automatico), "Ignorar este check" (con razon obligatoria y expiracion), "Ver documentacion"

**Historial de scores:**
- Vista dedicada: line chart con linea por categoria + linea de score general
- Eje X: tiempo (selectable: ultima semana, mes, trimestre)
- Eje Y: 0-100%
- Lineas: general = coral gruesa 3px, categorias = colores atenuados 2px
- Puntos de cambio: anotaciones cuando se aplico una accion correctiva
- Brush/zoom: seleccionar rango para hacer zoom
- Export: PNG/SVG del chart

**Accion correctiva sugerida:**
- Sistema de sugerencias basado en reglas + ML (V2)
- Cada check puede tener 1-3 acciones sugeridas ordenadas por impacto
- Acciones automaticas: "Aumentar timeout a 60s en todos los agentes del tenant" → boton "Aplicar" con confirm modal que muestra diff
- Acciones manuales: link a documentacion paso a paso
- Tracking: cuando el usuario aplica una sugerencia, se registra en auditoria y se mide impacto en proximo score

**Checks predefinidos (MVP):**

| Check | Categoria | Que mide | Umbral warning | Umbral fail |
|-------|-----------|----------|----------------|-------------|
| Agent timeout config | Rendimiento | Timeout vs duracion real | 80% uso | >100% uso |
| DB connection pool | Rendimiento | Conexiones disponibles | <20% libre | <10% libre |
| API rate limit usage | Rendimiento | Uso de rate limits | >70% | >90% |
| Error rate 24h | Confiabilidad | % de ejecuciones con error | >2% | >5% |
| Retry exhaustion | Confiabilidad | Agente que agota retries | >5% casos | >20% casos |
| Secret rotation age | Seguridad | Dias desde ultima rotacion | >80 dias | >90 dias |
| TLS cert expiry | Seguridad | Dias hasta expiracion | <30 dias | <7 dias |
| Password policy | Seguridad | Fuerza de passwords de equipo | <80% fuerte | <50% fuerte |
| Agent version drift | Mantenibilidad | Agentes en version vieja | >20% | >50% |
| Config consistency | Mantenibilidad | Variaciones de config inesperadas | >10% | >30% |

**Confidence level: HIGH** — Panel Sanidad es tab principal del producto; esta spec balancea informacion densa con claridad para toma de decisiones rapidas.



---

## Reglas de implementacion para agentes IA

Esta seccion es una guia operativa para que agentes de IA generen componentes de FaberLoom consistentemente. Sigue estas reglas para mantener el sistema de densidad dual sin quebrar el voice de marca.

### 1. Identificar el modo antes de generar

**Nunca asumas el modo.** Antes de escribir cualquier JSX/CSS, determina:

1. **En que tab/contexto vive este componente?**
   - Configurar, Iterar, Sanidad → 90% Operacion
   - Landing, Documentacion, Onboarding inicial → Lectura
   - Reportes exportados, empty states educativos → Lectura

2. **El usuario esta leyendo o actuando?**
   - Leyendo → verificar si necesita modo Lectura
   - Actuando (configurando, monitoreando, decidiendo) → Operacion

3. **Cuantas decisiones por minuto tomara el usuario aqui?**
   - >3 decisiones/minuto → Operacion obligatorio
   - <1 decision/minuto → puede ser Lectura

**Checklist mental:**
```
□ Identifique el modo correcto (Lectura/Operacion/Mix)
□ Verifique que la tipografia corresponde al modo
□ Verifique que el espaciado corresponde al modo
□ Verifique que el uso de coral es apropiado al modo
□ Asegure que la transicion desde/hacia este componente es coherente
```

### 2. Reglas tipograficas inquebrantables

| Regla | Consecuencia de romperla |
|-------|-------------------------|
| Crimson Pro Italic 500 **solo** en display H1-H3, titulos de seccion editorial, citas, estados empty celebratorios | Si se usa en tablas o forms: rompe legibilidad, se siente pretencioso |
| Inter 700 **solo** en titulos de pagina modo Operacion, labels de seccion, nav items activos | Si se usa en body text: crea fatiga visual, pierde jerarquia |
| Inter 400 para todo body text en ambos modos | Si se reemplaza por bold: se pierde la calma del voice |
| JetBrains Mono **exclusivamente** para datos tecnicos: logs, hashes, timestamps, codigo, JSON | Si se usa para UI labels: se siente tecnico en exceso |
| Nunca usar font-size <10px en texto UI legible | Inaccesible, ilegal en muchas jurisdicciones |
| Line-height minimo 1.4 en Operacion, 1.6 en Lectura | Menos = texto apretado e ilegible |

### 3. Reglas de color

| Regla | Token/rango | Consecuencia |
|-------|-------------|--------------|
| El cream `#F4F1ED` siempre es el fondo base | `--bg-base` | Fondo blanco puro rompe la marca |
| El ink `#1F1E1C` siempre es el texto principal | `--text-primary` | Negro puro `#000000` es demasiado duro |
| El coral `#C96442` es acento exclusivo | `--accent` | Nunca usar como fondo de superficie grande |
| Coral nunca excede 5% de la superficie visible en modo Operacion | — | Mas = visual noise, pierde funcionalidad |
| En modo Lectura, coral puede ser mas prominente (hasta 15%) | — | CTAs, acentos decorativos, links |
| Estados semanticos (success/warning/error/info) son para estados, no para branding | `--status-*` | Mezclar con branding crea confusion |
| Texto en fondo oscuro (ink): siempre cream `#F4F1ED`, nunca blanco puro | `--text-inverse` | Blanco puro en ink es demasiado contrastante |
| Bordes: nunca mas de 1px en modo Operacion | — | Bordes gruesos suman peso visual innecesario |
| Opacidad minima para texto funcional: 40% | — | Menos = ilegible en pantallas de baja calidad |

### 4. Reglas de espaciado

| Regla | Token | Consecuencia de romper |
|-------|-------|----------------------|
| En Operacion: 8px base unit, multiplos (8, 16, 24, 32, 48) | `--space-*` | Espaciado arbitrario = inconsistencia visual |
| En Lectura: 12px base unit, multiplos (12, 24, 36, 48, 64) | `--space-lg-*` | Mezclar base units entre modos rompe la transicion |
| Padding de tabla (celdas): 10px vertical, 12px horizontal | `--cell-padding` | Menos = datos amontonados, mas = desperdicio de espacio |
| Gap entre botones de accion inline: 8px | `--action-gap` | Mas = acciones dispersas, menos = riesgo de click erroneo |
| Altura de fila de tabla: 44px (+-2px) | `--row-height` | Mas = menos datos visibles, menos = targets de click pequenos |
| Max-width de contenido modo Lectura: 720px para texto, 1200px para layouts | `--content-max` | Lineas de texto largas = fatiga de lectura |
| Sidebar expandido: 240px, colapsado: 56px | `--sidebar-*` | Cambiar estos valores requiere recalcular todo el grid |

### 5. Reglas de componentes

**Tablas:**
- Siempre implementar header sticky (se ve al scrollear)
- Siempre implementar filas alternadas o hover claro (facilita seguir fila)
- Siempre usar `title` attribute o tooltip en celdas truncadas
- Nunca truncar hash, timestamp, o estado sin tooltip de valor completo
- Checkbox de seleccion en columna fija a la izquierda (no scrollea horizontalmente)
- Si hay >100 filas: paginacion obligatoria, virtualizacion recomendada

**Formularios:**
- Label siempre arriba del input (no inline, no placeholder como label)
- Mensaje de error siempre debajo del input, nunca solo color rojo
- Input de 36px alto, nunca menos (target touch-friendly)
- Boton submit primario siempre visible, nunca requiriendo scroll
- Validar en blur, no en keystroke (excepto password strength)
- Dirty check antes de cerrar modal/drawer con cambios sin guardar

**Filtros:**
- Filtros aplicados deben ser visibles siempre (chips o contador)
- "Limpiar filtros" debe ser accessible en <=2 clicks desde cualquier estado filtrado
- Search debe tener debounce (200ms) y loading indicator
- Resultados filtrados deben mostrar contador ("N resultados")

**Feedback:**
- Toast de exito: auto-dismiss 5s
- Toast de error: manual dismiss obligatorio
- Toast nunca bloquea acciones del usuario (no modal)
- Modal de confirmacion destructiva: requerir typing del nombre del objeto para delete tenant/workspace
- Loading states: skeleton preferido sobre spinner (mantiene layout)

### 6. Reglas de animacion

| Contexto | Duracion maxima | Easing | Propiedad |
|----------|-----------------|--------|-----------|
| Modo Operacion — micro-interacciones | 150ms | `cubic-bezier(0.4, 0, 0.2, 1)` | background-color, border-color, opacity |
| Modo Operacion — aparicion de paneles | 200-250ms | `cubic-bezier(0.4, 0, 0.2, 1)` | transform, opacity |
| Modo Lectura — transiciones de seccion | 400-600ms | `cubic-bezier(0.25, 0.1, 0.25, 1)` | transform, opacity, margin |
| Modo Lectura — entrada de elementos | 500ms + stagger | `cubic-bezier(0.25, 0.1, 0.25, 1)` | transform, opacity |
| Skeleton loading | 1500ms | ease-in-out | background-position (shimmer) |
| Spinner | 800ms | linear | transform (rotation) |

**Prohibiciones animacion:**
- ❌ Nunca animar width/height (causa reflow, jank)
- ❌ Nunca usar `all` en transitions (especifico siempre)
- ❌ Nunca superar 600ms en cualquier transicion (se siente lento)
- ❌ Nunca usar animaciones de entrada en modo Operacion (solo fade instant o 100ms)
- ❌ Nunca usar `!important` en animaciones

### 7. Reglas de responsividad

| Breakpoint | Ancho | Cambios principales |
|------------|-------|---------------------|
| Mobile | <640px | Sidebar oculto (hamburger), tabla scroll horizontal, filtros en sheet bottom, single column |
| Tablet | 640-1024px | Sidebar colapsado por defecto, 2 columnas max, drawer en full-screen |
| Desktop | 1024-1440px | Sidebar expandido, layout completo, todas las features |
| Wide | >1440px | Sidebar expandido, tabla aprovecha ancho, drawer mas amplio |

**Reglas mobile:**
- Tablas: scroll horizontal nativo, columnas menos importantes ocultas
- Filtros: sheet que se desliza desde bottom (no lateral)
- Modales: full-screen en mobile, centrados en desktop
- Touch targets minimo 44x44px
- Font-size nunca menor a 14px en inputs (previene zoom iOS)

### 8. Reglas de accesibilidad (a11y)

| Regla | Nivel | Implementacion |
|-------|-------|----------------|
| Contraste minimo 4.5:1 para texto normal | WCAG AA | Verificar todos los `--text-*` sobre `--bg-*` |
| Contraste 3:1 para texto grande (>18px bold) | WCAG AA | Titulos, badges |
| Focus visible en todos los elementos interactivos | WCAG AA | Outline 2px coral, offset 2px |
| Navegacion completa por teclado | WCAG AA | Tab order logico, escape cierra overlays |
| Roles ARIA en componentes complejos | WCAG AA | `role="dialog"`, `aria-expanded`, `aria-live` |
| Alt text en imagenes e iconos decorativos | WCAG AA | Iconos puramente decorativos: `aria-hidden="true"` |
| Reducir motion respetado | WCAG AA | `@media (prefers-reduced-motion)` → sin animaciones |
| Screen reader announcements para toasts | WCAG AA | `aria-live="polite"` region para toasts |

### 9. Cheatsheet de decision rapida

```
ESTOY CONSTRUYENDO... → MODO → TOKENS CLAVE

Landing page section      → Lectura  → --font-display, --space-section-lg, --accent
Onboarding step 1-3       → Lectura  → --font-display, --space-block-lg
Empty state primera vez   → Lectura  → --font-display, coral prominente
Reporte ejecutivo         → Lectura  → --font-display, --content-max:720px
Modal de confirmacion grave → Mix    → Titulo: --font-display, Body: --font-body-sm

table de agentes          → Operacion → --font-data, --row-height, --cell-padding
formulario de config      → Operacion → --font-body-sm, input 36px, validacion debajo
filtros de tabla          → Operacion → chips inline, --space-element-sm
dashboard KPIs            → Operacion → --font-body, badges, sparklines
log stream                → Operacion → --font-mono, 11px, colores por nivel
panel sanidad             → Operacion → scorecards, progress bars, checks tabla
modal rapido (discard)    → Operacion → --font-body-sm, acciones claras
tooltip                   → Operacion → --font-caption, 12px, inverse colors
dropdown menu             → Operacion → --font-body-sm, 36px items
command palette           → Operacion → --font-body, input 48px, resultados icon+text
```

### 10. Anti-patterns detectables

| Anti-pattern | Deteccion | Fix |
|--------------|-----------|-----|
| "Voy a usar un card grande con padding 32px para mostrar un dato de tabla" | Card en contexto de tabla densa | Usar celda de tabla directamente, no card |
| "Voy a poner Crimson Pro en los headers de tabla" | Serif en tabla | Usar Inter 11px uppercase para headers de tabla |
| "Voy a hacer un fondo blanco #FFFFFF para que se vea limpio" | Fondo blanco puro | Usar cream `#F4F1ED` siempre |
| "Voy a poner coral de fondo para que resalte" | Coral como fondo de superficie | Coral solo para acentos, bordes, iconos activos |
| "Voy a hacer el texto de tabla mas chico para que quepa" | Font-size <11px en tabla | Truncar con tooltip, o ajustar columnas, nunca <11px |
| "Voy a poner animacion de fade-up en la tabla de agentes" | Animacion de entrada en modo Operacion | Sin animacion o fade instantaneo (<100ms) |
| "Voy a usar placeholder como label para ahorrar espacio" | Placeholder = label | Label siempre visible arriba del input |
| "Voy a poner un spinner en lugar de skeleton mientras carga la tabla" | Spinner donde va skeleton | Skeleton mantiene layout, spinner no |
| "El modo oscuro se ve mejor para operaciones" | Dark mode propuesto | No hay dark mode en FaberLoom v1. Cream base siempre. |
| "Voy a poner un toggle para modo compacto/espacioso" | Toggle de densidad | La densidad es contextual, no preferencia. No toggle. |

---

## Apendice A: Tokens de diseno (resumen)

### Colores

| Token | Valor hex | Uso |
|-------|-----------|-----|
| `--bg-base` | `#F4F1ED` | Fondo primario todo el producto |
| `--bg-elevated` | `#FAF9F7` | Modales, drawers, dropdowns |
| `--bg-secondary` | `#EEEBE6` | Sidebars, headers de tabla |
| `--bg-tertiary` | `#E5E2DC` | Filas alternadas, hover sutil |
| `--text-primary` | `#1F1E1C` | Texto principal |
| `--text-secondary` | `#1F1E1CA6` | Metadata, captions |
| `--text-tertiary` | `#1F1E1C66` | Placeholders, hints |
| `--text-inverse` | `#F4F1ED` | Texto sobre fondos oscuros |
| `--accent` | `#C96442` | Acento primario (coral) |
| `--accent-hover` | `#B55634` | Coral oscurecido 10% |
| `--accent-muted` | `#C9644226` | Coral 15% opacity |
| `--border` | `#1F1E1C1F` | Bordes estandar |
| `--border-focus` | `#C96442` | Borde focus (coral) |
| `--pizarra` | `#5A6B7C` | Iconos secundarios, badges info |
| `--status-success` | `#2D7A5F` | Exito, pass, agent OK |
| `--status-warning` | `#C9962E` | Warning, retry pending |
| `--status-error` | `#A94442` | Error, fail, blocked |
| `--status-info` | `#4A7FB5` | Info, hints tecnicos |

### Tipografia

| Token | Fuente | Peso | Tamano | Line-height |
|-------|--------|------|--------|-------------|
| `--font-display` | Crimson Pro | 500 italic | 48-64px | 1.15 |
| `--font-h1` | Inter | 700 | 24-28px | 1.3 |
| `--font-h2` | Inter | 700 | 18-20px | 1.35 |
| `--font-h3` | Inter | 600 | 14-16px | 1.4 |
| `--font-body` | Inter | 400 | 13-14px | 1.5 |
| `--font-body-lg` | Inter | 400 | 16-18px | 1.6 |
| `--font-data` | Inter | 400 | 12-13px | 1.4 |
| `--font-mono` | JetBrains Mono | 400 | 11-12px | 1.4 |
| `--font-caption` | Inter | 500 | 11-12px | 1.3 |
| `--font-badge` | Inter | 600 | 10-11px | 1.2 |

### Espaciado

| Token | Valor | Contexto |
|-------|-------|----------|
| `--space-section-lg` | 48px | Lectura: entre secciones |
| `--space-block-lg` | 32px | Lectura: entre bloques |
| `--space-element-lg` | 24px | Lectura: entre elementos |
| `--space-section-sm` | 24px | Operacion: entre secciones |
| `--space-block-sm` | 16px | Operacion: entre bloques |
| `--space-element-sm` | 8-12px | Operacion: entre elementos |
| `--space-unit` | 8px | Base unit Operacion |
| `--space-unit-lg` | 12px | Base unit Lectura |
| `--cell-padding` | 10px 12px | Tabla: vertical horizontal |
| `--row-height` | 44px | Altura fila de tabla |
| `--input-height` | 36px | Altura input estandar |
| `--button-height` | 36px | Altura boton estandar |
| `--action-gap` | 8px | Entre botones inline |
| `--page-gutter-lg` | 64px | Lectura: padding horizontal pagina |
| `--page-gutter-sm` | 24px | Operacion: padding horizontal pagina |
| `--sidebar-expanded` | 240px | Sidebar ancho expandido |
| `--sidebar-collapsed` | 56px | Sidebar ancho colapsado |
| `--content-max` | 720px / 1200px | Max-width contenido Lectura |

---

## Apendice B: Roadmap de componentes

### MVP (Semanas 1-4)

**Tablas y datos:** Tabla basica, Tabla con paginacion, Fila expandible, Fila con acciones inline, Bulk actions bar, Sorting indicators, Empty state tabla, Loading skeleton tabla, Error boundary tabla

**Formularios:** Input text con validacion, Input con icono, Textarea, Select/Dropdown, Multi-select, Checkbox, Radio, Toggle, File upload, Form multi-step, Validation errors

**Filtros y busqueda:** Search bar global, Filtro lateral panel, Filtro inline chips, Search results empty

**Feedback y estados:** Toast (4 variantes), Modal confirm, Modal form, Drawer/Panel, Tooltip, Popover/Dropdown menu, Loading spinner, Skeleton, Empty state generico, Error boundary, Progress bar, Badge/Tag/Pill, Banner

**Navegacion:** Sidebar collapsible, Top nav/Header, Breadcrumbs, Tabs primary, Tabs secondary, Pagination

### V1 (Meses 2-3)

**Tablas y datos:** Tabla virtualizada, Column resizing, Column reordering

**Formularios:** Combobox autocomplete, Form inline editing, Form empty state

**Filtros y busqueda:** Saved filters

**Feedback y estados:** Modal info (editorial), Empty state por categoria

**Navegacion:** Tabs overflow, Command palette / Spotlight search

### V2 (Meses 4-6)

**Tablas y datos:** (completos)

**Formularios:** Slider, Date picker

**Filtros y busqueda:** Filtro avanzado query builder

**Feedback y estados:** (completos)

**Navegacion:** (completo)

**Patterns especificos:** Acciones correctivas automaticas en Sanidad, ML para sugerencias, Branding por tenant

---

## Apendice C: Glosario

| Termino | Definicion |
|---------|------------|
| **Trust Ladder** | Sistema de autonomia progresiva de FaberLoom. El usuario delega mas control a la IA conforme aumenta la confianza. |
| **Modo Lectura** | Registro de interfaz espacioso, editorial, brand-forward. Para momentos de reflexion y absorcion. |
| **Modo Operacion** | Registro de interfaz denso, funcional, brand-discreet. Para momentos de accion y monitoreo. |
| **Brand-forward** | Uso prominente de elementos de marca: coral, serif italic, espaciado generoso. |
| **Brand-discreet** | Uso restringido de marca: ink dominante, coral solo para acciones activas, tipografia UI. |
| **Brand-absent** | Nunca permitido. Marca siempre presente aunque sea sutilmente. |
| **Hacedor moderno** | Persona usuario de FaberLoom: studios de diseno, agencias creativas, consultoras boutique, freelancers senior, makers. |
| **Telar** | Metafora central de FaberLoom. La IA prepara (hilos), el usuario teje (decide, configura, supervisa). |
| **Hash chaining** | Tecnica criptografica donde cada bloque de auditoria contiene el hash del bloque anterior, formando una cadena inmutable. |
| **Scorecard** | Panel de metricas de sanidad que muestra scores por categoria y checks individuales. |
| **Tenant** | Instancia aislada de FaberLoom para un cliente/equipo. Cada tenant tiene sus agentes, configs y usuarios. |

---

## Document control

| Version | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0.0 | 2026-01-15 | AI Agent — Design Systems | Version inicial. Sistema de densidad dual, 52 componentes ranqueados, 4 patterns especificos, reglas de implementacion para agentes IA. |

---

*"La IA prepara, vos tejes."*

*Este documento es parte del Brand Book v2 2026 de FaberLoom. Para consultas sobre implementacion, referirse a los tokens de diseno en Apendice A y al cheatsheet de decision en Seccion 9 de Reglas de implementacion.*
