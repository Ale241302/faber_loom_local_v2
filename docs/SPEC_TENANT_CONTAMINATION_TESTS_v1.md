---
id: SPEC_TENANT_CONTAMINATION_TESTS
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Plataforma (IDX_ARQUITECTURA_FUNDACIONAL)
tipo: spec
last_review: 2026-06-02
stamp: DRAFT -- 2026-06-02 -- creado en Cowork (generated_staging), pendiente promocion a canonico
aplica_a: [MWT, FaberLoom]
---

# SPEC_TENANT_CONTAMINATION_TESTS -- Suite de pruebas anti-cross-tenant

> Origen: auditoria externa 2026-06-02 (gap P1). Las reglas multi-tenant existen
> (RLS por tenant_id, tenant_model_allowlist, overrides en scope propio) pero NO hay
> una suite que intente activamente cruzar la frontera de tenant en cada superficie.
> Las fixtures Ciclope (702 assertions) validan correctitud funcional, no aislamiento.

## A. Proposito

Definir una suite de pruebas adversariales cuyo objetivo es FALLAR si un dato, memoria,
embedding, output, cache, log o tool de un tenant A puede ser alcanzado desde el contexto
de un tenant B. La suite corre en CI y como gate pre-deploy. Severidad de cualquier fuga:
critical = deploy bloqueado.

## B. Principio de diseno

Cada prueba asume mala fe: construye un escenario que INTENTA la fuga y verifica que el
sistema la impide tecnicamente (no por convencion). Toda prueba declara: superficie,
vector de ataque, resultado esperado (bloqueo), y evidencia de bloqueo.

## C. Superficies cubiertas (7)

| # | Superficie | Vector de ataque | Resultado esperado |
|---|---|---|---|
| S1 | Postgres / RLS | Query sin filtro tenant_id, o con tenant_id falsificado via payload | 0 filas de otro tenant; RLS rechaza |
| S2 | Embeddings / pgvector | Similarity search desde tenant B que deberia recuperar chunks de A | 0 hits cross-tenant; namespace por tenant aplicado |
| S3 | Memoria (Letta / memory stack) | Recall desde agente de B apuntando a memory_id de A | acceso denegado; scope por tenant en memory key |
| S4 | Output pinning | Resolver pinned_output_id de A desde request de B | no resuelve; pin scoped a tenant |
| S5 | Cache (prompt cache / idempotency) | Cache hit cruzado por prefijo identico entre tenants | cache key incluye tenant_id; no hay hit cruzado |
| S6 | Logs / audit | Lectura de AuditEntry o Token Ledger de A desde rol de B | filtrado por tenant; 0 entradas ajenas |
| S7 | Tools / actions | Invocar action con resource_id de A desde B | Action Engine rechaza; tenant mismatch |

## D. Vectores transversales obligatorios

1. **tenant_id por contexto, nunca por header de cliente.** Una prueba debe intentar
   inyectar tenant_id via header/payload y verificar que el sistema lo ignora y usa el
   contexto autenticado (regla multi-tenant inquebrantable).
2. **Default-deny.** Ausencia de tenant_id resoluble => denegar, no abrir.
3. **Overrides per-tenant no se filtran.** Config de LLM/tools/skills de A no visible a B.

## E. Estructura de la prueba (referencia)

```yaml
test_id: TC-S2-001
surface: embeddings_pgvector
attack: "tenant_B issues similarity search expecting tenant_A chunks"
setup:
  seed_tenant_A: [doc_a1, doc_a2]
  actor: tenant_B
expected:
  cross_tenant_hits: 0
  block_evidence: "namespace filter tenant_id=B applied at query"
severity: critical
```

## F. Integracion y gate

- Corre en CI (GitHub Actions) y como pre-deploy gate.
- Reusa el mock LLM deterministico de SPEC_FB_CONTRACT_TEST_HARNESS para aislar de costo/no-determinismo.
- Cualquier resultado severity:critical en falla => deploy BLOCKED (mismo criterio que el
  contract test harness FaberLoom).
- Reporte: matriz superficie x resultado, con evidencia de bloqueo por cada prueba.

## G. Relacion con otras piezas

- Extiende el modelo multi-tenant declarado en CLAUDE.md (3 reglas) y ENT_PLAT_MULTITENANT (STUB).
- Complementa SPEC_FB_CONTRACT_TEST_HARNESS (funcional) con el eje de aislamiento.
- Consume tenant_model_allowlist de ENT_PLAT_LLM_ROUTING para S7.
- Se cruza con POL_DATA_CLASSIFICATION: una fuga cross-tenant de N2+ es ademas violacion de egress.

## H. Pendientes

- L1: poblar ENT_PLAT_MULTITENANT (hoy STUB) como fuente del modelo bajo prueba -- [PENDIENTE].
- L2: definir el seed minimo de 2 tenants sinteticos para CI -- [PENDIENTE].
- L3: decidir cobertura de S5 segun si prompt cache se habilita en F1 (ver SPEC_PROMPT_CACHE_DISCIPLINE).

---

Changelog:
- v1.0 (2026-06-02): Creacion. Origen: gap P1 de auditoria externa 2026-06-02. DRAFT en
  generated_staging (mirror OneDrive), pendiente promocion a canonico via sync_*_indexa.ps1
  + append a MANIFIESTO_CAMBIOS_v2 + referencia en IDX_ARQUITECTURA_FUNDACIONAL. ASCII puro.
