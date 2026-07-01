# PROMPT DE RE-PREGUNTA v2 — User Admin + Directory Sync + Knowledge Flow en FaberLoom

**Fecha:** 2026-04-19
**Destinatario:** mismo auditor (Principal PM/Arquitecto SaaS) que respondió v1.
**Pegá este prompt a continuación de su respuesta v1 para que itere con disciplina de frontera.**

---

## Calibración al auditor

Buena cabeza estratégica. Ordenaste el problema y trajiste precedencias útiles. Pero sobreextendiste el scope: cambiaste el enunciado de la pregunta (4 niveles → 4+1), introdujiste roles nuevos no decididos (`Dept Manager`, `Knowledge Reviewer`) y estrechaste P12 sin justificarlo contra el diseño vigente. En v2 necesito **disciplina de frontera**: separá lo ya decidido de lo que estás proponiendo, mapeá cualquier concepto nuevo al modelo actual, y bajá el diseño a una **beta slice mínima de 6-8 semanas**. Menos ambición lateral, más bisturí.

---

## Calificación por sección (recalibrada)

| Sección | Nota | Semáforo | Razón |
|---|---|---|---|
| §1 Veredicto rápido | **7.0** | 🟡 | Dirección correcta y detección del riesgo de mezclar conocimiento de cliente. Pero cambiaste el marco del problema antes de resolver la pregunta original. Eso es falta de disciplina, no "buena dirección". |
| §2 Modelo de identidad | **8.1** | 🟢 | OIDC-first para PYME fue pragmático. Falta lifecycle completo: invite, active, suspended, deprovisioned, merged, orphaned. |
| §3 Flujo de conocimiento | **8.7** | 🟢 | La parte más sólida: precedencias, promote-up, límites de sharing. Pero mezclaste `object scope` sin mapearlo al modelo vigente (`AgentSpec · AgentRuntime · AgentMemory`). |
| §4 Matriz de governance | **5.8** | 🔴 | Metiste dos roles no decididos. No es "borrador útil"; es respuesta a una pregunta que no te hice. Reescribir comprimida a los 3 roles actuales. |
| §5 UI implicada | **7.8** | 🟢 | North star razonable. Para v1 beta huele a consola de gobierno más pesada que el ICP. |
| §6 Riesgos LATAM PYME | **5.5** | 🔴 | Señalaste privacidad, adopción y costo en prosa. No los bajaste a decisión producto concreta por país/flujo/dato. Reescribir con tabla accionable. |
| §7 Decisiones del CEO | **9.0** | 🟢 | Muy accionable. Separó bloqueante de opcional. |
| §8 Qué NO hacer en v1 | **8.6** | 🟢 | Buen antídoto contra over-engineering. Algunas prohibiciones son más fuertes que la evidencia disponible. |

**Calificación global v1: 7.5/10.** Entrá a v2 con hambre, no con autocomplacencia.

---

## Contradicciones con el diseño vigente de FaberLoom

Pocas contradicciones duras porque el prompt v1 marcó estas tres áreas como gap sin spec. Mucho de lo que propusiste no contradice un freeze; propone diseño nuevo. Pero hay que explicitarlo para no confundir "propuesta" con "auditoría":

**1. Taxonomía 4 niveles vs 4+1.** El enunciado fija 4 niveles (`global / org / depto / user`). Vos propusiste `4+1` con `object scope`. No contradice freeze, pero cambia el marco antes de resolver la pregunta original. Necesito saber si 4+1 es para v1 beta o v1.5.

**2. Roles actuales vs roles nuevos.** Hoy hay `Tenant Owner · Admin · Operator`, y explícitamente "sin jerarquía más fina". Propusiste agregar `Dept Manager` y `Knowledge Reviewer`. Eso sí choca con el estado actual. Puede ser correcto, pero es cambio de modelo, no auditoría.

**3. P12 cross-skill.** El diseño actual dice "propagación cross-skill con checkbox por skill impactado". Vos propusiste auto solo dentro de mismo scope + mismo skill cluster, y review si cruza cluster. Eso estrecha la semántica. Justificar por qué es necesario.

**4. Tres objetos vs `object scope` no mapeado.** Los objetos base son `AgentSpec · AgentRuntime · AgentMemory`. Abriste una dimensión válida con `object scope`, pero no explicaste si vive en `AgentMemory`, en entidades de negocio aparte, o como ACL overlay externo. Necesito el mapping técnico explícito.

