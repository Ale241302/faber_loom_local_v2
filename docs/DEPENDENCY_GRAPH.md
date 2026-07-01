# DEPENDENCY_GRAPH — Grafo de Dependencias de Ensamblaje
id: DEPENDENCY_GRAPH
version: 4.1
status: VIGENTE
stamp: VIGENTE - 2026-05-04
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
last_verified: 2026-05-04
verified_by: Claude (Cowork) - retrieval optimization audit golden-set 10q

changelog:
- v4.1 (2026-05-04): +nodo dedicado ENT_OPS_STATE_MACHINE con 13 dependientes vivos (antes solo 2 implicitos via PLB_ORCHESTRATOR + PLB_INTERACCION_CLIENTE). Origen: audit retrieval golden-set 10q detecto undercover ~6x del blast radius real. ASCII puro.
- v4.0 (2026-04-13): KB Hygiene v4.7.0.

---

## Propósito

Pre-flight check para agentes. Antes de ensamblar un schema, el agente consulta este grafo para verificar que todas las dependencias están disponibles y vigentes.

**Alcance:** Este grafo cubre cadenas de ensamblaje de schemas y cadenas operativas criticas. No pretende ser el mapa completo de la KB (conteo total → ver `DASHBOARD_SNAPSHOT.md §Conteos`, fuente unica per POL_DETERMINISMO §1 Regla 3 v1.2). Archivos perifericos (STUBs, LOTEs legacy, POL_ transversales) no requieren nodo aqui salvo que sean consumidos activamente por un schema o cadena operativa.

---

## Cadenas por Schema — Árboles Completos

### SCH_LISTING_AMAZON

```
SCH_LISTING_AMAZON
├── requires: LOC_{PROD}_{LANG}.G1-G8
├── requires: ENT_PROD_{PROD}.C1 (specs técnicos)
├── requires: ENT_MERCADO_{M} (contexto mercado)
├── policies: POL_ROGERS (si PORON en claim)
├── policies: POL_STAMP (todo output)
├── policies: POL_CLAIMS_SCANNER (validación claims)
├── policies: ENT_COMP_CLAIMS (semáforo lenguaje producto)
└── output: Listing Amazon DRAFT → validación → ACTIVO
```

Productos disponibles:

| Producto | LOC EN | LOC ES | LOC PT | ENT_PROD | Status |
|----------|--------|--------|--------|----------|--------|
| Goliath | ✅ LOC_GOL_EN (28 lín) | ✅ LOC_GOL_ES (37 lín) | ✅ LOC_GOL_PT (37 lín) | ✅ ENT_PROD_GOL | LISTO |
| Velox | ✅ LOC_VEL_EN (17 lín) | ⚠️ LOC_VEL_ES (2 lín) | ⚠️ LOC_VEL_PT (2 lín) | ✅ ENT_PROD_VEL | PARCIAL |
| Orbis | ✅ LOC_ORB_EN (17 lín) | ⚠️ LOC_ORB_ES (2 lín) | ⚠️ LOC_ORB_PT (2 lín) | ✅ ENT_PROD_ORB v1.2 | PARCIAL |
| Leopard | ✅ LOC_LEO_EN (17 lín) | ⚠️ LOC_LEO_ES (2 lín) | ⚠️ LOC_LEO_PT (2 lín) | ✅ ENT_PROD_LEO | PARCIAL |
| Bison | ⚠️ LOC_BIS_EN (2 lín) | ⚠️ LOC_BIS_ES (2 lín) | ⚠️ LOC_BIS_PT (2 lín) | ✅ ENT_PROD_BIS | PARCIAL |

### SCH_APLUS_CONTENT

```
SCH_APLUS_CONTENT
├── requires: ENT_PROD_{PROD} (specs + contexto)
├── requires: LOC_{PROD}_{LANG} (copy localizado)
├── requires: ENT_MARCA_EEAT (Brand Story módulo 5)
├── requires: ENT_MERCADO_{M} (contexto mercado)
├── policies: POL_ROGERS (si PORON en claim)
├── policies: POL_STAMP
├── policies: ENT_COMP_CLAIMS (semáforo lenguaje producto)
└── output: A+ Content 5 módulos DRAFT → validación → ACTIVO
```

Mismo mapa de disponibilidad que SCH_LISTING_AMAZON + ENT_MARCA_EEAT (DRAFT, tiene contenido).

