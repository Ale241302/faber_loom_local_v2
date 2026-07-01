---
id: ENT_FB_USE_CASE_CATALOG_v1
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Plataforma
type: entity
stamp: DRAFT 2026-06-15 - catalogo de casos de uso multi-industria - NO implementacion - NO asesoria legal
fecha: 2026-06-15
agente: Claude (Cowork) - Arquitecto Ejecutor
aplica_a: [FaberLoom]
relacionado_con:
  - ENT_FB_VERTICAL_CANDIDATES_v2 (re-ranking por casos de uso)
  - PLAN_DESARROLLO_FABERLOOM_v4
disclaimer: |
  Los flags de compliance son ORIENTATIVOS, derivan del regimen aplicable tipico, NO son
  asesoria legal. Cada caso requiere validacion con abogado por jurisdiccion antes de operar.
  Marcas [PENDIENTE - VERIFICAR] donde el regimen depende de detalle no disponible.
---

# ENT_FB_USE_CASE_CATALOG_v1
## Catalogo de casos de uso multi-industria (lote ancla)

## 1. Tesis del catalogo

El atomo de FaberLoom es el **workspace heredable que se autoenriquece**: un alcance que (a) hereda contexto de su padre/pares, (b) deja hacer el trabajo dentro, (c) deposita conocimiento reutilizable como subproducto. El primitivo es indiferente a la industria; lo que cambia por caso es la **herencia**, el **NEVER autonomo** y el **regimen de compliance**. Este catalogo prueba esa generalidad con casos deliberadamente dispares.

Insight transversal (compliance como viento a favor, no barrera): en la UE el **AI Act** clasifica varios usos como alto riesgo (empleo, educacion-evaluacion, credito, servicios esenciales, biometria) y exige supervision humana + trazabilidad. En US los sectoriales (HIPAA, FINRA/Reg BI, FDCPA, FCRA, UPL, FERPA, FDA) empujan lo mismo. La arquitectura de FaberLoom (HITL obligatorio + evidence bundle + grounding trazado) ES el control de compliance. El compliance vende el producto por caso.

## 2. Esquema por caso

```
id            : UC-<n>
familia       : independiente_regulado | depto_corporativo | servicios_pro | educacion | comercio | nicho
industria/pro : quien
workspace     : scope + de quien HEREDA
trigger->uso->deposita : pedido entrante -> que hace -> que conocimiento queda
NEVER         : accion que el agente NUNCA ejecuta autonomo (siempre HITL)
compliance_US : ley sectorial tipica
compliance_EU : GDPR + AI Act risk tier + secreto profesional / regimen sectorial
```

Leyenda AI Act: ALTO = anexo III (empleo, educacion-eval, credito, servicios esenciales, justicia); LIM = riesgo limitado (transparencia); MIN = minimo.

---

## 3. Familia A - Profesionales independientes regulados

| # | Industria / pro | Workspace -> hereda | Trigger -> uso -> deposita | NEVER autonomo | US | EU / AI Act |
|---|---|---|---|---|---|---|
| UC-01 | Abogado inmigracion | caso cliente -> practica | consulta -> memo de opciones -> criterios USCIS, plantillas | dar consejo final, presentar | UPL | GDPR / ALTO |
| UC-02 | Abogado laboral | expediente -> materia | demanda entrante -> analisis de riesgo -> precedentes | firmar, presentar escrito | n/a | secreto prof, GDPR / ALTO |
| UC-03 | Contador / fiscalista | cliente -> firma | duda fiscal -> calculo preliminar -> tratamientos | firmar declaracion, opinar final | Circular 230, GLBA | GDPR / LIM |
| UC-04 | Auditor externo | engagement -> firma | hallazgo -> workpaper draft -> tests reusables | emitir opinion de auditoria | SOX, PCAOB | GDPR / LIM |
| UC-05 | Asesor financiero (RIA) | cliente -> compliance | consulta -> nota de inversion -> rationale | ejecutar trade, recomendar final | SEC, FINRA Reg BI | MiFID II / ALTO (credito/inversion) |
| UC-06 | Broker de seguros | cliente -> ramo | necesidad -> comparativo de polizas -> reglas de suscripcion | emitir/vincular poliza | state insurance law | IDD, GDPR / LIM |
| UC-07 | Medico clinica privada | paciente -> protocolo de la clinica | mensaje -> triage/respuesta -> guias internas | diagnostico, prescripcion | HIPAA | GDPR-salud, MDR / ALTO |
| UC-08 | Psicologo / terapeuta | paciente -> practica | nota de sesion -> resumen estructurado -> plantillas | diagnostico, alta | HIPAA | GDPR cat. especial / ALTO |
| UC-09 | Ingeniero estructural | proyecto -> normativa | RFI -> respuesta spec -> detalles por norma | firmar/sellar calculo | liability state | eIDAS, Eurocodigos / LIM |
| UC-10 | Notario | expediente -> protocolo | documento -> checklist + borrador -> formularios | autorizar, dar fe | state notary | eIDAS, secreto / ALTO |
| UC-11 | Agente aduanal | despacho -> regimen | embarque -> clasificacion arancelaria + draft -> criterios HS | declarar final, liberar carga | CBP, OFAC | UCC, AML / LIM |
| UC-12 | Despacho de patentes / IP | invencion -> cartera | divulgacion -> busqueda + borrador reivindicaciones -> prior art | presentar ante oficina | USPTO | EPO, secreto / LIM |

