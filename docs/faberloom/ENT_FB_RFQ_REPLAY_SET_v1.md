---
id: ENT_FB_RFQ_REPLAY_SET_v1
version: 1.1
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma
type: entity
stamp: VIGENTE 2026-05-02 (v1.1 post correccion modelo 2 capas R5)
fecha: 2026-05-02 (update v1.1)
agente: Cowork (redaccion) + CEO (decisiones) + ChatGPT (auditoria R2+R3+R4+R5)
aplica_a: [FaberLoom]
implementa:
  - ENT_FB_VERTICAL_SPEC_OBJECT_v1 (parametrizacion per vertical)
  - POL_FB_KR_PRIVACY_TIERS_v1 (anonimizacion TENANT_DERIVED)
relacionado_con:
  - SPEC_FB_KNOWLEDGE_RIVER_v1 (Layer 1 + Layer 2 arena)
  - ENT_FB_CURATOR_OPERATING_MODEL_v1 (curador rotacion)
  - SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1 (replay set como benchmark wedge)
  - SPEC_FB_ARENA_OPTIMIZER_v1 (PENDIENTE · usa replay set como pool canonico)
---

# ENT_FB_RFQ_REPLAY_SET_v1
## Pool canonico de RFQs historicas para benchmark Arena + suite regresion

## 1. Proposito

Define el pool de RFQs reales historicas que sirve como:
1. **Benchmark Arena Layer 1+2** · evaluacion modelos LLM contra tareas reales del tenant
2. **Suite regresion separada** · 30 fixtures Ciclope (20 R3 cross-industria + 10 safety_footwear MWT) para validar no-regresion
3. **Source of truth para metricas wedge** · comparacion baseline (Sem 0) vs operacion (Sem 7-10)

Sin replay set canonico · "medimos demo · no wedge" (R2).

## 2. Pool · 3 capas de tamano

| Capa | Cantidad | Cuando |
|---|---|---|
| MVP_MIN | 60 | obligatorio Sem 0 baseline · CEO extrae AI-assisted del histórico |
| TARGET | 120 | crecimiento natural Sem 1-12 con auto-add producción |
| CAP | 200 | maximo · rotacion mensual mantiene tamaño |

## 3. Split fairness (R2)

```
40% ganadas       (cotizaciones que cerraron)
25% perdidas      (cotizaciones que no cerraron)
25% ambiguas      (cotizaciones con dudas tecnicas/comerciales)
10% edge/regulatorias (casos raros · regulatorios · alto valor)
```

**Regla R4 inquebrantable:** rotacion mensual NUNCA puede romper este split. Cualquier retiro mensual debe preservar 40/25/25/10 + ≥30% Critical+High. El curador NO puede "limpiar" justo los casos incomodos.

## 4. Sub-split obligatorio (R2)

Cada caso del pool debe tener tags por:
- pais (MX · CO · CR · etc)
- proveedor (Marluvas · Tecmater · futuros)
- familia SKU (calzado dielectrico · calzado agro · zapato seguridad · etc)
- volumen (small <50 unidades · medium 50-200 · large >200)
- stock (completo · parcial · sin stock)
- cliente (recurrente · nuevo)
- complejidad (RFQ simple · RFQ mixta multi-SKU)

Esto evita que el pool quede sesgado a un sub-segmento.

## 5. Casos bloqueantes minimos (R3)

Pool debe tener **≥30% casos Critical+High** del total. Si rotacion mensual baja del umbral · alarma al curador. Esto evita que el sistema "aprenda a cotizar lo facil y escalar lo incomodo" (R3).

## 6. Stratified reservoir + pinned edge cases (R2)

NO FIFO puro. Algoritmo:
- Stratified reservoir sampling para mantener distribucion del split
- Casos marcados `pinned_edge` por AM no expiran hasta que exista reemplazo equivalente
- FIFO botaria casos raros valiosos (R2)

## 7. Lifecycle estados (R4 · ajuste critico)

Cada caso en el replay set tiene UNO de estos estados:

| Estado | Significado | Transiciones |
|---|---|---|
| `candidate` | recien agregado · NO usado en benchmark · espera curador validacion | → active (curador aprueba) · → rejected_contaminated |
| `active` | validado · forma parte del pool oficial · entra a arena | → pinned_edge · → retired |
| `pinned_edge` | edge case marcado · NO se retira hasta tener reemplazo equivalente | → retired (con reemplazo) |
| `retired` | sacado del pool activo · queda en archivo trazable | terminal · solo restore manual |
| `rejected_contaminated` | AM/curador detecto datos contaminados · NO se usa | terminal |

**Sin lifecycle, Sprint 1 inventaria estados en codigo. R4 critico: la arquitectura ya perdio aunque compile.**

