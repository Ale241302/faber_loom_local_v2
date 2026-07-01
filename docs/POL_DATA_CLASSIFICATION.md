# POL_DATA_CLASSIFICATION — Clasificación de Datos
id: POL_DATA_CLASSIFICATION
version: 1.4
domain: Compliance (IDX_COMPLIANCE)
status: VIGENTE
activation_trigger: Action Engine D9 (consumo desde 2026-04-28) · Piloto ISO (base de cadena ISO de datos)
visibility: [INTERNAL]
stamp: VIGENTE — 2026-04-28
refs: POL_VISIBILIDAD, ENT_PLAT_SEGURIDAD, ENT_COMP_PRIVACIDAD, SPEC_ACTION_ENGINE (D9), SPEC_AUDIT_MODULE (D10), ENT_FABERLOOM_PRICING_TIERS, ARCH_AGENT_PRINCIPLES (P13, P14)
iso: 27001:2022 A.5.12, A.5.13
aplica_a: [SHARED]

---

## A. Propósito

Define cómo se clasifican todos los datos que MWT genera, procesa o almacena. Extiende POL_VISIBILIDAD (que clasifica documentos internos) al dominio de datos de terceros, datos biométricos y datos de distribuidores.

POL_VISIBILIDAD sigue vigente para documentos del knowledge base. Esta policy agrega clasificación para datos operativos y de terceros.

---

## B. Niveles de clasificación

| Nivel | Etiqueta | Quién accede | Ejemplo | Almacenamiento | Cifrado |
|-------|---------|-------------|---------|---------------|---------|
| N0 | [PUBLIC] | Cualquiera | Catálogo productos, specs técnicas, claims aprobados | Cualquiera | No requerido |
| N1 | [INTERNAL] | Equipo MWT | Estrategia, riesgos, métricas internas, playbooks | PostgreSQL / MinIO / Git | En reposo recomendado |
| N2 | [CONFIDENTIAL] | CEO + roles autorizados | Pricing fábrica, márgenes, costos, modelos financieros | PostgreSQL con RLS | En reposo obligatorio |
| N3 | [DISTRIBUTOR-SCOPED] | Distribuidor owner + CEO | Catálogo del distribuidor, métricas de uso, escaneos de sus clientes | PostgreSQL con RLS + tenant_id | En tránsito y reposo obligatorio |
| N4 | [BIOMETRIC] | Sistema (procesamiento) + CEO (auditoría) | Escaneos de presión plantar, perfiles biomecánicos, métricas corporales | PostgreSQL cifrado + MinIO cifrado | En tránsito y reposo obligatorio. Anonimizable. |

---

## C. Reglas por nivel

### C1. N0 [PUBLIC]
- Puede aparecer en cualquier output externo.
- No requiere consentimiento para uso.
- Coincide con `[PUBLIC]` de POL_VISIBILIDAD; `[ALL]` es alias legacy deprecated desde 2026-04-28 (ver §H taxonomía canónica).

### C2. N1 [INTERNAL]
- No sale en outputs externos.
- Coincide con `[INTERNAL]` de POL_VISIBILIDAD; `[CREATIVE]` y `[TECH]` son aliases legacy deprecated desde 2026-04-28 que se tratan como `[INTERNAL]` (ver §H taxonomía canónica).

### C3. N2 [CONFIDENTIAL]
- Coincide con [CEO-ONLY] de POL_VISIBILIDAD.
- Acceso auditado: cada consulta genera log entry.
- Nunca aparece en: proformas cliente, espejo documental, portal B2B, outputs del scanner.

### C4. N3 [DISTRIBUTOR-SCOPED]
- Dato pertenece al distribuidor. MWT es procesador, no propietario.
- Row-level security con tenant_id. Distribuidor A no ve datos de Distribuidor B.
- CEO ve todo con flag de auditoría.
- Eliminación obligatoria si distribuidor termina contrato (ref → POL_RETENCION_ESCANEOS).
- Requiere DPA (Data Processing Agreement) firmado antes de capturar datos.

