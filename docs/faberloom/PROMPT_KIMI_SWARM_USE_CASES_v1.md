# PROMPT KIMI SWARM - CASOS DE USO FABERLOOM (200) - v1

**uso:** orquestar un swarm Kimi que genere 200 casos de uso multi-industria para FaberLoom,
sharded por industria, imitando el esquema del lote ancla y SIN duplicarlo.
**semilla obligatoria (adjuntar):** `ENT_FB_USE_CASE_CATALOG_v1.md` (58 casos ancla + esquema).
**post-proceso:** un merge pass (Claude o CLI) consolida semilla + swarm, dedupe, y cura a 200 unicos.

> Reglas Kimi aprendidas (NO quitar): Kimi ancla en palabras sueltas e ignora contexto. Por eso
> cada agente lleva (1) titulo de dominio en linea 1, (2) guard de alcance explicito, (3) RUN_ID,
> (4) prohibicion de palabras ambiguas, (5) "si dudas, detente". Sin esto el shard se contamina.

---

## 0. Como correr (orquestador)

1. Adjuntar `ENT_FB_USE_CASE_CATALOG_v1.md` como contexto a CADA agente (es la semilla y el anti-dup).
2. Lanzar 10 agentes en paralelo, uno por shard (seccion 2). Cada agente = 20 casos.
3. Cada agente usa el TEMPLATE (seccion 3) con su `<SHARD>` y `<RUN_ID>`.
4. Recolectar las 10 salidas (200 filas pipe-delimited).
5. Correr el MERGE (seccion 4) para consolidar con los 58 ancla, dedupe y curar a 200 finales.

Total objetivo: 200 casos NUEVOS del swarm; tras merge+dedupe con el ancla, curar el corpus a 200 unicos de mayor valor (no acumular basura por llegar al numero).

---

## 1. Guardrails globales (aplican a TODO agente)

- Generar SOLO para la industria del shard asignado. Cero casos de otra industria.
- Cada caso DEBE ser un workspace heredable que se autoenriquece: scope + de quien hereda + que conocimiento deposita como subproducto del trabajo.
- "caso de uso" = trabajo entrante repetitivo que produce un artefacto del que el profesional es RESPONSABLE y que requiere aprobacion humana (HITL). NO tareas creativas sin responsabilidad (descartar periodismo, arte).
- Cada caso lleva un NEVER autonomo: la accion que el agente NUNCA ejecuta solo (firmar, enviar, mover dinero, decidir, presentar). El NEVER es obligatorio.
- NO inventar leyes. Si no sabes el regimen, escribir `[PENDIENTE-VERIFICAR]`. Nunca citar una ley falsa.
- NO duplicar ningun trigger ya presente en la semilla `ENT_FB_USE_CASE_CATALOG_v1.md`.
- Palabras prohibidas por ambiguas (no usarlas en la salida): "varios", "etc", "entre otros", "gestion general", "soluciones".
- Salida = SOLO filas pipe-delimited. Cero prosa, cero encabezado, cero explicacion. Si dudas del alcance, detente y pregunta.

---

## 2. Shards (10 x 20 = 200)

| # | RUN_ID | SHARD (industria/profesion exacta) |
|---|---|---|
| 1 | UC-legal-20260615 | Servicios juridicos (abogados independientes y bufetes: laboral, penal, civil, corporativo, IP, inmigracion, notarial) |
| 2 | UC-contable-20260615 | Contabilidad y fiscal (CPA, fiscalistas, auditoria, outsourcing contable, nomina) |
| 3 | UC-salud-20260615 | Salud privada (clinicas, consultorios, odontologia, psicologia, veterinaria, laboratorios) |
| 4 | UC-finanzas-corp-20260615 | Finanzas corporativas (AR, AP, conciliaciones, contabilidad, tesoreria, FP&A, compliance/AML) |
| 5 | UC-rrhh-20260615 | Recursos humanos (consultas empleados, reclutamiento, onboarding, relaciones laborales, beneficios) |
| 6 | UC-ops-logistica-20260615 | Operaciones y logistica (importacion, exportacion, aduanas, compras/procurement, supply chain) |
| 7 | UC-educacion-20260615 | Educacion e investigacion (estudiantes, docentes, asistentes de catedra, coordinacion, labs) |
| 8 | UC-comercio-dist-20260615 | Comercio y distribucion B2B (distribuidores tecnicos, mayoristas, dealers, ecommerce/FBA, account management) |
| 9 | UC-inmob-construccion-20260615 | Inmobiliario y construccion (agentes, property management, arquitectura, ingenieria, facility) |
| 10 | UC-marketing-agencias-20260615 | Agencias y servicios profesionales (marketing, RRPP, consultoria, diseno, traduccion, eventos) |

