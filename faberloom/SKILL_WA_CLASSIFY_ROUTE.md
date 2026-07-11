---
name: "Clasificación y ruteo de mensajes WhatsApp"
description: "Skill en estado DRAFT. Estructura de template disponible; requiere localización LATAM, conectores reales y golden cases validados antes de promover. [PENDIENTE — NO INVENTAR]"
version: "0.1.0"
metadata:
  fbl:
    id: "SKILL_WA_CLASSIFY_ROUTE"
    type: "agent"
    architectural_archetype: "generator"
    archetype: "generator"
    domain: "WHATSAPP"
    visibility: "INTERNAL"
    status: "DRAFT"
    pack_id: "wtp_whatsapp_formal"
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

# Clasificación y ruteo de mensajes WhatsApp

**ID:** `SKILL_WA_CLASSIFY_ROUTE`

**Estado:** DRAFT

Estructura de template disponible; requiere localización LATAM y golden cases reales.

## Pendientes explícitos

- Localizar template a contexto LATAM (NIIF, derecho civil, Código de Trabajo).
- Definir tool allowlist y conectores reales.
- Reemplazar placeholders por golden cases reales validados.

*[PENDIENTE — NO INVENTAR]*
