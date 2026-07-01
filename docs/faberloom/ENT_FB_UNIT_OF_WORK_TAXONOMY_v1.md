---
id: ENT_FB_UNIT_OF_WORK_TAXONOMY_v1
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Plataforma
type: entity
stamp: DRAFT 2026-05-02 — punto ciego mas peligroso R7 · nombrado · NO implementado
fecha: 2026-05-02
agente: Cowork (redaccion) + ChatGPT (auditoria R7)
aplica_a: [FaberLoom]
status_motivo: |
  ChatGPT R7: "Unit of Work + scoped permissions es el punto ciego MAS peligroso.
  Software houses y legal lo exponen primero · en primer piloto serio · semana 2 NO ano 2.
  Rompe RBAC + Knowledge River + Privacy Tiers + User Learning + Committee + Audit + Evidence Bundle."
  
  Esta pieza queda NOMBRADA (DRAFT) · NO implementada.
  Implementacion al primer vertical regulado activo (legal · software · etc).
relacionado_con:
  - SPEC_FB_AUTH_TENANT_RBAC_v1 (necesita extension client/matter scope)
  - ENT_FB_VERTICAL_CANDIDATES_v1
  - SPEC_FB_KNOWLEDGE_RIVER_v1.1
  - POL_FB_KR_PRIVACY_TIERS_v1.1
  - SPEC_FB_DMS_INTEGRATION_v1 (DMS doc usually attached to unit_of_work)
origen: ChatGPT R7 punto ciego #1 (mas peligroso) · "concepto matter polisemico"
---

# ENT_FB_UNIT_OF_WORK_TAXONOMY_v1
## Taxonomia canonica de unidades de trabajo cross-vertical

## 1. Proposito · por que es punto ciego MAS peligroso

R7 critical: cada vertical regulado tiene su propio concepto de "unidad de trabajo" (matter · encounter · transaction · project · sprint · incident). Si NO se canoniza la taxonomia · cada vertical inventa nombres y permisos distintos · rompe:

| Pieza canonizada | Como rompe sin unit_of_work |
|---|---|
| RBAC/Auth | permisos por tenant son demasiado gruesos · faltan client/matter/project scope |
| Knowledge River | aprendizaje se enruta mal · lo de un cliente termina en template · lo de un expediente como patron funcional |
| Privacy Tiers | TIER 4 RESTRICTED no tiene scope claro (hasta donde llega un "cliente"?) |
| User Learning | patterns capa 1 mezclan multiples clientes/proyectos del mismo AM |
| Committee | promotion confunde scope (matter-specific va al template global) |
| Audit | trace_id sin matter_id queda colgado |
| Evidence Bundle | bundle no asociable a unidad correcta |

**Cuando explota:** primer piloto serio con multi-cliente per-tenant · semana 2 · NO ano 2.

## 2. Status

**DRAFT** · pieza NOMBRADA · NO implementada.

Implementacion: cuando primer vertical regulado se active (legal o software · post-MWT). En MWT cotizacion v1 · `unit_of_work = quote_id` actua como suficiente · no se requiere taxonomia.

## 3. Taxonomia canonica per vertical

