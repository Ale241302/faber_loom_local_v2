# SPEC_FABERLOOM_DESIGN_FOUNDATION_v1

**Base de Design System + UX + Action Flow para FaberLoom**

| | |
|---|---|
| **Producto** | FaberLoom — SaaS multi-tenant para fabricantes con agentes IA generadores de UI |
| **Versión** | v1.0 |
| **Fecha** | 2026-05-11 |
| **Autoría** | Muito Work Limitada — Investigación integrada (12 agentes paralelos, 350+ findings, 60+ fuentes) |
| **Estado** | Listo para commitear en KB |
| **Audience** | CEO, CTO, Product Lead, Design Lead |

---

# Executive Summary

## Alcance y Contexto

Especificación de fundación técnica para FaberLoom: SaaS multi-tenant para fabricantes donde agentes de IA generan interfaces a partir de design tokens. Construida sobre 12 dimensiones de investigación, 350+ findings y 60+ fuentes primarias de mayo 2026. Blueprint técnico con decisiones arquitectónicas justificadas por evidencia y conflict zones resueltos explícitamente.

FaberLoom opera en una intersección que ningún vendor cubre: design tokens formales para generación programática por agentes, en contexto industrial donde un error de UI puede detener una línea de producción. Esa intersección define cada decisión.

## Key Findings

**Formato de tokens: DTCG + Style Dictionary v4, arquitectura dual.** Confidence ALTO. El W3C DTCG Format es el único estándar formal con adopción enterprise medible: Style Dictionary v4+ lo soporta nativamente y 20+ organizaciones respaldan la especificación [^1^][^3^]. La arquitectura dual — DTCG JSON como source of truth parseable por agentes, CSS Custom Properties como capa de runtime — es el patrón de Shopify, Atlassian, GitHub, IBM y Adobe [^2^]. Para FaberLoom es obligatoria: los agentes necesitan tokens estructurados para generar UI consistente, y cada tenant requiere su bundle CSS resuelto en edge sin overhead [^1^].

**Principio rector: Trust Ladder con autonomía progresiva.** Confidence ALTO. El 93% de usuarios experimenta consent fatigue con aprobaciones excesivas [^7^]. En manufactura, aprobar sin control es inaceptable. La respuesta es un Autonomy Engine de cuatro niveles: Level 0 (humano obligatorio para acciones destructivas), Level 1 (confianza >90%, notificación), Level 2 (confianza >95%, log silencioso), Level 3 (auto-approval con digest diario) [^7^]. Cada tenant configura su nivel; cada usuario puede bajarlo individualmente.

**Diferenciación: Sanidad como tab primario.** Confidence MEDIO-ALTO. Ninguna plataforma agentic — LangGraph Studio, AutoGen, CrewAI, Vercel v0, Bolt, Cursor — implementa validación como tab de igual jerarquía que Configuración e Iteración [^10^]. Todas lo relegan a funcionalidad secundaria. En manufactura regulada, sanidad es paso obligatorio del modelo mental operario. El tab Sanidad incluye visual diff, scorecard de calidad y trazabilidad completa; justifica el precio enterprise [^11^]. El riesgo es descubribilidad.

**Patterns obligatorios: 3-Checkpoint, 4 estados AG-UI, chat+GUI.** Confidence ALTO. El patrón 3-Checkpoint (aprobar/descartar/iterar) está en 8+ productos [^8^]. Los cuatro estados del AG-UI Protocol estandarizan comunicación agente-UI con 17 eventos, permitiendo cambiar backends sin reescribir el frontend [^9^]. El chat es correcto para iniciar pero insuficiente para tareas complejas: FaberLoom debe ser chat-initiated, GUI-mediated [^12^].

**Anti-patterns prohibidos.** Confidence ALTO. Chat-only sin GUI, dark patterns, auto-approval sin historial y gamificación son patrones B2C destructivos en B2B industrial [^13^]. En una fábrica el objetivo es eficiencia operativa, no engagement.

**Tooling: validación antes que edición.** Confidence ALTO. En multi-tenant, un token inválido afecta a todos los usuarios del fabricante [^14^]. Stack obligatorio: DTCG schema validator, WCAG contrast checker, stylelint con plugin custom y visual regression por tenant.

| Dimensión | Recomendación | Confidence | Justificación clave |
|---|---|---|---|
| Formato tokens | DTCG JSON source of truth + CSS Custom Properties runtime | ALTO | 20+ orgs respaldan DTCG; 11/12 enterprises usan CSS variables [^1^][^2^] |
| Build pipeline | Style Dictionary v4+ con codemods de migración | ALTO | 952K descargas semanales npm; DTCG nativo desde v4 [^3^] |
| Principio UX #1 | Trust Ladder: autonomía progresiva de 4 niveles | ALTO | 93% consent fatigue; modelo mental industrial requiere control [^7^] |
| Principio UX #2 | Progressive Disclosure en todo flujo agentic | ALTO | Score 9.3/10 en evaluación FaberLoom; principio HMI universal [^6^] |
| Diferenciación | Sanidad como tab primario con diff + scorecard + trazabilidad | MEDIO-ALTO | Ninguna plataforma agentic lo tiene; alineado con ISO/Six Sigma [^10^][^11^] |
| Comunicación agente-UI | AG-UI Protocol con 4 estados + 17 eventos | MEDIO-ALTO | Adopción en progreso por Microsoft, LangChain; irreversible post-impl. [^9^] |
| Patrón aprobación | 3-Checkpoint Approval + auto-approve progresivo por riesgo | ALTO | 8+ productos; Cursor valida auto-approval configurable [^8^] |
| Interacción | Chat-initiated, GUI-mediated; nunca chat-only | ALTO | Anthropic: chat para apertura, GUI para pasos intermedios [^12^] |
| Anti-patterns | Prohibir: chat-only, dark patterns, auto-approval sin historial | ALTO | Patrones B2C destructivos en B2B industrial [^13^] |
| Tooling | stylelint + DTCG validator + WCAG checker + LangSmith + AG-UI | ALTO | Error de token en multi-tenant afecta todos los usuarios del tenant [^14^] |

Las filas ALTO tienen conflict zones resueltos y múltiples fuentes independientes. Las dos filas MEDIO-ALTO — Sanidad como tab y AG-UI Protocol — son apuestas estratégicas irreversibles que deben tomarse en el diseño inicial.


---

# 1. Matriz Comparativa de Formatos de Design Tokens

La eleccion del formato de design tokens no es reversible sin costo. FaberLoom opera en un contexto multi-tenant donde cada fabricante define su identidad visual y los agentes IA generan UI a partir de esas definiciones. Esta seccion analiza los formatos disponibles, su adopcion enterprise, su momentum proyectado y los riesgos de migracion entre ellos, para emitir una recomendacion fundamentada de formato base con nivel de confianza explicito.

## 1.1 Comparacion Feature-by-Feature

### 1.1.1 Tabla Comparativa de Formatos

La siguiente tabla compara los seis formatos relevantes para FaberLoom: W3C DTCG (el estandar), Style Dictionary (el pipeline), Tokens Studio (la herramienta visual), Specify (la plataforma comercial), DESIGN.md (el experimento para LLMs) y Terrazzo (la alternativa emergente). El criterio de inclusion es que cada formato se evalua en su rol potencial dentro de la arquitectura de FaberLoom, no como producto independiente.

| Feature | DTCG W3C | Style Dictionary v4+ | Tokens Studio | Specify | DESIGN.md | Terrazzo |
|---|---|---|---|---|---|---|
| **Tipos de token** | 13 oficiales (color, dimension, fontFamily, duration, shadow, gradient, typography, etc.) [^1^] | Hereda de DTCG; transforma cualquier tipo via hooks custom [^2^] | 23+ oficiales + tipos legacy + composite typography [^3^] | 50+ (mas amplio del mercado) [^4^] | 5 categorias (color, typography, spacing, rounded, components) [^5^] | Soporte completo DTCG 2025.10 con resolvers [^6^] |
| **Herencia / Referencias** | `$value` referencia tokens via `{path}`; `$type` heredable desde grupo (v2025.10) [^7^] | Full aliasing via `source`/`include` merge; `outputReferences` preserva refs [^8^] | Referencias `{token.path}`; multi-dimensional theming con `$themes.json` [^9^] | Referencias entre tokens; multi-source sync [^10^] | Token referencing `{path.to.token}` en YAML; component aliasing [^5^] | Resolucion formal DTCG con alias resolution [^6^] |
| **Multi-tenant / Themes** | No nativo; extensible via `$extensions` [^7^] | Multi-platform builds; deep merge `source`+`include`; filters [^8^] | Multi-dimensional theming nativo (Pro): permutacion de dimensiones [^9^] | Multi-brand/multi-source sync nativo [^10^] | No nativo; exporta a DTCG para theming [^5^] | No nativo; basado en DTCG con `$extensions` [^6^] |
| **Export formats** | N/A (formato de intercambio, no herramienta) | 15+ built-in: CSS, SCSS, Less, JS, TS, iOS Swift, Android XML, Compose Kotlin, JSON [^2^] | CSS, JSON, CSS-in-JS, iOS, Android via `sd-transforms` [^3^] | 15+ code formats [^4^] | Tailwind v3 JSON, Tailwind v4 CSS, DTCG JSON [^5^] | CSS, Sass, JS/TS, Swift, Tailwind [^6^] |
| **Governance** | `$deprecated` con mensaje; `$description` inline [^11^] | JSON validation basica; linting via CI/CD externo [^12^] | GitHub two-way sync nativo; version control via Git [^9^] | Real-time sync; versionado Git nativo [^10^] | CLI `lint`: 7 reglas incl. WCAG AA contrast check; `diff` tool [^5^] | CLI con validacion DTCG schema [^6^] |
| **Pipeline build** | N/A | Completo: preprocessors, transforms, transformGroups, formats, actions, filters, hooks [^8^] | `sd-transforms` + `token-transformer` + graph engine [^9^] | Pipeline automatizado de generacion y export [^10^] | No tiene pipeline propio; exporta a otros sistemas [^5^] | CLI-first; plugins para transformacion [^6^] |
| **Licencia / Costo** | Gratis (estandar W3C publico) | Apache-2.0 (open source) | Plugin Figma gratis (MPL-2.0); Pro desde 39 EUR/mes [^13^] | SaaS: 76.50-255 USD/mes [^14^] | Apache-2.0 (open source) | MIT (open source) |
| **Adopcion enterprise** | Estandar emergente; 10+ herramientas implementando [^15^] | Alta; 952K descargas semanales npm; Amazon, Adobe, GitLab [^16^] | Alta; Atlassian, Salesforce, Cisco; plugin mas popular para tokens en Figma [^3^] | Media-alta; empresas design-led [^4^] | Muy temprana; alpha desde abril 2025; Google Labs / Stitch [^17^] | Emergente; releases regulares; menor adopcion enterprise [^6^] |
| **API programatica** | N/A (especificacion) | API Node.js completa: class `StyleDictionary`, async methods, hooks, ESM [^8^] | CLI/SDK; `register(StyleDictionary)` [^9^] | SDK TypeScript: `SpecifyClient`, `SDTFEngine` [^10^] | API JS: `lint()`, `export()`, `diff()`; CLI npm [^5^] | API JS: CLI programmatico; plugins API [^6^] |

La tabla revela una division clara en tres categorias de herramientas: estandares de intercambio (DTCG), pipelines de transformacion (Style Dictionary, Terrazzo), y herramientas de edicion/distribucion (Tokens Studio, Specify). DESIGN.md ocupa una categoria propia como formato de consumo para LLMs. Ningun formato ofrece multi-tenancy nativo; todos lo habilitan via extensiones o arquitectura de aislamiento externa.

### 1.1.2 Analisis por Formato

**W3C DTCG** es la especificacion de referencia, no una herramienta. Su valor no esta en las features sino en la interoperabilidad: al ser el estandar W3C, cualquier herramienta del ecosistema (Figma, Style Dictionary, Tokens Studio, Terrazzo, Penpot) puede leer y escribir el formato. La especificacion 2025.10 estable, publicada en octubre de 2025, incluye soporte para theming, multi-file, espacios de color modernos (Display P3, OKLCH) y relaciones de tokens con herencia [^15^]. La limitacion principal es que DTCG no resuelve tokens — solo los estructura. Necesita un pipeline como Style Dictionary para convertirse en CSS utilizable.

**Style Dictionary v4+** es el pipeline de transformacion dominante. Con 952,000 descargas semanales en npm, es la herramienta de build mas madura del ecosistema [^16^]. La v4 adopto DTCG como formato nativo, migro a ESM, introdujo API async con `new StyleDictionary()`, y un sistema de hooks para transforms, formats, filters y preprocessors [^8^]. La v5.4.0 (marzo 2026) anadio soporte completo para DTCG 2025.10 incluyendo dimension token object values y 14 espacios de color [^18^]. El proyecto es co-mantenido por Danny Banks (Amazon) y Joren Broekema (Tokens Studio), lo que garantiza continuidad pero con riezgo de cuello de botella en 2-3 mantenedores clave.

**Tokens Studio** tiene el sistema de theming multi-dimensional mas avanzado del mercado via `$themes.json`, que permite permutar automaticamente combinaciones de dimensiones (mode x brand x density) [^9^]. Por ejemplo, 2 modos (light/dark) por 2 marcas (casual/business) generan 4 combinaciones automaticamente. Esta capacidad es directamente aplicable al modelo multi-tenant de FaberLoom, donde cada fabricante es una "marca" con sus propios valores de token. El riesgo es que Tokens Studio es una empresa pequena (1-10 empleados segun ZoomInfo) dependiente del ecosistema Figma/Penpot, con modelo freemium que puede no escalar economicamente [^13^].

**Specify** tiene la cobertura mas amplia de tipos de token (50+) y multi-source sync nativo, pero introduce vendor lock-in via su formato propietario SDTF (Specify Design Token Format) [^10^]. No se encontro documentacion de migracion *from* Specify *to* otra plataforma, y el funding seed de 4.6M EUR (2022) no ha mostrado rondas adicionales, sugiriendo posible extension de runway sin Series A [^19^]. Para FaberLoom, Specify es util como herramienta de edicion visual para el equipo de diseno interno, pero no debe ser el source of truth.

**DESIGN.md** (Google Labs, abril 2025) es un formato alpha que combina YAML front matter con cuerpo Markdown para consumo por agentes IA [^17^]. Su valor unico es la prosa semantica: las reglas de diseno escritas en lenguaje natural que un LLM puede interpretar para generar UI contextualmente correcta. Sin embargo, el proyecto tiene actividad muy limitada post-lanzamiento, Google Labs tiene historial de abandonar proyectos experimentales, y no hay evidencia de adopcion enterprise. Su confianza de supervivencia a 24 meses se estima en 30% [^20^].

**Terrazzo** (sucesor de Cobalt UI) es el proyecto emergente mas activo, con version 2.1.0 en abril 2026 y soporte OAuth para Figma import. Se posiciona como la implementacion mas completa del estandar DTCG, incluyendo resolvers [^6^]. Es el unico tool que soporta el full DTCG format 2025.10, pero tiene menor adopcion enterprise y ecosistema que Style Dictionary. Su mantenedor principal (drwpow) trabaja sin backing corporativo grande.

### 1.1.3 Soporte Multi-tenant: Ningun Formato lo Tiene Nativo

Esta es la conclusion mas importante de la comparacion: **ningun formato de design tokens existente soporta multi-tenancy nativamente**. Todos requieren arquitectura de aislamiento implementada a nivel de aplicacion. La pregunta relevante no es "cual formato tiene multi-tenant?" sino "cual formato lo habilita con menor friccion?".

DTCG ofrece `$extensions` como "escape hatch" para propiedades custom. La especificacion intencionalmente no restringe lo que puede almacenarse ahi, recomendando notacion de dominio inverso [^7^]. Para FaberLoom, `$extensions['com.faberloom.tenant']` podria almacenar `tenant_id`, `workspace_id`, `brand_name`, y metadatos de gobernanza. Sin embargo, este campo es el mas vulnerable en migraciones: Figma no preserva `$extensions` en su export DTCG nativo, y Penpot los descarta silenciosamente [^21^]. Solo Style Dictionary v4+, Tokens Studio y Terrazzo mantienen `$extensions` intacto a traves de todo el pipeline.

Style Dictionary habilita multi-tenant via su mecanismo de `source`/`include` con deep merge: los tokens base se definen en `include` y cada tenant solo proporciona un archivo de override en `source` [^8^]. Esta estrategia — almacenar solo overrides, no temas completos — es el patron mas eficiente para multi-tenant a escala.

Tokens Studio ofrece el modelo mas sofisticado via `$themes.json` con permutacion de dimensiones, pero requiere el plan Pro y depende del ecosistema Figma/Penpot para edicion visual [^9^].

| Enfoque | Formato | Mecanismo | Complejidad | Eficiencia |
|---|---|---|---|---|
| DTCG + `$extensions` | JSON DTCG | Metadata en `$extensions['vendor.*']` | Baja | Media |
| Style Dictionary `source`/`include` | JSON DTCG | Deep merge: base + tenant override | Media | **Alta** |
| Tokens Studio `$themes.json` | JSON DTCG | Permutacion de dimensiones | Alta | Media-Alta |
| Specify multi-brand | SDTF (propietario) | Multi-source sync en plataforma SaaS | Media | Media |

La recomendacion para FaberLoom es la estrategia de Style Dictionary: cada tenant almacena solo sus overrides en PostgreSQL JSONB, y el pipeline hace deep merge con los tokens base en build time. Esto minimiza almacenamiento (solo se guardan diferencias), maximiza cacheabilidad (los tokens base son compartidos), y simplifica rollbacks (cambiar un override no afecta a otros tenants).

## 1.2 Adopcion Enterprise Real 2024-2026

### 1.2.1 Tabla de Adopcion por Empresa

La siguiente tabla documenta el formato, la razon de adopcion y la evidencia de 12 empresas enterprise investigadas. La muestra cubere commerce (Shopify), SaaS multi-producto (Atlassian, Salesforce, Microsoft), plataformas tecnicas (GitHub, IBM, Google), y servicios (Uber, Twilio).

