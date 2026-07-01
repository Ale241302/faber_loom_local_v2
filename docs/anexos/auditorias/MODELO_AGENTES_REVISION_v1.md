# Modelo de Arquitectura de Agentes IA — Solicitud de Opinión Externa

**De:** Álvaro (CEO Muito Work Limitada)
**Para:** modelo de IA externo (ChatGPT u otro)
**Pedido concreto:** crítica honesta del modelo propuesto. Buscar huecos, tensiones, simplificaciones erróneas, y ángulos no considerados. NO concordar reflexivamente.

---

## 1. Contexto del autor y por qué importa para tu crítica

Tengo una empresa, **Muito Work Limitada (MWT)** en Costa Rica, con tres tracks:

- **Rana Walk** — marca propia de plantillas ergonómicas, vendiendo en Amazon FBA, en expansión a otros canales.
- **Representación B2B** — distribuyo Marluvas y Tecmater (calzado de trabajo) en clientes industriales de México a Colombia.
- **FaberLoom** — proyecto SaaS B2B LATAM para PYMEs/fabricantes, en construcción.

Estoy construyendo arquitectura de agentes IA para operar todo. Stack: Claude Code, Cowork, n8n, Google Drive, Amazon SP-API, Helium 10. Mi KB tiene 430+ archivos `.md` versionados (taxonomía de 8 tipos canónicos: ENT/PLB/SCH/LOC/POL/IDX/SKILL/LOTE + especiales SPEC/ARCH/AUDIT).

El modelo que voy a presentar es para **FaberLoom** (multi-tenant SaaS) pero también para **mwt.one** (operación interna single-tenant). Aplica conceptualmente a cualquier dominio: legal, consultoría, educación, agencia, fabricación.

---

## 2. Problema que el modelo intenta resolver

Construir agentes IA útiles que:

- Sean **auditables y deterministas** (no cajas negras).
- Distingan **conocimiento factual** de **lente cognitiva**.
- Permitan **curaduría humana** del aprendizaje (no auto-promoción).
- Funcionen **multi-tenant** sin contaminación cross-cliente.
- Soporten **herencia** (templates marketplace → org → local).
- Escalen sin que cada caso requiera diseño nuevo.

---

## 3. Primitivas del modelo

Cinco primitivas operativas + dos contenedores:

```
Usuario
  ├── CTX usuario (preferencias personales, persistente)
  ├── (opcional) pertenece a Organización
  │     ├── CTX org (lente cognitiva organizacional)
  │     ├── KB org (conocimiento curado)
  │     └── Catálogo org (Skills + Agentes + Templates de Workspace)
  │
  ├── Marketplace (templates públicos, curados upstream)
  │
  └── Workspaces operativos (scope con MANDATO)
        └── Ej. WS_SONDEL
              ├── Mandato (propósito + scope + vigencia + autoridad + constraints)
              ├── KB del workspace
              ├── Invocaciones (agentes/skills, locales o referenciados)
              ├── Outputs producidos
              ├── Pool de candidatos local (aprendizajes pendientes curaduría)
              └── Sub-agentes/sub-skills ad-hoc
```

### 3.1 Definiciones

| Primitiva | Definición |
|---|---|
| **Conocimiento** | Lo factual, citable, estable. Ejemplo: el Código de Trabajo, una sentencia, las specs de un producto, los datos de un cliente |
| **Contexto** | La lente que define cómo se usa el conocimiento. La doctrina del bufete, el estilo del operador, los criterios de relevancia |
| **Skill** | Habilidad atómica con contract input/output. Verbo. Ejemplo: `redactar_demanda`, `calcular_indemnización` |
| **Agente** | Ejecutor con varios skills coordinados internamente. Persona-rol. Ejemplo: `AGT_ASISTENTE_LITIGIO_LABORAL` |
| **Workspace** | Scope contextual con propósito declarado (mandato). Contenedor que orquesta hacia adentro |

### 3.2 Diferencia clave Skill vs Agente

> **Skill = un verbo** (atómico).
> **Agente = una persona-rol con varios verbos** (compuesto).

Si necesito una habilidad atómica con input/output claros → Skill. Si necesito un asistente que coordina varios pasos con criterio + memoria de trabajo → Agente.

### 3.3 Diferencia clave Agente vs Workspace

> **Agente** compone su comportamiento (es una persona).
> **Workspace** compone el escenario (es un contenedor).

El agente orquesta hacia adentro de su identidad. El workspace orquesta hacia afuera, invocando agentes/skills.

**Importante:** un "orquestador entre agentes" NO es un agente nuevo. ES el workspace. La lógica de orquestación cross-agente vive en el workspace, no en una primitiva separada.

---

## 4. Cinco tipos de Contexto (ciudadano de primera clase)

