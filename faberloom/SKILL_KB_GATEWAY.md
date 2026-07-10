---
name: "Gateway transaccional KB"
description: "Legacy MWT skill migrated to manifest v2. [PENDIENTE — NO INVENTAR] completa instrucciones, golden samples y tool allowlist antes de promover."
version: "1.0.0"
metadata:
  fbl:
    id: "SKILL_KB_GATEWAY"
    type: "agent"
    architectural_archetype: "validator"
    archetype: "validator"
    domain: "Plataforma"
    visibility: "INTERNAL"
    status: "SHADOW"
    inputs:
      - id: request
        type: text
    outcome:
      primary: "generate_output"
    budget:
      kill_switch:
        enabled: true
        max_cost_usd: 1.0
    contract:
      outputs:
        - id: primary_output
          kind: asset
          destination: "external/ceo_review"
          requires_human_approval: true
    learning_consolidation:
      target: "none"
      auto_apply: false
---

# Gateway transaccional KB

Legacy MWT skill imported as SHADOW. Original source: `docs/SKILL_KB_GATEWAY.md`.

**Estado:** SHADOW — requiere revisión humana antes de activación.
**Archetype:** validator.

## Pendientes explícitos

- [PENDIENTE — NO INVENTAR] Completar instrucciones de runtime específicas del dominio.
- [PENDIENTE — NO INVENTAR] Definir tool allowlist y triggers reales.
- [PENDIENTE — NO INVENTAR] Reemplazar golden samples de ejemplo por casos reales validados.