```yaml
unit_of_work_taxonomy:
  
  safety_footwear (MWT actual):
    canonical: quote
    aliases: ["proforma", "cotizacion"]
    scope_dimensions: [tenant_id, customer_id, quote_id]
    privilege_inherited: TENANT_DERIVED
    typical_lifecycle: [draft, sent, won, lost, expired]
  
  legal_practice:
    canonical: matter
    aliases: ["expediente", "caso"]
    scope_dimensions: [tenant_id, client_id, matter_id, sub_agent_id, document_class]
    privilege_inherited: LEGAL_PRIVILEGED (TIER 4)
    typical_lifecycle: [intake, conflict_check_pending, active, stayed, settlement_pending, closed, archived, restricted_hold]
    matter_team_concept: SI · permisos per matter team membership
  
  software_factory:
    canonical: project
    sub_units: [repo, sprint, PR, deployment, incident]
    scope_dimensions: [tenant_id, client_id, project_id, repo_id, environment, sub_unit_type]
    privilege_inherited: NDA_PROTECTED + IP_RESTRICTED
    typical_lifecycle_project: [discovery, active, maintenance, archived]
    typical_lifecycle_sprint: [planned, active, completed]
    typical_lifecycle_PR: [open, in_review, approved, merged, closed]
    typical_lifecycle_incident: [detected, investigating, resolved, postmortem]
    multi_unit_simultaneo: SI · permisos heterogeneos per sub-unit
  
  medical_regulated:
    canonical: encounter
    aliases: ["episode", "patient_case"]
    scope_dimensions: [tenant_id, patient_id, encounter_id, provider_id, specialty]
    privilege_inherited: PHI (TIER 4)
    typical_lifecycle: [scheduled, active, completed, follow_up_required, closed]
    cross_encounter_continuity: SI · paciente con multiple encounters relacionados
  
  financial_advisory:
    canonical: account
    sub_units: [transaction, portfolio, recommendation]
    scope_dimensions: [tenant_id, client_id, account_id, sub_unit_type]
    privilege_inherited: KYC_PROTECTED (TIER 4)
    typical_lifecycle_account: [opening, active, frozen, closed]
    multi_account_per_client: SI
  
  compliance_audit:
    canonical: audit_cycle
    sub_units: [control_test, finding, remediation_action]
    scope_dimensions: [tenant_id, audited_entity_id, audit_cycle_id, control_id]
    privilege_inherited: AUDIT_RESTRICTED (TIER 4)
    typical_lifecycle: [planning, fieldwork, reporting, remediation_tracking, closed]
  
  industrial_HSE:
    canonical: work_order
    sub_units: [incident, batch, RFQ, production_run]
    scope_dimensions: [tenant_id, facility_id, work_order_id, sub_unit_type]
    privilege_inherited: HSE_RESTRICTED (TIER 4 si incidente · sino TENANT_DERIVED)
    typical_lifecycle: depende del sub_unit
  
  insurance:
    canonical: claim
    sub_units: [policy, underwriting_case]
    scope_dimensions: [tenant_id, policyholder_id, claim_id, sub_unit_type]
    privilege_inherited: PHI + KYC + LEGAL (mezclado · TIER 4)
    typical_lifecycle_claim: [reported, investigating, evaluating, settling, paid, denied, closed]
```

## 4. Scope dimensions canonicas

Cada unit_of_work declara dimensiones de scope obligatorias para RBAC + Knowledge River:

```yaml
access_scope_dimensions_canonicas:
  - tenant_id: ALWAYS (RLS Postgres)
  - client_id: si vertical tiene multi-cliente per-tenant
  - unit_of_work_id: ALWAYS (matter/encounter/project/etc)
  - sub_unit_id: si vertical tiene sub-units (PR/incident/finding/etc)
  - sub_agent_id: si sub-agent tiene clearance distinto
  - data_class: privacy tier (PRIVATE_RAW · TENANT_DERIVED · GLOBAL_PROMOTABLE · TIER 4)
  - action: lectura/escritura/promote/aprobar/etc
```

## 5. Knowledge routing por unit_of_work · canonico R7

R7: distincion knowledge funcional vs procesal NO es 2-fold · es **4-fold** cross-vertical:

```yaml
knowledge_routing:
  funcional_heredable:
    description: "patterns reusables cross-cliente"
    scope: tenant (con anonimizacion)
    promotable_to_committee: SI
    examples:
      legal: "checklist despido injustificado"
      software: "PR review patterns"
      medical: "sintomas comunes per condicion"
  
  procesal_cliente_especifico:
    description: "queda en cliente · NO heredable cross-cliente"
    scope: client_id
    promotable_to_committee: NO
    examples:
      legal: "Cliente ABC exige aprobacion CFO"
      software: "Cliente XYZ usa algoritmo propietario"
      medical: "Paciente Ana es alergica a X"
  
  contextual_unit_of_work:
    description: "queda en matter/encounter/project · NO heredable"
    scope: unit_of_work_id
    promotable_to_committee: NO
    examples:
      legal: "Este expediente tiene testigo contradictorio"
      software: "Este sprint tiene blocker en X"
      medical: "Esta cirugia tuvo complicacion Y"
  
  stack_environment_configuracion:
    description: "depende del stack/version · contextual tecnico"
    scope: tenant + version_specific
    promotable_to_committee: SI con metadata tecnica
    examples:
      software: "Next 15 + Supabase + RLS"
      industrial: "Linea produccion 3 con calibracion X"
      medical: "Hospital usa formulario X"
```

## 6. Reglas de routing canonicas

1. **Knowledge funcional puede subir a comite** (capa 2) con anonimizacion fuerte
2. **Knowledge procesal-cliente NUNCA sale del client_id scope**
3. **Knowledge contextual-unit_of_work NUNCA sale del unit_of_work scope** (incluso dentro del mismo cliente)
4. **Knowledge stack/environment promotable con metadata tecnica explicita** (version · tech version)
5. **Cross-tenant promotion (L3→L4)** requiere los 7 checks privacy YA canonizados (POL_FB_KR_PRIVACY_TIERS_v1.1)
6. **Sub-unit del mismo unit_of_work puede compartir contexto** (ej: PRs del mismo sprint comparten knowledge sprint)
7. **Sub-unit cross-unit_of_work NO comparte contexto** (PR de sprint A no comparte con sprint B salvo con promote explicit)

