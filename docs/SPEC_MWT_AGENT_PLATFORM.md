# SPEC_MWT_AGENT_PLATFORM — MWT como Plataforma de Agentes
id: SPEC_MWT_AGENT_PLATFORM
version: 1.1
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
type: SPEC
stamp: VIGENTE — 2026-04-17
aprobador: CEO
aplica_a: [MWT]
relacionado: ARCH_AGENT_PRINCIPLES.md · SKILL_RUNTIME.md · SPEC_AUTONOMY_CONTROL_ENGINE.md · SPEC_FABERLOOM_MVP.md · ENT_FABERLOOM_INSIGHTS_KIMI_EMAIL.md

---

## Declaración

MWT tiene **tres componentes independientes** que se relacionan pero no se mezclan:

```
MWT Knowledge Hub  →  Claude/Cowork  (fuente de verdad, KB, skills, arquitectura)
        ↓ diseño, principios, gold samples
   ┌────┴────┐
mwt.one    FaberLoom
(stack      (stack
 propio)     propio)
```

**MWT Knowledge Hub:** La KB de 279 archivos que corre en Claude/Cowork. Es el cerebro —
diseño de arquitectura, skills, gold samples, documentación operativa. El CEO (Álvaro)
lo opera directamente. No tiene runtime de agentes propio — es conocimiento estructurado.

**mwt.one:** Plataforma operativa de MWT. Stack independiente, agentes con identidad MWT
(no Claude), single-tenant. Consume el conocimiento del Hub vía pgvector.

**FaberLoom:** SaaS multi-tenant para PYMEs B2B LATAM. Stack independiente, agentes con
identidad Faber (no Claude). Comparte arquitectura fundacional con mwt.one pero son
codebases, deployments y bases de datos separadas.

Este documento define la arquitectura de **mwt.one**. El Knowledge Hub se documenta
implícitamente en toda la KB. FaberLoom se documenta en SPEC_FABERLOOM_MVP.md.

---

## Diferencias clave: mwt.one vs FaberLoom vs Knowledge Hub

| Dimensión | MWT Knowledge Hub | mwt.one | FaberLoom |
|-----------|-------------------|---------|-----------|
| Runtime | Claude/Cowork | FastAPI + LiteLLM | FastAPI + LiteLLM |
| Identidad del agente | Claude (visible para CEO) | Agente MWT (propio) | Faber (propio) |
| Tenants | 1 | 1 | N organizaciones |
| Usuarios | 1 (CEO) | 1 (CEO) | N por organización |
| LLM | Anthropic directo | Anthropic vía LiteLLM | Anthropic vía LiteLLM |
| KB storage | Markdown 279 archivos | pgvector (embeddings del Hub) | pgvector + PostgreSQL |
| Multi-tenant isolation | No aplica | No aplica | RLS por org |
| WhatsApp | No | Canal B2B (Marluvas/Tecmater) | Canal primario onboarding |
| Pricing / billing | No aplica | No aplica | $29-39/mes flat |
| Compliance | No aplica | CR — Ley 8968 | CO + MX + CR + PA |
| Autonomía máxima | No aplica | PROPONE → AUTO_NOTIFICA | Todos los niveles |

---

## Stack de mwt.one

```
Capa de interacción:
  FastAPI               → runtime de agentes MWT (identidad propia, no Claude)
  LiteLLM               → routing a Anthropic API (Claude invisible para operaciones)
  WhatsApp Business API → canal B2B con clientes (Marluvas, Tecmater, distribuidores)
  Telegram Bot          → canal HITL — aprobaciones CEO, notificaciones internas

  [Nota: MWT Knowledge Hub (Claude/Cowork) es componente separado — opera
   en paralelo como herramienta del CEO, no como runtime de mwt.one]

Capa de automatización:
  n8n (>= v1.120)       → orquestación, webhooks, integración de servicios
                          MCP nativo para flujos automáticos
                          Webhook para flujos HITL (aprobación CEO)

Capa de datos:
  pgvector              → embeddings KB — retrieval semántico sobre Knowledge Hub
  Google Drive          → documentos operativos, proformas, reportes
  PostgreSQL            → estado operativo, OutcomeLedger, UserControlProfile

Capa de negocio:
  Amazon SP-API         → ventas Rana Walk FBA (private app — sin fees)
  Helium 10             → research y monitoreo Amazon
  SAP (clientes B2B)    → sistema de clientes Marluvas/Tecmater (acceso vía agente)
```

