VERIFICACION CASOS DE USO FABERLOOM - SWARM UNICO (60 casos, 10 familias)   # LINEA 1 = DOMINIO. NO BORRAR NI MOVER.
RUN_ID: VER-ALL-20260615   ·   correr en ESPACIO NUEVO, con acceso WEB, como despliegue multiagente.

================================================================
ORQUESTACION
================================================================
Desplega 10 sub-agentes, uno por familia (seccion CASOS). Cada sub-agente verifica solo su familia con web.
Al terminar, un sub-agente consolidador une las 10 tablas en una sola y arma las dos listas finales.
No re-corras volumen: esto es VERIFICACION, no generacion. No agregues ni quites casos; verifica los 60 dados.

================================================================
MANDATO ANTI-SESGO (no romper)
================================================================
- Lista cruda. NINGUN caso es mejor que otro. Investiga cada uno por su cuenta. No infieras importancia del orden.
- PROHIBIDO puntuar quien construye, cuando, o "viabilidad para equipo chico". La capacidad de quien construye NO es parte de este analisis (se decide despues, aparte). Meterla aca sesga el mapa hacia el presente.
- Carga regulatoria = DATO del caso, no penalizacion. Reportala; nunca bajes un score por ella.
- NO inventes competidores, precios ni tamanos de mercado. Cada dato lleva fuente (URL) o se marca [NO-VERIFICADO]. Mejor "no encontre" que un dato falso.
- "No existe competidor vertical" es un hallazgo VALIDO; confirmalo buscando, no lo asumas.
- Geografia: en legal, distingue notary public common-law (US, atestigua firmas, trivial) del notario civil-law (LATAM/EU, escritura). Son profesiones distintas.

================================================================
PRODUCTO (neutral, solo para evaluar encaje)
================================================================
FaberLoom = plataforma donde un profesional arma un copiloto sobre un "workspace" heredable que se autoenriquece:
hace el trabajo (redacta/analiza/cotiza/diagnostica), un humano aprueba antes de que salga (HITL), y cada
aprobacion deposita conocimiento reutilizable. Grounding en conocimiento propio + aprobacion + memoria.
No es un chatbot generico.

================================================================
TAREA POR CASO
================================================================
1. Competidores reales (web): horizontales (ChatGPT/Copilot/Glean/Notion AI) y verticales de esa profesion.
   Por cada uno: nombre, que hace, precio si es publico, y si tiene (a) workspace por cliente, (b) HITL estructurado, (c) memoria/aprendizaje. URL obligatoria.
2. Fuerza del incumbente: dominante / moderado / debil / ausente (con evidencia, no a ojo).
3. Senal de mercado (web): tamano o cantidad de profesionales, con fuente; si no hay, [NO-VERIFICADO].
4. Impacto intrinseco 1-5: frecuencia del dolor x horas ahorrables x disposicion a pagar x cantidad de profesionales.
5. Encaje-moat 1-5: cuanto aporta defensibilidad el patron (grounding propio + HITL + herencia) en ESE caso.
6. Carga regulatoria (dato): AI Act tier (ALTO/LIM/MIN) + ley sectorial US/EU.

================================================================
FORMATO DE SALIDA (una fila por caso, pipe-delimited)
================================================================
id | industria | competidor_principal | que_le_falta | fuerza_incumbente | senal_mercado | impacto_1a5 | encaje_moat_1a5 | carga_regulatoria | fuentes_URL

CONSOLIDADO FINAL (lo arma el sub-agente consolidador):
- tabla unica con los 60 casos
- LISTA A: casos sin competidor vertical (posible espacio en blanco)
- LISTA B: casos con incumbente dominante (a evitar de frente)
NO recomendar beachhead. La verificacion mapea con evidencia; no decide.

================================================================
CASOS (60, por familia -> un sub-agente cada una)
================================================================

### SHARD 1 - SALUD (RUN_ID VER-salud)
C02 | salud odontologia   | plan de tratamiento dental + odontograma progresivo
C04 | salud medico        | nota clinica estructurada + historial
C07 | salud psicologia    | nota de evolucion terapeutica
C11 | salud veterinaria   | ficha clinica + diagnostico diferencial
C17 | salud laboratorio   | transcripcion / validacion de resultados
C23 | salud fisioterapia  | plan de rehabilitacion por patologia
C25 | salud cumplimiento  | breach risk assessment HIPAA / notificacion
C30 | salud farmacia      | revision de recetas / interacciones
C38 | salud nutricion     | plan nutricional + seguimiento
C39 | salud forense       | valoracion de secuelas / dictamen pericial

