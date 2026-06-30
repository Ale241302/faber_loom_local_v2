# ENT_GOB_DECISIONES — Registro de Decisiones Arquitectónicas y Estratégicas
id: ENT_GOB_DECISIONES
version: 2.3
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
stamp: VIGENTE — 2026-06-30
classification: ENTITY — Registro centralizado de decisiones que trascienden un sprint
aplica_a: [MWT]

---

## A. Propósito

Registro formal de decisiones arquitectónicas, estratégicas y de negocio. Formato ADR (Architecture Decision Records) adaptado a MWT. Solo decisiones que trascienden un sprint — las decisiones de scope de sprint quedan en cada LOTE.

Cada decisión registra: contexto, alternativas evaluadas, decisión tomada, consecuencias, y si es reversible. La distinción reversible/irreversible importa: las one-way doors se piensan más, las two-way doors se pueden experimentar.

---

## B. Registro de Decisiones

### DEC-001: Stack MVP = Django + DRF + PostgreSQL + MinIO
- **Fecha:** 2026-02-26
- **Contexto:** Sistema operativo para CEO, ~50-100 expedientes activos. 1 VPS Hostinger KVM 8.
- **Alternativas evaluadas:** Validado por Gemini, ChatGPT y Claude como stack adecuado para el caso de uso.
- **Decisión:** Django monolito con DRF, PostgreSQL, MinIO para archivos. 6 contenedores Docker.
- **Consecuencias:** Sin event bus, sin microservicios, sin Celery workers en MVP. Simplicidad operativa.
- **Reversible:** NO — migrar de framework tiene costo prohibitivo post-MVP.
- **Ref:** ENT_PLAT_INFRA, ENT_PLAT_MVP

### DEC-002: Secuencia de lanzamiento GOL → ORB → VEL → LEO → BIS
- **Fecha:** [CEO: completar fecha]
- **Contexto:** 5 productos, recursos limitados, riesgo de canibalización entre GOL y BIS (ambos usan PORON XRD).
- **Alternativas evaluadas:** [CEO: si hubo otras secuencias consideradas]
- **Decisión:** Lanzamiento secuencial. BIS no se lanza antes de GOL >1,000 reviews.
- **Consecuencias:** Concentra recursos. Retrasa time-to-market de BIS. Protege demand share de GOL.
- **Reversible:** SÍ — la secuencia se puede ajustar según datos de mercado.
- **Ref:** ENT_PROD_LANZAMIENTO

### DEC-003: Modelo de distribución por nodos con contrato inteligente
- **Fecha:** [CEO: completar fecha]
- **Contexto:** Distribución multi-país requiere intermediarios locales con autonomía operativa controlada.
- **Alternativas evaluadas:** [CEO: distribuidores tradicionales vs modelo de nodos]
- **Decisión:** Nodos como entidades semi-autónomas con contrato normativo (ENT_PLAT_CONTRATO_NODO).
- **Consecuencias:** Mayor control, mayor complejidad de setup. Requiere plataforma tecnológica.
- **Reversible:** PARCIAL — el modelo se puede simplificar pero la estructura de contratos ya está diseñada.
- **Ref:** ENT_PLAT_CONTRATO_NODO, ENT_DIST_DISTRIBUIDORES

### DEC-004: Command-heavy architecture (no CRUD-first)
- **Fecha:** [CEO: completar fecha]
- **Contexto:** Sistema de expedientes con state machine. Cada transición es un comando con validación.
- **Alternativas evaluadas:** ViewSet + @action (CRUD-first) vs APIView por command (command-heavy).
- **Decisión:** Cada command = 1 endpoint POST dedicado. No ViewSet.
- **Consecuencias:** Más endpoints, más control, más testeable. Menos convencional para Django.
- **Reversible:** NO — refactorizar a ViewSet requiere reescribir la capa API completa.
- **Ref:** LOTE_SM_SPRINT1

### DEC-005: KB pre-ingeniada con stubs y toggles
- **Fecha:** 2026-03 (evolución progresiva)
- **Contexto:** La KB documenta productos, mercados y procesos que aún no están activos. Necesidad de tener la estructura lista sin llenar contenido especulativo.
- **Alternativas evaluadas:** Solo documentar lo activo vs pre-ingeniar toda la estructura.
- **Decisión:** Stubs con planned_sprint/planned_date, toggles para activar cuando corresponda. POL_STUB_LIFECYCLE como governance.
- **Consecuencias:** KB más grande pero preparada para escalar. Riesgo de stubs abandonados (mitigado por POL_STUB_LIFECYCLE).
- **Reversible:** SÍ — los stubs se pueden deprecar sin impacto.
- **Ref:** POL_STUB_LIFECYCLE, RW_ROOT

