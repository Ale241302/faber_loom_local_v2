# Auditoría de capacidades del curador — Vista Skills (E5-0)

**Fecha de ejecución:** 2026-07-13T19:12:23.833015+00:00
**DB engine:** inferred from env
**SCHEMA_VERSION:** 48
**Estado general:** ⚠️ HAY HALLAZGOS

## Resumen ejecutivo

- Archivos `faberloom/SKILL_*.md` revisados: **79**
- Skills en DB (`skill_manifest`) por estado: `{}`
- Permiso `canManageSkills` incluye `curator`: **SÍ**

## Hallazgos automáticos

| Severidad | Categoría | Hallazgo | URL |
|-----------|-----------|----------|-----|
| P2 | skill_manifest | app/faberloom/SKILL_AMAZON_OPS.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_AMAZON_OPS.md |
| P1 | skill_manifest | app/faberloom/SKILL_BO_DEVOLUCION_NC.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_BO_DEVOLUCION_NC.md |
| P1 | skill_manifest | app/faberloom/SKILL_BO_DEVOLUCION_NC.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_BO_DEVOLUCION_NC.md |
| P1 | skill_manifest | app/faberloom/SKILL_BO_DEVOLUCION_NC.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_BO_DEVOLUCION_NC.md |
| P2 | skill_manifest | app/faberloom/SKILL_BO_DEVOLUCION_NC.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_BO_DEVOLUCION_NC.md |
| P1 | skill_manifest | app/faberloom/SKILL_BO_RECEPCION_MATCH.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_BO_RECEPCION_MATCH.md |
| P1 | skill_manifest | app/faberloom/SKILL_BO_RECEPCION_MATCH.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_BO_RECEPCION_MATCH.md |
| P1 | skill_manifest | app/faberloom/SKILL_BO_RECEPCION_MATCH.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_BO_RECEPCION_MATCH.md |
| P2 | skill_manifest | app/faberloom/SKILL_BO_RECEPCION_MATCH.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_BO_RECEPCION_MATCH.md |
| P1 | skill_manifest | app/faberloom/SKILL_BO_STOCK_DISPONIBLE.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_BO_STOCK_DISPONIBLE.md |
| P1 | skill_manifest | app/faberloom/SKILL_BO_STOCK_DISPONIBLE.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_BO_STOCK_DISPONIBLE.md |
| P1 | skill_manifest | app/faberloom/SKILL_BO_STOCK_DISPONIBLE.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_BO_STOCK_DISPONIBLE.md |
| P2 | skill_manifest | app/faberloom/SKILL_BO_STOCK_DISPONIBLE.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_BO_STOCK_DISPONIBLE.md |
| P2 | skill_manifest | app/faberloom/SKILL_CLIENT_SERVICE.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CLIENT_SERVICE.md |
| P1 | skill_manifest | app/faberloom/SKILL_CM_ACCOUNT_BRIEF.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CM_ACCOUNT_BRIEF.md |
| P1 | skill_manifest | app/faberloom/SKILL_CM_ACCOUNT_BRIEF.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CM_ACCOUNT_BRIEF.md |
| P1 | skill_manifest | app/faberloom/SKILL_CM_ACCOUNT_BRIEF.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CM_ACCOUNT_BRIEF.md |
| P2 | skill_manifest | app/faberloom/SKILL_CM_ACCOUNT_BRIEF.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CM_ACCOUNT_BRIEF.md |
| P1 | skill_manifest | app/faberloom/SKILL_CM_CALL_CAPTURE.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CM_CALL_CAPTURE.md |
| P1 | skill_manifest | app/faberloom/SKILL_CM_CALL_CAPTURE.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CM_CALL_CAPTURE.md |
| P1 | skill_manifest | app/faberloom/SKILL_CM_CALL_CAPTURE.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CM_CALL_CAPTURE.md |
| P2 | skill_manifest | app/faberloom/SKILL_CM_CALL_CAPTURE.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CM_CALL_CAPTURE.md |
| P1 | skill_manifest | app/faberloom/SKILL_CM_CARTERA_PRIORITIZE.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CM_CARTERA_PRIORITIZE.md |
| P1 | skill_manifest | app/faberloom/SKILL_CM_CARTERA_PRIORITIZE.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CM_CARTERA_PRIORITIZE.md |
| P1 | skill_manifest | app/faberloom/SKILL_CM_CARTERA_PRIORITIZE.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CM_CARTERA_PRIORITIZE.md |
| P2 | skill_manifest | app/faberloom/SKILL_CM_CARTERA_PRIORITIZE.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CM_CARTERA_PRIORITIZE.md |
| P1 | skill_manifest | app/faberloom/SKILL_CM_REORDER_PREDICT.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CM_REORDER_PREDICT.md |
| P1 | skill_manifest | app/faberloom/SKILL_CM_REORDER_PREDICT.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CM_REORDER_PREDICT.md |
| P1 | skill_manifest | app/faberloom/SKILL_CM_REORDER_PREDICT.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CM_REORDER_PREDICT.md |
| P2 | skill_manifest | app/faberloom/SKILL_CM_REORDER_PREDICT.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CM_REORDER_PREDICT.md |
| P2 | skill_manifest | app/faberloom/SKILL_COMPLIANCE_CHECKER.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_COMPLIANCE_CHECKER.md |
| P2 | skill_manifest | app/faberloom/SKILL_COPY.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_COPY.md |
| P1 | skill_manifest | app/faberloom/SKILL_CO_CARTERA_X_FE.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CO_CARTERA_X_FE.md |
| P1 | skill_manifest | app/faberloom/SKILL_CO_CASH_PROJECTION.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CO_CASH_PROJECTION.md |
| P1 | skill_manifest | app/faberloom/SKILL_CO_DUNNING_FE.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CO_DUNNING_FE.md |
| P1 | skill_manifest | app/faberloom/SKILL_CO_PAYMENT_MATCH_FE.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CO_PAYMENT_MATCH_FE.md |
| P1 | skill_manifest | app/faberloom/SKILL_CO_PROMESA_PAGO.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CO_PROMESA_PAGO.md |
| P1 | skill_manifest | app/faberloom/SKILL_CO_SECUENCIA.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CO_SECUENCIA.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_DISPUTE_PACK.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_DISPUTE_PACK.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_DISPUTE_PACK.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_DISPUTE_PACK.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_DISPUTE_PACK.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_DISPUTE_PACK.md |
| P2 | skill_manifest | app/faberloom/SKILL_CX_DISPUTE_PACK.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_DISPUTE_PACK.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_DOC_COMPLETENESS.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_DOC_COMPLETENESS.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_DOC_COMPLETENESS.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_DOC_COMPLETENESS.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_DOC_COMPLETENESS.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_DOC_COMPLETENESS.md |
| P2 | skill_manifest | app/faberloom/SKILL_CX_DOC_COMPLETENESS.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_DOC_COMPLETENESS.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_DUTY_CALC.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_DUTY_CALC.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_DUTY_CALC.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_DUTY_CALC.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_DUTY_CALC.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_DUTY_CALC.md |
| P2 | skill_manifest | app/faberloom/SKILL_CX_DUTY_CALC.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_DUTY_CALC.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_EMBARQUE_TRACK.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_EMBARQUE_TRACK.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_EMBARQUE_TRACK.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_EMBARQUE_TRACK.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_EMBARQUE_TRACK.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_EMBARQUE_TRACK.md |
| P2 | skill_manifest | app/faberloom/SKILL_CX_EMBARQUE_TRACK.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_EMBARQUE_TRACK.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_HS_CLASSIFY.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_HS_CLASSIFY.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_HS_CLASSIFY.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_HS_CLASSIFY.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_HS_CLASSIFY.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_HS_CLASSIFY.md |
| P2 | skill_manifest | app/faberloom/SKILL_CX_HS_CLASSIFY.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_HS_CLASSIFY.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_LANDED_COST.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_LANDED_COST.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_LANDED_COST.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_LANDED_COST.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_LANDED_COST.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_LANDED_COST.md |
| P2 | skill_manifest | app/faberloom/SKILL_CX_LANDED_COST.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_LANDED_COST.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_ORIGIN_CHECK.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_ORIGIN_CHECK.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_ORIGIN_CHECK.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_ORIGIN_CHECK.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_ORIGIN_CHECK.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_ORIGIN_CHECK.md |
| P2 | skill_manifest | app/faberloom/SKILL_CX_ORIGIN_CHECK.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_ORIGIN_CHECK.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_PEDIMENTO_CROSSCHECK.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_PEDIMENTO_CROSSCHECK.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_PEDIMENTO_CROSSCHECK.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_PEDIMENTO_CROSSCHECK.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_PEDIMENTO_CROSSCHECK.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_PEDIMENTO_CROSSCHECK.md |
| P2 | skill_manifest | app/faberloom/SKILL_CX_PEDIMENTO_CROSSCHECK.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_PEDIMENTO_CROSSCHECK.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_REG_WATCH.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_REG_WATCH.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_REG_WATCH.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_REG_WATCH.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_REG_WATCH.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_REG_WATCH.md |
| P2 | skill_manifest | app/faberloom/SKILL_CX_REG_WATCH.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_REG_WATCH.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_REQUISITOS_PREVIOS.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_REQUISITOS_PREVIOS.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_REQUISITOS_PREVIOS.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_REQUISITOS_PREVIOS.md |
| P1 | skill_manifest | app/faberloom/SKILL_CX_REQUISITOS_PREVIOS.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_REQUISITOS_PREVIOS.md |
| P2 | skill_manifest | app/faberloom/SKILL_CX_REQUISITOS_PREVIOS.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_CX_REQUISITOS_PREVIOS.md |
| P2 | skill_manifest | app/faberloom/SKILL_DEMAND_FORECASTER.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_DEMAND_FORECASTER.md |
| P2 | skill_manifest | app/faberloom/SKILL_EXPERIMENT_RUNNER.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_EXPERIMENT_RUNNER.md |
| P1 | skill_manifest | app/faberloom/SKILL_FE_CABYS_VALIDATE.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FE_CABYS_VALIDATE.md |
| P1 | skill_manifest | app/faberloom/SKILL_FE_COMPLEMENTO_PAGO.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FE_COMPLEMENTO_PAGO.md |
| P1 | skill_manifest | app/faberloom/SKILL_FE_NOTA_CD_LINK.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FE_NOTA_CD_LINK.md |
| P1 | skill_manifest | app/faberloom/SKILL_FE_RECEPTOR_RECONCILE.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FE_RECEPTOR_RECONCILE.md |
| P1 | skill_manifest | app/faberloom/SKILL_FE_REJECT_FIX.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FE_REJECT_FIX.md |
| P1 | skill_manifest | app/faberloom/SKILL_FE_RESEND.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FE_RESEND.md |
| P1 | skill_manifest | app/faberloom/SKILL_FE_RETENCION_MATCH.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FE_RETENCION_MATCH.md |
| P1 | skill_manifest | app/faberloom/SKILL_FE_STATUS_CHECK.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FE_STATUS_CHECK.md |
| P1 | skill_manifest | app/faberloom/SKILL_FI_ASIENTOS.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FI_ASIENTOS.md |
| P1 | skill_manifest | app/faberloom/SKILL_FI_ASIENTOS.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FI_ASIENTOS.md |
| P1 | skill_manifest | app/faberloom/SKILL_FI_ASIENTOS.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FI_ASIENTOS.md |
| P2 | skill_manifest | app/faberloom/SKILL_FI_ASIENTOS.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FI_ASIENTOS.md |
| P1 | skill_manifest | app/faberloom/SKILL_FI_CIERRE_NARRADO.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FI_CIERRE_NARRADO.md |
| P1 | skill_manifest | app/faberloom/SKILL_FI_CIERRE_NARRADO.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FI_CIERRE_NARRADO.md |
| P1 | skill_manifest | app/faberloom/SKILL_FI_CIERRE_NARRADO.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FI_CIERRE_NARRADO.md |
| P2 | skill_manifest | app/faberloom/SKILL_FI_CIERRE_NARRADO.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FI_CIERRE_NARRADO.md |
| P1 | skill_manifest | app/faberloom/SKILL_FI_EEFF.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FI_EEFF.md |
| P1 | skill_manifest | app/faberloom/SKILL_FI_EEFF.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FI_EEFF.md |
| P1 | skill_manifest | app/faberloom/SKILL_FI_EEFF.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FI_EEFF.md |
| P2 | skill_manifest | app/faberloom/SKILL_FI_EEFF.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FI_EEFF.md |
| P1 | skill_manifest | app/faberloom/SKILL_FI_VARIACIONES.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FI_VARIACIONES.md |
| P1 | skill_manifest | app/faberloom/SKILL_FI_VARIACIONES.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FI_VARIACIONES.md |
| P1 | skill_manifest | app/faberloom/SKILL_FI_VARIACIONES.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FI_VARIACIONES.md |
| P2 | skill_manifest | app/faberloom/SKILL_FI_VARIACIONES.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FI_VARIACIONES.md |
| P1 | skill_manifest | app/faberloom/SKILL_FRONTEND_TEN_PRINCIPLES_V2.md: No se pudo parsear el frontmatter YAML | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_FRONTEND_TEN_PRINCIPLES_V2.md |
| P1 | skill_manifest | app/faberloom/SKILL_GE_BRIEF_RECURRENTE.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_GE_BRIEF_RECURRENTE.md |
| P1 | skill_manifest | app/faberloom/SKILL_GE_BRIEF_RECURRENTE.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_GE_BRIEF_RECURRENTE.md |
| P1 | skill_manifest | app/faberloom/SKILL_GE_BRIEF_RECURRENTE.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_GE_BRIEF_RECURRENTE.md |
| P2 | skill_manifest | app/faberloom/SKILL_GE_BRIEF_RECURRENTE.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_GE_BRIEF_RECURRENTE.md |
| P1 | skill_manifest | app/faberloom/SKILL_GE_PULSO.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_GE_PULSO.md |
| P1 | skill_manifest | app/faberloom/SKILL_GE_PULSO.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_GE_PULSO.md |
| P1 | skill_manifest | app/faberloom/SKILL_GE_PULSO.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_GE_PULSO.md |
| P2 | skill_manifest | app/faberloom/SKILL_GE_PULSO.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_GE_PULSO.md |
| P1 | skill_manifest | app/faberloom/SKILL_GE_QBR.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_GE_QBR.md |
| P1 | skill_manifest | app/faberloom/SKILL_GE_QBR.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_GE_QBR.md |
| P1 | skill_manifest | app/faberloom/SKILL_GE_QBR.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_GE_QBR.md |
| P2 | skill_manifest | app/faberloom/SKILL_GE_QBR.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_GE_QBR.md |
| P1 | skill_manifest | app/faberloom/SKILL_GE_RIESGOS.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_GE_RIESGOS.md |
| P1 | skill_manifest | app/faberloom/SKILL_GE_RIESGOS.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_GE_RIESGOS.md |
| P1 | skill_manifest | app/faberloom/SKILL_GE_RIESGOS.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_GE_RIESGOS.md |
| P2 | skill_manifest | app/faberloom/SKILL_GE_RIESGOS.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_GE_RIESGOS.md |
| P1 | skill_manifest | app/faberloom/SKILL_HR_CONTRATACION.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_HR_CONTRATACION.md |
| P1 | skill_manifest | app/faberloom/SKILL_HR_CONTRATACION.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_HR_CONTRATACION.md |
| P1 | skill_manifest | app/faberloom/SKILL_HR_CONTRATACION.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_HR_CONTRATACION.md |
| P2 | skill_manifest | app/faberloom/SKILL_HR_CONTRATACION.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_HR_CONTRATACION.md |
| P2 | skill_manifest | app/faberloom/SKILL_HUMANIZE_BRAND.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_HUMANIZE_BRAND.md |
| P2 | skill_manifest | app/faberloom/SKILL_HUMANIZE_COMMS.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_HUMANIZE_COMMS.md |
| P2 | skill_manifest | app/faberloom/SKILL_KB_AUDITOR.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_KB_AUDITOR.md |
| P2 | skill_manifest | app/faberloom/SKILL_KB_GATEWAY.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_KB_GATEWAY.md |
| P1 | skill_manifest | app/faberloom/SKILL_LG_CONTRATO_REVIEW.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_LG_CONTRATO_REVIEW.md |
| P1 | skill_manifest | app/faberloom/SKILL_LG_CONTRATO_REVIEW.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_LG_CONTRATO_REVIEW.md |
| P1 | skill_manifest | app/faberloom/SKILL_LG_CONTRATO_REVIEW.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_LG_CONTRATO_REVIEW.md |
| P2 | skill_manifest | app/faberloom/SKILL_LG_CONTRATO_REVIEW.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_LG_CONTRATO_REVIEW.md |
| P1 | skill_manifest | app/faberloom/SKILL_LG_NDA_TRIAGE.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_LG_NDA_TRIAGE.md |
| P1 | skill_manifest | app/faberloom/SKILL_LG_NDA_TRIAGE.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_LG_NDA_TRIAGE.md |
| P1 | skill_manifest | app/faberloom/SKILL_LG_NDA_TRIAGE.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_LG_NDA_TRIAGE.md |
| P2 | skill_manifest | app/faberloom/SKILL_LG_NDA_TRIAGE.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_LG_NDA_TRIAGE.md |
| P1 | skill_manifest | app/faberloom/SKILL_LG_PREFIRMA.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_LG_PREFIRMA.md |
| P1 | skill_manifest | app/faberloom/SKILL_LG_PREFIRMA.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_LG_PREFIRMA.md |
| P1 | skill_manifest | app/faberloom/SKILL_LG_PREFIRMA.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_LG_PREFIRMA.md |
| P2 | skill_manifest | app/faberloom/SKILL_LG_PREFIRMA.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_LG_PREFIRMA.md |
| P1 | skill_manifest | app/faberloom/SKILL_LG_VENCIMIENTOS.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_LG_VENCIMIENTOS.md |
| P1 | skill_manifest | app/faberloom/SKILL_LG_VENCIMIENTOS.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_LG_VENCIMIENTOS.md |
| P1 | skill_manifest | app/faberloom/SKILL_LG_VENCIMIENTOS.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_LG_VENCIMIENTOS.md |
| P2 | skill_manifest | app/faberloom/SKILL_LG_VENCIMIENTOS.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_LG_VENCIMIENTOS.md |
| P1 | skill_manifest | app/faberloom/SKILL_LG_VIGENCIA_NORMA.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_LG_VIGENCIA_NORMA.md |
| P1 | skill_manifest | app/faberloom/SKILL_LG_VIGENCIA_NORMA.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_LG_VIGENCIA_NORMA.md |
| P1 | skill_manifest | app/faberloom/SKILL_LG_VIGENCIA_NORMA.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_LG_VIGENCIA_NORMA.md |
| P2 | skill_manifest | app/faberloom/SKILL_LG_VIGENCIA_NORMA.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_LG_VIGENCIA_NORMA.md |
| P1 | skill_manifest | app/faberloom/SKILL_MK_BRAND_AUDIT.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_MK_BRAND_AUDIT.md |
| P1 | skill_manifest | app/faberloom/SKILL_MK_BRAND_AUDIT.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_MK_BRAND_AUDIT.md |
| P1 | skill_manifest | app/faberloom/SKILL_MK_BRAND_AUDIT.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_MK_BRAND_AUDIT.md |
| P2 | skill_manifest | app/faberloom/SKILL_MK_BRAND_AUDIT.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_MK_BRAND_AUDIT.md |
| P1 | skill_manifest | app/faberloom/SKILL_MK_CAMPANA.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_MK_CAMPANA.md |
| P1 | skill_manifest | app/faberloom/SKILL_MK_CAMPANA.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_MK_CAMPANA.md |
| P1 | skill_manifest | app/faberloom/SKILL_MK_CAMPANA.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_MK_CAMPANA.md |
| P2 | skill_manifest | app/faberloom/SKILL_MK_CAMPANA.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_MK_CAMPANA.md |
| P1 | skill_manifest | app/faberloom/SKILL_MK_CONTENIDO_VOZ.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_MK_CONTENIDO_VOZ.md |
| P1 | skill_manifest | app/faberloom/SKILL_MK_CONTENIDO_VOZ.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_MK_CONTENIDO_VOZ.md |
| P1 | skill_manifest | app/faberloom/SKILL_MK_CONTENIDO_VOZ.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_MK_CONTENIDO_VOZ.md |
| P2 | skill_manifest | app/faberloom/SKILL_MK_CONTENIDO_VOZ.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_MK_CONTENIDO_VOZ.md |
| P1 | skill_manifest | app/faberloom/SKILL_OP_PROVEEDOR_EVAL.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_OP_PROVEEDOR_EVAL.md |
| P1 | skill_manifest | app/faberloom/SKILL_OP_PROVEEDOR_EVAL.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_OP_PROVEEDOR_EVAL.md |
| P1 | skill_manifest | app/faberloom/SKILL_OP_PROVEEDOR_EVAL.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_OP_PROVEEDOR_EVAL.md |
| P2 | skill_manifest | app/faberloom/SKILL_OP_PROVEEDOR_EVAL.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_OP_PROVEEDOR_EVAL.md |
| P1 | skill_manifest | app/faberloom/SKILL_OP_SOP.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_OP_SOP.md |
| P1 | skill_manifest | app/faberloom/SKILL_OP_SOP.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_OP_SOP.md |
| P1 | skill_manifest | app/faberloom/SKILL_OP_SOP.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_OP_SOP.md |
| P2 | skill_manifest | app/faberloom/SKILL_OP_SOP.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_OP_SOP.md |
| P1 | skill_manifest | app/faberloom/SKILL_OP_STATUS.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_OP_STATUS.md |
| P1 | skill_manifest | app/faberloom/SKILL_OP_STATUS.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_OP_STATUS.md |
| P1 | skill_manifest | app/faberloom/SKILL_OP_STATUS.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_OP_STATUS.md |
| P2 | skill_manifest | app/faberloom/SKILL_OP_STATUS.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_OP_STATUS.md |
| P1 | skill_manifest | app/faberloom/SKILL_PL_CARGAS_VALIDATE.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_PL_CARGAS_VALIDATE.md |
| P1 | skill_manifest | app/faberloom/SKILL_PL_CARGAS_VALIDATE.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_PL_CARGAS_VALIDATE.md |
| P1 | skill_manifest | app/faberloom/SKILL_PL_CARGAS_VALIDATE.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_PL_CARGAS_VALIDATE.md |
| P2 | skill_manifest | app/faberloom/SKILL_PL_CARGAS_VALIDATE.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_PL_CARGAS_VALIDATE.md |
| P1 | skill_manifest | app/faberloom/SKILL_PL_PREP.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_PL_PREP.md |
| P1 | skill_manifest | app/faberloom/SKILL_PL_PREP.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_PL_PREP.md |
| P1 | skill_manifest | app/faberloom/SKILL_PL_PREP.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_PL_PREP.md |
| P2 | skill_manifest | app/faberloom/SKILL_PL_PREP.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_PL_PREP.md |
| P1 | skill_manifest | app/faberloom/SKILL_PL_RECTIFICACION.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_PL_RECTIFICACION.md |
| P1 | skill_manifest | app/faberloom/SKILL_PL_RECTIFICACION.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_PL_RECTIFICACION.md |
| P1 | skill_manifest | app/faberloom/SKILL_PL_RECTIFICACION.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_PL_RECTIFICACION.md |
| P2 | skill_manifest | app/faberloom/SKILL_PL_RECTIFICACION.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_PL_RECTIFICACION.md |
| P2 | skill_manifest | app/faberloom/SKILL_PROFORMA_BUILDER.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_PROFORMA_BUILDER.md |
| P1 | skill_manifest | app/faberloom/SKILL_SV_ESCALACION.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_SV_ESCALACION.md |
| P1 | skill_manifest | app/faberloom/SKILL_SV_ESCALACION.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_SV_ESCALACION.md |
| P1 | skill_manifest | app/faberloom/SKILL_SV_ESCALACION.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_SV_ESCALACION.md |
| P2 | skill_manifest | app/faberloom/SKILL_SV_ESCALACION.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_SV_ESCALACION.md |
| P1 | skill_manifest | app/faberloom/SKILL_SV_GARANTIA_DEVOLUCION.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_SV_GARANTIA_DEVOLUCION.md |
| P1 | skill_manifest | app/faberloom/SKILL_SV_GARANTIA_DEVOLUCION.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_SV_GARANTIA_DEVOLUCION.md |
| P1 | skill_manifest | app/faberloom/SKILL_SV_GARANTIA_DEVOLUCION.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_SV_GARANTIA_DEVOLUCION.md |
| P2 | skill_manifest | app/faberloom/SKILL_SV_GARANTIA_DEVOLUCION.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_SV_GARANTIA_DEVOLUCION.md |
| P1 | skill_manifest | app/faberloom/SKILL_SV_RESPUESTA.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_SV_RESPUESTA.md |
| P1 | skill_manifest | app/faberloom/SKILL_SV_RESPUESTA.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_SV_RESPUESTA.md |
| P1 | skill_manifest | app/faberloom/SKILL_SV_RESPUESTA.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_SV_RESPUESTA.md |
| P2 | skill_manifest | app/faberloom/SKILL_SV_RESPUESTA.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_SV_RESPUESTA.md |
| P1 | skill_manifest | app/faberloom/SKILL_SV_TEMAS.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_SV_TEMAS.md |
| P1 | skill_manifest | app/faberloom/SKILL_SV_TEMAS.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_SV_TEMAS.md |
| P1 | skill_manifest | app/faberloom/SKILL_SV_TEMAS.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_SV_TEMAS.md |
| P2 | skill_manifest | app/faberloom/SKILL_SV_TEMAS.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_SV_TEMAS.md |
| P1 | skill_manifest | app/faberloom/SKILL_SV_TRIAGE.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_SV_TRIAGE.md |
| P1 | skill_manifest | app/faberloom/SKILL_SV_TRIAGE.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_SV_TRIAGE.md |
| P1 | skill_manifest | app/faberloom/SKILL_SV_TRIAGE.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_SV_TRIAGE.md |
| P2 | skill_manifest | app/faberloom/SKILL_SV_TRIAGE.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_SV_TRIAGE.md |
| P1 | skill_manifest | app/faberloom/SKILL_TR_DECLARACION_INFO.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_TR_DECLARACION_INFO.md |
| P1 | skill_manifest | app/faberloom/SKILL_TR_DECLARACION_INFO.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_TR_DECLARACION_INFO.md |
| P1 | skill_manifest | app/faberloom/SKILL_TR_DECLARACION_INFO.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_TR_DECLARACION_INFO.md |
| P2 | skill_manifest | app/faberloom/SKILL_TR_DECLARACION_INFO.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_TR_DECLARACION_INFO.md |
| P1 | skill_manifest | app/faberloom/SKILL_TR_PERMISOS_CAL.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_TR_PERMISOS_CAL.md |
| P1 | skill_manifest | app/faberloom/SKILL_TR_PERMISOS_CAL.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_TR_PERMISOS_CAL.md |
| P1 | skill_manifest | app/faberloom/SKILL_TR_PERMISOS_CAL.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_TR_PERMISOS_CAL.md |
| P2 | skill_manifest | app/faberloom/SKILL_TR_PERMISOS_CAL.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_TR_PERMISOS_CAL.md |
| P1 | skill_manifest | app/faberloom/SKILL_TR_RETENCION_CERT.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_TR_RETENCION_CERT.md |
| P1 | skill_manifest | app/faberloom/SKILL_TR_RETENCION_CERT.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_TR_RETENCION_CERT.md |
| P1 | skill_manifest | app/faberloom/SKILL_TR_RETENCION_CERT.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_TR_RETENCION_CERT.md |
| P2 | skill_manifest | app/faberloom/SKILL_TR_RETENCION_CERT.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_TR_RETENCION_CERT.md |
| P1 | skill_manifest | app/faberloom/SKILL_TR_TIPO_CAMBIO_ADJ.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_TR_TIPO_CAMBIO_ADJ.md |
| P1 | skill_manifest | app/faberloom/SKILL_TR_TIPO_CAMBIO_ADJ.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_TR_TIPO_CAMBIO_ADJ.md |
| P1 | skill_manifest | app/faberloom/SKILL_TR_TIPO_CAMBIO_ADJ.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_TR_TIPO_CAMBIO_ADJ.md |
| P2 | skill_manifest | app/faberloom/SKILL_TR_TIPO_CAMBIO_ADJ.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_TR_TIPO_CAMBIO_ADJ.md |
| P1 | skill_manifest | app/faberloom/SKILL_TR_TRAMITE_TRACK.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_TR_TRAMITE_TRACK.md |
| P1 | skill_manifest | app/faberloom/SKILL_TR_TRAMITE_TRACK.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_TR_TRAMITE_TRACK.md |
| P1 | skill_manifest | app/faberloom/SKILL_TR_TRAMITE_TRACK.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_TR_TRAMITE_TRACK.md |
| P2 | skill_manifest | app/faberloom/SKILL_TR_TRAMITE_TRACK.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_TR_TRAMITE_TRACK.md |
| P1 | skill_manifest | app/faberloom/SKILL_WA_AGREEMENT_CAPTURE.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_WA_AGREEMENT_CAPTURE.md |
| P1 | skill_manifest | app/faberloom/SKILL_WA_AGREEMENT_CAPTURE.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_WA_AGREEMENT_CAPTURE.md |
| P1 | skill_manifest | app/faberloom/SKILL_WA_AGREEMENT_CAPTURE.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_WA_AGREEMENT_CAPTURE.md |
| P2 | skill_manifest | app/faberloom/SKILL_WA_AGREEMENT_CAPTURE.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_WA_AGREEMENT_CAPTURE.md |
| P1 | skill_manifest | app/faberloom/SKILL_WA_CLASSIFY_ROUTE.md: status no permitido: draft | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_WA_CLASSIFY_ROUTE.md |
| P1 | skill_manifest | app/faberloom/SKILL_WA_CLASSIFY_ROUTE.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_WA_CLASSIFY_ROUTE.md |
| P1 | skill_manifest | app/faberloom/SKILL_WA_CLASSIFY_ROUTE.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_WA_CLASSIFY_ROUTE.md |
| P2 | skill_manifest | app/faberloom/SKILL_WA_CLASSIFY_ROUTE.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_WA_CLASSIFY_ROUTE.md |
| P1 | skill_manifest | app/faberloom/SKILL_WA_ORDER_CAPTURE.md: status no permitido: definition_pending | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_WA_ORDER_CAPTURE.md |
| P1 | skill_manifest | app/faberloom/SKILL_WA_ORDER_CAPTURE.md: kill_switch.enabled no es true | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_WA_ORDER_CAPTURE.md |
| P1 | skill_manifest | app/faberloom/SKILL_WA_ORDER_CAPTURE.md: learning_consolidation.auto_apply no es false | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_WA_ORDER_CAPTURE.md |
| P2 | skill_manifest | app/faberloom/SKILL_WA_ORDER_CAPTURE.md: contiene placeholders [PENDIENTE — NO INVENTAR] | https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_WA_ORDER_CAPTURE.md |

