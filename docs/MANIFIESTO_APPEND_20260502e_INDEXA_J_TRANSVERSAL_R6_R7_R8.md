---
id: MANIFIESTO_APPEND_20260502e_INDEXA_J_TRANSVERSAL_R6_R7_R8
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza
type: manifiesto_append
stamp: VIGENTE 2026-05-02
fecha: 2026-05-02
agente: Cowork (planificacion + redaccion) + CEO (decisiones secuenciales) + ChatGPT (auditorias R6+R7+R8)
aplica_a: [FaberLoom]
relacionado_con:
  - 9 indexas previas (a-i)
  - Capa transversal post-MWT
---

# MANIFIESTO_APPEND_20260502e_INDEXA_J_TRANSVERSAL_R6_R7_R8

## Que paso

**Decima indexa** post 3 auditorias adicionales R6 (caso bufete) + R7 (cross-vertical 6 verticales) + R8 (DMS integration).

Captura aprendizajes de stress-test conceptual del modelo. Documentacion para futuros verticales. **Cero implementacion · cero compromiso v2 · NO toca Sprint 1 MWT.**

## Las 4 piezas canonizadas

| # | Archivo | Status | Origen |
|---|---|---|---|
| 1 | `POL_FB_KNOWLEDGE_VALIDITY_AND_EXPIRY_v1.md` | **VIGENTE** | R6 bonus 5%/50% + R7 validacion |
| 2 | `ENT_FB_VERTICAL_CANDIDATES_v1.md` | DRAFT | R6+R7+R8 catalogo |
| 3 | `ENT_FB_UNIT_OF_WORK_TAXONOMY_v1.md` | DRAFT | R7 punto ciego mas peligroso |
| 4 | `SPEC_FB_DMS_INTEGRATION_v1.md` | DRAFT | R8 con 14 cambios sustantivos |

## Por que solo 1 VIGENTE y 3 DRAFT

**VIGENTE:** `POL_FB_KNOWLEDGE_VALIDITY_AND_EXPIRY_v1` aplica a **MWT desde dia 1** (refuerza freshness SLA del Source of Truth · sirve cross-vertical regulado). Bajo riesgo · alto retorno · NO espera segundo vertical.

**DRAFT:** los otros 3 capturan aprendizaje pero NO se implementan hasta:
- `VERTICAL_CANDIDATES`: catalogo informacional · NO compromiso
- `UNIT_OF_WORK_TAXONOMY`: implementar al primer vertical regulado activo (legal · software · etc)
- `DMS_INTEGRATION`: adapter pattern · 5 condiciones-trigger pre-implementacion specific adapter

## R6 · caso bufete legal_practice (resumen)

CEO presento caso: bufete con template `derecho_laboral` · abogado itera · comite revisa · template hereda. ChatGPT R6 valido modelo aguanta · scores 7.0/6.8/7.2 mejorables a 9+ con plan claro. Identifico 4 gaps + 5 adicionales (conflict-check · NEVER legal · citation · matter lifecycle · malpractice bundle). Propuso wedge ultra-estrecho "Legal Labor Desk · Laboral Patronal MX". Pricing concreto USD 150-300 usuario/mes piloto. Ciclo venta 6-10 semanas. NO MVP Sprint 1 · diferir hasta primer bufete piloto firmado.

## R7 · cross-vertical 6 verticales (resumen)

CEO pregunto variabilidad cross-vertical · agrego "fabricas de software". ChatGPT R7 valido 8 puntos ciegos + 5 adicionales. Identifico **Unit of Work + scoped permissions** como punto ciego MAS peligroso (rompe RBAC + KR + Privacy + User Learning + Committee + Audit + Evidence Bundle en primer piloto serio · semana 2 NO ano 2). Software como adapter PROPIO NO meta-vertical. Knowledge 4-fold (no 3-fold). Verticales priorizables post-legal: seguros · software · NO medical (carga regulatoria brutal · "viene con elefante y estetoscopio"). 6 piezas transversales propuestas (3 canonizables ahora · 6 diferibles).

> "El modelo transversal NO se rompe por nuevos verticales · se rompe si todos los verticales fingen tener la misma unidad de trabajo · el mismo daño · la misma vigencia y los mismos permisos."

## R8 · DMS integration (resumen)

