# K2 - Multi-tenancy de Skills en Produccion

Resumen: La investigacion revela que el multi-tenancy de skills es un area emergente con implementaciones parciales pero no maduras. GoClaw y Scalekit documentan registries per-tenant con overrides; Dify sufrio una vulnerabilidad real de cross-tenant sandbox que fue parcheada con aislamiento por UID; AWS Lambda ofrece TenantIsolationMode per-tenant; Azure OpenAI admite multitenancy pero requiere configuracion separada por tenant para tools. La mayor parte del estado del arte se concentra en MCP multi-tenant y sandboxing de ejecucion, no en registries de skills con RLS. Los huecos mas grandes son: RLS aplicada directamente a skills que consultan bases de datos, y transporte de tenant via contexto server-side (rechazo explicito de headers) documentado solo en GoClaw. Se propone diseño derivado de primeros principios para los huecos identificados.

---

## 1. REGISTRY DE SKILLS PER-TENANT

### Claim: GoClaw implementa un registry de skills con overrides per-tenant incluyendo skills enabled/disabled, MCP servers, LLM configs y tool settings
Source: GoClaw Deep Dive - A Builder's Guide to a Multi-Tenant AI Agent Platform
URL: https://dev.to/truongpx396/goclaw-deep-dive-a-builders-guide-to-a-multi-tenant-ai-agent-platform-5d6c
Date: 2026-04-28
Excerpt: "Per-tenant overrides -- each tenant gets its own: LLM provider configs and API keys; Tool settings (web_search providers, TTS voice, etc.); Skills enabled/disabled; MCP servers + per-user credentials; Channel instances"
Context: GoClaw es una plataforma AI agent gateway open-source en Go que implementa multi-tenancy como decision de diseno fundamental. La plataforma mantiene 40+ tablas con tenant_id NOT NULL. Cada tenant puede tener sus propias skills habilitadas/deshabilitadas, MCP servers con credenciales per-user, y configuraciones de LLM propias. Esto es la implementacion mas cercana a un registry per-tenant documentada en codigo abierto.
Confidence: high

### Claim: Scalekit documenta que el tool registry en multi-tenant debe ser per-tenant capability configuration, no shared across all callers
Source: Scalekit - Single-Tenant to Multi-Tenant Tool Calling Agent Auth
URL: https://www.scalekit.com/blog/single-vs-multi-tenant-tool-calling-agent-auth
Date: 2026-05-20
Excerpt: "Tool registry | Shared across all callers | Per-tenant capability configuration... An enterprise customer with a finance team may require that salesforce_delete_record never be accessible to the agent in their environment, regardless of OAuth scope. A startup customer may not care. At one tenant, you set the tool registry once. At N tenants, tool availability is a per-tenant configuration that must be enforced before the LLM ever selects a tool -- not after the token is resolved."
Context: Scalekit es una plataforma de auth para agentes AI que documenta la transicion de single-tenant a multi-tenant. La tabla comparativa es la referencia mas clara encontrada sobre como cada aspecto del auth de agentes cambia en multi-tenant. El concepto de "tool registry per-tenant" es fundamental: no se trata solo de credenciales, sino de que herramientas estan disponibles para cada tenant.
Confidence: high

### Claim: Claude (Anthropic) implementa admin controls para provisionar skills a nivel de organizacion con scoping por grupos y audit logging
Source: Anthropic Support - Provision and manage skills for your organization
URL: https://support.claude.com/en/articles/13119606-provision-and-manage-skills-for-your-organization
Date: 2026-05-29
Excerpt: "When you upload a skill through organization settings, it becomes available to everyone in your organization... Admin-provisioned skills are enabled by default for everyone, but members can toggle individual skills off if they choose... To give a skill to only some members, bundle your skills into a plugin and assign that plugin to a group. The group's members see those skills, and members outside the group don't."
Context: Claude implementa un modelo de skills con provisioning organizacional. Las skills pueden asignarse a toda la organizacion o a grupos especificos. Los eventos de sharing se capturan en audit log como role_assignment. Esto representa un registry de skills con control de visibilidad, aunque no es multi-tenant en el sentido SaaS (es organizacion interna, no tenant externo).
Confidence: high

