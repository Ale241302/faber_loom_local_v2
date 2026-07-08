---
name: SKILL_FE_STATUS_CHECK
description: |
  Valida el estado de comprobantes de facturación electrónica contra fuentes
  oficiales (ATV CR / SAT MX / DIAN CO) y genera un reporte de discrepancias
  con evidencia citada.
version: 0.1.0
metadata:
  fbl:
    id: SKILL_FE_STATUS_CHECK
    type: agent
    architectural_archetype: validator
    domain: FISCALIDAD
    archetype: routine
    visibility: INTERNAL
    status: SHADOW
    inputs:
      kb_refs:
        - POL_FE_ATV_CR
        - POL_FE_SAT_MX
        - POL_FE_DIAN_CO
    contract:
      outputs:
        - id: status_report
          schema: SCH_FE_STATUS_REPORT
          kind: asset
          destination: drafts/queue
          required: true
          requires_human_approval: true
      schema_lock: strict
    state_machine:
      ref: SCH_STATE_MACHINE_BASIC
    golden_samples:
      - id: GS_FE_STATUS_001
        validates_outputs: [status_report]
        evaluation_use: reference
        added_by: ceo
        added_at: 2026-07-07
    outcome:
      primary: validation_coverage_pct
      baseline_value: 0
      target_at_60d: "> 95"
      measurement_cadence: weekly
    budget:
      usd_monthly: 10
      hard_cap_usd: 25
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

# SKILL_FE_STATUS_CHECK

Este skill consulta el estado de comprobantes electrónicos en fuentes oficiales.
Cada afirmación sobre un comprobante debe ir acompañada de un evidence bundle
con URL de consulta, fecha/hora de captura y hash del contenido.