## 4. Familia B - Departamentos corporativos

| # | Industria / pro | Workspace -> hereda | Trigger -> uso -> deposita | NEVER autonomo | US | EU / AI Act |
|---|---|---|---|---|---|---|
| UC-13 | RRHH consultas empleados | tema (vacaciones/incap/permiso) -> politica global | consulta -> respuesta heredable -> criterios | decision disciplinaria/despido | EEOC, FMLA | GDPR, works council / ALTO |
| UC-14 | RRHH reclutamiento | vacante -> cliente interno | CV -> screening estructurado -> rubricas | descartar/rankear sin humano | EEOC | GDPR / ALTO |
| UC-15 | RRHH onboarding | nuevo empleado -> plantilla de alta | alta -> paquete de docs -> checklist | enviar contrato final | I-9 | GDPR / LIM |
| UC-16 | Finanzas - cuentas por cobrar | cobranza -> finanzas | factura vencida -> dunning por tono/historial -> reglas de cobro | amenazar, reportar a buro | FDCPA | GDPR / LIM |
| UC-17 | Finanzas - cuentas por pagar | pagos -> finanzas | factura proveedor -> validacion 3-way match -> excepciones | ejecutar pago | SOX | GDPR / LIM |
| UC-18 | Finanzas - conciliaciones | banco/cuenta -> finanzas | extracto -> matching + diferencias -> patrones | cerrar periodo | SOX | DORA (si financiera) / MIN |
| UC-19 | Contabilidad | cuenta -> finanzas | transaccion -> clasificacion sugerida -> tratamientos | asiento final, cerrar libros | GAAP, SOX | GDPR / MIN |
| UC-20 | Tesoreria | flujo -> finanzas | posicion -> proyeccion de caja -> supuestos | mover dinero, transferir | SOX | DORA / MIN |
| UC-21 | Operaciones - import maritimo | importacion -> area ops | embarque -> checklist documental + draft -> incoterms, navieras | liberar carga, declarar | CBP | UCC / MIN |
| UC-22 | Operaciones - exportacion | exportacion -> area ops | orden -> packing + certificado origen draft -> requisitos pais | certificar final | EAR, OFAC | dual-use / LIM |
| UC-23 | Compras / procurement | categoria -> compras | requisicion -> RFQ a proveedores + comparativo -> historico precios | adjudicar, firmar OC | n/a | proc rules, GDPR / LIM |
| UC-24 | Legal interno (contratos) | contrato -> playbook | NDA/MSA entrante -> redline contra playbook -> clausulas tipo | firmar, vincular | n/a | GDPR / LIM |
| UC-25 | Compliance / AML | caso -> politica | alerta -> analisis + narrativa -> tipologias | cerrar SAR, decidir reporte | BSA/AML | AMLD / ALTO |
| UC-26 | Customer Success / Soporte | ticket -> KB de producto | consulta -> respuesta citada -> articulos KB | prometer SLA, reembolsar | n/a | GDPR / LIM |

## 5. Familia C - Servicios profesionales

| # | Industria / pro | Workspace -> hereda | Trigger -> uso -> deposita | NEVER autonomo | US | EU / AI Act |
|---|---|---|---|---|---|---|
| UC-27 | Consultora de estrategia | engagement -> firma | pedido -> draft de analisis -> frameworks, decks pasados | recomendacion final sin socio | n/a | GDPR / MIN |
| UC-28 | Agencia de marketing | cliente -> agencia | brief -> copy/campana draft -> guia de marca | publicar, pautar | FTC ads | GDPR, ePrivacy / LIM |
| UC-29 | Agencia de RRPP | cliente -> agencia | crisis -> draft de comunicado -> mensajes clave | emitir comunicado | n/a | GDPR / LIM |
| UC-30 | Despacho contable outsourcing | cliente -> firma | cierre -> draft EEFF + variaciones -> tratamientos | firmar, presentar | GAAP | GDPR / MIN |
| UC-31 | Reclutadora boutique | busqueda -> cliente | CV -> shortlist + notas -> rubricas | descartar sin humano | EEOC | GDPR / ALTO |
| UC-32 | Estudio de diseno / UX | proyecto -> estudio | feedback -> doc de handoff -> sistema de diseno | n/a | n/a | GDPR / MIN |
| UC-33 | Despacho de arquitectura | cartera -> estudio | licitacion -> propuesta tecnica -> plantillas | firmar/sellar | liability | GDPR / LIM |
| UC-34 | Traductor jurado | encargo -> glosario | documento -> traduccion draft -> memoria de traduccion | certificar traduccion | n/a | eIDAS / LIM |

