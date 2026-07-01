# SPEC_FABERLOOM_MVP — Plan de Validación 60 Días
id: SPEC_FABERLOOM_MVP
version: 1.2
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: SPEC
stamp: VIGENTE — 2026-04-28
aprobador: CEO
fuente: Investigación Kimi Swarm + ARCH_AGENT_PRINCIPLES + Kimi #3 Ruflo (4 gaps) + sesión Data Classification + Pricing Tiers + Audit Module
aplica_a: [FaberLoom]
relacionado: ENT_FABERLOOM_INSIGHTS_KIMI.md · docs/faberloom/ENT_FB_INSIGHTS_KIMI_RUFLO_v1.md · SPEC_AUTONOMY_CONTROL_ENGINE.md · SPEC_LLM_ROUTING_ARCHITECTURE.md · SPEC_ACTION_ENGINE.md (D9, D10) · SPEC_AUDIT_MODULE.md · POL_DATA_CLASSIFICATION.md · docs/faberloom/ENT_FB_PRICING_TIERS_v1.md · ARCH_AGENT_PRINCIPLES.md (P14)

---

## Declaración

El MVP de FaberLoom tiene dos objetivos indivisibles:

1. **Validación conductual**: una PYME B2B real delega tareas operativas a un agente y
   percibe ROI medible en 30 días calendario.

2. **Core loop estable**: consulta → KB → acción propuesta → HITL → aprendizaje → mejora.
   Este ciclo genera el activo defensivo: gold samples validados por cliente, no transferibles.

**Restricción crítica:** un MVP que supera 16 semanas no es un MVP — es un producto completo.
Target: 8 semanas (60 días). La ventana de mercado es 18-24 meses (I05).

---

## Foco del MVP

**Un agente, 3-5 herramientas, 2 workflows:**

| Workflow | Por qué primero | Métrica de dolor |
|----------|----------------|-----------------|
| Cobranza y recordatorios | 51% de LATAM reporta dificultades para cobrar a tiempo | Ciclo cobro 45-67 días; morosidad 31.4% promedio |
| Proformas y cotizaciones | 15-30 min manual vs <5 min automatizado | Repetición diaria, error frecuente |