Esta es la decisión más fuerte del modelo. Contexto NO es solo metadata — es primitiva con cinco sabores:

| Tipo | Vive en | Mutabilidad | Ejemplo |
|---|---|---|---|
| **CTX base de skill/agente** | Definición del skill (versionado) | Bump por release | "El skill `redactar_demanda` redacta con estilo formal, estructura X, jurisprudencia preferida Y" |
| **CTX organizacional** | Catálogo org (versionado) | Bump por curaduría organizacional | "En este bufete priorizamos sala constitucional sobre sala segunda en despidos" |
| **CTX workspace** | Workspace mismo | Mutable durante vida del workspace | "Cliente Sondel, contrato 2024, prefiere conciliación, deadline jueves" |
| **CTX usuario** | Memoria del usuario | Mutable | "Este operador siempre rechaza opción X, prefiere PDFs en español" |
| **CTX vivo (sesión)** | Runtime, transient | Por hilo | "Estoy redactando réplica para audiencia del jueves" |

Inyección al agente en orden de prioridad: **base → org → workspace → usuario → vivo** (más específico sobreescribe más general).

---

## 5. Mandato — contexto fundacional del workspace

Cada workspace tiene un **mandato** que declara:

```yaml
proposito: para qué existe este workspace
scope_incluye: qué entra
scope_excluye: qué no entra (importante)
autoridad: qué puede decidir el agente solo / qué requiere aprobación
vigencia: hasta cuándo (fecha o evento)
constraints: policies inquebrantables que aplican
```

Sin mandato no hay workspace. Es lo que permite aislamiento, curaduría útil, y auditoría.

**Pregunta abierta:** elegí "mandato" porque suena natural en B2B legal/representación. Para casos como estudiante (workspace "Cálculo 2") o producto interno suena raro. La idea es traducir UI por vertical: B2B = Mandato, educativo = Objetivo, producto = Misión, default = Propósito. **¿Mejor término universal?**

---

## 6. Niveles de herencia y curaduría

```
NIVEL 1 — MARKETPLACE (público, curado upstream)
   │  copiar / forkear como punto de partida
   ▼
NIVEL 2 — CATÁLOGO ORG (curado por la organización)
   │  instanciar (reference) o forkear (copy)
   ▼
NIVEL 3 — WORKSPACE LOCAL (operativo, scope cliente/proyecto/tema)
   │  crear ad-hoc dentro
   ▼
NIVEL 4 — SUB-AGENTE / SUB-SKILL AD-HOC (vida atada al workspace)
```

### 6.1 Instanciar vs Forkear

| Operación | Qué hace | Cuándo usarla |
|---|---|---|
| **Instanciar (reference)** | Workspace usa el agente/skill por referencia. Si org bumpea version, todos lo ven | Default. Mantiene determinismo cross-workspace |
| **Forkear (copy)** | Workspace copia y aplica overrides locales. Se desacopla del original | Cuando se necesita comportamiento divergente del estándar org |

### 6.2 Flujo de aprendizaje (subida por curaduría)

Inspirado en Principio 11 de mi `ARCH_AGENT_PRINCIPLES` v1.5 (clasificador de aprendizaje a 3 destinos), extendido con dimensión de alcance:

```
Output generado → feedback humano → clasificador propone:

DESTINO (qué tipo):
  A) CONTEXTO          → hecho organizacional / lente nueva
  B) SKILL REFINEMENT  → regla de comportamiento del skill
  C) GOLD SAMPLE       → output completo de referencia futura

ALCANCE (a qué nivel se promueve):
  · Personal     → CTX usuario (sólo me afecta a mí)
  · Local        → CTX workspace (sólo este scope)
  · Cliente      → CTX/KB del WS_ORG_<cliente> (cura: dueño del cliente)
  · Org          → Catálogo org (cura: curador organizacional)
  · Marketplace  → Template público (cura: anonimización + revisión upstream)

Cada subida = gate humano + audit + bump de versión.
```

### 6.3 Patrón doble workspace por cliente

Para un cliente como Sondel hay **dos workspaces** distintos:

| Tipo | Ubicación | Rol | Curado por |
|---|---|---|---|
| **WS_ORG_SONDEL** | Catálogo org | Maestro del cliente: historia, contratos, doctrina aplicada, lecciones acumuladas | Curaduría organizacional |
| **WS_OP_SONDEL** | Operativo local del operador | Día-a-día: tareas activas, drafts en curso, conversación actual | Operador, con promoción al WS_ORG vía curaduría |

`WS_OP_SONDEL` hereda al crearse del `WS_ORG_SONDEL`. Aprendizajes operativos suben vía curaduría al maestro del cliente. Aprendizajes transversales (aplicables a otros clientes) suben al CTX/KB org general anonimizado.

---

## 7. Capacidades de creación

