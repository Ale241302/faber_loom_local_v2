# MANIFIESTO_APPEND — CORE BLINDADO
aplica_a: [SHARED]

**Fecha:** 2026-04-28
**Sesión:** Auditoría iterativa del CORE constitucional FaberLoom
**Resultado:** CORE BLINDADO ✅ (validación dual ChatGPT 5.5 + Kimi K2.6)

---

## Resumen ejecutivo

El CORE constitucional de FaberLoom (Anillo 0 + Anillo 1 contratos) fue
sometido a auditoría iterativa con dos LLMs externos en 3 iteraciones.
Ambos auditores cerraron con el threshold definido (≥8.5 global · 0
scores <7 · 0 BLOCKERs).

**Trayectoria del salto:**

| Auditor | Iter 1 | Iter 2 | Iter 3 | Veredicto |
|---------|--------|--------|--------|-----------|
| ChatGPT 5.5 | 7.6 | 8.1 | **8.7** | CIERRA ✅ |
| Kimi K2.6 | 6.3 | 7.83 | **8.5** | CIERRA ✅ |
| Promedio consolidado | 6.95 | 7.97 | **8.6** | — |

Score consolidado +1.65 desde baseline. D2 (no contradicción) y D5
(seguridad/compliance) fueron los mayores ganadores: +1.8 y +1.5
respectivamente.

---

## Archivos modificados

| Archivo | De → A | Cambios principales |
|---------|--------|---------------------|
| `docs/ARCH_AGENT_PRINCIPLES.md` | v1.3 → v1.5 | P3 invariante absoluto · P4 Nivel 3 solo internas · P11 multi-propuestas/single-destino + apéndice operativo Clasificador · P12 filtro N2+ obligatorio + confirmante humano por receptor · P13 aislamiento absoluto + jerarquía intra-tenant + pre-filtering + step-up auth 3 niveles · P7 tabla 11 transiciones · Tier 2 restricción external/high/N3+ · Glosario 7 términos vinculantes |
| `docs/POL_DATA_CLASSIFICATION.md` | v1.2 → v1.4 | §H taxonomía visibility canónica + aliases deprecated · §H.6 PII scanner pre-ingestión HARD BLOCK · Enforcement tabla SOFT/HARD por tipo · §I cost-mode opt-in default OFF + ModelFingerprint trigger probation + caso no-estructurado P14 + N4 "US/EU exclusivo" 6 condiciones vinculantes · §J protección mapping KEK + TTL + sandbox per-tenant · §K naturaleza técnica scanner pre-prompt |

**Archivos nuevos generados durante el proceso (working artifacts):**

- `core_audit_bundle.md` — bundle iter 1 (baseline)
- `core_audit_bundle_v2.md` — bundle iter 2 (post decisiones CEO Gemini)
- `core_audit_bundle_v3.md` — bundle iter 3 (CORE BLINDADO)
- `GEMINI_BRIEF_DECISIONES_CORE_20260428.md` — brief para resolución
  verbal de 2 decisiones críticas con CEO