---

## 3. TEMPLATE por agente (pegar tal cual, reemplazar <SHARD> y <RUN_ID>)

```
CATALOGO DE CASOS DE USO - FABERLOOM - SHARD: <SHARD>      # LINEA 1 = DOMINIO. NO BORRAR NI MOVER.
RUN_ID: <RUN_ID>

CONTEXTO (semilla adjunta): ENT_FB_USE_CASE_CATALOG_v1.md define el esquema y 58 casos ancla.
Imita el esquema. NO repitas ningun trigger de la semilla.

ALCANCE (no salir de aca):
- Genera EXACTAMENTE 20 casos de uso para: <SHARD>. Solo esta industria.
- Cada caso = workspace heredable que se autoenriquece (scope + de quien hereda + que deposita).
- Cada caso = trabajo entrante repetitivo -> artefacto del que el profesional es responsable -> requiere HITL.
- Cada caso lleva un NEVER autonomo obligatorio (firmar/enviar/mover/decidir/presentar).
- NO inventes leyes. Si no sabes: [PENDIENTE-VERIFICAR]. NO uses: varios, etc, entre otros, gestion general, soluciones.
- NO generes casos de otra industria. NO repitas el mismo trigger dos veces dentro de tu lote.

FORMATO (una fila por caso, pipe-delimited, en este orden EXACTO):
id | familia | industria_pro | workspace->hereda | trigger->uso->deposita | NEVER_autonomo | compliance_US | compliance_EU_y_AIActTier

REGLAS DE CAMPO:
- id: <RUN_ID>-NN (NN = 01..20)
- AIActTier: ALTO si el uso cae en empleo, educacion-evaluacion, credito/inversion, servicios esenciales, biometria, justicia, salud-decision; si no, LIM o MIN.
- compliance_US y compliance_EU: regimen aplicable tipico; si no aplica, "n/a"; si dudas, [PENDIENTE-VERIFICAR].

EJEMPLO (imitar SOLO el formato, NO el contenido):
UC-legal-20260615-01 | independiente_regulado | Abogado laboral | expediente->materia | demanda entrante->analisis de riesgo->precedentes | firmar/presentar escrito | UPL | secreto profesional, GDPR / ALTO

ENTREGA: 20 filas. Nada mas. Si dudas del alcance, detente y pregunta.
```

---

## 4. MERGE / normalizacion (post-swarm, correr con Claude o CLI, NO Kimi)

1. Concatenar las 10 salidas (200 filas) + los 58 casos ancla del catalogo = corpus ~258.
2. Normalizar: mismo orden de columnas, trim, un solo idioma, IDs re-secuenciados UC-001..
3. Dedupe: colapsar casos con el MISMO (industria + trigger) aunque varie la redaccion. Marcar colisiones.
4. Validar campo a campo: que cada fila tenga NEVER no vacio; que AIActTier sea ALTO/LIM/MIN; que no haya ley citada sin respaldo (si sospechosa -> [PENDIENTE-VERIFICAR]).
5. Curar a 200 unicos de mayor valor (descartar relleno, casos sin responsabilidad/HITL, o sin conocimiento que depositar).
6. Salida final: `ENT_FB_USE_CASE_CATALOG_v2.md` (extiende v1, mismo esquema, agrupado por familia) + changelog + append a MANIFIESTO_CAMBIOS_v2.

Criterio de descarte en la curacion (matar el caso si):
- output es creativo/novel sin anclaje (no hay conocimiento propietario que grounding).
- saber generico alcanza (ChatGPT solo lo resuelve -> no es caso FaberLoom).
- no hay responsabilidad ni necesidad de aprobacion (HITL no aplica).

---

## 5. Notas

- Compliance generado por el swarm es ORIENTATIVO, no asesoria legal. El merge marca lo dudoso.
- Si un shard devuelve <20 utiles tras curacion, NO rellenar con basura: dejar el shard corto y anotar el gap.
- Este prompt y la semilla se entregan juntos: sin la semilla, el swarm pierde el esquema y se contamina.
