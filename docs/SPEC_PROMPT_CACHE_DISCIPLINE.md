# SPEC_PROMPT_CACHE_DISCIPLINE -- Disciplina de Prompt Caching para Always-loaded

---
id: SPEC_PROMPT_CACHE_DISCIPLINE
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
type: SPEC
stamp: DRAFT -- 2026-05-07 -- pendiente medicion real H2 post-implementacion
aprobador: CEO
aplica_a: [MWT, FaberLoom]
relacionado: SPEC_ACTION_ENGINE.md (D11) · POL_CONTEXT_BUDGET.md · DEC-009 en ENT_GOB_DECISIONES.md
data_classification: N1
---

## Declaracion

Especifica reglas operativas para que el prefijo estable de archivos Always-loaded sea cacheable por proveedores LLM (Anthropic prompt caching, equivalentes en otros proveedores). Aplica a:

- CLAUDE.md, RW_ROOT.md, DASHBOARD_SNAPSHOT.md, ARCH_AGENT_PRINCIPLES.md, WIKI.md
- IDX_*, POLs Always Tier (POL_NUEVO_DOC, POL_VISIBILIDAD, POL_STAMP, POL_EPHEMERAL_OUTPUT, POL_CONTEXT_BUDGET, POL_DATA_CLASSIFICATION, POL_BRANCH_PR, POL_ROOT_FILE_CLASSIFICATION)
- SKILL_* Always Tier
- ENT_GOB_PENDIENTES, ENT_GOB_DECISIONES
- SPEC_ACTION_ENGINE, SPEC_HOOKS_FAIL_CLOSED

Status DRAFT hasta validar con medicion real (H2: cache hit ratio actual <30%). Promueve a VIGENTE post-medicion confirmatoria.

---

## Por que este documento existe

Prefijo estable Always-loaded estimado en ~45K tokens, repetido en ~100% de calls de Cowork (AG-07), Claude Code (AG-02), y Claude Projects. Sin disciplina:

- Costo proyectado sin cache: ~$527/mes (130 calls/dia agregadas, Sonnet 4.6)
- Costo proyectado con cache 90%: ~$59/mes
- **Ahorro proyectado: ~$468/mes (~$5,600/ano)**

Bloqueante actual: timestamps al inicio de archivos Always-loaded invalidan el cache en cada bump, perdiendo el descuento de 90% sobre cached input.

---

## Las 4 reglas cementadas

### R1 -- Volatiles al final, nunca al inicio

Todo campo que cambie con frecuencia (timestamp `Ultima actualizacion`, version bumps en footer, contadores) se ubica al **final del documento**, no en el header ni cerca del top.

**Permitido en header:** id, version, status, visibility, domain, type, stamp, aprobador, aplica_a, relacionado, data_classification (todos campos estructurales).

**Prohibido en header:** timestamps de actualizacion, fechas de generacion, contadores de archivos, conteos.

**Footer canonico para Always-loaded:**

```
---
Ultima actualizacion: YYYY-MM-DD vX.Y.Z
Generado por: [agente]
```

### R2 -- Cache breakpoints explicitos en system prompts

Agentes que usan archivos Always-loaded como system prompt (Cowork, Claude Code) deben:

1. Habilitar `cache_control: {type: "ephemeral"}` en el bloque del system prompt
2. Garantizar que el prefijo cacheable sea >=1024 tokens (Anthropic minimum)
3. Mantener orden estable de bloques entre calls (mismo agent invariant orden)

### R3 -- Orden canonico de bloques en system prompts multi-fuente

Cuando un agente compone su system prompt desde multiples archivos KB, el orden es:

```
[1] CLAUDE.md (entrada raiz canonica)
[2] ARCH_AGENT_PRINCIPLES.md (P0-P14, P16)
[3] RW_ROOT.md (meta-reglas + taxonomia)
[4] WIKI.md (contract humano + ANTI_RATIONALIZATION_REGISTRY)
[5] POLs Always Tier (orden alfabetico por filename)
[6] IDX_* relevantes (orden alfabetico por dominio)
[7] SKILL_* del agente activo (orden alfabetico)
[8] ENT_GOB_DECISIONES + ENT_GOB_PENDIENTES
[9] SPEC_ACTION_ENGINE + SPEC_HOOKS_FAIL_CLOSED (medular)
--- cache_control breakpoint aqui ---
[10] Contexto session-specific (volatil)
[11] User query
```

