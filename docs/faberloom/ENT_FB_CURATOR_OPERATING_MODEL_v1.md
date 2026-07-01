---
id: ENT_FB_CURATOR_OPERATING_MODEL_v1
version: 1.0
status: DEPRECATED
visibility: [INTERNAL]
domain: Plataforma
type: entity
stamp: DEPRECATED 2026-05-02 — sustituido por 2 archivos (capa usuario + capa organizacion)
fecha: 2026-05-01 (creado) · 2026-05-02 (deprecated)
agente: Cowork (redaccion) + CEO (decisiones) + ChatGPT (auditoria R2+R4)
aplica_a: [FaberLoom]
implementa: SPEC_FB_KNOWLEDGE_RIVER_v1 (rol curador 3 modos gobernanza)
status_motivo: |
  ChatGPT R5 + CEO 2026-05-02 detectaron error conceptual:
  este archivo mezclaba curaduria personal del AM con gobernanza organizacional del comite.
  Son 2 capas distintas que necesitan separarse.
sustituido_por:
  - ENT_FB_USER_LEARNING_MODEL_v1 (capa 1 USUARIO · curaduria personal AM)
  - ENT_FB_COMMITTEE_OPERATING_MODEL_v1 (capa 2 ORGANIZACION · gobernanza colegiada)
relacionado_con:
  - SPEC_FB_KNOWLEDGE_RIVER_v1.1 (modelo 2 capas canonizado · L0-L2 usuario · L3-L4 organizacion)
  - ENT_FB_RFQ_REPLAY_SET_v1.1 (2 etapas validacion AM + comite)
  - POL_FB_KR_PRIVACY_TIERS_v1.1 (k-anon SOLO en transiciones L2→L3 · NO capa 1)
---

# ENT_FB_CURATOR_OPERATING_MODEL_v1 [DEPRECATED 2026-05-02]
## Modelo operativo del rol Curador organizacional

> **DEPRECATED · NO USAR.** Este archivo fue sustituido por la separacion en 2 capas tras correccion error conceptual CEO + auditoria ChatGPT R5:
>
> - **Capa 1 USUARIO** · `ENT_FB_USER_LEARNING_MODEL_v1` · curaduria personal del AM con SUS agentes · sin k-anon · L2 episodica privada
> - **Capa 2 ORGANIZACION** · `ENT_FB_COMMITTEE_OPERATING_MODEL_v1` · gobernanza colegiada del comite · k-anon ≥5 + 7 checks privacy · L3 colectivo + L4 firmado
>
> El error conceptual era tratar "curador" como rol universal · cuando en realidad hay curaduria personal y gobernanza organizacional · son cosas distintas.
>
> Contenido original abajo se preserva para referencia historica · NO se usa para implementacion. Sprint 1 implementa los 2 archivos sustitutos.

## 1. Proposito

Define el rol Curador organizacional en cadencia + scope + decisiones + autoridad. Sin curador operacional · "el sistema acumula supersticiones con confianza estadistica" (R4). Es la diferencia entre "AI aprende" y "criterio acumulado versionado".

> **Insight ChatGPT R4:** "El moat no es tener documentos. Es tener criterio acumulado versionado: regla + evidencia + decision + resultado. Ahi FaberLoom empieza a parecer telar industrial y no carpeta compartida con cafeina."

## 2. El rol · responsabilidad

El Curador es responsable de:
- Evaluar el aprendizaje organizacional **integral** y **periodicamente** (no en tiempo real)
- Decidir que patterns se promueven · que se corrigen · que se bloquean
- Mantener consistencia entre gold samples · templates · reglas tenant-derived
- Resolver conflictos entre fuentes
- Auditar el corpus de conocimiento del tenant

El Curador **NO** es operador del AM. NO toma decisiones operativas en tiempo real. NO genera cotizaciones.

## 3. Cadencias canonicas

### 3.1 Diario · 15 min

**Cuando:** primera hora de la manana
**Que revisa:**
- Outputs criticos del dia anterior (cotizaciones · errores · escalaciones)
- Candidate samples auto-add nuevos (validar para promover o reject)
- Alertas de freshness violation o evidence gap

**Decisiones tipicas:**
- Promote candidate sample a active (si valida)
- Reject candidate (si contaminado o sesgado)
- Escalar pattern a comite semanal si requiere discusion

**Output:** entrada minima en log diario · max 15 min.

### 3.2 Semanal · 60-90 min · comite curaduria

**Cuando:** mismo dia/hora cada semana (recomendado lunes manana)
**Quienes:** Curador + AM + responsable comercial (en MWT v1: Alvaro · multi-hat · ver §5)
**Que revisa:**
- Patterns nuevos detectados en uso semanal
- Candidate samples acumulados durante la semana
- Conflictos entre fuentes (curador decide cual prevalece o escala)
- Templates que necesitan iteration
- Excepciones recurrentes que sugieren regla nueva

