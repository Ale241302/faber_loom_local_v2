# Dimension 1: Formatos de Design Tokens - Comparacion Tecnica Feature-by-Feature

> **Contexto:** FaberLoom - SaaS multi-tenant para fabricantes donde cada fabricante define su identidad visual y la hereda en su workspace. Los agentes IA generan UI desde tokens + prosa semantica.
> **Fecha de investigacion:** Mayo 2026
> **Investigador:** Sistema de investigacion tecnica

---

## Tabla Comparativa Principal

| Feature | DESIGN.md | DTCG | Style Dictionary | Specify | Tokens Studio |
|---------|-----------|------|------------------|---------|---------------|
| **Token types soportados** | Color, Dimension, Typography, Spacing, Rounded, Component refs | 13 tipos oficiales: color, dimension, fontFamily, fontWeight, duration, cubicBezier, number, strokeStyle, border, transition, shadow, gradient, typography + $extensions | Hereda de DTCG (v4); transforma cualquier tipo via hooks custom | 50+ token types (mas amplio del mercado) | 23+ token types oficiales + tipos legacy/unofficial + composite (typography) |
| **Herencia / extends** | Token references `{path.to.token}` en YAML; component-to-token aliasing | `$value` puede referenciar otro token via `{token.path}`; `$type` heredable desde grupo (v2025.10) | Full aliasing via `source`/`include` merge; referencias preservables con `outputReferences` | Referencias entre tokens; multi-source sync | Referencias `{token.path}`; multi-dimensional theming con token sets |
| **Multi-tenant / themes** | No nativo; exporta a DTCG para theming | `$type` inheritance desde grupo; no nativo multi-tenant pero extensible via `$extensions` | Si: multi-platform builds; token sets separados por theme; theme switching via config | Si: multi-brand/multi-source sync nativo | Si (Pro): multi-dimensional theming via `$themes.json`; permutacion de dimensiones (mode x brand) |
| **Formatos de export** | Tailwind v3 JSON, Tailwind v4 CSS, DTCG JSON | N/A (formato estandar de intercambio) | CSS, SCSS, Less, Stylus, JS, TS, JSON, iOS Swift (class/enum/struct), Android XML, Compose Kotlin, Flutter | 15+ code formats | CSS, JSON, CSS-in-JS, iOS, Android, 10+ formats via sd-transforms |
| **Governance / versionado** | CLI con `lint`, `diff`, `export`; WCAG AA contrast checks; reglas de linting estructurado | `$deprecated` para migraciones; `$description` para documentacion | JSON validation basica; linting via CI/CD externo | Team collaboration con real-time sync; versionado Git nativo | GitHub two-way sync nativo; version control via Git; CLI/SDK para transformaciones |
| **Transformaciones / build** | Export a otros formatos (no build pipeline propiamente) | N/A (especificacion, no herramienta) | Pipeline completo: preprocessors, transforms, transformGroups, formats, actions, filters | Pipeline automatizado de generacion y export | sd-transforms package para Style Dictionary; token-transformer; graph engine |
| **Licencia y costo** | Apache-2.0 (gratis, open source) | Gratis (estandar W3C publico) | Apache-2.0 (gratis, open source) | ~$76.50-$255/mes (SaaS comercial) | Plugin Figma gratis (MPL-2.0); Studio/Pro de pago |
| **Adopcion enterprise** | Muy temprana (alpha, desde abr 2026); Google Labs / Stitch | Estandar emergente W3C v1 (oct 2025); amplia adopcion en progreso | Alta; Amazon, Salesforce, Atlassian, GitLab, y muchos mas | Media-alta; empresas design-led | Alta; usado por equipos grandes (Atlassian, Salesforce, Cisco) |
| **Tooling ecosystem** | CLI oficial (@google/design.md); linter; diff tool; export | Validadores DTCG; sd-transforms; terrazzo; cobolt-ui | Extenso: sd-transforms, configurator, playground, plugins CI/CD | Integracion con Figma, Tokens Studio, Variables, GitHub | Plugin Figma, Penpot plugin, sd-transforms, configurator, CLI, Framer integration |
| **Programmatic access** | API JavaScript: `lint()`, `export()`, `diff()`; CLI npm | N/A (especificación) | API Node.js completa: `StyleDictionary` class, async methods, hooks, ESM | SDK TypeScript (@specifyapp/sdk): `SpecifyClient`, `SDTFClient`, `SDTFEngine` | CLI/SDK; sd-transforms ESM; graph engine; `register(StyleDictionary)` |