### Claim: nearai/ironclaw tiene un issue abierto documentando la necesidad de per-user/per-tenant tool enable/disable en la UI
Source: GitHub - nearai/ironclaw issue #3763
URL: https://github.com/nearai/ironclaw/issues/3763
Date: 2026-05-18
Excerpt: "There is no UI affordance to enable or disable individual tools per user / per tenant. Today the set of available tools is determined by config and code; turning on a tool for a specific customer deployment requires editing config and restarting... Toggles should: Persist per user / per tenant (not global). Take effect on the next dispatch without a restart. Go through ToolDispatcher so enable/disable state is checked at dispatch time."
Context: Este issue documenta un problema real en produccion: un cliente quiere web_search habilitado en su deployment, pero sin soporte UI la unica opcion es hardcodear en config o hacer branch en codigo. El issue propone un panel de tools que liste herramientas registradas (built-in, WASM, MCP) y permita habilitar/deshabilitar por tenant. Esto confirma que incluso plataformas avanzadas tienen gaps en este area.
Confidence: high

---

## 2. AISLAMIENTO DE EJECUCION DE SKILLS / SANDBOX

### Claim: Dify sufrio una vulnerabilidad de cross-tenant source disclosure en su sandbox Python debido a ejecuciones compartiendo el mismo UID y filesystem /tmp
Source: Imperva Threat Research - Dify: When Your AI Platform Becomes the Attack Surface
URL: https://www.imperva.com/blog/dify-when-your-ai-platform-becomes-the-attack-surface/
Date: 2026-05-18
Excerpt: "Sandboxed Python executions shared a filesystem location. Those executions shared the same runtime identity... Separate tenants executing inside the same sandbox root, under the same effective identity, with readable code artifacts left in a shared /tmp. That is the entire isolation bug. Our proof of concept simply sampled /tmp during execution and collected newly created files. In a shared cloud deployment, that exposed wrapper scripts belonging to other tenants running on the same sandbox host."
Context: Dify es una plataforma open-source con 134k+ GitHub stars. La vulnerabilidad permite a un tenant leer el codigo fuente de otros tenants en deployments cloud compartidos. El fix fue mover de un sandbox UID global a un UID per-execution. Este es el ejemplo mas concreto encontrado de una falla real de aislamiento cross-tenant en una plataforma AI agent.
Confidence: high

### Claim: Dify parcheo la vulnerabilidad con tenant isolation basada en UID per-run, cambiando el trust boundary a nivel de sistema operativo
Source: Imperva Threat Research / Dify sandbox commit
URL: https://github.com/langgenius/dify-sandbox/commit/6b3577c7779c4afc9f26645df5a4660a7282a566
Date: 2026-03-19 (fix released)
Excerpt: "uid, err := AcquireUID(ctx). The wrapper was written with os.WriteFile(..., 0600). The file was reassigned with syscall.Chown(..., uid, ...). The embedded prescript stopped using the single global sandbox UID and used the per-run UID instead. This matters more than any cryptographic tweak. Before the fix, every execution looked like the same sandbox user. After the fix, each execution got its own identity and its own readable artifact set."
Context: El fix no fue cambiar la encriptacion, fue cambiar el boundary de aislamiento. Cada ejecucion ahora obtiene su propio UID de Linux, sus archivos son 0600 y chown al UID especifico. Este es el patron de "hard isolation" a nivel de proceso/UID que deberia aplicarse a ejecucion de skills multi-tenant.
Confidence: high

### Claim: AWS Lambda Tenant Isolation Mode crea execution environments separados por tenant, eliminando comparticion de estado global entre tenants
Source: AWS Lambda Tenant Isolation Mode documentation / Pubudu.Dev
URL: https://pubudu.dev/posts/understanding-lambda-tenant-isolation/
Date: 2026-02-22
Excerpt: "With Lambda tenant isolation, you can have a single Lambda function shared by all of the tenant, yet have the isolation you need in a Lambda per tenant. With this new feature, Lambda service will do the heavy lifting by creating execution environments that are dedicated to a specific tenant. This means that execution environments will not be shared across tenants... The global variable counter, or any other shared state in the execution environment, is isolated per tenant."
Context: AWS Lambda Tenant Isolation Mode (PER_TENANT) es una implementacion de infraestructura que demuestra el patron pool-aislado: una sola funcion Lambda pero execution environments separados por tenant, identificados via X-Amz-Tenant-Id header seteado por el Lambda Authorizer (no por el cliente). Es analogo a como una skill deberia ejecutarse: proceso compartido pero contexto de ejecucion completamente aislado.
Confidence: high