## 8. Auto-add vs auto-promote · 2 etapas validacion (v1.1 post R5)

> **CRITICO v1.1:** R5 + CEO 2026-05-02 separaron validacion en 2 etapas explicitas alineadas con modelo 2 capas (capa USUARIO + capa ORGANIZACION).

### 8.1 Etapa 1 · auto-add → candidate (capa USUARIO)

| Operacion | Cuando ocurre | Resultado | Requiere validacion |
|---|---|---|---|
| **Auto-add** | AM aprueba/rechaza/edita output produccion | caso entra como `candidate` | NO |

### 8.2 Etapa 2 · candidate → active (capa USUARIO · AM-driven)

| Operacion | Quien decide | Cuando | Resultado |
|---|---|---|---|
| **Promote candidate → active** | **AM** valida en su flujo personal | AM-driven · cadencia semanal en su Mesa de Control | caso queda en pool MVP del AM (capa 1 · L2) |

Esta etapa es soberania del AM (`ENT_FB_USER_LEARNING_MODEL_v1`). NO requiere comite.

### 8.3 Etapa 3 · active → cross-AM organizacional (capa ORGANIZACION · comite)

| Operacion | Quien decide | Trigger | Resultado |
|---|---|---|---|
| **Promote active L2 → L3 cross-AM** | **Comite** (capa 2) | Cuando ≥5 AMs aplicaron patterns similares · cumple k-anon ≥5 | Pattern queda en pool organizacional cross-AM (L3) |

Esta etapa es soberania del comite (`ENT_FB_COMMITTEE_OPERATING_MODEL_v1`). Aplica 7 checks privacy.

### 8.4 Resumen de las 3 etapas

```
PRODUCCION → Etapa 1 (auto-add) → CANDIDATE
                                    ↓
                                  Etapa 2 (AM valida · capa 1) → ACTIVE en L2 personal
                                                                   ↓
                                                                 Etapa 3 (comite valida · capa 2 · k-anon ≥5) → L3 cross-AM
```

R4+R5 explicit: "Auto-add desde produccion esta bien. Auto-promote NUNCA. AM valida primero (capa 1) · comite valida cross-AM (capa 2)."

**MWT v1 con 1 AM:** todos los patterns se quedan en etapa 2 (L2 del AM Alvaro) · etapa 3 dormida hasta multi-AM · k-anon ≥5 imposible con 1 solo AM.

## 9. Anti-leakage replay vs suite regresion Ciclope (R4)

Los 30 fixtures Ciclope (20 R3 + 10 safety_footwear) son **suite regresion separada** del pool MVP. Reglas:

```
Suite regresion:
- 30 fixtures se ejecutan SIEMPRE pre-deploy y pre-promote
- NO se usan para entrenar memory packs
- NO se usan para promover candidate samples
- NO se mezclan con el pool MVP de 60+ casos reales
- Solo validan no-regresion del comportamiento canonico

Pool MVP:
- 60 RFQs reales que CEO extrae Sem 0 (AI-assisted via Gmail/Outlook+SAP)
- Crece con auto-add hasta 120-200
- Es la fuente de verdad para benchmarks Arena Layer 1+2
- Es el dataset para metricas wedge
```

R4 explicit: "fixtures no se usan para entrenar/promover memory packs · solo para validar no-regresion."

## 10. Metadata minima obligatoria per caso (R4)

Aunque el schema YAML completo se difiere a SPEC implementacion · cada caso del replay set debe tener al minimo:

```yaml
case:
  case_id: string  # uuid
  tenant_id: string  # ej. mwt
  vertical: string  # ej. safety_footwear · ref vertical_spec_object
  country: string  # ISO · destino del cliente
  supplier: string  # marluvas · tecmater · etc
  sku_family: string  # ej. dielectric_boot · agro_boot · safety_shoe
  outcome: enum  # won · lost · ambiguous · edge
  difficulty: enum  # low · medium · high · critical
  exception_type: array<string>  # ref ENT_FB_RFQ_EXCEPTION_TAXONOMY_v1
  privacy_tier: enum  # PRIVATE_RAW · TENANT_DERIVED · GLOBAL_PROMOTABLE · RESTRICTED_SENSITIVE_OR_REGULATED
  source_trace: string  # email_id · call_id · etc · trazabilidad al origen
  state: enum  # candidate · active · pinned_edge · retired · rejected_contaminated
  added_at: ISO8601
  promoted_at: ISO8601?
  promoted_by: string?  # email del curador
```

Sin este minimo · el pool queda como "casos que nos acordamos" (R4).

## 11. Anonimizacion (POL_FB_KR_PRIVACY_TIERS_v1)