---

## 1. DESIGN.md (Google Labs)

### Descripcion General

DESIGN.md es un formato de especificacion open-source de Google Labs para describir sistemas de diseno a agentes de coding. Combina tokens de diseno legibles por maquinas (YAML front matter) con prosa de diseno legible por humanos (cuerpo markdown), permitiendo que los LLMs apliquen identidad visual correctamente.

```
Claim: DESIGN.md es un formato alpha de Google Labs, open-source bajo Apache-2.0, que combina YAML front matter con markdown body para consumo por agentes IA.
Source: GitHub - google-labs-code/design.md
URL: https://github.com/google-labs-code/design.md
Date: 2026-04-10
Excerpt: "DESIGN.md is a self-contained, plain-text representation of a design system. It defines the visual identity of a brand and product, thereby ensuring that these stylistic choices can be followed across design sessions and between different AI agents and tools."
Context: Es la contraparte de diseno para CLAUDE.md/AGENTS.md. Google Stitch es el consumidor de referencia.
Confidence: high
```

### Token Types Soportados

| Categoria | Tipos | Notas |
|-----------|-------|-------|
| Color | Hex (sRGB) | `#1A1C1E` - simple, sin espacios de color avanzados |
| Typography | fontFamily, fontSize, fontWeight, lineHeight, letterSpacing, fontFeature, fontVariation | Objeto compuesto |
| Spacing | Scale tokens (xs, sm, md, lg, xl) | Valor numerico o dimension |
| Rounded | Scale levels (sm, md, lg, full) | Dimension (px, em, rem) |
| Components | backgroundColor, textColor, typography, rounded, padding, size, height, width | Mapea a sub-tokens via referencias |

```
Claim: DESIGN.md soporta 5 categorias de tokens: colors, typography, spacing, rounded, y components, con token referencing via sintaxis {path.to.token}.
Source: design.md/docs/spec.md
URL: https://github.com/google-labs-code/design.md/blob/main/docs/spec.md
Date: 2026-04-10
Excerpt: "Design tokens are embedded as YAML front matter... colors, typography, spacing, rounded, components"
Context: No soporta shadows, borders, gradients, durations, ni otros tipos avanzados nativamente.
Confidence: high
```

### Herencia y Referencias

- **Token referencing**: Sintaxis `{path.to.token}` para cross-referencing (inspirado en DTCG)
- **Component aliasing**: Los componentes referencian tokens definidos, ej: `backgroundColor: "{colors.tertiary}"`
- No hay sistema nativo de theming o multi-dimensional token sets

### Export y Build Pipeline

| Formato | Comando | Descripcion |
|---------|---------|-------------|
| Tailwind v3 JSON | `export --format json-tailwind` | Emite `theme.extend` object |
| Tailwind v4 CSS | `export --format css-tailwind` | Emite `@theme { ... }` block |
| DTCG JSON | `export --format dtcg` | W3C Design Tokens Format Module |

```
Claim: DESIGN.md exporta a Tailwind v3, Tailwind v4 CSS, y formato DTCG W3C via CLI.
Source: GitHub - google-labs-code/design.md
URL: https://github.com/google-labs-code/design.md
Date: 2026-04-10
Excerpt: "Export DESIGN.md tokens to other formats... Tailwind v3 config (JSON), Tailwind v4 theme (CSS), DTCG tokens.json"
Context: No tiene pipeline de build propio; es un formato de definicion que exporta a otros sistemas.
Confidence: high
```

### Governance

- **Linting**: CLI `npx @google/design.md lint` - 7 reglas:
  - `broken-ref`: error en referencias rotas
  - `missing-primary`: warning si no hay color primary
  - `contrast-ratio`: WCAG AA check para backgroundColor/textColor
  - `orphaned-tokens`: tokens no referenciados
  - `section-order`: orden canonico de secciones
- **Diff**: `npx @google/design.md diff` compara versiones y detecta regresiones

### Limitaciones para FaberLoom