**Nota sobre n8n (actualizada post-Kimi Email):** n8n v1.120+ (nov 2025) expone MCP nativo
en 3 modos: Instance-Level MCP, MCP Server Trigger Node, y MCP Client Node.
**Para flujos automatizables** (SKILL_KB_AUDITOR, SKILL_DEMAND_FORECASTER) → usar MCP nativo.
**Para flujos HITL** (drafts que requieren aprobación CEO) → webhook sigue siendo obligatorio.
Limitaciones MCP en n8n: timeout 5 min, sin human-in-the-loop, sin input binario.
Actualizar n8n a >= v1.120 para habilitar. Ver ENT_FABERLOOM_INSIGHTS_KIMI_EMAIL.md E01.

---

## Los 3 Objetos en MWT

### AgentSpec → `SKILL_*.md`
Cada skill es un AgentSpec: define qué es el agente, su trigger, su autonomy_ceiling,
sus kb_refs, su state machine y sus criterios de aprendizaje.

10 skills activos (todos en SHADOW):
- SKILL_AMAZON_OPS · SKILL_CLIENT_SERVICE · SKILL_COMPLIANCE_CHECKER
- SKILL_COPY · SKILL_DEMAND_FORECASTER · SKILL_EXPERIMENT_RUNNER
- SKILL_HUMANIZE_BRAND · SKILL_HUMANIZE_COMMS · SKILL_KB_AUDITOR
- SKILL_PROFORMA_BUILDER

### AgentRuntime → `SKILL_RUNTIME.md`
Dashboard único de estado operativo. Registra por skill:
estado actual, autonomía real, métricas acumuladas, temperatura de aprendizaje, memoria activa.

**Extensiones pendientes (de SPEC_AUTONOMY_CONTROL_ENGINE v1.1):**
- `oscillation_counter` por skill — contador de auto-aprobaciones consecutivas
- `human_alignment_score` por skill — calibración perceptual CEO

### AgentMemory → `SKILL_MEM_*.md`
Un archivo por skill, creado solo cuando hay gold samples confirmados por CEO.
Contiene: gold samples activos, patrones aprobados, correcciones recurrentes.

**Extensión pendiente:** OutcomeLedger por skill — tabla de uses/outcomes por gold sample.
Ver sección OutcomeLedger más abajo.

---

## pgvector en MWT

MWT usa pgvector para retrieval semántico sobre la KB de markdown. No es multi-tenant
(todo el índice es de MWT). No tiene el problema pgvector + RLS de FaberLoom.

**Arquitectura de retrieval:**
```
Query CEO / trigger skill
        ↓
L1 Classifier (intent, complexity, required_caps)
        ↓
pgvector similarity search sobre KB indexada
  → threshold > 0.85: shortcut al gold sample similar si existe
  → threshold 0.75-0.85: retrieval + generación
  → threshold < 0.75: escalación o búsqueda ampliada
        ↓
L3 Prompt Compiler: adapta contexto al modelo activo (Claude Sonnet 4.x)
        ↓
Generación → HITL (P3 Draft-first) → feedback → OutcomeLedger
```

**Pendiente técnico:** benchmark propio de latencia pgvector con la KB actual (277 docs).
Target: < 50ms para retrieval + compilación de contexto.

---

## WhatsApp en MWT

WhatsApp Business API está activo en MWT para comunicación B2B con:
- Distribuidores Marluvas / Tecmater (México → Colombia)
- Seguimiento de pedidos y proformas
- Cobranza y recordatorios

**Estado actual:** operación mayoritariamente manual. El agente puede proponer mensajes
(SKILL_CLIENT_SERVICE, SKILL_HUMANIZE_COMMS) pero el envío lo ejecuta el CEO.

**Roadmap de autonomía WhatsApp:**
```
Hoy:     CEO redacta y envía manualmente
Nivel 1: Agente propone borrador → CEO aprueba → CEO envía
Nivel 2: Agente propone → CEO aprueba → agente envía via n8n webhook
Nivel 3: Agente envía y notifica post-hecho (solo mensajes pre-aprobados de bajo impacto)
```

**Restricción P3 (Draft-first absoluto):** ningún mensaje sale sin aprobación CEO
hasta que el skill demuestre Approval rate > 80% durante ≥ 14 días. Sin excepción.

---

## Prompt Caching en MWT

