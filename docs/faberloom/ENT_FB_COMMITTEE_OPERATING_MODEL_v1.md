---
id: ENT_FB_COMMITTEE_OPERATING_MODEL_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma
type: entity
stamp: VIGENTE 2026-05-02
fecha: 2026-05-02
agente: Cowork (redaccion) + CEO (correccion conceptual) + ChatGPT (auditoria R5)
aplica_a: [FaberLoom]
sustituye: ENT_FB_CURATOR_OPERATING_MODEL_v1 (DEPRECATED · scope solo individual + organizacional mezclado · este reemplaza la parte organizacional)
implementa: SPEC_FB_KNOWLEDGE_RIVER_v1.1 (capa ORGANIZACION L3-L4)
relacionado_con:
  - ENT_FB_USER_LEARNING_MODEL_v1 (capa USUARIO L0-L2 · separada)
  - SPEC_FB_KNOWLEDGE_RIVER_v1.1 (modelo 2 capas)
  - POL_FB_KR_PRIVACY_TIERS_v1.1 (k-anon ≥5 aplica solo aqui)
  - ENT_FB_RFQ_REPLAY_SET_v1.1 (2 etapas validacion · comite valida cross-AM)
origen: correccion error conceptual CEO 2026-05-02 + ChatGPT R5
---

# ENT_FB_COMMITTEE_OPERATING_MODEL_v1
## Modelo operativo del comite organizacional (CAPA 2 ORGANIZACION)

## 1. Proposito

Define la **capa 2 del aprendizaje** · gobernanza organizacional sobre patterns que MULTIPLES AMs aplicaron en sus instancias (capa 1) y que potencialmente son organizacionales.

Sin esta separacion canonizada · curaduria personal del AM se mezcla con gobernanza colectiva. Resultado: UI confusa · controles falsos de privacidad · roles contaminados.

> **Insight CEO 2026-05-02:** "lo que el [AM] integra es lo que va al comite para revisar que de lo que aprendio la organizacion puede ser considerado para toda la comunidad."

## 2. Diferencia con CAPA 1 (ENT_FB_USER_LEARNING_MODEL_v1)

| Aspecto | CAPA 1 USUARIO | CAPA 2 ORGANIZACION (este archivo) |
|---|---|---|
| Actor | AM individual | Comite (curador + reviewers) |
| Decide | SU agente personal | Pattern organizacional cross-AM |
| Cadencia | AM-driven · cuando quiera | Semanal/mensual estructurada |
| Memoria target | L2 episodica privada | L3 colectivo / L4 firmado |
| Privacidad | Sin k-anon | k-anon ≥5 obligatorio |
| Visibilidad | Solo el AM | Patrones agregados visibles al comite |
| UI | Mesa de Control AM-view | Pantalla rol Gobernanza separada |
| Resultado | Su agente mejora | Knowledge organizacional cross-AM/cross-tenant |

## 3. El rol comite

El comite es responsable de:
- Evaluar patterns que MULTIPLES AMs integraron a sus agentes (capa 1) y promover los validos a capa 2
- Auditar el corpus de conocimiento organizacional
- Resolver conflictos entre fuentes (cuando capa 1 detecta · escala)
- Mantener consistencia entre templates · gold samples · reglas tenant-derived
- Decidir promocion a L3 colectivo y L4 indexed firmado
- Aplicar privacy reviews + 7 checks promocion

**El comite NO es operador del AM.** NO toma decisiones operativas en tiempo real. NO genera cotizaciones. NO ve el flujo personal del AM.

## 4. Composicion del comite

### 4.1 Roles minimos

- **Curador (chair)** · responsable principal · convoca sesiones · firma decisiones
- **Reviewers** · 2-3 personas con expertise relevante (compliance · pricing · operaciones · legal)
- **Auditor opcional** · participa con read-only · puede objetar pero no votar

### 4.2 En MWT v1 (1 AM operativo)

CEO Alvaro hace **multi-rol**:
- Rol AM (operador diario · capa 1)
- Rol Comite (curador + sole reviewer · capa 2)
- Rol CEO (decisiones estrategicas)

Cada decision registra `actor_role_at_decision = COMMITTEE` (NO solo usuario · ver §6).

### 4.3 En tenants grandes

Comite separado fisicamente del operador:
- Curador · gerente comercial · 1 persona
- Reviewers · analista pricing + analista compliance · 2-3 personas
- Cadencia comite es horizontal · NO bloquea operacion del AM

## 5. Cadencias del comite

### 5.1 Sesion semanal · 60-90 min · comite curaduria

**Cuando:** mismo dia/hora cada semana (lunes recomendado · post-rotacion replay set)
**Quienes:** curador + reviewers (en MWT v1: Alvaro multi-hat)
**Que revisa:**
- Patterns CANDIDATE acumulados durante la semana (de AMs aplicaron en sus L2)
- Patterns que cumplen k-anon ≥5 (multiples AMs los aplicaron a sus agentes)
- Conflictos de fuentes escalados desde capa 1
- Cambios al replay set (promote/retire/pinned_edge)
- Rechazo ejemplos contaminados detectados

