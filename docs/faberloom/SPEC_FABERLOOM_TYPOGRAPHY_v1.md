# SPEC_FABERLOOM_TYPOGRAPHY_v1.md

| id | FAB-TYP-2026 |
| version | 1.0.0 |
| status | DRAFT → RECOMMENDED |
| visibility | INTERNAL |
| domain | faberloom |

---

## Stack tipografico final recomendado

### Fuente 1: Crimson Pro — Rol principal (Display + Headline + Body editorial)

| Atributo | Valor |
|----------|-------|
| **Role** | Display / Headline / Body editorial |
| **Weights seleccionados** | 400, 500, 600 |
| **Styles seleccionados** | normal, italic |
| **Variable font** | Si — eje `wght` 200-900 (utilizamos 400-600) |
| **Subsets** | `latin`, `latin-ext` |
| **Payload estimado** | ~40 KB (latin-ext, variable, normal + italic) |
| **Wordmark** | "Faber" en Crimson Pro Italic 500 (irreversible) |

**Justificacion:**

Crimson Pro es la fuente del wordmark "Faber" en italic 500 — su presencia en el stack es no-negociable. Como old-style serif diseñada expresamente para produccion digital y editorial, encarna perfectamente el manifiesto del "telar del hacedor moderno": transmite calma, precision y respeto por el oficio sin caer en la frialdad de una geometrica ni en la ornamentalidad excesiva de un display. Su eje variable `wght` permite una gradacion fina entre 400 (body elegante), 500 (wordmark, enfasis) y 600 (headlines impactantes), todo en un unico archivo variable por subset y estilo. El soporte completo de Latin Extended garantiza acentuacion correcta en espanol (a, e, i, o, u, n, ¿, ¡).

**Confidence:** **ALTO** — vinculada al wordmark, validada por personalidad de marca y versatilidad editorial.

---

### Fuente 2: Inter — Rol secundario (UI + Body funcional)

| Atributo | Valor |
|----------|-------|
| **Role** | UI / Interface / Body funcional |
| **Weights seleccionados** | 400, 500, 600, 700 |
| **Styles seleccionados** | normal, italic |
| **Variable font** | Si — ejes `wght` 100-900 (utilizamos 400-700), `opsz` 14-32 |
| **Subsets** | `latin`, `latin-ext` |
| **Payload estimado** | ~32 KB (latin-ext, variable, normal + italic, rango 400-700) |
| **Fallback stack** | `system-ui`, `-apple-system`, `BlinkMacSystemFont`, `'Segoe UI'`, `Roboto`, `sans-serif` |

**Justificacion:**

Inter fue disenada explicitamente para interfaces de usuario en pantallas, con optimizaciones de hinting que preservan la legibilidad hasta 11px. Su clasificacion neo-grotesque geometrica la hace neutra, profesional y "invisible" en la interfaz — cualidades esenciales para un SaaS B2B donde el contenido del usuario (tablas, formularios, dashboards) es el protagonista. El eje variable `wght` cubre cuatro pesos funcionales (Regular para body, Medium para labels, SemiBold para tabs/headlines de UI, Bold para botones primarios) en un solo archivo por subset. El eje `opsz` (optical size) mejora la legibilidad a tamanos pequenos automaticamente. Con soporte completo de Latin Extended y payload minimo (~11 KB por subset en variable italic, ~21 KB en roman), es la fuente UI mas eficiente del catalogo evaluado.

**Confidence:** **ALTO** — estandar de facto para UI moderna, validada tecnicamente, menor payload del grupo.

---

### Fuente 3: IBM Plex Mono — Rol terciario (Datos / Codigo / Logs)

| Atributo | Valor |
|----------|-------|
| **Role** | Datos monoespaciados / Code / Logs / Timestamps / JSON |
| **Weights seleccionados** | 400, 500 |
| **Styles seleccionados** | normal, italic |
| **Variable font** | No disponible en Google Fonts (version variable existe en repo IBM, no expuesta via API) |
| **Subsets** | `latin`, `latin-ext` |
| **Payload estimado** | ~55 KB total (4 archivos estaticos: 400 normal, 400 italic, 500 normal, 500 italic × latin + latin-ext) |
| **Fallback stack** | `'SF Mono'`, `Monaco`, `Inconsolata`, `'Roboto Mono'`, `'Courier New'`, `monospace` |

**Justificacion:**