Estos artifacts permanecen en `C:\Users\alvar\OneDrive\Documentos\Claude\Projects\MWT KB\`
como evidencia auditable del proceso. No son parte del CORE — son material
de proceso.

---

## Decisiones CEO formalizadas

Tres decisiones de producto se cristalizaron como cláusulas vinculantes
del CORE durante la auditoría:

**Decisión 1 (iter 2 vía Gemini) — P3 absoluto / Nivel 3 solo internas:**
"La autonomía externa solo se otorga tras un proceso comprobado de
aprendizaje y alta certeza técnica. Como un vehículo en carretera —
no se acelera hasta tener confianza absoluta de que el sistema
responde." Nivel 3 AUTO_NOTIFICA queda restringido a acciones
internas reversibles probadas.

**Decisión 2 (iter 2 vía Gemini) — Aislamiento absoluto del aprendizaje:**
"FaberLoom no es una consola IA de propósito general. Es un repositorio
operativo de la organización cliente. El conocimiento reside en la
organización del cliente, no en FaberLoom." Sin global learning derivado
de uso comercial. Gold samples globales solo escritos internamente por
FaberLoom sin uso de data cliente.

**Decisión 3 (iter 3 vía chat) — Step-up authentication 3 niveles:**
Cuando un agente publicado a la organización responde sobre datos
PROPIOS del consultante, el sistema aplica auth adicional según
classification: Nivel A (sesión normal, N0/N1) · Nivel B (MFA fresh
+ IP estable, N2/N3, TTL 15 min) · Nivel C (Nivel B + propósito +
aprobación humano_responsable, N4 o documentos formales con valor legal).

---

## Hallazgos residuales (deuda Anillo 2)

Los auditores dejaron 3 observaciones no-bloqueantes para revisar
cuando se audite Anillo 1+2:

1. Catalogar `error_class` y "IP estable" en glosario formal o
   definirlos en SPEC técnica del Anillo 2 (esfuerzo: 1h)
2. Documentar mecanismo de detección de "falla en aislamiento"
   (memory leak entre workers) en SPEC_AUDIT_MODULE D10 (esfuerzo: 2h)
3. Definir proceso de "des-identificación irreversible" para promoción
   excepcional de hechos N2+ a Org-wide — playbook 1 página CEO-only
   (esfuerzo: 1h)

Total deuda Anillo 2: ~4h. No bloquea cierre del CORE.

---

## Lo que esto habilita

Con el CORE blindado, los anillos exteriores se construyen heredando
estas garantías sin posibilidad de contradecirlas:

- **Anillo 1 (Contratos):** SPEC_ACTION_ENGINE v1.2 + SPEC_AUDIT_MODULE
  v1.0 ya están VIGENTE y respetan el CORE actual. Próxima auditoría
  los stress-tests con la misma metodología iterativa.
- **Anillo 2 (Composición):** SPEC_FABERLOOM_SKILL_COMPOSITION v1.0,
  SPEC_FABERLOOM_AGENT_COMPOSITION v1.1, SPEC_FABERLOOM_WORKFLOW_ENGINE
  v1.0 — todos en DRAFT. Pueden promover a APPROVED sabiendo que el
  cimiento es sólido.
- **Anillo 3+ (ejecución, infra, producto, comercial, compliance):**
  el equipo de implementación arranca con un contrato constitucional
  que un abogado técnico puede hacer cumplir entre dos ingenieros del
  equipo (criterio explícito del auditor).

---

## Validación externa

**ChatGPT 5.5 (iteración 3) — texto literal del veredicto:**
"La iteración 3 cierra. Los riesgos que quedan son de precisión
editorial o de implementación en Anillo 2, no de contrato CORE.
El salto fue claro: 7.6 → 8.1 → 8.7."

**Kimi K2.6 (iteración 3) — texto literal del veredicto:**
"El bundle v3 cumple el threshold de cierre. Las 12 remediaciones de
esta iteración consolidaron los hallazgos convergentes de ChatGPT 5.5,
Kimi K2.6 (iter 2) y decisiones CEO via Gemini. No quedan BLOCKERs,
contradicciones literales ni scores por debajo de 7."

---

## Estado canónico post-cierre

| Aspecto | Estado |
|---------|--------|
| ARCH_AGENT_PRINCIPLES | v1.5 VIGENTE — CORE constitucional blindado |
| POL_DATA_CLASSIFICATION | v1.4 VIGENTE — política de datos blindada |
| 6 reglas inquebrantables KB | Sin cambios — siguen vigentes |
| Jerarquía de invariantes | Tier 1 (P1, P3, P5, P9, P13 + hard blocks DPA) absolutos · Tier 2 con restricción external/high/N3+ · Tier 3 meta |
| Glosario vinculante | 7 términos definidos operativamente |

---

## Tag git asociado

`core-v1.0-blindado` — primera versión del CORE constitucional con
doble validación externa cerrada.

---

## Próximos pasos

| # | Acción | Cuándo |
|---|--------|--------|
| 1 | Sync OneDrive → repo canónico ejecutado | Hoy (post este append) |
| 2 | Mirror oficial restaurado | Hoy |
| 3 | Auditoría Anillo 1 (SPEC_ACTION_ENGINE + SPEC_AUDIT_MODULE) | Próxima sesión, misma metodología iterativa |
| 4 | Auditoría Anillo 2 (3 SPECs Composición) post Anillo 1 | A definir |
| 5 | Resolución de 3 deudas residuales del Anillo 2 | Durante auditoría Anillo 2 |

---

**Aprobador:** CEO (Álvaro)
**Origen del proceso:** sesión Cowork "MWT Knowledge" 2026-04-28
**Stack del proceso:** ChatGPT 5.5 + Kimi K2.6 (auditores) · Gemini
(facilitador decisiones CEO) · Claude Sonnet 4.6 en Cowork (consolidador
+ editor del CORE)
