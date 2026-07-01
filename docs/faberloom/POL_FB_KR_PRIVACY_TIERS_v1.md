---
id: POL_FB_KR_PRIVACY_TIERS_v1
version: 1.1
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma
type: policy
stamp: VIGENTE 2026-05-02 (v1.1 post correccion modelo 2 capas R5)
fecha: 2026-05-02 (update v1.1)
agente: Cowork (redaccion) + CEO (decisiones) + ChatGPT (auditoria R2+R3+R5)
aplica_a: [FaberLoom]
extiende: POL_DATA_CLASSIFICATION (sealed v1.4 · NO modifica core · agrega tiers Knowledge River)
relacionado_con:
  - SPEC_FB_KNOWLEDGE_RIVER_v1
  - POL_DATA_CLASSIFICATION (core sealed)
  - SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1
  - ENT_FB_VERTICAL_SPEC_OBJECT_v1
referencias_legales:
  - LFPDPPP Mexico (Ley Federal de Proteccion de Datos Personales en Posesion de los Particulares)
  - LGPD Brasil (Lei Geral de Protecao de Dados)
  - Habeas Data Colombia (Ley 1581 de 2012)
  - NIST de-identification guidelines
---

# POL_FB_KR_PRIVACY_TIERS_v1
## Politica de tiers de privacy para Knowledge River

## 1. Proposito

Knowledge River canoniza 5 capas de conocimiento (L0-L4). Sin policy de privacy granular, la promocion de patterns cross-tenant queda liquida. R2 marco esto como gap critico: "k-anon ≥5 NO es suficiente" para cumplir LFPDPPP MX + LGPD BR.

Esta politica define **4 tiers de privacy** que segmentan los datos del Knowledge River por sensibilidad y elegibilidad para promocion cross-tenant.

> **Insight ChatGPT R2:** "k-anon ≥5 sirve como barrera estadistica minima · pero no cubre base legal · finalidad · consentimiento · transferencias · minimizacion · derechos ARCO/LGPD · seguridad · retencion ni segregacion tenant."

> **Insight ChatGPT R3:** TIER 4 RESTRICTED_SENSITIVE_OR_REGULATED es necesario para B2B industrial con datos HSE, biometria, secretos comerciales duros · NO es policy generic.

## 2. Los 4 tiers canonicos

### 2.1 PRIVATE_RAW
- **Definicion:** datos crudos del tenant · identificadores directos presentes · sin transformacion
- **Almacenamiento:** tenant-isolated · no shared physical storage cross-tenant
- **Retencion:** corta · definida por contrato (default 90 dias para operacionales · variable para regulados)
- **Acceso:** solo rol autorizado del tenant (AM · supervisor · CEO · auditor del tenant)
- **Transferencia cross-tenant:** **PROHIBIDA**
- **Borrado:** ARCO/LGPD ejecutable sobre dato original · cascade a derivados trazables
- **Ejemplos:** emails clientes raw · proformas con datos identificables · transcripciones llamadas con voces · contratos con clausulas

### 2.2 TENANT_DERIVED
- **Definicion:** datos derivados del tenant · sin identificadores directos · pero comerciales/operacionalmente identificables al tenant origen
- **Almacenamiento:** tenant-isolated · indices separados per tenant
- **Retencion:** media · default 365 dias · configurable
- **Acceso:** tenant + curador del tenant
- **Transferencia cross-tenant:** **PROHIBIDA externa** · permitida entre derivados del mismo tenant
- **Borrado:** debe invalidar derivados trazables si dependen de dato personal eliminado
- **Ejemplos:** patrones de tono comercial del tenant · gold samples de respuestas · sender profiles agregados · scoring de productos

### 2.3 GLOBAL_PROMOTABLE
- **Definicion:** patrones abstractos sin tenant · cliente · precio · persona · contrato ni patron comercial identificable
- **Almacenamiento:** pool multi-tenant · solo accesible via API anonimizada
- **Retencion:** larga permitida (>2 anos · revisable)
- **Acceso:** multi-tenant · TODOS los tenants reciben patrones anonimizados via routing.global
- **Transferencia:** permitida solo como template/patron · NUNCA con datos especificos
- **Borrado:** por lineage si se demuestra origen removible · borrado individual no aplica (es patron agregado)
- **Ejemplos:** "para industria X · cuando confidence_classifier <0.7 · escalation rate aumenta 12%" · sin nombrar industrias/empresas

### 2.4 RESTRICTED_SENSITIVE_OR_REGULATED (TIER 4)
- **Definicion:** datos sensibles o regulados que NO pueden salir del tenant ni siquiera anonimizados
- **Almacenamiento:** tenant-isolated · encripcion at-rest reforzada · key per tenant
- **Retencion:** larga regulada · per legislacion aplicable (5-10 anos tipico)
- **Acceso:** acceso limitado · override approval · audit obligatoria de cada acceso
- **Transferencia cross-tenant:** **PROHIBIDA siempre** · sin excepcion
- **Borrado:** por procedimiento regulatorio · NO ejecutable en runtime sin aprobacion CEO + DPO
- **Ejemplos:**
  - Salud / ergonomia trabajador (incidentes HSE · workers comp claims)
  - Biometria (huella · retina · facial recognition)
  - Datos laborales sensibles (sueldos · evaluaciones · disciplinarias)
  - Secretos comerciales duros (formulas · procesos manufactura · diseños propietarios)
  - Precios estrategicos individualizables (descuentos VIP exclusivos · margenes negociados unicos)
  - Documentos contractuales con penalidades (licitaciones · acuerdos confidencialidad)

