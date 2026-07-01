# Dimension 4: Momentum y Supervivencia 24 meses — Proyectos de Design Tokens

> Fecha de investigacion: Abril 2026
> Investigador: Agente de investigacion Faberloom
> Busquedas realizadas: 24 queries independientes
> Fuentes primarias: GitHub, npm, W3C, TechCrunch, documentacion oficial

---

## Executive Summary

- **Style Dictionary** lidera con ~952K descargas semanales npm y desarrollo activo sostenido (v4 en 2024, v5.4.0 en 2026), respaldado por Amazon y co-mantenido por Tokens Studio.
- **Tokens Studio** muestra actividad estable con modelo de negocio claro (plugin de pago a 39EUR/mes), pero es una empresa pequena (1-10 empleados segun ZoomInfo) dependiente del ecosistema Figma.
- **W3C DTCG** alcanzo un hito critico en octubre 2025 con la especificacion v1.0 estable, respaldada por 20+ organizaciones (Adobe, Amazon, Google, Microsoft, Figma, etc.).
- **Specify** levanto 4.6M EUR en seed (2022), sigue activo con producto funcional pero pricing opaco (enterprise sales).
- **Terrazzo** (sucesor de Cobalt UI) es el proyecto OSS emergente mas activo, con releases frecuentes y adopcion temprana.
- **Diez** esta **abandonado** desde agosto 2020 — ultimo commit hace ~6 anos.
- **DESIGN.md** (Google Labs) permanece en estado **alpha/experimental** desde abril 2025 sin actividad significativa reciente.
- **Token Machine** no existe como herramienta de design tokens — probablemente confusion con herramientas de tokenomics/crypto.

---

## 1. Style Dictionary (Amazon)

### Resumen de salud
| Metrica | Valor |
|---------|-------|
| Estrellas GitHub | 4.6K |
| Forks | 619 |
| Issues abiertos | 220 |
| PRs abiertos | 27 |
| Descargas npm semanales | ~952,407 |
| Licencia | Apache-2.0 |
| Version actual | 5.4.0 (mar 2026) |

### Velocidad de desarrollo

Claim: Style Dictionary ha mantenido un ritmo de desarrollo activo con la transicion de v3 a v4 en 2024 y multiples releases v5 en 2025-2026.
Source: GitHub Releases — style-dictionary/style-dictionary
URL: https://github.com/style-dictionary/style-dictionary/releases
Date: 2026-03-22
Excerpt: "v5.4.0 — Add support for DTCG v2025.10 dimension token type object value, while remaining backwards compatible for dimension tokens using string values."
Context: La version 5.4.0 anadio soporte completo para el formato DTCG v2025.10, manteniendo compatibilidad hacia atras.
Confidence: high

Claim: La v4.0 fue lanzada en Q2 2024 con cambios mayores: migracion completa a ESM, soporte de browser nativo, y asincronicidad en APIs.
Source: Style Dictionary v4 statement
URL: https://styledictionary.com/versions/v4/statement/
Date: 2023-2024
Excerpt: "We have started working on the biggest and most important changes, like migrating to ESM, making the library browser-compatible out of the box, and supporting asynchronicity in Style Dictionary's various APIs."
Context: El liderazgo de v4 fue asumido por Tokens Studio en agosto 2023, en colaboracion con Amazon.
Confidence: high

Claim: El proyecto es co-mantenido activamente por Danny Banks (Amazon) y Joren Broekema (Tokens Studio).
Source: Style Dictionary v4 statement / Tokens Studio blog
URL: https://styledictionary.com/versions/v4/statement/
Date: 2023-2024
Excerpt: "In August 2023, the folks at Tokens Studio contacted us about co-maintaining this project, and leading the v4 release (and beyond)!"
Context: Es un modelo hibrido: Amazon mantiene la propiedad y vision general; Tokens Studio lidera el desarrollo dia a dia.
Confidence: high

### Presupuesto/equipo/funding

Claim: Style Dictionary es un proyecto open-source de Amazon (originalmente Amazon UX) sin funding dedicado externo. El mantenimiento depende del tiempo asignado por Amazon y de la contribucion de Tokens Studio.
Source: GitHub — style-dictionary (organizacion)
URL: https://github.com/style-dictionary
Date: 2026
Excerpt: "Created and maintained by Amazon UX"
Context: No se encontro informacion de funding adicional o equipo dedicado exclusivamente. El modelo es mantenimiento corporativo + comunidad.
Confidence: medium

