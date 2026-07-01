# ENT_FABERLOOM_INSIGHTS_KIMI_EMAIL — Insights Estratégicos Kimi Swarm (Email + Conectividad)
id: ENT_FABERLOOM_INSIGHTS_KIMI_EMAIL
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: ENT
stamp: VIGENTE — 2026-04-17
aprobador: CEO
aplica_a: [FaberLoom, MWT]
relacionado: ENT_FABERLOOM_INSIGHTS_KIMI.md · SPEC_FABERLOOM_MVP.md · SPEC_MWT_AGENT_PLATFORM.md · ARCH_AGENT_PRINCIPLES.md

---

## Contexto

Segunda investigación Kimi Swarm. Foco: email corporativo, mensajería, automatización de
workflows y conectividad multi-canal (e-commerce + LLM). 14 dimensiones, 14+ research tracks,
análisis cruzado entre 30+ búsquedas independientes por dimensión.

**Fuente:** `Kimi_Agent_Corporate Email Integration.zip` — análisis recibido 2026-04-17.
**Complementa:** ENT_FABERLOOM_INSIGHTS_KIMI (primera investigación — arquitectura de agentes).

---

## INSIGHT E01 — n8n Tiene MCP Nativo desde Nov 2025 (RESUELVE CONFLICTO PREVIO)

**Confianza:** Alta (documentación oficial + 3 fuentes independientes)
**Aplica a:** FaberLoom · MWT

**Hallazgo:**
n8n lanzó soporte MCP nativo en noviembre 2025 (v1.120+) en **tres modos**:

| Modo | Dirección | Descripción |
|------|-----------|-------------|
| Instance-Level MCP | n8n como servidor | Instancia completa expuesta como MCP server; workflows elegibles = tools |
| MCP Server Trigger Node | n8n como servidor (por workflow) | Workflow individual se convierte en MCP server custom |
| MCP Client Node | n8n como cliente | n8n consume herramientas de MCP servers externos |

**Limitaciones críticas del modo MCP en n8n:**
- Timeout de 5 minutos para ejecuciones MCP
- Solo un trigger por workflow visible al cliente MCP
- No soporta input binario
- **No soporta human-in-the-loop** (multi-stage interaction)
- Workflows MCP deben ser "fast, deterministic, fully automatable"

**Implicación:** La nota ⚠️ CONFLICTO en SPEC_MWT_AGENT_PLATFORM y ENT_FABERLOOM_INSIGHTS_KIMI
(que decía "n8n no expone MCP nativo") queda **parcialmente resuelta** pero con matiz:
n8n SÍ expone MCP nativo para flujos automatizados. Sin embargo, los flujos HITL (draft-first,
aprobación humana) no pueden correr como herramientas MCP directas — requieren el patrón webhook.
La arquitectura correcta para FaberLoom es MCP para flujos automáticos + webhook para HITL.

**Acción:** Actualizar SPEC_MWT_AGENT_PLATFORM.md y ENT_FABERLOOM_INSIGHTS_KIMI.md para reflejar
esta resolución parcial.

---

## INSIGHT E02 — Protocol Gap LATAM: 12-18 Meses de Ventana de Primer Mover

**Confianza:** Alta
**Aplica a:** FaberLoom

**Hallazgo:**
MCP se ha consolidado como estándar universal (97M descargas/mes del SDK, 10,000+ servidores
públicos). Solo **MercadoLibre y QuickBooks** tienen MCP servers oficiales en LATAM. Los sistemas
contables dominantes carecen completamente de conectores:

| Sistema | País | API REST | MCP Server | Camino |
|---------|------|----------|------------|--------|
| MercadoLibre | 18 países | Sí | **Sí (oficial)** | Nativo |
| Siigo | CO/MX | Sí | Vía Konvex | Wrapper |
| Alegra | CO/MX/PE | Sí | Vía Konvex | Wrapper |
| ContaAzul | BR | Sí | No | Custom |
| CONTPAQi Nube | MX | Parcial | No | Custom |
| Aspel | MX | **No** | No | SDK C# / DB directa |
| Bind ERP | MX | Sí | No | Custom |
| SAP Business One | Global | Sí | No | Custom |