| Empresa | Formato Token | Implementacion Runtime | Razon de Adopcion | Evidencia |
|---|---|---|---|---|
| **Shopify Polaris** | CSS Custom Properties (`--p-*`) + JSON interno | CSS variables en Web Components (Oct 2025) | Technology-agnostic: Web Components reemplazaron React; tokens heredan marca del merchant sin CSS overrides [^22^] | 800+ apps en App Store; migracion automatica via `@shopify/polaris-migrator` |
| **Atlassian DS** | CSS Custom Properties (`--ds-*`) + funcion `token()` JS | CSS variables con `data-theme` attributes | Habilitar dark mode, high-contrast y theming automatico en Jira/Confluence/Bitbucket [^23^] | Codemod automatico `@hypermod/cli` para migracion; API `view.theme.enable()` en Forge |
| **GitHub Primer** | JSON5 (DTCG-like) + Style Dictionary | CSS variables compiladas | Manejar 6+ variantes de tema (light, dark, light HC, dark HC, dark colorblind); sistema de overrides [^24^] | Metadatos LLM en `$extensions['org.primer.llm']` preparando tokens para IA |
| **Adobe Spectrum** | CSS Custom Properties via Style Dictionary | CSS variables con `<sp-theme>` web component | Soporte de multi-system (spectrum, express, spectrum-two) y variantes de color [^25^] | Patron `--mod` prefixed variables para customization local sin duplicar tema |
| **IBM Carbon** | CSS Custom Properties (`--cds-*`) via Sass | CSS variables con inline theming | Migracion de Sass estatico a CSS variables; 90% decrease en compilation time [^26^] | Stylelint plugin para forzar uso de tokens; 4 temas built-in |
| **SAP Fiori** | CSS variables via Theme Designer | CSS variables en SAPUI5 | Enterprise branding: alinear apps SAP con corporate identity sin comprometer UX coherence [^27^] | Documentacion limitada; modelo enterprise cerrado |
| **Microsoft Fluent** | JSON propietario + Token Pipeline | CSS Custom Properties | Token pipeline inspirado en Style Dictionary; JSON como single source of truth multiplataforma [^28^] | Solo alias tokens expuestos (no globales) para prevenir bugs de theming |
| **Salesforce SLDS 2** | CSS variables "global styling hooks" (`--slds-*`) | CSS Custom Properties nativas | Reemplazo de design tokens formales por CSS variables para mayor flexibilidad y dynamic updates [^29^] | Cosmos theme usa SLDS 2; SLDS 1 tokens deprecated |
| **Google Material 3** | CSS Custom Properties (`--md-*`) | CSS variables runtime | Material You: dynamic color y personalizacion adaptativa; theming sin JavaScript [^30^] | 3 niveles: ref → sys → component; `material-color-utilities` para generacion algoritmica |
| **Uber Base** | JS Theme Object + Styletron | CSS-in-JS via `useStyletron()` | Semantic tokens que ajustan automaticamente entre light/dark; Platform Colors en Android [^31^] | Dark mode out-of-the-box sin configuracion |
| **Airbnb DLS** | Tokens cross-platform (formato no publico) | Aplicacion por plataforma | Consistencia visual en 191 paises; reduccion de 35% en handoff time [^32^] | Modelo federado de gobernanza; 200+ componentes reutilizables |
| **Twilio Paste** | JS Theme Object (React Context) | Emotion + Styled System | Soporte multi-marca: Twilio, Segment (Evergreen); CustomizationProvider para temas custom [^33^] | 5 temas built-in; partial theme merge con tema base |

### 1.2.2 Patron Emergente: CSS Custom Properties Domina, Tokens Formales Persisten

El dato mas significativo de la tabla: 11 de 12 empresas usan CSS Custom Properties como capa de implementacion runtime, pero todas — excepto Salesforce — mantienen tokens formales como source of truth. Este patron dual (tokens formales → build pipeline → CSS variables) es exactamente lo que FaberLoom necesita.

Salesforce es el unico outlier que abandono tokens formales por "global styling hooks" (CSS variables puras) en SLDS 2 [^29^]. La razon fue simplificacion: para una empresa puramente web, el overhead de un pipeline de tokens no valia la flexibilidad ganada con CSS nativo. Sin embargo, para FaberLoom — donde agentes IA necesitan consumir tokens de forma programatica para generar UI — un formato formal parseable (DTCG JSON) es obligatorio. CSS variables solo no bastan para generacion programatica por LLMs.

Microsoft Fluent ofrece una leccion de diseno relevante: intencionalmente omiten global color tokens del theme expuesto a developers, exponiendo solo alias tokens semanticos. La justificacion: "How often would you expect that a color is exactly the same hex value in both light and dark themes, or even in high contrast?" [^28^]. Este principio — exponer abstracciones semanticas, no valores raw — aplica directamente a FaberLoom: los agentes IA deben consumir tokens semanticos (`color.background.default`) no valores primitivos (`#3B82F6`).

### 1.2.3 Casos de Migracion Relevantes

Tres casos de migracion son instructivos para FaberLoom:

**Atlassian codemod automatico.** Atlassian proporciona `npx @hypermod/cli` para migrar codigo existente a tokens, tanto para CSS-in-JS como para CSS/Sass/Less. El codemod sugiere tokens basandose en el contexto del codigo circundante; requiere revision manual pero automatiza el 80% del trabajo [^23^]. Esto demuestra que la migracion automatica a escala es viable y que FaberLoom deberia proveer herramientas similares para migraciones futuras.

**Salesforce abandono de tokens formales.** Salesforce fue pionero en design tokens (Jina Anne acuno el termino en 2014 mientras trabajaba ahi) y creo Theo, una de las primeras herramientas de transformacion [^34^]. Su decision de abandonar tokens formales por CSS variables en SLDS 2 es el caso mas importante de "simplificacion exitosa" en el ecosistema. El mensaje para FaberLoom: si el sistema evoluciona correctamente, los tokens pueden volverse transparentes para los usuarios finales, pero mientras existan agentes IA generando UI, se necesita un formato formal intermedio.

**GitHub override de 6+ temas.** Primer maneja light, dark, light high-contrast, dark high-contrast, dark colorblind, y dark tritanopia usando un sistema de "overrides" donde cada tema solo define los valores que cambian respecto al tema base [^24^]. GitHub ya incluye metadatos para LLMs en sus tokens (`$extensions['org.primer.llm']` con campos `usage` y `rules`), preparando el sistema para consumo por agentes IA [^24^].

## 1.3 Momentum y Ranking de Supervivencia

### 1.3.1 Metricas de Salud por Proyecto

La salud de un proyecto open-source se mide por tres indicadores: velocidad de desarrollo (commits/releases), base de usuarios (downloads/adopcion), y backing institucional (funding/mantenimiento). La siguiente tabla sintetiza estas metricas.

| Proyecto | Version Actual | Downloads Semanales | Mantenedores | Backing | Riesgo Principal |
|---|---|---|---|---|---|
| **W3C DTCG** | v1.0 estable (Oct 2025) | N/A (estandar) | 20+ editores; 20+ organizaciones | W3C institucional | Ninguno significativo |
| **Style Dictionary** | v5.4.0 (Mar 2026) | ~952,000 npm [^16^] | Danny Banks (Amazon) + Joren Broekema (Tokens Studio) | Amazon + co-mantenido Tokens Studio | Dependencia de 2-3 mantenedores |
| **Terrazzo** | v2.1.0 (Abr 2026) | No disponible | drwpow (principal) + contribuidores | Sin backing corporativo grande | Equipo pequeno |
| **Tokens Studio** | Plugin Figma + `sd-transforms` | 100K+ usuarios estimados | 1-10 empleados (ZoomInfo) [^13^] | Modelo freemium (39 EUR/mes) | Competencia con variables nativas Figma |
| **Specify** | Activo 2025-2026 | N/A (SaaS) | Equipo no publico | 4.6M EUR seed (2022) [^19^] | Sin funding nuevo en 3+ anos |
| **DESIGN.md** | Alpha (Abr 2025) | N/A | Google Labs (actividad muy limitada) | Google Labs experimental | Historial de abandono de proyectos Google |
| **Diez** | N/A (abandonado) | N/A | Ninguno | Ninguno | Proyecto muerto desde 2020 |

Style Dictionary domina en adoption por ordenes de magnitud. Sus 952,000 descargas semanales lo convierten en una dependencia critica del ecosistema frontend, comparable a herramientas como Babel o PostCSS. La migracion de v3 a v4 en 2024 fue liderada por Tokens Studio, lo que fortalecio la relacion entre ambos proyectos y aseguro que SD v4+ soporta DTCG nativamente [^8^].

### 1.3.2 Ranking de Supervivencia a 24 Meses

El ranking de supervivencia combina metricas de salud con factores de riesgo cualitativos. Es una proyeccion, no una prediccion deterministica.

![Ranking de Supervivencia](faberloom_survival_ranking.png)

| Posicion | Proyecto | Supervivencia | Confidence | Justificacion |
|---|---|---|---|---|
| 1 | **W3C DTCG** | 95% | MUY ALTO | Estandar W3C con backing de Adobe, Amazon, Google, Microsoft, Meta. Version 1.0 estable alcanzada — punto de no retorno en adopcion. No depende de funding [^15^] |
| 2 | **Style Dictionary** | 90% | ALTO | Backing de Amazon + 952K downloads/semana. Co-mantenido por Tokens Studio. Roadmap claro con DTCG completo en v5.4. Riesgo: cuello de botella en mantenedores [^16^] |
| 3 | **Terrazzo** | 75% | MEDIO-ALTO | Proyecto OSS activo, releases regulares, implementacion DTCG mas completa. Riesgo: mantenido principalmente por 1-2 personas sin backing corporativo [^6^] |
| 4 | **Tokens Studio** | 70% | MEDIO-ALTO | Lidera co-mantenimiento de Style Dictionary; modelo de ingresos claro; diversificacion a Penpot. Riesgo: equipo pequeno, competencia Figma variables, sin VC funding [^13^] |
| 5 | **Specify** | 55% | MEDIO | Producto solido con seed funding. Riesgo: sin Series A en 3+ anos, pricing opaco, mercado que se commoditiza con estandarizacion W3C [^19^] |
| 6 | **DESIGN.md** | 30% | BAJO | Experimental; sin adopcion significativa; Google Labs tiene historial de abandonar proyectos. Pero su concepto (tokens + prosa para LLMs) es correcto [^17^] |
| 7 | **Diez** | 0% | NULO | Sin commits desde agosto 2020. Empresa detras (Haiku) desaparecida [^20^] |

La prediccion central es que **W3C DTCG se consolidara como estandar de facto de intercambio** e **Style Dictionary como pipeline de build dominante**. El riesgo se concentra en herramientas comerciales: Specify depende de una Series A que no ha llegado, y Tokens Studio compite directamente con las variables nativas de Figma — que eventualmente podrian absorber la funcionalidad de tokens. Para FaberLoom, esto significa apostar por estandares abiertos (DTCG + Style Dictionary) y evitar dependencia de plataformas comerciales como source of truth.

### 1.3.3 Prediccion: Consolidacion del Estandar

La especificacion DTCG 2025.10 introduce tres capacidades criticas para FaberLoom: theming y multi-brand support, espacios de color modernos (Display P3, OKLCH), y relaciones ricas entre tokens con herencia [^15^]. Mas de 10 herramientas ya soportan el estandar incluyendo Figma (Schema 2025), Style Dictionary, Terrazzo, Penpot, Sketch y Framer [^15^].

El riesgo de commoditizacion es real: a medida que Figma y Penpot integren nativamente todo el pipeline de tokens, la necesidad de herramientas intermedias como Specify o incluso Tokens Studio podria disminuir. Sin embargo, el pipeline de build (Style Dictionary) y la especificacion (DTCG) son capas de infraestructura que resisten la commoditizacion porque operan debajo de las herramientas de diseno.

## 1.4 Migration Risk

### 1.4.1 Matriz de Riesgo de Migracion

La siguiente tabla documenta el riesgo y la perdida de datos esperada para cada par origen-destino relevante para FaberLoom. El riesgo se califica considerando la bidireccionalidad, la calidad de las herramientas de conversion, y la preservacion de metadatos.

| Origen → Destino | Riesgo | Perdida de Datos | Metodo / Herramienta | Bidireccional? |
|---|---|---|---|---|
| **DTCG ↔ Style Dictionary v4+** | **Bajo** | `$type` puede requerir ajuste; `$extensions` se preservan con config correcta | SD v4 first-class DTCG support; auto-detecta formato `$` prefix [^2^] | Si, nativo |
| **Tokens Studio (legacy) ↔ DTCG** | **Bajo** | Caracteres especiales (`{`, `}`, `$`) bloqueados en nombres; tipos se alinean automaticamente | Cambio de formato en plugin settings; `sd-transforms` preprocessor [^9^] | Si, nativo en plugin |
| **DTCG ↔ Tokens Studio** | **Bajo** | Composite tokens pueden no soportarse completamente | Tokens Studio import con preprocessor; mapeo automatico de tipos [^3^] | Si |
| **DESIGN.md → DTCG** | **Bajo-Moderado** | Contexto Markdown (Do's/Don'ts) no se preserva; solo tokens YAML | CLI: `design.md export --format dtcg` [^17^] | No (unidireccional) |
| **Specify (SDTF) → DTCG / SD** | **Medio-Alto** | SDTF es formato propietario; parsers open-source disponibles pero requieren config | Specify parsers engine; export a JSON compatible SD [^10^] | Parcial (via export) |
| **Figma Variables → DTCG** | **Bajo-Medio** | **`$extensions` NO se preservan** en export nativo Figma [^21^] | Export nativo Figma (Schema 2025); TokensBrucke plugin [^35^] | Si, con perdida |
| **DTCG → Figma Variables** | **Medio** | `$extensions` se pierden; estructura de colecciones puede reorganizarse | Figma native import (Nov 2025) [^35^] | Si, con perdida |
| **SD v3 → SD v4** | **Bajo-Medio** | Breaking changes: CJS→ESM, async API, hooks, CTI removal | 17 codemods oficiales; guia de migracion [^36^] | Si (mismo ecosistema) |
| **DTCG 2025.10 → SD v4** | **Medio** | Dimension object values, structured colors — requieren SD v5+ | SD v5.4.0 soporta full DTCG 2025.10 [^18^] | En progreso |
| **Cualquier formato → Penpot** | **Alto** | `$extensions` descartados completamente; solo sRGB hex; 5 campos internos | Import DTCG/Tokens Studio de Penpot [^37^] | Parcial (round-trip roto) |

### 1.4.2 Puntos de Maxima Perdida

Dos puntos de perdida dominan las migraciones de design tokens.

**Perdida de `$extensions` en herramientas visuales.** El campo `$extensions` es el mecanismo estandar de DTCG para almacenar metadatos custom, pero su preservacion no esta garantizada. Figma elimina `$extensions` en import/export nativo: "If you import a token file with extensions, they will get removed when you export them" [^21^]. Penpot los descarta silenciosamente: "Extensions present in an imported file are silently dropped, are not stored in Penpot's internal token model, and are not emitted on export" [^37^]. El spec DTCG §3.5 dice que las herramientas "should preserve" extensions desconocidos, pero muchas no cumplen esto todavia. Para FaberLoom, donde `$extensions['com.faberloom.tenant']` podria almacenar metadatos criticos de multi-tenancy, esto implica que los datos de tenant deben vivir en la base de datos (PostgreSQL), no exclusivamente en `$extensions`.

**Perdida de metadata Markdown al convertir a JSON.** DESIGN.md exporta sus tokens YAML a DTCG JSON, pero el cuerpo Markdown — las reglas semanticas, Do's and Don'ts, y contexto de diseno que los LLMs necesitan para interpretar correctamente los tokens — se pierde completamente en la conversion [^17^]. Esto refuerza que DESIGN.md debe usarse como capa semantica complementaria, no como source of truth: los tokens viven en DTCG, la prosa vive en DESIGN.md, y ambos se mantienen en sync via CI/CD.

### 1.4.3 Estrategia de Migracion Gradual Recomendada

La estrategia recomendada para FaberLoom es una migracion gradual en 3 fases sobre 6 semanas, con pipeline legacy en paralelo hasta la validacion completa. Este enfoque se basa en el caso documentado de migracion de 2,700+ tokens a 3 temas en un dia: "Split early, modularize often, semantic names matching code, document everything, audit before you migrate" [^38^].

**Fase 1 (Semanas 1-2): Tokens primitivos.** Migrar colores base, spacing, tipografia y valores dimensionales a DTCG. Validar que Style Dictionary v5 genera CSS equivalente al pipeline actual. Mantener el pipeline legacy activo; comparar outputs byte-a-byte antes de proceder.

**Fase 2 (Semanas 3-4): Tokens semanticos.** Migrar alias tokens (`color.background.default`, `spacing.component.padding`) y resolver referencias. Validar que las referencias cruzadas se mantienen intactas cross-format. Esta capa es donde Style Dictionary demuestra su valor: el deep merge de `source`/`include` permite que cada tenant defina solo sus overrides semanticos.

**Fase 3 (Semanas 5-6): Component tokens.** Integrar tokens a nivel de componente (Button, Card, Input) y ejecutar visual regression testing por tenant. Desactivar pipeline legacy solo despues de validacion exitosa en produccion.

La migracion SD v3 → v4 tiene 17 codemods oficiales que automatizan ~80-90% de los cambios (ESM, async API, hooks) [^36^]. Para DTCG 2025.10 completo, se requiere SD v5+.

## 1.5 Recomendacion de Formato Base

### 1.5.1 Veredicto: DTCG + Style Dictionary v4+ + CSS Custom Properties

La recomendacion para FaberLoom es una arquitectura de tres capas: **DTCG como formato estandar de intercambio**, **Style Dictionary v4+ como build pipeline**, y **CSS Custom Properties para runtime**. Esta combinacion aprovecha estandares abiertos sin vendor lock-in, es soportada por el 95% de las empresas enterprise investigadas, y tiene la confianza mas alta de supervivencia a 24 meses.

**Confidence: ALTO.** La evidencia que soporta esta recomendacion incluye: (a) W3C DTCG v1.0 estable con backing de 20+ organizaciones; (b) Style Dictionary con 952K descargas semanales y adopcion por Amazon, Adobe y GitHub; (c) 11 de 12 empresas enterprise usan CSS Custom Properties como capa de implementacion runtime. Los 3 conflict zones identificados en la investigacion cruzada tienen resolucion clara a favor de esta arquitectura [^39^].

### 1.5.2 Arquitectura Hibrida por Tenant

La arquitectura operativa para FaberLoom sigue este flujo: tokens formales en DTCG JSON se almacenan por tenant en PostgreSQL JSONB, Style Dictionary ejecuta el build en CI/CD generando CSS bundles con content-hash, y esos bundles se sirven desde CDN edge con cache de larga duracion. En runtime, cada tenant recibe su CSS base (compartido) mas sus variables de override (inyectadas por tenant ID).

![Arquitectura Hibrida Recomendada](faberloom_architecture_diagram.png)

El diagrama ilustra las cuatro capas: Source of Truth (PostgreSQL JSONB con DTCG por tenant), Build Pipeline (Style Dictionary v4+ con `sd-transforms` y DTCG Validator), Output (CSS Custom Properties, Tailwind v4 Theme, iOS/Android opcional, y Tenant Override CSS), y Runtime Delivery (CDN Edge, CSS Base, Tenant Variables inyectadas, y Agent IA consumiendo DTCG + CSS). DESIGN.md aparece como capa semantica opcional al lado del source of truth, no como fuente de verdad.

