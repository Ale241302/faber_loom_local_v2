---
name: "Contratación y código de trabajo"
description: "Skill en estado DRAFT. Estructura de template disponible; requiere localización LATAM, conectores reales y golden cases validados antes de promover. [PENDIENTE — NO INVENTAR]"
version: "0.1.0"
metadata:
  fbl:
    id: "SKILL_HR_CONTRATACION"
    type: "agent"
    architectural_archetype: "generator"
    archetype: "generator"
    domain: "RRHH"
    visibility: "INTERNAL"
    status: "DRAFT"
    pack_id: "wtp_rrhh"
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

# Contratación y código de trabajo

**ID:** `SKILL_HR_CONTRATACION`

**Estado:** DRAFT

Estructura de template disponible; requiere localización LATAM y golden cases reales.

## Pendientes explícitos

- Localizar template a contexto LATAM (NIIF, derecho civil, Código de Trabajo).
- Definir tool allowlist y conectores reales.
- Reemplazar placeholders por golden cases reales validados.

*[PENDIENTE — NO INVENTAR]*
