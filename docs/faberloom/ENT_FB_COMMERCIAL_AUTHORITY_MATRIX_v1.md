---
id: ENT_FB_COMMERCIAL_AUTHORITY_MATRIX_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma
type: entity
stamp: VIGENTE 2026-04-30
fecha: 2026-04-30
agente: Cowork (redaccion) + CEO (decisiones) + ChatGPT (auditoria R2+R3)
aplica_a: [FaberLoom]
implementa: ENT_FB_VERTICAL_SPEC_OBJECT_v1 (authority_overrides)
relacionado_con:
  - ENT_FB_VERTICAL_SPEC_OBJECT_v1
  - ENT_FB_QUOTING_SOURCE_OF_TRUTH_v1
  - ENT_FB_RFQ_EXCEPTION_TAXONOMY_v1
  - ARCH_AGENT_PRINCIPLES (HITL P3 absoluto · core sealed)
referencias_externas:
  - SAP CPQ Approval Rules (patron de referencia)
  - Salesforce CPQ Advanced Approvals (patron de referencia)
---

# ENT_FB_COMMERCIAL_AUTHORITY_MATRIX_v1
## Matriz canonica de autoridad para decisiones comerciales B2B

## 1. Proposito

Define **quien decide que** en cada decision comercial del flow de cotizacion. Aterriza la Autonomy Ladder INTERNO (L0-L5 sealed v2) en autoridad operacional concreta y medible.

5 niveles de autoridad · 7 decisiones canonicas · lista de 8 decisiones NUNCA delegables a agente solo.

> **Insight ChatGPT R2:** "No existe set canonico universal. Lo defendible es copiar el patron CPQ: reglas de aprobacion por descuento, monto, violacion de regla, workflow/status y aprobadores." (referencia SAP CPQ + Salesforce CPQ Advanced Approvals)

## 2. Los 5 niveles de autoridad

```
Nivel 1 · agente solo
  → sub-agente decide y ejecuta sin pasar por humano
  → SOLO permitido para decisiones reversibles, sin compromiso comercial
  → ejemplos: clasificacion intent, summary, lookup, transcript

Nivel 2 · agente + AM
  → sub-agente prepara · AM aprueba/edita antes de salir
  → P3 draft-first absoluto aplica
  → ejemplos: respuesta status_inquiry, draft email simple

Nivel 3 · AM
  → AM toma la decision · sub-agentes son herramientas
  → ejemplos: precio default, plazo entrega normal

Nivel 4 · AM + supervisor
  → AM prepara · supervisor co-aprueba antes de envio
  → ejemplos: descuento fuera politica, sustitucion tecnica con cambio cert

Nivel 5 · CEO
  → CEO escala explicito · ningun nivel inferior decide
  → ejemplos: margen bajo umbral minimo, contratos con penalidad alta
```

## 3. Las 7 decisiones canonicas con default authority

| # | Decision | Default | Escalacion automatica | Nunca agente solo |
|---|---|---|---|---|
| 1 | Precio | AM (Nivel 3) | AM+supervisor (4) si descuento >politica | si |
| 2 | Margen | AM+supervisor (Nivel 4) | CEO (5) si bajo `vertical_spec.pricing_overrides.margin_floor_default` | si |
| 3 | Credito | AM+supervisor (Nivel 4 con fuente finance/ERP) | FAIL+notif AM si `credit_status=blocked` | si |
| 4 | Sustitucion SKU | agente+AM (Nivel 2) si equivalencia tecnica certificada | AM+supervisor (4) si cambia certificacion/puntera/plantilla/norma/pais | si para sustitucion no identica |
| 5 | Plazo entrega | AM (Nivel 3) si fuente proveedor/3PL vigente | AM+supervisor (4) si penalidad/licitacion/contractual | si para promesa contractual |
| 6 | Promesa stock | agente+AM (Nivel 2) solo si ATP fresco | AM (3) si parcial · AM+supervisor (4) si reserva grande/cliente estrategico | si si stock parcial >10% pedido |
| 7 | Envio proforma final | NUNCA agente solo · siempre AM minimo (Nivel 3) | AM+supervisor (4) en clientes tier_platinum o monto >umbral configurable | absoluto |

## 4. Lista NEVER agente solo (8 decisiones)

Son decisiones donde **bajo ninguna circunstancia** el agente decide sin humano. Si el sistema intenta auto-decidir → bug critico · auto-bloqueo y log severity:critical.

1. **Precio especial** (descuento fuera lista vigente)
2. **Margen bajo umbral minimo** (debajo de margin_floor_default)
3. **Credito** (cualquier accion sobre credit_status)
4. **Sustitucion tecnica no identica** (cambio cert · puntera · plantilla · norma · pais)
5. **Promesa stock con stock parcial >10%**
6. **Compromiso entrega con penalidad contractual**
7. **Excepcion pais regulatoria** (override de country rules)
8. **Envio proforma final al cliente** (NUNCA send sin firma humana)

## 5. Como se determina la autoridad para una decision dada

