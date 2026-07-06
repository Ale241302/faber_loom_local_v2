---
id: ENT_FB_SKILL_CATALOG_v1
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: ENT
stamp: DRAFT - 2026-07-06 - catalogo maestro de skills a dotar - NO implementacion
fecha: 2026-07-06
agente: Claude (Cowork)
aplica_a: [FaberLoom]
fuentes:
  - SWARM_SKILLS_GAPS_20260706 (A1-A5 + agregador B, corrida Kimi 2026-07-06)
  - Catalogo skills Claude/Anthropic (~130 skills, referencia de estructura)
  - ENT_FB_UNIT_OF_WORK_TAXONOMY_v1, ENT_FB_USE_CASE_CATALOG_v1, ENT_FB_WORK_TYPE_PACK_v1
relacionado_con:
  - ENT_FB_SUB_AGENTS_LIBRARY_v1 (composicion atomica)
  - SCH_FB_SKILL_MANIFEST_v2 (template de spec por skill)
  - ENT_FB_TOOL_CATALOG_v1 (conectores)
changelog:
  - v1.0 (2026-07-06) creacion. Integra gaps capas 0-4 + swarm + templates Claude.
---

# ENT_FB_SKILL_CATALOG_v1
## Catalogo maestro de skills a dotar a FaberLoom

## 0. Principios (no negociables al leer este catalogo)

1. FaberLoom asiste miles de puestos en operaciones distintas. NO es un cotizador; quoting es
   UN pack entre muchos (wtp_b2b_quoting ya existe y no se re-cataloga aqui).
2. Un skill = composicion de primitivos + vocabulario de area + conectores. No se escriben
   miles de skills; se instancia la gramatica por pack.
3. Dato exacto (tasa, partida, estado de comprobante, saldo) = lookup a fuente con cita y
   fecha. NUNCA memoria del modelo.
4. Toda accion con efecto externo = HITL. La autonomia se gana por track record (ceilings).
5. Estados de este catalogo: EXISTE (en KB), TEMPLATE (estructura robable de skill Claude),
   GAP (desde cero). Prioridad hereda score del swarm (columna P, 1=max).

## 1. Gramatica: primitivos

P01 clasificar | P02 extraer | P03 calcular | P04 conciliar | P05 redactar_calibrado |
P06 resumir | P07 priorizar | P08 proyectar | P09 alertar_recurrente | P10 capturar_acuerdo |
P11 publicar_a_kb | P12 auditar_contra_estandar | P13 rutear | P14 escalar

Nuevos por stress test A1 (proponer a ENT_FB_UNIT_OF_WORK_TAXONOMY v2):

- P15 verificar_vigencia_normativa: confirmar que norma/arancel/requisito citado sigue vigente,
  detectar modificaciones (base de REG_WATCH y de todo lookup regulatorio).
- P16 rastrear_externo: consulta en tiempo real a sistema de tercero no controlado (portal
  tributario, tracking transportista, TICA) con captura de evidencia (URL+fecha+screenshot).
- P17 corregir_en_cascada_temporal: recalculo retroactivo con dependencias encadenadas
  (planilla rectificada, notas de credito, intereses acumulados).
- P18 capturar_interaccion_informal: WhatsApp/verbal/no estructurado -> compromiso trazable.
  Redefine P10: el acuerdo pyme LATAM no nace firmado; nace en chat.

Descartados de A1 (fuera de scope agente software): calibrar_instrumento,
reconfigurar_espacio_fisico, ejecutar_transaccion_presencial, reconfigurar_ruta_dinamica.
Resueltos via P14+HITL (juicio humano protegido, no primitivo): evaluar_razonabilidad,
decidir_disposicion_no_conforme, evaluar_severidad_clinica, gestionar_interaccion_emocional.

## 2. Prerequisitos capa 0 (sin esto los skills son wrappers)

| # | Pieza | Estado |
|---|---|---|
| C0-1 | Captura de acuerdo/interaccion informal -> conocimiento firmado citable (P18) | GAP |
| C0-2 | Recopilacion viva P16: navegacion web automatizada + evidence bundle (fuentes A3 son web/manual, SIN API documentada) | GAP |
| C0-3 | Memoria por cliente/tenant heredable por workspace | parcial (M17, Atlas) |
| C0-4 | Loop aprendizaje: gold samples firmados mejoran skill | parcial (Knowledge River) |
| C0-5 | Ceilings de autonomia por track record | disenado, falta mecanica |
| C0-6 | Orquestacion con estado entre skills (flujos multi-paso persistentes) | parcial (Routines) |
| C0-7 | Evidence bundle generalizado a todo output | parcial (quote bundle) |
| C0-8 | Voz por tenant/cliente | specced (VOICE_HUMANIZER v2) |