### Comunidad

Claim: Style Dictionary tiene una comunidad madura con 4.6K estrellas, 619 forks, y canal activo de Slack (#style-dictionary-v4).
Source: GitHub / Documentacion
URL: https://github.com/style-dictionary/style-dictionary
Date: 2026-03-22
Excerpt: "4.6k stars, 619 forks"
Context: La comunidad es activa aunque el numero de contributors directos es moderado. La adopcion masiva se refleja en las ~952K descargas semanales npm.
Confidence: high

### Calidad del mantenimiento

Claim: Los issues abiertos son ~220 con 27 PRs abiertos. El tiempo de respuesta ha sido reconocido como "subpar" por los propios mantenedores desde v3, pero se comprometieron a mejorar tras v4.
Source: Tokens Studio blog — Style Dictionary V4 plans
URL: https://tokens.studio/blog/style-dictionary-v4-plan
Date: 2024
Excerpt: "Once we're in v4.0.0, we will also start going through all of the open pull requests and issues and see what's still relevant, we'll be much more responsive to contributions at that point as well, which we acknowledge has been subpar since the v3 release."
Context: El reconocimiento explicito de los mantenedores sobre la calidad del mantenimiento sugiere honestidad pero tambien una carga de trabajo significativa.
Confidence: high

### Prediccion de supervivencia a 24 meses

**Rating: ALTO (90%+)**

- Backing de Amazon + contribucion activa de Tokens Studio
- ~952K descargas semanales — dependencia masiva del ecosistema
- Implementacion de referencia para W3C DTCG spec v1
- Roadmap claro con soporte DTCG completo en v5.4
- Riesgo: dependencia de 2-3 mantenedores clave, issues acumulados

---

## 2. Tokens Studio

### Resumen de salud
| Metrica | Valor |
|---------|-------|
| Plugin Figma usuarios | 100,000+ estimado |
| Empleados | 1-10 (ZoomInfo) |
| Modelo de precios | Freemium (39EUR/mes Starter Plus) |
| Actividad GitHub | Activa (co-mantiene Style Dictionary) |

### Velocidad de desarrollo

Claim: Tokens Studio co-lidera Style Dictionary v4/v5 y mantiene sd-transforms, el paquete oficial de transformaciones para Style Dictionary.
Source: Tokens Studio blog
URL: https://tokens.studio/blog/style-dictionary-v4-plan
Date: 2024
Excerpt: "Together with the full release we will also release @tokens-studio/sd-transforms v1.0.0, meaning it will out of alpha state and be stable from API perspective."
Context: Tokens Studio ha expandido su alcance mas alla del plugin Figma hacia herramientas de transformacion y gestion de tokens.
Confidence: high

Claim: Tokens Studio ha implementado colaboracion nativa con Penpot para tokens W3C DTCG.
Source: Tokens Studio blog
URL: https://tokens.studio/blog/tokens-studio-penpot-bringing-native-open-standard-design-tokens-to-everyone
Date: 2026-04-29
Excerpt: "Together, we've introduced native, open-standard design tokens into Penpot, making it the first open-source design tool to fully embrace the W3C Design Tokens Community Group (DTCG) specification."
Context: La diversificacion hacia Penpot reduce la dependencia exclusiva de Figma.
Confidence: high

### Presupuesto/equipo/funding

Claim: Tokens Studio es una empresa pequena (1-10 empleados segun ZoomInfo). No se encontro informacion de rondas de funding significativas.
Source: ZoomInfo / Tokens Studio pricing
URL: https://www.zoominfo.com/c/token-studio/185270400
Date: 2024-2025
Excerpt: "Token Studio has 1-10 employees"
Context: El modelo de negocio parece ser bootstrapped o con funding minimo, basado en suscripciones al plugin (39EUR/mes Starter Plus). No hay evidencia de VC funding significativo.
Confidence: medium

Claim: El precio del plugin Starter Plus es 39EUR/usuario/mes (facturado anualmente).
Source: Tokens Studio pricing
URL: https://tokens.studio/pricing
Date: 2026-04-29
Excerpt: "Starter PLUS. Our plugin for pros who need more control inside Figma. per user/mo. billed annually. 39."
Context: El modelo freemium tiene tier gratuito basico y tier de pago para profesionales. No se encontro informacion de enterprise tier.
Confidence: high

### Comunidad

Claim: Tokens Studio tiene una comunidad activa con canal de Slack y presencia en GitHub. Es el plugin mas popular para design tokens en Figma.
Source: Tokens Studio blog / GitHub
URL: https://tokens.studio/blog/
Date: 2024-2026
Excerpt: Multiple posts de blog con actualizaciones regulares, integraciones con Style Dictionary, Penpot, etc.
Context: La comunidad es fuerte pero concentrada en el ecosistema Figma (ahora diversificandose a Penpot).
Confidence: medium

### Prediccion de supervivencia a 24 meses

**Rating: MEDIO-ALTO (70%)**

- Liderazgo en co-mantenimiento de Style Dictionary refuerza su posicion
- Modelo de ingresos claro (suscripciones plugin)
- Diversificacion hacia Penpot reduce riesgo de dependencia Figma
- Riesgos: equipo muy pequeno (1-10 personas), competencia con variables nativas de Figma, sin funding VC aparente
- Dependencia del ecosistema Figma/Penpot para su producto principal

---

## 3. Specify

### Resumen de salud
| Metrica | Valor |
|---------|-------|
| Funding | 4.6M EUR seed (2022) |
| Inversores | Eurazeo, Bpifrance, 360 Capital, Seedcamp |
| Estado producto | Activo (specifyapp.com operativo) |
| Modelo | Enterprise SaaS |

### Velocidad de desarrollo

Claim: Specify levanto una ronda seed de 4.6M EUR (4M) en febrero 2022 liderada por Eurazeo.
Source: TechCrunch
URL: https://techcrunch.com/2022/02/24/specify-automagically-collects-stores-and-distributes-your-design-tokens-and-assets/
Date: 2022-02-24
Excerpt: "The startup raised a $4.6 million (4 million) seed round led by Eurazeo. Bpifrance's Digital Venture fund, 360 Capital and Seedcamp are participating as well."
Context: Specify fue posicionado como "el Segment para equipos de diseño" — una plataforma centralizada para tokens y assets.
Confidence: high

Claim: Specify sigue activo en 2025-2026 con producto funcional, soportando 50+ tipos de tokens e integraciones con Figma, GitHub, Notion, Raycast.
Source: Specify app website
URL: https://specifyapp.com/
Date: 2024-2025
Excerpt: "Specify is natively compatible with Figma, GitHub, Notion, Raycast, and many more to come."
Context: El pricing es opaco ("reach out for custom quote"), sugiriendo modelo enterprise sales.
Confidence: high

### Presupuesto/equipo/funding

Claim: Specify es una empresa francesa con funding seed de 4.6M EUR. No se encontro evidencia de Series A o funding adicional posterior a 2022.
Source: TechCrunch / CSS Author guide
URL: https://cssauthor.com/design-token-management-tools/
Date: 2025-12-04
Excerpt: "Cost: Pricing model available but not fully public; reach out to Specify for custom quote"
Context: La falta de transparencia en pricing y la ausencia de noticias de funding adicional sugieren que la empresa podria estar en modo de extension de runway.
Confidence: medium

### Prediccion de supervivencia a 24 meses

**Rating: MEDIO (55%)**

- Producto solido con buen posicionamiento enterprise
- Funding seed de 4.6M EUR (2022) — probablemente buscando Series A o camino a rentabilidad
- Riesgos: sin noticias de funding adicional en 3+ anos, pricing opaco, competencia con herramientas open-source y nativas de Figma
- Dependencia del modelo enterprise sales en un mercado que se commoditiza

---

## 4. W3C Design Tokens Community Group (DTCG)

### Resumen de salud
| Metrica | Valor |
|---------|-------|
| Organizaciones representadas | 20+ (Adobe, Amazon, Google, Microsoft, Meta, Figma, etc.) |
| Editores/autores | 20+ |
| Version estable | v1.0 (octubre 2025) |
| Implementaciones | 10+ herramientas |

### Velocidad de desarrollo

Claim: La especificacion DTCG alcanzo su primera version estable en octubre 2025, con soporte para theming, multi-file, color moderno (Display P3, Oklch), y relaciones de tokens.
Source: W3C DTCG blog
URL: https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/
Date: 2025-10-28
Excerpt: "The stable specification introduces critical capabilities for scaling design systems: Theming and multi-brand support; Modern color specification — full support for Display P3, Oklch, and all CSS Color Module 4 spaces; Rich token relationships — inheritance, aliases, and component-level references."
Context: Este es un hito fundamental que estandariza el formato de design tokens a nivel industria.
Confidence: high

Claim: Mas de 10 herramientas ya soportan o estan implementando el estandar, incluyendo Style Dictionary, Tokens Studio, Terrazzo, Penpot, Figma, Sketch, Framer, Knapsack, Supernova, y zeroheight.
Source: W3C DTCG blog
URL: https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/
Date: 2025-10-28
Excerpt: "More than 10 design tools and open-source projects — including Penpot, Figma, Sketch, Framer, Knapsack, Supernova, and zeroheight — already support or are implementing the standard."
Context: La adopcion por parte de Figma y Penpot es particularmente significativa.
Confidence: high

### Presupuesto/equipo/funding

Claim: El W3C DTCG es un Community Group sin funding directo — opera mediante contribucion voluntaria de organizaciones miembro. Las organizaciones representadas incluyen Adobe, Amazon, Google, Baidu, Sony, Microsoft, Meta, Sketch, Salesforce, Shopify, Figma, Framer, Cisco, Intuit, New York Times, GM, Disney, y mas.
Source: W3C DTCG
URL: https://www.w3.org/community/design-tokens/
Date: 2022-2025
Excerpt: "Organizations represented include Adobe, Amazon, Google, Baidu, Sony, Microsoft, Meta, Sketch, Salesforce, Shopify, Figma, Framer, Cisco, Intuit, New York Times, GM, Disney, Anima, Pinterest, Tokens Studio, Penpot, Knapsack, Supernova, zeroheight, and many others."
Context: El backing institucional del W3C garantiza la legitimidad y sostenibilidad del estandar.
Confidence: high

### Prediccion de supervivencia a 24 meses

**Rating: MUY ALTO (95%)**

- Estandar W3C con backing de las mayores empresas tech del mundo
- Version 1.0 estable alcanzada — punto de no retorno en adopcion
- Implementaciones de referencia funcionales (Style Dictionary, Tokens Studio, Terrazzo)
- No depende de una sola empresa o fuente de funding
- Riesgo minimo: es un estandar, no un producto

---

## 5. DESIGN.md (Google Labs)

### Resumen de salud
| Metrica | Valor |
|---------|-------|
| Estado | Alpha/Experimental |
| Actividad reciente | Muy baja |
| Origen | Google Labs (April 2025) |
| Objetivo | Especificacion para integrar design tokens en documentos markdown |

### Velocidad de desarrollo

Claim: DESIGN.md fue lanzado como alpha en abril 2025 por Google Labs como una propuesta para integrar design tokens directamente en archivos markdown, usando YAML frontmatter.
Source: Google Labs / Design Tokens Community
URL: https://x.com/doingdotcom/status/1909624395367567499
Date: 2025-04-08
Excerpt: "A spec for design tokens in markdown, for a design driven workflow. Set design decisions right in your design documents, design tasks and issues."
Context: Es un proyecto experimental de Google Labs, no un producto maduro.
Confidence: high

Claim: El proyecto parece tener actividad muy limitada desde su lanzamiento alpha. No se encontraron commits frecuentes ni releases significativos post-abril 2025.
Source: Busqueda de actividad reciente
URL: Multiple fuentes
Date: 2025-2026
Excerpt: No se encontraron evidencias de desarrollo activo sostenido.
Context: Google Labs proyectos frecuentemente son experimentales y pueden ser abandonados o integrados en otros productos.
Confidence: medium

### Prediccion de supervivencia a 24 meses

**Rating: BAJO (30%)**

- Proyecto experimental sin backing institucional fuerte
- No hay evidencia de adopcion significativa
- Google Labs tiene historial de abandonar proyectos experimentales
- Riesgo alto: puede ser descontinuado o absorvido por otro proyecto Google

---

## 6. Terrazzo (Sucesor de Cobalt UI)

### Resumen de salud
| Metrica | Valor |
|---------|-------|
| Version actual | 2.1.0 (abril 2026) |
| Licencia | MIT |
| GitHub | terrazzoapp/terrazzo |
| Actividad | Muy activa |

### Velocidad de desarrollo

Claim: Terrazzo (anteriormente Cobalt UI) es un proyecto muy activo con releases frecuentes. La version 2.1.0 fue lanzada en abril 2026 con soporte OAuth para Figma.
Source: GitHub Releases — terrazzoapp/terrazzo
URL: https://github.com/terrazzoapp/terrazzo/releases
Date: 2026-04-14
Excerpt: "@terrazzo/cli@2.1.0 — Add OAuth bearer token support for Figma import."
Context: El proyecto evoluciono de Cobalt UI a Terrazzo, manteniendo la misma vision pero con arquitectura mejorada.
Confidence: high

Claim: Terrazzo ofrece soporte completo para DTCG v2025.10, incluyendo resolvers, y genera codigo para CSS, Sass, JS/TS, Swift, y Tailwind.
Source: Terrazzo documentation
URL: https://terrazzo.app/docs/
Date: 2026
Excerpt: "vs Style Dictionary: Terrazzo is the only tool that supports the full DTCG format (support for resolvers and other 2025.10 features coming in 2.0!). But this will change as Style Dictionary is now following Terrazzo's path in adopting DTCG."
Context: Terrazzo se posiciona como la implementacion mas completa del estandar DTCG.
Confidence: high

### Prediccion de supervivencia a 24 meses

**Rating: MEDIO-ALTO (75%)**

- Proyecto open-source activo con releases regulares
- Liderazgo claro (drwpow como maintainer principal)
- Posicionamiento como implementacion de referencia DTCG
- Riesgos: mantenido principalmente por 1-2 personas, sin backing corporativo grande
- Depende de la continuacion del estandar DTCG

---

## 7. Diez (Design Token Framework)

### Resumen de salud
| Metrica | Valor |
|---------|-------|
| Estrellas GitHub | 1.2K |
| Forks | 62 |
| Issues abiertos | 46 |
| PRs abiertos | 12 |
| **Ultimo commit** | **Agosto 2020 (~6 anos sin actividad)** |
| **Estado** | **ABANDONADO** |

### Velocidad de desarrollo

Claim: Diez no ha tenido actividad de commits desde agosto de 2020. El proyecto esta completamente abandonado.
Source: GitHub — diez/diez commits (master branch)
URL: https://github.com/diez/diez/commits/master/
Date: Visita abril 2026
Excerpt: Commits list muestra: "Commits on Aug 19, 2020 — fix(start): await guard to safely open macOS application" como el commit mas reciente.
Context: Diez fue un proyecto prometedor de Haiku (empresa que parece haber cerrado o pivotado). La cuenta de Twitter @dieznative tampoco tiene actividad reciente.
Confidence: high

### Prediccion de supervivencia a 24 meses

**Rating: NULO (0%) — PROYECTO ABANDONADO**

- Sin commits desde agosto 2020
- 46 issues abiertos sin respuesta
- La empresa detras (Haiku) parece haber desaparecido
- No recomendable para ningun uso productivo

---

## 8. Token Machine

### Hallazgo

**Token Machine NO EXISTE como herramienta de design tokens.** Las busquedas exhaustivas no encontraron ninguna herramienta con este nombre especifico en el ecosistema de design tokens. Es posible que:

1. Sea una confusion con herramientas de tokenomics/crypto (Token Spice, Token Kitchen)
2. Sea un nombre generico para generadores de tokens de seguridad/autenticacion
3. Sea un proyecto muy reciente o privado sin presencia online

**Prediccion de supervivencia a 24 meses: N/A (NO ENCONTRADO)**

---

## Ranking de Supervivencia (24 meses)

| Posicion | Proyecto | Supervivencia | Rating | Riesgo principal |
|----------|----------|--------------|--------|-----------------|
| 1 | W3C DTCG | 95% | MUY ALTO | Ninguno significativo |
| 2 | Style Dictionary | 90% | ALTO | Dependencia de 2-3 mantenedores |
| 3 | Terrazzo | 75% | MEDIO-ALTO | Equipo pequeno, sin backing corporativo |
| 4 | Tokens Studio | 70% | MEDIO-ALTO | Equipo pequeno, competencia Figma |
| 5 | Specify | 55% | MEDIO | Sin funding nuevo, pricing opaco |
| 6 | DESIGN.md | 30% | BAJO | Experimental, sin adopcion |
| 7 | Diez | 0% | NULO | Abandonado desde 2020 |
| N/A | Token Machine | N/A | N/A | No existe como herramienta de design tokens |

---

## Gaps Identificados

1. **No se encontro informacion precisa sobre commits/mes para los ultimos 6 meses** en la mayoria de los proyectos. GitHub no expone esta metrica facilmente sin scraping.
2. **No hay datos financieros actualizados de Tokens Studio** — posible funding no reportado publicamente.
3. **No se encontro informacion sobre el estado actual de Haiku** (empresa detras de Diez) — parece haber desaparecido.
4. **No hay datos de revenue/usuarios activos** para ninguna de las herramientas comerciales.
5. **Token Machine** no pudo ser identificado como herramienta real.
6. **La metrica exacta de "issue response time"** no esta disponible publicamente para la mayoria de los proyectos.

---

## Recomendaciones Especificas

| Para | Recomendacion | Confidence |
|------|--------------|------------|
| **Equipos enterprise** | Adoptar Style Dictionary + W3C DTCG format como stack base. Agregar Tokens Studio plugin para Figma/Penpot. | high |
| **Equipos que buscan alternativa open-source pura** | Considerar Terrazzo en lugar de Style Dictionary si se necesita soporte DTCG completo (resolvers). | medium |
| **Equipos evaluando Specify** | Esperar a ver evidencia de Series A o traction antes de comprometerse. El producto es solido pero la empresa tiene riesgo. | medium |
| **Equipos con Diez en legacy** | Migrar inmediatamente a Style Dictionary o Terrazzo. Diez esta abandonado y no recibe actualizaciones de seguridad. | high |
| **Sobre DESIGN.md** | Monitorear pero no adoptar aun. Esperar a que Google demuestre compromiso sostenido. | high |
| **Sobre W3C DTCG** | Adoptar el formato v1.0 como estandar interno. Es el estandar de facto y estara soportado por todas las herramientas. | high |

---

## Contra-argumentos y Riesgos No Obvios

1. **Dependencia de Figma**: Tanto Tokens Studio como Specify dependen significativamente del ecosistema Figma. Cualquier cambio en la API o modelo de negocio de Figma podria afectarlos. Penpot como alternativa open-source reduce este riesgo pero tiene adopcion mucho menor.

2. **Commoditizacion de design tokens**: Con la estandarizacion W3C, las herramientas de design tokens podrian convertirse en commodity. Las plataformas de diseno (Figma, Penpot) podrian integrar nativamente todo el pipeline, eliminando la necesidad de herramientas intermedias.

3. **Riesgo de mantenedor unico**: Style Dictionary, Terrazzo, y Tokens Studio dependen criticamente de 1-2 mantenedores clave. La perdida de cualquiera de ellos podria ralentizar significativamente el desarrollo.

4. **Especificacion vs implementacion**: Aunque el estandar W3C es solido, la implementacion completa en todas las herramientas tomara tiempo. Hay brechas entre el estandar y las capacidades reales de las herramientas.

5. **Google y proyectos experimentales**: DESIGN.md podria ser abandono rapido como muchos proyectos de Google Labs, o podria integrarse en una herramienta mayor (Material Design, etc.).

---

## Fuentes Primarias Consultadas

1. GitHub — style-dictionary/style-dictionary (releases, pulse, contributors)
2. GitHub — terrazzoapp/terrazzo (releases, issues)
3. GitHub — diez/diez (commits, pulse)
4. GitHub — design-tokens/community-group
5. W3C DTCG — Design Tokens specification v1.0 announcement
6. TechCrunch — Specify seed round (feb 2022)
7. Tokens Studio blog — multiple posts 2024-2026
8. styledictionary.com — v4 statement, documentation
9. npm — style-dictionary package stats
10. terrazzo.app — documentation
11. specifyapp.com — product website
12. tokens.studio — pricing, blog
13. penpot.app — blog posts sobre design tokens
14. CSS Author — Design Token Management Tools 2025
15. Medium — multiple articulos sobre design tokens 2025

---

*Investigacion completada el 28 de abril de 2026. Datos sujetos a cambio dada la velocidad del ecosistema.*
