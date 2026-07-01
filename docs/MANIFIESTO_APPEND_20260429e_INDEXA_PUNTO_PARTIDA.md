---
id: MANIFIESTO_APPEND_20260429e_INDEXA_PUNTO_PARTIDA
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: manifiesto_append
stamp: VIGENTE 2026-04-29
fecha: 2026-04-29
agente: Cowork (planificacion + ediciones) + CEO (ejecucion git via PowerShell)
aplica_a: [MWT, FaberLoom]
---

# MANIFIESTO_APPEND_20260429e_INDEXA_PUNTO_PARTIDA

## Que paso
Indexa de "punto de partida limpio" post-saneamiento de la contaminacion FB del 29-abr. Cierra deudas heredadas detectadas en auditoria post-merge:

1. **3 SPECs MWT del 28-abr huerfanos en IDX_PLATAFORMA**: SPEC_ACTION_ENGINE, SPEC_AUDIT_MODULE, ENT_PLAT_ACTION_REGISTRY existian en docs/ raiz desde el 28 (commits bc3695b y 7c403b6) pero NO aparecian en la tabla de IDX_PLATAFORMA. Bug de routing del 28, no del saneamiento. Indexados ahora.

2. **3 SPECs MWT mas con routing parcial**: SPEC_AUTONOMY_CONTROL_ENGINE, SPEC_LLM_ROUTING_ARCHITECTURE, SPEC_QUERY_PROCESSING_PIPELINE estaban referenciados en otros archivos pero no en IDX_PLATAFORMA. Indexados.

3. **Regla "FB vive bajo docs/faberloom/" no documentada**: la leccion del incidente del 29 quedo en MANIFIESTO_REMEDIACION pero no en CLAUDE.md (entrada raiz canonica). Agregada como seccion explicita.

4. **RW_ROOT y DASHBOARD_SNAPSHOT desactualizados**: el saneamiento revirtio RW_ROOT a bc3695b v4.8.7 y DASHBOARD a v10.0 que reflejaban estado pre-29 contaminado. Bumpeados a v4.8.8 y v11.0 con conteos reales post-saneamiento.

## Cambios concretos (5 archivos modificados, 1 archivo nuevo)

### 1. docs/IDX_PLATAFORMA.md
- +1 entrada en tabla Entities: ENT_PLAT_ACTION_REGISTRY (catalogo 53 acciones + DPA LATAM)
- +5 entradas en tabla "Arquitectura de Plataforma": SPEC_ACTION_ENGINE, SPEC_AUDIT_MODULE, SPEC_AUTONOMY_CONTROL_ENGINE, SPEC_LLM_ROUTING_ARCHITECTURE, SPEC_QUERY_PROCESSING_PIPELINE
- Total 6 archivos antes huerfanos ahora ruteados desde su IDX

### 2. CLAUDE.md
- +seccion "Scope FaberLoom" (post-Visibilidad, pre-Scopes de agente)
- Regla absoluta: "Todo archivo nuevo de FaberLoom vive bajo docs/faberloom/. Nunca crear archivos FB en docs/ raiz."
- Excepcion documentada: ~40 archivos FB-puros legitimos pre-29 viven aun en docs/ raiz por compatibilidad con refs cruzadas. Migracion lazy (cuando se editen).
- Justificacion del incidente 29-abr referenciada via MANIFIESTO_REMEDIACION

### 3. docs/RW_ROOT.md
- v4.8.7 -> v4.8.8
- Stamp: 2026-04-27 -> 2026-04-29 (post-saneamiento contaminacion FB)
- +Entry en changelog: documenta saneamiento + indexa punto partida

### 4. docs/DASHBOARD_SNAPSHOT.md
- v10.0 -> v11.0
- aplica_a: [SHARED] -> [MWT, FaberLoom] (cross-scope correcto)
- Conteos actualizados: docs/ raiz 285->298, +docs/faberloom/ (11), +docs/faberloom/gold_samples/ (3), +docs/archivo/manifiestos/contaminacion-29abr/ (5)
- ENT_ 96->99, SPEC_ 11->13
- Versiones bumped: SPEC_ACTION_ENGINE v1.2, SPEC_AUDIT_MODULE v1.0, SPEC_AUTONOMY_CONTROL_ENGINE v1.2, SPEC_LLM_ROUTING_ARCHITECTURE v1.2, SPEC_QUERY_PROCESSING_PIPELINE v1.0, ARCH_AGENT_PRINCIPLES v1.5 (CORE BLINDADO), POL_DATA_CLASSIFICATION v1.4

### 5. docs/MANIFIESTO_APPEND_20260429e_INDEXA_PUNTO_PARTIDA.md (este archivo)
- Nuevo

## Que NO se hizo (defer explicito)

1. **Mover los ~40 FB-puros legitimos pre-29 a docs/faberloom/**: lazy migration. Cuando se edite un archivo FB de docs/ raiz por cualquier motivo, se mueve a docs/faberloom/ en el mismo PR.
   - Razon: mover ahora rompe ~50+ refs cruzadas. Trade-off operacional vs consistencia. Documentado como excepcion en CLAUDE.md.

2. **Reindex pgvector**: operacion de infra, requiere reiniciar mwt-knowledge container. Pendiente en CEO-XX.

3. **Crear ENT_FB_ANCHOR_USE_CASES_v1.md**: mapeo 11 SKILL_ MWT -> templates FB. Diferido hasta que arranque trabajo FB real (no urgente).

4. **Resolver 3 buckets aplica_a (Bucket 1 SHARED 111 entradas, Bucket 2 CROSS 9, Bucket 3 FB-puro raiz 32)**: caso por caso, post-merge. Bucket 3 esta cubierto por la lazy migration documentada en CLAUDE.md.

5. **Revisar SPEC_USER_ADMIN_KNOWLEDGE_FLOW_v1_BETA**: huerfano legitimo FB. Sera resuelto cuando se mueva a docs/faberloom/ via lazy migration.

## Diferencia con MANIFIESTO_APPEND_20260429_REMEDIACION_FB
- REMEDIACION_FB documenta el QUE-PASO de la contaminacion + COMO-SE-LIMPIO (3 commits del branch saneamiento-29abr-fb).
- INDEXA_PUNTO_PARTIDA (este) documenta las 5 mejoras de routing + governance que se indexan post-merge para dejar la KB en estado consistente. Es el paso siguiente al saneamiento.

## Stamp
VIGENTE 2026-04-29 - Indexa punto de partida post-saneamiento. Cierra deudas heredadas pre-29 (3 SPECs huerfanos en IDX_PLATAFORMA) + incorpora regla operacional "FB vive bajo docs/faberloom/" como leccion del incidente.