### SCH_PROFORMA_MWT

```
SCH_PROFORMA_MWT
├── requires: ENT_PLAT_LEGAL_ENTITY.C (issuer/receiver)
├── requires: ENT_COMERCIAL_PRICING (transfer price policy)
├── requires: ENT_COMERCIAL_MODELOS (modelos comerciales)
├── requires: ENT_PLAT_DESIGN_TOKENS.J (token set ART-02)
├── requires: ART-01 OC Cliente (trigger externo)
├── requires: ART-03 Decisión B/C (modo pricing)
├── policies: POL_VISIBILIDAD (vista dual CEO/cliente)
├── policies: POL_DETERMINISMO (dato único)
├── policies: POL_INMUTABILIDAD (completed = no edit)
├── policies: POL_NUNCA_TRADUCIR (códigos, NCM)
├── policies: POL_DETERMINISMO (sin dato = PENDIENTE)
├── policies: POL_PRINT (impresión dual-view, 13 reglas canónicas)
├── golden_example: PF_0000-2026_GOLDEN_EXAMPLE.html
├── approval: CEO aprueba antes de enviar
└── output: Proforma dual-view DRAFT → CEO approval → ACTIVO
```

Status dependencias: ENT_PLAT_LEGAL_ENTITY ✅ (VIGENTE) · ENT_COMERCIAL_PRICING ⚠️ (DRAFT, contenido mínimo) · ENT_COMERCIAL_MODELOS ✅ (DRAFT, tiene contenido) · ENT_PLAT_DESIGN_TOKENS ✅ (VIGENTE, +sección J v1.1).

### SCH_CONTRATO_NODO

```
SCH_CONTRATO_NODO
├── requires: ENT_PLAT_LEGAL_ENTITY (issuer + receiver con tax_id)
├── requires: ENT_COMERCIAL_PRICING (transfer_price_policy base)
├── requires: ENT_MARCA_IP (propiedad marca Rana Walk)
├── requires: ENT_PLAT_CONTRATO_NODO (ciclo de vida + modelo ejecución)
├── requires: parent_contract (si no es raíz → padre status: active)
├── policies: POL_INMUTABILIDAD (CAPA 2 inmutable desde signed)
├── policies: POL_DETERMINISMO (no duplicar vs NodeContract)
├── policies: POL_VISIBILIDAD (channel_params = CEO-ONLY)
├── policies: POL_NUNCA_TRADUCIR (tech names inmutables)
└── output: Contrato DRAFT → CEO sign → ACTIVE → inmutable
```

Status dependencias: ENT_PLAT_LEGAL_ENTITY ✅ · ENT_COMERCIAL_PRICING ⚠️ · ENT_MARCA_IP ⚠️ (DRAFT, contenido mínimo) · ENT_PLAT_CONTRATO_NODO ✅ (DRAFT, 16K contenido).

### SCH_ISO_AUDIT_PACK

```
SCH_ISO_AUDIT_PACK
├── requires: POL_CALIDAD (política calidad firmada)
├── requires: POL_SSO (política SSO firmada)
├── requires: POL_DATA_CLASSIFICATION (clasificación datos)
├── requires: ENT_GOB_RIESGOS (registro riesgos)
├── requires: ENT_GOB_KPI (indicadores desempeño)
├── requires: ENT_PLAT_SEGURIDAD (roles + control acceso)
├── requires: ENT_PLAT_INFRA (infraestructura documentada)
├── requires: ENT_OPS_EXPEDIENTE (procesos operativos)
├── requires: PLB_REVISION_DIRECCION (actas revisión dirección)
├── requires: PLB_ACCION_CORRECTIVA (no conformidades)
├── requires: PLB_AUDIT_ISO (reportes auditoría interna)
├── requires: POL_ARCHIVO (gestión documental)
├── requires: POL_DETERMINISMO (dato único)
├── requires: POL_STAMP (control vigencia)
├── policies: POL_VISIBILIDAD (nunca incluir CEO-ONLY)
├── policies: POL_NUNCA_TRADUCIR (tech names)
└── output: Pack evidencia ISO DRAFT → auditoría → presentable
```