**Decisiones tipicas:**
- Promote pattern a L3 colectivo · documentar rationale
- Reject pattern (no es organizacional · viola politicas · sesgo detectado)
- Diferir a sesion siguiente (necesita mas data o revision)

**Output minimo:**
```yaml
sesion_comite:
  fecha: ISO8601
  hat_actor: COMMITTEE
  participantes: [emails]
  patrones_revisados: array<{pattern_id, decision, rationale}>
  promociones_l3: array<pattern_id>
  rechazos: array<{pattern_id, reason}>
  diferidos: array<{pattern_id, next_review_date}>
  conflictos_resueltos: array<{conflict_id, resolution}>
  next_review: ISO8601
```

### 5.2 Sesion mensual · freeze pack memoria/templates

**Cuando:** ultimo viernes del mes
**Que se congela:**
- Templates aprobados (correo · proforma · cover letter)
- Gold samples activos
- Reglas/prompts tenant-derived (compliance profile · pricing rules · sustitucion policies)
- Promociones a L3 del mes
- Patterns rechazados (queda registro de que NO se aprende)

**Resultado:** snapshot inmutable del corpus organizacional al cierre del mes.

### 5.3 Cadencia para tenants chicos (R4 ajuste)

Tenants con 1-2 AMs pueden combinar:
- Sesion semanal sola (60-90 min)
- Mensual freeze obligatorio para todos · sin excepcion

## 6. Cambio de hat (R4 critico)

En MWT v1 una sola persona (CEO Alvaro) cubre:
- Rol AM (operador diario · capa 1)
- Rol Comite (gobernanza periodica · capa 2)
- Rol CEO (decisiones estrategicas)

**Regla R4 inquebrantable:** cada decision se registra con `actor_role_at_decision`:

```yaml
decision_log_entry:
  decision_id: <uuid>
  user: alvaro@mwt.cr
  actor_role_at_decision: COMMITTEE  # o AM o CEO segun la decision
  decision_type: promote_pattern_l3 | reject_pattern | freeze_pack | etc
  capa: 2  # explicit · capa 1 o capa 2
  timestamp: ISO8601
  context: {...}
```

Cuando MWT crezca y los roles se separen fisicamente · log historico ya distingue por hat (no requiere refactor).

## 7. Decisiones que toma el comite · 7 acciones canonicas

| # | Accion | Trigger |
|---|---|---|
| 1 | Promote pattern L2 → L3 | Pattern cumple k-anon ≥5 + 7 checks privacy + comite aprueba rationale |
| 2 | Reject pattern | Datos contaminados · sesgo detectado · viola politicas · NO organizacional |
| 3 | Promote pattern L3 → L4 indexed firmado | Pattern validado >=90d en L3 · cross-tenant abstraction valida · DPA firmado |
| 4 | Demote pattern L3 → archived | Pattern detectado obsoleto · regulatorio cambio · drift detectado |
| 5 | **Resolver conflicto entre fuentes** (escalado desde capa 1) | Capa 1 detecta conflicto · escala via authority matrix |
| 6 | Escalar a CEO/legal | Decision excede autoridad del comite · requiere instancia superior |
| 7 | Freeze mensual | Ultimo viernes del mes · congela pack |

Cada accion emite audit event con SHA-chain.

## 8. Que NUNCA hace el comite

1. **No interviene en curaduria personal AM.** Capa 1 es soberania del AM.
2. **No ve patterns con count <5 AMs.** k-anon ≥5 obligatorio antes de visibilidad comite.
3. **No promueve patterns sin 7 checks privacy** (privacy review · reidentification · l-diversity · secret-commercial · lineage · tenant consent · purpose compatibility).
4. **No bloquea operacion AM.** Si comite no se reune · operacion sigue normal.
5. **No reviewa cada accion del AM** · solo los CANDIDATE patterns que cumplen k-anon.

## 9. Comportamiento si comite no hace freeze (R4)

| Tiempo sin freeze | Comportamiento |
|---|---|
| 0-34 dias | Normal · sin alerta |
| 35-59 dias | **Warning visible** al curador · "templates organizacionales sin congelar 35 dias" · NO bloquea operacion |
| 60+ dias | **Bloqueo tecnico de promociones L2→L3** · operacion AM continua normal · capa 1 sigue · capa 2 promociones pausadas hasta freeze |

R4 explicit: "bloquear solo aprendizaje organizacional · no operacion AM ni capa 1 personal."

## 10. Resolver conflicto fuentes (escalado desde capa 1)

Cuando capa 1 detecta conflicto entre fuentes (ej. SAP dice stock 285 vs 3PL dice 310) · si excede autoridad del AM · escala al comite:

1. Sistema detecta conflicto · alerta al comite
2. Comite decide cual fuente prevalece para el caso especifico (basado en confianza · freshness · trazabilidad)
3. Si decision excede autoridad del comite (ej. afecta precio/credito) → escala a Authority Matrix → CEO
4. Documenta razonamiento en log
5. Considera si conflicto sugiere REGLA PERMANENTE nueva (vs decision puntual)

