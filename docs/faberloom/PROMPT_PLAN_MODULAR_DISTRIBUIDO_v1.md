# PROMPT_PLAN_MODULAR_DISTRIBUIDO_v1 -- Prompt Fugu/Kimi para Plan de Desarrollo Modular Distribuido
id: PROMPT_PLAN_MODULAR_DISTRIBUIDO_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: PROMPT
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: PLB_PROMPTING_FUGU_KIMI_v1.md - PLB_AUDIT_PATTERN_v1.md - SPEC_FB_BUILD_SEQUENCE_v3.md - PLAN_DESARROLLO_FABERLOOM_v5.md - SCH_FB_FUNCTIONAL_SPEC_v1.md

---

## Proposito

Prompt listo para copiar-pegar que le pide a Fugu Ultra (y a Kimi en paralelo) un
PLAN DE DESARROLLO MODULAR DISTRIBUIDO (contract-first) para FaberLoom E0-E3,
secuenciando las 14 fichas funcionales M07-M20.

Decisiones de diseno del prompt (alineado a la guia Fugu y a PLB_AUDIT_PATTERN):
- Estrategia Fugu: parallel execution + bring-in-specialist (uno por dominio de
  modulo) + debate-and-aggregation SOLO para particionar tracks.
- Eje rector: CONTRACT-FIRST (principio MWT: define QUE, no COMO). Cada modulo se
  construye independiente porque expone un contrato estable; los tracks
  distribuidos dependen de contratos, no de estado interno compartido.
- Estructura: SPINE serial (infra transversal) vs TRACKS paralelos.
- CoT de orquestacion al inicio (guia Fugu Sec.5.2).
- Nota: la guia Fugu es solo-Fugu; el patron dual Fugu+Kimi viene de
  PLB_AUDIT_PATTERN_v1. Para Kimi, [RUN_ID] en linea 1 + guard anti-anclaje.

Alcance asumido (decision CEO 2026-06-24): FULL SaaS multi-tenant E0-E3 (pausa
PAUSAR-Y-VALIDAR levantada para este plan). "Distribuido" = paralelizacion
contract-first (modulos construibles por agentes/equipos separados sin pisarse),
no equipos geograficos.

---

## Prompt (Fugu Ultra; mismo texto para Kimi + guard anti-anclaje)

