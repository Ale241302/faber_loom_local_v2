---
id: ENT_FB_VERTICAL_CANDIDATES_v1
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Plataforma
type: entity
stamp: DRAFT 2026-05-02 — catalogo informacional · NO implementacion
fecha: 2026-05-02
agente: Cowork (redaccion) + CEO (decisiones) + ChatGPT (auditoria R6+R7+R8)
aplica_a: [FaberLoom]
status_motivo: |
  Catalogo informacional de verticales candidatos para FaberLoom post-MWT.
  NO compromete v2. NO implementa nada. NO toca Sprint 1 MWT.
  Documenta aprendizaje de auditorias R6 (legal) · R7 (cross-vertical) · R8 (DMS).
relacionado_con:
  - ENT_FB_VERTICAL_SPEC_OBJECT_v1.1 (adapter pattern padre)
  - SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1.1 (MWT como primer adapter safety_footwear)
  - POL_FB_KNOWLEDGE_VALIDITY_AND_EXPIRY_v1 (transversal aplicable a todos)
  - ENT_FB_UNIT_OF_WORK_TAXONOMY_v1 (DRAFT · punto ciego mas peligroso R7)
  - SPEC_FB_DMS_INTEGRATION_v1 (DRAFT · adapter pattern DMS R8)
---

# ENT_FB_VERTICAL_CANDIDATES_v1
## Catalogo de verticales candidatos para FaberLoom post-MWT

## 1. Proposito

Documenta verticales candidatos identificados durante auditorias R6 (caso bufete) + R7 (cross-vertical) + R8 (DMS integration). 

**Status: DRAFT · NO implementacion · NO compromiso v2 · NO toca Sprint 1 MWT.**

Sirve como:
- Captura de aprendizaje (no perder insights de 3 auditorias)
- Roadmap product informacional
- Stress test conceptual del modelo (validar que adapter pattern funciona)
- Lista de gaps especificos per vertical (cuando aplique implementar)

> **Frase canonica R7:** El modelo transversal NO se rompe por nuevos verticales · se rompe si todos los verticales fingen tener la misma unidad de trabajo, el mismo daño, la misma vigencia y los mismos permisos.

## 2. Estado actual · prioridades

| Vertical | Estado | Prioridad post-MWT | Auditoria origen |
|---|---|---|---|
| **safety_footwear** (MWT) | ✓ VIGENTE Sprint 1 | (ya activo) | R3 |
| **legal_practice** | candidato fuerte v2 | ALTA · post-MWT | R6 |
| **software_factory** | candidato fuerte v2 | ALTA · post-MWT | R7 |
| **insurance** | candidato | MEDIA | R7 |
| **medical_regulated** | candidato | MEDIA-BAJA | R7 (carga regulatoria brutal) |
| **financial_advisory** | candidato | MEDIA | R7 |
| **compliance_audit** | candidato | MEDIA | R7 |
| **industrial_HSE** (mas alla calzado) | candidato | BAJA | R7 |
| **pharma_lifesciences** | observacion | DIFERIDA | R7 |
| **government_procurement** | observacion | DIFERIDA | R7 |
| **education** | observacion | DIFERIDA · low priority | R7 |
| **energy_utilities** | observacion | DIFERIDA | R7 |

## 3. Verticales · ficha por candidato

### 3.1 legal_practice (R6)

