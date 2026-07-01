---
id: POL_FB_KNOWLEDGE_VALIDITY_AND_EXPIRY_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma
type: policy
stamp: VIGENTE 2026-05-02
fecha: 2026-05-02
agente: Cowork (redaccion) + CEO (decisiones) + ChatGPT (auditoria R6+R7)
aplica_a: [FaberLoom]
implementa: bonus 5%/50% R6 ChatGPT (mejora transversal cross-vertical regulado)
relacionado_con:
  - SPEC_FB_KNOWLEDGE_RIVER_v1.1
  - ENT_FB_USER_LEARNING_MODEL_v1
  - ENT_FB_COMMITTEE_OPERATING_MODEL_v1
  - ENT_FB_RFQ_REPLAY_SET_v1.1
  - ENT_FB_QUOTING_SOURCE_OF_TRUTH_v1.1
  - POL_FB_KR_PRIVACY_TIERS_v1.1
origen: ChatGPT R6 bonus 5%/50% + R7 validacion · "criterio vencido NO es conocimiento · es trampa con toga"
---

# POL_FB_KNOWLEDGE_VALIDITY_AND_EXPIRY_v1
## Politica transversal de vigencia y expiry del knowledge

## 1. Proposito

R6 + R7 critico: **knowledge sin vigencia es peligroso en TODO vertical regulado**. Lo que en MWT cotizacion es "precio vencido" · en legal es "criterio juridico vencido" · en medico es "guideline obsoleto" · en financiero es "regulacion cambiada" · en software es "framework deprecated o CVE".

Esta politica es **transversal** (NO legal-only · NO MWT-only). Aplica a:
- MWT cotizacion B2B (ya canonizado · vigencia per fuente)
- Legal practice (jurisprudencia · ley · plazos procesales)
- Medical regulated (guidelines · drug recalls · contraindicaciones)
- Financial advisory (regulaciones · tasas · KYC · scoring)
- Compliance auditing (normas · CVEs · audit cycles)
- Industrial HSE (normas tecnicas · certificados · lotes · recalls)
- Software factories (frameworks · CVEs · APIs deprecated · runtime versions)

> **Frase canonica:** Knowledge sin metadata de vigencia · NO es conocimiento gobernable.

## 2. Estructura canonica · `validity_metadata`

Cada knowledge candidate (pattern · template · regla · gold sample · etc) debe llevar:

```yaml
validity_metadata:
  # Origen
  domain_type: enum  # regulated · operational · commercial · technical · legal
  jurisdiction: string?  # ISO country/region · solo si aplica
  authority_source: string  # quien dicta · ej. "ASTM" · "INVIMA" · "Banco Central MX" · "ISO" · "RFC IETF"
  authority_rank: int?  # 1=primaria · 2=interpretacion · 3=criterio interno
  
  # Tiempo
  effective_from: date  # cuando empezo a aplicar
  valid_until: date?  # null = sin expiry conocido
  review_due_at: date  # OBLIGATORIO · proxima revision agendada
  
  # Lineage
  supersedes: string?  # version anterior reemplazada
  superseded_by: string?  # version posterior que lo reemplaza (cuando aplique)
  version: string  # ej. "v1.0" · "ASTM_F2413-18"
  
  # Governance
  reviewer_required: boolean  # true si requiere reviewer humano para promote
  reviewer: string?  # quien reviso
  reviewed_at: ISO8601?
  
  # Comportamiento al expirar
  stale_action: enum  # warn · block · archive · auto_review
  warn_threshold_days: int  # default 30 · warning antes de expirar
  block_threshold_days: int  # default 0 · cuando bloquear uso
  
  # Trazabilidad
  created_at: ISO8601
  created_by: string
  trace_id: string  # cadena audit
```

## 3. Aplicacion per vertical

### 3.1 MWT cotizacion (ya canonizado · refuerzo aqui)

| Knowledge | Validity field |
|---|---|
| Lista precios | effective_from · valid_until · review 24h |
| Stock ATP | freshness 5min · STALE 15min · FAIL 60min |
| Catalogo SKU | review 30d |
| Cert ASTM F2413 | valid_until 1095d (3 anos) |

### 3.2 Legal practice

| Knowledge | Validity field |
|---|---|
| Criterio jurisprudencial | review_due_at trimestral · authority_source: SCJN/Tribunal X |
| Reforma legal | superseded_by trackeable · effective_from explicit |
| Plazo procesal | valid_until con calculo legal-aware |
| Template demanda | review semestral · stale_action: warn |
| Estrategia procesal | NO promotable cross-cliente · queda en matter |

### 3.3 Medical regulated

| Knowledge | Validity field |
|---|---|
| Guideline clinica | review trimestral · authority_source: organismo per pais |
| Drug recall | stale_action: BLOCK inmediato · alert critico |
| Contraindicacion | valid_until indefinido · revision con cada update FDA/COFEPRIS |
| Protocolo institucional | review semestral |

### 3.4 Financial advisory

| Knowledge | Validity field |
|---|---|
| Regulacion bancaria | superseded_by tracking · authority_source: regulador |
| Tasa interes | freshness <24h · stale_action: BLOCK |
| KYC client profile | review anual · stale_action: warn |
| Risk scoring model | version explicit · review trimestral |

### 3.5 Compliance auditing

| Knowledge | Validity field |
|---|---|
| Norma ISO/SOC | valid_until per certification cycle |
| CVE | freshness <24h via NVD · stale_action: BLOCK |
| Audit finding | matter-scoped · NO promotable global |
| Control test | review per audit cycle |

### 3.6 Industrial HSE