- **Alpha status**: El formato esta en alpha activo; cambios esperados
- **No multi-tenant nativo**: Sin soporte para themes, modes, o workspaces multiples
- **Tipos limitados**: Sin soporte nativo para shadow, border, gradient, animation tokens
- **Sin API REST/GraphQL**: Solo API JavaScript local

---

## 2. W3C DTCG (Design Tokens Community Group Format)

### Descripcion General

El formato DTCG es la especificacion estandar del W3C para design tokens, publicada como v1 estable en octubre de 2025. Es un formato de intercambio (no una herramienta) que define como los tokens deben estructurarse para interoperabilidad cross-tool.

```
Claim: W3C DTCG publico la especificacion v1 estable en octubre 2025, definiendo estandar universal para design tokens.
Source: CSS Author - Design Token Management Tools 2025
URL: https://cssauthor.com/design-token-management-tools/
Date: 2025-12-04
Excerpt: "W3C Design Tokens Framework (Specification v1 – Oct 2025)... With W3C v1 stable, you're no longer locked into proprietary token formats."
Context: Soportado por 10+ herramientas incluyendo Tokens Studio, Supernova, Penpot, Style Dictionary, Figma.
Confidence: high
```

### Token Types Oficiales (13)

| Tipo | Descripcion | Ejemplo |
|------|-------------|---------|
| `color` | Color en UI | `#ff0000` o objeto con colorSpace/components |
| `dimension` | Distancia unidimensional | `{"value": 16, "unit": "px"}` |
| `fontFamily` | Nombre de fuente o array | `"Inter"` o `["Inter", "sans-serif"]` |
| `fontWeight` | Peso de fuente | `400`, `700` |
| `duration` | Unidad de tiempo | `{"value": 200, "unit": "ms"}` |
| `cubicBezier` | Curva de animacion | `[0.4, 0.0, 0.2, 1]` |
| `number` | Numero sin unidades | `1.5` |
| `strokeStyle` | Estilo de trazo | `{"lineCap": "round", "lineJoin": "round"}` |
| `border` | Borde completo | `{color, width, style} |
| `transition` | Transicion animada | `{duration, delay, timingFunction}` |
| `shadow` | Sombra (single o array) | `{color, offsetX, offsetY, blur, spread, inset}` |
| `gradient` | Gradiente de colores | Array de stops `{color, position}` |
| `typography` | Estilo tipografico completo | `{fontFamily, fontSize, fontWeight, lineHeight, letterSpacing}` |

```
Claim: DTCG define 13 tipos oficiales: color, dimension, fontFamily, fontWeight, duration, cubicBezier, number, strokeStyle, border, transition, shadow, gradient, typography.
Source: Terrazzo Docs - DTCG Tokens
URL: https://terrazzo.app/docs/guides/dtcg/
Date: Unknown
Excerpt: "Currently, the DTCG format defines the following types: Color, Dimension, Font Family, Font Weight, Duration, Cubic Bezier, Number, Stroke Style, Border, Transition, Shadow, Gradient, Typography"
Context: Tipos pendientes: fontStyle, percentage/ratio, File para assets.
Confidence: high
```

### Herencia y Referencias

- **Token referencing**: `{path.to.token}` en `$value` para aliasing
- **$type inheritance**: En la version 2025.10, `$type` puede definirse en el grupo y heredarse por los tokens hijos
- **$extensions**: Escape hatch para propiedades custom, tool-specific, governance metadata

```
Claim: DTCG permite heredar $type desde grupos (v2025.10) y usar $extensions para propiedades custom.
Source: Always Twisted - Understanding $extensions in the Design Tokens Specification
URL: https://www.alwaystwisted.com/articles/understanding-extensions-in-the-design-tokens-spec.html
Date: 2026-01-30
Excerpt: "The DTCG intentionally placed almost no constraints on what can go in here... Use reverse domain notation."
Context: $extensions es clave para SaaS multi-tenant: podria almacenar tenant_id, workspace metadata, etc.
Confidence: high
```

### Multi-tenancy

- No tiene soporte nativo para multi-tenant o multi-brand
- Extensible via `$extensions` para almacenar metadatos de workspace/tenant
- Style Dictionary v4+ puede manejar multi-theme builds sobre archivos DTCG

### Governanza

- `$deprecated` con mensaje de migracion antes de eliminar tokens
- `$description` para documentacion inline
- Semantic versioning recomendado en archivos

```
Claim: DTCG incluye propiedades para governance: $deprecated para deprecacion controlada y $description para documentacion.
Source: LobeHub Skills - design-tokens
URL: https://lobehub.com/skills/tyler-r-kendrick-agent-skills-design-tokens
Date: 2026-03-05
Excerpt: "Use $deprecated with a migration message before removing tokens... Add $description to non-obvious tokens"
Context: La gobernanza se implementa en la herramienta que consume DTCG, no en la especificacion misma.
Confidence: high
```

---

## 3. Style Dictionary (Amazon)

### Descripcion General

Style Dictionary es un build system open-source creado por Amazon (Danny Banks, 2017) que transforma design tokens de una fuente unica a multiples formatos de plataforma. La v4 (2024+) adopto DTCG como formato nativo.

```
Claim: Style Dictionary v4 adopto el formato DTCG nativamente, convirtiendo tokens DTCG a cualquier formato de plataforma.
Source: Style Dictionary Docs - DTCG
URL: https://styledictionary.com/info/dtcg/
Date: Unknown
Excerpt: "As of version 4, Style Dictionary has first-class support for the DTCG format."
Context: El principal build system de la industria. En v5 se planea soporte completo para DTCG 2025.10.
Confidence: high
```

### Token Types y Transforms

- **ESM-only** en v4 (ya no soporta CJS)
- **Hooks system**: transforms, formats, filters, actions, parsers, preprocessors
- **TransformGroups predefinidos**: `css`, `scss`, `js`, `ios-swift`, `android`, `compose`

### Formatos Built-in

| Plataforma | Formato | Ejemplo Output |
|------------|---------|----------------|
| CSS | `css/variables` | Custom Properties |
| SCSS | `scss/variables` | Variables SCSS |
| Less | `less/variables` | Variables Less |
| JS | `javascript/es6` | Export ES6 |
| TS | `typescript/es6-declarations` | Declarations |
| iOS | `ios-swift/class.swift` | `public class` |
| iOS | `ios-swift/enum.swift` | `public enum` |
| iOS | `ios-swift/any.swift` | Custom objectType |
| Android | `android/colors` | XML colors |
| Android | `android/dimens` | XML dimensions |
| Compose | `compose/object` | Kotlin object |
| JSON | `json/nested` | JSON nested |
| JSON | `json/flat` | JSON flat |

```
Claim: Style Dictionary soporta 15+ formatos built-in incluyendo CSS, SCSS, JS, TS, iOS Swift (class/enum/struct), Android XML, y Compose Kotlin.
Source: Style Dictionary Docs - Built-in formats
URL: https://styledictionary.com/reference/hooks/formats/predefined/
Date: Unknown
Excerpt: "ios-swift/class.swift, ios-swift/enum.swift, ios-swift/any.swift, android/colors, compose/object, css/variables, scss/variables, javascript/es6, typescript/es6-declarations"
Context: Custom formats y transforms son extensibles via hooks.
Confidence: high
```

### Multi-tenancy / Theming

- **Multi-platform builds**: Diferentes plataformas desde la misma fuente
- **Source/Include merge**: Archivos base + overrides por tema
- **Filters**: Token filtering por atributos para builds condicionales
- **Async API**: `new StyleDictionary(cfg)`, `buildAllPlatforms()` retorna Promise

```
Claim: Style Dictionary soporta multi-theme via source/include merging, filters, y configuracion por plataforma.
Source: Medium - Design tokens architecture
URL: https://medium.com/@jdposada/design-tokens-architecture-7544c9a8f33a
Date: 2025-10-29
Excerpt: "Git as the single source of truth, Tokens Studio for two-way sync, and a CI/CD pipeline with Style Dictionary to validate, transform, and distribute tokens automatically."
Context: El patron tipico es Git -> Style Dictionary -> npm package -> aplicaciones.
Confidence: high
```

### Programmatic Access (v4)

```javascript
import StyleDictionary from 'style-dictionary';

