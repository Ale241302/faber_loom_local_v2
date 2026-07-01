# MANIFIESTO_APPEND_20260421_LLM_ORCHESTRATION
fecha: 2026-04-21
autor: Claude (Cowork)
tipo: INDEXACION (canonización post-validación)
trigger: CEO — "empieza por indexar el conocimiento" sobre decisiones LLM Orchestration post Kimi Swarm #4
aplica_a: [SHARED]

---

## Resumen

Canoniza el downgrade del modelo de routing FaberLoom F1 de **adaptive completo → tiered hardcoded YAML**, gatillado por validación Kimi Swarm #4 con verdict `LOW confidence` (break-even 9,524 drafts/mes vs beta real 600, N≥20 power 6.5%, pesos heurísticos sin fundamento, SPOF LiteLLM, cross-tenant poisoning, data residency sin hard block).

3 decisiones nuevas registradas (DEC-006/007/008). 18 preguntas abiertas capturadas (Q1-Q18). 1 ENT renovado (LLM_ROUTING v1.0→v2.0). 1 archivo verbatim nuevo (kimi_swarm_4). Mejoras Kimi diferidas preservadas para F2 cuando se cumpla gate (3 tenants × 5K drafts/mes × 3 meses).

Este batch cierra Fase 1 del handoff Cowork v3.5 sobre LLM orchestration. Fase 2 (crear SPEC_FABERLOOM_RESEARCH_SWARM, SPEC_FABERLOOM_KNOWLEDGE_BROKER, SPEC_FABERLOOM_SWARM_PLANNER, SPEC_FABERLOOM_INVOCATION_REGISTRY) queda bloqueada hasta respuestas CEO a Q1-Q18 P0.

## Contexto

Handoff Cowork v3.5 (2026-04-20) entregó 17 decisiones D1-D17, de las cuales D11 (F1 adaptive routing) quedó pendiente de validación. Se ejecutó Kimi Swarm #4 con 4 sub-agentes especializados (A1 cost/ROI, A2 reliability/ops, A3 data science, A4 security/compliance). Los 4 sub-agentes convergieron en `LOW confidence` por razones distintas pero complementarias, identificando 3 blockers top y 3 mejoras 10× capitalizables hoy.

El CEO aprobó opción B del Kimi (downgrade F1 a hardcoded + postponer adaptive a F2 gated). Este batch canoniza esa decisión en la KB.

## Archivos creados

| Archivo | Bytes | Función |
|---------|-------|---------|
| `archivo/kimi_swarm_4_adaptive_routing.md` | ~12000 | Verbatim A1+A2+A3+A4 Kimi, síntesis LOW confidence, top 3 blockers, top 3 mejoras 10×, 1 gap (cold start), mejoras diferidas F2, orquestación reference Research Swarm F1 |
| `MANIFIESTO_APPEND_20260421_LLM_ORCHESTRATION.md` | (este) | Manifiesto del gate |