El system prompt de cada skill + los kb_refs declarados son repetitivos entre sesiones.
Estructurar prompts static-first (context estático primero, query dinámica al final)
reduce costo 45-90% con break-even en 2 lecturas (I10 — Kimi).

**Acción inmediata:** revisar todos los SKILL_*.md y verificar que kb_refs esté declarado
al inicio del system prompt, antes de cualquier contenido dinámico.

---

## OutcomeLedger en MWT

A diferencia de FaberLoom (tabla PostgreSQL), MWT implementa OutcomeLedger como
sección en cada `SKILL_MEM_*.md`:

```markdown
## OutcomeLedger

| gold_sample_id | uses | approved | edited | rejected | avg_edit_distance | status |
|---------------|------|----------|--------|----------|-------------------|--------|
| GS-001        | 5    | 4        | 1      | 0        | 0.12              | active |
| GS-002        | 8    | 3        | 3      | 2        | 0.38              | degrading |
```

**Reglas de salud (igual que FaberLoom):**
```
approval_rate < 0.60 en últimas 10 uses  → "degrading", CEO notificado en SKILL_RUNTIME
approval_rate < 0.40 en últimas 5 uses   → "deprecated", retirar de retrieval
avg_edit_distance > 0.40                 → revisar si sigue siendo gold sample válido
```

El SKILL_KB_AUDITOR es responsable de detectar gold samples degradados en cada ciclo
de auditoría y reportarlos al CEO.

---

## UserControlProfile en MWT

Con un solo usuario (CEO), el UserControlProfile es simple: una sección en SKILL_RUNTIME.md
que registra las preferencias observadas del CEO por tipo de acción.

```
## UserControlProfile — CEO

| action_type              | preferred_level | confidence | sample_size | avg_approval_ms |
|--------------------------|----------------|------------|-------------|-----------------|
| proforma_draft           | PROPONE        | —          | 0           | —               |
| whatsapp_draft_cliente   | PROPONE        | —          | 0           | —               |
| kb_update_interno        | EJECUTA_INTERNO| —          | 0           | —               |
| reporte_amazon           | PROPONE        | —          | 0           | —               |

oscillation_counter:     0   (reset cada vez que CEO aprueba algo que normalmente era auto)
complacency_score:       —   (calculable cuando hay ≥ 20 aprobaciones con tiempo < 3s)
```

Este perfil se actualiza en SKILL_RUNTIME.md después de cada 20 ejecuciones por tipo.

---

## Oscillation Counter en MWT

Con un solo usuario, el riesgo de complacencia es real: el CEO puede desarrollar
el hábito de aprobar sin leer si el agente es bueno.

```
Por skill, el oscillation_counter se incrementa con cada auto-aprobación rápida (< 3s).
Al llegar a 20:
  → la siguiente propuesta del skill se marca como REQUIERE_REVISIÓN_EXPLÍCITA
  → se añade resumen de "qué hice" al inicio del output
  → oscillation_counter = 0
```

Implementación: campo en cada bloque de skill en SKILL_RUNTIME.md.

---

## Estado Actual de Autonomía — 10 Skills

Todos en SHADOW. Ninguno ha ejecutado aún.

| Skill | Ceiling | ImpactVector típico | Riesgo principal |
|-------|---------|---------------------|-----------------|
| SKILL_PROFORMA_BUILDER | PROPONE | customer_visible=0.9, financial_risk=0.7 | Margen CEO-ONLY nunca en output |
| SKILL_CLIENT_SERVICE | PROPONE | external_side_effect=0.8 | Mensaje a cliente sin aprobación |
| SKILL_HUMANIZE_COMMS | PROPONE | external_side_effect=0.8 | Ídem |
| SKILL_HUMANIZE_BRAND | PROPONE | customer_visible=0.6 | Copy fuera de brand |
| SKILL_COPY | PROPONE | customer_visible=0.6 | Compliance antes de publicar |
| SKILL_DEMAND_FORECASTER | PROPONE | financial_risk=0.5 | Forecast incorrecto → pedido errado |
| SKILL_AMAZON_OPS | EJECUTA_INTERNO | reversibility=0.3 | Cambio listing en producción |
| SKILL_COMPLIANCE_CHECKER | EJECUTA_INTERNO | data_sensitivity=0.6 | Falso negativo de compliance |
| SKILL_EXPERIMENT_RUNNER | EJECUTA_INTERNO | blast_radius=0.4 | Experimento sin gate PLB_EXPERIMENTACION |
| SKILL_KB_AUDITOR | AUTO_NOTIFICA | reversibility=0.1 | Ninguno — solo lectura + reporte |