**No se construye multi-agente en MVP.** Tres pilares de evidencia verificable
(actualizados v1.1 post Kimi #3 Ruflo, ver ENT_FABERLOOM_INSIGHTS_KIMI_RUFLO §I-RUFLO-07):

1. MAST (UC Berkeley, NeurIPS 2025 Spotlight) — 41-86.7% tasa de fallo en multi-agente
   sobre 1,642 trazas, 14 modos de fallo, Cohen's Kappa = 0.88.
2. Single-agent iguala multi-agent en razonamiento multi-hop bajo igual presupuesto
   de tokens (NeurIPS 2025, argumento information-theoretic vía Data Processing Inequality).
3. Confiabilidad compuesta degrada exponencialmente: 10 handoffs al 99% = 90.4%;
   20 handoffs al 95% = 35.8%. Costo multi-agente 2-5× tokens.

Gartner (2027 prediction): 40% de proyectos agentic AI cancelados — usado como
contexto de mercado, no como evidencia técnica directa. Un equipo de 1-3 devs no
puede depurar coordinación inter-agente mientras valida hipótesis de mercado
simultáneamente.

---

## Stack Técnico

| Componente | Tecnología | Función | Costo/mes |
|------------|------------|---------|-----------|
| Backend API | FastAPI + Pydantic AI | Orquestación agente, endpoints REST | $0 |
| Base de datos | Supabase (PostgreSQL + pgvector + RLS) | Datos, vector search, auth, multi-tenant | $0-25 |
| Gateway LLM | LiteLLM | Routing proveedores, rate limiting, token tracking | $0 |
| Frontend | Next.js 15 | Consola web admin, HITL approval UI | $0 |
| Cola de tareas | ARQ + Redis | Workflows async, retries | $0-20 |
| Canal primario | WhatsApp Business API | Interacción agente-usuario (72% LATAM) | $0-50 |
| Hosting | Railway / Fly.io | Backend + frontend + workers | $20-50 |
| Observabilidad | Langfuse + logging estructurado | Trazabilidad, cost tracking | $0-50 |
| **Total** | | | **$70-195** |

**Notas críticas del stack:**
- Fijar versiones exactas en poetry.lock y pnpm-lock.yaml desde el inicio
- 20-30% del esfuerzo de desarrollo a observabilidad y guardrails — no como complemento
- RLS de Supabase como argumento de ventas: "cada cliente tiene su espacio aislado"
- Benchmark pgvector + RLS antes de escalar a 100+ tenants (ver I06)

**Alternativas de respaldo:**
- FastAPI → Django Ninja si el equipo requiere baterías incluidas
- ARQ → Celery + RabbitMQ si se requiere mayor madurez
- WhatsApp → Telegram Bot API como respaldo inmediato

---

## Plan por Semanas

### Semanas 1-2: Fundación técnica + primer workflow (cobranza)

**Entregables:**
- Stack completo desplegado (FastAPI + Supabase + ARQ + Next.js + LiteLLM)
- Pipeline de 8 fases operativo: recepción WhatsApp → KB → acción → HITL → log
- Workflow cobranza end-to-end: recibir instrucción, consultar facturas vencidas,
  generar mensajes personalizados, presentar para aprobación humana antes de envío
- Consola web mínima: historial de tareas, aprobación/rechazo, métricas básicas
- Prompt estructurado para caching (static-first: system prompt + KB al inicio)

**Criterio de éxito:** el agente completa el flujo de cobranza de principio a fin
sin intervención técnica, con latencia < 5s para presentar el borrador al usuario.

### Semanas 3-4: KB Upload Wizard + segundo workflow (proformas)

**Entregables:**
- KB Upload Wizard: interfaz para subir documentos (listas de precios, condiciones
  comerciales, plantillas) con verificación de comprensión antes de usar en producción
- Workflow proformas: solicitud → consulta lista precios en KB → cálculo con reglas
  comerciales → borrador de proforma para aprobación
- HITL básico operativo: toda acción que implique envío a tercero requiere confirmación
  explícita (botón en WhatsApp o consola web)
- Señalización de confianza binaria HIGH/LOW (superior a porcentajes numéricos)

**Criterio de éxito:** dos workflows operan sin interferencias; gate humano funcional
sin generar fatiga de decisión.

### Semanas 5-6: Gold samples + optimización de costos

**Entregables:**
- Gold samples manuales: cada aprobación/corrección genera par (contexto, acción_corregida)
  almacenado en pgvector con outcome_score inicial
- Prompt caching configurado: system prompt + KB por tenant se cachea, break-even en 2 lecturas
- Routing básico por tiers: single-LLM con LiteLLM preparado para multi-LLM en Fase 3
- Observabilidad: task completion rate > 70% como umbral mínimo de calidad
- Logging estructurado de cada interacción agente-usuario

**Criterio de éxito:** costo de inferencia por conversación < $0.05 con caching activo.

### Semanas 7-8: Onboarding clientes beta + iteración

**Entregables:**
- 3-5 clientes beta en producción (criterios de selección: ver sección siguiente)
- Onboarding vía WhatsApp, no web app
- Ciclos de feedback de 48 horas: métricas cuantitativas + cualitativas
- Iteraciones rápidas basadas en feedback real

**Criterio de éxito:** métricas de validación (ver sección siguiente).

---

## Criterios de Selección de Clientes Beta

- PYMEs manufactureras B2B con procesos de cobranza y cotización manuales
- 5-50 empleados
- Disposición para dedicar ≥30 minutos semanales a dar feedback
- Un decisor con autoridad para aprobar/rechazar acciones del agente
- Sin CRM enterprise (Salesforce, Dynamics) — son el segmento no atendido
- Preferiblemente en Colombia, México o Costa Rica (compliance conocido)

---

## Métricas de Éxito del MVP

| Dimensión | Métrica | Umbral |
|-----------|---------|--------|
| Adopción | % clientes beta usando el agente ≥3 veces/semana | ≥ 70% |
| Confianza | % acciones aprobadas sin modificación (desde semana 4) | > 80% |
| Valor | Reducción tiempo en cobranza y proformas (auto-reportado) | ≥ 30% |
| Retención | % clientes beta que renuevan mes 2 (aunque sea gratis) | 100% |

**Regla crítica:** si un cliente beta no percibe valor suficiente para continuar gratis
en el mes 2, la hipótesis de producto requiere revisión fundamental, no ajustes incrementales.

---

## Roadmap Post-MVP (12 meses)

| Fase | Período | Entregable principal |
|------|---------|---------------------|
| Fase 1 | Mes 1 | Pipeline 8 fases + routing single-LLM + KB + consola |
| Fase 2 | Mes 2 | Task Authorization IBAC + async escalation queue + 2 workflows |
| Fase 3 | Mes 3 | Routing multi-LLM por tiers + TokenLedger + prompt caching |
| Fase 4 | Meses 4-5 | Motor autonomía ImpactVector + Promotion Engine + ECE/Brier + Oscillation Counter |
| Fase 5 | Meses 5-6 | Gold samples + OutcomeLedger + UserControlProfile + cross-skill propagation |
| Fase 6 | Meses 7-12 | Agentes delegados + ModelFingerprint + seguridad 6 capas + compliance 4 países |

**Priorización por ROI (top 8 antes de Fase 4):**

| # | Funcionalidad | Valor | Esfuerzo | Secuencia |
|---|--------------|-------|----------|-----------|
| 1 | HITL con checkpoint-resume | Crítico | 2 sem | Fase 2 |
| 2 | Prompt caching Anthropic | Alto | 1 sem | Fase 3 |
| 3 | Workflows cobranza + proformas | Crítico | 3 sem | Fase 2 |
| 4 | Consola web + confianza binaria HIGH/LOW | Alto | 2 sem | Fase 1 |
| 5 | WhatsApp Business API | Alto | 1 sem | Fase 1 |
| 6 | IBAC + Task Authorization | Alto | 2 sem | Fase 2 |
| 7 | Routing multi-LLM por tiers | Alto | 3 sem | Fase 3 |
| 8 | TokenLedger | Medio-Alto | 1 sem | Fase 3 |

Las primeras 8 funcionalidades concentran 80% del valor percibido al 40% del esfuerzo total.

---

## Riesgos Críticos (top 5)

| Riesgo | Dato | Mitigación |
|--------|------|------------|
| Hallucination cascades | MAST: 41-86.7% tasa de fallo en multi-agente (NeurIPS 2025, 1,642 trazas) — single-agent en MVP elimina el riesgo en origen | Observabilidad desde día 1, golden sets de evaluación, single-agent obligatorio en MVP |
| Prompt injection | 84% tasa de éxito de ataque | Draft-first absoluto (P3), nunca envío externo sin aprobación |
| Runaway costs | Sin routing multi-LLM el margen se erosiona | Caching desde semana 5, routing básico en Fase 3 |
| Trust collapse | Un error irreversible destruye relación con PYME | HITL en todo lo que toca al cliente, señalización HIGH/LOW |
| Technical debt | Gartner: 40% de proyectos agentic AI cancelados para 2027 | Stack versiones fijas, 20-30% esfuerzo a observabilidad, P14 deterministic-first reduce superficie LLM |

---

## Principios que Gobiernan el MVP

Aplican todos los ARCH_AGENT_PRINCIPLES, con énfasis en:
- **P3 Draft-first absoluto**: nunca envío externo sin aprobación humana — sin excepción
- **P2 Contexto mínimo**: el agente carga solo lo declarado en kb_refs, no toda la KB
- **P9 Gobernanza embebida**: los gates de seguridad son parte del flow, no una capa encima
- **P14 Deterministic First**: regex/parsers XML ANTES de LLM call. Tier 0 obligatorio en MVP.

---

## Tier 0 obligatorio (post Kimi #3 Ruflo)

Antes del L1 Haiku clasificador, todo request pasa por Tier 0 determinístico:

| Capa | Implementación | Latencia | Costo |
|---|---|---|---|
| Tier 0 (regex + parsers XML LATAM) | `tier0.py` middleware FastAPI + LiteLLM pre-call hooks + Pydantic validation | ~5-50 μs | $0 |
| L1 Haiku (clasificador) | Solo si Tier 0 retorna `confidence < threshold` o caso no cubierto | ~750-1,100 ms | $0.00012-0.00038/req |
| L2 Dispatcher | Solo tasks que requieren modelo más capaz | varía por modelo | varía |
| Human Gate | Tools con `requires_approval=True` | minutos | tiempo humano |

**14 reglas concretas para sprint 1:**
- Parsers XML por país: DIAN (UBL 2.1 Colombia), SII (DTE Chile), SAT (CFDI 4.0 México), AFIP (Argentina), SEFAZ (NFe Brasil)
- Validación TIN por país (NIT, RUT, RFC, CUIT, CNPJ)
- Extracción email con regex compilado
- Validación de monto con currency code
- Detección de moneda en texto libre
- Parser de fechas en formatos LATAM (dd/mm/yyyy)
- Detección de número de factura por patrón
- Más 5 reglas por workflow específico (cobranza/proformas)

**Mantenimiento:** ~1 día/trimestre por cambios fiscales LATAM. Schemas DIAN/SII/SAT/AFIP/SEFAZ se actualizan con frecuencia variable. Asignar bug-bash ritualizado al cierre de cada sprint con 20 docs reales por país.

**Cobertura proyectada:** 60-80% de tasks simples resueltas en Tier 0 (Kimi #3 dim01-02). Reducción de costos LLM 40-95% sobre baseline.

**Spot-check pendiente antes de comprometer:** validar `60-80%` contra muestra real de 20 docs Marluvas/Tecmater. Si cobertura real <50%, reducir scope a top 5 reglas.

---

## Diferenciador competitivo: Tiers de confidencialidad + Cost-mode

PYME LATAM hoy elige entre Claude.ai / ChatGPT / Gemini directos, donde ya acepta transferencia internacional. FaberLoom NO compite en "data residency LATAM" — compite en:

1. **Multi-modelo orquestado** vs un solo proveedor (Action Engine routing).
2. **Memoria cross-sesión per-cliente** (gold samples, OutcomeLedger).
3. **Workflow B2B específico** (cobranza, proformas, AR/AP).
4. **DPA chain consolidada** — un solo DPA con FaberLoom vs N DPAs con N providers.
5. **Tiers de confidencialidad como producto** — Starter / Pro / Enterprise / Government con audit creciente.
6. **Cost-mode opt-in** para data N0/N1 — habilita DeepSeek/Kimi self-host con ahorro hasta 70%.

Costo blended estimado por perfil de cliente (vs Claude.ai puro):

| Cliente | Distribución | Costo blended | Vs Claude.ai |
|---|---|---|---|
| Conservador (default mode) | 100% US/EU | ~$25/mes Sonnet equiv | igual |
| Mixto (default + cost-mode) | 70% US/EU + 30% China-self-host | ~$15/mes | **40% más barato** |
| Agresivo (cost-mode máximo) | 30% US/EU (PII) + 70% China | ~$8/mes | **70% más barato** |

Ver `docs/faberloom/ENT_FB_PRICING_TIERS_v1.md` para estructura completa.

Métrica MVP: **% de Pro/Enterprise upsell** desde Starter en primeros 60 días.

---

Changelog:
- v1.2 (2026-04-28): +Diferenciador competitivo Tiers + Cost-mode. +Refs SPEC_ACTION_ENGINE D9/D10, POL_DATA_CLASSIFICATION, ENT_FABERLOOM_PRICING_TIERS, SPEC_AUDIT_MODULE. Cuadro costo blended vs Claude.ai. Origen: indexa hallazgos data classification + audit module + pricing tiers.
- v1.1 (2026-04-27): Argumentación contra multi-agente actualizada con MAST (NeurIPS 2025) reemplazando "87% en 4h" no verificable. +Sección Tier 0 obligatorio. +P14 en énfasis. Origen: Kimi #3 Ruflo. CZ-001 resuelta — ver ENT_FABERLOOM_INSIGHTS_KIMI_RUFLO §I-RUFLO-07.
- v1.0 (2026-04-17): Creación. Plan 60 días, stack técnico con alternativas, métricas de éxito.