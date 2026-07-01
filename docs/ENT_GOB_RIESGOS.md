# ENT_GOB_RIESGOS — Registro de Riesgos
id: ENT_GOB_RIESGOS
version: 2.0
domain: Gobernanza (IDX_GOBERNANZA)
status: VIGENTE
visibility: [INTERNAL]
stamp: VIGENTE — aprobado 2026-03-15
iso: 9001:2015 §6.1, 45001:2018 §6.1, 27001:2022 §6.1
aplica_a: [MWT]

---

## A. Propósito

Registro único de riesgos de MWT. Cubre las tres dimensiones ISO: calidad (9001), seguridad ocupacional (45001) y seguridad de la información (27001). Cada riesgo se evalúa con la misma metodología para facilitar priorización cruzada.

Principio: un riesgo, un registro. Si un riesgo afecta múltiples dimensiones, se documenta una vez con tags de todas las ISOs aplicables.

---

## B. Metodología de evaluación

Escala Probabilidad (P): 1 = Improbable, 2 = Posible, 3 = Probable, 4 = Casi seguro.
Escala Impacto (I): 1 = Menor, 2 = Moderado, 3 = Mayor, 4 = Crítico.
Score = P × I. Máximo 16.

| Score | Nivel | Acción |
|-------|-------|--------|
| 1–4 | BAJO | Aceptar. Monitorear en revisión trimestral. |
| 5–8 | MEDIO | Mitigar. Definir control y responsable. |
| 9–12 | ALTO | Mitigar con prioridad. Escalar a CEO si no hay control definido. |
| 13–16 | CRÍTICO | Acción inmediata. CEO decide. No operar sin mitigación. |

---

## C. Registro — Riesgos de Calidad (ISO 9001)

| ID | Riesgo | P | I | Score | Control existente | Acción adicional |
|----|--------|---|---|-------|------------------|-----------------|
| R-Q01 | Error en cálculo de pricing genera pérdida en expediente | 3 | 4 | 12 ALTO | Doble vista costos (ENT_OPS_EXPEDIENTE.C1), validación manual CEO | ENT_GOB_KPI: medir % expedientes con corrección de costo post-aprobación |
| R-Q02 | Proforma con datos incorrectos enviada a cliente | 2 | 3 | 6 MEDIO | Flujo CEO review antes de envío (PLB_REGISTRO_PROFORMA), consecutivo controlado | Ninguna adicional — control es suficiente |
| R-Q03 | Clasificación NCM errónea genera exposición legal | 2 | 4 | 8 MEDIO | Verificación con Alejandra (customs analyst) | Documentar protocolo de validación NCM como checklist |
| R-Q04 | Expediente supera 90 días de crédito sin cobrar | 3 | 3 | 9 ALTO | Reloj crédito 90d con alerta P10 (ENT_OPS_EXPEDIENTE.C4), bloqueo día 75 | Control automático en sistema — monitorear efectividad |
| R-Q05 | Claim no aprobado por Compliance aparece en material público | 2 | 3 | 6 MEDIO | POL_CLAIMS_SCANNER claim check, POL_STAMP, ENT_COMP_CONTENT_RULES.A | Ninguna adicional |

---

## D. Registro — Riesgos SSO (ISO 45001)

| ID | Riesgo | P | I | Score | Control existente | Acción adicional |
|----|--------|---|---|-------|------------------|-----------------|
| R-S01 | Riesgo ergonómico trabajo remoto (postura, pantalla, jornada) | 3 | 2 | 6 MEDIO | — | Guía ergonomía básica para equipo remoto |
| R-S02 | Lesión por manipulación de cajas en recepción de mercancía | 2 | 2 | 4 BAJO | Volúmenes bajos, carga no excesiva | Registrar si hay incidente |
| R-S03 | Exposición a riesgos en visitas a plantas industriales de clientes | 2 | 3 | 6 MEDIO | — | Protocolo: usar EPP del cliente en visitas a planta |
| R-S04 | Uso incorrecto del scanner por vendedor (tropiezo con mat/cable) | 2 | 1 | 2 BAJO | Diseño: antideslizante, cable ≥1.5m, peso <2.5kg | Incluir en manual de uso |

---

## E. Registro — Riesgos de Seguridad de la Información (ISO 27001)