### DEC-006: FaberLoom F1 routing = tiered hardcoded YAML (no adaptive)
- **Fecha:** 2026-04-21
- **Contexto:** Spec §9 Adaptive Routing original proponía runtime router + evidence ledger + weekly tuning + score compuesto + guardrails N≥20. Validación Kimi Swarm #4 (`archivo/kimi_swarm_4_adaptive_routing.md`) arrojó `LOW confidence`: break-even 9,524 drafts/mes vs beta 600, N≥20 power 6.5%, pesos heurísticos sin fundamento, decay 0.9/mes demasiado lento, SPOF LiteLLM, cross-tenant poisoning en tablas sin `tenant_id`, data residency sin hard block (CEO-ONLY podía rutear a CN).
- **Alternativas evaluadas:** (a) lanzar adaptive completo F1 según spec original; (b) downgrade a tiered hardcoded F1 con adaptive postpuesto; (c) híbrido con shadow mode F1 pero sin enforcement.
- **Decisión:** opción (b). F1 usa YAML estático en git (`faberloom/config/llm_tiers.yaml`) con 4 tiers: simple → gemini_flash, medium → kimi_k2, complex → sonnet_4_6, local_only → ollama_llama_3_2_3b. Cambios = commit + PR. Git history reemplaza `routing_policy_version`. Sin evidence ledger, sin weekly tuning, sin score compuesto, sin shadow testing, sin MAB.
- **Consecuencias:** (+) TTM rápido, complejidad operativa 10× menor, cero over-engineering sobre 600 drafts/mes; (−) pierde adaptación automática, debe refactorizarse al llegar a F2. Tablas descartadas de S1: `model_evidence_ledger`, `routing_policy_proposal`, `routing_policy_version`, `workflow_step_routing` dinámico.
- **Reversible:** SÍ — promover a F2 sólo añade tablas + proceso; el YAML se mantiene como fallback.
- **Ref:** ENT_PLAT_LLM_ROUTING §F, archivo/kimi_swarm_4_adaptive_routing.md (Kimi A1 + A3 verbatim).

### DEC-007: Arena Mode descartado de FaberLoom F1
- **Fecha:** 2026-04-21
- **Contexto:** Arena Mode (head-to-head de modelos en producción con voto humano estilo chatbot-arena) propuesto como parte del learning loop adaptive.
- **Alternativas evaluadas:** (a) Arena Mode F1 para generar evidence inicial; (b) descartar de F1 y re-evaluar en F2 junto con adaptive; (c) Arena sólo sobre dataset sintético gold.
- **Decisión:** opción (b). Razón: volumen beta (200-600 drafts/mes) insuficiente para N≥20 por comparación de modelos, 2-3 sprints de build, no hay tensión real entre modelos con tiered Sonnet reducer.
- **Consecuencias:** libera slot de Add-on 6 para **Voice Profile** (ver D17 en handoff v3.5, aprobado como 6º Add-on tenant-level). UI mockup v3.5 necesita ajuste en v4.0 para remover Arena tab y sumar Voice Profile.
- **Reversible:** SÍ — reconsiderar cuando gate F2 abra (ref DEC-008).
- **Ref:** ENT_PLAT_LLM_ROUTING §G.4, archivo/kimi_swarm_4_adaptive_routing.md.