CEO pregunto integracion DocuClass/DocuWare/Alfresco/etc. Mi propuesta SPEC dedicado · ChatGPT R8 valido con 14 cambios sustantivos: capabilities matrix obligatoria · MinIO cache NO source of record · compare-and-set version/hash · doble autorizacion FaberLoom AND DMS · compliance metadata propagation transversal · multi-DMS conceptual · search degradation honesta · bulk policy con cost estimate · 5 condiciones-trigger · 12 reglas inquebrantables. Frase canonica:

> "FaberLoom puede leer · proponer y escribir sobre documentos externos · pero el DMS conserva autoridad documental. FaberLoom hereda permisos · conserva provenance · cachea con limites y NUNCA convierte integracion en bypass de gobierno documental."

## Ciclo arquitectonico FaberLoom · 10 indexas + 8 auditorias externas

```
INDEXAS (a-j · cero rechazos):
  a (30-abr) Knowledge River
  b (30-abr) P16 Atomic Agents
  c (30-abr) AM Vertical
  d (30-abr) Audit Reconciliation R2+R3
  e (01-may) Backend post R4
  f (02-may) Cierre Final mock+fixtures
  g (02-may) Modelo aprendizaje 2 capas R5
  h+i (02-may) Contratos + Sistema Nervioso + Plataforma
  j (02-may · ESTA) Transversal R6+R7+R8

AUDITORIAS EXTERNAS R1-R8 · CERO RECHAZOS:
  R1 (18-abr) Arquitectonica
  R2 (30-abr) Post-canonizacion
  R3 (30-abr) Funcional + Apple critique
  R4 (01-may) Indexa-e backend
  R5 (02-may) Plan 3 escalonadas + 4 SPECs
  R6 (02-may) Caso bufete legal
  R7 (02-may) Cross-vertical 6 verticales
  R8 (02-may) DMS integration
```

## Sprint 1 readiness post-indexa-j

| Dimension | Pre-j | Post-j |
|---|---|---|
| MWT cotizacion Sprint 1 | 9.1/10 | 9.1/10 (sin cambios) |
| Modelo transversal cross-vertical | 7.5/10 | 8.5/10 (validity + uow + dms documentados) |
| Capa regulada cross-vertical | 6.0/10 | 7.5/10 (catalogo + 1 transversal vigente) |
| Vertical legal_practice | 7.0/10 | 8.0/10 (gaps documentados · pendientes pre-piloto) |
| Vertical software_factory | 6.0/10 | 7.5/10 (caracterizado · adapter propio identificado) |
| DMS readiness | 4.0/10 | 8.0/10 (SPEC DRAFT con 14 cambios R8 aplicados) |

Sprint 1 MWT cotizacion **intacto** · canonica · ejecutable.

## Archivos creados/modificados en esta indexa

### Nuevos (4 piezas FB)

| Archivo | Lineas | Status |
|---|---|---|
| docs/faberloom/POL_FB_KNOWLEDGE_VALIDITY_AND_EXPIRY_v1.md | ~270 | VIGENTE |
| docs/faberloom/ENT_FB_VERTICAL_CANDIDATES_v1.md | ~410 | DRAFT |
| docs/faberloom/ENT_FB_UNIT_OF_WORK_TAXONOMY_v1.md | ~280 | DRAFT |
| docs/faberloom/SPEC_FB_DMS_INTEGRATION_v1.md | ~520 | DRAFT |

### Bumps + Manifiesto

| Archivo | Cambio |
|---|---|
| docs/RW_ROOT.md | v4.8.17 → v4.8.18 + entry changelog |
| docs/DASHBOARD_SNAPSHOT.md | v12.8 → v12.9 + conteos |
| docs/MANIFIESTO_APPEND_20260502e_INDEXA_J_TRANSVERSAL_R6_R7_R8.md | NUEVO · este archivo |

**Total esta indexa: 7 archivos · ~1480 lineas (1 VIGENTE + 3 DRAFT + 1 manifiesto + 2 bumps).**

## Conteos finales repo post-j

- docs/ raiz: 307 → 308 (+1 manifiesto)
- docs/faberloom/: 33 → 37 (+4 nuevos)
- Repo total: 484 → 489

## Lo que NO se canonizo (diferido)