## 3. Catalogo por pack (orden = prioridad swarm)

### PACK 1 - wtp_fiscalidad_electronica (P=1, score 125, triple senal, cero competencia)

| Skill | Primitivos | Trigger | Fuente template | Estado |
|---|---|---|---|---|
| SKILL_FE_STATUS_CHECK | P16,P04,P09 | diario / al emitir | ninguna | GAP |
| SKILL_FE_REJECT_FIX | P02,P05,P12 | comprobante rechazado | ninguna | GAP |
| SKILL_FE_RECEPTOR_RECONCILE | P04,P09,P10 | semanal (plazo 8 dias CR) | ninguna | GAP |
| SKILL_FE_CABYS_VALIDATE | P12,P16 | al emitir | ninguna | GAP |
| SKILL_FE_COMPLEMENTO_PAGO | P03,P04,P05 | pago parcial (MX CFDI) | ninguna | GAP |
| SKILL_FE_NOTA_CD_LINK | P03,P05,P12 | devolucion/descuento/correccion | ninguna | GAP |
| SKILL_FE_RESEND | P02,P05,P16 | reclamo receptor | ticket-deflector (parcial) | GAP |
| SKILL_FE_RETENCION_MATCH | P04,P12,P09 | semanal pre-declaracion | ninguna | GAP |

Base capa 2 requerida: esquemas XML v4.4 CR / CFDI 4.0 MX / UBL DIAN CO, catalogo CABYS,
APIs oficiales de validacion [PENDIENTE-VERIFICAR existencia y acceso: Hacienda ATV, SAT, DIAN].

### PACK 2 - wtp_comex (P=2, score 100, moat sin fuente)

| Skill | Primitivos | Trigger | Fuente template | Estado |
|---|---|---|---|---|
| SKILL_CX_DOC_COMPLETENESS | P12,P07,P09 | embarque pre-arribo | ninguna | GAP |
| SKILL_CX_PEDIMENTO_CROSSCHECK | P04,P12 | pre-presentacion aduana | ninguna | GAP |
| SKILL_CX_LANDED_COST | P03,P04 | factura importacion + gastos | ninguna | GAP |
| SKILL_CX_HS_CLASSIFY | P01,P16,P15 | producto nuevo | ninguna | GAP |
| SKILL_CX_DUTY_CALC | P03,P16 | pre-cotizacion importacion | ninguna | GAP |
| SKILL_CX_ORIGIN_CHECK | P12,P15 | uso de preferencia tratado | ninguna | GAP |
| SKILL_CX_REQUISITOS_PREVIOS | P16,P09 | producto/destino nuevo | ninguna | GAP |
| SKILL_CX_REG_WATCH | P15,P09 | recurrente (gacetas/DOF/DOU) | ninguna | GAP |
| SKILL_CX_DISPUTE_PACK | P02,P06,C0-7 | disputa/reclasificacion | ninguna | GAP |
| SKILL_CX_EMBARQUE_TRACK | P16,P08,P09 | embarque en transito | ninguna | GAP |

Fuentes vivas mapeadas por A3 (todas web/manual): TICA, SIECA/AIC, SIICEX/TIGIE, MUISCA,
VUCE CR/MX/CO, gacetas oficiales. Corredores v1: BR->CR (sin tratado, DAI pleno), BR->MX
(ACE 53), BR->CO (ACE 72), CR->CA (SAC/RCO), USMCA en segunda ola.

### PACK 3 - wtp_cobranza (P=3, score 80-100)

| Skill | Primitivos | Trigger | Fuente template | Estado |
|---|---|---|---|---|
| SKILL_CO_DUNNING_FE | P05,P07,P16 | factura vencida (incluye clave numerica + estado tributario + link pago) | invoice-chase | TEMPLATE |
| SKILL_CO_CASH_PROJECTION | P08,P03 | semanal / pre-planilla | cash-flow-snapshot | TEMPLATE |
| SKILL_CO_PAYMENT_MATCH_FE | P04,P09,P12 | extracto bancario | reconciliation | TEMPLATE |
| SKILL_CO_SECUENCIA | P09,P13,P14 | dunning escalonado | email-sequence (mecanica) | TEMPLATE |
| SKILL_CO_CARTERA_X_FE | P06,P08,P09 | semanal gerencia (cartera x estado FE) | ninguna | GAP |
| SKILL_CO_PROMESA_PAGO | P18,P10,P09 | acuerdo de pago via WhatsApp/llamada | ninguna | GAP (requiere C0-1) |