### DEC-008: Adaptive Routing postpuesto a F2, gated a 5K drafts/mes × 3 tenants × 3 meses
- **Fecha:** 2026-04-21
- **Contexto:** DEC-006 descarta adaptive para F1 pero no lo mata; es un futuro deseable cuando haya volumen estadísticamente defendible. Kimi A3 calcula que N≥500/semana se necesita para power ≥50% detectando deltas de 5pp en approval rate.
- **Alternativas evaluadas:** (a) gate por número de tenants (≥10); (b) gate por volumen agregado (≥15K drafts/mes global); (c) gate por tenant-activo sostenido (3 tenants × 5K × 3 meses); (d) gate por revenue (≥$5K MRR).
- **Decisión:** opción (c). 3 tenants con 5,000 drafts/mes sostenido durante 3 meses consecutivos → trigger de build F2. Rationale: volumen per-tenant (no agregado) mitiga cold-start; sostén de 3 meses filtra spikes; 3 tenants da diversidad para detectar tenant-specific drift sin over-fitting.
- **Mejoras Kimi capitalizables cuando F2 llegue** (archivadas en ENT_PLAT_LLM_ROUTING §G.2 y archivo/kimi_swarm_4_adaptive_routing.md §"Mejoras Kimi diferidas"): decay semanal 0.85 (reemplaza 0.9/mes), concept drift detection Page-Hinkley/ADWIN, MAB híbrido Thompson+ε-greedy, pesos aprendidos vía regresión logística (reemplaza 0.40/0.20/0.15/0.15/0.10 heurísticos), umbral N≥500 (reemplaza N≥20), 4-eyes workflow + firma digital SOC 2, dataset sintético para shadow testing, evidence per-tenant obligatoria.
- **Consecuencias:** F2 no se comienza hasta cumplir gate; ahorra 2-3 sprints de build prematuro; cuando se construya, parte de un corpus Kimi-validado ya maduro.
- **Reversible:** PARCIAL — gate se puede ajustar si el CEO decide bajar umbral, pero las lecciones arquitectónicas (tenant_id obligatorio, drift detection, pesos aprendidos) son one-way doors una vez canonizadas.
- **Ref:** ENT_PLAT_LLM_ROUTING §G, archivo/kimi_swarm_4_adaptive_routing.md (Kimi A1 + A3 + A4 verbatim).

### DEC-009: Prompt Cache Discipline para archivos Always-loaded

- **Fecha:** 2026-05-07
- **Contexto:** Prefijo estable Always-loaded estimado en ~45K tokens, repetido en ~100% de calls de Cowork/Claude Code/Claude Projects. Sin disciplina de cache, costo proyectado ~$527/mes solo en input. Anthropic prompt caching ofrece 90% off cached read pero requiere prefijo invariante. H4 detectada: timestamps al inicio de archivos Always-loaded (CLAUDE.md, RW_ROOT, DASHBOARD_SNAPSHOT) rompen cache en cada bump.

- **Alternativas evaluadas:**
  - (a) mover timestamp al final del documento
  - (b) cache_control breakpoint despues del bloque volatil inicial
  - (c) timestamp solo via Git log (fuera del archivo)
  - (d) no hacer nada, aceptar miss

- **Decision:** opcion (a) + R1-R4 cementadas en SPEC_PROMPT_CACHE_DISCIPLINE v1.0. Timestamps al final, orden canonico de bloques en system prompts, cache_control breakpoint explicito antes de session-specific context, TTL 5min default. Aplica a archivos Always-loaded.

- **Consecuencias:**
  - (+) Ahorro proyectado ~$5,600/ano en input cost
  - (+) Latencia TTFT -30% en calls cacheadas
  - (+) Compatible con D9 (Data Classification Routing) y D10 (Audit Module) del Action Engine
  - (-) Disciplina obligatoria en headers -- bump version o auditor request a "fecha en header" requiere variant alternativa
  - (-) Implementacion requiere bump SPEC_ACTION_ENGINE v1.2->v1.3 con +D11
  - (-) Sprint mecanico timestamp-al-footer ~35 archivos diferido a post-A1 para coordinarse con A1 que produce 12 SPECs nuevos

- **Reversible:** SI -- revertir es trivial (mover timestamp arriba, quitar cache_control). Lo unico one-way es el orden canonico de bloques R3, que rompe cache para versiones anteriores si se cambia.

- **Ref:** SPEC_PROMPT_CACHE_DISCIPLINE.md (v1.0), SPEC_ACTION_ENGINE.md (v1.3 +D11), POL_CONTEXT_BUDGET.md, MANIFIESTO_CAMBIOS_v2.md (BATCH 2026-05-07 PROMPT_CACHE)

- **Origen:** HANDOFF Cowork 28-abr (analisis articulo TDS Agentic AI tokens) actualizado post Sprint 0