## Archivos modificados

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `ENT_PLAT_LLM_ROUTING.md` | REESCRITURA v1.0→v2.0 | Preserva §B rankings arena.ai + §C pricing + §D task routing MWT-owned. Expande §E PLT-11 a 6 tablas (+`tenant_model_allowlist` hard block, tenant_id obligatorio + RLS en `llm_usage_log`, HA LiteLLM 2 instances + HAProxy, audit findings absorbiendo 4 critiques Kimi). Nueva §F FaberLoom F1 tiered hardcoded (YAML 4 tiers · runtime flow 7 steps · circuit breakers 2 niveles · cold start 30d · F1 limits). Nueva §G F2 adaptive postponed (gate 5K×3t×3m · mejoras Kimi archivadas · tablas descartadas S1 · Arena Mode descartada). Nueva §H separación MWT vs FaberLoom |
| `ENT_GOB_DECISIONES.md` | EDIT v1.0→v2.0 | +DEC-006 FaberLoom F1 = tiered hardcoded YAML (NO adaptive) · +DEC-007 Arena Mode descartado F1 · +DEC-008 Adaptive Routing postpuesto F2 gated 5K×3t×3m · renumera antiguo DEC-006 stub a DEC-009. Stats: 8 decisiones (2 irreversible + 5 reversible + 2 parcial-reversible) |
| `ENT_GOB_PENDIENTES.md` | EDIT v12.0→v13.0 | +Q1-Q18 track "Open questions post-Kimi Swarm #4 — LLM Orchestration". 7 P0 + 7 P1 + 4 P2. Cada Q con propuesta agente, prioridad, unblocks. Origen 2026-04-21 |
| `IDX_PLATAFORMA.md` | EDIT última revisión | Última revisión 2026-04-19→2026-04-21. ENT_PLAT_LLM_ROUTING row actualizado: DRAFT v1.0 → DRAFT v2.0 con feature list (tiered hardcoded F1 FaberLoom + data residency `tenant_model_allowlist` + HA LiteLLM + circuit breakers + cold start 30d + F2 adaptive postponed; model registry, pricing, PLT-11 arquitectura preservados) |
| `IDX_GOBERNANZA.md` | EDIT health + nueva sub-sección | Health +1 archivo Kimi Swarm #4. Última revisión 2026-04-20→2026-04-21. Nueva sub-sección "Archivo — Kimi Swarm validaciones" con 3 entradas (agentes_virtuales, 3_workflows_autonomous, 4_adaptive_routing LOW confidence) |
| `RW_ROOT.md` | EDIT v4.8.4→v4.8.5 | Changelog v4.8.5 con resumen del INDEXA LLM Orchestration |

## Decisiones de indexación

1. **Update sobre ENT existente, NO nuevo SPEC.** El archivo `ENT_PLAT_LLM_ROUTING.md` existía como v1.0 DRAFT. Según POL_DETERMINISMO, se reescribe a v2.0 en lugar de crear `SPEC_FABERLOOM_LLM_ORCHESTRATION` duplicado. Market data (§B rankings arena.ai + §C pricing + §D task routing MWT) preservado verbatim. La arquitectura FaberLoom F1 se suma como §F dentro del mismo doc, con §H separación explícita MWT vs FaberLoom para evitar confusión.

2. **DEC-006/007/008 dentro de `ENT_GOB_DECISIONES.md`, NO en subfolder ADR.** Reconocimiento de KB mostró que no existe `docs/archivo/adr/` — las decisiones se acumulan en el ENT único con numeración secuencial (DEC-001 a DEC-005 precedentes). Se respeta el patrón y el antiguo DEC-006 stub se renumera a DEC-009.

3. **Verbatim Kimi → archivo/ con nomenclatura consistente.** Sigue el patrón `kimi_swarm_<N>_<topic>.md` (precedentes: `kimi_swarm_3_workflows_autonomous.md`, `kimi_swarm_agentes_virtuales.md`). Esto facilita re-evaluación cuando gate F2 abra — el corpus Kimi queda listo para consultar sin buscar por chats.

4. **Q1-Q18 dentro de ENT_GOB_PENDIENTES track FaberLoom, NO doc separado.** Consistente con política anterior (OQs AUDIT A7, brechas B1-B6). Priorización P0-P2 permite al CEO atacar en orden sin ruido.

5. **Mejoras Kimi diferidas archivadas en §G.2 de LLM_ROUTING + verbatim en archivo/.** Doble custodia: el ENT resume para consulta rápida, el archivo guarda fundamentos Kimi completos. Cuando F2 llegue, arrancamos de corpus maduro (decay 0.85/semana, Page-Hinkley, MAB híbrido, pesos aprendidos, N≥500, 4-eyes SOC 2, sintético shadow, per-tenant evidence).

