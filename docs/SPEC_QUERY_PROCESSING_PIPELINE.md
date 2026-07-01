# SPEC_QUERY_PROCESSING_PIPELINE — Pipeline de Procesamiento de Consulta
id: SPEC_QUERY_PROCESSING_PIPELINE
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: SPEC
stamp: VIGENTE — 2026-04-17
aprobador: CEO
aplica_a: [MWT, FaberLoom]

---

## Propósito

Documentar el pipeline completo que ejecuta un agente IA (Claude/Cowork como referencia,
FaberLoom como implementación propia) desde que recibe una consulta hasta que produce un
output y cierra el ciclo de aprendizaje.

Esto no es teoría — es la arquitectura observable en Cowork hoy, mapeable directamente
a los 12 principios de ARCH_AGENT_PRINCIPLES.md.

---

## VISIÓN GENERAL DEL PIPELINE

```
[CONSULTA RAW]
      ↓
  FASE 0 — Recepción + metadata
      ↓
  FASE 1 — Carga de contexto (memoria + instrucciones)
      ↓
  FASE 2 — Detección de intención + skill matching
      ↓
  FASE 3 — Carga de SK (instrucciones del skill)
      ↓
  FASE 4 — Resolución de KB (contexto de conocimiento)
      ↓
  FASE 5 — Ensamblaje del contexto efectivo
      ↓
  FASE 6 — Generación con constraints activos
      ↓
  FASE 7 — Output + gate humano
      ↓
  FASE 8 — Ciclo de aprendizaje (si aplica)
      ↓
[MEMORIA ACTUALIZADA]
```

---

## FASE 0 — Recepción + Metadata

### Qué ocurre
El sistema recibe el texto crudo del usuario junto con metadata de contexto:
- Fecha y hora actuales (inyectadas automáticamente)
- Identificador del usuario / organización
- Historial de conversación activa (ventana de contexto)
- Variables de entorno del workspace (modelo, sesión, directorio)

### En Cowork (observable)
```
env: {
  date: "2026-04-17",
  model: "claude-sonnet-4-6",
  session_id: "confident-cool-johnson",
  workspace: "/sessions/.../mnt/MWT KB"
}
user_preferences: [idioma, tono, stack, comportamiento esperado]
```

### En FaberLoom (target)
```
AgentRuntime.last_trigger = "timestamp"
AgentRuntime.session_context = {org_id, user_id, canal, idioma}
AgentRuntime.estado = "receiving"
```

---

## FASE 1 — Carga de Contexto (Memoria + Instrucciones del Proyecto)

### Qué ocurre
Antes de leer la consulta, el agente carga su "identidad operativa":

**1a — CLAUDE.md / Instrucciones del proyecto**
El archivo de instrucciones del workspace se inyecta como contexto de sistema.
Contiene: reglas inquebrantables, navegación de la KB, taxonomía, scopes de agente,
convenciones, tech names que no se traducen.

**1b — MEMORY.md (índice de memoria)**
Se lee el índice de memorias persistentes. Cada entrada es un puntero a un archivo.
El sistema evalúa cuáles son relevantes para la consulta actual.

**1c — Archivos de memoria relevantes**
Solo los archivos cuya descripción en MEMORY.md coincide con el tema de la consulta
son cargados completamente. En el screenshot visible:
- `project_faberloom_architecture.md` → cargado porque la consulta toca agentes
- `project_faberloom_agents_design.md` → cargado porque toca diseño de agentes

**Principio activado: P2 — Contexto mínimo y exacto.**
No se carga toda la memoria — solo lo declarado como relevante.

### En Cowork (observable)
```
[Memoria leída] Project faberloom architecture
[Memoria leída] Project faberloom agents design
```

### En FaberLoom (target)
```
AgentSpec.kb_refs → lista de archivos a cargar
AgentMemory.gold_samples → ejemplos aprobados del skill
AgentMemory.patrones → reglas derivadas de correcciones previas
AgentMemory.sender_profiles → si la consulta involucra un remitente conocido
```

---

## FASE 2 — Detección de Intención + Skill Matching

### Qué ocurre
El sistema analiza la consulta e identifica:

**2a — ¿Es conversación simple o tarea compleja?**
- Conversación simple → respuesta directa, no se activa skill
- Tarea compleja → verificar si existe un skill que la resuelva mejor

**2b — Matching de skill**
Se compara la consulta contra la lista de skills disponibles usando:
- `trigger_word` exacto (ej: "copy", "proforma", "forecast")
- Descripción semántica del skill (ej: "analiza transcripciones de ventas")
- Patrones de invocación implícita (ej: "dame un email para X" → SKILL_HUMANIZE_COMMS)