```yaml
vertical_id: legal_practice
parent_industry: professional_services_regulated
status: candidate_strong_v2

unidad_de_trabajo: matter / expediente / caso
multi_cliente_per_tenant: SI · privilegio cliente-abogado obligatorio
sub_agentes_tipicos: laboral · penal · cobro · contratos · compliance

NEVER_actions_canonicas: 10
  - dar opinion legal final al cliente
  - presentar demanda/escrito
  - firmar documento juridico
  - recomendar aceptar/rechazar acuerdo
  - calcular contingencia como certeza
  - definir estrategia procesal final
  - enviar comunicacion a contraparte
  - cerrar expediente
  - cambiar clasificacion privilegio
  - promover knowledge legal a template comun

DMS_tipicos:
  - NetDocuments (legal-specific · enterprise)
  - iManage (legal/financial enterprise)
  - Worldox (legal mid-market)
  - DocuWare
  - SharePoint

vigencia_critica:
  - jurisprudencia · reforma · criterio · plazo procesal

privilegio_obligatorio: TIER 4 LEGAL_PRIVILEGED
  - cliente-abogado privilegio
  - anonimizacion fuerte para cross-cliente
  - conflict-check obligatorio antes de activar Agente Cliente

clearance_subagentes:
  - bar admission per pais
  - especialidad penal/laboral/etc
  - matter-team membership

wedge_MVP_recomendado:
  "Legal Labor Desk · Laboral Patronal MX"
  - 1 bufete · 1 socio senior · 1 pais · 1 materia · 1 workflow
  - intake → checklist → memo INTERNO de riesgo
  - NO envio externo · NO consejo final · NO cliente integral

pricing_estimado:
  setup_piloto: USD 2500-7500
  usuario_mes: USD 150-300
  minimo: 3 usuarios o USD 750/mes
  duracion_piloto: 8-12 semanas

gaps_P0_pre_piloto:
  - POL_FB_LEGAL_PRIVILEGE_v1
  - ENT_FB_LEGAL_REGULATORY_METADATA_v1
  - SPEC_FB_LEGAL_SUBAGENT_CREDENTIALS_v1
  - extension Authority Matrix legal NEVER-actions
  - conflict-check obligatorio
  - matter lifecycle states
  - malpractice audit bundle

competencia_directa: Harvey AI · CoCounsel · etc
diferenciador_FaberLoom: knowledge organizacional gobernado con templates · permisos por matter · privilege-aware
```

### 3.2 software_factory (R7)

```yaml
vertical_id: software_factory
parent_industry: professional_services_technical
regulation_profile: compliance_heavy_not_statutory
status: candidate_strong_v2

unidad_de_trabajo: project / repo / sprint / PR / deployment / incident
multi_cliente_per_tenant: SI · 5-20 clientes simultaneos comun
sub_agentes_tipicos:
  - architecture
  - security
  - QA / testing
  - DevOps / infra
  - code review
  - documentation
  - migration

NEVER_actions_tecnicas: 9
  - merge main
  - deploy production
  - delete database
  - rotate secrets
  - change IAM
  - disable monitoring
  - modify billing
  - expose logs
  - alter audit trail

DMS_tipicos:
  - GitHub / GitLab / Bitbucket (repos · NO DMS clasico)
  - Confluence / Notion (docs)
  - Jira / Linear (issues)

vigencia_microscopica:
  - framework versions (Next 14 → 15 → 16)
  - CVE / vulnerabilities
  - APIs deprecated
  - dependencies (npm · pip · etc)
  - cloud provider features

knowledge_4_fold:
  funcional_heredable: "patterns · best practices · anti-patterns"
  cliente_proyecto: "su codebase · NO heredable"
  tech_stack: "versions · frameworks · depende"
  organizacional: "conventions del software house"

clearance_subagentes:
  - tech expertise (security lead · DevOps · maintainer)
  - release manager
  - production access (bastion · prod credentials)

privilege_critico: NDA cliente + IP code
ip_contamination_risk: CRITICO
  - patterns funcionales heredables
  - codigo cliente NUNCA cross-cliente
  - patrones de bug detectados pueden compartirse anonimizados

wedge_MVP_recomendado:
  "Code Review Desk · 1 software house · 1 stack canonico"
  - 1 stack (Next.js + TypeScript + Postgres por ejemplo)
  - PR review automatizado (NO merge auto)
  - Best practices scan
  - CVE detection en dependencies
  - Documentacion auto-suggest

pricing_estimado:
  setup_piloto: USD 1500-5000
  usuario_mes: USD 99-199
  minimo: 5 desarrolladores

competencia_directa: GitHub Copilot · Codeium · Cursor · etc
diferenciador_FaberLoom: knowledge organizacional + governance + IP isolation per cliente
  (NO es codigo-completion · es PR review + docs + governance)
```

### 3.3 insurance (R7)

```yaml
vertical_id: insurance
parent_industry: financial_services_regulated
status: candidate_medium_v2

complexity: alto · mezcla medico + financiero + legal + fraude + claims

unidad_de_trabajo: claim / policy / underwriting_case
multi_cliente_per_tenant: SI · poliza-holders + claimants

NEVER_actions:
  - aprobar/rechazar claim final
  - emitir poliza
  - calcular prima final
  - recomendar settlement
  - cancelar poliza

vigencia_critica:
  - regulaciones aseguradoras
  - tablas actuariales
  - contratos reaseguro

gaps_P0: similar a financial_advisory + medical_regulated
```

### 3.4 medical_regulated (R7)