Cada caso entra al pool como **TENANT_DERIVED** por default. Reglas:
- Solo PATTERNS ABSTRACTOS pueden aspirar a `GLOBAL_PROMOTABLE` (no RFQs historicas completas)
- Promocion a GLOBAL_PROMOTABLE requiere los 7 checks (privacy review · reidentification test · l-diversity · secret-commercial review · lineage audit · tenant consent/contract check · purpose compatibility check)
- Casos `RESTRICTED_SENSITIVE_OR_REGULATED` (TIER 4) NUNCA salen del tenant · ni siquiera anonimizados

## 12. Ciclo rotacion (R4 ajustado)

| Cadencia | Quien | Que hace |
|---|---|---|
| Semanal | Curador (rol Gobernanza) | Review de candidatos auto-add · marca para promote o reject |
| Mensual | Curador (comite si tenant grande) | Retira casos redundantes · agrega RFQs nuevas cerradas con outcome conocido · valida split 40/25/25/10 · valida ≥30% Critical+High |

**Regla critica R4:** retiro mensual NUNCA rompe stratified split ni baja del 30% Critical+High.

## 13. Estructura YAML config tenant + audit log

```yaml
replay_set_config:
  tenant_id: mwt
  vertical: safety_footwear
  
  pool:
    target_size: 120
    cap_size: 200
    min_size: 60
    
  split_targets:
    won: 0.40
    lost: 0.25
    ambiguous: 0.25
    edge: 0.10
    critical_plus_high_min: 0.30
    
  rotation:
    review_frequency: weekly
    retire_frequency: monthly
    preserve_split_strict: true
    
  auto_add:
    enabled: true
    from: [am_approval, am_rejection]
    initial_state: candidate
    auto_promote: false  # SIEMPRE false · curador valida
    
  regression_suite:
    fixture_sources:
      - source: ciclope_r3_cross_industry
        count: 20
        path: docs/anexos/ciclope_fixtures/r3_cross_industry/
      - source: ciclope_safety_footwear_mwt
        count: 10
        path: docs/anexos/ciclope_fixtures/safety_footwear/
    isolation: strict  # NO entrenamiento · NO promote a memory pack
```

Cada operacion sobre el pool emite audit event con SHA-chain.

## 14. Reglas inquebrantables

1. **Auto-add SI · auto-promote NO.** Curador siempre valida promote.
2. **Rotacion preserva split 40/25/25/10 + ≥30% Critical+High.** Sin excepcion.
3. **Suite regresion Ciclope NO entrena · solo valida.** Aislada del pool MVP.
4. **Cada caso tiene metadata minima obligatoria.** Sin metadata = caso invalido.
5. **TIER 4 NUNCA cross-tenant.** Aplica POL_FB_KR_PRIVACY_TIERS_v1.
6. **Pool MVP arranca con 60 RFQs reales del CEO Sem 0.** No menos.
7. **Pinned edge cases sobreviven a rotacion** hasta tener reemplazo equivalente.

## 15. Pendientes [PENDIENTE — NO INVENTAR]

- Localizacion fisica del pool (DB postgres? S3? formato?) → diferido a SPEC_FB_REPLAY_SET_IMPLEMENTATION_v1
- Schema YAML exacto del config → diferido a SPEC implementacion
- Algoritmo concreto stratified reservoir → diferido SPEC tecnico
- Auto-extraction script Sem 0 (Gmail/Outlook+SAP query patterns) → diferido tooling Sem 0
- Pool size cap dinamico segun tenant tier (gold/platinum mas grande?) → v2

## NO IMPLICA (R4 bonus 5%/50%)

`ENT_FB_RFQ_REPLAY_SET_v1` **NO implica entrenamiento automatico**. El pool es benchmark + suite regresion. Cualquier uso para fine-tuning de modelos requiere SPEC explicito + DPA del tenant + privacy review. NO confundir replay set con training set.

## Changelog
- 2026-05-01 v1.0 VIGENTE: Creacion inicial post review R4. Pool 3 capas (60 MVP · 120 target · 200 cap) con split 40/25/25/10 + ≥30% Critical+High. 5 estados lifecycle (candidate · active · pinned_edge · retired · rejected_contaminated). Auto-add → candidate · auto-promote prohibido. Suite regresion Ciclope (30 fixtures) aislada del pool MVP. Metadata minima obligatoria 11 campos. Anonimizacion TENANT_DERIVED default · 7 checks promocion. Curador valida semanal · retira mensual preservando split. Estructura YAML config tenant. Linea NO implica entrenamiento automatico.

## Stamp
VIGENTE 2026-05-01 — Pool canonico para benchmark Arena + metricas wedge + suite regresion. Sin esta pieza · "medimos demo, no wedge" (R2). Lifecycle explicito evita "cola FIFO glorificada" en Sprint 1 (R4).