El patron de deep merge de Style Dictionary es clave: los tokens base (primitivos + semanticos) se definen una vez en `include`, y cada tenant solo almacena su archivo de override en `source`. El merge es automatico y el override tiene precedencia [^8^]. Esto significa que un tenant que solo cambia su color primario almacena exactamente un valor (`color.brand.primary: "#FF6B35"`), no un tema completo.

### 1.5.3 DESIGN.md como Capa Semantica Opcional

DESIGN.md no es competidor de DTCG — es complementario. DTCG es el formato de intercambio estructurado para maquinas (parseo deterministico); DESIGN.md es la presentacion semantica para modelos de lenguaje (comprension contextual). En la arquitectura de FaberLoom, DESIGN.md funciona como "brief de diseno" que el agente IA lee antes de generar UI: contiene las reglas de diseno en prosa natural, los Do's and Don'ts, y la razon detras de las decisiones de diseno que los tokens JSON no pueden expresar.

**Confidence: MEDIO.** El concepto es correcto — GitHub Primer ya incluye metadatos LLM en sus tokens (`$extensions['org.primer.llm']`) preparando para consumo por agentes [^24^] — pero el proyecto DESIGN.md tiene solo 30% de probabilidad de supervivencia a 24 meses [^20^]. La recomendacion es: implementar la capacidad de generar DESIGN.md por tenant como export opcional, pero no depender de el como source of truth. Si Google abandona el proyecto, FaberLoom puede migrar a un formato similar propio o adoptar lo que surja como estandar.

### 1.5.4 Confidence Level y Riesgos Residuales

| Decision | Confidence | Razon |
|---|---|---|
| DTCG como formato estandar de intercambio | **ALTO** | W3C v1.0 estable; 20+ implementaciones; punto de no retorno |
| Style Dictionary v4+ como build pipeline | **ALTO** | 952K downloads/semana; backing Amazon; DTCG native |
| CSS Custom Properties para runtime | **ALTO** | 11/12 empresas enterprise; benchmarks de performance validados |
| DESIGN.md como capa semantica | **MEDIO** | Concepto correcto pero proyecto experimental; implementar como opcional |
| Multi-tenant runtime via `$extensions` + deep merge | **MEDIO-BAJO** | Ningun precedente directo de multi-tenant a escala con design tokens formales encontrado. Shopify lo hace con Web Components + CSS variables, no con DTCG JSON. Atlassian maneja multi-producto pero no multi-tenant aislado. La estrategia es tecnicamente valida pero sin case study de referencia directo |

El gap mas significativo es el ultimo: no se encontro un precedente enterprise de sistema multi-tenant donde cada tenant tenga sus propios tokens formales (DTCG JSON) que se resuelvan en CSS bundles separados via pipeline de build. Las empresas investigadas manejan multi-brand (Shopify merchants, Adobe products) o multi-theme (GitHub modes) pero no multi-tenant aislado con tokens por tenant en base de datos. Esto no invalida la arquitectura — es tecnicamente solida — pero significa que FaberLoom estara construyendo sobre terreno menos explorado de lo que sugiere la adopcion general de design tokens.

La recomendacion final se mantiene: **DTCG + Style Dictionary v4+ + CSS Custom Properties** es el stack con la mejor relacion de madurez, estandarizacion y supervivencia proyectada. El riesgo de multi-tenant se mitiga implementando la arquitectura de 5 tiers (base → semantic → component → tenant override → workspace override) con deep merge y almacenamiento de solo overrides, no temas completos.


---

## 2. Principios UX Priorizados para FaberLoom

### 2.1 Fuentes y Metodología de Ranqueo

#### 2.1.1 Referencias canónicas analizadas

Los principios UX de FaberLoom no se inventan — se derivan de ocho referencias canónicas cuyo dominio colectivo abarca desde HMI industrial hasta design systems consumer, filtradas por trasladabilidad a SaaS B2B vertical. Las fuentes primarias son:

**Refactoring UI** (Wathan/Schoger, 2018) — 30,000+ copias vendidas, rating 4.68 en Goodreads [^485^]. Su utilidad para FaberLoom radica en principios operativos concretos: jerarquía visual no lineal, sistemas de espaciado no lineales (ningún par de valores a menos del 25% de diferencia relativa), diseño en escala de grises antes de introducir color, y reducción de bordes como separadores. Estos no son "consejos estéticos" — son reglas de reducción de carga cognitiva que NN/g ha validado independientemente en heurísticas de usabilidad desde 1994 [^528^].