FaberLoom es un producto SaaS B2B con componentes tecnicos visibles: logs de agente, timestamps, hashes, bloques de JSON configuracion, y fragmentos de codigo en documentacion. En estos contextos, una fuente monoespaciada no es un lujo sino una necesidad funcional — alinea numericos en tablas, facilita la lectura de estructuras anidadas, y diferencia claramente el contenido de datos del contenido de interfaz. IBM Plex Mono es la contraparte monoespaciada de una superfamilia coherente (IBM Plex), disenada para UI, con terminaciones claras y diferenciacion de glifos ambiguos (0/O, 1/l/I). Aunque Google Fonts no expone su version variable, el payload de dos pesos (400 para logs, 500 para enfasis en timestamps/hash) es asumible (~55 KB para latin + latin-ext, ambos estilos). La alternativa — usar `ui-monospace` del sistema — sacrifica consistencia visual entre plataformas.

**Confidence:** **MEDIO-ALTO** — justificado por el contexto tecnico del producto, aunque el payload estatico es un compromiso.

---

## Tabla de uso por contexto

| Contexto | Fuente | Weight | Size | Line-height | Letter-spacing | Uso ejemplo |
|----------|--------|--------|------|-------------|----------------|-------------|
| **H1 (hero)** | Crimson Pro | 600 | 48-64px | 1.1 | -0.02em | Titulo de landing page |
| **H2 (section)** | Crimson Pro | 500 | 32-40px | 1.2 | -0.01em | Nombre de seccion en dashboard |
| **H3 (card title)** | Crimson Pro | 500 | 24px | 1.3 | 0 | Titulo de tarjeta, nombre de proyecto |
| **H4 (subtitulo)** | Crimson Pro | 400 | 18-20px | 1.4 | 0 | Subtitulo, caption editorial |
| **Body editorial** | Crimson Pro | 400 | 16-18px | 1.65 | 0 | Manifiesto, documentacion larga, blog |
| **Body funcional** | Inter | 400 | 14-16px | 1.5 | 0 | Descripciones, mensajes de chat, tooltips |
| **Caption / Helper** | Inter | 400 | 12px | 1.4 | 0.01em | Texto de ayuda, metadatos, footnotes |
| **Button (primary)** | Inter | 600 | 14px | 1 | 0.01em | CTA, botones de accion |
| **Button (secondary)** | Inter | 500 | 14px | 1 | 0.01em | Botones secundarios, icon buttons |
| **Tab** | Inter | 500 | 14px | 1 | 0.02em | Tabs de navegacion |
| **Tab (active)** | Inter | 600 | 14px | 1 | 0.02em | Tab seleccionado |
| **Input / Textarea** | Inter | 400 | 14-16px | 1.5 | 0 | Formularios, campos de texto |
| **Input (label)** | Inter | 500 | 12px | 1.3 | 0.02em | Label flotante, field caption |
| **Badge (pill)** | Inter | 500 | 11-12px | 1 | 0.03em | Etiquetas de estado, tags |
| **Table header** | Inter | 600 | 12px | 1.2 | 0.03em | Encabezados de tabla, sortable |
| **Table cell** | Inter | 400 | 13-14px | 1.4 | 0 | Contenido de tabla |
| **Table cell (mono)** | IBM Plex Mono | 400 | 13px | 1.4 | 0 | IDs, timestamps, hash corto |
| **Code block / Log** | IBM Plex Mono | 400 | 13px | 1.6 | 0 | Logs de agente, JSON, stack traces |
| **Code inline** | IBM Plex Mono | 400 | 0.9em | 1.4 | 0 | `variableName`, atributos tecnicos en texto |
| **Timestamp** | IBM Plex Mono | 500 | 11-12px | 1.3 | 0.02em | 2026-01-15T14:32:01Z |
| **Navigation** | Inter | 500 | 14px | 1 | 0.01em | Menu principal, sidebar |
| **Toast / Alert** | Inter | 500 | 14px | 1.4 | 0 | Notificaciones, alertas |
| **Empty state** | Crimson Pro | 400 italic | 18px | 1.5 | 0 | Mensajes inspiradores, estados vacios |
| **Wordmark** | Crimson Pro | 500 italic | — | 1 | 0 | **Faber**Loom (irreversible) |

---

## Evaluacion comparativa de las 11 fuentes auditadas

### SERIF fonts

