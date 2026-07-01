---
id: ENT_FB_USER_LEARNING_MODEL_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma
type: entity
stamp: VIGENTE 2026-05-02
fecha: 2026-05-02
agente: Cowork (redaccion) + CEO (correccion conceptual) + ChatGPT (auditoria R5)
aplica_a: [FaberLoom]
implementa: SPEC_FB_KNOWLEDGE_RIVER_v1.1 (capa USUARIO L0-L2)
relacionado_con:
  - ENT_FB_COMMITTEE_OPERATING_MODEL_v1 (capa ORGANIZACIONAL · rol distinto)
  - ENT_FB_CURATOR_OPERATING_MODEL_v1 (DEPRECATED · sustituido por estos 2)
  - SPEC_FB_KNOWLEDGE_RIVER_v1.1 (modelo 2 capas)
  - POL_FB_KR_PRIVACY_TIERS_v1.1 (sin k-anon en capa usuario)
  - ENT_FB_RFQ_REPLAY_SET_v1.1 (2 etapas validacion)
origen: correccion error conceptual CEO 2026-05-02 + ChatGPT R5
---

# ENT_FB_USER_LEARNING_MODEL_v1
## Modelo de aprendizaje personal del AM con sus agentes (CAPA 1 USUARIO)

## 1. Proposito

Define la **capa 1 del aprendizaje** · curaduria personal del AM con sus agentes individuales. Esta capa es independiente de la capa 2 organizacional (gobernada por `ENT_FB_COMMITTEE_OPERATING_MODEL_v1`).

Sin esta separacion canonizada, mezclamos curaduria personal diaria con comite organizacional · introducimos falsos bloqueos de privacidad · UI equivocada · roles contaminados.

> **Insight CEO 2026-05-02:** "el usuario siempre esta agregando conocimiento y se le informa de patrones y nuevas cosas que se han aprendido y el tiene un proceso de curado que el itera y se integra y de lo que el integra es lo que va al comite para revisar que de lo que aprendio la organizacion puede ser considerado para toda la comunidad. uno es el usuario y otro la organizacion."

> **Insight ChatGPT R5:** "El error anterior era tratar 'curador' como si fuera un rol universal. No lo es. Hay curaduria personal y hay gobernanza organizacional. Usar la misma palabra para ambas capas crea controles falsos y UI incorrecta."

## 2. Diferencia con CAPA 2 organizacional

| Aspecto | CAPA 1 USUARIO (este archivo) | CAPA 2 ORGANIZACION (ENT_FB_COMMITTEE) |
|---|---|---|
| Actor | AM individual | Comite (curador + reviewers) |
| Decide | Que aprende SU agente personal | Que se vuelve patron organizacional |
| Cadencia | AM-driven · cuando quiera | Semanal/mensual estructurada |
| Memoria target | L2 episodica privada | L3 colectivo / L4 firmado |
| Privacidad | Sin k-anon · es SU propio data | k-anon ≥5 obligatorio |
| Visibilidad | Solo el AM ve sus aprendizajes | Patrones agregados cross-AM |
| UI | Mesa de Control (AM-view) | Pantalla rol Gobernanza separada |
| Resultado | Su agente mejora para SU uso | Pattern organizacional cross-AM |

## 3. Como funciona la curaduria personal

### 3.1 Deteccion automatica de patterns

Mientras el AM usa sus agentes (`@cotizador` · `@asistente_legal` · etc) cada interaccion produce signals:
- AM aprueba draft sin edicion → signal `accepted_clean`
- AM edita draft >20% texto → signal `edit_heavy` con diff
- AM rechaza draft con razon tipificada → signal `rejected` + razon
- AM corrige output via iteracion en AgentConsole → signal `iteration_correction`

Sistema detecta cuando un signal se REPITE en >=3 ocasiones similares · marca como `pattern_candidate_personal`.

### 3.2 Notificacion al AM

Notificacion semanal discreta (footer-zone Mesa de Control · NO interrumpe operacion):

```
"Aprendiste 3 cosas esta semana"
[ Revisar mis aprendizajes ]
```

Tipo `lo que importa hoy` de Things 3 · sin urgencia · sin coral.

### 3.3 Vista de revision personal del AM