Status dependencias: ENT_GOB_RIESGOS ✅ · ENT_GOB_KPI ✅ · ENT_PLAT_SEGURIDAD ❌ (STUB) · ENT_PLAT_INFRA ✅ · ENT_OPS_EXPEDIENTE ✅ · PLB_REVISION_DIRECCION ✅ · PLB_ACCION_CORRECTIVA ✅ · PLB_AUDIT_ISO ✅. **Bloqueador:** ENT_PLAT_SEGURIDAD es STUB — necesita contenido antes de ensamblar.

---

## Cadenas por Schema — Referencia Rápida

| Schema | Hereda de | Requires principales | Policies |
|--------|-----------|---------------------|----------|
| SCH_PAGINA_PRODUCTO | — | ENT_PROD_{X}, LOC_{X}_{LANG}, ENT_OPS_TALLAS, ENT_MERCADO_{M} | POL_STAMP |
| SCH_FICHA_TECNICA | — | ENT_PROD_{X}, ENT_TECH, ENT_OPS_TALLAS | POL_STAMP |
| SCH_LLMS_TXT | — | Todos ENT_PROD_*, ENT_TECH, ENT_MARCA_*, ENT_OPS_TALLAS | POL_NUNCA_TRADUCIR |
| SCH_BRIEF_PROVEEDOR | — | ENT_PROD_{X}, LOC_{X}_{LANG}, ENT_COMP_VISUAL, ENT_MARCA_IP, ENT_MERCADO_{M} | POL_VISIBILIDAD |
| SCH_EMPAQUE_BASE | — | ENT_PROD_{X}.A2/E1-E7/E13-E16, ENT_MARCA_IP, ENT_MERCADO_{M}, LOC_{PROD}_EN, ENT_COMP_ROGERS(cond) | POL_ROGERS, POL_STAMP, POL_ANTI_CONFUSION, POL_ORIGEN_LOCAL |
| SCH_EMPAQUE_CAJA_4 | SCH_EMPAQUE_BASE | + layout 4 pares | hereda policies base |
| SCH_EMPAQUE_BOLSA_2 | SCH_EMPAQUE_BASE | + layout 2 pares | hereda policies base |
| SCH_STICKER_BASE | — | ENT_PROD_{X}.E13-E16/F4, ENT_OPS_TALLAS, LOC_TALLAS_{LANG}, ENT_MERCADO_{M}, LOC_{PROD}_{LANG}.C3 | POL_NUNCA_TRADUCIR, POL_ANTI_CONFUSION, POL_ORIGEN_LOCAL |
| SCH_STICKER_CAJA | SCH_STICKER_BASE | + layout caja | hereda policies base |
| SCH_STICKER_BOLSA | SCH_STICKER_BASE | + layout bolsa | hereda policies base |

---

## Cadenas Operativas — Amazon / Mercados

### PLB_OPS_AMAZON

```
PLB_OPS_AMAZON
├── requires: ENT_COMERCIAL_COSTOS (fees, storage)
├── requires: ENT_COMP_AMAZON (compliance policies)
├── requires: ENT_GOB_KPI.B3 (métricas marketplace)
├── consumes: PLB_EXPERIMENTACION (cambios de listing)
├── consumes: PLB_SUPPORT (post-venta)
├── consumes: PLB_ADS (reglas PPC + stock)
└── refs: AUT-001..004 en ENT_PLAT_AUTOMATIONS (inventory sync, restock)
```

### ENT_MKT_KEYWORDS

```
ENT_MKT_KEYWORDS
├── seeds: ENT_MKT_ICP.B5/D5/E5 (buyer language por mercado)
├── seeds: ENT_MKT_USER_TYPES.B (search corridors por user type)
├── outputs_to: LOC_{PROD}_{LANG}.G7 (backend terms ensamblados)
├── consumed_by: PLB_ADS (PPC targeting)
├── consumed_by: PLB_EXPERIMENTACION (test copy)
├── consumed_by: PLB_COPY (integración en listings)
└── consumed_by: SCH_LISTING_AMAZON (assembly final)
```

### ENT_MKT_COMPETENCIA

```
ENT_MKT_COMPETENCIA
├── consumed_by: ENT_MKT_ICP (validación wedge — B9)
├── consumed_by: PLB_EXPERIMENTACION.R5 (trigger competencia)
├── consumed_by: ENT_OPS_DEMAND_PLANNING (contexto mercado)
└── refs: ENT_PROD_COMPARATIVA (diferenciación técnica)
```

### ENT_MKT_USER_TYPES

