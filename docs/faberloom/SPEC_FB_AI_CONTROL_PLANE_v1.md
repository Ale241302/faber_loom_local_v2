---
id: SPEC_FB_AI_CONTROL_PLANE_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE 2026-05-02 (canoniza mockup iakeys v2 / iak2)
fecha: 2026-05-02
agente: Cowork (redaccion) + CEO (decision arquitectura)
aplica_a: [FaberLoom]
fuente_verdad: docs/anexos/mockups/mockup_e1_full_navigable.html (pantalla iakeys · namespace iak2)
relacionado:
  - SPEC_ACTION_ENGINE.md
  - SPEC_LLM_ROUTING_ARCHITECTURE.md
  - SPEC_AUDIT_MODULE.md
  - SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1.md
  - POL_DATA_CLASSIFICATION (v1.4)
referencia_externa: brief externo "FABERLOOM / KNOWLEDGE MWT BRIEF MAESTRO" (chat externo · referencia complementaria · mock manda)
---

# SPEC_FB_AI_CONTROL_PLANE_v1

## AI Control Plane · iak2 · canonizacion del mockup

## 1. Por que existe este documento

El mockup `mockup_e1_full_navigable.html` implementa la pantalla iakeys (AI Control Plane) con 8 tabs, 15 inspectors dinamicos, 12 entidades mock y reglas de seguridad explicitas en UI. Este SPEC canoniza ese diseno como source-of-truth operativo para FaberLoom Foundation Beta E1.

El brief externo "FABERLOOM / KNOWLEDGE MWT" (escrito por LLM externo) cubre conceptualmente lo mismo pero con sobre-fragmentacion del modelo de datos. El mock manda. El brief sirve como referencia.

## 2. Tesis del modulo

```
No configuramos modelos. Configuramos cadenas de inteligencia gobernadas.
La Arena recomienda. Governance aprueba. Routing ejecuta. Ledger demuestra.
```

Cada tab del Control Plane responde a un slice de esa cadena.

## 3. Estructura · 8 tabs canon

| # | Tab | Que decide |
|---|---|---|
| 1 | Overview | findings + profiles activos + candidates pending |
| 2 | Secure Keys | que provider esta provisionado, vault state, DPA, modalities |
| 3 | AI Profiles | que receta operativa esta disponible (prep+pack+producer+final+gate) |
| 4 | Agent Bindings | que agente+skill consume que profile |
| 5 | Routing Inheritance | cascade tenant->workspace->profile->binding->skill_contract->run + blocked caps |
| 6 | Prompting Profiles | que estrategia de prompt por modelo familia + prompt pack recipes |
| 7 | Arena / Eval Lab | ranking de recetas + fallback ladder + test suites |
| 8 | Ledger & Governance | token entries + governance entries + policy blocks + candidates queue |

## 4. Inspector dinamico · 15 modes

Cada item clickeable abre el inspector derecho en uno de estos modes:

`provider · profile · binding · inheritance · blocked_capability · prompt_profile · prompt_recipe · arena_recipe · fallback_rule · test_suite · ledger_entry · governance_entry · policy_block · diagnostic · candidate`

Cada inspector responde con la misma estructura:

```
- Que es
- Quien lo controla
- Que afecta
- Que se puede editar
- Que NO se puede editar (bloque ⛔ explicito)
- Policy aplicada
- Evidencia / ledger / audit
- Acciones permitidas
- Guardrails
```

No usar modales. Inspector derecho es el unico lugar de detalle.

## 5. Entidades mock declaradas

12 colecciones en el mock (mantener sincronizadas con backend cuando exista):

`IAK_PROVIDERS` (4) · `IAK_PROFILES` (6) · `IAK_BINDINGS` (10) · `IAK_INHERITANCE` (6 layers) · `IAK_BLOCKED_CAPS` (6) · `IAK_PROMPT_PROFILES` (4 model families) · `IAK_PROMPT_RECIPES` (3) · `IAK_ARENA_RECIPES` (4 ladder) · `IAK_FALLBACK_RULES` (6) · `IAK_LEDGER_ENTRIES` (2 con campos canon) · `IAK_GOV_ENTRIES` (2) · `IAK_POLICY_BLOCKS` (3) · `IAK_DIAGNOSTIC` (5) · `IAK_CANDIDATES` (push-able)

## 6. Reglas inquebrantables (visibles en UI)

| # | Regla | Implementacion en mock |
|---|---|---|
| 1 | Keys belong to the tenant. Agents only receive permissions | secret_ref / masked_key · key_visibility:never_exposed |
| 2 | Skills nunca llaman providers directo | direct_provider_sdk en blocked_caps |
| 3 | Toda llamada LLM pasa por Action Engine | Skill -> Action Engine -> Provider Adapter |
| 4 | AI Profile es policy operativa, no modelo | profile encapsula prep+pack+producer+final+gate |
| 5 | Working language can change. Facts cannot | Prompt Profiles con working_language vs output_language |
| 6 | Deny gana sobre allow | Routing Inheritance · cascade declarada |
| 7 | Hijo restringe · no amplia sin Governance | capability_request_candidate obligatorio para ampliar |
| 8 | Fallback puede bajar costo o cambiar provider · nunca bajar seguridad | preserves_security:true en cada fallback rule |
| 9 | Cheap prep no reemplaza strong producer | recipe = prep + producer + final pass |
| 10 | Audit log es inmutable | ledger entries read-only · solo rollback_candidate |

## 7. Acciones prohibidas (explicitas en cada inspector)

```
- Show key complete
- Copy key
- Assign key to agent
- Use outside Action Engine
- Bypass Ledger
- Direct provider SDK
- Quitar final pass cliente-facing sin Governance
- Habilitar video/image/audio generation directo
- Editar ledger historico
- Borrar audit
- Modificar version firmada in-place
```

## 8. Candidates · 9 tipos

Toda accion que cambia estado significativo crea candidate (no aplica directo):

`routing_ladder_candidate · ai_profile_candidate · prompt_recipe_candidate · output_pin_candidate · provider_policy_review · capability_request_candidate · policy_exception_candidate · rollback_candidate · budget_adjustment_candidate`

Estados: `DRAFT -> PENDING_GOVERNANCE -> APPROVED | REJECTED`

## 9. Topbar canon

```
[AI CONTROL PLANE · TENANT MWT · N active provider · M profiles · K bindings]
[search] [Diagnostico] [Run Arena] [+ Candidate] [Ver-como Owner|Admin|Operator|Auditor]
```

`Ver-como` cambia que acciones son visibles segun rol.

## 10. Que NO esta en este SPEC

- Backend real (vive en SPEC_FB_DATA_MODEL_v1.md)
- Implementacion del Action Engine (vive en SPEC_ACTION_ENGINE.md)
- Routing matrix runtime (vive en SPEC_LLM_ROUTING_ARCHITECTURE.md)
- Audit hash chain (vive en SPEC_AUDIT_MODULE.md)
- Voice Profile (vive en SPEC_FB_VOICE_HUMANIZER_v1.md)
- Knowledge Atlas (vive en SPEC_FB_KNOWLEDGE_ATLAS_v1.md)

## 11. Changelog

- v1.0 (2026-05-02) · Canonizacion del mockup iakeys v2 / iak2 (commit pushado al canon). Source-of-truth operativo para Foundation Beta E1.