6. **Tablas descartadas de S1 documentadas explícitamente.** `model_evidence_ledger`, `routing_policy_proposal`, `routing_policy_version`, `workflow_step_routing` dinámico quedan anotadas en §G.3 como "borradas del blueprint S1 → re-introducir en S-F2". Evita que aparezcan por inercia en futuros esquemas.

7. **Gate F2 como política cuantitativa, no discrecional.** `3 tenants × 5,000 drafts/mes × 3 meses` es criterio objetivo. Protege contra build prematuro por entusiasmo. Solo CEO puede bajar umbral (reversibilidad parcial declarada en DEC-008).

## Ámbito del gate

```
GATE ✅ INDEXA LLM Orchestration (señal CEO: "empieza por indexar el conocimiento")
✔ Determinismo     — Update sobre ENT_PLAT_LLM_ROUTING existente (no crea SPEC duplicado). DEC-006/007/008 dentro de ENT_GOB_DECISIONES (patrón preexistente DEC-001..005). Archivo Kimi con nomenclatura consistente
✔ Tipo             — ENT (update LLM_ROUTING · update DECISIONES · update PENDIENTES) + ARCHIVO (verbatim Kimi). Ningún tipo nuevo
✔ Stamp            — ENT_PLAT_LLM_ROUTING DRAFT (pending Q1-Q18 CEO) · ENT_GOB_DECISIONES VIGENTE v2.0 · ENT_GOB_PENDIENTES VIGENTE v13.0 · archivo DRAFT INTERNAL · RW_ROOT VIGENTE v4.8.5
✔ Version          — LLM_ROUTING v1.0→v2.0 · DECISIONES v1.0→v2.0 · PENDIENTES v12.0→v13.0 · RW_ROOT v4.8.4→v4.8.5. Todos con changelog
✔ Impacto cruzado  — IDX_PLATAFORMA (LLM_ROUTING row) · IDX_GOBERNANZA (health + archivo sub-sección + DECISIONES/PENDIENTES noted) · RW_ROOT (changelog) · NO toca FROZEN · NO toca POL_
✔ Pendientes       — +18 OQ (Q1-Q18) en ENT_GOB_PENDIENTES track FaberLoom. 7 P0 bloquean Fase 2 SPECs. Mejoras Kimi diferidas archivadas (no convertidas en OQ — son work post-gate)
✔ Sin inventados   — Verbatim Kimi preservado íntegro. YAML 4 tiers usa modelos ya registrados en §B/§C. Gate F2 citado desde DEC-008. Ninguna cifra nueva inventada
✔ IDX              — IDX_PLATAFORMA (LLM_ROUTING) + IDX_GOBERNANZA (DECISIONES v2.0 + PENDIENTES v13.0 + archivo Kimi #4) actualizados. RW_ROOT changelog
✔ Seguridad        — INTERNAL todos. tenant_model_allowlist es hard block pre-tier-check (data residency canonizada). ENT_PLAT_SEGURIDAD PARTNER_B2B referenciado en §E. CEO-ONLY preservado en §D
```

## Refs activos

- `ENT_PLAT_LLM_ROUTING.md` v2.0 DRAFT — ENT canónico post-Kimi
- `ENT_GOB_DECISIONES.md` v2.0 VIGENTE — DEC-006/007/008
- `ENT_GOB_PENDIENTES.md` v13.0 VIGENTE — Q1-Q18 track FaberLoom
- `archivo/kimi_swarm_4_adaptive_routing.md` — verbatim A1+A2+A3+A4 LOW confidence
- `archivo/kimi_swarm_3_workflows_autonomous.md` — precedente HIGH confidence (contraste metodológico)
- `SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` v1.0 — pendiente bump a 30 tablas S1 post-aprobación CEO (Fase 2)
- `ENT_PLAT_SEGURIDAD.md` — referenciada por §E (tenant_model_allowlist, RLS, Fernet vault)
- `ARCH_AGENT_PRINCIPLES.md` v1.2 — P13 Contención aplicable al draft-first de Research Swarm F1
- `MANIFIESTO_APPEND_20260420_AUDIT_FABERLOOM_REFRESH.md` — handoff v3.5 que enlazaba D11 con Kimi #4 pending