Cualquier desviacion de este orden invalida el cache prefix. El orden se versiona en este SPEC. Cambios requieren bump semver + 2 versiones de coexistencia (D4 SPEC_ACTION_ENGINE).

### R4 -- TTL discipline

- Default TTL: **5 min** (Anthropic baseline, gratis)
- Sprint largo LOTE_ activo: **1h TTL** (premium 2x cache write, justificable solo si sesion activa >5 min entre calls)
- Sesiones idle >5 min entre calls: aceptar miss, no extender TTL
- Metrica observable (D6 SPEC_ACTION_ENGINE): `cache_hit_ratio` per agent_id, retencion 30 dias

---

## Implementacion por agente

| Agente | Implementador | Accion concreta | Sprint |
|---|---|---|---|
| Claude Projects (CEO) | Anthropic gestiona | Cero accion -- Anthropic cachea automatico con TTL 5min | -- |
| Claude Code (AG-02) | Alejandro | Habilitar `cache_control` en system prompt builder. Reordenar bloques per R3 | Post-S26 |
| Cowork (AG-07) | Cowork mismo | Idem Claude Code | Post-S26 |
| FaberLoom MVP | FaberLoom dev | Implementar desde Fase 3 (prompt caching) per SPEC_FABERLOOM_MVP | Mes 3 |

Para Kimi K2.6, DeepSeek, ChatGPT: documentar politicas equivalentes per-provider en `ENT_PLAT_LLM_PROVIDERS_CACHE_POLICIES.md` cuando se necesite (no urgente).

---

## Metricas de exito

| Metrica | Baseline estimado | Target post-implementacion |
|---|---|---|
| Cache hit ratio (Cowork + Claude Code) | <30% | >70% |
| Costo input mensual agregado | ~$527 | <$100 |
| Latencia media TTFT | actual | -30% en calls cacheadas |

Medicion: 1 semana post-implementacion. Si hit ratio <50%, abrir bug -- probable volatil escondido.

---

## Anti-patrones explicitos

| Anti-patron | Por que falla |
|---|---|
| Header con `Ultima actualizacion` cerca del top | Cada bump invalida cache de TODO el archivo |
| Reordenar bloques entre calls | Cache miss garantizado |
| Bumpear version en system prompt cada session | Idem |
| TTL 1h sin justificacion de uso continuo | Premium 2x sin payoff |
| Cachear data N3/N4 (BIOMETRIC, DISTRIB-SCOPED) sin verificar provider DPA | Conflicto con D9 SPEC_ACTION_ENGINE |

---

## Riesgos asumidos

- Anthropic cambia TTL/pricing/mecanica: documentado, low impact (degrada gradual)
- Multi-provider divergence: cada provider tiene politica propia. R1-R4 aplican a Anthropic primario, otros documentan excepciones
- Volatiles escondidos: posible que existan timestamps en archivos no auditados. Mitigacion: post-implementacion medir hit ratio real, debugging si <50%
- **Hooks fail-closed (Sprint 0 B1) bloquean writes a archivos Always-loaded sin sync script firmado.** Sprint mecanico R1 (timestamp-al-footer) requiere coordinarse con `sync_*_indexa.ps1` con actor `sync_indexa_script`

---

## Changelog

```
v1.0 (2026-05-07): Creacion. Origen: HANDOFF Cowork 28-abr (sesion Claude Projects)
                   actualizado post Sprint 0 (A0 + B0 + B1 ejecutados).
                   Aplica a 4 archivos canonical_docs nuevos post Sprint 0:
                   WIKI.md, POL_BRANCH_PR_v1, POL_ROOT_FILE_CLASSIFICATION_v1,
                   SPEC_HOOKS_FAIL_CLOSED_v1.
```

---

Ultima actualizacion: 2026-05-07 v1.0
Generado por: Cowork (AG-07) -- Arquitecto Ejecutor