**2c — ¿Clarificación necesaria?**
Si la consulta es ambigua o subespecificada, el sistema puede preguntar antes de
activar el skill. Esto evita generar output con supuestos incorrectos.

**Principio activado: P7 — State machine explícita.**
Estado pasa de `receiving` → `resolving_intent`.

### En Cowork (observable)
```
[Lista de skills disponibles inyectada en system prompt]
[Evaluación: ¿coincide trigger_word? ¿coincide descripción?]
→ Si match → Skill tool invocado
```

### En FaberLoom (target)
```
Clasificador de intención evalúa:
  trigger_word exacto         → score 1.0
  keyword en descripción      → score 0.7
  contexto implícito          → score 0.5
Si score > 0.6 → cargar skill
Si score ambiguo → preguntar
```

---

## FASE 3 — Carga del Skill (AgentSpec efectivo)

### Qué ocurre
Al activarse un skill, el sistema carga el archivo `SKILL_*.md` correspondiente.
Este archivo contiene:

```
trigger_word          → cómo se activa
role                  → identidad del agente en este skill
objective             → qué produce
autonomy_ceiling      → máximo nivel de autonomía posible
kb_refs               → qué conocimiento necesita (declarado, no todo)
state_machine         → estados operativos de este skill
events                → qué eventos emite
learning_consolidation → qué outputs califican como memoria
output_format         → estructura exacta del output esperado
constraints           → qué no puede hacer (limits hardcoded)
escalation_policy     → qué hacer fuera de scope
```

**En MWT:** el archivo SKILL_*.md IS el AgentSpec.
**En FaberLoom:** el AgentSpec tiene 2 capas:
- Base layer (FaberLoom global, inmutable) — el skill genérico
- Org layer (customización por organización) — lo que el agente aprendió de esta org

Las dos capas se mergean en runtime → AgentSpec efectivo.

**Principio activado: P1 — Separación en 3 objetos.**
AgentSpec cargado. AgentRuntime actualizado con estado actual. AgentMemory
ya fue cargada en Fase 1.

### En Cowork (observable)
```
[Skill tool invocado] → Claude lee SKILL_COPY.md
[Skill cargado] → instrucciones del skill activas en contexto
```

### En FaberLoom (target)
```
AgentSpec efectivo = merge(base_skill, org_customization)
Versión base: v1.0 (FaberLoom)
Org layer: gold_samples, patrones aprobados, voz de marca, excepciones documentadas
```

---

## FASE 4 — Resolución de KB (Conocimiento Necesario)

### Qué ocurre
El skill declara en `kb_refs` exactamente qué archivos de conocimiento necesita.
El sistema los carga en este momento — no antes, no más de lo declarado.

Ejemplos por skill:
```
SKILL_COPY:
  kb_refs: [ENT_PROD_*, LOC_COPY_*, ENT_MARCA_IDENTIDAD, POL_CLAIMS_SCANNER]

SKILL_DEMAND_FORECASTER:
  kb_refs: [ENT_DIST_FORECAST_SIGNALS, ENT_DIST_SAP_SCHEMAS, PLB_DEMAND_FORECASTING]

SKILL_HUMANIZE_COMMS:
  kb_refs: [ENT_MARCA_MW_IDENTIDAD, LOC_COMMS_*, PLB_COMUNICACION]
```