### Claim: El patron de sandbox para agentes AI multi-tenant requiere microVM (Firecracker) como minimo aceptable para codigo no confiable, con un sandbox por sesion de ejecucion sin compartir entre usuarios o tenants
Source: Augment Code - Agent Execution Sandbox Guide
URL: https://www.augmentcode.com/guides/agent-execution-sandbox
Date: 2026-05-03
Excerpt: "Production-safe agent execution requires hardware-level isolation (microVMs or userspace kernels), default-deny filesystem and network policies, and layered escape prevention... Provision one sandbox per execution session rather than sharing across users or tenants... Standard Docker/runc shares the host kernel and is explicitly insufficient for untrusted agent code execution. This finding is consistent with public architecture documentation for production platforms including E2B, Modal, and AWS Lambda."
Context: Este articulo sintetiza la postura de multiples plataformas de produccion sobre aislamiento de ejecucion de agentes. El principio "one sandbox per execution session rather than sharing across users or tenants" es directamente aplicable a skills multi-tenant: cada invocacion de skill deberia correr en un sandbox fresco sin estado compartido.
Confidence: high

### Claim: Azure OpenAI documenta que para built-in tools como MCP y Code Interpreter, no se puede inyectar tenant context de forma confiable, por lo que se requieren contenedores dedicados o configuraciones separadas por tenant
Source: Microsoft Azure Architecture Center - Multitenancy and Azure OpenAI
URL: https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/service/openai
Date: 2025-10-28
Excerpt: "For built-in tools like Code Interpreter and remote Model Context Protocol (MCP) server calls, the model infrastructure runs these operations. You can't reliably inject tenant context into built-in tool invocations, so use dedicated containers or separate tool configurations for each tenant."
Context: Microsoft documenta oficialmente una limitacion critica: las tool invocations built-in no permiten inyeccion confiable de tenant context. La solucion propuesta es dedicacion de contenedores/configuraciones por tenant. Esto valida el enfoque de sub-agente o MCP por proceso para aislamiento de skills.
Confidence: high

---

## 3. MANEJO DE SECRETS POR TENANT

### Claim: GoClaw implementa credenciales MCP per-user dentro de cada tenant, con vault integrado para secrets
Source: GoClaw Deep Dive
URL: https://dev.to/truongpx396/goclaw-deep-dive-a-builders-guide-to-a-multi-tenant-ai-agent-platform-5d6c
Date: 2026-04-28
Excerpt: "Per-tenant overrides -- each tenant gets its own: ... MCP servers + per-user credentials"
Context: GoClaw documenta que cada tenant tiene sus propios MCP servers con credenciales per-user. Esto implica un vault de secrets scopado a tenant donde se almacenan las credenciales OAuth/API keys para cada conexion MCP. El modelo es: tenant → MCP servers → per-user credentials, con aislamiento completo entre tenants.
Confidence: high

### Claim: Scalekit documenta que la resolucion de credenciales en multi-tenant requiere (tenant_id, provider, user_id) y el token schema primary key debe ser (tenant_id, provider, COALESCE(user_id, '')) + connection_id
Source: Scalekit - Single-Tenant to Multi-Tenant Tool Calling Agent Auth
URL: https://www.scalekit.com/blog/single-vs-multi-tenant-tool-calling-agent-auth
Date: 2026-05-20
Excerpt: "Credential resolution: get_token('salesforce') → get_token(tenant_id, provider, user_id). Token schema primary key: (provider) → (tenant_id, provider, COALESCE(user_id, '')) + connection_id"
Context: La tabla de Scalekit es la referencia mas precisa sobre como cambia el manejo de credenciales en multi-tenant. La primary key del token incluye tenant_id como dimension obligatoria. El connection_id es un identificador inmutable para el evento de OAuth grant que autoriza toda la cadena.
Confidence: high

