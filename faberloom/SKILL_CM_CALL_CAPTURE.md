---
name: "Captura de llamadas comerciales"
description: "Skill en estado DRAFT. Estructura de template disponible; requiere localización LATAM, conectores reales y golden cases validados antes de promover. [PENDIENTE — NO INVENTAR]"
version: "0.1.0"
metadata:
  fbl:
    id: "SKILL_CM_CALL_CAPTURE"
    type: "agent"
    architectural_archetype: "generator"
    archetype: "generator"
    domain: "COMERCIAL"
    visibility: "INTERNAL"
    status: "DRAFT"
    pack_id: "wtp_comercial"
    contract:
      outputs:
        - id: "primary_decision"
          kind: "decision"
          required: true
    outcome:
      primary: "ready_when_golden_cases_verified"
    tenant_scope:
      mode: "single"
---

# Captura de llamadas comerciales

**ID:** `SKILL_CM_CALL_CAPTURE`

**Estado:** DRAFT

Estructura de template disponible; requiere localización LATAM y golden cases reales.

## Pendientes explícitos

- Localizar template a contexto LATAM (NIIF, derecho civil, Código de Trabajo).
- Definir tool allowlist y conectores reales.
- Reemplazar placeholders por golden cases reales validados.

*[PENDIENTE — NO INVENTAR]*