```
ENT_MKT_USER_TYPES
├── seeds: ENT_MKT_ICP (datos demográficos buyer)
├── seeds: ENT_PROD_{GOL,VEL,ORB,LEO,BIS,MAN,ORC} (specs + target)
├── seeds: LOC_{PROD}_EN (messaging aprobado)
├── consumed_by: PLB_COPY (targeting por user type)
├── consumed_by: PLB_ADS (audience targeting)
├── consumed_by: SCH_LISTING_AMAZON (buyer persona en copy)
├── consumed_by: SCH_APLUS_CONTENT (módulos por user type)
├── consumed_by: ENT_MKT_KEYWORDS (search corridors → keywords)
├── policies: ENT_COMP_CLAIMS (lenguaje compliance-safe)
└── status: DRAFT v1.0 — 9 user types × 7 productos
```

### ENT_COMP_CLAIMS

```
ENT_COMP_CLAIMS
├── extends: POL_CLAIMS_SCANNER (scanner → productos)
├── refs: ENT_COMP_AMAZON.B1 (Amazon prohibited claims)
├── refs: ENT_COMP_REGULATORIO.B1 (ANVISA — confort ≠ medical)
├── refs: POL_ROGERS (disclaimer PORON)
├── consumed_by: PLB_COPY (gate de validación claims)
├── consumed_by: PLB_ADS (ad copy validation)
├── consumed_by: SCH_LISTING_AMAZON (claim check)
├── consumed_by: SCH_APLUS_CONTENT (claim check)
├── consumed_by: ENT_MKT_USER_TYPES (lenguaje compliance-safe)
└── status: DRAFT v1.0 — semáforo GREEN/YELLOW/RED
```

### ENT_MERCADO_BR

```
ENT_MERCADO_BR
├── consumed_by: SCH_LISTING_AMAZON (contexto mercado BR)
├── consumed_by: ENT_MKT_ICP.D (ICP Goliath×BR)
├── consumed_by: ENT_COMERCIAL_CANAL.C2 (canales BR)
├── consumed_by: SCH_STICKER_BASE (sticker specs BR)
├── consumed_by: ENT_OPS_EMPAQUE_FISICO (requisitos BR)
├── refs: ENT_COMP_REGULATORIO (ANVISA, INMETRO, CDC)
└── refs: ENT_PLAT_LEGAL_ENTITY (FRANQ-BR)
```

### ENT_MERCADO_CR

```
ENT_MERCADO_CR
├── consumed_by: SCH_LISTING_AMAZON (contexto mercado CR)
├── consumed_by: ENT_MKT_ICP.E (ICP Goliath×CR)
├── refs: ENT_COMP_REGULATORIO (MEIC)
└── refs: ENT_PLAT_LEGAL_ENTITY (MWT-CR)
```

### ENT_COMP_AMAZON

```
ENT_COMP_AMAZON
├── consumed_by: PLB_OPS_AMAZON (compliance operativo)
├── consumed_by: PLB_EXPERIMENTACION (validación claims en listings)
├── consumed_by: PLB_ADS (advertising policies)
├── refs: ENT_COMP_CLAIMS (claims permitidos/prohibidos)
├── refs: POL_CLAIMS_SCANNER (validación automática)
└── refs: POL_ROGERS (marca PORON)
```

### PLB_INTERACCION_CLIENTE

```
PLB_INTERACCION_CLIENTE
├── requires: ENT_OPS_STATE_MACHINE (estados para respuestas — FROZEN)
├── requires: ENT_OPS_EXPEDIENTE (campos del expediente)
├── requires: ARTIFACT_REGISTRY (documentos descargables ART-01..12)
├── requires: ENT_PLAT_CANALES_CLIENTE (canales de entrada + auth)
├── consumes: ENT_PLAT_KNOWLEDGE.E3 (pgvector para producto, PostgreSQL para expedientes)
├── consumes: LOC_SVC_ES + LOC_SVC_PT (templates de respuesta)
├── consumes: ENT_PLAT_I18N (idioma del cliente)
└── refs: ENT_GOB_AGENTES.E.SVC-01
```

### ENT_PLAT_CANALES_CLIENTE

```
ENT_PLAT_CANALES_CLIENTE
├── requires: LOTE_SM_SPRINT8 (JWT, roles CLIENT_*, permisos)
├── consumed_by: PLB_INTERACCION_CLIENTE (reglas por canal)
├── refs: ENT_PLAT_LEGAL_ENTITY (mapeo client → legal entity)
├── refs: ENT_PLAT_SEGURIDAD (auth por canal, signed URLs)
└── refs: ENT_PLAT_KNOWLEDGE.E3 (routing consultas B2B)
```

