---
id: SPEC_FB_KNOWLEDGE_ATLAS_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE 2026-05-02 (canoniza mockup pantalla kb / namespace kn2)
fecha: 2026-05-02
agente: Cowork (redaccion) + CEO (decision arquitectura)
aplica_a: [FaberLoom]
fuente_verdad: docs/anexos/mockups/mockup_e1_full_navigable.html (pantalla kb · namespace kn2)
relacionado:
  - SPEC_FB_KNOWLEDGE_RIVER_v1.md
  - SPEC_FB_AI_CONTROL_PLANE_v1.md
  - SPEC_FB_VOICE_HUMANIZER_v1.md
  - ARCH_AGENT_PRINCIPLES.md
  - RW_ROOT.md
---

# SPEC_FB_KNOWLEDGE_ATLAS_v1

## Knowledge Atlas · kn2 · canonizacion del mockup

## 1. Por que existe este documento

El mockup implementa Knowledge Atlas como consola medular del capital intelectual. Reemplaza la idea anterior de "Knowledge Base = tabla de documentos" por una consola operativa con 7 vistas, 11 tipos de nodo, grafo SVG navegable e inspector dinamico de 6 modes.

Este SPEC canoniza ese diseno como fuente de verdad. El brief externo "Knowledge & Context" describe la misma idea con otro nombre · usar Knowledge Atlas como nombre canon.

## 2. Frase guia

```
Cada aprendizaje debe encontrar su lugar correcto en el mapa antes de volverse verdad.
Knowledge no es donde se guardan archivos.
Es donde se decide que informacion se vuelve usable, para quien, por cuanto tiempo, con que riesgo y con que impacto.
```

## 3. Estructura · 7 vistas canon

| # | Vista | Que decide |
|---|---|---|
| 1 | Atlas | grafo SVG de nodos conectados con verbos (usa/alimenta/gobierna/produce/consumido_por/aprendio_de/estructura) |
| 2 | River L0-L4 | flujo de aprendizaje 5 capas · personal vs organizacional |
| 3 | Aprendizaje personal | learning candidates AM-facing con Aplicar/Editar/Ignorar |
| 4 | Voice Profile | mini view del Humanizer (ver SPEC_FB_VOICE_HUMANIZER_v1.md) |
| 5 | Context Pack Trace | replay pipeline de un run concreto (Run -> Router -> Sources -> Builder -> Compiler -> Ledger -> Audit) |
| 6 | Impacto | cascade + risk panel + tests + change plan (simulador de cambio) |
| 7 | Governance / Audit | bandeja 4 columnas: Candidates editables / Versions read-only / Signatures / Audit entries inmutables |

## 4. Tipos de nodo · 11

`SRC` (fuente original) · `ENT` (entity / dato) · `SCH` (schema) · `POL` (policy) · `PLB` (playbook) · `SKILL` (capacidad) · `AGENT` (agente) · `OUTPUT` (output verificable) · `MEM` (memoria personal) · `CASE` (replay case) · `VOICE_*` (5 sub-tipos de voz · ver Humanizer)

Cada nodo tiene border-left coloreado por tipo · status pill (VIGENTE/SIGNED/CANDIDATE/STALE/CONFLICTED/BLOCKED/USABLE) · privacy tier (PRIVATE_RAW/TENANT_DERIVED/GLOBAL_PROMOTABLE/RESTRICTED).

## 5. Knowledge River · 5 capas

```
L0 Initial Knowledge   · sources crudas (CSVs, PDFs, exports SAP)
L1 Working Context     · context packs (lo minimo que entra al modelo)
L2 Personal Episodic   · aprendizaje del usuario · NO sale del tenant sin firma
L3 Collective Pool     · candidatos org · requiere committee + checks privacy
L4 Signed Indexed      · verdad del sistema · inmutable · nuevas versiones se archivan
```

Regla canon visible en UI:
```
Auto-add si. Auto-promote nunca.
L2 pertenece al usuario. L3 pertenece a la organizacion.
```

## 6. Inspector dinamico · 6 modes

`node` (default · 7 r-cards: Health/Root placement/Privacy/Consumers/Routing economy/Audit/Actions) · `trace` · `impact` · `candidate` · `version` · `audit`

Reglas:
- Candidate inspector es editable (campos proposed_text/classification/destination/scope/reason)
- Version inspector es read-only (solo diff + rollback candidate)
- Audit inspector es read-only (solo replay + integrity check)

## 7. Context Pack Trace · pipeline canon

```
01 RUN -> 02 ROUTER DECISION -> 03 SOURCES -> 04 BUILDER (Included/Excluded) -> 05 COMPILER -> 06 LEDGER -> 07 AUDIT
```

Sources (5 fuentes evaluadas): Agent Map · KN/Root · Memory · Policies · **Voice Overlay** (Humanizer)

Builder produce context pack mininimo:
- Naive retrieval: 62k tokens
- Rooted context pack: 3.8k tokens
- Ahorro: 93.8%

## 8. Impacto · simulador de cambio

5 secciones canon:
- A. Change Target (editable)
- B. Impact Cascade (jerarquica · target -> skill -> agent -> output -> client_facing)
- C. Risk Panel (6 risks: stale/policy/customer-facing/margin/privacy/regression)
- D. Required Tests (replay cases + policy checks + schema + HITL)
- E. Change Plan (DRAFT · enviable a Governance)

Acciones permitidas: crear change_candidate · enviar a Governance · correr arena · notificar consumidores · bloquear uso temporal.
Acciones prohibidas: editar nodo firmado · borrar dependencia · modificar policy/schema/entity sin candidate.

## 9. Governance/Audit · 4 secciones bandeja

```
Candidates (editables) · Versions (read-only diff/rollback) · Signatures (firma controlada) · Audit Entries (inmutables)
```

Reglas:
```
Candidate = editable
Version firmada = read-only
Audit entry = read-only
Rollback = candidate, no borrado
Knowledge firmado no se edita in-place: se archiva y se crea nueva version.
```

## 10. Roles soportados (Ver-como)

`Owner · AM · Curator · Auditor`

Cada rol cambia que acciones son visibles en el inspector:
- AM: Aplicar / Editar / Ignorar
- Curator: Promote / Reject / Freeze
- Auditor: Diff / Trace ID / Export evidencia
- Owner: Todo

## 11. Que NO esta en este SPEC

- Backend de nodes/edges (vive en SPEC_FB_DATA_MODEL_v1.md)
- Action Engine (vive en SPEC_ACTION_ENGINE.md)
- Voice Profile (vive en SPEC_FB_VOICE_HUMANIZER_v1.md)
- AI routing/keys (vive en SPEC_FB_AI_CONTROL_PLANE_v1.md)

## 12. Changelog

- v1.0 (2026-05-02) · Canonizacion del mockup kb / kn2 (7 vistas + 11 nodos + Voice integration). Source-of-truth para Foundation Beta E1.