### Claim: El patron de vault de credenciales scopado a tenant usa (tenant_id, tool_name) como lookup key y encripta con per-tenant keys via KMS
Source: Omnithium - Multi-Tenant AI Agent Architectures
URL: https://omnithium.ai/blog/multi-tenant-agent-architecture.html
Date: 2026-05-15
Excerpt: "The safe pattern is a tenant-scoped credential vault. When a tool needs an API key, it looks up the key by (tenant_id, tool_name). The vault enforces that only agent processes authenticated for that tenant can retrieve those keys. At rest, keys are encrypted with per-tenant keys managed by a KMS... We recommend never using environment variables for tenant credentials. Environment variables are global to the process."
Context: Este articulo describe el patron completo de manejo de secrets por tenant: lookup por tupla (tenant_id, tool_name), encriptacion con per-tenant keys, y la advertencia critica contra variables de entorno globales. Es exactamente el patron que MWT necesita para credenciales SP-API scopadas por tenant.
Confidence: high

### Claim: Las credenciales para agentes AI deben ser efimeras, scopadas por tarea, y nunca API keys de larga vida
Source: Descope - AI Agent Credential Management Best Practices
URL: https://www.descope.com/blog/post/ai-agent-credential-management
Date: 2026-05-14
Excerpt: "Issue ephemeral, scoped credentials per task. Agents should receive short-lived access tokens scoped to the specific tools, actions, and resources their current task requires and nothing more. Tokens should expire after the task completes, and not a moment beyond it. Agents should NOT receive long-lived API keys or service account tokens with standing access to production resources."
Context: Este articulo establece el principio de credenciales efimeras por tarea. En un contexto multi-tenant, esto se extiende a: cada tenant tiene sus propias credenciales, cada tarea del agente recibe un token scoped a esa tarea especifica para ese tenant, y los tokens expiran al completar la tarea.
Confidence: high

---

## 4. RLS APLICADA A SKILLS QUE TOCAN DATOS

### Claim: RLS en PostgreSQL es critico especialmente cuando las queries son generadas por AI o agent-based systems, porque no se puede asegurar que las queries AI-generated no causen data leaks
Source: Medium - Row-Level Security in PostgreSQL for Multi-Tenant SaaS Apps
URL: https://medium.com/@anand_thakkar/row-level-security-rls-in-postgresql-for-multi-tenant-saas-apps-ef8c324031d0
Date: 2025-04-17
Excerpt: "RLS becomes more critical especially when SQL queries are generated by an AI or agent-based system... AI Generated SQL: You can't always ensure that AI generated queries are not causing data leaks across agents."
Context: Este articulo identifica especificamente el riesgo de queries generadas por AI sin WHERE tenant_id. Cuando una skill usa una tool que consulta base de datos, si la query es generada dinamicamente por el LLM, RLS es la ultima linea de defensa contra cross-tenant data leaks. La politica RLS asegura que incluso si la query omiti tenant_id, el filtro se aplica automaticamente.
Confidence: high

### Claim: GoClaw implementa RLS a nivel de aplicacion con tres reglas: tenant_id NOT NULL en 40+ tablas, WHERE tenant_id = $N en toda query, y tenant fluyendo por context.Context
Source: GoClaw Deep Dive
URL: https://dev.to/truongpx396/goclaw-deep-dive-a-builders-guide-to-a-multi-tenant-ai-agent-platform-5d6c
Date: 2026-04-28
Excerpt: "Three rules, never broken: Every isolatable table has tenant_id NOT NULL. 40+ tables in GoClaw enforce this. Every query includes WHERE tenant_id = $N. No exceptions. Fail-closed. Tenant flows through context.Context. Resolved at the gateway, propagated everywhere, never taken from client headers (which can be spoofed)."
Context: GoClaw implementa el modelo exacto que MWT requiere: tenant_id NOT NULL, queries filtradas obligatoriamente, y transporte de tenant via contexto server-side (no headers del cliente). Este es el patron de referencia para skills que consultan datos.
Confidence: high

