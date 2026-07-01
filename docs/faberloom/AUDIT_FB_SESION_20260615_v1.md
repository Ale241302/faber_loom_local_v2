# AUDIT_FB_SESION_20260615 - Decision confiabilidad + deltas Knowledge River

id: AUDIT_FB_SESION_20260615_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (IDX_FB_FOUNDATION_BETA)
type: AUDIT
stamp: VIGENTE -- 2026-06-15 -- sesion de pensamiento Project "MWT Knowledge"
aprobador: CEO (Alvaro)
aplica_a: [FaberLoom]
relacionado: SPEC_FB_KNOWLEDGE_RIVER_v1 v1.1 - ENT_FB_INSIGHTS_KIMI_SWARM_8_ATERRIZAJE_v1 - SPEC_FB_BUILD_SEQUENCE_v3 - SPEC_FB_AUTH_TENANT_RBAC_v1

---

## A. Proposito

Registrar lo que produjo la sesion de pensamiento del 2026-06-15: una decision de
producto (nivel de confiabilidad) y dos observaciones (deltas) sobre el Knowledge
River surgidas del swarm FB-SWARM-2026-06-15. NO edita SPEC (respeta SPEC freeze
hasta E2). Los deltas quedan como observacion para backlog post-E2.

## B. Decision registrada - nivel de confiabilidad (CEO 2026-06-15)

FaberLoom apunta a asistentes "MUY CONFIABLES con chequeos automaticos", NO
"contractual/garantizado al 100%".

Consecuencias:
- Se sigue alquilando inferencia (Claude/OpenAI). NO self-hosted deterministico en v1.
- El tope de la fabrica de niveles 0-4 = "muy confiable con validacion automatica".
- Respaldo: el nivel contractual byte-identical no es alcanzable sobre API comercial
  (ver ENT_FB_INSIGHTS_KIMI_SWARM_8 B.1).

Hueco abierto: la confiabilidad es un EJE distinto del Knowledge River (el River
gobierna flujo de conocimiento; la confiabilidad gobierna calidad de output). Hoy no
tiene archivo canonico dedicado. Mapear contra la fabrica de niveles 0-4 y dejar
explicito que "nivel 4 != contractual".

## C. Delta A - colision de nomenclatura "niveles" (observacion, NO edit)

El River tiene "3 niveles de aprendizaje" (L1 auto / L2 firma rapida / L3 critico =
gobernanza de cambios). La fabrica tiene "niveles 0-4" (madurez/confiabilidad del
skill). Misma palabra, dos sistemas. Riesgo de confusion en SPEC y UI.
Accion sugerida (post-E2): renombrar un eje (ej. "niveles de gobernanza" vs "grados
de confiabilidad").

## D. Delta B - aislamiento storage L0/L2 puede ser insuficiente (observacion, NO edit)

El River describe L0/L2 como "postgres + pgvector con user_id como filtro estricto".
El swarm documento que para agentes LLM el filtro por user_id/metadata NO basta en la
capa vectorial (namespace/shard por tenant es el minimo) y que hay fugas LLM que
RLS+user_id no cubre (KV-cache, tool state global).
Accion sugerida (post-E2): revisar storage de L0/L2 contra SPEC_FB_AUTH_TENANT_RBAC_v1
y POL_FB_KR_PRIVACY_TIERS. NO urgente (capa 2 del River dormida con 1 AM).

Nota: el riesgo de privacidad al promover aprendizaje de un tercero YA esta cubierto en
canon (pool anonimo + k-anonymity >=5). No es hueco.

## E. Restricciones aplicadas en este indexado

- No se toco FROZEN (ENT_OPS_STATE_MACHINE, PLB_ORCHESTRATOR).
- No se creo SPEC_FB nuevo (SPEC freeze). Deltas como observacion AUDIT.
- Visibilidad INTERNAL. Nada CEO-ONLY.

---

Changelog:
- v1.0 (2026-06-15): creacion. Decision de confiabilidad "muy confiable, no contractual". Delta A (colision nomenclatura niveles) y Delta B (aislamiento storage L0/L2) como observaciones para backlog post-E2. Derivado de sesion de pensamiento 2026-06-15 + FB-SWARM-2026-06-15.