## 6. Familia D - Educacion / investigacion

| # | Industria / pro | Workspace -> hereda | Trigger -> uso -> deposita | NEVER autonomo | US | EU / AI Act |
|---|---|---|---|---|---|---|
| UC-35 | Estudiante universitario | materia -> carrera/semestre | tema -> resumen + guia de estudio -> apuntes, dudas resueltas | hacer examen, entregar como propio | FERPA, integridad acad. | GDPR / MIN |
| UC-36 | Docente / profesor | curso -> departamento | entrega -> feedback + rubrica draft -> banco de items | calificar final sin revisar | FERPA | GDPR / ALTO (eval educativa) |
| UC-37 | Asistente de catedra (TA) | curso -> profesor | duda alumno -> respuesta heredable -> FAQ del curso | calificar | FERPA | GDPR / LIM |
| UC-38 | Investigador / laboratorio | proyecto -> linea de investigacion | paper -> revision de literatura -> notas, citas | fabricar datos, enviar a journal | n/a | GDPR, etica / LIM |
| UC-39 | Coordinador academico | programa -> facultad | consulta -> respuesta normada -> reglamentos | resolver caso disciplinario | FERPA | GDPR / LIM |
| UC-40 | Tutor privado | alumno -> materia | sesion -> plan de estudio -> ejercicios | n/a (cuidado menores) | n/a | GDPR menores / LIM |

## 7. Familia E - Comercio / distribucion / ecommerce

| # | Industria / pro | Workspace -> hereda | Trigger -> uso -> deposita | NEVER autonomo | US | EU / AI Act |
|---|---|---|---|---|---|---|
| UC-41 | Distribuidor tecnico B2B | cliente -> area comercial | RFQ -> cotizacion trazada a lista -> nomenclatura, reglas precio | precio inventado, enviar | n/a | GDPR / MIN |
| UC-42 | Importador / mayorista | proveedor -> categoria | pedido -> orden + costeo landed -> historico | comprometer compra | n/a | GDPR / MIN |
| UC-43 | Retailer omnicanal | tienda -> cadena | consulta -> respuesta + disponibilidad -> FAQ | n/a | CCPA | GDPR / LIM |
| UC-44 | Ecommerce / Amazon FBA | listing -> marca | resena/mensaje -> respuesta -> objeciones frecuentes | violar ToS Amazon, prometer | FTC | GDPR, consumer / LIM |
| UC-45 | Account manager B2B | cuenta -> cartera | seguimiento -> draft proactivo (reposicion) -> ciclo cliente | comprometer descuento | n/a | GDPR / MIN |
| UC-46 | Distribuidor farma/dispositivos | cliente -> regulatorio | pedido -> cotizacion + docs regulatorios -> requisitos | claim off-label | FDA | MDR / LIM |
| UC-47 | Dealer de equipo industrial | cliente -> linea | RFQ -> cotizacion tecnica + specs -> configuraciones | comprometer entrega | n/a | GDPR / MIN |
| UC-48 | Concesionario autopartes | cliente -> catalogo | consulta SKU -> cotizacion + compatibilidad -> cruces de parte | precio inventado | n/a | GDPR / MIN |

## 8. Familia F - Nicho / otros independientes