## 3. Promocion entre tiers · alineado con modelo 2 capas (v1.1)

```
CAPA 1 USUARIO (AM soberano · sin k-anon · L2 episodica privada):
  PRIVATE_RAW (data crudo) ──[AM aplica pattern personal]──> queda en L2 (TENANT_DERIVED individual)
  
  Aqui NO aplica k-anon · NO aplica los 7 checks · es data del AM.

CAPA 2 ORGANIZACION (comite · k-anon ≥5 · L3 colectivo):
  L2 multiples AMs (≥5 con patterns similares) ──[comite + 7 checks]──> L3 cross-AM (GLOBAL_PROMOTABLE)
  L3 estable >=90d ──[comite + DPA tenant]──> L4 indexed firmado (cross-tenant)
  
  Aqui SI aplica k-anon ≥5 · SI aplican los 7 checks · responsabilidad del comite.

TIER 4:
  RESTRICTED_SENSITIVE_OR_REGULATED ──[NUNCA promueve]──> ✗
```

**Regla critica v1.1 (correccion R5):** k-anon ≥5 SOLO se aplica en transiciones L2 → L3 (capa 2 · responsabilidad comite). NUNCA en cadencia personal del AM (capa 1). El AM NO ve k-anon en su flujo diario.

### 7 checks obligatorios para promover TENANT_DERIVED → GLOBAL_PROMOTABLE

1. **Privacy review humana** · curador del tenant + curador FB (si aplica) revisan antes de promover
2. **Reidentification test** · verificar imposibilidad de reidentificar tenant origen via combinacion de patterns
3. **L-diversity check** · ademas de k-anon ≥5 · cada equivalence class debe tener al menos l valores distintos en atributo sensible
4. **Secret-commercial review** · verificar que pattern no expone estrategia comercial · pricing · cliente · proveedor
5. **Lineage audit** · trazar origen del pattern · todas las entradas que lo formaron · verificar consents
6. **Tenant consent/contract check** · verificar DPA firmado del tenant origen · finalidad permitida explicitamente
7. **Purpose compatibility check** · proposito original del dato (operacional · entrenamiento · etc) debe ser compatible con uso futuro como pattern global

Si CUALQUIER check falla → no promueve · vuelve a TENANT_DERIVED · razon documentada.

## 4. Reglas operacionales minimas per tier

### 4.1 PRIVATE_RAW
| Dimension | Regla |
|---|---|
| Almacenamiento | Tenant-isolated · cifrado at-rest · key per tenant |
| Retencion | Definida por contrato · default 90d operacionales |
| Acceso | Solo roles autorizados · cada acceso loggeado |
| Transferencia | Cross-tenant prohibida · transferencia interna requiere audit |
| Borrado | ARCO/LGPD ejecutable · cascade a derivados |

### 4.2 TENANT_DERIVED
| Dimension | Regla |
|---|---|
| Almacenamiento | Tenant-isolated · indices separados · sin identificadores directos |
| Retencion | Media · default 365d · configurable |
| Acceso | Tenant + curador del tenant |
| Transferencia | Externa prohibida · interna permitida con audit |
| Borrado | Invalida derivados trazables si origen personal eliminado |

### 4.3 GLOBAL_PROMOTABLE
| Dimension | Regla |
|---|---|
| Almacenamiento | Pool multi-tenant · API anonimizada |
| Retencion | Larga · revisable cada 24 meses |
| Acceso | Multi-tenant via routing.global |
| Transferencia | Como template/patron solamente · sin datos especificos |
| Borrado | Por lineage · individual no aplica |

### 4.4 RESTRICTED_SENSITIVE_OR_REGULATED (TIER 4)
| Dimension | Regla |
|---|---|
| Almacenamiento | Tenant-isolated · cifrado refortzado · key per tenant + key escrow regulatorio |
| Retencion | Larga regulada · 5-10 anos tipico · variable por legislacion |
| Acceso | Limitado · override approval · audit obligatoria cada acceso |
| Transferencia | Prohibida siempre · sin excepcion |
| Borrado | Procedimiento regulatorio · CEO+DPO aprobacion |

## 5. Compliance per legislacion

### 5.1 LFPDPPP Mexico
- Tratamiento legitimo · controlado · informado de datos personales
- Reglamento exige medidas administrativas · fisicas · tecnicas
- Funciones definidas (Aviso de Privacidad · DPO si aplica)
- Analisis de riesgo de datos personales