Click → modal o pantalla con los patterns detectados en lenguaje del AM:

```
Esta semana corregiste 3 patrones en @cotizador:

  - Industrias del Norte siempre pide validez 30d (no 15d default)
    Detectado en 4 cotizaciones · ultima 02-may
    [ Aplicar a mi agente ]   [ Editar antes ]   [ Ignorar ]

  - BC-7240 requiere puntera composite cuando uso es petrolero
    Detectado en 3 cotizaciones · ultima 30-abr
    [ Aplicar a mi agente ]   [ Editar antes ]   [ Ignorar ]

  - Construsur pidio descuento 12% en pedidos >300 pares
    Detectado en 3 cotizaciones · ultima 01-may
    [ Aplicar a mi agente ]   [ Editar antes ]   [ Ignorar ]
```

NO aparece: k-anon · L3 · `@CURADOR` · `ACPT N` · badges comite.

### 3.4 Acciones del AM

Para cada pattern · 3 opciones:

| Accion | Resultado |
|---|---|
| **Aplicar a mi agente** | Pattern entra a memoria L2 episodica del AM · agente ajusta default para futuras tareas similares |
| **Editar antes** | AM modifica el pattern (refine wording · ajustar threshold · etc) · luego aplica |
| **Ignorar** | Pattern descartado · sistema NO vuelve a sugerirlo (a menos que aparezca con frecuencia mayor o variante distinta) |

### 3.5 Resultado · memoria L2 episodica privada

Patterns aplicados quedan en L2 (privada del AM):
- Solo el AM ve estos patterns
- NO cross-AM
- NO cross-tenant
- NO k-anon (es SU data · no tiene sentido anonimizar)
- Privacy tier: PRIVATE_RAW para AM-identificable + TENANT_DERIVED para abstraccion del pattern

### 3.6 Rollback personal

AM puede deshacer cualquier pattern aplicado:
- Vista "patrones aplicados" en config personal
- Click "deshacer" → pattern vuelve a `inactive` · agente vuelve a comportamiento default
- Cambio versionado · audit trail mantenido

## 4. Que NUNCA hace la curaduria personal

1. **No promueve patterns cross-AM.** Eso es responsabilidad del comite (capa 2).
2. **No aplica k-anon.** Es data del AM · no requiere anonimizacion.
3. **No requiere comite review.** AM es soberano sobre SU agente personal.
4. **No bloquea operacion del AM.** Si AM ignora todos los aprendizajes · cotizaciones siguen normales.
5. **No comparte patterns con otros AMs** sin pasar por capa 2 organizacional.
6. **No expone L3+ ni glossary k-anon ni indices firmados.** Eso es UI de comite.

## 5. Transicion CAPA 1 → CAPA 2 (cuando aplica)

Patterns aplicados por AMs individualmente quedan en L2. **El sistema NO los promueve auto a L3.** Promotion es responsabilidad del comite (capa 2):

```
1. AM1 aplica pattern X a su agente (L2)
2. AM2 aplica pattern X (similar) a su agente (L2)
3. AM3 aplica pattern X (similar) a su agente (L2)
4. AM4 aplica pattern X (similar) a su agente (L2)
5. AM5 aplica pattern X (similar) a su agente (L2)
   ↓
   (sistema detecta cross-AM count >=5 · k-anon ≥5 cumplido)
   ↓
6. Pattern aparece como CANDIDATE en pantalla del comite (capa 2)
7. Comite decide: promote a L3 organizacional · O reject · O diferir
```

En MWT v1 con 1 AM (Alvaro) · no se llega a k-anon ≥5 · todos los patterns quedan en L2 · capa 2 esta dormida hasta multi-AM.

## 6. Estructura YAML del config personal