**Konvex** es la única solución LATAM con API REST unificada + MCP Server propio para Siigo,
Alegra, NetSuite y QuickBooks. Reporta 80% de ahorro en tiempo de integración.

**Estrategia:** FaberLoom adopta Konvex para sistemas ya soportados; construye MCP servers custom
para Aspel (Firebird read-only + CSV write) y sistemas fuera del alcance de Konvex.

**Ventana temporal:** 12-18 meses antes de que los propios vendors lancen conectores oficiales.
Una vez los agentes de terceros dependen de los MCP servers de FaberLoom → switching cost sube.

---

## INSIGHT E03 — Paradoja del Email: Gratis pero Complejo vs Abstracción Pagada

**Confianza:** Alta
**Aplica a:** FaberLoom

**Hallazgo:**
Gmail API y MS Graph API son **gratuitas** pero requieren infraestructura significativa.
IMAP/SMTP es universal pero complejo de operar a escala. Las "Universal Email APIs" cobran por simplificar:

| Servicio | Modelo | Costo (100 cuentas) | Self-hosted | Recomendación |
|---------|--------|---------------------|-------------|----------------|
| Gmail API | Gratuita | $0 API + $70-90/mes Workspace | No | MVP + clientes GW |
| MS Graph | Gratuita | $0 API + $36-62/mes M365 | No | MVP + clientes M365 |
| EmailEngine | Licencia fija | ~$35-60/mes (VPS + Redis) | Sí | **Recomendado** para IMAP |
| Nylas | SaaS | ~$165/mes ($15 + 100×$1.50) | No | Evitar a escala |
| ATAT | Open source | $0 infra | Sí | Solo referencia |

**M365 más barato que Google Workspace en LATAM:**
- M365 Business Basic: COP $15,200 (~$3.58 USD/mes CO), MXN $68 (~$3.78 USD/mes MX)
- Google Workspace Business Starter: ~$7-14 USD/mes
- Para PYMEs tradicionales, M365 es 2-4× más barato. Favorece adopción.

