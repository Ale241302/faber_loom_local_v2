# ENT_FB_WORK_TYPE_PACK_v1 -- Work-Type Packs Unidad de Expansion FaberLoom
id: ENT_FB_WORK_TYPE_PACK_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: ENT
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: ENT_FB_DECISIONES_E1_v1.md · ENT_FB_VERTICAL_CANDIDATES_v1.md · SPEC_FB_AGENT_BUILDER_v1.md

---

## Declaracion

Un work-type pack es la unidad de expansion del producto.
Todo lo que un tenant necesita para operar un tipo especifico
de trabajo administrativo desde el primer dia.

Frase canonica:
  Externo: resolvemos este trabajo mejor que nadie.
  Interno: todos los trabajos comparten la misma gramatica operacional.

---

## 1. Estructura canonica

id: string
name: string
version: semver
status: draft | active | deprecated

work_description: que hace el usuario hoy sin FaberLoom
unit_of_work: unidad atomica (RFQ / cobro / memo / listing)
user_persona: quien lo usa
value_proposition: que resuelve FaberLoom para esta persona

case_schema:
  fields: campos de cada caso
  evidence_fields: campos del evidence bundle
  exception_codes: excepciones con severity_weight
  validity_rules: freshness de fuentes de datos

connectors:
  inbound: canales de entrada (MCP connectors)
  outbound: canales de salida
  data_sources: fuentes de datos (KB, ERP, API)

skills:
  sealed: skills FaberLoom no editables
  tenant_configurable: skills que el tenant puede ajustar

agents:
  - id, category, skill_ref, autonomy_ceiling_default
    status_initial: siempre shadow al instalar

validators:
  - id, type (schema_check|freshness_check|rule_check)
    description, blocks_on_fail

risk_rules:
  low_risk_signals: lista
  medium_risk_signals: lista
  high_risk_signals: lista

seed_memory:
  gold_samples_count: int
  gold_samples_source: MWT real | sinteticos

success_metrics:
  primary: VCT u equivalente
  secondary: lista

data_class_typical: N-level tipico
never_actions: lo que el agente NUNCA hace en este vertical
adjacent_packs: packs relacionados para expansion natural

---

## 2. Pack 1 -- wtp_b2b_quoting_safety_footwear (ACTIVO wedge E1)

id: wtp_b2b_quoting_safety_footwear
name: Cotizacion B2B Calzado Seguridad
version: 1.0.0
status: active

work_description:
  El asistente comercial recibe RFQs por WhatsApp y email, busca
  productos en catalogo, verifica stock y precios, arma proformas,
  y las envia al cliente. Todo manual, 15-25h/semana.

unit_of_work: RFQ (solicitud de cotizacion)
user_persona: Asistente comercial / coordinador ventas B2B
value_proposition:
  El RFQ llega, FaberLoom prepara la cotizacion con evidencia completa.
  El asistente revisa y aprueba. 30% menos tiempo. Cero errores precio.

case_schema:
  fields: cliente, productos, cantidades, tallas, norma_tecnica,
    plazo_entrega, condiciones_pago, moneda, destino, uso_final
  evidence_fields: 18 campos (ver SCH_FB_QUOTE_EVIDENCE_BUNDLE)
  exception_codes: 15 canonicos (ver ENT_FB_RFQ_EXCEPTION_TAXONOMY)
  validity_rules:
    lista_precios: freshness <= 7 dias (BLOCKS si vence)
    stock: freshness <= 24h (advertencia si vence)
    certificados: freshness <= 90 dias
    tipo_cambio: freshness <= 1 dia

connectors:
  inbound: [whatsapp_bsp, gmail_oauth, imap_custom]
  outbound: [whatsapp_bsp, gmail_send]
  data_sources: [catalogo_productos, lista_precios, stock_db,
    historial_clientes, kb_normas_tecnicas]

skills:
  sealed: [SKILL_PROFORMA_BUILDER, SKILL_COMPLIANCE_CHECKER,
    SKILL_CLIENT_SERVICE, SKILL_HUMANIZE_COMMS]
  tenant_configurable: [voz_empresa, terminos_comerciales,
    excepciones_cliente]

agents:
  @cotizador: Cognitivo, SKILL_PROFORMA_BUILDER, ceiling=PROPONE
  @mail_ventas: Canal, SKILL_CLIENT_SERVICE, ceiling=EJECUTA_INTERNO
  @seguidor_rfq: Proceso, SKILL_KB_AUDITOR, ceiling=AUTO_NOTIFICA
    trigger: cron 0 6 * * 1-5 America/Costa_Rica

validators:
  precio_vigente: freshness_check <= 7 dias, blocks_on_fail=true
  stock_vigente: freshness_check <= 24h, blocks_on_fail=false
  norma_detectada: schema_check, blocks_on_fail=false

risk_rules:
  low_risk: cliente conocido >=3 compras, SKU en catalogo,
    precio vigente, stock suficiente, norma exacta detectada
  medium_risk: cliente nuevo, precio limite margen, stock parcial
  high_risk: excepcion fuera 15 codigos, norma ambigua,
    cliente en disputa, margen negativo

seed_memory:
  gold_samples_count: 15
  gold_samples_source: MWT real (RFQs historicos CEO 2026-S2)

success_metrics:
  primary: VCT >= 30% semana 6
    con >= 3 tenants, >= 50 RFQs reales, 0 errores severos
  secondary: tiempo_ciclo < 5 min, edit_rate < 40%, rejection_rate < 10%

data_class_typical: N2
never_actions:
  - comprometer fecha entrega sin confirmar proveedor
  - enviar precio si margen < threshold_minimo tenant
  - dar descuento sin aprobacion Owner
  - modificar datos cliente en CRM
  - enviar comunicacion externa sin human_approver_id

adjacent_packs:
  - wtp_b2b_quoting_ppe (mismo buyer, catalogo EPP)
  - wtp_b2b_collections (mismo tenant, flujo cobro)
  - wtp_b2b_quoting_industrial (MRO/repuestos)

---

## 3. Instalacion en tenant

1. Owner selecciona pack en wizard bootstrap paso 5
2. Sistema crea agentes base en status=shadow
3. Owner completa placeholders: catalogo, precios, canales, voz
4. Sistema carga seed_memory (gold samples iniciales)
5. Owner prueba con 3-5 casos reales en SANDBOX
6. Owner aprueba --> agentes pasan a active
7. Pack operativo

---

## 4. Expansion adyacente

Correcta (mismo buyer + canal + flow general):
  wtp_b2b_quoting_safety_footwear --> wtp_b2b_quoting_ppe
    --> wtp_b2b_quoting_industrial --> wtp_b2b_collections

Incorrecta (estructura radicalmente distinta):
  wtp_legal_practice: diferente unit_of_work, compliance, buyer.
  Requiere pack propio, no se deriva del pack de cotizacion.

---

## 5. Metrica VCT

VCT = Verified Commercial Throughput

Formula:
  RFQs enviados sin edicion material / total RFQs reales en scope

Edicion material: cambio que altera precio, producto, cantidad o norma.
Edicion de estilo: NO cuenta como material.

Meta Foundation Beta semana 6:
  VCT >= 30%
  >= 3 tenants activos simultaneamente
  >= 50 RFQs reales procesados
  0 errores severos de confianza

---
Changelog:
- v1.0 (2026-06-24): Creacion. Estructura canonica. Pack 1 completo.
  Instalacion. Expansion adyacente. VCT con formula exacta.
  Cubre gap G6. Alineado con ENT_FB_DECISIONES_E1_v1 D1/D2.