### ENT_PLAT_SEGURIDAD

```
ENT_PLAT_SEGURIDAD
├── consumed_by: ENT_PLAT_CANALES_CLIENTE (seguridad por canal B2B)
├── consumed_by: ENT_PLAT_KNOWLEDGE (visibility tiers, API security)
├── consumed_by: PLB_INTERACCION_CLIENTE (signed URLs, anti-injection)
├── consumed_by: PLB_INCIDENT_RESPONSE (clasificación + contactos)
├── refs: ENT_PLAT_INFRA (infraestructura física)
├── refs: POL_DATA_CLASSIFICATION (clasificación datos)
├── refs: POL_VISIBILIDAD (reglas visibilidad)
└── refs: LOTE_SM_SPRINT8 (JWT, roles, permisos)
```

### PLB_INCIDENT_RESPONSE

```
PLB_INCIDENT_RESPONSE
├── requires: ENT_PLAT_SEGURIDAD (framework + clasificación incidentes)
├── refs: ENT_PLAT_INFRA (infraestructura afectada)
├── refs: ENT_GOB_RIESGOS (riesgos estratégicos)
└── refs: ENT_COMP_REGULATORIO (LGPD notificación 72h)
```

### ENT_OPS_EMPAQUE_FISICO

```
ENT_OPS_EMPAQUE_FISICO
├── consumed_by: SCH_EMPAQUE_BASE (arquitectura multi-mercado)
├── consumed_by: SCH_EMPAQUE_CAJA_4 (hereda de base)
├── consumed_by: SCH_EMPAQUE_BOLSA_2 (hereda de base)
├── refs: SCH_STICKER_BASE (matriz de stickers)
├── refs: ENT_MERCADO_BR (requisitos sticker BR)
├── refs: ENT_MERCADO_CR (requisitos sticker CR)
├── refs: ENT_MERCADO_USA (requisitos sticker USA)
└── refs: ENT_COMP_REGULATORIO.B5 (validación legal)
```

### ENT_PLAT_LLM_ROUTING

```
ENT_PLAT_LLM_ROUTING
├── requires: ENT_PLAT_INFRA (servidor donde corre)
├── requires: ENT_PLAT_SEGURIDAD (API keys, encryption)
├── requires: ENT_PLAT_KNOWLEDGE (LLM consumption layer)
└── consumed_by: PLB_PROMPTING (instrucciones de uso)
```

### PLB_PROMPTING

```
PLB_PROMPTING
├── requires: ENT_PLAT_LLM_ROUTING (datos de modelos)
└── requires: ENT_GOB_AGENTES (quién opera)
```

---

## Grafo Inverso — ¿Quién Consume Cada Entity?

### ENT_PROD_GOL (Goliath)
- SCH_LISTING_AMAZON (via LOC_GOL_{LANG})
- SCH_APLUS_CONTENT
- SCH_PAGINA_PRODUCTO
- SCH_FICHA_TECNICA
- SCH_EMPAQUE_CAJA_4 / SCH_EMPAQUE_BOLSA_2
- SCH_STICKER_CAJA / SCH_STICKER_BOLSA
- SCH_BRIEF_PROVEEDOR
- SCH_LLMS_TXT
- PLB_COPY (referencia copywriting)
- PLB_ADS (targeting por specs)
- ENT_MKT_USER_TYPES (cruce user types × producto)

### ENT_PROD_VEL (Velox)
Mismo patrón que Goliath. LOC EN completo, LOC ES/PT parciales.

### ENT_PROD_ORB (Orbis)
Mismo patrón que Goliath. LOC EN completo, LOC ES/PT parciales. **v1.2:** C1 = LeapCore + NanoSpread (sin Arch System).

### ENT_PROD_LEO (Leopard)
Mismo patrón que Goliath. LOC EN completo, LOC ES/PT parciales.

### ENT_PROD_BIS (Bison)
Mismo patrón que Goliath. Todos los LOC parciales (2 líneas).

### ENT_PROD_MAN (Manta)
Mismo patrón que Goliath. LOC EN/ES/PT completos.

### ENT_PROD_ORC (Orca)
Mismo patrón que Goliath. LOC EN/ES/PT completos.