| Knowledge | Validity field |
|---|---|
| Norma tecnica ASTM/NIOSH | valid_until per cert | 
| Certificado producto | valid_until explicit · stale_action: BLOCK |
| Permiso ambiental | valid_until per autoridad · review_due 90d antes |
| Procedure HSE | review anual |

### 3.7 Software factories

| Knowledge | Validity field |
|---|---|
| Framework version | superseded_by tracking · CVE alerts |
| CVE/vulnerability | freshness <24h · stale_action: BLOCK |
| API contract externa | superseded_by · breaking changes alert |
| Best practice tech | review trimestral |
| Dependency version | review continuous · auto-PR cuando expira |

## 4. Comportamiento del sistema con knowledge stale

```
1. Pattern aprendido en L2 con validity_metadata.valid_until = 2026-12-31

2. Sistema poll diario:
   - Si valid_until - now < warn_threshold_days → emite evento `validity.warning`
   - Si valid_until - now < block_threshold_days → emite evento `validity.block`
   - Si valid_until pasado → status: archived (NO se elimina · audit preserved)

3. Stale_action behaviors:
   - warn: pattern usable pero genera warning en evidence_bundle
   - block: pattern NO se usa en outputs nuevos · queda historico
   - archive: pattern movido a archived · NO active queries
   - auto_review: trigger comite revision para extender validity

4. Curador (capa 2 organizacion) recibe alerts agregadas semanal:
   - patterns proximos a expirar
   - patterns con stale_action triggered
   - propuesta de renovacion vs archive
```

## 5. Integracion con piezas canonizadas

| Pieza | Como integra |
|---|---|
| `SPEC_FB_KNOWLEDGE_RIVER_v1.1` | Toda promotion L2→L3 requiere validity_metadata completo |
| `ENT_FB_USER_LEARNING_MODEL_v1` | Patterns capa 1 con validity_metadata · AM ve "este pattern expira en N dias" |
| `ENT_FB_COMMITTEE_OPERATING_MODEL_v1` | Comite review semanal incluye validity_warnings · review_due_at queue |
| `ENT_FB_RFQ_REPLAY_SET_v1.1` | Cases del replay set llevan validity_metadata · stale cases archived |
| `ENT_FB_QUOTING_SOURCE_OF_TRUTH_v1.1` | Las 16 fuentes ya tienen freshness SLA (caso especial de validity) |
| `POL_FB_KR_PRIVACY_TIERS_v1.1` | Validity NO sustituye privacy tier · son ortogonales |

## 6. Eventos canonicos validity

```
validity.metadata.added           ← knowledge candidate creado con metadata
validity.warning                  ← N dias antes de expirar
validity.block                    ← stale_action=block triggered
validity.expired                  ← valid_until pasado · archived
validity.review_due               ← review_due_at alcanzado
validity.renewed                  ← curador renovó validity
validity.superseded               ← superseded_by setteado
```

## 7. Reglas inquebrantables

1. **Knowledge sin `validity_metadata` NO es promotable** · L2→L3 bloqueado.
2. **`review_due_at` es obligatorio** · null no permitido (forzar revision periodica).
3. **`stale_action` debe declarar comportamiento explicito** (warn/block/archive/auto_review).
4. **CVE-related y drug-recall y safety-critical son siempre `stale_action: block` y `freshness <24h`**.
5. **Patterns con validity vencida NO se eliminan** · se archivan (audit preservation).
6. **Curador puede renovar validity con justificacion** · NO indefinidamente · max extension 1 ciclo.
7. **`superseded_by` chain debe ser unidireccional** · NO ciclos.
8. **`valid_until` NO sustituye revisions periodicas** · review_due_at es independiente.
9. **Cliente NUNCA ve metadata raw** · solo "Vigente hasta X" en evidence bundle.

## 8. Pendientes [PENDIENTE — NO INVENTAR]

- Migration tooling para cargar validity_metadata en patterns existentes (post-canonizacion)
- Integration con feeds externos auto (NVD para CVEs · FDA recalls · etc) → diferido v2
- Auto-review trigger (LLM-assisted suggestion para extender validity) → diferido v3
- Compliance reporting per vertical (cuantos patterns expirando) → diferido v2

## NO IMPLICA (R4 bonus 5%/50%)

`POL_FB_KNOWLEDGE_VALIDITY_AND_EXPIRY_v1` **NO implica auto-update automatico de knowledge desde fuentes externas**. La validity declara cuando el knowledge expira · pero el RENEW lo decide humano (curador). Sistemas externos (NVD · FDA · regulatorio) pueden DISPARAR alertas · pero NUNCA reemplazar review humana en knowledge regulado.

## Changelog
- 2026-05-02 v1.0 VIGENTE: Creacion inicial post R6 bonus + R7 validacion. Politica transversal cross-vertical regulado (legal · medical · financial · compliance · industrial · software · MWT cotizacion). Estructura validity_metadata canonica con 14 campos (origen + tiempo + lineage + governance + stale_action + trazabilidad). Aplicacion documentada per 7 verticales con ejemplos. 7 eventos canonicos validity. 9 reglas inquebrantables incluyendo CVE/drug-recall/safety con block obligatorio. NO implica auto-update sin review humana. Esta canonizada como VIGENTE (no DRAFT) porque aplica HOY a MWT (refuerza freshness SLA del Source of Truth) sin esperar verticales nuevos.

## Stamp
VIGENTE 2026-05-02 — Politica transversal de vigencia. Bonus 5%/50% R6 aplicado. Aplica a TODOS los verticales regulados desde dia 1. Sin esto · "criterio vencido es trampa con toga" (R6) · drug recall ignored · CVE explotado · etc. Cero costo de canonizar ahora · alto retorno cross-vertical.
