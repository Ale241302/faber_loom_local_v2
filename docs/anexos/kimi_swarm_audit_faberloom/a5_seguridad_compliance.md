# Auditoría de Seguridad y Compliance — FaberLoom

**Rol:** Agente 5 — Arquitecto de Seguridad y Compliance  
**Fecha:** 2026-06-24  
**Objetivo:** Evaluar si FaberLoom puede venderse hoy a clientes regulados (banca, gobierno, salud / hospitales) en LATAM sin incurrir en afirmaciones engañosas de compliance.  
**Alcance:** Repositorio canónico `C:\dev\mwt-knowledge-hub\` (documentos de diseño, mockups, hooks/tests de KB). No se audita código de producción porque, tras búsqueda en el repo y en el sistema de archivos, **no se encontró backend/frontend ejecutable de FaberLoom**. La auditoría contrasta las especificaciones y planes contra la implementación real disponible.  
**Limitación:** Esta auditoría es técnica y documental; no constituye asesoría legal. Las referencias a LGPD, LFPDPPP, Ley 1581, Ley 8968 y otras normas se basan en los documentos del Knowledge Hub y deben validarse con abogado local antes de cualquier contrato.

---

## 1. Resumen ejecutivo

| # | Componente auditado | ¿Cumple? | Estado |
|---|----------------------|----------|--------|
| 1 | Clasificación de datos N0-N4 y etiquetado | **Parcial / solo en diseño** | Especificado en `POL_DATA_CLASSIFICATION v1.4`; sin implementación probada. |
| 2 | Hard block D9 (routing por data class y DPA) | **Parcial / solo en diseño** | Especificado en `SPEC_ACTION_ENGINE D9` y `POL_DATA_CLASSIFICATION §I`; sin Engine implementado. |
| 3 | D10 audit trail inmutable | **No** | `SPEC_AUDIT_MODULE v1.1` detalla schema; implementación efectiva post-MVP (Fase 4-5). |
| 4 | Aislamiento multi-tenant (RLS) | **No** | `SPEC_FB_AUTH_TENANT_RBAC_v1` exige RLS; el plan vigente prioriza desktop single-user (`PLAN_DESARROLLO_FABERLOOM_v5 §2.2`). |
| 5 | ModelFingerprint / contención de modelos | **Parcial / solo en diseño** | `ARCH_AGENT_PRINCIPLES P13` + `POL_DATA_CLASSIFICATION §I`; no hay implementación. |
| 6 | Gold sample pipeline y privacidad cross-tenant | **Parcial / solo en diseño** | `POL_FB_KR_PRIVACY_TIERS_v1.1` define 7 checks; sin automatización ni comité operativo. |
| 7 | Cadena DPA y registro de subprocesadores | **No** | Reglas definidas; `CEO-39` (P1) pendiente: DPAs firmados y subprocessor registry. |
| 8 | Voice profile y LGPD/LFPDPPP (biometría/voz) | **Parcial / atenuado** | E1 se reduce a bloque de estilo textual; voz grabada/transcripción diferida. Riesgo residual si se agrega sin tratar como N4. |
| 9 | Export / portabilidad de auditoría | **No** | Mencionado en trazabilidad y `SPEC_AUDIT_MODULE`; sin endpoints implementados. |
| 10 | Procedimiento de notificación de brechas | **No** | `CEO-41` (P2) pendiente; solo referencia de 72h a ANPD en `ENT_COMP_REGULATORIO.md B3`. |

**Veredicto general:** FaberLoom **NO está listo para venderse a bancos, gobiernos u hospitales** en su estado actual. La arquitectura de seguridad y compliance está razonablemente diseñada en papel, pero los controles técnicos, los contratos (DPA), el audit trail inmutable, el aislamiento multi-tenant y los procedimientos de incidentes no están implementados ni documentados operativamente.

---

## 2. Metodología y alcance

1. Se leyeron los documentos canónicos de FaberLoom y plataforma referidos a seguridad, privacidad, clasificación, routing, audit, multi-tenant, voz y gobernanza.  
2. Se buscó código de producción (backend, frontend, tests de seguridad ejecutables) en el repo y en rutas comunes del sistema; solo se encontraron: mockups HTML, documentación markdown, fixtures de contract-tests, scripts de auditoría del KB y tests de hooks de KB.  
3. Se contrastó cada control de diseño contra: (a) existencia del documento, (b) estado de aprobación, (c) plan de implementación, (d) evidencia de implementación.  
4. Se clasificaron los hallazgos en P0 (bloqueante venta regulada), P1 (riesgo alto, debe cerrarse antes de beta enterprise) y P2 (mejora/deuda).

---

## 3. Análisis por componente

### 3.1 Clasificación de datos N0-N4 y etiquetado

**1. ¿Cumple?** Parcial — solo en diseño.  
**2. Evidencia:** `POL_DATA_CLASSIFICATION v1.4` define niveles N0-N4, metadata obligatoria (`classification`, `owner`, `retention_policy`, etc.), PII scanner pre-ingestión con hard block si detecta N2+ en docs `[PUBLIC]`, y selector UX por sesión (`§K`). `PLAN_DESARROLLO_FABERLOOM_v5 §E0.5b` incluye una matriz data_class/provider, pero su estado al cierre de esta auditoría es de tareas por hacer. No hay código ni dataset golden validado.  
**3. Riesgo:** Sin scanner probado, un documento con RUT/NIT/CNPJ/RFC/CUIT, precios o datos de salud puede indexarse como N0/N1 y filtrarse a modelos sin DPA. Eso viola LGPD art. 46, LFPDPPP y Ley 1581.  
**4. Recomendación:** Implementar el pipeline regex+LLM judge (`POL_DATA_CLASSIFICATION §K`), validar contra ≥500 documentos LATAM por vertical con accuracy ≥92%, y bloquear ingestión por defecto hasta clasificación válida. No prometer procesamiento de N2+ hasta tener pruebas.

### 3.2 Hard block D9 (routing por data class y DPA)

**1. ¿Cumple?** Parcial — solo en diseño.  
**2. Evidencia:** `SPEC_ACTION_ENGINE D9` y `POL_DATA_CLASSIFICATION §I` establecen el hard block: N3/N4 solo a providers US/EU con DPA firmado, sin override CEO; cost-mode OFF por defecto; `PlanUpgradeRequired` si la class supera el ceiling del plan. `ENT_PLAT_ACTION_REGISTRY v1.1` lista DPA por provider (Anthropic/OpenAI/Google ✅; DeepSeek/Kimi managed ❌). Sin embargo, el Action Engine es un contrato API; la implementación real está en roadmap semana 3-9. `PLAN_DESARROLLO_FABERLOOM_v5 §E1a-Base` habla de un `PolicyGate` propio, pero no se encontró código.  
**3. Riesgo:** Sin enforcement centralizado, cada skill podría rutear datos N3/N4 a DeepSeek/Kimi managed, generando transferencia transfronteriza sin DPA y multas en Brasil/Colombia/México.  
**4. Recomendación:** Codificar `PolicyGate` fail-closed antes de cualquier llamada a LiteLLM; tests unitarios/matriciales por combinación `(data_class, provider, tenant_plan, addon)`; registrar todo bypass con razón; no habilitar cost-mode hasta tener DPA registry operativo.

### 3.3 D10 audit trail inmutable

**1. ¿Cumple?** No.  
**2. Evidencia:** `SPEC_AUDIT_MODULE v1.1` define `AuditEntry`, hash chain, storage tiers (hot/warm/cold), auditor read-only API, attestation reports ISO/SOC2/LGPD/Ley 1581. `SPEC_ACTION_ENGINE D10` cementa el contrato. El roadmap señala implementación efectiva en **Fase 4-5 (post-MVP)**. `PLAN_DESARROLLO_FABERLOOM_v5 §E1a-Base` menciona solo “audit log append-only (metadata only)”.  
**3. Riesgo:** Sin audit trail inmutable no se puede demostrar qué modelo vio qué dato, ni reproducir decisiones, ni entregar reportes firmados a reguladores. Es feature contractual de Enterprise/Government (`SPEC_AUDIT_MODULE §Lo que NO es`).  
**4. Recomendación:** Priorizar Fase 4: schema + hash chain + storage separado con S3 Object Lock/Azure Immutable Blob; endpoints read-only con MFA; templates de attestation aprobados por DPO/abogado.

### 3.4 Aislamiento multi-tenant (RLS)

**1. ¿Cumple?** No.  
**2. Evidencia:** `SPEC_FB_AUTH_TENANT_RBAC_v1 §3.2` exige Postgres RLS en todas las tablas tenant-scoped, headers `x-tenant-id`, `x-actor-role`, etc. Sin embargo, `PLAN_DESARROLLO_FABERLOOM_v5 §2.2` prioriza **desktop single-user local-first con SQLite** (sin multi-tenant ni RLS), y el despliegue web/server queda condicional a E2.5. No se encontró backend multi-tenant.  
**3. Riesgo:** Para un banco/gobierno/hospital el modelo deseado es SaaS multi-tenant con aislamiento estricto. Vender la versión desktop como solución “segura” no resuelve el control de acceso interno ni la separación de datos entre unidades/ clientes. Además, el plan de dualidad deja pendiente la prueba de aislamiento por tabla.  
**4. Recomendación:** Para tiers Enterprise/Government usar exclusivamente el despliegue server con PostgreSQL 16 + RLS + `FORCE ROW LEVEL SECURITY` + tests de aislamiento automatizados por tabla. Documentar y probar headers obligatorios desde el primer request.

### 3.5 ModelFingerprint / contención de modelos

**1. ¿Cumple?** Parcial — solo en diseño.  
**2. Evidencia:** `ARCH_AGENT_PRINCIPLES P13` define `ModelFingerprint` y probation al cambiar provider/version. `POL_DATA_CLASSIFICATION §I` conecta el routing con P13. `SPEC_ACTION_ENGINE` menciona capability drift detection en semana 10+. No se encontró implementación.  
**3. Riesgo:** Cambiar de Sonnet 4.6 a 4.7 o de OpenAI a Anthropic sin revalidación puede degradar calidad o romper controles de anonimización/formato, afectando outputs cliente-facing.  
**4. Recomendación:** Implementar fingerprint + probation antes de permitir cambios de modelo/version en producción; vincularlo al `ActionResult` y a `AuditEntry`.

### 3.6 Gold sample pipeline y privacidad cross-tenant

**1. ¿Cumple?** Parcial — solo en diseño.  
**2. Evidencia:** `POL_FB_KR_PRIVACY_TIERS_v1.1` define 4 tiers (PRIVATE_RAW, TENANT_DERIVED, GLOBAL_PROMOTABLE, RESTRICTED_SENSITIVE_OR_REGULATED) y 7 checks obligatorios para promover TENANT_DERIVED → GLOBAL_PROMOTABLE (privacy review, reidentification test, l-diversity, secret-commercial review, lineage, consent/contract, purpose compatibility). `SPEC_FB_RAG_SECURITY_FIREWALL_v1` añade `P11_SECURITY_PRECHECK` antes de promover aprendizajes. En Foundation Beta E1 la composición jerárquica y el pool L3 cross-tenant están bloqueados (`SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1`), por lo que el riesgo está atenuado, pero la automatización de los 7 checks no existe.  
**3. Riesgo:** Cuando se habilite E2/E3, un comité mal instrumentado o un bug en los checks puede llevar secretos comerciales o datos personales al pool global.  
**4. Recomendación:** Codificar los 7 checks como gates obligatorios (CI + revisión humana) antes de cualquier promoción cross-tenant; no activar el pool global hasta tener aprobación legal y auditoría externa.

### 3.7 Cadena DPA y registro de subprocesadores

**1. ¿Cumple?** No.  
**2. Evidencia:** `POL_DATA_CLASSIFICATION §I` define DPA reconocido y 6 condiciones vinculantes para procesar N4 (sede legal, región de cómputo, DPA firmado, subprocesadores declarados, no-retention, auditoría). `ENT_PLAT_ACTION_REGISTRY v1.1` indica DPA por provider. `ENT_GOB_PENDIENTES.md §CEO-39` lista como pendiente P1: “Registro formal de DPAs firmados por provider con data_class permitida y region.” El anexo `D3_Base_Legal_Datos_B2B.md` advierte que se requiere validación con abogado local en cada jurisdicción. No se encontró evidencia de DPAs firmados.  
**3. Riesgo:** Sin DPA firmado no se puede legalmente procesar N3/N4 con proveedores US/EU. Brasil (LGPD) requiere SCCs ANPD; Colombia requiere CCM de la RIPD o autorización expresa. Vender “DPA chain consolidada” sin DPAs firmados es una afirmación engañosa.  
**4. Recomendación:** Crear DPA-as-code registry (`ENT_GOB_ENGINEERING_COMPETENCIES C10`), firmar DPA con Anthropic/OpenAI/Google, documentar subprocesadores, configurar ZDR (`CEO-38`) y alertas a 90 días de vencimiento.

### 3.8 Voice profile y LGPD/LFPDPPP (biometría/voz)

**1. ¿Cumple?** Parcial / riesgo atenuado en E1.  
**2. Evidencia:** `SCH_FB_VOICE_PROFILE_v1` define el schema del “sabor del user”, con `privacy_tier` default `PRIVATE_RAW` (nunca cross-tenant) y opción `TENANT_DERIVED` con opt-in explícito (E2+). `SPEC_FB_VOICE_HUMANIZER_v2.1` colapsa el alcance E1-E2 a: bloque de estilo por tenant + few-shots de gold samples + filtros post-generación; la resolución property-by-property y el aprendizaje HITL de voz quedan diferidos a E3+. `ENT_COMP_REGULATORIO.md B3` trata como dato sensible el escaneo de presión plantar, no la voz en E1.  
**3. Riesgo:** Aunque E1 no procesa voz grabada, el nombre “Voice Profile” puede generar expectativas de biometría. Si en E2/E3 se agrega transcripción de llamadas o TTS de voz real sin consentimiento explícito y tratamiento N4, se incumple LGPD/LFPDPPP.  
**4. Recomendación:** Mantener E1 como perfil de estilo textual sin grabación; si se añade voz real, tratar como N4, requerir consentimiento explícito, DPA, zero-retention, no entrenamiento, y notificación de breach en 72h.

### 3.9 Export / portabilidad de auditoría

**1. ¿Cumple?** No.  
**2. Evidencia:** `SPEC_AUDIT_MODULE §4` define endpoints de auditoría y attestation reports. `AUDIT_FABERLOOM_TRAZABILIDAD_V3_v1.md` incluye C16 “Data portability per user (LGPD)” con UI “Mis datos” + JSON download + audit `user.data_exported`. `AUDIT_FABERLOOM_A7_CHAT_CONTRADICTIONS_v1.md` señala que faltaba mecanismo de export user-level. No se encontró implementación.  
**3. Riesgo:** LGPD art. 18 y equivalentes otorgan derecho de portabilidad. No poder exportar datos del usuario/tenant en formato estructurado es incumplimiento directo.  
**4. Recomendación:** Implementar endpoints de export por usuario y por tenant (JSON/PDF firmado), incluyendo inputs, outputs, audit entries y voice profile; registrar evento `user.data_exported`; validar con dataset de prueba.

### 3.10 Procedimiento de notificación de brechas

**1. ¿Cumple?** No.  
**2. Evidencia:** `ENT_GOB_PENDIENTES.md §CEO-41` (P2) dice: “Procedimiento de notificación ante brechas. Plazo LGPD: 72h a ANPD. Equivalente en CO/MX/CR pendiente de verificación con abogado.” `ENT_COMP_REGULATORIO.md B3` repite la obligación de 72h a ANPD y referencia `PLB_INCIDENT_RESPONSE.B4`, pero no se encontró dicho documento. No hay RACI, contactos ni simulacros.  
**3. Riesgo:** Incumplimiento de LGPD art. 46 y art. 33 (notificación), LFPDPPP y Ley 1581; multas, daño reputacional y responsabilidad civil.  
**4. Recomendación:** Redactar `PLB_INCIDENT_RESPONSE` con: definición de breach personal, tiempos por jurisdicción (ANPD 72h, SIC, AAIP, PRODHAB), RACI, canales de notificación, simulacro trimestral y integración con D10 para evidencia.

---

## 4. Pregunta crítica adicional

### ¿Puede venderse hoy FaberLoom a un banco, gobierno u hospital sin engaño?

**Respuesta: NO.**

Fundamentos:

1. **No existe producto ejecutable de producción.** El repositorio contiene especificaciones, mockups navegables y tests de hooks del KB, pero no un backend/frontend que implemente los controles auditados.  
2. **Los controles de seguridad y compliance son de diseño, no de runtime.** Ninguno de los hard blocks (D9), el audit trail inmutable (D10), el RLS multi-tenant, el PII scanner ni el DPA registry está implementado y probado.  
3. **Faltan contratos y procedimientos legales operativos.** `CEO-39` (DPA/subprocessor registry) y `CEO-41` (breach notification) están pendientes. Sin ellos no se puede sostener ante un regulador que se cumplen LGPD, LFPDPPP o Ley 1581.  
4. **El plan de desarrollo vigente prioriza desktop single-user.** Ese despliegue no satisface los requisitos de aislamiento, auditoría externa y gobernanza que exigen banca, gobierno y salud.  
5. **La RAG Security Firewall está aprobada en diseño pero no en runtime.** `SPEC_FB_RAG_SECURITY_FIREWALL_v1` exige 26 fixtures red-team, simulacros Competitor Poisoned RFQ e Insider Poisoned Approval Drill, y `stale_scan_exposure_count=0` antes de promocionar a `P0_APPROVED`. Ninguno de esos gates se cumplió.

Vender FaberLoom hoy a un cliente regulado requeriría afirmar capacidades técnicas y legales que no existen. Eso expone a MWT a demandas, rescisiones de contrato, multas regulatorias y daño reputacional irreversible.

---

## 5. Hallazgos priorizados

### P0 — Bloqueantes para venta regulada (no negociables)

| # | Hallazgo | Origen / evidencia |
|---|----------|-------------------|
| P0.1 | No hay backend/frontend de producción implementado. | Solo KB, mockups, hooks/tests y fixtures en `C:\dev\mwt-knowledge-hub\`. |
| P0.2 | D10 audit trail inmutable no implementado. | `SPEC_AUDIT_MODULE v1.1` roadmap Fase 4-5 post-MVP. |
| P0.3 | Cadena DPA no firmada ni registrada. | `ENT_GOB_PENDIENTES.md §CEO-39`. |
| P0.4 | Aislamiento multi-tenant con RLS no implementado; arquitectura actual es desktop single-user. | `SPEC_FB_AUTH_TENANT_RBAC_v1 §3.2` vs `PLAN_DESARROLLO_FABERLOOM_v5 §2.2`. |
| P0.5 | Procedimiento de notificación de brechas no existe. | `ENT_GOB_PENDIENTES.md §CEO-41`. |
| P0.6 | RAG Security Firewall no alcanzó runtime approval. | `SPEC_FB_RAG_SECURITY_FIREWALL_v1` `runtime_approval_requires`. |

### P1 — Riesgo alto: cerrar antes de beta Enterprise/Government

| # | Hallazgo | Origen / evidencia |
|---|----------|-------------------|
| P1.1 | Clasificación de datos N0-N4 / PII scanner no implementado. | `POL_DATA_CLASSIFICATION §K`. |
| P1.2 | Hard block D9 no implementado en código. | `SPEC_ACTION_ENGINE D9`. |
| P1.3 | Gold sample pipeline / 7 checks de promoción cross-tenant no automatizados. | `POL_FB_KR_PRIVACY_TIERS_v1.1 §3`. |
| P1.4 | ModelFingerprint / probation no implementado. | `ARCH_AGENT_PRINCIPLES P13`. |
| P1.5 | Export / portabilidad de datos no implementado. | `AUDIT_FABERLOOM_TRAZABILIDAD_V3_v1.md` C16; `SPEC_AUDIT_MODULE §4`. |
| P1.6 | Zero Data Retention no configurado contractualmente. | `ENT_GOB_PENDIENTES.md §CEO-38`. |

### P2 — Mejoras / deuda técnica y legal

| # | Hallazgo | Origen / evidencia |
|---|----------|-------------------|
| P2.1 | Conflicto de planificación: `SPEC_FB_BUILD_SEQUENCE_v3` vs `PLAN_DESARROLLO_FABERLOOM_v5`. | `PLAN_DESARROLLO_FABERLOOM_v5 §0`. |
| P2.2 | Aviso de privacidad y consentimiento LGPD para scanner BR pendiente. | `ENT_COMP_REGULATORIO.md B3`. |
| P2.3 | DPO designado no documentado. | `POL_FB_KR_PRIVACY_TIERS_v1.1 §6`. |
| P2.4 | Pricing y tiers sin validación de mercado. | `ENT_FB_PRICING_TIERS_v1 §Limitaciones`. |
| P2.5 | Deletion/retention workflows no implementados. | `ENT_GOB_PENDIENTES.md §CEO-40`. |

---

## 6. Conclusión y recomendación de no-venta

FaberLoom cuenta con una **arquitectura de seguridad y compliance bien pensada en papel**: clasificación N0-N4, hard block D9, audit trail D10, RLS multi-tenant, privacy tiers, RAG firewall y DPA chain. Sin embargo, **ninguno de esos controles está implementado y probado en un producto ejecutable** al cierre de esta auditoría.

**Recomendación:**

- **NO vender** FaberLoom a bancos, gobiernos, hospitales ni ningún cliente regulado hasta cerrar los hallazgos P0.  
- Limitar la beta inicial a clientes no regulados, con contratos que NO mencionen compliance LGPD/LFPDPPP/auditoría inmutable/RLS multi-tenant como entregables, o que los aclaren explícitamente como “roadmap futuro”.  
- Priorizar la implementación en este orden: DPA registry → D9 PolicyGate → D10 audit trail → RLS multi-tenant → breach notification → PII scanner → RAG firewall runtime approval → export portability.  
- Obtener dictamen legal escrito por país (CR, GT, CO, MX, BR, AR, CL, PE) antes de procesar datos personales o sensibles de clientes reales.  
- Realizar una auditoría externa independiente después de cerrar los P0, antes de cualquier oferta Enterprise/Government.

---

## 7. Fuentes consultadas

- `C:\dev\mwt-knowledge-hub\docs\CLAUDE.md`
- `C:\dev\mwt-knowledge-hub\docs\RW_ROOT.md`
- `C:\dev\mwt-knowledge-hub\docs\ARCH_AGENT_PRINCIPLES.md`
- `C:\dev\mwt-knowledge-hub\docs\SPEC_ACTION_ENGINE.md`
- `C:\dev\mwt-knowledge-hub\docs\POL_DATA_CLASSIFICATION.md`
- `C:\dev\mwt-knowledge-hub\docs\SPEC_AUDIT_MODULE.md`
- `C:\dev\mwt-knowledge-hub\docs\ENT_PLAT_ACTION_REGISTRY.md`
- `C:\dev\mwt-knowledge-hub\docs\ENT_COMP_REGULATORIO.md`
- `C:\dev\mwt-knowledge-hub\docs\ENT_GOB_PENDIENTES.md`
- `C:\dev\mwt-knowledge-hub\docs\ENT_GOB_ENGINEERING_COMPETENCIES.md`
- `C:\dev\mwt-knowledge-hub\docs\faberloom\SPEC_FABERLOOM_MVP.md`
- `C:\dev\mwt-knowledge-hub\docs\faberloom\SPEC_FB_AUTH_TENANT_RBAC_v1.md`
- `C:\dev\mwt-knowledge-hub\docs\faberloom\SPEC_FB_RAG_SECURITY_FIREWALL_v1.md`
- `C:\dev\mwt-knowledge-hub\docs\faberloom\SPEC_FB_AI_CONTROL_PLANE_v1.md`
- `C:\dev\mwt-knowledge-hub\docs\faberloom\POL_FB_KR_PRIVACY_TIERS_v1.md`
- `C:\dev\mwt-knowledge-hub\docs\faberloom\SCH_FB_VOICE_PROFILE_v1.md`
- `C:\dev\mwt-knowledge-hub\docs\faberloom\SPEC_FB_VOICE_HUMANIZER_v2.md`
- `C:\dev\mwt-knowledge-hub\docs\faberloom\ENT_FB_PRICING_TIERS_v1.md`
- `C:\dev\mwt-knowledge-hub\docs\faberloom\SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1.md`
- `C:\dev\mwt-knowledge-hub\docs\faberloom\PLAN_DESARROLLO_FABERLOOM_v5.md`
- `C:\dev\mwt-knowledge-hub\docs\AUDIT_FABERLOOM_TRAZABILIDAD_V3_v1.md`
- `C:\dev\mwt-knowledge-hub\docs\AUDIT_FABERLOOM_A7_CHAT_CONTRADICTIONS_v1.md`
- `C:\dev\mwt-knowledge-hub\docs\anexos\kimi_swarm_7\D3_Base_Legal_Datos_B2B.md`

---

*Fin del informe.*
