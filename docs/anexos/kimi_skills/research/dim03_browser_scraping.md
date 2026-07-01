# DIMENSIÓN 3 — Browser Automation, Scraping, Research

## Skills relevantes encontrados

| Skill | Repo | Instalación | Score MWT | Score FB | Por qué (1 línea) |
|---|---|---|---|---|---|
| **agent-browser** | [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) | `npx skills add vercel-labs/agent-browser` | **ALTO** | **ALTO** | Browser automation CLI nativo Rust, snapshot refs @e1/@e2, ~90% menos tokens que Playwright MCP; ideal para flujos multi-step y QA visual. |
| **browser-use** | [browser-use/browser-use](https://github.com/browser-use/browser-use) | `npx skills add browser-use/browser-use@browser-use` | **ALTO** | **ALTO** | Persistent browser sessions, visual element indexing, soporta cloud browsers anti-bot/CAPTCHA; 91k+ estrellas, muy maduro. |
| **browserbase/skills** (browser) | [browserbase/skills](https://github.com/browserbase/skills) | `npx skills add browserbase/skills` o `/plugin install browse@browserbase` | **ALTO** | **ALTO** | Anti-bot stealth, CAPTCHA solving, residential proxies en 195+ países; el más seguro para scraping comercial contra sitios con protección. |
| **apify-ecommerce** | [apify/agent-skills](https://github.com/apify/agent-skills) | `npx skills add apify/agent-skills` o `/plugin install apify-ecommerce@apify-agent-skills` | **ALTO** | **MEDIO** | Scraping de Amazon, Walmart, eBay, IKEA y 50+ marketplaces vía Apify Actors; pay-per-result, rate-limiting gestionado por Apify. |
| **apify-competitor-intelligence** | [apify/awesome-skills](https://github.com/apify/awesome-skills) | `/plugin marketplace add apify/awesome-skills` + `/plugin install apify-competitor-intelligence@awesome-skills` | **ALTO** | **MEDIO** | Análisis de competidores en Google Maps, Booking, Facebook, Instagram, YouTube, TikTok; útil para inteligencia B2B y de marca. |
| **apify-brand-reputation-monitoring** | [apify/awesome-skills](https://github.com/apify/awesome-skills) | `/plugin install apify-brand-reputation-monitoring@awesome-skills` | **MEDIO** | **ALTO** | Monitoreo de reviews, ratings, sentiment y brand mentions; ideal para FaberLoom gestionando reputación de PYMEs LATAM. |
| **competitor-price-tracker** | [onewave-ai/claude-skills](https://github.com/onewave-ai/claude-skills) | `npx skills add onewave-ai/claude-skills --skill competitor-price-tracker` | **ALTO** | **MEDIO** | Monitorea páginas de precios de competidores y alerta cambios; rastrea discount patterns y promotional cycles. |
| **tavily-research** | [tavily-ai/skills](https://github.com/tavily-ai/skills) | `npx skills add tavily-ai/skills --all` + instalar CLI (`curl -fsSL https://cli.tavily.com/install.sh \| bash`) | **MEDIO** | **ALTO** | Deep research con citas, web search, crawl, extract y map; muy útil para investigación de mercado LATAM sin necesidad de browser. |
| **tavily-crawl** | [tavily-ai/skills](https://github.com/tavily-ai/skills) | (incluido en `--all` o `npx skills add tavily-ai/skills --skill tavily-crawl`) | **MEDIO** | **ALTO** | Crawl de sitios completos con extracción de contenido y semantic filtering; ideal para documentar sitios B2B competidores. |
| **firecrawl-scrape** | [firecrawl/cli](https://github.com/mendableai/firecrawl) | `npx skills add firecrawl/cli --skill firecrawl-scrape` | **MEDIO** | **ALTO** | Extracción estructurada de datos de páginas individuales (HTML → JSON limpio); muy popular para scraping ético. |
| **firecrawl-crawl** | [firecrawl/cli](https://github.com/mendableai/firecrawl) | `npx skills add firecrawl/cli --skill firecrawl-crawl` | **MEDIO** | **ALTO** | Crawl de sitios enteros con paginación automática; output markdown estructurado listo para ingestión LLM. |
| **deep-research (Gemini)** | [sanjay3290/ai-skills](https://github.com/sanjay3290/ai-skills/tree/main/skills/deep-research) | `/plugin marketplace add sanjay3290/ai-skills` + `/plugin install deep-research@ai-skills` | **MEDIO** | **ALTO** | Research autónomo multi-step vía Gemini Deep Research Agent; $2-5 por tarea, ideal para informes de mercado y landscaping. |
| **199-biotechnologies/deep-research** | [199-biotechnologies/claude-deep-research-skill](https://github.com/199-biotechnologies/claude-deep-research-skill) | `git clone https://github.com/199-biotechnologies/claude-deep-research-skill.git ~/.claude/skills/deep-research` | **MEDIO** | **ALTO** | Pipeline de 8 fases con source credibility scoring y validación automatizada; no requiere API key de terceros. |
| **last30days** | [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | `/plugin marketplace add mvanhorn/last30days-skill` o `npx add-skill mvanhorn/last30days-skill` | **MEDIO** | **MEDIO** | Research paralelo en Reddit, X, YouTube, HN, Polymarket con scoring por engagement; útil para tendencias de consumo y competencia. |
| **lackeyjb/playwright-skill** | [lackeyjb/playwright-skill](https://github.com/lackeyjb/playwright-skill) | `/plugin marketplace add lackeyjb/playwright-skill` + `/plugin install playwright-skill@playwright-skill` | **MEDIO** | **MEDIO** | Model-invoked Playwright: Claude escribe y ejecuta código Playwright on-the-fly; headless por defecto visible, bueno para prototipos. |
| **dev-browser** | [SawyerHood/dev-browser](https://github.com/SawyerHood/dev-browser) | `/plugin marketplace add sawyerhood/dev-browser` + `/plugin install dev-browser@sawyerhood/dev-browser` | **MEDIO** | **MEDIO** | Persistent browser sessions con QuickJS sandbox; 14% más rápido y 39% más barato que Playwright MCP en benchmarks publicados. |
| **use-my-browser** | [xixu-me/skills](https://skills.sh/xixu-me/skills/use-my-browser) | `npx skills add xixu-me/skills --skill use-my-browser` | **BAJO** | **MEDIO** | Permite al agente usar el browser del usuario directamente; útil para sesiones autenticadas en sitios B2B sin re-login. |
| **web-scraping (mindrally)** | [mindrally/skills](https://skills.sh/mindrally/skills/web-scraping) | `npx skills add mindrally/skills --skill web-scraping` | **MEDIO** | **BAJO** | Skill genérico de web scraping con guías de patrones anti-detection; útil como fallback educativo. |
| **anti-detect-browser** | [antibrow/anti-detect-browser-skills](https://skills.sh/antibrow/anti-detect-browser-skills/anti-detect-browser) | `npx skills add antibrow/anti-detect-browser-skills --skill anti-detect-browser` | **MEDIO** | **BAJO** | Skill enfocado en evadir bot detection para scraping a mayor escala; complementario a browserbase. |

### Skills descartados (mencionados pero no aplica)

| Skill | Razón descarte |
|---|---|
| **testdino-hq/playwright-skill** | Es un **pack de 70+ guías para E2E testing**, no para scraping productivo o investigación competitiva. Su scope es QA/test automation. |
| **Shpigford/screenshots** | Genera **marketing screenshots** (Product Hunt, landing pages) con Playwright. No hace scraping ni extracción de datos. |
| **jthack/ffuf-claude-skill** | Herramienta de **seguridad ofensiva / fuzzing web** (FFUF). Únicamente para pentesting autorizado; riesgo legal si se usa para scraping no autorizado. |
| **mindrally/skills@puppeteer-automation** | 792 installs, overlap total con Playwright skills superiores. Puppeteer está en declive frente a Playwright/agent-browser. |
| **claude-office-skills/skills@amazon-seller** | Skill para **gestión de cuenta de vendedor Amazon** (listings, inventory), no para scraping competitivo. |
| **membranedev/application-skills@mercado-libre** | 10 installs, sin documentación verificable; demasiado inmaduro para producción. |
| **anthropics/skills/webapp-testing** | Ya incluido en **Cowork plugins core** / `anthropic-skills/*` están explícitamente excluidos de recomendación. |

### Gaps detectados (skills que MWT/FB debería escribir)

| Nombre propuesto | Justificación | Para MWT o FB | Prioridad |
|---|---|---|---|
| **amazon-fba-competitive-monitor** | Amazon prohíbe scraping directo en su ToS. Se necesita un skill que orqueste **Keepa API + Sellics/Helium 10 data export + screenshot de listings** vía browserbase (no scraping HTML), generando alertas de precio/stock/reviews sin violar ToS. | MWT | **ALTA** |
| **mercado-libre-scraper-latam** | No existe skill robusto para scraping de Mercado Libre (MLA, MLB, MLM). PYMEs LATAM usan ML como canal principal. Necesita manejar paginación, filtros, y rate-limiting ético para Argentina/Brasil/México/Colombia/Chile. | FB + MWT | **ALTA** |
| **b2b-competitor-site-monitor** | Monitoreo de cambios en sitios corporativos B2B (Marluvas, Tecmater y similares): nuevos productos, PDFs de catálogos, cambios de precio listado, noticias de distribución. Sin API disponible. Debería usar firecrawl-crawl + diffing. | MWT | **ALTA** |
| **html-to-json-extractor** | Skill dedicado a extraer estructuras semánticas de HTML (tablas de producto, specs técnicas, listados) y normalizarlas a JSON usando LLM. firecrawl lo hace parcialmente pero no hay skill puro de "HTML → JSON con schema configurable". | FB + MWT | **MEDIA** |
| **latam-market-research-agent** | Variante localizada de deep-research que prioriza fuentes LATAM: tiendanube, mercadolibre, linio, falabella, coppel, plus paginasamarillas, Google Maps locales. Necesita pipeline en español/portugués. | FB | **MEDIA** |
| **price-alert-scheduler** | Skill que combina competitor-price-tracker + scheduling para ejecutar monitoreos periódicos (cron-like) y emitir alertas cuando cambian precios o listings de competidores clave. | MWT | **MEDIA** |

### Caveats técnicos

- **Amazon ToS & legal**: Amazon tiene los anti-bot más agresivos del e-commerce (CAPTCHA visual, rate limiting, bloqueo de IPs, demandas legales contra scrapers). No se recomienda scraping directo de amazon.com sin usar Apify (que gestiona legalidad y rate limiting) o browserbase (stealth + proxies rotativas). Incluso con estas herramientas, el riesgo de suspensión de cuenta existe si se scrapea desde IPs vinculadas a la cuenta de vendedor MWT.
- **Cloudflare / DataDome / PerimeterX**: `agent-browser` (Vercel) **no tiene anti-bot nativo** y se rompe frecuentemente contra Cloudflare Turnstile. Para sitios con estas protecciones, usar obligatoriamente **browserbase/skills** o **browser-use/cloud**.
- **Costos de browserbase**: Browserbase cobra por créditos de sesión. Un flujo de scraping diario de 50 URLs puede costar $5-20/mes según configuración. Apify cobra pay-per-result (aprox. $0.001-0.01 por página según Actor). Tavily tiene tier gratuito (1000 créditos/mes) y luego pay-as-you-go.
- **Dependencias de CLI**: `browser-use` requiere instalar su CLI (`curl -fsSL https://browser-use.com/cli/install.sh | bash`) y autenticar API key. `tavily` requiere `tvly` CLI. `firecrawl` requiere API key. Estos son pasos extra de onboarding que deben documentarse en el setup de MWT/FB.
- **deep-research (sanjay3290)**: Usa Gemini Deep Research API, que **cuesta $2-5 por tarea** y tiene timeout máximo de 60 min. No es gratis y no soporta fuentes autenticadas/privadas.
- **last30days**: Requiere llaves propias para X/Twitter (login manual), YouTube (`yt-dlp`), y ScrapeCreators para TikTok/Instagram. Reddit y HN funcionan sin API key. No es 100% automatizable sin intervención de setup inicial.
- **dev-browser**: Scripts corren en QuickJS WASM sandbox (no Node.js), por lo que **no se puede importar cualquier librería npm**; está limitado a la API de Playwright expuesta por el skill.
- **Playwright skills (lackeyjb)**: Por defecto corre `headless: false` (browser visible), lo cual puede ser problemático en servidores headless o CI. Necesita configuración explícita para headless en producción.
- **apify-ecommerce**: Aunque menciona Amazon, Apify no garantiza evasión 100% de bloqueos de Amazon. Se recomienda usarlo solo para sitios de competidores menores o marketplaces secundarios, y siempre con rate limiting conservador.
- **Sin skill de Mercado Libre robusto**: El ecosistema de skills tiene un vacío total para LATAM e-commerce. Cualquier agente de FaberLoom que necesite datos de ML deberá usar scraping directo (riesgoso) o escribir un skill propio usando Apify Actors custom.

---

**Fuentes verificadas**: skills.sh, GitHub (vercel-labs/agent-browser, browser-use/browser-use, browserbase/skills, lackeyjb/playwright-skill, sanjay3290/ai-skills, mvanhorn/last30days-skill, onewave-ai/claude-skills, apify/agent-skills, apify/awesome-skills, tavily-ai/skills, firecrawl/cli, 199-biotechnologies/claude-deep-research-skill, SawyerHood/dev-browser), awesome-agent-skills (VoltAgent/awesome-agent-skills, ComposioHQ/awesome-claude-skills).