**5. Directory corrupto / fallback.** Propusiste "directory manda identidad; FaberLoom manda autorización" como regla. Válida. Pero no cubriste: ¿qué pasa cuando el directory está caído, mal configurado, o el cliente pierde acceso a su tenant Entra ID? ¿Auth fallback? ¿Emergency admin? ¿Modo offline? Sin eso, la regla es frágil.

---

## Re-preguntas por sección

### §1 — Veredicto rápido

1. ¿`object scope` es realmente parte del modelo de conocimiento o es una capa aparte de contexto comercial/CRM?
2. Si mantenemos 4 niveles en v1, ¿qué dolores concretos aparecen en los primeros 3 design partners por no tener `object scope`?
3. ¿Cuál es el criterio para decidir si "cliente/cuenta/oportunidad" merece ser scope formal y no solo metadata + ACL?
4. ¿Tu recomendación 4+1 aplica ya en beta o la ves como v1.5?
5. ¿Qué señales te harían volver de 4+1 a 4 puros?

### §2 — Modelo de identidad

1. ¿Cuál es el state machine exacto del usuario: `invited → active → suspended → deprovisioned → merged → orphaned`? Dame los eventos que gatillan cada transición.
2. Cuando un usuario pasa de manual a synced, ¿cómo resolvés merge, rollback y auditoría si el admin se equivoca?
3. ¿Qué campos exactos son inmutables, cuáles son synced desde directory y cuáles son local override?
4. ¿Cómo modelás offboarding cuando el usuario tenía knowledge user-private, credenciales personales y aprendizaje candidato?
5. ¿Qué harías si el cliente usa Microsoft para login pero mantiene estructura comercial fuera del directory?
6. **[NUEVO]** Dame el **ERD mínimo** (tablas + FKs + índices) para `user`, `user_sync_state`, `membership`, `override_flags`. No prosa — estructura.
7. **[NUEVO]** Si v1 es Supabase RLS: ¿cómo resolvés policy con 4 niveles + merge state sin explosión combinatoria de RLS policies? ¿O necesitás policy engine externo (OPA / Cedar)? Recomendación directa, no lista neutral.
8. **[NUEVO]** Directory caído / corrupto / cliente pierde acceso a Entra ID: ¿emergency admin? ¿auth fallback? ¿modo offline? ¿cómo recuperás la org sin que FaberLoom se convierta en punto único de falla?

### §3 — Flujo de conocimiento

1. ¿Dónde vive técnicamente cada overlay: tablas separadas, metadata en vector docs, o policy engine aparte?
2. ¿Cómo se explica al usuario final por qué ganó una regla de depto sobre una de org sin volver la UI un expediente judicial?
3. ¿Tu precedencia cambia por tipo de skill o es universal para todos?
4. ¿Cómo se hace rollback de una promoción `user → depto → org` sin dejar embeddings zombies?
5. ¿Qué pruebas de leakage proponés para validar P13 y el sharing intra-org antes de salir a beta?
6. **[NUEVO]** Con 4 overlays compuestos + ACL + pgvector retrieval: ¿cuántas queries por prompt del usuario? ¿Qué cacheás y a qué TTL? Dame el worst case en ms, no en intuición.
7. **[NUEVO]** Migration path: si después decidimos pasar de 4 a 4+1 (tu propuesta), ¿qué pasa con el conocimiento ya indexado? ¿Backfill completo, dual-read, reindex incremental? ¿Puede hacerse zero-downtime?
8. **[NUEVO]** Mapeo técnico de `object scope` al modelo actual: ¿vive en `AgentMemory` con un tag, en una tabla `business_entity` aparte, o en el CRM externo consultado via connector? Una opción concreta, no tres.

### §4 — Matriz de governance (reescribir con disciplina)

1. Si no agregamos roles nuevos en v1, ¿cómo comprimís tu matriz a solo `Tenant Owner / Admin / Operator` sin perder control?
2. ¿Qué permisos son absolutamente bloqueantes para `Operator` y por qué?
3. ¿`Knowledge Reviewer` tiene que ser rol formal o alcanza con permiso granular por feature (ej. `can_approve_promotion = true` sobre un Admin)?
4. ¿Cómo evitás que `Admin` termine siendo superusuario de todo y destruya el principio de private-by-default?
5. ¿Qué permisos deberían ser temporales y delegables (ej. "Operator puede aprobar hasta fin de mes mientras el CEO está de viaje")?

### §5 — UI implicada