## 7. Implicaciones para piezas canonizadas

| Pieza | Cambio cuando se implemente UNIT_OF_WORK |
|---|---|
| `SPEC_FB_AUTH_TENANT_RBAC_v1` | Extension v1.1: agregar `unit_of_work_id`, `client_id`, `sub_unit_id` a access_scope · permission_grant per scope dimension |
| `SPEC_FB_KNOWLEDGE_RIVER_v1.1` | Routing 4-fold (funcional/procesal/contextual/stack) explicit · scope dimension obligatoria en pattern |
| `POL_FB_KR_PRIVACY_TIERS_v1.1` | TIER 4 con scope unit_of_work_id (no solo tenant_id) · promotion respeta scope |
| `ENT_FB_USER_LEARNING_MODEL_v1` | Patterns capa 1 con scope dimensions · AM ve solo sus units of work |
| `ENT_FB_COMMITTEE_OPERATING_MODEL_v1` | Comite ve solo patterns funcionales (no procesales) |
| `SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1` | Generalizar a `SCH_FB_WORK_PRODUCT_EVIDENCE_BUNDLE` con unit_of_work_id |
| `SPEC_FB_INTEGRATION_LAYER_v1` | Headers x-* extender con `x-unit-of-work-id` · `x-client-id` |
| `SPEC_FB_EVENTING_AND_OUTBOX_v1` | Eventos con scope dimensions completos |

## 8. Cuando implementar (trigger)

NO implementar hasta que:
1. **Primer vertical regulado activo** (legal · software · etc piloto firmado)
2. **Tenant con multi-cliente real** (>3 clientes simultaneos en un mismo tenant)
3. **Permisos heterogeneos detectados** (sub-agente con clearance distinto del archetype)

Hasta entonces · MWT cotizacion v1 con `quote_id` como unit_of_work suficiente · NO se requiere taxonomia.

## 9. Reglas inquebrantables (cuando se implemente)

1. **Cada vertical declara su `canonical` unit_of_work** · NO multiples nombres genericos
2. **Scope dimensions obligatorias** · permission check sin scope completo = bug critico
3. **Knowledge procesal-cliente NUNCA sale del scope** · sin excepcion · sin override
4. **Sub-units heredan permisos del parent unit_of_work** salvo override explicit
5. **`unit_of_work` debe estar en TODA query DB con tenant_id** (RLS extendido)
6. **Migration cuando se implementa** debe ser per-vertical · NO big-bang
7. **NO permitir `unit_of_work_id = null`** en operaciones que producen knowledge candidate

## 10. Pendientes (cuando se implemente · NO ahora)

- Migration tooling per vertical · cargar unit_of_work_id en knowledge existente
- UI per unit_of_work (matter view · project view · etc)
- Cross-unit_of_work search controlado
- Bulk operations respetando scope dimensions
- Audit trail enriquecido con scope dimensions

## NO IMPLICA (R4 bonus 5%/50%)

`ENT_FB_UNIT_OF_WORK_TAXONOMY_v1` **NO implica implementacion en Sprint 1 MWT**. MWT cotizacion v1 funciona con `quote_id` simple. La taxonomia se IMPLEMENTA cuando aparezca primer vertical regulado activo (legal · software · etc) que tenga multi-cliente per-tenant · NO antes.

Esta pieza queda **NOMBRADA** para que cuando se implemente · no se invente al apuro.

## Changelog
- 2026-05-02 v1.0 DRAFT: Creacion inicial post R7. Punto ciego mas peligroso identificado por ChatGPT. Taxonomia canonica per 8 verticales (safety_footwear MWT · legal_practice · software_factory · medical_regulated · financial_advisory · compliance_audit · industrial_HSE · insurance). 7 dimensiones canonicas de access_scope. Knowledge routing 4-fold (funcional/procesal/contextual/stack). 7 reglas de routing canonicas. Implicaciones documentadas para 8 piezas canonizadas (RBAC · KR · Privacy · User Learning · Committee · Evidence Bundle · Integration Layer · Eventing). Status DRAFT · NO implementacion · trigger 3 condiciones (vertical regulado activo · multi-cliente real · permisos heterogeneos).

## Stamp
DRAFT 2026-05-02 — Punto ciego MAS peligroso identificado · nombrado · NO implementado. Sprint 1 MWT intacto. Cuando primer vertical regulado se active · esta pieza se vuelve VIGENTE con migration per-vertical.