| Fuente | Peso carga | Licencia | Latin Extended | Legib. 12px | Personalidad marca | Versatilidad | DTCG/Variable | **Score** |
|--------|-----------|----------|---------------|-------------|-------------------|-------------|---------------|-----------|
| **Crimson Pro** | 4/5 | 5/5 | 5/5 | 2/5 | 5/5 | 4/5 | 5/5 (variable) | **30/35** |
| Cormorant Garamond | 3/5 | 5/5 | 5/5 | 2/5 | 3/5 | 3/5 | 4/5 (variable) | 25/35 |
| EB Garamond | 3/5 | 5/5 | 5/5 | 2/5 | 4/5 | 3/5 | 4/5 (variable) | 26/35 |
| Playfair Display | 3/5 | 5/5 | 5/5 | 1/5 | 3/5 | 2/5 | 4/5 (variable) | 23/35 |
| Lora | 4/5 | 5/5 | 5/5 | 3/5 | 3/5 | 3/5 | 4/5 (variable) | 27/35 |
| DM Serif Display | 5/5 | 5/5 | 5/5 | 1/5 | 3/5 | 1/5 | 2/5 (no variable) | 22/35 |

### SANS-SERIF fonts

| Fuente | Peso carga | Licencia | Latin Extended | Legib. 12px | Personalidad marca | Versatilidad | DTCG/Variable | **Score** |
|--------|-----------|----------|---------------|-------------|-------------------|-------------|---------------|-----------|
| **Inter** | 5/5 | 5/5 | 5/5 | 5/5 | 4/5 | 5/5 | 5/5 (variable, opsz) | **34/35** |
| Inter Tight | 4/5 | 5/5 | 5/5 | 4/5 | 4/5 | 3/5 | 5/5 (variable) | 30/35 |
| Space Grotesk | 3/5 | 5/5 | 5/5 | 4/5 | 3/5 | 2/5 (sin italica) | 4/5 (variable) | 26/35 |
| IBM Plex Sans | 4/5 | 5/5 | 5/5 | 5/5 | 3/5 | 3/5 | 4/5 (variable) | 29/35 |
| Manrope | 4/5 | 5/5 | 5/5 | 4/5 | 3/5 | 2/5 (sin italica) | 4/5 (variable) | 26/35 |

---

## Tabla de eliminacion (las fuentes descartadas)

| Fuente descartada | Razon principal | Confidence |
|-------------------|-----------------|------------|
| **Cormorant Garamond** | Serif elegante pero excesivamente ornamental; alto contraste en pesos finos dificulta legibilidad en pantalla; personalidad mas "literaria" que "de oficio". Reemplazada por Crimson Pro (mas versatil y ya vinculada al wordmark). | ALTO |
| **EB Garamond** | Revival historico excepcional para editorial impresa, pero sus optical sizes (8pt/12pt) y OpenType features (swashes, small caps) son overkill para un SaaS. Personalidad academica/tradicional demasiado marcada, menos adaptable que Crimson Pro para un producto tech. | ALTO |
| **Playfair Display** | Construida exclusivamente para display; contraste extremo la hace ilegible en body o UI. Solo 16 estilos generan payload innecesario si solo se usan 2-3 pesos. Demasiado "moda editorial" para un B2B tech. | ALTO |
| **Lora** | Buena fuente de texto con raices caligraficas, pero su personalidad es mas "cuento/narrativa" que "precision/oficio". Menos distinguida en display que Crimson Pro y menos eficiente en UI que Inter. Ocupa un rol intermedio sin liderar en ningun contexto. | ALTO |
| **DM Serif Display** | Solo 2 estilos (400 + italic), no variable, diseñada exclusivamente para titulares grandes. Incapaz de cubrir body o cualquier peso intermedio. Payload aceptable pero versatilidad nula. | ALTO |
| **Inter Tight** | Version condensada de Inter util para headlines compactos, pero su espaciado reducido penaliza la legibilidad en body largo. No aporta suficiente diferenciacion frente a Inter estandar para justificar un segundo archivo. Si se necesita condensacion, usar `letter-spacing: -0.01em` en Inter. | MEDIO |
| **Space Grotesk** | Geometrica futurista sin italica — limitacion critica para un producto con contenido editorial (documentacion, manifiesto). Su origen en Space Mono le da un aire "tecnico frio" que no alinea con el tono "calmo, respetuoso del oficio". Mejor como fuente de acento que como fuente base. | ALTO |
| **IBM Plex Sans** | Excelente fuente corporativa, pero pesa psicologicamente mas "enterprise legacy" que "maker moderno". Sus pesos terminan en 700 (sin 800/900), limitando jerarquias dramaticas. Inter la supera en optimizacion para pantalla, pesos disponibles y ecosistema. | MEDIO |
| **Manrope** | Geometrica moderna sin italica — al igual que Space Grotesk, la ausencia de cursiva real la descalifica para contenido mixto editorial/UI. Sus "icon ligatures" son un feature interesante pero irrelevante para FaberLoom. Menos refinada en 12px que Inter. | ALTO |