## Estado final del track LLM Orchestration

| Asunto | Status |
|--------|--------|
| F1 routing model | ✅ Canonizado: tiered hardcoded YAML 4 tiers (`simple`/`medium`/`complex`/`local_only`) |
| Data residency enforcement | ✅ Canonizado: `tenant_model_allowlist` hard block pre-tier-check |
| HA LiteLLM | ✅ Canonizado: 2 instances (4000 primary + 4001 backup) + HAProxy health 10s |
| Circuit breakers | ✅ Canonizado: 2 niveles (provider + model) · Redis state · 50%/20req open · 1req half-open · <10%/10req close |
| Cold start | ✅ Canonizado: 30 días manual + CEO review semanal + fallback YAML default |
| Arena Mode | ✅ Descartado F1 (DEC-007) · reconsiderar en F2 |
| Adaptive routing F1 | ❌ Descartado (DEC-006) |
| Adaptive routing F2 | ⏸ Postpuesto gated (DEC-008) — 3 tenants × 5K drafts/mes × 3 meses |
| Voice Profile (6º Add-on) | 🟡 Aprobado en handoff D17 → pendiente spec (Fase 2) |
| Research Swarm F1 sin critic | 🟡 Aprobado — pendiente SPEC_FABERLOOM_RESEARCH_SWARM_v1 (Fase 2) |
| Knowledge Broker | 🟡 Aprobado — pendiente SPEC_FABERLOOM_KNOWLEDGE_BROKER_v1 (Fase 2) |
| Swarm Planner | 🟡 Aprobado — pendiente SPEC_FABERLOOM_SWARM_PLANNER_v1 (Fase 2) |
| Invocation Registry | 🟡 Aprobado — pendiente SPEC_FABERLOOM_INVOCATION_REGISTRY_v1 (Fase 2) |
| Q1-Q18 CEO responses | ⏸ Bloqueante para Fase 2 (7 P0 + 7 P1 + 4 P2) |

## Lo que el CEO tiene que decidir ahora

1. **Responder Q1-Q18 por prioridad** (ENT_GOB_PENDIENTES v13.0 track FaberLoom LLM Orchestration):
   - **7 P0 bloqueantes:** parámetros YAML finales (tiers default · max_cost), thresholds circuit breaker, política cold-start review, tenant_model_allowlist default por plan (Starter/Pro/Enterprise), Fernet key rotation cadence, observabilidad (Langfuse), alerting mínimo
   - **7 P1:** operativas post-beta
   - **4 P2:** mejoras diferidas

2. **Con Q1-Q18 P0 resueltos → Fase 2 SPECs** (bloqueada hasta aquí):
   - SPEC_FABERLOOM_RESEARCH_SWARM_v1 (sin critic)
   - SPEC_FABERLOOM_KNOWLEDGE_BROKER_v1
   - SPEC_FABERLOOM_SWARM_PLANNER_v1
   - SPEC_FABERLOOM_INVOCATION_REGISTRY_v1
   - SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT bump → 30 tablas S1 final
   - SPEC_SKILL_COMPOSITION update (Voice Profile 6º Add-on)
   - SPEC_AGENT_COMPOSITION v1.1→v1.2
   - FABERLOOM_MOCKUP_CHANGES v3.6→v4.0 (remover Arena tab + sumar Voice Profile)

3. **Al cumplir gate F2** (3 tenants × 5K drafts/mes × 3 meses sostenido): disparar build adaptive partiendo de corpus Kimi-validado (§G.2 mejoras archivadas).

## Stamp

INDEXACION VIGENTE desde 2026-04-21. Track LLM Orchestration Fase 1 CERRADO. Fase 2 gated a Q1-Q18 P0 resolution. F2 adaptive gated a volumen real post-beta.