### C5. N4 [BIOMETRIC]
- Dato personal sensible bajo LGPD (Brasil Art. 5 y 11), BIPA (Illinois), CCPA (California).
- Requiere consentimiento explícito del usuario escaneado antes de captura (ref → POL_CONSENTIMIENTO).
- Procesamiento determinístico y versionado (ref → POL_DETERMINISMO): mismos inputs = mismos outputs.
- Anonimización programada: después del período de retención, el perfil se desvincula de la persona.
- Hash de integridad obligatorio: SHA-256 del frame al momento de captura. Inmutable post-captura.
- Derecho de eliminación: el usuario escaneado puede solicitar borrado de su escaneo.

---

## D. Mapeo a sistemas

| Sistema | Datos que maneja | Niveles aplicables |
|---------|-----------------|-------------------|
| PostgreSQL (MWT.ONE) | Expedientes, costos, márgenes, estados | N1, N2 |
| PostgreSQL (Scanner SaaS) | Escaneos, perfiles, catálogos distribuidor | N3, N4 |
| MinIO | Documentos, facturas, escaneos archivados | N1, N2, N3, N4 |
| Git (knowledge base) | Entities, policies, playbooks, schemas | N0, N1 |
| Email (servidor correo) | Comunicaciones operativas | N1, N2 (temporal — ref POL_ARCHIVO) |

---

## E. Acciones prohibidas por nivel

| Acción | N0 | N1 | N2 | N3 | N4 |
|--------|----|----|----|----|-----|
| Publicar sin revisión | ✅ | ❌ | ❌ | ❌ | ❌ |
| Compartir entre distribuidores | ✅ | ✅ | ❌ | ❌ | ❌ |
| Exportar sin cifrado | ✅ | ✅ | ❌ | ❌ | ❌ |
| Almacenar en dispositivo local | ✅ | ✅ | ❌ | ❌ | ❌ |
| Usar para training de IA | ✅ | ✅ | ❌ | ❌ | ❌ |
| Retener indefinidamente | ✅ | ✅ | ✅ | Según DPA | Según POL_RETENCION_ESCANEOS |

---

## F. Etiquetado

Todo registro de datos nivel N2+ debe tener en su metadata:
- `classification`: nivel (N0-N4)
- `owner`: quién es dueño del dato (MWT, distribuidor, usuario final)
- `retention_policy`: ref a la policy de retención aplicable
- `created_at`: timestamp de creación
- `created_by`: actor que creó el registro

Para N4 (biométrico) adicionalmente:
- `consent_id`: referencia al registro de consentimiento (ref → §G)
- `integrity_hash`: SHA-256 del dato original
- `motor_version`: versión del motor biomecánico que lo procesó
- `anonymization_date`: fecha programada de anonimización

---

## G. Consent Receipt — Modelo para datos N4

Cuando se captura un dato N4 [BIOMETRIC], el sistema debe generar un consent receipt vinculado al escaneo.

### G1. Campos mínimos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| consent_id | UUID | Identificador único del consentimiento |
| scan_id | ref | Escaneo al que se vincula |
| timestamp | datetime | Momento en que se otorgó consentimiento |
| distributor_id | ref (tenant) | Distribuidor en cuyo punto de venta se capturó |
| purpose | enum | fitting_recommendation (único propósito válido en v1) |
| scope | text | "Medición de presión plantar para recomendación de calzado y plantilla" |
| policy_version | string | Versión de la política de privacidad aceptada |
| method | enum | digital_checkbox (en UI del scanner, pre-scan) |
| revocable | boolean | true — usuario puede solicitar eliminación |
| revoked_at | datetime | null hasta que se revoque. Si se revoca → anonimizar scan. |