```
1. Sistema identifica decision_type del output (precio, margen, sustitucion, etc)
2. Carga default authority de la matriz (tabla seccion 3)
3. Verifica vertical_spec_object.authority_overrides[decision_type]
   ├─ Si existe override → usa override
   └─ Si no → usa default
4. Verifica triggers de escalacion automatica:
   ├─ Descuento > politica → escala
   ├─ Margen < margin_floor → escala
   ├─ Cliente tier_platinum + monto >umbral → escala
   ├─ Pedido en pais con regulacion especial → escala
   └─ Sub-agente confidence < threshold → escala
5. Verifica lista NEVER agente solo
   └─ Si match → forzar nivel >=AM (3) sin importar default
6. Resultado: authority_required = max(default, escalacion_auto, never_agente_solo_floor)
```

## 6. Action-risk metadata en cada tool

Consistente con `ENT_PLAT_ACTION_REGISTRY` y proyect_faberloom_architecture v2 ("ACTION-RISK REGISTRY MUST v1"). Cada tool/action lleva metadata estructurada:

```yaml
action:
  action_id: send_proforma_to_client
  risk_class: critical
  approval_mode: human_only  # never_agente
  reversible: false
  customer_visible: true
  financial_impact: true
  legal_effect: true
  source_of_truth: pricing_master + customer_terms
  required_authority: AM_minimum
  hitl_gate: P3_absolute
```

Policy engine usa este metadata · LLM no clasifica risk final.

## 7. Estructura YAML del tenant config

```yaml
authority_matrix_config:
  tenant_id: mwt
  vertical_spec_object: safety_footwear

  # Defaults heredados de la matriz canonica
  use_canonical_defaults: true

  # Overrides especificos del tenant
  overrides:
    - decision: precio
      default_level: AM
      override_level: AM_supervisor
      condition: "discount_percent > 12"
      reason: "MWT politica interna max 12% discount sin escalar"

    - decision: envio_proforma_final
      default_level: AM
      override_level: AM_supervisor
      condition: "amount_usd > 25000"
      reason: "umbral firma supervisor MWT para deals grandes"

  # Configuracion de aprobadores
  approvers:
    AM:
      - email: alvaro@mwt.cr
      - email: vendedor1@mwt.cr
    AM_supervisor:
      - email: alvaro@mwt.cr  # CEO actua como supervisor en MWT v1
    CEO:
      - email: alvaro@mwt.cr
    finance:
      - email: contabilidad@mwt.cr

  # SLA per nivel de aprobacion
  sla:
    AM_review_hours: 4
    supervisor_review_hours: 24
    CEO_review_hours: 48
    out_of_hours_handler: notify_backup_AM_then_escalate
```

## 8. Audit obligatorio

Cada decision sometida a authority matrix genera evento:

```yaml
event: authority_decision
decision_id: <uuid>
decision_type: precio | margen | credito | sustitucion | plazo | stock | proforma_final
authority_required: AM | AM_supervisor | CEO
escalation_reason: discount_above_policy | margin_below_floor | tier_platinum_high_amount | etc
approver: <email>
approved_at: <ISO8601>
approval_action: approved | edited | rejected | escalated
sla_status: on_time | breached
trace_id: <id>
```

Va al audit log con SHA-chain.

## 9. Comportamiento out-of-hours

Cuando AM/supervisor no esta disponible:
- Escalar al backup designado en `sla.out_of_hours_handler`
- Si backup tampoco responde en SLA → escalar al siguiente nivel
- Si CEO no responde en `CEO_review_hours` → mantener BLOCKED y notificar al CEO al siguiente login

NUNCA auto-aprobar por timeout. NUNCA enviar al cliente sin firma humana.

## 10. Reglas inquebrantables

1. **NUNCA agente solo en las 8 decisiones de la lista NEVER.** Bug critico si ocurre.
2. **HITL P3 draft-first absoluto** se mantiene · este matriz no lo sobrescribe.
3. **Authority cambios requieren versioning del config** · cambios sin SHADOW 30d prohibidos.
4. **Cliente NUNCA ve la matriz.** Es interno · audit log puede compartirse con cliente solo si `customer_visible:true` esta marcado.
5. **NUNCA auto-aprobar por timeout.** Out-of-hours escalando · no por defecto.
6. **vertical_spec_object.authority_overrides es la unica forma de modificar defaults canonicos** · no hardcoded patches.

## 11. Pendientes v1.1

1. Approver pools dinamicos (en lugar de email lists hardcoded)
2. Vacation handling automatico (out-of-office calendar integration)
3. Approval delegation explicita (Alvaro → asistente para X dias)
4. Dashboard de SLA breaches per approver
5. Aprovacion movil con autenticacion fuerte (FIDO2 o equivalente)

## Changelog
- 2026-04-30 v1.0 VIGENTE: Creacion inicial post R2+R3. 5 niveles de autoridad con definiciones operacionales · 7 decisiones canonicas con defaults + escalacion automatica + flag never_agente_solo · lista canonica 8 NEVER agente solo (precio especial · margen bajo · credito · sustitucion no identica · promesa stock parcial >10% · compromiso con penalidad · excepcion pais · envio proforma final) · referencia patron SAP CPQ + Salesforce CPQ · accion-risk metadata integrada per ENT_PLAT_ACTION_REGISTRY · vertical_spec_object.authority_overrides como unico mecanismo modificacion · audit event schema · comportamiento out-of-hours sin auto-aprobacion · 6 reglas inquebrantables.

## Stamp
VIGENTE 2026-04-30 — Aterriza Autonomy Ladder INTERNO en autoridad operacional medible. Define que NUNCA delegar a agente solo (8 decisiones · lista cerrada). Implementacion: tenant config carga matriz canonica + overrides per vertical_spec_object.