## 11. Herramientas del comite · pantalla rol Gobernanza

El comite opera en pantalla del rol Gobernanza definida en `SPEC_FB_KNOWLEDGE_RIVER_v1.1` (3 universos: Operacion · Gobernanza · Audit).

Funcionalidad minima esperada:
- Vista patterns CANDIDATE con k-anon ≥5 cumplido (listos para review)
- Vista conflictos abiertos escalados desde capa 1
- Vista templates con su lifecycle
- Vista replay set con estados (capa 2 valida promote)
- Boton "Freeze Pack Mensual"
- Log de decisiones del comite filtrable por actor_role_at_decision = COMMITTEE
- Export pack para audit externo

Mock visual referenciado: `curator-workspace.html` (entrega Claude Design v3) · pendiente refactor v6 alineado con Mesa de Control + separacion explicita de AM-view.

## 12. Moat · criterio acumulado versionado

Diferencial defendible vs ChatGPT/Notion/Linear:

| Plataforma | Modelo |
|---|---|
| ChatGPT/Notion | Memoria implicita · sin curaduria · sin trazabilidad |
| Linear/Jira | Templates manuales · sin destilacion · sin pool L3 |
| **FaberLoom** | 2 capas: AM soberano sobre SU agente + comite gobierna L3 organizacional con k-anon ≥5 + audit cross-tenant |

R4 insight: "criterio acumulado versionado" es el moat real · imposible replicar sin curaduria periodica + tracking decisiones + audit trail + separacion de capas.

## 13. Reglas inquebrantables

1. **Comite es rol funcional · no persona.** Misma persona puede ejercer multiple hats con `actor_role_at_decision` registrado.
2. **k-anon ≥5 obligatorio antes de visibilidad comite.** Patterns con count <5 NO entran a queue.
3. **7 checks privacy obligatorios** antes de promote L3 (privacy review · reidentification · l-diversity · secret-commercial · lineage · tenant consent · purpose compatibility).
4. **Comite NO bloquea capa 1.** Si comite no se reune · curaduria personal sigue.
5. **Cada decision genera audit event con SHA-chain.**
6. **Promote L3 → L4 requiere >=90d en L3** (estabilidad · sin reverts).
7. **Cambios al replay set requieren preservar split 40/25/25/10 + ≥30% Critical+High** (R4 inquebrantable de replay set).
8. **MWT v1 con 1 AM** · capa 2 dormida hasta multi-AM · todos los patterns de Alvaro quedan en SU L2 personal · comite no tiene patterns que revisar hasta multi-AM.

## 14. Pendientes [PENDIENTE — NO INVENTAR]

- Pantalla comite definitiva alineada con Mesa de Control v6 → diferida indexa-i post mock v6
- SPEC_FB_GOVERNANCE_UI_v1 (mockups + interacciones detalladas) → diferida
- Algoritmo concreto de deteccion de patterns recurrentes cross-AM → diferida v2
- Templates pre-canonicos para comite iniciar (no empieza desde cero) → diferida indexa-i
- Cuando MWT alcance multi-AM (Sprint 1+) · cuanto tarda hasta primer pattern cross-AM cumple k-anon ≥5 → metricas a observar

## NO IMPLICA (R4 bonus 5%/50%)

`ENT_FB_COMMITTEE_OPERATING_MODEL_v1` **NO implica intervencion en capa 1 personal**. El comite opera SOLO sobre patterns que multiples AMs aplicaron y cumplen k-anon ≥5. Curaduria personal del AM (capa 1) es soberana y NO requiere aprobacion del comite. Si comite no se reune · capa 1 sigue · operacion AM sigue · solo se pausan promociones L2→L3.

## Changelog
- 2026-05-02 v1.0 VIGENTE: Creacion inicial post correccion error conceptual CEO + auditoria R5 ChatGPT. Sustituye scope organizacional del archivo previo `ENT_FB_CURATOR_OPERATING_MODEL_v1` (DEPRECATED). Define capa 2 ORGANIZACION con comite (curador + reviewers) · 2 cadencias (semanal 60-90min · mensual freeze) · 7 acciones canonicas · 7 checks privacy promote L3 · `actor_role_at_decision = COMMITTEE` para multi-rol persona MWT v1. Comportamiento freeze: warning 35d · bloqueo promociones 60d · NO bloquea operacion AM ni capa 1. Resolver conflicto fuentes como escalation desde capa 1. 8 reglas inquebrantables incluyendo MWT v1 capa 2 dormida hasta multi-AM. NO implica intervencion en capa 1 personal.

## Stamp
VIGENTE 2026-05-02 — Capa 2 del modelo aprendizaje 2 capas. Gobierno organizacional sobre patterns cross-AM cumpliendo k-anon ≥5. Reemplaza scope organizacional del previo curator. Capa 1 personal queda en `ENT_FB_USER_LEARNING_MODEL_v1` separado.