Si un dato declarado en `kb_refs` no existe o está DEPRECATED → el agente escala.
No inventa. (Principio P2 + Regla inquebrantable #1 de CLAUDE.md)

**Principio activado: P9 — Gobernanza embebida.**
Policy gate: ¿Están todas las dependencias KB vigentes? Si no → escalar, no continuar.

### En FaberLoom (target)
```
resolver_kb(skill.kb_refs) → [
  verificar_status(archivo),         # ¿VIGENTE? ¿DEPRECATED? ¿STUB?
  verificar_version(archivo),        # ¿Versión esperada?
  cargar_contenido(archivo),         # Contenido al contexto
  registrar_en_runtime(archivo)      # Para audit trail
]
```

---

## FASE 5 — Ensamblaje del Contexto Efectivo

### Qué ocurre
En este punto el sistema tiene todo lo que necesita para generar. Se construye el
"contexto efectivo" — la suma exacta de todo lo que el agente ve al generar:

```
CONTEXTO EFECTIVO = 
  [1] System prompt base (comportamiento del agente)
  [2] Instrucciones del proyecto (CLAUDE.md)
  [3] Preferencias del usuario
  [4] Memoria relevante cargada (archivos de /auto-memory/)
  [5] AgentSpec del skill activo (SKILL_*.md)
  [6] Gold samples del skill (outputs aprobados previos)
  [7] Patrones aprobados (correcciones históricas)
  [8] Archivos KB declarados en kb_refs
  [9] Historial de conversación activa
  [10] Consulta actual del usuario
```

**Budget de contexto activo (POL_CONTEXT_BUDGET):**
El sistema prioriza lo más relevante si el total excede el límite de tokens.
Orden de prioridad: constraints > skill > gold samples > KB > historial > conversación.

**Principio activado: P2 — Contexto mínimo y exacto.**
La calidad del output es función directa de la precisión del contexto, no del volumen.

### En FaberLoom (target)
```
context_window = assemble([
  system_base,
  agentspec_effective,      # base + org layer mergeado
  agentmemory.gold_samples, # solo los del skill activo
  agentmemory.patrones,
  kb_resolved,              # solo los kb_refs
  conversation_active,
  query
], budget=POL_CONTEXT_BUDGET.max_tokens)
```

---

## FASE 6 — Generación con Constraints Activos

### Qué ocurre
El modelo genera el output con todos los constraints del AgentSpec activos.

**Constraints evaluados antes de generar:**
- ¿La acción está dentro del scope declarado en AgentSpec? Si no → escalar
- ¿El nivel de autonomía actual permite esta acción? (ref: Autonomy Ladder)
- ¿Alguna política prohíbe esta acción? (POL_CLAIMS_SCANNER, draft-first, etc.)
- ¿Hay dependencia KB rota? → no generar, escalar

**Constraints evaluados durante generación:**
- Format: respetar `output_format` del skill
- Datos: solo usar lo que está en kb_refs — no inventar
- Tono: respetar voz de marca declarada
- Claims: validar contra POL_CLAIMS_SCANNER antes de incluir

**Draft-first (P3 — absoluto):**
Si el output implica acción externa (email, webhook, CRM write) → siempre draft.
El agente propone. El humano aprueba. Sin excepciones.

**Estado del agente durante generación:**
```
AgentRuntime.estado = "drafting"
AgentRuntime.tarea_activa = {descripción, skill, contexto}
```

### En FaberLoom (target)
```
policy_gate_pre_generate([
  scope_check(query, agentspec.scope),
  autonomy_check(agentruntime.nivel, accion.impacto),
  kb_dependency_check(agentspec.kb_refs),
  draft_first_check(accion.tipo)  # externo → siempre draft
])
→ si pasa todos → generar
→ si falla alguno → estado = "escalated" o "blocked"
```

---

## FASE 7 — Output + Gate Humano

### Qué ocurre
El agente presenta el output con toda la trazabilidad:

**Estructura del output card (FaberLoom):**
```
[Output generado]
─────────────────────────────────────
Fuentes usadas: ENT_PROD_MANTA, LOC_COPY_ES, gold_sample_#7
Nivel de confianza: 82% (basado en 14 ejecuciones previas similares)
Gold sample activo: sí (ejemplo #7 usado como referencia)
─────────────────────────────────────
[Aprobar] [Editar] [Rechazar]
   ↓          ↓        ↓
approved  edited    rejected
```

**Feedback tipificado al rechazar (P6):**
```
tone / data / structure / policy / scope / context
```
Sin esta clasificación no hay aprendizaje útil — solo "no me gustó".

**Estado del agente post-output:**
```
AgentRuntime.estado = "awaiting_approval"
AgentRuntime.outputs_pendientes += 1
AgentRuntime.termometro_aprendizaje += peso(tipo_output)
```

**Principio activado: P3 — Draft-first + P6 — Feedback tipificado.**

---

## FASE 8 — Ciclo de Aprendizaje

### Qué ocurre (solo si el humano interactúa con el output)

**8a — Evento estructurado emitido:**
```
draft.approved → {output_id, approval_rate_actual, edit_distance: 0}
draft.edited   → {output_id, edit_distance, campos_modificados, tipo_corrección}
draft.rejected → {output_id, reason_code: "tone|data|structure|policy|scope|context"}
```

**8b — Termómetro de aprendizaje:**
Cada evento suma al termómetro del skill:
```
🔵 0-2 outputs → Frío (no urgente)
🟡 3-5 outputs → Tibio (revisar pronto)
🔴 6+ outputs  → Caliente (consolidar ya)
```

**8c — Gate humano: "Indexar Aprendizaje"**
Al presionar el botón → modal muestra propuesta del clasificador (P11):

```
Clasificador evalúa cada output pendiente:

  ¿Qué cambió? ¿Cuánto? ¿Cómo?
        ↓
  Propone destino:
  
  A) CONTEXTO         → hecho organizacional que el skill no sabía
                        → escribe a pgvector namespace org (cross-skill)
  
  B) SKILL REFINEMENT → regla de comportamiento mal aplicada
                        → escribe a Org AgentSpec (layer de org)
  
  C) GOLD SAMPLE      → output aprobado con ≤20% de edición
                        → escribe a AgentMemory del skill
```

**8d — Propagación cross-skill (P12):**
Si el aprendizaje aplica a más de un skill → modal muestra checkboxes:
```
Alcance detectado: Cluster "comunicación"

✅ SKILL_COPY           (origen)
✅ SKILL_HUMANIZE_COMMS (mismo cluster)
✅ SKILL_CLIENT_SERVICE (mismo cluster)
☐  SKILL_DEMAND_FORECASTER (diferente dominio)

[Confirmar todos] [Seleccionar cuáles] [Descartar]
```

**8e — Solo al confirmar → escribe a memoria.**
`auto_approve: false` siempre. El humano es el gate de escritura.

**8f — Actualización de métricas de autonomía:**
```
AgentRuntime.executions_total += 1
AgentRuntime.approval_rate = rolling_avg(últimas 20)
AgentRuntime.edit_light_rate = rolling_avg(últimas 20)
AgentRuntime.rejection_rate = rolling_avg(últimas 20)

→ ¿Cumple criterios de promoción? (P4) → proponer subir nivel
→ ¿Degradación automática? (rejection > 30% en últimas 5) → degradar
```

**Principios activados: P4 · P5 · P6 · P11 · P12.**

---

## RESUMEN: QUÉS HACE EL SISTEMA EN CADA FASE

| Fase | Qué carga | Qué decide | Principio |
|------|-----------|------------|-----------|
| 0 — Recepción | metadata, fecha, sesión | contexto de ejecución | — |
| 1 — Memoria | MEMORY.md → archivos relevantes | qué recuerda de conversaciones previas | P2 |
| 2 — Intención | skills disponibles | ¿qué skill activo? ¿preguntar? | P7 |
| 3 — Skill | SKILL_*.md = AgentSpec | identidad, constraints, formato | P1 |
| 4 — KB | kb_refs del skill | conocimiento necesario y suficiente | P2, P9 |
| 5 — Ensamblaje | todo lo anterior | contexto efectivo con budget | P2 |
| 6 — Generación | constraints activos | output dentro de scope y formato | P3, P9 |
| 7 — Gate humano | output + trazabilidad | aprobar / editar / rechazar | P3, P6 |
| 8 — Aprendizaje | eventos estructurados | qué escribir a memoria y dónde | P4, P5, P11, P12 |

---

## IMPLICACIONES PARA FABERLOOM

### Lo que Cowork hace que FaberLoom debe replicar
1. Cargar instrucciones de proyecto antes de leer la consulta (CLAUDE.md → AgentSpec)
2. Indexar memoria y cargar solo lo relevante (MEMORY.md → AgentMemory lazy-load)
3. Detectar skill por trigger_word o semántica (skill matching → clasificador de intención)
4. Resolver kb_refs del skill antes de generar (dependency check + KB resolver)
5. Ensamblar contexto con budget explícito (no pasar todo siempre)
6. Presentar output con trazabilidad de fuentes (qué usó, por qué)
7. Capturar feedback tipificado — no texto libre
8. Clasificar aprendizaje antes de escribir a memoria (clasificador P11)
9. Propagar aprendizaje cross-skill con gate de confirmación (P12)

### Lo que FaberLoom añade que Cowork no tiene
- State machine explícita con colores/badges en UI
- Termómetro de aprendizaje visible
- Autonomy Ladder con promoción por evidencia
- Gold samples versionados con 13 campos
- Org layer sobre AgentSpec base (dos capas mergeadas)
- Métricas de autonomía por agente (approval%, edit-light%, rejection%)
- Degradación automática si rejection > 30%
- Handoffs estructurados entre agentes (paquete explícito P10)

---

## REFERENCIA A OTROS DOCUMENTOS

| Documento | Relación |
|-----------|----------|
| ARCH_AGENT_PRINCIPLES.md | Los 12 principios que gobiernan cada fase |
| SCH_SKI