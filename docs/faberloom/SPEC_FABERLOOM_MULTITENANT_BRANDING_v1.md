| id | FAB-MTB-2026 |
| version | 1.0.0 |
| status | DRAFT |
| visibility | INTERNAL |
| domain | faberloom |

## Resumen Ejecutivo

FaberLoom es un SaaS B2B multi-tenant donde cada tenant representa un workspace/equipo/organizacion. Este documento define la estrategia de branding multi-tenant que permite a FaberLoom mantener su identidad de marca (paleta cream/ink/coral, wordmark serif/sans, voz calma y precisa) mientras ofrece a los tenants niveles crecientes de personalizacion de marca — desde co-branding hasta white-label completo.

**Problema central**: El color coral (#C96442) es el UNICO driver de interaccion de FaberLoom. Cuando un tenant introduce su propio color de acento en Nivel 2 y 3, se produce un conflicto critico: ¿coral de FaberLoom o accent del tenant?

**Decision clave**: Este documento propone una estrategia de "contextualizacion de marca" donde coral se reserva para el chrome de FaberLoom (navegacion, controles de la plataforma) y el accent del tenant se aplica al contenido del tenant (reportes, dashboards, elementos de accion del negocio del cliente). En Nivel 3 (white-label), coral se neutraliza por completo.

**Arquitectura**: Se propone un sistema de tokens DTCG con tres capas — fijos FaberLoom, overrideables por tenant, y fallback — implementado via CSS Custom Properties con scope por atributo `data-tenant`.

---

## 1. Investigacion de Mercado

### 1.1 Comparativa de Productos

| Producto | Marca propia | Marca tenant | Custom accent | Nivel maximo | URL ref |
|----------|-------------|--------------|---------------|--------------|---------|
| Notion | Wordmark, icon, colores propios (10 colores fijos) | Logo workspace, icono personalizado, dominio notion.site | NO — solo paleta fija propia | N1 (producto brand) con toques de tenant (logo, icon) | [^150^](https://www.notion.com/help/manage-your-notion-sites) [^153^](https://www.notion.com/help/guides/the-ultimate-quickstart-guide-to-notion-for-enterprise) |
| Linear | Wordmark "Linear", azul desaturado como brand color | Ninguna — Linear mantiene control total del chrome | NO — azul de Linear siempre presente | N1 (full product brand) | [^182^](https://linear.app/brand) |
| Slack | Slack logo, "a Slack company", colores propios | Logo workspace, custom sidebar themes (colores del tenant) | SI — tenant puede definir colores de sidebar personalizados | N2 (co-branded workspace) | [^132^](https://www.zdnet.com/article/how-to-organize-your-slack-workspaces-with-custom-themes/) [^154^](https://www.zdnet.com/article/how-to-customize-the-slack-sidebar-for-a-more-efficient-experience/) |
| Intercom | "Powered by Intercom", logo Intercom | Logo del cliente, primary color, background color, action color | SI — cliente define primary color y action color | N2 (co-branded messenger) / N3 con white-label en planes superiores | [^144^](https://www.intercom.com/help/en/articles/6612589-set-up-and-customize-the-messenger) [^151^](https://community.intercom.com/customer-faq-28/inquiry-on-intercom-white-labeling-options-4577) [^152^](https://www.intercom.com/help/en/articles/3946163-style-your-messenger-to-support-multiple-brands) |
| HubSpot | "HubSpot" branding en portal | Logo cliente, primary/secondary/accent colors, fonts | SI — full brand kit con primary, secondary, accent colors | N2 (co-branded portal) | [^123^](https://knowledge.hubspot.com/branding/edit-your-logo-favicon-and-brand-colors) [^124^](https://www.struto.io/blog/a-practical-guide-to-branding-and-customising-your-hubspot-starter-website) |
| Webflow | "Made in Webflow", badge Webflow | Logo agencia, full CSS control, custom domain | SI — full control (white-label extremo) | N3 (full white-label en Agency/Growth workspaces) | [^138^](https://help.webflow.com/hc/en-us/articles/33961375916947-Legacy-Editor-branding-whitelabeling) [^130^](https://www.pixelfleek.com/services/webflow-white-labeling) |
| Stripe Connect | Logo Stripe siempre visible en flujos | Logo merchant, brand color, accent color, icon | SI — brand color + accent color del merchant | N2 (co-branded) — Stripe siempre presente como procesador | [^128^](https://docs.stripe.com/get-started/account/branding) [^134^](https://stripe.com/connect/features) |
| Supabase | Verde Supabase (jungle green) como brand | Supabase Auth UI permite custom colors via theme tokens | SI — brand, brandAccent, brandButtonText customizables via theme | N2 (componentes co-branded) / N3 (con custom hooks) | [^149^](https://blog.aiherrera.com/enhancing-user-experience-the-power-of-supabase-auth-ui) [^156^](https://mobbin.com/colors/brand/supabase) |
| Vercel | "Vercel" branding, blue ribbon, cod gray | Logo equipo, pero chrome siempre de Vercel | NO — colores de Vercel no se overridean | N1 (full product brand) | [^137^](https://mobbin.com/colors/brand/vercel) |
| Figma | Logo Figma, purple brand | Icon workspace, background color, description (Enterprise) | SI — background color del workspace custom | N2 (workspace customization limitada) | [^157^](https://forum.figma.com/product-updates-3/visual-customization-for-workspaces-22723) [^159^](https://help.figma.com/hc/en-us/articles/16262618858903-Change-a-workspace-icon-color-or-description) |

### 1.2 Hallazgos Clave de la Investigacion

**Confidence Level: HIGH** — Basado en documentacion oficial y analisis de producto de 10 plataformas SaaS multi-tenant.

#### 1.2.1 Notion: Producto-First, Tenant-Second

Notion mantiene control total sobre la experiencia visual. Los tenants pueden subir un logo e icono, pero:
- No pueden cambiar colores de acento — Notion impone sus 10 colores fijos [^133^](https://www.notion.com/help/customize-and-style-your-content)
- Los colores de bloques (callouts, backgrounds) son del sistema Notion, no del tenant
- En Notion Sites (publico), el tenant puede remover branding de Notion si usa custom domain [^150^](https://www.notion.com/help/manage-your-notion-sites)
- El wordmark "Notion" nunca aparece en el workspace interno, pero la estructura visual es inequivocamente Notion

**Patron**: Nivel 1 puro en workspace interno. Nivel 3 solo en sitios publicos con custom domain.

#### 1.2.2 Linear: Control Absoluto del Producto

Linear no permite NINGUNA personalizacion de marca por workspace [^164^](https://linear.app/docs/workspaces). Cada workspace tiene la misma apariencia: azul desaturado de Linear, tipografia uniforme, chrome identico. La diferenciacion entre workspaces es solo funcional (distintos miembros, distintos proyectos), no visual.

**Patron**: Nivel 1 estricto. No hay conflicto de marca porque no hay marca del tenant.

#### 1.2.3 Slack: Tenant Co-Branding en el Sidebar

Slack permite custom themes por workspace donde el tenant puede definir:
- Colores de navegacion (System Navigation)
- Colores de items seleccionados
- Colores de indicadores de presencia
- Colores de notificaciones [^132^](https://www.zdnet.com/article/how-to-organize-your-slack-workspaces-with-custom-themes/)

El logo de Slack permanece en la esquina, pero el sidebar se viste con los colores del tenant. Esto ayuda a distinguir visualmente multiples workspaces.

**Patron**: Nivel 2 — Slack mantiene estructura y logo propio, tenant colorea el sidebar.

#### 1.2.4 Intercom: Multi-Brand Co-Branding

Intercom ofrece el modelo mas sofisticado de co-branding:
- El cliente puede importar automaticamente su marca (logo + colores) desde su dominio [^142^](https://fin.ai/help/en/articles/13975779-customize-the-fin-messenger)
- Primary color reemplaza el color de accion de Intercom en botones, links, message bubbles
- Background color personaliza el header del Messenger Home
- Soporte multi-brand: un workspace puede tener distintos estilos por dominio/URL [^152^](https://www.intercom.com/help/en/articles/3946163-style-your-messenger-to-support-multiple-brands)
- White-label disponible en planes superiores (remover "Powered by Intercom") [^151^](https://community.intercom.com/customer-faq-28/inquiry-on-intercom-white-labeling-options-4577)

**Patron**: Nivel 2 por defecto con posibilidad de Nivel 3. El color de acion del tenant GANA sobre el de Intercom.

#### 1.2.5 HubSpot: Full Brand Kit del Cliente

HubSpot permite al tenant definir:
- Logo, favicon
- Primary color, secondary color, accent colors [^123^](https://knowledge.hubspot.com/branding/edit-your-logo-favicon-and-brand-colors)
- Fonts (primary, secondary, custom fonts)
- El brand kit se aplica en content editor, scheduling pages, quotes, conversation channels
- NOTA: Los brand colors NO aparecen en sales templates y emails (hay limites)

**Patron**: Nivel 2 — HubSpot mantiene estructura del portal pero el tenant define colores y tipografia.

#### 1.2.6 Webflow: White-Label Extremo

Webflow permite white-label completo en workspaces Agency/Growth:
- Remover branding de Webflow del legacy Editor [^138^](https://help.webflow.com/hc/en-us/articles/33961375916947-Legacy-Editor-branding-whitelabeling)
- Upload logo propio en el Editor
- El cliente final nunca sabe que Webflow existe detras
- Custom domains completos

**Patron**: Nivel 3 puro — el producto se vuelve completamente invisible.

#### 1.2.7 Stripe Connect: Co-Branded con Marca Procesador Persistente

Stripe Connect maneja branding de manera jerarquica:
- Brand settings (icon, logo, brand color, accent color) del merchant se aplican en checkout, customer portal, invoices [^128^](https://docs.stripe.com/get-started/account/branding)
- En Connect, el customer portal usa los brand settings de la connected account cuando el platform usa direct charges o destination charges con `on_behalf_of`
- Stripe SIEMPRE aparece como procesador — no hay white-label completo del flujo de pago
- La marca del platform y la marca del merchant coexisten

**Patron**: Nivel 2 — co-branding obligatorio. El brand color del merchant gana en la superficie de pago, pero Stripe permanece como entidad de procesamiento.

#### 1.2.8 Supabase: Token-Based Theming

Supabase ofrece theming via tokens en Auth UI:
- `brand`, `brandAccent`, `brandButtonText` customizables [^149^](https://blog.aiherrera.com/enhancing-user-experience-the-power-of-supabase-auth-ui)
- Custom CSS styles y temas propios
- El brand color de Supabase (verde) se puede reemplazar completamente
- Supabase mantiene estructura (layout, espaciado) pero el tenant controla colores

**Issue conocido**: El componente `badge` con variant `success` usaba `brand` colors en lugar de verde fijo, lo que causaba que badges de exito se vieran azules en tenants con brand color blue. [^160^](https://github.com/supabase/supabase/issues/31062) — **Esto ilustra exactamente el conflicto coral vs tenant-accent que FaberLoom debe resolver.**

**Patron**: Nivel 2 con tokens, pero con problemas de semantic-to-brand mapping.

#### 1.2.9 Vercel: Product-First, Sin Customizacion Tenant

Vercel mantiene control total del chrome del dashboard. Los teams pueden tener logos, pero:
- Blue Ribbon como color primario siempre presente [^137^](https://mobbin.com/colors/brand/vercel)
- Cod Gray y Alabaster como neutrales fijos
- No hay opcion de cambiar colores por team

**Patron**: Nivel 1 estricto, similar a Linear.

#### 1.2.10 Figma: Workspace Customization Limitada

Figma permite a org admins (Enterprise) personalizar workspaces:
- Cambiar icono (logo del tenant) [^159^](https://help.figma.com/hc/en-us/articles/16262618858903-Change-a-workspace-icon-color-or-description)
- Background color del workspace (solid color o custom HEX)
- Description del workspace
- El brand purple de Figma permanece en la navegacion global

**Patron**: Nivel 1.5 — mas que Linear/Vercel pero menos que Intercom/HubSpot. Solo el workspace tile se personaliza, no el chrome completo.

---

## 2. Los 3 Niveles de Branding Intensity

### 2.1 Nivel 1: Full FaberLoom

**Que es**: Chrome completo de la aplicacion FaberLoom. Todas las superficies controladas por FaberLoom con identidad visual propia intacta.

**Tokens que usa FaberLoom**: TODOS
- `color.background.cream` (#F4F1ED) — fondo principal
- `color.text.ink` (#1F1E1C) — texto principal
- `color.accent.coral` (#C96442) — UNICO driver de interaccion
- `color.accent.pizarra` (#5A6B7C) — secundario
- `typography.wordmark.faber` — serif italic
- `typography.wordmark.loom` — sans bold coral
- `spacing.*`, `layout.*`, `component.*` — estructura completa

**Tokens que usa el tenant**: NINGUNO

**Cuando aplica**:
| Superficie | Nivel | Razon |
|------------|-------|-------|
| Billing / Plan / Suscripcion | N1 | Es un servicio de FaberLoom, no del tenant |
| Settings globales de la plataforma | N1 | Chrome de FaberLoom |
| Help / Support / Documentacion | N1 | Voz y marca de FaberLoom |
| Login / Signup / Onboarding de FaberLoom | N1 | First touch de marca FaberLoom |
| Admin de organizacion de FaberLoom | N1 | Control de plataforma |

**Caracteristicas**:
- Wordmark "FaberLoom" completo visible (serif + sans coral)
- Coral es el unico color de interaccion (CTAs, links activos, estados de foco)
- Pizarra como secundario (badges, tags secundarios)
- Cream como fondo, Ink como texto
- Sin identificacion visual del tenant en el chrome

**Confidence Level: HIGH** — Nivel basico, sin conflictos.

---

### 2.2 Nivel 2: Co-Branded

**Que es**: Workspace del tenant con toques de marca del tenant coexistiendo con la marca FaberLoom. El tenant se siente "en su espacio" pero sabe que esta usando FaberLoom.

**Tokens que usa FaberLoom**: Estructura, layout, componentes base
- `spacing.*` — espaciado del sistema
- `layout.*` — estructura de grid, breakpoints
- `component.*` — forma, bordes, sombras de componentes
- `typography.body.*` — tipografia de lectura (si no hay brand font del tenant)
- `color.background.cream` — mantenido como base
- `color.text.ink` — mantenido como texto
- `color.neutral.*` — grises del sistema

**Tokens que usa el tenant**:
- `brand.logo` — logo del tenant en sidebar header
- `brand.name` — nombre del tenant visible
- `color.accent.tenant` — REEMPLAZA temporalmente a coral en contenido del tenant
- `typography.brand.*` — fuente del tenant (opcional, si proporcionada)
- `color.background.tenant` — variante del fondo (opcional)

**Cuando aplica**:
| Superficie | Nivel | Razon |
|------------|-------|-------|
| Dashboard principal del tenant | N2 | El tenant necesita sentirse "en su espacio" |
| Sidebar header | N2 | Logo + nombre del tenant |
| Reportes compartidos internamente | N2 | Audience es equipo del tenant |
| Canvas / Workspace del tenant | N2 | Contenido propio del tenant |
| Settings del workspace del tenant | N2 | Configuracion de su espacio |

**CONFLICTO CRITICO: coral-de-FaberLoom vs accent-del-tenant**

En Nivel 2, ambos colores coexisten. La resolucion propuesta es **contextualizacion**:

| Contexto | Color dominante | Ejemplo |
|----------|----------------|---------|
| Chrome de FaberLoom (navegacion, controles de plataforma, settings globales) | Coral de FaberLoom | Boton "Upgrade plan", link "Help", menu de usuario FaberLoom |
| Contenido del tenant (dashboard, reportes, canvas, acciones de negocio) | Accent del tenant | Boton "Generar reporte", link "Ver analisis", CTA de workflow |
| Estados de interaccion en contenido tenant | Accent del tenant | Hover en botones del dashboard, foco en inputs del workspace |
| Estados de interaccion en chrome FaberLoom | Coral de FaberLoom | Hover en boton de settings globales |

**Regla de oro N2**: Si la accion pertenece al DOMINIO del tenant (su negocio, sus datos, sus workflows), usa `accent-tenant`. Si la accion pertenece al DOMINIO de FaberLoom (la plataforma, billing, ayuda, settings globales), usa coral.

**Confidence Level: MEDIUM-HIGH** — La contextualizacion requiere disciplina de implementacion pero es sostenible.

---

### 2.3 Nivel 3: White-Label / Tenant-Forward

**Que es**: Vistas que el tenant comparte con su propio cliente final. El producto FaberLoom debe volverse lo mas invisible posible. El cliente final del tenant no debe saber que FaberLoom existe (salvo que el tenant lo desee).

**Tokens que usa FaberLoom**: Estructura minima
- `spacing.*` — espaciado (invisible)
- `layout.*` — estructura de grid (invisible)
- `typography.body.*` — tipografia fallback (solo si tenant no define brand font)
- `shadow.*`, `border.*` — tokens estructurales invisibles

**Tokens que usa el tenant**: TODOS
- `brand.logo` — logo del tenant (obligatorio)
- `brand.name` — nombre del tenant (obligatorio)
- `brand.domain` — dominio custom (opcional)
- `color.accent.primary` — color de acento del tenant (obligatorio)
- `color.accent.secondary` — secundario del tenant (opcional)
- `color.background.*` — fondos del tenant (obligatorio)
- `color.text.*` — texto del tenant (obligatorio)
- `typography.brand.*` — fuente del tenant (opcional, fallback a body de FaberLoom)

**Cuando aplica**:
| Superficie | Nivel | Razon |
|------------|-------|-------|
| Reportes externos compartidos | N3 | Audience es cliente final del tenant |
| Portal de cliente del tenant | N3 | El tenant ofrece servicio bajo su marca |
| Embeddings en sitio del tenant | N3 | Widget/iframe debe parecer del tenant |
| Dashboard publico del tenant | N3 | Public-facing bajo marca del tenant |

**"Powered by FaberLoom" — Estrategia**:

En N3, el badge "Powered by FaberLoom" es OPT-IN (controlado por el tenant), no forzado. Cuando se muestra:
- Ubicacion: footer discreto, esquina inferior derecha
- Apariencia: wordmark monocromatico en gris neutro (sin coral)
- Sin link (para no romper white-label) o link con UTM params
- Tamanio: pequeno, no prominente

**En N3 puro (tenant lo desea)**: Badge removido por completo. FaberLoom es completamente invisible.

**Neutralizacion en N3**:
- Coral SE ELIMINA por completo del white-label
- El fondo cream puede mantenerse SOLO si el tenant no define background propio (fallback)
- Ink se reemplaza por el color de texto del tenant
- Toda la paleta FaberLoom se neutraliza o se usa como fallback exclusivo

**Confidence Level: HIGH** — White-label es bien entendido en la industria.

---

## 3. Matriz de Decisiones

| Situacion | Nivel recomendado | Tokens FaberLoom | Tokens tenant | Notas |
|-----------|-------------------|------------------|---------------|-------|
| Billing de FaberLoom | N1 | Todos | Ninguno | Superficie de FaberLoom, no del tenant |
| Plan / Upgrade | N1 | Todos | Ninguno | Decision de compra sobre producto FaberLoom |
| Settings globales de la plataforma | N1 | Todos | Ninguno | Chrome de FaberLoom |
| Help / Docs / Support | N1 | Todos | Ninguno | Voz de FaberLoom |
| Onboarding inicial | N1 | Todos | Ninguno | First impression de marca FaberLoom |
| Dashboard interno del tenant | N2 | Estructura + neutrales | Logo + accent + nombre | Conflicto coral resuelto por contexto |
| Sidebar del workspace | N2 | Estructura + neutrales | Logo + accent sidebar + nombre | Header co-branded |
| Reportes compartidos internamente | N2 | Estructura + neutrales | Logo + accent + nombre | Audience: equipo del tenant |
| Canvas / Workspace del tenant | N2 | Estructura + body font | Accent + background opcional | Contenido del tenant |
| Settings del workspace | N2 | Estructura + neutrales | Nombre + logo | Config tenant en plataforma FaberLoom |
| Reporte compartido externamente | N3 | Estructura minima | Todos | "Powered by" opt-in |
| Portal de cliente del tenant | N3 | Estructura minima | Todos | White-label completo o casi |
| Embed en sitio del tenant | N3 | Estructura minima | Todos | Widget debe parecer del tenant |
| Dashboard publico del tenant | N3 | Estructura minima | Todos | Dominio custom opcional |

---

## 4. Resolucion del Conflicto Coral vs Tenant-Accent

### 4.1 Las 4 Opciones Evaluadas

#### Opcion 1: "Tenant gana siempre"

En N2/N3, coral se reemplaza completamente por el accent del tenant. El tenant nunca ve coral en su workspace.

| Pros | Cons |
|------|------|
| Simple de implementar | FaberLoom pierde identidad en su propia plataforma |
| Tenant siente maxima propiedad | El UNICO driver de interaccion de FaberLoom desaparece |
| Un solo color de acento en toda la UI | No hay diferenciacion visual entre chrome de FaberLoom y contenido del tenant |

**Veredicto**: DESCARTADA. Coral es el unico driver de interaccion; eliminarlo diluye la marca FaberLoom de manera inaceptable.

**Confidence Level: HIGH**

---

#### Opcion 2: "Coral persistente"

Coral siempre presente como "marca de FaberLoom" en algun elemento pequeno (ej: pequeno dot en la navegacion, link "powered by" en sidebar).

| Pros | Cons |
|------|------|
| Mantiene presencia de marca FaberLoom | Puede sentirse como marca impuesta al tenant |
| Coral siempre visible | En N3 rompe white-label |
| Implementacion simple | El tenant puede percibirlo como "marca intrusiva" |

**Veredicto**: DESCARTADA para N3. En N2 podria funcionar pero genera friccion. No escala a white-label.

**Confidence Level: HIGH**

---

#### Opcion 3: "Contextual" (RECOMENDADA)

Coral en chrome de FaberLoom (controles de plataforma), tenant-accent en contenido del tenant (dashboards, reportes, workflows).

| Pros | Cons |
|------|------|
| Preserva identidad FaberLoom donde pertenece | Requiere clasificar cada componente por dominio |
| Da al tenant propiedad de su contenido | Mayor complejidad de implementacion |
| Resuelve conflicto sin neutralizar a nadie | Necesita documentacion clara de "que va con que color" |
| Escalable a N3 (coral se elimina ahi) | Requiere decisiones de diseno por equipo |

**Veredicto**: ELEGIDA para N2. En N3 coral se elimina por completo (evoluciona a neutral).

**Confidence Level: HIGH** — Es la estrategia que mejor balancea las necesidades de ambas marcas.

---

#### Opcion 4: "Neutralizacion"

En N3, todo se vuelve neutral (grises) salvo logo del tenant.

| Pros | Cons |
|------|------|
| Maximo white-label | Pierde calidez de la paleta cream/ink |
| Ningun color compite con el tenant | Puede sentirse "generico" |
| Facil de implementar | No aprovecha la identidad visual de FaberLoom como valor |

**Veredicto**: DESCARTADA como estrategia principal. Se usa SOLO en N3 cuando el tenant no define colores propios (fallback), no como eleccion activa.

**Confidence Level: MEDIUM** — Util como fallback, no como estrategia.

---

### 4.2 Decision y Justificacion

**Se adopta Opcion 3: Contextual** con la siguiente logica:

**En Nivel 1 (Full FaberLoom)**:
- Coral es el UNICO driver de interaccion. Sin conflicto.

**En Nivel 2 (Co-Branded)**:
- Se introduce `color.accent.tenant` como variable CSS
- Coral permanece en: navegacion global de FaberLoom, settings de plataforma, billing, ayuda, badges de "FaberLoom feature"
- `accent-tenant` se aplica en: dashboards del tenant, reportes internos, canvas, workflows, CTAs de acciones de negocio
- La regla de decision: "¿Es una accion del negocio del tenant o de la plataforma FaberLoom?"

**En Nivel 3 (White-Label)**:
- Coral SE ELIMINA por completo
- Todo se vuelve del tenant (colores, logo, tipografia)
- Fallback a neutrales cream/gris solo si el tenant no define algo
- "Powered by FaberLoom" es opt-in, y cuando se muestra es monocromatico gris

**Confidence Level: HIGH** — Esta decision es REVERSIBLE pre-launch (se puede ajustar el mapeo de que componentes usan que color) pero se vuelve IRREVERSIBLE post-launch si los tenants ya configuraron sus colores.

---

## 5. Arquitectura de Tokens

### 5.1 Estrategia General

Basado en DTCG specification [^173^](https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/) y Style Dictionary v4 [^163^](https://lobehub.com/bg/skills/dylantarre-design-system-skills-style-dictionary) [^165^](https://www.alwaystwisted.com/articles/a-design-tokens-workflow-part-9.html), se propone una arquitectura de tres capas:

```
tokens/
├── faberloom/              # Nivel 1: Tokens fijos de FaberLoom
│   ├── primitives/
│   │   ├── colors.json     # cream, ink, coral, pizarra + escala neutrales
│   │   ├── spacing.json
│   │   ├── typography.json
│   │   └── shadows.json
│   ├── semantic/
│   │   ├── actions.json    # coral como acento de accion
│   │   ├── surfaces.json   # cream, ink, neutrales
│   │   └── feedback.json   # estados semanticos
│   └── components/
│       ├── button.json
│       ├── input.json
│       └── card.json
├── tenant/                 # Nivel 2-3: Tokens overrideables
│   ├── brand.json          # logo, nombre, dominio
│   ├── colors.json         # accent-primary, accent-secondary
│   ├── typography.json     # brand-font (opcional)
│   └── surfaces.json       # background-custom (opcional)
└── system/                 # Meta-tokens del sistema multi-tenant
    ├── levels.json         # Definicion de niveles de branding
    └── fallback.json       # Mapeo de fallbacks
```

### 5.2 Tokens Fijos de FaberLoom (Nunca Cambian)

```json
{
  "fl": {
    "primitive": {
      "color": {
        "cream": { "$value": "#F4F1ED", "$type": "color" },
        "ink": { "$value": "#1F1E1C", "$type": "color" },
        "coral": { "$value": "#C96442", "$type": "color" },
        "pizarra": { "$value": "#5A6B7C", "$type": "color" }
      }
    },
    "semantic": {
      "action": {
        "primary": { "$value": "{fl.primitive.color.coral}", "$type": "color" },
        "secondary": { "$value": "{fl.primitive.color.pizarra}", "$type": "color" }
      },
      "surface": {
        "background": { "$value": "{fl.primitive.color.cream}", "$type": "color" },
        "text": { "$value": "{fl.primitive.color.ink}", "$type": "color" }
      }
    }
  }
}
```

Estos tokens se compilan a CSS Custom Properties en `:root` y NUNCA se overridean.

### 5.3 Tokens Overrideables por Tenant

```json
{
  "tenant": {
    "brand": {
      "name": { "$value": "", "$type": "string" },
      "logo": { "$value": "", "$type": "string" },
      "domain": { "$value": "", "$type": "string" }
    },
    "color": {
      "accent": {
        "primary": { "$value": "", "$type": "color", "$description": "Replaces coral in N2/N3 contexts" },
        "secondary": { "$value": "", "$type": "color" }
      },
      "surface": {
        "background": { "$value": "", "$type": "color" },
        "text": { "$value": "", "$type": "color" }
      }
    },
    "typography": {
      "brand": {
        "family": { "$value": "", "$type": "fontFamily" }
      }
    }
  }
}
```

### 5.4 Tokens con Fallback

Los tokens semanticos de nivel 2 usan fallback logic:

```json
{
  "semantic": {
    "action": {
      "tenant": {
        "$value": "{tenant.color.accent.primary}",
        "$type": "color",
        "$extensions": {
          "fallback": "{fl.primitive.color.coral}"
        }
      }
    }
  }
}
```

### 5.5 Implementacion CSS Custom Properties

```css
/* 1. Tokens fijos FaberLoom en :root */
:root {
  --fl-color-cream: #F4F1ED;
  --fl-color-ink: #1F1E1C;
  --fl-color-coral: #C96442;
  --fl-color-pizarra: #5A6B7C;
  
  --fl-action-primary: var(--fl-color-coral);
  --fl-action-secondary: var(--fl-color-pizarra);
  --fl-surface-background: var(--fl-color-cream);
  --fl-surface-text: var(--fl-color-ink);
}

/* 2. Defaults de tenant (sin override = usan fallback de FaberLoom) */
:root {
  --tenant-color-accent-primary: var(--fl-color-coral);
  --tenant-color-accent-secondary: var(--fl-color-pizarra);
  --tenant-color-surface-background: var(--fl-color-cream);
  --tenant-color-surface-text: var(--fl-color-ink);
  --tenant-typography-brand-family: inherit;
}

/* 3. Override por tenant activo */
[data-tenant="acme-corp"] {
  --tenant-color-accent-primary: #0284c7;
  --tenant-color-accent-secondary: #0ea5e9;
  --tenant-color-surface-background: #f8fafc;
  --tenant-color-surface-text: #0f172a;
  --tenant-typography-brand-family: 'Roboto', sans-serif;
}

/* 4. Nivel de branding como atributo */
[data-branding-level="n1"] {
  --action-primary: var(--fl-action-primary);
  --action-secondary: var(--fl-action-secondary);
  --surface-background: var(--fl-surface-background);
  --surface-text: var(--fl-surface-text);
}

[data-branding-level="n2"] {
  --action-primary: var(--tenant-color-accent-primary);
  --action-secondary: var(--tenant-color-accent-secondary);
  --surface-background: var(--tenant-color-surface-background);
  --surface-text: var(--tenant-color-surface-text);
}

[data-branding-level="n3"] {
  --action-primary: var(--tenant-color-accent-primary);
  --action-secondary: var(--tenant-color-accent-secondary);
  --surface-background: var(--tenant-color-surface-background);
  --surface-text: var(--tenant-color-surface-text);
  --fl-action-primary: var(--tenant-color-accent-primary); /* Override incluso de fl-* */
}
```

### 5.6 Aplicacion en Componentes

```css
/* Boton de accion del TENANT (N2) */
.btn-tenant-action {
  background-color: var(--action-primary);
  color: white;
}

/* Boton de accion de FABERLOOM (N1 chrome) */
.btn-platform-action {
  background-color: var(--fl-action-primary);
  color: white;
}

/* En N3, ambos usan el color del tenant */
[data-branding-level="n3"] .btn-platform-action {
  background-color: var(--action-primary);
}
```

### 5.7 Pipeline Style Dictionary v4

```javascript
// style-dictionary.config.js
const themes = ['n1', 'n2', 'n3'];

module.exports = {
  source: [
    'tokens/faberloom/primitives/**/*.json',
    'tokens/faberloom/semantic/**/*.json',
  ],
  include: ['tokens/tenant/**/*.json'], // Overrideables
  
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'build/css/',
      files: themes.map(level => ({
        destination: `brand-${level}.css`,
        format: 'css/variables',
        filter: (token) => {
          // N1: solo tokens FaberLoom
          if (level === 'n1') return token.path[0] === 'fl';
          // N2/N3: incluir overrides de tenant
          return true;
        },
        options: {
          outputReferences: true,
          selector: level === 'n1' ? ':root' : `[data-branding-level="${level}"]`
        }
      }))
    }
  }
};
```

### 5.8 Reglas de Fallback en Runtime

```javascript
// Pseudocodigo del runtime multi-tenant
function resolveToken(tokenName, tenantConfig, brandingLevel) {
  // N1: siempre FaberLoom
  if (brandingLevel === 'n1') {
    return faberloomTokens[tokenName];
  }
  
  // N2/N3: intentar tenant, fallback a FaberLoom
  if (tenantConfig && tenantConfig[tokenName]) {
    return tenantConfig[tokenName];
  }
  
  return faberloomTokens[tokenName]; // Fallback siempre disponible
}
```

---

## 6. Decisiones Irreversibles

Las siguientes decisiones serian costosas de cambiar post-launch (requeririam migracion de datos de tenant o breaking changes en la API de branding):

| # | Decision | Impacto si se cambia | Reversibilidad |
|---|----------|---------------------|----------------|
| 1 | **Estructura de niveles de branding (N1/N2/N3)** | Requeriria re-mapear todas las superficies de la app y re-configurar tenants | IRREVERSIBLE post-launch |
| 2 | **Formato de los tokens de tenant** (JSON schema) | Breaking change en API de branding, migracion de configs de tenant | IRREVERSIBLE sin migracion |
| 3 | **Nombres de CSS Custom Properties** | Breaking change en CSS de todos los componentes | IRREVERSIBLE sin codemod |
| 4 | **Regla "coral en chrome, tenant-accent en contenido"** | Re-entrenamiento de usuarios, re-diseno de componentes | REVERSIBLE pre-launch, dificil post-launch |
| 5 | **Estrategia "Powered by FaberLoom" opt-in vs forced** | Cambio de posicionamiento comercial | REVERSIBLE con comunicacion |
| 6 | **Decision de N1 estricto en billing/settings** | Podria abrirse a N2 mas adelante sin breaking change | REVERSIBLE |

---

## 7. Recomendacion Arquitectural

### 7.1 Construir Ahora (Pre-Launch)

| Prioridad | Item | Razon |
|-----------|------|-------|
| P0 | Tokens fijos FaberLoom en DTCG + CSS | Base de todo el sistema de diseño |
| P0 | Nivel 1 implementado | Producto usable sin multi-tenant |
| P1 | Arquitectura de override por tenant (CSS variables + data-tenant) | Habilita N2/N3 sin refactor masivo |
| P1 | Definicion del JSON schema de tenant branding | Contrato que no se puede cambiar facilmente despues |
| P2 | Nivel 2 con regla contextual (coral vs tenant-accent) | Diferenciador competitivo |
| P2 | API de guardado/recuperacion de brand config por tenant | Backend para multi-tenant |

### 7.2 Construir Mas Adelante (Post-Launch)

| Prioridad | Item | Razon |
|-----------|------|-------|
| P3 | Nivel 3 completo (white-label) | Requiere infraestructura de dominios custom, mas complejo |
| P3 | "Powered by FaberLoom" badge configurable | Feature de marketing, no bloqueante |
| P3 | Import automatico de marca desde dominio (como Intercom) | Nice-to-have, no critico |
| P4 | Multi-brand por tenant (sub-brands) | Solo si tenants enterprise lo solicitan |
| P4 | Custom CSS/CSS-in-JS para tenants avanzados | Riesgo de breaking changes, requiere sandboxing |

---

## 8. Apendice: Glosario

| Termino | Definicion |
|---------|------------|
| DTCG | Design Tokens Community Group — especificacion W3C para tokens de diseño |
| CSS Custom Properties | Variables CSS nativas (`--var: value`) para theming dinamico |
| Branding Level | Nivel de intensidad de marca propia vs tenant (N1/N2/N3) |
| Chrome | Elementos de UI de la plataforma (navegacion, headers, controles) |
| Tenant | Cliente/organizacion que usa FaberLoom como workspace |
| Coral | Color #C96442, unico driver de interaccion de FaberLoom |
| Contextual (regla) | Coral en chrome de FaberLoom, tenant-accent en contenido del tenant |
| White-label | Producto completamente rebrandeado bajo marca del tenant |

---

## 9. Referencias

| # | Referencia | URL |
|---|------------|-----|
| 1 | Notion Sites & Custom Domains | [^150^](https://www.notion.com/help/manage-your-notion-sites) |
| 2 | Notion Enterprise Settings | [^153^](https://www.notion.com/help/guides/the-ultimate-quickstart-guide-to-notion-for-enterprise) |
| 3 | Notion Colors & Customization | [^133^](https://www.notion.com/help/customize-and-style-your-content) |
| 4 | Linear Brand Guidelines | [^182^](https://linear.app/brand) |
| 5 | Linear Workspaces | [^164^](https://linear.app/docs/workspaces) |
| 6 | Slack Custom Themes | [^132^](https://www.zdnet.com/article/how-to-organize-your-slack-workspaces-with-custom-themes/) |
| 7 | Intercom Messenger Setup | [^144^](https://www.intercom.com/help/en/articles/6612589-set-up-and-customize-the-messenger) |
| 8 | Intercom Multi-Brand | [^152^](https://www.intercom.com/help/en/articles/3946163-style-your-messenger-to-support-multiple-brands) |
| 9 | Intercom White-Label | [^151^](https://community.intercom.com/customer-faq-28/inquiry-on-intercom-white-labeling-options-4577) |
| 10 | HubSpot Brand Kit | [^123^](https://knowledge.hubspot.com/branding/edit-your-logo-favicon-and-brand-colors) |
| 11 | Webflow White-Label | [^138^](https://help.webflow.com/hc/en-us/articles/33961375916947-Legacy-Editor-branding-whitelabeling) |
| 12 | Stripe Branding | [^128^](https://docs.stripe.com/get-started/account/branding) |
| 13 | Stripe Connect Features | [^134^](https://stripe.com/connect/features) |
| 14 | Supabase Auth UI Theming | [^149^](https://blog.aiherrera.com/enhancing-user-experience-the-power-of-supabase-auth-ui) |
| 15 | Supabase Badge Brand Issue | [^160^](https://github.com/supabase/supabase/issues/31062) |
| 16 | Vercel Brand Colors | [^137^](https://mobbin.com/colors/brand/vercel) |
| 17 | Figma Workspace Customization | [^159^](https://help.figma.com/hc/en-us/articles/16262618858903-Change-a-workspace-icon-color-or-description) |
| 18 | DTCG Specification Stable | [^173^](https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/) |
| 19 | Style Dictionary Multi-Brand | [^165^](https://www.alwaystwisted.com/articles/a-design-tokens-workflow-part-9.html) |
| 20 | Multi-Tenant SaaS Architecture | [^143^](https://quantumbyte.ai/articles/multi-tenant-architecture) |
| 21 | White-Label SaaS Strategy | [^146^](https://bidscube.com/blog/understanding-white-label-saas/) |
| 22 | Tailwind v4 Multi-Tenant Theming | [^184^](https://wawand.co/blog/posts/managing-multiple-portals-with-tailwind/) |

---

*Documento preparado por el equipo de Producto + Design de FaberLoom. Para consultas, contactar #product-design.*