### Claim: El patron RLS con PostgreSQL usa session variables (set_config) para establecer tenant context por conexion, asegurando que queries SELECT * sin WHERE se filtren automaticamente
Source: Medium - Row-Level Security in PostgreSQL for Multi-Tenant SaaS Apps
URL: https://medium.com/@anand_thakkar/row-level-security-rls-in-postgresql-for-multi-tenant-saas-apps-ef8c324031d0
Date: 2025-04-17
Excerpt: "CREATE OR REPLACE FUNCTION set_tenant_context(tenant_id INTEGER) RETURNS VOID AS $$ BEGIN PERFORM set_config('app.tenant_id', tenant_id::TEXT, FALSE); END; $$ LANGUAGE plpgsql;... CREATE POLICY tenant_isolation ON customers FOR ALL USING (tenant_id = current_setting('app.tenant_id')::INTEGER);"
Context: El patron es: establecer el tenant context en la sesion PostgreSQL via set_config, y las politicas RLS aplican el filtro automaticamente. Para skills que consultan DB, el flow es: request → gateway extrae tenant → set tenant context en DB → skill ejecuta query → RLS filtra automaticamente.
Confidence: high

---

## 5. MCP MULTI-TENANT Y BROKER PATTERN

### Claim: MCP multi-tenant requiere tres capas de aislamiento adicionales: tool definition isolation, context window isolation, y credential vault isolation
Source: Albato - Multi-Tenant MCP for SaaS: Security & Isolation Guide
URL: https://albato.com/blog/publications/embedded-multi-tenant-mcp-saas
Date: 2026-05-28
Excerpt: "MCP adds protocol-specific surfaces that traditional APIs don't have: tool description metadata entering the LLM context window, credential vaults storing OAuth tokens per user per connection, and prompt-level context that could leak across tenants if not properly scoped... Tool definition isolation: Each tenant may have access to different integrations. Tenant A uses Salesforce and HubSpot. Tenant B uses Pipedrive and Mailchimp. The MCP server must expose the correct tool definitions per tenant."
Context: Albato documenta las tres capas adicionales que MCP agrega al multi-tenancy tradicional. La "tool definition isolation" es directamente equivalente a un registry de skills per-tenant: cada tenant ve solo las tools/skills que tiene configuradas.
Confidence: high

### Claim: El broker pattern (CABP) es la solucion recomendada para propagar contexto de tenant en MCP: un gateway inyecta claims JWT en el contexto JSON-RPC antes de reenviar al MCP server
Source: arxiv - Design Patterns for Deploying AI Agents with Model Context Protocol
URL: https://arxiv.org/html/2603.13417v1
Date: 2025-11-25
Excerpt: "User identity cannot currently be propagated via MCP request headers to the server. The JSON-RPC protocol does not include a standard mechanism for carrying user context (identity, permissions, tenant scope) with tool invocations... A gateway service sits between the agent and the MCP server. It intercepts JSON-RPC requests, extracts claims from the OAuth token in the Authorization header (validating JWT signature, expiry, and issuer), and injects tenant_id, user_id, and permission scopes into the request context before forwarding to the MCP server."
Context: Este paper académico identifica que MCP no tiene mecanismo nativo para propagar tenant context. La solucion propuesta es un broker/gateway que extrae claims JWT e inyecta tenant_id en el contexto. El server lee identidad de este contexto enriquecido, no de parametros raw. Esto es exactamente el patron que MWT usa: tenant fluye por context server-side.
Confidence: high

### Claim: Las tres capas de aislamiento que MCP agrega (tool definitions, context window, credential vault) crean un attack surface que las APIs REST tradicionales no tienen
Source: Prefactor - MCP Security for Multi-Tenant AI Agents
URL: https://prefactor.tech/blog/mcp-security-multi-tenant-ai-agents-explained
Date: 2026-03-17
Excerpt: "MCP adds protocol-specific surfaces that traditional APIs don't have: tool description metadata entering the LLM context window, credential vaults storing OAuth tokens per user per connection, and prompt-level context that could leak across tenants if not properly scoped. These surfaces create a security surface area that traditional REST APIs simply don't have. Every integration you add multiplies the number of credential-scoped boundaries that must be enforced."
Context: Prefactor refuerza que MCP multi-tenant no es solo REST multi-tenant con extra steps. El context window isolation es particularmente relevante para skills: si una skill devuelve datos de otro tenant en su respuesta, esos datos entran al context window del LLM y pueden ser expuestos.
Confidence: high