| Primitiva | Crear nuevo | Heredar de Org | Heredar de Marketplace | Forkear de otro local |
|---|---|---|---|---|
| **Workspace** | Sí | Sí (template del cliente registrado en org) | Sí (template público) | Sí |
| **Agente** | Sí (custom local) | Sí (catálogo org) | Sí (template marketplace) | Sí |
| **Skill** | Sí (custom local) | Sí (catálogo org) | Sí (template marketplace) | Sí |
| **CTX** | Sí | Sí | Sí | Sí |
| **Conocimiento (KB)** | Sí (cargar al WS) | Sí (consumir KB org via reference) | N/A | Sí (importar) |

---

## 8. Decisiones arquitectónicas tomadas

1. **Contexto es ciudadano de primera clase** (no metadata). Cinco tipos, cinco lugares.
2. **Conocimiento es lo citable; contexto es lo que decide cómo se cita.**
3. **Skill = atómico, Agente = compuesto interno, Workspace = contenedor externo.**
4. **No hay "AGT orquestador".** El workspace orquesta cross-agente.
5. **Workspace = scope con MANDATO obligatorio declarado al crear.**
6. **Sub-agentes ad-hoc viven dentro del workspace**, vida atada al workspace.
7. **Profundidad máxima 3 niveles operativos** (workspace → sub-agente → skills). No anidar más.
8. **Sub-agentes son stateless cross-workspace.** Estado se persiste en workspace.
9. **Curaduría = gate humano (no auto-promoción)**, replicando patrón ya existente en mi KB (POL_DETERMINISMO + MANIFIESTO_APPEND + bump version).
10. **Workspace de cliente tiene dos caras**: WS_ORG (maestro org) y WS_OP (operativo local).
11. **Default es instanciar (reference), no forkear**, para mantener determinismo.
12. **Herencia es cascada de capas**, no flat — el contexto base global se sobreescribe por org → workspace → usuario → vivo.
13. **El "orquestador" como agente no existe** — es lógica del workspace.
14. **Sub-agentes no crean sub-sub-agentes.** Si se necesita, abrir nuevo workspace.

---

## 9. Tensiones / preguntas abiertas donde busco opinión

### 9.1 Mandato como término universal

Elegí "Mandato" para el contexto fundacional del workspace. Funciona en B2B legal/representación pero no en estudiante o producto interno. ¿Hay un término más universal? ¿Es mejor traducir UI por vertical vs un solo término técnico subyacente?

### 9.2 Propiedad de outputs

En el caso bufete:
- Datos del expediente del cliente → propiedad cliente.
- Demanda redactada por el bufete → work for hire, propiedad bufete con copia entregada.
- Aprendizajes anonimizados → propiedad bufete.

¿Esta clasificación se sostiene legalmente cross-jurisdicción LATAM? ¿Cómo se maneja al cierre del workspace? ¿El cliente puede pedir "todo lo que aprendieron sobre mí" como portabilidad GDPR/LGPD/Ley 8968?

### 9.3 Curaduría escalable

Curaduría organizacional con gate humano por cada candidato escala mal. Mi recomendación interna fue "agente curador IA con gate humano para casos high-stakes" pero eso introduce un agente que cura agentes — riesgo de regresión circular. ¿Cómo lo resolverías?

### 9.4 Trigger de aprendizaje

Sin trigger claro el pool de candidatos se vuelve ruido. Mis triggers candidatos:
- Patrón recurrente (3+ veces el mismo criterio)
- Corrección explícita del operador sobre output
- Decisión declarativa ("usá siempre X")
- Diff entre output del agente y entregable final

¿Qué falta o sobra? ¿Cómo evitar que el sistema "aprenda" cosas espurias del operador?

### 9.5 Composición cross-materia

Caso real: un asunto del cliente toca laboral + tributario simultáneamente. Mi decisión: el workspace orquesta (invoca uno → recibe output → lo pasa de input al otro → sintetiza). Sub-agentes nunca se hablan directamente. ¿Es la mejor solución? ¿Hay literatura sobre orquestación multi-agente que valga la pena considerar?

### 9.6 Aislamiento cross-cliente con templates compartidos

Si Skill X es template marketplace usado en muchos workspaces, y aprendí algo trabajando con Cliente A, ¿cómo evito que ese aprendizaje contamine el comportamiento de Skill X cuando lo uso con Cliente B sin pasar por curaduría? Mi respuesta actual: aprendizajes locales viven en CTX workspace, nunca tocan el skill base. Promoción al base requiere curaduría organizacional con anonimización. ¿Suficiente?

### 9.7 Versionado de templates instanciados

Si un workspace usa Skill X v1.2 (instanciado, no forkeado), y la org bumpea a v1.3, ¿el workspace adopta v1.3 automáticamente? Riesgos:
- Adopción automática puede romper outputs in-flight.
- Adopción manual lleva a fragmentación de versiones cross-workspace.