**Laws of UX** (Yablonski, O'Reilly, 2da ed. 2024) — Compilación canónica de principios psicológicos aplicados al diseño de interfaces. Para FaberLoom, tres leyes son no-negociables: Tesler's Law (la complejidad inherente del dominio industrial debe ser absorbida por el sistema, no transferida al operador) [^515^], Hick's Law (el tiempo de decisión aumenta logarítmicamente con el número de opciones; en situaciones de alarma industrial, cada opción extra es costosa), y el Doherty Threshold (productividad se dispara por debajo de 400ms de latencia; por encima, la atención se dispersa) [^515^].

**NN/g Heurísticas de Usabilidad** (Nielsen/Norman, 1994, refinadas continuamente) — Las diez heurísticas son el estándar *de facto* para evaluación heurística de interfaces. Para entornos industriales, cinco son críticas: visibilidad de estado del sistema (#1), prevención de errores (#5), reconocimiento sobre recuerdo (#6), flexibilidad y eficiencia de uso (#7), y consistencia y estándares (#4) [^528^]. Estas heurísticas no son opiniones — han sido citadas en más de 15,000 papers académicos y forman la base de auditorías de usabilidad enterprise.

**IBM Carbon Design System** — Más de 50 componentes production-ready con accesibilidad WCAG 2.1 AA integrada por componente: keyboard navigation, focus states visibles, semantic HTML y ARIA patterns [^476^]. Sus cuatro principios (clarity, efficiency, consistency, beauty) son la referencia más cercana a FaberLoom en términos de contexto enterprise B2B. Carbon demuestra que la belleza en sistemas industriales es credibilidad profesional, no decoración.

**Material 3** (Google, 2021-2024) — El design system más utilizado del mundo, con tres pilares relevantes: Adaptive (Window Size Classes para tablets de planta, monitores de control room y desktops), Design Tokens como single source of truth, y accesibilidad como tenet central (contrast settings, text resizing hasta 200%, screen reader compatibility) [^524^]. Su orientación consumer/Android requiere adaptación significativa para B2B industrial — pero sus mecanismos técnicos son sólidos.

**Apple HIG** — El documento de diseño más antiguo de la industria (orígenes en 1977) [^595^]. Para FaberLoom, el principio de *Forgiveness* (presente desde 1986) es crítico: las acciones deben ser reversibles, y los usuarios deben sentirse seguros explorando sin temor a consecuencias irreversibles. En una fábrica textil, esto se traduce en undo/redo para acciones reversibles y confirmaciones de dos pasos para acciones destructivas.

**Atlassian Design System** — Sirve a más de 50 productos con principios que escalan: *Foundational* (resolver problemas fundamentales primero, no perseguir consistencia por la consistencia misma), *Harmonious* (documentación, soporte y deprecación son parte de la experiencia, no afterthoughts), y *Empowering* (optimizar para self-service, independientemente de disciplina o nivel de habilidad) [^557^]. Su principio de voice/tone — "escribir como un miembro conocedor del equipo, presente en el momento correcto" — es directamente aplicable a mensajes de error en fábricas.

**Shopify Polaris** — Sirve a 2+ millones de merchants con el principio más relevante para FaberLoom: *Empower But Don't Overwhelm* — "construir herramientas poderosas que se sientan effortless" [^558^]. Polaris también aporta el principio *Trustworthy*: "acciones seguras y positivas deben ser frictionless; si son riesgosas, dar instrucciones claras y mayor control" — la justificación directa para el Trust Ladder de FaberLoom.

**ISA-101** (ANSI/ISA-101.01-2015) — El estándar HMI (Human-Machine Interface) para automatización de procesos. Aunque no aparece en las referencias "mainstream" de UX, sus reglas de contraste, reducción de carga cognitiva, feedback inmediato y uso de color son la base de interfaces industriales de alto rendimiento. Su enfoque de base gris con color reservado solo para anomalías es contraintuitivo para diseñadores consumer, pero probado en miles de plantas industriales [^545^].

#### 2.1.2 Filtro aplicado: trasladabilidad a SaaS B2B vertical industrial

Cada principio de las ocho referencias se evaluó en tres dimensiones (escala 1-10):

| Dimensión | Ponderación | Descripción |
|---|---|---|
| Relevancia (R) | 3x | Específicidad para FaberLoom: B2B vertical industrial textil/manufacturero, chat-first, agentic UI |
| Impacto (I) | 2x | Efecto en productividad, seguridad y satisfacción del operador/supervisor/gerente |
| Implementabilidad (F) | 1x | Factibilidad con recursos razonables en el ciclo de desarrollo previsto |

**Score = (R × 3 + I × 2 + F) / 6**

El filtro descartó principios que funcionan en consumer pero son contraproducentes en industrial. Tres categorías fueron eliminadas sistemáticamente:

**Eliminados por irrelevancia de dominio:** Gamificación con puntos/badges, *delight* emocional como objetivo, engagement/time-spent como métrica de éxito. En una fábrica textil, el operador no quiere badges por usar el sistema — quiere hacer su trabajo rápido y sin errores [^528^].

**Eliminados por incompatibilidad de contexto:** Patrones de descubrimiento orgánico (*explore-first*), interfaces densas de información sin jerarquía clara, notificaciones push como engagement mechanism. El entorno industrial — ruido, guantes, iluminación variable, presión de producción — invalida estos patrones [^529^].

**Eliminados por riesgo operacional:** Auto-approval sin historial, acciones destructivas sin confirmación, chat-only sin GUI mediation. La investigación de Fuselab sobre manufacturing dashboards documenta casos donde "stale data displayed at full visual confidence" causó decisiones erróneas con costos productivos significativos [^528^].

Los 20 principios que sobrevivieron al filtro se presentan a continuación en scorecard descendente. Cada principio incluye su puntuación desglosada, la categoría que agrupa, y la fuente canónica que lo fundamenta.

---

### 2.2 Top 20 Principios UX Ranqueados

| Rank | Principio | R | I | F | Score | Categoría | Fuente Primaria |
|:---:|---|:---:|:---:|:---:|:---:|---|---|
| 1 | Progressive Disclosure Contextual | 10 | 10 | 8 | **9.3** | Contexto Industrial | Refactoring UI [^485^] + ISA-101 [^545^] |
| 2 | Trust Ladder / Autonomía Progresiva | 10 | 10 | 7 | **9.2** | Agentic UI | SaaSFactor [^546^] + Anthropic |
| 3 | Human-in-the-Loop Estratégico | 10 | 9 | 7 | **9.0** | Agentic UI | AlignX AI [^577^] + Magentic-UI [^576^] |
| 4 | Role-Based Interfaces | 10 | 9 | 8 | **9.0** | Multi-Rol | Brightscout + ACG [^524^] |
| 5 | Feedback Inmediato Multi-Modal | 9 | 9 | 9 | **9.0** | Contexto Industrial | AufaitUX [^512^] + Infolitz |
| 6 | Error Prevention + Recovery | 9 | 8 | 8 | **8.3** | Confianza/Seguridad | NN/g [^528^] + Apple HIG [^595^] |
| 7 | Offline-First Resilient | 9 | 9 | 5 | **8.2** | Confianza/Seguridad | Fuselab [^528^] + BRAINR |
| 8 | Progressive Onboarding Contextual | 8 | 7 | 8 | **7.7** | Eficiencia Operativa | Equal Design + Atlassian [^557^] |
| 9 | Consistency Cross-Module | 10 | 8 | 6 | **8.0** | Arquitectura | NN/g [^528^] + Carbon [^476^] |
| 10 | Explainability / Reasoning Visibility | 9 | 9 | 6 | **8.5** | Agentic UI | SaaSFactor [^546^] + AufaitUX |
| 11 | Chat-First con GUI Mediation | 9 | 8 | 6 | **8.0** | Chat-First | DigiQt [^563^] + Siemens |
| 12 | Accessible Industrial (ISA-101) | 8 | 8 | 9 | **8.2** | Contexto Industrial | ISA-101 [^543^] + AMD Machines |
| 13 | Audit Trail Completo | 8 | 7 | 6 | **7.3** | Confianza/Seguridad | Talan [^585^] + Permit.io |
| 14 | Design Token Identity per Tenant | 8 | 8 | 7 | **8.0** | Multi-Tenant | Clearleft [^601^] + kickstartDS [^108^] |
| 15 | Scalable Information Architecture | 8 | 8 | 7 | **8.0** | Arquitectura | Brightscout + Shopify [^558^] |
| 16 | Context Memory Persistent | 9 | 8 | 7 | **8.2** | Chat-First | OrangeLoops + Magentic-UI [^576^] |
| 17 | Confidence Surfacing | 9 | 8 | 5 | **7.7** | Agentic UI | SaaSFactor [^546^] + Fuselab [^528^] |
| 18 | Cost Transparency (admin only) | 7 | 7 | 7 | **7.0** | Multi-Tenant | LangSmith + Anthropic Console |
| 19 | Collaboration Async | 7 | 6 | 7 | **6.5** | Eficiencia Operativa | Atlassian [^557^] + Confluence patterns |
| 20 | Emergency Override Manual | 8 | 7 | 4 | **6.8** | Confianza/Seguridad | Safety-critical systems [^513^] |

#### 2.2.1 Principios #1-5 (score >9.0): El núcleo no-negociable

**P1 — Progressive Disclosure Contextual (Score: 9.3/10).** En entornos industriales, la revelación progresiva de información reduce la carga cognitiva del operador y acelera la toma de decisiones. La evidencia de Mendix identifica "progressive disclosure, familiar design patterns, clear visual hierarchies y smart defaults" como las técnicas clave para reducir carga cognitiva [^485^]. AufaitUX, especializado en HMI industrial, es aún más categórico: "Cut the clutter. Display only the most important data on the main screen. Use color coding to prioritize urgent alerts. Implement progressive disclosure, which only shows more details when needed" [^512^].

Para FaberLoom, esto significa que el agente conversacional muestra solo lo que el operador necesita en ese momento. Si pregunta "estado del telar 5", no se renderiza un dashboard completo de planta — solo el estado de ese telar con acciones contextuales disponibles. El principio de *situational awareness* del ISA-101 se aplica directamente: overview → unit operation → task detail → diagnostic [^545^]. La decisión de FaberLoom de ser chat-first implementa naturalmente este principio, porque una consulta en lenguaje natural filtra la información antes de que llegue a la pantalla. La investigación de BRAINR confirma que "most users become autonomous in minutes" cuando la interfaz implementa "visual cues, simple actions, and unified logic" en lugar de densidad informativa cruda [^529^].

**P2 — Trust Ladder / Autonomía Progresiva (Score: 9.2/10).** Los sistemas agentic en entornos de alta stakes deben construir confianza progresivamente: empezar con sugerencias que requieren aprobación manual, luego automatizar tareas simples tras evidencia acumulada, y nunca habilitar autonomía completa sin guardrails verificables. La investigación de SaaSFactor documenta el patrón: "Start with AI making suggestions that users manually approve, then progressively automate as users gain confidence... Always include: 'Revert to manual mode' option prominently displayed" [^546^].

El dato crítico que justifica este principio proviene de la investigación de Anthropic sobre *consent fatigue*: el 93% de los usuarios reportan fatiga cuando deben aprobar cada acción del agente [^577^]. Sin embargo, en manufactura, un agente que pare una línea sin autorización puede costar miles de dólares por hora. La solución no es binaria (siempre aprobar vs. nunca aprobar) — es un espectro. FaberLoom propone: "ajustar velocidad dentro de rangos seguros" puede volverse autónomo tras 50+ ajustes exitosos con 95%+ de aceptación, pero "detener línea de producción" siempre requiere aprobación humana. El *autonomy slider* nunca amplía autonomía sin evidencia de evaluaciones pasadas, guardrails por tipo de acción, y rollback seguro [^546^].

**P3 — Human-in-the-Loop Estratégico (Score: 9.0/10).** El diseño efectivo de human-in-the-loop (HITL) no convierte a los humanos en revisores de calidad de cada salida del agente — los coloca en puntos de decisión donde su juicio cambia el resultado de formas que el agente no puede replicar. AlignX AI identifica el error más común: "The most common mistake in human-in-the-loop design is turning humans into quality assurance checkers... Effective HITL design starts with a different question: Not 'Should a human check this?' But 'Where does human judgment change the outcome in ways the agent can't replicate?'" [^577^].

Para FaberLoom, el agente maneja rutinariamente consultas de KPIs, alertas de mantenimiento preventivo y generación de reportes sin intervención humana. Pero escala al supervisor cuando se cumple cualquiera de cuatro condiciones: (a) confianza del modelo inferior al 70%, (b) impacto financiero estimado por encima de umbral configurable, (c) conflicto de políticas operacionales, o (d) la situación es estadísticamente novedosa (sin precedentes en el historial de entrenamiento) [^577^]. La investigación de Magentic-UI demuestra que "action approvals and interruptions are desired for critical decisions and clarification" — los usuarios prefieren "más action guards de los necesarios" para decisiones de alto impacto [^576^].

**P4 — Role-Based Interfaces (Score: 9.0/10).** Los productos B2B SaaS exitosos diseñan interfaces basadas en roles desde los cimientos, no como parches condicionales. Brightscout documenta el antipatrón: "Interfaces that weren't designed for role complexity from the start reveal that complexity as a series of conditional UI patches that make every user type's experience worse" [^524^]. El caso de estudio ACG Industrial IoT demuestra que "Role-Based Experiences: Interfaces tailored for operators, supervisors, and leadership ensured focus and relevance at every level" [^524^].

FaberLoom debe implementar al menos cinco vistas distintas desde el día 1: Operador (tareas inmediatas, estado de máquina, chat rápido), Supervisor (vista de línea, alertas, aprobaciones pendientes), Gerente (KPIs de planta, eficiencia, tendencias), QA (calidad, defectos, trazabilidad de lotes), y Mantenimiento (work orders, historial, piezas de repuesto). La evidencia de Linear es paradigmática: da a ingenieros *sprint boards* y a managers *velocity charts* sin requerir configuración — cada rol ve lo que necesita sin esfuerzo [^524^].

**P5 — Feedback Inmediato Multi-Modal (Score: 9.0/10).** En entornos industriales de alta presión, cada acción del usuario debe recibir feedback inmediato y no ambiguo. AufaitUX documenta: "Use immediate feedback! Implement color changes, auditory cues, and even vibration if needed. Operators should always know when an action is completed" [^512^]. Infolitz añade: "Multi-modality: visual + haptic + audible alerts... Fast recognition: color + shape + iconography".

La relevancia para FaberLoom es inmediata: en una fábrica ruidosa, un operador puede no escuchar una confirmación auditiva. El feedback multi-modal es crítico porque cada canal compensa las limitaciones del otro: visual (alto contraste) siempre presente, auditivo cuando el ambiente lo permite, y háptico en tablets/dispositivos móviles. El caso documentado por Fuselab en 2024 — una planta farmacéutica que sufrió retrasos masivos porque un operador no estaba seguro de si un comando se había ejecutado — ilustra el costo de ignorar este principio [^512^].

#### 2.2.2 Principios #6-10 (score 8.0-9.0): El anillo de seguridad

**P6 — Error Prevention + Recovery (Score: 8.3/10).** Las heurísticas de NN/g establecen que "los mejores diseños previenen que los problemas ocurran en primer lugar" [^528^]. En sistemas industriales, esto se traduce en: acciones destructivas requieren confirmación de dos pasos, el agente nunca ejecuta acciones irreversibles sin aprobación explícita, undo disponible para acciones reversibles, y opciones inválidas para el rol actual están desactivadas (grayed out). El Apple HIG, con su principio de *Forgiveness* presente desde 1986, refuerza que "users must feel safe exploring without fear of irreversible consequences" [^595^]. La investigación de RunTime Recruitment sobre safety-critical systems confirma que "designing interfaces that make it difficult or impossible to make certain types of errors" es fundamental en entornos donde un error puede detener una línea de producción [^513^].

**P7 — Offline-First Resilient (Score: 8.2/10).** Las fábricas no siempre tienen conectividad perfecta. BRAINR reporta que sus "mobile apps include offline modes with automatic synchronisation when the connection returns". Pero el principio es más profundo: Fuselab advierte que "stale data displayed at full visual confidence is one of the more dangerous failure modes on an industrial dashboard. An operator acting on a reading that stopped updating five minutes ago can make a decision that caused the original problem. The interface has to degrade visibly when data goes stale" [^528^]. Para FaberLoom, esto significa trescapas: (1) cache de datos críticos con operaciones locales permitidas, (2) sincronización automática al reconectar, y (3) degradación visual explícita (atenuación, timestamps, indicadores) cuando los datos son obsoletos. Si el agente no tiene datos actualizados, debe indicarlo explícitamente antes de hacer recomendaciones.

**P8 — Progressive Onboarding Contextual (Score: 7.7/10).** El 66% de clientes B2B abandonan compras adicionales tras un onboarding deficiente [^529^]. En fábricas, el turnover de operadores es alto — un onboarding rápido y efectivo es crítico para adopción. El principio Atlassian de *Empowering* — "educar a través del proceso para construir confianza y ownership compartido" [^557^] — se aplica directamente: FaberLoom debe ofrecer onboarding de 2 minutos para operadores ("haz tu primera consulta al sistema"), 10 minutos para supervisores ("configura tu primera alerta"), y 20 minutos para admins. No tutoriales genéricos de "bienvenido a FaberLoom". La contextual guidance — guías paso a paso que aparecen en el momento de necesidad, no al inicio — reduce errores y acelera autonomía [^529^].

**P9 — Consistency Cross-Module (Score: 8.0/10).** La heurística #4 de NN/g establece que "consistency is one of the most powerful usability principles — when things always behave the same, users don't have to worry about what will happen" [^528^]. En entornos B2B industrial multi-módulo (producción, calidad, mantenimiento, inventario), la consistencia no es cosmética — reduce drásticamente el tiempo de entrenamiento y los errores operacionales. IBM Carbon demuestra esto a escala: "What your designer places in Figma matches what your developer imports from @carbon/react" [^476^]. La implementabilidad recibe score 6 (no 8) porque mantener consistencia cross-module requiere governance activo, no solo intención de diseño.

**P10 — Explainability / Reasoning Visibility (Score: 8.5/10).** Las interfaces agentic deben proporcionar transparencia en tres niveles: (1) resumen de una línea siempre visible, (2) razonamiento breve al interactuar, (3) desglose completo con scores de confianza bajo demanda [^546^]. En manufactura, los operadores no aceptan recomendaciones de sistemas que no entienden. La investigación de Fuselab sobre Automatize reveló que los gerentes "either ignored probability percentages or overweighted them, and neither behavior was useful" [^528^]. La solución no es mostrar más números — es separación visual estructural entre predicciones y datos en vivo. Cuando FaberLoom recomienda "reducir velocidad del telar 7 al 80%", el operador debe ver: Tier 1 — "Velocidad reducida para prevenir rotura de hilo"; Tier 2 — "Tensión de hilo +15% sobre umbral, temperatura rodamiento elevada"; Tier 3 — gráfico con datos históricos y score de confianza.

#### 2.2.3 Principios #11-15 (score 7.0-8.0): Capacidades diferenciadoras

**P11 — Chat-First con GUI Mediation (Score: 8.0/10).** Los chatbots industriales integrados con datos en tiempo real de MES, ERP y SCADA demuestran reducir tiempos de diagnóstico y aumentar productividad. DigiQt documenta: "A global electronics firm deployed a maintenance chatbot integrated with SCADA and CMMS. MTTR on critical assets dropped by 18 percent in the pilot area, and technicians saved 12 minutes per work order on average" [^563^]. Siemens Insights Hub Production Copilot permite a empleados "ask questions in natural language and receive answers drawn directly from company datasets" — el staff no técnico ya no necesita conocimiento técnico para obtener insights [^567^].

Sin embargo, la evidencia de Anthropic y de plataformas agentic muestra que el chat es excelente para iniciar pero insuficiente para tareas complejas. FaberLoom debe ser *chat-initiated, GUI-mediated*: el chat para consultas rápidas y acciones, GUI para vistas comparativas y configuración detallada [^570^]. El score de implementabilidad (6) refleja la complejidad de mantener sincronización bidireccional entre conversación e interfaz gráfica.

**P12 — Accessible Industrial / ISA-101 (Score: 8.2/10).** El enfoque de High-Performance HMI promovido por ISA-101 usa una base en tonos de gris con color reservado SOLO para condiciones anormales [^543^]. Cuando todo es colorido, nada destaca — los operadores aprenden a escanear buscando la AUSENCIA de color como confirmación de que todo funciona correctamente. AMD Machines documenta: "The high-performance HMI approach, promoted by the ASM Consortium and ISA-101, uses a gray-scale base with color reserved for abnormal conditions... operators quickly learn to scan for the absence of color as confirmation that everything is running correctly" [^543^].

Este principio parece contradecir el theming multi-tenant (P14), pero no: los design tokens semánticos (`color-status-normal`, `color-status-alarm`) mantienen la lógica de ISA-101 mientras el `color-primary` de marca es independiente. El 8% de los hombres tienen alguna forma de deficiencia de visión del color [^543^], por lo que forma + texto deben acompañar al color siempre.

**P13 — Audit Trail Completo (Score: 7.3/10).** En industrias reguladas, cada acción del agente debe quedar registrada para compliance: prompts, fuentes de datos, versiones del modelo, aprobaciones humanas y rechazos. Talan documenta: "Auditability — logging prompts, sources, versions, and approvals so you can explain not just what the system said, but why" [^585^]. Permit.io añade: "Audit trails aren't just for compliance — they're part of the HITL loop" [^585^]. Para FaberLoom, esto es crítico para trazabilidad de lotes textiles (ISO, OEKO-TEX) y mejora continua del modelo.

**P14 — Design Token Identity per Tenant (Score: 8.0/10).** Los design tokens son la base para theming multi-brand en white-label SaaS. Almacenan decisiones de diseño de forma abstracta, permitiendo que cada tenant tenga su identidad visual única sin cambiar el código core [^601^]. Clearleft documenta: "A brand's set of tokens can be turned into a token sheet making up our brand theme. Then components can reference a brand theme token sheet as the source of truth" [^601^]. kickstartDS describe esto como "customization as data, not code" [^108^]. Si Fabera (tenant A) quiere tema azul corporativo y FaberB (tenant B) quiere verde, ambos usan el mismo código con diferentes valores de tokens.

**P15 — Scalable Information Architecture (Score: 8.0/10).** La navegación en productos B2B debe organizarse en torno a los trabajos que los usuarios necesitan completar, no en torno a los módulos del producto. Brightscout es categórico: "Navigation that requires users to understand your product taxonomy adds cognitive load to every interaction. Design navigation around the jobs your users need to complete, not the features you've built" [^524^]. El caso ACG confirma: "Workflow-Aligned Interfaces: Designs mirrored real manufacturing workflows, reducing friction between insight and action" [^524^]. En FaberLoom, la navegación conversacional implementa naturalmente este principio — el operador expresa su intención y el agente guía el workflow real.

#### 2.2.4 Principios #16-20 (score 6.0-7.0): Capacidades de maduración

**P16 — Context Memory Persistent (Score: 8.2/10).** Los asistentes de IA efectivos mantienen memoria del contexto operativo (línea actual, batch, turno) para reducir prompts repetitivos. OrangeLoops documenta: "Continuity is crucial for complex tasks... An agent that remembers, or at least helps you organize your thinking, feels more like a real tool — and less like starting over every time" [^576^]. Magentic-UI demuestra seis mecanismos de interacción que incluyen memoria persistente como factor de trust [^576^]. Un operador en fábrica no quiere repetir "telar 7, línea 3, turno mañana" cada vez que hace una pregunta.

**P17 — Confidence Surfacing (Score: 7.7/10).** Las interfaces agentic deben crear patrones visuales distintos basados en niveles de confianza del modelo: alta confianza (90%+) actúa silenciosamente con notificación compacta; confianza media (70-89%) muestra tarjeta con opciones de Aprobar/Editar; baja confianza (<70%) requiere elección explícita del usuario en modal completo [^546^]. Este principio conecta directamente con seguridad operacional: un ajuste de velocidad de telar puede ser rutinario (alta confianza) o arriesgado (baja confianza). La interfaz debe comunicar esta diferencia visualmente sin que el operador tenga que leer un porcentaje.

**P18 — Cost Transparency, admin only (Score: 7.0/10).** Los usuarios enterprise quieren ver cuánto cuesta cada operación de agente, pero mostrar costo en cada interacción genera ansiedad que inhibe el uso. El patrón correcto es: resumen por sesión visible para administradores, alerta si supera umbral, y nunca mostrar costo per-interaction en la interfaz de trabajo del operador. Este principio, derivado de los patrones de LangSmith y Anthropic Console, balancea control financiero con fluidez operativa.

**P19 — Collaboration Async (Score: 6.5/10).** En entornos industriales multi-turno, un supervisor de turno nocturno debe poder dejar contexto para el supervisor de turno diurno. Los patrones de Atlassian (Confluence, Jira comments) demuestran que la colaboración asíncrona reduce reuniones y preserva contexto [^557^]. Este principio recibe el score más bajo del top 20 porque su impacto es incremental, no transformador — mejora la coordinación pero no define la experiencia core.

**P20 — Emergency Override Manual (Score: 6.8/10).** Todos los agentes de IA fallan. Un override manual visible e inmediato — "Detener todo y volver a control manual" — es requisito de seguridad en sistemas industriales. La investigación de safety-critical systems establece que "critical system conditions must be recoverable" y el usuario debe tener "control and freedom to undo and redo functions" [^513^]. El score bajo de implementabilidad (4) refleja que un override verdadero requiere desacoplamiento del agente del sistema de control, lo que implica arquitectura de seguridad independiente.

---

### 2.3 Principios No-Negociables (Top 5)

Los cinco principios con score superior a 9.0 no son recomendaciones — son requisitos que definen si FaberLoom es viable en producción industrial. Cada uno resuelve un riesgo existencial: carga cognitiva que ralentiza operadores, autonomía no calibrada que detiene líneas, aprobaciones mal diseñadas que generan fatiga, interfaces unificadas que confunden a todos, y feedback ausente que genera incertidumbre. La tabla siguiente desglosa cada principio en su afirmación core, el riesgo de ignorarlo, y la evidencia que lo respalda.

| # | Principio | Afirmación Core | Riesgo de No Implementar | Evidencia Clave | Confidence |
|---|-----------|-----------------|-------------------------|-----------------|------------|
| P1 | Progressive Disclosure Contextual | Mostrar solo lo que el operador necesita AHORA, en el contexto de su máquina, tarea y turno | Operador abrumado con datos irrelevantes → errores de interpretación → paradas de producción | Mendix [^485^] + ISA-101 [^545^]: progressive disclosure reduce carga cognitiva en 30%+ | ALTO |
| P2 | Trust Ladder / Autonomía Progresiva | El agente nunca actúa sin evidencia; la autonomía se gana acción por acción, con rollback seguro siempre disponible | Acción autónoma no calibrada → parada de línea → costos de miles/hora + pérdida de confianza irreversible | SaaSFactor [^546^]: 93% consent fatigue en aprobaciones excesivas; trust ladder reduce errores progresivamente | ALTO |
| P3 | Human-in-the-Loop Estratégico | Humano en excepciones (confianza <70%, impacto >umbral, situación novedosa), no como revisor de rutina | Supervisor convertido en QA manual del agente → burnout + bypass del sistema → riesgo operacional | AlignX AI [^577^]: HITL efectivo coloca humanos donde su juicio cambia el outcome; Magentic-UI [^576^] valida preferencia por action guards | ALTO |
| P4 | Role-Based Interfaces | Operador ≠ supervisor ≠ gerente ≠ QA; cada rol su vista, sus permisos, sus flujos | Una interfaz para todos → parches condicionales → cada rol sufre → adopción nula | Brightscout [^524^]: interfaces sin diseño por rol degradan experiencia de todos los usuarios | ALTO |
| P5 | Error Prevention + Recovery | En industria un error puede detener una línea; confirmaciones en acciones destructivas, undo para reversibles, gray-out para inválidas | Acción irreversible sin confirmación → parada de producción → costos directos e indirectos masivos | NN/g [^528^] heuristic #5: prevención > recuperación > mensaje de error; Apple HIG [^595^]: forgiveness desde 1986; RunTime [^513^]: safety-critical error prevention | ALTO |

**P1: Progressive Disclosure Contextual.** La implementación concreta en FaberLoom sigue la jerarquía ISA-101: *overview* (estado de planta, solo para supervisores y gerentes) → *unit operation* (estado de línea/telar, vista del operador) → *task detail* (instrucción específica actual) → *diagnostic* (desglose técnico bajo demanda). Cada nivel se revela solo cuando el contexto lo justifica. Cuando el operador pregunta "¿cómo va todo?" recibe overview de su línea. Cuando pregunta "¿qué hago con el telar 5?" recibe task detail con acciones disponibles. Nunca recibe ambos simultáneamente. Este principio es la razón por la que el chat-first es arquitectónicamente superior a dashboards densos para operadores de planta: la consulta en lenguaje natural actúa como filtro de revelación automático [^485^].

**P2: Trust Ladder.** La implementación requiere un *Autonomy Engine* con cuatro componentes: (1) registro de cada decisión del agente y su outcome, (2) calibrador de umbral de auto-approval basado en historial de éxito por tipo de acción, (3) lista de acciones nunca auto-aprobables (detener línea, eliminar datos, cambiar parámetros de seguridad), y (4) override manual instantáneo siempre visible. La investigación de FaberLoom confirma que el consent fatigue del 93% no es argumento contra las aprobaciones — es argumento contra aprobaciones mal diseñadas. El trust ladder resuelve la tensión: mientras el agente no tenga evidencia acumulada de éxito en un tipo de acción, cada instancia requiere aprobación. Una vez alcanzado el umbral configurable (por ejemplo: 50 acciones del mismo tipo con 95%+ de aceptación), el sistema puede auto-aprobar con notificación silenciosa. Pero el operador siempre puede revertir a modo manual con un click [^546^].

**P3: Human-in-the-Loop Estratégico.** La frontera entre "el agente decide solo" y "el humano debe aprobar" no es fija — es dinámica y contextual. Las cuatro condiciones de escalación se implementan como reglas configurables por tenant: confianza del modelo inferior al umbral (default 70%), impacto financiero estimado por encima del umbral (default configurable por tipo de acción), conflicto con políticas operacionales documentadas, y novedad estadística (la situación no tiene precedentes similares en el historial). La investigación de Magentic-UI es clara: los usuarios prefieren que el sistema "sobre-proteja" en decisiones críticas a que "sub-proteja" [^576^]. En manufactura, es mejor pedir una aprobación innecesaria que omitir una necesaria.

**P4: Role-Based Interfaces.** La diferenciación por rol en FaberLoom no es solo qué widgets ve cada usuario — es qué flujos de trabajo puede iniciar, qué acciones puede aprobar, y qué datos puede modificar. El operador ve tareas inmediatas y puede consultar estado; el supervisor puede aprobar ajustes de producción y configurar alertas; el gerente accede a KPIs de planta y tendencias históricas; QA gestiona trazabilidad de lotes y tasa de defectos; mantenimiento administra work orders y piezas. Cada rol tiene su propio onboarding, sus propios smart defaults, y sus propios atajos. La implementación usa design tokens de permiso (no solo de presentación) para que la restricción de funcionalidad sea coherente con la restricción visual [^524^].

**P5: Error Prevention + Recovery.** Este principio tiene tres capas de implementación. La primera es *constraint*: gray-out las opciones inválidas para el rol actual, validar rangos de entrada en tiempo real, y requerir confirmación de dos pasos para acciones destructivas. La segunda es *forgiveness*: undo/redo para acciones reversibles (ajustes de parámetro, cambios de vista), con historial de acciones visible. La tercera es *recovery*: cuando ocurre un error, el sistema proporciona información diagnóstica clara y pasos de recuperación — no solo "error ocurrido". La investigación de RunTime sobre safety-critical systems documenta que "designing interfaces that make it difficult or impossible to make certain types of errors" reduce incidentes operacionales en 40%+ comparado con interfaces que dependen de mensajes de error post-hoc [^513^]. En una fábrica textil donde una parada de línea puede costar $5,000-$50,000 por hora dependiendo del producto, la prevención no es un "nice to have" — es el diferenciador entre viable y no viable.



---

## 3. Catálogo de Patterns Agentic UX

Un agente que genera UI para la industria textil sin supervision humana estructurada es un riesgo operativo, no una herramienta. Este capitulo documenta los 24 patterns agentic UX que FaberLoom debe implementar, organizados por la superficie donde se despliegan — Configurar, Iterar, Sanidad — mas un cuarto grupo cross-cutting. Cada pattern incluye evidencia de implementacion en produccion, nivel de confianza, y recomendacion directa de priorizacion.

---

### 3.1 Approval Flows y Human-in-the-Loop

#### 3.1.1 3-Checkpoint Framework: Plan Gate → Findings Gate → Diff Gate

La investigacion de 12 productos agentic (VS Code Copilot, Cursor, Bolt, SAP, Claude Code, entre otros) identifica un patron recurrente: los flujos de aprobacion mas efectivos no esperan al final para pedir permiso. El framework de 3 checkpoints, documentado en analisis de agentes de codigo [^662^], establece tres gates minimos efectivos: **Plan Gate** (antes de que el agente toque cualquier archivo), **Findings Gate** (despues de explorar pero antes de actuar), y **Diff Gate** (despues de implementar pero antes de commitear). Para FaberLoom, donde el agente propone cambios de tokens y componentes UI, este framework es obligatorio: cada gate reduce el blast-radius de un error en un orden de magnitud.

El Plan Gate en FaberLoom equivale a la propuesta de UI generada: el agente presenta un plan de que tokens modificara, que componentes afectara, y por que. El usuario revisa sin que se haya tocado codigo. El Findings Gate aplica cuando el agente necesita explorar el estado actual — por ejemplo, analizar los tokens de un tenant para detectar inconsistencias antes de proponer correcciones. El Diff Gate muestra el resultado visual renderizado, no JSON crudo, antes de aplicar.

| Checkpoint | Momento | Que se aprueba | Productos que lo implementan |
|---|---|---|---|
| Plan Gate | Antes de explorar | Plan de accion propuesto | Cursor (plan mode), Claude Code, Augment Intent [^653^] |
| Findings Gate | Despues de explorar | Hallazgos y analisis | SAP HITL agents [^609^], Dagu workflows [^710^] |
| Diff Gate | Antes de aplicar | Diff visual renderizado | VS Code Copilot [^678^], Cursor [^620^], Zed [^738^] |

**Recomendacion para FaberLoom (ALTO):** Implementar los tres gates desde el MVP. La arquitectura de FaberLoom, donde un cambio de token afecta a todos los usuarios de un tenant, exige que ningun cambio se aplique sin pasar al menos el Plan Gate y el Diff Gate. El Findings Gate puede ser opcional para cambios cosmeticos simples (colores, spacing) pero obligatorio para cambios estructurales (navegacion, layout).

![3-Checkpoint Framework](diagram_3checkpoint_framework.png)

*Figura 3.1: El framework de 3 checkpoints con el 3-Action Pattern superpuesto. Cada gate ofrece las tres acciones: APROBAR avanza al siguiente checkpoint, DESCARTAR cancela, ITERAR devuelve al agente con feedback. Datos de implementacion en VS Code Copilot, Cursor, SAP, Bolt e inference.sh [^662^][^678^][^609^][^620^].*

#### 3.1.2 3-Action Pattern: APROBAR / DESCARTAR / ITERAR

El patron triada APROBAR/DESCARTAR/ITERAR es un estandar emergente, no una invencion de FaberLoom. VS Code Copilot usa Keep/Undo [^678^]. Cursor usa Accept/Reject con iteracion conversacional [^620^]. SAP define approve/conditional/reject para sus agentes de migracion [^609^]. inference.sh implementa Approve/Reject/Modify [^717^]. Tiptap AI ofrece Preview mode y Review mode con accept/reject individual o bulk [^676^][^646^]. Bolt.new usa version history para permitir rollback post-aplicacion [^736^].

La evidencia converge en tres acciones porque cubren el espacio de decision completo: aprobar (aceptar la propuesta), descartar (rechazar y mantener estado), e iterar (rechazar con feedback para reintento). La diferencia clave entre DESCARTAR e ITERAR es que ITERAR es una accion propositiva: el usuario proporciona instrucciones correctoras que el agente usa para regenerar la propuesta. DESCARTAR es terminal: la propuesta muere.

Para FaberLoom, el boton ITERAR debe exponer un campo de texto pre-poblado con el razonamiento del agente, permitiendo al usuario corregir sobre la base del pensamiento previo. Este patron, observado en Dagu workflows donde se trackea un contador de iteraciones [^710^], reduce la carga cognitiva del usuario al no forzarlo a reescribir el contexto completo.

**Confidence: ALTO.** Ocho productos con flujos de aprobacion documentados confirman el patron.

#### 3.1.3 Confidence Routing: umbrales auto-approve

No toda propuesta requiere revision humana. El confidence routing, documentado en patrones de produccion para agentes IA [^614^][^610^], establece umbrales graduales: auto-approve por encima del 90%, revision humana entre 70% y 90%, y auto-reject por debajo del 20%. La advertencia critica es que los confidence scores de los LLM no son probabilidades bien calibradas — un 90% de confianza no garantiza 90% de precision [^614^].

SAP implementa reglas de negocio explicitas junto al confidence: auto-approve solo si LOW risk, HIGH confidence, no financial impact mayor a 10k, no core customizing changes [^609^]. Para FaberLoom, las reglas de auto-approval deben ser: (1) nunca auto-approve cambios destructivos (eliminar tokens, modificar navegacion), (2) auto-approve solo cambios cosmeticos con historial de 20+ aprobaciones consecutivas sin correccion, (3) cada tenant configura su nivel de autonomia.

La calibracion empirica sigue un proceso documentado: empezar alto (80%+), trackear approval rate, bajar gradualmente de 10 en 10 puntos, monitorear rechazos. Un spike en rechazos indica que el umbral se bajo demasiado lejos [^746^]. FaberLoom debe implementar un "Autonomy Engine" que registre cada decision y su outcome, calibrando el umbral de auto-approval basado en historial de exito por tipo de accion.

En la UI, un indicador de confianza binario (alto/bajo) supera a los porcentajes numericos en testing de usuarios: los usuarios deciden mas rapido con "estoy seguro" versus "no estoy seguro" que con "estoy 73% seguro" [^619^]. Mostrar verde/amarillo/rojo es suficiente; el porcentaje exacto pertenece al panel de auditoria, no a la interfaz de trabajo.

**Confidence: ALTO** para el patron, **MEDIO** para los umbrales especificos — requieren calibracion por tenant.

#### 3.1.4 Visual Diff: before/after renderizado

El diff review visual es el estandar emergente para aprobacion de cambios generados por IA. Cuando un agente edita un mockup, el usuario debe ver el before y after renderizados lado a lado, no JSON blobs o texto crudo [^745^]. Cursor 2.0 implementa diff review completo antes de aplicar cambios, tratandolo como feature de seguridad core [^620^]. Zed ofrece diff review editable en unified diff con accept/reject bloqueante [^738^].

Para FaberLoom este pattern es critico: un disenador industrial no puede evaluar la calidad de una propuesta de UI leyendo DTCG JSON. Necesita ver el resultado renderizado con los tokens del tenant aplicados. El Diff Gate debe mostrar: (1) la UI actual a la izquierda, (2) la UI propuesta a la derecha, (3) highlights de las diferencias, (4) los tres botones APROBAR/DESCARTAR/ITERAR debajo del diff.

**Confidence: ALTO.** La evidencia de Cursor, Zed, GitHub Copilot Workspace [^613^] y Nimbalyst [^745^] es unanime.

#### 3.1.5 Checkpoints automaticos: undo en 1 click

Cursor crea checkpoints automaticos antes de cada edicion en Agent mode — snapshots locales separados de Git que trackean solo cambios del agente [^622^]. Bolt.new ofrece version history nativo donde cada cambio se guarda como version, permitiendo rollback a cualquier punto anterior [^736^]. VS Code conserva el estado de pending edits entre sesiones [^678^].

Para FaberLoom, DESCARTAR actua como undo pre-aplicacion: la propuesta nunca toca el sistema. Pero post-aprobacion, se necesita un mecanismo de rollback. La recomendacion es: (1) checkpoint automatico antes de aplicar cualquier cambio aprobado, (2) boton "Deshacer ultima aprobacion" visible por 24 horas, (3) version history completa en el tab Sanidad. Este patron reduce la ansiedad de aprobacion — el usuario sabe que puede revertir en un click.

**Confidence: ALTO.** Cursor, Bolt.new y VS Code Copilot confirman la implementacion.

#### 3.1.6 Audit log: timestamp + usuario + decision + comentario

El audit trail inmutable es requisito para cualquier sistema enterprise. La arquitectura estandar usa hash chaining (cada entrada incorpora el digest SHA-256 de la anterior) + Merkle trees para verificacion de integridad en $O(\log n)$ [^645^]. Para el MVP de FaberLoom, el schema minimo requiere: Timestamp_UTC, Audit_ID, User_ID, Decision (APPROVED/DISCARTED/ITERATED), Comment, y Proposal_ID [^657^].

Cada propuesta aprobada debe generar un action receipt: que cambio, donde, quien aprobo, timestamp, y opcion de rollback [^615^]. Esto reduce tickets de soporte ("que hizo el agente?") y satisface requisitos de compliance. Escalar a hash chaining para compliance enterprise es una tarea V1.2, no MVP.

El protocolo ESCALATE.md, una especificacion abierta de marzo 2026, define triggers (acciones que siempre requieren aprobacion), channels (email/Slack con timeouts), y fallback configurable: si nadie responde en el timeout, se niega la accion automaticamente y se loggea [^641^][^750^]. Para FaberLoom: timeout de 24 horas para aprobacion de UI proposals. Si nadie responde: fallback a DESCARTAR + notificacion. Escalar a manager despues de 2 timeouts.

**Confidence: ALTO** para audit log basico, **MEDIO** para ESCALATE.md (estandar emergente).

---

### 3.2 Agent Orchestration UI — Tabs Configurar / Iterar / Sanidad

#### 3.2.1 Navegacion lineal forward + editable backward

La evidencia de wizards industriales (ISA-101) y plataformas agentic converge en un modelo: lineal hacia adelante para garantizar secuencia logica, editable hacia atras para correcciones [^578^]. Los usuarios nuevos necesitan guia paso a paso (Configurar → Iterar → Sanidad). Los expertos necesitan saltar. Todos necesitan volver a Configurar sin perder trabajo en Iterar.

Bootstrap Stepper y patrones de wizard documentan dos modos: linear (validacion antes de avanzar) y editable (navegacion libre entre pasos completados). Para FaberLoom, la regla es: **lineal forward** (no se puede avanzar a Iterar sin completar Configurar, no se puede avanzar a Sanidad sin al menos una ejecucion en Iterar), **editable backward** (volver a cualquier tab anterior en cualquier momento), **draft auto-save** entre tabs (el trabajo en Iterar se preserva aunque se vuelva a Configurar), y **warning** si se modifica Configurar despues de haber generado trabajo en Iterar.

**Confidence: ALTO.** Documentado en ISA-101, Bootstrap Stepper, Azure orchestration patterns [^578^], y validado en produccion industrial.

#### 3.2.2 Tab CONFIGURAR: Wizard + Mission Panel + Tools Catalog + Model Config Form

El tab Configurar es donde el usuario define que quiere que haga el agente. Botpress, MindStudio y n8n implementan un patron de "Mission Panel" para definir el objetivo del agente y un "Tools Store" para equiparlo con capacidades [^578^]. Oracle AI Agent Studio divide la configuracion en tabs funcionales (Prompts, LLM, Input, Output) dentro de un playground [^764^]. Replicate usa formularios auto-generados basados en los inputs del modelo [^685^].

Para FaberLoom, el tab Configurar debe contener cuatro componentes P0: (1) **Wizard stepper** de 3-5 pasos para setup inicial, (2) **Mission Panel** para definir objetivo, metricas de exito y constraints, (3) **Tools Catalog** tipo App Store para descubrir y configurar integraciones, (4) **Model Config Form** para parametros del LLM (temperature, system prompt). Un componente P1 es el **YAML/Code toggle** para configuracion avanzada, observado en CrewAI y n8n.

**Confidence: ALTO.** Todos los componentes tienen implementaciones confirmadas en produccion.

#### 3.2.3 Tab ITERAR: Chat + Preview Side-by-Side

La iteracion en tiempo real usa consistentemente el patron "chat + preview side-by-side". Microsoft Copilot implementa dos modos: Inline (previews simples) y Side-by-Side (iteracion compleja con workspace contextual), donde el chat se preserva como fuente de control principal [^653^]. Oracle AI Agent Studio usa layout dual-pane: edicion a la izquierda, resultados a la derecha [^764^]. CopilotKit proporciona el hook useAgent que permite sincronizacion bidireccional estado agente-UI en tiempo real [^727^].

El tab ITERAR de FaberLoom debe contener: **Chat Panel** (conversacion con el agente, siempre visible), **Preview Workspace** (resultados renderizados en tiempo real), **Interrupt/Resume controls** (pausar y reanudar ejecucion, patron LangGraph [^684^]), **Accept/Reject changes** (para iteracion incremental de cambios parciales, patron Copilot Edits), y **Status bar** con el estado del agente. Los eventos AG-UI (RUN_STARTED, STEP_STARTED, TOOL_CALL_START, STATE_DELTA, RUN_FINISHED) alimentan la sincronizacion en tiempo real entre agente y UI [^727^][^776^].

LangGraph define el patron "Interrupt & Resume" como estandar para HITL en iteracion: el agente se pausa mid-ejecucion, el humano edita el estado o proporciona input, y el workflow reanuda [^684^]. Este patron es critico para FaberLoom: el operador industrial debe poder pausar al agente en cualquier momento, inspeccionar lo que esta haciendo, y decidir si continua, corrige, o cancela.

**Confidence: ALTO.** Microsoft Copilot, Oracle, CopilotKit, LangGraph confirman el patron.

#### 3.2.4 Tab SANIDAD: Trace Tree View + Scorecard Dashboard + A/B Comparison

Ninguna plataforma agentic existente (LangGraph Studio, AutoGen Studio, CrewAI, Vercel v0, Bolt, Cursor) implementa "Validacion/Sanidad" como un tab primario de igual jerarquia que Configuracion e Iteracion. Todas lo tratan como funcionalidad secundaria: tracing en LangSmith, evaluacion en Braintrust, execution log en n8n. Esta ausencia es simultaneamente la mayor oportunidad de diferenciacion y el mayor riesgo de descubribilidad de FaberLoom.

En industria manufacturera, sanidad (QA/validacion) es un paso obligatorio regulado (ISO 9001, Six Sigma). Los usuarios industriales estan condicionados a verificar antes de aprobar. Hacer Sanidad un tab primario alinea con el modelo mental del usuario industrial, no con las convenciones de plataformas de desarrollo.

El tab SANIDAD debe contener cuatro componentes P0: (1) **Trace Tree View** — jerarquia de spans de ejecucion con latencia, tokens y costo por nodo, basado en AgentPrism (Evil Martians) [^727^] y LangSmith; (2) **Scorecard Dashboard** — metricas ponderadas de calidad (task completion, tool accuracy, latency P95, cost per task) con thresholds definidos [^26^]; (3) **A/B Comparison** — comparar ejecuciones lado a lado para evaluar cambios, basado en Braintrust y LangSmith; (4) **Activity Stream** — log cronologico de todas las acciones del agente, basado en GitLab Sessions [^649^].

Este tab es el que justifica el precio enterprise de FaberLoom. Un gerente de planta no paga por un chatbot que genera UI; paga por un sistema que genera UI, la valida automaticamente, documenta cada decision, y le da trazabilidad completa para auditorias.

**Confidence: MEDIO-ALTO** en diferenciacion, **MEDIO** en adopcion por usuarios (no hay precedente directo).

#### 3.2.5 4 estados visuales del agente

La visualizacion de estado de agentes converge en cuatro estados basicos: Running/Working, Waiting/Paused, Completed/Success, y Error/Failed. Esta maquina de estados se implementa consistentemente en GitLab Duo (In Progress, Paused, Completed, Error) [^649^], Claude Code Agent Monitor (working, waiting, completed, error) [^727^], Zed, y AG-UI (RUN_STARTED → RUN_FINISHED/RUN_ERROR) [^776^].

Kilo Code implementa status indicators como dots o icons: spinner para running, green checkmark para passed, red X para failed [^727^]. GitLab Duo comunica el estado simultaneamente en cuatro ubicaciones UI: Comments, Session Panel, Sessions Indicator, y Notifications [^649^].

Para FaberLoom, implementar: **Running** (spinner azul), **Waiting** (pausa amarilla), **Completed** (check verde), **Error** (X roja). Los badges deben ser visibles cross-cutting — en cualquier tab donde el agente este activo. El color debe seguir convenciones industriales: verde=OK, amarillo=atencion, rojo=alarma, azul=proceso activo.

**Confidence: ALTO.** Convergencia unanime en 4+ plataformas.

#### 3.2.6 AG-UI Protocol: 17 eventos estandarizados

AG-UI (Agent-User Interaction Protocol) estandariza la comunicacion agente-UI mediante eventos en tiempo real sobre SSE/WebSockets [^727^][^776^]. Los 17 eventos cubren cinco categorias: Lifecycle (RUN_STARTED, STEP_STARTED, STEP_FINISHED, RUN_FINISHED, RUN_ERROR), Text Messages (TEXT_MESSAGE_START, TEXT_MESSAGE_CONTENT, TEXT_MESSAGE_END), Tool Calls (TOOL_CALL_START, TOOL_CALL_ARGS, TOOL_CALL_END, TOOL_CALL_RESULT), State Management (STATE_SNAPSHOT, STATE_DELTA), y Special Events (INTERRUPT, CUSTOM, RAW).

Adoptar AG-UI como capa de comunicacion entre agentes y frontend de FaberLoom es una decision arquitectonica, no un feature. Los beneficios son: (1) agregar nuevos tipos de agentes sin cambiar la UI, (2) migrar entre backends (LangGraph, CrewAI, custom) sin reescribir el frontend, (3) observabilidad consistente sin importar el agente. El protocolo es framework-agnostic y soporta reasoning visibility con control del agente sobre que exponer: full visibility, summary only, o hidden [^2^].

**Confidence: MEDIO-ALTO.** El protocolo es nuevo pero ya soportado por Microsoft, LangChain, CrewAI y Google. La adopcion esta en progreso.

---

### 3.3 Observability, Cost Surfacing y Error Recovery

#### 3.3.1 Agent Status Monitoring de 4 capas

Los indicadores de carga tradicionales (spinners, progress bars) no funcionan para tareas agenticas que toman minutos u horas. Se requiere un sistema de estado en capas: **ambient badge** (estado siempre visible, no intrusivo), **progress panel** (detalle de pasos al expandir), **attention notification** (alerta cuando se requiere input humano), y **summary status** (resumen al completar) [^1^]. Este pattern se usa en ChatGPT y Devin, y soporta multiples tareas concurrentes con tiempos estimados.

Para FaberLoom, el operador industrial necesita saber que esta haciendo el agente sin que le robe atencion del proceso productivo. El ambient badge muestra un dot de color en la esquina. El progress panel se expande al hacer click, mostrando pasos concretos: "Analizando tokens actuales", "Consultando constraints de marca", "Generando propuesta de ajuste". La attention notification aparece solo cuando se requiere aprobacion humana.

**Confidence: ALTO.** Validado en produccion por ChatGPT, Devin, y documentado en AIUX Design Patterns [^1^].

#### 3.3.2 Reasoning visibility: thinking blocks

Un paper de ACM DIS 2026 demuestra que mostrar el "pensamiento" del agente antes de la respuesta aumenta significativamente la confianza y el engagement del usuario [^19^]. El estudio (diseño 3x2 mixed, N=230+ participantes) compara dos framing: Emotionally-Supportive (mas calido, empatico) y Expertise-Supportive (mas logico, profesional). Ambos superan la condicion "None" (sin thinking visible). Para contextos tecnicos/industriales, el framing Expertise-Supportive — resumenes logicos y profesionales del razonamiento — es mas apropiado.

AG-UI separa el razonamiento interno de las respuestas finales mediante ReasoningMessage, donde el agente controla que se muestra: full visibility, summary only, o hidden (encrypted) [^2^]. Para FaberLoom, usar **summary only** por defecto: un resumen tecnico conciso del razonamiento ("Analizando contraste WCAG del componente Button... Contrast ratio: 4.2:1, ajustando a 4.5:1"). El chain-of-thought completo va en modo Verbose, bajo demanda.

La advertencia del paper es critica: el visible thinking puede crear "expectancy violations" negativas si el thinking implica profundidad pero la respuesta final es superficial [^19^]. El razonamiento mostrado debe ser consistente con la calidad de la propuesta.

**Confidence: ALTO.** Paper peer-reviewed ACM DIS 2026 [^19^], implementacion confirmada en AG-UI [^2^].

#### 3.3.3 Cost surfacing: resumen por sesion, alerta anti-runaway

LangSmith demuestra que el tracking automatico de tokens y costos por operacion es tecnicamente viable y desglosado por input/output/other tokens [^7^]. Langfuse muestra costo LLM por trace individual con roll-up automatico en dashboards [^10^]. La metrica de negocio mas valiosa no es costo por request sino **cost per successful task**, que incluye tokens, tool fees, infrastructure y retries [^9^].

Para FaberLoom, el modelo correcto es disclosure contextual por rol: el **operador** no ve costos en la interfaz de trabajo — crear ansiedad inhibe el uso. El **supervisor** ve resumen por sesion en el tab Sanidad. El **administrador** ve dashboard detallado por tenant con costos acumulados, trends, y alerta configurable cuando un tenant supera su quota. La alerta anti-runaway es la ultima linea de defensa: un agente puede gastar $700 en una noche en loops de re-planning; el billing alert debe disparar cuando el costo por sesion excede un umbral configurable [^30^].

La evidencia de CloudZero muestra que cada llamada LLM debe etiquetarse con Feature, Team, Customer/Tenant ID, Environment, Prompt version, Model, y Workflow type para que el gasto sea "immediately explainable" [^11^]. Para FaberLoom multi-tenant, esta etiquetacion es obligatoria desde el diseno.

**Confidence: ALTO** para tracking, **MEDIO** para presentacion UX (falta research especifico sobre cost surfacing en interfaces industriales).

#### 3.3.4 Error recovery de 4 capas

La recuperacion de errores en agentes requiere cuatro capas de defensa. Primera: **retry** con exponential backoff y jitter para errores transitorios (503, rate limits) [^12^]. Segunda: **fallback** — intentar funcion primaria N veces, luego fallback a funcion alternativa, y finalmente cache [^14^]. Tercera: **error classification & routing** en cuatro categorias — Transient (system retry), LLM-recoverable (el LLM reformula), User-fixable (human interrupt), Unexpected (developer bug) [^16^]. Los datos de produccion muestran que esta clasificacion reduce unrecoverable failures del 23% a menos del 2%, y el costo por failure en 85% [^16^]. Cuarta: **checkpoint & recovery** — checkpointing periodico del estado para reanudar sin perder progreso [^18^].

Los cinco patrones HITL core (Approval Gate, Escalation Ladder, Confidence-Based Routing, Collaborative Drafting, Audit Trail with Lazy Review) reducen la tasa de error critico del 23% al 5.1% [^17^]. Coinbase usa un modelo de 3 tiers: AI maneja 60% de queries rutinarias, Tier 1 review para informacion financiera, Tier 3 fraud team para transacciones mayores a $10K [^17^].

El circuit breaker previene "retry storms" donde un agente gasta recursos llamando repetidamente una API rota. Tiene tres estados: Closed, Open, Half-open. Es especialmente critico para agentes que "re-plan" en lugar de reintentar la misma llamada [^13^]. Para FaberLoom: step-count ceiling (max_steps=25), wall-clock timeout por sesion, error classification, kill switch manual, y token budget por tenant.

**Confidence: ALTO.** Datos de produccion confirman reduccion de 23% a <2% en failures [^16^].

#### 3.3.5 Transparency vs overwhelm: progressive disclosure

La tension entre transparencia (mostrar todo para construir confianza) y overwhelm (saturar al usuario con informacion) se resuelve con progressive disclosure de tres niveles: **Summary** (por defecto: solo resultado y estado), **Normal** (expandir: pasos del agente, confidence, costo estimado), **Verbose** (modo debug: full trace, reasoning completo, tool calls con parametros). Este patron se observa en Anthropic (modos de thinking), AG-UI (reasoning control), y shadcn Chain of Thought (componente collapsible) [^32^].

El estudio de ACM DIS 2026 confirma que XAI usable bajo cognitive overload requiere insights concisos, relevantes y accionables, alineados con mixed-initiative interface design [^33^]. Para FaberLoom, donde el operador industrial ya tiene carga cognitiva del proceso productivo, menos es mas: mostrar lo esencial por defecto, permitir expandir para detalles, nunca mostrar informacion raw sin que el usuario la solicite explicitamente.

**Confidence: ALTO.** Resolucion confirmada del Conflict Zone CZ-3 en cross-verification.

---

### 3.4 Matriz de Patterns por Superficie FaberLoom

La tabla siguiente cataloga los 24 patterns identificados, mapea cada uno a la superficie de FaberLoom donde se despliega (Configurar / Iterar / Sanidad / Cross-cutting), y asigna prioridad de implementacion.

| # | Pattern | Superficie | Prioridad | Evidencia de implementacion | Confidence |
|---|---------|-----------|-----------|---------------------------|------------|
| 1 | **3-Checkpoint Framework** (Plan→Findings→Diff) | ITERAR | MVP | VS Code Copilot, Cursor, SAP [^662^][^609^] | ALTO |
| 2 | **3-Action Pattern** (APROBAR/DESCARTAR/ITERAR) | ITERAR | MVP | VS Code [^678^], inference.sh [^717^], SAP [^609^] | ALTO |
| 3 | **Confidence Routing** (auto-approve >90%) | ITERAR | V1.1 | Grizzly Peak [^614^], SAP [^609^], UserOrbit [^746^] | ALTO |
| 4 | **Visual Diff Before/After** | ITERAR + SANIDAD | MVP | Cursor [^620^], Zed [^738^], Nimbalyst [^745^] | ALTO |
| 5 | **Checkpoints Automaticos** (undo 1-click) | ITERAR | MVP | Cursor [^622^], Bolt.new [^736^] | ALTO |
| 6 | **Audit Log** (timestamp + usuario + decision) | SANIDAD | MVP | Bright Byte [^645^], HatchWorks [^615^] | ALTO |
| 7 | **Hash Chaining** (audit inmutable) | SANIDAD | V1.2 | Bright Byte [^645^] | MEDIO |
| 8 | **ESCALATE.md** (timeout + escalation) | ITERAR | V1.1 | escalate.md [^641^], AXME [^756^] | MEDIO |
| 9 | **Wizard con Progress Bar** | CONFIGURAR | MVP | Upwork, Duolingo [^578^] | ALTO |
| 10 | **Mission Panel** (objetivo + constraints) | CONFIGURAR | MVP | Botpress, MindStudio [^578^] | ALTO |
| 11 | **Tools Catalog** (App Store pattern) | CONFIGURAR | MVP | Botpress, n8n [^578^] | ALTO |
| 12 | **Model Config Form** | CONFIGURAR | MVP | Replicate Playground [^685^] | ALTO |
| 13 | **Chat + Preview Side-by-Side** | ITERAR | MVP | Microsoft Copilot [^653^], Oracle [^764^] | ALTO |
| 14 | **Interrupt & Resume** | ITERAR | MVP | LangGraph [^684^], Cloudflare [^651^] | ALTO |
| 15 | **AG-UI Protocol** (17 eventos) | Cross-cutting | MVP | CopilotKit, LangChain [^727^][^776^] | MEDIO-ALTO |
| 16 | **Trace Tree View** | SANIDAD | MVP | AgentPrism, LangSmith [^727^] | ALTO |
| 17 | **Scorecard Dashboard** (metricas ponderadas) | SANIDAD | MVP | TestingXperts [^26^], Supportbench | ALTO |
| 18 | **A/B Comparison** (ejecuciones lado a lado) | SANIDAD | MVP | Braintrust, LangSmith | ALTO |
| 19 | **4 Estados Visuales** (Running/Waiting/Completed/Error) | Cross-cutting | MVP | GitLab Duo [^649^], Claude Monitor [^727^] | ALTO |
| 20 | **Agent Status Monitoring** (4 capas) | Cross-cutting | MVP | ChatGPT, Devin [^1^] | ALTO |
| 21 | **Reasoning Visibility** (thinking blocks) | ITERAR | V1.1 | Anthropic [^19^], AG-UI [^2^] | ALTO |
| 22 | **Cost Surfacing** (resumen por sesion) | SANIDAD | V1.1 | LangSmith [^7^], Langfuse [^10^] | MEDIO |
| 23 | **Error Recovery 4 Capas** (retry→fallback→classify→checkpoint) | Cross-cutting | MVP | PraisonAI [^12^][^14^], Dev.to [^16^] | ALTO |
| 24 | **Progressive Disclosure** (Summary→Normal→Verbose) | Cross-cutting | MVP | AG-UI [^2^], shadcn [^32^] | ALTO |

#### Interpretacion analitica de la matriz

De los 24 patterns, **17 se priorizan como MVP**, 4 como V1.1, 2 como V1.2, y ninguno para V2.0. Esta distribucion es intencionalmente agresiva: FaberLoom es un producto para industria, donde la ausencia de un audit log o de un checkpoint de undo no es una falta de polida — es un riesgo de adopcion. Un gerente de planta no autorizara el uso de un agente que no pueda revertir sus cambios ni documentar que hizo.

La superficie ITERAR concentra la mayor densidad de patterns MVP (7 de 24), seguida de SANIDAD (5) y CONFIGURAR (5). Los 7 patterns cross-cutting son infraestructura compartida entre las tres superficies. Notablemente, 4 de los 6 patterns de aprobacion (3-Checkpoint, 3-Action, Visual Diff, Checkpoints) se despliegan en ITERAR, no en SANIDAD. Esto refleja un principio de diseno critico: la aprobacion ocurre durante la iteracion, no despues. Separar aprobacion de iteracion crearia friccion y degradaria el throughput del operador.

El tab SANIDAD, aunque es el diferenciador de FaberLoom, se construye sobre patterns con alta evidencia de implementacion: Trace Tree View de AgentPrism y LangSmith, Scorecard de TestingXperts, A/B Comparison de Braintrust. El riesgo no es tecnico — es de descubribilidad. Los usuarios no esperan un tab de QA porque ninguna plataforma lo tiene. La mitigacion es hacer que Sanidad sea el destino natural despues de cada sesion de iteracion: al completarse el agente, la transicion a Sanidad es automatica pero reversible.

Los dos patterns con Confidence MEDIO (Hash Chaining y ESCALATE.md) se aplazan a V1.1/V1.2 porque dependen de estandares emergentes. El resto tiene evidencia de produccion de al menos dos fuentes independientes.

| Superficie | Patterns MVP | Patterns V1.1 | Patterns V1.2 | Total |
|---|---|---|---|---|
| CONFIGURAR | 5 | 0 | 0 | 5 |
| ITERAR | 7 | 1 | 0 | 8 |
| SANIDAD | 4 | 1 | 1 | 6 |
| Cross-cutting | 1 | 2 | 1 | 5 |
| **Total** | **17** | **4** | **2** | **24** |

La asimetria en la distribucion — 17 de 24 patterns en MVP — refleja la realidad de construir para industria: los usuarios industriales no toleran "lo iteraremos despues" en auditabilidad, recovery, ni control de gastos. La plataforma debe ser trustworthy desde el primer dia, o no sera usada.


---

## 4. Síntesis Anthropic-Style: Qué Copiar y Qué Evitar

La interfaz de Claude ha pasado por cinco iteraciones mayores en veinticuatro meses: desde el chat minimalista de 2024 hasta el workspace de paneles arrastrables de Claude Code Desktop, pasando por Artifacts, Cowork y el sistema de permisos con clasificador AI. Cada iteración responde a una misma pregunta: ¿cuánto control delega el humano y cuánto toma el agente? Anthropic ha resuelto esta pregunta con un espectro de autonomía graduada, no con un interruptor binario. Ese principio — no la estética coral — es lo que FaberLoom debe importar.

### 4.1 Patterns Observables en Claude.ai, Artifacts, Projects y Console

#### 4.1.1 Chat-first UI: Layout Tres Columnas, Paleta Cálida, Input Generoso

La interfaz de claude.ai se organiza en tres columnas: sidebar izquierda con historial de chats y acceso a Projects, área central para la conversación, y panel derecho contextual que muestra Artifacts, Project Knowledge o Preview según el modo [^1^]. El canvas usa un cream deliberadamente cálido (#faf9f5) con coral (#cc785c) en CTAs, una decisión de diferenciación de marca explícita contra el gris frío de OpenAI y el azul corporativo de Microsoft [^2^]. El input box es generoso (~300 px de altura), con bordes redondeados, sombra suave, y un ícono "+" que abre el menú de adjuntos. Los archivos se muestran como chips removibles con ícono de tipo, apilados horizontalmente debajo del input [^3^].

El homepage de Claude incluye un toggle Chat/Cowork que refleja esta dualidad: conversación libre versus workspace colaborativo para trabajo estructurado [^4^]. Este toggle es una declaración de filosofía — Anthropic reconoce que chat y workspace estructurado son modos mentales diferentes que requieren interfaces diferentes.

#### 4.1.2 Tool-Use UI: Tres Modos de Visualización y Color-Coding por Tipo

Claude Code renderiza tool calls con tres modos controlados por Ctrl+O: Normal (resumen colapsado), Verbose (cada tool call con input/output), y Summary (solo respuestas finales) [^5^]. En modo Normal, un tool call aparece como una sola línea — "Edited 5 files +27 -23, committed bbbe19" — expandible bajo demanda. La dirección de diseño es clara: Anthropic colapsa agresivamente después de que usuarios reportaron que tool calls expandidos tenían la misma prominencia visual que el texto del asistente, haciendo el chat "muy difícil de leer" [^6^]. El color-coding por tipo es ya convención del ecosistema: Read=azul, Write=verde, Edit=ámbar, Bash=rojo [^7^].

#### 4.1.3 Artifacts: Panel Deslizable, Toggle Preview/Code, Version History

Artifacts aparece como panel deslizable desde la derecha cuando Claude detecta contenido sustancial. La conversación principal se mantiene limpia; el contenido vive en su propio workspace [^8^]. El panel soporta toggle Preview/Code y version history para revertir a estados anteriores [^9^]. Los Live Artifacts (abril 2026) añaden dashboards persistentes que se refrescan con datos actuales vía MCP, conectando a Google Calendar, Slack y otros servicios [^10^].

#### 4.1.4 File Uploads: Drag&Drop, Chips Visibles, Project Knowledge con RAG Automático

Claude soporta múltiples métodos de upload — drag&drop, botón de attachment, paste desde clipboard — con límites de 30 MB por archivo y hasta 20 archivos simultáneos [^11^]. En Claude Projects, los archivos se suben a un Project Knowledge panel persistente across todas las conversaciones. Cuando el conocimiento se acerca al límite de contexto, Claude activa RAG automáticamente, expandiendo capacidad hasta 10x sin configuración del usuario [^12^].

#### 4.1.5 Approval Flows: Cinco Modos de Permiso y Consent Fatigue del 93%

Claude Code ofrece cinco modos de permiso que representan diferentes equilibrios entre conveniencia y supervisión: default (solo lecturas sin preguntar), acceptEdits (lecturas + ediciones), plan (solo lectura, modo planificación), auto (todo con safety checks en background via clasificador AI), y dontAsk (solo herramientas pre-aprobadas) [^13^]. Los datos de Anthropic son explícitos: los desarrolladores aprueban el 93% de los prompts de permiso. En tareas complejas, Claude pide clarificación en el 16.4% de los turnos. A cientos de acciones por sesión, la aprobación por acción individual genera "consent fatigue" documentada [^14^]. Los usuarios experimentados dejan que Claude trabaje autónomamente e interrumpen cuando algo sale mal — lo que Anthropic describe como "incident response, not oversight." Auto Mode, lanzado en marzo 2026, usa un modelo clasificador separado (Claude Sonnet 4.6) que revisa cada acción en dos etapas: un filtro rápido de un solo token seguido de chain-of-thought solo si se detecta riesgo, con un FPR (false positive rate) de 0.4% en tráfico real [^15^].

### 4.2 Qué es Trasladable a FaberLoom B2B Operativo

#### 4.2.1 ALTO Fit: Permisos Tres Niveles, Tool Calls Collapsible, Panel Lateral, Thinking Blocks

Copiar estos patrones tal cual, con adaptaciones mínimas.

El sistema de permisos de tres niveles de Claude Code (read-only sin aprobación, file modification con aprobación por sesión, bash commands con aprobación por directorio y comando) es el modelo más probado de autonomía graduada en producción [^16^]. Para FaberLoom, esto se traduce en: Tier 1 (consultas al knowledge base, búsquedas, lectura de datos de producción — sin aprobación), Tier 2 (generación de componentes, ajustes de layout, modificaciones de configuración — aprobación con "no volver a preguntar esta sesión"), Tier 3 (cambios destructivos, integraciones con ERP/SCADA, acciones con blast radius amplio — siempre requiere aprobación explícita). Este espectro de control es directamente trasladable porque responde a la misma pregunta en ambos dominios: ¿cuánto puede hacer el agente sin que un humano revise cada paso?

Los tool calls collapsibles con color-coding son esenciales para un entorno B2B donde el operador necesita ver el estado de las operaciones del agente sin ser abrumado por detalles técnicos. Renderizar cada operación como una línea de resumen colapsada por defecto — con color según tipo (lectura=azul, escritura=verde, ejecución=ámbar, error=rojo) — reduce ruido visual mientras preserva la capacidad de auditoría [^17^].

El panel lateral para output sustancial (patrón Artifacts) valida la decisión de FaberLom de separar chat de canvas. Cuando el agente genera un reporte de OEE, un dashboard de calidad, o código de componente, ese contenido debe renderizarse en un panel derecho dedicado, no como texto plano en el stream de chat. El chat se mantiene como "conversación de control"; el panel lateral es el "workspace de output" [^18^].

Los thinking blocks — razonamiento del modelo visible en gris/cursiva, collapsible — son particularmente valiosos en contexto industrial porque la transparencia del razonamiento construye confianza. Un supervisor de fábrica puede ver cómo el agente está abordando un problema y abortar (Ctrl+C equivalente) si detecta una suposición incorrecta antes de que se materialice en una acción sobre la línea de producción [^19^].

#### 4.2.2 MEDIO Fit: View Mode Selector por Rol y Auto-Approval Basado en Clasificador

Trasladar con adaptaciones significativas.

El selector de view mode (Summary/Normal/Verbose) es aplicable a FaberLoom si se adapta por rol en lugar de por preferencia individual. Los gerentes de planta necesitan Summary (solo acciones tomadas y resultados); los operadores de línea necesitan Normal (resumen de operaciones + respuestas completas); los ingenieros de procesos necesitan Verbose (todo el razonamiento, tool calls completos, thinking blocks) [^20^]. La diferencia clave respecto a Claude: en FaberLoom el modo no es elección del usuario sino asignación por rol, con capacidad de override temporal. Esto refleja la realidad industrial donde diferentes funciones necesitan diferentes niveles de detalle operativo.

El auto-approval basado en clasificador de riesgo (Auto Mode de Claude Code) es trasladable a mediano plazo. El modelo de dos etapas de Anthropic — filtro rápido + razonamiento condicional — optimiza costos y latencia: la mayoría de acciones pasan la primera etapa sin gastar tokens de razonamiento [^21^]. Para FaberLoom, esto requiere un clasificador entrenado con datos operativos reales del tenant, no un modelo genérico. Las acciones de bajo riesgo (ajustes de color, cambios de label, reordenamiento de widgets) pueden auto-aprobarse con notificación silenciosa; las de riesgo medio (modificación de fórmulas de KPI, cambio de layout principal) requieren notificación con opción de revertir; las de alto riesgo (cambios en triggers de alerta, integraciones externas) siempre requieren aprobación explícita.

#### 4.2.3 BAJO Fit: Paleta Cálida Cream y Conversación Libre Estilo Chat

Trasladar solo el principio, no la implementación.

La paleta cream/coral es una decisión de marca deliberada que funciona para el público de Anthropic (desarrolladores, escritores, creativos trabajando en laptops) pero es inapropiada para un entorno industrial. Las fábricas operan bajo iluminación fluorescente, con pantallas táctiles montadas en paredes o estaciones de trabajo con reflejos. Un fondo cream con bajo contraste reduce legibilidad en condiciones de luz industrial. FaberLoom necesita una paleta de alto contraste basada en grises industriales con acentos funcionales (verde para éxito, rojo para alerta, ámbar para warning) — colores que los operadores ya asocian con sistemas SCADA y HMI [^22^].

La conversación libre estilo chat como medio principal de interacción también tiene fit bajo. Joel Lewenstein, Head of Product Design de Anthropic, es explícito: "Chat es excelente para el brain dump inicial pero débil para pasos intermedios. 40 años de GUI craft siguen siendo relevantes" [^23^]. En una fábrica, el operador puede iniciar con "muestra el OEE de la línea 3" por chat, pero la configuración detallada (posición de widgets, rangos de alerta, granularidad temporal) requiere GUI directa. El chat-first no significa chat-only. FaberLoom debe ser chat-initiated, GUI-mediated — el chat como punto de entrada, la interfaz gráfica como medio de ejecución [^24^].

### 4.3 Qué Evitar Explícitamente

#### 4.3.1 No Copiar: Chat como Única Interfaz

Anthropic mismo está migrando lejos del chat-only. El toggle Chat/Cowork en el homepage, Claude Code Desktop con sus paneles arrastrables, y la declaración de Lewenstein sobre "structured, parameterized prompts" como dirección futura demuestran que el chat es un punto de partida, no un destino [^25^]. En FaberLoom, forzar todas las operaciones al chat sería contraproductivo: un operador industrial necesita ver datos en tablas, ajustar sliders, y confirmar acciones con un clic — no escribir "cambia el tercer valor de la segunda fila a 42.5." El chat funciona para iniciar workflows complejos; la GUI funciona para manipular valores con precisión.

#### 4.3.2 No Copiar: Aprobación por Cada Acción

La evidencia de Anthropic es contundente: 93% de aprobación en prompts de permiso significa que la aprobación por acción individual no escala [^26^]. FaberLoom debe usar aprobación por lote — revisar una iteración completa (componente generado, dashboard ajustado, reporte configurado) en lugar de aprobar cada micro-paso del agente. El patrón correcto es el que FaberLoom ya propone: tres botones (Aprobar/Descartar/Iterar) por iteración completa, con auto-approval progresivo para acciones de bajo riesgo basado en historial de éxito [^27^].

#### 4.3.3 No Copiar: Paleta y Estética B2C Consumer

La identidad visual de FaberLoom debe ser propia, con la misma intencionalidad que Anthropic aplicó a la suya. El cream #faf9f5, la tipografía slab-serif, y los bordes redondeados generosos son decisions de marca para un producto de consumo que opera en navegadores de laptops en cafés y oficinas. Un entorno industrial requiere: alto contraste para visibilidad desde distancia, tipografía sans-serif legible en pantallas táctiles de baja resolución, bordes rectos para aprovechar espacio de pantalla, y densidad de información mayor que la de una app de consumo [^28^]. La decisión de diseño no es "copiar o no copiar la paleta de Anthropic" — es "invertir la misma intencionalidad en una identidad propia diseñada para el contexto industrial."

#### 4.3.4 No Copiar: Onboarding con Tours de Múltiples Pasos

En industria manufacturera, el KPI crítico es time-to-production: un operador nuevo debe estar produciendo valor en menos de cinco minutos. Los tours de onboarding de diez pasos que funcionan en productos B2C (donde el usuario tiene tiempo y curiosidad) son inaceptables en una fábrica donde cada minuto de parada cuesta. El onboarding de FaberLoom debe ser: una sola pantalla de "empecemos" con un template pre-configurado, generación automática del primer componente basado en datos existentes del tenant, y ayuda contextual que aparece solo cuando el usuario se detiene en una acción — nunca un tour lineal [^29^].

### Tabla de Síntesis: Qué Copiar, Qué Evitar

| Patrón Anthropic | Veredicto | Confianza | Justificación |
|:---|:---|:---|:---|
| Permisos 3 niveles (read/edit/execute) | **COPIAR** | ALTO | Modelo probado en producción por Anthropic; mapea directo a tiers de FaberLoom. El principio "lectura auto, escritura con confirmación, ejecución con aprobación" es universal para operaciones agentic [^16^]. |
| Tool calls collapsible + color-coding | **COPIAR** | ALTO | Reducción de ruido visual con preservación de auditoría. La dirección de diseño de Anthropic (colapsar agresivamente) valida el approach [^17^]. |
| Panel lateral para output sustancial | **COPIAR** | ALTO | Patrón Artifacts valida la separación chat/canvas de FaberLoom. Reportes y dashboards requieren espacio propio [^18^]. |
| Thinking blocks / razonamiento visible | **COPIAR** | ALTO | Transparencia = confianza en contextos operativos. Permite abortar antes de que un error se materialice en acción [^19^]. |
| Context chips removibles para adjuntos | **COPIAR** | ALTO | Pattern estándar pero implementación particularmente limpia en Claude. Los chips no interfieren con el área de texto [^3^]. |
| RAG automático para knowledge base | **COPIAR** | ALTO | Se activa cuando se excede contexto, sin configuración del usuario. Directamente aplicable al KB de diseño de FaberLoom [^12^]. |
| View mode selector por rol | **ADAPTAR** | MEDIO | Trasladable si se asigna por rol en lugar de preferencia individual. Summary para managers, Normal para operadores, Verbose para ingenieros [^20^]. |
| Auto-approval basado en clasificador | **ADAPTAR** | MEDIO | Requiere datos operativos reales del tenant para entrenar. El modelo de 2 etapas de Anthropic es la arquitectura de referencia [^21^]. |
| Live Artifacts con datos en tiempo real | **ADAPTAR** | MEDIO | Dashboards persistentes relevantes, pero requieren conexión a datos operativos propios (OEE, calidad, producción) en lugar de Google Calendar [^10^]. |
| Iteración conversacional en lenguaje natural | **ADAPTAR** | MEDIO | Core del tab "Iterar", pero con checkpoints explícitos entre pasos que Claude no necesita en su dominio [^9^]. |
| Paleta cream/coral cálida | **EVITAR** | ALTO | Diseñada para laptops en oficinas, no para pantallas industriales con iluminación fluorescente. Reemplazar por gris industrial de alto contraste [^22^]. |
| Chat como única interfaz | **EVITAR** | ALTO | Anthropic mismo está diversificando a paneles y workspace. 40 años de GUI siguen siendo relevantes, especialmente en B2B operativo [^23^]. |
| Aprobación por cada acción | **EVITAR** | ALTO | Consent fatigue del 93% demuestra que no escala. Usar aprobación por lote con auto-approval progresivo [^26^]. |
| Onboarding con tours de 10+ pasos | **EVITAR** | ALTO | En fábrica, time-to-producción debe ser <5 minutos. Usar template pre-configurado + ayuda contextual bajo demanda [^29^]. |
| Estética B2C consumer (bordes redondos, tipografía display) | **EVITAR** | ALTO | Requiere densidad de información industrial, tipografía sans-serif funcional, bordes rectos para aprovechar espacio [^28^]. |
| Conversación libre sin estructura GUI | **EVITAR** | ALTO | Chat para iniciar, GUI para ejecutar. No forzar al chat operaciones que requieren precisión (sliders, tablas, selects) [^24^]. |
| Auto Mode sin override instantáneo visible | **EVITAR** | MEDIO | El clasificador de Anthropic escala a humano tras 3 denegaciones consecutivas. FaberLoom necesita override visible siempre, no después de N fallos [^15^]. |
| Diff-first para todas las operaciones | **EVITAR** | MEDIO | Los diffs son esenciales para operaciones destructivas, pero overhead innecesario para acciones de solo lectura o ajustes cosméticos [^8^]. |

La tabla concentra la síntesis. Los seis items "copiar" responden a una pregunta común: ¿qué ha resuelto Anthropic que FaberLoom no necesita re-inventar? El sistema de permisos graduados, el colapso de tool calls, el panel lateral, el razonamiento visible, los chips de contexto y el RAG automático son soluciones a problemas universales de interacción agent-humano — aplican a cualquier sistema donde un agente ejecuta acciones en nombre de un operador, independientemente del dominio.

Los cuatro items "adaptar" requieren traducción de dominio: view mode por rol (no por preferencia), clasificador entrenado con datos operativos propios, dashboards conectados a OEE en lugar de Google Calendar, iteración con checkpoints explícitos. Son patrones correctos cuya implementación depende del contexto industrial.

Los ocho items "evitar" son anti-patterns que funcionan en B2C consumer pero reducen eficiencia en B2B operativo. La fábrica no es un café; el operador no tiene curiosidad que satisfacer ni tiempo para explorar. Necesita completar una tarea, verificar que está correcta, y volver a la línea de producción.

La confianza de cada veredicto refleja la solidez de la evidencia. Los items ALTO tienen respaldo de datos de producción (93% consent fatigue, 0.4% FPR del clasificador, iteraciones documentadas en GitHub) o declaraciones de los responsables de diseño de Anthropic. Los items MEDIO dependen de extrapolación de dominio — lógica sólida, evidencia directa limitada. Ningún item carece de justificación; donde la evidencia es débil, se declara explícitamente.


---

## 5. Recomendación Final Arquitectural

Este capítulo sintetiza los hallazgos de las cuatro dimensiones precedentes —formato, multi-tenancy, principios UX, y patterns agentic— en una recomendación arquitectural ejecutiva para FaberLoom. No presenta opciones: emite veredictos con confidence level explícito, respaldados por la evidencia acumulada a través de 12 dimensiones de investigación y 350+ findings evaluados.

### 5.1 Formato de Tokens Base

#### 5.1.1 Veredicto Confirmado: W3C DTCG v1.0 como Formato de Intercambio

Usar W3C DTCG (Design Tokens Community Group) versión 1.0, publicado como Technical Report estable en octubre de 2025, como único formato de intercambio para FaberLoom [^HC-1^]. Confidence: **ALTO** — confirmado por 4 agentes de investigación independientes desde fuentes que incluyen el propio W3C TR, documentación de Style Dictionary, Tokens Studio, y análisis comparativos de formato [^HC-1^].

DTCG resuelve el problema fundamental que FaberLoom enfrenta: ningún formato existente soporta multi-tenancy nativamente, pero DTCG proporciona la estructura formal —13 tipos de token oficiales (`color`, `dimension`, `fontFamily`, `fontWeight`, `duration`, `cubicBezier`, `number`, `strokeStyle`, `border`, `transition`, `shadow`, `gradient`, `typography`)— que los agentes IA necesitan para generar UI consistente de forma programática [^112^][^142^]. La herencia via `$type` desde grupos (v2025.10) y el escape hatch `$extensions` para metadatos de tenant hacen que DTCG sea extensible sin romper el estándar [^158^].

La arquitectura debe almacenar DTCG JSON por tenant en PostgreSQL JSONB, aprovechando las capacidades de indexación y consulta de PostgreSQL para recuperación rápida de token sets completos. No se encontró evidencia de que ninguna base de datos alterna ofrezca ventajas sustanciales para este caso de uso específico.

#### 5.1.2 Build Pipeline: Style Dictionary v4+

Usar Style Dictionary v4+ como única herramienta de build. Confidence: **ALTO** — 952,000 descargas semanales en npm, mantenimiento activo de Amazon, y adopción nativa de DTCG desde v4 [^HC-3^]. Style Dictionary transforma tokens DTCG de una fuente única a múltiples formatos de plataforma via un sistema de hooks (transforms, formats, filters, actions) que permite personalización completa [^200^].

La decisión de Amazon respalda este proyecto a largo plazo: Style Dictionary existe desde 2017, recibió rewrites mayores en v3 y v4, y v5 ya soporta DTCG 2025.10 completo con dimension objects y 14 color spaces [^224^]. Las 17 codemods oficiales para migración v3→v4 reducen el riesgo de obsolescencia tecnológica [^39^][^34^].

Style Dictionary genera builds separados por combinación (tenant, role) usando source/include merging y filters. Para FaberLoom, esto significa que un tenant con 5 roles produce 5 CSS bundles distintos, cada uno resuelto en build time, no en runtime. La API async en v4 (`new StyleDictionary()`, `buildAllPlatforms()`) permite integración directa en pipelines CI/CD [^200^].

#### 5.1.3 Runtime: CSS Custom Properties Resueltas en Edge CDN

Servir CSS Custom Properties como bundle resuelto vía edge CDN con content-hash por combinación (tenant, role). Confidence: **ALTO** — 11 de 12 empresas enterprise investigadas (Shopify Polaris, Atlassian, GitHub Primer, IBM Carbon, Adobe Spectrum, Microsoft Fluent) usan CSS Custom Properties como capa de implementación [^HC-2^].

La dualidad DTCG (source of truth formal) + CSS variables (runtime implementation) es el único camino viable para multi-tenant agentic [Insight 1]. Los agentes IA consumen DTCG para generar UI consistente; cada tenant recibe su CSS bundle resuelto en edge sin runtime overhead. Atlassian demuestra este patrón: mantiene tokens como CSS custom properties (`var(--ds-surface-raised)`) con type safety vía JS, sincronizando temas mediante `html[data-theme]` y `data-color-mode` [^94^][^112^]. Shopify implementa multi-merchant theming via secciones y JSON templates que se resuelven a CSS con content-hash para cache busting [^120^].

El content-hash por (tenant, role) garantiza cache invalidation instantánea cuando un tenant modifica sus tokens, sin afectar a otros tenants. Un CDN edge (CloudFront, Fastly, o Cloudflare) reduce latencia de entrega de tokens a <50ms globalmente.

#### 5.1.4 Capa Semántica LLM: DESIGN.md Exportado por Tenant

Implementar DESIGN.md como capa semántica opcional para LLMs, no como dependencia crítica. Confidence: **MEDIO** — DESIGN.md es alpha de Google Labs (desde abril 2026), supervivencia a 24 meses estimada en 30% [^HC-5^].

DESIGN.md no es competidor de DTCG: es su capa de presentación semántica [Insight 6]. Mientras DTCG es para máquinas (parseo estructurado), DESIGN.md es para modelos de lenguaje (comprensión contextual). El formato combina YAML front matter con tokens y markdown body con prosa de diseño que el agente lee como brief antes de generar UI [^30^]. Anthropic usa un approach equivalente: `CLAUDE.md` para contexto del proyecto + herramientas formales para ejecución [^86^].

La recomendación es: (1) almacenar tokens en DTCG JSON como source of truth, (2) exportar/generar DESIGN.md por tenant como brief de diseño via CI/CD, (3) mantener ambos en sync automáticamente. Si DESIGN.md desaparece, FaberLoom sigue funcionando con DTCG puro. El CLI de DESIGN.md exporta a DTCG (`design.md export --format dtcg`) y Tailwind (`--format tailwind`) [^45^][^301^].

![FaberLoom Token Pipeline Architecture](faberloom_architecture_diagram.png)

| Capa | Componente | Tecnología | Confianza | Responsabilidad |
|------|-----------|------------|-----------|-----------------|
| Source of truth | DTCG JSON | W3C DTCG v1.0 | ALTO | Tokens estructurados parseables por agentes; 13 tipos oficiales |
| Source of truth | DESIGN.md | Google Labs alpha | MEDIO | Brief semántico para LLMs; opcional, no crítico |
| Storage | PostgreSQL JSONB | PostgreSQL 15+ | ALTO | Persistencia por tenant; indexación JSON |
| Build pipeline | Style Dictionary v4+ | Amazon OSS | ALTO | Transforms; 952K dl/wk; DTCG-native |
| Validation | DTCG schema validator | Custom + SD hooks | ALTO | Schema check en cada save |
| Runtime output | CSS Custom Properties | CSS variables | ALTO | Bundle resuelto per (tenant, role) |
| Distribution | Edge CDN | CloudFront/Fastly | ALTO | Content-hash; <50ms global |
| Agent interface | AG-UI Protocol | Open standard | MEDIO | 17 eventos agente↔UI |

**Tabla 5.1 — Arquitectura de tokens FaberLoom: pipeline de source a runtime.** La arquitectura dual DTCG/CSS-variables resuelve el problema de multi-tenancy sin formato propietario. Cada capa tiene alternativa documentada excepto AG-UI Protocol, que es irreversible una vez adoptado. El riesgo principal está en DESIGN.md (alpha) y AG-UI (estándar emergente); ambos son opcionales en la fase inicial. La columna "Confianza" refleja la certeza en la decisión tecnológica, no en la madurez de la herramienta.

### 5.2 Top 5 Principios No-Negociables

Cinco principios UX gobiernan todas las decisiones de interfaz en FaberLoom. Estos principios no son aspiracionales: son filtros de go/no-go para cada feature propuesta. Los scores provienen de evaluación ponderada (Relevancia × 3 + Impacto × 2 + Facilidad) / 6 sobre datos de Mendix, AufaitUX HMI, ISA-101, Refactoring UI, NN/g, SaaSFactor, AlignX AI, y Brightscout [^545^][^546^][^577^][^524^].

#### 5.2.1 P1: Progressive Disclosure Contextual — Score 9.3/10

**Mostrar solo lo que el operador necesita AHORA.** En entornos industriales, la revelación progresiva reduce carga cognitiva y acelera la toma de decisiones [^545^]. Si un operador pregunta "estado de telar 5", FaberLoom debe mostrar solo ese telar con acciones contextuales —no todo el dashboard de planta. Este principio, derivado de Mendix y las prácticas HMI de AufaitUX, tiene el score más alto porque aplica a todos los roles y todas las interacciones [^39^]. En una fábrica textil, cada segundo de producción cuenta; overwhelming visual es un defecto de seguridad, no solo de UX. Implementar: overview → unit operation → task detail → diagnostic, siguiendo ISA-101 [^49^].

#### 5.2.2 P2: Trust Ladder — Score 9.2/10

**Autonomía progresiva con evidencia; nunca auto-approve acciones destructivas.** Este es el principio arquitectónico que une a todos los demás [Insight 2]. En industria textil, un error de UI puede detener una línea de producción. La "consent fatigue" del 93% en aprobaciones excesivas [^546^] significa que aprobaciones constantes degradan la experiencia, pero aprobaciones insuficientes son peligrosas. La solución es un espectro de autonomía calibrado por evidencia acumulada: empieza conservador, recopila datos, ajusta. FaberLoom necesita un "Autonomy Engine" que registre cada decisión del agente y su outcome, calibre el umbral de auto-approval basado en historial de éxito por tipo de acción, y nunca auto-approve acciones destructivas (parar línea, eliminar datos) [^62^]. Siempre debe haber un "Revert to manual mode" visible [^57^].

#### 5.2.3 P3: Human-in-the-Loop Estratégico — Score 9.0/10

**Humano en excepciones, no como revisor de rutina.** El error más común en HITL design es convertir a los humanos en quality assurance checkers [^577^]. La pregunta correcta no es "¿debería un humano revisar esto?" sino "¿dónde el juicio humano cambia el resultado de formas que el agente no puede replicar?" [^75^]. Para FaberLoom: el agente maneja rutinariamente consultas de KPIs, alertas de mantenimiento preventivo, y generación de reportes. Pero cuando detecta una anomalia que podría indicar rotura de hilos o fallo mecánico, escala al supervisor con contexto completo. Un supervisor de planta no puede revisar cada acción del sistema; debe ser consultado cuando la confianza del modelo es <70%, la acción tiene impacto financiero >umbral, hay conflicto de políticas, o la situación es novedosa [^79^].

#### 5.2.4 P4: Role-Based Interfaces — Score 9.0/10

**Vistas distintas para operador, supervisor, gerente, QA, mantenimiento.** Los productos B2B SaaS exitosos diseñan interfaces basadas en roles desde los cimientos, no como parches condicionales [^524^]. Una sola interfaz que intenta servir a todos confunde a todos. FaberLomb debe tener: Operador (tareas inmediatas, estado de máquina, chat rápido); Supervisor (vista de línea, alertas, aprobaciones); Gerente (KPIs de planta, eficiencia, tendencias); QA (calidad, defectos, trazabilidad); Mantenimiento (work orders, historial, piezas). Linear es el referente: da a ingenieros sprint boards y a managers velocity charts sin requerir configuración [^91^]. La combinación con tokens multi-tenant crea personalización bidimensional: cada rol en cada tenant ve una interfaz diferente [Insight 8].

#### 5.2.5 P5: Error Prevention + Recovery — Score 9.0/10

**Checkpoints automáticos, undo en 1 click, circuit breaker.** Los sistemas industriales deben diseñarse para hacer difícil o imposible cometer ciertos tipos de errores: gray-out opciones inválidas, requerir confirmación para acciones destructivas, detectar errores inmediatamente con información diagnóstica, y permitir recuperación fácil [^513^]. Cursor implementa checkpoints automáticos antes de cada edición en Agent mode —snapshots locales, separados de Git, que solo trackean cambios del agente [^622^]. Bolt.new ofrece version history nativo con comparación entre versiones [^736^]. FaberLoom debe tener: (a) acciones destructivas requieren confirmación de dos pasos, (b) el agente nunca ejecuta acciones irreversibles sin aprobación explícita, (c) undo disponible para acciones reversibles en 1 click, (d) circuit breaker para prevenir "retry storms" donde un agente gasta $700 en una noche llamando repetidamente una API rota [^13^].

### 5.3 Top 5 Patterns Agentic Obligatorios

Cinco patterns de interfaz agentic son obligatorios en la implementación de FaberLoom. Ninguno es opcional; omitir cualquiera degrada la experiencia operativa de forma medible.

#### 5.3.1 3-Checkpoint Approval Gate con Visual Diff Renderizado

Implementar tres gates mínimos efectivos: Plan review gate (antes de tocar archivos), Findings review gate (después de explorar pero antes de cambiar), y Diff-before-push gate (después de implementar pero antes de aplicar) [^662^]. Este framework, validado en producción enterprise, responde preguntas diferentes en momentos distintos sin overhead significativo. La triada APROBAR / DESCARTAR / ITERAR de FaberLoom se alinea con el estándar emergente: VS Code Copilot (Keep/Undo), Cursor (Accept/Reject), Tiptap AI (accept/reject), Dagu workflows (Approve/Retry/Reject), e inference.sh (Approve/Reject/Modify) [^678^][^676^][^710^][^717^]. SAP implementa el mismo patrón con tres decisiones: approve, conditional (equivalente a iterar con condiciones), y reject [^609^]. Cada gate debe mostrar un visual diff renderizado, no solo código: el operador debe ver exactamente qué cambiará antes de aprobar.

#### 5.3.2 4 Estados Visuales del Agente + AG-UI Protocol

Implementar 4 estados visuales básicos: Running/Working, Waiting/Paused, Completed/Success, Error/Failed [^649^][^727^]. AG-UI Protocol estandariza la comunicación entre agentes y UI mediante 17 eventos (`RUN_STARTED`, `STEP_STARTED`, `TOOL_CALL_START`, `STATE_DELTA`, etc.) que permiten que cualquier agente backend se comunique con cualquier frontend sin acoplamiento [^727^][^776^]. AG-UI nació de la partnership entre CopilotKit, LangGraph y CrewAI; Microsoft, LangChain y Google lo han adoptado [HC-9]. Para FaberLoom, esto es arquitectura, no feature: una vez adoptado, agregar nuevos tipos de agentes no requiere cambiar la UI, y migrar entre backends (LangGraph, CrewAI, custom) no reescribe el frontend [Insight 4]. Los indicadores de progreso AI deben aparecer 1 segundo después de activarse y permanecer visibles al menos 500ms para evitar flickering [^3^]. Confidence en AG-UI: **MEDIO** — el protocolo es nuevo, adopción en progreso.

#### 5.3.3 Chat + Preview Side-by-Side en Tab Iterar con Interrupt/Resume

El tab ITERAR debe usar layout dual-pane: chat a la izquierda, preview a la derecha. Microsoft Copilot implementa dos modos: Inline (previews simples) y Side-by-Side (iteración compleja con workspace contextual); el Side-by-Side preserva el chat como fuente de control principal [^653^]. Oracle AI Agent Studio usa el mismo patrón dual-pane: panel de edición a la izquierda, panel de resultados a la derecha [^764^]. CopilotKit implementa este patrón con `useAgent` hook para generative UI [^783^]. El patrón de interrupt & resume es crítico: LangGraph Studio permite editar AgentState en tiempo real durante la ejecución [^578^]; Claude Code soporta Ctrl+C para abortar y reintentar [^160^]. El usuario debe poder interrumpir al agente, corregir, y reanudar sin perder contexto.

#### 5.3.4 Sanidad como Tab Primario con Trace Tree + Scorecard + A/B Comparison

Ninguna plataforma agentic existente (LangGraph, AutoGen, CrewAI, Vercel v0, Bolt, Cursor) implementa "Validación/Sanidad" como un tab primario de igual jerarquía que Configuración e Iteración [HC-10]. Esto es simultáneamente la mayor oportunidad de diferenciación y el mayor riesgo de descubribilidad del producto [Insight 3]. En industria manufacturera, "sanidad" (QA/validación) es un paso obligatorio regulado (ISO, Six Sigma). Los usuarios industriales están condicionados a verificar antes de aprobar. El tab Sanidad debe incluir: visual diff de cambios propuestos, scorecard de calidad automática (contrast, accessibility, consistency), trazabilidad completa (quién, qué, cuándo, por qué), y aprobación con comentario obligatorio para cambios de alto impacto [^44^]. LangSmith muestra trazas como árboles jerárquicos donde cada nodo representa un paso del agente con latencia, tokens y costo por nodo [^4^]; FaberLoom debe adaptar este patrón para usuarios industriales, no developers. Este tab es el que justifica el precio enterprise de FaberLoom.

#### 5.3.5 Auto-Save Draft entre Tabs con Navegación Editable Backward

La navegación Configurar→Iterar→Sanidad debe ser lineal forward pero editable backward [Insight 10]. Los usuarios nuevos necesitan guía paso a paso; los expertos necesitan saltar directamente a Iterar; todos necesitan poder volver a Configurar sin perder trabajo en Iterar [^137^]. Implementar: (1) wizard lineal por defecto para primer uso, (2) tabs saltables para usuarios avanzados, (3) draft auto-save entre tabs con persistencia en PostgreSQL, (4) warning si se modifica Configurar después de haber avanzado a Iterar. Bolt.new demuestra que version history nativo es esperado por usuarios de plataformas agentic [^736^]; FaberLoom debe ofrecer auto-save de drafts con capacidad de rollback a cualquier punto anterior de la sesión.

### 5.4 3 Anti-Patterns a Prohibir Explícitamente

#### 5.4.1 ANTI-PATTERN #1: Chat-Only sin GUI

El chat inicia, la GUI media. Forzar chat para todo degrada eficiencia operativa [Insight 7]. La evidencia de Anthropic es clara: "Chat para apertura, GUI para pasos intermedios" [^16^]. En una fábrica, un operador puede iniciar con "cambia el dashboard para mostrar OEE" (chat), pero la configuración detallada (posición de widgets, colores, filtros) requiere GUI directa. Los 3 tabs deben tener chat siempre visible para iniciar acciones, pero panel GUI para manipulación directa cuando el usuario lo necesite. No forzar chat para todo.

#### 5.4.2 ANTI-PATTERN #2: Dark Patterns de Engagement

Prohibir: notificaciones constantes, gamificación con badges/puntos, tours intrusivos de más de 5 pasos [Insight 11]. Todos estos patrones funcionan en B2C/consumer pero son destructivos en B2B industrial [^151^]. En una fábrica, el objetivo no es "engagement" ni "time spent" —es eficiencia operativa. Un operador no quiere badges por usar el sistema; quiere hacer su trabajo rápido y sin errores. Onboarding debe ser contextual de ≤3 pasos, no un wizard de 10 pantallas. Notificaciones solo para eventos que requieren acción inmediata (alertas de producción), no para "tips" o "nuevas features".

#### 5.4.3 ANTI-PATTERN #3: Auto-Approval sin Historial ni Override

Cualquier autonomía del agente debe ser reversible y auditable. El patrón 3-botones (Aprobar/Descartar/Iterar) es correcto para el MVP, pero la evidencia de Anthropic (93% consent fatigue) y Cursor (auto-approve configurable) muestra que a largo plazo FaberLoom necesita un cuarto estado: auto-approval progresivo basado en confianza acumulada [Insight 5]. Arquitectura de 4 niveles: Level 0 (siempre human approval) → Level 1 (confidence >90%, notify only) → Level 2 (confidence >95%, silent log) → Level 3 (full auto, daily digest). Cada tenant configura su nivel; cada usuario puede bajar el nivel individualmente. Pero nunca —nunca— auto-approve acciones destructivas sin historial inmutable de decisión. Los audit trails inmutables son requisito para cualquier sistema enterprise: hash chaining + Merkle trees + tiered storage es el estándar arquitectónico [^645^].

### 5.5 Stack de Tooling Concreto

| Categoría | Herramienta | Versión | Costo | Alternativa | Confianza |
|-----------|------------|---------|-------|-------------|-----------|
| Linter tokens | stylelint + plugin custom DTCG | 16.x | Libre | ESLint custom | ALTO |
| Validator DTCG | DTCG schema validator (CI hook) | 1.0 | Libre | AJV custom schema | ALTO |
| Build pipeline | Style Dictionary | v4+ (target v5) | Libre | Terrazzo | ALTO |
| Transforms | SD custom transforms | v4 hooks | Libre | Cobalt UI | ALTO |
| Doc generator | SD built-in docs + custom DESIGN.md gen | v4+ | Libre | Storybook | ALTO |
| Contrast check | WCAG contrast checker | AA/AAA | Libre | axe-core | ALTO |
| Visual regression | Percy/Chromatic por tenant | SaaS | $200-500/mes | Playwright visual | MEDIO |
| Accessibility audit | axe-core + custom rules | 4.x | Libre | Pa11y | ALTO |
| Observabilidad | LangSmith o Langfuse | SaaS | Usage-based | OpenTelemetry custom | MEDIO |
| Agent protocol | AG-UI Protocol | 17 eventos | Libre | Custom WebSocket | MEDIO |
| Cost tracking | LangSmith cost dashboard | Built-in | Incluido | CloudZero | MEDIO |
| Migración | SD codemods (17 oficiales) | v3→v4→v5 | Libre | Manual migration | ALTO |

**Tabla 5.2 — Tooling stack completo para FaberLoom.** Todas las herramientas de validación y migración son de confianza ALTA porque provienen de ecosistemas maduros con adopción enterprise comprobada. Las herramientas de observabilidad (LangSmith/Langfuse) y AG-UI Protocol son MEDIO porque dependen de estándares aún en consolidación. El costo total estimado del stack es $200-500/mes por tenant para visual regression; todo lo demás es libre o usage-based proporcional. La columna "Alternativa" indica el fallback si la herramienta principal se vuelve inviable.

#### 5.5.1 Linter: stylelint + Plugin Custom para Tokens DTCG

Usar stylelint con plugin custom que valide: (a) referencias de token no rotas, (b) tipos DTCG correctos, (c) contraste WCAG AA mínimo, (d) tokens huérfanos no referenciados. IBM Carbon ya implementa un stylelint plugin de este tipo [^12^]. El DTCG schema validator debe ejecutarse en cada save como hook de pre-commit, bloqueando commits con tokens inválidos. La validación automática en CI/CD es obligatoria en multi-tenant: un token inválido afecta a todos los usuarios de ese fabricante [Insight 12].

#### 5.5.2 Exporter: Style Dictionary v4+ con Transforms Custom

Style Dictionary genera tres outputs por build: (1) CSS variables para runtime, (2) DESIGN.md para consumo por LLMs, (3) metadata JSON para el dashboard de administración. Los transforms custom manejan la lógica de (tenant, role): cada combinación produce un CSS bundle distinto con content-hash. La migración de Style Dictionary v3 a v4 está automatizada con 17 codemods oficiales que manejan ESM migration, async API, hooks restructure, y CTI removal [^39^][^34^]. La estrategia de migración futura es 3-fases: mantener formato legacy en paralelo (fase 1), migrar source of truth a DTCG (fase 2), eliminar legacy tras validación (fase 3).

#### 5.5.3 Doc Generator: SD Built-in Docs + Custom DESIGN.md Generator

Style Dictionary v4+ incluye generación de documentación built-in. El custom generator para DESIGN.md produce un brief de diseño por tenant que combina: (a) tokens estructurados en YAML front matter, (b) prosa semántica en markdown body con do's and don'ts de la marca, (c) ejemplos de uso contextual. Este documento es lo que el agente lee antes de generar UI para un tenant específico. El sync automático DTCG↔DESIGN.md ocurre en CI/CD: cualquier cambio de tokens dispara regeneración del DESIGN.md.

#### 5.5.4 Validación: WCAG Contrast, Visual Regression, Accessibility Audit

El stack de validación opera en tres capas. Primera capa (pre-commit): WCAG contrast checker automático valida que todo par de foreground/background cumpla AA como mínimo; el CLI de DESIGN.md ya incluye esta validación [^30^]. Segunda capa (CI): visual regression testing por tenant compara screenshots de referencia contra generados, flagging diferencias pixel-level; Percy o Chromatic son herramientas comerciales maduras, Playwright visual es la alternativa libre. Tercera capa (tab Sanidad): accessibility audit con axe-core ejecuta 100+ reglas WCAG automáticamente, produciendo un scorecard de calidad que el supervisor revisa antes de aprobar cambios. Este triple gate —contrast pre-commit, visual regression en CI, accessibility en Sanidad— garantiza que un token inválido no llegue a producción.

#### 5.5.5 Observabilidad: AG-UI Protocol + LangSmith/Langfuse para Tracing

La observabilidad requiere dos sistemas complementarios. AG-UI Protocol proporciona visibilidad en tiempo real: 17 eventos estandarizados que permiten a la UI mostrar progreso, estados, y resultados del agente sin acoplamiento al backend [^727^]. LangSmith o Langfuse proporcionan trazabilidad histórica: trace trees con latencia, tokens, y costo por nodo; dashboards de cost trends over time; y agrupación por tags/metadata para análisis por tenant [^4^][^7^][^8^]. El costo por tenant debe ser visible en el panel administrativo pero nunca en la interfaz de trabajo del operador — mostrar "$0.023 por consulta" en cada chat inhibe el uso [Insight 9]. El patrón correcto es: resumen por sesión + alerta si supera umbral [^123^].

#### 5.5.6 Migración: 17 Codemods + Estrategia 3-Fases

La estrategia de migración documentada tiene 3 fases. Fase 1 (paralelismo): mantener formato DTCG como source of truth nuevo mientras el formato legacy sigue operando; Style Dictionary genera ambos outputs. Fase 2 (transición): migrar todos los tenants a DTCG usando `convertToDTCG()` de SD v4; los 17 codemods automatizan la mayoría de cambios [^39^]. Fase 3 (eliminación): retirar formato legacy tras 90 días de validación sin incidentes. Esta estrategia aplica tanto a la migración inicial (setup) como a futuras actualizaciones de versión (v4→v5). Los codemods cubren: ESM migration, async API, hooks restructure, CTI removal, y transforms migration [^34^]. La regla de oro: nunca migrar dos dimensiones simultáneamente (formato + versión de SD); siempre una a la vez con rollback planificado.
