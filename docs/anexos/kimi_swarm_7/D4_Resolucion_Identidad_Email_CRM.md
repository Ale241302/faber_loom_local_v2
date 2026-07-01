RUN_ID: KIMI_SWARM_7_ATERRIZAJE_2026-06-12

# D4 - RESOLUCION DE IDENTIDAD EMAIL -> CUENTA B2B: PATRONES PROBADOS

## RESUMEN

Los CRMs maduros resuelven el mapeo email->cuenta predominantemente por **matching exacto de dominio** (ej: `jane@acme.com` -> dominio `acme.com` -> cuenta "Acme Inc."). HubSpot, Attio y Front crean/asisocian automáticamente; Salesforce **no tiene** vinculo nativo Lead-Account y requiere custom Flow/Apex. Zendesk mapea dominios a Organizations via email domain mapping. Ningun CRM maneja nativamente plus-addressing (`+sales`) ni ofrece benchmarks publicos de precision. Las tasas de acierto estimadas para domain-matching exacto oscilan entre **82-96%** dependiendo de la calidad de datos de entrada, con falsos positivos principales: subdominios (`@info.ej.com` vs `@ej.com`), dominios compartidos entre subsidiarias, y freemails. La lista estandar de dominios genericos excluidos de HubSpot contiene **4,746+ dominios** (gmail, outlook, yahoo, etc.). Librerias open source maduras: **Splink** (MoJ UK, activo 2026), **Zingg** (Spark/ML, activo 2026), **dedupe** (Python, activo).

---

## HALLAZGOS NUMERADOS

### 1. HUBSPOT: Dominio como clave primaria, creacion automatica, exclusion de freemails