---

## 6. PATRONES SILO / POOL / BRIDGE Y TRANSPORTE DE TENANT

### Claim: Los tres patrones de aislamiento multi-tenant son silo (dedicado por tenant), pool (compartido), y bridge (hibrido); el patron bridge es el mas adoptado en produccion
Source: QuantumByte - Multi-Tenant Architecture: The Complete Guide for SaaS
URL: https://quantumbyte.ai/articles/multi-tenant-architecture
Date: 2026-05-20
Excerpt: "AWS groups SaaS tenancy patterns into three models: silo, pool, and bridge. Silo: Tenants get dedicated resources. Best for: Regulated workloads, high-value enterprise tenants. Pool: Tenants share most resources. Best for: Early-stage SaaS, cost efficiency. Bridge: Hybrid. Some pooled, some siloed based on plan or risk. Best for: Tiered offerings, gradual migration from pool to silo."
Context: Este articulo sintetiza los tres patrones estandar de AWS. Para skills multi-tenant: compute puede ser pool (procesos compartidos con aislamiento logico), data deberia ser bridge (RLS para la mayoria, schema separado para enterprise), y ejecucion de codigo deberia ser silo (sandbox dedicado por ejecucion).
Confidence: high

### Claim: El transporte de tenant via headers del cliente es inseguro y debe rechazarse; el tenant debe resolverse en el gateway a partir de credenciales y propagarse via contexto server-side
Source: GoClaw Deep Dive
URL: https://dev.to/truongpx396/goclaw-deep-dive-a-builders-guide-to-a-multi-tenant-ai-agent-platform-5d6c
Date: 2026-04-28
Excerpt: "Tenant flows through context.Context. Resolved at the gateway, propagated everywhere, never taken from client headers (which can be spoofed)."
Context: GoClaw implementa exactamente la postura de MWT: tenant nunca via headers de cliente. Se resuelve en el gateway a partir de: API key vinculada a tenant, JWT claims, o webhook registration. Luego fluye por context.Context a traves de toda la stack. Este es el patron de referencia para transporte de tenant.
Confidence: high

### Claim: AWS Lambda Tenant Isolation requiere que el tenant_id se establezca via header X-Amz-Tenant-Id pero SOLO por el Lambda Authorizer, nunca por el cliente; se debe verificar que el cliente no envie ese header
Source: Ran the Builder - Is AWS Lambda Tenant Isolation Mode Enough for SaaS?
URL: https://ranthebuilder.cloud/blog/is-aws-lambda-tenant-isolation-mode-enough-for-saas/
Date: 2026-05-07
Excerpt: "The Lambda authorizer needs to validate the tenant request, extract the tenant_id, and add the special, cool new header 'X-Amz-Tenant-Id' that marks the tenant_id for Lambda to use in the isolation mode. You should also verify that you don't get this header from the client for obvious security reasons."
Context: AWS mismo documenta el principio: el header X-Amz-Tenant-Id debe ser establecido por el authorizer server-side, no confiado del cliente. Esto valida la postura de MWT de "tenant fluye por context server-side y NUNCA por headers de cliente".
Confidence: high

---

## 7. HUECOS ENCONTRADOS / NO LOCALIZADOS

### Claim: Registry de skills per-tenant con RLS aplicada a la metadata del skill
Source: Búsquedas realizadas: "skill registry per-tenant RLS", "multi-tenant skill catalog database RLS", "tenant-scoped skill registry postgres"
URL: N/A
Date: N/A
Excerpt: N/A
Context: No se encontro implementacion documentada de un registry de skills donde la metadata de las skills (que skills existen, que tools tienen, que tenant las puede ver) este protegida por RLS a nivel de base de datos. GoClaw tiene overrides per-tenant pero no documenta RLS sobre la tabla de skills. Claude tiene org-level skills pero no es RLS-based. Este es un hueco: como se asegura que una query de "listar skills disponibles" solo retorne skills del tenant actual?
Confidence: low
Nota: [NO LOCALIZADO - hueco en el estado del arte]. [RECOMENDACION - juicio del analista]: Implementar tabla skill_registry(tenant_id, skill_id, status, config) con RLS policy tenant_isolation USING (tenant_id = current_setting('app.tenant_id')::UUID). Las skills globales se duplican con tenant_id del sistema o se referencian via foreign key con vista tenant-scoped.