| # | Industria / pro | Workspace -> hereda | Trigger -> uso -> deposita | NEVER autonomo | US | EU / AI Act |
|---|---|---|---|---|---|---|
| UC-49 | Agente inmobiliario | propiedad/cliente -> cartera | consulta -> ficha + respuesta -> objeciones, comps | discriminar criterios, cerrar | Fair Housing | GDPR / LIM |
| UC-50 | Property manager | edificio -> portafolio | reclamo inquilino -> respuesta segun contrato -> politicas | desalojar, discriminar | Fair Housing | GDPR / LIM |
| UC-51 | Planner de eventos | evento -> agencia | pedido -> propuesta + timeline -> proveedores | comprometer contrato | n/a | GDPR / MIN |
| UC-52 | Coach / consultor RRHH indep | cliente -> practica | caso -> plan de intervencion -> metodologia | decidir sobre empleo | EEOC | GDPR / ALTO (si afecta empleo) |
| UC-53 | Agencia de viajes corporativa | cuenta -> cartera | solicitud -> itinerario + politica de viaje -> tarifas | emitir/comprar boleto | n/a | GDPR, package travel / LIM |
| UC-54 | Despacho de arquitectura paisajista | proyecto -> estudio | requerimiento -> propuesta + especie vegetal -> fichas | firmar plano | n/a | GDPR / MIN |
| UC-55 | Gestor de fondos inmobiliarios | activo -> fondo | consulta inversor -> reporte draft -> KPIs | recomendacion de inversion | SEC | AIFMD, MiFID / ALTO |
| UC-56 | Despacho de seguros corporativo | poliza -> cuenta | siniestro -> analisis cobertura draft -> precedentes | aprobar/rechazar claim | state insurance | IDD / ALTO |
| UC-57 | Veterinaria | paciente -> clinica | consulta -> triage + respuesta -> protocolos | diagnostico, prescripcion | state vet | GDPR / LIM |
| UC-58 | Despacho de arquitectura BIM / facility | edificio -> cartera | incidencia -> orden de trabajo + respuesta -> historico mantenimiento | comprometer obra | n/a | GDPR / MIN |

---

## 9. Patron que valida la tesis

Los 58 casos comparten esqueleto: workspace + herencia + deposito de conocimiento + HITL. Lo que varia es solo (industria, herencia, NEVER, regimen). Eso es lo que hace a FaberLoom horizontal de verdad: no son 58 productos, es 1 telar con 58 configuraciones. Densidad de "ALTO" en AI Act (UC-05, 07, 08, 10, 13, 14, 25, 31, 36, 52, 55, 56) marca donde el compliance es argumento de venta mas fuerte.

## 10. Como escalar a 200 con Kimi (prompt blindado, sharded)

No correr un swarm de 200 a ciegas. Sharded por familia, mismo esquema, dedupe despues. Plantilla por shard (1 corrida por industria, blindada segun reglas Kimi: titulo de dominio linea 1, guard de alcance, erradicar ambiguos, ID de corrida):

```
CATALOGO DE CASOS DE USO - FABERLOOM - SHARD: <INDUSTRIA EXACTA>     # linea 1 = dominio, no borrar
RUN_ID: UC-<industria>-<fecha>

ALCANCE (no salir de aca):
- Genera EXACTAMENTE 20 casos de uso para la industria/profesion: <INDUSTRIA EXACTA>.
- Cada caso DEBE ser un workspace heredable que se autoenriquece (scope + de quien hereda + que conocimiento deposita).
- "caso de uso" = un trabajo entrante repetitivo que produce un artefacto del que el profesional es responsable.
- NO inventes leyes; si no sabes el regimen, escribe [PENDIENTE-VERIFICAR].
- NO generes casos de otra industria. NO repitas el mismo trigger dos veces.

FORMATO (una fila por caso, pipe-delimited, sin prosa):
id | industria | workspace->hereda | trigger->uso->deposita | NEVER_autonomo | compliance_US | compliance_EU+AIActTier

EJEMPLO (imitar formato, no copiar contenido):
UC-x | <industria> | caso->practica | consulta->memo->criterios | dar consejo final | UPL | GDPR/ALTO

ENTREGA: 20 filas. Nada mas. Si dudas del alcance, detente y pregunta.
```

Shards sugeridos (10 x 20 = 200): legal, contable/fiscal, salud, finanzas corporativas, RRHH, operaciones/logistica, educacion, comercio/distribucion, inmobiliario/construccion, marketing/agencias. Despues: Claude (o CLI) normaliza, dedupe contra este lote ancla, y marca colisiones.

## 11. [PENDIENTE - NO INVENTAR]

- Flags de compliance son orientativos; validar por jurisdiccion con abogado antes de operar cualquier caso.
- AI Act risk tier definitivo depende del detalle de implementacion; varios marcados [PENDIENTE-VERIFICAR] al implementar.
- Priorizacion de cual caso es beachhead: pendiente (depende del loop cold-start, ver ENT_FB_VERTICAL_CANDIDATES_v2).

## 12. Changelog

- v1.0 (2026-06-15): lote ancla de 58 casos multi-industria + esquema + prompt Kimi sharded para escalar a 200. No toca FROZEN. No crea SPEC. Compliance orientativo, no asesoria legal.