### DEC-010: Jarvis Orchestrator diferido — gates G1-G4 antes de build
- **Fecha:** 2026-04-28
- **Aprobador:** CEO (delegado al Arquitecto Cowork — sesión 2026-04-28 "eres el arquitecto")
- **Contexto:** CEO planteó construir un agente conversacional persistente per-user ("Jarvis") que cruce sub-agentes y ejecute rutinas re-evaluables sobre el Action Engine, en reemplazo de flujos predefinidos. Plan en 3 fases (F1 reactivo / F2 rutinas+memoria episódica / F3 proactivo+multi-tenant). ROI personal estimado 4x-15x. Ver MANIFIESTO_APPEND_20260428_JARVIS_IDEA y CEO-36 en ENT_GOB_PENDIENTES.
- **Verificación de pre-reqs (estado real 2026-04-28):**
  - Action Registry ≥30 actions catalogadas: ✅ 53 actions (ENT_PLAT_ACTION_REGISTRY v1.1)
  - Action Engine **runtime ejecutable**: ❌ solo contrato v1.2 VIGENTE; runtime passthrough programado sem 3+ del roadmap
  - Memoria persistente per-user: ❌ Letta en CEO-34 piloto sin decisión; ENT_PLAT_MEMORY_STACK DRAFT
  - FaberLoom MVP fuera de path crítico Engine: ❌ MVP en sem 3-9 consume mismo Engine, conflicto de prioridad
- **Alternativas evaluadas:**
  - (a) **Build F1 ahora** — descartado: construir orquestador sobre Engine sin runtime es construir sobre arena; cada sub-agente seguiría hardcoded, lo opuesto al objetivo del Action Engine
  - (b) **Diferir con gates cuantitativos** — elegido: respeta secuencia arquitectónica (Engine → memoria → Jarvis), no cierra la puerta, define disparador objetivo
  - (c) **Descartar definitivamente** — descartado: el ROI personal estimado es alto y el patrón es estratégicamente sólido; descartarlo cierra opcionalidad valiosa sin razón
  - (d) **Build paralelo a Engine** — descartado: dobla riesgo de retrabajo (cada cambio del contrato Engine rompe Jarvis); viola P14 deterministic-first y P3 draft-first
- **Decisión:** **DEFER con 4 gates cuantitativos.** Reabrir CEO-36 cuando se cumplan TODOS:
  - **G1 — Engine runtime vivo:** Action Engine passthrough en producción + ≥3 skills MWT migradas al Engine (no hardcoded)
  - **G2 — Memoria persistente operativa:** Letta piloto DONE en `mwt-sprint-active` o stack alternativo equivalente VIGENTE
  - **G3 — FaberLoom MVP estable:** sem 6+ del roadmap, fuera de path crítico de modificaciones al Engine
  - **G4 — Datos suficientes para aprender:** OutcomeLedger con ≥1000 decisiones loggeadas (corpus mínimo para que Jarvis tenga sobre qué razonar)
- **Recomendación intermedia (CEO-37):** ejecutar **captura formal de rutinas mentales CEO** en sesión Cowork de 90-120 min ANTES de cualquier build de Jarvis. Output `ENT_GOB_RUTINAS_CEO.md` (CEO-ONLY). Razones: (a) valida hipótesis de carga mental con datos reales, (b) genera corpus de entrenamiento, (c) detecta rutinas automatizables YA con n8n + Engine passthrough (captura 30-40% del valor por 2% del costo), (d) clasifica rutinas re-evaluables (Jarvis-fit) vs deterministas (n8n-fit). Costo: 2-3h CEO + 1h arquitecto.
- **Consecuencias:**
  - No se asignan recursos a Jarvis hasta cumplir gates (estimado 8-12 semanas calendario realista)
  - Action Engine y Letta se priorizan como pre-condición arquitectónica
  - CEO-37 ejecuta antes de reabrir CEO-36 — la captura de rutinas es invariable independiente de la decisión final
  - Si en 12 semanas los gates no se cumplen → revisar prioridades del roadmap, no Jarvis
- **Reversible:** SÍ — gates se pueden ajustar si CEO decide acelerar (ej. contratando dev dedicado a Engine runtime). La decisión NO descarta Jarvis, solo difiere el build con criterios objetivos. Two-way door.
- **Ref:** ENT_GOB_PENDIENTES CEO-36 + CEO-37 · MANIFIESTO_APPEND_20260428_JARVIS_IDEA · SPEC_ACTION_ENGINE v1.2 §Roadmap · ENT_PLAT_ACTION_REGISTRY v1.1 · ENT_PLAT_MEMORY_STACK · ARCH_AGENT_PRINCIPLES P3/P4/P9/P13/P14

