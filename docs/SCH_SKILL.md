# SCH_SKILL — Schema Canónico de Skills MWT
id: SCH_SKILL
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: SCH
stamp: VIGENTE — 2026-04-16
aplica_a: [SHARED]

---

## Propósito

Define la estructura obligatoria para todos los archivos `SKILL_*.md` de la KB MWT.
Todo skill debe cumplir este schema. Cualquier campo ausente es deuda técnica.

Este schema implementa la arquitectura de agentes MWT basada en tres capas:
- **AgentSpec** → lo que el skill ES (definición estática)
- **AgentRuntime** → lo que el skill HACE (rastreado en `SKILL_RUNTIME.md`)
- **AgentMemory** → lo que el skill APRENDIÓ (rastreado en `SKILL_MEM_*.md`)

---

## Estructura Obligatoria — Header

```
# SKILL_{ID} — {Nombre legible}
id: SKILL_{ID}
version: {semver}
status: {SHADOW | ACTIVE | PAUSED | DEPRECATED}
visibility: [{tier}]
domain: {Dominio} (IDX_{DOMINIO})
type: SKILL
stamp: {STATUS} — {YYYY-MM-DD}
trigger_word: {palabra-clave}
autonomy_ceiling: {PROPONE | EJECUTA_INTERNO | AUTO_NOTIFICA}
escalation_policy: {ref → POL_* o "CEO directo"}
```

### Campos de header — definiciones

**`trigger_word`**
Palabra o frase corta que el CEO escribe para activar el skill en sesión.
Convención: kebab-case, sin espacios, máximo 3 palabras.
Ejemplos: `amazon-ops`, `proforma`, `kb-audit`, `client-service`

**`autonomy_ceiling`**
Nivel máximo de autonomía que este skill puede alcanzar.
No es el nivel actual — es el techo posible. El nivel actual vive en `SKILL_RUNTIME.md`.
- `PROPONE` — siempre genera draft, nunca ejecuta sin aprobación
- `EJECUTA_INTERNO` — puede ejecutar acciones internas (KB, métricas, resúmenes) sin aprobación
- `AUTO_NOTIFICA` — puede ejecutar y notifica post-hecho (reservado para skills maduros con alto approval rate)

**`escalation_policy`**
Qué hace el skill cuando enfrenta un caso fuera de su scope o ambigüedad crítica.
Ejemplos: `CEO directo`, `ref → POL_ESCALATION`, `pausar y notificar`

---

## Estructura Obligatoria — Secciones

### ## Propósito
Una frase. Qué resuelve este skill para MWT.

### ## Contexto
Datos operativos relevantes para el agente al activarse. Máximo lo necesario — no pegar toda la KB aquí.

### ## KB refs obligatorias
Lista de archivos que el agente DEBE leer al activarse con este skill.
Formato: `- ARCHIVO_ID — razón por la que lo necesita`

### ## Capacidades
Lista numerada de lo que el skill puede hacer. Verbos concretos, no aspiraciones.

### ## Restricciones
Lista de lo que el skill NUNCA hace o SIEMPRE verifica antes de actuar.
Incluir refs a POL_ cuando aplique.

### ## State Machine
Estados operativos específicos de este skill. No genéricos — adaptar al dominio.

Formato obligatorio:
```
Estados: {estado_1} · {estado_2} · ... · {estado_n}

Transiciones:
- activado → drafting (trigger word recibido)
- drafting → awaiting_approval (output generado)
- awaiting_approval → approved (CEO confirma)
- awaiting_approval → rejected (CEO descarta)
- approved → executing (acción en curso)
- executing → completed (tarea finalizada)
- cualquier_estado → escalated (caso fuera de scope)
```

### ## Events
Eventos estructurados que este skill emite durante su ejecución.
Estos eventos alimentan el sistema de aprendizaje y el termómetro de consolidación.

Formato obligatorio:
```
- skill.activated — trigger word detectado
- draft.generated — output producido para revisión
- draft.approved — CEO confirmó sin cambios mayores
- draft.approved_with_edits — CEO confirmó con correcciones
- draft.rejected — CEO descartó el output
- kb.cited — fragmento de KB usado en respuesta
- policy.blocked — acción bloqueada por restricción
- escalated — caso derivado fuera del scope
- {evento_específico_del_skill} — descripción
```

