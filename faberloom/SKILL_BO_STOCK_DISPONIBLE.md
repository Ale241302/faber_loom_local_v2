---
name: "Consulta de stock disponible"
description: "Skill en estado DEFINITION_PENDING. El alcance, entradas, conectores y golden cases aún no han sido definidos. [PENDIENTE — NO INVENTAR]"
version: "0.1.0"
metadata:
  fbl:
    id: "SKILL_BO_STOCK_DISPONIBLE"
    type: "agent"
    architectural_archetype: "generator"
    archetype: "generator"
    domain: "BODEGA"
    visibility: "INTERNAL"
    status: "DEFINITION_PENDING"
    pack_id: "wtp_bodega_importacion"
    contract:
      outputs:
        - id: "primary_decision"
          kind: "decision"
          required: true
    outcome:
      primary: "definition_pending"
    tenant_scope:
      mode: "single"
---

# Consulta de stock disponible

**ID:** `SKILL_BO_STOCK_DISPONIBLE`

**Estado:** DEFINITION_PENDING

GAP sin definición de alcance; no se ejecuta hasta que se especifique.

## Pendientes explícitos

- Definir alcance, entradas y salidas del skill.
- Identificar conectores y fuentes de evidencia.
- Diseñar golden cases con datos reales del tenant.

*[PENDIENTE — NO INVENTAR]*