| ID | Riesgo | P | I | Score | Control existente | Acción adicional |
|----|--------|---|---|-------|------------------|-----------------|
| R-I01 | Acceso no autorizado a datos CEO-ONLY (costos, márgenes) | 2 | 4 | 8 MEDIO | POL_VISIBILIDAD, roles ENT_PLAT_SEGURIDAD | Auditar acceso trimestralmente (PLB_AUDIT_ISO) |
| R-I02 | Breach de datos biométricos del scanner | 1 | 4 | 4 BAJO (pre-scanner) | — | Cifrado E2E + hash integridad (ENT_PLAT_SCANNER_SECURITY) |
| R-I03 | Distribuidor A accede a datos de Distribuidor B | 2 | 4 | 8 MEDIO (con scanner) | — | Row-level security + tenant_id (ENT_PLAT_MULTITENANT) |
| R-I04 | Pérdida de datos por fallo del servidor | 2 | 4 | 8 MEDIO | Backup weekly Hostinger | Backup diario para datos biométricos. Probar restore. |
| R-I05 | Scanner robado o perdido con datos locales | 2 | 3 | 6 MEDIO | — | Política no-cache local: scanner no almacena escaneos. Todo va al servidor. |
| R-I06 | Secrets o API keys expuestas en repositorio | 2 | 4 | 8 MEDIO | Secrets via .env, nunca en docker-compose (ENT_PLAT_INFRA) | Scan automatizado de secrets en CI/CD |
| R-I07 | Empleado o agente IA accede fuera de su scope | 2 | 3 | 6 MEDIO | PLB_ORCHESTRATOR §C (scope por agente), aprobación CEO | Logging de acceso (ENT_PLAT_OBSERVABILIDAD) |

---

## F. Revisión

Este registro se revisa en cada revisión por la dirección (ref → PLB_REVISION_DIRECCION). Riesgos nuevos se agregan cuando se identifican. Scores se actualizan cuando cambian controles o contexto.

Cuando un riesgo se materializa → se registra como incidente en PLB_ACCION_CORRECTIVA y se evalúa si el score debe subir.

---

## G. Riesgos estratégicos — borrador para evaluación CEO

| ID | Riesgo | Dimensión ISO | P (1-4) | I (1-4) | Score | Nivel | Control propuesto |
|----|--------|---------------|---------|---------|-------|-------|-------------------|
| R-S01 | Dependencia de proveedor único (Marluvas) | 9001 | 3 | 3 | 9 | ALTO | Calificar ≥1 proveedor alternativo PORON XRD (Dongguan Hengyi/KOLON) + stock 60 días. Score residual con control: 4 (Bajo) |
| R-S02 | 16 policies bootstrap vencen simultáneamente 2026-05-30 | 9001 | 2 | 3 | 6 | MEDIO | Renovar + escalonar vencimientos. Score residual: 2 (Bajo) |
| R-S03 | Concentración en canal único (Amazon USA) — 22-35% tasa suspensión | 9001 | 3 | 4 | 12 | ALTO | Auditoría Account Health + Brand Registry + docs compliance Marluvas. Score residual: 6 (Medio) |
| R-S04 | CEO como punto único de fallo operativo | 45001 | 2 | 4 | 8 | MEDIO | LLC USA + poder notarial + sobre de emergencia con accesos. Score residual: 4 (Bajo) |
| R-S05 | KB sin backup automatizado (216 archivos .md) | 27001 | 3 | 3 | 9 | ALTO | GitHub privado (fuente de verdad) + cron git pull cada 5min en servidor + Nginx auth para Perplexity + MinIO backup diario. Esfuerzo: 3-4h Ale. Score residual: 3 (Bajo). Spec: DeepSeek Prompt 6 |
| R-S06 | Vencimiento de policies sin proceso activo de renovación | 9001 | 2 | 2 | 4 | BAJO | Calendario de gobernanza + alertas 90/30/7 días. Score residual: 2 (Bajo) |

> Nota: P×I evaluados por Perplexity (Auditor) con datos de mercado verificados — fuentes en INVESTIGACIONES_PERPLEXITY_GAPS_CEO.pdf §1. Controles propuestos priorizados: R-S03 y R-S05 inmediato, R-S02 antes mayo 2026, R-S01 90 días, R-S04 120 días, R-S06 30 días.

---

Stamp: DRAFT — Pendiente aprobación CEO