## Requiere ojo humano (≤5 ítems)

1. [REQUIERE OJO HUMANO] skill_manifest — app/faberloom/SKILL_AMAZON_OPS.md: contiene placeholders [PENDIENTE — NO INVENTAR]
   - URL: https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_AMAZON_OPS.md
2. [REQUIERE OJO HUMANO] skill_manifest — app/faberloom/SKILL_BO_DEVOLUCION_NC.md: status no permitido: definition_pending
   - URL: https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_BO_DEVOLUCION_NC.md
3. [REQUIERE OJO HUMANO] skill_manifest — app/faberloom/SKILL_BO_DEVOLUCION_NC.md: kill_switch.enabled no es true
   - URL: https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_BO_DEVOLUCION_NC.md
4. [REQUIERE OJO HUMANO] skill_manifest — app/faberloom/SKILL_BO_DEVOLUCION_NC.md: learning_consolidation.auto_apply no es false
   - URL: https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_BO_DEVOLUCION_NC.md
5. [REQUIERE OJO HUMANO] skill_manifest — app/faberloom/SKILL_BO_DEVOLUCION_NC.md: contiene placeholders [PENDIENTE — NO INVENTAR]
   - URL: https://github.com/Ale241302/faber_loom_local_v2/blob/main/app/faberloom/SKILL_BO_DEVOLUCION_NC.md

## Snippet de permisos

```js
"const canManageSkills = [\"owner\", \"curator\", \"admin\"].includes(userRole) || isPlatformAdmin(user);"
```