### ENT_TECH (Tecnologías)
- SCH_FICHA_TECNICA (specs técnicos)
- SCH_LLMS_TXT (sección tecnologías)
- PLB_COPY (claims técnicos)

### ENT_MARCA_EEAT (Brand Story)
- SCH_APLUS_CONTENT (módulo 5 Brand Story)
- SCH_LLMS_TXT (sección About)

### ENT_PLAT_LEGAL_ENTITY (Entidades Legales)
- SCH_PROFORMA_MWT (issuer/receiver)
- SCH_CONTRATO_NODO (partes del contrato)

---

### PLB_ORCHESTRATOR (FROZEN)

```
PLB_ORCHESTRATOR
├── requires: MWT_ARCHITECTURE_PACKAGE (paquete arquitectónico)
├── consumed_by: LOTE_SM_SPRINT0 (bootstrap)
├── consumed_by: LOTE_SM_SPRINT1..10 (referencia operativa)
├── refs: ENT_OPS_STATE_MACHINE (FROZEN — estados del expediente)
└── status: FROZEN — no modificar, solo referenciar
```

### ENT_OPS_STATE_MACHINE (FROZEN v1.2.2)

```
ENT_OPS_STATE_MACHINE
├── consumed_by: PLB_ORCHESTRATOR (commands + transaction boundaries)
├── consumed_by: PLB_INTERACCION_CLIENTE (estados para respuestas B2B)
├── consumed_by: PLB_REGISTRO_PROFORMA (C1-C5 commands)
├── consumed_by: SKILL_CLIENT_SERVICE (estados expediente)
├── consumed_by: ENT_PLAT_CANALES_CLIENTE (transiciones canónicas)
├── consumed_by: ENT_GOB_KPI (event log para KPI tiempo por fase)
├── consumed_by: ENT_PLAT_SSOT (SSOT #1 estados expediente)
├── consumed_by: ENT_PROD_LANZAMIENTO (T2.4 lead time)
├── consumed_by: ENT_OPS_CASO_2391 (H2/H3/H7/H8 — Sprint 11)
├── consumed_by: LOC_SVC_ES (estados canónicos ES)
├── consumed_by: LOC_SVC_PT (estados canônicos PT)
├── consumed_by: ROADMAP_EXTENDIDO_POST_DIRECTRIZ
├── consumed_by: docs/faberloom/SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1
├── refs_históricos: LOTE_SM_SPRINT20B/22/23/25/26 (DONE — referencia inmutable)
└── status: FROZEN — modificación rompe los 13 dependientes vivos. Solo referenciar.
```

### ENT_COMERCIAL_CLIENTES

```
ENT_COMERCIAL_CLIENTES
├── requires: ENT_PLAT_LEGAL_ENTITY (mapeo cliente → entidad legal)
├── consumed_by: PLB_REGISTRO_PROFORMA (datos del cliente en proforma)
├── consumed_by: SCH_PROFORMA_MWT (receiver data)
└── refs: ENT_MERCADO_{M} (contexto mercado del cliente)
```

### PLB_REGISTRO_PROFORMA

```
PLB_REGISTRO_PROFORMA
├── requires: SCH_PROFORMA_MWT (schema de ensamblaje)
├── requires: ENT_COMERCIAL_CLIENTES (datos cliente)
├── requires: ENT_COMERCIAL_PRICING (política de precios)
└── refs: ARTIFACT_REGISTRY.ART-02 (instancia proforma)
```

### PLB_INDEXACION

```
PLB_INDEXACION
├── consumed_by: Claude (Arquitecto) — gate de auto-auditoría
├── refs: POL_DETERMINISMO, POL_NUEVO_DOC, POL_STAMP
├── refs: ENT_GOB_PENDIENTES (check #6)
└── refs: ENT_PLAT_SEGURIDAD (check #9)
```

### PLB_INTEL_ITERACION_MANUAL

```
PLB_INTEL_ITERACION_MANUAL
├── refs: ENT_GOB_AGENTES (modelo 5 agentes)
├── refs: ENT_PLAT_LLM_ROUTING (selección de modelo)
└── refs: PLB_PROMPTING (fichas de precisión)
```

### PLB_PILOTO_B2B

```
PLB_PILOTO_B2B
├── requires: ENT_MKT_ICP (criterios selección piloto)
├── requires: ENT_PLAT_CANALES_CLIENTE (canales B2B)
└── status: STUB — contenido pendiente
```