1. ¿Cuáles 2 pantallas son imprescindibles para beta y cuáles deberían esperar?
2. ¿El "Overlay Resolver" vive en Admin Panel, en consola del agente, o en ambos?
3. ¿Cómo simplificás "Org Structure + Identity + Sharing + Promotions" para un CEO no técnico?
4. ¿Qué parte del audit log debe ser legible para negocio y qué parte solo para soporte interno?
5. ¿Cómo harías que la UI refleje P11/P12 sin meterle al usuario un diagrama de red eléctrica?
6. **[NUEVO]** Test de comprensibilidad: la matriz rol × scope × permiso tiene potencialmente ≥60 celdas. ¿Progressive disclosure, o renunciás a la matriz y usás otro patrón UX? Decidí cuál.
7. **[NUEVO]** **Time-to-first-value.** Flujo end-to-end: CEO firma → primer draft útil. ¿Cuántos pasos? ¿Qué pasos son skippables? Dame el **número de clicks objetivo** (target numérico, no "pocos").
8. **[NUEVO]** UX de error, no de configuración. El admin se equivocó: compartió algo que no debía, o promovió un patrón que rompe tono. ¿Cómo lo detecta y lo revierte en ≤3 clicks? ¿Qué visualización da confianza de que el rollback fue completo?

### §6 — Riesgos LATAM PYME (reescribir en tabla accionable)

1. ¿Qué **tres países** deberíamos usar como baseline regulatorio para v1 y por qué? (No "todos" — tres, ordenados.)
2. ¿Qué categorías de datos te obligan a pedir consentimiento explícito versus interés legítimo o contrato?
3. ¿Qué cambia si el conocimiento incluye conversaciones con clientes versus solo artefactos internos?
4. ¿Cuál es el mínimo legal-operativo aceptable para beta: DPA, retention policy, export/delete, audit log? Lista concreta.
5. ¿Qué workaround sí tolerarías 90 días y cuál te negás a tolerar aunque atrase el launch?
6. **[NUEVO]** Reescribí §6 como **tabla**: `[país × regulación × requisito técnico × decisión producto v1 × costo estimado]`. Prosa = score 5.5. Tabla = score 8+.

### §7 — Decisiones del CEO

1. De tus 10 decisiones: **marcá cuáles 3 bloquean mockups y cuáles 3 bloquean backend**. Son listas distintas — no me las mezcles.
2. ¿En qué orden las tomarías para evitar retrabajo de producto y backend?
3. ¿Qué decisión requiere **validación con design partners** antes de cerrarla, y cuál podés cerrar con solo criterio arquitectónico?
4. ¿Cuál de tus recomendaciones tiene más riesgo de estar sobrecalibrada a enterprise tools?
5. ¿Cuál aceptarías dejar abierta hasta después del primer piloto pagado?
6. **[NUEVO]** Para cada una de las 10: ¿es **one-way-door** (costosa de revertir) o **two-way-door** (reversible en ≤2 semanas)? Esto cambia cuáles tomamos hoy sin más info y cuáles esperan evidencia.

### §8 — Qué NO hacer en v1

1. ¿Cuáles de tus "NO hacer" son **absolutos** y cuáles son solo **"no hacer todavía"**? Marcalos.
2. ¿Podría existir una versión limitada de auto-share intra-depto en beta cerrada con opt-in explícito?
3. ¿Qué **mínimo de policy engine** sí necesitás aunque digas "no construyas ABAC bonito"? Sin ese mínimo, ¿cuándo quiebra?
4. ¿Cuál es la tentación más peligrosa entre roles, scopes, SCIM y propagation? Una, no tres.
5. ¿Qué evidencia concreta te haría cambiar de postura y adelantar una de esas piezas a v1?

---

## Acoplamiento con billing (pregunta parcial — responder sin extenderse)

User admin + knowledge flow acoplan con el modelo de facturación. No te pido resolver billing completo (es otra ronda), pero sí admitir el acople para que v2 no diseñe algo que se caiga cuando agreguemos precio:

**A. Seat counting y directory sync.** Si sincronizo M365 con 200 empleados pero solo 20 usan FaberLoom activamente: ¿seats = 20, 200, o MAU? ¿Cómo lo verifica el cliente sin que parezca letra chica? Recomendación directa.

**B. Pricing gate por capacidad de admin.** ¿Qué nivel de directory sync está en free vs paid? (Ej. OIDC básico free / SCIM + auto-deprovision paid / Audit log exportable enterprise.) Dame la línea de corte concreta, no filosofía.

