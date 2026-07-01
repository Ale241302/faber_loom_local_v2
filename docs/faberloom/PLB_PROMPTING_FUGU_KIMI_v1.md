# PLB_PROMPTING_FUGU_KIMI_v1 -- Guia de Prompting Fugu Ultra / Kimi (lista para usar)
id: PLB_PROMPTING_FUGU_KIMI_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: PLB
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom, MWT]
relacionado: PLB_AUDIT_PATTERN_v1.md - SCH_FB_FUNCTIONAL_SPEC_v1.md - ENT_FB_DECISIONES_E1_v1.md - ARCH_AGENT_PRINCIPLES.md

---

## Proposito

Prompts listos para copiar-pegar para las tres auditorias canonicas FaberLoom
(runtime tecnico, contradicciones KB, fichas funcionales) + reglas por modelo +
patron de sintesis cruzada. Operacionaliza PLB_AUDIT_PATTERN_v1. No es teoria:
cada seccion trae el prompt completo con placeholders {{ASI}}.

Como usar: 1. Copiar el prompt de la seccion que aplique. 2. Reemplazar cada
{{PLACEHOLDER}}. 3. Ejecutar el MISMO prompt en Fugu Ultra y en Kimi en paralelo.
4. Traer ambos outputs a Claude Projects (Arquitecto Ejecutor) y aplicar la
Seccion 5.

Convencion de placeholders: {{RUN_ID}} identifica la corrida (ej. R5-2026-06-24);
siempre primero en linea 1 para anclar el dominio y evitar que el modelo derive.

---

## 1. Prompt de auditoria runtime tecnico

Uso: detectar gaps entre la spec y lo que el codigo puede implementar realmente.
Roles: Runtime Architect / Security Auditor / Desktop Engineer. Estrategia Fugu:
build-and-debug. Salida en secciones A-E. Este es el prompt de Round 5 (2026-06-24).

```
[RUN_ID: {{RUN_ID}}] AUDITORIA RUNTIME TECNICO -- FaberLoom Foundation Beta E1

GUARD DE ALCANCE: Audita SOLO runtime e implementabilidad de los modulos listados
abajo. No redisenes el producto. No propongas features nuevos. Si un documento
canonico no esta en CONTEXTO, no asumas su contenido: marcalo como dato faltante.

--- CONTEXTO DEL PROYECTO ---
Stack: {{STACK}}  (ej. Django + Celery + PostgreSQL/RLS + Redis Streams +
  pgvector + LiteLLM + Letta + Electron/Next.js)
Decisiones resueltas: {{DECISIONES_RESUELTAS}}
Runtime flow: {{RUNTIME_FLOW}}
Aislamiento multi-tenant: {{MODELO_AISLAMIENTO}} (7 capas)
Modulos a auditar: {{MODULOS}}  (ej. M07-M20)
Lectura de archivos (Fugu Agent / Kimi Agent -- rutas absolutas):
  {{RUTAS_ABSOLUTAS_REPO}}
  (modelos web: el contenido critico va pegado al final, ver bloque INLINE)

--- ROLES (responsabilidades mutuamente excluyentes) ---
ROLE A -- Runtime Architect: Django/Celery/PostgreSQL/RLS, transacciones,
  outbox, jobs, consistencia eventual.
ROLE B -- Security Auditor: aislamiento multi-tenant, data class N0-N4, D9 policy
  gate, audit hash chain, compliance LATAM.
ROLE C -- Desktop Engineer: Electron/WebSocket/session, offline/reconexion,
  auto-update, seguridad de tokens en cliente.

--- PROCESO (estrategia: build-and-debug) ---
Fase 1: ROLE A y ROLE B auditan independientemente.
Fase 2: ROLE C audita independientemente.
Fase 3: los tres comparan hallazgos. Coincidencia entre roles = alta confianza.

--- PREGUNTAS (solo especificas; codigo por pregunta) ---
{{PREGUNTAS}}  (formato A1, B2, C3, ... una por linea)

--- FORMATO DE SALIDA ---
Por cada pregunta:
  PREGUNTA: [codigo]
  HALLAZGO: [respuesta directa]
  GAP DETECTADO: [que falta]
  RIESGO: [P0 bloquea / P1 importante / P2 mejora]
  RECOMENDACION: [que hacer exactamente]
Luego, secciones de cierre:
  A. Hallazgos Runtime Architect
  B. Hallazgos Security Auditor
  C. Hallazgos Desktop Engineer
  D. Debate y consenso entre roles (coincidencias y divergencias)
  E. SINTESIS CRUZADA:
     - Top 5 gaps que aparecen en mas de un ROLE
     - Failure mas probable en los primeros 90 dias
     - Decision tecnica que reverterian
     - Tests requeridos antes de S1A

--- INLINE (solo para modelos web que no leen el repo) ---
{{CONTENIDO_CRITICO_PEGADO}}
```

---

## 2. Prompt de resolucion de contradicciones

