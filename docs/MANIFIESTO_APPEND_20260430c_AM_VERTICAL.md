---
id: MANIFIESTO_APPEND_20260430c_AM_VERTICAL
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza
type: manifiesto_append
stamp: VIGENTE 2026-04-30
fecha: 2026-04-30
agente: Cowork (planificacion + redaccion) + CEO (decisiones de scope flagship)
aplica_a: [FaberLoom]
relacionado_con:
  - MANIFIESTO_APPEND_20260430_KNOWLEDGE_RIVER
  - MANIFIESTO_APPEND_20260430b_P16_DECOMPOSITION
  - ENT_FB_SUB_AGENTS_LIBRARY_v1
  - SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1
---

# MANIFIESTO_APPEND_20260430c_AM_VERTICAL

## Que paso
Tercera y ultima indexa del 30-abr. Cierra el ciclo arquitectonico del dia: Knowledge River (modelo conocimiento) + P16 (modelo ejecucion) + Vertical AM (primer caso productivo aplicando ambos end-to-end).

CEO instruyo "haslos todos para indexar no hagas nada de programacion solo indexar conocimiento" tras presentar 4 opciones para los pendientes. Decisiones aplicadas:
- #1 → opcion A: catalogo verticalizado AM B2B (HECHO en esta indexa)
- #2 → opcion B: SPEC minimo + 3 flows criticos (HECHO en esta indexa)
- #3 → opcion C: governance SPEC diferido hasta tener vertical produciendo eventos reales (NO HECHO · documentado como diferido explicito)
- #4 → opcion C: update agent builder diferido hasta tener catalogo + SPEC AM en datos reales (NO HECHO · documentado como diferido explicito)

## Decisiones arquitectonicas reforzadas

1. **Pickeo libre del catalogo** (no pre-categorizacion core/vertical)
   - Insight CEO: "se puede escoger cualquiera que este en templates, simplemente escojo si necesito"
   - Refactor "core vs vertical" emergera con datos cuando aparezca segundo vertical (Code, Soporte, etc)
   - Hasta entonces el catalogo es el catalogo, builder expone todos los sub-agentes y el usuario pickea

2. **Scope minimo para validar P16 antes de comprometer mas SPECs**
   - Riesgo identificado: SPECs largos sin codigo se desconectan de realidad rapido (leccion Indexa Punto Partida 6 SPECs huerfanos del 28-abr)
   - Mitigacion: SPEC mininimo + 3 flows criticos cubriendo 80% del volumen real (clasificacion + cotizacion + escalacion)

3. **Diferir governance SPEC hasta evidencia real**
   - Knowledge River SPEC define el QUE (modelo conceptual)
   - Governance SPEC tecnico (tablas postgres, eventos, APIs) requiere saber QUE eventos genera el vertical real
   - Escribir tabla schemas antes de tener evento real = inventar
   - Cuando AG_AM produzca eventos en shadow mode, ahi se escribe governance SPEC sobre realidad

4. **Diferir update agent builder hasta evidencia real**
   - Builder current asume composicion sin sub-agentes
   - Actualizar el flow conversacional antes de saber como se compone realmente con sub-agentes en produccion = inventar UX
   - Tras 30-60d de tenant beta MWT/Marluvas con AG_AM en shadow, el flow conversacional surgira de patterns de uso reales

## Archivos creados/modificados en esta indexa

| Archivo | Accion | Lineas |
|---|---|---|
| docs/faberloom/ENT_FB_SUB_AGENTS_LIBRARY_v1.md | NUEVO | ~430 |
| docs/faberloom/SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1.md | NUEVO | ~350 |
| docs/RW_ROOT.md | bump v4.8.10 → v4.8.11 + entry changelog | +1 entry |
| docs/DASHBOARD_SNAPSHOT.md | bump v12.1 → v12.2 + conteos | +1 entry |
| docs/MANIFIESTO_APPEND_20260430c_AM_VERTICAL.md | NUEVO · este archivo | ~150 |

## Conteos esperados post-indexa
- docs/ raiz: 300 → 301 (+1 manifiesto)
- docs/faberloom/: 13 → 15 (+1 ENT + 1 SPEC)
- Repo total: 421 → 424

## Cierre del dia 30-abr · 3 indexas consecutivas