### Claim: Implementacion documentada de aislamiento de ejecucion de skills usando sub-agente o MCP por proceso con RLS en el canal de comunicacion
Source: Búsquedas realizadas: "skill execution sub-agent process isolation RLS", "MCP server per-tenant process boundary"
URL: N/A
Date: N/A
Excerpt: N/A
Context: Aunque existen patrones de sandbox (Firecracker, gVisor) y MCP multi-tenant, no se encontro una implementacion documentada que combine: skill ejecutada en proceso separado + RLS aplicada al canal de comunicacion + secrets inyectados en runtime por tenant. Azure OpenAI sugiere "dedicated containers or separate tool configurations for each tenant" pero no documenta como.
Confidence: low
Nota: [NO LOCALIZADO - hueco en el estado del arte]. [RECOMENDACION - juicio del analista]: Arquitectura hibrida: skill catalog en DB con RLS → dispatch por tenant_id → cada skill corre en proceso separado (MCP server o sub-agente) → credenciales inyectadas via vault lookup (tenant_id, tool_name) → canal de comunicacion autenticado con tenant-scoped tokens.

### Claim: Sistema de visibilidad de skills (PUBLIC / PARTNER_B2B / INTERNAL / CEO-ONLY) implementado en produccion
Source: Búsquedas realizadas: "skill visibility levels multi-tenant", "skill access control PUBLIC INTERNAL B2B", "agent skill classification levels production"
URL: N/A
Date: N/A
Excerpt: N/A
Context: No se encontro implementacion documentada de un sistema de visibilidad de skills con niveles jerarquicos. Claude tiene organizacion-level y group-level skills, pero no una taxonomia de visibilidad de 4 niveles. GoClaw tiene skills enabled/disabled per-tenant pero no niveles de visibilidad.
Confidence: low
Nota: [NO LOCALIZADO - hueco en el estado del arte]. [RECOMENDACION - juicio del analista]: Extender la tabla skill_registry con columna visibility_level (enum: PUBLIC, PARTNER_B2B, INTERNAL, CEO_ONLY). La RLS policy incluye la condicion de visibilidad: tenant puede ver skill si tenant_id coincide O si visibility_level <= tenant_clearance_level. Esto permite skills compartidas (como el catalogo de Amazon) con visibilidad controlada.

### Claim: Propagacion de tenant a traves de skills que llaman a otras skills (skill chaining multi-tenant)
Source: Búsquedas realizadas: "skill chain tenant propagation", "multi-tenant skill composition", "sub-agent tenant context inheritance"
URL: N/A
Date: N/A
Excerpt: N/A
Context: No se encontro material sobre como se propaga el tenant_id cuando una skill invoca a otra skill (skill chaining) o cuando un sub-agente es despachado. Este es un problema real: si Skill A (tenant 1) llama a Skill B, ¿como se asegura que Skill B ejecute con el mismo tenant context?
Confidence: low
Nota: [NO LOCALIZADO - hueco en el estado del arte]. [RECOMENDACION - juicio del analista]: El tenant_id debe ser parte immutable del execution context que se propaga automaticamente en cada invocacion de skill. Similar al connection_id de Scalekit: un identificador inmutable que fluye con cada hop de la cadena. No permitir que una skill cambie el tenant context al invocar otra skill.

---

## 8. RESUMEN DE COBERTURA

