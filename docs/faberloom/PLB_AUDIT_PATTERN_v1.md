# PLB_AUDIT_PATTERN_v1 -- Patron Canonico de Auditoria Multi-Agente FaberLoom
id: PLB_AUDIT_PATTERN_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: PLB
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom, MWT]
relacionado: ENT_FB_DECISIONES_E1_v1.md · ARCH_AGENT_PRINCIPLES.md

---

## Proposito

Patron reproducible para auditorias tecnicas de KB y arquitectura
FaberLoom. Emergido empiricamente el 2026-06-24 en la sesion de
auditoria Foundation Beta E1 con Fugu Ultra y Kimi 2.7.

El mismo prompt estructurado con roles explicitos y puntos de
verificacion produce outputs comparables en Fugu Ultra y Kimi 2.7.
El patron es agnostico de modelo.

---

## 1. Principio central

Un prompt de auditoria para orquestador multi-agente no es igual
a un prompt para modelo monolitico.

Requiere pensar en:
  - descomposicion en subtareas
  - roles con responsabilidades distintas
  - puntos de verificacion entre fases
  - sintesis cruzada al final

---

## 2. Arquitectura de Fugu Ultra (Sakana AI)

Fugu Ultra es un orquestador multi-agente, no un modelo monolitico.

Componentes:
  Trinity: tres roles por tarea
    Thinker:  planifica y descompone
    Worker:   ejecuta la subtarea
    Verifier: verifica el output

  Conductor (GRPO): decide via reinforcement learning
    Que modelo del pool usar para cada subtarea
    Cuando escalar a mas agentes
    Cuando parar

3 estrategias emergentes:

  debate-and-aggregation:
    Multiples agentes resuelven independientemente.
    Agregador detecta discrepancias y produce respuesta final.
    Activar con: "genera multiples intentos independientes y compara"

  build-and-debug:
    Un agente construye, otro revisa buscando bugs.
    Activar con: "implementa primero, luego un rol diferente revisa"

  bring-in-specialist:
    Subtarea requiere expertise especializado.
    Activar con: "esta subtarea requiere expertise en X"

Nota Kimi 2.7:
  No es orquestador pero produce outputs comparables cuando el prompt
  especifica roles explicitos y puntos de verificacion.
  El mismo prompt funciona en ambos modelos.

---

## 3. Estructura canonica del prompt de auditoria

Secciones delimitadas obligatorias:

  --- CONTEXTO DEL PROYECTO ---
  Stack, decisiones resueltas, runtime flow, aislamiento multi-tenant.
  Si el modelo lee archivos del repo (Fugu Agent, Kimi Agent):
    incluir rutas absolutas.
  Si no puede (modelos web):
    pegar contenido critico inline.

  --- ROLES ---
  Minimo 3 roles con responsabilidades mutuamente excluyentes.
  Roles tipicos FaberLoom:
    ROLE A -- Runtime Architect: Django/Celery/PostgreSQL/RLS
    ROLE B -- Security Auditor:  multi-tenant isolation y compliance
    ROLE C -- Desktop Engineer:  Electron/WebSocket/session

  --- PROCESO ---
  Fase 1: cada ROLE analiza independientemente
  Fase 2: debate y consenso entre roles
  Fase 3: sintesis cruzada

  --- PREGUNTAS ---
  Solo preguntas especificas. Sin padding.
  Codigo por pregunta: A1, B2, C3.
  Formato:
    PREGUNTA: [codigo]
    HALLAZGO: [respuesta directa]
    GAP DETECTADO: [que falta]
    RIESGO: [P0 bloquea / P1 importante / P2 mejora]
    RECOMENDACION: [que hacer exactamente]

  --- FORMATO DE SALIDA ---
  Estructura esperada + SINTESIS CRUZADA con:
    Top 5 gaps que aparecen en mas de un ROLE
    Failure mas probable en primeros 90 dias
    Decision tecnica que reverterian
    Tests requeridos antes de S1A

---

## 4. Activacion de estrategias

build-and-debug (runtime y seguridad):
  "Fase 1: ROLE A y ROLE B auditan independientemente.
   Fase 2: ROLE C audita independientemente.
   Fase 3: comparan hallazgos. Coincidencias = alta confianza."

debate-and-aggregation (decisiones y contradicciones):
  "Cada ROLE analiza independientemente y producen
   un veredicto por consenso."

bring-in-specialist (compliance, pgvector, Electron):
  "Esta subtarea requiere expertise en X."

---

## 5. Patron dual Fugu + Kimi

Ejecutar el mismo prompt en Fugu Ultra y Kimi 2.7 simultaneamente.
Traer ambos outputs al Arquitecto Ejecutor (Claude Projects).

Interpretacion:
  Coinciden = alta confianza, implementar sin debate
  Divergen = decision CEO
  Uno vio y el otro no = blind spot, investigar

Tendencias observadas:
  Fugu Ultra: mas precision tecnica, detecta contradicciones
    internas entre documentos.
  Kimi 2.7: mas pragmatismo operacional, propuestas implementables
    con recursos limitados.
  Claude Projects: arbitro con contexto canonico de la KB.

---

## 6. Checklist antes de lanzar auditoria

Estructura:
  Secciones delimitadas con ---?
  Formato de salida completamente especificado?
  Preguntas especificas (no generales)?
  Puntos de verificacion entre fases?

Contenido:
  Contexto de dominio suficiente (stack, decisiones)?
  Tareas descompuestas en subtareas identificables?
  Roles con responsabilidades distintas sin overlap?
  Preguntas incluyen texto exacto de documentos en conflicto?

Estrategia:
  Estrategia emergente activada?
  Criterios de aceptacion medibles?

---

## 7. Tipos de auditoria FaberLoom

### Runtime tecnico (usada 2026-06-24 Round 5)
  Objetivo: gaps entre spec y lo que el codigo puede implementar
  Roles: Runtime Architect / Security Auditor / Desktop Engineer
  Estrategia: build-and-debug
  Output: gaps P0/P1/P2 + tests requeridos

### Contradicciones KB (usada 2026-06-24 Round 5b)
  Objetivo: resolver conflictos entre documentos canonicos
  Roles: Pragmatic Engineer / Security Architect / Product Architect
  Estrategia: debate-and-aggregation
  Output: decision arquitectonica + spec ejecutable + doc ganador

### Fichas funcionales (usada 2026-06-24 Kimi Swarm)
  Objetivo: especificar modulos en 13 dimensiones
  Roles: 6 agentes especializados por modulo + sintetizador
  Estrategia: parallel analysis + cross-synthesis
  Output: fichas + contradicciones detectadas + pendientes CEO

---
Changelog:
- v1.0 (2026-06-24): Creacion. Patron emergido de auditoria
  Foundation Beta E1 con Fugu Ultra + Kimi 2.7. Arquitectura
  Trinity/Conductor, estructura canonica, patron dual, 3 tipos.
