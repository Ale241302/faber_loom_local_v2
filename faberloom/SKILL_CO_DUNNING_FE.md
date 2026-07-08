---
name: SKILL_CO_DUNNING_FE
description: |
  Genera un recordatorio de pago personalizado a partir de una factura vencida,
  incluyendo clave numérica, estado tributario y link de pago. El borrador se
  detiene en HITL antes de envío.
version: 0.1.0
metadata:
  fbl:
    id: SKILL_CO_DUNNING_FE
    type: agent
    architectural_archetype: generator
    domain: COBRANZA
    archetype: routine
    visibility: INTERNAL
    status: SHADOW
    inputs:
      kb_refs:
        - POL_BRAND_VOICE
        - POL_DUNNING_SEQUENCE
    contract:
      outputs:
        - id: dunning_draft
          schema: SCH_DUNNING_DRAFT
          kind: asset
          destination: drafts/queue
          required: true
          requires_human_approval: true
      schema_lock: strict
    state_machine:
      ref: SCH_STATE_MACHINE_BASIC
    golden_samples:
      - id: GS_CO_DUNNING_001
        validates_outputs: [dunning_draft]
        evaluation_use: reference
        added_by: ceo
        added_at: 2026-07-07
    outcome:
      primary: days_sales_outstanding_reduction
      baseline_value: 45
      target_at_60d: "< 35"
      measurement_cadence: weekly
    budget:
      usd_monthly: 15
      hard_cap_usd: 40
      kill_switch:
        enabled: true
        trigger_on:
          - consecutive_failures: 3
    autonomy:
      current_level: 0
      target_level: 1
      promotion_criteria:
        runs_minimum: 100
        acceptance_rate_min: 0.90
    tenant_scope:
      mode: single
      tenants: [default]
---

# SKILL_CO_DUNNING_FE

Este skill genera recordatorios de pago a partir de facturas vencidas. Nunca
envía el mensaje directamente: el borrador siempre pasa por aprobación humana
(HITL) antes de cualquier acción con efecto externo.