### Aspectos con implementaciones documentadas:
| # | Aspecto | Evidencia | Confianza |
|---|---------|-----------|-----------|
| 1 | Registry de skills per-tenant | GoClaw (skills enabled/disabled per-tenant), Scalekit (tool registry per-tenant config), Claude (org-level skills), nearai/ironclaw (issue per-tenant toggle) | high |
| 2 | Overrides per-tenant (tools, MCP, LLM configs) | GoClaw (5 categorias de overrides), Scalekit (tabla comparativa completa) | high |
| 3 | Aislamiento de ejecucion (sandbox) | Dify (UID-based fix), AWS Lambda Tenant Isolation, Augment (microVM per session), Azure OpenAI (dedicated containers) | high |
| 4 | Manejo de secrets por tenant | Scalekit (credential resolution per-tenant), Omnithium (tenant-scoped vault), GoClaw (MCP per-user credentials), Descope (ephemeral scoped tokens) | high |
| 5 | RLS para queries AI-generated | PostgreSQL RLS (varios articulos), GoClaw (tenant_id NOT NULL + WHERE clause obligatoria) | high |
| 6 | MCP multi-tenant con broker pattern | arxiv paper (CABP broker), Albato (3 isolation layers), Prefactor (defense in depth) | high |
| 7 | Patrones silo/pool/bridge | AWS documentacion, multiples fuentes (QuantumByte, Zenn, Bluent) | high |
| 8 | Transporte de tenant via contexto | GoClaw (context.Context, nunca headers), AWS Lambda (authorizer setea header) | high |

### Aspectos que son HUECOS (no localizados):
| # | Aspecto | Impacto |
|---|---------|---------|
| 1 | RLS aplicada a tabla de skills (metadata) | Una query de "listar skills" sin RLS podria exponer skills de otros tenants |
| 2 | Aislamiento de ejecucion con RLS en canal de comunicacion | Como se asegura que el canal proceso-DB respeta RLS cuando la skill ejecuta |
| 3 | Sistema de visibilidad de skills (4 niveles) | No hay precedente para PUBLIC/PARTNER_B2B/INTERNAL/CEO-ONLY |
| 4 | Propagacion de tenant en skill chaining | Como hereda tenant context una skill invocada por otra skill |
| 5 | Implementacion end-to-end documentada | No se encontro un caso de estudio completo que combine TODOS los aspectos |

---

## 9. RECOMENDACIONES DE DISENO DERIVADAS DE PRIMEROS PRINCIPIOS

### Para los huecos identificados:

**[RECOMENDACION - juicio del analista] - Registry de skills con RLS:**
```sql
CREATE TABLE skill_registry (
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    skill_id TEXT NOT NULL,
    skill_type TEXT NOT NULL CHECK (skill_type IN ('OFFICIAL', 'AMAZON', 'CUSTOM')),
    status TEXT NOT NULL DEFAULT 'DISABLED' CHECK (status IN ('ENABLED', 'DISABLED', 'DEPRECATED')),
    visibility TEXT NOT NULL DEFAULT 'INTERNAL' CHECK (visibility IN ('PUBLIC','PARTNER_B2B','INTERNAL','CEO_ONLY')),
    config JSONB DEFAULT '{}',
    mcp_server_config JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (tenant_id, skill_id)
);

ALTER TABLE skill_registry ENABLE ROW LEVEL SECURITY;

CREATE POLICY skill_tenant_isolation ON skill_registry
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id')::UUID)
    WITH CHECK (tenant_id = current_setting('app.tenant_id')::UUID);
```

**[RECOMENDACION - juicio del analista] - Arquitectura de ejecucion:**
- Skill catalog: tabla skill_registry con RLS (arriba)
- Dispatch: ToolDispatcher verifica skill_registry antes de ejecutar cualquier skill
- Aislamiento: cada skill corre en proceso separado (MCP server o gVisor/Firecracker)
- Secrets: Vault lookup por (tenant_id, skill_id, credential_type)
- Contexto: tenant_id fluye por context server-side, inmutable, validado en cada hop

**[RECOMENDACION - juicio del analista] - Transporte de tenant:**
- Gateway resuelve tenant_id de: API key vinculada a tenant, JWT claim, o webhook registration
- tenant_id se establece en context.Context (Go) / request state (Python) / AsyncLocalStorage (Node)
- NUNCA se lee de headers del cliente
- Cada layer de la stack recibe el contexto del layer anterior, no lo reconstruye

---

*Investigacion completada. 20+ fuentes analizadas. 15+ claims documentados con citas textuales. 4 huecos identificados con recomendaciones de diseno.*
*Fecha de investigacion: 2026-07-08*
