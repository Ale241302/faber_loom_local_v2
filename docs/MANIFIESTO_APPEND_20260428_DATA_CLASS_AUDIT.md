# MANIFIESTO_APPEND_20260428_DATA_CLASS_AUDIT
id: MANIFIESTO_APPEND_20260428_DATA_CLASS_AUDIT
type: TRANSITORIO
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
stamp: VIGENTE — 2026-04-28
expires: post-consolidación en MANIFIESTO_CAMBIOS_v2.md
aplica_a: [SHARED]

---

## Contexto

Sesión Cowork 2026-04-28 (segunda parte) tras indexa Action Engine medular. CEO planteó tres iteraciones que cambiaron material el contract:

1. **Audit del Kimi 22-abr** identificó 3 gaps reales (cross-tenant poisoning, data residency, cold start) — solo 2 críticos no cubiertos.
2. **Discusión perfil PYME** reveló que competencia real es Claude.ai/ChatGPT/Gemini, no providers chinos. Framing correcto: DPA-disponible vs no, no geográfico.
3. **Niveles de anonimato configurables** + **tiers comerciales** + **módulo de auditoría robusto** para sectores regulados (gobierno/banca/salud).

CEO `indexa hayasgos` autoriza materialización.

## Cambios ejecutados

### 1. SPEC_ACTION_ENGINE.md v1.1 → v1.2

Agregado:
- **D9 — Data Classification Routing**: hard block N3/N4 a providers sin DPA, cost-mode opt-in para N0/N1, conversation_ceiling per-sesión, PlanUpgradeRequired exception
- **D10 — Audit Module Inmutable**: hash chain, decision provenance, policy version pinning, replay capability, auditor read-only API, attestation reports
- ActionContext extendido con `data_classification`, `anonymization_level`, `conversation_ceiling`, `tenant_plan`, `addons_enabled`
- ActionResult extendido con `audit_id`, `policy_version_applied`, `classification_enforced`
- Excepciones tipadas: `PlanUpgradeRequired`, `CeilingExceeded`

10 decisiones cementadas (era 8).

### 2. POL_DATA_CLASSIFICATION.md v1.1 → v1.2

Status DRAFT → VIGENTE.

Secciones nuevas:
- **§I Routing a modelos LLM (Action Engine D9)**: tabla N0-N4 → routing + DPA + cost-mode + anonim + audit
- **§J Niveles de anonimización L0-L3**: Raw / Basic redact / LLM redact / Synthetic. Costo extra/req. De-anonim post-respuesta.
- **§K Modelo UX selector de confidencialidad**: 4 niveles visuales (🌐 💼 🔒 🛡️) mapeados a internos. Tres momentos de asignación (ingest / per-conversación / real-time ad-hoc).
- **§L Mapeo a tiers comerciales**: ceiling habilitado por plan + D9 enforcement code
- **§M Retención de audit por nivel**: hot/warm/cold con tiers temporales

### 3. SCH_ACTION_SPEC.yaml v1.0 → v1.1

Nuevo bloque `data_classification`:
- `dpa_available: bool`
- `accepts_data_class: list[N0-N4]`
- `max_anonymization_level: L0-L3`
- `requires_audit_entry: bool` (default true)

### 4. SPEC_FABERLOOM_MVP.md v1.1 → v1.2

Agregado sección "Diferenciador competitivo: Tiers de confidencialidad + Cost-mode":
- 6 diferenciadores reales vs Claude.ai/ChatGPT
- Cuadro costo blended (3 perfiles cliente: conservador/mixto/agresivo)
- Métrica MVP: % Pro/Enterprise upsell desde Starter

### 5. ENT_PLAT_ACTION_REGISTRY.md v1.0 → v1.1

Tabla LLM provider extendida con columnas DPA LATAM y accepts_data_class. Distinción crítica:
- Anthropic/OpenAI/Google: DPA ✅ → N0-N4
- DeepSeek/Kimi managed: DPA ❌ → N0-N1 con cost-mode
- Kimi K2.6 self-host: DPA propio ✅ → N0-N4 (separado como action_id distinto)

### 6. ENT_FABERLOOM_PRICING_TIERS.md v1.0 (NUEVO)

4 tiers comerciales:
- Starter $19-29 (N1)
- Pro $59-89 (N2 con add-on Confidencial)
- Enterprise $249-399 (N3 + audit full)
- Government $999-2499 custom (N4 + auditor API + 10y retention)

7 add-ons opcionales. Mapping a Action Engine D9 enforcement. Estrategia de upsell. Comparativa vs Claude.ai/ChatGPT.

### 7. SPEC_AUDIT_MODULE.md v1.0 (NUEVO)