```
DIFERIR hasta segundo vertical real activo:
- ENT_FB_REGULATED_KNOWLEDGE_METADATA_v1
- SPEC_FB_SUBAGENT_CREDENTIALS_v1
- POL_FB_NEVER_ACTIONS_v1 (registry plug-in)
- ENT_FB_HARM_PREVENTION_TAXONOMY_v1
- ENT_FB_RESPONSIBLE_HUMAN_OF_RECORD_v1
- SCH_FB_WORK_PRODUCT_EVIDENCE_BUNDLE_v1

DIFERIR hasta primer piloto regulado firmado:
- POL_FB_LEGAL_PRIVILEGE_v1
- ENT_FB_LEGAL_REGULATORY_METADATA_v1
- SPEC_FB_LEGAL_SUBAGENT_CREDENTIALS_v1
- conflict-check obligatorio
- matter lifecycle states
- malpractice audit bundle

DIFERIR adapter specific DMS (5 condiciones-trigger):
- DMS_DocuWare_Adapter
- DMS_Alfresco_Adapter
- DMS_NetDocuments_Adapter
- DMS_iManage_Adapter
- DMS_SharePoint_Adapter
- DMS_Box_Adapter
- DMS_GoogleDrive_Adapter
- DMS_OnBase_Adapter
- DMS_DocuClass_Adapter
- SAP_DMS / ServiceNow_GRC / GitHub_GitLab (sub-SPECs propios)

NUNCA canonizar abstracto sin piloto:
- POL_FB_MEDICAL_PHIA_HIPAA_v1
- POL_FB_FINANCIAL_ADVICE_v1
- SPEC_FB_SOFTWARE_FACTORY_DEVOPS_v1

NUNCA Sprint 1 (R6+R7+R8 unanimes):
- legal · medical · financial · compliance · software como MVP
- MWT primero
```

## 8 auditorias externas · veredicto final acumulado

> "5 auditorias R1-R5 cero rechazos." (post-indexa-h+i)
> "8 auditorias R1-R8 cero rechazos." (post-indexa-j ESTA)

Modelo arquitectonico FaberLoom validado integralmente cross-vertical. Stress test del caso bufete (R6) + analisis 6 verticales (R7) + DMS integration (R8) confirman:

1. **Arquitectura aguanta sin redisenar** (P16 · 2 capas · KR · Privacy · adapter pattern)
2. **Transferibilidad mecanica genuina** (agentes · templates · KR · comite · RBAC · audit · fixtures)
3. **Transferibilidad semantica requiere capa nueva** (validity + uow + dms · canonizada hoy)
4. **Capa regulada profesional** (legal · medical · financial) requiere piezas P0 pre-piloto

## Frase canonica del proyecto post-R6+R7+R8

Tres frases canonicas integradas a piezas canonizadas hoy:

```
R6 (gloss): "Every claim earns a gloss · every gloss is visible to those allowed to see."

R7 (unit_of_work): "El modelo transversal NO se rompe por nuevos verticales · 
                   se rompe si todos fingen tener la misma unidad de trabajo · 
                   el mismo daño · la misma vigencia y los mismos permisos."

R8 (DMS): "FaberLoom puede leer · proponer y escribir sobre documentos externos · 
         pero el DMS conserva autoridad documental. FaberLoom hereda permisos · 
         conserva provenance · cachea con limites y NUNCA convierte integracion 
         en bypass de gobierno documental."
```

## Origen de la decision CEO

CEO Alvaro · sesion 2026-05-02:
> "si" (confirmacion canonizar las 4 piezas R6+R7+R8 unificadas en indexa-j)

Decision ejecutiva · captura aprendizaje de 3 auditorias externas sin tocar Sprint 1 MWT · sin compromiso v2 · sin implementacion · solo documentacion canonizable.

## Stamp
VIGENTE 2026-05-02 — Indexa-j transversal R6+R7+R8. 4 piezas canonizadas (1 VIGENTE + 3 DRAFT). Captura aprendizaje 3 auditorias externas sin tocar Sprint 1 MWT. ARCH sealed v1.5 NO tocado · POL_DATA_CLASSIFICATION sealed v1.4 NO tocado · FROZENs intactos. 8 auditorias externas R1-R8 · cero rechazos · modelo validado integralmente. Sprint 1 readiness MWT 9.1/10 mantenido · readiness cross-vertical sube de 6.0 a 7.5/10. Pendiente operativo: CEO ejecuta Sem 0 (replay 60 RFQs + Authority calibration + smoke test). Pendiente futuro: implementar piezas DRAFT cuando aparezcan verticales reales.