### ## Learning Consolidation
Define qué tipos de outputs de este skill son candidatos a consolidar en AgentMemory.

Formato:
```
Candidatos a gold sample:
- {tipo de output que, si se aprueba, debe promoverse a memoria}

Candidatos a patrón:
- {corrección recurrente que indica regla implícita}

Candidatos a excepción:
- {caso borde aprobado que no encaja en reglas generales}

Trigger de consolidación: indexa-{trigger_word}
```

### ## Changelog
```
- v{n} ({YYYY-MM-DD}): {descripción del cambio}
```

---

## Ciclo de Vida de un Skill

```
SHADOW → ACTIVE → PAUSED → DEPRECATED
```

**SHADOW:** El skill existe pero solo observa. No ejecuta acciones externas.
Condición para pasar a ACTIVE: mínimo 3 ejecuciones supervisadas con approval rate > 70%.

**ACTIVE:** Operación normal. Puede ejecutar hasta su `autonomy_ceiling`.
El nivel de autonomía real se gestiona en `SKILL_RUNTIME.md`.

**PAUSED:** Suspendido temporalmente. Mantiene su memoria. No responde a trigger word.
Casos: skill en revisión, dependencia rota, excepción pendiente de resolución.

**DEPRECATED:** Fuera de uso. Memoria archivada. Trigger word desactivado.

---

## Flujo de Aprendizaje (Learning Loop)

```
1. CEO activa skill con trigger_word
       ↓
2. Sistema carga AgentSpec (este archivo) + AgentMemory (SKILL_MEM_*.md si existe)
       ↓
3. Agente ejecuta y genera outputs
       ↓
4. Outputs emiten eventos estructurados
       ↓
5. Termómetro de aprendizaje sube (outputs pendientes de consolidar)
       ↓
6. CEO presiona "Indexar Aprendizaje" (trigger: indexa-{trigger_word})
       ↓
7. Modal muestra resumen:
   · Patrones nuevos detectados
   · Correcciones recurrentes
   · Gold samples candidatos
   · Excepciones identificadas
       ↓
8. CEO confirma → consolida en SKILL_MEM_{ID}.md
   CEO edita → ajusta antes de consolidar
   CEO descarta → descarta sin escribir a memoria
       ↓
9. AgentMemory actualizado → próxima sesión arranca con ese conocimiento fijo
```

**Temperatura del termómetro:**
- 🔵 Frío (0–2 outputs): sin presión de consolidar
- 🟡 Tibio (3–5 outputs): recomendable consolidar esta semana
- 🔴 Caliente (6+ outputs): consolidar antes de próxima ejecución

---

## Relación con otros archivos

| Archivo | Relación |
|---------|----------|
| `SKILL_RUNTIME.md` | Dashboard de estado actual y métricas de todos los skills |
| `SKILL_MEM_{ID}.md` | Memoria acumulada del skill (se crea cuando hay volumen real) |
| `POL_*` | Políticas referenciadas en restricciones y escalation_policy |
| `PLB_ORCHESTRATOR` | FROZEN — define cómo los skills se coordinan con agentes |
| `IDX_{DOMINIO}` | Router del dominio al que pertenece el skill |

---

## Checklist de Validación (pre-ACTIVE)

Un skill no debe pasar de DRAFT a ACTIVE sin cumplir:

- [ ] Header completo con todos los campos obligatorios
- [ ] trigger_word único en toda la KB (no colisiona con otro skill)
- [ ] autonomy_ceiling definido y justificado
- [ ] escalation_policy referenciada
- [ ] KB refs verificadas (todos los archivos existen y están VIGENTES)
- [ ] State machine completa con transiciones
- [ ] Events definidos (mínimo los 8 estándar + específicos del skill)
- [ ] Learning Consolidation definida
- [ ] Mínimo 3 ejecuciones en SHADOW con registro en SKILL_RUNTIME.md
- [ ] Approval rate > 70% en ejecuciones SHADOW

---

Changelog:
- v1.0 (2026-04-16): Creación. Arquitectura AgentSpec/Runtime/Memory. Trigger words, state machine, learning loop con termómetro y modal de consolidación. Basado en arquitectura Faberloom adaptada a escala MWT.