Mi inclinación: notificación + ventana de prueba + adopción explícita por el owner del workspace. ¿Mejor patrón?

### 9.8 ¿El modelo cubre casos no transaccionales?

El modelo está pensado para tareas con output entregable (cotización, demanda, reporte). ¿Cómo encaja con casos donde el agente es **conversacional puro** (asistente de soporte, tutor, brainstorm)? ¿Skill atómico con output "respuesta conversacional" basta o necesito otra primitiva?

### 9.9 Memory del agente — diferencia con CTX

Mi `ARCH_AGENT_PRINCIPLES` distingue:
- AgentSpec (lo que el agente ES) → estático, versionado.
- AgentRuntime (lo que HACE) → dinámico, métricas.
- AgentMemory (lo que APRENDIÓ) → curado, gold samples.

¿Cómo se relaciona AgentMemory con los 5 CTX que propongo? ¿Es subset, superset, ortogonal? Mi lectura tentativa: AgentMemory = gold samples + patrones aprobados, distinto de CTX (que es lente cognitiva). Pero ambos alimentan al agente en runtime.

### 9.10 Falta alguna primitiva

Las que considero pero descarté:
- **Tarea / Caso** — pensé en hacerlo primitiva pero quedó como objeto dentro del workspace, no primitiva.
- **Política** — la POL_ ya existe en mi KB como constraint inquebrantable, pero ¿debería ser primitiva del modelo nuevo?
- **Evento / Trigger** — los agentes pueden activarse por eventos, no solo por trigger word. No lo modelé.
- **Tool / Action** — distinción tool (capacidad técnica como SP-API) vs skill (capacidad conceptual con criterio). No lo separé.

¿Falta alguna? ¿Sobra alguna de las que tengo?

---

## 10. Estado actual del repositorio (contexto operativo)

Para que entiendas dónde estoy implementando:

- **430+ archivos `.md` versionados** en repo `mwt-knowledge-hub`, mirror en OneDrive para Cowork.
- **Taxonomía actual**: ENT (104), PLB (40), POL (31), LOC (32), SCH (20), SKILL (13), IDX (12), SPEC (14), ARCH (1), + audit logs.
- **Estado tipos en KB**: no existe `AGT_`, `CTX_`, ni `WS_` como prefijos. Son las primitivas nuevas que propongo.
- **PLB_ es muletilla**: ~50% son contexto-criterio (PLB_COPY), ~50% son skill-procedimiento (PLB_OPS_AMAZON). En el modelo nuevo se separan.
- **POL_ tiene dos sub-naturalezas**: ~50% constraints inquebrantables (compliance/legal), ~50% lentes cognitivas (criterios calidad). Las segundas migran a CTX_.
- **ENT_GOB_AGENTES está mezclado** humanos (Alejandro AG-02) e IA (RW-Ops). Se va a separar.
- **`ARCH_AGENT_PRINCIPLES.md` v1.5** ya tiene Principio 11 (clasificador aprendizaje 3 destinos) y P1 (3 objetos: AgentSpec/Runtime/Memory). Buena base.
- **13 skills definidos**, todos atómicos, todos en SHADOW (observan, no ejecutan autónomamente).
- **No tengo ningún agente orquestador definido** ni workspaces formales como tipo de archivo.
- **Estoy diseñando antes de codear** — esta es decisión de arquitectura, no implementación inmediata.

---

## 11. Lo que NO necesito de la opinión externa

- Que me digas que el modelo "está bien".
- Que me sugieras estudiar X libro famoso de IA — tengo conocimiento técnico sólido.
- Marketing-talk sobre "transformación digital".
- Frameworks genéricos sin aterrizaje en mi caso.

## 12. Lo que SÍ necesito

- **Huecos**: qué casos rompe el modelo.
- **Tensiones**: dónde una decisión choca con otra.
- **Experiencia en producción**: si trabajaste con sistemas multi-agente, qué patrones conocidos ignoré.
- **Simplificaciones erróneas**: dónde estoy reduciendo algo que es más complejo.
- **Trade-offs no evaluados**: qué decisión podría ser distinta y por qué.
- **Casos de borde**: workspaces enormes, organizaciones jerárquicas, sub-organizaciones, cross-org collaboration.
- **Implementación**: qué challenge técnico aparece al codear esto en producción multi-tenant.

---

## 13. Formato de respuesta esperado

Tabla de hallazgos:

| Sección | Hallazgo | Severidad (alta/media/baja) | Recomendación concreta |
|---|---|---|---|

Más prosa libre para contexto donde corresponda. No tablas vacías ni concesiones reflexivas.

Gracias por la honestidad.

---

**Fin del documento.**