---

## Consideraciones especiales

### IBM Plex Mono

| Atributo | Valor |
|----------|-------|
| **Recomendacion** | **INCLUIR** como fuente de datos/codigo/logs |
| **Weights** | 400 (logs, code), 500 (timestamps, hash emphasis) |
| **Styles** | normal, italic |
| **Variable font** | No disponible via Google Fonts API (solo estatica) |
| **Payload total** | ~55 KB (4 archivos WOFF2: 400n, 400i, 500n, 500i × latin + latin-ext) |
| **Carga recomendada** | `font-display: optional` — cargar solo cuando el usuario acceda a paneles tecnicos (logs, config). No bloquear el critical rendering path. |

**Razonamiento de inclusion:**

En un producto "chat-first agentic", el usuario vera regularmente: (a) logs de ejecucion del agente, (b) bloques de JSON de configuracion, (c) timestamps de conversacion, (d) hashes de version/sesion. Una fuente proporcional como Inter funciona para (c) y (d) en formato legible, pero falla en (a) y (b) donde la alineacion vertical de estructuras anidadas es critica. IBM Plex Mono proporciona:

- Diferenciacion clara de glifos ambiguos: `0` vs `O`, `1` vs `l` vs `I`
- Alineacion tabular de numeros por defecto (feature `tnum`)
- Coherencia de marca IBM Plex con el tono "preciso, tecnico, profesional"
- Latin Extended completo para acentos en logs multilenguaje

**Alternativa si se descarta:** Usar `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace` — funcional pero inconsistente entre plataformas (macOS vs Windows vs Linux).

---

### Variable fonts

| Fuente | Eje variable | Rango usado | Beneficio |
|--------|-------------|-------------|-----------|
| **Crimson Pro** | `wght` | 400-600 | 3 pesos continuous en 1 archivo por subset (~40 KB vs ~90 KB estaticos estimados) |
| **Inter** | `wght`, `opsz` | 400-700, 14-32 | 4+ pesos continuous + ajuste optico automatico en ~32 KB |

**Payload comparativo:**

| Escenario | Estatico (KB) | Variable (KB) | Ahorro |
|-----------|--------------|---------------|--------|
| Crimson Pro: 400,500,600 × 2 estilos × 2 subsets | ~90 | ~40 | **~56%** |
| Inter: 400,500,600,700 × 2 estilos × 2 subsets | ~96 | ~32 | **~67%** |

**Recomendacion:** Usar siempre la version variable de Crimson Pro e Inter via Google Fonts API v2. El navegador descarga solo los subsets necesarios gracias a `unicode-range`.

---

### Rendimiento

#### Estrategia de carga

```html
<!-- Preload: Critical rendering path -->
<link rel="preload" href="https://fonts.gstatic.com/s/crimsonpro/v28/q5uBsoa5M_tv7IihmnkabARekY1wDfKi.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuLyfAZ9hjp-Ek-_EeA.woff2" as="font" type="font/woff2" crossorigin>

<!-- Google Fonts API v2: non-blocking -->
<link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,500;0,600;1,400;1,500;1,600&family=Inter:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600;1,700&family=IBM+Plex+Mono:ital,wght@0,400;0,500;1,400;1,500&display=swap&subset=latin,latin-ext" rel="stylesheet">
```

#### Prioridad de preload

| Prioridad | Fuente | Weight | Subset | Justificacion |
|-----------|--------|--------|--------|---------------|
| **1 (critical)** | Crimson Pro | 500 italic | latin, latin-ext | Wordmark "Faber" visible inmediatamente |
| **2 (critical)** | Inter | 400-700 roman | latin, latin-ext | Todo el texto de UI depende de esto |
| 3 (deferred) | Crimson Pro | 400,600 | latin-ext | Headlines y body editorial (segundo viewport) |
| 4 (on-demand) | IBM Plex Mono | 400,500 | latin, latin-ext | Solo si el usuario abre panel tecnico |

#### font-display

| Fuente | Recomendacion | Razon |
|--------|--------------|-------|
| Crimson Pro | `font-display: swap` | El wordmark debe verse lo antes posible; FOUT aceptable por brevedad |
| Inter | `font-display: swap` | UI sin fuente es inusable; swap inmediato |
| IBM Plex Mono | `font-display: optional` | Si no esta cacheada, usar fallback monospace; no bloquear por datos secundarios |

#### Fallback stack