**Orden de prioridad para primer ciclo SHADOW:**
1. SKILL_KB_AUDITOR — menor riesgo, mayor valor inmediato, único candidato a AUTO_NOTIFICA
2. SKILL_PROFORMA_BUILDER — mayor frecuencia de uso, gold sample golden example disponible
3. SKILL_DEMAND_FORECASTER — datos SAP disponibles, skill más complejo técnicamente

---

## Roadmap de Autonomía MWT

| Fase | Cuándo | Qué |
|------|--------|-----|
| Fase 0 — Ahora | Completado | 3 objetos implementados, todos skills en SHADOW |
| Fase 1 — Próxima | Ejecutar primer ciclo SHADOW (3 ejecuciones por skill top-3) |
| Fase 2 | Mes 1 | OutcomeLedger activo en SKILL_MEM_* de skills ejecutados |
| Fase 3 | Mes 1-2 | UserControlProfile con ≥ 20 samples por acción frecuente |
| Fase 4 | Mes 2-3 | Oscillation Counter operativo, primer skill promovido de SHADOW → PROPONE activo |
| Fase 5 | Mes 3+ | SKILL_KB_AUDITOR → AUTO_NOTIFICA si cumple criterios de promoción |
| Fase 6 | Mes 4+ | Benchmark pgvector + optimización prompt caching por skill |

---

## Lo que MWT Hereda de la Investigación Kimi

| Insight | Aplica a MWT | Implementación |
|---------|-------------|----------------|
| I03 Trampa Gold Sample | ✅ Directo | OutcomeLedger en SKILL_MEM_*.md |
| I04 Oscilador Confianza | ✅ Directo | oscillation_counter en SKILL_RUNTIME.md |
| I07 Fragilidad Stack | ✅ Directo | Fijar versión Claude Sonnet activa; ModelFingerprint |
| I08 Doblaje Calibración | ✅ Directo | HumanAlignmentScore en SKILL_RUNTIME.md |
| I10 Prompt Caching | ✅ Directo | Reestructurar SKILL_*.md para static-first |
| I11 WhatsApp | ✅ Ya activo | Roadmap de autonomía WhatsApp (ver arriba) |
| I02 Efecto Supabase | ⬜ No aplica | Single-tenant, no necesita RLS como diferenciador |
| I05 Ventana LATAM | ⬜ No aplica | No es producto comercial |
| I06 pgvector RLS | ⬜ Parcial | No hay RLS pero sí benchmark pendiente |
| I09 Patrón Primer Dólar | ✅ Conceptual | Gold samples de MWT = conocimiento tácito de operación |

---

## Pendientes Técnicos

| Pendiente | Prioridad | Quién |
|-----------|-----------|-------|
| Benchmark pgvector MWT — latencia retrieval con 277 docs | Media | CEO + Claude |
| Reestructurar SKILL_*.md para prompt caching (static-first) | Alta | Claude |
| Agregar oscillation_counter + human_alignment_score a SKILL_RUNTIME.md | Alta | Claude |
| Crear SKILL_MEM_*.md con OutcomeLedger para los 3 skills prioritarios | Media | Claude (post primer ciclo SHADOW) |
| Primer ciclo SHADOW: SKILL_KB_AUDITOR (3 ejecuciones documentadas) | Alta | CEO + Claude |

---

Changelog:
- v1.2 (2026-04-17): Corrección arquitectural fundamental — MWT tiene 3 componentes independientes:
  Knowledge Hub (Claude/Cowork), mwt.one (stack propio FastAPI+LiteLLM), FaberLoom (SaaS multi-tenant).
  mwt.one tiene identidad de agente propia (no Claude). Stack actualizado con FastAPI+LiteLLM+Telegram.
  Tabla comparativa extendida a 3 columnas. CEO confirmó separación.
- v1.1 (2026-04-17): Nota n8n actualizada — MCP nativo disponible desde v1.120 (nov 2025).
  Flujos automáticos → MCP; flujos HITL → webhook. Conflicto previo resuelto (parcial).
  Ref: ENT_FABERLOOM_INSIGHTS_KIMI_EMAIL.md E01.
- v1.0 (20