**Arquitectura recomendada:**
- Prioridad MVP: Gmail API (MCP connector #1 de Claude) + MS Graph (unificado email+cal+contactos)
- IMAP universal (v1.0): EmailEngine self-hosted, no Nylas
- Relay de salida: Amazon SES (bulk, $0.10/1K) + Postmark (críticos, mejor deliverability)

**Nota crítica MS Graph:**
- Webhooks expiran cada 7 días, requieren HTTPS con respuesta < 3 segundos
- TLS 1.2 obligatorio para validación (TLS 1.3 no funciona confiablemente)
- Admin del tenant M365 debe dar consentimiento una vez → fricción de onboarding

---

## INSIGHT E04 — WhatsApp Tax vs Telegram Hack: Arquitectura Híbrida

**Confianza:** Alta
**Aplica a:** FaberLoom · MWT

**Hallazgo:**
WhatsApp ($0.014-$0.102 por conversación según país) es el "tax" de LATAM — necesario para
clientes externos pero costoso. Telegram ($0, 210M usuarios LATAM) es el "hack" para operaciones
internas donde se controla la adopción.

**Arquitectura óptima:**
```
Canal externo (clientes):     WhatsApp Business API
Canal interno (equipo/HITL):  Telegram Bot API (gratuito)
```

**Cálculo de ahorro:** 500 conversaciones/día CO = ~$210/mes en WhatsApp.
Si 40% son internas (aprobaciones, alertas, escalaciones) → mover a Telegram ahorra ~$84/mes/cliente.
A escala de 100 clientes → $8,400/mes de ahorro en infraestructura.

**Para FaberLoom:** El canal de aprobación HITL (notificaciones draft-first) debe ser Telegram,
no WhatsApp. El agente envía el borrador por Telegram al operador; el operador aprueba/rechaza
con botones; el agente ejecuta. Costo adicional = $0.

**Para MWT:** Validar si los distribuidores aceptan Telegram para comunicación interna del equipo
MWT. Canal externo con clientes Marluvas/Tecmater permanece en WhatsApp.

---

## INSIGHT E05 — Stack de los $150: Unit Economics desde el Cliente #1

**Confianza:** Media (depende de optimización y volumen real)
**Aplica a:** FaberLoom

**Hallazgo:**
El stack completo de FaberLoom tiene costos de infraestructura muy inferiores a los competidores
(Zapier + servicios cloud = $50-100/cliente/mes en infra). Con stack open-source + AWS:

| Fase | Stack | Costo/mes | Margen (precio $50-100/cliente) |
|------|-------|-----------|----------------------------------|
| MVP (60d) | Gmail + Telegram + n8n + Claude Bedrock | ~$60 | 80%+ |
| v1.0 (6m) | + Graph + WhatsApp + Slack + SP-API | ~$210 | 75-80% |
| v2.0 (12m) | + MCP servers LATAM + TikTok + Walmart | ~$410 | 70-75% |

**Costo por cliente:** ~$2-10/mes a volumen normal de PYMEs 5-50 empleados.

**Desglose MVP:**
- n8n self-hosted: €10/mes
- Claude API vía Amazon Bedrock: ~$50/mes
- AWS SES: $0.10/1,000 emails
- Telegram: $0
- Gmail API: $0
- Total: ~$60/mes para 5-10 clientes piloto

---

## INSIGHT E06 — Divergencia LLM: No Hay Write Once Run Anywhere

**Confianza:** Alta
**Aplica a:** FaberLoom

**Hallazgo:**
MCP es protocolo abierto adoptado por Claude, ChatGPT y Gemini. Pero cada plataforma tiene
capas propietarias no interoperables:

| Plataforma | Capa propietaria | Relevancia FaberLoom |
|-----------|-----------------|---------------------|
| Claude | MCP Apps + iframes interactivos | Mejor soporte MCP nativo |
| ChatGPT | GPT Store (159K+ GPTs) | Acceso a mercado masivo |
| Gemini | Workspace Extensions nativas | Integración nativa G Suite |

**Decisión:** No invertir en abstracciones LLM-agnósticas ahora — es prematuro.
Estrategia: Core en Claude (mejor MCP), conectores específicos para Gemini en clientes G Suite.

---

## INSIGHT E07 — Amazon SP-API: Moat Inverso para PYMEs

**Confianza:** Alta
**Aplica a:** FaberLoom · MWT (Rana Walk)

**Hallazgo:**
Amazon distingue entre "private apps" (self-authorize por seller, **exentas de fees**) y
"public apps" (multi-tenant, $1,400/año + usage fees).

**Modelo correcto para FaberLoom:**
- Cada cliente configura su propia LWA app (self-authorize = private app = $0)
- FaberLoom NO centraliza el acceso SP-API
- Más fricción de onboarding pero costo = $0 vs $1,400/año + variables

**Aplicación MWT:** Rana Walk ya debe operar como private app. Confirmar configuración.
SP-API fees retrasados indefinidamente desde 2024 — pero el modelo private preserva
independencia de cambios de política de Amazon.

---

## INSIGHT E08 — Draft-First + HITL: 94% Approval Rate en Producción

**Confianza:** Alta
**Aplica a:** FaberLoom · MWT

**Hallazgo:**
Datos de sistemas HITL en producción (email intelligence):
- **94%** de borradores aprobados sin cambios
- **6%** rechazados
- **22%** de las aprobaciones incluyen modificaciones menores
- **Mediana de respuesta:** 8 minutos

Este patrón aparece en email, Slack, Teams, WhatsApp y SP-API — es universal, no específico
al canal.

**Nivel de aprobación por tipo de acción:**

| Acción | Riesgo | Aprobación requerida |
|--------|--------|---------------------|
| Lectura + clasificación | Bajo | No |
| Creación de borrador | Medio | Condicional |
| Envío individual | Medio | Sí |
| Envío masivo >10 destinatarios | Alto | Obligatoria |
| Eliminación de emails | Alto | Obligatoria |
| Modificación de etiquetas | Bajo | No |

**Implicación para ARCH_AGENT_PRINCIPLES P3 (Draft-first absoluto):** Los datos confirman que
el patrón es el correcto. El riesgo a resolver no es que el agente sea malo (94% OK) sino que
el humano deje de leer (complacency_score → Oscillation Counter, I04 de Kimi #1).

---

## INSIGHT E09 — n8n como Capa de Orquestación Universal (con Clarificación HITL)

**Confianza:** Alta
**Aplica a:** FaberLoom · MWT

**Hallazgo:**
n8n v1.120+ cumple 5 funciones de orquestación:
1. Consumir MCP servers externos (MCP Client Node)
2. Exponer workflows como MCP tools (Instance-Level / MCP Server Trigger)
3. Actuar como webhook gateway multi-fuente (Switch Node para enrutamiento)
4. Implementar colas de escalación async (Queue Mode)
5. Conectar con 400+ servicios sin código custom

**Arquitectura de FaberLoom con n8n:**
```
Triggers → n8n Switch Node
                ↓
    [Email]  [WhatsApp]  [Telegram]  [MercadoLibre]
                ↓
    n8n AI Agent Node (invoca Claude vía MCP)
                ↓
    Draft generado → Cola aprobación Telegram (HITL)
                ↓
    Aprobado → n8n ejecuta acción en sistema externo
```

**Clarificación HITL:** Los workflows MCP de n8n (timeout 5 min, sin HITL) manejan acciones
automatizables. El ciclo de aprobación humana corre como workflow separado con trigger webhook
(Telegram callback) — fuera del modo MCP. Ambos flujos coexisten en n8n.

**Para MWT:** n8n es el orquestador actual. La actualización a v1.120+ desbloquea MCP nativo
para skills automatizables (SKILL_KB_AUDITOR, SKILL_DEMAND_FORECASTER) sin cambiar la arquitectura
de base.

---

## INSIGHT E10 — TikTok Shop LATAM: Ventana de 12-18 Meses

**Confianza:** Media (depende de adopción en LATAM)
**Aplica a:** FaberLoom

**Hallazgo:**
TikTok Shop en expansión agresiva en MX, BR, CO, CL, PE. Partner API v2 es moderna (OAuth +
request signing). El ecosistema de tools para TikTok Shop en LATAM está casi vacío — perfil
ideal: sellers PYMEs jóvenes, técnicamente adeptos.

**A diferencia de Amazon:** SP-API fees inciertos, ecosistema saturado de herramientas.
TikTok Shop = virgen en LATAM + API moderna + sellers sin herramientas de optimización.

**Posición:** Feature post-MVP (v2.0, mes 12+). Target: sellers multi-canal Amazon + TikTok.

---

## Tabla de Prioridad de Acción

| Insight | Prioridad | Acción inmediata |
|---------|-----------|-----------------|
| E01 — n8n MCP nativo | **Crítica** | Actualizar SPEC_MWT_AGENT_PLATFORM + ENT_KIMI_INSIGHTS (nota conflicto → resuelta con matiz) |
| E02 — Protocol Gap LATAM | **Alta** | Evaluar Konvex; reservar esfuerzo para MCP server Siigo/Alegra en v2.0 |
| E03 — Email stack | **Alta** | Usar Gmail + Graph en MVP; EmailEngine (no Nylas) para IMAP |
| E04 — WA Tax vs Telegram | **Alta** | HITL notifications → Telegram; WhatsApp solo para clientes externos |
| E05 — Unit economics | Media | Validar con 5 clientes piloto; confirmar costo real vs estimado |
| E07 — SP-API private | **Alta** | Confirmar que Rana Walk es private app (MWT) y FaberLoom usa self-authorize por cliente |
| E08 — HITL 94% | Media | Confirmar métricas en primeros clientes; ajustar si diverge |
| E09 — n8n orquestación | Media | Actualizar a n8n v1.120+; separar flujos MCP (auto) de webhook (HITL) |
| E10 — TikTok Shop | Baja | Feature en roadmap v2.0; no bloquea MVP |

---

## Conflictos Resueltos vs Persistentes

| Conflicto | Resolución |
|-----------|------------|
| n8n no tiene MCP nativo | **RESUELTO (parcial):** n8n v1.120+ tiene MCP nativo para flujos automáticos. HITL sigue requiriendo webhook. |
| n8n bidireccionalidad solo via webhook | **MATIZADO:** Bidireccionalidad MCP nativa existe pero con limitación de 5 min y sin HITL. Webhook es oblig