```css
/* Display / Headline / Body editorial */
font-family: 'Crimson Pro', 'Georgia', 'Times New Roman', serif;

/* UI / Body funcional */
font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;

/* Datos / Codigo / Logs */
font-family: 'IBM Plex Mono', 'SF Mono', Monaco, Inconsolata, 'Liberation Mono', 'Courier New', monospace;
```

---

## DTCG mapping

```json
{
  "font": {
    "family": {
      "display": {
        "$value": "'Crimson Pro', 'Georgia', 'Times New Roman', serif",
        "$type": "fontFamily",
        "description": "Display, headlines, body editorial, wordmark"
      },
      "body": {
        "$value": "'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
        "$type": "fontFamily",
        "description": "Body funcional, UI general"
      },
      "ui": {
        "$value": "'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
        "$type": "fontFamily",
        "description": "Botones, tabs, tablas, forms, badges — alias de body"
      },
      "mono": {
        "$value": "'IBM Plex Mono', 'SF Mono', Monaco, Inconsolata, 'Courier New', monospace",
        "$type": "fontFamily",
        "description": "Logs, codigo, timestamps, datos tecnicos"
      }
    },
    "weight": {
      "display": {
        "regular": { "$value": 400, "$type": "fontWeight" },
        "medium": { "$value": 500, "$type": "fontWeight" },
        "semibold": { "$value": 600, "$type": "fontWeight" }
      },
      "body": {
        "regular": { "$value": 400, "$type": "fontWeight" },
        "medium": { "$value": 500, "$type": "fontWeight" },
        "semibold": { "$value": 600, "$type": "fontWeight" },
        "bold": { "$value": 700, "$type": "fontWeight" }
      },
      "mono": {
        "regular": { "$value": 400, "$type": "fontWeight" },
        "medium": { "$value": 500, "$type": "fontWeight" }
      }
    },
    "size": {
      "hero": { "$value": "3rem", "$type": "dimension" },
      "h1": { "$value": "2.5rem", "$type": "dimension" },
      "h2": { "$value": "2rem", "$type": "dimension" },
      "h3": { "$value": "1.5rem", "$type": "dimension" },
      "h4": { "$value": "1.25rem", "$type": "dimension" },
      "body": { "$value": "1rem", "$type": "dimension" },
      "body-sm": { "$value": "0.875rem", "$type": "dimension" },
      "caption": { "$value": "0.75rem", "$type": "dimension" },
      "badge": { "$value": "0.6875rem", "$type": "dimension" }
    },
    "line-height": {
      "tight": { "$value": 1.1, "$type": "number" },
      "snug": { "$value": 1.25, "$type": "number" },
      "normal": { "$value": 1.5, "$type": "number" },
      "relaxed": { "$value": 1.65, "$type": "number" }
    },
    "letter-spacing": {
      "tight": { "$value": "-0.02em", "$type": "dimension" },
      "normal": { "$value": "0", "$type": "dimension" },
      "wide": { "$value": "0.02em", "$type": "dimension" },
      "wider": { "$value": "0.03em", "$type": "dimension" }
    }
  }
}
```

---

## Decisiones irreversibles

| # | Decision | Costo de reversion | Mitigacion |
|---|----------|-------------------|------------|
| 1 | **Crimson Pro Italic 500 para wordmark "Faber"** | MUY ALTO — requiere redisenar logo, favicon, assets de marca, documentacion, templates. | Ninguna; esta decision esta tomada por Brand v2. |
| 2 | **Inter como unica fuente UI** | MEDIO — cambiar fuente UI afecta todos los componentes, layouts, y percepcion de densidad. Inter es tan comun que la inversion es segura. | Documentar tokens DTCG para que un cambio futuro sea un swap de `$value`, no un refactor de CSS. |
| 3 | **Inclusion de IBM Plex Mono** | BAJO-MEDIO — eliminarla implica cambiar `font-family: mono` por stack de sistema. No hay dependencias funcionales. | Usar `font-display: optional` para que nunca bloquee el render; si se elimina, solo cambia el token `$value`. |
| 4 | **Uso de variable fonts via Google Fonts API v2** | BAJO — si un navegador no soporta variable fonts, Google Fonts sirve estaticos automaticamente. | La API de Google Fonts maneja el fallback transparentemente. |
| 5 | **Subset latin + latin-ext (sin cyrillic/greek)** | BAJO — si FaberLoom se internacionaliza a Rusia o Grecia, agregar subsets es trivial via parametro `subset` en la URL. | Monitorear analytics de usuarios; expandir subsets segun demanda. |