### SHARD 2 - LEGAL (RUN_ID VER-legal)
C01 | legal laboral             | analisis de riesgo de demanda laboral entrante
C10 | legal penal               | analisis probatorio / estrategia de defensa
C13 | legal inmigracion         | revision de formularios inmigratorios
C15 | legal notario civil-law   | revision de formalidades de escritura (LATAM/EU)
C42 | legal familia             | calculo de pension alimenticia

### SHARD 3 - FINANZAS Y AUDITORIA (RUN_ID VER-finanzas)
C05 | finanzas conciliaciones | conciliacion bancaria mensual / matching
C09 | auditoria               | prueba sustantiva / workpaper + hallazgos
C12 | finanzas FP&A           | analisis de varianzas mensuales
C18 | finanzas AML            | investigacion de alerta / draft SAR
C19 | finanzas controller     | cierre contable mensual / ajustes
C24 | finanzas prestamos      | scoring / apelacion de credito
C60 | finanzas fintech        | scoring alternativo de credito digital

### SHARD 4 - RRHH (RUN_ID VER-rrhh)
C03 | rrhh reclutamiento | screening masivo de CVs -> shortlist
C08 | rrhh nomina        | calculo de nomina recurrente
C16 | rrhh onboarding    | verificacion documental de alta
C26 | rrhh relaciones    | investigacion interna de misconduct

### SHARD 5 - EDUCACION (RUN_ID VER-educacion)
C20 | educacion calificacion   | calificacion masiva con rubrica
C40 | educacion orientador     | plan de estudios / alerta de desercion
C49 | educacion universidad    | evaluacion de admision universitaria
C50 | educacion acomodo        | plan IEP/504 de acomodo por discapacidad
C51 | educacion calif asistida | calificacion asistida / nota final
C55 | educacion coordinacion   | emision de constancia academica

### SHARD 6 - INMOBILIARIO / CONSTRUCCION / ARQUITECTURA (RUN_ID VER-inmobiliario)
C14 | inmob property mgmt | ticket de mantenimiento / reparacion
C22 | inmob tasacion      | tasacion / informe de comparables
C28 | inmob agente        | ficha comparativa de lead
C31 | inmob facility      | work order management
C37 | construccion obra   | evaluacion de seguridad en obra (<1M)
C43 | arquitectura tecnico| memoria de calculo / cumplimiento de codigo
C44 | inmob HOA           | reclamo de propietario / resolucion

### SHARD 7 - OPERACIONES / LOGISTICA / COMPRAS (RUN_ID VER-operaciones)
C06 | ops aduanas          | clasificacion arancelaria HS + checklist documental
C41 | ops account mgmt     | propuesta de solucion B2B
C45 | ops procurement      | cotizacion comparativa de proveedores
C46 | ops compras B2B      | cotizacion por SKU negociado
C47 | ops inventario       | conteo ciclico / ajuste de stock
C54 | ops last mile        | incidencia de entrega
C58 | ops telecom          | queja FCC / borrador de contestacion
C59 | ops transporte aereo | incidente de seguridad / reporte FAA-NTSB

### SHARD 8 - COMERCIO / DISTRIBUCION / ECOMMERCE (RUN_ID VER-comercio)
C36 | comercio ferreteria   | asesoria de materiales por proyecto DIY
C48 | comercio ecommerce    | picking / validacion de orden multicanal
C52 | comercio distribucion | orden repetitiva / verificar stock / proforma

### SHARD 9 - SERVICIOS INDEPENDIENTES NICHO (RUN_ID VER-servicios)
C27 | servicios traductor | traduccion certificada / jurada
C29 | servicios guarderia | evaluacion de admision infantil
C32 | servicios seguridad | evaluacion de incidente de guardia
C33 | servicios mecanico  | diagnostico por sintomas + presupuesto
C34 | servicios funeraria | organizacion de ceremonia / papeleo postumo
C35 | servicios limpieza  | evaluacion de servicio / reasignacion
C53 | marketing agencia   | impacto de solicitud de cambio en presupuesto/tiempo

### SHARD 10 - SEGUROS / TECH / GOBIERNO (RUN_ID VER-seguros-tech-gov)
C21 | seguros siniestros | valoracion de siniestro / propuesta de liquidacion
C56 | tech biometria     | validacion biometrica de identidad
C57 | gov bienestar      | evaluacion de elegibilidad de beneficio social

================================================================
Si dudas del alcance, detente y pregunta. No entregar nada fuera del formato.
