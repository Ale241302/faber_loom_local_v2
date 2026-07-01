# ENT_RESEARCH_FABERLOOM_KIMI_2026-04 — Research Kimi FaberLoom B2B Regulado
id: ENT_RESEARCH_FABERLOOM_KIMI_2026-04
version: 2.0
status: VIGENTE — REFERENCE (FaberLoom v2 multi-tenant)
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: ENT
stamp: VIGENTE — 2026-04-29f
aprobador: CEO (sesión Cowork 2026-04-29 + ajuste refs 2026-04-29f)
aplica_a: [FaberLoom]
relacionado: ENT_FB_RESEARCH_AGENT_ECOSYSTEM_2026-04.md (research general FB) · SPEC_FABERLOOM_AGENT_COMPOSITION_v1.md · SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md · docs/faberloom/ENT_FB_PRICING_TIERS_v1.md · SPEC_FB_AGENT_BUILDER_v1.md

---

## Propósito

Research específico del Kimi K2 swarm parallel (abril 2026) sobre **FaberLoom como SaaS multi-tenant para fabricantes**. Aplicable únicamente a FaberLoom — NO al builder MWT v1.

Separado deliberadamente de `ENT_RESEARCH_AGENT_ECOSYSTEM_2026-04.md` para evitar context bleed: insumos para MWT vs insumos para FB que requieren scopes evaluativos distintos.

---

## Origen

- Sesión Cowork 2026-04-29
- Lanzamiento: Kimi K2 swarm parallel, abril 2026
- Foco: FaberLoom B2B regulado multi-tenant
- Archivos crudos: `faberloom_research_*.md` en uploads del workspace

---

## 7 frentes investigados

1. Multi-tenant isolation en SaaS de agentes
2. Memory frameworks producción 2026
3. Policy-as-code para AI agents
4. Observabilidad y eval stack
5. Costos reales en producción
6. Compliance B2B regulado
7. Agent Specification Language standard

---

## 4 insights cruzados (alta confianza declarada por Kimi — autocrítica abajo)

| # | Insight | Confidence | Aplicabilidad MWT |
|---|---------|------------|---------------------|
| 1 | Agent Gateway unificado como primitiva arquitectónica única (OPA + tenant isolation + OTel + audit) | high | NO — MWT single-tenant no requiere gateway |
| 2 | TCO invertido — 90% LLM, 10% infra → optimizar tokens 10x más ROI que infra | high | sí, aplica también a MWT (decisión arquitectónica universal) |
| 3 | SKILL.md extensible como compliance carrier | high | parcial — MWT lo adoptó vía SCH_SKILL_MANIFEST_V2 sin la dimensión compliance enterprise |
| 4 | Brecha 12-18 meses entre frameworks y compliance | high | informa diferenciación de FB vs competencia |

---

## 7 decisiones desbloqueadas — solo para FB

| # | Decisión | Estado MWT |
|---|----------|------------|
| 1 | pgvector + RLS multi-tenant | NO aplica (MWT single-tenant) |
| 2 | OPA/Rego policy engine + MCP Gateway propio | NO aplica (MWT usa hooks Python) |
| 3 | Mem0 como memory layer primaria | NO aplica (MWT usa pgvector flat + tabla episodic) |
| 4 | Langfuse + Braintrust como observabilidad | parcial — MWT adoptó Langfuse, no Braintrust |
| 5 | Extender SKILL.md con namespace propio | adoptado en MWT vía `metadata.mwt.*` |
| 6 | API Anthropic hasta 5k invocaciones/día | adoptado en MWT |
| 7 | México LFPDPPP como compliance constraint principal LATAM | atención compartida — MWT vende a México con Marluvas/Tecmater |

---

## Autocrítica documentada del research Kimi

El research Kimi tiene tres áreas donde la confianza declarada por Kimi excede la evidencia disponible. Al evaluar para FaberLoom hay que ponderar:

1. **Mem0 como "ganador"** — claim de marketing en su propio benchmark LOCOMO. Track record B2B regulado real es corto. Adoptar con plan de salida documentado.

2. **Agent Gateway unificado** — "convergencia emergente" según Kimi, no consolidada en producción. Trade-off entre simplicidad operacional y separation of concerns no analizado a fondo. Vale como dirección, no como dogma.

3. **Brecha 12-18 meses entre frameworks y compliance** — la ventana puede cerrar más rápido (Microsoft AGT abril 2026 ya lo cierra parcialmente). La oportunidad existe pero más corta.

---

## Diferenciales sobrevivientes para FaberLoom (vs ChatGPT Workspace Agents 2026-04)

| Gap OpenAI Workspace Agents | Diferencial FaberLoom |
|------------------------------|------------------------|
| Lock-in OpenAI Codex cloud | model-agnostic (Claude / Kimi / open via LiteLLM) |
| Compliance LFPDPPP México / data residency LATAM ausente | constraint LFPDPPP-first desde diseño |
| Cliente fabricante industrial no es ChatGPT-native | UX vertical (wizards, no chat-first) |
| Sin integración ERP fabricantes (SAP B1, Bind, Aspel, Siigo) | capabilities verticales en catálogo |
| Pricing créditos volátil (post mayo 2026) | pricing predecible por outcome/tenant |
| Multi-tenant pool genérico | multi-tenant criptográfico B2B regulado |
| Dependencia internet + cloud OpenAI | self-hosted opcional |

Los 5 primeros son robustos a corto-medio plazo. Los 2 últimos son técnicos y replicables si OpenAI prioriza.

---

## Trigger para reactivar este research

Este documento queda **archivado** hasta que aparezca alguno de:

1. Prospect FaberLoom firmando LOI o carta de interés concreta
2. Demo concreto a fabricante industrial que generó interés repetido
3. Decisión explícita CEO de pivotar negocio a SaaS para fabricantes

Hasta entonces: NO usar como insumo para decisiones de MWT v1.

---

## Estado de este documento

Documento de **referencia archivada para FaberLoom**. No se actualiza salvo:

- Si Kimi (u otra herramienta) emite research adicional sobre estos temas FB
- Si breach o quiebre legal en algún framework recomendado
- Si cambia el panorama competitivo (ChatGPT Workspace Agents pricing, lanzamientos relevantes)
- Si se reactiva el proyecto FB

---

Stamp: VIGENTE — 2026-04-29 (saneamiento 2026-04-29d)

Changelog:
- v1.0 (2026-04-29d): creación. Extraído del archivo ENT_RESEARCH_AGENT_ECOSYSTEM_2026-04.md (que mezclaba research MWT + FB) durante saneamiento de KB para corregir context bleed entre proyectos. Solo contenido específicamente FaberLoom.