### G2. Reglas
- Sin consent_id válido, el sistema no permite iniciar escaneo.
- Consent receipt es inmutable (ref → POL_INMUTABILIDAD). Revocación = nuevo registro, no edición.
- Consent receipt se almacena separado del escaneo. Si se anonimiza el scan, el consent receipt persiste como evidencia de que hubo consentimiento válido en su momento.
- Implementación: Fase 2 del roadmap ISO, junto con POL_CONSENTIMIENTO.

---

## H. Regla de precedencia Visibilidad × Classification

POL_VISIBILIDAD controla quién ve documentos del knowledge base (editorial, operativo).
POL_DATA_CLASSIFICATION controla cómo se protegen datos operativos en sistemas (técnico).

Reglas:
1. Classification manda sobre Visibility para controles técnicos (cifrado, acceso DB, logging).
2. Visibility manda sobre Classification para outputs y documentos editoriales.
3. Todo documento que contenga datos N2+ debe tener visibility mínima [INTERNAL].
4. Todo documento que contenga datos N3+ debe tener visibility [CEO-ONLY] **y** metadata `distribution_scope: <tenant_id>`. DISTRIBUTOR-SCOPED es propiedad de classification, NO es un tier de visibility.
5. Un documento [PUBLIC]/[ALL] nunca puede contener datos N2, N3 o N4 inline. Si necesita referenciarlos, usa ref → sin incluir el dato.
6. **Detección de N2+ en docs [PUBLIC]/[ALL]:** chunker pgvector ejecuta PII scanner pre-ingestión. Si detecta patrones N2+ en documento declarado [PUBLIC]/[ALL], **HARD BLOCK** — ingestión rechazada + escala al CEO. Sin scanner disponible, ingestión bloqueada por default. Esta detección NO admite override Tier 2.

**Taxonomía canónica de visibility (v1.4 — reconciliación):**

Los tiers de visibility canónicos son los declarados en R6 de las reglas KB:

| Tier canónico | Quién ve | Aliases legacy (deprecated 2026-04-28) |
|---|---|---|
| `[PUBLIC]` | Cualquiera, incluido proveedores externos | `[ALL]` |
| `[PARTNER_B2B]` | CEO + clientes B2B autorizados | (nuevo, sin alias previo) |
| `[INTERNAL]` | Equipo MWT | `[CREATIVE]`, `[TECH]` |
| `[CEO-ONLY]` | Solo CEO | (sin alias) |

Los aliases `[ALL]`, `[CREATIVE]`, `[TECH]` quedan **DEPRECATED** desde
2026-04-28 — siguen siendo legibles por compatibilidad pero todo
archivo nuevo o modificado debe usar los 4 tiers canónicos. POL_VISIBILIDAD
debe actualizarse a la taxonomía canónica en próxima revisión (no en
scope de iteración CORE actual).

Mientras la migración no se complete, las equivalencias arriba son
vinculantes para enforcement y auditoría: `[ALL]` se trata como
`[PUBLIC]`, `[CREATIVE]` y `[TECH]` se tratan como `[INTERNAL]`.

---

## Enforcement

**Severidad por tipo de violación (v1.4 — clarificación):**

| Violación detectada | Severidad | Acción |
|---|---|---|
| Archivo sin campo `visibility:` | SOFT | Agregar visibility en próxima sesión, notificar en health check, no bloquea trabajo |
| Archivo con visibility usando alias deprecated (`[ALL]`, `[CREATIVE]`, `[TECH]`) | SOFT | Migrar a tier canónico, notificar |
| Archivo con visibility incorrecta para su classification declarada (ej. doc N3+ sin `[CEO-ONLY]`) | SOFT-HIGH | Corregir antes de compartir, escalar si persiste >2 sesiones |
| **Detección de PII / dato N2+ en doc declarado `[PUBLIC]`/`[ALL]`** (§H.6 — PII scanner) | **HARD BLOCK** | Ingestión rechazada inmediatamente, escala al CEO con muestra del patrón detectado, ningún chunk persiste |
| Routing N3/N4 a provider sin DPA reconocido (§I) | **HARD BLOCK** | Action Engine retorna `DPAUnavailable`, no ejecuta, AuditEntry inmutable |
| Lectura del mapping token↔real fuera del proceso de de-anonimización (§J) | **HARD BLOCK** | Acceso denegado, alerta crítica, AuditEntry inmutable |