```yaml
user_learning_config:
  user_id: alvaro@mwt.cr
  agents:
    cotizador:
      detection_threshold: 3  # n veces el pattern se repite
      notification_cadence: weekly
      auto_archive_ignored_after_days: 30
    asistente_legal:
      detection_threshold: 5  # mas conservador en legal
      notification_cadence: weekly
      auto_archive_ignored_after_days: 60

  patterns_active:
    - pattern_id: pat_001
      agent: cotizador
      summary: "Industrias del Norte: validez 30d default (no 15d)"
      detected_count: 4
      first_detected: 2026-04-25
      last_detected: 2026-05-02
      applied_at: 2026-05-02T14:23:11Z
      privacy_tier: PRIVATE_RAW
      versioned_in_l2: l2_pat_001_v1

  patterns_ignored:
    - pattern_id: pat_007
      agent: cotizador
      summary: "Aceros Penoles: respuesta en mayusculas"
      ignored_at: 2026-04-30T09:15:00Z
      reason: "no es pattern · es preferencia personal cliente"
```

## 7. Reglas inquebrantables

1. **AM es soberano sobre SU agente.** Curaduria personal NO requiere aprobacion comite.
2. **Sin k-anon en capa 1.** Es SU data · k-anon NO aplica.
3. **Sin L3+ visible al AM** en su flujo personal.
4. **Patterns aplicados son rollback-able** · cambio versionado.
5. **Promotion a L3 es responsabilidad COMITE** · NO sistema auto.
6. **Notificacion no bloquea operacion.** Footer-zone discreto · click opcional.
7. **Lenguaje en patterns es del AM** · no jerga sistema (NO "@CURADOR ACPT N · L3 · k-anon").
8. **MWT v1 con 1 AM** · capa 2 dormida hasta multi-AM · todos los patterns quedan en L2.

## 8. Implicaciones UI · Mesa de Control AM-view

**Eliminar del AM-view (correccion mock v5):**
- `@CURADOR · ACPT N`
- `L3` visible
- `k-anon ≥5`
- Badges promocion organizacional
- Lenguaje "aprobacion colectiva"
- Pool L3 con k-anon visible

**Reemplazar con:**
- "Aprendiste N cosas esta semana"
- "Detectado en tus ultimas cotizaciones"
- "Aplicar a mi agente"
- "Editar antes"
- "Ignorar"
- "Memoria personal L2"
- "Visible solo para ti"
- "Pendiente de revision personal"

UI separada (rol Gobernanza · `curator-workspace.html` futuro) · es donde aparece la capa 2.

## 9. Pendientes [PENDIENTE — NO INVENTAR]

- Algoritmo concreto de deteccion de patterns (similarity threshold · clustering) → diferido SPEC implementacion
- Schema YAML completo del config personal → diferido SPEC implementacion
- UI Mesa de Control personal `Aprendizaje sugerido` → en mock v6 (refactor pendiente)
- Integracion L2 → vector store del agente · cuando aplicar pattern → diferido SPEC tecnico
- Edge case: AM aplica pattern · luego cliente cambia (Industrias del Norte ahora pide validez 60d) · como detectar contradiccion → diferido v1.1

## NO IMPLICA (R4 bonus 5%/50%)

`ENT_FB_USER_LEARNING_MODEL_v1` **NO implica gobernanza organizacional**. La curaduria personal del AM es soberana sobre SU agente. Cualquier promocion cross-AM · cross-tenant · k-anon · privacy review · es responsabilidad del comite organizacional (`ENT_FB_COMMITTEE_OPERATING_MODEL_v1`). NO confundir capas.

## Changelog
- 2026-05-02 v1.0 VIGENTE: Creacion inicial post correccion error conceptual CEO + auditoria R5 ChatGPT. Define capa 1 USUARIO con curaduria personal del AM (deteccion automatica patterns · notificacion semanal discreta · vista revision personal · 3 acciones aplicar/editar/ignorar · resultado L2 episodica privada · rollback personal). Diferenciacion clara de capa 2 organizacional. Reglas inquebrantables: AM soberano · sin k-anon · sin L3 visible · MWT v1 capa 2 dormida hasta multi-AM. UI fixes obligatorios mock v5 → v6 documentados (eliminar @CURADOR · ACPT N · L3 · k-anon del AM-view · reemplazar con lenguaje personal). NO implica gobernanza organizacional.

## Stamp
VIGENTE 2026-05-02 — Capa 1 del modelo aprendizaje 2 capas. Correccion error conceptual canonizado · separa curaduria personal AM de gobernanza organizacional comite. Sin esta canonizacion · UI mezcla niveles · roles contaminados · controles falsos.
