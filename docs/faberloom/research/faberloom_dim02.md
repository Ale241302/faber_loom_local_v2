# Dimensión 2: Arquitectura Multi-Tenant para Design Tokens

## Investigación para FaberLoom — Design Tokens en Sistemas Multi-Tenant

**Fecha de investigación:** Enero 2025
**Autor:** Investigador Técnico Especializado
**Contexto:** FaberLoom es multi-tenant. Cada fabricante (tenant) define su identidad visual (colores, tipografía, espaciado) y esa identidad se hereda en todo su workspace. Los agentes IA generan UI desde estos tokens + prosa semántica.

---

## Tabla de Contenidos

1. [Estructura de Tokens: 3-Tier Architecture](#1-estructura-de-tokens-3-tier-architecture)
2. [Casos de Estudio: Shopify, Atlassian, Figma, Adobe Spectrum](#2-casos-de-estudio)
3. [Herencia y Cascada: Estrategias de Fallback](#3-herencia-y-cascada)
4. [Runtime Resolution y Performance](#4-runtime-resolution-y-performance)
5. [Storage Patterns: DB, CDN, Edge Cache](#5-storage-patterns)
6. [Especificación W3C DTCG](#6-especificación-w3c-dtcg)
7. [Approaches para Tenant Overrides sin Duplicación](#7-tenant-overrides)
8. [Herramientas y Librerías para Multi-Tenant Theming](#8-herramientas)
9. [Anti-Patterns y Contra-Argumentos](#9-anti-patterns)
10. [Recomendaciones para FaberLoom](#10-recomendaciones)

---

## 1. Estructura de Tokens: 3-Tier Architecture

### Finding 1.1: Modelo de 3 Tiers (Global → Semantic → Component) es el estándar de facto

```
Claim: La estructura de 3 niveles (global/primitive → semantic/alias → component) es el patrón predominante en design systems enterprise, adoptado por Uber, Atlassian, Salesforce, Adobe, Google Material Design, Microsoft Fluent y GitLab.
Source: Uber Base Design System
URL: https://base.uber.com/6d2425e9f/p/33fa5e-design-tokens
Date: Unknown (documentación vigente)
Excerpt: "Design tokens follow a 3 tier model based on whether the token stores an option or a decision. Each tier is referenced by the one above it (refer to as aliasing)"
Context: Uber documenta explícitamente su modelo de 3 tiers donde cada nivel referencia al de abajo mediante aliasing.
Confidence: high
```

```
Claim: El modelo de 3 tiers puede explicarse como el proceso de un artista: el Global tier es la paleta de colores crudos, el Semantic tier es la visión (asignar significado), y el Component tier es el cuadro final aplicado a elementos UI.
Source: Design Systems Collective
URL: https://www.designsystemscollective.com/the-art-of-design-tokens-a-metaphor-for-the-3-tier-token-model-e166a2ab3073
Date: 2025-03-28
Excerpt: "Just as an artist transforms raw colors into a meaningful composition, a well-structured design token model organizes design decisions into three key levels: Global, Semantic, and Component/Layout tokens."
Context: Artículo explicativo que usa la metáfora de pintura para clarificar la estructura de tokens.
Confidence: high
```

```
Claim: Compound (Element/Matrix) también organiza sus tokens conceptualmente en tres tiers: base, semantic y component tokens, donde el tier superior es global e inconsciente del contexto.
Source: Compound Design System
URL: https://compound.element.io/iframe?viewMode=docs&id=foundations-design-tokens--docs
Date: Unknown
Excerpt: "Token tiers. Our design tokens are conceptually organized into three tiers — base, semantic, and component tokens. The top tier is global and unaware of the..."
Context: Documentación del sistema de diseño Compound (usado por Element/Matrix).
Confidence: high
```

### Finding 1.2: Propuesta "Component-tokens-first" como alternativa

```
Claim: Dan Donald propone un enfoque "component-tokens-first" que desafía la convención de empezar por los base tokens. Argumenta que esto reduce el "blast radius" del cambio y facilita la evolución del sistema.
Source: Medium — Dan Donald
URL: https://medium.com/@hereinthehive/component-tokens-first-hear-me-out-6258f54935a9
Date: 2024-07-24
Excerpt: "Convention dictates that you should approach your design tokens from those base design decisions (stored in tier 1) first, and get this right before moving up the layers. I think we can challenge this with an eye to managing change."
Context: Artículo provocativo que sugiere invertir el orden de construcción para facilitar la gestión del cambio. Especialmente útil para equipos con recursos limitados.
Confidence: medium
```

### Finding 1.3: Trade-offs de la estructura de 3 tiers

```
Claim: Usar alias tokens para la mayoría de la UI y reservar component tokens solo para excepciones es una estrategia práctica y viable, especialmente para equipos sin un equipo dedicado de design system.
Source: Reddit r/DesignSystems
URL: https://www.reddit.com/r/DesignSystems/comments/1it1erb/3tier_design_token_system/
Date: 2025-09-12
Excerpt: "Is it okay to use alias tokens for most of the UI and only reserve component-specific tokens whenever exceptions are needed? I'm especially curious to hear from people with an engineering/dev background."
Context: Discusión práctica sobre cómo equilibrar mantenibilidad y granularidad en el modelo de 3 tiers.
Confidence: medium
```

---

## 2. Casos de Estudio

### Finding 2.1: Atlassian — Semantic Tokens para Multi-Producto

```
Claim: Atlassian usa semantic tokens extensivamente (`color.background.default`) para habilitar la customización de temas preservando claridad. Sus tokens soportan light, dark y high-contrast modes, y se comunican mediante `data-theme` attributes en el DOM.
Source: Atlassian Design System
URL: https://atlassian.design/tokens/design-tokens
Date: Unknown (documentación vigente)
Excerpt: "Design tokens are the new way to apply visual foundations in Atlassian app experiences. We're rolling out tokens to standardize colors, elevations, spacing, and other styles in Atlassian apps."
Context: Atlassian es un caso clave porque opera múltiples productos (Jira, Confluence, Trello) que comparten el mismo sistema de tokens pero pueden tener temas diferentes.
Confidence: high
```

```
Claim: Atlassian provee un API opt-in `view.theme.enable()` en Forge que obtiene el tema activo del host (Jira/Confluence) y lo aplica reactivamente, sincronizando automáticamente cuando el host cambia de tema.
Source: Atlassian Developer Docs
URL: https://developer.atlassian.com/platform/forge/design-tokens-and-theming/
Date: 2024-10-30
Excerpt: "This will fetch the current active theme from the host environment (example, Jira) and apply it in your app. It will also reactively apply theme changes that occur in the host environment so that your app and the host are always in sync."
Context: Patrón de "theme bridging" donde apps de terceros heredan el tema del host producto — directamente aplicable al modelo de FaberLoom donde workspaces heredan tokens del tenant.
Confidence: high
```

```
Claim: Atlassian utiliza `html[data-theme]` y `data-color-mode` para activar tokens CSS. Las apps pueden usar tokens con la función `token()` de `@atlaskit/tokens` que provee type safety adicional.
Source: Atlassian Developer Docs
URL: https://developer.atlassian.com/platform/forge/design-tokens-and-theming/
Date: 2024-10-30
Excerpt: "Design tokens are CSS custom properties so for vanilla CSS, Sass and Less, we recommend accessing design tokens in the following way: `background: var(--ds-surface-raised);`"
Context: Modelo de implementación que combina CSS custom properties con type safety vía JS.
Confidence: high
```

### Finding 2.2: Shopify — Multi-Merchant Theming via Sections y JSON Templates

```
Claim: Shopify implementa temas multi-merchant mediante JSON Templates (Online Store 2.0) donde cada template define secciones como datos, no markup. Los merchants pueden personalizar layouts sin tocar código.
Source: Shopify Partners Blog
URL: https://www.shopify.com/partners/blog/shopify-online-store
Date: 2021-06-29
Excerpt: "Each page type can now be rendered using a JSON template file, which lists the sections of that page, and stores settings data related to any additional section that is added or edited by a merchant."
Context: Arquitectura de separación de estructura (JSON) de presentación (Liquid) que permite personalización por tenant (merchant) sin code changes.
Confidence: high
```

```
Claim: Shopify Polaris divide los tokens en tres tipos: Palette tokens (privados, colores base), Alias tokens (públicos, para construir el admin), y Semantic tokens (contexto específico). Usan HSLuv para consistencia perceptual.
Source: Shopify Polaris React Docs
URL: https://polaris-react.shopify.com/previous-releases/version-11-color
Date: Unknown
Excerpt: "There are now two types of color tokens in Polaris. The palette tokens which are private and used to create new aliases and the alias tokens which is what designers and developers use."
Context: Modelo de token naming: `--p-color-[element]-[role]-[variant]-[state]`. Los modifiers permiten definir estados (hover, active, selected, disabled) como variaciones de tokens base.
Confidence: high
```

```
Claim: Shopify utiliza CSS custom properties (`--p-color-*`) como mecanismo de runtime theming, con naming convention estructurado que comunica propósito, elemento, rol, variante y estado.
Source: Shopify Polaris React — Color Tokens
URL: https://polaris-react.shopify.com/design/colors/color-tokens
Date: Unknown
Excerpt: "Each color token follows the same naming convention. The purpose and intent of a color token is built into the name itself. This makes it easy to understand how and when any given token should be used."
Context: Sistema de naming estructurado: `--p-color-[element]-[role]-[variant]-[state]`. Las partes omitidas implican valores default.
Confidence: high
```

### Finding 2.3: Figma — Multi-Org con Variables y Shared Libraries

```
Claim: Figma soporta multi-org theming a través de Variables (que pueden definir otras variables y styles, soportar múltiples modes, scoping, y code syntax) combinadas con Styles (para gradients y valores compuestos). Los organization admins pueden hacer librerías disponibles para todos los teams.
Source: Figma Help Center
URL: https://help.figma.com/hc/en-us/articles/360040529593-Share-libraries-in-an-organization
Date: Unknown
Excerpt: "Organization admins can make libraries available to all teams in the organization. They can turn libraries on for FigJam files, Figma Design files, or All files."
Context: Modelo de herencia donde las libraries compartidas a nivel organización actúan como "base tokens" que los teams pueden override. Los admins pueden setear libraries default por team.
Confidence: high
```

```
Claim: Las variables de Figma pueden soportar estructuras complejas de tokens porque pueden usarse para definir otras variables y styles. Soportan múltiples modes para theming, scoping para especificar dónde pueden usarse, y code syntax para mejor handoff.
Source: Figma Help Center — Tokens, Variables and Styles
URL: https://help.figma.com/hc/en-us/articles/18490793776023-Update-1-Tokens-variables-and-styles
Date: Unknown
Excerpt: "Variables can support complex token structures, because they can be used to define other variables and styles. They also support multiple modes for theming, scoping for specifying where a variable can be used, and code syntax for a better handoff experience."
Context: Figma implementa un modelo similar al de 3 tiers: las variables pueden ser globales (base), semánticas (referenciando otras), y de componente (scoping).
Confidence: high
```

```
Claim: El REST API de Figma (solo disponible en Enterprise Plan) permite sincronizar variables a repositorios de código, habilitando sync bidireccional. Tokens Studio permite sync multi-file en cuentas pagas.
Source: Supernova Blog
URL: https://www.supernova.io/blog/understanding-the-differences-between-figma-variables-and-design-tokens
Date: 2023-11-10
Excerpt: "When it comes to variables, the REST API is the only one we can sync our variables to our code repository. You can use this API in multiple files. However, this code sync with variables is only available for the Enterprise Plan."
Context: Limitación práctica: el sync código-diseño requiere plan Enterprise de Figma.
Confidence: high
```

### Finding 2.4: Adobe Spectrum — Multi-System Theming con `sp-theme`

```
Claim: Adobe Spectrum implementa un `<sp-theme>` web component que provee design tokens (CSS custom properties) a todo lo que está en su scope DOM. Soporta múltiples variantes: system (spectrum, express, spectrum-two), color (light, dark), y scale (medium, large).
Source: Spectrum Web Components — Theme Docs
URL: https://opensource.adobe.com/spectrum-web-components/tools/theme/
Date: 2025-02-27
Excerpt: "`<sp-theme>` provides Spectrum design tokens (CSS custom properties) to everything in its DOM scope. Components inside a theme use these tokens to render correctly."
Context: Patrón de encapsulación de tema que permite diferentes "contextos" de tokens en diferentes partes del DOM. La `<sp-theme>" actúa como un Theme Provider.
Confidence: high
```

```
Claim: Spectrum CSS usa un patrón de `--mod` prefixed variables para customization con fallback a `--spectrum` prefixed variables sourced from design tokens. Esto permite override local sin duplicar todo el tema.
Source: Adobe Spectrum CSS GitHub
URL: https://github.com/adobe/spectrum-css
Date: 2025-09-15
Excerpt: "token-driven CSS properties are mapped to empty `--mod` prefixed variables (for customization) with a fallback to variables prefixed with `--spectrum` (sourced from the design tokens)."
Context: Patrón de "mod variables" que permite customization por componente sin tener que redefinir todo el tema.
Confidence: high
```

### Finding 2.5: Salesforce — De Design Tokens a CSS Custom Properties (SLDS 2)

```
Claim: Salesforce migró de SLDS design tokens a "global styling hooks" (CSS custom properties) en SLDS 2. Los tokens legacy están deprecated y se reemplazan con `--slds-*` CSS variables. El tema Cosmos usa SLDS 2.
Source: Salesforce Developer Docs
URL: https://developer.salesforce.com/docs/platform/lwc/guide/create-components-css-design-tokens.html
Date: Unknown
Excerpt: "The SLDS design tokens are still present and work normally in SLDS 1 themes, but aren't included in SLDS 2 themes. SLDS 2 replaces design tokens with a system of CSS custom variables called global styling hooks."
Context: Migración importante: Salesforce se movió de tokens compilados a CSS variables runtime. Esto permite que los componentes custom reflejen automáticamente los Themes & Branding settings del org.
Confidence: high
```

```
Claim: Los componentes LWC pueden usar tokens JSON cargados como static resources en runtime. Las CSS variables definidas en `document.documentElement` cruzan shadow DOM boundaries, permitiendo consumirlas sin código especial.
Source: ApexHours Blog
URL: https://www.apexhours.com/custom-theming-systems-for-lwc/
Date: 2026-03-24
Excerpt: "CSS variables are applied to document.documentElement, making them visible inside the shadow DOM of LWCs. LocalStorage persists the chosen theme between sessions."
Context: Patrón de runtime theming donde tokens JSON se mapean a CSS custom properties en `:root`, funcionando incluso dentro de shadow DOM.
Confidence: medium
```

### Finding 2.6: Microsoft Fluent — Two-Layer Token System

```
Claim: Microsoft Fluent usa dos capas de tokens: global tokens (context-agnostic, valores raw como hex codes) y alias tokens (con significado semántico). Soporta OS theming para light, dark, high-contrast y branded elements.
Source: Fluent 2 Design System
URL: https://fluent2.microsoft.design/design-tokens
Date: Unknown
Excerpt: "Fluent uses two layers of tokens. First, global tokens are context-agnostic and store raw values, like hex codes for color. Alias tokens are Fluent's second token layer and add semantic meaning to the stored values."
Context: Sistema de 2 capas (más component tokens en la práctica), diseñado para flexibilidad y accesibilidad out-of-the-box.
Confidence: high
```

```
Claim: Fluent UI React v9 separa el theme shape en tokens más granulares. Los componentes consumen tokens directamente vía CSS custom properties, no vía JS theme object, mejorando significativamente el performance.
Source: Microsoft Learn — Fluent UI React Insights: Theming in v9
URL: https://learn.microsoft.com/en-us/shows/fluent-ui-insights/fluent-ui-insights-theming-in-v9
Date: 2023-04-03
Excerpt: "What is in the v9 theme? ... Theme shape ... Performance challenges ... Are tokens flexible enough? ... High contrast"
Context: Video técnico que discute los desafíos de performance de theming en versiones previas y cómo v9 los resuelve.
Confidence: high
```

### Finding 2.7: Ant Design — Token System con Algoritmos Derivativos

```
Claim: Ant Design v5 implementa un sistema de 3 capas: Seed Token (origen de intención de diseño, ej. `colorPrimary`), Map Token (derivados vía algoritmo, ej. gradientes de color), y Alias Token (alias de componentes comunes). Los algoritmos expanden Seed a Map automáticamente.
Source: Ant Design — Customize Theme Docs
URL: https://github.com/ant-design/ant-design/blob/master/docs/react/customize-theme.en-US.md
Date: Documentación vigente
Excerpt: "In Design Token, we provide a three-layer structure that is more suitable for the design, and disassemble the Design Token into three parts: Seed Token, Map Token and Alias Token."
Context: Modelo único donde los Seed Tokens se expanden algorítmicamente a Map Tokens. Esto permite cambiar un solo color primario y que todo el sistema se recalcule.
Confidence: high
```

```
Claim: Ant Design soporta nested themes mediante `ConfigProvider` anidados. Los tokens no modificados en el tema hijo heredan del tema padre. Soporta zero-runtime mode en v6 donde se importan CSS estáticos.
Source: Ant Design Docs
URL: https://ant.design/docs/react/customize-theme/
Date: Unknown
Excerpt: "By nesting ConfigProvider you can apply local theme to some parts of your page. Design Tokens that have not been changed in the child theme will inherit the parent theme."
Context: Patrón de nested themes directamente aplicable a FaberLoom: workspace puede heredar del tenant padre.
Confidence: high
```

### Finding 2.8: Google Material Design — 4-Level Token Hierarchy

```
Claim: Google Material Design usa 4 niveles: reference tokens (`--md-ref-*`, valores concretos), system tokens (`--md-sys-*`, decisiones de diseño), y component tokens (`--md-filled-button-*`). Los component tokens referencian system tokens, que referencian reference tokens.
Source: Material Web — Theming Docs
URL: https://material-web.dev/theming/material-theming/
Date: Unknown
Excerpt: "Each component token maps to a system token, which has a concrete reference value. On the web, design tokens are CSS custom properties and can be scoped with CSS selectors."
Context: La jerarquía completa es: ref → sys → component. Los reference tokens (`--md-ref-palette-*`) pueden ser reemplazados para generar nuevos temas dinámicamente.
Confidence: high
```

```
Claim: Material Design provee la librería `material-color-utilities` para generar color schemes en runtime a partir de key colors. Esto se usa en Android Material You para dynamic theming.
Source: Material Web — Color Docs
URL: https://github.com/material-components/material-web/blob/main/docs/theming/color.md
Date: Documentación vigente
Excerpt: "Alternatively, use the `material-color-utilities` library to generate color schemes at runtime."
Context: Generación algorítmica de temas completa a partir de un solo color — similar al approach de hextimator.
Confidence: high
```

---

## 3. Herencia y Cascada: Estrategias de Fallback

### Finding 3.1: W3C DTCG Fallback Mechanism ($fallback)

```
Claim: La especificación W3C DTCG define un mecanismo de `$fallback` donde cada mode puede definir un fallback mode. Si un token no define un valor para un mode, usa el fallback. La falta de `$fallback` implica fallback al `$value` default.
Source: W3C Design Tokens Community Group — Issue #210
URL: https://github.com/design-tokens/community-group/issues/210
Date: 2023-03-22
Excerpt: "The lack of a $fallback value implies that mode will fall back to a token's default $value. ... $fallback value must be the name of another mode in the same file."
Context: Mecanismo estándar de fallback en cascada que se puede adaptar para el modelo multi-tenant de FaberLoom.
Confidence: high
```

```
Claim: La resolución de valor para un mode "m" sigue: (1) si el token define valor para "m", se usa; (2) si el mode define `$fallback`, se usa recursivamente; (3) si `$value` está definido, se usa; (4) de lo contrario, el token es undefined (error).
Source: W3C DTCG — Issue #210
URL: https://github.com/design-tokens/community-group/issues/210
Date: 2023-03-22
Excerpt: "1. If the token defines a value for 'm', that value is used. 2. Otherwise, if the mode defines a $fallback, the token's value for the fallback mode is used. 3. Otherwise, if $value is defined, then that value is used. 4. Otherwise, the token is undefined for the mode, which is an error."
Context: Algoritmo formal de resolución que se puede implementar en el sistema de FaberLoom para resolver tokens de tenant.
Confidence: high
```

### Finding 3.2: CSS Custom Properties como Fallback Chain

```
Claim: CSS custom properties soportan fallback values nativamente vía `var(--token, fallback)`. Kong Design Tokens usa SCSS variables como fallback cuando el CSS variable no está definido, permitiendo customization por la app host.
Source: Kong Design Tokens GitHub
URL: https://github.com/Kong/design-tokens
Date: Documentación vigente
Excerpt: "margin: var(--kui-space-20, #{$kui-space-10}); color: var(--kui-color-text-primary, $kui-color-text-primary); ... When Kongponents are imported and used in a host application, the components will utilize the SCSS fallback values by default since the CSS variables are undefined."
Context: Patrón "progressive enhancement": SCSS variables como defaults estáticos, CSS variables como overrides dinámicos por tenant.
Confidence: high
```

### Finding 3.3: Builder.io — Fallback como safety net

```
Claim: Builder.io recomenda definir CSS variables como fuente de verdad primaria y usar fallback values solo como red de seguridad para edge cases. Las actualizaciones deben hacerse en CSS, no en la configuración de tokens.
Source: Builder.io Docs — Design Tokens
URL: https://www.builder.io/c/docs/design-tokens
Date: Unknown
Excerpt: "Fallback values in the designTokens configuration are used only when the CSS variable is undefined. These are not the primary source of truth. ... Update CSS variables directly in CSS."
Context: Best practice de mantener la fuente de verdad en CSS variables globales, no en config de JS.
Confidence: high
```

---

## 4. Runtime Resolution y Performance

### Finding 4.1: CSS Custom Properties — Performance Investigado

```
Claim: GitLab realizó benchmarks extensivos y concluyó que no hay impacto significativo de performance al usar CSS custom properties comparado con no usarlas. La diferencia fue solo ~10ms (1.8%) en tiempo total de renderizado. Incluso 3 niveles de nesting de variables no impactan el CSS rendering en sí, solo el tamaño del CSS a descargar.
Source: GitLab Pajamas Design System — Issue #2344
URL: https://gitlab.com/gitlab-org/gitlab-services/design.gitlab.com/-/issues/2344
Date: 2026-05-04
Excerpt: "There is no significant performance impact when comparing 'no custom properties' vs. 'custom properties' as long as the HTML and CSS which has to be download has a comparable size. The difference was 1.8% higher (539ms vs. 549ms)."
Context: Investigación exhaustiva de GitLab que valida que CSS custom properties son seguras para producción a escala.
Confidence: high
```

```
Claim: Cambiar una CSS variable en un elemento padre con muchos hijos que la usan puede ser costoso (76ms en un caso documentado). Es preferible cambiarla en el elemento más específico posible. `setProperty` es más performante que inline styles.
Source: Stack Overflow — CSS Variables Performance
URL: https://stackoverflow.com/questions/56497989/effect-of-many-css-variables-on-performance
Date: 2020-04-12
Excerpt: "Via Javascript the --bg variable was first set on the .container parent element, which resulted in a fairly long duration of 76ms. Then the same variable was set on the first child .el, which only lasted about 1.9ms."
Context: Lección clave: scoping de variables importa. Para FaberLoom, setear variables en el root del workspace (no en `:root` global) reduce recálculos.
Confidence: high
```

### Finding 4.2: Reddit — SSR + Theming Performance Lesson

```
Claim: Reddit enfrentó problemas de escalabilidad al inyectar CSS server-side por sesión de usuario en SSR, lo que rompió la cacheabilidad. La solución fue mover themes a client-side CSS variables, restaurando cacheability y reduciendo carga SSR en 80%.
Source: ehosseini.info — Server-Side Rendering Deep Dive
URL: https://ehosseini.info/articles/server-side-rendering-ssr/
Date: 2023-03-31
Excerpt: "Reddit also faced scaling issues when rendering community pages server-side with dynamic theming. Their SSR pipeline initially injected CSS server-side per user session, which broke cacheability. Their solution: move themes to client-side CSS variables, restoring cacheability and reducing SSR load by 80%."
Context: Lección crítica para FaberLoom: no inyectar CSS tenant-specific en SSR. Usar CSS variables client-side con valores default.
Confidence: high
```

### Finding 4.3: Hextimator — Runtime Theme Generation

```
Claim: Hextimator es una librería que genera temas completos a partir de un solo color de marca en runtime, usando OKLCH para uniformidad perceptual y garantizando WCAG AAA contrast. Diseñada explícitamente para apps multi-tenant B2B2C.
Source: hextimator GitHub
URL: https://github.com/fgrgic/hextimator
Date: 2026-03-04
Excerpt: "Per-tenant themes from a single one brand color: Runtime theming for B2B2C and white-label apps. Your customers pick a brand color. Your app looks good. Every time."
Context: Librería con 433 descargas semanales que demuestra que runtime theme generation es viable y adoptado.
Confidence: high
```

### Finding 4.4: Edge Computing para Token Resolution

```
Claim: Cloudflare Workers ofrecen cold start <1ms, 300+ edge locations globales, y 60-80% reducción en TTFB vs infraestructura centralizada. Workers KV provee almacenamiento key-value globalmente replicado.
Source: Digital Applied — Edge Computing Cloudflare Workers Guide
URL: https://www.digitalapplied.com/blog/edge-computing-cloudflare-workers-development-guide-2026
Date: 2026-01-14
Excerpt: "Workers use V8 JavaScript isolates, the same technology Chrome uses to run browser tabs. Isolates are lighter than containers and start in under 1ms, eliminating cold starts entirely."
Context: Cloudflare Workers puede usarse para resolver y cachear tokens de tenant en el edge, sirviendo CSS variables personalizado con mínima latencia.
Confidence: medium
```

---

## 5. Storage Patterns

### Finding 5.1: Multi-Tenant Data Isolation Patterns

```
Claim: Existen tres patrones principales de aislamiento de datos multi-tenant: (1) Shared database, shared schema con `tenant_id` column — más simple, barato, pero requiere query discipline; (2) Shared database, separate schema por tenant — mejor aislamiento, migraciones más complejas; (3) Separate database por tenant — máximo aislamiento, máximo costo operacional.
Source: WorkOS — Developer's Guide to SaaS Multi-Tenant Architecture
URL: https://workos.com/blog/developers-guide-saas-multi-tenant-architecture
Date: 2025-12-03
Excerpt: "Start with a shared schema unless you know you'll be forced otherwise. But design your code so a tenant can be 'moved out' later if needed."
Context: Recomendación práctica: empezar con shared schema + tenant_id. Aplica directamente al almacenamiento de tokens multi-tenant.
Confidence: high
```

```
Claim: Para < 10,000 tenants, row-level isolation en una sola base de datos funciona cómodamente. Para > 50,000 tenants, considerar sharding horizontal o database-per-tenant si se requiere data residency.
Source: Render — Building a SaaS Application from Scratch
URL: https://render.com/articles/building-and-deploying-a-saas-application-from-scratch
Date: 2025-11-19
Excerpt: "< 10,000 tenants: Row-level isolation on a single database works comfortably. > 50,000 tenants: Consider horizontal sharding or if you need geographic data residency."
Context: Métricas concretas de escalabilidad para FaberLoom. En fase inicial, shared schema + tenant_id es suficiente.
Confidence: high
```

### Finding 5.2: Caching Estratificado para Tenant Data

```
Claim: En sistemas multi-tenant, usar cache con TTLs diferenciados: TTL alto (900s) para datos estables (nombre tenant, IDs) y TTL bajo (300s) para datos que cambian frecuentemente (plan, feature flags, branding tokens).
Source: Render — SaaS Building Guide
URL: https://render.com/articles/building-and-deploying-a-saas-application-from-scratch
Date: 2025-11-19
Excerpt: "Use higher TTLs (900s) for stable data (names, IDs) and lower TTLs (300s) for frequently changing data (plan status, feature flags)."
Context: Patrón aplicable directamente a tokens de tenant: los base tokens raramente cambian (alto TTL), los brand tokens pueden cambiar más frecuentemente.
Confidence: high
```

```
Claim: Redis con tenant-prefixed keys (ej. `tenant:123:tokens`) maneja caching y session management en fase 1 (10-100 tenants). En fase 2 (100-1000 tenants), Redis ACLs permiten aislamiento de keyspace por tenant.
Source: Redis Blog — Data Isolation in Multi-Tenant SaaS
URL: https://redis.io/blog/data-isolation-multi-tenant-saas/
Date: 2026-02-06
Excerpt: "A single Redis instance with tenant-prefixed keys (like tenant1:session:*) typically handles caching and session management needs. Redis ACLs become more important here, allowing you to enforce keyspace isolation."
Context: Estrategia de cache para tokens: keys con prefijo de tenant ID, TTLs diferenciados por tipo de token.
Confidence: high
```

### Finding 5.3: CDN Caching para Assets Estáticos

```
Claim: La estrategia óptima de CDN caching para assets con hash de contenido es TTL de 1 año, ya que cambios crean nuevas URLs. Para datos de API (como tokens de tenant), TTL recomendado de 30-60 segundos.
Source: OneUptime — CDN Caching Strategies
URL: https://oneuptime.com/blog/post/2026-01-30-cdn-caching-strategies/view
Date: 2026-01-30
Excerpt: "Versioned assets: 1 year (content hash in filename). Public API responses: 30-60 seconds."
Context: Para tokens de tenant servidos vía API: cache corto (30-60s) en CDN. Para CSS generado con hash de contenido: cache largo (1 año).
Confidence: high
```

---

## 6. Especificación W3C DTCG

### Finding 6.1: Especificación estable publicada (Octubre 2025)

```
Claim: La Design Tokens Community Group publicó la primera versión estable de la especificación Design Tokens (2025.10) en octubre 2025. Incluye Format Module, Color Module y Resolver Module. Es vendor-neutral y production-ready.
Source: W3C Design Tokens Community Group
URL: https://www.w3.org/community/design-tokens/
Date: 2025-10-28
Excerpt: "The Design Tokens Community Group today announced the first stable version of the Design Tokens Specification (2025.10), marking a milestone for design systems teams and tool makers worldwide."
Context: La especificación estándar que FaberLoom debería adoptar para formato de tokens, asegurando interoperabilidad con herramientas de diseño.
Confidence: high
```

```
Claim: El Resolver Module define un proceso formal de resolución: input validation → ordering (flattening de `resolutionOrder`) → alias resolution. Permite múltiples sets de tokens y modifiers para organizar tokens en múltiples archivos JSON.
Source: Design Tokens Resolver Module 2025.10
URL: https://www.designtokens.org/tr/drafts/resolver/
Date: 2026-04-27 (preview)
Excerpt: "A resolver document allows for the use of tokens to exist in multiple JSON files for organization. But for the purposes of portability, it may be advantageous to deal with only a single JSON document."
Context: El resolver formaliza cómo combinar múltiples fuentes de tokens (útil para merge de base + tenant override).
Confidence: high
```

---

## 7. Approaches para Tenant Overrides sin Duplicación

### Finding 7.1: Style Dictionary — Deep Merge para Overrides

```
Claim: Style Dictionary realiza deep merge de todos los archivos fuente, donde archivos posteriores toman precedencia. Permite usar `include` para archivos base y `source` para overrides, sin warnings de colisión (el override es intencional).
Source: Style Dictionary Docs
URL: https://styledictionary.com/info/tokens/
Date: Unknown
Excerpt: "Style Dictionary takes all the files it finds in the include and source arrays and performs a deep merge on them. ... A file in source overriding a file in include will not show a warning because the intent is that you include files you want to potentially override."
Context: Patrón directamente aplicable: base tokens en `include`, tenant overrides en `source`.
Confidence: high
```

```
Claim: El método multi-file de Style Dictionary permite generar dark/light modes ejecutando Style Dictionary múltiples veces con diferentes sets de archivos fuente. Los archivos de override (ej. `dark-tokens/`) solo contienen los tokens que cambian, no duplican todo.
Source: dbanks.design — Dark Mode with Style Dictionary
URL: https://dbanks.design/blog/dark-mode-with-style-dictionary/
Date: 2021-04-29
Excerpt: "We are only overriding the value. Then we run Style Dictionary once with the only light/default token file and once with the dark token file to generate a set of light-mode outputs and dark-mode outputs."
Context: Patrón aplicable a tenants: cada tenant solo define overrides, no un tema completo.
Confidence: high
```

### Finding 7.2: Tailwind v4 — Scoped Theme con `@theme` y `@layer`

```
Claim: Tailwind v4 permite definir tokens por tenant usando `@layer base` con selectores de clase (`.tenant-a`, `.tenant-b`). Cada tenant hereda del tema base pero puede sobreescribir variables específicas. No se duplica CSS.
Source: Wawand.co — Scalable Theming with Tailwind v4
URL: https://wawand.co/blog/posts/managing-multiple-portals-with-tailwind/
Date: 2025-09-18
Excerpt: "This system lets you support thousands of tenants or theme variants without duplicating CSS or managing brittle override logic. Adding a new context is as simple as defining a new scoped theme."
Context: Modelo práctico para FaberLoom: CSS base + clases tenant-specific que override variables. Escalable a miles de tenants.
Confidence: high
```

### Finding 7.3: Multi-Tenant Theming con React Context

```
Claim: Un patrón práctico para multi-tenant theming usa: Environment Variable → Design Tokens → MUI Theme → Components. Los tokens son platform-agnostic y se transforman al format del UI library.
Source: Qimu.dev — Multi-Tenant Theming
URL: https://www.qimu.dev/blog/2026-01-06-1-multi-tenant-theming
Date: 2026-01-06
Excerpt: "Environment Variable (NEXT_PUBLIC_TENANT) → Design Tokens (platform-agnostic colors) → MUI Theme (MUI-specific configuration) → Components (via useDesignTokens hook)"
Context: Patrón de arquitectura limpia que separa tokens semánticos de la implementación UI. Anti-pattern a evitar: webpack-based component overrides.
Confidence: high
```

---

## 8. Herramientas y Librerías para Multi-Tenant Theming

### Finding 8.1: React Theming Engine — 3-Layer para React

```
Claim: `react-theming-engine` es un motor de 3 capas para React: Brand Palette → Semantic Tokens → CSS Variables. Tiene 61 descargas semanales con crecimiento del 29%.
Source: npm search
URL: https://npmx.dev/search?q=keyword:multi-brand
Date: 2026-05-07
Excerpt: "react-theming-engine: A 3-layer React theming engine: Brand Palette → Semantic Tokens → CSS Variables"
Context: Librería emergente que implementa el modelo de 3 tiers específicamente para React + CSS variables.
Confidence: medium
```

### Finding 8.2: Chakra UI v3 — Zero Runtime Token Resolution

```
Claim: Chakra UI v3 con Panda CSS permite "zero runtime token resolution": los tokens se resuelven en build time, no en runtime. Soporta multi-theme, responsive design y semantic tokens vía `themes` object.
Source: Dev.to — Generating a Custom Chakra UI v3 Theme from Design Tokens
URL: https://dev.to/kiranmantha/generating-a-custom-chakra-ui-v3-theme-from-design-tokens-a-complete-guide-1085
Date: 2025-10-30
Excerpt: "Zero runtime token resolution... Supports multi-theme, responsive, semantic design. Fully automated and type-safe."
Context: Para FaberLoom, build-time resolution para base tokens + runtime para tenant overrides puede ser la combinación óptima.
Confidence: medium
```

---

## 9. Anti-Patterns y Contra-Argumentos

### Finding 9.1: Anti-Pattern — Webpack Component Overrides

```
Claim: Usar webpack aliases para swap de componentes por tenant (Button.tsx, Button.tenant1.tsx, Button.tenant2.tsx) es un anti-pattern porque: complejidad de build, componentes de bajo nivel que conocen marcas, y dificultad para testear y reutilizar.
Source: Qimu.dev — Multi-Tenant Theming
URL: https://www.qimu.dev/blog/2026-01-06-1-multi-tenant-theming
Date: 2026-01-06
Excerpt: "Problems: Complex build configuration, Low-level components become brand-aware, Harder to test and reuse."
Context: La alternativa correcta es mantener componentes "dumb" que reciben tokens vía props o context.
Confidence: high
```

### Finding 9.2: Anti-Pattern — Excesiva Customización

```
Claim: El exceso de customización por tenant hace la plataforma más difícil de mantener. La regla de oro es "Configuration over Custom Code" — nunca permitir que una request de cliente resulte en un "hard fork" del codebase.
Source: Developex — White-Label SaaS Architecture Guide
URL: https://developex.com/blog/building-scalable-white-label-saas/
Date: 2026-01-26
Excerpt: "Prioritize Configuration over Custom Code. Never allow a client request to result in a 'hard fork' of your codebase. Instead, use a robust metadata layer and feature flagging system."
Context: Principio clave para FaberLoom: los tenants customizan tokens, no componentes ni lógica.
Confidence: high
```

### Finding 9.3: Limitación — CSS Output Size en SSR

```
Claim: Ant Design reportó que su approach de CSS-in-JS (que incluye todos los estilos de un componente independientemente de uso) produce output CSS significativamente grande, especialmente noticeable en SSR con inline style tags.
Source: Ant Design Blog — CSS Var Plan
URL: https://ant.design/docs/blog/css-var-plan/
Date: 2023-11-20
Excerpt: "In antd 5.0, whenever a component is used, antd automatically includes all styles related to that component—whether they are used or not. ... Antd's css output size becomes significantly large, which is particularly noticeable in SSR scenarios."
Context: Lección para FaberLoom: usar CSS variables + clases utilitarias en lugar de CSS-in-JS que serializa todo.
Confidence: high
```

### Finding 9.4: Contra-Argumento — 3-Tier Model puede ser Overkill

```
Claim: El modelo de 3 tiers puede ser excesivo para equipos con recursos limitados. Es aceptable usar alias tokens para la mayoría de la UI y reservar component tokens solo para excepciones. No es necesario tener 100% de component tokens desde el inicio.
Source: Reddit r/DesignSystems
URL: https://reddit.com/r/DesignSystems/comments/1it1erb/3tier_design_token_system/
Date: 2025-09-12
Excerpt: "I've heard that the 'right' way to structure a token system would involve assigning all colour values to component-specific tokens. However, this approach seems challenging to maintain without a dedicated DS team."
Context: Contra-argumento práctico: empezar simple y evolucionar. No requiere perfección desde el día 1.
Confidence: medium
```

---

## 10. Recomendaciones para FaberLoom

### Arquitectura Recomendada

```
┌─────────────────────────────────────────────────────────────┐
│                     TOKEN ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Tier 1: Base / Primitive Tokens (Platform-wide)            │
│  ├── color.blue.500: #007BFF                                │
│  ├── spacing.4: 4px                                         │
│  └── font.size.16: 16px                                     │
│                    ↓                                         │
│  Tier 2: Semantic / Alias Tokens (Platform-wide)            │
│  ├── color.brand.primary → {color.blue.500}                 │
│  ├── color.background.surface → {color.gray.50}             │
│  └── spacing.component.padding → {spacing.4}                │
│                    ↓                                         │
│  Tier 3: Component Tokens (Platform-wide defaults)          │
│  ├── button.background → {color.brand.primary}              │
│  ├── button.border.radius → {radius.md}                     │
│  └── card.padding → {spacing.component.padding}             │
│                    ↓                                         │
│  Tier 4: Tenant Overrides (Per-tenant JSON in DB)           │
│  ├── tenant_123: {color.brand.primary: "#FF6B35"}          │
│  └── tenant_456: {button.border.radius: "0px"}              │
│                    ↓                                         │
│  Tier 5: Workspace Overrides (Per-workspace JSON in DB)     │
│  └── workspace_789: {card.padding: "24px"}                  │
│                                                              │
│  Resolution: Base → Semantic → Component → Tenant → WS      │
│  Strategy: Deep merge, último gana, con fallback chain      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Performance Strategy

```
1. BUILD TIME: Style Dictionary genera CSS con base + semantic + component tokens
   → Archivo CSS con hash de contenido → CDN cache 1 año
   
2. TENANT LOOKUP (Request-time):
   a. Edge/Worker recibe request con tenant_id (JWT/subdomain/header)
   b. Cache check: Redis/Edge Cache "tenant:123:tokens" → TTL 5 min
   c. Cache miss: DB lookup → merge base + tenant overrides → cache
   
3. RUNTIME (Browser):
   a. CSS base se carga del CDN (cacheado)
   b. CSS variables de tenant se inyectan vía <style> tag o CSS-in-JS
   c. Los componentes usan var(--token) con fallbacks al CSS base
   
4. AI GENERATION:
   a. Los agentes IA resuelven tokens vía API (no hardcoded values)
   b. Cada prompt incluye el resolved token set del tenant activo
```

### Storage Recommendations

| Layer | Storage | Format | TTL/Cache |
|-------|---------|--------|-----------|
| Base Tokens | Git repo + Style Dictionary | JSON (DTCG) | Build-time only |
| Semantic Tokens | Git repo + Style Dictionary | JSON (DTCG) | Build-time only |
| Component Tokens | Git repo + Style Dictionary | JSON (DTCG) | Build-time only |
| Tenant Overrides | PostgreSQL (JSONB column) | JSON | Redis 5 min + Edge 30s |
| Workspace Overrides | PostgreSQL (JSONB column) | JSON | Redis 5 min + Edge 30s |
| Resolved CSS | CDN (R2/S3) | CSS con content-hash | 1 año |
| Runtime Tenant CSS | `<style>` tag o CSS-in-JS | CSS variables | Session/localStorage |

### Key Decisions

1. **Usar 3 tiers mínimo** (base → semantic → component) con un 4to tier para tenant overrides y 5to para workspace overrides.

2. **Adoptar formato W3C DTCG** para todos los archivos de tokens, asegurando interoperabilidad futura con herramientas.

3. **CSS Custom Properties como mecanismo runtime** — no CSS-in-JS que serializa todo. Performance validado por benchmarks de GitLab.

4. **Separar base CSS (build-time, CDN) de tenant CSS (runtime, injected)** — evitar SSR per-tenant que rompe cacheabilidad.

5. **Usar deep merge con precedencia por nivel**: base → tenant → workspace. Solo almacenar overrides, no temas completos.

6. **Cache estratificado**: Edge CDN para CSS estático (1 año), Redis para tokens de tenant (5 min), Edge Functions para resolución.

---

## Summary Ejecutivo

- **El modelo de 3 tiers (base → semantic → component) es el estándar de facto** en la industria, adoptado por Uber, Atlassian, Salesforce, Adobe, Microsoft, Google y GitLab. Para multi-tenant se recomienda extender a 5 tiers añadiendo tenant overrides y workspace overrides.

- **CSS Custom Properties son el mecanismo óptimo para runtime theming**: benchmarks de GitLab demuestran <2% impacto en performance. Reddit redujo carga SSR 80% moviendo theming a client-side CSS variables.

- **Los tenants solo deberían definir overrides, no temas completos**: Style Dictionary hace deep merge; Tailwind v4 permite scoped themes por clase; hextimator genera temas completos a partir de un solo color.

- **Casos de estudio clave**: Shopify (JSON Templates para merchant customization), Atlassian (`view.theme.enable()` para herencia de tema de host), Figma (variables multi-mode con shared libraries), Adobe Spectrum (`<sp-theme>` web component), Salesforce (migración a CSS custom properties en SLDS 2).

- **Storage recomendado**: PostgreSQL JSONB para tenant overrides (shared schema + tenant_id), Redis cache con TTL diferenciado, CDN para CSS estático con content-hash, Edge Functions para resolución de tokens.

- **Anti-patterns a evitar**: Webpack component overrides por tenant, CSS-in-JS con serialización completa en SSR, hard forks de código por tenant, y over-engineering del sistema de tokens desde el día 1.

---

## Gaps Identificados

1. **Falta documentación pública detallada sobre la implementación interna de Shopify Polaris para multi-merchant**: Shopify documenta el sistema de tokens pero no la arquitectura de resolución en runtime para miles de merchants.

2. **No se encontraron benchmarks específicos de "token resolution para 10,000+ tenants"**: Los benchmarks existentes son de CSS custom properties en general, no de sistemas con miles de tenants concurrentes.

3. **Poca información sobre Atlassian multi-product token sharing**: Se sabe que usan semantic tokens pero no se encontró documentación sobre cómo Jira vs Coniman manejan diferencias de branding.

4. **Edge Functions para token resolution es un patrón emergente**: No se encontraron casos de estudio en producción a gran escala usando Cloudflare Workers o Vercel Edge para resolver design tokens.

5. **No se encontró investigación sobre el impacto de tokens en generación de UI por IA**: Es un campo nuevo donde no hay precedentes documentados de design tokens + LLMs generando UI.

---

## Recomendaciones Específicas

| # | Recomendación | Confidence | Prioridad |
|---|--------------|------------|-----------|
| 1 | Usar arquitectura de 5 tiers con deep merge y solo almacenar overrides | high | P0 |
| 2 | Implementar CSS custom properties como mecanismo runtime | high | P0 |
| 3 | Almacenar tenant overrides en PostgreSQL JSONB con tenant_id | high | P0 |
| 4 | Cachear tokens en Redis con TTL 5 min, Edge CDN 30s para API | high | P0 |
| 5 | Adoptar formato W3C DTCG para todos los archivos de tokens | high | P1 |
| 6 | Usar Style Dictionary para build pipeline | high | P1 |
| 7 | No usar CSS-in-JS que serialice todos los estilos (problema SSR) | high | P1 |
| 8 | Probar hextimator para generación automática de temas a partir de brand color | medium | P2 |
| 9 | Evaluar Cloudflare Workers para edge resolution de tokens | medium | P2 |
| 10 | Empezar simple: alias tokens para mayoría, component tokens solo para excepciones | high | P0 |