La severidad SOFT aplica solo a metadata faltante o aliases deprecated
sin datos sensibles detectados. Cualquier detección activa de fuga de
classification (N2+ en lugar incorrecto) es HARD BLOCK sin override.

---

## I. Routing a modelos LLM (Action Engine D9)

Extiende N0-N4 a routing de calls LLM. Cada `ActionContext` lleva `data_classification` y el Engine aplica:

| Nivel | Routing LLM | Cost-mode | Anonim default | Audit |
|---|---|---|---|---|
| N0 PUBLIC | cualquier modelo | sí | L0 | básico |
| N1 INTERNAL | modelos con DPA (Anthropic/OpenAI/Google) por default · cost-mode habilita DeepSeek/Kimi self-host con opt-in tenant | opt-in tenant (default OFF) | L1 | básico |
| N2 CONFIDENTIAL | US/EU + DPA obligatorio | no | L2 | detallado |
| N3 DISTRIBUTOR-SCOPED | US/EU + DPA + RLS per-tenant | no | L2 | detallado + RLS |
| N4 BIOMETRIC | US/EU exclusivo (ver definición vinculante abajo) | no | L3 obligatoria | full + retention 10y |

**Reconciliación cost-mode N1 (v1.3):** §I y §K usan la misma semántica — `opt-in tenant` con default OFF. Si tenant no activa cost-mode explícitamente, todo N1 va a providers con DPA. Esto evita que data N1 termine en providers no-DPA por defecto.

**DPA (Data Processing Agreement) reconocido para LATAM:**
- ✅ Anthropic, OpenAI, Google: DPA estándar disponible
- ❌ DeepSeek, Kimi (managed China): sin DPA reconocido — solo permitidos para N0/N1 con cost-mode opt-in tenant
- ⚠️ Self-host (Kimi K2.6 MIT en infra propia LATAM): vos sos el processor, vos firmás DPA con clientes

**Hard block (v1.3 — sin override):** N3/N4 nunca se envían a providers sin DPA reconocido. **No existe override CEO para omitir DPA.** El CEO solo puede aprobar cambio de provider después de registrar DPA válido y base legal aplicable. Cualquier intento de routing N3/N4 a provider sin DPA registrado retorna `PlanUpgradeRequired` o `DPAUnavailable` desde el Action Engine — no se ejecuta.

**Definición vinculante de "US/EU exclusivo" para N4 (v1.4):** un provider califica para procesar data N4 solo si cumple TODAS estas condiciones simultáneamente:

1. **Sede legal del provider:** corporación constituida en jurisdicción US o EU/EEA. Sin proxies offshore.
2. **Región de cómputo de inferencia:** API endpoint procesa exclusivamente en data centers ubicados físicamente en US o EU. Si el provider tiene endpoints multi-región, FaberLoom debe seleccionar explícitamente endpoint US/EU y firmar el restrictivo correspondiente.
3. **DPA reconocido y firmado:** Data Processing Agreement vigente con FaberLoom como controller, provider como processor, cubriendo art. 33 LGPD + Cláusulas Contractuales Tipo (SCC) UE si aplica.
4. **Subprocesadores declarados:** lista de subprocesadores del provider documentada y aprobada por FaberLoom. Cualquier cambio de subprocesador requiere notificación previa + revisión.
5. **Política de no-retention:** provider no retiene data N4 más allá del request (sin training, sin caché persistente, sin logs de prompt). Si el provider tiene retention default, FaberLoom debe optar por modo zero-retention contractualmente.
6. **Auditoría:** provider acepta auditoría externa periódica (mínimo anual) por auditor designado por FaberLoom o cliente Government tier.