### PACK 4 - wtp_planilla (P=4, score 100)

| Skill | Primitivos | Trigger | Fuente template | Estado |
|---|---|---|---|---|
| SKILL_PL_PREP | P03,P12,P13 | quincenal/mensual (CCSS/SICERE/IMSS + archivo banco local) | ninguna | GAP |
| SKILL_PL_RECTIFICACION | P17,P03 | error retroactivo | ninguna | GAP |
| SKILL_PL_CARGAS_VALIDATE | P12,P15 | cambio de tasas/normativa | ninguna | GAP |

### PACK 5 - wtp_tributario (P=5, score 80)

| Skill | Primitivos | Trigger | Fuente template | Estado |
|---|---|---|---|---|
| SKILL_TR_DECLARACION_INFO | P01,P02,P03 | periodo (DIOT, exogena, D-151) | tax-prep (estructura) | TEMPLATE |
| SKILL_TR_RETENCION_CERT | P03,P05,P12 | pago a proveedor | ninguna | GAP |
| SKILL_TR_TRAMITE_TRACK | P16,P09,P13 | tramite ATV/SAT/DIAN abierto | ninguna | GAP |
| SKILL_TR_PERMISOS_CAL | P09,P07,P15 | vencimiento permiso/patente/licencia | vendor-check (mecanica) | TEMPLATE |
| SKILL_TR_TIPO_CAMBIO_ADJ | P03,P04,P16 | factura moneda extranjera | ninguna | GAP |

### PACK 6 - wtp_whatsapp_formal (P=6, score 75, depende de C0-1/P18)

| Skill | Primitivos | Trigger | Fuente template | Estado |
|---|---|---|---|---|
| SKILL_WA_CLASSIFY_ROUTE | P01,P02,P13 | mensaje entrante | ticket-triage | TEMPLATE |
| SKILL_WA_ORDER_CAPTURE | P02,P18,P13 | pedido en chat -> registro formal p/FE | ninguna | GAP |
| SKILL_WA_AGREEMENT_CAPTURE | P18,P10 | acuerdo verbal/chat -> compromiso trazable | call-summary (parcial) | GAP |

### PACK 7 - wtp_bodega_importacion (P=7, score 48)

| Skill | Primitivos | Trigger | Fuente template | Estado |
|---|---|---|---|---|
| SKILL_BO_RECEPCION_MATCH | P02,P04,P09 | recepcion vs packing list/factura (idioma/moneda) | ninguna | GAP |
| SKILL_BO_DEVOLUCION_NC | P02,P12,P05 | devolucion fisica -> nota credito + inventario | ninguna | GAP |
| SKILL_BO_STOCK_DISPONIBLE | P02,P07,P16 | consulta pre-venta (incluye transito) | ninguna | GAP |

### PACK 8 - wtp_comercial (templates Claude, localizar)

| Skill | Fuente template | Estado |
|---|---|---|
| SKILL_CM_ACCOUNT_BRIEF | call-prep + business-pulse (degradacion) | TEMPLATE |
| SKILL_CM_CALL_CAPTURE | call-summary | TEMPLATE |
| SKILL_CM_CARTERA_PRIORITIZE | lead-triage invertido a clientes | TEMPLATE |
| SKILL_CM_REORDER_PREDICT | ninguna (ciclo de recompra) | GAP |

### PACK 9 - wtp_servicio

| Skill | Fuente template | Estado |
|---|---|---|
| SKILL_SV_TRIAGE | ticket-triage | TEMPLATE |
| SKILL_SV_RESPUESTA | draft-response + VOICE_HUMANIZER | TEMPLATE |
| SKILL_SV_ESCALACION | customer-escalation | TEMPLATE |
| SKILL_SV_TEMAS | customer-pulse | TEMPLATE |
| SKILL_SV_GARANTIA_DEVOLUCION | handle-complaint + BO_DEVOLUCION_NC | TEMPLATE |

### PACK 10 - wtp_finanzas_cierre (localizar NIIF, no US-GAAP)

| Skill | Fuente template | Estado |
|---|---|---|
| SKILL_FI_CIERRE_NARRADO | month-end-prep / close-month | TEMPLATE |
| SKILL_FI_ASIENTOS | journal-entry | TEMPLATE |
| SKILL_FI_VARIACIONES | variance-analysis | TEMPLATE |
| SKILL_FI_EEFF | financial-statements | TEMPLATE |