```yaml
vertical_id: medical_regulated
parent_industry: healthcare_regulated
status: candidate_medium_low_v2 (carga regulatoria brutal)

unidad_de_trabajo: encounter / episode / patient_case
multi_cliente_per_tenant: SI · trilateral (paciente · proveedor · pagador)

NEVER_actions:
  - diagnostico
  - prescripcion
  - alta medica
  - cirugia recommendation
  - drug interaction final decision

vigencia_critica:
  - guidelines clinicas (per pais)
  - drug recalls (criticos · stale_action: block inmediato)
  - contraindications

DMS_tipicos:
  - Epic · Cerner · Allscripts (EHR · NO DMS clasico)
  - OnBase
  - PACS para imagenes

privilege_obligatorio: PHI + LFPDPPP-salud + LGPD-saude
  - HIPAA aplica si transfronterizo
  - registro sanitario per pais

clearance_subagentes:
  - medical license per pais
  - especialidad (cardiologia · oncologia · pediatria)
  - hospital privileges

wedge_MVP_NO_recomendado_v2:
  "Vertical mas pesado regulatoriamente · diferir hasta tener legal o software validados"
  ChatGPT R7: "viene con elefante y estetoscopio"
```

### 3.5 financial_advisory (R7)

```yaml
vertical_id: financial_advisory
parent_industry: financial_services_regulated
status: candidate_medium_v2

unidad_de_trabajo: account / transaction / portfolio / recommendation
multi_cliente_per_tenant: SI · multilateral (cliente · banco · regulador)

NEVER_actions:
  - ejecutar trade
  - recomendacion personalizada final
  - KYC final approval
  - aprobacion credito final
  - reporting regulatorio final

vigencia_critica:
  - regulaciones (CNBV MX · SFC CO · BCB BR)
  - tasas
  - KYC profiles
  - risk scoring models

DMS_tipicos:
  - OpenText
  - SharePoint
  - OnBase

clearance_subagentes:
  - CFP / CFA / Series 7
  - compliance officer
  - trader autorizado

outcome_atribucion: medible_parcialmente_atribuible_con_reservas
  (mercado · perfil cliente · no solo agente)

NO_outcome_based_pricing: regla dura
```

### 3.6 compliance_audit (R7)

```yaml
vertical_id: compliance_audit
parent_industry: governance_risk_compliance
status: candidate_medium_v2

unidad_de_trabajo: audit_cycle / control_test / finding
multi_stakeholder: multi (auditor · auditado · regulador)

NEVER_actions:
  - emitir finding final
  - cerrar control
  - certificar cumplimiento
  - aprobar remediation

vigencia_critica:
  - normas (ISO · SOC · NIST · etc)
  - CVEs (criticos · freshness <24h · stale_action: block)
  - audit cycles

DMS_tipicos:
  - ServiceNow GRC
  - Archer
  - LogicGate
  - SharePoint

clearance_subagentes:
  - CIA / CISA / CISM
  - lead auditor ISO
```

### 3.7 industrial_HSE (mas alla calzado · R7)

```yaml
vertical_id: industrial_HSE
parent_industry: industrial_supply_regulated
status: candidate_low_v2 (MWT calzado seguridad ya cubre subset)

unidad_de_trabajo: work_order / incident / batch / RFQ / production_run

stakeholders: multilateral (operador · supervisor · cliente · regulador · proveedor · aseguradora)

NEVER_actions:
  - safety override
  - liberar lote peligroso
  - incident response final decision
  - environmental permit override

vigencia_critica:
  - normas tecnicas (ASTM · NIOSH · IEC)
  - certificados (per cert validity period)
  - lotes (vencimiento · recall)
  - permisos ambientales

DMS_tipicos:
  - SAP DMS
  - SharePoint
  - OnBase
  - Alfresco
```

## 4. Verticales en observacion (DIFERIDOS · low priority post-MWT)

### 4.1 pharma_lifesciences

```
Mas regulado que medical hospitalario.
Trazabilidad lotes · promocion · farmacovigilancia · clinical trials.
DIFERIR · alta carga regulatoria · alto valor pero alta complejidad.
```

### 4.2 government_procurement

```
Alta auditabilidad · conflicto interes · transparencia · licitaciones.
Buen fit conceptual con FaberLoom (governance + audit).
DIFERIR · ciclos de venta gobierno son largos.
```

### 4.3 education

```
Menores · datos sensibles · evaluaciones · compliance.
Menor prioridad comercial (margenes bajos · presupuestos publicos).
DIFERIR · no descartar.
```

### 4.4 energy_utilities

```
Safety · regulacion · infraestructura critica.
Carga regulatoria pesada similar a medical.
DIFERIR · industry-specific · no general.
```