**Implementacion FaberLoom:** PRIVATE_RAW + TENANT_DERIVED cumplen via tenant-isolation + roles + audit. GLOBAL_PROMOTABLE requiere DPA explicito + finalidad documentada. TIER 4 NUNCA cross-tenant.

### 5.2 LGPD Brasil
- Principios: finalidad · adecuacion · necesidad · transparencia · seguridad · prevencion · accountability
- Dato anonimizado deja de ser personal SOLO si no puede reidentificarse con medios tecnicos razonables disponibles al momento del tratamiento
- Base legal para tratamiento + reglas uso compartido

**Implementacion FaberLoom:** Reidentification test obligatorio (check #2) cumple criterio LGPD de "medios tecnicos razonables". DPO requerido para tenants brasileros.

### 5.3 Habeas Data Colombia (Ley 1581/2012)
- Consentimiento previo · expreso · informado
- Tratamiento por finalidad explicita
- Derecho a actualizar · rectificar · suprimir
- Transferencia internacional con garantias

**Implementacion FaberLoom:** Tenant consent/contract check (check #6) cumple. Cross-border transfer dentro LATAM con DPA cumple.

### 5.4 Equivalentes (Argentina · Chile · Peru)
Politicas locales mas relajadas que MX/BR/CO pero PRIVATE_RAW y TIER 4 cumplen automaticamente. TENANT_DERIVED requiere DPA si transferencia internacional.

## 6. DPO (Data Protection Officer)

LGPD Brasil exige DPO para empresas que tratan datos personales en escala. LFPDPPP no exige pero recomienda. Habeas Data Colombia exige Oficial de Proteccion de Datos para responsables grandes.

**Politica FaberLoom:**
- Tenants con >1000 customers en Brasil → DPO obligatorio antes Sem 0
- Tenants en MX/CO → recomendado · obligatorio si procesan datos sensibles (TIER 4)
- DPO designado debe firmar DPA con FaberLoom como co-controller

## 7. Privacy classification en cada output

`SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1` lo refleja en `privacy_classification`:

```yaml
privacy_classification:
  inputs_tier: enum  # PRIVATE_RAW | TENANT_DERIVED | GLOBAL_PROMOTABLE | RESTRICTED_SENSITIVE_OR_REGULATED
  outputs_tier: enum
  cross_tenant_eligibility: boolean
```

Regla: `outputs_tier >= inputs_tier` (no se puede declasificar). Cross_tenant_eligibility=true requiere outputs_tier=GLOBAL_PROMOTABLE Y los 7 checks pasados.

## 8. Reglas inquebrantables

1. **TIER 4 NUNCA cross-tenant.** Sin excepcion · sin override · sin "caso especial".
2. **Promocion requiere los 7 checks.** Skip de cualquier check = promocion invalida.
3. **k-anon ≥5 es minimo NO suficiente.** Siempre acompañar con l-diversity + reidentification test.
4. **DPA firmado obligatorio para Layer 1 cross-tenant.** Sin DPA · tenant solo opera con su Layer 2 propia.
5. **Retencion no es eterna por comodidad.** Default 90d/365d/2 anos · revisable per tier · borrado obligatorio al expirar.
6. **Audit log obligatorio per acceso a TIER 4.** Each access logged · revisado mensual por DPO si existe.
7. **Cliente final NUNCA ve clasificacion privacy.** Es interno operacional · audit visible solo a tenant + DPO + auditor regulatorio.
8. **Cambios de tier requieren versionado del policy.** No se mutan tiers en runtime.

## 9. Pendientes v1.1

1. Per-tenant privacy review board (cuando tenant grande tiene >1 curador)
2. Auto-clasificacion de outputs por LLM (con HITL P3 para validar)
3. Privacy dashboard analitico (queries acceso TIER 4 · trends)
4. Cross-tenant pool query metrics (cuanto se usa Layer 1 vs Layer 2)
5. Right-to-be-forgotten implementacion automatizada (cascade)

## Changelog
- 2026-04-30 v1.0 VIGENTE: Creacion inicial post R2+R3. 4 tiers canonicos (PRIVATE_RAW · TENANT_DERIVED · GLOBAL_PROMOTABLE · RESTRICTED_SENSITIVE_OR_REGULATED) · TIER 4 agregado en R3 para datos HSE/biometria/secretos comerciales/precios estrategicos. 7 checks obligatorios promocion (3 agregados en R2: lineage audit · tenant consent/contract check · purpose compatibility check). Compliance per LFPDPPP MX + LGPD BR + Habeas Data CO + equivalentes. DPO requirements documentados. Integration con SCH_FB_QUOTE_EVIDENCE_BUNDLE.privacy_classification. 8 reglas inquebrantables. NO modifica POL_DATA_CLASSIFICATION sealed v1.4 · es extension separada Knowledge River-specific.

## Stamp
VIGENTE 2026-04-30 — Endurece Knowledge River cumpliendo LFPDPPP/LGPD/Habeas Data. k-anon ≥5 + l-diversity + 7 checks promocion en pipeline. TIER 4 protege datos sensibles industriales (HSE · biometria · secretos comerciales). Sin esta politica · cross-tenant pool es riesgo legal · no moat.