Sin las 6 condiciones, el provider NO califica para N4 aunque tenga "presencia US/EU". Esta definición se valida con DPO/abogado antes de firmar contrato con cada provider nuevo.

**Conexión con P13 ModelFingerprint (v1.3):** cuando un tenant cambia provider o version (ej. Sonnet 4.5 → 4.6), el routing §I dispara automáticamente probation P13 del agente que lo usaba. Mientras está en probation, el agente baja un nivel de autonomía y debe revalidar antes de restaurar nivel previo. El routing §I ejecuta la nueva ModelFingerprint pero la autonomía no se transfiere.

**P14 — Definición de "caso no-estructurado" (v1.3):** un input es no-estructurado y elegible para LLM Fallback solo si cumple TODAS estas condiciones:
- Parser determinístico aplicable (regex, XML parser, schema validation) retorna `parse_error` o `confidence < 0.85`
- El input no matchea ninguno de los formatos LATAM cubiertos en Tier 0 (DIAN UBL 2.1, SII DTE, SAT CFDI 4.0, AFIP, SEFAZ NFe)
- El skill declara explícitamente en su AgentSpec que admite fallback LLM para esa action_class

Si las 3 condiciones no se cumplen, se escala a Human Gate sin invocar LLM.

---

## J. Niveles de anonimización (L0-L3)

Ortogonal a N0-N4. **Sensibilidad ≠ protección aplicada.** Configurable per-tenant.

| Nivel | Mecanismo | Costo extra/req | Use case típico |
|---|---|---|---|
| L0 — Raw | Chunk va tal cual al modelo | $0 | N0 PUBLIC, catálogos |
| L1 — Basic redact | Regex local: NIT, email, montos→rangos | ~$0 (local) | N1 INTERNAL operativa |
| L2 — LLM redact | Haiku 4.5 anonimiza pre-prompt | ~$0.005 | N2/N3 PII estándar |
| L3 — Synthetic | Datos sintéticos por mapping (real ↔ token) | ~$0.015 | N4 BIOMETRIC, regulado |

**De-anonimización post-respuesta:** sistema mapea L2/L3 tokens de vuelta a valores reales para presentar al usuario. Modelo nunca ve la data real.

**Protección del mapping token↔real (v1.3):** el mapping es activo crítico — si se filtra, la anonimización es reversible y la garantía cae. Reglas obligatorias:

- Storage: tabla separada del operativo, cifrada con KEK (Key Encryption Key) per-tenant
- Acceso: solo el proceso del Action Engine que ejecuta la de-anonimización post-respuesta. Ningún otro componente (UI, workers de otros skills, observabilidad) puede leer el mapping
- TTL: configurable per-tenant. Default 24h para L2, 1h para L3. Después del TTL, el mapping se elimina y la respuesta del modelo queda permanentemente anonimizada
- Auditoría: cada lectura del mapping genera AuditEntry inmutable (D10 del Action Engine) con hash chain
- Tamper detection: validación periódica de hash chain del mapping. Inconsistencia → alerta crítica + freeze + auditoría manual

**Imposibilidad de override:** ni siquiera el CEO puede leer el mapping de otro tenant. Acceso administrativo solo via auditor read-only API con MFA + audit-of-audit (SPEC_AUDIT_MODULE).

**Segregación per-tenant del proceso de de-anonimización (v1.4):** el proceso del Action Engine que ejecuta de-anonimización corre en sandbox aislado per-tenant. Reglas obligatorias:

- Worker del Action Engine procesando tenant A NO comparte memoria, namespace de variables, caché interno, ni file descriptors con worker procesando tenant B
- Implementación: cada worker es un proceso separado (no thread compartido) con cgroup/namespace isolation a nivel OS, o microVM (Firecracker/equivalente) para sandbox máximo
- El KEK de descifrado se carga al iniciar el procesamiento del request específico y se purga del proceso al terminar — nunca persiste cross-request
- Falla en aislamiento (ej. detección de memory leak entre workers) dispara HARD BLOCK del proceso afectado + alerta crítica + freeze del mapping del tenant comprometido hasta auditoría manual

---

## K. Modelo UX — Selector de confidencialidad por sesión

Cada conversación expone selector visual al cliente:

| Selector UX | Mapeo interno | Modelos disponibles |
|---|---|---|
| 🌐 Público | ceiling=N0, cost-mode ON, anonim L0 | cualquiera |
| 💼 Trabajo (default) | ceiling=N1, cost-mode opt-in tenant (default OFF), anonim L1 | US/EU con DPA por default · DeepSeek/Kimi self-host si tenant activa cost-mode |
| 🔒 Confidencial | ceiling=N2, cost-mode OFF, anonim L2 | US/EU con DPA |
| 🛡️ Privado | ceiling=N4, cost-mode OFF, anonim L3, audit full | US/EU exclusivo |

**Comportamiento:**
- Si chunk recuperado supera ceiling → modal "Esta consulta requiere 🔒. ¿Elevar nivel? [Sí] [No]". Audit trail registra el cambio.
- Tenant en modo strict (admin lock) → selector deshabilitado, fijo en nivel definido.

**Tres momentos de asignación de classification:**

1. **Al ingestar contenido** (source of truth): cliente sube doc → sistema clasifica via PII scanner + LLM judge → metadata pgvector. Sin classification → no se ingesta (default safe N1).
2. **Per-conversación**: cliente puede setear ceiling al iniciar sesión.
3. **Real-time input ad-hoc**: usuario pega texto en chat → scanner pre-prompt clasifica → si supera ceiling, bloquea o pide override.

**Naturaleza técnica del scanner pre-prompt y del PII scanner de ingestión (v1.4):**

| Componente | Especificación |
|---|---|
| Pipeline | 2 etapas: (1) regex determinístico para patrones LATAM conocidos (NIT, RUT, RFC, CUIT, CNPJ, número de tarjeta, email, teléfono, fecha de nacimiento, dirección), (2) LLM judge solo si etapa 1 retorna `confidence < 0.85` o detecta señal ambigua |
| Modelo LLM judge | Claude Haiku 4.5 (o equivalente Tier 1 con DPA reconocido) con structured output forzado |
| Output schema | `{ classification_detectada: enum[N0,N1,N2,N3,N4], patrones_encontrados: [{tipo, ubicacion, confidence}], anonimizacion_sugerida: enum[L0,L1,L2,L3], requiere_consent: boolean }` |
| Latencia objetivo | < 500 ms p95 (etapa 1 sola: ~5-50 μs; etapa 2 con LLM: ~300-450 ms) |
| Accuracy mínima | >= 92% en validación contra dataset golden de 500 docs LATAM por tenant. Si baja de 90%, escala al CEO + revisión de prompts |
| Costo objetivo | < $0.001 por scan (etapa 1 dominante en 70-80% de casos por P14 deterministic-first) |
| Falla del scanner | HARD BLOCK de ingestión / del input ad-hoc — no se procesa sin clasificación válida |
| Mantenimiento | Revisión trimestral de patrones LATAM por equipo de compliance del tenant. Cambios fiscales LATAM (DIAN, SII, SAT, AFIP, SEFAZ) actualizan patrones en bug-bash de cierre de sprint |

**Routing decision = max(class) en el prompt:**

```
prompt = chunks_recuperados + input_user + system_prompt
max_class = max(c.data_class for c in prompt)
Engine rutea según max_class y aplica anonim correspondiente.
```

---

## L. Mapeo a tiers comerciales (FaberLoom pricing)