### PLB_AUDIT_VISUAL_BRIEF

```
PLB_AUDIT_VISUAL_BRIEF
├── refs: ENT_COMP_VISUAL (guidelines visuales)
├── refs: ENT_PLAT_DESIGN_TOKENS (tokens sistema)
└── consumed_by: PLB_AUDIT_VISUAL (auditoría visual completa)
```

### ENT_PROD_SCANNER_GLOSARIO

```
ENT_PROD_SCANNER_GLOSARIO
├── consumed_by: ENT_PROD_SCANNER (terminología)
├── consumed_by: PLB_SCANNER_DISTRIB (vocabulario distribución)
└── refs: ENT_TECH (tecnologías base)
```

Changelog:
- v1.0 (2026-03-14): creación inicial. 5 schemas con árbol completo, 10 referencia rápida, grafo inverso 8 entities. (Ola K).
- v1.1 (2026-03-14): conteos LOC_GOL_ES/PT corregidos 14→37 (F-1).
- v1.2 (2026-03-15): policies SCH_PROFORMA corregidas (POL_STAMP/PRINT → POL_VISIBILIDAD/DETERMINISMO/INMUTABILIDAD/NUNCA_TRADUCIR/VACIO). Fix contradicción hallazgo ChatGPT H3.
- v2.0 (2026-03-15): +6 cadenas operativas Amazon/Mercados (PLB_OPS_AMAZON, ENT_MKT_KEYWORDS, ENT_MKT_COMPETENCIA, ENT_MERCADO_BR, ENT_MERCADO_CR, ENT_COMP_AMAZON). Cierra brecha: 6 archivos estratégicos fuera del grafo. Sesión completitud v4.3.
- v2.1 (2026-03-15): +2 cadenas canal B2B (PLB_INTERACCION_CLIENTE, ENT_PLAT_CANALES_CLIENTE). Sesión canal B2B v4.4.
- v2.2 (2026-03-15): +3 cadenas seguridad (ENT_PLAT_SEGURIDAD, PLB_INCIDENT_RESPONSE, ENT_PLAT_CANALES_CLIENTE ref actualizada). Sesión seguridad + auditoría triangulada v4.4.1.
- v2.3 (2026-03-16): SCH_PROFORMA_MWT +ENT_PLAT_DESIGN_TOKENS.J, +POL_PRINT, +golden_example.
- v2.4 (2026-03-15): +ENT_OPS_EMPAQUE_FISICO. SCH_STICKER_BASE +LOC. SCH_EMPAQUE_BASE +LOC. ENT_MERCADO_BR +consumed_by sticker/empaque.
- v2.5 (2026-03-18): +ENT_PLAT_LLM_ROUTING y PLB_PROMPTING al grafo. Consolidación 3 patches pendientes.
- v2.6 (2026-03-18): +LOTE_SM_SPRINT0 (histórico). +PLB_RISK_ASSESSMENT (STUB). +ENT_PLAT_SCANNER_SECURITY (STUB). 3 refs rotas resueltas.
- v2.7 (2026-03-18): +LOTE_SM_SPRINT10 ref. Remediación stamps y headers.
- v3.0 (2026-03-18): +8 nodos críticos (PLB_ORCHESTRATOR FROZEN, ENT_COMERCIAL_CLIENTES, PLB_REGISTRO_PROFORMA, PLB_INDEXACION, PLB_INTEL_ITERACION_MANUAL, PLB_PILOTO_B2B, PLB_AUDIT_VISUAL_BRIEF, ENT_PROD_SCANNER_GLOSARIO). Contrato de alcance documentado.
- v3.1 (2026-04-03): +ENT_MKT_USER_TYPES (nodo completo con seeds, consumed_by, policies). +ENT_COMP_CLAIMS (nodo actualizado: extends POL_CLAIMS_SCANNER, consumed_by 5 archivos). ENT_MKT_KEYWORDS +seeds ENT_MKT_USER_TYPES. SCH_LISTING_AMAZON +policies ENT_COMP_CLAIMS. SCH_APLUS_CONTENT +policies ENT_COMP_CLAIMS. Grafo inverso +MAN, +ORC, +ENT_MKT_USER_TYPES en todos los productos. ENT_PROD_ORB nota v1.2 (sin Arch System). Conteo archivos: 289.