const sd = new StyleDictionary({
  source: ['tokens/**/*.json'],
  preprocessors: ['tokens-studio'],
  platforms: { css: { transformGroup: 'tokens-studio', files: [...] } }
});

await sd.cleanAllPlatforms();
await sd.buildAllPlatforms();
```

```
Claim: Style Dictionary v4 usa ESM, API async con new StyleDictionary(), y soporta preprocessors como 'tokens-studio'.
Source: Style Dictionary Docs - Configuration
URL: https://styledictionary.com/reference/config/
Date: Unknown
Excerpt: "source, include, tokens, expand, platforms, hooks, preprocessors, parsers..."
Context: Breaking change de v3: StyleDictionary.extend() -> new StyleDictionary(); CJS -> ESM.
Confidence: high
```

---

## 4. Specify

### Descripcion General

Specify es una plataforma comercial SaaS para gestion de design tokens, enfocada en designers. Actua como "token engine" consolidando multiples fuentes (Figma Variables, Tokens Studio) en una sola fuente de verdad.

```
Claim: Specify soporta 50+ token types, multi-source sync nativo, y export a 15+ formatos de codigo.
Source: CSS Author - Design Token Management Tools 2025
URL: https://cssauthor.com/design-token-management-tools/
Date: 2025-12-04
Excerpt: "50+ token types supported (the most comprehensive)... Multi-source sync (Figma, Variables, Tokens Studio simultaneously)... Export to 15+ code formats"
Context: Es la plataforma con mayor cobertura de tipos de token del mercado.
Confidence: high
```

### Features Clave

| Feature | Descripcion |
|---------|-------------|
| Token Types | 50+ (mas amplio del mercado) |
| Multi-source | Figma Variables + Tokens Studio simultaneo |
| Export | 15+ code formats |
| Colaboracion | Real-time sync |
| Compliance | W3C Design Tokens compliant |
| Naming | Smart naming suggestions |

### Programmatic Access

```
Claim: Specify ofrece un SDK TypeScript en npm (@specifyapp/sdk) con APIs como SpecifyClient, SDTFClient, y SDTFEngine.
Source: Specify Docs - Specify SDK
URL: https://docs.specifyapp.com/reference/specify-sdk
Date: 2024-03-25
Excerpt: "The @specifyapp/sdk TypeScript package is available on npm... SpecifyClient, SDTFClient, SDTFEngine, TokenState | CollectionState | GroupState"
Context: SDK completo para acceso programatico. La API parece estar enfocada en GraphQL-like queries.
Confidence: medium
```

### Precios

| Plan | Precio | Notas |
|------|--------|-------|
| Essentials | $76.50/mes | Plan base |
| Advanced | $255.00/mes | Plan avanzado |

```
Claim: Specify tiene precios desde $76.50/mes (Essentials) hasta $255/mes (Advanced).
Source: SaaSworthy - Specify Pricing
URL: https://www.saasworthy.com/product/specifyapp/pricing
Date: 2025-07-04
Excerpt: "Essentials Plan at $76.50 per month. Advanced Plan at $255.00 per month."
Context: Tambien ofrecen free trial. Modelo SaaS puramente comercial.
Confidence: medium
```

### Limitaciones para FaberLoom

- **Costo recurrente**: $900-$3,000+/ano
- **Vendor lock-in**: Plataforma SaaS cerrada
- **No multi-tenant nativo**: Aunque soporta multi-brand, la isolation por workspace/tenant requeriria arquitectura custom

---

## 5. Tokens Studio

### Descripcion General

Tokens Studio es un plugin open-source para Figma (y Penpot) que gestiona design tokens con capacidades avanzadas. Tiene una version gratuita como plugin Figma y una plataforma de pago (Studio/Pro).

```
Claim: Tokens Studio es open source (MPL-2.0), soporta 23+ token types, y tiene W3C DTCG compliance.
Source: CSS Author - Design Token Management Tools 2025
URL: https://cssauthor.com/design-token-management-tools/
Date: 2025-12-04
Excerpt: "23+ token types... GitHub integration for version control and CI/CD automation... W3C Design Tokens Specification v1 compliance"
Context: El plugin Figma es gratuito. La plataforma Studio/Pro es de pago. Repositorio tiene 1.6k+ stars.
Confidence: high
```

### Token Types (23+)

| Categoria | Token Types |
|-----------|-------------|
| Basic | color, dimension, fontFamily, fontWeight, duration, cubicBezier, number |
| Typography | fontFamily, fontWeight, lineHeight, letterSpacing, paragraphSpacing, paragraphIndent, textDecoration, textCase |
| Visual | borderRadius, borderWidth, borderColor, boxShadow, opacity |
| Layout | spacing, sizing |
| Asset | asset, font |
| Otros | other |

```
Claim: Tokens Studio soporta tipos oficiales DTCG + tipos propios legacy (borderWidth, fontSize, etc.) + composite tokens (typography con 9 propiedades).
Source: Tokens Studio Docs - Token Types
URL: https://docs.tokens.studio/manage-tokens/token-types
Date: 2025-01-09
Excerpt: "Official Token Types are listed in the W3C DTCG Specifications... Unofficial Token Types were created by Tokens Studio before the W3C DTCG Specs defined an alternate Token Type."
Context: Tiene conversion automatica de tipos legacy a DTCG via sd-transforms preprocessor.
Confidence: high
```

### Multi-dimensional Theming (Pro)

Tokens Studio tiene el sistema de theming mas avanzado del mercado via `$themes.json`:

```
Claim: Tokens Studio soporta multi-dimensional theming nativo con permutacion automatica de combinaciones tema.
Source: npm - @tokens-studio/sd-transforms
URL: https://www.npmjs.com/package/@tokens-studio/sd-transforms
Date: 2025-12-10
Excerpt: "Running permutateThemes on these themes will generate 4 theme combinations: light_casual, dark_casual, light_business, dark_business"
Context: Ejemplo: 2 grupos (mode: light/dark, brand: casual/business) = 4 combinaciones. Ideal para multi-tenant.
Confidence: high
```

**Ejemplo de multi-dimensional theming:**
```javascript
import { register, permutateThemes } from '@tokens-studio/sd-transforms';
// Genera: light_casual, dark_casual, light_business, dark_business
const themes = permutateThemes($themes, { separator: '_' });
```

### GitHub Sync (Two-way)

- Push de JSON tokens a GitHub
- Pull de tokens desde cualquier Figma file
- Branch-based workflow
- Token storage: folder (multi-file, Pro) o single file (free)

### sd-transforms

```
Claim: sd-transforms es el paquete oficial que conecta Tokens Studio con Style Dictionary, con transforms para CSS, Android, y tipos custom.
Source: GitHub - tokens-studio/sd-transforms
URL: https://github.com/tokens-studio/sd-transforms
Date: 2025-12-10
Excerpt: "Custom transforms for Style-Dictionary, to work with Design Tokens that are exported from Tokens Studio"
Context: Soporta: expand, math resolution, opacity %->decimal, color modifiers, shadow transforms, Android Compose.
Confidence: high
```

### Precios

| Plan | Costo | Features |
|------|-------|----------|
| Free (Plugin) | Gratis | Token management basico, single-file sync |
| Pro/Studio | De pago | Multi-file sync, $themes, GitHub automation, CLI |

---

## Recomendaciones para FaberLoom

### Escenario: SaaS Multi-tenant con Agentes IA

Dado el contexto de FaberLoom (SaaS multi-tenant donde cada fabricante define su identidad visual y agentes IA generan UI), aqui va el analisis:

| Requisito | Mejor Opcion | Razonamiento |
|-----------|-------------|--------------|
| **Fuente de verdad** | DTCG + Style Dictionary v4 | Estandar abierto, transformable a cualquier formato, no vendor lock-in |
| **Definicion de marca por tenant** | Tokens Studio ($themes) o Style Dictionary config por tenant | Multi-dimensional theming nativo en Tokens Studio; SD soporta multi-config |
| **Generacion de UI por IA** | DESIGN.md como capa de presentacion | Los agentes consumen DESIGN.md que exporta a DTCG; el formato YAML+MD es nativo para LLMs |
| **Build pipeline** | Style Dictionary v4 + sd-transforms | Pipeline robusto, CI/CD friendly, async API, DTCG native |
| **Governance** | Git + CI/CD + linting custom | Versionado en Git, semantic-release, Conventional Commits |

### Arquitectura Recomendada

```
Tenant A                    Tenant B
   |                           |
   v                           v