Uso: resolver conflictos entre documentos canonicos (ej. D5.1, D6.1). Roles:
Pragmatic Engineer / Security Architect / Product Architect. Estrategia Fugu:
debate-and-aggregation. Salida: decision arquitectonica + spec ejecutable + doc
ganador. Este es el prompt de Round 5b (2026-06-24).

```
[RUN_ID: {{RUN_ID}}] RESOLUCION DE CONTRADICCIONES -- FaberLoom KB canonica

GUARD DE ALCANCE: Resolve SOLO las contradicciones listadas. No abras nuevas
discusiones. Cita el texto exacto de cada documento en conflicto (id + version).
No inventes un criterio nuevo si los documentos no lo soportan: si falta base,
escala a CEO.

--- CONTEXTO DEL PROYECTO ---
Stack/runtime: {{STACK_RUNTIME}}
Reglas inquebrantables: no inventar datos; status aprobado pesa mas que draft;
  KB VIGENTE gana sobre memoria; no tocar FROZEN.
Lectura de archivos (rutas absolutas): {{RUTAS_ABSOLUTAS_REPO}}

--- CONTRADICCIONES A RESOLVER ---
CONTRADICCION 1 ({{CODIGO_1}}, ej. D5.1):
  Documento A: {{DOC_A_ID_VERSION}} dice: "{{TEXTO_A}}"
  Documento B: {{DOC_B_ID_VERSION}} dice: "{{TEXTO_B}}"
  Impacto: {{IMPACTO_1}}
CONTRADICCION 2 ({{CODIGO_2}}, ej. D6.1):
  Documento A: {{DOC_A2_ID_VERSION}} dice: "{{TEXTO_A2}}"
  Documento B: {{DOC_B2_ID_VERSION}} dice: "{{TEXTO_B2}}"
  Impacto: {{IMPACTO_2}}

--- ROLES (responsabilidades mutuamente excluyentes) ---
ROLE A -- Pragmatic Engineer: que es implementable con recursos limitados, costo
  y complejidad de cada opcion.
ROLE B -- Security Architect: cual opcion preserva aislamiento multi-tenant,
  compliance y data class.
ROLE C -- Product Architect: cual opcion sirve mejor al usuario y al roadmap E1.

--- PROCESO (estrategia: debate-and-aggregation) ---
Fase 1: cada ROLE analiza cada contradiccion independientemente y emite veredicto.
Fase 2: los tres debaten y producen un veredicto por consenso.
Fase 3: si no hay consenso, lo declaran explicitamente como decision CEO.

--- FORMATO DE SALIDA (por cada contradiccion) ---
  CONTRADICCION: [codigo]
  VEREDICTO ROLE A / B / C: [opcion + razon, una linea cada uno]
  CONSENSO: [opcion ganadora | NO CONSENSO -> decision CEO]
  DOC GANADOR: [id + version que queda VIGENTE]
  DOC PERDEDOR: [id + version a deprecar o enmendar]
  SPEC EJECUTABLE: [que cambia exactamente, listo para indexar]
  RIESGO RESIDUAL: [P0/P1/P2 + cual]
```

---

## 3. Prompt de fichas funcionales (Kimi Swarm)

Uso: especificar modulos nuevos en las 13 dimensiones canonicas. Roles: N agentes
especializados (1 por grupo de modulos) + 1 sintetizador. Estrategia: parallel
analysis + cross-synthesis. Salida: fichas + contradicciones + pendientes CEO.

```
[RUN_ID: {{RUN_ID}}] FICHAS FUNCIONALES 13 DIMENSIONES -- FaberLoom E1

GUARD DE ALCANCE: Especifica SOLO los modulos asignados a TU agente. Usa las 13
dimensiones EXACTAS de SCH_FB_FUNCTIONAL_SPEC_v1. No reimplementes modulos de
otros agentes. Dato ausente = [PENDIENTE -- NO INVENTAR]. No inventes precios,
SKUs ni decisiones CEO.

--- CONTEXTO DEL PROYECTO ---
Plantilla canonica (13 dimensiones): SCH_FB_FUNCTIONAL_SPEC_v1.md
Fichas de referencia (formato y profundidad, NO reimplementar):
  {{RUTAS_FICHAS_REFERENCIA}}  (ej. M01-M06)
Docs base (rutas absolutas): {{RUTAS_ABSOLUTAS_REPO}}
Convenciones: roles canonicos Owner/Admin/Operator/Supervisor/Viewer (E1 activa
  Owner/Operator, resto E3+); zonas Mesa 1-5; data class N0-N4; autonomy ladder
  L0-L4; estados de draft/task/skill/agente/rutina segun el SCH.

--- MODULOS ASIGNADOS A ESTE AGENTE ---
{{LISTA_MODULOS}}  (cada uno con su descripcion detallada y campos conocidos)

--- PROCESO ---
Por cada modulo, completa las 13 dimensiones:
  D1 Existencia / D2 Proposito / D3 Creacion / D4 Uso diario / D5 Edicion /
  D6 Movimiento y estado / D7 Output / D8 Errores / D9 Aprendizaje /
  D10 Eliminacion / D11 Relaciones / D12 Compliance / D13 Desktop vs Web.
Cabecera por ficha: MODULO / SUPERFICIE / SPRINT E1 / ROLES / DATA CLASS.

--- FORMATO DE SALIDA ---
Una ficha por modulo en las 13 dimensiones, con el nivel de detalle de las fichas
de referencia. Al final de TODO:
  PENDIENTES que requieren decision CEO (lista numerada con [PENDIENTE -- NO INVENTAR])
  CONTRADICCIONES DETECTADAS CON LA KB (id+version de cada documento en conflicto)
No resuelvas contradicciones: documentalas para CEO.
```

