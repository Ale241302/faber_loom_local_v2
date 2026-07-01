# ENT_PLAT_MULTITENANT - Aislamiento Multi-tenant
id: ENT_PLAT_MULTITENANT
status: VIGENTE
visibility: [INTERNAL]
version: 1.0
domain: Plataforma (IDX_PLATAFORMA)
stamp: VIGENTE -- 2026-06-12 -- deja de ser STUB; consolida invariantes dispersos (era el vacio ALTA del eje 6 de AUDIT_KB_2026-06-09)
aplica_a: [SHARED]

---

## A. Proposito

Entidad canonica del aislamiento multi-tenant. Consolida los invariantes que estaban
dispersos en CLAUDE.md, WIKI seccion 7 y SPECs FB. Un agente que rutee aqui encuentra
la regla, no un placeholder.

## B. Los 5 invariantes (NUNCA romper)

1. Toda query incluye filtro `tenant_id`. Sin excepcion.
2. `tenant_id` NOT NULL en toda tabla aislable.
3. RLS policies son source of truth (no app-layer enforcement solo).
4. Tenant context fluye via Context (Go) o middleware (Python). NUNCA via header del cliente.
5. Overrides per-tenant (LLM config, tools, skills enabled) viven en scope tenant; no se filtran cross-tenant.

## C. Extension 2026: el lente de workspace (segundo nivel de scope)

Ademas del tenant, los items operativos llevan `workspace_id` y el acceso se media
por membresia (`workspace_members`). El scope del lente se aplica server-side
(RLS o WHERE), nunca solo en UI. Detalle: SCH_FB_CORE_TABLES_v1.

## D. Punteros canonicos (corrige los rotos de WIKI seccion 7)

| Tema | Doc real |
|---|---|
| Privacidad por capas de knowledge | docs/faberloom/POL_FB_KR_PRIVACY_TIERS_v1.md |
| Auth + RBAC por tenant | docs/faberloom/SPEC_FB_AUTH_TENANT_RBAC_v1.md (roles E1: 2, per PLB E-4) |
| Tests de contaminacion cross-tenant | docs/SPEC_TENANT_CONTAMINATION_TESTS_v1.md |
| Bootstrap de tenant | docs/faberloom/SPEC_FB_TENANT_BOOTSTRAP_SEED_v1.md |
| Envelope de providers por tenant | docs/faberloom/SPEC_FB_ROUTING_PRESETS_v1.md (capa preset, solo Owner) |
| Schemas fisicos con tenant_id + workspace_id | docs/faberloom/SCH_FB_CORE_TABLES_v1.md |

Nota: WIKI.md linea ~145 apunta a paths inexistentes (docs/SPEC_FB_MULTI_TENANT_*).
WIKI es control_surface: su correccion requiere break-glass CEO. Mientras tanto este
ENT es el destino correcto.

## E. Multi-tenant real en el roadmap

Se gana con el segundo inquilino (Fase 5 / E3 condicional a gate E2.5). En E1-E2:
single-tenant con RLS y workspace_id desde el dia 1 (barato ahora, carisimo despues),
contamination test con tenant seed #2 como fitness de F1.

---

Changelog:
- v1.0 (2026-06-12): Deja de ser STUB. Consolida 5 invariantes (de WIKI seccion 7) +
  lente de workspace + tabla de punteros canonicos (corrige refs rotas detectadas en
  AUDIT_KB_2026-06-09 eje 4). No introduce reglas nuevas: consolida y referencia.
- v0.1 (2026-03-14): header normalizado + status: STUB (Ola A).
