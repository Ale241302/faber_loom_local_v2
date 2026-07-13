# PLAN_FB_ROADMAP_E5_E10_v1 — Roadmap maestro FaberLoom post-Agente Vivo

id: PLAN_FB_ROADMAP_E5_E10
version: 1.0.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: PLAN
stamp: VIGENTE — 2026-07-12 — roadmap maestro E5-E10, autoría del Arquitecto Ejecutor por delegación del CEO
aprobador: CEO
relacionado: PLAN_DESARROLLO_FABERLOOM_ETAPA4_v2.md · AUDIT_E4_PLAN_VS_CODIGO_20260712.md · SPEC_FB_EVOLUTION_ROADMAP_v1.md

---

## 1. Punto de partida (verificado 2026-07-12)

Etapas 1-4 cerradas en su lado codeable. La plataforma tiene: multi-tenant con Postgres+RLS y prefijos MinIO por tenant; Agente Vivo (presencia única, chat general, workspace briefs INDEX-only, planner con modos manual/shadow/natural gobernado por el ACE, orquestador multi-paso con HITL→WorkLoom, memoria CAPA 1 sobre M17, termómetro de aprendizaje); fábrica de skills (PACK 1/3 en SHADOW con harvester y tablero de readiness; olas 3-5 en DRAFT/DEFINITION_PENDING); conectores tributarios mock/sandbox/live gateados por certificado; WhatsApp bidireccional draft-first; billing manual con PDF no fiscal; signup público gated en `manual`. SCHEMA_VERSION=48; suite 724 passed / 0 failed.

## 2. Principio rector del roadmap

**Las etapas alternan CONSTRUIR y OPERAR.** E4 construyó el agente; E5 lo opera y madura hasta el primer cliente pagando. E6 abre la puerta comercial; E7 sube la autonomía con los datos de E5-E6. E8 paga la deuda técnica de plataforma; E9 abre el ecosistema; E10 escala y certifica. Ninguna etapa arranca su núcleo sin el gate de salida de la anterior — pero cada plan permite bandas paralelas explícitas para no serializar lo independiente.

## 3. Mapa de etapas

| Etapa | Nombre | Núcleo | Gate de salida (resumen) |
|---|---|---|---|
| **E5** | Madurez operativa y primer cliente | Operar shadow→natural; PACK 1/3 ACTIVE; e-factura real; design partner con soak de 30 días y factura pagada | Tenant externo ≥30d, ≥10 casos, 0 fugas, factura pagada, natural estable en ≥3 workspaces |
| **E6** | Apertura comercial self-serve | Signup auto ON, planes/pricing reales, billing recurrente, soporte operativo, branding por tenant | ≥10 tenants activos self-serve, churn de onboarding <50%, 0 incidentes P0, facturación mensual corriendo |
| **E7** | Autonomía L3 y aprendizaje organizacional | Autonomy Ladder nivel 3 interno vía ACE; CAPA 2 del learning model; eval arena | ≥2 acciones internas en L3 estables 30d; eval arena corriendo por release; CAPA 2 con comité curador activo |
| **E8** | Plataforma técnica moderna | Frontend a bundle/ES modules, realtime, desktop Electron, performance | Front migrado sin regresión funcional; realtime en tasks/chat; desktop firmado con auto-update |
| **E9** | Ecosistema e integraciones | API pública, webhooks/outbox, DMS, agentic commerce (MCP), packs 4-13 por demanda | API v1 estable con ≥2 integraciones reales de tenants; ≥3 packs adicionales ACTIVE en tenants reales |
| **E10** | Escala, resiliencia y certificación | Observabilidad, HA/DR, memoria a escala, pentest + ruta ISO, acta GA 1.0 | DR simulacro exitoso; pentest remediado; SLOs cumplidos 90d; ACTA_GA_1_0 firmada |

## 4. Bandas paralelas permitidas

- La **fábrica de skills** (definiciones de la needs-list, golden cases, promociones) corre transversal desde E5 hasta E9: nunca bloquea una etapa, siempre suma packs.
- La **deuda frontend** (E8-0) puede adelantarse a cualquier etapa si el var-hack de Babel produce un bug de producción.
- Los ítems de **seguridad recurrente** (backup smoke, rotaciones programadas, canarios) son operación permanente desde E5-2; se auditan en cada acta de etapa.

## 5. Reglas transversales (heredadas y vigentes en TODO el roadmap)

R1 cero datos inventados (`[PENDIENTE — NO INVENTAR]` para todo dato externo/de negocio; el hito que lo necesita define QUIÉN lo provee y su DoD lo exige). R2 FROZEN intocable. R3 HITL/draft-first para todo efecto externo — la Regla Sagrada del Ladder no se negocia en ninguna etapa. R4 fail-closed. R5 aislamiento tenant (RLS + Context + campos latentes de AGENTS.md en toda tabla nueva + policy en `postgres_rls_policies.sql` + canario). R6 adapter dual SQLite/Postgres (lección E4: nada de funciones SQL no portables en queries críticas). R7 suite completa 0 failed con passed estrictamente creciente, verificada AL CIERRE DE CADA HITO. R8 migraciones aditivas numeradas desde SCHEMA_VERSION real verificado al arrancar. R9 platform_admin solo agregados. R10 changelog + commit atómico por hito + `graphify update .`. R11 decisiones del planner logueadas. R12 derivados regenerables. R13 toda enmienda de spec KB se versiona con changelog, jamás se viola en silencio.

**Protocolo de ejecución con Fugu (igual que E3/E4):** una ola por orden; auditoría con evidencia por archivo al cierre de cada ola (formato AUDIT_E3_DETAILED); quien construye no audita — el diff lo revisa un agente distinto; rama por etapa (`e5-madurez`, `e6-apertura`, ...) con **merge a main + tag al cierre de cada etapa y deploy SIEMPRE desde main** (lección E4). En auditorías sobre este repo vía OneDrive: verificar contenido en disco, no confiar en mtimes.

## 6. Archivos de este roadmap

- `PLAN_DESARROLLO_FABERLOOM_ETAPA5_v1.md` — Madurez operativa y primer cliente
- `PLAN_DESARROLLO_FABERLOOM_ETAPA6_v1.md` — Apertura comercial self-serve
- `PLAN_DESARROLLO_FABERLOOM_ETAPA7_v1.md` — Autonomía L3 y aprendizaje organizacional
- `PLAN_DESARROLLO_FABERLOOM_ETAPA8_v1.md` — Plataforma técnica moderna
- `PLAN_DESARROLLO_FABERLOOM_ETAPA9_v1.md` — Ecosistema e integraciones
- `PLAN_DESARROLLO_FABERLOOM_ETAPA10_v1.md` — Escala, resiliencia y certificación

Cada plan es autocontenido: decisiones tomadas, hitos con qué/cómo/archivos/tests/DoD, riesgos P0 y gate de salida. Los planes E7-E10 incluyen una cláusula de re-validación: antes de arrancar cada uno, el Arquitecto revisa el plan contra los datos reales de la etapa anterior y emite v1.1 si hace falta — el plan no se ejecuta a ciegas dos etapas después de escrito.

## 7. Changelog

- v1.0.0 (2026-07-12): Creación. Roadmap maestro E5-E10 con gates encadenados, bandas paralelas y reglas transversales.