```
[RUN_ID: {{RUN_ID, ej. PLAN-MOD-2026-06-24}}] PLAN DE DESARROLLO MODULAR DISTRIBUIDO -- FaberLoom E0-E3

--- PLAN DE ORQUESTACION (documentar ANTES de ejecutar) ---
1. Tipo de problema: planificacion de build MODULAR y DISTRIBUIDO (contract-first).
2. Descomposicion: por modulo (M07-M20) como unidad independiente con contrato.
3. Roles/especialistas que asignas por dominio de modulo.
4. Estrategia: parallel execution (construir tracks simultaneos) + bring-in-
   specialist (por dominio) + debate-and-aggregation SOLO para particionar tracks.
5. Puntos de verificacion: integridad de contratos entre modulos.
Luego ejecuta.

--- PRINCIPIO RECTOR: CONTRACT-FIRST (principio MWT: define QUE, no COMO) ---
Cada modulo se construye de forma independiente porque expone un CONTRATO estable
(inputs, outputs, eventos emitidos/consumidos, schemas, RLS, audit). Los tracks
distribuidos NO comparten estado interno; solo dependen de contratos. El plan debe
permitir que builders separados (agentes o equipos) avancen en paralelo sin pisarse.

--- CONTEXTO DEL PROYECTO (leer del repo, rutas absolutas) ---
Repo: C:\dev\mwt-knowledge-hub  | Reglas: CLAUDE.md, WIKI.md
Plantilla funcional (13 dims, ver D11 Relaciones de cada ficha = contrato):
  docs\faberloom\SCH_FB_FUNCTIONAL_SPEC_v1.md
Secuencia vigente: docs\faberloom\SPEC_FB_BUILD_SEQUENCE_v3.md
Plan previo a superseder: docs\faberloom\PLAN_DESARROLLO_FABERLOOM_v5.md
Routing 3 capas / fabrica niveles 0-4: docs\faberloom\SPEC_FB_ROUTING_PRESETS_v1.md
Foundation Beta + enmiendas (E-3/E-4/E-5): docs\faberloom\PLB_FB_FOUNDATION_BETA_v1.md
Eventing (contratos de eventos): docs\faberloom\SPEC_FB_EVENTING_AND_OUTBOX_v1.md
14 fichas (cada una con su contrato en D7 Output, D11 Relaciones, D12 Compliance):
  docs\faberloom\SPEC_FB_FUNC_M07..M20_*_v1.md
Stack: Django+Celery+PostgreSQL/RLS+Redis Streams+pgvector+MinIO+LiteLLM+Letta+
  Next.js+Electron. Anthropic-only con DPA. Aislamiento 7 capas (M16).
  Kill criteria E1: >=1 incidente privacy = kill.
No tocar FROZEN (ENT_OPS_STATE_MACHINE, PLB_ORCHESTRATOR). Dato ausente =
  [PENDIENTE -- NO INVENTAR]. No inventar esfuerzos en horas (tallas S/M/L/XL).

--- ROLES (mutuamente excluyentes) ---
ROLE A -- Module Partitioner: extrae el contrato de cada modulo, arma el DAG de
  dependencias, y particiona en TRACKS paralelizables vs el SPINE serial compartido.
ROLE B -- Platform Architect: define el SPINE (infra transversal que debe existir
  antes de forkear tracks: aislamiento M16, auth/sesion M08, eventing/outbox M15,
  audit M12, policy gate M11); valida que los contratos permiten construir en
  paralelo sin acoplar estado interno.
ROLE C -- Specialist per dominio: asigna especialista por track (RLS/multi-tenant,
  ML classifier, HITL/UX, Electron/desktop, eventing) e identifica integration
  risk + tests de contrato entre tracks.

--- PROCESO ---
Fase 1 (debate-and-aggregation): genera 2-3 particiones de tracks independientes
  y agrega la mejor.
Fase 2 (parallel): por cada track, detalla modulos, contrato, can-start-when,
  criterios de aceptacion, tests.
Fase 3 (specialist + verificacion): integration points y contract tests entre
  tracks; valida que el SPINE habilita el paralelismo declarado.

--- OBJETIVO: PLAN_DESARROLLO_FABERLOOM_v6 (modular distribuido, supersede v5) ---
1. SPINE serial: infra transversal que bloquea todo (orden minimo obligatorio).
2. TRACKS paralelos: grupos de modulos construibles en simultaneo tras el spine,
   cada uno con su especialista, contrato, y can-start-when.
3. Registro de contratos modulo->modulo (que expone / que consume cada uno).
4. DAG de dependencias (que bloquea a que; que es paralelizable).
5. Integration points + contract tests entre tracks (incl. 5 tests cross-tenant
   de M16 antes de abrir cualquier track).
6. Riesgos P0/P1 (foco: integration risk del paralelismo) + kill criteria.
7. Pendientes-CEO que bloquean cada track. Contradicciones KB (id+version, no resolver).

--- FORMATO DE SALIDA ---
Markdown. Bloque SPINE + un bloque por TRACK {modulos / contrato / can-start-when /
aceptacion / tests / especialista / riesgo}. Cerrar con SINTESIS CRUZADA: el spine
en una linea, los tracks paralelos posibles, top 5 integration risks, y confianza
(ALTA/MEDIA/BAJA) por track.
```

---

## Spine y tracks sugeridos (hipotesis de arranque; Fugu/Kimi lo validan)

SPINE serial (debe existir antes de forkear): M16 (aislamiento/RLS) -> M08
(auth/sesion) -> M15 (outbox/eventing) -> M12/M11 (audit + policy gate).
TRACKS paralelos sobre el spine:
- Track Action Engine: M10 (classifier) -> M13 (HITL) -> M14 (outcome ledger).
- Track Tenant/RBAC: M07 (bootstrap wizard) + M09 (RBAC).
- Track Memoria: M17 (Letta).
- Track Desktop: M18 (auth Electron) -> M19 (offline sync) -> M20 (auto-update).

---

Changelog:
- v1.0 (2026-06-24): Creacion. Prompt para plan de desarrollo modular distribuido
  contract-first (Fugu Ultra + Kimi). Estrategia parallel + specialist; spine vs
  tracks; CoT de orquestacion. Alineado a la guia Fugu y a PLB_AUDIT_PATTERN_v1.