### PACK 11 - wtp_legal (localizar derecho civil LATAM)

| Skill | Fuente template | Estado |
|---|---|---|
| SKILL_LG_NDA_TRIAGE | triage-nda | TEMPLATE |
| SKILL_LG_CONTRATO_REVIEW | review-contract / contract-review | TEMPLATE |
| SKILL_LG_VENCIMIENTOS | vendor-check | TEMPLATE |
| SKILL_LG_PREFIRMA | signature-request | TEMPLATE |
| SKILL_LG_VIGENCIA_NORMA | ninguna (P15 puro) | GAP |

### PACK 12 - wtp_gerencia

| Skill | Fuente template | Estado |
|---|---|---|
| SKILL_GE_PULSO | business-pulse | TEMPLATE |
| SKILL_GE_BRIEF_RECURRENTE | monday-brief / friday-brief / month-heads-up | TEMPLATE |
| SKILL_GE_QBR | quarterly-review | TEMPLATE |
| SKILL_GE_RIESGOS | risk-assessment | TEMPLATE |

### PACK 13 - wtp_operaciones / marketing / rrhh (segunda ola)

| Skill | Fuente template | Estado |
|---|---|---|
| SKILL_OP_SOP | runbook / process-doc | TEMPLATE |
| SKILL_OP_STATUS | status-report | TEMPLATE |
| SKILL_OP_PROVEEDOR_EVAL | vendor-review | TEMPLATE |
| SKILL_MK_CAMPANA | campaign-plan | TEMPLATE |
| SKILL_MK_CONTENIDO_VOZ | draft-content + VOICE_HUMANIZER | TEMPLATE |
| SKILL_MK_BRAND_AUDIT | brand-review | TEMPLATE |
| SKILL_HR_CONTRATACION | job-post-builder (localizar Codigo de Trabajo) | TEMPLATE |

## 4. Ya existentes en KB (no se re-catalogan)

SKILL_PROFORMA_BUILDER, SKILL_CLIENT_SERVICE, SKILL_COMPLIANCE_CHECKER, SKILL_HUMANIZE_COMMS,
SKILL_HUMANIZE_BRAND, SKILL_KB_AUDITOR, SKILL_KB_GATEWAY, SKILL_DEMAND_FORECASTER,
SKILL_AMAZON_OPS, SKILL_COPY, SKILL_EXPERIMENT_RUNNER, SKILL_VOICE_HUMANIZER,
SKILL_RW_REVIEW_TRIAGE, SKILL_RW_LISTING_OPT + 10 sub-agentes AG_SUB_* (ENT_FB_SUB_AGENTS_LIBRARY_v1)
+ pack activo wtp_b2b_quoting_safety_footwear.

## 5. Conteo y secuencia

- Total catalogado: 62 skills en 13 packs. GAP desde cero: 33. TEMPLATE (estructura Claude
  robable): 29. Ya existentes: 14 skills + 10 sub-agentes.
- Secuencia: (1) C0-1 y C0-2 de capa 0 (desbloquean todo lo demas segun convergencia B),
  (2) PACK 1 fiscalidad electronica (dogfooding MWT inmediato + score maximo),
  (3) PACK 3 cobranza (skill 2 de E2 ya agendado), (4) PACK 2 comex corredor BR->CR,
  (5) resto por score. Packs 8-13 son mayormente TEMPLATE: volumen mecanico, no diseno.
- Golden cases por pack desde operacion MWT real: facturas propias (PACK 1/3), importaciones
  Marluvas (PACK 2/7), planilla MWT (PACK 4), EEFF Del Risco (PACK 10).

## 6. Pendientes que condicionan el catalogo

- [PENDIENTE-VERIFICAR] APIs oficiales de facturacion electronica (Hacienda ATV CR, SAT MX,
  DIAN CO): existencia confirma viabilidad tecnica del PACK 1 sin scraping.
- [PENDIENTE-VERIFICAR] 15 items regulatorios del swarm (tratados, leyes proteccion datos,
  resoluciones) listados en faberloom_B_convergencia seccion 4.
- Decision CEO: adoptar P15-P18 en ENT_FB_UNIT_OF_WORK_TAXONOMY v2 (contradiccion 1 del
  agregador: la taxonomia v1 NO es exhaustiva).

---

Stamp: DRAFT - 2026-07-06 - generado en Cowork desde SWARM_SKILLS_GAPS_20260706, pendiente indexar