Materialización de D10:
- AuditEntry schema completo (decision provenance + hash chain + policy pinning)
- Storage tiered (hot/warm/cold immutable con S3 Object Lock)
- Auditor read-only API con MFA + audit-of-audit
- Attestation reports por estándar (ISO 27001, SOC 2, LGPD, Ley 1581, Ley 25.326)
- Roadmap Fase 4-5 (post-MVP)
- Performance targets

## Counts post-indexa

| Métrica | Antes | Después | Delta |
|---|---|---|---|
| Total .md | 427 | 430 | +3 (PRICING_TIERS + AUDIT_MODULE + MANIFIESTO) |
| Total .yaml | 1 | 1 | 0 (SCH_ACTION_SPEC editado, no nuevo) |
| docs/ activos .md | 291 | 294 | +3 |

## Archivos modificados (resumen)

| Archivo | Versión | Tipo |
|---|---|---|
| `SPEC_ACTION_ENGINE.md` | v1.1 → v1.2 | +D9 +D10 + ActionContext/Result extendidos |
| `POL_DATA_CLASSIFICATION.md` | v1.1 → v1.2 (+VIGENTE) | +§I §J §K §L §M (5 secciones nuevas) |
| `SCH_ACTION_SPEC.yaml` | v1.0 → v1.1 | +bloque data_classification |
| `SPEC_FABERLOOM_MVP.md` | v1.1 → v1.2 | +diferenciador competitivo + costo blended |
| `ENT_PLAT_ACTION_REGISTRY.md` | v1.0 → v1.1 | +DPA LATAM + accepts_data_class por LLM |
| `ENT_FABERLOOM_PRICING_TIERS.md` | v1.0 (NUEVO) | 4 tiers + 7 add-ons + comparativa |
| `SPEC_AUDIT_MODULE.md` | v1.0 (NUEVO) | D10 materializado, roadmap Fase 4-5 |
| `MANIFIESTO_APPEND_20260428_DATA_CLASS_AUDIT.md` | v1.0 (NUEVO) | Este archivo |

## Decisiones arquitectónicas confirmadas

| Decisión | Resolución |
|---|---|
| Framing US vs China | **DPA disponible vs no**, no geográfico |
| Cost-mode | Opt-in tenant, default OFF, solo N0/N1 |
| Anonimización | Configurable L0-L3 per-tenant, ortogonal a N0-N4 |
| Tier ceiling enforcement | Hard, en Engine D9 (no en skill) |
| Audit Module | Cementado en contract API v1.0 vía audit_id en ActionResult |
| Audit implementation | Diferido a Fase 4-5 (post-MVP) |
| Tiers comerciales | 4 (Starter/Pro/Enterprise/Government) + 7 add-ons |
| Diferenciador FaberLoom | NO data residency LATAM, SÍ DPA chain + audit + tiers + cost-mode |

## NO ejecutado (pendiente)

| Pendiente | Razón |
|---|---|
| Update CLAUDE.md count 427→430 | Esta sesión, ahora |
| Update RW_ROOT counts | Próxima sesión mantenimiento |
| Update IDX_COMERCIAL con ENT_FABERLOOM_PRICING_TIERS | Próxima sesión |
| Update IDX_PLATAFORMA con SPEC_AUDIT_MODULE | Próxima sesión |
| WebSearch pricing actual abril 2026 (Haiku 4.5, Sonnet 4.6, Kimi K2.6 API) | Antes de Fase 2 sem 3 |
| Implementación real D9 (Python) | Sem 3-9 del roadmap |
| Implementación real D10 (Audit Module) | Fase 4-5 (sem 12-20) |
| Validación pricing tiers con primeros 3-10 tenants beta | MVP 60 días |

## Próxima acción CEO recomendada

```
[PLATAFORMA] Indexa data classification + pricing tiers + audit module — D9 D10 + 5 docs

- SPEC_ACTION_ENGINE v1.1 → v1.2 (+D9 Data Classification +D10 Audit Module)
- POL_DATA_CLASSIFICATION v1.1 → v1.2 VIGENTE (+5 secciones I-M)
- SCH_ACTION_SPEC.yaml v1.0 → v1.1 (+data_classification block)
- SPEC_FABERLOOM_MVP v1.1 → v1.2 (+diferenciador comercial + costo blended)
- ENT_PLAT_ACTION_REGISTRY v1.0 → v1.1 (+DPA LATAM por LLM)
- Nuevo ENT_FABERLOOM_PRICING_TIERS v1.0 (4 tiers + 7 add-ons)
- Nuevo SPEC_AUDIT_MODULE v1.0 (D10 materializado, Fase 4-5)

Origen: sesión Cowork 2026-04-28 segunda parte. Iteraciones discutidas:
audit Kimi 22-abr + framing perfil PYME + niveles anonimato configurables +
tiers comerciales + módulo auditoría sectores regulados.
```

---

Trigger: CEO `indexa hayasgos` (sesión 2026-04-28, Cowork mode).