---

## 4. Reglas de prompting por modelo

Mismo prompt, distinta forma de entrega segun el modelo:

```
Fugu Ultra (Sakana AI) -- ID modelo: fugu-ultra-20260615
  - Orquestador multi-agente (Trinity: Thinker/Worker/Verifier; Conductor GRPO).
  - Lee archivos del repo directamente: dar RUTAS ABSOLUTAS.
  - Estrategias emergentes a activar segun tipo:
      build-and-debug         -> auditorias de runtime (Seccion 1)
      debate-and-aggregation  -> contradicciones (Seccion 2)
      bring-in-specialist     -> subtareas de compliance / pgvector / Electron
  - Tiende a: precision tecnica, detecta contradicciones internas entre documentos.

Kimi Agent -- lee archivos del repo directamente (rutas absolutas)
  - No es orquestador, pero produce outputs comparables con el MISMO prompt si
    hay roles explicitos + puntos de verificacion.
  - Mas pragmatico operacionalmente (implementabilidad con recursos limitados).
  - Ejecutar en PARALELO con Fugu para comparar.
  - Anti-anclaje: Kimi ancla en palabras sueltas e ignora contexto -> titulo de
    dominio en linea 1 ([RUN_ID]...), guard de alcance explicito, y erradicar
    palabras ambiguas del prompt.

Kimi web -- NO lee el repo: pegar el contenido critico INLINE al final del prompt.

Claude Projects (Arquitecto Ejecutor) -- usar project_knowledge_search primero.
  - Rol de arbitro con el contexto canonico de la KB.
  - No re-genera lo que Fugu/Kimi ya produjeron: sintetiza (Seccion 5).
```

---

## 5. Patron de sintesis cruzada

Como procesar los dos outputs (Fugu + Kimi) en Claude Projects, una vez ejecutado
el mismo prompt en ambos en paralelo.

```
PASO 1: project_knowledge_search del dominio antes de leer los outputs (anclar en
  KB canonica, no en lo que dicen los modelos).
PASO 2: alinear hallazgos por codigo de pregunta (A1, B2, ...) o por modulo.
PASO 3: clasificar cada hallazgo:
```

Matriz de decision:
```
Situacion                         | Lectura                  | Accion
----------------------------------|--------------------------|---------------------------
Fugu y Kimi COINCIDEN             | alta confianza           | implementar sin debate
Fugu y Kimi DIVERGEN             | conflicto real           | decision CEO
Uno VIO y el otro NO             | blind spot               | investigar antes de decidir
```

Tendencias para ponderar (no para creer ciegamente):
```
Fugu Ultra: precision tecnica; bueno detectando contradicciones internas entre
  documentos. Si Fugu marca una contradiccion que Kimi no vio -> revisar los docs.
Kimi: pragmatismo; bueno viendo que se puede implementar con recursos limitados.
  Si Kimi marca inviabilidad que Fugu ignoro -> revisar costo/complejidad real.
Claude Projects: arbitro con contexto canonico; resuelve solo con base en KB
  VIGENTE; lo que no este en KB se escala, no se inventa.
```

Salida de la sintesis:
```
- Tabla de hallazgos: codigo | Fugu | Kimi | clasificacion | accion
- Lista "implementar sin debate" (coincidencias)
- Lista "decision CEO" (divergencias) con el texto de ambos lados
- Lista "blind spots" (uno vio, otro no) con plan de verificacion
- Top riesgos P0/P1 consolidados
```

---

## Checklist antes de lanzar (resumen de PLB_AUDIT_PATTERN_v1 Sec.6)

```
Estructura: secciones delimitadas con --- ? formato de salida especificado?
  preguntas especificas (no generales)? puntos de verificacion entre fases?
Contenido: contexto de dominio suficiente? subtareas identificables? roles sin
  overlap? las preguntas incluyen el texto exacto de los docs en conflicto?
Estrategia: estrategia emergente activada? criterios de aceptacion medibles?
Anti-Kimi: [RUN_ID] en linea 1? guard de alcance? sin palabras ambiguas?
```

---

Changelog:
- v1.0 (2026-06-24): Creacion. 5 secciones de prompts listos para usar (auditoria
  runtime, contradicciones, fichas Swarm, reglas por modelo, sintesis cruzada).
  Operacionaliza PLB_AUDIT_PATTERN_v1; integra el guard anti-anclaje de Kimi.