**C. Churn signal desde admin panel.** ¿Qué **tres comportamientos** de administración predicen cancelación? (Ej. "0 promotions en 30 días", "admin no abrió audit log nunca", "connector mal configurado sin remediar". Tres indicadores accionables para Customer Success.)

---

## Gaps nuevos surgidos al leer v1

1. **Offboarding y ownership post-salida.** Qué pasa con knowledge user-private, learning candidate, firmas, preferencias y credenciales cuando alguien sale. Incluir retention y transferencia a manager.
2. **Identity lifecycle completo.** No basta con manual vs synced; falta merge, unmerge, suspend, restore y orphan handling.
3. **Knowledge sensitivity taxonomy.** Hoy hablamos por scope, pero no por sensibilidad: público interno / restringido / confidencial / PII / canal-secret. Taxonomía ortogonal al scope.
4. **Rollback y expiración de conocimiento promovido.** Si un patrón promoted-up deja de servir, ¿cómo se retira sin romper trazabilidad ni retrieval? TTL o revalidation?
5. **Mapping técnico entre `object scope` y modelo actual.** Si existe, vive en CRM objects, en `AgentMemory`, en ACL tags, o en otra entidad. Una opción.
6. **Redacción y sanitización antes de promover.** Pipeline explícito para quitar PII, secretos y señales personales antes de compartir aprendizaje entre scopes.
7. **Testing formal de leakage.** No solo RLS; casos de prueba multi-tenant, intra-org, cross-dept y cross-skill. P13 inquebrantable = suite de tests específica, no buena fe.
8. **Audit lineage entendible por humanos.** No solo log técnico; "por qué se compartió / quién aprobó / desde qué scope subió". Legible para el CEO.
9. **Distinción entre conocimiento y configuración.** Firma, tono, formato fiscal, credenciales y políticas no necesariamente deben vivir todos en el mismo sistema de overlays. Separar explícitamente.
10. **Beta slice realista.** Propuesta brutalmente mínima: qué sí shippear en 6-8 semanas sin convertir FaberLoom en "SAP con sneakers".
11. **[NUEVO] Sandbox / preview antes de aplicar.** El admin cambia precedencia org vs depto → ¿puede previsualizar el efecto en outputs existentes antes de commit? Sin preview, el miedo al cambio paraliza la adopción.
12. **[NUEVO] Exportabilidad del conocimiento.** Si el cliente churnea, ¿se lleva su KB? ¿En qué formato (JSON, Markdown, embeddings)? ¿Con qué retention en FaberLoom post-churn? Acopla con LGPD/GDPR derecho al olvido.
13. **[NUEVO] Auditoría externa (SOC 2 / ISO 27001).** ¿Qué decisiones de hoy hacen imposible o caras estas certificaciones mañana? No es "certificar ya"; es "no pintarnos en la esquina". Lista corta de no-regrets.

---

## Restricciones para v2

- **No introduzcas más conceptos nuevos** sin mapearlos al modelo vigente (3 objetos, 3 capas de skill, 5 niveles de Autonomy Ladder, P11/P12/P13).
- **Tablas obligatorias** en §4 (governance), §6 (LATAM), §7 (decisiones one-way vs two-way).
- **ERD mínimo** en §2 (identidad).
- **Números concretos** en §3 (latencia, queries/prompt, cache TTL) y §5 (clicks to first value).
- **Recomendación directa** con el porqué. No listas neutrales de opciones.
- **Beta slice de 6-8 semanas** al final de v2: qué sí ship, qué no, qué va en v1.5, qué va en v2.0.
- Si algo sigue siendo pregunta abierta después de v2, marcalo explícitamente como `[AÚN ABIERTO — REQUIERE DATA DE DESIGN PARTNERS]` en vez de improvisar.

---

## Entregable esperado v2

Mismo formato de 8 secciones del v1, pero con:
- Secciones §4 y §6 **reescritas completas** (no solo parchadas).
- Nuevas sub-respuestas numeradas para las preguntas marcadas **[NUEVO]** en cada §.
- Sección "Acoplamiento con billing" respondida en ≤300 palabras.
- Anexo final: **"Beta slice v1 — 6-8 semanas"**, una página máximo, bulleted, con fechas tentativas y owner sugerido.

**Score objetivo para v2: ≥8.8/10.** Menos que eso y vamos a v3.