### DEC-011: SpaceLoom Spike E1 — track canónico único Foundation Beta, spike como dogfood interno
- **Fecha:** 2026-06-30
- **Aprobador:** CEO
- **Contexto:** Se construyó un artefacto ejecutable (FastAPI + SQLite + pywebview + .exe) sobre `PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md` que comparte nombre "FaberLoom" con el track canónico firmado `PLB_FB_FOUNDATION_BETA_v1.md` (Postgres + RLS + Next.js + 13 sprints). Esto genera una colisión de marca y arquitectura (STACK-01). El spike tiene 221 tests verdes y cerró SL0–SL4, pero no es multi-tenant, no cumple TIER 1 Foundation Beta y no está indexado en la KB.
- **Alternativas evaluadas:**
  - (a) **Spike de validación / dogfood interno** — elegido: se registra como no canónico, se mantienen aprendizajes, se archiva cuando Foundation Beta entregue reemplazo funcional para MWT.
  - (b) **Pivote desktop-first** — descartado: contradice la inversión y plan firmado en Foundation Beta v1.3.1.
  - (c) **Etapa incremental definitiva** — descartado: el stack SQLite/pywebview no escala al canon Postgres/RLS; no se justifica convertirlo en producto.
- **Decisión:** El spike se trata como **(A) spike de validación con matiz operativo**: es dogfood interno de MWT mientras Foundation Beta no tenga reemplazo funcional, pero su destino final es archivarse. El track de ejecución canónico único es **FaberLoom Foundation Beta v1.3.1**. El spike se etiqueta como artefacto "SpaceLoom Spike E1", se despliega bajo `spike.faberloom.ai` y se registra en `MANIFIESTO_APPEND_20260630_SPACELOOM_SPIKE_E1.md`. El repo de trabajo (`Ale241302/faber_loom_local_v2`) **se mantiene con su nombre actual**; solo cambia la etiqueta/concepto del spike.
- **Consecuencias:**
  - No se mergea código SQLite/pywebview al canon.
  - SpaceLoom se reserva como pilar de marca (home cognitivo / canvas), no como nombre de prototipo.
  - Los aprendizajes validados (`edit_pct ≤ 0.2` para gold, gate Owner/Admin shadow→active, `confirmation_token + idempotency_key`, provider allowlist/budget/fallback, workspace sealing, versionado routine/skill/source) se portan a los specs de Foundation Beta.
  - SL5 (correo) del spike queda diferido; el flag `email_connector_enabled=false` se documenta explícitamente.
  - Acciones de rename/repo/domain son tracking interno del spike, no entran como CEO-XX.
- **Reversible:** SÍ — se puede ajustar la fecha de sunset o acelerar el archivado si Foundation Beta avanza más rápido. La decisión de no canonizar el spike es reversible mientras no se mergee con Foundation Beta.
- **Ref:** `MANIFIESTO_APPEND_20260630_SPACELOOM_SPIKE_E1.md` · `PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md` · `PLB_FB_FOUNDATION_BETA_v1.md` · `IDX_FB_FOUNDATION_BETA.md`

---

## C. Estadísticas
| Métrica | Valor |
|---------|-------|
| Total decisiones registradas | 11 |
| Irreversibles (one-way doors) | 2 (DEC-001, DEC-004) |
| Reversibles (two-way doors) | 8 (DEC-002, DEC-005, DEC-006, DEC-007, DEC-009, DEC-010, DEC-011, futuras) |
| Parcialmente reversibles | 2 (DEC-003, DEC-008) |

---
Changelog:
- v1.0 (2026-03-14): creación inicial con 5 ADRs extraídos de entities existentes (E-2).
- v2.0 (2026-04-21): +DEC-006 (FaberLoom F1 tiered hardcoded routing) +DEC-007 (Arena Mode descartado F1) +DEC-008 (Adaptive Routing postpuesto F2 gated 5K×3t×3m). Trigger: Kimi Swarm #4 validación LOW confidence (verbatim archivado en docs/archivo/kimi_swarm_4_adaptive_routing.md). Canoniza el downgrade post-validación. Renumera antiguo DEC-006 stub a DEC-009.
- v2.1 (2026-04-28): +DEC-010 (Jarvis Orchestrator diferido — gates G1-G4 antes de build). Decisión arquitecto Cowork delegada por CEO sesión 2026-04-28. Two-way door. Refuerzo: CEO-37 captura rutinas mentales como precondición intermedia.
- v2.2 (2026-05-07): DEC-009 completado -- Prompt Cache Discipline reemplaza placeholder. Stats actualizados: total 9 (mal contado pre-DEC-010) corregido a 10; reversibles 6 -> 7 (suma DEC-009). Origen: HANDOFF Cowork 28-abr actualizado post Sprint 0.
- v2.3 (2026-06-30): +DEC-011 (SpaceLoom Spike E1 — track canónico único Foundation Beta, spike como dogfood interno). Resuelve STACK-01. Stats actualizados: total 10 -> 11; reversibles 7 -> 8.