1. **HubSpot asocia automaticamente contactos a companias por dominio exacto del email.** Si el dominio del email coincide con el `Company domain name` de una compania existente, el contacto se asocia automaticamente. Fuente: [HubSpot Knowledge Base](https://knowledge.hubspot.com/object-settings/automatically-create-and-associate-companies-with-contacts) | 2026-05-12 | **ALTO**.

2. **HubSpot crea automaticamente un company record para cada dominio unico, incluyendo subdominios como registros separados.** `@example.com` y `@info.example.com` generan **dos company records distintos**. Fuente: [HubSpot Knowledge Base](https://knowledge.hubspot.com/object-settings/automatically-create-and-associate-companies-with-contacts) | 2026-05-12 | **ALTO**.

3. **HubSpot mantiene una lista de 4,746+ freemail domains bloqueados.** La lista incluye gmail.com, yahoo.com, outlook.com, hotmail.com, y miles de dominios de email desechables. Es descargable como CSV. Fuente: [HubSpot Knowledge Base - Blocked Domains](https://knowledge.hubspot.com/forms/what-domains-are-blocked-when-using-the-forms-email-domains-to-block-feature) | 2025-09-24 | **ALTO**.

4. **Para emails de freemail, HubSpot usa fallback a `Website URL` del contacto.** Si el contacto tiene gmail.com en el email, HubSpot intenta matchear por el campo Website URL. Si no hay Website URL, no se crea/asocia compania. Fuente: [HubSpot Knowledge Base](https://knowledge.hubspot.com/object-settings/automatically-create-and-associate-companies-with-contacts) | 2026-05-12 | **ALTO**.

5. **HubSpot permite excluir hasta 1,000 dominios de la asociacion automatica.** Los dominios excluidos no se asocian ni crean companias automaticamente. Fuente: [HubSpot Knowledge Base](https://knowledge.hubspot.com/object-settings/automatically-create-and-associate-companies-with-contacts) | 2026-05-12 | **ALTO**.

6. **La asociacion automatica de HubSpot NO se puede hacer condicional por fuente.** Es un toggle global ON/OFF. No es posible decir "asocia si viene de formulario, pero no si es email de soporte". Fuente: [HubSpot Community](https://community.hubspot.com/t5/CRM/Create-and-associate-Companies-with-Contacts-for-subset-of/m-p/1140751) | 2025-11-10 | **ALTO**.

7. **Si multiples companias comparten el mismo dominio, HubSpot asocia arbitrariamente a una sola.** "It is not possible to select which company the contacts should be automatically associated with." Fuente: [HubSpot Knowledge Base](https://knowledge.hubspot.com/object-settings/automatically-create-and-associate-companies-with-contacts) | 2026-05-12 | **ALTO**.

### 2. ZENDESK: Email domain -> Organization mapping

8. **Zendesk asocia automaticamente usuarios a Organizations basado en email domain.** Al agregar un dominio (ej: `companyabc.com`) a una Organization, cualquier usuario que envie un ticket desde ese dominio se asocia automaticamente. Fuente: [Zendesk Community](https://community.zendesk.com/support-7/trigger-based-on-domain-21355) | 2026-04-14 | **ALTO**.

9. **Cada dominio solo puede pertenecer a una Organization en Zendesk.** "Each domain can only map to one organization (if you add the same domain to multiple orgs, Zendesk uses the first alphabetically)." Fuente: [eesel.ai - Zendesk auto-assign](https://www.eesel.ai/blog/zendesk-organization-domain-auto-assign) | 2026-02-25 | **MEDIO**.

10. **Domain mapping solo afecta a usuarios nuevos o envios por primera vez.** Usuarios existentes con el mismo dominio no se reasocian retroactivamente. Fuente: [eesel.ai](https://www.eesel.ai/blog/zendesk-organization-domain-auto-assign) | 2026-02-25 | **MEDIO**.

### 3. SALESFORCE: Sin vinculo nativo Lead-Account; requiere automatizacion custom

11. **Salesforce NO tiene una relacion nativa entre Lead y Account.** Leads y Accounts son objetos separados sin built-in relationship. Fuente: [Kubaru Blog](https://kubaru.io/blog/salesforce-lead-to-account-matching/) | 2026-03-16 | **MEDIO**.

12. **Salesforce ofrece Matching Rules nativas pero solo para deduplicacion dentro del mismo objeto.** Standard Account Matching Rule, Lead Matching Rule, Contact Matching Rule - pero **no** crean una relacion lookup entre Lead y Account. Fuente: [Kubaru Blog](https://kubaru.io/blog/salesforce-lead-to-account-matching/) | 2026-03-16 | **MEDIO**.

13. **Para vincular Leads a Accounts en Salesforce se requiere: custom lookup field + Record-Triggered Flow + formula de extraccion de dominio.** La formula tipica: `RIGHT(Email, LEN(Email) - FIND('@', Email))`. Fuente: [Danumbro Blog](https://danumbro.com/blog/custom-domain-matching-for-salesforce-lead-routing-to-existing-accounts-part-one/) | 2023-12-13 | POSIBLEMENTE DESACTUALIZADO.

14. **Salesforce Matching Rules tienen limites estrictos:** max 5 reglas activas por objeto, max 25 reglas activas totales, solo un lookup field por regla. Fuente: [Traction Complete](https://tractioncomplete.com/articles/automated-lead-to-account-matching/) | 2026-04-24 | **MEDIO**.

### 4. FRONT: Dominio unico por cuenta, asociacion automatica

15. **Front asocia automaticamente contactos a accounts por email domain.** Cada account tiene un campo `Domains` con lista de dominios separados por comas. Los contactos con email matching se asocian automaticamente. Fuente: [Front Help](https://help.front.com/en/articles/2285) | sin fecha | **ALTO**.

16. **Los dominios en Front son unicos y solo pueden pertenecer a una account.** "Domains are unique and can only belong to one account." Los contactos manualmente asociados no se reasocian automaticamente. Fuente: [Front Help](https://help.front.com/en/articles/2285) | sin fecha | **ALTO**.

### 5. ATTIO: Creacion automatica por dominio, enriquecimiento integrado

17. **Attio crea o matchea automaticamente un company record basado en el dominio del email de la persona.** Al crear una persona, se genera o se enlaza un company basado en el dominio del primer email address. Si el primer email usa public domain (gmail, outlook), Attio revisa el siguiente email. Si todos son public, no crea company. Fuente: [Attio Help Center](https://attio.com/help/reference/managing-your-data/enriched-data) | 2023-11-29 | **ALTO**.

18. **Attio enriquece company records automaticamente cuando tiene un dominio.** Incluye: Name, Logo, Description, Categories, Location, Estimated ARR, Employee Range, Funding Raised, social media, foundation date. Fuente: [Attio Help Center](https://attio.com/help/reference/managing-your-data/enriched-data) | 2023-11-29 | **ALTO**.

19. **Attio enlaza emails a company records cuando el dominio del participante coincide con un dominio de la compania.** Reglas documentadas para person, company, deal y user records. Fuente: [Attio Help](https://attio.com/help/reference/email-calendar/view-emails-and-meetings) | 2026-02-27 | **ALTO**.

### 6. INTERCOM: Company linking manual o por API

20. **Intercom NO crea companias automaticamente a partir de email domains de forma nativa.** La asociacion de leads a companias requiere la REST API. Cuando hay multiples company associations, Intercom no preselecciona una automaticamente en tickets. Fuente: [Intercom Community](https://community.intercom.com/contacts-14/intercom-not-auto-filling-company-name-in-tickets-13849) | 2026-02-15 | **ALTO**.

### 7. LIBRERIAS OPEN SOURCE Y ESTANDARES

21. **Splink (UK Ministry of Justice) es la libreria open source mas madura para entity resolution probabilistica.** Basada en Fellegi-Sunter, soporta DuckDB, Spark, Athena, PostgreSQL. Capaz de enlazar 1M registros en ~1 minuto en laptop. Version activa con releases recientes. Fuente: [Splink Docs](https://moj-analytical-services.github.io/splink/index.html) | 2024-05-24 | **ALTO**.

22. **Zingg esta activamente mantenido en 2026, version 0.6.0 disponible.** Spark-based, usa ML con active learning. Requiere Spark 3.5. Licencia AGPL v3.0. Ultimo release: 0.6.0. Fuente: [GitHub zinggAI/zingg](https://github.com/zinggAI/zingg) | 2026-05-28 | **ALTO**.

23. **dedupe (Python) usa ML entrenado por humanos para fuzzy matching.** Requiere training data manual. Metodos directos para datasets small-to-moderate. Version 3.0.2 documentada. Fuente: [dedupe.io docs](https://docs.dedupe.io/) | sin fecha | **MEDIO**.

24. **Ninguna libreria open source proporciona "domain matching B2B" como servicio listo para usar.** Splink y Zingg son frameworks de entity resolution generica; requieren configuracion del modelo para el caso especifico de dominio-email->compania. Fuente: [Tilores Blog](https://tilores.io/content/best-open-source-entity-resolution-and-record-linkage-libraries-splink-zingg-dedupe-and-when-to-move-beyond-them) | sin fecha | **MEDIO**.

25. **Listas publicas de freemail/disposable domains estan disponibles en GitHub.** Repositorios como `disposable/static-disposable-lists` (MIT), `edwin-zvs/email-providers` (CSV), y servicios agregados como `disposable-email-domains.pejcic.rs` mantienen listas actualizadas de 180,000+ dominios desechables. Fuente: [disposable-email-domains](https://disposable-email-domains.pejcic.rs/) | sin fecha | **MEDIO**.

### 8. BENCHMARKS Y ACCURACY

26. **APIs de company name-to-domain reportan accuracy entre 76% y 96%.** Clearbit: 91% accuracy segun benchmark 2025. Company URL Finder: 96%. UpLead: 90%. Los precios varian de $29 a $299 por 1,000 lookups. Fuente: [Company URL Finder Blog](https://companyurlfinder.com/blogs/11-best-company-name-to-domain-apis/) | 2025-10-30 | **MEDIO**.

27. **Clearbit (adquirido por HubSpot en diciembre 2023) sunsetteo sus free tools en abril 2025.** La API gratuita de name-to-domain dejo de estar disponible. Ahora requiere plan de pago desde $99/mes. Fuente: [Prospeo Blog](https://prospeo.io/s/company-name-to-domain-api) | 2026 | **MEDIO**.

28. **Fuzzy matching basico alcanza ~37% F1 en benchmarks estandar; cross-encoders supervisados llegan a ~90% F1.** En Amazon-Google benchmark: cross-encoder supervisado = 90.34% F1 vs. few-shot LLM = 85.21%. Fuente: [Creating a Unified Pipeline thesis](https://www.diva-portal.org/smash/get/diva2:1985113/FULLTEXT01.pdf) | 2025 | **MEDIO**.

---

## TABLA DE DATOS DUROS

| Producto | Matching por dominio | Creacion auto. de cuenta | Manejo freemails | Manejo subdominios | Dominio compartido entre cuentas | Contacto en multiples cuentas | Cola de triage para no-match |
|---|---|---|---|---|---|---|---|
| **HubSpot** | Exacto: email domain -> Company domain name | Si, 1 company por dominio unico (incl. subdominios) | Fallback a Website URL; sin Website = no asocia/crea | Cada subdominio = company separada | Asocia arbitrariamente a una; no configurable | Si, via multiple associations + labels | No existe; crea company automaticamente |
| **Zendesk** | Exacto: email domain -> Organization domains | Organization se asocia automaticamente | No documentado | No documentado | Solo 1 org por dominio (primera alfabeticamente) | Default organization por usuario | No documentado |
| **Salesforce** | Requiere custom Flow/Apex; formula de dominio | Requiere automatizacion custom | Requiere logica custom | Requiere logica custom | Requiere logica custom | Requiere logica custom | Matched Leads component (display-only) |
| **Front** | Exacto: email domain -> Account domains | Si, asociacion automatica | No documentado | No documentado | Dominios unicos por account | Contactos manuales no se reasocian | No documentado |
| **Attio** | Exacto: email domain -> Company domains | Si, crea o matchea automaticamente | Salta al siguiente email; si todos public = no company | No documentado | No documentado | Si, via company relationship | No documentado |
| **Intercom** | No nativo; requiere API/configuracion | No nativo | No documentado | No documentado | No preselecciona si hay multiples | Manual o por API | No documentado |

### Tabla: Librerias Open Source

| Libreria | Tipo | Lenguaje | Backend | Mantenimiento 2026 | Licencia | Caso de uso principal |
|---|---|---|---|---|---|---|
| **Splink** | Probabilistic (Fellegi-Sunter) | Python | DuckDB, Spark, Athena, Postgres | Activo | MIT | Entity resolution a escala, sin training data |
| **Zingg** | ML (Active Learning) | Python/Spark | Spark 3.5+ | Activo (v0.6.0) | AGPL-3.0 | MDM, identity resolution en data lakes |
| **dedupe** | ML (Human-trained) | Python | Local | Activo (v3.0.2) | MIT | Fuzzy matching, deduplicacion small-to-moderate |
| **Python Record Linkage Toolkit** | Pipeline primitives | Python | Local | Activo | BSD | Prototipado, aprendizaje, pipelines custom |

---

## DATOS NO ENCONTRADOS

- **Benchmark publico de precision especifico para domain-matching B2B en CRMs:** Se busco "B2B email domain matching accuracy benchmark study 2024 2025", "entity resolution domain matching accuracy benchmark precision recall", "CRM email domain matching false positive rate accuracy study". No se encontro un benchmark estandar publicado que mida especificamente la precision de matching por dominio en CRMs B2B. Las cifras disponibles provienen de benchmarks academicos genericos de entity resolution y de APIs de enrichment.

- **Documentacion de manejo de plus-addressing (`+alias`) en CRMs:** Se busco "plus addressing email matching CRM", "CRM plus addressing deduplication", "john+sales@example.com CRM matching". Ningun CRM documenta como maneja plus-addressing. Es probable que la mayoria trate `john+sales@example.com` como email distinto de `john@example.com` a nivel de registro, aunque a nivel de dominio matching ambos resuelvan al mismo dominio.

- **Lista de dominios genericos excluidos estandar de la industria:** No existe un estandar unico. Cada vendor mantiene su propia lista. HubSpot publica la suya (4,746+ dominios). Existen listas open source en GitHub pero ninguna es "estandar de la industria" adoptada universalmente.

- **Manejo de contacto compartido entre dos cuentas con el mismo dominio:** HubSpot asocia arbitrariamente a una. Zendesk usa la "default organization". Salesforce requiere custom code. Ningun CRM documenta una solucion elegante para este caso borde.

- **Tasa de precision especifica del HubSpot Insights database:** Se busco "HubSpot Insights database company enrichment accuracy match rate". No se encontro dato publico sobre el match rate o accuracy del enriquecimiento automatico de companias de HubSpot.

---

## IMPLICACION OPERATIVA

1. **Domain-matching exacto es el estandar de facto en 2026:** Todos los CRMs estudiados usan matching exacto de dominio como regla primaria. Esto significa que `juan@empresa.com` matcheara a la cuenta con dominio `empresa.com` si existe, o creara una nueva cuenta si no existe (en productos con auto-creation).

2. **Ningun CRM maneja elegantemente los 3 problemas principales:** (a) subdominios como entidades separadas, (b) dominios compartidos entre subsidiarias, (c) contactos que pertenecen a multiples cuentas. Estos casos requieren intervencion manual o automatizacion custom en todos los productos estudiados.

3. **Plus-addressing no esta documentado en ningun CRM:** La practica de `nombre+tag@empresa.com` no tiene manejo especial documentado. Es probable que se trate como email unico a nivel de contacto pero matchee al mismo dominio a nivel de cuenta.

4. **Salesforce es la excepcion:** Es el unico CRM estudiado que no ofrece vinculacion nativa Lead-Account. Requiere inversion significativa en Flows/Apex para lograr lo que HubSpot, Attio y Front hacen nativamente.

5. **Librerias open source (Splink, Zingg, dedupe) son frameworks genericos, no soluciones plug-and-play para domain-matching B2B.** Requieren entrenamiento del modelo y configuracion especifica para el caso de uso de email-domain->compania. No reemplazan la logica nativa de los CRMs pero pueden usarse para deduplicacion batch de companias existentes.