DESIGN.md (por tenant)    DESIGN.md (por tenant)
   |                           |
   v                           v
Export --format dtcg      Export --format dtcg
   |                           |
   v                           v
tokens/tenant-a.dtcg.json  tokens/tenant-b.dtcg.json
   |                           |
   +-----------+---------------+
               |
               v
        Style Dictionary v4
        (transform + build)
               |
       +-------+-------+
       |               |
       v               v
  CSS Variables     Tailwind Theme
  (runtime)         (build-time)
       |
       v
   UI Components
   (Agente IA lee
    DESIGN.md +
    consume CSS vars)
```

### Estrategia Hibrida Recomendada

1. **DTCG como formato base de intercambio**: Todos los tokens se almacenan en formato DTCG estandar
2. **Style Dictionary v4 como build pipeline**: Transforma DTCG a CSS/Tailwind/JSON para cada tenant
3. **DESIGN.md como contrato IA**: Cada tenant tiene un DESIGN.md que describe su identidad (el agente lee esto para generar UI con contexto de marca)
4. **Tokens Studio (opcional)**: Para el equipo de diseno interno que edita tokens en Figma
5. **Git como source of truth**: Repositorio con tokens por tenant, CI/CD automatizado

### Contra-argumentos y Consideraciones

| Contra-argumento | Mitigacion |
|-------------------|------------|
| DESIGN.md es alpha | Usar solo como capa de presentacion para IA, no como fuente de verdad; monitorear evolucion |
| DTCG no tiene multi-tenant nativo | Implementar via $extensions o separacion de archivos por tenant en el repositorio |
| Style Dictionary requiere Node.js | Es build-time, no runtime; se ejecuta en CI/CD |
| Tokens Studio Pro tiene costo | La version gratuita del plugin cubre necesidades basicas; evaluar ROI de Pro |
| Sin solucion "todo en uno" | La composicion de herramientas especializadas es preferible a vendor lock-in en enterprise |

---

## Gaps Identificados

1. **No hay comparacion head-to-head independiente** de los 5 formatos en un solo articulo; la mayoria de comparaciones son de subsets (Specify vs Tokens Studio, Style Dictionary vs Theo, etc.)

2. **Specify API documentation es escasa**: El SDK existe pero la documentacion detallada de endpoints REST/GraphQL no es publicamente accesible

3. **DESIGN.md no tiene evaluacion de produccion aun**: Al ser alpha (abr 2026), no hay case studies de adopcion enterprise

4. **Multi-tenancy nativo en design tokens**: Ningun formato tiene soporte nativo para aislamiento por tenant/workspace; requiere arquitectura custom

5. **Performance a escala**: No se encontraron benchmarks de Style Dictionary v4 procesando 10k+ tokens en CI/CD

6. **Tokens Studio pricing exacto**: No hay precios publicos detallados para el plan Pro/Studio

7. **Soporte para AI-native workflows**: Solo DESIGN.md esta explicitamente disenado para consumo por LLMs; los demas requieren parsing

---

## Summary Ejecutivo

1. **Para FaberLoom, recomendamos una estrategia hibrida**: DTCG como formato base estandar, Style Dictionary v4 como pipeline de build, y DESIGN.md como capa semantica para agentes IA. Esta combinacion aprovecha los estandares abiertos sin vendor lock-in.

2. **Ningun formato tiene multi-tenancy nativo**: La isolation por tenant debe implementarse a nivel de arquitectura (separacion de archivos/repositorios por tenant, o namespace de tokens), no en el formato mismo.

3. **Style Dictionary v4 es la pieza central tecnica**: Su adopcion de DTCG como formato nativo, su extenso ecosistema de transforms/formatos, y su API async moderna lo convierten en el build system mas maduro para enterprise.

4. **DESIGN.md es prometedor pero inmaduro**: En alpha, con cambios esperados. Su valor unico es la combinacion YAML+Markdown para consumo por LLMs. Recomendado como capa de presentacion, no como fuente de verdad.

5. **Specify y Tokens Studio son complementarios para equipos de diseno**: Specify como plataforma SaaS para designers; Tokens Studio como plugin Figma para edicion de tokens. Ambos pueden alimentar el pipeline DTCG+Style Dictionary.

6. **Multi-dimensional theming de Tokens Studio es el modelo a seguir**: Su sistema de `$themes.json` con permutacion de dimensiones (mode x brand) es el patron mas avanzado para multi-tenant visual identity.

---

## Fuentes Consultadas

| # | Fuente | URL | Fecha |
|---|--------|-----|-------|
| 1 | DESIGN.md Spec (GitHub) | https://github.com/google-labs-code/design.md | 2026-04-10 |
| 2 | DESIGN.md Full Spec | https://github.com/google-labs-code/design.md/blob/main/docs/spec.md | 2026-04-10 |
| 3 | DTCG Format Module 2025.10 | https://www.designtokens.org/tr/drafts/format/ | 2026-05-08 |
| 4 | Style Dictionary v4 DTCG | https://styledictionary.com/info/dtcg/ | Unknown |
| 5 | Style Dictionary Config | https://styledictionary.com/reference/config/ | Unknown |
| 6 | Style Dictionary Formats | https://styledictionary.com/reference/hooks/formats/predefined/ | Unknown |
| 7 | Tokens Studio Docs - Token Types | https://docs.tokens.studio/manage-tokens/token-types | 2025-01-09 |
| 8 | Tokens Studio Token Format | https://docs.tokens.studio/manage-settings/token-format | 2025-01-09 |
| 9 | Tokens Studio GitHub | https://github.com/tokens-studio | 2026-05-08 |
| 10 | sd-transforms (GitHub) | https://github.com/tokens-studio/sd-transforms | 2025-12-10 |
| 11 | sd-transforms (npm) | https://www.npmjs.com/package/@tokens-studio/sd-transforms | 2025-12-10 |
| 12 | Specify SDK Docs | https://docs.specifyapp.com/reference/specify-sdk | 2024-03-25 |
| 13 | CSS Author - Token Tools 2025 | https://cssauthor.com/design-token-management-tools/ | 2025-12-04 |
| 14 | Design Tokens Architecture | https://medium.com/@jdposada/design-tokens-architecture-7544c9a8f33a | 2025-10-29 |
| 15 | SaaSworthy - Specify Pricing | https://www.saasworthy.com/product/specifyapp/pricing | 2025-07-04 |
| 16 | Understanding $extensions | https://www.alwaystwisted.com/articles/understanding-extensions-in-the-design-tokens-spec.html | 2026-01-30 |
| 17 | Style Dictionary v4 Plans | https://tokens.studio/blog/style-dictionary-v4-plan | 2026-04-29 |
| 18 | Token Formats Comparison (Hyva) | https://docs.hyva.io/hyva-themes/working-with-tailwindcss/design-tokens/formats.html | Unknown |
| 19 | DTCG Tokens Guide (Terrazzo) | https://terrazzo.app/docs/guides/dtcg/ | Unknown |
| 20 | Deep Dive on Design Tokens | https://deep-dive-on-design-tokens.com/3-integration/ | Unknown |
| 21 | Multi-Brand Systems | https://frontendmasters.com/blog/exploring-multi-brand-systems-with-tokens-and-composability/ | 2025-12-19 |
| 22 | Multi-Brand Design Systems | https://robertcelt95.medium.com/theming-architecture-multi-brand-design-systems-that-actually-work-ad7ed8445fed | 2025-11-27 |
| 23 | DESIGN.md Explained | https://departmentofproduct.substack.com/p/designmd-explained-the-format-reshaping | 2026-04-27 |
| 24 | Google makes DESIGN.md open source | https://medium.com/design-bootcamp/google-makes-design-md-open-source-on-its-way-to-become-a-industry-standard-16119f2368dd | 2026-04-22 |
| 25 | Tokens Studio Website | https://tokens.studio/ | 2026-04-29 |
| 26 | Design Token Governance | https://www.door3.com/blog/design-token-governance | 2024-10-11 |
| 27 | GitLab - Authoring Design Tokens | https://design.gitlab.com/product-foundations/design-tokens-authoring | 2026-01-16 |
| 28 | Design Lint/Enforcement | https://medium.com/design-bootcamp/why-your-design-tokens-work-in-theory-and-break-in-practice-67c77dcbec3d | 2026-04-25 |

---

*Documento generado por investigacion tecnica. Todas las citas corresponden a fuentes verificadas al momento de la investigacion.*