Cada plan habilita un ceiling de classification. Ver `docs/faberloom/ENT_FB_PRICING_TIERS_v1.md` para detalle.

| Plan | Ceiling habilitado | Anonim default | Audit |
|---|---|---|---|
| Starter | N1 | L1 | básico |
| Pro | N2 (con add-on Confidencial) | L2 | detallado |
| Enterprise | N3 | L2/L3 | full |
| Government | N4 | L3 | full + auditor API + 10y retention |

**Action Engine D9 enforcement:**
```python
if data_classification > tenant_plan_ceiling(tenant_plan, addons):
    raise PlanUpgradeRequired(suggested_addon="confidencial_addon")
```

**Diferenciador comercial:** PYME que ya usa Claude.ai/ChatGPT acepta transferencia internacional. FaberLoom ofrece **el mismo provider con DPA chain consolidada + classification + audit + cost-mode opcional** — valor diferenciado real, no solo "data en LATAM".

---

## M. Retención de audit por nivel

| Nivel | Retención mínima audit log | Storage |
|---|---|---|
| N0/N1 | 1 año | hot storage |
| N2/N3 | 5 años | warm storage |
| N4 | 10 años | cold storage cifrado + immutable |

Hash chain validation periódica (ver SPEC_AUDIT_MODULE D10).

---

Changelog:
- v1.4 (2026-04-28): Iteración 3 de auditoría CORE. Cambios: (a) §H reglas 4-6 reescritas — taxonomía visibility canónica unificada (4 tiers R6: PUBLIC/PARTNER_B2B/INTERNAL/CEO-ONLY) + aliases legacy [ALL]/[CREATIVE]/[TECH] DEPRECATED con tabla de equivalencias; (b) Enforcement reescrito con tabla de severidad SOFT vs HARD BLOCK por tipo de violación; (c) §I N4 "US/EU exclusivo" definido vinculantemente — 6 condiciones simultáneas (sede legal, región cómputo, DPA, subprocesadores, no-retention, auditoría); (d) §J segregación per-tenant del proceso de de-anonimización (sandbox/cgroup/microVM, KEK purga post-request, falla aislamiento → HARD BLOCK); (e) §K naturaleza técnica de PII scanner / scanner pre-prompt — pipeline regex+Haiku, latencia <500ms p95, accuracy ≥92%, costo <$0.001/scan. Origen: ChatGPT iter 2 H10/H11/H13 + Kimi iter 2 R2.6/G3.8.
- v1.3 (2026-04-28): Iteración 2 de auditoría CORE post ChatGPT 5.5 + Kimi K2.6. Decisión CEO via Gemini: aislamiento absoluto del aprendizaje (no global learning). Cambios: (a) §H punto 4 reescrito — DISTRIBUTOR-SCOPED es classification, no visibility tier; (b) §H punto 6 nuevo — detección automática de N2+ en docs [ALL] vía PII scanner pre-ingestión; (c) §I hard block N3/N4 sin override CEO posible; (d) §I cost-mode N1 reconciliado con §K (opt-in tenant default OFF); (e) §I conexión explícita con P13 ModelFingerprint para probation post cambio de provider; (f) §I definición vinculante de "caso no-estructurado" para P14; (g) §J protección obligatoria del mapping token↔real (KEK + TTL + audit + tamper detection). Origen: 4 BLOCKERs + hallazgos convergentes consolidados en chat MWT Knowledge.
- v1.2 (2026-04-28): +§I Routing LLM (Action Engine D9) +§J Niveles anonim L0-L3 +§K UX selector +§L Mapeo tiers comerciales +§M Retención audit. Status DRAFT → VIGENTE. Origen: indexa hallazgos data classification + audit module + pricing tiers.
- v1.1 (sesión anterior): N0-N4 + scanner biométrico Rana Walk + ISO 27001.
- v1.0 (creación): primer scaffolding policy.