| Indexa | Hora | Output | Pieza arquitectonica |
|---|---|---|---|
| 30abr-a (Knowledge River) | manana | SPEC_FB_KNOWLEDGE_RIVER_v1 (~600 linea) | modelo conocimiento (templates como activos) |
| 30abr-b (P16 Decomposition) | tarde | ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1 (192 lineas) | modelo ejecucion (orquestadores delgados + sub-agentes atomicos) |
| 30abr-c (AM Vertical) | tarde-tarde | ENT_FB_SUB_AGENTS_LIBRARY_v1 + SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1 (~780 lineas combined) | primer caso productivo aplicando ambos |

Total nuevas lineas de conocimiento canonizado en el dia: ~1570 lineas.

ARCH_AGENT_PRINCIPLES.md sealed v1.5 NO tocado en ninguna de las 3 indexas (P16 vive como extension FB). FROZENs intactos.

## Pendientes post-merge

### Inmediatos (proxima sesion)
1. Cuando se aborde implementacion code: PLB_ORCHESTRATOR + AG-01 a AG-07 toman SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1 como contract y construyen sub-agentes individuales en SHADOW
2. Pricing $XXX en SPEC_FB_VERTICAL_AM [PENDIENTE — CEO + finance]
3. Decisiones pendientes v1.1 en SPEC_FB_VERTICAL_AM (7 items)

### Mediano plazo (2-4 semanas)
4. ENT_FB_GOVERNANCE_PROFILES_v1 con los 5 perfiles preconfigurados detallados (del manifiesto Knowledge River)
5. CLI commands: `fbl subagent ls/inspect/test`, `fbl orchestrator inspect`, `fbl trace <request_id>`, `fbl template ls/publish/clone`
6. POL nueva (o extension de POL_DATA_CLASSIFICATION) para reglas de redaction PII obligatoria antes de pool L3 cross-tenant

### Diferidos explicitos (esperan datos reales)
7. SPEC_FB_TEMPLATE_GOVERNANCE_v1 (tablas postgres, eventos, APIs REST) → cuando AG_AM produzca eventos reales en shadow
8. SPEC_FB_AGENT_BUILDER v3.0 reescrito P16-native → cuando catalogo + SPEC AM tengan 30-60d de uso real

### Validaciones 90d (post-implementacion)
9. Token cost reduction -65% +-10pp (P16)
10. Latency p95 F1 <8s · F2 <13s · F3 <5s
11. Send-rate sin edicion sustantiva DRAFT_WRITER >=0.6 (P15)
12. Proforma close-rate PROFORMA_BUILDER >= baseline humano (P15)
13. Escalation SLA compliance >=95%
14. Curador overhead <2h/sem per tenant
15. Audit log searchability <30s

## Diferencial defendible reforzado vs competencia

Tras esta indexa, FaberLoom tiene 3 piezas arquitectonicas que ChatGPT WA / Notion / Linear NO tienen:
1. **Knowledge River**: templates como activos organizacionales con destilacion colegiada (ChatGPT/Notion: agentes privados sin captura colectiva)
2. **P16 Atomic Agents**: composicion fractal con sub-agentes atomicos especializados (ChatGPT: monolitico) — habilita -65% token cost + audit granular + learning concentration
3. **Vertical AM B2B end-to-end**: SPEC contract-first listo para implementar con metricas de validacion 90d (competencia: agente generico sin contracts ni outcome accountability)

Moat real: arquitectura desde dia 1 que ChatGPT no puede copiar sin redisenar su core.

## Origen del insight clave del dia

CEO durante la sesion vespertina, articulando preferencia operacional:
> "yo veo que se puede escoger cualquiera que este en templates, simplemente escojo si necesito"

Y posteriormente, instruccion ejecutiva:
> "haslos todos para indexar no hagas nada de programacion solo indexar conocimiento"

La instruccion captura la disciplina de no contaminar el deliverable de hoy con codigo: separar fase de canonizacion de conocimiento (fast, low risk) de fase de implementacion (slow, high risk). Es consistente con principio de contract-first del Action Engine (decision D del 28-abr).

## Stamp
VIGENTE 2026-04-30 — Indexa de cierre del 30-abr. 3 indexas consecutivas canonizan: Knowledge River (modelo conocimiento) + P16 Atomic Agents (modelo ejecucion) + Vertical AM B2B (primer caso productivo). FB v1 listo para implementacion: SPECs contract-first, sub-agentes con schema I/O completo, metricas de validacion 90d definidas, governance + builder updates explicitamente diferidos hasta evidencia real. ARCH sealed v1.5 NO tocado. FROZENs intactos.