**Decisiones tipicas:**
- Promote/reject samples con discusion grupal
- Crear/actualizar templates
- Marcar templates obsoletos
- Resolver conflictos fuentes

**Output minimo (R4):**
```yaml
sesion_semanal:
  fecha: ISO8601
  hat_actor: CURATOR
  participantes: [emails]
  decisiones_tomadas: array<{decision_id, type, rationale}>
  samples_promovidos: array<sample_id>
  samples_rechazados: array<{sample_id, reason}>
  conflictos_abiertos: array<{conflict_id, sources, status}>
  freeze_status: enum  # on_track · at_risk · overdue
  next_review: ISO8601
```

NO acta larga. Solo lo accionable + trazable.

### 3.3 Mensual · freeze · pack memoria/templates

**Cuando:** ultimo viernes del mes
**Que se congela (R4 explicit):**
- Templates aprobados (correo · proforma · cover letter)
- Gold samples activos
- Reglas/prompts tenant-derived (compliance profile · pricing rules · sustitucion policies)
- Promociones/retiros del replay set del mes
- Candidate samples rechazados (queda registro de qué NO se aprende)

**Que NO se congela:**
- Operacion AM diaria · drafts en proceso · cotizaciones activas
- Auto-add candidates del replay set (siguen entrando)

**Resultado:** snapshot inmutable del corpus al cierre del mes · base estable para el siguiente mes.

### 3.4 Ajuste para tenants pequenos (R4 voto CEO aceptado)

Tenants chicos (1 AM · low volumen) pueden:
- Combinar diario + semanal en una sesion semanal sola (60-90 min)
- Mensual freeze obligatorio para todos · sin excepcion

Tenants grandes (>3 AM · alto volumen) deben mantener cadencia completa diaria + semanal + mensual.

## 4. Scope · 9 items que el curador toca

1. Templates de correo
2. Reglas de proforma
3. Reglas ASTM/SKU (vertical_spec_object certifications)
4. Excepciones recurrentes
5. Gold samples
6. Rechazo de ejemplos contaminados
7. **Conflictos entre fuentes** (R4 ajuste · decision explicita · ver §6)
8. Templates obsoletos
9. Patterns candidatos a cross-tenant

## 5. Cambio de hat (R4 critico)

En MWT v1 una sola persona (CEO Alvaro) cubre:
- Rol AM (operador diario)
- Rol Curador (gobernanza periodica)
- Rol CEO (decisiones estrategicas)

**Regla R4 inquebrantable:** cada decision se registra con `actor_role_at_decision`, no solo con usuario:

```yaml
decision_log_entry:
  decision_id: <uuid>
  user: alvaro@mwt.cr
  actor_role_at_decision: CURATOR  # o AM o CEO segun la decision
  decision_type: promote_sample | resolve_conflict | freeze_pack | etc
  timestamp: ISO8601
  context: {...}
```

Sin esto · auditoria futura queda confusa. Cuando MWT crezca y los roles se separen fisicamente · el log historico ya distingue por hat (no requiere refactor).

R4 explicit: "el rol curador es funcionalmente separado del rol AM. La misma persona puede ejercer ambos en tenants pequenos · pero cada decision debe registrar el hat activo."

## 6. Decisiones que toma el curador · 7 acciones canonicas

| # | Accion | Trigger |
|---|---|---|
| 1 | Promote candidate sample → active | sample valida criterios + curador aprueba |
| 2 | Reject candidate sample | datos contaminados · sesgo detectado · viola politicas |
| 3 | Crear/actualizar template | pattern recurrente justifica nuevo template |
| 4 | Marcar template obsoleto | uso cae · drift detectado · regulatorio cambia |
| 5 | **Resolver conflicto entre fuentes** (R4) | dos fuentes contradicen · curador decide cual prevalece o escala a Authority Matrix |
| 6 | Escalar a comite/CEO | decision excede autoridad del curador · requiere comercial/legal/CEO |
| 7 | Freeze mensual | ultimo viernes del mes · congela pack |

Cada accion emite audit event con SHA-chain.

## 7. Comportamiento si curador no hace freeze (R4 separacion explicit)

| Tiempo sin freeze | Comportamiento del sistema |
|---|---|
| 0-34 dias | normal · sin alerta |
| 35-59 dias | **Warning visible al AM** · "templates sin congelar 35 dias" · NO bloquea operacion |
| 60+ dias | **Bloqueo tecnico de promociones de candidate samples** · operacion AM continua normal · cotizaciones siguen · pero NO se promueven samples nuevos hasta freeze |

R4 explicit: "Bloquear solo aprendizaje/promociones · no operacion AM ni generacion de cotizaciones."

## 8. Resolver conflicto fuentes (R4 ajuste)

Cuando dos fuentes contradicen sobre el mismo dato (ej. SAP dice stock 285 vs 3PL dice 310 con delta >5%) · el curador:

1. Recibe alerta automatica del sistema
2. Decide cual fuente prevalece para el caso especifico (basado en confianza · freshness · trazabilidad)
3. Si decision excede su autoridad (ej. afecta precio/credito) → escala a Authority Matrix
4. Documenta razonamiento en log
5. Considera si el conflicto sugiere regla permanente nueva (vs decision puntual)

Output minimo:
```yaml
conflict_resolution:
  conflict_id: <uuid>
  sources_in_conflict: [source_a, source_b]
  data_field: stock | price | lead_time | etc
  decision: source_a | source_b | escalate_to_authority | manual_override
  rationale: string
  permanent_rule_proposed: boolean
  resolved_by: alvaro@mwt.cr
  hat: CURATOR
```

## 9. Herramientas del curador · pantalla rol Gobernanza

El curador opera en la pantalla del rol Gobernanza definida en SPEC_FB_KNOWLEDGE_RIVER_v1 (3 universos: Operacion · Gobernanza · Audit).

Funcionalidad minima esperada (sin entrar a SPEC UI · solo capability list):
- Vista candidate samples pendientes
- Vista conflictos abiertos
- Vista templates con su lifecycle
- Vista replay set con estados
- Boton "Freeze Pack Mensual"
- Log de decisiones del curador filtrable
- Export pack para audit externo

Mock visual referenciado: `curator-workspace.html` (entrega Claude Design v3) · pendiente refactor v4 alineado con Mesa de Control.

## 10. Moat · criterio acumulado versionado

Diferencial defendible vs ChatGPT/Notion/Linear:

| Plataforma | Modelo |
|---|---|
| ChatGPT/Notion | Memoria implicita · sin curaduria · sin trazabilidad de decisiones |
| Linear/Jira | Templates manuales · sin destilacion automatica · sin pool L3 |
| **FaberLoom** | Curaduria periodica + criterio versionado (regla + evidencia + decision + resultado) |

R4 insight: "criterio acumulado versionado" es el moat real. NO los documentos. Cada decision del curador contribuye a un activo organizacional irreproducible.

## 11. Reglas inquebrantables

1. **Curador es rol funcional · no persona.** Misma persona puede ejercer multiple hats con `actor_role_at_decision` registrado.
2. **Cadencias diaria + semanal + mensual son default.** Tenants chicos pueden combinar diaria+semanal · mensual freeze obligatorio para todos.
3. **Warning 35d · bloqueo tecnico promociones 60d.** NUNCA bloquear operacion AM.
4. **Conflicto fuentes = decision explicita** (no solo scope) · documentado con rationale.
5. **Cada decision del curador genera audit event con SHA-chain.**
6. **Promote candidate → active SIEMPRE requiere curador.** No auto-promote.
7. **Cross-tenant promotions requieren los 7 checks** (POL_FB_KR_PRIVACY_TIERS_v1).

## 12. Pendientes [PENDIENTE — NO INVENTAR]

- Pantalla curador definitiva alineada con Mesa de Control v4 → diferida a indexa-f post mock v4
- SPEC_FB_GOVERNANCE_UI_v1 (mockups + interacciones detalladas) → diferida
- Algoritmo concreto de deteccion de patterns recurrentes (sugerir regla nueva al curador) → diferida v2
- Templates pre-canonicos para curador iniciar (no empieza desde cero) → diferida indexa-f

## NO IMPLICA (R4 bonus 5%/50%)

`ENT_FB_CURATOR_OPERATING_MODEL_v1` **NO implica bloqueo operativo del AM**. El curador opera en cadencia periodica · NO interrumpe el flujo diario del AM. Si curador no hace freeze · solo se bloquean PROMOCIONES de samples · NO se bloquean cotizaciones ni drafts ni operacion AM normal.

## Changelog
- 2026-05-01 v1.0 VIGENTE: Creacion inicial post review R4. Rol curador con 3 cadencias canonicas (diaria 15min · semanal 60-90min comite · mensual freeze). 9 items en scope · 7 acciones que toma. Cambio de hat con `actor_role_at_decision` registrado para multi-rol persona (MWT v1 CEO=AM=Curador). Comportamiento freeze separado: warning 35d · bloqueo promociones 60d · NO bloqueo operacion AM. Conflicto fuentes como decision explicita con rationale. Output minimo sesion semanal definido (decisiones · samples · conflictos · freeze status). Pantalla rol Gobernanza referenciada. 7 reglas inquebrantables. Linea NO implica bloqueo operativo del AM.

## Stamp
VIGENTE 2026-05-01 — Curador como rol funcional con cadencia + scope + decisiones canonicas. Diferencia entre "AI aprende" y "criterio acumulado versionado" (R4). Hat tracking habilita multi-rol en tenants pequenos sin perder auditabilidad cuando crezcan.