## 5. Capa transversal regulada · 6 piezas pendientes

ChatGPT R7 identifico que NO basta vertical_spec_object actual para regulados profesionales. Faltan piezas TRANSVERSALES (aplican a >=3 verticales):

| Pieza | Status | Razon canonizar / diferir |
|---|---|---|
| `POL_FB_KNOWLEDGE_VALIDITY_AND_EXPIRY_v1` | **VIGENTE** (canonizada hoy) | Aplica MWT tambien · transversal · bajo riesgo |
| `ENT_FB_UNIT_OF_WORK_TAXONOMY_v1` | **DRAFT** (canonizada hoy) | Punto ciego mas peligroso · debe quedar nombrado |
| `SPEC_FB_DMS_INTEGRATION_v1` | **DRAFT** (canonizada hoy) | Adapter pattern · NO implementacion sin tenant |
| `ENT_FB_REGULATED_KNOWLEDGE_METADATA_v1` | DIFERIR | Hasta segundo vertical activo |
| `SPEC_FB_SUBAGENT_CREDENTIALS_v1` | DIFERIR | Hasta primer piloto regulado |
| `POL_FB_NEVER_ACTIONS_v1` | DIFERIR | Registry plug-in per vertical · necesita verticales activos |
| `ENT_FB_HARM_PREVENTION_TAXONOMY_v1` | DIFERIR | Severity ponderada cross-vertical · necesita verticales activos |
| `ENT_FB_RESPONSIBLE_HUMAN_OF_RECORD_v1` | DIFERIR | Necesita verticales regulados activos |
| `SCH_FB_WORK_PRODUCT_EVIDENCE_BUNDLE_v1` | DIFERIR | Generalizacion del Quote Evidence Bundle · cuando segundo vertical |

## 6. Reglas inquebrantables del catalogo

1. **Este catalogo es INFORMACIONAL · NO compromiso v2.** Que un vertical aparezca aqui NO significa que se va a construir.
2. **Sprint 1 MWT es sagrado** · ningun vertical aqui canonizado interfiere con MWT.
3. **Implementacion per vertical SOLO cuando piloto firmado** · 5 condiciones-trigger (R8).
4. **Software factories es adapter PROPIO · NO meta-vertical generic** (R7 critical).
5. **Medical regulated diferido low priority v2** · alta carga regulatoria · NO entrar pronto.
6. **Insurance + Software factories priorizables sobre medical** despues de legal (R7).
7. **Cualquier piloto regulado requiere canonizar piezas P0** del vertical antes de aceptar.

## 7. Pendientes [PENDIENTE — NO INVENTAR]

- Validacion de pricing per vertical · solo confirmable con conversaciones reales con potenciales tenants
- Conversaciones exploratorias (R6 recomendo 3 bufetes para legal · similar para otros)
- Trademark + DPA legal templates per pais LATAM
- DMS adapter implementations · diferidas hasta tenant lo exija (R8)

## NO IMPLICA (R4 bonus 5%/50%)

`ENT_FB_VERTICAL_CANDIDATES_v1` **NO implica roadmap commit v2**. Es catalogo de aprendizaje · stress test conceptual del modelo · referencia futura. CEO + equipo deciden cuando + cual implementar segun:
- demanda real (piloto firmado)
- recursos disponibles
- validacion MWT exitosa
- gaps P0 cerrados pre-piloto

NO es promesa al mercado · NO es sales material · NO bloquea Sprint 1.

## Changelog
- 2026-05-02 v1.0 DRAFT: Creacion inicial post auditorias R6+R7+R8. Catalogo informacional de 12 verticales (8 candidatos + 4 observacion). Fichas detalladas para legal_practice (R6) · software_factory (R7) · medical_regulated (R7) · financial_advisory (R7) · compliance_audit (R7) · industrial_HSE (R7) · insurance (R7). Verticales en observacion: pharma · government · education · energy. Capa transversal regulada con 9 piezas pendientes (3 canonizadas hoy · 6 diferidas hasta segundo vertical activo). 7 reglas inquebrantables. Status DRAFT · NO implementacion · NO compromiso v2.

## Stamp
DRAFT 2026-05-02 — Catalogo de aprendizaje de 3 auditorias externas (R6+R7+R8). Captura insights antes de perderlos. Stress test conceptual confirma que modelo arquitectonico aguanta cross-vertical regulado · pero requiere capa transversal nueva para escalar sin parches. Sprint 1 MWT intacto.
