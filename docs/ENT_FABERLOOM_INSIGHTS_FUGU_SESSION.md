# ENT_FABERLOOM_INSIGHTS_FUGU_SESSION
id: ENT_FABERLOOM_INSIGHTS_FUGU_SESSION
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: ENT
stamp: VIGENTE — 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: ENT_FABERLOOM_INSIGHTS_KIMI_FUGU.md · SPEC_AUDIT_MODULE.md · SPEC_LLM_ROUTING_ARCHITECTURE.md

---

## FG-01 — orchestrator_policy_pool_hash para D10
**Impacta:** SPEC_AUDIT_MODULE.md
Campo nuevo: hash SHA256 de politica de pool activa cuando routing es opaco.
Tambien verificar presencia de anonymization_level.
Accion: bump SPEC_AUDIT_MODULE proximo sprint.

## FG-02 — Fugu Standard N0/N1 OK; Ultra N3/N4 NO
**Impacta:** ENT_PLAT_LLM_ROUTING.md
N0/N1: Fugu Standard OK. N2: con masking. N3/N4: solo DPA LATAM o self-hosted.
Accion: registrar en tenant_model_allowlist con restriccion data_class.

## FG-03 — 13 features L1 classifier (input Q19)
**Impacta:** SPEC_LLM_ROUTING_ARCHITECTURE.md L1
task_type_confidence, schema_parse_success, num_documents, num_counterparties,
jurisdiction_count, data_class, tenant_risk_tier, estimated_tokens,
expected_latency, business_value, validator_failure_count,
prior_case_similarity, requires_human_gate.
Accion: agregar a SPEC_LLM_ROUTING L1 proximo bump.

## FG-04 — Cost model 30 casos/semana validado
**Impacta:** ENT_FABERLOOM_PRICING_TIERS.md
80-90% deterministico $0.02-$0.20/caso. 8-18% fuerte/Standard $0.10-$0.75.
1-2% Ultra $0.20-$2+. Total realista $13-$65/mes por tenant.

## FG-05 — Compliance LATAM pendientes 9-12
**Impacta:** ENT_GOB_PENDIENTES.md
Pendientes: 9.no-training controls 10.DPA registry 11.deletion/retention 12.breach notification.
Accion: agregar a ENT_GOB_PENDIENTES track compliance.

## FG-06 — P14 validado por Fugu
Fugu textual: "Keep your P14 policy layer outside the model."
Accion: ninguna. Confirma decision existente.

---
Changelog:
- v1.0 (2026-06-24): 6 hallazgos sesion Fugu via Codex.
