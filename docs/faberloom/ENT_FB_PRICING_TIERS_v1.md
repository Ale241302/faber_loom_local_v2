# ENT_FABERLOOM_PRICING_TIERS — Estructura de tiers comerciales
id: ENT_FB_PRICING_TIERS_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (IDX_FB_FOUNDATION_BETA)
type: ENT
stamp: VIGENTE — 2026-04-28
aprobador: CEO (delegado al Arquitecto Cowork)
aplica_a: [FaberLoom]
relacionado: SPEC_FABERLOOM_MVP.md · POL_DATA_CLASSIFICATION.md · SPEC_ACTION_ENGINE.md (D9, D10) · SPEC_AUDIT_MODULE.md

---

## Declaración

FaberLoom monetiza el nivel de confidencialidad y el módulo de auditoría como diferenciadores comerciales. Cuatro planes con add-ons que desbloquean clases de data superiores y features de compliance.

**Modelo de cobro: suscripción base + add-ons desbloqueables.** Cap por add-on para evitar overage surprises.

---

## Estructura de tiers

| Plan | Precio sugerido (USD/mes) | Ceiling habilitado | Modelos | Anonim | Audit |
|---|---|---|---|---|---|
| **Starter** | $19-29 | N1 (Trabajo) | cualquier modelo + DPA | L1 | básico (1 año retención) |
| **Pro** | $59-89 | N2 (con add-on Confidencial) | US/EU con DPA | L2 | detallado (5 años) |
| **Enterprise** | $249-399 | N3 (Distribuidor-scoped) | US/EU + RLS estricto | L2/L3 configurable | full (7 años) |
| **Government** | $999-2499 (custom) | N4 (Privado, audit completo) | US/EU exclusivo | L3 obligatoria | full + auditor API + 10 años retención |

---

## Add-ons opcionales

| Add-on | Precio sugerido | Desbloquea |
|---|---|---|
| Confidencial Add-on | $30/mes (sobre Starter) | N2 hasta 500 msg/mes ($0.05 c/msg adicional) |
| Audit Pro | $50/mes | Compliance attestation reports + retention extendida |
| Compliance Pack LATAM | $100/mes | DPA chain documentada + reportes regulatorios LGPD/Ley 1581/Ley 25.326 |
| Multi-region Storage | $150/mes (Enterprise+) | Storage en us/eu/latam con BYO encryption keys |
| Auditor API Access | $200/mes (Enterprise+) | Endpoint read-only para auditores externos con MFA |
| SLA 99.9% | $200/mes (Enterprise+) | Soporte 24/7 + uptime guarantee |
| SLA 99.95% + onboarding compliance officer | included en Government | — |

---

## Mapeo a Action Engine D9 enforcement

```python
# Pseudo-código del enforcement en el Engine
def get_tenant_ceiling(tenant_plan: str, addons: list[str]) -> str:
    base = {
        "starter": "N1",
        "pro": "N1",  # default sin addon
        "enterprise": "N3",
        "government": "N4",
    }[tenant_plan]

    if "confidencial_addon" in addons and tenant_plan in ("starter", "pro"):
        return "N2"
    if tenant_plan == "pro":
        return "N1"  # default

    return base

def enforce_d9(ctx: ActionContext) -> None:
    ceiling = get_tenant_ceiling(ctx.tenant_plan, ctx.addons_enabled)
    if ctx.data_classification > ceiling:
        raise PlanUpgradeRequired(suggested_addon=suggest_addon(ctx))
```

---

## Estrategia de upsell

```
Starter ($29) — entry-level, cubre 80% de casos PYME
   ↓ trigger: cliente toca data PII o necesita compliance
Pro ($79) — añade Confidencial, target 30% de Starter conversion
   ↓ trigger: cliente regulado o multi-tenant complejo
Enterprise ($299) — añade audit + RLS estricto + multi-region
   ↓ trigger: gobierno, banca, salud, ONG con donantes
Government (custom) — onboarding manual, contratos B2G/Enterprise

Métrica MVP target:
  - 60% Starter (PYMEs estándar)
  - 25% Pro (con Confidencial add-on)
  - 12% Enterprise
  - 3% Government
```

---

## Comparativa vs competencia directa

| Capacidad | Claude.ai Pro $20/mes | ChatGPT Plus $20/mes | FaberLoom Starter $29 | FaberLoom Pro $79 |
|---|---|---|---|---|
| Multi-modelo orquestado | ❌ | ❌ | ✅ | ✅ |
| Memoria cross-sesión per-cliente | ⚠️ Projects | ⚠️ Memory | ✅ Gold samples | ✅ + OutcomeLedger |
| Tiers de confidencialidad | ❌ | ❌ | ✅ N0-N1 | ✅ N0-N2 |
| Audit log inmutable | ❌ | ❌ | ⚠️ Básico | ✅ Detallado |
| DPA chain consolidada | ❌ | ❌ | ✅ | ✅ |
| Workflow B2B (cobranza/proformas) | ❌ | ❌ | ✅ | ✅ |
| Cost-mode opt-in | ❌ | ❌ | ✅ | ✅ |

---

## Limitaciones v1.0

| Limitación | Mitigación |
|---|---|
| Pricing propuesto sin validación de mercado | A/B test en MVP 60 días con primeros 3-10 tenants beta |
| Add-ons granulares pueden generar fricción | Templates de bundle "Compliance Pack" simplifican decisión |
| Government tier requiere contratos custom | Manual durante MVP, automatizar v2 cuando haya 5+ Government clients |
| Costo blended depende de cost-mode adoption | Default seguro (cost-mode OFF), opt-in con educación al usuario |

---

Changelog:
- 2026-06-15 (AUDIT-ROUTING-2026-06-14): Renombrado desde docs/ENT_FABERLOOM_PRICING_TIERS.md a docs/faberloom/ENT_FB_PRICING_TIERS_v1.md. id y domain actualizados. v1.0 se mantiene.
- v1.0 (2026-04-28): Creación. 4 tiers (Starter/Pro/Enterprise/Government) + 7 add-ons. Mapping a Action Engine D9. Comparativa vs Claude.ai/ChatGPT. Origen: indexa hallazgos data classification + pricing tiers + audit module.
